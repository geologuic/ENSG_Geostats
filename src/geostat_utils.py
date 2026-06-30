import os
import pandas as pd
import numpy as np
import gstlearn as gl
import gstlearn.plot as gp
import matplotlib.pyplot as plt


def charger_donnees_jura(chemin_fichier="../../data/juradata.csv"):
    """Charge le jeu de données Jura et convertit les coordonnées X et Y de mètres en kilomètres.
    Teste plusieurs chemins possibles pour fonctionner quel que soit l'endroit
    d'où le notebook est lancé.
    """
    # Liste des chemins possibles où chercher le fichier de données

    chemins_a_tester = [
        chemin_fichier,
        os.path.join("..", "..", "data", "juradata.csv"),
        os.path.join("..", "..", "..", "data", "juradata.csv"),   # depuis src/notebooks/jura/
        os.path.join("data", "juradata.csv"),
        # Chemin absolu basé sur l'emplacement du module (src/) : robuste quel que soit le dossier courant
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "juradata.csv")) if '__file__' in globals() else None,
    ]
    # On teste chaque chemin : on s'arrête au premier qui existe

    for chemin in chemins_a_tester:
        if chemin and os.path.exists(chemin):
            donnees = pd.read_csv(chemin, sep=";")
            donnees["X"] = donnees["X"] / 1000.0
            donnees["Y"] = donnees["Y"] / 1000.0
            return donnees

    # Aucun chemin valide trouvé : on signale une erreur claire
    raise FileNotFoundError(f"Fichier juradata.csv introuvable. Chemins testés : {chemins_a_tester}")


def creer_db_gstlearn(df, variables=["X", "Y", "Pb"], noms_locators=["x1", "x2", "z1"]):
    """Crée un objet Db de gstlearn à partir d'un tableau pandas (DataFrame).

    Les "locators" indiquent le rôle de chaque colonne :
    x1, x2 = coordonnées ; z1 = variable étudiée (Pb).
    """
    donnees = df[variables].to_numpy()              # extraction des colonnes utiles en tableau numpy
    nombre_echantillons = donnees.shape[0]          # nombre de lignes = nombre de points de mesure
    db = gl.Db.createFromSamples(
        nombre_echantillons,
        tab=donnees.flatten(),                      # gstlearn attend les valeurs "à plat"
        names=variables,
        locatorNames=noms_locators
    )
    return db

def filtrer_valeurs_aberrantes(db, nom_colonne="Pb", seuil=132):
    """Filtre les valeurs aberrantes en ajoutant une sélection : on ne garde que les valeurs sous le seuil."""
    valeurs = db.getColumn(nom_colonne)             # récupère toutes les valeurs de la colonne
    id_selection = db.addSelection(valeurs < seuil)  # masque : on ignore les valeurs >= seuil
    return id_selection


def preparer_db_gaussienne():

    """Initialise la base Jura, applique le filtrage des valeurs aberrantes et l'anamorphose de Hermite.

    Transforme la variable Pb dans l'espace gaussien (Y.Pb) et la définit comme variable active.

    Retourne : tuple : (data_jura, db, anam_hermite) """

    data_jura = charger_donnees_jura()
    db = creer_db_gstlearn(data_jura)
    filtrer_valeurs_aberrantes(db, "Pb", 132)

    anam_hermite = gl.AnamHermite(25)               # transformation avec 25 polynômes de Hermite
    anam_hermite.fitFromLocator(db)                 # apprend la forme de la distribution
    err = anam_hermite.rawToGaussianByLocator(db)   # transforme Pb -> Y.Pb (espace gaussien)
    db.setLocator("Y.Pb", gl.ELoc.Z)                # Y.Pb devient la variable à étudier

    return data_jura, db, anam_hermite


def creer_grille(df, nx=100, ny=100):
    """Crée une grille gstlearn (DbGrid) couvrant l'emprise des coordonnées du DataFrame.

    Cette grille sert ensuite à estimer la variable partout (krigeage).
    """
    min_x, max_x = df["X"].min(), df["X"].max()
    min_y, max_y = df["Y"].min(), df["Y"].max()

    etendue_x = max_x - min_x
    etendue_y = max_y - min_y
    dx = etendue_x / nx
    dy = etendue_y / ny
    grille = gl.DbGrid.create(
        [nx, ny],
        [dx, dy],
        [min_x, min_y]
    )
    return grille

def afficher_variogramme(vario, model, titre, variance, unite="km", chemin_fichier=None):
    """Trace le variogramme expérimental et le modèle ajusté avec gstlearn.plot.

    unite : unité de distance affichée en abscisse ("km" en 2D, "m" pour le 1D GoldPrice).
    chemin_fichier : si fourni, chemin complet où enregistrer la figure au format PNG.
    """
    ax = gp.varmod(vario, model, showPairs=True)
    ax.set_ylim(0, variance * 2)
    plt.xlabel(f"Distance ({unite})")
    plt.ylabel(r"$\gamma(h)$")
    plt.title(titre)
    if chemin_fichier:
        plt.savefig(chemin_fichier, dpi=150, bbox_inches="tight")
    plt.show()
    plt.close()  
    print(model)
