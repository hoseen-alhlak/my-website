#!/usr/bin/env python3
"""Cover and section-divider art for the atlas."""
from pathlib import Path
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
import arabic_reshaper
from bidi.algorithm import get_display

ROOT = Path("/home/user/atlas")
FONTS = ROOT / "fonts"
CHARTS = ROOT / "charts"

for fp in FONTS.glob("*.ttf"):
    font_manager.fontManager.addfont(str(fp))

NAVY = "#0E2433"
GOLD = "#C6A15B"
CREAM = "#F7F2E8"
TEAL = "#2C6E7A"
TERRACOTTA = "#C45C4A"
INK = "#F7F2E8"

NASKH = font_manager.FontProperties(fname=str(FONTS / "NotoNaskhArabic-Regular.ttf"))
NASKH_B = font_manager.FontProperties(fname=str(FONTS / "NotoNaskhArabic-Bold.ttf"))
SANS = font_manager.FontProperties(fname=str(FONTS / "NotoSansArabic-Regular.ttf"))
SANS_B = font_manager.FontProperties(fname=str(FONTS / "NotoSansArabic-Bold.ttf"))


def ar(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text))


def cover():
    fig = plt.figure(figsize=(8.27, 11.69), facecolor=NAVY)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 8.27)
    ax.set_ylim(0, 11.69)
    ax.axis("off")
    ax.set_facecolor(NAVY)

    # gold frame
    ax.add_patch(Rectangle((0.38, 0.38), 7.51, 10.93, fill=False, edgecolor=GOLD, lw=1.1))
    ax.add_patch(Rectangle((0.48, 0.48), 7.31, 10.73, fill=False, edgecolor=GOLD, lw=0.4, alpha=0.5))

    ax.text(4.135, 10.55, "A T L A S   ·   2 0 2 6", ha="center", color=GOLD, fontsize=9)
    ax.plot([2.4, 5.87], [10.28, 10.28], color=GOLD, lw=0.6)

    ax.text(4.135, 9.35, ar("أطلس المفردات البصرية"), ha="center", color=CREAM, fontsize=28, fontproperties=NASKH_B)
    ax.text(4.135, 8.72, ar("دليل شامل لاختيار الرسم البياني"), ha="center", color=GOLD, fontsize=13, fontproperties=NASKH)
    ax.text(4.135, 8.28, "A Visual Vocabulary of Data Visualization", ha="center", color="#D9D1C2", fontsize=10)

    ax.plot([1.8, 6.47], [7.95, 7.95], color=GOLD, lw=0.5, alpha=0.7)

    # stats row
    stats = [("80", ar("رسماً بيانياً")), ("10", ar("عائلات بصرية")), ("8", ar("مبادئ تصميم"))]
    xs = [2.05, 4.135, 6.22]
    for x, (n, lab) in zip(xs, stats):
        ax.text(x, 7.42, n, ha="center", color=GOLD, fontsize=22, fontweight="bold")
        ax.text(x, 7.08, lab, ha="center", color=CREAM, fontsize=9, fontproperties=NASKH)

    # mosaic of charts
    thumbs = [
        "column.png", "line.png", "scatter.png", "heatmap.png",
        "treemap.png", "sankey.png", "violin.png", "choropleth.png",
    ]
    coords = [
        (0.85, 3.55), (2.7, 3.55), (4.55, 3.55), (6.4, 3.55),
        (0.85, 1.85), (2.7, 1.85), (4.55, 1.85), (6.4, 1.85),
    ]
    for (x, y), name in zip(coords, thumbs):
        img = plt.imread(CHARTS / name)
        ax.imshow(img, extent=(x, x + 1.55, y, y + 1.45), aspect="auto", zorder=3)
        ax.add_patch(Rectangle((x, y), 1.55, 1.45, fill=False, edgecolor=GOLD, lw=0.5, zorder=4))

    ax.text(4.135, 1.35, ar("كل رسم مع وصف استخدامه · متى تختاره ومتى تتجنّبه"), ha="center", color=CREAM, fontsize=10, fontproperties=NASKH)
    ax.text(4.135, 0.85, ar("مبني على Visual Vocabulary و From Data to Viz و Data Viz Catalogue"), ha="center", color="#B7A994", fontsize=8, fontproperties=NASKH)

    out = ROOT / "cover.png"
    fig.savefig(out, dpi=160, facecolor=NAVY)
    plt.close(fig)
    print("cover", out)


def divider(title_ar: str, title_en: str, subtitle: str, fname: str, accent=GOLD):
    fig = plt.figure(figsize=(8.27, 11.69), facecolor=NAVY)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 8.27)
    ax.set_ylim(0, 11.69)
    ax.axis("off")
    ax.set_facecolor(NAVY)
    ax.add_patch(Rectangle((0.38, 0.38), 7.51, 10.93, fill=False, edgecolor=accent, lw=1.0))
    ax.plot([1.5, 6.77], [6.55, 6.55], color=accent, lw=0.7)
    ax.text(4.135, 7.15, ar(title_ar), ha="center", color=CREAM, fontsize=26, fontproperties=NASKH_B)
    ax.text(4.135, 6.15, title_en.upper(), ha="center", color=accent, fontsize=11)
    ax.text(4.135, 5.45, ar(subtitle), ha="center", color="#D9D1C2", fontsize=11, fontproperties=NASKH, wrap=True)
    out = ROOT / "dividers" / fname
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=140, facecolor=NAVY)
    plt.close(fig)
    print("divider", out)


if __name__ == "__main__":
    cover()
    cats = [
        ("الحجم والمقارنة", "Magnitude", "أظهر الحجم المطلق أو النسبي بين الفئات.", "d_magnitude.png"),
        ("الترتيب", "Ranking", "حين يكون الموقع في القائمة أهم من القيمة نفسها.", "d_ranking.png"),
        ("الانحراف عن مرجع", "Deviation", "أكّد الفرق عن صفر أو هدف أو متوسط.", "d_deviation.png"),
        ("التوزيع", "Distribution", "كيف تنتشر القيم؟ أين الكثافة وأين الشذوذ؟", "d_distribution.png"),
        ("العلاقات والارتباط", "Correlation", "هل يتحرك متغيّران معاً؟ وكيف؟", "d_correlation.png"),
        ("التغيّر عبر الزمن", "Change over time", "الاتجاه، الموسمية، والانكسار.", "d_time.png"),
        ("الجزء من الكل", "Part-to-whole", "كيف يتكون المجموع من أجزائه؟", "d_part.png"),
        ("الجغرافيا والمكان", "Spatial", "حين يكون الموقع الجغرافي هو القصة.", "d_spatial.png"),
        ("التدفق والشبكات", "Flow & networks", "حركة الكميات والعلاقات بين الكيانات.", "d_flow.png"),
        ("الهرمية والمتخصص", "Hierarchy & specialised", "البُنى، العمليات، والنص.", "d_special.png"),
    ]
    for a, e, s, f in cats:
        divider(a, e, s, f)
