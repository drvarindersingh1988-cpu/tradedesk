"""
MRCP REVISION NOTE: Iatrogenic Sciatic & Common Peroneal Nerve Injury From IM Injection
Page size: A3 Portrait (297mm x 420mm) for readable, spacious layout.
PIL diagram rule: text-safe card toolkit (wrap_text + card + header_band + finish) — no overlap.
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

OUT = '/mnt/user-data/outputs/Iatrogenic_Sciatic_Peroneal_Nerve_Injury_MRCP_Note.pdf'
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

# Interactive Q&A and self-test styles
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

# ── Interactive Professor Q&A dialogue block (Permanent Rule #19) ───────────
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

# ── End-of-topic MCQ self-test + separate answer key (Permanent Rule #20/21)
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

print('Building PIL diagrams (text-safe card layout)...')

# ── TEXT-SAFE DIAGRAM TOOLKIT (Permanent Rule #22) ──────────────────────────
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
    Height is fully computed from wrapped content — never guessed."""
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
    """Title band whose height is computed from the WRAPPED line count."""
    inner_w = W - 2 * pad_x
    lines = wrap_text(draw, title, font, inner_w)
    bar_h = len(lines) * lh(font) + 32
    draw.rectangle([0, 0, W - 1, bar_h], fill=accent)
    draw_block(draw, pad_x, 16, title, font, text_color, inner_w, align='center')
    return bar_h

def finish(img, draw, W, bottom_y, footer_text, f_xs, accent='#0d5c63'):
    """Dark footer band whose height is computed from the WRAPPED line count,
    then crop the canvas to the REAL content height."""
    inner_w = W - 60
    lines = wrap_text(draw, footer_text, f_xs, inner_w)
    foot_h = len(lines) * lh(f_xs) + 20
    top = bottom_y + 14
    draw.rectangle([0, top, W - 1, top + foot_h], fill=accent)
    draw_block(draw, 30, top + 10, footer_text, f_xs, '#ffffff', inner_w, align='center')
    return img.crop((0, 0, W, top + foot_h + 6))

CARD_FONTS = {'T': 24, 'B': 17, 'XS': 14}
PAD_X = 46

# ── PIL 1: The sciatic nerve — origin, course, and its two divisions ───────
def make_sciatic_anatomy():
    W, H_MAX = 900, 1500
    f = load_fonts(CARD_FONTS)
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PAD_X, W - PAD_X
    hh = header_band(draw, W, 'THE SCIATIC NERVE — ORIGIN, COURSE AND ITS TWO DIVISIONS', f['T'], PAD_X)

    yy = hh + 22
    yy = card(draw, x0, x1, yy,
        'ORIGIN — THE SACRAL PLEXUS (ROOTS L4, L5, S1, S2, S3)',
        'The sciatic nerve is the LARGEST nerve in the body. It is formed from the ventral rami of L4-S3 inside the pelvis, leaves through the greater sciatic foramen, and runs deep to (almost always BELOW) piriformis into the buttock.',
        f['B'], f['XS'], '#0d5c63', '#dff2f1')
    yy += 16
    yy = card(draw, x0, x1, yy,
        'COURSE THROUGH THE BUTTOCK — WHY IM INJECTIONS MATTER',
        'In the buttock, the sciatic nerve runs roughly midway between the greater trochanter (hip) and the ischial tuberosity (sit bone), deep to gluteus maximus. ANY injection placed too low and too medial in the buttock (the classic "dorsogluteal" site) can pierce or bathe this nerve in drug.',
        f['B'], f['XS'], '#c0392b', '#fde8e8')
    yy += 16
    yy = card(draw, x0, x1, yy,
        'TWO BUNDLES TRAVELLING TOGETHER — TIBIAL + COMMON PERONEAL',
        'The sciatic nerve is really TWO nerves wrapped in one sheath from the very start: the TIBIAL division (medial, from anterior divisions of L4-S3) and the COMMON PERONEAL (FIBULAR) division (lateral, from posterior divisions of L4-S2). They usually split apart at the apex of the popliteal fossa, but a single injury in the buttock can damage one division far more than the other.',
        f['B'], f['XS'], '#7d3c98', '#f5eef8')
    yy += 16
    yy = card(draw, x0, x1, yy,
        'WHY THE PERONEAL DIVISION IS HIT HARDER — THE KEY EXAM FACT',
        'The common peroneal division is more LATERALLY placed and more LOOSELY tethered within the sciatic nerve sheath, making it more vulnerable to compression, traction and needle/chemical injury than the tibial division. This is why an injection injury to the sciatic nerve so often produces a "common peroneal nerve palsy" picture (foot drop, dorsum numbness) with relatively SPARED tibial function (plantarflexion and sole sensation intact) — exactly as in this patient.',
        f['B'], f['XS'], '#d4640a', '#fef3e2')
    yy += 16
    yy = card(draw, x0, x1, yy,
        'BELOW THE KNEE — THE COMMON PERONEAL NERVE SPLITS AGAIN',
        'At the fibular neck (where it winds around the bone, very superficially — another classic injury site), the common peroneal nerve divides into the SUPERFICIAL PERONEAL nerve (evertor muscles + lateral lower leg/dorsum sensation) and the DEEP PERONEAL nerve (dorsiflexors of foot/toes + first web space sensation only).',
        f['B'], f['XS'], '#1a8a94', '#e0f4f5')

    final = finish(img, draw, W, yy,
        'KEY FOR MRCP — sciatic nerve = tibial + common peroneal "two nerves in one sheath"; the peroneal division is the lateral, looser, more vulnerable one',
        f['XS'])
    return i2r(final, CW)

# ── PIL 2: Safe vs unsafe intramuscular injection sites ─────────────────────
def make_injection_sites():
    W, H_MAX = 900, 1500
    f = load_fonts(CARD_FONTS)
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PAD_X, W - PAD_X
    hh = header_band(draw, W, 'INTRAMUSCULAR INJECTION SITES — SAFE VS DANGEROUS', f['T'], PAD_X)

    yy = hh + 22
    yy = card(draw, x0, x1, yy,
        'VENTROGLUTEAL SITE — THE RECOMMENDED "SAFE" SITE',
        'Found by placing the heel of the hand on the greater trochanter, index finger on the anterior superior iliac spine, and middle finger spread back along the iliac crest — the injection goes into the triangle between the fingers (gluteus medius/minimus). NO major nerve or vessel runs through this triangle. This is the FIRST CHOICE site for IM injections in adults.',
        f['B'], f['XS'], '#28a745', '#d4edda')
    yy += 16
    yy = card(draw, x0, x1, yy,
        'DORSOGLUTEAL SITE — THE TRADITIONAL "DANGER ZONE"',
        'The classic "upper outer quadrant of the buttock" site, used for decades. The sciatic nerve runs directly beneath this region in a significant minority of people, and its course is variable. A needle placed too low, too medial, or too deep can directly traumatise the nerve, or deposit an irritant drug close enough to cause a chemical neuritis even WITHOUT direct needle contact.',
        f['B'], f['XS'], '#c0392b', '#fde8e8')
    yy += 16
    yy = card(draw, x0, x1, yy,
        'WHY THIS PATIENT\'S INJECTION WAS HIGH-RISK',
        'IM diclofenac was given into the LEFT HIP/BUTTOCK for renal colic — a common, well-intentioned choice. But diclofenac is a known chemical irritant to nerve tissue if deposited close to the sciatic nerve, and the IMMEDIATE numbness "below the knee" reported at the moment of injection strongly suggests the needle tip was at, or very near, the sciatic nerve itself.',
        f['B'], f['XS'], '#d4640a', '#fef3e2')
    yy += 16
    yy = card(draw, x0, x1, yy,
        'OTHER ALTERNATIVES — VASTUS LATERALIS AND DELTOID',
        'Vastus lateralis (anterolateral mid-thigh) is very safe and is the preferred site in infants and young children. The deltoid is convenient for small-volume injections (e.g., vaccines) but only suits volumes up to about 1 mL because of its small muscle bulk and the nearby axillary nerve and posterior circumflex humeral artery.',
        f['B'], f['XS'], '#2471a3', '#e8f4fd')
    yy += 16
    yy = card(draw, x0, x1, yy,
        'TECHNIQUE POINTS THAT REDUCE NERVE INJURY RISK',
        'Use the ventrogluteal site whenever possible for adults. Use the correct needle length for body habitus. Aspirate before injecting (where still recommended locally) to avoid intravascular injection. If the patient reports SUDDEN sharp pain, electric "shock-like" sensation, or numbness/tingling radiating down the limb DURING injection — STOP immediately and withdraw; this is the warning sign of needle-nerve contact.',
        f['B'], f['XS'], '#1a8a94', '#e0f4f5')

    final = finish(img, draw, W, yy,
        'MEMORY — "VENTRO is BETTER, DORSO is DANGER": ventrogluteal = nerve-free triangle; dorsogluteal = sciatic nerve territory',
        f['XS'])
    return i2r(final, CW)

# ── PIL 3: Sensory territories of the leg and foot ──────────────────────────
def make_sensory_map():
    W, H_MAX = 1500, 900
    f = load_fonts(CARD_FONTS)
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PAD_X, W - PAD_X
    hh = header_band(draw, W, 'SENSORY TERRITORIES OF THE LEG AND FOOT — MAPPING THE NUMBNESS', f['T'], PAD_X)

    nerves = [
        ('#c0392b', '#fde8e8', 'DEEP PERONEAL NERVE — first web space ONLY',
         'Supplies a SMALL "postage stamp" patch of skin between the 1st and 2nd toes (the dorsal first web space) — and NOTHING else. This patient\'s numbness, confined to the area "from the metatarsal joint to the big toe," is the textbook deep peroneal sensory territory.'),
        ('#d4640a', '#fef3e2', 'SUPERFICIAL PERONEAL NERVE — most of the dorsum of the foot',
         'Supplies sensation to most of the DORSUM (top) of the foot and the lower lateral shin, EXCEPT the first web space (deep peroneal) and the lateral border of the foot (sural). Loss here points to a lesion above the ankle but at/below where the two peroneal branches separate.'),
        ('#7d3c98', '#f5eef8', 'SURAL NERVE — lateral border of foot and little toe',
         'A purely sensory branch (from tibial + common peroneal contributions) supplying the lateral border of the foot and the little toe — often used for nerve biopsy because it is purely sensory.'),
        ('#2471a3', '#e8f4fd', 'TIBIAL NERVE / MEDIAL & LATERAL PLANTAR NERVES — the SOLE',
         'Supplies the entire SOLE of the foot (plantar surface) plus plantarflexion and toe flexion power. In this patient, the sole is normal and flexion is preserved — telling us the TIBIAL division is intact.'),
        ('#28a745', '#d4edda', 'SAPHENOUS NERVE — medial shin and medial ankle',
         'A sensory branch of the FEMORAL nerve (NOT sciatic) supplying the medial side of the leg below the knee and the medial malleolus/ankle — useful as a "control" area: if THIS is also numb, the lesion is not isolated to the sciatic/peroneal system.'),
    ]
    yy = hh + 22
    for accent, bg, title, body in nerves:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 14

    final = finish(img, draw, W, yy,
        'EXAM FACT — a numb first web space ALONE = deep peroneal nerve; numb whole dorsum = superficial peroneal; numb sole = tibial; numb medial shin (femoral territory) = NOT sciatic at all',
        f['XS'])
    return i2r(final, CW)

# ── PIL 4: Foot drop — where is the lesion? Five differentials side by side ─
def make_foot_drop_diff():
    W, H_MAX = 900, 1700
    f = load_fonts(CARD_FONTS)
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PAD_X, W - PAD_X
    hh = header_band(draw, W, 'FOOT DROP — FIVE DIFFERENTIALS AND HOW TO TELL THEM APART', f['T'], PAD_X)

    diffs = [
        ('#c0392b', '#fde8e8', '1. COMMON PERONEAL NERVE PALSY (fibular neck)',
         'Foot drop + numbness over dorsum/first web space. ANKLE JERK NORMAL (S1 intact). FOOT INVERSION (tibialis posterior, tibial nerve) PRESERVED. Classic causes: leg crossing, prolonged squatting, tight plaster cast, weight loss.'),
        ('#d4640a', '#fef3e2', '2. SCIATIC NERVE LESION (e.g., this patient — buttock injection)',
         'Foot drop + dorsum numbness (peroneal division) BUT may also have variable involvement of tibial division (plantarflexion/sole sensation/ankle jerk). Hip/buttock pain or a clear injection history is the giveaway. Severity ranges from a pure "peroneal-pattern" picture (as here) to a complete sciatic palsy.'),
        ('#e6a817', '#fff3cd', '3. L5 RADICULOPATHY (lumbar disc prolapse)',
         'Foot drop + numbness over dorsum/lateral shin BUT ALSO weak hip abduction (gluteus medius, also L5) and often weak FOOT INVERSION (tibialis posterior is L5, NOT purely a peroneal-nerve muscle). Back pain, positive straight-leg raise. Ankle jerk usually NORMAL (S1).'),
        ('#7d3c98', '#f5eef8', '4. S1 RADICULOPATHY',
         'Weak plantarflexion and eversion, numbness over the SOLE/lateral foot, and a REDUCED OR ABSENT ankle jerk. True "foot drop" (dorsiflexion weakness) is uncommon — included here as the classic ankle-jerk contrast to the others.'),
        ('#2471a3', '#e8f4fd', '5. PERIPHERAL POLYNEUROPATHY (e.g., diabetes, alcohol)',
         'Usually BILATERAL and symmetrical, "glove and stocking" sensory loss, often with absent ankle jerks BILATERALLY, and a longer history of gradual numbness/tingling rather than a single triggering event.'),
    ]
    yy = hh + 22
    for accent, bg, title, body in diffs:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 14

    final = finish(img, draw, W, yy,
        'THE THREE QUESTIONS THAT LOCALISE FOOT DROP — (1) Ankle jerk normal or absent? (2) Inversion (tibialis posterior) weak or strong? (3) Hip abduction weak or strong?',
        f['XS'])
    return i2r(final, CW)

# ── PIL 5: Seddon's classification of nerve injury ──────────────────────────
def make_seddon_classification():
    W, H_MAX = 900, 1500
    f = load_fonts(CARD_FONTS)
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PAD_X, W - PAD_X
    hh = header_band(draw, W, "SEDDON'S CLASSIFICATION OF NERVE INJURY — WHAT KIND OF INJURY IS THIS?", f['T'], PAD_X)

    grades = [
        ('#28a745', '#d4edda', '1. NEURAPRAXIA — "the nerve is stunned, not torn"',
         'A temporary conduction block — myelin sheath is locally damaged but the axon itself stays intact (continuity preserved). Caused by compression, stretch, or local chemical irritation (e.g., a drug deposited next to the nerve). RECOVERY: typically days to a few weeks, usually COMPLETE. This is the most likely injury type in this patient — a chemical/compressive insult from the injection, with immediate numbness but normal-looking nerve on imaging.'),
        ('#e6a817', '#fff3cd', '2. AXONOTMESIS — "the wire is cut, but the conduit survives"',
         'The axon itself is disrupted but the surrounding connective tissue sheaths (endoneurium, perineurium, epineurium) remain intact. Caused by more severe crush or stretch injury. RECOVERY: SLOW — the axon must regrow down its own tube at roughly 1 mm per day ("an inch a month"), so recovery can take MONTHS, but the prognosis is usually good because the regrowing axon is guided back to its correct target.'),
        ('#c0392b', '#fde8e8', '3. NEUROTMESIS — "the whole cable is severed"',
         'Complete disruption of the axon AND all surrounding connective tissue layers — usually from direct laceration (e.g., a needle cutting through the nerve) or severe traction. RECOVERY: will NOT occur spontaneously to any useful degree; SURGICAL repair (nerve grafting/repair) is required, and outcomes are often incomplete even then.'),
        ('#2471a3', '#e8f4fd', 'WHY THIS MATTERS FOR THIS PATIENT',
         'The clinical picture — IMMEDIATE numbness at the moment of injection, a SHARPLY localised sensory deficit (deep peroneal territory only), PRESERVED motor power in flexion, and NO progressive weakness — is most consistent with NEURAPRAXIA (chemical/compressive), with an excellent chance of FULL recovery within days to a few weeks. Persistent or worsening deficit beyond 2-3 weeks should prompt nerve conduction studies to look for axonotmesis.'),
    ]
    yy = hh + 22
    for accent, bg, title, body in grades:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 16

    final = finish(img, draw, W, yy,
        'MEMORY — "PRAXIA pauses, TMESIS cuts": neurAPRAXIA = temporary pause in conduction (fast recovery); axonoTMESIS/neuroTMESIS = the axon is physically cut (slow/no recovery)',
        f['XS'])
    return i2r(final, CW)

img_sciatic   = make_sciatic_anatomy()
img_injsites  = make_injection_sites()
img_sensory   = make_sensory_map()
img_footdrop  = make_foot_drop_diff()
img_seddon    = make_seddon_classification()

print('PIL diagrams done.')

# ═══════════════════════════════════════════════════════════════════════════
# STORY BUILD
# ═══════════════════════════════════════════════════════════════════════════
story = []

story.append(Paragraph('IATROGENIC SCIATIC &amp; PERONEAL NERVE INJURY', sTitle))
story.append(Paragraph('From an Intramuscular Injection — Anatomy, Localisation, Differentials and Management — MRCP Part 1, Part 2 &amp; PACES, Interactive Edition', sSub))
story.append(HRFlowable(width=CW, thickness=2, color=TEAL, spaceAfter=10))

# §1 Clinical Scenario
sec_header('Section 1: The Clinical Scenario — A Real Case From The Ward', story)
story.append(bp('A man presents with sudden, severe LEFT FLANK PAIN — in the loin, radiating towards the lower abdomen and groin. He is restless and breathing fast with the pain. His blood pressure is normal, his pulse is around 55-56 beats per minute (relatively SLOW for someone in severe pain — a vagal response that is well-recognised in renal colic), and his oxygen saturation is normal.'))
story.append(bp('An ultrasound scan shows LEFT-SIDED HYDRONEPHROSIS (a swollen, fluid-filled kidney from back-pressure). Urinalysis shows RED BLOOD CELLS (RBCs) but the full blood count is normal. A LEFT URETERIC STONE is suspected, with a possible secondary urinary tract infection.'))
story.append(bp('To control the pain, the patient is given <b>IM diclofenac into the LEFT BUTTOCK/HIP</b>. At the exact moment of this injection, he reports an IMMEDIATE sensation of numbness spreading down the back of his leg, BELOW THE KNEE. He is then given <b>IM Platifillin</b> (an antispasmodic, hyoscine/atropine-like drug used for ureteric spasm) and <b>IV pantoprazole</b> (a proton pump inhibitor, often co-prescribed with NSAIDs/antispasmodics to protect the stomach). He feels better afterwards, though he has one episode of vomiting. Immediately after the injection, he is UNABLE TO STAND on the left leg.'))
story.append(bp('Two to three hours later, after sleeping, he feels generally better — but now notices a PERSISTENT NUMBNESS over the dorsum (top) of the left foot, SHARPLY LOCALISED to the area between the first metatarsal joint and the big toe. He can feel and move ALL his other toes entirely normally. He CAN FLEX the foot and toes, but CANNOT EXTEND (dorsiflex) them in this specific area. Sensation and power are otherwise completely normal.'))
story.append(bp('His past history includes previous surgery for varicose veins in the left leg, and he has visible "corona phlebectatica" — a fan-shaped cluster of small dilated veins around the ankle, a sign of chronic venous insufficiency, noted here as an INCIDENTAL finding.'))
professor_says('Two things are happening in this patient AT THE SAME TIME, and your job is to keep them in two separate mental folders. FOLDER ONE: a left ureteric stone causing renal colic — needs imaging, analgesia, and urology follow-up. FOLDER TWO: a brand-new neurological deficit that appeared at the EXACT MOMENT of an intramuscular injection in the buttock — this is now an iatrogenic (treatment-caused) problem in its own right, and it is THIS folder that we will spend most of this note on, because it is the one most likely to be missed, and most likely to appear in your exam.', story)
memory_hook('THE TIMING IS THE DIAGNOSIS: numbness appearing AT THE INSTANT of an IM injection into the buttock, in the distribution below the knee, points overwhelmingly to a SCIATIC NERVE INJURY from that injection — not a complication of the kidney stone itself.', story)
divider(story)

# §2 Sciatic Nerve Anatomy
sec_header('Section 2: Sciatic Nerve Anatomy — One Nerve, Two Divisions', story)
professor_says('You cannot localise ANY peripheral nerve injury until you know the normal anatomy cold. The sciatic nerve is the single most commonly injured nerve from gluteal intramuscular injections — and almost always, it is one specific HALF of it that suffers the most. Learn this anatomy and the rest of this topic falls into place by logic alone.', story)

story.append(img_sciatic)
story.append(bp('The sciatic nerve: formed from L4-S3, runs through the buttock as two divisions wrapped together, splits into tibial and common peroneal nerves', sImg))
story.append(Spacer(1, 6))

image_search_box('sciatic nerve anatomy gluteal region tibial common peroneal divisions', 'Google Images / Radiopaedia', story)

qa_block(
    'A patient receives an IM injection in the buttock and immediately feels numbness shooting down the back of the leg, below the knee. Hours later, he has numbness over the dorsum of the foot and weak toe extension, but normal sole sensation and normal toe flexion.',
    'Why would ONE injection injure the dorsiflexors and dorsum sensation, but completely SPARE the plantarflexors and sole sensation, if both sets of muscles are supplied by branches of the SAME sciatic nerve?',
    'Remember that the sciatic nerve is not really one cable — it is TWO cables (tibial and common peroneal) running side by side in one sheath. Which of the two is more loosely attached and more laterally placed, and therefore more exposed to a needle or to an irritant drug?',
    'Because the sciatic nerve is anatomically TWO separate nerve bundles — the TIBIAL division (medial, supplies plantarflexion and sole sensation) and the COMMON PERONEAL division (lateral, supplies dorsiflexion and dorsum sensation) — travelling together inside one connective tissue sheath. The common peroneal division is more laterally placed and more loosely tethered, making it far more vulnerable to a misplaced needle or to a chemically irritant drug deposited nearby. A single injection can therefore injure ONE division while leaving the other completely untouched — exactly the pattern seen in this patient.',
    story)

story.append(bp('<b>Quick anatomy recap — the journey from spine to toes:</b>'))
for pt in [
    '<b>Roots:</b> Ventral rami of L4, L5, S1, S2, S3 combine in the sacral plexus.',
    '<b>Exit:</b> Leaves the pelvis through the greater sciatic foramen, usually passing BELOW piriformis (a small but important muscle — see Section 4 for "piriformis syndrome").',
    '<b>Buttock:</b> Runs roughly midway between the greater trochanter and the ischial tuberosity, deep to gluteus maximus — directly beneath the classic "dorsogluteal" injection site.',
    '<b>Thigh:</b> Supplies the hamstrings (knee flexion) and part of adductor magnus.',
    '<b>Popliteal fossa:</b> Divides into the TIBIAL nerve (continues down the back of the calf, supplies plantarflexors/toe flexors and sole sensation) and the COMMON PERONEAL (FIBULAR) nerve (winds around the fibular neck, supplies dorsiflexors/evertors and dorsum sensation).',
    '<b>Below the knee:</b> Common peroneal splits into SUPERFICIAL peroneal (eversion + lateral lower leg/dorsum sensation) and DEEP peroneal (dorsiflexion of foot and toes + first web space sensation only).',
]:
    story.append(bp(f'  • {pt}'))
memory_hook('"TIP-TOP": TIbial = Plantarflexion (push your foot down, like standing on TIPtoe); common PeronEal = TOP of foot (dorsiflexion, "TOP" = peroneal). If the patient cannot lift the TOP of the foot but CAN push down (tiptoe), the PERONEAL component is the one in trouble.', story)
divider(story)

# §3 Injection Sites
sec_header('Section 3: Safe vs Unsafe Intramuscular Injection Sites', story)
professor_says('Every IM injection is, in theory, an invasive procedure with a small but real risk of nerve injury. The WHOLE of this complication is preventable with correct site selection — which is exactly why it is such a popular "system error" or "patient safety" topic in PACES communication and ethics stations.', story)

story.append(img_injsites)
story.append(bp('Ventrogluteal (safe, nerve-free) vs dorsogluteal (sciatic nerve territory) injection sites', sImg))
story.append(Spacer(1, 6))

image_search_box('ventrogluteal vs dorsogluteal injection site landmarks', 'Google Images / Nursing anatomy diagrams', story)

story.append(bp('<b>How to find the ventrogluteal site (the one to teach and to use):</b>'))
for pt in [
    'Patient lying on their side or back. Place the heel of your hand on the GREATER TROCHANTER of the femur (the bony prominence of the hip).',
    'Point your INDEX finger towards the ANTERIOR SUPERIOR ILIAC SPINE (ASIS).',
    'Spread your MIDDLE finger back along the iliac crest, away from the index finger, forming a "V" or triangle shape with your fingers.',
    'The injection goes into the CENTRE of this triangle — into gluteus medius/minimus, an area free of major nerves and vessels.',
]:
    story.append(bp(f'  • {pt}'))

alert_box('THE SCIATIC NERVE INJURY WARNING SIGN: if a patient reports a sudden electric shock-like pain, a "shooting" sensation, or numbness/tingling radiating DOWN THE LEG at the moment of injection — STOP, withdraw the needle immediately, and document the event clearly. Continuing to inject after this warning is what converts a possible neurapraxia into a more serious axonal injury.', story)
memory_hook('REMEMBER THE TRIANGLE: ventrogluteal = a triangle made with YOUR OWN HAND on the patient\'s hip, away from any nerve. Dorsogluteal ("upper outer quadrant") sits directly over the variable course of the sciatic nerve — avoid it for routine IM injections in adults wherever the ventrogluteal site is accessible.', story)
divider(story)

# §4 Mechanisms of Nerve Injury — Seddon's Classification
sec_header("Section 4: Mechanisms of Nerve Injury — Seddon's Classification", story)
professor_says('Once you have decided "this is a nerve injury," the very next question — every single time, in the exam and on the ward — is "what KIND of nerve injury, and what does that mean for recovery?" Seddon\'s classification answers exactly that question, and it is one of the most reliably examined pieces of neuroanatomy in MRCP.', story)

story.append(img_seddon)
story.append(bp("Seddon's classification: neurapraxia, axonotmesis and neurotmesis — mechanism and recovery compared", sImg))
story.append(Spacer(1, 6))

story.append(bp('<b>How a needle or an injected drug can injure a nerve — three mechanisms:</b>'))
for pt in [
    '<b>Direct mechanical trauma:</b> the needle tip itself touches or partially pierces the nerve — usually causes IMMEDIATE pain/paraesthesia at the moment of injection (as in this patient).',
    '<b>Chemical/toxic neuritis:</b> the injected drug (diclofenac is a recognised culprit) is deposited within or immediately adjacent to the nerve sheath, causing local inflammation and temporary conduction block — even if the needle itself never touched the nerve fascicles.',
    '<b>Compression/ischaemia:</b> a haematoma or swelling around the nerve after injection compresses it from outside, reducing its blood supply.',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 4))

qa_block(
    'This patient had IMMEDIATE numbness at the moment of injection, a sensory deficit confined to a single small area (the first web space/dorsum of the big toe), preserved motor power in flexion, and no progressive weakness over the following hours.',
    'Based on Seddon\'s classification, which type of nerve injury is MOST LIKELY here, and what does that predict about his recovery timeline?',
    'Think about which type of injury causes a temporary "switching off" of conduction without physically destroying the axon — and how quickly that type typically recovers.',
    'This pattern — immediate onset, localised, with motor sparing and no progression — is most consistent with NEURAPRAXIA (a local conduction block from compression or chemical irritation, with the axon itself intact). The expected recovery is FULL, usually within DAYS TO A FEW WEEKS. If the deficit instead WORSENED over the following days, or failed to improve by 2-3 weeks, axonotmesis would become more likely, and nerve conduction studies/EMG would be the next step (see Section 9).',
    story)

story.append(bp('<b>A note on "piriformis syndrome" — a related but DIFFERENT mechanism:</b>'))
story.append(bp('Piriformis syndrome is sciatic nerve irritation caused by the piriformis MUSCLE itself compressing or spasming around the nerve (sometimes the nerve even runs THROUGH the muscle in some people) — usually from prolonged sitting, trauma, or overuse, NOT from an injection. It typically causes deep buttock pain radiating down the leg, often WITHOUT a clear sensory/motor deficit as sharp as seen here. It is mentioned because it is a classic differential for "sciatica-like" pain in MRCP, but the clear temporal link to an injection in this patient points firmly away from it.'))
memory_hook("SEDDON'S THREE — NEURAPRAXIA (conduction pause, axon intact, recovers in days-weeks), AXONOTMESIS (axon cut, sheath intact, regrows at ~1mm/day = months), NEUROTMESIS (everything cut, needs surgery). This patient's picture = textbook NEURAPRAXIA.", story)
divider(story)

# §5 Sensory Territories — Mapping the Numbness
sec_header('Section 5: Sensory Territories of the Leg and Foot — Mapping the Numbness', story)
professor_says('In peripheral neurology, the SHAPE of the sensory loss is often more diagnostic than any imaging test. A patient cannot draw you a dermatome map, but if YOU know the maps, their description of "numb here, but not there" becomes a precise localising tool — exactly as it was in this case.', story)

story.append(img_sensory)
story.append(bp('Sensory territories: deep peroneal (first web space), superficial peroneal (dorsum), sural (lateral foot), tibial (sole), and saphenous (medial shin) — non-sciatic control territory', sImg))
story.append(Spacer(1, 6))

image_search_box('deep peroneal nerve sensory distribution first web space dorsum foot', 'Google Images / Radiopaedia', story)

qa_block(
    'The patient describes numbness "from the joint of the metatarsal bone to the big toe" on the dorsum of the left foot — and nowhere else. All other toes, the sole, and the rest of the leg feel completely normal.',
    'Which single named cutaneous nerve territory matches this description EXACTLY, and what does that tell you about WHICH division of the sciatic nerve, and WHICH branch below the knee, has been affected?',
    'There is one nerve in the entire leg whose sensory territory is famously TINY — just the skin between the first and second toes. Which nerve is this, and which division of the common peroneal nerve gives rise to it?',
    'This is the EXACT territory of the DEEP PERONEAL NERVE — a small "postage stamp" patch of skin over the first web space and the adjacent sides of the first and second toes, and NOTHING else. The deep peroneal nerve is a terminal branch of the COMMON PERONEAL nerve (itself the lateral division of the sciatic nerve). Therefore: the lesion has affected the COMMON PERONEAL DIVISION of the sciatic nerve, and within it, predominantly the DEEP PERONEAL branch — while the TIBIAL division (sole sensation, plantarflexion) and the SUPERFICIAL PERONEAL branch (most of the dorsum, eversion) remain intact. This is about as precisely localised as a peripheral nerve lesion can get on history alone.',
    story)

story.append(bp('<b>Why the saphenous nerve matters as a "control":</b>'))
story.append(bp('The saphenous nerve is a sensory branch of the FEMORAL nerve, supplying the medial shin and medial ankle — it has NOTHING to do with the sciatic nerve. If a patient has numbness here TOO, the problem cannot be confined to the sciatic/peroneal system, and a more proximal (e.g., lumbar plexus, cauda equina) or more diffuse (polyneuropathy) process must be considered. In THIS patient, the saphenous territory is entirely normal — another point supporting a clean, isolated, distal sciatic/peroneal lesion.'))
memory_hook('THE "POSTAGE STAMP" RULE — if the numb area is small, sharply defined, and confined to the first web space only, think DEEP PERONEAL NERVE. If it spreads across the whole top of the foot, think SUPERFICIAL PERONEAL or COMMON PERONEAL more proximally. If it includes the sole, think TIBIAL or full SCIATIC involvement.', story)
divider(story)

# §6 Motor Examination — Localising the Lesion
sec_header('Section 6: Motor Examination — Using "Foot Drop" To Localise The Lesion', story)
professor_says('Sensation tells you WHERE the skin is numb. Power tells you WHICH MUSCLES — and therefore which nerve ROOTS and which nerve TRUNKS — are affected. Combining the two is how you go from "something is wrong with the leg" to "the lesion is here, and only here." Always examine BOTH.', story)

story.append(bp('<b>The key movements to test, and what each one tells you:</b>'))
mot_table = [
    ['Movement Tested','Muscle(s)','Nerve','Root(s)','Finding In This Patient'],
    ['Ankle dorsiflexion\n(lift foot/toes UP)','Tibialis anterior,\nextensor digitorum\nlongus, extensor\nhallucis longus','Deep peroneal\n(from common\nperoneal)','L4, L5\n(mainly L5)','WEAK — cannot extend\nthe big toe/forefoot —\nthis IS the "foot drop"\ncomponent here.'],
    ['Ankle plantarflexion\n(push foot DOWN,\n"stand on tiptoe")','Gastrocnemius,\nsoleus','Tibial','S1, S2','NORMAL — patient\ncan flex the foot —\nTIBIAL division intact.'],
    ['Foot eversion\n(turn sole outward)','Peroneus longus\nand brevis','Superficial\nperoneal','L5, S1','Reported as\nessentially normal —\nsuperficial peroneal\nspared/mild.'],
    ['Foot inversion\n(turn sole inward)','Tibialis posterior','Tibial','L4, L5','NORMAL — an\nIMPORTANT negative:\nweak inversion would\npoint to L5 root or\nfull sciatic, not an\nisolated peroneal lesion.'],
    ['Knee flexion\n("bend the knee\nagainst resistance")','Hamstrings','Sciatic\n(both divisions,\nproximal branches)','L5, S1, S2','Not specifically\ndescribed — if WEAK,\nthis would suggest a\nmore PROXIMAL (higher,\nbuttock-level) lesion.'],
    ['Ankle (S1) reflex','Gastrocnemius/\nsoleus stretch reflex','Tibial','S1, S2','Expected NORMAL —\ntibial division intact;\nan ABSENT ankle jerk\nwould point away from\na pure peroneal lesion.'],
]
story.append(plain_table(mot_table,[CW*0.18, CW*0.18, CW*0.14, CW*0.1, CW*0.4]))
story.append(Spacer(1, 4))

qa_block(
    'On examination, the patient cannot dorsiflex his left big toe and forefoot (cannot lift them "up"), but plantarflexion (pushing down), foot inversion, and the ankle reflex are all NORMAL.',
    'Using ONLY the table above, build the localisation argument step by step: which nerve, which division, and roughly where along its course is the lesion most likely to be?',
    'Work from the BOTTOM up: if inversion (tibialis posterior, L4/L5 via the TIBIAL nerve) is normal, can the L5 root itself be the problem? If the ankle jerk (S1, tibial) is normal, can the WHOLE sciatic nerve be cut?',
    'NORMAL inversion (tibialis posterior — supplied by the TIBIAL nerve but carrying L4/L5 fibres) makes an L5 ROOT lesion unlikely, because an L5 radiculopathy would usually weaken inversion too. A NORMAL ankle jerk (S1, tibial nerve) makes a COMPLETE sciatic nerve transection unlikely. What remains is weakness confined to muscles supplied by the DEEP PERONEAL NERVE (extensor hallucis longus, extensor digitorum longus, tibialis anterior) — i.e. an isolated lesion of the COMMON PERONEAL DIVISION of the sciatic nerve, affecting predominantly its DEEP PERONEAL branch. Combined with the sensory findings from Section 5, this triangulates the lesion to the sciatic nerve at (or just distal to) the buttock, selectively involving the peroneal division — exactly where the injection needle would have been.',
    story)
memory_hook('FOOT DROP EXAM IN THREE MOVES: (1) Dorsiflexion — weak = peroneal problem. (2) Inversion — if ALSO weak, think L5 root, not just peroneal nerve. (3) Ankle jerk — if ALSO absent, think S1/tibial/full sciatic, not just peroneal nerve. Normal (2) and (3) = isolated common peroneal (or its deep branch) lesion.', story)
divider(story)

# §7 Foot Drop — Differential Diagnosis
sec_header('Section 7: Foot Drop — The Five Differentials, Side By Side', story)
professor_says('"Foot drop" is a SIGN, not a diagnosis — in the same way that "chest pain" is not a diagnosis. MRCP loves to give you a foot-drop vignette and then bury ONE extra clue (an absent reflex, a back pain history, a bilateral pattern, an injection history) that tells you exactly where the lesion really is. Train yourself to hunt for that one clue.', story)

story.append(img_footdrop)
story.append(bp('Foot drop — five differentials and the key bedside findings that separate them', sImg))
story.append(Spacer(1, 6))

story.append(bp('<b>Applying this to our patient — working through the five differentials:</b>'))
for pt in [
    '<b>Common peroneal nerve palsy at the fibular neck</b> — usually from external compression (leg crossing, prolonged squatting, weight loss, plaster cast) rather than an injection in the buttock; ankle jerk and inversion preserved (matches our patient on exam, but the HISTORY points higher, to the buttock).',
    '<b>Sciatic nerve lesion (this patient)</b> — buttock injection with immediate radiating numbness is the giveaway; the deficit can range from a mild "peroneal-pattern" picture (as here) to a full sciatic palsy depending on which fascicles are affected.',
    '<b>L5 radiculopathy</b> — look for back pain, a positive straight-leg raise, and WEAK INVERSION/hip abduction in addition to foot drop; ankle jerk usually preserved. Our patient has none of these — no back pain, normal inversion.',
    '<b>S1 radiculopathy</b> — weak plantarflexion/eversion, sole numbness, ABSENT ankle jerk; essentially the mirror image of our patient\'s findings (which shows normal plantarflexion and normal sole sensation).',
    '<b>Peripheral polyneuropathy</b> — would be BILATERAL and symmetrical with a longer history; our patient has a sudden, unilateral, temporally-linked-to-injection deficit.',
]:
    story.append(bp(f'  • {pt}'))
info_box('<b>The single most useful exam habit:</b> whenever you see "foot drop" in a vignette, immediately ask yourself THREE questions in order — (1) Is it ONE side or BOTH? (2) Is the ankle jerk present? (3) Is inversion (tibialis posterior) preserved? These three answers alone correctly localise the great majority of foot-drop vignettes in MRCP.', story)
memory_hook('"ONE NERVE, ONE ROOT, OR MANY NERVES?" — Common peroneal palsy = ONE nerve, distal, compressive. L5/S1 radiculopathy = ONE root, with back pain ± reflex change. Polyneuropathy = MANY nerves, bilateral, symmetrical, gradual. Sciatic injection injury = ONE nerve, proximal, with a clear temporal trigger.', story)
divider(story)

# §8 The Original Presentation — Flank Pain & Hydronephrosis
sec_header('Section 8: Back To Folder One — Flank Pain, Hydronephrosis and Haematuria', story)
professor_says('Do not let an interesting neurological complication make you forget the patient still has an undiagnosed left ureteric stone with hydronephrosis and possible infection. In MRCP, a vignette that introduces a "distractor" complication is often testing whether you can STILL manage the original problem correctly.', story)

story.append(bp('<b>Differential diagnosis of left flank pain with hydronephrosis and haematuria:</b>'))
flank_table = [
    ['Diagnosis','Key Supporting Features','Key Distinguishing Test'],
    ['Ureteric colic\n(stone) — most likely here','Sudden severe loin-to-groin pain,\nrestlessness (cannot lie still — unlike\nperitonitis), microscopic haematuria,\nhydronephrosis on ultrasound.','Non-contrast CT KUB —\ngold standard, identifies\n>99% of stones and their size/location.'],
    ['Pyelonephritis /\ninfected hydronephrosis\n(must exclude)','Fever, rigors, loin tenderness,\npossible sepsis. Can co-exist WITH\nan obstructing stone — an "infected\nobstructed system" is a UROLOGICAL\nEMERGENCY needing urgent decompression.','Urine culture, blood\ncultures, CRP/WCC,\ntemperature charting.'],
    ['Renal cell carcinoma','Painless or painful haematuria,\nflank mass, weight loss — usually\nmore insidious onset, older patients.','CT urogram with contrast\n(once stone/infection excluded).'],
    ['Ruptured/leaking AAA\n("never miss")','Sudden severe flank/back pain,\noften with haemodynamic instability,\npulsatile abdominal mass — a vascular\nemergency mimicking renal colic,\nespecially in older patients.','Bedside ultrasound/CT\naortogram if any\nhaemodynamic concern.'],
    ['Musculoskeletal\n(loin) pain','Pain reproducible on movement\nor palpation, no haematuria,\nnormal urinalysis and ultrasound.','Clinical — diagnosis\nof exclusion.'],
]
story.append(plain_table(flank_table,[CW*0.22, CW*0.42, CW*0.36]))
story.append(Spacer(1, 4))

qa_block(
    'This patient has hydronephrosis, microscopic haematuria, a normal full blood count, restlessness, and a relatively SLOW pulse (55-56 bpm) despite severe pain.',
    'Two things to explain: (1) why is restlessness itself a useful clinical sign here, and (2) is a pulse of 55-56 reassuring, worrying, or simply incidental in this context?',
    'Compare renal colic to peritonitis — does a patient with peritonitis want to move around, or lie still? For the pulse — think VAGAL (parasympathetic) responses to severe visceral pain.',
    '(1) Patients with renal colic are classically RESTLESS, rolling around and unable to find a comfortable position — UNLIKE peritonitis, where patients lie completely still because movement worsens the pain. Restlessness here is actually a clue IN FAVOUR OF a colicky (ureteric) cause rather than peritoneal irritation. (2) A relatively slow pulse (55-56) during severe pain is most likely a VAGAL (parasympathetic) response to visceral pain/distension — a recognised, usually BENIGN, finding in renal colic, and not by itself a sign of haemodynamic compromise. It would only become worrying if accompanied by hypotension, chest pain, or other signs of a cardiac event — none of which are present here.',
    story)

alert_box('THE ONE COMBINATION YOU MUST NEVER MISS: FEVER + OBSTRUCTION (hydronephrosis) = an INFECTED, OBSTRUCTED KIDNEY. This is a urological EMERGENCY requiring urgent decompression (nephrostomy or ureteric stent) PLUS IV antibiotics — analgesia alone is not enough, and delay can lead to rapid sepsis and irreversible renal damage.', story)
memory_hook('RENAL COLIC RECALL: restless + writhing (unlike peritonitis) + loin-to-groin pain + microscopic haematuria + hydronephrosis on ultrasound = ureteric stone until proven otherwise. Non-contrast CT KUB is the definitive imaging. Always check temperature — fever + obstruction = emergency decompression.', story)
divider(story)

# §9 Investigations
sec_header('Section 9: Investigations — For Both The Nerve Injury AND The Stone', story)
professor_says('Two problems, two investigation pathways — but notice how the TIMING of investigations differs: the nerve injury is watched and re-examined over days to weeks before any electrical test is needed, while the stone needs definitive IMAGING much sooner.', story)

story.append(bp('<b>(A) Investigating the suspected nerve injury:</b>'))
nerve_inv_table = [
    ['Investigation','When To Do It','What It Shows','MRCP Key Point'],
    ['Clinical neurological\nexamination (repeated)','Immediately, then\ndaily for the\nfirst 1-2 weeks.','Documents the BASELINE\ndeficit and tracks\nimprovement or progression\nover time.','The single most important\n"investigation" — a clearly\ndocumented baseline exam\nprotects both patient and doctor.'],
    ['Nerve conduction\nstudies (NCS)','Usually delayed until\nat least 2-3 weeks\nafter the injury.','Conduction velocity and\namplitude across the\nsuspected lesion site —\ndistinguishes neurapraxia\nfrom axonotmesis.','Done TOO EARLY, distal\nWallerian degeneration may not\nyet have occurred and results\ncan be falsely reassuring.'],
    ['Electromyography\n(EMG)','Also from around\n2-3 weeks post-injury.','Spontaneous denervation\npotentials (fibrillations,\npositive sharp waves) in\naffected muscles if axonal\nloss has occurred.','"3-week rule" — fibrillation\npotentials take about 2-3 weeks\nto appear after axonal injury;\nan EMG done on day 1 is\nuninformative for this.'],
    ['MRI lumbosacral\nspine / pelvis\n(if no improvement)','If no clinical\nimprovement by\n2-3 weeks, or if\ndiagnosis uncertain.','Excludes a structural cause\n(e.g., disc prolapse,\nhaematoma compressing\nthe nerve, mass lesion).','Reserve for atypical or\nnon-resolving cases — not\nneeded for a typical, improving,\ninjection-related neurapraxia.'],
]
story.append(plain_table(nerve_inv_table,[CW*0.18, CW*0.16, CW*0.32, CW*0.34]))
story.append(Spacer(1, 4))

story.append(bp('<b>(B) Investigating the suspected ureteric stone:</b>'))
for pt in [
    '<b>Urinalysis</b> (already done) — confirms microscopic haematuria; also check for nitrites/leucocytes (infection).',
    '<b>Urine culture</b> — essential given the suspicion of infection.',
    '<b>Bloods:</b> FBC (already normal), U&Es/creatinine (renal function — especially important if the kidney is obstructed), CRP (infection/inflammation), serum calcium and urate (metabolic stone risk factors).',
    '<b>Non-contrast CT KUB (kidney-ureter-bladder)</b> — the GOLD STANDARD investigation, performed within 24 hours of presentation per NICE guidance, to confirm the stone, its size, and exact location, and to assess the degree of obstruction.',
    '<b>Repeat renal ultrasound</b> — a reasonable first-line/initial test (as already done here), especially in pregnancy or where CT is to be avoided, but less sensitive than CT for ureteric stones themselves (it shows the downstream effect — hydronephrosis — rather than the stone directly).',
]:
    story.append(bp(f'  • {pt}'))
memory_hook('NERVE INJURY = WATCH AND DOCUMENT FIRST, ELECTROPHYSIOLOGY AT 2-3 WEEKS IF NOT RESOLVING. STONE = CT KUB WITHIN 24 HOURS, PLUS U&Es/CRP/urine culture to catch the dangerous "infected obstructed kidney" combination early.', story)
divider(story)

# §10 Management
sec_header('Section 10: Management — Acute Care, Physiotherapy, and the Renal Colic', story)
professor_says('Good management here is mostly about NOT doing harm, REASSURING appropriately, and knowing exactly when to escalate. There is very little "active treatment" needed for a neurapraxia — but there is a great deal of correct DOCUMENTATION, SAFETY-NETTING, and PARALLEL management of the stone.', story)

story.append(bp('<b>(A) Immediate management of the suspected nerve injury:</b>'))
for pt in [
    '<b>Document everything</b> — exact timing of onset relative to the injection, precise distribution of sensory loss, every muscle tested and its power (use the MRC 0-5 scale), and any change over time. This single step protects the patient (correct ongoing care) and the clinician (medico-legal clarity).',
    '<b>Avoid further IM injections in the SAME buttock</b> — switch to the opposite side, or to the ventrogluteal/vastus lateralis sites, or to an alternative route (oral/IV/PR) if clinically appropriate.',
    '<b>Reassure appropriately</b> — explain that this pattern (immediate, localised, with preserved flexion) is most likely a temporary "bruising" of the nerve (neurapraxia) that usually recovers within days to a few weeks, while being honest that it needs to be RE-CHECKED, not ignored.',
    '<b>Safety-net clearly</b> — ask the patient to report any WORSENING of weakness or numbness, spread to new areas, or new pain, and arrange a follow-up neurological review (e.g., at 1-2 weeks).',
    '<b>Physiotherapy referral</b> — even for an expected-to-recover neurapraxia, early physiotherapy input helps maintain joint range of motion (preventing a fixed equinus contracture from unopposed plantarflexor tone) and can teach gait re-education.',
    '<b>Ankle-foot orthosis (AFO)</b> — a lightweight splint that holds the foot in a neutral/dorsiflexed position, preventing tripping ("foot slap") and contractures, used temporarily WHILE recovery is awaited — not a permanent fix unless recovery fails.',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 4))

story.append(bp('<b>(B) Continuing management of the renal colic / suspected ureteric stone:</b>'))
for pt in [
    '<b>Analgesia</b> — NSAIDs (e.g., diclofenac, given by a SAFER route — see Section 11) remain first-line for renal colic per NICE; IV paracetamol is an alternative if NSAIDs are contraindicated or, as here, have just caused a complication.',
    '<b>Antiemetic</b> — for the vomiting episode (e.g., a standard antiemetic; note that pantoprazole itself does not treat vomiting — it protects the stomach lining, often co-prescribed alongside NSAIDs/steroids).',
    '<b>Urgent CT KUB</b> within 24 hours to confirm the stone\'s size and location.',
    '<b>Urology referral</b> — most stones <5mm pass spontaneously with analgesia and hydration; stones 5-10mm may need medical expulsive therapy (e.g., an alpha-blocker such as tamsulosin); stones >10mm, or any stone with infection or deteriorating renal function, usually need urological intervention (e.g., ureteroscopy, lithotripsy, or, if infected/obstructed, urgent decompression with a nephrostomy or stent).',
    '<b>Monitor temperature and inflammatory markers</b> closely — any sign of infection in an obstructed system changes this from "urgent" to "emergency."',
]:
    story.append(bp(f'  • {pt}'))

info_box('<b>The "incidental" findings — do not over-investigate them now:</b> the history of previous varicose vein surgery and visible corona phlebectatica (small dilated ankle veins from chronic venous insufficiency) are CHRONIC, UNRELATED findings. They do not explain an ACUTE, sharply-demarcated sensory/motor deficit that began at the instant of an injection — but they are worth noting in the records as part of a complete examination.', story)
memory_hook('MANAGEMENT IN ONE LINE: document the nerve findings precisely, avoid re-injecting that buttock, reassure + safety-net + physio/AFO for the nerve — while getting the CT KUB, treating pain safely, and watching for infection in the obstructed kidney.', story)
divider(story)

# §11 Drug Review
sec_header('Section 11: Drug Review — Diclofenac, Platifillin and Pantoprazole', story)
professor_says('Three drugs were given to this patient, in quick succession, for entirely sensible reasons — and yet ONE of them is now centre-stage as the probable cause of a new neurological deficit. Knowing each drug\'s mechanism, indication, and route-related risks lets you explain exactly what happened, and what to do differently next time.', story)

drug_table = [
    ['Drug','Class / Mechanism','Why It Was Given Here','Key Caution / Link To This Case'],
    ['Diclofenac\n(IM)','NSAID — non-selective\nCOX-1/COX-2 inhibitor,\nreduces prostaglandin\nsynthesis -> reduces\npain and ureteric spasm.','First-line analgesia for\nrenal colic per NICE —\nvery effective for\nureteric smooth muscle\nspasm pain.','RECOGNISED to cause local\nchemical/neurotoxic irritation\nif deposited near a nerve.\nAlso: caution in renal impairment\n(this patient has an obstructed\nkidney) — NSAIDs can reduce\nrenal blood flow further. THE\nLIKELY CAUSE of this patient\'s\nnerve injury via the IM route.'],
    ['Platifillin\n(IM)','Antimuscarinic\n(anticholinergic)\nantispasmodic — similar\nfamily to hyoscine/atropine;\nrelaxes smooth muscle\nspasm of the ureter.','Given to relieve\nureteric smooth\nmuscle spasm,\ncomplementing the\nanalgesic effect\nof the NSAID.','Typical antimuscarinic\nside effects: dry mouth,\ntachycardia, blurred vision,\nurinary retention, constipation.\nNo specific link to nerve\ninjury — but worth knowing\nas a "non-MRCP-mainstream"\ndrug name that may appear\nin international vignettes.'],
    ['Pantoprazole\n(IV)','Proton pump inhibitor\n(PPI) — irreversibly\ninhibits the gastric\nH+/K+ ATPase\n("proton pump").','Gastric protection —\noften co-prescribed\nwhenever an NSAID is\ngiven, especially in\nan unwell, vomiting\npatient.','Does NOT treat nausea/\nvomiting itself (a common\nmisconception) — a separate\nantiemetic is needed for that.\nLong-term PPI use is linked\nto hypomagnesaemia, B12\ndeficiency, and increased\nfracture/C. difficile risk —\nnot relevant acutely here.'],
]
story.append(plain_table(drug_table,[CW*0.13, CW*0.22, CW*0.25, CW*0.4]))
story.append(Spacer(1, 4))

qa_block(
    'A colleague says: "Well, the diclofenac is a perfectly correct drug choice for renal colic — so nothing was done WRONG here."',
    'Is this statement entirely fair? Separate the CHOICE OF DRUG from the CHOICE OF ROUTE/SITE — were both optimal?',
    'NICE does recommend an NSAID such as diclofenac for renal colic — that part is correct. But diclofenac can be given by several ROUTES (oral, IM, PR/suppository, IV). Does the ROUTE chosen here carry a risk that an alternative route would not?',
    'The statement is only PARTLY fair. The CHOICE of drug (an NSAID such as diclofenac) for renal colic is entirely guideline-concordant — NICE specifically recommends NSAIDs as first-line analgesia for renal colic. However, the ROUTE AND SITE chosen — an IM injection into the buttock — carries a specific, recognised risk of sciatic nerve injury that an alternative route (oral, IV, or PR/suppository, all of which avoid the gluteal region entirely) would not carry. So: right drug, right indication — but the ROUTE introduced an avoidable risk. This is a useful, non-judgemental way to frame the learning point for an incident review or PACES ethics discussion.',
    story)
memory_hook('THREE DRUGS, THREE JOBS: Diclofenac = kills the PAIN (NSAID, also the probable culprit via the IM route). Platifillin = relaxes the SPASM (antimuscarinic antispasmodic). Pantoprazole = protects the STOMACH (PPI) — but does NOT stop vomiting.', story)
divider(story)

# §12 Prognosis & Recovery Timeline
sec_header('Section 12: Prognosis and Recovery Timeline', story)
professor_says('Patients (and their families) almost always ask the same question first: "Will it get better, and how long will it take?" Being able to give an honest, evidence-based timeline — and to explain what would make you WORRY — is one of the most valuable communication skills in this whole topic.', story)

prog_table = [
    ['Injury Type','Typical Timeline','What To Expect','When To Worry'],
    ['Neurapraxia\n(most likely here)','Days to a\nfew weeks\n(often 2-6 weeks).','FULL recovery\nis the norm —\nsensation usually\nreturns before\nmotor power.','No improvement at all\nby 2-3 weeks ->\narrange NCS/EMG and\nspecialist neurology\nreferral.'],
    ['Axonotmesis','Months — axon\nregrows at\n~1mm/day\n("an inch a month").','Recovery is SLOWER\nbut often good,\nstarting proximally\nand moving distally\n(a Tinel\'s sign can\nbe used to track\nregeneration).','Plateauing of recovery,\nor a Tinel\'s sign that\nstops advancing ->\nreassess with imaging\n+ specialist input.'],
    ['Neurotmesis','No spontaneous\nrecovery.','Will NOT improve\nwithout surgery;\neven with surgical\nrepair, recovery\nis often incomplete.','Should already have\nbeen identified early\n(severe injury\nmechanism, complete\ndeficit) — urgent\nsurgical referral.'],
]
story.append(plain_table(prog_table,[CW*0.18, CW*0.18, CW*0.32, CW*0.32]))
story.append(Spacer(1, 4))

story.append(bp('<b>What to tell THIS patient, in plain language:</b>'))
for pt in [
    '"The numbness you feel in that small area of your foot is most likely because the injection was given very close to a nerve, and the nerve has been temporarily \'stunned\' — a bit like when your arm \'goes to sleep\' after lying on it awkwardly, but in a more localised area."',
    '"The good news is that you can still move your foot well in most directions, and the area affected is small — both of these are REASSURING signs that point towards a temporary problem."',
    '"Most people in this situation recover FULLY within a few days to a few weeks, often without any specific treatment, though we will keep an eye on it."',
    '"If the numbness spreads, gets worse, or you develop NEW weakness anywhere else in the leg, please let us know straight away — this would change our plan."',
]:
    story.append(bp(f'  • {pt}'))
memory_hook('PROGNOSIS RULE OF THUMB: sensory recovery usually comes BEFORE motor recovery. "Inch a month" = axonotmesis regrowth rate. No improvement by 2-3 weeks = time for NCS/EMG, not more reassurance.', story)
divider(story)

# §13 Prevention
sec_header('Section 13: Prevention — Getting The Injection Technique Right Every Time', story)
professor_says('Prevention is where this whole topic earns its keep clinically. A few seconds of correct technique converts a "never event" into a non-event. This is also exactly the kind of "systems and safety" content that PACES communication/ethics stations love to explore.', story)

story.append(bp('<b>A simple, repeatable checklist for every gluteal IM injection:</b>'))
for pt in [
    '<b>1. Choose the site deliberately</b> — ventrogluteal is preferred for adults; avoid the dorsogluteal "upper outer quadrant" wherever possible.',
    '<b>2. Identify landmarks every time</b> — do not rely on "the same spot as last time"; use the hand-positioning technique (Section 3) for the ventrogluteal site on every patient.',
    '<b>3. Choose an appropriate needle length</b> — based on the patient\'s body habitus, to ensure the drug reaches muscle without being so long that it risks deeper structures.',
    '<b>4. Inject slowly and watch the patient\'s face</b> — sudden grimacing, a cry of pain, or a description of "shooting" or "electric" sensation means STOP immediately.',
    '<b>5. If a nerve-type symptom occurs</b> — withdraw the needle slightly or fully, reassess, and consider choosing a different site for the remainder of the dose if still clinically needed.',
    '<b>6. Document</b> — site used, any unexpected patient response, and post-injection neurological status, especially after ANY injection where the patient reports unusual sensations.',
    '<b>7. Consider the ROUTE, not just the site</b> — for patients at higher risk (anticoagulated, needle-phobic, or where IM injection is simply not essential), oral, IV, or PR formulations of the same drug may achieve the same goal with less risk.',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 4))

image_search_box('correct ventrogluteal injection technique hand position diagram', 'Google Images / Nursing skills videos', story)

memory_hook('PREVENTION IN ONE SENTENCE: "Right site (ventrogluteal), right landmarks (every time), right needle, and STOP at the first sign of a nerve-type symptom" — this single habit prevents almost every iatrogenic sciatic nerve injury.', story)
divider(story)

# §14 Top MRCP/PACES Trigger Scenarios
sec_header('Section 14: Top MRCP/PACES Trigger Scenarios — Connecting Both Topics', story)
professor_says('MRCP loves to test TWO topics in ONE vignette. This case is a perfect example: a renal colic vignette that pivots, mid-question, into a peripheral neurology vignette. Recognise the PIVOT POINT, and you will not be caught off guard.', story)

trig_table = [
    ['Trigger Phrase In The Vignette','What It Should Make You Think'],
    ['"...numbness shot down the leg AT THE MOMENT of the injection..."','Iatrogenic sciatic nerve injury from the IM injection — start localising immediately.'],
    ['"...numb patch confined to the skin between the first and second toes..."','DEEP PERONEAL NERVE territory — common peroneal division of the sciatic nerve.'],
    ['"...can plantarflex but cannot dorsiflex; ankle jerk and inversion normal..."','Isolated common peroneal (deep peroneal branch) lesion — NOT L5 root, NOT S1, NOT full sciatic.'],
    ['"...weak inversion AND foot drop, with back pain and a positive straight-leg raise..."','L5 radiculopathy, not a peripheral nerve lesion.'],
    ['"...absent ankle jerk, weak plantarflexion, numb sole..."','S1 radiculopathy or tibial nerve involvement — NOT a pure peroneal lesion.'],
    ['"...bilateral, symmetrical, glove-and-stocking numbness, long history of diabetes..."','Peripheral polyneuropathy, not a focal nerve injury.'],
    ['"...injection given in the upper outer quadrant of the buttock (dorsogluteal)..."','Recognise this as the HIGH-RISK site for sciatic nerve injury — ventrogluteal is safer.'],
    ['"...renal colic, restless patient, pulse 55-56, hydronephrosis, microscopic haematuria..."','Classic ureteric colic — CT KUB within 24 hours is the definitive next investigation.'],
    ['"...fever PLUS hydronephrosis..."','Infected obstructed kidney — urological EMERGENCY, urgent decompression needed.'],
    ['"...EMG performed on day 1 shows no abnormality..."','Too early — fibrillation potentials take 2-3 weeks to appear after axonal injury; repeat later if clinically indicated.'],
    ['"...patient established on diclofenac, develops a hypertensive crisis with episodic palpitations and sweating..."','Think phaeochromocytoma — NSAIDs are not the cause; do not be distracted (cross-reference with the Hypertension note).'],
    ['"...patient with renal colic given an NSAID develops worsening renal function and reduced urine output..."','NSAIDs reduce renal blood flow (prostaglandin-mediated afferent arteriolar dilation is blocked) — caution in any patient with an obstructed or already-compromised kidney.'],
]
story.append(plain_table(trig_table,[CW*0.45, CW*0.55]))
memory_hook('THE PIVOT-POINT HABIT: as soon as a vignette mentions an INJECTION followed by a NEW NEUROLOGICAL SYMPTOM "at the same time," mentally switch from whatever the original problem was into "localise this nerve injury" mode — then switch back to finish the original problem afterwards.', story)
divider(story)

# §15 PACES + Minimal Resources
sec_header('Section 15: PACES Examination Guide and Minimal Resources Summary', story)
professor_says('In PACES, this topic appears inside the NEUROLOGY station (peripheral nerve examination of the leg) and inside HISTORY-TAKING / COMMUNICATION stations ("a patient is concerned about a complication of their treatment"). Be ready to examine a foot drop methodically, AND to explain an iatrogenic complication honestly and calmly.', story)

story.append(bp('<b>PACES Station 3 (Neurology) — Examining a Patient With Suspected Foot Drop:</b>'))
paces_exam = [
    ['Examination Step','What To Do / Look For','What It Tells You'],
    ['Inspection','Watch the patient walk —\nlook for "high-stepping"\n(steppage) gait, and for\nfoot slap on heel strike.','A classic visual sign of\nfoot drop — the patient lifts\nthe knee higher to clear\nthe dropped foot.'],
    ['Tone and bulk','Compare both legs for\nwasting (especially the\nanterior shin/peroneal\ncompartment) and tone.','Wasting suggests a more\nchronic or axonal\nprocess; acute neurapraxia\nusually shows no wasting yet.'],
    ['Power — dorsiflexion,\nplantarflexion, inversion,\neversion, toe extension','Test each movement\nagainst resistance,\nMRC grade 0-5,\ncompare both sides.','Localises the lesion exactly\nas in Section 6 — the\ncombination of findings\nis the whole answer.'],
    ['Sensation','Light touch and pinprick\nover the first web space,\ndorsum, sole, lateral foot,\nand medial shin (saphenous).','Maps onto the named\ncutaneous nerve territories\n(Section 5) to confirm\nor refine localisation.'],
    ['Reflexes','Ankle (S1) and knee (L3/4)\njerks, both sides.','An absent ankle jerk points\naway from an isolated\nperoneal lesion, towards\nS1/tibial/full sciatic involvement.'],
    ['Gait re-check\n+ functional test','Ask the patient to walk\non their heels (tests\ndorsiflexion) and on\ntheir toes (tests\nplantarflexion).','A quick functional summary\nof the whole exam — heel-walking\nis impaired in foot drop;\ntoe-walking is preserved if\nthe tibial division is intact.'],
]
story.append(plain_table(paces_exam,[CW*0.22, CW*0.4, CW*0.38]))
story.append(Spacer(1, 6))

story.append(bp('<b>PACES Communication — Explaining This Complication To The Patient (in plain language):</b>'))
for pt in [
    '"The injection we gave you to help with your kidney pain was given close to a major nerve that runs through the buttock and down the leg. It seems the nerve has been irritated by this — a bit like a bruise on a nerve."',
    '"This has caused a small numb patch on the top of your foot, between your big toe and second toe, and some difficulty lifting your toes upward. The rest of your foot — including the sole and your ability to push your foot down — is working completely normally."',
    '"In most cases like this, the nerve recovers fully on its own within a few days to a few weeks, without needing any specific treatment."',
    '"We will avoid giving any further injections into that side, we will check on you regularly, and if it has not improved within a couple of weeks, we will arrange a nerve test to look more closely."',
    '"I want to be honest with you — this was an unintended effect of a needle placed very close to a nerve. We will document this clearly in your notes, and we are reviewing how we give these injections to reduce the chance of this happening to anyone else."',
    '"In the meantime, we will continue to investigate and manage your kidney stone, which is a separate issue and remains our other priority."',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 6))

minimal_rows = [
    [Paragraph('<b>MINIMAL RESOURCES SUMMARY — Managing Suspected Iatrogenic Sciatic/Peroneal Nerve Injury With Limited Equipment</b>', sAlert)],
    [Paragraph('If no nerve conduction studies/EMG are available: A careful, repeated CLINICAL examination (power, sensation, reflexes, mapped against named nerve territories) at presentation and again at 1-2 weeks gives most of the information needed to decide between watchful waiting and referral.', sBody)],
    [Paragraph('If no AFO (ankle-foot orthosis) is available: A simple high-top boot, firm bandage strapping the foot in a neutral position, or even taping can reduce tripping risk while awaiting recovery — formal AFOs can be arranged later if recovery is delayed.', sBody)],
    [Paragraph('If physiotherapy is not immediately accessible: Teach the patient simple passive range-of-motion exercises for the ankle (gently moving the foot up and down through its full range several times a day) to prevent stiffness/contracture while nerve recovery is awaited.', sBody)],
    [Paragraph('If CT KUB is not available for the renal stone: A repeat renal ultrasound, urinalysis, and clinical monitoring of pain/fever/renal function can guide initial management; refer onward for CT and urology input as soon as accessible, especially if fever develops.', sBody)],
    [Paragraph('If specialist neurology referral has a long wait: Provide clear written safety-netting advice (what worsening looks like, and to seek urgent review if it occurs), and a planned review date — most cases will have resolved before the appointment is even due.', sBody)],
    [Paragraph('The single most valuable "test" in this entire topic costs nothing: a clearly documented neurological examination, repeated over time, by the same observer wherever possible.', sBody)],
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
memory_hook('PACES READY-RECKONER: Watch the GAIT first (steppage gait = visual diagnosis). Test dorsiflexion, plantarflexion, inversion, eversion, sensation (first web space vs sole vs medial shin), and the ankle jerk — these few tests localise almost every foot-drop case. Explain in plain words: "nerve bruise," "small numb patch," "usually recovers fully," "we will not inject that side again," and be HONEST that this was unintended.', story)
divider(story)

# §16 Self-Test
story.append(PageBreak())
sec_header('Section 16: Self-Test — Iatrogenic Nerve Injury & Renal Colic MCQ Examination (15 Questions)', story)
professor_says('Now it is YOUR turn to be the professor. Attempt every question fully before turning to the answer key at the very end of this document. Write your answer in the blank space provided.', story)
story.append(bp('<i>Instructions: Each question is a short clinical scenario, exactly as it would appear in the MRCP exam. Choose the SINGLE best answer from the options given (A-E). Write your chosen letter in the blank space. The correct answers and full explanations are given separately in Section 17, at the very end — do not look ahead!</i>'))
story.append(Spacer(1, 8))

mcq(1,
    'A 50-year-old man receives an IM injection of diclofenac into the left buttock for renal colic. At the moment of injection he feels numbness shoot down the back of his leg. Hours later he has a small numb patch confined to the first web space of the left foot, and cannot extend (dorsiflex) his big toe — but plantarflexion and the ankle jerk are normal. Which structure is most likely injured?',
    [('A','Tibial nerve'),
     ('B','Sural nerve'),
     ('C','Common peroneal division of the sciatic nerve (deep peroneal branch)'),
     ('D','Saphenous nerve'),
     ('E','Femoral nerve')],
    'C',
    'A numb first web space plus weak toe/foot dorsiflexion, with preserved plantarflexion and ankle jerk, is the textbook picture of an isolated lesion of the common peroneal division of the sciatic nerve, predominantly affecting its deep peroneal branch.',
    story)

mcq(2,
    'A patient has foot drop with numbness over the dorsum of the foot. Ankle jerk is preserved and foot inversion (tibialis posterior) is normal. There is no back pain and no recent injection, but he describes habitually sitting with his legs crossed for long periods. What is the most likely diagnosis?',
    [('A','L5 radiculopathy'),
     ('B','Common peroneal nerve palsy at the fibular neck (compressive)'),
     ('C','Sciatic nerve injury from an injection'),
     ('D','S1 radiculopathy'),
     ('E','Diabetic peripheral polyneuropathy')],
    'B',
    'Preserved ankle jerk and inversion exclude L5/S1 root and full sciatic involvement. A clear compressive history (leg crossing) at the fibular neck, where the common peroneal nerve is very superficial, is the classic cause of this isolated, distal pattern.',
    story)

mcq(3,
    'A patient has foot drop, numbness over the sole and lateral border of the foot, weak plantarflexion, and an ABSENT ankle jerk. Which lesion best fits this picture?',
    [('A','Isolated deep peroneal nerve lesion'),
     ('B','Common peroneal nerve palsy at the fibular neck'),
     ('C','S1 root or tibial nerve involvement (or a more complete sciatic nerve lesion)'),
     ('D','Saphenous nerve lesion'),
     ('E','Femoral nerve lesion')],
    'C',
    'An absent ankle jerk and weak plantarflexion implicate the TIBIAL division (S1/S2) — this pattern points to S1 root pathology, tibial nerve involvement, or a more complete sciatic nerve lesion, NOT an isolated peroneal lesion.',
    story)

mcq(4,
    'A patient presents with foot drop, weak foot inversion, weak hip abduction, low back pain, and a positive straight-leg raise test. The ankle jerk is normal. What is the most likely diagnosis?',
    [('A','Common peroneal nerve palsy'),
     ('B','L5 radiculopathy'),
     ('C','S1 radiculopathy'),
     ('D','Sciatic nerve injection injury'),
     ('E','Peripheral polyneuropathy')],
    'B',
    'Weak inversion (tibialis posterior, L4/L5) and weak hip abduction (gluteus medius, L5) cannot be explained by a peroneal nerve lesion alone — both are L5 myotome muscles. Combined with back pain and a positive straight-leg raise, this is L5 radiculopathy.',
    story)

mcq(5,
    'A 65-year-old man with longstanding type 2 diabetes presents with gradually progressive numbness and tingling in both feet and lower legs in a "glove and stocking" distribution, with absent ankle jerks bilaterally. What is the most likely diagnosis?',
    [('A','Bilateral common peroneal nerve palsy'),
     ('B','Diabetic peripheral polyneuropathy'),
     ('C','Bilateral L5 radiculopathy'),
     ('D','Bilateral sciatic nerve injury'),
     ('E','Acute Guillain-Barre syndrome')],
    'B',
    'A bilateral, symmetrical, gradually progressive "glove and stocking" sensory loss with absent ankle jerks in a patient with longstanding diabetes is the classic picture of diabetic peripheral polyneuropathy — a length-dependent, symmetrical process, unlike the focal, unilateral, sudden-onset injuries discussed elsewhere in this note.',
    story)

mcq(6,
    'A patient has a suspected sciatic nerve injury from an IM injection given 2 days ago, with persistent dorsum numbness and weak toe extension. EMG performed today shows no spontaneous denervation activity. What is the best interpretation of this result?',
    [('A','This excludes any nerve injury'),
     ('B','The EMG is too early — fibrillation/denervation potentials take roughly 2-3 weeks to appear after axonal injury, so a normal EMG at day 2 is uninformative and should be repeated later if the deficit persists'),
     ('C','This confirms neurotmesis'),
     ('D','EMG should never be repeated regardless of clinical course'),
     ('E','This confirms the nerve is completely normal and no follow-up is needed')],
    'B',
    '"The 3-week rule": denervation (fibrillation) potentials on EMG take approximately 2-3 weeks to develop after axonal injury. An EMG performed too early can be falsely reassuring and should be repeated at 2-3 weeks if the clinical deficit has not resolved.',
    story)

mcq(7,
    'Which intramuscular injection site in adults is preferred for routine injections because it is free of major nerves and vessels, avoiding the sciatic nerve entirely?',
    [('A','Dorsogluteal (upper outer quadrant of the buttock)'),
     ('B','Ventrogluteal site'),
     ('C','Deltoid, for any volume'),
     ('D','Directly over the popliteal fossa'),
     ('E','Lower medial thigh, close to the femoral vessels')],
    'B',
    'The ventrogluteal site, identified using the hand-positioning landmark technique (greater trochanter, ASIS, iliac crest), is free of major nerves and vessels and is the preferred site for IM injections in adults — unlike the traditional dorsogluteal site, which overlies the variable course of the sciatic nerve.',
    story)

mcq(8,
    'A patient with an obstructed left kidney due to a ureteric stone (left hydronephrosis) is given an NSAID for pain relief. What is the main renal concern with NSAID use in this setting?',
    [('A','NSAIDs directly cause hyperkalaemia by blocking aldosterone receptors'),
     ('B','NSAIDs inhibit prostaglandin-mediated afferent arteriolar dilation, reducing renal blood flow and risking acute kidney injury in an already compromised, obstructed kidney'),
     ('C','NSAIDs cause direct crystal deposition within the renal tubules'),
     ('D','NSAIDs have no clinically relevant renal effects'),
     ('E','NSAIDs cause renal artery stenosis acutely')],
    'B',
    'Prostaglandins normally dilate the afferent arteriole, maintaining glomerular filtration when renal perfusion is compromised. NSAIDs block this protective mechanism — a particular concern in a kidney that is already obstructed and under stress.',
    story)

mcq(9,
    'Platifillin was given as an antispasmodic to relieve ureteric smooth muscle spasm during this patient\'s renal colic. To which drug class does it belong, and what is its mechanism of action?',
    [('A','Beta-2 agonist — relaxes smooth muscle via increased intracellular cAMP'),
     ('B','Antimuscarinic (anticholinergic) agent — blocks muscarinic acetylcholine receptors, relaxing ureteric smooth muscle, similar in family to hyoscine/atropine'),
     ('C','NSAID — inhibits cyclo-oxygenase and prostaglandin synthesis'),
     ('D','Opioid analgesic — acts on mu-opioid receptors'),
     ('E','Dihydropyridine calcium channel blocker')],
    'B',
    'Platifillin is an antimuscarinic (anticholinergic) antispasmodic, in the same pharmacological family as hyoscine and atropine, used to relax smooth muscle spasm — here, ureteric spasm contributing to renal colic pain.',
    story)

mcq(10,
    "According to Seddon's classification, which type of nerve injury involves disruption of the AXON itself but PRESERVATION of the surrounding connective tissue sheaths (endoneurium, perineurium, epineurium), with regeneration occurring at approximately 1mm per day?",
    [('A','Neurapraxia'),
     ('B','Axonotmesis'),
     ('C','Neurotmesis'),
     ('D','Wallerian degeneration, as a distinct fourth category'),
     ('E','Segmental demyelination without axonal involvement')],
    'B',
    'Axonotmesis = the axon is disrupted but the connective tissue scaffolding remains intact, allowing the regenerating axon to be guided back towards its original target at the classic rate of "an inch a month" (~1mm/day).',
    story)

mcq(11,
    'An ankle-foot orthosis (AFO) is prescribed for a patient with foot drop following a suspected sciatic/common peroneal nerve injury that is expected to recover. What is its primary purpose at this stage?',
    [('A','To permanently replace the function of the dorsiflexor muscles for life'),
     ('B','To hold the foot in a neutral/dorsiflexed position, preventing tripping ("foot slap") and contractures while spontaneous nerve recovery is awaited'),
     ('C','To directly treat and accelerate regeneration of the injured nerve'),
     ('D','To compress the sciatic nerve and reduce local inflammation'),
     ('E','To reduce swelling in the calf and prevent deep vein thrombosis')],
    'B',
    'An AFO is a temporary functional aid — it prevents tripping and contractures while the nerve recovers; it does not itself treat the nerve injury, and is not necessarily permanent unless recovery fails.',
    story)

mcq(12,
    'A patient presents with sudden severe loin-to-groin pain, microscopic haematuria on urinalysis, and left hydronephrosis on ultrasound. Which investigation is recommended, ideally within 24 hours, to confirm the diagnosis and characterise the stone?',
    [('A','MRI of the lumbar spine'),
     ('B','Non-contrast CT KUB (kidney-ureter-bladder)'),
     ('C','Intravenous urogram with contrast'),
     ('D','Renal biopsy'),
     ('E','Cystoscopy')],
    'B',
    'Non-contrast CT KUB is the gold-standard investigation for suspected ureteric colic, identifying the great majority of stones and characterising their size and location, and is recommended within 24 hours of presentation.',
    story)

mcq(13,
    'A patient with severe renal colic is restless, has a normal blood pressure, and a pulse of 55-56 bpm. What is the most likely explanation for this relatively slow pulse?',
    [('A','Beta-blocker overdose'),
     ('B','A vagal (parasympathetic) response to severe visceral pain — a recognised, usually benign finding in renal colic'),
     ('C','Complete heart block requiring urgent pacing'),
     ('D','Hypothermia'),
     ('E','Digoxin toxicity')],
    'B',
    'Severe visceral pain, including renal colic, can trigger a vagally-mediated relative bradycardia. In the absence of hypotension, chest pain, or other red flags, this is a recognised and usually benign accompaniment of renal colic, not a primary cardiac problem.',
    story)

mcq(14,
    'A patient with known hydronephrosis from a left ureteric stone develops a temperature of 38.9°C with rigors. What is the most appropriate immediate management?',
    [('A','Oral antibiotics and discharge home for outpatient follow-up'),
     ('B','Urgent urological decompression (nephrostomy or ureteric stent) plus IV antibiotics — an infected, obstructed kidney is a urological emergency'),
     ('C','Increase the dose of NSAID analgesia and observe'),
     ('D','Reassure the patient that fever is an expected feature of renal colic'),
     ('E','Arrange outpatient lithotripsy in two weeks\' time')],
    'B',
    'Fever in the presence of an obstructed urinary system (infected hydronephrosis/pyonephrosis) is a urological emergency. It requires urgent decompression (nephrostomy or ureteric stent) together with IV antibiotics — analgesia alone is inadequate and delay risks rapid sepsis and renal damage.',
    story)

mcq(15,
    'On examination of a patient with foot drop, foot inversion (tibialis posterior) is WEAK, hip abduction is WEAK, and there is numbness over the dorsum and lateral shin. Which finding most clearly distinguishes this from an ISOLATED common peroneal nerve lesion?',
    [('A','The presence of foot drop itself'),
     ('B','Weakness of foot inversion (tibialis posterior — supplied by the tibial nerve but carrying L5 fibres) together with weak hip abduction (gluteus medius, L5) — neither is explained by a peroneal nerve lesion alone, pointing instead to an L5 radiculopathy'),
     ('C','The presence of numbness over the dorsum of the foot'),
     ('D','A normal ankle jerk'),
     ('E','The fact that symptoms are unilateral')],
    'B',
    'Tibialis posterior (inversion) is supplied by the TIBIAL nerve, not the common peroneal nerve — but it carries L5 root fibres. Weakness of inversion AND hip abduction (also L5, via the superior gluteal nerve) cannot be explained by a lesion confined to the common peroneal nerve, and instead localises the lesion to the L5 NERVE ROOT.',
    story)

divider(story)

# §17 Answer Key — kept separate, on its own page, so the test stays "blank" until checked
story.append(PageBreak())
sec_header('Section 17: Answer Key — Self-Test Solutions and Explanations', story)
info_box('<b>Now check your work.</b> Go back through Section 16 question by question, compare your written answer with the correct answer below, and read the explanation — especially for any question you got wrong.', story)
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
    [Paragraph('MASTER MEMORY SUMMARY — IATROGENIC SCIATIC/PERONEAL NERVE INJURY', sGrnB)],
    [Paragraph('THE CASE: numbness shooting down the leg AT THE MOMENT of an IM diclofenac injection into the left buttock for renal colic, leaving a sharply localised numb patch over the first web space/dorsum of the big toe, with weak toe/foot dorsiflexion but normal plantarflexion, inversion, sole sensation and ankle jerk.', sGrn)],
    [Paragraph('ANATOMY: the sciatic nerve = TWO nerves (tibial + common peroneal) in one sheath, formed from L4-S3, running through the buttock beneath the dorsogluteal injection zone. The common peroneal division is more lateral and loosely tethered -> more vulnerable to needle/chemical injury. Below the knee it splits into superficial peroneal (eversion + dorsum sensation) and deep peroneal (dorsiflexion + first web space sensation only).', sGrn)],
    [Paragraph('LOCALISATION LOGIC: numb first web space ONLY = deep peroneal. Weak dorsiflexion + normal plantarflexion/inversion/ankle jerk = isolated common peroneal (deep peroneal branch) lesion, NOT L5 root, NOT S1, NOT full sciatic, NOT polyneuropathy (which is bilateral).', sGrn)],
    [Paragraph("SEDDON'S CLASSIFICATION: NEURAPRAXIA (conduction block, axon intact, recovers days-weeks) -- AXONOTMESIS (axon cut, sheath intact, regrows ~1mm/day) -- NEUROTMESIS (everything cut, needs surgery). This patient's picture (immediate, localised, motor-sparing, non-progressive) = textbook NEURAPRAXIA.", sGrn)],
    [Paragraph('INJECTION SITES: VENTROGLUTEAL (hand-landmark triangle, nerve-free) = preferred for adults. DORSOGLUTEAL ("upper outer quadrant") = sciatic nerve danger zone. STOP immediately if the patient reports shooting pain or numbness during injection.', sGrn)],
    [Paragraph('INVESTIGATIONS: document serial clinical exams first. NCS/EMG only from 2-3 weeks (the "3-week rule" for denervation potentials). MRI spine/pelvis only if no improvement by 2-3 weeks.', sGrn)],
    [Paragraph('MANAGEMENT: document precisely, avoid further injections in that buttock, reassure + safety-net, physiotherapy + AFO if needed while awaiting recovery. Most neurapraxias recover FULLY within days to a few weeks; sensory recovery usually precedes motor recovery.', sGrn)],
    [Paragraph('THE PARALLEL PROBLEM (renal colic): restless patient (unlike peritonitis), relative bradycardia (vagal response, usually benign), hydronephrosis + microscopic haematuria = ureteric stone -> non-contrast CT KUB within 24h. FEVER + OBSTRUCTION = infected obstructed kidney = urological EMERGENCY (urgent decompression + IV antibiotics).', sGrn)],
    [Paragraph('DRUGS: Diclofenac (NSAID) = right drug for renal colic, but IM route into the buttock carries sciatic nerve risk, AND caution with renal blood flow in an obstructed kidney. Platifillin = antimuscarinic antispasmodic for ureteric spasm. Pantoprazole = gastric protection, NOT an antiemetic.', sGrn)],
    [Paragraph('PACES: examine gait (steppage gait), then dorsiflexion/plantarflexion/inversion/eversion/sensation/ankle jerk in sequence. Explain in plain words: "nerve bruise," "small numb patch," "usually recovers fully," "we will not inject that side again," and be HONEST that this was an unintended effect of treatment.', sGrn)],
]
innerG = Table(gRows, colWidths=[CW-4])
innerG.setStyle(gTS1)
outerG = Table([[innerG]], colWidths=[CW])
outerG.setStyle(gTSO)
story.append(outerG)
story.append(Spacer(1, 14))

# Footer note
story.append(HRFlowable(width=CW, thickness=1.5, color=HexColor('#0d5c63'), spaceAfter=6))
story.append(Paragraph('MRCP Revision Note: Iatrogenic Sciatic and Common Peroneal Nerve Injury From Intramuscular Injection — Anatomy, Localisation, Differentials and Management, With Linked Renal Colic Case  |  Ganesh & Kuruvilla Prescribing Reference / NICE Renal Colic Guidance  |  Sections 1-17 inclusive, with Interactive Q&A and Self-Test', ParagraphStyle('FT', fontName='DV-I', fontSize=8, leading=11, textColor=HexColor('#555555'), alignment=1)))

# Build document
doc.build(story)
print('SUCCESS:', OUT)
