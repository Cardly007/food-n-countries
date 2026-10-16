import streamlit as st

st.set_page_config(
    page_title="Recettes en ligne : diversité ou uniformisation ?",
    page_icon="🍲",
    layout="wide",
)

# Ordre du menu = ordre de lecture du parcours guidé (variante grand public).
# La page 5_Explorer_BI.py (PyGWalker) est volontairement retirée de la
# navigation : outil d'exploration libre, hors du fil narratif. Le fichier
# est conservé dans app_pages/.
pages = {
    "Introduction": [
        st.Page("app_pages/0_Accueil.py", title="Accueil", icon=":material/home:", default=True),
    ],
    "Le parcours": [
        st.Page("app_pages/1_Carte.py", title="1. Une étiquette, des pays", icon=":material/map:"),
        st.Page("app_pages/2_Profil_Nutritionnel.py", title="2. Des profils qui se ressemblent ?", icon=":material/restaurant:"),
        st.Page("app_pages/3_Notes_vs_Nutrition.py", title="3. Notes et richesse", icon=":material/star:"),
        st.Page("app_pages/4_Alternatives_Saines.py", title="4. Des alternatives", icon=":material/health_and_safety:"),
    ],
    "En savoir plus": [
        st.Page("app_pages/6_Methodologie.py", title="Méthodologie", icon=":material/science:"),
    ],
}

pg = st.navigation(pages)
pg.run()
