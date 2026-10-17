"""
Socle visuel commun à toutes les pages (Séances 2 et 3).

- Gabarit Plotly épuré (data-ink ratio) : fond blanc, grille très légère,
  pas de cadre, pas d'effet, marges réduites.
- Palettes adaptées au daltonisme : Okabe-Ito, jamais d'opposition
  rouge / vert.
- Une couleur FIXE par pays, identique sur toutes les pages.
- Un format unique de KPI et de titre de graphique (titre = question).

Toute figure affichée doit passer par `apply_theme`.
"""

import html

import plotly.graph_objects as go
import streamlit as st

# --- Palettes --------------------------------------------------------------

# Okabe-Ito (Séance 2). Le jaune est gardé dans la palette de référence mais
# n'est PAS utilisé comme couleur de pays : son contraste sur fond blanc est
# trop faible (1,3:1, validé par script, voir JOURNAL_IA.md). Il est remplacé
# par le vermillon Okabe-Ito, sans risque d'opposition rouge / vert puisque
# la palette ne contient aucun vert.
OKABE_ITO = {
    "bleu": "#0072B2",
    "orange": "#E69F00",
    "bleu_ciel": "#56B4E9",
    "jaune": "#F0E442",
    "rose": "#CC79A7",
    "vermillon": "#D55E00",
    "gris": "#999999",
}

CATEGORICAL = [
    OKABE_ITO["bleu"],
    OKABE_ITO["orange"],
    OKABE_ITO["bleu_ciel"],
    OKABE_ITO["rose"],
    OKABE_ITO["vermillon"],
]

# Séquentielle : une seule teinte, du clair au foncé.
SEQUENTIAL = "Blues"
SEQUENTIAL_MAIN = OKABE_ITO["bleu"]

# Mise en évidence : fond neutre + une couleur d'accent pour ce qui compte.
NEUTRAL = "#BDBDBD"
ACCENT = OKABE_ITO["orange"]

# Alerte : réservée aux dépassements de seuil, avec parcimonie.
ALERT = OKABE_ITO["vermillon"]

# Encre (texte, axes, lignes de référence)
INK = "#262626"
INK_MUTED = "#595959"
GRID = "#EEEEEE"
REFERENCE_LINE = "#595959"

FONT_FAMILY = "Source Sans Pro, Helvetica, Arial, sans-serif"

# --- Couleur fixe par pays --------------------------------------------------

# Les 5 pays les plus représentés dans cuisines.csv (single_country), triés
# par nombre de recettes décroissant puis par ordre alphabétique pour les
# ex-aequo. Ce dictionnaire est volontairement figé : un pays garde la même
# couleur sur toutes les pages, quel que soit le filtre.
COUNTRY_COLORS = {
    "Brésil": CATEGORICAL[0],
    "Canada": CATEGORICAL[1],
    "Philippines": CATEGORICAL[2],
    "Chine": CATEGORICAL[3],
    "Cuba": CATEGORICAL[4],
}
OTHER_COUNTRY = OKABE_ITO["gris"]
MAX_COLOR_CATEGORIES = len(CATEGORICAL)


def country_color_map(countries: list[str]) -> dict[str, str]:
    """Couleur de chaque pays d'une sélection.

    Les pays du dictionnaire fixe gardent toujours leur couleur. Les autres
    reçoivent, dans l'ordre alphabétique, les couleurs de la palette encore
    libres dans la sélection, puis le gris si la sélection dépasse la
    palette (ce que les pages évitent en limitant la sélection à
    MAX_COLOR_CATEGORIES pays).
    """
    mapping = {c: COUNTRY_COLORS[c] for c in countries if c in COUNTRY_COLORS}
    free = [col for col in CATEGORICAL if col not in mapping.values()]
    for c in sorted(set(countries) - set(mapping)):
        mapping[c] = free.pop(0) if free else OTHER_COUNTRY
    return mapping


# --- Gabarit Plotly ----------------------------------------------------------

def apply_theme(fig: go.Figure, title: str | None = None, subtitle: str | None = None,
                height: int = 450) -> go.Figure:
    """Applique le gabarit épuré commun à une figure Plotly."""
    fig.update_layout(
        template="none",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family=FONT_FAMILY, size=14, color=INK),
        height=height,
        margin=dict(l=10, r=20, t=60 if title else 20, b=10),
        hoverlabel=dict(bgcolor="white", font_size=13, font_family=FONT_FAMILY),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            title_text="", bgcolor="rgba(0,0,0,0)",
        ),
        coloraxis_colorbar=dict(outlinewidth=0, thickness=12, len=0.7),
    )
    axis_style = dict(
        showline=False, zeroline=False, ticks="", gridcolor=GRID, gridwidth=1,
        title_font=dict(size=13, color=INK_MUTED), tickfont=dict(color=INK_MUTED),
        automargin=True,
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)
    if title:
        text = f"<b>{html.escape(title)}</b>"
        if subtitle:
            text += f"<br><span style='font-size:13px;color:{INK_MUTED}'>{html.escape(subtitle)}</span>"
        fig.update_layout(title=dict(text=text, x=0, xanchor="left", font=dict(size=16)))
    return fig


def hide_grid(fig: go.Figure, axis: str = "both") -> go.Figure:
    """Retire la grille d'un axe (ex : axe des catégories d'un graphique en barres)."""
    if axis in ("x", "both"):
        fig.update_xaxes(showgrid=False)
    if axis in ("y", "both"):
        fig.update_yaxes(showgrid=False)
    return fig


# --- Composants Streamlit -----------------------------------------------------

def chart_title(question: str, subtitle: str | None = None) -> None:
    """Titre de graphique sous forme de question + sous-titre d'encodage."""
    st.markdown(f"#### {question}")
    if subtitle:
        st.caption(subtitle)


def kpi(label: str, value: str, help: str | None = None, subtitle: str | None = None,
        container=None) -> None:
    """Format unique de KPI : titre, valeur, sous-titre.

    N'utilise pas `st.metric(delta=...)` : sa flèche verte / rouge opposerait
    rouge et vert et suggérerait un jugement (hausse = bien) hors de propos.
    """
    target = container if container is not None else st
    box = target.container(border=True)
    box.markdown(
        f"<div style='font-size:0.9rem;color:{INK_MUTED}'>{html.escape(label)}</div>"
        f"<div style='font-size:2rem;font-weight:600;color:{INK};line-height:1.2'>"
        f"{html.escape(value)}</div>",
        unsafe_allow_html=True,
        help=help,
    )
    if subtitle:
        box.caption(subtitle)


# --- Formats numériques (français) --------------------------------------------

def fmt_int(x) -> str:
    return f"{x:,.0f}".replace(",", " ")


def fmt_pct(x, decimals: int = 0) -> str:
    return f"{x * 100:.{decimals}f}".replace(".", ",") + " %"


def fmt_num(x, decimals: int = 1) -> str:
    return f"{x:,.{decimals}f}".replace(",", " ").replace(".", ",")
