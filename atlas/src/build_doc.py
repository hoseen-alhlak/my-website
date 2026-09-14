#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the Arabic Visual Vocabulary Word atlas."""
from __future__ import annotations

import copy
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn, nsmap
from docx.shared import Cm, Mm, Pt, RGBColor, Emu, Inches

from catalog import CATS, CHARTS, SOURCES, PRINCIPLES, PRINCIPLE_PAGES

ROOT = Path("/home/user/atlas")
CHART_DIR = ROOT / "charts"
DIV_DIR = ROOT / "dividers"
COVER = ROOT / "cover.png"
OUT = Path("/home/user/أطلس_المفردات_البصرية.docx")

NAVY = RGBColor(0x0E, 0x24, 0x33)
GOLD = RGBColor(0xC6, 0xA1, 0x5B)
TEAL = RGBColor(0x2C, 0x6E, 0x7A)
TERRACOTTA = RGBColor(0xC4, 0x5C, 0x4A)
CREAM = RGBColor(0xF7, 0xF2, 0xE8)
INK = RGBColor(0x1C, 0x28, 0x33)
SLATE = RGBColor(0x5B, 0x65, 0x70)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SAND = RGBColor(0xE6, 0xD9, 0xC4)
PAPER = RGBColor(0xFB, 0xF7, 0xF0)

FONT_AR = "Noto Naskh Arabic"
FONT_SANS = "Noto Sans Arabic"
FONT_EN = "Calibri"


def _rfonts(run, name, cs=None):
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    cs = cs or name
    rFonts.set(qn("w:ascii"), FONT_EN)
    rFonts.set(qn("w:hAnsi"), FONT_EN)
    rFonts.set(qn("w:cs"), cs)
    rFonts.set(qn("w:eastAsia"), name)
    # rtl mark for arabic
    rtl = rPr.find(qn("w:rtl"))
    if rtl is None:
        rtl = OxmlElement("w:rtl")
        rPr.append(rtl)
    csb = rPr.find(qn("w:cs"))
    if csb is None:
        csb = OxmlElement("w:cs")
        rPr.append(csb)


def set_run(run, text, size=12, bold=False, color=INK, font=FONT_AR, italic=False):
    run.text = text
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.name = font
    _rfonts(run, font, cs=font)


def set_rtl_p(p, align="right"):
    pPr = p._p.get_or_add_pPr()
    bidi = pPr.find(qn("w:bidi"))
    if bidi is None:
        bidi = OxmlElement("w:bidi")
        pPr.append(bidi)
    bidi.set(qn("w:val"), "1")
    jc = pPr.find(qn("w:jc"))
    if jc is None:
        jc = OxmlElement("w:jc")
        pPr.append(jc)
    mapping = {"right": "right", "left": "left", "center": "center", "both": "both"}
    jc.set(qn("w:val"), mapping.get(align, "right"))


def add_p(doc_or_cell, text, size=12, bold=False, color=INK, space_after=6, space_before=0, align="right", font=FONT_AR, italic=False):
    if hasattr(doc_or_cell, "paragraphs") and hasattr(doc_or_cell, "add_paragraph") is False:
        # cell
        p = doc_or_cell.paragraphs[0] if (doc_or_cell.paragraphs and not doc_or_cell.paragraphs[0].text) else doc_or_cell.add_paragraph()
        if doc_or_cell.paragraphs[0] is p and p.text:
            p = doc_or_cell.add_paragraph()
    else:
        p = doc_or_cell.add_paragraph()
    p.clear() if False else None
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.line_spacing = 1.18
    run = p.add_run()
    set_run(run, text, size=size, bold=bold, color=color, font=font, italic=italic)
    set_rtl_p(p, align=align)
    return p


def shade_cell(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = tcPr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tcPr.append(shd)
    shd.set(qn("w:fill"), hex_color)
    shd.set(qn("w:val"), "clear")


def set_cell_borders(cell, color="C6A15B", sz="4"):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), sz)
        el.set(qn("w:color"), color)
        el.set(qn("w:space"), "0")
        tcBorders.append(el)
    tcPr.append(tcBorders)


def set_table_rtl(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        tbl.insert(0, tblPr)
    bidi = OxmlElement("w:bidiVisual")
    bidi.set(qn("w:val"), "1")
    tblPr.append(bidi)


def no_table_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "nil")
        borders.append(el)
    tblPr.append(borders)


def set_cell_margins(cell, **kw):
    """kw in twips-like via dxa: top/left/bottom/right in points converted."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for k, v_pt in kw.items():
        node = OxmlElement(f"w:{k}")
        node.set(qn("w:w"), str(int(v_pt * 20)))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def clear_cell(cell):
    for p in cell.paragraphs:
        p.clear()
        p.text = ""


def cell_text(cell, text, size=11, bold=False, color=INK, align="right", font=FONT_AR, after=4):
    # use first paragraph
    p = cell.paragraphs[0]
    p.text = ""
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    run = p.add_run()
    set_run(run, text, size=size, bold=bold, color=color, font=font)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing = 1.15
    set_rtl_p(p, align=align)
    return p


def add_cell_p(cell, text, size=11, bold=False, color=INK, align="right", font=FONT_AR, after=3):
    p = cell.add_paragraph()
    run = p.add_run()
    set_run(run, text, size=size, bold=bold, color=color, font=font)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing = 1.15
    set_rtl_p(p, align=align)
    return p


def page_break(doc):
    p = doc.add_paragraph()
    run = p.add_run()
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    run._element.append(br)
    set_rtl_p(p)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)


def set_doc_rtl(doc):
    for section in doc.sections:
        sectPr = section._sectPr
        bidi = OxmlElement("w:bidi")
        bidi.set(qn("w:val"), "1")
        sectPr.append(bidi)
        # A4
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.top_margin = Cm(1.4)
        section.bottom_margin = Cm(1.5)
        section.left_margin = Cm(1.6)
        section.right_margin = Cm(1.6)
        section.header_distance = Cm(0.6)
        section.footer_distance = Cm(0.6)


def set_doc_defaults(doc):
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = FONT_AR
    normal.font.size = Pt(12)
    normal.font.color.rgb = INK
    rPr = normal.element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), FONT_EN)
    rFonts.set(qn("w:hAnsi"), FONT_EN)
    rFonts.set(qn("w:cs"), FONT_AR)
    rFonts.set(qn("w:eastAsia"), FONT_AR)
    # default paragraph rtl
    pPr = normal.element.find(qn("w:pPr"))
    if pPr is None:
        pPr = OxmlElement("w:pPr")
        normal.element.append(pPr)
    bidi = OxmlElement("w:bidi")
    bidi.set(qn("w:val"), "1")
    pPr.append(bidi)


def add_header_footer(doc):
    section = doc.sections[0]
    section.different_first_page_header_footer = True
    # empty first-page header/footer so the cover is clean
    fp_h = section.first_page_header
    fp_h.is_linked_to_previous = False
    fp_h.paragraphs[0].text = ""
    fp_f = section.first_page_footer
    fp_f.is_linked_to_previous = False
    fp_f.paragraphs[0].text = ""
    header = section.header
    header.is_linked_to_previous = False
    hp = header.paragraphs[0]
    hp.text = ""
    run = hp.add_run()
    set_run(run, "أطلس المفردات البصرية  ·  Visual Vocabulary Atlas  ·  2026", size=8, color=GOLD, font=FONT_SANS)
    set_rtl_p(hp, align="center")
    hp.paragraph_format.space_after = Pt(2)

    footer = section.footer
    footer.is_linked_to_previous = False
    fp = footer.paragraphs[0]
    fp.text = ""
    set_rtl_p(fp, align="center")
    r1 = fp.add_run()
    set_run(r1, "صفحة  ", size=8, color=SLATE, font=FONT_AR)
    # page number field
    fld1 = OxmlElement("w:fldChar")
    fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld2 = OxmlElement("w:fldChar")
    fld2.set(qn("w:fldCharType"), "end")
    r2 = fp.add_run()
    r2._element.append(fld1)
    r2._element.append(instr)
    r2._element.append(fld2)
    r2.font.size = Pt(8)
    r2.font.color.rgb = SLATE
    r3 = fp.add_run()
    set_run(r3, "  |  مصادر: FT Visual Vocabulary · From Data to Viz · Data Viz Catalogue", size=8, color=SLATE, font=FONT_EN)


def gold_rule(doc):
    table = doc.add_table(rows=1, cols=1)
    table.autofit = True
    cell = table.cell(0, 0)
    shade_cell(cell, "C6A15B")
    cell_text(cell, "", size=2, after=0)
    set_cell_margins(cell, top=0, bottom=0, left=0, right=0)
    # height
    tr = table.rows[0]._tr
    trPr = tr.get_or_add_trPr()
    trHeight = OxmlElement("w:trHeight")
    trHeight.set(qn("w:val"), "80")
    trHeight.set(qn("w:hRule"), "exact")
    trPr.append(trHeight)
    no_table_borders(table)


def navy_banner(doc, title, subtitle=""):
    table = doc.add_table(rows=1, cols=1)
    cell = table.cell(0, 0)
    shade_cell(cell, "0E2433")
    set_cell_margins(cell, top=8, bottom=8, left=10, right=10)
    cell_text(cell, title, size=16, bold=True, color=CREAM, align="center", font=FONT_SANS, after=2)
    if subtitle:
        add_cell_p(cell, subtitle, size=10, color=GOLD, align="center", font=FONT_EN, after=2)
    no_table_borders(table)


def insert_image(doc, path, width_cm=17.4):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.space_before = Pt(4)
    run = p.add_run()
    run.add_picture(str(path), width=Cm(width_cm))
    set_rtl_p(p, align="center")
    return p


def add_label_block(doc, label, body, label_color=TEAL):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    r1 = p.add_run()
    set_run(r1, label + "  ", size=11, bold=True, color=label_color, font=FONT_SANS)
    r2 = p.add_run()
    set_run(r2, body, size=11, color=INK, font=FONT_AR)
    set_rtl_p(p, align="right")


def chart_card(doc, n, item, cat_ar):
    # top bar
    table = doc.add_table(rows=1, cols=2)
    table.autofit = True
    set_table_rtl(table)
    c0, c1 = table.cell(0, 0), table.cell(0, 1)
    shade_cell(c0, "0E2433")
    shade_cell(c1, "2C6E7A")
    set_cell_margins(c0, top=6, bottom=6, left=8, right=8)
    set_cell_margins(c1, top=6, bottom=6, left=8, right=8)
    cell_text(c0, f"{n:02d}   {item['ar']}", size=14, bold=True, color=CREAM, font=FONT_SANS, after=0)
    cell_text(c1, item["en"], size=10, color=CREAM, align="left", font=FONT_EN, after=0)
    no_table_borders(table)

    img = CHART_DIR / f"{item['id']}.png"
    if img.exists():
        insert_image(doc, img, width_cm=16.6)

    # description grid 2x3
    box = doc.add_table(rows=3, cols=2)
    box.autofit = True
    set_table_rtl(box)
    pairs = [
        ("ماذا يُظهر", item["purpose"], "متى تستخدمه", item["when"]),
        ("متى تتجنّبه", item["avoid"], "البيانات المطلوبة", item["data"]),
        ("خطأ شائع", item["mistake"], "بديل أفضل أحياناً", item["alt"]),
    ]
    fills = [("F7F2E8", "EFE6D6"), ("F4E8E4", "F7F2E8"), ("E7EEF0", "F7F2E8")]
    for r, ((l1, t1, l2, t2), (f1, f2)) in enumerate(zip(pairs, fills)):
        a, b = box.cell(r, 0), box.cell(r, 1)
        shade_cell(a, f1)
        shade_cell(b, f2)
        set_cell_margins(a, top=6, bottom=6, left=8, right=8)
        set_cell_margins(b, top=6, bottom=6, left=8, right=8)
        set_cell_borders(a, "E6D9C4", "8")
        set_cell_borders(b, "E6D9C4", "8")
        cell_text(a, l1, size=9, bold=True, color=TERRACOTTA, font=FONT_SANS, after=2)
        add_cell_p(a, t1, size=10.5, color=INK, after=2)
        cell_text(b, l2, size=9, bold=True, color=TEAL, font=FONT_SANS, after=2)
        add_cell_p(b, t2, size=10.5, color=INK, after=2)


def principles_examples(doc):
    div = DIV_DIR / "d_principles.png"
    if div.exists():
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(str(div), width=Cm(17.8))
        set_rtl_p(p, "center")
    else:
        navy_banner(doc, "المبادئ مطبّقة", "Principles in practice")

    for item in PRINCIPLE_PAGES:
        page_break(doc)
        # title bar
        table = doc.add_table(rows=1, cols=2)
        set_table_rtl(table)
        c0, c1 = table.cell(0, 0), table.cell(0, 1)
        shade_cell(c0, "0E2433")
        shade_cell(c1, "C45C4A")
        set_cell_margins(c0, top=7, bottom=7, left=9, right=9)
        set_cell_margins(c1, top=7, bottom=7, left=9, right=9)
        cell_text(c0, f"مبدأ {item['n']}   {item['title']}", size=14, bold=True, color=CREAM, font=FONT_SANS, after=0)
        cell_text(c1, item["en"], size=10, color=CREAM, align="left", font=FONT_EN, after=0)
        no_table_borders(table)

        add_p(doc, item["setup"], size=12, space_before=8, space_after=6)

        img = CHART_DIR / f"{item['id']}.png"
        if img.exists():
            insert_image(doc, img, width_cm=16.8)

        box = doc.add_table(rows=1, cols=2)
        # LTR table so columns sit under the figure: left = misleading, right = honest
        a, b = box.cell(0, 0), box.cell(0, 1)
        shade_cell(a, "F4E8E4")
        shade_cell(b, "E7EEF0")
        set_cell_margins(a, top=7, bottom=7, left=8, right=8)
        set_cell_margins(b, top=7, bottom=7, left=8, right=8)
        set_cell_borders(a, "C45C4A", "10")
        set_cell_borders(b, "2C6E7A", "10")
        cell_text(a, "لماذا هذا مضلّل", size=10, bold=True, color=TERRACOTTA, font=FONT_SANS, after=3, align="right")
        add_cell_p(a, item["wrong"], size=11, after=2)
        cell_text(b, "لماذا هذا صادق", size=10, bold=True, color=TEAL, font=FONT_SANS, after=3, align="right")
        add_cell_p(b, item["right"], size=11, after=2)

        rule = doc.add_table(rows=1, cols=1)
        cell = rule.cell(0, 0)
        shade_cell(cell, "0E2433")
        set_cell_margins(cell, top=7, bottom=7, left=10, right=10)
        cell_text(cell, "القاعدة:  " + item["rule"], size=11, color=CREAM, font=FONT_AR, after=0)
        no_table_borders(rule)


def intro_pages(doc):
    navy_banner(doc, "كيف يُقرأ هذا الأطلس", "How to use this atlas")
    add_p(doc, "هذا الملف ليس معرض رسوم. هو أداة اختيار: كل صفحة تطرح رسماً، ثم تجيب عن الأسئلة التي تمنع استخدام الرسم الخطأ في اللحظة الحرجة.", size=12, space_after=8, space_before=10)
    add_p(doc, "نُظِّم الأطلس وفق منطق Financial Times Visual Vocabulary: التصنيف حسب الغرض لا حسب الشكل. الشكل خدّاع؛ الغرض هو العقد مع القارئ.", size=12, space_after=8)

    add_p(doc, "كيف تختار في ثلاث خطوات", size=14, bold=True, color=NAVY, font=FONT_SANS, space_before=8, space_after=6)
    steps = [
        "1) اكتب جملة الرسالة: «أريد أن يرى القارئ أن …». إن عجزت عن إكمال الجملة، لا ترسم بعد.",
        "2) حدّد عائلة الغرض: حجم، ترتيب، انحراف، توزيع، علاقة، زمن، جزء من كل، مكان، تدفق، هرمية.",
        "3) داخل العائلة اختر أبسط رسم يُنجز الجملة. إن تردّدت بين رسمين، اختر الأصدق إدراكياً لا الأجمل.",
    ]
    for s in steps:
        add_p(doc, s, size=12, space_after=4)

    add_p(doc, "مبادئ لا تُساوَم", size=14, bold=True, color=NAVY, font=FONT_SANS, space_before=12, space_after=6)
    for title, body in PRINCIPLES:
        add_label_block(doc, title + ".", body, label_color=TEAL)
    add_p(doc, "في الصفحات التالية: كل مبدأ مع نفس البيانات، مرسومة مرّتين. اليسار مضلّل، واليمين صادق.", size=11, color=SLATE, space_before=8, italic=True)

    page_break(doc)
    principles_examples(doc)

    page_break(doc)
    navy_banner(doc, "مصفوفة الاختيار السريع", "Chart chooser")
    add_p(doc, "اقرأ العمود الأيمن: إن طابق نيتك، ابدأ بالرسم المقترح. العمود الأيسر يحميك من الاختيار الشائع الخاطئ.", size=11, space_before=8, space_after=8, color=SLATE)

    rows = [
        ("الهدف", "ابدأ بـ", "تجنّب عادةً"),
        ("مقارنة أحجام فئات", "أعمدة أفقية / عمودية / لولي بوب", "دائرة لأكثر من 5 شرائح"),
        ("ترتيب أو دوري", "أعمدة مرتّبة / Slope / Bump", "رادار لعشرة كيانات"),
        ("فرق عن هدف أو صفر", "أعمدة متباعدة / فائض-عجز", "دائرة أو مساحة نسبية"),
        ("شكل التوزيع والشواذ", "مدرج / صندوق / كمان / سرب", "عمود لبيانات متصلة"),
        ("علاقة بين متغيّرين", "انتشار / فقاعات / Hexbin", "خط يوحي بزمن غير موجود"),
        ("اتجاه عبر الزمن", "خط / مساحة / شموع للأسواق", "دائرة لكل سنة"),
        ("حصّة من كلّ", "مكدّس 100٪ / وافل / شريط", "دائرة ثلاثية الأبعاد"),
        ("تركيب هرمي", "Treemap / Sunburst / Icicle", "دوائر متداخلة بلا مقياس"),
        ("جغرافيا بمعدّل", "Choropleth", "تلوين المجاميع المطلقة"),
        ("جغرافيا بعدد مطلق", "فقاعات على خريطة / كثافة نقاط", "Choropleth للمجاميع"),
        ("حركة كمّيات", "Sankey / Alluvial", "Chord إذا لزم رقم دقيق"),
        ("مؤشر مقابل هدف", "Bullet", "Gauge يسرق الصفحة"),
        ("عدم يقين", "عارضات خطأ / مروحة", "نقطة متوسطة وحدها"),
        ("نص وانطباع", "جدول تكرار / أعمدة كلمات", "سحابة كلمات لقرار"),
    ]
    t = doc.add_table(rows=len(rows), cols=3)
    t.autofit = True
    set_table_rtl(t)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            set_cell_margins(cell, top=5, bottom=5, left=6, right=6)
            set_cell_borders(cell, "C9BFAE", "6")
            if i == 0:
                shade_cell(cell, "0E2433")
                cell_text(cell, val, size=10, bold=True, color=CREAM, font=FONT_SANS, after=0)
            else:
                shade_cell(cell, "F7F2E8" if i % 2 == 0 else "FFFFFF")
                col = TERRACOTTA if j == 2 else INK
                cell_text(cell, val, size=10, bold=(j == 0), color=col, after=0)

    add_p(doc, "ملاحظة: بعض الرسوم تنتمي لأكثر من عائلة (الشلال حجم وتدفق، الخريطة الحرارية علاقة وتوزيع). وُضعت في العائلة التي تُستخدم فيها أكثر.", size=10, color=SLATE, space_before=10, italic=True)

    page_break(doc)
    navy_banner(doc, "فهرس العائلات والرسوم", "Contents")
    add_p(doc, "", size=6, space_after=4)
    n = 1
    for key, ar, en, _div in CATS:
        add_p(doc, f"{ar}  —  {en}", size=13, bold=True, color=NAVY, font=FONT_SANS, space_before=8, space_after=3)
        names = []
        for item in CHARTS[key]:
            names.append(f"{n:02d} {item['ar']}")
            n += 1
        add_p(doc, "  ·  ".join(names), size=10, color=SLATE, space_after=4)


def sources_pages(doc):
    navy_banner(doc, "المصادر والنسب", "Sources — the spine of this atlas")
    add_p(doc, "جُمعت المادة من المراجع التي يعتمدها محرّرو البيانات والأكاديميون، لا من قوائم تسويقية لأدوات ذكاء الأعمال. العربية هنا صياغة وتحرير؛ المنهج بصري عالمي.", size=12, space_before=10, space_after=10)

    add_p(doc, "المراجع الأساسية (بهذا الترتيب تقريباً)", size=13, bold=True, color=NAVY, font=FONT_SANS, space_after=8)
    for i, (title, url, note) in enumerate(SOURCES, 1):
        box = doc.add_table(rows=1, cols=1)
        cell = box.cell(0, 0)
        shade_cell(cell, "F7F2E8" if i % 2 else "FFFFFF")
        set_cell_borders(cell, "C6A15B", "8")
        set_cell_margins(cell, top=7, bottom=7, left=10, right=10)
        cell_text(cell, f"{i}.  {title}", size=11, bold=True, color=NAVY, font=FONT_SANS, after=2)
        add_cell_p(cell, note, size=11, color=INK, after=2)
        add_cell_p(cell, url, size=9, color=TEAL, after=1, font=FONT_EN)
        no_table_borders(box)
        add_p(doc, "", size=4, space_after=4)

    add_p(doc, "مصادر عربية مساندة", size=13, bold=True, color=NAVY, font=FONT_SANS, space_before=8, space_after=6)
    add_p(doc, "الكتالوج العربي المتخصص في «اختيار الرسم» ما زال أضعف من الإنجليزي. المقالات العربية المفيدة تشرح الأنواع الإحصائية الأساسية (أعمدة، خطوط، دوائر، مدرج، صندوق، تبعثر) ضمن مناهج الإحصاء، لكنها نادراً ما تغطي Sankey أو Ridgeline أو Bullet. لذلك بُني هذا الأطلس ليكون مرجعاً عربي اللغة بمعيار المصدر العالمي، لا تلخيصاً لمدوّنات عامة.", size=12, space_after=8)
    add_p(doc, "من المواد العربية المفيدة كمقدّمات صفّية: شروح أنواع العيّنات والرسوم في منصات البحث الأكاديمي العربية، ومقررات تصوّر البيانات التي تستخدم Matplotlib/Seaborn. لا تغني عن FT Visual Vocabulary أو From Data to Viz عند اتخاذ قرار التصميم.", size=12, space_after=10)

    add_p(doc, "حدود هذا الأطلس", size=13, bold=True, color=NAVY, font=FONT_SANS, space_after=6)
    add_p(doc, "الرسوم هنا نماذج تحريرية مولَّدة، ليست بيانات حقيقية. الخرائط تخطيطية لا إسقاطاً جغرافياً. بعض الأنواع النادرة جداً (Chernoff faces، Kagi، Renko، Cartogram الديموغرافي الحقيقي) أُشير إلى وجودها في Data Viz Project دون إثقال الأطلس بها. إذا احتجت نوعاً غير موجود، ابدأ من data-to-viz.com حسب شكل جدولك.", size=12, space_after=8)

    gold_rule(doc)
    add_p(doc, "أطلس المفردات البصرية  ·  تحرير عربي بمعيار Visual Vocabulary  ·  2026", size=10, color=SLATE, align="center", space_before=12)
    add_p(doc, "للاستخدام التعليمي والمهني. انسب الفضل للمراجع الأصلية عند إعادة النشر.", size=9, color=SLATE, align="center")


def build():
    doc = Document()
    set_doc_defaults(doc)
    set_doc_rtl(doc)
    add_header_footer(doc)

    # Cover
    if COVER.exists():
        # tighter margins for cover
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(str(COVER), width=Cm(17.8))
        set_rtl_p(p, "center")

    page_break(doc)
    intro_pages(doc)

    n = 1
    for key, ar, en, divname in CATS:
        page_break(doc)
        div = DIV_DIR / divname
        if div.exists():
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            run.add_picture(str(div), width=Cm(17.8))
            set_rtl_p(p, "center")
        else:
            navy_banner(doc, ar, en)

        for item in CHARTS[key]:
            page_break(doc)
            chart_card(doc, n, item, ar)
            n += 1

    page_break(doc)
    sources_pages(doc)

    doc.save(str(OUT))
    print("saved", OUT, "charts", n - 1, "size_mb", round(OUT.stat().st_size / 1e6, 2))


if __name__ == "__main__":
    build()
