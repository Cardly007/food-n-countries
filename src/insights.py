"""
Indicateurs et titres-insights calculés (variante grand public).

RÈGLE (brief, section 1.1) : aucun chiffre ni conclusion n'est écrit en dur
dans un texte affiché. Chaque titre-insight est produit par une fonction
`build_insight_title_*` qui choisit sa formulation selon la valeur calculée :
si les chiffres ne soutiennent pas le message attendu, le titre le dit.

Les seuils de bascule entre formulations sont des constantes nommées
ci-dessous, pour être discutés dans le journal de bord (JOURNAL_IA.md).

Ces indicateurs sont calculés ici, à partir des parquets existants de
data/processed/, sans modifier le pipeline (data_processing/).
"""

import numpy as np
import pandas as pd
from scipy import stats

from src.theme import (
    country_label, fmt_int, fmt_num, fmt_pct, fmt_signed, ingredient_label,
)

# ---------------------------------------------------------------------------
# Seuils de bascule (à justifier dans le journal)
# ---------------------------------------------------------------------------

# Axe 1 — écart de fréquence d'un ingrédient entre le pays qui l'utilise le
# plus et celui qui l'utilise le moins (en points de pourcentage).
COMMON_SPREAD_MAX = 0.25      # ≤ 25 points : ingrédient « commun »
DISTINCT_SPREAD_MIN = 0.40    # ≥ 40 points : ingrédient « qui fait la différence »
COMMON_MIN_FREQ = 0.20        # un ingrédient « commun » doit être présent dans ≥ 20 % des recettes

# Axe 2 — un pays a un profil « proche » si sa médiane est à ±20 % de la
# médiane globale. Pays retenus : au moins 20 recettes.
CONVERGENCE_BAND = 0.20
MIN_RECIPES_PER_COUNTRY = 20
CONVERGENCE_STRONG = 0.75     # ≥ 75 % des pays proches : « très proches »
CONVERGENCE_MAJORITY = 0.50   # ≥ 50 % : « la plupart »

# Axe 3 — force d'une corrélation de Spearman (repères usuels).
RHO_VERY_WEAK = 0.10
RHO_WEAK = 0.30
ALPHA = 0.05
SCATTER_SAMPLE_SIZE = 3000    # points affichés dans chaque nuage (calculs sur toutes les recettes)
RATING_DIFF_NEGLIGIBLE = 0.05  # écart de note moyenne < 0,05 étoile : « quasi identique »

# Axe 4 — effectif minimal pour afficher le pourcentage d'un pays.
MIN_RECIPES_AXE4 = 15


NUTRIENT_MEDIAN_PHRASE = {
    "calories": "calories médianes",
    "fat": "teneurs médianes en lipides",
    "carbs": "teneurs médianes en glucides",
    "protein": "teneurs médianes en protéines",
}


def _join_fr(items: list[str]) -> str:
    """['a', 'b', 'c'] -> 'a, b et c'."""
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " et " + items[-1]


def _cap(text: str) -> str:
    return text[:1].upper() + text[1:]


# ---------------------------------------------------------------------------
# Accueil — total dédupliqué
# ---------------------------------------------------------------------------

def deduplicated_total(overlap: pd.Series) -> int:
    """Nombre de recettes distinctes dans les deux tables (jointure sur l'URL)."""
    return int(overlap.n_all_recipes + overlap.n_cuisines - overlap.n_overlap)


# ---------------------------------------------------------------------------
# Axe 1 — base d'ingrédients
# ---------------------------------------------------------------------------

# Rapport « pays le plus représenté / pays médian » sous lequel on considère
# qu'aucun pays ne domine l'offre.
DOMINANCE_RATIO = 1.5


def build_insight_title_axe1_counts(by_country: pd.DataFrame, top_k: int = 3) -> tuple[str, str]:
    """Titre du classement des pays par nombre de recettes."""
    ranked = rank_countries(by_country)
    top = ranked.head(top_k)
    ratio = ranked["n_recipes"].max() / ranked["n_recipes"].median()
    names = _join_fr([country_label(c) for c in top["country"]])
    if ratio < DOMINANCE_RATIO:
        title = (f"Aucun pays ne domine : {names} en tête, avec {fmt_int(ranked['n_recipes'].max())} "
                 f"recettes contre {fmt_int(ranked['n_recipes'].median())} pour un pays médian")
    else:
        title = f"{names} concentrent l'offre de recettes étiquetées par pays"
    subtitle = f"Orange = les {top_k} pays en tête, signalés aussi sur la carte"
    return title, subtitle


def rank_countries(by_country: pd.DataFrame) -> pd.DataFrame:
    """Classement déterministe : nombre de recettes décroissant, puis nom."""
    return by_country.sort_values(["n_recipes", "country"], ascending=[False, True]).reset_index(drop=True)


def staple_spread(staples: pd.DataFrame, countries: list[str]) -> pd.DataFrame:
    """Par ingrédient : fréquence min / max / moyenne entre les pays choisis, et écart."""
    sub = staples[staples["country"].isin(countries)]
    out = (
        sub.groupby("ingredient")["pct_recipes"]
        .agg(freq_min="min", freq_max="max", freq_mean="mean")
        .assign(spread=lambda d: d["freq_max"] - d["freq_min"])
        .sort_values("spread")
        .reset_index()
    )
    return out


def build_insight_title_axe1(spread: pd.DataFrame, n_countries: int) -> tuple[str, str]:
    """Titre-insight du comparatif d'ingrédients.

    Formulation choisie selon le nombre d'ingrédients « communs » (écart
    ≤ COMMON_SPREAD_MAX et fréquence moyenne ≥ COMMON_MIN_FREQ) et
    « distinctifs » (écart ≥ DISTINCT_SPREAD_MIN).
    """
    if spread.empty or n_countries < 2:
        return ("Choisissez au moins deux pays pour comparer leurs ingrédients de base", "")
    common = spread[(spread["spread"] <= COMMON_SPREAD_MAX) & (spread["freq_mean"] >= COMMON_MIN_FREQ)]
    distinct = spread[spread["spread"] >= DISTINCT_SPREAD_MIN].sort_values("spread", ascending=False)
    common_names = [ingredient_label(i) for i in common["ingredient"]]
    distinct_names = [ingredient_label(i) for i in distinct["ingredient"]]

    verb = "revient" if len(common_names[:3]) == 1 else "reviennent"
    verb_d = "distingue" if len(distinct_names[:2]) == 1 else "distinguent"
    if len(common) >= len(spread) / 2:
        title = "Les mêmes ingrédients de base reviennent d'un pays à l'autre"
    elif common_names and distinct_names:
        title = (f"{_cap(_join_fr(common_names[:3]))} {verb} partout ; "
                 f"{_join_fr(distinct_names[:2])} {verb_d} davantage les pays")
    elif common_names:
        title = f"{_cap(_join_fr(common_names[:3]))} {verb} dans des proportions voisines d'un pays à l'autre"
    else:
        title = "Ces ingrédients de base varient nettement d'un pays à l'autre"

    # Sous-titre : l'ingrédient le plus homogène et le plus variable, chiffrés.
    lo, hi = spread.iloc[0], spread.iloc[-1]
    parts = [
        f"Écart le plus faible : {ingredient_label(lo.ingredient)} "
        f"(de {fmt_pct(lo.freq_min)} à {fmt_pct(lo.freq_max)} des recettes selon le pays)",
        f"le plus fort : {ingredient_label(hi.ingredient)} "
        f"(de {fmt_pct(hi.freq_min)} à {fmt_pct(hi.freq_max)})",
    ]
    subtitle = " ; ".join(parts)
    return title, subtitle


# ---------------------------------------------------------------------------
# Axe 2 — convergence des profils nutritionnels
# ---------------------------------------------------------------------------

def nutrient_convergence(mappable: pd.DataFrame, nutrient: str = "calories",
                         band: float = CONVERGENCE_BAND,
                         min_n: int = MIN_RECIPES_PER_COUNTRY) -> dict:
    """Part des pays dont la médiane est proche (±band) de la médiane globale."""
    valid = mappable.dropna(subset=[nutrient])
    global_median = float(valid[nutrient].median())
    per = valid.groupby("country")[nutrient].agg(["median", "count"])
    per = per[per["count"] >= min_n]
    rel = per["median"] / global_median - 1
    within = rel.abs() <= band
    most = rel.abs().idxmax() if len(rel) else None
    return {
        "nutrient": nutrient,
        "global_median": global_median,
        "n_countries": int(len(per)),
        "n_within": int(within.sum()),
        "share_within": float(within.mean()) if len(per) else float("nan"),
        "band": band,
        "most_distinct": most,
        "most_distinct_rel": float(rel.loc[most]) if most is not None else float("nan"),
        "n_missing": int(mappable[nutrient].isna().sum()),
        "n_total": int(len(mappable)),
    }


def build_insight_title_axe2(conv: dict) -> tuple[str, str]:
    """Titre-insight des boîtes à moustaches : bascule sur la part de pays proches."""
    phrase = NUTRIENT_MEDIAN_PHRASE[conv["nutrient"]]
    k, n, share = conv["n_within"], conv["n_countries"], conv["share_within"]
    band_txt = fmt_pct(conv["band"])
    if n == 0:
        return ("Pas assez de recettes par pays pour comparer les profils", "")
    if share >= CONVERGENCE_STRONG:
        title = f"Des profils très proches : {k} pays sur {n} ont des {phrase} à ±{band_txt} de la médiane globale"
    elif share >= CONVERGENCE_MAJORITY:
        title = f"La plupart des pays ({k} sur {n}) ont des {phrase} à ±{band_txt} de la médiane globale"
    else:
        title = f"Des profils contrastés : seuls {k} pays sur {n} ont des {phrase} à ±{band_txt} de la médiane globale"
    most = conv["most_distinct"]
    subtitle = (f"Le plus éloigné : {country_label(most)} "
                f"({fmt_signed(conv['most_distinct_rel'] * 100, 0)} % par rapport à la médiane globale). "
                f"Pays d'au moins {MIN_RECIPES_PER_COUNTRY} recettes ; sans distinction desserts / plats.")
    return title, subtitle


def build_key_message_axe2(conv: dict) -> str:
    """Conclusion de la page 2, conditionnée à la part de pays proches."""
    title, _ = build_insight_title_axe2(conv)
    if conv["n_countries"] and conv["share_within"] >= CONVERGENCE_MAJORITY:
        return f"<b>{title}.</b> Les recettes changent d'étiquette, beaucoup moins de profil."
    return f"<b>{title}.</b> Sur cette variable, l'étiquette va de pair avec un profil distinct."


def build_home_headline(conv: dict) -> str:
    """Accroche de l'accueil : affirmée seulement si la convergence est majoritaire."""
    if conv["n_countries"] and conv["share_within"] >= CONVERGENCE_MAJORITY:
        return "Les cuisines « du monde » en ligne se ressemblent plus qu'il n'y paraît"
    return "Les cuisines « du monde » en ligne se ressemblent-elles autant qu'on le dit ?"


# ---------------------------------------------------------------------------
# Axe 3 — notes et richesse
# ---------------------------------------------------------------------------

def spearman_summary(df: pd.DataFrame, x: str, y: str = "avg_rating") -> dict:
    d = df.dropna(subset=[x, y])
    if len(d) < 3:
        return {"rho": float("nan"), "p": float("nan"), "n": int(len(d))}
    rho, p = stats.spearmanr(d[x], d[y])
    return {"rho": float(rho), "p": float(p), "n": int(len(d))}


def correlation_strength(rho: float, p: float) -> str:
    """'tres_faible' | 'faible' | 'moderee' (non significatif => très faible)."""
    if np.isnan(rho) or p >= ALPHA or abs(rho) < RHO_VERY_WEAK:
        return "tres_faible"
    if abs(rho) < RHO_WEAK:
        return "faible"
    return "moderee"


def build_insight_title_axe3(corr: dict, var_phrase: str) -> tuple[str, str]:
    """Titre d'un nuage de points note × variable, selon la force réelle de ρ.

    `var_phrase` : la variable dans une phrase, ex. « en calories ».
    Jamais de formulation causale : « va de pair avec », « lien ».
    """
    rho, p, n = corr["rho"], corr["p"], corr["n"]
    strength = correlation_strength(rho, p)
    direction = "plus hautes" if rho > 0 else "plus basses"
    if strength == "tres_faible":
        title = f"Lien très faible entre la richesse {var_phrase} et la note"
    elif strength == "faible":
        title = f"Les recettes plus riches {var_phrase} vont de pair avec des notes légèrement {direction}"
    else:
        title = f"Les recettes plus riches {var_phrase} vont de pair avec des notes {direction}"
    signif = "non significatif" if p >= ALPHA else "significatif"
    subtitle = (f"Corrélation de rang (Spearman) ρ = {fmt_num(rho, 2)}, {signif} au seuil de 5 %, "
                f"sur {fmt_int(n)} recettes")
    return title, subtitle


def build_key_message_axe3(corrs: list[dict]) -> str:
    """Message clé de la page 3, à partir des deux corrélations."""
    strengths = [correlation_strength(c["rho"], c["p"]) for c in corrs]
    if all(s == "tres_faible" for s in strengths):
        return ("Pas vraiment : la note d'une recette n'est presque pas liée à sa richesse "
                "en calories ou en glucides. Les recettes riches ne sont pas « récompensées » "
                "par la communauté, et les recettes légères ne sont pas pénalisées.")
    if any(s == "moderee" for s in strengths):
        return ("En partie : les recettes plus riches vont de pair avec des notes différentes, "
                "sans que l'on puisse dire pourquoi (desserts, effet de sélection…).")
    return ("Très peu : le lien entre richesse et note existe mais reste faible ; "
            "la note dépend surtout d'autres choses que la composition nutritionnelle.")


def comfort_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """Note moyenne avec / sans ingrédient « réconfort », IC à 95 %."""
    d = df.dropna(subset=["avg_rating"])
    g = d.groupby("has_comfort_ingredient")["avg_rating"].agg(["mean", "std", "count"])
    g["ci95"] = 1.96 * g["std"] / np.sqrt(g["count"])
    g = g.reset_index()
    g["groupe"] = g["has_comfort_ingredient"].map(
        {True: "Avec beurre, crème, fromage ou bacon", False: "Sans ces ingrédients"})
    return g.sort_values("has_comfort_ingredient")


def build_insight_title_comfort(df: pd.DataFrame) -> tuple[str, str]:
    d = df.dropna(subset=["avg_rating"])
    with_ = d.loc[d["has_comfort_ingredient"], "avg_rating"]
    without = d.loc[~d["has_comfort_ingredient"], "avg_rating"]
    if len(with_) < 2 or len(without) < 2:
        return ("Pas assez de recettes pour comparer", "")
    diff = with_.mean() - without.mean()
    p = stats.ttest_ind(with_, without, equal_var=False).pvalue
    if abs(diff) < RATING_DIFF_NEGLIGIBLE or p >= ALPHA:
        title = "Avec ou sans beurre, crème ou fromage : des notes quasi identiques"
    elif diff > 0:
        title = "Les recettes avec beurre, crème ou fromage sont un peu mieux notées"
    else:
        title = "Les recettes avec beurre, crème ou fromage sont un peu moins bien notées"
    subtitle = (f"Écart de {fmt_signed(diff, 2)} étoile en moyenne "
                f"({'non significatif' if p >= ALPHA else 'significatif'} au seuil de 5 %)")
    return title, subtitle


# ---------------------------------------------------------------------------
# Axe 4 — alternatives saines et bien notées
# ---------------------------------------------------------------------------

def healthy_mask(df: pd.DataFrame, cal_max: float, fat_max: float,
                 rating_min: float, ratings_min: float) -> pd.Series:
    """Les valeurs manquantes (NaN) ne passent jamais le filtre."""
    return (
        (df["calories"] <= cal_max)
        & (df["fat"] <= fat_max)
        & (df["avg_rating"] >= rating_min)
        & (df["total_ratings"] >= ratings_min)
    )


def healthy_by_country(mappable: pd.DataFrame, mask: pd.Series,
                       min_n: int = MIN_RECIPES_AXE4) -> pd.DataFrame:
    out = (
        mappable.assign(_ok=mask)
        .groupby("country")
        .agg(n_total=("name", "count"), n_healthy=("_ok", "sum"))
        .assign(pct_healthy=lambda d: d["n_healthy"] / d["n_total"])
        .reset_index()
    )
    out = out[out["n_total"] >= min_n]
    return out.sort_values(["pct_healthy", "n_healthy"], ascending=False).reset_index(drop=True)


def build_insight_title_axe4(by_country: pd.DataFrame, top_k: int = 3) -> tuple[str, str]:
    if by_country.empty or by_country["n_healthy"].sum() == 0:
        return ("Avec ces critères, aucune recette étiquetée par pays ne passe le filtre",
                "Essayez d'assouplir les critères dans « Régler mes critères ».")
    top = by_country.head(top_k)
    names = _join_fr([country_label(c) for c in top["country"]])
    title = (f"{names} en tête : jusqu'à {fmt_pct(top['pct_healthy'].max())} "
             f"de leurs recettes sont saines et bien notées")
    subtitle = (f"Sur un pays type, environ {fmt_pct(by_country['pct_healthy'].median())} des recettes "
                f"(médiane des {len(by_country)} pays d'au moins {MIN_RECIPES_AXE4} recettes). "
                f"Petits effectifs : quelques recettes suffisent à changer le classement.")
    return title, subtitle


def threshold_rates(mappable: pd.DataFrame, flag_col: str, value_col: str,
                    countries: list[str]) -> tuple[pd.DataFrame, float]:
    """Part de recettes au-dessus d'un seuil, par pays et globale (valeurs connues seulement)."""
    known = mappable.dropna(subset=[value_col])
    global_rate = float(known[flag_col].mean())
    per = (known[known["country"].isin(countries)]
           .groupby("country")[flag_col].agg(rate="mean", n="count")
           .reset_index().sort_values("rate", ascending=False))
    return per, global_rate


def build_insight_title_axe2_thresholds(per: pd.DataFrame, global_rate: float,
                                        seuil_txt: str) -> tuple[str, str]:
    """Titre du graphique des dépassements de seuil (expander de la page 2)."""
    if per.empty:
        return ("Aucun pays à afficher", "")
    above = per[per["rate"] > global_rate]
    hi, lo = per.iloc[0], per.iloc[-1]
    title = (f"Recettes au-delà de {seuil_txt} : de {fmt_pct(lo.rate)} ({country_label(lo.country)}) "
             f"à {fmt_pct(hi.rate)} ({country_label(hi.country)})")
    subtitle = (f"{len(above)} pays sur {len(per)} au-dessus de la moyenne de l'ensemble "
                f"({fmt_pct(global_rate)}, trait vertical). Seuil indicatif, par portion.")
    return title, subtitle


def build_conclusion(conv: dict, corrs: list[dict], n_healthy: int,
                     n_countries_with: int, n_countries: int) -> str:
    """Conclusion du parcours : chaque clause n'apparaît que si son indicateur la soutient."""
    parts = []
    if conv["n_countries"] and conv["share_within"] >= CONVERGENCE_MAJORITY:
        parts.append("Les cuisines « du monde » ont des profils nutritionnels plus proches "
                     "que leurs étiquettes ne le laissent penser")
    else:
        parts.append("Les cuisines « du monde » gardent des profils nutritionnels en partie distincts")
    if all(correlation_strength(c["rho"], c["p"]) == "tres_faible" for c in corrs):
        parts.append("la note ne dit presque rien de la richesse d'un plat")
    else:
        parts.append("la note va de pair, faiblement, avec la richesse d'un plat")
    text = ", et ".join(parts) + "."
    if n_healthy:
        text += (f" Mais il n'est pas nécessaire de choisir entre plaisir et équilibre : "
                 f"**{fmt_int(n_healthy)} recettes** répondent aux deux, dans "
                 f"{fmt_int(n_countries_with)} des {fmt_int(n_countries)} pays comparés.")
    return text
