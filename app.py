import streamlit as st

st.set_page_config(
    page_title="Allrecipes reflète-t-elle la diversité culinaire mondiale ?",
    page_icon=":material/public:",
    layout="wide",
)

pages = {
    "Introduction": [
        st.Page("app_pages/0_Accueil.py", title="Accueil", icon=":material/home:"),
    ],
    "Quatre questions": [
        st.Page("app_pages/1_Couverture.py", title="1. Couverture", icon=":material/public:"),
        st.Page("app_pages/2_Ingredients.py", title="2. Ingrédients", icon=":material/grid_on:"),
        st.Page("app_pages/3_Attention.py", title="3. Attention", icon=":material/reviews:"),
        st.Page("app_pages/4_Facettes.py", title="4. Facettes (type de plat)", icon=":material/restaurant_menu:"),
    ],
    "Comprendre": [
        st.Page("app_pages/6_Methodologie.py", title="Méthodologie", icon=":material/science:"),
    ],
}

pg = st.navigation(pages)
pg.run()
