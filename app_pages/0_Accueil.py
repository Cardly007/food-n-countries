import pandas as pd
import streamlit as st

from src.insights import build_home_headline, deduplicated_total, nutrient_convergence
from src.load_data import load_processed
from src.story import METHODO_PAGE, STEPS
from src.theme import fmt_int, fmt_num, kpi

overlap = load_processed("overlap_stats").iloc[0]
cuisines = load_processed("cuisines_enriched")
all_recipes = load_processed("all_recipes_enriched")
mappable = cuisines[cuisines["map_type"] == "single_country"]

# Accroche : le message central, affirmé seulement si les données le soutiennent
# (part de pays aux calories médianes proches de la médiane globale, axe 2).
st.title(build_home_headline(nutrient_convergence(mappable, "calories")))

st.markdown(
    """
**À qui s'adresse cette application ?** Aux lecteurs curieux de cuisine et d'alimentation.

**Quel message ?** Les cuisines « du monde » telles qu'elles sont présentées en ligne
se ressemblent plus qu'il n'y paraît.

**Question centrale :** les recettes de chaque pays sont-elles aussi différentes
qu'elles en ont l'air ?
"""
)

# Note moyenne calculée sur les recettes distinctes (une recette présente dans
# les deux tables n'est comptée qu'une fois).
distinct = pd.concat([all_recipes, cuisines]).drop_duplicates("url")
n_countries = len(load_processed("by_country"))

col1, col2, col3 = st.columns(3)
with col1:
    kpi(
        "Recettes analysées",
        fmt_int(deduplicated_total(overlap)),
        help=(
            "Deux tables issues du site Allrecipes : des recettes générales "
            f"({fmt_int(overlap.n_all_recipes)}) et des recettes classées par cuisine "
            f"({fmt_int(overlap.n_cuisines)}). {fmt_int(overlap.n_overlap)} recettes "
            "figurent dans les deux : elles ne sont comptées qu'une fois."
        ),
        subtitle="publiées sur le site Allrecipes",
    )
with col2:
    kpi(
        "Étiquettes « cuisine du monde »",
        fmt_int(cuisines["country"].nunique()),
        help="Certaines étiquettes ne sont pas des pays (« Soul Food », « Jewish »…) : voir la page Méthodologie.",
        subtitle=f"dont {fmt_int(n_countries)} correspondent à un seul pays",
    )
with col3:
    kpi(
        "Note moyenne des recettes",
        f"{fmt_num(distinct['avg_rating'].mean(), 1)} / 5",
        help=f"Moyenne sur les {fmt_int(distinct['avg_rating'].notna().sum())} recettes notées.",
        subtitle="attribuée par les internautes",
    )

st.subheader("Le parcours, en quatre étapes")
st.markdown("\n".join(f"{i}. {phrase}" for i, (_, phrase) in enumerate(STEPS, start=1)))

st.page_link(STEPS[0][0], label="Commencer →", icon=":material/play_arrow:")

st.caption("Les choix de calcul et les limites des données sont détaillés dans la page Méthodologie.")
st.page_link(METHODO_PAGE, label="Méthodologie", icon=":material/science:")
