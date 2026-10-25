"""
Pipeline de la refonte « Allrecipes reflète-t-elle la diversité culinaire
mondiale ? ». À relancer si les CSV ou les fichiers de référence changent :

    python data_processing/build_diversity_data.py

Lit data/csv/*.csv, data/reference/*.csv et data/processed/overlap_stats.parquet
(produit par build_processed_data.py), et écrit de NOUVEAUX fichiers dans
data/processed/ (les fichiers existants ne sont pas modifiés) :

    T1  continent_summary.parquet, cuisine_catalog.parquet, map_presence.parquet
    T2  ingredient_freq.parquet, cuisine_families.parquet
    T3  attention.parquet
    T4  dish_mix.parquet, dish_validation.parquet
    T5  + statistiques diverses : diversity_stats.parquet (format long)

Affiche à la fin un tableau « valeur calculée / valeur de contrôle » (brief
de la refonte). Un écart de plus de 10 % est signalé et expliqué dans
JOURNAL_IA.md : on ne force jamais un résultat.
"""

import sys
from math import comb, sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, leaves_list, linkage, optimal_leaf_ordering
from scipy.spatial.distance import pdist, squareform
from scipy.stats import spearmanr

from src.country_mapping import (
    CONTINENTS, CUISINE_LABELS_FR, EXTRA_MAP_ISO3, attach_iso3, get_continent,
)
from src.dish_type import DESSERT, DISH_GROUPS, classify_dish
from src.ingredients import INGREDIENT_LABELS, ingredient_presence

ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = ROOT / "data" / "csv"
REF_DIR = ROOT / "data" / "reference"
OUT_DIR = ROOT / "data" / "processed"

MIN_RECIPES = 15        # seuil d'affichage d'une cuisine (axes 2, 3, 4)
SMALL_RECIPES = 30      # en dessous : effectif signalé par un astérisque
CAP_RECIPES = 60        # repère du plafond de collecte (60 à 67 recettes)
N_FAMILIES = 5          # coupe du dendrogramme
RECENT_FROM = "2022-01-01"

# Familles de cuisines : nom géographique donné APRÈS inspection des
# groupes (voir JOURNAL_IA.md). Chaque groupe est reconnu par une cuisine
# « ancre » ; si la classification change au point qu'un groupe ne contient
# pas exactement une ancre, le script s'arrête pour qu'on ré-inspecte.
FAMILY_ANCHORS = {
    "German": "Europe du Nord, centrale et de l'Est, et cuisines au profil pâtissier",
    "Chinese": "Asie de l'Est et du Sud-Est",
    "Indian": "Asie du Sud",
    "Italian": "Méditerranée, Moyen-Orient, Amérique latine et Sud des États-Unis",
    "Tex-Mex": "Tex-Mex",
}


def load_cuisines() -> pd.DataFrame:
    df = pd.read_csv(CSV_DIR / "cuisines.csv")
    df["date_published"] = pd.to_datetime(df["date_published"], errors="coerce")
    for col in ["avg_rating", "total_ratings"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = attach_iso3(df)
    df["cuisine"] = df["country"].map(CUISINE_LABELS_FR)
    df["continent"] = df["country"].map(get_continent)
    df["dish_group"] = df["name"].map(classify_dish)
    return df


# --- T1 : continents et couverture -------------------------------------------
def build_coverage(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    catalog = (
        df.groupby(["country", "cuisine", "iso3", "map_type", "continent"], dropna=False)
        .size().reset_index(name="n_recettes")
        .sort_values("n_recettes", ascending=False)
    )

    pop = pd.read_csv(REF_DIR / "population_continent.csv")
    assert set(pop["continent"]) == set(CONTINENTS), "continents incohérents"
    pop["pct_population"] = pop["population_millions"] / pop["population_millions"].sum()

    with_cont = catalog.dropna(subset=["continent"])
    cats = with_cont.groupby("continent").size().rename("n_categories")
    summary = pop.merge(cats, left_on="continent", right_index=True, how="left")
    summary["n_categories"] = summary["n_categories"].fillna(0).astype(int)
    summary["pct_categories"] = summary["n_categories"] / summary["n_categories"].sum()
    summary["ecart_points"] = 100 * (summary["pct_categories"] - summary["pct_population"])
    summary = summary.sort_values("ecart_points").reset_index(drop=True)

    present = catalog[catalog["map_type"] == "single_country"][["iso3", "country", "cuisine"]]
    extra = [
        {"iso3": iso, "country": cat, "cuisine": CUISINE_LABELS_FR[cat]}
        for cat, isos in EXTRA_MAP_ISO3.items() for iso in isos
    ]
    map_presence = pd.concat([present, pd.DataFrame(extra)], ignore_index=True)
    return catalog, summary, map_presence


# --- T2 : ingrédients et familles ---------------------------------------------
def build_ingredients(df: pd.DataFrame, kept: list[str]) -> pd.DataFrame:
    presence = ingredient_presence(df["ingredients"])
    presence["country"] = df["country"].values
    presence["is_dessert"] = (df["dish_group"] == DESSERT).values
    presence = presence[presence["country"].isin(kept)]

    rows = []
    for scope, sub in [("tout", presence),
                       ("sans_desserts", presence[~presence["is_dessert"]])]:
        n = sub.groupby("country").size()
        pct = sub.groupby("country")[list(INGREDIENT_LABELS)].mean()
        long = pct.reset_index().melt(id_vars="country", var_name="ingredient", value_name="pct")
        long["scope"] = scope
        long["n_recettes"] = long["country"].map(n)
        rows.append(long)
    freq = pd.concat(rows, ignore_index=True)
    freq["cuisine"] = freq["country"].map(CUISINE_LABELS_FR)
    freq["ingredient_label"] = freq["ingredient"].map(INGREDIENT_LABELS)
    return freq


def freq_matrix(freq: pd.DataFrame, scope: str) -> pd.DataFrame:
    return (freq[freq["scope"] == scope]
            .pivot(index="country", columns="ingredient", values="pct")
            [list(INGREDIENT_LABELS)])


def mean_similarity(m: pd.DataFrame) -> float:
    return float((1 - pdist(m.values, "cosine")).mean())


def adjusted_rand(a: pd.Series, b: pd.Series) -> float:
    """Indice de Rand ajusté entre deux partitions (même index)."""
    t = pd.crosstab(a, b).values
    s_ij = sum(comb(int(x), 2) for x in t.ravel())
    s_a = sum(comb(int(x), 2) for x in t.sum(axis=1))
    s_b = sum(comb(int(x), 2) for x in t.sum(axis=0))
    expected = s_a * s_b / comb(int(t.sum()), 2)
    return (s_ij - expected) / (0.5 * (s_a + s_b) - expected)


def build_families(freq: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    m = freq_matrix(freq, "tout")
    d = pdist(m.values, "cosine")
    z = optimal_leaf_ordering(linkage(d, "average"), d)
    labels = pd.Series(fcluster(z, N_FAMILIES, "maxclust"), index=m.index)
    order = [m.index[i] for i in leaves_list(z)]

    # Nom des familles : ancre géographique + ingrédients caractéristiques
    # (les 3 dont la fréquence dépasse le plus la moyenne des 45 cuisines).
    names, traits = {}, {}
    for fam, members in labels.groupby(labels).groups.items():
        anchors = [a for a in FAMILY_ANCHORS if a in members]
        if len(anchors) != 1:
            raise RuntimeError(
                f"La famille {list(members)} contient {len(anchors)} ancres : "
                "ré-inspecter les groupes et mettre à jour FAMILY_ANCHORS.")
        names[fam] = FAMILY_ANCHORS[anchors[0]]
        lift = (m.loc[members].mean() - m.mean()).sort_values(ascending=False)
        traits[fam] = ", ".join(INGREDIENT_LABELS[i].lower() for i in lift.index[:3])

    # Numérotation des familles dans l'ordre du dendrogramme (1 = en haut).
    seen = list(dict.fromkeys(labels[c] for c in order))
    renum = {old: new for new, old in enumerate(seen, start=1)}
    families = pd.DataFrame({
        "country": order,
        "cuisine": [CUISINE_LABELS_FR[c] for c in order],
        "family_id": [renum[labels[c]] for c in order],
        "family_label": [names[labels[c]] for c in order],
        "family_traits": [traits[labels[c]] for c in order],
        "ordre": range(len(order)),
    })

    # Stabilité : autres liaisons, autres nombres de groupes, sans desserts.
    stab = {}
    for method in ["complete", "weighted"]:
        alt = pd.Series(fcluster(linkage(d, method), N_FAMILIES, "maxclust"), index=m.index)
        stab[f"ari_liaison_{method}"] = adjusted_rand(labels, alt)
    for k in [N_FAMILIES - 1, N_FAMILIES + 1]:
        alt = pd.Series(fcluster(z, k, "maxclust"), index=m.index)
        stab[f"ari_k{k}"] = adjusted_rand(labels, alt)
    m_sd = freq_matrix(freq, "sans_desserts").loc[m.index]
    alt = pd.Series(fcluster(linkage(pdist(m_sd.values, "cosine"), "average"),
                             N_FAMILIES, "maxclust"), index=m.index)
    stab["ari_sans_desserts"] = adjusted_rand(labels, alt)

    # Dépendance aux desserts : similarité moyenne, globale et par famille.
    stab["sim_moyenne_tout"] = mean_similarity(m)
    stab["sim_moyenne_sans_desserts"] = mean_similarity(m_sd)
    stab["sim_moyenne_sans_sel"] = mean_similarity(m.drop(columns="salt"))
    fam_bake = renum[labels["German"]]
    members = families.loc[families["family_id"] == fam_bake, "country"]
    stab["sim_famille_europe_tout"] = mean_similarity(m.loc[members])
    stab["sim_famille_europe_sans_desserts"] = mean_similarity(m_sd.loc[members])
    return families, stab


# --- T3 : attention du public -------------------------------------------------
def build_attention(df: pd.DataFrame, kept: list[str]) -> tuple[pd.DataFrame, dict]:
    # total_ratings manquant (≈ 4 % des recettes) : la note moyenne et le
    # nombre de commentaires sont alors manquants eux aussi. On l'interprète
    # comme « aucun avis encore » et on compte 0 avis (la recette fait
    # partie de l'offre mais n'a pas capté d'attention).
    d = df.assign(avis=df["total_ratings"].fillna(0))

    def per_cuisine(sub: pd.DataFrame) -> pd.DataFrame:
        g = sub.groupby(["country", "cuisine", "map_type"]).agg(
            n_recettes=("name", "size"),
            avis_total=("avis", "sum"),
            note_moyenne=("avg_rating", "mean"),
        ).reset_index()
        g["avis_par_recette"] = g["avis_total"] / g["n_recettes"]
        return g.sort_values("avis_par_recette", ascending=False).reset_index(drop=True)

    att = per_cuisine(d[d["country"].isin(kept)])

    stats = {"pct_avis_manquants": float(df["total_ratings"].isna().mean())}
    # Variante : recettes sans avis exclues (au lieu de compter 0).
    excl = d[d["country"].isin(kept)].groupby("country")["total_ratings"].mean()
    stats["rho_manquants_exclus_vs_zero"] = float(
        spearmanr(att.set_index("country")["avis_par_recette"], excl.loc[att["country"]]).statistic)
    # Ancienneté : une recette plus ancienne a-t-elle mécaniquement plus d'avis ?
    sub = d[d["country"].isin(kept)]
    age = (sub["date_published"].max() - sub["date_published"]).dt.days
    stats["spearman_anciennete_avis"] = float(spearmanr(age, sub["avis"]).statistic)
    stats["pearson_anciennete_avis"] = float(np.corrcoef(age, sub["avis"])[0, 1])
    stats["pct_recettes_depuis_2022"] = float((df["date_published"] >= RECENT_FROM).mean())
    recent = per_cuisine(sub[sub["date_published"] >= RECENT_FROM]).set_index("country")
    stats["rho_classement_depuis_2022"] = float(spearmanr(
        att.set_index("country")["avis_par_recette"],
        recent["avis_par_recette"].reindex(att["country"])).statistic)

    # Contrôles du brief : 41 catégories « pays » (single_country).
    pays = per_cuisine(d[d["map_type"] == "single_country"])
    stats["controle_41_pays_mediane"] = float(pays["avis_par_recette"].median())
    stats["controle_41_pays_part_top5"] = float(pays["avis_total"].head(5).sum() / pays["avis_total"].sum())
    return att, stats


# --- T4 : type de plat --------------------------------------------------------
def build_dish_mix(df: pd.DataFrame, kept: list[str]) -> pd.DataFrame:
    sub = df[df["country"].isin(kept)]
    mix = (sub.groupby(["country", "cuisine", "dish_group"]).size()
           .unstack(fill_value=0).reindex(columns=DISH_GROUPS, fill_value=0)
           .stack().rename("n").reset_index())
    mix["n_total"] = mix.groupby("country")["n"].transform("sum")
    mix["pct"] = mix["n"] / mix["n_total"]
    mix["petit_effectif"] = mix["n_total"] < SMALL_RECIPES
    return mix


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def build_dish_validation() -> pd.DataFrame:
    """Taux d'erreur mesuré sur l'échantillon 2 (vérifié à la main, tiré
    APRÈS l'ajustement des règles sur l'échantillon 1)."""
    val = pd.read_csv(REF_DIR / "validation_type_plat.csv")
    mesure = val[val["echantillon"] == 2]
    # Garde-fou : l'heuristique actuelle doit reproduire les prédictions
    # vérifiées ; sinon le taux mesuré ne s'applique plus.
    drift = (mesure["name"].map(classify_dish) != mesure["groupe_predit"]).sum()
    if drift:
        raise RuntimeError(
            f"{drift} prédictions de l'échantillon de validation ont changé : "
            "le taux d'erreur mesuré n'est plus valable, re-valider à la main.")
    n = len(mesure)
    k = int((mesure["statut"] == "erreur").sum())
    amb = int((mesure["statut"] == "ambigu").sum())
    lo, hi = wilson(k, n)
    return pd.DataFrame([{
        "n_echantillon": n, "n_erreurs": k, "n_ambigus": amb,
        "taux_erreur": k / n, "taux_erreur_avec_ambigus": (k + amb) / n,
        "ic95_bas": lo, "ic95_haut": hi,
        "n_echantillon_ajustement": int((val["echantillon"] == 1).sum()),
        "n_erreurs_ajustement": int((val.loc[val["echantillon"] == 1, "statut"] == "erreur").sum()),
        "n_desserts_manques": int(((mesure["statut"] == "erreur")
                                   & (mesure["groupe_verifie"] == DESSERT)).sum()),
    }])


def plural_bug_stats(df: pd.DataFrame, kept: list[str]) -> dict:
    """Effet du bug des pluriels (motif `\\begg\\b` de src/ingredients.py) sur la
    fréquence médiane de l'œuf et de l'oignon, cuisines retenues."""
    sub = df[df["country"].isin(kept)]
    text = sub["ingredients"].fillna("").str.lower()
    out = {}
    for name, old, new in [("oeuf", r"\begg\b", r"\beggs?\b"),
                           ("oignon", r"\bonion\b", r"\bonions?\b")]:
        for tag, pattern in [("singulier", old), ("corrige", new)]:
            pct = text.str.contains(pattern, regex=True).groupby(sub["country"]).mean()
            out[f"{name}_mediane_{tag}"] = float(pct.median())
    return out


# --- Contrôles ----------------------------------------------------------------
def control_table(rows: list[tuple[str, float, float]]) -> pd.DataFrame:
    t = pd.DataFrame(rows, columns=["indicateur", "calcule", "controle"])
    t["ecart_%"] = 100 * (t["calcule"] - t["controle"]) / t["controle"].replace(0, np.nan)
    t["alerte"] = np.where(t["ecart_%"].abs() > 10, "ÉCART > 10 %", "")
    return t


def build():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_cuisines()

    counts = df["country"].value_counts()
    kept = sorted(counts[counts >= MIN_RECIPES].index)

    catalog, continent_summary, map_presence = build_coverage(df)
    freq = build_ingredients(df, kept)
    families, fam_stats = build_families(freq)
    attention, att_stats = build_attention(df, kept)
    dish_mix = build_dish_mix(df, kept)
    validation = build_dish_validation()

    overlap = pd.read_parquet(OUT_DIR / "overlap_stats.parquet").iloc[0]
    n_unique = int(overlap.n_all_recipes + overlap.n_cuisines - overlap.n_overlap)
    all_urls = pd.read_csv(CSV_DIR / "all_recipes.csv", usecols=["url"])["url"]
    assert n_unique == len(set(all_urls) | set(df["url"])), "total dédupliqué incohérent"

    stats = {
        "n_recettes_uniques": n_unique,
        "n_categories": int(df["country"].nunique()),
        "n_categories_retenues": len(kept),
        "seuil_recettes": MIN_RECIPES,
        "seuil_petit_effectif": SMALL_RECIPES,
        "n_categories_continent": int(catalog["continent"].notna().sum()),
        "n_categories_single_country": int((catalog["map_type"] == "single_country").sum()),
        "n_recettes_single_country": int(catalog.loc[catalog["map_type"] == "single_country", "n_recettes"].sum()),
        "n_pays_carte": int(map_presence["iso3"].nunique()),
        "seuil_plafond": CAP_RECIPES,
        "annee_recente": int(RECENT_FROM[:4]),
        "n_categories_plafond": int((catalog["n_recettes"] >= CAP_RECIPES).sum()),
        "max_recettes_categorie": int(catalog["n_recettes"].max()),
        "avis_total": float(df["total_ratings"].fillna(0).sum()),
        "n_ingredients": len(INGREDIENT_LABELS),
        "n_familles": N_FAMILIES,
        **fam_stats,
        **att_stats,
        **plural_bug_stats(df, kept),
    }

    # Écriture
    catalog.to_parquet(OUT_DIR / "cuisine_catalog.parquet", index=False)
    continent_summary.to_parquet(OUT_DIR / "continent_summary.parquet", index=False)
    map_presence.to_parquet(OUT_DIR / "map_presence.parquet", index=False)
    freq.to_parquet(OUT_DIR / "ingredient_freq.parquet", index=False)
    families.to_parquet(OUT_DIR / "cuisine_families.parquet", index=False)
    attention.to_parquet(OUT_DIR / "attention.parquet", index=False)
    dish_mix.to_parquet(OUT_DIR / "dish_mix.parquet", index=False)
    validation.to_parquet(OUT_DIR / "dish_validation.parquet", index=False)
    pd.DataFrame({"stat": list(stats), "value": [float(v) for v in stats.values()]}).to_parquet(
        OUT_DIR / "diversity_stats.parquet", index=False)

    # Tableau de contrôle (valeurs du brief)
    cs = continent_summary.set_index("continent")
    pays_freq = freq_matrix(freq, "tout")
    pays_freq = pays_freq[pays_freq.index.isin(catalog.loc[catalog.map_type == "single_country", "country"])]
    att = attention.set_index("country")["avis_par_recette"]
    dm = dish_mix[dish_mix["dish_group"] == DESSERT].set_index("country")["pct"]
    rows = [
        ("Total dédupliqué", n_unique, 15589),
        ("Catégories single_country", stats["n_categories_single_country"], 41),
        ("Recettes single_country", stats["n_recettes_single_country"], 1762),
        ("Catégories retenues (>= 15 recettes)", len(kept), 45),
        *[(f"% population {c}", 100 * cs.loc[c, "pct_population"], v)
          for c, v in [("Asie", 59), ("Afrique", 18), ("Europe", 9),
                       ("Amérique du Nord", 7.5), ("Amérique du Sud", 5.5), ("Océanie", 0.6)]],
        *[(f"% catégories {c}", 100 * cs.loc[c, "pct_categories"], v)
          for c, v in [("Europe", 40), ("Asie", 35), ("Amérique du Sud", 12),
                       ("Amérique du Nord", 9), ("Afrique", 2), ("Océanie", 2)]],
        *[(f"Recettes {c}", counts[c], v)
          for c, v in [("Belgian", 6), ("Swiss", 10), ("Colombian", 11), ("Bangladeshi", 12)]],
        ("Soy sauce max (37 pays) %", 100 * pays_freq["soy sauce"].max(), 82),
        ("Cumin max (37 pays) %", 100 * pays_freq["cumin"].max(), 68),
        ("Ginger max (37 pays) %", 100 * pays_freq["ginger"].max(), 75),
        ("Egg min (37 pays) %", 100 * pays_freq["egg"].min(), 2),
        ("Egg max (37 pays) %", 100 * pays_freq["egg"].max(), 86),
        ("Egg médiane (37 pays) %", 100 * pays_freq["egg"].median(), 29),
        ("Similarité moyenne, tout", fam_stats["sim_moyenne_tout"], 0.68),
        ("Similarité moyenne, sans desserts", fam_stats["sim_moyenne_sans_desserts"], 0.68),
        ("Similarité famille Europe, tout", fam_stats["sim_famille_europe_tout"], 0.88),
        ("Similarité famille Europe, sans desserts", fam_stats["sim_famille_europe_sans_desserts"], 0.81),
        ("Avis/recette médiane (41 pays)", att_stats["controle_41_pays_mediane"], 51),
        ("Part des avis du top 5 (41 pays) %", 100 * att_stats["controle_41_pays_part_top5"], 36),
        ("Avis/recette Greek", att["Greek"], 180),
        ("Avis/recette French", att["French"], 160),
        ("Avis/recette Canadian", att["Canadian"], 135),
        ("Avis/recette Thai", att["Thai"], 127),
        ("Avis/recette Japanese", att["Japanese"], 117),
        ("Avis/recette Persian", att["Persian"], 17),
        ("Avis/recette Chilean", att["Chilean"], 20),
        ("Note moyenne min (pays)", attention.loc[attention.map_type == "single_country", "note_moyenne"].min(), 4.25),
        ("Note moyenne max (pays)", attention.loc[attention.map_type == "single_country", "note_moyenne"].max(), 4.69),
        ("Corrélation ancienneté x avis (Spearman)", att_stats["spearman_anciennete_avis"], -0.05),
        ("rho classement depuis 2022", att_stats["rho_classement_depuis_2022"], 0.98),
        ("% recettes depuis 2022", 100 * att_stats["pct_recettes_depuis_2022"], 91),
        ("% desserts Pakistani", 100 * dm["Pakistani"], 0),
        ("% desserts Austrian", 100 * dm["Austrian"], 70),
    ]
    table = control_table(rows)
    pd.set_option("display.width", 160)
    print(table.to_string(index=False, float_format=lambda x: f"{x:,.2f}"))
    print("\nStabilité des familles (indice de Rand ajusté, 1 = partition identique) :")
    for k, v in fam_stats.items():
        if k.startswith("ari"):
            print(f"  {k:28s} {v:.2f}")
    print("\nFamilles :")
    for fam, g in families.groupby("family_id"):
        print(f"  {fam}. {g.family_label.iloc[0]} [{g.family_traits.iloc[0]}] : {', '.join(g.country)}")
    print("\nValidation du type de plat :", validation.iloc[0].to_dict())
    print("\nOK — fichiers écrits dans", OUT_DIR)


if __name__ == "__main__":
    build()
