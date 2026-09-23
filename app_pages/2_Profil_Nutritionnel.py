import streamlit as st
import plotly.express as px

from src.load_data import load_processed
from src.nutrition import THRESHOLDS

st.title("Axe 2 — Le profil diététique mondialisé")

st.caption(
    f"Seuils indicatifs utilisés (par portion, voir src/nutrition.py) : "
    f"calories > {THRESHOLDS['calories_high']} kcal, "
    f"lipides > {THRESHOLDS['fat_high_g']} g, "
    f"glucides > {THRESHOLDS['carbs_high_g']} g (proxy sucre en l'absence de "
    f"colonne dédiée)."
)

cuisines = load_processed("cuisines_enriched")
mappable = cuisines[cuisines["map_type"] == "single_country"]

by_country = load_processed("by_country")
top_n = st.slider("Nombre de pays affichés (triés par nombre de recettes)", 5, 40, 15)
countries = by_country.sort_values("n_recipes", ascending=False).head(top_n)["country"].tolist()
subset = mappable[mappable["country"].isin(countries)]

tab1, tab2 = st.tabs(["Dispersion par pays", "Dépassement de seuils"])

with tab1:
    metric = st.radio("Variable", ["calories", "fat", "carbs", "protein"], horizontal=True)
    fig = px.box(
        subset,
        x="country",
        y=metric,
        category_orders={"country": countries},
        points=False,
    )
    fig.update_layout(height=500, xaxis_title=None)
    st.plotly_chart(fig, width='stretch')
    st.caption(
        "Si la boîte à moustaches d'un pays est nettement décalée par "
        "rapport aux autres, ce pays garde une spécificité nutritionnelle. "
        "Si toutes les boîtes se superposent, cela va dans le sens d'une "
        "convergence vers un profil standardisé."
    )

with tab2:
    exceed_by_country = by_country[by_country["country"].isin(countries)].sort_values(
        "pct_exceeds_calories", ascending=False
    )
    fig2 = px.bar(
        exceed_by_country,
        x="country",
        y=["pct_exceeds_calories", "pct_exceeds_fat"],
        barmode="group",
        labels={"value": "% de recettes dépassant le seuil", "country": "", "variable": "Seuil"},
    )
    fig2.update_yaxes(tickformat=".0%")
    fig2.update_layout(height=500)
    st.plotly_chart(fig2, width='stretch')

st.divider()
st.warning(
    "⚠️ Rappel : il n'y a pas de colonne `category` (dessert / plat "
    "principal...) dans ce dataset. Un pays surreprésenté en desserts aura "
    "mécaniquement plus de recettes riches en glucides, sans que cela "
    "traduise une spécificité culinaire nationale. À signaler comme limite "
    "à l'oral plutôt que comme conclusion définitive.",
    icon="⚠️",
)
