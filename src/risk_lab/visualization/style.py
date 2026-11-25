"""Shared plot style and a save helper."""

import matplotlib

matplotlib.use("Agg", force=False)
import matplotlib.pyplot as plt  # noqa: E402

from risk_lab.reporting.results import figure_path  # noqa: E402

COLORS = {
    "main": "#1f4e79",
    "second": "#c0504d",
    "third": "#6b8e23",
    "grey": "#7f7f7f",
}


def apply_style():
    """Plain readable defaults."""
    plt.rcParams.update(
        {
            "figure.figsize": (7.5, 4.2),
            "figure.dpi": 110,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
        }
    )


def save_figure(fig, module, name):
    """Save a figure under experiments/figures/<module>/."""
    path = figure_path(module, name)
    fig.savefig(path, bbox_inches="tight")
    return path
