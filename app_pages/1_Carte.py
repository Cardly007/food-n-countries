import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.indicators import country_summary, excluded_from_map, staples
from src.labels import INGREDIENT_LABELS, MAP_TYPE_LABELS, label
from src.nutrition import THRESHOLDS
from src.theme import (
    INK_MUTED, MAX_COLOR_CATEGORIES, SEQUENTIAL, SEQUENTIAL_MAIN,
    apply_theme, chart_title, country_color_map, fmt_int, hide_grid,
)

st.title("Axe 1 — Diagnostic : d'où viennent les recettes ?")
st.markdown(
    "*D'où viennent les recettes étiquetées par pays, et leur base "
    "d'ingrédients diffère-t-elle d'un pays à l'autre ?*"
)

summary = country_summary()
excluded = excluded_from_map()

METRICS = {
    "n_recipes": {"fmt": ",.0f", "pct": False},
    "avg_rating": {"fmt": ".2f", "pct": False},
    "median_calories": {"fmt": ",.0f", "pct": False},
    "median_fat": {"fmt": ".1f", "pct": False},
    "median_carbs": {"fmt": ".1f", "pct": False},
    "pct_exceeds_calories": {"fmt": ".0%", "pct": True},
    "pct_exceeds_fat": {"fmt": ".0%", "pct": True},
    "pct_exceeds_carbs": {"fmt": ".0%", "pct": True},
    "pct_healthy_well_rated": {"fmt": ".0%", "pct": True},
    "avg_approx_n_items": {"fmt": ".1f", "pct": False},
}
THRESHOLD_NOTES = {
    "pct_exceeds_calories": f"seuil : {THRESHOLDS['calories_high']} kcal / portion",
    "pct_exceeds_fat": f"seuil : {THRESHOLDS['fat_high_g']} g / portion",
    "pct_exceeds_carbs": f"seuil : {THRESHOLDS['carbs_high_g']} g / portion",
    "avg_approx_n_items": "approximation : nombre de virgules + 1, à comparer entre pays uniquement",
}


def build_map(df: pd.DataFrame, metric: str) -> go.Figure:
    """Carte choroplèthe : LOCALISER (comparaison seulement approximative)."""
    fmt = METRICS[metric]["fmt"]
    fig = px.choropleth(
        df,
        locations="iso3",
        color=metric,
        hover_name="pays",
        hover_data={"iso3": False, metric: f":{fmt}", "n_recipes": True},
        labels={metric: label(metric), "n_recipes": label("n_recipes")},
        color_continuous_scale=SEQUENTIAL,
    )
    fig.update_geos(
        showframe=False, showcoastlines=False, showcountries=True,
        countrycolor="white", landcolor="#F2F2F2", showocean=False,
        projection_type="natural earth",
    )
    if METRICS[metric]["pct"]:
        fig.update_coloraxes(colorbar_tickformat=".0%")
    fig.update_coloraxes(colorbar_title_text="")
    apply_theme(fig, height=480)
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    return fig


def build_ranking(df: pd.DataFrame, metric: str) -> go.Figure:
    """Classement trié : COMPARER précisément (position / longueur)."""
    d = df.dropna(subset=[metric]).sort_values(metric, ascending=True)
    fmt = METRICS[metric]["fmt"]
    hover = f"<b>%{{y}}</b><br>{label(metric)} : %{{x:{fmt}}}<br>{label('n_recipes')} : %{{customdata}}<extra></extra>"
    if metric == "avg_rating":
        # Note moyenne : points sur un axe zoomé (une barre devrait partir de 0
        # et écraserait des écarts de quelques dixièmes).
        fig = go.Figure(go.Scatter(
            x=d[metric], y=d["pays"], mode="markers",
            marker=dict(color=SEQUENTIAL_MAIN, size=9),
            customdata=d["n_recipes"], hovertemplate=hover,
        ))
        lo = max(0, d[metric].min() - 0.1)
        fig.update_xaxes(range=[lo, 5], title_text=f"{label(metric)} — axe zoomé de {lo:.1f} à 5")
        fig.update_yaxes(showgrid=True)
    else:
        fig = go.Figure(go.Bar(
            x=d[metric], y=d["pays"], orientation="h",
            marker=dict(color=SEQUENTIAL_MAIN),
            customdata=d["n_recipes"], hovertemplate=hover,
        ))
        fig.update_xaxes(rangemode="tozero", title_text=label(metric))
        hide_grid(fig, "y")
    if METRICS[metric]["pct"]:
        fig.update_xaxes(tickformat=".0%")
    apply_theme(fig, height=max(400, 20 * len(d) + 80))
    fig.update_yaxes(title_text=None, tickfont=dict(size=12))
    return fig


def ingredient_order(df: pd.DataFrame) -> list[str]:
    return (
        df.groupby("ingredient_label")["pct_recipes"].mean()
        .sort_values(ascending=False).index.tolist()
    )


def build_staples_bars(df: pd.DataFrame, countries: list[str]) -> go.Figure:
    """Barres groupées : comparaison précise, ≤ 5 pays (couleurs fixes)."""
    colors = country_color_map(countries)
    fig = px.bar(
        df, x="ingredient_label", y="pct_recipes", color="pays", barmode="group",
        category_orders={"ingredient_label": ingredient_order(df), "pays": countries},
        color_discrete_map=colors,
        labels={"pct_recipes": label("pct_recipes"), "ingredient_label": label("ingredient"), "pays": "Pays"},
        hover_data={"pct_recipes": ":.0%"},
    )
    fig.update_yaxes(tickformat=".0%", rangemode="tozero")
    fig.update_traces(marker_line_color="white", marker_line_width=1)
    apply_theme(fig, height=450)
    hide_grid(fig, "x")
    fig.update_xaxes(title_text=None)
    return fig


def build_staples_heatmap(df: pd.DataFrame, countries: list[str]) -> go.Figure:
    """Heatmap pays × ingrédient : repérer des motifs, même échelle séquentielle."""
    order = ingredient_order(df)
    pivot = (
        df.pivot_table(index="pays", columns="ingredient_label", values="pct_recipes")
        .reindex(index=countries, columns=order)
    )
    fig = px.imshow(
        pivot, color_continuous_scale=SEQUENTIAL, zmin=0, zmax=1, aspect="auto",
        text_auto=".0%",
        labels={"color": label("pct_recipes"), "x": label("ingredient"), "y": "Pays"},
    )
    fig.update_coloraxes(colorbar_tickformat=".0%", colorbar_title_text="")
    fig.update_traces(xgap=2, ygap=2, textfont_size=11)
    apply_theme(fig, height=max(320, 26 * len(countries) + 120))
    hide_grid(fig)
    fig.update_xaxes(side="top", title_text=None)
    fig.update_yaxes(title_text=None)
    return fig


# --- 1. Localiser -------------------------------------------------------------
metric = st.selectbox(
    "Indicateur affiché",
    options=list(METRICS.keys()),
    format_func=label,
)
note = THRESHOLD_NOTES.get(metric)

col_map, col_rank = st.columns([3, 2])
with col_map:
    chart_title(
        f"Où se situent les pays étiquetés, et comment varie « {label(metric).lower()} » ?",
        "Plus le bleu est foncé, plus la valeur est élevée. Pays en gris clair : "
        "aucune recette étiquetée. La couleur ne permet qu'une comparaison "
        "approximative : voir le classement à droite."
        + (f" ({note})" if note else ""),
    )
    st.plotly_chart(build_map(summary, metric), width="stretch")
with col_rank:
    chart_title(
        "Quels pays se classent en tête sur cet indicateur ?",
        "Pays triés du plus élevé (en haut) au plus faible. "
        + ("Points : l'axe est zoomé pour lire des écarts de quelques dixièmes."
           if metric == "avg_rating" else "Longueur des barres à partir de 0."),
    )
    st.plotly_chart(build_ranking(summary, metric), width="stretch")

n_missing = summary[metric].isna().sum()
st.caption(
    f"{fmt_int(summary['n_recipes'].sum())} recettes réparties sur "
    f"{len(summary)} pays affichables sur la carte."
    + (f" {n_missing} pays sans valeur pour cet indicateur ne sont pas classés." if n_missing else "")
)

with st.expander(f"{fmt_int(excluded['n_recipes'].sum())} recettes non cartographiables — pourquoi ?",
                 icon=":material/warning:"):
    st.markdown(
        "Ces étiquettes ne correspondent pas à un pays unique et ne sont donc "
        "**pas affichées sur la carte** (voir Méthodologie). Elles restent "
        "prises en compte dans les recettes candidates de l'axe 4."
    )
    st.dataframe(
        excluded.assign(map_type=excluded["map_type"].map(MAP_TYPE_LABELS))[["pays", "map_type", "n_recipes"]]
        .rename(columns={"pays": "Étiquette", "map_type": label("map_type"), "n_recipes": label("n_recipes")}),
        width="stretch", hide_index=True,
    )

st.divider()

# --- 2. Comparer les ingrédients ----------------------------------------------
chart_title(
    "Les pays s'appuient-ils sur les mêmes ingrédients de base ?",
    "Part des recettes de chaque pays qui contiennent l'ingrédient (détection "
    "par mot-clé dans la liste d'ingrédients). Ingrédients triés par fréquence "
    "moyenne décroissante. Chaque pays garde la même couleur sur toutes les pages.",
)

st_df = staples().assign(ingredient_label=lambda d: d["ingredient"].map(INGREDIENT_LABELS))
by_size = summary.sort_values(["n_recipes", "country"], ascending=[False, True])["pays"].tolist()

c1, c2 = st.columns([3, 1])
view = c2.segmented_control(
    "Vue", ["Barres groupées", "Heatmap"], default="Barres groupées",
    help="Barres : comparaison précise de quelques pays. Heatmap : repérer des "
         "motifs sur beaucoup de pays (intensité = ordre de grandeur).",
)
show_all = c2.toggle("Heatmap : tous les pays", value=False, disabled=view != "Heatmap")
selected = c1.multiselect(
    f"Pays à comparer (au plus {MAX_COLOR_CATEGORIES})",
    options=sorted(summary["pays"].unique()),
    default=by_size[:MAX_COLOR_CATEGORIES],
    max_selections=MAX_COLOR_CATEGORIES,
)

if view == "Heatmap" and show_all:
    countries = by_size
else:
    countries = [c for c in by_size if c in selected]

if countries:
    subset = st_df[st_df["pays"].isin(countries)]
    if view == "Heatmap":
        st.plotly_chart(build_staples_heatmap(subset, countries), width="stretch")
    else:
        st.plotly_chart(build_staples_bars(subset, countries), width="stretch")
    st.caption(
        "Comment lire : si, pour un même ingrédient, les valeurs sont proches "
        "d'un pays à l'autre, la base d'ingrédients est commune ; si elles "
        "diffèrent nettement, chaque pays garde une base propre. "
        f"Liste de {st_df['ingredient'].nunique()} ingrédients de base, non "
        "exhaustive (voir Méthodologie)."
    )
else:
    st.info("Sélectionnez au moins un pays pour afficher le comparatif.")
