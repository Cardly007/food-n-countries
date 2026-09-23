"""
Table de correspondance entre les 49 valeurs de la colonne `country` de
cuisines.csv et un code ISO-3 pour la carte choroplèthe.

POURQUOI CE FICHIER EXISTE (à garder dans le journal de bord) :
La colonne `country` du dataset n'est PAS une liste de pays. C'est un mélange
de nationalités ("Chinese", "Italian"), de régions multi-pays
("Scandinavian", "Australian and New Zealander"), de traditions culinaires
régionales américaines ("Soul Food", "Cajun and Creole", "Tex-Mex",
"Southern Recipes") et de cuisines communautaires/religieuses sans État
("Jewish", "Amish and Mennonite"). Une IA à qui on demande "trace une carte
du monde des cuisines" produira très probablement une choroplèthe en forçant
chaque valeur sur un pays — c'est exactement le genre d'erreur à repérer et
documenter dans l'étape 3 (audit critique) du projet.

Règle adoptée ici : seules les valeurs de type "single_country" sont
affichées sur la carte choroplèthe. Les autres (multi_country, us_regional,
non_national) sont conservées dans les analyses non géographiques
(nutrition, notes, ingrédients) mais explicitement exclues de la carte, avec
un compteur affiché à l'utilisateur pour qu'il sache combien de recettes
sont concernées.
"""

import pandas as pd

# map_type:
#   single_country  -> un seul pays, code ISO-3 fiable
#   multi_country   -> couvre plusieurs pays, pas de choroplèthe simple
#   us_regional     -> tradition culinaire régionale/communautaire aux
#                      États-Unis, pas une nationalité
#   non_national    -> tradition culinaire communautaire/religieuse sans
#                      territoire national propre
COUNTRY_MAPPING = {
    "Canadian":                       {"iso3": "CAN", "map_type": "single_country"},
    "Brazilian":                      {"iso3": "BRA", "map_type": "single_country"},
    "Filipino":                       {"iso3": "PHL", "map_type": "single_country"},
    "Cuban":                          {"iso3": "CUB", "map_type": "single_country"},
    "Chinese":                        {"iso3": "CHN", "map_type": "single_country"},
    "Russian":                        {"iso3": "RUS", "map_type": "single_country"},
    "Indian":                         {"iso3": "IND", "map_type": "single_country"},
    "French":                         {"iso3": "FRA", "map_type": "single_country"},
    "Italian":                        {"iso3": "ITA", "map_type": "single_country"},
    "Japanese":                       {"iso3": "JPN", "map_type": "single_country"},
    "Greek":                          {"iso3": "GRC", "map_type": "single_country"},
    "German":                         {"iso3": "DEU", "map_type": "single_country"},
    "Vietnamese":                     {"iso3": "VNM", "map_type": "single_country"},
    "Thai":                           {"iso3": "THA", "map_type": "single_country"},
    "Spanish":                        {"iso3": "ESP", "map_type": "single_country"},
    "Polish":                         {"iso3": "POL", "map_type": "single_country"},
    "Korean":                         {"iso3": "KOR", "map_type": "single_country"},
    "Portuguese":                     {"iso3": "PRT", "map_type": "single_country"},
    "Lebanese":                       {"iso3": "LBN", "map_type": "single_country"},
    "Persian":                        {"iso3": "IRN", "map_type": "single_country"},
    "Jamaican":                       {"iso3": "JAM", "map_type": "single_country"},
    "Peruvian":                       {"iso3": "PER", "map_type": "single_country"},
    "Turkish":                        {"iso3": "TUR", "map_type": "single_country"},
    "Danish":                         {"iso3": "DNK", "map_type": "single_country"},
    "Swedish":                        {"iso3": "SWE", "map_type": "single_country"},
    "Argentinian":                    {"iso3": "ARG", "map_type": "single_country"},
    "Norwegian":                      {"iso3": "NOR", "map_type": "single_country"},
    "Pakistani":                      {"iso3": "PAK", "map_type": "single_country"},
    "Malaysian":                      {"iso3": "MYS", "map_type": "single_country"},
    "Indonesian":                     {"iso3": "IDN", "map_type": "single_country"},
    "Israeli":                        {"iso3": "ISR", "map_type": "single_country"},
    "Chilean":                        {"iso3": "CHL", "map_type": "single_country"},
    "Dutch":                          {"iso3": "NLD", "map_type": "single_country"},
    "Austrian":                       {"iso3": "AUT", "map_type": "single_country"},
    "South African":                  {"iso3": "ZAF", "map_type": "single_country"},
    "Finnish":                        {"iso3": "FIN", "map_type": "single_country"},
    "Bangladeshi":                    {"iso3": "BGD", "map_type": "single_country"},
    "Colombian":                      {"iso3": "COL", "map_type": "single_country"},
    "Swiss":                          {"iso3": "CHE", "map_type": "single_country"},
    "Belgian":                        {"iso3": "BEL", "map_type": "single_country"},
    "Puerto Rican":                   {"iso3": "PRI", "map_type": "single_country"},

    # Multi-pays : pas de choroplèthe simple sans double-compter les pays
    "Australian and New Zealander":   {"iso3": None, "map_type": "multi_country"},
    "Scandinavian":                   {"iso3": None, "map_type": "multi_country"},

    # Traditions régionales/communautaires aux États-Unis, pas des pays
    "Soul Food":                      {"iso3": None, "map_type": "us_regional"},
    "Cajun and Creole":               {"iso3": None, "map_type": "us_regional"},
    "Tex-Mex":                        {"iso3": None, "map_type": "us_regional"},
    "Southern Recipes":               {"iso3": None, "map_type": "us_regional"},

    # Communautés religieuses/diasporiques sans territoire national propre
    "Jewish":                         {"iso3": None, "map_type": "non_national"},
    "Amish and Mennonite":            {"iso3": None, "map_type": "non_national"},
}


def get_mapping_df() -> pd.DataFrame:
    """Retourne la table de correspondance sous forme de DataFrame."""
    df = pd.DataFrame.from_dict(COUNTRY_MAPPING, orient="index")
    df.index.name = "country"
    return df.reset_index()


def attach_iso3(cuisines_df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute les colonnes iso3 et map_type à un DataFrame cuisines.

    Toute valeur de `country` absente de COUNTRY_MAPPING lève une erreur
    explicite plutôt que d'être silencieusement ignorée : si Allrecipes
    ajoute une nouvelle catégorie, on veut le savoir plutôt que la voir
    disparaître silencieusement de la carte.
    """
    mapping = get_mapping_df()
    unknown = set(cuisines_df["country"].unique()) - set(mapping["country"])
    if unknown:
        raise ValueError(
            f"Valeurs de 'country' non répertoriées dans COUNTRY_MAPPING : "
            f"{sorted(unknown)}. Ajoutez-les à src/country_mapping.py."
        )
    return cuisines_df.merge(mapping, on="country", how="left")
