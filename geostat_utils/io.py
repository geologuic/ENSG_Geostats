"""
geostat_utils.io
=================

Auteur: Oumayma Razik — PFE ENSG 2025-2026
Révisions: Guilaume Caumon.

Fonctions liées à l'entrée/sortie et à la préparation des données :
- chargement de fichiers CSV (générique + wrapper spécifique Jura pour compatibilité)
- création d'un objet Db gstlearn depuis un DataFrame
- filtrage des valeurs aberrantes
- transformation gaussienne (anamorphose de Hermite)
- création d'une grille d'estimation
"""

from pathlib import Path
from typing import *
import re

import pandas as pd
import gstlearn as gl
import matplotlib.pyplot as plt
import json

# ==========================================================================
# Constantes du projet (jeu de données Jura)
# ==========================================================================

SEUIL_ABERRANT_PB_DEFAUT = 132    # seuil (mg/kg) au-delà duquel une valeur de Pb est jugée aberrante
NB_POLYNOMES_HERMITE_DEFAUT = 25  # nombre de polynômes de Hermite pour l'anamorphose gaussienne

class ResultsDir:
    _shared_state = {}
    def __init__(self, output_dir: str):
        self.__dict__ = self._shared_state  # Share state across instances
        if not hasattr(self, "_output_dir"):  # Initialize only once
            self._output_dir = Path(output_dir).absolute()
            self._output_dir.mkdir(parents=True, exist_ok=True)

    def save_fig(self, name: str, *args: Any, **kwargs: Any) -> None:
        """Save a matplotlib figure to the output directory.

        Args:
            name: Filename (e.g., "plot.png").
            *args: Additional positional arguments for `plt.savefig`.
            **kwargs: Additional keyword arguments for `plt.savefig` (e.g., dpi=300).
        """
        if not re.match(r'^[\w\-.]+$', name):
            raise ValueError(f"Invalid filename: {name}")
        filepath = self._output_dir / name
        plt.savefig(filepath, *args, **kwargs)

    def save_data(self, data: Any, name: str, **kwargs: Any) -> None:
        """Save data to a file (e.g., CSV, JSON, pickle)."""
        if not re.match(r'^[\w\-.]+$', name):
            raise ValueError(f"Invalid filename: {name}")
        filepath = self._output_dir / name
        if name.endswith('.csv'):
            pd.DataFrame(data).to_csv(filepath, **kwargs)
        elif name.endswith('.json'):
            import json
            with open(filepath, 'w') as f:
                json.dump(data, f, **kwargs)
        else:
            raise ValueError(f"Unsupported file format: {name}")

# ==========================================================================
# Chargement des données
# ==========================================================================

def charger_donnees(chemin_fichier: Path, chemins_alternatifs: Path=None, colonnes_km=None, separateur=";"):
    """Charge un fichier CSV en testant plusieurs chemins possibles, et convertit
    optionnellement certaines colonnes de mètres en kilomètres.

    Paramètres
    ----------
    chemin_fichier : str
        Chemin principal à tester en premier.
    chemins_alternatifs : list[str] ou None
        Autres chemins à tester si le premier n'existe pas (utile car un notebook
        peut être lancé depuis des dossiers de profondeur différente).
    colonnes_km : list[str] ou None
        Colonnes à diviser par 1000 (conversion mètres -> kilomètres). Si None,
        aucune conversion n'est appliquée.
    separateur : str
        Séparateur du CSV (";" par défaut, cohérent avec les jeux de données du TD6).

    Retourne
    --------
    pandas.DataFrame
    """
    chemins_a_tester = [chemin_fichier] + (chemins_alternatifs or [])

    for chemin in chemins_a_tester:
        if chemin.exists():
            donnees = pd.read_csv(chemin, sep=separateur)
            if colonnes_km:
                for colonne in colonnes_km:
                    donnees[colonne] = donnees[colonne] / 1000.0
            return donnees

    raise FileNotFoundError(f"Fichier introuvable. Chemins testés : {chemins_a_tester}")


def charger_donnees_jura(chemin_fichier="../../data/juradata.csv"):
    """Wrapper de compatibilité : charge le jeu de données Jura.

    NOTE : le fichier `juradata.csv` corrigé contient déjà les
    coordonnées X et Y en kilomètres (ex. X=2.386, Y=3.077). Aucune conversion
    mètres -> km n'est donc appliquée ici (`colonnes_km=None`). Si un jour vous
    repassez à une source de données en mètres, remettez `colonnes_km=["X", "Y"]`.

    Conservé tel quel pour ne pas casser les notebooks existants (01, 02, 03 - Jura).
    En interne, s'appuie sur la fonction générique `charger_donnees`.
    """
    chemins_alternatifs = [
        Path("..")/".."/"data"/"juradata.csv",
        Path("..")/".."/".."/"data"/"juradata.csv",  # depuis src/notebooks/jura/
        Path("data")/ "juradata.csv",
        Path(__file__)/".."/".."/"data"/"juradata.csv",
    ]
    return charger_donnees(
        chemin_fichier,
        chemins_alternatifs=chemins_alternatifs,
        colonnes_km=None,  # ["X", "Y"] déjà en km dans le fichier corrigé -> pas de conversion
        separateur=";",
    )

# ==========================================================================
# Création de la base de données gstlearn
# ==========================================================================
def creer_db_gstlearn(df, variables=None, noms_locators=None):
    """Crée un objet Db de gstlearn à partir d'un tableau pandas (DataFrame).

    Les "locators" indiquent le rôle de chaque colonne :
    x1, x2 (...) = coordonnées ; z1 = variable étudiée.
    Fonctionne aussi bien en 1D (ex. GoldPrice) qu'en 2D (Jura, Gold 2D).

    Paramètres
    ----------
    df : pandas.DataFrame
        Tableau contenant au moins les colonnes listées dans `variables`.
    variables : list[str] ou None
        Colonnes de `df` à utiliser, dans l'ordre. Par défaut : jeu Jura ["X","Y","Pb"].
    noms_locators : list[str] ou None
        Locators gstlearn associés à `variables`, même ordre/longueur.
        Par défaut : ["x1", "x2", "z1"] (2 coordonnées + 1 variable).

    Retourne
    --------
    gl.Db
        Base de données gstlearn prête à l'emploi (coordonnées + variable étudiée).

    Lève
    ----
    ValueError
        Si `variables` et `noms_locators` n'ont pas la même longueur.
    """
    # On évite les listes en valeur par défaut (mutable default argument) :
    # elles sont construites ici, dans le corps de la fonction.
    if variables is None:
        variables = ["X", "Y", "Pb"]
    if noms_locators is None:
        noms_locators = ["x1", "x2", "z1"]
    if len(variables) != len(noms_locators):
        raise ValueError(
            f"`variables` ({len(variables)} éléments) et `noms_locators` "
            f"({len(noms_locators)} éléments) doivent avoir la même longueur."
        )

    donnees = df[variables].to_numpy()
    nombre_echantillons = donnees.shape[0]
    db = gl.Db.createFromSamples(
        nombre_echantillons,
        tab=donnees.flatten(),
        names=variables,
        locatorNames=noms_locators
    )
    return db

def filtrer_valeurs_aberrantes(db, nom_colonne, seuil):
    """Filtre les valeurs aberrantes en ajoutant une sélection : on ne garde
    que les valeurs strictement inférieures au seuil.

    Paramètres
    ----------
    db : gl.Db
        Base gstlearn contenant la colonne à filtrer.
    nom_colonne : str
        Nom de la colonne sur laquelle appliquer le seuil (ex. "Pb").
    seuil : float
        Valeur limite (exclue) : seules les valeurs strictement inférieures
        à `seuil` sont conservées dans la sélection.

    Retourne
    --------
    int
        Identifiant de la sélection créée dans `db` (rang de la colonne
        de sélection ajoutée).
    """
    valeurs = db.getColumn(nom_colonne)
    id_selection = db.addSelection(valeurs < seuil)
    return id_selection

# ==========================================================================
# Anamorphose gaussienne (transformation Normal Score / Hermite)
# ==========================================================================

def anamorphose_gaussienne(db, nom_variable, nb_polynomes=NB_POLYNOMES_HERMITE_DEFAUT):
    """Applique une anamorphose gaussienne (polynômes de Hermite) à une variable
    d'un Db déjà créé, et la définit comme variable active (locator Z).

    Fonction générique : ne dépend d'aucun nom de variable ou de jeu de données
    particulier (contrairement à `preparer_db_gaussienne_jura`).

    Paramètres
    ----------
    db : gl.Db
        Base gstlearn contenant déjà la variable `nom_variable`.
    nom_variable : str
        Nom de la variable brute à transformer (ex. "Pb", "Values").
    nb_polynomes : int
        Nombre de polynômes de Hermite utilisés pour l'ajustement (25 par défaut).

    Retourne
    --------
    tuple : (db, anam_hermite)
        db modifié en place (une nouvelle colonne "Y.<nom_variable>" est ajoutée),
        et l'objet d'anamorphose (utile pour la back-transformation ultérieure).
    """
    db.setLocator(nom_variable, gl.ELoc.Z)
    anam_hermite = gl.AnamHermite(nb_polynomes)
    anam_hermite.fitFromLocator(db)
    anam_hermite.rawToGaussianByLocator(db)
    db.setLocator(f"Y.{nom_variable}", gl.ELoc.Z)
    return db, anam_hermite


def preparer_db_gaussienne_jura(seuil_aberrant=SEUIL_ABERRANT_PB_DEFAUT):
    """Wrapper de compatibilité (ancien nom : `preparer_db_gaussienne`) : reproduit
    la chaîne complète spécifique au TD Jura (chargement -> Db -> filtrage -> anamorphose
    sur la variable Pb).

    Conservé pour ne pas casser les notebooks Jura existants (02, 03, 04).
    Pour un nouveau jeu de données, préférer l'enchaînement générique :
        df = charger_donnees(...)
        db = creer_db_gstlearn(df, variables=[...], noms_locators=[...])
        filtrer_valeurs_aberrantes(db, "ma_variable", seuil)
        db, anam = anamorphose_gaussienne(db, "ma_variable")

    Paramètres
    ----------
    seuil_aberrant : float
        Seuil (mg/kg) au-delà duquel une valeur de Pb est jugée aberrante.
        Par défaut 132 (voir `SEUIL_ABERRANT_PB_DEFAUT`).

    Retourne
    --------
    tuple : (data_jura, db, anam_hermite)
        data_jura : pandas.DataFrame, données brutes Jura non filtrées.
        db : gl.Db, base filtrée avec la variable gaussienne "Y.Pb" active.
        anam_hermite : gl.AnamHermite, objet d'anamorphose ajusté.
    """
    data_jura = charger_donnees_jura()
    db = creer_db_gstlearn(data_jura)
    filtrer_valeurs_aberrantes(db, "Pb", seuil_aberrant)
    db, anam_hermite = anamorphose_gaussienne(db, "Pb")
    return data_jura, db, anam_hermite

preparer_db_gaussienne = preparer_db_gaussienne_jura
# ==========================================================================
# Grille d'estimation
# ==========================================================================

def creer_grille(df, nx=100, ny=100, colonnes=("X", "Y")):
    """Crée une grille gstlearn (DbGrid) couvrant l'emprise des coordonnées du DataFrame.

    Cette grille sert ensuite à estimer la variable partout (krigeage) ou à simuler
    (bandes tournantes). Générique : fonctionne pour n'importe quel jeu de données 2D
    du moment que les colonnes de coordonnées sont précisées.

    Paramètres
    ----------
    df : pandas.DataFrame
        Tableau contenant les colonnes de coordonnées à utiliser.
    nx, ny : int
        Nombre de mailles de la grille selon X et Y (100 par défaut chacun).
    colonnes : tuple[str, str]
        Noms des colonnes de coordonnées dans `df` (("X", "Y") par défaut).

    Retourne
    --------
    gl.DbGrid
        Grille régulière couvrant l'emprise des données, prête pour le
        krigeage ou la simulation.
    """
    col_x, col_y = colonnes
    min_x, max_x = df[col_x].min(), df[col_x].max()
    min_y, max_y = df[col_y].min(), df[col_y].max()

    dx = (max_x - min_x) / nx
    dy = (max_y - min_y) / ny
    grille = gl.DbGrid.create(
        [nx, ny],
        [dx, dy],
        [min_x, min_y]
    )
    return grille

def sauvegarder_resultats_krigeage(rmse_ok, rmse_sk, pred_ok_pb, pred_sk_pb,
                                    chemin="../../../data/rmse_krigeage.json"):
    """Sauvegarde les RMSE et les prédictions ponctuelles du krigeage (OK, SK)
    dans un fichier JSON, pour que le notebook 05 (ML) puisse les récupérer
    sans dépendre du kernel du notebook 04.

    Paramètres
    ----------
    rmse_ok : float
        RMSE du krigeage ordinaire.
    rmse_sk : float
        RMSE du krigeage simple.
    pred_ok_pb : array-like
        Prédictions ponctuelles du krigeage ordinaire (Pb, mg/kg).
    pred_sk_pb : array-like
        Prédictions ponctuelles du krigeage simple (Pb, mg/kg).
    chemin : str
        Chemin du fichier JSON de sortie.

    Retourne
    --------
    None
        Écrit directement le fichier JSON sur disque.
    """
    with open(chemin, "w") as f:
        json.dump({
            "rmse_ok": rmse_ok, "rmse_sk": rmse_sk,
            "pred_ok_pb": list(pred_ok_pb), "pred_sk_pb": list(pred_sk_pb),
        }, f)

def charger_resultats_krigeage(chemin="../../../data/rmse_krigeage.json"):
    """Charge les RMSE et les prédictions ponctuelles du krigeage sauvegardés
    par le notebook 04. Retourne None si le fichier n'existe pas encore.

    Paramètres
    ----------
    chemin : str
        Chemin du fichier JSON à charger (doit avoir été créé au préalable
        par `sauvegarder_resultats_krigeage`).

    Retourne
    --------
    dict ou None
        Dictionnaire avec les clés 'rmse_ok', 'rmse_sk', 'pred_ok_pb',
        'pred_sk_pb' si le fichier existe, sinon None.
    """
    try:
        with open(chemin) as f:
            return json.load(f)
    except FileNotFoundError:      
        return None


   