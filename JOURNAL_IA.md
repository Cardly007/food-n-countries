# Journal de bord — audit critique de l'IA

Projet : « Allrecipes reflète-t-elle la diversité culinaire mondiale ? »
(M2 MIAGE Dauphine, Visualisation de données, Séances 1 à 6).

Ce journal documente, graphique par graphique, la proposition brute de l'IA,
sa critique au regard du cours, les alternatives écartées et la version
retenue. Captures de la version initiale : `docs/captures_avant/` ; version
finale : `docs/captures_apres/`. Tableau des valeurs de contrôle :
`docs/controles_pipeline.txt` (sortie de `data_processing/build_diversity_data.py`).

> Note de transparence : la refonte (code, calculs, validation manuelle du
> type de plat, rédaction de ce journal) a été réalisée par un assistant IA
> (Claude Code) à partir d'un brief de l'équipe. Les verdicts « à la main » de
> `data/reference/validation_type_plat.csv` ont donc été posés par l'IA :
> **l'équipe doit les relire** avant la soutenance (le fichier est fait pour
> ça : une ligne par recette, prédiction, verdict, commentaire).

---

## 1. Historique des décisions (matière pour l'oral)

### 1.1 Pivot de problématique

Hypothèse initiale : « les plateformes uniformisent les cuisines du monde sur
un profil nutritionnel riche, que les notes récompenseraient ». Elle a été
testée et **en partie infirmée** (recalcul sur `cuisines.csv`, 45 cuisines
d'au moins 15 recettes, η² = part de variance expliquée) :

| Variable | η² pays | η² type de plat (heuristique) |
|---|---|---|
| Calories | 0,063 | 0,115 |
| Lipides | 0,058 | 0,079 |
| Glucides | 0,045 | 0,049 |
| Protéines | 0,117 | 0,234 |

- Le pays n'explique que 5 à 12 % des différences nutritionnelles (le brief
  annonçait 2 à 8 % ; l'écart vient du périmètre — 45 cuisines — et des
  protéines). Avec 45 groupes, environ 2 % sont attendus par simple hasard.
- Le type de plat pèse jusqu'à deux fois plus (calories, protéines), autant
  pour les glucides.
- Corrélation note × richesse quasi nulle sur `all_recipes.csv` : ρ de
  Spearman = 0,04 (calories), 0,07 (lipides), −0,01 (glucides) ; |ρ| < 0,1
  aussi en ne gardant que les recettes à 10 avis ou plus.

Conclusion : la nutrition dit surtout « dessert ou plat », pas « quel pays ».
La question a été reformulée autour de la **représentation** : quelles
cuisines le catalogue propose, avec quel contenu, quelle attention et sous
quelles facettes. Destinataire : un responsable éditorial ; décision :
quelles cuisines ajouter ou mettre en avant.

### 1.2 Graphiques écartés et pourquoi

- **Boxplots par pays** (ancienne page 2) : illisibles pour un non-expert,
  sans appui dans les Séances 4 à 6, et ils comparent surtout des mélanges
  desserts/plats différents.
- **Barres groupées 8 pays × 11 ingrédients** (ancienne page 1) : 8 couleurs
  catégorielles simultanées (au-delà des ~6 recommandées, Séance 2), lecture
  croisée impossible ; à 40 × 15 ce serait pire. Remplacées par une heatmap.
- **Carte en dégradé du nombre de recettes** (ancienne page 1) : le dégradé
  reflète le plafond de collecte, pas la place des cuisines (artefact).
  Remplacée par une carte à deux états.
- **Camembert / treemap des avis** (proposition IA courante) : les avis par
  recette ne forment pas un tout (Séance 5). Barres triées à la place.
- **Nuages de points note × calories avec droite OLS** (ancienne page 3) :
  ρ ≈ 0, la droite suggère une relation qui n'existe pas.
- **PyGWalker** (ancienne page 5) : outil d'exploration libre sans question
  ni destinataire ; contraire à « une vue = un objectif de lecture ».

### 1.3 Adaptations assumées

- **Diagramme à flèches** : enseigné pour un « avant / après » (Séance 4).
  Ici il relie « poids dans la population mondiale » et « poids dans le
  catalogue ». Même logique de lecture (direction et ampleur d'un écart),
  d'où l'adaptation. Repli prévu (barres groupées horizontales, axe à zéro,
  Séance 6) : non nécessaire, les flèches restent lisibles avec 6 lignes.
- **Heatmap** : enseignée pour un motif d'ensemble ; ici on y écrit aussi la
  valeur dans chaque case (Séance 4, exercice 6) pour éviter un second
  graphique en barres.

### 1.4 Bugs corrigés, validations, vérifications

- **Pluriels des ingrédients** : `src/ingredients.py` cherchait `\begg\b`,
  `\bonion\b`. « eggs » et « onions » n'étaient pas comptés. Médiane de
  l'œuf (45 cuisines) : 12 % → 30 % ; oignon : 35 % → 47 %. Nouveaux motifs
  explicites (`DIVERSITY_INGREDIENTS`), testés sur des cas pièges (eggplant,
  peanut butter, buttermilk, coconut milk, rice vinegar, gingersnap).
- **Type de plat** : heuristique sur le titre (`src/dish_type.py`).
  Échantillon 1 (100 recettes, graine 2024) : 12 erreurs, utilisé pour
  corriger les règles. Échantillon 2 indépendant (100 autres recettes,
  graine 7) tiré **après** les corrections et **non utilisé pour ajuster** :
  9 erreurs (9 %, IC 95 % de Wilson 5–16 %) + 2 cas ambigus (blintzes,
  blinis). 6 des 9 erreurs sont des desserts/pains classés en plats (nisu,
  lefsa, kruschicki, sufganiyot, jemput-jemput, julekake) : la part des
  desserts est sous-estimée. Les règles ont ensuite été **gelées** ; le
  pipeline s'arrête si une prédiction de l'échantillon 2 change (sinon le
  taux affiché ne serait plus valable). Biais résiduel : les règles ont été
  inspirées par des titres du même corpus.
- **Ancienneté et avis** : corrélation de rang ancienneté × avis = −0,05 ;
  91 % des recettes datent de 2022 ou après ; classement des cuisines
  recalculé sur ces seules recettes : ρ = 0,99. Pas d'effet d'ancienneté.
- **Avis manquants** (4,4 %) : note et commentaires manquent aussi → lus
  comme « aucun avis » et comptés 0. Les exclure : ρ = 1,00 avec le
  classement retenu.
- **Accessibilité** : simulation de deutéranopie, protanopie et tritanopie
  (matrices de Machado et al., 2009) sur les captures finales. Carte et
  flèches restent lisibles ; sur l'axe 4, le rose Okabe-Ito et le gris
  `#999999` devenaient presque identiques → gris éclairci en `#CCCCCC`
  (écart volontaire à la palette du brief).
- **Affirmation corrigée** : le brief disait que « la plupart » des
  catégories plafonnent autour de 60–67 recettes ; en fait 22 sur 49. Les
  textes affichés donnent le décompte calculé.

### 1.5 Écarts aux valeurs de contrôle du brief

Toutes les valeurs sont dans `docs/controles_pipeline.txt`. Écarts > 10 % :

| Indicateur | Calculé | Contrôle | Cause |
|---|---|---|---|
| % catégories Afrique / Océanie | 2,33 | 2 | arrondi du contrôle (1/43) ; 0,3 point d'écart |
| Gingembre max (37 pays ≥ 15 recettes) | 64 % | 75 % | le contrôle prenait la cuisine bangladaise (75 %, **12 recettes**, sous le seuil) ; avec le seuil, max = pakistanaise |
| Œuf min | 1,5 % | 2 % | arrondi (0,5 point) |
| Desserts, cuisine autrichienne | 77 % | « > 70 % » | le contrôle est une borne basse : conforme |

Écart proche du seuil : similarité cosinus moyenne entre cuisines 0,74 (contrôle
0,68). Sans le sel, ingrédient quasi universel qui rapproche tous les profils,
on retrouve 0,69 : le test préliminaire ne l'incluait vraisemblablement pas.
Le constat utile est inchangé : la similarité moyenne est la même avec ou sans
desserts (0,74 / 0,75), mais celle de la famille « Europe du Nord… » baisse
(0,90 → 0,84 ; contrôle 0,88 → 0,81).

Population : les valeurs par continent du brief (tableau de la Séance 5) ont
été utilisées telles quelles (`data/reference/population_continent.csv`) ;
**le tableau complet des pays du cours n'était pas disponible** pour les
recalculer. À remplacer si l'équipe le fournit.

### 1.6 Familles de cuisines

Classification hiérarchique (cosinus, liaison moyenne, 5 groupes). Le test
préliminaire du brief annonçait « Asie du Sud et épices (+ Jamaïque,
Indonésie, Malaisie) » : avec le vocabulaire corrigé, Jamaïque, Indonésie et
Malaisie rejoignent l'Asie de l'Est et du Sud-Est (sauce soja, gingembre) ;
l'Asie du Sud se réduit à l'Inde et au Pakistan. Le groupe « pâtissier »
contient aussi le Brésil, le Chili, le Canada, la France, l'Afrique du Sud :
il traduit une forte part de pâtisserie plus qu'une géographie, d'où son nom.

Stabilité (indice de Rand ajusté avec la partition retenue) : liaison
pondérée 1,00 ; 4 groupes 0,93 ; 6 groupes 0,77 ; liaison complète 0,62 ;
sans desserts 0,57. Les blocs asiatiques et méditerranéen sont stables ; le
groupe pâtissier se scinde selon la méthode et dépend des desserts. Les
familles sont donc présentées comme une aide à la lecture (ordre des lignes),
pas comme un résultat.

---

## 2. Audit graphique par graphique

### Accueil — KPI

- État initial / proposition brute : 3 `st.metric` (recettes générales,
  recettes par pays, % de chevauchement). Texte d'accueil annonçant
  « 16 644 recettes » écrit en dur (somme des deux tables, avec doublons).
- Critique : chiffre faux (1 055 doublons) et codé en dur ; le % de
  chevauchement n'aide pas le destinataire (Séance 1 : cadrage) ; pas de
  bloc « pour qui / pour décider quoi ».
- Alternatives écartées : garder les deux tables en KPI séparés (oblige le
  lecteur à faire la soustraction).
- Version finale : bloc de brief ; 3 KPI au format unique `kpi` (titre,
  valeur, sous-titre) : 15 589 recettes uniques (calculé depuis
  `overlap_stats`, infobulle sur la nature des tables), 49 catégories, avis
  analysés. Parcours en 4 questions, limites calculées.
- Décision : **modifié**.

### Ancienne page 1 — Carte choroplèthe à indicateur variable

- État initial : `px.choropleth` continu, 8 indicateurs au choix, palette
  changeant selon l'indicateur (OrRd ou Blues), légende `n_recipes` brute.
- Critique : le nombre de recettes est un artefact du plafond de collecte ;
  intensité de couleur pour comparer des valeurs proches (Séance 2 : la
  couleur ne sert qu'à un ordre de grandeur) ; nom de colonne brut visible ;
  la palette rouge-orangé suggère un jugement (« trop calorique »).
- Alternatives écartées : bulles proportionnelles (même artefact).
- Version finale : voir « Page 1 — carte présent / absent ».
- Décision : **écarté**.

### Ancienne page 1 — Barres groupées ingrédients × pays

- État initial : 8 pays × 11 ingrédients, une couleur par pays, motifs
  d'ingrédients sans pluriel.
- Critique : 8 couleurs catégorielles (Séance 2) ; tâche « voir un motif
  d'ensemble » mal servie par des barres (Séance 4) ; chiffres faux (bug des
  pluriels) ; seulement 8 pays visibles à la fois.
- Alternatives écartées : petits multiples (45 panneaux, trop long).
- Version finale : heatmap (page 2).
- Décision : **écarté**.

### Ancienne page 2 — Boxplots nutritionnels et barres de dépassement de seuils

- État initial : boxplots calories/lipides/glucides/protéines par pays ;
  barres groupées « % au-dessus du seuil ».
- Critique : public non expert (Séance 4, garde-fous « lisible en 5 s ») ;
  seuils arbitraires ; la question nutritionnelle a été infirmée (§ 1.1).
- Décision : **écarté** (page archivée).

### Ancienne page 3 — Nuages de points note × nutrition, tableau « réconfort »

- État initial : 2 nuages avec droite OLS, ρ affiché ; tableau brut avec
  noms de colonnes (`has_comfort_ingredient`, `mean`, `count`).
- Critique : ρ ≈ 0 ; la droite induit une lecture causale ; colonnes brutes.
- Décision : **écarté** (page archivée).

### Ancienne page 4 — Alternatives saines (barres verticales)

- État initial : barres verticales « % de recettes saines et bien notées »
  par pays, noms de pays en abscisse inclinés.
- Critique : critère composite arbitraire ; barres verticales avec 40
  étiquettes longues (Séance 6 : préférer l'horizontal) ; pas d'effectif.
- Décision : **écarté** (page archivée).

### Ancienne page 5 — PyGWalker

- Critique : pas de question ni de destinataire ; dépendance lourde.
- Décision : **écarté** (page archivée, `pygwalker` retiré des dépendances).

### Page 1 — Carte présent / absent

- Proposition brute : choroplèthe continue du nombre de recettes.
- Critique : cf. ancienne carte (artefact du plafond, Séance 2).
- Alternatives écartées : dégradé ; carte par continent (masque les pays).
- Version finale : couleur **discrète à deux états** (orange = cuisine
  proposée, gris clair = aucune), 43 pays (41 catégories « pays » + Australie
  et Nouvelle-Zélande), sans légende (le sous-titre explique). Tâche :
  localiser. Note listant les 7 catégories non cartographiables (calculée).
- Décision : **modifié**.

### Page 1 — Diagramme à flèches par continent

- Proposition brute : aucune (nouveau graphique) ; une IA proposerait
  typiquement un camembert des recettes par continent.
- Critique : le camembert compare mal deux distributions (Séance 5) et
  compterait des recettes (plafond).
- Alternatives : barres groupées 2 séries (repli, Séance 6) ; barres
  divergentes de l'écart seul (perd les deux niveaux).
- Version finale : flèche de % population → % catégories, axe 0–100 %,
  triée par écart, couleur divergente bleu/orange selon le sens, étiquette
  de l'écart en points, étiquetage direct « population / catalogue » au lieu
  d'une légende. Pas de couleur par continent (double encodage, Séance 3).
  Adaptation assumée (§ 1.3).
- Décision : **nouveau**.

### Page 2 — Heatmap cuisine × ingrédient

- Proposition brute : barres groupées (ancienne page 1).
- Critique : voir plus haut.
- Alternatives écartées : barres complémentaires (redondantes avec les
  valeurs dans les cases) ; colorbar (redondante, supprimée : data-ink,
  Séance 3) ; tri alphabétique (cache les motifs).
- Version finale : 45 lignes × 17 ingrédients, une teinte (Blues), zmin = 0,
  valeur dans chaque case, effectif dans le libellé, lignes triées par ordre
  du dendrogramme et séparées par famille (nom + 3 ingrédients
  caractéristiques à droite). Filtres : familles (découper la complexité,
  Séance 3) et bascule « sans desserts » (cases masquées « n < 15 » quand il
  reste trop peu de recettes). Cuisines < 15 recettes exclues et nommées.
- Décision : **nouveau**.

### Page 3 — Barres horizontales des avis par recette

- Proposition brute : camembert / treemap des avis par cuisine.
- Critique : pas un tout cohérent (Séance 5) ; comparaison d'angles.
- Alternatives : 41 pays seulement — proposé en option (« Pays seulement »),
  la vue par défaut garde les 45 cuisines car les traditions américaines
  (Sud des États-Unis, cajun, soul food) sont dans le haut du classement,
  ce qui intéresse directement un responsable éditorial.
- Version finale : seule barre horizontale du site, triée, gris + accent
  orange sur les 5 premières, médiane en pointillé, valeurs en étiquettes
  (axe sans graduation, redondant), axe à zéro, effectif et astérisque si
  < 30 recettes. Notes moyennes (4,25–4,73) en annotation seulement :
  elles ne discriminent pas.
- Décision : **nouveau**.

### Page 4 — Barres empilées à 100 % par type de plat

- Proposition brute : barres empilées en valeurs absolues, ordre alphabétique.
- Critique : en absolu, les cuisines (de 15 à 67 recettes) ne sont pas
  comparables ; seule la couche de base se lit avec précision (Séance 6).
- Alternatives écartées : 4 petits multiples (lecture de la composition
  perdue) ; camembert par cuisine (45 camemberts).
- Version finale : 100 %, desserts/pâtisseries/pains en premier segment,
  tri par cette part, valeur écrite dans le segment, effectif `Cuisine (n)`
  et astérisque si n < 30, légende en haut, Okabe-Ito (gris éclairci après
  test daltonisme). Encadré sur l'heuristique et son taux d'erreur mesuré.
  Vraie composition : la somme vaut 100 % (Séance 5).
- Décision : **nouveau**.

---

## 3. Checklist de relecture (section 6 du brief)

| Critère | Carte | Flèches | Heatmap | Barres avis | Empilées 100 % |
|---|---|---|---|---|---|
| Tâche → graphique (S4) | localiser | comparer 2 états | motif | classer | composition |
| Titre = question + sous-titre (S3) | oui | oui | oui | oui | oui |
| Couleur au service de la tâche | 2 états | sens de l'écart | intensité | accent top 5 | 4 groupes |
| Barres à zéro (S3) | — | axe 0–100 | — | oui | 0–100 % |
| Pas de double encodage | oui | oui (pas de couleur par continent) | colorbar retirée | oui | oui |
| Composition = vrai tout (S5) | — | — | — | pas d'empilement | oui |
| ≤ 6 couleurs catégorielles | 1 | 2 | 1 teinte | 2 | 4 |
| Petits effectifs signalés | — | — | n, « n < 15 » | n, * | n, * |
| Daltonisme testé | oui | oui | oui | oui | corrigé |

Aucun nom de colonne brut n'est affiché ; tous les chiffres des textes sont
calculés (`diversity_stats.parquet` et autres fichiers du pipeline).
