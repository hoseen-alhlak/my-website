#!/usr/bin/env python3
"""Side-by-side misleading vs honest examples for the 8 design principles."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle, FancyBboxPatch
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

sys.path.insert(0, str(Path(__file__).parent))
from style import (
    PALETTE, NAVY, INK, GOLD, CREAM, PAPER, TERRACOTTA, TEAL, SAGE, CORAL,
    SLATE, SAND, MUTED, polish, CHARTS,
)
from make_cover import divider

rng = np.random.default_rng(7)
SEQ = LinearSegmentedColormap.from_list("seq", ["#F4EBD8", "#8FB3B0", "#2C6E7A", "#0E2433"])
RAINBOW = plt.get_cmap("jet")


def pair_axes(h=4.55):
    fig, axes = plt.subplots(1, 2, figsize=(10.5, h), facecolor=CREAM)
    fig.subplots_adjust(wspace=0.28, left=0.07, right=0.97, top=0.86, bottom=0.16)
    return fig, axes


def banner(ax, text, bad=True):
    color = TERRACOTTA if bad else TEAL
    ax.set_title(text, color="white", fontsize=10, fontweight="bold", pad=10)
    # title box via axes title cannot easily have bg; use a transAxes patch
    ax.annotate(
        text,
        xy=(0.5, 1.08),
        xycoords="axes fraction",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
        color="white",
        bbox=dict(boxstyle="square,pad=0.35", facecolor=color, edgecolor="none"),
    )
    ax.set_title("")  # replaced by annotate


def save(fig, name):
    path = CHARTS / f"{name}.png"
    fig.savefig(path, dpi=150, facecolor=CREAM, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    return path


def p01_question():
    """Same market data: pie of this year vs slope 2020→2025."""
    fig, (ax1, ax2) = pair_axes()
    banner(ax1, "MISLEADING  ·  pie of this year", bad=True)
    banner(ax2, "HONEST  ·  answers the growth question", bad=False)

    labels = ["Mobile", "Store", "Web", "Other"]
    y2025 = [48, 22, 20, 10]
    y2020 = [30, 40, 20, 10]
    ax1.pie(
        y2025,
        labels=labels,
        colors=PALETTE[:4],
        startangle=90,
        explode=(0.04, 0, 0, 0),
        autopct="%1.0f%%",
        wedgeprops=dict(edgecolor=CREAM, linewidth=1.5),
        pctdistance=0.7,
    )
    ax1.set_xlabel("Question was: which channel grew?\nThis only shows 2025 share.", fontsize=8, color=SLATE)

    for lab, a, b, col in zip(labels, y2020, y2025, PALETTE):
        ax2.plot([0, 1], [a, b], color=col, lw=2.3, marker="o", ms=7)
        ax2.text(-0.08, a, f"{lab}  {a}", ha="right", va="center", fontsize=8)
        ax2.text(1.08, b, str(b), ha="left", va="center", fontsize=8, color=col)
    ax2.set_xlim(-0.55, 1.4)
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(["2020", "2025"])
    ax2.set_yticks([])
    for sp in ax2.spines.values():
        sp.set_visible(False)
    ax2.set_xlabel("Mobile rose. Store fell. Web and Other stood still.", fontsize=8, color=SLATE)
    polish(ax2, ygrid=False)
    save(fig, "p01_question")


def p02_position():
    fig, (ax1, ax2) = pair_axes()
    banner(ax1, "MISLEADING  ·  close slices as a pie", bad=True)
    banner(ax2, "HONEST  ·  same numbers as bars", bad=False)

    labs = ["North", "South", "East", "West"]
    vals = [26, 24, 25, 25]
    ax1.pie(
        vals,
        labels=[f"{l}\n{v}%" for l, v in zip(labs, vals)],
        colors=PALETTE[:4],
        startangle=90,
        wedgeprops=dict(edgecolor=CREAM, linewidth=1.5),
    )
    ax1.set_xlabel("All four look almost equal.\nThey are — but 26 vs 24 is invisible.", fontsize=8, color=SLATE)

    y = np.arange(len(labs))
    order = np.argsort(vals)[::-1]
    ax2.barh(y, np.array(vals)[order], color=TEAL, height=0.55, zorder=3)
    ax2.set_yticks(y)
    ax2.set_yticklabels(np.array(labs)[order])
    ax2.invert_yaxis()
    ax2.set_xlim(20, 28)
    ax2.set_xlabel("Axis starts at 20 to show the gap —\nand that fact is declared.", fontsize=8, color=SLATE)
    for i, v in enumerate(np.array(vals)[order]):
        ax2.text(v + 0.08, i, f"{v}%", va="center", fontsize=8)
    polish(ax2, ygrid=False, xgrid=True)
    save(fig, "p02_position")


def p03_maps():
    fig, (ax1, ax2) = pair_axes(h=4.8)
    banner(ax1, "MISLEADING  ·  colour = raw counts", bad=True)
    banner(ax2, "HONEST  ·  colour = rate per 100k", bad=False)

    regions = [
        [(0.3, 0.4), (3.1, 0.3), (3.3, 2.7), (0.5, 2.9)],
        [(3.1, 0.3), (6.4, 0.5), (6.1, 3.0), (3.3, 2.7)],
        [(6.4, 0.5), (9.4, 0.7), (9.3, 3.2), (6.1, 3.0)],
        [(0.5, 2.9), (3.3, 2.7), (3.5, 5.4), (0.7, 5.3)],
        [(3.3, 2.7), (6.1, 3.0), (6.3, 5.5), (3.5, 5.4)],
        [(6.1, 3.0), (9.3, 3.2), (9.2, 5.4), (6.3, 5.5)],
    ]
    pop = np.array([10.0, 8.0, 2.0, 1.2, 5.0, 3.0])  # million
    cases = np.array([900, 720, 280, 250, 300, 150])
    rate = cases / pop  # per million ≈ per 100k *10, relative is what matters
    names = ["R1", "R2", "R3", "R4", "R5", "R6"]

    def draw(ax, values, cmap):
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_xlim(0, 10)
        ax.set_ylim(-1.0, 6.0)
        vmax = values.max()
        for poly, v, n in zip(regions, values, names):
            xs, ys = zip(*poly)
            ax.fill(xs, ys, color=cmap(v / vmax), edgecolor=CREAM, lw=2)
            ax.text(sum(xs) / 4, sum(ys) / 4, n, ha="center", va="center",
                    color="white" if v / vmax > 0.55 else NAVY, fontsize=8, fontweight="bold")

    draw(ax1, cases, SEQ)
    ax1.text(5, -0.15, "Biggest region looks worst.\nIt is only the most populated.", ha="center", va="top", fontsize=8, color=SLATE)
    draw(ax2, rate, SEQ)
    ax2.text(5, -0.15, "R3 and R4 (small, dense) are the\nreal hotspots. The story flipped.", ha="center", va="top", fontsize=8, color=SLATE)
    save(fig, "p03_maps")


def p04_causation():
    fig, (ax1, ax2) = pair_axes()
    banner(ax1, "MISLEADING  ·  'ice cream causes drowning'", bad=True)
    banner(ax2, "HONEST  ·  both follow the season", bad=False)

    months = np.arange(1, 13)
    temp = np.array([8, 9, 12, 16, 20, 25, 28, 27, 23, 17, 12, 9])
    ice = 20 + temp * 1.8 + rng.normal(0, 2, 12)
    drown = 4 + temp * 0.55 + rng.normal(0, 1.1, 12)

    ax1.scatter(ice, drown, s=42, color=TEAL, zorder=3, edgecolors=NAVY, lw=0.3)
    z = np.polyfit(ice, drown, 1)
    xs = np.linspace(ice.min(), ice.max(), 40)
    ax1.plot(xs, np.polyval(z, xs), color=TERRACOTTA, lw=1.7)
    ax1.set_xlabel("Ice-cream sales")
    ax1.set_ylabel("Drownings")
    polish(ax1, xgrid=True)
    ax1.text(0.05, 0.92, "r = 0.91   so… causation?", transform=ax1.transAxes,
             fontsize=8, color=TERRACOTTA, fontweight="bold")

    ax2.plot(months, (ice - ice.min()) / (ice.max() - ice.min()), color=GOLD, lw=2.1, label="Ice cream")
    ax2.plot(months, (drown - drown.min()) / (drown.max() - drown.min()), color=TEAL, lw=2.1, label="Drownings")
    ax2.plot(months, (temp - temp.min()) / (temp.max() - temp.min()), color=TERRACOTTA, lw=1.6, ls="--", label="Temperature")
    ax2.set_xticks(months)
    ax2.set_xticklabels(list("JFMAMJJASOND"))
    ax2.set_ylabel("Scaled 0–1")
    ax2.legend(loc="upper left", fontsize=7.5)
    polish(ax2)
    ax2.set_xlabel("The lurking variable is heat, not ice cream.", fontsize=8, color=SLATE)
    save(fig, "p04_causation")


def p05_dualaxis():
    fig, (ax1, ax2) = pair_axes()
    banner(ax1, "MISLEADING  ·  dual axis, cooked scales", bad=True)
    banner(ax2, "HONEST  ·  two panels, zero-based", bad=False)

    x = np.arange(2019, 2025)
    revenue = np.array([100, 101, 100.5, 102, 101.5, 103])  # almost flat
    users = np.array([12, 20, 35, 52, 74, 98])  # exploding

    ax1.plot(x, revenue, color=TEAL, lw=2.3, marker="o", label="Revenue")
    ax1.set_ylabel("Revenue", color=TEAL)
    ax1.set_ylim(99, 104)
    ax1b = ax1.twinx()
    ax1b.plot(x, users, color=TERRACOTTA, lw=2.3, marker="o", label="Users")
    ax1b.set_ylabel("Users", color=TERRACOTTA)
    ax1b.spines["top"].set_visible(False)
    ax1b.set_ylim(0, 110)
    polish(ax1)
    ax1.set_xlabel("Revenue looks like it 'tracks' users.\nIt barely moved. The axis did the acting.", fontsize=8, color=SLATE)

    # honest: split — we'll draw users on ax2 and annotate revenue
    ax2_top = ax2
    ax2_top.plot(x, revenue, color=TEAL, lw=2.2, marker="o")
    ax2_top.set_ylabel("Revenue")
    ax2_top.set_ylim(0, 120)
    ax2_top.set_title("")
    polish(ax2_top)
    ax2_top.set_xlabel("Revenue on a 0–120 scale: a 3-point drift.\nUsers belong on a separate chart.", fontsize=8, color=SLATE)
    ax2_top.text(2019.1, 110, "Revenue  100 → 103", fontsize=8, color=TEAL, fontweight="bold")
    # small inset bars for users
    inset = ax2.inset_axes([0.48, 0.12, 0.48, 0.42])
    inset.bar(x, users, color=TERRACOTTA, width=0.6)
    inset.set_title("Users", fontsize=7, color=TERRACOTTA)
    inset.tick_params(labelsize=6, length=0)
    inset.set_ylim(0, 110)
    inset.set_facecolor(PAPER)
    for sp in inset.spines.values():
        sp.set_color("#C9BFAE")
        sp.set_linewidth(0.6)
    inset.spines["top"].set_visible(False)
    inset.spines["right"].set_visible(False)
    save(fig, "p05_dualaxis")


def p06_color():
    fig, (ax1, ax2) = pair_axes(h=4.6)
    banner(ax1, "MISLEADING  ·  rainbow heatmap", bad=True)
    banner(ax2, "HONEST  ·  sequential colour", bad=False)

    data = rng.integers(10, 90, (7, 8)).astype(float)
    data[2, 5] = 95
    im1 = ax1.imshow(data, cmap="jet", aspect="auto")
    im2 = ax2.imshow(data, cmap=SEQ, aspect="auto")
    for ax in (ax1, ax2):
        ax.set_xticks(range(8))
        ax.set_xticklabels([f"W{i+1}" for i in range(8)], fontsize=7)
        ax.set_yticks(range(7))
        ax.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], fontsize=7)
        polish(ax, ygrid=False)
    ax1.set_xlabel("Jet creates fake cliffs.\nYellow looks like a category, not a value.", fontsize=8, color=SLATE)
    ax2.set_xlabel("One hue, light → dark.\nQuantity is the only message.", fontsize=8, color=SLATE)
    save(fig, "p06_color")


def p07_decoration():
    fig = plt.figure(figsize=(10.5, 4.7), facecolor=CREAM)
    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    ax2 = fig.add_subplot(1, 2, 2)
    fig.subplots_adjust(wspace=0.22, left=0.04, right=0.97, top=0.84, bottom=0.16)

    ax1.annotate(
        "MISLEADING  ·  3D bars",
        xy=(0.5, 1.08),
        xycoords="axes fraction",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
        color="white",
        bbox=dict(boxstyle="square,pad=0.35", facecolor=TERRACOTTA, edgecolor="none"),
    )
    ax2.annotate(
        "HONEST  ·  2D bars, same data",
        xy=(0.5, 1.08),
        xycoords="axes fraction",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
        color="white",
        bbox=dict(boxstyle="square,pad=0.35", facecolor=TEAL, edgecolor="none"),
    )

    labs = ["A", "B", "C", "D"]
    vals = np.array([42, 55, 48, 51])
    xpos = np.arange(len(vals))
    ax1.bar3d(xpos, np.zeros_like(xpos), np.zeros_like(xpos), 0.6, 0.6, vals,
              color=PALETTE[:4], shade=True, edgecolor=CREAM)
    ax1.set_xticks(xpos)
    ax1.set_xticklabels(labs)
    ax1.set_yticks([])
    ax1.set_zlabel("Value")
    ax1.set_facecolor(CREAM)
    ax1.xaxis.pane.fill = False
    ax1.yaxis.pane.fill = False
    ax1.zaxis.pane.fill = False
    ax1.set_xlabel("Perspective steals height.\nC looks smaller than it is.", fontsize=8, color=SLATE, labelpad=8)

    bars = ax2.bar(labs, vals, color=TEAL, width=0.62, zorder=3)
    bars[1].set_color(TERRACOTTA)
    for b, v in zip(bars, vals):
        ax2.text(b.get_x() + b.get_width() / 2, v + 1, str(v), ha="center", fontsize=8)
    ax2.set_ylim(0, 65)
    ax2.set_ylabel("Value")
    polish(ax2)
    ax2.set_xlabel("Position on a shared axis.\nB is first; the rest are close.", fontsize=8, color=SLATE)
    save(fig, "p07_decoration")


def p08_uncertainty():
    fig, (ax1, ax2) = pair_axes()
    banner(ax1, "MISLEADING  ·  means as exact ranks", bad=True)
    banner(ax2, "HONEST  ·  means + 95% CI", bad=False)

    labs = ["Method A", "Method B", "Method C", "Method D"]
    means = np.array([72.1, 74.0, 71.4, 73.2])
    ci = np.array([3.8, 4.1, 3.6, 3.9])
    order = np.argsort(means)[::-1]

    colors = [TERRACOTTA if i == 0 else TEAL for i in range(4)]
    ax1.bar(np.array(labs)[order], means[order], color=colors, width=0.62, zorder=3)
    ax1.set_ylim(68, 76)
    ax1.set_ylabel("Score")
    polish(ax1)
    ax1.set_xlabel("B 'wins'. The truncated axis\nand missing CI invent a champion.", fontsize=8, color=SLATE)

    x = np.arange(4)
    ax2.bar(x, means, color=TEAL, width=0.55, zorder=3)
    ax2.errorbar(x, means, yerr=ci, fmt="none", ecolor=NAVY, elinewidth=1.3, capsize=5, zorder=4)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labs, fontsize=8)
    ax2.set_ylim(0, 90)
    ax2.set_ylabel("Score")
    polish(ax2)
    ax2.set_xlabel("Every interval overlaps.\nThere is no detectable winner.", fontsize=8, color=SLATE)
    save(fig, "p08_uncertainty")


EXAMPLES = [
    p01_question, p02_position, p03_maps, p04_causation,
    p05_dualaxis, p06_color, p07_decoration, p08_uncertainty,
]


if __name__ == "__main__":
    divider(
        "المبادئ مطبّقة",
        "Principles in practice",
        "نفس البيانات. رسم مضلّل إلى اليسار، ورسم صادق إلى اليمين.",
        "d_principles.png",
    )
    for fn in EXAMPLES:
        fn()
        print("ok", fn.__name__)
    print("done")
