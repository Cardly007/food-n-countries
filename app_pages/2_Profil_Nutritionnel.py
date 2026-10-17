import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.indicators import (
    THRESHOLD_BY_NUTRIENT, country_summary, global_exceed_rate, mappable_cuisines,
)
from src.labels import NUTRIENT_SHORT, NUTRIENT_UNIT, label
from src.theme import (
    ACCENT, INK_MUTED, NEUTRAL, REFERENCE_LINE, SEQUENTIAL_MAIN,
    apply_theme, chart_title, fmt_int, fmt_num, fmt_pct, hide_grid,
)

st.title("Axe 2 — Test : les pays gardent-ils un profil nutritionnel propre ?")
st.markdown("*Les recettes de chaque pays gardent-elles un profil nutritionnel propre ?*")

mappable = mappable_cuisines()
summary = country_summary()
by_size = summary.sort_values(["n_recipes", "country"], ascending=[False, True])

top_n = st.slider(
    "Nombre de pays affichés (les plus représentés en nombre de recettes)",
    3, len(by_size), min(8, len(by_size)),
)
countries = by_size.head(top_n)["pays"].tolist()
subset = mappable[mappable["pays"].isin(countries)]


def build_boxplots(df: pd.DataFrame, nutrient: str, global_median: float) -> go.Figure:
    """Boîtes à moustaches par pays + médiane globale en référence."""
    order = df.groupby("pays")[nutrient].median().sort_values(ascending=False).index.tolist()
    unit = NUTRIENT_UNIT[nutrient]
    fig = go.Figure()
    for pays in order:
        fig.add_trace(go.Box(
            y=df.loc[df["pays"] == pays, nutrient], name=pays,
            marker_color=SEQUENTIAL_MAIN, fillcolor="rgba(0,114,178,0.15)",
            line=dict(width=1.5), boxpoints=False, showlegend=False,
            hovertemplate=f"<b>{pays}</b><br>%{{y:.0f}} {unit}<extra></extra>",
        ))
    fig.add_hline(
        y=global_median, line=dict(color=REFERENCE_LINE, width=1.5, dash="dash"),
        annotation_text=f"Médiane, tous pays : {fmt_num(global_median, 0)} {unit}",
        annotation_position="top left", annotation_font_color=INK_MUTED,
        annotation_bgcolor="rgba(255,255,255,0.85)",
    )
    apply_theme(fig, height=500)
    fig.update_yaxes(title_text=label(nutrient), rangemode="tozero")
    fig.update_xaxes(title_text=None)
    hide_grid(fig, "x")
    return fig


def build_threshold_bars(df: pd.DataFrame, nutrient: str, global_rate: float) -> go.Figure:
    """Part des recettes au-dessus d'un seuil, pays triés ; accent au-dessus du taux global."""
    col = f"pct_exceeds_{nutrient}"
    d = df.dropna(subset=[col]).sort_values(col, ascending=True)
    colors = [ACCENT if v > global_rate else NEUTRAL for v in d[col]]
    fig = go.Figure(go.Bar(
        x=d[col], y=d["pays"], orientation="h", marker_color=colors,
        customdata=d[[f"n_known_{nutrient}", f"n_missing_{nutrient}"]].to_numpy(),
        hovertemplate=(
            "<b>%{y}</b><br>%{x:.0%} des recettes renseignées"
            "<br>%{customdata[0]} recettes renseignées, %{customdata[1]} sans valeur<extra></extra>"
        ),
    ))
    fig.add_vline(
        x=global_rate, line=dict(color=REFERENCE_LINE, width=1.5, dash="dash"),
        annotation_text=f"Tous pays : {fmt_pct(global_rate)}",
        annotation_position="top", annotation_font_color=INK_MUTED,
    )
    apply_theme(fig, height=max(320, 28 * len(d) + 100))
    fig.update_xaxes(tickformat=".0%", rangemode="tozero", title_text=label(col))
    fig.update_yaxes(title_text=None)
    hide_grid(fig, "y")
    return fig


tab1, tab2 = st.tabs(["Dispersion par pays", "Dépassement de seuils"])

with tab1:
    nutrient = st.radio(
        "Nutriment", list(NUTRIENT_SHORT), format_func=NUTRIENT_SHORT.get, horizontal=True,
    )
    global_median = mappable[nutrient].median()
    chart_title(
        f"Les pays ont-ils des valeurs de {NUTRIENT_SHORT[nutrient].lower()} différentes ?",
        f"Chaque boîte couvre la moitié centrale des recettes du pays (trait = médiane, "
        f"moustaches = valeurs courantes, valeurs extrêmes masquées), en "
        f"{NUTRIENT_UNIT[nutrient]} par portion. Pays triés par médiane décroissante. "
        f"Ligne pointillée = médiane de toutes les recettes des {len(summary)} pays.",
    )
    st.plotly_chart(build_boxplots(subset, nutrient, global_median), width="stretch")
    n_missing = int(subset[nutrient].isna().sum())
    st.caption(
        "Comment lire : si les boîtes sont alignées autour de la ligne pointillée, "
        "les profils convergent ; une boîte nettement au-dessus ou au-dessous "
        "signale un profil propre au pays."
        + (f" {fmt_int(n_missing)} recettes sans valeur de {NUTRIENT_SHORT[nutrient].lower()} "
           "ne sont pas représentées." if n_missing else "")
    )

with tab2:
    thr_nutrient = st.radio(
        "Seuil", list(THRESHOLD_BY_NUTRIENT),
        format_func=lambda n: f"{NUTRIENT_SHORT[n]} > {THRESHOLD_BY_NUTRIENT[n]} {NUTRIENT_UNIT[n]} / portion",
        horizontal=True,
    )
    rate = global_exceed_rate(thr_nutrient)
    chart_title(
        f"Dans quels pays les recettes dépassent-elles le plus souvent le seuil de "
        f"{NUTRIENT_SHORT[thr_nutrient].lower()} ({THRESHOLD_BY_NUTRIENT[thr_nutrient]} "
        f"{NUTRIENT_UNIT[thr_nutrient]} / portion) ?",
        "Part des recettes renseignées du pays au-dessus du seuil, pays triés par "
        "part décroissante, axe à partir de 0. Orange : pays au-dessus de la part "
        "observée sur l'ensemble des pays (ligne pointillée) ; gris : en dessous.",
    )
    st.plotly_chart(
        build_threshold_bars(summary[summary["pays"].isin(countries)], thr_nutrient, rate),
        width="stretch",
    )
    n_miss = int(summary[summary["pays"].isin(countries)][f"n_missing_{thr_nutrient}"].sum())
    if n_miss:
        st.caption(
            f"{fmt_int(n_miss)} recettes sans valeur de {NUTRIENT_SHORT[thr_nutrient].lower()} "
            "sont exclues du calcul (et non comptées comme « sous le seuil »)."
        )
    st.caption("Seuils indicatifs (voir Méthodologie). Les glucides servent de proxy du sucre, "
               "faute de colonne dédiée.")

st.divider()
st.warning(
    "Rappel : le jeu de données n'indique pas la catégorie de plat (dessert, "
    "plat principal…). Un pays sur-représenté en desserts aura mécaniquement "
    "plus de recettes riches en glucides, sans que cela traduise une "
    "spécificité culinaire nationale. À traiter comme une limite plutôt que "
    "comme une conclusion définitive.",
    icon=":material/warning:",
)
