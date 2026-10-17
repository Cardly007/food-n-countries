import streamlit as st

from src import insights as ins
from src.country_mapping import get_mapping_df
from src.load_data import load_processed
from src.nutrition import HEALTHY_CRITERIA, THRESHOLDS
from src.theme import MAP_TYPE_LABELS, country_label, fmt_int, fmt_num, fmt_pct

st.title("Méthodologie et limites")

st.markdown(
    "Cette page rassemble les choix de calcul et les limites des données. "
    "Tous les chiffres ci-dessous sont recalculés à partir des données."
)

overlap = load_processed("overlap_stats").iloc[0]
cuisines = load_processed("cuisines_enriched")
n_dedup = ins.deduplicated_total(overlap)

st.subheader("1. Deux tables qui se recoupent : un total dédupliqué")
st.markdown(
    f"Les recettes viennent de deux tables du site Allrecipes : {fmt_int(overlap.n_all_recipes)} "
    f"recettes générales et {fmt_int(overlap.n_cuisines)} recettes classées par cuisine. "
    f"{fmt_int(overlap.n_overlap)} recettes ({fmt_pct(overlap.pct_cuisines_in_all_recipes, 1)} de la "
    f"seconde table) figurent dans les deux (même adresse web). Additionner les deux tables "
    f"compterait ces recettes deux fois : le total affiché à l'accueil est donc "
    f"{fmt_int(overlap.n_all_recipes)} + {fmt_int(overlap.n_cuisines)} − {fmt_int(overlap.n_overlap)} "
    f"= **{fmt_int(n_dedup)} recettes distinctes**."
)

st.subheader("2. L'étiquette « pays » n'est pas toujours un pays")
mapping = get_mapping_df()
not_country = mapping[mapping["map_type"] != "single_country"]
n_not_country = int((cuisines["map_type"] != "single_country").sum())
st.markdown(
    f"{len(not_country)} des {cuisines['country'].nunique()} étiquettes de cuisine "
    f"({fmt_int(n_not_country)} recettes, {fmt_pct(n_not_country / len(cuisines))} des recettes classées "
    "par cuisine) ne correspondent pas à un pays unique. Elles sont exclues de la carte et des "
    "comparaisons entre pays, mais comptées dans les totaux (voir `src/country_mapping.py`) :"
)
st.dataframe(
    not_country.assign(
        etiquette=not_country["country"].map(country_label),
        type=not_country["map_type"].map(MAP_TYPE_LABELS),
    ).sort_values("type")[["etiquette", "type"]],
    column_config={"etiquette": "Étiquette", "type": "Type d'étiquette"},
    width="stretch", hide_index=True,
)

st.subheader("3. Ni sucre, ni catégorie de plat")
st.markdown(
    """
- Les seules valeurs nutritionnelles disponibles sont les calories, les lipides, les glucides
  et les protéines, **par portion**. Il n'y a pas de mesure du sucre : les glucides servent
  d'indice, et certains ingrédients sont repérés par mot-clé dans la liste des ingrédients
  (`src/ingredients.py`).
- Il n'y a **pas de catégorie** (dessert, plat, boisson…). Une différence entre deux pays peut
  venir de la composition de leurs recettes (plus ou moins de desserts) plutôt que de leur
  cuisine. Exemple observé : des cocktails passent le filtre « sain et bien noté » de la page 4.
"""
)

st.subheader("4. Ingrédients : un repérage par mot-clé")
st.markdown(
    """
La liste des ingrédients est un texte libre, séparé par des virgules, dont certains éléments
contiennent eux-mêmes une virgule (« margarine, softened » est un seul ingrédient). On ne compte
donc pas les ingrédients : on repère la **présence** de quelques ingrédients de base par
mot-clé. Le nombre d'ingrédients approximatif (virgules + 1) surestime le vrai nombre et ne sert
qu'à comparer des pays entre eux.
"""
)

st.subheader("5. Seuils nutritionnels")
st.markdown(
    f"Repères indicatifs par portion, pour un adulte à environ 2 000 kcal par jour, pas des normes "
    f"médicales (`src/nutrition.py`) :\n"
    f"- page 2, « au-delà du seuil » : plus de {THRESHOLDS['calories_high']} kcal, "
    f"plus de {THRESHOLDS['fat_high_g']} g de lipides ;\n"
    f"- page 4, « sain et bien noté » (par défaut, réglable) : au plus "
    f"{HEALTHY_CRITERIA['calories_max']} kcal, au plus {HEALTHY_CRITERIA['fat_max_g']} g de lipides, "
    f"note d'au moins {fmt_num(HEALTHY_CRITERIA['min_rating'], 1)} avec au moins "
    f"{HEALTHY_CRITERIA['min_total_ratings']} avis."
)

st.subheader("6. Nuages de points : un échantillon affiché, un calcul sur tout")
st.markdown(
    "Pour rester lisibles, les nuages de points de la page 3 n'affichent qu'un **échantillon "
    f"aléatoire de {fmt_int(ins.SCATTER_SAMPLE_SIZE)} recettes** (tirage fixe, reproductible). La droite de tendance et la "
    "corrélation sont calculées sur **toutes** les recettes retenues ; le nombre total est "
    "indiqué au-dessus des graphiques."
)

st.subheader("7. Corrélation ≠ causalité")
st.markdown(
    "Un lien entre la note et la richesse d'une recette ne dirait pas que les internautes "
    "« récompensent » les plats riches : il pourrait venir des desserts, ou du fait que seules "
    "les recettes qui plaisent reçoivent beaucoup d'avis. Les titres n'emploient donc jamais de "
    "formulation causale (« va de pair avec », « lien »)."
)

st.subheader("8. Règles de prudence des titres")
st.markdown(
    f"""
Chaque titre-insight est **calculé** par une fonction (`src/insights.py`) qui choisit sa
formulation selon la valeur obtenue. Si les chiffres ne soutiennent pas le message attendu, le
titre le dit.

| Page | Indicateur | Bascule entre formulations |
|---|---|---|
| Accueil, page 2 | part des pays (≥ {ins.MIN_RECIPES_PER_COUNTRY} recettes) dont la médiane est à ±{fmt_pct(ins.CONVERGENCE_BAND)} de la médiane globale | ≥ {fmt_pct(ins.CONVERGENCE_STRONG)} « très proches », ≥ {fmt_pct(ins.CONVERGENCE_MAJORITY)} « la plupart », sinon « contrastés » |
| Page 1 | écart de fréquence d'un ingrédient entre pays | ≤ {fmt_num(ins.COMMON_SPREAD_MAX * 100, 0)} points : commun ; ≥ {fmt_num(ins.DISTINCT_SPREAD_MIN * 100, 0)} points : distinctif |
| Page 1 | pays le plus représenté / pays médian | < {fmt_num(ins.DOMINANCE_RATIO, 1)} : « aucun pays ne domine » |
| Page 3 | corrélation de rang (Spearman) | \\|ρ\\| < {fmt_num(ins.RHO_VERY_WEAK, 2)} ou non significatif : « lien très faible » ; < {fmt_num(ins.RHO_WEAK, 2)} : « légèrement » |
| Page 3 | écart de note avec / sans ingrédients « réconfort » | < {fmt_num(ins.RATING_DIFF_NEGLIGIBLE, 2)} étoile ou non significatif : « quasi identiques » |
| Page 4 | part de recettes saines et bien notées par pays (≥ {ins.MIN_RECIPES_AXE4} recettes) | pays en tête nommés ; message adapté si aucune recette ne passe |

Ces seuils sont des valeurs rondes fixées à l'avance ; ils n'ont pas été ajustés pour obtenir
un message donné. Le détail de chaque choix est consigné dans `JOURNAL_IA.md`.
"""
)

st.subheader("9. Exploration libre")
st.markdown(
    "Une page d'exploration libre (`app_pages/5_Explorer_BI.py`, outil PyGWalker) existe dans le "
    "projet mais n'apparaît pas dans le menu : cette version de l'application suit un parcours guidé."
)
