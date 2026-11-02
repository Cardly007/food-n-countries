import plotly.graph_objects as go
import streamlit as st

from src.dish_type import DESSERT, DISH_GROUPS
from src.load_data import load_processed, load_stats
from src.theme import (
    CATEGORICAL, MUTED, TEXT, apply_theme, chart_title, fmt_int, fmt_pct, page_header, show,
)

stats = load_stats()
mix = load_processed("dish_mix")
val = load_processed("dish_validation").iloc[0]
small = stats["seuil_petit_effectif"]

page_header(
    "facettes",
    "4. Chaque cuisine est-elle montrée par des plats variés ?",
    "Quatrième question : les facettes. Une cuisine présente dans le catalogue "
    "peut n'y être représentée que par un seul type de plat (par exemple ses "
    "pâtisseries). Quelle image de chaque cuisine le catalogue donne-t-il ?",
)

VIEW_ALL = "Toutes les catégories (100 % empilé)"
VIEW_OPTIONS = [VIEW_ALL] + DISH_GROUPS

selected_view = st.segmented_control(
    "Type de plat affiché :",
    VIEW_OPTIONS,
    default=VIEW_ALL,
    help="Sélectionnez 'Toutes les catégories' pour la vue d'ensemble empilée, ou isolez une catégorie pour classer directement les cuisines par ordre décroissant.",
) or VIEW_ALL

colors = dict(zip(DISH_GROUPS, CATEGORICAL))

if selected_view == VIEW_ALL:
    col_sort, _ = st.columns([3, 1])
    with col_sort:
        sort_group = st.segmented_control(
            "Trier les cuisines par part décroissante de :",
            DISH_GROUPS,
            default=DESSERT,
            help="Seul le segment de base (à gauche) se compare avec précision. Choisissez quelle catégorie trie les barres empilées.",
        ) or DESSERT

    ordered_groups = [sort_group] + [g for g in DISH_GROUPS if g != sort_group]
    sorted_sub = mix[mix["dish_group"] == sort_group].sort_values("pct", ascending=False)
    order = sorted_sub["country"].tolist()
    n_total = sorted_sub.set_index("country")["n_total"]
    labels = {c: f"{cu}{'*' if n_total[c] < small else ''}"
              for c, cu in zip(sorted_sub["country"], sorted_sub["cuisine"])}

    chart_title(
        "Quelle part des recettes de chaque cuisine sont des desserts, des plats, des soupes ou des accompagnements ?",
        f"Chaque barre = 100 % des recettes de la cuisine (* = moins de {fmt_int(small)} recettes, "
        f"effectif total au survol). Cuisines triées par part de "
        f"{sort_group.lower()} (premier segment à gauche) : c'est la seule couche qui "
        "se lit précisément, car elle part de zéro ; les autres ne donnent qu'un ordre "
        "de grandeur. Type de plat déduit du titre de la recette (heuristique, voir "
        "ci-dessous).",
    )

    fig = go.Figure()
    for group in ordered_groups:
        g = mix[mix["dish_group"] == group].set_index("country").loc[order]
        fig.add_trace(go.Bar(
            y=[labels[c] for c in order], x=100 * g["pct"], name=group, orientation="h",
            marker=dict(color=colors[group], line=dict(color="white", width=1)),
            customdata=g[["n", "n_total"]],
            hovertemplate=f"<b>%{{y}}</b> — Total : %{{customdata[1]}} recettes<br>"
                          f"{group} : %{{x:.0f}} % (%{{customdata[0]}} sur %{{customdata[1]}})<extra></extra>",
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
        f"« Plats principaux » est le groupe par défaut : il contient aussi les entrées, "
        f"en-cas et garnitures que le titre ne permet pas de reconnaître. "
        f"Cuisines à moins de {fmt_int(stats['seuil_recettes'])} recettes exclues."
    )

else:
    # Catégorie unique isolée : tri décroissant immédiat avec zéro commun
    sub = mix[mix["dish_group"] == selected_view].sort_values("pct", ascending=False).reset_index(drop=True)
    order = sub["country"].tolist()
    n_total = sub.set_index("country")["n_total"]
    labels = {c: f"{cu}{'*' if n_total[c] < small else ''}"
              for c, cu in zip(sub["country"], sub["cuisine"])}

    chart_title(
        f"Quelles cuisines proposent la plus grande part de {selected_view.lower()} ?",
        f"Cuisines triées par ordre décroissant de la part de {selected_view.lower()} (* = moins de {fmt_int(small)} recettes, "
        f"effectif total au survol). En haut : la cuisine où ce type de plat est le plus représenté.",
    )

    median_pct = 100 * sub["pct"].median()
    max_val = 100 * sub["pct"].max()

    fig = go.Figure(go.Bar(
        y=[labels[c] for c in order],
        x=100 * sub["pct"],
        orientation="h",
        marker=dict(color=colors[selected_view], line=dict(color="white", width=0.5)),
        text=[f"{v:.0f} %" for v in 100 * sub["pct"]],
        textposition="outside",
        textfont=dict(size=11, color=TEXT),
        cliponaxis=False,
        customdata=sub[["n", "n_total"]],
        hovertemplate=f"<b>%{{y}}</b> — Total : %{{customdata[1]}} recettes<br>"
                      f"<b>{selected_view} : %{{x:.1f}} %</b> (%{{customdata[0]}} sur %{{customdata[1]}})<extra></extra>",
    ))
    fig.add_vline(x=median_pct, line=dict(color=MUTED, width=1.5, dash="dot"))
    fig.add_annotation(
        x=median_pct, y=1, yref="paper", yanchor="bottom", xanchor="left", xshift=4,
        text=f"médiane : {median_pct:.0f} %", showarrow=False,
        font=dict(size=11, color=MUTED),
    )
    apply_theme(fig, height=22 * len(order) + 80)
    fig.update_layout(
        margin=dict(l=10, r=40, t=30, b=10),
        bargap=0.25,
        showlegend=False,
    )
    fig.update_xaxes(
        range=[0, min(100, max(max_val * 1.15, 30))],
        ticksuffix=" %",
        showgrid=True,
        gridcolor="#F2F2F2",
    )
    fig.update_yaxes(autorange="reversed", tickfont=dict(color=TEXT, size=12))
    show(fig)

    top_cuisine = sub.iloc[0]
    st.caption(
        f"La cuisine avec la plus forte part de {selected_view.lower()} est **{top_cuisine['cuisine']}** "
        f"avec {fmt_pct(top_cuisine['pct'], 0)} de ses recettes ({fmt_int(top_cuisine['n'])} sur {fmt_int(top_cuisine['n_total'])}). "
        f"« Plats principaux » est le groupe par défaut : il contient aussi les entrées, en-cas et garnitures. "
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
