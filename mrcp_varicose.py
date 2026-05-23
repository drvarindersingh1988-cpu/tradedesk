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
PURPLE_L=HexColor('#f5eef8'); PURPLE_D=HexColor('#7d3c98')
NAVY   = HexColor('#1a1a2e'); WHITE  = HexColor('#ffffff')

PAGE_W, PAGE_H = A4
MARGIN = 18*mm
CW = PAGE_W - 2*MARGIN

doc = SimpleDocTemplate('/mnt/user-data/outputs/Varicose_Veins_MRCP_Note.pdf',
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

# ── PIL helpers ───────────────────────────────────────────────────────────────
def pf(sz):
    try: return ImageFont.truetype(FD+'DejaVuSans.ttf', sz)
    except: return ImageFont.load_default()
def pfb(sz):
    try: return ImageFont.truetype(FD+'DejaVuSans-Bold.ttf', sz)
    except: return ImageFont.load_default()
def text_size(draw, text, font):
    bb = draw.textbbox((0,0), text, font=font)
    return bb[2]-bb[0], bb[3]-bb[1]
def wrap_text(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ''
    for word in words:
        test = (cur+' '+word).strip()
        if text_size(draw, test, font)[0] <= max_w: cur = test
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
    if accent: draw.rectangle([bx, y, bx+6, y+box_h], fill=border)
    ty = y + pad_y
    offset = 3 if accent else 0
    for text, font, color, ww, wh in line_data:
        draw.text((cx-ww//2+offset, ty), text, font=font, fill=color)
        ty += wh + line_gap
    return y + box_h
def img2rl(img, w):
    buf = io.BytesIO(); img.save(buf,'PNG'); buf.seek(0)
    return RLImage(buf, width=w, height=w*img.height/img.width)

# ═══════════════════════════════════════════════════════════════════════════════
# PIL DIAGRAM 1 — Venous Anatomy of the Leg
# ═══════════════════════════════════════════════════════════════════════════════
def make_venous_anatomy():
    W, H = 900, 900
    img = Image.new('RGB', (W, H), '#f8fffe')
    draw = ImageDraw.Draw(img)
    fb = pfb(15); fn = pf(12); fs = pf(11)

    draw.rectangle([0, 0, W, 40], fill='#0d5c63')
    tw, _ = text_size(draw, 'VENOUS ANATOMY OF THE LEG', pfb(16))
    draw.text(((W-tw)//2, 10), 'VENOUS ANATOMY OF THE LEG', font=pfb(16), fill='#ffffff')

    # Column headers
    draw_box(draw, 225, 55, [('DEEP VENOUS SYSTEM', fb, '#ffffff')],
             '#2471a3', '#2471a3', accent=False, min_w=200)
    draw_box(draw, 675, 55, [('SUPERFICIAL VENOUS SYSTEM', fb, '#ffffff')],
             '#0d5c63', '#0d5c63', accent=False, min_w=200)

    # Deep system boxes (left side), top=IVC/femoral, bottom=calf veins
    deep_items = [
        (225, 120, 'IVC (Inferior Vena Cava)', 'No valves — blood from both legs'),
        (225, 210, 'Common Femoral Vein', 'In femoral triangle, groin'),
        (225, 300, 'Femoral Vein', 'Deep — runs with femoral artery'),
        (225, 390, 'Popliteal Vein', 'Behind the knee'),
        (225, 480, 'Posterior Tibial Vein', 'Medial lower leg'),
        (225, 560, 'Anterior Tibial Vein', 'Dorsal foot / anterior leg'),
        (225, 640, 'Peroneal Vein', 'Lateral lower leg'),
    ]
    for cx, y, title, sub in deep_items:
        draw_box(draw, cx, y, [(title, pfb(11), '#1a2e50'), (sub, pf(10), '#444466')],
                 '#2471a3', '#dbeafe', accent=True, min_w=180)

    # Superficial system boxes (right side)
    surf_items = [
        (675, 120, 'SFJ (Saphenofemoral Junction)', 'GSV joins femoral vein, groin'),
        (675, 210, 'GSV — Medial Thigh', 'Great Saphenous Vein, longest in body'),
        (675, 300, 'GSV — Medial Knee', 'Crosses medial joint line'),
        (675, 390, 'GSV — Medial Calf', 'Visible when varicose'),
        (675, 480, 'SPJ (Saphenopopliteal Junction)', 'SSV joins popliteal vein'),
        (675, 560, 'SSV — Posterior Calf', 'Small Saphenous Vein'),
        (675, 640, 'GSV — Medial Ankle', 'Anterior to medial malleolus'),
    ]
    for cx, y, title, sub in surf_items:
        draw_box(draw, cx, y, [(title, pfb(11), '#0d3320'), (sub, pf(10), '#2d5a3d')],
                 '#0d5c63', '#d4edda', accent=True, min_w=200)

    # Arrows in deep system (downward = blood flows up, so arrows UP)
    for y in [165, 255, 345, 435, 515, 595]:
        arrow_down(draw, 225, y+15, y-5, color='#2471a3', w=2, hs=7)

    # Arrows in superficial system (upward)
    for y in [165, 255, 345, 525, 605]:
        arrow_down(draw, 675, y+15, y-5, color='#0d5c63', w=2, hs=7)

    # Perforating vein connections (horizontal, with valve symbols)
    perforator_levels = [
        (395, 'Hunterian perforator (thigh)'),
        (460, "Dodd's perforator (lower thigh)"),
        (530, "Boyd's perforator (below knee)"),
        (600, "Cockett's perforators (lower leg)"),
        (670, "Ankle perforators"),
    ]
    for py, label in perforator_levels:
        x1, x2 = 330, 560
        cx2 = (x1+x2)//2
        draw.line([(x1, py), (x2, py)], fill='#d4640a', width=2)
        # valve triangle pointing right (deep direction normal = superficial->deep)
        draw.polygon([(cx2-6, py-5),(cx2-6, py+5),(cx2+6, py)], fill='#d4640a')
        lw, lh = text_size(draw, label, pf(9))
        draw.text((cx2-lw//2, py-lh-2), label, font=pf(9), fill='#8b3a00')

    # Legend
    y_leg = 730
    draw.rectangle([40, y_leg, W-40, y_leg+100], fill='#fffff0', outline='#cccccc', width=1)
    draw.text((55, y_leg+8), 'LEGEND:', font=pfb(11), fill='#1a1a2e')
    draw.rectangle([55, y_leg+28, 80, y_leg+44], fill='#dbeafe', outline='#2471a3', width=2)
    draw.text((88, y_leg+28), 'Deep venous system (carries 90% of venous return)', font=pf(10), fill='#1a1a2e')
    draw.rectangle([55, y_leg+52, 80, y_leg+68], fill='#d4edda', outline='#0d5c63', width=2)
    draw.text((88, y_leg+52), 'Superficial venous system (varicose veins occur here)', font=pf(10), fill='#1a1a2e')
    draw.line([(55, y_leg+80), (80, y_leg+80)], fill='#d4640a', width=2)
    draw.text((88, y_leg+74), 'Perforating veins with one-way valves (superficial->deep normal)', font=pf(10), fill='#1a1a2e')

    final_h = y_leg + 110
    img = img.crop((0, 0, W, final_h))
    return img

# ═══════════════════════════════════════════════════════════════════════════════
# PIL DIAGRAM 2 — CEAP Classification Visual
# ═══════════════════════════════════════════════════════════════════════════════
def make_ceap_diagram():
    W = 900
    stages = [
        ('C0', 'No visible disease', 'Patient has symptoms (aching, heaviness) but NO visible veins', '#e8f5e9', '#388e3c'),
        ('C1', 'Telangiectasia / Spider veins', 'Tiny (<1mm) red/purple vessels. Reticular veins (1-3mm, blue). Cosmetic only.', '#f1f8e9', '#689f38'),
        ('C2', 'Varicose Veins', 'Raised, tortuous veins >3mm. The classic "varicose vein" stage.', '#fff9c4', '#f9a825'),
        ('C3', 'Oedema', 'Ankle swelling present. No skin changes yet. Calf feels tight in evenings.', '#fff3e0', '#ef6c00'),
        ('C4a', 'Pigmentation OR Eczema', 'Haemosiderin (brown/rust skin staining). Stasis eczema. Medial ankle.', '#fce4ec', '#c62828'),
        ('C4b', 'Lipodermatosclerosis OR Atrophie blanche', 'Hard, woody skin. Inverted champagne bottle shape. Pre-ulcer stage. HIGH RISK.', '#f3e5f5', '#6a1b9a'),
        ('C5', 'Healed venous ulcer', 'Scarred area above ankle where an ulcer has healed. Will likely recur.', '#e8eaf6', '#283593'),
        ('C6', 'Active venous ulcer', 'Open ulcer at medial gaiter area. Requires urgent compression + vascular referral.', '#b71c1c', '#ffffff'),
    ]
    row_h = 80
    H = len(stages) * row_h + 80
    img = Image.new('RGB', (W, H), '#ffffff')
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 45], fill='#0d5c63')
    tw, _ = text_size(draw, 'CEAP CLASSIFICATION — Clinical Severity of Venous Disease', pfb(15))
    draw.text(((W-tw)//2, 12), 'CEAP CLASSIFICATION — Clinical Severity of Venous Disease', font=pfb(15), fill='#ffffff')

    for i, (grade, title, desc, bg, tc) in enumerate(stages):
        y = 50 + i * row_h
        draw.rectangle([10, y+4, W-10, y+row_h-4], fill=bg, outline='#cccccc', width=1)
        # Grade badge
        draw.rectangle([18, y+12, 72, y+row_h-12], fill=tc, outline=tc, width=1)
        gw, gh = text_size(draw, grade, pfb(14))
        draw.text((45-gw//2, y+(row_h-gh)//2), grade, font=pfb(14), fill='#ffffff' if tc != '#ffffff' else '#c62828')
        # Title
        draw.text((85, y+10), title, font=pfb(13), fill=tc if tc != '#ffffff' else '#c62828')
        # Description — wrap
        desc_lines = wrap_text(draw, desc, pf(10), W-200)
        dy = y+30
        for dl in desc_lines:
            draw.text((85, dy), dl, font=pf(10), fill='#333333')
            dy += 14
        # Severity arrow on right
        arrow_txt = 'MILD' if i < 2 else ('MODERATE' if i < 4 else ('SEVERE' if i < 6 else 'CRITICAL'))
        aw, _ = text_size(draw, arrow_txt, pf(9))
        draw.text((W-aw-20, y+(row_h-14)//2), arrow_txt, font=pf(9), fill=tc if tc != '#ffffff' else '#c62828')

    # Severity arrow on far right
    arr_x = W - 8
    draw.line([(arr_x, 50), (arr_x, H-10)], fill='#888888', width=3)
    draw.polygon([(arr_x, H-10), (arr_x-6, H-22), (arr_x+6, H-22)], fill='#888888')

    img = img.crop((0, 0, W, H))
    return img

# ═══════════════════════════════════════════════════════════════════════════════
# PIL DIAGRAM 3 — Management Algorithm
# ═══════════════════════════════════════════════════════════════════════════════
def make_management_algo():
    W, H = 900, 950
    img = Image.new('RGB', (W, H), '#f8fffe')
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 42], fill='#0d5c63')
    tw, _ = text_size(draw, 'VARICOSE VEIN MANAGEMENT ALGORITHM (NICE CG168)', pfb(15))
    draw.text(((W-tw)//2, 11), 'VARICOSE VEIN MANAGEMENT ALGORITHM (NICE CG168)', font=pfb(15), fill='#ffffff')

    y = 55
    # Start box
    y = draw_box(draw, 450, y, [('Symptomatic Varicose Veins', pfb(13), '#ffffff'),
        ('Aching, heaviness, skin changes, ulcer, SVT, bleeding', pf(10), '#e0f4f5')],
        '#0d5c63', '#0d5c63', accent=False, min_w=400) + 10
    arrow_down(draw, 450, y, y+30); y += 30

    # ABPI box
    y = draw_box(draw, 450, y, [('Step 1: Measure ABPI (Ankle-Brachial Pressure Index)', pfb(12), '#0d3320'),
        ('Using hand-held Doppler probe + BP cuff', pf(10), '#2d5a3d'),
        ('Normal ABPI = 1.0-1.3', pf(10), '#2d5a3d')],
        '#0d5c63', '#d4edda', accent=True, min_w=380) + 8

    # Two branches from ABPI
    arrow_down(draw, 450, y, y+25); y += 25
    branch_y = y
    # Left branch (ABPI low)
    arrow_right(draw, 450, 200, branch_y+15, color='#c0392b')
    left_end = draw_box(draw, 170, branch_y+5,
        [('ABPI < 0.8', pfb(11), '#ffffff'), ('Significant arterial disease', pf(10), '#ffe0e0')],
        '#c0392b', '#c0392b', accent=False, min_w=240)
    arrow_down(draw, 170, left_end, left_end+20)
    draw_box(draw, 170, left_end+20,
        [('Compression CONTRAINDICATED', pfb(10), '#7b0000'),
         ('Refer to Vascular Surgery', pf(10), '#7b0000'),
         ('Arterial assessment first', pf(10), '#7b0000')],
        '#c0392b', '#fde8e8', accent=True, min_w=240)

    # Right branch (ABPI normal)
    arrow_right(draw, 450, 700, branch_y+15, color='#0d5c63')
    right_top = draw_box(draw, 730, branch_y+5,
        [('ABPI > 0.8 (normal)', pfb(11), '#ffffff'), ('Venous treatment possible', pf(10), '#e0f4f5')],
        '#0d5c63', '#0d5c63', accent=False, min_w=240)
    arrow_down(draw, 730, right_top, right_top+20)
    rt2 = draw_box(draw, 730, right_top+20,
        [('NICE referral criteria met?', pfb(11), '#0d3320'),
         ('(trunk varices / skin changes / SVT / bleed / ulcer)', pf(9), '#2d5a3d')],
        '#0d5c63', '#d4edda', accent=True, min_w=240) + 8
    arrow_down(draw, 730, rt2, rt2+25); rt2 += 25
    rt3 = draw_box(draw, 730, rt2,
        [('Duplex Ultrasound Mapping', pfb(11), '#0d3320'),
         ('Maps incompetent veins, SFJ/SPJ status', pf(10), '#2d5a3d'),
         ('Excludes deep vein incompetence', pf(10), '#2d5a3d')],
        '#0d5c63', '#d4edda', accent=True, min_w=240) + 8

    # Three treatment options under duplex
    arrow_down(draw, 730, rt3, rt3+20); rt3 += 20

    opt_y = rt3
    tx_opts = [
        (560, '#1a8a94', '#e0f7fa', '1st LINE: EVLA or RFA', 'Endovenous Laser/Radiofrequency', 'Day case. Local anaesthesia. 90-95% success.'),
        (730, '#e6a817', '#fff9c4', '2nd LINE: Foam Sclerotherapy', 'Ultrasound-guided foam (UGFS)', 'If unsuitable for thermal ablation.'),
        (900, '#7d3c98', '#f5eef8', '3rd LINE: Surgery', 'High tie + strip + phlebectomy', 'If unsuitable for EVLA or UGFS.'),
    ]
    for tx_cx, brd, bg, t1, t2, t3 in tx_opts:
        draw_box(draw, tx_cx, opt_y,
            [(t1, pfb(10), brd), (t2, pf(9), '#333333'), (t3, pf(9), '#555555')],
            brd, bg, accent=True, min_w=190)

    # Conservative path (no referral criteria)
    cons_x = 450
    cons_y = branch_y + 180
    arrow_right(draw, 730, 540, cons_y-10, color='#666666')
    draw_box(draw, 540, cons_y-35,
        [('No NICE criteria: Conservative', pfb(10), '#444444'),
         ('Class II compression + Lifestyle', pf(9), '#555555')],
        '#888888', '#f0fafb', accent=False, min_w=200)

    final_h = opt_y + 120
    img = img.crop((0, 0, W, final_h))
    return img

# ─────────────────────────────────────────────
# BUILD STORY
# ─────────────────────────────────────────────
story = []

# ── TITLE ─────────────────────────────────────────────────────────────────────
story.append(Spacer(1,8))
story.append(Paragraph('VARICOSE VEINS', sTitle))
story.append(Paragraph('Venous Disease from Valve to Ulcer — MRCP Parts 1, 2 &amp; PACES Complete Guide', sSub))
story.append(Paragraph(
    'Covering: Venous anatomy • CEAP classification • Duplex USS • ABPI '
    '• Trendelenburg test • EVLA • Foam sclerotherapy • Compression therapy '
    '• Venous ulcers • Prescribing (Ganesh &amp; Kuruvilla)', sSub))
divider(story)

# ── §1 OVERVIEW ───────────────────────────────────────────────────────────────
sec_header('1. OVERVIEW &amp; KEY FACTS', story)
story.append(Paragraph(
    'Imagine 30% of the adults around you have tortuous, dilated, rope-like veins running '
    'under the skin of their legs — that is the scale of varicose vein disease. <b>Varicose veins</b> '
    '(from the Latin <i>varix</i> = twisted) are abnormally dilated, tortuous superficial veins '
    'greater than 3mm in diameter, caused by incompetent venous valves that allow blood to '
    'fall backwards (reflux) rather than travelling upward to the heart. They are not merely cosmetic — '
    'they are the commonest cause of venous leg ulcers, which cost the NHS an estimated '
    '£1-2 billion per year and cause enormous suffering. NICE Guideline CG168 (2013) '
    'transformed treatment: endovenous laser ablation (EVLA) — not surgical stripping — is now '
    'the first-line treatment for suitable patients.', sBody))
story.append(Spacer(1,4))

kf_data = [
    ['Key Fact', 'Value', 'Why It Matters Clinically'],
    ['Prevalence in adults', '30% (1 in 3)', 'One of the commonest conditions in general practice and vascular clinics'],
    ['Sex ratio', 'Female:Male = 2:1 (some studies equal)', 'Pregnancy, oestrogen/progesterone increase venous wall compliance'],
    ['GSV (Great Saphenous Vein) incompetence', '~75% of cases', 'Most varicose veins arise from SFJ (saphenofemoral junction) valve failure'],
    ['SSV (Small Saphenous Vein) incompetence', '~25% of cases', 'SSV varices = posterior calf distribution; SPJ anatomy is variable'],
    ['Normal venous pressure at ankle (standing)', '~90 mmHg', 'This is the hydrostatic pressure of a column of blood from heart to ankle'],
    ['Venous pressure at ankle (walking — normal)', '~30 mmHg', 'Calf muscle pump reduces pressure by 66% — this is the ambulatory venous pressure (AVP)'],
    ['Venous pressure at ankle (walking — varicose)', '60-90 mmHg', 'AVP stays high = venous hypertension = root cause of ALL complications'],
    ['Venous leg ulcers caused by venous disease', '>80%', 'The most important long-term complication; can take years to develop'],
    ['NICE first-line treatment (CG168, 2013)', 'Endovenous thermal ablation (EVLA/RFA)', 'Replaced surgical stripping; day case, local anaesthesia, 90-95% success at 5 years'],
    ['Lifetime recurrence risk after any treatment', '20-40% at 5 years', 'Neovascularisation at SFJ after surgery; incomplete treatment; new valve failure'],
]
story.append(plain_table(kf_data, [CW*0.30, CW*0.22, CW*0.48]))
divider(story)

# ── §2 ANATOMY ────────────────────────────────────────────────────────────────
sec_header('2. ANATOMY — The Two-System Highway of the Leg', story)
story.append(Paragraph(
    'Professor\'s teaching: <b>Imagine two separate road networks in the leg.</b> The deep system '
    '(motorway — thick-walled, running between the muscles) carries 90% of the venous blood back '
    'to the heart. The superficial system (country roads — thin-walled, just under the skin) carries '
    'the remaining 10%. They are connected by "slip roads" — the perforating veins — which have '
    'one-way valves allowing traffic only FROM the superficial TOWARDS the deep. '
    'When the main junction valve (the Saphenofemoral Junction) fails, the whole superficial '
    'system backs up with traffic — the veins dilate, elongate, and become tortuous. '
    'This is a varicose vein.', sBody))
story.append(Spacer(1,4))

anat_data = [
    ['Structure', 'Location', 'Drains Into', 'Clinical Relevance'],
    ['GSV (Great Saphenous Vein)\n— longest vein in body',
     'Begins at medial dorsal foot venous arch, runs anterior to medial malleolus, ascends medial calf and thigh',
     'Femoral vein at SFJ (Saphenofemoral Junction) — 3-4cm below and lateral to pubic tubercle in the groin',
     'Site of 75% of varicose veins. Accessible for cannulation at medial ankle in emergencies. '
     'Harvested for coronary artery bypass graft (CABG) surgery.'],
    ['SSV (Small Saphenous Vein)',
     'Begins at lateral dorsal foot, runs posterior to lateral malleolus, ascends posterior calf',
     'Popliteal vein at SPJ (Saphenopopliteal Junction) behind the knee — level is variable (can be high)',
     'Site of 25% of varicose veins. Posterior calf distribution. Variable SPJ anatomy = must map with duplex before treatment.'],
    ['SFJ (Saphenofemoral Junction)',
     '3-4cm below and lateral to pubic tubercle in femoral triangle, groin',
     'The terminal valve of the GSV sits here. When this fails = reflux down entire GSV.',
     'The most important valve in the leg. Saphena varix = dilatation of terminal GSV at SFJ = looks like a groin lump = can mimic inguinal hernia.'],
    ['Femoral vein\n(deep — NOT superficial despite old name)',
     'Runs with femoral artery in the femoral triangle and adductor (Hunter\'s) canal',
     'Common femoral vein -> external iliac vein -> IVC',
     'Previously called "superficial femoral vein" (misleading name — IT IS A DEEP VEIN). DVT occurs here. The name is being retired to prevent confusion.'],
    ['Perforating veins\n(communicating veins)',
     'Pass through deep fascia (thick fibrous layer around muscles) connecting superficial to deep',
     'Superficial -> Deep (normal direction)',
     "Cockett's perforators (medial lower leg = 'blowout' varicosities beside ankle), Boyd's (below knee), Dodd's (lower thigh), Hunterian (mid-thigh). When valves fail = deep blood refluxes outward = massive varicosities beside ankle."],
    ['Venous valves',
     'Inside vein — bicuspid (two leaflets) semilunar valves, like the aortic valve in miniature',
     'Prevent retrograde (backward) flow under gravity',
     '15-20 valves in the GSV. Most valves in distal leg. IVC has NO valves. Reflux time >0.5 seconds on duplex USS = valve incompetence confirmed.'],
]
story.append(plain_table(anat_data, [CW*0.18, CW*0.22, CW*0.25, CW*0.35]))
story.append(Spacer(1,6))

# Anatomy PIL diagram
diag1 = make_venous_anatomy()
story.append(img2rl(diag1, CW))
story.append(Paragraph('Diagram 1: Venous anatomy of the leg — deep system (blue), superficial system (green), perforating veins (orange). Arrows show normal upward blood flow direction.',
    ParagraphStyle('Cap', fontName='DV-I', fontSize=8, leading=11, textColor=HexColor('#555555'), alignment=1)))
story.append(Spacer(1,4))
image_search_box('great saphenous vein anatomy medial thigh leg labelled', 'TeachMeAnatomy.info', story)
image_search_box('saphenofemoral junction anatomy ultrasound', 'Radiopaedia.org', story)
divider(story)

# ── §3 PHYSIOLOGY ─────────────────────────────────────────────────────────────
sec_header('3. PHYSIOLOGY — How Blood Gets Back Up the Leg', story)
story.append(Paragraph(
    'The heart pumps blood down the legs easily — gravity does the work. Getting it back UP '
    'against gravity is the challenge. The body uses three mechanisms, like a relay team. '
    'Understand these and you understand every complication of varicose veins.', sBody))
story.append(Spacer(1,3))

phys_data = [
    ['Mechanism', 'How It Works', 'Failure in Varicose Veins', 'Clinical Consequence'],
    ['1. Calf Muscle Pump\n(the most important)',
     'During walking, gastrocnemius and soleus (calf muscles) contract, squeezing the deep veins between them — like squeezing a toothpaste tube from the bottom. Blood is forced upward. Normal AVP (ambulatory venous pressure) drops from 90 mmHg at rest to 30 mmHg on walking — a 66% reduction.',
     'Valve-incompetent superficial veins allow blood to reflux back down during the refilling phase. The deep pump pushes blood up, but the superficial veins immediately let it fall back down again. AVP stays at 60-90 mmHg.',
     'Venous hypertension = the root cause of ALL complications: oedema, skin pigmentation, lipodermatosclerosis, ulceration. Immobility (e.g. long-haul flight, post-op bedrest) = calf pump inactive = DVT risk.'],
    ['2. Venous Valves\n(the one-way doors)',
     'Bicuspid leaflet valves snap shut immediately after blood flows past them, preventing reflux. 15-20 valves in the GSV alone. Reflux = failure of these valves to close competently.',
     'Valve cusps weaken and fail to meet in the centre — a gap forms. Blood falls backward (reflux). High pressure damages the next valve down. Progressive valve failure travels distally = the whole GSV becomes incompetent.',
     'Reflux time >0.5 seconds on duplex USS = valve incompetence. As each valve fails, the visible varicosity extends further down the leg.'],
    ['3. Respiratory Pump\n(suction effect)',
     'On inspiration (breathing in), the diaphragm descends, creating negative pressure inside the chest cavity. This sucks venous blood upward into the thorax — like a vacuum cleaner turning on and drawing blood centrally.',
     'Not directly impaired by varicose veins — but relevant in hospitalised, intubated patients where positive-pressure ventilation reverses this (pushes, does not suck).',
     'Relevant clinically: explain to patients why elevating the leg AND deep breathing exercises after surgery both help prevent DVT — they activate this mechanism.'],
    ['Starling Forces\n(why oedema develops)',
     'Capillary hydrostatic pressure pushes fluid OUT into the tissues. Plasma oncotic pressure (from albumin in blood) pulls fluid back IN. Normally balanced.',
     'Venous hypertension raises capillary hydrostatic pressure. More fluid is forced out into the interstitium than can be returned. Fibrinogen also leaks out, forms a fibrin cuff around capillaries.',
     'Oedema = excess interstitial fluid. Fibrin cuffs block oxygen delivery to skin cells = skin ischaemia = lipodermatosclerosis = ulceration. This is why venous oedema is a PRE-ULCER warning sign.'],
]
story.append(plain_table(phys_data, [CW*0.15, CW*0.28, CW*0.27, CW*0.30]))
divider(story)

# ── §4 PATHOLOGY ──────────────────────────────────────────────────────────────
sec_header('4. PATHOLOGY &amp; PATHOPHYSIOLOGY', story)
story.append(Paragraph(
    '<b>Always ask: Why does THIS patient have varicose veins?</b> 80% are primary (valves simply '
    'wear out). 20% are secondary — caused by something else. Missing the secondary cause means '
    'treating the wrong problem. A 25-year-old with unilateral varicose veins and pelvic pain '
    'has a tumour until proven otherwise.', sBody))
story.append(Spacer(1,4))

path_data = [
    ['Type', 'Mechanism', 'Risk Factors / Causes', 'Key Investigation to Exclude', 'MRCP Teaching Point'],
    ['Primary varicose veins\n(80% of cases)',
     'Intrinsic weakness of vein wall collagen and/or valve cusp leaflets. Valve at SFJ fails first. Blood refluxes from femoral vein into GSV. High pressure transmitted distally. Each valve below fails in turn (progressive valve failure).',
     'Family history (50% have positive FHx), increasing age, female sex, prolonged standing, obesity, pregnancy (increases compliance transiently)',
     'Duplex USS to map incompetence. No additional investigations needed for typical primary VVs.',
     'Primary VVs = most common. Bilateral, progressive, genetic tendency. Treat the incompetent junction (SFJ/SPJ).'],
    ['Secondary: Post-thrombotic syndrome (most important secondary cause)',
     'DVT damages valve leaflets as the thrombus dissolves. Permanent valve incompetence in deep AND superficial veins. Deep venous hypertension causes reflux through perforators into superficial system.',
     'Previous DVT (even years prior), hypercoagulable states (thrombophilia), immobility, cancer',
     'Duplex USS for deep vein reflux and patency. Thrombophilia screen in young patients.',
     'Key: deep vein incompetence cannot be treated by superficial vein surgery. Must explain this to patient — VVs will improve but not resolve. Deep venous disease = lifelong compression.'],
    ['Secondary: Pelvic obstruction',
     'Tumour, lymph node mass, or May-Thurner syndrome (left common iliac artery compresses left common iliac vein against L5 vertebra) compress iliac veins. Back-pressure transmitted down to leg veins.',
     'Ovarian/uterine/rectal/prostate cancer. May-Thurner = young women, predominantly LEFT sided',
     'CT or MRI pelvis. Duplex of iliac veins.',
     'May-Thurner syndrome: young woman + left-sided varicose veins + no family history = consider iliac vein compression. Treatment: iliac vein stenting, THEN treat VVs.'],
    ['Secondary: Pregnancy',
     'Gravid uterus compresses IVC (inferior vena cava) and iliac veins. Progesterone relaxes smooth muscle in vein walls = veins become more compliant and dilate. Increased circulating blood volume by 40%.',
     'All trimesters; worsens with each pregnancy',
     'Clinical diagnosis. Duplex if DVT suspected.',
     'VVs often improve after delivery (IVC decompressed). Compression stockings during pregnancy are safe and effective. Do NOT perform EVLA or sclerotherapy in pregnancy.'],
    ['Secondary: AV fistula\n(arteriovenous)',
     'Abnormal direct connection between artery and vein. Arterialised blood (at arterial pressure ~120mmHg) enters the venous system — massively overwhelms valve capacity. Unusual distribution, atypical patient age.',
     'Congenital (Parkes Weber syndrome), post-traumatic, post-surgical (e.g. dialysis fistula), Klippel-Trenaunay',
     'Duplex Doppler shows high-flow pulsatile venous flow. Bruit/thrill palpable over VVs.',
     'Branham\'s sign (Nicoladoni sign): compress the AV fistula with digital pressure -> heart rate decreases (less venous return to right heart). Classic sign of haemodynamically significant AV fistula.'],
]
story.append(plain_table(path_data, [CW*0.15, CW*0.25, CW*0.20, CW*0.18, CW*0.22]))
story.append(Spacer(1,5))

story.append(Paragraph('The Fibrin Cuff Theory — How Venous Hypertension Causes Skin Breakdown', sH2))
story.append(Paragraph(
    'High ambulatory venous pressure forces fibrinogen (the clotting protein) out through '
    'the walls of the skin capillaries. Outside the capillary, fibrinogen is converted to '
    'fibrin — forming a stiff <b>fibrin cuff</b> around each tiny capillary, like wrapping '
    'a straw in electrical tape. This cuff acts as a barrier between the blood inside the '
    'capillary and the skin cells outside — oxygen and nutrients cannot diffuse across. '
    'White blood cells (leucocytes = the immune cells) become trapped in the cuff, release '
    'tissue-damaging enzymes (MMPs = matrix metalloproteinases, which break down collagen and '
    'tissue structure), and the skin gradually dies from the inside. The result: '
    '<b>lipodermatosclerosis</b> (hard, woody, indurated skin) progressing to '
    '<b>venous ulceration</b>. Meanwhile, broken-down red blood cells leak haemosiderin '
    '(the iron-containing pigment) into the skin, creating the characteristic '
    '<b>brown rust-staining</b> of the medial ankle.', sBody))
divider(story)

# ── §5 RISK FACTORS ───────────────────────────────────────────────────────────
sec_header('5. AETIOLOGY &amp; RISK FACTORS', story)
rf_data = [
    ['Risk Factor', 'Mechanism', 'Modifiable?', 'Clinical Note'],
    ['Family history (50% of patients)', 'Autosomal dominant tendency — defective collagen in vein walls and valve cusps', 'No', 'If parent has VVs, offspring have 60-90% lifetime risk. Take FHx routinely.'],
    ['Female sex', 'Oestrogen/progesterone increase venous wall compliance; pregnancy; higher body fat distribution', 'No', 'F:M = 2:1. Oral contraceptive pill and HRT both increase risk. Consider VTE risk with OCP.'],
    ['Increasing age', 'Progressive collagen degeneration; cumulative years of hydrostatic stress on valves', 'No', 'Prevalence rises sharply after age 30. Significant disease usually presents in 4th-6th decade.'],
    ['Pregnancy', 'IVC compression, progesterone, +40% blood volume increase', 'Partially (manage, not prevent)', 'Class II compression stockings from first trimester. Usually improves after delivery.'],
    ['Obesity (BMI >30)', 'Increased intra-abdominal pressure, compresses iliac veins; impaired calf pump efficiency', 'YES — weight loss', 'Weight loss reduces venous pressure and slows progression. Required before treatment in morbidly obese.'],
    ['Prolonged standing (occupational)', 'Static standing = calf pump does not activate (pump works only with walking). Constant high AVP all day.', 'YES — job modification / regular walking breaks', 'Surgeons, teachers, hairdressers, retail workers. Advise: shift weight heel-to-toe while standing to activate the pump.'],
    ['Previous DVT', 'Post-thrombotic syndrome: permanent valve damage', 'No (prevent further DVT)', 'Always ask about DVT history. Secondary VVs = deep venous incompetence may coexist.'],
    ['Constipation / straining', 'Valsalva manoeuvre raises intra-abdominal pressure, impedes venous return from legs', 'YES — diet, laxatives', 'Ask about bowel habits. Chronic constipation worsens VVs over years.'],
    ['Previous VV surgery', 'Neovascularisation at SFJ ligation site — new tiny vessels regrow and reconnect the reflux pathway', 'No (prevent with good primary surgery)', 'Recurrent VVs after surgery = complex anatomy. Foam sclerotherapy or repeat EVLA preferred over re-do surgery.'],
]
story.append(plain_table(rf_data, [CW*0.22, CW*0.30, CW*0.13, CW*0.35]))
divider(story)

# ── §6 CLINICAL FEATURES ──────────────────────────────────────────────────────
sec_header('6. CLINICAL FEATURES — Symptoms and Signs', story)
story.append(Paragraph(
    'The classic varicose vein patient: a woman in her 40s who has had two pregnancies, '
    'works as a nurse, and stands for hours each shift. She describes her legs as "heavy and '
    'aching" by the end of the day, "like they are full of lead." Her ankles swell by evening '
    'and are normal in the morning. She itches over her varicose veins. She has noticed '
    'brown discolouration around her right ankle. This history alone — you have already '
    'diagnosed C4a venous disease without looking at her legs.', sBody))
story.append(Spacer(1,4))

cf_data = [
    ['Feature', 'Description', 'Pathological Mechanism', 'CEAP Grade'],
    ['Aching / heaviness / fatigue in legs',
     'Worse at end of day. Worse after prolonged standing. BETTER with walking and with leg elevation. Classic "heavy legs by evening."',
     'Venous distension. High venous pressure. Activation of venous nociceptors (pain receptors in vein wall).',
     'C2-C3'],
    ['Ankle swelling (oedema)',
     'Pitting oedema worse in evenings, resolves after overnight elevation. Press with thumb for 10 seconds — releases = pitting = fluid in interstitium.',
     "Venous hypertension exceeds Starling's balance point: more fluid pushed out of capillaries than drawn back in. Fibrin cuffing worsens over time.",
     'C3'],
    ['Itching (pruritus)',
     'Over the course of the varicose veins, especially the medial calf. Can lead to scratching -> skin breakdown -> entry point for infection.',
     'Release of inflammatory mediators (histamine, prostaglandins) from mast cells trapped in venous stasis. Also part of venous eczema.',
     'C3-C4a'],
    ['Haemosiderin pigmentation',
     'Brown/rust-coloured staining of the skin at the medial gaiter area (above and around the medial malleolus). Does not blanch. Permanent once established.',
     'Red blood cells escape from high-pressure capillaries, break down in tissue. Haemosiderin (iron from haemoglobin) deposits permanently in skin macrophages.',
     'C4a'],
    ['Venous eczema (stasis eczema)',
     'Itchy, red, weeping, scaly, crusting skin over and around varicose veins. Can be mistaken for cellulitis (but bilateral, not spreading, not tender to deep palpation).',
     'Inflammatory response to venous stasis. Triggered by topical products applied to the skin (contact sensitisation is common in venous eczema patients — many become allergic to lanolin, neomycin, preservatives).',
     'C4a'],
    ['Lipodermatosclerosis (LDS)',
     '"Hardening" of the skin and subcutaneous fat of the lower leg — feels like wood when you palpate it. The leg develops an "inverted champagne bottle" shape — narrowed lower calf, full upper calf. Tender in acute phase (acute LDS = red, hot, tender = often misdiagnosed as cellulitis).',
     'Chronic fibrin cuffing, leucocyte trapping, collagen replacement of subcutaneous fat (liposclerosis). The subcutaneous tissue is literally replaced by fibrous tissue.',
     'C4b'],
    ['Atrophie blanche',
     'Smooth, white, scarred plaques surrounded by telangiectasia and haemosiderin pigmentation. Usually above and around medial malleolus. Ivory-white, stellate (star-shaped) appearance.',
     'Capillary destruction — areas where ALL the capillaries have been destroyed by chronic inflammation. Zero blood supply = ANY breach in the skin will not heal = EXTREMELY HIGH ulcer risk.',
     'C4b'],
    ['Venous ulcer',
     'Shallow ulcer at medial gaiter area (around and above medial malleolus). Irregular, well-defined sloping edges. Base: pink granulation tissue. Surrounding: LDS, pigmentation, eczema. NOT on the foot/heel (unlike arterial). Often painless unless infected.',
     'End-stage venous hypertension. Skin ischaemia from fibrin cuffing. Minor trauma (or none) triggers ulceration in already-compromised skin.',
     'C6 (active) / C5 (healed)'],
    ['Corona phlebectatica',
     'Fan-shaped array of tiny blue/red intradermal vessels radiating around the medial or lateral ankle. Like a fan-shaped spider web at the ankle.',
     'Marker of severe chronic venous hypertension — high pressure in the perforating veins forces blood into the tiny dermal capillaries.',
     'C4a-b (strongly predicts progression)'],
    ['Superficial thrombophlebitis (SVT)',
     'Warm, tender, red, firm, palpable cord along the varicose vein. The vein clots (thromboses) and becomes inflamed. Usually self-limiting but can propagate to DVT via SFJ.',
     'Stagnant blood in dilated varicose vein activates coagulation cascade. Vein wall inflammation. If thrombus reaches the SFJ = direct propagation into the femoral vein.',
     'Complication of C2+'],
]
story.append(plain_table(cf_data, [CW*0.20, CW*0.30, CW*0.30, CW*0.20]))
divider(story)

# ── §7 CEAP CLASSIFICATION ────────────────────────────────────────────────────
sec_header('7. CEAP CLASSIFICATION — The Severity Staging System', story)
story.append(Paragraph(
    'CEAP stands for <b>C</b>linical severity, <b>E</b>tiology, <b>A</b>natomy, '
    '<b>P</b>athophysiology. In clinical practice, we most commonly use just the '
    '<b>C (Clinical)</b> part. Think of it as the "cancer staging" of venous disease — '
    'the higher the C number, the worse the disease, the more urgent the treatment. '
    'NICE uses CEAP to determine who needs referral and what treatment to offer.', sBody))
story.append(Spacer(1,4))

ceap_data = [
    ['CEAP Grade', 'Clinical Finding', 'Appearance', 'NICE Action', 'MRCP Teaching Point'],
    ['C0', 'No visible or palpable signs', 'Normal-looking leg but symptoms present (aching, heaviness)',
     'Conservative management only (compression, lifestyle)', 'Symptoms without signs are still real. Always check for symptoms in history.'],
    ['C1', 'Telangiectasia or reticular veins',
     'Spider veins (<1mm, red/purple) or reticular veins (1-3mm, blue). NOT raised above skin surface.',
     'Conservative. No NICE referral criteria unless symptomatic with other criteria.',
     'C1 is cosmetic venous disease. NHS does not fund treatment for cosmetic indications. Private treatment only.'],
    ['C2', 'Varicose veins', 'Raised, tortuous, dilated veins >3mm. The classic "varicose vein."',
     'Refer to vascular services IF symptomatic. NICE CG168: offer EVLA first-line.',
     'C2 = trunk varicose veins = one of the NICE referral criteria. Document distribution (GSV vs SSV territory).'],
    ['C3', 'Oedema', 'Ankle pitting oedema. No skin changes yet. Socks leave marks.',
     'Refer. Compression class II. Duplex USS.',
     'Oedema at this stage = significant venous hypertension. Risk of skin breakdown is escalating.'],
    ['C4a', 'Pigmentation OR venous eczema',
     'Haemosiderin brown staining and/or itchy, scaly, eczematous skin around the medial ankle.',
     'Refer urgently. Compression class II-III (ABPI first). Emollients + mild topical steroid for eczema.',
     'C4a is when the skin is telling you it is being damaged. Do not delay treatment further.'],
    ['C4b', 'Lipodermatosclerosis OR atrophie blanche',
     'Hard, woody skin. Inverted champagne bottle. White scarred patches with no capillaries.',
     'Urgent vascular referral. Priority treatment — EVLA if suitable to prevent ulceration.',
     'C4b = the ulcer has not happened yet but is highly likely. This is the last chance to prevent C6.'],
    ['C5', 'Healed venous ulcer',
     'Scarred, hyperpigmented area where an ulcer has healed. Surrounding LDS.',
     'Lifelong class II-III compression. Treat incompetent veins (reduces 70% -> 25% recurrence).',
     'C5 WITHOUT treating the underlying vein = 70% chance of recurrence within 5 years. EVLA reduces this dramatically.'],
    ['C6', 'Active venous ulcer',
     'Open ulcer at medial gaiter area. Variable size. Granulation tissue base. +/- infection.',
     'URGENT. Four-layer compression bandaging + dressings. ABPI mandatory. Vascular referral for EVLA (heals ulcer faster).',
     'C6 = the worst end of the spectrum. Most common cause of chronic non-healing wounds. Costs NHS >1 billion per year.'],
]
story.append(plain_table(ceap_data, [CW*0.10, CW*0.18, CW*0.22, CW*0.25, CW*0.25]))
story.append(Spacer(1,5))

# CEAP PIL diagram
diag2 = make_ceap_diagram()
story.append(img2rl(diag2, CW))
story.append(Paragraph('Diagram 2: CEAP classification — C0 (no disease) to C6 (active ulcer). Each stage represents worsening venous hypertension and skin damage.',
    ParagraphStyle('Cap2', fontName='DV-I', fontSize=8, leading=11, textColor=HexColor('#555555'), alignment=1)))
divider(story)

# ── §8 CLINICAL EXAMINATION ───────────────────────────────────────────────────
sec_header('8. CLINICAL EXAMINATION — The Full Varicose Vein Examination', story)
story.append(Paragraph(
    'The golden rule: <b>ALWAYS examine the patient standing.</b> Varicose veins collapse when the '
    'patient lies down — you will miss them completely. Examine from the front, both sides, and behind. '
    'The examination has three phases: Look (inspect), Feel (palpate), Test (special tests). '
    'In PACES, describe everything you see systematically before you touch anything.', sBody))
story.append(Spacer(1,4))

exam_data = [
    ['Step', 'Action', 'What You Are Looking/Feeling For', 'Professor\'s Teaching Point'],
    ['1. Inspection\n(patient STANDING)',
     'Expose both lower legs completely from groin to foot. Ask patient to stand facing you. Examine front, lateral, and posterior aspects.',
     'Distribution of varices: medial thigh/calf = GSV territory; posterior calf = SSV territory. Document which segments are affected.',
     'Never say "bilateral varicose veins" without noting if they are symmetric. Asymmetric = secondary cause until excluded. Bilateral = more likely primary or bilateral DVT history.'],
    ['2. Skin changes\n(inspect)',
     'Inspect the medial gaiter area specifically (ankle to mid-calf, medial surface). Look at both ankles.',
     'Haemosiderin pigmentation (brown), venous eczema (red/scaly), LDS (indurated skin), atrophie blanche (white patches), active ulcer, corona phlebectatica (ankle fan veins).',
     'The skin tells you the severity. You can determine the CEAP grade from inspection alone before you touch the patient.'],
    ['3. Scars and groin\n(inspect)',
     'Look in both groins for scars (horizontal scar just below inguinal ligament = previous SFJ ligation). Look behind both knees (popliteal fossa scar = previous SPJ ligation).',
     'Previous surgery changes anatomy and complicates re-treatment. Neovascularisation at SFJ tie is the commonest cause of recurrent VVs after surgery.',
     'If there is a groin scar = ask: "Have you had varicose vein surgery before?" These patients need duplex before ANY further treatment.'],
    ['4. Saphena varix\n(inspect + palpate groin)',
     'Look in the right then left groin for a swelling just below the inguinal ligament. Ask patient to cough. Palpate the swelling.',
     'A saphena varix is a dilatation of the terminal GSV at the SFJ. It appears as a soft, compressible, bluish groin swelling. A COUGH IMPULSE is felt (blood falls through incompetent SFJ on coughing).',
     'DIFFERENTIAL: inguinal hernia! Key differences: saphena varix (1) disappears completely when patient lies flat, (2) a fluid thrill is transmitted from tapping the VVs below, (3) no bowel sounds audible over it. Duplex USS confirms.'],
    ['5. Palpation',
     'With patient standing, palpate the varicose veins gently. Assess: temperature (warmth = SVT or inflammation), tenderness (SVT), skin texture of gaiter area (hard = LDS, normal = early disease).',
     'Warm, tender, firm cord along a vein = superficial thrombophlebitis. Hard, woody, non-pitting skin = LDS. Pitting oedema = press thumb at medial malleolus for 10 seconds.',
     'Always palpate the ENTIRE length of the varicose veins. An apparently simple GSV varicosity may have a thrombosed segment that the patient has not noticed.'],
    ['6. Percussion\n(Tap / Schwartz test)',
     'Ask patient to remain standing. Place fingers of your left hand on the varicosity in the thigh. With your right hand, tap sharply on the varicosity lower down (calf level).',
     'A transmitted impulse (fluid thrill) felt in the thigh = the vein contains a continuous column of blood with no functional valves between the tap point and your fingers. Positive = varicosity confirmed.',
     'Like tapping one end of a water-filled hosepipe and feeling the pressure wave at the other end. Works only if the fluid column is continuous and uninterrupted by competent valves.'],
    ['7. Cough impulse\nover SFJ',
     'Place your fingers firmly over the SFJ (3-4cm below and lateral to the pubic tubercle). Ask the patient to cough sharply.',
     'A transmitted impulse FELT under your fingers = SFJ valve is incompetent. The sudden rise in intra-abdominal pressure on coughing transmits directly through the open valve into the GSV.',
     'Same principle as checking for an indirect inguinal hernia cough impulse. Distinguishes a saphena varix from an inguinal hernia: hernia = reducible separately; saphena varix = fluid thrill from below.'],
    ['8. Trendelenburg\n(Tourniquet) Test',
     'Step 1: Patient lies supine, elevate leg 45 degrees to empty the veins (about 60 seconds). Step 2: Apply digital pressure (or tourniquet) firmly at the SFJ. Step 3: Ask patient to stand quickly. Step 4a: Observe for filling from below (feet upward) while pressure maintained. Step 4b: Release pressure suddenly — observe for filling from above.',
     'Filling from BELOW while pressure maintained = incompetent perforating veins below the tourniquet are refilling the superficial system. Rapid filling from ABOVE on pressure release = incompetent SFJ — blood falls back down through the open junction the moment you release.',
     'Interpret the test in stages. Both types of filling can occur together (most common). If tourniquet at mid-thigh controls varices when patient stands = incompetence is ABOVE the tourniquet (SFJ). If not controlled = perforator incompetence below the tourniquet.'],
    ['9. Neurovascular\nassessment',
     'Palpate: dorsalis pedis pulse (dorsum of foot, between 1st and 2nd metatarsal bases) and posterior tibial pulse (behind medial malleolus). Test light touch on dorsum of foot. Check capillary refill in toenails.',
     'Absent pulses = peripheral arterial disease = ABPI <0.8 = compression CONTRAINDICATED. Reduced sensation = peripheral neuropathy = diabetic foot risk.',
     'NEVER prescribe compression without first assessing the arterial supply. This is the commonest avoidable harm in venous disease management.'],
    ['10. PACES summary\nstatement',
     'After completing examination, present your findings formally.',
     '"These are varicose veins in the distribution of the great saphenous vein on the medial aspect of the right lower limb. There is haemosiderin pigmentation at the medial gaiter area. The Trendelenburg test demonstrates saphenofemoral junction incompetence. CEAP grade C4a. I would perform duplex USS and ABPI measurement before recommending treatment."',
     'Always state: distribution, skin changes, CEAP grade, which test was positive, and your next investigation. This is the format examiners expect.'],
]
story.append(plain_table(exam_data, [CW*0.12, CW*0.25, CW*0.33, CW*0.30]))
story.append(Spacer(1,4))
image_search_box('varicose vein examination OSCE Trendelenburg test', 'YouTube — search Geeky Medics', story)
image_search_box('lipodermatosclerosis atrophie blanche venous eczema photos', 'DermNetNZ.org', story)
divider(story)

# ── §9 INVESTIGATIONS ─────────────────────────────────────────────────────────
sec_header('9. INVESTIGATIONS', story)
story.append(Paragraph(
    'In modern vascular practice, the duplex ultrasound has replaced nearly every other '
    'investigation for varicose veins. But you must know what each test shows, because '
    'MRCP Part 1 tests the theory and clinical practice demands you know WHAT you are '
    'requesting and WHY.', sBody))
story.append(Spacer(1,3))

inv_data = [
    ['Investigation', 'What It Shows', 'When to Request', 'Normal / Abnormal Values', 'Clinical Action'],
    ['Duplex Ultrasound (USS)\n— the single most important test',
     'B-mode grey-scale image shows vein anatomy. Doppler measures blood flow direction and velocity. Manual calf compression test: normal = brief forward flow then valve closure (<0.5 sec refill). Abnormal = prolonged reflux >0.5 seconds = incompetent valve.',
     'ALWAYS before any interventional treatment (NICE CG168). To diagnose incompetence (SFJ, SPJ, perforators). To exclude concurrent DVT. To map anatomy before EVLA.',
     'Reflux >0.5 seconds = valve incompetence. GSV diameter >5mm at SFJ = significant incompetence. Tibiofibular clear space (as reference).',
     'If DVT found = treat DVT first (anticoagulate, then reassess VVs 3 months later). If no DVT + reflux mapped = proceed to EVLA/foam/surgery.'],
    ['ABPI\n(Ankle-Brachial Pressure Index)',
     'Ratio of ankle systolic BP to brachial (arm) systolic BP. Measured with hand-held Doppler probe + standard sphygmomanometer (BP cuff). Ask patient to lie flat for 10 min first. Measure brachial pressure in both arms. Apply cuff to ankle, use Doppler to find dorsalis pedis/posterior tibial signal, inflate and record systolic.',
     'MANDATORY before prescribing any compression therapy. Before surgery (baseline). In all patients >50 years or diabetic.',
     '>1.3 = calcified arteries (common in diabetes/renal failure) — use toe-brachial index instead. 0.9-1.3 = normal. 0.8-0.9 = mild PAD (peripheral arterial disease). 0.5-0.8 = significant PAD — reduced compression only under specialist supervision. <0.5 = severe PAD = critical limb ischaemia.',
     'ABPI <0.8 = FULL COMPRESSION CONTRAINDICATED. Refer to vascular for arterial assessment. Treat arterial disease first. ABPI 0.8-0.9: Class I compression (14-17mmHg) only under specialist supervision.'],
    ['FBC\n(Full Blood Count)',
     'Haemoglobin (anaemia), white cell count (infection), platelets',
     'If venous ulcer present (exclude anaemia slowing healing). If cellulitis/infected ulcer (leucocytosis = white cell count raised). Pre-operatively.',
     'Hb normal: Male >130 g/L, Female >120 g/L. WBC 4-11 x10^9/L.',
     'Anaemia: investigate cause, treat with iron/folate/B12. If WBC raised + clinically infected ulcer: systemic antibiotics.'],
    ['CRP / ESR\n(Inflammatory markers)',
     'CRP (C-reactive protein) rises within hours of inflammation. ESR (erythrocyte sedimentation rate) rises more slowly. Both non-specific markers of inflammation/infection.',
     'If thrombophlebitis suspected. If infected ulcer. If cellulitis. Baseline before antibiotics.',
     'CRP normal <10 mg/L. Raised CRP = confirms active infection/inflammation.',
     'CRP >100 + spreading cellulitis = systemic infection = IV antibiotics + hospital admission may be needed.'],
    ['Wound swab\n(for infected ulcers)',
     'Identifies causative organisms and their antibiotic sensitivities (MC&S = microscopy, culture and sensitivity).',
     'ONLY if clinical signs of active infection: increased pain, odour, purulence, spreading cellulitis >2cm from wound edge, systemic signs (fever, raised CRP/WBC). NOT for routine colonisation.',
     'All chronic wounds are colonised (bacteria present but not causing active infection). A positive swab without clinical infection = do NOT treat with antibiotics.',
     'Staphylococcus aureus (most common) = flucloxacillin. MRSA = doxycycline or trimethoprim. Pseudomonas = ciprofloxacin. Anaerobes (foul-smelling) = metronidazole. Always treat the patient, not just the swab.'],
    ['Thrombophilia screen',
     'Antithrombin III, Protein C, Protein S (natural anticoagulants — deficiency = hypercoagulable). Factor V Leiden (activated protein C resistance — most common thrombophilia in Europeans). Prothrombin gene mutation. Antiphospholipid antibodies (APS = lupus anticoagulant + anticardiolipin antibodies).',
     'Young patient (<45 years) with DVT-related secondary VVs. Recurrent DVT. Unusual site DVT. Family history of thrombosis.',
     'Factor V Leiden present in ~5% of Europeans but only a minority develop DVT.',
     'Confirmed thrombophilia may require lifelong anticoagulation. Refer to haematology. Affects all future surgical and prescribing decisions.'],
    ['Blood glucose / HbA1c',
     'HbA1c (glycated haemoglobin — reflects average blood glucose over past 3 months) identifies undiagnosed diabetes or poor diabetic control.',
     'All patients with venous ulcers (diabetes impairs wound healing and adds neuropathic and arterial components).',
     'HbA1c >48 mmol/mol (6.5%) = diabetes. 42-47 = pre-diabetes.',
     'Poor glycaemic control = delayed wound healing = prolonged ulcer = amputation risk. Optimise HbA1c before and during ulcer treatment.'],
]
story.append(plain_table(inv_data, [CW*0.16, CW*0.26, CW*0.18, CW*0.20, CW*0.20]))
story.append(Spacer(1,4))
image_search_box('duplex ultrasound varicose vein reflux test demonstration', 'YouTube', story)
image_search_box('ABPI measurement technique Doppler probe ankle', 'YouTube', story)
divider(story)

# ── §10 MANAGEMENT ────────────────────────────────────────────────────────────
sec_header('10. MANAGEMENT — Conservative, Interventional, and Ulcer Care', story)
story.append(Paragraph(
    'NICE CG168 (2013) changed the management of varicose veins fundamentally. '
    'The key message: <b>endovenous thermal ablation (laser or radiofrequency) is now '
    'first-line treatment — not surgery.</b> Compression alone is not a cure. '
    'Conservative management is for patients who are unfit for or decline intervention.', sBody))
story.append(Spacer(1,4))

story.append(Paragraph('A. Conservative Management', sH2))
cons_data = [
    ['Conservative Measure', 'What To Do', 'Mechanism', 'Evidence / Limit'],
    ['Lifestyle: walking',
     'Regular brisk walking for at least 30 minutes daily. Avoid prolonged static standing (if unavoidable, shift weight heel-to-toe regularly while standing).',
     'Activates calf muscle pump. Reduces AVP. Improves venous return.',
     'Walking is the single most effective free intervention. Static standing is harmful — the pump only works with active plantar/dorsiflexion movement.'],
    ['Lifestyle: weight loss',
     'Target BMI <30 through diet and exercise. Refer to dietitian or weight management programme.',
     'Reduces intra-abdominal pressure, reduces compression on iliac veins, improves calf pump efficiency.',
     'Essential for obese patients before surgical intervention (increased surgical risk + poor outcomes). Slows disease progression.'],
    ['Lifestyle: leg elevation',
     'Elevate feet ABOVE heart level when sitting or resting. Raise foot of bed by 10-15cm.',
     'Gravity-assists venous return. Reduces AVP to near zero when fully supine and elevated. Reduces oedema.',
     'Effective for symptomatic relief. Does not reverse underlying incompetence. Patients must be specifically told: putting feet on a low footstool is NOT adequate — the feet must be above the heart.'],
    ['Compression stockings',
     'Class I (14-17 mmHg): mild symptoms, telangiectasia. Class II (18-24 mmHg): standard for symptomatic VVs, oedema, DVT prophylaxis. Class III (25-35 mmHg): severe disease, venous ulcers. Measure ankle circumference + calf circumference to select correct size. Put on in the morning before getting out of bed.',
     'External compression reduces the diameter of superficial veins. Increases venous velocity. Prevents reflux. Reduces AVP. Reduces oedema by increasing interstitial pressure.',
     'REQUIRE ABPI >0.8 before prescribing. Contraindicated: ABPI <0.8, acute DVT (first 24h), significant cardiac failure. Compliance is the biggest problem — many patients find them difficult to apply (prescribe a stocking applicator aid for elderly patients).'],
]
story.append(plain_table(cons_data, [CW*0.18, CW*0.25, CW*0.25, CW*0.32]))
story.append(Spacer(1,5))

story.append(Paragraph('B. NICE CG168 Referral Criteria and Treatment Pathway', sH2))
info_box(
    'NICE CRITERIA FOR REFERRAL TO VASCULAR SERVICES: Refer if symptomatic AND any of the following: '
    '(1) Trunk varicose veins, (2) Lower limb skin changes (C4-C6), '
    '(3) Superficial vein thrombosis (SVT), (4) Bleeding varicose veins, (5) Venous leg ulcer. '
    'Do NOT offer compression hosiery alone as definitive treatment to patients who are suitable for intervention.',
    story)

tx_data = [
    ['Treatment', 'Technique', 'Anaesthesia', 'Setting', 'Success Rate', 'When Used per NICE'],
    ['EVLA\n(Endovenous Laser Ablation)\nAlso called EVLT',
     'Laser fibre inserted into GSV via needle at the knee under USS guidance. Advanced to 2cm from SFJ. Tumescent local anaesthesia (dilute lidocaine) infiltrated around the vein to protect surrounding tissue and collapse the vein. Laser activated on withdrawal — heats vein wall to >70 degrees C, destroys endothelium. Vein scars shut permanently.',
     'Tumescent local anaesthesia (large volume very dilute lidocaine). No general anaesthesia needed.',
     'Day case (outpatient). Patient walks out same day.',
     '90-95% at 5 years',
     'FIRST-LINE for suitable anatomy (GSV straight enough to insert catheter). NICE preferred treatment.'],
    ['RFA\n(Radiofrequency Ablation, ClosureFAST)',
     'Same principle as EVLA but uses radiofrequency energy instead of laser. Delivered in 20-second cycles as catheter withdrawn in 6.5cm steps. Slightly less post-procedure bruising and pain than EVLA.',
     'Tumescent local anaesthesia',
     'Day case',
     '90-95% at 5 years',
     'FIRST-LINE — equivalent to EVLA. Some surgeons prefer RFA for its slightly better tolerability.'],
    ['UGFS\n(Ultrasound-Guided Foam Sclerotherapy)',
     'Sclerosant (polidocanol or STS = sodium tetradecyl sulphate) mixed with air as foam (Tessari technique: 1ml liquid + 4ml air via 3-way tap). Injected directly into varicose vein under USS guidance. Foam displaces blood = direct endothelial contact = chemical destruction = thrombosis = fibrosis. Compression stocking worn 2 weeks after.',
     'No anaesthesia — needle injection only',
     'Outpatient clinic',
     '70-80% at 5 years. Higher recurrence than EVLA.',
     'SECOND-LINE if unsuitable for thermal ablation. Also used for: recurrent VVs after surgery, SSV disease (variable SPJ anatomy), residual tributaries after EVLA, perforator incompetence.'],
    ['Surgical: High Tie + Strip',
     'Groin incision — GSV ligated flush with femoral vein at SFJ. All SFJ tributaries individually ligated (critical — failure to do so = recurrence via neovascularisation). Metal stripper inserted from groin to knee level — GSV stripped out. Phlebectomies (2mm stab incisions) remove tributaries. Strip to KNEE ONLY — not ankle (avoid saphenous nerve damage = medial lower leg numbness).',
     'General or spinal anaesthesia',
     'Day case or overnight stay',
     '75-85% at 5 years. Higher recurrence than EVLA.',
     'THIRD-LINE per NICE. Still widely performed. Preferred for very large veins, when anatomy unsuitable for endovenous approaches, or when patient/surgeon preference.'],
    ['Four-layer compression bandaging\n(for venous ulcers)',
     'Four-layer system (Profore or similar): Layer 1 = orthopaedic wool. Layer 2 = crepe bandage. Layer 3 = light compression bandage. Layer 4 = cohesive (self-adherent) bandage. Delivers 40 mmHg at ankle, graduating to 17 mmHg at knee. Changed 1-2x per week.',
     'None',
     'Community nursing / district nurses / clinic',
     '70% ulcer healing in 12 weeks with compression',
     'First-line for venous ulcers. ABPI >0.8 mandatory first. After ulcer heals, treat underlying incompetent vein to prevent recurrence.'],
]
story.append(plain_table(tx_data, [CW*0.14, CW*0.28, CW*0.12, CW*0.10, CW*0.12, CW*0.24]))
story.append(Spacer(1,5))

# Management algorithm PIL
diag3 = make_management_algo()
story.append(img2rl(diag3, CW))
story.append(Paragraph('Diagram 3: Varicose vein management algorithm (NICE CG168). ABPI measurement is the mandatory first step before any compression therapy.',
    ParagraphStyle('Cap3', fontName='DV-I', fontSize=8, leading=11, textColor=HexColor('#555555'), alignment=1)))
divider(story)

# ── §11 PHARMACOLOGY ──────────────────────────────────────────────────────────
sec_header('11. PHARMACOLOGY &amp; PRESCRIBING', story)
story.append(Paragraph(
    'Based on Ganesh &amp; Kuruvilla "Prescribing in General Medical Practice" and current NICE/BNF guidance. '
    'Every drug below has a specific clinical indication — know the dose, mechanism, contraindications, '
    'and monitoring for each.', sBody))
story.append(Spacer(1,3))

pharm_data = [
    ['Drug / Treatment', 'Dose', 'Indication', 'Mechanism', 'Key Side Effects', 'Contraindications', 'Monitoring'],
    ['Fondaparinux\n(Arixtra)',
     '2.5mg SC (subcutaneous = injected under skin) once daily for 45 days',
     'SVT (superficial vein thrombosis) extending to within 3cm of SFJ. High-risk SVT to prevent DVT/PE propagation.',
     'Selective factor Xa inhibitor (Xa = a key clotting factor; inhibiting it blocks the coagulation cascade). Does not require monitoring like warfarin.',
     'Bleeding. Injection site reactions. Rare: thrombocytopenia (low platelets).',
     'CrCl (creatinine clearance = measure of kidney function) <20ml/min (accumulates in renal failure = bleeding risk). Active bleeding. Bacterial endocarditis.',
     'Renal function (eGFR) before prescribing. Platelet count if prolonged use. No routine INR monitoring needed.'],
    ['Enoxaparin\n(Clexane) — LMWH',
     'Prophylactic: 40mg SC once daily (for DVT prevention post-surgery or immobility). Therapeutic: 1mg/kg SC twice daily (for confirmed DVT/PE treatment).',
     'DVT prophylaxis post-VV surgery. Treatment of DVT complicating varicose veins. Alternative to fondaparinux for high-risk SVT.',
     'LMWH (low molecular weight heparin) = inhibits factor Xa and IIa (thrombin). Predictable dose-response, less monitoring than unfractionated heparin.',
     'Bleeding. Injection site bruising. Rare: HIT (heparin-induced thrombocytopenia — immune reaction causing paradoxical clotting — rare with LMWH).',
     'Pregnancy (LMWH is SAFE in pregnancy — does NOT cross the placenta). Severe renal impairment (use UFH instead). Previous HIT.',
     'Platelet count before and every 5-7 days in first 3 weeks. Anti-Xa levels only if renal impairment or extremes of weight.'],
    ['Ibuprofen',
     '400mg three times daily (TDS) with food. Duration: 7-14 days for SVT.',
     'Pain and inflammation in superficial thrombophlebitis. Adjunct for VV pain.',
     'NSAID: non-selective COX (cyclo-oxygenase) inhibitor. Reduces prostaglandins = reduces inflammation, pain, fever.',
     'GI upset, peptic ulcer, GI bleeding. Fluid retention. Hypertension. Cardiovascular risk with prolonged use. Renal impairment.',
     'Peptic ulcer disease. eGFR <30 (renal failure). Heart failure. Pregnancy (especially 3rd trimester — premature ductus arteriosus closure). Aspirin-sensitive asthma.',
     'BP if prolonged use. Renal function if >4 weeks. Add PPI (omeprazole 20mg OD) if GI risk factors.'],
    ['Diclofenac\nTopical (gel)',
     '1.16% gel (Voltarol) applied 2-4g per application, 3-4 times daily to affected area. Rub in gently.',
     'Local pain from SVT. Reduces need for oral NSAIDs and their systemic side effects.',
     'Same as ibuprofen (COX inhibitor). Topical route = minimal systemic absorption = fewer systemic side effects.',
     'Local skin reactions. Rare systemic NSAID effects at low levels.',
     'Open skin wounds/ulcers. Known hypersensitivity to NSAIDs.',
     'No routine monitoring for topical use.'],
    ['Flucloxacillin',
     '500mg four times daily (QDS), 30 min before food, 7-14 days. IV: 1-2g QDS if severe.',
     'Infected venous ulcer (Staphylococcus aureus first-line coverage). Cellulitis around VVs or ulcers.',
     'Beta-lactam penicillinase-resistant antibiotic. Kills Staphylococcus aureus (including MSSA) by inhibiting bacterial cell wall synthesis.',
     'GI upset. Rash. Rare: cholestatic jaundice (hepatotoxicity, more common with high doses/prolonged use). Anaphylaxis.',
     'Penicillin allergy (use clarithromycin 500mg BD instead). Porphyria.',
     'LFTs (liver function tests) if treatment >2 weeks. Clinical review at 48h to confirm improving.'],
    ['Pentoxifylline\n(Oxpentifylline, Trental)',
     '400mg three times daily (TDS) by mouth with meals, up to 6 months.',
     'Venous leg ulcers — adjunct to compression to improve healing. NICE: recommended as optional adjunct when compression alone fails.',
     'Methylxanthine drug. Reduces blood viscosity: makes red blood cells more flexible (deformable) so they can squeeze through fibrin-cuffed capillaries more easily. Improves oxygen delivery to ischaemic skin around ulcer.',
     'GI: nausea, vomiting, dyspepsia (most common — take with food). Headache. Dizziness. Flushing.',
     'Recent MI (myocardial infarction). Cerebral haemorrhage. Severe hepatic impairment. Retinal bleeding.',
     'No specific routine monitoring. Review response at 6 weeks.'],
    ['Polidocanol\n(Aethoxysclerol) — sclerosant',
     '0.25-3% solution as foam. 1% foam for GSV/large tributaries. 0.25-0.5% for smaller veins. Max 2mg/kg per session. Foam made by Tessari method: 1ml liquid + 4ml air via 3-way tap.',
     'Ultrasound-guided foam sclerotherapy (UGFS) for varicose veins.',
     'Detergent: disrupts lipid bilayer of endothelial cells. Cell lysis -> exposure of sub-endothelial collagen -> platelet activation -> thrombus formation -> fibrosis -> vein occlusion.',
     'Skin staining (brown marks at injection sites — can persist months). Post-injection thrombophlebitis (painful hard cord = resolves in weeks). DVT (uncommon). Visual disturbances (foam microbubbles via PFO). Anaphylaxis (rare).',
     'Known PFO (patent foramen ovale — a hole in the heart between right and left atria — present in 25% of adults; foam bubbles can cross via PFO to cerebral circulation). Active DVT. Acute infection.',
     'Duplex USS after 1-2 weeks to confirm vein is closed. Watch for DVT symptoms.'],
    ['Hydrocortisone 1%\ncream/ointment',
     'Apply thinly twice daily to affected skin for up to 7-14 days. Not on open wounds.',
     'Venous (stasis) eczema around varicose veins.',
     'Mild topical corticosteroid. Reduces inflammatory cell activity in the skin, reduces histamine release, reduces itch and redness.',
     'Skin thinning with prolonged use. Perilesional skin fragility.',
     'Infected skin (do not apply to ulcers). Rosacea. Perioral dermatitis.',
     'Review at 7-14 days. Do not use for >4 weeks without review. If eczema worsens = suspect contact sensitisation (refer to dermatology for patch testing).'],
]
story.append(plain_table(pharm_data, [CW*0.13, CW*0.12, CW*0.13, CW*0.16, CW*0.15, CW*0.16, CW*0.15]))
divider(story)

# ── §12 COMPLICATIONS ─────────────────────────────────────────────────────────
sec_header('12. COMPLICATIONS', story)

comp_data = [
    ['Complication', 'Mechanism', 'Clinical Features', 'Emergency Management', 'Definitive Management'],
    ['Superficial Vein Thrombosis\n(SVT — also called superficial thrombophlebitis)',
     'Stagnant blood in dilated VVs activates coagulation cascade. Vein clots. Inflammation in vein wall.',
     'Warm, tender, red, firm, palpable cord along course of varicose vein. Patient systemically well (no fever unless infection or DVT).',
     'NSAIDs (ibuprofen 400mg TDS) + compression stocking + encourage walking. If within 3cm of SFJ: fondaparinux 2.5mg OD x 45 days (CALISTO trial) to prevent propagation to DVT.',
     'Treat underlying varicose veins (EVLA/foam/surgery) to prevent recurrence. Duplex USS to exclude concurrent DVT (present in 25% of SVT cases).'],
    ['Varicose Vein Bleeding\n(Emergency)',
     'Skin over medial ankle varicosities is thin and fragile (LDS destroys normal architecture). Vein ruptures from minor trauma or spontaneously. Bleeding is heavy because venous pressure at standing = 90 mmHg.',
     'Sudden severe bleeding from ankle/lower leg, often alarming in volume. Patient usually elderly, often on anticoagulants.',
     '1. LIE PATIENT DOWN IMMEDIATELY (drops venous pressure to near zero). 2. ELEVATE leg above heart level. 3. FIRM direct pressure for 10 min. 4. DO NOT apply tourniquet (increases venous pressure = worsens bleeding). Nearly always stops with this alone.',
     'Attend hospital if does not stop within 15 min. Once bleeding controlled: definitive VV treatment is a NICE indication for referral. This is a serious complication that predicts future life-threatening bleeding episodes.'],
    ['Venous Leg Ulcer\n(most serious complication)',
     'End-stage venous hypertension. Fibrin cuffing. Leucocyte trapping. Skin ischaemia. Atrophie blanche areas have NO capillaries — any breach = non-healing wound.',
     'Medial gaiter area (around medial malleolus). Shallow, sloping irregular edges. Pink granulation base. Surrounded by LDS and pigmentation. NOT on toes/heel (arterial). Can be painless unless infected.',
     'ABPI first. Four-layer compression bandaging (ABPI >0.8). Non-adherent dressing. Antibiotics ONLY if clinical infection (not just colonisation). Elevate, walk.',
     'Treat underlying venous incompetence: EVLA shown to heal ulcers faster and reduce recurrence from 70% to <25% at 5 years. Without treating the vein, 70% of healed ulcers recur.'],
    ['DVT (Deep Vein Thrombosis)',
     'Virchow\'s triad: (1) Stasis — blood pools in dilated VVs. (2) Endothelial injury — VV wall is abnormal. (3) Hypercoagulability — immobility, dehydration, post-op state.',
     'Unilateral calf/leg swelling, warmth, redness, tenderness. Wells score: clinical probability. D-dimer (if <500 ug/L = DVT excluded in low-probability patients).',
     'LMWH (enoxaparin 1mg/kg BD or 1.5mg/kg OD) until confirmed/excluded. Elevate limb. Do NOT massage.',
     'DOAC (apixaban 10mg BD x7 days then 5mg BD; or rivaroxaban 15mg BD x21 days then 20mg OD) for 3-6 months. Identify and treat precipitating cause.'],
    ['Post-Thrombotic Syndrome\n(PTS)',
     'After DVT: thrombus damages valve leaflets as it lyses. Permanent deep venous valve incompetence. Chronic deep venous hypertension. Secondary VVs, oedema, skin changes, ulceration develop over years.',
     'Chronic leg swelling, heaviness, aching, skin changes, VVs in a patient with history of DVT. Often worse than primary VVs. Duplex shows deep venous reflux.',
     'No acute management.',
     'Lifelong graduated compression. Physiotherapy (manual lymphatic drainage). Superficial VV treatment improves symptoms but deep incompetence persists. Iliac vein stenting if significant iliac stenosis on imaging.'],
    ['Saphena Varix',
     'Dilatation of terminal GSV at SFJ. Appears as a groin lump. Competent SFJ valve is absent.',
     'Soft, compressible, bluish groin swelling 3-4cm below inguinal ligament. Disappears completely when patient lies flat. Cough impulse positive. Fluid thrill transmitted from tapping varices below.',
     'No emergency management needed.',
     'Treat the underlying SFJ incompetence (EVLA or surgery). Important to distinguish from inguinal hernia (see exam section).'],
]
story.append(plain_table(comp_data, [CW*0.17, CW*0.20, CW*0.20, CW*0.22, CW*0.21]))
divider(story)

# ── §13 SPECIAL POPULATIONS ───────────────────────────────────────────────────
sec_header('13. SPECIAL POPULATIONS', story)

sp_data = [
    ['Population', 'Special Considerations', 'Safe Treatments', 'Avoid / Extra Caution'],
    ['Pregnancy',
     'VVs worsen with each pregnancy. IVC compressed by growing uterus. Progesterone relaxes vein walls. Usually partially improve after delivery. Treat symptoms during pregnancy conservatively.',
     'Class II graduated compression stockings from first trimester. Regular walking. Leg elevation. These are safe throughout pregnancy.',
     'EVLA, foam sclerotherapy, surgery: ALL contraindicated in pregnancy. NSAIDs: avoid in third trimester (risk of premature ductus arteriosus closure and oligohydramnios). Defer interventional treatment until 3 months postpartum.'],
    ['Elderly patients',
     'Higher prevalence of PAD (peripheral arterial disease) = ABPI more often <0.8 = compression contraindicated more frequently. Skin fragility = compression injury risk. Poor compliance with stockings (difficult to apply). Higher surgical risk.',
     'ABPI measurement is MANDATORY. Class I compression if tolerated and ABPI adequate. Community nursing support for dressing changes. Four-layer bandaging for ulcers by district nurse.',
     'Full compression bandaging without ABPI = catastrophic risk of arterial occlusion. Assess fall risk before surgery. Stocking applicator aids prescribed routinely.'],
    ['Diabetes mellitus',
     'Peripheral neuropathy: cannot feel pressure sores from compression. Peripheral arterial disease: ABPI frequently <0.8, falsely elevated due to calcification (use toe-brachial index instead). Impaired wound healing. Mixed ulcers (venous + arterial + neuropathic) are common.',
     'Optimise HbA1c. ABPI/TBI (toe-brachial index) before any compression. Multidisciplinary foot/wound care team. Proper foot care education.',
     'Full compression if ABPI <0.8 or calcified arteries without TBI. Flucloxacillin for infected ulcers — check renal function (many diabetics have CKD). Avoid NSAIDs if CKD.'],
    ['Klippel-Trenaunay Syndrome\n(congenital)',
     'Triad (all on same limb): port wine stain + varicose veins + limb hypertrophy. Deep veins may be absent or hypoplastic (underdeveloped). The varicose veins may be the primary drainage pathway.',
     'Conservative: compression. Careful surgical planning only after full duplex + venography to map the deep venous anatomy.',
     'DO NOT strip the varicose veins if the deep venous system is absent or hypoplastic — the superficial veins ARE the main drainage pathway. Removing them = acute venous ischaemia of the limb. Always check deep vein anatomy first.'],
    ['Obesity (BMI >30)',
     'Compression stocking fit difficult. EVLA technically possible but sometimes anatomically challenging. Increased surgical risk.',
     'EVLA (preferred over surgery due to lower complication rate in obesity). Custom-measured compression stockings. Weight loss programme.',
     'Standard stocking sizes often do not fit — must measure and order custom size. Inadequate stocking = no therapeutic effect.'],
    ['Anticoagulated patients\n(warfarin/DOACs)',
     'Bleeding risk from varicose vein rupture is higher. Pre-operative management of anticoagulation required. SVT management may already be covered by existing anticoagulation.',
     'If already adequately anticoagulated for another indication: existing anticoagulation may cover SVT risk. EVLA can be performed with careful peri-operative anticoagulation bridging.',
     'Do NOT stop anticoagulation abruptly without plan. Warfarin: bridge with LMWH peri-operatively. DOACs: discuss with prescribing team re timing of omission for surgery.'],
]
story.append(plain_table(sp_data, [CW*0.17, CW*0.31, CW*0.27, CW*0.25]))
divider(story)

# ── §14 MRCP EXAM TRIGGERS ────────────────────────────────────────────────────
sec_header('14. MRCP EXAM TRIGGERS — 12 Clinical Scenarios', story)

triggers = [
    ('A 50-year-old woman with varicose veins. ABPI = 0.7. She asks for compression stockings. What do you do?',
     'ABPI 0.7 = significant peripheral arterial disease. FULL COMPRESSION STOCKINGS ARE CONTRAINDICATED. Applying full compression to a leg with ABPI 0.7 would compress the already-compromised arterial blood supply, potentially causing pressure necrosis and limb-threatening ischaemia. Action: refer to vascular surgery for arterial assessment (consider angioplasty/bypass to improve ABPI first). Reduced compression (Class I, 14-17mmHg) can ONLY be prescribed under specialist supervision once arterial disease is assessed. Key teaching: ALWAYS measure ABPI before prescribing compression. This is a patient safety issue.'),
    ('SVT confirmed on duplex, extending to 2cm from the SFJ. What do you prescribe, what is the dose and duration, and why?',
     'Fondaparinux (Arixtra) 2.5mg subcutaneously once daily for 45 days. Mechanism: selective factor Xa inhibitor — blocks coagulation cascade before thrombin formation. Reason: SVT within 3cm of SFJ has a 5-10% risk of propagating through the incompetent SFJ valve into the femoral vein, causing DVT and potentially PE. The CALISTO trial (2010) showed fondaparinux 2.5mg x 45 days reduced thromboembolic complications by 85% compared to placebo. NICE recommends this or prophylactic LMWH. NSAIDs alone are INSUFFICIENT for this high-risk scenario.'),
    ('A 35-year-old man has bilateral varicose veins and a history of DVT 3 years ago. What is the most important investigation and what are you looking for?',
     'Duplex USS. You are looking for: (1) Deep vein incompetence (post-thrombotic syndrome) — is there reflux in the femoral or popliteal vein? (2) Deep vein patency — is the previous DVT fully recanalised or is there chronic occlusion? (3) Perforator incompetence. (4) Extent of superficial reflux. Also: thrombophilia screen (young patient + DVT = exclude factor V Leiden, protein C/S deficiency, antiphospholipid syndrome). Key teaching: if deep venous incompetence is found, superficial vein treatment will improve symptoms but NOT resolve the underlying deep problem — explain this to the patient before offering treatment.'),
    ('What is the CEAP grade for a patient with hard, woody skin and white patches around the ankle, but no current ulcer?',
     'CEAP C4b. C4b = Lipodermatosclerosis (LDS) or atrophie blanche (or both). This is the PRE-ULCER stage — the most critical point at which to intervene, because if treated now (EVLA for the incompetent vein), ulceration can be prevented. If left untreated, progression to C6 (active ulcer) is likely. NICE: C4b is a NICE referral criterion — urgent vascular referral + duplex USS + treatment plan.'),
    ('A venous ulcer wound swab grows MRSA. The ulcer is clean, painless, and slowly healing. Do you prescribe antibiotics?',
     'NO — not based on the swab result alone. All chronic wounds are colonised (bacteria are present but not causing active infection). The clinical assessment determines whether antibiotics are needed: ONLY prescribe antibiotics if there are clinical signs of active infection: (1) Spreading cellulitis >2cm from wound edge, (2) Increased wound pain, odour, or purulence, (3) Systemic signs (fever, raised WBC/CRP, patient feels unwell). If the ulcer is clean and healing: continue compression, wound dressings, and silver-containing dressings (Aquacel-Ag) to reduce bioburden. Unnecessary antibiotics = antibiotic resistance + C.difficile risk.'),
    ('A varicose vein bleeds at the ankle. What immediate advice do you give and what must you NOT do?',
     'Immediate management: (1) LIE DOWN immediately — this drops the venous pressure from ~90mmHg to near zero. (2) ELEVATE the leg above heart level. (3) Apply FIRM direct pressure to the bleeding point with a clean cloth for 10-15 minutes. This almost always stops the bleeding. Critical: DO NOT APPLY A TOURNIQUET. A tourniquet obstructs venous drainage while arterial inflow continues — this INCREASES venous pressure below the tourniquet and WORSENS the bleeding paradoxically. After bleeding is controlled: attend hospital for further assessment. NICE: varicose vein bleeding = indication for referral to vascular services for definitive treatment.'),
    ('A 60-year-old man has a painless, soft, bluish lump in the right groin that disappears when he lies down. A cough impulse is present. You can feel a fluid thrill when you tap his varicose veins in the thigh. What is the diagnosis and how does it differ from an inguinal hernia?',
     'Saphena varix — dilatation of the terminal GSV at the SFJ. Key differences from an inguinal hernia: (1) Saphena varix COMPLETELY disappears on lying flat; inguinal hernia may not reduce spontaneously. (2) Fluid thrill transmitted from tapping varicose veins below the groin — this cannot occur with a hernia (no fluid column from the varices). (3) No bowel sounds audible over a saphena varix. (4) Duplex USS confirms venous connection. Both have a positive cough impulse. Management: treat the underlying SFJ incompetence (EVLA or surgery). No hernia repair required.'),
    ('NICE CG168 states the first-line treatment for suitable varicose veins is?',
     'Endovenous thermal ablation — either EVLA (endovenous laser ablation) or RFA (radiofrequency ablation). Both are day-case procedures performed under local tumescent anaesthesia. 90-95% success at 5 years. Patient walks out the same day. Faster recovery and lower complication rate than surgical stripping. If unsuitable for thermal ablation (e.g. very tortuous veins, unfavourable anatomy): foam sclerotherapy (UGFS) second-line. If unsuitable for UGFS: surgical ligation and stripping third-line. Important: NICE states compression stockings alone should NOT be offered as definitive treatment to patients who are suitable for intervention.'),
    ('What is May-Thurner syndrome and in what patient should you suspect it?',
     'May-Thurner syndrome (also called iliac vein compression syndrome or Cockett syndrome): the RIGHT common iliac ARTERY crosses over and compresses the LEFT common iliac VEIN against the L5 vertebra. This creates chronic obstruction of the left iliac vein. Consequence: back-pressure transmitted down the left leg = left-sided DVT, left-sided varicose veins, left leg oedema and skin changes, pelvic congestion. Suspect in: young women with predominantly LEFT-sided varicose veins, no family history, no other secondary cause — especially if they have had a left-sided DVT. Investigation: CT venography or duplex USS of iliac veins. Treatment: iliac vein balloon angioplasty and stenting, followed by treatment of the secondary varicose veins.'),
    ('Why should you NOT perform EVLA or sclerotherapy in pregnancy?',
     'Reasons to avoid endovenous treatment in pregnancy: (1) Radiation risk: duplex USS is safe, but any X-ray guidance would risk the fetus. (2) Drug safety: tumescent lidocaine (large volumes) — fetal safety not established. Sclerosants (polidocanol, STS) — no safety data in pregnancy. (3) DVT risk: pregnancy is already a hypercoagulable state; inducing vein thrombosis with thermal ablation or sclerosant could trigger DVT/PE. (4) May improve spontaneously: many pregnancy-related varicose veins partially resolve after delivery when IVC compression is relieved. Correct management: Class II compression stockings from first trimester, regular walking, leg elevation. Review 3 months post-delivery — if VVs persist and symptomatic, then investigate and treat.'),
    ('A patient is on warfarin (INR = 2.8) for atrial fibrillation and develops a varicose vein bleed. Does the warfarin need to be reversed?',
     'For a simple varicose vein bleed: NO reversal needed. The bleed is due to the high venous pressure in the varicose vein, not primarily because of the warfarin — a non-anticoagulated patient with the same varicose vein would also bleed, just for slightly less time. Management: lie down, elevate, firm direct pressure — will almost always stop. Warfarin reversal (vitamin K, FFP) is reserved for life-threatening bleeds (intracranial haemorrhage, haemodynamic instability). Unnecessarily reversing anticoagulation puts the patient at risk of stroke (they are on warfarin for AF — if INR drops, AF can cause embolic stroke). Document the incident and arrange urgent vascular referral for definitive VV treatment.'),
    ('Klippel-Trenaunay syndrome — what is the danger of stripping the varicose veins?',
     'In Klippel-Trenaunay syndrome, the deep venous system may be absent, hypoplastic (underdeveloped), or abnormal — the superficial varicose veins may be the PRIMARY venous drainage pathway for the limb. If you strip these veins without investigating the deep venous system first, you remove the only drainage route for venous blood. Consequence: acute venous ischaemia of the limb — massive swelling, pain, skin breakdown, limb-threatening emergency. Mandatory pre-operative investigation: duplex USS + MRI venography to assess the deep venous system. If deep veins are absent or inadequate: compression management only, NO stripping. Even if deep veins are present, surgery must be approached with extreme caution.'),
]

for i, (q, a) in enumerate(triggers):
    tdata = [
        [Paragraph(f'<b>Scenario {i+1}:</b> {q}',
                   ParagraphStyle(f'QS{i}', fontName='DV-B', fontSize=8.5, leading=12, textColor=NAVY))],
        [Paragraph(f'<b>Answer:</b> {a}',
                   ParagraphStyle(f'AS{i}', fontName='DV', fontSize=8, leading=12, textColor=NAVY))]
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

# ── §15 PACES + MINIMAL RESOURCES ────────────────────────────────────────────
sec_header('15. PACES EXAMINATION &amp; MINIMAL RESOURCES PROTOCOL', story)

story.append(Paragraph('A. PACES Varicose Vein Examination — Complete Guide', sH2))
paces_data = [
    ['Step', 'What To Do', 'What You Are Looking For', 'Examiner\'s Teaching Point'],
    ['1. Introduction\n+ Consent',
     'Introduce yourself. Explain: "I need to examine the veins in your legs. I\'ll need you to stand for most of the examination." Wash hands. Position patient standing, both legs fully exposed from groin to feet.',
     'General: body habitus (obese?), gait (any chronic limp?), leg length discrepancy (Klippel-Trenaunay).',
     'NEVER examine a varicose vein patient lying down — veins collapse. If examiner asks why patient is standing, say: "Varicose veins fill under hydrostatic pressure when standing — I need the patient upright to see them."'],
    ['2. Inspect\n(front)',
     'Systematically inspect both legs from groin to foot. Note: distribution of varices (medial thigh/calf = GSV; posterior calf = SSV). Look for previous scars in groins.',
     'Tortuous dilated veins. Groin scars (previous SFJ ligation). Saphena varix (groin lump). Skin: haemosiderin, eczema, LDS. Ankle swelling.',
     'Describe distribution precisely: "There are varicose veins along the medial aspect of the left lower leg in the distribution of the great saphenous vein, with extension onto the medial thigh."'],
    ['3. Inspect\n(behind)',
     'Ask patient to turn around. Inspect posterior calf for SSV varicosities. Look at posterior knee for SPJ ligation scars.',
     'SSV varicosities (posterior calf). Popliteal fossa scarring.',
     'Do not forget the back of the leg — SSV varices are entirely on the posterior surface. Examiners will award marks for specifically asking the patient to turn around.'],
    ['4. Skin changes\n(inspect)',
     'Look specifically at the medial gaiter area (from medial malleolus to mid-calf) on both legs. CEAP grade the findings.',
     'Haemosiderin (C4a), LDS — hard woody skin (C4b), atrophie blanche (C4b), corona phlebectatica, venous ulcer (C6), healed ulcer scar (C5).',
     '"I note haemosiderin pigmentation at the medial gaiter area of the left leg, consistent with CEAP C4a disease. There is no active ulceration."'],
    ['5. Palpation',
     'Palpate: varicosities for temperature and tenderness. Medial gaiter skin (hard = LDS). Ankle (pitting oedema — press for 10 sec). Groin for saphena varix.',
     'Warm tender cord = SVT. Hard indurated skin = LDS. Pitting oedema. Saphena varix — compressible, bluish, disappears on lying.',
     'Present your findings sequentially: look then feel. Do not jump to palpation before completing inspection.'],
    ['6. Tap test\n(Schwartz)',
     'Place one hand on the thigh varicosity. Tap firmly with other hand on a lower varicosity.',
     'Fluid thrill transmitted upward = continuous fluid column without competent valves between the two points.',
     'Positive tap test confirms: (1) the vein is connected and blood-filled, (2) there are no competent valves in between.'],
    ['7. Cough impulse\nat SFJ',
     'Place fingers firmly over SFJ (3-4cm below and lateral to pubic tubercle). Ask patient to cough sharply.',
     'Impulse felt under fingers = SFJ valve incompetent.',
     'If saphena varix present: "I can feel a cough impulse at the SFJ, consistent with saphenofemoral junction incompetence and a saphena varix."'],
    ['8. Trendelenburg\ntest',
     'Patient lies supine. Elevate leg 45 degrees. Apply digital pressure at SFJ. Patient stands. Observe for filling from below. Release pressure — observe for filling from above.',
     'Below-filling (pressure maintained) = perforator incompetence. Above-filling (on release) = SFJ incompetence.',
     'Practice this test many times — the timing (hold, watch, release, watch) is easy to get wrong under exam pressure.'],
    ['9. Peripheral pulses',
     'Palpate dorsalis pedis and posterior tibial pulses bilaterally.',
     'Absent/weak pulses = PAD = ABPI needed = compression may be contraindicated.',
     '"I would like to measure the ABPI before recommending compression therapy."'],
    ['10. Closing\nstatement',
     'Summarise findings. State next investigation and management plan.',
     '"In summary, this patient has symptomatic CEAP C4a varicose veins in the GSV distribution of the left lower limb, with saphenofemoral junction incompetence on Trendelenburg testing. I would investigate with duplex ultrasound and ABPI measurement, and refer to vascular services for consideration of endovenous laser ablation per NICE CG168."',
     'A complete closing summary scores high marks. Always mention ABPI, duplex, and NICE guideline recommendation.'],
]
story.append(plain_table(paces_data, [CW*0.12, CW*0.25, CW*0.30, CW*0.33]))
story.append(Spacer(1,6))

story.append(Paragraph('B. Minimal Resources Protocol — What To Do With Clinical Exam + CBC + Basic Medicines Only', sH2))
story.append(Paragraph(
    '<b>At your facility: clinical examination + X-ray + CBC + medicines. No duplex USS initially, no CT/MRI.</b> '
    'Here is how to manage varicose vein disease to a high standard with these resources. '
    'Your clinical examination IS your duplex USS in many situations.', sBody))
story.append(Spacer(1,3))

min_data = [
    ['Condition', 'Clinical Assessment (No Duplex)', 'Treatment With Limited Resources', 'When to Refer / Escalate'],
    ['Symptomatic VVs\n(C2-C3)',
     'Full VV examination: distribution, skin changes, CEAP grade. Trendelenburg test: SFJ vs perforator incompetence. Pulse check: dorsalis pedis + posterior tibial. If Doppler available: measure ABPI.',
     'Class II compression stockings if pulses present and no signs of arterial disease. Lifestyle advice: walking daily, weight loss, elevation. Paracetamol/ibuprofen for aching (short course). Refer when possible for duplex + EVLA.',
     'Refer: any skin changes (C4+), SVT, bleeding, ulcer. Young patient with unilateral VVs: exclude secondary cause (pelvic mass — palpate abdomen/pelvis for mass).'],
    ['Skin changes C4-C6\n(Pre-ulcer or ulcer)',
     'Inspect medial gaiter carefully. CEAP grade. Check ABPI (pulse check + Doppler if available). If ABPI cannot be measured: check pulses clinically. Absent pulses = assume arterial disease = reduced compression only.',
     'Class II compression if pulses present. Four-layer bandaging for active ulcer (or simple non-adherent dressing + firm crepe if four-layer not available). Weekly dressing change. CBC to check for anaemia (slows healing). Blood glucose (check for diabetes).',
     'Urgent referral: active ulcer (C6) not healing in 4 weeks. Signs of arterial disease. MRSA or non-healing infected wound. Suspected malignancy (any ulcer not healing in 3 months = biopsy).'],
    ['Superficial Thrombophlebitis',
     'Tender warm cord along varicose vein. Exclude DVT clinically: is the whole calf swollen and tender? Is the patient systemically unwell? Homan\'s sign (pain on dorsiflexion) is non-specific. Measure calf circumference bilaterally (>2cm difference = suspect DVT).',
     'Distal SVT (not near groin): ibuprofen 400mg TDS with food x 7-14 days + compression stocking + walking. Near SFJ (tenderness extending toward groin): fondaparinux 2.5mg SC OD x 45 days. CBC: check WBC (elevated = concurrent infection).',
     'Refer if DVT clinically suspected (for duplex USS confirmation + formal anticoagulation). Refer if SVT extends to SFJ level and patient is systemically unwell.'],
    ['Varicose vein\nbleeding',
     'No investigation needed acutely. After bleeding stops: examine to CEAP grade and assess extent of VVs.',
     'Acute: lie down, elevate, firm pressure x 10 min. DO NOT tourniquet. After resolution: start Class II compression to prevent recurrence while awaiting definitive treatment.',
     'Refer to vascular for definitive treatment (NICE criteria: bleeding = indication for referral). Hospital if bleeding does not stop with 15 min of pressure or patient haemodynamically unstable.'],
    ['Infected venous ulcer',
     'Clinical signs of infection: spreading cellulitis, increased pain, odour, purulence, fever. CBC: WBC raised = systemic infection. Consider blood glucose (undiagnosed diabetes).',
     'Systemic antibiotics if clinically infected: flucloxacillin 500mg QDS x 7-14 days (S.aureus first-line). If penicillin allergic: clarithromycin 500mg BD. Dressings: non-adherent + absorbent. Elevate. Continue compression if ABPI adequate.',
     'Admit: spreading cellulitis not improving on oral antibiotics within 48h. Systemic sepsis (fever + tachycardia + confusion). Suspected necrotising fasciitis (pain out of proportion, gas in wound on X-ray = emergency).'],
]
story.append(plain_table(min_data, [CW*0.17, CW*0.28, CW*0.28, CW*0.27]))
story.append(Spacer(1,6))

alert_box(
    'PROFESSOR\'S FINAL MESSAGE: The most important test you can perform for a patient with '
    'varicose veins costs nothing and takes 2 minutes: feel both feet for pulses. '
    'One check tells you whether compression is safe. Miss it and you risk the limb. '
    'The Trendelenburg test tells you whether the SFJ is incompetent — the same information '
    'a duplex scan gives, in the hands of a doctor who has practised it. '
    'ABPI with a hand-held Doppler is a skill every doctor should master — it can be done '
    'in any clinic with a basic Doppler probe and a blood pressure cuff.',
    story, color=GREEN_L, border=GREEN_D)

divider(story)

# ── §16 MEMORY HOOK ───────────────────────────────────────────────────────────
sec_header('16. MEMORY HOOK — The Complete Story in One Paragraph', story)

hook_text = (
    'The Great Saphenous Vein (GSV — the longest vein in the body, running from the medial '
    'ankle to the groin) is held in check by a crucial valve at the Saphenofemoral Junction '
    '(SFJ) — and when that valve fails (from age, pregnancy, genetics, prolonged standing), '
    'femoral venous blood falls backward down the entire GSV under gravity, because nothing '
    'is stopping it. The calf muscle pump, which normally drives walking pressure down from '
    '90 mmHg to 30 mmHg, can no longer compensate — ambulatory venous pressure (AVP) stays '
    'dangerously high. This venous hypertension forces fibrinogen out through fragile capillary '
    'walls, forming fibrin cuffs around skin capillaries that block oxygen delivery to the '
    'overlying skin — haemosiderin (rust-brown pigment from broken red cells) stains the medial '
    'ankle, the skin hardens into lipodermatosclerosis (the inverted champagne bottle sign), '
    'atrophie blanche (white, capillary-dead skin) appears, and finally a venous ulcer opens '
    'at the medial gaiter area. CEAP grades this journey: C0 (no signs) through C6 (active '
    'ulcer). The Trendelenburg test uncovers the mechanism: fill from ABOVE when pressure '
    'released = SFJ incompetence; fill from BELOW = perforating vein failure. ABPI must be '
    'measured before any compression (ABPI <0.8 = arteries compromised = full compression '
    'contraindicated = risk of limb ischaemia). NICE CG168 says treat with endovenous laser '
    'ablation (EVLA) first, foam sclerotherapy second, surgical stripping third. For '
    'superficial vein thrombosis (SVT) near the SFJ: fondaparinux 2.5mg subcutaneously once '
    'daily for 45 days (CALISTO trial) prevents the clot propagating into the femoral vein as '
    'a DVT. For varicose vein bleeding: lie down and elevate (drops pressure to zero) + firm '
    'direct pressure — never tourniquet (tourniquets INCREASE venous pressure below them). '
    'Saphena varix mimics an inguinal hernia but disappears completely on lying flat and '
    'transmits a fluid thrill from the varices below. Klippel-Trenaunay syndrome: port wine '
    'stain + varicose veins + limb hypertrophy — NEVER strip the veins without checking that '
    'the deep veins exist. May-Thurner syndrome: young woman, left-sided DVT + varicose veins '
    '= left common iliac vein compressed by right iliac artery = stent the iliac vein first.'
)

t = Table([[Paragraph(hook_text, sHook)]], colWidths=[CW])
t.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,-1),GREEN_L),
    ('BOX',(0,0),(-1,-1),2,GREEN_D),
    ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
    ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),
]))
story.append(t)
story.append(Spacer(1,8))

divider(story)
story.append(Paragraph(
    '<i>Varicose Veins Revision Note — MRCP Parts 1, 2 &amp; PACES Preparation</i>',
    ParagraphStyle('Ft', fontName='DV-I', fontSize=8, leading=11,
                   textColor=HexColor('#888888'), alignment=1)))

# ── BUILD PDF ─────────────────────────────────────────────────────────────────
doc.build(story)
print('SUCCESS: /mnt/user-data/outputs/Varicose_Veins_MRCP_Note.pdf')
