import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from scipy import stats

from src.load_data import load_processed

st.title("Axe 3 — Le biais d'évaluation de la communauté")
st.markdown("#### *Les internautes récompensent-ils systématiquement le gras et le sucre ?*")
with st.expander("🌍 Contexte culturel & historique : La conquête mondiale du sucre et du gras"):
    st.markdown("""
    **Pourquoi trouvons-nous du sucre et du gras dans autant de recettes ?**
    
    * **L'illusion du 'tout sucré' :** Jusqu'au XVIIIᵉ siècle, le sucre était un produit de luxe inaccessible. La cuisine traditionnelle méditerranéenne (Grecque, Espagnole) ou asiatique salée ne l'utilisait pratiquement pas. C'est l'industrialisation américaine du XXᵉ siècle qui a généralisé les sucres ajoutés même dans les plats salés.
    * **Ce que disent nos données par pays :**
      * **Les moins sucrés :** Le Pakistan (**12%** de recettes avec sucre), l'Argentine (**17%**) et la Grèce (**18%**).
      * **Le paradoxe thaïlandais :** **84%** des recettes thaïes utilisent du sucre (sucre de palme indispensable à l'équilibre acide/piment), mais seulement **26%** de graisses lourdes (pas de beurre ni de fromage).
      * **L'Europe du Nord :** Suède et Pays-Bas dépassent **90%** de recettes sucrées/beurrées sur la plateforme (forte sur-représentation des pâtisseries et traditions du goûter).
    """)

use_ai = st.session_state.get("use_ai_dataset", False)

# 1. Chargement et filtres
if not use_ai:
    source = st.segmented_control(
        "Population analysée",
        ["Recettes générales (14 426)", "Recettes catégorisées par pays (2 218)"],
        default="Recettes générales (14 426)"
    )
    df = load_processed("all_recipes_enriched") if source and "générales" in source else load_processed("cuisines_enriched")
else:
    df = load_processed("all_recipes_enriched")
    categories = df["recipe_category"].dropna().unique().tolist()
    if "Unknown" in categories:
        categories.remove("Unknown")
        
    selected_categories = st.multiselect(
        "Filtrer par catégorie de plat (Classification IA)",
        options=sorted(categories),
        default=None,
        help="Permet d'isoler les plats principaux des desserts pour neutraliser le biais de catégorie."
    )
    if selected_categories:
        df = df[df["recipe_category"].isin(selected_categories)]

min_ratings = st.slider(
    "Filtrer le bruit : nombre minimum d'avis par recette",
    0, 100, 10,
    help="Évite les notes extrêmes (ex: 5.0 avec seulement 1 avis)."
)

# Nettoyage des NaN pour assurer la cohérence statistique des calculs
df = df[df["total_ratings"] >= min_ratings].copy()
df = df.dropna(subset=["calories", "fat", "carbs", "avg_rating", "total_ratings"]).copy()

st.divider()

# -------------------------------------------------------------
# VISUALISATION 1 : Tendance par tranche calorique
# -------------------------------------------------------------
st.subheader("1. La note moyenne progresse-t-elle avec les calories ?")
st.caption("Découpage des recettes en tranches de 250 kcal pour dépasser la dispersion du nuage de points brut.")

bins = [0, 250, 500, 750, 1000, 10000]
labels = ["Très léger (<250 kcal)", "Modéré (250-500)", "Riche (500-750)", "Très riche (750-1000)", "Extrême (>1000)"]
df["cal_bracket"] = pd.cut(df["calories"], bins=bins, labels=labels)

cal_summary = (
    df.dropna(subset=["cal_bracket"])
    .groupby("cal_bracket", observed=False)
    .agg(
        avg_rating=("avg_rating", "mean"),
        count=("name", "count"),
        avg_reviews=("total_ratings", "median")
    )
    .reset_index()
)

total_recipes = cal_summary["count"].sum()
cal_summary["pct"] = (cal_summary["count"] / total_recipes) * 100

# Format de l'étiquette : Note + Nombre de recettes
cal_summary["bar_label"] = cal_summary.apply(
    lambda r: f"{r['avg_rating']:.2f} ★  ({r['count']:,} recettes)".replace(",", " "),
    axis=1
)

col_a, col_b = st.columns([3, 2])

with col_a:
    fig_cal = px.bar(
        cal_summary,
        x="avg_rating",
        y="cal_bracket",
        orientation="h",
        text="bar_label",
        labels={"avg_rating": "Note moyenne", "cal_bracket": "Tranche calorique"},
        color="avg_rating",
        color_continuous_scale="Blues",
    )
    fig_cal.update_traces(
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Note moyenne : %{x:.2f} ★<br>"
            "Effectif : %{customdata[0]:,} recettes (%{customdata[1]:.1f}%)<br>"
            "Médiane d'avis : %{customdata[2]} avis<extra></extra>"
        ),
        customdata=cal_summary[["count", "pct", "avg_reviews"]].values
    )
    fig_cal.update_xaxes(range=[4.0, 5.0], title_text="Note moyenne (sur 5)")
    fig_cal.update_layout(height=340, coloraxis_showscale=False, yaxis_title=None)
    st.plotly_chart(fig_cal, width="stretch")

with col_b:
    st.markdown("##### 📊 Synthèse dynamique")
    if not cal_summary.empty:
        best_bracket = cal_summary.loc[cal_summary["avg_rating"].idxmax()]
        worst_bracket = cal_summary.loc[cal_summary["avg_rating"].idxmin()]
        delta_rating = best_bracket["avg_rating"] - worst_bracket["avg_rating"]
        
        st.metric(
            "Tranche la mieux notée",
            f"{best_bracket['cal_bracket']}",
            f"{best_bracket['avg_rating']:.2f} ★ (écart max: +{delta_rating:.2f})"
        )
    
    rho, p = stats.spearmanr(df["calories"], df["avg_rating"])
    st.metric(
        "Corrélation de Spearman (ρ)",
        f"{rho:.3f}",
        help="Une valeur proche de 0 indique qu'il n'y a pas de progression continue entre calories et note."
    )
    st.caption(f"Calculé sur **{len(df):,} recettes** filtrées.".replace(",", " "))

# -------------------------------------------------------------
# VISUALISATION 2 : Ingrédients clés — Le Duel Gras vs Sucre
# -------------------------------------------------------------
st.divider()
st.subheader("2. Quel est l'impact réel des ingrédients plaisirs (Gras vs Sucre) ?")
st.caption("Comparaison directe de la note moyenne et de l'engagement selon la présence de gras ou de sucre ajouté.")

# Sélecteur de l'ingrédient à tester
ingredient_type = st.segmented_control(
    "Levier de gourmandise testé :",
    ["Gras / Réconfort (beurre, crème, fromage, bacon)", "Sucres ajoutés (sucre, miel, chocolat, sirop)"],
    default="Gras / Réconfort (beurre, crème, fromage, bacon)"
)

# Détermination de la variable à analyser
if "Gras" in ingredient_type:
    test_col = "has_comfort_ingredient"
    label_true = "Avec ingrédient réconfort"
    label_false = "Sans ingrédient réconfort"
    sub_caption = "Ingrédients détectés : beurre, crème, fromage, bacon, mayonnaise."
else:
    # Si mode IA disponible, on utilise le champ NLP sinon le proxy regex
    test_col = "has_added_sugar_nlp" if (use_ai and "has_added_sugar_nlp" in df.columns) else "has_sugar_proxy"
    label_true = "Avec sucres ajoutés"
    label_false = "Sans sucres ajoutés"
    sub_caption = "Ingrédients détectés : sucre, miel, sirop d'érable, mélasse, pépites de chocolat."

ingredient_summary = (
    df.groupby(test_col)
    .agg(
        note_moyenne=("avg_rating", "mean"),
        avis_mediane=("total_ratings", "median"),
        nb_recettes=("name", "count")
    )
    .reset_index()
)
ingredient_summary["label"] = ingredient_summary[test_col].map({
    True: label_true,
    False: label_false
})

ingredient_summary["label_note"] = ingredient_summary.apply(
    lambda r: f"{r['note_moyenne']:.2f} ★  ({r['nb_recettes']:,} recettes)".replace(",", " "), axis=1
)
ingredient_summary["label_eng"] = ingredient_summary.apply(
    lambda r: f"{int(r['avis_mediane'])} avis  ({r['nb_recettes']:,} recettes)".replace(",", " "), axis=1
)

c1, c2 = st.columns(2)

with c1:
    fig_ing_note = px.bar(
        ingredient_summary,
        x="note_moyenne",
        y="label",
        orientation="h",
        text="label_note",
        color=test_col,
        color_discrete_map={True: "#2563EB", False: "#94A3B8"},
        labels={"note_moyenne": "Note moyenne", "label": ""}
    )
    fig_ing_note.update_traces(textposition="outside")
    fig_ing_note.update_xaxes(range=[4.0, 5.0])
    fig_ing_note.update_layout(height=240, showlegend=False, yaxis_title=None)
    st.plotly_chart(fig_ing_note, width="stretch")

with c2:
    fig_ing_eng = px.bar(
        ingredient_summary,
        x="avis_mediane",
        y="label",
        orientation="h",
        text="label_eng",
        color=test_col,
        color_discrete_map={True: "#2563EB", False: "#94A3B8"},
        labels={"avis_mediane": "Médiane des avis", "label": ""}
    )
    fig_ing_eng.update_traces(textposition="outside")
    max_eng = ingredient_summary["avis_mediane"].max()
    fig_ing_eng.update_xaxes(range=[0, max_eng * 1.5])
    fig_ing_eng.update_layout(height=240, showlegend=False, yaxis_title=None)
    st.plotly_chart(fig_ing_eng, width="stretch")

st.caption(f"💡 *{sub_caption}*")

# -------------------------------------------------------------
# VISUALISATION 3 : Heatmap Nutritionnelle 2D (Gras vs Sucre)
# -------------------------------------------------------------
st.divider()
st.subheader("3. Matrice nutritionnelle : Quel équilibre Gras vs Glucides séduit le plus ?")
st.caption("Carte de chaleur (Heatmap) croisant le niveau de lipides et de glucides pour révéler la combinaison gagnante.")

# Découpage en terciles (Faible, Moyen, Riche)
df["fat_level"] = pd.qcut(df["fat"], q=3, labels=["Faible en gras", "Moyen en gras", "Riche en gras"])
df["carb_level"] = pd.qcut(df["carbs"], q=3, labels=["Faible en glucides", "Moyen en glucides", "Riche en glucides"])

# Choix de la métrique à observer
metric_choice = st.radio(
    "Métrique analysée dans la matrice :",
    ["Note moyenne (Satisfaction)", "Médiane des avis (Engagement)"],
    horizontal=True
)

agg_col = "avg_rating" if "Note" in metric_choice else "total_ratings"
agg_fn = "mean" if "Note" in metric_choice else "median"

matrix_stats = (
    df.groupby(["carb_level", "fat_level"], observed=False)
    .agg(
        valeur=(agg_col, agg_fn),
        effectif=("name", "count")
    )
    .reset_index()
)

# Préparation du tableau pivot pour la Heatmap
pivot_val = matrix_stats.pivot(index="carb_level", columns="fat_level", values="valeur")
pivot_count = matrix_stats.pivot(index="carb_level", columns="fat_level", values="effectif")

# Création des textes annotés au centre de chaque case
text_matrix = []
for carb in pivot_val.index:
    row_text = []
    for fat in pivot_val.columns:
        v = pivot_val.loc[carb, fat]
        c = pivot_count.loc[carb, fat]
        if "Note" in metric_choice:
            row_text.append(f"<b>{v:.2f} ★</b><br><span style='font-size:11px;'>({c:,} recettes)</span>".replace(",", " "))
        else:
            row_text.append(f"<b>{int(v)} avis</b><br><span style='font-size:11px;'>({c:,} recettes)</span>".replace(",", " "))
    text_matrix.append(row_text)

fig_heatmap = go.Figure(
    data=go.Heatmap(
        z=pivot_val.values,
        x=list(pivot_val.columns),
        y=list(pivot_val.index),
        text=text_matrix,
        texttemplate="%{text}",
        textfont={"size": 13},
        colorscale="YlGnBu",
        hoverongaps=False,
    )
)

fig_heatmap.update_layout(
    height=400,
    xaxis_title="Teneur en Lipides (Gras)",
    yaxis_title="Teneur en Glucides (Proxy Sucre)",
    yaxis=dict(autorange="reversed"),
)
st.plotly_chart(fig_heatmap, width="stretch")
