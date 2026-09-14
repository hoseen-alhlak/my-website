#!/usr/bin/env python3
"""Generate atlas chart images with a consistent editorial style."""
from __future__ import annotations

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Wedge, Rectangle, FancyArrowPatch, Arc
from matplotlib.collections import PatchCollection, LineCollection
from matplotlib.sankey import Sankey
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.dates as mdates
from datetime import datetime, timedelta

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from style import PALETTE, NAVY, INK, GOLD, CREAM, PAPER, TERRACOTTA, TEAL, SAGE, CORAL, SLATE, SAND, MUTED, new_fig, polish, save

rng = np.random.default_rng(42)
CMAP = LinearSegmentedColormap.from_list("atlas", ["#F4E6C8", "#C6A15B", "#C45C4A", "#2C6E7A", "#0E2433"])
CMAP2 = LinearSegmentedColormap.from_list("atlas2", ["#EDE4D4", "#8FB3B0", "#2C6E7A", "#0E2433"])


def _cats(n, prefix="فئة"):
    # Latin labels keep matplotlib clean; Arabic lives in the Word text.
    return [f"A{i+1}" for i in range(n)] if False else [
        "North", "South", "East", "West", "Central", "Coast", "Highland", "Valley"
    ][:n]


# ---------------------------------------------------------------------------
# MAGNITUDE
# ---------------------------------------------------------------------------
def chart_column():
    fig, ax = new_fig()
    cats = ["Retail", "Energy", "Health", "Finance", "Industry", "Edu"]
    vals = np.array([42, 67, 55, 81, 36, 48])
    bars = ax.bar(cats, vals, color=TEAL, width=0.62, zorder=3)
    bars[3].set_color(TERRACOTTA)
    ax.set_ylabel("Revenue (m)")
    polish(ax)
    ax.set_ylim(0, 95)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, str(v), ha="center", va="bottom", fontsize=8, color=INK)
    save(fig, "column")


def chart_bar():
    fig, ax = new_fig()
    cats = ["Customer support", "Product quality", "Delivery speed", "Price", "Brand trust", "After-sales"]
    vals = np.array([88, 76, 71, 64, 59, 47])
    y = np.arange(len(cats))
    ax.barh(y, vals, color=TEAL, height=0.58, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(cats)
    ax.invert_yaxis()
    ax.set_xlabel("Satisfaction index")
    polish(ax, ygrid=False, xgrid=True)
    ax.set_xlim(0, 100)
    save(fig, "bar")


def chart_grouped_bar():
    fig, ax = new_fig()
    cats = ["Q1", "Q2", "Q3", "Q4"]
    x = np.arange(len(cats))
    w = 0.25
    a, b, c = [22, 30, 28, 41], [18, 24, 33, 29], [12, 19, 21, 26]
    ax.bar(x - w, a, w, label="Product A", color=TEAL, zorder=3)
    ax.bar(x, b, w, label="Product B", color=TERRACOTTA, zorder=3)
    ax.bar(x + w, c, w, label="Product C", color=GOLD, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(cats)
    ax.set_ylabel("Units (k)")
    ax.legend(ncol=3, loc="upper left")
    polish(ax)
    save(fig, "grouped_bar")


def chart_lollipop():
    fig, ax = new_fig()
    cats = ["Norway", "Sweden", "Denmark", "Finland", "Iceland", "Netherlands"]
    vals = np.array([92, 85, 81, 78, 74, 70])
    y = np.arange(len(cats))
    ax.hlines(y, 0, vals, color=TEAL, linewidth=2, zorder=2)
    ax.scatter(vals, y, s=70, color=TERRACOTTA, zorder=3, edgecolors=NAVY, linewidths=0.4)
    ax.set_yticks(y)
    ax.set_yticklabels(cats)
    ax.invert_yaxis()
    ax.set_xlabel("Index")
    polish(ax, ygrid=False, xgrid=True)
    ax.set_xlim(0, 100)
    save(fig, "lollipop")


def chart_dot_plot():
    fig, ax = new_fig()
    cats = ["Literacy", "Health", "Jobs", "Housing", "Transit", "Safety"]
    y = np.arange(len(cats))
    city_a = [81, 74, 69, 55, 62, 77]
    city_b = [70, 80, 58, 71, 49, 66]
    ax.scatter(city_a, y, s=64, color=TEAL, label="City A", zorder=3)
    ax.scatter(city_b, y, s=64, color=TERRACOTTA, label="City B", zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(cats)
    ax.invert_yaxis()
    ax.set_xlabel("Score")
    ax.legend()
    polish(ax, ygrid=False, xgrid=True)
    save(fig, "dot_plot")


def chart_pictogram():
    fig, ax = new_fig(7.6, 3.8)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5.2)
    ax.axis("off")
    labels = [("On time", 9, TEAL), ("Delayed", 3, TERRACOTTA)]
    y = 3.4
    for lab, n, col in labels:
        ax.text(0.2, y + 0.7, lab, fontsize=10, color=NAVY, fontweight="bold")
        for i in range(10):
            circ = Circle((0.7 + i * 1.05, y), 0.32, facecolor=col if i < n else SAND, edgecolor="none")
            ax.add_patch(circ)
        ax.text(11.4, y, f"{n*10}%", va="center", fontsize=10, color=INK)
        y -= 1.8
    ax.text(0.2, 4.85, "Each circle = 10% of shipments", fontsize=8, color=SLATE)
    save(fig, "pictogram")


def chart_proportional_area():
    fig, ax = new_fig(7.6, 4.2)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.set_aspect("equal")
    ax.axis("off")
    items = [("A", 160, 2.0, 2.4, TEAL), ("B", 90, 5.3, 2.4, TERRACOTTA), ("C", 40, 7.9, 2.4, GOLD)]
    scale = 0.11
    for name, val, x, y, col in items:
        r = math.sqrt(val) * scale
        ax.add_patch(Circle((x, y), r, facecolor=col, alpha=0.9, edgecolor="none"))
        ax.text(x, y, str(val), ha="center", va="center", color="white", fontsize=11, fontweight="bold")
        ax.text(x, 0.45, name, ha="center", color=NAVY, fontsize=10)
    ax.text(0.3, 4.6, "Area encodes value (not radius)", fontsize=8, color=SLATE)
    save(fig, "proportional_area")


def chart_bullet():
    fig, ax = new_fig(7.6, 3.6)
    ranges = [(0, 50, "#E6D9C4"), (50, 75, "#C9B48A"), (75, 100, "#A89060")]
    for a, b, c in ranges:
        ax.barh(0, b - a, left=a, height=0.55, color=c, zorder=1)
    ax.barh(0, 68, height=0.18, color=NAVY, zorder=3)
    ax.plot(80, 0, marker="|", markersize=22, color=TERRACOTTA, markeredgewidth=3, zorder=4)
    ax.set_xlim(0, 100)
    ax.set_yticks([0])
    ax.set_yticklabels(["On-time delivery"])
    ax.set_xlabel("Score  ·  poor / adequate / good   |  target = 80")
    polish(ax, ygrid=False, xgrid=False)
    ax.spines["left"].set_visible(False)
    save(fig, "bullet")


def chart_radial_bar():
    fig, ax = new_fig(6.4, 6.0)
    ax.remove()
    ax = fig.add_subplot(111, polar=True)
    labels = ["Speed", "Quality", "Cost", "Trust", "Reach", "NPS"]
    vals = np.array([70, 85, 55, 78, 62, 90])
    theta = np.linspace(0, 2 * np.pi, len(vals), endpoint=False)
    width = 2 * np.pi / len(vals) * 0.7
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.bar(theta, vals, width=width, color=PALETTE[:6], alpha=0.92, edgecolor=CREAM, linewidth=1)
    ax.set_xticks(theta)
    ax.set_xticklabels(labels)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_ylim(0, 100)
    ax.set_facecolor(PAPER)
    save(fig, "radial_bar")


# ---------------------------------------------------------------------------
# RANKING
# ---------------------------------------------------------------------------
def chart_ordered_bar():
    fig, ax = new_fig()
    cats = ["Team D", "Team A", "Team F", "Team B", "Team E", "Team C"]
    vals = np.array([96, 88, 81, 74, 61, 52])
    colors = [TERRACOTTA if i == 0 else TEAL for i in range(len(vals))]
    y = np.arange(len(cats))
    ax.barh(y, vals, color=colors, height=0.58, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(cats)
    ax.invert_yaxis()
    ax.set_xlabel("Performance score")
    polish(ax, ygrid=False, xgrid=True)
    save(fig, "ordered_bar")


def chart_slope():
    fig, ax = new_fig()
    names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
    y1 = np.array([80, 65, 50, 40, 30])
    y2 = np.array([70, 78, 35, 55, 48])
    for n, a, b in zip(names, y1, y2):
        col = TEAL if b >= a else TERRACOTTA
        ax.plot([0, 1], [a, b], color=col, lw=2.2, zorder=2)
        ax.scatter([0, 1], [a, b], color=col, s=36, zorder=3)
        ax.text(-0.06, a, f"{n}  {a}", ha="right", va="center", fontsize=8)
        ax.text(1.06, b, str(b), ha="left", va="center", fontsize=8, color=col)
    ax.set_xlim(-0.45, 1.35)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["2020", "2025"])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    polish(ax, ygrid=False)
    save(fig, "slope")


def chart_bump():
    fig, ax = new_fig()
    years = np.array([2019, 2020, 2021, 2022, 2023, 2024])
    ranks = {
        "A": [1, 1, 2, 2, 1, 1],
        "B": [2, 3, 3, 1, 2, 3],
        "C": [3, 2, 1, 3, 3, 2],
        "D": [4, 4, 4, 4, 4, 4],
    }
    for (name, r), col in zip(ranks.items(), PALETTE):
        ax.plot(years, r, color=col, lw=2.4, marker="o", ms=7, label=name)
    ax.invert_yaxis()
    ax.set_yticks([1, 2, 3, 4])
    ax.set_ylabel("Rank")
    ax.legend(ncol=4, loc="lower left")
    polish(ax, xgrid=True)
    save(fig, "bump")


def chart_dumbbell():
    fig, ax = new_fig()
    cats = ["Region 1", "Region 2", "Region 3", "Region 4", "Region 5"]
    a = np.array([32, 45, 28, 51, 40])
    b = np.array([48, 41, 44, 60, 38])
    y = np.arange(len(cats))
    ax.hlines(y, a, b, color=SAND, lw=3, zorder=1)
    ax.scatter(a, y, s=70, color=TEAL, zorder=3, label="2018")
    ax.scatter(b, y, s=70, color=TERRACOTTA, zorder=3, label="2025")
    ax.set_yticks(y)
    ax.set_yticklabels(cats)
    ax.invert_yaxis()
    ax.set_xlabel("Rate (%)")
    ax.legend()
    polish(ax, ygrid=False, xgrid=True)
    save(fig, "dumbbell")


# ---------------------------------------------------------------------------
# DEVIATION
# ---------------------------------------------------------------------------
def chart_diverging_bar():
    fig, ax = new_fig()
    cats = ["Trade", "Energy", "Tourism", "Agriculture", "Tech", "Finance"]
    vals = np.array([12, -8, 5, -15, 22, -3])
    colors = [TEAL if v >= 0 else TERRACOTTA for v in vals]
    y = np.arange(len(cats))
    ax.barh(y, vals, color=colors, height=0.62, zorder=3)
    ax.axvline(0, color=NAVY, lw=0.9)
    ax.set_yticks(y)
    ax.set_yticklabels(cats)
    ax.set_xlabel("Change vs. baseline (%)")
    polish(ax, ygrid=False, xgrid=True)
    save(fig, "diverging_bar")


def chart_butterfly():
    fig, ax = new_fig()
    ages = ["0-14", "15-24", "25-34", "35-44", "45-54", "55-64", "65+"]
    male = np.array([12, 9, 11, 10, 8, 7, 5])
    female = np.array([11, 8.5, 10.5, 10, 8.5, 7.5, 6])
    y = np.arange(len(ages))
    ax.barh(y, -male, color=TEAL, height=0.7, label="Male")
    ax.barh(y, female, color=CORAL, height=0.7, label="Female")
    ax.set_yticks(y)
    ax.set_yticklabels(ages)
    ax.set_xlabel("Share of population (%)")
    xt = np.array([-12, -8, -4, 0, 4, 8, 12])
    ax.set_xticks(xt)
    ax.set_xticklabels([abs(t) for t in xt])
    ax.axvline(0, color=NAVY, lw=0.8)
    ax.legend(loc="lower right")
    polish(ax, ygrid=False, xgrid=True)
    save(fig, "butterfly")


def chart_surplus_deficit():
    fig, ax = new_fig()
    x = np.arange(2014, 2025)
    y = np.array([4, 2, -1, -3, -5, -2, 1, 3, 2, -1, 2.5])
    ax.fill_between(x, y, 0, where=y >= 0, color=TEAL, alpha=0.85, interpolate=True)
    ax.fill_between(x, y, 0, where=y < 0, color=TERRACOTTA, alpha=0.85, interpolate=True)
    ax.plot(x, y, color=NAVY, lw=1.4)
    ax.axhline(0, color=NAVY, lw=0.8)
    ax.set_ylabel("Balance (% of GDP)")
    polish(ax)
    save(fig, "surplus_deficit")


# ---------------------------------------------------------------------------
# DISTRIBUTION
# ---------------------------------------------------------------------------
def chart_histogram():
    fig, ax = new_fig()
    data = rng.normal(72, 12, 400)
    ax.hist(data, bins=18, color=TEAL, edgecolor=CREAM, linewidth=0.6, zorder=3)
    ax.axvline(np.median(data), color=TERRACOTTA, lw=1.8, ls="--", label="Median")
    ax.set_xlabel("Exam score")
    ax.set_ylabel("Count")
    ax.legend()
    polish(ax)
    save(fig, "histogram")


def chart_density():
    fig, ax = new_fig()
    from scipy.stats import gaussian_kde

    for mu, sd, col, lab in [(68, 8, TEAL, "Group A"), (74, 10, TERRACOTTA, "Group B")]:
        d = rng.normal(mu, sd, 350)
        xs = np.linspace(35, 110, 250)
        kde = gaussian_kde(d)
        ys = kde(xs)
        ax.fill_between(xs, ys, color=col, alpha=0.35)
        ax.plot(xs, ys, color=col, lw=2, label=lab)
    ax.set_xlabel("Value")
    ax.set_ylabel("Density")
    ax.legend()
    polish(ax)
    save(fig, "density")


def chart_boxplot():
    fig, ax = new_fig()
    data = [rng.normal(m, s, 80) for m, s in [(20, 4), (24, 5), (18, 3.5), (30, 6), (22, 4.5)]]
    bp = ax.boxplot(data, patch_artist=True, widths=0.55, medianprops=dict(color=NAVY, lw=1.6))
    for i, box in enumerate(bp["boxes"]):
        box.set_facecolor(PALETTE[i])
        box.set_alpha(0.85)
        box.set_edgecolor(NAVY)
        box.set_linewidth(0.8)
    for el in bp["whiskers"] + bp["caps"]:
        el.set_color(SLATE)
    ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May"])
    ax.set_ylabel("Delivery time (days)")
    polish(ax)
    save(fig, "boxplot")


def chart_violin():
    fig, ax = new_fig()
    data = [rng.normal(m, s, 120) for m, s in [(5, 1.2), (6.2, 1.6), (4.8, 0.9), (7.1, 1.8)]]
    parts = ax.violinplot(data, showmeans=False, showmedians=True, showextrema=False)
    for i, b in enumerate(parts["bodies"]):
        b.set_facecolor(PALETTE[i])
        b.set_alpha(0.85)
        b.set_edgecolor(NAVY)
    parts["cmedians"].set_color(NAVY)
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xticklabels(["A", "B", "C", "D"])
    ax.set_ylabel("Response time (s)")
    polish(ax)
    save(fig, "violin")


def chart_beeswarm():
    fig, ax = new_fig()
    for i, (mu, sd, col) in enumerate([(10, 2, TEAL), (13, 2.4, TERRACOTTA), (9, 1.6, GOLD)]):
        y = rng.normal(mu, sd, 70)
        x = i + rng.normal(0, 0.07, 70)
        ax.scatter(x, y, s=14, color=col, alpha=0.75, edgecolors="none", zorder=3)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["Control", "Trial A", "Trial B"])
    ax.set_ylabel("Score")
    polish(ax)
    save(fig, "beeswarm")


def chart_ridgeline():
    fig, ax = new_fig(7.6, 5.0)
    from scipy.stats import gaussian_kde

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    xs = np.linspace(0, 20, 200)
    for i, m in enumerate(months):
        d = rng.normal(8 + i * 0.6, 2.2 - i * 0.12, 200)
        kde = gaussian_kde(d)
        ys = kde(xs)
        ys = ys / ys.max() * 0.9
        offset = len(months) - i
        ax.fill_between(xs, offset, offset + ys, color=PALETTE[i], alpha=0.85, zorder=i)
        ax.plot(xs, offset + ys, color=NAVY, lw=0.6, zorder=i)
        ax.text(-0.4, offset, m, ha="right", va="bottom", fontsize=8, color=NAVY)
    ax.set_yticks([])
    ax.set_xlabel("Daily demand")
    ax.set_xlim(-2.5, 20)
    polish(ax, ygrid=False)
    ax.spines["left"].set_visible(False)
    save(fig, "ridgeline")


def chart_strip():
    fig, ax = new_fig()
    for i, mu in enumerate([12, 15, 11, 18]):
        y = rng.normal(mu, 2.5, 40)
        ax.scatter(y, np.full_like(y, i) + rng.uniform(-0.12, 0.12, 40), s=18, color=PALETTE[i], alpha=0.8, zorder=3)
    ax.set_yticks([0, 1, 2, 3])
    ax.set_yticklabels(["Site A", "Site B", "Site C", "Site D"])
    ax.set_xlabel("Measurement")
    polish(ax, ygrid=False, xgrid=True)
    save(fig, "strip")


def chart_qq():
    from scipy import stats

    fig, ax = new_fig()
    sample = rng.normal(0, 1, 120)
    osm, osr = stats.probplot(sample, dist="norm")[0]
    ax.scatter(osm, osr, s=18, color=TEAL, alpha=0.85, zorder=3)
    ax.plot(osm, osm, color=TERRACOTTA, lw=1.4)
    ax.set_xlabel("Theoretical quantiles")
    ax.set_ylabel("Sample quantiles")
    polish(ax, xgrid=True)
    save(fig, "qq")


def chart_ecdf():
    fig, ax = new_fig()
    for mu, col, lab in [(50, TEAL, "A"), (58, TERRACOTTA, "B")]:
        d = np.sort(rng.normal(mu, 8, 150))
        y = np.arange(1, len(d) + 1) / len(d)
        ax.step(d, y, where="post", color=col, lw=2, label=lab)
    ax.set_xlabel("Value")
    ax.set_ylabel("Cumulative probability")
    ax.legend()
    polish(ax)
    save(fig, "ecdf")


# ---------------------------------------------------------------------------
# CORRELATION
# ---------------------------------------------------------------------------
def chart_scatter():
    fig, ax = new_fig()
    x = rng.normal(50, 12, 80)
    y = 0.7 * x + rng.normal(10, 8, 80)
    ax.scatter(x, y, s=32, color=TEAL, alpha=0.8, edgecolors=NAVY, linewidths=0.3, zorder=3)
    z = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, np.polyval(z, xs), color=TERRACOTTA, lw=1.6)
    ax.set_xlabel("Ad spend")
    ax.set_ylabel("Conversions")
    polish(ax, xgrid=True)
    save(fig, "scatter")


def chart_bubble():
    fig, ax = new_fig()
    x = rng.uniform(10, 90, 18)
    y = rng.uniform(15, 85, 18)
    s = rng.uniform(80, 900, 18)
    colors = (PALETTE * 3)[: len(x)]
    ax.scatter(x, y, s=s, c=colors, alpha=0.7, edgecolors=NAVY, linewidths=0.4, zorder=3)
    ax.set_xlabel("GDP per capita")
    ax.set_ylabel("Life expectancy")
    polish(ax, xgrid=True)
    save(fig, "bubble")


def chart_hexbin():
    fig, ax = new_fig()
    x = rng.normal(0, 1, 2000)
    y = x * 0.55 + rng.normal(0, 0.8, 2000)
    hb = ax.hexbin(x, y, gridsize=22, cmap=CMAP2, mincnt=1)
    fig.colorbar(hb, ax=ax, fraction=0.046, pad=0.03)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    polish(ax, ygrid=False)
    save(fig, "hexbin")


def chart_density2d():
    fig, ax = new_fig()
    x = rng.normal(0, 1, 800)
    y = x * 0.4 + rng.normal(0, 0.9, 800)
    ax.hist2d(x, y, bins=28, cmap=CMAP2)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    polish(ax, ygrid=False)
    save(fig, "density2d")


def chart_connected_scatter():
    fig, ax = new_fig()
    t = np.arange(12)
    x = 20 + np.cumsum(rng.normal(1.2, 2, 12))
    y = 15 + np.cumsum(rng.normal(0.8, 2.2, 12))
    ax.plot(x, y, color=TEAL, lw=1.6, marker="o", ms=6, zorder=3)
    ax.scatter(x[0], y[0], s=80, color=SAGE, zorder=4)
    ax.scatter(x[-1], y[-1], s=80, color=TERRACOTTA, zorder=4)
    ax.annotate("Start", (x[0], y[0]), xytext=(8, 8), textcoords="offset points", fontsize=8)
    ax.annotate("End", (x[-1], y[-1]), xytext=(8, 8), textcoords="offset points", fontsize=8)
    ax.set_xlabel("Unemployment")
    ax.set_ylabel("Inflation")
    polish(ax, xgrid=True)
    save(fig, "connected_scatter")


def chart_corr_heatmap():
    fig, ax = new_fig(6.4, 5.4)
    vars_ = ["Rev", "Cost", "NPS", "Churn", "Ads", "Staff"]
    n = len(vars_)
    m = rng.normal(0, 0.3, (n, n))
    m = (m + m.T) / 2
    np.fill_diagonal(m, 1)
    im = ax.imshow(m, cmap=CMAP, vmin=-1, vmax=1)
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(vars_)
    ax.set_yticklabels(vars_)
    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{m[i, j]:.1f}", ha="center", va="center", fontsize=7.5, color="white" if abs(m[i, j]) > 0.55 else INK)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    polish(ax, ygrid=False)
    save(fig, "corr_heatmap")


def chart_parallel():
    fig, ax = new_fig(7.8, 4.3)
    dims = ["Speed", "Quality", "Price", "Design", "Support"]
    data = rng.uniform(0.2, 1, (8, 5))
    data[:, 2] = 1 - data[:, 0] * 0.5 + rng.uniform(0, 0.2, 8)
    x = np.arange(5)
    for i, row in enumerate(data):
        ax.plot(x, row, color=PALETTE[i % len(PALETTE)], lw=1.6, alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(dims)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Normalized score")
    polish(ax, xgrid=True)
    save(fig, "parallel")


# ---------------------------------------------------------------------------
# TIME
# ---------------------------------------------------------------------------
def chart_line():
    fig, ax = new_fig()
    x = np.arange(2014, 2026)
    y = 40 + np.cumsum(rng.normal(1.4, 2.2, len(x)))
    ax.plot(x, y, color=TEAL, lw=2.4, marker="o", ms=4.5, zorder=3)
    ax.fill_between(x, y, y.min() - 4, color=TEAL, alpha=0.12)
    ax.set_ylabel("Index")
    polish(ax)
    save(fig, "line")


def chart_multiline():
    fig, ax = new_fig()
    x = np.arange(2016, 2026)
    for i, lab in enumerate(["Series A", "Series B", "Series C"]):
        y = 30 + i * 8 + np.cumsum(rng.normal(0.8, 1.8, len(x)))
        ax.plot(x, y, color=PALETTE[i], lw=2.2, label=lab)
    ax.legend()
    ax.set_ylabel("Users (k)")
    polish(ax)
    save(fig, "multiline")


def chart_area():
    fig, ax = new_fig()
    x = np.arange(12)
    y = 20 + np.sin(x / 2) * 8 + x
    ax.fill_between(x, y, color=TEAL, alpha=0.45)
    ax.plot(x, y, color=TEAL, lw=2)
    ax.set_xticks(x)
    ax.set_xticklabels(list("JFMAMJJASOND"))
    ax.set_ylabel("Stock")
    polish(ax)
    save(fig, "area")


def chart_stacked_area():
    fig, ax = new_fig()
    x = np.arange(2016, 2026)
    a = 20 + np.linspace(0, 8, 10)
    b = 15 + np.linspace(0, 3, 10)
    c = 10 + np.linspace(2, 0, 10)
    ax.stackplot(x, a, b, c, colors=[TEAL, GOLD, TERRACOTTA], labels=["Core", "Plus", "Other"], alpha=0.9)
    ax.legend(loc="upper left")
    ax.set_ylabel("Revenue")
    polish(ax)
    save(fig, "stacked_area")


def chart_streamgraph():
    fig, ax = new_fig()
    x = np.linspace(0, 10, 80)
    layers = []
    for i, k in enumerate([0.6, 1.1, 0.8, 1.4, 0.9]):
        layers.append((np.sin(x * k + i) + 1.2) * (1.4 + 0.3 * i))
    layers = np.array(layers)
    ax.stackplot(x, layers, baseline="sym", colors=PALETTE[:5], alpha=0.92)
    ax.set_yticks([])
    ax.set_xlabel("Time")
    polish(ax, ygrid=False)
    ax.spines["left"].set_visible(False)
    save(fig, "streamgraph")


def chart_step():
    fig, ax = new_fig()
    x = np.arange(10)
    y = np.array([2, 2, 5, 5, 5, 8, 8, 3, 3, 6])
    ax.step(x, y, where="post", color=TEAL, lw=2.2)
    ax.fill_between(x, y, step="post", color=TEAL, alpha=0.18)
    ax.set_ylabel("Price tier")
    ax.set_xlabel("Week")
    polish(ax)
    save(fig, "step")


def chart_candlestick():
    fig, ax = new_fig()
    n = 18
    close = 100 + np.cumsum(rng.normal(0.2, 1.6, n))
    open_ = close + rng.normal(0, 1.1, n)
    high = np.maximum(open_, close) + rng.uniform(0.3, 2.0, n)
    low = np.minimum(open_, close) - rng.uniform(0.3, 2.0, n)
    for i in range(n):
        col = TEAL if close[i] >= open_[i] else TERRACOTTA
        ax.vlines(i, low[i], high[i], color=col, lw=1)
        ax.add_patch(Rectangle((i - 0.28, min(open_[i], close[i])), 0.56, abs(close[i] - open_[i]) + 0.05, facecolor=col, edgecolor=col))
    ax.set_ylabel("Price")
    ax.set_xlabel("Session")
    polish(ax)
    save(fig, "candlestick")


def chart_calendar_heatmap():
    fig, ax = new_fig(7.8, 2.8)
    data = rng.integers(0, 10, (7, 16))
    im = ax.imshow(data, cmap=CMAP2, aspect="auto")
    ax.set_yticks(range(7))
    ax.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    ax.set_xticks([])
    ax.set_xlabel("Weeks")
    polish(ax, ygrid=False)
    save(fig, "calendar_heatmap")


def chart_sparkline_panel():
    fig, axes = plt.subplots(4, 1, figsize=(7.6, 4.0), sharex=True)
    names = ["Revenue", "Users", "Churn", "NPS"]
    for ax, name, col in zip(axes, names, PALETTE):
        y = 10 + np.cumsum(rng.normal(0, 1, 30))
        ax.plot(y, color=col, lw=1.6)
        ax.fill_between(np.arange(30), y, alpha=0.12, color=col)
        ax.set_ylabel(name, rotation=0, ha="right", va="center", fontsize=8)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(length=0)
    axes[-1].set_xlabel("Last 30 days")
    fig.tight_layout()
    save(fig, "sparkline")


def chart_control():
    fig, ax = new_fig()
    y = rng.normal(50, 3.2, 28)
    y[17] = 64
    x = np.arange(1, 29)
    mu, sd = 50, 3.2
    ax.plot(x, y, color=TEAL, marker="o", ms=4, lw=1.5)
    ax.axhline(mu, color=NAVY, lw=1)
    ax.axhline(mu + 3 * sd, color=TERRACOTTA, ls="--", lw=1)
    ax.axhline(mu - 3 * sd, color=TERRACOTTA, ls="--", lw=1)
    ax.scatter([18], [64], s=70, color=TERRACOTTA, zorder=4)
    ax.set_ylabel("Measurement")
    ax.set_xlabel("Sample")
    polish(ax)
    save(fig, "control")


def chart_fan():
    fig, ax = new_fig()
    x = np.arange(0, 16)
    y = 20 + np.cumsum(np.concatenate([rng.normal(0.6, 0.8, 10), np.zeros(6)]))
    y[10:] = y[9] + np.arange(1, 7) * 0.7
    ax.plot(x[:10], y[:10], color=TEAL, lw=2.2)
    for k, a in [(4, 0.15), (2.5, 0.28), (1.2, 0.45)]:
        lo = y[9:] - k * np.sqrt(np.arange(7))
        hi = y[9:] + k * np.sqrt(np.arange(7))
        ax.fill_between(x[9:], lo, hi, color=TEAL, alpha=a, linewidth=0)
    ax.plot(x[9:], y[9:], color=TEAL, lw=1.5, ls="--")
    ax.axvline(9, color=MUTED, lw=0.8, ls=":")
    ax.set_ylabel("Forecast")
    polish(ax)
    save(fig, "fan")


# ---------------------------------------------------------------------------
# PART TO WHOLE
# ---------------------------------------------------------------------------
def chart_pie():
    fig, ax = new_fig(6.2, 4.4)
    sizes = [38, 24, 18, 12, 8]
    labels = ["A", "B", "C", "D", "E"]
    explode = (0.03, 0, 0, 0, 0)
    ax.pie(sizes, labels=labels, colors=PALETTE[:5], startangle=90, explode=explode, wedgeprops=dict(width=1, edgecolor=CREAM, linewidth=1.5), autopct="%1.0f%%", pctdistance=0.72)
    ax.set_aspect("equal")
    save(fig, "pie")


def chart_donut():
    fig, ax = new_fig(6.2, 4.4)
    sizes = [42, 28, 18, 12]
    wedges, *_ = ax.pie(sizes, colors=PALETTE[:4], startangle=90, wedgeprops=dict(width=0.42, edgecolor=CREAM, linewidth=2))
    ax.text(0, 0, "100%\nshare", ha="center", va="center", fontsize=11, color=NAVY, fontweight="bold")
    ax.legend(wedges, ["Core 42%", "Plus 28%", "Labs 18%", "Other 12%"], loc="center left", bbox_to_anchor=(0.95, 0.5))
    save(fig, "donut")


def chart_waffle():
    fig, ax = new_fig(6.4, 4.0)
    ax.set_aspect("equal")
    values = [42, 27, 18, 13]
    cols = PALETTE[:4]
    cells = []
    for v, c in zip(values, cols):
        cells += [c] * v
    for i, c in enumerate(cells[:100]):
        r, col = divmod(i, 10)
        ax.add_patch(Rectangle((col, 9 - r), 0.88, 0.88, facecolor=c, edgecolor=CREAM, linewidth=1.2))
    ax.set_xlim(-0.2, 13.5)
    ax.set_ylim(-0.2, 10.2)
    ax.axis("off")
    for i, (lab, v) in enumerate(zip(["A", "B", "C", "D"], values)):
        ax.add_patch(Rectangle((10.6, 8.2 - i * 1.3), 0.5, 0.5, facecolor=cols[i], edgecolor="none"))
        ax.text(11.3, 8.35 - i * 1.3, f"{lab}  {v}%", va="center", fontsize=9)
    save(fig, "waffle")


def chart_stacked_bar():
    fig, ax = new_fig()
    cats = ["Q1", "Q2", "Q3", "Q4"]
    a, b, c = [20, 22, 25, 30], [12, 15, 14, 18], [8, 9, 11, 10]
    ax.bar(cats, a, color=TEAL, label="New")
    ax.bar(cats, b, bottom=a, color=GOLD, label="Renewal")
    ax.bar(cats, c, bottom=np.array(a) + np.array(b), color=TERRACOTTA, label="Expansion")
    ax.set_ylabel("Revenue")
    ax.legend()
    polish(ax)
    save(fig, "stacked_bar")


def chart_stacked100():
    fig, ax = new_fig()
    cats = ["2019", "2020", "2021", "2022", "2023", "2024"]
    raw = np.array([[40, 35, 30, 28, 25, 22], [35, 38, 40, 42, 44, 46], [25, 27, 30, 30, 31, 32]], dtype=float)
    raw = raw / raw.sum(axis=0) * 100
    ax.bar(cats, raw[0], color=TEAL, label="On-prem")
    ax.bar(cats, raw[1], bottom=raw[0], color=GOLD, label="Hybrid")
    ax.bar(cats, raw[2], bottom=raw[0] + raw[1], color=TERRACOTTA, label="Cloud")
    ax.set_ylabel("Share (%)")
    ax.set_ylim(0, 100)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.12))
    polish(ax)
    save(fig, "stacked100")


def _squarify(values, x, y, w, h):
    """Simple squarified-ish treemap (slice-and-dice by remaining space)."""
    values = [float(v) for v in values]
    total = sum(values)
    rects = []
    for i, v in enumerate(values):
        if total <= 0:
            break
        frac = v / total
        if w >= h:
            rw = w * frac
            rects.append((x, y, rw, h))
            x += rw
            w -= rw
        else:
            rh = h * frac
            rects.append((x, y, w, rh))
            y += rh
            h -= rh
        total -= v
    return rects


def chart_treemap():
    fig, ax = new_fig(7.6, 4.4)
    labels = ["Mobile", "Web", "Store", "Partners", "Other", "Events"]
    vals = [38, 22, 16, 12, 8, 4]
    rects = _squarify(vals, 0, 0, 10, 6)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.set_aspect("equal")
    ax.axis("off")
    for (x, y, w, h), lab, v, c in zip(rects, labels, vals, PALETTE):
        ax.add_patch(Rectangle((x, y), w, h, facecolor=c, edgecolor=CREAM, linewidth=2))
        if w * h > 3:
            ax.text(x + w / 2, y + h / 2 + 0.15, lab, ha="center", va="center", color="white", fontsize=9, fontweight="bold")
            ax.text(x + w / 2, y + h / 2 - 0.25, f"{v}%", ha="center", va="center", color="white", fontsize=8)
    save(fig, "treemap")


def chart_sunburst():
    fig, ax = new_fig(6.2, 5.2)
    ax.set_aspect("equal")
    ax.axis("off")
    # inner ring
    inner = [40, 35, 25]
    outer = [18, 22, 20, 15, 12, 13]
    ax.pie(inner, radius=0.55, colors=[TEAL, TERRACOTTA, GOLD], wedgeprops=dict(width=0.28, edgecolor=CREAM, linewidth=2))
    ax.pie(outer, radius=0.92, colors=[PALETTE[i % len(PALETTE)] for i in range(6)], wedgeprops=dict(width=0.32, edgecolor=CREAM, linewidth=2))
    ax.text(0, 0, "All", ha="center", va="center", fontsize=11, color=NAVY, fontweight="bold")
    save(fig, "sunburst")


def chart_marimekko():
    fig, ax = new_fig()
    widths = np.array([0.35, 0.25, 0.22, 0.18])
    stacks = np.array([[0.5, 0.4, 0.55, 0.3], [0.3, 0.35, 0.25, 0.45], [0.2, 0.25, 0.2, 0.25]])
    x0 = 0
    cats = ["EU", "US", "ASIA", "ROW"]
    for i, w in enumerate(widths):
        bottom = 0
        for j, col in enumerate([TEAL, GOLD, TERRACOTTA]):
            h = stacks[j, i]
            ax.add_patch(Rectangle((x0, bottom), w, h, facecolor=col, edgecolor=CREAM, linewidth=1.5))
            bottom += h
        ax.text(x0 + w / 2, -0.06, cats[i], ha="center", va="top", fontsize=8)
        x0 += w
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.12, 1)
    ax.set_yticks([0, 0.5, 1])
    ax.set_yticklabels(["0%", "50%", "100%"])
    ax.set_xticks([])
    polish(ax, ygrid=False)
    save(fig, "marimekko")


def chart_circle_pack():
    fig, ax = new_fig(6.6, 5.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-4.2, 4.2)
    ax.set_ylim(-3.4, 3.6)
    circles = [
        (0, 0.2, 1.8, TEAL, "Core"),
        (-2.3, -0.6, 1.1, TERRACOTTA, "West"),
        (2.35, -0.4, 1.05, GOLD, "East"),
        (0.2, 2.35, 0.85, SAGE, "North"),
        (-1.6, 1.7, 0.7, CORAL, "Labs"),
        (1.7, 1.85, 0.62, PALETTE[5], "New"),
    ]
    for x, y, r, c, lab in circles:
        ax.add_patch(Circle((x, y), r, facecolor=c, alpha=0.88, edgecolor=CREAM, linewidth=2))
        ax.text(x, y, lab, ha="center", va="center", color="white", fontsize=8, fontweight="bold")
    save(fig, "circle_pack")


def chart_waterfall():
    fig, ax = new_fig()
    labels = ["Start", "New", "Price", "Churn", "Cost", "End"]
    deltas = [80, 18, 8, -12, -9, 0]
    # last is total
    running = 0
    xs = np.arange(len(labels))
    bottoms = []
    heights = []
    colors = []
    for i, d in enumerate(deltas):
        if i == 0 or i == len(deltas) - 1:
            if i == len(deltas) - 1:
                d = running
            bottoms.append(0)
            heights.append(d)
            colors.append(NAVY if i == 0 or i == len(deltas) - 1 else TEAL)
            running = d if i == 0 else running
        else:
            if d >= 0:
                bottoms.append(running)
                heights.append(d)
                colors.append(TEAL)
                running += d
            else:
                running += d
                bottoms.append(running)
                heights.append(-d)
                colors.append(TERRACOTTA)
    ax.bar(xs, heights, bottom=bottoms, color=colors, width=0.62, zorder=3)
    run_val = float(deltas[0])
    for i, d in enumerate(deltas[1:-1], start=1):
        ax.plot([i - 1 + 0.31, i - 0.31], [run_val, run_val], color=MUTED, lw=0.8)
        run_val += d
    ax.set_xticks(xs)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Value")
    polish(ax)
    save(fig, "waterfall")


def chart_funnel():
    fig, ax = new_fig(6.6, 4.6)
    stages = [("Visits", 100), ("Leads", 62), ("Trials", 34), ("Paid", 18), ("Renew", 11)]
    ax.set_xlim(-60, 60)
    ax.set_ylim(-0.6, 5.4)
    ax.axis("off")
    for i, (lab, v) in enumerate(stages):
        y = 4.6 - i
        w = v * 0.5
        col = PALETTE[i]
        ax.fill([ -w, w, w * 0.86, -w * 0.86], [y, y, y - 0.78, y - 0.78], color=col, alpha=0.92)
        ax.text(0, y - 0.4, f"{lab}  ·  {v}", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
    save(fig, "funnel")


def chart_pyramid():
    fig, ax = new_fig(6.4, 4.6)
    layers = [("Vision", 0.9, NAVY), ("Strategy", 1.5, TEAL), ("Ops", 2.2, GOLD), ("Execution", 3.1, TERRACOTTA)]
    y = 0
    ax.set_xlim(-4, 4)
    ax.set_ylim(-0.2, 4.4)
    ax.axis("off")
    for lab, w, col in reversed(layers):
        ax.fill([-w, w, w - 0.15, -w + 0.15], [y, y, y + 0.85, y + 0.85], color=col)
        ax.text(0, y + 0.42, lab, ha="center", va="center", color="white", fontsize=10, fontweight="bold")
        y += 0.95
    save(fig, "pyramid")


# ---------------------------------------------------------------------------
# SPATIAL
# ---------------------------------------------------------------------------
def chart_choropleth():
    fig, ax = new_fig(7.2, 4.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.2)
    # stylised regions
    regions = [
        [(0.4, 0.5), (3.2, 0.4), (3.4, 2.8), (0.6, 3.0)],
        [(3.2, 0.4), (6.5, 0.6), (6.2, 3.1), (3.4, 2.8)],
        [(6.5, 0.6), (9.5, 0.8), (9.4, 3.3), (6.2, 3.1)],
        [(0.6, 3.0), (3.4, 2.8), (3.6, 5.5), (0.8, 5.4)],
        [(3.4, 2.8), (6.2, 3.1), (6.4, 5.6), (3.6, 5.5)],
        [(6.2, 3.1), (9.4, 3.3), (9.3, 5.5), (6.4, 5.6)],
    ]
    vals = [0.2, 0.45, 0.7, 0.35, 0.9, 0.55]
    from matplotlib.colors import Normalize
    import matplotlib.cm as cm

    for poly, v in zip(regions, vals):
        xs, ys = zip(*poly)
        ax.fill(xs, ys, color=CMAP2(v), edgecolor=CREAM, linewidth=2)
    for i, (poly, v) in enumerate(zip(regions, vals), 1):
        xs, ys = zip(*poly)
        ax.text(sum(xs) / 4, sum(ys) / 4, f"R{i}", ha="center", va="center", color=NAVY if v < 0.6 else "white", fontsize=8)
    sm = plt.cm.ScalarMappable(cmap=CMAP2, norm=Normalize(0, 1))
    cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("Rate")
    save(fig, "choropleth")


def chart_bubble_map():
    fig, ax = new_fig(7.2, 4.6)
    ax.set_aspect("equal")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    # faint land blobs
    ax.add_patch(Circle((3.2, 3.1), 2.2, facecolor=SAND, edgecolor="none", alpha=0.7))
    ax.add_patch(Circle((6.8, 2.6), 1.8, facecolor=SAND, edgecolor="none", alpha=0.7))
    ax.add_patch(Circle((5.0, 4.3), 1.1, facecolor=SAND, edgecolor="none", alpha=0.7))
    pts = [(2.4, 3.4, 420), (3.6, 2.5, 260), (4.8, 3.8, 180), (6.4, 2.2, 500), (7.4, 3.3, 220), (5.5, 1.6, 90)]
    for x, y, s in pts:
        ax.scatter([x], [y], s=s, color=TEAL, alpha=0.55, edgecolors=NAVY, linewidths=0.5, zorder=3)
    ax.axis("off")
    save(fig, "bubble_map")


def chart_dot_density():
    fig, ax = new_fig(7.2, 4.4)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.add_patch(Rectangle((0.4, 0.4), 9.2, 5.2, facecolor="#EFE6D6", edgecolor=SAND, lw=1))
    clusters = [((2.5, 2.2), 80), ((5.2, 3.8), 50), ((7.6, 2.4), 70), ((4.0, 4.6), 25)]
    for (cx, cy), n in clusters:
        xs = rng.normal(cx, 0.55, n)
        ys = rng.normal(cy, 0.4, n)
        ax.scatter(xs, ys, s=8, color=TEAL, alpha=0.75, edgecolors="none")
    save(fig, "dot_density")


def chart_connection_map():
    fig, ax = new_fig(7.2, 4.6)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.add_patch(Circle((5, 3), 2.8, facecolor=SAND, edgecolor="none", alpha=0.55))
    hubs = {"A": (3.2, 3.8), "B": (6.8, 4.0), "C": (7.2, 2.0), "D": (4.4, 1.6), "E": (5.1, 3.2)}
    pairs = [("A", "B"), ("A", "E"), ("B", "C"), ("C", "D"), ("D", "E"), ("B", "E")]
    for a, b in pairs:
        x1, y1 = hubs[a]
        x2, y2 = hubs[b]
        rad = 0.15 if abs(x2 - x1) > 1 else 0.25
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-", color=TEAL, lw=1.6, connectionstyle=f"arc3,rad={rad}", alpha=0.8))
    for k, (x, y) in hubs.items():
        ax.scatter([x], [y], s=90, color=TERRACOTTA, zorder=4, edgecolors=NAVY, linewidths=0.4)
        ax.text(x, y + 0.28, k, ha="center", fontsize=8, color=NAVY)
    save(fig, "connection_map")


# ---------------------------------------------------------------------------
# FLOW / NETWORK
# ---------------------------------------------------------------------------
def chart_sankey():
    fig, ax = new_fig(7.8, 4.6)
    ax.axis("off")
    sankey = Sankey(ax=ax, scale=0.012, offset=0.22, head_angle=120, format="%.0f", unit="%")
    sankey.add(flows=[40, 25, 35, -30, -40, -30], labels=["In A", "In B", "In C", "Out X", "Out Y", "Out Z"], orientations=[1, 0, -1, 1, 0, -1], facecolor=TEAL, alpha=0.85)
    sankey.finish()
    save(fig, "sankey")


def chart_chord():
    fig, ax = new_fig(6.2, 5.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    n = 6
    labels = list("ABCDEF")
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    # arcs
    for i, t in enumerate(theta):
        wedge = Wedge((0, 0), 1.0, np.degrees(t) - 22, np.degrees(t) + 22, width=0.12, facecolor=PALETTE[i], edgecolor=CREAM)
        ax.add_patch(wedge)
        ax.text(1.18 * np.cos(t), 1.18 * np.sin(t), labels[i], ha="center", va="center", fontsize=9)
    # chords
    links = [(0, 2), (0, 4), (1, 3), (1, 5), (2, 5), (3, 4), (0, 3)]
    for a, b in links:
        t1, t2 = theta[a], theta[b]
        p1 = (0.86 * np.cos(t1), 0.86 * np.sin(t1))
        p2 = (0.86 * np.cos(t2), 0.86 * np.sin(t2))
        path = FancyArrowPatch(p1, p2, connectionstyle="arc3,rad=0.35", arrowstyle="-", color=PALETTE[a], lw=2.2, alpha=0.55)
        ax.add_patch(path)
    save(fig, "chord")


def chart_network():
    fig, ax = new_fig(6.6, 5.0)
    ax.set_aspect("equal")
    ax.axis("off")
    # simple force-like layout
    nodes = {
        0: (0.0, 0.1),
        1: (-1.4, 0.9),
        2: (1.5, 0.8),
        3: (-1.6, -0.9),
        4: (1.3, -1.0),
        5: (0.1, 1.5),
        6: (-0.2, -1.6),
        7: (2.2, 0.0),
        8: (-2.2, 0.1),
    }
    edges = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (1, 5), (1, 8), (2, 7), (2, 5), (3, 6), (3, 8), (4, 7), (4, 6)]
    for a, b in edges:
        x1, y1 = nodes[a]
        x2, y2 = nodes[b]
        ax.plot([x1, x2], [y1, y2], color="#B7A994", lw=1.3, zorder=1)
    for i, (x, y) in nodes.items():
        s = 420 if i == 0 else 220
        col = TERRACOTTA if i == 0 else TEAL
        ax.scatter([x], [y], s=s, color=col, zorder=3, edgecolors=CREAM, linewidths=1.4)
        ax.text(x, y, str(i), ha="center", va="center", color="white", fontsize=8, fontweight="bold")
    save(fig, "network")


def chart_arc():
    fig, ax = new_fig(7.8, 3.6)
    n = 8
    xs = np.linspace(0.5, 7.3, n)
    y = 0.35
    pairs = [(0, 3), (0, 5), (1, 2), (1, 6), (2, 7), (3, 4), (4, 7), (5, 7)]
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 3.2)
    for a, b in pairs:
        x1, x2 = xs[a], xs[b]
        h = 0.45 + (x2 - x1) * 0.35
        arc = Arc(((x1 + x2) / 2, y), x2 - x1, h * 2, theta1=0, theta2=180, color=TEAL, lw=1.6, alpha=0.85)
        ax.add_patch(arc)
    ax.scatter(xs, [y] * n, s=90, color=TERRACOTTA, zorder=4, edgecolors=NAVY, linewidths=0.4)
    for i, x in enumerate(xs):
        ax.text(x, y - 0.28, f"N{i+1}", ha="center", fontsize=8)
    ax.axis("off")
    save(fig, "arc")


def chart_alluvial():
    fig, ax = new_fig(7.6, 4.6)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    left = [("A", 3.5, TEAL), ("B", 2.5, GOLD), ("C", 2.0, TERRACOTTA)]
    right = [("X", 4.0, PALETTE[3]), ("Y", 2.4, PALETTE[4]), ("Z", 1.6, PALETTE[5])]
    # positions
    def stack(items, x, h0=1.2):
        pos = []
        y = h0
        for name, h, col in items:
            pos.append((name, x, y, h, col))
            ax.add_patch(Rectangle((x - 0.28, y), 0.56, h, facecolor=col, edgecolor=CREAM, lw=1))
            ax.text(x + (0.55 if x < 5 else -0.55), y + h / 2, name, ha="left" if x < 5 else "right", va="center", fontsize=9, color=NAVY, fontweight="bold")
            y += h + 0.35
        return pos

    L = stack(left, 1.6)
    R = stack(right, 8.4)
    flows = [
        (0, 0, 2.0),
        (0, 1, 1.0),
        (0, 2, 0.5),
        (1, 0, 1.2),
        (1, 1, 0.9),
        (1, 2, 0.4),
        (2, 0, 0.8),
        (2, 1, 0.5),
        (2, 2, 0.7),
    ]
    lcur = [p[2] for p in L]
    rcur = [p[2] for p in R]
    for li, ri, h in flows:
        y1, y2 = lcur[li], rcur[ri]
        xs = np.linspace(1.88, 8.12, 40)
        t = (xs - 1.88) / (8.12 - 1.88)
        top = y1 + h + (y2 + h - (y1 + h)) * (3 * t**2 - 2 * t**3)
        bot = y1 + (y2 - y1) * (3 * t**2 - 2 * t**3)
        ax.fill_between(xs, bot, top, color=L[li][4], alpha=0.35, linewidth=0)
        lcur[li] += h
        rcur[ri] += h
    save(fig, "alluvial")


# ---------------------------------------------------------------------------
# HIERARCHY / SPECIAL
# ---------------------------------------------------------------------------
def chart_dendrogram():
    fig, ax = new_fig(7.6, 4.4)
    # handmade dendrogram
    leaves = np.linspace(0.6, 7.4, 8)
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 5)
    for x in leaves:
        ax.plot([x, x], [0.3, 1.2], color=TEAL, lw=1.5)
    pairs = [(0, 1, 1.8), (2, 3, 1.6), (4, 5, 2.0), (6, 7, 1.7)]
    mids = []
    for a, b, h in pairs:
        x1, x2 = leaves[a], leaves[b]
        ax.plot([x1, x1, x2, x2], [1.2, h, h, 1.2], color=TEAL, lw=1.5)
        mids.append(((x1 + x2) / 2, h))
    # higher
    ax.plot([mids[0][0], mids[0][0], mids[1][0], mids[1][0]], [mids[0][1], 3.0, 3.0, mids[1][1]], color=TEAL, lw=1.5)
    ax.plot([mids[2][0], mids[2][0], mids[3][0], mids[3][0]], [mids[2][1], 2.7, 2.7, mids[3][1]], color=TEAL, lw=1.5)
    ax.plot([(mids[0][0] + mids[1][0]) / 2] * 2 + [(mids[2][0] + mids[3][0]) / 2] * 2, [3.0, 4.2, 4.2, 2.7], color=TEAL, lw=1.5)
    for i, x in enumerate(leaves):
        ax.text(x, 0.1, f"L{i+1}", ha="center", fontsize=8)
    ax.axis("off")
    save(fig, "dendrogram")


def chart_icicle():
    fig, ax = new_fig(7.6, 4.2)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 2), 10, 1, facecolor=NAVY, edgecolor=CREAM, lw=1.5))
    ax.text(5, 2.5, "Root", ha="center", va="center", color="white", fontsize=10)
    xs, ws = [0, 4.5, 7.2], [4.5, 2.7, 2.8]
    labs = ["Branch A", "Branch B", "Branch C"]
    for x, w, lab, c in zip(xs, ws, labs, [TEAL, TERRACOTTA, GOLD]):
        ax.add_patch(Rectangle((x, 1), w, 1, facecolor=c, edgecolor=CREAM, lw=1.5))
        ax.text(x + w / 2, 1.5, lab, ha="center", va="center", color="white", fontsize=8)
    leaves = [(0, 1.6, "a1"), (1.6, 1.5, "a2"), (3.1, 1.4, "a3"), (4.5, 1.4, "b1"), (5.9, 1.3, "b2"), (7.2, 1.5, "c1"), (8.7, 1.3, "c2")]
    for x, w, lab in leaves:
        ax.add_patch(Rectangle((x, 0), w, 1, facecolor=SAGE if "a" in lab else (CORAL if "b" in lab else PALETTE[5]), edgecolor=CREAM, lw=1.2, alpha=0.9))
        ax.text(x + w / 2, 0.5, lab, ha="center", va="center", color="white", fontsize=8)
    save(fig, "icicle")


def chart_radar():
    fig = plt.figure(figsize=(6.2, 5.2), facecolor=CREAM)
    ax = fig.add_subplot(111, polar=True)
    labels = ["Speed", "Quality", "Cost", "Design", "Support", "Reach"]
    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]
    for vals, col, lab in [([0.8, 0.65, 0.4, 0.7, 0.6, 0.75], TEAL, "A"), ([0.55, 0.8, 0.7, 0.5, 0.75, 0.45], TERRACOTTA, "B")]:
        v = vals + vals[:1]
        ax.plot(angles, v, color=col, lw=2, label=lab)
        ax.fill(angles, v, color=col, alpha=0.18)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_yticks([0.25, 0.5, 0.75])
    ax.set_ylim(0, 1)
    ax.set_facecolor(PAPER)
    ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1))
    save(fig, "radar")


def chart_nightingale():
    fig = plt.figure(figsize=(6.2, 5.2), facecolor=CREAM)
    ax = fig.add_subplot(111, polar=True)
    n = 12
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    r = np.array([4, 6, 9, 12, 14, 11, 8, 6, 5, 4, 3, 3.5])
    width = 2 * np.pi / n * 0.92
    ax.bar(theta, r, width=width, color=[CMAP2(v / 14) for v in r], edgecolor=CREAM, linewidth=1)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(theta)
    ax.set_xticklabels(list("JFMAMJJASOND"))
    ax.set_yticks([])
    ax.set_facecolor(PAPER)
    save(fig, "nightingale")


def chart_gantt():
    fig, ax = new_fig(7.8, 4.4)
    tasks = [("Discover", 0, 3), ("Design", 2.5, 4), ("Build", 5, 6), ("Test", 9, 3), ("Launch", 11.5, 2)]
    for i, (name, start, dur) in enumerate(tasks):
        ax.barh(i, dur, left=start, height=0.45, color=PALETTE[i], zorder=3)
        ax.text(start + dur + 0.15, i, name, va="center", fontsize=8, color=NAVY)
    ax.set_yticks([])
    ax.set_xlabel("Week")
    ax.set_xlim(0, 16)
    polish(ax, ygrid=False, xgrid=True)
    ax.spines["left"].set_visible(False)
    save(fig, "gantt")


def chart_timeline():
    fig, ax = new_fig(7.8, 3.4)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    ax.plot([0.5, 9.5], [1.4, 1.4], color=NAVY, lw=1.6)
    events = [(1.2, "Founded", 1), (3.0, "Series A", 0), (5.1, "Launch", 1), (7.0, "EU expand", 0), (8.8, "IPO", 1)]
    for x, lab, up in events:
        ax.scatter([x], [1.4], s=55, color=TERRACOTTA, zorder=3)
        y = 2.15 if up else 0.55
        ax.plot([x, x], [1.4, y + (0.15 if up else -0.15)], color=MUTED, lw=0.8)
        ax.text(x, y, lab, ha="center", fontsize=8, color=NAVY)
    save(fig, "timeline")


def chart_venn():
    fig, ax = new_fig(6.4, 4.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-2.2, 2.2)
    ax.set_ylim(-1.8, 1.9)
    ax.add_patch(Circle((-0.55, 0), 1.15, facecolor=TEAL, alpha=0.35, edgecolor=TEAL, lw=2))
    ax.add_patch(Circle((0.55, 0), 1.15, facecolor=TERRACOTTA, alpha=0.35, edgecolor=TERRACOTTA, lw=2))
    ax.text(-1.15, 0, "A", ha="center", fontsize=12, color=NAVY, fontweight="bold")
    ax.text(1.15, 0, "B", ha="center", fontsize=12, color=NAVY, fontweight="bold")
    ax.text(0, 0, "A∩B", ha="center", fontsize=10, color=NAVY)
    save(fig, "venn")


def chart_pareto():
    fig, ax = new_fig()
    cats = ["A", "B", "C", "D", "E", "F", "G"]
    vals = np.array([42, 26, 14, 8, 5, 3, 2], dtype=float)
    cum = np.cumsum(vals) / vals.sum() * 100
    ax.bar(cats, vals, color=TEAL, zorder=3)
    ax2 = ax.twinx()
    ax2.plot(cats, cum, color=TERRACOTTA, marker="o", lw=2)
    ax2.set_ylim(0, 105)
    ax2.set_ylabel("Cumulative %")
    ax2.spines["top"].set_visible(False)
    ax.set_ylabel("Frequency")
    polish(ax)
    save(fig, "pareto")


def chart_gauge():
    fig, ax = new_fig(6.4, 3.8)
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-0.15, 1.25)
    ax.set_aspect("equal")
    ax.axis("off")
    wedges = [(180, 120, TERRACOTTA), (120, 60, GOLD), (60, 0, TEAL)]
    for a, b, c in wedges:
        ax.add_patch(Wedge((0, 0), 1, b, a, width=0.28, facecolor=c, edgecolor=CREAM, lw=2))
    # needle at 72% -> angle 180*(1-0.72)=50.4 from right = 50.4 deg
    ang = np.radians(180 - 72 * 1.8)
    ax.plot([0, 0.72 * np.cos(ang)], [0, 0.72 * np.sin(ang)], color=NAVY, lw=3)
    ax.scatter([0], [0], s=40, color=NAVY, zorder=5)
    ax.text(0, -0.05, "72 / 100", ha="center", va="top", fontsize=12, color=NAVY, fontweight="bold")
    save(fig, "gauge")


def chart_errorbar():
    fig, ax = new_fig()
    x = np.arange(5)
    y = np.array([12, 18, 15, 22, 17])
    err = np.array([1.5, 2.1, 1.2, 2.4, 1.8])
    ax.errorbar(x, y, yerr=err, fmt="o", color=TEAL, ecolor=NAVY, elinewidth=1.2, capsize=4, ms=8)
    ax.set_xticks(x)
    ax.set_xticklabels(["A", "B", "C", "D", "E"])
    ax.set_ylabel("Mean ± 95% CI")
    polish(ax)
    save(fig, "errorbar")


def chart_heatmap():
    fig, ax = new_fig(6.6, 4.6)
    data = rng.integers(10, 95, (7, 8))
    im = ax.imshow(data, cmap=CMAP2)
    ax.set_xticks(range(8))
    ax.set_yticks(range(7))
    ax.set_xticklabels([f"W{i+1}" for i in range(8)])
    ax.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    polish(ax, ygrid=False)
    save(fig, "heatmap")


def chart_wordcloud_like():
    fig, ax = new_fig(7.4, 4.4)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    words = [
        ("data", 0.5, 3.2, 28, TEAL),
        ("trend", 3.3, 4.4, 16, TERRACOTTA),
        ("map", 6.8, 3.6, 20, GOLD),
        ("flow", 2.0, 1.5, 14, SAGE),
        ("rank", 5.2, 2.2, 18, CORAL),
        ("share", 7.6, 1.6, 13, PALETTE[5]),
        ("time", 4.4, 5.1, 12, TEAL),
        ("risk", 8.2, 4.8, 11, TERRACOTTA),
        ("cluster", 0.8, 5.0, 10, NAVY),
        ("outlier", 5.8, 0.7, 10, SLATE),
        ("density", 3.6, 3.3, 12, TEAL),
        ("story", 7.0, 2.7, 15, NAVY),
    ]
    for w, x, y, s, c in words:
        ax.text(x, y, w, fontsize=s, color=c, ha="left", va="center", fontweight="bold", alpha=0.9)
    save(fig, "wordcloud")


def chart_ohlc():
    fig, ax = new_fig()
    n = 16
    close = 50 + np.cumsum(rng.normal(0.1, 1.1, n))
    open_ = close + rng.normal(0, 0.8, n)
    high = np.maximum(open_, close) + rng.uniform(0.2, 1.4, n)
    low = np.minimum(open_, close) - rng.uniform(0.2, 1.4, n)
    for i in range(n):
        col = TEAL if close[i] >= open_[i] else TERRACOTTA
        ax.vlines(i, low[i], high[i], color=col, lw=1.3)
        ax.hlines(open_[i], i - 0.25, i, color=col, lw=1.6)
        ax.hlines(close[i], i, i + 0.25, color=col, lw=1.6)
    ax.set_ylabel("Price")
    ax.set_xlabel("Session")
    polish(ax)
    save(fig, "ohlc")


def chart_horizon():
    fig, axes = plt.subplots(4, 1, figsize=(7.6, 4.2), sharex=True)
    x = np.linspace(0, 12, 200)
    for i, ax in enumerate(axes):
        y = np.sin(x * (0.7 + i * 0.2) + i) * (1.2 + 0.2 * i)
        pos = np.clip(y, 0, None)
        neg = np.clip(-y, 0, None)
        ax.fill_between(x, 0, np.clip(pos, 0, 0.7), color=TEAL, alpha=0.85)
        ax.fill_between(x, 0, np.clip(pos - 0.7, 0, 0.7), color=TEAL, alpha=0.5)
        ax.fill_between(x, 0, np.clip(neg, 0, 0.7), color=TERRACOTTA, alpha=0.85)
        ax.set_yticks([])
        ax.set_ylabel(f"S{i+1}", rotation=0, ha="right", va="center")
        ax.spines["left"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_ylim(0, 0.75)
    axes[-1].set_xlabel("Time")
    fig.tight_layout()
    save(fig, "horizon")


def chart_span():
    fig, ax = new_fig()
    cats = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    lo = np.array([2, 3, 4, 3, 5, 6])
    hi = np.array([8, 9, 11, 10, 12, 13])
    y = np.arange(len(cats))
    ax.hlines(y, lo, hi, color=TEAL, lw=6, alpha=0.85)
    ax.scatter(lo, y, s=20, color=NAVY, zorder=3)
    ax.scatter(hi, y, s=20, color=NAVY, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(cats)
    ax.set_xlabel("Range")
    polish(ax, ygrid=False, xgrid=True)
    save(fig, "span")


def chart_population_pyramid():
    # already have butterfly; make a more classic pyramid with more bins
    fig, ax = new_fig()
    ages = [f"{i}-{i+4}" for i in range(0, 80, 5)] + ["80+"]
    n = len(ages)
    male = np.linspace(8, 2.2, n) + rng.normal(0, 0.2, n)
    female = np.linspace(7.6, 2.8, n) + rng.normal(0, 0.2, n)
    y = np.arange(n)
    ax.barh(y, -male, color=TEAL, height=0.85, label="Male")
    ax.barh(y, female, color=CORAL, height=0.85, label="Female")
    ax.set_yticks(y[::2])
    ax.set_yticklabels(ages[::2], fontsize=7)
    ax.axvline(0, color=NAVY, lw=0.7)
    ax.set_xlabel("Population (%)")
    ax.legend(loc="upper right")
    polish(ax, ygrid=False, xgrid=True)
    save(fig, "population_pyramid")


ALL = [
    chart_column, chart_bar, chart_grouped_bar, chart_lollipop, chart_dot_plot,
    chart_pictogram, chart_proportional_area, chart_bullet, chart_radial_bar,
    chart_ordered_bar, chart_slope, chart_bump, chart_dumbbell,
    chart_diverging_bar, chart_butterfly, chart_surplus_deficit,
    chart_histogram, chart_density, chart_boxplot, chart_violin, chart_beeswarm,
    chart_ridgeline, chart_strip, chart_qq, chart_ecdf, chart_population_pyramid,
    chart_scatter, chart_bubble, chart_hexbin, chart_density2d, chart_connected_scatter,
    chart_corr_heatmap, chart_parallel,
    chart_line, chart_multiline, chart_area, chart_stacked_area, chart_streamgraph,
    chart_step, chart_candlestick, chart_calendar_heatmap, chart_sparkline_panel,
    chart_control, chart_fan, chart_horizon, chart_span,
    chart_pie, chart_donut, chart_waffle, chart_stacked_bar, chart_stacked100,
    chart_treemap, chart_sunburst, chart_marimekko, chart_circle_pack,
    chart_waterfall, chart_funnel, chart_pyramid,
    chart_choropleth, chart_bubble_map, chart_dot_density, chart_connection_map,
    chart_sankey, chart_chord, chart_network, chart_arc, chart_alluvial,
    chart_dendrogram, chart_icicle, chart_radar, chart_nightingale,
    chart_gantt, chart_timeline, chart_venn, chart_pareto, chart_gauge,
    chart_errorbar, chart_heatmap, chart_wordcloud_like, chart_ohlc,
]


if __name__ == "__main__":
    failed = []
    for fn in ALL:
        try:
            fn()
            print("ok", fn.__name__)
        except Exception as e:
            failed.append((fn.__name__, repr(e)))
            print("FAIL", fn.__name__, e)
            plt.close("all")
    print("done", "failed", len(failed))
    for f in failed:
        print(" ", f)
