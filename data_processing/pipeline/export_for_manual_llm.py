import pandas as pd
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.load_data import DATA_DIR

CHECKPOINT_FILE = DATA_DIR / "processed" / "03_enriched_checkpoint.jsonl"
INPUT_FILE = DATA_DIR / "processed" / "02_nlp_processed.parquet"
OUTPUT_EXPORT = DATA_DIR / "processed" / "remaining_recipes_to_enrich.json"
PROMPT_EXPORT = DATA_DIR / "processed" / "prompt_for_ai.txt"

def export_remaining():
    df = pd.read_parquet(INPUT_FILE)
    
    processed_urls = set()
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    processed_urls.add(data["url"])
                    
    mask = (~df["url"].isin(processed_urls)) & (df["iso3_inferred"].isna())
    df_to_process = df[mask]
    
    print(f"Recettes restantes à traiter : {len(df_to_process)}")
    
    # Création du fichier JSON à donner à l'IA
    export_list = []
    for _, row in df_to_process.iterrows():
        export_list.append({
            "url": row["url"],
            "title": row["name"],
            "ingredients": row.get("nlp_ingredients", row.get("ingredients", ""))
        })
        
    with open(OUTPUT_EXPORT, "w", encoding="utf-8") as f:
        json.dump(export_list, f, indent=2, ensure_ascii=False)
        
    print(f"Fichier exporté avec succès : {OUTPUT_EXPORT}")
    
    # Création du fichier contenant le prompt
    prompt_text = """Salut ! Je te fournis en pièce jointe un fichier JSON contenant une liste de recettes (avec url, titre et ingrédients).

TA TÂCHE :
Pour chaque recette de ce fichier, détermine le pays d'origine et la catégorie du plat.
Génère-moi en retour un NOUVEAU fichier JSON (ou donne-le-moi à télécharger) qui respecte EXACTEMENT cette structure :

[
  {
    "url": "l_url_exacte_de_la_recette",
    "country_iso3": "Le code ISO-3 du pays d'origine le plus probable (ex: ITA, FRA, JPN). Si c'est américain, mets USA. Si impossible à deviner, mets UNKNOWN",
    "category": "La catégorie (choisis STRICTEMENT parmi: Dessert, Main Dish, Starter, Beverage, Side Dish)"
  },
  ...
]

Il est impératif que tu me renvoies toutes les recettes traitées dans ce format.
"""
    with open(PROMPT_EXPORT, "w", encoding="utf-8") as f:
        f.write(prompt_text)
        
    print(f"Prompt généré avec succès : {PROMPT_EXPORT}")

if __name__ == "__main__":
    export_remaining()
