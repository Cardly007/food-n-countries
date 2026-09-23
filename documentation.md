# Documentation de l'Application "Diversité vs Uniformisation Culinaire"

Ce document décrit l'architecture de l'application Streamlit et le rôle de chacune de ses pages. L'objectif global de l'application est d'analyser des milliers de recettes (issues d'Allrecipes) pour questionner la tension entre la diversité géographique affichée et l'uniformisation nutritionnelle réelle.

## Point d'entrée : `app.py`
Le fichier `app.py` à la racine est le chef d'orchestre de l'application. Il utilise la nouvelle API de navigation de Streamlit (`st.navigation` et `st.Page`) pour définir la barre latérale, le menu, les icônes (Material Design) et lier chaque page au script correspondant situé dans le dossier `app_pages/`.

## Le dossier `app_pages/`

### `0_Accueil.py` (Accueil)
**Rôle :** Introduire le contexte du projet.
* Affiche la problématique globale.
* Présente quelques indicateurs clés (KPIs) comme le volume de recettes analysées et le taux de chevauchement entre les recettes classées par pays et le corpus général.
* Résume les quatre grands axes d'analyse de l'application.

### `1_Carte.py` (Axe 1 : L'illusion de la diversité géographique)
**Rôle :** Analyser la provenance des recettes et leurs bases d'ingrédients.
* **Carte Choroplèthe Interactive :** Permet de visualiser différentes métriques (nombre de recettes, calories médianes, note moyenne) réparties par pays.
* **Comparaison des ingrédients de base :** Un graphique interactif permettant de comparer la fréquence d'utilisation d'ingrédients standards (sucre, beurre, farine) entre différents pays sélectionnés, afin de repérer une éventuelle standardisation mondiale de la préparation.

### `2_Profil_Nutritionnel.py` (Axe 2 : Le profil diététique mondialisé)
**Rôle :** Comparer la qualité diététique des recettes selon leur pays d'origine.
* **Boîtes à moustaches (Boxplots) :** Affiche la dispersion des valeurs nutritionnelles (calories, lipides, glucides, protéines) par pays. 
* **Dépassement de seuils :** Un graphique en barres montrant la proportion de recettes dépassant les seuils recommandés en lipides ou en calories pour chaque pays.

### `3_Notes_vs_Nutrition.py` (Axe 3 : Le biais d'évaluation de la communauté)
**Rôle :** Vérifier l'hypothèse de la "prime à la malbouffe".
* **Nuages de points (Scatter plots) :** Croise la note moyenne (rating) avec la densité calorique ou en glucides, et calcule la corrélation statistique (Spearman).
* **Analyse des "ingrédients réconforts" :** Montre via un tableau si la présence d'ingrédients très riches (fromage, bacon, crème...) impacte positivement la note donnée par les internautes.

### `4_Alternatives_Saines.py` (Axe 4 : La viabilité des alternatives saines)
**Rôle :** Identifier s'il est possible de concilier "plat très bien noté" et "plat sain".
* **Filtres interactifs dynamiques :** L'utilisateur peut régler ses propres seuils (Calories maximales, Note minimale, etc.).
* **Classement des pays "sains" :** Un graphique met en avant les pays produisant la plus grande proportion d'alternatives saines selon ces critères.
* **Explorateur de données :** Un tableau détaillé listant les recettes répondant aux critères stricts pour prouver leur existence réelle.

### `5_Explorer_BI.py` (Outil d'exploration libre)
**Rôle :** Fournir une liberté totale d'analyse sur le jeu de données.
* **PyGWalker intégré :** Remplace un outil externe (comme Looker ou Tableau) en embarquant une véritable interface de "Business Intelligence" glisser-déposer au sein même de la page Streamlit.
* Permet aux utilisateurs d'explorer librement `all_recipes` ou `cuisines` en créant leurs propres graphiques à la volée.

### `6_Methodologie.py` (Limites et Choix Techniques)
**Rôle :** Assurer la rigueur et l'honnêteté intellectuelle de l'analyse.
* Liste les limites liées au jeu de données (ex: la colonne `country` contient parfois des régions ou catégories ethniques qui ne sont pas des pays).
* Explique les biais possibles (corrélation vs causalité, l'absence d'une colonne spécifiant si un plat est un dessert ou un plat de résistance).
* Détaille les choix faits sur les approximations (comme la méthode de comptage des ingrédients).

---

## Logique de chargement des données
* Le fichier `src/load_data.py` contient les fonctions de chargement.
* Afin de garantir la rapidité et l'interactivité de l'application, les fonctions de lecture des fichiers de données (Parquet/CSV) sont protégées par le décorateur `@st.cache_data`. Ainsi, elles ne sont lues qu'une seule fois et conservées en mémoire pour toute la durée de la session utilisateur.
