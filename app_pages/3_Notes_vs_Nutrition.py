import streamlit as st
import plotly.express as px
from scipy import stats

from src.load_data import load_processed

st.title("Axe 3 — Le biais d'évaluation de la communauté")

use_ai = st.session_state.get("use_ai_dataset", False)

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
        help="L'IA a catégorisé les plats. Cela permet de comparer ce qui est comparable (ex: Les plats principaux les plus gras sont-ils mieux notés ?)"
    )
    if selected_categories:
        df = df[df["recipe_category"].isin(selected_categories)]

min_ratings = st.slider(
    "Nombre minimum d'avis pour inclure une recette",
    0, 200, 10,
    help="Une recette avec 2 avis à 5 étoiles n'est pas comparable à une "
         "recette avec 500 avis à 4.6. On filtre les recettes peu notées "
         "pour éviter un signal bruité.",
)
df = df[df["total_ratings"] >= min_ratings]

col1, col2 = st.columns(2)

with col1:
    st.subheader("Note vs calories")
    fig = px.scatter(
        df.sample(min(3000, len(df)), random_state=0),
        x="calories", y="avg_rating",
        size="total_ratings", # Pondération par l'engagement
        opacity=0.35,
        trendline="ols",
        labels={"calories": "Calories / portion", "avg_rating": "Note moyenne", "total_ratings": "Nombre d'avis"},
    )
    fig.update_layout(height=420)
    st.plotly_chart(fig, width='stretch')
    rho, p = stats.spearmanr(df["calories"], df["avg_rating"])
    st.caption(f"Corrélation de Spearman : ρ = {rho:.3f} (p = {p:.4f}, n = {len(df):,})".replace(",", " "))

with col2:
    if use_ai:
        st.subheader("Note vs Présence de sucres ajoutés")
        # En mode IA, on a la vraie variable NLP pour les sucres ajoutés !
        sugar_stats = df.groupby("has_added_sugar_nlp")["avg_rating"].agg(["mean", "count"]).reset_index()
        sugar_stats["has_added_sugar_nlp"] = sugar_stats["has_added_sugar_nlp"].map(
            {True: "Contient des sucres ajoutés (NLP)", False: "N'en contient pas"}
        )
        st.dataframe(sugar_stats, width='stretch', hide_index=True)
        # Ajout d'un petit boxplot pour visualiser
        fig2 = px.box(
            df, x="has_added_sugar_nlp", y="avg_rating",
            points="all",
            labels={"has_added_sugar_nlp": "Sucres ajoutés", "avg_rating": "Note moyenne"}
        )
        fig2.update_xaxes(tickvals=[False, True], ticktext=["Sans sucres ajoutés", "Avec sucres ajoutés"])
        fig2.update_layout(height=300)
        st.plotly_chart(fig2, width='stretch')
    else:
        st.subheader("Note vs glucides (proxy sucre)")
        fig2 = px.scatter(
            df.sample(min(3000, len(df)), random_state=0),
            x="carbs", y="avg_rating",
            size="total_ratings",
            opacity=0.35,
            trendline="ols",
            labels={"carbs": "Glucides (g) / portion", "avg_rating": "Note moyenne", "total_ratings": "Nombre d'avis"},
        )
        fig2.update_layout(height=420)
        st.plotly_chart(fig2, width='stretch')
        rho2, p2 = stats.spearmanr(df["carbs"], df["avg_rating"])
        st.caption(f"Corrélation de Spearman : ρ = {rho2:.3f} (p = {p2:.4f}, n = {len(df):,})".replace(",", " "))

st.divider()
st.subheader("Ingrédients \"réconfort\" (beurre, crème, fromage, bacon...) et note")
comfort_stats = df.groupby("has_comfort_ingredient")["avg_rating"].agg(["mean", "count"]).reset_index()
comfort_stats["has_comfort_ingredient"] = comfort_stats["has_comfort_ingredient"].map(
    {True: "Contient un ingrédient réconfort", False: "N'en contient pas"}
)
st.dataframe(comfort_stats, width='stretch', hide_index=True)

if use_ai:
    st.success(
        "**Objectif atteint !** Grâce à la classification IA des catégories de plats, "
        "nous pouvons désormais filtrer uniquement sur les 'Main Dish' ou 'Starter'. "
        "Si la corrélation entre les calories et la note reste positive, nous avons "
        "la preuve irréfutable que la plateforme récompense la malbouffe indépendamment "
        "du fait qu'il s'agisse d'un dessert !",
        icon=":material/check_circle:",
    )
else:
    st.info(
        "Une corrélation positive entre note et densité calorique ne prouve "
        "pas une 'prime à la malbouffe' : sans colonne catégorie, une partie du "
        "signal peut venir de la sur-représentation des desserts parmi les "
        "recettes riches. Activez le mode IA dans le menu pour résoudre ce problème.",
        icon=":material/warning:",
    )
