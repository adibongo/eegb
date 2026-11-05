"""
eegb_style.py — shared chart style for every EEGB Python script.

Usage (from the project root, e.g. in RStudio with reticulate or in a terminal):
    import sys; sys.path.insert(0, "python")
    from eegb_style import *
    set_style()
    ...
    save(fig, "s02", "f03")   # -> sessions/s02/figures/python/s02_f03.png
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")            # draws to files; works in RStudio, terminals and servers
import matplotlib.pyplot as plt

# Lagos Business School deck palette (matches the slides and the R theme)
NAVY, TEAL, TEAL2, GOLD = "#122867", "#0A6AA1", "#0088C7", "#D99A2B"
RUST, SLATE, INK, LIGHT, GRID = "#B5541A", "#5C6B7A", "#1A2233", "#F3F6F9", "#E1E7EE"
OLIVE, SKY = "#8C8A4E", "#7FB3C8"
PALETTE = [TEAL, GOLD, NAVY, RUST, TEAL2, OLIVE, SKY, SLATE]

def set_style():
    plt.rcParams.update({
        "figure.figsize": (10, 5.6), "figure.dpi": 100, "savefig.dpi": 200,
        "font.family": "sans-serif",
        "font.sans-serif": ["Calibri", "Carlito", "Arial", "DejaVu Sans"],
        "font.size": 13, "axes.titlesize": 16, "axes.titleweight": "bold", "axes.titlecolor": NAVY,
        "axes.titlelocation": "left", "axes.titlepad": 14,
        "axes.labelsize": 13, "axes.labelcolor": INK, "axes.edgecolor": "#B8C2CE",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
        "xtick.color": SLATE, "ytick.color": SLATE, "legend.frameon": False,
        "axes.prop_cycle": matplotlib.cycler(color=PALETTE),
    })

def naira(x, pos=None):
    """Axis formatter: 12500 -> ₦12.5k ; 2500000 -> ₦2.5m"""
    if abs(x) >= 1e6: return f"₦{x/1e6:.1f}m"
    if abs(x) >= 1e3:
        k = x / 1e3
        return f"₦{k:.0f}k" if abs(k - round(k)) < 1e-9 or abs(x) >= 1e5 else f"₦{k:.1f}k"
    return f"₦{x:.0f}"

def save(fig, session, fig_id):
    """Save a figure to sessions/<session>/figures/python/<session>_<fig_id>.png"""
    out = Path("sessions") / session / "figures" / "python"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{session}_{fig_id}.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", path)
    return path

def usd(x, pos=None):
    """Axis formatter: 2500000000 -> $2.5bn ; 45 -> $45"""
    if abs(x) >= 1e9: return f"${x/1e9:.1f}bn"
    if abs(x) >= 1e6: return f"${x/1e6:.1f}m"
    return f"${x:,.0f}"

def pct(x, pos=None):
    """Axis formatter for values already in percent: 12.5 -> 12.5%"""
    return f"{x:.0f}%" if abs(x - round(x)) < 1e-9 else f"{x:.1f}%"

def note(fig, text="Source: EEGB stylised teaching data (data/). Not official statistics."):
    """Small grey source line under a chart."""
    fig.text(0.01, -0.02, text, fontsize=9.5, color=SLATE, ha="left", va="top")
