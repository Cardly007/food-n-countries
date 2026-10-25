import streamlit as st

from src.load_data import load_processed, load_stats
from src.theme import fmt_int, kpi

stats = load_stats()
overlap = load_processed("overlap_stats").iloc[0]

st.title("Allrecipes reflète-t-elle la diversité culinaire mondiale ?")

with st.container(border=True):
    st.markdown(
        "**À qui s'adresse cette application ?** Aux responsables éditoriaux et "
        "produit d'une plateforme de recettes.  \n"
        "**Pour décider quoi ?** Quelles cuisines ajouter au catalogue ou mettre "
        "en avant.  \n"
        "**Question centrale :** le catalogue d'Allrecipes reflète-t-il la "
        "diversité culinaire mondiale ?"
    )

c1, c2, c3 = st.columns(3)
with c1:
    kpi(
        "Recettes uniques", fmt_int(stats["n_recettes_uniques"]),
        help=(
            f"Deux tables : {fmt_int(overlap.n_all_recipes)} recettes générales, sans "
            f"pays, et {fmt_int(overlap.n_cuisines)} recettes classées par cuisine. "
            f"Elles ne sont pas incluses l'une dans l'autre : "
            f"{fmt_int(overlap.n_overlap)} recettes sont communes (même URL). "
            f"Total sans doublon : {fmt_int(overlap.n_all_recipes)} + "
            f"{fmt_int(overlap.n_cuisines)} − {fmt_int(overlap.n_overlap)}. "
            f"Les analyses portent sur les {fmt_int(overlap.n_cuisines)} recettes "
            f"classées par cuisine."
        ),
        sub=f"dont {fmt_int(overlap.n_cuisines)} classées par cuisine",
    )
with c2:
    kpi(
        "Catégories de cuisines", fmt_int(stats["n_categories"]),
        help="Catégories définies par Allrecipes : pays, régions multi-pays, "
             "traditions régionales américaines et communautés.",
        sub=f"{fmt_int(stats['n_categories_single_country'])} correspondent à un seul pays",
    )
with c3:
    kpi(
        "Avis analysés", fmt_int(stats["avis_total"]),
        help="Somme des évaluations (étoiles) laissées par les utilisateurs sur les "
             "recettes classées par cuisine.",
        sub="sur les recettes classées par cuisine",
    )

st.subheader("Le parcours : quatre questions")
st.caption("De l'offre au contenu, puis à l'attention du public et aux facettes montrées.")

steps = [
    ("app_pages/1_Couverture.py", "1. Couverture", ":material/public:",
     "Le catalogue couvre-t-il le monde ?",
     "Quels pays ont une cuisine proposée, et le poids de chaque continent suit-il sa population ?"),
    ("app_pages/2_Ingredients.py", "2. Ingrédients", ":material/grid_on:",
     "Les cuisines sont-elles vraiment différentes dans l'assiette ?",
     f"Fréquence de {fmt_int(stats['n_ingredients'])} ingrédients dans chaque cuisine, regroupées en familles."),
    ("app_pages/3_Attention.py", "3. Attention", ":material/reviews:",
     "Quelles cuisines le public suit-il ?",
     "Nombre moyen d'avis par recette, cuisine par cuisine."),
    ("app_pages/4_Facettes.py", "4. Facettes", ":material/restaurant_menu:",
     "Chaque cuisine est-elle montrée par des plats variés ?",
     "Part des desserts, plats, soupes et accompagnements dans chaque cuisine."),
]
cols = st.columns(2)
for i, (page, label, icon, question, desc) in enumerate(steps):
    with cols[i % 2].container(border=True):
        st.markdown(f"**{question}**")
        st.caption(desc)
        st.page_link(page, label=label, icon=icon)

st.subheader("Ce que ces données permettent, et ne permettent pas, de dire")
st.markdown(
    f"""
- **Une seule plateforme**, anglophone et à audience surtout américaine : on mesure
  la représentation dans *ce* catalogue, pas la diversité culinaire réelle du monde.
- **Collecte plafonnée** : {fmt_int(stats['n_categories_plafond'])} catégories sur
  {fmt_int(stats['n_categories'])} comptent entre {fmt_int(stats['seuil_plafond'])} et
  {fmt_int(stats['max_recettes_categorie'])} recettes, et aucune n'en a davantage.
  Le nombre de recettes d'une grande cuisine ne s'interprète donc pas ; seuls
  comptent la présence ou l'absence d'une cuisine et les petits effectifs.
- **Des catégories hétérogènes** : la colonne « pays » mélange des pays, des
  régions multi-pays, des traditions régionales américaines et des communautés.
  Détails dans la page Méthodologie.
"""
)
st.page_link("app_pages/6_Methodologie.py", label="Méthodologie et limites",
             icon=":material/science:")
