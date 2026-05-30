#!/usr/bin/env python3
"""MRCP Anaemia Comprehensive Revision Note — Part 1"""

import io, os, textwrap
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image as RLImage, HRFlowable, KeepTogether)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageDraw, ImageFont

# ── FONTS ────────────────────────────────────────────────────────────────────
_FD = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('DV',   _FD+'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DV-B', _FD+'DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DV-I', _FD+'DejaVuSansMono-Oblique.ttf'))
pdfmetrics.registerFont(TTFont('DV-BI',_FD+'DejaVuSansMono-BoldOblique.ttf'))

# ── COLOURS ───────────────────────────────────────────────────────────────────
TEAL   = HexColor('#0d5c63'); TEAL_M  = HexColor('#1a8a94')
TEAL_L = HexColor('#e0f4f5'); TEAL_XL = HexColor('#f0fafb')
AMBER  = HexColor('#fff3cd'); AMBER_B = HexColor('#e6a817')
GREEN_L= HexColor('#d4edda'); GREEN_D = HexColor('#28a745')
RED_L  = HexColor('#fde8e8'); RED_D   = HexColor('#c0392b')
ORA_L  = HexColor('#fef3e2'); ORA_D   = HexColor('#d4640a')
BLUE_L = HexColor('#e8f4fd'); BLUE_D  = HexColor('#2471a3')
PUR_L  = HexColor('#f5eef8'); PUR_D   = HexColor('#7d3c98')
NAVY   = HexColor('#1a1a2e'); WHITE   = HexColor('#ffffff')
PINK_L = HexColor('#fce4ec'); PINK_D  = HexColor('#c62828')

# ── PAGE GEOMETRY ─────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
MARGIN = 18 * mm
CW = PAGE_W - 2 * MARGIN

OUT = '/mnt/user-data/outputs/Anaemia_MRCP_Note.pdf'
doc = SimpleDocTemplate(OUT, pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=MARGIN, bottomMargin=MARGIN)

# ── PARAGRAPH STYLES ──────────────────────────────────────────────────────────
sTitle = ParagraphStyle('TT', fontName='DV-B', fontSize=22, leading=28,
    textColor=TEAL, spaceAfter=6, alignment=1)
sSub   = ParagraphStyle('TS', fontName='DV-I', fontSize=10, leading=14,
    textColor=TEAL_M, spaceAfter=4, alignment=1)
sH1    = ParagraphStyle('H1', fontName='DV-B', fontSize=13, leading=17,
    textColor=TEAL, spaceAfter=4)
sH2    = ParagraphStyle('H2', fontName='DV-B', fontSize=10, leading=14,
    textColor=TEAL_M, spaceAfter=3)
sBody  = ParagraphStyle('Bo', fontName='DV',   fontSize=9,  leading=14,
    textColor=NAVY,  spaceAfter=3)
sBold  = ParagraphStyle('BB', fontName='DV-B', fontSize=9,  leading=14,
    textColor=NAVY,  spaceAfter=3)
sAlert = ParagraphStyle('Al', fontName='DV-B', fontSize=9,  leading=13,
    textColor=RED_D, spaceAfter=3)
sImg   = ParagraphStyle('Im', fontName='DV-I', fontSize=8,  leading=12,
    textColor=BLUE_D,spaceAfter=2)
sPro   = ParagraphStyle('Pr', fontName='DV-I', fontSize=9,  leading=14,
    textColor=HexColor('#2c3e50'), spaceAfter=3, leftIndent=12)

# ── STORY LIST ────────────────────────────────────────────────────────────────
story = []

# ── HELPER: BODY PARAGRAPH ────────────────────────────────────────────────────
def bp(text, style=None):
    return Paragraph(text, style or sBody)

# ── HELPER: SECTION HEADER ────────────────────────────────────────────────────
def sec_header(text, story):
    story.append(Spacer(1, 6))
    story.append(Paragraph(text, sH1))
    story.append(Spacer(1, 3))

# ── HELPER: DIVIDER ───────────────────────────────────────────────────────────
def divider(story):
    story.append(Spacer(1, 4))
    t = Table([['']], colWidths=[CW])
    t.setStyle(TableStyle([('LINEABOVE',(0,0),(0,0),1,TEAL_M),
        ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
    story.append(t)
    story.append(Spacer(1, 4))

# ── HELPER: PLAIN TABLE (all cells auto-wrapped as Paragraphs) ────────────────
def plain_table(data, widths, header=True):
    rows = []
    for i, row in enumerate(data):
        st = sH2 if (i == 0 and header) else sBody
        rows.append([Paragraph(str(c), st) for c in row])
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),TEAL_L),
        ('TEXTCOLOR',(0,0),(-1,0),TEAL),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,TEAL_XL]),
        ('GRID',(0,0),(-1,-1),0.5,TEAL_M),
        ('TOPPADDING',(0,0),(-1,-1),4),
        ('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),5),
        ('RIGHTPADDING',(0,0),(-1,-1),5),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    return t

# ── HELPER: ALERT BOX (red) ───────────────────────────────────────────────────
def alert_box(text, story):
    t = Table([[Paragraph(f'<b>ALERT: {text}</b>', sAlert)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),RED_L),
        ('BOX',(0,0),(-1,-1),1.5,RED_D),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,4))

# ── HELPER: INFO BOX (amber) ──────────────────────────────────────────────────
def info_box(text, story, color=None, border=None):
    bg = color or AMBER; brd = border or AMBER_B
    t = Table([[Paragraph(text, sBody)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),bg),
        ('BOX',(0,0),(-1,-1),1.5,brd),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,4))

# ── HELPER: IMAGE SEARCH BOX ──────────────────────────────────────────────────
def image_search_box(term, site, story):
    txt = f'IMAGE: Search <b>"{term}"</b> on <b>{site}</b> to visualise this concept.'
    t = Table([[Paragraph(txt, sImg)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),BLUE_L),
        ('BOX',(0,0),(-1,-1),1,BLUE_D),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,4))

# ── HELPER: PROFESSOR BOX (teal) ──────────────────────────────────────────────
def professor_says(text, story):
    t = Table([[Paragraph(f'<i>Professor: {text}</i>', sPro)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),TEAL_XL),
        ('BOX',(0,0),(-1,-1),1,TEAL_M),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,4))

# ── HELPER: MEMORY HOOK (amber) ───────────────────────────────────────────────
def memory_hook(text, story):
    sM = ParagraphStyle('MH', fontName='DV-B', fontSize=8.5, leading=13,
        textColor=HexColor('#7b3f00'), spaceAfter=0)
    t = Table([[Paragraph(f'MEMORY: {text}', sM)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),AMBER),
        ('BOX',(0,0),(-1,-1),1.5,AMBER_B),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,4))

# ── PIL HELPERS ───────────────────────────────────────────────────────────────
DPI = 150
def _px(mm_val): return int(mm_val * DPI / 25.4)
def _fnt(path, size):
    try: return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

_FPATH  = _FD + 'DejaVuSans.ttf'
_FBPATH = _FD + 'DejaVuSans-Bold.ttf'

def wt(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ''
    for w in words:
        test = (cur + ' ' + w).strip()
        try: tw = draw.textlength(test, font=font)
        except: tw = len(test) * 7
        if tw <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines or [text]

def draw_box(draw, x, y, w, fill_hex, border_hex, lines, font, txt_hex, pad=8):
    lh = font.size + 4 if hasattr(font, 'size') else 16
    h = lh * len(lines) + pad * 2
    draw.rectangle([x, y, x+w, y+h], fill=fill_hex, outline=border_hex, width=2)
    ty = y + pad
    for ln in lines:
        try: tw = draw.textlength(ln, font=font)
        except: tw = len(ln)*7
        tx = x + (w - tw) // 2
        draw.text((tx, ty), ln, font=font, fill=txt_hex)
        ty += lh
    return h

def arr_d(draw, x, y, size=14, fill='#555555'):
    draw.polygon([(x,y),(x-size//2,y-size),(x+size//2,y-size)], fill=fill)
    draw.line([(x,y-size),(x,y-size*2)], fill=fill, width=2)

def arr_r(draw, x, y, size=14, fill='#555555'):
    draw.polygon([(x,y),(x-size,y-size//2),(x-size,y+size//2)], fill=fill)
    draw.line([(x-size,y),(x-size*2,y)], fill=fill, width=2)

def arr_l(draw, x, y, size=14, fill='#555555'):
    draw.polygon([(x,y),(x+size,y-size//2),(x+size,y+size//2)], fill=fill)
    draw.line([(x+size,y),(x+size*2,y)], fill=fill, width=2)

def i2r(img, max_w=None):
    buf = io.BytesIO()
    img.save(buf, 'PNG'); buf.seek(0)
    mw = max_w or CW
    iw, ih = img.size
    scale = float(mw) / iw
    return RLImage(buf, width=iw*scale, height=ih*scale)

# ── PIL DIAGRAM 1: RBC LIFECYCLE ──────────────────────────────────────────────
def make_rbc_lifecycle():
    W, H = 900, 580
    img = Image.new('RGB', (W, H), '#ffffff')
    d = ImageDraw.Draw(img)
    fS = _fnt(_FPATH,  13)
    fM = _fnt(_FPATH,  15)
    fB = _fnt(_FBPATH, 16)
    fT = _fnt(_FBPATH, 18)

    # Title
    title = 'RED BLOOD CELL (RBC) LIFECYCLE'
    try: tw = d.textlength(title, font=fT)
    except: tw = len(title)*10
    d.text(((W-tw)//2, 10), title, font=fT, fill='#0d5c63')

    # Top: Kidney box
    kidney_lines = wt(d, 'KIDNEY (detects low O2 in blood)', fM, 200)
    kh = draw_box(d, 30, 50, 220, '#e8f4fd', '#2471a3', kidney_lines, fM, '#1a1a2e', pad=8)

    # Arrow down from kidney
    arr_d(d, 140, 50+kh+28, 14, '#2471a3')
    d.line([(140, 50+kh+2),(140, 50+kh+14)], fill='#2471a3', width=2)
    epo_label = 'EPO signal'
    try: tw2 = d.textlength(epo_label, font=fS)
    except: tw2 = len(epo_label)*8
    d.text((145, 50+kh+8), epo_label, font=fS, fill='#2471a3')

    # Bone marrow box (left column, below kidney)
    bm_y = 50 + kh + 50
    bm_lines = ['BONE MARROW']
    bm_h = draw_box(d, 20, bm_y, 240, '#d4edda', '#28a745', bm_lines, fB, '#155724', pad=10)

    # Maturation stages inside BM
    stages = ['Stem Cell', 'Pronormoblast', 'Normoblast (loses nucleus)', 'Reticulocyte (almost mature)', 'Mature RBC (no nucleus, no mitochondria)']
    sy = bm_y + bm_h + 6
    for s in stages:
        sl = wt(d, s, fS, 220)
        sh = draw_box(d, 30, sy, 210, '#f0fafb', '#1a8a94', sl, fS, '#0d5c63', pad=5)
        if s != stages[-1]:
            arr_d(d, 135, sy+sh+14, 10, '#1a8a94')
            d.line([(135, sy+sh+2),(135, sy+sh+4)], fill='#1a8a94', width=2)
        sy += sh + 20

    # Arrow right from mature RBC to bloodstream
    arr_r(d, 370, sy - 30, 14, '#c0392b')
    d.line([(244, sy-30),(356, sy-30)], fill='#c0392b', width=2)
    d.text((250, sy-48), '  Released into blood', font=fS, fill='#c0392b')

    # Bloodstream box (centre-right)
    bs_y = 180
    bs_lines = wt(d, 'BLOODSTREAM - carries O2 to all body tissues', fM, 250)
    bs_h = draw_box(d, 380, bs_y, 260, '#fce4ec', '#c62828', bs_lines, fM, '#c62828', pad=10)
    d.text((385, bs_y+bs_h+4), '120-day lifespan', font=fS, fill='#c62828')

    # Arrow down from bloodstream to spleen
    arr_d(d, 510, bs_y+bs_h+52, 14, '#555555')
    d.line([(510, bs_y+bs_h+20),(510, bs_y+bs_h+38)], fill='#555555', width=2)
    d.text((516, bs_y+bs_h+28), 'Old/damaged RBCs', font=fS, fill='#555555')

    # Spleen box
    sp_y = bs_y + bs_h + 70
    sp_lines = ['SPLEEN (and liver) - removes', 'old damaged RBCs']
    sp_h = draw_box(d, 380, sp_y, 260, '#f5eef8', '#7d3c98', sp_lines, fM, '#4a235a', pad=8)

    # Three recycling arrows from spleen downward
    rec_y = sp_y + sp_h + 40
    boxes = [
        ('Iron recycled', 'via Transferrin', 'to Bone Marrow', '#e0f4f5', '#1a8a94', '#0d5c63'),
        ('Haem -> Bilirubin', 'via Liver -> Bile', '-> excreted in stool', '#fff3cd', '#e6a817', '#7b3f00'),
        ('Globin -> Amino', 'acids recycled', 'for new proteins', '#d4edda', '#28a745', '#155724'),
    ]
    bx_w = 75
    bx_start = 385
    for i, (t1, t2, t3, fc, bc, tc) in enumerate(boxes):
        bx = bx_start + i * 88
        arr_d(d, bx+38, rec_y-2, 10, '#555555')
        d.line([(bx+38, sp_y+sp_h+2),(bx+38, rec_y-16)], fill='#555555', width=2)
        bl = [t1, t2, t3]
        bh = draw_box(d, bx, rec_y, bx_w, fc, bc, bl, fS, tc, pad=5)

    # Arrow from iron box back to bone marrow (left)
    arr_l(d, 383, rec_y+20, 12, '#1a8a94')
    d.text((280, rec_y+12), '<- iron recycled', font=fS, fill='#1a8a94')

    # Crop to content
    final_h = rec_y + 100
    img = img.crop((0, 0, W, min(final_h, H)))
    return i2r(img)

# ── PIL DIAGRAM 2: ANAEMIA CLASSIFICATION FLOWCHART ───────────────────────────
def make_anaemia_classification():
    W, H = 900, 660
    img = Image.new('RGB', (W, H), '#ffffff')
    d = ImageDraw.Draw(img)
    fS = _fnt(_FPATH,  12)
    fM = _fnt(_FPATH,  14)
    fB = _fnt(_FBPATH, 15)
    fT = _fnt(_FBPATH, 18)

    title = 'ANAEMIA CLASSIFICATION BY MCV (Mean Cell Volume)'
    try: tw = d.textlength(title, font=fT)
    except: tw = len(title)*11
    d.text(((W-tw)//2, 8), title, font=fT, fill='#0d5c63')

    # Top: Anaemia box
    an_lines = wt(d, 'ANAEMIA = Low Haemoglobin (Hb)', fB, 300)
    an_h = draw_box(d, 280, 45, 340, '#e0f4f5', '#0d5c63', an_lines, fB, '#0d5c63', pad=10)

    # Arrow down
    arr_d(d, 450, 45+an_h+28, 14, '#555555')
    d.line([(450,45+an_h+2),(450,45+an_h+14)], fill='#555555', width=2)

    # MCV check box
    mv_y = 45+an_h+45
    mv_lines = wt(d, 'Step 1: Check MCV (Mean Cell Volume - average size of red cells)', fM, 400)
    mv_h = draw_box(d, 225, mv_y, 450, '#fff3cd', '#e6a817', mv_lines, fM, '#7b3f00', pad=8)

    # Three branch lines
    bline_y = mv_y + mv_h + 10
    branch_y = bline_y + 50
    d.line([(450, mv_y+mv_h),(450, bline_y)], fill='#555555', width=2)
    d.line([(120, bline_y),(780, bline_y)], fill='#555555', width=2)
    d.line([(120, bline_y),(120, branch_y)], fill='#555555', width=2)
    d.line([(450, bline_y),(450, branch_y)], fill='#555555', width=2)
    d.line([(780, bline_y),(780, branch_y)], fill='#555555', width=2)

    # Three MCV boxes
    mic_h = draw_box(d, 20, branch_y, 200, '#fde8e8', '#c0392b', ['MICROCYTIC', 'MCV < 80 fL'], fB, '#c0392b', pad=8)
    nor_h = draw_box(d, 350, branch_y, 200, '#e0f4f5', '#0d5c63', ['NORMOCYTIC', 'MCV 80-100 fL'], fB, '#0d5c63', pad=8)
    mac_h = draw_box(d, 680, branch_y, 200, '#d4edda', '#28a745', ['MACROCYTIC', 'MCV > 100 fL'], fB, '#155724', pad=8)

    # Causes lists
    causes_y = branch_y + max(mic_h, nor_h, mac_h) + 30

    mic_causes = ['Iron Deficiency (most common)', 'Thalassaemia', 'Anaemia of Chronic Disease', 'Sideroblastic Anaemia', 'Lead Poisoning']
    nor_causes = ['Acute Blood Loss', 'Haemolytic Anaemia', 'Anaemia of Chronic Disease', 'Aplastic Anaemia', 'Renal (low EPO)', 'Mixed B12 + Fe deficiency']
    mac_causes = ['B12 Deficiency', 'Folate Deficiency', 'Alcohol excess', 'Liver disease', 'Hypothyroidism', 'Drugs (methotrexate etc)', 'Reticulocytosis']

    def cause_list(cx, cy, causes, clr):
        y = cy
        for c in causes:
            cl = wt(d, '  ' + c, fS, 185)
            ch = draw_box(d, cx, y, 195, '#ffffff', clr, cl, fS, '#1a1a2e', pad=4)
            arr_d(d, cx+98, y-2, 8, clr)
            d.line([(cx+98,y-14),(cx+98,y-2)], fill=clr, width=1)
            y += ch + 8
        return y

    cause_list(22, causes_y, mic_causes, '#c0392b')
    cause_list(352, causes_y, nor_causes, '#0d5c63')
    cause_list(682, causes_y, mac_causes, '#28a745')

    # Memory mnemonic
    mn_y = causes_y + 260
    mn_lines = wt(d, 'MICROCYTIC mnemonic: TAILS = Thalassaemia, Anaemia of CD, Iron deficiency, Lead, Sideroblastic', fS, 850)
    draw_box(d, 20, mn_y, 860, '#fff3cd', '#e6a817', mn_lines, fS, '#7b3f00', pad=6)

    final_h = mn_y + 60
    img = img.crop((0, 0, W, min(final_h, H)))
    return i2r(img)

# ── PIL DIAGRAM 3: IRON CYCLE ─────────────────────────────────────────────────
def make_iron_cycle():
    W, H = 900, 560
    img = Image.new('RGB', (W, H), '#ffffff')
    d = ImageDraw.Draw(img)
    fS = _fnt(_FPATH,  12)
    fM = _fnt(_FPATH,  14)
    fB = _fnt(_FBPATH, 15)
    fT = _fnt(_FBPATH, 18)

    title = 'IRON METABOLISM - The Complete Cycle'
    try: tw = d.textlength(title, font=fT)
    except: tw = len(title)*11
    d.text(((W-tw)//2, 8), title, font=fT, fill='#0d5c63')

    # Diet box (top left)
    diet_h = draw_box(d, 20, 45, 160, '#fef3e2', '#d4640a', ['DIETARY IRON', 'Haem (meat) 25% absorbed', 'Non-haem (plants) 5%'], fS, '#d4640a', pad=6)

    # Arrow right to gut
    arr_r(d, 230, 45+diet_h//2, 14, '#d4640a')
    d.line([(182, 45+diet_h//2),(216, 45+diet_h//2)], fill='#d4640a', width=2)

    # Gut/duodenum box
    gut_y = 45
    gut_h = draw_box(d, 240, gut_y, 180, '#fff3cd', '#e6a817', ['DUODENUM & upper JEJUNUM', 'Fe3+ reduced to Fe2+', 'Ferroportin exports iron', 'Hepcidin BLOCKS ferroportin'], fS, '#7b3f00', pad=6)

    # Arrow right to transferrin
    tr_y = gut_y + gut_h//2
    arr_r(d, 480, tr_y, 14, '#2471a3')
    d.line([(422, tr_y),(466, tr_y)], fill='#2471a3', width=2)

    # Transferrin box (centre)
    tf_lines = wt(d, 'TRANSFERRIN (transport protein in blood)', fM, 180)
    tf_y = gut_y
    tf_h = draw_box(d, 490, tf_y, 200, '#e8f4fd', '#2471a3', tf_lines + ['30% saturated normally'], fM, '#1a1a2e', pad=6)

    # Three destinations from transferrin
    dest_y = tf_y + tf_h + 50
    d.line([(590, tf_y+tf_h),(590, dest_y-10)], fill='#555555', width=2)
    d.line([(200, dest_y-10),(830, dest_y-10)], fill='#555555', width=2)
    for cx in [200, 590, 830]:
        d.line([(cx, dest_y-10),(cx, dest_y)], fill='#555555', width=2)

    # Dest boxes
    draw_box(d, 110, dest_y, 170, '#d4edda', '#28a745', ['BONE MARROW', '65% of body iron', 'Makes haemoglobin'], fS, '#155724', pad=6)
    draw_box(d, 505, dest_y, 170, '#fce4ec', '#c62828', ['LIVER/SPLEEN', 'Ferritin stores iron', '20% of body iron'], fS, '#c62828', pad=6)
    draw_box(d, 745, dest_y, 170, '#f5eef8', '#7d3c98', ['MUSCLES/TISSUES', 'Myoglobin', '15% of body iron'], fS, '#4a235a', pad=6)

    # Recycling: Spleen -> macrophages -> transferrin
    rec_y = dest_y + 100
    d.line([(590, dest_y+70),(590, rec_y)], fill='#c62828', width=2)
    d.text((595, dest_y+78), 'RBC destroyed after 120 days', font=fS, fill='#c62828')
    draw_box(d, 490, rec_y, 200, '#fde8e8', '#c0392b', ['MACROPHAGES', 'break down haem', 'FREE IRON released'], fS, '#c0392b', pad=6)

    # Arrow from macrophages back to transferrin (cycle)
    cyc_lines = ['Iron re-enters', 'circulation via', 'transferrin']
    arr_l(d, 488, rec_y+30, 12, '#2471a3')
    d.line([(400, rec_y+30),(476, rec_y+30)], fill='#2471a3', width=2)
    draw_box(d, 200, rec_y+10, 190, '#e8f4fd', '#2471a3', cyc_lines, fS, '#1a1a2e', pad=5)

    # Hepcidin label
    hep_lines = wt(d, 'HEPCIDIN (liver hormone) - the master regulator: HIGH iron -> more hepcidin -> blocks ferroportin -> less absorption. Low iron -> less hepcidin -> more absorption.', fS, 860)
    h_y = rec_y + 120
    draw_box(d, 20, h_y, 860, '#fff3cd', '#e6a817', hep_lines, fS, '#7b3f00', pad=6)

    final_h = h_y + 80
    img = img.crop((0, 0, W, min(final_h, H)))
    return i2r(img)

# ── PIL DIAGRAM 4: HAEMOLYSIS PATHWAYS ────────────────────────────────────────
def make_haemolysis_diagram():
    W, H = 900, 520
    img = Image.new('RGB', (W, H), '#ffffff')
    d = ImageDraw.Draw(img)
    fS = _fnt(_FPATH,  12)
    fM = _fnt(_FPATH,  14)
    fB = _fnt(_FBPATH, 15)
    fT = _fnt(_FBPATH, 18)

    title = 'HAEMOLYSIS PATHWAYS - Intravascular vs Extravascular'
    try: tw = d.textlength(title, font=fT)
    except: tw = len(title)*11
    d.text(((W-tw)//2, 8), title, font=fT, fill='#0d5c63')

    # Haemolysis box at top centre
    hem_lines = wt(d, 'HAEMOLYSIS = Premature Destruction of RBCs', fB, 350)
    hem_h = draw_box(d, 275, 45, 350, '#fde8e8', '#c0392b', hem_lines, fB, '#c0392b', pad=10)

    # Two branch lines
    b_y = 45 + hem_h + 10
    end_y = b_y + 40
    d.line([(450, 45+hem_h),(450, b_y)], fill='#555555', width=2)
    d.line([(220, b_y),(680, b_y)], fill='#555555', width=2)
    d.line([(220, b_y),(220, end_y)], fill='#555555', width=2)
    d.line([(680, b_y),(680, end_y)], fill='#555555', width=2)

    # Left: Intravascular
    iv_h = draw_box(d, 20, end_y, 400, '#fce4ec', '#c62828', ['INTRAVASCULAR HAEMOLYSIS', '(RBCs destroyed INSIDE blood vessels)'], fB, '#c62828', pad=10)

    # Right: Extravascular
    ev_h = draw_box(d, 480, end_y, 400, '#f5eef8', '#7d3c98', ['EXTRAVASCULAR HAEMOLYSIS', '(RBCs destroyed in SPLEEN and LIVER)'], fB, '#4a235a', pad=10)

    cause_y = end_y + max(iv_h, ev_h) + 15

    # Intravascular causes
    iv_causes = ['G6PD deficiency', 'Autoimmune haemolytic anaemia (warm)', 'Mechanical (prosthetic heart valves)', 'Paroxysmal Nocturnal Haemoglobinuria', 'Microangiopathic (TTP, HUS, DIC)']
    iv_markers = ['Free Hb in plasma (haemoglobinaemia)', 'Haemoglobinaemia + haemoglobinuria (red urine)', 'Haptoglobin VERY LOW (binds free Hb)', 'LDH raised (leaks from destroyed cells)', 'Haemosiderinuria (iron in urine late)']

    # Extravascular causes
    ev_causes = ['Hereditary spherocytosis', 'Sickle cell disease', 'Thalassaemia', 'Cold AIHA', 'Liver/spleen trapping']
    ev_markers = ['Unconjugated bilirubin HIGH (jaundice)', 'Urobilinogen raised in urine', 'Haptoglobin mildly reduced', 'Splenomegaly prominent', 'LDH mildly raised']

    # Draw cause and marker boxes
    def side_boxes(cx, cy, items, fc, bc, tc):
        y = cy
        for item in items:
            il = wt(d, item, fS, 370)
            ih = draw_box(d, cx, y, 385, fc, bc, il, fS, tc, pad=4)
            y += ih + 5
        return y

    y1 = side_boxes(22, cause_y, ['CAUSES:'] + iv_causes, '#fde8e8', '#c0392b', '#c0392b')
    side_boxes(22, y1+5, ['LAB MARKERS:'] + iv_markers, '#fff3cd', '#e6a817', '#7b3f00')

    y2 = side_boxes(482, cause_y, ['CAUSES:'] + ev_causes, '#f5eef8', '#7d3c98', '#4a235a')
    side_boxes(482, y2+5, ['LAB MARKERS:'] + ev_markers, '#d4edda', '#28a745', '#155724')

    final_h = max(y1, y2) + 220
    img = img.crop((0, 0, W, min(final_h, H)))
    return i2r(img)

# ── BUILD DIAGRAMS ────────────────────────────────────────────────────────────
print('Building PIL diagrams...')
rbc_img   = make_rbc_lifecycle()
class_img = make_anaemia_classification()
iron_img  = make_iron_cycle()
haem_img  = make_haemolysis_diagram()
print('PIL diagrams done.')

# ═══════════════════════════════════════════════════════════════════════════════
# STORY BEGINS
# ═══════════════════════════════════════════════════════════════════════════════

# ── TITLE PAGE ────────────────────────────────────────────────────────────────
story.append(Spacer(1, 8))
story.append(Paragraph('ANAEMIA', sTitle))
story.append(Paragraph('Comprehensive MRCP Revision Note | Parts 1, 2 &amp; PACES', sSub))
story.append(Paragraph('From First Principles to Examination Mastery', sSub))
story.append(Spacer(1, 6))

tag_data = [['Topic','Coverage','Style','Standard'],
    ['Anaemia — all types', 'Part 1 + Part 2 + PACES','Teach Me From Zero','MRCP 2026']]
story.append(plain_table(tag_data, [CW*0.25, CW*0.25, CW*0.25, CW*0.25]))
story.append(Spacer(1, 8))
divider(story)

# ── SECTION 1: OVERVIEW ───────────────────────────────────────────────────────
sec_header('Section 1: Overview — What Is Anaemia and Why Does It Matter?', story)
professor_says('Imagine your blood as a delivery service. Red blood cells are the delivery vans, and oxygen is the package they carry. Anaemia means you do not have enough vans — or the vans are broken — so the oxygen does not arrive where it needs to go. The body notices this shortage and sends alarm signals. Those alarm signals are the symptoms we see.', story)

story.append(bp('<b>ANAEMIA</b> (pronounced an-EE-me-a, from Greek: "without blood") is defined as a reduction in '
    'the concentration of haemoglobin (Hb — the red oxygen-carrying protein inside red blood cells) '
    'below the normal level for that person\'s age and sex. '
    'It is not a diagnosis in itself — it is a <b>sign of an underlying problem</b> that must be found.'))
story.append(Spacer(1,4))

story.append(bp('<b>Normal Haemoglobin ranges</b> (these are the standard thresholds used by the WHO — '
    'World Health Organisation — and MRCP):'))
hb_norms = [
    ['Group', 'Normal Hb (g/dL = grams per decilitre)', 'Anaemia defined as'],
    ['Adult men', '13.5–17.5 g/dL', '< 13.0 g/dL'],
    ['Adult women (non-pregnant)', '11.5–15.5 g/dL', '< 12.0 g/dL'],
    ['Pregnant women', '11.0–14.0 g/dL (physiologically lower — see Section 10)', '< 11.0 g/dL'],
    ['Children 6 months–5 years', '11.0–14.0 g/dL', '< 11.0 g/dL'],
    ['Elderly (>65 years)', 'Same thresholds, but anaemia more common and often under-investigated', '< 13.0 (men), < 12.0 (women)'],
]
story.append(plain_table(hb_norms, [CW*0.22, CW*0.40, CW*0.38]))

story.append(Spacer(1,6))
story.append(bp('<b>Why anaemia matters clinically</b> — the consequences of insufficient oxygen delivery:'))
why_table = [
    ['System affected', 'What happens', 'Symptoms you see'],
    ['Brain (needs constant O2)', 'Neurons (brain cells) poorly oxygenated', 'Dizziness, headache, poor concentration, fainting (syncope)'],
    ['Heart (works harder to compensate)', 'Pumps faster and harder to deliver same O2 with fewer RBCs', 'Palpitations, shortness of breath on exertion, angina (chest pain from heart muscle starved of O2 — especially dangerous in pre-existing heart disease)'],
    ['Muscles', 'Insufficient O2 for aerobic (oxygen-based) energy production', 'Fatigue, weakness, exercise intolerance'],
    ['Skin & mucous membranes', 'Less blood reaching skin surface', 'Pallor (paleness) of skin, conjunctivae (inner lower eyelid), palms'],
    ['Kidneys (sense low O2)', 'Detect hypoxia (low O2) and increase EPO production', 'Often normal unless chronic anaemia → renal impairment'],
    ['Foetus (in pregnancy)', 'Placenta delivers less O2 to growing baby', 'Intrauterine growth restriction (IUGR), preterm birth'],
]
story.append(plain_table(why_table, [CW*0.22, CW*0.36, CW*0.42]))

story.append(Spacer(1,6))
story.append(bp('<b>Global burden:</b> Anaemia affects approximately <b>1.62 billion people worldwide</b> '
    '(25% of the global population). Iron deficiency anaemia (IDA) is the <b>most common nutritional disorder on Earth</b>. '
    'In the UK, approximately 20% of women of childbearing age have iron deficiency. '
    'Despite being so common, anaemia is frequently undertreated — particularly in elderly patients.'))
divider(story)

# ── SECTION 2: ANATOMY & PHYSIOLOGY ──────────────────────────────────────────
sec_header('Section 2: Anatomy & Physiology — How Blood Works', story)
professor_says('Before you can understand why blood goes wrong, you need to see how it works when it goes right. Think of blood as a river system: red cells (the boats carrying oxygen), white cells (the army defending the river), platelets (the repair crew fixing leaks), and plasma (the river water itself — carrying proteins, nutrients, waste products).', story)

story.append(bp('<b>BLOOD COMPOSITION</b> — blood makes up approximately 7-8% of body weight (about 5 litres in a 70kg adult):'))
blood_comp = [
    ['Component', 'What it is', 'Normal count/level', 'Primary function'],
    ['Red Blood Cells (RBCs)\nErythrocytes', 'Biconcave disc (donut-shaped without the hole all the way through). No nucleus. No mitochondria. Packed with haemoglobin.', 'Men: 4.5-5.5 x10^12/L\nWomen: 3.8-4.8 x10^12/L', 'Carry O2 from lungs to tissues. Carry CO2 (carbon dioxide — waste gas) back to lungs.'],
    ['Haemoglobin (Hb)', 'A protein made of 4 chains (globin) each with a haem group in the centre. The haem group contains iron which binds O2. Normal HbA (adult) = 2 alpha + 2 beta chains.', 'Men: 13.5-17.5 g/dL\nWomen: 11.5-15.5 g/dL', 'Each Hb molecule carries 4 O2 molecules (one per haem group). Without iron, haemoglobin cannot carry O2.'],
    ['White Blood Cells (WBCs)\nLeukocytes', 'Various types (neutrophils, lymphocytes, monocytes, eosinophils, basophils). Have nuclei. Short lifespan (hours to days).', '4.0-11.0 x10^9/L total', 'Immune defence against infection, cancer cells, foreign bodies.'],
    ['Platelets\nThrombocytes', 'Tiny fragments from megakaryocytes (giant bone marrow cells). No nucleus. Contain clotting proteins.', '150-400 x10^9/L', 'Form the primary platelet plug when a blood vessel is damaged. Initiate clotting cascade.'],
    ['Plasma', 'The liquid part of blood (55% of blood volume). Mostly water (90%). Contains proteins (albumin, globulins, clotting factors), glucose, electrolytes, hormones, waste products.', 'Not counted — it is the liquid', 'Transports all dissolved substances. Maintains blood pressure, pH, and temperature.'],
]
story.append(plain_table(blood_comp, [CW*0.14, CW*0.30, CW*0.20, CW*0.36]))

story.append(Spacer(1,8))
story.append(bp('<b>HAEMATOPOIESIS</b> (hay-mat-oh-po-EE-sis) — the process of making blood cells:'))
professor_says('Think of the bone marrow as the factory for all blood cells. All blood cells start as the same raw material — the pluripotent stem cell (a master cell that can become any type of blood cell). Then, depending on which hormones are present, the stem cell is guided down different production lines.', story)

hpoe = [
    ['Stage', 'Location', 'What happens', 'Key hormone'],
    ['Before birth', 'Yolk sac (weeks 3-8), liver and spleen (weeks 6-28)', 'Haematopoiesis (blood making) begins outside bones. This is why liver/spleen enlarge in diseases causing extramedullary haematopoiesis (blood making outside marrow — as in thalassaemia major).', 'None specific'],
    ['Birth to adulthood', 'All bones initially, then restricted to flat bones (sternum, ribs, skull, pelvis, vertebrae) and ends of long bones by adulthood', 'Red bone marrow is the active factory. Yellow (fatty) marrow stores energy and can reactivate if needed (e.g. in haemolytic anaemia — the marrow \'converts\' back to red marrow).', 'EPO (erythropoietin from kidneys)'],
    ['EPO signal', 'Kidney peritubular cells (cells surrounding kidney tubules) detect low O2 → produce EPO', 'EPO travels via blood to bone marrow → binds receptors on erythroid progenitors → stimulates proliferation and maturation into RBCs', 'EPO (erythropoietin)'],
    ['RBC maturation\n(6-7 days)', 'In bone marrow: Pluripotent stem cell > Myeloid progenitor > Erythroid progenitor > Pronormoblast > Basophilic normoblast > Polychromatic normoblast > Orthochromatic normoblast > Reticulocyte > Mature RBC', 'As cells mature: nucleus condenses and is expelled (enucleation). Cell fills with haemoglobin. Mitochondria are lost. Cell becomes the classic biconcave disc — this shape gives maximum surface area:volume ratio for gas exchange.', 'EPO, iron, B12, folate, vitamin C'],
    ['Reticulocyte', 'Released from bone marrow into bloodstream. Matures over 1-2 days in blood.', 'A reticulocyte (reh-TIK-yoo-lo-site) is an immature RBC still containing ribosomes (RNA remnants). It stains blue/purple on special stains. Normal reticulocyte count 0.5-2.5% of RBCs. RAISED reticulocyte count = bone marrow working hard (haemolysis, blood loss, recovery from treatment). LOW reticulocyte count = bone marrow not responding (aplastic anaemia, infiltration, deficiency states).', 'EPO + maturation factors'],
    ['RBC lifespan', '120 days in circulation', 'Old/damaged RBCs are recognised by splenic macrophages (the spleen\'s cleaning cells) and removed. The haem → bilirubin. Iron → recycled via transferrin. Globin → amino acids.', 'No specific hormone'],
]
story.append(plain_table(hpoe, [CW*0.14, CW*0.18, CW*0.45, CW*0.23]))
story.append(Spacer(1,6))
story.append(rbc_img)
story.append(Spacer(1,4))
story.append(bp('<i>Figure 1: The complete RBC lifecycle — from EPO signal through bone marrow maturation, '
    'circulation, and recycling by the spleen. Understanding this cycle explains every type of anaemia.</i>', sImg))
divider(story)

# ── SECTION 3: IRON METABOLISM ────────────────────────────────────────────────
sec_header('Section 3: Iron Metabolism — The Iron Story From Plate to Protein', story)
professor_says('Iron is the most important single element for making haemoglobin. Without iron, the haem group cannot hold oxygen. Think of iron as the engine in the delivery van — without it, the van is just a box on wheels. The body is extremely clever about managing iron — it has no dedicated excretion mechanism (unlike most other minerals), so it controls iron levels entirely through absorption. This is regulated by one master hormone: hepcidin.', story)

story.append(bp('<b>Total body iron:</b> approximately 3–4 grams in an adult. Distribution:'))
fe_dist = [
    ['Compartment', 'Amount', 'Form', 'Function'],
    ['Haemoglobin (in RBCs)', '~65% (2–2.5g)', 'Haem-iron (Fe2+ bound to porphyrin ring)', 'O2 transport — the main use of iron'],
    ['Storage (liver, spleen, bone marrow)', '~20-25% (1–1.5g)', 'Ferritin (soluble, inside cells) and haemosiderin (insoluble, older storage form)', 'Reserve pool. Ferritin releases iron when needed. Serum ferritin is a surrogate marker of iron stores — LOW ferritin = iron deficiency.'],
    ['Myoglobin (muscle)', '~10-15% (300mg)', 'Haem-iron', 'Muscle O2 storage and use'],
    ['Transport (blood plasma)', '~0.1% (3-4mg)', 'Bound to transferrin (each transferrin molecule has 2 iron binding sites)', 'Carries iron from gut and recycling to bone marrow. Transferrin saturation (% of sites occupied) normally ~30%. Low saturation = iron deficiency. High = iron overload.'],
    ['Enzymes and other proteins', '~5-10%', 'Various', 'Cytochromes (energy production in mitochondria), catalase, ribonucleotide reductase (DNA synthesis)'],
]
story.append(plain_table(fe_dist, [CW*0.22, CW*0.12, CW*0.26, CW*0.40]))

story.append(Spacer(1,6))
story.append(bp('<b>Iron absorption — how iron gets from food into the body:</b>'))
fe_abs = [
    ['Step', 'Detail', 'Clinical relevance'],
    ['1 — Food sources', 'HAEM iron (from meat, fish, poultry — the haem molecule from myoglobin and haemoglobin): absorbed at 20-30% efficiency. NON-HAEM iron (from plant sources — spinach, lentils, fortified cereals, eggs): absorbed at only 5-10% efficiency. Daily requirement: men 8mg, women 18mg (higher due to menstrual losses), pregnancy 27mg.', 'Vegetarians and vegans are at higher risk of IDA. Vitamin C (ascorbic acid) doubles non-haem iron absorption by reducing Fe3+ to Fe2+ (the absorbable form). Tea, coffee, calcium, phytates (in bran) reduce absorption.'],
    ['2 — Stomach', 'Gastric acid (hydrochloric acid) reduces Fe3+ (ferric iron, the form in food) to Fe2+ (ferrous iron, the absorbable form). The enzyme ferrireductase (duodenal cytochrome b) also assists.', 'ACHLORHYDRIA (no stomach acid) — e.g. in PPI (proton pump inhibitor) overuse, gastric atrophy, gastrectomy — impairs iron absorption. This is why IDA can be caused by long-term PPIs.'],
    ['3 — Duodenal absorption', 'Fe2+ enters duodenal enterocytes (gut lining cells) via the DMT-1 transporter (Divalent Metal Transporter 1). Inside the cell, iron is stored as ferritin or exported.', 'The duodenum and proximal jejunum are the ONLY sites of iron absorption. Any disease damaging this area (e.g. coeliac disease damaging the duodenal villi) → iron malabsorption.'],
    ['4 — Export into blood', 'Ferroportin (the only known iron export protein in the body) transports iron from enterocytes into the bloodstream. Iron then binds to transferrin.', 'HEPCIDIN (a peptide hormone made by the liver) DEGRADES ferroportin — blocking iron export. This is the master switch: high iron or inflammation → liver makes more hepcidin → less iron absorbed. Low iron → less hepcidin → more iron absorbed. Hepcidin is why inflammation causes the "anaemia of chronic disease."'],
    ['5 — Body iron regulation', 'The body cannot actively excrete iron. Iron is lost only through: intestinal cell shedding (1mg/day), blood loss (menstruation, GI bleeding), sweat, skin cells. Net balance: absorb exactly as much as you lose.', 'Any cause of BLOOD LOSS = iron loss = potential IDA. Menstrual blood loss >80ml/cycle = menorrhagia = commonest cause of IDA in women of childbearing age. GI blood loss is the commonest cause in men and post-menopausal women — always investigate.'],
]
story.append(plain_table(fe_abs, [CW*0.10, CW*0.47, CW*0.43]))
story.append(Spacer(1,6))
story.append(iron_img)
story.append(Spacer(1,4))
story.append(bp('<i>Figure 2: The iron cycle — from dietary intake through absorption, transport, use, '
    'and recycling. Hepcidin is the master regulator controlling how much iron enters the bloodstream.</i>', sImg))
memory_hook('HEPCIDIN = the GATE KEEPER of iron. When the liver makes more hepcidin (due to high iron OR inflammation), it LOCKS the gate (ferroportin) and no iron gets out of the gut or recycling stores into the blood. Anaemia of chronic disease = inflammation-driven high hepcidin = iron locked away despite adequate stores.', story)
divider(story)

# ── SECTION 4: CLASSIFICATION FRAMEWORK ──────────────────────────────────────
sec_header('Section 4: Classification Framework — How to Approach Any Anaemia', story)
professor_says('When you see a low Hb, your first question is always: what size are the red cells? This is measured by the MCV — Mean Cell Volume — the average volume of a single red blood cell, measured in femtolitres (fL — a femtolitre is one quadrillionth of a litre). The MCV immediately narrows your differential diagnosis to three categories. From there, you ask more specific questions.', story)

story.append(bp('<b>MCV (Mean Cell Volume)</b> — the most important first discriminator in anaemia workup. Normal: 80–100 fL.'))
story.append(Spacer(1,4))
story.append(class_img)
story.append(Spacer(1,4))
story.append(bp('<i>Figure 3: Anaemia classification by MCV. The TAILS mnemonic covers all microcytic causes. '
    'Most normocytic anaemias are found via clinical context. Macrocytic anaemia always prompts B12/folate check.</i>', sImg))

story.append(Spacer(1,6))
story.append(bp('<b>Second discriminator — the RETICULOCYTE COUNT</b> (normal 0.5-2.5% of RBCs, or 25-100 x10^9/L):'))
retic_table = [
    ['Reticulocyte count', 'What it tells you', 'Interpretation'],
    ['RAISED (>2.5% or >100 x10^9/L)\n= Hyperproliferative', 'Bone marrow is working hard, producing more young cells in response to anaemia', 'HAEMOLYTIC ANAEMIA (RBCs being destroyed → marrow compensates) or BLOOD LOSS (acute haemorrhage → marrow compensates) or TREATMENT RESPONSE (iron/B12 given → marrow responding — reticulocyte peak at 7-10 days post-treatment)'],
    ['NORMAL/LOW (<0.5% or <25 x10^9/L)\n= Hypoproliferative', 'Bone marrow is NOT responding appropriately despite low Hb', 'DEFICIENCY STATES (iron, B12, folate — marrow lacks building materials) or APLASTIC ANAEMIA (marrow failure) or MARROW INFILTRATION (leukaemia, lymphoma, myeloma, metastases) or RENAL ANAEMIA (not enough EPO to stimulate marrow) or ANAEMIA OF CHRONIC DISEASE'],
]
story.append(plain_table(retic_table, [CW*0.25, CW*0.30, CW*0.45]))

story.append(Spacer(1,6))
story.append(bp('<b>The systematic blood count — key parameters and what they mean:</b>'))
fbc_params = [
    ['Parameter', 'What it measures', 'Normal range', 'Low means', 'High means'],
    ['Hb\n(Haemoglobin)', 'Total Hb concentration in blood', 'Men: 13.5-17.5\nWomen: 11.5-15.5 g/dL', 'Anaemia', 'Polycythaemia (too many RBCs — dehydration, myeloproliferative disorder, high altitude)'],
    ['MCV\n(Mean Cell Volume)', 'Average size of one RBC', '80-100 fL', 'Microcytic: IDA, thalassaemia, sideroblastic', 'Macrocytic: B12/folate deficiency, alcohol, liver disease, hypothyroidism'],
    ['MCH\n(Mean Cell Haemoglobin)', 'Average amount of Hb in one RBC', '27-33 pg', 'Hypochromic (pale cells — less Hb per cell): IDA, thalassaemia', 'Hyperchromic: not clinically seen in isolation (usually macrocytic anaemias)'],
    ['MCHC\n(Mean Cell Hb Concentration)', 'Concentration of Hb within RBCs', '315-360 g/L', 'Hypochromic: IDA', 'Raised MCHC (>360): HEREDITARY SPHEROCYTOSIS (small dense spherical cells)'],
    ['RDW\n(Red cell Distribution Width)', 'Variability in RBC size (anisocytosis)', '11.5-14.5%', 'Not clinically relevant', 'HIGH RDW = MIXED picture (e.g. IDA + B12 together) or active haemolysis. Helps distinguish IDA (high RDW) from thalassaemia trait (normal RDW — cells all uniformly small)'],
    ['Reticulocytes', 'Young RBCs — just released from marrow', '0.5-2.5%', 'Bone marrow NOT responding (aplasia, deficiency)', 'Bone marrow working HARD (haemolysis, blood loss, treatment response)'],
    ['Ferritin', 'Main intracellular iron storage protein. Serum ferritin is an acute phase reactant (rises with inflammation).', '12-300 mcg/L', 'LOW ferritin = iron deficiency (specific — first test to fall)', 'HIGH ferritin = iron overload (haemochromatosis), inflammation, liver disease, malignancy, ferritin can be falsely normal in IDA+inflammation'],
    ['Serum iron', 'Iron in transit (bound to transferrin)', '11-30 micromol/L', 'IDA, anaemia of chronic disease', 'Iron overload, haemolysis'],
    ['Transferrin\nTIBC\n(Total Iron Binding Capacity)', 'Capacity of transferrin to bind iron. Reflects transferrin level.', 'TIBC: 45-70 micromol/L\nTransferrin sat: 20-40%', 'ACD, liver disease, protein malnutrition', 'IDA (more transferrin made to capture scarce iron) — TIBC raised in IDA'],
]
story.append(plain_table(fbc_params, [CW*0.12, CW*0.22, CW*0.18, CW*0.22, CW*0.26]))
memory_hook('IDA PATTERN: Low Hb, Low MCV, Low MCH, Low ferritin, LOW serum iron, HIGH TIBC, LOW transferrin saturation. TAILS mnemonic for microcytic causes. Remember: TIBC goes UP in IDA (the body makes MORE of the transport protein when iron is scarce — like building more trucks when there is less cargo).', story)
divider(story)

# ── SECTION 5: IRON DEFICIENCY ANAEMIA (IDA) ─────────────────────────────────
sec_header('Section 5: Iron Deficiency Anaemia (IDA) — The World\'s Most Common Anaemia', story)
professor_says('Iron deficiency anaemia is like running out of fuel for the delivery vans. The vans are there (bone marrow is trying to make RBCs), but without iron, each van can only be half-filled with oxygen. The cells get smaller and paler — hypochromic (hypo = less, chromic = colour) microcytic (micro = small, cytic = cell) anaemia.', story)

story.append(bp('IDA is the most common cause of anaemia worldwide, affecting approximately 500 million people. '
    'Understanding the <b>CAUSE</b> is as important as treating the deficiency — '
    'iron deficiency in an adult man or post-menopausal woman is a GI malignancy '
    'until proven otherwise and demands urgent investigation.'))
story.append(Spacer(1,4))

story.append(bp('<b>Causes of IDA — organised by mechanism:</b>'))
ida_causes = [
    ['Mechanism', 'Specific causes', 'Who to suspect', 'Key investigation'],
    ['Insufficient intake\n(not eating enough iron)',
     'Poor diet: vegan/vegetarian diet without supplementation, poverty, eating disorders, restrictive diets. Infants on exclusive breast milk beyond 6 months (breast milk is low in iron).',
     'Young vegan women, elderly living alone, infants, food insecurity.',
     'Dietary history. Ferritin + serum iron. Dietary supplementation may suffice.'],
    ['Impaired absorption\n(cannot absorb iron from gut)',
     'Coeliac disease (gluten-triggered immune destruction of duodenal villi — the finger-like projections that absorb nutrients). Atrophic gastritis (thinning of stomach lining → no acid → poor Fe reduction). Post-gastrectomy or bariatric surgery (bypass duodenum). Long-term PPIs. Crohn\'s disease affecting duodenum/jejunum.',
     'Any unexplained IDA not responding to oral iron. Check for coeliac antibodies (anti-TTG IgA — tissue transglutaminase). Young women with IDA plus other unexplained symptoms (fatigue, bloating, diarrhoea).',
     'Anti-TTG IgA + total IgA. Endoscopy + duodenal biopsy. H. pylori testing (H. pylori-associated gastritis impairs iron absorption).'],
    ['Increased demand\n(body needs more iron than usual)',
     'Pregnancy (foetus needs iron for its own haemoglobin — mother must supply). Rapid growth (infancy, adolescence). Erythropoietic demand (haemolysis, polycythaemia vera treated with venesection).',
     'All pregnant women. Adolescent girls with growth spurts. Premature infants.',
     'FBC every trimester in pregnancy. Routine iron supplementation in pregnancy (ferrous sulfate 200mg daily in UK).'],
    ['Increased loss\n(losing blood = losing iron)',
     'MENSTRUATION: The most common cause in women of childbearing age. Menorrhagia (heavy periods >80ml/cycle = loss of ~40mg iron/cycle). GI BLEEDING: Most common cause in adult men and post-menopausal women — peptic ulcer, oesophageal varices, colorectal cancer, angiodysplasia, NSAID-induced gastropathy. DONATION: Regular blood donors. HAEMATURIA: Rarely significant enough. PARASITIC INFECTION: Hookworm (Ancylostoma, Necator) is the most common cause of IDA globally — the worm attaches to intestinal wall and ingests blood daily.',
     'Women: menstrual history, fibroid symptoms. Men and post-menopausal women: ALWAYS investigate GI tract. Immigrant/traveller from tropical endemic area: stool ova and parasites.',
     'Menstrual history (PBAC score). OGD + colonoscopy in adult men and post-menopausal women with IDA — this is a MUST. Stool occult blood test (FIT — faecal immunochemical test). CT colonography if colonoscopy not tolerated.'],
]
story.append(plain_table(ida_causes, [CW*0.14, CW*0.28, CW*0.26, CW*0.32]))

story.append(Spacer(1,6))
story.append(bp('<b>Stages of Iron Deficiency</b> (from earliest to anaemia — this is how IDA develops progressively):'))
ida_stages = [
    ['Stage', 'What is happening', 'Lab findings', 'Symptoms'],
    ['Stage 1: Depleted iron stores\n(Pre-latent deficiency)', 'Iron stores (ferritin) begin to fall but blood count still normal. The body is drawing on reserves.', 'Ferritin LOW (often first abnormality). Serum iron and TIBC: normal. Hb: normal.', 'Usually none. Maybe fatigue.'],
    ['Stage 2: Iron-deficient erythropoiesis\n(Latent deficiency)', 'Stores exhausted. Not enough iron for normal RBC production. Transferrin saturation falls. Bone marrow produces smaller, paler cells.', 'Ferritin LOW. Serum iron LOW. TIBC HIGH. Transferrin saturation LOW (<15%). Hb still normal or borderline. MCV may be borderline.', 'Fatigue, reduced exercise tolerance. Possibly restless legs.'],
    ['Stage 3: Iron deficiency anaemia\n(Frank IDA)', 'Full anaemia develops. RBCs are visibly small and pale on blood film.', 'Hb LOW. MCV LOW (<80fL). MCH LOW. MCHC LOW. Ferritin very LOW (<12mcg/L). RDW HIGH (anisocytosis — uneven cell sizes as iron stores fluctuate).', 'Full symptom picture: fatigue, pallor, dyspnoea (breathlessness), palpitations, headache, poor concentration. Iron-specific symptoms: pica (craving to eat ice/clay/chalk/paper), koilonychia, angular stomatitis, glossitis, hair loss, restless legs.'],
]
story.append(plain_table(ida_stages, [CW*0.18, CW*0.28, CW*0.26, CW*0.28]))

story.append(Spacer(1,6))
story.append(bp('<b>IDA-specific clinical signs</b> — features unique to iron deficiency (not seen in other anaemias):'))
ida_signs = [
    ['Sign', 'What it looks like', 'Why it happens'],
    ['Koilonychia\n(spoon-shaped nails)', 'Nails become thin, brittle, and concave (spoon-shaped) — you could balance a drop of water in them. Look at fingernails from the side.', 'Severe iron deficiency affects nail keratin (the protein making up nails). Iron is needed for enzymes in keratin synthesis.'],
    ['Angular stomatitis\n(angular cheilitis)', 'Cracks and sores at the corners of the mouth. Painful, may bleed.', 'Iron deficiency impairs mucosal healing. Also associated with B12/folate deficiency.'],
    ['Glossitis', 'Tongue becomes smooth, shiny, and red (atrophic glossitis) — the normally rough surface (papillae) disappears. Painful, burning tongue.', 'Loss of tongue papillae (the small bumps on the surface) due to iron deficiency affecting the rapidly dividing mucosal cells.'],
    ['Pica\n(PIE-kah)', 'Compulsive craving to eat non-food substances: ice (pagophagia — most specific for IDA), clay (geophagia), chalk, paper, dirt. Also craving of specific foods (usually carbohydrate-rich).', 'The mechanism is unclear but pica resolves within days of iron supplementation. Ask about it — patients are often embarrassed to mention it.'],
    ['Dysphagia\n(Plummer-Vinson syndrome)', 'Difficulty swallowing due to post-cricoid web (a thin web of tissue in the throat) forming in severe long-standing IDA. Rare nowadays but classic exam question.', 'Iron deficiency damages mucosal lining, allowing webs to form. Important: Plummer-Vinson syndrome is associated with increased risk of post-cricoid carcinoma.'],
    ['Hair thinning / alopecia', 'Diffuse hair loss — often missed. Non-scarring (hair will regrow with treatment).', 'Hair follicles are highly metabolically active. Iron deficiency impairs follicle cycling.'],
    ['Restless legs syndrome\n(RLS)', 'Irresistible urge to move legs, especially at night. Uncomfortable creeping, crawling sensations. Relieved by movement.', 'Iron is needed for dopamine (a neurotransmitter) synthesis in the brain. Iron deficiency → dopamine dysfunction → RLS. IDA is the most common correctable cause of RLS.'],
]
story.append(plain_table(ida_signs, [CW*0.18, CW*0.38, CW*0.44]))
alert_box('IDA IN ADULT MEN OR POST-MENOPAUSAL WOMEN = INVESTIGATE THE GI TRACT. Colorectal cancer is the most important diagnosis NOT to miss. Refer urgently for OGD + colonoscopy. Do NOT just treat with iron and reassess — this delays a potentially curable cancer diagnosis. If IDA + upper GI symptoms: OGD first. If IDA + change in bowel habit: colonoscopy first. If both: both simultaneously.', story)
divider(story)

# ── SECTION 6: ANAEMIA OF CHRONIC DISEASE (ACD) ───────────────────────────────
sec_header('Section 6: Anaemia of Chronic Disease (ACD) — Inflammation Locking Away Iron', story)
professor_says('Anaemia of chronic disease is one of the most misunderstood conditions in medicine. The body actually HAS enough iron — it is just locked away and cannot be used. The villain is hepcidin, which is produced in large amounts in response to inflammation. The body does this as a defence mechanism — bacteria and cancer cells need iron to grow, so the body tries to "hide" the iron from them. The side effect is anaemia.', story)

story.append(bp('ACD (also called anaemia of inflammation) is the <b>second most common cause of anaemia worldwide</b>, '
    'after IDA. It is seen in any chronic inflammatory, infectious, or malignant condition. '
    'The key message: <b>the bone marrow is functional and iron stores are ADEQUATE — '
    'the problem is that inflammation (via hepcidin) prevents iron from being used.</b>'))
story.append(Spacer(1,4))

acd_table = [
    ['Aspect', 'Detail'],
    ['Causes', 'Rheumatoid arthritis (RA), SLE (systemic lupus erythematosus), IBD (inflammatory bowel disease — Crohn\'s, ulcerative colitis), chronic infections (TB, HIV, osteomyelitis, bacterial endocarditis), malignancy (any cancer), CKD (chronic kidney disease — also has EPO deficiency component), heart failure, COPD, obesity.'],
    ['Mechanism', '1. Inflammation (via IL-6 — interleukin 6, a signalling protein) → stimulates liver to make more HEPCIDIN. 2. Hepcidin degrades ferroportin on gut enterocytes and macrophages. 3. Iron is trapped inside macrophages and cannot enter the bloodstream. 4. Less iron reaches the bone marrow. 5. RBC production falls → anaemia. ALSO: inflammatory cytokines directly suppress EPO production and shorten RBC lifespan.'],
    ['Blood picture', 'Usually NORMOCYTIC (normal MCV) — but can be mildly MICROCYTIC. Hb usually 8-10 g/dL (mild-moderate anaemia — rarely severe). Reticulocyte count: LOW/NORMAL (marrow not responding fully despite low Hb). WBC and platelets often raised (due to underlying inflammation).'],
    ['Lab findings', 'Ferritin: NORMAL or HIGH (iron stores are present — ferritin is also an acute phase reactant, so it rises with inflammation). Serum iron: LOW (iron cannot escape from stores). TIBC/Transferrin: LOW (in contrast to IDA where TIBC is raised — this is the KEY distinguishing feature). Transferrin saturation: LOW. CRP/ESR: HIGH (markers of inflammation — will be raised in ACD).'],
    ['KEY DIFFERENCE from IDA', 'In IDA: Low ferritin + HIGH TIBC + Low serum iron. In ACD: NORMAL/HIGH ferritin + LOW TIBC + Low serum iron. When both ACD and IDA coexist (very common in IBD, renal failure, malignancy): ferritin may be misleadingly normal (inflammation falsely normalises it) — check soluble transferrin receptor (sTfR — raised in IDA, normal in ACD) or sTfR:log ferritin ratio (>2 suggests concurrent IDA).'],
    ['Treatment', 'TREAT THE UNDERLYING DISEASE first (immunosuppression for RA, antibiotics for infection, chemotherapy for cancer). Iron supplements do NOT help (iron stores are adequate). IV iron (ferric carboxymaltose or iron sucrose) may be used cautiously in specific settings (pre-operative optimisation, IBD, CKD — where IV iron can bypass the hepcidin block). EPO (erythropoietin injections) for CKD-related ACD. Blood transfusion only if symptomatic and Hb <8 g/dL.'],
]
story.append(plain_table(acd_table, [CW*0.18, CW*0.82]))
memory_hook('ACD vs IDA CHEAT: In IDA the TIBC goes UP (body desperately makes more transferrin carriers when iron is scarce). In ACD the TIBC goes DOWN (inflammation reduces transferrin production). Ferritin is LOW in IDA, NORMAL or HIGH in ACD. Think: "In IDA the body HUNGERS for iron — more carriers, empty stores. In ACD the body HIDES the iron — full stores, less transport."', story)
divider(story)

# ── SECTION 7: MEGALOBLASTIC ANAEMIA — B12 AND FOLATE ─────────────────────────
sec_header('Section 7: Megaloblastic Anaemia — B12 and Folate Deficiency', story)
professor_says('B12 and folate are like the instruction manual for building red blood cells. The bone marrow can gather all the iron and protein it needs, but without B12 and folate, it cannot read the blueprint to divide the cells correctly. So the cells grow big but cannot divide properly — they become enlarged (macro = big, cytic = cell) and abnormal. This is megaloblastic anaemia.', story)

story.append(bp('<b>The common pathway:</b> Both B12 and folate are required for the synthesis of thymidine '
    '(one of the four DNA building blocks — imagine thymidine as the T piece in the DNA jigsaw). '
    'Without thymidine, DNA cannot be replicated. '
    'The cells cannot divide properly. '
    'Cell bodies grow bigger (RNA and protein synthesis continue) but the nucleus cannot duplicate. '
    'The result: MEGALOBLASTS — large immature cells with a large nucleus that looks young '
    'despite the cell body being mature. '
    'This is called <b>nuclear:cytoplasmic asynchrony</b> (nucleus looks younger than the cell body).'))
story.append(Spacer(1,6))

b12_vs_folate = [
    ['Feature', 'Vitamin B12 (Cobalamin)', 'Folate (Folic Acid, Vitamin B9)'],
    ['Source',
     'ANIMAL PRODUCTS ONLY: meat, fish, eggs, dairy. Absent from plants. Vegans must supplement. ONLY synthesised by bacteria, not by animals or plants.',
     'GREEN LEAFY VEGETABLES (folate = from the Latin "folium" = leaf): spinach, broccoli, asparagus. Also: nuts, legumes, fortified cereals, citrus fruit. Destroyed by overcooking.'],
    ['Absorption',
     'Complex process: dietary B12 is released from food by gastric acid and pepsin. Then INTRINSIC FACTOR (IF — a glycoprotein made ONLY by gastric parietal cells in the stomach fundus and body) binds B12. The B12-IF complex is absorbed ONLY in the TERMINAL ILEUM (last section of small intestine) via specific receptors.',
     'Absorbed in the PROXIMAL JEJUNUM (first section of small intestine, just after the duodenum) by a simple transport mechanism. No special binding protein needed.'],
    ['Body stores',
     '3-5 YEARS\' worth stored in the liver. Therefore, deficiency takes YEARS to develop (e.g. after gastrectomy, deficiency appears 3-5 years later; in vegans, takes years of no supplementation).',
     'Only 3-4 MONTHS\' worth in body. Deficiency develops MUCH FASTER — within months of poor diet or increased demand.'],
    ['Function',
     'Required for: (1) DNA synthesis — via thymidylate synthase pathway. (2) MYELIN SYNTHESIS — the fatty sheath wrapping nerve fibres. B12 is essential for converting homocysteine to methionine (the methyl trap — without B12, folate cannot be "recycled" from methyltetrahydrofolate). (3) Normal neurological function.',
     'Required for: (1) DNA synthesis — same thymidylate pathway as B12. (2) Amino acid metabolism. (3) Neural tube formation in the foetus — hence folate supplementation (400mcg daily) BEFORE conception and for the first 12 weeks of pregnancy prevents neural tube defects (spina bifida, anencephaly).'],
    ['Deficiency causes',
     'PERNICIOUS ANAEMIA (most common in UK — autoimmune destruction of parietal cells or antibodies against intrinsic factor itself — so no IF = no B12 absorption). Veganism/vegetarianism without B12 supplementation. Gastrectomy (removes IF-producing cells). Terminal ileal disease or resection (Crohn\'s disease, surgical resection). Bacterial overgrowth (bacteria consume B12 in the gut before absorption). Fish tapeworm (Diphyllobothrium latum — consumes B12). Metformin (reduces B12 absorption by 30% — check B12 annually in long-term metformin users). Nitrous oxide (N2O — "laughing gas" — inactivates B12 by oxidising cobalt, causing acute megaloblastic crisis; recreational N2O abuse is an emerging cause of subacute combined degeneration of the spinal cord).',
     'Poor diet (commonest cause worldwide): elderly living alone, alcohol dependency (poor diet + impaired folate metabolism), poverty. INCREASED DEMAND: pregnancy (foetal neural tube formation), haemolytic anaemia (increased RBC turnover demands more folate), malignancy. MALABSORPTION: coeliac disease (proximal jejunal damage). DRUGS: Methotrexate (blocks dihydrofolate reductase — the enzyme that activates folate). Phenytoin (anti-epileptic — impairs absorption). Trimethoprim (antibiotic — also blocks dihydrofolate reductase — this is why co-trimoxazole causes megaloblastosis). Pyrimethamine (anti-malarial). Alcohol (impairs absorption + metabolism + increases renal excretion).'],
    ['Clinical features',
     'ANAEMIA SYMPTOMS (fatigue, pallor, breathlessness, palpitations). NEUROLOGICAL: Subacute combined degeneration of the spinal cord (SACD) — the most serious feature, not seen in folate deficiency alone: posterior column damage (loss of proprioception/vibration sense — patient cannot feel where their feet are → ataxia — unsteady gait) + lateral corticospinal tract damage (upper motor neurone signs — spasticity, hyperreflexia). Also: peripheral neuropathy (tingling, numbness in hands and feet), memory impairment, psychiatric symptoms ("megaloblastic madness" — depression, psychosis). Glossitis, angular stomatitis, jaundice (mild — from ineffective erythropoiesis).',
     'ANAEMIA SYMPTOMS. NO neurological features (folate deficiency alone does NOT cause SACD or peripheral neuropathy). Glossitis, angular stomatitis. In pregnancy: if untreated, neural tube defects in the baby. Very important: GIVING FOLATE TO A B12-DEFICIENT PATIENT CAN MASK THE ANAEMIA BUT ALLOW THE NEUROLOGICAL DAMAGE TO CONTINUE — always check B12 BEFORE starting folate.'],
    ['Blood and lab findings',
     'HIGH MCV (>100 fL) — macrocytic anaemia. Low reticulocyte count (hypoproliferative — marrow cannot make cells). Hypersegmented neutrophils on blood film (neutrophils with 5+ lobes — nuclear hypersegmentation is pathognomonic of megaloblastic anaemia). Serum B12: LOW (<150 ng/L = deficient; 150-200 = borderline). Elevated homocysteine (raised in both B12 and folate deficiency). Elevated methylmalonic acid (MMA — raised ONLY in B12 deficiency, not folate — useful distinguisher). Anti-parietal cell antibodies (90% of PA) and anti-intrinsic factor antibodies (50% of PA — more specific).',
     'HIGH MCV. Low reticulocyte count. Hypersegmented neutrophils. RBC folate (most reliable): LOW (<150 mcg/L). Serum folate: also checked but can be transiently low with poor diet. Homocysteine: elevated. MMA: NORMAL (this distinguishes folate deficiency from B12 deficiency — MMA only rises in B12 deficiency because it needs B12 to be metabolised).'],
    ['Treatment',
     'IM (intramuscular) Hydroxocobalamin 1mg every other day x 6 doses (loading), then 1mg every 3 months for life (maintenance — lifelong because the CAUSE is rarely correctable in pernicious anaemia). Oral B12 (1000mcg daily) works if cause is dietary (veganism) — high-dose oral can overcome the lack of IF by passive absorption. NEVER give folate alone until B12 has been checked and treated if deficient.',
     'Folic acid 5mg daily orally for 4 months (treat and correct stores). Ongoing supplementation if cause is not correctable. PREVENTION: 400mcg folic acid daily for all women planning pregnancy. 5mg daily for high-risk groups (previous NTD baby, sickle cell, thalassaemia, coeliac, on antiepileptics).'],
]
story.append(plain_table(b12_vs_folate, [CW*0.14, CW*0.43, CW*0.43]))
alert_box('CRITICAL RULE: ALWAYS check BOTH B12 AND folate before starting either supplement. Giving folate to a B12-deficient patient corrects the anaemia (removing the diagnostic clue) but the neurological damage (SACD) continues undetected and progresses — potentially causing irreversible paraplegia and sensory loss. Check B12 first. ALWAYS.', story)
image_search_box('Megaloblastic anaemia blood film', 'Google Images: hypersegmented neutrophils blood film / macrocytic anaemia peripheral smear / pernicious anaemia megaloblast', story)
divider(story)

# ── SECTION 8: HAEMOLYTIC ANAEMIAS ────────────────────────────────────────────
sec_header('Section 8: Haemolytic Anaemias — When Red Cells Die Too Soon', story)
professor_says('Haemolytic anaemia is like losing your delivery vans to a traffic accident — not because you cannot make them (the factory is working fine, in fact it is in overdrive) but because they are being destroyed before completing their route. The bone marrow compensates by producing young cells frantically — hence the raised reticulocyte count. The hallmarks are: anaemia + raised bilirubin (jaundice) + raised LDH + raised reticulocytes.', story)

story.append(bp('<b>Common haemolysis markers</b> (these distinguish haemolytic anaemia from other causes):'))
haem_markers = [
    ['Marker', 'Normal', 'In haemolysis', 'Why'],
    ['Reticulocyte count', '0.5-2.5%', 'RAISED (>3-5%)', 'Bone marrow compensating — producing young cells faster'],
    ['Unconjugated bilirubin', '<17 mcmol/L', 'RAISED (jaundice if >34)', 'Haem from destroyed RBCs → bilirubin faster than liver can conjugate it. Pre-hepatic jaundice = unconjugated hyperbilirubinaemia.'],
    ['LDH (Lactate Dehydrogenase)', '< 250 U/L', 'RAISED', 'LDH leaks from RBCs when they are destroyed. A general marker of cell breakdown.'],
    ['Haptoglobin', '0.3-2.0 g/L', 'LOW (often undetectable)', 'Haptoglobin binds free haemoglobin in plasma and the complex is cleared by the liver. In haemolysis, free Hb overwhelms haptoglobin → it gets consumed and disappears.'],
    ['Blood film', 'Normal RBCs', 'Abnormal shapes', 'Spherocytes (hereditary spherocytosis, AIHA), elliptocytes (HE), sickle cells, target cells, schistocytes (fragmented cells = microangiopathic haemolysis), Heinz bodies (G6PD after oxidative stress)'],
    ['Urinary haemosiderin', 'Absent', 'Present (intravascular only)', 'Free Hb in plasma is filtered by kidney → some iron deposits in renal tubular cells → appear in urine as haemosiderin. Indicates intravascular haemolysis specifically.'],
    ['Coombs test (DAT — Direct Antiglobulin Test)', 'Negative', 'POSITIVE in immune haemolysis', 'Detects antibody (IgG) or complement (C3) coating the surface of RBCs. A positive DAT = autoimmune or alloimmune (transfusion reaction) haemolysis.'],
]
story.append(plain_table(haem_markers, [CW*0.20, CW*0.14, CW*0.14, CW*0.52]))

story.append(Spacer(1,6))
story.append(haem_img)
story.append(Spacer(1,4))
story.append(bp('<i>Figure 4: Intravascular (inside blood vessels) vs extravascular (in spleen/liver) haemolysis. '
    'The pattern of lab markers differs between the two types, helping identify the cause.</i>', sImg))

story.append(Spacer(1,6))
story.append(bp('<b>Major causes of haemolytic anaemia:</b>'))

haem_causes = [
    ['Condition', 'Mechanism', 'Clinical features', 'Diagnosis', 'Treatment'],
    ['Autoimmune Haemolytic Anaemia\n(AIHA) — Warm type',
     'IgG antibodies coat RBCs at 37 degrees C (body temperature). Splenic macrophages recognise the antibody-coated cells and engulf them = extravascular haemolysis.',
     'Insidious anaemia, jaundice, splenomegaly. Associated conditions: SLE, CLL (chronic lymphocytic leukaemia), drugs (methyldopa, penicillin, cephalosporins), lymphoma.',
     'POSITIVE DAT (Coombs) for IgG +/- C3. Blood film: spherocytes (RBCs lose membrane as macrophages nibble at them, becoming spherical). Raised unconjugated bilirubin, raised LDH, low haptoglobin.',
     'STEROIDS (prednisolone 1mg/kg/day) — first line (suppresses antibody production and macrophage function). Rituximab (anti-CD20 monoclonal antibody) for steroid-refractory cases. Splenectomy for chronic relapsing cases. Folic acid supplementation (increased RBC turnover demands more folate).'],
    ['Autoimmune Haemolytic Anaemia\n(AIHA) — Cold type\n(Cold Agglutinin Disease)',
     'IgM antibodies bind RBCs at temperatures below 37 degrees C (cold temperatures — extremities, ears, nose). Complement is activated on the RBC surface — intravascular haemolysis AND extravascular (liver macrophages).',
     'Acrocyanosis (blue discolouration of fingers, toes, ears in cold). Raynaud\'s phenomenon. Haemoglobinuria (red urine in cold weather). Associated with Mycoplasma pneumoniae infection (causes a transient cold AIHA — self-limiting) and EBV infection. Also lymphoma.',
     'POSITIVE DAT for C3 only (not IgG, because IgM dissociates at 37C but has already fixed complement). Blood film: red cell agglutination (clumping). Cold agglutinin titre: raised. Thermal amplitude testing.',
     'KEEP WARM (avoid cold exposure — literally wearing gloves, warm clothing). Treat underlying cause (Mycoplasma: azithromycin; lymphoma: chemotherapy). Rituximab for chronic CAD. Steroids less effective than in warm AIHA. Blood transfusion via blood warmer if required.'],
    ['Hereditary Spherocytosis (HS)',
     'Autosomal dominant (usually) mutation in red cell membrane proteins (spectrin, ankyrin, band 3 protein). The cytoskeleton (the scaffolding inside the RBC membrane) is defective. The cell loses its biconcave shape and becomes spherical. Spheres are less deformable — trapped and destroyed by the spleen.',
     'Most common inherited haemolytic anaemia in Northern Europeans. Presents in childhood or adulthood with: anaemia (variable severity), jaundice, splenomegaly, GALLSTONES (from chronic elevated bilirubin → pigment gallstones). Aplastic crisis precipitated by Parvovirus B19 infection (the virus infects erythroid progenitors, temporarily stopping RBC production — the patient, who is already compensating, becomes severely anaemic).',
     'Blood film: SPHEROCYTES (small, dense, round cells lacking central pallor — unlike normal biconcave disc). High MCHC (>360 g/L — most specific lab finding for HS). Positive osmotic fragility test. EMA (eosin-5-maleimide) binding test on flow cytometry — gold standard. Family history.',
     'Folic acid 5mg daily (lifelong — increased turnover). SPLENECTOMY for moderate-severe HS (resolves haemolysis as the spleen is the site of destruction). VACCINATIONS before splenectomy: pneumococcal, meningococcal, Hib — protect against encapsulated bacteria (asplenia = high risk of overwhelming post-splenectomy infection). Transfusion in aplastic crisis.'],
    ['G6PD Deficiency\n(Glucose-6-phosphate dehydrogenase)',
     'X-linked recessive mutation (affects mostly males). G6PD enzyme protects RBCs from oxidative stress by maintaining NADPH and glutathione levels. Without G6PD, oxidative damage unfolds — haemoglobin oxidises → Heinz bodies (denatured Hb clumps) form → cells destroyed in spleen and blood vessels.',
     'EPISODIC (not chronic) haemolysis triggered by: DRUGS (primaquine, dapsone, nitrofurantoin, rasburicase), INFECTIONS (any), FOODS (fava beans — Italian name "favism"), METABOLIC STRESS (diabetic ketoacidosis). Between episodes: COMPLETELY NORMAL blood count. Common in sub-Saharan Africa, Mediterranean, Middle East, South Asia — where it provides partial protection against Plasmodium falciparum malaria.',
     'During crisis: anaemia, jaundice, haemoglobinuria (dark urine). Blood film: HEINZ BODIES on supravital stain (cresyl blue) — denatured Hb inclusions. Bite cells (Heinz body bitten off by splenic macrophage). G6PD enzyme assay: LOW activity. IMPORTANT: assay may be FALSELY NORMAL during a haemolytic crisis (because old G6PD-deficient cells are being destroyed, leaving only younger cells with higher enzyme activity — wait 3 months to retest after crisis).',
     'AVOIDANCE of triggers (provide a list of drugs to avoid). No specific treatment during crisis — supportive. Blood transfusion if severe. Folic acid. IMPORTANT: check G6PD before prescribing oxidative drugs — rasburicase (for tumour lysis syndrome treatment) is absolutely contraindicated in G6PD deficiency.'],
    ['Sickle Cell Disease\n(SCD)',
     'Autosomal recessive. A single amino acid mutation in the beta-globin gene (glutamate replaced by valine at position 6). This produces HbS instead of HbA. Under low oxygen, HbS polymerises → RBCs become rigid sickle-shaped. Sickle cells: occlude small blood vessels (vaso-occlusion → pain crises, organ infarction) and are destroyed prematurely (haemolytic anaemia).',
     'HAEMOLYTIC ANAEMIA: chronic anaemia (Hb 60-90 g/L typically — but well-tolerated as HbS releases O2 more readily than HbA). VASO-OCCLUSIVE CRISES: painful bone crises (commonest — agonising pain in long bones from infarction). Acute chest syndrome (lung infarction/pneumonia = major cause of death — fever, chest pain, respiratory compromise, new infiltrate on CXR). Stroke (cerebrovascular infarction in children — transcranial Doppler screening recommended). Splenic sequestration (sudden massive splenomegaly — acute fall in Hb — in young children). Priapism (painful persistent erection — urological emergency). Dactylitis (painful swelling of hands/feet in infants — first presentation). Avascular necrosis of hips/shoulders. Chronic organ damage: renal failure, retinopathy, leg ulcers.',
     'Hb electrophoresis or HPLC (High-Performance Liquid Chromatography): shows HbS predominant, absent HbA (in SCD homozygous). Sickle solubility test (Sickledex) — screening only, confirms HbS present. Newborn screening (heel prick Guthrie test in UK detects HbSS, HbSC, HbS-thalassaemia).',
     'CHRONIC: Hydroxycarbamide (hydroxyurea) — increases HbF (foetal haemoglobin — does not sickle) production → reduces crisis frequency by 50%. Folic acid 5mg daily. Penicillin V prophylaxis lifelong (asplenic — functional hyposplenism from repeated infarction). Vaccinations (as for splenectomy). PAIN CRISIS: analgesia (WHO ladder — paracetamol, NSAID, opioids; morphine PCA for severe crises), IV fluids (hydration reduces sickling), O2 (target SpO2 >94%), warmth, rest. ACUTE CHEST: O2, antibiotics (cephalosporin + macrolide), exchange transfusion (replaces HbS with HbA). TRANSFUSION: only for Hb <50 g/L, acute chest, stroke, or pre-operatively. CURATIVE: stem cell/bone marrow transplantation (available for selected cases, especially children with severe disease and matched sibling donor).'],
    ['Thalassaemia',
     'Autosomal recessive disorders of globin chain synthesis. ALPHA-THALASSAEMIA: reduced alpha chain production (due to gene deletions on chromosome 16). BETA-THALASSAEMIA: reduced beta chain production (due to mutations on chromosome 11). Imbalanced chain production → excess chains precipitate → damage RBCs → haemolysis.',
     'ALPHA-THAL: 1 gene deleted = silent carrier. 2 deleted = alpha-thal trait (mild microcytosis, no anaemia). 3 deleted = HbH disease (moderate haemolytic anaemia). 4 deleted = Hb Barts (hydrops fetalis — incompatible with life, stillborn or neonatal death). BETA-THAL TRAIT (heterozygous): MICROCYTOSIS with LOW NORMAL Hb — clinically silent. Often confused with IDA — KEY DIFFERENCE: in beta-thal trait, RDW is NORMAL (cells uniformly small) and ferritin is normal. BETA-THAL MAJOR (homozygous): severe anaemia presents within first year of life. Hepatosplenomegaly (extramedullary haematopoiesis). Bone deformity (frontal bossing — prominent forehead, maxillary prominence, chipmunk facies — from marrow expansion into bones). Growth retardation. Iron overload from transfusions.',
     'Hb electrophoresis / HPLC: beta-thal trait shows raised HbA2 (>3.5%) — pathognomonic. HbH: fast-moving band. Blood film: target cells, microcytosis, hypochromia. DNA analysis for alpha-thal. Ferritin: NORMAL (distinguishes from IDA — see below).',
     'BETA-THAL TRAIT: No treatment — genetic counselling. BETA-THAL MAJOR: Regular blood transfusions every 3-4 weeks (target Hb >100 g/L to suppress abnormal bone marrow erythropoiesis). IRON CHELATION: desferrioxamine (subcutaneous infusion overnight), deferasirox (oral), deferiprone (oral) — to prevent iron overload from transfusions (hepatic and cardiac iron overload is the leading cause of death in thalassaemia major). CURATIVE: bone marrow transplantation. SPLENECTOMY for hypersplenism.'],
]
story.append(plain_table(haem_causes, [CW*0.13, CW*0.19, CW*0.23, CW*0.20, CW*0.25]))
memory_hook('HAEMOLYTIC ANAEMIA TRIAD: Anaemia + Jaundice (raised unconjugated bilirubin) + Splenomegaly. Add: raised reticulocytes + raised LDH + low haptoglobin. For the blood film: Spherocytes = HS or warm AIHA. Sickle cells = SCD. Target cells = thalassaemia/liver disease. Schistocytes (fragments) = microangiopathic (TTP, HUS, DIC). Heinz bodies = G6PD. Bite cells = G6PD.', story)
divider(story)

# ── SECTION 9: APLASTIC ANAEMIA AND MDS ───────────────────────────────────────
sec_header('Section 9: Aplastic Anaemia and Myelodysplastic Syndrome (MDS)', story)
professor_says('Aplastic anaemia is total bone marrow failure — like a factory that has burned down. No workers, no production. Not just red cells, but ALL blood cell lines fail simultaneously: RBCs (anaemia), white cells (neutropaenia → infection), and platelets (thrombocytopaenia → bleeding). This is a medical emergency with high mortality without treatment.', story)

aplastic_data = [
    ['Aspect', 'Aplastic Anaemia', 'Myelodysplastic Syndrome (MDS)'],
    ['Definition', 'Destruction or failure of haematopoietic stem cells → hypocellular (empty) bone marrow → pancytopaenia (low RBCs, WBCs, and platelets).', 'Clonal (derived from a single abnormal cell) disorder of haematopoietic stem cells. Cells are made but they are abnormal and die before release (ineffective haematopoiesis). Risk of transformation to acute myeloid leukaemia (AML).'],
    ['Causes', 'IDIOPATHIC (most common, 70%) — autoimmune T-cell attack on stem cells. DRUGS: Chloramphenicol (the classic drug — now rarely used), NSAIDs, sulfonamides, gold, carbimazole. RADIATION. VIRUSES: EBV, Hepatitis (hepatitis-associated aplastic anaemia). PAROXYSMAL NOCTURNAL HAEMOGLOBINURIA (PNH) — associated. CONGENITAL: Fanconi anaemia (chromosome fragility syndrome — associated with short stature, skeletal anomalies, cafe-au-lait spots, renal anomalies).', 'IDIOPATHIC (most common). SECONDARY: Prior chemotherapy or radiotherapy (treatment-related MDS). Benzene exposure. Smoking. Increasing age (median diagnosis: 70 years). Down syndrome.'],
    ['Blood count', 'PANCYTOPAENIA: ALL three cell lines low. Anaemia (normocytic usually), neutropaenia (<1.5 x10^9/L), thrombocytopaenia (<150 x10^9/L). Reticulocytes: very low (marrow not producing cells).', 'Cytopaenia (usually one or more cell lines low). Anaemia most common — macrocytic. Abnormal cells on film (dysplasia): hypogranular neutrophils, bilobed neutrophils (pseudo-Pelger-Huet), hyposegmented or ring sideroblasts (abnormal mitochondrial iron deposits around nucleus).'],
    ['Bone marrow biopsy', 'HYPOCELLULAR: mostly fat cells, very few haematopoietic cells. This is the KEY diagnostic finding.', 'HYPERCELLULAR or normocellular with DYSPLASTIC (abnormal-looking) cells. Ring sideroblasts on Perls stain (iron accumulates around nucleus in ring shape). Raised blast percentage (immature cells): >5% blasts = high-grade MDS, risk of AML.'],
    ['Severity (aplastic)', 'SEVERE: Neutrophils <0.5, platelets <20, reticulocytes <20 x10^9/L, plus hypocellular marrow. NON-SEVERE: Does not meet above criteria.', 'WHO MDS subtypes: MDS with single lineage dysplasia (MDS-SLD), MDS with ring sideroblasts (MDS-RS), MDS with excess blasts (MDS-EB1: 5-9% blasts, MDS-EB2: 10-19% blasts — high AML transformation risk).'],
    ['Treatment', 'SEVERE: Bone marrow transplant (BMT) — curative, preferred in younger patients with matched sibling donor. Immunosuppression (antithymocyte globulin ATG + ciclosporin + eltrombopag) — for patients not eligible for BMT or awaiting donor. SUPPORTIVE: Red cell and platelet transfusions, G-CSF (granulocyte colony-stimulating factor — stimulates neutrophil production), infection prophylaxis (broad-spectrum antibiotics, antifungals).', 'SUPPORTIVE (most MDS patients are elderly and cannot tolerate intensive treatment): Red cell transfusions + iron chelation (if transfusion-dependent — to prevent iron overload). EPO injections if EPO level <200 IU/L. HYPOMETHYLATING AGENTS: Azacitidine (5-azacytidine) — for high-risk MDS, reduces AML transformation risk. LENALIDOMIDE — for MDS with chromosome 5q deletion (del[5q] — very responsive to lenalidomide). BMT: only for younger fit patients with high-risk MDS.'],
]
story.append(plain_table(aplastic_data, [CW*0.14, CW*0.43, CW*0.43]))
divider(story)

# ── SECTION 10: RENAL ANAEMIA & SPECIAL POPULATIONS ───────────────────────────
sec_header('Section 10: Anaemia in Special Populations — Renal, Pregnancy, Elderly', story)

special_table = [
    ['Population', 'Why anaemia occurs', 'Blood picture', 'Management'],
    ['Chronic Kidney Disease\n(CKD) — Renal Anaemia',
     'Kidneys produce EPO (erythropoietin). As kidneys fail (GFR falls below 30-45 ml/min), EPO production falls dramatically. Without EPO stimulus, bone marrow slows RBC production. ALSO: shortened RBC lifespan, iron deficiency (from blood loss with dialysis), folate loss in dialysis, aluminium toxicity, chronic inflammation (ACD component), uraemic toxins suppressing marrow.',
     'Normocytic, normochromic. Haematocrit (percentage of blood that is RBCs) falls proportionally with GFR. Reticulocyte count: low. Ferritin may be falsely elevated (inflammation).',
     'IV IRON (iron sucrose, ferric carboxymaltose) — target ferritin 200-500 mcg/L + transferrin saturation 20-40%. ERYTHROPOIESIS-STIMULATING AGENTS (ESAs): Darbepoetin alfa or epoetin alfa subcutaneously. Target Hb: 100-120 g/L (NOT higher — targeting >130 g/L increases cardiovascular events and stroke). Blood transfusions avoided if possible (sensitises to HLA antigens → makes kidney transplant harder). Correct B12/folate deficiency.'],
    ['Pregnancy',
     'PHYSIOLOGICAL (DILUTIONAL) ANAEMIA: Plasma volume expands by 40-50% but RBC mass only increases 20-30%. Therefore Hb falls physiologically to a nadir at 28-32 weeks. This is NORMAL and expected. TRUE ANAEMIA CAUSES IN PREGNANCY: Iron deficiency (increased demand: foetus, placenta, expanded blood volume — requires 1000mg extra iron), Folate deficiency (increased demand for foetal neural tube and cell division), B12 deficiency (vegan mother).',
     'Microcytic (IDA) or macrocytic (folate/B12). Physiological anaemia: normocytic. Hb <110 g/dL in first/third trimester or <105 g/dL in second trimester = treat.',
     'IRON: ferrous sulfate 200mg three times daily (replace stores). IV iron (ferric carboxymaltose) if oral not tolerated or late presentation. FOLATE: 5mg/day throughout pregnancy (high dose if risk factors). B12: supplement if deficient (oral or IM). Transfusion only if symptomatic or Hb <70 g/dL near term. Neonatal consequences of maternal IDA: low birth weight, preterm birth, iron deficiency in infant (breast milk low in iron).'],
    ['Elderly (>65 years)',
     'Multifactorial: IDA (GI blood loss — cancer, NSAIDs, peptic ulcer), ACD (multiple chronic diseases), CKD, B12 and folate deficiency (poor diet, malabsorption), myelodysplastic syndrome, marrow infiltration by lymphoma/myeloma/metastases, functional decline (reduced food intake, isolation). ANAEMIA OF UNEXPLAINED AETIOLOGY affects up to 30% of elderly — often multifactorial.',
     'Variable — depends on cause. MCV is the key first discriminator. Multiple causes may coexist (IDA + ACD + CKD = complex picture).',
     'Full investigation to identify cause — do NOT assume it is "just old age." Treat identified cause specifically. Oral iron for IDA. B12/folate supplementation. EPO for CKD. Blood transfusion threshold lower in elderly with cardiac disease (Hb <80 g/dL or symptomatic at higher Hb). Investigate actively for underlying malignancy.'],
    ['Children and Infants',
     'NEONATAL: Physiological anaemia of the newborn (nadir at 6-12 weeks — healthy term infant); haemolytic disease of the foetus and newborn (HDN — Rh or ABO incompatibility, maternal antibodies cross placenta and attack foetal RBCs). INFANTS: Iron deficiency is most common — breast milk is low in iron; introduce iron-rich weaning foods by 6 months. CHILDREN: IDA (rapid growth), haemoglobinopathies (SCD — presents in infancy with dactylitis or splenic sequestration), thalassaemia (presents in first year).',
     'MCV lower in children (normal range age-dependent). Reticulocytosis in haemolytic disease. Sickle cells, spherocytes on film.',
     'Iron supplements for IDA. Exchange transfusion for severe HDN. Newborn screening for haemoglobinopathies. Immunoglobulin (phototherapy/IVIG for HDN). Genetic counselling for inherited haemoglobinopathies.'],
]
story.append(plain_table(special_table, [CW*0.15, CW*0.30, CW*0.20, CW*0.35]))
divider(story)

# ── SECTION 11: CLINICAL RECOGNITION ──────────────────────────────────────────
sec_header('Section 11: Clinical Recognition — Symptoms, Signs, Examination', story)
professor_says('Anaemia has two sets of features: those caused by LOW OXYGEN DELIVERY to tissues (common to all anaemias), and features specific to the TYPE and CAUSE (e.g. koilonychia for iron deficiency, SACD for B12, jaundice for haemolysis). In PACES, examining a patient with anaemia means telling a complete story from hands to abdomen — the examiner wants to see you CONNECT the signs to the underlying cause.', story)

story.append(bp('<b>General features of anaemia</b> — present in any type, proportional to severity and speed of onset:'))
gen_features = [
    ['Feature', 'Mechanism', 'Clinical detail'],
    ['Fatigue and weakness', 'Reduced O2 delivery to muscles', 'The most universal symptom. Often gradual — patients adapt and underreport. Ask: "How far can you walk before getting breathless or tired? How does this compare to 6 months ago?"'],
    ['Pallor (paleness)', 'Less Hb = less red colour in blood near skin surface', 'Check: conjunctivae (inner lower eyelid — pull gently down, normal = pink-red, anaemic = white/pale). Palmar creases (in severe anaemia, creases lose their normal pink colour). Tongue and mucous membranes. Do NOT rely on skin colour alone (varies with ethnicity and melanin).'],
    ['Dyspnoea on exertion\n(breathlessness when active)', 'Reduced O2 delivery → muscles switch to anaerobic metabolism → lactic acid → respiratory drive stimulated + heart compensates by pumping faster', 'Usually exertional first. In severe anaemia, occurs at rest. Ask about climbing stairs, walking flat, dressing. Orthopnoea (breathlessness lying flat) suggests cardiac compromise.'],
    ['Palpitations and tachycardia', 'Heart pumps faster to maintain O2 delivery despite fewer RBCs (cardiac compensation)', 'Resting pulse >100 suggests Hb <80 g/L typically. In acute blood loss: tachycardia is early and prominent. Elderly patients with cardiac disease may decompensate earlier.'],
    ['Headache and dizziness', 'Brain sensitive to O2 deprivation; cerebral vasodilation as compensation', 'Postural dizziness (lightheadedness on standing) from relative hypotension when compensatory mechanisms cannot maintain cerebral perfusion.'],
    ['Angina (chest pain on exertion)', 'Myocardium (heart muscle) at risk of ischaemia when O2 delivery reduced — especially if coronary artery disease present', 'In a patient with pre-existing ischaemic heart disease, even mild anaemia (Hb 90-100 g/L) can precipitate angina. Anaemia is a precipitant of acute coronary syndrome — check Hb in any ACS presentation.'],
    ['Ankle oedema\n(fluid in ankles)', 'High-output cardiac failure: the heart pumping faster/harder for prolonged period → heart fails → fluid backs up', 'In chronic severe anaemia, the cardiac compensation (increased output) eventually causes high-output heart failure. Look for elevated JVP, ankle oedema, basal crackles.'],
    ['Tinnitus and visual disturbance', 'Inner ear and retinal O2 sensitivity', 'Ringing in ears, flashing lights (photopsia) in severe anaemia. Can mimic carotid artery disease or hypertensive retinopathy.'],
]
story.append(plain_table(gen_features, [CW*0.20, CW*0.28, CW*0.52]))

story.append(Spacer(1,6))
story.append(bp('<b>Systematic examination of the anaemic patient (PACES approach — hands to abdomen):</b>'))
exam_table = [
    ['Area', 'Look for', 'Interpretation'],
    ['HANDS\n(examine carefully — many clues here)',
     'Koilonychia (spoon nails), pallor of palmar creases and nail beds, angular stomatitis clue from nails (fragile cuticles), clubbing (IBD, malignancy, cirrhosis — causes of GI blood loss), leukonychia (white nails — hypoalbuminaemia of chronic disease), splinter haemorrhages (endocarditis causing haemolytic anaemia), palmar erythema (liver disease), asterixis (if hepatic encephalopathy), dupuytren\'s contracture (alcohol), tremor.',
     'Koilonychia = IDA. Pallor of creases at Hb <80. Clubbing = suspect GI cause or haematological malignancy. Leukonychia = chronic disease. Palmar erythema = liver disease (varices causing GI bleed, or cirrhosis causing ACD).'],
    ['FACE & MOUTH',
     'Scleral icterus (yellow tinge of whites of eyes — jaundice = unconjugated hyperbilirubinaemia in haemolysis). Conjunctival pallor (best place to assess). Glossitis (smooth beefy tongue). Angular stomatitis (cracks at corners). Frontal bossing (thalassaemia). Parotid enlargement (alcohol). Racial features (Mediterranean for thalassaemia, African/Caribbean for SCD).',
     'Jaundice in anaemia = haemolytic until proven otherwise. Glossitis and angular stomatitis = IDA, B12, or folate. Frontal bossing = beta-thal major (maxillary expansion from marrow hyperplasia).'],
    ['NECK',
     'Lymphadenopathy (enlarged lymph nodes — cervical, supraclavicular). Thyroid size and consistency. JVP height (raised in high-output failure from severe anaemia, or transfusion overload).',
     'Lymphadenopathy + anaemia = lymphoma, CLL, leukaemia, metastatic cancer. Goitre = hypothyroidism → macrocytic anaemia.'],
    ['CHEST',
     'Murmurs: a systolic ejection murmur is NORMAL in severe anaemia (high-output state creates a flow murmur). Signs of cardiac failure (raised JVP, S3 gallop, basal crackles). Kyphoscoliosis or rib abnormalities (thalassaemia, Fanconi).',
     'Flow murmur in severe anaemia ≠ valve disease. But consider: existing valve disease can be precipitated/worsened by anaemia. Cardiac failure signs in context of anaemia = high-output failure or fluid overload.'],
    ['ABDOMEN',
     'Splenomegaly (enlarged spleen): measure in cm below left costal margin (rib edge). Hepatomegaly (enlarged liver). Hepatosplenomegaly. Ascites. Masses (malignancy as cause of ACD or GI blood loss). Abdominal tenderness (IBD, malignancy). Stool colour if available (meleana = black tarry stool).',
     'Massive splenomegaly (>10cm below costal margin) = myelofibrosis, CML, malaria, visceral leishmaniasis, portal hypertension. Moderate splenomegaly = haemolytic anaemia (all types), CLL, lymphoma. Hepatosplenomegaly = haematological malignancy, liver disease, infiltration.'],
    ['NEUROLOGICAL (crucial for B12)',
     'Peripheral sensation (light touch, pinprick) — check feet symmetrically. Proprioception (joint position sense — hold toe, move up/down with eyes closed, patient reports direction). Vibration sense (128 Hz tuning fork on bony prominences). Romberg\'s test (standing with feet together, eyes closed — positive = falls when eyes closed = posterior column deficit). Power and reflexes (upper motor neurone signs: hyperreflexia, spasticity, upgoing plantar [Babinski sign]).',
     'B12 deficiency SACD: Loss of proprioception + vibration (posterior columns) PLUS hyperreflexia + upgoing plantar (corticospinal tracts). The reflexes may initially be ABSENT (peripheral neuropathy) then become brisk if central tracts also involved. Wide-based gait, positive Romberg, difficulty walking in the dark.'],
    ['PR EXAMINATION\n(per rectum)',
     'Digital rectal examination: prostatic enlargement (benign or malignant), rectal mass (carcinoma), presence of blood (fresh = lower GI bleed, dark = melaena from upper GI bleed).',
     'ESSENTIAL in any male with unexplained IDA. Any adult with rectal bleeding symptoms. A cancer found on PR exam when the patient only came in for "tiredness from anaemia" = caught at a potentially curable stage.'],
]
story.append(plain_table(exam_table, [CW*0.14, CW*0.38, CW*0.48]))
divider(story)

# ── SECTION 12: INVESTIGATIONS ────────────────────────────────────────────────
sec_header('Section 12: Investigations — Reading the Blood Tests', story)
professor_says('A full blood count (FBC) is the starting gun. It tells you the severity of the anaemia (Hb level), the type (MCV), and gives clues about the cause (reticulocyte count, platelet and white cell counts). The peripheral blood film is like looking through a microscope at the actual red cells — seeing their shape, size, and any abnormal cells. This is one of the most informative investigations in medicine.', story)

story.append(bp('<b>The peripheral blood film — what to look for:</b>'))
film_table = [
    ['Finding on film', 'What it means (plain English)', 'Associated conditions'],
    ['Microcytes\n(small cells)', 'RBCs smaller than a lymphocyte nucleus', 'IDA, thalassaemia, sideroblastic anaemia, ACD (sometimes)'],
    ['Macrocytes\n(large cells)', 'RBCs larger than a lymphocyte nucleus', 'B12/folate deficiency, alcohol, liver disease, hypothyroidism, MDS, reticulocytosis'],
    ['Hypochromic cells\n(pale cells, large central pallor)', 'Cells with more than 1/3 of their diameter as pale area — less haemoglobin inside', 'IDA, thalassaemia, sideroblastic anaemia'],
    ['Spherocytes\n(small dense round cells, no central pallor)', 'Abnormal spherical RBCs (lost their biconcave shape)', 'Hereditary spherocytosis, warm AIHA, severe burns, ABO incompatibility transfusion reaction'],
    ['Target cells\n(cells with a central dense spot surrounded by pale ring, then dense ring)', 'Like a bullseye or target. Extra membrane relative to volume.', 'Thalassaemia, haemoglobin C, liver disease, hyposplenism, iron deficiency'],
    ['Sickle cells\n(crescent/sickle shaped)', 'Distorted rigid sickle-shaped RBCs', 'Sickle cell disease (HbSS, HbSC, HbS-thal)'],
    ['Schistocytes / Helmet cells\n(fragmented cells)', 'Red cell fragments — pieces of cells shredded by fibrin strands or prosthetic surfaces', 'Microangiopathic haemolytic anaemia: TTP (thrombotic thrombocytopaenic purpura), HUS (haemolytic uraemic syndrome), DIC, prosthetic heart valves, malignant hypertension'],
    ['Heinz bodies\n(on special stain only)', 'Denatured haemoglobin precipitates inside the cell — appear as dark clumps on supravital stain (cresyl violet)', 'G6PD deficiency (during haemolytic crisis), HbH disease (alpha-thal)'],
    ['Howell-Jolly bodies\n(small dark nuclear remnants)', 'Small dense blue-black dots inside RBCs — remnant of nuclear material normally removed by spleen', 'Hyposplenism or asplenia (after splenectomy, functional asplenia in SCD, coeliac disease)'],
    ['Hypersegmented neutrophils\n(5+ nuclear lobes)', 'Neutrophils normally have 2-3 lobes. More than 5 lobes = hypersegmentation', 'Megaloblastic anaemia (B12 or folate deficiency) — PATHOGNOMONIC when combined with macrocytosis'],
    ['Rouleaux formation\n(red cells stacked like coins)', 'RBCs clump together in long stacks (like a pile of coins)', 'Elevated globulins: myeloma (paraprotein causes clumping), chronic inflammation, pregnancy'],
    ['Blast cells\n(primitive immature cells with large nucleus)', 'Large immature cells from bone marrow — not normally seen in blood', 'Acute leukaemia (medical emergency), MDS with excess blasts, myelofibrosis (leukoerythroblastic picture)'],
    ['Leukoerythroblastic picture\n(immature cells of all lines)', 'Both immature WBCs (myelocytes, metamyelocytes) AND immature RBCs (nucleated red cells) in peripheral blood', 'Bone marrow infiltration: myeloma, metastatic cancer, lymphoma, myelofibrosis, severe infection. Indicates marrow being displaced by abnormal tissue.'],
]
story.append(plain_table(film_table, [CW*0.22, CW*0.30, CW*0.48]))

story.append(Spacer(1,6))
story.append(bp('<b>Additional investigations for specific anaemia types:</b>'))
add_ix = [
    ['Investigation', 'What it tests', 'When to request', 'Key result'],
    ['Serum ferritin', 'Iron stores', 'All anaemia workup', 'Low (<12): IDA. High: iron overload, inflammation, malignancy. Must interpret with CRP (inflammation falsely raises ferritin).'],
    ['Serum iron + TIBC + transferrin saturation', 'Iron in transit + transport capacity', 'Microcytic anaemia, before IV iron', 'IDA: low iron, high TIBC, low saturation (<15%). ACD: low iron, low TIBC, low saturation. Overload: high iron, low TIBC, high saturation (>60%).'],
    ['Serum B12', 'B12 level', 'Macrocytic anaemia, neuropathy, elderly, vegans, metformin users', 'Low (<150 ng/L): deficiency. Borderline (150-200): check MMA/homocysteine to confirm.'],
    ['Serum/RBC folate', 'Folate level', 'Macrocytic anaemia, pregnancy planning, alcohol', 'Low: deficiency. Check alongside B12 always.'],
    ['Methylmalonic acid (MMA)', 'B12-dependent metabolic pathway', 'Distinguishing B12 from folate deficiency when B12 borderline', 'Raised in B12 deficiency only (not in folate deficiency). Gold standard for confirming functional B12 deficiency.'],
    ['Homocysteine', 'Raised in both B12 and folate deficiency', 'Borderline B12/folate', 'Raised in both deficiencies and also in cardiovascular disease (independent risk factor for CVD).'],
    ['Haemoglobin electrophoresis/HPLC', 'Identifies abnormal haemoglobin types (HbA, HbS, HbC, HbF, HbA2)', 'Suspicion of SCD or thalassaemia, family history, ethnic groups at risk', 'HbA2 >3.5% = beta-thal trait. HbSS = sickle cell disease. Elevated HbF = thalassaemia major, SCD on hydroxycarbamide.'],
    ['Direct Antiglobulin Test (DAT/Coombs)', 'Antibody or complement on RBC surface', 'Suspected immune haemolysis', 'Positive IgG: warm AIHA. Positive C3 only: cold AIHA. Positive = immune-mediated haemolysis.'],
    ['LDH + haptoglobin', 'General haemolysis markers', 'Any suspected haemolytic anaemia', 'LDH raised + haptoglobin very low = haemolysis confirmed. The lower the haptoglobin, the more haemolysis.'],
    ['Osmotic fragility test / EMA binding test', 'RBC membrane deformability', 'Suspected hereditary spherocytosis', 'Increased osmotic fragility = HS. EMA flow cytometry: gold standard.'],
    ['Reticulocyte count', 'Bone marrow RBC production rate', 'All anaemia workup', 'High: marrow responding (haemolysis, blood loss, treatment). Low: marrow not responding (aplasia, deficiency, infiltration, ACD).'],
    ['Bone marrow aspirate and trephine biopsy', 'Direct examination of bone marrow', 'Aplastic anaemia, MDS, leukaemia suspicion, unexplained pancytopaenia, marrow infiltration', 'Hypocellular = aplastic. Hypercellular with dysplasia = MDS. Blasts >20% = AML. Infiltration by cancer/lymphoma cells.'],
    ['Serum EPO level', 'EPO (erythropoietin) concentration', 'Anaemia with low reticulocyte count, suspected polycythaemia vera, before starting ESA therapy in CKD', 'Low EPO + anaemia = renal anaemia (start EPO treatment). HIGH EPO in polycythaemia vera (rare — usually suppressed).'],
]
story.append(plain_table(add_ix, [CW*0.20, CW*0.18, CW*0.22, CW*0.40]))
divider(story)

# ── SECTION 13: PHARMACOLOGY ───────────────────────────────────────────────────
sec_header('Section 13: Pharmacology — Treating Anaemia', story)
professor_says('Treating anaemia without knowing the cause is like topping up the oil in a car with a leak — it may help temporarily but it does not fix the underlying problem. ALWAYS find the cause first, then treat with the specific agent. Giving the wrong treatment can HARM: for example, giving iron to someone who already has iron overload (haemochromatosis) is dangerous; giving folate to a B12-deficient patient masks the anaemia but allows neurological damage to progress.', story)

pharm_table = [
    ['Drug/Agent', 'Class & Mechanism', 'Indication', 'Dose', 'Key points / Adverse effects'],
    ['Ferrous sulfate\n(FeSO4)',
     'Oral iron supplement. Ferrous (Fe2+) form — most bioavailable for absorption.',
     'Iron deficiency anaemia — FIRST LINE if gut absorbs normally. Replace stores after treating cause.',
     '200mg THREE TIMES DAILY (contains 65mg elemental iron per tablet). Take on empty stomach for maximum absorption. Reticulocyte response at 7-10 days; Hb rise 10-20 g/L per week. CONTINUE for 3 months after Hb normalises (to replenish stores). PREVENTION: 200mg daily in pregnancy.',
     'GI side effects (nausea, constipation, diarrhoea, abdominal pain) in up to 40% — most common reason for non-compliance. BLACK STOOLS (normal — warn patient). If intolerant: try ferrous fumarate (easier on stomach) or switch to IV iron. Take with VITAMIN C (orange juice) to improve absorption. AVOID WITH: antacids, PPIs, calcium supplements, tetracycline (all reduce absorption — take iron 2h apart).'],
    ['Ferric carboxymaltose\n(Ferinject)\nor Iron sucrose (Venofer)',
     'IV iron formulations. Ferric (Fe3+) iron complexed to a carbohydrate shell. Delivered directly into bloodstream, bypassing gut absorption.',
     'IDA when oral iron is not tolerated, not effective (malabsorption), or needs rapid correction (pre-operative, severe symptomatic IDA, IBD, CKD on dialysis, heart failure with IDA).',
     'Ferric carboxymaltose: 500-1000mg IV over 15 minutes (max single dose 1000mg). Can give total replacement dose in 1-2 visits. Iron sucrose: 200mg IV per session, more frequent visits needed.',
     'Infusion reactions: flushing, hypotension, arthralgia — usually mild. Risk of severe hypersensitivity reaction is low (<0.1%). Do NOT give to patients with active infection (iron feeds bacteria). Monitor ferritin to avoid overload. Contraindicated in haemochromatosis. PHOSPHATE MONITORING for ferric carboxymaltose (causes hypophosphataemia in up to 75% of cases — usually transient but can be severe, especially with repeated doses).'],
    ['Hydroxocobalamin\n(B12 injection)',
     'Vitamin B12. Converted to active coenzyme forms (methylcobalamin, adenosylcobalamin) in cells.',
     'B12 deficiency — ESPECIALLY when caused by pernicious anaemia or post-gastrectomy (i.e., the cause cannot be corrected). Also when neurological features are present (parenteral route achieves higher levels faster).',
     'LOADING: 1mg IM every other day for 6 doses (12 days total). MAINTENANCE: 1mg IM every 3 months for LIFE (in pernicious anaemia — the cause is permanent). ORAL B12: 1000mcg daily — suitable for dietary deficiency (veganism) where absorption is intact (passive absorption at high doses).',
     'IM injections — painless if given correctly. Anaphylaxis is rare. Do NOT use cyanocobalamin by injection in smokers (conversion impaired). Blood count response: reticulocyte peak at 5-7 days after starting treatment. Hb normalises over 6-8 weeks. Neurological improvement: months to years (partial if severe). HYPOKALEMIA RISK: Hb rising rapidly → potassium enters new cells → check K+ in first few days.'],
    ['Folic acid',
     'Synthetic form of vitamin B9 (folate). Converted to active tetrahydrofolate in cells — required for DNA synthesis.',
     'Folate deficiency. Prevention of neural tube defects (pre-conception and first trimester). Chronic haemolytic anaemias (SCD, HS, thalassaemia — increased RBC turnover demands folate). Patients on methotrexate (give folate to prevent toxicity — does not reduce methotrexate efficacy when given correctly).',
     'TREATMENT: 5mg daily orally for 4 months (replace stores). PREVENTION in pregnancy: 400mcg daily (low risk) or 5mg daily (high risk: previous NTD, epilepsy, diabetes, obesity, thalassaemia, SCD). HAEMOLYTIC ANAEMIA: 5mg daily ongoing. METHOTREXATE SUPPLEMENTATION: 5mg once weekly (24-48h after methotrexate dose).',
     'Cheap, safe, well-tolerated. IMPORTANT: ALWAYS check B12 BEFORE starting folic acid — if B12 is deficient, correcting folate anaemia while leaving B12 untreated allows neurological damage to progress undetected.'],
    ['Darbepoetin alfa\n(Aranesp)\nEpoetin alfa (Eprex)',
     'Erythropoiesis-Stimulating Agents (ESAs). Synthetic analogues of erythropoietin (EPO). Bind EPO receptor on erythroid progenitors in bone marrow → stimulate RBC production.',
     'Renal anaemia (CKD — where endogenous EPO production is insufficient). Anaemia of malignancy (reducing transfusion requirements in patients on chemotherapy). MDS (low EPO level subgroup).',
     'Darbepoetin alfa: 0.45 mcg/kg subcutaneously once weekly or 0.75 mcg/kg every 2 weeks (longer half-life than epoetin). TARGET Hb: 100-120 g/L — NOT higher. Adjust dose to maintain in target range. Ensure adequate iron stores FIRST (IV iron commonly co-prescribed).',
     'HYPERTENSION (ESAs raise blood viscosity — monitor BP closely). THROMBOSIS (DVT, stroke, PE — more common at higher Hb targets — do NOT target Hb >130 g/L). PURE RED CELL APLASIA (PRCA) — rare but serious: anti-EPO antibodies develop, destroying all erythroid progenitors — switches to severe transfusion-dependent anaemia. ENSURE: iron, B12, folate adequate before starting (otherwise ESA response will be poor).'],
    ['Prednisolone\n(steroids)',
     'Glucocorticoid immunosuppressant. Reduces antibody production by B-lymphocytes (reduces auto-antibody causing AIHA). Reduces splenic macrophage activity (reduces destruction of antibody-coated RBCs). Anti-inflammatory.',
     'Warm autoimmune haemolytic anaemia (AIHA) — FIRST LINE. Immune thrombocytopaenic purpura (ITP). Some aplastic anaemia protocols. Haemolytic disease management.',
     '1mg/kg/day prednisolone orally (typically 60-80mg/day) until Hb normalises, then taper slowly over months.',
     'Monitor blood glucose (steroid hyperglycaemia), blood pressure, weight, mood (steroid psychosis), bone density (osteoporosis with prolonged use — prescribe calcium + vitamin D). PPI cover (omeprazole 20mg daily — prevents peptic ulcer). Monitor for infection (immunosuppression). In 70-80% of warm AIHA: response within 2-3 weeks. Relapse on taper requires rituximab or splenectomy.'],
    ['Hydroxycarbamide\n(Hydroxyurea, HU)',
     'Ribonucleotide reductase inhibitor → reduces DNA synthesis in bone marrow → inhibits abnormal cell lines. In sickle cell: increases HbF (foetal haemoglobin production) — HbF does not sickle and dilutes HbS, reducing polymerisation.',
     'SICKLE CELL DISEASE: reduces vaso-occlusive crisis frequency by 50%, reduces acute chest syndrome, reduces transfusion requirements, reduces mortality. Also used in polycythaemia vera and essential thrombocythaemia.',
     'Start at 15mg/kg/day orally. Increase by 5mg/kg every 12 weeks if tolerated. Max dose usually 35mg/kg/day. Target: raised MCV (evidence of HbF induction), Hb stable.',
     'MYELOSUPPRESSION — monitor FBC regularly (every 4 weeks initially then 2-3 monthly). Reduce dose if neutrophils <2.0 or platelets <80 x10^9/L. Teratogenic — effective contraception essential. Skin hyperpigmentation, leg ulcers (at high doses). Annual reassessment with specialist.'],
    ['Blood transfusion\n(Red Cell Concentrate)',
     'Provides immediate Hb to restore oxygen-carrying capacity. Each unit of packed red cells raises Hb by approximately 10-15 g/L in a 70kg adult.',
     'SYMPTOMATIC anaemia not correctable by other means. Hb <70-80 g/L in most patients. Hb <80-100 g/L in cardiac/respiratory compromise. Pre-operative optimisation if surgery cannot be delayed. Acute haemorrhage, haemolytic crisis.',
     'Usual transfusion: 1-2 units, reassess. Transfuse to symptom relief, not a number. In chronic transfusion-dependent patients: monthly or as needed, with iron chelation.',
     'RISKS: transfusion reactions (ABO incompatibility = catastrophic haemolysis — ALWAYS check patient ID and blood label), TACO (transfusion-associated circulatory overload — fluid overload, especially elderly/cardiac patients — give furosemide 40mg IV with alternate units), TRALI (transfusion-related acute lung injury — rare, life-threatening), alloimmunisation (HLA antibodies — complicates future transfusions and transplantation), infection transmission (rare but not zero). Irradiate blood for immunocompromised patients. CMV-negative blood for CMV-negative transplant recipients.'],
]
story.append(plain_table(pharm_table, [CW*0.13, CW*0.17, CW*0.14, CW*0.16, CW*0.40]))
divider(story)

# ── SECTION 14: MRCP HIGH-YIELD TRIGGERS ──────────────────────────────────────
sec_header('Section 14: MRCP Exam — High-Yield Scenarios and Triggers', story)

mrcp_table = [
    ['Stem / Trigger', 'Diagnosis', 'What the examiner wants to hear'],
    ['40-year-old Asian woman, tired and breathless. FBC: Hb 98 g/L, MCV 68 fL, MCH 20. Ferritin 8 mcg/L. She is a vegetarian.',
     'Iron deficiency anaemia (IDA) — dietary cause',
     'CONFIRM with low ferritin + low MCV + low MCH. Treat with ferrous sulfate 200mg TDS. BUT also investigate for underlying blood loss — check menstrual history (menorrhagia?), stool tests. Dietary advice: increase iron-rich plant foods, take with vitamin C. Consider anti-TTG IgA to exclude coeliac.'],
    ['60-year-old man, IDA on bloods. No GI symptoms. Examiner asks: what is your most important next step?',
     'Colorectal cancer until proven otherwise',
     'OGD + colonoscopy urgently. IDA in adult man or post-menopausal woman = GI malignancy investigation MANDATORY. Do not just treat with iron. Refer via urgent 2-week-wait pathway.'],
    ['50-year-old woman, anaemia, tingling in hands and feet, unsteady gait. B12 = 95 ng/L. MCV 112 fL. Hypersegmented neutrophils on film.',
     'Pernicious anaemia with SACD (subacute combined degeneration of spinal cord)',
     'Macrocytic anaemia + B12 deficiency + neurological features = SACD = pernicious anaemia. Check anti-IF antibodies (specific for PA), anti-parietal cell antibodies (sensitive). GIVE B12 IM immediately. Folate is contraindicated until B12 treated. Gastroscopy to confirm atrophic gastritis. Check for other autoimmune diseases (hypothyroidism, type 1 diabetes, Addison\'s, vitiligo — PA clusters with these).'],
    ['45-year-old woman with RA (rheumatoid arthritis), Hb 100 g/L, MCV 82 fL, ferritin 180 mcg/L (normal), serum iron LOW, TIBC LOW.',
     'Anaemia of chronic disease (ACD)',
     'TIBC LOW (not raised as in IDA) + ferritin normal/high = ACD. Treat the underlying RA (DMARD optimisation). Oral iron will not help. Consider IV iron if absolute iron deficiency co-exists (check sTfR).'],
    ['Patient presents with haemolytic anaemia. DAT positive for IgG. On methyldopa for hypertension.',
     'Drug-induced warm AIHA',
     'Methyldopa is the classic drug causing positive DAT and haemolytic anaemia. Also: penicillin, cephalosporins, quinidine. STOP the offending drug. Steroids if severe. The DAT may remain positive for months after stopping the drug.'],
    ['25-year-old Nigerian man, crisis of severe pain in long bones and chest. O2 sats 90%, CXR shows new right lower lobe infiltrate. SpO2 falling.',
     'Sickle cell disease — ACUTE CHEST SYNDROME',
     'Acute chest syndrome = new lung infiltrate + fever + respiratory symptoms in SCD patient = MEDICAL EMERGENCY. Management: O2 (target SpO2 >95%), IV antibiotics (cephalosporin + macrolide — covers atypical organisms too), analgesia, hydration, EXCHANGE TRANSFUSION (replaces HbS with HbA — indicated in severe/deteriorating acute chest). High mortality — escalate early.'],
    ['35-year-old Mediterranean woman, microcytic anaemia, MCV 68. Ferritin: NORMAL. Anti-TTG: negative. No menorrhagia. Siblings also have microcytosis.',
     'Beta-thalassaemia trait',
     'KEY DISTINCTION from IDA: ferritin NORMAL, RDW NORMAL (uniform small cells), Hb ONLY mildly reduced (often Hb 100-115 g/L). FAMILY HISTORY of microcytosis. CONFIRM with Hb electrophoresis: HbA2 >3.5% is PATHOGNOMONIC of beta-thal trait. No treatment — genetic counselling. Partner screening important (if both beta-thal trait: 25% chance of beta-thal major in children).'],
    ['Child with recurrent jaundice and gallstones. High MCHC on FBC. Splenomegaly. Father had splenectomy in his 30s.',
     'Hereditary spherocytosis (HS)',
     'Autosomal dominant — father affected (splenectomy history). HIGH MCHC (most specific lab marker for HS — >360 g/L). SPHEROCYTES on blood film. CONFIRM with EMA binding test (flow cytometry). Splenectomy curative for moderate-severe HS but requires pre-splenectomy vaccinations. Monitor for Parvovirus B19 aplastic crisis.'],
    ['Elderly man with pancytopaenia (all cell lines low). Bone marrow biopsy: hypocellular, mostly fat cells.',
     'Aplastic anaemia',
     'PANCYTOPAENIA + HYPOCELLULAR MARROW = aplastic anaemia. Assess severity: SEVERE = neutrophils <0.5, platelets <20, reticulocytes <20. Check for PNH clone (Ham\'s test or flow cytometry — PNH associated with aplastic). TREATMENT for severe aplastic: BMT if young + matched sibling donor; ATG + ciclosporin + eltrombopag if not BMT candidate.'],
    ['70-year-old man. Anaemia with raised MCV. Blood film: hypersegmented neutrophils + oval macrocytes. Serum B12: 350 ng/L (normal). Folate: 3.2 (mildly low). But MMA is ELEVATED.',
     'Functional B12 deficiency despite normal serum B12',
     'Serum B12 can be NORMAL in functional deficiency. RAISED MMA = B12 pathway not working despite apparently adequate level. Occurs in: subclinical deficiency (stores depleting), autoimmune gastritis without classic PA. TREAT WITH B12 (IM hydroxocobalamin). The macrocytic anaemia here could also have a folate component — treat both after establishing B12 is being treated.'],
    ['Patient with severe IDA. Ferrous sulfate prescribed but after 3 months the Hb has not improved.',
     'Non-response to oral iron — find out why',
     'REASONS FOR NON-RESPONSE: (1) Non-compliance (most common — side effects, forgetting). (2) Ongoing blood loss exceeding replacement rate. (3) Malabsorption (coeliac — check anti-TTG IgA). (4) Wrong diagnosis (thalassaemia, ACD). (5) Wrong medication (ferric formulation instead of ferrous). (6) Drug interaction (calcium, PPIs, antacids taken at same time). ACTION: dietary review, compliance check, investigate GI tract further, switch to IV iron, check coeliac antibodies.'],
    ['PACES: Examine this patient\'s abdomen. Finding: massive splenomegaly (15cm below costal margin) + anaemia signs.',
     'Haematological cause: myelofibrosis, CML, chronic malaria, or visceral leishmaniasis (kala-azar)',
     'MASSIVE splenomegaly (>10cm) causes: myelofibrosis (marrow replaced by fibrosis → extramedullary haematopoiesis in spleen — leukoerythroblastic picture on film), CML (chronic myeloid leukaemia — high WBC with myeloid precursors), chronic malaria (tropical — ask travel history), kala-azar (visceral leishmaniasis — endemic tropics). MRCP: know all causes of massive splenomegaly. Moderate splenomegaly + haemolytic picture = haemolytic anaemia (all types).'],
]
story.append(plain_table(mrcp_table, [CW*0.28, CW*0.20, CW*0.52]))
divider(story)

# ── SECTION 15: MINIMAL RESOURCES + PACES ─────────────────────────────────────
sec_header('Section 15: Minimal Resources Protocol & PACES Examination Guide', story)

story.append(bp('<b>Managing anaemia with limited investigations — resource-limited settings:</b>'))
minimal = [
    ['Clinical situation', 'Available resources', 'What to do', 'When to refer'],
    ['Suspected IDA\n(fatigue + pallor + dietary history)',
     'Clinical exam + haemoglobin only',
     '1. Clinical signs: koilonychia, pallor of conjunctivae and creases, angular stomatitis, smooth tongue, restless legs history, pica. 2. Full menstrual/dietary history. 3. PR examination for occult blood. 4. If haemoglobin low + clinical signs consistent: treat as IDA with ferrous sulfate 200mg TDS for 3 months. 5. Monitor symptom response and pallor change in 4-6 weeks.',
     'Any adult male or post-menopausal woman with IDA. No response to treatment after 4-6 weeks. Pica or very severe symptoms. PR bleeding or melaena. Significant weight loss.'],
    ['Suspected B12 deficiency\n(macrocytic anaemia + neurological)',
     'Clinical exam only',
     '1. Neurological assessment: test proprioception (joint position sense of great toe), vibration sense (128Hz fork on medial malleolus), Romberg\'s test (stand eyes closed), gait observation. 2. Tongue: smooth atrophic glossitis. 3. Dietary history: vegan? 4. History: gastrectomy, bowel resection, metformin use, nitrous oxide. 5. Treat empirically with B12 IM if clinical picture compelling and B12 not available to check. Do NOT delay treatment for neurological B12 deficiency.',
     'Urgent referral if significant neurological signs (proprioception loss, ataxia, UMN signs). Referral for gastroscopy to confirm/exclude pernicious anaemia.'],
    ['Haemolytic anaemia\n(jaundice + anaemia + splenomegaly)',
     'Clinical exam + bilirubin + haemoglobin',
     '1. Confirm haemolytic triad: anaemia + jaundice (yellow sclera, skin) + splenomegaly. 2. Family history and ethnic background (HS = Northern European, G6PD = African/Mediterranean, SCD = Sub-Saharan African, thalassaemia = Mediterranean/Asian). 3. Drug and trigger history (G6PD). 4. Folic acid 5mg daily — essential in all haemolytic anaemias. 5. Identify and remove trigger (drugs, infection treatment). 6. Ensure good hydration.',
     'Any severe haemolytic crisis with Hb <60 g/L. Evidence of intravascular haemolysis (dark urine). Aplastic crisis. Suspected transfusion requirement. Sickle cell crisis.'],
    ['Suspected malignancy\n(weight loss + anaemia + rectal bleeding)',
     'Clinical exam + PR + basic bloods',
     '1. Complete physical examination including lymph nodes, abdominal mass palpation, PR examination. 2. Ask about red flag symptoms: unintentional weight loss, change in bowel habit, dysphagia, haematemesis, melaena. 3. FIT (faecal immunochemical test) if available. 4. Urgent 2-week-wait referral if any red flag symptoms in combination with anaemia.',
     'ANY red flag symptom. IDA in adult man or post-menopausal woman. Rectal mass on PR. Palpable abdominal mass.'],
]
story.append(plain_table(minimal, [CW*0.16, CW*0.15, CW*0.40, CW*0.29]))

story.append(Spacer(1,8))
story.append(bp('<b>PACES Examination Approach — Anaemia stations:</b>'))
paces_table = [
    ['PACES Station', 'Likely scenario', 'Key examination findings to seek', 'Presentation to examiner'],
    ['Station 1 — Abdominal examination',
     'Patient with haematological condition: splenomegaly, hepatomegaly, or pallor',
     'Start hands: pallor of nails, koilonychia, leukonychia, clubbing, palmar erythema. Face: conjunctival pallor, jaundice, glossitis, angular stomatitis. Neck: lymphadenopathy. Abdomen: spleen size (measure in cm from costal margin, dip percussion first), liver size, ascites, masses. State: "I would like to examine the lymph nodes in the axillae and groins, look at the lower limb for oedema, and perform a PR examination."',
     '"This patient has pallor consistent with anaemia, splenomegaly of approximately X cm, and lymphadenopathy in the cervical region. My differential for this combination would include chronic lymphocytic leukaemia, lymphoma with secondary haemolytic anaemia, or myeloproliferative disease. I would investigate with FBC and film, LDH, Coombs test, and CT staging."'],
    ['Station 3 — Cardiovascular',
     'Patient with anaemia causing high-output failure or flow murmur',
     'Signs of anaemia: tachycardia, flow murmur (ejection systolic, best at left sternal edge, varies with position and respiratory cycle). Signs of high-output failure: raised JVP, displaced apex, S3 gallop, ankle oedema, basal crackles. Cause clues: koilonychia (IDA), jaundice (haemolytic), splenomegaly (haematological).',
     '"This patient has a flow murmur secondary to severe anaemia with evidence of high-output cardiac state — tachycardia and an ejection systolic murmur. The clue to the underlying cause is the koilonychia and angular stomatitis, suggesting iron deficiency anaemia. Urgent FBC and iron studies are required."'],
    ['Station 5 — Brief clinical consultation',
     'Patient presenting with fatigue and pallor — investigate and manage',
     'Take focused history: onset, associated symptoms (B symptoms: night sweats, fevers, weight loss = lymphoma/leukaemia), dietary history, menstrual history, medications (NSAIDs, metformin, anticoagulants, PPIs), family history (HS, thalassaemia, SCD), ethnic background. Brief examination targeting: conjunctival pallor, lymphadenopathy, splenomegaly.',
     'Summarise to examiner: "This patient has a 6-month history of fatigue with pallor and a likely iron deficiency picture based on dietary history and menorrhagia. I would request FBC with reticulocyte count, iron studies, serum B12 and folate, and review the peripheral blood film. Investigations to exclude GI pathology will depend on the above results and clinical context."'],
    ['Communication station',
     'Explaining a new diagnosis of pernicious anaemia, or counselling about beta-thalassaemia trait before pregnancy',
     'Not examination — communication skills',
     'PERNICIOUS ANAEMIA: "You have a condition called pernicious anaemia — this means your stomach is unable to produce a substance needed to absorb vitamin B12 from your diet. B12 is essential for making red blood cells and keeping your nerves healthy. You will need an injection of B12 every 3 months for the rest of your life — this is very safe and will prevent the anaemia returning. I would also like to check some other blood tests as this condition can sometimes be associated with other autoimmune conditions such as thyroid disease." Allow the patient to ask questions. Emphasise lifelong treatment and monitoring.'],
]
story.append(plain_table(paces_table, [CW*0.16, CW*0.17, CW*0.33, CW*0.34]))

story.append(Spacer(1,10))

# ── COMPREHENSIVE MEMORY HOOK ──────────────────────────────────────────────────
sGrn  = ParagraphStyle('GR',  fontName='DV',   fontSize=9,  leading=14, textColor=HexColor('#155724'), spaceAfter=0)
sGrnB = ParagraphStyle('GRB', fontName='DV-B', fontSize=10, leading=15, textColor=HexColor('#155724'), spaceAfter=2)
gTS1 = TableStyle([
    ('BACKGROUND',(0,0),(-1,-1),HexColor('#d4edda')),
    ('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),10),
    ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),
    ('TOPPADDING',(0,0),(0,0),8),('BOTTOMPADDING',(0,-1),(0,-1),8),
])
gTSO = TableStyle([
    ('BOX',(0,0),(-1,-1),2,HexColor('#28a745')),
    ('BACKGROUND',(0,0),(-1,-1),HexColor('#d4edda')),
    ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
    ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),
])
gRows = [
    [Paragraph('COMPREHENSIVE ANAEMIA MASTER SUMMARY', sGrnB)],
    [Paragraph('CLASSIFICATION: MCV Low = Microcytic (TAILS: Thalassaemia, ACD, Iron, Lead, Sideroblastic). MCV Normal = Normocytic (ACD, haemolysis, aplastic, renal, blood loss). MCV High = Macrocytic (B12, folate, alcohol, liver, hypothyroidism, drugs).', sGrn)],
    [Paragraph('IDA PATTERN: Low Hb + Low MCV + Low ferritin + Low serum iron + HIGH TIBC + Low transferrin saturation + High RDW. In adult men/post-menopausal women: ALWAYS investigate GI tract urgently (colorectal cancer).', sGrn)],
    [Paragraph('ACD PATTERN: Low-normal Hb + Normal/high ferritin + LOW TIBC + Low serum iron + Raised CRP/ESR. TIBC goes DOWN in ACD (opposite to IDA). Treat the underlying disease, not just the anaemia.', sGrn)],
    [Paragraph('B12 DEFICIENCY: Macrocytic + hypersegmented neutrophils + low B12 + raised MMA (B12-specific). SACD (posterior columns + corticospinal tracts). GIVE B12 FIRST before folate. Pernicious anaemia = anti-IF antibodies + atrophic gastritis.', sGrn)],
    [Paragraph('FOLATE DEFICIENCY: Same blood picture as B12 but NO neurological features. Raised homocysteine but NORMAL MMA. Short body stores (3-4 months). Give 5mg folic acid in pregnancy to prevent neural tube defects.', sGrn)],
    [Paragraph('HAEMOLYSIS TRIAD: Anaemia + Jaundice (raised unconjugated bilirubin) + Splenomegaly. Plus: raised LDH + low haptoglobin + raised reticulocytes. DAT positive = immune cause. Spherocytes = HS or warm AIHA. Schistocytes = microangiopathic (TTP/HUS/DIC).', sGrn)],
    [Paragraph('APLASTIC ANAEMIA: Pancytopaenia (all 3 lines low) + hypocellular marrow on biopsy. Severe: neutrophils <0.5 + platelets <20 + reticulocytes <20. BMT if young + matched donor; ATG + ciclosporin + eltrombopag if not.', sGrn)],
    [Paragraph('SICKLE CELL CRISIS: O2 + fluids + analgesia (WHO ladder, morphine PCA) + warmth. ACUTE CHEST: antibiotics + exchange transfusion. HYDROXYCARBAMIDE increases HbF = fewer crises. PENICILLIN V prophylaxis lifelong (functional asplenia).', sGrn)],
    [Paragraph('THALASSAEMIA TRAIT: Microcytic anaemia + NORMAL ferritin + NORMAL RDW (distinguish from IDA by RDW: normal in thal, high in IDA). Confirm with Hb electrophoresis: HbA2 >3.5% = beta-thal trait. No treatment, genetic counselling.', sGrn)],
    [Paragraph('IRON THERAPY: Ferrous sulfate 200mg TDS for 3 months after Hb normalises. With vitamin C, away from PPIs/calcium. IV ferric carboxymaltose for malabsorption/intolerance. Watch for hypophosphataemia with IV ferric carboxymaltose.', sGrn)],
    [Paragraph('B12 THERAPY: 1mg IM hydroxocobalamin every other day x6 (loading), then every 3 months LIFELONG in pernicious anaemia. Oral B12 1000mcg/day for dietary deficiency. WATCH: hypokalemia as Hb rises rapidly (potassium enters new red cells).', sGrn)],
    [Paragraph('INVESTIGATION ORDER: FBC + film + reticulocytes FIRST. Then MCV guides next: Microcytic = ferritin, iron studies, TIBC, anti-TTG, Hb electrophoresis. Macrocytic = B12 + folate, LFTs, TFTs, MMA. Haemolysis = DAT, haptoglobin, LDH, bilirubin. Unexplained = bone marrow biopsy.', sGrn)],
]
innerG = Table(gRows, colWidths=[CW-4])
innerG.setStyle(gTS1)
outerG = Table([[innerG]], colWidths=[CW])
outerG.setStyle(gTSO)
story.append(outerG)
story.append(Spacer(1,8))

# ── BUILD ──────────────────────────────────────────────────────────────────────
doc.build(story)
print('SUCCESS: /mnt/user-data/outputs/Anaemia_MRCP_Note.pdf generated.')
