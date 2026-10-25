import textwrap

import plotly.graph_objects as go
import streamlit as st

from src.ingredients import INGREDIENT_LABELS
from src.load_data import load_processed, load_stats
from src.theme import (
    MUTED, SEQUENTIAL, TEXT, apply_theme, chart_title, fmt_int, fmt_num, show,
)

stats = load_stats()
freq = load_processed("ingredient_freq")
families = load_processed("cuisine_families")
catalog = load_processed("cuisine_catalog")

st.title("2. Les cuisines sont-elles vraiment différentes dans l'assiette ?")
st.caption(
    "Deuxième question : le contenu. Au-delà de l'étiquette « grecque » ou "
    "« thaïlandaise », les recettes de chaque cuisine utilisent-elles des "
    "ingrédients différents ?"
)

# --- Filtres ----------------------------------------------------------------------
SCOPES = {"Toutes les recettes": "tout",
          "Sans desserts, pâtisseries et pains": "sans_desserts"}
fam_labels = (families.drop_duplicates("family_id")
              .sort_values("family_id")["family_label"].tolist())

scope_label = st.segmented_control(
    "Recettes prises en compte", list(SCOPES), default=list(SCOPES)[0],
    help="Les desserts reposent partout sur le sucre, le beurre, la farine et "
         "l'œuf. Les retirer permet de vérifier que les ressemblances entre "
         "cuisines ne viennent pas seulement de la part de pâtisserie.",
) or list(SCOPES)[0]
selected = st.pills(
    "Familles de cuisines affichées", fam_labels, selection_mode="multi",
    default=fam_labels,
    help="Familles obtenues par classification hiérarchique sur les fréquences "
         "d'ingrédients (toutes recettes). Voir la page Méthodologie.",
) or fam_labels
scope = SCOPES[scope_label]

# --- Données de la heatmap ----------------------------------------------------------
min_n = stats["seuil_recettes"]
rows = families[families["family_label"].isin(selected)].sort_values("ordre")
data = freq[freq["scope"] == scope]
mat = (data.pivot(index="country", columns="ingredient", values="pct")
       .loc[rows["country"], list(INGREDIENT_LABELS)] * 100)
n = data.drop_duplicates("country").set_index("country")["n_recettes"].loc[rows["country"]]
too_small = n < min_n
mat[too_small] = float("nan")

ylabels = [f"{c} ({fmt_int(k)})" for c, k in zip(rows["cuisine"], n)]
text = mat.map(lambda v: "" if v != v else f"{v:.0f}")
text[too_small] = "n < " + fmt_int(min_n)
hover_n = [[fmt_int(k)] * mat.shape[1] for k in n]

chart_title(
    "Quels ingrédients reviennent dans les recettes de chaque cuisine ?",
    "Chaque case = part des recettes de la cuisine contenant l'ingrédient (en %). "
    "Plus la case est foncée, plus l'ingrédient est fréquent. Entre parenthèses : "
    "nombre de recettes. Les lignes sont regroupées en familles de cuisines aux "
    "profils proches (nom à droite).",
)

fig = go.Figure(go.Heatmap(
    z=mat.values, x=list(INGREDIENT_LABELS.values()), y=ylabels,
    text=text.values, texttemplate="%{text}", textfont=dict(size=11),
    colorscale=SEQUENTIAL, zmin=0, zmax=100, xgap=1, ygap=1,
    customdata=hover_n,
    hovertemplate="%{y}<br>%{x} : %{z:.0f} % des %{customdata} recettes<extra></extra>",
    showscale=False,  # valeurs écrites dans les cases : l'échelle serait redondante
))

# Séparateurs et noms de familles (à droite des lignes concernées).
row_h = 22
for fam_id, block in rows.reset_index(drop=True).groupby("family_id", sort=False):
    first, last = block.index.min(), block.index.max()
    if first > 0:
        fig.add_shape(type="line", xref="paper", x0=0, x1=1, yref="y",
                      y0=first - 0.5, y1=first - 0.5, layer="above",
                      line=dict(color=TEXT, width=1.5))
    label = block["family_label"].iloc[0]
    traits = block["family_traits"].iloc[0]
    fig.add_annotation(
        x=1.0, xref="paper", xanchor="left", xshift=8,
        y=(first + last) / 2, yref="y", yanchor="middle",
        text="<b>" + "<br>".join(textwrap.wrap(label, 30)) + "</b><br>"
             f"<span style='color:{MUTED}'>plus fréquents :<br>{traits}</span>",
        showarrow=False, align="left", font=dict(size=11, color=TEXT),
    )

apply_theme(fig, height=max(320, row_h * len(rows) + 110))
fig.update_layout(margin=dict(l=10, r=210, t=60, b=10))
fig.update_xaxes(side="top", tickangle=-35, tickfont=dict(color=TEXT))
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
    hidden = rows.loc[too_small.values, "cuisine"].tolist()
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
