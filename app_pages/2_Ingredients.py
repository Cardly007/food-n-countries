import plotly.graph_objects as go
from plotly.colors import sample_colorscale, unlabel_rgb
import streamlit as st

from src.ingredients import INGREDIENT_LABELS
from src.load_data import load_processed, load_stats
from src.theme import SEQUENTIAL, TEXT, apply_theme, chart_title, fmt_int, fmt_num, show

# Vue par défaut (Séance 2 : mémoire de travail ; Séance 3 : découper la
# complexité) : quelques cuisines par continent et les ingrédients qui
# distinguent le plus les cuisines. Les bascules rendent la vue complète.
PER_CONTINENT = 3       # cuisines par continent dans la vue par défaut
N_INGREDIENTS = 11      # ingrédients les plus discriminants par défaut
NO_ZONE = "Sans territoire"
CONTINENT_ORDER = ["Europe", "Asie", "Amérique du Nord", "Amérique du Sud",
                   "Afrique", "Océanie", NO_ZONE]



def _luminance(rgb: tuple) -> float:
    lin = [c / 255 / 12.92 if c / 255 <= 0.04045 else ((c / 255 + 0.055) / 1.055) ** 2.4
           for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def _contrast(a: float, b: float) -> float:
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def text_color(value: float) -> str:
    """Blanc ou noir selon ce qui contraste le plus avec la case. Avec le noir
    (et non le gris foncé du thème), le pire cas reste au-dessus de 4,5:1
    (WCAG AA) sur toute l'échelle Blues."""
    bg = _luminance(unlabel_rgb(sample_colorscale(SEQUENTIAL, value / 100)[0]))
    return "white" if _contrast(1.0, bg) > _contrast(0.0, bg) else "black"


stats = load_stats()
freq = load_processed("ingredient_freq")
families = load_processed("cuisine_families")
catalog = load_processed("cuisine_catalog")
attention = load_processed("attention")

st.title("2. Les cuisines sont-elles vraiment différentes dans l'assiette ?")
st.caption(
    "Deuxième question : le contenu. Au-delà de l'étiquette « grecque » ou "
    "« thaïlandaise », les recettes de chaque cuisine utilisent-elles des "
    "ingrédients différents ?"
)

# --- Cuisines et continents ----------------------------------------------------------
# Même rattachement que la page 1 (traditions régionales comprises) ; ordre dans
# un bloc = ordre de la classification hiérarchique (profils voisins côte à côte).
min_n, small = stats["seuil_recettes"], stats["seuil_petit_effectif"]
cuisines = (
    families[["country", "cuisine", "family_label", "ordre"]]
    .merge(catalog[["country", "n_recettes", "continent_zone"]], on="country")
    .merge(attention[["country", "avis_total"]], on="country")
)
cuisines["bloc"] = cuisines["continent_zone"].fillna(NO_ZONE)

# Vue par défaut : cuisines d'au moins `small` recettes, les mieux représentées
# de chaque continent (plus de recettes ; à égalité, plus d'avis).
default_set = (
    cuisines[(cuisines["n_recettes"] >= small) & (cuisines["bloc"] != NO_ZONE)]
    .sort_values(["n_recettes", "avis_total"], ascending=False)
    .groupby("bloc").head(PER_CONTINENT)["country"]
)

# Ingrédients les plus discriminants : plus forte dispersion (écart-type) de la
# fréquence entre les cuisines, toutes recettes, calculée une fois sur toutes les
# cuisines pour que la sélection ne bouge pas avec les filtres.
spread = (freq[freq["scope"] == "tout"].groupby("ingredient")["pct"].std()
          .sort_values(ascending=False))
top_ingredients = set(spread.index[:N_INGREDIENTS])

# --- Filtres ----------------------------------------------------------------------
SCOPES = {"Toutes les recettes": "tout",
          "Sans desserts, pâtisseries et pains": "sans_desserts"}
scope_label = st.segmented_control(
    "Recettes prises en compte", list(SCOPES), default=list(SCOPES)[0],
    help="Les desserts reposent partout sur le sucre, le beurre, la farine et "
         "l'œuf. Les retirer permet de vérifier que les ressemblances entre "
         "cuisines ne viennent pas seulement de la part de pâtisserie.",
) or list(SCOPES)[0]
scope = SCOPES[scope_label]

c1, c2 = st.columns(2)
show_all_cuisines = c1.toggle(
    f"Tout afficher ({len(cuisines)} cuisines)", value=False,
    help=f"Par défaut : les {PER_CONTINENT} cuisines les mieux représentées de chaque "
         f"continent parmi celles d'au moins {fmt_int(small)} recettes.",
)
show_all_ingredients = c2.toggle(
    f"Tous les ingrédients ({len(INGREDIENT_LABELS)})", value=False,
    help=f"Par défaut : les {N_INGREDIENTS} ingrédients dont la fréquence varie le "
         f"plus d'une cuisine à l'autre.",
)

fam_labels = (families.drop_duplicates("family_id")
              .sort_values("family_id")["family_label"].tolist())
with st.expander("Filtrer par famille de cuisines (regroupement indicatif)"):
    st.caption(
        f"Familles issues d'une classification hiérarchique sur les fréquences "
        f"d'ingrédients. Regroupement indicatif, peu stable : sans les desserts, "
        f"l'accord avec la partition retenue n'est que de "
        f"{fmt_num(stats['ari_sans_desserts'], 2)} (indice de Rand ajusté, "
        f"1 = partition identique). Voir la page Méthodologie."
    )
    selected_fams = st.pills(
        "Familles affichées", fam_labels, selection_mode="multi", default=fam_labels,
    ) or fam_labels

# --- Données de la heatmap ----------------------------------------------------------
shown = cuisines[cuisines["family_label"].isin(selected_fams)]
if not show_all_cuisines:
    shown = shown[shown["country"].isin(default_set)]
shown = shown.assign(bloc_rank=shown["bloc"].map(CONTINENT_ORDER.index)) \
             .sort_values(["bloc_rank", "ordre"])
ingredients = [i for i in INGREDIENT_LABELS if show_all_ingredients or i in top_ingredients]

data = freq[freq["scope"] == scope]
pct = data.pivot(index="country", columns="ingredient", values="pct") * 100
n_scope = data.drop_duplicates("country").set_index("country")["n_recettes"]

# Une ligne d'en-tête (vide) par continent : l'espace et l'étiquette séparent les
# blocs par la position, sans couleur de continent.
z, text, ylabels, custom = [], [], [], []
for bloc, block in shown.groupby("bloc", sort=False):
    ylabels.append(f"<b>{bloc}</b>")
    z.append([None] * len(ingredients))
    text.append([""] * len(ingredients))
    custom.append([""] * len(ingredients))
    for r in block.itertuples():
        n = int(n_scope[r.country])
        star = "*" if r.n_recettes < small else ""
        ylabels.append(f"{r.cuisine} ({fmt_int(n)}){star}")
        if n < min_n:
            z.append([None] * len(ingredients))
            text.append([f"n < {fmt_int(min_n)}"] * len(ingredients))
        else:
            vals = [float(pct.loc[r.country, i]) for i in ingredients]
            z.append(vals)
            text.append([f"{v:.0f}" for v in vals])
        custom.append([fmt_int(n)] * len(ingredients))

n_rows = len(shown)
chart_title(
    "Quels ingrédients reviennent dans les recettes de chaque cuisine ?",
    "Chaque case = part des recettes de la cuisine contenant l'ingrédient (en %). "
    "Plus la case est foncée, plus l'ingrédient est fréquent. Entre parenthèses : "
    f"nombre de recettes ; * = moins de {fmt_int(small)} recettes. Cuisines "
    "regroupées par continent (comme en page 1), et rangées dans chaque bloc par "
    "ressemblance de profil. "
    + ("" if show_all_cuisines else
       f"Vue réduite : {n_rows} cuisines sur {len(cuisines)}. ")
    + ("" if show_all_ingredients else
       f"{len(ingredients)} ingrédients sur {len(INGREDIENT_LABELS)}, ceux qui "
       f"distinguent le plus les cuisines."),
)

xlabels = [INGREDIENT_LABELS[i] for i in ingredients]
fig = go.Figure(go.Heatmap(
    z=z, x=xlabels, y=ylabels,
    colorscale=SEQUENTIAL, zmin=0, zmax=100, xgap=1, ygap=1,
    customdata=custom, hoverongaps=False,
    hovertemplate="%{y}<br>%{x} : %{z:.0f} % des %{customdata} recettes<extra></extra>",
    showscale=False,  # valeurs écrites dans les cases : l'échelle serait redondante
))
# Valeurs écrites par une couche de texte, couleur choisie case par case pour
# garantir le contraste (blanc sur les cases foncées, foncé sur les claires).
cells = [(x, y, t, TEXT if v is None else text_color(v))
         for y, row_z, row_t in zip(ylabels, z, text)
         for x, v, t in zip(xlabels, row_z, row_t) if t]
fig.add_trace(go.Scatter(
    x=[c[0] for c in cells], y=[c[1] for c in cells], text=[c[2] for c in cells],
    mode="text", textfont=dict(size=11, color=[c[3] for c in cells]),
    hoverinfo="skip", showlegend=False,
))
apply_theme(fig, height=max(300, 24 * len(ylabels) + 110))
fig.update_layout(margin=dict(l=10, r=10, t=70, b=10))
fig.update_xaxes(side="top", tickangle=-35, tickfont=dict(color=TEXT, size=12))
fig.update_yaxes(autorange="reversed", tickfont=dict(color=TEXT, size=12))
show(fig)

# --- Notes de lecture (calculées) ------------------------------------------------
excluded = catalog[catalog["n_recettes"] < min_n].sort_values("n_recettes")
notes = [
    f"Cuisines à moins de {fmt_int(min_n)} recettes exclues : "
    + ", ".join(f"{c} ({fmt_int(k)})" for c, k in zip(excluded["cuisine"], excluded["n_recettes"]))
    + "."
]
if scope == "sans_desserts":
    hidden = shown.loc[shown["country"].map(n_scope) < min_n, "cuisine"].tolist()
    if hidden:
        notes.append(
            f"Sans les desserts, il reste moins de {fmt_int(min_n)} recettes pour : "
            + ", ".join(hidden) + " (lignes marquées « n < " + fmt_int(min_n) + " », valeurs masquées)."
        )
# Famille de référence du contrôle (celle de la cuisine allemande, voir pipeline).
bake_family = families.loc[families["country"] == "German", "family_label"].iloc[0]
notes.append(
    f"Effet du contrôle « sans desserts » (similarité cosinus moyenne entre "
    f"profils, 1 = identiques) : toutes cuisines, "
    f"{fmt_num(stats['sim_moyenne_tout'], 2)} avec desserts et "
    f"{fmt_num(stats['sim_moyenne_sans_desserts'], 2)} sans ; famille "
    f"« {bake_family} », {fmt_num(stats['sim_famille_europe_tout'], 2)} et "
    f"{fmt_num(stats['sim_famille_europe_sans_desserts'], 2)}."
)
notes.append(
    "Détection par mot-clé dans la liste d'ingrédients, pluriels compris "
    "(« eggs », « onions »). « Lait » exclut le lait de coco, « beurre » le "
    "beurre de cacahuète, « riz » le vinaigre et le vin de riz."
)
for note in notes:
    st.caption(note)
