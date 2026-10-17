import streamlit as st

from src.country_mapping import get_mapping_df
from src.indicators import (
    NUTRIENTS, SCATTER_SAMPLE_SIZE, SCATTER_X_CLIP_QUANTILE,
    all_recipes, cuisines, dedup_totals, excluded_from_map,
)
from src.ingredients import STAPLE_KEYWORDS
from src.labels import MAP_TYPE_LABELS, NUTRIENT_SHORT, country_label
from src.nutrition import HEALTHY_CRITERIA, THRESHOLDS
from src.theme import fmt_int, fmt_num, fmt_pct

st.title("Méthodologie et limites")

st.markdown(
    """
Cette page centralise les choix méthodologiques et leurs limites — à
réutiliser directement dans le journal de bord (section « Audit et critique
visuelle »). Tous les chiffres cités ici sont recalculés à partir des données.
"""
)

t = dedup_totals()
st.subheader("1. Deux tables, et un total dédupliqué")
st.markdown(
    f"La table des recettes générales contient {fmt_int(t['n_all_recipes'])} recettes, "
    f"celle des recettes étiquetées par pays en contient {fmt_int(t['n_cuisines'])}. "
    f"Seules {fmt_int(t['n_overlap'])} recettes ({fmt_pct(t['pct_overlap'], 1)} des "
    "recettes étiquetées) existent dans les deux (jointure sur l'URL). **Ce ne sont "
    "donc pas des sous-ensembles l'une de l'autre**, et additionner les deux tables "
    f"({fmt_int(t['n_all_recipes'] + t['n_cuisines'])}) compterait deux fois les "
    "recettes communes.\n\n"
    f"Le total affiché sur l'Accueil est **dédupliqué** : {fmt_int(t['n_all_recipes'])} + "
    f"{fmt_int(t['n_cuisines'])} − {fmt_int(t['n_overlap'])} = **{fmt_int(t['n_unique'])} "
    "recettes uniques**."
)

mapping = get_mapping_df()
excluded = excluded_from_map()
n_excl = int(excluded["n_recipes"].sum())
n_non_single = int((mapping["map_type"] != "single_country").sum())
st.subheader("2. L'étiquette « pays » n'est pas une liste de pays")
st.markdown(
    f"{n_non_single} des {len(mapping)} étiquettes ({fmt_int(n_excl)} recettes, "
    f"{fmt_pct(n_excl / t['n_cuisines'])} des recettes étiquetées) ne correspondent "
    "pas à un pays unique et sont exclues de la carte et des comparaisons par pays "
    "(voir `src/country_mapping.py`). Elles restent proposables comme recettes "
    "candidates à l'axe 4 :"
)
non_single = mapping[mapping["map_type"] != "single_country"].sort_values("map_type")
st.dataframe(
    non_single.assign(
        Étiquette=non_single["country"].map(country_label),
        Type=non_single["map_type"].map(MAP_TYPE_LABELS),
    )[["Étiquette", "Type"]],
    width="stretch", hide_index=True,
)

st.subheader("3. Pas de colonne sucre ni catégorie de plat")
st.markdown(
    """
- Les seules variables nutritionnelles disponibles sont les calories, les
  lipides, les glucides et les protéines (par portion). **Il n'y a pas de
  colonne sucre** : les analyses sur le sucre utilisent les glucides comme
  proxy, ou une détection par mot-clé dans la liste d'ingrédients
  (`src/ingredients.py`).
- **Il n'y a pas de catégorie de plat** (dessert / plat principal / entrée…).
  Une différence de profil nutritionnel entre deux pays peut donc refléter une
  différence de composition du corpus (plus ou moins de desserts) plutôt
  qu'une vraie différence culinaire nationale.
"""
)

st.subheader("4. Ingrédients : des approximations, pas des mesures exactes")
st.markdown(
    f"""
- La présence d'un ingrédient de base est détectée par mot-clé sur une liste
  de {len(STAPLE_KEYWORDS)} ingrédients, non exhaustive (axe 1).
- La liste d'ingrédients est un texte séparé par des virgules, mais certains
  items contiennent eux-mêmes une virgule (« margarine, softened » est un seul
  ingrédient). Le nombre d'ingrédients calculé par « nombre de virgules + 1 »
  **surestime légèrement** le vrai nombre : à utiliser en **comparaison
  relative entre pays**, jamais comme un chiffre absolu présenté seul.
"""
)

st.subheader("5. Seuils nutritionnels")
st.markdown(
    f"""
Les seuils (`src/nutrition.py`) sont des repères indicatifs par portion (base
~2 000 kcal / jour pour un adulte), pas des normes cliniques appliquées
littéralement :

- **Dépassement (axe 2)** : calories > {THRESHOLDS['calories_high']} kcal,
  lipides > {THRESHOLDS['fat_high_g']} g, glucides > {THRESHOLDS['carbs_high_g']} g
  (proxy sucre).
- **Recette saine et bien notée (axe 4, valeurs par défaut)** : calories ≤
  {HEALTHY_CRITERIA['calories_max']} kcal, lipides ≤ {HEALTHY_CRITERIA['fat_max_g']} g,
  note ≥ {fmt_num(HEALTHY_CRITERIA['min_rating'], 1)}, au moins
  {HEALTHY_CRITERIA['min_total_ratings']} avis. Le minimum d'avis évite de
  retenir une recette notée 5/5 par une seule personne.

Ces seuils sont **réglables en direct** sur la page Décision pour que le choix
soit assumé plutôt que subi : le tableau de recettes candidates suit les
seuils choisis.
"""
)

st.subheader("6. Corrélation ≠ causalité (axe 3)")
st.markdown(
    """
Une relation entre note et densité calorique ne démontre pas que les
utilisateurs « récompensent » la malbouffe : elle peut refléter une
sur-représentation des desserts et plats riches parmi les recettes les plus
commentées, ou un biais de sélection (seules les recettes qui plaisent
reçoivent beaucoup d'avis). Avec plusieurs milliers de recettes, une relation
très faible peut être statistiquement détectable sans être importante en
pratique : la page indique donc la **force** de la relation (ρ de Spearman),
pas seulement sa significativité.
"""
)

st.subheader("7. Échantillon des nuages de points (axe 3)")
st.markdown(
    f"""
Pour rester lisibles, les nuages de points ne dessinent qu'un **échantillon
aléatoire de {fmt_int(SCATTER_SAMPLE_SIZE)} recettes** (tirage fixe, reproductible). L'effectif réel
est écrit sous chaque graphique, et la droite de tendance comme le ρ de
Spearman sont calculés sur **toutes** les recettes renseignées, pas sur
l'échantillon. L'axe horizontal est limité au {SCATTER_X_CLIP_QUANTILE * 100:.0f}e centile ; le nombre de
recettes non dessinées est indiqué.
"""
)

st.subheader("8. Valeurs manquantes")
general, labelled = all_recipes(), cuisines()
rows = []
for n in NUTRIENTS + ["avg_rating"]:
    name = NUTRIENT_SHORT.get(n, "Note moyenne")
    rows.append({
        "Variable": name,
        "Recettes générales sans valeur": fmt_int(general[n].isna().sum()),
        "Recettes étiquetées sans valeur": fmt_int(labelled[n].isna().sum()),
    })
st.markdown(
    "Les valeurs manquantes ne sont ni remplacées ni comptées comme « sous le "
    "seuil » : les parts de l'axe 2 sont calculées sur les seules recettes "
    "renseignées, et une recette sans valeur pour un critère n'est pas retenue "
    "à l'axe 4. Le nombre de recettes concernées est affiché sous chaque graphique."
)
st.dataframe(rows, width="stretch", hide_index=True)
