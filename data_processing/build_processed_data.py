"""
Pipeline de préparation des données. À relancer à chaque fois que les CSV
bruts changent. Il crée désormais deux jeux de parquets :
1. Les originaux (basés sur cuisines.csv).
2. Les versions "AI" (basées sur 03_final_dataset.parquet).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from src.load_data import load_all_recipes, load_cuisines, PROCESSED_DIR
from src.country_mapping import attach_iso3
from src.ingredients import add_ingredient_flags, staple_frequency_by_group
from src.nutrition import add_threshold_flags, flag_healthy_and_well_rated

def build():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    all_recipes = load_all_recipes()
    cuisines = load_cuisines()

    # ==========================================
    # PARTIE 1 : DONNÉES ORIGINALES (V1)
    # ==========================================
    cuisines_v1 = attach_iso3(cuisines)
    cuisines_v1 = add_ingredient_flags(cuisines_v1)
    cuisines_v1 = add_threshold_flags(cuisines_v1)
    cuisines_v1 = flag_healthy_and_well_rated(cuisines_v1)
    cuisines_v1.to_parquet(PROCESSED_DIR / "cuisines_enriched.parquet", index=False)

    all_recipes_v1 = add_ingredient_flags(all_recipes)
    all_recipes_v1 = add_threshold_flags(all_recipes_v1)
    all_recipes_v1 = flag_healthy_and_well_rated(all_recipes_v1)
    all_recipes_v1.to_parquet(PROCESSED_DIR / "all_recipes_enriched.parquet", index=False)

    mappable_v1 = cuisines_v1[cuisines_v1["map_type"] == "single_country"].copy()
    by_country_v1 = (
        mappable_v1.groupby(["country", "iso3"])
        .agg(
            n_recipes=("name", "count"),
            avg_rating=("avg_rating", "mean"),
            median_calories=("calories", "median"),
            median_fat=("fat", "median"),
            median_carbs=("carbs", "median"),
            pct_exceeds_calories=("exceeds_calories", "mean"),
            pct_exceeds_fat=("exceeds_fat", "mean"),
            pct_healthy_well_rated=("is_healthy_and_well_rated", "mean"),
            avg_approx_n_items=("approx_n_items", "mean"),
        )
        .reset_index()
    )
    by_country_v1.to_parquet(PROCESSED_DIR / "by_country.parquet", index=False)
    
    staples_v1 = staple_frequency_by_group(mappable_v1, "country")
    staples_v1.to_parquet(PROCESSED_DIR / "staple_frequency.parquet", index=False)

    # ==========================================
    # PARTIE 2 : DONNÉES ENRICHIES PAR IA (V2)
    # ==========================================
    final_ds_path = PROCESSED_DIR / "03_final_dataset.parquet"
    if final_ds_path.exists():
        df_ai = pd.read_parquet(final_ds_path)
        
        # Le NLP a pu générer des string vides pour nlp_ingredients si échec, on fallback
        df_ai["ingredients"] = df_ai["nlp_ingredients"].replace("", pd.NA).fillna(df_ai["ingredients"])
        
        df_ai = add_ingredient_flags(df_ai)
        df_ai = add_threshold_flags(df_ai)
        df_ai = flag_healthy_and_well_rated(df_ai)
        df_ai["map_type"] = "single_country" # Toutes les recettes IA avec ISO3 sont considérées comme cartographiables
        
        # Pour utiliser le code existant qui groupe par "country" (nom), 
        # on copie l'iso3 dans 'country' et on dit que tout est un "single_country" mappable.
        df_ai_mappable = df_ai[df_ai["iso3"].notna()].copy()
        df_ai_mappable["country"] = df_ai_mappable["iso3"] # Hack visuel pour que country = iso3
        
        # On sauvegarde le dataset principal
        df_ai.to_parquet(PROCESSED_DIR / "cuisines_enriched_ai.parquet", index=False)
        df_ai.to_parquet(PROCESSED_DIR / "all_recipes_enriched_ai.parquet", index=False)

        by_country_ai = (
            df_ai_mappable.groupby(["country", "iso3"])
            .agg(
                n_recipes=("name", "count"),
                avg_rating=("avg_rating", "mean"),
                median_calories=("calories", "median"),
                median_fat=("fat", "median"),
                median_carbs=("carbs", "median"),
                pct_exceeds_calories=("exceeds_calories", "mean"),
                pct_exceeds_fat=("exceeds_fat", "mean"),
                pct_healthy_well_rated=("is_healthy_and_well_rated", "mean"),
                avg_approx_n_items=("real_ingredient_count", "mean"), # Utilise le vrai count NLP!
            )
            .reset_index()
        )
        by_country_ai.to_parquet(PROCESSED_DIR / "by_country_ai.parquet", index=False)
        
        staples_ai = staple_frequency_by_group(df_ai_mappable, "country")
        staples_ai.to_parquet(PROCESSED_DIR / "staple_frequency_ai.parquet", index=False)

    print("OK — fichiers (V1 et V2 IA) écrits dans", PROCESSED_DIR)

if __name__ == "__main__":
    build()
