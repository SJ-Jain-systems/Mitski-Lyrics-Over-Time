"""A small matplotlib theme built from the validated data-viz palette.

Colours and roles follow the reference palette: a fixed-order categorical set
(assigned by entity, never cycled), a single-hue blue ramp for magnitude, and
recessive grey chrome so the marks carry the ink. Figures render on the light
chart surface, which is what Quarto's default HTML/PDF output shows.
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt

# Chart chrome & ink (light surface)
SURFACE = "#fcfcfb"
PAGE = "#f9f9f7"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
GOOD = "#006300"

# Categorical palette, fixed order (blue, green, magenta, yellow, aqua, orange,
# violet, red). Assign by entity, in this order, and never rotate.
CATEGORICAL = [
    "#2a78d6",  # 1 blue
    "#008300",  # 2 green
    "#e87ba4",  # 3 magenta
    "#eda100",  # 4 yellow
    "#1baf7a",  # 5 aqua
    "#eb6834",  # 6 orange
    "#4a3aa7",  # 7 violet
    "#e34948",  # 8 red
]

# Single-hue sequential ramp (blue, light -> dark), for ordered magnitude.
SEQUENTIAL = [
    "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5",
    "#2a78d6", "#1c5cab", "#184f95", "#104281",
]

# Semantic roles used repeatedly in this report.
BLUE = CATEGORICAL[0]
GREEN = CATEGORICAL[1]
ORANGE = CATEGORICAL[5]
VIOLET = CATEGORICAL[6]
RED = CATEGORICAL[7]

# The visual "trilogy" colour story the source video describes.
TRILOGY = {
    "Be the Cowboy": "#c62828",   # explosion of red
    "Laurel Hell": "#111111",     # drenched in black
    "The Land Is Inhospitable and So Are We": "#7d8794",  # pulled-back, muted
}


def apply() -> None:
    """Install the theme globally for the current session/render."""
    mpl.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "figure.dpi": 140,
        "savefig.dpi": 140,
        "savefig.bbox": "tight",
        "font.size": 11,
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Segoe UI", "Helvetica", "Arial"],
        "text.color": INK,
        "axes.edgecolor": BASELINE,
        "axes.labelcolor": INK_2,
        "axes.titlecolor": INK,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlepad": 10,
        "axes.labelsize": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.frameon": False,
        "legend.fontsize": 10,
        "lines.linewidth": 2.0,
        "lines.markersize": 7,
    })


def style_axes(ax) -> None:
    """Per-axes touches the rcParams can't express (horizontal-only grid)."""
    ax.grid(axis="x", visible=False)
    ax.tick_params(length=0)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(BASELINE)


def new_fig(width=8.2, height=4.8):
    apply()
    fig, ax = plt.subplots(figsize=(width, height))
    style_axes(ax)
    return fig, ax
