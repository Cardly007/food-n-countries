# Journal de l'IA — Variante éditoriale

> Journal d'audit des propositions de l'IA (Claude Code) pour la variante
> « responsable éditorial, intention : éclairer une décision ».
> Chaque entrée suit le gabarit : état initial → critique (principe du cours,
> n° de séance) → alternatives envisagées / écartées → version finale →
> décision. Les choix de graphiques restent **provisoires** tant qu'ils
> n'ont pas été validés par le propriétaire du projet ; chacun est isolé
> dans une fonction `build_*` de sa page pour pouvoir être remplacé.

---

## Socle commun

### Toutes les pages — gabarit Plotly (`src/theme.py`, `apply_theme`)
- État initial : gabarit Plotly par défaut (fond gris clair `plotly`, grille marquée, couleurs attribuées automatiquement, titres et marges hétérogènes d'une page à l'autre).
- Critique : rapport data-ink faible et encre non informative (Séance 3) ; codes visuels non standardisés entre pages (Séance 3).
- Alternative(s) envisagée(s) et écartée(s), pourquoi : `template="simple_white"` de Plotly — écarté car il ajoute des lignes d'axes et des graduations noires (cadre) ; suppression totale de la grille — écartée pour les axes de valeur, où une grille très légère (`#EEEEEE`) aide la lecture précise sans attirer l'œil.
- Version finale et justification : `apply_theme(fig, title, subtitle, height)` appliqué à chaque figure : fond blanc, pas de cadre ni de graduations, grille très légère sur l'axe de valeur seulement (`hide_grid` sur l'axe des catégories), police unique, légende horizontale au-dessus du tracé, marges réduites.
- Décision : modifié.

### Toutes les pages — palettes
- État initial : couleurs par défaut de Plotly ; carte en `OrRd` (rouge) pour certains indicateurs et `Blues` pour d'autres.
- Critique : la palette par défaut de Plotly contient rouge et vert côte à côte, illisibles pour un lecteur deutéranope (Séance 2) ; changer d'échelle séquentielle selon l'indicateur suggère un jugement (rouge = mauvais) sans l'expliquer (Séance 3).
- Alternative(s) envisagée(s) et écartée(s), pourquoi : palette Okabe-Ito complète avec le **jaune `#F0E442`** comme 5e couleur de pays — **écartée après vérification par script** (validateur de palette : contraste 1,3:1 sur fond blanc, hors de la bande de luminosité, barres jaunes quasi invisibles). Proposition de l'IA d'utiliser le vert Okabe-Ito `#009E73` à la place — écartée : le brief interdit d'opposer rouge et vert, et le vermillon est déjà candidat.
- Version finale et justification : catégorielle = bleu `#0072B2`, orange `#E69F00`, bleu ciel `#56B4E9`, rose `#CC79A7`, vermillon `#D55E00` (Okabe-Ito, aucun vert ; validée : séparation daltonisme ΔE ≥ 8,5 sur toutes les paires). Séquentielle = `Blues` partout. Mise en évidence = gris `#BDBDBD` + accent orange. Alerte = vermillon, réservé aux dépassements de seuil. Le validateur signale un contraste < 3:1 pour l'orange, le bleu ciel et le rose : compensé par des légendes, des info-bulles et une vue tableau / heatmap avec valeurs.
- Décision : modifié.

### Toutes les pages — couleur fixe par pays
- État initial : couleur attribuée par Plotly selon l'ordre d'apparition ; un même pays change de couleur quand on modifie la sélection.
- Critique : « standardiser les codes visuels » (Séance 3) ; la couleur doit suivre l'entité, pas son rang.
- Alternative(s) envisagée(s) et écartée(s), pourquoi : une couleur pour chacun des 41 pays — impossible sous la limite de ~6 catégories de couleur (mémoire de travail, Séance 2). « Gris pour tous les autres pays » strictement — écarté pour le comparatif d'ingrédients : deux pays hors dictionnaire sélectionnés ensemble seraient indiscernables.
- Version finale et justification : dictionnaire figé `COUNTRY_COLORS` pour les 5 pays les plus représentés (tri par nombre de recettes, puis alphabétique pour les ex-aequo) ; un pays hors dictionnaire reçoit une couleur encore libre de la palette dans la sélection courante, et les sélections sont limitées à 5 pays. **Point à valider** : la couleur d'un pays hors dictionnaire peut donc varier selon la sélection.
- Décision : modifié.

### Toutes les pages — KPI (`kpi`) et titres (`chart_title`)
- État initial : `st.metric` avec `delta` (« x % du total ») affiché avec une flèche verte.
- Critique : la flèche verte/rouge de `delta` oppose rouge et vert et suggère une évolution (hausse = bien) alors qu'il s'agit d'une part du total (Séances 2 et 3). Titres de pages affirmatifs (« L'illusion de la diversité ») : conclusion imposée, contraire à l'intention « éclairer une décision ».
- Alternative(s) envisagée(s) et écartée(s), pourquoi : garder `st.metric` sans `delta` — écarté car il n'offre pas de sous-titre, alors que le brief demande titre + valeur + sous-titre.
- Version finale et justification : `kpi(label, value, help, subtitle)` = carte unique (titre, valeur, sous-titre neutre) ; `chart_title(question, subtitle)` = question + sous-titre qui explique l'encodage.
- Décision : modifié.

### Toutes les pages — libellés (`src/labels.py`)
- État initial : noms de colonnes bruts à l'écran (`pct_exceeds_calories`, `variable`, `has_comfort_ingredient`, `calories`…), étiquettes de pays en anglais (« Brazilian »), ingrédients en anglais.
- Critique : guider l'utilisateur, aucune variable technique visible (Séance 3).
- Alternative(s) envisagée(s) et écartée(s), pourquoi : renommer les colonnes dans le pipeline — écarté, le brief interdit de modifier `data_processing/`.
- Version finale et justification : couche d'affichage seule (`COLUMN_LABELS`, `COUNTRY_LABELS`, `INGREDIENT_LABELS`, `MAP_TYPE_LABELS`), unités incluses (« kcal / portion », « g / portion »).
- Décision : modifié.

### Indicateurs recalculés (`src/indicators.py`)
- État initial : `by_country.parquet` calcule `pct_exceeds_*` avec les valeurs manquantes comptées comme « sous le seuil » ; pas de part au-dessus du seuil de glucides ; corrélation de Spearman calculée sans retirer les valeurs manquantes.
- Critique : données manquantes lissées au lieu d'être visibles (Séance 3).
- Alternative(s) envisagée(s) et écartée(s), pourquoi : corriger le pipeline — interdit par le brief, signalé ici.
- Version finale et justification : `country_summary()` recalcule les parts sur les seules recettes renseignées et garde le nombre de valeurs manquantes ; `spearman()` retire les lignes incomplètes et renvoie l'effectif réel.
- Décision : modifié (à reporter dans le pipeline si le propriétaire le souhaite).

---

## Corrections transverses

### Navigation — page « Explorer (BI) » (PyGWalker)
- État initial : section « Outils » du menu latéral avec un explorateur PyGWalker sur les tables brutes.
- Critique : l'outil affiche les noms de colonnes bruts et laisse construire n'importe quel graphique (camemberts, double axe…) sans garde-fou, hors du fil diagnostic → test → hypothèse → décision (Séances 3 et 4).
- Alternative(s) envisagée(s) et écartée(s), pourquoi : supprimer le fichier — écarté (le brief demande de le garder) ; le laisser dans un expander de la Méthodologie — écarté, l'import de PyGWalker alourdit le chargement de la page.
- Version finale et justification : page retirée de `app.py`, fichier `app_pages/5_Explorer_BI.py` conservé hors navigation. `pygwalker` reste dans `requirements.txt` car ce fichier l'importe toujours.
- Décision : écarté de la navigation.

---

## Accueil

### Accueil — KPI « total de recettes »
- État initial : texte « 16 644 recettes » codé en dur + 3 `st.metric` (recettes générales, recettes par pays, chevauchement en %).
- Critique : 16 644 = 14 426 + 2 218 compte deux fois les recettes présentes dans les deux tables ; chiffre codé en dur, non recalculé si les données changent ; le chevauchement en % est un indicateur technique peu utile au destinataire (Séance 3, guider l'utilisateur).
- Alternative(s) envisagée(s) et écartée(s), pourquoi : afficher les deux tables séparément sans total — écarté, le destinataire veut l'ordre de grandeur du corpus ; un diagramme de Venn du chevauchement — écarté, surface peu lisible pour comparer et trop d'encre pour 3 nombres (Séance 2).
- Version finale et justification : 3 KPI au format `kpi` : recettes uniques (total dédupliqué = générales + par pays − communes, calculé depuis `overlap_stats`, avec le détail du calcul en sous-titre et la nature des deux tables en aide), recettes étiquetées par pays, étiquettes de cuisine (dont pays uniques, calculé depuis `country_mapping`).
- Décision : modifié.

### Accueil — brief décisionnel et parcours
- État initial : titre-question générique, liste des 4 axes avec des intitulés affirmatifs (« L'illusion de la diversité géographique »).
- Critique : intitulés qui imposent une conclusion avant l'analyse ; destinataire et décision non explicités (cadrage du sujet, Séance 1).
- Alternative(s) envisagée(s) et écartée(s), pourquoi : schéma graphique du parcours — écarté, 4 cartes texte suffisent et restent cliquables.
- Version finale et justification : bloc « À qui / Pour décider quoi / Question centrale », puis 4 cartes « diagnostic → test → hypothèse → décision » avec la question de chaque axe et un lien vers la page. Les entrées du menu latéral reprennent ces 4 étapes.
- Décision : modifié.

---

## Axe 1 — Diagnostic (`app_pages/1_Carte.py`)

### Axe 1 — carte choroplèthe (`build_map`)
- État initial : choroplèthe avec échelle `OrRd` (rouge) pour les indicateurs « négatifs » et `Blues` pour les autres ; titre = nom de l'indicateur ; seule vue des données par pays.
- Critique : changer de teinte selon l'indicateur impose un jugement (rouge = mauvais) et casse la cohérence (Séance 3) ; une intensité de couleur ne permet qu'une comparaison approximative, pas un classement (Séance 2) ; les pays sans donnée ne sont pas signalés comme tels.
- Alternative(s) envisagée(s) et écartée(s), pourquoi : carte à symboles proportionnels (cercles) — écartée, la surface est encore moins précise que la couleur (Séance 2) ; échelle divergente centrée sur la moyenne — écartée, aucun point milieu n'a de sens métier pour la plupart des indicateurs ; supprimer la carte — écarté, la tâche « localiser » reste pertinente pour le diagnostic.
- Version finale et justification : carte conservée pour **localiser**, échelle séquentielle unique `Blues`, sans cadre ni côtes, pays sans recette en gris clair (annoncé en sous-titre), titre-question, seuils rappelés en sous-titre pour les indicateurs de dépassement. Note : la carte télécharge le fond de carte depuis le CDN de Plotly ; elle n'a pas pu être affichée dans l'environnement de test (réseau bloqué), le reste de la page oui.
- Décision : modifié.

### Axe 1 — classement des pays (`build_ranking`, nouveau)
- État initial : inexistant (seul le texte « N recettes sur 41 pays »).
- Critique : pour comparer précisément, il faut encoder par position / longueur sur une échelle commune (Séances 2 et 4).
- Alternative(s) envisagée(s) et écartée(s), pourquoi : barres verticales — écartées, 41 libellés de pays deviendraient illisibles en abscisse ; barres pour la note moyenne — écartées, une barre part de 0 et écraserait des écarts de quelques dixièmes, alors qu'un axe tronqué est interdit pour des barres (Séance 3).
- Version finale et justification : barres horizontales triées (plus élevé en haut), axe à 0, une seule couleur (bleu) car la couleur ne porte aucune variable ; pour la note moyenne, **points** sur un axe zoomé dont la plage est écrite dans le titre de l'axe. Les pays sans valeur sont comptés sous le graphique.
- Décision : créé.

### Axe 1 — comparatif des ingrédients de base (`build_staples_bars`)
- État initial : barres groupées verticales, 8 pays par défaut, couleurs Plotly par défaut, nom de colonne `pct_recipes`, ingrédients en anglais dans l'ordre de la liste.
- Critique : 8 couleurs dépassent la limite de ~6 catégories de couleur (mémoire de travail, Séance 2) ; couleur d'un pays variable selon la sélection (Séance 3) ; ordre des ingrédients arbitraire.
- Alternative(s) envisagée(s) et écartée(s), pourquoi : petits multiples (un graphique par pays) — écartés, la comparaison entre pays pour un même ingrédient demanderait des allers-retours ; barres empilées — écartées, les parts ne forment pas un total (une recette contient plusieurs ingrédients) (Séance 5).
- Version finale et justification : barres groupées, **5 pays au plus** (sélection bloquée à 5), couleurs fixes par pays, ingrédients traduits et triés par fréquence moyenne décroissante, axe en % à partir de 0, fin liseré blanc entre barres adjacentes.
- Décision : modifié.

### Axe 1 — heatmap pays × ingrédient (`build_staples_heatmap`, nouveau)
- État initial : inexistant.
- Critique : les barres groupées ne passent pas à l'échelle au-delà de 5 pays ; pour repérer des **motifs** sur beaucoup de pays, l'intensité de couleur suffit (ordre de grandeur, Séance 2).
- Alternative(s) envisagée(s) et écartée(s), pourquoi : heatmap seule, sans barres — écartée, la couleur ne permet pas une comparaison précise entre 2 ou 3 pays ; échelle de couleur différente des autres graphiques — écartée (cohérence, Séance 3).
- Version finale et justification : sélecteur « Barres groupées / Heatmap » ; heatmap en `Blues` (0 à 100 %), valeurs écrites dans chaque case (l'information ne repose pas sur la couleur seule), option « tous les pays » réservée à la heatmap, pays triés par nombre de recettes.
- Décision : créé.

### Axe 1 — recettes non cartographiables (expander)
- État initial : tableau brut (`country`, `map_type`, `n_recipes`).
- Critique : noms de colonnes et codes techniques visibles (Séance 3).
- Version finale et justification : expander conservé, colonnes et types traduits, mention que ces recettes restent proposées comme candidates à l'axe 4.
- Alternative(s) envisagée(s) et écartée(s), pourquoi : aucune.
- Décision : modifié.

### Toutes les pages — couleur des widgets Streamlit (`.streamlit/config.toml`)
- État initial : thème Streamlit par défaut, puces de sélection et boutons en rouge.
- Critique : le rouge des widgets entre en concurrence avec les couleurs des pays (dont le vermillon) et avec la couleur d'alerte (Séance 3).
- Alternative(s) envisagée(s) et écartée(s), pourquoi : CSS injecté — écarté, la configuration de thème suffit et reste maintenable.
- Version finale et justification : couleur primaire = bleu `#0072B2` de la palette.
- Décision : modifié.

---

## Axe 2 — Test de la diversité (`app_pages/2_Profil_Nutritionnel.py`)

### Axe 2 — boîtes à moustaches par pays (`build_boxplots`)
- État initial : boxplots Plotly par défaut, 15 pays par défaut, ordre = nombre de recettes, choix de variable par nom brut (`calories`, `fat`…), aucun repère commun.
- Critique : la tâche est de **comparer des distributions** (Séance 4) : il faut un repère commun pour juger « convergence ou spécificité » ; 15 boîtes rendent la comparaison laborieuse ; ordre non lié à la variable lue ; libellés techniques (Séance 3).
- Alternative(s) envisagée(s) et écartée(s), pourquoi : violons — écartés, la forme de densité est plus difficile à comparer que médiane + quartiles pour un public non statisticien ; nuage de points par pays (strip plot) — écarté, ~65 points par pays se chevauchent ; une couleur par pays — écartée, la position en abscisse identifie déjà le pays (double encodage inutile, et > 6 couleurs).
- Version finale et justification : 8 pays par défaut (curseur conservé, jusqu'aux 41), pays triés par médiane décroissante, une seule couleur, **ligne de référence = médiane de toutes les recettes des 41 pays** annotée, valeurs extrêmes masquées (signalé en sous-titre), axe à partir de 0, consigne de lecture « boîtes alignées sur la ligne = convergence », nombre de recettes sans valeur indiqué.
- Décision : modifié.

### Axe 2 — dépassement de seuils (`build_threshold_bars`)
- État initial : barres verticales groupées (calories et lipides) avec légende `variable` / `pct_exceeds_calories`, tri sur les calories seulement, valeurs manquantes comptées comme « sous le seuil ».
- Critique : noms de colonnes bruts à l'écran (Séance 3) ; deux séries triées sur une seule rendent la seconde illisible ; données manquantes lissées (Séance 3) ; pas de repère pour juger si un pays est « au-dessus ».
- Alternative(s) envisagée(s) et écartée(s), pourquoi : barres groupées bien légendées — écartées, le tri ne peut servir qu'une série ; petits multiples des 3 seuils côte à côte — envisagés, écartés pour garder un seul graphique lisible sur écran étroit ; couleur d'alerte (vermillon) sur les pays au-dessus — écartée, l'alerte doit rester rare et un écart à la moyenne n'est pas un dépassement de norme.
- Version finale et justification : **un graphique par seuil** (sélecteur calories / lipides / glucides, le seuil glucides étant calculé dans `src/indicators.py`), barres horizontales triées par part décroissante, axe en % à partir de 0, ligne de référence = part observée sur l'ensemble des pays, gris neutre + accent orange pour les pays au-dessus de cette part, parts calculées sur les seules recettes renseignées (nombre exclu affiché).
- Décision : modifié.

### Axe 2 — avertissement « pas de catégorie de plat »
- État initial : `st.warning` conservé avec nom de colonne brut (`category`).
- Version finale et justification : avertissement conservé, reformulé sans nom de colonne.
- Critique / alternatives : aucune.
- Décision : conservé.

---

## Axe 3 — Hypothèse sur le levier (`app_pages/3_Notes_vs_Nutrition.py`)

### Axe 3 — nuages de points note × calories et note × glucides (`build_scatter`)
- État initial : deux `px.scatter` sur un échantillon de 3 000 recettes, droite OLS calculée **sur l'échantillon**, légende « n = » égale à toutes les recettes, axes Y indépendants, ρ de Spearman calculé sans retirer les valeurs manquantes, phrase de résultat technique (« ρ = …, p = … »), effectifs codés en dur dans le sélecteur de population (« 14 426 », « 2 218 »).
- Critique : l'échantillon n'est pas annoncé alors que n affiché = population entière (incohérence, Séance 3) ; deux axes Y différents empêchent de comparer les deux graphiques (cohérence, Séance 3) ; quelques recettes à plusieurs milliers de kcal écrasent le nuage ; jargon statistique sans explication (guider l'utilisateur, Séance 3) ; chiffres codés en dur.
- Alternative(s) envisagée(s) et écartée(s), pourquoi : nuage hexagonal (density heatmap) sur toutes les recettes — envisagé (supprime l'échantillonnage), écarté pour l'instant : les notes sont très discrètes (paliers de 0,1) et les hexagones produisent des bandes peu lisibles pour un non-spécialiste ; moyenne de la note par tranche de calories (binning) — bonne alternative, gardée en réserve si le propriétaire préfère supprimer l'échantillon ; échelle log en X — écartée, peu intuitive pour le destinataire.
- Version finale et justification : nuage sur un **échantillon de 3 000 recettes annoncé explicitement** (« échantillon de 3 000 recettes sur N ») ; tendance et ρ calculés sur toutes les recettes renseignées ; opacité 0,25 ; **même axe Y zoomé** pour les deux graphiques (point/courbe : troncature admise et écrite dans le titre d'axe) ; axe X limité au 99e centile avec le nombre de recettes non dessinées ; ρ rédigé en une phrase (sens, force, signification, rappel de l'échelle −1/+1, et mise en garde « détectable ≠ important » quand l'effet est quasi nul mais significatif) ; effectifs des populations calculés.
- Décision : modifié.

### Axe 3 — ingrédients « réconfort » et note (`build_comfort_points`)
- État initial : `st.dataframe` brut (`has_comfort_ingredient`, `mean`, `count`).
- Critique : un tableau ne montre pas l'écart ; noms de colonnes bruts (Séance 3).
- Alternative(s) envisagée(s) et écartée(s), pourquoi : deux barres — écartées, des barres doivent partir de 0, ce qui rend invisible un écart de quelques centièmes d'étoile, et les tronquer est interdit (Séance 3) ; boxplots des deux groupes — écartés, les notes très concentrées autour de 4,5 donnent deux boîtes quasi identiques qui ne répondent pas à la question « la moyenne diffère-t-elle ? ».
- Version finale et justification : **graphique en points** (moyenne de chaque groupe) avec intervalle de confiance à 95 %, axe zoomé dont la plage est écrite dans le titre d'axe, valeur et effectif écrits à côté de chaque point, gris = sans / orange = avec (accent sur le groupe testé).
- Décision : modifié.

### Axe 3 — encadré de prudence
- État initial : `st.info` sur le biais « desserts ».
- Version finale et justification : conservé, reformulé sans nom de colonne.
- Critique / alternatives : aucune.
- Décision : conservé.

---

## Axe 4 — Décision (`app_pages/4_Alternatives_Saines.py`)

### Axe 4 — KPI « recettes saines et bien notées »
- État initial : 2 `st.metric` avec `delta` (« x % du total ») affiché en vert avec une flèche.
- Critique : flèche verte = évolution positive, alors qu'il s'agit d'une part du total ; opposition implicite vert / rouge (Séances 2 et 3).
- Alternative(s) envisagée(s) et écartée(s), pourquoi : jauge — écartée, encre décorative pour un seul nombre (Séance 3).
- Version finale et justification : 4 filtres conservés (libellés avec unités) ; 2 KPI au format `kpi` : nombre, part du total en sous-titre, nombre de recettes non évaluables (valeur manquante) en aide.
- Décision : modifié.

### Axe 4 — part de recettes saines par pays (`build_country_bars`)
- État initial : barres verticales colorées uniformément, libellés de pays en abscisse, effectifs seulement au survol.
- Critique : 37 libellés verticaux illisibles ; aucune hiérarchie visuelle alors que la question est « quels pays en tête ? » (Séance 3, la couleur sert la tâche) ; effectifs invisibles alors qu'une part sur 18 recettes n'a pas le poids d'une part sur 65.
- Alternative(s) envisagée(s) et écartée(s), pourquoi : carte choroplèthe — écartée, déjà présente à l'axe 1 et moins précise (Séance 2) ; barres empilées « saines / autres » — écartées, l'empilement complique la lecture de la part ; accent sur les pays au-dessus de la moyenne — écarté ici au profit des N premiers, plus directement actionnable pour une mise en avant éditoriale.
- Version finale et justification : barres horizontales triées, axe à 0, **gris neutre + accent orange sur les 5 premiers pays**, « retenues / total » écrit au bout de chaque barre, seuil de 15 recettes minimum par pays conservé et rappelé (nombre de pays exclus calculé).
- Décision : modifié.

### Axe 4 — tableau des recettes candidates (nouveau, conclusion de la variante)
- État initial : `st.dataframe` brut dans un expander (colonnes `name`, `avg_rating`…), trié par note seulement, URL en texte brut.
- Critique : la partie « décision » était cachée et non actionnable ; noms de colonnes bruts (Séance 3).
- Alternative(s) envisagée(s) et écartée(s), pourquoi : « top 10 » figé en graphique — écarté, le responsable éditorial doit pouvoir filtrer et construire sa propre sélection ; inclure les recettes générales sans pays — écarté, elles ne répondent pas à l'objectif « diversité culinaire ».
- Version finale et justification : tableau visible en conclusion, mêmes seuils que les filtres du haut, tri par note puis nombre d'avis, filtres par pays et par nom, option pour inclure les étiquettes non nationales (Tex-Mex, Soul food…), libellés avec unités, lien cliquable « Ouvrir la recette », export CSV de la sélection.
- Décision : créé.

---

## Méthodologie (`app_pages/6_Methodologie.py`)

### Méthodologie — chiffres et nouvelles sections
- État initial : structure en 6 sections, plusieurs chiffres codés en dur (« 14 426 », « 2 218 », « 8 des 49 valeurs (396 recettes, 18 %) »), noms de colonnes bruts.
- Critique : **le chiffre codé en dur était faux** : le calcul depuis les données donne 456 recettes non cartographiables (21 % des recettes étiquetées), pas 396 (18 %). Exemple concret du risque d'un texte non recalculé (critère d'acceptation : aucun chiffre codé en dur).
- Alternative(s) envisagée(s) et écartée(s), pourquoi : déplacer la méthodologie dans des expanders sur chaque page — écarté, la page sert de matière au journal de bord et doit rester d'un seul tenant.
- Version finale et justification : structure conservée (sections 1 à 6) et complétée : total dédupliqué et son calcul (1), seuils de dépassement et critères « sain et bien noté » lus dans `src/nutrition.py` (5), « détectable ≠ important » (6), **échantillon des nuages de points** (7, taille et quantile lus dans `src/indicators.py`), **valeurs manquantes** avec tableau des effectifs (8). Tous les chiffres sont calculés.
- Décision : modifié.

---

## Propositions de l'IA écartées (synthèse)

| Proposition | Où | Raison de l'écart |
|---|---|---|
| Jaune Okabe-Ito comme 5e couleur de pays | Socle | Contraste 1,3:1 sur fond blanc (vérifié par script) |
| Vert Okabe-Ito pour remplacer le jaune | Socle | Interdit d'opposer rouge (vermillon) et vert |
| `st.metric` avec `delta` pour les parts | Accueil, axe 4 | Flèche verte/rouge = jugement d'évolution hors de propos |
| Diagramme de Venn du chevauchement des tables | Accueil | Surfaces peu comparables, encre excessive pour 3 nombres |
| Carte à symboles proportionnels | Axe 1 | Surface encore moins précise que la couleur |
| Barres pour la note moyenne par pays | Axe 1 | Axe à 0 obligatoire → écarts de dixièmes invisibles ; remplacé par des points |
| Barres empilées des ingrédients | Axe 1 | Les parts ne forment pas un total |
| Violons / strip plot par pays | Axe 2 | Moins lisibles que médiane + quartiles pour le destinataire |
| Couleur par pays dans les boxplots | Axe 2 | Double encodage (position + couleur) et > 6 couleurs |
| Vermillon (alerte) pour les pays au-dessus de la moyenne | Axe 2 | Un écart à la moyenne n'est pas un dépassement de norme |
| Hexbin / density heatmap des notes | Axe 3 | Notes discrètes → bandes peu lisibles (gardé en réserve, comme le binning) |
| Barres tronquées note avec / sans réconfort | Axe 3 | Barres tronquées interdites ; remplacé par des points + IC 95 % |
| Top 10 figé en graphique | Axe 4 | Le destinataire doit filtrer et construire sa sélection |

## Points à valider avec le propriétaire du projet

1. Couleur d'un pays hors des 5 pays du dictionnaire fixe : attribuée parmi les couleurs libres de la sélection (peut varier d'une sélection à l'autre).
2. Nuages de points : garder l'échantillon annoncé, ou passer à une moyenne de note par tranche de calories (sans échantillon).
3. Parts « au-dessus du seuil » recalculées hors valeurs manquantes dans `src/indicators.py` : à reporter dans le pipeline si souhaité (`by_country.parquet` les compte comme « sous le seuil »).
4. Libellés des pays traduits en français (`src/labels.py`) : à relire.
5. Accent orange des axes 2 (pays au-dessus de la part globale) et 4 (5 premiers pays) : règle d'accent différente selon la question, à confirmer.
