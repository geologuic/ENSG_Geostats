"""
geostat_utils.variogram
========================

Auteur : RAZIK OUMAYMA — PFE ENSG 2025-2026

Fonctions liées au variogramme expérimental, à son affichage, et à son
calage manuel interactif (widget).
"""

import matplotlib.pyplot as plt
import gstlearn as gl
import gstlearn.plot as gp
import ipywidgets as widgets
from ipywidgets import interactive_output
from IPython.display import display

# ==========================================================================
# Constantes par défaut
# ==========================================================================

VALEURS_DEFAUT_MODELES = {
    'Spherique':   (0.21, 0.60),
    'Exponentiel': (0.15, 0.86),
    'Gaussien':    (0.15, 0.70),
}
PORTEE_MIN_DEFAUT = 0.1
PORTEE_MAX_DEFAUT = 3.0
NUGGET_MAX_DEFAUT = 0.5

def afficher_variogramme(vario, model, titre, variance, unite="km", chemin_fichier=None):
    """Trace le variogramme expérimental et le modèle ajusté avec gstlearn.plot.

    Paramètres
    ----------
    unite : str
        Unité de distance affichée en abscisse ("km" en 2D, "m" pour le 1D GoldPrice).
    chemin_fichier : str ou None
        Si fourni, chemin complet où enregistrer la figure au format PNG.
    """
    ax = gp.varmod(vario, model, showPairs=True)
    ax.set_ylim(0, variance * 2)
    plt.xlabel(f"Distance ({unite})")
    plt.ylabel(r"$\gamma(h)$")
    plt.title(titre)
    if chemin_fichier:
        plt.savefig(chemin_fichier, dpi=150, bbox_inches="tight")
    plt.show()
    plt.close()  # évite l'accumulation de figures lors des appels répétés (widget)
    print(model)


# ==========================================================================
# Calage manuel interactif du variogramme (widget)
# ==========================================================================

TYPES_COVARIOGRAMMES = {
    'Spherique':   gl.ECov.SPHERICAL,
    'Exponentiel': gl.ECov.EXPONENTIAL,
    'Gaussien':    gl.ECov.GAUSSIAN,
}


class CalageVariogramme:
    """Widget interactif de calage manuel d'un modèle de variogramme
    (Nugget + Sphérique/Exponentiel/Gaussien).

    Après interaction de l'utilisateur avec les curseurs, le modèle courant est
    accessible via l'attribut `.model`.
    """

    def __init__(self, vario, variance, valeurs_defaut=None, facteur_correction=1.0,
                 unite="km", chemin_sortie=None, portee_min=PORTEE_MIN_DEFAUT, portee_max=PORTEE_MAX_DEFAUT,
                 nugget_max=NUGGET_MAX_DEFAUT):
        self.vario = vario
        self.variance = variance
        self.facteur_correction = facteur_correction
        self.unite = unite
        self.chemin_sortie = chemin_sortie
        self._afficher_variogramme = afficher_variogramme

        self.valeurs_defaut = valeurs_defaut or VALEURS_DEFAUT_MODELES

        modele_initial = list(self.valeurs_defaut.keys())[0]
        nugget_initial, portee_initiale = self.valeurs_defaut[modele_initial]

        self.widget_modele = widgets.Dropdown(
            options=list(self.valeurs_defaut.keys()),
            value=modele_initial,
            description='Modèle :'
        )
        self.widget_nugget = widgets.FloatSlider(
            value=nugget_initial, min=0.0, max=nugget_max,
            step=0.01, description='Nugget :'
        )
        self.widget_portee = widgets.FloatSlider(
            value=portee_initiale, min=portee_min, max=portee_max,
            step=0.01, description=f'Portée ({unite}) :'
        )

        def _update_defauts(change):
            self.widget_nugget.value, self.widget_portee.value = self.valeurs_defaut[change['new']]
        self.widget_modele.observe(_update_defauts, names='value')

        self.model = gl.Model()

    def _reglage(self, modele, nugget, portee):
        self.model = gl.Model()
        self.model.addCovFromParam(
            gl.ECov.NUGGET,
            sill=nugget * self.facteur_correction
        )
        self.model.addCovFromParam(
            TYPES_COVARIOGRAMMES[modele],
            range=portee,
            sill=(1 - nugget) * self.facteur_correction
        )
        chemin = f"{self.chemin_sortie}/calage_{modele}.png" if self.chemin_sortie else None
        self._afficher_variogramme(
            self.vario, self.model,
            f"Modèle ajusté manuellement — Nugget + {modele}",
            self.variance, unite=self.unite, chemin_fichier=chemin
        )

    def afficher(self):
        """Affiche le widget (dropdown + curseurs + graphique interactif)."""
        display(widgets.VBox([
            self.widget_modele,
            self.widget_nugget,
            self.widget_portee,
            interactive_output(self._reglage, {
                'modele': self.widget_modele,
                'nugget': self.widget_nugget,
                'portee': self.widget_portee,
            })
        ]))

def creer_widget_calage_variogramme(vario, variance, **kwargs):
    """Crée et affiche directement un widget de calage manuel.
    Retourne l'objet `CalageVariogramme` (accès au modèle courant via `.model`
    une fois que l'utilisateur a interagi avec les curseurs).
    """
    calage = CalageVariogramme(vario, variance, **kwargs)
    calage.afficher()
    return calage