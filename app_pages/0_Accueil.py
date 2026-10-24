import streamlit as st
import pandas as pd

from src.load_data import load_processed

st.title(":material/soup_kitchen: Les plateformes de recettes reflètent-elles la diversité culinaire mondiale ?")

use_ai = st.session_state.get("use_ai_dataset", False)

if use_ai:
    st.markdown(
        """
Ce projet analyse **16 644 recettes** de la plateforme collaborative Allrecipes, 
intégralement géolocalisées et classifiées grâce à l'Intelligence Artificielle (LLM). 
L'objectif est de questionner la tension entre **diversité culinaire affichée** et 
**uniformisation nutritionnelle**, en comparant toutes les cuisines à l'écrasante majorité de recettes "standard" américaines (65% du trafic).

Utilisez le menu à gauche pour naviguer entre les quatre axes d'analyse.
    """
    )
else:
    st.markdown(
        """
Ce projet analyse **16 644 recettes** de la plateforme collaborative Allrecipes
(dont seules **2 218** sont catégorisées par pays d'origine de base) pour
questionner une tension entre **diversité culinaire affichée** et
**uniformisation nutritionnelle possible**, sous couvert de notes élevées.

Utilisez le menu à gauche pour naviguer entre les quatre axes d'analyse.
    """
    )

col1, col2, col3 = st.columns(3)
try:
    if use_ai:
        df = load_processed("all_recipes_enriched")
        col1.metric("Recettes totales analysées", f"{len(df):,.0f}".replace(",", " "))
        
        # On calcule le nombre de pays uniques 
        n_countries = df["country"].nunique()
        col2.metric("Pays représentés", str(n_countries))
        
        usa_pct = (len(df[df["country"] == "USA"]) / len(df)) * 100
        col3.metric("Poids des USA", f"{usa_pct:.1f}%")
        
    else:
        overlap = load_processed("overlap_stats").iloc[0]
        col1.metric("Recettes générales (Sans pays)", f"{overlap.n_all_recipes:,.0f}".replace(",", " "))
        col2.metric("Recettes avec pays (cuisines.csv)", f"{overlap.n_cuisines:,.0f}".replace(",", " "))
except FileNotFoundError as e:
    st.error(str(e))

st.divider()

st.subheader("Les quatre axes")
st.markdown(
    """
1. **:material/public: Carte — L'illusion de la diversité géographique** : les recettes
   par pays s'appuient-elles sur des ingrédients distincts, ou sur une base
   uniformisée ?
2. **:material/set_meal: Profil nutritionnel** : les plats internationaux conservent-ils un
   profil diététique propre à leur région ?
3. **:material/star: Notes vs nutrition** : les recettes les mieux notées sont-elles
   aussi les plus caloriques / grasses ?
4. **:material/check_circle: Alternatives saines** : existe-t-il un volume significatif de
   recettes à la fois bien notées et nutritionnellement raisonnables, et
   d'où viennent-elles ?
"""
)

if not use_ai:
    st.info(
        "**Limite méthodologique** : La version de base du dataset mélange des nationalités et des catégories floues (Soul Food). Activez le mode **'Dataset IA Enrichi'** dans le menu de gauche pour corriger ce biais avec 16 000 recettes propres !",
        icon=":material/warning:",
    )
