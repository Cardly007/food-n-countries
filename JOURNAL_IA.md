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
