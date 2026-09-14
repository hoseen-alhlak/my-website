#!/usr/bin/env python3
"""Same dataset rendered 12 ways for the playground."""
from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).parent))
from style import PALETTE, NAVY, INK, TEAL, TERRACOTTA, GOLD, CREAM, PAPER, SLATE, polish, SAGE, CORAL

OUT = Path("/home/user/atlas-web/img/play")
OUT.mkdir(parents=True, exist_ok=True)

years = np.array([2020, 2021, 2022, 2023, 2024, 2025])
mobile = np.array([30, 34, 38, 42, 45, 48], dtype=float)
store = np.array([40, 36, 32, 28, 25, 22], dtype=float)
web = np.array([20, 20, 20, 20, 20, 20], dtype=float)
other = np.array([10, 10, 10, 10, 10, 10], dtype=float)
labs = ["Mobile", "Store", "Web", "Other"]
cols = [TEAL, TERRACOTTA, GOLD, SAGE]
y25 = [48, 22, 20, 10]


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=140, facecolor=CREAM, bbox_inches="tight", pad_inches=0.16)
    plt.close(fig)


def figax(w=7.2, h=4.1):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=CREAM)
    ax.set_facecolor(PAPER)
    return fig, ax


def pie():
    fig, ax = figax(6.2, 4.2)
    ax.pie(y25, labels=labs, colors=cols, startangle=90, autopct="%1.0f%%",
           wedgeprops=dict(edgecolor=CREAM, linewidth=1.5), pctdistance=0.7)
    save(fig, "pie")


def donut():
    fig, ax = figax(6.2, 4.2)
    w, *_ = ax.pie(y25, colors=cols, startangle=90, wedgeprops=dict(width=0.42, edgecolor=CREAM, linewidth=2))
    ax.text(0, 0, "2025", ha="center", va="center", fontsize=12, color=NAVY, fontweight="bold")
    ax.legend(w, [f"{l} {v}%" for l, v in zip(labs, y25)], loc="center left", bbox_to_anchor=(0.95, 0.5))
    save(fig, "donut")


def bar():
    fig, ax = figax()
    b = ax.bar(labs, y25, color=cols, width=0.62, zorder=3)
    for x, v in zip(labs, y25):
        ax.text(x, v + 1, str(v), ha="center", fontsize=8, color=INK)
    ax.set_ylabel("Share 2025 (%)")
    ax.set_ylim(0, 58)
    polish(ax)
    save(fig, "bar")


def lollipop():
    fig, ax = figax()
    order = np.argsort(y25)[::-1]
    y = np.arange(4)
    vals = np.array(y25)[order]
    names = np.array(labs)[order]
    ax.hlines(y, 0, vals, color=TEAL, lw=2)
    ax.scatter(vals, y, s=70, color=TERRACOTTA, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.set_xlim(0, 58)
    ax.set_xlabel("Share 2025 (%)")
    polish(ax, ygrid=False, xgrid=True)
    save(fig, "lollipop")


def grouped():
    fig, ax = figax()
    x = np.arange(len(years))
    w = 0.2
    for i, (s, c, n) in enumerate(zip([mobile, store, web, other], cols, labs)):
        ax.bar(x + (i - 1.5) * w, s, w, label=n, color=c, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.set_ylabel("Share (%)")
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.14))
    polish(ax)
    save(fig, "grouped")


def stacked():
    # absolute revenue = share × growing market — so total is NOT 100
    market = np.array([100, 112, 128, 146, 162, 180])
    m, s, w, o = mobile / 100 * market, store / 100 * market, web / 100 * market, other / 100 * market
    fig, ax = figax()
    ax.bar(years, m, color=TEAL, label="Mobile")
    ax.bar(years, s, bottom=m, color=TERRACOTTA, label="Store")
    ax.bar(years, w, bottom=m + s, color=GOLD, label="Web")
    ax.bar(years, o, bottom=m + s + w, color=SAGE, label="Other")
    ax.set_ylabel("Revenue (index)")
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.14))
    polish(ax)
    save(fig, "stacked")


def stacked100():
    stacked()  # already 100
    # rewrite name by copying - already 100%. save as stacked100 by re-running
    fig, ax = figax()
    ax.bar(years, mobile, color=TEAL, label="Mobile")
    ax.bar(years, store, bottom=mobile, color=TERRACOTTA, label="Store")
    ax.bar(years, web, bottom=mobile + store, color=GOLD, label="Web")
    ax.bar(years, other, bottom=mobile + store + web, color=SAGE, label="Other")
    ax.set_ylabel("Share (%)")
    ax.set_ylim(0, 100)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.14))
    polish(ax)
    save(fig, "stacked100")


def lines():
    fig, ax = figax()
    for s, c, n in zip([mobile, store, web, other], cols, labs):
        ax.plot(years, s, color=c, lw=2.2, marker="o", ms=5, label=n)
    ax.set_ylabel("Share (%)")
    ax.set_ylim(0, 55)
    ax.legend()
    polish(ax)
    save(fig, "line")


def slope():
    fig, ax = figax()
    for a, b, n, c in zip([30, 40, 20, 10], [48, 22, 20, 10], labs, cols):
        ax.plot([0, 1], [a, b], color=c, lw=2.3, marker="o", ms=7)
        ax.text(-0.08, a, f"{n}  {a}", ha="right", va="center", fontsize=8)
        ax.text(1.08, b, str(b), ha="left", va="center", fontsize=8, color=c)
    ax.set_xlim(-0.55, 1.4)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["2020", "2025"])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    polish(ax, ygrid=False)
    save(fig, "slope")


def area():
    fig, ax = figax()
    ax.stackplot(years, mobile, store, web, other, colors=cols, labels=labs, alpha=0.92)
    ax.set_ylabel("Share (%)")
    ax.set_ylim(0, 100)
    ax.legend(loc="lower left", ncol=2)
    polish(ax)
    save(fig, "area")


def treemap():
    fig, ax = figax(7.2, 4.2)
    vals = y25[:]
    # slice-and-dice
    rects = []
    x, y, w, h = 0, 0, 10, 6
    total = sum(vals)
    for v in vals:
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
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.set_aspect("equal")
    ax.axis("off")
    for (x, y, w, h), lab, v, c in zip(rects, labs, y25, cols):
        ax.add_patch(Rectangle((x, y), w, h, facecolor=c, edgecolor=CREAM, lw=2))
        ax.text(x + w / 2, y + h / 2, f"{lab}\n{v}%", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
    save(fig, "treemap")


def waffle():
    fig, ax = figax(6.4, 4.0)
    ax.set_aspect("equal")
    cells = []
    for v, c in zip(y25, cols):
        cells += [c] * v
    for i, c in enumerate(cells[:100]):
        r, col = divmod(i, 10)
        ax.add_patch(Rectangle((col, 9 - r), 0.88, 0.88, facecolor=c, edgecolor=CREAM, lw=1.1))
    ax.set_xlim(-0.2, 13.2)
    ax.set_ylim(-0.2, 10.2)
    ax.axis("off")
    for i, (lab, v) in enumerate(zip(labs, y25)):
        ax.add_patch(Rectangle((10.5, 8.2 - i * 1.3), 0.45, 0.45, facecolor=cols[i], edgecolor="none"))
        ax.text(11.15, 8.35 - i * 1.3, f"{lab} {v}%", va="center", fontsize=9)
    save(fig, "waffle")


if __name__ == "__main__":
    for fn in (pie, donut, bar, lollipop, grouped, stacked, stacked100, lines, slope, area, treemap, waffle):
        fn()
        print("ok", fn.__name__)
