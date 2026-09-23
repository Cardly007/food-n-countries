# Food & Countries — Diversité culinaire ou uniformisation nutritionnelle ?

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

Deux étapes : d'abord le pipeline de préparation des données (à relancer
uniquement si les CSV changent), puis Streamlit.

```bash
python data_processing/build_processed_data.py
streamlit run app.py
```

## Structure du projet

```
data/
  csv/                    -> CSV bruts (all_recipes.csv, cuisines.csv)
  processed/               -> généré par le pipeline, ignoré par git idéalement
data_processing/
  build_processed_data.py  -> pipeline : mapping pays, flags ingrédients,
                               seuils nutrition, agrégats par pays
src/
  load_data.py              -> chargement des CSV et des fichiers processed
  country_mapping.py        -> table de correspondance country -> ISO-3
                                (et documentation des catégories non
                                cartographiables)
  ingredients.py             -> détection d'ingrédients par mot-clé
  nutrition.py                -> seuils nutritionnels et critères "sain"
app.py                       -> page d'accueil / problématique
pages/
  1_Carte.py                 -> Axe 1 : diversité géographique
  2_Profil_Nutritionnel.py   -> Axe 2 : profil diététique mondialisé
  3_Notes_vs_Nutrition.py    -> Axe 3 : biais d'évaluation
  4_Alternatives_Saines.py   -> Axe 4 : alternatives saines
  5_Explorer_BI.py            -> iframe d'un dashboard BI externe (à publier)
  6_Methodologie.py            -> limites du dataset, pour le journal de bord
```

## Points méthodologiques à connaître avant de toucher au code

Voir en détail `pages/6_Methodologie.py` (rendu aussi dans l'appli) :

1. `all_recipes.csv` et `cuisines.csv` ne se recoupent qu'à ~48 % (jointure
   sur `url`) — ce ne sont pas des sous-ensembles l'un de l'autre.
2. La colonne `country` de `cuisines.csv` contient 49 valeurs dont 8 ne
   correspondent pas à un pays unique (`Jewish`, `Soul Food`,
   `Scandinavian`...). Ces recettes sont exclues de la carte choroplèthe
   mais gardées dans les autres analyses.
3. Pas de colonne sucre ni catégorie de plat dans le dataset.
4. Le comptage d'ingrédients (`approx_n_items`) est une approximation du
   fait de la structure du champ texte `ingredients`.

## Étape 5 — Tableau de bord BI embarqué

`pages/5_Explorer_BI.py` prévoit un `components.iframe()` prêt à recevoir
l'URL d'embed d'un dashboard Looker Studio / Tableau Public / Metabase.
Publier le dashboard puis coller l'URL dans `EMBED_URL`.

## Prochaines étapes suggérées

- Étape 2 du projet : soumettre le dataset à une IA, comparer sa proposition
  de mapping pays/visualisation à `src/country_mapping.py` — c'est
  volontairement un bon terrain de critique (une IA a de bonnes chances de
  forcer "Jewish" ou "Scandinavian" sur un seul pays).
- Enrichir `STAPLE_KEYWORDS` / `SUGAR_KEYWORDS` / `COMFORT_KEYWORDS` dans
  `src/ingredients.py` : la liste actuelle est un point de départ, pas une
  liste exhaustive.
- Ajouter des tests si le temps le permet (`streamlit.testing.v1.AppTest`
  a été utilisé pour valider ce squelette, voir historique de dev).
