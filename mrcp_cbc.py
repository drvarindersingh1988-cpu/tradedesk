"""
MRCP REVISION NOTE (MEDIUM): Complete Blood Count (CBC / FBC) — Reading, Interpreting, Common Patterns
A3 Portrait, text-safe PIL diagram toolkit, Interactive Q&A, MCQ self-test, separate answer key.
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

OUT = '/mnt/user-data/outputs/CBC_Complete_Blood_Count_MRCP_Note.pdf'
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

PAGE_W, PAGE_H = A3
MARGIN = 22*mm
CW = PAGE_W - 2*MARGIN

doc = SimpleDocTemplate(OUT, pagesize=A3,
      leftMargin=MARGIN, rightMargin=MARGIN,
      topMargin=MARGIN, bottomMargin=MARGIN)

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

def bp(text, st=None): return Paragraph(text, st or sBody)
def sec_header(title, story): story.append(Spacer(1,8)); story.append(Paragraph(title, sH1))
def divider(story): story.append(Spacer(1,4)); story.append(HRFlowable(width=CW, thickness=0.6, color=TEAL_M, spaceAfter=6))

def plain_table(data, widths, header=True):
    rows = []
    for i, row in enumerate(data):
        st = sH2 if (i == 0 and header) else sBody
        rows.append([Paragraph(str(c), st) if not hasattr(c,'wrap') else c for c in row])
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0, splitByRow=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),TEAL_L),('TEXTCOLOR',(0,0),(-1,0),TEAL),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,TEAL_XL]),
        ('GRID',(0,0),(-1,-1),0.6,TEAL_M),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    return t

def alert_box(text, story):
    t = Table([[Paragraph(f'<b>ALERT: {text}</b>', sAlert)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),RED_L),('BOX',(0,0),(-1,-1),2,RED_D),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,6))

def info_box(text, story, color=None, border=None):
    bg = color or BLUE_L; bd = border or BLUE_D
    t = Table([[Paragraph(text, sBody)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),bg),('BOX',(0,0),(-1,-1),2,bd),
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
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),TEAL_XL),('BOX',(0,0),(-1,-1),1.5,TEAL_M),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,6))

def memory_hook(text, story):
    t = Table([[Paragraph(f'MEMORY: {text}', sMem)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),AMBER),('BOX',(0,0),(-1,-1),2,AMBER_B),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,6))

def qa_block(statement, question, hint, answer, story):
    story.append(bp(statement)); story.append(Spacer(1,3))
    qt = Table([[Paragraph(f'<b>PROFESSOR ASKS:</b>  {question}', sQ)]], colWidths=[CW])
    qt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PUR_L),('BOX',(0,0),(-1,-1),1.5,PUR_D),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.append(qt); story.append(Spacer(1,3))
    ht = Table([[Paragraph(f'<i>HINT — think first:</i>  {hint}', sHint)]], colWidths=[CW])
    ht.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),AMBER),('BOX',(0,0),(-1,-1),1,AMBER_B),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(ht); story.append(Spacer(1,3))
    at = Table([[Paragraph(f'<b>ANSWER:</b>  {answer}', sAns)]], colWidths=[CW])
    at.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),GREEN_L),('BOX',(0,0),(-1,-1),1.5,GREEN_D),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.append(at); story.append(Spacer(1,8))

ANSWER_KEY = []
def mcq(num, vignette, options, correct, explanation, story):
    story.append(Paragraph(f'<b>Question {num}</b>', sQNum))
    story.append(Paragraph(vignette, sVig))
    for letter, text in options:
        story.append(Paragraph(f'{letter})  {text}', sOpt))
    story.append(Paragraph('Your answer: _________', sBody))
    story.append(Spacer(1,8))
    ANSWER_KEY.append((num, correct, explanation))

def print_answer_key(story):
    for num, letter, explanation in ANSWER_KEY:
        story.append(Paragraph(f'<b>Q{num} — Correct answer: {letter}</b>   {explanation}', sBody))
        story.append(Spacer(1,3))

def arr_r(draw, x, y, length=44, col='#0d5c63', w=3):
    draw.line([(x,y),(x+length,y)], fill=col, width=w)
    draw.polygon([(x+length,y),(x+length-10,y-6),(x+length-10,y+6)], fill=col)

def arr_d(draw, x, y, length=32, col='#0d5c63', w=3):
    draw.line([(x,y),(x,y+length)], fill=col, width=w)
    draw.polygon([(x,y+length),(x-6,y+length-10),(x+6,y+length-10)], fill=col)

def i2r(img, W):
    scale = W / img.width; nH = int(img.height * scale)
    img = img.resize((int(W), nH), Image.LANCZOS)
    buf = BytesIO(); img.save(buf, 'PNG'); buf.seek(0)
    return RLImage(buf, width=W, height=nH)

def load_fonts(sizes):
    fonts = {}
    for name, sz in sizes.items():
        try:
            fonts[name] = ImageFont.truetype(FONT_DIR+('DejaVuSans-Bold.ttf' if 'B' in name else 'DejaVuSans.ttf'), sz)
        except:
            fonts[name] = ImageFont.load_default()
    return fonts

print('Building PIL diagrams...')

def text_w(draw, s, font): return draw.textlength(s, font=font)

def wrap_text(draw, text, font, max_width):
    out = []
    for para in str(text).split('\n'):
        if para.strip() == '': out.append(''); continue
        words = para.split(' '); cur = ''
        for w in words:
            cand = w if not cur else cur + ' ' + w
            if text_w(draw, cand, font) <= max_width or not cur: cur = cand
            else: out.append(cur); cur = w
        if cur: out.append(cur)
    return out

def lh(font, factor=1.32): return int(font.size * factor)

def draw_block(draw, x, y, text, font, fill, max_width, align='left', extra_gap=0):
    lines = wrap_text(draw, text, font, max_width)
    step = lh(font) + extra_gap; cy = y
    for ln in lines:
        if align == 'center':
            w = text_w(draw, ln, font)
            draw.text((x + (max_width - w) / 2, cy), ln, font=font, fill=fill, anchor='la')
        else:
            draw.text((x, cy), ln, font=font, fill=fill, anchor='la')
        cy += step
    return cy

def card(draw, x0, x1, y, title, body, f_title, f_body, accent, body_bg, pad=13, line_gap=3):
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
    inner_w = W - 2 * pad_x
    lines = wrap_text(draw, title, font, inner_w)
    bar_h = len(lines) * lh(font) + 32
    draw.rectangle([0, 0, W - 1, bar_h], fill=accent)
    draw_block(draw, pad_x, 16, title, font, text_color, inner_w, align='center')
    return bar_h

def finish(img, draw, W, bottom_y, footer_text, f_xs, accent='#0d5c63'):
    inner_w = W - 60
    lines = wrap_text(draw, footer_text, f_xs, inner_w)
    foot_h = len(lines) * lh(f_xs) + 20
    top = bottom_y + 14
    draw.rectangle([0, top, W - 1, top + foot_h], fill=accent)
    draw_block(draw, 30, top + 10, footer_text, f_xs, '#ffffff', inner_w, align='center')
    return img.crop((0, 0, W, top + foot_h + 6))

CARD_FONTS = {'T': 24, 'B': 17, 'XS': 14}
PAD_X = 46

# ── PIL 1: CBC Components ────────────────────────────────────────────────────
def make_cbc_components():
    W, H_MAX = 900, 1800
    f = load_fonts(CARD_FONTS)
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PAD_X, W - PAD_X
    hh = header_band(draw, W, 'WHAT EACH NUMBER IN THE CBC/FBC MEANS — IN PLAIN LANGUAGE', f['T'], PAD_X)
    yy = hh + 22

    cards = [
        ('#0d5c63', '#dff2f1',
         'HAEMOGLOBIN (Hb) — the actual oxygen carrier',
         'Normal: Men ~130-170 g/L, Women ~120-160 g/L. Each red blood cell is packed with haemoglobin — the iron-containing protein that grabs oxygen in the lungs and delivers it to tissues. LOW Hb = anaemia. HIGH Hb = polycythaemia (too many cells, blood becomes sludgy).'),
        ('#c0392b', '#fde8e8',
         'MCV (Mean Cell Volume) — the SIZE of each red cell',
         'Normal: 80-100 fL. This single number tells you WHY the patient is anaemic. Low MCV = small red cells (microcytic). Normal MCV = normal-sized cells (normocytic). High MCV = large red cells (macrocytic). Always look at MCV alongside Hb — it points you straight to the cause.'),
        ('#7d3c98', '#f5eef8',
         'WHITE BLOOD COUNT (WBC) — your infection-fighting army',
         'Normal: 4.0-11.0 x10^9/L. This is a TOTAL count of all white cells. Always ask for the DIFFERENTIAL — this breaks it into types: neutrophils, lymphocytes, eosinophils, monocytes, basophils. Each type tells a different story.'),
        ('#d4640a', '#fef3e2',
         'PLATELETS — the tiny fragments that plug holes and stop bleeding',
         'Normal: 150-400 x10^9/L. Low (thrombocytopenia) = risk of bleeding. High (thrombocytosis) = reactive (infection, inflammation, iron deficiency) or, rarely, a myeloproliferative disorder.'),
        ('#2471a3', '#e8f4fd',
         'OTHER INDICES: MCH, MCHC, RDW — fine detail about red cell quality',
         'MCH (Mean Cell Haemoglobin, 27-33 pg): average Hb content per cell — low in iron deficiency. MCHC (Mean Cell Haemoglobin Concentration, 315-360 g/L): concentration of Hb in cells — very high in hereditary spherocytosis. RDW (Red Cell Distribution Width, 11-15%): how variable the cell sizes are — high in iron deficiency and mixed deficiencies.'),
    ]
    for accent, bg, title, body in cards:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 14

    final = finish(img, draw, W, yy,
        'FIRST STEP when you see any CBC: check Hb (is there anaemia?), MCV (what SIZE are the cells?), WBC (any infection/malignancy signal?), Platelets (any bleeding/clotting risk?)',
        f['XS'])
    return i2r(final, CW)

# ── PIL 2: Three types of anaemia ────────────────────────────────────────────
def make_anaemia_types():
    W, H_MAX = 900, 1800
    f = load_fonts(CARD_FONTS)
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PAD_X, W - PAD_X
    hh = header_band(draw, W, 'THE THREE TYPES OF ANAEMIA — MCV IS THE KEY', f['T'], PAD_X)
    yy = hh + 22

    cards = [
        ('#c0392b', '#fde8e8',
         'LOW MCV (<80 fL) — MICROCYTIC ANAEMIA — small red cells',
         'Causes to know: (1) IRON DEFICIENCY — most common, look for menorrhagia, GI blood loss, poor diet. Ferritin is low. (2) THALASSAEMIA — genetic, especially South Asian/Mediterranean patients; target cells on blood film. (3) ANAEMIA OF CHRONIC DISEASE — can be micro or normocytic; ferritin is normal or HIGH. (4) SIDEROBLASTIC ANAEMIA — rare, ring sideroblasts on film.'),
        ('#1a8a94', '#e0f4f5',
         'NORMAL MCV (80-100 fL) — NORMOCYTIC ANAEMIA — normal-sized cells',
         'Causes: (1) ACUTE BLOOD LOSS — sudden haemorrhage, not had time to change cell size yet. (2) ANAEMIA OF CHRONIC DISEASE — the most common anaemia overall. (3) CHRONIC KIDNEY DISEASE — low erythropoietin means fewer red cells made. (4) HAEMOLYTIC ANAEMIA — cells destroyed too fast; raised reticulocytes, raised bilirubin. (5) APLASTIC ANAEMIA — bone marrow fails; pancytopenia (low WBC and platelets too).'),
        ('#7d3c98', '#f5eef8',
         'HIGH MCV (>100 fL) — MACROCYTIC ANAEMIA — large red cells',
         'Causes: (1) B12 DEFICIENCY — pernicious anaemia, vegans, poor absorption. (2) FOLATE DEFICIENCY — poor diet, pregnancy, malabsorption, methotrexate. (3) ALCOHOL — direct toxic effect on marrow AND often dietary deficiency together. (4) HYPOTHYROIDISM — thyroid hormones needed for normal marrow function. (5) LIVER DISEASE — always causes macrocytosis. (6) DRUGS — methotrexate, hydroxycarbamide, azathioprine.'),
        ('#d4640a', '#fef3e2',
         'MEGALOBLASTIC vs NON-MEGALOBLASTIC MACROCYTOSIS',
         'MEGALOBLASTIC (B12/folate deficiency): hypersegmented neutrophils on the blood film (5+ lobes) — this is the pathognomonic finding. Oval macrocytes. May also have neurological symptoms with B12 deficiency (subacute combined degeneration of the cord). NON-MEGALOBLASTIC (alcohol, liver, hypothyroidism): round macrocytes, no hypersegmented neutrophils.'),
    ]
    for accent, bg, title, body in cards:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 14

    final = finish(img, draw, W, yy,
        'MCV TELLS YOU WHERE TO LOOK: Low = iron/thalassaemia. Normal = chronic disease/kidneys/haemolysis/acute loss. High = B12/folate/alcohol/liver/drugs.',
        f['XS'])
    return i2r(final, CW)

# ── PIL 3: WBC differential ──────────────────────────────────────────────────
def make_wbc_differential():
    W, H_MAX = 900, 1700
    f = load_fonts(CARD_FONTS)
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PAD_X, W - PAD_X
    hh = header_band(draw, W, 'THE WHITE CELL DIFFERENTIAL — WHAT EACH TYPE TELLS YOU', f['T'], PAD_X)
    yy = hh + 22

    cards = [
        ('#0d5c63', '#dff2f1',
         'NEUTROPHILS (40-70% of WBC) — the bacterial police',
         'HIGH (neutrophilia): bacterial infection, steroids, myocardial infarction, physiological stress, smoking, myeloid leukaemia. LOW (neutropenia <1.5): viral infections, drugs (chemotherapy, carbimazole, clozapine, NSAIDs), B12/folate deficiency, SLE, aplastic anaemia. DANGER: <0.5 = severe risk of life-threatening bacterial infection.'),
        ('#c0392b', '#fde8e8',
         'LYMPHOCYTES (20-40% of WBC) — the viral immune cells',
         'HIGH (lymphocytosis): viral infections (EBV/glandular fever, CMV), CLL (chronic lymphocytic leukaemia — think elderly patient with very high WBC, lymphocytosis, smear cells on film), whooping cough. LOW (lymphopenia): HIV (depletes CD4 T-lymphocytes), steroids, chemotherapy, severe sepsis.'),
        ('#d4640a', '#fef3e2',
         'EOSINOPHILS (1-4% of WBC) — the allergy and parasite cells',
         'HIGH (eosinophilia): the classic causes in MRCP are ASTHMA, ATOPIC CONDITIONS (eczema, hay fever), DRUG REACTIONS, PARASITIC INFECTIONS (especially in travellers), ADDISON\'S DISEASE (loss of cortisol removes normal eosinophil suppression). Also: Churg-Strauss vasculitis, Loeffler syndrome.'),
        ('#7d3c98', '#f5eef8',
         'MONOCYTES (2-8%) and BASOPHILS (<1%)',
         'MONOCYTOSIS: TB (classic), other chronic infections, sarcoidosis, inflammatory bowel disease, monocytic leukaemia. BASOPHILIA (<1% is normal; any significant rise is abnormal): strongly associated with CHRONIC MYELOID LEUKAEMIA (CML) — basophilia on a blood count in an adult should make you think CML until proven otherwise.'),
        ('#2471a3', '#e8f4fd',
         'BLAST CELLS — the alarm finding',
         'Blast cells are immature, abnormal white cells that should NOT be in the peripheral blood. If reported on a CBC differential, this is an EMERGENCY. They are seen in acute leukaemia (AML, ALL). Act immediately: urgent haematology review. Do not wait for the next routine appointment.'),
    ]
    for accent, bg, title, body in cards:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 14

    final = finish(img, draw, W, yy,
        'THE DIFFERENTIAL UNLOCKS THE WBC: neutrophils = bacteria/steroids/MI; lymphocytes = viruses/CLL; eosinophils = allergy/parasites/Addisons; basophilia = think CML; blast cells = acute leukaemia emergency.',
        f['XS'])
    return i2r(final, CW)

img_components = make_cbc_components()
img_anaemia    = make_anaemia_types()
img_wbc        = make_wbc_differential()

print('PIL diagrams done.')

# ═══════════════════════════════════════════════════════════════════════════
# STORY BUILD
# ═══════════════════════════════════════════════════════════════════════════
story = []

story.append(Paragraph('COMPLETE BLOOD COUNT (CBC / FBC)', sTitle))
story.append(Paragraph('Reading, Interpreting and Acting On Every Number — MRCP Part 1, Part 2 &amp; PACES, Interactive Edition', sSub))
story.append(HRFlowable(width=CW, thickness=2, color=TEAL, spaceAfter=10))

# §1 What is a CBC
sec_header('Section 1: What Is a CBC and Why Do We Do It?', story)
story.append(bp('The <b>Complete Blood Count (CBC)</b> — called a <b>Full Blood Count (FBC)</b> in the UK — is the single most ordered blood test in medicine. It counts and describes the three main types of cells in blood: <b>red blood cells</b> (which carry oxygen), <b>white blood cells</b> (which fight infection and respond to disease), and <b>platelets</b> (which stop bleeding). It also calculates a set of indices — numbers that describe the SIZE and QUALITY of the cells — which allow you to pinpoint WHY they are abnormal.'))
professor_says('You will look at CBCs every single day as a doctor. The mistake most juniors make is to look at ONE number — the haemoglobin — and stop there. The CBC is a STORY. The Hb tells you something is wrong. The MCV tells you WHY. The differential tells you what the BONE MARROW and immune system are doing. Read all of it, every time.', story)
divider(story)

# §2 The components
sec_header('Section 2: What Each Number Means', story)
story.append(img_components)
story.append(bp('Every number in the CBC/FBC — what it measures and what abnormalities mean', sImg))
story.append(Spacer(1, 6))
image_search_box('complete blood count FBC normal values reference ranges', 'Google Images / Medscape', story)

# Normal ranges quick-ref table
normal_table = [
    ['Parameter','Normal Range (Adults)','Low = Think...','High = Think...'],
    ['Haemoglobin (Hb)','Men: 130-170 g/L\nWomen: 120-160 g/L','Anaemia — use MCV\nto find the cause','Polycythaemia —\nprimary (PV) or\nsecondary (hypoxia,\nEPO abuse)'],
    ['MCV','80-100 fL','Microcytic: iron,\nthalassaemia,\nchronic disease','Macrocytic: B12/\nfolate, alcohol,\nliver, drugs'],
    ['WBC','4.0-11.0 x10^9/L','Infection, drugs,\naplastic, B12/folate\ndeficiency','Infection,\nleukaemia,\nsteroids, stress'],
    ['Neutrophils','1.8-7.5 x10^9/L','Viral, drugs,\nSLE, aplastic\n(<0.5 = danger!)','Bacterial infection,\nsteroids, MI,\nmyeloid leukaemia'],
    ['Lymphocytes','1.0-4.0 x10^9/L','HIV, steroids,\nchemotherapy','Viral, CLL,\nwhooping cough'],
    ['Eosinophils','0.04-0.4 x10^9/L','Steroids\n(suppress them)','Allergy, parasites,\nAddisons, drugs'],
    ['Platelets','150-400 x10^9/L','ITP, DIC, drugs,\nsepsis, hypersplenism','Reactive (infection,\niron def, inflam.) or\nmyeloproliferative'],
    ['RDW','11-15%','Not clinically\nsignificant if low','High = mixed\ndeficiency or iron\ndeficiency'],
]
story.append(plain_table(normal_table, [CW*0.15, CW*0.2, CW*0.32, CW*0.33]))
story.append(Spacer(1,6))
memory_hook('QUICK RULE: Hb tells you WHAT is wrong. MCV tells you WHY (for anaemia). Differential tells you WHICH white cell type — pointing to the mechanism. Platelets tell you bleeding/clotting risk.', story)
divider(story)

# §3 Anaemia
sec_header('Section 3: Interpreting Anaemia — MCV Is the Key', story)
story.append(bp('Anaemia (low Hb) has dozens of causes. The quickest way to organise them is by <b>MCV</b> — the size of the red cells. Think of it as opening the right drawer immediately, rather than searching every drawer in the room.'))

story.append(img_anaemia)
story.append(bp('The three MCV categories of anaemia — microcytic, normocytic, macrocytic — and the main causes of each', sImg))
story.append(Spacer(1, 6))

qa_block(
    'A 28-year-old woman presents with tiredness and breathlessness. Her CBC shows: Hb 88 g/L, MCV 62 fL, Platelets 480. She has heavy periods. Serum ferritin is 4 micrograms/L (low).',
    'What type of anaemia is this, what is the likely cause, and what does the raised platelet count (thrombocytosis) tell you in this context?',
    'Look at the MCV first: 62 fL is well below 80 — that immediately narrows the differential. Now combine with the ferritin, the clinical story (menorrhagia), and think about why the platelets might be raised in iron deficiency.',
    'This is MICROCYTIC ANAEMIA (MCV 62 fL) due to IRON DEFICIENCY — confirmed by a low ferritin (the most sensitive marker of iron stores). The cause is chronic blood loss from heavy menstruation. The reactive THROMBOCYTOSIS (platelets 480) is a recognised feature of iron deficiency anaemia — iron deficiency stimulates platelet production, and the thrombocytosis resolves once the iron deficiency is treated.',
    story)
memory_hook('MICROCYTIC + LOW FERRITIN = iron deficiency until proven otherwise. MICROCYTIC + NORMAL/HIGH FERRITIN = think thalassaemia or anaemia of chronic disease. Check BOTH.', story)
divider(story)

# §4 WBC differential
sec_header('Section 4: The White Blood Cell Differential', story)
story.append(bp('A raised or lowered total WBC count is just the beginning. The <b>differential</b> — which breaks it down into neutrophils, lymphocytes, eosinophils, monocytes and basophils — is where the real diagnosis lives.'))

story.append(img_wbc)
story.append(bp('The five white cell types and what their rise or fall means', sImg))
story.append(Spacer(1,6))

qa_block(
    'A 65-year-old man has a routine blood test. CBC shows: WBC 42 x10^9/L, Hb 128 g/L, Platelets 160. The differential shows the WBC is predominantly LYMPHOCYTES (38 x10^9/L). He feels well. The blood film report mentions "smear cells."',
    'What is the most likely diagnosis, and what is the significance of smear cells (also called smudge cells) on the blood film?',
    'An elderly patient, feels well, massively raised WBC that is LYMPHOCYTE-predominant — this is not an acute infection picture. Think of which chronic haematological condition presents like this in older patients, and what smear cells are (fragile cells that break during blood film preparation).',
    'This is classic CHRONIC LYMPHOCYTIC LEUKAEMIA (CLL). CLL typically presents in patients over 60, often found incidentally on a routine CBC, with a very high WBC that is predominantly lymphocytes. The cells in CLL are fragile — they break apart during blood film preparation, leaving smear cells (smudge cells), which are pathognomonic of CLL on the blood film.',
    story)

alert_box('BLAST CELLS on the blood film = ACUTE LEUKAEMIA until proven otherwise. This is an emergency. Do not dismiss them as a lab artefact. Call haematology immediately.', story)
memory_hook('CML: basophilia + very high WBC + splenomegaly. CLL: lymphocytosis + smear cells + elderly + feels well. AML/ALL: blast cells = emergency. These three leukaemia pictures appear constantly in MRCP Part 1.', story)
divider(story)

# §5 Platelets
sec_header('Section 5: Platelets — Low, High, and What To Do', story)

plt_table = [
    ['Platelet Count','Clinical Significance','Common Causes'],
    ['>400 x10^9/L\n(Thrombocytosis)','Usually REACTIVE\n(not dangerous);\nrare primary causes\ncan cause clots.','Reactive: infection,\niron deficiency, chronic\ninflammation, post-\nsplenectomy, malignancy.\nPrimary: essential\nthrombocythaemia,\npolycythaemia vera.'],
    ['100-150 x10^9/L\n(Mild reduction)','Increased bleeding risk\nwith trauma/surgery;\nmonitor.','Early ITP, drug reaction,\nhypersplenism, viral\ninfection.'],
    ['50-100 x10^9/L\n(Moderate reduction)','Significant bleeding\nrisk; avoid invasive\nprocedures where\npossible.','ITP, chemotherapy,\nDIC, B12/folate,\nhypersplenism.'],
    ['<50 x10^9/L\n(Severe thrombocytopenia)','Spontaneous bleeding\nrisk (petechiae,\npurpura, mucosal\nbleeds).','ITP, DIC, TTP, HUS,\naplastic anaemia,\nleukaemia, heparin-\ninduced (HIT).'],
    ['<20 x10^9/L\n(Critical)','High risk of\nspontaneous\nintracranial bleeding.','As above — requires\nurgent haematology\nreview and usually\nplatelet transfusion.'],
]
story.append(plain_table(plt_table, [CW*0.22, CW*0.36, CW*0.42]))
story.append(Spacer(1,6))

info_box('<b>ITP (Immune Thrombocytopenic Purpura):</b> autoantibodies destroy platelets; WBC and Hb are NORMAL — this is isolated thrombocytopenia. Presents with petechiae/purpura, no lymphadenopathy, no hepatosplenomegaly. Acute form in children after viral illness; chronic form in adults (especially women). Treatment: steroids, IVIG, rituximab, splenectomy. <b>TTP (Thrombotic Thrombocytopenic Purpura):</b> the pentad — microangiopathic haemolytic anaemia + thrombocytopenia + neurological symptoms + fever + renal failure. ADAMTS13 deficiency. Emergency — treat with plasma exchange.', story)
memory_hook('ITP = low platelets, normal Hb, normal WBC. TTP = low platelets + haemolytic anaemia + neuro + renal — the PENTAD. TTP is an emergency; ITP usually is not (unless count <20).', story)
divider(story)

# §6 Must-know CBC patterns
sec_header('Section 6: Must-Know CBC Patterns for MRCP', story)
professor_says('In the MRCP exam, you will rarely be given an isolated abnormality — they give you a complete CBC pattern and expect you to recognise it at a glance. These patterns come up again and again.', story)

pattern_table = [
    ['Pattern','What the CBC Shows','Diagnosis / Think Of'],
    ['Pancytopenia\n(all three lines low)','Low Hb, Low WBC,\nLow Platelets.','Aplastic anaemia (bone\nmarrow failure), B12/\nfolate deficiency (look\nfor macrocytosis), leukaemia/\nlymphoma infiltrating marrow,\nsevere sepsis, hypersplenism.'],
    ['Polycythaemia\n(high Hb + high\nred cell mass)','High Hb (>185 men,\n>165 women g/L),\noften raised WBC\nand platelets too.','Primary: POLYCYTHAEMIA\nVERA (JAK2 mutation;\nsplenomegaly; itching\nafter hot shower).\nSecondary: COPD, sleep\napnoea, high altitude,\nrenal cell carcinoma\n(EPO-secreting).'],
    ['Leucoerythroblastic\npicture','Immature white cells\n(myelocytes) + nucleated\nred cells in peripheral\nblood.','Bone marrow replacement\n— myelofibrosis,\nmetastatic cancer,\nleukaemia. The marrow\nis being pushed out\nof its space.'],
    ['Leukaemoid reaction','Very high WBC\n(>50) but NO blasts;\nall mature cells.','Severe infection,\nsteroids, G-CSF\ntreatment. Distinguished\nfrom CML by the\nLAP (leukocyte alkaline\nphosphatase) score —\nhigh in reaction, LOW\nin CML.'],
    ['Microangiopathic\nhaemolytic anaemia\n(MAHA)','Low Hb, low platelets,\nfragmented red cells\n(schistocytes) on film,\nhigh LDH, low\nhaptoglobin.','TTP, HUS, DIC, malignant\nhypertension, prosthetic\nheart valve haemolysis.'],
]
story.append(plain_table(pattern_table, [CW*0.2, CW*0.3, CW*0.5]))
story.append(Spacer(1,6))
memory_hook('POLYCYTHAEMIA VERA clues: high Hb + high WBC + high platelets + splenomegaly + aquagenic pruritus (itch after hot bath) + JAK2 V617F mutation. Secondary polycythaemia: high Hb but WBC and platelets NORMAL.', story)
divider(story)

# §7 Systematic approach
sec_header('Section 7: How to Read a CBC Systematically — A Five-Step Method', story)
story.append(bp('When you receive a CBC result, go through these five steps in order — every time:'))
for n, pt in enumerate([
    '<b>Step 1 — Haemoglobin:</b> Is it low (anaemia), normal, or high (polycythaemia)? This is the headline.',
    '<b>Step 2 — MCV:</b> If the Hb is low, what size are the cells? Low MCV → microcytic. Normal → normocytic. High → macrocytic. This is your diagnostic pointer.',
    '<b>Step 3 — WBC and the differential:</b> Is the total count raised or low? Which cell type is driving it? Neutrophil-dominant = bacterial/steroids/MI. Lymphocyte-dominant = viral/CLL. Eosinophilia = allergy/parasites/Addisons. Blast cells = emergency call haematology.',
    '<b>Step 4 — Platelets:</b> Risk of bleeding (low) or thrombosis/reactive (high)? Cross-check with Hb and WBC — pancytopenia tells a different story from isolated thrombocytopenia.',
    '<b>Step 5 — Put it together and request the BLOOD FILM:</b> Whenever the CBC does not fit a simple pattern, or you see unexplained cells, a blood film is the next step — it lets a haematologist look at the actual cells under a microscope.',
], 1):
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1,4))
memory_hook('5 STEPS: (1) Hb — is there anaemia? (2) MCV — why? (3) WBC differential — which cell? (4) Platelets — bleeding or clotting risk? (5) Blood film — when in doubt, look at the cells.', story)
divider(story)

# §8 Self-Test
story.append(PageBreak())
sec_header('Section 8: Self-Test — CBC MCQ Examination (10 Questions)', story)
professor_says('Attempt all questions before checking the answer key at the end. Write your answer in the blank.', story)
story.append(Spacer(1,6))

mcq(1,
    'A 45-year-old woman presents with fatigue. CBC: Hb 79 g/L, MCV 58 fL, WBC 6.5, Platelets 520. Ferritin 3 micrograms/L. What is the most likely diagnosis?',
    [('A','B12 deficiency anaemia'),
     ('B','Iron deficiency anaemia'),
     ('C','Thalassaemia trait'),
     ('D','Anaemia of chronic disease'),
     ('E','Folate deficiency')],
    'B',
    'Low Hb + very low MCV (microcytic) + very low ferritin = iron deficiency anaemia. The reactive thrombocytosis (520) is also characteristic of iron deficiency.',
    story)

mcq(2,
    'A 70-year-old man has a routine CBC: WBC 56 x10^9/L (predominantly lymphocytes 52 x10^9/L), Hb 130 g/L, Platelets 170. He feels well. Blood film: smear cells. What is the most likely diagnosis?',
    [('A','Acute myeloid leukaemia'),
     ('B','Infectious mononucleosis (glandular fever)'),
     ('C','Chronic lymphocytic leukaemia (CLL)'),
     ('D','Neutrophilia from bacterial infection'),
     ('E','Chronic myeloid leukaemia (CML)')],
    'C',
    'An elderly patient, feels well, very high lymphocyte-predominant WBC, and smear cells on the film = classic CLL picture.',
    story)

mcq(3,
    'Which of the following white cell differentials is most consistent with eosinophilia?',
    [('A','Bacterial pneumonia'),
     ('B','Addison\'s disease'),
     ('C','Acute myocardial infarction'),
     ('D','Chronic lymphocytic leukaemia'),
     ('E','HIV infection')],
    'B',
    'Eosinophilia is seen with allergy, asthma, parasitic infections, drug reactions, and Addison\'s disease (cortisol normally suppresses eosinophils; loss of cortisol = eosinophilia).',
    story)

mcq(4,
    'A CBC shows: Hb 88 g/L, MCV 112 fL, WBC 3.8 x10^9/L, Platelets 95. Blood film shows hypersegmented neutrophils (5-6 lobes). What is the unifying diagnosis?',
    [('A','Iron deficiency with reactive thrombocytosis'),
     ('B','Aplastic anaemia'),
     ('C','B12 or folate deficiency (megaloblastic anaemia)'),
     ('D','Alcohol-related liver disease (non-megaloblastic macrocytosis)'),
     ('E','Thalassaemia')],
    'C',
    'Macrocytic anaemia (MCV 112) + pancytopenia + hypersegmented neutrophils = megaloblastic anaemia, caused by B12 or folate deficiency. Hypersegmented neutrophils (>5 lobes) are pathognomonic of megaloblastic haematopoiesis.',
    story)

mcq(5,
    'A patient presents with petechiae and a platelet count of 15 x10^9/L. Haemoglobin and WBC are entirely normal. What is the most likely diagnosis?',
    [('A','Disseminated intravascular coagulation (DIC)'),
     ('B','Thrombotic thrombocytopenic purpura (TTP)'),
     ('C','Immune thrombocytopenic purpura (ITP)'),
     ('D','Aplastic anaemia'),
     ('E','Chronic lymphocytic leukaemia')],
    'C',
    'Isolated thrombocytopenia (only the platelets are affected; Hb and WBC are normal) is the hallmark of ITP — autoantibodies destroy platelets while the red cell and white cell lines are untouched.',
    story)

mcq(6,
    'A 55-year-old man has Hb 200 g/L, WBC 15 x10^9/L (neutrophil-predominant), Platelets 600, splenomegaly on examination, and reports itching after his morning shower. JAK2 V617F mutation detected. What is the diagnosis?',
    [('A','Secondary polycythaemia from COPD'),
     ('B','Polycythaemia vera (PV)'),
     ('C','Essential thrombocythaemia'),
     ('D','Chronic myeloid leukaemia (CML)'),
     ('E','Renal cell carcinoma secreting EPO')],
    'B',
    'Polycythaemia vera is characterised by raised Hb, raised WBC, raised platelets, splenomegaly, JAK2 V617F mutation, and aquagenic pruritus (itch after a hot bath/shower) — a classic MRCP triad.',
    story)

mcq(7,
    'A CBC shows pancytopenia (low Hb, low WBC, low platelets). Bone marrow biopsy shows a hypocellular marrow with fat replacing haematopoietic cells. What is the diagnosis?',
    [('A','Chronic myeloid leukaemia'),
     ('B','B12 deficiency'),
     ('C','Aplastic anaemia'),
     ('D','Hypersplenism'),
     ('E','Iron deficiency')],
    'C',
    'Aplastic anaemia = pancytopenia caused by failure of the bone marrow stem cells. The hallmark is a hypocellular marrow on biopsy (fat replaces normal blood-forming tissue). Treatment includes immunosuppression (anti-thymocyte globulin, ciclosporin) or bone marrow transplant.',
    story)

mcq(8,
    'A patient with known metastatic breast cancer has a CBC showing WBC 20 x10^9/L with immature myeloid cells (myelocytes) AND nucleated red blood cells in the peripheral blood. What term describes this pattern?',
    [('A','Reactive lymphocytosis'),
     ('B','Leucoerythroblastic picture'),
     ('C','Leukaemoid reaction'),
     ('D','Myelodysplastic syndrome'),
     ('E','CLL')],
    'B',
    'A leucoerythroblastic picture (immature WBCs + nucleated RBCs in the peripheral blood) results from bone marrow infiltration — the marrow is physically crowded out by metastatic tumour, pushing immature cells into the circulation.',
    story)

mcq(9,
    'Which drug is a well-recognised cause of MACROCYTIC anaemia by inhibiting folate metabolism?',
    [('A','Diclofenac'),
     ('B','Methotrexate'),
     ('C','Amlodipine'),
     ('D','Atorvastatin'),
     ('E','Ramipril')],
    'B',
    'Methotrexate inhibits dihydrofolate reductase, blocking folate metabolism and therefore DNA synthesis in rapidly dividing cells including red cell precursors, causing megaloblastic macrocytic anaemia. Co-prescribing folic acid reduces (but does not eliminate) this effect.',
    story)

mcq(10,
    'A patient presents with microangiopathic haemolytic anaemia (schistocytes on film, low Hb, very low platelets), neurological confusion, and acute kidney injury. What is the most important immediate treatment?',
    [('A','Platelet transfusion'),
     ('B','Broad-spectrum antibiotics'),
     ('C','Plasma exchange (plasmapheresis)'),
     ('D','IV iron infusion'),
     ('E','Corticosteroids alone')],
    'C',
    'This is THROMBOTIC THROMBOCYTOPENIC PURPURA (TTP) — the pentad includes MAHA, thrombocytopenia, neurological symptoms, fever, and renal failure. Caused by ADAMTS13 deficiency (congenital or acquired). Platelet transfusion is CONTRAINDICATED as it can worsen thrombosis. Plasma exchange (plasmapheresis) is the life-saving treatment — it replaces the missing ADAMTS13 enzyme.',
    story)

divider(story)

# §9 Answer Key
story.append(PageBreak())
sec_header('Section 9: Answer Key', story)
info_box('<b>Check your answers below.</b> Read each explanation carefully — especially for the questions you got wrong.', story)
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
    [Paragraph('MASTER MEMORY SUMMARY — COMPLETE BLOOD COUNT (CBC / FBC)', sGrnB)],
    [Paragraph('5-STEP READ: (1) Hb — anaemia or polycythaemia? (2) MCV — why? (3) WBC differential — which cell type and what does it mean? (4) Platelets — bleeding or thrombotic risk? (5) Blood film — when in doubt.', sGrn)],
    [Paragraph('MICROCYTIC (MCV <80): iron deficiency (low ferritin) | thalassaemia (normal/high ferritin, target cells) | anaemia of chronic disease (normal/high ferritin). NORMOCYTIC: acute blood loss | chronic disease | CKD (low EPO) | haemolysis | aplastic anaemia. MACROCYTIC: B12/folate (hypersegmented neutrophils = megaloblastic) | alcohol | liver | hypothyroidism | drugs (methotrexate, hydroxycarbamide).', sGrn)],
    [Paragraph('WBC DIFFERENTIAL: neutrophilia = bacteria/steroids/MI/stress. Neutropenia <0.5 = life-threatening infection risk. Lymphocytosis = viral/CLL (smear cells). Eosinophilia = allergy/parasites/Addisons/drugs. Basophilia = think CML. BLAST CELLS = call haematology NOW.', sGrn)],
    [Paragraph('KEY PATTERNS: Pancytopenia = aplastic anaemia / B12/folate / marrow infiltration. PV = raised Hb + raised WBC + raised platelets + JAK2 + aquagenic pruritus. CLL = elderly + massive lymphocytosis + smear cells + feels well. TTP = MAHA + thrombocytopenia + neuro + renal (DO NOT give platelets, give plasma exchange). ITP = isolated thrombocytopenia, normal Hb and WBC.', sGrn)],
    [Paragraph('IRON DEFICIENCY: low Hb + low MCV + low ferritin + reactive thrombocytosis. THALASSAEMIA TRAIT: low MCV but Hb mildly reduced or normal, ferritin normal, target cells, ethnicity clue. Always check both before labelling iron deficiency.', sGrn)],
]
innerG = Table(gRows, colWidths=[CW-4])
innerG.setStyle(gTS1)
outerG = Table([[innerG]], colWidths=[CW])
outerG.setStyle(gTSO)
story.append(outerG)
story.append(Spacer(1, 14))

story.append(HRFlowable(width=CW, thickness=1.5, color=HexColor('#0d5c63'), spaceAfter=6))
story.append(Paragraph('MRCP Revision Note: Complete Blood Count (CBC/FBC) — Interpretation, Key Patterns, and Self-Test  |  Sections 1-9', ParagraphStyle('FT', fontName='DV-I', fontSize=8, leading=11, textColor=HexColor('#555555'), alignment=1)))

doc.build(story)
print('SUCCESS:', OUT)
