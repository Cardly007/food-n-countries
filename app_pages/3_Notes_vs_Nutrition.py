import numpy as np
import plotly.graph_objects as go
import streamlit as st

from src.insights import (
    build_insight_title_axe3, build_insight_title_comfort, build_key_message_axe3,
    comfort_comparison, spearman_summary,
)
from src.load_data import load_processed
from src.story import key_message, next_button, step_header
from src.theme import (
    ACCENT, COLUMN_LABELS, NEUTRAL, TEXT_MUTED, apply_theme, chart_title, fmt_int, fmt_num, show,
)

STEP = 3
SAMPLE_SIZE = 3000
DEFAULT_MIN_RATINGS = 10
X_CLIP_QUANTILE = 0.99        # l'axe X s'arrête au 99e centile (lisibilité)
POPULATIONS = {
    "all": "Recettes générales",
    "cuisines": "Recettes étiquetées par pays",
}


# ---------------------------------------------------------------------------
# Graphiques
# ---------------------------------------------------------------------------

def build_scatter(df, x, y_range, x_max):
    """Nuage de points (échantillon) + tendance calculée sur TOUTES les recettes.

    Points gris (contexte) ; la droite de tendance en orange porte le message :
    une droite presque plate = lien très faible.
    """
    d = df.dropna(subset=[x, "avg_rating"])
    sample = d.sample(min(SAMPLE_SIZE, len(d)), random_state=0)
    slope, intercept = np.polyfit(d[x], d["avg_rating"], 1)
    xs = np.array([0, x_max])
    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=sample[x], y=sample["avg_rating"], mode="markers",
        marker=dict(size=5, color=NEUTRAL, opacity=0.5), showlegend=False,
        hovertemplate=f"%{{x:.0f}} · note %{{y:.2f}}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=xs, y=intercept + slope * xs, mode="lines", showlegend=False,
        line=dict(color=ACCENT, width=3), hoverinfo="skip",
    ))
    apply_theme(fig, height=400, grid=True)
    fig.update_xaxes(range=[0, x_max], title=COLUMN_LABELS[x])
    fig.update_yaxes(range=y_range, title=f"{COLUMN_LABELS['avg_rating']} — axe zoomé")
    return fig


def build_comfort_dots(comp, y_range):
    """Moyenne des notes avec / sans ingrédient « réconfort » (points + IC 95 %)."""
    fig = go.Figure()
    for _, r in comp.iterrows():
        color = ACCENT if r["has_comfort_ingredient"] else TEXT_MUTED
        fig.add_trace(go.Scatter(
            x=[r["groupe"]], y=[r["mean"]], mode="markers+text",
            marker=dict(size=16, color=color),
            error_y=dict(type="data", array=[r["ci95"]], color=color, thickness=2, width=10),
            text=[f"{fmt_num(r['mean'], 2)} / 5<br>({fmt_int(r['count'])} recettes)"],
            textposition="middle right", showlegend=False,
            hovertemplate=f"{r['groupe']} : %{{y:.3f}}<extra></extra>",
        ))
    apply_theme(fig, height=340, grid=True)
    fig.update_yaxes(range=y_range, title=f"{COLUMN_LABELS['avg_rating']} — axe zoomé")
    fig.update_xaxes(title=None, range=[-0.4, 1.9])  # marge à droite pour les étiquettes
    return fig


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

step_header(STEP)
st.title("… et la communauté note-t-elle mieux les recettes riches ?")

population = st.session_state.get("axe3_population", "all")
min_ratings = st.session_state.get("axe3_min_ratings", DEFAULT_MIN_RATINGS)

raw = load_processed("all_recipes_enriched" if population == "all" else "cuisines_enriched")
df = raw[raw["total_ratings"] >= min_ratings]
n_excluded = len(raw) - len(df)

corr_cal = spearman_summary(df, "calories")
corr_carbs = spearman_summary(df, "carbs")
key_message(build_key_message_axe3([corr_cal, corr_carbs]))

st.warning(
    "**Prudence avant de conclure.** Le site ne dit pas si une recette est un dessert ou un plat : "
    "une partie du lien (ou de l'absence de lien) peut venir des desserts, à la fois riches et "
    "souvent très bien notés. Et une corrélation ne dit jamais pourquoi deux choses vont ensemble.",
    icon=":material/warning:",
)

# Échelles communes aux deux nuages (mêmes axes Y pour comparer).
y_low = np.floor(df["avg_rating"].quantile(0.01) * 2) / 2
y_range = [y_low, 5.05]
x_max = {x: float(df[x].quantile(X_CLIP_QUANTILE)) for x in ("calories", "carbs")}
n_below = int((df["avg_rating"] < y_low).sum())

st.caption(
    f"{POPULATIONS[population]} ayant au moins {fmt_int(min_ratings)} avis : {fmt_int(len(df))} recettes "
    f"({fmt_int(n_excluded)} écartées faute d'avis suffisants). Chaque nuage montre un **échantillon "
    f"de {fmt_int(min(SAMPLE_SIZE, len(df)))} recettes sur {fmt_int(len(df))}** ; la droite orange est "
    f"calculée sur toutes. Axe des notes zoomé à partir de {fmt_num(y_low, 1)} ({fmt_int(n_below)} recettes "
    f"notées plus bas hors cadre) ; axe horizontal arrêté "
    f"au 99e centile (les 1 % de recettes les plus riches ne sont pas affichées)."
)

col1, col2 = st.columns(2)
with col1:
    t, s = build_insight_title_axe3(corr_cal, "en calories")
    chart_title(t, s)
    show(build_scatter(df, "calories", y_range, x_max["calories"]))
with col2:
    t, s = build_insight_title_axe3(corr_carbs, "en glucides")
    chart_title(t, s + " — les glucides servent d'indice du sucre, absent des données")
    show(build_scatter(df, "carbs", y_range, x_max["carbs"]))

st.divider()
comp = comfort_comparison(df)
t, s = build_insight_title_comfort(df)
chart_title(
    t,
    f"{s}. Point = note moyenne ; barre = marge d'incertitude à 95 %. "
    "Ingrédients « réconfort » : beurre, crème, fromage, bacon, mayonnaise (repérés par mot-clé).",
)
lo = (comp["mean"] - comp["ci95"]).min()
hi = (comp["mean"] + comp["ci95"]).max()
pad = max(0.05, (hi - lo))
show(build_comfort_dots(comp, [lo - pad, hi + pad]))
st.caption(
    f"Attention : l'axe vertical ne couvre que {fmt_num(2 * pad + hi - lo, 2)} étoile, pour rendre "
    "l'écart visible ; sur une échelle de 0 à 5, les deux points seraient confondus."
)

with st.expander("Aller plus loin"):
    c1, c2 = st.columns(2)
    c1.radio("Recettes analysées", list(POPULATIONS), format_func=POPULATIONS.get,
             key="axe3_population", horizontal=True)
    c2.slider(
        "Nombre minimum d'avis pour inclure une recette", 0, 200, key="axe3_min_ratings",
        value=DEFAULT_MIN_RATINGS,
        help="Une recette notée 5 par 2 personnes n'est pas comparable à une recette notée 4,6 "
             "par 500 personnes : on écarte les recettes trop peu notées.",
    )

next_button(STEP)
