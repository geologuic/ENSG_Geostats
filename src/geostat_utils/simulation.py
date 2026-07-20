"""
geostat_utils.simulation
=========================

Auteur : RAZIK OUMAYMA — PFE ENSG 2025-2026

Simulation conditionnelle par la méthode des Bandes Tournantes (Turning Bands
Simulation, TBS), et widget interactif d'affichage des réalisations.
"""

import numpy as np
import gstlearn as gl
import gstlearn.plot as gp
import matplotlib.pyplot as plt
import ipywidgets as widgets
from ipywidgets import interactive_output
from IPython.display import display

NB_SIMULATIONS_DEFAUT = 4
NB_BANDES_DEFAUT = 1000
SEED_DEFAUT = 12345
CMAP_SIMULATION_DEFAUT = "jet"
VMIN_SIMULATION_DEFAUT = -3
VMAX_SIMULATION_DEFAUT = 3


def simulation_bandes_tournantes(dbin, dbout, model_base, nom_variable, neigh=None,
                                 nb_simulations=NB_SIMULATIONS_DEFAUT, nb_bandes=NB_BANDES_DEFAUT, seed=SEED_DEFAUT,
                                 prefixe=None):
    """Réalise une simulation conditionnelle par bandes tournantes (TBS) sur `dbout`."""
    if neigh is None:
        neigh = gl.NeighUnique.create()
    if prefixe is None:
        prefixe = f"{nom_variable.replace('.', '')}Simu"

    if nom_variable not in dbin.getNames("*"):
        raise ValueError(f"La variable '{nom_variable}' n'existe pas dans dbin.")
    dbin.setLocator(nom_variable, gl.ELoc.Z)

    moyenne = np.mean(dbin.getColumn(nom_variable))

    model_simu = model_base.clone()
    model_simu.setMean(moyenne)

    gl.simtub(
        dbin=dbin, dbout=dbout, model=model_simu, neigh=neigh,
        nbsimu=nb_simulations, nbtuba=nb_bandes, seed=seed,
        namconv=gl.NamingConvention(prefixe)
    )

    return prefixe


def creer_widget_realisations(dbout, dbin, prefixe, nom_variable, nb_simulations=NB_SIMULATIONS_DEFAUT,
                            cmap=CMAP_SIMULATION_DEFAUT, vmin=VMIN_SIMULATION_DEFAUT, vmax=VMAX_SIMULATION_DEFAUT):
    """Crée et affiche un widget (ToggleButtons) pour parcourir les différentes
    réalisations d'une simulation par bandes tournantes.
    """
    options = [(f'Réalisation {i}', i) for i in range(1, nb_simulations + 1)]
    widget_realisation = widgets.ToggleButtons(
        options=options,
        value=1,
        description='Cartes (TBS):',
        button_style='warning'
    )

    def afficher(numero):
        tous_les_noms = dbout.getAllNames()
        candidats = [n for n in tous_les_noms if prefixe in n and n.endswith(f".S{numero}")]

        if not candidats:
            print(f"Aucune colonne trouvée pour prefixe='{prefixe}', réalisation {numero}.")
            print("Colonnes disponibles dans dbout :", tous_les_noms)
            return

        nom_colonne = candidats[0]

        fig, ax = gp.init(figsize=(8, 8), flagEqual=True)
        ax.raster(dbout, name=nom_colonne, flagLegend=True, cmap=cmap, vmin=vmin, vmax=vmax)
        ax.symbol(dbin, c="black")
        ax.decoration(title=f"Réalisation conditionnelle n°{numero} de {nom_variable} — Simulation TBS")
        plt.show()

    display(widgets.VBox([
        widget_realisation,
        interactive_output(afficher, {'numero': widget_realisation})
    ]))


def creer_widget_realisations_avec_seuil(dbout, dbin, prefixe, nom_variable, seuil,
                                          nb_simulations=NB_SIMULATIONS_DEFAUT,
                                          cmap="jet", vmin=20, vmax=120):
    """Comme `creer_widget_realisations`, mais affiche les valeurs en échelle brute
    (mg/kg) et superpose le contour de la zone dépassant `seuil`.
    """
    bornes = dbout.getExtremas()
    extent = [bornes[0][0], bornes[0][1], bornes[1][0], bornes[1][1]]

    options = [(f'Réalisation {i}', i) for i in range(1, nb_simulations + 1)]
    widget_realisation = widgets.ToggleButtons(options=options, value=1, description='Cartes :', button_style='info')

    def afficher(numero):
        nom_colonne = f"{prefixe}.S{numero}"
        valeurs = np.array(dbout.getColumn(nom_colonne))
        carte = valeurs.reshape(100, 100)
        zone = (valeurs > seuil).reshape(100, 100)

        fig, ax = plt.subplots(figsize=(6, 6))
        im = ax.imshow(carte, origin="lower", cmap=cmap, vmin=vmin, vmax=vmax,
                        extent=extent, interpolation="bilinear")
        plt.colorbar(im, ax=ax, label=f"{nom_variable}")
        ax.contour(zone.astype(int), levels=[0.5], colors="red", linewidths=2, extent=extent)
        ax.plot([], [], color="red", linewidth=2, label=f"Zone polluée (> {seuil} mg/kg)") 
        ax.set_title(f"Réalisation n°{numero} — {nom_variable}, seuil {seuil}")
        ax.set_xlabel("X (km)")
        ax.set_ylabel("Y (km)")
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=1)
        plt.tight_layout()
        plt.show()

    display(widgets.VBox([widget_realisation, interactive_output(afficher, {'numero': widget_realisation})]))


def ajouter_colonnes_reelles_simulation(dbout, prefixe, anam, nb_simulations=NB_SIMULATIONS_DEFAUT, nouveau_prefixe=None):
    """Retransforme chaque réalisation simulée (espace gaussien) en valeurs
    brutes (mg/kg), et les ajoute comme nouvelles colonnes dans la grille.
    """
    if nouveau_prefixe is None:
        nouveau_prefixe = f"{prefixe}_reel"

    for i in range(1, nb_simulations + 1):
        valeurs_gauss = dbout.getColumn(f"{prefixe}.Y.Pb.S{i}")
        valeurs_reel = np.array(anam.gaussianToRawVector(valeurs_gauss))
        dbout.setColumn(valeurs_reel, f"{nouveau_prefixe}.S{i}")

    return nouveau_prefixe