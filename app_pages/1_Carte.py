import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.insights import (
    build_insight_title_axe1, build_insight_title_axe1_counts, rank_countries, staple_spread,
)
from src.load_data import load_processed
from src.story import key_message, next_button, step_header
from src.theme import (
    ACCENT, COUNTRY_COLORS, MAP_TYPE_LABELS, NEUTRAL, SEQUENTIAL, SEQUENTIAL_LIGHT,
    apply_theme, chart_title, country_color, country_label, fmt_int, fmt_pct,
    ingredient_label, show,
)

STEP = 1
TOP_K = 3                     # pays mis en évidence (carte + barres)
N_BARS = 15                   # pays affichés dans le classement
DEFAULT_COUNTRIES = ["Italian", "Chinese", "Indian", "French"]
N_HEATMAP = 12                # pays de la heatmap (les plus représentés)

by_country = load_processed("by_country")
excluded = load_processed("excluded_from_map")
staples = load_processed("staple_frequency")
cuisines = load_processed("cuisines_enriched")
ranked = rank_countries(by_country)
top_countries = ranked.head(TOP_K)["country"].tolist()


# ---------------------------------------------------------------------------
# Graphiques (un choix = une fonction, facile à remplacer)
# ---------------------------------------------------------------------------

def build_map(by_country, highlight):
    """Choroplèthe une teinte (localiser) + annotation des pays en tête."""
    df = by_country.assign(pays=by_country["country"].map(country_label))
    fig = px.choropleth(
        df, locations="iso3", color="n_recipes", hover_name="pays",
        hover_data={"iso3": False, "n_recipes": True},
        color_continuous_scale=SEQUENTIAL, range_color=(0, df["n_recipes"].max()),
        labels={"n_recipes": "Recettes"},
    )
    top = df[df["country"].isin(highlight)]
    fig.add_trace(go.Scattergeo(
        locations=top["iso3"], mode="markers+text",
        text=top["pays"] + " (" + top["n_recipes"].astype(str) + ")",
        textposition="top center", textfont=dict(size=12, color="#222222"),
        marker=dict(size=9, color=ACCENT, line=dict(width=1, color="white")),
        hoverinfo="skip", showlegend=False,
    ))
    fig.update_geos(showframe=False, showcoastlines=False, showcountries=True,
                    countrycolor="white", showland=True, landcolor="#F2F2F2",
                    projection_type="natural earth", lataxis_range=[-58, 85])
    apply_theme(fig, height=430)
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0),
                      coloraxis_colorbar=dict(title="Recettes", thickness=12, len=0.6))
    return fig


def build_ranking_bars(ranked, highlight, n=N_BARS):
    """Barres horizontales triées (comparaison précise), gris + accent."""
    df = ranked.head(n).iloc[::-1].assign(pays=lambda d: d["country"].map(country_label))
    colors = [ACCENT if c in highlight else NEUTRAL for c in df["country"]]
    fig = go.Figure(go.Bar(
        x=df["n_recipes"], y=df["pays"], orientation="h", marker_color=colors,
        text=df["n_recipes"], textposition="outside", cliponaxis=False,
        hovertemplate="%{y} : %{x} recettes<extra></extra>",
    ))
    apply_theme(fig, height=430)
    fig.update_xaxes(range=[0, df["n_recipes"].max() * 1.15], title="Nombre de recettes",
                     showticklabels=False)
    return fig


def build_ingredient_dotplot(staples, countries, order):
    """Points par pays sur une même ligne par ingrédient (position = comparaison précise).

    Un trait gris relie le minimum au maximum : trait court = ingrédient
    utilisé dans des proportions voisines par tous les pays.
    """
    sub = staples[staples["country"].isin(countries)].copy()
    sub["ing"] = sub["ingredient"].map(ingredient_label)
    labels = [ingredient_label(i) for i in order]
    fig = go.Figure()
    rng = sub.groupby("ing")["pct_recipes"].agg(["min", "max"]).reindex(labels)
    for ing, row in rng.iterrows():
        fig.add_trace(go.Scatter(x=[row["min"], row["max"]], y=[ing, ing], mode="lines",
                                 line=dict(color=NEUTRAL, width=6), hoverinfo="skip",
                                 showlegend=False))
    for c in countries:
        d = sub[sub["country"] == c]
        fig.add_trace(go.Scatter(
            x=d["pct_recipes"], y=d["ing"], mode="markers", name=country_label(c),
            marker=dict(size=13, color=country_color(c), line=dict(width=1, color="white")),
            hovertemplate=f"{country_label(c)} · %{{y}} : %{{x:.0%}} des recettes<extra></extra>",
        ))
    apply_theme(fig, height=480, grid=False)
    fig.update_yaxes(categoryorder="array", categoryarray=labels[::-1], title=None)
    fig.update_xaxes(range=[0, 1], tickformat=".0%", showgrid=True, gridcolor="#EEEEEE",
                     title="Part des recettes du pays qui contiennent l'ingrédient")
    return fig


def build_ingredient_heatmap(staples, countries, order):
    """Vue d'ensemble pays × ingrédient (intensité = ordre de grandeur seulement)."""
    pv = (staples[staples["country"].isin(countries)]
          .pivot(index="country", columns="ingredient", values="pct_recipes")
          .reindex(index=countries, columns=order))
    fig = go.Figure(go.Heatmap(
        z=pv.values, x=[ingredient_label(i) for i in order],
        y=[country_label(c) for c in pv.index], colorscale=SEQUENTIAL_LIGHT, zmin=0, zmax=1,
        text=[[fmt_pct(v) for v in row] for row in pv.values], texttemplate="%{text}",
        textfont=dict(size=11), xgap=2, ygap=2,
        colorbar=dict(title="Part des<br>recettes", tickformat=".0%", thickness=12),
        hovertemplate="%{y} · %{x} : %{z:.0%}<extra></extra>",
    ))
    apply_theme(fig, height=40 * len(countries) + 120)
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(side="top")
    return fig


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

step_header(STEP)
st.title("L'étiquette promet la diversité…")

n_labels = cuisines["country"].nunique()
n_excluded = int(excluded["n_recipes"].sum())

# Sélection (dans l'expander plus bas) lue avant le calcul du message clé.
selected = st.session_state.get("axe1_countries", DEFAULT_COUNTRIES)
enough = len(selected) >= 2
compared = selected if enough else DEFAULT_COUNTRIES
spread = staple_spread(staples, compared)
ing_title, ing_subtitle = build_insight_title_axe1(spread, len(compared))

key_message(
    f"Le site range ses recettes sous {fmt_int(n_labels)} étiquettes « cuisine du monde », "
    f"dont {fmt_int(len(by_country))} pays. Derrière l'étiquette, la base d'ingrédients "
    f"change-t-elle vraiment ? <b>{ing_title}.</b>"
)

# --- Localiser -------------------------------------------------------------
count_title, count_subtitle = build_insight_title_axe1_counts(by_country, TOP_K)
chart_title(
    count_title,
    f"{count_subtitle}. Carte : couleur plus foncée = plus de recettes. "
    f"{fmt_int(n_excluded)} recettes dont l'étiquette n'est pas un pays ne sont pas cartographiées.",
)
col_map, col_bars = st.columns([3, 2])
with col_map:
    show(build_map(by_country, top_countries))
with col_bars:
    show(build_ranking_bars(ranked, top_countries))

with st.expander(f"Pourquoi {fmt_int(n_excluded)} recettes ne sont pas sur la carte ?"):
    st.markdown(
        "Certaines étiquettes ne désignent pas un pays : une région de plusieurs pays, "
        "une tradition régionale des États-Unis ou une communauté sans territoire. "
        "Elles restent comptées ailleurs, mais ne peuvent pas être placées sur une carte."
    )
    st.dataframe(
        excluded.assign(
            etiquette=excluded["country"].map(country_label),
            type=excluded["map_type"].map(MAP_TYPE_LABELS),
        )[["etiquette", "type", "n_recipes"]],
        column_config={
            "etiquette": "Étiquette", "type": "Type d'étiquette",
            "n_recipes": st.column_config.NumberColumn("Recettes"),
        },
        width="stretch", hide_index=True,
    )

# --- Comparer les ingrédients ---------------------------------------------
st.divider()
if enough:
    order = spread["ingredient"].tolist()  # du plus homogène au plus variable
    chart_title(
        ing_title,
        f"{ing_subtitle}. Chaque point = un pays ; trait gris = écart entre pays (court = proportions voisines). "
        "Ingrédients repérés par mot-clé dans la liste des ingrédients.",
    )
    show(build_ingredient_dotplot(staples, selected, order))
else:
    st.info("Choisissez au moins deux pays dans « Aller plus loin » pour comparer leurs ingrédients.")

with st.expander("Aller plus loin"):
    st.multiselect(
        "Pays comparés (cuisines ayant une couleur fixe dans toute l'application)",
        options=list(COUNTRY_COLORS),
        default=DEFAULT_COUNTRIES,
        format_func=country_label,
        key="axe1_countries",
        max_selections=len(COUNTRY_COLORS),
    )
    heat_countries = ranked.head(N_HEATMAP)["country"].tolist()
    heat_spread = staple_spread(staples, heat_countries)
    heat_title, heat_subtitle = build_insight_title_axe1(heat_spread, len(heat_countries))
    chart_title(
        f"Vue d'ensemble des {N_HEATMAP} pays les plus représentés : {heat_title[:1].lower()}{heat_title[1:]}",
        f"{heat_subtitle}. Couleur plus foncée = ingrédient plus fréquent ; colonnes rangées "
        "du plus homogène au plus variable.",
    )
    show(build_ingredient_heatmap(staples, heat_countries, heat_spread["ingredient"].tolist()))

next_button(STEP)
