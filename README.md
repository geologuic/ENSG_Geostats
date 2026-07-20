# Développement de notebooks Jupyter pour l'enseignement de la géostatistique

**Projet de Fin d'Études (stage)** — Master 2 Géologie Numérique, ENSG.

Ce dépôt reproduit en **Python** (`gstlearn`, `scikit-gstat`, `gstatsim`) les TD **TD5 à TD8** du module « Traitement statistique, géostatistique et approche systèmes » (ENSG 2A — S7), réalisés à l'origine sous **SKUA-Gocad**.

**Chaîne géostatistique couverte** : Exploration (TD5) → Anamorphose gaussienne → Variogramme (TD6) → Krigeage & simulation (TD7) → Étude de cas pollution (TD8) → Comparaison Machine Learning → Simulation non-stationnaire.

---

## Structure du projet

```
TD6-GEOSTAT-PFE-GN-ENSG/
├── data/
│   ├── juradata.csv                  # 259 points, Pb + 6 autres métaux, RockType/Landuse
│   ├── JuraValidationData.csv        # 100 points de validation indépendants
│   └── prix_or_1D.csv, image_2D_grille.csv, gold_2D_points.csv   (volet Or)
├── src/
│   ├── geostat_utils/                # package factorisé (io, variogram, kriging, simulation)
│   └── notebooks/
│       ├── jura/                     # 01 à 06 (TD5 → TD8 + ML + non-stationnaire)
│       └── gold_td6/                 # 3 exercices indépendants (TD6)
├── tests/test_geostat_utils.py
├── requirements.txt
└── README.md
```

### Package `geostat_utils`

Fonctions communes factorisées (`import geostat_utils as gutils`) :
- **`io.py`** : chargement, création de `Db` gstlearn, filtrage, anamorphose gaussienne, grille, sauvegarde des résultats de krigeage
- **`variogram.py`** : affichage et calage manuel interactif du variogramme
- **`kriging.py`** : krigeage SK/OK/UK + widget de visualisation
- **`simulation.py`** : simulation par bandes tournantes (TBS) + widgets de réalisations

---

## Notebooks — Volet Jura (`src/notebooks/jura/`)

| # | TD | Contenu |
|---|---|---|
| 01 | TD5 | Statistiques, anomalies, corrélations, régions (RockType/Landuse) |
| 02 | TD6 | Filtrage des aberrants + anamorphose gaussienne ( `Pb `en` Y.Pb`) |
| 03 | TD6 | Variogramme expérimental, modélisation, anisotropie |
| 04 | TD7+TD8 | Krigeage (SK/OK/UK), simulation TBS, superficie polluée, RMSE validation |
| 05 | TD8 (ext.) | Comparaison krigeage vs ML (Random Forest, XGBoost, CatBoost) |
| 06 | Complément | Simulation SGS non-stationnaire (clustering par Landuse) |

**Volet Or** (`src/notebooks/gold_td6/`, TD6, 3 exercices indépendants) : variogramme 1D (prix de l'or), variogramme 2D sur grille image, krigeage/simulation sur nuage de points.

---

## Installation

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

> *note* : `numpy<2.0` obligatoire — `gstatsim` (notebook 06) est incompatible avec NumPy 2.x.

---

## Exécution

- **Volet Jura** : lancer dans l'ordre 01 → 06 (le notebook 05 dépend de `rmse_krigeage.json`, généré par le notebook 04).
- **Volet Or** : les 3 exercices sont indépendants.

---

## Tests

```bash
pytest tests/ -v
```

---

## Bibliothèques principales

pandas, numpy (`<2.0`), matplotlib, ipywidgets, **gstlearn** (géostatistique), **scikit-gstat** + **gstatsim** (notebook 06), **scikit-learn**, **xgboost**, **catboost** (notebook 05), pytest.

---

## Auteur

**RAZIK OUMAYMA** — Master 2 Géologie Numérique, ENSG.

## Sources principales

- gstlearn — MINES Paris–PSL University (2025). Zenodo. https://doi.org/10.5281/zenodo.13343742
- Jeu de données Jura — Goovaerts, P. (1997). *Geostatistics for Natural Resources Evaluation*. Oxford University Press.
- RMSE — Chai, T., Draxler, R. R. (2014). *Geoscientific Model Development*, 7, 1247–1250. https://doi.org/10.5194/gmd-7-1247-2014
- scikit-gstat — Mälicke, M. (2022). *Geoscientific Model Development*, 15(6), 2505–2532.
- GStatSim — MacKie, E. et al. (2022). https://gatorglaciology.github.io/gstatsimbook/
- scikit-learn — Pedregosa, F. et al. (2011). *Journal of Machine Learning Research*, 12, 2825–2830. https://scikit-learn.org/