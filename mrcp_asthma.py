import os
from io import BytesIO
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, Image as RLImage)
from reportlab.lib.pagesizes import A4
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

TEAL   = HexColor('#0d5c63'); TEAL_M  = HexColor('#1a8a94')
TEAL_L = HexColor('#e0f4f5'); TEAL_XL = HexColor('#f0fafb')
AMBER  = HexColor('#fff3cd'); AMBER_B = HexColor('#e6a817')
GREEN_L= HexColor('#d4edda'); GREEN_D = HexColor('#28a745')
RED_L  = HexColor('#fde8e8'); RED_D   = HexColor('#c0392b')
ORA_L  = HexColor('#fef3e2'); ORA_D   = HexColor('#d4640a')
BLUE_L = HexColor('#e8f4fd'); BLUE_D  = HexColor('#2471a3')
PUR_L  = HexColor('#f5eef8'); PUR_D   = HexColor('#7d3c98')
NAVY   = HexColor('#1a1a2e'); WHITE   = HexColor('#ffffff')

PAGE_W, PAGE_H = A4; MARGIN = 18*mm; CW = PAGE_W - 2*MARGIN

doc = SimpleDocTemplate(OUT, pagesize=A4,
      leftMargin=MARGIN, rightMargin=MARGIN,
      topMargin=MARGIN, bottomMargin=MARGIN)

sTitle = ParagraphStyle('TT', fontName='DV-B', fontSize=20, leading=26,
         textColor=HexColor('#0d5c63'), spaceAfter=4, alignment=1)
sSub   = ParagraphStyle('TS', fontName='DV-I', fontSize=10, leading=14,
         textColor=HexColor('#1a8a94'), spaceAfter=2, alignment=1)
sH1    = ParagraphStyle('H1', fontName='DV-B', fontSize=13, leading=17,
         textColor=HexColor('#0d5c63'), spaceBefore=8, spaceAfter=4)
sH2    = ParagraphStyle('H2', fontName='DV-B', fontSize=10, leading=14,
         textColor=HexColor('#0d5c63'), spaceAfter=2)
sBody  = ParagraphStyle('Bo', fontName='DV', fontSize=9, leading=14,
         textColor=HexColor('#1a1a2e'), spaceAfter=3)
sPro   = ParagraphStyle('Pr', fontName='DV-I', fontSize=9, leading=14,
         textColor=HexColor('#1a8a94'), spaceAfter=4)
sImg   = ParagraphStyle('Im', fontName='DV-I', fontSize=8, leading=12,
         textColor=HexColor('#555555'), spaceAfter=4, alignment=1)
sAlert = ParagraphStyle('Al', fontName='DV-B', fontSize=9, leading=13,
         textColor=HexColor('#721c24'), spaceAfter=0)
sMem   = ParagraphStyle('MH', fontName='DV-B', fontSize=8.5, leading=13,
         textColor=HexColor('#856404'), spaceAfter=0)

def bp(text, st=None):
    return Paragraph(text, st or sBody)

def sec_header(title, story):
    story.append(Spacer(1, 6))
    story.append(Paragraph(title, sH1))

def divider(story):
    story.append(HRFlowable(width=CW, thickness=0.5, color=TEAL_M, spaceAfter=4))

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
        ('GRID',(0,0),(-1,-1),0.5,TEAL_M),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    return t

def alert_box(text, story):
    t = Table([[Paragraph(f'<b>ALERT: {text}</b>', sAlert)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),RED_L),
        ('BOX',(0,0),(-1,-1),1.5,RED_D),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(t); story.append(Spacer(1,4))

def info_box(text, story, color=None, border=None):
    bg = color or BLUE_L; bd = border or BLUE_D
    t = Table([[Paragraph(text, sBody)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),bg),
        ('BOX',(0,0),(-1,-1),1.5,bd),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(t); story.append(Spacer(1,4))

def image_search_box(term, site, story):
    txt = f'IMAGE: Search <b>"{term}"</b> on <b>{site}</b> to see a picture of this.'
    t = Table([[Paragraph(txt, sImg)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),HexColor('#f8f9fa')),
        ('BOX',(0,0),(-1,-1),1,HexColor('#adb5bd')),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story.append(t); story.append(Spacer(1,4))

def professor_says(text, story):
    t = Table([[Paragraph(f'<i>Professor says: "{text}"</i>', sPro)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),TEAL_XL),
        ('BOX',(0,0),(-1,-1),1,TEAL_M),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(t); story.append(Spacer(1,4))

def memory_hook(text, story):
    t = Table([[Paragraph(f'MEMORY: {text}', sMem)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),AMBER),
        ('BOX',(0,0),(-1,-1),1.5,AMBER_B),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(t); story.append(Spacer(1,4))

# ── PIL helpers ───────────────────────────────────────────────────────────────
def arr_r(draw, x, y, length=36, col='#0d5c63'):
    draw.line([(x,y),(x+length,y)], fill=col, width=2)
    draw.polygon([(x+length,y),(x+length-7,y-4),(x+length-7,y+4)], fill=col)

def arr_d(draw, x, y, length=28, col='#0d5c63'):
    draw.line([(x,y),(x,y+length)], fill=col, width=2)
    draw.polygon([(x,y+length),(x-4,y+length-7),(x+4,y+length-7)], fill=col)

def i2r(img, W):
    scale = W / img.width
    nH = int(img.height * scale)
    img = img.resize((int(W), nH), Image.LANCZOS)
    buf = BytesIO(); img.save(buf, 'PNG'); buf.seek(0)
    return RLImage(buf, width=W, height=nH)

print('Building PIL diagrams...')

# ── PIL 1: Airway Anatomy ─────────────────────────────────────────────────────
def make_airway_anatomy():
    W, H = 900, 360
    img = Image.new('RGB', (W, H), '#f0fafb')
    draw = ImageDraw.Draw(img)
    try:
        fB = ImageFont.truetype(FONT_DIR+'DejaVuSans-Bold.ttf', 13)
        fS = ImageFont.truetype(FONT_DIR+'DejaVuSans.ttf', 11)
        fXS= ImageFont.truetype(FONT_DIR+'DejaVuSans.ttf', 9)
    except:
        fB = fS = fXS = ImageFont.load_default()
    draw.rectangle([0,0,W-1,H-1], fill='#f0fafb', outline='#1a8a94', width=2)
    draw.text((W//2, 16), 'AIRWAY ANATOMY: WHERE EACH CONDITION OCCURS', font=fB, fill='#0d5c63', anchor='mm')

    # Airway chain (top to bottom, left column)
    levels = [
        (200, 55,  '#fde8e8', '#c0392b', 'NOSE / MOUTH',    'Entry point for air and allergens'),
        (200, 110, '#fef3e2', '#d4640a', 'PHARYNX (throat)', 'Shared passage for food and air'),
        (200, 165, '#f5eef8', '#7d3c98', 'LARYNX (voice box)','Contains vocal cords. UPPER airway.'),
        (200, 220, '#fff3cd', '#e6a817', 'TRACHEA (windpipe)','Carries air down to lungs.'),
        (200, 275, '#e8f4fd', '#2471a3', 'BRONCHI (main tubes)','Left and right bronchus. Branches.'),
        (200, 330, '#d4edda', '#28a745', 'BRONCHIOLES + ALVEOLI','Tiny airways. Gas exchange here.'),
    ]
    for cx, cy, bg, bd, name, detail in levels:
        bw=330; bh=36
        draw.rectangle([cx-bw//2, cy-bh//2, cx+bw//2, cy+bh//2], fill=bg, outline=bd, width=2)
        draw.text((cx, cy-8), name, font=fB, fill=bd, anchor='mm')
        draw.text((cx, cy+9), detail, font=fXS, fill='#1a1a2e', anchor='mm')
        if cy < 330:
            arr_d(draw, cx, cy+bh//2, length=16, col=bd)

    # Right column: conditions at each level
    conditions = [
        (640, 55,  '#fde8e8', '#c0392b', 'Allergens enter here', 'Pollens, dust, moulds, pet dander'),
        (640, 110, '#fef3e2', '#d4640a', 'Post-nasal drip', 'Can trigger cough + bronchoconstriction'),
        (640, 165, '#f5eef8', '#7d3c98', 'LARYNGOSPASM', 'VCD. Laryngeal oedema. HAE. Anaphylaxis.'),
        (640, 220, '#fff3cd', '#e6a817', 'Tracheal stenosis', 'Fixed obstruction. Stridor.'),
        (640, 275, '#e8f4fd', '#2471a3', 'LARGE AIRWAY obstruction', 'Foreign body. Tumour. Mucus plug.'),
        (640, 330, '#d4edda', '#28a745', 'ASTHMA / ALLERGIC BRONCHITIS', 'Bronchoconstriction. Inflammation. Mucus.'),
    ]
    for cx, cy, bg, bd, name, detail in conditions:
        bw=290; bh=36
        draw.rectangle([cx-bw//2, cy-bh//2, cx+bw//2, cy+bh//2], fill=bg, outline=bd, width=2)
        draw.text((cx, cy-8), name, font=fB, fill=bd, anchor='mm')
        draw.text((cx, cy+9), detail, font=fXS, fill='#1a1a2e', anchor='mm')
        # connecting line
        draw.line([(366, cy), (496, cy)], fill='#888888', width=1)
    draw.text((440, H-14), 'Upper airway = larynx and above. Lower airway = below larynx.', font=fS, fill='#555555', anchor='mm')
    return i2r(img, CW)

# ── PIL 2: Asthma Pathophysiology ─────────────────────────────────────────────
def make_asthma_path():
    W, H = 900, 380
    img = Image.new('RGB', (W, H), '#fff8f0')
    draw = ImageDraw.Draw(img)
    try:
        fB = ImageFont.truetype(FONT_DIR+'DejaVuSans-Bold.ttf', 13)
        fS = ImageFont.truetype(FONT_DIR+'DejaVuSans.ttf', 11)
        fXS= ImageFont.truetype(FONT_DIR+'DejaVuSans.ttf', 9)
    except:
        fB = fS = fXS = ImageFont.load_default()
    draw.rectangle([0,0,W-1,H-1], fill='#fff8f0', outline='#d4640a', width=2)
    draw.text((W//2, 16), 'ASTHMA: NORMAL AIRWAY vs ASTHMATIC AIRWAY', font=fB, fill='#d4640a', anchor='mm')

    # LEFT: Normal airway (cross-section)
    draw.rectangle([20, 35, 420, H-20], fill='#d4edda', outline='#28a745', width=2)
    draw.text((220, 52), 'NORMAL AIRWAY', font=fB, fill='#155724', anchor='mm')
    # Draw airway cross-section (circle)
    draw.ellipse([120, 70, 320, 200], fill='#ffffff', outline='#28a745', width=3)
    draw.ellipse([155, 100, 285, 170], fill='#e8f4fd', outline='#2471a3', width=2)
    draw.text((220, 135), 'WIDE OPEN', font=fB, fill='#2471a3', anchor='mm')
    draw.text((220, 150), 'LUMEN (air space)', font=fXS, fill='#2471a3', anchor='mm')
    # Labels
    items_n = [
        (220, 220, 'Thin smooth muscle layer'),
        (220, 238, 'Normal thin mucus lining'),
        (220, 256, 'No inflammation'),
        (220, 274, 'Air flows freely'),
        (220, 292, 'Normal FEV1/FVC ratio > 70%'),
    ]
    for x, y, txt in items_n:
        draw.text((x, y), txt, font=fXS, fill='#155724', anchor='mm')

    # RIGHT: Asthmatic airway
    draw.rectangle([480, 35, W-20, H-20], fill='#fde8e8', outline='#c0392b', width=2)
    draw.text((690, 52), 'ASTHMATIC AIRWAY (ATTACK)', font=fB, fill='#c0392b', anchor='mm')
    # Thickened wall
    draw.ellipse([570, 70, 810, 200], fill='#fde8e8', outline='#c0392b', width=8)
    draw.ellipse([630, 100, 750, 170], fill='#fef3e2', outline='#d4640a', width=2)
    # Mucus plug
    draw.ellipse([655, 118, 725, 152], fill='#e6a817', outline='#856404', width=2)
    draw.text((690, 135), 'MUCUS', font=fXS, fill='#856404', anchor='mm')
    draw.text((690, 148), 'PLUG', font=fXS, fill='#856404', anchor='mm')
    # Wall label
    draw.text((820, 135), 'THICK', font=fXS, fill='#c0392b', anchor='lm')
    draw.text((820, 148), 'WALL', font=fXS, fill='#c0392b', anchor='lm')
    items_a = [
        (690, 220, '3 main problems:'),
        (690, 238, '1. BRONCHOCONSTRICTION (muscle squeezes)'),
        (690, 256, '2. INFLAMMATION (wall swells, thickens)'),
        (690, 274, '3. MUCUS HYPERSECRETION (blocks lumen)'),
        (690, 292, 'FEV1/FVC ratio LOW. REVERSIBLE with bronchodilator.'),
    ]
    for x, y, txt in items_a:
        draw.text((x, y), txt, font=fXS, fill='#721c24', anchor='mm')

    # Triggers box at bottom
    draw.rectangle([20, 315, W-20, H-20], fill='#fff3cd', outline='#e6a817', width=2)
    draw.text((W//2, 332), 'COMMON TRIGGERS: Allergens | Cold air | Exercise | Smoke | Viral URTI | Emotion | NSAIDs/aspirin | Beta-blockers | Occupational', font=fXS, fill='#856404', anchor='mm')
    draw.text((W//2, H-18), 'All three problems (constriction + inflammation + mucus) happen together during an attack.', font=fS, fill='#555555', anchor='mm')
    return i2r(img, CW)

# ── PIL 3: Severity Classification ────────────────────────────────────────────
def make_severity():
    W, H = 900, 320
    img = Image.new('RGB', (W, H), '#ffffff')
    draw = ImageDraw.Draw(img)
    try:
        fB = ImageFont.truetype(FONT_DIR+'DejaVuSans-Bold.ttf', 13)
        fS = ImageFont.truetype(FONT_DIR+'DejaVuSans.ttf', 10)
        fXS= ImageFont.truetype(FONT_DIR+'DejaVuSans.ttf', 9)
    except:
        fB = fS = fXS = ImageFont.load_default()
    draw.rectangle([0,0,W-1,H-1], fill='#ffffff', outline='#1a8a94', width=2)
    draw.text((W//2, 16), 'ACUTE ASTHMA: SEVERITY CLASSIFICATION (BTS/SIGN)', font=fB, fill='#0d5c63', anchor='mm')

    grades = [
        ('#d4edda','#28a745','MODERATE','PEFR 50-75%','SpO2 >= 92%','Normal speech','HR < 110','RR < 25'),
        ('#fff3cd','#e6a817','ACUTE SEVERE','PEFR 33-50%','SpO2 >= 92%','Cannot complete','sentences','HR >= 110 or RR >= 25'),
        ('#fde8e8','#c0392b','LIFE-THREATENING','PEFR < 33%','SpO2 < 92%','Silent chest','Cyanosis / Exhaustion','Bradycardia / Confusion'),
        ('#f5eef8','#7d3c98','NEAR-FATAL','Rising PaCO2','Needs mechanical','ventilation','IMMEDIATE ICU','Arrest risk'),
    ]
    bw=(W-40)//4-6; bh=H-50
    sx=22
    for i,(bg,bd,t1,t2,t3,t4,t5,t6) in enumerate(grades):
        x0=sx+i*(bw+6); y0=36
        draw.rectangle([x0,y0,x0+bw,y0+bh], fill=bg, outline=bd, width=2)
        draw.text((x0+bw//2, y0+18), t1, font=fB, fill=bd, anchor='mm')
        draw.line([(x0+10,y0+30),(x0+bw-10,y0+30)], fill=bd, width=1)
        for j, txt in enumerate([t2,t3,t4,t5,t6]):
            draw.text((x0+bw//2, y0+46+j*40), txt, font=fXS, fill='#1a1a2e', anchor='mm')
    draw.text((W//2, H-12), 'PEFR = Peak Expiratory Flow Rate (% of personal best or predicted)', font=fS, fill='#555555', anchor='mm')
    return i2r(img, CW)

# ── PIL 4: Differential Diagnosis Map ─────────────────────────────────────────
def make_diff_map():
    W, H = 900, 360
    img = Image.new('RGB', (W, H), '#f0fafb')
    draw = ImageDraw.Draw(img)
    try:
        fB = ImageFont.truetype(FONT_DIR+'DejaVuSans-Bold.ttf', 12)
        fS = ImageFont.truetype(FONT_DIR+'DejaVuSans.ttf', 10)
        fXS= ImageFont.truetype(FONT_DIR+'DejaVuSans.ttf', 9)
    except:
        fB = fS = fXS = ImageFont.load_default()
    draw.rectangle([0,0,W-1,H-1], fill='#f0fafb', outline='#1a8a94', width=2)
    draw.text((W//2, 16), 'DIFFERENTIAL DIAGNOSIS: RECURRENT BREATHLESSNESS IN YOUNG ADULT', font=fB, fill='#0d5c63', anchor='mm')

    diffs = [
        # (cx, cy, bg, bd, title, clue1, clue2)
        (130, 95,  '#d4edda','#28a745','ASTHMA','WHEEZE. Responds to','steroids + bronchodilator.'),
        (340, 95,  '#f5eef8','#7d3c98','VCD / ILO','STRIDOR not wheeze.','Does NOT respond to Rx.'),
        (560, 95,  '#fde8e8','#c0392b','ANAPHYLAXIS','Urticaria. Hypotension.','Adrenaline reverses it.'),
        (770, 95,  '#fef3e2','#d4640a','LARYNGOSPASM','Very sudden. GERD link.','Brief episodes.'),
        (130, 230, '#e8f4fd','#2471a3','ABPA','Eosinophilia. Aspergillus','IgE raised. Plugs.'),
        (340, 230, '#fff3cd','#e6a817','HAE','Low C4. Family history.','NO urticaria. Slow onset.'),
        (560, 230, '#fde8e8','#856404','EOSINOPHILIC\nBRONCHITIS','Cough only. No wheeze.','FeNO raised. Sputum eos.'),
        (770, 230, '#f0fafb','#0d5c63','GERD-INDUCED','Night symptoms. Acid taste.','Responds to PPI.'),
    ]
    bw=160; bh=80
    for cx,cy,bg,bd,t1,t2,t3 in diffs:
        draw.rectangle([cx-bw//2,cy-bh//2,cx+bw//2,cy+bh//2], fill=bg, outline=bd, width=2)
        draw.text((cx, cy-28), t1, font=fB, fill=bd, anchor='mm')
        draw.text((cx, cy-5), t2, font=fXS, fill='#1a1a2e', anchor='mm')
        draw.text((cx, cy+13), t3, font=fXS, fill='#1a1a2e', anchor='mm')

    draw.text((W//2, H-30), 'KEY QUESTION: Does it respond to bronchodilators and steroids?', font=fS, fill='#0d5c63', anchor='mm')
    draw.text((W//2, H-14), 'YES = asthma-spectrum. NO = upper airway / non-asthmatic cause.', font=fS, fill='#555555', anchor='mm')
    return i2r(img, CW)

img_airway   = make_airway_anatomy()
img_asthpath = make_asthma_path()
img_severity = make_severity()
img_diffmap  = make_diff_map()
print('PIL diagrams done.')

story = []

# ── Title ──────────────────────────────────────────────────────────────────────
story.append(Paragraph('ACUTE ASTHMA, LARYNGEAL SPASM &amp; ALLERGIC AIRWAY DISEASE', sTitle))
story.append(Paragraph('Comprehensive MRCP Revision Note | Parts 1, 2 &amp; PACES', sSub))
story.append(Paragraph('All Causes of Recurrent Breathlessness in a Young Adult — From Zero to Expert', sSub))
story.append(Spacer(1, 8))
story.append(HRFlowable(width=CW, thickness=2, color=TEAL, spaceAfter=6))

# ── §1 CLINICAL SCENARIO + OVERVIEW ──────────────────────────────────────────
sec_header('Section 1: The Clinical Scenario — Understanding This Patient', story)

professor_says('Before we learn theory, let us understand this specific patient. A 22-year-old woman. Childhood episodes of breathlessness. Similar episodes for 4-5 days. Responds to inhaled steroids and IV steroids. But keeps coming back. Sometimes coughing. Sometimes completely breathless. This is the puzzle we will solve completely.', story)

story.append(bp('<b>The Clinical Scenario:</b>'))
scenario_points = [
    '<b>Age:</b> 22–24 years old. Young adult.',
    '<b>Sex:</b> Female. This is important — females have higher rates of severe asthma and certain conditions (VCD, HAE).',
    '<b>Past history:</b> Similar episodes in childhood. This strongly suggests atopic (allergic) disease — asthma, allergic rhinitis, or eczema.',
    '<b>Current problem:</b> Episodes over 4–5 days. Not one single attack — RECURRENT attacks. This tells us the trigger is ongoing or the treatment is not fully stopping the problem.',
    '<b>Response to treatment:</b> Responds to inhaled steroids + IV prednisolone/dexamethasone. This confirms airway inflammation is part of the problem.',
    '<b>But keeps recurring:</b> This means either: (1) The trigger is still present. (2) The treatment dose is not enough. (3) There is a second diagnosis alongside asthma. (4) The patient is not using inhalers correctly.',
    '<b>Symptoms:</b> Sometimes coughing only. Sometimes completely breathless. Variable symptoms suggest reversible airway obstruction — hallmark of asthma.',
]
for pt in scenario_points:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 5))

story.append(bp('<b>The Big Question — What Is Causing This?</b>'))
story.append(bp('There are MANY possible causes of recurrent breathlessness and cough in a young woman. We will study all of them in detail. The key is to diagnose correctly — because the treatment is COMPLETELY DIFFERENT for each condition.'))
story.append(Spacer(1, 3))

story.append(img_diffmap)
story.append(bp('Differential diagnosis map — all possible causes of recurrent breathlessness in a young adult', sImg))
story.append(Spacer(1, 5))

overview_table = [
    ['Condition','Simple Name','Main Symptom','Responds to Steroids?','Key Clue'],
    ['Asthma','Airways close up\nand get inflamed','Wheeze + breathlessness\n+ cough. Episodic.','YES — strongly','Childhood history.\nReversible obstruction.\nPEFR improves.'],
    ['VCD / ILO\n(Vocal Cord Dysfunction)','Vocal cords close\ninwards during breathing','STRIDOR (high-pitched\nnoise on breathing IN).\nNot wheeze.','NO — does not respond','Anxiety link.\nNormal tests between\nepisodes. Diagnosed\nby laryngoscopy.'],
    ['Laryngospasm\n(larynx muscle spasm)','Brief sudden complete\nclosure of vocal cords','Sudden gasping.\nCannot breathe for\na few seconds.\nThen resolves.','NO — brief and\nself-limiting','GERD trigger.\nAnxiety. Chlorine.\nBreathing exercises\ncure it.'],
    ['Laryngeal Oedema\n(Anaphylaxis)','Allergic swelling of\nthe larynx — airway\nbecomes blocked','Stridor. Drooling.\nRapid onset.\nMay have hives/rash.','PARTIAL — needs\nadrenaline primarily','Triggers: nuts,\nbee sting, drug.\nAdrenaline reverses it.'],
    ['HAE\n(Hereditary Angioedema)','Inherited swelling of\ndeep tissues —\ncan block airway','Swelling of face,\nlips, tongue, larynx.\nAbdominal colic.','NO — does NOT\nrespond to adrenaline,\nsteroids, or antihistamine','C4 low. C1-INH\nlow. Family history.\nNo urticaria (hives).'],
    ['ABPA\n(Allergic Bronchopulmonary\nAspergillosis)','Allergic reaction to\nfungus (Aspergillus)\nliving in airways','Wheezing. Brownish\nmucus plugs.\nRecurrent collapse.','YES — steroids\nclear it','Aspergillus IgE high.\nCentral bronchiectasis\non CT. Eosinophilia.'],
    ['Eosinophilic Bronchitis','Airway inflammation\nwith high eosinophil\ncells. Not asthma.','COUGH — only.\nNo wheeze.\nNo airflow obstruction.','YES — ICS works','FeNO raised.\nSputum eosinophils.\nNormal spirometry.'],
    ['GERD-Induced\n(Acid reflux)','Stomach acid flows\nup to larynx and\ntriggers airway reflex','Chronic cough.\nHoarseness.\nWorse at night / after\nmeals. Lying flat.','PARTIAL — PPI\nis the main treatment','Heartburn history.\nNo wheeze between\nepisodes. PPI test.'],
]
story.append(plain_table(overview_table,[CW*0.14,CW*0.16,CW*0.17,CW*0.17,CW*0.36]))

memory_hook('RECURRENT BREATHLESSNESS IN YOUNG ADULT: Think ASTHMA first. Then ask: does it respond to bronchodilators? Does it have stridor (upper airway) or wheeze (lower airway)? Is there urticaria (anaphylaxis)? Family history of swelling (HAE)? Acid reflux? Anxiety?', story)
divider(story)

# ── §2 ANATOMY ────────────────────────────────────────────────────────────────
sec_header('Section 2: Anatomy — The Airway From Top to Bottom', story)

professor_says('To understand all these conditions, you must know the airway anatomy. Think of the airway as a tree — wide trunk (trachea) that branches into smaller and smaller twigs (bronchioles). Different conditions affect different parts of this tree.', story)

story.append(img_airway)
story.append(bp('Airway anatomy showing where each condition causes obstruction', sImg))
story.append(Spacer(1, 5))

story.append(bp('<b>Upper Airway (from nose to larynx):</b>'))
for pt in [
    '<b>Nose and sinuses:</b> Air enters. Warmed, moistened, filtered. Allergens (pollen, dust, mould spores) enter here first. Allergic rhinitis (hayfever) starts here and can worsen asthma.',
    '<b>Pharynx (FAR-inks):</b> Throat. The common passage for food and air. Post-nasal drip (mucus dripping down from nose) can trigger cough and bronchospasm.',
    '<b>Larynx (LAIR-inks) = the voice box:</b> Contains the vocal cords (two muscular folds). They vibrate to make sound. They should open fully during breathing. When they close abnormally = laryngospasm or VCD. The larynx is protected by the epiglottis (flap that closes during swallowing).',
    '<b>Vocal cords:</b> In normal breathing: wide open (like a V shape). In laryngospasm/VCD: close together (like a tiny slit — obstruction of airflow). In laryngeal oedema (swelling): swollen shut.',
    '<b>Epiglottis (ep-ih-GLOT-iss):</b> The flap above the larynx. Closes during swallowing. Can swell in severe anaphylaxis or epiglottitis (rare in adults).',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 5))

story.append(bp('<b>Lower Airway (from trachea downwards):</b>'))
for pt in [
    '<b>Trachea (TRAY-kee-ah) = windpipe:</b> The main central tube. 10–12cm long. Supported by C-shaped cartilage rings. Fixed — does not collapse. Tracheal stenosis (narrowing) causes a fixed obstruction.',
    '<b>Carina (kah-RY-nah):</b> The point where the trachea splits into left and right bronchi. Very sensitive to cough reflex.',
    '<b>Main bronchi (BRON-kye):</b> Right and left. Right bronchus is wider and more vertical — foreign bodies more commonly go to the right side.',
    '<b>Lobar and segmental bronchi:</b> Smaller branches going to each part of the lung.',
    '<b>Bronchioles (BRON-kee-oles):</b> The tiniest airways. Less than 1mm wide. NO cartilage to hold them open. They are held open only by the elastic recoil (pulling force) of surrounding lung tissue. In asthma, their muscle walls squeeze shut (bronchoconstriction).',
    '<b>Alveoli (al-VEE-oh-lie) = air sacs:</b> Tiny balloon-like structures. 300 million in each lung. Where oxygen crosses into blood and carbon dioxide crosses back out (gas exchange).',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 5))

story.append(bp('<b>Key Concept — Upper vs Lower Airway Obstruction:</b>'))
ul_table = [
    ['Feature','Upper Airway Obstruction\n(Larynx and above)','Lower Airway Obstruction\n(Bronchi and below)'],
    ['Sound produced','STRIDOR (STRY-dor) — harsh,\nhigh-pitched sound on BREATHING IN\n(inspiratory). Like a crowing or seal-bark sound.','WHEEZE — musical whistling sound\non BREATHING OUT (expiratory).\nCan also be inspiratory in severe asthma.'],
    ['When heard','During INSPIRATION (breathing in) mainly','During EXPIRATION (breathing out) mainly'],
    ['Conditions','Laryngospasm. VCD. Laryngeal oedema.\nAnaphylaxis. HAE. Epiglottitis. Croup.','Asthma. COPD. Allergic bronchitis.\nABPA. Eosinophilic bronchitis.'],
    ['Response to salbutamol\n(bronchodilator)','NO — salbutamol only opens LOWER\nairways. Cannot open the larynx.','YES — salbutamol opens bronchioles.'],
    ['Flow-volume loop\n(spirometry graph)','Variable extrathoracic obstruction:\nInspiratory limb is flat (cut off).','Variable intrathoracic obstruction:\nExpiratory limb shows concave shape.'],
]
story.append(plain_table(ul_table,[CW*0.2,CW*0.4,CW*0.4]))

info_box('<b>KEY CLINICAL POINT:</b> Stridor = upper airway. Wheeze = lower airway. They are DIFFERENT sounds in DIFFERENT places. A patient with VCD (vocal cord dysfunction) will make a STRIDOR sound — not a wheeze. Salbutamol will NOT help them. This is the most common reason VCD is misdiagnosed as asthma.', story)

image_search_box('upper vs lower airway obstruction flow volume loop comparison', 'Radiopaedia.org or Google Images', story)
memory_hook('STRIDOR = UPPER AIRWAY (larynx and above). WHEEZE = LOWER AIRWAY (bronchioles). Stridor is heard on BREATHING IN. Wheeze is heard on BREATHING OUT. Salbutamol only helps LOWER airway problems.', story)
divider(story)

# ── §3 ASTHMA — PATHOPHYSIOLOGY ───────────────────────────────────────────────
sec_header('Section 3: Asthma — Pathophysiology (How It Happens)', story)

professor_says('Asthma is the most common cause of recurrent breathlessness in young people. Understanding the mechanism tells you exactly why each drug works. This is a favourite in MRCP Part 1.', story)

story.append(bp('<b>What is Asthma? — Very Simple First:</b>'))
story.append(bp('Asthma (AZ-mah) = a long-term condition of the airways. The airways are too sensitive. They overreact to things that would not bother a normal person.'))
story.append(bp('Think of it like this: normal airways are like a calm river. In asthma, the airways are like a river that floods at the first sign of rain. A tiny trigger causes a massive overreaction.'))
story.append(Spacer(1, 5))

story.append(img_asthpath)
story.append(bp('Normal airway vs asthmatic airway — three simultaneous problems', sImg))
story.append(Spacer(1, 5))

story.append(bp('<b>Step 1: Sensitisation — The First Exposure</b>'))
story.append(bp('The first time a person with a genetic tendency (atopy) breathes in an allergen (e.g. cat dander), their immune system overreacts.'))
story.append(bp('The immune system makes <b>IgE antibodies</b> (a type of immune protein) that are specific to that allergen. These IgE antibodies attach to <b>mast cells</b> (fat-looking cells sitting in the airway lining). The mast cells are now primed — like a gun loaded and ready to fire.'))
story.append(Spacer(1, 3))

story.append(bp('<b>Step 2: The Allergic Reaction — The Second Exposure (Early Phase)</b>'))
story.append(bp('The next time the person breathes in the same allergen, it binds to the IgE on the mast cells. This triggers the mast cell to EXPLODE — releasing chemicals.'))
story.append(bp('The main chemicals released:'))
for pt in [
    '<b>Histamine</b> (HISS-tah-meen): Causes immediate bronchoconstriction (airway squeezes shut). Causes mucus production. Causes vasodilation.',
    '<b>Leukotrienes</b> (loo-KOH-try-eenz): More powerful than histamine. Cause prolonged bronchoconstriction. Cause mucus production. Released over hours.',
    '<b>Prostaglandins</b>: Cause airway inflammation and bronchoconstriction.',
    '<b>Tryptase</b>: Enzyme released from mast cells. A blood test for tryptase confirms anaphylaxis.',
]:
    story.append(bp(f'  • {pt}'))
story.append(bp('<b>Result:</b> Airways narrow (bronchoconstriction) within minutes. Peak at 15–30 minutes. This is the EARLY phase reaction.'))
story.append(Spacer(1, 3))

story.append(bp('<b>Step 3: The Late Phase — 4–8 Hours Later</b>'))
story.append(bp('4–8 hours later, a second wave of inflammation arrives. Eosinophils (ee-OH-sin-oh-fills — a type of white blood cell) and T-lymphocytes invade the airway wall.'))
story.append(bp('This is the LATE phase reaction. It causes: ongoing inflammation, thickening of the airway wall, continued airway narrowing.'))
story.append(bp('The late phase is why steroids are important — steroids target this inflammation. Salbutamol only helps the early phase (bronchoconstriction). It does NOT help the late phase inflammation.'))
story.append(Spacer(1, 3))

story.append(bp('<b>Step 4: Airway Remodelling — Long-Term Changes</b>'))
story.append(bp('If asthma is poorly controlled for years, permanent changes happen to the airway. This is called <b>remodelling</b>:'))
for pt in [
    'Smooth muscle in airway wall gets thicker and stronger (hypertrophy).',
    'Subepithelial fibrosis (sub-ep-ith-EE-lee-al fy-BRO-sis) — scar tissue under the surface lining.',
    'Blood vessel growth in the airway wall (angiogenesis).',
    'Goblet cell hyperplasia — more mucus-producing cells.',
    'These changes are IRREVERSIBLE. They cause persistent airflow limitation even between attacks.',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 4))

story.append(bp('<b>Three Core Problems in Every Asthma Attack:</b>'))
three_problems = [
    ['Problem','What Happens','Drug That Fixes It','Timing of Effect'],
    ['1. BRONCHOCONSTRICTION\n(airway muscle squeezes)','Smooth muscle in\nbronchiole walls tightens.\nAirway diameter reduces.\nAir cannot flow.','Salbutamol (SABA)\nIpratropium (SAMA)\nMagnesium sulphate','Minutes.\nImmediate relief.'],
    ['2. INFLAMMATION\n(wall swells, thickens)','Eosinophils, mast cells,\nT-cells infiltrate wall.\nWall becomes swollen\nand thickened.','Inhaled corticosteroids\n(ICS): budesonide,\nbeclometasone, fluticasone.\nOral/IV steroids.','Hours to days.\nNot immediate.'],
    ['3. MUCUS HYPERSECRETION\n(plugs block airways)','Goblet cells over-produce\nthick sticky mucus.\nMucus plugs block\nsmaller airways.','Hydration. Nebulised\nbronchodilators loosen.\nPhysiotherapy.\nDNase in bronchiectasis.','Hours.\nNeeds clearance.'],
]
story.append(plain_table(three_problems,[CW*0.22,CW*0.26,CW*0.28,CW*0.24]))

story.append(Spacer(1, 4))
story.append(bp('<b>Why Does This Patient\'s Asthma Keep Coming Back?</b>'))
story.append(bp('The steroids suppress the inflammation. The patient feels better. But if the TRIGGER is still present (e.g. cat at home, mould in the bedroom, occupational exposure), the inflammation returns as soon as the steroid effect wears off.'))
story.append(bp('This is called <b>refractory</b> or <b>difficult-to-control asthma</b>. The question to ask is: <b>what is the ongoing trigger?</b>'))
for pt in [
    'Is there a pet at home (cat dander is the most common persistent allergen)?',
    'Is there mould (damp house, bathroom, old books)?',
    'Is she using NSAIDs or aspirin (can trigger asthma)?',
    'Is she on a beta-blocker (can trigger asthma)?',
    'Is there an occupational trigger (baker\'s flour, latex, isocyanates in spray paint)?',
    'Is she using her inhalers correctly (poor technique = poor drug delivery)?',
    'Is there a second diagnosis (VCD, HAE, ABPA) being missed?',
]:
    story.append(bp(f'  • {pt}'))

memory_hook('ASTHMA MECHANISM: Allergen → IgE on Mast cells → Histamine + Leukotrienes + Prostaglandins → Bronchoconstriction (early) + Eosinophilic inflammation (late) + Mucus plugging. Salbutamol = bronchoconstriction. Steroids = inflammation. Both needed.', story)
divider(story)

# ── §4 CAUSES AND TRIGGERS ────────────────────────────────────────────────────
sec_header('Section 4: Causes and Triggers of Asthma — Why Did This Happen?', story)

professor_says('Asthma has a genetic component and an environmental trigger component. You need BOTH to develop asthma. Understanding triggers is clinically crucial — removing the trigger can cure the patient better than any drug.', story)

story.append(bp('<b>Genetic Basis — Atopy (AT-oh-pee):</b>'))
story.append(bp('Atopy means a tendency to develop allergic diseases. It is inherited (runs in families). Atopic people make too much IgE in response to allergens.'))
story.append(bp('The atopic triad: <b>Asthma + Allergic rhinitis (hayfever) + Atopic dermatitis (eczema)</b>. If a patient has one, ask about the others.'))
story.append(bp('Genes involved: IL-4, IL-5, IL-13 pathway genes. HLA-DQB1 gene. Filaggrin gene (also causes eczema).'))
story.append(Spacer(1, 5))

story.append(bp('<b>Common Asthma Triggers — Detailed:</b>'))
triggers_table = [
    ['Trigger Category','Specific Triggers','Why They Trigger Asthma','Clinical Importance'],
    ['ALLERGENS\n(most important)','Cat dander (most potent).\nHouse dust mite (Dermatophagoides).\nDog dander. Cockroach.\nTree pollen. Grass pollen.\nMould (Aspergillus, Alternaria).','IgE-mediated mast cell\ndegranulation → histamine\n+ leukotrienes → bronchoconstriction.','Ask about pets at home.\nBedding type (feather vs\nsynthetic). Damp walls (mould).\nSkin prick test identifies allergen.'],
    ['RESPIRATORY\nINFECTIONS','Rhinovirus (most common).\nInfluenza. RSV.\nMycoplasma. Chlamydophila.\nSinusitis (chronic).','Viruses trigger airway\ninflammation directly.\nBacterial toxins irritate.\nPost-infectious hyperresponsiveness\ncan last weeks.','Most common trigger for\nacute exacerbations.\nVaccinate: annual flu vaccine\nfor all asthma patients.\nAntibiotics only if bacterial.'],
    ['DRUGS','NSAIDs (aspirin, ibuprofen,\ndiclofenac — ANY NSAID).\nBeta-blockers (atenolol,\npropranolol — even eye drops).\nACE inhibitors (cause cough).','NSAIDs: block COX-1 → shunt\narachidonic acid to leukotriene\npathway → massive leukotriene\nrelease → severe bronchoconstriction.\nBeta-blockers: block beta-2\nreceptors → bronchoconstriction.','ASPIRIN-EXACERBATED\nRESPIRATORY DISEASE (AERD)\n= Samter\'s triad: Asthma +\nNasal polyps + NSAID sensitivity.\nNever give NSAIDs or beta-blockers\nto asthma patients without consideration.'],
    ['OCCUPATIONAL\nEXPOSURE','Flour dust (bakers).\nIsocyanates (spray painters).\nLatex (healthcare workers).\nColophony (solderers).\nAnimal proteins (vets, farmers).','Occupational sensitisation:\nboth IgE-mediated and\nnon-IgE-mediated mechanisms.\nSymptomatic only at work.\nBetter on weekends/holidays.','Occupational asthma accounts\nfor 10–15% of adult asthma.\nKey question: "Are symptoms\nbetter on holidays?"\nRemoval from exposure = cure.'],
    ['PHYSICAL FACTORS','Exercise (running, cold air\nbreathing during exercise).\nCold dry air (winter).\nFog and mist.','Rapid breathing through mouth\nin exercise bypasses nasal\nwarming/humidification.\nCold dry air causes osmotic\nchange in airway lining cells.','Exercise-induced bronchoconstriction:\nSalbutamol 15 min before exercise.\nMontelukast (leukotriene antagonist)\nvery effective prophylaxis.'],
    ['EMOTIONAL /\nPSYCHOLOGICAL','Stress. Anxiety.\nLaughter. Crying.\nHyperventilation.','Emotional states alter\nbreathing pattern.\nHyperventilation dries airways.\nPsychological factors also\nmodify symptom perception.','Anxiety can mimic asthma\nAND worsen real asthma.\nVCD (vocal cord dysfunction)\nstrongly linked to anxiety.\nImportant: exclude VCD.'],
    ['HORMONAL','Premenstrual asthma\n(perimenstrual period).\nPregnancy. Thyroid disease.','Oestrogen and progesterone\nfluctuations alter airway\nresponsiveness.\nPregnanolone (progesterone\nmetabolite) is a bronchodilator.','Some women have severe\nasthma in the days before\nperiod. Leukotriene antagonists\n(montelukast) and GnRH\nanalogue therapy can help.'],
    ['GASTRO-OESOPHAGEAL\nREFLUX (GERD)','Acid reflux from stomach\ninto oesophagus and\npossibly larynx.','Vagal reflex: acid in the\noesophagus triggers vagus\nnerve → bronchoconstriction\n(even without aspiration).\nMicro-aspiration: acid\ndamages airway lining.','Often silent (no heartburn).\nTest: 24-hour pH monitoring.\nTreatment: PPI + lifestyle.\nGERD accounts for 10%\nof difficult asthma.'],
]
story.append(plain_table(triggers_table,[CW*0.16,CW*0.22,CW*0.32,CW*0.3]))

info_box('<b>Samter\'s Triad (AERD — Aspirin-Exacerbated Respiratory Disease):</b> Three things together: (1) Asthma. (2) Nasal polyps (growths in the nose causing blockage). (3) Sensitivity to NSAIDs (aspirin, ibuprofen). Mechanism: NSAIDs block COX-1 enzyme → arachidonic acid is shunted into leukotriene pathway → huge leukotriene surge → severe bronchoconstriction. Treatment: avoid ALL NSAIDs. Use paracetamol for pain. Montelukast (leukotriene receptor blocker) is key treatment. Aspirin desensitisation possible in specialist centres.', story)

memory_hook('ASTHMA TRIGGERS: Allergens (cat most potent). Viral URTI (rhinovirus most common). NSAIDs + Beta-blockers (NEVER give to asthmatics). Occupational (better on holidays = occupational asthma). Exercise (salbutamol before). GERD (silent acid reflux). Premenstrual. Mould. Stress.', story)
divider(story)

# ── §5 CLINICAL FEATURES ──────────────────────────────────────────────────────
sec_header('Section 5: Clinical Features — What Does Asthma Look Like?', story)

professor_says('The clinical presentation of asthma is so characteristic that you can often diagnose it from the history alone. The key words are: episodic, variable, reversible, and worse at night or early morning.', story)

story.append(bp('<b>The Classic Asthma History:</b>'))
for pt in [
    '<b>Episodic:</b> Attacks come and go. Between attacks the patient may be completely normal. This is crucial — a patient who is ALWAYS breathless does not have classic asthma (may have COPD or fixed obstruction).',
    '<b>The triad of symptoms:</b> (1) Wheeze (WEE-ze — a musical whistling sound). (2) Breathlessness (difficulty breathing). (3) Cough (often dry, worse at night). All three together = classic asthma.',
    '<b>Cough variant asthma:</b> Some patients have ONLY cough — no wheeze, no breathlessness. The cough is typically dry, irritating, worse at night and early morning. This patient sometimes has cough only — this fits.',
    '<b>Nocturnal pattern:</b> Symptoms worse at night (2–4am) and early morning. This is because cortisol (natural steroid) is lowest at night. Airways are naturally narrowest at 4am (circadian rhythm).',
    '<b>Trigger identification:</b> Ask specifically about cats, dogs, dusty rooms, exercise, cold air, perfumes, smoke, certain drugs.',
    '<b>Variable symptoms:</b> Some days fine, some days bad. Varies with allergen exposure and triggers. This variability is a diagnostic hallmark.',
    '<b>Childhood history:</b> Often starts in childhood. Many children seem to "grow out of it" — but it can return in adulthood, especially in women (hormonal triggers).',
    '<b>Family history:</b> 60–70% of asthma patients have a family member with asthma, hayfever, or eczema.',
    '<b>Personal atopic history:</b> Hayfever (runny, itchy nose in pollen season). Eczema (dry itchy patches of skin in childhood). Allergic conjunctivitis (itchy red eyes).',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 5))

story.append(bp('<b>Examination — What You Find in an Asthma Attack:</b>'))
exam_table = [
    ['Sign','What You See/Hear','Meaning','Severity Indicator'],
    ['Respiratory Rate','Increased: 20–30/min.\nVery fast >30 = severe.','Body working harder\nto breathe. Airways\nnarrowed.','Rate >25 = acute severe.\nRate >30 = life-threatening.'],
    ['Use of accessory\nmuscles','Sternocleidomastoid\n(neck muscles) visible\nwhen breathing.\nIntercostal recession\n(ribs pull in).','Normal breathing uses\nonly the diaphragm.\nAccessory muscles used\nwhen very breathless.','Severe attack sign.'],
    ['Position','Sitting upright.\nLeaning forward on\nhands (tripod position).','Maximises lung volume.\nPatient instinctively\nfinds best position.','Cannot lie flat = severe.'],
    ['Speech','Short sentences only.\nOr single words only.\nOr cannot speak.','Cannot speak full\nsentences = uses all\nbreath just to breathe.','Cannot speak full\nsentence = acute severe.\nSingle words = life-threatening.'],
    ['Pulse / Heart Rate','Tachycardia >110 bpm.\n(Also: salbutamol\nitself causes tachycardia)','Body compensating.\nHypoxia drives tachycardia.','HR >110 = acute severe.\nBradycardia in VERY\nsevere = pre-arrest.'],
    ['Wheeze','Expiratory wheeze\nheard all over chest.\nBoth sides.','Air forced through\nnarrowed bronchioles\ncreates wheeze.','SILENT CHEST = NO wheeze\n= life-threatening.\n(No air moving = cannot\nmake wheeze sound.)'],
    ['Percussion','Hyper-resonant\n(more hollow than normal)\nor normal.','Hyperinflation —\nair trapped behind\nobstructed airways.','Bilateral in asthma.\n(Unilateral dullness =\npneumothorax/pneumonia).'],
    ['Peak Flow\n(PEFR)','Reduced from patient\'s\npersonal best.\nUse portable peak\nflow meter.','Best objective measure\nof airway obstruction\nin the ward setting.','See severity table above.\n<50% = severe.\n<33% = life-threatening.'],
    ['Oxygen Saturation','SpO2 may be low\n(<92%) in severe attack.','Mismatch between\nventilated and perfused\nareas of lung.','SpO2 <92% on air =\nlife-threatening or\nneeds ICU consideration.'],
    ['Pulsus Paradoxus','BP drops >10 mmHg\nduring inspiration.\n(Measure: systolic BP\nduring breathing).','Marked airway obstruction\ncauses large swings\nin intrathoracic pressure.','If present = severe attack.\nAsk for manual sphygmo\nif suspected.'],
]
story.append(plain_table(exam_table,[CW*0.16,CW*0.22,CW*0.3,CW*0.32]))
story.append(Spacer(1, 5))

story.append(img_severity)
story.append(bp('Acute asthma severity classification — BTS/SIGN guidelines', sImg))
story.append(Spacer(1, 4))

alert_box('SILENT CHEST = LIFE-THREATENING ASTHMA. No wheeze does NOT mean improving asthma. It means the airways are so tight that NO AIR IS MOVING. This is a pre-arrest state. Immediate senior help + ITU referral + IV magnesium + consider intubation.', story)

alert_box('LIFE-THREATENING FEATURES: SpO2 <92%. PEFR <33% predicted. Silent chest. Cyanosis. Bradycardia. Hypotension. Exhaustion. Confusion. These patients may need ICU. Do NOT leave them alone.', story)

memory_hook('ASTHMA EXAM: Wheeze + tachycardia + accessory muscles + cannot complete sentences = ACUTE SEVERE. Silent chest + SpO2 <92% + confusion/bradycardia = LIFE-THREATENING = call for help NOW. PEFR: 50-75% = moderate. 33-50% = severe. <33% = life-threatening.', story)
divider(story)

# ── §6 INVESTIGATIONS ─────────────────────────────────────────────────────────
sec_header('Section 6: Investigations — How Do We Confirm the Diagnosis?', story)

professor_says('Asthma is a clinical diagnosis confirmed by objective tests. But investigations also help identify the trigger, assess severity, and rule out other diagnoses. Know every test and what it means.', story)

story.append(bp('<b>Lung Function Tests — The Most Important Tests in Asthma:</b>'))
story.append(Spacer(1, 3))

lung_tests = [
    ['Test','What It Measures','Normal vs Asthma','How to Interpret'],
    ['Spirometry\n(SPY-rom-et-ree)','Patient blows hard and fast into a machine.\nMeasures:\nFEV1 = Volume blown in 1 second.\nFVC = Total volume blown out.\nFEV1/FVC ratio.','Normal FEV1/FVC > 70%.\nObstructive pattern: FEV1/FVC < 70%.\nFEV1 reduced.\nFVC normal or slightly reduced.','In asthma between attacks:\nMay be NORMAL.\nIn attack: obstruction pattern.\nKey: REVERSIBILITY TEST confirms asthma.'],
    ['Bronchodilator\nReversibility Test','Give salbutamol 400mcg inhaled.\nRepeat spirometry 15 minutes later.','POSITIVE = significant asthma:\nFEV1 improves by > 12% AND\n> 200ml from baseline.\nOR PEFR improves > 20%.','Positive reversibility = confirms\nreversible airflow obstruction = asthma.\nIrreversible obstruction despite\nbronchodilator = consider COPD or\nfixed obstruction.'],
    ['Peak Expiratory\nFlow Rate (PEFR)','Patient blows hard into a small\nhandheld meter. Measures the\nPEAK speed of exhalation.\nRecorded in litres/minute.','Compare to personal best or\npredicted (based on age/height/sex).\nNormal >80% predicted.\nIn asthma: reduced during attack.','Peak flow diary: measure morning\nand evening for 2–4 weeks.\nVariability > 20% between morning\nand evening = strong evidence\nof asthma. Key monitoring tool.'],
    ['Bronchial\nProvocation Test\n(methacholine or\nhistamine challenge)','Give increasing doses of methacholine\nor histamine (things that make\nairways tighten). Measure FEV1.','Positive = FEV1 drops >20%\nat low concentration (PC20 < 8mg/ml).\nNegative = airways do not react.','Used when spirometry and PEFR\nnormal but symptoms suggest asthma.\nHigh sensitivity — good to EXCLUDE asthma\nif negative. Performed in specialist lung lab.'],
    ['FeNO\n(Fractional exhaled\nNitric Oxide)','Patient breathes into a machine.\nMeasures nitric oxide in exhaled breath.\nNO is produced by inflamed airway cells.','Normal < 25 ppb.\nRaised (> 40 ppb) = eosinophilic\nairway inflammation = allergic asthma.','High FeNO = responds well to\ninhaled steroids.\nLow FeNO in a symptomatic patient\n= consider non-eosinophilic asthma\nor alternative diagnosis (VCD).'],
    ['Flow-Volume Loop\n(part of spirometry)','Graph showing flow rate vs volume\nduring both forced inhalation\nand exhalation.','Normal: smooth curved shape.\nAsthma (lower airway): concave\n(scooped) expiratory limb.\nUpper airway obstruction: flat\ninspiratory limb.','KEY for diagnosing VCD:\nVCD shows flat inspiratory limb\n(upper airway cuts off flow during\nbreathing in). Normal expiratory limb.'],
]
story.append(plain_table(lung_tests,[CW*0.16,CW*0.28,CW*0.28,CW*0.28]))
story.append(Spacer(1, 6))

story.append(bp('<b>Blood Tests in Asthma:</b>'))
blood_table = [
    ['Test','Result in Asthma','Significance'],
    ['Full Blood Count (FBC)','Eosinophilia: eosinophils > 0.3 x10^9/L\n(often > 1.0 in severe allergic asthma).','Eosinophils are key inflammatory cells in asthma.\nHigh eosinophils = allergic/eosinophilic asthma.\nResponds well to inhaled steroids and biologics.'],
    ['Total IgE\n(Immunoglobulin E)','Raised (> 100 IU/mL in allergic asthma,\noften > 1000 in ABPA).','Marker of atopic sensitisation. High IgE\n= candidate for omalizumab (anti-IgE biologic).\nVery high IgE (> 1000) = consider ABPA.'],
    ['Specific IgE (RAST test)\nor Skin Prick Test','Specific IgE to cat, dog, house dust mite,\npollens, moulds — identifies exact allergen.','Guides allergen avoidance advice.\nIdentifies trigger for targeted treatment\n(immunotherapy / desensitisation).'],
    ['Aspergillus IgE and\nAspergillus Precipitins','High in ABPA (Allergic Bronchopulmonary\nAspergillosis). Normal in simple asthma.','Raised Aspergillus-specific IgE +\nraised total IgE = ABPA until proven otherwise.'],
    ['C4 level and\nC1-esterase inhibitor\n(C1-INH) level + function','C4 low in HAE (Hereditary Angioedema).\nC1-INH low in HAE type 1 (80% of cases).','C4 is the BEST SCREENING TEST for HAE.\nAlways check C4 in recurrent laryngeal\nswelling/angioedema WITHOUT urticaria.'],
    ['Tryptase (serum)','Raised (> 11.4 mcg/L) in anaphylaxis.\nPeak at 30–90 minutes after reaction.','Confirms anaphylaxis. Must be taken within\n1–3 hours of attack. Normal tryptase does\nnot exclude anaphylaxis.'],
    ['Blood Glucose','May be raised after steroid treatment.','Monitor. Prednisolone raises blood sugar.\nImportant in diabetic patients.'],
    ['Arterial Blood Gas\n(ABG) in severe attack','Early: LOW PaCO2 (hyperventilating).\nLate: NORMAL or HIGH PaCO2 = DANGER.\nLow PaO2 in severe attack.','NORMAL or HIGH PaCO2 in a\nbreathing-hard asthma patient =\nTIRING = impending respiratory failure.\nThis is a sign for ICU.'],
]
story.append(plain_table(blood_table,[CW*0.24,CW*0.38,CW*0.38]))
story.append(Spacer(1, 6))

story.append(bp('<b>Imaging in Asthma:</b>'))
imaging_table = [
    ['Test','When to Do It','What It Shows in Asthma'],
    ['Chest X-ray (CXR)','Acute attack (to exclude complications).\nFirst attack at any age.','Usually NORMAL between attacks.\nIn attack: hyperinflation (flat diaphragms,\nhorizontal ribs, increased AP diameter).\nMay show: pneumothorax (complication),\npneumonia (trigger), mucus plugging.'],
    ['CT Thorax\n(High resolution — HRCT)','Not routine for simple asthma.\nDone if: suspected ABPA, bronchiectasis,\nor diagnosis uncertain.','In ABPA: central bronchiectasis\n(bronchiectasis in the inner parts\nof the lung — characteristic pattern).\nMucus plugs. Tree-in-bud pattern.'],
    ['CT/MRI Sinuses','Persistent symptoms. Suspected\nnasal polyps or sinusitis.','Nasal polyps (in Samter\'s triad).\nChronic sinusitis. Pan-sinusitis in ABPA.'],
    ['Direct Laryngoscopy\nor Nasendoscopy','Suspected VCD (vocal cord dysfunction).\nSuspected upper airway abnormality.','In VCD: vocal cords PARADOXICALLY ADDUCT\n(close) during inspiration, when they should\nbe open. Diagnostic if done during an attack.\nBetween attacks: usually normal.'],
]
story.append(plain_table(imaging_table,[CW*0.2,CW*0.35,CW*0.45]))

info_box('<b>MRCP Key — PaCO2 in Asthma:</b> In the early stages of an asthma attack, the patient breathes fast and hard. This causes them to blow off CO2. So PaCO2 is LOW (hypocapnia). As the patient tires, breathing becomes less effective. PaCO2 RISES towards normal. A NORMAL PaCO2 in a patient working hard to breathe with asthma = WARNING SIGN. A HIGH PaCO2 = the patient is exhausted and about to stop breathing = ICU emergency.', story)

memory_hook('INVESTIGATIONS IN ASTHMA: Spirometry (FEV1/FVC <70%) + Reversibility (>12% + 200ml after salbutamol) = confirms asthma. FeNO >40 = eosinophilic inflammation. Peak flow diary variability >20% = asthma. C4 low = HAE. High total IgE + Aspergillus IgE = ABPA. ABG: normal/high PaCO2 in attack = ICU.', story)
divider(story)

# ── §7 MANAGEMENT — ACUTE AND CHRONIC ────────────────────────────────────────
sec_header('Section 7: Management — Treating the Acute Attack and Long-Term Control', story)

professor_says('Treatment of asthma has two parts: (1) Stopping the acute attack NOW. (2) Preventing the next attack from happening. Many patients only focus on the rescue inhaler and forget the preventer. This is why their asthma keeps coming back.', story)

story.append(bp('<b>PART A: Treating the Acute Attack — Step by Step:</b>'))
story.append(Spacer(1, 3))

acute_table = [
    ['Severity','First Steps','Additional Treatment','When to Consider ICU'],
    ['MODERATE\n(PEFR 50-75%)\nCan speak sentences','Salbutamol 2.5–5mg\nnebulised. Repeat every\n20–30 min if needed.\nOxygen to maintain\nSpO2 94–98%.\nPrednisolone 40mg oral.','If not improving after\n3 nebulisers:\nAdd ipratropium 500mcg\nnebulised.\nAdmit to hospital.','Usually managed on\nmedical ward.\nICU only if deteriorates.'],
    ['ACUTE SEVERE\n(PEFR 33-50%)\nCannot complete\nsentences','Immediate high-flow O2\n(15L non-rebreathe).\nSalbutamol 5mg\nnebulised CONTINUOUSLY\n(back-to-back).\nIpratropium 500mcg\nneb every 4-6 hours.\nHydrocortisone 100mg IV\nor Prednisolone 40mg oral.','Magnesium sulphate:\n1.2–2g IV over 20 min\n(first-line add-on for\nacute severe asthma).\nCXR to exclude\npneumothorax.','If PEFR not improving\nafter 1 hour.\nPaCO2 rising.\nExhausted patient.'],
    ['LIFE-THREATENING\n(PEFR <33%)\nSilent chest\nCyanosis/Confusion','CALL SENIOR HELP + ICU.\nHigh flow O2.\nContiguous salbutamol\nnebulisers.\nIpratropium nebulisers.\nIV hydrocortisone 100mg.','Magnesium sulphate\n1.2–2g IV over 20 min.\nIV salbutamol infusion\n(5–10 mcg/min) if\nnot responding.\nIV aminophylline\n(rarely — specialist\nconsult needed).\nHeliox (70:30\nHelium:Oxygen mix).','IMMEDIATE ICU involvement.\nPrepare for intubation\nif deteriorating.\nNon-invasive ventilation\nmay help bridge.'],
]
story.append(plain_table(acute_table,[CW*0.18,CW*0.28,CW*0.3,CW*0.24]))
story.append(Spacer(1, 5))

story.append(bp('<b>Why Magnesium Sulphate Works in Asthma:</b>'))
story.append(bp('Magnesium (mag-NEE-zee-um) is a natural calcium channel blocker. In smooth muscle, contraction depends on calcium entering the muscle cell. Magnesium blocks calcium entry. Result: smooth muscle in the bronchiole wall RELAXES. Airways open.'))
story.append(bp('<b>Dose:</b> 1.2–2g IV over 20 minutes. Given ONCE. Evidence from BTS guidelines and MAGICS trial.'))
story.append(bp('<b>Important:</b> Also available as NEBULISED magnesium sulphate (isotonic solution, 2.5ml) combined with salbutamol. Can be given even in primary care.'))
story.append(Spacer(1, 5))

story.append(bp('<b>PART B: Long-Term Management — BTS/SIGN Step-Up Therapy:</b>'))
story.append(bp('The British Thoracic Society (BTS) and Scottish Intercollegiate Guidelines Network (SIGN) publish a step-up system. You start at the lowest step and move up if symptoms are not controlled.'))
story.append(Spacer(1, 3))

steps_table = [
    ['Step','Treatment','What It Does','When to Use This Step'],
    ['Step 1\n(Mild intermittent)','SABA (Short-Acting Beta-2 Agonist)\nInhaled salbutamol PRN only.\nNo daily preventer needed.','Salbutamol opens airways\nwithin minutes. Lasts 4 hours.','Symptoms < twice per week.\nNocturnal symptoms < once/month.\nNo limitation of activity.'],
    ['Step 2\n(Regular preventer)','Add ICS\n(Inhaled Corticosteroid):\nBeclometasone 200–400 mcg/day\nor Budesonide or Fluticasone.\nSABA PRN as well.','ICS reduces airway\ninflammation daily.\nReduces exacerbations\nand long-term remodelling.','Using SABA more than twice\nper week. Any nocturnal\nsymptoms. Start here for most\nnewly diagnosed asthma.'],
    ['Step 3\n(Add-on therapy)','Add LABA (Long-Acting Beta-2\nAntagonist): Salmeterol or\nFormoterol PLUS ICS.\nCombination inhalers available:\nSeretide (salmeterol+fluticasone),\nSymbicort (formoterol+budesonide).','LABA opens airways for\n12 hours. Added to ICS,\nnot used alone\n(LABA alone = risk of\nasthma death if no ICS).','Not controlled on\nStep 2. LABA added only\nIF already on ICS.'],
    ['Step 4\n(Increase ICS or\nadd further agents)','High-dose ICS (up to 2000mcg\nbeclometasone/day).\nAdd LTRA (Montelukast)\nor Theophylline or LAMA\n(Tiotropium).','Montelukast blocks\nleukotriene receptors.\nTheoyphylline: bronchodilator\n+ anti-inflammatory.\nTimotropium: anticholinergic.','Still not controlled\non Step 3. Review\ninhaler technique first.\nRefer to specialist.'],
    ['Step 5\n(Specialist care)','BIOLOGICS:\nOmalizumab (anti-IgE).\nMepolizumab (anti-IL-5).\nBenralizumab (anti-IL-5Ra).\nDupilumab (anti-IL-4/13).\n+/- Oral steroids\n(lowest dose possible).','Biologics target\nspecific parts of the\ninflammatory pathway.\nDramatic effect in\nselected patients.','Severe refractory asthma\nnot controlled on maximum\ninhaled therapy. Requires\nspecialist centre.\nPatients selected by\nbiomarker profile.'],
]
story.append(plain_table(steps_table,[CW*0.12,CW*0.3,CW*0.25,CW*0.33]))
story.append(Spacer(1, 5))

story.append(bp('<b>Biologics — The Modern Revolution in Severe Asthma:</b>'))
bio_table = [
    ['Biologic','Target','Mechanism','Who Gets It','Key Points'],
    ['Omalizumab\n(Xolair)','IgE antibody\n(binds to free IgE)','Neutralises IgE before\nit can attach to mast\ncells. Mast cells\ncannot degranulate.','Total IgE 30–1500 IU/mL.\nSensitised to a perennial\nallergen (dust mite, cat).\nStep 4/5 uncontrolled.','Injected every 2–4 weeks.\nDose based on IgE level\nand body weight.\n16-week trial then assess.'],
    ['Mepolizumab\n(Nucala)','IL-5 cytokine','Blocks IL-5 which\nstimulates eosinophil\nproduction. Reduces\nblood eosinophil count.','Blood eosinophils\n>= 300 cells/uL.\nFrequent exacerbations\ndespite Step 4.','Monthly SC injection.\nReduces exacerbation\nrate by ~50%. Can\nreduce/stop oral steroids.'],
    ['Benralizumab\n(Fasenra)','IL-5 receptor\n(IL-5Ra)','Blocks IL-5 receptor\non eosinophils.\nAlso directly depletes\neosinophils via ADCC.','Blood eosinophils\n>= 300 cells/uL.\nStep 4 uncontrolled.','First 3 doses monthly,\nthen every 8 weeks.\nVery rapid eosinophil\ndepletion.'],
    ['Dupilumab\n(Dupixent)','IL-4 receptor alpha\n(IL-4Ra)','Blocks both IL-4\nand IL-13 signalling.\nReduces multiple\nallergic pathways.','FeNO >= 25 ppb or\neosinophils >= 150.\nAlso approved for\natopic dermatitis.','Every 2 weeks SC.\nWorks across multiple\natopic conditions.'],
    ['Tezepelumab\n(Tezspire)','TSLP\n(Thymic Stromal\nLymphopoietin)','Blocks TSLP — the\nupstream cytokine\nthat triggers the\nentire allergic cascade.\nBroadest target.','Severe uncontrolled\nasthma regardless\nof eosinophil level\n(also non-eosinophilic).','Monthly SC. Newest\nbiologic. Works in\nboth eosinophilic\nAND non-eosinophilic\nasthma.'],
]
story.append(plain_table(bio_table,[CW*0.14,CW*0.1,CW*0.22,CW*0.22,CW*0.32]))

info_box('<b>Why This Patient Keeps Relapsing — The Answer:</b> This patient is on the right treatment (steroids work). But she keeps relapsing. The most likely reasons: (1) Trigger still present — allergen at home or workplace. (2) Undertreatment — needs step-up. (3) Poor inhaler technique — most patients use inhalers incorrectly. (4) Poor adherence (forgetting preventer inhaler daily). (5) Second diagnosis — consider VCD, ABPA, or HAE contributing. (6) Premenstrual asthma — if attacks match menstrual cycle. Action: check technique, check trigger, step up, and refer to specialist.', story)

memory_hook('BTS STEPS: 1=SABA PRN. 2=Add ICS. 3=Add LABA (NEVER LABA without ICS). 4=High ICS + Montelukast/Theophylline/Tiotropium. 5=Biologics (Omalizumab=high IgE; Mepolizumab/Benralizumab=high eosinophils; Tezepelumab=any type). Magnesium sulphate 1.2-2g IV = standard in acute severe asthma.', story)
divider(story)

# ── §8 DIFFERENTIAL DIAGNOSES IN DETAIL ──────────────────────────────────────
sec_header('Section 8: Differential Diagnoses — All the Conditions That Look Like Asthma', story)

professor_says('This is the most important section for MRCP. Many conditions mimic asthma. If you treat them all as asthma, you will harm some patients. Know each condition deeply — the key difference, the key test, and the key treatment.', story)

# ── VCD ──
story.append(bp('<b>8a. Vocal Cord Dysfunction (VCD) / Inducible Laryngeal Obstruction (ILO)</b>'))
professor_says('VCD is the great mimic. It looks like asthma, sounds like asthma — but is NOT asthma. Patients with VCD are often wrongly labelled as "brittle asthma" and given unnecessary steroids for years. Knowing VCD changes their lives.', story)

story.append(bp('<b>What is VCD?</b>'))
story.append(bp('VCD = Vocal Cord Dysfunction. The vocal cords (two muscular folds in the larynx) abnormally close DURING BREATHING — especially during inspiration (breathing in). This blocks air entry. The patient cannot breathe in properly.'))
story.append(bp('In normal breathing: vocal cords OPEN WIDE when you breathe in. In VCD: the cords close (adduct) paradoxically — backwards from what they should do. This is why it is also called <b>Paradoxical Vocal Cord Movement (PVCM)</b>.'))
story.append(bp('<b>The newer term:</b> ILO = Inducible Laryngeal Obstruction. More accurate because the larynx (not just the cords) is involved.'))
story.append(Spacer(1, 4))

vcd_table = [
    ['Feature','VCD / ILO','Asthma'],
    ['Age and sex','Young women most common.\nAthletes.\nHealthcare workers.','Any age. Childhood onset common.'],
    ['Sound','STRIDOR — heard on\nBREATHING IN (inspiratory).\nHarsh, croaking sound.','WHEEZE — heard on\nBREATHING OUT (expiratory).\nMusical, whistling.'],
    ['Triggers','Irritants (chlorine, perfume,\nfumes). Exercise.\nAnxiety/stress.\nPost-nasal drip. Emotion.','Allergens. Cold air. Exercise.\nNSAIDs. Viral URTI. Smoke.'],
    ['Response to\nSalbutamol','Does NOT respond.\nSalbutamol does not help\nthe larynx.','Significant improvement.\nFEV1 improves > 12%.'],
    ['Response to\nSteroids','Does NOT respond.\nSteroids do nothing\nfor muscle spasm.','YES — ICS and oral steroids\nclear the inflammation.'],
    ['Between attacks','Normal spirometry.\nNormal FeNO.\nNormal peak flow.\nNo wheeze on auscultation.','May have abnormal spirometry.\nRaised FeNO.\nVariable PEFR.'],
    ['Diagnosis','Laryngoscopy or\nnasendoscopy DURING\nan attack. See cords\nclosing on inspiration.','Spirometry + reversibility\ntest. FeNO. Peak flow diary.'],
    ['Flow-volume loop','FLAT INSPIRATORY LIMB\n(cut off at top of loop).\nExpiratory limb normal.','Concave (scooped)\nexpiratory limb.\nInspiratory limb normal.'],
    ['Treatment','Speech therapy\n(breathing retraining,\nnasendoscopy biofeedback).\nTreat GERD if present.\nPsychological support.\nAvoid triggers.','Inhaled steroids.\nSalbutamol.\nStep-up therapy.'],
]
story.append(plain_table(vcd_table,[CW*0.22,CW*0.39,CW*0.39]))
story.append(Spacer(1, 4))

info_box('<b>VCD KEY FACTS for MRCP:</b> (1) VCD is VERY COMMON and COMMONLY MISDIAGNOSED as asthma. (2) Stridor = upper airway = VCD. Wheeze = lower airway = asthma. (3) VCD does NOT respond to salbutamol or steroids. (4) Diagnosed by nasendoscopy/laryngoscopy DURING an episode. (5) Treated by speech and language therapist (SLT) with breathing exercises. (6) FeNO is NORMAL in VCD (no eosinophilic inflammation). (7) Many patients have BOTH VCD and asthma simultaneously.', story)
divider(story)

# ── Laryngospasm ──
story.append(bp('<b>8b. Laryngospasm (LAR-in-go-spazm) — Sudden Airway Closure</b>'))
story.append(bp('<b>What is it?</b> A sudden, brief, involuntary spasm (tightening) of the laryngeal muscles. The vocal cords snap shut completely. The patient cannot breathe at all for a few seconds to minutes. It is terrifying. Then it resolves spontaneously.'))
story.append(Spacer(1, 3))
for pt in [
    '<b>Presentation:</b> Sudden onset breathlessness or inability to breathe. High-pitched inspiratory stridor or silence (complete closure). Usually lasts seconds to 1–2 minutes. Resolves on its own. Patient very frightened.',
    '<b>Common triggers:</b> GERD (acid reflux irritating the larynx — most common cause). Chlorine gas. Anaesthetic gas (during induction — common surgical emergency). Post-extubation. Emotional stress. Spicy food. Cold liquids.',
    '<b>GERD-induced laryngospasm:</b> Acid from the stomach refluxes up to the larynx. Even tiny amounts of acid on the larynx trigger a violent protective spasm. Often happens at night (lying flat). Patient wakes up unable to breathe for a minute. Terrifying.',
    '<b>Diagnosis:</b> Clinical history. Laryngoscopy between attacks usually normal. 24-hour pH monitoring confirms GERD.',
    '<b>Treatment:</b> Treat underlying GERD with PPI (proton pump inhibitor — omeprazole 20–40mg daily). Lifestyle: elevate head of bed, avoid food 3 hours before sleep, avoid alcohol/caffeine. Breathing exercises. In acute attack: remain calm. Breathe through nose slowly. Sipping cold water may help. Valsalva manoeuvre (bear down). IV calcium gluconate if hypocalcaemia is the cause.',
    '<b>Hypocalcaemia-induced laryngospasm:</b> Low calcium (from hypoparathyroidism, after thyroid surgery damaging parathyroids) causes muscle over-excitability. Laryngospasm is a symptom. Chvostek\'s sign (tapping facial nerve causes facial twitch) and Trousseau\'s sign (BP cuff inflation causes carpal spasm). Treat with IV calcium gluconate.',
]:
    story.append(bp(f'• {pt}'))
divider(story)

# ── Laryngeal Oedema / Anaphylaxis ──
story.append(bp('<b>8c. Laryngeal Oedema — Allergic Swelling of the Airway</b>'))
story.append(bp('<b>What is it?</b> Laryngeal oedema (ee-DEE-mah) = swelling of the laryngeal tissues. This narrows the airway rapidly. Can completely block air entry. A medical emergency.'))
story.append(Spacer(1, 3))
for pt in [
    '<b>Most common cause: Anaphylaxis</b> (ana-fill-AX-iss) = a severe, life-threatening allergic reaction. IgE-mediated mast cell degranulation causes massive histamine release → laryngeal oedema + bronchospasm + vasodilation + urticaria (hives).',
    '<b>Common triggers of anaphylaxis:</b> Nuts (peanuts, tree nuts). Shellfish. Bee/wasp sting (venom). Penicillin and other drugs. Latex. Contrast dye. Exercise (exercise-induced anaphylaxis). Idiopathic (no cause found).',
    '<b>Features of anaphylaxis:</b> Urticaria (URTIH-kair-ee-ah) = hives = raised itchy red wheals on skin. Angioedema (swelling of lips, tongue, face). Laryngeal oedema (stridor, hoarse voice, unable to swallow). Bronchospasm (wheeze). Hypotension (low blood pressure). Tachycardia.',
    '<b>Treatment of anaphylaxis:</b> ADRENALINE (epinephrine) IM 0.5mg (0.5ml of 1:1000) into the OUTER THIGH. This is the ONLY proven life-saving treatment. Give IMMEDIATELY. IM, not IV (unless cardiac arrest). Repeat after 5 minutes if no improvement. Then: IV fluids, chlorphenamine (antihistamine) IV 10mg, hydrocortisone 200mg IV. Lie patient flat (unless vomiting/dyspnoeic — then sit up). Airway support.',
    '<b>ACE Inhibitor-induced angioedema:</b> ACE inhibitors (ramipril, lisinopril, enalapril) block the breakdown of bradykinin. Bradykinin accumulates and causes angioedema of the face, lips, and larynx — WITHOUT urticaria. Can occur at ANY TIME after starting the drug — even years later. Does NOT respond to adrenaline or antihistamines. Treatment: stop the ACE inhibitor. IV icatibant (bradykinin B2 receptor antagonist) for severe episodes. Switch to ARB (but 10% cross-reactivity) or avoid both.',
]:
    story.append(bp(f'• {pt}'))

alert_box('ADRENALINE IN ANAPHYLAXIS: 0.5mg IM (outer thigh). Use EpiPen if available. This is the ONLY proven life-saving treatment. Antihistamines and steroids are SECONDARY — they are NOT life-saving in acute anaphylaxis. Never delay adrenaline to give antihistamine first.', story)
divider(story)

# ── HAE ──
story.append(bp('<b>8d. Hereditary Angioedema (HAE) — The Great Impostor</b>'))
professor_says('HAE is rare but dangerous. It causes laryngeal swelling that kills. Unlike anaphylaxis, it does NOT have urticaria. Adrenaline does NOT help. If you miss this diagnosis, your patient could die from the next episode.', story)

story.append(bp('<b>What is HAE?</b>'))
story.append(bp('HAE = a genetic (inherited) condition. The body is missing or has low levels of <b>C1-esterase inhibitor (C1-INH)</b>. This protein normally controls the complement system and the contact activation pathway (kinin system).'))
story.append(bp('Without C1-INH: bradykinin (BRAD-ee-KY-nin) — a peptide that makes blood vessels leaky — accumulates in huge amounts. Result: swelling (angioedema) in deep tissues.'))
story.append(Spacer(1, 3))

hae_table = [
    ['Feature','HAE','Allergic Angioedema (Anaphylaxis)'],
    ['Mechanism','Bradykinin-mediated.\nC1-INH deficiency or dysfunction.\nGenetic.','Histamine-mediated.\nIgE mast cell degranulation.\nAcquired (after allergen exposure).'],
    ['Urticaria (hives)','ABSENT — there are NO HIVES.\nThis is the KEY differentiator.','PRESENT — itchy wheals\non skin are hallmark.'],
    ['Onset','Slow — over hours.\nBuilds gradually over 24–72 hours.','Fast — minutes to hours.\nPeak within 30 minutes of trigger.'],
    ['Triggers','Trauma (even minor — dental work).\nStress. Oestrogen (OCP trigger!).\nACE inhibitors (worsen HAE).\nInfection. Menstruation.','Allergen exposure:\nnuts, bees, drugs, latex.'],
    ['Sites of swelling','Face, lips, tongue, larynx.\nAbdomen (causes severe\ncolic — can mimic\nacute abdomen).\nGenitalia. Extremities.','Face, lips, tongue, throat.\nGeneralised skin hives.\nBronchospasm. Anaphylaxis.'],
    ['Family history','Usually YES — autosomal dominant\n(parent also had episodes).\nBut new mutations occur.','No family pattern.'],
    ['Blood tests','C4 LOW (best screening test).\nC1-INH level LOW (Type 1, 80%).\nC1-INH function LOW\n(Type 2, 20%).','C4 normal.\nC1-INH normal.\nIgE raised. Tryptase raised.'],
    ['Response to\nadrenaline','NO — does NOT respond.\nBradykinin pathway\nnot affected by adrenaline.','YES — adrenaline is\nlife-saving in anaphylaxis.'],
    ['Response to\nantihistamines','NO — histamine is NOT\nthe mechanism.','YES — helps urticaria\nand mild symptoms.'],
    ['Treatment\n(acute attack)','C1-INH concentrate (Berinert).\nIcatibant (bradykinin B2\nreceptor antagonist).\nFresh Frozen Plasma (FFP)\nif above not available.','Adrenaline IM 0.5mg.\nChlorphenamine IV.\nHydrocortisone IV.\nIV fluids.'],
    ['Prophylaxis\n(prevention)','Tranexamic acid (anti-fibrinolytic).\nDanazol (androgen — increases\nC1-INH synthesis). Lanadelumab\n(monoclonal antibody — kallikrein\ninhibitor). C1-INH infusion\nbefore planned procedures.','Allergen avoidance.\nEpiPen prescription.\nImmunotherapy in some cases.'],
]
story.append(plain_table(hae_table,[CW*0.2,CW*0.4,CW*0.4]))
story.append(Spacer(1, 4))

info_box('<b>HAE Types:</b> Type 1 (80%): C1-INH level LOW, C1-INH function LOW, C4 LOW. Type 2 (20%): C1-INH level NORMAL or HIGH, but C1-INH function LOW, C4 LOW. Type 3 (rare): C1-INH normal, caused by FXII gene mutation, usually in women on oestrogen-containing OCP. C4 is LOW in ALL types during attacks and often LOW between attacks — making it the BEST SCREENING TEST.', story)

memory_hook('HAE KEY POINTS: No urticaria (hives) + slow swelling + family history + abdominal colic = THINK HAE. C4 LOW = best screening test. C1-INH low = confirms it. Adrenaline and antihistamines DO NOT WORK. Treatment: C1-INH concentrate or Icatibant. OCP worsens HAE (oestrogen trigger). ACE inhibitors CONTRAINDICATED in HAE.', story)
divider(story)

# ── ABPA ──
story.append(bp('<b>8e. Allergic Bronchopulmonary Aspergillosis (ABPA)</b>'))
story.append(bp('<b>What is it?</b> ABPA = an allergic reaction to the fungus <b>Aspergillus fumigatus</b> (as-PER-jih-lus fyoo-MIH-gay-tus). The fungus colonises (lives in) the airways but does not invade. The immune system overreacts to it.'))
story.append(bp('Think of it like having a wild animal living in your house that you are severely allergic to. The animal is not attacking you, but your immune system is causing massive damage trying to fight it.'))
story.append(Spacer(1, 3))
for pt in [
    '<b>Who gets it:</b> Almost always in patients with pre-existing asthma OR cystic fibrosis. Aspergillus lives in soil, compost, rotting vegetation, old buildings.',
    '<b>Symptoms:</b> Wheeze (worse than usual asthma). Cough with brownish or black mucus plugs (the fungus is in the mucus). Recurrent lung collapse (mucus plug blocks a bronchus). Fever. Night sweats. Weight loss.',
    '<b>Diagnostic criteria (modified Rosenberg-Patterson):</b> (1) Asthma. (2) Total IgE >1000 IU/mL (very high). (3) Aspergillus-specific IgE raised. (4) Aspergillus precipitins (IgG antibodies) positive. (5) Blood eosinophilia. (6) Central bronchiectasis on CT (bronchiectasis in the inner, central parts of the lung — opposite to the peripheral pattern of other bronchiectasis). (7) Fleeting pulmonary infiltrates on CXR (shadows that come and go).',
    '<b>CT findings:</b> Central bronchiectasis. Mucoid impaction (mucus plugs showing as "finger-in-glove" or "toothpaste" shadows on CXR). High-attenuation mucus (calcium in mucus plugs).',
    '<b>Treatment:</b> Oral prednisolone (0.5mg/kg/day for 2 weeks, then taper over 3–6 months) to suppress the immune reaction. <b>Plus</b> antifungal: itraconazole 200mg twice daily (or voriconazole) for 4–6 months to reduce fungal burden. Monitor: total IgE (should fall with treatment — a rising IgE means relapse).',
    '<b>Long-term complications:</b> Proximal bronchiectasis. Lung fibrosis. Aspergilloma (fungal ball forming in a cavity).',
]:
    story.append(bp(f'• {pt}'))

memory_hook('ABPA: Asthma + very HIGH total IgE (>1000) + brownish mucus plugs + central bronchiectasis on CT + Aspergillus IgE raised. Treatment: Prednisolone + Itraconazole. Monitor: total IgE falls with treatment. Rising IgE = relapse.', story)
divider(story)

# ── Eosinophilic bronchitis ──
story.append(bp('<b>8f. Eosinophilic Bronchitis (EB)</b>'))
story.append(bp('<b>What is it?</b> Eosinophilic bronchitis = inflammation of the airways with lots of eosinophil cells — exactly like asthma. BUT there is NO bronchoconstriction and NO airflow obstruction. The patient has <b>COUGH ONLY</b>.'))
story.append(Spacer(1, 3))
for pt in [
    '<b>Symptoms:</b> Chronic dry cough. No wheeze. No breathlessness. Cough is often the only symptom — worse in the morning or with exposure to irritants.',
    '<b>Spirometry:</b> NORMAL — this is the key difference from asthma. FEV1/FVC normal. No reversibility.',
    '<b>FeNO:</b> RAISED (>25 ppb) — shows eosinophilic inflammation present.',
    '<b>Sputum:</b> Induced sputum shows > 3% eosinophils — confirms the diagnosis.',
    '<b>Why no bronchoconstriction?</b> In asthma, mast cells are located INSIDE the smooth muscle layer of bronchioles. In EB, mast cells are in the epithelium (surface lining) only — not in the muscle. So they cannot trigger muscle spasm.',
    '<b>Treatment:</b> Inhaled corticosteroids (ICS) — very effective. Symptoms resolve completely. This is why it is important to diagnose: responds well to simple inhaler therapy.',
    '<b>Common causes:</b> Occupational exposure (flour, latex). Isocyanates. Post-nasal drip.',
]:
    story.append(bp(f'• {pt}'))
divider(story)

# ── GERD ──
story.append(bp('<b>8g. GERD-Induced Cough and Airway Disease</b>'))
story.append(bp('<b>What is it?</b> GERD (Gastro-Oesophageal Reflux Disease) = acid from the stomach flows backwards up the oesophagus (food pipe). This can trigger airway symptoms through two mechanisms:'))
story.append(Spacer(1, 3))
for pt in [
    '<b>Vagal reflex mechanism:</b> Acid touches the lower oesophagus. This triggers the vagus nerve (which also supplies the airways). The vagus nerve reflex causes cough and mild bronchoconstriction — even without acid reaching the lungs.',
    '<b>Micro-aspiration mechanism:</b> Tiny amounts of acid or stomach contents are aspirated (breathed in) into the airways. This directly damages and irritates the bronchial mucosa, causing inflammation and airway hyperresponsiveness.',
    '<b>Laryngopharyngeal reflux (LPR):</b> Acid reaches the larynx. Causes hoarseness (husky voice). Chronic throat-clearing. Globus sensation (feeling of something stuck in the throat). Laryngospasm at night.',
    '<b>Presentation:</b> Chronic cough (often the only symptom — no heartburn in 40%). Worse lying flat. Worse after meals. Worse at night. Hoarse voice. Clears throat frequently.',
    '<b>Asthma-GERD link:</b> GERD is found in up to 70% of asthma patients. GERD can worsen asthma control. Treating GERD can improve asthma in some patients.',
    '<b>Diagnosis:</b> 24-hour ambulatory pH monitoring (gold standard). High-resolution oesophageal manometry. Upper GI endoscopy (to assess oesophagitis). Empirical PPI trial: if symptoms improve on 4-week PPI trial = GERD confirmed.',
    '<b>Treatment:</b> PPI (omeprazole 20–40mg daily). Lifestyle: head of bed elevated, avoid food 3 hours before sleep, avoid coffee/alcohol/fatty foods/chocolate/mint. Weight loss if obese. H2-antagonist (ranitidine) or alginate (Gaviscon) add-ons.',
]:
    story.append(bp(f'• {pt}'))

memory_hook('GERD CAUSES: Cough (without heartburn in 40%). Laryngospasm at night (wakes from sleep gasping). Hoarse voice. Asthma triggers. KEY TEST: 24-hour pH monitoring. TREATMENT: PPI + head of bed elevated + avoid food 3h before sleep.', story)
divider(story)

# ── §9 COMPLICATIONS ──────────────────────────────────────────────────────────
sec_header('Section 9: Complications of Acute Severe Asthma', story)

professor_says('Most patients with asthma do well with treatment. But in severe attacks, life-threatening complications can occur — and you need to recognise them quickly.', story)

comp_table = [
    ['Complication','What Happens','Signs','Treatment'],
    ['Pneumothorax\n(noo-mo-THOR-ax)\n(air in chest space)','Overinflated lung bursts.\nAir leaks into the space\nbetween lung and chest wall.\nLung collapses.','Sudden WORSENING of\nbreathing in a known asthma\npatient. Unilateral reduced\nbreath sounds. Hyper-resonance\non one side. Tracheal deviation\n(tension pneumothorax).','Small: observation.\nLarge/tension: needle\ndecompression (2nd intercostal\nspace, mid-clavicular line) THEN\nchest drain. Never delay\nin tension pneumothorax.'],
    ['Respiratory Failure','Airways so blocked that\ngas exchange fails completely.\nPaCO2 rises.\nPaO2 falls.','Cyanosis. Confusion.\nRising PaCO2 on ABG.\nBradycardia (late sign).','ICU. Non-invasive ventilation\n(NIV) may help.\nIntubation and\nmechanical ventilation\nif deteriorating.'],
    ['Mucus Plugging and\nLobe Collapse\n(atelectasis)','Thick mucus plugs block\na main bronchus or lobar\nbronchus. Air cannot\nget past. Lobe collapses.','Sudden worsening.\nCXR: loss of volume\nin one lobe. Opacification.','Physiotherapy.\nNebulised DNase if repeated.\nBronchoscopy to remove\nplug in severe cases.'],
    ['Hypokalaemia\n(low potassium\nfrom salbutamol)','Salbutamol stimulates beta-2\nreceptors which drive K+ into\ncells. Serum K+ falls.','Muscle weakness. Cramps.\nECG changes (U waves,\nflattened T waves).\nArrhythmia risk.','Monitor K+ in all\nacute severe asthma.\nPotassium replacement\nIV if <3.0 mmol/L.'],
    ['Lactic Acidosis\n(from salbutamol)','High-dose nebulised/IV\nsalbutamol can cause\nlactic acidosis.\nMetabolic side effect.','Raised lactate on ABG.\nTachycardia. Agitation.\nLow bicarbonate.','Reduce salbutamol dose.\nMay mimic deteriorating\nasthma — check lactate\nin all severe attacks\non high-dose salbutamol.'],
    ['Steroid Adverse\nEffects (long-term)','Long courses of oral\nprednisolone cause:\noseoporosis, diabetes,\ncataracts, skin thinning,\nadrenal suppression.','Signs develop over months.\nWeight gain. Bruising easily.\nHyperglycaemia. Bone pain.','Use minimum effective\nsteroid dose. Calcium\n+ vitamin D supplements.\nBone protection (bisphosphonate)\nif prolonged oral steroids.'],
]
story.append(plain_table(comp_table,[CW*0.16,CW*0.26,CW*0.28,CW*0.3]))

alert_box('TENSION PNEUMOTHORAX in asthma: Sudden severe unilateral breathlessness + absent breath sounds + tracheal deviation AWAY from the affected side. Do NOT wait for CXR. Immediate needle decompression: 2nd intercostal space, mid-clavicular line, above the rib (to avoid neurovascular bundle below the rib). This is immediately life-threatening.', story)

memory_hook('ASTHMA COMPLICATIONS: Pneumothorax (sudden unilateral worsening). Respiratory failure (rising PaCO2). Mucus plug collapse. Hypokalaemia (salbutamol drives K+ into cells — check K+ in severe attacks). Lactic acidosis (paradoxically from high-dose salbutamol). Long-term steroids: osteoporosis + diabetes + adrenal suppression.', story)
divider(story)

# ── §10 SPECIAL SITUATIONS ───────────────────────────────────────────────────
sec_header('Section 10: Special Situations in Asthma', story)

story.append(bp('<b>Asthma in Pregnancy:</b>'))
for pt in [
    'Asthma follows the "rule of thirds" in pregnancy: 1/3 improve, 1/3 stay same, 1/3 worsen.',
    'Uncontrolled asthma in pregnancy is more dangerous than the medications. Poorly controlled asthma risks: preterm birth, low birth weight, pre-eclampsia.',
    'ALL current asthma medications (salbutamol, ICS, prednisolone) are safe in pregnancy. Do NOT stop inhalers during pregnancy.',
    'Monitor more frequently. Avoid NSAID-containing analgesics. Influenza vaccination is especially important in pregnancy.',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 4))

story.append(bp('<b>Aspirin/NSAID-Exacerbated Asthma (Samter\'s Triad):</b>'))
for pt in [
    'Classical triad: Asthma + Nasal polyps + NSAID sensitivity.',
    'Affects ~10% of asthmatics. Mechanism: COX-1 blockade shunts arachidonic acid into 5-lipoxygenase pathway → massive leukotrienes (LTC4, LTD4, LTE4) → severe bronchoconstriction + nasal symptoms.',
    'Reaction within 30–120 minutes of ingesting ANY NSAID. Can be life-threatening.',
    'Management: Avoid ALL NSAIDs. Paracetamol safe (weak COX-1, safe up to 1g). Montelukast (leukotriene antagonist) excellent preventive therapy. Aspirin desensitisation in specialist centres (tolerance can be induced by starting at very low doses and gradually increasing under medical supervision).',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 4))

story.append(bp('<b>Occupational Asthma:</b>'))
for pt in [
    'Definition: asthma caused by exposure to an agent at work.',
    'Key question: "Are your symptoms better on weekends and holidays and worse when you return to work?"',
    'Common occupational sensitisers: Isocyanates (spray painting, foam manufacturing). Flour dust (bakers). Latex (healthcare). Colophony solder fumes (electronics). Animal proteins (lab workers, vets).',
    'Management: Remove from exposure — complete removal gives best outcome. If cannot remove, use respiratory protection. SABA prophylaxis before exposure if mild. Step-up therapy. Compensation and occupational health involvement.',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 4))

story.append(bp('<b>Exercise-Induced Bronchoconstriction (EIB):</b>'))
for pt in [
    'Symptoms during or immediately after vigorous exercise. Peak at 5–10 minutes after exercise stops.',
    'Mechanism: rapid breathing through mouth during exercise → cold, dry air → osmotic changes in airway cells → mast cell activation → bronchoconstriction.',
    'Management: Warm-up exercises (reduce severity). Nose-breathing where possible. Short-acting salbutamol (400mcg) 15 minutes before exercise. Long-acting montelukast very effective prophylaxis for EIB.',
    'Elite athletes: EIB is very common. Must use non-prohibited medications. SABA is allowed in sport (must declare). Some beta-2 agonists are banned at high doses.',
]:
    story.append(bp(f'• {pt}'))
divider(story)

# ── §11 PHARMACOLOGY ─────────────────────────────────────────────────────────
sec_header('Section 11: Pharmacology — Every Drug Used in Asthma and Airway Disease', story)

pharm_table = [
    ['Drug / Class','Mechanism','Dose / Route','Key Points'],
    ['Salbutamol\n(SABA — Short-Acting\nBeta-2 Agonist)','Stimulates beta-2 adrenergic\nreceptors on bronchiole smooth muscle.\nActivates adenylyl cyclase → cAMP\nrises → muscle RELAXES → airway opens.\nOnset: 5 minutes. Duration: 4 hours.','Inhaled MDI: 100mcg 1–2 puffs PRN.\nNebulised: 2.5–5mg every 20–30 min\nin attack. IV infusion: 5–10 mcg/min\nin life-threatening attack.','Beta-2 selectivity — minimal\nbeta-1 cardiac effects at standard doses.\nSide effects: tremor, tachycardia,\nhypokalaemia, lactic acidosis (high dose).\nNEVER use SABA alone without ICS\nin persistent asthma (masking).'],
    ['Ipratropium\n(SAMA — Short-Acting\nMuscarinic Antagonist)','Blocks M3 muscarinic receptors\non bronchial smooth muscle.\nBlocks the vagus nerve\'s bronchoconstrictor\neffect. Also reduces mucus secretion.\nOnset: 15 min. Duration: 6 hours.','Nebulised 500mcg every 4–6 hours.\nAdded to salbutamol in acute severe\nand life-threatening asthma.','Added to salbutamol in:\nacute severe and\nlife-threatening attacks.\nNot for routine long-term\nasthma maintenance.\nBeneficial mainly in\nacute severe asthma.'],
    ['Beclometasone /\nBudesonide / Fluticasone\n(ICS — Inhaled\nCorticosteroids)','Binds intracellular glucocorticoid\nreceptors in airway cells.\nReduces transcription of\npro-inflammatory genes (IL-4, IL-5,\nIL-13, eotaxin).\nReduces eosinophil recruitment\nand mast cell numbers in airway.','Beclometasone:\nLow dose: 100–400 mcg/day.\nHigh dose: 800–2000 mcg/day.\nTwice daily dosing.','Most important preventer drug.\nStart at step 2 in all\npersistent asthma.\nSide effects: oral candidiasis\n(thrush) — rinse mouth after.\nHoarse voice. Systemic effects\n(growth suppression in children)\nat high doses.'],
    ['Salmeterol / Formoterol\n(LABA — Long-Acting\nBeta-2 Agonist)','Same mechanism as salbutamol\nbut acts for 12 hours.\nFormoterol: onset in 5 min\n(can be used as rescue in SMART\nregimen with ICS/formoterol).','Salmeterol 50mcg twice daily.\nFormoterol 6–12 mcg twice daily.\nAlways combined with ICS.','NEVER use LABA without ICS\n(risk of asthma death from masking).\nCombined inhalers: Seretide\n(salmeterol+fluticasone) or\nSymbicort (formoterol+budesonide).'],
    ['Montelukast\n(LTRA — Leukotriene\nReceptor Antagonist)','Blocks cysteinyl leukotriene\nreceptors (CysLT1) on airway cells.\nLeukotrienes (LTC4, LTD4, LTE4)\nare the main mediators of both\nbronchospasm and inflammation\nin asthma.','10mg oral once daily (adults).\n5mg chewable tablet\n(children 6–14 years).','Add-on at step 4.\nExcellent for:\nNSAID/aspirin-exacerbated asthma.\nExercise-induced bronchoconstriction.\nAllergic rhinitis comorbidity.\nSide effects: rarely — neuropsychiatric\n(nightmares, mood changes). Alert patient.'],
    ['Theophylline\n(Aminophylline IV\n= theophylline salt)','Phosphodiesterase inhibitor.\nRaises cAMP in smooth muscle\n→ bronchodilation.\nAlso: adenosine receptor\nantagonism. Anti-inflammatory\neffects at low doses.','Oral theophylline: 200–400mg\ntwice daily (modified release).\nIV aminophylline: loading dose\n5mg/kg over 20 min THEN\n0.5mg/kg/hr infusion. ONLY\nif not already on theophylline.','Narrow therapeutic window:\nTherapeutic level: 10–20 mg/L.\nToxic > 20 mg/L.\nToxicity: nausea, vomiting,\nseizures, arrhythmias.\nMonitor levels.\nMany drug interactions (erythromycin,\nciprofloxacin, cimetidine increase levels).'],
    ['Magnesium Sulphate\nIV','Calcium channel blocker in smooth\nmuscle. Blocks Ca2+ entry into\nbronchiole smooth muscle cells.\nResult: bronchiole relaxes,\nairway opens.','1.2–2g IV over 20 minutes.\nSingle dose in acute severe\nor life-threatening asthma.\nAlso available nebulised.','Given once in acute attack.\nEvidence from BTS guidelines.\nSide effects: flushing, hypotension\n(rare at this dose). Safe at these doses.\nDo NOT repeat dose routinely.'],
    ['Prednisolone\n(oral steroids)','Systemic corticosteroid.\nSame mechanism as ICS\nbut systemic effect.\nPowerful anti-inflammatory.','Acute attack: 40mg once daily\nfor 5 days (adults).\nChronic: lowest effective dose.\nIV hydrocortisone 100mg in\nsevere attack (cannot swallow).','5-day course: no need\nto taper (short course).\nLonger courses: wean gradually\n(suppress adrenal cortex).\nSide effects of long-term:\noseoporosis, diabetes, hypertension,\ncataracts, adrenal suppression.'],
    ['Adrenaline\n(Epinephrine)','Alpha-1: vasoconstriction\n(reduces laryngeal oedema).\nBeta-2: bronchodilation.\nBeta-1: cardiac stimulation.','Anaphylaxis: 0.5mg IM\n(0.5ml of 1:1000).\ninto outer thigh.\nEpiPen: 0.3mg auto-injector.','FIRST-LINE for anaphylaxis.\nIM preferred over IV\n(IV causes dangerous arrhythmias\nunless cardiac arrest).\nRepeat after 5 minutes\nif no response.'],
    ['Icatibant\n(Firazyr)','Bradykinin B2 receptor\nantagonist.\nBlocks bradykinin\'s effect\non blood vessel walls.\nPrevents oedema formation.','30mg SC injection.\nRepeat after 6 hours\nif needed (max 3 doses\nin 24 hours).','SPECIFIC for HAE acute attacks\nand ACE inhibitor-induced angioedema.\nNot useful in histamine-mediated\nangioedema (anaphylaxis).'],
    ['C1-INH concentrate\n(Berinert, Ruconest)','Replaces the missing\nC1-esterase inhibitor\nprotein directly.\nRestores control of\nbradykinin generation.','Berinert: 20 units/kg IV.\nRuconest (recombinant): 50 units/kg IV.','First-line for HAE acute attacks.\nAlso used as prophylaxis before\nplanned procedures or surgery.\nSafe in pregnancy.'],
    ['Omeprazole / PPIs\n(Proton Pump Inhibitors)','Irreversibly inhibits\nH+/K+-ATPase pump\nin stomach parietal cells.\nReduces gastric acid\nproduction by 95%.','20–40mg oral once daily\nbefore morning meal.','Treat GERD contributing to\nasthma/laryngospasm.\nFew side effects at standard doses.\nLong-term: low magnesium, low B12,\nincreased C. difficile risk.'],
]
story.append(plain_table(pharm_table,[CW*0.16,CW*0.24,CW*0.18,CW*0.42]))
divider(story)

# ── §12 MRCP EXAM TRIGGERS ───────────────────────────────────────────────────
sec_header('Section 12: MRCP Exam Triggers — High-Yield Clinical Scenarios', story)

triggers = [
    ['#','Scenario','Key Teaching Point','Answer'],
    ['1','A 23-year-old woman with known asthma presents with wheeze. She uses her salbutamol inhaler 20 times/day. Her PEFR is 38% of predicted. She can speak single words only.',
     'Acute severe or life-threatening asthma — severity classification.',
     'PEFR 33–50% = acute severe. Cannot speak = approaching life-threatening. Give: continuous salbutamol neb + ipratropium neb + hydrocortisone 100mg IV + magnesium sulphate 2g IV over 20 min + oxygen + CXR.'],
    ['2','A patient with acute severe asthma does not improve after 3 salbutamol nebulisers and IV hydrocortisone. What is the next step?',
     'Add-on therapy in acute severe asthma — magnesium.',
     'IV magnesium sulphate 1.2–2g over 20 minutes. This is first-line add-on in BTS guidelines for acute severe asthma not responding to SABA + steroids.'],
    ['3','A 24-year-old woman presents with episodic breathlessness and stridor. Spirometry is normal between attacks. Salbutamol and steroids do not help.',
     'Vocal cord dysfunction (VCD) — classic presentation.',
     'VCD — diagnosed by laryngoscopy during attack showing paradoxical adduction of cords on inspiration. Normal FeNO. Treat: speech therapy. Refer to ENT/respiratory.'],
    ['4','A 26-year-old woman presents with recurrent facial and lip swelling, abdominal colic, and one episode of throat swelling. No urticaria. Her mother has the same condition.',
     'Hereditary Angioedema (HAE) — key differentiators.',
     'HAE: No urticaria (distinguishes from allergic angioedema). Family history. Abdominal colic. Check: C4 (will be LOW). C1-INH level and function. Adrenaline does NOT work. Treat acute episode with C1-INH concentrate or icatibant.'],
    ['5','A patient is on ramipril for hypertension. She now presents with sudden swelling of her lips and tongue. No rash. No breathlessness.',
     'ACE inhibitor-induced angioedema — bradykinin mechanism.',
     'ACE inhibitors block breakdown of bradykinin → bradykinin accumulates → angioedema. No urticaria. Can occur years after starting the drug. STOP the ACE inhibitor immediately. Switch to ARB with caution (10% cross-reactivity) or alternative antihypertensive. Acute: icatibant or C1-INH concentrate.'],
    ['6','A 25-year-old asthmatic woman is given ibuprofen by her GP for knee pain. 45 minutes later she develops severe wheeze requiring hospital admission.',
     'Aspirin-exacerbated respiratory disease (AERD) / Samter\'s Triad.',
     'NSAIDs contraindicated. Check for nasal polyps (Samter\'s triad). Prescribe: paracetamol for pain. Start montelukast. Refer to specialist for aspirin desensitisation if needed.'],
    ['7','A 22-year-old asthmatic has total serum IgE of 2400 IU/mL, positive Aspergillus IgE, sputum eosinophilia, and central bronchiectasis on CT.',
     'ABPA — diagnostic criteria.',
     'ABPA. Treatment: oral prednisolone (0.5mg/kg for 2 weeks then taper) + itraconazole 200mg twice daily for 4–6 months. Monitor: total IgE — should fall. Rising IgE = relapse.'],
    ['8','An asthma patient on step 3 (ICS + LABA) still has frequent exacerbations. Blood eosinophils = 800 cells/uL. Total IgE = 450 IU/mL.',
     'Biologic therapy selection — eosinophilic asthma.',
     'Step 5 biologic candidate. High eosinophils = mepolizumab or benralizumab (anti-IL-5 / anti-IL-5Ra). If sensitised to perennial allergen also = omalizumab (anti-IgE). Refer to severe asthma service.'],
    ['9','An asthma patient has PEFR 29% and rising PaCO2 of 5.8 kPa (normal). She looks exhausted.',
     'Rising PaCO2 in asthma = DANGER sign.',
     'Normal PaCO2 in a tachypnoeic asthma patient = patient is tiring. Rising PaCO2 = impending respiratory failure. CALL ICU immediately. Prepare for intubation. Give magnesium sulphate, IV salbutamol infusion.'],
    ['10','A young woman wakes from sleep at 2am, gasping and unable to breathe for about 30 seconds. Her chest exam and peak flow are normal in clinic.',
     'Laryngospasm from GERD — nocturnal pattern.',
     'GERD-induced laryngospasm. Nocturnal attacks as acid refluxes when lying flat. Investigate: 24-hour pH monitoring. Empirical trial: omeprazole 40mg daily. Lifestyle: head of bed up, no food 3 hours before sleep.'],
    ['11','A newly diagnosed asthmatic is started on salbutamol only (PRN). She comes back 6 months later with frequent attacks.',
     'Undertreated asthma — importance of ICS preventer.',
     'Salbutamol alone (SABA) does not treat the underlying inflammation. She needs step 2 treatment: add ICS (beclometasone 200–400 mcg twice daily). Explain difference between reliever (salbutamol) and preventer (ICS).'],
    ['12','A patient with severe asthma is started on salmeterol (LABA) alone without ICS.',
     'LABA without ICS = dangerous.',
     'LABA monotherapy in asthma is CONTRAINDICATED. It can mask worsening asthma and increase asthma deaths. LABA must ALWAYS be combined with ICS. Replace with combination inhaler (Seretide or Symbicort).'],
]
story.append(plain_table(triggers,[CW*0.04,CW*0.26,CW*0.22,CW*0.48]))
divider(story)

# ── §13 PACES AND MINIMAL RESOURCES ──────────────────────────────────────────
sec_header('Section 13: PACES Guide + Minimal Resources Management', story)

story.append(bp('<b>PACES — History Station: Recurrent Breathlessness in Young Adult</b>'))
for pt in [
    '<b>Open question:</b> "Can you tell me about your breathing problem in your own words?"',
    '<b>Onset:</b> "When did this first start? Did you have anything like this as a child?"',
    '<b>Character:</b> "When you get breathless, do you also wheeze? Do you hear a whistling from your chest or a noise from your throat?"',
    '<b>Upper vs lower:</b> "The noise — is it when you breathe IN or breathe OUT?" (In = upper = VCD/laryngeal. Out = lower = asthma/bronchitis.)',
    '<b>Triggers:</b> "Does anything bring it on? Pets, dust, cold air, exercise, perfumes, stress, certain foods? Any medications (NSAIDs, beta-blockers, ACE inhibitors)?"',
    '<b>Time pattern:</b> "When in the day is it worst? Is it worse at night? Worse in the mornings? Worse at work than at weekends?"',
    '<b>Treatment response:</b> "Does the reliever inhaler (salbutamol) help? How much? How quickly?" (If no response to salbutamol → consider VCD, HAE.)',
    '<b>Atopic history:</b> "Do you have hayfever? Eczema? Any food allergies? Any previous anaphylaxis?"',
    '<b>Swelling:</b> "Have you ever had swelling of your lips, tongue, or throat? Any abdominal cramps during attacks? Any skin hives/rash?" (Rash + swelling = anaphylaxis. Swelling without rash = HAE.)',
    '<b>Acid reflux:</b> "Do you get heartburn? Does it wake you at night? Do you sometimes wake up unable to breathe for a minute?"',
    '<b>Menstrual link:</b> "Do attacks link to your menstrual cycle? Worse just before your period?" (Premenstrual asthma.)',
    '<b>Family history:</b> "Does anyone in your family have asthma, severe allergies, or episodes of facial swelling?" (HAE is autosomal dominant.)',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 5))

story.append(bp('<b>PACES — Examination: The Breathless Young Patient</b>'))
for pt in [
    '<b>End of bed:</b> Distress? Position (tripod = severe). Using neck muscles? Cyanosed? Able to speak?',
    '<b>Vital signs:</b> RR, HR, BP, SpO2, PEFR (most important bedside test in asthma).',
    '<b>Hands:</b> Tremor (salbutamol side effect). Clubbing absent in asthma (clubbing = consider bronchiectasis). CRT.',
    '<b>Face:</b> Flushed (early attack). Pursed lip breathing. Nasal flaring. Nasal polyps (Samter\'s). Facial/lip swelling (angioedema). Urticaria on skin.',
    '<b>Neck:</b> Trachea central (deviation = pneumothorax). Accessory muscle use (sternocleidomastoid). JVP raised in tension pneumothorax.',
    '<b>Chest inspection:</b> Barrel-shaped (hyperinflation). Intercostal recession. Harrison\'s sulcus (rib deformity in chronic childhood asthma — ribs pulled in at attachment to diaphragm).',
    '<b>Percussion:</b> Hyperresonant bilaterally (hyperinflation). Unilateral hyper-resonance = pneumothorax.',
    '<b>Auscultation:</b> Bilateral expiratory wheeze (asthma). High-pitched inspiratory stridor (upper airway). Monophonic wheeze (single pitch = fixed obstruction = tumour or foreign body). Polyphonic wheeze (multiple pitches = asthma). Silent chest = life-threatening.',
    '<b>Abdominal:</b> Not typically affected in asthma. Tenderness + bloating in HAE (abdominal colic attack).',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 5))

story.append(bp('<b>PACES Presentation Template:</b>'))
story.append(bp('"This 23-year-old woman presents with recurrent wheeze, breathlessness, and cough since childhood. On examination she is mildly breathless, using accessory muscles. Respiratory rate is 26. SpO2 is 95% on air. Peak flow is 58% of predicted. There is bilateral expiratory wheeze on auscultation. The lungs are hyperresonant to percussion. The trachea is central. In summary, this picture is consistent with an acute exacerbation of asthma. I would assess severity, initiate salbutamol nebulisers and oral prednisolone, request a chest X-ray to exclude pneumothorax, and arrange admission for monitoring."'))
story.append(Spacer(1, 5))

story.append(bp('<b>Minimal Resources Management:</b>'))
minimal_table = [
    ['Step','Action','Minimum Resources'],
    ['1. Confirm asthma','Peak flow (PEFR) measurement.\nCheck it before and after salbutamol.\n>20% improvement = reversible obstruction.','Portable peak flow meter.'],
    ['2. Oxygen','Nasal prongs 4–6 L/min\nor simple face mask.','Oxygen cylinder + mask.'],
    ['3. Salbutamol','Via MDI (pressurised inhaler)\n+ spacer device.\n4–10 puffs (400–1000 mcg) every\n20 minutes — as effective as nebuliser.','MDI inhaler + spacer.\nSpacers can be improvised from\na plastic bottle with a hole.'],
    ['4. Steroids','Oral prednisolone 40mg.\nIf cannot swallow: IV hydrocortisone 100mg.','Tablets. Injectable preparation.'],
    ['5. Assess response','PEFR again after 15–30 minutes.\nImproving = continue. Worsening = escalate.','Peak flow meter. Watch.'],
    ['6. Refer','All acute severe attacks:\nrefer to hospital with monitoring.','Phone. Transport.'],
    ['7. Discharge plan','Written Asthma Action Plan.\nInhaler technique check.\nSpare salbutamol. Follow-up in 48h.','Paper. Inhaler.'],
]
story.append(plain_table(minimal_table,[CW*0.1,CW*0.55,CW*0.35]))

memory_hook('PACES: PEFR is the most important bedside test in asthma. Always state it. Wheeze = lower airway. Stridor = upper airway. Silent chest = EMERGENCY. Always ask about triggers, atopy family history, and response to salbutamol. For VCD: ask "does the noise happen breathing IN or OUT?"', story)
divider(story)

# ── MASTER SUMMARY ────────────────────────────────────────────────────────────
story.append(Spacer(1, 6))
sGrn  = ParagraphStyle('GR',  fontName='DV',   fontSize=8.5, leading=13, textColor=HexColor('#155724'), spaceAfter=0)
sGrnB = ParagraphStyle('GRB', fontName='DV-B', fontSize=10,  leading=15, textColor=HexColor('#155724'), spaceAfter=2)
gTS1  = TableStyle([
    ('BACKGROUND',(0,0),(-1,-1),HexColor('#d4edda')),
    ('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),10),
    ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),
    ('TOPPADDING',(0,0),(0,0),8),('BOTTOMPADDING',(0,-1),(0,-1),8),
])
gTSO  = TableStyle([
    ('BOX',(0,0),(-1,-1),2,HexColor('#28a745')),
    ('BACKGROUND',(0,0),(-1,-1),HexColor('#d4edda')),
    ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
    ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),
])
gRows = [
    [Paragraph('MASTER MEMORY SUMMARY — ASTHMA, LARYNGEAL SPASM & AIRWAY DISEASE', sGrnB)],
    [Paragraph('ANATOMY KEY: Stridor = UPPER airway (larynx). Wheeze = LOWER airway (bronchioles). Salbutamol only helps LOWER airway. Stridor on inspiration = VCD/laryngospasm/laryngeal oedema.', sGrn)],
    [Paragraph('ASTHMA MECHANISM: Allergen + IgE + Mast cells → Histamine + Leukotrienes → Bronchoconstriction (early, salbutamol reverses) + Eosinophilic inflammation (late, steroids reverse) + Mucus plugging. All 3 together in attack.', sGrn)],
    [Paragraph('TRIGGERS: Allergens (cat most potent). Rhinovirus URTI. NSAIDs + Beta-blockers (NEVER give). Occupational (better on holidays). GERD. Exercise. Premenstrual. Mould.', sGrn)],
    [Paragraph('SEVERITY: PEFR 50-75% = Moderate. 33-50% = Acute Severe (cannot complete sentences, HR>110, RR>25). <33% = Life-Threatening (silent chest, SpO2 <92%, cyanosis, exhaustion, confusion, bradycardia). Rising PaCO2 = ICU EMERGENCY.', sGrn)],
    [Paragraph('ACUTE MANAGEMENT: Oxygen (94-98%) + Salbutamol neb (5mg continuous) + Ipratropium 500mcg + Hydrocortisone 100mg IV + Magnesium sulphate 1.2-2g IV over 20 min (in acute severe/life-threatening). CXR (exclude pneumothorax).', sGrn)],
    [Paragraph('BTS STEPS: 1=SABA PRN. 2=+ICS. 3=+LABA (NEVER without ICS). 4=High ICS + Montelukast/Theophylline/Tiotropium. 5=Biologics (Omalizumab=high IgE; Mepolizumab/Benralizumab=high eosinophils; Tezepelumab=any).', sGrn)],
    [Paragraph('VCD/ILO: Stridor (not wheeze). Inspiratory obstruction. No response to salbutamol/steroids. Normal FeNO. Diagnosed by laryngoscopy. Treated by speech therapy. Flow-volume loop: flat inspiratory limb.', sGrn)],
    [Paragraph('HAE: No urticaria. Slow swelling (hours). Abdominal colic. Family history. C4 LOW (best screen). C1-INH low. Adrenaline/antihistamines DO NOT WORK. Treat: C1-INH concentrate or Icatibant. OCP + ACE inhibitors WORSEN HAE.', sGrn)],
    [Paragraph('ANAPHYLAXIS: Urticaria + angioedema + bronchospasm + hypotension. ADRENALINE 0.5mg IM (outer thigh) FIRST. Then: IV fluids + chlorphenamine + hydrocortisone. Tryptase confirms (take 1-3h after attack).', sGrn)],
    [Paragraph('ABPA: Asthma + total IgE >1000 + central bronchiectasis on CT + Aspergillus IgE raised + eosinophilia. Treatment: Prednisolone + Itraconazole. Monitor IgE.', sGrn)],
    [Paragraph('GERD-ASTHMA: GERD causes cough, laryngospasm (nocturnal gasping), and worsens asthma. Treat: PPI + elevate head of bed + avoid food 3h before sleep. 24h pH monitoring confirms.', sGrn)],
    [Paragraph('PHARMACOLOGY: Salbutamol (beta-2, 4h). Ipratropium (anticholinergic, add in acute severe). ICS (preventer, anti-inflammatory). LABA (12h, always with ICS). Montelukast (leukotriene blocker, NSAID asthma). Theophylline (narrow window, monitor levels). Magnesium 2g IV (calcium channel blocker, relaxes bronchioles). Icatibant (bradykinin B2 antagonist, HAE).', sGrn)],
    [Paragraph('MRCP KEYS: (1) PEFR <33% + silent chest = life-threatening. (2) Normal PaCO2 in tachypnoeic asthmatic = tiring = ICU. (3) LABA must NEVER be given without ICS. (4) HAE: C4 low, no urticaria, no adrenaline. (5) VCD: stridor, no response to salbutamol, speech therapy treats. (6) ACE inhibitor angioedema = bradykinin = stop drug, give icatibant. (7) Theophylline toxicity = arrhythmias + seizures.', sGrn)],
]
innerG = Table(gRows, colWidths=[CW-4])
innerG.setStyle(gTS1)
outerG = Table([[innerG]], colWidths=[CW])
outerG.setStyle(gTSO)
story.append(outerG)
story.append(Spacer(1, 12))

doc.build(story)
print('SUCCESS: Asthma & Laryngeal Airway MRCP Note saved to', OUT)
