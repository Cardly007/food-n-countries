import streamlit as st
import plotly.express as px

from src.load_data import load_processed
from src.nutrition import HEALTHY_CRITERIA

st.title("Axe 4 — La viabilité des alternatives saines")

st.caption(
    f"Critère \"saine et bien notée\" utilisé (modifiable dans "
    f"src/nutrition.py) : calories ≤ {HEALTHY_CRITERIA['calories_max']} kcal, "
    f"lipides ≤ {HEALTHY_CRITERIA['fat_max_g']} g, "
    f"note ≥ {HEALTHY_CRITERIA['min_rating']}, "
    f"avis ≥ {HEALTHY_CRITERIA['min_total_ratings']}."
)

col1, col2, col3, col4 = st.columns(4)
cal_max = col1.number_input("Calories max", 100, 1500, HEALTHY_CRITERIA["calories_max"], step=50)
fat_max = col2.number_input("Lipides max (g)", 0, 100, HEALTHY_CRITERIA["fat_max_g"], step=5)
rating_min = col3.slider("Note min", 3.0, 5.0, HEALTHY_CRITERIA["min_rating"], 0.1)
ratings_min = col4.number_input("Avis min", 0, 500, HEALTHY_CRITERIA["min_total_ratings"], step=10)

all_recipes = load_processed("all_recipes_enriched")
cuisines = load_processed("cuisines_enriched")

def apply_custom_filter(df):
    return df[
        (df["calories"] <= cal_max)
        & (df["fat"] <= fat_max)
        & (df["avg_rating"] >= rating_min)
        & (df["total_ratings"] >= ratings_min)
    ]

healthy_all = apply_custom_filter(all_recipes)
healthy_cuisines = apply_custom_filter(cuisines[cuisines["map_type"] == "single_country"])

col1, col2 = st.columns(2)
col1.metric(
    "Recettes générales saines et bien notées",
    f"{len(healthy_all):,}".replace(",", " "),
    f"{len(healthy_all) / len(all_recipes):.1%} du total",
)
col2.metric(
    "Recettes par pays saines et bien notées",
    f"{len(healthy_cuisines):,}".replace(",", " "),
    f"{len(healthy_cuisines) / len(cuisines[cuisines['map_type']=='single_country']):.1%} du total cartographiable",
)

st.divider()
st.subheader("D'où viennent ces alternatives saines ?")

by_country_health = (
    cuisines[cuisines["map_type"] == "single_country"]
    .assign(_ok=lambda d: (
        (d["calories"] <= cal_max) & (d["fat"] <= fat_max)
        & (d["avg_rating"] >= rating_min) & (d["total_ratings"] >= ratings_min)
    ))
    .groupby("country")
    .agg(n_total=("name", "count"), n_healthy=("_ok", "sum"))
    .assign(pct_healthy=lambda d: d["n_healthy"] / d["n_total"])
    .reset_index()
)
by_country_health = by_country_health[by_country_health["n_total"] >= 15]  # évite les % sur trop peu de recettes

fig = px.bar(
    by_country_health.sort_values("pct_healthy", ascending=False),
    x="country", y="pct_healthy",
    hover_data=["n_total", "n_healthy"],
    labels={"pct_healthy": "% de recettes saines et bien notées", "country": ""},
)
fig.update_yaxes(tickformat=".0%")
fig.update_layout(height=500)
st.plotly_chart(fig, width='stretch')
st.caption("Pays avec au moins 15 recettes catégorisées, pour éviter les pourcentages sur de trop petits effectifs.")

with st.expander("Voir les recettes correspondantes"):
    cols_show = ["name", "country", "calories", "fat", "avg_rating", "total_ratings", "url"]
    st.dataframe(
        healthy_cuisines[cols_show].sort_values("avg_rating", ascending=False),
        width='stretch', hide_index=True,
    )
