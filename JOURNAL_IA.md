# Journal de l'IA — branche `variante-grand-public`

> Variante B : grand public, intention « sensibiliser ».
> Ce journal consigne, graphique par graphique, les propositions faites avec
> l'assistant IA (Claude Code), leur critique au regard du cours (Séances 1
> à 6) et la décision retenue. Il est destiné à être repris tel quel dans le
> journal de bord.

## Constats préalables (exploration des données, avant toute modification)

Avant de rédiger un seul titre, les chiffres ont été recalculés depuis les
parquets de `data/processed/` pour vérifier ce que les données soutiennent
réellement. Trois constats ont orienté la suite :

1. **Axe 1 — les ingrédients ne sont pas uniformes partout.** Certains
   ingrédients de base (sel, sucre) apparaissent dans des proportions
   voisines d'un pays à l'autre, mais d'autres (beurre, huile d'olive, farine,
   lait) varient fortement. Le titre ne peut donc pas affirmer « tous les pays
   cuisinent la même chose » : il distingue les ingrédients communs de ceux
   qui différencient (calcul détaillé plus bas).
2. **Axe 2 — les calories médianes par pays sont proches de la médiane
   globale** pour la grande majorité des pays : c'est l'argument le plus
   solide en faveur du message « les profils se ressemblent ».
3. **Axe 3 — le lien entre richesse et note est très faible** (|ρ| de
   Spearman inférieur à 0,1 sur les deux tables). Le fil prévu dans le brief
   (« les notes semblent récompenser les recettes riches ») **n'est pas
   soutenu par les données** : conformément à la règle 1.1, le titre est
   choisi par `build_insight_title_axe3` et dit « lien très faible ».
   Point à valider avec le propriétaire du projet (voir fin du journal).

## Socle technique

### Transverse — gabarit Plotly (`src/theme.py`)
- État initial : chaque page utilisait le gabarit Plotly par défaut (fond
  gris, grille marquée, couleurs attribuées automatiquement, palette
  `OrRd` / rouge pour certaines métriques).
- Critique : le fond gris et la grille dense réduisent le data-ink ratio
  (Séance 3) ; les couleurs automatiques changent d'une page à l'autre pour
  un même pays (cohérence, Séance 3) ; les palettes rouge/vert par défaut
  ne sont pas sûres pour les daltoniens (Séance 2).
- Alternative(s) envisagée(s) et écartée(s) : un `pio.templates.default`
  global a été envisagé, écarté car il agit de façon implicite ; une
  fonction appelée explicitement sur chaque figure rend le choix visible
  dans le code et vérifiable à la relecture.
- Version finale et justification : `apply_theme(fig, ...)` appelé sur
  chaque figure (fond blanc, pas de cadre, grille absente ou gris très
  clair, marges réduites, légende horizontale en haut) ; palettes Okabe-Ito
  (catégorielle), `Blues` (séquentielle), gris `#BDBDBD` + orange
  `#E69F00` (mise en évidence), vermillon `#D55E00` (alerte, dépassement de
  seuil uniquement).
- Décision : modifié.

### Transverse — couleur fixe par pays
- État initial : couleurs attribuées par Plotly selon l'ordre d'apparition.
- Critique : un même pays changeait de couleur selon la page et la
  sélection (Séance 3, « standardiser les codes visuels »).
- Alternative(s) envisagée(s) et écartée(s) : attribuer une couleur aux 41
  pays, écarté (bien au-delà de ~6 couleurs distinguables, Séance 2).
- Version finale et justification : `COUNTRY_COLORS` donne une couleur
  Okabe-Ito fixe à cinq cuisines emblématiques (Italie, Chine, Inde, France,
  Japon) ; tous les autres pays sont en gris. L'orange n'est attribué à
  aucun pays : il reste réservé à l'accent (mise en évidence), pour qu'il
  garde un sens unique dans toute l'application.
- Décision : modifié.

### Transverse — KPI et titres
- État initial : `st.metric` avec des formats variables (delta en
  pourcentage sur une page, aide sur une autre, séparateur de milliers
  remplacé à la main).
- Critique : formats incohérents d'une page à l'autre (Séance 3).
- Version finale et justification : `kpi(label, value, help, subtitle)`
  (format unique : titre, valeur, sous-titre) et `chart_title(headline,
  subtitle)` (titre-insight + sous-titre qui explique l'encodage et la
  limite). Formats de nombres centralisés (`fmt_int`, `fmt_pct`, `fmt_num`).
- Décision : modifié.

### Transverse — navigation
- État initial : menu avec une section « Outils » contenant
  `5_Explorer_BI.py` (PyGWalker).
- Critique : la variante grand public impose un ordre de lecture (logique
  narrative et guidée) ; un outil d'exploration libre façon BI s'adresse à
  un public expert et casse le fil.
- Version finale et justification : page retirée du menu (fichier conservé
  hors navigation) ; menu réordonné dans l'ordre du parcours ; chaque page
  affiche « Étape X sur 4 » et se termine par un bouton « Suite → »
  (`src/story.py`). `pygwalker` reste dans `requirements.txt` car
  `5_Explorer_BI.py` l'importe toujours.
- Décision : modifié.

## Page Accueil (`app_pages/0_Accueil.py`)

### Accueil — titre d'accroche (titre-insight)
- État initial : question générale « Les plateformes de recettes reflètent-elles
  la diversité culinaire mondiale ? » et un paragraphe citant « 16 644 recettes »
  écrit en dur.
- Critique : le chiffre écrit en dur additionne deux tables qui se recoupent
  (doublons) ; un titre-question ne transmet pas l'intention « sensibiliser »
  (Séance 1, adéquation destinataire / intention).
- Version finale et justification : `build_home_headline(conv)`.
  - Formule : `conv = nutrient_convergence(recettes mono-pays, "calories")`,
    part des pays (≥ 20 recettes) dont la médiane de calories par portion est
    à ±20 % de la médiane globale.
  - Seuil de bascule : part ≥ 50 % → affirmation « Les cuisines « du monde »
    en ligne se ressemblent plus qu'il n'y paraît » ; sinon → question
    « … se ressemblent-elles autant qu'on le dit ? ».
  - Pourquoi : l'accroche ne doit affirmer le message central que si
    l'indicateur le plus direct (axe 2) le soutient. Valeur actuelle : 21 pays
    sur 34 (62 %) → affirmation.
- Décision : modifié.

### Accueil — KPI
- État initial : 3 `st.metric` (recettes générales, recettes par pays,
  chevauchement en %), sans total dédupliqué.
- Critique : le lecteur grand public additionne spontanément les deux
  premiers chiffres et obtient un total faux ; le « chevauchement » est un
  détail technique hors du message (Séance 1, destinataire).
- Alternative(s) envisagée(s) et écartée(s) : garder les trois chiffres
  techniques avec une note, écarté (trop de détails techniques sur la page
  d'entrée, renvoyés en Méthodologie).
- Version finale et justification : 3 KPI au format unique `kpi` :
  recettes analysées = `n_all_recipes + n_cuisines − n_overlap` (aide qui
  explique les deux tables et le recoupement) ; nombre d'étiquettes
  « cuisine du monde » (sous-titre : combien correspondent à un seul pays) ;
  note moyenne sur les recettes distinctes (dédupliquées par URL). Tous les
  chiffres sont calculés.
- Décision : modifié.

### Accueil — liste des axes
- État initial : liste des quatre axes en texte libre, menu à gauche en
  accès libre.
- Critique : logique narrative et guidée attendue pour cette variante
  (Séance 1) ; le lecteur doit savoir par où commencer.
- Version finale et justification : rappel des quatre étapes du fil (tirées
  de `src/story.py`, source unique) et bouton « Commencer → » vers l'axe 1.
  L'avertissement technique sur la colonne `country` est déplacé en
  Méthodologie (lien en bas de page).
- Décision : modifié.

## Page 1 — Carte & ingrédients (`app_pages/1_Carte.py`)

### Page 1 — message clé (titre-insight)
- Formule : texte composé de deux valeurs calculées (nombre d'étiquettes
  distinctes dans `cuisines`, nombre de pays cartographiables) et du titre
  produit par `build_insight_title_axe1` pour les pays comparés.
- Pourquoi : le fil prévoyait « l'étiquette promet la diversité » ; le
  message pose la question puis donne la réponse **calculée**, qui est
  aujourd'hui « ces ingrédients de base varient nettement d'un pays à
  l'autre ». Ce résultat nuance le fil : la diversité des ingrédients est
  réelle, la convergence apparaît plutôt sur le profil nutritionnel (page 2).

### Page 1 — carte choroplèthe
- État initial : choroplèthe avec menu déroulant de 8 indicateurs, palette
  `OrRd` (rouge) pour certains, `Blues` pour d'autres, noms de colonnes
  bruts dans le titre (`pct_exceeds_calories`…).
- Critique : une carte sert à **localiser** (Séance 4) ; l'utiliser pour
  comparer des pourcentages précis est inadapté (intensité de couleur =
  ordre de grandeur seulement, Séance 2). Palette changeante d'un indicateur
  à l'autre (cohérence, Séance 3). Rouge à éviter (Séance 2).
- Alternative(s) envisagée(s) et écartée(s) : garder le sélecteur
  d'indicateurs, écarté (pas de message unique, lecture non guidée) ; carte
  à symboles proportionnels, écartée (les effectifs sont trop proches les
  uns des autres pour que la taille porte un message).
- Version finale et justification : une seule variable (nombre de
  recettes), échelle séquentielle une teinte (`Blues`) partant de 0,
  **annotation** en orange des 3 pays en tête. Les 456 recettes non
  cartographiables sont signalées dans le sous-titre et détaillées dans un
  expander, avec libellés lisibles (données manquantes visibles, Séance 3).
- Décision : modifié.

### Page 1 — classement des pays (nouveau)
- État initial : inexistant.
- Critique : la carte ne permet pas de comparer précisément les effectifs
  (Séance 2 : position/longueur > couleur).
- Version finale et justification : barres horizontales triées des 15 pays
  les plus représentés, axe à zéro, valeurs affichées en bout de barre,
  gris neutre + orange sur les 3 pays en tête (les mêmes que ceux annotés
  sur la carte : l'accent relie les deux vues).
- Titre-insight : `build_insight_title_axe1_counts`. Formule : rapport
  `max(n_recipes) / médiane(n_recipes)`. Seuil : < 1,5 → « Aucun pays ne
  domine : … en tête, avec X recettes contre Y pour un pays médian » ;
  sinon → « … concentrent l'offre ». Valeur actuelle : 67 / 45 ≈ 1,49.
  Le titre cite les deux effectifs plutôt qu'un adjectif (« à peine plus »,
  envisagé puis écarté car il minimisait un écart de près de 50 %).
- Décision : créé.

### Page 1 — comparatif d'ingrédients
- État initial : barres groupées, 8 pays par défaut (8 couleurs Plotly
  automatiques), 11 ingrédients en anglais, soit 88 barres.
- Critique : bien au-delà de ~6 couleurs (Séance 2) ; couleurs non fixes
  par pays (Séance 3) ; impossible de voir en 5 secondes si les pays se
  ressemblent (Séance 4) ; libellés en anglais.
- Alternative(s) envisagée(s) et écartée(s) : heatmap pays × ingrédient
  comme graphique principal (piste du brief), écartée en graphique principal
  car l'intensité de couleur ne donne qu'un ordre de grandeur (Séance 2) ;
  **conservée comme vue d'ensemble** dans « Aller plus loin » (12 pays,
  échelle `Blues` éclaircie pour garder le texte lisible, valeurs écrites
  dans les cases).
- Version finale et justification : diagramme en points (« dot plot »), une
  ligne par ingrédient, un point par pays (4 cuisines emblématiques par
  défaut : Italie, Chine, Inde, France, couleurs fixes), trait gris entre le
  minimum et le maximum. La **position** porte la comparaison ; la longueur
  du trait gris montre directement l'écart entre pays. Ingrédients triés du
  plus homogène au plus variable ; axe 0–100 %. Sélecteur limité aux 5
  cuisines à couleur fixe (cohérence des couleurs).
- Titre-insight : `build_insight_title_axe1`. Formule : pour chaque
  ingrédient, `écart = max − min` de la part de recettes qui le contiennent,
  entre les pays comparés. Seuils : « commun » si écart ≤ 25 points et
  fréquence moyenne ≥ 20 % ; « distinctif » si écart ≥ 40 points. Bascule :
  au moins la moitié des ingrédients communs → « Les mêmes ingrédients de
  base reviennent d'un pays à l'autre » ; communs et distinctifs → « X et Y
  reviennent partout ; Z distingue davantage les pays » ; aucun commun →
  « Ces ingrédients de base varient nettement d'un pays à l'autre ».
  Sous-titre : ingrédients à l'écart le plus faible et le plus fort, chiffrés.
  Valeur actuelle : aucun ingrédient commun (le sucre, à 29 points, est
  juste au-dessus du seuil), d'où la formulation « varient nettement ».
  Les seuils sont des valeurs rondes fixées a priori et **n'ont pas été
  ajustés** pour obtenir le message attendu.
- Décision : modifié.

### Transverse — couleur primaire Streamlit
- Constat à la relecture visuelle : les puces du sélecteur de pays
  apparaissaient en rouge (couleur primaire par défaut de Streamlit).
- Version finale : `.streamlit/config.toml` fixe la couleur primaire au bleu
  Okabe-Ito `#0072B2`.
- Décision : modifié.

## Page 2 — Profil nutritionnel (`app_pages/2_Profil_Nutritionnel.py`)

### Page 2 — boîtes à moustaches par pays (graphique principal)
- État initial : deux onglets ; boîtes à moustaches de 15 pays par défaut
  (curseur jusqu'à 40), une couleur Plotly par défaut, variable choisie par
  boutons radio avec noms bruts (`calories`, `fat`…), sans repère commun.
- Critique : sans ligne de référence, l'œil doit comparer 15 boîtes deux à
  deux : le message (convergence) n'est pas lisible en 5 secondes
  (Séance 4) ; noms de colonnes bruts (Séance 3) ; deux onglets = deux
  messages concurrents.
- Alternative(s) envisagée(s) et écartée(s) : barres des médianes par pays,
  écartées car elles masquent la dispersion (comparer des distributions,
  Séance 4) ; violons, écartés (moins familiers pour le grand public) ;
  boîtes colorées par pays, écartées (double encodage avec l'axe X, et 8
  couleurs dépassent ~6 catégories).
- Version finale et justification : 8 pays les plus représentés, boîtes
  grises, **ligne de référence orange = médiane globale** (l'accent porte le
  message du titre), axe partant de 0, points extrêmes masqués et axe
  borné aux moustaches (échelle explicite), annotation de lecture sous le
  graphique, nombre de valeurs manquantes indiqué dans le sous-titre.
  Variable et nombre de pays réglables dans « Aller plus loin ».
- Titre-insight : `build_insight_title_axe2`. Formule : sur les pays d'au
  moins 20 recettes, part des pays dont la médiane (calories par défaut) est
  à ±20 % de la médiane globale de toutes les recettes mono-pays. Seuils :
  ≥ 75 % → « Des profils très proches : k pays sur n… » ; ≥ 50 % → « La
  plupart des pays (k sur n)… » ; sinon → « Des profils contrastés : seuls k
  pays sur n… ». Sous-titre : pays le plus éloigné (écart relatif) et limite
  « sans distinction desserts / plats ». Valeurs actuelles : calories 21/34
  (62 %), lipides 24/34, glucides 21/34 → « la plupart » ; protéines 9/34 →
  « profils contrastés » (le titre bascule bien quand la donnée ne soutient
  pas le message).
- Message clé : `build_key_message_axe2` ajoute « Les recettes changent
  d'étiquette, beaucoup moins de profil » **seulement** si la part ≥ 50 % ;
  sinon une phrase qui reconnaît un profil distinct.
- Décision : modifié.

### Page 2 — dépassement des seuils (graphique secondaire)
- État initial : onglet dédié, barres verticales groupées
  (`pct_exceeds_calories`, `pct_exceeds_fat`), légende « variable » brute.
- Critique : libellés bruts (Séance 3) ; deux séries groupées pour un
  message secondaire ; noms de pays verticaux difficiles à lire.
- Version finale et justification : déplacé dans « Aller plus loin » ; un
  seuil à la fois (radio), barres horizontales triées décroissantes, axe à
  0, valeurs affichées, trait pointillé = moyenne de l'ensemble ; couleur
  d'alerte (vermillon) **uniquement** pour les pays au-dessus de la moyenne,
  gris sinon (alerte avec parcimonie, Séance 2).
- Titre-insight : `build_insight_title_axe2_thresholds` : « Recettes au-delà
  de [seuil] : de [min] ([pays]) à [max] ([pays]) », sous-titre « k pays sur
  n au-dessus de la moyenne (x %) ». Valeurs calculées, seuils lus dans
  `src/nutrition.py`.
- Décision : modifié.

### Page 2 — avertissement « pas de colonne catégorie »
- État initial : `st.warning` en bas de page, avec nom de colonne brut.
- Version finale : encadré `st.info` juste sous le graphique principal,
  reformulé sans jargon.
- Décision : modifié.
