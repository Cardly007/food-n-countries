import pandas as pd
from pathlib import Path
import sys

# Ajouter le chemin racine pour importer src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.load_data import load_all_recipes, load_cuisines, DATA_DIR
from src.country_mapping import COUNTRY_MAPPING

def merge_and_map():
    print("Chargement des données...")
    all_recipes = load_all_recipes()
    cuisines = load_cuisines()
    
    print(f"all_recipes: {len(all_recipes)} recettes")
    print(f"cuisines: {len(cuisines)} recettes")
    
    # Priorité aux données de 'cuisines' car elles ont déjà le pays d'Allrecipes
    # On concatène et on enlève les doublons sur l'URL
    df_merged = pd.concat([cuisines, all_recipes], ignore_index=True)
    
    # On supprime les doublons en gardant la première occurrence (celle de 'cuisines')
    df_merged = df_merged.drop_duplicates(subset=["url"], keep="first").reset_index(drop=True)
    
    print(f"Après fusion et dédoublonnage: {len(df_merged)} recettes uniques")
    
    # Mapping probabiliste (forcer les catégories vagues en pays ISO-3)
    # On ajoute nos règles de redressement pour cet exercice
    probabilistic_mapping = {
        "Australian and New Zealander": "AUS",
        "Jewish": "ISR",
        "Scandinavian": "SWE", # Ou on pourrait dupliquer pour NOR, DNK
        "Soul Food": "USA",
        "Cajun and Creole": "USA",
        "Tex-Mex": "USA",
        "Southern Recipes": "USA",
        "Amish and Mennonite": "USA" # Historiquement basés aux USA
    }
    
    # On met à jour ou on crée la colonne 'iso3_inferred'
    def infer_iso3(row):
        country_label = row.get("country")
        if pd.isna(country_label):
            return None
            
        # Si c'est déjà un pays mappé standard dans COUNTRY_MAPPING
        if country_label in COUNTRY_MAPPING and COUNTRY_MAPPING[country_label]["iso3"]:
            return COUNTRY_MAPPING[country_label]["iso3"]
            
        # Sinon, utilisation du mapping probabiliste
        if country_label in probabilistic_mapping:
            return probabilistic_mapping[country_label]
            
        return None

    df_merged["iso3_inferred"] = df_merged.apply(infer_iso3, axis=1)
    
    output_path = DATA_DIR / "processed" / "01_merged_mapped.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_merged.to_parquet(output_path, index=False)
    print(f"Étape 1 terminée. Fichier sauvegardé : {output_path}")

if __name__ == "__main__":
    merge_and_map()
