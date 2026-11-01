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

# Catégorielle (4 groupes, page 4) : la couche de base, sujet de la page,
# prend l'accent orange (« ce qui compte » partout dans l'appli) ; les autres
# couches sont des teintes distinctes Okabe-Ito (bleu, bleu ciel) et le gris
# de fond. Écarts ΔE ≥ 24 entre couches voisines, y compris en simulation de
# deutéranopie, protanopie et tritanopie. Pas de rouge/vert.
CATEGORICAL = [ACCENT, "#0072B2", "#56B4E9", GREY]

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


# --- Textes & En-têtes pastels ----------------------------------------------
PAGE_THEMES = {
    "accueil": {
        "name": "Accueil",
        "tag": "VUE D'ENSEMBLE",
        "bg_card": "#FFF7F2",
        "border": "#FFD8C2",
        "accent": "#E06D53",
        "badge_bg": "#FFE8DC",
        "badge_text": "#8A3B14",
        "url": "accueil",
    },
    "couverture": {
        "name": "1. Couverture",
        "tag": "QUESTION 1 · OFFRE DU CATALOGUE",
        "bg_card": "#F2F8FE",
        "border": "#CBE4FD",
        "accent": "#2B78C5",
        "badge_bg": "#E3F2FD",
        "badge_text": "#154A78",
        "url": "couverture",
    },
    "ingredients": {
        "name": "2. Ingrédients",
        "tag": "QUESTION 2 · PROFILS D'INGRÉDIENTS",
        "bg_card": "#F1F9F2",
        "border": "#C8E6C9",
        "accent": "#388E3C",
        "badge_bg": "#E8F5E9",
        "badge_text": "#1E5E26",
        "url": "ingredients",
    },
    "attention": {
        "name": "3. Attention",
        "tag": "QUESTION 3 · INTÉRÊT DU PUBLIC",
        "bg_card": "#FFFDF2",
        "border": "#FFE082",
        "accent": "#D97706",
        "badge_bg": "#FFF8E1",
        "badge_text": "#7A5200",
        "url": "attention",
    },
    "facettes": {
        "name": "4. Facettes",
        "tag": "QUESTION 4 · TYPES DE PLATS",
        "bg_card": "#FAF5FC",
        "border": "#E1BEE7",
        "accent": "#8E24AA",
        "badge_bg": "#F3E5F5",
        "badge_text": "#5C1D6E",
        "url": "facettes",
    },
    "methodologie": {
        "name": "Méthodologie",
        "tag": "RIGUEUR & LIMITES",
        "bg_card": "#F0FAF9",
        "border": "#B2DFDB",
        "accent": "#00897B",
        "badge_bg": "#E0F2F1",
        "badge_text": "#004D40",
        "url": "methodologie",
    },
}


def page_header(key: str, title: str, subtitle: str | None = None) -> None:
    """En-tête de page avec badge pastel thématique sobre, sans émojis."""
    t = PAGE_THEMES.get(key, PAGE_THEMES["accueil"])
    badge_bg = t.get("badge_bg", "#FFE8DC")
    border = t.get("border", "#FFD8C2")
    badge_text = t.get("badge_text", "#8A3B14")
    tag = t.get("tag", "")
    accent = t.get("accent", "#E06D53")

    st.markdown(
        f"""
        <div style="margin-bottom: 8px;">
            <span style="
                display: inline-block;
                padding: 4px 12px;
                border-radius: 999px;
                background-color: {badge_bg};
                border: 1px solid {border};
                color: {badge_text};
                font-size: 0.75rem;
                font-weight: 700;
                letter-spacing: 0.06em;
            ">
                {tag}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.markdown(
        f'<div style="height: 3px; width: 56px; background-color: {accent}; '
        f'border-radius: 2px; margin: 10px 0 20px 0;"></div>',
        unsafe_allow_html=True,
    )


def chart_title(question: str, subtitle: str | None = None) -> None:
    """Titre de graphique = une question ; sous-titre = mode de lecture."""
    st.markdown(f"#### {question}")
    if subtitle:
        st.caption(subtitle)


def kpi(label: str, value: str, help: str | None = None,
        sub: str | None = None, theme_key: str | None = None) -> None:
    """Format unique de KPI avec bordure et fond subtil pastel optionnel."""
    if theme_key and theme_key in PAGE_THEMES:
        t = PAGE_THEMES[theme_key]
        st.markdown(
            f"""
            <div style="
                background-color: {t['bg_card']};
                border: 1px solid {t['border']};
                border-left: 4px solid {t['accent']};
                border-radius: 10px;
                padding: 14px 16px;
                margin-bottom: 12px;
                min-height: 110px;
            ">
                <div style="font-size: 0.85rem; color: {MUTED}; font-weight: 500;">{label}</div>
                <div style="font-size: 2rem; font-weight: 700; color: {TEXT}; line-height: 1.25; margin: 4px 0;">{value}</div>
                {f'<div style="font-size: 0.78rem; color: {t["badge_text"]};">{sub}</div>' if sub else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        with st.container(border=True):
            st.metric(label, value, help=help)
            if sub:
                st.caption(sub)


def get_global_css() -> str:
    """CSS global pour styliser la barre latérale et l'interface avec des tons pastels."""
    return """
    <style>
    /* Barre latérale générale */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FAF8F5 0%, #F4F1EA 100%) !important;
        border-right: 1px solid #EAE5DC !important;
    }

    /* En-tête de la barre latérale */
    .sidebar-header-brand {
        padding: 12px 14px;
        background: #FFFFFF;
        border: 1px solid #ECE7DE;
        border-radius: 12px;
        margin-bottom: 14px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    }
    .sidebar-brand-pill {
        display: inline-block;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #8C8276;
        background: #F3EFE9;
        padding: 2px 8px;
        border-radius: 999px;
        margin-bottom: 4px;
    }
    .sidebar-brand-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #2D251E;
        line-height: 1.25;
    }

    /* Titres de sections dans la barre latérale */
    [data-testid="stSidebarNav"] span[data-testid="stSidebarNavSectionHeader"],
    [data-testid="stSidebarNav"] li div span:first-child {
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: #8D8175 !important;
    }

    /* Liens de navigation dans la barre latérale */
    [data-testid="stSidebarNav"] a,
    [data-testid="stSidebarNavItems"] a {
        border-radius: 9px !important;
        margin: 3px 6px !important;
        padding: 7px 12px !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        transition: all 0.15s ease-in-out !important;
        border-left: 4px solid transparent !important;
    }

    /* Onglet Accueil : Pêche / Terracotta */
    [data-testid="stSidebarNav"] a[href*="accueil" i] {
        color: #4A3528 !important;
    }
    [data-testid="stSidebarNav"] a[href*="accueil" i]:hover {
        background: #FFF3EB !important;
        border-left: 4px solid #FFA07A !important;
        transform: translateX(2px);
    }
    [data-testid="stSidebarNav"] a[href*="accueil" i][aria-current="page"],
    [data-testid="stSidebarNav"] a[href*="accueil" i].active {
        background: linear-gradient(90deg, #FFE8DC 0%, #FFF5ED 100%) !important;
        border-left: 4px solid #E06D53 !important;
        font-weight: 700 !important;
        color: #7A2E19 !important;
    }

    /* Onglet 1. Couverture : Bleu Ciel */
    [data-testid="stSidebarNav"] a[href*="couverture" i] {
        color: #1A365D !important;
    }
    [data-testid="stSidebarNav"] a[href*="couverture" i]:hover {
        background: #EEF6FC !important;
        border-left: 4px solid #64B5F6 !important;
        transform: translateX(2px);
    }
    [data-testid="stSidebarNav"] a[href*="couverture" i][aria-current="page"],
    [data-testid="stSidebarNav"] a[href*="couverture" i].active {
        background: linear-gradient(90deg, #E1F0FA 0%, #F0F7FD 100%) !important;
        border-left: 4px solid #2B78C5 !important;
        font-weight: 700 !important;
        color: #154A78 !important;
    }

    /* Onglet 2. Ingrédients : Vert Sauge / Menthe */
    [data-testid="stSidebarNav"] a[href*="ingredients" i] {
        color: #1A4222 !important;
    }
    [data-testid="stSidebarNav"] a[href*="ingredients" i]:hover {
        background: #EFF8F1 !important;
        border-left: 4px solid #81C784 !important;
        transform: translateX(2px);
    }
    [data-testid="stSidebarNav"] a[href*="ingredients" i][aria-current="page"],
    [data-testid="stSidebarNav"] a[href*="ingredients" i].active {
        background: linear-gradient(90deg, #E2F4E5 0%, #F1F9F2 100%) !important;
        border-left: 4px solid #388E3C !important;
        font-weight: 700 !important;
        color: #1E5E26 !important;
    }

    /* Onglet 3. Attention : Ambre / Miel Doux */
    [data-testid="stSidebarNav"] a[href*="attention" i] {
        color: #4E3800 !important;
    }
    [data-testid="stSidebarNav"] a[href*="attention" i]:hover {
        background: #FFFBEB !important;
        border-left: 4px solid #FFD54F !important;
        transform: translateX(2px);
    }
    [data-testid="stSidebarNav"] a[href*="attention" i][aria-current="page"],
    [data-testid="stSidebarNav"] a[href*="attention" i].active {
        background: linear-gradient(90deg, #FFF3CD 0%, #FFFDF5 100%) !important;
        border-left: 4px solid #E69F00 !important;
        font-weight: 700 !important;
        color: #7A5200 !important;
    }

    /* Onglet 4. Facettes : Lilas / Lavande */
    [data-testid="stSidebarNav"] a[href*="facettes" i] {
        color: #4A1B57 !important;
    }
    [data-testid="stSidebarNav"] a[href*="facettes" i]:hover {
        background: #FAF2FC !important;
        border-left: 4px solid #BA68C8 !important;
        transform: translateX(2px);
    }
    [data-testid="stSidebarNav"] a[href*="facettes" i][aria-current="page"],
    [data-testid="stSidebarNav"] a[href*="facettes" i].active {
        background: linear-gradient(90deg, #F3DEFA 0%, #FAF5FC 100%) !important;
        border-left: 4px solid #8E24AA !important;
        font-weight: 700 !important;
        color: #5C1D6E !important;
    }

    /* Onglet Méthodologie : Sarcelle / Cyan Doux */
    [data-testid="stSidebarNav"] a[href*="methodologie" i] {
        color: #0E443F !important;
    }
    [data-testid="stSidebarNav"] a[href*="methodologie" i]:hover {
        background: #EDFAF8 !important;
        border-left: 4px solid #4DB6AC !important;
        transform: translateX(2px);
    }
    [data-testid="stSidebarNav"] a[href*="methodologie" i][aria-current="page"],
    [data-testid="stSidebarNav"] a[href*="methodologie" i].active {
        background: linear-gradient(90deg, #D4F4F0 0%, #EDFAF8 100%) !important;
        border-left: 4px solid #00897B !important;
        font-weight: 700 !important;
        color: #004D40 !important;
    }

    /* Conteneurs et cartes bordered */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border-radius: 10px !important;
        border-color: #EBE5DC !important;
        background-color: #FFFFFF;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    }
    </style>
    """
