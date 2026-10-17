"""
Libellés affichés à l'écran (Séance 3 : aucun nom de colonne brut visible).

Les données gardent leurs noms de colonnes et leurs valeurs d'origine
(anglais) ; seule la couche d'affichage est traduite ici.
"""

import pandas as pd

# Colonnes -> libellé lisible avec unité
COLUMN_LABELS = {
    "name": "Recette",
    "country": "Pays",
    "pays": "Pays",
    "url": "Lien",
    "calories": "Calories (kcal / portion)",
    "fat": "Lipides (g / portion)",
    "carbs": "Glucides (g / portion)",
    "protein": "Protéines (g / portion)",
    "avg_rating": "Note moyenne (sur 5)",
    "total_ratings": "Nombre d'avis",
    "reviews": "Nombre de commentaires",
    "n_recipes": "Nombre de recettes",
    "median_calories": "Calories médianes (kcal / portion)",
    "median_fat": "Lipides médians (g / portion)",
    "median_carbs": "Glucides médians (g / portion)",
    "pct_exceeds_calories": "Part des recettes au-dessus du seuil calorique",
    "pct_exceeds_fat": "Part des recettes au-dessus du seuil de lipides",
    "pct_exceeds_carbs": "Part des recettes au-dessus du seuil de glucides",
    "pct_healthy_well_rated": "Part des recettes saines et bien notées",
    "avg_approx_n_items": "Nombre approximatif d'ingrédients (moyenne)",
    "map_type": "Type de catégorie",
    "pct_recipes": "Part des recettes contenant l'ingrédient",
    "ingredient": "Ingrédient de base",
}

# Nutriments utilisés dans les sélecteurs (nom court, sans unité)
NUTRIENT_SHORT = {
    "calories": "Calories",
    "fat": "Lipides",
    "carbs": "Glucides",
    "protein": "Protéines",
}
NUTRIENT_UNIT = {"calories": "kcal", "fat": "g", "carbs": "g", "protein": "g"}

MAP_TYPE_LABELS = {
    "single_country": "Pays unique",
    "multi_country": "Plusieurs pays",
    "us_regional": "Tradition régionale des États-Unis",
    "non_national": "Communauté sans territoire national",
}

INGREDIENT_LABELS = {
    "sugar": "Sucre",
    "all-purpose flour": "Farine de blé",
    "butter": "Beurre",
    "salt": "Sel",
    "egg": "Œuf",
    "vegetable oil": "Huile végétale",
    "olive oil": "Huile d'olive",
    "milk": "Lait",
    "onion": "Oignon",
    "garlic": "Ail",
    "black pepper": "Poivre noir",
}

COUNTRY_LABELS = {
    "Canadian": "Canada",
    "Brazilian": "Brésil",
    "Filipino": "Philippines",
    "Cuban": "Cuba",
    "Chinese": "Chine",
    "Russian": "Russie",
    "Indian": "Inde",
    "French": "France",
    "Italian": "Italie",
    "Japanese": "Japon",
    "Greek": "Grèce",
    "German": "Allemagne",
    "Vietnamese": "Viêt Nam",
    "Thai": "Thaïlande",
    "Spanish": "Espagne",
    "Polish": "Pologne",
    "Korean": "Corée",
    "Portuguese": "Portugal",
    "Lebanese": "Liban",
    "Persian": "Iran (cuisine persane)",
    "Jamaican": "Jamaïque",
    "Peruvian": "Pérou",
    "Turkish": "Turquie",
    "Danish": "Danemark",
    "Swedish": "Suède",
    "Argentinian": "Argentine",
    "Norwegian": "Norvège",
    "Pakistani": "Pakistan",
    "Malaysian": "Malaisie",
    "Indonesian": "Indonésie",
    "Israeli": "Israël",
    "Chilean": "Chili",
    "Dutch": "Pays-Bas",
    "Austrian": "Autriche",
    "South African": "Afrique du Sud",
    "Finnish": "Finlande",
    "Bangladeshi": "Bangladesh",
    "Colombian": "Colombie",
    "Swiss": "Suisse",
    "Belgian": "Belgique",
    "Puerto Rican": "Porto Rico",
    "Australian and New Zealander": "Australie et Nouvelle-Zélande",
    "Scandinavian": "Scandinavie",
    "Soul Food": "Soul food (États-Unis)",
    "Cajun and Creole": "Cajun et créole (États-Unis)",
    "Tex-Mex": "Tex-Mex (États-Unis)",
    "Southern Recipes": "Cuisine du Sud (États-Unis)",
    "Jewish": "Cuisine juive",
    "Amish and Mennonite": "Amish et mennonite",
}


def label(col: str) -> str:
    return COLUMN_LABELS.get(col, col)


def country_label(country: str) -> str:
    return COUNTRY_LABELS.get(country, country)


def add_country_label(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute la colonne `pays` (libellé français) à partir de `country`."""
    return df.assign(pays=df["country"].map(country_label))
