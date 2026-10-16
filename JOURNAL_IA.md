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
