import streamlit as st
from src.load_data import load_processed
from src.country_mapping import get_mapping_df

st.title("Méthodologie et limites")

st.markdown(
    """
Cette page centralise les choix méthodologiques et leurs limites — à
réutiliser directement dans le Journal de bord (section "Audit et critique
visuelle").
"""
)

st.subheader("1. Deux tables, pas une seule population de 16 644 recettes")
overlap = load_processed("overlap_stats").iloc[0]
st.write(
    f"`all_recipes.csv` contient {overlap.n_all_recipes:,.0f} recettes, "
    f"`cuisines.csv` en contient {overlap.n_cuisines:,.0f}. Seules "
    f"{overlap.n_overlap:,.0f} recettes ({overlap.pct_cuisines_in_all_recipes:.1%} "
    f"de `cuisines.csv`) existent dans les deux (jointure sur l'URL). "
    f"**Ce ne sont donc pas des sous-ensembles l'un de l'autre** : on ne "
    f"peut pas dire \"les 14 426 recettes, dont 2 218 catégorisées par pays\".".replace(",", " ")
)

st.subheader("2. La colonne `country` n'est pas une liste de pays")
st.markdown(
    "8 des 49 valeurs de `country` (396 recettes, 18 % de `cuisines.csv`) "
    "ne correspondent pas à un pays unique et sont exclues de la carte "
    "choroplèthe (voir `src/country_mapping.py`) :"
)
mapping = get_mapping_df()
st.dataframe(
    mapping[mapping["map_type"] != "single_country"].sort_values("map_type"),
    width='stretch', hide_index=True,
)

st.subheader("3. Pas de colonne sucre ni catégorie de plat")
st.markdown(
    """
- Les seules variables nutritionnelles disponibles sont `calories`, `fat`,
  `carbs`, `protein` (par portion). **Il n'y a pas de colonne sucre** : les
  analyses sur le sucre utilisent soit `carbs` comme proxy, soit une
  détection par mot-clé dans le texte libre `ingredients`
  (`src/ingredients.py`, `SUGAR_KEYWORDS`).
- **Il n'y a pas de colonne catégorie** (dessert / plat principal /
  entrée...). Une différence de profil nutritionnel entre deux pays peut
  donc refléter une différence de composition du corpus (plus ou moins de
  desserts) plutôt qu'une vraie différence culinaire nationale.
"""
)

st.subheader("4. Comptage d'ingrédients : une approximation, pas une mesure exacte")
st.markdown(
    """
Le champ `ingredients` est une liste jointe par `", "`, mais certains items
contiennent eux-mêmes une virgule interne (ex : `"margarine, softened"` est
un seul ingrédient, pas deux). Le nombre d'items calculé par
`nombre de virgules + 1` (`approx_n_items`) **surestime légèrement** le
vrai nombre d'ingrédients. À utiliser en **comparaison relative entre
pays**, jamais comme un chiffre absolu présenté seul.
"""
)

st.subheader("5. Seuils nutritionnels")
st.markdown(
    """
Les seuils utilisés (`src/nutrition.py`) sont des repères indicatifs (base
~2000 kcal/jour pour un adulte), pas des normes cliniques ou OMS
appliquées littéralement. Ils sont volontairement paramétrables et modifiés
en direct sur la page **Alternatives saines** pour que le choix de seuil
soit assumé plutôt que subi.
"""
)

st.subheader("6. Corrélation ≠ causalité (Axe 3)")
st.markdown(
    """
Une corrélation positive entre note et densité calorique/lipidique ne
démontre pas que les utilisateurs "récompensent" la malbouffe : elle peut
refléter une sur-représentation des desserts et plats riches parmi les
recettes les plus commentées, ou un biais de sélection (seules les
recettes qui plaisent reçoivent beaucoup d'avis).
"""
)
