import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.indicators import all_recipes, cuisines, healthy_mask, n_missing_criteria
from src.labels import label
from src.nutrition import HEALTHY_CRITERIA
from src.theme import (
    ACCENT, INK_MUTED, NEUTRAL, apply_theme, chart_title, fmt_int, fmt_num, fmt_pct, hide_grid, kpi,
)

MIN_RECIPES_PER_COUNTRY = 15   # évite des parts calculées sur trop peu de recettes
N_ACCENT = 5                   # pays mis en évidence en tête de classement

st.title("Axe 4 — Décision : quelles recettes mettre en avant ?")
st.markdown("*Combien de recettes sont à la fois saines et bien notées, et dans quels pays ?*")

st.caption(
    "Critères par défaut (réglables ci-dessous, voir Méthodologie) : "
    f"calories ≤ {HEALTHY_CRITERIA['calories_max']} kcal / portion, "
    f"lipides ≤ {HEALTHY_CRITERIA['fat_max_g']} g / portion, "
    f"note ≥ {fmt_num(HEALTHY_CRITERIA['min_rating'], 1)}, "
    f"au moins {HEALTHY_CRITERIA['min_total_ratings']} avis."
)

c1, c2, c3, c4 = st.columns(4)
cal_max = c1.number_input("Calories max (kcal / portion)", 100, 1500, HEALTHY_CRITERIA["calories_max"], step=50)
fat_max = c2.number_input("Lipides max (g / portion)", 0, 100, HEALTHY_CRITERIA["fat_max_g"], step=5)
rating_min = c3.slider("Note minimale (sur 5)", 3.0, 5.0, HEALTHY_CRITERIA["min_rating"], 0.1)
ratings_min = c4.number_input("Nombre d'avis minimal", 0, 500, HEALTHY_CRITERIA["min_total_ratings"], step=10)
criteria = dict(cal_max=cal_max, fat_max=fat_max, rating_min=rating_min, ratings_min=ratings_min)

general = all_recipes()
labelled = cuisines()
mappable = labelled[labelled["map_type"] == "single_country"]

healthy_general = general[healthy_mask(general, **criteria)]
healthy_mappable = mappable[healthy_mask(mappable, **criteria)]

# --- KPI --------------------------------------------------------------------------
k1, k2 = st.columns(2)
kpi(
    "Recettes générales saines et bien notées",
    fmt_int(len(healthy_general)),
    subtitle=f"{fmt_pct(len(healthy_general) / len(general), 1)} des {fmt_int(len(general))} recettes générales",
    help=f"{fmt_int(n_missing_criteria(general))} recettes générales n'ont pas toutes les "
         "valeurs nécessaires (calories, lipides, note, avis) et ne peuvent pas être retenues.",
    container=k1,
)
kpi(
    "Recettes étiquetées par pays saines et bien notées",
    fmt_int(len(healthy_mappable)),
    subtitle=f"{fmt_pct(len(healthy_mappable) / len(mappable), 1)} des {fmt_int(len(mappable))} "
             "recettes rattachées à un pays unique",
    help=f"{fmt_int(n_missing_criteria(mappable))} de ces recettes n'ont pas toutes les "
         "valeurs nécessaires et ne peuvent pas être retenues.",
    container=k2,
)

st.divider()


def country_health(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.assign(_ok=healthy_mask(df, **criteria))
        .groupby("pays")
        .agg(n_total=("name", "count"), n_healthy=("_ok", "sum"))
        .assign(pct_healthy=lambda d: d["n_healthy"] / d["n_total"])
        .reset_index()
    )


def build_country_bars(d: pd.DataFrame) -> go.Figure:
    """Part de recettes saines et bien notées par pays : gris + accent sur les premiers."""
    d = d.sort_values(["pct_healthy", "n_healthy"], ascending=False).reset_index(drop=True)
    colors = [ACCENT if i < N_ACCENT and v > 0 else NEUTRAL for i, v in enumerate(d["pct_healthy"])]
    d = d.iloc[::-1]
    colors = colors[::-1]
    fig = go.Figure(go.Bar(
        x=d["pct_healthy"], y=d["pays"], orientation="h", marker_color=colors,
        text=[f"{h} / {t}" for h, t in zip(d["n_healthy"], d["n_total"])],
        textposition="outside", textfont=dict(color=INK_MUTED, size=11), cliponaxis=False,
        customdata=d[["n_healthy", "n_total"]].to_numpy(),
        hovertemplate="<b>%{y}</b><br>%{x:.0%} des recettes du pays<br>"
                      "%{customdata[0]} recettes retenues sur %{customdata[1]}<extra></extra>",
    ))
    apply_theme(fig, height=max(320, 20 * len(d) + 100))
    fig.update_xaxes(tickformat=".0%", rangemode="tozero", title_text=label("pct_healthy_well_rated"))
    fig.update_yaxes(title_text=None, tickfont=dict(size=12))
    hide_grid(fig, "y")
    return fig


ch = country_health(mappable)
shown = ch[ch["n_total"] >= MIN_RECIPES_PER_COUNTRY]
chart_title(
    "Dans quels pays trouve-t-on la plus forte part de recettes saines et bien notées ?",
    f"Part des recettes du pays qui remplissent les 4 critères choisis, pays triés "
    f"par part décroissante, axe à partir de 0. Orange : les {N_ACCENT} premiers pays ; "
    "gris : les autres. À droite de chaque barre : recettes retenues / recettes du pays.",
)
st.plotly_chart(build_country_bars(shown), width="stretch")
st.caption(
    f"Pays avec au moins {MIN_RECIPES_PER_COUNTRY} recettes étiquetées "
    f"({len(shown)} sur {len(ch)}), pour éviter des parts calculées sur trop "
    "peu de recettes. Les recettes sans valeur pour un critère ne sont pas retenues."
)

st.divider()

# --- Conclusion : recettes candidates -----------------------------------------------
st.subheader("Quelles recettes mettre en avant ?")
st.markdown(
    "Recettes étiquetées par pays qui remplissent les critères choisis ci-dessus, "
    "triées par note puis par nombre d'avis. Filtrez par pays ou par nom pour "
    "construire une sélection éditoriale."
)

include_other = st.toggle(
    "Inclure les étiquettes qui ne sont pas des pays (Tex-Mex, Soul food, cuisine juive…)",
    value=False,
)
pool = labelled if include_other else mappable
candidates = pool[healthy_mask(pool, **criteria)]

f1, f2 = st.columns([2, 1])
countries_filter = f1.multiselect(
    "Pays", sorted(candidates["pays"].unique()), placeholder="Tous les pays",
)
search = f2.text_input("Rechercher dans le nom de la recette", placeholder="ex. : soup, salad…")
if countries_filter:
    candidates = candidates[candidates["pays"].isin(countries_filter)]
if search:
    candidates = candidates[candidates["name"].str.contains(search, case=False, na=False, regex=False)]

COLS = ["name", "pays", "calories", "fat", "avg_rating", "total_ratings", "url"]
table = (
    candidates.sort_values(["avg_rating", "total_ratings"], ascending=False)[COLS]
    .rename(columns={c: label(c) for c in COLS})
)
st.caption(
    f"{fmt_int(len(table))} recettes candidates — critères : calories ≤ {cal_max} kcal, "
    f"lipides ≤ {fat_max} g, note ≥ {fmt_num(rating_min, 1)}, au moins {ratings_min} avis."
)
st.dataframe(
    table,
    width="stretch", hide_index=True,
    column_config={
        label("calories"): st.column_config.NumberColumn(format="%.0f"),
        label("fat"): st.column_config.NumberColumn(format="%.0f"),
        label("avg_rating"): st.column_config.NumberColumn(format="%.2f"),
        label("total_ratings"): st.column_config.NumberColumn(format="%d"),
        label("url"): st.column_config.LinkColumn(display_text="Ouvrir la recette"),
    },
)
st.download_button(
    "Télécharger la sélection (CSV)",
    table.to_csv(index=False).encode("utf-8"),
    file_name="recettes_candidates.csv",
    mime="text/csv",
    icon=":material/download:",
)
