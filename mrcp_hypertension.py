"""
MRCP REVISION NOTE: Arterial Hypertension — Diagnosis, Outpatient & Emergency Management
Page size: A3 Portrait (297mm x 420mm) for readable, spacious layout.
PIL diagram rule: fB=28px, fS=22px, fXS=17px — renders ~22/17/13pt on A3.
Interactive Professor Q&A woven through + end-of-topic MCQ self-test + separate answer key.
"""
import os
from io import BytesIO
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, Image as RLImage, PageBreak)
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageDraw, ImageFont

OUT = '/mnt/user-data/outputs/Hypertension_MRCP_Note.pdf'
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

# New styles for interactive Q&A and self-test
sQ     = ParagraphStyle('QQ', fontName='DV-B', fontSize=10, leading=14,
         textColor=HexColor('#5b2c6f'), spaceAfter=0)
sHint  = ParagraphStyle('HH', fontName='DV-I', fontSize=9.5, leading=14,
         textColor=HexColor('#856404'), spaceAfter=0)
sAns   = ParagraphStyle('AA', fontName='DV', fontSize=10, leading=15,
         textColor=HexColor('#155724'), spaceAfter=0)
sQNum  = ParagraphStyle('QN', fontName='DV-B', fontSize=11.5, leading=16,
         textColor=HexColor('#0d5c63'), spaceBefore=8, spaceAfter=3)
sVig   = ParagraphStyle('VG', fontName='DV', fontSize=10, leading=15,
         textColor=HexColor('#1a1a2e'), spaceAfter=4)
sOpt   = ParagraphStyle('OP', fontName='DV', fontSize=9.8, leading=14,
         textColor=HexColor('#1a1a2e'), spaceAfter=2, leftIndent=16)

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

# ── NEW: Interactive Professor Q&A dialogue block (Permanent Rule #19) ───────
# Pattern: Professor STATES a fact -> ASKS a question -> gives a HINT/memory
# device -> REVEALS the answer with explanation. Mirrors ward-round teaching.
def qa_block(statement, question, hint, answer, story):
    story.append(bp(statement))
    story.append(Spacer(1, 3))
    qt = Table([[Paragraph(f'<b>PROFESSOR ASKS:</b>  {question}', sQ)]], colWidths=[CW])
    qt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PUR_L),
        ('BOX',(0,0),(-1,-1),1.5,PUR_D),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.append(qt); story.append(Spacer(1, 3))
    ht = Table([[Paragraph(f'<i>HINT — think first:</i>  {hint}', sHint)]], colWidths=[CW])
    ht.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),AMBER),
        ('BOX',(0,0),(-1,-1),1,AMBER_B),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(ht); story.append(Spacer(1, 3))
    at = Table([[Paragraph(f'<b>ANSWER:</b>  {answer}', sAns)]], colWidths=[CW])
    at.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),GREEN_L),
        ('BOX',(0,0),(-1,-1),1.5,GREEN_D),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.append(at); story.append(Spacer(1, 8))

# ── NEW: End-of-topic MCQ self-test + separate answer key (Permanent Rule #20/21)
ANSWER_KEY = []   # collects (number, correct_letter, explanation) for the separate key

def mcq(num, vignette, options, correct, explanation, story):
    """options: list of (letter, text). correct: letter. Stores answer for the key page."""
    story.append(Paragraph(f'<b>Question {num}</b>', sQNum))
    story.append(Paragraph(vignette, sVig))
    for letter, text in options:
        story.append(Paragraph(f'{letter})  {text}', sOpt))
    story.append(Paragraph('Your answer: _________     (write A-E here, check the key at the end)', sBody))
    story.append(Spacer(1, 8))
    ANSWER_KEY.append((num, correct, explanation))

def print_answer_key(story):
    for num, letter, explanation in ANSWER_KEY:
        story.append(Paragraph(f'<b>Q{num} — Correct answer: {letter}</b>   {explanation}', sBody))
        story.append(Spacer(1, 3))

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

# ── PIL 1: BP = CO x SVR — Physiology of Blood Pressure Regulation ───────────
def make_bp_physiology():
    W, H = 900, 760
    img = Image.new('RGB', (W, H), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    f = load_fonts({'T':28,'B':24,'S':19,'XS':16})

    draw.rectangle([0,0,W-1,H-1], fill='#f4fbfc', outline='#1a8a94', width=3)
    draw.rectangle([0,0,W-1,52], fill='#0d5c63')
    draw.text((W//2, 26), 'HOW BLOOD PRESSURE IS NORMALLY CONTROLLED',
              font=f['T'], fill='#ffffff', anchor='mm')

    # Central equation box
    draw.rectangle([280, 78, 620, 148], fill='#fff3cd', outline='#e6a817', width=3)
    draw.text((450, 100), 'BLOOD PRESSURE  =', font=f['B'], fill='#5b3a00', anchor='mm')
    draw.text((450, 130), 'CARDIAC OUTPUT  x  RESISTANCE OF VESSELS', font=f['S'], fill='#5b3a00', anchor='mm')

    # Down arrows to two branches
    arr_d(draw, 370, 148, length=30, col='#0d5c63', w=3)
    arr_d(draw, 530, 148, length=30, col='#0d5c63', w=3)

    # Left branch: Cardiac Output box
    draw.rectangle([110, 188, 430, 268], fill='#e8f4fd', outline='#2471a3', width=3)
    draw.text((270, 208), 'CARDIAC OUTPUT (CO)', font=f['B'], fill='#2471a3', anchor='mm')
    draw.text((270, 234), 'CO = Heart Rate  x  Stroke Volume', font=f['XS'], fill='#333333', anchor='mm')
    draw.text((270, 254), 'Driven by: sympathetic nerves + blood volume', font=f['XS'], fill='#333333', anchor='mm')

    # Right branch: SVR box
    draw.rectangle([470, 188, 790, 268], fill='#fde8e8', outline='#c0392b', width=3)
    draw.text((630, 208), 'VESSEL RESISTANCE (SVR)', font=f['B'], fill='#c0392b', anchor='mm')
    draw.text((630, 234), 'How tightly arterioles are squeezed shut', font=f['XS'], fill='#333333', anchor='mm')
    draw.text((630, 254), 'Driven by: RAAS + sympathetic tone + endothelium', font=f['XS'], fill='#333333', anchor='mm')

    arr_d(draw, 270, 268, length=28, col='#2471a3', w=3)
    arr_d(draw, 630, 268, length=28, col='#c0392b', w=3)

    # Four regulatory systems row
    systems = [
        ('#d4edda','#28a745','KIDNEYS','Control salt and water.\nMore salt kept = more\nblood volume = higher BP.'),
        ('#f5eef8','#7d3c98','RAAS CASCADE','Renin -> Angiotensin I ->\nAngiotensin II (by ACE) ->\nvasoconstriction + aldosterone.'),
        ('#fef3e2','#d4640a','SYMPATHETIC\nNERVOUS SYSTEM','Adrenaline + noradrenaline.\nIncrease heart rate AND\nsqueeze blood vessels.'),
        ('#e0f4f5','#1a8a94','BARORECEPTORS','Pressure sensors in carotid\nsinus + aortic arch.\nFast moment-to-moment control.'),
    ]
    box_w = 190; box_h = 150; gap = 14
    start_x = (W - (4*box_w + 3*gap)) // 2
    top_y = 320
    for i,(bg,bd,name,detail) in enumerate(systems):
        x0 = start_x + i*(box_w+gap)
        draw.rectangle([x0, top_y, x0+box_w, top_y+box_h], fill=bg, outline=bd, width=3)
        draw.text((x0+box_w//2, top_y+30), name, font=f['B'], fill=bd, anchor='mm')
        draw.multiline_text((x0+box_w//2, top_y+95), detail, font=f['XS'], fill='#333333', anchor='mm', align='center', spacing=6)

    # Down arrows from systems to outcome
    for i in range(4):
        x0 = start_x + i*(box_w+gap) + box_w//2
        arr_d(draw, x0, top_y+box_h, length=26, col=systems[i][1], w=3)

    # Outcome box
    draw.rectangle([170, top_y+box_h+30, 730, top_y+box_h+100], fill='#0d5c63', outline='#0d5c63', width=3)
    draw.text((W//2, top_y+box_h+50), 'NORMAL BP MAINTAINED:  AROUND 120/80 mmHg',
              font=f['B'], fill='#ffffff', anchor='mm')
    draw.text((W//2, top_y+box_h+76), 'Hypertension = ANY of these systems pushes too hard, for too long, in the wrong direction',
              font=f['XS'], fill='#d4edda', anchor='mm')

    # Footer
    draw.rectangle([0, H-36, W-1, H-1], fill='#0d5c63')
    draw.text((W//2, H-18),
              'KEY EQUATION FOR MRCP:  BP = CARDIAC OUTPUT  x  SYSTEMIC VASCULAR RESISTANCE  (SVR)',
              font=f['XS'], fill='#ffffff', anchor='mm')

    img.save('/tmp/bp_physiology.png')

make_bp_physiology()
img_physiology = i2r(Image.open('/tmp/bp_physiology.png'), CW)

# ── PIL 2: Target Organ Damage Map ───────────────────────────────────────────
def make_organ_damage():
    W, H = 900, 760
    img = Image.new('RGB', (W, H), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    f = load_fonts({'T':28,'B':24,'S':19,'XS':16})

    draw.rectangle([0,0,W-1,H-1], fill='#f4fbfc', outline='#1a8a94', width=3)
    draw.rectangle([0,0,W-1,52], fill='#0d5c63')
    draw.text((W//2, 26), 'HYPERTENSION: THE SILENT KILLER — TARGET ORGAN DAMAGE',
              font=f['T'], fill='#ffffff', anchor='mm')

    organs = [
        ('#fde8e8','#c0392b','BRAIN','Stroke (bleed or clot)  |  Hypertensive encephalopathy  |  Vascular dementia  |  TIA'),
        ('#f5eef8','#7d3c98','EYES (RETINA)','Hypertensive retinopathy grades I-IV  |  Papilloedema in malignant HTN  |  Visual loss'),
        ('#e8f4fd','#2471a3','HEART','Left ventricular hypertrophy (LVH)  |  Heart failure  |  Angina / MI  |  Atrial fibrillation'),
        ('#fef3e2','#d4640a','KIDNEYS','Nephrosclerosis  |  Proteinuria (ACR raised)  |  Chronic kidney disease  |  Renal failure'),
        ('#d4edda','#28a745','BLOOD VESSELS','Aortic aneurysm  |  Aortic dissection  |  Peripheral artery disease  |  Atherosclerosis'),
    ]
    box_h = 96; gap = 18
    start_y = 78
    cx = W//2; bw = 760
    for i,(bg,bd,name,detail) in enumerate(organs):
        cy = start_y + i*(box_h+gap) + box_h//2
        x0 = cx - bw//2; x1 = cx + bw//2
        draw.rectangle([x0, cy-box_h//2, x1, cy+box_h//2], fill=bg, outline=bd, width=3)
        draw.text((x0+115, cy), name, font=f['B'], fill=bd, anchor='mm')
        draw.line([(x0+220, cy-box_h//2+12),(x0+220, cy+box_h//2-12)], fill=bd, width=2)
        draw.multiline_text((x0+250, cy), detail.replace('  |  ','\n'), font=f['XS'], fill='#333333', anchor='lm', spacing=7)
        if i < len(organs)-1:
            arr_d(draw, cx, cy+box_h//2, length=gap, col=bd, w=3)

    draw.rectangle([0, H-36, W-1, H-1], fill='#0d5c63')
    draw.text((W//2, H-18),
              'WHY "SILENT"?  Usually NO symptoms until organ damage already happened — this is why we screen everyone',
              font=f['XS'], fill='#ffffff', anchor='mm')

    img.save('/tmp/organ_damage.png')

make_organ_damage()
img_organdamage = i2r(Image.open('/tmp/organ_damage.png'), CW)

# ── PIL 3: BP Classification / Staging Chart ─────────────────────────────────
def make_classification():
    W, H = 900, 700
    img = Image.new('RGB', (W, H), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    f = load_fonts({'T':28,'B':23,'S':19,'XS':16})

    draw.rectangle([0,0,W-1,H-1], fill='#f4fbfc', outline='#1a8a94', width=3)
    draw.rectangle([0,0,W-1,52], fill='#0d5c63')
    draw.text((W//2, 26), 'BLOOD PRESSURE CATEGORIES (NICE / ESC 2023)',
              font=f['T'], fill='#ffffff', anchor='mm')

    # Column headers
    draw.text((250, 76), 'CLINIC BP (mmHg)', font=f['S'], fill='#0d5c63', anchor='mm')
    draw.text((620, 76), 'HOME / AMBULATORY BP (mmHg)', font=f['S'], fill='#0d5c63', anchor='mm')

    cats = [
        ('#d4edda','#28a745','OPTIMAL / NORMAL','< 120/80','< 115/75'),
        ('#e0f4f5','#1a8a94','HIGH-NORMAL','120-139 / 80-89','115-134 / 75-84'),
        ('#fff3cd','#e6a817','STAGE 1 HYPERTENSION','140-159 / 90-99','135-149 / 85-94'),
        ('#fef3e2','#d4640a','STAGE 2 HYPERTENSION','160-179 / 100-119','150-179 / 95-119'),
        ('#fde8e8','#c0392b','SEVERE HYPERTENSION\n(STAGE 3)','>= 180 / 120',' clinic measurement\n used — admit if symptoms'),
        ('#5b2c6f','#3a1a4f','HYPERTENSIVE EMERGENCY','>= 180/120 PLUS\nsigns of organ damage','Same-day specialist\nassessment required'),
    ]
    box_h = 86; gap = 14
    start_y = 96
    for i,(bg,bd,name,clinic,home) in enumerate(cats):
        cy = start_y + i*(box_h+gap) + box_h//2
        txtcol = '#ffffff' if i==5 else bd
        draw.rectangle([60, cy-box_h//2, 840, cy+box_h//2], fill=bg, outline=bd, width=3)
        draw.multiline_text((250, cy), name, font=f['B'], fill=txtcol, anchor='mm', align='center', spacing=4)
        draw.multiline_text((480, cy), clinic, font=f['S'], fill=('#ffffff' if i==5 else '#333333'), anchor='lm', align='left', spacing=5)
        draw.multiline_text((660, cy), home, font=f['XS'], fill=('#ffffff' if i==5 else '#333333'), anchor='lm', align='left', spacing=5)

    draw.rectangle([0, H-36, W-1, H-1], fill='#0d5c63')
    draw.text((W//2, H-18),
              'RULE: Home/ambulatory BP readings are LOWER than clinic BP — this difference is built into the categories',
              font=f['XS'], fill='#ffffff', anchor='mm')

    img.save('/tmp/classification.png')

make_classification()
img_classification = i2r(Image.open('/tmp/classification.png'), CW)

# ── PIL 4: NICE Stepwise Treatment Ladder (A / C / D rule) ───────────────────
def make_treatment_ladder():
    W, H = 900, 800
    img = Image.new('RGB', (W, H), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    f = load_fonts({'T':28,'B':23,'S':19,'XS':16})

    draw.rectangle([0,0,W-1,H-1], fill='#f4fbfc', outline='#1a8a94', width=3)
    draw.rectangle([0,0,W-1,52], fill='#0d5c63')
    draw.text((W//2, 26), 'NICE STEPWISE DRUG LADDER FOR HYPERTENSION (THE A-C-D RULE)',
              font=f['T'], fill='#ffffff', anchor='mm')

    # Step boxes
    steps = [
        ('#d4edda','#28a745','STEP 1','Age < 55 and NOT Black African/Caribbean origin:  start  A  (ACE inhibitor or ARB)\nAge >= 55  OR  Black African/Caribbean origin (any age):  start  C  (Calcium channel blocker)'),
        ('#e0f4f5','#1a8a94','STEP 2','Combine  A + C\n(ACE inhibitor or ARB  PLUS  Calcium channel blocker)'),
        ('#fff3cd','#e6a817','STEP 3','Add  D  — a thiazide-like diuretic\nA + C + D   (e.g., ramipril + amlodipine + indapamide)'),
        ('#fef3e2','#d4640a','STEP 4\n(RESISTANT HTN)','Confirm with ABPM/HBPM first. If K+ <= 4.5: ADD low-dose SPIRONOLACTONE.\nIf K+ > 4.5: add ALPHA-BLOCKER or BETA-BLOCKER. Refer to specialist.'),
    ]
    box_h = 132; gap = 20
    start_y = 76
    for i,(bg,bd,step,detail) in enumerate(steps):
        cy = start_y + i*(box_h+gap) + box_h//2
        draw.rectangle([60, cy-box_h//2, 840, cy+box_h//2], fill=bg, outline=bd, width=3)
        draw.rectangle([60, cy-box_h//2, 230, cy+box_h//2], fill=bd)
        draw.multiline_text((145, cy), step, font=f['B'], fill='#ffffff', anchor='mm', align='center', spacing=4)
        draw.multiline_text((255, cy), detail, font=f['XS'], fill='#333333', anchor='lm', align='left', spacing=8)
        if i < len(steps)-1:
            arr_d(draw, 145, cy+box_h//2, length=gap, col=bd, w=3)

    # Footer reminder
    draw.rectangle([0, H-44, W-1, H-1], fill='#0d5c63')
    draw.multiline_text((W//2, H-22),
              'REMEMBER:  A = ACE-inhibitor/ARB   C = Calcium channel blocker   D = thiazide-like Diuretic   |   TARGET: < 140/90 (under 80y) or < 150/90 (80y+)',
              font=f['XS'], fill='#ffffff', anchor='mm', align='center', spacing=6)

    img.save('/tmp/treatment_ladder.png')

make_treatment_ladder()
img_ladder = i2r(Image.open('/tmp/treatment_ladder.png'), CW)

print('PIL diagrams done.')

# ═══════════════════════════════════════════════════════════════════════════
# STORY BUILD
# ═══════════════════════════════════════════════════════════════════════════
story = []

story.append(Paragraph('ARTERIAL HYPERTENSION', sTitle))
story.append(Paragraph('Diagnosis · Outpatient Management · Hypertensive Emergencies — MRCP Part 1, Part 2 & PACES, Interactive Edition', sSub))
story.append(HRFlowable(width=CW, thickness=2, color=TEAL, spaceAfter=10))

# §1 Clinical Scenario
sec_header('Section 1: The Clinical Scenario — How Hypertension Usually Presents', story)
story.append(bp('A 52-year-old man comes to the clinic for a routine check-up before a minor surgery. He feels completely well. His blood pressure is measured as <b>168/102 mmHg</b>. He is shocked — "But doctor, I feel fine! How can something be wrong with me?"'))
story.append(bp('This is the single most important lesson about hypertension: <b>it almost never causes symptoms until it has already caused damage.</b> This is why it is called "the silent killer." Our job as doctors is to find it BEFORE it causes a stroke, heart attack, or kidney failure — not after.'))
professor_says('Hypertension is not a disease you "feel" — it is a disease you "measure." A patient can have a blood pressure of 200/120 and feel perfectly well while their brain, heart, and kidneys are being silently damaged every single day. This is exactly why every single patient who walks into your clinic — for ANY reason — should have their blood pressure checked.', story)
memory_hook('THE SILENT KILLER: No symptoms + slow organ damage + measurable on a simple cuff = the perfect argument for screening every adult who visits a clinic, regardless of why they came.', story)
divider(story)

# §2 Definition, Classification & Diagnosis
sec_header('Section 2: Definition, Classification and How We Diagnose It', story)
professor_says('Before treating anything, you must be able to DEFINE it and DIAGNOSE it correctly. Get this wrong, and you either over-treat a healthy person or under-treat a sick one. Both are dangerous.', story)

story.append(bp('<b>Definition:</b> Hypertension (HTN) means persistently raised arterial blood pressure — high enough, for long enough, that it raises the risk of stroke, heart attack, kidney failure, and early death. "Persistent" is the key word — one high reading in a stressed patient does NOT mean hypertension.'))
story.append(Spacer(1, 4))

qa_block(
    'Imagine a patient comes to clinic, sits down, and you measure their BP as 162/96 mmHg. You write "hypertension" in the notes and start a tablet immediately.',
    'Is this the correct way to diagnose hypertension? Why or why not?',
    'Think about "white coat syndrome" — does everyone\'s blood pressure behave the same in a clinic as it does at home?',
    'NO — this is incorrect. A single clinic reading is not enough. Many people have "white coat hypertension" — their BP rises simply because they are anxious in a clinical setting. The correct approach: if clinic BP is >= 140/90, you must CONFIRM the diagnosis with Ambulatory Blood Pressure Monitoring (ABPM) — a device worn for 24 hours that measures BP every 30 minutes — OR Home Blood Pressure Monitoring (HBPM) over at least 4-7 days (morning and evening, two readings each time, discard day 1). Only a confirmed AVERAGE reading establishes the diagnosis.',
    story)

story.append(img_classification)
story.append(bp('Blood pressure categories — NICE/ESC 2023 thresholds for clinic vs home/ambulatory readings', sImg))
story.append(Spacer(1, 6))

story.append(bp('<b>How the diagnosis pathway works in practice:</b>'))
for pt in [
    '<b>Step 1:</b> Measure clinic BP. If >= 140/90 mmHg, repeat in the other arm (use the higher reading — this also screens for subclavian artery disease).',
    '<b>Step 2:</b> If clinic BP is between 140/90 and 180/120, offer ABPM (preferred) or HBPM to confirm before labelling someone "hypertensive."',
    '<b>Step 3:</b> If clinic BP >= 180/120, look immediately for signs of organ damage (this changes everything — see Section 10 on emergencies).',
    '<b>Step 4:</b> Once confirmed (by ABPM/HBPM average), formally diagnose, stage the severity, and assess overall cardiovascular risk (e.g., QRISK score) before deciding on treatment.',
]:
    story.append(bp(f'  • {pt}'))
info_box('<b>Why does staging matter?</b> Staging is not just an academic label — it decides URGENCY. Stage 1 in a low-risk young patient may only need lifestyle change. Stage 2 in anyone needs drug treatment. Severe hypertension (>= 180/120) needs same-day assessment for organ damage. This single number changes your entire plan.', story)
memory_hook('DIAGNOSIS RULE: Clinic BP >= 140/90 -> CONFIRM with ABPM or HBPM (never diagnose on one reading) -> THEN stage severity -> THEN decide treatment urgency. "Measure twice, treat once."', story)
divider(story)

# §3 Physiology
sec_header('Section 3: Physiology — How the Body Normally Controls Blood Pressure', story)
professor_says('You cannot understand what goes WRONG in hypertension until you understand what goes RIGHT in a healthy person. Every drug we use targets one of these normal control systems. Learn this section perfectly — it is the foundation for everything that follows.', story)

story.append(img_physiology)
story.append(bp('The master equation and the four systems that regulate blood pressure', sImg))
story.append(Spacer(1, 6))

story.append(bp('<b>The Master Equation — memorise this first:</b>'))
story.append(bp('<b>BLOOD PRESSURE = CARDIAC OUTPUT (CO) x SYSTEMIC VASCULAR RESISTANCE (SVR)</b>'))
story.append(bp('Cardiac output is how much blood the heart pumps per minute (Heart Rate x Stroke Volume). Systemic vascular resistance is how tightly the small arteries (arterioles) are squeezed. If EITHER goes up — and stays up — blood pressure rises. Every single antihypertensive drug works by reducing one of these two things.'))
story.append(Spacer(1, 5))

qa_block(
    'A patient asks you: "Doctor, my heart feels fine, it is not racing — so why is my blood pressure high?"',
    'How would you explain this to the patient using the master equation?',
    'Remember — blood pressure has TWO halves to the equation. If the pump (heart) is normal, what is the other half doing?',
    'You would say: "Your heart is indeed pumping normally — that is the CARDIAC OUTPUT half of the equation. But the SECOND half — the tightness of your blood vessels (systemic vascular resistance) — has increased. Imagine squeezing a garden hose: the same amount of water now creates much higher pressure inside the hose. Your arteries have become \'squeezed,\' usually because of an overactive RAAS system or stiffened vessel walls — and that is what is raising your pressure, not your heart rate."',
    story)

story.append(bp('<b>The Four Regulatory Systems — know each one (these are your drug targets later):</b>'))
phys_table = [
    ['System','How It Works','Effect on BP','Drug That Targets It'],
    ['RAAS\n(Renin-Angiotensin-\nAldosterone System)','Kidney releases renin when it senses low\nblood flow -> renin converts angiotensinogen\nto Angiotensin I -> ACE (in the lungs) converts\nit to Angiotensin II -> vasoconstriction +\naldosterone release (keeps salt and water).','RAISES BP via\nvasoconstriction\n+ salt/water\nretention.','ACE inhibitors,\nARBs (angiotensin\nreceptor blockers),\nspironolactone\n(aldosterone blocker).'],
    ['Sympathetic\nNervous System','"Fight or flight" response. Releases\nadrenaline and noradrenaline. Increases\nheart rate, contractility, AND squeezes\nblood vessels (alpha-1 receptors).','RAISES BP via\nfaster heart +\nvasoconstriction.','Beta-blockers,\nalpha-blockers\n(e.g., doxazosin).'],
    ['Renal salt and\nwater handling','Kidneys decide how much sodium and\nwater to keep or excrete. More salt kept ->\nmore water retained (osmosis) -> more\nblood volume -> higher pressure.','RAISES BP when\ntoo much salt\nand water kept.','Thiazide-like\ndiuretics (e.g.,\nindapamide, bendro-\nflumethiazide).'],
    ['Baroreceptor\nreflex','Pressure-sensors in the carotid sinus and\naortic arch detect BP changes second-by-\nsecond, send signals to the brainstem,\nwhich adjusts heart rate and vessel tone.','FAST, MOMENT-\nTO-MOMENT\ncorrection of BP.','Not directly drugged\n— but explains\npostural hypotension\nas a drug side effect.'],
]
story.append(plain_table(phys_table,[CW*0.18, CW*0.34, CW*0.2, CW*0.28]))
info_box('<b>Why this matters clinically:</b> Every antihypertensive drug class exists because it blocks ONE of these four systems. If you know the system, you already know the drug class, its main side effect, and often the patient group it suits best. This is the single most efficient way to learn hypertension pharmacology — work backwards from physiology to drugs, never memorise drug lists in isolation.', story)
memory_hook('FOUR SYSTEMS THAT RAISE BP: RAAS (renin -> angiotensin -> aldosterone), Sympathetic nervous system (adrenaline), Kidneys (salt and water retention), and the fast-acting Baroreceptor reflex. Each has a matching drug class — learn them as PAIRS, not separately.', story)
divider(story)

# §4 Pathophysiology
sec_header('Section 4: Pathophysiology — How and Why Hypertension Develops', story)
professor_says('In about 90-95% of patients, we never find a single "cause" — we call this primary (essential) hypertension. It develops from a combination of genetics, age, lifestyle, and slow vessel changes. Understanding these mechanisms explains why lifestyle changes genuinely work, and why the disease gets worse with age if untreated.', story)

story.append(bp('<b>Primary (Essential) Hypertension — the 90-95% majority — key mechanisms:</b>'))
for pt in [
    '<b>Genetic predisposition:</b> Family history strongly increases risk. Multiple genes affect how the kidneys handle salt and how blood vessels respond to hormones.',
    '<b>Age-related arterial stiffening:</b> Over decades, the elastic walls of large arteries (aorta, carotids) become stiffer (less elastin, more collagen). Stiff pipes transmit pressure more directly — this mainly raises SYSTOLIC pressure in the elderly (isolated systolic hypertension).',
    '<b>Endothelial dysfunction:</b> The endothelium (the inner lining of blood vessels) normally releases nitric oxide (NO) — a powerful natural vasodilator. In hypertension, this lining becomes "sick" and produces less NO, so vessels stay more constricted.',
    '<b>Increased sympathetic tone:</b> Chronic stress, obesity, and poor sleep (e.g., obstructive sleep apnoea) keep the sympathetic nervous system switched on for too long, raising both heart rate and vessel tone persistently.',
    '<b>Salt sensitivity:</b> Some people\'s kidneys are genetically less efficient at excreting sodium. Extra salt -> extra water retained (osmosis) -> higher blood volume -> higher pressure. This is why a low-salt diet helps some patients dramatically and others very little.',
    '<b>RAAS overactivity:</b> In some patients the renin-angiotensin-aldosterone system stays switched on inappropriately, driving chronic vasoconstriction and salt retention.',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 5))

qa_block(
    'You see two patients with the exact same blood pressure reading: 158/96 mmHg. One is 28 years old and very fit. The other is 74 years old.',
    'Which one is more likely to have "essential" (primary) hypertension with no findable cause, and which one should make you suspect a SECONDARY cause that needs to be investigated?',
    'Essential hypertension typically develops gradually with age. A high BP in someone YOUNG and otherwise healthy is statistically unusual — what does that suggest?',
    'The 74-year-old fits the typical pattern of primary (essential) hypertension — gradual arterial stiffening and age-related changes are extremely common at this age, and no specific cause is usually found. The 28-year-old, however, is UNUSUAL — young age with significant hypertension should make you actively search for a SECONDARY cause (kidney disease, endocrine tumour, coarctation of the aorta, or drugs). This is a classic exam principle: "Young + hypertensive = look harder for a cause."',
    story)
memory_hook('PRIMARY HTN MECHANISM CHAIN: Genes + age -> stiff vessels + sick endothelium (less nitric oxide) + salt-sensitive kidneys + overactive sympathetic/RAAS systems -> chronically squeezed arteries -> persistently raised BP. "Young hypertensive patient" = always hunt for a secondary cause.', story)
divider(story)

# §5 Causes — Secondary Hypertension
sec_header('Section 5: Causes of Secondary Hypertension — The 5-10% You Must Not Miss', story)
professor_says('Secondary hypertension is rare but CURABLE — find the cause, fix it, and the patient may need no tablets at all for the rest of their life. This is one of the most rewarding diagnoses in medicine, and one of the most heavily examined topics in MRCP. Learn this table as if a patient\'s cure depends on you remembering it — because it does.', story)

sec_table = [
    ['Category','Specific Cause','Clue That Points To It','Confirmatory Test'],
    ['RENAL\n(most common\nsecondary cause)','Renal artery stenosis\n(atherosclerosis or\nfibromuscular dysplasia)\nChronic kidney disease\nPolycystic kidney disease','Abdominal bruit (whooshing\nsound over the renal arteries).\nSudden worsening of BP control.\nBig rise in creatinine after\nstarting an ACE inhibitor.','Renal artery Doppler\nultrasound or CT/MR\nangiography.\nU&Es, eGFR, renal\nultrasound.'],
    ['ENDOCRINE:\nConn\'s syndrome\n(primary\nhyperaldosteronism)','Adrenal adenoma or\nbilateral hyperplasia\nover-secreting aldosterone.','Hypertension PLUS\nunexplained LOW potassium\n(muscle weakness, cramps)\nPLUS mild metabolic alkalosis.','Aldosterone:renin ratio\n(raised aldosterone,\nsuppressed renin).\nAdrenal CT.'],
    ['ENDOCRINE:\nPhaeochromocytoma','Catecholamine-secreting\ntumour of the adrenal\nmedulla (or extra-adrenal\nparaganglioma).','CLASSIC TRIAD: episodic\nheadache + sweating +\npalpitations, with BP\nspikes ("paroxysmal" pattern).','24-hour urinary\nmetanephrines /\nplasma free metanephrines.\nCT/MRI adrenal imaging.'],
    ['ENDOCRINE:\nCushing\'s syndrome','Excess cortisol — from a\npituitary tumour, adrenal\ntumour, or long-term steroid use.','Central obesity, moon face,\nbuffalo hump, purple striae,\nproximal muscle weakness,\neasy bruising, thin skin.','Overnight dexamethasone\nsuppression test.\n24-hour urinary free cortisol.'],
    ['ENDOCRINE:\nThyroid disease','Both hyper- and\nhypothyroidism can\nraise blood pressure.','Hyperthyroid: weight loss,\ntremor, heat intolerance.\nHypothyroid: weight gain,\ncold intolerance, slow pulse.','TSH, free T4.'],
    ['VASCULAR:\nCoarctation of\nthe aorta','Congenital narrowing\nof the aorta, usually\njust after the left\nsubclavian artery.','Hypertension in the ARMS\nbut LOW BP in the legs.\nRadio-femoral delay on\npalpation. Murmur. Usually\nfound in young patients.','Echocardiogram.\nCT/MR aortography.\nCXR: "rib notching"\n(collateral vessels).'],
    ['DRUG-INDUCED','NSAIDs, combined oral\ncontraceptive pill,\ncorticosteroids, ciclosporin,\nliquorice (glycyrrhizic acid),\ncocaine, decongestants\n(pseudoephedrine).','Always take a careful\ndrug and recreational\nsubstance history — this\nis the cheapest "test"\nyou can ever do.','Drug history +\nstopping the drug\nand re-checking BP.'],
    ['OBSTRUCTIVE\nSLEEP APNOEA\n(OSA)','Repeated airway collapse\nduring sleep -> intermittent\nhypoxia -> sympathetic\nsurges -> sustained hypertension.','Loud snoring, witnessed\napnoeas, daytime sleepiness,\nobesity, morning headaches,\nresistant hypertension.','Sleep study\n(polysomnography).\nEpworth Sleepiness Scale.'],
    ['PREGNANCY','Pre-eclampsia — new\nhypertension after 20 weeks\ngestation with proteinuria\nor organ dysfunction.','Headache, visual disturbance,\nepigastric pain, oedema,\nbrisk reflexes, in a pregnant\nwoman after 20 weeks.','Urine protein:creatinine\nratio, placental growth\nfactor (PlGF), liver and\nkidney function tests.'],
]
story.append(plain_table(sec_table,[CW*0.16, CW*0.24, CW*0.3, CW*0.3]))
story.append(Spacer(1, 4))

qa_block(
    'A 34-year-old woman is found to have a blood pressure of 172/108 mmHg. Her blood test shows a potassium level of 2.9 mmol/L (normal is roughly 3.5-5.0). She also mentions occasional muscle cramps and weakness.',
    'What is the SINGLE most likely secondary cause, and what test would you order first to confirm it?',
    'The combination to focus on is: HYPERTENSION + LOW POTASSIUM. Which hormone, when secreted in excess, causes the kidney to retain sodium (raising BP) while "dumping" potassium (causing low potassium)?',
    'This is classic for CONN\'S SYNDROME (primary hyperaldosteronism). Excess aldosterone makes the kidney reabsorb sodium and water (raising BP) while excreting potassium (causing hypokalaemia — hence the cramps and weakness). The first confirmatory test is the PLASMA ALDOSTERONE-TO-RENIN RATIO — a high aldosterone with a suppressed (low) renin confirms the diagnosis. An adrenal CT scan then localises the tumour or hyperplasia.',
    story)

alert_box('THE TWO MOST DANGEROUS THINGS TO MISS: (1) Phaeochromocytoma — giving a beta-blocker FIRST in an undiagnosed phaeochromocytoma can cause a fatal hypertensive crisis (unopposed alpha-stimulation). ALWAYS give an alpha-blocker first. (2) Coarctation of the aorta in a young hypertensive patient — always feel for radio-femoral delay and check four-limb blood pressures.', story)
memory_hook('SECONDARY HTN — "CHAPS" memory hook: Coarctation, Hyperaldosteronism (Conn\'s)/Hypercortisolism (Cushing\'s), Apnoea (OSA) and Adrenal tumours (phaeo), Parenchymal renal disease/renal artery stenosis, Steroids/drugs/pregnancy. Young + resistant + odd electrolytes = always go hunting.', story)
divider(story)
print('Part 1 complete:', len(story), 'flowables')

# §6 Clinical Features
sec_header('Section 6: Clinical Features — History, Examination and End-Organ Damage', story)
professor_says('Remember the golden rule from Section 1: hypertension is usually SILENT. So when you DO find symptoms, they almost always mean one of two things — either the pressure is dangerously high RIGHT NOW (an emergency), or organ damage has already begun. Learn to read these signs as alarm bells, not coincidences.', story)

story.append(bp('<b>Why most patients have NO symptoms (the usual presentation):</b>'))
story.append(bp('The vast majority of hypertensive patients are diagnosed incidentally — at a routine check-up, before surgery, during pregnancy booking, or at a pharmacy blood pressure machine. This is precisely why opportunistic screening (checking BP whenever a patient attends for ANY reason) is so important — and so heavily emphasised in MRCP and PACES.'))
story.append(Spacer(1, 4))

qa_block(
    'A patient says: "Doctor, I get headaches sometimes — could that be from my high blood pressure?"',
    'Is a typical, mild, intermittent headache a reliable symptom of chronic hypertension? What headache pattern SHOULD worry you?',
    'Think about the difference between "chronic, slowly progressive" disease and "acute, dangerously high" disease. Which one causes dramatic symptoms?',
    'In chronic, stable hypertension, headache is NOT a reliable or specific symptom — most "hypertension headaches" patients describe are actually tension headaches occurring coincidentally. However, a SEVERE, sudden, "worst-ever" headache, especially with visual disturbance, vomiting, or confusion, in a patient with very high BP (>= 180/120), is a RED FLAG for a hypertensive emergency (e.g., hypertensive encephalopathy or intracranial bleed) — not a "normal" hypertension symptom. Context and severity change everything.',
    story)

story.append(img_organdamage)
story.append(bp('Target organ damage map — what silent hypertension eventually destroys, organ by organ', sImg))
story.append(Spacer(1, 6))

exam_table = [
    ['What You Examine','Sign To Look For','What It Tells You','Why It Matters'],
    ['Both arms — BP\nin each arm','Difference > 15 mmHg\nbetween arms.','Possible subclavian artery\nstenosis or aortic disease.','Always measure both arms at\nfirst visit; use the higher reading\nfor all future decisions.'],
    ['Radial and\nfemoral pulses\ntogether','Radio-femoral delay\n(femoral pulse arrives\nnoticeably later).','Coarctation of the aorta\n— classic in young patients.','Simple bedside test that can\ndiagnose a curable cause in seconds.'],
    ['Fundoscopy\n(ophthalmoscope)','Hypertensive retinopathy:\nGrade I (silver wiring),\nGrade II (AV nipping),\nGrade III (haemorrhages,\ncotton-wool spots),\nGrade IV (papilloedema).','Direct visualisation of\nblood vessel damage —\nthe retina is a "window"\ninto the brain\'s vessels.','Grade III/IV = malignant\n(accelerated) hypertension =\nadmit immediately.'],
    ['Cardiovascular\nexamination','Heaving or displaced apex\nbeat, fourth heart sound (S4),\nsigns of heart failure\n(bibasal crackles, raised JVP,\nperipheral oedema).','Left ventricular hypertrophy\n(LVH) — the heart muscle\nthickens from years of\npumping against high resistance.','LVH is an independent\npredictor of heart attack,\nstroke, and arrhythmia\n(especially atrial fibrillation).'],
    ['Abdominal\nexamination','Renal artery bruit\n(whooshing sound on\nauscultation over the\nupper abdomen/flanks).\nPalpable kidneys\n(polycystic kidneys).','Renal artery stenosis or\nstructural kidney disease\nas a secondary cause.','A bruit found on a routine\nabdominal exam can lead\ndirectly to a curable diagnosis.'],
    ['Neurological\nexamination','Focal weakness, visual\nfield loss, confusion,\ndysarthria.','Stroke or TIA — a\ndirect complication of\nlong-standing hypertension.','New focal neurology +\nvery high BP = call for\nemergency stroke assessment.'],
]
story.append(plain_table(exam_table,[CW*0.18, CW*0.24, CW*0.27, CW*0.31]))
alert_box('FUNDOSCOPY IS NOT OPTIONAL: Grade III (flame haemorrhages, cotton-wool spots) or Grade IV (papilloedema — swollen optic disc) retinopathy means MALIGNANT (ACCELERATED) HYPERTENSION. This patient needs SAME-DAY hospital admission, regardless of how well they say they feel. The eye is showing you what is happening inside the brain.', story)
memory_hook('EXAM CHECKLIST FOR EVERY HYPERTENSIVE PATIENT: Both arms\' BP + radio-femoral pulses + fundoscopy + heart (apex beat, S4, failure signs) + abdomen (bruit, kidneys) + neuro exam. Each one can reveal either a CURABLE secondary cause or DANGEROUS organ damage — never skip any of them.', story)
divider(story)

# §7 Investigations
sec_header('Section 7: Investigations — Confirming Diagnosis, Finding Damage, Hunting Causes', story)
professor_says('Investigations in hypertension serve THREE separate purposes — confirm the diagnosis, look for organ damage that has already happened, and screen for a treatable secondary cause. Keep these three goals separate in your mind; it will completely change how you read an exam question.', story)

invx_table = [
    ['Investigation','Purpose','What You Are Looking For','MRCP Key Point'],
    ['ABPM (Ambulatory\nBlood Pressure\nMonitoring)','CONFIRM diagnosis\n(avoid white-coat effect).','Average BP over 24h, with\n>= 14 readings during waking\nhours, taken every 30-60 min.','NICE-preferred confirmation\nmethod. Daytime average\n>= 135/85 = confirmed HTN.'],
    ['HBPM (Home Blood\nPressure Monitoring)','Alternative to ABPM if not\ntolerated or unavailable.','Two readings, 1 minute apart,\nseated, morning and evening,\nfor at least 4-7 days (discard day 1).','Average of all readings\n(excluding day 1)\n>= 135/85 = confirmed HTN.'],
    ['Urea & Electrolytes\n(U&Es), eGFR','Baseline kidney function +\nbaseline potassium\n(important before starting drugs).','Raised creatinine/low eGFR\n= renal damage or renal cause.\nLow potassium = think Conn\'s.\nHigh potassium = caution\nwith ACE-i/ARB/spironolactone.','MUST be done BEFORE\nstarting an ACE inhibitor\nor ARB, then re-checked\n1-2 weeks after starting.'],
    ['Urine albumin:\ncreatinine ratio (ACR)\n+ urine dipstick','Detect early kidney\ndamage (microalbuminuria)\nbefore creatinine even rises.','ACR > 3 mg/mmol =\nclinically significant\nproteinuria — early\nsign of kidney damage.','Often the EARLIEST detectable\nsign of hypertensive kidney\ndamage — found before any\nsymptoms appear.'],
    ['HbA1c / fasting\nglucose, lipid profile','Assess overall\ncardiovascular risk\n(diabetes and cholesterol\noften coexist with HTN).','Raised glucose or\ncholesterol increases\noverall cardiovascular risk\nand changes treatment targets.','Used to calculate\nQRISK score — guides whether\nstatins are also needed.'],
    ['12-lead ECG','Look for left ventricular\nhypertrophy (LVH),\nischaemia, arrhythmia\n(especially AF).','Voltage criteria for LVH\n(e.g., Sokolow-Lyon criteria),\nST/T wave changes ("strain\npattern"), atrial fibrillation.','LVH on ECG = years of\nuncontrolled hypertension =\nindependent risk factor for\nsudden cardiac death.'],
    ['Echocardiogram\n(if LVH suspected\nor heart failure signs)','More sensitive than ECG\nfor structural heart changes.','LVH, diastolic dysfunction,\nvalve disease, ejection fraction.','Confirms and quantifies\ncardiac damage; guides\nheart failure management\nif found.'],
    ['Fundoscopy','Direct visualisation of\nretinal blood vessels.','Hypertensive retinopathy\ngrading I-IV (see Section 6).','Grade III/IV = admit\nas malignant hypertension.'],
    ['Specific tests for\nsecondary causes\n(only if suspected)','Targeted hunting based\non history/exam clues —\nNOT routine for everyone.','Aldosterone:renin ratio (Conn\'s),\n24h urinary metanephrines (phaeo),\ndexamethasone suppression test\n(Cushing\'s), renal artery Doppler,\nsleep study (OSA), TSH (thyroid).','Only test for secondary\ncauses if the history/exam\ngives you a CLUE — do not\nscreen everyone for everything.'],
]
story.append(plain_table(invx_table,[CW*0.2, CW*0.2, CW*0.28, CW*0.32]))
story.append(Spacer(1, 4))

qa_block(
    'You are about to start a patient on an ACE inhibitor (e.g., ramipril) for newly diagnosed hypertension.',
    'What TWO blood results must you check BEFORE starting the drug, and what must you check again 1-2 weeks AFTER starting it — and why?',
    'ACE inhibitors affect the kidney\'s filtering pressure and can cause potassium to rise. What two values reflect exactly these two things?',
    'You must check U&Es (urea and electrolytes) and eGFR (kidney function) BEFORE starting — this gives you a baseline. Then re-check POTASSIUM and CREATININE/eGFR again 1-2 weeks after starting. ACE inhibitors reduce the pressure inside the glomerulus (by blocking angiotensin II\'s constricting effect on the efferent arteriole), which can cause creatinine to rise — a small rise (up to 30%) is acceptable, but a LARGE rise suggests bilateral renal artery stenosis and the drug must be stopped. ACE inhibitors also raise potassium (by reducing aldosterone) — dangerous hyperkalaemia can develop, especially if combined with spironolactone or in patients with kidney disease.',
    story)
memory_hook('THREE GOALS OF INVESTIGATION: (1) CONFIRM — ABPM/HBPM. (2) ASSESS DAMAGE ALREADY DONE — U&Es/ACR (kidney), ECG/echo (heart), fundoscopy (eyes). (3) HUNT FOR A CURABLE CAUSE — only if history/exam gives a clue (low K+ -> Conn\'s, episodic symptoms -> phaeo, snoring -> OSA). Always check U&Es and potassium before AND after starting an ACE inhibitor or ARB.', story)
divider(story)

# §8 Outpatient / Chronic Management
sec_header('Section 8: Outpatient (Chronic) Management — Lifestyle and the Stepwise Drug Ladder', story)
professor_says('This is the heart of day-to-day hypertension practice — what you will do in clinic, week after week, for the rest of your career. Two pillars: LIFESTYLE (always, for everyone) and DRUGS (the stepwise A-C-D ladder). Know both, and know exactly when to step up.', story)

story.append(bp('<b>Pillar 1 — Lifestyle measures (offer to EVERY patient, regardless of whether drugs are also started):</b>'))
for pt in [
    '<b>Reduce dietary salt:</b> Aim for less than 6g/day (about one teaspoon). This is one of the single most effective non-drug interventions, especially in salt-sensitive patients.',
    '<b>Reduce alcohol intake:</b> Excess alcohol both raises BP directly and reduces the effectiveness of antihypertensive drugs.',
    '<b>Increase physical activity:</b> Regular aerobic exercise (e.g., brisk walking 30 minutes most days) lowers BP and improves overall cardiovascular risk.',
    '<b>Weight loss:</b> Even a modest weight loss (5-10% of body weight) produces measurable reductions in blood pressure.',
    '<b>Reduce caffeine:</b> Excess caffeine can cause transient BP spikes — moderate intake is reasonable.',
    '<b>Stop smoking:</b> Smoking does not directly cause sustained hypertension, but dramatically multiplies overall cardiovascular risk — essential advice regardless.',
    '<b>Relaxation and stress reduction:</b> Chronic stress keeps the sympathetic nervous system switched on; techniques such as mindfulness can help some patients.',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 6))

story.append(bp('<b>Pillar 2 — The NICE Stepwise Drug Ladder (the famous "A-C-D rule"):</b>'))
story.append(img_ladder)
story.append(bp('NICE stepwise treatment algorithm for hypertension — the A-C-D rule, step by step', sImg))
story.append(Spacer(1, 6))

qa_block(
    'A 60-year-old Black African-Caribbean man and a 38-year-old White British woman are both newly diagnosed with hypertension and need to start their first tablet.',
    'According to the NICE A-C-D rule, which FIRST-LINE drug class should each of them start on, and why does ethnicity matter here?',
    'The rule splits patients by AGE (above or below 55) AND by ethnicity (Black African or African-Caribbean origin, of any age). Which group tends to have lower-renin physiology, making ACE inhibitors/ARBs less effective as monotherapy?',
    'The 60-year-old Black African-Caribbean man should start on a CALCIUM CHANNEL BLOCKER ("C", e.g., amlodipine) — both because he is over 55 AND because of his ethnicity. The 38-year-old White British woman, being under 55 and not of Black African/Caribbean origin, should start on an ACE INHIBITOR or ARB ("A", e.g., ramipril or losartan). The reason: Black African-Caribbean patients, on average, tend to have lower circulating renin levels, so drugs that block the RAAS pathway (ACE-i/ARB) are statistically less effective as a FIRST single agent in this group — calcium channel blockers work more reliably as monotherapy. (Note: this guidance applies to first-line CHOICE only — by Step 2, most patients end up on a combination anyway.)',
    story)

story.append(bp('<b>BP targets (know these — they are frequently tested):</b>'))
target_table = [
    ['Patient Group','Clinic BP Target','ABPM/HBPM Target'],
    ['Age under 80 years','< 140/90 mmHg','< 135/85 mmHg'],
    ['Age 80 years and over','< 150/90 mmHg','< 145/85 mmHg'],
    ['Type 1 or Type 2 diabetes\n(with kidney, eye, or\ncerebrovascular disease)','< 130/80 mmHg','Lower targets — individualised\nwith specialist input'],
    ['Pregnancy','< 135/85 mmHg\n(treat early — labetalol first-line)','Specialist obstetric monitoring'],
]
story.append(plain_table(target_table,[CW*0.32, CW*0.34, CW*0.34]))
info_box('<b>When to step up the ladder:</b> If BP remains above target on the current step (after allowing the drug to take full effect, usually 4 weeks), check ADHERENCE first (ask directly — "Are you able to take your tablets every day?"), check INHALER/TABLET technique and side effects, THEN add the next drug in the sequence. Never simply swap drugs randomly — follow the ladder logically.', story)
memory_hook('A-C-D LADDER: Step 1 = A (under 55, not Black African/Caribbean) or C (55+, or Black African/Caribbean any age). Step 2 = A+C. Step 3 = A+C+D. Step 4 (resistant) = add spironolactone if K+ <= 4.5, or alpha-/beta-blocker if K+ > 4.5. TARGET: < 140/90 (under 80), < 150/90 (80+), < 130/80 (diabetes + organ disease).', story)
divider(story)

# §9 Pharmacology
sec_header('Section 9: Pharmacology of Antihypertensive Drugs — Mechanism, Side Effects, Prescribing', story)
professor_says('Notice how every drug class here maps directly back to the four regulatory systems from Section 3. If you understand the physiology, the pharmacology becomes simple logic rather than rote memorisation. This is "Teach Me From Zero" in action — building new knowledge on a foundation you already have.', story)

pharm_table = [
    ['Drug Class\n(examples)','Mechanism','Key Side Effects','MRCP Prescribing Points\n(Ganesh & Kuruvilla)'],
    ['ACE INHIBITORS\n(ramipril, lisinopril,\nperindopril)\n— the "A"','Block Angiotensin-Converting\nEnzyme -> less Angiotensin II ->\nless vasoconstriction + less\naldosterone (less salt retention).','DRY COUGH (bradykinin\nbuild-up — very common,\nclassic exam answer).\nAngioedema (rare but\ndangerous). Hyperkalaemia.\nFirst-dose hypotension.','Check U&Es/K+ before and\n1-2 weeks after starting.\nA rise in creatinine up to\n30% is acceptable. AVOID\nin pregnancy (teratogenic)\nand bilateral renal artery stenosis.'],
    ['ARBs — Angiotensin\nReceptor Blockers\n(losartan, candesartan,\nvalsartan)\n— alternative "A"','Block the angiotensin II\nreceptor (AT1) directly —\nsame downstream effect as\nACE-i but no bradykinin build-up.','Similar to ACE-i but\nNO COUGH (key exam\ndifference). Hyperkalaemia.\nHypotension.','First choice if a patient\ndevelops a dry cough on an\nACE inhibitor. Same monitoring\nrules and pregnancy avoidance\nas ACE inhibitors.'],
    ['CALCIUM CHANNEL\nBLOCKERS\n(amlodipine, nifedipine\n— dihydropyridines;\ndiltiazem, verapamil\n— rate-limiting)\n— the "C"','Block L-type calcium\nchannels in vascular smooth\nmuscle (and in the heart for\nrate-limiting types) ->\nvasodilation +/- reduced heart rate.','Ankle/peripheral oedema\n(very common — fluid shifts\nout of capillaries, not\ntrue fluid overload).\nFlushing, headache,\ngum hypertrophy.','Ankle swelling does NOT\nrespond to diuretics (it is\nnot fluid overload) — may\nneed to switch class or add\nan ACE-i/ARB which can reduce it.\nAVOID verapamil + beta-blocker\ncombination (risk of heart block).'],
    ['THIAZIDE-LIKE\nDIURETICS\n(indapamide,\nchlortalidone)\n— the "D"','Block sodium reabsorption\nin the distal convoluted\ntubule of the kidney ->\nmore sodium and water excreted\n-> reduced blood volume.','Hyponatraemia, hypokalaemia,\nhypercalcaemia, hyperuricaemia\n(can trigger gout), erectile\ndysfunction, postural hypotension.','Indapamide and chlortalidone\n(thiazide-LIKE) preferred over\nold-style bendroflumethiazide\n(thiazide). Check electrolytes\nperiodically. Caution in gout.'],
    ['BETA-BLOCKERS\n(bisoprolol, atenolol,\nlabetalol)\n— 4th-line generally,\nbut important exceptions','Block beta-1 adrenoceptors\nin the heart -> reduced heart\nrate and contractility ->\nreduced cardiac output.','Bradycardia, fatigue,\ncold extremities,\nbronchospasm (avoid in\nasthma — beta-2 effect),\nmasking of hypoglycaemia\nin diabetics, erectile dysfunction.','NOT first-line for\nuncomplicated hypertension\n(per NICE) UNLESS there is\nALSO angina, post-MI, heart\nfailure, or in younger women\nof childbearing potential where\nACE-i/ARB are contraindicated.'],
    ['ALPHA-BLOCKERS\n(doxazosin)\n— Step 4 option','Block alpha-1 adrenoceptors\nin vascular smooth muscle ->\nvasodilation.','Postural (orthostatic)\nhypotension — falls risk\nin elderly, especially with\nfirst dose. Dizziness, syncope.','Give first dose at bedtime\n(reduce first-dose hypotension\nrisk). Useful add-on in resistant\nhypertension, especially with\ncoexisting prostatic symptoms (BPH).'],
    ['SPIRONOLACTONE\n(aldosterone\nantagonist)\n— Step 4 first choice\nif K+ <= 4.5','Blocks the aldosterone\nreceptor in the distal\nnephron -> less sodium/water\nretention, less potassium loss\n(potassium-SPARING).','HYPERKALAEMIA (the major\nrisk — monitor closely).\nGynaecomastia and breast\ntenderness in men (less with\nselective eplerenone).','Excellent in RESISTANT\nhypertension (often reveals\nan underlying high-aldosterone\nstate). MUST monitor potassium\nclosely, especially if combined\nwith ACE-i/ARB.'],
]
story.append(plain_table(pharm_table,[CW*0.18, CW*0.22, CW*0.27, CW*0.33]))
info_box('<b>The "ACE-i cough vs ARB" question — a guaranteed exam favourite:</b> ACE inhibitors block the breakdown of bradykinin (a peptide that also causes cough and, rarely, angioedema), because ACE itself normally breaks bradykinin down. ARBs act further downstream — they block the angiotensin II receptor directly — and do NOT affect bradykinin levels. This is exactly why ARBs are the standard substitute when a patient develops a troublesome dry cough on an ACE inhibitor.', story)
memory_hook('DRUG CLASS QUICK-RECALL: ACE-i = dry cough + angioedema (bradykinin). ARB = same benefit, NO cough. CCB = ankle swelling (not fluid overload — diuretics will not help). Thiazide-like = low Na+/K+, high Ca2+/urate (can trigger gout). Beta-blocker = NOT first-line, reserved for compelling indications (angina, post-MI, HF, young women). Spironolactone = potassium-SPARING — watch for HYPERkalaemia + gynaecomastia.', story)
divider(story)

# §10 Hypertensive Emergencies
sec_header('Section 10: Hypertensive Emergencies and Urgencies — When High BP Becomes a Crisis', story)
professor_says('This is where hypertension stops being a "clinic problem" and becomes a "resuscitation room problem." The single most important skill here is distinguishing an EMERGENCY (organ damage happening NOW) from an URGENCY (very high number, but no acute damage) — because treating them the same way can kill the patient.', story)

qa_block(
    'Two patients both arrive at the emergency department with a blood pressure of 220/130 mmHg. Patient A feels completely well and has a normal examination. Patient B is confused, has blurred vision, and a headache that started suddenly two hours ago.',
    'Are these the same emergency? Should both be treated identically, with the same speed and the same drugs?',
    'The NUMBER is identical. What is different between the two patients — and which of the two findings actually defines an "emergency" in hypertension?',
            'NO — these are two completely different situations, despite the identical number. Patient A has a HYPERTENSIVE URGENCY — a very high BP with NO evidence of acute organ damage; this can be managed with ORAL medication and BP lowered gradually over 24-48 hours as an outpatient or short admission. Patient B has a HYPERTENSIVE EMERGENCY (this specific pattern is called hypertensive encephalopathy) — there IS evidence of acute organ damage (confusion, visual disturbance, sudden severe headache); this requires IMMEDIATE admission, IV medication, and controlled BP reduction in a monitored setting. The defining feature of an emergency is NOT the number — it is evidence of ACUTE ORGAN DAMAGE happening right now.',
    story)

emerg_table = [
    ['Feature','Hypertensive URGENCY','Hypertensive EMERGENCY'],
    ['Definition','Severely raised BP\n(usually >= 180/120) WITHOUT\nacute organ damage.','Severely raised BP\n(usually >= 180/120) WITH\nacute, ongoing organ damage.'],
    ['Examples of\npresentation','Patient feels well or has\nmild headache; found\nincidentally or at routine visit.','Hypertensive encephalopathy,\nacute stroke, acute coronary\nsyndrome, aortic dissection,\nacute pulmonary oedema,\neclampsia, acute kidney injury,\nmalignant hypertension with\nGrade III/IV retinopathy.'],
    ['Speed of\nBP reduction','GRADUAL — over\n24-48 hours, often\nwith oral medication.','CONTROLLED but urgent —\nIV medication in a monitored\n(HDU/ICU) setting, with\nstrict reduction limits\n(see below).'],
    ['Setting','Can often be managed\nas outpatient or short\nobservation admission.','MUST be admitted —\nHDU/ICU level monitoring,\narterial line for continuous\nBP monitoring.'],
    ['Why "speed"\nmatters so much','Lowering BP too fast in\neither situation can cause\nharm — but the emergency\nsetting needs careful balance\nbetween treating damage and\nnot causing new damage.','RAPID, uncontrolled lowering\ncan cause cerebral, cardiac,\nor renal HYPOPERFUSION —\nturning a hypertensive crisis\ninto a stroke or heart attack\nfrom UNDER-perfusion.'],
]
story.append(plain_table(emerg_table,[CW*0.18, CW*0.38, CW*0.44]))
alert_box('THE GOLDEN RULE OF EMERGENCY BP REDUCTION: Do NOT lower the blood pressure too fast. The brain, heart, and kidneys have "auto-regulated" to function at a high pressure for months or years — sudden normalisation can cause them to be UNDER-perfused, causing a stroke, MI, or kidney injury. Standard target: reduce mean arterial pressure by NO MORE than 25% within the first 1-2 hours, then gradually towards normal over the next 24-48 hours (exception: aortic dissection — reduce faster and more aggressively, and ischaemic stroke — usually do NOT lower BP acutely at all unless thrombolysis is planned).', story)

story.append(bp('<b>Emergency Treatment — Practical Approach (in hospital, monitored setting):</b>'))
emerg_mgmt = [
    ['Clinical Situation','First-Line IV Drug','Key Practical Notes'],
    ['Hypertensive\nencephalopathy /\nmalignant hypertension\n(general)','Labetalol IV infusion\n(alpha- and beta-blocker)\nor IV glyceryl trinitrate (GTN)','Continuous arterial BP monitoring.\nReduce MAP by no more than\n25% in the first hour. Reassess\nneurology continuously.'],
    ['Acute pulmonary\noedema (heart failure)\nwith very high BP','IV GTN (nitrate) +\nIV furosemide (loop diuretic)\n+ oxygen/CPAP as needed','Nitrate reduces preload AND\nafterload — directly helps\nboth the lungs and the\noverloaded heart.'],
    ['Aortic dissection','IV labetalol or\nIV esmolol (rapid-acting\nbeta-blocker) FIRST,\nthen vasodilator if needed','Lower heart rate AND BP\nFAST and AGGRESSIVELY (this is\nthe one exception to "go slow") —\ntarget systolic ~100-120 mmHg\nand HR ~60 within minutes —\nto reduce the shearing force\non the aortic wall.'],
    ['Eclampsia /\nsevere pre-eclampsia','IV labetalol, IV hydralazine,\nor oral nifedipine; IV\nmagnesium sulphate for\nseizure prophylaxis/treatment','Magnesium sulphate treats\nand prevents seizures\n(NOT primarily a BP drug —\ndo not confuse the two roles).\nDelivery of the baby is the\ndefinitive treatment.'],
    ['Phaeochromocytoma\ncrisis','IV phentolamine or\nphenoxybenzamine\n(ALPHA-blocker FIRST)','NEVER give a beta-blocker\nfirst — unopposed alpha-\nstimulation causes a\nfatal hypertensive surge.\nAlpha-block first, beta-block\nlater if needed.'],
]
story.append(plain_table(emerg_mgmt,[CW*0.22, CW*0.28, CW*0.5]))
memory_hook('EMERGENCY VS URGENCY: The NUMBER never defines an emergency — ORGAN DAMAGE does (encephalopathy, stroke, dissection, pulmonary oedema, eclampsia, AKI, Grade III/IV retinopathy). GOLDEN RULE: drop MAP by <= 25% in the first hour (except aortic dissection — go FAST and HARD, and ischaemic stroke — usually do NOT lower acutely). Phaeo crisis = ALPHA-blocker first, NEVER beta-blocker first.', story)
divider(story)

# §11 Special Situations
sec_header('Section 11: Hypertension in Special Situations', story)
professor_says('Real patients do not arrive as "textbook hypertension" — they arrive pregnant, elderly, diabetic, with kidney disease, or simply not responding to treatment. MRCP Part 2 and PACES are built around exactly these "what do you do differently here?" scenarios.', story)

special_table = [
    ['Special Situation','Key Differences','Management Principles','MRCP / PACES Key Points'],
    ['PREGNANCY','Pre-eclampsia = new\nhypertension + proteinuria\nafter 20 weeks. Risk of\neclampsia (seizures), HELLP\nsyndrome, growth restriction.','First-line: LABETALOL.\nAlternatives: nifedipine,\nmethyldopa. AVOID ACE-i,\nARBs (teratogenic — renal\nagenesis, oligohydramnios),\nand thiazides.','Magnesium sulphate prevents\nand treats eclamptic seizures\n(it is NOT an antihypertensive —\ndo not confuse its purpose).\nDelivery is the definitive cure.\nAspirin from 12 weeks reduces\npre-eclampsia risk in high-risk women.'],
    ['ELDERLY / FRAILTY','Isolated systolic hypertension\n(stiff aorta) common.\nHigher fall risk with\npostural hypotension.\nMultiple comorbidities\nand polypharmacy.','Higher BP target\n(< 150/90 if 80+).\nStart low, go slow with\ndoses. Always check for\npostural drop (lying and\nstanding BP).','"Treating the number, not\nthe patient" can cause falls\nand fractures — always weigh\nbenefit vs harm in frail elderly.\nReview medications regularly\n(deprescribing is sometimes correct).'],
    ['DIABETES\n(Type 1 or Type 2)','Hypertension accelerates\ndiabetic nephropathy and\nretinopathy. Both diseases\ndamage blood vessels —\nthe combination is much\nworse than either alone.','LOWER target: < 130/80\nif kidney, eye, or\ncerebrovascular disease present.\nACE-i/ARB preferred —\nadditional kidney-protective\neffect (reduce proteinuria).','ACE-i/ARB are first-line\nin diabetics REGARDLESS of\nage or ethnicity, because of\ntheir specific renal protective\nbenefit (reduce intra-glomerular\npressure) — overriding the usual A-C-D order.'],
    ['CHRONIC KIDNEY\nDISEASE (CKD)','Hypertension both CAUSES\nand RESULTS FROM CKD —\na dangerous two-way cycle.\nFluid overload contributes\nto high BP.','ACE-i/ARB first-line\n(slow progression of CKD,\nreduce proteinuria) — but\nmonitor potassium and\ncreatinine closely. Loop\ndiuretics if fluid-overloaded.','Small creatinine rises\n(up to 30%) after starting\nACE-i/ARB are EXPECTED and\nacceptable — do not stop the\ndrug for this alone. Large\nrises suggest renal artery stenosis.'],
    ['RESISTANT\nHYPERTENSION','BP remains above target\ndespite THREE drugs at\noptimal doses (including\na diuretic).','Confirm with ABPM/HBPM\n(exclude white-coat effect)\nfirst. Check ADHERENCE.\nThen add spironolactone\n(if K+ <= 4.5) per Step 4.','Always ask: "Are you actually\ntaking your tablets?" — true\nnon-adherence is a FAR more\ncommon cause of "resistant"\nhypertension than any rare\nsecondary cause. Screen for OSA.'],
]
story.append(plain_table(special_table,[CW*0.16, CW*0.25, CW*0.27, CW*0.32]))
memory_hook('SPECIAL SITUATIONS: Pregnancy = labetalol (NEVER ACE-i/ARB — teratogenic) + magnesium for seizures (not BP). Elderly = start low, go slow, watch for falls. Diabetes/CKD = ACE-i/ARB first regardless of age/ethnicity (renal protection) + lower target < 130/80. Resistant = check adherence FIRST, then add spironolactone.', story)
divider(story)
print('Part 2 complete:', len(story), 'flowables')

# §12 Complications
sec_header('Section 12: Complications of Long-Standing or Poorly Controlled Hypertension', story)
professor_says('Every complication in this section is a DIRECT consequence of the mechanisms you already learned in Sections 3 and 4 — chronically squeezed, stiffened, damaged blood vessels eventually fail wherever they are. If you understand WHY, you will never need to memorise this list — you will be able to predict it.', story)

comp_table = [
    ['Complication','How It Develops','How to Recognise','Why It Matters / Management Link'],
    ['STROKE\n(ischaemic or\nhaemorrhagic)','Chronic high pressure damages\nsmall penetrating arteries\n(causing small bleeds or\nlacunar infarcts) and\naccelerates atherosclerosis\nin large arteries (causing\nclots).','Sudden focal neurological\ndeficit — weakness, speech\ndisturbance, visual loss,\nfacial droop (use FAST:\nFace, Arm, Speech, Time).','The single largest cause\nof death and disability linked\nto hypertension. Each 10 mmHg\nreduction in systolic BP\nreduces stroke risk substantially\n— this is why control matters so much.'],
    ['ISCHAEMIC HEART\nDISEASE / HEART\nFAILURE','LVH from pumping against\nhigh resistance for years ->\nthickened, stiff heart muscle\n-> eventually cannot relax\n(diastolic dysfunction) or\ncannot pump (systolic failure).\nAlso accelerates coronary\natherosclerosis.','Exertional chest pain (angina),\nbreathlessness, ankle swelling,\northopnoea, raised JVP,\ndisplaced apex beat, S4 heart sound.','Long-term BP control\ndirectly reduces LVH and\nthe risk of heart failure and\nheart attacks — one of the\nclearest "treatment prevents\ndisease" stories in medicine.'],
    ['CHRONIC KIDNEY\nDISEASE','Persistent high pressure\ndamages the small vessels\nwithin the kidney\n(nephrosclerosis), reducing\nfiltration capacity over years.','Initially silent — found via\nrising creatinine/falling eGFR\nor proteinuria (raised ACR)\non screening blood/urine tests.','Hypertension and CKD\ndrive each other in a vicious\ncycle — controlling BP slows\nCKD progression; CKD makes\nBP harder to control.'],
    ['HYPERTENSIVE\nRETINOPATHY','Direct damage to small\nretinal blood vessels —\nprogressing through grades\nI to IV with worsening severity.','Grade I: silver wiring.\nGrade II: AV nipping.\nGrade III: flame haemorrhages,\ncotton-wool spots.\nGrade IV: papilloedema\n(disc swelling) — sight-threatening.','Grade III/IV signals\nMALIGNANT (accelerated)\nhypertension — a same-day\nemergency admission, NOT\na routine eye clinic referral.'],
    ['AORTIC ANEURYSM\nAND DISSECTION','Chronic high pressure\nweakens and stretches the\naortic wall (aneurysm) or\ntears its inner layer, allowing\nblood to split the wall apart\n(dissection).','Aneurysm: often silent,\nfound on imaging, or a\npulsatile abdominal mass.\nDissection: sudden, severe,\n"tearing" chest/back pain,\nunequal arm BP, new murmur\n(aortic regurgitation).','Dissection is a TRUE\nemergency requiring rapid,\naggressive BP and heart rate\nreduction (the one exception\nto the "go slow" rule — see\nSection 10) plus emergency\nsurgical assessment.'],
    ['PERIPHERAL ARTERY\nDISEASE','Accelerated atherosclerosis\nin the arteries of the legs\nreduces blood flow to the\nlimbs.','Intermittent claudication\n(cramping leg pain on walking,\nrelieved by rest), cold limbs,\nabsent pulses, poor wound healing.','A marker of WIDESPREAD\nvascular disease — a patient\nwith PAD very likely has\ncoronary and cerebrovascular\ndisease too; treat the whole\nvascular system, not just the legs.'],
    ['VASCULAR\nDEMENTIA','Repeated small strokes and\nchronic reduced blood flow\nto the brain over years cause\ncumulative cognitive decline.','Step-wise decline in memory\nand executive function\n(unlike the gradual decline\nof Alzheimer\'s disease),\noften with focal neurological signs.','Good BP control in\nmidlife is one of the most\nevidence-based ways to\nreduce dementia risk in later life\n— a powerful message for patient education.'],
]
story.append(plain_table(comp_table,[CW*0.18, CW*0.25, CW*0.27, CW*0.3]))
memory_hook('COMPLICATIONS MAP DIRECTLY ONTO TARGET ORGANS: Brain = stroke + vascular dementia. Heart = LVH + heart failure + IHD. Kidneys = CKD (vicious cycle). Eyes = retinopathy grades I-IV (III/IV = emergency). Vessels = aneurysm/dissection + peripheral artery disease. Every complication is the SAME mechanism (chronic vessel damage) playing out in a different organ.', story)
divider(story)

# §13 MRCP Top Trigger Scenarios
sec_header('Section 13: Top 12 MRCP Exam Trigger Scenarios — Hypertension', story)
professor_says('These twelve scenarios represent the patterns examiners return to year after year. If a hypertension question appears in your exam, it is very likely to be a variation of one of these. Read each one as a "pattern to recognise," not a fact to memorise.', story)

triggers = [
    ['#','MRCP Scenario','Answer / Key Point'],
    ['1','Clinic BP is 152/94 mmHg in an asymptomatic 45-year-old. What is the correct next step?','Do NOT diagnose from one reading. Offer ABPM (preferred) or HBPM to confirm before labelling as hypertension.'],
    ['2','A 26-year-old has a BP of 168/104 mmHg with no other findings. What should you specifically consider?','Young age + significant hypertension = actively investigate for a SECONDARY cause (renal, endocrine, coarctation, drugs) — do not simply label as "essential."'],
    ['3','Hypertensive patient has unprovoked hypokalaemia (K+ 2.8) and muscle cramps. Likely diagnosis and first test?','Conn\'s syndrome (primary hyperaldosteronism). First test: plasma aldosterone-to-renin ratio (raised aldosterone + suppressed renin).'],
    ['4','Patient has episodic headaches, palpitations, and sweating with intermittent BP spikes. What must you do BEFORE any drug treatment?','Suspect phaeochromocytoma. Confirm with urinary/plasma metanephrines. CRITICAL: give an ALPHA-blocker first — never a beta-blocker first (risk of fatal hypertensive crisis from unopposed alpha-stimulation).'],
    ['5','Young patient has high BP in the arms but weak femoral pulses and radio-femoral delay. Diagnosis?','Coarctation of the aorta. Confirm with echocardiogram and CT/MR aortography; CXR may show rib notching.'],
    ['6','58-year-old White British man needs his first antihypertensive. According to NICE, what is first-line?','ACE inhibitor or ARB ("A") — because he is over 55 only by a small margin but NOT of Black African/Caribbean origin... actually being 58 places him in the >=55 group, so the correct first-line is a CALCIUM CHANNEL BLOCKER ("C"). (Always check the age cut-off carefully — this exact trap appears often.)'],
    ['7','Patient develops a persistent dry cough on ramipril. What is the best next step?','Switch to an ARB (e.g., losartan) — same RAAS-blocking benefit, but ARBs do not cause cough because they do not affect bradykinin breakdown.'],
    ['8','Patient on amlodipine develops bilateral ankle swelling. Should you add a diuretic?','No — this swelling is from peripheral vasodilation (fluid shift), NOT fluid overload, so diuretics will not help. Consider switching class or adding an ACE-i/ARB, which can reduce this specific oedema.'],
    ['9','Patient remains above target on A+C+D (three drugs at full dose). Potassium is 4.2 mmol/L. Next step?','This is resistant hypertension. Confirm with ABPM/HBPM, check adherence, then ADD LOW-DOSE SPIRONOLACTONE (since K+ <= 4.5).'],
    ['10','Patient presents with BP 230/140 mmHg, severe headache, confusion, and Grade IV retinopathy on fundoscopy. What is the diagnosis and immediate plan?','Hypertensive emergency (malignant hypertension with encephalopathy). Admit immediately to a monitored setting, start IV antihypertensives (e.g., labetalol), and reduce MAP by no more than 25% in the first hour.'],
    ['11','A pregnant woman at 32 weeks has new hypertension, proteinuria, and brisk reflexes. What is the diagnosis and first-line drug?','Pre-eclampsia. First-line antihypertensive: LABETALOL. Magnesium sulphate is given to prevent/treat eclamptic SEIZURES (not as a BP-lowering drug). Delivery is the definitive treatment. AVOID ACE-i/ARB (teratogenic).'],
    ['12','Patient with chest/back "tearing" pain, unequal arm blood pressures, and a new murmur. What is the diagnosis and how fast should BP be lowered?','Aortic dissection. This is the EXCEPTION to the "go slow" rule — lower heart rate and BP rapidly and aggressively (IV labetalol or esmolol first) to reduce shearing stress on the aortic wall, alongside emergency surgical assessment.'],
]
story.append(plain_table(triggers,[CW*0.04, CW*0.4, CW*0.56]))
memory_hook('TOP TRIGGERS: One reading never diagnoses HTN (confirm with ABPM/HBPM). Young + hypertensive = hunt for a cause. Low K+ = Conn\'s. Episodic spells = phaeo (alpha-block first). Radio-femoral delay = coarctation. Cough on ACE-i = switch to ARB. Ankle swelling on CCB = do NOT add a diuretic. Resistant HTN = check adherence, then spironolactone. Number alone never equals "emergency" — organ damage does. Aortic dissection = the ONE exception — lower BP FAST.', story)
divider(story)

# §14 PACES + Minimal Resources
sec_header('Section 14: PACES Examination Guide and Minimal Resources Summary', story)
professor_says('In PACES, hypertension rarely appears as a "diagnose this" station on its own — it appears INSIDE other stations: cardiovascular examination, history-taking, communication skills, and ethics/explaining-a-new-diagnosis scenarios. Be ready to examine for it, ask about it, and explain it in plain language, all at once.', story)

story.append(bp('<b>PACES Station 1 — Examination: What To Specifically Look For:</b>'))
paces_exam = [
    ['Examination Step','What To Do / Look For','What It Tells You'],
    ['Measure BP correctly','Both arms, seated, relaxed,\ncuff at heart level, after\n5 minutes of rest. Repeat if\nfirst reading is high.','Demonstrates correct technique\n— examiners specifically watch\nfor this. A >15 mmHg difference\nbetween arms is itself a finding to report.'],
    ['Pulses','Radial AND femoral pulses\ntogether — feel for\nradio-femoral delay.','Coarctation of the aorta —\na classic "spot diagnosis"\nin a young patient.'],
    ['Fundoscopy','Examine the retina —\nlook for silver wiring,\nAV nipping, haemorrhages,\ncotton-wool spots, papilloedema.','Grading hypertensive\nretinopathy — and immediately\nflagging a possible emergency\n(Grade III/IV).'],
    ['Praecordium\n(heart examination)','Apex beat character and\nposition, heart sounds\n(listen for S4), signs of\nheart failure.','Evidence of LVH or\nheart failure — long-standing,\npoorly controlled hypertension.'],
    ['Abdomen','Auscultate for renal\nartery bruits; palpate\nfor enlarged kidneys.','Possible secondary causes —\nrenal artery stenosis,\npolycystic kidney disease.'],
]
story.append(plain_table(paces_exam,[CW*0.22, CW*0.4, CW*0.38]))
story.append(Spacer(1, 6))

story.append(bp('<b>PACES Communication — Explaining a New Diagnosis of Hypertension (in plain language):</b>'))
for pt in [
    '"Your blood pressure is the force of blood pushing against the walls of your blood vessels. When this force is too high for too long, it slowly damages your blood vessels — like water at high pressure slowly wearing down a pipe."',
    '"This is sometimes called \'the silent killer\' because most people feel completely normal — that is exactly why we check it, even when you feel fine."',
    '"The good news: this is one of the most TREATABLE conditions in medicine. With the right combination of lifestyle changes and, if needed, tablets, we can bring your risk right down to a much safer level."',
    '"We will start with simple changes — less salt in food, regular walking, less alcohol — and we will check your blood pressure again. If it is still high, we will add a tablet, and we may need to add a second or third one over time. This is normal and does not mean things are getting worse — it means we are fine-tuning your treatment."',
    '"You may feel completely well on treatment — please do not stop your tablets just because you feel fine. The whole point of these tablets is to protect you from problems you cannot feel happening."',
    '"If you ever get a sudden, severe headache, vision changes, chest pain, or weakness down one side, please go to the emergency department immediately — these could be signs that your blood pressure has become dangerously high."',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 6))

minimal_rows = [
    [Paragraph('<b>MINIMAL RESOURCES SUMMARY — Managing Hypertension With Limited Equipment</b>', sAlert)],
    [Paragraph('If only a manual sphygmomanometer is available: Still fully diagnostic — measure both arms, seated, after 5 minutes rest, repeat if high. No automated machine is required.', sBody)],
    [Paragraph('If no ABPM device: Use Home Blood Pressure Monitoring (HBPM) with any validated home cuff — twice daily for 4-7 days gives an equally valid confirmation.', sBody)],
    [Paragraph('If no biochemistry lab nearby: Prioritise getting AT LEAST a baseline potassium and creatinine before starting an ACE inhibitor/ARB or spironolactone — these are the two values that can cause real harm if ignored.', sBody)],
    [Paragraph('If no echocardiogram: A careful clinical exam (apex beat, S4, signs of failure) plus a 12-lead ECG (looking for LVH voltage criteria) gives most of the information you need to detect cardiac damage.', sBody)],
    [Paragraph('If specialist secondary-cause testing is unavailable: A good history and examination (radio-femoral delay, abdominal bruit, episodic symptoms, drug history, low potassium) will identify MOST patients who need referral — refer onward for confirmatory testing.', sBody)],
    [Paragraph('Three drugs that cover almost every situation: a calcium channel blocker (amlodipine), an ACE inhibitor (ramipril), and a thiazide-like diuretic (indapamide) — these three, used in the correct stepwise order, control the overwhelming majority of patients worldwide.', sBody)],
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
story.append(Spacer(1, 8))
memory_hook('PACES READY-RECKONER: Always measure BOTH arms. Always feel for radio-femoral delay. Always do fundoscopy. Explain in plain words: "silent," "treatable," "do not stop tablets when you feel well," "seek emergency help for sudden severe headache/vision change/weakness." Three drugs (amlodipine, ramipril, indapamide) treat most of the world\'s hypertension.', story)
divider(story)

# §15 Self-Test
story.append(PageBreak())
sec_header('Section 15: Self-Test — Hypertension MCQ Examination (12 Questions)', story)
professor_says('Now it is YOUR turn to be the professor. Attempt every question fully before turning to the answer key at the very end of this document. Write your answer in the blank space provided. This is the single best way to find out what you truly know — versus what you only THINK you know.', story)
story.append(bp('<i>Instructions: Each question is a short clinical scenario, exactly as it would appear in the MRCP exam. Choose the SINGLE best answer from the options given (A-E). Write your chosen letter in the blank space. The correct answers and full explanations are given separately in Section 16, at the very end — do not look ahead!</i>'))
story.append(Spacer(1, 8))

mcq(1,
    'A 48-year-old woman attends for a routine cervical smear. Incidentally, her BP is recorded as 158/96 mmHg. She feels entirely well and has no past medical history. What is the most appropriate next step?',
    [('A','Start an ACE inhibitor immediately'),
     ('B','Reassure her that this is normal for her age'),
     ('C','Offer ambulatory blood pressure monitoring (ABPM) to confirm the diagnosis'),
     ('D','Admit her to hospital for urgent assessment'),
     ('E','Repeat the BP measurement in 12 months')],
    'C',
    'A single clinic reading is never sufficient to diagnose hypertension (white-coat effect). NICE recommends confirming with ABPM (preferred) or HBPM before making the diagnosis and starting treatment.',
    story)

mcq(2,
    'A 29-year-old man is found to have a BP of 172/108 mmHg at three separate visits. He is otherwise fit and well, runs marathons, and has no family history of hypertension. What should you do?',
    [('A','Reassure him — young fit people often have falsely high readings'),
     ('B','Start a calcium channel blocker and review in 3 months'),
     ('C','Investigate for a secondary cause of hypertension'),
     ('D','Advise him to simply reduce his training intensity'),
     ('E','Discharge him with lifestyle advice only')],
    'C',
    'Significant hypertension in a young, otherwise healthy patient is unusual and should prompt active investigation for a secondary cause (renal, endocrine, coarctation, or drug-related) — "young + hypertensive = look harder."',
    story)

mcq(3,
    'A 41-year-old woman has resistant hypertension, recurrent muscle cramps, and a serum potassium of 2.9 mmol/L with mild metabolic alkalosis. Which investigation should be requested first?',
    [('A','24-hour urinary free cortisol'),
     ('B','Plasma aldosterone-to-renin ratio'),
     ('C','Plasma free metanephrines'),
     ('D','Renal artery Doppler ultrasound'),
     ('E','Overnight dexamethasone suppression test')],
    'B',
    'Hypertension with unexplained hypokalaemia and metabolic alkalosis is the classic pattern of Conn\'s syndrome (primary hyperaldosteronism). The aldosterone-to-renin ratio (raised aldosterone, suppressed renin) is the correct first-line confirmatory test.',
    story)

mcq(4,
    'A 35-year-old man has episodic attacks of headache, palpitations, pallor, and sweating, during which his BP spikes to 220/130 mmHg. Phaeochromocytoma is suspected and confirmed. Before starting any definitive treatment, which class of drug MUST be started first?',
    [('A','Beta-blocker'),
     ('B','Thiazide-like diuretic'),
     ('C','ACE inhibitor'),
     ('D','Alpha-blocker'),
     ('E','Calcium channel blocker')],
    'D',
    'In phaeochromocytoma, an alpha-blocker (e.g., phenoxybenzamine) MUST be given first. Starting a beta-blocker first leaves alpha-receptors unopposed, causing a potentially fatal hypertensive crisis from unrestrained vasoconstriction.',
    story)

mcq(5,
    'A 16-year-old boy is found to have hypertension confined to the upper limbs, with weak femoral pulses and radio-femoral delay. Which investigation would best confirm the underlying diagnosis?',
    [('A','24-hour ABPM'),
     ('B','Renal artery Doppler ultrasound'),
     ('C','Echocardiogram and CT/MR aortography'),
     ('D','Plasma aldosterone-to-renin ratio'),
     ('E','Urinary metanephrines')],
    'C',
    'This is the classic presentation of coarctation of the aorta (hypertension in the arms, weak femoral pulses, radio-femoral delay). Echocardiography and CT/MR aortography confirm the site and severity of the narrowing.',
    story)

mcq(6,
    'A 60-year-old man of Black African-Caribbean origin requires his first antihypertensive medication. According to the NICE stepwise (A-C-D) algorithm, which drug class should be started first?',
    [('A','ACE inhibitor'),
     ('B','Angiotensin receptor blocker'),
     ('C','Calcium channel blocker'),
     ('D','Thiazide-like diuretic'),
     ('E','Beta-blocker')],
    'C',
    'NICE recommends starting with a calcium channel blocker ("C") for patients aged 55 or over, OR of Black African or African-Caribbean origin (of any age) — this patient meets both criteria. Lower-renin physiology makes ACE-i/ARB monotherapy less reliably effective in this group.',
    story)

mcq(7,
    'A patient established on ramipril for hypertension develops a persistent, troublesome dry cough. What is the most appropriate next step?',
    [('A','Stop all antihypertensive treatment'),
     ('B','Add a calcium channel blocker without changing the ACE inhibitor'),
     ('C','Switch to an angiotensin receptor blocker (ARB)'),
     ('D','Reassure the patient that the cough will resolve with continued treatment'),
     ('E','Switch to a beta-blocker')],
    'C',
    'ACE inhibitor cough is caused by accumulation of bradykinin (normally broken down by ACE). ARBs block the angiotensin II receptor directly, without affecting bradykinin, and therefore do not cause this cough — the standard substitute.',
    story)

mcq(8,
    'A patient taking amlodipine for hypertension develops bilateral ankle swelling. Blood pressure remains well controlled. What is the most appropriate management of the swelling?',
    [('A','Add a loop diuretic such as furosemide'),
     ('B','Add a thiazide-like diuretic'),
     ('C','Stop amlodipine and consider an alternative agent or adding an ACE inhibitor/ARB'),
     ('D','Increase the dose of amlodipine'),
     ('E','Restrict fluid intake')],
    'C',
    'Calcium channel blocker-induced ankle swelling results from peripheral vasodilation and fluid shift into tissues — NOT true fluid overload — so diuretics are ineffective. Switching class, or adding an ACE inhibitor/ARB (which can reduce this specific oedema), is the correct approach.',
    story)

mcq(9,
    'A patient remains above target blood pressure despite being on optimal doses of an ACE inhibitor, a calcium channel blocker, and a thiazide-like diuretic. Serum potassium is 4.1 mmol/L. What is the most appropriate next step?',
    [('A','Add an alpha-blocker'),
     ('B','Add a beta-blocker'),
     ('C','Add low-dose spironolactone'),
     ('D','Switch the ACE inhibitor to an ARB'),
     ('E','Increase the dose of the thiazide-like diuretic further')],
    'C',
    'This is resistant hypertension (uncontrolled on three drugs including a diuretic). With potassium <= 4.5 mmol/L, NICE recommends adding low-dose spironolactone as the Step 4 option of choice, with close monitoring of potassium.',
    story)

mcq(10,
    'A 70-year-old man presents with a BP of 226/138 mmHg, sudden severe headache, confusion, and Grade IV hypertensive retinopathy on fundoscopy. What is the most appropriate immediate management?',
    [('A','Start oral amlodipine and review in clinic in one week'),
     ('B','Reassure and discharge with lifestyle advice'),
     ('C','Admit for monitored IV antihypertensive treatment, reducing mean arterial pressure by no more than 25% in the first hour'),
     ('D','Rapidly normalise the blood pressure to 120/80 mmHg within the first hour using IV agents'),
     ('E','Give a single dose of oral labetalol and send home with a follow-up appointment')],
    'C',
    'This is a hypertensive emergency (malignant hypertension with encephalopathy and Grade IV retinopathy — papilloedema). The patient needs admission to a monitored setting with controlled, GRADUAL IV BP reduction — no more than 25% fall in mean arterial pressure in the first hour — to avoid hypoperfusion injury to already auto-regulated organs.',
    story)

mcq(11,
    'A woman at 33 weeks of pregnancy develops new hypertension, proteinuria, headache, and brisk reflexes. Eclamptic seizures are a concern. Which TWO statements are correct regarding her management?',
    [('A','Labetalol is the first-line antihypertensive, and magnesium sulphate is used to prevent/treat seizures (not to lower blood pressure)'),
     ('B','ACE inhibitors are the first-line antihypertensive choice in pregnancy'),
     ('C','Magnesium sulphate is the first-line antihypertensive agent in pre-eclampsia'),
     ('D','Definitive treatment is delivery of the baby, when appropriate and safe'),
     ('E','Thiazide diuretics are preferred for long-term control during pregnancy')],
    'A and D',
    'Labetalol is first-line for BP control in pre-eclampsia; magnesium sulphate is given specifically to prevent and treat eclamptic SEIZURES, not as an antihypertensive — these are two separate roles that are very commonly confused. ACE inhibitors, ARBs, and thiazides are AVOIDED in pregnancy (teratogenic / harmful). Delivery of the baby remains the definitive cure for pre-eclampsia.',
    story)

mcq(12,
    'A 64-year-old man presents with sudden, severe, "tearing" interscapular back pain. His blood pressure is 210/124 mmHg, with a 40 mmHg difference between his two arms, and a new early diastolic murmur is heard. What is the diagnosis, and how should his blood pressure be managed acutely?',
    [('A','Hypertensive urgency — lower the BP gradually over 24-48 hours with oral agents'),
     ('B','Aortic dissection — lower the heart rate and blood pressure rapidly and aggressively with IV labetalol or esmolol'),
     ('C','Phaeochromocytoma crisis — start an alpha-blocker and observe over several hours'),
     ('D','Acute coronary syndrome — give thrombolysis immediately without addressing blood pressure'),
     ('E','Malignant hypertension — reduce mean arterial pressure by no more than 25% over the first hour')],
    'B',
    'The combination of tearing back pain, unequal arm blood pressures, and a new aortic regurgitation murmur (early diastolic) strongly suggests aortic dissection. This is the ONE exception to the "go slow" rule in hypertensive emergencies — heart rate and blood pressure should be lowered rapidly and aggressively (target HR ~60, systolic ~100-120 mmHg) using IV labetalol or esmolol, to reduce shearing stress on the weakened aortic wall, alongside emergency surgical referral.',
    story)

divider(story)

# §16 Answer Key — kept separate, on its own page, so the test stays "blank" until checked
story.append(PageBreak())
sec_header('Section 16: Answer Key — Self-Test Solutions and Explanations', story)
info_box('<b>Now check your work.</b> Go back through Section 15 question by question, compare your written answer with the correct answer below, and read the explanation — especially for any question you got wrong. Understanding WHY an answer is correct (or incorrect) is far more valuable than simply knowing which letter to circle.', story)
print_answer_key(story)
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
    [Paragraph('MASTER MEMORY SUMMARY — ARTERIAL HYPERTENSION', sGrnB)],
    [Paragraph('DEFINITION: Persistently raised BP, high enough for long enough to raise risk of stroke, MI, kidney failure, and death. USUALLY SILENT — "the silent killer." Master equation: BP = Cardiac Output x Systemic Vascular Resistance.', sGrn)],
    [Paragraph('DIAGNOSIS: NEVER diagnose from one clinic reading. Clinic >= 140/90 -> CONFIRM with ABPM (preferred, daytime average >= 135/85) or HBPM (>= 4-7 days, average >= 135/85). Severe = >= 180/120 -> check for organ damage same day.', sGrn)],
    [Paragraph('PHYSIOLOGY = FOUR SYSTEMS (and their drug targets): RAAS (ACE-i, ARB, spironolactone), Sympathetic NS (beta-/alpha-blockers), Renal salt/water handling (thiazide-like diuretics), Baroreceptor reflex (explains postural hypotension side effects).', sGrn)],
    [Paragraph('CAUSES: 90-95% primary/essential (age, genes, stiff vessels, salt sensitivity, sick endothelium). 5-10% secondary — "CHAPS": Coarctation, Hyperaldosteronism/Hypercortisolism, Apnoea/Adrenal (phaeo), Parenchymal renal disease, Steroids/drugs/pregnancy. Young + hypertensive = hunt for a cause.', sGrn)],
    [Paragraph('EXAMINATION: Both arms\' BP, radio-femoral delay, fundoscopy (grade retinopathy I-IV), heart (LVH signs, S4, failure), abdomen (renal bruit, kidneys), neuro exam. Grade III/IV retinopathy = malignant HTN = same-day admission.', sGrn)],
    [Paragraph('OUTPATIENT TREATMENT — A-C-D LADDER: Step 1 = A (under 55, not Black African/Caribbean) or C (55+ or Black African/Caribbean any age). Step 2 = A+C. Step 3 = A+C+D. Step 4 (resistant) = spironolactone (K+ <= 4.5) or alpha-/beta-blocker (K+ > 4.5). PLUS lifestyle always: salt < 6g/day, exercise, weight loss, less alcohol, stop smoking.', sGrn)],
    [Paragraph('TARGETS: < 140/90 (under 80y) | < 150/90 (80y+) | < 130/80 (diabetes/CKD with organ disease) | < 135/85 (pregnancy).', sGrn)],
    [Paragraph('DRUG QUICK-RECALL: ACE-i = dry cough + angioedema (bradykinin) + avoid pregnancy. ARB = same benefit, no cough. CCB = ankle swelling (NOT fluid overload — diuretics will not help). Thiazide-like = low Na+/K+, high Ca2+/urate (gout). Beta-blocker = not first-line, reserved for compelling indications. Spironolactone = K+-SPARING -> watch HYPERkalaemia + gynaecomastia.', sGrn)],
    [Paragraph('EMERGENCY VS URGENCY: The NUMBER never defines an emergency — ORGAN DAMAGE does (encephalopathy, stroke, dissection, pulmonary oedema, eclampsia, AKI, Grade III/IV retinopathy). GOLDEN RULE: drop MAP by <= 25% in the first hour. EXCEPTION: aortic dissection — go FAST and HARD (labetalol/esmolol). Phaeo crisis = ALPHA-blocker first, never beta first.', sGrn)],
    [Paragraph('SPECIAL SITUATIONS: Pregnancy = labetalol + magnesium for seizures (NOT BP) + delivery is the cure; NEVER ACE-i/ARB. Elderly = start low go slow, watch falls. Diabetes/CKD = ACE-i/ARB first regardless of age/ethnicity (renal protection). Resistant = check ADHERENCE first, then spironolactone.', sGrn)],
    [Paragraph('COMPLICATIONS: Stroke, IHD/heart failure (LVH), CKD, retinopathy (I-IV), aortic aneurysm/dissection, peripheral artery disease, vascular dementia — all are the SAME mechanism (chronic vessel damage) in different organs.', sGrn)],
    [Paragraph('PACES: Measure both arms, feel for radio-femoral delay, always do fundoscopy. Explain simply: "silent," "very treatable," "do not stop tablets when feeling well," "seek emergency help for sudden severe headache/visual change/weakness." Three drugs (amlodipine, ramipril, indapamide) treat most of the world.', sGrn)],
]
innerG = Table(gRows, colWidths=[CW-4])
innerG.setStyle(gTS1)
outerG = Table([[innerG]], colWidths=[CW])
outerG.setStyle(gTSO)
story.append(outerG)
story.append(Spacer(1, 14))

# Footer note
story.append(HRFlowable(width=CW, thickness=1.5, color=HexColor('#0d5c63'), spaceAfter=6))
story.append(Paragraph('MRCP Revision Note: Arterial Hypertension — Diagnosis, Outpatient Management and Hypertensive Emergencies  |  NICE NG136 / ESC 2023 Guidelines  |  Ganesh & Kuruvilla Prescribing Reference  |  Sections 1-16 inclusive, with Interactive Q&A and Self-Test', ParagraphStyle('FT', fontName='DV-I', fontSize=8, leading=11, textColor=HexColor('#555555'), alignment=1)))

# Build document
doc.build(story)
print('SUCCESS: Hypertension_MRCP_Note.pdf written to', OUT)
