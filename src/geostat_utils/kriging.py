"""
geostat_utils.kriging
======================

Auteur : RAZIK OUMAYMA — PFE ENSG 2025-2026

Krigeage Simple (SK), Ordinaire (OK) et Universel (UK), et widget interactif
d'affichage des cartes de krigeage.
Factorise le code qui était dupliqué (à quelques renommages de variables près)
entre `04_krigeage_simulation.ipynb` (Jura) et `03_exercice3_krigeage_simulation.ipynb` (Gold).
"""

import numpy as np
import gstlearn as gl
import gstlearn.plot as gp
import matplotlib.pyplot as plt
import ipywidgets as widgets
from ipywidgets import interactive_output
from IPython.display import display

PREFIXE_KRIGING_DEFAUT = "Kriging"
CMAP_DEFAUT = "jet"

def krigeage_sk_ok_uk(dbin, dbout, model_base, nom_variable, neigh=None, prefixe=PREFIXE_KRIGING_DEFAUT):
    """Réalise le krigeage Simple (SK), Ordinaire (OK) et Universel (UK) sur `dbout`
    à partir des données de `dbin`, avec le modèle de covariance `model_base`.

    Paramètres
    ----------
    dbin : gl.Db
        Base contenant les données mesurées.
    dbout : gl.DbGrid
        Grille sur laquelle réaliser l'estimation (voir `geostat_utils.io.creer_grille`).
    model_base : gl.Model
        Modèle de covariance déjà ajusté (Nugget + structure), SANS dérive.
        Il sera cloné 3 fois en interne (un clone par méthode) pour ne pas être modifié.
    nom_variable : str
        Nom de la variable à krieger (ex. "Y.Pb", "Values"). Doit être la variable
        active (locator Z) de `dbin`.
    neigh : gl.ANeigh ou None
        Voisinage à utiliser. Si None, un voisinage unique est créé automatiquement
        (adapté aux jeux de données de taille modeste, type TD).
    prefixe : str
        Préfixe utilisé pour nommer les colonnes créées dans `dbout`
        (ex. "Kriging_simple.<nom_variable>.estim").

    Retourne
    --------
    dict avec les clés 'neigh' (voisinage utilisé) et 'moyenne' (moyenne globale
    de la variable, utilisée pour le krigeage simple).
    """
    if neigh is None:
        neigh = gl.NeighUnique.create()

    # On force `nom_variable` comme variable active (locator Z) de `dbin` :
    # gl.kriging() krige la variable désignée par le locator Z, pas celle
    # passée en argument ici. Sans cette ligne, un appel avec un `nom_variable`
    # différent du locator Z déjà en place kriguerait silencieusement la
    # mauvaise colonne tout en affichant le bon nom partout ailleurs.
    if nom_variable not in dbin.getNames("*"):
        raise ValueError(f"La variable '{nom_variable}' n'existe pas dans dbin.")
    dbin.setLocator(nom_variable, gl.ELoc.Z)

    moyenne = np.mean(dbin.getColumn(nom_variable))

    # ---- Krigeage Simple (SK) : moyenne connue et fixe ----
    model_sk = model_base.clone()
    model_sk.setMean(moyenne)
    gl.kriging(
        dbin=dbin, dbout=dbout, model=model_sk, neigh=neigh,
        flag_est=True, flag_varz=True,
        namconv=gl.NamingConvention(f"{prefixe}_simple")
    )

    # ---- Krigeage Ordinaire (OK) : moyenne inconnue, estimée localement ----
    model_ok = model_base.clone()
    model_ok.addDrift(gl.DriftM())
    gl.kriging(
        dbin=dbin, dbout=dbout, model=model_ok, neigh=neigh,
        flag_est=True, flag_varz=True,
        namconv=gl.NamingConvention(f"{prefixe}_ordinaire")
    )

    # ---- Krigeage Universel (UK) : tendance linéaire (drift d'ordre 1) ----
    model_uk = model_base.clone()
    model_uk.setDriftIRF(order=1)
    gl.kriging(
        dbin=dbin, dbout=dbout, model=model_uk, neigh=neigh,
        flag_est=True, flag_std=True, flag_varz=False,
        namconv=gl.NamingConvention(f"{prefixe}_universel")
    )

    return {"neigh": neigh, "moyenne": moyenne}


def creer_widget_cartes_krigeage(dbout, dbin, nom_variable, prefixe=PREFIXE_KRIGING_DEFAUT, cmap=CMAP_DEFAUT):
    """Crée et affiche un widget interactif permettant de choisir la méthode
    de krigeage (SK/OK/UK) et le type de carte (estimation ou variance/écart-type).

    À utiliser après `krigeage_sk_ok_uk` (les colonnes attendues dans `dbout`
    doivent déjà exister).
    """
    widget_methode = widgets.Dropdown(
        options=[
            ('Krigeage Simple (SK)', 'simple'),
            ('Krigeage Ordinaire (OK)', 'ordinaire'),
            ('Krigeage Universel (UK)', 'universel'),
        ],
        value='simple',
        description='Méthode'
    )
    widget_carte = widgets.Dropdown(
        options=[
            ('Estimation', 'estim'),
            ('Variance/Écart-type', 'varz'),
        ],
        value='estim',
        description='Carte:'
    )

    def afficher(choix_methode, choix_carte):
        # Le krigeage universel ne calcule que l'écart-type (stdev), pas la variance (varz)
        if choix_methode == 'universel' and choix_carte == 'varz':
            nom_carte = f'{prefixe}_universel.{nom_variable}.stdev'
        else:
            nom_carte = f'{prefixe}_{choix_methode}.{nom_variable}.{choix_carte}'

        fig, ax = gp.init(figsize=(6, 6), flagEqual=True)
        ax.raster(dbout, name=nom_carte, flagLegend=True, cmap=cmap)
        ax.symbol(dbin, c="black")
        ax.decoration(title=f"Krigeage {choix_methode} — {choix_carte}")
        plt.show()
        plt.close()

    display(widgets.VBox([
        widget_methode,
        widget_carte,
        interactive_output(afficher, {
            'choix_methode': widget_methode,
            'choix_carte': widget_carte,
        })
    ]))
