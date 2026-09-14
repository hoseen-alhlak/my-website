"""Shared visual language for the atlas charts."""
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path("/home/user/atlas")
CHARTS = ROOT / "charts"
FONTS = ROOT / "fonts"
CHARTS.mkdir(parents=True, exist_ok=True)

# Editorial palette — ink, sand, terracotta, teal
NAVY = "#0E2433"
INK = "#1C2833"
GOLD = "#C6A15B"
CREAM = "#F7F2E8"
PAPER = "#FBF7F0"
TERRACOTTA = "#C45C4A"
TEAL = "#2C6E7A"
SAGE = "#6B8F71"
CORAL = "#E07A5F"
SLATE = "#5B6570"
SAND = "#E6D9C4"
MUTED = "#8A8478"

PALETTE = [
    "#2C6E7A",
    "#C45C4A",
    "#C6A15B",
    "#6B8F71",
    "#4A6FA5",
    "#E07A5F",
    "#8B5E83",
    "#D4A373",
    "#3D5A4C",
    "#A8483D",
]

for fp in FONTS.glob("*.ttf"):
    font_manager.fontManager.addfont(str(fp))

mpl.rcParams.update(
    {
        "figure.facecolor": CREAM,
        "axes.facecolor": PAPER,
        "axes.edgecolor": "#C9BFAE",
        "axes.labelcolor": INK,
        "axes.titlecolor": NAVY,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.labelsize": 8.5,
        "xtick.color": SLATE,
        "ytick.color": SLATE,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "text.color": INK,
        "grid.color": "#E6DCCB",
        "grid.linewidth": 0.6,
        "font.size": 9,
        "font.family": "DejaVu Sans",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "legend.fontsize": 8,
        "figure.dpi": 140,
        "savefig.dpi": 150,
        "savefig.facecolor": CREAM,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.18,
    }
)


def new_fig(w=7.6, h=4.15):
    fig, ax = plt.subplots(figsize=(w, h))
    return fig, ax


def polish(ax, ygrid=True, xgrid=False):
    ax.set_axisbelow(True)
    if ygrid:
        ax.yaxis.grid(True, color="#E6DCCB", linewidth=0.65)
    if xgrid:
        ax.xaxis.grid(True, color="#E6DCCB", linewidth=0.65)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_linewidth(0.7)


def save(fig, name: str):
    path = CHARTS / f"{name}.png"
    fig.savefig(path)
    plt.close(fig)
    return path
