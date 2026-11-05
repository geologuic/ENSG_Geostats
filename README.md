# Notebooks Jupyter en Python pour le cours de Géostatistique ENSG

*Auteurs: Oumayma Razik, Guillaume Caumon*

Ce dépôt propose des exercices pour les TDs de 2eme année à l'ENSG en géostatistique. 
Il s'appuie sur la bibliothèque [gstlearn](https://gstlearn.org/). Il complémente les TDs existants sur AspenSKUA.

## Installation

Il est recommandé de créer un environnement virtuel python incluant les dépendances. 

Pour cela lancer PyCharm, puis ouvrir le répertoire courant. Aller dans `Setting.. > Python > Interpreter`, puis sélectionner 
`Add Interpreter > Add Local Interpreter`. Une boîte de dialogue s'ouvre. 
Il faut générer un nouvel environnement (`Generate New`), de type `uv` (le plus rapide), et choisir le répertoire courant. 
Puis, ouvrir un terminal et lancer 
```
uv pip install -r requirements.txt
```
 

Cela peut se également se faire sous Linux ou Windows en ligne de commande: 

```
uv venv                     # Ou: python -m venv .venv
.venv\Scripts\activate      # Windows
uv pip install -r requirements.txt
jupyter-notebook.exe 
```

## TD6

 - [Calcul de variogramme en 1D](TD06Geostat/01_variogramme1D.ipynb)
 - [Calcul de variogramme en 2D](TD06Geostat/02_variogramme2D.ipynb)

## Structure du projet

```
TD6-GEOSTAT-PFE-GN-ENSG/
├── data/                       # Les fichiers de données
├── geostat_utils/              # package d'utilitaires python (io, variogram, kriging, simulation)
├── start.ipynb                 # Le Notebook de démarrage
├── TD*/
│    └── *.ipynb                # Notebooks python pour les TDs
├── tests/test_geostat_utils.py # Tests
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


## Tests

```bash
pytest tests/ -v
```

---

## Sources principales

- gstlearn — MINES Paris–PSL University (2025). Zenodo. https://doi.org/10.5281/zenodo.13343742
- Jeu de données Jura — Goovaerts, P. (1997). *Geostatistics for Natural Resources Evaluation*. Oxford University Press.
- RMSE — Chai, T., Draxler, R. R. (2014). *Geoscientific Model Development*, 7, 1247–1250. https://doi.org/10.5194/gmd-7-1247-2014
- scikit-gstat — Mälicke, M. (2022). *Geoscientific Model Development*, 15(6), 2505–2532.
- GStatSim — MacKie, E. et al. (2022). https://gatorglaciology.github.io/gstatsimbook/
- scikit-learn (exemple ColumnTransformer) — The scikit-learn developers. *Column Transformer with Mixed Types*. https://scikit-learn.org/stable/auto_examples/compose/plot_column_transformer_mixed_types.html
- pandas — Documentation de manipulation de données tabulaires (chargement, filtrage, jointures des jeux de données Jura). https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html
- matplotlib — Documentation des raccourcis de mise en forme utilisés pour l'ensemble des figures du rapport. https://matplotlib.org/stable/tutorials/coding_shortcuts.html