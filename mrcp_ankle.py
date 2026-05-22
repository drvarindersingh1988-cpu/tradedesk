import io, os
from PIL import Image, ImageDraw, ImageFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

os.makedirs('/mnt/user-data/outputs', exist_ok=True)

FD = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('DV',    FD+'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DV-B',  FD+'DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DV-I',  FD+'DejaVuSansMono-Oblique.ttf'))
pdfmetrics.registerFont(TTFont('DV-BI', FD+'DejaVuSansMono-BoldOblique.ttf'))
registerFontFamily('DV', normal='DV', bold='DV-B', italic='DV-I', boldItalic='DV-BI')

TEAL   = HexColor('#0d5c63'); TEAL_M = HexColor('#1a8a94')
TEAL_L = HexColor('#e0f4f5'); TEAL_XL= HexColor('#f0fafb')
AMBER  = HexColor('#fff3cd'); AMBER_B= HexColor('#e6a817')
GREEN_L= HexColor('#d4edda'); GREEN_D= HexColor('#28a745')
RED_L  = HexColor('#fde8e8'); RED_D  = HexColor('#c0392b')
ORANGE_L=HexColor('#fef3e2'); ORANGE_D=HexColor('#d4640a')
BLUE_L = HexColor('#e8f4fd'); BLUE_D = HexColor('#2471a3')
NAVY   = HexColor('#1a1a2e'); WHITE  = HexColor('#ffffff')

PAGE_W, PAGE_H = A4
MARGIN = 18*mm
CW = PAGE_W - 2*MARGIN

doc = SimpleDocTemplate('/mnt/user-data/outputs/Ankle_Foot_Injuries_Note.pdf',
    pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=MARGIN, bottomMargin=MARGIN)

def S(name, **kw):
    return ParagraphStyle(name, fontName=kw.get('font','DV'),
        fontSize=kw.get('sz',10), leading=kw.get('lead',14),
        textColor=kw.get('color',NAVY), spaceAfter=kw.get('sa',4),
        spaceBefore=kw.get('sb',2), alignment=kw.get('align',0),
        leftIndent=kw.get('li',0))

sTitle = S('T',  font='DV-B', sz=22, color=TEAL,  sa=6, align=1)
sSub   = S('Su', font='DV-I', sz=10, color=TEAL_M,sa=4, align=1)
sH1    = S('H1', font='DV-B', sz=13, color=TEAL,  sa=4)
sH2    = S('H2', font='DV-B', sz=11, color=TEAL_M,sa=3)
sBody  = S('Bo', font='DV',   sz=9,  lead=14,     sa=3)
sBold  = S('Bl', font='DV-B', sz=9,  lead=13,     sa=3)
sSmall = S('Sm', font='DV',   sz=8,  lead=12,     sa=2)
sHook  = S('Hk', font='DV',   sz=9,  lead=14, color=HexColor('#1a5c2a'), sa=0)
sCap   = S('Ca', font='DV-I', sz=8,  lead=11, color=HexColor('#555555'), sa=2, align=1)
sAlert = S('Al', font='DV-B', sz=9,  lead=13, color=RED_D, sa=3)
sImg   = S('Im', font='DV-I', sz=8,  lead=12, color=BLUE_D, sa=2)

def sec_header(title, story):
    story.append(Spacer(1,6))
    story.append(Paragraph(title, sH1))
    story.append(Spacer(1,3))

def divider(story):
    story.append(Spacer(1,4))
    t = Table([['']],colWidths=[CW])
    t.setStyle(TableStyle([('LINEABOVE',(0,0),(0,0),1,TEAL_M),
        ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
    story.append(t)
    story.append(Spacer(1,4))

def plain_table(data, col_widths, alt=True):
    sth = ParagraphStyle('PTH', fontName='DV-B', fontSize=8, leading=11,
        textColor=WHITE, spaceAfter=0, spaceBefore=0)
    std = ParagraphStyle('PTD', fontName='DV', fontSize=7.5, leading=11,
        textColor=NAVY, spaceAfter=0, spaceBefore=0)
    def wrap(cell, is_hdr):
        if isinstance(cell, str):
            return Paragraph(cell.replace('\n', '<br/>'), sth if is_hdr else std)
        return cell
    pdata = [[wrap(c, ri==0) for c in row] for ri, row in enumerate(data)]
    t = Table(pdata, colWidths=col_widths, repeatRows=1)
    base = [
        ('BACKGROUND',(0,0),(-1,0),TEAL),
        ('GRID',(0,0),(-1,-1),0.5,TEAL_M),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
    ]
    if alt: base.append(('ROWBACKGROUNDS',(0,1),(-1,-1),[TEAL_XL, TEAL_L]))
    t.setStyle(TableStyle(base))
    return t

def alert_box(text, story, color=RED_L, border=RED_D):
    t = Table([[Paragraph(text, sAlert)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),color),
        ('BOX',(0,0),(-1,-1),1.5,border),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,4))

def info_box(text, story, color=AMBER, border=AMBER_B):
    t = Table([[Paragraph(text, sBody)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),color),
        ('BOX',(0,0),(-1,-1),1.5,border),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,4))

def image_search_box(term, website, story):
    text = f'IMAGE: Search <b>"{term}"</b> on <b>{website}</b> to visualise this concept.'
    t = Table([[Paragraph(text, sImg)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),BLUE_L),
        ('BOX',(0,0),(-1,-1),1,BLUE_D),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,3))

# ── PIL helpers ──────────────────────────────────────────────────────────────
def pf(sz):
    try: return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', sz)
    except: return ImageFont.load_default()

def pfb(sz):
    try: return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', sz)
    except: return ImageFont.load_default()

def text_size(draw, text, font):
    bb = draw.textbbox((0,0), text, font=font)
    return bb[2]-bb[0], bb[3]-bb[1]

def wrap_text(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ''
    for word in words:
        test = (cur + ' ' + word).strip()
        if text_size(draw, test, font)[0] <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = word
    if cur: lines.append(cur)
    return lines

def arrow_down(draw, cx, y1, y2, color='#555555', w=2, hs=8):
    draw.line([(cx,y1),(cx,y2)], fill=color, width=w)
    draw.polygon([(cx,y2),(cx-hs//2,y2-hs),(cx+hs//2,y2-hs)], fill=color)

def arrow_right(draw, x1, x2, cy, color='#555555', w=2, hs=8):
    draw.line([(x1,cy),(x2,cy)], fill=color, width=w)
    draw.polygon([(x2,cy),(x2-hs,cy-hs//2),(x2-hs,cy+hs//2)], fill=color)

def draw_box(draw, cx, y, lines, border, fill, pad_x=14, pad_y=10, line_gap=5, min_w=160, accent=True):
    line_data = []
    content_w = min_w - 2*pad_x - (6 if accent else 0)
    for text, font, color in lines:
        for wline in wrap_text(draw, text, font, content_w):
            ww, wh = text_size(draw, wline, font)
            content_w = max(content_w, ww)
            line_data.append((wline, font, color, ww, wh))
    box_w = content_w + 2*pad_x + (6 if accent else 0)
    box_h = sum(h for _,_,_,_,h in line_data) + (len(line_data)-1)*line_gap + 2*pad_y
    bx = cx - box_w//2
    draw.rectangle([bx, y, bx+box_w, y+box_h], fill=fill, outline=border, width=2)
    if accent:
        draw.rectangle([bx, y, bx+6, y+box_h], fill=border)
    ty = y + pad_y
    offset = 3 if accent else 0
    for text, font, color, ww, wh in line_data:
        draw.text((cx - ww//2 + offset, ty), text, font=font, fill=color)
        ty += wh + line_gap
    return y + box_h

def img2rl(img, w):
    buf = io.BytesIO(); img.save(buf,'PNG'); buf.seek(0)
    return RLImage(buf, width=w, height=w*img.height/img.width)

# ─────────────────────────────────────────────────────────────────────────────
# DIAGRAM 1 — Lateral Ankle Ligaments
# ─────────────────────────────────────────────────────────────────────────────
def make_diagram1():
    W, H = 900, 650
    img = Image.new('RGB', (W, H), '#f8fbfc')
    draw = ImageDraw.Draw(img)

    # Title
    y = 12
    y = draw_box(draw, W//2, y,
        [('LATERAL ANKLE LIGAMENTS AND SPRAIN GRADES', pfb(16), '#ffffff')],
        '#0d5c63', '#0d5c63', min_w=700, accent=False)
    y += 14

    # Left half: Bones + Ligaments (cx=225)
    cx_l = 225
    y_l = y

    y_l = draw_box(draw, cx_l, y_l,
        [('LATERAL VIEW - RIGHT ANKLE (outer side)', pfb(11), '#ffffff')],
        '#0d5c63', '#1a8a94', min_w=380, accent=False)
    y_l += 10

    # Fibula box
    yf = y_l
    yf = draw_box(draw, cx_l, yf,
        [('FIBULA', pfb(11), '#1a1a2e'),
         ('Thin outer lower leg bone', pf(9), '#1a1a2e'),
         ('Lateral malleolus = bony bump at bottom', pf(9), '#1a1a2e')],
        '#1a8a94', '#e0f4f5', min_w=340)
    yf += 8

    # ATFL box (red/orange) - between fibula front and talus front
    atfl_y = yf
    atfl_y = draw_box(draw, cx_l, atfl_y,
        [('ATFL - Anterior TaloFibular Ligament', pfb(10), '#ffffff'),
         ('MOST COMMONLY TORN LIGAMENT IN HUMAN BODY', pfb(9), '#ffe0e0'),
         ('Runs horizontal: front of fibula -> front of talus', pf(9), '#ffffff'),
         ('Under max stress when foot is plantarflexed+inverted', pf(9), '#ffffff')],
        '#c0392b', '#e74c3c', min_w=340)
    atfl_y += 6

    # Talus box
    talus_y = atfl_y
    talus_y = draw_box(draw, cx_l, talus_y,
        [('TALUS', pfb(11), '#1a1a2e'),
         ('Wedge-shaped ankle bone', pf(9), '#1a1a2e'),
         ('Sits between fibula above, calcaneus below', pf(9), '#1a1a2e'),
         ('No muscle attachments - moved by ligaments only', pf(9), '#333333')],
        '#1a8a94', '#e0f4f5', min_w=340)
    talus_y += 6

    # CFL box (blue)
    cfl_y = talus_y
    cfl_y = draw_box(draw, cx_l, cfl_y,
        [('CFL - Calcaneofibular Ligament', pfb(10), '#ffffff'),
         ('SECOND MOST COMMONLY TORN', pfb(9), '#d0e8ff'),
         ('Runs diagonally down: fibula tip -> calcaneus side', pf(9), '#ffffff'),
         ('Resists inversion across ankle + subtalar joints', pf(9), '#ffffff')],
        '#2471a3', '#2980b9', min_w=340)
    cfl_y += 6

    # Calcaneus box
    calc_y = cfl_y
    calc_y = draw_box(draw, cx_l, calc_y,
        [('CALCANEUS (heel bone)', pfb(11), '#1a1a2e'),
         ('Largest bone in the foot', pf(9), '#1a1a2e'),
         ('Forms the heel', pf(9), '#1a1a2e')],
        '#1a8a94', '#e0f4f5', min_w=340)
    calc_y += 8

    # PTFL box (green)
    ptfl_y = calc_y
    ptfl_y = draw_box(draw, cx_l, ptfl_y,
        [('PTFL - Posterior TaloFibular Ligament', pfb(10), '#1a1a2e'),
         ('RARELY TORN - Strongest lateral ligament', pfb(9), '#1a5c2a'),
         ('At the back of ankle', pf(9), '#1a1a2e'),
         ('Only tears in most severe Grade III injuries', pf(9), '#1a1a2e')],
        '#28a745', '#d4edda', min_w=340)

    # Right half: Sprain grades (cx=675)
    cx_r = 675
    y_r = y

    y_r = draw_box(draw, cx_r, y_r,
        [('LATERAL ANKLE SPRAIN GRADES', pfb(11), '#ffffff')],
        '#0d5c63', '#1a8a94', min_w=380, accent=False)
    y_r += 10

    y_r = draw_box(draw, cx_r, y_r,
        [('GRADE I - MILD', pfb(12), '#1a5c2a'),
         ('Microscopic tears only - ligament stretched but intact', pf(9), '#1a1a2e'),
         ('Mild swelling, no bruising, full weight-bearing', pf(9), '#1a1a2e'),
         ('Anterior drawer: negative', pf(9), '#1a1a2e'),
         ('Return to sport: 1-2 weeks', pfb(9), '#1a5c2a')],
        '#28a745', '#d4edda', min_w=380)
    y_r += 10

    y_r = draw_box(draw, cx_r, y_r,
        [('GRADE II - MODERATE', pfb(12), '#7a3800'),
         ('Partial tear - some fibres torn, some intact', pf(9), '#1a1a2e'),
         ('Moderate swelling + bruising (ecchymosis)', pf(9), '#1a1a2e'),
         ('Weight-bearing painful but possible', pf(9), '#1a1a2e'),
         ('Anterior drawer: mild laxity', pf(9), '#1a1a2e'),
         ('Return to sport: 3-6 weeks', pfb(9), '#7a3800')],
        '#d4640a', '#fef3e2', min_w=380)
    y_r += 10

    y_r = draw_box(draw, cx_r, y_r,
        [('GRADE III - COMPLETE RUPTURE', pfb(12), '#ffffff'),
         ('All fibres torn - complete disruption', pf(9), '#ffffff'),
         ('Severe swelling + significant bruising', pf(9), '#ffffff'),
         ('Cannot weight-bear, haemarthrosis possible', pf(9), '#ffffff'),
         ('Anterior drawer: marked laxity (>10mm)', pf(9), '#ffffff'),
         ('Talar tilt: positive if CFL also torn', pf(9), '#ffffff'),
         ('Return to sport: 6-12 weeks', pfb(9), '#ffe0e0')],
        '#c0392b', '#c0392b', min_w=380)
    y_r += 10

    draw_box(draw, cx_r, y_r,
        [('KEY CLINICAL TESTS:', pfb(10), '#0d5c63'),
         ('Anterior drawer -> ATFL (pull foot forward)', pf(9), '#1a1a2e'),
         ('Talar tilt -> CFL (invert foot firmly)', pf(9), '#1a1a2e'),
         ('Squeeze test -> Syndesmosis (squeeze fibula+tibia)', pf(9), '#1a1a2e'),
         ('Thompson test -> Achilles (squeeze calf)', pf(9), '#1a1a2e')],
        '#1a8a94', '#e0f4f5', min_w=380)

    return img

# ─────────────────────────────────────────────────────────────────────────────
# DIAGRAM 2 — Ottawa Ankle Rules
# ─────────────────────────────────────────────────────────────────────────────
def make_diagram2():
    W, H = 900, 700
    img = Image.new('RGB', (W, H), '#f8fbfc')
    draw = ImageDraw.Draw(img)

    y = 12
    y = draw_box(draw, W//2, y,
        [('OTTAWA ANKLE AND FOOT RULES - When to X-ray', pfb(16), '#ffffff'),
         ('Sensitivity ~100% for fractures - if ALL negative = NO X-ray needed', pf(11), '#e0f4f5')],
        '#0d5c63', '#0d5c63', min_w=750, accent=False)
    y += 18

    # Left column - Ankle rules (cx=225)
    cx_l = 225
    y_l = y

    y_l = draw_box(draw, cx_l, y_l,
        [('ANKLE X-RAY NEEDED IF:', pfb(12), '#ffffff')],
        '#c0392b', '#c0392b', min_w=360, accent=False)
    y_l += 8

    y_l = draw_box(draw, cx_l, y_l,
        [('RULE 1 (Lateral)', pfb(10), '#ffffff'),
         ('Bone tenderness at POSTERIOR 6cm', pf(9), '#ffffff'),
         ('or TIP of LATERAL MALLEOLUS', pf(9), '#ffffff'),
         ('(fibula bottom - outer ankle bump)', pf(9), '#ffe0e0')],
        '#c0392b', '#e74c3c', min_w=360)
    y_l += 8

    y_l = draw_box(draw, cx_l, y_l,
        [('RULE 2 (Medial)', pfb(10), '#ffffff'),
         ('Bone tenderness at POSTERIOR 6cm', pf(9), '#ffffff'),
         ('or TIP of MEDIAL MALLEOLUS', pf(9), '#ffffff'),
         ('(tibia bottom - inner ankle bump)', pf(9), '#ffe0e0')],
        '#c0392b', '#e74c3c', min_w=360)
    y_l += 8

    y_l = draw_box(draw, cx_l, y_l,
        [('RULE 3 (Weight-bearing)', pfb(10), '#ffffff'),
         ('Unable to weight-bear BOTH:', pf(9), '#ffffff'),
         ('(1) Immediately after injury AND', pf(9), '#ffffff'),
         ('(2) Now in the clinic (4 steps)', pf(9), '#ffffff'),
         ('Must be unable to take 4 steps both times', pf(9), '#ffe0e0')],
        '#c0392b', '#e74c3c', min_w=360)
    y_l += 12

    y_l = draw_box(draw, cx_l, y_l,
        [('ALL 3 NEGATIVE?', pfb(11), '#1a5c2a'),
         ('NO X-RAY NEEDED', pfb(12), '#1a5c2a'),
         ('Treat as ligament sprain', pf(9), '#1a1a2e'),
         ('PEACE and LOVE protocol', pf(9), '#1a1a2e'),
         ('Sensitivity ~100% = almost never misses a fracture', pf(8), '#333333')],
        '#28a745', '#d4edda', min_w=360)

    # Right column - Foot rules (cx=675)
    cx_r = 675
    y_r = y

    y_r = draw_box(draw, cx_r, y_r,
        [('FOOT X-RAY NEEDED IF:', pfb(12), '#ffffff')],
        '#d4640a', '#d4640a', min_w=360, accent=False)
    y_r += 8

    y_r = draw_box(draw, cx_r, y_r,
        [('FOOT RULE 1', pfb(10), '#7a3800'),
         ('Bone tenderness at BASE OF 5th METATARSAL', pf(9), '#1a1a2e'),
         ('(outer midfoot - bony prominence)', pf(9), '#1a1a2e'),
         ('Peroneus brevis avulsion fracture most common', pf(9), '#555555')],
        '#d4640a', '#fef3e2', min_w=360)
    y_r += 8

    y_r = draw_box(draw, cx_r, y_r,
        [('FOOT RULE 2', pfb(10), '#7a3800'),
         ('Bone tenderness at NAVICULAR', pf(9), '#1a1a2e'),
         ('(inner midfoot, boat-shaped bone)', pf(9), '#1a1a2e'),
         ('Just in front of ankle on inner side', pf(9), '#555555')],
        '#d4640a', '#fef3e2', min_w=360)
    y_r += 8

    y_r = draw_box(draw, cx_r, y_r,
        [('FOOT RULE 3 (Weight-bearing)', pfb(10), '#7a3800'),
         ('Unable to weight-bear BOTH:', pf(9), '#1a1a2e'),
         ('(1) Immediately after injury AND', pf(9), '#1a1a2e'),
         ('(2) Now in clinic (4 steps)', pf(9), '#1a1a2e')],
        '#d4640a', '#fef3e2', min_w=360)
    y_r += 12

    y_r = draw_box(draw, cx_r, y_r,
        [('IMPORTANT DISTINCTIONS:', pfb(10), '#0d5c63'),
         ('Avulsion fracture (5th MT base styloid) = good prognosis', pf(9), '#1a1a2e'),
         ('Jones fracture (5th MT shaft) = poor blood supply', pf(9), '#1a1a2e'),
         ('Jones = high non-union risk -> may need surgery', pf(9), '#c0392b')],
        '#1a8a94', '#e0f4f5', min_w=360)

    # Bottom box full width
    final_y = max(y_l, y_r) + 18
    draw_box(draw, W//2, final_y,
        [('CRITICAL: Always palpate the ENTIRE fibula up to the knee!', pfb(11), '#ffffff'),
         ('Maisonneuve fracture = proximal fibula fracture + widened ankle mortise from eversion injury', pf(9), '#ffe0e0'),
         ('Missed if you only examine the ankle. Widened medial clear space (>4mm) = unstable = surgery needed.', pf(9), '#ffe0e0'),
         ('Ottawa rules apply to adults and children over 5 years old.', pf(9), '#ffe0e0')],
        '#c0392b', '#8b0000', min_w=820, accent=False)

    final_h = final_y + 110
    img = img.crop((0, 0, W, min(final_h, H)))
    return img

# ─────────────────────────────────────────────────────────────────────────────
# DIAGRAM 3 — PEACE and LOVE Framework
# ─────────────────────────────────────────────────────────────────────────────
def make_diagram3():
    W, H = 900, 800
    img = Image.new('RGB', (W, H), '#f8fbfc')
    draw = ImageDraw.Draw(img)

    y = 12
    y = draw_box(draw, W//2, y,
        [('PEACE and LOVE - Modern Ankle Sprain Treatment (2019)', pfb(16), '#ffffff'),
         ('Dubois & Esculier, British Journal of Sports Medicine, 2019', pf(10), '#e0f4f5'),
         ('Replaced the old RICE protocol - most evidence-based approach', pf(10), '#e0f4f5')],
        '#0d5c63', '#0d5c63', min_w=800, accent=False)
    y += 18

    # Left half: PEACE (cx=225)
    cx_l = 225
    y_l = y

    y_l = draw_box(draw, cx_l, y_l,
        [('PEACE - First 48-72 Hours', pfb(13), '#ffffff')],
        '#c0392b', '#c0392b', min_w=380, accent=False)
    y_l += 8

    boxes_l = [
        ('P = PROTECTION', 'Reduce loading for 1-3 days. Crutches if needed. Prevents further aggravation of torn fibres.'),
        ('E = ELEVATION', 'Raise leg ABOVE heart level. Uses gravity to drain swelling away from ankle toward the body.'),
        ('A = AVOID anti-inflammatory', 'Do NOT aggressively ice or take NSAIDs in first 72h. Inflammation INITIATES healing. Suppressing it may delay repair.'),
        ('C = COMPRESSION', 'Elastic bandage or compression sock. Reduces swelling by increasing external pressure.'),
        ('E = EDUCATION', 'Explain the injury. Set realistic return-to-activity timeline. Encourage active role. Avoid excessive medicalisation.'),
    ]
    colors_l = ['#e74c3c','#c0392b','#e74c3c','#c0392b','#e74c3c']
    fills_l  = ['#fde8e8','#fde8e8','#fde8e8','#fde8e8','#fde8e8']

    for i,(title,desc) in enumerate(boxes_l):
        prev_y = y_l
        y_l = draw_box(draw, cx_l, y_l,
            [(title, pfb(10), '#c0392b'),
             (desc, pf(9), '#1a1a2e')],
            colors_l[i], fills_l[i], min_w=380)
        if i < len(boxes_l)-1:
            arrow_down(draw, cx_l, y_l, y_l+10, color='#c0392b', w=2)
            y_l += 10

    # Right half: LOVE (cx=675)
    cx_r = 675
    y_r = y

    y_r = draw_box(draw, cx_r, y_r,
        [('LOVE - Day 3 Onwards', pfb(13), '#ffffff')],
        '#1a5c2a', '#1a5c2a', min_w=380, accent=False)
    y_r += 8

    boxes_r = [
        ('L = LOAD', 'Gradually increase loading. Walking -> jogging -> running -> sport-specific. Stimulates collagen fibre alignment along lines of stress.'),
        ('O = OPTIMISM', 'Positive mindset improves outcomes. Fear of re-injury leads to movement avoidance which delays recovery. Reassure the patient.'),
        ('V = VASCULARISATION', 'Cardiovascular exercise within days: swimming, cycling. Does not stress ankle. Maintains fitness + promotes blood flow to healing tissue.'),
        ('E = EXERCISE', 'Progressive rehabilitation: range of motion -> strength (peroneals, calf) -> proprioception (balance board) -> return to sport criteria.'),
    ]

    for i,(title,desc) in enumerate(boxes_r):
        y_r = draw_box(draw, cx_r, y_r,
            [(title, pfb(10), '#1a5c2a'),
             (desc, pf(9), '#1a1a2e')],
            '#28a745', '#d4edda', min_w=380)
        if i < len(boxes_r)-1:
            arrow_down(draw, cx_r, y_r, y_r+10, color='#28a745', w=2)
            y_r += 10

    # Bottom comparison box
    final_y = max(y_l, y_r) + 20
    draw_box(draw, W//2, final_y,
        [('EVOLUTION OF TREATMENT PROTOCOLS:', pfb(11), '#0d5c63'),
         ('OLD (1978): RICE = Rest + Ice + Compression + Elevation (complete rest delays healing)', pf(9), '#c0392b'),
         ('NEWER (2012): POLICE = Protection + Optimal Loading + Ice + Compression + Elevation', pf(9), '#d4640a'),
         ('NEWEST (2019): PEACE & LOVE = most evidence-based - some inflammation is NECESSARY for healing', pfb(9), '#1a5c2a'),
         ('"Optimal Loading" means: controlled movement + gentle exercise from Day 1, not complete rest', pf(9), '#1a1a2e')],
        '#1a8a94', '#e0f4f5', min_w=820, accent=False)

    return img

# ─────────────────────────────────────────────────────────────────────────────
# DIAGRAM 4 — Rehabilitation Phases Flowchart
# ─────────────────────────────────────────────────────────────────────────────
def make_diagram4():
    W, H = 900, 1000
    img = Image.new('RGB', (W, H), '#f8fbfc')
    draw = ImageDraw.Draw(img)

    cx = W // 2
    y = 12

    y = draw_box(draw, cx, y,
        [('ANKLE SPRAIN REHABILITATION - Phases and Progression', pfb(16), '#ffffff'),
         ('Grade II-III sprains: 6-12 weeks. Grade I: 1-2 weeks.', pf(10), '#e0f4f5')],
        '#0d5c63', '#0d5c63', min_w=800, accent=False)
    y += 14

    phases = [
        ('#0d5c63', '#e0f4f5',
         'ACUTE PHASE (Days 1-3)',
         ['PEACE protocol: Protection + Elevation + Avoid anti-inflammatory + Compression + Education',
          'Ice for PAIN RELIEF (10-20 min on, 30 min off) - NOT for inflammation suppression',
          'Gentle ankle circles and alphabet exercises within pain-free range',
          'Elevate leg above heart level as much as possible',
          'Crutches if unable to weight-bear comfortably']),
        ('#1a5c2a', '#d4edda',
         'EARLY REHABILITATION (Days 3-14)',
         ['Weight-bearing as tolerated - progress from partial to full weight-bearing',
          'Active range of motion: alphabet exercises (trace A-Z with big toe in air)',
          'Theraband resistance: eversion (foot turns outward) + dorsiflexion exercises',
          'Single-leg balance: 30 seconds, eyes open, flat surface',
          'Gentle calf stretching: straight knee + bent knee (gastrocnemius + soleus)']),
        ('#7a3800', '#fef3e2',
         'STRENGTH AND BALANCE PHASE (Weeks 2-6)',
         ['Calf raises: double leg -> single leg on flat -> single leg on step edge (eccentric)',
          'Wobble board / BOSU ball: proprioception training - progress to eyes closed',
          'Resistance band: 4-way ankle strengthening (all directions)',
          'Side-stepping, lateral band walks, mini-squats',
          'Pain-free jogging in a straight line when single-leg balance >30 seconds']),
        ('#1a3a6e', '#e8f4fd',
         'SPORT-SPECIFIC PHASE (Weeks 6+)',
         ['Change of direction drills: figure of 8, shuttle runs',
          'Plyometrics: two-leg jump landing -> single-leg hop -> reactive jumps',
          'Sport-specific movements: kicking, cutting, side-steps at full speed',
          'Full training session before returning to competitive match play']),
        ('#28a745', '#d4edda',
         'RETURN TO SPORT CRITERIA (all must be met)',
         ['Full pain-free range of motion equal to uninjured side',
          'Single-leg balance duration equal to uninjured side',
          'Single-leg hop test = 90% or more of uninjured side distance',
          'Sport-specific drills completed without pain or giving way',
          'Both player AND clinician are confident to return']),
        ('#c0392b', '#fde8e8',
         'PREVENTION (ongoing after return to sport)',
         ['Proprioception training: 10 minutes wobble board 3x per week - ongoing',
          'Lace-up ankle brace for 6-12 months after Grade II-III sprain',
          'Appropriate footwear: good lateral support, avoid worn soles',
          'Pre-activity warm-up including ankle mobility exercises',
          'Address modifiable risks: strengthen weak peroneals, improve proprioception']),
    ]

    for i, (border, fill, title, items) in enumerate(phases):
        lines = [(title, pfb(11), border)]
        for item in items:
            lines.append(('- ' + item, pf(9), '#1a1a2e'))
        prev_y = y
        y = draw_box(draw, cx, y, lines, border, fill, min_w=780)
        if i < len(phases) - 1:
            arrow_down(draw, cx, y, y+18, color='#0d5c63', w=3, hs=10)
            y += 18

    final_h = y + 10
    img = img.crop((0, 0, W, final_h))
    return img

# ═══════════════════════════════════════════════════════════════════════════
# BUILD STORY
# ═══════════════════════════════════════════════════════════════════════════
story = []

# ── TITLE PAGE ───────────────────────────────────────────────────────────────
story.append(Spacer(1,8))
story.append(Paragraph('ANKLE AND FOOT INJURIES', sTitle))
story.append(Paragraph('Sprains | Ligament Tears | Tendon Injuries | Fractures | Treatment', sSub))
story.append(Paragraph('Anatomy | Physiology | Pathology | Pharmacology | Clinical Management | Examination', sSub))
divider(story)

# ── §1 OVERVIEW ──────────────────────────────────────────────────────────────
sec_header('1. OVERVIEW', story)

story.append(Paragraph(
    'Ankle sprains are the most common musculoskeletal injury in the world — accounting for approximately 25% of all '
    'sports injuries and 1 in every 10,000 people per day in the UK attending A&amp;E with an ankle injury. The ankle is a '
    'complex joint where three bones meet and are held together by numerous ligaments (strong fibrous bands connecting '
    'bone to bone — like tight rubber cables that stop the joint moving too far). When the ankle rolls beyond its '
    'normal range, these ligaments are stretched or torn — this is a sprain.', sBody))

story.append(Paragraph(
    'The vast majority (85%) of ankle sprains are <b>lateral (outer side) sprains</b> — the ankle rolls inward '
    '(<b>inversion</b> — the sole of the foot turns inward) causing damage to the ligaments on the outside of the '
    'ankle. The key question in every ankle injury is: is this just a ligament sprain, or has a bone been broken? The '
    '<b>Ottawa Ankle Rules</b> (a clinical decision tool — a set of simple bedside tests that tell you whether an '
    'X-ray is needed) help make this decision quickly and accurately.', sBody))

story.append(Paragraph(
    'Treatment has evolved significantly. The old approach of complete rest (<b>RICE</b> — Rest, Ice, Compression, '
    'Elevation) has been replaced by early controlled movement and rehabilitation. Modern evidence shows that early '
    'return to activity with appropriate support, combined with physiotherapy and <b>proprioception training</b> '
    '(training the body\'s position-sensing system — proprioception comes from Latin <i>proprius</i> = one\'s own + '
    '<i>capio</i> = to grasp — it is the body\'s ability to sense where it is in space, provided by nerve endings '
    'called <b>mechanoreceptors</b> in ligaments, tendons, and joint capsules), gives the best long-term outcomes and '
    'reduces the risk of <b>chronic ankle instability</b> (ongoing giving-way of the ankle that affects up to 40% of '
    'people after a severe sprain if not properly rehabilitated).', sBody))

divider(story)

# ── §2 ANATOMY ────────────────────────────────────────────────────────────────
sec_header('2. ANATOMY', story)
story.append(Paragraph('The Bones of the Ankle and Foot', sH2))

story.append(Paragraph(
    'The ankle and foot contain <b>26 bones, 33 joints</b>, and over 100 muscles, tendons, and ligaments. '
    'Understanding the key bones and joints is essential for understanding injuries.', sBody))

bones_data = [
    ['Bone', 'Location', 'What It Does / Why It Matters'],
    ['Tibia (shinbone)', 'Main large bone of the lower leg. The medial malleolus (Latin: "small hammer") is the lower end of the tibia — the bony bump on the inner ankle.',
     'Forms the inner (medial) wall of the ankle joint. Fracture of medial malleolus = part of bimalleolar ankle fracture.'],
    ['Fibula', 'Thin bone parallel to tibia on outer (lateral) side. The lateral malleolus is the lower end of the fibula — the outer ankle bump.',
     'Forms the outer (lateral) wall of the ankle joint. Most commonly fractured bone in ankle injuries. Ottawa rules specifically check this bone.'],
    ['Talus', 'Wedge-shaped bone between tibia+fibula above and calcaneus below. Has NO muscle attachments.',
     'The ankle joint (talocrural joint) = tibia + fibula + talus. Talar fractures risk avascular necrosis (bone death) due to very limited blood supply.'],
    ['Calcaneus (heel bone)', 'Largest bone in the foot — forms the heel.',
     'Calcaneal fractures from falls from height ("Don\'t Jump" fracture — axial loading). Associated with spinal compression fractures — always X-ray the spine.'],
    ['Navicular', 'Boat-shaped bone (Latin: navicula = small boat) on the inner midfoot.',
     'Stress fractures common in athletes. Tenderness at navicular = Ottawa foot rules positive. Tibialis posterior tendon attaches here — rupture causes flat foot.'],
    ['Cuboid', 'Cube-shaped bone on the outer midfoot.',
     'Cuboid syndrome (subluxation). Peroneus longus tendon passes under cuboid in a groove.'],
    ['Cuneiforms (3 bones)', 'Inner midfoot in front of navicular — medial, intermediate, lateral.',
     'Lisfranc injury = ligament/fracture complex at tarsometatarsal joints. Easy to miss — check for gap between 1st and 2nd metatarsal bases on X-ray.'],
    ['Metatarsals (5 long bones)', 'Midfoot to forefoot.',
     '5th metatarsal base: peroneus brevis attachment — avulsion fracture very common with inversion sprains. Jones fracture = shaft fracture, worse blood supply, higher non-union risk.'],
    ['Phalanges (14 toe bones)', 'Toes. Great toe = 2 phalanges. Other toes = 3 each.',
     'Fractures common but usually managed conservatively with buddy strapping (taping injured toe to adjacent toe).'],
]
story.append(plain_table(bones_data, [CW*0.18, CW*0.38, CW*0.44]))
story.append(Spacer(1,4))

story.append(Paragraph(
    'The <b>ankle joint itself</b> (talocrural joint — from Latin: talus + crural = relating to the leg) is a '
    '<b>hinge joint</b> — it moves in one plane: <b>dorsiflexion</b> (pulling foot up toward shin) and '
    '<b>plantarflexion</b> (pointing foot down). Normal range: dorsiflexion 20°, plantarflexion 50°. The bony '
    'architecture creates a natural <b>mortise</b> (from carpentry: a socket that grips a tenon — the talus sits in '
    'the mortise formed by tibia and fibula). The mortise is <b>widest at the front</b> — this is why the ankle is '
    'most stable in dorsiflexion and most vulnerable to ligament injury in plantarflexion (when the narrower part of '
    'the talus is in the mortise, leaving more play in the joint).', sBody))

image_search_box('ankle joint bones anatomy tibia fibula talus', 'TeachMeAnatomy.info', story)

story.append(Paragraph('Ligaments of the Ankle', sH2))
story.append(Paragraph(
    'Ligaments connect bone to bone. They are made of <b>dense regular connective tissue</b> — tightly packed '
    'parallel collagen fibres (collagen = the main structural protein of the body, providing tensile strength). '
    'When overstretched, individual fibres tear: <b>Grade I</b> = microscopic, <b>Grade II</b> = partial, '
    '<b>Grade III</b> = complete rupture.', sBody))

ligs_data = [
    ['Ligament', 'Location', 'What It Does', 'Injury Significance'],
    ['ATFL\n(Anterior TaloFibular)', 'Front of lateral malleolus (fibula) to front of talus — nearly horizontal.',
     'Resists forward movement of talus and inversion when foot is plantarflexed.',
     'THE MOST COMMONLY INJURED LIGAMENT IN THE HUMAN BODY. First to tear in lateral ankle sprain. Tested by anterior drawer test.'],
    ['CFL\n(Calcaneofibular)', 'Tip of lateral malleolus downward to side of calcaneus (heel).',
     'Resists inversion across both ankle AND subtalar joints.',
     'Second to tear in lateral sprains. Tested by talar tilt test (invert foot while stabilising lower leg).'],
    ['PTFL\n(Posterior TaloFibular)', 'Back of lateral malleolus to back of talus.',
     'Resists backward movement of talus — the strongest lateral ligament.',
     'Only tears in most severe injuries (Grade III, ATFL + CFL already torn). Rarely injured in isolation.'],
    ['Deltoid ligament', 'Fan-shaped, MEDIAL (inner) side — 4 parts fanning from medial malleolus to talus, navicular, and calcaneus.',
     'Very strong — resists eversion (foot rolling outward) and protects medial ankle.',
     'Rarely torn alone — requires enormous force. Often associated with fibula fracture (Maisonneuve fracture: proximal fibula fracture from eversion).'],
    ['Syndesmosis\n(AITFL + PITFL + interosseous membrane)', 'AITFL: connects lower tibia to lower fibula at front. Interosseous membrane: fibrous sheet between tibia and fibula along entire length.',
     'Hold tibia and fibula together — keep ankle mortise the correct width. Essential for stability.',
     'High ankle sprain from external rotation + dorsiflexion. Longer to heal (6-12 weeks). Tests: squeeze test, external rotation test, Cotton test.'],
    ['Spring ligament\n(plantar calcaneonavicular)', 'From calcaneus to navicular on the sole — under the foot.',
     'Supports head of talus and helps maintain medial longitudinal arch.',
     'Rupture leads to progressive flat foot (pes planus). Associated with tibialis posterior tendon dysfunction.'],
]
story.append(plain_table(ligs_data, [CW*0.16, CW*0.24, CW*0.24, CW*0.36]))
story.append(Spacer(1,4))

image_search_box('ankle lateral ligaments ATFL CFL PTFL diagram', 'Radiopaedia.org', story)
image_search_box('ankle deltoid ligament medial view anatomy', 'Kenhub.com', story)

story.append(Paragraph('Muscles and Tendons of the Ankle', sH2))

tendons_data = [
    ['Tendon / Muscle', 'Location', 'Action', 'Injury'],
    ['Achilles tendon\n(gastrocnemius + soleus)', 'Posterior (back) of ankle. Thickest and strongest tendon in the body — withstands up to 12x body weight during running.',
     'Plantarflexion — essential for walking, running, jumping, tiptoe.',
     'Rupture: "felt like I was kicked from behind" — gap palpable, Thompson test positive. Tendinopathy: posterior heel pain worst in the morning.'],
    ['Peroneus longus + brevis\n(peroneal tendons)', 'Behind the lateral malleolus in a groove, held by peroneal retinaculum.',
     'Eversion and plantarflexion. Peroneus longus also supports the transverse arch.',
     'Tear or subluxation (tendon pops out of groove — snapping on outer ankle). Avulsion fracture of 5th metatarsal base. Peroneal tendinopathy in runners.'],
    ['Tibialis posterior', 'Behind the medial malleolus — deepest muscle of posterior compartment.',
     'Most important dynamic arch support. Inversion of foot.',
     'Tibialis posterior tendon dysfunction (TPTD) — progressive flat foot. "Too many toes" sign. Rupture in middle-aged women.'],
    ['Tibialis anterior', 'Front of lower leg, inserts at medial cuneiform and 1st metatarsal base.',
     'Dorsiflexion + inversion. Lifts foot with each step.',
     'Rupture causes foot drop (cannot dorsiflex). Also from deep peroneal nerve injury.'],
    ['Flexor hallucis longus (FHL)', 'Behind ankle in groove between tubercles of talus.',
     'Flexes big toe — critical for push-off phase of gait.',
     'FHL tendinopathy in ballet dancers. Hallux saltans (triggering of big toe — like trigger finger in the hand).'],
    ['Extensor tendons\n(EDL + EHL)', 'Front of ankle.',
     'Dorsiflexion + toe extension.',
     'Extensor tendinopathy on the dorsum (top) of foot — from tight laces or footwear.'],
]
story.append(plain_table(tendons_data, [CW*0.20, CW*0.23, CW*0.22, CW*0.35]))
story.append(Spacer(1,4))

image_search_box('Achilles tendon anatomy gastrocnemius soleus insertion', 'TeachMeAnatomy.info', story)
image_search_box('peroneal tendons lateral ankle anatomy', 'Radiopaedia.org', story)

divider(story)

# ── §3 PHYSIOLOGY ─────────────────────────────────────────────────────────────
sec_header('3. PHYSIOLOGY', story)

story.append(Paragraph(
    '<b>Movements and Ranges:</b> The ankle complex performs 6 movements — <b>dorsiflexion</b> (20°, talocrural joint), '
    '<b>plantarflexion</b> (50°, talocrural), <b>inversion</b> (35°, subtalar joint — the joint between talus and '
    'calcaneus directly below it), <b>eversion</b> (15°, subtalar), <b>adduction</b> (foot turns inward in horizontal '
    'plane), and <b>abduction</b> (foot turns outward). The combination of inversion + adduction + plantarflexion = '
    '<b>supination</b> (the common ankle sprain position). Eversion + abduction + dorsiflexion = <b>pronation</b>.', sBody))

story.append(Paragraph(
    '<b>Proprioception (body position sensing):</b> The ligaments of the ankle contain <b>mechanoreceptors</b> (nerve '
    'endings that respond to mechanical deformation — stretching, pressure, vibration — like tiny microphones that '
    'detect movement). These send continuous signals to the brain about joint position. After an ankle sprain, the '
    'mechanoreceptors in the torn ligament are damaged → proprioception is lost → the ankle is less stable even '
    'after the ligament heals → this is why <b>re-sprain rate is 40–70% without proper rehabilitation</b>. '
    'Proprioception training (balance exercises on wobble boards, single-leg standing, perturbation training) retrains '
    'the remaining mechanoreceptors to compensate.', sBody))

story.append(Paragraph(
    '<b>The Foot Arch and Weight Distribution:</b> The foot has <b>3 arches</b> (medial longitudinal arch — the main '
    'arch visible from the side; lateral longitudinal arch — along the outer edge; transverse arch — across the ball '
    'of the foot). These arches act as springs — storing and releasing energy with each step, absorbing impact (up to '
    '2.5× body weight during walking, 5× during running). The <b>Windlass mechanism</b>: when the toes are '
    'extended (dorsiflexed), the plantar fascia tightens like a bowstring → raises the arch → supinates the foot '
    '→ stiffens it for push-off. When the plantar fascia is inflamed (<b>plantar fasciitis</b>), the Windlass '
    'mechanism is painful. <b>Pes planus</b> (flat foot) and <b>pes cavus</b> (high arch) are both associated with '
    'abnormal biomechanics and increased injury risk.', sBody))

divider(story)

# ── §4 INJURIES TABLE ─────────────────────────────────────────────────────────
sec_header('4. ANKLE AND FOOT INJURIES — KEY FEATURES', story)

injuries_data = [
    ['Injury', 'Mechanism', 'Structure Injured', 'Key Exam Finding', 'Treatment Summary'],
    ['Grade I lateral sprain', 'Inversion + plantarflexion (ankle rolls inward with foot pointed down)',
     'ATFL stretched, microscopic tears only',
     'Mild swelling + tenderness over ATFL. Full weight-bearing. Stable.',
     'POLICE (first 48-72h) then early mobilisation, physiotherapy. Return to sport 1-2 weeks.'],
    ['Grade II lateral sprain', 'Same mechanism, more force',
     'ATFL partial tear + CFL may be stretched',
     'Moderate swelling, bruising (ecchymosis), tenderness over ATFL and CFL. Some laxity on anterior drawer.',
     'POLICE + brace/air cast. Physiotherapy 2-4 weeks. Return to sport 3-6 weeks.'],
    ['Grade III lateral sprain', 'Same mechanism, severe force',
     'ATFL complete rupture + CFL complete rupture + possible PTFL',
     'Severe swelling, significant bruising, marked laxity on anterior drawer and talar tilt. Possible haemarthrosis.',
     'Functional rehabilitation (NOT cast). Brace. Physio 6-12 weeks. Surgery rarely needed. Return to sport 6-12 weeks.'],
    ['High ankle sprain\n(syndesmotic)', 'External rotation of foot with dorsiflexion — foot planted, body rotates over it',
     'AITFL + PITFL + interosseous membrane',
     'Pain ABOVE ankle (not over malleolus), squeeze test positive, external rotation test positive.',
     'Longer recovery 6-12 weeks. Boot or cast. Surgery if syndesmosis unstable on stress X-ray (diastasis).'],
    ['Medial (deltoid) sprain', 'Forced eversion (foot rolls outward)',
     'Deltoid ligament (one or more of 4 parts)',
     'Pain and tenderness over medial malleolus and deltoid ligament.',
     'Rare in isolation — always consider Maisonneuve fracture (proximal fibula fracture — palpate entire fibula!).'],
    ['Achilles tendon rupture', 'Sudden push-off (sprint start, jump) — often middle-aged "weekend warriors"',
     'Achilles tendon — complete rupture 2-6cm above insertion (watershed zone)',
     'Gap palpable above heel. Thompson test POSITIVE (calf squeeze = foot does NOT move). Cannot tiptoe.',
     'Conservative: functional brace in plantarflexion. OR surgical repair. Both give good outcomes.'],
    ['Peroneal tendon subluxation', 'Sudden dorsiflexion with peroneal contraction — e.g. sudden stop',
     'Peroneal retinaculum tears (strap holding tendons in groove)',
     'Snap/pop on outer ankle. Tenderness behind lateral malleolus. Tendon clicks out of groove on exam.',
     'Conservative if minor. Surgery (retinaculum repair) if recurrent subluxation.'],
    ['Plantar fasciitis', 'Repetitive strain/overuse. Risk: flat feet, high arch, obesity, prolonged standing',
     'Plantar fascia — microtears at calcaneal attachment',
     'Classic: WORST PAIN WITH FIRST STEPS IN MORNING. Tenderness at medial calcaneal tuberosity (inner heel).',
     'Stretching, orthotics, NSAIDs, night splint, corticosteroid injection (max 2 — fat pad atrophy risk), shockwave therapy.'],
    ['Lisfranc injury', 'Indirect: axial load with foot plantarflexed. Direct: crush.',
     'Lisfranc ligament (medial cuneiform to 2nd metatarsal base) + associated structures',
     'Tender at tarsometatarsal joints (midfoot). Gap >2mm between 1st/2nd metatarsal bases on X-ray. Cannot tiptoe.',
     'EASY TO MISS = HIGH MEDICO-LEGAL RISK. Undisplaced: non-weight-bearing cast. Displaced: surgery (ORIF or fusion).'],
    ['5th MT base avulsion', 'Inversion sprain — peroneus brevis pulls off bone fragment',
     'Peroneus brevis avulsion at 5th metatarsal styloid',
     'Tenderness at 5th metatarsal BASE (outer midfoot). Ottawa foot rules positive.',
     'Conservative (boot/cast 4-6 weeks). Distinguish from Jones fracture (shaft — higher non-union risk, may need surgery).'],
]
story.append(plain_table(injuries_data, [CW*0.17, CW*0.17, CW*0.18, CW*0.23, CW*0.25]))
story.append(Spacer(1,4))

divider(story)

# ── §5 PATHOLOGY ──────────────────────────────────────────────────────────────
sec_header('5. PATHOLOGY AND MECHANISM', story)

story.append(Paragraph(
    '<b>At the moment of injury:</b> When the ankle suddenly inverts beyond its normal range — typically landing from '
    'a jump with the foot plantarflexed, or stepping on an uneven surface — the lateral ankle ligaments are placed '
    'under tension greater than their tensile strength. The <b>ATFL fails first</b> because it is the weakest and under '
    'maximum tension in the plantarflexed + inverted position. Collagen fibres tear sequentially: first microscopic '
    '(Grade I), then partial (Grade II), then complete (Grade III). The tear releases a flood of '
    '<b>inflammatory mediators</b>: <b>prostaglandins</b> (from arachidonic acid via COX enzymes — the same pathway '
    'blocked by NSAIDs like ibuprofen), <b>histamine</b> (from mast cells), and <b>cytokines</b> (TNF-alpha, IL-1) '
    '→ swelling (oedema from leaky capillaries), redness (vasodilatation), warmth, and pain (prostaglandins '
    'sensitise pain receptors/nociceptors).', sBody))

story.append(Paragraph(
    '<b>Acute inflammatory phase (0–72 hours):</b> Immediately after injury: bleeding from torn blood vessels '
    '→ haematoma. Inflammatory cells arrive: neutrophils within hours, macrophages within 24–48h. The classic '
    'signs of inflammation: <b>rubor</b> (redness), <b>calor</b> (heat), <b>dolor</b> (pain), <b>tumor</b> (swelling), '
    '<b>functio laesa</b> (loss of function) — are all present. Modern evidence (Bleakley et al., BJSM, 2012) '
    'shows that <b>some inflammation is NECESSARY for healing</b> — it initiates the repair process. Completely '
    'suppressing it with ice and total rest may actually delay healing. This is why the <b>POLICE protocol</b> replaced '
    'RICE — "Optimal Loading" means applying gentle, controlled stress to the healing tissue to stimulate proper '
    'collagen fibre alignment.', sBody))

story.append(Paragraph(
    '<b>The repair phases (days to months):</b> Ligament healing occurs in three overlapping phases: (1) '
    '<b>Inflammatory phase</b>: 0–72 hours. (2) <b>Proliferative phase</b>: day 3 to week 6 — fibroblasts '
    '(fibro = fibre + blast = maker) migrate into the tear and lay down new <b>Type III collagen</b> (weaker, less '
    'organised — like a scar). (3) <b>Remodelling phase</b>: week 6 to 12–18 months — Type III collagen '
    'is gradually replaced by <b>Type I collagen</b> (stronger, better organised) under the influence of mechanical '
    'loading. Without this loading, the fibres remain disorganised and weak — which is why immobilisation in a cast '
    'for Grade II/III sprains produces worse long-term results than functional rehabilitation.', sBody))

story.append(Paragraph(
    '<b>Chronic ankle instability (CAI):</b> Up to 40% of people who suffer a significant lateral ankle sprain '
    'develop CAI — the ankle repeatedly "gives way," particularly on uneven ground. This happens for two reasons: '
    '(1) <b>Mechanical instability</b> — the ligament heals with lax scar tissue → excessive bony movement '
    '(laxity). (2) <b>Functional instability</b> — the mechanoreceptors in the torn ligament are permanently '
    'damaged → proprioception is reduced → the peroneal muscles (dynamic protectors of the lateral ankle) '
    'react more slowly to unexpected inversion stress → the ankle gives way before the muscles can protect it. '
    'Treatment of CAI requires BOTH components: bracing/surgery for mechanical instability, AND intensive '
    'proprioception + peroneal strengthening for functional instability.', sBody))

story.append(Paragraph(
    '<b>Achilles tendon rupture mechanism:</b> The Achilles tendon is most at risk during rapid <b>eccentric loading</b> '
    '— when the calf muscles are trying to contract but the ankle is simultaneously forced into dorsiflexion, '
    'creating a combined tension + stretch force. This typically happens during a sudden explosive push-off (starting '
    'a sprint, jumping, lunging in racket sports). Rupture almost always occurs in the <b>"watershed zone"</b> — '
    '2–6cm above the calcaneal insertion where blood supply is poorest. Predisposing factors: age 30–50 '
    '(tendon degeneration), <b>fluoroquinolone antibiotics</b> (ciprofloxacin, levofloxacin — directly inhibit '
    'collagen synthesis in tenocytes and activate matrix metalloproteinases that break down collagen — a classic '
    'exam question: "patient on ciprofloxacin develops sudden Achilles pain — what is the risk?"), '
    'corticosteroid injections into the tendon, and hyperlipidaemia.', sBody))

divider(story)

# ── §6 CLINICAL FEATURES ──────────────────────────────────────────────────────
sec_header('6. CLINICAL FEATURES', story)
story.append(Paragraph('History — What the Patient Tells You', sH2))

story.append(Paragraph(
    'In clinical practice, always take a structured history: <b>Mechanism</b> (how did it happen? inversion/eversion? '
    'height of fall? sport?), <b>Timing</b> (immediate swelling = haemarthrosis/fracture; delayed swelling = ligament '
    'sprain), <b>Weight-bearing</b> (immediate inability = more serious), <b>Previous injuries</b> (re-sprain on same '
    'ankle = chronic instability?), <b>Occupation/sport</b>, <b>Medications</b> (fluoroquinolones, steroids — '
    'tendon rupture risk), <b>Symptoms</b>: clicking (peroneal subluxation), giving way (instability), locking '
    '(loose body in joint — osteochondral defect = a chunk of cartilage + bone broken off and floating inside).', sBody))

exam_data = [
    ['Test', 'How to Perform', 'Positive Result Means'],
    ['Look (Inspection)', 'Look for swelling (diffuse = ligament sprain; focal = specific tendon/bone), bruising (ecchymosis — pattern reveals what is torn), deformity, alignment, arches.',
     'Bruising below lateral malleolus = ATFL. Bruising at 5th metatarsal base = avulsion fracture. Gross deformity = fracture/dislocation.'],
    ['Feel (Palpation)', 'Systematically palpate: lateral malleolus (tip + posterior 6cm), medial malleolus (tip + posterior 6cm), ATFL (anterior to lateral malleolus), CFL (below lateral malleolus), base of 5th metatarsal, navicular, Achilles tendon (feel for gap), entire fibula up to knee.',
     'Point tenderness on bone = possible fracture (Ottawa rules). Gap in Achilles = rupture. Tenderness over ligament = sprain.'],
    ['Ottawa Ankle Rules', '(1) Bone tenderness at posterior edge or TIP of LATERAL malleolus?\n(2) Bone tenderness at posterior edge or TIP of MEDIAL malleolus?\n(3) Unable to weight-bear (4 steps) both immediately AND now?',
     'ANY positive = X-ray the ankle. Sensitivity ~100% for fractures (almost never misses). Use to RULE OUT fracture.'],
    ['Ottawa Foot Rules', '(1) Bone tenderness at BASE of 5th METATARSAL?\n(2) Bone tenderness at NAVICULAR?\n(3) Unable to weight-bear?',
     'ANY positive = X-ray the foot.'],
    ['Anterior Drawer Test', 'Stabilise lower leg with one hand. Grasp heel with other and pull foot forward (anteriorly) with knee bent 90°.',
     'Excessive forward movement of talus (>3mm more than other side, or >10mm absolute) = ATFL rupture. May feel a "clunk" (suction sign).'],
    ['Talar Tilt Test', 'Stabilise lower leg. Hold heel and tilt foot into inversion (push sole inward).',
     'Excessive inversion angulation (>10° more than other side) = CFL rupture.'],
    ['Thompson Test', 'Patient prone or kneeling on a chair. Squeeze the calf muscle belly firmly.',
     'POSITIVE = foot does NOT plantarflex = Achilles tendon RUPTURED. NEGATIVE = foot plantarflexes = tendon intact.'],
    ['Syndesmosis Squeeze Test', 'Squeeze tibia and fibula together firmly at mid-calf level (NOT at the ankle itself).',
     'Pain at the ankle/syndesmosis = POSITIVE = high ankle sprain (syndesmotic injury).'],
    ['External Rotation Stress Test', 'Hold lower leg, dorsiflex foot, then externally rotate it (turn sole outward).',
     'Pain at syndesmosis = POSITIVE = AITFL injury.'],
    ['Single Heel Rise Test', 'Ask patient to stand on affected leg and rise up onto tiptoe (calf raise).',
     'CANNOT perform = tibialis posterior tendon rupture (cannot raise arch for push-off) OR Achilles tendon rupture.'],
    ['Too Many Toes Sign', 'View patient from BEHIND while they stand naturally.',
     'Seeing more than 2 toes lateral to the heel = foot is abducted = tibialis posterior tendon dysfunction (progressive flat foot).'],
]
story.append(plain_table(exam_data, [CW*0.18, CW*0.44, CW*0.38]))
story.append(Spacer(1,4))

image_search_box('Ottawa ankle rules clinical diagram', 'FOAM-EM.com or Google Images', story)
image_search_box('anterior drawer test ankle examination', 'Physio-Pedia.com', story)
image_search_box('Thompson test Achilles tendon rupture', 'Google Images', story)

divider(story)

# ── §7 INVESTIGATIONS ─────────────────────────────────────────────────────────
sec_header('7. INVESTIGATIONS', story)

inv_data = [
    ['Investigation', 'What It Is', 'When to Order', 'What You Find'],
    ['Plain X-ray\n(ankle series: AP, lateral, mortise)', 'X-ray showing bones only — cannot see ligaments or tendons. Mortise view (ankle rotated 15° internally) is essential for assessing the joint space.',
     'When Ottawa ankle or foot rules are POSITIVE.',
     'Fractures of malleoli, talus, calcaneus. Widened mortise (>4mm medial clear space = syndesmotic disruption = unstable). Avulsion fragment at 5th metatarsal base.'],
    ['MRI\n(Magnetic Resonance Imaging)', 'Gold standard for soft tissue. Uses magnetic fields + radio waves. NO radiation. Excellent for ligaments, tendons, cartilage.',
     'Grade III sprains, suspected Achilles rupture, suspected Lisfranc injury, osteochondral defect, persistent pain after 6 weeks.',
     'Ligament tears (complete vs partial), tendon tears, bone marrow oedema (bruising inside bone visible on MRI but NOT on X-ray), osteochondral lesions.'],
    ['Ultrasound (USS)', 'Uses sound waves. Cheaper and faster than MRI. Portable. Can be done dynamically (watching tendons move in real time).',
     'Achilles tendon (rupture, tendinopathy), peroneal tendons (tears, subluxation), plantar fascia thickness.',
     'Achilles gap (complete rupture), tendon thickening (tendinopathy), peroneal subluxation visible in real-time.'],
    ['CT\n(Computed Tomography)', 'Detailed 3D bone imaging from multiple X-ray angles. Excellent for bones, less good for soft tissue.',
     'Complex fractures (calcaneal fracture for surgical planning), Lisfranc injuries (assess displacement), osteochondral lesions.',
     'Fracture pattern, displacement, articular surface involvement (intra-articular = worse prognosis).'],
    ['Stress X-rays', 'Standard X-rays taken while ankle is stressed (manual inversion/external rotation under image intensifier).',
     'Suspected syndesmotic instability — assess whether fibula and tibia separate under stress.',
     'Tibiofibular diastasis (separation >5mm) = unstable syndesmosis = needs surgery.'],
    ['Bone scan\n(nuclear medicine)', 'Radioactive tracer injected and taken up by areas of high bone turnover (stress reaction or fracture). Detects stress fractures before plain X-ray.',
     'Suspected stress fracture in athlete with normal X-ray (navicular, 5th MT shaft, fibula).',
     '"Hot spot" at site of stress fracture. Very sensitive but less specific than MRI.'],
]
story.append(plain_table(inv_data, [CW*0.18, CW*0.27, CW*0.27, CW*0.28]))
story.append(Spacer(1,4))

image_search_box('ankle MRI ligament tear ATFL', 'Radiopaedia.org', story)
image_search_box('ankle fracture X-ray Ottawa rules', 'Radiopaedia.org', story)

divider(story)

# ── §8 MANAGEMENT ─────────────────────────────────────────────────────────────
sec_header('8. MANAGEMENT AND PRESCRIBING', story)
story.append(Paragraph('PEACE and LOVE — The Modern Evidence-Based Framework (2019)', sH2))

story.append(Paragraph(
    'The most up-to-date evidence-based framework for acute soft tissue injuries is <b>PEACE and LOVE</b> '
    '(Dubois &amp; Esculier, British Journal of Sports Medicine, 2019):', sBody))

story.append(Paragraph(
    '<b>PEACE (first days):</b> <b>P</b>rotection (unload/restrict movement for 1–3 days to prevent aggravation), '
    '<b>E</b>levation (elevate above heart level — gravity drains swelling), <b>A</b>void anti-inflammatory modalities '
    '(avoid aggressive NSAIDs and ice in first 72h — some inflammation is NECESSARY for healing), '
    '<b>C</b>ompression (elastic bandage — reduces swelling), <b>E</b>ducation (explain injury, reassure, set '
    'realistic expectations).', sBody))

story.append(Paragraph(
    '<b>LOVE (subsequent management):</b> <b>L</b>oad (gradually increase loading — early controlled movement '
    'guides collagen alignment), <b>O</b>ptimism (positive mindset improves outcomes — fear of re-injury leads to '
    'movement avoidance which delays recovery), <b>V</b>ascularisation (cardiovascular exercise not stressing ankle — '
    'swimming, cycling — starts within days), <b>E</b>xercise (progressive exercise restoring ROM, strength, and '
    'proprioception before return to sport).', sBody))

info_box('<b>In practice — first 48–72 hours guidance for patients:</b> Protect the ankle (crutches if needed). '
         'Elevate the leg (above hip level when sitting/lying). Gentle compression bandage. Gentle movement within '
         'pain-free range from Day 1. Ice can be used for pain relief (10–20 minutes on, 30 minutes off) but not '
         'excessively. Begin gentle weight-bearing as pain allows.', story)

story.append(Paragraph('Pharmacological Treatment', sH2))

drugs_data = [
    ['Drug', 'Dose', 'Indication', 'Important Cautions'],
    ['Paracetamol\n(acetaminophen)', '1g orally every 4-6 hours, max 4g/day. Reduce to 500mg QDS in elderly, liver disease, or body weight <50kg.',
     'First-line analgesia for all ankle injuries — safe, well-tolerated, no anti-platelet effect so does not worsen bruising.',
     'Hepatotoxicity (liver damage) in overdose. Caution: liver disease, alcohol excess, malnutrition. Often underused — very effective.'],
    ['Ibuprofen\n(NSAID)', '400mg orally TDS with food, max 1.2g/day OTC or 2.4g/day prescribed.',
     'Short-term analgesia + anti-inflammatory after 72h (not in first 72h following PEACE protocol). Helpful for chronic tendinopathy.',
     'AVOID in: renal impairment (reduces renal blood flow → AKI risk), peptic ulcer disease (COX-1 inhibition reduces gastric mucus), cardiovascular disease, asthma (NSAID-sensitive), pregnancy after 30 weeks. Add PPI (omeprazole 20mg OD) if using regularly.'],
    ['Naproxen\n(NSAID)', '250-500mg BD orally with food.',
     'Alternative NSAID — longer acting, twice daily dosing.',
     'Same cautions as ibuprofen. Slightly better cardiovascular profile than diclofenac.'],
    ['Diclofenac', '50mg TDS orally OR topical gel (diclofenac 1% — Voltarol) 3-4x daily to affected area.',
     'Topical diclofenac is effective for acute sprains with lower systemic absorption (less GI and renal risk) than oral NSAIDs.',
     'Oral: same cautions as ibuprofen + higher cardiovascular risk. Topical: much safer systemically but may cause local skin reactions.'],
    ['Codeine', '30-60mg orally every 4-6h, max 240mg/day. Do NOT use in children <12 or breastfeeding.',
     'Short-term severe pain — combined with paracetamol (co-codamol). Not for chronic ankle pain.',
     'Constipation (common — prescribe laxative). Drowsiness, nausea, dependence risk. Pro-drug converted by CYP2D6: poor metabolisers get no analgesia; ultra-rapid metabolisers get morphine toxicity.'],
    ['Corticosteroid injection\n(e.g. triamcinolone 40mg)', 'Injected by trained clinician under ultrasound guidance into specific sites.',
     'Plantar fasciitis (heel injection), peroneal tendinopathy, retrocalcaneal bursitis (inflamed fluid-filled sac at back of heel).',
     'AVOID injecting INTO the Achilles tendon (rupture risk). Limit to 2-3 injections per site per lifetime. Risk: skin depigmentation, fat pad atrophy (permanent, painful).'],
    ['LMWH\n(e.g. enoxaparin 40mg SC daily)', 'Subcutaneous injection — usually by patient self-injection.',
     'DVT prophylaxis when limb is immobilised in a cast or boot, particularly in patients with additional risk factors.',
     'Monitor platelets (HIT — Heparin-Induced Thrombocytopenia — rare but serious immune reaction). Renal dose adjustment required. Teach patient injection technique.'],
]
story.append(plain_table(drugs_data, [CW*0.16, CW*0.20, CW*0.26, CW*0.38]))
story.append(Spacer(1,4))

alert_box('FLUOROQUINOLONES (ciprofloxacin, levofloxacin) + TENDONS: Stop the antibiotic immediately if the patient '
          'develops tendon pain while on a fluoroquinolone. These drugs inhibit collagen synthesis in tenocytes and '
          'activate collagen-degrading enzymes (MMPs). The Achilles tendon is most commonly affected. Risk is increased '
          'by: age, concurrent corticosteroids, renal impairment. This is a well-known drug interaction and a '
          'common exam question.', story)

story.append(Paragraph('Physiotherapy and Rehabilitation', sH2))

story.append(Paragraph(
    '<b>Grade I sprain:</b> Active range of motion (AROM) exercises from day 1 (alphabet exercises — trace the '
    'alphabet in the air with the big toe to move ankle through all ranges), weight-bearing as tolerated, '
    'proprioception exercises (single-leg standing — progress to eyes closed, then on foam/wobble board), '
    'return to sport when pain-free and equal proprioception to other side (typically 1–2 weeks).', sBody))

story.append(Paragraph(
    '<b>Grade II–III sprain:</b> Phase 1 (week 1–2): PEACE + LOVE protocol, gentle AROM, crutches if needed, '
    'compression brace or lace-up ankle support. Phase 2 (week 2–6): Strengthening — peroneal eversion '
    'exercises using resistance band (theraband), calf raises, tibialis anterior strengthening; balance training '
    '(wobble board, BOSU ball). Phase 3 (week 6+): Sport-specific training, plyometrics (explosive jumping and '
    'landing exercises), return to sport when: pain-free, full ROM, single-leg balance equal to other side, '
    'can complete sport-specific drills without pain or giving way.', sBody))

story.append(Paragraph(
    '<b>Achilles tendon management:</b> <b>Alfredson protocol</b> (most evidence-based physiotherapy for Achilles '
    'tendinopathy): stand on a step, go up on tiptoe on the good leg, then lower slowly and controlled on the '
    'AFFECTED leg only (eccentric loading = muscle working while lengthening) — 3 sets of 15 reps twice daily, '
    '12 weeks. This stimulates collagen remodelling. For Achilles rupture — <b>functional bracing protocol</b>: '
    'boot with heel wedges (maintaining plantarflexion, reducing tension on torn tendon), progressively reduce '
    'heel wedges over 8–12 weeks while tendon heals, then physiotherapy.', sBody))

story.append(Paragraph('Surgical Options', sH2))
story.append(Paragraph(
    'Most ankle sprains are treated non-operatively. Surgery is considered for: Grade III ATFL + CFL rupture '
    'with persistent chronic instability after adequate rehabilitation (<b>Brostrom procedure</b> — lateral '
    'ankle ligament reconstruction, where the torn ATFL is tightened/imbricated and reattached to the fibula; '
    'Gould modification adds extensor retinaculum reinforcement); syndesmotic instability (screw or tightrope '
    'fixation of the syndesmosis); ankle fractures (<b>ORIF</b> — Open Reduction Internal Fixation); Achilles '
    'rupture in young athletes (surgical repair gives lower re-rupture rate but higher complication rate — '
    'DVT, wound infection, sural nerve injury).', sBody))

divider(story)

# ── §9 DIAGRAMS ───────────────────────────────────────────────────────────────
sec_header('9. ANATOMICAL AND CLINICAL DIAGRAMS', story)

story.append(Paragraph('Diagram 1: Lateral Ankle Ligaments and Sprain Grades', sH2))
d1 = make_diagram1()
story.append(img2rl(d1, CW))
story.append(Paragraph('Lateral ankle ligament anatomy (ATFL, CFL, PTFL) and the three grades of sprain with clinical features.', sCap))
story.append(Spacer(1,8))

story.append(Paragraph('Diagram 2: Ottawa Ankle and Foot Rules', sH2))
d2 = make_diagram2()
story.append(img2rl(d2, CW))
story.append(Paragraph('Ottawa rules for deciding whether to X-ray ankle and foot injuries. Sensitivity ~100% for fractures.', sCap))
story.append(Spacer(1,8))

story.append(Paragraph('Diagram 3: PEACE and LOVE Treatment Framework', sH2))
d3 = make_diagram3()
story.append(img2rl(d3, CW))
story.append(Paragraph('Modern evidence-based approach to acute ankle sprain treatment (Dubois & Esculier, BJSM 2019).', sCap))
story.append(Spacer(1,8))

story.append(Paragraph('Diagram 4: Rehabilitation Phases Flowchart', sH2))
d4 = make_diagram4()
story.append(img2rl(d4, CW))
story.append(Paragraph('Phase-by-phase rehabilitation progression from acute injury to return to sport, with return-to-sport criteria.', sCap))
story.append(Spacer(1,8))

divider(story)

# ── §10 CROSS-SUBJECT TABLE ────────────────────────────────────────────────────
sec_header('10. CROSS-SUBJECT CONNECTIONS', story)

cross_data = [
    ['Subject', 'What This Topic Teaches', 'Key Clinical Concept'],
    ['Anatomy', '26 bones of ankle/foot, 3 arches, lateral ligaments (ATFL, CFL, PTFL), medial deltoid, syndesmosis, Achilles, peroneal tendons, tibialis posterior.',
     'ATFL = most commonly injured ligament in the human body. Mortise view X-ray shows talar-malleolus gaps. Lateral malleolus is lower than medial — foot naturally inverts under gravity.'],
    ['Physiology', 'Ankle movements (dorsiflexion/plantarflexion at talocrural; inversion/eversion at subtalar), proprioception via mechanoreceptors, foot arches as energy-storing springs, Windlass mechanism.',
     'Proprioception loss after ankle sprain = functional instability. Peroneal reaction time increases by ~80ms after ATFL tear — explains why ankle gives way before muscles can protect it.'],
    ['Biochemistry', 'Collagen synthesis (fibroblasts, Type I vs III collagen), prostaglandin pathway (arachidonic acid → COX-1/COX-2 → prostaglandins → pain, swelling), collagen maturation timeline.',
     'NSAIDs block COX → reduce prostaglandins → pain relief but also reduce healing signal in first 72h. Fluoroquinolones inhibit collagen synthesis in tenocytes → Achilles rupture risk.'],
    ['Pathology', 'Ligament tear grades (I-II-III), acute inflammation phases, 3-phase collagen remodelling, chronic ankle instability, avascular necrosis risk (talus, Jones fracture), haemarthrosis.',
     'Jones fracture (5th metatarsal shaft) has poor blood supply = high non-union risk. Calcaneal fracture from height = check spine (axial force transmitted up through skeleton).'],
    ['Pharmacology', 'NSAIDs (COX-1/COX-2 inhibition), paracetamol, codeine (CYP2D6 conversion), corticosteroids (tendon rupture risk), LMWH (DVT prophylaxis), fluoroquinolone-tendon interaction.',
     'Ibuprofen + renal impairment = AKI (NSAIDs block prostaglandin-mediated renal vasodilation). Corticosteroid injection INTO Achilles tendon = rupture risk (never do this).'],
    ['Radiology', 'Ottawa rules (reduce radiation), AP/lateral/mortise X-ray views, MRI for soft tissue, USS for tendons, CT for complex fractures, bone scan for stress fractures.',
     'Mortise view: the key ankle X-ray. Normal mortise space = uniform 4mm gap between talus and each malleolus. If medial gap >4mm = syndesmotic disruption.'],
    ['Emergency Medicine', 'Ottawa ankle and foot rules, haemarthrosis aspiration, ankle dislocation reduction (neurovascular emergency), Lisfranc injury (easy to miss = medico-legal risk), compartment syndrome.',
     'Ankle dislocation = neurovascular emergency. Check dorsalis pedis + posterior tibial pulse + sensation before and after any manipulation.'],
    ['Orthopaedics/Surgery', 'ORIF indications, Brostrom procedure for chronic lateral ankle instability, syndesmotic screw/tightrope, Achilles surgical repair vs functional bracing, calcaneal fracture ORIF.',
     'Brostrom = lateral ankle ligament reconstruction. Ligament is imbricated (shortened) and reattached to fibula. Gould modification adds extensor retinaculum reinforcement.'],
    ['Physiotherapy', 'PEACE and LOVE protocol, Alfredson eccentric loading for Achilles tendinopathy, rehabilitation phases, proprioception training, return-to-sport criteria, hop tests.',
     'Alfredson protocol = eccentric heel drops on step. 3x15 reps BD x12 weeks. Strongest evidence for mid-portion Achilles tendinopathy.'],
    ['Rheumatology', 'Gout (monosodium urate crystals, 1st MTP joint = podagra), pseudogout (calcium pyrophosphate, ankle/knee), reactive arthritis (Reiter: arthritis + urethritis + uveitis), seronegative spondyloarthropathies (Achilles enthesopathy in ankylosing spondylitis).',
     'Gout: hyperuricaemia → urate crystals → acute inflammation → colchicine or indomethacin acutely, allopurinol (xanthine oxidase inhibitor) for prevention. Ankylosing spondylitis = HLA-B27 + bilateral sacroiliitis + Achilles enthesitis.'],
    ['Dermatology', 'Bruising patterns, diabetic foot skin breakdown, pressure sores from cast/boot, contact dermatitis from tape, blistering.',
     'Diabetic foot = peripheral neuropathy (no protective sensation) + peripheral vascular disease (poor healing) + immunocompromise. Charcot neuroarthropathy = massive joint destruction in diabetic neuropathy.'],
    ['Diabetes/Endocrinology', 'Diabetic peripheral neuropathy, Charcot foot (neuroarthropathy), ABI (ankle-brachial index), Wagner classification of diabetic foot ulcers, multidisciplinary diabetic foot team.',
     'ABI = ankle systolic BP / brachial systolic BP. Normal >1.0. <0.9 = PAD. <0.5 = severe PAD = critical limb ischaemia. Measured with hand-held Doppler probe.'],
    ['Paediatrics', 'Salter-Harris fractures (growth plate injuries in children — 5 types), Sever\'s disease (calcaneal apophysitis in 8-14yr old boys), tarsal coalition (abnormal bony fusion → rigid flat foot in adolescent).',
     'Salter-Harris: Type I = through growth plate only (X-ray may look normal — clinical diagnosis); Type II = growth plate + metaphysis (most common); Type V = crush (worst). Mnemonic: SALTR.'],
    ['Sports Medicine', 'Extrinsic risk factors (training errors, footwear, surface), intrinsic risk factors (previous sprain, weak peroneals, hyperlaxity — Beighton score), return-to-sport criteria, taping, stress fractures.',
     'Beighton score (generalised hypermobility): 9 points (little finger hyperextension x2, thumb to forearm x2, elbow hyperextension x2, knee hyperextension x2, palms flat on floor). Score >4/9 = hypermobility syndrome.'],
]
story.append(plain_table(cross_data, [CW*0.16, CW*0.47, CW*0.37]))
story.append(Spacer(1,4))

divider(story)

# ── §11 ANALOGIES ─────────────────────────────────────────────────────────────
sec_header('11. ANALOGIES FOR UNDERSTANDING', story)

analogies_data = [
    ['Concept', 'Plain-Language Analogy'],
    ['ATFL (most commonly sprained ligament)',
     'The ATFL is like the handbrake cable of a bicycle — when the wheel suddenly twists the wrong way, this thin cable takes all the tension first and snaps before the thicker frame structures.'],
    ['Ligament sprain grades',
     'Think of a ship\'s mooring rope: Grade I = a few threads fraying (still holds the ship). Grade II = half the rope torn (ship wobbles at the dock). Grade III = complete snap (ship drifts free — the joint has nothing holding it).'],
    ['Proprioception loss after sprain',
     'Imagine driving a car with the steering feedback removed — you can still turn the wheel but cannot feel what the road surface is doing. Ankle proprioception loss = the automatic balancing system is gone — the ankle "gives way" on uneven ground before the muscles can react.'],
    ['Collagen remodelling',
     'Healing collagen is like papier-mache drying — initially wet and flexible (Type III, weak), gradually hardening into its final shape (Type I, strong). Physiotherapy = moulding it correctly while it sets. Immobilisation = it dries in the wrong shape.'],
    ['Ottawa rules',
     'Like a security check at an airport — Ottawa rules only flag you for a full scan (X-ray) if specific trigger points are positive. Negative Ottawa = cleared quickly without radiation. Sensitivity ~100% = almost never misses a fracture.'],
    ['Achilles tendon watershed zone',
     'The watershed zone (2-6cm above the heel) is like a remote farmhouse at the end of a long track — furthest from the main blood supply road. When overloaded (overuse/fluoroquinolones) or supply is poor (vascular disease), this is the first place to fail.'],
]
story.append(plain_table(analogies_data, [CW*0.25, CW*0.75]))
story.append(Spacer(1,4))

divider(story)

# ── §12 DIAGRAM REFERENCES ────────────────────────────────────────────────────
sec_header('12. CLINICAL DECISION FLOWCHARTS (see Diagrams above)', story)
story.append(Paragraph(
    'Refer to <b>Diagram 2</b> (Ottawa Ankle and Foot Rules) for the decision flowchart on when to X-ray ankle '
    'injuries. Refer to <b>Diagram 4</b> (Rehabilitation Phases) for the step-by-step progression from acute injury '
    'to return to sport. Refer to <b>Diagram 3</b> (PEACE and LOVE) for the evidence-based treatment framework.', sBody))

divider(story)

# ── §13 EXAM TRIGGERS ─────────────────────────────────────────────────────────
sec_header('13. EXAM TRIGGERS — 12 CLINICAL SCENARIOS', story)

triggers = [
    ('A 25-year-old footballer inverts his right ankle during a match. Swelling over lateral ankle. He can walk 4 steps but is limping. Tenderness at ATFL only — not at malleolus tips or 5th metatarsal base. Does he need an X-ray?',
     'NO. Ottawa ankle rules are NEGATIVE: no tenderness at posterior 6cm or tip of either malleolus, and he CAN weight-bear. No foot rules positive either. Diagnosis = Grade II lateral ankle sprain (ATFL). Manage with PEACE and LOVE, ankle brace, physiotherapy. No radiation required.'),

    ('A 45-year-old woman started on ciprofloxacin for a UTI. She develops sudden severe pain in her left ankle while walking. Examination shows a palpable gap 4cm above the heel. Thompson test positive.',
     'Achilles tendon rupture, precipitated by ciprofloxacin (fluoroquinolone). Classic: gap palpable above heel, Thompson test positive (squeeze calf — foot does not move). Mechanism: fluoroquinolones inhibit collagen synthesis in tenocytes and activate collagen-degrading MMPs. Management: functional brace (plantarflexion) vs surgical repair. Stop the antibiotic. Warn patients on fluoroquinolones of tendon rupture risk.'),

    ('A 30-year-old marathon runner has 6 weeks of gradually worsening midfoot pain, worse when running. X-ray is normal. Ottawa rules are positive for navicular tenderness. What investigation confirms the diagnosis and what is the treatment?',
     'Navicular stress fracture. Normal X-ray does NOT exclude stress fracture. MRI (gold standard — shows bone marrow oedema and fracture line) or bone scan. Treatment: non-weight-bearing cast for 6-8 weeks (navicular has poor blood supply — poor healing if loaded). High non-union risk if missed. Return to running only after imaging confirms healing.'),

    ('An 18-year-old twists his ankle playing basketball. He has severe swelling and bruising. Tenderness on palpating the entire fibula — including at the level of the knee. His ankle X-ray shows widening of the medial clear space (gap between medial malleolus and talus = 6mm). What is the diagnosis?',
     'Maisonneuve fracture — proximal fibula fracture (near the knee) with syndesmotic disruption at the ankle. The eversion/external rotation force travels up the interosseous membrane and breaks the fibula at its proximal neck. Medial clear space >4mm = unstable ankle mortise = surgical stabilisation of the syndesmosis required. KEY: always palpate the ENTIRE fibula in ankle injuries. Request proximal fibula X-ray if medial clear space is widened.'),

    ('A 55-year-old woman has 3 months of pain on the inner ankle, worse on standing. From behind, you notice excessive pronation and 3 toes visible beyond her heel on the right side. She cannot do a single heel raise on the right. What is the diagnosis?',
     'Tibialis posterior tendon dysfunction (TPTD) — progressive failure of the main dynamic arch support. Too many toes sign (>2 toes visible from behind) = foot is abducted = arch collapsed. Cannot single heel rise = tendon is not working. MRI confirms diagnosis. Early disease: orthotic insoles + physiotherapy. Late (complete rupture with rigid flat foot): surgery (tendon transfer + calcaneal osteotomy to rebuild arch).'),

    ('A 60-year-old diabetic man with peripheral neuropathy injures his foot but reports minimal pain. The foot looks hot, red, and massively swollen. X-ray shows fragmentation and subluxation of multiple midfoot bones. What is this condition?',
     'Charcot neuroarthropathy (Charcot foot). Peripheral neuropathy = no pain sensation = patient continues walking on a seriously fractured foot → progressive joint destruction. Autonomic neuropathy causes increased blood flow to foot → bone resorption + fragmentation. Treatment: total contact casting (non-weight-bearing, specially moulded to distribute pressure), until acute phase resolves (foot no longer hot). High risk of ulceration, infection, amputation without proper management.'),

    ('A patient steps off a curb and inverts his ankle. X-ray shows an avulsion fragment at the base of the 5th metatarsal. How do you differentiate between an avulsion fracture and a Jones fracture, and why does it matter?',
     'Avulsion fracture = at the STYLOID (very tip of 5th metatarsal base) where peroneus brevis attaches. Good blood supply = heals well conservatively (boot or firm shoe 4-6 weeks). Jones fracture = at the PROXIMAL SHAFT (metaphyseal-diaphyseal junction, just distal to the tuberosity). Poor blood supply = high non-union and re-fracture risk. Athletes: intramedullary screw fixation recommended. Distinction made on X-ray by exact location of fracture line relative to the tuberosity.'),

    ('A 35-year-old rugby player has had 3 ankle sprains in 2 years on the same ankle. Ankle "gives way" on uneven ground. MRI shows ATFL and CFL tears with lax scar tissue. Conservative physiotherapy has failed for 6 months. What is the next management step?',
     'Surgical lateral ankle ligament reconstruction — Brostrom procedure (anatomic repair: ATFL and CFL are imbricated/shortened and reattached to their fibular origin). Gould modification adds extensor retinaculum reinforcement. This addresses mechanical instability. Functional instability (proprioception) is addressed with intensive post-operative physiotherapy. Success rate approximately 85-90%.'),

    ('An elderly woman on warfarin falls and sustains a bimalleolar ankle fracture. Her INR is 3.5. What additional considerations are there?',
     'Anticoagulation management before surgery: warfarin reversal (vitamin K + fresh frozen plasma if emergency). Bone healing: anticoagulation does not significantly impair bone healing but increases haematoma risk. DVT prophylaxis: already anticoagulated — ensure therapeutic during immobilisation. Assess cause of fall (osteoporosis, cardiac arrhythmia, syncope, polypharmacy). Post-fracture bone protection: calcium + vitamin D, DEXA scan for osteoporosis, bisphosphonate if indicated. Warfarin interactions with surgical drugs.'),

    ('A 28-year-old woman has heel pain worst with the first steps in the morning. It improves after 10 minutes of walking then worsens after prolonged standing. Tenderness at the medial calcaneal tuberosity. What is the diagnosis and treatment?',
     'Plantar fasciitis — inflammation/degeneration of the plantar fascia at its calcaneal attachment. Classic history: first-step pain (plantar fascia shortens overnight → sudden stretch on first step). Treatment ladder: (1) calf + plantar fascia stretching 3x daily; (2) orthotic insoles (heel cups); (3) avoid barefoot walking; (4) NSAIDs (ibuprofen 400mg TDS with food); (5) night splint; (6) corticosteroid injection if fails (max 2 — fat pad atrophy risk); (7) shockwave therapy (ESWT); (8) surgery last resort (plantar fascia release).'),

    ('A 22-year-old male presents with midfoot pain after a road traffic accident. X-ray shows subtle widening between the 1st and 2nd metatarsal bases. He can barely weight-bear. What diagnosis must you exclude and why?',
     'Lisfranc injury — fracture-dislocation at the tarsometatarsal (Lisfranc) joint complex. EASY TO MISS — only ~50% detected on initial plain X-ray. Key sign: gap >2mm between base of 1st and 2nd metatarsal = Lisfranc ligament disruption. CT scan for confirmation and surgical planning. If missed: patient weight-bears on unstable midfoot → permanent collapse → chronic midfoot arthritis → severe disability. HIGH MEDICO-LEGAL RISK. Treatment: undisplaced = non-weight-bearing cast 6-8 weeks; displaced = ORIF or primary arthrodesis.'),

    ('Fluoroquinolone antibiotics and tendon rupture — explain the mechanism and what you should tell patients.',
     'Fluoroquinolones (ciprofloxacin, levofloxacin, moxifloxacin) have a class effect on tendons. Mechanism: (1) chelate magnesium ions from tenocytes → impairs mitochondrial function → reduces collagen synthesis; (2) activate MMPs (matrix metalloproteinases) that break down collagen matrix; (3) increase oxidative stress in tendon tissue. Achilles most commonly affected but also peroneal, rotator cuff, patellar tendons. Risk higher with: age, concurrent corticosteroids, renal impairment (drug accumulates), previous tendon disease. MHRA guidance: stop fluoroquinolone immediately if tendon pain develops. Always counsel patients before prescribing.'),
]

for i, (q, a) in enumerate(triggers):
    tdata = [
        [Paragraph(f'<b>Scenario {i+1}:</b> {q}',
                   ParagraphStyle('QS', fontName='DV-B', fontSize=8.5, leading=12, textColor=HexColor('#1a1a2e')))],
        [Paragraph(f'<b>Answer:</b> {a}',
                   ParagraphStyle('AS', fontName='DV', fontSize=8, leading=12, textColor=HexColor('#1a1a2e')))]
    ]
    t = Table(tdata, colWidths=[CW])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),TEAL_XL),
        ('BACKGROUND',(0,1),(-1,1),AMBER),
        ('BOX',(0,0),(-1,-1),1,TEAL_M),
        ('GRID',(0,0),(-1,-1),0.5,TEAL_M),
        ('TOPPADDING',(0,0),(-1,-1),5),
        ('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),8),
        ('RIGHTPADDING',(0,0),(-1,-1),8),
    ]))
    story.append(t)
    story.append(Spacer(1,5))

divider(story)

# ── §14 CLINICAL EXAMINATION ──────────────────────────────────────────────────
sec_header('14. CLINICAL EXAMINATION TIPS AND PACES', story)
story.append(Paragraph('Examining the Ankle — Step by Step', sH2))

exam_steps = [
    ['Step', 'What to Do', 'What to Look/Feel For'],
    ['1 - Expose and compare', 'Expose both lower legs and feet. Ask patient to stand initially if possible. Compare both ankles side by side.',
     'Swelling (diffuse vs localised), bruising (and pattern), deformity, alignment, arches (flat foot/high arch), muscle wasting (chronic).'],
    ['2 - Gait', 'Ask patient to walk away and back. Then walk on heels (tests tibialis anterior/dorsiflexors), then on tiptoes (tests calf/plantarflexors and tibialis posterior).',
     'Antalgic gait (shortened stance phase on painful side). Foot drop (cannot dorsiflex — foot slaps on ground). Inability to tiptoe = tibialis posterior or Achilles pathology.'],
    ['3 - Look from behind', 'Patient stands facing away. Observe heel alignment (valgus = tilted outward; varus = inward). Count toes visible lateral to heel.',
     '>2 toes visible lateral to heel = "too many toes" sign = tibialis posterior dysfunction + flat foot (foot is abducted).'],
    ['4 - Systematic palpation', 'Palpate: medial malleolus tip + posterior 6cm. Lateral malleolus tip + posterior 6cm. ATFL (anterior to lateral malleolus). CFL (below lateral malleolus). 5th metatarsal base. Navicular. Achilles tendon (full length — feel for gap). Plantar heel (calcaneal tuberosity). Entire fibula up to knee.',
     'Point tenderness on bone = Ottawa positive = X-ray. Gap in Achilles = rupture. ATFL tenderness = lateral sprain. Plantar heel tenderness = plantar fasciitis.'],
    ['5 - Range of motion', 'Passive and active: dorsiflexion (normal 20 degrees), plantarflexion (50 degrees), inversion (35 degrees), eversion (15 degrees). Assess subtalar motion separately.',
     'Reduced ROM — is it painful throughout or only at end-range? Stiffness after ankle fracture or arthritis.'],
    ['6 - Special tests', 'Anterior drawer (ATFL), talar tilt (CFL), Thompson (Achilles), squeeze test (syndesmosis), external rotation test (syndesmosis), single heel rise (tibialis posterior + Achilles).',
     'See Sections 6 and 8 above for full interpretation of each test result.'],
    ['7 - Neurovascular assessment', 'Palpate dorsalis pedis pulse (dorsum of foot between 1st and 2nd metatarsal bases) and posterior tibial pulse (behind and below medial malleolus). Test light touch + pin-prick sensation. Capillary refill (press toenail — normal: pink return <2 seconds).',
     'Absent pulses + reduced sensation = peripheral vascular disease + neuropathy. ALWAYS check in elderly and diabetic patients. Check BEFORE and AFTER manipulation of any fracture/dislocation.'],
]
story.append(plain_table(exam_steps, [CW*0.18, CW*0.42, CW*0.40]))
story.append(Spacer(1,6))

story.append(Paragraph('<b>Video Resources — Search These Exact Terms:</b>', sH2))
video_resources = [
    '"Geeky Medics ankle examination OSCE" on YouTube — full structured ankle examination',
    '"Geeky Medics Ottawa ankle rules" on YouTube — how to apply the rules clinically',
    '"Thompson test Achilles tendon rupture examination" on YouTube — demonstration',
    '"anterior drawer test ankle" on YouTube — how to test ATFL laxity',
    '"ATFL CFL PTFL ankle anatomy 3D" on YouTube — 3D animated anatomy of lateral ankle ligaments',
    '"Alfredson protocol eccentric heel drops Achilles tendinopathy" on YouTube — exact exercise technique',
    '"plantar fasciitis stretching exercises" on YouTube — the specific stretches to teach patients',
    '"Charcot foot diabetic neuropathy X-ray" on Radiopaedia.org — classic imaging appearance',
    '"Lisfranc injury X-ray subtle signs" on Radiopaedia.org — how not to miss it',
    '"ankle MRI ligament anatomy" on Radiopaedia.org — normal and torn ligaments on MRI',
]
for v in video_resources:
    story.append(Paragraph('• ' + v, sBody))

divider(story)

# ── §15 MEMORY HOOK ───────────────────────────────────────────────────────────
sec_header('15. MEMORY HOOK', story)

hook_text = (
    'The ankle rolls inward (inversion + plantarflexion = supination) and the three lateral ligaments tear in '
    'order from front to back — ATFL first (the most horizontal, under maximum stress when the foot is pointed '
    'down), then CFL, then PTFL only in the worst injuries — while the strong medial deltoid almost never tears '
    'alone (when it does, look for a Maisonneuve fracture hiding at the knee). The Ottawa ankle rules save '
    'unnecessary radiation: bone tenderness at the tips or posterior 6cm of either malleolus, or inability to '
    'weight-bear = X-ray; tenderness at the navicular or 5th metatarsal base = foot X-ray — and always palpate '
    'the ENTIRE fibula because a proximal fibula fracture with widened ankle mortise = Maisonneuve = surgical '
    'emergency. Treat acute sprains with PEACE in the first 3 days (Protection + Elevation + Avoid '
    'anti-inflammatory + Compression + Education) then LOVE (Load + Optimism + Vascularisation + Exercise) — '
    'the old RICE protocol is obsolete. NSAIDs (ibuprofen, naproxen — block COX and reduce prostaglandins) are '
    'useful after 72h but avoid in renal impairment, peptic ulcer, cardiovascular disease, and pregnancy; '
    'fluoroquinolones (ciprofloxacin) must never be forgotten as a cause of Achilles tendon rupture because they '
    'inhibit collagen synthesis in tenocytes — stop the drug if tendon pain develops. Thompson test (squeeze '
    'calf — foot does not move = ruptured Achilles) and anterior drawer test (pull foot forward — excessive '
    'movement = ATFL rupture) are the two most important examination tests. The Achilles tendon watershed zone '
    '(2–6cm above the heel insertion) has the poorest blood supply and is where rupture always occurs. '
    'Proprioception retraining is not optional — it is the essential step that prevents 40% re-sprain rate, '
    'because the mechanoreceptors (position-sensing nerve endings) in the torn ligament are permanently damaged '
    'and must be retrained. Never miss a Lisfranc injury (gap between 1st and 2nd metatarsal bases on X-ray) '
    '— it destroys the midfoot permanently if left untreated. In diabetics, always check pulses and sensation, '
    'calculate the ankle-brachial index, and suspect Charcot neuroarthropathy if the foot is hot, swollen, and '
    'surprisingly painless.'
)

t = Table([[Paragraph(hook_text, sHook)]], colWidths=[CW])
t.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,-1),GREEN_L),
    ('BOX',(0,0),(-1,-1),2,GREEN_D),
    ('LEFTPADDING',(0,0),(-1,-1),10),
    ('RIGHTPADDING',(0,0),(-1,-1),10),
    ('TOPPADDING',(0,0),(-1,-1),10),
    ('BOTTOMPADDING',(0,0),(-1,-1),10),
]))
story.append(t)
story.append(Spacer(1,8))

divider(story)

# ── §16 PRACTICAL DIAGNOSTICS & PROCEDURES ───────────────────────────────────
sec_header('16. PRACTICAL DIAGNOSTICS & PROCEDURES', story)
story.append(Paragraph(
    '<b>Professor\'s Introduction:</b> At a facility with X-ray, blood tests, and medicines — but without CT '
    'or MRI — these hands-on skills define your clinical excellence. Think of yourself as a detective: '
    'your hands, eyes, and a well-read X-ray give you 90% of the diagnosis. The investigations simply confirm '
    'what your examination already told you. Master these procedures and you will manage ankle and foot '
    'injuries to the same standard as any major hospital.', sBody))
story.append(Spacer(1,4))

# ── 16A. PATIENT PREPARATION ──────────────────────────────────────────────────
story.append(Paragraph('A. Preparing the Patient for X-ray', sH2))
story.append(Paragraph(
    'Before you even position the patient for X-ray, preparation matters. A poorly positioned patient '
    'gives a poor image, leading to missed fractures or unnecessary repeat exposures. Think of it like '
    'taking a photograph — the setup determines the quality of the picture.', sBody))

prep_data = [
    ['Step', 'Action', 'Why It Matters'],
    ['1. Explain and consent',
     'Tell the patient: "I need to take an X-ray of your ankle. It uses a small amount of radiation and '
     'is painless. I will need you to stay very still for a few seconds." Ask about pregnancy (females of '
     'childbearing age). Document that radiation risk was discussed.',
     'Reduces patient anxiety = better cooperation = less movement blur. Mandatory in all females of '
     'childbearing age — delay or shield if pregnant unless clinically urgent (spinal injury, limb-threatening).'],
    ['2. Remove all metallic objects',
     'Ask patient to remove: shoes and socks, ankle supports/braces, taping, splints, jewellery '
     '(ankle chains, toe rings), dressings with metal components, plaster if recent and clinically indicated.',
     'Metal causes bright white artefacts on X-ray that can obscure fracture lines. An ankle chain can '
     'look exactly like a chip fracture on X-ray — always remove before imaging.'],
    ['3. Check for open wounds / contamination',
     'Inspect the skin over the injured area before positioning. Photograph and document any open wounds. '
     'Do not remove emergency splints if the limb is clearly deformed or neurovascularly compromised — '
     'image through the splint and reassess after.',
     'Open fractures (bone protruding through skin or wound communicating with fracture) are surgical '
     'emergencies. Removing splints risks further displacement and neurovascular injury.'],
    ['4. Gather previous imaging',
     'Ask: "Have you had an X-ray of this ankle before?" Retrieve previous films. Compare old to new '
     '— baseline changes vs acute injury.',
     'Old fractures, hardware (screws, plates), and degenerative changes can mimic acute fractures. '
     'An old healed avulsion at 5th metatarsal base looks identical to an acute fracture without comparison.'],
    ['5. Screen and shield',
     'Use lead gonadal shield (apron over the pelvis) for patients under 40. Use thyroid collar if '
     'the beam is near the neck. Pregnant patients: lead apron over the abdomen regardless.',
     'ALARA principle (As Low As Reasonably Achievable) — all radiation exposure must be clinically '
     'justified. Gonadal dose from ankle X-ray is tiny but shielding is standard practice.'],
    ['6. Position for comfort and accuracy',
     'If the patient is in severe pain, give analgesia FIRST (paracetamol 1g IV or oral, or '
     'intranasal diamorphine in severe acute trauma) and wait 15-20 minutes before positioning. '
     'A patient bracing against pain cannot hold still for a good image.',
     'Pain = muscle guarding = involuntary movement = blurred image. Treating pain is not just '
     'humane — it directly improves image quality and diagnostic accuracy.'],
]
story.append(plain_table(prep_data, [CW*0.15, CW*0.47, CW*0.38]))
story.append(Spacer(1,6))

# ── 16B. X-RAY VIEWS ──────────────────────────────────────────────────────────
story.append(Paragraph('B. Ankle X-ray Views — How to Position and What Each View Shows', sH2))
story.append(Paragraph(
    'The ankle always requires a MINIMUM of two views (AP and lateral). The mortise view is the most '
    'important for assessing joint congruency. Think of it like viewing a box from three different angles '
    '— each view reveals something the others hide. Never diagnose from a single view alone.', sBody))

xray_views_data = [
    ['View', 'Patient Position', 'Beam Position', 'Key Structures Shown', 'Common Mistake'],
    ['AP (Anteroposterior)\n— Ankle',
     'Patient sitting or supine on table. Knee slightly flexed. Foot resting flat on cassette/detector in neutral position (90 degrees to leg). Long axis of foot pointing straight up.',
     'X-ray beam directed vertically downward, centred midway between the malleoli, 2.5cm above the ankle joint line. SID (source-image distance) = 100cm standard.',
     'Distal tibia, fibula, tibiotalar joint, both malleoli (overlap in this view). Evaluates tibia and fibula length and alignment. Useful for bimalleolar fractures.',
     'Foot externally rotated (patient not holding foot correctly) = mortise is not visible = looks like there is no joint space. Always check foot is truly neutral before accepting the image.'],
    ['Lateral\n— Ankle',
     'Patient lying on their side (affected side down). Knee slightly flexed. Medial side of foot against the detector. The lateral malleolus should be directly over the medial malleolus (superimposed). Long axis of foot horizontal.',
     'X-ray beam directed horizontally, perpendicular to the film, centred over the lateral malleolus. Ankle joint should be exactly in profile.',
     'Posterior malleolus of tibia (third malleolus — often fractured in trimalleolar injuries), Achilles tendon pre-Achilles fat pad (swelling = Achilles pathology), calcaneofibular relationship, calcaneal morphology.',
     'Fibulas not superimposed = patient rotated = posterior malleolus fracture can be missed. Ensure the two malleoli overlap exactly by checking on the monitor before finalising.'],
    ['Mortise View\n— The Key Ankle View',
     'Same as AP position BUT the entire leg is internally rotated 15-20 degrees. This brings the fibula out of the way and opens the ankle mortise so all three sides of the joint space can be seen simultaneously. Check: the 2nd toe should now point straight up.',
     'Same as AP — beam vertically downward, centred at the ankle joint.',
     'The ankle mortise (the socket that holds the talus): medial clear space (between talus and medial malleolus), superior joint space (between talus and tibial plafond), lateral space (between talus and fibula). All three should be EQUAL = 4mm uniform gap.',
     'Insufficient internal rotation = mortise not truly open = asymmetric gap that falsely suggests injury. If in doubt, do both AP and mortise, compare. The mortise view is the one that tells you if the ankle is stable or not.'],
    ['Weight-Bearing\n— Ankle + Foot',
     'Patient stands on the detector/cassette. Full body weight through the injured foot. Usually only done when acute pain is controlled and fracture excluded.',
     'AP beam from front (for ankle) or from above (for foot) with patient standing. Lateral view with patient standing on a step.',
     'Flat foot (pes planus) — only visible under load. Lisfranc injury — subtle widening only seen under weight. Subtalar arthritis. Tibialis posterior dysfunction. True foot arch height.',
     'Requesting weight-bearing views before excluding fracture = patient walks on an unrecognised fracture = fracture displaces = disaster. Always do standard views first, exclude fracture, THEN consider weight-bearing if needed.'],
    ['Foot AP\n(Dorsoplantar)',
     'Patient sitting, foot flat on the detector. Weight of the leg rests naturally. Knee slightly flexed. Long axis of foot aligned with long axis of detector.',
     'Beam directed from above (anteroposterior direction), angled 15 degrees towards the heel to compensate for the dorsal curvature of the foot. Centred at the base of the 3rd metatarsal.',
     'All metatarsal shafts and bases, phalanges, interphalangeal and MTP (metatarsophalangeal) joints, Lisfranc joint (tarsometatarsal joints), cuboid, navicular, cuneiforms.',
     'Too much beam angle (>20 degrees) = metatarsal bases overlap each other = Lisfranc injury missed. 15 degrees is the standard — check your department protocol.'],
    ['Foot Lateral',
     'Same as ankle lateral — patient lying on their side, medial foot against the detector, foot in profile.',
     'Beam horizontal, perpendicular to the film, centred at the mid-foot (navicular level).',
     'Calcaneus (tuberosity, sustentaculum tali, Bohler\'s angle — normal 20-40 degrees, reduced in calcaneal fracture), midfoot alignment, plantar fascia attachment, longitudinal arch height.',
     'Bohler\'s angle < 20 degrees = calcaneal fracture with loss of height. This is missed on AP alone. Always include lateral foot view when calcaneus injury suspected.'],
    ['Foot Oblique',
     'Patient sitting. Foot on the detector, tilted 30-45 degrees onto its medial border (oblique position). The plantar surface faces 45 degrees from the cassette.',
     'Beam vertical, centred at the base of the 3rd metatarsal.',
     'Lateral metatarsal bases (3rd, 4th, 5th) and their tarsometatarsal joints, cuboid-metatarsal junction, calcaneocuboid joint, peroneal groove on fibula, 5th metatarsal base (for avulsion vs Jones distinction).',
     'Missing the oblique view = Jones fracture vs avulsion fracture cannot be distinguished = wrong management. The oblique is ESSENTIAL for 5th metatarsal injuries.'],
]
story.append(plain_table(xray_views_data, [CW*0.12, CW*0.22, CW*0.16, CW*0.26, CW*0.24]))
story.append(Spacer(1,4))

image_search_box('ankle mortise view positioning technique', 'YouTube', story)
image_search_box('ankle X-ray AP lateral mortise normal anatomy labelled', 'Radiopaedia.org', story)
story.append(Spacer(1,4))

# ── 16C. READING THE X-RAY ────────────────────────────────────────────────────
story.append(Paragraph('C. How to Read an Ankle/Foot X-ray — The ABCDS Systematic Approach', sH2))
story.append(Paragraph(
    'Here is the golden rule: <b>NEVER look at one area first.</b> Every radiologist and surgeon uses a '
    'systematic method because the eye is drawn to the obvious injury and misses a second fracture. '
    'The classic teaching: "The most obvious finding on the X-ray is often not the most important one." '
    'Use ABCDS — Adequacy, Bones, Cartilage/joints, Density, Soft tissues — in that exact order every time.', sBody))

abcds_data = [
    ['Letter', 'What to Check', 'Key Questions', 'What Abnormality Means'],
    ['A\nAdequacy',
     'Is the X-ray diagnostic quality? Are all views present (AP + lateral + mortise for ankle; AP + lateral + oblique for foot)? Is the correct area included? Is there adequate penetration (can you see the trabecular bone pattern)?',
     'Can I see both malleoli and the proximal 5cm of tibia and fibula? Is the entire foot on the image? Is the image too dark (over-exposed) or too white (under-exposed)?',
     'Inadequate view = request a repeat. An unreadable X-ray is worse than no X-ray — it gives false reassurance. Write "inadequate — repeat required" rather than guessing.'],
    ['B\nBones',
     'Look at EVERY bone individually. Trace the cortical outline (the bright white outer shell) of each bone like tracing around a map. Then look at the internal trabecular pattern (the internal lattice of bone). Do both on every view.',
     'Is the cortex smooth and continuous? Any step, kink, lucent (dark) line, or impaction (white/sclerotic band)? Any area of the bone missing (lytic lesion)? Is each bone the expected shape?',
     'Cortical break = fracture. Lucent line through bone = fracture line. Sclerotic (white) band = stress fracture or healing fracture. Periosteal reaction (new bone alongside cortex) = healing fracture, osteomyelitis. Missing cortex = destructive lesion (tumour, infection, Charcot).'],
    ['C\nCartilage\n& Joints',
     'Look at each joint space. Joint cartilage is not visible on X-ray — what you see is the joint space (the gap between the two bones, which represents the cartilage). This space should be: uniform, of normal width, and the articular surfaces should be parallel.',
     'ANKLE: Is the mortise uniform — equal gap on all 3 sides (medial, superior, lateral)? FOOT: Is each tarsometatarsal joint space equal? Is the 1st-2nd metatarsal base gap normal (<2mm)? Any articular surface irregularity (step-off = fracture into the joint)?',
     'Mortise medial gap > 4mm = deltoid ligament disruption OR lateral ligament complex injury = UNSTABLE ankle = seek proximal fibula fracture (Maisonneuve). 1st-2nd metatarsal gap > 2mm = Lisfranc injury = surgical emergency. Narrowed joint space = arthritis. Irregular surface = intra-articular fracture.'],
    ['D\nDensity\n(Special)',
     'Compare bone density bilaterally (if you have both ankles). Look for areas that are unusually white (sclerotic/dense) or unusually dark (lucent/osteopenic). Look at the calcaneus specifically — measure Bohler\'s angle on the lateral view.',
     'Is one area of bone whiter than the surrounding bone (sclerosis)? Is there a diffuse loss of bone density (osteoporosis — trabeculae look sparse)? Calcaneus lateral: draw line from tuberosity to posterior facet, then from posterior facet to anterior process — normal angle 20-40 degrees.',
     'Sclerotic lesion = metastasis, bone island, healing fracture, Paget\'s. Generalised osteopenia = osteoporosis (DEXA scan, fall risk). Bohler\'s angle < 20 degrees = calcaneal fracture with height loss = almost always requires CT and likely surgical fixation.'],
    ['S\nSoft Tissues',
     'Look at the soft tissue shadows around the bones. Fat pads are dark (black) on X-ray; swelling replaces fat with fluid (grey). The pre-Achilles fat pad (Kager\'s triangle) is a key sign on lateral ankle view.',
     'Is there soft tissue swelling (generalised haziness replacing fat planes)? Is the pre-Achilles fat triangle visible or obliterated? Any gas in the soft tissues (bubbles in the soft tissue = gas-producing infection = surgical emergency)? Any radio-opaque foreign body (glass, metal, stone)?',
     'Obliterated Kager\'s fat triangle = fluid/haematoma = Achilles tendon injury. Soft tissue swelling pattern: lateral = ATFL injury; medial = deltoid/eversion injury. Soft tissue gas = necrotising fasciitis = emergency surgical debridement within hours. Foreign body = requires localisation for removal.'],
]
story.append(plain_table(abcds_data, [CW*0.08, CW*0.25, CW*0.30, CW*0.37]))
story.append(Spacer(1,4))

# Key measurements table
story.append(Paragraph('Key Ankle X-ray Measurements (Mortise View)', sH2))
measurements_data = [
    ['Measurement', 'Normal Value', 'If Abnormal', 'Clinical Significance'],
    ['Medial clear space\n(talus to medial malleolus)', '= 4mm (equal to superior joint space)', '> 4mm = UNSTABLE',
     'Widening = deltoid ligament rupture OR lateral ligament injury allowing lateral talus shift. Always seek proximal fibula fracture if unexplained widening = Maisonneuve.'],
    ['Superior joint space\n(talus to tibial plafond)', '= 4mm (uniform)', 'Asymmetric or > 4mm = abnormal',
     'Should be equal to medial clear space. Asymmetry indicates talar tilt = posterior or anterior ankle instability.'],
    ['Tibiofibular overlap\n(AP view)', '> 10mm', '< 10mm = syndesmotic disruption',
     'The tibia and fibula overlap on the standard AP view. Loss of overlap = the fibula has moved laterally = syndesmosis torn = unstable ankle = surgery.'],
    ['Tibiofibular clear space\n(both AP and mortise views)', '< 6mm', '> 6mm = syndesmotic disruption',
     'The clear space between fibula and posterior tibia (measured 1cm above joint line). Wide space = syndesmosis injury = ankle mortise is opening up = surgical stabilisation required.'],
    ['Talocrural angle\n(AP or mortise view)', '83 +/- 4 degrees', 'Asymmetric compared to other side',
     'The angle between the distal tibial articular surface and a line between the fibular tips. Asymmetry > 2 degrees compared to the other ankle suggests fibular shortening (Weber C fracture).'],
    ['Bohler\'s angle\n(Lateral foot view, calcaneus)', '20-40 degrees', '< 20 degrees = calcaneal fracture',
     'Measures calcaneal height. Reduced angle = calcaneal fracture with height collapse (usually fall from height). < 20 degrees almost always requires CT for surgical planning.'],
]
story.append(plain_table(measurements_data, [CW*0.22, CW*0.16, CW*0.16, CW*0.46]))
story.append(Spacer(1,4))

# Weber classification
story.append(Paragraph('Weber Classification of Lateral Malleolus (Fibula) Fractures', sH2))
story.append(Paragraph(
    'The Weber classification is the most commonly used system for ankle fractures and is based on the '
    'RELATIONSHIP of the fibula fracture to the tibiofibular syndesmosis (the strong ligamentous connection '
    'between the tibia and fibula at the ankle). The higher the fracture, the more likely the syndesmosis '
    'is disrupted, and the more unstable the ankle.', sBody))
weber_data = [
    ['Weber Type', 'Fracture Location', 'Syndesmosis Status', 'Stability', 'Treatment'],
    ['Type A', 'BELOW the level of the syndesmosis (below the ankle joint line). The fibula fracture is distal — below the point where tibia and fibula are joined.',
     'INTACT — fracture is below the syndesmosis so the joint between tibia and fibula is not disturbed.',
     'STABLE — the ankle mortise is intact because the syndesmosis holds the fibula in the correct position.',
     'Conservative: plaster below-knee cast for 4-6 weeks in most cases. Surgical only if displaced or associated with medial/posterior malleolus fracture.'],
    ['Type B', 'AT the level of the syndesmosis — the fracture line runs at the joint between tibia and fibula, often spiralling upward.',
     'Partially torn OR intact — may have partial syndesmotic disruption. KEY: check the medial clear space.',
     'VARIABLE — check medial clear space. If medial space normal = stable (conservative). If medial space widened = unstable (surgical).',
     'Undisplaced, stable: below-knee cast 6 weeks. Displaced or medial clear space widened: ORIF (Open Reduction Internal Fixation) — lateral plate + lag screw. Most common Weber type.'],
    ['Type C', 'ABOVE the syndesmosis — fibula fracture is proximal (higher up the leg). Can be very proximal — even at the fibular neck (= MAISONNEUVE fracture = the fracture is at the knee level but the ankle injury is the real problem).',
     'DISRUPTED — the fracture force must have travelled through the syndesmosis to break the fibula this high. The syndesmosis is torn.',
     'UNSTABLE — the ankle mortise is disrupted because the fibula is no longer held to the tibia at the ankle joint.',
     'SURGICAL — ORIF fibula, syndesmotic screw or tightrope device to hold tibia and fibula together while the syndesmosis heals (8-12 weeks before weight bearing). Medial malleolus fixation if fractured. Non-operative = unacceptable in most cases.'],
]
story.append(plain_table(weber_data, [CW*0.10, CW*0.26, CW*0.18, CW*0.16, CW*0.30]))
story.append(Spacer(1,4))

image_search_box('Weber classification ankle fractures diagram labelled', 'Radiopaedia.org', story)
image_search_box('Maisonneuve fracture X-ray ankle proximal fibula', 'Radiopaedia.org', story)
story.append(Spacer(1,4))

# ── 16D. PLASTER OF PARIS APPLICATION ──────────────────────────────────────────
story.append(Paragraph('D. Applying a Plaster of Paris (POP) Backslab — Step by Step', sH2))
story.append(Paragraph(
    '<b>What is Plaster of Paris?</b> POP (Plaster of Paris) is calcium sulphate hemihydrate — it sets '
    'hard when mixed with water as the crystals reform. It has been used for 150 years to immobilise '
    'fractures because it is cheap, mouldable, and easy to apply. We use a <b>backslab</b> (a slab of '
    'plaster on one side only, not a complete cylinder) in the acute setting because swelling always '
    'increases after injury — a complete cast would act as a tourniquet and compress the leg, causing '
    'compartment syndrome (the most feared complication of casting). A backslab allows the limb to swell '
    'safely. A complete cast is applied only when swelling has fully subsided — usually 5-10 days later.', sBody))
info_box(
    'SAFETY RULE: In acute injuries, ALWAYS apply a backslab (not a full circular cast). '
    'A full cast on an acutely injured, swelling limb can cause compartment syndrome — '
    'a surgical emergency that can result in limb loss or death if the cast is not split immediately.',
    story, color=AMBER, border=AMBER_B)

pop_data = [
    ['Step', 'Action', 'Professor\'s Teaching Point'],
    ['1. Materials',
     'Gather: stockinette (tubular bandage — 7.5cm for below-knee), orthopaedic wool/padding (Orthoban, '
     '7.5-10cm wide), POP plaster bandages (7.5-10cm width for below-knee, 10-15cm for above-knee or upper '
     'limb), bowl of warm water (30-35 degrees C — body temperature), non-sterile gloves, bandage scissors.',
     'Warm water accelerates setting — do not use hot water (burns risk, also sets too fast to mould). '
     'Cold water slows setting — good for complex fractures needing longer moulding time.'],
    ['2. Position the patient',
     'Below-knee backslab: patient sitting on the edge of the bed or trolley with the knee at 90 degrees '
     'and the foot hanging freely. You need to position the ankle at EXACTLY 90 degrees neutral dorsiflexion '
     '(foot at right angle to leg). Ask the patient to "hold your foot up as if you are stepping on the '
     'accelerator at exactly 90 degrees."',
     'CRITICAL: The ankle position in the cast determines the functional outcome. Equinus (foot pointed '
     'downward) = the patient will not be able to walk normally after the cast is removed. EXCEPTION: '
     'Achilles tendon rupture is deliberately immobilised in 20-30 degrees plantarflexion (equinus) '
     'to relax the tendon and allow healing.'],
    ['3. Stockinette',
     'Apply stockinette from the metatarsal heads (ball of the foot) to the tibial tuberosity (just below '
     'the knee). Leave 5cm extra at each end — this will be folded back over the cast edges later to create '
     'a smooth comfortable edge. Cut a notch for the thumb at the upper end if it is an above-ankle cast.',
     'The stockinette protects the skin from direct contact with the plaster (which generates heat as it '
     'sets — can cause mild burns). The folded edges prevent the raw cast edge from cutting into the skin.'],
    ['4. Orthopaedic wool',
     'Apply two layers of wool padding, overlapping each layer by half, from metatarsal heads to tibial '
     'tuberosity. Apply EXTRA wool (double or triple thickness) over ALL bony prominences: both malleoli '
     '(medial and lateral), the heel (calcaneus), the dorsum of the foot, and the tibial crest.',
     'Bony prominences are where pressure sores develop under a cast. A cast sore under plaster can go '
     'unnoticed (the patient just reports pain "in the cast") and can cause skin breakdown, osteomyelitis, '
     'or permanent tendon damage. Extra wool here is not optional — it is essential.'],
    ['5. Make the slab',
     'POP slab: measure the length from metatarsal heads around the heel to the tibial tuberosity '
     '(posterior surface). Roll out 8-10 layers of POP bandage this length, fold over to make the slab. '
     'Width should cover from one side of the leg to the other at the widest point. Standard below-knee '
     'backslab: posterior slab only, applied to the back of the leg.',
     '8-10 layers gives enough strength. Fewer = slab breaks. More = too heavy, too much heat generation. '
     'Some departments use a U-slab configuration: one arm along the medial side and one along the lateral '
     'side of the leg = better rotational control for ankle fractures.'],
    ['6. Wet the slab',
     'Submerge the slab in the warm water until the bubbles stop (all air replaced by water = '
     'approximately 10-15 seconds). Lift out and hold vertically for 3-5 seconds to let excess water drip. '
     'Then squeeze GENTLY from both ends towards the centre (like squeezing a sponge) — never wring or '
     'twist, as this removes too much water and weakens the set.',
     'Too dry = slab crumbles when moulding, weak final cast. Too wet = runny plaster drips everywhere, '
     'takes too long to set, and the layers do not bond properly. The correct consistency is like cream — '
     'wet but holds together.'],
    ['7. Apply the slab',
     'Apply the wet slab to the posterior (back) surface of the leg while an assistant (or the patient) '
     'holds the foot at 90 degrees neutral. Centre the slab over the heel and Achilles region. '
     'The slab should extend from the metatarsal heads, around the heel, up the back of the leg to '
     '2-3cm below the knee joint (popliteal fossa).',
     'The most common mistake: applying the slab while the ankle is in equinus (pointed down) because '
     'it is easier to apply without fighting the patient. This is NOT acceptable for fractures. Always '
     'maintain 90 degrees throughout application. Two people make this much easier.'],
    ['8. Smooth and mould',
     'Using wet gloved hands, smooth the plaster surface firmly from proximal to distal. Eliminate all '
     'ridges, folds, and air pockets. You have approximately 3-5 minutes before the plaster starts to '
     'stiffen. Mould around the heel contour and gently around the malleoli — but do NOT press hard over '
     'the malleoli (pressure sore risk).',
     'Ridges and creases in the set plaster cause pressure points that can cause skin breakdown. Think of '
     'it like ironing a shirt — you are smoothing out any wrinkles before it sets permanently. The plaster '
     'will feel warm as it sets — this is normal (exothermic crystallisation reaction).'],
    ['9. Fold edges and bandage',
     'While the plaster is still slightly soft, fold the stockinette ends back over the edges of the slab. '
     'Apply a crepe bandage over the whole construction from toes to just below the knee, overlapping by '
     'half with each turn. Apply with MODERATE tension — firm but not tight (able to slip two fingers '
     'under the bandage).',
     'The bandage holds the slab against the leg during setting and smooths the outer surface. Too tight '
     '= tourniquet effect. Too loose = slab slides and dries in the wrong position. The "two-finger" rule '
     'is the bedside check for correct bandage tension.'],
    ['10. Hold for setting',
     'The plaster sets in stages: (1) Initial set: 2-5 minutes — feels firm but still slightly soft. '
     '(2) Final set: 20-30 minutes — hard and rigid. (3) Full strength: 24-48 hours (POP needs '
     'this long to fully crystallise and reach maximum strength). Hold the foot at 90 degrees throughout '
     'initial setting. The plaster is hot during this phase — warn the patient.',
     'The most common time for displacement: the 5 minutes after plaster application when the slab is '
     'firm but not yet set, and the helper lets go prematurely. Someone must hold the foot in position '
     'until the plaster is truly rigid. Use the knuckle test: knock on the cast — a hollow sound = not '
     'set; a solid thunk = set.'],
    ['11. Neurovascular check',
     'Before the patient leaves: check (1) capillary refill in all five toenails (<2 seconds = normal), '
     '(2) sensation — can they feel light touch on the dorsum of foot and toes, (3) active toe movement '
     '— ask patient to wiggle all toes, (4) colour — toes should be pink, not blue/white/dusky.',
     'EMERGENCY if: toes blue/white = vascular compromise. Toes cold + unable to wiggle = nerve compression. '
     'Cast must be split immediately (cut through the full width of the cast and bandage on both sides = '
     '"bivalving") without delay. The window for saving a limb from compartment syndrome is 6 hours.'],
    ['12. Patient instructions',
     'Give written AND verbal instructions: (1) ELEVATE the leg above heart level for first 24-48 hours '
     '(reduces swelling). (2) KEEP DRY — no bathing, cover with plastic bag for showers. (3) DO NOT '
     'WEIGHT-BEAR for 24-48h (POP not at full strength). (4) Return IMMEDIATELY if: toes go numb, '
     'cold, blue, painful under cast, or burning sensation. (5) Follow-up in fracture clinic in 5-7 days.',
     'Most cast complications present within 24-48h. The commonest reason patients ignore warning signs '
     'is that they think mild discomfort is normal. Emphasise: "Any numbness, tingling, or skin burning '
     'inside the cast is an emergency — come to hospital immediately, day or night."'],
]
story.append(plain_table(pop_data, [CW*0.14, CW*0.46, CW*0.40]))
story.append(Spacer(1,4))

# Positions table
story.append(Paragraph('Ankle Position for Different Injuries', sH2))
positions_data = [
    ['Injury', 'Cast Position', 'Reason'],
    ['Ankle fracture (stable Weber A, undisplaced Weber B)',
     '90 degrees neutral dorsiflexion (right angle, foot at 90 degrees to leg)',
     'Functional position — allows normal gait after cast removal. Prevents equinus contracture of Achilles.'],
    ['Achilles tendon rupture (conservative management)',
     '20-30 degrees plantarflexion (foot slightly pointed down = equinus)',
     'Relaxes the Achilles tendon — reduces tension on the healing tendon ends. Progressive dorsiflexion over weeks as healing progresses.'],
    ['5th metatarsal fracture, metatarsal fractures',
     '90 degrees neutral, plantar slab (under the sole of the foot)',
     'Offloads the metatarsal from ground-reaction forces. Plantar slab provides a platform for the foot.'],
    ['Grade III ankle sprain (complete ligament tear, conservative)',
     '90 degrees neutral, functional brace or below-knee cast',
     'Neutral position allows proprioception retraining. Brace preferred over cast for most Grade III sprains as allows controlled movement.'],
    ['Tibialis posterior tendon tear (acute)',
     '90 degrees neutral with slight inversion (foot turned slightly inward)',
     'Reduces tension on the tibialis posterior tendon while healing.'],
]
story.append(plain_table(positions_data, [CW*0.30, CW*0.30, CW*0.40]))
story.append(Spacer(1,6))

image_search_box('below knee POP backslab application technique step by step', 'YouTube', story)
image_search_box('ankle cast bivalving compartment syndrome technique', 'YouTube', story)
story.append(Spacer(1,4))

# ── 16E. SYNTHETIC CAST ────────────────────────────────────────────────────────
story.append(Paragraph('E. Synthetic (Fibreglass / Scotch-Cast) Application', sH2))
story.append(Paragraph(
    'Synthetic casting material (commonly known by the brand name Scotch-Cast or Delta-Cast) uses a '
    'fibreglass or polyester fabric impregnated with polyurethane resin that sets on contact with water. '
    'Think of it as the upgrade version of POP: lighter, stronger, and more water-resistant, but less '
    'forgiving in terms of moulding. The principle of application is identical to POP — the differences '
    'are in the material properties and the timing.', sBody))

synth_data = [
    ['Property', 'Plaster of Paris (POP)', 'Synthetic Fibreglass Cast'],
    ['Weight', 'Heavier (3-4x heavier than fibreglass)', 'Light — patients prefer this'],
    ['Setting time', '10-15 min initial set, 24-48h full strength', '3-5 min initial set, 20-30 min full strength'],
    ['Mouldability', 'Excellent — highly conformable while wet', 'Limited — stiffer, harder to mould precisely'],
    ['Water resistance', 'Dissolves and softens when wet — must be kept dry', 'Resistant to light moisture — not waterproof but tolerates splashes'],
    ['Strength when set', 'Good (adequate for most fractures)', 'Superior — 4-5x stronger than POP for same thickness'],
    ['Cost', 'Cheap (essential for low-resource settings)', 'More expensive (3-5x cost of POP)'],
    ['Skin irritation', 'Minimal', 'Glass fibres can cause skin irritation — always use stockinette + wool'],
    ['Best use', 'Acute injuries (first 24-72h) — when swelling expected, when precise moulding needed, backslab applications', 'Definitive cast (after swelling settled, day 5-10), paediatrics (waterproof for bathing), active patients'],
    ['Removal', 'Easily cut with scissors or standard cast saw', 'Requires oscillating cast saw — more difficult'],
    ['Heat during setting', 'Moderate heat (exothermic) — patient feels warmth', 'Minimal heat generation — safer in neuropathic patients (diabetes)'],
    ['MRCP relevance', 'Know the indications and complications of both', 'Synthetic preferred in diabetics due to less heat generation'],
]
story.append(plain_table(synth_data, [CW*0.22, CW*0.39, CW*0.39]))
story.append(Spacer(1,4))

alert_box(
    'IMPORTANT: In diabetic patients with peripheral neuropathy, use EXTRA wool padding and prefer '
    'synthetic cast (less heat) for definitive casting. Diabetics cannot feel pressure sores developing '
    'inside the cast. Check feet at EVERY follow-up appointment — diabetic foot complications can '
    'escalate to amputation within days if cast sores are missed.', story)

story.append(Paragraph('Key Differences in Application Technique (Synthetic vs POP):', sH2))
synth_app = [
    ['Stage', 'POP Technique', 'Synthetic Technique', 'Why Different'],
    ['Wetting', 'Submerge until bubbles stop (10-15 sec)', 'Dip briefly — 2-3 seconds only. Squeeze gently.',
     'Synthetic resin activates rapidly with water. Over-wetting wastes resin and accelerates setting too fast.'],
    ['Number of layers', '8-10 layers for a slab', '3-4 layers for equivalent strength',
     'Fibreglass is 4-5x stronger — fewer layers needed. More layers = too rigid = compartment syndrome risk.'],
    ['Moulding window', '3-5 minutes', '1-2 minutes only — works faster',
     'Must work quickly. Prepare everything before wetting. Two people required for complex moulding.'],
    ['Gloves', 'Regular non-sterile gloves',
     'REQUIRED: vinyl or polyethylene gloves essential — polyurethane resin is a contact sensitiser (can cause allergic contact dermatitis on repeated exposure). Always glove.', 'Resin sensitisation is an occupational hazard for healthcare workers who apply many casts without gloves.'],
    ['Edge finishing', 'Fold stockinette back easily while soft',
     'Must fold back BEFORE the resin sets (within first minute). Once set, edges are rough and sharp — file with cast file.',
     'Synthetic sets rigid quickly. Sharp edges cut into the skin at the cast margins.'],
]
story.append(plain_table(synth_app, [CW*0.14, CW*0.25, CW*0.35, CW*0.26]))
story.append(Spacer(1,6))

image_search_box('fibreglass synthetic cast application ankle technique', 'YouTube', story)
story.append(Spacer(1,4))

# ── 16F. MINIMAL RESOURCES PROTOCOL ───────────────────────────────────────────
story.append(Paragraph('F. Minimal Resources Clinical Protocol — The Professor\'s Summary', sH2))
story.append(Paragraph(
    '<b>Your site has: Clinical examination + X-ray + CBC + medicines. No CT, no MRI, no ultrasound.</b> '
    'Here is how to manage ankle and foot injuries to a high standard with exactly these resources. '
    'Remember: the best investigations in the world cannot replace a careful examination by a doctor '
    'who knows what they are looking for.', sBody))

minimal_data = [
    ['Clinical Problem', 'What to Do (Minimal Resources)', 'When to Refer', 'Why This Works Without CT/MRI'],
    ['Ankle sprain — lateral',
     '1. Examine: anterior drawer test (ATFL), talar tilt (CFL), whole fibula palpation. '
     '2. Apply Ottawa rules — if negative, no X-ray needed. '
     '3. If positive, get ankle X-ray (AP + lateral + mortise). '
     '4. Check entire fibula clinically — if tender at knee = get knee X-ray (Maisonneuve). '
     '5. Grade by anterior drawer: Grade I (no laxity), II (increased laxity but firm end-point), '
     'III (no end-point = complete tear). '
     '6. Treat by grade: I = PEACE/LOVE + early mobilisation. II = brace + physio. III = backslab '
     '+ fracture clinic referral for possible Brostrom surgical assessment.',
     'Refer if: Maisonneuve suspected, medial clear space > 4mm on X-ray, neurovascular compromise, '
     'complete Grade III that fails 6 months conservative treatment.',
     'Anterior drawer + talar tilt give you equivalent information to MRI ligament grading in experienced hands. '
     'Ottawa rules have 100% sensitivity — no fracture is missed clinically.'],
    ['Ankle fracture',
     '1. Palpate ALL malleoli, entire fibula (to knee), medial column. '
     '2. Get 3 X-ray views (AP + lateral + mortise). '
     '3. Classify Weber (A/B/C) from X-ray. '
     '4. Check medial clear space (> 4mm = unstable). '
     '5. Check tibiofibular overlap (< 10mm = syndesmosis disruption). '
     '6. Stable Weber A + undisplaced Weber B = below-knee backslab + non-weight bearing + '
     'fracture clinic 5-7 days. '
     '7. Unstable (Weber C, displaced, bimalleolar, medial clear space widened) = splint, '
     'neurovascular check, URGENT surgical referral.',
     'Refer: ALL Weber C, ALL displaced fractures, medial clear space widening, bimalleolar or '
     'trimalleolar fractures, open fractures, neurovascular compromise.',
     'X-ray + Weber classification + medial clear space measurement = surgery vs conservative decision '
     'in most cases. CT is only needed for complex multi-fragment or calcaneal fractures.'],
    ['Achilles tendon rupture',
     '1. Classic history: sudden "pop" in back of ankle, unable to plantarflex, often on fluoroquinolones. '
     '2. Thompson test (squeeze calf — foot does NOT plantarflex = positive = ruptured). '
     '3. Palpate gap in Achilles (2-6cm above heel insertion). '
     '4. X-ray: usually normal — look for obliteration of Kager\'s fat triangle (lateral view). '
     '5. Decision: functional brace (equinus) vs surgical repair. For most active patients under 60, '
     'surgical repair = better re-rupture rates. Conservative = functional brace in equinus for 8-12 '
     'weeks with gradual dorsiflexion.',
     'Refer to orthopaedics for surgical decision-making. Thompson test + clinical gap = sufficient '
     'diagnosis for referral without MRI.',
     'Thompson test + gap palpation = diagnosis. No MRI needed. Surgical referral based on clinical '
     'findings alone is standard practice.'],
    ['Lisfranc injury',
     '1. High index of suspicion: midfoot pain after forced plantar/dorsiflexion, unable to '
     'weight-bear, swelling over dorsum of foot, "N-spot" tenderness at 1st-2nd metatarsal base. '
     '2. Standard foot AP + oblique + lateral X-ray. '
     '3. Check: gap between 1st and 2nd metatarsal base (normal < 2mm). '
     '4. Check: 2nd metatarsal base should align exactly with middle cuneiform medial border. '
     '5. If clinically suspected but X-ray normal: DO NOT DISCHARGE — immobilise in non-weight-bearing '
     'backslab and arrange urgent orthopaedic review. Weight-bearing X-ray in 5-7 days may show '
     'instability. Up to 50% missed on initial X-ray.',
     'ALL suspected Lisfranc injuries = urgent orthopaedic referral regardless of X-ray findings. '
     'The consequences of missing this injury are permanent (midfoot collapse, chronic arthritis, disability).',
     'Even without CT, the combination of clinical suspicion + plain X-ray measurements + non-weight-bearing '
     'immobilisation protects the patient while awaiting definitive imaging at a tertiary centre.'],
    ['Plantar fasciitis',
     '1. Classic history + point tenderness at medial calcaneal tuberosity. '
     '2. X-ray: calcaneal spur on lateral view (present in 50% — NOT the cause of pain but confirms '
     'chronic traction). Rule out stress fracture of calcaneus (Bohler\'s angle). '
     '3. Treat: daily stretching (plantar fascia stretch + calf stretch), heel cups/orthotics, '
     'NSAIDs (ibuprofen 400mg TDS with food x2 weeks), avoid barefoot walking. '
     '4. If no improvement in 6-8 weeks: corticosteroid injection (methylprednisolone 40mg + '
     'lidocaine 1ml at medial calcaneal tuberosity using anatomical landmark injection technique).',
     'Refer if: bilateral presentation (consider seronegative arthritis — ankylosing spondylitis), '
     'not responding after 3 months conservative management, stress fracture on X-ray.',
     'Plantar fasciitis is 100% clinical diagnosis. X-ray only to rule out bony pathology. '
     'No MRI needed for straightforward cases.'],
    ['Charcot foot (diabetic)',
     '1. Classic: hot, red, swollen foot in diabetic with peripheral neuropathy, minimal pain, '
     'raised temperature (> 2 degrees C difference compared to other foot with thermometer/back of hand). '
     '2. X-ray: early Charcot may look normal or show subtle fragmentation. Late = complete joint '
     'destruction, bone debris, subluxation. '
     '3. DO NOT WEIGHT-BEAR — apply total contact cast or non-weight-bearing support immediately. '
     '4. Bisphosphonate (zoledronic acid IV or alendronic acid oral) may reduce bone resorption in '
     'acute phase. '
     '5. Manage blood glucose aggressively. Multidisciplinary referral: diabetes team, vascular surgery, orthopaedics.',
     'ALWAYS refer: Charcot foot requires multidisciplinary team. Orthopaedics, diabetology, vascular surgery, '
     'podiatry all involved. Urgent referral to prevent progression to ulceration and amputation.',
     'Clinical diagnosis of acute Charcot is possible from history + examination + basic X-ray. '
     'MRI is the gold standard for early diagnosis but immediate management (non-weight-bearing) '
     'can be started based on clinical picture alone.'],
]
story.append(plain_table(minimal_data, [CW*0.18, CW*0.35, CW*0.22, CW*0.25]))
story.append(Spacer(1,6))

# Final minimal resources alert box
alert_box(
    'PROFESSOR\'S FINAL WORD: At your facility, your clinical examination IS your MRI. '
    'The anterior drawer test tells you if the ATFL is torn. The Thompson test tells you '
    'if the Achilles is ruptured. Too-many-toes sign tells you the tibialis posterior has failed. '
    'The medial clear space on X-ray tells you if the ankle mortise is stable. '
    'Learn these clinical tools to expert level — they work as well as advanced imaging in the hands '
    'of a skilled examiner, and they are available at 3am in any emergency with no waiting time.',
    story, color=GREEN_L, border=GREEN_D)

story.append(Spacer(1,8))

# Final divider and footer
divider(story)
story.append(Paragraph(
    '<i>Ankle and Foot Injuries Revision Note — MRCP / Medical Finals / PACES Preparation</i>',
    ParagraphStyle('Ft', fontName='DV-I', fontSize=8, leading=11,
                   textColor=HexColor('#888888'), alignment=1)))

# ── BUILD PDF ────────────────────────────────────────────────────────────────
doc.build(story)
print('SUCCESS: /mnt/user-data/outputs/Ankle_Foot_Injuries_Note.pdf')
