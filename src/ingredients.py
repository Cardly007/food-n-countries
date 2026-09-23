"""
Détection d'ingrédients par mots-clés dans le champ texte libre `ingredients`.

LIMITE CONNUE À DOCUMENTER DANS LE JOURNAL DE BORD :
Le champ `ingredients` est une liste jointe par ", " où certains items
contiennent eux-mêmes des virgules internes (ex: "margarine, softened" est
UN SEUL ingrédient avec une note de préparation, pas deux). Un simple
`.split(',')` sur-compte donc le nombre d'ingrédients et casse des items en
fragments ("margarine" / "softened" séparés). C'est un piège typique d'une
proposition IA non vérifiée : demander à un LLM de "compter les
ingrédients" sur ce champ sans le signaler donnera un nombre gonflé et
incohérent d'une recette à l'autre.

Deux approximations sont utilisées ici, documentées comme telles :
1. Détection de présence d'ingrédient par recherche de mot-clé (regex sur
   le texte brut) — fiable pour "est-ce que la recette contient du sucre ?"
2. Nombre approximatif d'items = nombre de virgules + 1 — sur-estime
   légèrement le vrai nombre d'ingrédients distincts, à utiliser en
   comparaison relative (entre pays) plutôt qu'en valeur absolue.
"""

import re
import pandas as pd

# Mots-clés = proxy pour un profil "sucré / gras / réconfort" à l'américaine,
# utilisé pour l'axe 3 (biais d'évaluation) en l'absence de colonne "sugar".
SUGAR_KEYWORDS = [
    "sugar", "honey", "syrup", "molasses", "brown sugar", "powdered sugar",
    "condensed milk", "chocolate chip", "maple",
]

COMFORT_KEYWORDS = [
    "butter", "cream", "cheese", "bacon", "mayonnaise", "sour cream",
    "cream cheese", "heavy cream",
]

# Petit vocabulaire d'ingrédients "de base" utilisé pour l'axe 1
# (uniformisation des ingrédients à travers le monde). Liste non
# exhaustive, à enrichir par l'équipe — la mesure la plus fiable reste la
# fréquence des mots (TF) issue d'une vraie tokenisation, voir
# data_processing/build_processed_data.py.
STAPLE_KEYWORDS = [
    "sugar", "all-purpose flour", "butter", "salt", "egg", "vegetable oil",
    "olive oil", "milk", "onion", "garlic", "black pepper",
]


def _contains_any(text: str, keywords: list[str]) -> bool:
    text = text.lower()
    return any(re.search(rf"\b{re.escape(kw)}\b", text) for kw in keywords)


def add_ingredient_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute des colonnes booléennes et un compte approximatif d'items."""
    df = df.copy()
    ing = df["ingredients"].fillna("").astype(str)
    df["has_sugar_proxy"] = ing.apply(lambda t: _contains_any(t, SUGAR_KEYWORDS))
    df["has_comfort_ingredient"] = ing.apply(lambda t: _contains_any(t, COMFORT_KEYWORDS))
    df["n_staples_present"] = ing.apply(
        lambda t: sum(1 for kw in STAPLE_KEYWORDS if _contains_any(t, [kw]))
    )
    # Approximation du nombre d'items (voir avertissement en tête de fichier)
    df["approx_n_items"] = ing.apply(lambda t: t.count(",") + 1 if t else 0)
    return df


def staple_frequency_by_group(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Pour chaque groupe (ex: pays), % de recettes contenant chaque staple.

    Sert à répondre à l'axe 1 : les recettes s'appuient-elles sur une base
    d'ingrédients uniformisée à travers le monde ?
    """
    df = df.copy()
    ing = df["ingredients"].fillna("").astype(str).str.lower()
    rows = []
    for kw in STAPLE_KEYWORDS:
        present = ing.apply(lambda t, kw=kw: bool(re.search(rf"\b{re.escape(kw)}\b", t)))
        tmp = df.assign(_present=present).groupby(group_col)["_present"].mean()
        for group, pct in tmp.items():
            rows.append({group_col: group, "ingredient": kw, "pct_recipes": pct})
    return pd.DataFrame(rows)
