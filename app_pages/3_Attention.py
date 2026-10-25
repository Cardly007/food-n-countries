import plotly.graph_objects as go
import streamlit as st

from src.load_data import load_processed, load_stats
from src.theme import (
    ACCENT, GREY, MUTED, TEXT, apply_theme, chart_title, fmt_int, fmt_num, fmt_pct, show,
)

TOP_N = 5

stats = load_stats()
att = load_processed("attention")

st.title("3. Quelles cuisines le public suit-il ?")
st.caption(
    "Troisième question : l'attention. Toutes les cuisines du catalogue "
    "reçoivent-elles le même intérêt de la part des utilisateurs du site ?"
)

pays = att[att["map_type"] == "single_country"]
OPTIONS = {
    f"Toutes les cuisines ({len(att)})": att,
    f"Pays seulement ({len(pays)})": pays,
}
choice = st.segmented_control(
    "Cuisines comparées", list(OPTIONS), default=list(OPTIONS)[0],
    help="« Pays seulement » retire les traditions régionales ou communautaires "
         "(Sud des États-Unis, cajun, soul food, Tex-Mex, juive, amish) et la "
         "catégorie multi-pays « Scandinave ».",
) or list(OPTIONS)[0]
d = OPTIONS[choice].sort_values("avis_par_recette", ascending=False).reset_index(drop=True)
median = d["avis_par_recette"].median()
top_share = d["avis_total"].head(TOP_N).sum() / d["avis_total"].sum()

chart_title(
    "Combien d'avis une recette de chaque cuisine reçoit-elle en moyenne ?",
    f"Avis par recette = nombre total d'évaluations des recettes de la cuisine ÷ "
    f"nombre de recettes (entre parenthèses). En orange : les {TOP_N} premières. "
    f"Trait vertical : médiane des cuisines affichées. Un « avis » mesure "
    f"l'engagement des utilisateurs, ni la qualité des recettes ni une "
    f"préférence mondiale.",
)

small = stats["seuil_petit_effectif"]
labels = [f"{c} ({fmt_int(n)}){'*' if n < small else ''}"
          for c, n in zip(d["cuisine"], d["n_recettes"])]
colors = [ACCENT if i < TOP_N else GREY for i in range(len(d))]
fig = go.Figure(go.Bar(
    x=d["avis_par_recette"], y=labels, orientation="h",
    marker_color=colors,
    text=[fmt_int(v) for v in d["avis_par_recette"]], textposition="outside",
    textfont=dict(size=11, color=TEXT), cliponaxis=False,
    customdata=d[["avis_total", "n_recettes"]],
    hovertemplate="%{y}<br>%{x:.0f} avis par recette<br>"
                  "%{customdata[0]:,.0f} avis pour %{customdata[1]} recettes<extra></extra>",
))
fig.add_vline(x=median, line=dict(color=MUTED, width=1.5, dash="dot"))
fig.add_annotation(
    x=median, y=1, yref="paper", yanchor="bottom", xanchor="left", xshift=4,
    text=f"médiane : {fmt_int(median)}", showarrow=False,
    font=dict(size=11, color=MUTED),
)
apply_theme(fig, height=22 * len(d) + 80)
fig.update_layout(margin=dict(l=10, r=40, t=30, b=10), bargap=0.25)
fig.update_xaxes(range=[0, d["avis_par_recette"].max() * 1.1], showticklabels=False,
                 showline=False)
fig.update_yaxes(autorange="reversed", tickfont=dict(color=TEXT, size=12))
show(fig)

st.caption(
    f"\\* Moins de {fmt_int(small)} recettes : moyenne fragile, à lire avec prudence. "
    f"Les {TOP_N} premières cuisines regroupent {fmt_pct(top_share)} des "
    f"{fmt_int(d['avis_total'].sum())} avis des cuisines affichées. Les notes "
    f"moyennes varient peu d'une cuisine à l'autre (de "
    f"{fmt_num(d['note_moyenne'].min(), 2)} à {fmt_num(d['note_moyenne'].max(), 2)} "
    f"sur 5) : elles ne distinguent pas les cuisines et ne sont donc pas représentées."
)
st.info(
    f"Audience principalement américaine : ce classement reflète l'intérêt des "
    f"utilisateurs d'Allrecipes, pas les goûts du monde. "
    f"Recettes sans aucune évaluation ({fmt_pct(stats['pct_avis_manquants'], 1)} "
    f"des recettes) comptées pour 0 avis. Vérifications : l'ancienneté d'une "
    f"recette n'explique pas son nombre d'avis (corrélation de rang "
    f"{fmt_num(stats['spearman_anciennete_avis'], 2)}), et le classement reste "
    f"le même si l'on ne garde que les recettes publiées depuis "
    f"{int(stats['annee_recente'])} "
    f"(ρ = {fmt_num(stats['rho_classement_depuis_2022'], 2)}).",
    icon=":material/info:",
)
