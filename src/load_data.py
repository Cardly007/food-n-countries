"""Chargement des données brutes. Chemins relatifs à la racine du repo."""

from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_CSV_DIR = DATA_DIR / "csv"
PROCESSED_DIR = DATA_DIR / "processed"

NUMERIC_COLS = [
    "calories", "fat", "carbs", "protein",
    "avg_rating", "total_ratings", "reviews",
    "prep_time", "cook_time", "total_time", "servings",
]


def _coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["date_published"] = pd.to_datetime(df["date_published"], errors="coerce")
    return df


@st.cache_data
def load_all_recipes() -> pd.DataFrame:
    df = pd.read_csv(RAW_CSV_DIR / "all_recipes.csv")
    return _coerce_types(df)


@st.cache_data
def load_cuisines() -> pd.DataFrame:
    df = pd.read_csv(RAW_CSV_DIR / "cuisines.csv")
    return _coerce_types(df)


@st.cache_data
def load_processed(name: str) -> pd.DataFrame:
    """Charge un fichier déjà pré-calculé par build_processed_data.py.

    Lève une erreur claire si le pipeline n'a pas encore été exécuté, plutôt
    que de planter avec un FileNotFoundError générique dans Streamlit.
    """
    path = PROCESSED_DIR / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} introuvable. Lancez d'abord : "
            f"python data_processing/build_processed_data.py"
        )
    return pd.read_parquet(path)
