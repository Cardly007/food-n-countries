import streamlit as st

st.set_page_config(
    page_title="Recettes en ligne : diversité ou uniformisation ?",
    page_icon="🍲",
    layout="wide",
)

pages = {
    "Introduction": [
        st.Page("app_pages/0_Accueil.py", title="Accueil", icon=":material/home:"),
        st.Page("app_pages/6_Methodologie.py", title="Méthodologie", icon=":material/science:"),
    ],
    "Axes d'analyse": [
        st.Page("app_pages/1_Carte.py", title="1. Diagnostic : origine et ingrédients", icon=":material/map:"),
        st.Page("app_pages/2_Profil_Nutritionnel.py", title="2. Test : profil nutritionnel", icon=":material/restaurant:"),
        st.Page("app_pages/3_Notes_vs_Nutrition.py", title="3. Hypothèse : notes et richesse", icon=":material/star:"),
        st.Page("app_pages/4_Alternatives_Saines.py", title="4. Décision : recettes à promouvoir", icon=":material/health_and_safety:"),
    ],
}
# app_pages/5_Explorer_BI.py (PyGWalker) est conservé dans le dépôt mais retiré
# de la navigation : l'exploration libre par glisser-déposer expose les noms
# de colonnes bruts et sort du parcours diagnostic -> décision (JOURNAL_IA.md).

pg = st.navigation(pages)
pg.run()
