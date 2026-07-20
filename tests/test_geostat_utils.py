import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import geostat_utils as gutils


def test_valeurs_defaut_modeles():
    assert "Spherique" in gutils.VALEURS_DEFAUT_MODELES
    assert gutils.VALEURS_DEFAUT_MODELES["Spherique"] == (0.21, 0.60)


def test_creer_grille():
    import pandas as pd
    df = pd.DataFrame({"X": [0.0, 1.0], "Y": [0.0, 1.0]})
    grille = gutils.creer_grille(df, nx=10, ny=10)
    assert grille.getNSample() == 100


def test_filtrer_valeurs_aberrantes():
    import pandas as pd
    df = pd.DataFrame({"X": [0, 1, 0, 1], "Y": [0, 0, 1, 1], "Valeur": [10, 20, 200, 30]})
    db = gutils.creer_db_gstlearn(df, variables=["X", "Y", "Valeur"], noms_locators=["x1", "x2", "z1"])
    gutils.filtrer_valeurs_aberrantes(db, "Valeur", seuil=100)
    assert db.getNSample(True) == 3


def test_creer_db_gstlearn():
    import pandas as pd
    df = pd.DataFrame({"X": [0, 1, 2], "Y": [0, 1, 2], "Valeur": [10, 20, 30]})
    db = gutils.creer_db_gstlearn(df, variables=["X", "Y", "Valeur"], noms_locators=["x1", "x2", "z1"])
    assert db.getNSample() == 3