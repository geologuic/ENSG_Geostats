"""
geostat_utils
=============

Package développé par RAZIK OUMAYMA dans le cadre de mon PFE
"Développement de notebooks Jupyter pour l'enseignement de la géostatistique"
ENSG, 2025-2026.

Organisé en sous-modules par thème :
- io                 : chargement des données, création de Db, filtrage, anamorphose, grille
- variogram          : calcul et affichage du variogramme expérimental
- kriging            : krigeage Simple/Ordinaire/Universel + widget d'affichage des cartes
- simulation         : simulation par bandes tournantes (TBS) + widget de réalisations

Tous les noms sont ré-exportés ici pour que l'usage existant dans les notebooks
(`import geostat_utils as gutils` puis `gutils.ma_fonction(...)`) continue de
fonctionner sans aucune modification.
"""
__version__ = "0.0.1"

from .io import (
    charger_donnees,
    charger_donnees_jura,
    creer_db_gstlearn,
    filtrer_valeurs_aberrantes,
    anamorphose_gaussienne,
    preparer_db_gaussienne_jura,
    preparer_db_gaussienne,  
    creer_grille,
    sauvegarder_resultats_krigeage,
    charger_resultats_krigeage,
    sauvegarder_figure,
)

from .variogram import (
    afficher_variogramme,
    CalageVariogramme,
    creer_widget_calage_variogramme,
    VALEURS_DEFAUT_MODELES,
)

from .kriging import (
    krigeage_sk_ok_uk,
    creer_widget_cartes_krigeage,
)

from .simulation import (
    simulation_bandes_tournantes,
    creer_widget_realisations,
    creer_widget_realisations_avec_seuil,
    ajouter_colonnes_reelles_simulation,
)

__all__ = [
    "charger_donnees",
    "charger_donnees_jura",
    "creer_db_gstlearn",
    "filtrer_valeurs_aberrantes",
    "anamorphose_gaussienne",
    "preparer_db_gaussienne_jura",
    "preparer_db_gaussienne",
    "creer_grille",
    "sauvegarder_resultats_krigeage",
    "charger_resultats_krigeage",
    "sauvegarder_figure",
    "afficher_variogramme",
    "CalageVariogramme",
    "creer_widget_calage_variogramme",
    "VALEURS_DEFAUT_MODELES",
    "krigeage_sk_ok_uk",
    "creer_widget_cartes_krigeage",
    "simulation_bandes_tournantes",
    "creer_widget_realisations",
    "creer_widget_realisations_avec_seuil",
    "ajouter_colonnes_reelles_simulation",
]