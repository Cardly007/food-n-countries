import pandas as pd
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.load_data import DATA_DIR

# Fichier que l'utilisateur doit placer après l'avoir généré par l'IA
IA_RESULT_FILE = DATA_DIR / "processed" / "ai_results.json"
CHECKPOINT_FILE = DATA_DIR / "processed" / "03_enriched_checkpoint.jsonl"

def import_results():
    if not IA_RESULT_FILE.exists():
        print(f"ERREUR: Le fichier {IA_RESULT_FILE} est introuvable.")
        print("Veuillez sauvegarder la réponse de l'IA dans ce fichier et relancer le script.")
        sys.exit(1)
        
    try:
        with open(IA_RESULT_FILE, "r", encoding="utf-8") as f:
            ai_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERREUR: Le fichier ai_results.json n'est pas un JSON valide. Détail: {e}")
        sys.exit(1)
        
    print(f"[{len(ai_data)}] recettes trouvées dans le fichier de l'IA.")
    
    # On ajoute ces résultats au checkpoint
    count_added = 0
    with open(CHECKPOINT_FILE, "a", encoding="utf-8") as f:
        for item in ai_data:
            if "url" in item:
                # On formate pour correspondre au format du checkpoint
                data_to_save = {
                    "url": item["url"],
                    "llm_iso3": item.get("country_iso3", "UNKNOWN"),
                    "llm_category": item.get("category", "UNKNOWN")
                }
                f.write(json.dumps(data_to_save) + "\n")
                count_added += 1
                
    print(f"{count_added} recettes ont été ajoutées au checkpoint de sauvegarde !")
    print("Vous pouvez maintenant relancer 'python data_processing/pipeline/03_llm_enrichment.py'")
    print("Le script va reconstruire le Dataset Final (03_final_dataset.parquet) instantanément.")

if __name__ == "__main__":
    import_results()
