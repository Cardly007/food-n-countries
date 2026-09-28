# Pipeline d'Enrichissement des Données (NLP & LLM)

Ce dossier contient un pipeline de transformation en 3 étapes pour enrichir et nettoyer nos jeux de données `all_recipes` et `cuisines`. 
Le but est de palier le manque de données géographiques (pays) sur la majorité des recettes, de classifier les recettes (Dessert, Plat principal...), et d'obtenir des mesures précises des ingrédients.

## Les 3 étapes du pipeline

### Étape 1 : `01_mapping_and_merge.py`
**Rôle :** Fusionner les sources et appliquer un mapping probabiliste.
- Fusionne `all_recipes.csv` (16k) et `cuisines.csv` (2k).
- Supprime les doublons en se basant sur l'URL de la recette.
- Applique des règles de "redressement géographique". Par exemple, une recette estampillée "Tex-Mex" ou "Jewish" ne correspond pas à un pays ISO-3 par défaut. Le script les réassigne au pays le plus probable (USA, Israël, etc.) pour qu'elles apparaissent sur la carte choroplèthe.

### Étape 2 : `02_nlp_ingredients.py`
**Rôle :** Traitement local du langage naturel pour l'analyse des ingrédients.
- Utilise la bibliothèque `ingredient-parser-nlp` (modèle CRF).
- Extrait la "racine" de l'ingrédient (transforme `"1 1/2 cup finely chopped brown sugar"` en `"brown sugar"`).
- Compte le nombre exact d'ingrédients (en excluant les erreurs liées aux virgules dans le texte d'origine).
- Détecte avec précision la présence de sucres ajoutés via l'analyse du nom extrait (`has_added_sugar_nlp`).
*Avantage : Fonctionne à 100% en local, sans consommer de tokens API.*

### Étape 3 : `03_llm_enrichment.py`
**Rôle :** Catégorisation par Intelligence Artificielle.
- Lit les recettes qui n'ont toujours **pas de pays** attitré.
- Envoie le Titre et la Liste des ingrédients à une API LLM (Gemini par défaut, OpenRouter en fallback).
- Demande au modèle de deviner :
  1. Le code ISO-3 du pays d'origine probable.
  2. La catégorie du plat (Dessert, Main Dish, Starter...).
- **Résilience (Reprise) :** Chaque réponse de l'API est sauvegardée instantanément dans un fichier `03_enriched_checkpoint.jsonl`. En cas d'erreur réseau, d'interruption ou de limite atteinte (Rate Limit), le script peut être relancé et reprendra exactement là où il s'est arrêté, sans refaire les requêtes précédentes.

## Prérequis et Installation

1. S'assurer d'avoir les librairies nécessaires :
```bash
pip install pandas python-dotenv requests ingredient-parser-nlp
```

2. Configurer les clés API :
- Copier le fichier `.env.example` et le renommer en `.env`.
- Insérer les clés `GEMINI_API_KEY` et `OPENROUTER_API_KEY`.
*(Le fichier `.env` est ignoré par Git pour des raisons de sécurité).*

## Exécution

Lancez les scripts dans l'ordre depuis la racine du projet :
```bash
python data_processing/pipeline/01_mapping_and_merge.py
python data_processing/pipeline/02_nlp_ingredients.py
python data_processing/pipeline/03_llm_enrichment.py
```

Le fichier final sera généré dans `data/processed/03_final_dataset.parquet`.
