"""
MRCP REVISION NOTE: Safe Intramuscular Injection Technique — Gluteal Anatomy and Site Selection
Page size: A3 Portrait (297mm x 420mm) for readable, spacious layout.
Text-safe PIL diagram toolkit (wrap_text + card + header_band + finish) — no overlap.
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

OUT = '/mnt/user-data/outputs/Safe_IM_Injection_Technique_MRCP_Note.pdf'
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
CW = PAGE_W - 2*MARGIN       # ~717pt content width

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

# ── PIL 1: Anatomy of the buttock — why the site matters ────────────────────
def make_gluteal_anatomy():
    W, H_MAX = 900, 1800
    f = load_fonts(CARD_FONTS)
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PAD_X, W - PAD_X
    hh = header_band(draw, W, 'ANATOMY OF THE BUTTOCK — WHY THE SITE OF AN INJECTION MATTERS', f['T'], PAD_X)

    yy = hh + 22
    yy = card(draw, x0, x1, yy,
        'THE GLUTEAL MUSCLES — THREE OVERLAPPING LAYERS',
        'Gluteus maximus is the large, most superficial muscle giving the buttock its shape. Beneath it lie gluteus medius and gluteus minimus, the smaller "hip abductor" muscles. Most IM injections enter either gluteus maximus (the old dorsogluteal site) or gluteus medius (the ventrogluteal site) — but this whole region also contains major nerves and vessels passing beneath these muscles.',
        f['B'], f['XS'], '#0d5c63', '#dff2f1')
    yy += 16
    yy = card(draw, x0, x1, yy,
        'THE SCIATIC NERVE — THE STRUCTURE WE MOST WANT TO AVOID',
        'The sciatic nerve (roots L4-S3) leaves the pelvis through the greater sciatic notch and runs down deep to gluteus maximus, roughly midway between the posterior superior iliac spine and the ischial tuberosity — but its exact course varies between people, and in some it lies more superficial or more lateral than textbook diagrams suggest.',
        f['B'], f['XS'], '#c0392b', '#fde8e8')
    yy += 16
    yy = card(draw, x0, x1, yy,
        'SUPERIOR GLUTEAL VESSELS AND NERVE',
        'The superior gluteal artery, vein and nerve emerge from the upper part of the greater sciatic notch and supply/innervate gluteus medius and minimus. An injection placed too far medially or superiorly in the buttock risks these structures as well as the sciatic nerve.',
        f['B'], f['XS'], '#7d3c98', '#f5eef8')
    yy += 16
    yy = card(draw, x0, x1, yy,
        'THE OLD "UPPER OUTER QUADRANT" RULE — WHY IT IS NO LONGER ENOUGH ON ITS OWN',
        'Dividing the buttock into four quadrants and aiming for the upper-outer one was the traditional teaching for the dorsogluteal site. Imaging studies have shown the sciatic nerve, and the branching point of the superior gluteal artery, can lie within or very close to this "safe" quadrant in a significant minority of people — particularly when the quadrant is harder to judge accurately, such as in larger patients.',
        f['B'], f['XS'], '#d4640a', '#fef3e2')
    yy += 16
    yy = card(draw, x0, x1, yy,
        'THE VENTROGLUTEAL SAFE ZONE — GLUTEUS MEDIUS, AWAY FROM THE SCIATIC NERVE',
        'The ventrogluteal site overlies gluteus medius on the outer, upper part of the hip — anatomically separated from the sciatic nerve, the superior gluteal vessels, and the major bony landmarks by a reliable margin. This is why it is now recommended as the FIRST-CHOICE site for IM injections in adults.',
        f['B'], f['XS'], '#1a8a94', '#e0f4f5')

    final = finish(img, draw, W, yy,
        'KEY CONCEPT — the sciatic nerve\'s course is variable enough that a LANDMARK-BASED technique (not "upper outer quadrant by eye") is essential for safety, especially in larger patients',
        f['XS'])
    return i2r(final, CW)

# ── PIL 2: Finding the ventrogluteal site step by step ──────────────────────
def make_ventrogluteal_landmark():
    W, H_MAX = 900, 1800
    f = load_fonts(CARD_FONTS)
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PAD_X, W - PAD_X
    hh = header_band(draw, W, 'FINDING THE VENTROGLUTEAL SITE — THE HOCHSTETTER LANDMARK METHOD', f['T'], PAD_X)

    steps = [
        ('#0d5c63', '#dff2f1', 'STEP 1 — POSITION THE PATIENT',
         'The patient can be supine, lying on their side, or prone — what matters is that the hip and knee on the injection side are slightly flexed, relaxing the gluteal muscles and making the landmarks easier to feel.'),
        ('#1a8a94', '#e0f4f5', 'STEP 2 — PLACE YOUR PALM ON THE GREATER TROCHANTER',
         'Using the hand OPPOSITE to the side being injected (right hand for the patient\'s left hip), place the heel of your palm flat over the greater trochanter — the bony prominence felt on the outer upper thigh.'),
        ('#7d3c98', '#f5eef8', 'STEP 3 — POINT YOUR INDEX FINGER TO THE ANTERIOR SUPERIOR ILIAC SPINE (ASIS)',
         'Keeping your palm on the trochanter, stretch your index finger forward until it touches the ASIS — the bony point at the front of the pelvis that you can feel through the hip.'),
        ('#d4640a', '#fef3e2', 'STEP 4 — SPREAD YOUR MIDDLE FINGER BACK ALONG THE ILIAC CREST',
         'Spread your middle finger backwards along the iliac crest, away from the index finger, so that your index and middle fingers form a "V" (or triangle) shape.'),
        ('#c0392b', '#fde8e8', 'STEP 5 — INJECT INTO THE CENTRE OF THE V — INTO GLUTEUS MEDIUS',
         'The centre of the V/triangle formed by your fingers overlies gluteus medius, well clear of the sciatic nerve and major vessels. Insert the needle here, perpendicular to the skin (90 degrees).'),
    ]
    yy = hh + 22
    for accent, bg, title, body in steps:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 16

    final = finish(img, draw, W, yy,
        'KEY CONCEPT — this is a HAND-LANDMARK technique, not a "by eye" estimate: the V formed between your index and middle fingers IS the injection site',
        f['XS'])
    return i2r(final, CW)

# ── PIL 3: The five IM injection sites compared ─────────────────────────────
def make_site_comparison():
    W, H_MAX = 900, 1800
    f = load_fonts(CARD_FONTS)
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PAD_X, W - PAD_X
    hh = header_band(draw, W, 'THE FIVE MAIN INTRAMUSCULAR INJECTION SITES, COMPARED', f['T'], PAD_X)

    sites = [
        ('#0d5c63', '#dff2f1', '1. VENTROGLUTEAL (GLUTEUS MEDIUS) — FIRST CHOICE FOR MOST ADULT IM INJECTIONS',
         'Free of major nerves and vessels. Can accommodate larger volumes (up to around 3mL, sometimes more) and is suitable for thick or irritant medications, such as depot antipsychotics.'),
        ('#c0392b', '#fde8e8', '2. DORSOGLUTEAL (GLUTEUS MAXIMUS, "UPPER OUTER QUADRANT") — TRADITIONAL BUT FALLING OUT OF FAVOUR',
         'Overlies the variable course of the sciatic nerve and the superior gluteal vessels. Absorption can also be slower, because gluteus maximus is less vascular and often has more overlying fat, especially if landmarks are misjudged.'),
        ('#7d3c98', '#f5eef8', '3. DELTOID — CONVENIENT, BUT SMALL VOLUMES ONLY',
         'Used for vaccines and other small-volume injections (typically up to 1mL). The site is the thickest part of the muscle, roughly 2-3 finger-breadths below the acromion — too low risks the radial nerve and the brachial artery in the spiral groove of the humerus.'),
        ('#d4640a', '#fef3e2', '4. VASTUS LATERALIS (ANTEROLATERAL THIGH) — PREFERRED IN INFANTS',
         'A large muscle with no major nerves or vessels nearby, on the outer thigh between the greater trochanter and the knee. The preferred site in infants and young children, who have insufficient gluteal muscle bulk.'),
        ('#2471a3', '#e8f4fd', '5. RECTUS FEMORIS (ANTERIOR THIGH) — A SELF-INJECTION SITE',
         'On the front of the thigh; easily reached by patients to inject themselves (for example, some biologic therapies), though it can be more uncomfortable than other sites because of its rich nerve supply.'),
    ]
    yy = hh + 22
    for accent, bg, title, body in sites:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 14

    final = finish(img, draw, W, yy,
        'KEY CONCEPT — VENTROGLUTEAL = first choice for adults; VASTUS LATERALIS = first choice for infants; DORSOGLUTEAL = avoid where possible because of its relationship to the sciatic nerve',
        f['XS'])
    return i2r(final, CW)

# ── PIL 4: Step-by-step safe IM injection technique ─────────────────────────
def make_technique_steps():
    W, H_MAX = 900, 1800
    f = load_fonts(CARD_FONTS)
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PAD_X, W - PAD_X
    hh = header_band(draw, W, 'STEP-BY-STEP SAFE INTRAMUSCULAR INJECTION TECHNIQUE', f['T'], PAD_X)

    steps = [
        ('#0d5c63', '#dff2f1', 'STEP 1 — CHECK AND PREPARE',
         'Confirm the right patient, right drug, right dose, right route and right time, and check for allergies. Inspect the chosen site for scars, lumps, bruising, infection or skin lesions — pick a different site if any are present. Perform hand hygiene and don gloves.'),
        ('#1a8a94', '#e0f4f5', 'STEP 2 — CHOOSE THE NEEDLE: LENGTH AND GAUGE',
         'Needle LENGTH depends on the site and the patient\'s subcutaneous fat — long enough to reach muscle, not so long that it risks deeper structures. Needle GAUGE depends on the viscosity of the drug — thicker suspensions (depot antipsychotics, some penicillins) need a wider-bore needle than clear aqueous solutions.'),
        ('#7d3c98', '#f5eef8', 'STEP 3 — POSITION, CLEAN THE SKIN, AND STRETCH OR DISPLACE IT',
         'Position the patient so the muscle is relaxed. Clean the skin with an alcohol swab and let it dry. Either stretch the skin taut between two fingers, or displace it sideways (the Z-track technique) — the choice depends on the drug being given.'),
        ('#d4640a', '#fef3e2', 'STEP 4 — INSERT THE NEEDLE AT 90 DEGREES, IN ONE SMOOTH MOTION',
         'For most adult IM sites, insert the needle quickly and confidently at a 90-degree angle to the skin, to a depth that leaves a small length of the needle visible — roughly two-thirds of the needle\'s length in an average adult.'),
        ('#c0392b', '#fde8e8', 'STEP 5 — INJECT SLOWLY, THEN WITHDRAW AND RELEASE THE SKIN',
         'Inject the medication slowly and steadily (roughly 10 seconds per millilitre) to reduce discomfort and let the tissue accommodate the volume. Withdraw the needle smoothly, then release any stretched or displaced skin — this "seals" the needle track and helps stop the drug leaking back along it.'),
    ]
    yy = hh + 22
    for accent, bg, title, body in steps:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 16

    final = finish(img, draw, W, yy,
        'KEY CONCEPT — "90 degrees, two-thirds of the needle, slow injection, smooth withdrawal" applies to almost every adult IM site',
        f['XS'])
    return i2r(final, CW)

# ── PIL 5: Complications of IM injection and how they are prevented ────────
def make_complications():
    W, H_MAX = 900, 1800
    f = load_fonts(CARD_FONTS)
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PAD_X, W - PAD_X
    hh = header_band(draw, W, 'COMPLICATIONS OF INTRAMUSCULAR INJECTION — AND HOW EACH IS PREVENTED', f['T'], PAD_X)

    comps = [
        ('#c0392b', '#fde8e8', 'NERVE INJURY (E.G., SCIATIC/PERONEAL, RADIAL, AXILLARY)',
         'Sudden severe pain, an "electric shock" sensation, or numbness/weakness following an injection suggests direct needle trauma to a nerve. PREVENTION: correct site selection (ventrogluteal rather than dorsogluteal; correct deltoid landmark) and STOPPING immediately if the patient reports a shooting or electric sensation during insertion.'),
        ('#7d3c98', '#f5eef8', 'INTRAVASCULAR INJECTION',
         'Accidental injection of a drug intended for muscle directly into a blood vessel can cause rapid systemic effects, or, with some depot preparations, embolic complications. PREVENTION: slow, controlled injection technique, and being alert to any sudden change if blood appears in the needle hub on insertion.'),
        ('#d4640a', '#fef3e2', 'INJECTION-SITE INFECTION — ABSCESS OR CELLULITIS',
         'Presents as increasing pain, redness, swelling, warmth, and sometimes a discharging lump at the injection site, days after the injection. PREVENTION: strict aseptic technique, single-use sterile needles and syringes, and cleaning the skin before injection.'),
        ('#1a8a94', '#e0f4f5', 'MUSCLE FIBROSIS AND CONTRACTURE (REPEATED INJECTIONS)',
         'Repeated injections into the same site, especially in children receiving frequent injections such as antibiotics, can cause localised muscle fibrosis, scarring and contracture over time. PREVENTION: rotate injection sites systematically and record which site was used last.'),
        ('#2471a3', '#e8f4fd', 'HAEMATOMA AND BLEEDING (ESPECIALLY IN ANTICOAGULATED PATIENTS)',
         'Patients on anticoagulants or with bleeding disorders are at higher risk of a painful intramuscular haematoma after an IM injection. PREVENTION: where possible use the smallest appropriate needle gauge, apply firm pressure (without rubbing) for several minutes afterwards, and consider whether a non-IM route is available for that drug.'),
    ]
    yy = hh + 22
    for accent, bg, title, body in comps:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 14

    final = finish(img, draw, W, yy,
        'KEY CONCEPT — most serious IM injection complications are PREVENTABLE through site selection, technique and asepsis, not "bad luck"',
        f['XS'])
    return i2r(final, CW)

img_anatomy  = make_gluteal_anatomy()
img_landmark = make_ventrogluteal_landmark()
img_sites    = make_site_comparison()
img_technique= make_technique_steps()
img_complic  = make_complications()

print('PIL diagrams done.')

# ═══════════════════════════════════════════════════════════════════════════
# STORY BUILD
# ═══════════════════════════════════════════════════════════════════════════
story = []

story.append(Paragraph('SAFE INTRAMUSCULAR INJECTION TECHNIQUE', sTitle))
story.append(Paragraph('Gluteal Anatomy, Site Selection and Avoiding Nerve Injury — MRCP Part 1, Part 2 &amp; PACES, Interactive Edition', sSub))
story.append(HRFlowable(width=CW, thickness=2, color=TEAL, spaceAfter=10))

# §1 Clinical Scenario
sec_header('Section 1: Why This Topic Matters', story)
story.append(bp('We have already discussed a case where a patient receiving IM diclofenac for renal colic developed a SCIATIC/COMMON PERONEAL NERVE INJURY because of where the injection was given. That case was not a freak accident — it is a recognised, well-described complication, and almost entirely PREVENTABLE if the person giving the injection understands the anatomy of the buttock and uses a reliable LANDMARK TECHNIQUE rather than "by eye."'))
professor_says('Every doctor, nurse, and medical student gives IM injections — often hundreds over a career — yet the anatomy behind WHY one site is safer than another is rarely taught properly. This note works through the anatomy, the landmark techniques for every major IM site, the step-by-step safe procedure, and the complications that follow when things go wrong. By the end, you should be able to explain — and demonstrate — why the ventrogluteal site is now preferred for most adult IM injections.', story)
divider(story)

# §2 Anatomy of the buttock
sec_header('Section 2: Anatomy of the Buttock — Why the Site Matters', story)
story.append(bp('The buttock is not a uniform mass of muscle that is "safe anywhere." It is a layered structure: GLUTEUS MAXIMUS superficially, GLUTEUS MEDIUS and GLUTEUS MINIMUS more deeply, and — running beneath and between these muscles — the SCIATIC NERVE and the SUPERIOR GLUTEAL VESSELS/NERVE. An injection that goes too deep, too medial, or into the wrong quadrant can strike any of these structures.'))

story.append(img_anatomy)
story.append(bp('The layered anatomy of the buttock — gluteal muscles, the sciatic nerve, the superior gluteal vessels, and why the "upper outer quadrant" rule has limits', sImg))
story.append(Spacer(1, 6))

image_search_box('gluteal region anatomy sciatic nerve ventrogluteal dorsogluteal injection sites', 'Google Images / Radiopaedia', story)

qa_block(
    'A nursing student is taught to give IM injections into the "upper outer quadrant" of the buttock, and is told this is always safe because it avoids the sciatic nerve.',
    'Is the "upper outer quadrant" rule a guarantee of safety? What is the single biggest limitation of this rule, especially in larger patients?',
    'Think about WHERE the sciatic nerve actually runs (roughly midway between two bony landmarks), and how accurately a "quadrant" drawn by eye on a buttock of varying size and shape can really be judged.',
    'No — the upper-outer-quadrant rule is a useful APPROXIMATION, not a guarantee. Its biggest limitation is that the sciatic nerve\'s course is variable between individuals, and the quadrant itself becomes harder to judge accurately by eye as the buttock gets larger (in obese patients) — meaning the "safe" quadrant can, in a meaningful minority of people, actually overlie the nerve or the superior gluteal vessels. This is why a precise, palpable LANDMARK technique (the ventrogluteal method, Section 3) is now preferred over a visually-estimated quadrant.',
    story)
memory_hook('THREE STRUCTURES TO RESPECT IN THE BUTTOCK: the SCIATIC NERVE (deep to gluteus maximus, midway between PSIS and ischial tuberosity), the SUPERIOR GLUTEAL VESSELS/NERVE (upper part of the greater sciatic notch), and the variability of BOTH between individuals — which is why landmark technique beats "by eye."', story)
divider(story)

# §3 The Ventrogluteal Site
sec_header('Section 3: The Ventrogluteal Site — The Preferred Site For Adult IM Injections', story)
story.append(bp('The VENTROGLUTEAL site overlies GLUTEUS MEDIUS on the outer, upper part of the hip. It is found using a simple HAND-LANDMARK technique (the Hochstetter, or von Hochstetter, method), which uses the greater trochanter, the anterior superior iliac spine (ASIS), and the iliac crest to define a small triangle that is reliably free of major nerves and vessels.'))

story.append(img_landmark)
story.append(bp('The Hochstetter landmark method for finding the ventrogluteal site, step by step', sImg))
story.append(Spacer(1, 6))

image_search_box('ventrogluteal injection site Hochstetter landmark technique hand position', 'Google Images / YouTube', story)

story.append(bp('<b>Why the ventrogluteal site is now preferred:</b>'))
for pt in [
    'It is anatomically separated from the sciatic nerve, the superior gluteal vessels, and major bony landmarks by a reliable margin — in almost everyone, regardless of body habitus.',
    'It can accommodate larger volumes (up to around 3mL, sometimes more) and thicker/more viscous medications.',
    'Patient positioning is flexible — supine, lateral, or prone all work.',
    'The landmark technique uses the clinician\'s OWN HAND as a measuring tool, so it scales naturally to the size of the patient — unlike a quadrant "drawn by eye."',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 4))

qa_block(
    'You are about to give an IM depot antipsychotic injection (a relatively large, viscous volume) to an adult patient. You are deciding between the ventrogluteal and dorsogluteal sites.',
    'Which site would you choose, and what TWO separate reasons make it the better choice for THIS particular injection?',
    'Think about (1) the anatomical safety margin from the sciatic nerve, and (2) which muscle better tolerates a larger volume of a thick/irritant medication.',
    'The VENTROGLUTEAL site is the better choice, for two reasons: (1) it is reliably clear of the sciatic nerve and superior gluteal vessels, which is especially important for a depot drug that may cause local tissue irritation or, rarely, embolic complications if injected near a vessel; and (2) gluteus medius at the ventrogluteal site tolerates larger volumes of viscous medication well, with reliable absorption — both factors make it the recommended site for depot antipsychotic injections in current guidance.',
    story)
memory_hook('VENTROGLUTEAL = "V for Very safe, Very versatile" — first choice for most adult IM injections, including depot antipsychotics, found using the HAND-LANDMARK "V" technique (palm on trochanter, index to ASIS, middle finger along iliac crest, inject in the V).', story)
divider(story)

# §4 The Dorsogluteal Site
sec_header('Section 4: The Dorsogluteal Site — Why It Is Falling Out Of Favour', story)
story.append(bp('The DORSOGLUTEAL site is the traditional "upper outer quadrant of the buttock" injection site, targeting GLUTEUS MAXIMUS. It was, for decades, the default IM site taught to nurses and doctors worldwide — and it is still in widespread use. However, current evidence and guidance increasingly favour the ventrogluteal site instead, for the reasons below.'))

story.append(bp('<b>Problems with the dorsogluteal site:</b>'))
for pt in [
    '<b>Proximity to the sciatic nerve</b> — its course is variable, and in some individuals it lies closer to the "upper outer quadrant" than expected, especially when the quadrant is misjudged.',
    '<b>Proximity to the superior gluteal artery and nerve</b> — an injection placed too superiorly or medially risks these vessels.',
    '<b>Slower, less predictable absorption</b> — gluteus maximus is less vascular than gluteus medius, and there is often more subcutaneous fat overlying it, which can mean the "intramuscular" injection actually ends up subcutaneous if the needle is too short.',
    '<b>Quadrant estimation is harder in larger patients</b> — the larger the buttock, the harder it is to judge "upper outer quadrant" accurately by eye, and the greater the absolute distance error for a given angular misjudgement.',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 4))

info_box('This does NOT mean the dorsogluteal site is "forbidden" — it remains an option, particularly where the ventrogluteal site cannot be used (e.g., local skin conditions, patient positioning constraints). But where there is a choice, current guidance favours the ventrogluteal site for adults, precisely because of the issues above.', story)
memory_hook('DORSOGLUTEAL = the site most often blamed for sciatic nerve injury — not because it is always dangerous, but because the "upper outer quadrant" is an ESTIMATE, and estimates have a margin of error that the sciatic nerve sometimes falls inside.', story)
divider(story)

# §5 Comparing all five IM sites
sec_header('Section 5: Comparing All Five Intramuscular Injection Sites', story)
story.append(bp('Beyond the gluteal region, IM injections can also be given into the DELTOID (upper arm), the VASTUS LATERALIS (anterolateral thigh), and the RECTUS FEMORIS (anterior thigh). Each has its own landmark, typical use, and pitfalls.'))

story.append(img_sites)
story.append(bp('The five main IM injection sites compared — preferred uses, volumes, and the structures to avoid at each', sImg))
story.append(Spacer(1, 6))

image_search_box('intramuscular injection sites deltoid vastus lateralis ventrogluteal dorsogluteal rectus femoris comparison', 'Google Images', story)

site_table = [
    ['Site','Muscle','Typical Use','Structure(s) To Avoid'],
    ['Ventrogluteal','Gluteus medius','First choice for most\nadult IM injections,\nincluding depot\nantipsychotics\n(up to ~3mL+).','Sciatic nerve, superior\ngluteal vessels — both\nreliably AVOIDED here.'],
    ['Dorsogluteal','Gluteus maximus','Traditional site;\nstill used where\nventrogluteal is\nnot accessible.','Sciatic nerve, superior\ngluteal vessels — course\nvariable, quadrant\nestimation error.'],
    ['Deltoid','Deltoid (middle\nfibres)','Vaccines and other\nsmall volumes\n(up to ~1mL).','Radial nerve and\nbrachial artery in the\nspiral groove if the\nsite is too low.'],
    ['Vastus lateralis','Vastus lateralis\n(quadriceps)','First choice in\ninfants and young\nchildren; also used\nin adults.','Femoral nerve/vessels\n(medial), sciatic nerve\n(posterior) — both\navoided by staying\nanterolateral.'],
    ['Rectus femoris','Rectus femoris\n(quadriceps)','Self-injection\n(e.g., some\nbiologic therapies).','Femoral nerve/vessels\nif injected too medially.'],
]
story.append(plain_table(site_table,[CW*0.16, CW*0.16, CW*0.32, CW*0.36]))
story.append(Spacer(1, 4))

qa_block(
    'A 6-month-old infant requires an IM vaccine. The gluteal muscles in infants are small and underdeveloped, and the sciatic nerve occupies a relatively larger proportion of the buttock in infancy than in adults.',
    'Which site should be used for IM injections in infants and young children, and why is the gluteal region specifically AVOIDED in this age group?',
    'Think about muscle BULK relative to nerve size — what happens to the safety margin when the target muscle is small but the nerve running through the region is relatively large?',
    'The VASTUS LATERALIS (anterolateral thigh) is the preferred site in infants and young children. The gluteal region is avoided because the gluteal muscles are not yet well developed, meaning there is less muscle bulk to "buffer" the needle from the sciatic nerve — the safety margin that exists in a well-muscled adult buttock does not reliably exist in an infant.',
    story)
memory_hook('"V FOR VENTROGLUTEAL IN ADULTS, V FOR VASTUS LATERALIS IN INFANTS" — both are "V" sites chosen because they keep the needle away from major nerves; DELTOID is for small volumes only; RECTUS FEMORIS is mainly a self-injection site.', story)
divider(story)

# §6 Needle Selection
sec_header('Section 6: Needle Selection — Length, Gauge, and Body Habitus', story)
professor_says('A needle that is too SHORT for a given site may deposit the drug in subcutaneous fat rather than muscle — slowing absorption and, for some drugs (e.g., depot antipsychotics, vaccines), reducing effectiveness or increasing local reactions. A needle that is too LONG risks reaching structures beyond the muscle. Getting this right is not guesswork — it depends on the SITE and the patient\'s BODY HABITUS.', story)

needle_table = [
    ['Factor','What It Determines','Practical Point'],
    ['Needle LENGTH','How deep the tip\nreaches — must pass\nthrough skin and\nsubcutaneous fat to\nreach muscle, without\ngoing beyond it.','Larger patients (more\nsubcutaneous fat) generally\nneed a LONGER needle for\nthe same site; thin\npatients or children\nneed a SHORTER one.'],
    ['Needle GAUGE\n(bore width)','How easily the drug\ncan be drawn up and\ninjected, and how much\ndiscomfort/tissue trauma\nresults.','Thicker/viscous drugs\n(depot antipsychotics,\nsome penicillin\nsuspensions) need a\nWIDER bore (lower\ngauge number); thin\naqueous drugs and\nvaccines can use a\nNARROWER bore\n(higher gauge number).'],
    ['Injection SITE','Different sites have\ndifferent typical\nsubcutaneous fat\ndepths and muscle\nbulk.','Deltoid and vastus\nlateralis usually need\na shorter needle than\nventrogluteal/\ndorsogluteal in the\nsame patient.'],
]
story.append(plain_table(needle_table,[CW*0.18, CW*0.38, CW*0.44]))
story.append(Spacer(1, 4))

alert_box('A needle chosen purely "by habit," without considering the SITE and the individual PATIENT, is one of the most common avoidable errors in IM injection technique — and a needle that is too short for an obese patient is a well-recognised cause of an injection that is, unintentionally, only subcutaneous.', story)
memory_hook('LENGTH depends on the PATIENT (fat thickness); GAUGE depends on the DRUG (viscosity). Both also depend on the SITE. Never choose a needle "on autopilot."', story)
divider(story)

# §7 Step-by-step technique
sec_header('Section 7: Step-by-Step Safe Intramuscular Injection Technique', story)
story.append(bp('Once the site has been chosen and located using the appropriate landmark technique, and an appropriate needle selected, the actual injection follows a consistent five-step sequence — regardless of which site is being used.'))

story.append(img_technique)
story.append(bp('The five-step sequence for a safe IM injection — preparation, needle selection, skin technique, insertion, and injection/withdrawal', sImg))
story.append(Spacer(1, 6))

image_search_box('intramuscular injection technique 90 degree angle Z-track demonstration', 'Google Images / YouTube', story)

qa_block(
    'You are giving an IM injection. As you insert the needle, the patient suddenly cries out and describes a sharp, shooting, "electric shock"-like pain travelling down the back of their leg.',
    'What does this symptom suggest, and what is the SINGLE most important immediate action?',
    'Think about what structure, if directly contacted by a needle, would produce a sudden shooting/electric sensation radiating along a limb — and what continuing to inject (or continuing to advance the needle) into that structure would risk.',
    'A sudden shooting, "electric shock"-like pain radiating down the limb during needle insertion strongly suggests the needle has come into direct contact with a NERVE (e.g., the sciatic nerve, if the buttock is the site). The single most important immediate action is to STOP — withdraw the needle slightly (or fully) WITHOUT injecting any further — before re-assessing the site, rather than continuing to advance or inject, which risks worsening a nerve injury that may otherwise have been only a brief, reversible contact.',
    story)
memory_hook('"ELECTRIC SHOCK = STOP." Any sudden shooting/radiating pain on needle insertion means STOP immediately, withdraw, and reassess — do not inject through it.', story)
divider(story)

# §8 Z-track and aspiration
sec_header('Section 8: The Z-Track Technique and the Aspiration Debate', story)
story.append(bp('<b>The Z-track technique:</b> before inserting the needle, the skin and subcutaneous tissue are pulled sideways (laterally) by about 1-1.5cm and held in that displaced position while the needle is inserted and the drug injected. After withdrawing the needle, the skin is released, returning to its normal position. This creates a "Z-shaped," zig-zag needle track through the tissues, rather than a straight one.'))

story.append(bp('<b>Why use it?</b> Once the skin is released, the displaced layers seal over the needle track at different points — reducing the chance of the injected drug TRACKING BACK along the needle path into the subcutaneous tissue or onto the skin surface. This is particularly useful for drugs that are known to be irritant, can stain the skin, or are given in larger volumes (e.g., iron preparations, some depot medications).'))

story.append(bp('<b>The aspiration debate:</b> "aspiration" means pulling back gently on the plunger after inserting the needle, before injecting, to check that the needle tip has not entered a blood vessel (if blood appears in the syringe, the needle is repositioned). This was traditionally taught as a routine step for ALL IM injections.'))

for pt in [
    'More recent guidance (including for many vaccines) has moved AWAY from routine aspiration for injections into sites such as the deltoid and vastus lateralis, on the basis that major blood vessels are not typically present at these sites when correct landmark technique is used, and that aspiration may increase discomfort without meaningful safety benefit.',
    'However, for SITES OR DRUGS where intravascular injection would be particularly hazardous (for example, some depot preparations into the gluteal region), many protocols still recommend aspiration as an additional safety step.',
    '<b>The exam-safe answer:</b> know that aspiration practice varies by site and by local/national guidance — the unifying principle is "be aware of the possibility of intravascular injection, and follow the specific guidance for the drug and site you are using."',
]:
    story.append(bp(f'  • {pt}'))
memory_hook('Z-TRACK = displace the skin BEFORE injecting, release it AFTER withdrawing — seals the needle track. ASPIRATION = a safety check whose routine use now varies by site/drug — know the PRINCIPLE (avoiding intravascular injection), not a single universal rule.', story)
divider(story)

# §9 Volume limits
sec_header('Section 9: Volume Limits and Multiple Injections', story)
story.append(bp('Each IM site has a practical upper limit for the volume of medication that can be comfortably and safely accommodated in a single injection. Exceeding this limit increases pain, the risk of the drug tracking back along the needle path, and can reduce absorption.'))

vol_table = [
    ['Site','Typical Adult Volume Limit','Notes'],
    ['Ventrogluteal','Up to ~3mL, sometimes\nslightly more in a\nwell-muscled adult.','The largest practical\nvolume of the commonly\nused sites.'],
    ['Dorsogluteal','Up to ~3mL.','Similar volume capacity\nto ventrogluteal, but\nwith the anatomical\ndrawbacks discussed\nin Section 4.'],
    ['Vastus lateralis','Up to ~2-3mL in\nadults; smaller\nvolumes in infants\n(e.g., ~0.5-1mL).','Volume limit in\ninfants is much\nlower due to smaller\nmuscle bulk.'],
    ['Deltoid','Up to ~1mL\n(occasionally up to\n~2mL in larger\nadults).','The smallest-capacity\ncommonly used site —\nthis is why most\nvaccines given here\nare small-volume.'],
]
story.append(plain_table(vol_table,[CW*0.18, CW*0.38, CW*0.44]))
story.append(Spacer(1, 4))

story.append(bp('<b>If a single injection would exceed the safe volume for the chosen site</b>, the dose should be SPLIT between two separate sites (e.g., both deltoids, or one ventrogluteal and one vastus lateralis), rather than forcing a large volume into one site. This should be clearly documented, including which site received which part of the dose.'))
memory_hook('"WHEN IN DOUBT, SPLIT THE DOSE." A volume that exceeds the comfortable limit for a site is not a reason to "push it in anyway" — it is a reason to use two sites.', story)
divider(story)

# §10 Complications
sec_header('Section 10: Complications of IM Injection — and How They Are Prevented', story)
story.append(bp('Most serious complications of IM injection fall into a small number of recognisable categories — and almost all of them are preventable through correct site selection, technique, and asepsis, as the case discussed earlier in this series of notes illustrates.'))

story.append(img_complic)
story.append(bp('The main complications of IM injection, their warning signs, and how each is prevented', sImg))
story.append(Spacer(1, 6))

image_search_box('intramuscular injection complications nerve injury abscess haematoma muscle fibrosis', 'Google Images', story)

alert_box('Any patient who reports a shooting/electric pain, immediate or progressive numbness, or weakness following an IM injection should have this DOCUMENTED CLEARLY, the affected limb examined and re-examined over time, and — if it does not resolve — referred for further assessment, exactly as described in our earlier note on iatrogenic sciatic/peroneal nerve injury.', story)
memory_hook('FIVE COMPLICATIONS, FIVE PREVENTIONS: Nerve injury -> correct site + stop if shooting pain. Intravascular injection -> slow injection + awareness. Abscess/cellulitis -> asepsis. Fibrosis/contracture -> rotate sites. Haematoma -> smallest needle + pressure, especially if anticoagulated.', story)
divider(story)

# §11 High-risk drugs given IM
sec_header('Section 11: High-Risk Drugs Given Intramuscularly', story)
story.append(bp('Not all IM injections carry the same risk profile. Some drugs are particularly relevant to MRCP because of their specific properties — viscosity, irritancy, or the consequences if injected into the wrong site or structure.'))

drug_table = [
    ['Drug / Class','Why It Matters IM','Practical Point'],
    ['Depot antipsychotics\n(e.g., haloperidol\ndecanoate, zuclopenthixol\ndecanoate)','Oily, viscous\npreparations; large\nvolumes; given at\ninfrequent intervals\nso errors are not\nquickly correctable.','Ventrogluteal preferred;\nZ-track technique often\nrecommended; rotate\nsites between doses.'],
    ['Diclofenac (NSAID)','As discussed in our\nearlier note — IM NSAID\ninjections into the\nbuttock have been\nassociated with sciatic\nnerve injury.','Correct site selection\n(ventrogluteal) is the\nkey preventive step;\noral/rectal routes are\nalternatives where\nappropriate.'],
    ['Vitamin B12\n(hydroxocobalamin)','Given regularly (e.g.,\nevery 2-3 months for\npernicious anaemia) —\nrepeated injections over\nyears.','Site ROTATION is\nimportant to avoid\ncumulative muscle\nfibrosis at one\nrepeatedly-used site.'],
    ['Benzathine penicillin','Very viscous suspension;\nused for conditions such\nas syphilis and rheumatic\nfever prophylaxis.','Requires a wider-bore\nneedle; slow injection\nreduces discomfort and\nthe (rare) risk of an\nembolic reaction if\ninjected intravascularly.'],
    ['Vaccines (e.g.,\ninfluenza, COVID-19)','Given to huge numbers\nof people, including\nthose who are needle-\nphobic or have\nbleeding disorders.','Deltoid is standard for\nadults; aspiration is\ngenerally NOT performed\nfor most modern vaccines\ngiven into the deltoid.'],
]
story.append(plain_table(drug_table,[CW*0.22, CW*0.38, CW*0.40]))
story.append(Spacer(1, 4))

qa_block(
    'A patient with pernicious anaemia has received IM hydroxocobalamin (vitamin B12) injections every 3 months for the past 10 years, always into the same site because "it\'s easier to find."',
    'What complication is this patient at increased risk of, specifically because of the REPEATED use of the same site — and what simple practice would reduce this risk?',
    'Think about what happens to muscle tissue when it is repeatedly punctured and injected into, over years, at exactly the same point.',
    'This patient is at increased risk of LOCALISED MUSCLE FIBROSIS AND CONTRACTURE at the repeatedly-used site, from the cumulative effect of many injections into the same small area of tissue over a decade. The simple preventive practice is SITE ROTATION — systematically alternating between the available IM sites (and between left and right sides) for each injection, ideally with a documented record of which site was used last.',
    story)
memory_hook('REPEATED INJECTIONS (B12, depot antipsychotics, some vaccines given in series) = ROTATE SITES. A single injection = choose the BEST site for that drug and patient.', story)
divider(story)

# §12 Special populations
sec_header('Section 12: Special Populations', story)
story.append(bp('The general principles above apply to most adults — but several patient groups need additional consideration.'))

for pt in [
    '<b>Infants and young children:</b> use the VASTUS LATERALIS (or, in older children, the deltoid for small volumes) — the gluteal region is avoided because gluteal muscle bulk is insufficient relative to the size of the sciatic nerve in this age group (Section 5).',
    '<b>Elderly or very thin patients:</b> reduced subcutaneous fat AND reduced muscle bulk mean a SHORTER needle may be needed to avoid the injection being too deep, but care must be taken not to choose a needle so short that the injection becomes subcutaneous rather than intramuscular.',
    '<b>Obese patients:</b> increased subcutaneous fat may require a LONGER needle to reach muscle at the chosen site, and landmark techniques (rather than visual estimation of a "quadrant") become even more important, as discussed in Section 2.',
    '<b>Patients on anticoagulants or with bleeding disorders:</b> where possible, use the smallest appropriate needle gauge, apply firm pressure (not rubbing) for several minutes after the injection, and consider whether a non-IM route (oral, subcutaneous, intravenous) is available for the same drug — IM injections are relatively contraindicated in significant coagulopathy unless no alternative exists.',
    '<b>Patients with neuromuscular disease or significant muscle wasting:</b> reduced muscle bulk at standard sites may make the ventrogluteal or vastus lateralis sites relatively safer/more reliable than a wasted gluteus maximus.',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 4))
memory_hook('SPECIAL POPULATIONS — SAME PRINCIPLES, DIFFERENT NUMBERS: infants -> vastus lateralis; elderly/thin -> shorter needle but still IM; obese -> longer needle + landmark technique; anticoagulated -> smallest needle + pressure + consider alternative route.', story)
divider(story)

# §13 Recap: how the earlier case could have been prevented
sec_header('Section 13: Recap — How the Earlier Nerve Injury Case Could Have Been Prevented', story)
story.append(bp('Returning to the case from our earlier note: a patient receiving IM diclofenac for renal colic developed a sciatic/common peroneal nerve injury after an injection into the buttock. Now that we have worked through gluteal anatomy, site selection, and technique in detail, we can identify exactly where in the process a different choice would likely have prevented this complication.'))

prevent_table = [
    ['Step In The Process','What Happened','What Could Have Been Done Differently'],
    ['Site selection','Injection given into\nthe dorsogluteal\n("upper outer quadrant")\nregion.','Choosing the\nVENTROGLUTEAL site\n(Section 3) would have\nplaced the injection\nreliably clear of the\nsciatic nerve.'],
    ['Landmark technique','Site estimated\nvisually rather than\nusing a hand-landmark\nmethod.','Using the Hochstetter\nmethod (Section 3)\nturns site selection\ninto a reproducible,\npalpable technique\nrather than a\nvisual estimate.'],
    ['Response to\nimmediate symptoms','Patient reported\nnumbness shooting\ndown the leg AT THE\nMOMENT of injection.','Immediate cessation of\ninjection at the first\nsign of a shooting/\nelectric sensation\n(Section 7) may limit\nthe injury to a brief,\nreversible contact\n(neurapraxia) rather\nthan a more sustained\ninjury.'],
]
story.append(plain_table(prevent_table,[CW*0.2, CW*0.38, CW*0.42]))
story.append(Spacer(1, 4))

professor_says('This is the value of connecting topics together: the SAME case can teach you the neuroanatomy of foot drop (our earlier note), AND the preventive anatomy and technique that should stop it happening in the first place (this note). In the exam, and in real practice, being able to move fluently between "what went wrong" and "how it is prevented" is exactly the kind of joined-up clinical reasoning that is rewarded.', story)
memory_hook('THE SAME CASE, TWO LESSONS: Note 1 = how to DIAGNOSE a sciatic/peroneal nerve injury once it has happened. Note 2 (this one) = how to PREVENT it happening in the first place, through site selection, landmark technique, and stopping immediately if a shooting pain occurs.', story)
divider(story)

# §14 PACES Station
sec_header('Section 14: PACES Station — Demonstrating and Explaining Safe IM Injection Technique', story)
story.append(bp('In a PACES-style station, you may be asked to demonstrate the ventrogluteal landmark technique on a manikin, or to explain to a patient (or a junior colleague) why a particular site and technique are being used. The structure below covers both.'))

paces_table = [
    ['Domain','What To Demonstrate / Say','Why It Matters'],
    ['Identifying the\nsite (practical)','Talk through the\nHochstetter landmark\nmethod out loud as you\nperform it: "I\'m placing\nmy palm on the greater\ntrochanter, my index\nfinger towards the ASIS,\nand spreading my middle\nfinger along the iliac\ncrest — I\'ll inject in\nthe centre of this V."','Demonstrates that you\nunderstand WHY this is\nthe site, not just\nWHERE to point — the\nexaminer is assessing\nunderstanding, not\njust a memorised\nposition.'],
    ['Safety checks\n(communication)','"Before I begin, I\'m\nchecking your details,\nthe drug and dose, and\nlooking at the skin here\nfor any scars, lumps or\nsigns of infection."','Reflects the\n"check and prepare"\nstep (Section 7) and\nshows systematic,\nsafe practice.'],
    ['Explaining the\nchoice of site\n(communication)','"I\'m using this site on\nthe side of your hip\nrather than the buttock,\nbecause it keeps the\nneedle well away from a\nlarge nerve that runs\nthrough the buttock."','Plain-language\nexplanation of WHY —\nbuilds trust and\nreflects genuine\nunderstanding of the\nanatomy.'],
    ['What to do if the\npatient reports\nshooting pain\n(communication +\nsafety)','"If you feel any sudden\nshooting or electric\nsensation down your leg\nat any point, tell me\nimmediately and I will\nstop straight away."','Pre-warning the patient\nand having a clear plan\nfor this scenario\ndemonstrates insight\ninto the most important\nsafety-netting step in\nthe whole procedure.'],
    ['After the\ninjection\n(communication)','"That\'s done. I\'ll just\napply gentle pressure\nfor a moment. Let me\nknow if you notice any\nunusual numbness,\nweakness, or worsening\npain over the next few\nhours."','Sets up appropriate\nsafety-netting and\ndocumentation, and\nshows the candidate\nthinks beyond the\nmoment of injection\nitself.'],
]
story.append(plain_table(paces_table,[CW*0.18, CW*0.46, CW*0.36]))
story.append(Spacer(1, 6))

story.append(bp('<b>PACES Communication — Explaining the procedure to a needle-anxious patient (in plain language):</b>'))
for pt in [
    '"This injection goes into the muscle on the side of your hip, not your bottom — it\'s actually a safer spot because it keeps the needle away from a big nerve."',
    '"It will feel like a quick scratch, then a bit of pressure as the medicine goes in — I\'ll go slowly to make it as comfortable as possible."',
    '"If at any point you feel a sudden shooting or electric feeling down your leg, tell me straight away and I\'ll stop immediately — that\'s really important."',
    '"Afterwards, it\'s normal to feel a little soreness at the site for a day or so. But if you notice any numbness, weakness, or that the soreness is getting worse rather than better, please let us know."',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 6))

minimal_rows = [
    [Paragraph('<b>MINIMAL RESOURCES SUMMARY — Giving Safe IM Injections With Limited Equipment</b>', sAlert)],
    [Paragraph('If a range of needle lengths/gauges is not available: Use the LONGEST and WIDEST-bore needle available that is appropriate for the drug and site, rather than the shortest/narrowest — an injection that ends up subcutaneous (too short a needle) is a common and avoidable error, and is generally a bigger problem than slightly more discomfort from a wider bore.', sBody)],
    [Paragraph('If you are unsure of the ventrogluteal landmark technique: The simplest reliable fallback is to ask the patient to lie on their side with the upper hip and knee flexed, place your hand flat on the greater trochanter as described in Section 3, and use the V formed between your index and middle fingers — this requires no equipment beyond your own hand.', sBody)],
    [Paragraph('If a treatment room/couch is not available: The ventrogluteal site can be accessed with the patient standing, sitting, supine, lateral, or prone — it is one of the most POSITION-FLEXIBLE sites, which is useful in resource-limited or bedside settings.', sBody)],
    [Paragraph('If documentation systems are basic: A simple paper record of "date, drug, dose, SITE (left/right, ventrogluteal/deltoid/etc.), and any immediate reaction" is enough to support safe site rotation for patients receiving repeated injections (e.g., B12, depot antipsychotics).', sBody)],
    [Paragraph('The single most valuable "device" in this entire topic costs nothing: your own hand, used correctly, to find the ventrogluteal landmark.', sBody)],
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
memory_hook('PACES READY-RECKONER: Narrate the LANDMARK as you find it. Explain WHY this site (away from the nerve). Pre-warn about shooting pain and have a clear "I will stop" plan. Safety-net afterwards (numbness, weakness, worsening pain).', story)
divider(story)

# §15 Self-Test
story.append(PageBreak())
sec_header('Section 15: Self-Test — Safe IM Injection Technique MCQ Examination (12 Questions)', story)
professor_says('Now it is YOUR turn to be the professor. Attempt every question fully before turning to the answer key at the very end of this document. Write your answer in the blank space provided.', story)
story.append(bp('<i>Instructions: Each question is a short clinical scenario, exactly as it would appear in the MRCP exam. Choose the SINGLE best answer from the options given (A-E). Write your chosen letter in the blank space. The correct answers and full explanations are given separately in Section 16, at the very end — do not look ahead!</i>'))
story.append(Spacer(1, 8))

mcq(1,
    'Which IM injection site is now generally recommended as the FIRST CHOICE for most adult intramuscular injections, including depot antipsychotics, because it is reliably free of major nerves and vessels?',
    [('A','Dorsogluteal (upper outer quadrant)'),
     ('B','Ventrogluteal'),
     ('C','Deltoid'),
     ('D','Rectus femoris'),
     ('E','Vastus medialis')],
    'B',
    'The ventrogluteal site, identified using a hand-landmark technique, is reliably free of major nerves and vessels and is now the recommended first-choice IM site for most adult injections, including larger or more viscous preparations such as depot antipsychotics.',
    story)

mcq(2,
    'When using the Hochstetter (von Hochstetter) landmark technique to find the ventrogluteal site, which bony landmarks are used to form the "V" shape between the index and middle fingers?',
    [('A','The posterior superior iliac spine and the ischial tuberosity'),
     ('B','The greater trochanter and the acromion'),
     ('C','The anterior superior iliac spine and the iliac crest'),
     ('D','The pubic symphysis and the iliac crest'),
     ('E','The ischial tuberosity and the iliac crest')],
    'C',
    'After placing the palm on the greater trochanter, the index finger is pointed towards the anterior superior iliac spine (ASIS), and the middle finger is spread back along the iliac crest — the "V" between these two fingers overlies gluteus medius, the ventrogluteal site.',
    story)

mcq(3,
    'What is the main anatomical concern with the traditional dorsogluteal ("upper outer quadrant") injection site?',
    [('A','It is too superficial to reach any muscle'),
     ('B','It overlies the variable course of the sciatic nerve and the superior gluteal vessels'),
     ('C','It cannot accommodate any volume greater than 0.5mL'),
     ('D','It is only accessible with the patient standing'),
     ('E','It always requires general anaesthesia')],
    'B',
    'The dorsogluteal site overlies the region through which the sciatic nerve and superior gluteal vessels pass, and their exact course varies between individuals — the "upper outer quadrant" is an estimate that may not always lie clear of these structures, especially in larger patients.',
    story)

mcq(4,
    'A 4-month-old infant requires an IM vaccine. Which site is preferred, and why?',
    [('A','Dorsogluteal — because infants have a small sciatic nerve'),
     ('B','Deltoid — because infants have well-developed shoulder muscles'),
     ('C','Vastus lateralis — because gluteal muscle bulk is insufficient relative to the sciatic nerve at this age'),
     ('D','Ventrogluteal — identical landmarks to adults'),
     ('E','Rectus femoris — because infants can self-administer here')],
    'C',
    'In infants and young children, the gluteal muscles are not yet well developed, so there is less muscle bulk to separate the needle from the sciatic nerve. The vastus lateralis (anterolateral thigh) is a large muscle with no major nerves or vessels nearby and is the preferred site at this age.',
    story)

mcq(5,
    'A patient is to receive an IM injection of a thick, oily depot antipsychotic preparation. Which TWO factors should specifically influence the choice of needle?',
    [('A','The patient\'s eye colour and handedness'),
     ('B','The viscosity of the drug (gauge) and the patient\'s subcutaneous fat thickness at the chosen site (length)'),
     ('C','The time of day and the room temperature'),
     ('D','The patient\'s preferred arm for blood pressure measurement'),
     ('E','The colour of the syringe')],
    'B',
    'Needle GAUGE should be wide enough to accommodate a viscous/oily drug without excessive force; needle LENGTH should be sufficient to reach muscle through the patient\'s subcutaneous fat at the chosen site, without being unnecessarily long.',
    story)

mcq(6,
    'During insertion of an IM needle into the buttock, the patient suddenly reports a sharp, shooting, "electric shock"-like pain radiating down the back of the leg. What is the most appropriate immediate action?',
    [('A','Continue injecting slowly, as this sensation is expected and harmless'),
     ('B','Inject the full dose quickly to finish before the sensation worsens'),
     ('C','Stop immediately, withdraw the needle without injecting further, and reassess'),
     ('D','Switch to a longer needle and try again at the same spot'),
     ('E','Ignore the report and ask the patient to remain still')],
    'C',
    'A sudden shooting/electric pain radiating along a limb during needle insertion suggests direct nerve contact. The needle should be stopped and withdrawn immediately without further injection, to minimise the risk of converting a brief, reversible contact into a more significant nerve injury.',
    story)

mcq(7,
    'What is the purpose of the Z-track injection technique?',
    [('A','To make the injection more painful as a deterrent to repeated use'),
     ('B','To displace the skin and subcutaneous tissue before injection, so that on release the tissue layers seal over the needle track and reduce the chance of the drug tracking back to the surface'),
     ('C','To guarantee the needle enters a blood vessel'),
     ('D','To allow the injection to be given without cleaning the skin'),
     ('E','To increase the volume that can be given at a single site beyond normal limits')],
    'B',
    'In the Z-track technique, the skin is displaced laterally before needle insertion and released after withdrawal. The displaced tissue layers then seal over the needle track at different points, reducing the chance of the injected drug tracking back into subcutaneous tissue or onto the skin surface.',
    story)

mcq(8,
    'Regarding "aspiration" (pulling back on the plunger before injecting) for IM injections, which statement is most accurate?',
    [('A','Aspiration is mandatory for every IM injection at every site, with no exceptions'),
     ('B','Aspiration practice varies by site and drug — for example, it is generally not performed for many vaccines given into the deltoid, but may still be recommended for certain depot injections into the gluteal region'),
     ('C','Aspiration is never required for any IM injection'),
     ('D','Aspiration replaces the need for correct site selection'),
     ('E','Aspiration is only relevant for intravenous injections, not IM')],
    'B',
    'Aspiration is not a single universal rule — guidance varies by site and drug. Many modern vaccine protocols for the deltoid do not require routine aspiration, while some depot injections into the gluteal region may still recommend it as an additional safety step against intravascular injection.',
    story)

mcq(9,
    'A patient receiving IM vitamin B12 (hydroxocobalamin) injections every 3 months for the past several years, always at the same site, develops a firm, less mobile area of muscle at that site. What is the most likely cause, and what simple practice would reduce the risk of this?',
    [('A','Allergic reaction; switch to a different drug entirely'),
     ('B','Localised muscle fibrosis from repeated injection at the same site; reduced by systematic site rotation'),
     ('C','Normal ageing change unrelated to the injections'),
     ('D','Evidence of intravascular injection; requires anticoagulation'),
     ('E','A sign that the needle used was too long')],
    'B',
    'Repeated injections into the same site over years can cause localised muscle fibrosis and contracture. Systematic rotation of injection sites (and sides) reduces the cumulative trauma to any single area of muscle.',
    story)

mcq(10,
    'A patient on long-term warfarin requires an IM injection that cannot be substituted for another route. Which of the following is the MOST appropriate approach?',
    [('A','Use the largest-gauge (widest-bore) needle available to inject as quickly as possible'),
     ('B','Use the smallest appropriate needle gauge, apply firm pressure (without rubbing) for several minutes afterwards, and document clearly'),
     ('C','Avoid any pressure on the site afterwards, to prevent bruising'),
     ('D','Give the injection into the deltoid regardless of the drug, as this site never bleeds'),
     ('E','Double the usual injection speed to "get it over with"')],
    'B',
    'In anticoagulated patients where an IM injection cannot be avoided, using the smallest appropriate needle gauge and applying firm (not rubbing) pressure for several minutes afterwards reduces the risk of haematoma; clear documentation supports monitoring.',
    story)

mcq(11,
    'Why is the ventrogluteal site considered particularly POSITION-FLEXIBLE compared with some other IM sites?',
    [('A','It can only be accessed with the patient standing upright'),
     ('B','It can be accessed with the patient supine, lateral (on their side), or prone, as long as the hip and knee on the injection side are slightly flexed'),
     ('C','It requires the patient to be under general anaesthesia'),
     ('D','It can only be used if the patient is asleep'),
     ('E','It requires a specialised operating table')],
    'B',
    'The ventrogluteal site can be reached with the patient in a supine, lateral, or prone position, provided the hip and knee on the injection side are slightly flexed to relax the gluteal muscles — making it useful across a wide range of clinical settings, including bedside care.',
    story)

mcq(12,
    'A junior doctor asks why a patient who previously received an IM diclofenac injection into the dorsogluteal region developed numbness in the first web space of the foot and weakness of toe extension shortly afterwards. Which explanation best links the anatomy discussed in this note to that earlier case?',
    [('A','The injection was given into the deltoid by mistake'),
     ('B','The dorsogluteal site overlies the variable course of the sciatic nerve; the deep peroneal branch (supplying the first web space and toe extensors) was likely affected by direct needle trauma at this site'),
     ('C','Diclofenac cannot cause any nerve-related side effects by any route'),
     ('D','The vastus lateralis was used, which has no relationship to the sciatic nerve'),
     ('E','The patient\'s symptoms were entirely unrelated to the injection and represent a coincidental stroke')],
    'B',
    'This links directly to our earlier note: the dorsogluteal site overlies the variable course of the sciatic nerve. Direct needle trauma here can injure the common peroneal division (deep peroneal branch), producing first web space numbness and weak toe/foot dorsiflexion — exactly the pattern described in that case, and exactly the complication that ventrogluteal site selection (this note) is designed to prevent.',
    story)

divider(story)

# §16 Answer Key
story.append(PageBreak())
sec_header('Section 16: Answer Key — Self-Test Solutions and Explanations', story)
info_box('<b>Now check your work.</b> Go back through Section 15 question by question, compare your written answer with the correct answer below, and read the explanation — especially for any question you got wrong.', story)
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
    [Paragraph('MASTER MEMORY SUMMARY — SAFE INTRAMUSCULAR INJECTION TECHNIQUE', sGrnB)],
    [Paragraph('VENTROGLUTEAL = first choice for most adult IM injections (gluteus medius), found by the Hochstetter hand-landmark "V" (palm on greater trochanter, index to ASIS, middle finger along iliac crest). Reliably clear of the sciatic nerve and superior gluteal vessels.', sGrn)],
    [Paragraph('DORSOGLUTEAL ("upper outer quadrant," gluteus maximus) overlies the variable course of the sciatic nerve and superior gluteal vessels — falling out of favour as a first choice, though still used when ventrogluteal is not accessible.', sGrn)],
    [Paragraph('OTHER SITES: DELTOID for small volumes (~1mL, vaccines) — too low risks the radial nerve/brachial artery. VASTUS LATERALIS = first choice in infants (insufficient gluteal bulk). RECTUS FEMORIS = a self-injection site.', sGrn)],
    [Paragraph('TECHNIQUE: check/prepare -> choose needle (LENGTH by patient fat, GAUGE by drug viscosity) -> clean skin and stretch/displace (Z-track) -> insert at 90 degrees, ~2/3 of needle -> inject slowly (~10 sec/mL) -> withdraw and release skin.', sGrn)],
    [Paragraph('"ELECTRIC SHOCK = STOP" — any sudden shooting/radiating pain on insertion means stop immediately, withdraw without injecting further, and reassess.', sGrn)],
    [Paragraph('COMPLICATIONS AND PREVENTION: nerve injury (correct site + stop on shooting pain); intravascular injection (slow injection, awareness); abscess/cellulitis (asepsis); muscle fibrosis/contracture from repeated injections (rotate sites); haematoma in anticoagulated patients (smallest needle + pressure).', sGrn)],
    [Paragraph('VOLUME LIMITS: ventrogluteal/dorsogluteal up to ~3mL, vastus lateralis ~2-3mL (less in infants), deltoid ~1mL. If a dose would exceed the limit for one site, SPLIT it between two sites and document clearly.', sGrn)],
    [Paragraph('THE LINK BACK: the earlier sciatic/peroneal nerve injury case (dorsogluteal diclofenac injection) is exactly the scenario that ventrogluteal site selection, correct landmark technique, and stopping immediately on shooting pain are designed to prevent.', sGrn)],
]
innerG = Table(gRows, colWidths=[CW-4])
innerG.setStyle(gTS1)
outerG = Table([[innerG]], colWidths=[CW])
outerG.setStyle(gTSO)
story.append(outerG)
story.append(Spacer(1, 14))

# Footer note
story.append(HRFlowable(width=CW, thickness=1.5, color=HexColor('#0d5c63'), spaceAfter=6))
story.append(Paragraph('MRCP Revision Note: Safe Intramuscular Injection Technique — Gluteal Anatomy, Site Selection and Avoiding Nerve Injury  |  Sections 1-16, with Interactive Q&A, PACES Station, and Self-Test', ParagraphStyle('FT', fontName='DV-I', fontSize=8, leading=11, textColor=HexColor('#555555'), alignment=1)))

# Build document
doc.build(story)
print('SUCCESS:', OUT)
