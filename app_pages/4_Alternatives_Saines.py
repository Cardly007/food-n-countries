import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.load_data import load_processed
from src.nutrition import HEALTHY_CRITERIA

# Dictionnaire de traduction en français des 49 pays et traditions culinaires
COUNTRY_FR = {
    "Canadian": "Canada", "Brazilian": "Brésil", "Filipino": "Philippines", "Cuban": "Cuba",
    "Chinese": "Chine", "Russian": "Russie", "Indian": "Inde", "French": "France",
    "Italian": "Italie", "Japanese": "Japon", "Greek": "Grèce", "German": "Allemagne",
    "Vietnamese": "Vietnam", "Thai": "Thaïlande", "Spanish": "Espagne", "Polish": "Pologne",
    "Korean": "Corée du Sud", "Portuguese": "Portugal", "Lebanese": "Liban", "Persian": "Iran",
    "Jamaican": "Jamaïque", "Peruvian": "Pérou", "Turkish": "Turquie", "Danish": "Danemark",
    "Swedish": "Suède", "Argentinian": "Argentine", "Norwegian": "Norvège", "Pakistani": "Pakistan",
    "Malaysian": "Malaisie", "Indonesian": "Indonésie", "Israeli": "Israël", "Chilean": "Chili",
    "Dutch": "Pays-Bas", "Austrian": "Autriche", "South African": "Afrique du Sud", "Finnish": "Finlande",
    "Bangladeshi": "Bangladesh", "Colombian": "Colombie", "Swiss": "Suisse", "Belgian": "Belgique",
    "Puerto Rican": "Porto Rico", "Australian and New Zealander": "Australie & Nlle-Zélande",
    "Scandinavian": "Scandinavie", "Soul Food": "Soul Food (USA)", "Cajun and Creole": "Cajun & Créole (USA)",
    "Tex-Mex": "Tex-Mex (USA)", "Southern Recipes": "Sud des USA", "Jewish": "Cuisine Juive",
    "Amish and Mennonite": "Amish & Mennonite",
}

st.title("Axe 4 — La viabilité des alternatives saines")
st.markdown("#### *Peut-on concilier légèreté diététique et haute satisfaction gustative ?*")

# 1. Filtres interactifs personnalisables
with st.expander("⚙️ Ajuster les critères d'une recette 'saine et bien notée'", expanded=False):
    col1, col2, col3, col4 = st.columns(4)
    cal_max = col1.number_input("Calories max (kcal)", 100, 1500, HEALTHY_CRITERIA["calories_max"], step=50)
    fat_max = col2.number_input("Lipides max (g)", 0, 100, HEALTHY_CRITERIA["fat_max_g"], step=5)
    rating_min = col3.slider("Note minimale (★)", 3.0, 5.0, HEALTHY_CRITERIA["min_rating"], 0.1)
    ratings_min = col4.number_input("Nombre d'avis min", 0, 500, HEALTHY_CRITERIA["min_total_ratings"], step=5)

all_recipes = load_processed("all_recipes_enriched")
cuisines = load_processed("cuisines_enriched")
mappable = cuisines[cuisines["map_type"] == "single_country"].copy()

# Traduction française des pays
mappable["country_fr"] = mappable["country"].map(COUNTRY_FR).fillna(mappable["country"])

def is_healthy(df):
    return (
        (df["calories"] <= cal_max)
        & (df["fat"] <= fat_max)
        & (df["avg_rating"] >= rating_min)
        & (df["total_ratings"] >= ratings_min)
    )

all_recipes["is_healthy"] = is_healthy(all_recipes)
mappable["is_healthy"] = is_healthy(mappable)

n_healthy_all = all_recipes["is_healthy"].sum()
total_all = len(all_recipes)
pct_all = n_healthy_all / total_all

# -------------------------------------------------------------
# VISUALISATION 1 : Partie d'un tout (Donut Chart)
# -------------------------------------------------------------
st.subheader("1. Quelle est la part des recettes saines dans le répertoire mondial ?")

col_kpi1, col_donut = st.columns([1, 2])

with col_kpi1:
    st.metric(
        "Recettes conformes",
        f"{n_healthy_all:,}".replace(",", " "),
        f"{pct_all:.1%} du catalogue total"
    )
    st.write(
        f"Pour être qualifiée de **saine et appréciée**, la recette doit cumuler : "
        f"≤ **{cal_max} kcal**, ≤ **{fat_max}g** de lipides, ≥ **{rating_min} ★** et au moins **{ratings_min}** avis."
    )

with col_donut:
    donut_df = pd.DataFrame({
        "Statut": ["Saines & bien notées", "Autres recettes"],
        "Nombre": [n_healthy_all, total_all - n_healthy_all]
    })
    fig_donut = px.pie(
        donut_df,
        names="Statut",
        values="Nombre",
        hole=0.65,
        color="Statut",
        color_discrete_map={
            "Saines & bien notées": "#10B981",
            "Autres recettes": "#E2E8F0"
        }
    )
    fig_donut.update_traces(textinfo="percent", hoverinfo="label+value+percent")
    fig_donut.update_layout(
        height=260,
        margin=dict(t=10, b=10, l=10, r=10),
        annotations=[dict(text=f"<b>{pct_all:.1%}</b><br>Saines", x=0.5, y=0.5, font_size=20, showarrow=False)],
        showlegend=True
    )
    st.plotly_chart(fig_donut, width="stretch")

st.divider()

# -------------------------------------------------------------
# VISUALISATION 2 : Classement des pays (Barres Horizontales - Top N aéré)
# -------------------------------------------------------------
st.subheader("2. Quels pays comptent la plus forte proportion d'alternatives saines ?")

col_sub, col_slider = st.columns([3, 2])
with col_sub:
    st.caption("Diagramme en barres horizontales trié — pays disposant d'au moins 15 recettes catégorisées.")
with col_slider:
    # Curseur pour découper la complexité (Séance 3 du cours)
    top_n = st.slider("Nombre de pays affichés (Top)", 5, 25, 10)

by_country_health = (
    mappable.groupby("country_fr")
    .agg(
        n_total=("name", "count"),
        n_healthy=("is_healthy", "sum"),
        cal_median=("calories", "median"),
        rating_mean=("avg_rating", "mean")
    )
    .assign(pct_healthy=lambda d: d["n_healthy"] / d["n_total"])
    .reset_index()
)

# On filtre les pays avec effectif suffisant, on trie, et on prend le Top N
by_country_filtered = (
    by_country_health[by_country_health["n_total"] >= 15]
    .sort_values("pct_healthy", ascending=True)
    .tail(top_n)
)

# Format d'étiquette compact en français
by_country_filtered["bar_label"] = by_country_filtered.apply(
    lambda r: f"{r['pct_healthy']:.1%}  ({int(r['n_healthy'])}/{int(r['n_total'])})",
    axis=1
)

fig_bar = px.bar(
    by_country_filtered,
    x="pct_healthy",
    y="country_fr",
    orientation="h",
    text="bar_label",
    color="pct_healthy",
    color_continuous_scale="Tealgrn",
    labels={"pct_healthy": "% de recettes saines", "country_fr": "Pays"},
)
fig_bar.update_traces(
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Part de recettes saines : %{x:.1%}<extra></extra>"
)

# Règle du cours : baseline à 0% et marge pour que le texte ne soit jamais tronqué
max_val = max(0.35, by_country_filtered["pct_healthy"].max() * 1.30)
fig_bar.update_xaxes(tickformat=".0%", range=[0, max_val])
fig_bar.update_layout(height=max(280, top_n * 35), coloraxis_showscale=False, yaxis_title=None)
st.plotly_chart(fig_bar, width="stretch")

# -------------------------------------------------------------
# VISUALISATION 3 : Matrice Santé vs Satisfaction (Quadrant 2D)
# -------------------------------------------------------------
st.divider()
st.subheader("3. Matrice de positionnement : Cuisines légères vs Cuisines adorées")
st.caption("Chaque bulle représente une gastronomie nationale (taille = nombre total de recettes analysées).")

valid_quad = by_country_health[by_country_health["n_total"] >= 15].copy()
med_cal = valid_quad["cal_median"].median()
med_rate = valid_quad["rating_mean"].median()

fig_quad = px.scatter(
    valid_quad,
    x="cal_median",
    y="rating_mean",
    size="n_total",
    text="country_fr",
    color="pct_healthy",
    color_continuous_scale="Tealgrn",
    labels={
        "cal_median": "Calories médianes par portion (kcal)",
        "rating_mean": "Note moyenne des recettes (★)",
        "n_total": "Recettes analysées",
        "pct_healthy": "% Sain"
    },
)
fig_quad.update_traces(
    textposition="top center",
    hovertemplate=(
        "<b>%{text}</b><br>"
        "Calories médianes : %{x:.0f} kcal<br>"
        "Note moyenne : %{y:.2f} ★<br>"
        "Part saine : %{marker.color:.1%}<extra></extra>"
    )
)

# Lignes de référence pour créer les 4 quadrants
fig_quad.add_vline(x=med_cal, line_dash="dot", line_color="#94A3B8")
fig_quad.add_hline(y=med_rate, line_dash="dot", line_color="#94A3B8")

# Balisage explicite en français des 4 quadrants
fig_quad.add_annotation(
    x=med_cal * 0.85, y=med_rate * 1.025,
    text="🏆 <b>Cuisines Vertueuses</b><br>(Légères & Très appréciées)",
    showarrow=False, font=dict(color="#047857", size=11), align="center"
)
fig_quad.add_annotation(
    x=med_cal * 1.20, y=med_rate * 1.025,
    text="🍔 <b>Plaisirs Coupables</b><br>(Riches & Très appréciées)",
    showarrow=False, font=dict(color="#B45309", size=11), align="center"
)
fig_quad.add_annotation(
    x=med_cal * 0.85, y=med_rate * 0.975,
    text="🥗 <b>Diététique mais clivante</b><br>(Légères mais notes modérées)",
    showarrow=False, font=dict(color="#64748B", size=11), align="center"
)
fig_quad.add_annotation(
    x=med_cal * 1.20, y=med_rate * 0.975,
    text="⚠️ <b>Zone critique</b><br>(Riches & Moins bien notées)",
    showarrow=False, font=dict(color="#DC2626", size=11), align="center"
)

fig_quad.update_layout(height=520, coloraxis_colorbar=dict(title="% Sain"))
st.plotly_chart(fig_quad, width="stretch")

# -------------------------------------------------------------
# TABLEAU DE DÉTAIL EN FRANÇAIS
# -------------------------------------------------------------
with st.expander("Consulter la liste détaillée des recettes saines sélectionnées"):
    cols_show = ["name", "country_fr", "calories", "fat", "avg_rating", "total_ratings", "url"]
    table_display = mappable[mappable["is_healthy"]][cols_show].sort_values("avg_rating", ascending=False).copy()
    table_display = table_display.rename(columns={
        "name": "Recette",
        "country_fr": "Pays d'origine",
        "calories": "Calories (kcal)",
        "fat": "Lipides (g)",
        "avg_rating": "Note (★)",
        "total_ratings": "Nombre d'avis",
        "url": "Lien Allrecipes"
    })
    st.dataframe(
        table_display,
        width="stretch",
        hide_index=True,
        column_config={
            "Lien Allrecipes": st.column_config.LinkColumn("Lien Allrecipes", display_text="Voir la recette")
        }
    )
