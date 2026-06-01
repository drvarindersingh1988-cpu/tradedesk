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

OUT = '/mnt/user-data/outputs/Septic_Shock_MRCP_Note.pdf'
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

sTitle = ParagraphStyle('TT', fontName='DV-B', fontSize=22, leading=28,
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

# ─── PIL helpers ─────────────────────────────────────────────────────────────
def wt(draw, text, x, y, font, fill='#1a1a2e', anchor='mm'):
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)

def arr_r(draw, x, y, length=40, col='#0d5c63'):
    draw.line([(x, y), (x+length, y)], fill=col, width=2)
    draw.polygon([(x+length, y), (x+length-8, y-5), (x+length-8, y+5)], fill=col)

def arr_d(draw, x, y, length=30, col='#0d5c63'):
    draw.line([(x, y), (x, y+length)], fill=col, width=2)
    draw.polygon([(x, y+length), (x-5, y+length-8), (x+5, y+length-8)], fill=col)

def i2r(img, W):
    scale = W / img.width
    nH = int(img.height * scale)
    img = img.resize((int(W), nH), Image.LANCZOS)
    buf = BytesIO(); img.save(buf, 'PNG'); buf.seek(0)
    return RLImage(buf, width=W, height=nH)

print('Building PIL diagrams...')

# ─── PIL 1: Sepsis Cascade ────────────────────────────────────────────────────
def make_sepsis_cascade():
    W, H = 900, 290
    img = Image.new('RGB', (W, H), '#ffffff')
    draw = ImageDraw.Draw(img)
    try:
        fB = ImageFont.truetype(FONT_DIR+'DejaVuSans-Bold.ttf', 14)
        fS = ImageFont.truetype(FONT_DIR+'DejaVuSans.ttf', 11)
        fXS= ImageFont.truetype(FONT_DIR+'DejaVuSans.ttf', 10)
    except:
        fB = fS = fXS = ImageFont.load_default()
    draw.rectangle([0,0,W-1,H-1], fill='#f0fafb', outline='#1a8a94', width=2)
    draw.text((W//2,16), 'THE SEPSIS CASCADE: INFECTION TO ORGAN FAILURE', font=fB, fill='#0d5c63', anchor='mm')
    steps = [
        ('#fde8e8','#c0392b','INFECTION','Bacteria/virus','enters body','Mortality: low'),
        ('#fef3e2','#d4640a','SIRS','Body alarm','response','~5%'),
        ('#fff3cd','#e6a817','SEPSIS','Infection +','organ danger','~15%'),
        ('#f5eef8','#7d3c98','SEPTIC SHOCK','Low BP needs','vasopressors','30-50%'),
        ('#fde8e8','#721c24','MODS','Multiple organ','failure','>50%'),
    ]
    bw=140; cy=160; gap=36
    total=(len(steps)*bw)+(len(steps)-1)*gap
    sx=(W-total)//2
    for i,(bg,bd,t1,t2,t3,mort) in enumerate(steps):
        cx=sx+i*(bw+gap)+bw//2
        x0,y0=cx-bw//2,cy-50
        draw.rectangle([x0,y0,x0+bw,y0+100], fill=bg, outline=bd, width=2)
        draw.text((cx,y0+15),t1,font=fB,fill=bd,anchor='mm')
        draw.text((cx,y0+36),t2,font=fXS,fill='#1a1a2e',anchor='mm')
        draw.text((cx,y0+52),t3,font=fXS,fill='#1a1a2e',anchor='mm')
        draw.text((cx,y0+72),mort,font=fXS,fill=bd,anchor='mm')
        draw.text((cx,y0+90),'mortality',font=fXS,fill=bd,anchor='mm')
        if i<len(steps)-1:
            arr_r(draw, cx+bw//2, cy, length=gap-2, col=bd)
    draw.text((W//2,H-14),'Recognise early. Treat fast. Every hour matters.', font=fS, fill='#555555', anchor='mm')
    return i2r(img, CW)

# ─── PIL 2: Pathophysiology ───────────────────────────────────────────────────
def make_pathophys():
    W, H = 900, 380
    img = Image.new('RGB', (W, H), '#fff8f8')
    draw = ImageDraw.Draw(img)
    try:
        fB = ImageFont.truetype(FONT_DIR+'DejaVuSans-Bold.ttf', 13)
        fS = ImageFont.truetype(FONT_DIR+'DejaVuSans.ttf', 11)
        fXS= ImageFont.truetype(FONT_DIR+'DejaVuSans.ttf', 9)
    except:
        fB = fS = fXS = ImageFont.load_default()
    draw.rectangle([0,0,W-1,H-1], fill='#fff8f8', outline='#c0392b', width=2)
    draw.text((W//2,16), 'HOW INFECTION CAUSES SEPTIC SHOCK', font=fB, fill='#c0392b', anchor='mm')
    # Top box: infection
    cx=W//2
    draw.rectangle([cx-160,32,cx+160,72], fill='#fde8e8', outline='#c0392b', width=2)
    draw.text((cx,52),'INFECTION + TOXINS (LPS, exotoxins)',font=fB,fill='#c0392b',anchor='mm')
    arr_d(draw,cx,72,length=20,col='#c0392b')
    # Cytokines box
    draw.rectangle([cx-200,92,cx+200,132], fill='#fef3e2', outline='#d4640a', width=2)
    draw.text((cx,107),'MACROPHAGES release CYTOKINES',font=fB,fill='#d4640a',anchor='mm')
    draw.text((cx,124),'TNF-alpha, IL-1, IL-6, IL-8',font=fXS,fill='#1a1a2e',anchor='mm')
    # Three branches
    branch_y=132
    boxes=[
        (150,'#e8f4fd','#2471a3','VASODILATION','Nitric oxide opens','all blood vessels','BP drops sharply'),
        (450,'#f5eef8','#7d3c98','CAPILLARY LEAK','Fluid leaves vessels','Tissues swell (oedema)','Blood volume falls'),
        (750,'#fef3e2','#d4640a','CARDIAC DEPRESSION','Cytokines weaken heart','Less blood pumped out','Low cardiac output'),
    ]
    for bx,bg,bd,t1,t2,t3,t4 in boxes:
        draw.line([(cx,branch_y),(bx,branch_y+30)],fill='#888888',width=2)
        bw2=175; bh=95; x0=bx-bw2//2; y0=branch_y+30
        draw.rectangle([x0,y0,x0+bw2,y0+bh],fill=bg,outline=bd,width=2)
        draw.text((bx,y0+14),t1,font=fB,fill=bd,anchor='mm')
        draw.text((bx,y0+34),t2,font=fXS,fill='#1a1a2e',anchor='mm')
        draw.text((bx,y0+50),t3,font=fXS,fill='#1a1a2e',anchor='mm')
        draw.text((bx,y0+66),t4,font=fXS,fill='#1a1a2e',anchor='mm')
        arr_d(draw,bx,y0+bh,length=18,col=bd)
    # Bottom
    draw.rectangle([cx-220,300,cx+220,340],fill='#fde8e8',outline='#721c24',width=2)
    draw.text((cx,315),'TISSUE HYPOPERFUSION + ORGAN FAILURE (MODS)',font=fB,fill='#721c24',anchor='mm')
    draw.text((cx,332),'Lactate rises. Kidneys fail. Lungs fail. Brain fails.',font=fXS,fill='#721c24',anchor='mm')
    draw.text((W//2,H-14),'All three mechanisms work together at the same time.',font=fS,fill='#555555',anchor='mm')
    return i2r(img, CW)

# ─── PIL 3: qSOFA vs SOFA ─────────────────────────────────────────────────────
def make_scoring():
    W, H = 900, 340
    img = Image.new('RGB', (W, H), '#f0fafb')
    draw = ImageDraw.Draw(img)
    try:
        fB = ImageFont.truetype(FONT_DIR+'DejaVuSans-Bold.ttf', 13)
        fS = ImageFont.truetype(FONT_DIR+'DejaVuSans.ttf', 11)
        fXS= ImageFont.truetype(FONT_DIR+'DejaVuSans.ttf', 10)
    except:
        fB = fS = fXS = ImageFont.load_default()
    draw.rectangle([0,0,W-1,H-1],fill='#f0fafb',outline='#1a8a94',width=2)
    draw.text((W//2,16),'SEPSIS SCORING TOOLS',font=fB,fill='#0d5c63',anchor='mm')
    # qSOFA left
    draw.rectangle([15,32,440,H-15],fill='#e8f4fd',outline='#2471a3',width=2)
    draw.text((228,52),'qSOFA  (Quick Bedside Score)',font=fB,fill='#2471a3',anchor='mm')
    draw.text((228,70),'No blood tests needed. Score 2+ = assess for sepsis.',font=fXS,fill='#1a1a2e',anchor='mm')
    qitems=[
        ('1. Respiratory Rate >= 22/min','+1'),
        ('2. Altered conscious level (GCS<15)','+1'),
        ('3. Systolic BP <= 100 mmHg','+1'),
    ]
    for i,(label,pts) in enumerate(qitems):
        y=90+i*68
        draw.rectangle([30,y,425,y+58],fill='#ffffff',outline='#2471a3',width=1)
        draw.text((228,y+20),label,font=fB,fill='#2471a3',anchor='mm')
        draw.text((228,y+42),f'Score: {pts}',font=fB,fill='#c0392b',anchor='mm')
    draw.text((228,H-30),'Max = 3. Each item = 1 point.',font=fXS,fill='#555555',anchor='mm')
    # SOFA right
    draw.rectangle([460,32,W-15,H-15],fill='#e0f4f5',outline='#0d5c63',width=2)
    draw.text((672,52),'SOFA Score  (ICU / Lab Score)',font=fB,fill='#0d5c63',anchor='mm')
    draw.text((672,70),'Increase >= 2 points = organ dysfunction = SEPSIS.',font=fXS,fill='#1a1a2e',anchor='mm')
    sofa=[('Lungs','PaO2/FiO2 ratio'),('Clotting','Platelets'),
          ('Liver','Bilirubin'),('Heart','MAP / vasopressors'),
          ('Brain','GCS'),('Kidneys','Creatinine/urine')]
    rh=(H-120)//len(sofa)-3
    for i,(organ,detail) in enumerate(sofa):
        y=88+i*(rh+3)
        draw.rectangle([470,y,W-25,y+rh],fill='#ffffff',outline='#0d5c63',width=1)
        draw.text((480,y+rh//2-6),organ,font=fB,fill='#0d5c63',anchor='lm')
        draw.text((480,y+rh//2+8),detail,font=fXS,fill='#555555',anchor='lm')
    draw.text((672,H-30),'Max = 24 (4 pts x 6 organs). Higher = worse.',font=fXS,fill='#555555',anchor='mm')
    return i2r(img, CW)

# ─── PIL 4: Sepsis-6 Bundle ───────────────────────────────────────────────────
def make_sepsis6():
    W, H = 900, 280
    img = Image.new('RGB', (W, H), '#f8fff8')
    draw = ImageDraw.Draw(img)
    try:
        fB = ImageFont.truetype(FONT_DIR+'DejaVuSans-Bold.ttf', 14)
        fS = ImageFont.truetype(FONT_DIR+'DejaVuSans.ttf', 11)
        fXS= ImageFont.truetype(FONT_DIR+'DejaVuSans.ttf', 10)
    except:
        fB = fS = fXS = ImageFont.load_default()
    draw.rectangle([0,0,W-1,H-1],fill='#f8fff8',outline='#28a745',width=2)
    draw.text((W//2,16),'SEPSIS-6 BUNDLE: DO ALL 6 WITHIN 1 HOUR',font=fB,fill='#28a745',anchor='mm')
    # 3 GIVE
    draw.rectangle([15,32,440,H-15],fill='#d4edda',outline='#28a745',width=2)
    draw.text((228,52),'3 GIVE',font=fB,fill='#155724',anchor='mm')
    give=[('1. Give HIGH-FLOW OXYGEN','Target SpO2 >= 94%'),
          ('2. Give IV FLUID BOLUS','500ml crystalloid over 15 min'),
          ('3. Give IV ANTIBIOTICS','Broad-spectrum. Within 1 hour.')]
    for i,(t1,t2) in enumerate(give):
        y=68+i*62
        draw.rectangle([28,y,425,y+52],fill='#ffffff',outline='#28a745',width=1)
        draw.text((228,y+16),t1,font=fB,fill='#155724',anchor='mm')
        draw.text((228,y+36),t2,font=fXS,fill='#1a1a2e',anchor='mm')
    # 3 TAKE
    draw.rectangle([460,32,W-15,H-15],fill='#fde8e8',outline='#c0392b',width=2)
    draw.text((672,52),'3 TAKE',font=fB,fill='#721c24',anchor='mm')
    take=[('4. Take BLOOD CULTURES','Before antibiotics if possible'),
          ('5. Measure BLOOD LACTATE','Lactate >= 2 = tissue hypoperfusion'),
          ('6. Measure URINE OUTPUT','Catheter. Target >= 0.5 ml/kg/hr')]
    for i,(t1,t2) in enumerate(take):
        y=68+i*62
        draw.rectangle([470,y,W-28,y+52],fill='#ffffff',outline='#c0392b',width=1)
        draw.text((672,y+16),t1,font=fB,fill='#721c24',anchor='mm')
        draw.text((672,y+36),t2,font=fXS,fill='#1a1a2e',anchor='mm')
    return i2r(img, CW)

img_cascade  = make_sepsis_cascade()
img_pathophys= make_pathophys()
img_scoring  = make_scoring()
img_sepsis6  = make_sepsis6()
print('PIL diagrams done.')

story = []

# ── Title ──────────────────────────────────────────────────────────────────────
story.append(Paragraph('SEPSIS AND SEPTIC SHOCK', sTitle))
story.append(Paragraph('Comprehensive MRCP Revision Note | Parts 1, 2 &amp; PACES', sSub))
story.append(Paragraph('From Infection to Organ Failure — Very Simple Language Throughout', sSub))
story.append(Spacer(1,8))
story.append(HRFlowable(width=CW, thickness=2, color=TEAL, spaceAfter=6))

# ── §1 OVERVIEW ────────────────────────────────────────────────────────────────
sec_header('Section 1: Overview — What is Sepsis?', story)

professor_says('Sepsis is one of the most important conditions in all of medicine. It kills more people each year than many cancers combined. It is treatable — but ONLY if recognised and treated FAST. Every doctor must know this topic perfectly.', story)

story.append(bp('<b>Simple explanation first:</b>'))
story.append(bp('Your body has an immune system. Think of it as your defence army. When bacteria or viruses enter the body, your immune system fights them.'))
story.append(bp('Sometimes the immune system fights TOO HARD. It does not just attack the infection. It starts attacking the body itself. Blood vessels open too wide. Fluid leaks out of blood vessels. The heart becomes weak. Organs start to fail.'))
story.append(bp('This is sepsis. It is not just an infection. It is the body\'s own defence going out of control — causing more damage than the infection itself.'))
story.append(Spacer(1,5))

story.append(bp('<b>Key Numbers — Why This Matters:</b>'))
for item in [
    '49 million cases of sepsis worldwide every year.',
    '11 million deaths from sepsis per year — that is 20% of all global deaths.',
    'In the UK: 123,000 cases per year. 37,000 deaths per year.',
    'Every 1-hour delay in antibiotic treatment increases mortality by approximately 7%.',
    'Septic shock has a death rate of 30–50%.',
    'Sepsis is the most common cause of death in the ICU (Intensive Care Unit).',
    'It is PREVENTABLE and TREATABLE — if caught early.',
]:
    story.append(bp(f'• {item}'))
story.append(Spacer(1,5))

story.append(bp('<b>The Definitions (Updated in 2016 — Called Sepsis-3):</b>'))
story.append(bp('In 2016, experts updated the definitions. This is called <b>Sepsis-3</b>. The old terms changed. MRCP tests the NEW definitions.'))
story.append(Spacer(1,3))

def_table = [
    ['Term','Old Definition (before 2016)','NEW Sepsis-3 Definition (2016)','Simple Explanation'],
    ['SIRS\n(Systemic Inflammatory Response Syndrome)','2 or more of: fever/hypothermia, fast heart, fast breathing, abnormal WBC','NO LONGER PART OF SEPSIS DEFINITION.\nSIRS can happen without infection\n(e.g. surgery, pancreatitis, trauma).','Body alarm response.\nCan happen with or without infection.\nNot specific enough for sepsis diagnosis.'],
    ['SEPSIS','Infection + SIRS criteria','Life-threatening organ dysfunction\ncaused by a dysregulated (out of control)\nhost response to infection.\nDiagnosed by: suspected infection\n+ SOFA score increase of 2+ points.','Infection that is DAMAGING ORGANS.\nThis is serious.\nNeeds hospital treatment.'],
    ['SEVERE SEPSIS','Sepsis + organ dysfunction','THIS TERM IS NO LONGER USED.\nJust called "Sepsis" now.','Old term. Removed in Sepsis-3.\nDo not use it in exams.'],
    ['SEPTIC SHOCK','Sepsis + low BP not fixed by fluids','Sepsis PLUS BOTH:\n1. Vasopressors needed to keep\n   MAP >= 65 mmHg.\n2. Blood lactate > 2 mmol/L\n   despite adequate fluid.\nMortality > 40%.','Most dangerous stage.\nBP very low.\nFluids alone cannot fix it.\nNeeds ICU and vasopressor drugs.'],
]
story.append(plain_table(def_table, [CW*0.14,CW*0.22,CW*0.36,CW*0.28]))
story.append(Spacer(1,5))

info_box('<b>KEY MRCP FACT — Sepsis-3 (2016):</b> "Severe sepsis" is GONE. Sepsis = infection + organ dysfunction (SOFA increase ≥2). Septic shock = sepsis + vasopressors needed + lactate >2 mmol/L. Old SIRS criteria are no longer the definition of sepsis.', story)

memory_hook('SEPSIS = Infection + organ dysfunction (SOFA +2). SEPTIC SHOCK = Sepsis + vasopressors + lactate >2. "Severe sepsis" is REMOVED. SIRS is NOT the definition any more.', story)
divider(story)

# ── §2 ANATOMY ─────────────────────────────────────────────────────────────────
sec_header('Section 2: Anatomy — The Circulation and How Shock Disrupts It', story)

professor_says('To understand septic shock, first understand the normal blood circulation. Then you will understand exactly what goes wrong — and why the treatment works.', story)

story.append(bp('<b>The Normal Circulation — The Pump, The Pipes, The Pressure:</b>'))
for pt in [
    '<b>Heart</b> = the pump. Beats ~70 times per minute. Each beat pushes blood into the arteries.',
    '<b>Arteries</b> = the large pipes carrying blood AWAY from the heart. The aorta (ay-OR-tah) is the biggest.',
    '<b>Arterioles</b> (ar-TEER-ee-oles) = small arteries with muscular walls. They can squeeze (constrict) or relax (dilate). This is how blood pressure is controlled.',
    '<b>Capillaries</b> (KAP-ill-air-ees) = the tiniest vessels. One cell thick. Where oxygen and nutrients pass into the organs.',
    '<b>Veins</b> = carry blood BACK to the heart.',
    '<b>Blood pressure</b> depends on two things: (1) How hard the heart pumps. (2) How tight the arterioles are. Both must work together.',
    '<b>MAP</b> (Mean Arterial Pressure) = the average pressure in arteries. Normal = 70–100 mmHg. Organs need MAP ≥65 mmHg to survive.',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1,5))

story.append(bp('<b>The Endothelium (en-doh-THEE-lee-um) — The Inner Lining:</b>'))
story.append(bp('Every blood vessel has a lining on the inside. One cell thick. Called the endothelium.'))
story.append(bp('It controls: what passes through vessel walls. Blood pressure. Clotting. Inflammation.'))
story.append(bp('<b>In sepsis:</b> Bacterial toxins damage the endothelium. It becomes leaky. Fluid escapes into tissues. Vessels dilate widely. Result: very low blood pressure + tissue swelling + organ failure.'))
story.append(Spacer(1,5))

story.append(bp('<b>The Four Types of Shock — Comparison:</b>'))
shock_table = [
    ['Type','Simple Meaning','Heart Output','Vessel Resistance','Common Causes'],
    ['DISTRIBUTIVE\n(includes Septic Shock)','Vessels too wide.\nBlood spreads out.\nBP drops.','HIGH\n(heart works harder)','LOW\n(vessels dilated)','Sepsis. Anaphylaxis.\nNeurogenic (spinal injury).'],
    ['HYPOVOLAEMIC\n(Low Volume)','Not enough fluid\nin the circulation.','LOW','HIGH\n(vessels squeeze\nto compensate)','Haemorrhage. Burns.\nSevere vomiting/diarrhoea.'],
    ['CARDIOGENIC\n(Heart Failure)','The pump is broken.\nHeart cannot push\nblood out.','LOW','HIGH','Heart attack. Severe\nheart failure. Arrhythmia.'],
    ['OBSTRUCTIVE','Something physically\nblocking blood flow.','LOW','HIGH','PE. Cardiac tamponade.\nTension pneumothorax.'],
]
story.append(plain_table(shock_table,[CW*0.18,CW*0.28,CW*0.14,CW*0.16,CW*0.24]))

image_search_box('types of shock haemodynamic comparison cardiac output SVR', 'Google Images', story)
memory_hook('4 TYPES OF SHOCK: Distributive (vessels wide — sepsis). Hypovolaemic (not enough fluid). Cardiogenic (heart broken). Obstructive (blocked). SEPTIC = High output + LOW resistance.', story)
divider(story)

# ── §3 CAUSES OF SEPSIS ────────────────────────────────────────────────────────
sec_header('Section 3: Causes of Sepsis — What Infections Lead to Sepsis?', story)

professor_says('Any infection CAN cause sepsis. But certain infections are more likely. Know the common sources — this guides your antibiotic choice.', story)

causes_table = [
    ['Source','Common Organisms','Key Clinical Clue','MRCP Point'],
    ['Chest / Lungs\n(Pneumonia)\nMost common overall','Streptococcus pneumoniae.\nLegionella. Klebsiella.\nStaphylococcus aureus.','Cough. Sputum. Breathless.\nDull on percussion.\nReduced breath sounds.','Most common sepsis source in MRCP scenarios.\nCAP + sepsis = classic question.\nCURB-65 score measures severity.'],
    ['Urinary Tract\n(Urosepsis)','E. coli (most common).\nKlebsiella. Proteus.\nEnterococcus.','Burning urine. Frequency.\nLoin / flank pain.\nRigors (violent shaking).','Most common source in women + elderly.\nUrine dipstick positive.\nMSU culture confirms organism.'],
    ['Abdomen / GI\n(Gut / Biliary)','E. coli. Bacteroides.\nEnterococcus. Mixed bugs.','Abdominal pain. Vomiting.\nPeritonism. Jaundice.\nRecent abdominal surgery.','Ascending cholangitis:\nCharcot\'s triad = Fever + Jaundice\n+ RUQ pain = biliary sepsis.\nNeeds emergency ERCP.'],
    ['Skin / Soft Tissue\n(Cellulitis /\nNecrotising fasciitis)','Streptococcus.\nStaphylococcus. MRSA.\nMixed organisms in NF.','Red hot swollen skin.\nPain OUT OF PROPORTION\nto appearance = NF sign.\nCrepitus (crackling) under skin.','Necrotising fasciitis = surgical emergency.\nPain far worse than skin looks.\nImmediate surgery — do NOT wait.\nDo NOT give just antibiotics.'],
    ['CNS\n(Meningitis)','Neisseria meningitidis.\nStreptococcus pneumoniae.\nListeria (elderly/immunocomp).','Neck stiffness. Headache.\nPhotophobia (hates light).\nNon-blanching rash.','Non-blanching rash = meningococcaemia.\nGive IM benzylpenicillin 1.2g IMMEDIATELY.\nDo NOT wait for blood tests.\nEvery minute matters.'],
    ['IV Line / Catheter\n(Healthcare infection)','Staphylococcus aureus.\nS. epidermidis.\nCandida.','Fever after line insertion.\nTender red line site.\nRigors in hospital patient.','Always suspect line sepsis in\nhospitalised patient with unexplained fever.\nRemove the line. Send tip for culture.'],
]
story.append(plain_table(causes_table,[CW*0.16,CW*0.2,CW*0.28,CW*0.36]))

story.append(bp('<b>The Organisms — What You Need to Know:</b>'))
for pt in [
    '<b>Gram-negative bacteria</b> (E. coli, Klebsiella, Pseudomonas, Neisseria): Have outer layer called LPS (lipopolysaccharide / endotoxin). LPS is a powerful trigger of the immune cascade. Causes most severe sepsis.',
    '<b>Gram-positive bacteria</b> (Staphylococcus, Streptococcus, Enterococcus): Release exotoxins and peptidoglycan. Can cause equally severe sepsis.',
    '<b>MRSA</b> (Methicillin-Resistant Staphylococcus aureus): Hospital-acquired. Resistant to most antibiotics. Needs vancomycin or linezolid.',
    '<b>Candida</b> (a fungus): Causes sepsis in immunosuppressed patients, those on long antibiotic courses, ICU patients. Treat with fluconazole or caspofungin.',
]:
    story.append(bp(f'• {pt}'))

memory_hook('COMMON SEPSIS SOURCES: Chest (pneumonia). Urine (women/elderly). Abdomen (gut/biliary). Skin (necrotising fasciitis = surgical emergency). CNS (meningitis — non-blanching rash = penicillin IMMEDIATELY). IV line.', story)
divider(story)

# ── §4 PATHOPHYSIOLOGY ────────────────────────────────────────────────────────
sec_header('Section 4: Pathophysiology — How Does Infection Become Shock?', story)

professor_says('This section explains the mechanism. WHY do organs fail? Once you understand this, the treatment makes perfect sense. Do not skip this section — it is the heart of the topic.', story)

story.append(img_cascade)
story.append(bp('Sepsis Cascade — each step is more dangerous than the last', sImg))
story.append(Spacer(1,5))

story.append(bp('<b>Step 1: The Pathogen Enters</b>'))
story.append(bp('A pathogen (bacteria, virus, fungus) enters the body. It releases PAMPs — "enemy flags" the immune system recognises. Examples: LPS from gram-negative bacteria, peptidoglycan from gram-positive bacteria.'))
story.append(Spacer(1,3))

story.append(bp('<b>Step 2: Macrophages Sound the Alarm</b>'))
story.append(bp('Macrophages (MAK-ro-fay-jez) are the body\'s guard cells. They detect the enemy flags. They release cytokines (SIGH-to-kynes) — chemical messengers that say "DANGER — attack everywhere!"'))
story.append(bp('Main cytokines: <b>TNF-alpha, IL-1, IL-6, IL-8</b>. These spread in the bloodstream. They affect the whole body.'))
story.append(Spacer(1,3))

story.append(img_pathophys)
story.append(bp('How cytokines cause three simultaneous problems leading to shock', sImg))
story.append(Spacer(1,5))

story.append(bp('<b>Step 3: Three Deadly Events Happen at the Same Time</b>'))
story.append(Spacer(1,3))

story.append(bp('<b>3a. Vasodilation — blood vessels open too wide:</b>'))
story.append(bp('Cytokines tell the arteriole walls to RELAX. All blood vessels open wide. Blood flows in but cannot create enough pressure.'))
story.append(bp('Main chemical: <b>Nitric oxide (NO)</b> — released massively by the endothelium. Result: blood pressure drops sharply.'))
story.append(Spacer(1,3))

story.append(bp('<b>3b. Capillary Leak — fluid escapes from blood vessels:</b>'))
story.append(bp('Cytokines damage the tight junctions between endothelial cells. Fluid leaks from inside vessels into tissues.'))
story.append(bp('The patient looks swollen (oedema) but their blood vessels are EMPTY. This is why IV fluids are needed urgently.'))
story.append(Spacer(1,3))

story.append(bp('<b>3c. Myocardial Depression — the heart weakens:</b>'))
story.append(bp('Cytokines directly attack heart muscle. The heart contracts less forcefully. This is called septic cardiomyopathy.'))
story.append(bp('Partially reversible if the patient survives and the infection is treated.'))
story.append(Spacer(1,5))

story.append(bp('<b>Step 4: Tissue Hypoperfusion — organs stop getting blood</b>'))
story.append(bp('Hypoperfusion (HY-po-per-FEW-zhun) = low blood flow to organs. Cells run out of oxygen.'))
story.append(bp('Cells switch to anaerobic (without oxygen) energy production. This makes <b>lactic acid (lactate)</b>.'))
story.append(bp('<b>HIGH LACTATE = cells dying = organs failing.</b> Lactate >2 mmol/L = abnormal. >4 mmol/L = very high death risk.'))
story.append(Spacer(1,3))

story.append(bp('<b>Step 5: MODS — Multiple Organ Dysfunction Syndrome</b>'))
for pt in [
    '<b>Lungs</b> → ARDS (Acute Respiratory Distress Syndrome). Lungs fill with fluid. Cannot exchange oxygen. Patient needs ventilator.',
    '<b>Kidneys</b> → AKI (Acute Kidney Injury). Stop making urine. Creatinine rises. May need dialysis (kidney replacement).',
    '<b>Liver</b> → Jaundice. Raised bilirubin. Clotting problems (coagulopathy).',
    '<b>Brain</b> → Encephalopathy (en-KEFF-al-OPP-ath-ee). Confusion. Agitation. Reduced consciousness.',
    '<b>Blood</b> → DIC (Disseminated Intravascular Coagulation). Clotting everywhere. All clotting factors used up. Then bleeding everywhere.',
    '<b>Gut</b> → Ileus (bowel stops). Stress ulcers. Bacterial translocation (bacteria cross from gut into blood).',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1,4))

info_box('<b>DIC — Disseminated Intravascular Coagulation:</b> Clots form in tiny blood vessels throughout the body all at once. All clotting factors are used up. Now the patient bleeds everywhere too. Blood tests: LOW platelets + prolonged PT/APTT + LOW fibrinogen + HIGH D-dimer. Treatment: treat the underlying sepsis. Replace clotting factors with FFP (fresh frozen plasma), cryoprecipitate, and platelets.', story)

memory_hook('PATHOPHYSIOLOGY: Infection → Cytokines (TNF-alpha, IL-1, IL-6) → Vasodilation (nitric oxide) + Capillary leak + Cardiac depression → Low BP + Poor organ flow → Lactate rises → MODS. Lactate = marker of oxygen debt.', story)
divider(story)

# ── §5 CLINICAL FEATURES ──────────────────────────────────────────────────────
sec_header('Section 5: Clinical Features — What Does Sepsis Look Like?', story)

professor_says('The most important skill in sepsis is RECOGNISING IT EARLY. Many patients deteriorate for hours before anyone notices. You must know what to look for — from across the room.', story)

story.append(bp('<b>History — What the Patient Tells You:</b>'))
for pt in [
    '<b>Source symptoms:</b> Cough + sputum (chest). Burning urine + loin pain (urine). Abdominal pain + vomiting (gut). Red hot swollen skin (cellulitis). Headache + stiff neck (meningitis).',
    '<b>Fever or feeling cold:</b> High temperature (>38°C) OR low temperature (<36°C) — both are abnormal.',
    '<b>Rigors:</b> Violent uncontrollable shaking and shivering. Cannot stop it. Means bacteria are in the bloodstream. Classic sign of serious infection.',
    '<b>Confusion or strange behaviour:</b> Family notice this first. "He was fine this morning, now he does not know where he is." Confusion in an unwell patient = sepsis until proven otherwise.',
    '<b>Not passing urine:</b> Kidneys not getting enough blood. Oliguria (ol-IH-gyoo-ree-ah) = reduced urine output.',
    '<b>Feeling like dying:</b> Patients with severe sepsis often say they feel they are going to die. Take this seriously. It is a real symptom.',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1,5))

story.append(bp('<b>Examination — What You Find:</b>'))
exam_table = [
    ['Finding','What You See','What It Means','Threshold / Normal'],
    ['Temperature','Fever >38°C\nor Hypothermia <36°C','Fever = body fighting infection.\nHypothermia = immune system overwhelmed.\nHypothermia is WORSE than fever.','Normal: 36.5–37.5°C'],
    ['Heart Rate\n(Tachycardia)','Pulse >90 bpm.\nOften 110–130.\n>130 = very serious.','Heart beats faster to maintain BP\nas blood vessels dilate.','Normal: 60–100 bpm'],
    ['Blood Pressure\n(Hypotension)','Systolic <100 mmHg.\nMAP <65 mmHg = dangerous.\nBP 80/50 = critically low.','Vessels dilated. Heart cannot maintain\npressure. Organs are not being perfused.','Normal systolic: 110–140.\nNormal MAP: 70–100 mmHg.'],
    ['Respiratory Rate\n(Tachypnoea)','Rate >20/min.\nOften 25–35.\n>30 = very serious.','Lungs compensating for lactic acidosis.\nBrain also drives faster breathing\nwhen oxygen is low.','Normal: 12–20/min'],
    ['Skin','Early: warm, flushed.\nLate: cold, mottled (blotchy),\nclammy (cold + sweaty).','Mottling = very poor perfusion.\nSkin capillaries empty.\nCold + mottled = near-death sign.','Normal: warm, pink, dry.'],
    ['Capillary Refill\nTime (CRT)','Press fingernail 5 sec.\nCount until colour returns.','Normal <2 seconds.\n>2 sec = poor peripheral circulation\n= early shock sign.','Normal: <2 seconds'],
    ['Urine Output','<0.5 ml/kg/hour\n(oliguria)','Kidneys reducing urine to conserve\nfluid when BP is low.\nOliguria = early kidney injury.','Normal: 0.5–1 ml/kg/hour'],
    ['Consciousness','Confused. Agitated.\nDrowsy. Unresponsive.','Reduced brain perfusion.\nAny drop in consciousness\nin a sick patient = serious.','Normal: Alert, GCS 15'],
    ['Petechiae\n(peh-TEE-kee-ay)','Tiny dark red spots.\nDO NOT blanch when\npressed with a glass.','Blood leaked under skin.\nNon-blanching = meningococcal\nsepticaemia = EMERGENCY.','ABNORMAL — always urgent.'],
]
story.append(plain_table(exam_table,[CW*0.14,CW*0.23,CW*0.37,CW*0.26]))
story.append(Spacer(1,4))

alert_box('NON-BLANCHING RASH (petechiae/purpura) in a febrile patient = MENINGOCOCCAL SEPTICAEMIA. Do NOT wait for blood tests. Give IM/IV benzylpenicillin 1.2g IMMEDIATELY. Then transfer to hospital. Every minute of delay can cause death or limb loss.', story)

memory_hook('SEPSIS RED FLAGS: Temp <36 or >38. HR >90. RR >20. SpO2 <94%. SBP <100. Confused. Mottled cold skin. No urine. Any combination in an unwell patient = THINK SEPSIS. Start Sepsis-6 immediately.', story)
divider(story)

# ── §6 SCORING SYSTEMS ────────────────────────────────────────────────────────
sec_header('Section 6: Scoring Systems — qSOFA, SOFA, NEWS2', story)

professor_says('Scoring systems help you decide how sick the patient is. They are not perfect — but they give you a number to act on. The key is to use them FAST at the bedside.', story)

story.append(img_scoring)
story.append(bp('qSOFA (bedside, no tests) vs SOFA (ICU, needs labs)', sImg))
story.append(Spacer(1,5))

story.append(bp('<b>qSOFA (Quick SOFA) — The Bedside Screen:</b>'))
story.append(bp('You can calculate qSOFA in under 30 seconds. No blood tests needed. You just need your eyes and a blood pressure cuff.'))
story.append(Spacer(1,3))

qsofa_table = [
    ['Item','What to Measure','Abnormal Value','Points'],
    ['Respiratory Rate','Count breaths for 30 seconds. Double it.','>=22 breaths per minute','1'],
    ['Altered Consciousness','Ask orientation questions. Check GCS.','GCS < 15 (any confusion)','1'],
    ['Systolic Blood Pressure','Take BP with cuff.','<= 100 mmHg','1'],
]
story.append(plain_table(qsofa_table, [CW*0.22,CW*0.32,CW*0.28,CW*0.18]))
story.append(Spacer(1,3))

story.append(bp('Total maximum = 3. <b>Score 2 or more</b> = high risk of organ dysfunction = assess fully for sepsis = start treatment.'))
story.append(bp('Important: qSOFA is a SCREENING tool. A low score does NOT rule out sepsis. If you clinically think it is sepsis, treat it.'))
story.append(Spacer(1,5))

story.append(bp('<b>SOFA Score — The Full Organ Assessment:</b>'))
story.append(bp('SOFA = Sequential Organ Failure Assessment. Used in ICU. Needs blood tests. Measures organ dysfunction across 6 organ systems.'))
story.append(bp('<b>SEPSIS IS DEFINED AS: suspected infection + SOFA score increase of 2 or more points.</b>'))
story.append(Spacer(1,3))

sofa_table = [
    ['Organ System','What is Measured','Score 0 (normal)','Score 1','Score 2','Score 3-4 (worst)'],
    ['Lungs\n(Respiration)','PaO2/FiO2 ratio\n(oxygen level\nin blood ÷ oxygen\nbeing given)','> 400','300–400','200–300','< 200 (or < 100\nif on ventilator)'],
    ['Blood\n(Coagulation)','Platelet count\n(clotting cells\nin blood)','>150 x10^9/L','100–150','50–100','< 50'],
    ['Liver','Bilirubin level\n(yellow pigment —\nrises when liver\nis failing)','< 20 umol/L','20–32','33–101','> 101'],
    ['Heart\n(Cardiovascular)','MAP and vasopressor\nuse','MAP >= 65 mmHg','MAP < 65','Dopamine <= 5\nor dobutamine','Noradrenaline or\nhigh-dose dopamine'],
    ['Brain\n(CNS)','GCS\n(level of\nconsciousness)','GCS 15','GCS 13–14','GCS 10–12','GCS < 10'],
    ['Kidneys\n(Renal)','Creatinine and\nurine output','< 110 umol/L','110–170','171–299\nor UO < 0.5 ml/kg/hr','> 300 umol/L\nor UO < 0.3 ml/kg/hr'],
]
story.append(plain_table(sofa_table,[CW*0.14,CW*0.18,CW*0.15,CW*0.14,CW*0.18,CW*0.21]))
story.append(Spacer(1,4))

story.append(bp('<b>NEWS2 Score (National Early Warning Score 2) — Used in UK Wards:</b>'))
story.append(bp('NEWS2 is used on general hospital wards to detect deteriorating patients EARLY — before they become critically ill.'))
story.append(bp('It scores 6 observations: respiratory rate, oxygen saturation, supplemental oxygen, temperature, systolic BP, heart rate, and consciousness.'))
story.append(bp('<b>NEWS2 score 5 or more = escalate urgently. Score 7+ = consider ICU review.</b>'))
story.append(Spacer(1,3))

info_box('<b>MRCP Key Point — qSOFA vs SOFA:</b> qSOFA is the bedside SCREENING tool. SOFA is the formal DIAGNOSTIC criterion for sepsis. In the exam: if asked "how is sepsis defined?" — answer: suspected infection + SOFA increase ≥2. If asked "what quick bedside tool helps?" — answer: qSOFA score ≥2.', story)

memory_hook('qSOFA: RR >=22, Altered consciousness, SBP <=100. Score 2+ = suspect sepsis. SOFA: 6 organs scored 0-4 each. Increase 2+ = SEPSIS DEFINED. NEWS2: ward score for early deterioration. Score 5+ = escalate.', story)
divider(story)

# ── §7 INVESTIGATIONS ─────────────────────────────────────────────────────────
sec_header('Section 7: Investigations — What Tests Do We Do in Sepsis?', story)

professor_says('In sepsis, investigations serve three purposes: (1) Confirm there is an infection and how severe it is. (2) Find the SOURCE of infection. (3) Assess how much organ damage has already occurred.', story)

story.append(bp('<b>Immediate Bedside Tests (Do These First — Within Minutes):</b>'))
bedside_table = [
    ['Test','What It Measures','Result in Sepsis','Why Important'],
    ['Temperature','Core body temperature','Fever >38°C\nor Hypothermia <36°C','Confirms systemic response.\nHypothermia is a BAD sign.'],
    ['Heart rate\nBlood pressure\nRespiratory rate','Vital signs','All abnormal in sepsis\n(see clinical features)','Forms qSOFA score.\nGuides urgency.'],
    ['Oxygen Saturation\n(SpO2)','% of haemoglobin\ncarrying oxygen','Low in chest sepsis,\nARDS, or severe shock','Guide oxygen therapy.\nTarget SpO2 94–98%.'],
    ['Capillary glucose\n(BM)','Blood sugar level','May be HIGH (stress response)\nor LOW (especially in sepsis)','Hypoglycaemia worsens\nbrain injury. Treat if <4 mmol/L.'],
    ['Urine output\n(via catheter)','Volume of urine\nper hour','< 0.5 ml/kg/hour\n= oliguria','Reflects kidney perfusion.\nKey monitoring parameter.'],
    ['ECG','Heart rhythm\nand rate','Tachycardia.\nMay show AF\nor ischaemia in sepsis.','Sepsis can cause\narrhythmias and\ntroponin rise.'],
]
story.append(plain_table(bedside_table,[CW*0.18,CW*0.22,CW*0.25,CW*0.35]))
story.append(Spacer(1,6))

story.append(bp('<b>Blood Tests (Take All Together — One Venepuncture):</b>'))
blood_table = [
    ['Test','What It Shows','Expected in Sepsis','Clinical Significance'],
    ['FBC\n(Full Blood Count)','All blood cell counts','WBC raised >12 or very LOW <4\n(both abnormal).\nNeutrophilia. Bands (immature\nwhite cells) = "left shift".','Raised WBC = infection fighting.\nVery LOW WBC = immune system\noverwhelmed = very serious.\nThrombocytopaenia (low platelets) = DIC.'],
    ['CRP\n(C-Reactive Protein)','Inflammation marker\nmade by liver','Raised >10 mg/L.\nOften >100 in severe sepsis.\nVery high (>200) = severe.','Rises 6–12 hours after infection starts.\nSerial measurements show treatment response.\nFalling CRP = infection improving.'],
    ['Procalcitonin\n(PCT)','Protein released\nspecifically in\nbacterial infections','Raised in bacterial sepsis.\nNormal in viral infections.','More specific than CRP for bacterial infection.\nUseful for antibiotic DE-ESCALATION:\nIf PCT falls quickly, can stop antibiotics sooner.\nReduces antibiotic overuse.'],
    ['Blood Lactate','Lactic acid from\nanaerobic metabolism\n(oxygen-starved cells)','Normal < 2 mmol/L.\nSeptic shock definition:\n> 2 mmol/L after fluids.','KEY PARAMETER.\nLactate = oxygen debt marker.\n>2 = tissue hypoperfusion.\n>4 = very high mortality.\nFalling lactate = treatment working.'],
    ['U&E\n(Urea & Electrolytes)','Kidney function\nand electrolyte balance','Raised creatinine + urea\n(= AKI).\nHyperkalaemia in AKI.','Guides fluid therapy.\nMonitors for AKI.\nPotassium management critical.'],
    ['LFTs\n(Liver Function Tests)','Liver enzymes\nand bilirubin','Raised bilirubin.\nRaised ALT/AST.\nLow albumin.','Liver dysfunction in sepsis.\nLow albumin = severity marker.\nJaundice in biliary sepsis.'],
    ['Coagulation\n(PT, APTT, Fibrinogen,\nD-dimer)','Blood clotting ability','PT prolonged.\nAPTT prolonged.\nFibrinogen LOW.\nD-dimer VERY HIGH.\nPlatelets LOW.','This pattern = DIC.\nD-dimer alone not specific\n(raised in many conditions).'],
    ['Blood Cultures\nx 2 sets','Identify the exact\nbug causing infection','May be POSITIVE (bacteraemia)\nor NEGATIVE','Take BEFORE antibiotics if possible.\nDo NOT delay antibiotics for cultures.\nPositive culture guides antibiotic choice.'],
    ['Group & Save\n(G&S)','Blood group\n(pre-transfusion)','Routine','Prepare for possible\nblood products in severe sepsis.'],
    ['Troponin','Heart muscle damage','May be raised in sepsis\n(sepsis-induced cardiomyopathy)','Raised troponin in sepsis = poor prognosis.\nNot necessarily a heart attack.'],
    ['Blood glucose','Sugar in blood','May be high or low','Hyperglycaemia common\nin sepsis. Target 6–10 mmol/L\nwith insulin if needed.'],
    ['Arterial Blood Gas\n(ABG)','Oxygen. CO2. pH.\nBicarbonate. Lactate.','Metabolic acidosis\n(low pH, low bicarbonate).\nRaised lactate.\nLow PaO2.','ESSENTIAL in septic shock.\nShows degree of acidosis.\nGuides ventilator settings.\nConfirms lactate level.'],
]
story.append(plain_table(blood_table,[CW*0.17,CW*0.2,CW*0.27,CW*0.36]))
story.append(Spacer(1,6))

story.append(bp('<b>Urine Tests:</b>'))
for pt in [
    'Urine dipstick: leucocytes, nitrites, blood = UTI/urosepsis.',
    'MSU (midstream urine) for culture: identifies exact organism + antibiotic sensitivity.',
    'Urine output monitoring: via catheter, measured hourly.',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1,5))

story.append(bp('<b>Imaging — Finding the Source:</b>'))
imaging_table = [
    ['Test','When to Use','What It Shows'],
    ['Chest X-ray\n(CXR)','All patients with sepsis.\nFirst-line imaging.','Pneumonia (consolidation — white area).\nPleural effusion. Pulmonary oedema (ARDS). Pneumothorax.'],
    ['Ultrasound\n(USS Abdomen/Pelvis)','Suspected abdominal or\nbiliary source.','Gallstones. Bile duct dilation (cholangitis). Liver abscess. Renal abscess. Free fluid (perforation).'],
    ['CT Abdomen/Pelvis\n(with contrast)','When USS inconclusive.\nSuspected abdominal source.\nPost-surgical patient.','Gold standard for abdominal source identification. Shows abscesses, perforations, bowel ischaemia.'],
    ['CT Head','Altered consciousness.\nSuspected meningitis\nBEFORE lumbar puncture.','Exclude raised intracranial pressure before LP. If raised ICP and LP done = brain herniation = death.'],
    ['Echocardiogram\n(Echo)','Suspected endocarditis\nor cardiac dysfunction.','Heart valve vegetations (endocarditis).\nLV function (septic cardiomyopathy).\nPericardial effusion.'],
    ['Lumbar Puncture\n(LP)','Suspected meningitis.\nOnly if CT head normal\nand no signs of raised ICP.','CSF: white cells, protein, glucose, gram stain, culture. Confirms meningitis and identifies organism.'],
]
story.append(plain_table(imaging_table,[CW*0.2,CW*0.3,CW*0.5]))

info_box('<b>BLOOD CULTURES — Important Rules:</b> Take 2 sets from different sites (or one peripheral + one from central line). Each set = one aerobic bottle + one anaerobic bottle. Take BEFORE antibiotics if possible — but do NOT delay antibiotics more than 45 minutes waiting for cultures. Positive blood culture = bacteraemia (bacteria in the blood) = adjust antibiotics to the sensitivity result (de-escalate).', story)

memory_hook('KEY INVESTIGATIONS IN SEPSIS: Blood cultures x2 (before antibiotics). Lactate (>2 = bad). FBC + CRP + Procalcitonin. ABG (acid-base). U&E + LFTs + Coagulation. Urine dipstick + MSU. CXR. Then image to find source (USS/CT). LACTATE IS THE MOST IMPORTANT SINGLE RESULT.', story)
divider(story)

# ── §8 MANAGEMENT — SEPSIS-6 AND RESUSCITATION ───────────────────────────────
sec_header('Section 8: Management — The Sepsis-6 Bundle and Resuscitation', story)

professor_says('The treatment of sepsis is TIME CRITICAL. The Sepsis-6 bundle must be started within ONE HOUR of recognition. Think of it as a fire alarm — when it goes off, everyone acts at the same time, not one thing after another.', story)

story.append(img_sepsis6)
story.append(bp('Sepsis-6 Bundle: 3 Give + 3 Take — all within 1 hour of recognition', sImg))
story.append(Spacer(1,5))

story.append(bp('<b>The Sepsis-6 Bundle — Detailed Explanation:</b>'))
s6_table = [
    ['Action','Exactly What to Do','Why','Target'],
    ['1. Give HIGH-FLOW\nOXYGEN','15L/min via non-rebreathe mask.\nTitrate down once stable.','Correct hypoxia.\nSupport failing organs.\nSeptic cells need more oxygen.','SpO2 94–98%\n(88–92% in COPD)'],
    ['2. Give IV FLUID\nBOLUS','30 ml/kg IV crystalloid\n(usually 500ml bolus first,\nthen reassess).\nHartmann\'s or Normal Saline.','Correct hypovolaemia from\ncapillary leak and vasodilation.\nRestore organ perfusion pressure.','MAP >= 65 mmHg.\nUrine output\n>= 0.5 ml/kg/hr.'],
    ['3. Give IV\nANTIBIOTICS','Broad-spectrum empirical\nantibiotics WITHIN 1 HOUR.\nChoice guided by source\n(see §9).','Kill the causative organism.\nEvery hour of delay = 7% more\nmortality in septic shock.','Within 1 hour of\nrecognition. No delay.'],
    ['4. Take BLOOD\nCULTURES','2 sets (aerobic + anaerobic).\nFrom 2 different sites.\nBEFORE antibiotics if possible.','Identify exact organism.\nGuide antibiotic de-escalation\nlater.\nAvoid antibiotic resistance.','Before antibiotics.\nDo NOT delay antibiotics\n>45 min waiting for cultures.'],
    ['5. Measure\nBLOOD LACTATE','Arterial blood gas (ABG)\nor venous sample.\nRepeat at 2 hours.','Lactate = tissue oxygen debt.\nShows severity.\nFalling lactate = responding.','Target: lactate\n< 2 mmol/L.\nTrend is key.'],
    ['6. Measure URINE\nOUTPUT','Insert urinary catheter.\nMeasure urine hourly.','Urine output = kidney perfusion.\nOliguria = kidney failing.\nGuides fluid management.','Target >= 0.5 ml/kg/hr.\nMonitor strictly hourly.'],
]
story.append(plain_table(s6_table,[CW*0.2,CW*0.3,CW*0.28,CW*0.22]))
story.append(Spacer(1,5))

story.append(bp('<b>Fluid Resuscitation — Details:</b>'))
for pt in [
    '<b>Initial bolus:</b> 500ml crystalloid (Hartmann\'s or normal saline) over 15 minutes. Reassess after each bolus.',
    '<b>Total volume:</b> Up to 30ml/kg in the first 3 hours (e.g. 2100ml for a 70kg patient).',
    '<b>Reassess after EACH bolus:</b> Has BP improved? Is urine output better? Are there signs of fluid overload (crackles in lungs, worsening oxygen)?',
    '<b>Hartmann\'s solution preferred</b> over large volumes of normal saline — avoids hyperchloraemic acidosis.',
    '<b>If fluids do not fix BP:</b> Start vasopressors. Noradrenaline is first choice.',
    '<b>Fluid overload is dangerous:</b> Too much fluid causes pulmonary oedema (fluid in lungs) and worsens ARDS. Dynamic fluid responsiveness tests (passive leg raising) guide further fluids.',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1,5))

story.append(bp('<b>Vasopressors — When Fluids Are Not Enough:</b>'))
story.append(bp('If MAP remains <65 mmHg despite adequate fluid resuscitation, the patient needs vasopressors. Vasopressors are drugs that make blood vessels tighten — raising blood pressure.'))
story.append(Spacer(1,3))

vasopressor_table = [
    ['Drug','Mechanism','Dose','When Used','Key Points'],
    ['Noradrenaline\n(Norepinephrine)\n— FIRST LINE','Alpha-1 agonist.\nConstricts blood vessels.\nRaises vascular resistance.\nSome beta-1 (mild heart effect).','Start 0.01–0.3 mcg/kg/min IV.\nTitrate to MAP >= 65.','FIRST-LINE vasopressor\nin septic shock.\nGiven via CENTRAL LINE.','Causes peripheral\nvasoconstriction.\nDo NOT give peripherally\n(causes tissue necrosis).\nNeeds central venous access.'],
    ['Vasopressin\n(ADH)','Acts on V1 receptors\nin blood vessels.\nCauses vasoconstriction\nindependently of\ncatecholamine receptors.','0.03 units/min IV\n(fixed dose).','Added to noradrenaline\nwhen not achieving\nMAP target on\nnoradrenaline alone.','Can reduce noradrenaline\nrequirement. Does not\ncause tachycardia.\nUsed as second-line add-on.'],
    ['Adrenaline\n(Epinephrine)','Alpha + Beta agonist.\nBoth vasoconstriction\nand cardiac stimulation.','0.01–1 mcg/kg/min.','Refractory septic shock\nnot responding to\nnoradrenaline.\nAnaphylaxis (first line).','Increases heart rate\nand force. Can cause\narrhythmias. Raises\nblood lactate (not\nreflecting true worsening).'],
    ['Dobutamine','Beta-1 agonist.\nIncreases heart contractility\nand cardiac output.\nMild vasodilation.','2.5–20 mcg/kg/min.','Added when cardiac\noutput is LOW despite\nadequate filling (septic\ncardiomyopathy).','Does NOT raise BP\ndirectly — raises\ncardiac output.\nUsed alongside\nnoradrenaline.'],
]
story.append(plain_table(vasopressor_table,[CW*0.16,CW*0.22,CW*0.15,CW*0.22,CW*0.25]))

info_box('<b>Hour-1 Bundle (Surviving Sepsis Campaign 2018):</b> In SEPTIC SHOCK (lactate >2 mmol/L OR sepsis with high suspicion), the entire Sepsis-6 must be completed within 1 hour. This is more aggressive than the old 3-hour and 6-hour bundles. Evidence shows that 1-hour completion reduces mortality. Time from recognition to antibiotics is the most critical single factor.', story)

memory_hook('SEPSIS-6: 3 GIVE = Oxygen + IV Fluids + IV Antibiotics. 3 TAKE = Blood Cultures + Lactate + Urine Output. ALL WITHIN 1 HOUR. Vasopressors if MAP <65 despite fluids. Noradrenaline = first-line vasopressor. Target MAP >= 65 mmHg.', story)
divider(story)

# ── §9 ANTIBIOTICS AND SOURCE CONTROL ────────────────────────────────────────
sec_header('Section 9: Antibiotics and Source Control', story)

professor_says('The right antibiotic, given fast, saves lives. The wrong antibiotic, given late, kills. Start broad, then narrow when you have culture results. And always ask: can we REMOVE the source of infection?', story)

story.append(bp('<b>Empirical Antibiotic Choice — By Source:</b>'))
story.append(bp('Empirical (em-PEER-ih-kul) means you are guessing the bug based on the likely source. You do not yet have culture results. Choose antibiotics that cover the most likely organisms.'))
story.append(Spacer(1,3))

ab_table = [
    ['Suspected Source','First-Line Empirical Antibiotics','Alternative (Penicillin Allergy)','Notes'],
    ['Unknown source\n(no clear focus)','Piperacillin-tazobactam\n(Tazocin) 4.5g IV every 8h\n+/- Vancomycin if MRSA risk','Meropenem 1g IV every 8h\n+ Vancomycin','Broadest cover.\nAdd vancomycin if:\nline infection, recent\nhospital, MRSA known.'],
    ['Chest\n(Pneumonia-CAP)','Co-amoxiclav 1.2g IV tds\n+ Clarithromycin 500mg IV bd\n(covers atypicals: Legionella,\nMycoplasma)','Levofloxacin 500mg IV od\n(covers all CAP organisms)','Add oseltamivir (Tamiflu)\nif influenza suspected.\nSARS-CoV-2: follow\ncurrent guidelines.'],
    ['Urinary Tract\n(Urosepsis)','Cefuroxime 1.5g IV tds\nOR\nCo-amoxiclav 1.2g IV tds','Ciprofloxacin 400mg IV bd\n(if allergy confirmed)\n+ Gentamicin if severe','Simple UTI: oral antibiotics.\nSevere urosepsis: IV.\nAdjust when culture back.'],
    ['Abdomen / GI\n(Gut/Biliary)','Piperacillin-tazobactam\n(Tazocin) 4.5g IV every 8h\n(covers gram-neg + anaerobes)','Meropenem + Metronidazole','Perforated bowel: needs\nsurgery + antibiotics.\nCholangitis: needs ERCP\nor biliary drainage urgently.'],
    ['Skin / Soft Tissue\n(Cellulitis)','Co-amoxiclav 1.2g IV tds\n+ Flucloxacillin 1–2g IV qds\n(adds Staph coverage)','Vancomycin 15-20mg/kg\nevery 12h (MRSA cover)','Necrotising fasciitis:\nMeropenem + Clindamycin\n+ Vancomycin.\nPLUS URGENT SURGERY.'],
    ['CNS\n(Meningitis)','Ceftriaxone 2g IV every 12h\n+ Dexamethasone 0.15mg/kg\nevery 6h x 4 days','Chloramphenicol 25mg/kg IV\nevery 6h (if penicillin\nallergy — discuss with micro)','Give dexamethasone WITH\nfirst dose of antibiotic.\nReduces deafness and\nbrain damage in bacterial\nmeningitis.'],
    ['Line infection\n(CRBSI)','Vancomycin 15-20mg/kg\nevery 12h\n+ REMOVE the line','Teicoplanin or Daptomycin\n(if vancomycin not tolerated)','Always remove or replace\nthe infected line.\nSend line tip for culture.'],
    ['Neutropenic Sepsis\n(WBC very low due to\nchemotherapy)','Piperacillin-tazobactam\n(Tazocin) 4.5g IV every 8h\nIMMEDIATELY + URGENTLY','Meropenem if high risk\nor local resistance patterns','Add antifungal (caspofungin)\nif no response after 48h.\nHaematology team input.\nVERY HIGH MORTALITY IF DELAYED.'],
]
story.append(plain_table(ab_table,[CW*0.17,CW*0.28,CW*0.25,CW*0.3]))
story.append(Spacer(1,5))

story.append(bp('<b>Antibiotic De-escalation — Narrowing Down After 48–72 Hours:</b>'))
for pt in [
    '<b>Review at 48–72 hours:</b> Blood culture and sensitivity results should be back. Narrow antibiotics to the most targeted choice that covers the identified organism.',
    '<b>Procalcitonin (PCT) guidance:</b> If PCT is falling rapidly, antibiotics can often be stopped earlier. Studies show PCT-guided de-escalation reduces antibiotic exposure without worsening outcomes.',
    '<b>IV to oral switch:</b> Once patient is improving, switch from IV to oral antibiotics as soon as they can swallow and absorb tablets.',
    '<b>Duration:</b> Most uncomplicated bacterial sepsis = 5–7 days. Endocarditis = 4–6 weeks. Meningitis = 10–14 days. Neutropenic sepsis = until neutrophils recover.',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1,5))

story.append(bp('<b>Source Control — Removing the Focus of Infection:</b>'))
professor_says('Antibiotics kill bacteria. But if there is a bag of pus (abscess) or a dead piece of tissue, antibiotics CANNOT reach it. You must remove or drain the source. Antibiotics alone are not enough.', story)

source_table = [
    ['Source','Source Control Action','Timing'],
    ['Infected IV line\nor urinary catheter','Remove the line or catheter.\nInsert new one at different site.','Immediately on suspicion.'],
    ['Abscess\n(collection of pus)','Percutaneous drainage by\nradiologist (CT/USS guided)\nor surgical drainage.','As soon as possible.\nAntibiotics alone will not clear\na walled-off abscess.'],
    ['Perforated bowel\nor appendicitis','Emergency surgery to repair\nthe perforation and wash\nout the abdomen.','Emergency — within hours.'],
    ['Biliary obstruction\n(cholangitis)','ERCP (endoscopic procedure\nto drain the bile duct)\nor percutaneous biliary drain.','Urgent — within 24 hours\nfor severe cholangitis.'],
    ['Necrotising fasciitis','Urgent surgical debridement\n(cutting away all infected\nand dead tissue). Extensive.','EMERGENCY — minutes to hours.\nEvery hour increases mortality.'],
    ['Endocarditis\n(heart valve infection)','Medical: 4–6 weeks antibiotics.\nSurgical valve replacement\nif: large vegetation, heart\nfailure, embolic events.','Surgery when indicated\n(discuss with cardiology\nand cardiothoracic surgery).'],
]
story.append(plain_table(source_table,[CW*0.22,CW*0.48,CW*0.3]))

alert_box('NECROTISING FASCIITIS: Do NOT give antibiotics alone and wait. This infection spreads along the fascia (the tissue layer under skin) at a rate of 1cm per hour. The only treatment is emergency surgical debridement. Any delay = more tissue lost = higher mortality. Classic sign: pain far WORSE than the skin appearance suggests.', story)

memory_hook('ANTIBIOTICS: Start broad (Tazocin for unknown source). Add vancomycin if MRSA risk. Narrow at 48-72h when cultures back. De-escalate with procalcitonin guidance. SOURCE CONTROL = drain abscess / remove line / surgery. Antibiotics + source control = together. Neither alone is enough.', story)
divider(story)

# ── §10 ORGAN SUPPORT AND ICU CARE ───────────────────────────────────────────
sec_header('Section 10: Organ Support — ICU Management', story)

professor_says('When organs fail, we need machines and drugs to support them while the antibiotics and the patient\'s immune system fight the infection. This is ICU care. Each organ has its own support strategy.', story)

organ_support_table = [
    ['Failing Organ','Problem','Support Given','Key Points'],
    ['Lungs\n(ARDS)','Lungs fill with fluid.\nCannot exchange oxygen.\nRefractory hypoxia.','Mechanical ventilation\n(ventilator machine breathes\nfor the patient).\nHigh PEEP settings.\nLow tidal volumes\n(6 ml/kg ideal body weight).','ARDS NET protocol:\nLow tidal volume ventilation\nreduces mortality.\nAvoid high pressures.\nProne (face down) ventilation\nfor severe ARDS — improves oxygenation.'],
    ['Kidneys\n(AKI)','Creatinine rising.\nNot making urine.\nFluid overload.\nHyperkalaemia.','Renal Replacement\nTherapy (RRT) = dialysis\nin ICU (CVVHF —\ncontinuous filtration).','Start RRT when:\nSevere fluid overload,\nRaising potassium,\nSevere acidosis,\nUraemic complications.\nDialysis is a BRIDGE — most\npatients recover kidney function\nif they survive sepsis.'],
    ['Heart\n(Septic Cardiomyopathy)','Weak heart muscle.\nLow cardiac output.\nNot pumping enough.','Dobutamine infusion\n(2.5–20 mcg/kg/min)\nto increase contractility.\nDo NOT use beta-blockers\n(these reduce heart contractility).','Echo monitors heart function.\nTroponin rise expected.\nMost recover cardiac function\nif infection treated.'],
    ['Brain\n(Encephalopathy)','Confusion.\nAgitation.\nDelirium.','Stop sedatives early\nif possible.\nAvoid benzodiazepines\n(worsen delirium).\nDexmedetomidine if\nsedation needed.\nNightly sedation breaks.','Sepsis encephalopathy\nis REVERSIBLE if infection\ntreated. Regular orientation.\nNoise/light reduction.\nMobilise early.'],
    ['Blood\n(DIC)','Bleeding + clotting\nat same time.\nAll clotting factors\nused up.','Treat underlying sepsis.\nFFP (Fresh Frozen Plasma)\nfor clotting factors.\nCryoprecipitate for\nfibrinogen.\nPlatelet transfusion if\n<50 x10^9/L + bleeding.','Heparin NOT routinely\nused in septic DIC.\nTreat the source —\nDIC improves when\ninfection is controlled.'],
    ['Glucose\n(Hyperglycaemia)','Stress response raises\nblood sugar.\nHigh glucose worsens\noutcomes.','Insulin infusion.\nTarget blood glucose\n6–10 mmol/L.','Do NOT target normal glucose\n(4–6) — increases hypoglycaemia\nrisk in ICU.\nCheck glucose every 1–2 hours.'],
    ['Gut\n(Stress Ulcers)','Gut mucosa damaged\nby poor perfusion.\nRisk of upper GI\nbleeding.','Proton pump inhibitor\n(e.g. omeprazole 40mg IV\nor oral once daily).\nEnteral nutrition early\n(feeding via nasogastric tube).','Early enteral (gut) nutrition\nprotects gut mucosa.\nImproves gut immune function.\nStart within 24–48 hours\nof ICU admission.'],
]
story.append(plain_table(organ_support_table,[CW*0.14,CW*0.2,CW*0.28,CW*0.38]))
story.append(Spacer(1,5))

story.append(bp('<b>Corticosteroids in Septic Shock:</b>'))
story.append(bp('In refractory septic shock (patient still needs high doses of vasopressors despite adequate fluids and antibiotics), hydrocortisone may help.'))
steroid_table = [
    ['Drug','Dose','When to Use','Evidence','Side Effects'],
    ['Hydrocortisone','200 mg/day IV\n(50mg IV every 6h\nor 200mg continuous\n24h infusion)','REFRACTORY septic shock:\nNot achieving MAP >= 65\ndespite adequate fluids\n+ vasopressors\n(noradrenaline > 0.25\nmcg/kg/min).','APROCCHSS trial (2018):\nHydrocortisone + fludrocortisone\nreduced 90-day mortality.\nADRESSS trial: less clear.\nCurrent guideline: use in\nrefractory shock.','Hyperglycaemia (most common).\nSuperinfection (secondary\ninfection) risk.\nGI bleeding. Weak muscles.'],
]
story.append(plain_table(steroid_table,[CW*0.12,CW*0.2,CW*0.25,CW*0.25,CW*0.18]))
story.append(Spacer(1,4))

info_box('<b>MRCP Key Point — Steroids in Sepsis:</b> Hydrocortisone is used ONLY in REFRACTORY septic shock (still needing high-dose vasopressors despite fluids + antibiotics). It is NOT given routinely to all sepsis patients. The mechanism: sepsis causes relative adrenal insufficiency — cortisol levels are insufficient despite high ACTH. Hydrocortisone replaces the deficient cortisol.', story)

memory_hook('ICU ORGAN SUPPORT: Lungs = ventilator (low tidal volume 6ml/kg). Kidneys = CVVHF dialysis. Heart = dobutamine. Blood = FFP + cryoprecipitate + platelets for DIC. Glucose = insulin (target 6–10 mmol/L). Gut = PPI + early enteral feeding. Steroids (hydrocortisone) = ONLY in refractory shock on high vasopressors.', story)
divider(story)

# ── §11 COMPLICATIONS ─────────────────────────────────────────────────────────
sec_header('Section 11: Complications of Sepsis', story)

professor_says('Sepsis damages every organ in the body. The complications are the result of that damage. Some are reversible. Some are not. Knowing them helps you monitor the patient and recognise deterioration.', story)

comp_table = [
    ['Complication','What Happens','Signs + Tests','Treatment'],
    ['ARDS\n(Acute Respiratory\nDistress Syndrome)','Lungs fill with inflammatory\nfluid. Oxygen cannot cross\nthe damaged membrane.\nNot due to heart failure.','SpO2 low. CXR: bilateral\nwhite fluffy shadows.\nABG: low PaO2/FiO2 ratio < 200.\nNo raised JVP/heart failure.','Mechanical ventilation.\nLow tidal volumes.\nProne positioning.\nAvoid excess fluids.'],
    ['AKI\n(Acute Kidney Injury)','Poor blood flow to kidneys.\nDirect cytokine damage.\nNephrotoxic antibiotics\n(gentamicin, vancomycin).','Rising creatinine.\nRising urea.\nFalling urine output.\nHyperkalaemia.','IV fluids to restore\nkidney perfusion.\nStop nephrotoxic drugs.\nRRT (dialysis) if severe.'],
    ['DIC\n(Disseminated Intravascular\nCoagulation)','Clotting everywhere at once.\nAll clotting factors\nconsumed. Then bleeding.','Low platelets. Prolonged PT.\nLow fibrinogen. Very high\nD-dimer. Bleeding from\nmultiple sites.','Treat infection (remove cause).\nReplace clotting factors:\nFFP + cryoprecipitate + platelets.'],
    ['Septic Cardiomyopathy\n(Heart dysfunction)','Cytokines weaken\nheart muscle.\nLow cardiac output\ndespite vasopressors.','Echo: low ejection fraction.\nRaised troponin.\nSigns of low output (cold\nperipheries, rising lactate).','Dobutamine infusion.\nAvoid excess fluids\n(worsens low output heart).\nUsually reversible.'],
    ['Hepatic dysfunction\n(Liver failure)','Reduced liver blood\nflow + direct toxin\ndamage.','Raised bilirubin (jaundice).\nRaised ALT/AST.\nLow albumin.\nCoagulopathy (raised PT).','Treat infection.\nAvoiding hepatotoxic drugs.\nNutritional support.\nRarely needs specific treatment.'],
    ['Encephalopathy\n(Brain dysfunction)','Poor brain perfusion.\nInflammatory mediators\ncross blood-brain barrier.','Confusion. Delirium.\nAgitation. Reduced GCS.\nAbnormal EEG.','Treat infection.\nMinimise sedation.\nDelirium prevention bundle.\nUsually fully reversible.'],
    ['Ileus\n(Bowel stops working)','Cytokines paralyse\nbowel smooth muscle.','No bowel sounds.\nAbdominal distension.\nNausea. Cannot absorb feeds.','NG tube decompression.\nProkinetics (metoclopramide).\nEarly enteral feeding.\nCorrect electrolytes (K+, Mg2+).'],
    ['Adrenal Insufficiency\n(Relative)','Adrenal glands cannot\nproduce enough cortisol\ndespite high ACTH\n(stress hormone).','Refractory hypotension.\nHyponatraemia.\nHypoglycaemia.\nHigh potassium.','Hydrocortisone 200mg/day.\n(See §10 steroids section.)'],
    ['Long-term effects\nof sepsis survivorship','After surviving sepsis:\ncognitive impairment,\nchronic fatigue, PTSD,\nmuscle weakness.','Identified months after\ndischarge — memory,\nconcentration, mood.','Rehabilitation.\nPsychological support.\n"Post-sepsis syndrome"\nis increasingly recognised.'],
]
story.append(plain_table(comp_table,[CW*0.18,CW*0.25,CW*0.27,CW*0.3]))

memory_hook('SEPSIS COMPLICATIONS: ARDS (lungs fail). AKI (kidneys fail). DIC (bleed + clot). Cardiomyopathy (heart weakens). Hepatic dysfunction. Encephalopathy. Ileus. Adrenal insufficiency. Long-term: cognitive impairment, fatigue, PTSD.', story)
divider(story)

# ── §12 SPECIAL SITUATIONS ───────────────────────────────────────────────────
sec_header('Section 12: Special Situations in Sepsis', story)

professor_says('Certain groups of patients present with sepsis differently, or require special management. These are high-yield MRCP topics.', story)

story.append(bp('<b>Neutropenic Sepsis (Febrile Neutropaenia) — Cancer Patients on Chemotherapy:</b>'))
for pt in [
    '<b>Definition:</b> Neutrophil count <0.5 × 10⁹/L (very low infection-fighting cells) + temperature >38°C (or clinical sepsis signs).',
    '<b>Why dangerous:</b> Neutrophils are the main defence against bacterial infection. Without them, minor infections become rapidly fatal. No neutrophils = no natural defence.',
    '<b>Presentation:</b> Often NO localising symptoms. Just fever, malaise, sometimes a cough or sore throat. The patient may look deceptively well but deteriorate within hours.',
    '<b>Management:</b> Piperacillin-tazobactam (Tazocin) 4.5g IV every 8 hours IMMEDIATELY — within 1 hour of triage. No delay. Add vancomycin if line infection suspected. Add antifungal (caspofungin) if fever persists >48–72 hours despite antibiotics.',
    '<b>G-CSF (Granulocyte Colony-Stimulating Factor):</b> Can stimulate the bone marrow to produce more neutrophils faster. Used in severe or prolonged neutropaenia.',
    '<b>Isolation:</b> Reverse barrier nursing — protect the patient FROM the environment, not the other way around.',
    '<b>MRCP point:</b> Neutropenic sepsis is an ONCOLOGICAL EMERGENCY. Any cancer patient on chemotherapy with a fever must receive antibiotics within 1 hour, regardless of the time of day.',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1,5))

story.append(bp('<b>Meningococcal Septicaemia — The Non-Blanching Rash Emergency:</b>'))
for pt in [
    '<b>Organism:</b> Neisseria meningitidis — a gram-negative diplococcus (round bacteria in pairs). Spread by droplets. Young people, students, and crowded living most at risk.',
    '<b>Types:</b> Group B most common in UK. Group C (and ACWY) vaccine-preventable.',
    '<b>Classic presentation:</b> Young person. Sudden severe headache. Fever. Neck stiffness. Non-blanching petechial or purpuric rash. Can progress from mild fever to death within 24 hours.',
    '<b>The glass test:</b> Press a glass firmly against the rash. If spots DO NOT go white (do not blanch) = petechiae or purpura = blood under the skin = possible meningococcaemia.',
    '<b>Immediate action:</b> IM or IV benzylpenicillin 1.2g IMMEDIATELY — before transfer to hospital. If penicillin allergy: cefotaxime. This is one of the few situations where antibiotics are given BEFORE admission.',
    '<b>In hospital:</b> Ceftriaxone 2g IV every 12 hours. Blood cultures + LP (after CT head if signs of raised ICP). Supportive ICU care.',
    '<b>Complications:</b> Waterhouse-Friderichsen syndrome = bilateral adrenal haemorrhage due to DIC → adrenal insufficiency → cardiovascular collapse. Requires hydrocortisone.',
    '<b>Contacts:</b> Close contacts should receive ciprofloxacin or rifampicin prophylaxis within 24 hours to prevent secondary cases.',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1,5))

story.append(bp('<b>Toxic Shock Syndrome (TSS):</b>'))
for pt in [
    '<b>What it is:</b> A specific type of septic shock caused by exotoxins (superantigens) released by Staphylococcus aureus or Streptococcus pyogenes.',
    '<b>Staphylococcal TSS:</b> Associated with retained tampons, nasal packing, surgical wounds. TSST-1 toxin activates huge numbers of T cells (polyclonal T cell activation) → massive cytokine release → shock.',
    '<b>Streptococcal TSS:</b> Associated with necrotising fasciitis or invasive Streptococcal infection. More severe. Higher mortality.',
    '<b>Features:</b> High fever. Diffuse sunburn-like rash. Low BP. Multi-organ failure. Desquamation (skin peeling) 1–2 weeks later.',
    '<b>Treatment:</b> Remove source (e.g. tampon). IV fluids. Flucloxacillin or vancomycin + clindamycin. Clindamycin is important — it inhibits toxin production (protein synthesis inhibitor) even though the bacteria may be resistant to it.',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1,5))

story.append(bp('<b>Sepsis in the Elderly — Atypical Presentation:</b>'))
for pt in [
    'Elderly patients do NOT always have fever. They may be HYPOTHERMIC. They may have only confusion as the presenting feature.',
    'Any unexplained acute confusion in an elderly patient = assume infection/sepsis until proven otherwise.',
    'Common sources in elderly: UTI (most common), pneumonia, pressure ulcer, bowel source.',
    'Higher mortality than younger patients due to reduced physiological reserve and multiple comorbidities.',
    'Be cautious with fluids — elderly hearts may not tolerate large boluses. Avoid fluid overload.',
]:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1,5))

story.append(bp('<b>Sepsis in Pregnancy:</b>'))
for pt in [
    'Chorioamnionitis (uterine infection), urinary tract infection, and post-partum endometritis are the most common sources.',
    'Normal pregnancy changes: WBC is normally raised (up to 15,000), heart rate is normally faster, blood pressure normally lower. These changes make sepsis harder to recognise.',
    'Group A Streptococcus (Streptococcus pyogenes) is the most dangerous organism in pregnancy — can cause rapidly fatal sepsis.',
    'Any pregnant or recently delivered woman with fever + rigors + abdominal pain = obstetric emergency.',
    'NEWS2 is NOT validated in pregnancy. Use obstetric-specific early warning scores (MEOWS).',
]:
    story.append(bp(f'• {pt}'))

alert_box('WATERHOUSE-FRIDERICHSEN SYNDROME: Bilateral adrenal haemorrhage in meningococcal septicaemia. Caused by DIC destroying the adrenal glands. Signs: sudden cardiovascular collapse, purpuric rash, adrenal insufficiency. Treatment: IV hydrocortisone 100mg STAT + resuscitation. Very high mortality.', story)

memory_hook('SPECIAL SITUATIONS: Neutropenic sepsis = Tazocin within 1 hour (no delay — oncological emergency). Meningococcal = benzylpenicillin IM IMMEDIATELY + glass test. TSS = clindamycin inhibits toxin production. Elderly = hypothermia + confusion (not always fever). Pregnancy = Group A Strep most dangerous.', story)
divider(story)

# ── §13 PHARMACOLOGY ─────────────────────────────────────────────────────────
sec_header('Section 13: Pharmacology — Key Drugs in Sepsis Management', story)

professor_says('You need to know the drugs by name, mechanism, dose, and when to use them. This section covers everything from antibiotics to vasopressors to supportive drugs.', story)

pharm_table = [
    ['Drug','Class / Mechanism','Dose','Key Clinical Notes'],
    ['Noradrenaline\n(Norepinephrine)','Sympathomimetic.\nAlpha-1 agonist:\nconstricts blood vessels.\nBeta-1: mild cardiac\nstimulation.','Start 0.01 mcg/kg/min IV.\nTitrate up to 0.3–1\nmcg/kg/min to\nachieve MAP >= 65.','FIRST-LINE vasopressor.\nMust give via CENTRAL LINE\n(peripheral = tissue necrosis).\nMonitor BP continuously (arterial line).'],
    ['Vasopressin\n(ADH)','Acts on V1 vascular\nreceptors → vasoconstriction\nindependently of\nadrenergic receptors.','0.03 units/min\n(fixed dose)\nIV infusion.','Second-line — added to\nnoradrenaline when not\nat MAP target.\nDoes NOT increase heart rate.\nSpare noradrenaline dose.'],
    ['Dobutamine','Beta-1 agonist.\nIncreases heart rate\nand contractility.\nMild vasodilation.','2.5–20 mcg/kg/min\nIV infusion.','Add when cardiac output LOW\ndespite adequate filling.\nDoes NOT raise BP — raises\ncardiac output.\nCan cause tachyarrhythmias.'],
    ['Hydrocortisone','Glucocorticoid.\nAnti-inflammatory.\nReplaces deficient\ncortisol in adrenal\ninsufficiency of sepsis.','200 mg/day IV.\n50mg IV every 6h\nor 200mg/24h\ncontinuous infusion.','Only in REFRACTORY septic\nshock on high vasopressors.\nCause: relative adrenal insufficiency.\nSide effects: hyperglycaemia,\nimmune suppression, GI bleeding.'],
    ['Piperacillin-\nTazobactam\n(Tazocin)','Extended-spectrum penicillin\n+ beta-lactamase inhibitor.\nKills gram-positive,\ngram-negative, AND\nanaerobes.','4.5g IV every 8h\n(every 6h in\nsevere sepsis\nor Pseudomonas).','Broad-spectrum — for unknown\nsource or abdominal sepsis.\nSodium load — caution in\nheart failure. Adjust\nfor renal impairment.'],
    ['Meropenem','Carbapenem antibiotic.\nKills almost all bacteria\nincluding resistant\norganisms.\nInhibits cell wall synthesis.','1g IV every 8h\n(2g if meningitis\nor severe infection).','Reserve for severe sepsis,\nresistant organisms, or\nfailure of other antibiotics.\nAntimicrobial stewardship:\ndo not overuse carbapenems.'],
    ['Vancomycin','Glycopeptide antibiotic.\nActs on gram-positive\nbacteria only.\nInhibits cell wall synthesis.','15–20 mg/kg IV\nevery 12h\n(dose by weight\nand renal function).\nMonitor levels.','MRSA. Line infections.\nGram-positive sepsis.\nNephrotoxic — monitor\nrenal function.\nOtotoxic in overdose.\nTarget trough 15–20 mg/L.'],
    ['Gentamicin','Aminoglycoside antibiotic.\nBactericidal against\ngram-negative bacteria.\nInhibits 30S ribosome.','5–7 mg/kg IV\nonce daily\n(extended interval\ndosing).\nMonitor levels.','Synergy with penicillins.\nNephrotoxic + ototoxic.\nSingle daily dosing\nless nephrotoxic than\nmultiple doses.\nMonitor: pre-dose level.'],
    ['Ceftriaxone','3rd gen cephalosporin.\nBeta-lactam.\nBroad spectrum gram +/-.\nExcellent CNS penetration.','2g IV every 12h\n(for meningitis).\n1–2g once daily\n(other sepsis).','Drug of choice for\nbacterial meningitis.\nLong half-life = once or\ntwice daily dosing.\nBiliary excretion — can\ncause biliary sludge\nwith prolonged use.'],
    ['Fluconazole','Azole antifungal.\nInhibits ergosterol\nsynthesis (fungal\ncell membrane).','400mg IV/oral\nonce daily\nfor candidaemia.','For Candida sepsis.\nNot active against\nAspergillus.\nCan use if Candida\nknown susceptible.\nCheck drug interactions.'],
    ['Caspofungin','Echinocandin antifungal.\nInhibits glucan\nsynthesis in fungal\ncell wall.','70mg IV loading\nthen 50mg IV\nonce daily.','For severe Candida\ninfection or Candida\nresistant to fluconazole.\nBetter tolerated\nthan fluconazole.\nFor empirical antifungal\nin neutropenic sepsis.'],
    ['Normal Saline\n0.9% NaCl\nor Hartmann\'s','IV crystalloid.\nReplaces extracellular\nfluid volume.','500ml bolus IV\nover 15–30 min.\nRepeat up to\n30 ml/kg total.','Hartmann\'s preferred\nfor large volumes\n(avoids hyperchloraemic\nacidosis from large\nnormal saline volumes).'],
    ['Human Albumin\nSolution (HAS)','Colloid fluid.\n20% or 4.5% solution.','100–200ml of\n20% albumin.','Used in septic shock\nnot responding to\ncrystalloids alone.\nAlbumin 4% equivalent\nto crystalloid volume\nexpansion. May help\nin hypoalbuminaemic\npatients.'],
]
story.append(plain_table(pharm_table,[CW*0.16,CW*0.22,CW*0.16,CW*0.46]))

info_box('<b>Prescribing in Sepsis (Ganesh and Kuruvilla principles):</b> Always check: (1) Allergy before any antibiotic. (2) Renal function before aminoglycosides and vancomycin. (3) Pregnancy status before fluconazole (teratogenic). (4) Drug interactions — vancomycin + diuretics = increased nephrotoxicity. (5) Gentamicin levels — check pre-dose level before second dose. (6) De-escalate antibiotics at 48–72h using culture sensitivities.', story)

memory_hook('VASOPRESSORS: 1st = Noradrenaline. 2nd = Vasopressin (add-on). 3rd = Adrenaline (refractory). Low cardiac output = Dobutamine. Steroids = Hydrocortisone in refractory shock only. ANTIBIOTICS: Unknown source = Tazocin. Resistant/severe = Meropenem. MRSA/line = Vancomycin. Meningitis = Ceftriaxone. Fungal = Caspofungin.', story)
divider(story)

# ── §14 MRCP EXAM TRIGGERS ───────────────────────────────────────────────────
sec_header('Section 14: MRCP Exam Triggers — High-Yield Scenarios', story)

professor_says('These are the exact clinical scenarios that appear in MRCP Part 1, Part 2, and PACES. Learn these patterns and you will recognise them in the exam within seconds.', story)

triggers = [
    ['#','Clinical Scenario','Key Teaching Point','Answer / Action'],
    ['1','A 68-year-old woman is found confused at home. Temperature 35.8°C. HR 110. RR 22. BP 90/50. Raised WBC and CRP. Urine dipstick: nitrites positive.',
     'Hypothermia + confusion in elderly = sepsis (urosepsis). Hypothermia is a BAD sign.',
     'Sepsis-6 immediately. IV fluids. Urine cultures + blood cultures. IV antibiotics (cefuroxime). Urology review if obstructed.'],
    ['2','A patient with septic shock receives 2 litres of IV fluid. MAP remains 55 mmHg. What is the next step?',
     'Fluid-refractory septic shock. When do you start vasopressors?',
     'Start noradrenaline infusion via central line. Target MAP >=65 mmHg. Also consider arterial line for continuous BP monitoring.'],
    ['3','A 20-year-old student develops sudden severe headache, fever, neck stiffness, and a non-blanching rash. What do you do?',
     'Meningococcal septicaemia. What is the most urgent action?',
     'Give IM/IV benzylpenicillin 1.2g IMMEDIATELY. Transfer to hospital. Do NOT wait for CT or blood tests. Give antibiotics first.'],
    ['4','A 55-year-old chemotherapy patient presents to A&E with fever of 38.5°C. WBC 0.8 x10^9/L.',
     'Neutropenic sepsis. What is the critical action?',
     'Piperacillin-tazobactam 4.5g IV within 1 hour of triage. Sepsis-6 bundle. Haematology review. This is an oncological emergency.'],
    ['5','A patient with septic shock is on noradrenaline 0.3 mcg/kg/min and vasopressin 0.03 units/min. MAP still 58 mmHg. What drug do you add?',
     'Steroids in refractory septic shock.',
     'Hydrocortisone 200mg/day IV (50mg every 6h). Evidence from APROCCHSS trial. This is REFRACTORY septic shock — relative adrenal insufficiency.'],
    ['6','Blood cultures grow Staphylococcus aureus. The patient has a central venous catheter. What is the management?',
     'CRBSI — catheter-related bloodstream infection. Source control.',
     'Remove the central line. Send tip for culture. Start vancomycin 15-20mg/kg IV every 12h. Echocardiogram to exclude endocarditis (vegetation on heart valve).'],
    ['7','A patient has fever, rigors, right upper quadrant pain, and jaundice. Temperature 39°C. Raised bilirubin and ALP.',
     'Charcot\'s triad — ascending cholangitis.',
     'Biliary sepsis. Sepsis-6. IV antibiotics (Tazocin). Urgent ERCP within 24 hours for bile duct drainage. Ultrasound to confirm bile duct dilation.'],
    ['8','A 45-year-old woman has cellulitis of the leg. Despite 48 hours of IV antibiotics, the pain is getting WORSE. The skin looks relatively normal but she is screaming in pain.',
     'Pain out of proportion to appearance = necrotising fasciitis.',
     'SURGICAL EMERGENCY. Do NOT wait. Emergency surgical debridement. Call theatre immediately. Antibiotics (meropenem + clindamycin + vancomycin) alongside surgery. Clindamycin inhibits toxin production.'],
    ['9','A post-operative patient develops fever, hypotension, diffuse erythematous rash, and diarrhoea on day 2 after gynaecological surgery.',
     'Toxic Shock Syndrome (Staphylococcal). Clue: diffuse rash + multi-system.',
     'IV fluids + vancomycin + clindamycin. Clindamycin ESSENTIAL — inhibits toxin production even if organism resistant. Remove any foreign material (packing, sutures). Search for retained foreign body.'],
    ['10','A patient is on Sepsis-6. Blood cultures have been taken. Antibiotics are ready but the nurse says "we haven\'t got the full sensitivities yet". Should you wait?',
     'Blood cultures before antibiotics — but do NOT delay antibiotics.',
     'Give antibiotics NOW. Do NOT wait for sensitivity results. Empirical broad-spectrum antibiotics save lives. Narrow antibiotics at 48-72h when sensitivities return.'],
    ['11','A patient in septic shock has the following blood results: Platelets 45. PT prolonged. APTT prolonged. Fibrinogen 0.8 g/L. D-dimer very high.',
     'DIC — Disseminated Intravascular Coagulation.',
     'Treat underlying sepsis (antibiotics + source control). Give FFP 15ml/kg. Give cryoprecipitate if fibrinogen <1.5 g/L. Give platelets if <50 and bleeding. Do NOT give heparin routinely.'],
    ['12','A patient survived ICU with severe sepsis 6 months ago. Now attending clinic complaining of poor memory, fatigue, and nightmares.',
     'Post-sepsis syndrome — long-term complications of sepsis.',
     'Acknowledge this is real. Refer to rehabilitation services. Psychological support / PTSD assessment. Cognitive assessment. "Post-intensive care syndrome (PICS)" is now well recognised.'],
]
story.append(plain_table(triggers,[CW*0.04,CW*0.28,CW*0.24,CW*0.44]))
divider(story)

# ── §15 MINIMAL RESOURCES + PACES ───────────────────────────────────────────
sec_header('Section 15: Minimal Resources Summary + PACES Guide', story)

story.append(bp('<b>Managing Sepsis With Minimal Resources:</b>'))
professor_says('In a small hospital, night shift, or resource-limited setting, you may not have ICU beds, vasopressors, or advanced monitoring. Here is what you CAN do with basic resources.', story)

minimal_table = [
    ['Step','Action','Minimum Resources Needed'],
    ['1. Recognise','Use qSOFA: RR, BP, consciousness.\nThink "could this be sepsis?"','Eyes, BP cuff, watch.'],
    ['2. Oxygen','Give high-flow oxygen via mask.\nOr nasal prongs at 4-6 L/min.','Oxygen cylinder + mask.'],
    ['3. IV Access + Fluids','Large-bore IV cannula.\n500ml IV fluid fast.','Cannula. IV fluid bag.'],
    ['4. Blood Cultures','Take blood from vein into\naerobic + anaerobic bottles.','Blood culture bottles.\nGloves and sterile technique.'],
    ['5. Antibiotics','Start empirical IV antibiotics.\nBroad-spectrum. Within 1 hour.','Basic antibiotics:\nAmoxicillin + gentamicin if limited.\nOral ciprofloxacin if IV not possible.'],
    ['6. Urine Output','Insert catheter.\nMeasure every hour.\nOliguria = give more fluids.','Urinary catheter and bag.'],
    ['7. Temperature, HR, BP','Measure every 30 minutes.\nDocument all observations.','Thermometer. BP cuff.'],
    ['8. Blood Tests','FBC, CRP, U&E if available.\nUrine dipstick.\nPregnancy test if woman.','Minimal lab. Dipstick strips.'],
    ['9. Transfer','If deteriorating and no ICU:\nrefer and transfer to higher facility.\nContinue treatment during transfer.','Ambulance. Phone for referral.'],
    ['10. Source Control','Drain any abscess. Remove\ninfected cannula. Treat\nthe source physically.','Surgical drainage kit.\nClinical skills.'],
]
story.append(plain_table(minimal_table,[CW*0.08,CW*0.54,CW*0.38]))
story.append(Spacer(1,6))

story.append(bp('<b>PACES — History Station: Suspected Sepsis</b>'))
paces_hx = [
    '<b>Open:</b> "Can you tell me what has been happening?" Listen without interrupting.',
    '<b>Source symptoms:</b> "Any cough or difficulty breathing? Any pain passing urine? Any abdominal pain? Any skin redness or swelling? Any neck stiffness or headache?"',
    '<b>Duration:</b> "When did this start? How quickly did it get worse?"',
    '<b>Rigors:</b> "Have you had any severe shaking or shivering episodes?"',
    '<b>Fever:</b> "Have you felt hot or cold? Any sweats?"',
    '<b>Systemic:</b> "Any reduced urine? Any confusion (ask family)? Any recent travel?"',
    '<b>Risk factors:</b> "Any recent surgery, hospital stay, or procedure? Any chemotherapy? Any diabetes or immune problems? Any IV drug use? Any new sexual partners (PID)?"',
    '<b>Drug history:</b> "Any antibiotics recently? Any steroids or immunosuppressants? Any allergies?"',
    '<b>Social:</b> "Who lives with you? Can you normally look after yourself?"',
]
for pt in paces_hx:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1,5))

story.append(bp('<b>PACES — Examination: The Septic Patient</b>'))
paces_ex = [
    '<b>End of bed:</b> Does the patient look ill? Flushed or mottled? Confused? Breathing fast?',
    '<b>Vital signs:</b> Temperature. HR. BP. RR. SpO2. These define severity.',
    '<b>Hands:</b> Capillary refill time. Warm (early sepsis) vs cold (late shock). Peripheral cyanosis. IV line sites (infection?).',
    '<b>Face:</b> Jaundice (biliary/hepatic sepsis). Pallor. Conjunctival pallor. Oral candida (immunosuppressed).',
    '<b>Neck:</b> Neck stiffness (Kernig\'s sign — cannot extend knee when hip is flexed = meningism). Lymphadenopathy.',
    '<b>Chest:</b> Dullness + reduced breath sounds + bronchial breathing = consolidation (pneumonia). Pleural rub.',
    '<b>Abdomen:</b> Tenderness (source). Murphy\'s sign (gallbladder). Organomegaly. Ascites.',
    '<b>Skin:</b> Rash (non-blanching = meningococcal). Cellulitis. Necrotising fasciitis (pain out of proportion). Purpura.',
    '<b>Legs:</b> Calf tenderness (DVT source?). Oedema.',
    '<b>Catheter bag:</b> Urine colour. Volume. Turbid/cloudy = UTI.',
]
for pt in paces_ex:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1,5))

story.append(bp('<b>PACES Presentation Template — Sepsis:</b>'))
story.append(bp('"On examination, this patient appears acutely unwell. Temperature is 38.9°C. Heart rate 118. Blood pressure 88/52. Respiratory rate 26. Oxygen saturation 94% on air. The patient is flushed and confused. Capillary refill is 3 seconds peripherally. There is dullness and bronchial breathing at the right base, consistent with consolidation. There are no skin rashes. In summary, the clinical picture is consistent with community-acquired pneumonia causing sepsis with haemodynamic compromise. I would immediately initiate the Sepsis-6 bundle, obtain blood cultures, measure lactate, and give broad-spectrum antibiotics (co-amoxiclav + clarithromycin IV) within 1 hour."'))

memory_hook('PACES: Always state vital signs clearly. Always give a working diagnosis. Always give a management plan. Never say "I don\'t know" — say your differential and how you would investigate. Examiners want to hear: "I am concerned this patient has sepsis. I would initiate the Sepsis-6 bundle immediately."', story)
divider(story)

# ── MASTER MEMORY SUMMARY ────────────────────────────────────────────────────
story.append(Spacer(1,6))
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
    [Paragraph('MASTER MEMORY SUMMARY — SEPSIS AND SEPTIC SHOCK', sGrnB)],
    [Paragraph('DEFINITIONS (Sepsis-3, 2016): Sepsis = infection + SOFA increase >=2. Septic Shock = sepsis + vasopressors needed + lactate >2 mmol/L. "Severe sepsis" no longer used. SIRS no longer defines sepsis.', sGrn)],
    [Paragraph('PATHOPHYSIOLOGY: Infection → Macrophages → Cytokines (TNF-alpha, IL-1, IL-6) → Vasodilation (NO) + Capillary leak + Myocardial depression → Low BP + Poor perfusion → Lactate rises → MODS.', sGrn)],
    [Paragraph('COMMON SOURCES: Lungs (most common overall). Urine (most common in women/elderly). Abdomen/biliary (Charcot triad = cholangitis). Skin (NF = surgical emergency). CNS (meningitis).', sGrn)],
    [Paragraph('CLINICAL RED FLAGS: Temp <36 or >38. HR >90. RR >20. SBP <100. Confused. Mottled cold skin. No urine. Non-blanching rash = give benzylpenicillin IMMEDIATELY.', sGrn)],
    [Paragraph('SCORING: qSOFA (bedside): RR>=22, Confusion, SBP<=100. Score 2+ = suspect sepsis. SOFA: 6 organs, increase 2+ = sepsis defined. NEWS2: ward early warning, score 5+ = escalate.', sGrn)],
    [Paragraph('INVESTIGATIONS: Blood cultures x2 BEFORE antibiotics. Lactate (>2 = bad, >4 = very high mortality). FBC + CRP + Procalcitonin + ABG + U&E + LFTs + Coagulation. Urine dip + MSU. CXR. Then image to find source.', sGrn)],
    [Paragraph('SEPSIS-6 BUNDLE (within 1 hour): 3 GIVE = High-flow oxygen + IV fluid bolus (30ml/kg) + IV broad-spectrum antibiotics. 3 TAKE = Blood cultures + Lactate + Urine output (catheter).', sGrn)],
    [Paragraph('VASOPRESSORS: 1st line = Noradrenaline (via central line). 2nd = Vasopressin (add-on). Low cardiac output = Dobutamine. Steroids = Hydrocortisone 200mg/day ONLY in refractory shock.', sGrn)],
    [Paragraph('ANTIBIOTICS: Unknown source = Tazocin. Pneumonia = Co-amoxiclav + Clarithromycin. Urosepsis = Cefuroxime. Meningitis = Ceftriaxone + Dexamethasone. MRSA/Line = Vancomycin. Neutropenic = Tazocin IMMEDIATELY. Perforated gut = Tazocin or Meropenem.', sGrn)],
    [Paragraph('SPECIAL SITUATIONS: Neutropenic sepsis = Tazocin within 1 hour (oncological emergency). Meningococcal = benzylpenicillin IM before admission. TSS = clindamycin inhibits toxin. Cholangitis = ERCP urgently. NF = theatre immediately.', sGrn)],
    [Paragraph('COMPLICATIONS: ARDS (ventilate, low tidal volumes). AKI (dialysis if needed). DIC (FFP + cryoprecipitate + platelets). Septic cardiomyopathy (dobutamine). Adrenal insufficiency (hydrocortisone). Post-sepsis syndrome (PTSD, cognitive impairment).', sGrn)],
    [Paragraph('MRCP KEYS: (1) Sepsis-3 definitions. (2) Lactate >2 = septic shock definition. (3) Antibiotics within 1 hour. (4) Noradrenaline first-line vasopressor. (5) Hydrocortisone only in refractory shock. (6) Procalcitonin guides de-escalation. (7) Clindamycin in TSS/NF (toxin inhibition). (8) Waterhouse-Friderichsen = bilateral adrenal haemorrhage in meningococcaemia.', sGrn)],
]
innerG = Table(gRows, colWidths=[CW-4])
innerG.setStyle(gTS1)
outerG = Table([[innerG]], colWidths=[CW])
outerG.setStyle(gTSO)
story.append(outerG)
story.append(Spacer(1,12))

doc.build(story)
print('SUCCESS: Septic Shock MRCP Note saved to', OUT)
