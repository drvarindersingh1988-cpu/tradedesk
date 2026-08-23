"""
MRCP VISUAL QUICK NOTE: Discoid Lupus Erythematosus (DLE) — Management
Short, visual, exam-focused. Presentation-style PDF. Easy to memorise.
"""
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

OUT = '/mnt/user-data/outputs/DLE_Discoid_Lupus_Quick_Note.pdf'
FONT_DIR = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('DV',   FONT_DIR + 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DV-B', FONT_DIR + 'DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DV-I', FONT_DIR + 'DejaVuSansMono-Oblique.ttf'))

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

sTitle = ParagraphStyle('TT', fontName='DV-B', fontSize=30, leading=36,
         textColor=WHITE, spaceAfter=4, alignment=1)
sSub   = ParagraphStyle('TS', fontName='DV-I', fontSize=13, leading=17,
         textColor=TEAL_L, spaceAfter=4, alignment=1)
sH1    = ParagraphStyle('H1', fontName='DV-B', fontSize=16, leading=22,
         textColor=TEAL, spaceBefore=10, spaceAfter=5)
sH2    = ParagraphStyle('H2', fontName='DV-B', fontSize=11, leading=15,
         textColor=TEAL, spaceAfter=3)
sBody  = ParagraphStyle('Bo', fontName='DV', fontSize=10, leading=15,
         textColor=NAVY, spaceAfter=4)
sImg   = ParagraphStyle('Im', fontName='DV-I', fontSize=9, leading=13,
         textColor=HexColor('#555555'), spaceAfter=5, alignment=1)
sAlert = ParagraphStyle('Al', fontName='DV-B', fontSize=10, leading=14,
         textColor=HexColor('#721c24'), spaceAfter=0)
sMem   = ParagraphStyle('MH', fontName='DV-B', fontSize=10, leading=14,
         textColor=HexColor('#856404'), spaceAfter=0)
sBIG   = ParagraphStyle('BG', fontName='DV-B', fontSize=22, leading=28,
         textColor=GREEN_D, spaceAfter=4, alignment=1)
sANSW  = ParagraphStyle('AN', fontName='DV-B', fontSize=14, leading=20,
         textColor=NAVY, spaceAfter=4, alignment=1)

def bp(text, st=None): return Paragraph(text, st or sBody)
def divider(story): story.append(Spacer(1,4)); story.append(HRFlowable(width=CW, thickness=0.6, color=TEAL_M, spaceAfter=6))

def mem(text, story):
    t = Table([[Paragraph(f'MEMORY: {text}', sMem)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),AMBER),('BOX',(0,0),(-1,-1),2,AMBER_B),
        ('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),14),
        ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,8))

def big_answer(text, story):
    t = Table([[Paragraph(text, sBIG)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),GREEN_L),('BOX',(0,0),(-1,-1),3,GREEN_D),
        ('LEFTPADDING',(0,0),(-1,-1),20),('RIGHTPADDING',(0,0),(-1,-1),20),
        ('TOPPADDING',(0,0),(-1,-1),16),('BOTTOMPADDING',(0,0),(-1,-1),16)]))
    story.append(t); story.append(Spacer(1,10))

def alert(text, story):
    t = Table([[Paragraph(f'✗ WRONG / DANGER: {text}', sAlert)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),RED_L),('BOX',(0,0),(-1,-1),2.5,RED_D),
        ('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),14),
        ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,6))

def info(text, story, bg=None, bd=None):
    t = Table([[Paragraph(text, sBody)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),bg or BLUE_L),('BOX',(0,0),(-1,-1),2,bd or BLUE_D),
        ('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),14),
        ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,6))

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
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    return t

# PIL toolkit
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

def draw_block(draw, x, y, text, font, fill, max_width, align='left', gap=0):
    lines = wrap_text(draw, text, font, max_width)
    cy = y
    for ln in lines:
        if align == 'center':
            w = text_w(draw, ln, font)
            draw.text((x + (max_width - w)/2, cy), ln, font=font, fill=fill, anchor='la')
        else:
            draw.text((x, cy), ln, font=font, fill=fill, anchor='la')
        cy += lh(font) + gap
    return cy

def hband(draw, W, title, font, pad, accent='#0d5c63'):
    inner_w = W - 2*pad
    lines = wrap_text(draw, title, font, inner_w)
    bar_h = len(lines)*lh(font)+32
    draw.rectangle([0,0,W-1,bar_h], fill=accent)
    draw_block(draw, pad, 16, title, font, '#ffffff', inner_w, align='center')
    return bar_h

def card(draw, x0, x1, y, title, body, ft, fb, accent, bg, pad=14, gap=3):
    iw = (x1-x0)-2*pad
    tl = wrap_text(draw, title, ft, iw); bl = wrap_text(draw, body, fb, iw) if body else []
    bh = len(tl)*lh(ft)+16
    bdy_h = (len(bl)*(lh(fb)+gap)+2*pad) if bl else 0
    draw.rectangle([x0,y,x1,y+bh], fill=accent)
    draw_block(draw, x0+pad, y+8, title, ft, '#ffffff', iw)
    if bl:
        draw.rectangle([x0,y+bh,x1,y+bh+bdy_h], fill=bg, outline=accent, width=3)
        draw_block(draw, x0+pad, y+bh+pad, body, fb, '#2b2b2b', iw, gap=gap)
    return y+bh+bdy_h

def finish(img, draw, W, bottom_y, footer_text, f_xs, accent='#0d5c63'):
    iw = W-60
    lines = wrap_text(draw, footer_text, f_xs, iw)
    fh = len(lines)*lh(f_xs)+20; top = bottom_y+14
    draw.rectangle([0,top,W-1,top+fh], fill=accent)
    draw_block(draw, 30, top+10, footer_text, f_xs, '#ffffff', iw, align='center')
    return img.crop((0,0,W,top+fh+6))

CF = {'T':26,'B':18,'XS':15,'XL':32}
PX = 46

print('Building diagrams...')

# ── DIAGRAM 1: Management Ladder ─────────────────────────────────────────────
def make_ladder():
    W, H_MAX = 900, 1700
    f = load_fonts(CF)
    img = Image.new('RGB',(W,H_MAX),'#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PX, W-PX
    hh = hband(draw, W, 'DLE MANAGEMENT — STEP-UP LADDER', f['T'], PX)
    yy = hh+22

    steps = [
        ('#28a745','#d4edda',
         'STEP 1 — ALL PATIENTS: Sun protection + lifestyle',
         'HIGH-FACTOR SUNSCREEN (SPF 50+) every day — even in winter, even indoors near windows. Avoid direct sun exposure 10am-4pm. Wear a wide-brim hat. STOP SMOKING — smoking reduces the effectiveness of hydroxychloroquine.'),
        ('#0d5c63','#dff2f1',
         'STEP 2 — FIRST-LINE TREATMENT: Topical corticosteroids',
         'Potent topical steroid (e.g., mometasone furoate, clobetasol propionate) applied to active lesions. Use for a limited course. If the rash responds — maintain with a milder steroid or calcineurin inhibitor. This step is what FAILED in the question.'),
        ('#e6a817','#fff3cd',
         'STEP 3 — NOT RESPONDING TO TOPICAL STEROIDS? → ORAL HYDROXYCHLOROQUINE',
         'THIS IS THE ANSWER. Dose: 200-400 mg daily (max 5 mg/kg/day). Takes 2-3 months to work — tell the patient this. Reduces UV sensitivity, modulates the autoimmune response. MONITORING: annual eye check (risk of retinopathy at cumulative doses). Effective in ~70% of DLE cases.'),
        ('#7d3c98','#f5eef8',
         'STEP 4 — PARTIAL RESPONSE OR FAILURE: Add or switch',
         'Add MEPACRINE (quinacrine) to hydroxychloroquine — safe to combine. OR switch to oral CHLOROQUINE if hydroxychloroquine fails. Alternatives: oral RETINOIDS (acitretin), THALIDOMIDE (highly effective but severe teratogen — strict contraception), DAPSONE (for bullous or widespread lesions), METHOTREXATE.'),
        ('#c0392b','#fde8e8',
         'STEP 5 — SEVERE OR REFRACTORY: Systemic immunosuppression',
         'Oral prednisolone SHORT courses (bridge while waiting for hydroxychloroquine to work — NOT long-term first choice for DLE). Azathioprine, mycophenolate mofetil, ciclosporin for refractory cases. Refer to dermatology/rheumatology.'),
    ]
    for accent, bg, title, body in steps:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 14

    final = finish(img, draw, W, yy,
        'ALWAYS: sunscreen (step 1). Topical steroid (step 2). If fails → ORAL HYDROXYCHLOROQUINE (step 3). This is the most tested step in MRCP.',
        f['XS'])
    return i2r(final, CW)

# ── DIAGRAM 2: Answer Options Explained ──────────────────────────────────────
def make_options():
    W, H_MAX = 900, 1800
    f = load_fonts(CF)
    img = Image.new('RGB',(W,H_MAX),'#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PX, W-PX
    hh = hband(draw, W, 'WHY EACH ANSWER OPTION IS RIGHT OR WRONG', f['T'], PX)
    yy = hh+22

    opts = [
        ('#c0392b','#fde8e8',
         '✗ A. UV LIGHT THERAPY — WRONG. CONTRAINDICATED.',
         'DLE is a PHOTOSENSITIVE disease. UV light TRIGGERS and WORSENS lupus skin lesions. This is one of the most important exam traps. UV phototherapy is used for psoriasis and vitiligo — NEVER for lupus.'),
        ('#28a745','#d4edda',
         '✓ B. ORAL HYDROXYCHLOROQUINE — CORRECT ANSWER.',
         'This is the standard second-line treatment when topical steroids have failed in DLE. It is an antimalarial drug that also has immunomodulatory and anti-inflammatory effects in the skin. Takes 2-3 months to work. Requires annual eye monitoring. About 70% of patients respond.'),
        ('#d4640a','#fef3e2',
         '✗ C. TOPICAL DAPSONE — WRONG. Not standard for DLE.',
         'Topical dapsone (Aczone gel) is used for acne. Oral dapsone has a role in bullous (blistering) lupus and widespread DLE, but it is a STEP 4 option — not the next step when topical steroids have simply failed in classic DLE.'),
        ('#d4640a','#fef3e2',
         '✗ D. ORAL PREDNISOLONE — WRONG as "most appropriate next step."',
         'Oral steroids can be used as a SHORT bridge while hydroxychloroquine takes effect, but they are NOT recommended as the definitive next step when topical steroids fail in DLE. Hydroxychloroquine is preferred because it is safer for long-term use. Steroids = bridge, not the answer the question is looking for.'),
        ('#c0392b','#fde8e8',
         '✗ E. TOPICAL HYDROXYCHLOROQUINE — WRONG. This formulation does not exist clinically.',
         'Hydroxychloroquine is only available as an ORAL tablet. There is no licensed topical formulation. This is a distractor option designed to catch candidates who know the drug name but are uncertain about the route.'),
    ]
    for accent, bg, title, body in opts:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 14

    final = finish(img, draw, W, yy,
        'THE TRAP IN THIS QUESTION: UV = contraindicated (photosensitive disease). Topical hydroxychloroquine = does not exist. Oral prednisolone = not the first choice here. ORAL HYDROXYCHLOROQUINE = correct.',
        f['XS'])
    return i2r(final, CW)

# ── DIAGRAM 3: Key facts to memorise ─────────────────────────────────────────
def make_keyfacts():
    W, H_MAX = 900, 1600
    f = load_fonts(CF)
    img = Image.new('RGB',(W,H_MAX),'#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PX, W-PX
    hh = hband(draw, W, 'DLE — KEY FACTS TO MEMORISE FOR THE EXAM', f['T'], PX)
    yy = hh+22

    facts = [
        ('#0d5c63','#dff2f1',
         'WHAT IS DLE?',
         'Discoid Lupus Erythematosus is a CHRONIC AUTOIMMUNE SKIN DISEASE. It causes erythematous (red), scaly, disc-shaped plaques, most commonly on the face, scalp and ears. If untreated, it leaves scarring and pigment change. It is part of the lupus spectrum — only ~5% of DLE patients develop systemic SLE (vs 70-80% of subacute cutaneous LE).'),
        ('#7d3c98','#f5eef8',
         'PHOTOSENSITIVITY — the most important single fact',
         'UV light worsens DLE. Sun protection is part of EVERY patient\'s treatment, regardless of what else is prescribed. This fact also rules out UV therapy as a treatment option — it will make things worse.'),
        ('#2471a3','#e8f4fd',
         'HYDROXYCHLOROQUINE MONITORING — the exam monitoring question',
         'The feared side effect is RETINOPATHY — cumulative-dose-dependent toxic damage to the retina that can cause permanent visual loss. Annual eye check (visual fields, OCT) is mandatory. Risk is low at standard doses (<5 mg/kg/day) for the first 5 years. Also: safe in pregnancy (unlike most immunosuppressants). Can prolong the QT interval — check ECG if other QT-prolonging drugs are being used.'),
        ('#d4640a','#fef3e2',
         'SMOKING — the clinical point examiners love',
         'Smoking REDUCES the efficacy of hydroxychloroquine in lupus skin disease. This is well-evidenced. Always advise smoking cessation as part of DLE management — it is not just general health advice here, it specifically improves treatment response.'),
    ]
    for accent, bg, title, body in facts:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 14

    final = finish(img, draw, W, yy,
        'DLE = photosensitive chronic autoimmune skin disease. UV worsens it. Hydroxychloroquine treats it. Annual eye check mandatory. Smoking impairs treatment response.',
        f['XS'])
    return i2r(final, CW)

img_ladder  = make_ladder()
img_options = make_options()
img_facts   = make_keyfacts()

print('Diagrams done.')

# ═══════════════════════════════════════════════════════════════════════════
# STORY BUILD
# ═══════════════════════════════════════════════════════════════════════════
story = []

# ── Cover ──────────────────────────────────────────────────────────────────
cover_bg = Table([[
    Paragraph('DISCOID LUPUS ERYTHEMATOSUS', sTitle),
]], colWidths=[CW])
cover_bg.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,-1),TEAL),
    ('LEFTPADDING',(0,0),(-1,-1),20),('RIGHTPADDING',(0,0),(-1,-1),20),
    ('TOPPADDING',(0,0),(-1,-1),18),('BOTTOMPADDING',(0,0),(-1,-1),8),
]))
story.append(cover_bg)
sub_bg = Table([[Paragraph('Management, Drug Choices and Why They Work — MRCP Quick Visual Note', sSub)]], colWidths=[CW])
sub_bg.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),TEAL_M),
    ('LEFTPADDING',(0,0),(-1,-1),20),('RIGHTPADDING',(0,0),(-1,-1),20),
    ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),14),]))
story.append(sub_bg)
story.append(Spacer(1, 14))

# ── The question + answer (big visual) ────────────────────────────────────
story.append(Paragraph('THE QUESTION', ParagraphStyle('QH', fontName='DV-B', fontSize=13, leading=18, textColor=TEAL, spaceAfter=4)))
info('<b>A 34-year-old female with discoid lupus erythematosus has an erythematous, scaly rash on her face that has NOT responded to topical steroid creams. What is the most appropriate next step?</b>', story)

big_answer('✓  ORAL HYDROXYCHLOROQUINE  ✓', story)

# ── One-line rule ─────────────────────────────────────────────────────────
rule_t = Table([[Paragraph(
    'THE RULE: Topical steroids → if no response → ORAL HYDROXYCHLOROQUINE (not more topical treatment, not UV, not oral prednisolone as the first choice)',
    ParagraphStyle('RU', fontName='DV-B', fontSize=12, leading=17, textColor=WHITE, alignment=1))]], colWidths=[CW])
rule_t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),HexColor('#0d5c63')),
    ('LEFTPADDING',(0,0),(-1,-1),18),('RIGHTPADDING',(0,0),(-1,-1),18),
    ('TOPPADDING',(0,0),(-1,-1),14),('BOTTOMPADDING',(0,0),(-1,-1),14),]))
story.append(rule_t)
story.append(Spacer(1, 14))

alert('UV LIGHT THERAPY is CONTRAINDICATED in lupus — UV triggers and worsens the disease. This is a deliberately placed trap in the question.', story)
divider(story)

# ── Management ladder ─────────────────────────────────────────────────────
story.append(Paragraph('Section 1: The Management Ladder', ParagraphStyle('SH', fontName='DV-B', fontSize=15, leading=20, textColor=TEAL, spaceBefore=8, spaceAfter=5)))
story.append(img_ladder)
story.append(bp('Five-step treatment ladder for DLE — from sunscreen to systemic immunosuppression', sImg))
story.append(Spacer(1,8))
divider(story)

# ── Options explained ─────────────────────────────────────────────────────
story.append(Paragraph('Section 2: Why Each Answer Option Is Right or Wrong', ParagraphStyle('SH', fontName='DV-B', fontSize=15, leading=20, textColor=TEAL, spaceBefore=8, spaceAfter=5)))
story.append(img_options)
story.append(bp('Colour-coded: green = correct, orange = wrong for other reasons, red = dangerous/contraindicated', sImg))
story.append(Spacer(1,8))
divider(story)

# ── Key facts ─────────────────────────────────────────────────────────────
story.append(Paragraph('Section 3: Key Facts to Memorise', ParagraphStyle('SH', fontName='DV-B', fontSize=15, leading=20, textColor=TEAL, spaceBefore=8, spaceAfter=5)))
story.append(img_facts)
story.append(Spacer(1,6))

# Hydroxychloroquine quick-ref table
hcq_table = [
    ['Hydroxychloroquine — Quick Reference','Details'],
    ['Drug class','Antimalarial / immunomodulator'],
    ['Dose in DLE','200-400 mg/day orally (max 5 mg/kg/day)'],
    ['Onset of action','2-3 months — warn the patient'],
    ['Efficacy in DLE','~70% respond'],
    ['Main side effect to monitor','RETINOPATHY (cumulative dose-dependent)'],
    ['Monitoring','Annual eye check (visual fields + OCT)'],
    ['Safe in pregnancy?','YES — one of the few immunomodulators that is'],
    ['Effect of smoking','REDUCES efficacy — always advise cessation'],
    ['QT interval','Can prolong — check if co-prescribing other QT drugs'],
]
story.append(plain_table(hcq_table,[CW*0.45, CW*0.55]))
story.append(Spacer(1,8))

mem('DLE LADDER: SUN BLOCK → TOPICAL STEROID → ORAL HYDROXYCHLOROQUINE → MEPACRINE/CHLOROQUINE → THALIDOMIDE/RETINOIDS/DAPSONE → SYSTEMIC IMMUNOSUPPRESSION. The exam always tests Step 3.', story)
mem('UV = CONTRAINDICATED (photosensitive). TOPICAL hydroxychloroquine = does not exist. ORAL PREDNISOLONE = bridge not first choice. ORAL HYDROXYCHLOROQUINE = the answer.', story)
divider(story)

# ── Master summary card ───────────────────────────────────────────────────
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
    [Paragraph('MASTER MEMORY CARD — DISCOID LUPUS ERYTHEMATOSUS', sGrnB)],
    [Paragraph('WHAT IT IS: chronic autoimmune skin disease → red, scaly, disc-shaped plaques on face/scalp/ears. Photosensitive. Only ~5% develop systemic SLE.', sGrn)],
    [Paragraph('STEP 1 (ALWAYS): SPF 50+ sunscreen daily. Sun avoidance 10am-4pm. STOP SMOKING (impairs hydroxychloroquine response).', sGrn)],
    [Paragraph('STEP 2: TOPICAL STEROIDS (potent) — first active treatment.', sGrn)],
    [Paragraph('STEP 3 (EXAM ANSWER): TOPICAL STEROIDS FAIL → ORAL HYDROXYCHLOROQUINE 200-400 mg/day. Takes 2-3 months. Annual eye check (retinopathy risk). Safe in pregnancy.', sGrn)],
    [Paragraph('STEP 4: Mepacrine + hydroxychloroquine combination. Or chloroquine. Or oral retinoids, dapsone, thalidomide (teratogenic — strict contraception!).', sGrn)],
    [Paragraph('STEP 5 (SEVERE/REFRACTORY): Short-course oral prednisolone as bridge. Azathioprine/MMF/ciclosporin for refractory cases.', sGrn)],
    [Paragraph('THE TRAPS: (1) UV therapy = CONTRAINDICATED. (2) Topical hydroxychloroquine = does not exist. (3) Oral prednisolone = bridge, not first choice for Step 3. (4) Hydroxychloroquine works in ~70% — if it fails, add mepacrine or switch.', sGrn)],
]
innerG = Table(gRows, colWidths=[CW-4])
innerG.setStyle(gTS1)
outerG = Table([[innerG]], colWidths=[CW])
outerG.setStyle(gTSO)
story.append(outerG)
story.append(Spacer(1,14))

story.append(HRFlowable(width=CW, thickness=1.5, color=TEAL, spaceAfter=6))
story.append(Paragraph('MRCP Visual Quick Note: Discoid Lupus Erythematosus — Management, Drug Choices and Exam Traps',
    ParagraphStyle('FT', fontName='DV-I', fontSize=8, leading=11, textColor=HexColor('#555555'), alignment=1)))

doc.build(story)
print('SUCCESS:', OUT)
