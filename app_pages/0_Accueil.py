import streamlit as st
import pandas as pd

from src.load_data import load_processed

st.title("🍲 Les plateformes de recettes reflètent-elles la diversité culinaire mondiale ?")

st.markdown(
    """
Ce projet analyse **16 644 recettes** de la plateforme collaborative Allrecipes
(2 218 catégorisées par pays d'origine, 14 426 recettes générales) pour
questionner une tension entre **diversité culinaire affichée** et
**uniformisation nutritionnelle possible**, sous couvert de notes élevées.

Utilisez le menu à gauche pour naviguer entre les quatre axes d'analyse.
"""
)

col1, col2, col3 = st.columns(3)
try:
    overlap = load_processed("overlap_stats").iloc[0]
    col1.metric("Recettes générales", f"{overlap.n_all_recipes:,.0f}".replace(",", " "))
    col2.metric("Recettes catégorisées par pays", f"{overlap.n_cuisines:,.0f}".replace(",", " "))
    col3.metric(
        "Chevauchement entre les deux tables",
        f"{overlap.pct_cuisines_in_all_recipes:.0%}",
        help="Part des recettes de cuisines.csv qui existent aussi dans all_recipes.csv (jointure sur l'URL)."
    )
except FileNotFoundError as e:
    st.error(str(e))

st.divider()

st.subheader("Les quatre axes")
st.markdown(
    """
1. **🗺️ Carte — L'illusion de la diversité géographique** : les recettes
   par pays s'appuient-elles sur des ingrédients distincts, ou sur une base
   uniformisée ?
2. **🥗 Profil nutritionnel** : les plats internationaux conservent-ils un
   profil diététique propre à leur région ?
3. **⭐ Notes vs nutrition** : les recettes les mieux notées sont-elles
   aussi les plus caloriques / grasses ?
4. **✅ Alternatives saines** : existe-t-il un volume significatif de
   recettes à la fois bien notées et nutritionnellement raisonnables, et
   d'où viennent-elles ?
"""
)

st.info(
    "⚠️ **Limite méthodologique à garder en tête sur toutes les pages** : "
    "la colonne `country` du dataset mélange des nationalités (\"Chinese\") "
    "et des catégories qui ne sont pas des pays (\"Soul Food\", \"Jewish\", "
    "\"Scandinavian\"...). Voir la page Méthodologie pour le détail.",
    icon=":material/warning:",
)
