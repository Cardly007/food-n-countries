import pandas as pd
import json
import os
import time
import requests
from pathlib import Path
import sys

try:
    from dotenv import load_dotenv
except ImportError:
    print("Veuillez installer python-dotenv : pip install python-dotenv")
    sys.exit(1)

load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.load_data import DATA_DIR

CHECKPOINT_FILE = DATA_DIR / "processed" / "03_enriched_checkpoint.jsonl"
INPUT_FILE = DATA_DIR / "processed" / "02_nlp_processed.parquet"
OUTPUT_FILE = DATA_DIR / "processed" / "03_final_dataset.parquet"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# On garde le modèle par défaut ou celui défini dans le .env
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free")

BATCH_SIZE = 15  # Nombre de recettes traitées par appel API

def call_openrouter_batch(batch_data):
    if not OPENROUTER_API_KEY:
        raise ValueError("Clé OpenRouter manquante dans le .env.")
        
    prompt = f"""
Voici une liste JSON contenant {len(batch_data)} recettes de cuisine avec leur "url", "title" et "ingredients".

{json.dumps(batch_data, indent=2, ensure_ascii=False)}

Ta tâche :
Renvoie-moi UNIQUEMENT un tableau JSON contenant exactement {len(batch_data)} objets.
Chaque objet doit avoir ces 3 clés :
- "url": L'identifiant url exact de la recette que je t'ai fourni.
- "country_iso3": Le code ISO-3 du pays d'origine le plus probable. Si c'est américain, mets "USA". Si tu ne sais pas, mets "UNKNOWN".
- "category": La catégorie (choisis parmi: "Dessert", "Main Dish", "Starter", "Beverage", "Side Dish").

Règle absolue : Ne renvoie que le tableau JSON valide. Pas d'introduction, pas de markdown autour, juste le tableau json [{{...}}, {{...}}].
"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:8501",
        "Content-Type": "application/json"
    }
    data = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 8000,
        # "response_format": {"type": "json_object"} # Beaucoup de modèles ne supportent pas ça sur OpenRouter quand la racine est un Array. On demande un texte brut formaté.
    }
    
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    if not response.ok:
        raise Exception(f"Erreur OpenRouter HTTP {response.status_code}: {response.text}")
        
    content = response.json()["choices"][0]["message"]["content"]
    
    # Nettoyage
    content = content.replace("```json", "").replace("```", "").strip()
    
    # Parfois l'IA renvoie un objet contenant le tableau plutôt que le tableau direct
    try:
        parsed_json = json.loads(content)
        if isinstance(parsed_json, dict):
            # Si elle a mis le tableau dans une clé (ex: {"recipes": [...]})
            for v in parsed_json.values():
                if isinstance(v, list):
                    return v
            return [parsed_json] # Au pire des cas
        return parsed_json
    except json.JSONDecodeError:
        print("Erreur de décodage JSON de l'IA :", content[:100], "...")
        raise

def process_with_llm():
    if not INPUT_FILE.exists():
        print(f"Veuillez d'abord exécuter l'étape 2 (Fichier {INPUT_FILE} manquant).")
        return
        
    df = pd.read_parquet(INPUT_FILE)
    
    processed_data = {}
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    processed_data[data["url"]] = data
                    
    processed_urls = set(processed_data.keys())
    print(f"Recettes déjà traitées trouvées dans le checkpoint : {len(processed_urls)}")
    
    mask_to_process = (~df["url"].isin(processed_urls)) & (df["iso3_inferred"].isna())
    df_to_process = df[mask_to_process]
    
    print(f"Recettes restantes à envoyer à l'API LLM : {len(df_to_process)}")
    
    if len(df_to_process) > 0:
        if not OPENROUTER_API_KEY:
            print("ERREUR: Aucune clé API OPENROUTER_API_KEY trouvée dans le fichier .env !")
            sys.exit(1)
            
        with open(CHECKPOINT_FILE, "a", encoding="utf-8") as f:
            # On découpe en lots (batches)
            chunks = [df_to_process.iloc[i:i + BATCH_SIZE] for i in range(0, len(df_to_process), BATCH_SIZE)]
            
            print(f"Traitement découpé en {len(chunks)} requêtes (Lots de {BATCH_SIZE} recettes).")
            
            for chunk_idx, chunk in enumerate(chunks):
                print(f"Envoi du lot {chunk_idx + 1}/{len(chunks)} ...")
                
                # Préparation des données du lot
                batch_payload = []
                for idx, row in chunk.iterrows():
                    batch_payload.append({
                        "url": row["url"],
                        "title": row["name"],
                        "ingredients": row.get("nlp_ingredients", row.get("ingredients", ""))
                    })
                
                try:
                    # Appel API pour le lot complet
                    results = call_openrouter_batch(batch_payload)
                    
                    if not isinstance(results, list):
                        print("Erreur: L'IA n'a pas renvoyé une liste. On passe ce lot.")
                        continue
                        
                    # Sauvegarde des résultats
                    for item in results:
                        url = item.get("url")
                        if not url:
                            continue
                            
                        data_to_save = {
                            "url": url,
                            "llm_iso3": item.get("country_iso3", "UNKNOWN"),
                            "llm_category": item.get("category", "UNKNOWN")
                        }
                        
                        f.write(json.dumps(data_to_save) + "\n")
                        processed_data[url] = data_to_save
                        
                    f.flush() # Force l'écriture sur le disque
                    
                    # Petite pause pour OpenRouter
                    time.sleep(1)
                    
                except KeyboardInterrupt:
                    print("\nArrêt manuel par l'utilisateur. Progression sauvegardée.")
                    break
                except Exception as e:
                    print(f"Erreur sur le lot {chunk_idx + 1}. L'erreur est : {e}")
                    print("On passe au lot suivant après une pause...")
                    time.sleep(5)
                    continue

    print("\nReconstruction du dataset final avec les données enrichies...")
    
    final_iso3 = []
    final_category = []
    
    for idx, row in df.iterrows():
        url = row["url"]
        
        if url in processed_data:
            ia_iso3 = processed_data[url].get("llm_iso3")
            final_iso3.append(ia_iso3 if ia_iso3 != "UNKNOWN" else None)
            final_category.append(processed_data[url].get("llm_category"))
        else:
            final_iso3.append(row.get("iso3_inferred"))
            final_category.append("Unknown")
            
    df["final_country_iso3"] = final_iso3
    df["recipe_category"] = final_category
    df["iso3"] = df["final_country_iso3"]
    
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_FILE, index=False)
    print(f"Terminé ! Le dataset final est prêt : {OUTPUT_FILE}")

if __name__ == "__main__":
    process_with_llm()
