"""
geostat_utils.variogram
========================

Auteur : RAZIK OUMAYMA — PFE ENSG 2025-2026
Revision: Guillaume Caumon

Fonctions liées au variogramme expérimental, à son affichage, et à son
calage manuel interactif (widget).
"""

import matplotlib.pyplot as plt
import gstlearn as gl
import gstlearn.plot as gp
import ipywidgets as widgets
import numpy as np

from .io import ResultsDir

# ==========================================================================
# Constantes par défaut
# ==========================================================================

def compute_lag_widths(lag_centers: np.ndarray) -> np.ndarray:
    """Estimate lag widths for from centers.
    :param lag_centers: 1D array of interval centers in ascending order.
    """
    widths = np.zeros_like(lag_centers)
    if len(lag_centers) > 1:
        widths[0] = lag_centers[1] - lag_centers[0]
        widths[-1] = lag_centers[-1] - lag_centers[-2]
        widths[1:-1] = (lag_centers[2:] - lag_centers[:-2]) / 2
    else:
        raise(NotImplementedError("Not enough lags to display $N(h)$"))
    return widths


def plot_1D_variogram(variogram: gl.Vario, title: str = None, filename = None, model = None,
                      frequency_as_histogram = True, scale_freq_width:float = 0.6) -> None:
    """
    :param variogram: The gstlearn empirical variogram
    :param title: The title of the figure
    :param filename: The filename to save the figure to a png file (not saved if None)
    :param model: The variogram model to display
    :param frequency_as_histogram: Specifies whether to display the number of pairs for each variogram point as a histogram
    :param scale_freq_width:
    :return: None
    """
    gp.varmod(variogram, model, showPairs=True, flagDrawVariance=True)
    plt.title('Variogramme expérimental' if title is None else title)

    ax1 = plt.gca()
    ax1.set_ylabel(r"$\gamma(h)$")
    if frequency_as_histogram:
        frequencies = variogram.getAllSw(0)  # Number of pairs per lag
        lag_centers = variogram.getAllHh(0)  # Mean distance per lag

        ax2 = ax1.twinx()  # Create a shared X, separate Y-axis
        ax2.set_ylabel("Nombre de paires", color="blue")
        ax2.tick_params(axis='y', colors='blue')
        max_freq = max(frequencies)
        ax2.set_ylim(0.0, float(max_freq/0.3))

        widths = compute_lag_widths(lag_centers) * scale_freq_width

        ax2.bar(
            lag_centers,
            frequencies,
            width=widths,
            color='blue',
            edgecolor='black',
            alpha=0.5,
            label="Nombre de paires"
        )
    results = ResultsDir('dummy')
    if filename is not None:
        results.save_fig(f"{filename}.png", bbox_inches="tight")
    plt.show()

class InteractiveVariogramFit:
    """Interactive widget for manual isotropic variogram modeling

    The initial value is chosen as half the maximum lag, 0 nugget and sill equal to the variance
    The user can change parameter values, then the model is available as self.model.
    """

    def __init__(self, vario: gl.Vario, unit: str = "m"):
        self.vario = vario
        self.default_type = 'Spherique'
        self.variance = vario.getVar(0, 0)
        self.total_sill = self.variance
        self.default_range = 0.5 * vario.getNLag(0) * vario.getDPas(0)
        self.default_nugget = 0.
        self.unit = unit
        self.max_possible_range = self.default_range * 4
        self.max_possible_sill = self.variance * 2

    def interactive_variogram_plot(
            self,
            model_type: str,
            vario_range: float,
            nugget: float,
            sill: float
    ) -> None:
        """
        Renders an interactive 1D geostatistical variogram model

        Generates a continuous spatial variogram model using ``gstlearn``
        on top of an experimental variogram.

        :param model_type: The variogram model type, among 'Spherical', 'Exponential', 'Gaussian', 'Cubic'.
        :param range: The correlation range (distance beyond whith there is no correlation).
        :param nugget: The measurement error or discontinuity at 0 (nugget effect), in % of the variance.
        :param sill: The sill of the variogram, theoretically equal to the variance.

        :return: None. Outputs an interactive, dual-axis Matplotlib canvas directly into the cell frame.

        :raises KeyError: If the supplied ``model_type`` string fails to map to an active ``gl.ECov`` definition.
        """
        types_cov: dict[str, gl.ECov] = {
            "Spherical": gl.ECov.SPHERICAL,
            "Exponential": gl.ECov.EXPONENTIAL,
            "Gaussian": gl.ECov.GAUSSIAN,
            "Cubic": gl.ECov.CUBIC
        }
        selected_type: gl.ECov = types_cov[model_type]
        self.total_sill = sill

        model: gl.Model = gl.Model()
        # Get widget values
        if nugget > 0.0:
            true_nugget = self.variance * nugget
            model.addCovFromParam(type=gl.ECov.NUGGET, sill=true_nugget)
        model.addCovFromParam(type=selected_type, sill=self.total_sill * (1. - nugget), range=vario_range)

        self.model = model

        plot_1D_variogram(self.vario, "Interactive variogram fitting", model=model, frequency_as_histogram=True)

    def interact(self):
        """
        Creates the interactive widget
        """
        widgets.interact(
            self.interactive_variogram_plot,
            model_type=widgets.Dropdown(
                options=["Spherical", "Exponential", "Gaussian", "Cubic"],
                value="Spherical",
                description="Modèle:"
            ),
            vario_range=widgets.FloatSlider(
                min=0.01,
                max=self.max_possible_range,
                step=self.max_possible_range / 100.0,
                value=self.default_range,
                description="Portée (Range):"
            ),
            nugget=widgets.FloatSlider(
                min=0.0,
                max=1,
                step=0.01,
                value=0.0,
                description="Nugget ($C_0$), in % of the sill:"
            ),
            sill=widgets.FloatSlider(
                min=0.0,
                max=self.max_possible_sill,
                step=self.variance / 100.0,
                value=self.variance,
                description="Palier (Sill):"
            )
        )