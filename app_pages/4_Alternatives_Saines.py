import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.insights import (
    MIN_RECIPES_AXE4, build_conclusion, build_insight_title_axe4, healthy_by_country,
    healthy_mask, nutrient_convergence, spearman_summary,
)
from src.load_data import load_processed
from src.nutrition import HEALTHY_CRITERIA
from src.story import key_message, next_button, step_header
from src.theme import (
    ACCENT, NEUTRAL, apply_theme, chart_title, country_label, fmt_int, fmt_num, fmt_pct, kpi, show,
)

STEP = 4
TOP_K = 3
DEFAULT_MIN_RATINGS = 10   # même filtre par défaut que la page 3
N_BARS = 15

all_recipes = load_processed("all_recipes_enriched")
cuisines = load_processed("cuisines_enriched")
mappable = cuisines[cuisines["map_type"] == "single_country"]
# Recettes distinctes des deux tables (une recette présente dans les deux
# n'est comptée qu'une fois).
distinct = pd.concat([all_recipes, cuisines]).drop_duplicates("url")


def build_healthy_bars(by_country, top_k=TOP_K, n=N_BARS):
    """Barres horizontales triées ; gris + accent orange sur les pays en tête."""
    df = by_country.head(n).iloc[::-1].assign(pays=lambda d: d["country"].map(country_label))
    top = set(by_country.head(top_k)["country"])
    colors = [ACCENT if c in top else NEUTRAL for c in df["country"]]
    fig = go.Figure(go.Bar(
        x=df["pct_healthy"], y=df["pays"], orientation="h", marker_color=colors,
        text=[f"{fmt_pct(p)} ({k}/{t})" for p, k, t in zip(df["pct_healthy"], df["n_healthy"], df["n_total"])],
        textposition="outside", cliponaxis=False,
        hovertemplate="%{y} : %{x:.0%} des recettes<extra></extra>",
    ))
    apply_theme(fig, height=34 * len(df) + 80)
    fig.update_xaxes(range=[0, max(df["pct_healthy"].max(), 0.01) * 1.3], tickformat=".0%",
                     title="Part des recettes du pays, saines et bien notées")
    return fig


step_header(STEP)
st.title("Bonne nouvelle : des alternatives existent")

# Critères : valeurs par défaut = compromis raisonnable défini dans src/nutrition.py.
crit = {
    "cal_max": st.session_state.get("axe4_cal", HEALTHY_CRITERIA["calories_max"]),
    "fat_max": st.session_state.get("axe4_fat", HEALTHY_CRITERIA["fat_max_g"]),
    "rating_min": st.session_state.get("axe4_rating", HEALTHY_CRITERIA["min_rating"]),
    "ratings_min": st.session_state.get("axe4_n", HEALTHY_CRITERIA["min_total_ratings"]),
}
crit_txt = (f"au plus {fmt_int(crit['cal_max'])} kcal et {fmt_int(crit['fat_max'])} g de lipides "
            f"par portion, note d'au moins {fmt_num(crit['rating_min'], 1)} / 5 "
            f"avec au moins {fmt_int(crit['ratings_min'])} avis")


def _mask(df):
    return healthy_mask(df, crit["cal_max"], crit["fat_max"], crit["rating_min"], crit["ratings_min"])


n_healthy = int(_mask(distinct).sum())
n_healthy_mappable = int(_mask(mappable).sum())
by_country = healthy_by_country(mappable, _mask(mappable))

if n_healthy:
    key_message(
        f"<b>{fmt_int(n_healthy)} recettes</b> sont à la fois légères et plébiscitées par les "
        f"internautes, soit {fmt_pct(n_healthy / len(distinct))} des recettes du site analysées."
    )
else:
    key_message("Avec ces critères, aucune recette ne passe le filtre : essayez de les assouplir.")

st.caption(f"Critères retenus : {crit_txt}.")

c1, c2 = st.columns(2)
with c1:
    kpi("Recettes saines et bien notées", fmt_int(n_healthy),
        help="Toutes les recettes analysées, chacune comptée une fois.",
        subtitle=f"{fmt_pct(n_healthy / len(distinct), 1)} des {fmt_int(len(distinct))} recettes")
with c2:
    kpi("Dont recettes étiquetées par pays", fmt_int(n_healthy_mappable),
        help="Recettes dont l'étiquette correspond à un seul pays.",
        subtitle=f"{fmt_pct(n_healthy_mappable / len(mappable), 1)} des {fmt_int(len(mappable))} recettes")

title, subtitle = build_insight_title_axe4(by_country, TOP_K)
chart_title(
    title,
    f"{subtitle} Orange = les {TOP_K} pays en tête ; entre parenthèses, recettes retenues / recettes "
    f"du pays. {N_BARS} premiers pays sur {len(by_country)} (au moins {MIN_RECIPES_AXE4} recettes). "
    "Les recettes sans calories, lipides ou note ne peuvent pas être retenues.",
)
show(build_healthy_bars(by_country))

with st.expander("Régler mes critères"):
    a, b = st.columns(2)
    a.slider("Calories maximum par portion (kcal)", 100, 1500, step=50, key="axe4_cal",
             value=HEALTHY_CRITERIA["calories_max"])
    b.slider("Lipides maximum par portion (g)", 0, 100, step=5, key="axe4_fat",
             value=HEALTHY_CRITERIA["fat_max_g"])
    a.slider("Note minimum", 3.0, 5.0, step=0.1, key="axe4_rating",
             value=float(HEALTHY_CRITERIA["min_rating"]))
    b.slider("Nombre minimum d'avis", 0, 500, step=10, key="axe4_n",
             value=HEALTHY_CRITERIA["min_total_ratings"])
    st.caption("Repères indicatifs pour un adulte (environ 2 000 kcal par jour), pas des normes médicales.")

with st.expander("Voir les recettes"):
    rec = mappable[_mask(mappable)].sort_values(["avg_rating", "total_ratings"], ascending=False)
    st.dataframe(
        rec.assign(pays=rec["country"].map(country_label))[
            ["name", "pays", "calories", "fat", "avg_rating", "total_ratings", "url"]],
        column_config={
            "name": "Recette", "pays": "Pays",
            "calories": st.column_config.NumberColumn("Calories (kcal / portion)", format="%d"),
            "fat": st.column_config.NumberColumn("Lipides (g / portion)", format="%d"),
            "avg_rating": st.column_config.NumberColumn("Note (sur 5)", format="%.1f"),
            "total_ratings": st.column_config.NumberColumn("Avis", format="%d"),
            "url": st.column_config.LinkColumn("Lien", display_text="Voir la recette"),
        },
        width="stretch", hide_index=True,
    )

st.subheader("En résumé")
corrs = [spearman_summary(all_recipes[all_recipes["total_ratings"] >= DEFAULT_MIN_RATINGS], x)
         for x in ("calories", "carbs")]
st.markdown(build_conclusion(
    nutrient_convergence(mappable, "calories"), corrs, n_healthy,
    int((by_country["n_healthy"] > 0).sum()), len(by_country),
))

next_button(STEP)
