"""
Classification heuristique du type de plat à partir du TITRE de la recette.

Le dataset n'a pas de colonne « catégorie » (dessert, plat, entrée...). On
l'approche par mots-clés sur le titre, en 4 groupes :

    Plats principaux                 (défaut : tout ce qui n'est pas reconnu)
    Soupes et ragoûts
    Desserts, pâtisseries et pains
    Accompagnements et boissons      (salades, sauces et condiments, boissons)

Ordre de priorité : boissons, salades, soupes, sauces, desserts/pains, sinon
plat principal. Chaque règle a une liste d'exclusions pour les pièges
connus (« shepherd's pie », « egg rolls », « coffee cake », « sweet potato »,
« chicken in black bean sauce »...).

C'EST UNE HEURISTIQUE : son taux d'erreur est mesuré sur un échantillon
aléatoire de 100 recettes dont les verdicts ont été posés par l'IA, à
relire par le groupe (voir JOURNAL_IA.md et
data/reference/validation_type_plat.csv).
"""

import re

MAIN = "Plats principaux"
SOUP = "Soupes et ragoûts"
DESSERT = "Desserts, pâtisseries et pains"
SIDE = "Accompagnements et boissons"

# Ordre d'affichage : desserts en premier (segment de base de l'axe 4).
DISH_GROUPS = [DESSERT, MAIN, SOUP, SIDE]


def _rx(words: list[str]) -> re.Pattern:
    return re.compile(r"\b(?:" + "|".join(words) + r")\b")


# --- Boissons ---------------------------------------------------------------
DRINK = _rx([
    r"drinks?", r"cocktails?", r"punch", r"teas?", r"coffee", r"lattes?",
    r"smoothies?", r"lemonade", r"limeade", r"sangria", r"horchata",
    r"chicha", r"caipirinha", r"pisco sour", r"mojitos?", r"margaritas?",
    r"eggnog", r"coquito", r"lassi", r"chai", r"hot chocolate", r"cider",
    r"mulled wine", r"gl[öo]gg", r"liqueur", r"limoncello", r"lonkero",
    r"agua fresca", r"kvass", r"milkshakes?", r"spritz", r"sling", r"toddy",
    r"(?:fruit|banana|mango|strawberry|protein) shakes?", r"golden milk",
    r"rum runner", r"cr[eè]me de vie", r"daiquiris?", r"martinis?",
])
# « coffee cake », « tea cakes », « sweet tea peaches », « tea eggs »...
DRINK_EXCL = _rx([
    r"cakes?", r"cookies?", r"bread", r"jelly", r"panna cotta", r"rings?",
    r"eggs", r"peaches", r"sandwich(?:es)?", r"pudding", r"pie", r"chicken",
    r"pork", r"beef", r"salmon", r"ribs", r"steak", r"brined", r"smoked",
    r"rubbed", r"glazed", r"braised",
])

# --- Salades ----------------------------------------------------------------
SALAD = _rx([r"salads?", r"slaw", r"coleslaw", r"tabbouleh", r"fattoush",
             r"panzanella", r"kachumbari", r"pico de gallo"])

# --- Soupes et ragoûts ------------------------------------------------------
SOUP_RX = _rx([
    r"soups?", r"stews?", r"chowder", r"bisque", r"gumbo", r"bor(?:sch|scht|sht|shch)",
    r"pho", r"ramen", r"laksa", r"caldo", r"sopa", r"potage", r"consomm[ée]",
    r"goulash", r"gulyas", r"pozole", r"posole", r"menudo", r"sinigang",
    r"tinola", r"minestrone", r"gazpacho", r"solyanka", r"shchi", r"cassoulet",
    r"bouillabaisse", r"feijoada", r"tagine", r"hot ?pot", r"jjigae",
    r"chili con carne",
])
# « soup dumplings » (xiao long bao), « french onion soup focaccia »...
SOUP_EXCL = re.compile(r"\bsoups?\s+(?:focaccia|bread|dumplings?|mix|noodles?)\b")
# « chili » seul est un plat mijoté (soupe/ragoût), sauf s'il qualifie
# autre chose : « chili garlic paneer », « sweet chili sauce »...
CHILI = re.compile(
    r"(?<!sweet )\bchili\b(?!\s*(?:garlic|lime|sauce|oil|paste|powder|crisp|"
    r"flakes?|peppers?|chicken|shrimp|cavatappi|dogs?|mac|cheese|salt|rub|"
    r"[-–]))"
)

# --- Sauces et condiments ---------------------------------------------------
SAUCE = _rx([
    r"sauce", r"dips?", r"salsa", r"dressing", r"chutney", r"pickles?",
    r"pickled", r"relish", r"marinade", r"seasoning", r"spice (?:blend|mix|rub)",
    r"curry powder", r"garam masala", r"raita", r"tzatziki", r"hummus",
    r"houmous", r"guacamole", r"gravy", r"pesto", r"chimichurri", r"aioli",
    r"mayonnaise", r"vinaigrette", r"pebre", r"sofrito", r"recaito", r"harissa",
    r"zhoug", r"kimchi", r"sauerkraut", r"baba ghanoush", r"muhammara",
    r"labneh", r"jam", r"marmalade",
    r"(?:pepper|jalape[ñn]o|mint|hot pepper|chile|chili) jelly",
    r"(?:cucumber|garlic|mint) yogh?urt", r"pimento cheese", r"sushi vinegar",
    r"(?:7|seven) spices?", r"charoset", r"haroset", r"baharat", r"sazon",
])
# « chicken in black bean sauce », « souvlaki with tzatziki sauce »,
# « salsa chicken », « kimchi fried rice » : la sauce accompagne un plat.
SAUCE_EXCL = re.compile(
    r"\b(?:with|in|and|over|on)\b.*\b(?:sauce|dip|salsa|dressing|chutney|"
    r"gravy|pesto|raita|tzatziki|aioli|chimichurri|relish|kimchi)\b"
    r"|\b(?:salsa|kimchi|pesto|chimichurri|harissa|jam)\s+(?:chicken|pork|"
    r"beef|fried rice|rice|pancakes?|jun|jjigae|stew|soup|fish|shrimp|"
    r"pasta|noodles?|tofu|lamb|burgers?|steak|salmon|bokkeumbap|dumplings?|"
    r"mandu|thumbprint|cookies?|bars?|tarts?|filled)"
    r"|\bpickled?\s+(?:pork|herring|fish|beef)"
    r"|\bsauce with\b|\bjam\s+\w|\bchimichurri\s+(?!sauce)\w"
    r"|\b(?:pork|brats?|sausages?|chops|kielbasa|chicken|beef|ribs)\b.*\bsauerkraut"
    r"|\bsauerkraut\b.*\b(?:pork|brats?|sausages?|kielbasa|balls|soup)\b"
)

# --- Desserts, pâtisseries et pains ----------------------------------------
DESSERT_RX = _rx([
    r"cakes?", r"cookies?", r"brownies?", r"pies?", r"tarts?", r"tartlets?",
    r"tortes?", r"cupcakes?", r"puddings?", r"fudge", r"cand(?:y|ies)",
    r"cobblers?", r"muffins?", r"scones?", r"biscotti", r"cheesecakes?",
    r"mousse", r"truffles?", r"pastr(?:y|ies)", r"donuts?", r"doughnuts?",
    r"churros?", r"flan", r"custards?", r"baklava", r"tiramisu", r"strudel",
    r"cr[eê]pes?", r"pancakes?", r"waffles?", r"cinnamon rolls?", r"kringle",
    r"babka", r"rugelach", r"shortbread", r"gingerbread", r"kipferl?n?",
    r"buns?", r"bread", r"breads", r"loaf", r"loaves",
    # compléments après inspection des titres
    r"macarons?", r"macaroons?", r"meringues?", r"pavlova", r"lamingtons?",
    r"brigadeiros?", r"alfajores?", r"dulce de leche", r"ice cream", r"sorbet",
    r"gelato", r"halva", r"halwa", r"kheer", r"gulab jamun", r"mochi",
    r"panna cotta", r"jelly", r"trifle", r"compote", r"crumble", r"crisp", r"beignets?",
    r"kolache?s?", r"kolaczki", r"paczki", r"hamantaschen", r"challah",
    r"focaccia", r"naan", r"rotis?", r"chapatis?", r"parathas?", r"pitas?",
    r"bagels?", r"pretzels?", r"brioche", r"stollen", r"panettone",
    r"toffee", r"caramels?", r"chocolates?", r"cocada", r"bibingka",
    r"halo-halo", r"turon", r"kulfi", r"barfi", r"burfi", r"ladoo", r"laddu",
    r"jalebi", r"kunafa", r"knafeh", r"basbousa", r"ma'?amoul", r"sfouf",
    r"bars", r"squares", r"jelly roll", r"poppy seed roll",
    r"(?:bread|dinner|sweet|hawaiian|crescent) rolls?", r"semla", r"boller",
    r"pastel de nata", r"past[ée]is de nata", r"melktert", r"koeksisters?",
    r"vetkoek", r"rusks?", r"pão de queijo", r"pao de queijo", r"chipas?",
    r"pan de queso", r"pandesal", r"ensaymada", r"polvorones?",
    r"dessert", r"tres leches", r"quindim", r"beijinhos?", r"bolo",
    r"sticky rice with mango", r"mango sticky rice",
    r"teacakes?", r"zeppole", r"cannoli", r"sfogliatell[ae]", r"pizzelle",
    r"amaretti", r"panforte", r"krumkake", r"lefse", r"rosettes?",
    r"aebleskiver", r"[æa]bleskiver", r"kanelbullar", r"pulla", r"limpa",
    r"rugbr[øo]d", r"knäckebröd", r"crispbread", r"flatbread", r"ekmek",
    r"simit", r"pide", r"lavash", r"injera", r"arepas?", r"bammy",
    r"hardo bread", r"bulla", r"gizzada", r"cornbread", r"turkish delight",
    r"lokum", r"helva", r"loukoumades", r"malasadas?", r"stroop ?waff?els?",
    r"wafers?", r"boterkoek", r"cinnamon snails", r"(?:noodle|lokshen|apple) kugel",
    r"p[âa]te (?:sucr[ée]e|bris[ée]e)", r"po[gğ]a[cç]a", r"tartufo",
    r"pfeffern[uü]e?sse", r"shirini", r"suspiro", r"maja blanca", r"dough",
    r"(?:quince|apple|guava|sweet|pumpkin) empanadas?",
])
DESSERT_EXCL = re.compile(
    # tourtes et tartes salées
    r"\b(?:pork|meat|pot|(?<!sweet )potato|shepherd'?s?|cottage|onion|cabbage|spinach|"
    r"tomato|chicken|fish|tamale|beef|mince|steak|game|savory|savoury|"
    r"cheese and onion|leek|mushroom|bacon|ham|sausage|tuna|salmon|lamb|"
    r"turkey|pizza|crab)\s+(?:pies?|tarts?|pot pies?)\b"
    r"|\bpastel(?:on| de papas| de choclo)\b"
    r"|\bspanakopita|\bbourekas?|(?<!quince )(?<!apple )(?<!guava )(?<!sweet )(?<!pumpkin )\bempanadas?|\bpasties\b|\bpasty\b"
    # galettes salées
    r"|\b(?:fish|crab|potato|salmon|rice|shrimp|tuna|corn|zucchini|"
    r"cod|salt ?fish|codfish|tteok|vegetable|okonomiyaki)\s+cakes?\b"
    r"|\b(?:kimchi|savory|savoury|potato|scallion|green onion|vegetable|"
    r"seafood|korean|zucchini|mung bean|chive)\s+pancakes?\b"
    r"|\bjun\b|\bjeon\b|\bpajeon\b|\blatkes?\b"
    # boudins salés, divers
    r"|\b(?:black|yorkshire|blood|corn)\s+puddings?\b"
    r"|\btruffle (?:oil|fries|mac|pasta|salt)\b"
    r"|\b(?:salmon|chicken liver|liver|ham|tuna)\s+mousse\b"
    r"|\b(?:meat|salmon|tuna|ham|lentil|nut|turkey|veggie|vegetable)\s*loaf\b"
    r"|\bmeatloaf\b"
    r"|\b(?:steamed|pork|bbq|barbecue|char siu|chicken|beef)\s+buns?\b"
    r"|\bsiopao\b|\bbao\b"
    r"|\b(?:egg|spring|cabbage|sushi|california|sausage|salad|summer|"
    r"lumpia|tuna|crab|beef|pork|chicken)\s+rolls?\b"
    r"|\bbread(?:ed)?\s+(?:crumbs?|stuffing|dressing|salad|soup)\b"
    r"|\b(?:shrimp|prawn)\s+toast\b"
    r"|\b(?:dark|chocolate)\s+(?:chili|mole)\b|\bmole\b"
    r"|\b(?:chicken|beef|lamb|pork|gyros?|falafel|pizza)\b.*\bpitas?\b"
    r"|\bmac(?:aroni)?\s+and\s+cheese\b"
    r"|\bcaramel(?:i[sz]ed)?\s+(?:chicken|pork|fish|shrimp|salmon|beef|onions?)\b"
    r"|\bb[aá]nh x[eè]o\b|\bbun kabab\b|\b[æa]e?ggekage\b|\brappie\b"
    r"|\bcheesecake factory\b|\bg[oö]zleme\b|\bpizza dough\b"
)


def classify_dish(title: str) -> str:
    """Retourne le groupe de plat d'une recette à partir de son titre."""
    t = str(title).lower()
    if DRINK.search(t) and not DRINK_EXCL.search(t):
        return SIDE
    if SALAD.search(t):
        return SIDE
    if (SOUP_RX.search(t) or CHILI.search(t)) and not SOUP_EXCL.search(t):
        return SOUP
    if SAUCE.search(t) and not SAUCE_EXCL.search(t):
        return SIDE
    if DESSERT_RX.search(t) and not DESSERT_EXCL.search(t):
        return DESSERT
    return MAIN
