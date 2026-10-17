import plotly.graph_objects as go
import streamlit as st

from src.insights import (
    build_insight_title_axe2, build_insight_title_axe2_thresholds, build_key_message_axe2,
    nutrient_convergence,
    rank_countries, threshold_rates,
)
from src.load_data import load_processed
from src.nutrition import THRESHOLDS
from src.story import key_message, next_button, step_header
from src.theme import (
    ACCENT, ALERT, COLUMN_LABELS, NEUTRAL, NUTRIENT_SHORT, NUTRIENT_UNIT, apply_theme,
    chart_title, country_label, fmt_int, fmt_num, fmt_pct, show,
)

STEP = 2
DEFAULT_N_COUNTRIES = 8

cuisines = load_processed("cuisines_enriched")
mappable = cuisines[cuisines["map_type"] == "single_country"]
ranked = rank_countries(load_processed("by_country"))


# ---------------------------------------------------------------------------
# Graphiques
# ---------------------------------------------------------------------------

def build_boxplots(df, countries, nutrient, global_median):
    """Boîtes à moustaches par pays + ligne de référence = médiane globale.

    Boîtes grises (le pays est déjà sur l'axe : pas de double encodage) ;
    l'accent orange est réservé à la médiane globale, qui porte le message
    (boîtes alignées sur la ligne = profils qui convergent).
    """
    unit = NUTRIENT_UNIT[nutrient]
    fig = go.Figure()
    upper = 0
    for c in countries:
        v = df.loc[df["country"] == c, nutrient].dropna()
        q1, q3 = v.quantile([0.25, 0.75])
        upper = max(upper, min(v.max(), q3 + 1.5 * (q3 - q1)))
        fig.add_trace(go.Box(
            y=v, name=country_label(c), boxpoints=False, marker_color=NEUTRAL,
            line=dict(color="#7A7A7A", width=1.5), fillcolor=NEUTRAL, showlegend=False,
            hovertemplate=f"{country_label(c)}<br>%{{y}} {unit}<extra></extra>",
        ))
    fig.add_hline(y=global_median, line=dict(color=ACCENT, width=3, dash="dash"),
                  annotation_text=f"Médiane, tous pays : {fmt_num(global_median, 0)} {unit}",
                  annotation_position="top right", annotation_bgcolor="white",
                  annotation_font=dict(color="#222222", size=13))
    apply_theme(fig, height=460, grid=True)
    fig.update_yaxes(range=[0, upper * 1.05], title=COLUMN_LABELS[nutrient])
    return fig


def build_threshold_bars(per, global_rate):
    """Barres horizontales triées ; alerte (vermillon) seulement au-dessus de la moyenne."""
    df = per.iloc[::-1].assign(pays=lambda d: d["country"].map(country_label))
    colors = [ALERT if r > global_rate else NEUTRAL for r in df["rate"]]
    fig = go.Figure(go.Bar(
        x=df["rate"], y=df["pays"], orientation="h", marker_color=colors,
        text=[fmt_pct(r) for r in df["rate"]], textposition="outside", cliponaxis=False,
        customdata=df["n"], hovertemplate="%{y} : %{x:.0%} (sur %{customdata} recettes)<extra></extra>",
    ))
    fig.add_vline(x=global_rate, line=dict(color="#222222", width=1.5, dash="dot"))
    apply_theme(fig, height=40 * len(df) + 80)
    fig.update_xaxes(range=[0, max(df["rate"].max(), global_rate) * 1.2], tickformat=".0%",
                     title="Part des recettes au-delà du seuil")
    return fig


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

step_header(STEP)
st.title("… mais les profils nutritionnels se ressemblent-ils ?")

nutrient = st.session_state.get("axe2_nutrient", "calories")
n_countries = st.session_state.get("axe2_n", DEFAULT_N_COUNTRIES)
countries = ranked.head(n_countries)["country"].tolist()

conv = nutrient_convergence(mappable, nutrient)
title, subtitle = build_insight_title_axe2(conv)
key_message(build_key_message_axe2(conv))

chart_title(
    title,
    f"{subtitle} Graphique : les {n_countries} pays les plus représentés ; chaque boîte = la moitié "
    f"centrale des recettes du pays, trait = médiane. {fmt_int(conv['n_missing'])} recettes sans "
    f"valeur de {NUTRIENT_SHORT[nutrient]} sont écartées.",
)
show(build_boxplots(mappable, countries, nutrient, conv["global_median"]))
st.caption("Lecture : plus les boîtes sont alignées sur la ligne orange, plus les pays se ressemblent.")

st.info(
    "Prudence : le site ne dit pas si une recette est un dessert ou un plat. Un pays avec "
    "beaucoup de desserts paraîtra plus sucré ou plus calorique, sans que sa cuisine le soit.",
    icon=":material/info:",
)

with st.expander("Aller plus loin"):
    c1, c2 = st.columns(2)
    c1.radio("Variable comparée", list(NUTRIENT_SHORT), key="axe2_nutrient",
             format_func=lambda k: COLUMN_LABELS[k], horizontal=True)
    c2.slider("Nombre de pays affichés", 4, 10, key="axe2_n", value=DEFAULT_N_COUNTRIES)

    seuil = st.radio(
        "Seuil indicatif par portion",
        ["calories", "fat"],
        format_func=lambda k: (f"Calories > {THRESHOLDS['calories_high']} kcal" if k == "calories"
                               else f"Lipides > {THRESHOLDS['fat_high_g']} g"),
        horizontal=True,
    )
    flag = "exceeds_calories" if seuil == "calories" else "exceeds_fat"
    seuil_txt = (f"{THRESHOLDS['calories_high']} kcal" if seuil == "calories"
                 else f"{THRESHOLDS['fat_high_g']} g de lipides")
    per, global_rate = threshold_rates(mappable, flag, seuil, countries)
    t_title, t_subtitle = build_insight_title_axe2_thresholds(per, global_rate, seuil_txt)
    chart_title(t_title, t_subtitle + " Vermillon = au-dessus de la moyenne.")
    show(build_threshold_bars(per, global_rate))

next_button(STEP)
