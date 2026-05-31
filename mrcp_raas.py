#!/usr/bin/env python3
"""MRCP — ACE Inhibitors & RAAS Comprehensive Revision Note"""

import io, os, textwrap
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image as RLImage, KeepTogether)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageDraw, ImageFont

# ── FONTS ─────────────────────────────────────────────────────────────────────
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

OUT = '/mnt/user-data/outputs/RAAS_ACEi_MRCP_Note.pdf'
doc = SimpleDocTemplate(OUT, pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=MARGIN, bottomMargin=MARGIN)

# ── PARAGRAPH STYLES ──────────────────────────────────────────────────────────
sTitle = ParagraphStyle('TT', fontName='DV-B', fontSize=20, leading=26,
    textColor=TEAL, spaceAfter=6, alignment=1)
sSub   = ParagraphStyle('TS', fontName='DV-I', fontSize=10, leading=14,
    textColor=TEAL_M, spaceAfter=4, alignment=1)
sH1    = ParagraphStyle('H1', fontName='DV-B', fontSize=13, leading=17,
    textColor=TEAL, spaceAfter=4)
sH2    = ParagraphStyle('H2', fontName='DV-B', fontSize=10, leading=14,
    textColor=TEAL_M, spaceAfter=3)
sBody  = ParagraphStyle('Bo', fontName='DV',   fontSize=9,  leading=14,
    textColor=NAVY,  spaceAfter=3)
sPro   = ParagraphStyle('Pr', fontName='DV-I', fontSize=9,  leading=14,
    textColor=HexColor('#2c3e50'), spaceAfter=3, leftIndent=12)
sImg   = ParagraphStyle('Im', fontName='DV-I', fontSize=8,  leading=12,
    textColor=BLUE_D, spaceAfter=2)
sAlert = ParagraphStyle('Al', fontName='DV-B', fontSize=9,  leading=13,
    textColor=RED_D,  spaceAfter=3)

story = []

# ── HELPERS ───────────────────────────────────────────────────────────────────
def bp(text, st=None): return Paragraph(text, st or sBody)

def sec_header(text, story):
    story.append(Spacer(1,6)); story.append(Paragraph(text,sH1)); story.append(Spacer(1,3))

def divider(story):
    story.append(Spacer(1,4))
    t=Table([['']],colWidths=[CW])
    t.setStyle(TableStyle([('LINEABOVE',(0,0),(0,0),1,TEAL_M),
        ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
    story.append(t); story.append(Spacer(1,4))

def plain_table(data, widths, header=True):
    rows=[]
    for i,row in enumerate(data):
        st=sH2 if (i==0 and header) else sBody
        rows.append([Paragraph(str(c),st) for c in row])
    t=Table(rows,colWidths=widths,repeatRows=1 if header else 0)
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),TEAL_L),
        ('TEXTCOLOR',(0,0),(-1,0),TEAL),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,TEAL_XL]),
        ('GRID',(0,0),(-1,-1),0.5,TEAL_M),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    return t

def alert_box(text, story):
    t=Table([[Paragraph(f'<b>ALERT: {text}</b>',sAlert)]],colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),RED_L),
        ('BOX',(0,0),(-1,-1),1.5,RED_D),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,4))

def info_box(text, story, color=None, border=None):
    bg=color or AMBER; brd=border or AMBER_B
    t=Table([[Paragraph(text,sBody)]],colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),bg),
        ('BOX',(0,0),(-1,-1),1.5,brd),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,4))

def image_search_box(term, site, story):
    txt=f'IMAGE: Search <b>"{term}"</b> on <b>{site}</b> to visualise this concept.'
    t=Table([[Paragraph(txt,sImg)]],colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),BLUE_L),
        ('BOX',(0,0),(-1,-1),1,BLUE_D),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,4))

def professor_says(text, story):
    t=Table([[Paragraph(f'<i>Professor: {text}</i>',sPro)]],colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),TEAL_XL),
        ('BOX',(0,0),(-1,-1),1,TEAL_M),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,4))

def memory_hook(text, story):
    sM=ParagraphStyle('MH',fontName='DV-B',fontSize=8.5,leading=13,
        textColor=HexColor('#7b3f00'),spaceAfter=0)
    t=Table([[Paragraph(f'MEMORY: {text}',sM)]],colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),AMBER),
        ('BOX',(0,0),(-1,-1),1.5,AMBER_B),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,4))

def trial_box(trial, result, story):
    sT=ParagraphStyle('TB',fontName='DV-B',fontSize=8.5,leading=13,
        textColor=HexColor('#1a5c2a'),spaceAfter=0)
    sR=ParagraphStyle('TR',fontName='DV',fontSize=8.5,leading=13,
        textColor=HexColor('#155724'),spaceAfter=0)
    rows=[[Paragraph(f'TRIAL: {trial}',sT)],[Paragraph(f'Result: {result}',sR)]]
    t=Table(rows,colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),GREEN_L),
        ('BOX',(0,0),(-1,-1),1.5,GREEN_D),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('LEFTPADDING',(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,4))

# ── PIL HELPERS ───────────────────────────────────────────────────────────────
_FPATH  = _FD + 'DejaVuSans.ttf'
_FBPATH = _FD + 'DejaVuSans-Bold.ttf'

def _fnt(path, size):
    try: return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

def wt(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ''
    for w in words:
        test = (cur+' '+w).strip()
        try: tw = draw.textlength(test, font=font)
        except: tw = len(test)*7
        if tw <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines or [text]

def box_h(lines, font, pad=8):
    lh = (font.size if hasattr(font,'size') else 14) + 4
    return lh * len(lines) + pad * 2

def draw_box(draw, x, y, w, fill, border, lines, font, txt, pad=8):
    h = box_h(lines, font, pad)
    draw.rectangle([x,y,x+w,y+h], fill=fill, outline=border, width=2)
    lh = (font.size if hasattr(font,'size') else 14) + 4
    ty = y + pad
    for ln in lines:
        try: tw = draw.textlength(ln, font=font)
        except: tw = len(ln)*7
        tx = x + (w-tw)//2
        draw.text((tx,ty), ln, font=font, fill=txt)
        ty += lh
    return h

def arr_d(draw, x, y, length=24, size=12, fill='#555555'):
    draw.line([(x, y-length),(x, y-size)], fill=fill, width=2)
    draw.polygon([(x,y),(x-size//2,y-size),(x+size//2,y-size)], fill=fill)

def arr_r(draw, x, y, length=24, size=12, fill='#555555'):
    draw.line([(x-length,y),(x-size,y)], fill=fill, width=2)
    draw.polygon([(x,y),(x-size,y-size//2),(x-size,y+size//2)], fill=fill)

def arr_l(draw, x, y, length=24, size=12, fill='#555555'):
    draw.line([(x+length,y),(x+size,y)], fill=fill, width=2)
    draw.polygon([(x,y),(x+size,y-size//2),(x+size,y+size//2)], fill=fill)

def i2r(img, max_w=None):
    buf=io.BytesIO(); img.save(buf,'PNG'); buf.seek(0)
    mw=max_w or CW; iw,ih=img.size; scale=float(mw)/iw
    return RLImage(buf, width=iw*scale, height=ih*scale)

# ── PIL DIAGRAM 1: FULL RAAS CASCADE ─────────────────────────────────────────
def make_raas_cascade():
    W, H = 900, 780
    img = Image.new('RGB', (W, H), '#ffffff')
    d = ImageDraw.Draw(img)
    fS  = _fnt(_FPATH, 12)
    fM  = _fnt(_FPATH, 14)
    fB  = _fnt(_FBPATH, 15)
    fT  = _fnt(_FBPATH, 19)

    title = 'THE RENIN-ANGIOTENSIN-ALDOSTERONE SYSTEM (RAAS)'
    try: tw=d.textlength(title,font=fT)
    except: tw=len(title)*11
    d.text(((W-tw)//2, 8), title, font=fT, fill='#0d5c63')

    # Step 1: Triggers box (top)
    trig_y = 42
    trig_lines = ['TRIGGERS: Low BP / Low Na delivery to macula densa', 'Sympathetic activation (beta-1) / Low blood volume']
    trig_h = draw_box(d, 180, trig_y, 540, '#e8f4fd', '#2471a3', trig_lines, fM, '#1a1a2e', pad=8)

    # Arrow down
    arr_d(d, 450, trig_y+trig_h+28, 16, 14, '#2471a3')
    d.text((455, trig_y+trig_h+6), 'stimulates', font=fS, fill='#2471a3')

    # Step 2: JG cells / Renin
    ren_y = trig_y + trig_h + 46
    ren_lines = ['RENIN released', 'from Juxtaglomerular (JG) cells', 'in Kidney Afferent Arteriole']
    ren_h = draw_box(d, 240, ren_y, 420, '#fce4ec', '#c62828', ren_lines, fM, '#c62828', pad=8)

    # Arrow down with text
    arr_d(d, 450, ren_y+ren_h+28, 16, 14, '#555555')
    d.text((455, ren_y+ren_h+6), 'cleaves', font=fS, fill='#555555')
    # Angiotensinogen label on left
    ang_label = wt(d, 'Angiotensinogen (from Liver)', fS, 160)
    for i, l in enumerate(ang_label):
        d.text((20, ren_y+ren_h+6+i*16), l, font=fS, fill='#7d3c98')
    arr_r(d, 238, ren_y+ren_h+18, 40, 12, '#7d3c98')

    # Step 3: Angiotensin I
    a1_y = ren_y + ren_h + 46
    a1_lines = ['ANGIOTENSIN I (10 amino acids)', 'Inactive — just a precursor']
    a1_h = draw_box(d, 240, a1_y, 420, '#fff3cd', '#e6a817', a1_lines, fM, '#7b3f00', pad=8)

    # Arrow down
    arr_d(d, 450, a1_y+a1_h+28, 16, 14, '#555555')
    d.text((455, a1_y+a1_h+6), 'converted by ACE', font=fS, fill='#555555')
    # ACE label
    ace_label = wt(d, 'ACE (Angiotensin Converting Enzyme) — on lung + kidney endothelium', fS, 175)
    for i, l in enumerate(ace_label):
        d.text((22, a1_y+a1_h+4+i*16), l, font=fS, fill='#0d5c63')
    arr_r(d, 238, a1_y+a1_h+18, 40, 12, '#0d5c63')

    # Also: Bradykinin label (right side — ACE also degrades bradykinin)
    bk_x = 665
    bk_y = a1_y + a1_h + 4
    d.text((bk_x, bk_y), 'ACE also degrades', font=fS, fill='#c0392b')
    d.text((bk_x, bk_y+16), 'BRADYKININ', font=fB, fill='#c0392b')
    d.text((bk_x, bk_y+34), '(vasodilator)', font=fS, fill='#c0392b')

    # Step 4: Angiotensin II (central, active)
    a2_y = a1_y + a1_h + 46
    a2_lines = ['ANGIOTENSIN II (8 amino acids)', 'ACTIVE & POTENT vasoconstrictor', 'Acts via AT1 and AT2 receptors']
    a2_h = draw_box(d, 200, a2_y, 500, '#fde8e8', '#c0392b', a2_lines, fB, '#c0392b', pad=10)

    # Three output arrows from Ang II
    out_y = a2_y + a2_h + 10
    end_y = out_y + 44
    cx_left, cx_mid, cx_right = 160, 450, 740
    d.line([(450, a2_y+a2_h),(450, out_y)], fill='#555555', width=2)
    d.line([(cx_left, out_y),(cx_right, out_y)], fill='#555555', width=2)
    for cx in [cx_left, cx_mid, cx_right]:
        d.line([(cx, out_y),(cx, end_y)], fill='#555555', width=2)
    # Arrowheads
    for cx in [cx_left, cx_mid, cx_right]:
        d.polygon([(cx,end_y),(cx-8,end_y-14),(cx+8,end_y-14)], fill='#555555')

    # Left branch: Adrenal Cortex / Aldosterone
    al_y = end_y + 2
    al_lines = ['ADRENAL CORTEX', '(Zona Glomerulosa)', 'releases ALDOSTERONE']
    al_h = draw_box(d, 50, al_y, 220, '#d4edda', '#28a745', al_lines, fM, '#155724', pad=8)
    # Sub-box for aldosterone effects
    eff_lines = ['Kidney DCT/Collecting Duct:', 'Na+ reabsorption UP', 'K+ excretion UP', 'H2O follows Na+ -> BP UP']
    eff_h = draw_box(d, 50, al_y+al_h+4, 220, '#e8f4fd', '#2471a3', eff_lines, fS, '#1a1a2e', pad=6)

    # Middle branch: Direct vascular / cardiac effects (AT1)
    at1_y = end_y + 2
    at1_lines = ['AT1 RECEPTOR EFFECTS', 'Vasoconstriction -> BP UP', 'Cardiac hypertrophy', 'Na+ retention (prox. tubule)', 'Thirst + ADH release']
    at1_h = draw_box(d, 340, at1_y, 220, '#fde8e8', '#c0392b', at1_lines, fM, '#c0392b', pad=8)
    at2_lines = ['AT2 RECEPTOR EFFECTS', 'Vasodilation', 'Anti-proliferative', 'Natriuresis', '(counterbalances AT1)']
    at2_h = draw_box(d, 340, at1_y+at1_h+4, 220, '#f5eef8', '#7d3c98', at2_lines, fS, '#4a235a', pad=6)

    # Right branch: Posterior pituitary / ADH
    adh_y = end_y + 2
    adh_lines = ['POSTERIOR PITUITARY', 'releases ADH/Vasopressin', 'Water retention in', 'collecting duct', '-> volume expansion']
    adh_h = draw_box(d, 630, adh_y, 220, '#fff3cd', '#e6a817', adh_lines, fM, '#7b3f00', pad=8)

    # Bottom summary
    sum_y = al_y + al_h + eff_h + 18
    sum_lines = wt(d, 'NET EFFECT: Raised blood pressure + expanded blood volume + Na+ retention + K+ loss', fB, 820)
    draw_box(d, 20, sum_y, 860, '#e0f4f5', '#0d5c63', sum_lines, fB, '#0d5c63', pad=8)

    final_h = sum_y + 60
    img = img.crop((0, 0, W, min(final_h, H)))
    return i2r(img)

# ── PIL DIAGRAM 2: DRUG INTERVENTION POINTS ───────────────────────────────────
def make_drug_targets():
    W, H = 900, 680
    img = Image.new('RGB', (W, H), '#ffffff')
    d = ImageDraw.Draw(img)
    fS  = _fnt(_FPATH, 12)
    fM  = _fnt(_FPATH, 14)
    fB  = _fnt(_FBPATH, 15)
    fT  = _fnt(_FBPATH, 18)

    title = 'WHERE DRUGS BLOCK THE RAAS CASCADE'
    try: tw=d.textlength(title,font=fT)
    except: tw=len(title)*11
    d.text(((W-tw)//2, 8), title, font=fT, fill='#0d5c63')

    # Left column: RAAS cascade (simplified)
    cx = 300  # centre of cascade column

    # Angiotensinogen
    y = 45
    h = draw_box(d, cx-130, y, 260, '#f0fafb', '#1a8a94', ['Angiotensinogen (Liver)'], fM, '#1a1a2e', pad=8)

    # Arrow + Renin label
    arr_d(d, cx, y+h+24, 14, 12, '#555555')
    d.text((cx+6, y+h+4), 'Renin', font=fS, fill='#c62828')

    # Block 1: Direct Renin Inhibitor
    drug1_lines = wt(d, 'ALISKIREN (Direct Renin Inhibitor) Blocks renin activity directly', fS, 200)
    dh1 = draw_box(d, 560, y+h+2, 220, '#fce4ec', '#c62828', drug1_lines, fS, '#c0392b', pad=6)
    arr_l(d, 558, y+h+16, 40, 12, '#c62828')
    d.text((480, y+h+2), 'BLOCKED', font=fB, fill='#c62828')

    # Angiotensin I
    a1_y = y+h+42
    h1 = draw_box(d, cx-130, a1_y, 260, '#fff3cd', '#e6a817', ['Angiotensin I (inactive)'], fM, '#7b3f00', pad=8)

    # Arrow + ACE label
    arr_d(d, cx, a1_y+h1+24, 14, 12, '#555555')
    d.text((cx+6, a1_y+h1+4), 'ACE', font=fS, fill='#0d5c63')

    # Block 2: ACEi
    drug2_lines = ['ACE INHIBITORS', 'Ramipril, Lisinopril,', 'Enalapril, Perindopril,', 'Captopril, Quinapril']
    dh2 = draw_box(d, 560, a1_y+h1, 220, '#d4edda', '#28a745', drug2_lines, fS, '#155724', pad=6)
    arr_l(d, 558, a1_y+h1+16, 40, 12, '#28a745')
    d.text((480, a1_y+h1+2), 'BLOCKED', font=fB, fill='#28a745')

    # Bradykinin effect of ACEi
    bk_lines = wt(d, 'Bradykinin accumulates -> COUGH + Angioedema (bradykinin effect)', fS, 200)
    draw_box(d, 560, a1_y+h1+dh2+4, 220, '#fde8e8', '#c0392b', bk_lines, fS, '#c0392b', pad=5)

    # Angiotensin II
    a2_y = a1_y + h1 + 42
    h2 = draw_box(d, cx-130, a2_y, 260, '#fde8e8', '#c0392b', ['ANGIOTENSIN II', '(active, potent)'], fB, '#c0392b', pad=10)

    # Arrow to AT1 receptor
    arr_d(d, cx, a2_y+h2+24, 14, 12, '#555555')
    d.text((cx+6, a2_y+h2+4), 'AT1 receptor', font=fS, fill='#555555')

    # Block 3: ARBs
    drug3_lines = ['ARBs (AT1 Blockers)', 'Losartan, Candesartan,', 'Valsartan, Irbesartan,', 'Telmisartan, Olmesartan']
    dh3 = draw_box(d, 560, a2_y+h2+2, 220, '#e8f4fd', '#2471a3', drug3_lines, fS, '#1a1a2e', pad=6)
    arr_l(d, 558, a2_y+h2+20, 40, 12, '#2471a3')
    d.text((480, a2_y+h2+6), 'BLOCKED', font=fB, fill='#2471a3')

    # AT1 receptor effects
    at1_y = a2_y + h2 + 42
    h3 = draw_box(d, cx-130, at1_y, 260, '#fce4ec', '#c62828', ['AT1 Effects:', 'Vasoconstriction', 'Aldosterone release', 'Na+ retention, ADH'], fM, '#c62828', pad=8)

    # Arrow to Aldosterone
    arr_d(d, cx, at1_y+h3+24, 14, 12, '#555555')
    d.text((cx+6, at1_y+h3+4), 'adrenal cortex', font=fS, fill='#555555')

    # Aldosterone
    ald_y = at1_y + h3 + 42
    h4 = draw_box(d, cx-130, ald_y, 260, '#d4edda', '#28a745', ['ALDOSTERONE', '(mineralocorticoid)', 'Na+ reabsorption, K+ loss'], fM, '#155724', pad=8)

    # Block 4: Aldosterone antagonists
    drug4_lines = ['ALDOSTERONE ANTAGONISTS', 'Spironolactone', 'Eplerenone', '(block mineralocorticoid receptor)']
    dh4 = draw_box(d, 560, ald_y, 220, '#f5eef8', '#7d3c98', drug4_lines, fS, '#4a235a', pad=6)
    arr_l(d, 558, ald_y+20, 40, 12, '#7d3c98')
    d.text((480, ald_y+4), 'BLOCKED', font=fB, fill='#7d3c98')

    # Left: ARBs preserve bradykinin (advantage over ACEi)
    note_lines = wt(d, 'ARBs do NOT affect bradykinin -> NO cough. AT2 receptor still activated (vasodilatory, protective).', fS, 200)
    draw_box(d, 20, a2_y, 200, '#e0f4f5', '#0d5c63', note_lines, fS, '#0d5c63', pad=6)

    # Legend box at bottom
    leg_y = ald_y + h4 + 20
    leg_lines = ['GREEN = ACE inhibitors   BLUE = ARBs   RED = Aliskiren   PURPLE = Aldosterone antagonists']
    draw_box(d, 20, leg_y, 860, '#f0fafb', '#1a8a94', leg_lines, fS, '#0d5c63', pad=6)

    final_h = leg_y + 55
    img = img.crop((0, 0, W, min(final_h, H)))
    return i2r(img)

# ── PIL DIAGRAM 3: KIDNEY TUBULE — ALDOSTERONE EFFECTS ────────────────────────
def make_kidney_tubule():
    W, H = 900, 500
    img = Image.new('RGB', (W, H), '#ffffff')
    d = ImageDraw.Draw(img)
    fS  = _fnt(_FPATH, 12)
    fM  = _fnt(_FPATH, 14)
    fB  = _fnt(_FBPATH, 15)
    fT  = _fnt(_FBPATH, 18)

    title = 'ALDOSTERONE ACTION ON KIDNEY TUBULE (DCT & Collecting Duct)'
    try: tw=d.textlength(title,font=fT)
    except: tw=len(title)*11
    d.text(((W-tw)//2, 8), title, font=fT, fill='#0d5c63')

    # Left side: Blood (peritubular capillary)
    draw_box(d, 15, 50, 155, '#fce4ec', '#c62828', ['BLOOD', '(Peritubular', 'Capillary)', 'High Na+', 'Low K+'], fM, '#c62828', pad=8)

    # Tubular cell (centre)
    cell_x, cell_y, cell_w, cell_h = 200, 45, 500, 350
    d.rectangle([cell_x, cell_y, cell_x+cell_w, cell_y+cell_h], fill='#e8f4fd', outline='#2471a3', width=3)
    try: tw=d.textlength('TUBULAR CELL', font=fB)
    except: tw=120
    d.text((cell_x+(cell_w-tw)//2, cell_y+8), 'TUBULAR CELL', font=fB, fill='#1a1a2e')
    d.text((cell_x+(cell_w-tw)//2, cell_y+28), '(DCT and Collecting Duct)', font=fS, fill='#555555')

    # Inside cell: Aldosterone binds to MR
    ald_box_lines = wt(d, 'ALDOSTERONE enters cell, binds Mineralocorticoid Receptor (MR) in nucleus -> gene transcription', fS, 440)
    ah = draw_box(d, cell_x+20, cell_y+55, 460, '#d4edda', '#28a745', ald_box_lines, fS, '#155724', pad=6)

    # Na+/K+ ATPase (basolateral membrane)
    nka_y = cell_y + 55 + ah + 20
    nka_lines = ['Na+/K+ ATPase pump (basolateral)', 'Pumps 3 Na+ OUT -> blood', 'Pumps 2 K+ IN -> cell', 'Aldosterone UPREGULATES this pump -> MORE Na+ removed from cell']
    nka_h = draw_box(d, cell_x+20, nka_y, 460, '#fff3cd', '#e6a817', nka_lines, fS, '#7b3f00', pad=6)

    # ENaC channel (luminal membrane)
    enac_y = nka_y + nka_h + 10
    enac_lines = ['ENaC (Epithelial Na+ Channel) — luminal border', 'Aldosterone OPENS these channels -> Na+ floods in from urine', 'Water follows Na+ via osmosis -> volume expansion']
    enac_h = draw_box(d, cell_x+20, enac_y, 460, '#f5eef8', '#7d3c98', enac_lines, fS, '#4a235a', pad=6)

    # Right side: Urine (tubular lumen)
    draw_box(d, 720, 50, 165, '#fef3e2', '#d4640a', ['URINE', '(Tubular Lumen)', 'Low Na+', 'High K+', 'High H+'], fM, '#d4640a', pad=8)

    # Arrows showing Na+ movement
    arr_r(d, 198, nka_y+20, 30, 12, '#2471a3')  # Na+ out to blood
    d.text((30, nka_y+6), 'Na+ -> blood', font=fS, fill='#2471a3')
    d.text((30, nka_y+22), '(raised BP)', font=fS, fill='#2471a3')

    arr_l(d, 720, enac_y+20, 30, 12, '#d4640a')  # Na+ in from lumen
    d.text((726, enac_y+6), 'Na+ from', font=fS, fill='#d4640a')
    d.text((726, enac_y+22), 'urine', font=fS, fill='#d4640a')

    # K+ arrow (out to urine — K+ wasting effect)
    d.text((726, nka_y+38), 'K+ -> urine', font=fS, fill='#c0392b')
    d.text((726, nka_y+54), '(hypokalaemia)', font=fS, fill='#c0392b')
    arr_r(d, 720, nka_y+45, 20, 12, '#c0392b')

    # Net effects box at bottom
    net_y = cell_y + cell_h + 20
    net_lines = ['NET ALDOSTERONE EFFECTS: Na+ RETAINED + H2O retained (volume UP, BP UP) + K+ LOST (hypokalaemia) + H+ lost (metabolic alkalosis)']
    draw_box(d, 15, net_y, 870, '#fde8e8', '#c0392b', net_lines, fM, '#c0392b', pad=8)

    # Spironolactone/Eplerenone block
    spi_lines = wt(d, 'SPIRONOLACTONE / EPLERENONE block MR -> reverse all of the above -> Na+ lost, K+ retained', fS, 240)
    draw_box(d, 220, cell_y+55, 260, '#e8f4fd', '#2471a3', spi_lines, fS, '#2471a3', pad=5)

    final_h = net_y + 70
    img = img.crop((0, 0, W, min(final_h, H)))
    return i2r(img)

# ── PIL DIAGRAM 4: ACE INHIBITOR PHARMACOLOGY ────────────────────────────────
def make_acei_pharmacology():
    W, H = 900, 560
    img = Image.new('RGB', (W, H), '#ffffff')
    d = ImageDraw.Draw(img)
    fS  = _fnt(_FPATH, 12)
    fM  = _fnt(_FPATH, 14)
    fB  = _fnt(_FBPATH, 15)
    fT  = _fnt(_FBPATH, 17)

    title = 'ACE INHIBITORS — Key Drugs, Prodrugs & Adverse Effects'
    try: tw=d.textlength(title,font=fT)
    except: tw=len(title)*10
    d.text(((W-tw)//2, 8), title, font=fT, fill='#0d5c63')

    # Two column layout: Left = prodrug table, Right = adverse effects
    # Left: Prodrug classification
    draw_box(d, 20, 45, 400, '#e0f4f5', '#0d5c63', ['PRODRUG CLASSIFICATION'], fB, '#0d5c63', pad=8)

    prod_items = [
        ('PRODRUGS (inactive, must be activated by liver/gut esterases):', '#28a745', '#d4edda'),
        ('Ramipril -> Ramiprilat', '#155724', '#d4edda'),
        ('Enalapril -> Enalaprilat', '#155724', '#d4edda'),
        ('Perindopril -> Perindoprilat', '#155724', '#d4edda'),
        ('Quinapril -> Quinaprilat', '#155724', '#d4edda'),
        ('Trandolapril -> Trandolaprilat', '#155724', '#d4edda'),
        ('ACTIVE DRUGS (no conversion needed):', '#c0392b', '#fde8e8'),
        ('Lisinopril (most used in UK)', '#c0392b', '#fde8e8'),
        ('Captopril (short-acting, SH group)', '#c0392b', '#fde8e8'),
    ]

    py = 100
    for item, tc, fc in prod_items:
        il = wt(d, item, fS, 370)
        ih = draw_box(d, 25, py, 390, fc, '#aaaaaa', il, fS, tc, pad=4)
        py += ih + 3

    # Right: Adverse effects
    draw_box(d, 460, 45, 420, '#fde8e8', '#c0392b', ['ADVERSE EFFECTS'], fB, '#c0392b', pad=8)

    ae_items = [
        ('DRY PERSISTENT COUGH (10-15% Caucasians, up to 40% Asians) — Bradykinin accumulates in airways. A class effect. Switch to ARB.', '#c0392b', '#fde8e8'),
        ('ANGIOEDEMA (<0.5%) — Bradykinin causes tongue/throat swelling. Life-threatening. ABSOLUTE contraindication to re-challenge with any ACEi. Low cross-reactivity with ARBs.', '#c0392b', '#fde8e8'),
        ('HYPERKALAEMIA — Reduced aldosterone -> K+ retention. Monitor K+. Dangerous with spironolactone, NSAIDs, K+ supplements, CKD.', '#7b3f00', '#fff3cd'),
        ('FIRST-DOSE HYPOTENSION — Especially in volume-depleted patients, heart failure, high-dose diuretics. Start low, review in 1-2 weeks.', '#7b3f00', '#fff3cd'),
        ('AKI — Especially in bilateral renal artery stenosis (RAS). ACEi dilates efferent arteriole -> GFR drops. Accept up to 30% creatinine rise. >30% rise: STOP, image renal arteries.', '#c0392b', '#fde8e8'),
        ('TERATOGENICITY — Absolute contraindication ALL trimesters of pregnancy. Causes foetal renal dysplasia, oligohydramnios, limb defects.', '#c0392b', '#fde8e8'),
        ('TASTE DISTURBANCE / RASH — More common with captopril (SH group). Rare with newer ACEi.', '#155724', '#d4edda'),
    ]

    ay = 100
    for item, tc, fc in ae_items:
        il = wt(d, item, fS, 390)
        ih = draw_box(d, 465, ay, 415, fc, '#aaaaaa', il, fS, tc, pad=4)
        ay += ih + 3

    # Bottom: Renal haemodynamic effect
    bot_y = max(py, ay) + 15
    ren_lines = wt(d, 'RENAL HAEMODYNAMIC EFFECT: ACEi dilates efferent arteriole (more than afferent) -> reduces intraglomerular pressure -> protective in diabetic nephropathy (reduces proteinuria). BUT in RAS: efferent dilation with fixed afferent stenosis -> GFR collapses.', fM, 850)
    draw_box(d, 20, bot_y, 860, '#e0f4f5', '#0d5c63', ren_lines, fM, '#0d5c63', pad=8)

    final_h = bot_y + 80
    img = img.crop((0, 0, W, min(final_h, H)))
    return i2r(img)

# ── BUILD DIAGRAMS ────────────────────────────────────────────────────────────
print('Building PIL diagrams...')
raas_img  = make_raas_cascade()
drugs_img = make_drug_targets()
tubule_img= make_kidney_tubule()
pharm_img = make_acei_pharmacology()
print('PIL diagrams done.')

# ═══════════════════════════════════════════════════════════════════════════════
# STORY
# ═══════════════════════════════════════════════════════════════════════════════
story.append(Spacer(1,8))
story.append(Paragraph('ACE INHIBITORS &amp; THE RAAS', sTitle))
story.append(Paragraph('Renin-Angiotensin-Aldosterone System | Comprehensive MRCP Revision Note', sSub))
story.append(Paragraph('Parts 1, 2 &amp; PACES | Pharmacology · Physiology · Clinical Application', sSub))
story.append(Spacer(1,6))
tags=[['Topic','System','Key drugs','Trials'],
    ['RAAS + ACEi + ARBs + Aldosterone antagonists','Cardiovascular, Renal, Endocrine','Ramipril, Lisinopril, Losartan, Spironolactone','HOPE, CONSENSUS, RALES, ONTARGET']]
story.append(plain_table(tags,[CW*0.25,CW*0.25,CW*0.25,CW*0.25]))
story.append(Spacer(1,6))
divider(story)

# ── SECTION 1: OVERVIEW ────────────────────────────────────────────────────────
sec_header('Section 1: Overview — Why RAAS and ACE Inhibitors Matter', story)
professor_says('The Renin-Angiotensin-Aldosterone System is the body\'s master controller of blood pressure and blood volume. Think of it as a sophisticated pressure gauge with a feedback loop: when pressure falls, the system activates and raises it back up. ACE inhibitors and related drugs interfere with this system at key points — they are among the most important drugs in all of medicine, appearing in the treatment of hypertension, heart failure, kidney disease, and prevention of stroke and heart attack.', story)

story.append(bp('<b>The RAAS in one sentence:</b> When blood pressure or blood volume falls, '
    'the kidney releases renin → which converts angiotensinogen to angiotensin I → '
    'which is converted by ACE (Angiotensin Converting Enzyme) to angiotensin II → '
    'which raises blood pressure by constricting blood vessels and stimulating aldosterone → '
    'which causes the kidneys to retain sodium and water.'))
story.append(Spacer(1,4))
story.append(bp('<b>Why does this matter clinically?</b>'))
why_raas = [
    ['Clinical context', 'Why RAAS is involved', 'Which drug class to use'],
    ['Hypertension\n(high blood pressure)', 'Overactive RAAS is one of the main mechanisms in essential hypertension. Blocking RAAS reduces BP without causing the reflex tachycardia seen with many other antihypertensives.', 'ACE inhibitors (first-line in T1DM, T2DM with proteinuria, or patients <55 without Afro-Caribbean background). ARBs (when ACEi not tolerated). Both are recommended in CKD.'],
    ['Heart failure with reduced ejection fraction\n(HFrEF)', 'In heart failure, the heart pumps poorly → the body activates RAAS (senses low cardiac output as low BP) → further vasoconstriction and fluid retention → worsens heart function — a vicious cycle. ACEi break this cycle.', 'ACE inhibitors (FIRST LINE — CONSENSUS, SOLVD trials). ARBs if ACEi-intolerant. Add aldosterone antagonist (RALES/EPHESUS) for Class II-IV HFrEF.'],
    ['Chronic kidney disease\n(CKD) + proteinuria', 'High intraglomerular pressure damages kidney filtration barrier → protein leaks into urine (proteinuria) → accelerates kidney damage. ACEi selectively dilate efferent arteriole → reduce intraglomerular pressure → protect kidney.', 'ACE inhibitors or ARBs — reduce proteinuria by up to 40-50%, slow progression of CKD. Landmark: Lewis trial (captopril in T1DM nephropathy).'],
    ['Post-myocardial infarction\n(post-MI)', 'After MI, the damaged heart remodels — the ventricle dilates and thins (like a balloon being overstretched). RAAS activation drives this harmful remodelling. ACEi prevent it.', 'ACE inhibitors — start within 24h if no contraindication (SAVE, AIRE, TRACE trials). Ramipril specifically has the strongest evidence (HOPE trial for high CV risk patients).'],
    ['Diabetic nephropathy\n(kidney damage from diabetes)', 'Diabetes damages the glomerular filtration barrier. Early sign: microalbuminuria (tiny amounts of protein in urine). ACEi/ARBs reduce intraglomerular pressure → protect filtration barrier → slow progression from microalbuminuria to overt nephropathy to end-stage renal disease.', 'ACEi or ARBs — evidence for both. Start when microalbuminuria detected (uACR >3 mg/mmol in diabetics). IRMA-2, IDNT, RENAAL trials.'],
    ['Stroke prevention', 'RAAS blockade reduces blood pressure and may have direct vascular protective effects. Perindopril + indapamide (diuretic) combination showed remarkable benefit in secondary stroke prevention.', 'ACEi: PROGRESS trial — perindopril-based regimen reduced recurrent stroke risk by 28%.'],
]
story.append(plain_table(why_raas, [CW*0.20, CW*0.44, CW*0.36]))
divider(story)

# ── SECTION 2: ANATOMY & PHYSIOLOGY OF THE RAAS ──────────────────────────────
sec_header('Section 2: Anatomy & Physiology — The Complete RAAS Cascade', story)
professor_says('Let us walk through the RAAS step by step, as if we are following a message from the moment the kidney senses trouble. Imagine the kidney as a security guard who monitors blood pressure constantly. When pressure drops, the guard sends a hormonal alarm signal. That alarm triggers a cascade of events that ultimately brings the pressure back up — through three main routes: squeezing the blood vessels, telling the kidney to hold onto salt and water, and stimulating thirst.', story)

story.append(raas_img)
story.append(Spacer(1,4))
story.append(bp('<i>Figure 1: The complete RAAS cascade from trigger to effect. '
    'Every step in this chain is a potential drug target. '
    'Understanding the cascade lets you predict the consequences of blocking any step.</i>', sImg))
story.append(Spacer(1,6))

story.append(bp('<b>Step-by-step explanation of the RAAS:</b>'))
raas_steps = [
    ['Step', 'Location', 'What happens (plain English)', 'How it is regulated'],
    ['Step 1:\nTriggers → Renin Release',
     'Juxtaglomerular (JG) cells — modified smooth muscle cells in the wall of the afferent arteriole (the blood vessel entering the kidney glomerulus — the filtration unit)',
     'Three signals stimulate JG cells to release RENIN: (1) LOW BLOOD PRESSURE — the JG cells are mechanoreceptors (pressure sensors). They detect stretch in the arteriole wall. Low stretch = low pressure = release renin. (2) LOW NaCl DELIVERY to macula densa — the macula densa is a cluster of specialised cells in the distal tubule that senses NaCl concentration in the tubular fluid. Low NaCl = low blood volume = release renin. (3) SYMPATHETIC NERVOUS SYSTEM — beta-1 adrenoceptors on JG cells. Stimulation by adrenaline (epinephrine) and noradrenaline → direct release of renin. This is why beta-blockers reduce renin release.',
     'NEGATIVE FEEDBACK: Angiotensin II directly suppresses JG cells (short feedback loop). Atrial Natriuretic Peptide (ANP — released from the heart when it is overstretched = too much volume) also suppresses renin. Prostaglandins (PGI2, PGE2) stimulate renin release — this is why NSAIDs (which block prostaglandins) reduce renin and can worsen hypertension.'],
    ['Step 2:\nRenin cleaves\nAngiotensinogen\n→ Angiotensin I',
     'In the blood plasma. Angiotensinogen is made continuously by the LIVER.',
     'Renin is a protease (an enzyme that cuts proteins). It has one specific job: cutting off a 10-amino-acid fragment from angiotensinogen. This fragment is called ANGIOTENSIN I (Ang I). Ang I is biologically INACTIVE — it cannot do anything useful on its own. It is just a precursor — think of it as a key that has not yet been cut to the right shape.',
     'Angiotensinogen levels are increased by: oestrogens (oral contraceptive pill → raises angiotensinogen → raises Ang II → raises BP — one mechanism behind OCP-related hypertension), corticosteroids, thyroid hormones.'],
    ['Step 3:\nACE converts\nAngiotensin I\n→ Angiotensin II',
     'Primarily the PULMONARY ENDOTHELIUM (the lining of the blood vessels in the lungs). Also kidney, heart, brain, and vascular endothelium throughout the body. The lungs are uniquely positioned: 100% of cardiac output passes through them, so ACE has maximum access to Ang I.',
     'ACE (Angiotensin Converting Enzyme) is a zinc-containing metalloprotease. It removes two amino acids from the C-terminal end of Ang I → producing ANGIOTENSIN II (8 amino acids). Ang II is the most potent vasoconstrictor produced by the body. ALSO: ACE simultaneously breaks down BRADYKININ (a vasodilator and inflammatory mediator) into inactive fragments. This dual action explains why ACE inhibitors raise bradykinin levels — causing both the therapeutic benefit (vasodilation) and the side effects (cough, angioedema).',
     'ACE activity is reduced by: ACE inhibitors. ACE activity is increased by: nothing clinically — it simply converts all available Ang I.'],
    ['Step 4:\nAngiotensin II\nacts at receptors',
     'AT1 receptors: blood vessels, adrenal cortex, kidney, heart, brain. AT2 receptors: foetal tissues, kidney, adrenal gland.',
     'AT1 RECEPTOR (the predominant clinically relevant receptor): (1) VASOCONSTRICTION — Ang II is 40x more potent than noradrenaline as a vasoconstrictor. Acts on arterioles throughout the body → raises systemic vascular resistance → raises BP. (2) ADRENAL CORTEX — stimulates zona glomerulosa to release aldosterone. (3) KIDNEY PROXIMAL TUBULE — directly stimulates Na+/H+ exchanger → Na+ and water retained at this level (independent of aldosterone). (4) POSTERIOR PITUITARY — stimulates ADH (antidiuretic hormone / vasopressin) release → collecting duct water reabsorption → volume expansion. (5) HYPOTHALAMUS — stimulates thirst → increased water intake. (6) CARDIAC HYPERTROPHY — AT1 stimulation in cardiac myocytes → collagen deposition → ventricular wall thickening (maladaptive hypertrophy). AT2 RECEPTOR: counterbalances AT1. Mediates vasodilation, natriuresis (Na+ excretion), anti-fibrotic effects. ARBs block AT1 only, leaving AT2 free to activate (potentially protective effect of ARBs).',
     'Ang II is rapidly metabolised by angiotensinases. Half-life approximately 1 minute. Also converted to Angiotensin III (7 amino acids) and Angiotensin IV — which have further biological activities in the brain and kidney.'],
    ['Step 5:\nAldosterone acts\non kidney tubule',
     'Adrenal cortex zona glomerulosa (aldosterone production). Effect: DISTAL CONVOLUTED TUBULE (DCT) and CORTICAL COLLECTING DUCT of the kidney.',
     'Aldosterone is a mineralocorticoid (a steroid hormone from the adrenal cortex). It enters tubular cells, binds to the mineralocorticoid receptor (MR) in the nucleus, and activates genes encoding: (1) ENaC (Epithelial Na+ Channel) — opens Na+ channels on the luminal (urine-facing) side → Na+ floods from urine into cell. (2) Na+/K+ ATPase — pumps on the basolateral (blood-facing) side — pumps 3 Na+ out to blood, 2 K+ into cell. (3) Net result: Na+ is reabsorbed (into blood) + K+ is excreted (into urine) + H+ is excreted (metabolic alkalosis) + water follows Na+ osmotically → blood volume expands → BP rises.',
     'Aldosterone also regulated by: HIGH plasma K+ (directly stimulates adrenal zona glomerulosa — independent of RAAS). ACTH (mildly stimulates aldosterone). LOW Na+ (triggers Ang II which triggers aldosterone).'],
]
story.append(plain_table(raas_steps, [CW*0.13, CW*0.16, CW*0.41, CW*0.30]))
story.append(Spacer(1,6))
story.append(tubule_img)
story.append(Spacer(1,4))
story.append(bp('<i>Figure 2: Aldosterone\'s molecular action on the kidney distal tubule — '
    'showing ENaC channels, Na+/K+-ATPase pump, and the net effects on electrolytes and blood pressure. '
    'Spironolactone and eplerenone block the mineralocorticoid receptor inside the cell.</i>', sImg))
memory_hook('RAAS SEQUENCE: Renin → Angiotensinogen (liver) → Angiotensin I (inactive) → ACE (lung endothelium) → Angiotensin II (POWERFUL) → Adrenal cortex → Aldosterone → Kidney → Na+ IN, K+ OUT, H2O follows → BP UP. Short: "RAAS = Renin Activates Ang Sending Aldosterone" and then "Na+ IN K+ OUT H2O UP BP UP."', story)
divider(story)

# ── SECTION 3: ACE INHIBITORS — MECHANISM & PHARMACOLOGY ─────────────────────
sec_header('Section 3: ACE Inhibitors — Mechanism, Classification & Pharmacokinetics', story)
professor_says('An ACE inhibitor is like putting your hand over the nozzle of a garden hose while it is running — you reduce the pressure downstream without turning off the tap. The drug blocks the single enzyme that converts the inactive precursor into the powerful vasoconstrictor. The whole downstream cascade quietens: less vasoconstriction, less aldosterone, less Na+ retention, lower blood pressure. But there is a side effect: because ACE also breaks down bradykinin, bradykinin builds up and causes a persistent dry cough in many patients.', story)

story.append(bp('<b>Mechanism of ACE inhibitors:</b>'))
story.append(bp('ACE inhibitors contain a zinc-binding moiety (typically carboxylate, phosphonate, or thiol/sulfhydryl) '
    'that competes with the normal substrate (Ang I) for the zinc ion in the active site of ACE. '
    'By occupying the active site, they competitively inhibit ACE. '
    'The result is reduced conversion of Ang I → Ang II, causing:'))
mech_effects = [
    ['Effect of ACE inhibition', 'Consequence', 'Clinical benefit'],
    ['Angiotensin II levels fall', 'Less vasoconstriction → blood pressure falls. Less aldosterone release → less Na+/H2O retention, less K+ excretion (K+ rises — good in most contexts, dangerous if already high).', 'Lower blood pressure. Reduced preload and afterload in heart failure. Reduced glomerular pressure in CKD.'],
    ['Bradykinin levels rise\n(ACE normally breaks down bradykinin)', 'Bradykinin → vasodilation (via nitric oxide and prostacyclin production) — contributing to BP reduction. Bradykinin accumulates in the AIRWAYS → stimulates C-fibre cough receptors → PERSISTENT DRY COUGH. Bradykinin in tissues → prostaglandin and substance P release → ANGIOEDEMA if in submucosa of larynx/tongue/lips.', 'Additional antihypertensive effect. SIDE EFFECT: dry cough (class effect — 10-15% Caucasians, up to 40% Chinese/Japanese). RARE BUT SERIOUS SIDE EFFECT: angioedema (0.1-0.5%, more common in African-American patients).'],
    ['Aldosterone falls', 'Less Na+ reabsorption in DCT → mild natriuresis (Na+ excretion). Less K+ excretion → K+ tends to rise (hyperkalaemia risk). Less H2O retention → reduced blood volume.', 'Reduces oedema in heart failure. Reduces preload. RISK: hyperkalaemia — monitor K+ carefully.'],
    ['Intraglomerular pressure falls\n(efferent arteriole dilation)', 'Ang II preferentially constricts efferent arteriole (more than afferent). ACEi removes this preferential constriction → efferent dilates more than afferent → glomerular filtration pressure falls → GFR transiently decreases (creatinine rises slightly). Long-term: this lower filtration pressure protects the filtration barrier from mechanical damage.', 'EXPECTED: creatinine rise up to 30% from baseline in first 2 weeks (acceptable — due to efferent dilation). PROTECTIVE long-term: reduces proteinuria, slows CKD progression. DANGEROUS: in bilateral renal artery stenosis — the afferent arteriole has already narrowed blood supply; if efferent then dilates too, GFR collapses.'],
]
story.append(plain_table(mech_effects, [CW*0.22, CW*0.44, CW*0.34]))

story.append(Spacer(1,6))
story.append(pharm_img)
story.append(Spacer(1,4))
story.append(bp('<i>Figure 3: ACE inhibitor drug classification — prodrugs vs active drugs — and their adverse effect profile. '
    'The prodrug concept is important for MRCP: patients with liver failure may not activate prodrugs effectively.</i>', sImg))

story.append(Spacer(1,6))
story.append(bp('<b>Individual ACE inhibitors — key differences:</b>'))
acei_drugs = [
    ['Drug', 'Prodrug?', 'Elimination', 'Starting dose\n(hypertension)', 'Key clinical notes'],
    ['Ramipril\n(most commonly prescribed in UK)', 'YES → Ramiprilat', 'Renal (reduce dose in CKD; use with caution if eGFR <10)', '1.25mg once daily (start low especially in HF)', 'HOPE trial: 10mg daily → 22% reduction in CV events. AIRE trial: post-MI with LV dysfunction. MOST EVIDENCE for cardiac protection. Titrate to 10mg/day.'],
    ['Lisinopril', 'NO — active as given', 'Renal (adjust in CKD)', '2.5-5mg once daily', 'Unique: not a prodrug — useful when liver function impaired. Long half-life (24h). No food interactions. SOLVD-T trial (HF).'],
    ['Enalapril', 'YES → Enalaprilat', 'Renal', '5mg twice daily', 'CONSENSUS trial (1987): first major RCT showing ACEi survival benefit in HF. IV form (enalaprilat) exists for hypertensive emergencies.'],
    ['Perindopril', 'YES → Perindoprilat', 'Renal + biliary', '4mg once daily (2mg in elderly)', 'PROGRESS trial: perindopril ± indapamide → 28% reduction in recurrent stroke. Longer half-life. Often used in BP management.'],
    ['Captopril', 'NO — active as given', 'Renal', '12.5-25mg two or three times daily', 'FIRST ACEi developed. Short-acting (requires TDS dosing). Contains SULFHYDRYL (SH) group → more side effects: rash, taste disturbance, agranulocytosis (rare). SAVE trial: post-MI. Mainly used for rapid titration or testing tolerability. Less commonly prescribed now.'],
    ['Quinapril', 'YES → Quinaprilat', 'Renal', '10mg once daily', 'Good tissue penetration. Used in hypertension and HF. Avoid with tetracycline (chelation).'],
    ['Fosinopril', 'YES → Fosinoprilat', 'DUAL: renal + hepatic', '10mg once daily', 'ONLY ACEi with significant hepatic elimination — safer in severe CKD. Useful when renal impairment is severe.'],
    ['Trandolapril', 'YES → Trandolaprilat', 'Renal + biliary', '0.5mg once daily', 'TRACE trial: post-MI with LV dysfunction. Very long-acting — once daily.'],
]
story.append(plain_table(acei_drugs, [CW*0.15, CW*0.10, CW*0.13, CW*0.15, CW*0.47]))
memory_hook('PRODRUG vs ACTIVE: Active drugs end in "-pril" with NO hepatic activation needed. Lisinopril and Captopril are ACTIVE as given. All others (Ramipril, Enalapril, Perindopril, Fosinopril etc.) are PRODRUGS converted to "-prilat" forms. In LIVER FAILURE: use Lisinopril (active). For RENAL FAILURE: use Fosinopril (dual elimination). "LICE are active" — Lisinopril and Captopril are active.', story)
divider(story)

# ── SECTION 4: CLINICAL INDICATIONS ──────────────────────────────────────────
sec_header('Section 4: Clinical Indications — When to Use RAAS Blockade', story)
professor_says('ACE inhibitors and ARBs appear in more treatment guidelines than almost any other drug class. They are not just antihypertensives — they protect the heart, kidneys, and blood vessels by mechanisms beyond simple blood pressure lowering. Learning which trial supports which indication is essential for MRCP — the exam loves asking "which drug in which condition."', story)

story.append(drugs_img)
story.append(Spacer(1,4))
story.append(bp('<i>Figure 4: Where each drug class blocks the RAAS cascade. '
    'ACE inhibitors block ACE (preventing Ang II formation + raising bradykinin). '
    'ARBs block the AT1 receptor only (no bradykinin effect). '
    'Aldosterone antagonists block the final step in the kidney.</i>', sImg))

story.append(Spacer(1,6))
indications = [
    ['Indication', 'First-choice RAAS drug', 'Key evidence / trials', 'Target dose (ramipril unless specified)', 'MRCP pearl'],
    ['HYPERTENSION\n(first-line)',
     'ACEi or ARB — first line for: patients <55 years, all diabetics (T1 and T2), patients with CKD or proteinuria, post-MI, post-stroke. Afro-Caribbean patients: CCBs preferred first (ACEi/ARBs less effective in this population due to low-renin hypertension — add ACEi/ARB in combination).',
     'ALLHAT trial, HOPE trial, PROGRESS trial (stroke), LIFE trial (losartan).',
     'Ramipril 10mg daily. Lisinopril 20-40mg daily.',
     'NICE A/B/C/D: Step 1 — A (ACEi/ARB) if <55 or diabetic; C (CCB) if >55 or Afro-Caribbean. Step 2: A+C. Step 3: A+C+D (diuretic). Step 4: add spironolactone, beta-blocker, or alpha-blocker.'],
    ['HEART FAILURE with reduced EF\n(HFrEF, EF <40%)',
     'ACEi — ALL patients with HFrEF regardless of symptom severity (Class I recommendation). ARB if ACEi-intolerant. ARNI (sacubitril/valsartan — Entresto) now preferred over ACEi alone in established HFrEF (PARADIGM-HF trial).',
     'CONSENSUS 1987 (enalapril → 40% mortality reduction in 6 months), SOLVD-T (enalapril), SOLVD-P (prevention arm).',
     'Ramipril: start 2.5mg twice daily, target 5mg twice daily (or 10mg once daily). Enalapril: start 2.5mg twice daily, target 10-20mg twice daily.',
     'HFrEF drug combination: ACEi (or ARNI) + beta-blocker + MRA (mineralocorticoid receptor antagonist = spironolactone/eplerenone) + SGLT2 inhibitor = "The Fantastic Four" of HFrEF. All four reduce mortality.'],
    ['POST-MYOCARDIAL INFARCTION\n(post-MI)',
     'ACEi — ALL post-MI patients with LV dysfunction (EF <40%), symptomatic HF, or anterior ST-elevation MI. Start within 24h if BP allows.',
     'SAVE (captopril, EF <40%, reduced mortality 19%), AIRE (ramipril, post-MI with HF, reduced mortality 27%), TRACE (trandolapril), HOPE (ramipril, broader population without HF — 22% reduction in CV events).',
     'Ramipril: 2.5mg twice daily within 24h, target 5mg twice daily.',
     'MRCP question: "Which drug reduces mortality post-MI in a patient with reduced EF?" Answer: Ramipril (most evidence), or any ACEi. Also: add aldosterone antagonist (eplerenone, from EPHESUS trial) if post-MI with EF <40%.'],
    ['DIABETIC NEPHROPATHY\n(kidney protection in diabetes)',
     'ACEi (T1DM — strong evidence Lewis trial, captopril) or ARB (T2DM — IDNT trial irbesartan, RENAAL trial losartan). Either is acceptable. Use ACEi/ARB in all diabetics with: uACR >3 mg/mmol (microalbuminuria), or confirmed CKD, or hypertension.',
     'Lewis (1993): captopril in T1DM nephropathy → 50% reduction in risk of doubling creatinine. IDNT (2001): irbesartan in T2DM nephropathy. RENAAL (2001): losartan in T2DM nephropathy.',
     'Ramipril 10mg daily. Irbesartan 300mg daily (ARB option for T2DM).',
     'Start when uACR >3 mg/mmol EVEN IF BP NORMAL. Goal: uACR <3 (or at least 50% reduction). Do not combine ACEi + ARB (ONTARGET trial — no added benefit, more harm).'],
    ['CKD with proteinuria\n(non-diabetic)',
     'ACEi or ARB — reduce proteinuria and slow CKD progression regardless of cause (IgA nephropathy, lupus nephritis, FSGS etc.).',
     'AASK trial (ramipril in hypertensive kidney disease). Multiple trials in specific nephropathies.',
     'Ramipril 10mg daily. Titrate to maximum tolerated dose.',
     'Monitor: eGFR + K+ at baseline, 2 weeks after start and each dose increase. Accept up to 30% creatinine rise and K+ up to 5.5. If K+ >5.5 or creatinine rises >30%: STOP and investigate for renal artery stenosis.'],
    ['Secondary stroke prevention',
     'ACEi (perindopril) + diuretic (indapamide) combination — PROGRESS trial.',
     'PROGRESS (2001): perindopril 4mg ± indapamide 2.5mg → 28% reduction in recurrent stroke. Combination more effective than perindopril alone.',
     'Perindopril 4mg + indapamide 2.5mg (as Coversyl Plus fixed combination).',
     'Key: the benefit was largely from blood pressure lowering. Give to any patient with prior stroke/TIA regardless of starting BP.'],
    ['High cardiovascular risk\n(primary and secondary prevention)',
     'ACEi — HOPE trial established ramipril for broad high CV-risk population (not just hypertensives or HF patients).',
     'HOPE (2000): ramipril 10mg in patients >55 with cardiovascular risk factors (diabetes, prior CV event, or peripheral arterial disease) → 22% reduction in composite of MI, stroke, or cardiovascular death.',
     'Ramipril 10mg daily.',
     'MRCP: "55-year-old diabetic, BP 135/80, no HF. Should he be on an ACEi?" YES — HOPE trial evidence. Ramipril 10mg regardless of BP.'],
]
story.append(plain_table(indications, [CW*0.15, CW*0.19, CW*0.18, CW*0.16, CW*0.32]))

story.append(Spacer(1,4))
trial_box('CONSENSUS (1987) — Enalapril in severe HFrEF (Class III-IV, NYHA)', 'Enalapril reduced 6-month mortality by 40% vs placebo. The study was stopped early because the benefit was so large it was unethical to continue. Changed practice: ACEi became mandatory in HFrEF.', story)
trial_box('HOPE (2000) — Ramipril 10mg in high cardiovascular risk (NEJM)', 'Ramipril 10mg daily reduced the composite of MI, stroke, and cardiovascular death by 22% in patients with diabetes or established vascular disease, even those without hypertension or HF. Showed ACEi benefit extends beyond just BP lowering.', story)
trial_box('RALES (1999) — Spironolactone 25mg in severe HFrEF (NEJM)', 'Adding spironolactone to ACEi + loop diuretic in HFrEF (EF <35%) reduced all-cause mortality by 30% and hospitalisation by 35%. Transformed management: aldosterone antagonists became standard of care in HFrEF. Stopped early due to benefit.', story)
divider(story)

# ── SECTION 5: ADVERSE EFFECTS & CONTRAINDICATIONS ────────────────────────────
sec_header('Section 5: Adverse Effects & Contraindications of ACE Inhibitors', story)
professor_says('Every powerful drug has a shadow. ACE inhibitors are no exception. The cough is the most common reason patients stop the drug — it affects their quality of life. But the SERIOUS adverse effects — angioedema, hyperkalaemia, AKI in renal artery stenosis, and foetal harm in pregnancy — can be life-threatening. Knowing these lets you counsel patients, monitor appropriately, and switch to ARBs when needed.', story)

ae_table = [
    ['Adverse effect', 'Frequency', 'Mechanism', 'How to identify', 'What to do'],
    ['DRY PERSISTENT COUGH\n(THE most common reason for stopping ACEi)',
     '10-15% Caucasians. Up to 30-40% in South/East Asian populations (Chinese, Japanese, South Asian). F>M.',
     'Bradykinin accumulates in the airways (ACE no longer breaks it down). Bradykinin stimulates afferent C-fibres in bronchial mucosa → reflex dry cough. ALSO: substance P and prostaglandins contribute. A CLASS EFFECT — switching to a different ACEi will NOT resolve it.',
     'Dry, tickling, irritating, persistent cough. Onset weeks to months after starting (usually within 3 months). No wheeze, no sputum. Worse at night or on exertion. Resolves within 1-4 weeks of stopping the drug.',
     'SWITCH TO ARB (angiotensin receptor blocker) — ARBs do NOT affect bradykinin, so no cough. Do NOT rechallenge with another ACEi. If the patient insists on trying, try a lower dose or different ACEi — but the cough usually recurs. Exclude other causes of cough (GORD, post-nasal drip, asthma, ACEi-associated rhinitis).'],
    ['ANGIOEDEMA\n(rare but potentially fatal)',
     '0.1-0.5% overall. Higher in: African-American patients (3-4x higher risk), women, older patients, prior ACEi-related angioedema. Can occur years after starting the drug.',
     'BRADYKININ-MEDIATED (NOT histamine-mediated — unlike allergic anaphylaxis). Bradykinin causes increased vascular permeability → fluid shifts into subcutaneous and submucosal tissues → swelling. Because it is bradykinin-mediated: antihistamines and adrenaline are LESS EFFECTIVE than in histamine-mediated reactions (though still given). C1-esterase inhibitor concentrate or icatibant (bradykinin B2 receptor antagonist) are more specific treatments.',
     'Sudden onset swelling of face, lips, tongue, uvula, throat (laryngeal oedema — life-threatening stridor). May occur with or without urticaria. Abdomen can also be affected (visceral angioedema — presents as acute abdominal pain without skin manifestations — easily missed). No itch (unlike urticaria).',
     'IMMEDIATE: Secure airway (early intubation if threatened). Adrenaline 0.5mg IM (1:1000) for severe laryngeal involvement. Antihistamines (chlorphenamine) + hydrocortisone IV. Icatibant (Firazyr) 30mg SC or C1-esterase inhibitor concentrate for bradykinin-mediated angioedema. PERMANENTLY STOP THE ACEi — ABSOLUTE CONTRAINDICATION TO ANY FUTURE ACEi. Switch to ARB (lower but not zero cross-reactivity — 5-10% of ACEi angioedema patients also react to ARBs — counsel carefully and monitor closely).'],
    ['HYPERKALAEMIA\n(high potassium)',
     'Up to 10-40% of patients in high-risk groups (CKD, diabetes, on K+-sparing diuretics, NSAIDs, elderly).',
     'Reduced aldosterone → less K+ excretion in DCT/collecting duct → plasma K+ rises. Becomes dangerous when it causes cardiac arrhythmias (peaked T waves → QRS widening → VF → cardiac arrest at K+ >7 mmol/L).',
     'Blood test: K+ >5.0 is concerning, >5.5 is dangerous. ECG changes if K+ >6: peaked tall narrow T waves, prolonged PR interval, QRS widening.',
     'K+ 5.0-5.5: review diet (reduce high-K+ foods: bananas, tomatoes, oranges, potatoes), review other medications (stop K+ supplements, NSAIDs, potassium-sparing diuretics if possible), reduce ACEi dose, recheck in 1-2 weeks. K+ >5.5: STOP ACEi (or ARB). Investigate cause. Do NOT restart until K+ stabilised. K+ >6.5 with ECG changes: EMERGENCY — IV calcium gluconate (cardiac membrane stabilisation), insulin-dextrose, consider dialysis.'],
    ['FIRST-DOSE HYPOTENSION\n(symptomatic BP drop)',
     'Can be significant in: volume-depleted patients (high-dose diuretics, vomiting, diarrhoea), heart failure patients, bilateral renal artery stenosis.',
     'Loss of Ang II-mediated vasoconstriction → rapid fall in peripheral vascular resistance. The body has been compensating for poor cardiac output or low volume by running high Ang II levels; removing Ang II suddenly → hypotension.',
     'Dizziness, lightheadedness, syncope (fainting) within hours of first dose. BP may fall 20-30 mmHg systolic.',
     'PREVENTION: start with very low dose (captopril 6.25mg, ramipril 1.25mg). Give first dose at bedtime (patient lying down). Hold or reduce diuretics for 24-48h before starting. Ensure patient is not dehydrated. REVIEW BP 1-2 weeks after each dose increase.'],
    ['ACUTE KIDNEY INJURY (AKI)\nin renal artery stenosis (RAS)',
     'In patients with bilateral RAS or unilateral RAS in a single functioning kidney.',
     'Ang II preferentially constricts the EFFERENT arteriole — this maintains intraglomerular filtration pressure when afferent arteriole supply is already reduced by a stenosis. ACEi removes this efferent constriction → intraglomerular pressure collapses → GFR falls dramatically → AKI.',
     'Rise in creatinine >30% within 2 weeks of starting ACEi. An expected rise of up to 30% is acceptable (and protective long-term). Rise >30% suggests RAS — investigate with renal Doppler ultrasound or CT/MR angiography.',
     'STOP ACEi immediately if creatinine rises >30%. Refer for imaging of renal arteries. RAS confirmed: consider percutaneous transluminal angioplasty ± stenting (evidence is limited — ASTRAL trial showed angioplasty no better than medical management in most cases). Absolute contraindication: bilateral RAS — do NOT use ACEi or ARB.'],
    ['TERATOGENICITY\n(harm to developing baby)',
     'ABSOLUTE CONTRAINDICATION IN ALL TRIMESTERS OF PREGNANCY.',
     'Ang II is required for normal foetal kidney development. ACEi removes Ang II → foetal kidney dysplasia (kidneys fail to develop properly) → foetal oliguria (baby does not urinate) → oligohydramnios (reduced amniotic fluid — the baby\'s urine is the main component of amniotic fluid in the second half of pregnancy) → foetal lung hypoplasia (lungs cannot expand properly without amniotic fluid → hypoplastic/underdeveloped) → limb contractures (reduced foetal movement in reduced fluid) → calvarial hypoplasia (skull bone underdevelopment). First trimester: additionally teratogenic (cardiac malformations reported).',
     'Any woman of childbearing age on ACEi should have pregnancy status confirmed, be counselled about risk, and use effective contraception. Check at every appointment.',
     'STOP ACEi immediately if pregnancy confirmed or planned. Switch to methyldopa (first-line antihypertensive in pregnancy), labetalol, or nifedipine (all are safe in pregnancy). Do NOT use ACEi, ARBs, direct renin inhibitors, or aldosterone antagonists in pregnancy.'],
]
story.append(plain_table(ae_table, [CW*0.14, CW*0.10, CW*0.20, CW*0.22, CW*0.34]))
alert_box('ACEi ABSOLUTE CONTRAINDICATIONS: (1) Pregnancy — ALL trimesters (foetal renal dysplasia + oligohydramnios). (2) History of ACEi-induced angioedema. (3) Bilateral renal artery stenosis (or unilateral in single functioning kidney) — will precipitate AKI. (4) Hyperkalaemia >5.5 mmol/L (relative — must control before restarting). Switch to ARB for contraindications 1 and 3 with caution (angioedema is also partially contraindicated with ARBs — seek specialist advice).', story)
divider(story)

# ── SECTION 6: MONITORING PROTOCOL ────────────────────────────────────────────
sec_header('Section 6: Prescribing & Monitoring — Starting, Titrating, and Monitoring ACE Inhibitors', story)
professor_says('Starting an ACE inhibitor is just the beginning. The art is in monitoring — knowing what to check, when to check it, what findings to act on, and what findings to accept as expected. The NICE guidelines and prescribing textbooks (including Ganesh and Kuruvilla "Prescribing in General Medical Practice") provide clear monitoring protocols. In MRCP, you will be tested on these exact thresholds.', story)

mon_table = [
    ['When', 'What to check', 'Acceptable finding', 'Action required if abnormal'],
    ['BEFORE starting',
     'Blood pressure (baseline). Serum creatinine, eGFR (baseline — to detect pre-existing renal disease). Serum K+ (baseline — detect hyperkalaemia before starting). Urine ACR (albumin:creatinine ratio — if diabetic or CKD suspected). Pregnancy test (if woman of childbearing age). Renal artery stenosis risk assessment (peripheral arterial disease, known atherosclerosis, unequal kidney size on imaging, flash pulmonary oedema — these suggest possible bilateral RAS).',
     'Normal or expected values for this patient.',
     'K+ >5.0: optimise before starting, use with extreme caution. eGFR <30: start at very low dose, monitor closely, seek specialist advice. Suspected bilateral RAS: investigate BEFORE starting. Pregnancy positive: DO NOT start.'],
    ['1-2 WEEKS after starting\nor after EACH DOSE increase',
     'Serum creatinine (and calculate change from baseline). Serum K+. Blood pressure (check for first-dose hypotension).',
     'Creatinine rise of up to 30% from baseline (expected and ACCEPTABLE — represents reduced intraglomerular pressure). K+ up to 5.5 mmol/L.',
     'Creatinine rise >30%: STOP ACEi, investigate for renal artery stenosis (renal Doppler or CT/MR angiography). K+ >5.5: STOP ACEi, review other medications raising K+, investigate. BP too low (symptomatic hypotension): reduce dose, review diuretics, ensure euvolaemic.'],
    ['ANNUALLY\n(stable patient on long-term ACEi)',
     'Creatinine, eGFR, K+. BP. Urine ACR if diabetic or CKD. Medication review (any new drugs that interact — NSAIDs, K+ supplements, other antihypertensives).',
     'Creatinine and K+ stable within acceptable range. BP at target.',
     'Any deterioration: retitrate or investigate as above. Progressive eGFR decline despite ACEi: ensure BP well controlled, check adherence, exclude other nephrotoxins (NSAIDs, contrast dye).'],
    ['SICK-DAY RULES\n(during illness — dehydration risk)',
     'ACEi should be TEMPORARILY STOPPED during episodes of: diarrhoea and vomiting (dehydration → reduced renal perfusion → AKI risk with ACEi). Surgical procedures requiring fasting. Contrast-enhanced imaging (contrast nephropathy risk amplified with ACEi).',
     'N/A — temporarily stop the drug.',
     'Restart ACEi once patient is rehydrated and eating/drinking normally (usually 24-48h after recovery). This is the "Sick Day Rules" protocol given to all patients on ACEi/ARB/diuretics.'],
]
story.append(plain_table(mon_table, [CW*0.14, CW*0.28, CW*0.24, CW*0.34]))
info_box('<b>Prescribing pearl (from Ganesh &amp; Kuruvilla — Prescribing in General Medical Practice):</b> When starting an ACEi in a patient with heart failure, ensure the patient is euvolaemic (not dehydrated from over-diuresis). If the patient is on a loop diuretic, reduce the diuretic dose 24-48h before the first ACEi dose, or start with the lowest available dose (e.g. ramipril 1.25mg or captopril 6.25mg) at bedtime. Review BP and renal function in 1-2 weeks before uptitrating. Target dose: the maximum tolerated dose (evidence shows dose-dependent benefit — higher doses = more protection).', story)
divider(story)

# ── SECTION 7: ARBs — ANGIOTENSIN RECEPTOR BLOCKERS ───────────────────────────
sec_header('Section 7: ARBs — Angiotensin Receptor Blockers (the "Sartans")', story)
professor_says('If ACE inhibitors are like blocking the factory that makes the key, ARBs are like changing the lock. ARBs do not prevent Ang II from being made — they block the AT1 receptor that Ang II plugs into. The clinical result is almost identical to ACEi, with one important difference: bradykinin is not affected (because ACE still works), so there is no cough and much less angioedema.', story)

arb_overview = [
    ['Aspect', 'ACE Inhibitors', 'ARBs (Angiotensin Receptor Blockers)'],
    ['Mechanism', 'Block ACE enzyme → prevent Ang I → Ang II conversion → also raise bradykinin', 'Block AT1 receptor directly → Ang II cannot bind → AT2 receptor remains free to activate (vasodilation, anti-fibrotic effects). Bradykinin levels UNCHANGED.'],
    ['Effect on Ang II levels', 'REDUCE Ang II (less made)', 'Do NOT reduce Ang II — in fact, Ang II levels often RISE (because AT1 blockade causes feedback increase in renin release). But Ang II cannot act (receptor blocked).'],
    ['Effect on Bradykinin', 'RAISE bradykinin (ACE no longer degrades it)', 'NO CHANGE in bradykinin (ACE is still active)'],
    ['Cough', '10-40% of patients', 'Rare (<2%) — significantly less than ACEi'],
    ['Angioedema', '0.1-0.5% (bradykinin-mediated)', '0.1% (much less) — but cross-reactivity possible if severe ACEi angioedema'],
    ['Hyperkalaemia risk', 'YES — same mechanism (reduced aldosterone)', 'YES — same (AT1 blockade → reduced aldosterone)'],
    ['AKI in RAS risk', 'YES — same mechanism (efferent dilation)', 'YES — same (AT1 blockade reduces efferent constriction)'],
    ['Teratogenicity', 'ABSOLUTE CI in pregnancy', 'ABSOLUTE CI in pregnancy (same mechanism)'],
    ['Head-to-head evidence', 'ACEi slightly superior in post-MI and HFrEF (more data, cheaper)', 'Equivalent to ACEi in most outcomes. ONTARGET: telmisartan = ramipril but more AKI when combined.'],
    ['When to prefer ARB over ACEi', 'N/A', 'ACEi-intolerant due to cough. ACEi-intolerant due to minor angioedema (caution — check with specialist). Some T2DM nephropathy guidelines prefer ARB. Where AT2 receptor activation may provide additional benefit.'],
]
story.append(plain_table(arb_overview, [CW*0.22, CW*0.39, CW*0.39]))

story.append(Spacer(1,6))
story.append(bp('<b>Individual ARBs — key drugs:</b>'))
arb_drugs = [
    ['Drug', 'Dose (hypertension)', 'Key indication / trial', 'Notes'],
    ['Losartan\n(first ARB developed)', '50-100mg once daily', 'T2DM nephropathy (RENAAL trial — reduces ESRD). Heart failure (Val-HeFT). Hypertension. Uric acid lowering (unique — losartan increases uric acid excretion).', 'First ARB. Has uricosuric effect (lowers uric acid) — beneficial in patients with gout and hypertension. LIFE trial: superior to atenolol in hypertension for CV outcomes.'],
    ['Candesartan', '8-32mg once daily', 'HFrEF intolerant of ACEi (CHARM-Alternative trial). Combined with ACEi in refractory HF (CHARM-Added — small additional benefit but more hyperkalaemia).', 'CHARM programme: major evidence base in HF. More selective AT1 blockade.'],
    ['Valsartan', '80-320mg once daily', 'HFrEF (Val-HeFT: added to ACEi, reduced hospitalisation). Post-MI (VALIANT trial — equivalent to captopril in post-MI LV dysfunction).', 'PARADIGM-HF: sacubitril/valsartan (Entresto — valsartan combined with neprilysin inhibitor) superior to enalapril in HFrEF.'],
    ['Irbesartan', '150-300mg once daily', 'T2DM nephropathy (IDNT trial — reduced doubling of creatinine by 33%). Hypertension.', 'Good evidence in diabetic nephropathy. No significant drug interactions.'],
    ['Telmisartan', '40-80mg once daily', 'High CV risk (ONTARGET trial — equivalent to ramipril). Hypertension. Longest half-life of all ARBs (24h).', 'ONTARGET (2008): telmisartan = ramipril for CV protection. DUAL ACEi+ARB: MORE harm (AKI, hyperkalaemia) without additional CV benefit — DO NOT COMBINE.'],
    ['Olmesartan', '20-40mg once daily', 'Hypertension. Possible sprue-like enteropathy (rare — severe diarrhoea with villous atrophy) with high-dose long-term use.', 'Potent AT1 blocker. Watch for enteropathy (coeliac-like diarrhoea) — rare but reported.'],
]
story.append(plain_table(arb_drugs, [CW*0.14, CW*0.17, CW*0.38, CW*0.31]))
memory_hook('ARBs = "SARTANS" — all end in -sartan (Losartan, Candesartan, Valsartan, Irbesartan, Telmisartan, Olmesartan, Azilsartan). They "BLOCK THE LOCK" (AT1 receptor) without raising bradykinin. No cough. Same K+ and renal risks as ACEi. DO NOT combine ACEi + ARB (ONTARGET: no benefit + more harm). Choose ARB when patient cannot tolerate ACEi cough.', story)
trial_box('ONTARGET (2008) — Telmisartan vs Ramipril vs Both in high CV-risk patients (NEJM)', 'Telmisartan alone = Ramipril for CV outcomes. Telmisartan + Ramipril (dual RAAS blockade) = NO additional CV benefit + MORE hypotension, AKI, and hyperkalaemia. Conclusion: DO NOT USE ACEi + ARB TOGETHER ROUTINELY.', story)
divider(story)

# ── SECTION 8: ALDOSTERONE ANTAGONISTS ────────────────────────────────────────
sec_header('Section 8: Aldosterone Antagonists — Spironolactone & Eplerenone', story)
professor_says('If ACEi/ARBs block the upstream signal that tells the adrenal gland to release aldosterone, aldosterone antagonists go directly to the end organ and block aldosterone from doing its job. They block the mineralocorticoid receptor in the kidney tubule — the final step in the RAAS pathway. The result is potassium-sparing diuresis (Na+ is excreted, K+ is retained) and reduction of the harmful cardiac fibrosis that aldosterone causes.', story)

aldo_table = [
    ['Feature', 'Spironolactone', 'Eplerenone'],
    ['Type', 'Competitive mineralocorticoid receptor (MR) antagonist. ALSO: anti-androgenic (blocks testosterone and DHT receptor) and progestagenic effects.', 'Selective MR antagonist. No significant sex hormone receptor activity (more selective than spironolactone).'],
    ['Mechanism', 'Enters tubular cells, competes with aldosterone for binding to MR → blocks transcription of ENaC and Na+/K+ ATPase → Na+ is NOT reabsorbed (naturesis) + K+ is NOT lost (K+ retained — potassium-sparing) + H2O lost with Na+ (mild diuresis).', 'Same mechanism — selective MR blockade. More selective = fewer hormonal side effects.'],
    ['Indications', '(1) HEART FAILURE (HFrEF): RALES trial — 25mg/day added to ACEi + loop diuretic in class III-IV HFrEF → 30% mortality reduction. NICE: all HFrEF patients with EF <35%. (2) PRIMARY HYPERALDOSTERONISM (Conn\'s syndrome): aldosterone-secreting adrenal adenoma or bilateral adrenal hyperplasia → hypertension + hypokalaemia. Spironolactone is definitive medical treatment and pre-operative management before adrenalectomy. (3) SECONDARY HYPERALDOSTERONISM: liver cirrhosis + ascites (aldosterone secondary to portal hypertension → Na+ retention → ascites). Spironolactone is FIRST-LINE for management of ascites in cirrhosis (often combined with furosemide in 100:40 ratio). (4) RESISTANT HYPERTENSION: 4th-line antihypertensive (NICE Step 4) — surprisingly effective as small doses substantially lower BP in patients who have failed 3-drug regimens (often because underlying primary hyperaldosteronism is not diagnosed).', '(1) HFrEF — EMPHASIS-HF trial (2011): eplerenone 50mg in mild-moderate HFrEF (EF <30%, NYHA class II) on optimal ACEi + beta-blocker → 37% reduction in CV death or HF hospitalisation. (2) POST-MI with LV dysfunction: EPHESUS trial (2003): eplerenone added within 3-14 days post-MI with EF <40% → 15% reduction in mortality. Now standard care post-MI with LV dysfunction.'],
    ['Dose', 'HFrEF: start 25mg daily, target 25-50mg daily. Ascites: 100-400mg daily (often 100mg spiro:40mg furosemide ratio). Resistant hypertension: 25-50mg daily. Conn\'s syndrome: 100-400mg daily.', 'HFrEF: start 25mg daily, target 50mg daily. Post-MI: start 25mg daily, target 50mg daily.'],
    ['Side effects', '(1) HYPERKALAEMIA — most important. Monitor K+ regularly. Do NOT use if K+ >5.0 at baseline or eGFR <30. Especially dangerous combined with ACEi/ARB (triple RAAS blockade). (2) GYNAECOMASTIA (breast development in men) — due to anti-androgenic effect. Very common (up to 10% of men on high doses). Painful, persistent. Main reason men discontinue spironolactone. Switch to eplerenone if this occurs. (3) Menstrual irregularity and breast tenderness in women (hormonal effect). (4) Mild natriuresis: some patients feel dizzy. Monitor BP.', '(1) HYPERKALAEMIA — same risk as spironolactone. (2) NO gynaecomastia (selective MR antagonist — does not bind sex hormone receptors). (3) More expensive than spironolactone. (4) Similar diuretic and antihypertensive profile to spironolactone.'],
    ['Monitoring', 'K+ and creatinine at baseline, 1 month, 3 months, then 6-monthly. STOP if: K+ >5.5 mmol/L, creatinine >220 micromol/L (or rising significantly), AKI.', 'Same monitoring as spironolactone.'],
    ['Key contraindications', 'K+ >5.0 at baseline. eGFR <30 ml/min (accumulation → severe hyperkalaemia). Addison\'s disease (adrenal insufficiency — aldosterone deficiency). Combination with K+ supplements, K+-sparing diuretics (amiloride, triamterene) — excessive hyperkalaemia risk.', 'Same. Also: concurrent use of strong CYP3A4 inhibitors (ketoconazole, itraconazole, HIV protease inhibitors) — increases eplerenone levels dramatically → hyperkalaemia.'],
]
story.append(plain_table(aldo_table, [CW*0.14, CW*0.43, CW*0.43]))
trial_box('RALES (1999) — Spironolactone 25mg in severe HFrEF (NEJM, Pitt et al.)', 'Patients with NYHA Class III-IV HFrEF already on ACEi + loop diuretic: spironolactone 25mg/day reduced ALL-CAUSE MORTALITY by 30% and CV hospitalisation by 35%. Stopped early due to overwhelming benefit. However: subsequent population data showed hyperkalaemia deaths when widely adopted without proper monitoring — monitor K+ religiously.', story)
trial_box('EPHESUS (2003) — Eplerenone post-MI with LV dysfunction (NEJM)', 'Eplerenone 50mg started 3-14 days post-MI in patients with EF <40%: 15% reduction in all-cause mortality, 13% reduction in CV death/hospitalisation. Established eplerenone as standard care post-MI. Hyperkalaemia rate: 5.5% eplerenone vs 3.9% placebo — monitor K+.', story)
divider(story)

# ── SECTION 9: DIRECT RENIN INHIBITORS & NOVEL RAAS AGENTS ───────────────────
sec_header('Section 9: Direct Renin Inhibitors & Novel RAAS Agents', story)

novel_table = [
    ['Drug class', 'Drug name', 'Mechanism', 'Evidence & Use', 'Key limitations'],
    ['Direct Renin Inhibitor',
     'Aliskiren\n(Rasilez)',
     'Binds directly to the active site of RENIN (the enzyme at step 1 of the cascade) → blocks renin from cleaving angiotensinogen → reduces all downstream RAAS products (Ang I, Ang II, aldosterone). Plasma renin activity (PRA) falls dramatically. In contrast: ACEi and ARBs cause a compensatory RISE in renin (reactive hyperreninaemia as feedback is lost).',
     'Approved for: hypertension as monotherapy or in combination. Lowers BP comparably to ACEi/ARBs. ALTITUDE trial (2012): aliskiren + ACEi or ARB in diabetic nephropathy → increased risk of: hyperkalaemia, hypotension, and NON-FATAL STROKE AND RENAL IMPAIRMENT. Study stopped early due to harm.',
     'ALTITUDE trial: DO NOT combine with ACEi or ARBs in diabetics (increased harm). Limited additional benefit over existing RAAS drugs. No trial showing mortality benefit comparable to ACEi/ARBs. Not first-line. Use only in hypertension when other agents not tolerated.'],
    ['Sacubitril/Valsartan\n(Entresto)',
     'Sacubitril = Neprilysin inhibitor. Valsartan = ARB. Combined as ARNI (Angiotensin Receptor Neprilysin Inhibitor).',
     'Neprilysin degrades natriuretic peptides (BNP, ANP) and bradykinin. Sacubitril inhibits neprilysin → natriuretic peptides accumulate → vasodilation, natriuresis, anti-fibrotic effects in heart. Valsartan blocks AT1 receptor simultaneously → reduced vasoconstriction and aldosterone. Dual mechanism provides complementary benefit.',
     'PARADIGM-HF trial (2014, NEJM): sacubitril/valsartan vs enalapril in HFrEF (EF <40%) → 20% reduction in CV death, 21% reduction in HF hospitalisation, 16% reduction in all-cause mortality. NOW FIRST-LINE for HFrEF (preferred over ACEi alone in current ESC and NICE guidelines). Must be used INSTEAD of ACEi (not in addition — do not combine with ACEi due to angioedema risk from dual bradykinin elevation). Washout 36 hours needed when switching from ACEi.',
     'MUST STOP ACEi for 36 hours before starting (both raise bradykinin — combination → angioedema risk). Contraindicated in: pregnancy, history of angioedema, bilateral RAS. More expensive than generic ACEi. Requires K+ and renal monitoring (same as ACEi/ARBs).'],
    ['SGLT2 inhibitors\n(co-regulating RAAS)',
     'Empagliflozin, Dapagliflozin, Canagliflozin',
     'Not strictly RAAS drugs, but: SGLT2 inhibitors reduce glomerular hyperfiltration and intraglomerular pressure by a tubuloglomerular feedback mechanism — similar to ACEi/ARBs but via a different pathway. They may have additive renoprotective benefit when combined with ACEi/ARBs.',
     'EMPEROR-Reduced, DAPA-HF, CREDENCE trials: SGLT2 inhibitors reduce HF hospitalisation, CV death, and CKD progression. Now part of the "Fantastic Four" of HFrEF (alongside ACEi/ARNI, beta-blocker, MRA).',
     'Not a direct RAAS drug. Combined with ACEi/ARBs in HFrEF and CKD. Monitor: genital mycotic infections, DKA (rare in T2DM), euglycaemic DKA in T1DM. Avoid in eGFR <20.'],
]
story.append(plain_table(novel_table, [CW*0.14, CW*0.13, CW*0.24, CW*0.27, CW*0.22]))
memory_hook('ENTRESTO (sacubitril/valsartan) = "Entresto ENTERS to REPLACE" the ACEi in HFrEF. Never combine with ACEi (angioedema risk from double bradykinin rise). Wait 36 hours after stopping ACEi before starting Entresto. PARADIGM-HF: 20% mortality reduction vs enalapril = better than ACEi alone. The new first-line for HFrEF.', story)
divider(story)

# ── SECTION 10: RAAS IN DISEASE STATES ────────────────────────────────────────
sec_header('Section 10: RAAS in Disease States — Pathological Overactivation', story)
professor_says('The RAAS is designed for emergencies — to raise blood pressure when it falls. But in chronic disease states, it gets stuck in the "ON" position, causing harm instead of help. The higher the RAAS activation, the more damage it does to the heart, kidneys, and blood vessels. This is why blocking it is therapeutic, not just symptomatic.', story)

disease_table = [
    ['Disease state', 'How RAAS is altered', 'Consequences', 'RAAS drug of choice'],
    ['Heart failure\n(HFrEF)',
     'Low cardiac output → body senses "low blood pressure" → maximal RAAS activation → high Ang II + high aldosterone. Ang II: vasoconstriction (increased afterload → worsens failing heart). Aldosterone: Na+/H2O retention → volume overload → congestion + raised preload → worsens HF. RAAS becomes part of a VICIOUS CYCLE that accelerates cardiac deterioration.',
     'Cardiac remodelling: Ang II → cardiac hypertrophy → fibrosis → dilation → worse EF. Aldosterone → myocardial fibrosis (independent of BP effect). Progressive HF. Arrhythmias from cardiac fibrosis. Hypokalaemia from high aldosterone → ventricular ectopics.',
     'ACEi (or ARB/ARNI) + MRA. The "Fantastic Four" of HFrEF: ARNI + beta-blocker + MRA + SGLT2 inhibitor.'],
    ['Primary hyperaldosteronism\n(Conn\'s syndrome)',
     'AUTONOMOUS aldosterone production from adrenal adenoma (unilateral, 30-35%) or bilateral adrenal hyperplasia (65-70%) — independent of Ang II. RENIN is SUPPRESSED (the autonomous aldosterone secretion is detected by the body and RAAS feedback suppresses renin). This is the KEY diagnostic finding: raised aldosterone + SUPPRESSED RENIN.',
     'Hypertension (often difficult to control, multidrug resistant). Hypokalaemia (K+ <3.5 in 50% — the rest have normal K+ at diagnosis). Metabolic alkalosis (H+ excreted with K+). Increased cardiovascular risk beyond what is expected from BP alone (direct Ang II and aldosterone effects on vasculature and heart).',
     'SPIRONOLACTONE (or eplerenone) — blocks aldosterone receptor. 50-100mg/day controls BP and corrects K+ deficiency in bilateral hyperplasia. Unilateral adenoma: laparoscopic adrenalectomy (curative) with spironolactone pre-operatively.'],
    ['Renal artery stenosis\n(secondary hypertension)',
     'Stenosis of the renal artery → kidney beyond the stenosis is underperfused → senses low pressure → releases large amounts of RENIN → high Ang II → hypertension + contralateral kidney damages. RENIN is HIGH. Aldosterone is HIGH. K+ is LOW.',
     'Severe hypertension, often refractory. Bilateral RAS: eventually causes "flash pulmonary oedema" (sudden acute pulmonary oedema episodes without obvious cardiac cause — from Ang II-mediated vasoconstriction causing back-pressure into lungs). Renal failure if ACEi/ARB started (see above).',
     'AVOID ACEi/ARBs (will precipitate AKI). Treat hypertension with CCBs or alpha-blockers. Consider revascularisation (angioplasty ± stenting — ASTRAL trial: limited benefit in most; selected cases benefit).'],
    ['Liver cirrhosis\n(secondary hyperaldosteronism)',
     'Portal hypertension → splanchnic vasodilation → "effective" blood volume falls (blood pooling in portal system) → RAAS activated → high aldosterone → kidneys retain Na+/H2O → ascites (fluid accumulates in peritoneal cavity because hydrostatic pressure in portal vessels + low albumin → fluid leaks into abdomen). High aldosterone also drives K+ excretion → hypokalaemia.',
     'Ascites. Hepatorenal syndrome. Hypokalaemia (worsens hepatic encephalopathy — less K+ → body substitutes H+ for K+ → alkalosis → more NH3 converted to NH4+ → more crosses blood-brain barrier). Oedema.',
     'SPIRONOLACTONE (100-400mg) — first-line for ascites in cirrhosis. Added furosemide (usually 100mg spiro : 40mg furosemide) for refractory ascites. Large-volume paracentesis for tense ascites with albumin replacement.'],
    ['Chronic kidney disease\n(CKD)',
     'CKD → reduced nephron mass → RAAS activation (remaining nephrons hyperfiltrate to compensate) → intraglomerular hypertension → protein leak through damaged filtration barrier. Also: reduced Na+ delivery to macula densa → renin → Ang II. Ang II drives progressive glomerulosclerosis (scarring of glomeruli) and interstitial fibrosis.',
     'Progressive CKD (self-perpetuating cycle of nephron loss → hyperfiltration → more damage). Proteinuria (marker of glomerular barrier damage and predictor of GFR decline). Hypertension. CV disease (CKD patients have dramatically elevated CV risk — Ang II contributes to vascular disease).',
     'ACEi or ARB — reduce intraglomerular pressure, reduce proteinuria, slow CKD progression. Acceptable creatinine rise up to 30% (expected reduction in hyperfiltration). Monitor K+ carefully (CKD already reduces K+ excretion).'],
]
story.append(plain_table(disease_table, [CW*0.14, CW*0.26, CW*0.28, CW*0.32]))
divider(story)

# ── SECTION 11: DRUG INTERACTIONS ─────────────────────────────────────────────
sec_header('Section 11: Drug Interactions — What Potentiates Harm', story)

inter_table = [
    ['Interacting drug / class', 'Interaction with ACEi/ARB', 'Mechanism', 'What to do'],
    ['NSAIDs\n(ibuprofen, naproxen, diclofenac, aspirin >300mg)',
     'REDUCES antihypertensive effect of ACEi. INCREASES risk of AKI (triple whammy with diuretics).',
     'NSAIDs block prostaglandins → renal afferent arteriole constricts (prostaglandins normally dilate it) → less blood reaching glomerulus. Combined with ACEi-related efferent dilation → glomerular pressure collapses → AKI. Also: NSAIDs reduce renin release → reduced ACEi effectiveness.',
     'AVOID NSAIDs in patients on ACEi/ARBs if possible. Use paracetamol for analgesia instead. If NSAIDs unavoidable: monitor renal function closely. The "Triple Whammy" (ACEi + diuretic + NSAID) is a known cause of AKI — sick-day rules: stop all three during dehydration.'],
    ['Potassium-sparing diuretics\n(spironolactone, eplerenone, amiloride, triamterene)',
     'SEVERE HYPERKALAEMIA risk — potentially fatal cardiac arrhythmias.',
     'Both ACEi (via reduced aldosterone) and K+-sparing diuretics (by blocking aldosterone or Na+/K+ ATPase) reduce K+ excretion. Combined: K+ can rise to life-threatening levels (>7 mmol/L → VF).',
     'Use combination carefully with close monitoring (RALES trial used this combination safely with strict monitoring). Check K+ before, 1 week, 1 month, then 3-6 monthly. Target K+ <5.5. Do NOT combine in CKD without specialist supervision.'],
    ['Potassium supplements\n(Sando-K, Slow-K)',
     'Hyperkalaemia risk.',
     'Additive — both raise K+.',
     'Avoid concurrent use. If essential, monitor K+ very closely.'],
    ['Diuretics\n(loop and thiazide — furosemide, bendroflumethiazide)',
     'BENEFICIAL synergy for BP and HF management. Risk: FIRST-DOSE HYPOTENSION.',
     'Diuretics reduce volume → reflex RAAS activation (high renin state) → ACEi more effective (more Ang II to block). Risk: volume depletion + ACEi → more pronounced BP drop on first dose.',
     'Reduce diuretic dose before first ACEi dose in volume-depleted patients. Then can uptitrate both as tolerated.'],
    ['Antidiabetic drugs\n(insulin, sulphonylureas)',
     'ACEi may enhance insulin sensitivity and hypoglycaemic effect. Risk of hypoglycaemia (low blood sugar).',
     'ACEi improve peripheral glucose uptake and may reduce hepatic glucose production. Bradykinin also enhances insulin signalling.',
     'Monitor blood glucose when starting ACEi in insulin-dependent diabetics. May need to reduce insulin dose. This effect is generally beneficial — reduces HbA1c modestly.'],
    ['Allopurinol\n(gout drug)',
     'Increased risk of Stevens-Johnson syndrome and hypersensitivity reactions.',
     'Captopril (SH group) specific interaction. ACEi may increase allopurinol toxicity by reducing renal clearance.',
     'Use non-captopril ACEi in patients on allopurinol. Monitor carefully.'],
    ['Lithium\n(bipolar disorder treatment)',
     'ACEi reduce lithium excretion → lithium TOXICITY (nausea, tremor, confusion, seizures, renal failure).',
     'ACEi → reduced aldosterone → reduced Na+ reabsorption → compensatory proximal tubule reabsorbs more water + solutes including lithium. Lithium levels rise.',
     'Monitor lithium levels closely when starting ACEi. May need to reduce lithium dose. Alert psychiatrist. Avoid combination if possible.'],
    ['Ciclosporin / Tacrolimus\n(immunosuppressants post-transplant)',
     'Hyperkalaemia and AKI risk.',
     'Ciclosporin reduces renal blood flow + increases K+ retention. ACEi further reduces renal perfusion and K+ excretion.',
     'Monitor carefully. Common in renal transplant patients on immunosuppression + ACEi for graft protection.'],
    ['ACEi + ARB\n(dual RAAS blockade)',
     'NO ADDITIONAL BENEFIT. MORE HARM (hypotension, hyperkalaemia, AKI).',
     'Excessive RAAS blockade at two points → compounded risks without additive clinical benefit (ONTARGET trial).',
     'DO NOT COMBINE ACEi + ARB routinely. Exception: specialist may use in specific proteinuric nephropathies under close monitoring — not standard practice.'],
]
story.append(plain_table(inter_table, [CW*0.17, CW*0.24, CW*0.27, CW*0.32]))
alert_box('"TRIPLE WHAMMY" AKI: ACE INHIBITOR + DIURETIC + NSAID = dangerous combination. All three together dramatically reduce renal perfusion. Especially dangerous in elderly, dehydrated, or CKD patients. Sick-day rules: STOP all three during vomiting/diarrhoea. Re-start only when eating and drinking normally for 24-48 hours.', story)
divider(story)

# ── SECTION 12: RAAS IN HYPERTENSION GUIDELINES ────────────────────────────────
sec_header('Section 12: RAAS in Hypertension Guidelines — The ABCD Framework', story)

story.append(bp('<b>NICE 2019 Hypertension in Adults guideline — the ABCD step approach:</b>'))
abcd_table = [
    ['Step', 'Drug class', 'Drug choice', 'Rationale'],
    ['Step 1\n(monotherapy)',
     'A = ACEi or ARB\n(if <55 or diabetic)\nOR\nC = Calcium Channel Blocker\n(if ≥55 or Afro-Caribbean)',
     'A: Amlodipine or Lisinopril or Ramipril\nC: Amlodipine, Felodipine, Nifedipine\nAfro-Caribbean: START with C (not A — low renin state, ACEi/ARBs less effective as monotherapy)',
     'ACEi/ARBs work best in high-renin states (younger patients, diabetics). CCBs work in low-renin states (older, Afro-Caribbean). Adding them together (A+C) at step 2 covers both mechanisms.'],
    ['Step 2\n(combination)',
     'A + C\n(ACEi/ARB + CCB)',
     'e.g. Ramipril + Amlodipine\n(Sevikar, Tarka, or separate tablets)',
     'Combining two different mechanisms — RAAS blockade + vasodilation — provides superior BP control with complementary side effect profiles.'],
    ['Step 3\n(triple therapy)',
     'A + C + D\n(D = thiazide diuretic)',
     'Add Indapamide or Bendroflumethiazide\nNote: in CKD eGFR<30, use loop diuretic (furosemide) instead of thiazide',
     'Three-drug combination should control BP in majority of patients. If not controlled = RESISTANT HYPERTENSION.'],
    ['Step 4\n(resistant hypertension)',
     'Check adherence first. Then consider:\nSpironolactone 25mg (if K+ <4.5)\nDoxazosin (alpha-blocker)\nBisoprolol (beta-blocker)\nFurther specialist referral',
     'Spironolactone at step 4 is highly effective — many "resistant" cases have underlying primary hyperaldosteronism',
     'Primary hyperaldosteronism accounts for 10-20% of resistant hypertension. Even without primary hyperaldosteronism, aldosterone excess contributes to treatment resistance. Spironolactone 25mg lowers BP remarkably in this setting.'],
]
story.append(plain_table(abcd_table, [CW*0.10, CW*0.22, CW*0.28, CW*0.40]))

story.append(Spacer(1,6))
story.append(bp('<b>Special populations in hypertension management:</b>'))
spec_htn = [
    ['Population', 'RAAS drug recommendation', 'Specific advice'],
    ['Diabetics (T1 or T2)\nwith hypertension',
     'ACEi or ARB — first line regardless of age or ethnicity',
     'Preferred because they reduce diabetic nephropathy progression beyond just BP lowering (renal protection via glomerular pressure reduction). Start when microalbuminuria detected (uACR >3) even if BP is normal. Check K+ and creatinine at baseline and 2 weeks.'],
    ['CKD with proteinuria',
     'ACEi or ARB — first line',
     'Target BP <130/80 mmHg in proteinuric CKD. ACEi/ARBs reduce proteinuria (30-40% reduction), slow CKD progression. Accept creatinine rise up to 30%.'],
    ['Elderly (>80 years)',
     'Use ACEi/ARBs but be aware of increased hypotension risk',
     'Start at lowest dose. Review 1-2 weeks after starting. Target systolic BP 150-160 mmHg (HYVET trial — treating to <150 in >80yrs reduced mortality). Avoid overtreatment (causes falls, AKI).'],
    ['Pregnancy',
     'CONTRAINDICATED — DO NOT USE ACEi or ARBs',
     'Safe alternatives: Methyldopa (first-line), Labetalol (alpha+beta blocker — safe), Nifedipine (CCB — safe). Target BP <140/90 in pregnancy. Severe hypertension in pregnancy (>160/110) = eclampsia risk — treat urgently with IV labetalol or oral nifedipine.'],
    ['Bilateral renal artery stenosis',
     'CONTRAINDICATED — DO NOT USE ACEi or ARBs',
     'Use CCBs or alpha-blockers. Consider revascularisation for anatomical correction. Doppler ultrasound or CT/MR angiography for diagnosis.'],
    ['Heart failure with hypertension',
     'ACEi (or ARNI) — serves both purposes',
     'ACEi lowers BP AND treats HF. No need for additional antihypertensive if ACEi adequately titrated. Add beta-blocker (also treats both). Avoid CCBs with negative inotropy (verapamil, diltiazem) in HFrEF.'],
]
story.append(plain_table(spec_htn, [CW*0.17, CW*0.23, CW*0.60]))
divider(story)

# ── SECTION 13: MRCP EXAM HIGH-YIELD TRIGGERS ─────────────────────────────────
sec_header('Section 13: MRCP Exam — High-Yield RAAS Scenarios', story)

mrcp_table = [
    ['Stem / Trigger', 'Diagnosis / Answer', 'What the examiner wants'],
    ['Patient on ramipril for hypertension presents with a dry, irritating, persistent non-productive cough for 3 months. Peak flow normal. CXR clear.',
     'ACEi-induced cough (bradykinin accumulation in airways)',
     'SWITCH TO ARB (e.g. losartan or candesartan). Do NOT re-challenge with a different ACEi (class effect). Do NOT start antitussives. Do NOT investigate further unless other features suggest alternative cause (GORD, asthma, post-nasal drip — all worth excluding, but timing with ACEi start is key).'],
    ['Patient on ramipril for 2 years. Tongue and lip swelling, stridor developing. BP 130/80. No urticaria. No previous episodes.',
     'ACEi-induced angioedema (bradykinin-mediated)',
     'EMERGENCY: Secure airway. Adrenaline 0.5mg IM (1:1000). IV antihistamine + corticosteroid. Consider icatibant (bradykinin B2 antagonist) or C1-esterase inhibitor for bradykinin-mediated angioedema (less responsive to adrenaline than histamine-mediated). PERMANENTLY STOP ACEi — ABSOLUTE CONTRAINDICATION. Counsel about ARB (lower but not zero cross-reactivity).'],
    ['53-year-old woman, newly started on enalapril 10mg. Returns 2 weeks later. Creatinine risen from 90 to 120 micromol/L. K+ 4.9. BP 130/82.',
     'Expected and ACCEPTABLE creatinine rise from ACEi (efferent arteriole dilation reducing glomerular pressure)',
     'Calculate % rise: (120-90)/90 = 33% — borderline but the rest of the picture is reassuring (K+ acceptable, BP controlled). BORDERLINE CASE: some would continue with close monitoring; >30% rise is the standard threshold to STOP and investigate. Recheck in 2 weeks. If stable or improving: continue. If rising further: STOP ACEi and arrange renal artery imaging.'],
    ['60-year-old man, known bilateral renal artery stenosis, started on lisinopril by a new doctor. 1 week later: creatinine 500 micromol/L, K+ 6.5.',
     'ACEi-induced AKI in bilateral renal artery stenosis (efferent dilation → GFR collapses)',
     'IMMEDIATELY STOP LISINOPRIL. Emergency K+ management (IV calcium gluconate if ECG changes, insulin-dextrose). IV fluids. Admit. Renal review. Do NOT restart ACEi or ARB — absolute contraindication in bilateral RAS. Use CCB or alpha-blocker for BP instead. This is a preventable emergency.'],
    ['55-year-old man, MI 2 weeks ago. Echo: EF 35%. Currently on aspirin, atenolol, atorvastatin. What should be added?',
     'ACE inhibitor (post-MI with reduced EF)',
     'RAMIPRIL (AIRE/SAVE evidence). Start 2.5mg twice daily, target 5mg twice daily (or 10mg daily). Also add: EPLERENONE 50mg (EPHESUS — post-MI with EF <40%). Both ACEi and aldosterone antagonist are indicated. Check K+ and creatinine before starting each.'],
    ['Patient with HFrEF, EF 30%, already on lisinopril 20mg, bisoprolol, spironolactone 25mg. What further evidence-based treatment should be added?',
     'Sacubitril/valsartan (Entresto) — ARNI replacing the ACEi; plus SGLT2 inhibitor',
     'PARADIGM-HF: replace lisinopril with sacubitril/valsartan (must stop lisinopril 36h before starting Entresto — angioedema risk if combined). Add empagliflozin or dapagliflozin (SGLT2 inhibitor). The "Fantastic Four": ARNI + beta-blocker + MRA + SGLT2i.'],
    ['50-year-old man, hypertension resistant to 3 drugs (amlodipine + ramipril + indapamide). K+ 3.2. BP 175/100. Slight muscle weakness.',
     'Primary hyperaldosteronism (Conn\'s syndrome) — suspected from hypokalaemia + resistant hypertension',
     'ALDOSTERONE:RENIN RATIO (ARR) — the screening test. High aldosterone + LOW renin (suppressed) = primary hyperaldosteronism. Confirm with CT adrenals. If unilateral adenoma: adrenalectomy (curative). If bilateral hyperplasia: SPIRONOLACTONE (medical management). ADD SPIRONOLACTONE 25mg immediately — will correct K+ and BP dramatically.'],
    ['35-year-old woman with T1DM, uACR 25 mg/mmol (raised — microalbuminuria), BP 124/76 (normal). What do you do?',
     'Start ACEi despite normal BP — to protect kidneys (diabetic nephropathy)',
     'RAMIPRIL (or any ACEi) — start immediately for NEPHROPROTECTION even though BP is normal. Evidence: Lewis trial (captopril in T1DM). Target: reduce uACR below 3 or reduce by 50%. This is the cornerstone of preventing progression from microalbuminuria to overt nephropathy.'],
    ['Cirrhotic patient with tense ascites. Currently on 80mg furosemide. Urine Na+ low. K+ 3.0.',
     'Secondary hyperaldosteronism in cirrhosis — inadequate spironolactone',
     'The treatment of ascites in cirrhosis: SPIRONOLACTONE (first line) + furosemide in 100:40 ratio. The patient currently has only furosemide — add SPIRONOLACTONE 100mg initially. The low K+ and low urine Na+ both indicate high aldosterone state. Spironolactone blocks aldosterone → Na+ excretion + K+ retention + reduces ascites.'],
    ['PACES: 65-year-old woman with peripheral oedema, breathlessness, and raised JVP. She asks why she is on "so many heart tablets."',
     'Heart failure (HFrEF) — explaining her medications including ACEi/ARNI',
     'EXPLAIN in lay terms: "Your heart is not pumping as strongly as it should. Ramipril works by relaxing the blood vessels, which means your heart does not have to work as hard to push blood through them. It also reduces fluid build-up. Studies have shown it helps the heart work better over time and reduces the chance of being admitted to hospital. A common side effect is a dry cough — please tell us if that happens." Then demonstrate you know the monitoring: "We check your blood tests, including kidney function and potassium levels, regularly to make sure the drug is working safely."'],
    ['Patient on dual ACEi + ARB for nephropathy. Which trial stopped this practice?',
     'ONTARGET trial (2008)',
     'ONTARGET: telmisartan alone = ramipril for CV outcomes. TELMISARTAN + RAMIPRIL = NO extra CV benefit + more hypotension, AKI, and hyperkalaemia. DO NOT COMBINE ACEi + ARB. Exception: some proteinuric CKD specialists still use combination — but not standard care and not recommended in guidelines.'],
    ['New diagnosis of HFrEF in a 45-year-old South Asian man. He is intolerant of ACEi (dry cough). Examiner asks: what RAAS drug do you prescribe?',
     'ARB — candesartan or valsartan for HFrEF in ACEi-intolerant patients',
     'CANDESARTAN: CHARM-Alternative trial — candesartan in HFrEF patients who could not tolerate ACEi → reduced CV death and HF hospitalisation. Alternatively: sacubitril/VALSARTAN (Entresto) — contains valsartan (ARB) + neprilysin inhibitor. No cough (bradykinin not affected by ARBs). Same K+ and renal monitoring applies.'],
]
story.append(plain_table(mrcp_table, [CW*0.28, CW*0.22, CW*0.50]))
divider(story)

# ── SECTION 14: MINIMAL RESOURCES + PACES ─────────────────────────────────────
sec_header('Section 14: Minimal Resources & PACES Station Guide', story)

min_table = [
    ['Clinical situation', 'Available resources', 'What to do', 'When to refer'],
    ['Starting ACEi in hypertension\n(community / limited labs)',
     'BP measurement + basic urine dipstick + clinical assessment',
     '1. Check urine dipstick for proteinuria (suggest CKD) and blood (suggest renovascular disease). 2. Listen for renal bruits (if audible over renal angles: suspect RAS — DO NOT start ACEi until imaged). 3. Clinical signs of dehydration or HF (if severely dehydrated: correct before starting). 4. Start ramipril 1.25-2.5mg once daily. 5. Review BP in 2-4 weeks. Warn patient about cough (explain to come back if cough starts) and the rare risk of lip/tongue swelling (explain to call emergency services immediately).',
     'Any renal bruit. Bilateral oedema suggesting HF. Suspected secondary hypertension. K+ raised (>5.0) on any available blood test.'],
    ['Monitoring on ACEi\n(limited access to regular labs)',
     'Creatinine + K+ at start and 1 month later',
     '1. Baseline creatinine and K+ before starting. 2. Recheck at 2 weeks and 1 month. 3. If creatinine has risen by more than 30%: STOP ACEi, investigate for RAS. 4. If K+ has risen above 5.5: STOP ACEi, review diet and co-medications. 5. Establish "sick day" rules — give written instructions: "If you have severe vomiting or diarrhoea for >24h, hold your ramipril, diuretic, and any NSAID until you are eating and drinking normally again."',
     'Creatinine rise >30%. K+ >5.5. Patient with recurrent AKI episodes.'],
    ['Identifying ACEi-induced cough\n(history-taking)',
     'Clinical history only',
     '1. Ask specifically: "Have you developed any new cough since starting the blood pressure tablet?" 2. Characterise: dry, tickling, non-productive, worse at night — strongly suggests ACEi cough. 3. Timing: onset weeks to months after starting. 4. If yes and consistent with ACEi cough: STOP ACEi, switch to ARB (losartan 50mg or candesartan 8mg). 5. Confirm: cough resolves within 4 weeks of stopping ACEi.',
     'Cough not resolving after stopping ACEi (investigate alternative causes: GORD, post-nasal drip, asthma, malignancy, ACEi-independent cause).'],
]
story.append(plain_table(min_table, [CW*0.16, CW*0.15, CW*0.42, CW*0.27]))

story.append(Spacer(1,8))
story.append(bp('<b>PACES Station Guide — RAAS and cardiovascular stations:</b>'))
paces_table = [
    ['Station', 'Scenario', 'What to examine', 'Presentation style'],
    ['Station 3 — Cardiovascular examination',
     'Patient with heart failure on multiple medications. Examiner asks you to comment on findings and management.',
     'JVP: raised (measure in cm above sternal angle). Apex beat: displaced laterally (dilated LV). Heart sounds: S3 gallop (third heart sound = volume overload sign of HF). Murmurs: mitral regurgitation (common in dilated HF). Peripheral oedema: pitting to which level. Basal crackles. Signs of cardiac cachexia: weight loss, muscle wasting.',
     '"This patient has signs consistent with decompensated heart failure: elevated JVP at Xcm, displaced apex, S3, and bilateral pitting oedema to the knee. Management includes optimisation of their HFrEF medications — if not already on it, I would start an ACEi (or ARNI if tolerating well) and titrate to the maximum tolerated dose, ensure they are on a beta-blocker and mineralocorticoid receptor antagonist, and consider an SGLT2 inhibitor. I would also ensure loop diuretic is optimised for symptom relief."'],
    ['Station 5 — Brief clinical consultation (medications)',
     'Patient asks: "My doctor wants me to start a new blood pressure tablet called ramipril — what is it and what should I watch out for?"',
     'Not examination — communication and counselling',
     '"Ramipril works by relaxing and widening your blood vessels, which takes pressure off your heart and reduces your blood pressure. It is also very good at protecting your kidneys, especially if you have diabetes. There are a few things to look out for: the most common is a dry, persistent cough — about 1 in 10 people get this. If it bothers you, come and tell us and we can switch to a different type. Much rarer but more serious: if you ever notice swelling of your lips, tongue or throat, stop the tablet immediately and call 999. We will do a blood test in a couple of weeks to make sure your kidneys and potassium level are fine. Also, please avoid anti-inflammatory painkillers like ibuprofen while on this tablet — use paracetamol instead."'],
    ['Station 1 or 5 — Abdominal examination in hypertensive patient',
     'Hypertensive patient with possible secondary cause. Renal bruit or adrenal mass suspected.',
     'Listen over renal angles (just below costal margin, lateral to spine) with bell of stethoscope — renal bruit (blowing systolic-diastolic murmur suggests RAS). Palpate for adrenal/renal mass. Measure BP in both arms (difference >15 mmHg suggests subclavian stenosis). Visual field assessment (pituitary adenoma causing Cushing\'s — secondary hypertension with raised cortisol also activates RAAS).',
     '"I found a bruit over the right renal angle in this hypertensive patient. This raises the possibility of right renal artery stenosis as a cause of secondary hypertension. I would arrange a renal Doppler ultrasound as the initial non-invasive investigation, and if confirmed, CT/MR angiography for anatomical detail and planning of possible angioplasty. Importantly, I would NOT start an ACEi or ARB until bilateral RAS is excluded — risk of precipitating AKI."'],
]
story.append(plain_table(paces_table, [CW*0.13, CW*0.17, CW*0.30, CW*0.40]))

story.append(Spacer(1,10))

# ── MASTER MEMORY SUMMARY ─────────────────────────────────────────────────────
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
    [Paragraph('RAAS & ACEi MASTER SUMMARY', sGrnB)],
    [Paragraph('RAAS SEQUENCE: Low BP/volume -> Renin (kidney JG cells) -> Angiotensinogen (liver) -> Angiotensin I (inactive) -> ACE (lung endothelium) -> Angiotensin II (potent vasoconstrictor) -> AT1 receptor -> Vasoconstriction + Adrenal Aldosterone + ADH release -> Na+/K+/H2O effects -> BP UP.', sGrn)],
    [Paragraph('ACE ALSO DEGRADES BRADYKININ: ACEi -> bradykinin accumulates -> vasodilation (good) + DRY COUGH (bad) + rare ANGIOEDEMA (dangerous). ARBs have NO cough (no effect on bradykinin). Switch to ARB for cough.', sGrn)],
    [Paragraph('ACEi INDICATIONS: Hypertension (especially T1/T2DM, CKD, young <55). HFrEF (all patients, CONSENSUS/SOLVD). Post-MI with reduced EF (AIRE, SAVE, HOPE). Diabetic nephropathy. CKD with proteinuria. Secondary stroke prevention (PROGRESS with perindopril+indapamide).', sGrn)],
    [Paragraph('ACEi ADVERSE EFFECTS: COUGH (10-40%, bradykinin, switch to ARB). ANGIOEDEMA (<0.5%, bradykinin, stop permanently). HYPERKALAEMIA (reduced aldosterone, monitor K+). FIRST-DOSE HYPOTENSION (start low). AKI in bilateral RAS (creatinine >30% rise = STOP). TERATOGENICITY (all trimesters, absolute CI in pregnancy).', sGrn)],
    [Paragraph('ACEi ABSOLUTE CONTRAINDICATIONS: Pregnancy. Bilateral renal artery stenosis. History of ACEi angioedema. (Relative: K+ >5.5, eGFR <30 = specialist supervision required.)', sGrn)],
    [Paragraph('MONITORING: Check creatinine + K+ at baseline, 2 weeks, 1 month, then 6-monthly. ACCEPT: creatinine rise up to 30% (expected). ACCEPT: K+ up to 5.5 mmol/L. STOP if: creatinine >30% rise or K+ >5.5. Sick-day rules: hold ACEi + diuretic + NSAID during dehydrating illness.', sGrn)],
    [Paragraph('PRODRUGS: Ramipril, Enalapril, Perindopril, Fosinopril, Trandolapril (converted to -prilat). ACTIVE: Lisinopril and Captopril (no conversion needed). In liver failure: use Lisinopril. In CKD: use Fosinopril (dual renal + hepatic elimination).', sGrn)],
    [Paragraph('ARBs (SARTANS): Block AT1 receptor. No effect on bradykinin (no cough, less angioedema). Same K+ and AKI risks as ACEi. ONTARGET: do NOT combine ACEi + ARB. Use ARBs when ACEi intolerant (cough). Candesartan (CHARM), Valsartan (Val-HeFT), Losartan (RENAAL, LIFE), Irbesartan (IDNT).', sGrn)],
    [Paragraph('ALDOSTERONE ANTAGONISTS: Spironolactone (RALES: 30% mortality reduction in HFrEF) + Eplerenone (EPHESUS: post-MI with EF<40%; EMPHASIS-HF: mild HFrEF). Side effects: HYPERKALAEMIA (monitor K+), GYNAECOMASTIA (spironolactone only). Use eplerenone if gynaecomastia develops.', sGrn)],
    [Paragraph('CONN\'S SYNDROME: Primary hyperaldosteronism. High aldosterone + SUPPRESSED RENIN (key). Hypertension + hypokalaemia + resistant to 3 drugs. Diagnose with ARR (aldosterone:renin ratio). CT adrenals. Unilateral adenoma = adrenalectomy. Bilateral hyperplasia = SPIRONOLACTONE.', sGrn)],
    [Paragraph('ENTRESTO (sacubitril/valsartan): PARADIGM-HF: 20% better than enalapril in HFrEF. REPLACES ACEi (never combine). Stop ACEi 36h before starting. The Fantastic Four: ARNI + beta-blocker + MRA + SGLT2i = standard of care in HFrEF.', sGrn)],
    [Paragraph('TRIPLE WHAMMY: ACEi + diuretic + NSAID = AKI. Tell all patients: sick-day rules = hold all 3 during vomiting/diarrhoea. Use paracetamol not ibuprofen. Do not start with bilateral RAS. Lithium levels rise on ACEi (monitor). K+ supplements dangerous with ACEi (hyperkalaemia).', sGrn)],
]
innerG = Table(gRows, colWidths=[CW-4])
innerG.setStyle(gTS1)
outerG = Table([[innerG]], colWidths=[CW])
outerG.setStyle(gTSO)
story.append(outerG)
story.append(Spacer(1,8))

# ── BUILD ──────────────────────────────────────────────────────────────────────
doc.build(story)
print('SUCCESS: /mnt/user-data/outputs/RAAS_ACEi_MRCP_Note.pdf generated.')
