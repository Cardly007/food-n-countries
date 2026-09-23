"""
Seuils nutritionnels utilisés pour l'axe 2 (profil diététique) et l'axe 4
(alternatives saines).

Choix méthodologique important à défendre à l'oral : `calories`, `fat`,
`carbs`, `protein` sont déclarés PAR PORTION par l'auteur de la recette
(`servings`), pas par recette entière, et pas normalisés par apport
journalier de référence. Comparer des recettes entre elles nécessite donc
de garder `servings` en tête — une recette "4 portions, 600 kcal/portion"
n'est pas plus calorique qu'une recette "2 portions, 300 kcal/portion" par
portion, mais elle l'est pour un repas complet si le nombre de portions
réellement consommées diffère de celui déclaré. On raisonne ici uniquement
"par portion", ce qui est la seule base disponible et comparable.

Les seuils ci-dessous sont des repères indicatifs inspirés des
recommandations générales (OMS / apports de référence ~2000 kcal/jour pour
un adulte), pas des normes cliniques. Ils sont VOLONTAIREMENT explicites et
modifiables ici pour que l'équipe puisse les justifier/discuter dans le
journal de bord plutôt que les subir.
"""

import pandas as pd

# Seuils "par portion", exprimés comme une fraction d'un repas dans un
# régime à ~2000 kcal/jour (repère générique, pas un pays en particulier).
THRESHOLDS = {
    "calories_high": 600,   # kcal / portion
    "fat_high_g": 25,       # g / portion (repère ~30% des lipides d'un repas à 700 kcal)
    "carbs_high_g": 75,     # g / portion, utilisé comme proxy sucre en l'absence de colonne dédiée
}

HEALTHY_CRITERIA = {
    "calories_max": 500,
    "fat_max_g": 20,
    "min_rating": 4.5,
    "min_total_ratings": 20,
}


def add_threshold_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["exceeds_calories"] = df["calories"] > THRESHOLDS["calories_high"]
    df["exceeds_fat"] = df["fat"] > THRESHOLDS["fat_high_g"]
    df["exceeds_carbs"] = df["carbs"] > THRESHOLDS["carbs_high_g"]
    df["n_thresholds_exceeded"] = (
        df["exceeds_calories"].astype(int)
        + df["exceeds_fat"].astype(int)
        + df["exceeds_carbs"].astype(int)
    )
    return df


def flag_healthy_and_well_rated(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["is_healthy_and_well_rated"] = (
        (df["calories"] <= HEALTHY_CRITERIA["calories_max"])
        & (df["fat"] <= HEALTHY_CRITERIA["fat_max_g"])
        & (df["avg_rating"] >= HEALTHY_CRITERIA["min_rating"])
        & (df["total_ratings"] >= HEALTHY_CRITERIA["min_total_ratings"])
    )
    return df
