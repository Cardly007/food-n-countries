import streamlit as st

from src.country_mapping import get_mapping_df
from src.indicators import dedup_totals
from src.theme import fmt_int, fmt_pct, kpi

st.title("Recettes en ligne : diversité ou uniformisation ?")

# --- Brief décisionnel ------------------------------------------------------
with st.container(border=True):
    st.markdown(
        """
**À qui s'adresse cette application ?** Aux responsables éditoriaux de
plateformes de recettes en ligne.

**Pour décider quoi ?** Quelles recettes mettre en avant pour offrir à la fois
une diversité culinaire réelle et des options saines que les utilisateurs
apprécient.

**Question centrale :** les recettes étiquetées par pays reflètent-elles une
vraie diversité, ou masquent-elles une uniformisation nutritionnelle ?
"""
    )

# --- KPI ------------------------------------------------------------------------
try:
    t = dedup_totals()
    mapping = get_mapping_df()
    n_labels = len(mapping)
    n_single = int((mapping["map_type"] == "single_country").sum())

    c1, c2, c3 = st.columns(3)
    kpi(
        "Recettes uniques analysées",
        fmt_int(t["n_unique"]),
        subtitle=(
            f"{fmt_int(t['n_all_recipes'])} recettes générales + "
            f"{fmt_int(t['n_cuisines'])} étiquetées par pays − "
            f"{fmt_int(t['n_overlap'])} présentes dans les deux"
        ),
        help=(
            "Le jeu de données contient deux tables : les recettes générales "
            "(sans pays) et les recettes rangées par Allrecipes dans une catégorie de cuisine nationale ou régionale). Certaines "
            "recettes figurent dans les deux tables (même URL) : elles ne sont "
            "comptées qu'une fois ici."
        ),
        container=c1,
    )
    kpi(
        "Recettes étiquetées par pays",
        fmt_int(t["n_cuisines"]),
        subtitle=f"{fmt_pct(t['pct_overlap'])} d'entre elles figurent aussi dans les recettes générales",
        help="Recettes de la seule table qui porte une étiquette de pays.",
        container=c2,
    )
    kpi(
        "Étiquettes de cuisine",
        fmt_int(n_labels),
        subtitle=f"dont {fmt_int(n_single)} correspondent à un pays unique (cartographiables)",
        help=(
            "Les autres étiquettes désignent plusieurs pays, une tradition "
            "régionale des États-Unis ou une communauté sans territoire "
            "national (voir Méthodologie)."
        ),
        container=c3,
    )
except FileNotFoundError as e:
    st.error(str(e))

st.divider()

# --- Parcours --------------------------------------------------------------------
st.subheader("Le parcours : diagnostic → test → hypothèse → décision")

AXES = [
    ("1. Diagnostic", "app_pages/1_Carte.py",
     "D'où viennent les recettes étiquetées par pays, et leur base d'ingrédients "
     "diffère-t-elle d'un pays à l'autre ?"),
    ("2. Test de la diversité", "app_pages/2_Profil_Nutritionnel.py",
     "Les recettes de chaque pays gardent-elles un profil nutritionnel propre ?"),
    ("3. Hypothèse sur le levier", "app_pages/3_Notes_vs_Nutrition.py",
     "Les recettes les plus riches sont-elles mieux notées ?"),
    ("4. Décision", "app_pages/4_Alternatives_Saines.py",
     "Combien de recettes sont à la fois saines et bien notées, et dans quels pays ?"),
]
cols = st.columns(len(AXES))
for col, (step, page, question) in zip(cols, AXES):
    with col.container(border=True):
        st.markdown(f"**{step}**")
        st.markdown(question)
        st.page_link(page, label="Ouvrir", icon=":material/arrow_forward:")

st.info(
    "**Limite à garder en tête sur toutes les pages** : l'étiquette « pays » "
    "du jeu de données mélange des nationalités (Chine, Italie…) et des "
    "catégories qui ne sont pas des pays (Soul food, cuisine juive, "
    "Scandinavie…). Voir la page Méthodologie pour le détail.",
    icon=":material/warning:",
)
