import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.load_data import DATA_DIR

try:
    from ingredient_parser import parse_ingredient
except ImportError:
    print("ERREUR: La librairie NLP n'est pas installée.")
    print("Veuillez lancer : pip install ingredient-parser-nlp")
    sys.exit(1)

INPUT_FILE = DATA_DIR / "processed" / "01_merged_mapped.parquet"
OUTPUT_FILE = DATA_DIR / "processed" / "02_nlp_processed.parquet"

# Liste de mots-clés pour les sucres ajoutés
SUGAR_TERMS = {
    "sugar", "honey", "syrup", "molasses", "agave", "caramel", 
    "marshmallow", "frosting", "icing", "sucrose", "fructose", "corn syrup"
}

def process_ingredients_nlp():
    if not INPUT_FILE.exists():
        print(f"Fichier {INPUT_FILE} introuvable. Lancez l'étape 1 d'abord.")
        sys.exit(1)
        
    print("Chargement des recettes...")
    df = pd.read_parquet(INPUT_FILE)
    print(f"Traitement NLP de {len(df)} recettes...")
    
    all_extracted_names = []
    has_added_sugar_list = []
    real_ingredient_count = []
    
    for idx, row in df.iterrows():
        raw_ingredients_str = str(row.get("ingredients", ""))
        
        # Sur Allrecipes, les ingrédients sont souvent séparés par des virgules dans notre CSV
        items = [i.strip() for i in raw_ingredients_str.split(",") if i.strip()]
        
        cleaned_names = []
        has_sugar = False
        
        for item in items:
            # MAGIE DU NLP : Le modèle CRF déduit la structure de la phrase
            try:
                parsed = parse_ingredient(item)
                
                # On extrait la "racine" de l'ingrédient
                if parsed.name and parsed.name.text:
                    ing_name = parsed.name.text.lower()
                    cleaned_names.append(ing_name)
                    
                    if any(sugar_term in ing_name for sugar_term in SUGAR_TERMS):
                        has_sugar = True
            except Exception:
                pass
                
        all_extracted_names.append(", ".join(cleaned_names))
        has_added_sugar_list.append(has_sugar)
        real_ingredient_count.append(len(cleaned_names))
        
        if idx % 1000 == 0 and idx > 0:
            print(f"... {idx} recettes traitées")
            
    df["nlp_ingredients"] = all_extracted_names
    df["has_added_sugar_nlp"] = has_added_sugar_list
    df["real_ingredient_count"] = real_ingredient_count
    
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_FILE, index=False)
    print(f"Terminé ! Fichier sauvegardé : {OUTPUT_FILE}")

if __name__ == "__main__":
    process_ingredients_nlp()
