"""
Parcours guidé (variante grand public) : ordre de lecture imposé par l'auteur.

Chaque page d'axe affiche son étape dans le fil narratif, un message clé
calculé en haut, et se termine par un bouton « Suite → » vers la page
suivante.
"""

import streamlit as st

# Fil narratif : (fichier de la page, phrase du fil). L'ordre de la liste est
# l'ordre de lecture.
STEPS = [
    ("app_pages/1_Carte.py", "L'étiquette promet la diversité…"),
    ("app_pages/2_Profil_Nutritionnel.py", "… mais les profils nutritionnels se ressemblent-ils ?"),
    ("app_pages/3_Notes_vs_Nutrition.py", "… et la communauté note-t-elle mieux les recettes riches ?"),
    ("app_pages/4_Alternatives_Saines.py", "Bonne nouvelle : des alternatives existent"),
]
HOME_PAGE = "app_pages/0_Accueil.py"
METHODO_PAGE = "app_pages/6_Methodologie.py"


def step_header(step: int) -> None:
    """Rappelle en une ligne l'étape du fil (« Étape 2 sur 4 »)."""
    _, phrase = STEPS[step - 1]
    st.caption(f"Étape {step} sur {len(STEPS)} · {phrase}")


def key_message(text: str) -> None:
    """Message clé de la page, en haut, calculé depuis les données."""
    st.markdown(
        f"<div style='border-left:4px solid #E69F00;padding:0.4rem 0.9rem;"
        f"margin:0.3rem 0 1rem 0;font-size:1.1rem'>{text}</div>",
        unsafe_allow_html=True,
    )


def next_button(step: int) -> None:
    """Bouton « Suite → » vers l'étape suivante (ou la méthodologie en fin de parcours)."""
    st.divider()
    if step < len(STEPS):
        target, phrase = STEPS[step]
        st.page_link(target, label=f"Suite → {phrase}", icon=":material/arrow_forward:")
    else:
        st.page_link(METHODO_PAGE, label="Suite → Comment ces chiffres ont été calculés",
                     icon=":material/arrow_forward:")
