"""
Socle visuel commun à toutes les pages (Séances 2 et 3 du cours).

Tout ce qui touche à l'apparence passe par ce module, pour garantir la
cohérence entre pages (« standardiser les codes visuels ») :
- un gabarit Plotly épuré (data-ink ratio) appliqué à CHAQUE figure via
  `apply_theme` ;
- des palettes adaptées au daltonisme (Okabe-Ito), sans jamais opposer
  rouge et vert ;
- une couleur fixe par pays, identique sur toutes les pages ;
- un format unique pour les KPI (`kpi`) et pour les titres de graphique
  (`chart_title`) ;
- des formats de nombres à la française (espace des milliers, virgule
  décimale), pour qu'aucune page ne formate « à sa façon ».
"""

import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Palettes
# ---------------------------------------------------------------------------

# Okabe-Ito : palette catégorielle conçue pour rester distinguable par les
# personnes daltoniennes.
OKABE_ITO = {
    "bleu": "#0072B2",
    "orange": "#E69F00",
    "bleu_ciel": "#56B4E9",
    "jaune": "#F0E442",
    "rose": "#CC79A7",
    "vert_bleute": "#009E73",
    "vermillon": "#D55E00",
    "gris": "#999999",
}
CATEGORICAL = [
    OKABE_ITO["bleu"], OKABE_ITO["orange"], OKABE_ITO["bleu_ciel"],
    OKABE_ITO["rose"], OKABE_ITO["jaune"], OKABE_ITO["gris"],
]

# Séquentielle : une seule teinte (ordre de grandeur uniquement).
SEQUENTIAL = "Blues"
# Variante éclaircie pour les heatmaps annotées : le texte sombre reste
# lisible même sur les cases les plus foncées (contraste).
SEQUENTIAL_LIGHT = [[0.0, "#F7FBFF"], [0.5, "#9ECAE1"], [1.0, "#4292C6"]]

# Mise en évidence : gris neutre pour le fond, orange pour ce qui compte.
NEUTRAL = "#BDBDBD"
ACCENT = OKABE_ITO["orange"]

# Alerte : réservée aux dépassements de seuil, avec parcimonie.
ALERT = OKABE_ITO["vermillon"]

# Couleur de texte secondaire (annotations, axes).
TEXT_MUTED = "#555555"
GRID = "#EEEEEE"

# Couleur fixe par pays. L'orange n'est attribué à aucun pays : il reste
# réservé à la mise en évidence (accent), pour ne pas créer d'ambiguïté.
COUNTRY_COLORS = {
    "Italian": OKABE_ITO["bleu"],
    "Chinese": OKABE_ITO["rose"],
    "Indian": OKABE_ITO["vert_bleute"],
    "French": OKABE_ITO["bleu_ciel"],
    "Japanese": OKABE_ITO["jaune"],
}
OTHER_COUNTRY_COLOR = OKABE_ITO["gris"]


def country_color(country: str) -> str:
    """Couleur fixe d'un pays (gris pour les pays sans couleur dédiée)."""
    return COUNTRY_COLORS.get(country, OTHER_COUNTRY_COLOR)


def country_color_map(countries) -> dict:
    """Dictionnaire pays -> couleur, à passer en `color_discrete_map`."""
    return {c: country_color(c) for c in countries}


# Libellés français des étiquettes `country` (affichage uniquement).
COUNTRY_LABELS_FR = {
    "Canadian": "Canada", "Brazilian": "Brésil", "Filipino": "Philippines",
    "Cuban": "Cuba", "Chinese": "Chine", "Russian": "Russie", "Indian": "Inde",
    "French": "France", "Italian": "Italie", "Japanese": "Japon",
    "Greek": "Grèce", "German": "Allemagne", "Vietnamese": "Vietnam",
    "Thai": "Thaïlande", "Spanish": "Espagne", "Polish": "Pologne",
    "Korean": "Corée", "Portuguese": "Portugal", "Lebanese": "Liban",
    "Persian": "Iran (cuisine persane)", "Jamaican": "Jamaïque",
    "Peruvian": "Pérou", "Turkish": "Turquie", "Danish": "Danemark",
    "Swedish": "Suède", "Argentinian": "Argentine", "Norwegian": "Norvège",
    "Pakistani": "Pakistan", "Malaysian": "Malaisie", "Indonesian": "Indonésie",
    "Israeli": "Israël", "Chilean": "Chili", "Dutch": "Pays-Bas",
    "Austrian": "Autriche", "South African": "Afrique du Sud",
    "Finnish": "Finlande", "Bangladeshi": "Bangladesh", "Colombian": "Colombie",
    "Swiss": "Suisse", "Belgian": "Belgique", "Puerto Rican": "Porto Rico",
    "Australian and New Zealander": "Australie et Nouvelle-Zélande",
    "Scandinavian": "Scandinavie", "Soul Food": "Soul food (États-Unis)",
    "Cajun and Creole": "Cajun et créole (États-Unis)",
    "Tex-Mex": "Tex-Mex (États-Unis)",
    "Southern Recipes": "Sud des États-Unis", "Jewish": "Cuisine juive",
    "Amish and Mennonite": "Amish et mennonite",
}


def country_label(country: str) -> str:
    return COUNTRY_LABELS_FR.get(country, country)


# Libellés lisibles (avec unités) des colonnes : plus aucun nom brut à l'écran.
COLUMN_LABELS = {
    "calories": "Calories (kcal / portion)",
    "fat": "Lipides (g / portion)",
    "carbs": "Glucides (g / portion)",
    "protein": "Protéines (g / portion)",
    "avg_rating": "Note moyenne (sur 5)",
    "total_ratings": "Nombre d'avis",
    "n_recipes": "Nombre de recettes",
    "pct_exceeds_calories": "Part des recettes au-dessus du seuil calorique",
    "pct_exceeds_fat": "Part des recettes au-dessus du seuil de lipides",
    "pct_healthy_well_rated": "Part des recettes saines et bien notées",
    "country": "Pays",
    "name": "Recette",
    "url": "Lien",
    "map_type": "Type d'étiquette",
}

# Libellés courts (dans une phrase) des variables nutritionnelles.
NUTRIENT_SHORT = {
    "calories": "calories",
    "fat": "lipides",
    "carbs": "glucides",
    "protein": "protéines",
}
NUTRIENT_UNIT = {"calories": "kcal", "fat": "g", "carbs": "g", "protein": "g"}

MAP_TYPE_LABELS = {
    "multi_country": "Plusieurs pays",
    "us_regional": "Tradition régionale des États-Unis",
    "non_national": "Communauté sans territoire national",
    "single_country": "Un seul pays",
}

INGREDIENT_LABELS_FR = {
    "sugar": "sucre",
    "all-purpose flour": "farine",
    "butter": "beurre",
    "salt": "sel",
    "egg": "œuf",
    "vegetable oil": "huile végétale",
    "olive oil": "huile d'olive",
    "milk": "lait",
    "onion": "oignon",
    "garlic": "ail",
    "black pepper": "poivre noir",
}


def ingredient_label(ingredient: str) -> str:
    return INGREDIENT_LABELS_FR.get(ingredient, ingredient)


# ---------------------------------------------------------------------------
# Formats de nombres (à la française)
# ---------------------------------------------------------------------------

def fmt_int(x) -> str:
    """12345 -> '12 345' (espace insécable fine pour les milliers)."""
    return f"{x:,.0f}".replace(",", " ")


def fmt_pct(x, decimals: int = 0) -> str:
    """0.1234 -> '12 %' (virgule décimale, espace insécable)."""
    return f"{x * 100:.{decimals}f}".replace(".", ",") + " %"


def fmt_num(x, decimals: int = 1) -> str:
    """3.14159 -> '3,1'."""
    return f"{x:,.{decimals}f}".replace(",", " ").replace(".", ",")


def fmt_signed(x, decimals: int = 2) -> str:
    """0.0151 -> '+0,02'."""
    return ("+" if x >= 0 else "−") + fmt_num(abs(x), decimals)


# ---------------------------------------------------------------------------
# Gabarit Plotly
# ---------------------------------------------------------------------------

FONT_FAMILY = "Source Sans Pro, Helvetica, Arial, sans-serif"


def apply_theme(fig: go.Figure, title: str | None = None,
                subtitle: str | None = None, height: int = 420,
                grid: bool = False) -> go.Figure:
    """Applique le gabarit épuré à une figure Plotly (à appeler sur CHAQUE figure).

    - fond blanc, pas de cadre, pas d'ombre ni d'effet 3D ;
    - grille absente ou très légère (`grid=True` : lignes horizontales gris
      très clair, utile seulement pour lire des valeurs précises) ;
    - marges réduites, police lisible.

    Le titre est en général affiché hors figure avec `chart_title` ; `title`
    et `subtitle` ne servent que si la figure doit être autonome.
    """
    full_title = None
    if title:
        full_title = f"<b>{title}</b>"
        if subtitle:
            full_title += f"<br><span style='font-size:13px;color:{TEXT_MUTED}'>{subtitle}</span>"
    fig.update_layout(
        template="none",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family=FONT_FAMILY, size=14, color="#222222"),
        title=dict(text=full_title, x=0, xanchor="left") if full_title else None,
        height=height,
        margin=dict(l=10, r=20, t=60 if full_title else 20, b=10),
        hoverlabel=dict(bgcolor="white", font_size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    title_text=""),
    )
    axis_common = dict(showline=False, zeroline=False, ticks="",
                       title_font=dict(size=13, color=TEXT_MUTED),
                       tickfont=dict(size=12, color=TEXT_MUTED),
                       automargin=True)
    fig.update_xaxes(showgrid=False, **axis_common)
    fig.update_yaxes(showgrid=grid, gridcolor=GRID, gridwidth=1, **axis_common)
    return fig


def plotly_config() -> dict:
    """Configuration commune : barre d'outils discrète."""
    return {"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}


def show(fig: go.Figure) -> None:
    """Affiche une figure avec la configuration commune."""
    st.plotly_chart(fig, width="stretch", config=plotly_config())


# ---------------------------------------------------------------------------
# Composants Streamlit communs
# ---------------------------------------------------------------------------

def kpi(label: str, value: str, help: str | None = None,
        subtitle: str | None = None) -> None:
    """Format UNIQUE de KPI pour toute l'application : titre, valeur, sous-titre."""
    with st.container(border=True):
        st.metric(label, value, help=help)
        if subtitle:
            st.caption(subtitle)


def chart_title(headline: str, subtitle: str | None = None) -> None:
    """Titre de graphique (question ou insight) + sous-titre (encodage, limite)."""
    st.markdown(f"#### {headline}")
    if subtitle:
        st.caption(subtitle)
