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
