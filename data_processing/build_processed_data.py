"""
Pipeline de préparation des données. À relancer à chaque fois que les CSV
bruts changent :

    python data_processing/build_processed_data.py

Produit des fichiers .parquet dans data/processed/, consommés par l'appli
Streamlit (src/load_data.load_processed). On sépare volontairement ce calcul
de l'appli elle-même : les regex sur 16k lignes de texte n'ont pas besoin de
tourner à chaque interaction utilisateur.
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

    # --- Table 1 : cuisines enrichie (mapping pays + flags ingrédients + seuils) ---
    cuisines = attach_iso3(cuisines)
    cuisines = add_ingredient_flags(cuisines)
    cuisines = add_threshold_flags(cuisines)
    cuisines = flag_healthy_and_well_rated(cuisines)
    cuisines.to_parquet(PROCESSED_DIR / "cuisines_enriched.parquet", index=False)

    # --- Table 2 : all_recipes enrichie (mêmes flags, pas de pays) ---
    all_recipes_enriched = add_ingredient_flags(all_recipes)
    all_recipes_enriched = add_threshold_flags(all_recipes_enriched)
    all_recipes_enriched = flag_healthy_and_well_rated(all_recipes_enriched)
    all_recipes_enriched.to_parquet(PROCESSED_DIR / "all_recipes_enriched.parquet", index=False)

    # --- Table 3 : agrégats par pays (pour la carte, uniquement single_country) ---
    mappable = cuisines[cuisines["map_type"] == "single_country"].copy()
    by_country = (
        mappable.groupby(["country", "iso3"])
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
    by_country.to_parquet(PROCESSED_DIR / "by_country.parquet", index=False)

    # --- Table 4 : recettes exclues de la carte, pour affichage transparent ---
    excluded = cuisines[cuisines["map_type"] != "single_country"]
    excluded_summary = (
        excluded.groupby(["country", "map_type"])
        .size()
        .reset_index(name="n_recipes")
        .sort_values("n_recipes", ascending=False)
    )
    excluded_summary.to_parquet(PROCESSED_DIR / "excluded_from_map.parquet", index=False)

    # --- Table 5 : fréquence des ingrédients de base par pays (axe 1) ---
    staples = staple_frequency_by_group(mappable, "country")
    staples.to_parquet(PROCESSED_DIR / "staple_frequency.parquet", index=False)

    # --- Table 6 : recoupement des deux tables (pour l'axe 4 / méthodologie) ---
    overlap_urls = set(all_recipes["url"]) & set(cuisines["url"])
    overlap_stats = pd.DataFrame([{
        "n_all_recipes": len(all_recipes),
        "n_cuisines": len(cuisines),
        "n_overlap": len(overlap_urls),
        "pct_cuisines_in_all_recipes": len(overlap_urls) / len(cuisines),
    }])
    overlap_stats.to_parquet(PROCESSED_DIR / "overlap_stats.parquet", index=False)

    print("OK — fichiers écrits dans", PROCESSED_DIR)
    for f in sorted(PROCESSED_DIR.glob("*.parquet")):
        print(" -", f.name)


if __name__ == "__main__":
    build()
