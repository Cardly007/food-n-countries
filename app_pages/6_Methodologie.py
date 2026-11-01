import streamlit as st

from src.ingredients import DIVERSITY_INGREDIENTS, INGREDIENT_LABELS
from src.load_data import load_processed, load_stats
from src.theme import fmt_int, fmt_num, fmt_pct

stats = load_stats()
overlap = load_processed("overlap_stats").iloc[0]
catalog = load_processed("cuisine_catalog")
continents = load_processed("continent_summary")
families = load_processed("cuisine_families")
val = load_processed("dish_validation").iloc[0]

st.title("Méthodologie et limites")

st.markdown(
    """
Cette page centralise les choix méthodologiques et leurs limites. Tous les
chiffres sont recalculés depuis les données par
`data_processing/build_diversity_data.py` ; le détail des décisions et de
l'audit de l'IA est dans `JOURNAL_IA.md`.
"""
)

st.subheader("1. Deux tables, pas une seule population de recettes")
st.write(
    f"`all_recipes.csv` contient {fmt_int(overlap.n_all_recipes)} recettes (sans pays), "
    f"`cuisines.csv` en contient {fmt_int(overlap.n_cuisines)} (classées par cuisine). "
    f"Seules {fmt_int(overlap.n_overlap)} recettes "
    f"({fmt_pct(overlap.pct_cuisines_in_all_recipes, 1)} de `cuisines.csv`) existent "
    f"dans les deux (jointure sur l'URL) : **ce ne sont pas des sous-ensembles l'une "
    f"de l'autre**. Total sans doublon : {fmt_int(overlap.n_all_recipes)} + "
    f"{fmt_int(overlap.n_cuisines)} − {fmt_int(overlap.n_overlap)} = "
    f"**{fmt_int(stats['n_recettes_uniques'])} recettes uniques**. Toutes les analyses "
    f"de l'application portent sur `cuisines.csv`, seule table qui indique une cuisine."
)

st.subheader("2. La colonne « pays » n'est pas une liste de pays")
types = catalog["map_type"].value_counts()
st.markdown(
    f"Les {fmt_int(stats['n_categories'])} catégories sont choisies par Allrecipes : "
    f"{fmt_int(types.get('single_country', 0))} pays, "
    f"{fmt_int(types.get('multi_country', 0))} régions multi-pays, "
    f"{fmt_int(types.get('us_regional', 0))} traditions régionales américaines et "
    f"{fmt_int(types.get('non_national', 0))} communautés sans territoire national "
    f"(voir `src/country_mapping.py`). Il n'existe pas de catégorie « américaine » : "
    f"la cuisine des États-Unis n'apparaît qu'à travers ses traditions régionales."
)
TYPE_FR = {"single_country": "Pays", "multi_country": "Région multi-pays",
           "us_regional": "Tradition régionale (États-Unis)",
           "non_national": "Communauté"}
st.dataframe(
    catalog.assign(type=catalog["map_type"].map(TYPE_FR),
                   continent=catalog["continent"].fillna("— (hors continent)"))
    [["cuisine", "country", "type", "continent", "n_recettes"]]
    .sort_values(["type", "cuisine"])
    .rename(columns={"cuisine": "Cuisine", "country": "Libellé Allrecipes",
                     "type": "Nature", "continent": "Continent",
                     "n_recettes": "Recettes"}),
    hide_index=True, width="stretch", height=300,
)

st.subheader("3. Une collecte plafonnée")
st.markdown(
    f"{fmt_int(stats['n_categories_plafond'])} catégories sur "
    f"{fmt_int(stats['n_categories'])} ont entre {fmt_int(stats['seuil_plafond'])} et "
    f"{fmt_int(stats['max_recettes_categorie'])} recettes : la collecte a été "
    f"tronquée. **Le nombre de recettes d'une grande cuisine ne mesure donc pas sa "
    f"place sur le site** ; seules la présence ou l'absence d'une cuisine et les "
    f"petits effectifs sont informatifs. C'est pourquoi la carte de la page 1 est "
    f"à deux états (présent / absent) et non un dégradé du nombre de recettes. "
    f"Les cuisines de moins de {fmt_int(stats['seuil_recettes'])} recettes sont "
    f"exclues des pages 2 à 4 ({fmt_int(stats['n_categories_retenues'])} cuisines "
    f"retenues) ; celles de moins de {fmt_int(stats['seuil_petit_effectif'])} "
    f"recettes sont marquées d'un astérisque."
)

st.subheader("4. Continents et population")
st.markdown(
    f"{fmt_int(stats['n_categories_continent'])} catégories sont rattachées "
    f"directement à un continent (les Caraïbes en Amérique du Nord ; « Australienne "
    f"et néo-zélandaise » en Océanie ; « Scandinave » en Europe). La bascule "
    f"« Inclure les traditions régionales » de la page 1 rattache aussi les "
    f"traditions à leur territoire d'origine (`REGIONAL_ZONES` dans "
    f"`src/country_mapping.py`) : soul food, cajun et créole, Sud des États-Unis, "
    f"amish et Tex-Mex aux États-Unis, donc à l'Amérique du Nord "
    f"({fmt_int(stats['n_categories_continent_regional'])} catégories au total). Sur "
    f"la carte, ces pays apparaissent en « présence indirecte » ; le Mexique n'y "
    f"figure qu'à travers le Tex-Mex, faute de catégorie mexicaine. La cuisine juive "
    f"(diaspora, sans territoire ; Israël a sa propre catégorie) reste non "
    f"rattachée. Population : tableau worldpopulationreview.com fourni en Séance 5 "
    f"du cours, agrégé par continent (`data/reference/population_continent.csv`). "
    f"Les catégories sont comptées une à une, pas pondérées par leur nombre de "
    f"recettes."
)
nat = continents[continents["perimetre"] == "national"].set_index("continent")
reg = continents[continents["perimetre"] == "regional"].set_index("continent")
st.dataframe(
    nat.assign(
        pop=nat["pct_population"].map(lambda x: fmt_pct(x, 1)),
        cat=nat["pct_categories"].map(lambda x: fmt_pct(x, 1)),
        cat_reg=reg["pct_categories"].map(lambda x: fmt_pct(x, 1)),
        n_reg=reg["n_categories"],
    ).sort_values("pct_population", ascending=False).reset_index()
    [["continent", "population_millions", "pop", "n_categories", "cat", "n_reg", "cat_reg"]]
    .rename(columns={"continent": "Continent", "population_millions": "Population (M)",
                     "pop": "% population", "n_categories": "Catégories",
                     "cat": "% catégories", "n_reg": "Catégories (avec traditions)",
                     "cat_reg": "% catégories (avec traditions)"}),
    hide_index=True, width="stretch",
)

st.subheader("5. Ingrédients : vocabulaire et correction des pluriels")
st.markdown(
    f"Présence de {fmt_int(stats['n_ingredients'])} ingrédients détectée par mot-clé "
    f"dans la liste d'ingrédients : "
    + ", ".join(INGREDIENT_LABELS[k].lower() for k in DIVERSITY_INGREDIENTS)
    + ". Le vocabulaire mélange des ingrédients universels (sel, sucre, beurre…) et "
    "des marqueurs distinctifs (sauce soja, gingembre, cumin…).\n\n"
    f"**Bug corrigé** : la première version cherchait « egg » et « onion » sans le "
    f"pluriel. Or « 2 large eggs » est la forme la plus courante : la fréquence "
    f"médiane de l'œuf passait de {fmt_pct(stats['oeuf_mediane_singulier'])} "
    f"(motif au singulier) à {fmt_pct(stats['oeuf_mediane_corrige'])} une fois "
    f"corrigé, celle de l'oignon de {fmt_pct(stats['oignon_mediane_singulier'])} à "
    f"{fmt_pct(stats['oignon_mediane_corrige'])}. Périmètres choisis : « lait » "
    f"exclut le lait de coco, « beurre » le beurre de cacahuète, « riz » le vinaigre "
    f"et le vin de riz, « gingembre » exclut les biscuits « gingersnap »."
)

st.subheader("6. Familles de cuisines")
k = int(stats["n_familles"])
st.markdown(
    f"Chaque cuisine est décrite par son vecteur de fréquences d'ingrédients. "
    f"Classification hiérarchique ascendante : distance cosinus, liaison moyenne, "
    f"coupe en {fmt_int(stats['n_familles'])} groupes ; ordre des feuilles optimisé "
    f"pour trier les lignes de la heatmap. Les familles sont nommées **après** "
    f"inspection. Stabilité (indice de Rand ajusté, 1 = même partition) : liaison "
    f"pondérée {fmt_num(stats['ari_liaison_weighted'], 2)}, liaison complète "
    f"{fmt_num(stats['ari_liaison_complete'], 2)}, "
    f"{k - 1} groupes {fmt_num(stats['ari_k%d' % (k - 1)], 2)}, "
    f"{k + 1} groupes {fmt_num(stats['ari_k%d' % (k + 1)], 2)}, "
    f"sans les desserts {fmt_num(stats['ari_sans_desserts'], 2)}. Les grands blocs "
    f"(Asie de l'Est, Asie du Sud, Méditerranée) sont stables ; le grand groupe "
    f"« pâtissier » se scinde selon la méthode et dépend en partie des desserts : "
    f"ces familles sont une aide à la lecture, pas un résultat."
)
st.dataframe(
    families.groupby(["family_id", "family_label", "family_traits"], sort=True)["cuisine"]
    .apply(", ".join).reset_index()
    [["family_label", "family_traits", "cuisine"]]
    .rename(columns={"family_label": "Famille", "family_traits": "Plus fréquents qu'ailleurs",
                     "cuisine": "Cuisines"}),
    hide_index=True, width="stretch",
)

st.subheader("7. Attention du public : avis par recette")
st.markdown(
    f"**Avis par recette** = somme des évaluations (étoiles) des recettes "
    f"d'une cuisine ÷ nombre de recettes de cette cuisine. Les recettes sans "
    f"évaluation ({fmt_pct(stats['pct_avis_manquants'], 1)}, note et commentaires "
    f"manquants eux aussi) comptent pour 0 avis : elles font partie de l'offre mais "
    f"n'ont pas capté d'attention. Les exclure ne change presque rien au classement "
    f"(ρ = {fmt_num(stats['rho_manquants_exclus_vs_zero'], 2)}). L'ancienneté n'explique "
    f"pas le nombre d'avis (corrélation de rang "
    f"{fmt_num(stats['spearman_anciennete_avis'], 2)}) ; "
    f"{fmt_pct(stats['pct_recettes_depuis_2022'])} des recettes datent de "
    f"{int(stats['annee_recente'])} ou après, et le classement calculé sur ces seules "
    f"recettes est quasi identique (ρ = {fmt_num(stats['rho_classement_depuis_2022'], 2)}). "
    f"Les notes moyennes, très proches d'une cuisine à l'autre, ne sont pas représentées."
)

st.subheader("8. Type de plat : une heuristique mesurée")
st.markdown(
    f"Il n'y a pas de colonne « catégorie » (dessert, plat…). Le type de plat est "
    f"déduit de mots-clés du **titre** (`src/dish_type.py`), en 4 groupes, avec "
    f"l'ordre de priorité boissons, salades, soupes, sauces, desserts et pains, puis "
    f"plat principal par défaut, et des exclusions pour les pièges connus "
    f"(« shepherd's pie », « egg rolls », « coffee cake », « sweet potato »…). "
    f"Estimation de l'erreur : un premier échantillon aléatoire de "
    f"{fmt_int(val['n_echantillon_ajustement'])} recettes a servi à ajuster "
    f"les règles ({fmt_int(val['n_erreurs_ajustement'])} erreurs), puis un second "
    f"échantillon indépendant de {fmt_int(val['n_echantillon'])} recettes a servi à "
    f"mesurer : **{fmt_int(val['n_erreurs'])} erreurs, soit "
    f"{fmt_pct(val['taux_erreur'])}** (IC 95 % : {fmt_pct(val['ic95_bas'])} à "
    f"{fmt_pct(val['ic95_haut'])}), plus {fmt_int(val['n_ambigus'])} cas ambigus. "
    f"Les erreurs sous-estiment surtout les desserts. Les verdicts (détail recette "
    f"par recette dans `data/reference/validation_type_plat.csv`) ont été posés par "
    f"l'IA : ils doivent encore être relus par le groupe."
)

st.subheader("9. Limites générales")
st.markdown(
    """
- **Une seule plateforme**, anglophone, à audience surtout américaine : on mesure la
  représentation dans ce catalogue, pas la diversité culinaire réelle du monde.
- **Les catégories reflètent les choix éditoriaux d'Allrecipes** ; une cuisine absente
  peut exister ailleurs sur le site sous une autre étiquette.
- **Les mots-clés sont en anglais** et dépendent de la rédaction des recettes
  (« courgette » / « zucchini »…).
- **Corrélation n'est pas causalité** : un écart d'attention entre cuisines peut
  venir de la mise en avant par la plateforme, de la saisonnalité ou de quelques
  recettes très populaires.
"""
)
