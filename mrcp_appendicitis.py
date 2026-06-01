#!/usr/bin/env python3
"""MRCP — Acute Appendicitis Comprehensive Revision Note"""

import io
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image as RLImage)
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

# ── PAGE SETUP ────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
MARGIN = 18 * mm
CW = PAGE_W - 2 * MARGIN
OUT = '/mnt/user-data/outputs/Appendicitis_MRCP_Note.pdf'
doc = SimpleDocTemplate(OUT, pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=MARGIN,  bottomMargin=MARGIN)

# ── STYLES ────────────────────────────────────────────────────────────────────
sTitle = ParagraphStyle('TT', fontName='DV-B', fontSize=22, leading=28,
    textColor=TEAL, spaceAfter=6, alignment=1)
sSub   = ParagraphStyle('TS', fontName='DV-I', fontSize=10, leading=14,
    textColor=TEAL_M, spaceAfter=4, alignment=1)
sH1    = ParagraphStyle('H1', fontName='DV-B', fontSize=13, leading=17,
    textColor=TEAL, spaceAfter=4)
sH2    = ParagraphStyle('H2', fontName='DV-B', fontSize=10, leading=14,
    textColor=TEAL_M, spaceAfter=3)
sBody  = ParagraphStyle('Bo', fontName='DV', fontSize=9, leading=14,
    textColor=NAVY, spaceAfter=3)
sPro   = ParagraphStyle('Pr', fontName='DV-I', fontSize=9, leading=14,
    textColor=HexColor('#2c3e50'), spaceAfter=3, leftIndent=12)
sImg   = ParagraphStyle('Im', fontName='DV-I', fontSize=8, leading=12,
    textColor=BLUE_D, spaceAfter=2)
sAlert = ParagraphStyle('Al', fontName='DV-B', fontSize=9, leading=13,
    textColor=RED_D, spaceAfter=3)

story = []

# ── HELPER FUNCTIONS ──────────────────────────────────────────────────────────
def bp(text, st=None):
    return Paragraph(text, st or sBody)

def sec_header(text, story):
    story.append(Spacer(1, 6))
    story.append(Paragraph(text, sH1))
    story.append(Spacer(1, 3))

def divider(story):
    story.append(Spacer(1, 4))
    t = Table([['']], colWidths=[CW])
    t.setStyle(TableStyle([('LINEABOVE',(0,0),(0,0),1,TEAL_M),
        ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
    story.append(t)
    story.append(Spacer(1, 4))

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
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,4))

def info_box(text, story, color=None, border=None):
    bg  = color  or AMBER
    brd = border or AMBER_B
    t = Table([[Paragraph(text, sBody)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),bg),
        ('BOX',(0,0),(-1,-1),1.5,brd),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,4))

def image_search_box(term, site, story):
    txt = f'IMAGE: Search <b>"{term}"</b> on <b>{site}</b> to see a picture of this.'
    t = Table([[Paragraph(txt, sImg)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),BLUE_L),
        ('BOX',(0,0),(-1,-1),1,BLUE_D),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,4))

def professor_says(text, story):
    t = Table([[Paragraph(f'<i>Professor: {text}</i>', sPro)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),TEAL_XL),
        ('BOX',(0,0),(-1,-1),1,TEAL_M),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,4))

def memory_hook(text, story):
    sM = ParagraphStyle('MH', fontName='DV-B', fontSize=8.5, leading=13,
        textColor=HexColor('#7b3f00'), spaceAfter=0)
    t = Table([[Paragraph(f'MEMORY: {text}', sM)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),AMBER),
        ('BOX',(0,0),(-1,-1),1.5,AMBER_B),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,4))

# ── PIL HELPERS ───────────────────────────────────────────────────────────────
_FP  = _FD + 'DejaVuSans.ttf'
_FBP = _FD + 'DejaVuSans-Bold.ttf'

def _fnt(path, sz):
    try: return ImageFont.truetype(path, sz)
    except: return ImageFont.load_default()

def wt(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ''
    for w in words:
        test = (cur + ' ' + w).strip()
        try: tw = draw.textlength(test, font=font)
        except: tw = len(test) * 7
        if tw <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines or [text]

def draw_box(draw, x, y, w, fill, border, lines, font, txt_color, pad=8):
    lh = (font.size if hasattr(font,'size') else 14) + 4
    h  = lh * len(lines) + pad * 2
    draw.rectangle([x, y, x+w, y+h], fill=fill, outline=border, width=2)
    ty = y + pad
    for ln in lines:
        try: tw = draw.textlength(ln, font=font)
        except: tw = len(ln)*7
        draw.text((x + (w-tw)//2, ty), ln, font=font, fill=txt_color)
        ty += lh
    return h

def arr_d(draw, x, y, ln=20, sz=12, fill='#555555'):
    draw.line([(x, y-ln),(x, y-sz)], fill=fill, width=2)
    draw.polygon([(x,y),(x-sz//2,y-sz),(x+sz//2,y-sz)], fill=fill)

def arr_r(draw, x, y, ln=20, sz=12, fill='#555555'):
    draw.line([(x-ln,y),(x-sz,y)], fill=fill, width=2)
    draw.polygon([(x,y),(x-sz,y-sz//2),(x-sz,y+sz//2)], fill=fill)

def i2r(img, max_w=None):
    buf = io.BytesIO(); img.save(buf,'PNG'); buf.seek(0)
    mw = max_w or CW; iw, ih = img.size; sc = float(mw)/iw
    return RLImage(buf, width=iw*sc, height=ih*sc)

# ── PIL DIAGRAM 1: APPENDIX ANATOMY ──────────────────────────────────────────
def make_appendix_anatomy():
    W, H = 900, 620
    img = Image.new('RGB',(W,H),'#ffffff')
    d   = ImageDraw.Draw(img)
    fS  = _fnt(_FP,  12)
    fM  = _fnt(_FP,  14)
    fB  = _fnt(_FBP, 16)
    fT  = _fnt(_FBP, 18)

    # Title
    title = 'APPENDIX ANATOMY — Where Is It and What Surrounds It?'
    try: tw = d.textlength(title, font=fT)
    except: tw = len(title)*11
    d.text(((W-tw)//2, 8), title, font=fT, fill='#0d5c63')

    # Draw simple body outline (abdomen as rectangle)
    bx, by, bw, bh = 150, 45, 380, 450
    d.rectangle([bx,by,bx+bw,by+bh], outline='#aaaaaa', width=2)

    # Label four quadrants
    qc = bx + bw//2; qr = by + bh//2
    d.line([(qc,by),(qc,by+bh)], fill='#dddddd', width=1)
    d.line([(bx,qr),(bx+bw,qr)], fill='#dddddd', width=1)
    d.text((bx+10, by+10), 'RUQ', font=fS, fill='#aaaaaa')
    d.text((qc+10, by+10), 'LUQ', font=fS, fill='#aaaaaa')
    d.text((bx+10, qr+10), 'RIF', font=fB, fill='#c0392b')
    d.text((qc+10, qr+10), 'LIF', font=fS, fill='#aaaaaa')

    # Umbilicus (navel)
    ux, uy = qc, qr
    d.ellipse([ux-10,uy-10,ux+10,uy+10], fill='#f0e0d0', outline='#999999', width=2)
    d.text((ux-28, uy-26), 'Umbilicus', font=fS, fill='#555555')
    d.text((ux-18, uy-12), '(navel)', font=fS, fill='#555555')

    # Caecum (first part of large bowel, bottom right)
    cec_x, cec_y = bx+50, by+bh-100
    d.ellipse([cec_x,cec_y,cec_x+70,cec_y+70], fill='#fef3e2', outline='#d4640a', width=2)
    d.text((cec_x-10, cec_y-18), 'Caecum', font=fM, fill='#d4640a')
    d.text((cec_x, cec_y-4), '(start of', font=fS, fill='#555555')
    d.text((cec_x, cec_y+12), 'large bowel)', font=fS, fill='#555555')

    # Appendix hanging from caecum
    ap_x, ap_y = cec_x+35, cec_y+70
    d.rectangle([ap_x-8, ap_y, ap_x+8, ap_y+80], fill='#fde8e8', outline='#c0392b', width=2)
    d.ellipse([ap_x-8,ap_y+78,ap_x+8,ap_y+96], fill='#fde8e8', outline='#c0392b', width=2)
    d.text((ap_x+15, ap_y+20), 'APPENDIX', font=fB, fill='#c0392b')
    d.text((ap_x+15, ap_y+38), '(finger-shaped', font=fS, fill='#c0392b')
    d.text((ap_x+15, ap_y+54), 'pouch, ~9 cm)', font=fS, fill='#c0392b')

    # McBurney's point
    # ASIS location
    asis_x, asis_y = bx+20, by+bh-30
    d.ellipse([asis_x-6,asis_y-6,asis_x+6,asis_y+6], fill='#2471a3', outline='#2471a3')
    d.text((bx-120, asis_y-8), 'ASIS (hip bone', font=fS, fill='#2471a3')
    d.text((bx-120, asis_y+8), 'front bump)', font=fS, fill='#2471a3')
    d.line([(bx-10, asis_y),(asis_x-6, asis_y)], fill='#2471a3', width=1)

    # McBurney's point = 1/3 from ASIS to umbilicus
    mb_x = asis_x + (ux - asis_x)//3
    mb_y = asis_y + (uy - asis_y)//3
    d.ellipse([mb_x-8,mb_y-8,mb_x+8,mb_y+8], fill='#c0392b', outline='#c0392b')
    d.text((mb_x+12, mb_y-20), "McBurney's Point", font=fB, fill='#c0392b')
    d.text((mb_x+12, mb_y-4),  '1/3 from ASIS', font=fS, fill='#c0392b')
    d.text((mb_x+12, mb_y+12), 'to umbilicus', font=fS, fill='#c0392b')
    d.line([(asis_x, asis_y),(ux, uy)], fill='#2471a3', width=1, )
    d.ellipse([mb_x-4,mb_y-4,mb_x+4,mb_y+4], fill='#ffffff')

    # Right side: Appendix positions
    rx = bx + bw + 30
    ry = by
    d.text((rx, ry), 'APPENDIX POSITIONS', font=fB, fill='#0d5c63')
    d.text((rx, ry+20), '(varies in every person)', font=fS, fill='#555555')

    pos_data = [
        ('Retrocaecal', '65-70%', 'Behind the caecum.', '#d4edda', '#28a745'),
        ('Pelvic', '25-30%', 'Hangs into pelvis.', '#e8f4fd', '#2471a3'),
        ('Pre-ileal', '1%', 'In front of small bowel.', '#fff3cd', '#e6a817'),
        ('Subcaecal', '2%', 'Below caecum.', '#fde8e8', '#c0392b'),
        ('Paracolic', '1%', 'Beside colon.', '#f5eef8', '#7d3c98'),
    ]
    py = ry + 50
    for name, pct, desc, fc, bc in pos_data:
        ph = draw_box(d, rx, py, 300, fc, bc,
            [f'{name}  ({pct})', desc], fS, '#1a1a2e', pad=5)
        py += ph + 6

    # Blood supply label
    bs_y = by + bh + 10
    draw_box(d, bx, bs_y, bw, '#e0f4f5', '#0d5c63',
        ['Blood supply: Appendicular artery (from ileocolic branch of the superior mesenteric artery)'],
        fS, '#0d5c63', pad=6)

    final_h = bs_y + 60
    img = img.crop((0,0,W,min(final_h,H)))
    return i2r(img)

# ── PIL DIAGRAM 2: APPENDICITIS STAGES ───────────────────────────────────────
def make_appendicitis_stages():
    W, H = 900, 480
    img = Image.new('RGB',(W,H),'#ffffff')
    d   = ImageDraw.Draw(img)
    fS  = _fnt(_FP,  12)
    fM  = _fnt(_FP,  14)
    fB  = _fnt(_FBP, 15)
    fT  = _fnt(_FBP, 18)

    title = 'HOW APPENDICITIS DEVELOPS — 4 Stages'
    try: tw = d.textlength(title, font=fT)
    except: tw = len(title)*11
    d.text(((W-tw)//2, 8), title, font=fT, fill='#0d5c63')

    stages = [
        ('STAGE 1', 'BLOCKAGE', ['The opening of the appendix', 'gets blocked.', 'Usually by a hard lump', 'of old stool (faecolith),', 'or swollen lymph nodes.', 'Bacteria build up inside.'],
         '#e8f4fd', '#2471a3'),
        ('STAGE 2', 'INFLAMMATION', ['Bacteria grow and multiply.', 'The appendix wall swells.', 'Blood supply is reduced.', 'The wall becomes red,', 'hot and painful.', 'WBC count rises in blood.'],
         '#fff3cd', '#e6a817'),
        ('STAGE 3', 'GANGRENE', ['Blood flow stops completely.', 'The wall starts to die.', 'The appendix turns black.', 'It is very fragile now.', 'Any movement can burst it.', 'Patient is very unwell.'],
         '#fde8e8', '#c0392b'),
        ('STAGE 4', 'PERFORATION', ['The dead wall bursts open.', 'Pus and stool spill out.', 'This causes PERITONITIS', '(infection of the whole', 'abdominal cavity).', 'Life-threatening emergency.'],
         '#fce4ec', '#c62828'),
    ]

    bw = 195
    for i, (stg, name, lines, fc, bc) in enumerate(stages):
        bx = 20 + i * (bw + 18)
        # Stage number
        draw_box(d, bx, 42, bw, bc, bc, [stg], fB, '#ffffff', pad=6)
        # Name
        draw_box(d, bx, 42+36, bw, fc, bc, [name], fB, '#1a1a2e', pad=6)
        # Content lines
        draw_box(d, bx, 42+72, bw, '#ffffff', bc, lines, fS, '#1a1a2e', pad=6)
        # Arrow between boxes
        if i < 3:
            ax = bx + bw + 6
            arr_r(d, ax+12, 180, 8, 10, '#555555')

    # Time line at bottom
    tl_y = 390
    draw_box(d, 20, tl_y, 860, '#f0fafb', '#1a8a94',
        ['TIME: Stage 1 and 2 can take hours to days. Stage 3 and 4 happen faster.',
         'CHILDREN and ELDERLY go to Stage 4 faster because they cannot fight the infection as well.',
         'Every hour of delay after 36 hours increases perforation risk by about 1%.'],
        fS, '#0d5c63', pad=8)

    final_h = tl_y + 100
    img = img.crop((0,0,W,min(final_h,H)))
    return i2r(img)

# ── PIL DIAGRAM 3: PAIN MIGRATION + SIGNS MAP ─────────────────────────────────
def make_pain_map():
    W, H = 900, 560
    img = Image.new('RGB',(W,H),'#ffffff')
    d   = ImageDraw.Draw(img)
    fS  = _fnt(_FP,  12)
    fM  = _fnt(_FP,  14)
    fB  = _fnt(_FBP, 15)
    fT  = _fnt(_FBP, 18)

    title = 'PAIN MIGRATION IN APPENDICITIS — Where Pain Starts and Where It Moves'
    try: tw = d.textlength(title, font=fT)
    except: tw = len(title)*11
    d.text(((W-tw)//2, 8), title, font=fT, fill='#0d5c63')

    # Left: abdomen diagram showing pain migration
    bx, by, bw, bh = 30, 42, 340, 370
    d.rectangle([bx,by,bx+bw,by+bh], outline='#cccccc', width=2)
    qcx = bx + bw//2; qcy = by + bh//2
    d.line([(qcx,by),(qcx,by+bh)], fill='#eeeeee', width=1)
    d.line([(bx,qcy),(bx+bw,qcy)], fill='#eeeeee', width=1)

    # Step 1: Central/periumbilical pain
    ux, uy = qcx, qcy
    d.ellipse([ux-30,uy-30,ux+30,uy+30], fill='#fff3cd', outline='#e6a817', width=2)
    d.text((ux-26, uy-10), 'STEP 1', font=fS, fill='#7b3f00')
    d.text((ux-18, uy+4),  'Start', font=fS, fill='#7b3f00')

    # Arrow going to RIF
    arr_x = bx + 80; arr_y = by + bh - 80
    d.line([(ux, uy+30),(arr_x+20, arr_y-20)], fill='#c0392b', width=2)
    d.polygon([(arr_x+20,arr_y-20),(arr_x+10,arr_y-30),(arr_x+30,arr_y-30)], fill='#c0392b')

    # Step 2: RIF pain
    d.ellipse([arr_x-35,arr_y-35,arr_x+35,arr_y+35], fill='#fde8e8', outline='#c0392b', width=3)
    d.text((arr_x-26, arr_y-14), 'STEP 2', font=fS, fill='#c0392b')
    d.text((arr_x-12, arr_y+2),  'RIF', font=fB, fill='#c0392b')

    # Labels
    d.text((bx+5, by+5), 'RUQ', font=fS, fill='#aaaaaa')
    d.text((qcx+5, by+5), 'LUQ', font=fS, fill='#aaaaaa')
    d.text((bx+5, qcy+5), 'RIF', font=fB, fill='#c0392b')
    d.text((qcx+5, qcy+5), 'LIF', font=fS, fill='#aaaaaa')

    # McBurney's point dot
    mb_x = bx + 75; mb_y = by + bh - 60
    d.ellipse([mb_x-6,mb_y-6,mb_x+6,mb_y+6], fill='#c0392b')
    d.text((mb_x+10, mb_y-8), "McBurney's", font=fS, fill='#c0392b')
    d.text((mb_x+10, mb_y+6), 'Point', font=fS, fill='#c0392b')

    # Right side: explanation of migration
    rx = bx + bw + 30
    draw_box(d, rx, 42, 480, '#fff3cd', '#e6a817',
        ['WHY does the pain start in the centre and move to the right?'], fB, '#7b3f00', pad=8)

    ey = 100
    steps = [
        ('STEP 1 — Centre pain (first 6-12 hours)',
         ['The appendix is an organ with nerve fibres deep inside.',
          'When it first gets blocked and swollen,',
          'the pain signal cannot be located exactly.',
          'The brain feels it as a dull ache around the navel (belly button).',
          'This is called VISCERAL PAIN (pain from inside an organ).'],
         '#fff3cd', '#e6a817'),
        ('STEP 2 — Right lower pain (after 6-12 hours)',
         ['As the appendix wall gets more inflamed,',
          'it starts to irritate the sheet of tissue',
          'lining the inside of the abdomen.',
          'This sheet is called the PERITONEUM.',
          'The peritoneum has very precise nerve supply.',
          'Now the brain can locate the pain exactly',
          'in the Right Iliac Fossa (RIF) — right lower abdomen.',
          'This is called SOMATIC PAIN (sharp, well-located pain).'],
         '#fde8e8', '#c0392b'),
    ]
    for title_s, lines, fc, bc in steps:
        sh = draw_box(d, rx, ey, 480, fc, bc, [title_s]+lines, fS, '#1a1a2e', pad=6)
        ey += sh + 8

    # Key sign box
    ey += 4
    draw_box(d, rx, ey, 480, '#e0f4f5', '#0d5c63',
        ['KEY SIGN: PAIN on MOVEMENT.',
         'Any movement of the peritoneum (the lining sheet) causes pain.',
         'Patient lies still, knees pulled up, breathes shallow.',
         'Coughing or deep breathing makes pain worse.',
         'This is called PERITONISM.'],
        fS, '#0d5c63', pad=6)

    final_h = max(by+bh+20, ey+100)
    img = img.crop((0,0,W,min(final_h,H)))
    return i2r(img)

# ── PIL DIAGRAM 4: ALVARADO SCORE ────────────────────────────────────────────
def make_alvarado():
    W, H = 900, 520
    img = Image.new('RGB',(W,H),'#ffffff')
    d   = ImageDraw.Draw(img)
    fS  = _fnt(_FP,  12)
    fM  = _fnt(_FP,  14)
    fB  = _fnt(_FBP, 15)
    fT  = _fnt(_FBP, 18)

    title = 'ALVARADO SCORE — How Likely Is Appendicitis? (MANTRELS)'
    try: tw = d.textlength(title, font=fT)
    except: tw = len(title)*11
    d.text(((W-tw)//2, 8), title, font=fT, fill='#0d5c63')

    # Left side: scoring table
    rows_data = [
        ('M', 'Migration of pain to RIF (right lower area)', '1 point', '#e8f4fd', '#2471a3'),
        ('A', 'Anorexia (not wanting to eat)', '1 point', '#d4edda', '#28a745'),
        ('N', 'Nausea or vomiting', '1 point', '#f5eef8', '#7d3c98'),
        ('T', 'Tenderness (pain when pressing) in RIF', '2 points', '#fde8e8', '#c0392b'),
        ('R', 'Rebound tenderness in RIF', '1 point', '#fde8e8', '#c0392b'),
        ('E', 'Elevated temperature (above 37.3 C)', '1 point', '#fef3e2', '#d4640a'),
        ('L', 'Leucocytosis (raised white blood cells)', '2 points', '#fff3cd', '#e6a817'),
        ('S', 'Shift to left (more young white cells in blood)', '1 point', '#fff3cd', '#e6a817'),
    ]

    lx = 20; ly = 48; lw1=35; lw2=330; lw3=80
    # Header
    draw_box(d, lx, ly, lw1+lw2+lw3+8, '#e0f4f5', '#0d5c63',
        ['MANTRELS Scoring — Total = 10 points'], fB, '#0d5c63', pad=6)
    ly += 44

    for letter, desc, pts, fc, bc in rows_data:
        ph = draw_box(d, lx, ly, lw1, fc, bc, [letter], fB, '#1a1a2e', pad=6)
        draw_box(d, lx+lw1+2, ly, lw2, fc, '#cccccc', [desc], fS, '#1a1a2e', pad=6)
        draw_box(d, lx+lw1+lw2+4, ly, lw3, fc, bc, [pts], fB, bc, pad=6)
        ly += ph + 4

    # Total
    draw_box(d, lx, ly+4, lw1+lw2+lw3+8, '#e0f4f5', '#0d5c63',
        ['TOTAL SCORE: Maximum = 10 points'], fB, '#0d5c63', pad=6)

    # Right side: Score interpretation
    rx = lx + lw1 + lw2 + lw3 + 30
    draw_box(d, rx, 48, 400, '#e0f4f5', '#0d5c63',
        ['WHAT THE SCORE MEANS'], fB, '#0d5c63', pad=8)

    scores = [
        ('1 - 4', 'Appendicitis UNLIKELY', 'Send home. Watch and come back if worse.', '#d4edda', '#28a745'),
        ('5 - 6', 'POSSIBLE appendicitis', 'Keep in hospital. Observe. Repeat tests.', '#fff3cd', '#e6a817'),
        ('7 - 8', 'PROBABLE appendicitis', 'Plan surgery. Arrange theatre.', '#fde8e8', '#c0392b'),
        ('9 - 10', 'ALMOST CERTAIN appendicitis', 'Take to theatre now. Do not delay.', '#fce4ec', '#c62828'),
    ]
    sy = 110
    for sc, label, action, fc, bc in scores:
        sh = draw_box(d, rx, sy, 400, fc, bc,
            [f'Score {sc}:', label, action], fM, '#1a1a2e', pad=7)
        sy += sh + 6

    sy += 8
    draw_box(d, rx, sy, 400, '#fff3cd', '#e6a817',
        ['NOTE: Score is a guide only.',
         'A score of 5-6 with high clinical suspicion',
         'should still lead to imaging or surgery.',
         'Women of childbearing age: always check',
         'pregnancy test first (ectopic can mimic).'],
        fS, '#7b3f00', pad=6)

    final_h = max(ly+80, sy+100)
    img = img.crop((0,0,W,min(final_h,H)))
    return i2r(img)

# ── BUILD DIAGRAMS ─────────────────────────────────────────────────────────────
print('Building PIL diagrams...')
anat_img   = make_appendix_anatomy()
stage_img  = make_appendicitis_stages()
pain_img   = make_pain_map()
alv_img    = make_alvarado()
print('PIL diagrams done.')

# ═══════════════════════════════════════════════════════════════════════════════
# STORY
# ═══════════════════════════════════════════════════════════════════════════════
story.append(Spacer(1,8))
story.append(Paragraph('ACUTE APPENDICITIS', sTitle))
story.append(Paragraph('Comprehensive MRCP Revision Note | Parts 1, 2 &amp; PACES', sSub))
story.append(Paragraph('From First Principles to Examination Mastery — Very Simple Language', sSub))
story.append(Spacer(1,6))
tags=[['Topic','System','Key surgery','Common age'],
    ['Acute Appendicitis','Surgical emergency — Gastrointestinal','Laparoscopic appendicectomy','10-30 years (but any age)']]
story.append(plain_table(tags,[CW*0.25,CW*0.30,CW*0.25,CW*0.20]))
story.append(Spacer(1,6))
divider(story)

# ── SECTION 1: OVERVIEW ────────────────────────────────────────────────────────
sec_header('Section 1: Overview — What Is Acute Appendicitis?', story)
professor_says('Think of the appendix like a small finger attached to the start of the large intestine. Most of the time it does nothing and causes no trouble. But sometimes its opening gets blocked. Then bacteria grow inside it. It swells up. It gets infected. If not treated quickly, it bursts. A burst appendix is a life-threatening emergency. This whole process is called acute appendicitis.', story)

story.append(bp('The <b>appendix</b> (say it: ah-PEN-dix) is a small, tube-shaped pouch. '
    'It hangs from the start of the large intestine. '
    'It is in the <b>right lower part of the abdomen (belly)</b>. '
    'The medical name for this area is the <b>Right Iliac Fossa</b> — or RIF for short.'))
story.append(Spacer(1,4))
story.append(bp('<b>Acute appendicitis</b> (say it: ah-PEN-dih-sy-tis) means the appendix is inflamed. '
    '"Inflamed" means swollen, red, hot, and painful — like an infected wound. '
    '"Acute" means it has come on suddenly and is getting worse quickly.'))
story.append(Spacer(1,4))

key_facts = [
    ['Fact', 'Detail'],
    ['How common?',
     'Very common. About 1 in 13 people get appendicitis in their lifetime. '
     'It is the most common reason for emergency abdominal surgery in the world.'],
    ['Who gets it?',
     'Most common in people aged 10 to 30 years. '
     'But it can happen at any age — from babies to very old people. '
     'Slightly more common in males than females.'],
    ['How serious is it?',
     'It can kill if not treated. '
     'The main danger is the appendix bursting (perforating). '
     'When it bursts, infection spreads inside the whole abdomen. '
     'This is called peritonitis (per-ee-toh-NY-tis) — infection of the belly lining. '
     'Peritonitis can kill within hours.'],
    ['How is it treated?',
     'Surgery to remove the appendix. This operation is called appendicectomy '
     '(ah-pen-dih-SEK-toh-me). '
     'Most operations are done by keyhole surgery (laparoscopic — using small cuts and a camera). '
     'In some patients with early, uncomplicated infection: antibiotics alone can work.'],
    ['Lifetime risk without treatment?',
     'Without treatment, most cases of appendicitis progress to perforation within 36-72 hours. '
     'Each hour after 36 hours increases the risk of perforation by about 1%.'],
]
story.append(plain_table(key_facts, [CW*0.20, CW*0.80]))
divider(story)

# ── SECTION 2: ANATOMY ─────────────────────────────────────────────────────────
sec_header('Section 2: Anatomy — Where Is the Appendix and What Is Around It?', story)
professor_says('Before you can examine a patient or understand the pain, you need to know exactly where the appendix lives. Its neighbours — the small bowel, the large bowel, the right ureter, the ovary in women, the psoas muscle — are all important. Because when the appendix is inflamed, it irritates these neighbours too. And that causes some of the special signs we look for.', story)

story.append(anat_img)
story.append(Spacer(1,4))
story.append(bp('<i>Figure 1: Where the appendix sits in the abdomen. '
    'The red dot is McBurney\'s point — the spot on the skin directly over the appendix. '
    'The table on the right shows how the appendix position varies between people.</i>', sImg))

story.append(Spacer(1,6))
anatomy_table = [
    ['Structure', 'Plain English explanation', 'Why it matters in appendicitis'],
    ['Caecum\n(SEE-kum)',
     'The first part of the large intestine (large bowel). It is a pouch-like section at the bottom right of the abdomen. The appendix hangs from the bottom of the caecum.',
     'The appendix is attached to the caecum. When you feel for the appendix, you are looking for the caecum area first.'],
    ['McBurney\'s Point',
     'A specific point on the skin of the right lower abdomen. Found by measuring 1/3 of the way from the ASIS (the bony bump at the front of the right hip) to the navel (belly button). This is where most appendixes sit on the surface.',
     'Maximum tenderness (worst pain on pressing) at McBurney\'s point is a classic sign of appendicitis. Every doctor must know how to find this point.'],
    ['Ileum\n(ILL-ee-um)',
     'The last part of the small intestine. It connects to the caecum just beside the appendix.',
     'Inflammation of the ileum (ileitis) can look exactly like appendicitis. Crohn\'s disease (an inflammatory bowel disease) affects the ileum and is a common cause of confusion.'],
    ['Right ureter\n(YOO-reh-ter)',
     'The tube that carries urine from the right kidney down to the bladder. It passes close to the appendix.',
     'When the appendix is inflamed, it can irritate the ureter nearby. This causes white blood cells to appear in the urine — which can make you think the patient has a urine infection. Always check urine, but do not be misled.'],
    ['Right ovary\n(in women)',
     'The right ovary and fallopian tube are very close to the appendix in women.',
     'Ovary problems — ovarian cyst twisting (torsion), ruptured cyst, or ectopic pregnancy — can feel exactly like appendicitis. This is why appendicitis is harder to diagnose in women. Always do a pregnancy test in women of childbearing age.'],
    ['Psoas muscle\n(SO-az)',
     'A large muscle that runs along the inside of the lower back and connects to the hip. The appendix can rest on this muscle when it is in the retrocaecal position (behind the caecum).',
     'When the inflamed appendix touches the psoas muscle, moving the right hip causes pain. This is called the PSOAS SIGN (so-az sign). It suggests a retrocaecal appendix.'],
    ['Obturator muscle\n(OB-choo-ray-ter)',
     'A small muscle inside the pelvis. In pelvic appendix position, the appendix lies near this muscle.',
     'When the inflamed appendix touches the obturator muscle, rotating the right knee inward causes pain. This is called the OBTURATOR SIGN. It suggests a pelvic appendix.'],
    ['Peritoneum\n(peh-rit-oh-NEE-um)',
     'The thin sheet of tissue that lines the inside of the whole abdomen and covers the organs. It is like a plastic bag wrapping the inside of the belly.',
     'When the inflamed appendix touches this sheet, the sheet gets irritated too. Touching, pressing, or moving the peritoneum causes sharp pain. This is called PERITONISM or peritoneal irritation. It is a very important clinical sign.'],
]
story.append(plain_table(anatomy_table, [CW*0.14, CW*0.40, CW*0.46]))
memory_hook("McBurney's Point: Stand in front of the patient. Find the right hip bone bump (ASIS). Find the belly button. Draw an imaginary line between them. One-third of the way from the ASIS = McBurney's Point. Press firmly here. Maximum tenderness here = appendicitis.", story)
divider(story)

# ── SECTION 3: PATHOPHYSIOLOGY ─────────────────────────────────────────────────
sec_header('Section 3: Pathophysiology — How Appendicitis Develops Step by Step', story)
professor_says('The appendix is a small tube with a very narrow opening. Think of it like a thin straw. If you block the opening of the straw, and bacteria are living inside it, they have nowhere to go. They multiply, the pressure inside builds up, the walls get damaged, blood cannot flow, the tissue dies, and eventually — like a balloon that is overfilled — it bursts. Let me walk you through each step.', story)

story.append(stage_img)
story.append(Spacer(1,4))
story.append(bp('<i>Figure 2: The four stages of appendicitis — from blockage to burst. '
    'Treatment at Stage 1 or 2 has excellent outcomes. '
    'Stage 4 (perforation) has a much higher risk of death and complications.</i>', sImg))

story.append(Spacer(1,6))
path_table = [
    ['Stage', 'What is happening inside', 'Time', 'What the patient feels'],
    ['Stage 1\nBlockage\n(Obstruction)',
     'Something blocks the narrow opening (lumen) of the appendix. The most common causes:\n'
     'FAECOLITH (FAY-ko-lith): a hardened lump of old stool (poo) that got stuck in the opening. Most common cause in adults.\n'
     'LYMPHOID HYPERPLASIA (LIM-foyd): Swelling of the lymph nodes (small infection-fighting glands) inside the appendix wall. Most common cause in children — happens after a viral infection like a cold or sore throat.\n'
     'TUMOUR: Rare. A carcinoid tumour (a small slow-growing cancer) can block the opening.\n'
     'FOREIGN BODY: Rare. A seed, fruit stone, or small object.',
     '0-6 hours',
     'Early, vague pain around the navel (belly button). Mild nausea. Not wanting to eat. Patient may not be very worried yet.'],
    ['Stage 2\nInflammation\n(Appendicitis)',
     'With the opening blocked, bacteria that normally live harmlessly in the bowel start multiplying inside the appendix. Common bacteria: Escherichia coli (E. coli), Bacteroides, Enterococcus.\n'
     'As bacteria multiply, they release toxins. The body responds with inflammation (swelling, redness, heat). White blood cells rush to the area. The appendix wall swells and becomes tender.\n'
     'The raised pressure inside starts to compress small blood vessels in the wall.',
     '6-24 hours',
     'Pain moves from the centre to the RIGHT LOWER ABDOMEN (RIF). Pain is now sharp and well-located. Fever develops (usually 37.5-38.5 degrees C). Nausea or vomiting. Cannot eat. Walking hurts. Patient hunches over.'],
    ['Stage 3\nGangrene\n(Ischaemia)',
     'The blood vessels in the wall are fully compressed. Blood cannot get through. Without blood, the tissue has no oxygen. The appendix wall starts to die (gangrene means dead tissue).\n'
     'The wall turns from pink to dark green to black. It is now very fragile and thin. Any movement or pressure can crack it.',
     '24-48 hours',
     'Very unwell. High fever (above 38.5 degrees C). Severe constant RIF pain. Rigid abdomen (the muscles tighten involuntarily to protect the infected area). Patient cannot stand up straight. Looks pale and sweaty.'],
    ['Stage 4\nPerforation\n(Burst appendix)',
     'The dead wall tears open. The contents of the appendix — pus, bacteria, stool — spill into the abdomen. This causes PERITONITIS: infection of the peritoneum (the lining of the abdomen).\n'
     'The body tries to contain the infection. The omentum (a fatty apron of tissue in the abdomen) wraps around the appendix to form an APPENDIX MASS or PHLEGMON.\n'
     'If the containment fails, generalised peritonitis spreads throughout the whole abdomen. This can cause SEPSIS (serious life-threatening body-wide infection) and death.',
     'After 36-72 hours\n(sometimes earlier in\nyoung children and elderly)',
     'Sudden brief relief of pain when perforation happens (pressure released). Then pain returns MUCH WORSE and spreads across the whole abdomen. Rigid board-like abdomen. Very high fever. Patient looks very unwell — grey, sweaty, rapid heartbeat, low blood pressure. SEPTIC SHOCK if not treated urgently.'],
]
story.append(plain_table(path_table, [CW*0.10, CW*0.47, CW*0.13, CW*0.30]))
divider(story)

# ── SECTION 4: SYMPTOMS — WHAT THE PATIENT TELLS YOU ──────────────────────────
sec_header('Section 4: Symptoms — What the Patient Tells You (History)', story)
professor_says('When a patient comes to you with abdominal pain, your job is to listen carefully. In appendicitis, the history is often enough to make a strong clinical suspicion. Three features together are almost diagnostic: pain that started around the navel and moved to the right lower abdomen, loss of appetite, and a low fever. Learn to ask the right questions.', story)

story.append(pain_img)
story.append(Spacer(1,4))
story.append(bp('<i>Figure 3: The classic pain migration pattern of appendicitis. '
    'Pain starts around the navel (visceral pain — dull and central) then moves to the RIF (somatic pain — sharp and located). '
    'This migration happens in about 70% of patients.</i>', sImg))

story.append(Spacer(1,6))
story.append(bp('<b>Important questions to ask every patient with abdominal pain:</b>'))
hx_table = [
    ['Symptom', 'Typical pattern in appendicitis', 'Simple explanation', 'What it tells you'],
    ['PAIN — when did it start?',
     'Usually starts 4-12 hours before the patient comes to hospital.',
     'The pain has not been there for days. It came on in the last few hours.',
     'Sudden onset pain is more worrying than chronic pain.'],
    ['PAIN — where did it start?',
     'Starts around the NAVEL (belly button) or in the centre of the abdomen.',
     'The first pain is vague and hard to locate. Like a dull stomach ache.',
     'This is called visceral pain (pain from inside an organ). The brain cannot tell exactly where it is coming from.'],
    ['PAIN — where is it now?',
     'Moves to the RIGHT LOWER ABDOMEN (RIF, McBurney\'s point) within 6-12 hours.',
     'The pain sharpens and moves to the right lower belly.',
     'This migration (moving of pain) is the most classic symptom of appendicitis. Present in 70% of cases.'],
    ['PAIN — type and severity?',
     'First: dull, colicky (comes and goes in waves). Then: constant, sharp, stabbing in RIF.',
     'Early: it comes and goes. Later: it is there all the time and getting worse.',
     'Constant worsening pain = the inflammation is spreading.'],
    ['PAIN — does movement make it worse?',
     'YES. Moving, coughing, deep breathing, bumps in the car, walking — all make the pain worse.',
     'The patient walks carefully and slowly. Lying still helps.',
     'Pain on movement = the peritoneum (belly lining) is irritated = peritonism.'],
    ['ANOREXIA\n(AN-oh-REK-see-ah = not wanting to eat)',
     'Present in more than 90% of cases.',
     'The patient says: I have no appetite. I do not want to eat. Even looking at food makes me feel sick.',
     'Very useful symptom. If a patient has abdominal pain AND is hungry — appendicitis is less likely.'],
    ['NAUSEA and VOMITING',
     'Nausea (feeling sick) is common. Vomiting (being sick) happens in about 70% of cases.',
     'Important: vomiting usually starts AFTER the pain. If vomiting started before pain — think of other causes (gastroenteritis, bowel obstruction).',
     'Vomiting AFTER pain = appendicitis more likely. Vomiting BEFORE pain = think of other causes.'],
    ['FEVER\n(high body temperature)',
     'Low grade at first: 37.5 to 38.5 degrees C. Higher (above 38.5) suggests perforation or abscess.',
     'A mild temperature is common. A very high temperature means the infection has got worse.',
     'High fever = serious complication. Think perforation or sepsis.'],
    ['BOWEL CHANGES',
     'Usually constipation (difficulty passing stool). Diarrhoea is less common but can occur if pelvic appendix irritates the rectum.',
     'The gut slows down when there is inflammation nearby.',
     'Diarrhoea with RIF pain in a young person = also think mesenteric adenitis (swollen lymph nodes in the bowel).'],
    ['URINARY SYMPTOMS\n(pain passing urine or blood in urine)',
     'Can be present even in true appendicitis if the inflamed appendix is near the right ureter.',
     'The inflamed appendix can touch the tube that carries urine and cause irritation.',
     'Do not assume it is a urine infection. Always do a urine test AND consider appendicitis.'],
    ['LAST MENSTRUAL PERIOD\n(in women — always ask)',
     'ALWAYS ask in any woman of childbearing age.',
     'Ectopic pregnancy (a pregnancy in the fallopian tube instead of the womb) causes very similar pain and can be fatal if missed.',
     'Always do a PREGNANCY TEST (urine or blood HCG) before diagnosing appendicitis in women. No exceptions.'],
]
story.append(plain_table(hx_table, [CW*0.14, CW*0.22, CW*0.28, CW*0.36]))
memory_hook('APPENDICITIS HISTORY: Pain starts CENTRAL then MOVES to RIF. Vomiting comes AFTER pain (not before). ANOREXIA in 90% (no appetite). LOW FEVER. If a patient has RIF pain AND is hungry = think of another diagnosis. ALWAYS do a pregnancy test in women.', story)
divider(story)

# ── SECTION 5: EXAMINATION — SIGNS ────────────────────────────────────────────
sec_header('Section 5: Clinical Signs — What You Find When You Examine the Patient', story)
professor_says('This is where you become a detective. Each sign has a name, and each name tells a story. Most of these signs work because the inflamed appendix is irritating the peritoneum — the lining sheet of the abdomen. When you touch or move that sheet, it hurts. The different signs test for this in different ways.', story)

signs_table = [
    ['Sign', 'How to test it', 'Positive result', 'Why it happens', 'What it means'],
    ['TENDERNESS at McBurney\'s Point\n(most important sign)',
     'Press firmly with two fingers at McBurney\'s Point (1/3 from ASIS to navel, right side).',
     'The patient feels maximum pain exactly at this point.',
     'The appendix is directly beneath this point. Pressing here squeezes the inflamed appendix.',
     'Maximum tenderness at McBurney\'s Point = very strongly suggests appendicitis.'],
    ['GUARDING\n(involuntary rigidity)',
     'Place your warm hand flat on the right lower abdomen and press slowly.',
     'The muscles under your hand tighten on their own. You cannot press through them. This is not the patient tensing on purpose — it happens automatically.',
     'The body protects itself. The muscles contract to protect the inflamed peritoneum beneath.',
     'Guarding = peritonism = serious inflammation underneath. Always report whether guarding is voluntary (patient tensing on purpose) or involuntary (automatic = true peritonism).'],
    ['REBOUND TENDERNESS\n(also called Blumberg\'s sign)',
     'Press slowly and deeply into the abdomen. Then suddenly let go completely.',
     'The patient feels pain when you RELEASE your hand — not when you press.',
     'When you press, you push the inflamed peritoneum away. When you let go, it springs back and causes sudden pain.',
     'Rebound tenderness = peritoneal irritation = appendicitis or other serious cause.'],
    ['ROVSING\'S SIGN\n(ROV-sings)',
     'Press deeply on the LEFT lower abdomen (left iliac fossa = LIF).',
     'The patient feels pain in the RIGHT lower abdomen (RIF) even though you are pressing on the left.',
     'Pressing on the left side compresses the large intestine and pushes gas across to the right side. This increases pressure around the inflamed appendix on the right.',
     'Positive Rovsing\'s sign = appendicitis very likely. Classic MRCP question.'],
    ['PSOAS SIGN\n(SO-az)',
     'Patient lies flat. Lift the right leg straight up against your resistance (passive hip extension). Or ask patient to lift right leg against your hand.',
     'Pain is felt in the right lower abdomen.',
     'The psoas muscle runs beneath the appendix when it is in the retrocaecal position (behind the caecum). Moving the hip stretches this muscle and drags against the inflamed appendix.',
     'Positive psoas sign = retrocaecal appendix.'],
    ['OBTURATOR SIGN\n(OB-choo-ray-ter)',
     'Patient lies flat. Bend the right knee to 90 degrees. Rotate the lower leg inward (internal rotation of hip).',
     'Pain is felt deep in the right pelvis or lower abdomen.',
     'The obturator muscle sits inside the pelvis. When the appendix is in the pelvic position, it rests near this muscle. Rotating the hip makes the muscle move and rub against the inflamed appendix.',
     'Positive obturator sign = pelvic appendix.'],
    ['DUNPHY\'S SIGN\n(DUN-fee)',
     'Ask the patient to cough.',
     'Pain becomes sharper in the right lower abdomen.',
     'Coughing increases pressure inside the abdomen for a moment. This jolts the inflamed peritoneum.',
     'Pain on coughing = peritonism = appendicitis or other peritoneal irritation.'],
    ['HYPERAESTHESIA\n(HY-per-es-THEE-zhah)',
     'Lightly stroke or pinch the skin over the right lower abdomen.',
     'The skin is much more sensitive than the same area on the left side.',
     'Inflammation of the appendix irritates the nerve roots T10, T11, and L1 which also supply this skin area.',
     'Useful early sign. Often present before the classic pain migration.'],
    ['RIGIDITY\n(BOARD-LIKE ABDOMEN)',
     'Place your hand flat on the abdomen.',
     'The whole abdomen feels hard — like pressing on a wooden board.',
     'Generalised guarding means the whole peritoneum is inflamed (generalised peritonitis). The whole abdomen wall is in constant spasm.',
     'Board-like rigidity = PERFORATION until proven otherwise. Surgical emergency.'],
]
story.append(plain_table(signs_table, [CW*0.14, CW*0.18, CW*0.15, CW*0.25, CW*0.28]))
memory_hook("ROVSING'S SIGN: Press LEFT side, pain on RIGHT side = appendicitis. Remember it this way: Rovsing's = Reverse pressure. You press one side, patient feels pain on the other side.", story)
divider(story)

# ─────────────────────────────────────────────────────────────────────────────
# §6  SCORING SYSTEMS — ALVARADO SCORE
# ─────────────────────────────────────────────────────────────────────────────
sec_header('Section 6: Scoring Systems — The Alvarado Score', story)

story.append(bp('<b>What is a scoring system?</b>'))
story.append(bp('A scoring system is a simple tool. You add up points. The total score tells you how likely a diagnosis is. It helps doctors decide who needs surgery and who can wait and watch.'))
story.append(Spacer(1, 4))

professor_says('Think of the Alvarado Score like a checklist. Each item you tick adds a point. The higher the score, the more likely it is appendicitis. This is useful at 3am in a busy hospital with no CT scanner available.', story)

story.append(bp('<b>The MANTRELS / Alvarado Score — Full Explanation</b>'))
story.append(bp('MANTRELS is a memory word. Each letter stands for one item in the score. The maximum score is 10. Remember: <b>M-A-N-T-R-E-L-S</b>.'))
story.append(Spacer(1, 6))

img_alv = make_alvarado()
story.append(img_alv)
story.append(Spacer(1, 6))

alv_table = [
    [bp('<b>Letter</b>', sH2), bp('<b>Item</b>', sH2), bp('<b>Points</b>', sH2), bp('<b>Plain English Explanation</b>', sH2)],
    [bp('M'), bp('Migration of pain to RIF\n(Right Iliac Fossa)'), bp('1'), bp('Pain started around the navel. Now it has moved to the right lower abdomen. Classic appendicitis pattern.')],
    [bp('A'), bp('Anorexia (loss of appetite)'), bp('1'), bp('The patient does not want to eat. Even their favourite food does not interest them. This is because inflammation suppresses appetite.')],
    [bp('N'), bp('Nausea / Vomiting'), bp('1'), bp('Patient feels sick. May have vomited once or twice. The inflamed appendix triggers the vomiting centre in the brain via nerve signals.')],
    [bp('T'), bp('Tenderness in RIF'), bp('2'), bp('This is the most important sign. Worth 2 points. Pressing the right lower abdomen causes sharp pain. The appendix is inflamed and the covering (peritoneum) is sensitive.')],
    [bp('R'), bp('Rebound Tenderness in RIF'), bp('1'), bp('When you release your hand quickly after pressing, the pain becomes worse for a second. This means the peritoneum (the lining around the appendix) is irritated.')],
    [bp('E'), bp('Elevated Temperature\n(fever >37.3°C)'), bp('1'), bp('The body raises temperature to fight infection. Even a mild fever counts. A temperature above 37.3°C is significant.')],
    [bp('L'), bp('Leucocytosis\n(high white blood cell count)'), bp('2'), bp('White blood cells (the infection-fighting cells) go up in the blood. Worth 2 points. Usually WBC > 10,000. Shows the body is fighting infection.')],
    [bp('S'), bp('Shift of WBC to the left\n(Neutrophilia)'), bp('1'), bp('The young, immature white blood cells (called bands or stabs) appear in the blood. This means the body is working very hard to produce more infection fighters quickly.')],
]
story.append(plain_table(alv_table, [CW*0.06, CW*0.22, CW*0.08, CW*0.64]))
story.append(Spacer(1, 6))

story.append(bp('<b>How to interpret the score:</b>'))
score_interp = [
    [bp('<b>Score</b>', sH2), bp('<b>Interpretation</b>', sH2), bp('<b>Action</b>', sH2)],
    [bp('1 – 4'), bp('Appendicitis unlikely'), bp('Send home. Give clear instructions to return if worse. Follow up in 12–24 hours.')],
    [bp('5 – 6'), bp('Appendicitis possible'), bp('Admit to hospital. Watch and wait. Repeat examination in 4–6 hours. Repeat blood tests.')],
    [bp('7 – 8'), bp('Appendicitis probable'), bp('Strong likelihood of appendicitis. Prepare for surgery. Get imaging to confirm if possible.')],
    [bp('9 – 10'), bp('Appendicitis almost certain'), bp('Very high likelihood. Proceed to surgery with minimal delay. Do not wait for imaging if patient is deteriorating.')],
]
story.append(plain_table(score_interp, [CW*0.12, CW*0.35, CW*0.53]))
story.append(Spacer(1, 6))

info_box('<b>Other Scoring Systems:</b> The <b>Appendicitis Inflammatory Response (AIR) score</b> adds CRP (C-reactive protein) and is more sensitive. The <b>Pediatric Appendicitis Score (PAS)</b> is used for children. Both are refinements of the Alvarado concept — same idea, more data points.', story)

memory_hook('MANTRELS = Migration, Anorexia, Nausea, Tenderness (×2), Rebound, Elevated temp, Leucocytosis (×2), Shift left. Maximum 10 points. Score 7+ = probable appendicitis = prepare for operation.', story)
divider(story)

# ─────────────────────────────────────────────────────────────────────────────
# §7  INVESTIGATIONS
# ─────────────────────────────────────────────────────────────────────────────
sec_header('Section 7: Investigations — What Tests Do We Do?', story)

professor_says('In appendicitis, no single test is 100% accurate. The diagnosis is CLINICAL — meaning you use the story and examination FIRST. Tests support your clinical thinking. They do not replace it.', story)

story.append(bp('<b>Blood Tests</b>'))
blood_tests = [
    [bp('<b>Test</b>', sH2), bp('<b>What it measures</b>', sH2), bp('<b>Expected Result in Appendicitis</b>', sH2), bp('<b>Important Points</b>', sH2)],
    [bp('FBC\n(Full Blood Count)'), bp('Number of all blood cells — red cells, white cells, platelets'), bp('WBC raised (>10,000). Neutrophilia (high neutrophils — the main infection fighters). Bands (immature cells) present.'), bp('Normal WBC does NOT rule out appendicitis — especially early. Up to 30% of confirmed cases have normal WBC at first.')],
    [bp('CRP\n(C-Reactive Protein)'), bp('A protein made by the liver when there is inflammation anywhere in the body'), bp('Raised — often >10 mg/L. In perforation, often >50–100 mg/L.'), bp('CRP takes 6–12 hours to rise. Very early appendicitis may have normal CRP. Serial measurements (every 6–8 hours) are more useful than a single value.')],
    [bp('U&E\n(Urea and Electrolytes)'), bp('Kidney function + salt balance in the blood'), bp('Usually normal. Dehydration may cause raised urea.'), bp('Important before surgery — check kidney function. Also guides IV fluid replacement.')],
    [bp('LFTs\n(Liver Function Tests)'), bp('Liver enzymes and bilirubin'), bp('Usually normal in appendicitis.'), bp('Useful to exclude liver/gallbladder cause of pain (e.g. biliary colic). Raised bilirubin can occur in perforation/sepsis (portal pyaemia — rare).')],
    [bp('Serum amylase'), bp('Enzyme made by pancreas'), bp('Normal in appendicitis.'), bp('Important to exclude pancreatitis — which causes severe upper abdominal pain that can confuse the picture.')],
    [bp('Group & Save\n(G&S)'), bp('Blood group typing — cross-matching for transfusion'), bp('Routine before any operation.'), bp('Always request before surgery. If patient bleeds during operation, blood can be given quickly.')],
    [bp('Urine pregnancy test\n(Beta-hCG)'), bp('Pregnancy hormone'), bp('Negative in appendicitis.'), bp('MUST do in ALL women of reproductive age. Ectopic pregnancy (egg implanted in fallopian tube — not womb) mimics appendicitis exactly and is life-threatening.')],
]
story.append(plain_table(blood_tests, [CW*0.15, CW*0.22, CW*0.28, CW*0.35]))
story.append(Spacer(1, 8))

story.append(bp('<b>Urine Test (Urinalysis / Dipstick)</b>'))
story.append(bp('Dip a special strip into urine. The strip changes colour to show different things.'))
story.append(bp('In appendicitis: the urine test can show small amounts of blood, white cells or protein. This happens because the inflamed appendix sits near the ureter (the tube from kidney to bladder).'))
story.append(bp('<b>Important:</b> Small abnormalities in urine do NOT rule out appendicitis. Urine is checked mainly to rule out a kidney or bladder infection (UTI) causing the pain.'))
story.append(Spacer(1, 8))

story.append(bp('<b>Imaging Tests</b>'))
imaging_tests = [
    [bp('<b>Test</b>', sH2), bp('<b>What it shows</b>', sH2), bp('<b>Advantages</b>', sH2), bp('<b>Disadvantages</b>', sH2), bp('<b>MRCP Key Points</b>', sH2)],
    [bp('Ultrasound\n(USS)'), bp('Sound waves create a picture of the abdomen. Can see the appendix if it is inflamed and not hidden behind bowel gas.'), bp('Safe. No radiation. Good in pregnancy and children. Can do at bedside. Identifies ovarian causes in women.'), bp('Operator-dependent (skill matters). Cannot see the appendix in 20–30% of people — especially obese patients or when there is lots of bowel gas.'), bp('Sensitivity ~80%, Specificity ~93%. If USS shows appendix — good. If USS cannot find the appendix — this does NOT rule out appendicitis.')],
    [bp('CT Abdomen\n& Pelvis\n(with IV contrast)'), bp('X-ray beams from many angles create a detailed 3D picture. Can see the appendix, surrounding inflammation, fluid collections, perforation.'), bp('Most accurate investigation. Sensitivity ~94%, Specificity ~95%. Shows complications (abscess, perforation, peritonitis). Guides surgical planning.'), bp('Radiation dose. IV contrast can harm kidneys. Not first-line in children or pregnant women.'), bp('Gold standard imaging in adults. In perforated appendicitis: shows free air, fluid, thickened bowel wall. CT is used to confirm if diagnosis uncertain after clinical assessment.')],
    [bp('MRI Abdomen'), bp('Magnetic fields (no radiation) create detailed soft tissue images.'), bp('No radiation — safe in pregnancy. Excellent soft tissue detail. As accurate as CT in experienced hands.'), bp('Expensive. Slow — 30–40 minutes in scanner. Less available (especially nights/weekends).'), bp('Preferred investigation in PREGNANCY. Appendix moves upward as uterus grows — MRI tracks it accurately. Use if USS inconclusive.')],
    [bp('Plain X-ray\n(AXR)'), bp('Simple abdominal X-ray'), bp('Quick. Available everywhere. Cheap.'), bp('Poor sensitivity for appendicitis. Cannot see the appendix directly.'), bp('NOT useful for diagnosing appendicitis. BUT can show: free air under diaphragm (perforation), faecolith (calcified stone in appendix — rare but diagnostic), bowel obstruction pattern.')],
]
story.append(plain_table(imaging_tests, [CW*0.13, CW*0.22, CW*0.22, CW*0.2, CW*0.23]))
story.append(Spacer(1, 6))

info_box('<b>MRCP Key Point — Imaging Strategy:</b> Start with clinical assessment + bloods. Score with Alvarado. In women of reproductive age → ultrasound FIRST (to exclude ovarian/ectopic pathology). In men + clear clinical picture → can go to theatre without imaging. If diagnosis uncertain → CT abdomen/pelvis. In pregnancy → MRI preferred. In children → ultrasound first, then MRI if needed (avoid CT radiation in children).', story)

image_search_box('CT scan appendicitis axial view showing fat stranding', 'Radiopaedia.org', story)
memory_hook('Tests in appendicitis: FBC + CRP + U&E + Urine dip + Pregnancy test (women). Then image if uncertain. USS first (women/children). CT if still uncertain. MRI in pregnancy. Remember: NORMAL TESTS DO NOT RULE OUT APPENDICITIS.', story)
divider(story)

# ─────────────────────────────────────────────────────────────────────────────
# §8  DIFFERENTIAL DIAGNOSIS — WHAT ELSE CAN CAUSE RIGHT LOWER ABDOMINAL PAIN?
# ─────────────────────────────────────────────────────────────────────────────
sec_header('Section 8: Differential Diagnosis — What Else Could It Be?', story)

professor_says('The right lower abdomen has many structures nearby. Any of them can cause pain. The skill is to know what else it could be — so you do not operate unnecessarily or miss something dangerous.', story)

diff_dx = [
    [bp('<b>Condition</b>', sH2), bp('<b>Who gets it</b>', sH2), bp('<b>Key features that DIFFER from appendicitis</b>', sH2), bp('<b>Key test / action</b>', sH2)],
    [bp('Mesenteric Adenitis\n(inflamed lymph nodes\nnear the bowel)'), bp('Children mostly.\nCan affect adults.'), bp('Often follows a recent cold or throat infection. Lymph nodes (small filter glands) swell inside the abdomen. Tenderness moves around — not fixed at McBurney\'s point. Temperature often higher. No nausea pattern.'), bp('This is the MOST COMMON cause of right lower abdominal pain in CHILDREN. Diagnosis often made after USS or after watching the patient improve without surgery. No specific test — diagnosis of exclusion.')],
    [bp('Ectopic Pregnancy\n(egg implanted\noutside the womb)'), bp('Women of\nchildbearing age'), bp('Missed period. Vaginal bleeding. Very sudden severe pain. Can collapse (rupture = emergency). Pain may be in shoulder (blood irritates diaphragm). Shoulder tip pain is a red flag.'), bp('BETA-hCG (urine or blood pregnancy test) = POSITIVE. Urgent transvaginal ultrasound. Gynaecology emergency — call immediately.')],
    [bp('PID\n(Pelvic Inflammatory\nDisease — infection\nof womb/tubes)'), bp('Sexually active\nwomen'), bp('Bilateral lower abdominal pain (both sides). Vaginal discharge. Pain worse on moving the cervix (cervical excitation — feels like moving a bruise). Fever. No nausea-vomiting-anorexia sequence.'), bp('High vaginal swab. STI (sexually transmitted infection) screen. USS. Treat with antibiotics — no surgery needed unless abscess.')],
    [bp('Ovarian Cyst\n(fluid-filled balloon\non the ovary)'), bp('Women of all ages'), bp('Often sudden pain (if the cyst twists or bursts). Cyclical pain (linked to menstrual cycle). USS shows the cyst clearly. Blood tests usually normal.'), bp('Transvaginal USS. If ovarian torsion (twisted ovary) — surgical emergency. Otherwise manage according to cyst type.')],
    [bp('Ovarian Torsion\n(twisted ovary)'), bp('Women of\nreproductive age'), bp('Very sudden, severe, constant pain. Often nausea and vomiting. Ovary twists on its blood supply — blood flow cut off. This is a surgical emergency. USS shows absent blood flow to ovary.'), bp('Urgent USS with Doppler blood flow. Emergency surgery to untwist ovary before it dies.')],
    [bp('Meckel\'s Diverticulum\n(a blind pouch on\nthe small bowel)'), bp('Anyone — present\nfrom birth'), bp('Causes bleeding (dark red blood from rectum), bowel obstruction, or inflammation (mimics appendicitis almost exactly). Located 2 feet from the end of the small bowel.'), bp('RULE OF 2s: 2 feet from end of ileum. 2 inches long. 2% of population. 2% become symptomatic. 2 types of tissue (gastric/pancreatic). Diagnosed by Meckel\'s scan (nuclear medicine) or found at surgery.')],
    [bp('Crohn\'s Disease\n(chronic bowel\ninflammation)'), bp('Young adults\nmostly'), bp('Longer history of symptoms. Diarrhoea (sometimes bloody). Weight loss. Mouth ulcers. Joint pains. Skin changes. Often affects terminal ileum (end of small bowel) near appendix area — can look exactly like appendicitis on CT.'), bp('CT/MRI scan. Colonoscopy + biopsy. Blood: CRP raised, anaemia. Faecal calprotectin raised. Do NOT operate thinking it is appendicitis without CT — resecting bowel in Crohn\'s can cause serious complications.')],
    [bp('Ureteric Colic\n(kidney stone in\nthe ureter tube)'), bp('Anyone — peak\nage 30–60'), bp('Excruciating pain — comes in waves (colicky). Radiates from loin (back/flank) to groin. Patient cannot stay still — rolls around in pain (opposite to peritonitis where patient lies still). Haematuria (blood in urine) in 80%.'), bp('Urine dipstick: blood. CT KUB (kidney-ureter-bladder scan): gold standard. USS can show hydronephrosis (swollen kidney). Treat: analgesia (NSAIDs first), fluids, watchful waiting for small stones.')],
    [bp('Caecal Carcinoma\n(bowel cancer\non the right side)'), bp('Older adults\n>50 years'), bp('Longer history. Weight loss. Change in bowel habit. Anaemia (iron deficiency from slow bleeding). A hard mass may be felt in the right lower abdomen. Appendix can become obstructed by the tumour — causing acute appendicitis.'), bp('CT abdomen/pelvis. Colonoscopy + biopsy. Tumour markers (CEA). Important: right-sided colon cancer often presents late because the bowel is wide on the right side and does not obstruct early.')],
    [bp('Right-sided\nDiverticulitis'), bp('Usually older\nadults. Rare.'), bp('Pain similar to appendicitis. CT shows inflamed diverticulum (small pouch) on the caecum or ascending colon — not the appendix itself. May have previous similar episodes.'), bp('CT abdomen/pelvis makes the diagnosis. Treat with antibiotics first. Surgery if complicated.')],
    [bp('Psoas Abscess\n(infection next to\nthe hip-flexor muscle)'), bp('Anyone — more\ncommon in\nimmunosuppressed'), bp('Pain in the right lower abdomen + right hip. Patient walks with right hip flexed (bent) — it hurts to straighten the hip. Fever + night sweats. May have history of TB (tuberculosis) or Crohn\'s disease.'), bp('CT scan shows fluid collection next to psoas muscle. Treat: drain the abscess + antibiotics. TB screening.')],
]
story.append(plain_table(diff_dx, [CW*0.17, CW*0.14, CW*0.4, CW*0.29]))

alert_box('NEVER FORGET IN WOMEN: Always check pregnancy test before any diagnosis of appendicitis in a woman of childbearing age. Ectopic pregnancy looks exactly like appendicitis AND is immediately life-threatening if missed.', story)
memory_hook('DIFF DX RIGHT LOWER PAIN: Mesenteric Adenitis (kids), Ectopic Pregnancy (women — CHECK hCG), PID, Ovarian cyst/torsion, Meckel\'s, Crohn\'s, Ureteric colic, Caecal carcinoma (older patients). Remember: women have more causes — always USS pelvis in women.', story)
divider(story)

# ─────────────────────────────────────────────────────────────────────────────
# §9  MANAGEMENT — HOW DO WE TREAT APPENDICITIS?
# ─────────────────────────────────────────────────────────────────────────────
sec_header('Section 9: Management — How Do We Treat Appendicitis?', story)

professor_says('Management of appendicitis has changed dramatically in the last 10 years. Surgery used to be the ONLY answer. Now we know antibiotics alone can work in selected patients. But surgery remains the gold standard for most cases.', story)

story.append(bp('<b>Step 1: Initial Resuscitation — Stabilise the Patient First</b>'))
resus_steps = [
    [bp('<b>Action</b>', sH2), bp('<b>Why</b>', sH2), bp('<b>Details</b>', sH2)],
    [bp('IV Access'), bp('Needed for fluids + drugs'), bp('Large-bore cannula in arm vein. Take blood at the same time — FBC, CRP, U&E, G&S.')],
    [bp('IV Fluids'), bp('Patients are often dehydrated from vomiting and not eating'), bp('Start normal saline or Hartmann\'s solution. Give 500ml over 30 minutes if patient is dry. Monitor urine output.')],
    [bp('Analgesia\n(Pain relief)'), bp('Patient is in pain. Pain relief is SAFE and HUMANE.'), bp('Opioids (morphine, codeine) are SAFE. IV morphine 2.5–5mg titrated. Do NOT withhold analgesia — the old teaching that "analgesia masks signs" has been scientifically DISPROVEN. Evidence: analgesia does NOT affect diagnostic accuracy.')],
    [bp('Antiemetics\n(anti-vomiting drugs)'), bp('Patient may be nauseated or vomiting'), bp('Ondansetron 4mg IV OR cyclizine 50mg IV. Give with or before opioids.')],
    [bp('NBM\n(Nil by Mouth)'), bp('Patient may need surgery. Stomach must be empty to prevent aspiration during anaesthesia.'), bp('Put up NBM sign. Explain to patient. Continue IV fluids to prevent dehydration.')],
    [bp('Urinary catheter'), bp('Monitor fluid balance. Especially in sick/perforated patients.'), bp('Insert Foley catheter. Aim urine output >0.5ml/kg/hour.')],
    [bp('Observations'), bp('Monitor for deterioration'), bp('Temperature, pulse, blood pressure, oxygen saturation, respiratory rate every 30–60 minutes. NEWS2 score.')],
]
story.append(plain_table(resus_steps, [CW*0.18, CW*0.3, CW*0.52]))
story.append(Spacer(1, 8))

info_box('<b>MRCP KEY FACT — Analgesia in Appendicitis:</b> It was once taught that giving pain relief to patients with acute abdominal pain would "mask the signs" and make diagnosis harder. THIS IS NOW PROVEN WRONG. Multiple randomised controlled trials show opioid analgesia does NOT reduce diagnostic accuracy. Withholding pain relief is cruel and unjustified. Always give adequate analgesia.', story)

story.append(Spacer(1, 8))
story.append(bp('<b>Step 2: Antibiotic Treatment</b>'))

story.append(bp('Antibiotics are given to EVERYONE with suspected appendicitis. They treat the infection AND reduce complications. They are given BEFORE surgery (perioperative antibiotics) and continued AFTER surgery.'))
story.append(Spacer(1, 4))

ab_table = [
    [bp('<b>Situation</b>', sH2), bp('<b>Antibiotic Choice</b>', sH2), bp('<b>Dose and Route</b>', sH2), bp('<b>Duration</b>', sH2)],
    [bp('Simple appendicitis\n(not perforated)\n— before and after surgery'), bp('Cefuroxime\n+\nMetronidazole'), bp('Cefuroxime: 1.5g IV\nMetronidazole: 500mg IV'), bp('Single dose before surgery (perioperative). Up to 24 hours post-op. No longer needed once patient eating and well.')],
    [bp('Perforated appendicitis\nor severe infection\n(peritonitis, abscess)'), bp('Piperacillin-Tazobactam\n(brand name: Tazocin)\nOR\nCo-amoxiclav + Metronidazole'), bp('Piperacillin-Tazobactam:\n4.5g IV every 8 hours'), bp('5–7 days IV, then switch to oral if improving. Duration guided by clinical response and CRP trend.')],
    [bp('Penicillin allergy'), bp('Ciprofloxacin\n+\nMetronidazole'), bp('Ciprofloxacin: 400mg IV\nMetronidazole: 500mg IV'), bp('Same as above — guided by clinical response.')],
]
story.append(plain_table(ab_table, [CW*0.25, CW*0.25, CW*0.25, CW*0.25]))
story.append(Spacer(1, 8))

story.append(bp('<b>Step 3: Surgical Treatment — Appendicectomy</b>'))
story.append(bp('Appendicectomy means removing the appendix. This is the definitive (final, permanent) treatment. There are two ways to do it:'))
story.append(Spacer(1, 4))

surg_compare = [
    [bp('<b>Method</b>', sH2), bp('<b>How it is done</b>', sH2), bp('<b>Advantages</b>', sH2), bp('<b>Disadvantages</b>', sH2), bp('<b>When preferred</b>', sH2)],
    [bp('Laparoscopic\nAppendicectomy\n(Keyhole surgery)'), bp('3 small cuts (5–10mm). Camera inserted. Surgeon watches screen. Appendix removed through small cuts.'), bp('Less pain after operation. Shorter hospital stay (1–2 days). Faster return to normal activity. Better cosmetic result (tiny scars). Can see whole abdomen — finds other causes if it is NOT appendicitis.'), bp('Requires specialist equipment and training. Longer operating time. More expensive.'), bp('PREFERRED method in most hospitals now. Especially useful in women (can examine ovaries at same time). Obese patients. Diagnostic uncertainty.')],
    [bp('Open\nAppendicectomy\n(Gridiron incision)'), bp('Single cut in right lower abdomen over McBurney\'s point. Appendix found and removed directly.'), bp('Simpler. No special equipment. Can be done in any operating theatre anywhere in the world. Faster if anatomy is clear.'), bp('Bigger scar. More post-operative pain. Longer hospital stay. Harder to see rest of abdomen.'), bp('Perforated appendicitis with generalised peritonitis. Where laparoscopic equipment not available. Patient too unwell for prolonged anaesthesia.')],
]
story.append(plain_table(surg_compare, [CW*0.15, CW*0.2, CW*0.2, CW*0.2, CW*0.25]))
story.append(Spacer(1, 8))

story.append(bp('<b>Step 4: Antibiotics ONLY — Non-Operative Management (NEW EVIDENCE)</b>'))
professor_says('This is a game-changer in surgery. For 100 years we thought every appendicitis needed an operation. Two landmark trials changed this thinking.', story)

story.append(bp('<b>APPAC Trial (Finland, 2015)</b>'))
story.append(bp('APPAC = Appendicitis Acuta. A large randomised controlled trial from Finland.'))
story.append(bp('They took patients with uncomplicated appendicitis (no perforation, no abscess on CT). They split them into two groups: one group had surgery, the other group had antibiotics only (ertapenem then oral levofloxacin and metronidazole).'))
story.append(bp('Result: 73% of the antibiotic group were treated successfully WITHOUT surgery in the short term. At 5 years, 39% of the antibiotic group had eventually needed surgery (mostly because appendicitis came back).'))
story.append(Spacer(1, 4))

story.append(bp('<b>CODA Trial (USA, 2020)</b>'))
story.append(bp('A larger trial. Confirmed similar results. Antibiotics were non-inferior (not worse) to surgery for uncomplicated appendicitis.'))
story.append(bp('Key finding: Many patients PREFER antibiotics to avoid an operation. Antibiotics work well in the short term. Long-term, some will need surgery eventually.'))
story.append(Spacer(1, 6))

info_box('<b>When can we use antibiotics only (non-operative management)?</b> Criteria: CT-confirmed uncomplicated appendicitis (no perforation, no abscess, no faecolith). Patient is systemically well (not septic). Patient understands the 30% chance of needing surgery within 5 years. Patient agrees to the plan after counselling (shared decision-making). NOT suitable if: perforated, abscess present, faecolith (calcified stone) in appendix — these have very high failure rate with antibiotics.', story)

story.append(Spacer(1, 6))
story.append(bp('<b>Timing of Surgery</b>'))
timing_table = [
    [bp('<b>Situation</b>', sH2), bp('<b>Urgency</b>', sH2), bp('<b>Reasoning</b>', sH2)],
    [bp('Perforated appendicitis\n+ generalised peritonitis'), bp('EMERGENCY\nWithin 2 hours'), bp('Patient is critically ill. Peritoneum is contaminated. Every hour increases mortality (death rate). Immediate theatre.')],
    [bp('Appendix abscess\nor phlegmon'), bp('Not immediate surgery\n— often antibiotics first'), bp('Abscess can be drained (by radiologist with CT guidance). Then surgery planned later (interval appendicectomy — 6–8 weeks later) once inflammation settled.')],
    [bp('Uncomplicated appendicitis\n(no perforation)'), bp('Urgent — within 24 hours\nbut NOT emergency'), bp('Studies show waiting up to 24 hours for confirmed uncomplicated appendicitis does NOT increase perforation rate. Allows time for morning operating list, safer anaesthesia, consent.')],
]
story.append(plain_table(timing_table, [CW*0.3, CW*0.2, CW*0.5]))

memory_hook('MANAGEMENT: Resuscitate → IV fluids, analgesia (MORPHINE IS SAFE), NBM, antibiotics. Surgery: laparoscopic preferred. Open if perforated/peritonitis. APPAC/CODA trials: antibiotics alone work in 70% of uncomplicated cases. Perforated = emergency theatre within 2 hours.', story)
divider(story)

# ─────────────────────────────────────────────────────────────────────────────
# §10  COMPLICATIONS
# ─────────────────────────────────────────────────────────────────────────────
sec_header('Section 10: Complications — What Can Go Wrong?', story)

professor_says('Complications occur when appendicitis is not treated in time — or sometimes even after treatment. Understanding complications helps you recognise them early and act fast.', story)

complications = [
    [bp('<b>Complication</b>', sH2), bp('<b>What it means</b>', sH2), bp('<b>Signs and symptoms</b>', sH2), bp('<b>Treatment</b>', sH2)],
    [bp('Perforation\n(Burst appendix)'), bp('The appendix wall breaks open. Contents (bacteria, pus, faeces) pour into the abdomen.'), bp('Sudden severe worsening of pain. Then brief improvement (as pressure releases). Then generalised pain all over abdomen. High fever. Rigid abdomen. Tachycardia. Unwell patient.'), bp('Emergency surgery. Washout of the abdomen (peritoneal lavage). IV antibiotics: Tazocin. ICU care if septic. High mortality if delayed.')],
    [bp('Peritonitis\n(inflamed abdominal\nlining)'), bp('The peritoneum (the membrane lining the inside of the abdomen) becomes inflamed. Can be localised (around appendix) or generalised (whole abdomen).'), bp('Board-like rigid abdomen. Involuntary guarding. Rebound tenderness everywhere. Patient lies very still — any movement causes severe pain. Fever. Sepsis signs.'), bp('Emergency surgery. Washout. IV antibiotics. Supportive care. ICU if needed.')],
    [bp('Appendix Mass\n(Phlegmon)'), bp('The inflamed appendix becomes stuck to the surrounding bowel and fat (omentum). They form a mass — like a ball of inflamed tissue around the appendix. The appendix is in the middle but not yet perforated/abscessed.'), bp('Palpable (felt on examination) mass in right lower abdomen. Less acute now — pain may actually be improving. Mild fever. This often means the body has "contained" the infection.'), bp('Conservative management: IV antibiotics + rest + fluids. NO immediate surgery — operating now risks damaging stuck bowel. Plan interval appendicectomy 6–8 weeks later. If mass enlarges or patient worsens → consider surgery or drainage.')],
    [bp('Appendix Abscess'), bp('A collection of pus (infected fluid) forms around the appendix. The body has walled off the infection.'), bp('High fever. Swinging temperature (high, then normal, then high again). Palpable tender mass. Patient unwell but not in immediate danger of dying.'), bp('Percutaneous drainage (a radiologist inserts a drain through the skin using CT guidance). IV antibiotics. Then interval appendicectomy 6–8 weeks later after full recovery.')],
    [bp('Portal Pyaemia\n(infected blood clots\nto liver — RARE)'), bp('Bacteria enter the portal vein (the vein that drains blood from the bowel to the liver). Infected clots form in the liver, causing liver abscesses.'), bp('High swinging fever. Jaundice (yellow skin/eyes). Right upper abdominal pain (over the liver). Very unwell. Rare but serious.'), bp('CT abdomen. IV antibiotics for 4–6 weeks. Drainage of liver abscesses. Anticoagulation (blood-thinning) for portal vein thrombosis.')],
    [bp('Post-Operative\nWound Infection'), bp('The operation site becomes infected. Common after perforated appendicitis.'), bp('Red, hot, painful wound. Discharge (pus) from wound. Fever.'), bp('Open wound edges. Drain pus. Wound swab. Antibiotics if spreading cellulitis. Wound care. Delayed primary closure.')],
    [bp('Ileus\n(bowel stops working\nafter surgery)'), bp('The intestines become temporarily paralysed after surgery. This is normal for 24–48 hours. Prolonged ileus is a complication.'), bp('No bowel sounds. Nausea. No flatus (no passing of wind). Distended abdomen.'), bp('NBM. IV fluids. Nasogastric tube if vomiting. Usually resolves on its own in 3–5 days. Investigate if prolonged (check electrolytes, rule out obstruction).')],
    [bp('Adhesions and\nBowel Obstruction\n(long-term)'), bp('Scar tissue forms inside the abdomen after surgery or peritonitis. This scar tissue (adhesion) can wrap around bowel loops and block them — months or years later.'), bp('Episodes of severe colicky abdominal pain. Vomiting. Distension. Inability to pass wind or stool.'), bp('Surgery is the most common cause of bowel obstruction in developed countries. Treat with NG tube decompression, IV fluids. Surgery if not resolving — to divide the adhesions (adhesiolysis).')],
]
story.append(plain_table(complications, [CW*0.15, CW*0.22, CW*0.3, CW*0.33]))

alert_box('PERFORATION RATE: Rises dramatically with delay. At symptom onset: 5%. At 24 hours: 20%. At 48 hours: 50%+. Children and elderly perforate faster — they have thinner/weaker appendix walls.', story)
divider(story)

# ─────────────────────────────────────────────────────────────────────────────
# §11  SPECIAL SITUATIONS
# ─────────────────────────────────────────────────────────────────────────────
sec_header('Section 11: Special Situations — Appendicitis in Different Groups', story)

professor_says('Appendicitis does not always look the same. In certain groups of patients, the presentation is different — and missing the diagnosis has worse consequences. These are MRCP and PACES favourites.', story)

story.append(bp('<b>Appendicitis in PREGNANCY</b>'))
preg_points = [
    '<b>How common?</b> Most common non-obstetric (non-pregnancy related) surgical emergency in pregnancy. 1 in 1500 pregnancies.',
    '<b>The problem:</b> As pregnancy advances, the growing womb (uterus) pushes the appendix upward and to the right. By the third trimester (7–9 months), the appendix can be near the right upper abdomen — near the liver. Pain is NOT in the classic location.',
    '<b>Symptoms change:</b> Pain may be in the right upper or right lateral (side) abdomen rather than the right lower abdomen. Nausea and vomiting are present in normal pregnancy — so they are not helpful as diagnostic clues.',
    '<b>Delay is dangerous:</b> Perforation in pregnancy can cause preterm labour (baby born too early), miscarriage, or maternal sepsis. Fetal mortality in perforated appendicitis: 20–35%.',
    '<b>Investigations:</b> USS first — safe. But USS cannot see the appendix well when the uterus is large. <b>MRI is the imaging of choice</b> — no radiation, accurate, safe for the baby.',
    '<b>CT scan:</b> Use only if MRI not available and diagnosis uncertain — radiation risk to fetus is real but the risk of missing perforated appendicitis is higher. Clinical decision.',
    '<b>Surgery:</b> Laparoscopic appendicectomy is SAFE in all three trimesters. Do not delay surgery for fear of harming the pregnancy — untreated perforated appendicitis is far more dangerous.',
    '<b>Uterine tocolysis</b> (drugs to prevent uterine contractions): used sometimes after surgery in second/third trimester to prevent preterm labour.',
]
for pt in preg_points:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 4))
image_search_box('appendix position in pregnancy diagram showing upward displacement', 'Google Images', story)

story.append(Spacer(1, 8))
story.append(bp('<b>Appendicitis in the ELDERLY (Over 65 years)</b>'))
elderly_points = [
    '<b>Atypical presentation:</b> Older people have less sensitive nerves and weaker immune responses. They may feel less pain than expected. Fever may be absent or low-grade. The classic story is often incomplete.',
    '<b>Higher perforation rate:</b> Because symptoms are less dramatic, diagnosis is often delayed. The appendix wall is thinner and more fragile in older people — it perforates faster.',
    '<b>Diagnostic challenge:</b> Other causes of right lower pain in the elderly are more common — caecal carcinoma, diverticulitis. Always consider underlying cancer if an older person has "appendicitis".',
    '<b>Always get CT scan</b> in elderly patients — clinical exam and blood tests are less reliable. CT confirms diagnosis and rules out cancer.',
    '<b>High mortality:</b> Perforated appendicitis in the elderly carries 5–10% mortality. Poor physiological reserve (less ability to cope with stress). Comorbidities (heart disease, diabetes) make surgery riskier.',
    '<b>Management:</b> Same principles — surgery. But anaesthetic risk assessment is important. Involve anaesthetics early. Consider HDU/ICU post-operatively.',
]
for pt in elderly_points:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 8))

story.append(bp('<b>Appendicitis in CHILDREN</b>'))
child_points = [
    '<b>Most common differential:</b> Mesenteric adenitis — inflamed lymph nodes in the abdomen. Often follows a cold or throat infection. Very common in children. Can look exactly like appendicitis.',
    '<b>Younger children cannot describe symptoms:</b> A 3-year-old cannot say "my pain started around my navel and moved to the right". They cry, refuse food, guard their abdomen, lie still. High index of suspicion needed.',
    '<b>Thinner omentum:</b> Children have a thin, undeveloped omentum (the fat apron inside the abdomen that contains infection). The omentum in adults helps wall off infection. In young children, there is no protection — perforation leads to generalised peritonitis rapidly.',
    '<b>High perforation rate:</b> 30–50% of children with appendicitis are already perforated at the time of diagnosis. Delay is common because of atypical presentation and difficulty in diagnosis.',
    '<b>Scoring:</b> Use Pediatric Appendicitis Score (PAS) instead of Alvarado in children.',
    '<b>Imaging:</b> Ultrasound FIRST in children (no radiation). MRI if USS inconclusive. Avoid CT if possible — radiation is proportionally more harmful to growing children.',
    '<b>Neonates (newborn babies):</b> Appendicitis is extremely rare. Presents with abdominal distension, vomiting, perforation. Very high mortality. Difficult diagnosis.',
]
for pt in child_points:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 8))

story.append(bp('<b>RETROCAECAL Appendix — The Hidden Appendix</b>'))
retrocaecal_points = [
    '<b>What does retrocaecal mean?</b> Retro = behind. Caecal = caecum. The appendix sits BEHIND the caecum (the first part of the large bowel). It is the MOST COMMON position variant — present in 65–70% of people.',
    '<b>Why does it matter?</b> When the appendix is behind the caecum, it is separated from the anterior (front) abdominal wall. The normal signs (McBurney\'s tenderness, rebound) may be ABSENT or much less obvious.',
    '<b>Key sign: Psoas sign.</b> The psoas muscle is a long muscle that runs from the lower spine to the hip. It sits very close behind the caecum. An inflamed retrocaecal appendix irritates the psoas muscle.',
    '<b>Testing the psoas sign:</b> Patient lies on the LEFT side. Examiner extends the RIGHT hip backwards (moves the right leg back and up). This stretches the psoas muscle. If the appendix is inflamed near the psoas, this causes pain in the right lower abdomen. POSITIVE psoas sign = retrocaecal appendicitis.',
    '<b>Other atypical features:</b> Right flank or right hip pain rather than right lower abdominal pain. Urinary symptoms (appendix near the right ureter). Back pain.',
    '<b>Clinical implication:</b> A patient with typical systemic symptoms (fever, anorexia, nausea, raised WBC, raised CRP) but minimal abdominal tenderness — think retrocaecal appendicitis. Do not be falsely reassured.',
]
for pt in retrocaecal_points:
    story.append(bp(f'• {pt}'))

memory_hook('SPECIAL GROUPS: Pregnancy = appendix moves UP, use MRI. Elderly = atypical, get CT, high perforation, high mortality. Children = think mesenteric adenitis first, no omentum protection, fast perforation. Retrocaecal = psoas sign, no anterior tenderness.', story)
divider(story)

# ─────────────────────────────────────────────────────────────────────────────
# §12  APPENDIX TUMOURS
# ─────────────────────────────────────────────────────────────────────────────
sec_header('Section 12: Appendix Tumours — What Grows in the Appendix?', story)

professor_says('Tumours of the appendix are rare. But they are tested in MRCP because there are specific rules for management that examiners love to ask about.', story)

tumour_table = [
    [bp('<b>Tumour Type</b>', sH2), bp('<b>Key Facts</b>', sH2), bp('<b>Management</b>', sH2), bp('<b>MRCP Points</b>', sH2)],
    [bp('Carcinoid Tumour\n(Neuroendocrine Tumour)\n— MOST COMMON appendix tumour'), bp('Found in 0.3% of appendicectomy specimens. Most are at the TIP of the appendix. Made of neuroendocrine cells (cells that produce hormones). Usually found incidentally (by accident) during appendicectomy.'), bp('<b>Size rule:</b>\n• <2cm: Simple appendicectomy is CURATIVE. No further surgery needed.\n• >2cm: Right hemicolectomy needed (remove right half of the large bowel).\n• The cut-off is 2cm because tumours >2cm have a higher rate of lymph node spread.'), bp('MRCP loves the 2cm rule. If the question says "carcinoid found in appendix specimen, 1.5cm" → appendicectomy is sufficient. If >2cm → needs right hemicolectomy. Carcinoid syndrome (flushing, diarrhoea, wheezing) occurs ONLY if liver metastases present — because the liver normally breaks down the carcinoid hormones.')],
    [bp('Mucocele of\nthe Appendix'), bp('The appendix fills up with mucus (a thick fluid) and swells. It looks like a balloon full of jelly. Can be caused by: benign mucinous cystadenoma OR malignant mucinous cystadenocarcinoma.'), bp('Careful surgical removal. The appendix must NOT be ruptured during surgery. If it ruptures, mucus-producing cells spill into the abdomen.'), bp('DANGER: If a mucocele RUPTURES, it causes <b>Pseudomyxoma Peritonei</b> — the abdominal cavity fills with jelly-like mucus. This is extremely difficult to treat. Treatment: extensive surgery (cytoreduction) + heated chemotherapy washed into the abdomen (HIPEC). Poor prognosis.')],
    [bp('Adenocarcinoma\nof the Appendix'), bp('True cancer of the appendix lining. Very rare. Often presents like appendicitis. Found on histology (microscopy of the removed appendix specimen).'), bp('Right hemicolectomy regardless of size (it is a true cancer).'), bp('Always send the appendix specimen for histology after surgery. This is how rare tumours are found. Important medico-legal and oncological reason.')],
    [bp('Lymphoma'), bp('Very rare. The appendix contains lymphoid tissue (like the tonsils). Lymphoma can originate here.'), bp('Oncology referral. Chemotherapy.'), bp('Important to distinguish from appendicitis — though often diagnosed post-operatively on histology.')],
]
story.append(plain_table(tumour_table, [CW*0.2, CW*0.28, CW*0.25, CW*0.27]))

info_box('<b>Carcinoid Syndrome:</b> Carcinoid tumours produce serotonin (5-HT) and other hormones. Normally the liver destroys these hormones before they reach the rest of the body. Carcinoid syndrome ONLY occurs when there are liver metastases (secondary tumours in the liver) — because then the hormones bypass the liver and reach the systemic circulation. Symptoms: episodic flushing (bright red face), watery diarrhoea, wheezing (bronchospasm), right heart valve disease. Test: 24-hour urine 5-HIAA (breakdown product of serotonin).', story)

memory_hook('CARCINOID RULE OF 2: <2cm = appendicectomy alone is curative. >2cm = right hemicolectomy. Carcinoid syndrome ONLY with LIVER METS. Mucocele rupture → Pseudomyxoma Peritonei (jelly abdomen). Always send appendix for histology.', story)
divider(story)

# ─────────────────────────────────────────────────────────────────────────────
# §13  PHARMACOLOGY
# ─────────────────────────────────────────────────────────────────────────────
sec_header('Section 13: Pharmacology — Drugs Used in Appendicitis', story)

professor_says('You need to know the drugs, the doses, the mechanisms, and the rationale. This section covers everything from pain relief to antibiotics to post-operative care.', story)

pharm_table = [
    [bp('<b>Drug</b>', sH2), bp('<b>Class</b>', sH2), bp('<b>Mechanism</b>', sH2), bp('<b>Dose</b>', sH2), bp('<b>Clinical Notes</b>', sH2)],
    [bp('Morphine'), bp('Opioid analgesic\n(pain killer)'), bp('Binds to mu-opioid receptors in the brain and spinal cord. Reduces pain signal transmission. Produces strong analgesia (pain relief).'), bp('IV: 2.5–5mg slow IV.\nTitrate to effect.\nRepeat every 4 hours.\nPRN (as needed).'), bp('SAFE in appendicitis. Does NOT mask signs. Give with antiemetic. Monitor: respiratory rate, sedation score. Antidote: Naloxone.')],
    [bp('Paracetamol\n(Acetaminophen)'), bp('Non-opioid analgesic\n+ antipyretic\n(reduces fever)'), bp('Inhibits prostaglandin synthesis in the brain (central action). Mechanism not fully understood. Reduces pain and fever.'), bp('IV: 1g (15mg/kg if <50kg)\nevery 6 hours.\nOral: 1g every 4–6 hours.\nMax: 4g/24 hours.'), bp('First-line for mild-moderate pain. Safe in pregnancy. Liver toxicity in overdose — do not exceed 4g/day. Good baseline analgesia — use alongside opioids (reduces opioid requirement).')],
    [bp('Ibuprofen / NSAIDs\n(Non-Steroidal\nAnti-Inflammatory\nDrugs)'), bp('NSAID analgesic\n+ anti-inflammatory'), bp('Inhibits COX-1 and COX-2 enzymes → reduces prostaglandin synthesis → reduces pain, inflammation, fever.'), bp('Ibuprofen: 400mg oral\ntds (3 times a day)\nwith food.'), bp('AVOID in appendicitis pre-operatively: NSAIDs impair platelet function (bleeding risk in surgery). Avoid in: renal impairment, peptic ulcer, pregnancy (especially 3rd trimester).')],
    [bp('Ondansetron'), bp('Antiemetic\n(5-HT3 antagonist)'), bp('Blocks 5-HT3 (serotonin) receptors in the gut and brainstem vomiting centre. Prevents and treats nausea and vomiting.'), bp('IV: 4mg over 2–5 min.\nOral: 4–8mg\nRepeat after 4–6 hours.'), bp('First-line antiemetic for post-operative nausea. Can cause QT prolongation (check ECG in at-risk patients). Constipation is common side effect.')],
    [bp('Cyclizine'), bp('Antiemetic\n(antihistamine)'), bp('Blocks H1 histamine receptors and muscarinic receptors in the vomiting centre.'), bp('IV/IM: 50mg tds\n(3 times a day).\nOral: 50mg tds.'), bp('Good for motion sickness and opioid-induced nausea. Can cause dry mouth, blurred vision, urinary retention (anticholinergic effects). Avoid in severe heart failure.')],
    [bp('Cefuroxime'), bp('Cephalosporin\n(2nd generation)\n— antibiotic'), bp('Beta-lactam ring inhibits bacterial cell wall synthesis (peptidoglycan cross-linking). Bactericidal (kills bacteria).'), bp('IV: 1.5g at induction\n(anaesthetic start).\nPost-op: 750mg tds\nfor 24 hours.'), bp('Broad-spectrum — covers gram-positive and gram-negative bacteria. Covers the likely appendix bacteria (E.coli, Klebsiella, Enterococcus). Does NOT cover anaerobes — hence combined with metronidazole. 10% cross-reactivity with penicillin allergy.')],
    [bp('Metronidazole'), bp('Nitroimidazole\n— antibiotic\n+ antiprotozoal'), bp('Forms toxic free radicals inside anaerobic bacteria → damages DNA → bactericidal (kills). Only works in low-oxygen environments (anaerobes). Does NOT work against aerobic bacteria.'), bp('IV: 500mg tds\n(every 8 hours).\nOral: 400mg tds.'), bp('Essential partner to cefuroxime — covers ANAEROBES (Bacteroides fragilis — the main bug in perforated appendicitis). Disulfiram reaction with alcohol (severe vomiting) — warn patient. Metallic taste in mouth. Peripheral neuropathy with long courses.')],
    [bp('Piperacillin-\nTazobactam\n(Tazocin)'), bp('Extended-spectrum\npenicillin +\nbeta-lactamase inhibitor'), bp('Piperacillin: beta-lactam kills bacteria. Tazobactam: inhibits beta-lactamase enzyme (the enzyme bacteria use to destroy penicillins). Together they kill bacteria that would normally resist piperacillin alone.'), bp('IV: 4.5g every 8 hours\n(or every 6 hours in\nsevere sepsis).'), bp('Broad-spectrum — covers gram-positive, gram-negative, AND anaerobes in one drug. First-line for perforated appendicitis. Covers Pseudomonas. Adjust dose in renal impairment. Sodium load — relevant in heart failure.')],
    [bp('Normal Saline\n(0.9% NaCl)'), bp('IV crystalloid fluid'), bp('Replaces extracellular fluid. Each litre contains 154mmol sodium and 154mmol chloride.'), bp('500ml bolus IV over\n15–30 min for\ndehydration/sepsis.\nThen reassess.'), bp('Use for initial resuscitation. Risk: hyperchloraemic metabolic acidosis (too much chloride) with large volumes. Hartmann\'s solution (Ringer\'s lactate) is preferred for large volume resuscitation — more physiological.')],
    [bp('Hartmann\'s Solution\n(Ringer\'s Lactate)'), bp('Balanced IV crystalloid'), bp('More physiological than normal saline. Contains sodium, potassium, calcium, chloride, and lactate in near-physiological concentrations.'), bp('500ml–1L bolus for\nresuscitation. Then\nmaintenance as needed.'), bp('Preferred for large volume replacement in appendicitis/peritonitis. Does not cause hyperchloraemic acidosis. Lactate converted to bicarbonate in the liver (helps correct acidosis in sepsis).')],
]
story.append(plain_table(pharm_table, [CW*0.15, CW*0.13, CW*0.22, CW*0.15, CW*0.35]))
story.append(Spacer(1, 6))

info_box('<b>Key Prescribing Principle (Ganesh & Kuruvilla):</b> In surgical patients, use a multi-modal analgesic approach — paracetamol + opioid together works better than either alone. This reduces total opioid use and side effects. Always prescribe antiemetics alongside opioids. Always check drug allergies before prescribing antibiotics. Document every drug with dose, route, frequency and indication.', story)

memory_hook('ANTIBIOTICS IN APPENDICITIS: Simple = Cefuroxime + Metronidazole. Perforated = Tazocin (Piperacillin-Tazobactam). Penicillin allergy = Ciprofloxacin + Metronidazole. Metronidazole covers ANAEROBES — always pair it with something for aerobic bacteria.', story)
divider(story)

# ─────────────────────────────────────────────────────────────────────────────
# §14  MRCP EXAM TRIGGERS — WHAT SCENARIOS APPEAR IN MRCP PART 1, 2, AND PACES?
# ─────────────────────────────────────────────────────────────────────────────
sec_header('Section 14: MRCP Exam Triggers — Recognised High-Yield Scenarios', story)

professor_says('These are the exact types of clinical scenarios that appear in MRCP Part 1, Part 2, and PACES. Learn these patterns and you will recognise them in the exam within seconds.', story)

mrcp_triggers = [
    [bp('<b>#</b>', sH2), bp('<b>Scenario</b>', sH2), bp('<b>Key Teaching Point</b>', sH2), bp('<b>Answer / Action</b>', sH2)],
    [bp('1'), bp('A 25-year-old man has 12 hours of central abdominal pain that has moved to the right lower abdomen. He has nausea, fever 38.1°C, and right iliac fossa tenderness. WBC 14,000.'), bp('Classic migration of pain pattern + systemic features.'), bp('Diagnosis: Appendicitis. Alvarado score ~7. Management: Admit, NBM, IV fluids, cefuroxime + metronidazole, consent for laparoscopic appendicectomy.')],
    [bp('2'), bp('A doctor wants to give morphine to a patient with suspected appendicitis. His consultant says "do not give morphine — it will mask the signs."'), bp('Landmark teaching point. MRCP tests this regularly.'), bp('The consultant is WRONG. Evidence-based medicine shows opioid analgesia does NOT reduce diagnostic accuracy. Give morphine. Adequate analgesia is a patient right.')],
    [bp('3'), bp('A 28-year-old pregnant woman (16 weeks) has right-sided abdominal pain. Ultrasound is inconclusive. What is the next investigation?'), bp('Appendix position changes in pregnancy. Imaging choice in pregnancy.'), bp('MRI abdomen — no radiation, accurate, safe in all trimesters. Do NOT use CT if MRI available in a pregnant patient.')],
    [bp('4'), bp('A patient is treated with antibiotics only for uncomplicated CT-confirmed appendicitis. She is well at 48 hours. What is the risk of recurrence at 5 years?'), bp('APPAC/CODA trial data.'), bp('Approximately 30–39% will need surgery within 5 years. 70% can be managed long-term without surgery. This is the basis for non-operative management counselling.')],
    [bp('5'), bp('An appendicectomy specimen shows a 1.8cm carcinoid tumour at the tip of the appendix. What is the management?'), bp('Carcinoid 2cm rule — MRCP favourite.'), bp('Appendicectomy ALONE is curative for carcinoid <2cm. No further surgery needed. Reassure the patient.')],
    [bp('6'), bp('An appendicectomy specimen shows a 2.5cm carcinoid tumour. What is the management?'), bp('Same rule — the other side.'), bp('Right hemicolectomy is required. Tumours >2cm have significant risk of lymph node and distant metastases. Refer to oncology and colorectal surgery.')],
    [bp('7'), bp('A 70-year-old man has 3 days of worsening right lower abdominal pain. Examination: tender mass in the right lower quadrant. CRP 150. WBC 16,000.'), bp('Appendix mass (phlegmon) vs. caecal cancer. Important in elderly.'), bp('First: CT abdomen/pelvis — confirms appendix mass OR may reveal caecal carcinoma. For appendix mass: IV antibiotics + bowel rest. No immediate surgery. Plan interval appendicectomy +/- colonoscopy in 6–8 weeks to exclude underlying malignancy.')],
    [bp('8'), bp('A mucocele of the appendix is discovered during surgery. The surgeon accidentally ruptures it.'), bp('Mucocele complication.'), bp('Risk of Pseudomyxoma Peritonei — abdominal cavity fills with mucus-secreting cells. This is a serious complication requiring extensive surgery (cytoreduction + HIPEC — heated intraperitoneal chemotherapy). Patient should be informed and referred to specialist centre.')],
    [bp('9'), bp('A 5-year-old child has right lower abdominal pain after a cold last week. Temperature 38.5°C. Tender in RIF. USS: no appendix seen, some enlarged lymph nodes in the mesentery.'), bp('Mesenteric adenitis vs. appendicitis in children.'), bp('Most likely mesenteric adenitis. Observe and reassess. If improving → discharge with advice. If worsening → surgical review. Key point: mesenteric adenitis is the most common cause of RIF pain in CHILDREN.')],
    [bp('10'), bp('A patient has right lower abdominal pain but also urinary frequency, haematuria, and pain radiating to the groin. Patient cannot stay still.'), bp('Ureteric colic vs. appendicitis.'), bp('Colicky pain radiating to groin + haematuria + inability to lie still = ureteric colic (kidney stone). Order: urine dipstick (blood+), CT KUB. Treat with NSAIDs (diclofenac 75mg IM) + oral fluids.')],
    [bp('11'), bp('A 22-year-old woman has right lower abdominal pain and a positive pregnancy test. She is haemodynamically unstable (BP 80/50, HR 130).'), bp('Ectopic pregnancy — life-threatening emergency.'), bp('This is a RUPTURED ECTOPIC PREGNANCY. Call for emergency team. 2 large-bore IV cannulae. Blood transfusion. O-negative blood. Emergency laparotomy or laparoscopy. Gynaecology must be contacted IMMEDIATELY. This woman may die within minutes if not treated.')],
    [bp('12'), bp('A patient undergoing appendicectomy for simple appendicitis asks if they can just have antibiotics. What do you tell them?'), bp('Shared decision-making + APPAC/CODA evidence.'), bp('Explain the evidence: antibiotics work in 70% of cases in the short term. 30–39% will need surgery within 5 years if managed non-operatively. Faecolith present = high failure rate with antibiotics. If the patient understands and still prefers antibiotics → non-operative management is a valid evidence-based option.')],
]
story.append(plain_table(mrcp_triggers, [CW*0.04, CW*0.3, CW*0.25, CW*0.41]))
divider(story)

# ─────────────────────────────────────────────────────────────────────────────
# §15  MINIMAL RESOURCES SUMMARY + PACES GUIDE
# ─────────────────────────────────────────────────────────────────────────────
sec_header('Section 15: Minimal Resources Summary + PACES Examination Guide', story)

story.append(bp('<b>Managing Appendicitis With Minimal Resources — Clinical Exam + Basic Investigations Only</b>'))
professor_says('In many parts of the world — and in resource-limited settings, night shifts in small hospitals, or community settings — you will not have CT, MRI, or specialist surgeons immediately available. Here is how to manage with what you have.', story)

minimal_table = [
    [bp('<b>Step</b>', sH2), bp('<b>What to do</b>', sH2), bp('<b>Minimum resources needed</b>', sH2)],
    [bp('1. History'), bp('Listen to the story. Ask: Where did the pain start? Did it move? When did appetite go? Any fever, vomiting? Any chance of pregnancy? Any similar episodes before?'), bp('A calm room. Your ears and attention. Nothing else.')],
    [bp('2. Examination'), bp('Temperature. Check PR (pulse rate) and BP. Palpate gently — find the point of maximum tenderness. Check for rigidity. Test rebound, Rovsing\'s sign, psoas sign, obturator sign. Examine the groin and external genitalia (hernia?).'), bp('A thermometer. BP cuff. Your hands.')],
    [bp('3. Alvarado Score'), bp('Add up the score from history and examination findings. Leucocytosis is the only blood test needed for the score.'), bp('Blood count (FBC) is ideal. If not available, use the clinical score alone (MANTRELS minus L = max 8 points).')],
    [bp('4. Urine dipstick'), bp('Check for blood, leucocytes, nitrites. Positive = consider UTI or ureteric colic. Small abnormalities can be present in appendicitis — do not let this change a strong clinical diagnosis.'), bp('A urine dipstick strip (cheap and available everywhere).')],
    [bp('5. Pregnancy test'), bp('Mandatory in ALL women of reproductive age. If positive — ectopic pregnancy must be excluded before any other management.'), bp('Urine beta-hCG strip (cheap). Or blood beta-hCG if available.')],
    [bp('6. Decision'), bp('Score 1–4: Watch and reassess. Score 5–6: Admit, IV fluids, analgesia, serial exams. Score 7+: Probable appendicitis. If no imaging available and score is high with worsening condition → surgical referral + antibiotics.'), bp('Clinical judgement. A watch (to time serial exams). Paper to document.')],
    [bp('7. Antibiotics'), bp('Start cefuroxime + metronidazole IV or oral ciprofloxacin + metronidazole if IV not available. This buys time and reduces perforation risk.'), bp('Basic antibiotics available in any setting.')],
    [bp('8. Refer for surgery'), bp('If available, refer to surgical team early. Do not wait until the patient is critically ill. Early referral saves lives.'), bp('A phone. A referral letter with clear documented findings.')],
]
story.append(plain_table(minimal_table, [CW*0.08, CW*0.52, CW*0.4]))
story.append(Spacer(1, 8))

story.append(bp('<b>PACES Examination Guide — How to Present Appendicitis in the Exam</b>'))
professor_says('In PACES, you are examined on clinical skills. The examiner is watching HOW you take the history, HOW you examine, and HOW you present your findings. Here is a complete guide.', story)

story.append(bp('<b>PACES History Station — Acute Abdominal Pain</b>'))
paces_hx = [
    '<b>Introduce yourself:</b> "Hello, I am Dr X. I understand you have some abdominal pain. Would it be alright if I asked you a few questions?"',
    '<b>Open question:</b> "Can you tell me about the pain in your own words?"',
    '<b>Site:</b> "Can you point to where the pain is worst now?"',
    '<b>Onset:</b> "When did it start? Did it start suddenly or gradually?"',
    '<b>Character:</b> "What does the pain feel like — sharp, dull, cramping, constant?"',
    '<b>Radiation / Migration:</b> "Has the pain moved anywhere? Did it start in a different place?"',
    '<b>Associated symptoms:</b> "Have you felt sick? Been sick (vomited)? Any fever? Any loss of appetite? Any changes in bowel habit? Any urinary symptoms?"',
    '<b>Timing:</b> "Is the pain constant or does it come and go?"',
    '<b>Exacerbating / Relieving:</b> "Does anything make it worse or better? Movement? Eating? Lying still?"',
    '<b>Severity:</b> "On a scale of 0 to 10 where 10 is the worst pain imaginable, how would you rate it?"',
    '<b>In women:</b> "I need to ask — is there any chance you could be pregnant? When was your last period? Any vaginal discharge or bleeding?"',
    '<b>Past medical history:</b> "Any previous episodes? Any operations before? Any medical conditions?"',
    '<b>Drug history:</b> "Any medications? Any allergies?"',
    '<b>Social history:</b> "Do you smoke or drink alcohol? Any recent travel?"',
]
for pt in paces_hx:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 6))

story.append(bp('<b>PACES Examination Station — Abdominal Examination</b>'))
paces_ex = [
    '<b>Expose:</b> "I would examine the patient properly exposed from nipples to groin, maintaining dignity."',
    '<b>General:</b> Pallor, jaundice, fever (temperature), signs of dehydration (dry mouth, sunken eyes), pain score, position (lying still = peritonism).',
    '<b>Hands:</b> Clubbing, anaemia (palmar pallor), jaundice (palmar erythema), leuconychia (white nails = hypoalbuminaemia).',
    '<b>Face:</b> Eyes — jaundice, anaemia. Mouth — hydration.',
    '<b>Abdomen inspection:</b> Scars (previous surgery). Distension. Movement with breathing (peritonitis = abdomen does not move). Visible peristalsis.',
    '<b>Superficial palpation:</b> Light palpation all 9 areas. Start AWAY from the pain. Look at the patient\'s face, not your hand. Feel for guarding, rigidity.',
    '<b>Deep palpation:</b> Palpate each area again more deeply. Feel for masses. Liver. Spleen. Kidneys.',
    '<b>Specific signs:</b> McBurney\'s point tenderness. Rebound tenderness. Rovsing\'s sign. Psoas sign. Obturator sign. Murphy\'s sign (right upper quadrant — gallbladder). Grey-Turner / Cullen sign (bruising = haemorrhagic pancreatitis).',
    '<b>Percussion:</b> Liver. Spleen. Ascites (shifting dullness). Tympanic (gas) over the bowel.',
    '<b>Auscultation:</b> Bowel sounds — normal, absent (peritonitis/ileus), or high-pitched tinkling (obstruction).',
    '<b>Groin:</b> Herniae. Lymph nodes.',
    '<b>PR examination:</b> "I would offer a PR (rectal) examination if appropriate and consented." Tenderness on the right at the pelvic peritoneum.',
]
for pt in paces_ex:
    story.append(bp(f'• {pt}'))
story.append(Spacer(1, 6))

story.append(bp('<b>PACES Presentation Template</b>'))
story.append(bp('"On examination, this is a 25-year-old male who is in moderate pain, lying still. Temperature is 38.2°C. Heart rate 94. He looks flushed and unwell. There is no jaundice, pallor, or lymphadenopathy. Abdominal examination reveals guarding and maximum tenderness at McBurney\'s point in the right iliac fossa. Rebound tenderness is present at this site. Rovsing\'s sign is positive. There is no rigidity. Bowel sounds are present but reduced. In summary, the findings are consistent with acute appendicitis. I would like to confirm this with an Alvarado score, blood tests (FBC, CRP, U&E), urine dipstick, and pregnancy test in a woman of reproductive age, followed by imaging and surgical referral."'))

memory_hook('PACES: Present findings, give a diagnosis, give a management plan. Never say "I don\'t know what it is." Always have a working diagnosis based on your findings. MRCP examiners want to see clinical reasoning — not just a list of signs.', story)
divider(story)

# ─────────────────────────────────────────────────────────────────────────────
# MASTER MEMORY SUMMARY — GREEN BOX
# ─────────────────────────────────────────────────────────────────────────────
story.append(Spacer(1, 6))
sGrn  = ParagraphStyle('GR',  fontName='DV',   fontSize=8.5, leading=13, textColor=HexColor('#155724'), spaceAfter=0)
sGrnB = ParagraphStyle('GRB', fontName='DV-B', fontSize=10,  leading=15, textColor=HexColor('#155724'), spaceAfter=2)
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
    [Paragraph('MASTER MEMORY SUMMARY — ACUTE APPENDICITIS', sGrnB)],
    [Paragraph('ANATOMY: Appendix hangs from caecum (start of large bowel). McBurney\'s point = 1/3 from ASIS to umbilicus. Blood supply = appendicular artery (branch of ileocolic artery).', sGrn)],
    [Paragraph('PATHOPHYSIOLOGY: 4 stages. 1=Mucosal infection. 2=Transmural infection (all layers). 3=Gangrene (tissue death). 4=Perforation. Each stage is more dangerous.', sGrn)],
    [Paragraph('CLASSIC HISTORY: Central/peri-umbilical pain FIRST → migrates to RIF. Anorexia. Nausea. Low fever. Duration 12–72 hours to presentation.', sGrn)],
    [Paragraph('SIGNS: McBurney\'s tenderness. Rebound. Rovsing\'s. Psoas (retrocaecal). Obturator (pelvic). Rigidity = PERFORATION.', sGrn)],
    [Paragraph('ALVARADO/MANTRELS: Migration+Anorexia+Nausea+Tenderness(x2)+Rebound+Elevated temp+Leucocytosis(x2)+Shift left. Max=10. Score 7+ = probable appendicitis.', sGrn)],
    [Paragraph('INVESTIGATIONS: FBC (WBC raised). CRP (raised). U&E. Urine dip. Pregnancy test (ALL women). USS (women/children). CT (gold standard adults). MRI (pregnancy).', sGrn)],
    [Paragraph('MANAGEMENT: IV fluids + NBM + ANALGESIA (MORPHINE IS SAFE — do NOT withhold). Antibiotics: Cefuroxime + Metronidazole (simple). Tazocin (perforated). Surgery: laparoscopic preferred.', sGrn)],
    [Paragraph('TRIALS: APPAC + CODA = antibiotics alone effective in 70% uncomplicated cases. 30% need surgery within 5 years. Shared decision-making with patient.', sGrn)],
    [Paragraph('TIMING: Perforated + peritonitis = EMERGENCY (theatre within 2 hours). Appendix mass/abscess = antibiotics first, then interval appendicectomy 6–8 weeks later. Uncomplicated = within 24 hours.', sGrn)],
    [Paragraph('SPECIAL GROUPS: Pregnancy = MRI, appendix moves UP, laparoscopic surgery safe. Elderly = atypical, CT always, high perforation/mortality. Children = mesenteric adenitis most common, fast perforation. Retrocaecal = psoas sign.', sGrn)],
    [Paragraph('TUMOURS: Carcinoid most common. <2cm = appendicectomy alone. >2cm = right hemicolectomy. Mucocele rupture = Pseudomyxoma Peritonei. Always send specimen to histology.', sGrn)],
    [Paragraph('DIFF DX: Ectopic pregnancy (CHECK hCG IN ALL WOMEN). Mesenteric adenitis (kids). PID. Ovarian torsion. Ureteric colic. Crohn\'s. Caecal carcinoma (elderly).', sGrn)],
    [Paragraph('MRCP KEY: (1) Opioids SAFE in appendicitis — do NOT withhold. (2) Carcinoid: <2cm = curative with appendicectomy. (3) Pregnancy: MRI preferred. (4) Antibiotics alone = valid option for uncomplicated disease. (5) Mesenteric adenitis = most common RIF pain in children.', sGrn)],
]
innerG = Table(gRows, colWidths=[CW-4])
innerG.setStyle(gTS1)
outerG = Table([[innerG]], colWidths=[CW])
outerG.setStyle(gTSO)
story.append(outerG)
story.append(Spacer(1, 12))

# ─────────────────────────────────────────────────────────────────────────────
# BUILD
# ─────────────────────────────────────────────────────────────────────────────
doc.build(story)
print('SUCCESS: Acute Appendicitis MRCP Note saved to', OUT)
