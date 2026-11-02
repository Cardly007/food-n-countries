import streamlit as st

from src.theme import get_global_css

st.set_page_config(
    page_title="Allrecipes reflète-t-elle la diversité culinaire mondiale ?",
    page_icon=":material/public:",
    layout="wide",
)

# Injection du style pastel global (barre latérale + conteneurs)
st.markdown(get_global_css(), unsafe_allow_html=True)

# En-tête de la barre latérale
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-header-brand">
            <span class="sidebar-brand-pill">M2 MIAGE · Data Viz</span>
            <div class="sidebar-brand-title">Allrecipes & Diversité Culinaire</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

pages = {
    "Introduction": [
        st.Page("app_pages/0_Accueil.py", title="Accueil", icon=":material/home:", url_path="accueil"),
    ],
    "Quatre questions": [
        st.Page("app_pages/1_Couverture.py", title="1. Couverture", icon=":material/public:", url_path="couverture"),
        st.Page("app_pages/2_Ingredients.py", title="2. Ingrédients", icon=":material/grid_on:", url_path="ingredients"),
        st.Page("app_pages/3_Attention.py", title="3. Attention", icon=":material/reviews:", url_path="attention"),
        st.Page("app_pages/4_Facettes.py", title="4. Facettes (type de plat)", icon=":material/restaurant_menu:", url_path="facettes"),
    ],
}

pg = st.navigation(pages)
pg.run()

