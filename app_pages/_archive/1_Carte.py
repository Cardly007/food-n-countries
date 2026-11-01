import streamlit as st
import plotly.express as px

from src.load_data import load_processed

st.title("Axe 1 — L'illusion de la diversité géographique")

by_country = load_processed("by_country")
excluded = load_processed("excluded_from_map")

metric_labels = {
    "n_recipes": "Nombre de recettes",
    "avg_rating": "Note moyenne",
    "median_calories": "Calories médianes / portion",
    "median_fat": "Lipides médians (g) / portion",
    "pct_exceeds_calories": "% de recettes dépassant le seuil calorique",
    "pct_exceeds_fat": "% de recettes dépassant le seuil de lipides",
    "pct_healthy_well_rated": "% de recettes saines ET bien notées",
    "avg_approx_n_items": "Nombre approx. d'ingrédients (moyenne)",
}

metric = st.selectbox(
    "Indicateur affiché sur la carte",
    options=list(metric_labels.keys()),
    format_func=lambda k: metric_labels[k],
)

fig = px.choropleth(
    by_country,
    locations="iso3",
    color=metric,
    hover_name="country",
    hover_data={"n_recipes": True, "iso3": False},
    color_continuous_scale="OrRd" if "pct" in metric or "calor" in metric or "fat" in metric else "Blues",
    title=metric_labels[metric],
)
fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=550)
st.plotly_chart(fig, width='stretch')

st.caption(
    f"{by_country['n_recipes'].sum():,.0f} recettes réparties sur "
    f"{len(by_country)} pays affichables sur la carte.".replace(",", " ")
)

with st.expander(f"⚠️ {excluded['n_recipes'].sum()} recettes non cartographiables — pourquoi ?"):
    st.markdown(
        "Ces catégories de `country` ne correspondent pas à un pays unique "
        "et ne sont donc **pas affichées sur la carte** (voir Méthodologie) :"
    )
    st.dataframe(excluded, width='stretch', hide_index=True)

st.divider()
st.subheader("Base d'ingrédients : uniformisée ou distincte selon les pays ?")

staples = load_processed("staple_frequency")
top_countries = (
    by_country.sort_values("n_recipes", ascending=False).head(12)["country"].tolist()
)
selected = st.multiselect(
    "Pays à comparer (par fréquence d'apparition de chaque ingrédient de base)",
    options=sorted(by_country["country"].unique()),
    default=top_countries[:8],
)

if selected:
    subset = staples[staples["country"].isin(selected)]
    fig2 = px.bar(
        subset,
        x="ingredient",
        y="pct_recipes",
        color="country",
        barmode="group",
        labels={"pct_recipes": "% des recettes du pays contenant l'ingrédient", "ingredient": "Ingrédient de base"},
    )
    fig2.update_yaxes(tickformat=".0%")
    fig2.update_layout(height=450)
    st.plotly_chart(fig2, width='stretch')
    st.caption(
        "Si les barres sont proches pour tous les pays sur des ingrédients "
        "comme le sucre, la farine ou le beurre, cela va dans le sens d'une "
        "base uniformisée malgré l'étiquette 'pays d'origine'."
    )
else:
    st.info("Sélectionnez au moins un pays pour afficher le comparatif.")
