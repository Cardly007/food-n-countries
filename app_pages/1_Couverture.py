import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.load_data import load_processed, load_stats
from src.theme import (
    ACCENT, ACCENT_LIGHT, DIV_NEG, DIV_POS, GREY, GREY_LIGHT, MUTED, apply_theme,
    chart_title, fmt_int, fmt_num, fmt_pct, show,
)

stats = load_stats()
catalog = load_processed("cuisine_catalog")
continents = load_processed("continent_summary")
presence = load_processed("map_presence")

st.title("1. Le catalogue couvre-t-il le monde ?")
st.caption(
    "Première question : l'offre. On regarde quelles cuisines **existent** "
    "dans le catalogue d'Allrecipes, sans tenir compte de leur nombre de "
    "recettes (voir l'encadré en bas de page)."
)

with_regional = st.toggle(
    "Inclure les traditions régionales",
    value=True,
    help="Rattache les catégories qui ne sont pas des cuisines nationales à leur "
         "territoire d'origine : soul food, cajun et créole, Sud des États-Unis, "
         "amish et Tex-Mex aux États-Unis (Tex-Mex aussi au Mexique), Scandinave au "
         "Danemark, à la Norvège et à la Suède. Désactivé : seules les catégories "
         "nationales comptent.",
)

# --- Carte présent / absent ---------------------------------------------------
NATIONAL, INDIRECT = "Catégorie nationale", "Présence indirecte (tradition régionale)"
shown = presence if with_regional else presence[presence["statut"] == "nationale"]
by_iso = (
    shown.assign(label=shown["cuisine"].where(
        shown["statut"] == "nationale", shown["cuisine"] + " (indirecte)"))
    .groupby("iso3")
    .agg(statut=("statut", lambda s: NATIONAL if (s == "nationale").any() else INDIRECT),
         cuisines=("label", lambda s: "<br>".join(s)))
    .reset_index()
)
n_national = int((by_iso["statut"] == NATIONAL).sum())
n_indirect = int((by_iso["statut"] == INDIRECT).sum())
not_mapped = catalog[~catalog["country"].isin(shown["country"])
                     & (catalog["map_type"] != "single_country")]

subtitle = (f"Orange : pays dont la cuisine a sa propre catégorie sur Allrecipes "
            f"({fmt_int(n_national)} pays). ")
if with_regional:
    subtitle += (f"Orange clair : pays présents seulement à travers une tradition "
                 f"régionale ({fmt_int(n_indirect)} pays). ")
subtitle += ("Gris : aucune catégorie nationale dans le catalogue"
             + (" ni tradition régionale. " if with_regional else ". ")
             + "Survolez un pays pour voir les catégories.")
chart_title("Quels pays ont leur cuisine dans le catalogue ?", subtitle)

fig = px.choropleth(
    by_iso, locations="iso3", color="statut",
    color_discrete_map={NATIONAL: ACCENT, INDIRECT: ACCENT_LIGHT},
    category_orders={"statut": [NATIONAL, INDIRECT]},
    hover_name="cuisines",
    hover_data={"iso3": False, "statut": False, "cuisines": False},
)
fig.update_traces(marker_line_color="white", marker_line_width=0.5)
fig.update_geos(
    projection_type="natural earth",
    showframe=False, showcoastlines=False,
    showland=True, landcolor=GREY_LIGHT,
    showcountries=True, countrycolor="white",
    lataxis_range=[-57, 85],
    bgcolor="white",
)
apply_theme(fig, height=460)
fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
show(fig)

if with_regional:
    st.caption(
        "Le Mexique n'a pas de catégorie propre sur Allrecipes : il n'apparaît qu'à "
        "travers le Tex-Mex, cuisine texane d'inspiration mexicaine. Les États-Unis "
        "n'ont pas non plus de catégorie nationale, seulement des traditions "
        "régionales. Non rattachée : "
        + ", ".join(f"{c} ({fmt_int(n)} recettes)"
                    for c, n in zip(not_mapped["cuisine"], not_mapped["n_recettes"]))
        + ", cuisine de diaspora sans territoire (Israël a sa propre catégorie)."
    )
else:
    st.caption(
        f"Non cartographiables ({len(not_mapped)} catégories, "
        f"{fmt_int(not_mapped['n_recettes'].sum())} recettes) : "
        + ", ".join(sorted(not_mapped["cuisine"]))
        + ". Ce sont des traditions régionales ou communautaires, ou une région "
        "multi-pays (« Scandinave »). Elles restent dans les pages 2 à 4."
    )

st.divider()

# --- Diagramme à flèches par continent ------------------------------------------
perimetre = "regional" if with_regional else "national"
continents = continents[continents["perimetre"] == perimetre]
n_cont = int(stats["n_categories_continent_regional" if with_regional
                   else "n_categories_continent"])
chart_title(
    "Le poids de chaque continent dans le catalogue suit-il son poids dans la population mondiale ?",
    f"Chaque flèche part de la part du continent dans la population mondiale "
    f"(point gris) et arrive à sa part parmi les {n_cont} catégories de "
    f"cuisine rattachées à un continent. Orange : plus présent dans le "
    f"catalogue que dans la population ; bleu : moins présent. Étiquette : "
    f"écart en points de pourcentage. Les catégories sont comptées une à une, "
    f"pas en recettes."
    + (" Traditions régionales incluses (bascule en haut de page)." if with_regional
       else " Catégories nationales et multi-pays seulement."),
)

c = continents.sort_values("ecart_points")  # le plus sous-représenté en bas
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=100 * c["pct_population"], y=c["continent"], mode="markers",
    marker=dict(color=GREY, size=11), name="Population mondiale",
    customdata=c[["population_millions"]],
    hovertemplate="%{y}<br>Population : %{x:.1f} % (%{customdata[0]:,.0f} M hab.)<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=100 * c["pct_categories"], y=c["continent"], mode="markers",
    marker=dict(size=1, color="rgba(0,0,0,0)"), name="Catalogue",
    customdata=c[["n_categories"]],
    hovertemplate="%{y}<br>Catalogue : %{x:.1f} % (%{customdata[0]} catégories)<extra></extra>",
))
for _, r in c.iterrows():
    color = DIV_POS if r["ecart_points"] > 0 else DIV_NEG
    x0, x1 = 100 * r["pct_population"], 100 * r["pct_categories"]
    fig.add_annotation(
        x=x1, y=r["continent"], ax=x0, ay=r["continent"],
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2.5, arrowcolor=color,
        text="",
    )
    sign = "+" if r["ecart_points"] > 0 else "−"
    fig.add_annotation(
        x=max(x0, x1), y=r["continent"], xanchor="left", xshift=10,
        text=f"<b>{sign}{fmt_num(abs(r['ecart_points']), 0)} pts</b>",
        showarrow=False, font=dict(color=color, size=13),
    )
# Étiquetage direct des deux extrémités sur la ligne du haut (pas de légende).
top = c.iloc[-1]
for x, label in [(100 * top["pct_population"], "population"),
                 (100 * top["pct_categories"], "catalogue")]:
    fig.add_annotation(x=x, y=top["continent"], yshift=16, text=label,
                       showarrow=False, font=dict(color=MUTED, size=11))
apply_theme(fig, height=380)
fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=10))
fig.update_xaxes(range=[0, 100], ticksuffix=" %", showgrid=True,
                 gridcolor="#F2F2F2", title_text=None)
fig.update_yaxes(title_text=None)
show(fig)

all_perim = load_processed("continent_summary").set_index(["perimetre", "continent"])
na_nat = all_perim.loc[("national", "Amérique du Nord")]
na_reg = all_perim.loc[("regional", "Amérique du Nord")]
asia = continents.set_index("continent").loc["Asie"]
europe = continents.set_index("continent").loc["Europe"]
st.caption(
    f"Lecture : l'Europe représente {fmt_pct(europe['pct_population'])} de la "
    f"population mondiale et {fmt_pct(europe['pct_categories'])} des catégories ; "
    f"l'Asie, {fmt_pct(asia['pct_population'])} et "
    f"{fmt_pct(asia['pct_categories'])}. Population : worldpopulationreview.com "
    f"(tableau de la Séance 5 du cours). Avec les traditions régionales, l'Amérique "
    f"du Nord passe de {fmt_int(na_nat['n_categories'])} à "
    f"{fmt_int(na_reg['n_categories'])} catégories "
    f"({fmt_pct(na_nat['pct_categories'])} → {fmt_pct(na_reg['pct_categories'])}). "
    f"Les Caraïbes sont comptées en Amérique "
    f"du Nord. Une catégorie peut couvrir un petit pays comme un pays très "
    f"peuplé : la comparaison porte sur la variété de l'offre, pas sur "
    f"une « juste » proportion."
)

# --- Profondeur : petits effectifs ----------------------------------------------
small = catalog[catalog["n_recettes"] < stats["seuil_petit_effectif"]].sort_values("n_recettes")
with st.expander(f"Quelles cuisines n'ont que peu de recettes ? ({len(small)} catégories sous "
                 f"{fmt_int(stats['seuil_petit_effectif'])} recettes)"):
    st.warning(
        f"La collecte est plafonnée : {fmt_int(stats['n_categories_plafond'])} catégories sur "
        f"{fmt_int(stats['n_categories'])} ont {fmt_int(stats['seuil_plafond'])} recettes ou plus, et aucune n'en dépasse "
        f"{fmt_int(stats['max_recettes_categorie'])}. Le nombre de recettes d'une grande "
        f"cuisine ne mesure donc pas sa place réelle sur le site. Seuls les petits "
        f"effectifs ci-dessous sont informatifs.",
        icon=":material/warning:",
    )
    st.dataframe(
        small.assign(continent=small["continent"].fillna("— (hors continent)"))
        [["cuisine", "continent", "n_recettes"]].rename(columns={
            "cuisine": "Cuisine", "continent": "Continent", "n_recettes": "Recettes"}),
        hide_index=True, width="stretch",
    )
