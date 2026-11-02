import streamlit as st

from src.load_data import load_processed, load_stats
from src.theme import PAGE_THEMES, fmt_int, kpi, page_header

stats = load_stats()
overlap = load_processed("overlap_stats").iloc[0]

page_header(
    "accueil",
    "Allrecipes reflète-t-elle la diversité culinaire mondiale ?",
)

st.markdown(
    """
    <div style="
        background-color: #FFFDFB;
        border: 1px solid #ECE6DD;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    ">
        <div style="margin-bottom: 8px; font-size: 0.95rem;">
            <b style="color: #2D251E;">À qui s'adresse cette application ?</b> Aux responsables éditoriaux et produit de cette plateforme de recettes.
        </div>
        <div style="margin-bottom: 8px; font-size: 0.95rem;">
            <b style="color: #2D251E;">Pour décider quoi ?</b> Quelles cuisines ajouter au catalogue ou mettre en avant.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
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
        theme_key="accueil",
    )
with c2:
    kpi(
        "Catégories de cuisines", fmt_int(stats["n_categories"]),
        help="Catégories définies par Allrecipes : pays, régions multi-pays, "
             "traditions régionales américaines et communautés.",
        sub=f"{fmt_int(stats['n_categories_single_country'])} correspondent à un seul pays",
        theme_key="couverture",
    )
with c3:
    kpi(
        "Avis analysés", fmt_int(stats["avis_total"]),
        help="Somme des évaluations (étoiles) laissées par les utilisateurs sur les "
             "recettes classées par cuisine.",
        sub="sur les recettes classées par cuisine",
        theme_key="attention",
    )

st.subheader("Le parcours : quatre questions")
st.caption("De l'offre au contenu, puis à l'attention du public et aux facettes montrées.")

steps = [
    ("app_pages/1_Couverture.py", "1. Couverture", ":material/public:",
     "Le catalogue couvre-t-il le monde ?",
     "Quels pays ont une cuisine proposée, et le poids de chaque continent suit-il sa population ?",
     "couverture"),
    ("app_pages/2_Ingredients.py", "2. Ingrédients", ":material/grid_on:",
     "Les cuisines sont-elles vraiment différentes dans l'assiette ?",
     f"Fréquence de {fmt_int(stats['n_ingredients'])} ingrédients dans chaque cuisine, regroupées en familles.",
     "ingredients"),
    ("app_pages/3_Attention.py", "3. Attention", ":material/reviews:",
     "Quelles cuisines le public suit-il ?",
     "Nombre moyen d'avis par recette, cuisine par cuisine.",
     "attention"),
    ("app_pages/4_Facettes.py", "4. Facettes", ":material/restaurant_menu:",
     "Chaque cuisine est-elle montrée par des plats variés ?",
     "Part des desserts, plats, soupes et accompagnements dans chaque cuisine.",
     "facettes"),
]
cols = st.columns(2)
for i, (page, label, icon, question, desc, theme_k) in enumerate(steps):
    t = PAGE_THEMES[theme_k]
    with cols[i % 2]:
        st.markdown(
            f"""
            <div style="
                background-color: {t['bg_card']};
                border: 1px solid {t['border']};
                border-left: 4px solid {t['accent']};
                border-radius: 10px;
                padding: 14px 16px;
                margin-bottom: 10px;
                min-height: 125px;
            ">
                <span style="
                    display: inline-block;
                    padding: 2px 8px;
                    border-radius: 999px;
                    background-color: {t['badge_bg']};
                    color: {t['badge_text']};
                    font-size: 0.72rem;
                    font-weight: 700;
                    margin-bottom: 6px;
                ">{t['tag']}</span>
                <div style="font-weight: 700; font-size: 1rem; color: #2D251E; margin-bottom: 4px;">{question}</div>
                <div style="font-size: 0.84rem; color: #555555; line-height: 1.4;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(page, label=f"Explorer : {label}", icon=icon)

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
"""
)

