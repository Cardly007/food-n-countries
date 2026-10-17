import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.indicators import all_recipes, cuisines, describe_spearman, mean_with_ci, spearman
from src.labels import label
from src.theme import (
    ACCENT, INK_MUTED, NEUTRAL, SEQUENTIAL_MAIN,
    apply_theme, chart_title, fmt_int, fmt_num, hide_grid,
)

SAMPLE_SIZE = 3000
X_CLIP_QUANTILE = 0.99

st.title("Axe 3 — Hypothèse : les recettes les plus riches sont-elles mieux notées ?")
st.markdown("*Les recettes les plus riches sont-elles mieux notées ?*")

general, labelled = all_recipes(), cuisines()
POPULATIONS = {
    f"Recettes générales ({fmt_int(len(general))})": general,
    f"Recettes étiquetées par pays ({fmt_int(len(labelled))})": labelled,
}
source = st.segmented_control("Population analysée", list(POPULATIONS), default=list(POPULATIONS)[0])
df = POPULATIONS[source or list(POPULATIONS)[0]]

min_ratings = st.slider(
    "Nombre minimum d'avis pour inclure une recette",
    0, 200, 10,
    help="Une recette avec 2 avis à 5 étoiles n'est pas comparable à une "
         "recette avec 500 avis à 4,6. On filtre les recettes peu notées "
         "pour éviter un signal bruité.",
)
df = df[df["total_ratings"] >= min_ratings]
rated = df.dropna(subset=["avg_rating"])

# Même axe Y pour les deux nuages de points (comparaison directe).
Y_RANGE = [np.floor(rated["avg_rating"].min() * 2) / 2 - 0.05, 5.05] if len(rated) else [0, 5.05]


def build_scatter(d: pd.DataFrame, x: str) -> tuple[go.Figure, dict]:
    """Nuage de points sur un échantillon + droite de tendance calculée sur TOUTES les recettes."""
    d = d.dropna(subset=[x, "avg_rating"])
    x_max = d[x].quantile(X_CLIP_QUANTILE) if len(d) else 0
    sample = d.sample(min(SAMPLE_SIZE, len(d)), random_state=0)
    fig = go.Figure(go.Scattergl(
        x=sample[x], y=sample["avg_rating"], mode="markers",
        marker=dict(color=SEQUENTIAL_MAIN, size=5, opacity=0.25),
        text=sample["name"],
        hovertemplate=f"<b>%{{text}}</b><br>{label(x)} : %{{x:.0f}}<br>Note : %{{y:.2f}}<extra></extra>",
        name="Recette (échantillon)", showlegend=False,
    ))
    if len(d) >= 3:
        slope, intercept = np.polyfit(d[x], d["avg_rating"], 1)
        xs = np.array([0, x_max])
        fig.add_trace(go.Scatter(
            x=xs, y=intercept + slope * xs, mode="lines",
            line=dict(color=ACCENT, width=2.5), name="Tendance linéaire (toutes les recettes)",
            hoverinfo="skip",
        ))
    apply_theme(fig, height=430)
    fig.update_xaxes(title_text=label(x), range=[0, x_max])
    fig.update_yaxes(title_text=f"{label('avg_rating')} — axe zoomé", range=Y_RANGE)
    info = {"n": len(d), "n_sample": len(sample), "n_clipped": int((d[x] > x_max).sum()), "x_max": x_max}
    return fig, info


def scatter_caption(info: dict) -> str:
    return (
        f"Échantillon aléatoire de {fmt_int(info['n_sample'])} recettes sur "
        f"{fmt_int(info['n'])} affichées (lisibilité) ; la tendance et ρ sont "
        f"calculés sur les {fmt_int(info['n'])}. Axe horizontal limité à "
        f"{fmt_int(info['x_max'])} (99e centile) : {fmt_int(info['n_clipped'])} "
        "recettes au-delà ne sont pas dessinées."
    )


def build_comfort_points(d: pd.DataFrame) -> go.Figure:
    """Note moyenne avec / sans ingrédient « réconfort » : points + IC 95 %."""
    groups = [
        ("Sans ingrédient réconfort", d.loc[~d["has_comfort_ingredient"], "avg_rating"], NEUTRAL),
        ("Avec ingrédient réconfort", d.loc[d["has_comfort_ingredient"], "avg_rating"], ACCENT),
    ]
    fig = go.Figure()
    lows, highs = [], []
    for name, s, color in groups:
        r = mean_with_ci(s)
        if not r["n"]:
            continue
        lows.append(r["ci_low"] if not np.isnan(r["half"]) else r["mean"])
        highs.append(r["ci_high"] if not np.isnan(r["half"]) else r["mean"])
        fig.add_trace(go.Scatter(
            x=[r["mean"]], y=[name], mode="markers+text",
            marker=dict(color=color, size=14, line=dict(color="white", width=2)),
            error_x=dict(type="constant", value=0 if np.isnan(r["half"]) else r["half"],
                         color=INK_MUTED, thickness=1.5, width=6),
            text=[f"{fmt_num(r['mean'], 2)} / 5 (n = {fmt_int(r['n'])})"],
            textposition="top center", textfont=dict(color=INK_MUTED, size=13),
            hovertemplate=(f"<b>{name}</b><br>Note moyenne : %{{x:.3f}}<br>"
                           f"{fmt_int(r['n'])} recettes<extra></extra>"),
            showlegend=False,
        ))
    if lows:
        span = max(highs) - min(lows)
        pad = max(span * 0.6, 0.05)
        lo, hi = min(lows) - pad, max(highs) + pad
        fig.update_xaxes(range=[lo, hi],
                         title_text=f"{label('avg_rating')} — axe zoomé de {fmt_num(lo, 2)} à {fmt_num(hi, 2)}")
    apply_theme(fig, height=260)
    fig.update_yaxes(title_text=None, range=[-0.6, 1.8])
    hide_grid(fig, "y")
    return fig


col1, col2 = st.columns(2)
for col, x, title in [
    (col1, "calories", "Les recettes plus caloriques sont-elles mieux notées ?"),
    (col2, "carbs", "Les recettes plus riches en glucides sont-elles mieux notées ?"),
]:
    with col:
        chart_title(
            title,
            "Un point = une recette (bleu, semi-transparent : les zones foncées "
            "concentrent beaucoup de recettes). Ligne orange = tendance linéaire. "
            "Même axe vertical zoomé pour les deux graphiques.",
        )
        fig, info = build_scatter(df, x)
        st.plotly_chart(fig, width="stretch")
        st.caption(scatter_caption(info))
        x_name = "la teneur en calories" if x == "calories" else "la teneur en glucides (proxy du sucre)"
        st.markdown(describe_spearman(spearman(df, x, "avg_rating"), x_name))

st.divider()
chart_title(
    "Les recettes avec un ingrédient « réconfort » sont-elles mieux notées ?",
    "Ingrédients réconfort : beurre, crème, fromage, bacon, mayonnaise (détection "
    "par mot-clé). Point = note moyenne du groupe ; trait horizontal = intervalle "
    "de confiance à 95 % (si les traits se chevauchent, l'écart peut relever du "
    "hasard). Axe zoomé : l'écart réel se lit en dixièmes ou centièmes d'étoile.",
)
st.plotly_chart(build_comfort_points(rated), width="stretch")

st.info(
    "Une relation entre note et richesse ne prouve pas une « prime à la "
    "malbouffe » : sans catégorie de plat dans les données, une partie du "
    "signal peut venir de la sur-représentation des desserts parmi les "
    "recettes riches. À croiser avec une lecture d'un échantillon de recettes "
    "avant de conclure.",
    icon=":material/warning:",
)
