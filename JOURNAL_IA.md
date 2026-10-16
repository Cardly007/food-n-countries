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
