import plotly.graph_objects as go
import streamlit as st

from src.dish_type import DESSERT, DISH_GROUPS
from src.load_data import load_processed, load_stats
from src.theme import CATEGORICAL, TEXT, apply_theme, chart_title, fmt_int, fmt_pct, show

stats = load_stats()
mix = load_processed("dish_mix")
val = load_processed("dish_validation").iloc[0]
small = stats["seuil_petit_effectif"]

st.title("4. Chaque cuisine est-elle montrée par des plats variés ?")
st.caption(
    "Quatrième question : les facettes. Une cuisine présente dans le catalogue "
    "peut n'y être représentée que par un seul type de plat (par exemple ses "
    "pâtisseries). Quelle image de chaque cuisine le catalogue donne-t-il ?"
)

# Tri par part de desserts (le segment de base, le seul lisible avec précision).
dessert = mix[mix["dish_group"] == DESSERT].sort_values("pct", ascending=False)
order = dessert["country"].tolist()
n_total = dessert.set_index("country")["n_total"]
labels = {c: f"{cu} ({fmt_int(n_total[c])}){'*' if n_total[c] < small else ''}"
          for c, cu in zip(dessert["country"], dessert["cuisine"])}
colors = dict(zip(DISH_GROUPS, CATEGORICAL))

chart_title(
    "Quelle part des recettes de chaque cuisine sont des desserts, des plats, des soupes ou des accompagnements ?",
    "Chaque barre = 100 % des recettes de la cuisine (effectif entre parenthèses, "
    f"* = moins de {fmt_int(small)} recettes). Les cuisines sont triées par part de "
    "desserts, pâtisseries et pains (en orange), premier segment à gauche : c'est "
    "la seule couche qui se lit précisément, car elle part de zéro ; les autres "
    "couches ne donnent qu'un ordre de grandeur. Type de plat déduit du titre de "
    "la recette (heuristique, voir ci-dessous).",
)

fig = go.Figure()
for group in DISH_GROUPS:
    g = mix[mix["dish_group"] == group].set_index("country").loc[order]
    fig.add_trace(go.Bar(
        y=[labels[c] for c in order], x=100 * g["pct"], name=group, orientation="h",
        marker=dict(color=colors[group], line=dict(color="white", width=1)),
        text=[f"{v:.0f}" if group == DESSERT and v >= 5 else "" for v in 100 * g["pct"]],
        textposition="inside", insidetextanchor="start",
        textfont=dict(color=TEXT, size=11),  # texte foncé : contraste 6,7:1 sur l'orange
        customdata=g[["n", "n_total"]],
        hovertemplate=f"%{{y}}<br>{group} : %{{x:.0f}} % "
                      "(%{customdata[0]} recettes sur %{customdata[1]})<extra></extra>",
    ))
apply_theme(fig, height=22 * len(order) + 110)
fig.update_layout(
    barmode="stack", bargap=0.2,
    legend=dict(orientation="h", x=0, xanchor="left", y=1.0, yanchor="bottom",
                traceorder="normal", font=dict(size=12)),
    margin=dict(l=10, r=10, t=50, b=10),
)
fig.update_xaxes(range=[0, 100], ticksuffix=" %", showgrid=True,
                 gridcolor="#F2F2F2", dtick=25)
fig.update_yaxes(autorange="reversed", tickfont=dict(color=TEXT, size=12))
show(fig)

st.caption(
    f"Nombre dans le premier segment : part des desserts, pâtisseries et pains (%). "
    f"« Plats principaux » est le groupe par défaut : il contient aussi les entrées, "
    f"en-cas et garnitures que le titre ne permet pas de reconnaître. "
    f"Cuisines à moins de {fmt_int(stats['seuil_recettes'])} recettes exclues."
)
st.info(
    f"Le type de plat n'existe pas dans les données : chaque recette est classée par "
    f"mots-clés du titre (« cake », « soup », « salad »…). Taux d'erreur estimé : "
    f"{fmt_pct(val['taux_erreur'])} (intervalle de confiance à 95 % : "
    f"{fmt_pct(val['ic95_bas'])} à {fmt_pct(val['ic95_haut'])}), calculé sur un "
    f"échantillon aléatoire de {fmt_int(val['n_echantillon'])} recettes "
    f"(`validation_type_plat.csv`). Les verdicts de cet échantillon ont été posés "
    f"par l'IA et doivent encore être relus par le groupe. "
    f"{fmt_int(val['n_desserts_manques'])} des {fmt_int(val['n_erreurs'])} erreurs "
    f"relevées sont des desserts ou des pains classés en plats : la part des "
    f"desserts est donc plutôt sous-estimée. Les écarts de quelques points entre "
    f"deux cuisines ne sont pas interprétables.",
    icon=":material/info:",
)
