"""
Socle visuel commun à toutes les pages.

Principes appliqués (cours de visualisation, M2 MIAGE) :
- Séance 3 (data-ink ratio, charge cognitive) : fond blanc, pas de cadre,
  grille absente ou très légère, pas d'ombre ni de 3D, marges réduites.
- Séance 2 (couleur, daltonisme) : aucune opposition rouge/vert ; une
  couleur d'accent unique réservée à ce qui compte, le reste en gris.
- Séance 3 (cohérence) : un seul format de KPI et un seul format de titre
  de graphique (une question + un sous-titre qui explique la lecture).

Pas de palette par continent : les continents sont nommés par leurs
libellés, une couleur en plus serait un double encodage inutile.
"""

import plotly.graph_objects as go
import streamlit as st

# --- Palettes ---------------------------------------------------------------
# Mise en évidence : gris neutre pour le fond + un accent unique.
GREY = "#BDBDBD"
GREY_LIGHT = "#E6E6E6"
ACCENT = "#E69F00"  # orange Okabe-Ito
# Version claire de l'accent, pour un état « intermédiaire » (présence
# indirecte sur la carte). Écart de couleur ΔE ≥ 25 avec l'accent et avec le
# gris clair, y compris en simulation de deutéranopie, protanopie et tritanopie.
ACCENT_LIGHT = "#F6CD86"

# Divergente (sens d'un écart) : deux teintes distinctes, lisibles par les
# daltoniens, autour d'un point neutre.
DIV_POS = "#E69F00"  # au-dessus de la référence
DIV_NEG = "#0072B2"  # en dessous de la référence
DIV_NEUTRAL = GREY

# Séquentielle (heatmap) : une seule teinte.
SEQUENTIAL = "Blues"

# Catégorielle (4 groupes au maximum dans l'application) : Okabe-Ito. Le
# gris est éclairci (#999999 -> #CCCCCC) : en simulation de deutéranopie et
# de protanopie, le rose #CC79A7 devenait presque le même gris moyen.
CATEGORICAL = ["#0072B2", "#56B4E9", "#CC79A7", "#CCCCCC"]

TEXT = "#262626"
MUTED = "#6B6B6B"
FONT = "Source Sans Pro, Arial, sans-serif"


# --- Formats de nombres (français) -----------------------------------------
def fmt_int(x) -> str:
    """15589 -> '15 589' (espace insécable fine comme séparateur)."""
    return f"{int(round(x)):,}".replace(",", " ")


def fmt_num(x, decimals: int = 1) -> str:
    """4.25 -> '4,3' ; virgule décimale."""
    return f"{x:,.{decimals}f}".replace(",", " ").replace(".", ",")


def fmt_pct(x, decimals: int = 0) -> str:
    """0.593 -> '59 %' ; x est une proportion entre 0 et 1."""
    return f"{fmt_num(100 * x, decimals)} %"


# --- Figures ----------------------------------------------------------------
def apply_theme(fig: go.Figure, title: str | None = None,
                subtitle: str | None = None, height: int = 450) -> go.Figure:
    """Applique le style commun à une figure Plotly.

    Le titre est d'ordinaire porté par `chart_title` (au-dessus du
    graphique, dans Streamlit). `title`/`subtitle` ne servent que si la
    figure doit être lisible seule (export).
    """
    layout = dict(
        template="simple_white",
        height=height,
        font=dict(family=FONT, size=13, color=TEXT),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=10, r=10, t=30, b=10),
        hoverlabel=dict(bgcolor="white", font_size=13, font_family=FONT),
        legend=dict(title_text=""),
    )
    if title:
        text = f"<b>{title}</b>"
        if subtitle:
            text += f"<br><span style='font-size:13px;color:{MUTED}'>{subtitle}</span>"
        layout["title"] = dict(text=text, x=0, xanchor="left", font=dict(size=17))
        layout["margin"]["t"] = 80 if subtitle else 50
    fig.update_layout(**layout)
    # Axes sobres : pas de cadre ni de grille, lignes d'axe gris clair.
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=GREY_LIGHT,
                     ticks="", tickfont=dict(color=MUTED))
    fig.update_yaxes(showgrid=False, zeroline=False, linecolor=GREY_LIGHT,
                     ticks="", tickfont=dict(color=MUTED))
    return fig


PLOTLY_CONFIG = {"displaylogo": False, "modeBarButtonsToRemove": [
    "lasso2d", "select2d", "autoScale2d", "toggleSpikelines"]}


def show(fig: go.Figure) -> None:
    """Affiche une figure avec la configuration commune."""
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)


# --- Textes -----------------------------------------------------------------
def chart_title(question: str, subtitle: str | None = None) -> None:
    """Titre de graphique = une question ; sous-titre = mode de lecture."""
    st.markdown(f"#### {question}")
    if subtitle:
        st.caption(subtitle)


def kpi(label: str, value: str, help: str | None = None,
        sub: str | None = None) -> None:
    """Format unique de KPI : titre, valeur, sous-titre facultatif."""
    with st.container(border=True):
        st.metric(label, value, help=help)
        if sub:
            st.caption(sub)
