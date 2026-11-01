# Food & Countries — Allrecipes reflète-t-elle la diversité culinaire mondiale ?

Projet M2 MIAGE Dauphine — Visualisation de données & Analyse critique
assistée par IA. Dataset : [TidyTuesday 2025-09-16](https://github.com/rfordatascience/tidytuesday/tree/main/data/2025/2025-09-16)
(Allrecipes, `all_recipes.csv` 14 426 recettes, `cuisines.csv` 2 218 recettes
par pays d'origine).

## Installation

```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sous Windows
pip install -r requirements.txt
```

## Lancer l'appli

Deux scripts de préparation (à relancer seulement si les CSV changent), puis
Streamlit :

```bash
python data_processing/build_processed_data.py   # tables de base (overlap_stats...)
python data_processing/build_diversity_data.py   # refonte : axes 1 à 4 + contrôles
streamlit run app.py
```

`build_diversity_data.py` affiche un tableau « valeur calculée / valeur de
contrôle » (copie dans `docs/controles_pipeline.txt`).

## Problématique

**Allrecipes reflète-t-elle la diversité culinaire mondiale ?** Destinataire :
responsable éditorial d'une plateforme de recettes ; décision : quelles
cuisines ajouter ou mettre en avant. Quatre questions, une vue chacune :

| Page | Question | Graphique |
|---|---|---|
| 1. Couverture | Le catalogue couvre-t-il le monde ? | carte présent/absent + flèches par continent |
| 2. Ingrédients | Les cuisines sont-elles différentes dans l'assiette ? | heatmap cuisine × ingrédient |
| 3. Attention | Quelles cuisines le public suit-il ? | barres horizontales triées |
| 4. Facettes | Chaque cuisine est-elle montrée par des plats variés ? | barres empilées à 100 % |

## Structure du projet

```
data/
  csv/                     -> CSV bruts (all_recipes.csv, cuisines.csv)
  reference/               -> population par continent, validation manuelle du type de plat
  processed/               -> parquets générés par les deux pipelines
data_processing/
  build_processed_data.py  -> pipeline initial (inchangé)
  build_diversity_data.py  -> pipeline de la refonte (T1 à T5)
src/
  theme.py                 -> socle visuel : palettes, apply_theme, chart_title, kpi
  country_mapping.py       -> catégories -> ISO-3, continents, libellés français
  ingredients.py           -> détection d'ingrédients (vocabulaire corrigé des pluriels)
  dish_type.py             -> type de plat par mots-clés du titre (heuristique mesurée)
  load_data.py             -> chargement (cache dépendant de la date des fichiers)
app_pages/                 -> Accueil, 1 à 4, Méthodologie ; _archive/ = anciennes pages
docs/captures_avant|apres/ -> captures de la version initiale et finale
JOURNAL_IA.md              -> journal de bord : audit critique de l'IA
```

Voir `JOURNAL_IA.md` pour les décisions, et la page Méthodologie de
l'application pour les limites.
