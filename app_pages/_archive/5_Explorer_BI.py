import streamlit as st
import pygwalker as pyg
from src.load_data import load_all_recipes, load_cuisines

st.title("📊 Explorer — Tableau de bord BI (PyGWalker)")

st.markdown(
    """
Cette page embarque **PyGWalker**, un outil d'exploration visuelle de données 
qui transforme vos DataFrames Pandas en une interface similaire à Tableau Software.

Vous pouvez drag-and-drop les variables pour explorer les jeux de données librement.
"""
)

dataset_choice = st.segmented_control(
    "Choisissez le jeu de données à explorer :", 
    ["Toutes les recettes (all_recipes)", "Recettes par pays (cuisines)"],
    default="Toutes les recettes (all_recipes)"
)

with st.spinner("Chargement des données..."):
    if dataset_choice == "Toutes les recettes (all_recipes)":
        df = load_all_recipes()
    else:
        df = load_cuisines()

# Astuce PyGWalker dans Streamlit: définir use_env="streamlit" (ou laisser par défaut car pygwalker gère bien Streamlit maintenant)
pyg_html = pyg.to_html(df)
st.components.v1.html(pyg_html, height=800, scrolling=True)
