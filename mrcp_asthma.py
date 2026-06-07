"""
MRCP REVISION NOTE: Asthma, Laryngeal Spasm & Airway Disease
Page size: A3 Portrait (297mm x 420mm) for readable, spacious layout.
PIL diagram rule: fB=28px, fS=22px, fXS=17px — renders ~22/17/13pt on A3.
"""
import os
from io import BytesIO
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, Image as RLImage)
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageDraw, ImageFont

OUT = '/mnt/user-data/outputs/Asthma_Laryngeal_MRCP_Note.pdf'
FONT_DIR = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('DV',   FONT_DIR + 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DV-B', FONT_DIR + 'DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DV-I', FONT_DIR + 'DejaVuSansMono-Oblique.ttf'))
pdfmetrics.registerFont(TTFont('DV-BI',FONT_DIR + 'DejaVuSansMono-BoldOblique.ttf'))

# Colours
TEAL   = HexColor('#0d5c63'); TEAL_M  = HexColor('#1a8a94')
TEAL_L = HexColor('#e0f4f5'); TEAL_XL = HexColor('#f0fafb')
AMBER  = HexColor('#fff3cd'); AMBER_B = HexColor('#e6a817')
GREEN_L= HexColor('#d4edda'); GREEN_D = HexColor('#28a745')
RED_L  = HexColor('#fde8e8'); RED_D   = HexColor('#c0392b')
ORA_L  = HexColor('#fef3e2'); ORA_D   = HexColor('#d4640a')
BLUE_L = HexColor('#e8f4fd'); BLUE_D  = HexColor('#2471a3')
PUR_L  = HexColor('#f5eef8'); PUR_D   = HexColor('#7d3c98')
NAVY   = HexColor('#1a1a2e'); WHITE   = HexColor('#ffffff')

# A3 portrait geometry  (297mm wide x 420mm tall)
PAGE_W, PAGE_H = A3          # 841.89pt x 1190.55pt
MARGIN = 22*mm               # 22mm each side
CW = PAGE_W - 2*MARGIN       # ~700pt content width

doc = SimpleDocTemplate(OUT, pagesize=A3,
      leftMargin=MARGIN, rightMargin=MARGIN,
      topMargin=MARGIN, bottomMargin=MARGIN)

# Styles — slightly larger on A3
sTitle = ParagraphStyle('TT', fontName='DV-B', fontSize=26, leading=32,
         textColor=HexColor('#0d5c63'), spaceAfter=5, alignment=1)
sSub   = ParagraphStyle('TS', fontName='DV-I', fontSize=12, leading=16,
         textColor=HexColor('#1a8a94'), spaceAfter=3, alignment=1)
sH1    = ParagraphStyle('H1', fontName='DV-B', fontSize=15, leading=20,
         textColor=HexColor('#0d5c63'), spaceBefore=10, spaceAfter=5)
sH2    = ParagraphStyle('H2', fontName='DV-B', fontSize=11, leading=15,
         textColor=HexColor('#0d5c63'), spaceAfter=3)
sBody  = ParagraphStyle('Bo', fontName='DV', fontSize=10, leading=15,
         textColor=HexColor('#1a1a2e'), spaceAfter=4)
sPro   = ParagraphStyle('Pr', fontName='DV-I', fontSize=10, leading=15,
         textColor=HexColor('#1a8a94'), spaceAfter=5)
sImg   = ParagraphStyle('Im', fontName='DV-I', fontSize=9, leading=13,
         textColor=HexColor('#555555'), spaceAfter=5, alignment=1)
sAlert = ParagraphStyle('Al', fontName='DV-B', fontSize=10, leading=14,
         textColor=HexColor('#721c24'), spaceAfter=0)
sMem   = ParagraphStyle('MH', fontName='DV-B', fontSize=10, leading=14,
         textColor=HexColor('#856404'), spaceAfter=0)

def bp(text, st=None):
    return Paragraph(text, st or sBody)

def sec_header(title, story):
    story.append(Spacer(1, 8))
    story.append(Paragraph(title, sH1))

def divider(story):
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width=CW, thickness=0.6, color=TEAL_M, spaceAfter=6))

def plain_table(data, widths, header=True):
    rows = []
    for i, row in enumerate(data):
        st = sH2 if (i == 0 and header) else sBody
        new_row = []
        for c in row:
            if hasattr(c, 'wrap'):
                new_row.append(c)
            else:
                new_row.append(Paragraph(str(c), st))
        rows.append(new_row)
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0, splitByRow=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),TEAL_L),
        ('TEXTCOLOR',(0,0),(-1,0),TEAL),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,TEAL_XL]),
        ('GRID',(0,0),(-1,-1),0.6,TEAL_M),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    return t

def alert_box(text, story):
    t = Table([[Paragraph(f'<b>ALERT: {text}</b>', sAlert)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),RED_L),
        ('BOX',(0,0),(-1,-1),2,RED_D),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,6))

def info_box(text, story, color=None, border=None):
    bg = color or BLUE_L; bd = border or BLUE_D
    t = Table([[Paragraph(text, sBody)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),bg),
        ('BOX',(0,0),(-1,-1),2,bd),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,6))

def image_search_box(term, site, story):
    txt = f'IMAGE: Search <b>"{term}"</b> on <b>{site}</b> to see a picture of this.'
    t = Table([[Paragraph(txt, sImg)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),HexColor('#f8f9fa')),
        ('BOX',(0,0),(-1,-1),1,HexColor('#adb5bd')),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story.append(t); story.append(Spacer(1,5))

def professor_says(text, story):
    t = Table([[Paragraph(f'<i>Professor says: "{text}"</i>', sPro)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),TEAL_XL),
        ('BOX',(0,0),(-1,-1),1.5,TEAL_M),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,6))

def memory_hook(text, story):
    t = Table([[Paragraph(f'MEMORY: {text}', sMem)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),AMBER),
        ('BOX',(0,0),(-1,-1),2,AMBER_B),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,6))

# ── PIL helpers ───────────────────────────────────────────────────────────────
# On A3 with CW~700pt, PIL canvas W=900px → scale=0.778 pt/px
# fB=28px → 21.8pt  fS=22px → 17.1pt  fXS=17px → 13.2pt  — all readable

def arr_r(draw, x, y, length=44, col='#0d5c63', w=3):
    draw.line([(x,y),(x+length,y)], fill=col, width=w)
    draw.polygon([(x+length,y),(x+length-10,y-6),(x+length-10,y+6)], fill=col)

def arr_d(draw, x, y, length=32, col='#0d5c63', w=3):
    draw.line([(x,y),(x,y+length)], fill=col, width=w)
    draw.polygon([(x,y+length),(x-6,y+length-10),(x+6,y+length-10)], fill=col)

def i2r(img, W):
    scale = W / img.width
    nH = int(img.height * scale)
    img = img.resize((int(W), nH), Image.LANCZOS)
    buf = BytesIO(); img.save(buf, 'PNG'); buf.seek(0)
    return RLImage(buf, width=W, height=nH)

def load_fonts(sizes):
    fonts = {}
    for name, sz in sizes.items():
        try:
            if 'B' in name:
                fonts[name] = ImageFont.truetype(FONT_DIR+'DejaVuSans-Bold.ttf', sz)
            else:
                fonts[name] = ImageFont.truetype(FONT_DIR+'DejaVuSans.ttf', sz)
        except:
            fonts[name] = ImageFont.load_default()
    return fonts

print('Building PIL diagrams...')

# ── TEXT-SAFE DIAGRAM TOOLKIT ────────────────────────────────────────────────
# Definitive fix for diagram text overlap: every string is measured with
# draw.textlength(), wrapped to fit its box, and box/card height is computed
# FROM the wrapped line count — never assumed. Boxes stack by tracking the
# returned bottom-y, so overlap is structurally impossible.

def text_w(draw, s, font):
    return draw.textlength(s, font=font)

def wrap_text(draw, text, font, max_width):
    out = []
    for para in str(text).split('\n'):
        if para.strip() == '':
            out.append('')
            continue
        words = para.split(' ')
        cur = ''
        for w in words:
            cand = w if not cur else cur + ' ' + w
            if text_w(draw, cand, font) <= max_width or not cur:
                cur = cand
            else:
                out.append(cur)
                cur = w
        if cur:
            out.append(cur)
    return out

def lh(font, factor=1.32):
    return int(font.size * factor)

def draw_block(draw, x, y, text, font, fill, max_width, align='left', extra_gap=0):
    lines = wrap_text(draw, text, font, max_width)
    step = lh(font) + extra_gap
    cy = y
    for ln in lines:
        if align == 'center':
            w = text_w(draw, ln, font)
            draw.text((x + (max_width - w) / 2, cy), ln, font=font, fill=fill, anchor='la')
        else:
            draw.text((x, cy), ln, font=font, fill=fill, anchor='la')
        cy += step
    return cy

def card(draw, x0, x1, y, title, body, f_title, f_body, accent, body_bg, pad=13, line_gap=3):
    """Stacked card: coloured title bar (wrapped) + body box (wrapped).
    Height is fully computed from wrapped content — never guessed.
    Returns the bottom-y so the next card stacks below with a guaranteed gap."""
    inner_w = (x1 - x0) - 2 * pad
    title_lines = wrap_text(draw, title, f_title, inner_w)
    body_lines = wrap_text(draw, body, f_body, inner_w) if body else []
    bar_h = len(title_lines) * lh(f_title) + 16
    body_h = (len(body_lines) * (lh(f_body) + line_gap) + 2 * pad) if body_lines else 0

    draw.rectangle([x0, y, x1, y + bar_h], fill=accent, outline=accent)
    draw_block(draw, x0 + pad, y + 8, title, f_title, '#ffffff', inner_w)
    if body_lines:
        draw.rectangle([x0, y + bar_h, x1, y + bar_h + body_h], fill=body_bg, outline=accent, width=3)
        draw_block(draw, x0 + pad, y + bar_h + pad, body, f_body, '#2b2b2b', inner_w, extra_gap=line_gap)
    return y + bar_h + body_h

def header_band(draw, W, title, font, pad_x, accent='#0d5c63', text_color='#ffffff'):
    """Title band whose height is computed from the WRAPPED line count — a
    long title can never spill out of (or be clipped by) its coloured bar."""
    inner_w = W - 2 * pad_x
    lines = wrap_text(draw, title, font, inner_w)
    bar_h = len(lines) * lh(font) + 32
    draw.rectangle([0, 0, W - 1, bar_h], fill=accent)
    draw_block(draw, pad_x, 16, title, font, text_color, inner_w, align='center')
    return bar_h

def finish(img, draw, W, bottom_y, footer_text, f_xs, accent='#0d5c63'):
    """Dark footer band whose height is computed from the WRAPPED line count,
    then crop the canvas to the REAL content height (no dead space, and the
    footer can never spill past the bottom edge)."""
    inner_w = W - 60
    lines = wrap_text(draw, footer_text, f_xs, inner_w)
    foot_h = len(lines) * lh(f_xs) + 20
    top = bottom_y + 14
    draw.rectangle([0, top, W - 1, top + foot_h], fill=accent)
    draw_block(draw, 30, top + 10, footer_text, f_xs, '#ffffff', inner_w, align='center')
    return img.crop((0, 0, W, top + foot_h + 6))

print('Building PIL diagrams (text-safe card layout)...')

# ── PIL 1: Airway Anatomy — stacked cards, one per anatomical level ─────────
def make_airway_anatomy():
    W, H_MAX = 900, 1500
    f = load_fonts({'T': 24, 'B': 17, 'XS': 14})
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    pad_x = 46
    x0, x1 = pad_x, W - pad_x
    hh = header_band(draw, W, 'AIRWAY ANATOMY: WHERE EACH CONDITION OCCURS', f['T'], pad_x)

    levels = [
        ('#c0392b', '#fde8e8', 'NOSE / MOUTH — entry point for air and allergens',
         'Triggers enter here first: pollens, house dust mite, mould spores, pet dander.'),
        ('#d4640a', '#fef3e2', 'PHARYNX (throat) — shared passage for food and air',
         'Post-nasal drip: mucus running down the back of the throat triggers cough and bronchoconstriction.'),
        ('#7d3c98', '#f5eef8', 'LARYNX (voice box) — the UPPER airway begins here',
         'Contains the vocal cords. Conditions found here: laryngospasm, vocal cord dysfunction (VCD), and laryngeal oedema (anaphylaxis, hereditary angioedema, ACE-inhibitor angioedema).'),
        ('#b8860b', '#fff3cd', 'TRACHEA (windpipe) — a rigid cartilage tube',
         'Cartilage rings hold it open — it cannot collapse. Tracheal stenosis causes a FIXED obstruction: stridor on breathing in AND out.'),
        ('#2471a3', '#e8f4fd', 'BRONCHI — the main branching airway tubes',
         'Left and right bronchus, branching further into lobes. Large-airway obstruction here: foreign body, tumour, or a large mucus plug.'),
        ('#28a745', '#d4edda', 'BRONCHIOLES + ALVEOLI — the LOWER airway, where gas exchange happens',
         'The tiniest airways — exactly where ASTHMA and allergic bronchitis occur: bronchoconstriction, inflammation, and mucus plugging.'),
    ]
    yy = hh + 22
    for accent, bg, title, body in levels:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 18

    final = finish(img, draw, W, yy,
        'UPPER AIRWAY (larynx and above) → STRIDOR on breathing IN   |   LOWER AIRWAY (below larynx) → WHEEZE on breathing OUT',
        f['XS'])
    return i2r(final, CW)

# ── PIL 2: What happens inside the airway during an asthma attack ───────────
def make_asthma_path():
    W, H_MAX = 900, 1700
    f = load_fonts({'T': 24, 'B': 17, 'XS': 14})
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    pad_x = 46
    x0, x1 = pad_x, W - pad_x
    hh = header_band(draw, W, 'WHAT HAPPENS INSIDE THE AIRWAY DURING AN ASTHMA ATTACK', f['T'], pad_x)

    panel_top, panel_h = hh + 22, 230
    mid_gap = 32
    lx0, lx1 = x0, x0 + (x1 - x0 - mid_gap) // 2
    rx0, rx1 = lx1 + mid_gap, x1
    cy = panel_top + (panel_h - 50) // 2

    draw.rectangle([lx0, panel_top, lx1, panel_top + panel_h], outline='#0d5c63', width=3)
    cxL = lx0 + (lx1 - lx0) // 2
    draw.ellipse([cxL - 70, cy - 70, cxL + 70, cy + 70], outline='#2471a3', width=10)
    draw.ellipse([cxL - 46, cy - 46, cxL + 46, cy + 46], fill='#ffffff')
    draw_block(draw, lx0 + 16, panel_top + panel_h - 36,
               'NORMAL: wide-open lumen — air flows freely', f['XS'], '#1a1a2e',
               (lx1 - lx0) - 32, align='center')

    draw.rectangle([rx0, panel_top, rx1, panel_top + panel_h], outline='#c0392b', width=3)
    cxR = rx0 + (rx1 - rx0) // 2
    draw.ellipse([cxR - 70, cy - 70, cxR + 70, cy + 70], outline='#c0392b', width=10)
    draw.ellipse([cxR - 46, cy - 46, cxR + 46, cy + 46], fill='#e8a98c')
    draw.ellipse([cxR - 22, cy - 22, cxR + 22, cy + 22], fill='#7d3c98')
    draw_block(draw, rx0 + 16, panel_top + panel_h - 36,
               'ASTHMA ATTACK: wall muscle squeezes, lining swells, mucus blocks the centre',
               f['XS'], '#1a1a2e', (rx1 - rx0) - 32, align='center')

    yy = panel_top + panel_h + 26
    cards = [
        ('#2471a3', '#e8f4fd', '① BRONCHOCONSTRICTION — smooth muscle in the airway wall contracts',
         'The ring of smooth muscle wrapped around each airway squeezes tight, narrowing the tube air must pass through. This is the FASTEST of the three changes — the one that bronchodilators (salbutamol) reverse within minutes.'),
        ('#7d3c98', '#f5eef8', '② MUCOSAL OEDEMA — the airway lining becomes inflamed and swollen',
         'Eosinophils, mast cells and Th2 lymphocytes flood the wall, releasing histamine and leukotrienes. The lining swells inward, narrowing the lumen further. This is what inhaled corticosteroids treat — they switch off the inflammatory cascade.'),
        ('#b8860b', '#fff3cd', '③ MUCUS PLUGGING — thick, sticky mucus blocks the airway centre',
         'Goblet cells overproduce thick mucus that the cilia cannot clear. In fatal asthma at post-mortem the airways are characteristically packed solid with mucus plugs — one reason a severe attack can become eerily silent.'),
        ('#c0392b', '#fde8e8', 'THE RESULT — turbulent, restricted airflow the patient must work hard to push through',
         'All three changes occur together and reinforce each other. The patient must generate far greater respiratory effort to move air through the narrowed tube — heard as wheeze, and felt as breathlessness and chest tightness.'),
    ]
    for accent, bg, title, body in cards:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 16

    final = finish(img, draw, W, yy,
        'MEMORY DEVICE — the three culprits spell "C.O.M.": Constriction, Oedema, Mucus — all three must be treated together',
        f['XS'])
    return i2r(final, CW)

# ── PIL 3: Severity grading of an acute asthma attack ───────────────────────
def make_severity():
    W, H_MAX = 900, 1500
    f = load_fonts({'T': 24, 'B': 17, 'XS': 14})
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    pad_x = 46
    x0, x1 = pad_x, W - pad_x
    hh = header_band(draw, W, 'GRADING THE SEVERITY OF AN ACUTE ASTHMA ATTACK (BTS / SIGN)', f['T'], pad_x)

    levels = [
        ('#28a745', '#d4edda', 'MODERATE EXACERBATION',
         'PEFR 50–75% of best/predicted. Increasing symptoms but no features of acute severe asthma. SpO2 ≥ 92% on air. ACTION: nebulised/inhaled salbutamol, oral prednisolone 40–50 mg, reassess within 1 hour.'),
        ('#d4640a', '#fef3e2', 'ACUTE SEVERE ASTHMA',
         'ANY of: PEFR 33–50% of best/predicted, respiratory rate ≥ 25/min, heart rate ≥ 110/min, or inability to complete sentences in one breath. SpO2 ≥ 92%. ACTION: admit, give oxygen, nebulised salbutamol + ipratropium, oral or IV steroids, monitor closely.'),
        ('#c0392b', '#fde8e8', 'LIFE-THREATENING ASTHMA — any ONE of these features',
         'PEFR < 33% of best/predicted. SpO2 < 92% or PaO2 < 8 kPa. A "normal" PaCO2 (4.6–6.0 kPa) — a worrying sign of fatigue, NOT improvement. Silent chest, cyanosis, feeble respiratory effort, arrhythmia, hypotension, exhaustion, confusion or coma. ACTION: call ICU/anaesthetics now — IV magnesium sulfate, IV aminophylline, consider intubation.'),
        ('#7d3c98', '#f5eef8', 'NEAR-FATAL ASTHMA',
         'Raised PaCO2 and/or needing mechanical ventilation with raised inflation pressures. CO2 is rising because the patient can no longer sustain the work of breathing — a pre-arrest state needing immediate senior critical-care input.'),
    ]
    yy = hh + 22
    for accent, bg, title, body in levels:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 18

    final = finish(img, draw, W, yy,
        'KEY TRAP — a "normal" PaCO2 during an asthma attack is NOT reassuring: it means the patient is tiring and heading towards respiratory failure',
        f['XS'])
    return i2r(final, CW)

# ── PIL 4a: Differential map — the four classic asthma mimics ───────────────
def make_diff_map():
    W, H_MAX = 900, 1300
    f = load_fonts({'T': 24, 'B': 17, 'XS': 14})
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    pad_x = 46
    x0, x1 = pad_x, W - pad_x
    hh = header_band(draw, W, 'ALL POSSIBLE DIAGNOSES AT A GLANCE — UPPER vs LOWER AIRWAY CAUSES', f['T'], pad_x)

    diffs = [
        ('#2471a3', '#e8f4fd', 'ASTHMA — a LOWER-airway problem',
         'Episodic wheeze, cough (often nocturnal/early-morning), chest tightness — triggered by allergens, exercise, cold air or viral infection. Wheeze is heard on EXPIRATION. Reversible with a bronchodilator; confirmed by PEFR variability or spirometry with reversibility.'),
        ('#7d3c98', '#f5eef8', 'VOCAL CORD DYSFUNCTION / INDUCIBLE LARYNGEAL OBSTRUCTION (VCD/ILO) — an UPPER-airway problem',
         'Mimics asthma but does NOT respond to asthma treatment. Sudden breathlessness with noise localised to the THROAT, normal oxygen saturation. Stridor is heard mainly on INSPIRATION. Diagnosed by laryngoscopy showing paradoxical vocal-cord closure on breathing in.'),
        ('#c0392b', '#fde8e8', 'ANAPHYLAXIS — a MEDICAL EMERGENCY',
         'Rapid onset after allergen exposure (food, drug, sting). Laryngeal/lingual oedema causing stridor, plus urticaria, angioedema, hypotension and bronchospasm. Treat immediately: IM adrenaline 0.5 mg (1:1000), high-flow oxygen, IV fluids, remove the trigger.'),
        ('#d4640a', '#fef3e2', 'LARYNGOSPASM',
         'A sudden, brief, involuntary spasm of the vocal cords — triggered by reflux, irritant inhalation, or during anaesthesia/intubation. A frightening total inability to breathe in, with stridor, resolving within seconds to minutes as the spasm releases.'),
    ]
    yy = hh + 22
    for accent, bg, title, body in diffs:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 16

    final = finish(img, draw, W, yy,
        'STRIDOR on breathing IN = upper airway (larynx/trachea)   |   WHEEZE on breathing OUT = lower airway (bronchi/bronchioles)',
        f['XS'])
    return i2r(final, CW)

# ── PIL 4b: Differential map — the quieter mimics + the master question ─────
def make_diff_map2():
    W, H_MAX = 900, 1500
    f = load_fonts({'T': 24, 'B': 17, 'XS': 14})
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    pad_x = 46
    x0, x1 = pad_x, W - pad_x
    hh = header_band(draw, W, 'DIFFERENTIAL DIAGNOSIS MAP — DISTINGUISHING FEATURES, PATTERN BY PATTERN', f['T'], pad_x)

    diffs = [
        ('#28a745', '#d4edda', 'ALLERGIC BRONCHOPULMONARY ASPERGILLOSIS (ABPA)',
         'A hypersensitivity reaction to Aspergillus fumigatus colonising the airways of patients with asthma or cystic fibrosis. Look for: difficult-to-control wheeze, brown mucus plugs, eosinophilia, raised total IgE and Aspergillus-specific IgE, and central bronchiectasis on CT. Treated with oral corticosteroids ± itraconazole.'),
        ('#b8860b', '#fff3cd', 'HEREDITARY ANGIOEDEMA (HAE)',
         'A rare genetic disorder (C1-esterase-inhibitor deficiency) causing recurrent episodes of non-itchy, non-urticarial swelling of the face, lips, larynx and gut. Crucially it does NOT respond to adrenaline, antihistamines or steroids — it needs C1-inhibitor concentrate or icatibant. A family history is often present.'),
        ('#117a65', '#d7f0ec', 'EOSINOPHILIC BRONCHITIS',
         'Chronic cough WITHOUT wheeze or airflow obstruction — spirometry and PEFR variability are normal. Sputum shows eosinophilia. Responds well to inhaled corticosteroids. An important mimic to recognise whenever the spirometry simply does not fit an asthma label.'),
        ('#943126', '#f6dcd7', 'GASTRO-OESOPHAGEAL REFLUX (GERD)-INDUCED COUGH / WHEEZE',
         'Microaspirated acid reflux irritates the airway, triggering chronic cough, throat-clearing, nocturnal wheeze and laryngeal irritation — sometimes mistaken for asthma. Look for heartburn, a sour taste, and symptoms that worsen on lying flat or after meals. Responds to proton-pump inhibitors and lifestyle measures.'),
    ]
    yy = hh + 22
    for accent, bg, title, body in diffs:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 16

    yy = card(draw, x0, x1, yy + 6,
        'THE KEY QUESTION THAT SEPARATES THEM ALL',
        'WHERE is the noise coming from, and WHEN in the breathing cycle does it occur? Stridor on INSPIRATION → upper airway (larynx/trachea: VCD, anaphylaxis, laryngospasm, HAE). Wheeze on EXPIRATION → lower airway (bronchi/bronchioles: asthma, ABPA, eosinophilic bronchitis). Listen with your stethoscope over BOTH the trachea and the chest — the site of the loudest sound is your most powerful clinical clue.',
        f['B'], f['XS'], '#0d5c63', '#dff2f1')

    final = finish(img, draw, W, yy,
        'MEMORY DEVICE — "Not all that wheezes is asthma, and not all asthma wheezes": always ask WHERE and WHEN before you write the label "asthma"',
        f['XS'])
    return i2r(final, CW)

img_airway   = make_airway_anatomy()
img_asthpath = make_asthma_path()
img_severity = make_severity()
img_diffmap  = make_diff_map()
img_diffmap2 = make_diff_map2()
print('PIL diagrams done.')

# ─────────────────────────────────────────────────────────────────────────────
# STORY
# ─────────────────────────────────────────────────────────────────────────────
story = []

story.append(Paragraph('ACUTE ASTHMA, LARYNGEAL SPASM &amp; ALLERGIC AIRWAY DISEASE', sTitle))
story.append(Paragraph('Comprehensive MRCP Revision Note  |  Parts 1, 2 &amp; PACES', sSub))
story.append(Paragraph('All Causes of Recurrent Breathlessness in a Young Adult — From Zero to Expert', sSub))
story.append(Spacer(1, 10))
story.append(HRFlowable(width=CW, thickness=2.5, color=TEAL, spaceAfter=8))

# §1
sec_header('Section 1: The Clinical Scenario — Understanding This Patient', story)
professor_says('A 22-year-old woman. Childhood episodes of breathlessness. Similar episodes now for 4-5 days. Responds to inhaled and IV steroids. But keeps coming back. Sometimes only coughing. Sometimes completely breathless. Let us understand every possible cause — and solve this puzzle completely.', story)

story.append(bp('<b>What does this history tell us immediately?</b>'))
for pt in [
    '<b>Childhood episodes</b> → strongly suggests ATOPIC (allergic) disease — asthma, allergic rhinitis, eczema.',
    '<b>Responds to steroids</b> → confirms airway INFLAMMATION is part of the problem.',
    '<b>But keeps recurring</b> → either: the trigger is still present, the dose is not enough, inhaler technique is wrong, or a second diagnosis is being missed.',
    '<b>Sometimes cough only, sometimes breathless</b> → VARIABLE symptoms = hallmark of reversible airway obstruction = asthma pattern.',
    '<b>Female, 22 years old</b> → also consider VCD (vocal cord dysfunction — common in young women), premenstrual asthma, and HAE.',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 8))

story.append(img_diffmap)
story.append(bp('All possible diagnoses at a glance — upper vs lower airway causes', sImg))
story.append(Spacer(1, 8))

overview_table = [
    ['Condition','Key Sound','Responds to Salbutamol?','Responds to Steroids?','Key Test'],
    ['Asthma','Expiratory wheeze\n(breathing OUT)','YES — strongly','YES — strongly','Spirometry reversibility.\nPEFR diary. FeNO.'],
    ['VCD / ILO','Inspiratory STRIDOR\n(breathing IN)','NO','NO','Laryngoscopy during attack.\nFlow-volume loop.'],
    ['Laryngospasm','Silent or stridor.\nLasts seconds.','NO','NO','24h pH monitoring.\n(GERD link)'],
    ['Anaphylaxis /\nLaryngeal oedema','Stridor.\nRapid swelling.','NO','Partial only','Tryptase.\nSkin prick test.'],
    ['HAE','Stridor.\nSlow swelling\n(hours).','NO','NO — does NOT work','C4 level (LOW).\nC1-INH level.'],
    ['ABPA','Wheeze.\nBrownish mucus plugs.','Partial','YES','Total IgE > 1000.\nAspergillus IgE.\nCT thorax.'],
    ['Eosinophilic\nBronchitis','Cough only.\nNo wheeze.','NO obstruction','YES — ICS works well','FeNO raised.\nNormal spirometry.\nSputum eosinophils.'],
    ['GERD-induced','Cough. Hoarse.\nNight gasping.','No','Partial','24h pH monitoring.\nPPI trial.'],
]
story.append(plain_table(overview_table,[CW*0.14,CW*0.14,CW*0.14,CW*0.14,CW*0.44]))
memory_hook('RECURRENT BREATHLESSNESS IN YOUNG WOMAN: Is the sound on BREATHING IN (stridor = upper airway = VCD/laryngeal) or BREATHING OUT (wheeze = lower airway = asthma)? Does salbutamol help? If NO → not asthma. Check C4 for HAE. Check GERD. Check anxiety/VCD.', story)
divider(story)

# §2
sec_header('Section 2: Anatomy — The Airway From Top to Bottom', story)
professor_says('Think of the airway as a tree. Wide trunk (trachea) branches into smaller and smaller twigs (bronchioles). Different conditions block different parts of this tree. Upper tree = stridor. Lower tree = wheeze.', story)

story.append(img_airway)
story.append(bp('Airway anatomy — each level, its structure, and which condition blocks it', sImg))
story.append(Spacer(1, 8))

story.append(bp('<b>Upper Airway (nose → larynx):</b>'))
for pt in [
    '<b>Nose and sinuses:</b> Air enters here. Warmed, moistened, filtered. Allergens (pollen, dust, mould) enter first. Allergic rhinitis starts here and can worsen asthma below.',
    '<b>Pharynx (FAR-inks):</b> Common passage for food and air. Post-nasal drip (mucus dripping down from a blocked nose) triggers cough and mild bronchoconstriction.',
    '<b>Larynx (LAIR-inks) = voice box:</b> Contains the vocal cords. They should open WIDE during breathing in. When they close abnormally = laryngospasm or VCD. Site of anaphylactic and HAE swelling.',
    '<b>Vocal cords:</b> Normal breathing = wide V-shape (open). VCD = close together (paradoxical closure during inspiration). Laryngeal oedema = swollen shut.',
    '<b>Epiglottis:</b> Flap above larynx. Closes during swallowing. Can swell in severe anaphylaxis.',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 6))

story.append(bp('<b>Lower Airway (trachea → alveoli):</b>'))
for pt in [
    '<b>Trachea (TRAY-kee-ah) = windpipe:</b> Main central tube, 10-12cm long. Cartilage rings hold it open — it does not collapse. Tracheal stenosis causes fixed obstruction (stridor on BOTH breathing in AND out).',
    '<b>Main bronchi:</b> Right and left. Right is wider and more vertical — foreign bodies go right more often.',
    '<b>Bronchioles (BRON-kee-oles):</b> Smallest airways. No cartilage — held open only by elastic recoil of surrounding lung. In asthma: their muscular walls squeeze shut (bronchoconstriction). This is where salbutamol acts.',
    '<b>Alveoli (al-VEE-oh-lie):</b> 300 million tiny air sacs. Where oxygen crosses into blood and CO2 crosses out.',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 6))

ul_table = [
    ['Feature','UPPER Airway Obstruction\n(Larynx and above)','LOWER Airway Obstruction\n(Bronchi and bronchioles)'],
    ['Sound','STRIDOR — harsh crowing noise.\nHeard on BREATHING IN\n(inspiratory).','WHEEZE — musical whistling.\nHeard on BREATHING OUT\n(expiratory).'],
    ['Conditions','Laryngospasm. VCD/ILO.\nLaryngeal oedema.\nAnaphylaxis. HAE.\nEpiglottitis.','Asthma. COPD.\nAllergic / eosinophilic bronchitis.\nABPA.'],
    ['Salbutamol effect','NO — salbutamol only acts on\nlower airway smooth muscle.\nCannot open the larynx.','YES — opens bronchioles.\nFEV1 improves > 12%\nafter salbutamol.'],
    ['Flow-volume loop','FLAT INSPIRATORY LIMB\n(cut off at top).','Concave EXPIRATORY limb\n(scooped shape below normal).'],
]
story.append(plain_table(ul_table,[CW*0.18,CW*0.41,CW*0.41]))
info_box('<b>KEY CLINICAL POINT:</b> Stridor = upper airway. Wheeze = lower airway. They are different sounds in different places. A patient with VCD makes a STRIDOR — not a wheeze. Salbutamol will NOT help. This is the most common reason VCD is misdiagnosed as asthma for years.', story)
image_search_box('flow volume loop VCD vs asthma inspiratory flattening comparison', 'Radiopaedia.org or Google Images', story)
memory_hook('STRIDOR = UPPER AIRWAY (larynx and above) = breathing IN. WHEEZE = LOWER AIRWAY (bronchioles) = breathing OUT. Salbutamol only helps LOWER airway. Upper airway obstruction = refer ENT / laryngoscopy.', story)
divider(story)

# §3
sec_header('Section 3: Asthma — Pathophysiology (How It Happens)', story)
professor_says('Asthma is the most common cause of recurrent breathlessness in young people. Understanding the mechanism tells you exactly why each drug works. This is a frequent MRCP Part 1 question.', story)

story.append(img_asthpath)
story.append(bp('Normal airway vs asthmatic airway — three simultaneous problems during every attack', sImg))
story.append(Spacer(1, 8))

story.append(bp('<b>Simple analogy first:</b>'))
story.append(bp('A normal airway is like a wide motorway. Cars (air) flow freely. In asthma, the road suddenly: (1) gets narrowed by roadworks (bronchoconstriction), (2) the road surface swells up (inflammation), and (3) sticky mud covers part of the road (mucus). All three happen at once.'))
story.append(Spacer(1, 5))

story.append(bp('<b>Step 1: Sensitisation — The First Exposure</b>'))
story.append(bp('A person with a genetic tendency (atopy) breathes in an allergen. Their immune system makes <b>IgE antibodies</b> specific to that allergen. These IgE molecules attach to <b>mast cells</b> (large cells sitting in the airway lining). Mast cells are now primed — like a loaded gun.'))
story.append(Spacer(1, 4))

story.append(bp('<b>Step 2: Early Phase Reaction (0-30 minutes)</b>'))
story.append(bp('Next exposure to the same allergen triggers the mast cell to release stored chemicals immediately:'))
for pt in [
    '<b>Histamine:</b> Immediate bronchoconstriction + mucus production + vasodilation.',
    '<b>Leukotrienes (LTC4, LTD4, LTE4):</b> More powerful than histamine. Sustained bronchoconstriction + mucus. Blocked by montelukast.',
    '<b>Prostaglandins:</b> Airway inflammation and bronchoconstriction. Blocked by NSAIDs — BUT in Samter\'s triad, blocking COX makes more leukotrienes instead (see triggers).',
    '<b>Tryptase:</b> Enzyme from mast cells. Blood test for tryptase confirms anaphylaxis when raised within 1-3 hours.',
]:
    story.append(bp(f'  • {pt}'))
story.append(bp('<b>Peak at 15-30 minutes.</b> Salbutamol reverses the bronchoconstriction quickly.'))
story.append(Spacer(1, 4))

story.append(bp('<b>Step 3: Late Phase Reaction (4-8 hours later)</b>'))
story.append(bp('A second wave: <b>eosinophils</b> (ee-OH-sin-oh-fills) and T-lymphocytes flood into the airway wall. This causes prolonged inflammation and thickening of the wall. This is why steroids are essential — they target this late inflammatory phase.'))
story.append(Spacer(1, 4))

story.append(bp('<b>Step 4: Airway Remodelling (years of poorly controlled asthma)</b>'))
for pt in [
    'Smooth muscle thickens and gets stronger (hypertrophy) — attacks become stronger.',
    'Subepithelial fibrosis — scar tissue under the surface lining — partially irreversible.',
    'More goblet cells (mucus-producers) — chronic mucus hypersecretion.',
    'These changes cause persistent limitation even between attacks in severe disease.',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 6))

three_prob = [
    ['Problem','What Happens in Attack','Drug That Fixes It','Speed of Effect'],
    ['1. BRONCHOCONSTRICTION\nAirway muscle squeezes shut','Smooth muscle tightens around\nbronchioles. Airway narrows.\nAir cannot flow in or out.','Salbutamol (SABA)\nIpratropium (SAMA)\nMagnesium sulphate (IV)','MINUTES.\nImmediate relief.\nSalbutamol peak: 15 min.'],
    ['2. INFLAMMATION\nWall swells and thickens','Eosinophils and mast cells\ninvade wall. Wall becomes\nthickened and oedematous.','Inhaled corticosteroids (ICS)\nOral prednisolone\nIV hydrocortisone','HOURS TO DAYS.\nNot immediate.\nSteroids need time.'],
    ['3. MUCUS HYPERSECRETION\nGoblet cells over-produce','Thick sticky mucus produced.\nPlugs block small airways.\nMucus harder to cough out.','Hydration + physiotherapy.\nNebulised bronchodilators\nhelp loosen mucus.','HOURS.\nNeeds active clearance.'],
]
story.append(plain_table(three_prob,[CW*0.24,CW*0.26,CW*0.25,CW*0.25]))
story.append(Spacer(1, 5))

info_box('<b>Why does this patient keep relapsing?</b> Steroids clear the inflammation — she feels better. But if the TRIGGER remains (cat at home, damp walls, mould, NSAIDs, occupational exposure), inflammation returns as steroids wear off. Ask: pet at home? Mould in bedroom? Taking NSAIDs or aspirin? On beta-blocker? Using inhaler correctly? Is there a second diagnosis (VCD, ABPA, HAE) being missed?', story)
memory_hook('ASTHMA MECHANISM: Allergen → IgE + Mast cells → Histamine + Leukotrienes → Bronchoconstriction (early, salbutamol) + Eosinophilic inflammation (late, steroids) + Mucus plugging. All three happen simultaneously. Salbutamol reverses constriction. Steroids reduce inflammation. Both needed together.', story)
divider(story)

# §4
sec_header('Section 4: Causes and Triggers of Asthma', story)
professor_says('Knowing triggers is clinically crucial. Removing the trigger can cure the patient better than any drug. Always ask about every trigger category.', story)

story.append(bp('<b>Atopy (AT-oh-pee) — The Genetic Foundation:</b>'))
story.append(bp('Atopy = inherited tendency to make too much IgE against allergens. The atopic triad: <b>Asthma + Allergic rhinitis (hayfever) + Atopic eczema</b>. If a patient has one, always ask about the other two.'))
story.append(Spacer(1, 6))

triggers_table = [
    ['Trigger Category','Specific Examples','Mechanism','Clinical Importance'],
    ['ALLERGENS\n(most important)','Cat dander (most potent).\nHouse dust mite.\nDog. Cockroach.\nGrass / tree pollen.\nAspergillus / Alternaria mould.','IgE on mast cells → mast cell\ndegranulation → histamine\n+ leukotrienes.','Skin prick test or\nspecific IgE (RAST) identifies\nthe culprit allergen.\nAllergen avoidance is curative.'],
    ['RESPIRATORY\nINFECTIONS','Rhinovirus (most common).\nInfluenza. RSV.\nMycoplasma. Sinusitis.','Viruses cause direct\nairway inflammation +\npost-infectious hyperresponsiveness\nlasting weeks.','Most common trigger for\nexacerbations. Annual flu vaccine\nfor ALL asthma patients.\nAntibiotics only if bacterial.'],
    ['DRUGS\n(NEVER give these)','NSAIDs: aspirin, ibuprofen,\ndiclofenac — ANY NSAID.\nBeta-blockers: even eye drops.\nACE inhibitors: cause cough\n(not bronchoconstriction).','NSAIDs: block COX-1 →\nleukotrienes surge → severe\nbronchoconstriction.\nBeta-blockers: block beta-2\nreceptors → bronchoconstriction.','Samter\'s Triad: Asthma +\nNasal polyps + NSAID sensitivity.\nNEVER prescribe NSAIDs or\nbeta-blockers to asthmatics\nwithout very careful consideration.'],
    ['OCCUPATIONAL\nEXPOSURE','Isocyanates (spray painters).\nFlour dust (bakers).\nLatex (healthcare workers).\nColophony (solderers).\nAnimal proteins (vets, farmers).','IgE-mediated sensitisation\nOR direct airway irritation.\nSymptoms only at work.','KEY QUESTION: "Better on\nholidays and weekends?"\nYES = occupational asthma.\nRemoval from exposure = cure.'],
    ['PHYSICAL TRIGGERS','Exercise (running, cold air).\nCold dry air (winter).\nFog and mist.','Cold dry air bypasses nasal\nhumidification. Osmotic change\nin airway cells → mast cell\nactivation.','Salbutamol 400mcg\n15 min BEFORE exercise.\nMontelukast excellent for\nexercise-induced prevention.'],
    ['GERD\n(Acid reflux)','Stomach acid refluxing up\nto the oesophagus and larynx.\nOften NO heartburn (silent).','Vagal reflex: acid in\noesophagus triggers vagus nerve\n→ bronchoconstriction.\nMicro-aspiration damages airway.','24h pH monitoring confirms.\nPPI treatment can improve\nasthma control significantly.\nTest: empirical PPI trial.'],
    ['HORMONAL','Premenstrual asthma.\nPregnancy. Thyroid disease.','Oestrogen and progesterone\nfluctuations alter airway\nresponsiveness.','Ask: do attacks link to\nyour menstrual cycle?\nMontelukast helpful.\nGnRH analogue in specialist care.'],
]
story.append(plain_table(triggers_table,[CW*0.16,CW*0.22,CW*0.3,CW*0.32]))
info_box('<b>Samter\'s Triad (AERD — Aspirin-Exacerbated Respiratory Disease):</b> Three things together: (1) Asthma. (2) Nasal polyps. (3) NSAID sensitivity. NSAIDs block COX-1 → arachidonic acid shunted into leukotriene pathway → massive leukotriene surge → severe bronchoconstriction within 30-120 minutes. Treatment: avoid ALL NSAIDs. Paracetamol is safe. Montelukast is key preventive drug. Aspirin desensitisation possible in specialist centres.', story)
memory_hook('ASTHMA TRIGGERS: Cat (most potent allergen). Rhinovirus URTI (most common exacerbation trigger). NSAIDs + Beta-blockers = NEVER give (contraindicated). Occupational = better on holidays. Exercise = salbutamol before. GERD = silent reflux. Premenstrual = montelukast. Mould / dust mite at home.', story)
divider(story)

# §5
sec_header('Section 5: Clinical Features — History and Examination', story)
professor_says('Asthma is diagnosed largely from the HISTORY. The key words are: episodic, variable, reversible, worse at night, and improved by bronchodilator. Know these — they come up in MRCP Part 1 and PACES every year.', story)

story.append(bp('<b>Classic Asthma History — The Key Features:</b>'))
for pt in [
    '<b>Episodic:</b> Attacks come and go. Between attacks patient is completely normal. ALWAYS breathless = not classic asthma (think fixed obstruction, COPD).',
    '<b>The triad:</b> (1) WHEEZE — musical whistling on breathing out. (2) BREATHLESSNESS. (3) DRY COUGH — often worst at night and early morning.',
    '<b>Cough variant asthma:</b> Cough only — no wheeze, no breathlessness. Dry, irritating, nocturnal. This patient sometimes has cough only — this fits.',
    '<b>Nocturnal and early morning:</b> Cortisol (natural steroid) lowest at night. Airways narrowest at 4am (circadian rhythm). Classic asthma timing.',
    '<b>Trigger identification:</b> Ask specifically about cats, dogs, dusty rooms, exercise, cold air, perfume, smoke, NSAIDs, beta-blockers.',
    '<b>Variability:</b> Some days fine, some days bad. Varies with allergen exposure. This variability is a diagnostic hallmark.',
    '<b>Atopic history:</b> Hayfever, eczema, food allergies, previous anaphylaxis.',
    '<b>Family history:</b> 60-70% have a family member with asthma, hayfever, or eczema.',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 6))

story.append(img_severity)
story.append(bp('Acute asthma severity — BTS/SIGN classification with key parameters', sImg))
story.append(Spacer(1, 6))

exam_table = [
    ['Sign Found','What You See','What It Means','Severity Indicator'],
    ['Respiratory Rate','Increased: 20-30/min.\nVery fast >30 = serious.','Body working hard to breathe.\nAirways narrowed.','Rate >= 25 = acute severe.'],
    ['Accessory Muscles','Neck muscles (sternocleidomastoid)\nvisible when breathing.\nIntercostal recession.','Normal breathing = diaphragm only.\nAccessory muscles = very breathless.','Severe attack sign.'],
    ['Position','Sitting upright.\nTripod position (leaning forward).','Maximises lung volume.\nPatient instinctively finds best position.','Cannot lie flat = severe.'],
    ['Speech','Short sentences. Single words.\nOr cannot speak at all.','Uses all breath just to breathe.','Single words = life-threatening.'],
    ['Wheeze','Bilateral expiratory wheeze.\nPolyphonic (many pitches).','Air forced through narrowed bronchioles.\nPolyphonic = diffuse small airway disease.','SILENT CHEST = life-threatening.\n(No air moving = no wheeze.)'],
    ['Heart Rate','Tachycardia > 110 bpm.\nNote: salbutamol also causes tachycardia.','Hypoxia + compensation.\nSalbutamol beta-1 side effect.','HR >= 110 = acute severe.\nBradycardia = pre-arrest.'],
    ['PEFR\n(Peak Flow)','Reduced from personal best.\nMeasure with handheld meter.','Best objective bedside measure\nof airway obstruction.','< 50% = severe.\n< 33% = life-threatening.'],
    ['SpO2\n(Oxygen saturation)','May be low (< 92%)\nin severe attack.','V/Q mismatch — some areas\nventilated but not perfused.','< 92% on air = life-threatening.'],
]
story.append(plain_table(exam_table,[CW*0.17,CW*0.25,CW*0.33,CW*0.25]))
alert_box('SILENT CHEST = LIFE-THREATENING ASTHMA. No wheeze does NOT mean improving. It means airways are so blocked that NO AIR IS MOVING. This is a pre-arrest state. Call for immediate senior help + ICU + IV magnesium sulphate now.', story)
alert_box('LIFE-THREATENING FEATURES — any ONE of these: SpO2 < 92% | PEFR < 33% | Silent chest | Cyanosis | Bradycardia | Exhaustion | Confusion | Arrhythmia | Normal or HIGH PaCO2.', story)
memory_hook('ASTHMA EXAM: Wheeze + tachycardia + accessory muscles + cannot complete sentences = ACUTE SEVERE. Silent chest + SpO2 <92% + confusion/bradycardia = LIFE-THREATENING = call ICU immediately. PEFR: 50-75% = moderate. 33-50% = severe. <33% = life-threatening.', story)
divider(story)

# §6 Investigations
sec_header('Section 6: Investigations — How We Confirm the Diagnosis', story)
professor_says('The diagnosis of asthma is CLINICAL — based on history and examination. Investigations confirm it, assess severity, exclude other diagnoses, and guide treatment. Know which test proves what.', story)

story.append(bp('<b>Spirometry (Lung Function Tests) — The Gold Standard:</b>'))
for pt in [
    '<b>FEV1:</b> Forced Expiratory Volume in 1 second. How much air blown out in first second. Low in asthma (obstruction).',
    '<b>FVC:</b> Forced Vital Capacity. Total air blown out completely. Usually normal or mildly reduced.',
    '<b>FEV1/FVC ratio:</b> Normal is > 0.7 (or 70%). In asthma (obstruction) < 0.7. Key MRCP number.',
    '<b>Reversibility test:</b> Give salbutamol 400mcg. Repeat spirometry 15 minutes later. If FEV1 improves by > 12% AND > 200mL = REVERSIBLE OBSTRUCTION = confirms asthma.',
    '<b>Variability:</b> PEFR varies > 20% over the day (morning vs evening). Diurnal variation > 20% = diagnostic of asthma.',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 5))

invx_table = [
    ['Investigation','What It Measures','Asthma Finding','Why It Matters'],
    ['Spirometry + reversibility\n(FEV1, FVC, FEV1/FVC)','Airflow obstruction and\nreversibility after SABA.','Obstructive pattern:\nFEV1/FVC < 0.7.\n> 12% + > 200mL improvement\nafter salbutamol.','Confirms diagnosis.\nMRCP Part 1 essential.\nAlso distinguishes from COPD\n(poor reversibility in COPD).'],
    ['Peak Expiratory Flow\nRate (PEFR)','Maximum speed of breathing out.\nUsing hand-held meter.','Diurnal variation > 20%.\nReduced in attacks.\nCompare to personal best.','Cheap, bedside, monitor response.\nPatient does at home\n(asthma diary). Gold for monitoring.'],
    ['Fractional exhaled nitric\noxide (FeNO)','Eosinophilic airway inflammation.\nBiomarker of T2 inflammation.','> 40 ppb = significant\neosinophilic inflammation.\nConfirms atopic / eosinophilic\nasthma.','Predicts steroid response.\nGuides biologic therapy choices.\n> 25 = consider ICS. > 50 = very\nlikely to respond to ICS/biologics.'],
    ['Blood tests:\nEosinophil count,\nTotal IgE, Specific IgE','Atopy and eosinophilic\ninflammation markers.','Eosinophils > 0.3 x10^9/L\n= eosinophilic asthma.\nHigh IgE = atopic.\nSpecific IgE to allergen (RAST).','Guides biologic choice.\nMepolizumab/benralizumab needs\neosinophils > 0.3.\nOmalizumab needs high IgE.'],
    ['CXR (Chest X-ray)\n(in acute attack)','Look for: hyperinflation,\npneumothorax, consolidation,\nforeign body.','Usually NORMAL in asthma.\nMay see hyperinflation\n(flattened diaphragm).','To exclude: pneumothorax (tension).\npneumonia, foreign body.\nCXR CANNOT diagnose asthma.'],
    ['ABG (Arterial Blood Gas)\nin severe attack','PaO2, PaCO2, pH.\nOxygenation + ventilation.','Type 1 RF: low PaO2.\nInitially low PaCO2 (hyperventilating).\nNormal or high PaCO2 = DANGER\n= patient tiring = needs ITU.','PaCO2 rising in severe attack =\nrespiratory failure approaching.\nThis is a RED FLAG.\nCall ITU if PaCO2 > 4.5 in severe.'],
    ['Serum tryptase\n(within 1-3 hours)','Mast cell degranulation.\nReleased in anaphylaxis.','Raised > 11.4 mcg/L = anaphylaxis.\nNormal in asthma.','Distinguishes anaphylaxis from\nasthma. Repeat at 24h (baseline).\nHelps if patient recovering after\nepinephrine and uncertain cause.'],
    ['Skin prick tests\nor RAST (specific IgE)','IgE sensitisation to specific\nallergens (cat, HDM, grass etc).','Positive wheal-and-flare = IgE\nagainst that allergen.','Identifies specific trigger.\nGuides avoidance advice.\nNeeded before allergen\nimmunotherapy (desensitisation).'],
]
story.append(plain_table(invx_table, [CW*0.2, CW*0.22, CW*0.26, CW*0.32]))
info_box('<b>MRCP KEY FACT on ABG:</b> In an asthma attack, the patient hyperventilates → blows off CO2 → PaCO2 is LOW (< 4.5 kPa). If PaCO2 is NORMAL (4.5-6) or HIGH (> 6) during severe asthma, this means the patient is TIRING and can no longer hyperventilate. This is called "Type 2 respiratory failure" and signals impending respiratory arrest. Call ITU immediately. This is a favourite MRCP question.', story)
memory_hook('KEY INVESTIGATIONS: Spirometry FEV1/FVC < 0.7 + > 12% reversibility = confirms asthma. FeNO > 40 ppb = eosinophilic inflammation = steroid response. ABG in severe: LOW PaCO2 (hyperventilating) = compensating. NORMAL or HIGH PaCO2 = TIRING = ITU. PEFR variation > 20% = diagnostic. Tryptase raised only in anaphylaxis, not pure asthma.', story)
divider(story)

# §7 Management
sec_header('Section 7: Management — How We Treat Asthma', story)
professor_says('Management has two parts: ACUTE attack (emergency) and CHRONIC long-term. Know both. Know the BTS stepwise ladder perfectly — it comes up every year in MRCP.', story)

story.append(bp('<b>Part A: ACUTE SEVERE ASTHMA — Emergency Management:</b>'))
story.append(bp('This is a medical emergency. Act fast. Remember SHAM-O: Salbutamol + Hydrocortisone + Airway (oxygen) + Magnesium + Other (ipratropium + consider ITU).'))
story.append(Spacer(1, 5))

acute_mgmt = [
    ['Priority','Treatment','Dose + Route','Notes'],
    ['1. OXYGEN\n(first and always)','High-flow oxygen.\nTarget SpO2 94-98%.','15L via non-rebreather mask\ninitially. Titrate down.','Asthma patients are NOT CO2-retainers (that is COPD). Give high-flow O2 freely in acute attack.'],
    ['2. SALBUTAMOL\n(first-line bronchodilator)','Beta-2 agonist. Relaxes\nbronchial smooth muscle.\nFast. Effective.','2.5mg nebulised every 20-30\nminutes. Continuous if needed.\nOr 4-8 puffs via spacer if mild.','Causes tachycardia + tremor\n(beta-1 spillover). Repeat every\n20-30 mins. IV if nebuliser fails.'],
    ['3. IPRATROPIUM\n(add if moderate-severe)','Anticholinergic. Blocks\nvagal bronchoconstriction.\nAdds to salbutamol.','0.5mg (500mcg) nebulised\nevery 4-6 hours.\nCombine with salbutamol neb.','Not as potent as salbutamol\nbut additive effect. Continue for\nfirst 24-48h in severe attack.'],
    ['4. STEROIDS\n(essential — start ASAP)','Reduce eosinophilic inflammation.\nReduce airway swelling.\nPrevent late-phase reaction.','Oral prednisolone 40-50mg/day\nOR IV hydrocortisone 100mg QDS\nif cannot swallow. 5-7 day course.','NOT immediate effect — takes\n4-6 hours. Start within first\n30 minutes. Prevents relapse.\nTaper not needed for short courses.'],
    ['5. IV MAGNESIUM\n(add in severe/life-threatening)','Bronchodilator (blocks\ncalcium in smooth muscle).\nUsed if not responding.','2g IV over 20 minutes.\nSingle dose.','MRCP favourite! Give for\nlife-threatening OR severe\nnot responding after 1 hour.\nNo routine nebulised Mg evidence.'],
    ['6. HELIOX / IV\nSalbutamol (refractory)','Helium:oxygen mix.\nDecreases airway resistance.','IV salbutamol infusion if\nnebulised fails. ITU decision.','When failing all above — involve\nanaesthetics / ITU. May need\nNIV or intubation (last resort\n— intubation has HIGH risk in asthma).'],
    ['7. ANTIBIOTICS','Only if evidence of\nbacterial infection.','Amoxicillin 500mg TDS OR\ndoxycycline 200mg loading\nthen 100mg OD if penicillin-allergic.','Viral triggers (rhinovirus) are\nmost common — antibiotics NOT\nroutinely given unless\npurulent sputum / consolidation on CXR.'],
]
story.append(plain_table(acute_mgmt,[CW*0.16,CW*0.22,CW*0.25,CW*0.37]))
alert_box('WHEN TO CALL ITU: Life-threatening features + not responding to above after 30-60 minutes. Rising PaCO2. Exhaustion. Confusion. Silent chest not improving. Consider early intubation — but CAUTION: intubation in asthma carries high risk of dynamic hyperinflation + pneumothorax. Only intubate as last resort.', story)
story.append(Spacer(1, 8))

story.append(bp('<b>Part B: CHRONIC MANAGEMENT — The BTS/SIGN Stepwise Ladder (2022):</b>'))
story.append(bp('MRCP Part 1 and 2 essential — know each step, which drugs are added, and when to step up or down.'))
story.append(Spacer(1, 5))

bts_steps = [
    ['BTS Step','Treatment Added','Key Drug at This Step','When to Step Up'],
    ['STEP 1\nMild intermittent\n< 2x/week symptoms','SABA as-needed only.\nSalbutamol 100-200mcg\nwhen needed (PRN).','Salbutamol (SABA)\nTerbutaline (alternative SABA)','Symptoms > 2 times/week\nOR night waking\nOR SABA > 2x/week.'],
    ['STEP 2\nRegular preventer\n(most patients)','Add LOW-DOSE ICS.\nGiven REGULARLY every day\neven when well.','Beclometasone 200mcg/day\nFluticasone 100mcg/day\nBudesonide 200mcg/day','Poor control on step 2.\nSymptoms > 2x/week despite ICS.'],
    ['STEP 3\nInitial add-on therapy','Add LABA to ICS.\nGiven as COMBINATION inhaler.\nALWAYS with ICS (never alone).','Salmeterol or Formoterol\n+ ICS combined:\nSeretide (salmeterol + fluticasone)\nSymbicort (formoterol + budesonide)','Still poorly controlled.\nFEV1 not improving.'],
    ['STEP 3 ALTERNATIVES\n(if LABA not tolerated)','Leukotriene Receptor\nAntagonist (LTRA): Montelukast.\nOR slow-release theophylline.\nOR increase ICS dose.','Montelukast 10mg NOCTE\n(night-time, once daily)\nOR Theophylline SR\n(monitor blood levels)','LABA preferred over montelukast\nbut some patients prefer oral.'],
    ['STEP 4\nPoor control on step 3','Increase ICS to MEDIUM dose.\nConsider: LTRA + LABA + ICS.\nConsider: referral to specialist.','Beclometasone > 400-800mcg/day\nFluticasone > 250mcg/day\nAdd montelukast to existing\nICS + LABA combination.','Refer to specialist for\nfurther phenotyping and\nbiologic therapy assessment.'],
    ['STEP 5\nSevere refractory asthma\n(SPECIALIST only)','ORAL STEROIDS (lowest effective\ndose). BIOLOGICS if eligible.\nBronchial thermoplasty.','Prednisolone 5-10mg OD\nOR Biologics:\nOmalizumab (anti-IgE)\nMepolizumab (anti-IL-5)\nBenralizumab (anti-IL-5R)\nDupilumab (anti-IL-4R / IL-13)','Refer all step 5 patients to\nspecialist asthma clinic.\nPhenotyping essential before\nbiologic choice.'],
]
story.append(plain_table(bts_steps,[CW*0.17,CW*0.28,CW*0.27,CW*0.28]))
story.append(Spacer(1, 5))

story.append(bp('<b>Biologics for Severe Asthma — MRCP Part 2 Essential:</b>'))
biologics_table = [
    ['Drug Name','Target','Patient Type','MRCP Key Fact'],
    ['Omalizumab\n(Xolair)','Anti-IgE monoclonal antibody.\nBinds free IgE.','Atopic (allergic) asthma.\nHigh total IgE.\nSensitised to perennial allergen.\nBMI consideration for dosing.','Given SC every 2-4 weeks.\nDose based on body weight AND\nbaseline IgE level. Can cause\nanaphylaxis — observe 2h after.'],
    ['Mepolizumab\n(Nucala)','Anti-IL-5 antibody.\nReduces eosinophil production.','Eosinophilic asthma.\nBlood eosinophils > 0.3 x10^9/L.\nFrequent exacerbations.','SC monthly. Reduces exacerbations\nby ~50%. Must confirm high\neosinophil count before prescribing.\nAlso used in EGPA (eosinophilic GPA).'],
    ['Benralizumab\n(Fasenra)','Anti-IL-5 receptor.\nDirectly depletes eosinophils.','Eosinophilic asthma.\nSimilar to mepolizumab.\nBlood eos > 0.3 x10^9/L.','SC: monthly x3, then\nevery 8 weeks. Faster\nand more complete eosinophil\ndepletion than mepolizumab.'],
    ['Dupilumab\n(Dupixent)','Anti-IL-4R/IL-13.\nBlocks type 2 inflammation.','Moderate-severe eosinophilic\nasthma OR oral steroid-dependent.\nAlso for atopic eczema.','SC every 2 weeks. Works even\nif eosinophils normal. Also treats\natopic eczema and nasal polyps\n(same pathway). Good for Samter\'s.'],
    ['Tezepelumab\n(Tezspire)','Anti-TSLP (thymic stromal\nlymphopoietin). Upstream blocker.','Severe uncontrolled asthma.\nBroader indication — works in\nnon-eosinophilic types too.','Most recent biologic. SC monthly.\nFirst to work in both eosinophilic\nAND non-eosinophilic severe asthma.\nHigh-level evidence.'],
]
story.append(plain_table(biologics_table,[CW*0.15,CW*0.22,CW*0.25,CW*0.38]))
info_box('<b>PRESCRIBING KEY POINTS (Ganesh & Kuruvilla):</b> (1) SABA alone without ICS for > 2 weeks is dangerous — drives inflammation. (2) LABA must NEVER be used without ICS (risk of fatal asthma attack — black box warning). (3) Inhaler technique is the most commonly missed issue — check at every visit. (4) Spacer doubles drug delivery — recommend for ALL patients. (5) When prescribing prednisolone > 3 weeks, give PPI for gastric protection + bone protection (calcium + vitamin D).', story)
memory_hook('BTS LADDER: Step 1 = SABA PRN. Step 2 = ADD ICS. Step 3 = ADD LABA (always with ICS). Step 4 = increase ICS + LTRA. Step 5 = oral steroids + biologics. KEY: LABA NEVER without ICS. Montelukast = good for exercise-induced + Samter. Magnesium = 2g IV for severe. FeNO > 40 + eosinophils > 0.3 = biologic candidate.', story)
divider(story)

# §8 Differential Diagnoses
sec_header('Section 8: Differential Diagnoses — Conditions That Mimic Asthma', story)
professor_says('Every MRCP question about a young breathless patient with wheeze is testing whether you know the DIFFERENTIALS. Some look exactly like asthma but are not. Missing these causes harm. Know each one and how to distinguish it.', story)

story.append(img_diffmap2)
story.append(bp('Differential diagnosis map — distinguishing features, pattern by pattern', sImg))
story.append(Spacer(1, 6))

diff_table = [
    ['Condition','What It Is','How It Mimics Asthma','How To Tell Apart'],
    ['VOCAL CORD\nDYSFUNCTION (VCD)','Paradoxical vocal cord adduction\nduring INSPIRATION.\nFunctional (psychogenic or habit).','Breathlessness + stridor or wheeze.\nOften young female.\nDoes not respond to salbutamol.\nMultiple ED visits.','Inspiratory wheeze/stridor\n(NOT expiratory).\nNormal spirometry + FeNO.\nLaryngoscopy: cords close in\nnot open. Treated with speech\ntherapy (NOT inhalers).'],
    ['LARYNGEAL\nSPASM','Sudden forceful closure\nof vocal cords. Extreme VCD.\nCan be reflex (GERD, post-extubation).','Acute severe breathlessness\nin seconds. Stridor.\nPanic + feeling of choking.\nMay occur with asthma.','Typically self-limiting 30-60 sec.\nStridor INSPIRATORY.\nNo response to salbutamol.\nGERD-related: nocturnal episodes.\nTreatment: reassure + breathing\ntechniques + PPI for GERD.'],
    ['ANAPHYLAXIS with\nLARYNGEAL OEDEMA','Severe systemic IgE-mediated\nhypersensitivity reaction.\nRapid onset after allergen.','Acute bronchospasm +\nbreathlessness + wheeze.\nMay present as "asthma attack".','Look for: urticaria, angioedema,\nhypotension, facial swelling,\nstridor = laryngeal oedema.\nTryptase raised.\nMUST GIVE ADRENALINE (epinephrine)\n0.5mg IM immediately.\nDEATH without epinephrine.'],
    ['HEREDITARY\nANGIOOEDEMA (HAE)','C1-esterase inhibitor deficiency.\nAutosomal dominant.\nBradykinin-mediated.','Laryngeal oedema = life-threatening\nairway obstruction.\nRecurrent angioedema attacks.','No urticaria, no allergy.\nC4 low (even between attacks).\nC1-esterase inhibitor low.\nAdrenaline does NOT work (bradykinin not IgE).\nTreatment: C1-INH concentrate\nor icatibant (bradykinin blocker).'],
    ['ALLERGIC\nBRONCHOPULMONARY\nASPERGILLOSIS (ABPA)','Hypersensitivity reaction to\nAspergillus fumigatus\ncolonising asthmatic airways.','Difficult-to-control asthma.\nBrown mucus plugs.\nRecurrent infiltrates on CXR.\nBronchiectasis developing.','Central bronchiectasis on CT.\nHigh serum IgE (> 1000 IU/mL).\nSpecific IgE/IgG to Aspergillus +ve.\nBlood eosinophils high.\nTreatment: oral prednisolone +\nitraconazole antifungal.'],
    ['EOSINOPHILIC\nBRONCHITIS','Airway eosinophilic inflammation\nwithout bronchospasm.\nCause of chronic cough.','Dry cough (cough-variant).\nEosinophilia in sputum.\nMistaken for cough-variant asthma.','NORMAL spirometry.\nNormal airway hyperresponsiveness test.\nRaised sputum eosinophils\n(induced sputum).\nTreats well with ICS.\nNo bronchodilator needed.'],
    ['COPD\n(Older smoker — NOT this patient\nbut MRCP tests this)','Chronic obstructive pulmonary\ndisease. Neutrophilic.\nIrreversible airflow obstruction.','Chronic cough + wheeze +\nbreathlessness. May have\nhyperinflated chest. Barrel chest.','Age > 35. Smoker > 10 pack years.\nFEV1/FVC < 0.7 BUT < 12%\nreversibility. CXR: hyperinflation.\nNO nocturnal symptoms. Steady decline.'],
    ['CARDIAC ASTHMA\n(Heart failure)','Pulmonary oedema from left\nheart failure. Bronchospasm\nfrom fluid in airways.','Acute breathlessness + wheeze\n+ crepitations. Mimics acute asthma.\nCommon in elderly.','Bibasal crepitations + elevated JVP\n+ peripheral oedema. CXR: bat-wing\nedema + Kerley B lines.\nBNP raised. Responds to diuretics\nand GTN, NOT salbutamol.'],
]
story.append(plain_table(diff_table,[CW*0.17,CW*0.22,CW*0.25,CW*0.36]))
info_box('<b>REMEMBERING: Inspiratory vs Expiratory sounds</b> — STRIDOR = upper airway obstruction = heard breathing IN = larynx, trachea, epiglottis. WHEEZE = lower airway = heard breathing OUT = bronchioles, bronchi. Both can overlap in very severe disease. Anaphylaxis with laryngeal oedema can produce BOTH stridor + wheeze.', story)
memory_hook('DIFFERENTIALS: VCD = inspiratory wheeze + no response to salbutamol + laryngoscopy. Anaphylaxis = urticaria + hypotension + tryptase raised → epinephrine IM NOW. HAE = C4 low + C1-INH low + no urticaria → icatibant (NOT epinephrine). ABPA = IgE > 1000 + Aspergillus IgE/IgG + central bronchiectasis. Cardiac asthma = elderly + bibasal creps + BNP raised + diuretics help.', story)
divider(story)

# §9 Complications
sec_header('Section 9: Complications of Asthma', story)
professor_says('Asthma complications arise from either the disease itself (poorly controlled), the acute attack (immediate threats to life), or from long-term treatment side effects. All are examinable.', story)

comp_table = [
    ['Complication','How It Arises','How to Recognise','Management'],
    ['RESPIRATORY FAILURE\nType 1 and Type 2','Type 1: V/Q mismatch in attack.\nType 2: Respiratory muscle\nfatigue in severe/life-threatening.','ABG: PaO2 < 8kPa (Type 1).\nPaCO2 > 6kPa + low pH (Type 2).\nType 2 = ITU.','High-flow O2 + all asthma drugs.\nITU for ventilatory support\nif Type 2. Early ITU involvement.'],
    ['PNEUMOTHORAX','Alveolar rupture from high\nintrathoracic pressures during attack.\nOr from barotrauma if ventilated.','Sudden severe unilateral\nchest pain + worsening breathlessness.\nTracheal deviation (tension).','CXR confirms. Needle decompression\nfor tension. Chest drain for\nlarge pneumothorax.'],
    ['STATUS ASTHMATICUS','Severe attack not responding\nto standard treatment\n> 1 hour of optimal therapy.','Any life-threatening feature\npersisting despite treatment.\nIncreasing exhaustion + CO2 retention.','ITU admission. IV salbutamol.\nMagnesium sulphate.\nConsider intubation\n(last resort — high risk).'],
    ['MUCUS PLUGGING\n(Atelectasis)','Thick mucus plugs block airways\n→ collapse of lung segments\nbehind the block.','Lobar/segmental collapse on CXR.\nFever (secondary infection\nbehind plug possible).','Physiotherapy + hydration.\nHumidified oxygen.\nBronchoscopy for removal\nif severe collapse.'],
    ['SIDE EFFECTS:\nLong-term oral steroids','Prednisolone for poorly controlled\nasthma causes systemic effects.','Osteoporosis. Diabetes. Hypertension.\nAdrenal suppression. Obesity.\nCataract. Easy bruising.','Minimum effective dose.\nBone protection: Ca+D3 + bisphosphonate.\nAnnual bone density (DEXA scan).\nPrevent with step-down biologics.'],
    ['SIDE EFFECTS:\nInhaled steroids (ICS)','Local deposition in oropharynx.','Oral candidiasis (thrush).\nDysphonia (hoarse voice).','Spacer use. Rinse mouth after\nevery ICS dose — ALWAYS.\nAntifungal if thrush develops.'],
    ['ABPA (as complication)','Repeated Aspergillus colonisation\n→ bronchiectasis + fibrosis.','Progressive breathlessness.\nBronchiectasis on CT chest.','High-dose oral prednisolone\n+ itraconazole antifungal.\nMonitor IgE and eosinophils.'],
]
story.append(plain_table(comp_table,[CW*0.2,CW*0.22,CW*0.25,CW*0.33]))
memory_hook('COMPLICATIONS: Rising PaCO2 in acute attack = respiratory failure = ITU. Sudden unilateral pain = pneumothorax. Oral thrush from ICS = rinse mouth. Long-term oral steroids = bone protection needed. ABPA = bronchiectasis. Mucus plugging = collapse on CXR = physio.', story)
divider(story)

# §10 Special Situations
sec_header('Section 10: Asthma in Special Situations', story)
professor_says('MRCP Part 2 and PACES loves special situations. Asthma in pregnancy. Asthma in children (different from adults). Occupational asthma. Nocturnal asthma. Know each one.', story)

special_table = [
    ['Special Situation','Key Differences','Management Principles','MRCP Key Points'],
    ['ASTHMA IN\nPREGNANCY','One-third improve.\nOne-third stay same.\nOne-third worsen.\nFetal hypoxia from uncontrolled\nasthma is MORE dangerous\nthan ICS drugs.','CONTINUE all asthma medications.\nSAFE: Salbutamol, ICS, prednisolone,\nmontelukast, magnesium.\nSAFE: All step 1-4 drugs.\nAVOID: No strong evidence for\nbiotics in pregnancy — specialist.','Most common question:\n"Is it safe to use inhaler in pregnancy?"\nANSWER: YES. Uncontrolled asthma\nharms baby more than inhalers.\nAcute severe asthma in pregnancy\n= obstetric emergency. Admit all.'],
    ['EXERCISE-INDUCED\nASSUMPTION (EIA)','Bronchoconstriction 5-10 min\nafter exercise. Spontaneously\nresolves 30-60 min later.','SABA 15 min before exercise.\nMontelukast VERY effective.\nWarming up helps.\nCold weather — cover mouth/nose.','Diagnosis: 15% fall in FEV1\nor PEFR after standard\nexercise challenge test.\nAthletes: ensure medications\npermitted (most ICS and SABA\nare permitted in sport).'],
    ['NOCTURNAL ASTHMA','Cortisol lowest at 4am.\nAirway inflammation peaks at night.\nAirway cooling at night.','Long-acting beta-agonist (LABA)\nas part of ICS+LABA combination.\nCheck for GERD (nocturnal reflux).\nCheck dust mite in pillows/mattress.','Classic MRCP: patient wakes at 4am\ncoughing and wheezing = asthma.\n(COPD does not do this.)\nDiary entries show a.m. dip\nin PEFR.'],
    ['OCCUPATIONAL\nASSUMPTION (OA)','Starts > age 17 at work.\nSymptoms worse at work,\nbetter on holidays/weekends.','Remove from exposure = best treatment.\nTemporary improvement: ICS + SABA.\nReport to occupational health.\nLegal rights: reasonable\nadjustments by employer.','Most common causes: isocyanates,\nflour, latex, colophony.\nINVESTIGATION: serial PEFR (4 times/day\nat work vs home) for 4 weeks.\n20% variation at work = diagnostic.'],
    ['DIFFICULT/SEVERE\nREFRACTORY ASTHMA','Does not respond to\nstep 3-4 treatment.\nRequires specialist review.','Check: correct diagnosis?\nCheck: adherence (blood eosinophil\ncount helps if on ICS).\nCheck: inhaler technique.\nCheck: psychosocial factors.','4 D checklist:\nDiagnosis (correct?)\nDrug (right drug?)\nDelivery (right inhaler technique?)\nDriving factors (comorbidities?)\nOnly then consider biologics.'],
]
story.append(plain_table(special_table,[CW*0.18,CW*0.27,CW*0.27,CW*0.28]))
memory_hook('SPECIAL SITUATIONS: Pregnancy = SAFE to use all inhalers. Exercise-induced = salbutamol before + montelukast. Nocturnal = LABA + GERD check + dust mite. Occupational = serial PEFR at work vs home. Refractory = 4 Ds: Diagnosis, Drug, Delivery, Driving factors.', story)
divider(story)

# §11 Pharmacology
sec_header('Section 11: Pharmacology of Asthma Drugs — MRCP Detail', story)
professor_says('Know the mechanism, class, and side effects of every asthma drug. MRCP Part 1 tests mechanism. Part 2 tests choice and monitoring. PACES tests what you tell the patient.', story)

pharma_table = [
    ['Drug / Class','Mechanism','Key Side Effects','MRCP Prescribing Points'],
    ['SALBUTAMOL\n(Ventolin)\nShort-acting beta-2 agonist (SABA)','Agonist at beta-2 adrenoceptors\non bronchial smooth muscle.\nActivates adenylyl cyclase →\ncAMP → smooth muscle relaxation.','Tremor (most common).\nPalpitations + tachycardia.\nHypokalaemia (K+ shifts into cells).\nHyperglycaemia (diabetics).','Onset: 1-3 min. Peak: 15 min.\nDuration: 4-6h.\nNebulised dose: 2.5-5mg.\nInhaled via spacer: 4-8 puffs.\nDOSE-DOSE: hypokalaemia — check K+\nin severe attacks on frequent nebs.'],
    ['BECLOMETASONE /\nFLUTICASONE\nInhaled corticosteroid (ICS)','Binds glucocorticoid receptor\n→ reduces transcription of\npro-inflammatory cytokines.\nReduces eosinophilic inflammation.','Local: oral candidiasis, dysphonia.\nSystemic (high dose): adrenal\nsuppression, osteoporosis, skin\nthinning (less than oral).','ALWAYS rinse mouth after use.\nSpacer reduces oropharyngeal\ndeposition. Beclometasone 400mcg\nvia DPI = 200mcg via MDI with\nspacer (extra-fine particles more\nefficient). Check device type.'],
    ['SALMETEROL /\nFORMOTEROL\nLong-acting beta-2 agonist (LABA)','Same as salbutamol but longer\nchain. Duration 12h (salmeterol)\nor 12h (formoterol — faster onset).','Same as salbutamol but sustained.\nHypokalaemia. Tremor.\nBLACK BOX: increased asthma\ndeath if used WITHOUT ICS.','MUST ALWAYS be with ICS.\nNEVER prescribe LABA alone in asthma.\nFormoterol: faster onset — can\nbe used as SMART therapy\n(maintenance + reliever in same device).'],
    ['IPRATROPIUM\n(Atrovent)\nShort-acting muscarinic antagonist (SAMA)','Blocks M3 muscarinic receptors\non smooth muscle → reduces\nbronchospasm from vagal tone.\nAlso reduces secretions.','Dry mouth.\nUrinary retention (elderly men).\nConstipation.\nBlurred vision (eye exposure).','Used in acute severe attack\n(added to nebulised salbutamol).\nNOT first-line for chronic asthma\n(used in COPD). Duration 4-6h.\nIf accidentally in eyes: acute\nangle closure glaucoma risk.'],
    ['MONTELUKAST\n(Singulair)\nLeukotriene receptor antagonist (LTRA)','Blocks CysLT1 receptor.\nPrevents leukotrienes from\ncausing bronchoconstriction\n+ mucus + inflammation.','Neuropsychiatric side effects\n(FDA black box 2020):\ndepression, anxiety, nightmares,\naggression, suicidality.','10mg once at night (nocte).\nExcellent for: exercise-induced,\nSamter\'s triad, allergic rhinitis\n+ asthma, ABPA adjunct.\nWARN patients about mood changes.\nCan be used in pregnancy.'],
    ['THEOPHYLLINE\n(methylxanthine)','Phosphodiesterase inhibitor →\nincreases cAMP → bronchodilation.\nAlso adenosine receptor blockade.','NARROW THERAPEUTIC INDEX.\nNausea, vomiting, palpitations.\nArrhythmias + seizures in overdose.\nMultiple drug interactions.','Therapeutic range: 10-20 mg/L.\nReduced metabolism (higher levels):\nerythromycin, ciprofloxacin,\ncimetidine, heart failure, liver disease.\nMonitor blood levels. OLD drug — less\nused but still MRCP favourite for toxicity.'],
    ['PREDNISOLONE\n(oral steroid)','Systemic glucocorticoid.\nBroadly anti-inflammatory:\nreduces all cytokines, T-cells,\neosinophils, mast cells.','Short course: relatively safe.\nLong-term: Cushing syndrome,\nosteoporosis, diabetes, hypertension,\nadrenal suppression, peptic ulcer.','Acute severe: 40-50mg for 5-7 days\n(no taper needed for short course).\nLong-term: lowest effective dose.\nGive: PPI (gastroprotection) +\nCa + D3 + bisphosphonate (bone\nprotection) if > 3 months.'],
    ['OMALIZUMAB /\nMEPOLIZUMAB\n(biologic therapy)','Anti-IgE (omalizumab) or\nAnti-IL-5/IL-5R (mepolizumab,\nbenralizumab) → reduces\neosinophilic inflammation cascade.','Injection site reactions.\nAnaphylaxis (omalizumab — rare\nbut observe 2h after first 3 doses).\nHeadache, fatigue.','Specialist-only prescribing.\nCriteria: severe uncontrolled asthma\n+ high IgE (omalizumab) OR\neosinophils > 0.3 (anti-IL-5).\nGiven at home by patient (SC injection)\nafter training. NICE guidelines apply.'],
]
story.append(plain_table(pharma_table,[CW*0.17,CW*0.22,CW*0.26,CW*0.35]))
info_box('<b>Hypokalaemia in acute severe asthma:</b> Salbutamol drives potassium INTO cells via Na/K ATPase activation. In high-dose/continuous nebulised salbutamol + corticosteroids + hypoxia, serum K+ can fall dangerously. CHECK POTASSIUM in every severe acute attack. If K+ < 3.0 mmol/L, replace IV. This is a common MRCP scenario.', story)
memory_hook('DRUG FACTS: Salbutamol = tremor + tachycardia + hypokalaemia. ICS = rinse mouth (thrush). LABA NEVER without ICS. Montelukast = neuropsychiatric warning. Theophylline = narrow window + drug interactions. Mg = 2g IV. Prednisolone long-term = bone protection. Omalizumab = anaphylaxis risk → observe 2h.', story)
divider(story)

# §12 MRCP Exam Triggers
sec_header('Section 12: Top 12 MRCP Exam Trigger Scenarios', story)
professor_says('These are the most commonly tested clinical scenarios in MRCP Parts 1, 2, and PACES. Know each one by heart.', story)

triggers = [
    ['#','MRCP Scenario','Answer / Key Point'],
    ['1','Young woman, episodic wheeze and cough, worse at night, PEFR variable, atopic history.\nWhat confirms diagnosis?','FEV1/FVC < 0.7 + > 12% + > 200mL reversibility after salbutamol. Or PEFR diurnal variation > 20%.'],
    ['2','Asthma patient developing severe attack. PEFR 28% best. SpO2 88%. Silent chest.\nWhat is the immediate next step?','Life-threatening asthma. Oxygen + nebulised salbutamol + ipratropium + IV hydrocortisone 100mg + IV magnesium 2g. Call ITU.'],
    ['3','Asthmatic has PaCO2 5.8 kPa during severe attack. Pulse 110. Previously PaCO2 was low.\nWhat does this mean?','DANGER — rising PaCO2 = Type 2 respiratory failure = patient tiring = call ITU immediately for ventilatory support.'],
    ['4','Asthmatic on step 2 (ICS). Well but now needing SABA > 4x/week. Correct action?','Step up: add LABA to ICS. Prescribe ICS+LABA combination inhaler (Seretide or Symbicort). NEVER prescribe LABA alone.'],
    ['5','Young woman with recurrent breathlessness + wheeze not responding to salbutamol.\nSpiometry normal. FeNO 18 ppb. What is the likely diagnosis?','Vocal cord dysfunction (VCD). Spirometry normal (flow-volume loop shows variable extrathoracic obstruction). Laryngoscopy confirms. Treat with speech therapy.'],
    ['6','Patient on NSAIDs, nasal polyps, aspirin sensitivity, and severe asthma. What syndrome?','Samter\'s Triad (Aspirin-Exacerbated Respiratory Disease / AERD). Stop ALL NSAIDs. Montelukast is key. Paracetamol is safe.'],
    ['7','Asthmatic with very high IgE (> 1000), central bronchiectasis, Aspergillus-specific IgE positive.\nDiagnosis and treatment?','ABPA (Allergic Bronchopulmonary Aspergillosis). Oral prednisolone + itraconazole. Monitor IgE levels and eosinophils.'],
    ['8','Patient with recurrent facial/lip swelling + laryngeal oedema. C4 low. C1-esterase inhibitor low.\nDiagnosis and acute treatment?','Hereditary Angioedema (HAE). NOT allergic. Adrenaline does NOT work. Treat with C1-INH concentrate or icatibant (bradykinin B2 receptor blocker).'],
    ['9','Asthmatic athlete uses salbutamol frequently. Serum K+ is 2.8 mmol/L. Why?','Salbutamol causes hypokalaemia — drives K+ into cells via Na/K ATPase. Replace potassium IV. Check electrolytes in all acute severe asthma.'],
    ['10','Theophylline patient presents with vomiting + arrhythmia. Just started erythromycin. Why?','Erythromycin inhibits CYP1A2 → reduced theophylline metabolism → toxicity. Check theophylline blood level. Normal range 10-20 mg/L.'],
    ['11','Pregnant asthmatic asks if she should stop her ICS. Your advice?','CONTINUE ICS and all asthma medications. Uncontrolled asthma causes fetal hypoxia — far more dangerous than ICS. All step 1-4 drugs are safe in pregnancy.'],
    ['12','Patient with recurrent anaphylaxis after eating, urticaria, wheeze. Tryptase raised at 1h.\nWhat confirms anaphylaxis?','Raised serum tryptase (taken within 1-3h). Also: baseline tryptase at 24h (must be lower). Management: epinephrine 0.5mg IM, antihistamine, steroid. Investigate trigger with RAST.'],
]
story.append(plain_table(triggers,[CW*0.04, CW*0.41, CW*0.55]))
memory_hook('TOP TRIGGERS: PaCO2 rising = ITU. Silent chest = life-threatening. VCD = laryngoscopy + speech therapy. HAE = C4 low + icatibant (NOT adrenaline). Samter = NSAIDs + nasal polyps + asthma. ABPA = IgE > 1000 + bronchiectasis. Theophylline + erythromycin = toxicity. Pregnancy = CONTINUE inhalers.', story)
divider(story)

# §13 PACES + Minimal Resources
sec_header('Section 13: PACES Examination Guide + Minimal Resources Summary', story)
professor_says('PACES tests your examination skill, communication, and clinical reasoning. For asthma, the most likely stations are: Respiratory examination (Station 1), History Taking (Station 2), and Communication (Station 4). Know the full structured approach.', story)

story.append(bp('<b>PACES Station 1 — Respiratory Examination: What to Look For in Asthma:</b>'))
paces_exam = [
    ['Examination Step','What to Look For','What It Means in Asthma'],
    ['General inspection\n(first 10 seconds)','Sitting forward, tripod position.\nAccessory muscles visible.\nSpeaking in short phrases.\nInhaler or spacer nearby.','Forward lean = maximises lung volume.\nAccessory muscles = severe.\nCannot complete sentences = acute severe.'],
    ['Respiratory rate','Count for 30 seconds x2.\nNormal: 12-16/min.','> 25/min = acute severe asthma feature.\n> 30/min = critical.'],
    ['Peak flow (PEFR)','Ask patient to perform PEFR\n(if not in acute distress).\nCompare to predicted or best.','< 50% = severe. < 33% = life-threatening.\nCentral bedside diagnostic tool.'],
    ['Chest expansion','Both hands on chest wall.\nCompare both sides.','Equal but reduced globally in\nacute attack (both sides narrow equally).'],
    ['Percussion','Resonant or hyper-resonant.','Hyper-resonant = air trapping (severe).\nDullness = consolidation or effusion\n(not asthma — suggests another cause).'],
    ['Auscultation','Listen anteriorly + posteriorly\nall zones. Listen in expiration.','Expiratory wheeze — polyphonic\n(many pitches) in asthma.\nSilent chest = no air moving = emergency.'],
    ['Look for complications','Finger clubbing (NOT asthma).\nPursed lip breathing.\nBarrel chest (COPD).','Clubbing = NOT asthma → check for bronchiectasis\nor lung cancer. Barrel chest → COPD.\nIf clubbing present, reconsider diagnosis.'],
]
story.append(plain_table(paces_exam,[CW*0.22,CW*0.35,CW*0.43]))

story.append(Spacer(1, 8))
story.append(bp('<b>PACES Station 2 — History Taking: Structured Asthma History:</b>'))
for pt in [
    '<b>Opening:</b> "Tell me about your breathing problems from the beginning."',
    '<b>SOCRATES for dyspnoea:</b> Site (chest tightness) — Onset (sudden, gradual?) — Character (wheeze, cough, tight?) — Radiation — Alleviating/Aggravating — Timing (night, exercise, work) — Severity (PEFR diary, ED visits)',
    '<b>Key questions:</b> Any trigger? Better on holidays? On NSAIDs or beta-blockers? Have you had this since childhood? Any nasal polyps? Family history of asthma/eczema/hayfever?',
    '<b>Check inhaler use:</b> How do you use your inhaler? Do you use a spacer? Do you rinse your mouth after? When did you last take it today?',
    '<b>Impact on life:</b> Work? Exercise? Sleep? School/study? Sport? Days off? Recent hospital admissions?',
    '<b>Systems review:</b> Heartburn or reflux (GERD)? Snoring or nasal drip (rhinitis)? Eczema or skin problems?',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 8))

story.append(bp('<b>PACES Communication — Explaining Asthma and Inhalers to Patient:</b>'))
for pt in [
    '"Your breathing problem is called asthma. Asthma means the breathing tubes in your lungs are swollen and sometimes squeeze tight."',
    '"The blue inhaler (salbutamol) opens the tubes quickly — use it when you feel tight or wheezy. It works in minutes."',
    '"The brown/orange inhaler (your steroid preventer) reduces the swelling — you must use it EVERY DAY even when you feel well. It does NOT open the tubes immediately — it prevents attacks."',
    '"ALWAYS rinse your mouth with water after the brown inhaler to prevent a fungal infection in your mouth."',
    '"Your triggers are: [cats / exercise / cold air / dust]. Avoiding these is as important as your medication."',
    '"If you feel very breathless, use 4-10 puffs of your blue inhaler with a spacer. If not better in 10 minutes, call 999 (emergency)."',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 8))

# Minimal resources box
minimal_rows = [
    [Paragraph('<b>MINIMAL RESOURCES SUMMARY — Managing Asthma With Limited Equipment</b>', sAlert)],
    [Paragraph('If only ONE drug available: Salbutamol MDI via homemade spacer (plastic bottle with hole). 10 puffs = similar to nebuliser.', sBody)],
    [Paragraph('If no nebuliser: MDI + spacer. 4-8 puffs every 20 min. Just as effective as nebuliser in moderate attack if good technique.', sBody)],
    [Paragraph('If no spirometer: Serial PEFR with handheld meter is sufficient for diagnosis (diurnal variation > 20%).', sBody)],
    [Paragraph('If no IV access: Oral prednisolone 40-50mg is as effective as IV hydrocortisone for most acute attacks.', sBody)],
    [Paragraph('If no pulse oximeter: Respiratory rate + accessory muscle use + speech + PEFR = proxy severity markers.', sBody)],
    [Paragraph('If no FeNO or spirometry: Blood eosinophils > 0.3 + high total IgE + clinical history = enough to start ICS trial.', sBody)],
    [Paragraph('In resource-limited settings: Prioritise — Salbutamol + ICS + Oral prednisolone. These three cover 90% of acute and chronic asthma management.', sBody)],
]
minT1 = TableStyle([
    ('BACKGROUND',(0,0),(0,0),HexColor('#fff3cd')),
    ('BACKGROUND',(0,1),(-1,-1),HexColor('#fffde7')),
    ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),10),
    ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
    ('TOPPADDING',(0,0),(0,0),8),('BOTTOMPADDING',(-1,-1),(-1,-1),8),
])
minTO = TableStyle([
    ('BOX',(0,0),(-1,-1),2,HexColor('#f0a500')),
    ('BACKGROUND',(0,0),(-1,-1),HexColor('#fff3cd')),
    ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
    ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),
])
innerMin = Table(minimal_rows, colWidths=[CW-4])
innerMin.setStyle(minT1)
outerMin = Table([[innerMin]], colWidths=[CW])
outerMin.setStyle(minTO)
story.append(outerMin)
story.append(Spacer(1, 10))
memory_hook('MINIMAL RESOURCES: MDI + plastic bottle spacer = just as good as nebuliser. Oral prednisolone = as good as IV hydrocortisone. PEFR meter alone = diagnosis tool. Salbutamol + ICS + prednisolone = the essential three.', story)
divider(story)

# Master Memory Summary
sGrn  = ParagraphStyle('GR',  fontName='DV',   fontSize=9.5, leading=14, textColor=HexColor('#155724'), spaceAfter=0)
sGrnB = ParagraphStyle('GRB', fontName='DV-B', fontSize=11,  leading=16, textColor=HexColor('#155724'), spaceAfter=2)
gTS1 = TableStyle([
    ('BACKGROUND',(0,0),(-1,-1),HexColor('#d4edda')),
    ('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),10),
    ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
    ('TOPPADDING',(0,0),(0,0),10),('BOTTOMPADDING',(0,-1),(0,-1),10),
])
gTSO = TableStyle([
    ('BOX',(0,0),(-1,-1),2.5,HexColor('#28a745')),
    ('BACKGROUND',(0,0),(-1,-1),HexColor('#d4edda')),
    ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
    ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),
])
gRows = [
    [Paragraph('MASTER MEMORY SUMMARY — ASTHMA, LARYNGEAL SPASM & AIRWAY DISEASE', sGrnB)],
    [Paragraph('DEFINITION: Asthma = reversible, variable airflow obstruction + airway hyperresponsiveness + inflammation. Three changes: bronchoconstriction + eosinophilic inflammation + mucus plugging.', sGrn)],
    [Paragraph('MECHANISM: Allergen > IgE on mast cells > histamine + leukotrienes (early phase 15 min) > eosinophils + T-cells (late phase 4-8h). Salbutamol = early phase. Steroids = late phase.', sGrn)],
    [Paragraph('DIAGNOSIS: FEV1/FVC < 0.7 + > 12% and > 200mL reversibility after salbutamol. Or PEFR diurnal variation > 20%. FeNO > 40 ppb = eosinophilic. Symptom triad: wheeze + breathlessness + cough (nocturnal).', sGrn)],
    [Paragraph('SEVERITY (BTS): Moderate = PEFR 50-75%, RR < 25, SpO2 > 92%, speech normal. Severe = PEFR 33-50%, RR > 25, HR > 110, sentences broken. Life-threatening = PEFR < 33%, SpO2 < 92%, SILENT CHEST, confusion, bradycardia, high PaCO2.', sGrn)],
    [Paragraph('ACUTE MANAGEMENT: Oxygen (target 94-98%) + Salbutamol 2.5-5mg neb (repeat 20 min) + Ipratropium 500mcg neb + Hydrocortisone 100mg IV QDS or prednisolone 40-50mg oral + Magnesium 2g IV over 20 min (severe/LT). Call ITU if PaCO2 rising or not improving.', sGrn)],
    [Paragraph('BTS LADDER: Step 1 = SABA PRN. Step 2 = + ICS (low dose). Step 3 = + LABA (ALWAYS with ICS). Step 4 = increase ICS + LTRA. Step 5 = oral steroids + biologics (specialist). LABA NEVER alone in asthma.', sGrn)],
    [Paragraph('BIOLOGICS: Omalizumab = anti-IgE, atopic asthma, high IgE. Mepolizumab/Benralizumab = anti-IL-5, eosinophils > 0.3. Dupilumab = anti-IL-4R/IL-13, broad. Tezepelumab = anti-TSLP, works in non-eosinophilic too.', sGrn)],
    [Paragraph('DIFFERENTIALS: VCD = inspiratory wheeze + normal spirometry + laryngoscopy. Anaphylaxis = urticaria + tryptase up + epinephrine NOW. HAE = C4 low + C1-INH low + icatibant (NOT adrenaline). ABPA = IgE > 1000 + Aspergillus IgE + central bronchiectasis.', sGrn)],
    [Paragraph('DRUGS CONTRAINDICATED: NSAIDs (leukotrienes surge). Beta-blockers (bronchoconstriction even eye drops). ACE inhibitors cause cough (not bronchospasm). Samter triad: asthma + nasal polyps + NSAID sensitivity.', sGrn)],
    [Paragraph('KEY COMPLICATIONS: PaCO2 rising = Type 2 RF = ITU. Pneumothorax = sudden unilateral pain. Silent chest = no air = emergency. Long-term steroids = bone protection (bisphosphonate + Ca + D3). ICS = rinse mouth to prevent thrush.', sGrn)],
    [Paragraph('SPECIAL SITUATIONS: Pregnancy = SAFE to continue ALL inhalers. Exercise-induced = salbutamol 15 min before + montelukast. Occupational = serial PEFR (better on holiday = OA). Theophylline + erythromycin = toxicity (check level). Hypokalaemia from salbutamol = check K+ in severe attacks.', sGrn)],
    [Paragraph('PACES: Look for forward lean + accessory muscles + expiratory wheeze. Clubbing NOT asthma. Silent chest = emergency. PEFR at bedside = essential measure. Communication: "Use brown inhaler EVERY DAY. Blue inhaler = rescue only. Always rinse mouth after brown."', sGrn)],
]
innerG = Table(gRows, colWidths=[CW-4])
innerG.setStyle(gTS1)
outerG = Table([[innerG]], colWidths=[CW])
outerG.setStyle(gTSO)
story.append(outerG)
story.append(Spacer(1, 14))

# Footer note
story.append(HRFlowable(width=CW, thickness=1.5, color=HexColor('#0d5c63'), spaceAfter=6))
story.append(Paragraph('MRCP Revision Note: Asthma, Laryngeal Spasm and Airway Disease  |  BTS/SIGN Guidelines 2022  |  Ganesh & Kuruvilla Prescribing Reference  |  Sections 1-13 inclusive', ParagraphStyle('FT', fontName='DV-I', fontSize=8, leading=11, textColor=HexColor('#555555'), alignment=1)))

# Build document
doc.build(story)
print('SUCCESS: Asthma_Laryngeal_MRCP_Note.pdf written to', OUT)
