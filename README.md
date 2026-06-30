# Développement de notebooks Jupyter en Python pour l'enseignement de la géostatistique et l'estimation de ressources minérales

**Projet de Fin d'Études (stage)** — Master 2 **Géologie Numérique**, ENSG.

Ce dépôt correspond au **TD6** du projet : une série de notebooks pédagogiques reproduisant en **Python** (avec la bibliothèque **gstlearn**) un TD du module **
« Traitement statistique, géostatistique et approche systèmes »** (ENSG 2A — S7), réalisé à l'origine dans le logiciel **SKUA-Gocad**.

Le travail est organisé en **deux volets**, qui suivent la même chaîne géostatistique sur des jeux de données différents :

- **Volet Jura** — étude du **Plomb (Pb)** dans les sols (données 2D dispersées).
- **Volet Or** — étude du **prix de l'or** et de variables `Values`, en 1D, en grille 2D et en nuage de points 2D.

---

## Objectif

Parcourir la chaîne géostatistique complète, de l'exploration des données jusqu'à l'estimation et la simulation :

**Exploration → Anamorphose gaussienne → Variogramme → Krigeage & Simulation.**

---

## Données

| Fichier (`data/`) | Volet | Description | Variable étudiée |
|---|---|---|---|
| `juradata.csv` | Jura | 259 échantillons de sol 2D, coordonnées X/Y (km) | **Pb** (Plomb) en mg/kg |
| `prix_or_1D.csv` | Or | Série **1D** de 4 174 valeurs le long de l'axe `MD` | **GoldPrice** ($/once) |
| `image_2D_grille.csv` | Or | Grille image **2D** (Voxet 100×100 = 10 000 cellules) | **Values** |
| `gold_2D_points.csv` | Or | Nuage de **274 points 2D** dispersés | **Values** (normalisée) |

> `TD6_support_etudiant_2025.pptx` : support de cours d'origine (référence).

---

## Structure du projet

```
TD6-GEOSTAT-PFE-GN-ENSG/
├── data/
│   ├── juradata.csv                              
│   ├── prix_or_1D.csv                            
│   ├── image_2D_grille.csv                       
│   ├── gold_2D_points.csv                        
│   └── TD6_support_etudiant_2025.pptx            
├── src/
│   ├── geostat_utils.py                          (factorisation)
│   └── notebooks/
│       ├── jura/                                 # Volet Jura (Plomb)
│       │   ├── 01_chargement_exploration.ipynb
│       │   ├── 02_anamorphose_gaussienne.ipynb
│       │   ├── 03_variogramme_modelisation.ipynb
│       │   └── 04_krigeage_simulation.ipynb
│       └── gold_td6/                             # Volet Or (3 exercices)
│           ├── 01_exercice1_variogramme_1D.ipynb
│           ├── 02_exercice2_variogramme_2D_grille.ipynb
│           └── 03_exercice3_krigeage_simulation.ipynb
├── outputs/
│   └── gold/                                     # Figures PNG exportées par le volet Or
├── requirements.txt
├── .gitignore
└── README.md
```

### Le module `geostat_utils.py`

Pour éviter de répéter le même code (principe **DRY** — *Don't Repeat Yourself*), les fonctions communes aux **deux volets** sont **factorisées** dans un module Python unique, importé via :

```python
import geostat_utils as gutils
```

| Fonction | Rôle |
|---|---|
| `charger_donnees_jura(...)` | Charge le CSV Jura et convertit les coordonnées en km |
| `creer_db_gstlearn(df, variables, noms_locators)` | Crée une base `Db` gstlearn depuis un DataFrame (générique : 1D ou 2D) |
| `filtrer_valeurs_aberrantes(db, nom_colonne, seuil)` | Masque les valeurs au-dessus d'un seuil |
| `preparer_db_gaussienne()` | Pipeline Jura : chargement + filtrage + anamorphose de Hermite (→ `Y.Pb`) |
| `creer_grille(df, nx, ny)` | Crée la grille d'estimation (`DbGrid`) sur l'emprise des données |
| `afficher_variogramme(vario, model, titre, variance, unite, chemin_fichier)` | Trace variogramme + modèle ; `unite` = "km"/"m", sauvegarde PNG optionnelle |

> **Note d'import.** Les deux volets étant dans un sous-dossier de `src/notebooks/` (`jura/` ou `gold_td6/`), les notebooks remontent de deux niveaux pour atteindre le module : `sys.path.append(os.path.abspath(os.path.join("..", "..")))`. Le chargement des données Jura (`charger_donnees_jura`) reste robuste car il teste plusieurs chemins et un chemin absolu basé sur l'emplacement du module.

---

## Contenu des notebooks

### Volet Jura — `src/notebooks/jura/`

| Notebook | Étape | Description |
|---|---|---|
| **01** | Chargement & exploration | Lecture des données, carte spatiale et statistiques du Pb |
| **02** | Anamorphose gaussienne | Filtrage des aberrants et transformation du Pb en variable gaussienne **Y.Pb** |
| **03** | Variogramme & modélisation | Variogramme expérimental et ajustement du modèle **Nugget + Sphérique** |
| **04** | Krigeage & simulation | Krigeage (SK, OK, UK) et simulations par **bandes tournantes** |

### Volet Or — `src/notebooks/gold_td6/`

| Exercice | Données | Description |
|---|---|---|
| **01** | `prix_or_1D.csv` | Exploration et **variogramme 1D** du prix de l'or (GoldPrice) |
| **02** | `image_2D_grille.csv` | **Variogramme 2D** sur grille image (Voxet) et anisotropie |
| **03** | `gold_2D_points.csv` | **Variogramme 2D**, **krigeage** (SK, OK, UK) et **simulation TBS** sur nuage de points |

> Les figures du volet Or sont exportées automatiquement dans `outputs/gold/`.

---

## Installation

1. (Recommandé) Créer un environnement virtuel :
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   # source venv/bin/activate # Linux / Mac
   ```

2. Installer les bibliothèques nécessaires :
   ```bash
   pip install -r requirements.txt
   ```

---

## Exécution

- **Volet Jura** : lancer les notebooks **dans l'ordre** (01 >> 02 >> 03 >>04) depuis `src/notebooks/jura/`.
- **Volet Or** : les 3 exercices sont **indépendants** et peuvent être lancés séparément depuis `src/notebooks/gold_td6/`.

Chaque notebook est **autonome** : il reconstruit le contexte nécessaire en réutilisant le module `geostat_utils.py`. Il n'est donc pas obligatoire de garder les notebooks précédents ouverts.

> Pour un affichage correct des **widgets interactifs** (variogramme manuel, cartes de krigeage), exécuter les cellules dans l'ordre et, en cas de besoin, relancer le kernel (**Restart & Run All**).

---

## Bibliothèques utilisées

- **pandas** — chargement et manipulation des données
- **numpy** — calculs numériques et statistiques
- **matplotlib** — visualisation
- **ipywidgets** — réglages interactifs (variogramme, cartes de krigeage)
- **gstlearn** — analyses géostatistiques (variogramme, krigeage, simulation)

---

## Auteur

Projet réalisé par **RAZIK OUMAYMA** — Master 2 Géologie Numérique, ENSG.
