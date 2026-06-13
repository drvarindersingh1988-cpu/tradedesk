"""
MRCP REVISION NOTE (BRIEF): Lateral Hip Pain — Greater Trochanteric Pain Syndrome and Differentials
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

OUT = '/mnt/user-data/outputs/Lateral_Hip_Pain_GTPS_MRCP_Note.pdf'
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

# ── PIL 1: Anatomy of the lateral hip — why this area is so easily irritated ─
def make_lateral_hip_anatomy():
    W, H_MAX = 900, 1500
    f = load_fonts(CARD_FONTS)
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PAD_X, W - PAD_X
    hh = header_band(draw, W, 'ANATOMY OF THE LATERAL HIP — THE "ROTATOR CUFF OF THE HIP"', f['T'], PAD_X)

    yy = hh + 22
    yy = card(draw, x0, x1, yy,
        'THE GREATER TROCHANTER — the bony "shelf" you feel on the side of the hip',
        'A bony prominence on the upper femur. Several tendons attach directly onto it, and a cushioning bursa sits between the tendons and the bone — this whole region is the "greater trochanter complex."',
        f['B'], f['XS'], '#0d5c63', '#dff2f1')
    yy += 16
    yy = card(draw, x0, x1, yy,
        'GLUTEUS MEDIUS AND MINIMUS TENDONS — the hip\'s "rotator cuff"',
        'These muscles attach onto the greater trochanter and are responsible for stabilising the pelvis with every step (preventing it dropping on the opposite side). Like the shoulder\'s rotator cuff, these tendons are prone to degenerative tendinopathy with age and repetitive load — this is now recognised as the PRIMARY problem in most "trochanteric bursitis."',
        f['B'], f['XS'], '#c0392b', '#fde8e8')
    yy += 16
    yy = card(draw, x0, x1, yy,
        'TROCHANTERIC BURSA — the cushion that can become secondarily inflamed',
        'A small fluid-filled sac that reduces friction between the gluteal tendons/ITB and the bone. True isolated bursitis is less common than once thought — most bursal inflammation is now considered SECONDARY to underlying gluteal tendinopathy.',
        f['B'], f['XS'], '#7d3c98', '#f5eef8')
    yy += 16
    yy = card(draw, x0, x1, yy,
        'ILIOTIBIAL BAND (ITB) — the tight band running over the trochanter',
        'A thick band of fascia running from the pelvis down the outside of the thigh to the knee, passing directly over the greater trochanter. A tight ITB increases compressive load on the tendons and bursa beneath it with every step.',
        f['B'], f['XS'], '#d4640a', '#fef3e2')
    yy += 16
    yy = card(draw, x0, x1, yy,
        'WHY LYING ON THAT SIDE AT NIGHT, AND PROLONGED SITTING, HURT',
        'Lying on the affected side directly COMPRESSES the gluteal tendons and bursa between the body weight and the mattress — reproducing the pain. Sitting with the hip flexed and adducted (legs crossed, low chairs) does the same thing via the ITB. This "compression" pattern, rather than a "wear and tear with activity" pattern, is the hallmark of gluteal tendinopathy/GTPS.',
        f['B'], f['XS'], '#1a8a94', '#e0f4f5')

    final = finish(img, draw, W, yy,
        'KEY CONCEPT — pain reproduced by COMPRESSING the lateral hip (side-lying, crossed legs, prolonged sitting) = tendinopathy/GTPS pattern, not an "activity-driven" arthritis pattern',
        f['XS'])
    return i2r(final, CW)

# ── PIL 2: Differential diagnosis of hip-region pain ────────────────────────
def make_hip_pain_diff():
    W, H_MAX = 900, 1700
    f = load_fonts(CARD_FONTS)
    img = Image.new('RGB', (W, H_MAX), '#f4fbfc')
    draw = ImageDraw.Draw(img)
    x0, x1 = PAD_X, W - PAD_X
    hh = header_band(draw, W, 'HIP-REGION PAIN — FIVE DIFFERENTIALS AND HOW TO TELL THEM APART', f['T'], PAD_X)

    diffs = [
        ('#0d5c63', '#dff2f1', '1. GREATER TROCHANTERIC PAIN SYNDROME (GTPS) — most likely here',
         'LATERAL hip pain (over the bony "shelf"), worse lying on that side at night, worse with prolonged sitting/crossed legs, "start-up" limp that EASES once moving, and does NOT typically limit running. Tender directly over the greater trochanter; pain reproduced by resisted hip abduction.'),
        ('#c0392b', '#fde8e8', '2. HIP OSTEOARTHRITIS (OA)',
         'GROIN pain (sometimes radiating to the front of thigh/knee), morning stiffness usually LASTING >30 minutes, pain that WORSENS progressively with activity/walking distance, and reduced internal rotation on examination — the single most sensitive sign of hip OA.'),
        ('#e6a817', '#fff3cd', '3. LUMBAR SPINE — REFERRED PAIN / RADICULOPATHY',
         'Buttock/lateral hip pain that follows a dermatomal or sclerotomal pattern, often with BACK PAIN, pain on straight-leg raise, or neurological symptoms (numbness, weakness, reflex change) in the leg. Hip joint movements (especially internal rotation) are usually pain-free.'),
        ('#7d3c98', '#f5eef8', '4. PIRIFORMIS / DEEP GLUTEAL SYNDROME',
         'Deep, central BUTTOCK pain (more medial than GTPS), sometimes radiating down the back of the thigh (sciatic nerve irritation), worse with prolonged sitting and certain hip rotation movements. The "FAIR" test (Flexion, ADDuction, Internal Rotation) reproduces the pain.'),
        ('#2471a3', '#e8f4fd', '5. MERALGIA PARAESTHETICA / ITB SYNDROME',
         'Meralgia paraesthetica: burning/numbness over the ANTEROLATERAL thigh (lateral cutaneous nerve of thigh entrapment), no weakness. ITB syndrome: pain over the lateral hip/thigh or lateral knee, classically related to repetitive activity (running/cycling) rather than rest/compression.'),
    ]
    yy = hh + 22
    for accent, bg, title, body in diffs:
        yy = card(draw, x0, x1, yy, title, body, f['B'], f['XS'], accent, bg)
        yy += 14

    final = finish(img, draw, W, yy,
        'THE THREE QUESTIONS THAT LOCALISE HIP PAIN — (1) Lateral or groin? (2) Worse with COMPRESSION (lying/sitting) or with LOAD/activity? (3) Any back pain or neurological symptoms?',
        f['XS'])
    return i2r(final, CW)

img_anatomy = make_lateral_hip_anatomy()
img_diff    = make_hip_pain_diff()

print('PIL diagrams done.')

# ═══════════════════════════════════════════════════════════════════════════
# STORY BUILD
# ═══════════════════════════════════════════════════════════════════════════
story = []

story.append(Paragraph('LATERAL HIP PAIN', sTitle))
story.append(Paragraph('Greater Trochanteric Pain Syndrome and its Differentials — Brief MRCP/PACES Note', sSub))
story.append(HRFlowable(width=CW, thickness=2, color=TEAL, spaceAfter=10))

# §1 Clinical Scenario
sec_header('Section 1: The Clinical Scenario', story)
story.append(bp('A person describes a PERSISTENT LEFT HIP PAIN. It is WORSE AT NIGHT, particularly when LYING ON THE AFFECTED SIDE. During the day, it is worse after SITTING for long periods, and there is a LIMP at the very start of walking ("start-up pain") that eases once moving. Importantly, the pain does NOT stop running or exercise — it is mostly a problem when NOT mobile.'))
professor_says('Read that pattern again, slowly: pain triggered by LYING on the side, by SITTING, and by the FIRST few steps — but not by running. This is a "compression and start-up" pattern, not a "the more I use it, the worse it gets" pattern. That single distinction is the key to this whole topic, and it points overwhelmingly towards ONE diagnosis before you even examine the patient.', story)
divider(story)

# §2 The Most Likely Diagnosis
sec_header('Section 2: The Most Likely Diagnosis — Greater Trochanteric Pain Syndrome (GTPS)', story)
story.append(bp('<b>Greater Trochanteric Pain Syndrome (GTPS)</b> is an umbrella term covering GLUTEAL TENDINOPATHY (gluteus medius/minimus, the primary problem in most cases) and TROCHANTERIC BURSITIS (now usually considered secondary to the tendinopathy). It is the SINGLE MOST COMMON cause of lateral hip pain in adults, especially women aged 40-60, but also seen in active men.'))

story.append(img_anatomy)
story.append(bp('The lateral hip "rotator cuff" — gluteal tendons, trochanteric bursa, and the iliotibial band, all compressed by side-lying and sitting', sImg))
story.append(Spacer(1, 6))

image_search_box('greater trochanteric pain syndrome gluteus medius tendinopathy anatomy', 'Google Images / Radiopaedia', story)

story.append(bp('<b>Typical risk factors:</b>'))
for pt in [
    'Age 40-60, more common in women.',
    'A tight or overactive iliotibial band (ITB).',
    'Leg length discrepancy, or a Trendelenburg-type gait pattern.',
    'Coexisting low back pain or hip OA (these conditions commonly overlap).',
    'Repetitive loading activities — running, hill walking, standing on one leg for long periods.',
    'Previous hip surgery (e.g., total hip replacement via a lateral approach).',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 4))

qa_block(
    'Two patients both have lateral hip pain. Patient A says the pain gets WORSE the longer they walk or run, and is accompanied by groin stiffness lasting 45 minutes every morning. Patient B says the pain is fine during a run, but is severe at night lying on that side and after sitting for an hour.',
    'Which patient is more likely to have hip OSTEOARTHRITIS, and which is more likely to have GREATER TROCHANTERIC PAIN SYNDROME — and what is the underlying mechanical reason for the difference?',
    'Osteoarthritis is a "wear and tear with loading" disease of the JOINT itself — cartilage loss is aggravated by repetitive joint loading. GTPS is a "compression" disease of the TENDONS/BURSA OUTSIDE the joint — what specifically compresses these structures?',
    'Patient A (worsening with walking/activity, prolonged morning groin stiffness) fits HIP OSTEOARTHRITIS — articular cartilage loss is aggravated by cumulative joint loading, and synovial/capsular stiffness is worst after a period of rest (morning). Patient B (fine during running, but severe with side-lying and prolonged sitting) fits GREATER TROCHANTERIC PAIN SYNDROME — the gluteal tendons and bursa are COMPRESSED against the greater trochanter by body weight in side-lying, and by the iliotibial band in hip-flexed sitting positions; running with a rhythmic, non-sustained load often does not reproduce this compressive pain in the same way.',
    story)
memory_hook('GTPS PROFILE: LATERAL hip pain + worse LYING on that side + worse SITTING + "start-up" limp that EASES with movement + tender directly over the greater trochanter. Hip OA PROFILE: GROIN pain + morning stiffness >30 min + WORSENS with ongoing activity + reduced internal rotation.', story)
divider(story)

# §3 Differential Diagnosis
sec_header('Section 3: Differential Diagnosis — Five Causes Of Hip-Region Pain', story)
professor_says('"Hip pain" is a location, not a diagnosis. Before you settle on GTPS, run through the alternatives — especially because GTPS frequently COEXISTS with hip OA or lumbar spine disease, and missing a coexisting cause means incomplete treatment.', story)

story.append(img_diff)
story.append(bp('Five causes of hip-region pain and the features that separate them', sImg))
story.append(Spacer(1, 6))

diff_table = [
    ['Diagnosis','Pain Location','Aggravating Pattern','Key Examination Finding'],
    ['GTPS (gluteal\ntendinopathy/bursitis)','Lateral hip, over the\ngreater trochanter.\nMay radiate down the\nouter thigh (but not\nbelow the knee).','Lying on that side,\nprolonged sitting,\ncrossing legs,\n"start-up" pain.','Direct tenderness over\nthe greater trochanter;\npain on resisted hip\nabduction/external\nderotation test.'],
    ['Hip osteoarthritis','Groin, sometimes\nradiating to anterior\nthigh/knee.','Progressive with\nwalking distance;\nmorning stiffness\n>30 minutes.','Reduced and painful\ninternal rotation\n(most sensitive sign);\nantalgic gait.'],
    ['Lumbar spine\nreferred pain /\nradiculopathy','Buttock/lateral hip,\noften with back pain;\nmay radiate down\nthe leg.','Positional (bending,\nsitting), often with\nback symptoms;\nneurological symptoms\nin the leg.','Positive straight-leg\nraise; neurological\ndeficit; hip joint\nmovements relatively\npain-free.'],
    ['Piriformis / deep\ngluteal syndrome','Deep, central buttock\n(more medial than GTPS);\nmay radiate down\nposterior thigh.','Prolonged sitting;\ncertain hip rotation\nmovements.','Positive FAIR test\n(Flexion, ADDuction,\nInternal Rotation\nreproduces pain).'],
    ['Meralgia\nparaesthetica /\nITB syndrome','Meralgia: anterolateral\nthigh. ITB syndrome:\nlateral hip/thigh\nor lateral knee.','Meralgia: tight\nclothing/belts,\nprolonged standing.\nITB: repetitive\nrunning/cycling.','Meralgia: sensory\nchange only, no\nweakness. ITB: tender\nalong the band,\nworse with knee\nflexion under load.'],
]
story.append(plain_table(diff_table,[CW*0.16, CW*0.2, CW*0.28, CW*0.36]))
alert_box('RED FLAGS — DO NOT ATTRIBUTE TO GTPS WITHOUT EXCLUDING THESE: unexplained weight loss, night pain that is constant and NOT position-dependent, fever, history of cancer (possible bony metastasis), significant trauma (fracture), or new neurological deficit — these need urgent further assessment, not a tendinopathy diagnosis.', story)
memory_hook('FIVE-WAY SPLIT: GTPS = lateral + compression pattern. OA = groin + activity pattern. Lumbar = back pain + neuro signs. Piriformis = deep central buttock + FAIR test. Meralgia/ITB = pure sensory anterolateral thigh, or activity-related lateral knee.', story)
divider(story)

# §4 Examination and Investigations
sec_header('Section 4: Examination and Investigations', story)
story.append(bp('<b>Focused examination for suspected GTPS:</b>'))
for pt in [
    '<b>Palpation:</b> direct tenderness over the greater trochanter is the most consistent finding.',
    '<b>Resisted hip abduction</b> (patient lying on the unaffected side, abducting the top leg against resistance) — reproduces lateral hip pain in gluteal tendinopathy.',
    '<b>Single-leg stance for ~30 seconds</b> — may reproduce pain (the gluteal tendons must work hardest to stabilise the pelvis).',
    '<b>Hip range of movement</b> — internal rotation is usually preserved and pain-free in GTPS (in contrast to hip OA, where it is reduced and painful).',
    '<b>FAIR test</b> (Flexion, Adduction, Internal Rotation) — if THIS reproduces deep buttock pain, consider piriformis/deep gluteal syndrome instead.',
    '<b>Straight-leg raise and a brief neurological exam of the leg</b> — to screen for a lumbar spine cause.',
]:
    story.append(bp(f'  • {pt}'))
story.append(Spacer(1, 4))

story.append(bp('<b>Investigations — GTPS is primarily a CLINICAL diagnosis:</b>'))
for pt in [
    '<b>No imaging is required to make the diagnosis</b> in a typical presentation — history and examination are usually sufficient.',
    '<b>Plain X-ray of the hip/pelvis</b> — reasonable if hip OA, fracture, or another bony cause needs to be excluded, especially if the pattern is atypical or there has been trauma.',
    '<b>Ultrasound or MRI</b> — reserved for cases that fail to improve with first-line treatment, to look for a gluteal tendon TEAR (rather than simple tendinopathy) or significant bursal effusion, which may change management.',
    '<b>Bloods (ESR/CRP, and consider inflammatory markers/ANA in younger patients)</b> — only if an inflammatory or infective cause is suspected (e.g., systemic symptoms, fever, multiple joints involved) — NOT routine for a typical isolated GTPS presentation.',
]:
    story.append(bp(f'  • {pt}'))
memory_hook('GTPS = CLINICAL DIAGNOSIS. Tenderness over the trochanter + pain on resisted abduction + pain-free internal rotation = enough to start treatment. Reserve imaging for atypical presentations, red flags, or failure of first-line treatment.', story)
divider(story)

# §5 Management
sec_header('Section 5: Management', story)
professor_says('The management of GTPS has changed significantly over the last decade — it has shifted from "rest and steroid injection" towards "education, load management, and progressive strengthening," because gluteal tendinopathy behaves like other tendinopathies (e.g., rotator cuff, Achilles, patellar) — it needs PROGRESSIVE LOADING to recover, not prolonged rest.', story)

mgmt_table = [
    ['Approach','What It Involves','Evidence/Role'],
    ['Education and activity\nmodification (FIRST STEP)','Avoid COMPRESSIVE positions:\ndo not lie directly on the\naffected side (use a pillow\nbetween the knees when on\nthe other side), avoid sitting\nwith legs crossed, avoid\nstanding with the hip\n"hitched"/adducted.','Often produces significant\nimprovement on its own —\nremoving the compressive\ntrigger reduces ongoing\nirritation of the tendon/bursa.'],
    ['Analgesia','Short course of simple\nanalgesia (paracetamol)\nor an NSAID if no\ncontraindication, mainly\nto allow participation\nin physiotherapy.','Symptom control only —\ndoes not address the\nunderlying tendinopathy.'],
    ['Physiotherapy —\nprogressive gluteal\nstrengthening (KEY\nTREATMENT)','A structured, progressive\nloading programme for\ngluteus medius/minimus,\nstarting with isometric\nholds and progressing to\nfunctional strengthening.','BEST EVIDENCE for\nlong-term improvement —\nsuperior to corticosteroid\ninjection at medium/\nlong-term follow-up in\nclinical trials.'],
    ['Corticosteroid\ninjection','Image-guided or landmark-\nguided injection into the\ntrochanteric bursa.','Can give useful SHORT-TERM\nrelief, especially if pain is\nsevere enough to prevent\nengaging with physiotherapy —\nbut benefit often does not\npersist, and REPEATED\ninjections risk further\ntendon weakening.'],
    ['Extracorporeal shockwave\ntherapy (ESWT)','Mechanical shockwaves\napplied to the tendon\ninsertion.','An option for cases that\nfail to respond to\nload-management and\nphysiotherapy alone.'],
    ['Surgery (rare)','Bursectomy, ITB release,\nor gluteal tendon repair\n(if a confirmed tear).','Reserved for a small\nminority with confirmed\nstructural pathology that\nfails all conservative\nmeasures.'],
]
story.append(plain_table(mgmt_table,[CW*0.2, CW*0.42, CW*0.38]))
story.append(Spacer(1, 4))

story.append(bp('<b>Explaining this to the patient, in plain language:</b>'))
for pt in [
    '"This is a very common problem with the tendons on the outside of your hip — think of it as similar to a \'tennis elbow\', but in the hip. It is NOT arthritis and it is NOT a sign of damage to the hip joint itself."',
    '"The pain at night happens because lying on that side squashes the tendon. Try sleeping on your other side with a pillow between your knees, or on your back."',
    '"Avoid sitting with your legs crossed, and try not to stand with your weight sunk into one hip."',
    '"The most effective long-term treatment is a specific set of strengthening exercises from a physiotherapist — this takes weeks to months, but works better in the long run than an injection alone."',
    '"You do not need to stop your normal exercise or running because of this — in fact, staying generally active is helpful, as long as you avoid the specific positions that bring the pain on."',
]:
    story.append(bp(f'  • {pt}'))
memory_hook('"PILLOW, POSITION, PHYSIO" — pillow between the knees at night, avoid compressive sitting positions during the day, and a progressive gluteal-strengthening physiotherapy programme is the treatment with the best long-term evidence. Steroid injection = short-term bridge, not a long-term fix.', story)
divider(story)

# §6 Self-Test
story.append(PageBreak())
sec_header('Section 6: Self-Test — Lateral Hip Pain MCQ Examination (8 Questions)', story)
professor_says('Attempt every question before turning to the answer key at the end. Write your answer in the blank space provided.', story)
story.append(bp('<i>Instructions: Each question is a short clinical vignette. Choose the SINGLE best answer (A-E). The correct answers and explanations are given separately in Section 7, at the very end — do not look ahead!</i>'))
story.append(Spacer(1, 8))

mcq(1,
    'A 52-year-old woman reports persistent left lateral hip pain, worse at night when lying on that side, worse after sitting for long periods, with a brief limp at the start of walking that eases after a few steps. Running does not provoke the pain. What is the most likely diagnosis?',
    [('A','Hip osteoarthritis'),
     ('B','Greater trochanteric pain syndrome (gluteal tendinopathy)'),
     ('C','Lumbar radiculopathy'),
     ('D','Avascular necrosis of the femoral head'),
     ('E','Septic arthritis of the hip')],
    'B',
    'A "compression and start-up" pattern — worse lying on the affected side, worse with prolonged sitting, easing once moving, and not limiting running — is the classic profile of greater trochanteric pain syndrome (gluteal tendinopathy ± bursitis).',
    story)

mcq(2,
    'Which examination finding would make you favour HIP OSTEOARTHRITIS over greater trochanteric pain syndrome (GTPS) in a patient with hip-region pain?',
    [('A','Tenderness directly over the greater trochanter'),
     ('B','Pain reproduced by resisted hip abduction'),
     ('C','Reduced and painful internal rotation of the hip, with groin pain and morning stiffness over 30 minutes'),
     ('D','Pain on single-leg standing'),
     ('E','Pain that is worse when lying on the affected side')],
    'C',
    'Reduced, painful internal rotation with groin-predominant pain and prolonged morning stiffness (>30 minutes) is the classic profile of hip osteoarthritis. The other options (trochanteric tenderness, pain on resisted abduction, single-leg stance pain, pain lying on that side) are all features of GTPS.',
    story)

mcq(3,
    'A patient with suspected GTPS asks what they can do to reduce night-time pain. What is the most appropriate first-line advice?',
    [('A','Sleep on the affected side to "stretch out" the tendon'),
     ('B','Avoid lying directly on the affected side; sleep on the other side with a pillow between the knees, or on the back'),
     ('C','Take strong opioid analgesia every night before bed'),
     ('D','Completely avoid all walking and exercise until pain-free'),
     ('E','Arrange an urgent MRI before giving any advice')],
    'B',
    'Night pain in GTPS results from direct compression of the gluteal tendons/bursa when lying on the affected side. Simple positional advice (avoiding that position, using a pillow between the knees) directly addresses the mechanism and is first-line, low-risk advice.',
    story)

mcq(4,
    'What is the treatment for greater trochanteric pain syndrome with the BEST evidence for long-term improvement?',
    [('A','Prolonged bed rest until symptoms fully resolve'),
     ('B','Repeated corticosteroid injections into the trochanteric bursa every few weeks'),
     ('C','A structured, progressive gluteal-strengthening physiotherapy programme'),
     ('D','Long-term daily high-dose NSAIDs'),
     ('E','Immediate surgical bursectomy')],
    'C',
    'Like other tendinopathies, gluteal tendinopathy responds best to progressive loading/strengthening. Trials have shown physiotherapy-based exercise programmes give superior medium- to long-term outcomes compared with corticosteroid injection, which gives only short-term relief and risks tendon weakening if repeated.',
    story)

mcq(5,
    'A patient with deep, central buttock pain radiating down the back of the thigh reports the pain is reproduced when the hip is flexed, adducted, and internally rotated (the "FAIR" test). What is the most likely diagnosis?',
    [('A','Greater trochanteric pain syndrome'),
     ('B','Piriformis / deep gluteal syndrome'),
     ('C','Meralgia paraesthetica'),
     ('D','Hip osteoarthritis'),
     ('E','Iliotibial band syndrome')],
    'B',
    'A positive FAIR test (Flexion, ADDuction, Internal Rotation reproducing deep buttock pain, sometimes with sciatic radiation) is characteristic of piriformis/deep gluteal syndrome — the piriformis muscle compresses the sciatic nerve in this position.',
    story)

mcq(6,
    'A patient describes burning and numbness over the anterolateral thigh, with no associated muscle weakness, worse after wearing a tight belt and after long periods of standing. What is the most likely diagnosis?',
    [('A','Greater trochanteric pain syndrome'),
     ('B','L4 radiculopathy'),
     ('C','Meralgia paraesthetica (lateral cutaneous nerve of thigh entrapment)'),
     ('D','Hip osteoarthritis'),
     ('E','Piriformis syndrome')],
    'C',
    'Meralgia paraesthetica is entrapment of the lateral cutaneous nerve of the thigh (a purely sensory nerve), causing burning/numbness over the anterolateral thigh WITHOUT motor weakness, classically aggravated by tight clothing/belts and prolonged standing.',
    story)

mcq(7,
    'Which of the following is NOT a recognised risk factor for greater trochanteric pain syndrome?',
    [('A','Female sex and age 40-60'),
     ('B','A tight iliotibial band'),
     ('C','Leg length discrepancy'),
     ('D','Previous hip replacement via a lateral surgical approach'),
     ('E','A single episode of ankle sprain six months ago with full recovery')],
    'E',
    'A fully-recovered, unrelated ankle sprain is not a recognised risk factor for GTPS. Female sex/age 40-60, ITB tightness, leg length discrepancy, and previous lateral-approach hip surgery are all recognised risk factors.',
    story)

mcq(8,
    'A patient with a typical history and examination consistent with GTPS asks whether they need an MRI scan before starting treatment. What is the most appropriate response?',
    [('A','MRI is mandatory before any treatment can be started'),
     ('B','GTPS is primarily a clinical diagnosis; imaging is reserved for atypical presentations, red flags, or failure to improve with first-line treatment'),
     ('C','An X-ray is more useful than clinical examination for diagnosing GTPS'),
     ('D','Ultrasound is required to confirm bursal inflammation before any advice can be given'),
     ('E','No imaging is ever appropriate, even if symptoms fail to improve')],
    'B',
    'GTPS is diagnosed clinically from the history and examination. Imaging (ultrasound/MRI) is reserved for cases that are atypical, raise red flags, or fail to respond to first-line conservative treatment — where a tendon tear or other structural pathology needs to be excluded.',
    story)

divider(story)

# §7 Answer Key
story.append(PageBreak())
sec_header('Section 7: Answer Key — Self-Test Solutions and Explanations', story)
info_box('<b>Now check your work.</b> Go back through Section 6 question by question, compare your written answer with the correct answer below, and read the explanation — especially for any question you got wrong.', story)
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
    [Paragraph('MASTER MEMORY SUMMARY — LATERAL HIP PAIN / GTPS', sGrnB)],
    [Paragraph('THE PATTERN: lateral hip pain, worse lying on the affected side at night, worse with prolonged sitting, "start-up" limp that eases with movement, NOT limiting running = GREATER TROCHANTERIC PAIN SYNDROME (gluteal tendinopathy +/- bursitis) until proven otherwise.', sGrn)],
    [Paragraph('ANATOMY: gluteus medius/minimus tendons insert onto the greater trochanter ("rotator cuff of the hip"); the trochanteric bursa and iliotibial band sit over them. Compression (side-lying, crossed-leg sitting) reproduces the pain.', sGrn)],
    [Paragraph('DIFFERENTIALS: Hip OA = groin pain, >30 min morning stiffness, worsens with activity, reduced internal rotation. Lumbar referred pain = back pain +/- neuro signs, positive SLR. Piriformis/deep gluteal syndrome = deep central buttock pain, positive FAIR test. Meralgia paraesthetica = anterolateral thigh sensory change only, no weakness.', sGrn)],
    [Paragraph('RED FLAGS: weight loss, constant non-positional night pain, fever, cancer history, trauma, new neurological deficit -> investigate further, do not assume GTPS.', sGrn)],
    [Paragraph('INVESTIGATIONS: GTPS is a CLINICAL diagnosis. X-ray if OA/fracture needs excluding. USS/MRI only if atypical, red flags, or failed first-line treatment (look for tendon tear).', sGrn)],
    [Paragraph('MANAGEMENT — "PILLOW, POSITION, PHYSIO": avoid compressive positions (pillow between knees, avoid crossed-leg sitting), simple analgesia as needed, and a progressive gluteal-strengthening physiotherapy programme (BEST long-term evidence). Corticosteroid injection = short-term bridge only; avoid repeated injections. Stay generally active — do not stop exercise.', sGrn)],
]
innerG = Table(gRows, colWidths=[CW-4])
innerG.setStyle(gTS1)
outerG = Table([[innerG]], colWidths=[CW])
outerG.setStyle(gTSO)
story.append(outerG)
story.append(Spacer(1, 14))

# Footer note
story.append(HRFlowable(width=CW, thickness=1.5, color=HexColor('#0d5c63'), spaceAfter=6))
story.append(Paragraph('Brief MRCP/PACES Note: Lateral Hip Pain — Greater Trochanteric Pain Syndrome and Differentials  |  Sections 1-7, with Interactive Q&A and Self-Test', ParagraphStyle('FT', fontName='DV-I', fontSize=8, leading=11, textColor=HexColor('#555555'), alignment=1)))

# Build document
doc.build(story)
print('SUCCESS:', OUT)
