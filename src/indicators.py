"""
Indicateurs calculés côté application à partir des parquets existants.

Le pipeline (data_processing/) n'est pas modifié. Les indicateurs ci-dessous
corrigent ou complètent `by_country.parquet` :

- `pct_exceeds_*` du pipeline comptent une valeur manquante comme « ne
  dépasse pas le seuil » (une comparaison avec NaN vaut False). Ici les
  parts sont calculées sur les seules recettes renseignées, et le nombre de
  valeurs manquantes est conservé pour être affiché.
- `pct_exceeds_carbs` n'existe pas dans `by_country.parquet` : il est
  calculé ici.
"""

import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

from src.labels import add_country_label
from src.load_data import load_processed
from src.nutrition import THRESHOLDS

NUTRIENTS = ["calories", "fat", "carbs", "protein"]

# Nuages de points de l'axe 3 : taille de l'échantillon dessiné et quantile
# au-delà duquel l'axe horizontal est coupé (cités aussi en Méthodologie).
SCATTER_SAMPLE_SIZE = 3000
SCATTER_X_CLIP_QUANTILE = 0.99
THRESHOLD_BY_NUTRIENT = {
    "calories": THRESHOLDS["calories_high"],
    "fat": THRESHOLDS["fat_high_g"],
    "carbs": THRESHOLDS["carbs_high_g"],
}


@st.cache_data
def dedup_totals() -> dict:
    """Totaux des deux tables et total dédupliqué (jointure sur l'URL)."""
    o = load_processed("overlap_stats").iloc[0]
    return {
        "n_all_recipes": int(o.n_all_recipes),
        "n_cuisines": int(o.n_cuisines),
        "n_overlap": int(o.n_overlap),
        "pct_overlap": float(o.pct_cuisines_in_all_recipes),
        "n_unique": int(o.n_all_recipes + o.n_cuisines - o.n_overlap),
    }


@st.cache_data
def cuisines() -> pd.DataFrame:
    """Recettes étiquetées par pays, avec libellé français `pays`."""
    return add_country_label(load_processed("cuisines_enriched"))


@st.cache_data
def mappable_cuisines() -> pd.DataFrame:
    """Recettes dont l'étiquette correspond à un pays unique."""
    df = cuisines()
    return df[df["map_type"] == "single_country"].copy()


@st.cache_data
def all_recipes() -> pd.DataFrame:
    return load_processed("all_recipes_enriched")


@st.cache_data
def country_summary() -> pd.DataFrame:
    """Agrégats par pays, robustes aux valeurs manquantes."""
    df = mappable_cuisines()
    rows = []
    for (country, pays, iso3), g in df.groupby(["country", "pays", "iso3"]):
        row = {
            "country": country, "pays": pays, "iso3": iso3,
            "n_recipes": len(g),
            "avg_rating": g["avg_rating"].mean(),
            "n_rated": g["avg_rating"].notna().sum(),
            "median_calories": g["calories"].median(),
            "median_fat": g["fat"].median(),
            "median_carbs": g["carbs"].median(),
            "avg_approx_n_items": g["approx_n_items"].mean(),
        }
        for nutrient, thr in THRESHOLD_BY_NUTRIENT.items():
            known = g[nutrient].dropna()
            row[f"pct_exceeds_{nutrient}"] = (known > thr).mean() if len(known) else np.nan
            row[f"n_known_{nutrient}"] = len(known)
            row[f"n_missing_{nutrient}"] = len(g) - len(known)
        row["pct_healthy_well_rated"] = g["is_healthy_and_well_rated"].mean()
        rows.append(row)
    return pd.DataFrame(rows)


def global_exceed_rate(nutrient: str) -> float:
    known = mappable_cuisines()[nutrient].dropna()
    return float((known > THRESHOLD_BY_NUTRIENT[nutrient]).mean())


@st.cache_data
def staples() -> pd.DataFrame:
    return add_country_label(load_processed("staple_frequency"))


@st.cache_data
def excluded_from_map() -> pd.DataFrame:
    return add_country_label(load_processed("excluded_from_map"))


def spearman(df: pd.DataFrame, x: str, y: str) -> dict:
    """ρ de Spearman sur les lignes où x et y sont renseignés."""
    d = df[[x, y]].dropna()
    if len(d) < 3:
        return {"rho": np.nan, "p": np.nan, "n": len(d)}
    rho, p = stats.spearmanr(d[x], d[y])
    return {"rho": float(rho), "p": float(p), "n": len(d)}


def describe_spearman(res: dict, x_label: str, y_label: str = "la note") -> str:
    """Phrase lisible décrivant un ρ de Spearman (sans conclusion imposée)."""
    rho, p, n = res["rho"], res["p"], res["n"]
    if np.isnan(rho):
        return "Pas assez de recettes renseignées pour mesurer une relation."
    a = abs(rho)
    strength = (
        "quasi nulle" if a < 0.1 else "faible" if a < 0.3
        else "modérée" if a < 0.5 else "forte"
    )
    if a < 0.1:
        trend = "ne varie quasiment pas"
    else:
        trend = "a tendance à augmenter" if rho > 0 else "a tendance à baisser"
    signif = (
        "cette relation est statistiquement distinguable du hasard"
        if p < 0.05 else "cette relation n'est pas distinguable du hasard"
    )
    n_txt = f"{n:,}".replace(",", " ")
    p_txt = "p < 0,001" if p < 0.001 else f"p = {p:.3f}".replace(".", ",")
    rho_txt = f"{rho:.2f}".replace(".", ",").replace("-", "\u2212")
    if a < 0.1 and p < 0.05:
        signif += (" ; avec autant de recettes, un écart minime devient détectable "
                   "sans être important en pratique")
    return (
        f"Quand {x_label} augmente, {y_label} {trend} : relation **{strength}** "
        f"(ρ de Spearman = {rho_txt} sur {n_txt} recettes ; ρ varie de −1 à +1, "
        f"0 signifiant aucune relation). Avec {p_txt}, {signif}."
    )


def mean_with_ci(s: pd.Series) -> dict:
    """Moyenne, effectif et intervalle de confiance à 95 % (loi de Student)."""
    s = s.dropna()
    n = len(s)
    mean = s.mean() if n else np.nan
    if n > 1:
        half = stats.t.ppf(0.975, n - 1) * s.std(ddof=1) / np.sqrt(n)
    else:
        half = np.nan
    return {"mean": mean, "n": n, "ci_low": mean - half, "ci_high": mean + half, "half": half}


def healthy_mask(df: pd.DataFrame, cal_max, fat_max, rating_min, ratings_min) -> pd.Series:
    """Recettes saines et bien notées selon des seuils choisis.

    Une recette dont une des 4 valeurs manque n'est pas retenue.
    """
    return (
        (df["calories"] <= cal_max)
        & (df["fat"] <= fat_max)
        & (df["avg_rating"] >= rating_min)
        & (df["total_ratings"] >= ratings_min)
    )


def n_missing_criteria(df: pd.DataFrame) -> int:
    """Nombre de recettes non évaluables (une des 4 valeurs manque)."""
    return int(df[["calories", "fat", "avg_rating", "total_ratings"]].isna().any(axis=1).sum())
