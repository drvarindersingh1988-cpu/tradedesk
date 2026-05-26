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

doc = SimpleDocTemplate('/mnt/user-data/outputs/Choking_Heimlich_MRCP_Note.pdf',
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
sProfessor = S('Pr', font='DV-I', sz=9, lead=14, color=HexColor('#2c3e50'), sa=3,
               li=12)

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

def professor_says(text, story):
    t = Table([[Paragraph(f'<i>Professor: {text}</i>', sProfessor)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),TEAL_XL),
        ('BOX',(0,0),(-1,-1),1,TEAL_M),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,4))

def memory_hook_inline(text, story):
    sM = ParagraphStyle('MI', fontName='DV-B', fontSize=8.5, leading=13,
        textColor=HexColor('#7b3f00'), spaceAfter=0)
    t = Table([[Paragraph(f'MEMORY: {text}', sM)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),AMBER),
        ('BOX',(0,0),(-1,-1),1.5,AMBER_B),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,4))

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
def draw_box(draw, cx, y, lines, border, fill, pad_x=14, pad_y=10,
             line_gap=5, min_w=160, accent=True):
    line_data = []
    content_w = min_w - 2*pad_x - (6 if accent else 0)
    for text, font, color in lines:
        for wline in wrap_text(draw, text, font, content_w):
            ww, wh = text_size(draw, wline, font)
            content_w = max(content_w, ww)
            line_data.append((wline, font, color, ww, wh))
    box_w = content_w + 2*pad_x + (6 if accent else 0)
    box_h = (sum(h for _,_,_,_,h in line_data)
             + (len(line_data)-1)*line_gap + 2*pad_y)
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
# PIL DIAGRAM 1 — Upper Airway Anatomy
# ═══════════════════════════════════════════════════════════════════════════════
def make_airway_diagram():
    W, H = 900, 820
    img = Image.new('RGB', (W, H), '#f8fffe')
    draw = ImageDraw.Draw(img)
    draw.rectangle([0,0,W,42], fill='#0d5c63')
    t = 'UPPER AIRWAY ANATOMY — Where Choking Happens'
    tw, _ = text_size(draw, t, pfb(15))
    draw.text(((W-tw)//2, 11), t, font=pfb(15), fill='#ffffff')

    # Left column: structures top-to-bottom with descriptions
    structs = [
        (240, 60,  '#1a8a94', '#e0f4f5', 'MOUTH (Oral Cavity)',
         'The starting point. Food enters here.', 'Food is chewed and made into a soft ball (bolus).'),
        (240, 155, '#1a8a94', '#e0f4f5', 'THROAT (Pharynx)',
         'The shared passage for food AND air.', 'This is the danger zone — food and air cross here.'),
        (240, 250, '#0d5c63', '#d4edda', 'EPIGLOTTIS',
         'A flap of cartilage — like a trapdoor.', 'Closes over the airway when you swallow.'),
        (240, 345, '#c0392b', '#fde8e8', 'VOICE BOX (Larynx)',
         'Contains the vocal cords (glottis).', 'MOST COMMON site where food gets stuck.'),
        (240, 440, '#7d3c98', '#f5eef8', 'WINDPIPE (Trachea)',
         '10-12 cm long tube held open by C-shaped cartilage rings.', 'Leads air to the lungs.'),
        (240, 535, '#d4640a', '#fef3e2', 'RIGHT MAIN BRONCHUS',
         'Wider, shorter, more vertical than the left.', 'INHALED objects go here MORE OFTEN (right side).'),
        (240, 630, '#2471a3', '#e8f4fd', 'LEFT MAIN BRONCHUS',
         'Narrower, longer, angled to the left.', 'Objects less likely here — but possible.'),
    ]
    for cx, y, border, bg, title, sub1, sub2 in structs:
        draw_box(draw, cx, y, [
            (title, pfb(12), border),
            (sub1,  pf(10),  '#333333'),
            (sub2,  pf(9),   '#555555'),
        ], border, bg, accent=True, min_w=340, pad_y=8)

    # Arrows connecting structures
    for y_from, y_to in [(130,155),(225,250),(320,345),(415,440),(510,535),(605,630)]:
        arrow_down(draw, 240, y_from, y_to-5, color='#555555', w=2, hs=8)

    # Right column: obstruction sites with danger ratings
    draw.rectangle([510, 55, 890, 760], fill='#fffdf0', outline='#cccccc', width=1)
    draw.rectangle([510, 55, 890, 85], fill='#1a1a2e', outline='#1a1a2e', width=1)
    rh, _ = text_size(draw, 'OBSTRUCTION SITES & DANGER', pfb(12))
    draw.text((700-rh//2, 62), 'OBSTRUCTION SITES & DANGER', font=pfb(12), fill='#ffffff')

    danger_items = [
        (110, '#c0392b', 'SUPRAGLOTTIC', 'Above the vocal cords.',
         'MOST COMMON acute choking site. Food/objects sit at the',
         'top of the voice box. DANGER: HIGH.'),
        (210, '#c0392b', 'GLOTTIC', 'At the vocal cords (the opening between them).',
         'Most DANGEROUS position. No air can pass at all.',
         'Voice box completely blocked. DANGER: CRITICAL.'),
        (310, '#d4640a', 'SUBGLOTTIC/TRACHEAL', 'Below the voice box in the windpipe.',
         'Can cause partial or complete blockage.',
         'Objects here may move with coughing. DANGER: HIGH.'),
        (410, '#2471a3', 'RIGHT BRONCHUS', 'In the right airway branch to the right lung.',
         'Child aspirating (inhaling) a small toy or peanut.',
         'Causes right lung collapse or persistent infection. DANGER: MOD.'),
        (510, '#2471a3', 'LEFT BRONCHUS', 'In the left airway branch to the left lung.',
         'Less common. Same consequences as right bronchus.',
         'DANGER: MODERATE.'),
    ]
    for y_off, col, title, sub, line1, line2 in danger_items:
        y = 90 + y_off
        draw.rectangle([520, y, 880, y+80], fill='#ffffff', outline=col, width=2)
        draw.rectangle([520, y, 528, y+80], fill=col)
        draw.text((535, y+6), title, font=pfb(11), fill=col)
        draw.text((535, y+24), sub, font=pf(9), fill='#333333')
        dlines = wrap_text(draw, line1, pf(9), 320)
        dy = y+38
        for dl in dlines:
            draw.text((535, dy), dl, font=pf(9), fill='#555555'); dy+=13
        dlines2 = wrap_text(draw, line2, pf(9), 320)
        for dl in dlines2:
            draw.text((535, dy), dl, font=pf(9), fill='#555555'); dy+=13

    # Key fact at bottom
    draw.rectangle([20, 730, W-20, 800], fill='#fff3cd', outline='#e6a817', width=2)
    draw.text((35, 738), 'KEY FACT:', font=pfb(11), fill='#7b3f00')
    kf = ('The epiglottis (trap door) normally closes over the windpipe when you swallow. '
          'When it fails — if you eat too fast, talk while eating, laugh, or are '
          'semi-conscious — food bypasses the epiglottis and enters the airway.')
    klines = wrap_text(draw, kf, pf(10), W-80)
    ky = 755
    for kl in klines:
        draw.text((35, ky), kl, font=pf(10), fill='#7b3f00'); ky += 14

    final_h = 810
    img = img.crop((0,0,W,final_h))
    return img

# ═══════════════════════════════════════════════════════════════════════════════
# PIL DIAGRAM 2 — Choking Management Algorithm
# ═══════════════════════════════════════════════════════════════════════════════
def make_choking_algorithm():
    W = 900
    img = Image.new('RGB', (W, 980), '#f8fffe')
    draw = ImageDraw.Draw(img)
    draw.rectangle([0,0,W,42], fill='#c0392b')
    t = 'CHOKING MANAGEMENT ALGORITHM — Resuscitation Council UK'
    tw, _ = text_size(draw, t, pfb(14))
    draw.text(((W-tw)//2, 12), t, font=pfb(14), fill='#ffffff')

    y = 55
    y = draw_box(draw, 450, y, [
        ('SOMEONE IS CHOKING', pfb(14), '#ffffff'),
        ('Look for: hands clutching throat, cannot speak, cannot breathe, silent cough, turning blue', pf(10), '#ffe0e0'),
    ], '#c0392b', '#c0392b', accent=False, min_w=500) + 8
    arrow_down(draw, 450, y, y+25); y += 25

    # Branch: Can they cough/speak?
    y = draw_box(draw, 450, y, [
        ('Can they cough forcefully? Can they speak? Can they cry (infant)?', pfb(12), '#0d3320'),
        ('If YES = MILD obstruction. If NO = SEVERE obstruction.', pf(10), '#2d5a3d'),
    ], '#0d5c63', '#d4edda', accent=True, min_w=500) + 10

    branch_y = y
    arrow_right(draw, 450, 180, branch_y+15, color='#28a745')
    arrow_right(draw, 450, 720, branch_y+15, color='#c0392b')

    # LEFT = MILD
    left_y = branch_y + 5
    left_y = draw_box(draw, 180, left_y, [
        ('MILD OBSTRUCTION', pfb(11), '#ffffff'),
        ('Can cough / speak', pf(9), '#e0ffe0'),
    ], '#28a745', '#28a745', accent=False, min_w=280) + 8
    arrow_down(draw, 180, left_y, left_y+20); left_y += 20
    left_y = draw_box(draw, 180, left_y, [
        ('ENCOURAGE TO COUGH', pfb(11), '#0d3320'),
        ('Do NOT slap on back yet.', pf(9), '#333333'),
        ('Do NOT do abdominal thrusts yet.', pf(9), '#333333'),
        ('Stay with the person.', pf(9), '#333333'),
        ('If cough becomes ineffective', pf(9), '#333333'),
        ('or stops breathing -> SEVERE', pf(9), '#c0392b'),
    ], '#28a745', '#d4edda', accent=True, min_w=280) + 8
    arrow_down(draw, 180, left_y, left_y+20); left_y += 20
    draw_box(draw, 180, left_y, [
        ('If object expelled: DONE', pfb(10), '#0d3320'),
        ('Monitor closely. Seek medical review', pf(9), '#333333'),
        ('if any doubt object fully removed.', pf(9), '#333333'),
    ], '#28a745', '#e8f8ee', accent=False, min_w=280)

    # RIGHT = SEVERE
    right_y = branch_y + 5
    right_y = draw_box(draw, 720, right_y, [
        ('SEVERE OBSTRUCTION', pfb(11), '#ffffff'),
        ('Cannot cough / speak / breathe', pf(9), '#ffe0e0'),
    ], '#c0392b', '#c0392b', accent=False, min_w=280) + 8
    arrow_down(draw, 720, right_y, right_y+20); right_y += 20
    right_y = draw_box(draw, 720, right_y, [
        ('CALL FOR HELP (999 / crash team)', pfb(10), '#7b0000'),
        ('Shout for someone to call while you act.', pf(9), '#333333'),
    ], '#c0392b', '#fde8e8', accent=True, min_w=280) + 8
    arrow_down(draw, 720, right_y, right_y+20); right_y += 20
    right_y = draw_box(draw, 720, right_y, [
        ('5 BACK BLOWS', pfb(11), '#ffffff'),
        ('Lean patient forward. Support chest.', pf(9), '#ffe0e0'),
        ('Heel of hand between shoulder blades.', pf(9), '#ffe0e0'),
        ('5 firm blows. Check after each one.', pf(9), '#ffe0e0'),
    ], '#c0392b', '#c0392b', accent=False, min_w=280) + 8
    arrow_down(draw, 720, right_y, right_y+15); right_y += 15
    draw_box(draw, 720, right_y, [
        ('Object cleared?', pfb(10), '#0d3320'),
    ], '#0d5c63', '#d4edda', accent=False, min_w=160)
    right_y2 = right_y + 40
    arrow_right(draw, 720, 870, right_y+20, color='#28a745')
    draw_box(draw, 870, right_y+5, [('DONE', pfb(10), '#28a745')],
             '#28a745', '#d4edda', accent=False, min_w=60)
    arrow_down(draw, 720, right_y2, right_y2+15); right_y2 += 15
    right_y2 = draw_box(draw, 720, right_y2, [
        ('5 ABDOMINAL THRUSTS', pfb(11), '#ffffff'),
        ('(Heimlich Manoeuvre)', pfb(10), '#ffe8d0'),
        ('Stand BEHIND patient.', pf(9), '#ffe0e0'),
        ('Fist: thumb side on abdomen,', pf(9), '#ffe0e0'),
        ('halfway between navel + breastbone.', pf(9), '#ffe0e0'),
        ('Other hand over fist.', pf(9), '#ffe0e0'),
        ('Pull SHARPLY INWARD and UPWARD.', pf(9), '#ffe0e0'),
        ('Repeat up to 5 times.', pf(9), '#ffe0e0'),
    ], '#d4640a', '#d4640a', accent=False, min_w=280) + 8
    arrow_down(draw, 720, right_y2, right_y2+15); right_y2 += 15
    draw_box(draw, 720, right_y2, [
        ('ALTERNATE: 5 back blows + 5 abdominal thrusts', pfb(10), '#7b0000'),
        ('Keep repeating until cleared OR patient collapses.', pf(9), '#7b0000'),
    ], '#c0392b', '#fde8e8', accent=True, min_w=280)

    # UNCONSCIOUS box at bottom
    unc_y = max(left_y, right_y2) + 80
    arrow_down(draw, 450, unc_y-40, unc_y-10)
    unc_y = draw_box(draw, 450, unc_y, [
        ('IF PATIENT BECOMES UNCONSCIOUS', pfb(12), '#ffffff'),
        ('Lower carefully to the floor. Call 999 if not already done.', pf(10), '#ffe0e0'),
        ('START CPR (30 chest compressions : 2 breaths).', pfb(10), '#ffe0e0'),
        ('BEFORE EACH BREATH: open the mouth and LOOK.', pf(10), '#ffe0e0'),
        ('If you CAN SEE the object: remove it. If NOT: do NOT do blind finger sweep.', pf(10), '#ffe0e0'),
        ('Compressions may help dislodge the object.', pf(9), '#ffe0e0'),
    ], '#c0392b', '#c0392b', accent=False, min_w=600) + 8

    final_h = min(unc_y + 10, 970)
    img = img.crop((0,0,W,final_h))
    return img

# ═══════════════════════════════════════════════════════════════════════════════
# PIL DIAGRAM 3 — Special Populations
# ═══════════════════════════════════════════════════════════════════════════════
def make_special_populations():
    W = 900
    img = Image.new('RGB', (W, 560), '#f8fffe')
    draw = ImageDraw.Draw(img)
    draw.rectangle([0,0,W,42], fill='#7d3c98')
    t = 'CHOKING MANAGEMENT — SPECIAL POPULATIONS'
    tw, _ = text_size(draw, t, pfb(15))
    draw.text(((W-tw)//2, 12), t, font=pfb(15), fill='#ffffff')

    pops = [
        (150, '#c0392b', '#fde8e8',
         'INFANT (Under 1 year)',
         ['NEVER use abdominal thrusts (Heimlich).', 'Liver is unprotected = easily damaged.'],
         ['5 BACK BLOWS:', 'Hold face-DOWN on your forearm.', 'Head LOWER than chest (gravity helps).', 'Heel of hand: 5 firm blows between shoulder blades.'],
         ['5 CHEST THRUSTS:', 'Turn face-UP on your forearm.', 'Two fingers on breastbone.', '1 finger-width BELOW nipple line.', 'Push DOWN and slightly toward head.']),
        (450, '#d4640a', '#fef3e2',
         'PREGNANT WOMAN',
         ['NEVER use abdominal thrusts.', 'Compresses the pregnant uterus = harms baby.'],
         ['USE CHEST THRUSTS instead:', 'Stand BEHIND the patient.', 'Arms under her armpits, around chest.', 'Place hands on LOWER STERNUM (breastbone).', 'Pull SHARPLY BACKWARD (not upward).'],
         ['Same sequence: 5 back blows +', '5 chest thrusts alternating.', 'If unconscious: CPR with', 'left lateral tilt (15-30 degrees)', 'to move uterus off vena cava.']),
        (750, '#2471a3', '#e8f4fd',
         'OBESE PATIENT',
         ['Arms may not reach around abdomen.', 'Abdominal thrusts may be ineffective.'],
         ['USE CHEST THRUSTS instead:', 'Same position as for pregnancy.', 'Hands on lower sternum.', 'Pull SHARPLY BACKWARD.'],
         ['If unconscious:', 'Standard CPR position.', 'May need additional manpower', 'to maintain airway and', 'perform chest compressions.']),
    ]
    for cx, brd, bg, title, warning, col1, col2 in pops:
        y = 55
        y = draw_box(draw, cx, y, [(title, pfb(12), '#ffffff')],
                     brd, brd, accent=False, min_w=230) + 5
        draw_box(draw, cx, y, [(w, pf(9), '#7b0000') for w in warning],
                 '#c0392b', '#fde8e8', accent=True, min_w=230, pad_y=5)
        y2 = y + 75
        draw_box(draw, cx, y2, [(c, pf(9), '#0d3320') for c in col1],
                 brd, bg, accent=True, min_w=230, pad_y=6)
        y3 = y2 + 140
        draw_box(draw, cx, y3, [(c, pf(9), '#0d3320') for c in col2],
                 brd, bg, accent=True, min_w=230, pad_y=6)

    # Memory row at bottom
    draw.rectangle([20, 490, W-20, 545], fill='#fff3cd', outline='#e6a817', width=2)
    draw.text((35, 498), 'REMEMBER:', font=pfb(11), fill='#7b3f00')
    mem = ('INFANT = Back blows + CHEST thrusts (NO Heimlich). '
           'PREGNANT = Back blows + CHEST thrusts (NO Heimlich). '
           'OBESE = Back blows + CHEST thrusts (NO Heimlich). '
           'Memory: "ABC" = Always use Back blows + Chest thrusts when Heimlich is not possible.')
    mlines = wrap_text(draw, mem, pf(10), W-80)
    my = 516
    for ml in mlines:
        draw.text((35, my), ml, font=pf(10), fill='#7b3f00'); my += 14

    final_h = 550
    img = img.crop((0,0,W,final_h))
    return img

# ─────────────────────────────────────────────
# BUILD STORY
# ─────────────────────────────────────────────
story = []

# ── TITLE ─────────────────────────────────────────────────────────────────────
story.append(Spacer(1,8))
story.append(Paragraph('CHOKING &amp; THE HEIMLICH MANOEUVRE', sTitle))
story.append(Paragraph(
    'Foreign Body Airway Obstruction — Recognition, Emergency Management, '
    'Anatomy, Physiology, Special Populations, Dysphagia &amp; MRCP Preparation', sSub))
divider(story)

# ── §1 OVERVIEW ───────────────────────────────────────────────────────────────
sec_header('1. OVERVIEW — What Is Choking and Why Does It Kill?', story)
professor_says(
    'Let me paint you a picture. A person is sitting at the dinner table, eating and laughing '
    'at the same time. A piece of food goes "down the wrong way." In most cases, a cough or two '
    'clears it. But sometimes — the food lands directly on the voice box and blocks it completely. '
    'No air can get in. No air can get out. The brain starts dying within 4 minutes without oxygen. '
    'Within 6 minutes: permanent brain damage or death. This is choking. And the difference between '
    'life and death is knowing exactly what to do in those first 60 seconds.', story)

info_box(
    '<b>CHOKING</b> (medical term: <b>Foreign Body Airway Obstruction — FBAO</b>) means a piece of food, '
    'an object, or fluid has entered the breathing passage (airway) and is blocking it — either '
    'partially or completely — preventing air from reaching the lungs. '
    'Foreign = it does not belong there. Body = a physical object. Airway = the passage through '
    'which we breathe. Obstruction = a blockage.', story)

kf_data = [
    ['Key Fact', 'Number', 'Why It Matters'],
    ['Deaths from choking per year (UK)', '~200-300', 'Entirely preventable with correct immediate action'],
    ['Time before brain damage without oxygen', '4-6 minutes', 'You have minutes — not hours. Act immediately.'],
    ['Most common victims — adults', 'Elderly (especially with dentures, poor dentition, dementia)', 'Poor chewing, reduced swallow reflex, dry mouth from medications'],
    ['Most common victims — children', 'Age 6 months to 3 years', 'Put everything in their mouths; poor coordination of swallowing'],
    ['Most common food causing choking in adults', 'Meat, bread, hard boiled sweets, grapes', 'Large pieces swallowed without sufficient chewing'],
    ['Most common objects in children', 'Coins, small toy parts, grapes, hot dogs, nuts, grapes', 'Round, slippery objects are most dangerous — conform to airway shape'],
    ['Resuscitation Council UK guideline', 'Current 2021 guidelines', 'Standard used in MRCP, OSCEs, and real clinical practice'],
]
story.append(plain_table(kf_data, [CW*0.30, CW*0.32, CW*0.38]))
divider(story)

# ── §2 ANATOMY ────────────────────────────────────────────────────────────────
sec_header('2. ANATOMY — The Journey from Mouth to Lungs', story)
professor_says(
    'Close your eyes for a moment and imagine you are a tiny person, small enough to travel '
    'through the human body. You enter through the mouth. You travel down the throat. '
    'You reach a fork in the road — one path leads to the stomach (the food pipe, called the '
    'oesophagus), the other leads to the lungs (the airway). A remarkable flap of tissue '
    'called the EPIGLOTTIS acts as a trapdoor — every single time you swallow, it snaps shut '
    'over the airway entrance so food goes to the stomach, not the lungs. '
    'When this system fails — even for a fraction of a second — food enters the airway instead, '
    'and choking begins.', story)

story.append(Spacer(1,4))
anat_data = [
    ['Structure', 'Plain English Name', 'Location', 'Role in Normal Breathing/Swallowing', 'What Happens When Blocked'],
    ['Oral cavity', 'The mouth',
     'Everything inside your lips and teeth, including your tongue and the roof of your mouth',
     'Food enters here. You chew food into a soft mushy ball (called a "bolus" — think of it as a food parcel). Saliva (spit) from the salivary glands mixes in to lubricate the food and start digestion.',
     'Rarely blocked here — the mouth is wide and accessible. But large food pieces or objects placed in the mouth can get pushed back and cause obstruction.'],
    ['Pharynx', 'The throat',
     'The tube behind your mouth and nose, before the voice box. It is shared by both food and air.',
     'The throat is the CROSSROADS — both the food pipe and the airway start here. This is why you can choke: food and air compete for the same passage for a brief moment.',
     'Food sitting at the back of the throat before the epiglottis closes can be inhaled (breathed in) into the airway — this is the beginning of choking.'],
    ['Epiglottis', 'The trapdoor',
     'A leaf-shaped flap of flexible cartilage (firm but benchy tissue, like your ear) sitting at the top of the voice box, just behind the tongue',
     'Every time you swallow, the epiglottis flips DOWN over the entrance to the voice box like a lid closing. Food goes OVER it into the food pipe. The moment swallowing is done, it opens again and you breathe.',
     'If the epiglottis fails to close in time (eating too fast, distracted, semi-conscious), food enters the voice box directly. This is the key failure point in choking.'],
    ['Larynx', 'The voice box',
     'At the front of the neck — the bump you can feel (Adam\'s apple). Contains the vocal cords.',
     'Air passes through the vocal cords when you breathe in and out. When you speak, the cords vibrate and create your voice. The larynx is also the most important protective gate of the lower airway.',
     'THE MOST COMMON SITE WHERE CHOKING OCCURS. When food lands on the vocal cords (glottis = the opening between the cords), they may clamp shut reflexively (laryngospasm — the voice box goes into a protective spasm, slamming shut), making obstruction even worse.'],
    ['Trachea', 'The windpipe',
     'A 10-12cm long tube running from the voice box down to the chest, sitting in front of the food pipe (oesophagus)',
     'The main airway. Held open by 15-20 C-shaped rings of cartilage (firm tissue) so it never collapses. Air travels in and out through this tube with every breath.',
     'Objects or food that pass through the voice box can lodge in the trachea. Partial blockage = noisy breathing (stridor — a high-pitched crowing sound on breathing in). Complete blockage = no breathing.'],
    ['Carina', 'The fork in the road',
     'The bottom of the trachea, where it splits into the right and left main bronchi (airways to the right and left lungs)',
     'Simply a branching point — like a Y-junction in a road.',
     'Foreign bodies that travel this far may go left or right. The right bronchus is the MORE LIKELY destination — it is straighter, wider, and more vertical (like continuing in a straight line), while the left bronchus angles away.'],
    ['Right main bronchus', 'The right airway branch — to the right lung',
     'Wider (about 15mm), shorter (2-3cm long), MORE VERTICAL than the left — it is like a more direct continuation of the trachea',
     'Carries air to the right lung (which has 3 lobes — sections — called upper, middle, and lower).',
     'FOREIGN BODIES ARE MORE LIKELY TO LODGE HERE — because of the wider, more vertical angle. A child who inhales (breathes in) a peanut or toy piece: it almost always goes to the right side. Result: right lung collapse (atelectasis) or right-sided pneumonia.'],
    ['Left main bronchus', 'The left airway branch — to the left lung',
     'Narrower (about 11mm), longer (4-5cm), MORE HORIZONTAL — it angles across to the left to go around the heart',
     'Carries air to the left lung (which has 2 lobes — upper and lower — because the heart takes up space on the left side).',
     'Less common for foreign bodies to go here, but possible. Same consequences: lung collapse, infection.'],
]
story.append(plain_table(anat_data, [CW*0.11, CW*0.12, CW*0.18, CW*0.28, CW*0.31]))
story.append(Spacer(1,5))

diag1 = make_airway_diagram()
story.append(img2rl(diag1, CW))
story.append(Paragraph(
    'Diagram 1: The upper airway from mouth to bronchi, showing where foreign body obstruction occurs and the relative danger at each site.',
    ParagraphStyle('Cap1', fontName='DV-I', fontSize=8, leading=11,
                   textColor=HexColor('#555555'), alignment=1)))
story.append(Spacer(1,4))
image_search_box('upper airway anatomy larynx epiglottis trachea labelled diagram', 'TeachMeAnatomy.info', story)
image_search_box('epiglottis during swallowing animation', 'YouTube', story)
divider(story)

# ── §3 PHYSIOLOGY ─────────────────────────────────────────────────────────────
sec_header('3. PHYSIOLOGY — How the Body Normally Protects the Airway', story)
professor_says(
    'The human body is remarkably clever at protecting the airway from foreign objects. '
    'It has THREE powerful built-in defences that work automatically without you thinking '
    'about them. Understanding these defences explains why choking happens, and more importantly, '
    'why the Heimlich manoeuvre works.', story)

phys_data = [
    ['Defence Mechanism', 'Plain English Explanation', 'The Science', 'When It Fails', 'Clinical Significance'],
    ['The Swallowing Reflex\n(the most important defence)',
     'Every time you swallow, your brain automatically coordinates over 30 different muscles in exactly the right sequence and timing — without you consciously doing anything. The tongue pushes food back, the throat closes off the nose, the epiglottis flips down over the airway, the food pipe opens, and food goes in. The whole thing takes less than 1 second.',
     'Controlled by cranial nerves (nerves coming directly from the brain) — especially CN IX (glossopharyngeal) which senses the food at the back of the throat, and CN X (vagus) and CN XII (hypoglossal) which co-ordinate the muscle movements. The brain stem (the most primitive part of the brain, at the top of the spinal cord) is in charge.',
     'Neurological diseases (stroke, Parkinson\'s disease, Motor Neurone Disease), dementia, anaesthesia, unconsciousness, alcohol intoxication, old age (the reflex slows down), distractions while eating.',
     'After a stroke (sudden interruption of blood supply to a part of the brain), up to 50% of patients have swallowing problems (called dysphagia — difficulty swallowing). This is why stroke patients are "nil by mouth" initially and assessed by a speech therapist before eating.'],
    ['The Cough Reflex\n(the airway\'s alarm system)',
     'Sensors (called cough receptors) line the inside of the airways — from the voice box all the way down to the bronchi. The moment anything touches these sensors — dust, food, smoke, a crumb — an explosive cough is automatically triggered. A cough can expel air at speeds up to 800 litres per minute — about the speed of a hurricane — to blast the foreign object out.',
     'Receptors are stimulated, signals travel via the vagus nerve (cranial nerve X) to the cough centre in the brain stem. Deep inhalation (breathing in deeply first), then the glottis (the opening between the vocal cords) snaps SHUT, building pressure in the chest, then it suddenly opens and a huge burst of air is expelled.',
     'Severe obstruction where the cough is "silent" — this means the glottis is so tightly blocked that air cannot even build up behind it to create a forceful cough. Silent cough = complete obstruction = EMERGENCY.',
     'A STRONG cough (you can hear it) = air is still moving = some airway is open = mild obstruction. A SILENT or WEAK cough = no air is moving = complete or near-complete obstruction = act NOW (back blows + Heimlich).'],
    ['Laryngospasm\n(the reflexive clamp)',
     'When something touches the vocal cords unexpectedly — whether food, water, even cold air — the vocal cords can slam shut reflexively (like a clam shutting). This protective spasm is designed to stop anything from entering the lungs. However, if food is already stuck on the cords, this spasm can WORSEN the obstruction.',
     'Highly innervated (rich nerve supply) from the superior laryngeal nerve (a branch of the vagus nerve). The reflex is extremely sensitive — even a drop of water hitting the cords in a lightly anaesthetised patient can trigger it.',
     'Drowning, anaesthetic complications, gastro-oesophageal reflux (acid from the stomach reaching the throat). In children, can be triggered by a virus (croup) causing severe stridor.',
     'Important in anaesthesia: laryngospasm is a serious complication of general anaesthesia. Treatment: jaw thrust, positive pressure oxygen, small dose of suxamethonium (succinylcholine — a muscle relaxant) to break the spasm.'],
    ['The Heimlich Mechanism\n(the physics of the manoeuvre)',
     'The Heimlich manoeuvre works by mimicking a super-powered cough that you perform for the patient. Here is the physics: you push up sharply on the bottom of the diaphragm (the large dome-shaped muscle that separates the chest from the stomach, which moves up and down when you breathe). This sudden upward push RAMS the diaphragm into the chest. The chest cavity suddenly becomes smaller. The air inside the lungs has nowhere to go. It rushes upward and outward through the airway — like squeezing a balloon from the bottom — creating a burst of high-speed air that pops the foreign object out.',
     'The sudden increase in intrathoracic pressure (the pressure inside the chest cavity) creates an expiratory airflow (outward rush of air). Peak pressures of 100-200 cmH2O can be generated — similar to or exceeding a normal cough. This is enough to dislodge most food particles or objects from the airway.',
     'If the lungs are poorly inflated (patient is barely breathing already), there is less air to propel. This is why getting back blows in FIRST is important — back blows may dislodge the object before the lungs empty further.',
     'In unconscious patients: CPR chest compressions do something similar — they create repeated brief spikes of intrathoracic pressure with each compression, which can gradually loosen or dislodge a foreign body. This is why we check the mouth BEFORE each breath during CPR in a choking victim.'],
]
story.append(plain_table(phys_data, [CW*0.14, CW*0.26, CW*0.22, CW*0.18, CW*0.20]))

memory_hook_inline(
    '"Strong cough = some air moving = mild obstruction = encourage to cough. '
    'Silent cough = no air = complete obstruction = act immediately."', story)
divider(story)

# ── §4 PATHOLOGY ──────────────────────────────────────────────────────────────
sec_header('4. PATHOLOGY — What Happens Inside the Body During Choking', story)
professor_says(
    'Let me walk you through what happens, second by second, when someone chokes. '
    'Understanding this sequence tells you WHY every step of the management matters and '
    'why timing is so critical.', story)

path_data = [
    ['Time', 'What Is Happening Inside the Body', 'What You See on the Outside', 'What To Do'],
    ['0 seconds\n(obstruction occurs)',
     'A foreign object enters the larynx (voice box) or trachea (windpipe). The vocal cords may clamp shut reflexively (laryngospasm). Air can no longer flow through the blocked section. The lungs still contain air — they have not yet emptied.',
     'Sudden distress. Person grabs their throat (this is called the "universal choking sign" — the body\'s automatic response to airway obstruction). May try to cough. May look panicked.',
     'ASK: "Are you choking?" If they can speak/cough = mild obstruction. Encourage to cough.'],
    ['0-30 seconds\n(initial response)',
     'If partial obstruction: turbulent air rushes past the object, creating a noisy crowing sound (called stridor — pronounced "stry-dor" — means a high-pitched harsh sound on breathing in, caused by narrowed airway). If complete obstruction: coughing becomes ineffective or silent.',
     'Partial: noisy, strained breathing, stridor, weak cough, can still move some air. Complete: silent, no cough, cannot speak, starting to look frightened.',
     'If partial (noisy): continue encouraging to cough. If complete (silent): call for help NOW, begin back blows immediately.'],
    ['30-60 seconds\n(hypoxia begins)',
     'Oxygen level (called oxygen saturation — SpO2) starts to fall. The blood is still being pumped by the heart, but it is not picking up fresh oxygen from the lungs. The brain, heart, and all organs begin to experience oxygen shortage (called hypoxia — hypo = low, oxia = oxygen). The body responds by increasing the heart rate and breathing effort.',
     'Skin and lips start to turn blue or purple (this is called cyanosis — sigh-an-OH-sis — from the Greek word for blue, caused by deoxygenated haemoglobin, the red blood cell oxygen-carrier, turning dark blue when oxygen is stripped from it). Patient is visibly distressed, tachycardia (fast heart rate).',
     'If back blows have not worked: alternate with 5 abdominal thrusts (Heimlich manoeuvre). Speed is critical now.'],
    ['1-4 minutes\n(progressive hypoxia)',
     'SpO2 continues to fall. Brain cells (called neurons — they are the most sensitive cells in the body to oxygen deprivation) begin to die. Consciousness is impaired. Patient becomes confused, drowsy, then unresponsive. Heart rhythm may become irregular (arrhythmia — abnormal heartbeat) as the heart muscle becomes hypoxic.',
     'Patient becomes drowsy, slumps, may fall. Unconsciousness. Blue/grey complexion. No effective respiratory effort.',
     'Patient has become unconscious: lower to floor carefully, call 999, start CPR immediately. Look in mouth before each breath.'],
    ['4-6 minutes\n(irreversible damage)',
     'Permanent brain cell death. Even if the obstruction is cleared at this point, the patient may have permanent neurological damage (brain damage). The heart may stop (cardiac arrest) due to hypoxia.',
     'Unresponsive. No breathing. No pulse (cardiac arrest).',
     'CPR must be continued. Advanced airway management (laryngoscopy, intubation, surgical airway) if available. Defibrillation if shockable rhythm. Early defibrillation + CPR = only chance.'],
]
story.append(plain_table(path_data, [CW*0.13, CW*0.30, CW*0.27, CW*0.30]))
memory_hook_inline(
    '4 minutes = brain damage starts. 6 minutes = likely irreversible. '
    'You have ONE minute to act effectively. Every second of hesitation counts.', story)
divider(story)

# ── §5 RISK FACTORS ───────────────────────────────────────────────────────────
sec_header('5. RISK FACTORS &amp; CAUSES — Who Chokes and Why', story)
rf_data = [
    ['Risk Factor', 'Plain English Explanation', 'Medical Mechanism', 'Prevention Strategy'],
    ['Old age',
     'As we get older, our swallowing becomes slower and less precise. Muscles weaken. The automatic swallowing reflex that we take for granted becomes less reliable.',
     'Sarcopenia (loss of muscle mass and strength with age) affects the swallowing muscles. Reduced saliva production (xerostomia — dry mouth). Neurological slowing.',
     'Soft diet. Small mouthfuls. No talking while eating. Sit upright for all meals.'],
    ['Dentures (false teeth)',
     'False teeth sit on top of the gums and reduce the sensation in the roof of the mouth. The brain receives less feedback about where food is and how large each piece is.',
     'Reduced mechanoreception (the ability to feel pressure and texture) in the palate (roof of the mouth). Poor food bolus formation.',
     'Regular dental review. Ensure dentures fit well. Cut food into smaller pieces.'],
    ['Eating too fast',
     'When you eat fast, you do not chew food enough. Large pieces of food are swallowed whole. The throat and epiglottis have less time to co-ordinate properly.',
     'Reduced oral processing time. Large food bolus size exceeds the capacity of the pharynx to safely pass.',
     'Mindful eating. Proper mealtimes. Do not eat while distracted or walking.'],
    ['Eating and talking/laughing',
     'When you laugh or speak, your glottis (the opening between the vocal cords) is OPEN — this is the opposite of what you need when swallowing. Food lands on an open airway.',
     'Swallowing and breathing are mutually exclusive — the body cannot do both simultaneously. When vocalisation (speaking/laughing) occurs at the moment of swallowing, the airway protection fails.',
     'Simple awareness. "Finish your mouthful before you speak."'],
    ['Neurological diseases\n(stroke, Parkinson\'s, MND, dementia)',
     'These diseases damage the part of the brain or nerves that control swallowing. The person may not be able to coordinate swallowing safely, or may not feel food in the throat properly.',
     'Cranial nerve damage (IX, X, XII). Bulbar palsy (damage to the lower brain stem controlling swallowing and speech). Reduced cough reflex. Aspiration (food going into the lungs) may be silent — no cough at all ("silent aspiration").',
     'SALT (Speech and Language Therapy) assessment. Modified texture diet. Thickened fluids. Sometimes NG tube or PEG tube feeding.'],
    ['Alcohol / sedative drugs',
     'Alcohol and sedatives (sleeping tablets, anxiety medicines, strong painkillers like morphine) dull the reflexes. The cough reflex and swallowing coordination are impaired.',
     'CNS (central nervous system = brain and spinal cord) depression reduces reflex speed and consciousness. Increased aspiration risk especially when vomiting (inhaling vomit = aspiration pneumonia).',
     'Never eat a large meal immediately after drinking. Do not take sedatives with food. Ensure unconscious/heavily sedated patients are positioned correctly.'],
    ['Young children\n(6 months - 3 years)',
     'Young children have not yet developed the co-ordination and judgement to know what is safe to put in their mouths. They explore the world by putting objects in their mouth.',
     'Immature swallowing coordination. Smaller, narrower airway (even a small object can cause complete blockage). Deciduous teeth (baby teeth) may not chew food effectively.',
     'Age-appropriate food: no whole grapes, no whole nuts, no large chunks of meat for under-3s. Supervise mealtimes. Keep small objects out of reach. Cut food into small pieces.'],
    ['Hospital patients / post-operative',
     'After an operation (surgery), anaesthetic drugs and pain relief medicines can make patients drowsy and reduce their swallowing reflex. Tube feeding and intubation (breathing tube) can also impair swallowing temporarily.',
     'Post-extubation laryngeal oedema (swelling around the voice box after a breathing tube is removed), residual anaesthetic and opiate (pain-killing drug) effect, reduced consciousness.',
     '"Nil by mouth" until formally assessed. Swallow screening before any oral intake post-surgery or post-stroke. Dietitian and SALT team involvement.'],
]
story.append(plain_table(rf_data, [CW*0.17, CW*0.27, CW*0.27, CW*0.29]))
divider(story)

# ── §6 CLINICAL FEATURES ──────────────────────────────────────────────────────
sec_header('6. CLINICAL FEATURES — Recognising Choking Immediately', story)
professor_says(
    'The most important skill in choking management is immediate recognition. '
    'You do not have time to think "hmm, could this be something else?" '
    'You must recognise it in three seconds. Learn the signs so deeply that they '
    'are automatic. The body gives you very clear signals.', story)

story.append(Paragraph('The Universal Choking Sign', sH2))
story.append(Paragraph(
    'Across all human cultures worldwide, when a person is choking, they instinctively '
    'place one or both hands at their throat — fingers spread, grasping the neck. '
    'This is not something anyone teaches — it is an automatic, universal human response. '
    'When you see this sign, act immediately. Do not ask "are you okay?" — ask '
    '"<b>Are you choking?</b>" If they cannot answer = severe obstruction = begin back blows.', sBody))
story.append(Spacer(1,4))

recog_data = [
    ['Feature', 'MILD Obstruction\n(partial blockage — some air is getting through)', 'SEVERE Obstruction\n(complete or near-complete blockage — NO air)', 'What You Must Do'],
    ['Cough',
     'STRONG and forceful cough. You can hear the air being expelled. The patient is making noise — this is actually a GOOD sign because it means air is moving.',
     'Silent cough OR very weak, ineffective cough. No noise. Or just a tiny wheeze. The silence of a choke is more frightening than any sound.',
     'Mild = encourage to cough. Severe = act NOW.'],
    ['Voice / Speech',
     'Can still speak — may be hoarse or strained. May be able to say "I\'m choking" or "help."',
     'Cannot speak at all. No words come out. Mouth opens but nothing is heard. Or only a whisper.',
     'If they can speak = mild. Cannot speak = severe.'],
    ['Breathing',
     'Can breathe — but breathing is noisy. Stridor (that harsh crowing sound on breathing in) may be present — this is the sound of air forcing past a partial obstruction.',
     'Cannot breathe at all. Chest not rising and falling. Completely silent.',
     'Any breathing at all = some air = mild. No breathing = severe.'],
    ['Colour',
     'Normal skin colour or slightly flushed (red from the effort of coughing).',
     'Going blue around the lips and fingertips (cyanosis). May go very pale initially, then blue.',
     'Blue lips = no oxygen = critical emergency.'],
    ['Consciousness',
     'Fully alert and frightened. Can make eye contact. Can follow instructions.',
     'Initially alert and panicked, but rapidly becoming drowsy and confused as oxygen falls. Then loses consciousness.',
     'Losing consciousness = the obstruction has been there too long = CPR is next.'],
    ['Hand position',
     'May grip throat with one hand (universal sign).',
     'Clutching throat with both hands. Looks terrified. Starts to slump.',
     'Both hands at throat + cannot speak = severe. Act immediately.'],
]
story.append(plain_table(recog_data, [CW*0.16, CW*0.28, CW*0.28, CW*0.28]))
story.append(Spacer(1,4))
alert_box(
    'THE MOST IMPORTANT RULE: If the person CAN COUGH, CAN SPEAK, or CAN CRY (in babies) '
    '— it is MILD obstruction. DO NOT do back blows or abdominal thrusts yet. '
    'Encourage coughing. Watch closely. '
    'If they CANNOT cough, CANNOT speak, CANNOT breathe — it is SEVERE. Act NOW.', story)
divider(story)

# ── §7 MANAGEMENT — ADULTS ────────────────────────────────────────────────────
sec_header('7. MANAGEMENT — Adult Choking: The Step-by-Step Protocol', story)
professor_says(
    'Now I am going to teach you the exact sequence. Every step has a reason. '
    'Learn the steps AND the reasons — then you will never forget them, even under pressure.', story)

story.append(Paragraph('A. The Five Back Blows — Why First, How to Do Them', sH2))
story.append(Paragraph(
    '<b>Why back blows come FIRST:</b> Back blows create a sudden vibration and concussive force '
    'through the chest. This can dislodge the object by a different mechanism from the Heimlich — '
    'shaking it loose rather than blowing it out. They are also safer than abdominal thrusts '
    '(which carry a small risk of internal injury). Always try back blows first.', sBody))
story.append(Spacer(1,3))

backblow_data = [
    ['Step', 'Exact Action', 'Why You Do It This Way'],
    ['1. Position yourself',
     'Stand to the SIDE and slightly BEHIND the choking person.',
     'You need access to their back. Being slightly behind means you can support them if they fall forward (which many people do when bending).'],
    ['2. Support the chest',
     'Place your NON-DOMINANT hand flat against their chest (the front) to support them.',
     'The forward lean means their body weight needs support. You are also bracing them so the blow translates into force on the object, not just toppling the person over.'],
    ['3. Lean them forward',
     'Encourage or assist the person to bend forward at the waist, so their head is lower than their chest.',
     'GRAVITY helps. If the blow dislodges the object, you want it to fall OUT of the mouth, not FURTHER into the airway. Leaning forward = gravity works in your favour.'],
    ['4. The blow',
     'Use the HEEL of your dominant hand (the fleshy part at the base of your palm, below the little finger — not your palm flat, not your fingertips). Strike FIRMLY between the shoulder blades (the two flat bones on the upper back). FIVE times. Check after EACH blow.',
     'The heel of the hand delivers a firm, focused, concentrated force. Between the shoulder blades is the safest spot — close to the trachea (windpipe) inside. "Firm" means genuinely forceful — gentle pats do nothing. Check after each because the object may clear after blow 1, 2, or 3 — do not continue if it is already out.'],
    ['5. After each blow',
     'After each back blow, look quickly into the mouth. Has an object appeared? Is the person coughing? Can they speak now?',
     'If the object has been dislodged into the mouth, you may be able to see it and remove it (only if you can clearly see it — remove it with your fingers). If they are now coughing = good = encourage them to keep coughing.'],
]
story.append(plain_table(backblow_data, [CW*0.15, CW*0.42, CW*0.43]))
story.append(Spacer(1,5))

story.append(Paragraph('B. The Heimlich Manoeuvre (Abdominal Thrusts) — The Classic Technique', sH2))
professor_says(
    'Named after Dr Henry Heimlich, an American thoracic surgeon (chest surgeon) who described '
    'this technique in 1974. At the time, choking deaths were so common in restaurants that they '
    'were called "cafe coronary" because people assumed a person who suddenly collapsed while eating '
    'had a heart attack. Dr Heimlich realised it was often choking, and developed this manoeuvre. '
    'It is one of the most important emergency techniques ever described — and it is simple enough '
    'to teach to everyone.', story)

heimlich_data = [
    ['Step', 'Exact Action', 'The Physics — Why It Works'],
    ['1. Position behind',
     'Stand DIRECTLY BEHIND the choking person. Place one foot between their feet for stability (a wide stance keeps you balanced when you pull).',
     'You need to be behind them to pull inward and upward. A wide stance prevents you both from falling when you apply force.'],
    ['2. Find the landmark',
     'Find the NAVEL (belly button — the small indentation in the centre of the abdomen, where the umbilical cord was attached before birth) with one hand. Find the bottom of the BREASTBONE (the flat bone running down the centre of the chest — feel for where it ends at the bottom, called the xiphisternum or xiphoid process). Your target is the area HALFWAY BETWEEN these two points.',
     'This midpoint is directly over the upper abdomen. When you push here, you compress the stomach and push the diaphragm upward. Avoid the xiphoid process (bottom of breastbone) — it can snap off and cause internal injury.'],
    ['3. Make a fist',
     'Make a fist with your DOMINANT hand. Place the fist against the abdomen at your landmark point, with the THUMB SIDE of the fist touching the body (not the knuckle side). This is important — thumb-side placement ensures the force is directed correctly.',
     'The thumb side of the fist creates a point of contact that translates the inward-and-upward pull into diaphragm compression. Knuckle-side placement redirects force incorrectly and may cause rib injury.'],
    ['4. The thrust',
     'Grasp your fist FIRMLY with your other hand, fingers wrapping around it. Now pull SHARPLY INWARD (toward you) and UPWARD (toward the ceiling) simultaneously. It is one combined movement — in and up — like a letter "J" drawn in the air. Five thrusts in total.',
     'Inward compresses the abdominal contents against the diaphragm. Upward rams the diaphragm into the chest. The chest cavity suddenly shrinks. Air inside the lungs is compressed and rushes upward through the trachea and out of the mouth — acting as an artificial super-cough. Peak airflow generated can exceed 300 litres per minute.'],
    ['5. After each thrust',
     'After each thrust: check the mouth. Has the object appeared? Is the person coughing or breathing? If yes: remove object if visible, encourage coughing, keep watching.',
     'Do not stop and wait after all five — check continuously. The object may be expelled after the very first thrust in some cases.'],
    ['6. If unsuccessful',
     'Return to 5 back blows. Then 5 abdominal thrusts again. Keep alternating: back blows + abdominal thrusts, back blows + abdominal thrusts — until the object is expelled OR the patient loses consciousness.',
     'Different mechanisms — back blows (concussive vibration) and abdominal thrusts (artificial cough) — work better in different situations. Alternating maximises the chance of success.'],
]
story.append(plain_table(heimlich_data, [CW*0.12, CW*0.44, CW*0.44]))
story.append(Spacer(1,4))

memory_hook_inline(
    'Heimlich position: Stand BEHIND. Fist: THUMB side on abdomen. '
    'Location: HALFWAY between navel and breastbone. Pull: INWARD and UPWARD (letter J shape). '
    'Never: over the ribs, over the xiphoid, or over the breastbone itself.', story)

story.append(Spacer(1,4))

# Choking algorithm diagram
diag2 = make_choking_algorithm()
story.append(img2rl(diag2, CW))
story.append(Paragraph(
    'Diagram 2: Complete choking management algorithm for adults — from recognition through back blows, '
    'Heimlich manoeuvre, and CPR for unconscious patients. (Resuscitation Council UK, 2021)',
    ParagraphStyle('Cap2', fontName='DV-I', fontSize=8, leading=11,
                   textColor=HexColor('#555555'), alignment=1)))
story.append(Spacer(1,4))
image_search_box('Heimlich manoeuvre abdominal thrust technique demonstration', 'YouTube — search "Red Cross Heimlich manoeuvre"', story)
divider(story)

# ── §8 SPECIAL POPULATIONS ────────────────────────────────────────────────────
sec_header('8. MANAGEMENT IN SPECIAL POPULATIONS', story)
professor_says(
    'This is where most people fail in exams and in real life — they try to do the standard '
    'Heimlich manoeuvre on an infant and break the baby\'s liver, or they try it on a '
    'pregnant woman and compress the baby. Know these three exceptions COLD.', story)

story.append(Spacer(1,3))
diag3 = make_special_populations()
story.append(img2rl(diag3, CW))
story.append(Paragraph(
    'Diagram 3: Modified techniques for infants (under 1 year), pregnant women, and obese patients.',
    ParagraphStyle('Cap3', fontName='DV-I', fontSize=8, leading=11,
                   textColor=HexColor('#555555'), alignment=1)))
story.append(Spacer(1,5))

spec_data = [
    ['Population', 'Why Standard Heimlich Is Contraindicated', 'Modified Technique', 'Key Differences from Adult'],
    ['INFANT\n(under 1 year of age)',
     'The infant\'s liver (the large organ in the upper right abdomen) lies relatively higher in the abdomen in a baby compared to an adult, and is unprotected. An abdominal thrust on an infant can rupture (tear open) the liver, causing life-threatening internal bleeding.',
     '5 BACK BLOWS: Hold the infant face-DOWN along your forearm (like a rugby ball, with the head at your hand and the legs at your elbow). The infant\'s HEAD must be LOWER than the chest — gravity will help any dislodged object fall forward out of the mouth, not back into the throat. Support the head by holding the jaw gently — do not press the throat. Give 5 firm blows with the HEEL of your free hand between the shoulder blades. Then 5 CHEST THRUSTS: Turn the infant face-UP on your forearm (now the head is at your hand, face up). Place TWO FINGERS on the breastbone — positioned ONE FINGER-WIDTH BELOW the nipple line. Give 5 downward thrusts, each pushing about 1.5cm down. Alternate back blows and chest thrusts.',
     'Head must be LOWER than body throughout. CHEST thrusts (not abdominal). Two fingers on breastbone (not fist). NEVER do blind finger sweeps (insert a finger into a baby\'s mouth and blindly sweep = pushes the object further in).'],
    ['PREGNANT WOMAN\n(any stage of pregnancy)',
     'The pregnant uterus (womb — the organ where the baby grows, which expands as pregnancy progresses) fills the abdominal cavity. An abdominal thrust would compress the uterus and the baby inside it — potentially causing placental abruption (the placenta tearing away from the uterine wall, causing severe bleeding and fetal distress) or direct injury to the fetus.',
     '5 BACK BLOWS: Same as standard adult — lean forward, heel of hand between shoulder blades. Then 5 CHEST THRUSTS: Stand BEHIND the patient. Put both arms UNDER her armpits (at the level of her armpits, not her abdomen). Place your fist on the LOWER HALF OF THE BREASTBONE (not the abdomen). Grasp with the other hand. Pull SHARPLY BACKWARD (not upward — this is different from the standard Heimlich direction). Five times. Alternate back blows and chest thrusts.',
     'Chest thrusts not abdominal. Pull BACKWARD not upward. Hands on lower STERNUM (breastbone), not abdomen. If she becomes unconscious: CPR in LEFT LATERAL TILT (place a wedge or firm cushion under the right hip to tilt her 15-30 degrees to the LEFT) — this moves the heavy uterus off the inferior vena cava (the large vein returning blood to the heart from the lower body) and allows the heart to pump effectively during CPR.'],
    ['OBESE PATIENT\n(very high BMI — body mass index)',
     'The rescuer\'s arms may not reach around the large abdomen to position the fist correctly. The thick layer of fat over the abdomen may absorb the thrust force before it reaches the diaphragm, making abdominal thrusts ineffective.',
     '5 BACK BLOWS: Standard technique — lean forward, heel of hand between shoulder blades. Then 5 CHEST THRUSTS: Same position and technique as for pregnancy — stand behind, arms around chest at armpit level, hands on lower sternum, pull sharply backward. If the patient is too large for you to encircle: position them against a wall or firm surface and attempt chest thrusts from the front. Two-person technique if available.',
     'Chest thrusts not abdominal. May require two rescuers. If unconscious: standard CPR position (no need for lateral tilt unless very late pregnancy).'],
    ['SELF-CHOKING\n(alone with no help)',
     'No one can perform back blows or Heimlich on you. You must self-treat.',
     'Self-administered abdominal thrusts: Make a fist, place it thumb-side against your abdomen at the correct landmark. Use other hand to drive it inward and upward. Alternatively: thrust your upper abdomen hard against a firm edge — the back of a chair, a countertop, the corner of a table. This compresses the abdomen from the front. Several hard thrusts may dislodge the object.',
     'The back-of-chair technique (thrusting your abdomen against the chair back) is widely known. Call 999 FIRST (leave the phone on) before attempting self-treatment — tell the operator you are alone and choking so they can track your location.'],
]
story.append(plain_table(spec_data, [CW*0.14, CW*0.22, CW*0.36, CW*0.28]))
story.append(Spacer(1,4))
memory_hook_inline(
    '"When Heimlich is out, use CHEST thrusts instead." '
    'Three groups where Heimlich is out: Infants (liver injury risk), '
    'Pregnant (uterus injury risk), Obese (cannot reach). '
    'ALL three = back blows + chest thrusts.', story)
image_search_box('infant choking back blows chest thrusts technique', 'YouTube — search "St John Ambulance baby choking"', story)
divider(story)

# ── §9 IN-HOSPITAL MANAGEMENT ─────────────────────────────────────────────────
sec_header('9. IN-HOSPITAL MANAGEMENT — When Basic Manoeuvres Fail', story)
professor_says(
    'The manoeuvres we have learned work in most cases. But what happens when a patient arrives '
    'in the hospital still choking, or when basic manoeuvres have failed? '
    'In a hospital setting, you have tools and skills available that change the picture completely.', story)

hosp_data = [
    ['Intervention', 'Plain English Explanation', 'Who Does It', 'Equipment', 'When Used', 'Complications'],
    ['Direct laryngoscopy\n+ Magill\'s forceps',
     'A laryngoscope (LAR-in-go-scope) is a device with a curved metal blade and a light. It is inserted into the mouth and used to lift the tongue and jaw forward to directly SEE the voice box and the object stuck there. Magill\'s forceps are long, angled, scissor-like forceps (gripping tools) designed to reach into the throat and grasp the foreign body under direct vision.',
     'Emergency doctor, anaesthetist (specialist in airway management and anaesthesia), senior nurse with training',
     'Laryngoscope (Macintosh blade most common), Magill\'s forceps, light source, suction',
     'First-line in-hospital intervention if the object is visible in the larynx (voice box) or above. Can be done without anaesthetic in an emergency.',
     'Dental damage. Throat trauma. Laryngospasm (voice box spasm). Vomiting and aspiration.'],
    ['Flexible bronchoscopy',
     'A bronchoscope (bron-ko-SCOPE) is a thin flexible tube (about the thickness of a pencil) with a camera at the tip and a small working channel through which instruments can be passed. It is passed through the nose or mouth, past the voice box, into the trachea (windpipe) and bronchi (airway branches). The doctor can see exactly where the object is and retrieve it using forceps passed through the working channel.',
     'Respiratory physician (chest doctor), interventional pulmonologist, ENT surgeon',
     'Flexible bronchoscope, light source, monitor, retrieval forceps, snares, baskets',
     'Objects lodged in the trachea or bronchi (windpipe and airway branches). When object is visible but unreachable by laryngoscope.',
     'Bleeding. Airway trauma. Bronchospasm (airway spasm). Pneumothorax (collapsed lung — a rare complication). Requires sedation.'],
    ['Rigid bronchoscopy\n(under general anaesthetic)',
     'A rigid (hard, straight) bronchoscope is a metal tube that is passed under general anaesthesia (total unconsciousness — the patient is completely asleep). It is wider than a flexible scope, allowing larger instruments and better suction. Gives the most control for removing large or difficult objects.',
     'ENT surgeon or thoracic surgeon (chest surgeon), with anaesthetist',
     'Rigid bronchoscope, operating theatre, general anaesthesia equipment, full surgical team',
     'Large foreign bodies. Objects that cannot be grasped with flexible bronchoscope. Sharp objects (to prevent airway injury on removal). Children with foreign body aspiration (most commonly done under general anaesthetic in children).',
     'Risks of general anaesthesia. Airway trauma. Bleeding. Dental damage.'],
    ['Cricothyrotomy\n(emergency surgical airway)',
     'The cricothyroid membrane (kri-ko-THY-royd) is a small but crucially important gap between two cartilages (firm structures) in the voice box: the thyroid cartilage (the Adam\'s apple) above and the cricoid cartilage (the signet ring-shaped cartilage below). This membrane is thin, superficial (close to the surface of the skin), and highly accessible. A cricothyrotomy (making a hole through this membrane) bypasses the obstruction completely — air is delivered directly into the trachea below the stuck object.',
     'Emergency doctor, anaesthetist — this is a "last resort" emergency procedure',
     'Scalpel (surgical knife), size 6.0 cuffed tracheal tube (the breathing tube), 10ml syringe, bag-valve mask, tie/tape to secure the tube. Commercial kits also available.',
     'When ALL other measures have failed and the patient is dying. "Can\'t intubate, can\'t oxygenate" (CICO) — the most feared scenario in anaesthesia. Life-saving emergency.',
     'Incorrect placement. Bleeding. Damage to surrounding structures. Subcutaneous emphysema (air under the skin — feels like bubble wrap under the fingers). This is an emergency procedure — these risks are acceptable given the alternative (death).'],
    ['Tracheostomy\n(definitive surgical airway)',
     'A tracheostomy is a surgically created permanent (or long-term) opening into the trachea (windpipe) through the front of the neck, usually between the 2nd and 3rd tracheal rings. A tube is placed through this opening and the patient breathes through it. Unlike cricothyrotomy (which is a rapid emergency measure), tracheostomy is a planned procedure.',
     'ENT surgeon, general surgeon, thoracic surgeon',
     'Operating theatre, surgical team, anaesthetic support',
     'Long-term airway management (ICU patients on ventilators, patients with neurological conditions affecting swallowing long-term). NOT first-line for acute choking — cricothyrotomy is faster in emergency.',
     'Bleeding. Infection. Tracheal stenosis (narrowing of the windpipe after the tube is removed). Accidental decannulation (tube coming out).'],
]
story.append(plain_table(hosp_data, [CW*0.15, CW*0.28, CW*0.13, CW*0.13, CW*0.17, CW*0.14]))
story.append(Spacer(1,4))
image_search_box('cricothyrotomy technique emergency surgical airway', 'YouTube — search "CICO cricothyrotomy"', story)
image_search_box('rigid bronchoscopy foreign body removal child', 'YouTube', story)
divider(story)

# ── §10 POST-EVENT ASSESSMENT ──────────────────────────────────────────────────
sec_header('10. AFTER THE CHOKING EPISODE — Post-Event Assessment', story)
story.append(Paragraph(
    'Once the object has been removed and the person is breathing again, your job is not over. '
    'The Heimlich manoeuvre is a forceful intervention — it can cause injuries. '
    'Every person who has had abdominal thrusts performed MUST be assessed by a doctor. '
    'And every person who choked must be evaluated for WHY they choked — because choking '
    'is often a symptom of an underlying problem.', sBody))
story.append(Spacer(1,3))

post_data = [
    ['What to Check', 'Why', 'How to Check', 'What Abnormal Means'],
    ['Vital signs\n(basic measurements of body function)',
     'Choking causes hypoxia (low oxygen) which can affect the heart and brain even after the object is removed.',
     'Blood pressure, heart rate, breathing rate, oxygen saturation (SpO2 — measured with a small clip on the fingertip called a pulse oximeter), temperature.',
     'SpO2 < 95% = still some hypoxia = supplemental oxygen needed. Tachycardia (fast heart rate > 100 per minute) = hypoxia or pain. Irregular heart rhythm = hypoxia-induced arrhythmia.'],
    ['Abdominal examination\n(feeling the stomach area)',
     'Abdominal thrusts can injure the liver (the large organ in the upper right abdomen), spleen (the organ in the upper left abdomen — part of the immune system and blood filtering), stomach, or intestines.',
     'Feel (palpate) all four quadrants (quarters) of the abdomen gently with flat hand. Ask about pain. Look for bruising.',
     'Tenderness in the upper right abdomen = possible liver injury. Upper left = possible spleen. Mid-abdomen = possible gastric (stomach) injury. Arrange urgent CT abdomen if significant tenderness.'],
    ['Chest examination\n(feeling and listening to the chest)',
     'Abdominal thrusts can also fracture (break) ribs — especially in elderly patients whose bones are brittle (osteoporosis = thinning of bones, making them fragile). Less commonly, forceful thrusts can cause aortic dissection (tearing of the wall of the aorta — the main blood vessel from the heart).',
     'Palpate the rib cage for tenderness. Listen with a stethoscope: both sides of the chest should sound equal. Chest X-ray.',
     'Rib tenderness + cracking feeling on palpation = rib fracture. Unequal breath sounds = pneumothorax (collapsed lung from rib fracture piercing the lung). Severe central chest pain radiating to the back after thrusts = exclude aortic dissection (CT angiography needed).'],
    ['Examine the throat\n(oropharyngeal assessment)',
     'Look in the mouth with a torch and tongue depressor (a flat wooden stick used to press down the tongue). Is the foreign body still visible? Is there any bleeding in the throat? Has a tooth been knocked out?',
     'Good light, tongue depressor, patient co-operation.',
     'Residual foreign body = remove under direct vision or arrange bronchoscopy. Bleeding in throat = ENT review. Missing tooth = must account for it (could be inhaled into the airway — chest X-ray to check).'],
    ['Chest X-ray',
     'To check for: residual foreign body visible on X-ray (metal, bone, and some plastics are visible; soft food is not), pneumothorax (collapsed lung), rib fractures, aspiration pneumonia (infection in the lung from inhaled material).',
     'Standard PA (posteroanterior = taken from the back to the front) chest X-ray.',
     'Visible foreign body = further intervention. Pneumothorax = chest drain if large. Consolidation (white shadowing in the lung) = aspiration pneumonia = antibiotics.'],
    ['Investigate WHY they choked\n(underlying cause)',
     'Choking is a symptom. If a previously healthy adult chokes on food: probably just ate too fast. But if it is recurring, or if there is difficulty swallowing (dysphagia), there is an underlying problem to find.',
     'Full history: how long have they had swallowing difficulties? Any weight loss? Any voice change? Neurological examination (stroke, Parkinson\'s). Refer to ENT for laryngoscopy. Refer to gastroenterology for barium swallow (a special swallowing X-ray) or endoscopy.',
     'Oesophageal stricture (narrowing of the food pipe) = dilation procedure. Pharyngeal pouch (Zenker\'s diverticulum) = surgical treatment. Oesophageal or laryngeal cancer = urgent investigation. Neurological disease = SALT referral, diet modification.'],
]
story.append(plain_table(post_data, [CW*0.18, CW*0.22, CW*0.22, CW*0.38]))
divider(story)

# ── §11 COMPLICATIONS ─────────────────────────────────────────────────────────
sec_header('11. COMPLICATIONS', story)

comp_data = [
    ['Complication', 'What It Is (Plain English)', 'Mechanism', 'Signs to Look For', 'Management'],
    ['Rib fractures\n(broken ribs)',
     'A crack or complete break in one or more of the 12 pairs of curved bones that make up the rib cage. The rib cage protects the lungs and heart. Fractured ribs are painful, especially on breathing in.',
     'Direct force from the Heimlich manoeuvre or chest thrusts transmitted to the rib cage. Highest risk in elderly patients with osteoporosis (thin, brittle bones).',
     'Localised tenderness over specific ribs on pressing. Pain that is worse on taking a deep breath, coughing, or moving. Crepitus (a crackling or grinding sensation felt when you press the ribs).',
     'Analgesia (pain relief): regular paracetamol + NSAIDs (ibuprofen) if no contraindication. Encourage deep breathing (to prevent pneumonia). Most heal on their own in 6 weeks. Rarely: internal fixation if multiple ribs broken (flail chest).'],
    ['Liver laceration\n(a tear in the liver)',
     'The liver is a large, blood-rich organ in the upper right abdomen. A tear in its surface or deeper tissue causes internal bleeding (bleeding inside the body, not visible from the outside — this makes it dangerous because it can go undetected).',
     'Abdominal thrusts transmit force to the abdominal contents. The liver, being directly below the diaphragm (the breathing muscle) in the right upper abdomen, absorbs this force. Especially high risk if thrusts are placed too high (over the breastbone instead of the abdomen).',
     'Pain in the right upper abdomen (also called the right hypochondrium). Guarding (the abdomen becomes rigid as the muscles contract to protect the injured area). Hypotension (low blood pressure) and tachycardia (fast heart rate) if significant bleeding. Shoulder tip pain (referred pain from blood irritating the diaphragm).',
     'CT abdomen to assess severity. Minor lacerations: conservative (bed rest, monitoring). Major: surgical repair or embolisation (blocking the bleeding blood vessel using a catheter — a thin tube guided by X-ray imaging). Blood transfusion if significant blood loss.'],
    ['Splenic rupture\n(a tear in the spleen)',
     'The spleen is a fist-sized organ in the upper LEFT abdomen. Like the liver, it has a rich blood supply. A tear causes internal bleeding.',
     'Same mechanism as liver laceration. Less common than liver injury. High risk if Heimlich thrusts are placed too far to the left.',
     'Left upper abdominal pain. Kehr\'s sign (pain in the left shoulder tip — the same referred pain pattern as liver injury, just on the opposite side). Signs of internal bleeding (low BP, fast heart rate).',
     'Splenectomy (surgical removal of the spleen) if severe. Conservative management for minor injuries. Post-splenectomy vaccinations (vaccines against specific bacteria: pneumococcus, meningococcus, Haemophilus influenzae) because the spleen helps fight these organisms.'],
    ['Gastric rupture\n(tear in the stomach)',
     'The stomach is the balloon-like organ below the oesophagus (food pipe) where food collects and is mixed with acid. A rupture releases stomach contents (including acid) into the abdominal cavity, causing a condition called peritonitis (peri = around, itis = inflammation — widespread inflammation of the lining of the abdominal cavity).',
     'Extremely rare. Occurs when the stomach is very full (just eaten a large meal) and abdominal thrusts are applied. The sudden pressure on a distended (overfull) stomach can cause it to burst.',
     'Sudden severe abdominal pain after the Heimlich manoeuvre. Rigid "board-like" abdomen. Fever. Patient looks seriously unwell.',
     'Emergency surgery (laparotomy = opening the abdomen surgically to repair the rupture). Antibiotics for peritonitis. High mortality if diagnosis delayed.'],
    ['Aspiration pneumonia\n(lung infection from inhaled material)',
     'During and after choking, vomiting is common (the force of the manoeuvre compresses the stomach). If vomit is inhaled into the lungs, the stomach acid and bacteria cause a serious infection in the lung tissue.',
     'Acid from the stomach damages the lung tissue (chemical pneumonitis — lung inflammation from a chemical, in this case stomach acid). Bacteria from the mouth and stomach also infect the damaged tissue, causing true bacterial pneumonia.',
     'Fever (temperature > 38 degrees C), cough (productive — bringing up infected sputum, which is mucus from the lungs), shortness of breath (breathlessness), crackles (crackling sounds heard through a stethoscope in the affected part of the lung). Chest X-ray shows consolidation (white shadowing in the lower lobes — especially the right lower lobe, as that is where inhaled material most commonly ends up).',
     'Antibiotics: co-amoxiclav (a combination of amoxicillin and clavulanate, a drug that prevents bacteria from breaking down the antibiotic) for community-acquired aspiration pneumonia. Add metronidazole (an antibiotic that kills anaerobic bacteria — bacteria that live without oxygen, common in the mouth) if severe. Physiotherapy to help clear secretions.'],
    ['Aortic dissection\n(rare but life-threatening)',
     'The aorta (ay-OR-ta) is the main artery of the body — as wide as a garden hose — that carries blood from the heart to the whole body. A dissection is a tear in the wall of the aorta, where blood gets between the layers of the arterial wall.',
     'Rare complication. The sudden spike in pressure within the chest during abdominal thrusts can, in very rare cases, cause a tear in the aortic wall — especially in patients who already have weakened arterial walls (e.g. Marfan syndrome, hypertension).',
     'Sudden severe tearing or ripping chest pain radiating to the back. Unequal blood pressure readings in the two arms. Pulse deficit (pulse present on one side, absent on the other). New aortic regurgitation murmur (sound of blood flowing backward through a valve).',
     'Emergency CT aortogram (CT scan of the aorta with contrast dye to visualise the tear). Type A (involving the ascending aorta = the part that goes up from the heart): emergency open-heart surgery. Type B (descending aorta = goes down): medical management (blood pressure control) in most cases.'],
]
story.append(plain_table(comp_data, [CW*0.14, CW*0.18, CW*0.18, CW*0.24, CW*0.26]))
divider(story)

# ── §12 DYSPHAGIA & PREVENTION ────────────────────────────────────────────────
sec_header('12. DYSPHAGIA — Swallowing Difficulties and Prevention of Choking', story)
professor_says(
    'Dysphagia (dis-FAY-jee-ah) — from the Greek "dys" meaning difficult and "phagein" meaning to eat. '
    'It means difficulty swallowing. It is not the same as choking — dysphagia is the chronic '
    'underlying condition that puts a person at repeated risk of choking. '
    'Treating dysphagia prevents future choking episodes.', story)

story.append(Paragraph('Causes of Dysphagia — Two Main Groups', sH2))

dysph_data = [
    ['Cause', 'Plain English', 'Medical Detail', 'Key Investigation', 'Treatment'],
    ['NEUROLOGICAL CAUSES (the brain or nerves controlling swallowing are damaged)', '', '', '', ''],
    ['Stroke\n(cerebrovascular accident — CVA)',
     'A stroke is when blood supply to part of the brain is suddenly cut off (ischaemic stroke — most common, from a clot) or when a blood vessel bursts (haemorrhagic stroke — bleeding into the brain). Up to 50% of stroke survivors have dysphagia.',
     'Damage to the cortex (surface of the brain) or brain stem (the lower part of the brain that controls automatic functions including swallowing) impairs the swallowing reflex. Pseudobulbar palsy (damage to the upper motor neurons controlling the brain stem) or bulbar palsy (direct brain stem damage).',
     'SALT (Speech and Language Therapy) bedside swallowing assessment within 4 hours of admission. Video fluoroscopic swallow study (VFSS) — watching the patient swallow barium under X-ray to see exactly where the swallow goes wrong.',
     'Modified texture diet (soft, pureed, minced). Thickened fluids. NG tube (nasogastric tube — a thin plastic tube passed through the nose, down the throat, into the stomach) for feeding if aspiration risk too high. Long-term: PEG tube (percutaneous endoscopic gastrostomy — a tube directly into the stomach through the abdominal wall, placed by endoscopy).'],
    ["Parkinson's Disease",
     "A progressive neurological disease where the brain's dopamine-producing cells (dopamine = a chemical messenger in the brain that controls movement) gradually die. Swallowing requires precise, co-ordinated movement — and Parkinson's disrupts all coordinated movements.",
     'Bradykinesia (slow movement — brady = slow, kinesia = movement) affects the speed and coordination of the swallowing muscles. Rigidity (stiffness) of the throat muscles. Also: reduced saliva clearance, drooling, and delayed swallowing reflex.',
     'SALT assessment. Clinical swallowing evaluation.',
     "Optimise Parkinson's medications (levodopa/carbidopa must be timed carefully relative to meals). Soft diet. Thickened fluids. SALT therapy. Avoid dry, crumbly foods."],
    ['Motor Neurone Disease\n(MND / ALS)',
     'A progressive disease where the motor neurons (nerve cells that send signals from the brain and spinal cord to muscles) gradually die. Eventually, ALL voluntary muscles weaken — including the swallowing muscles.',
     'Degeneration of upper and lower motor neurons controlling the muscles of the tongue, lips, pharynx, and larynx.',
     'SALT assessment. Nasendoscopy (flexible camera through the nose to look at the throat).',
     'Thickened fluids, pureed diet early. PEG tube feeding as disease progresses. Palliative planning is essential — this disease has no cure.'],
    ['STRUCTURAL CAUSES (there is a physical obstruction or narrowing)', '', '', '', ''],
    ["Pharyngeal pouch\n(Zenker's diverticulum)",
     "A pouch (like a pocket or sac) that forms in the back wall of the throat. Food gets trapped in this pocket instead of going down the oesophagus. When the pocket fills, food regurgitates (comes back up) into the throat — sometimes hours after eating. The regurgitated food can then be inhaled.",
     "Forms at Killian's dehiscence — a weak point between two throat muscles. Increased pressure during swallowing forces the lining through this weak point, creating a diverticulum (a blind-ending pocket).",
     'Barium swallow X-ray (watching barium liquid go down the throat on X-ray) — the pouch fills with barium and is clearly visible. DO NOT do upper endoscopy first without knowing about the pouch — the endoscope can perforate the pouch.',
     'Surgical repair: endoscopic stapling (cutting the wall between the pouch and the oesophagus using a stapler inserted through the mouth) or open surgery. Highly effective.'],
    ['Oesophageal stricture\n(narrowing of the food pipe)',
     'The oesophagus (food pipe — the tube that carries food from the throat to the stomach) becomes narrowed. Food sticks at this narrowing.',
     'Causes: peptic stricture (scarring from chronic acid reflux — stomach acid repeatedly burning the lower oesophagus), post-radiotherapy (radiation treatment for cancer can scar the oesophagus), malignancy (cancer of the oesophagus or stomach pressing from within), rings (Schatzki ring — a thin ring of tissue at the lower oesophagus).',
     'Barium swallow. Upper endoscopy (camera into the oesophagus) for definitive diagnosis and biopsy (tissue sample) if cancer suspected.',
     'Endoscopic dilation (stretching the narrowing using a balloon or bougie — a tapered dilating instrument). Cancer: surgery, radiotherapy, chemotherapy, endoscopic stenting.'],
    ['Oesophageal cancer',
     'A malignant (cancerous) tumour growing in the wall of the oesophagus. As the tumour grows, it narrows the food pipe from the inside.',
     'Two main types: squamous cell carcinoma (from the squamous cells lining the upper two-thirds of the oesophagus — strongly associated with smoking and alcohol) and adenocarcinoma (from glandular cells in the lower oesophagus — associated with chronic gastro-oesophageal reflux and Barrett\'s oesophagus).',
     'Upper GI endoscopy with biopsy. CT chest/abdomen/pelvis for staging. PET scan.',
     'Depends on stage: curative (surgery — Ivor Lewis oesophagectomy = removal of part of oesophagus and stomach) if caught early, combined with neoadjuvant chemotherapy. Palliative (symptom control — endoscopic stenting, radiotherapy) if advanced.'],
]
story.append(plain_table(dysph_data, [CW*0.16, CW*0.18, CW*0.22, CW*0.18, CW*0.26]))
story.append(Spacer(1,5))

story.append(Paragraph('Prevention of Choking — Practical Advice', sH2))
prev_data = [
    ['Preventable Factor', 'Practical Prevention Advice', 'Applies To'],
    ['Eating too fast', 'Put down cutlery between bites. Chew each mouthful at least 20 times before swallowing. Eat at a table, not standing or walking.', 'Everyone, especially adults eating alone'],
    ['Distractions at mealtimes', 'No talking with a mouth full of food. No screens at the dinner table (they distract from chewing). No laughter during mouthfuls.', 'All ages — especially children'],
    ['Large food pieces', 'Cut meat into small pieces (no larger than 1.5cm for elderly). Avoid whole grapes for children under 5 (cut into quarters lengthwise). Avoid hard boiled sweets, large pieces of hard bread.', 'Children under 5 years, elderly, denture wearers'],
    ['Unsafe foods for children', 'Under 3 years: no whole grapes, no whole nuts, no raw carrots, no whole hot dogs, no large chunks of meat, no hard candy. These are the classic choking foods in children.', 'Infants and toddlers'],
    ['Alcohol before eating', 'Avoid heavy alcohol before or during meals. Even moderate alcohol impairs swallowing coordination and the cough reflex.', 'Adults'],
    ['Unsupervised children eating', 'Always sit children down for meals. Always supervise children under 5 during eating. Never let young children eat in car seats (reclined position = harder to swallow safely).', 'Infants and toddlers'],
    ['Known dysphagia (swallowing problems)', 'Follow SALT advice on food texture and fluid thickness. Use IDDSI (International Dysphagia Diet Standardisation Initiative) framework: 7 levels from thin liquid to regular food. Ensure carers know the patient\'s diet level.', 'Post-stroke, Parkinson\'s, MND, dementia patients'],
    ['Small objects accessible to children', 'Keep coins, batteries (especially small "button" batteries — highly toxic if swallowed or inhaled), toy parts, jewellery out of reach. Toys rated for age appropriateness.', 'Homes with children under 5'],
]
story.append(plain_table(prev_data, [CW*0.22, CW*0.52, CW*0.26]))
divider(story)

# ── §13 CROSS-SUBJECT CONNECTIONS ─────────────────────────────────────────────
sec_header('13. CROSS-SUBJECT CONNECTIONS', story)
cross_data = [
    ['Medical Subject', 'Connection to Choking / FBAO', 'Key Learning Point'],
    ['Neurology',
     'Stroke (up to 50% have dysphagia). Parkinson\'s disease (bradykinesia impairs swallowing). Motor Neurone Disease (progressive bulbar palsy). Myasthenia gravis (fatigable weakness — gets worse with repeated use — affects swallowing muscles late in disease). Guillain-Barre syndrome (acute ascending paralysis that can affect cranial nerves and swallowing).',
     'Always assess swallowing in any neurological patient. Silent aspiration (food entering the airway without triggering a cough) is dangerous because it goes unnoticed — leads to recurrent aspiration pneumonia.'],
    ['Paediatrics',
     'Foreign body aspiration (FBA) is a paediatric emergency. Peak age: 6 months - 3 years. Objects: coins (most common), toy parts, batteries, food (nuts, grapes, hot dogs). Right bronchus more commonly affected. Chest X-ray: may show overinflation of one lung (air trapping — the object acts as a one-way valve, letting air in but not out) rather than collapse.',
     'Classic presentation: sudden onset cough, wheeze, or stridor in a previously well child. ALWAYS suspect FBA in a child with sudden onset unilateral wheeze. Rigid bronchoscopy under general anaesthesia is the definitive treatment.'],
    ['ENT (Ear, Nose and Throat)',
     'Laryngoscopy, rigid bronchoscopy, tracheostomy. Pharyngeal pouch (Zenker\'s diverticulum). Laryngeal cancer (voice change + dysphagia = refer urgently to ENT). Post-radiotherapy strictures.',
     'Indirect laryngoscopy (using a mirror) or flexible nasendoscopy (a flexible camera through the nose) allows visualisation of the larynx. Critical skill for ENT assessment of dysphagia.'],
    ['Gastroenterology',
     'Oesophageal food bolus impaction (food gets stuck in the food pipe, not the airway — different from choking. Patient can still breathe but cannot swallow, saliva pools). Oesophageal stricture, Schatzki ring, achalasia (the lower oesophageal sphincter fails to relax), oesophageal cancer.',
     'Food bolus impaction: treatment is endoscopic removal or allowing it to pass spontaneously (often with buscopan/hyoscine to relax the oesophageal muscle). NOT the same emergency as airway obstruction — but may mimic it in a panic.'],
    ['Anaesthesia',
     'Rapid Sequence Induction (RSI) — the technique used when a patient with a full stomach needs to be intubated (a breathing tube inserted) urgently: pre-oxygenate, apply cricoid pressure (pressing on the cricoid cartilage to compress the oesophagus and prevent regurgitation), give rapid-acting induction agent (propofol) + muscle relaxant (suxamethonium), intubate. "Can\'t intubate, can\'t oxygenate" (CICO) = surgical airway immediately.',
     'Cricoid pressure (Sellick\'s manoeuvre): press on the cricoid cartilage (the ring-shaped cartilage below the voice box, easily palpable) to compress the oesophagus against the vertebra behind it. Prevents passive regurgitation of stomach contents during induction of anaesthesia.'],
    ['Infectious Disease / Respiratory Medicine',
     'Aspiration pneumonia: most common in the right lower lobe (right bronchus more vertical = right lower lobe is where aspirated material settles). Causative organisms: mixed aerobic and anaerobic bacteria from the mouth — Streptococcus, Staphylococcus, Klebsiella, anaerobes. Treatment: co-amoxiclav + metronidazole. Lung abscess as a complication of untreated aspiration pneumonia.',
     'Aspiration is a predisposing factor for lung abscess (a contained pocket of pus in the lung). Suspect in patients with: fever + productive cough + weight loss + alcohol abuse history + abnormal swallowing. CT chest + sputum culture. Prolonged antibiotics (6-12 weeks).'],
    ['Geriatrics',
     'Choking is disproportionately common in elderly patients. Multiple risk factors: reduced swallowing reflex, poor dentition, dentures, cognitive impairment (dementia), polypharmacy (taking many medications — anticholinergics and antihistamines cause dry mouth, making it harder to form a food bolus).',
     'Always review medications in elderly patients with dysphagia. Tricyclic antidepressants, antihistamines, antipsychotics, antiparkinsonian drugs — all cause dry mouth (xerostomia). Regular saliva substitutes and adequate hydration help.'],
    ['Radiology',
     'Chest X-ray: look for hyperlucency (one lung appearing blacker/more air-filled than the other = air trapping from one-way valve obstruction), consolidation (white shadowing = aspiration pneumonia), foreign body (visible if metal or bone). Barium swallow: shows pharyngeal pouch, oesophageal stricture, motility disorders. CT: best for complex cases.',
     'The CLASSIC X-ray finding of foreign body aspiration in children: one lung overinflated (more black) compared to the other. The object acts like a valve — air gets in past it, but cannot get out. The lung traps progressively more air. This is called obstructive emphysema.'],
]
story.append(plain_table(cross_data, [CW*0.16, CW*0.46, CW*0.38]))
divider(story)

# ── §14 MRCP EXAM TRIGGERS ────────────────────────────────────────────────────
sec_header('14. MRCP EXAM TRIGGERS — 12 Clinical Scenarios', story)

triggers = [
    ('A 2-year-old is brought to A&E (Accident and Emergency — the emergency department) with sudden onset coughing and wheezing that started during play. He is afebrile (no fever) and was previously well. His chest X-ray shows hyperinflation of the right lung. What is the diagnosis and management?',
     'Foreign body aspiration (FBA). The sudden onset in a previously well child during play = inhaled object. Afebrile (no temperature) = not an infection. Right lung hyperinflation on chest X-ray = air trapping (the foreign body acts as a one-way valve in the right bronchus: air gets past it on breathing in but cannot escape on breathing out). The right main bronchus is more vertical and wider = objects almost always go right. Management: urgent rigid bronchoscopy under general anaesthesia by an ENT surgeon or paediatric surgeon. The object is retrieved under direct vision using forceps through the rigid scope. Do NOT attempt Heimlich if the child is still coughing and breathing — only intervene if complete obstruction develops.'),
    ('In a restaurant, a 55-year-old man suddenly grabs his throat, cannot speak, and is going blue. He cannot cough. His partner asks what to do. Walk through the exact management sequence.',
     'Severe FBAO (foreign body airway obstruction). He cannot speak + cannot cough + is cyanotic (going blue) = complete obstruction = SEVERE. Management sequence: (1) Call 999 immediately (get someone else to call while you act). (2) Stand to his side and slightly behind him. Support his chest. Lean him forward. Give 5 FIRM BACK BLOWS with the heel of the hand between the shoulder blades. Check after each. (3) If back blows fail: stand BEHIND him. Fist (thumb side) on the abdomen, halfway between navel and breastbone. Other hand over fist. Pull SHARPLY INWARD AND UPWARD. 5 times. (4) ALTERNATE: 5 back blows, 5 abdominal thrusts, 5 back blows, etc. (5) If he becomes unconscious: lower carefully, START CPR (30:2), look in the mouth before each breath. These are the exact Resuscitation Council UK 2021 guidelines.'),
    ('After successful Heimlich manoeuvre, the patient complains of severe right upper abdominal pain with tenderness. BP is 90/60 (normal is around 120/80). What has happened and what do you do?',
     'Liver laceration (tear in the liver) from the abdominal thrusts. The combination of right upper quadrant pain + tenderness + hypotension (low blood pressure — BP 90/60 means blood pressure has dropped) = internal bleeding from the liver. The liver is directly under the diaphragm in the right upper abdomen and can be lacerated by forceful thrusts — especially if the thrusts were too high (over the lower ribs rather than the abdomen). Management: IV access (two large-bore cannulas), IV fluids and blood transfusion, urgent CT abdomen to assess severity, surgical or interventional radiology (embolisation = blocking the bleeding vessel using a catheter) depending on severity. This patient needs emergency hospital assessment.'),
    ('You are called to assess a 78-year-old woman in a care home who has been found unresponsive after a meal. She has advanced dementia. What is your immediate assessment?',
     'Consider FBAO as the cause of unresponsiveness. She is in a high-risk group: elderly, dementia (impaired swallowing reflex, does not recognise danger foods), found after a meal. Assessment: Is she breathing? Look for chest rise, feel for airflow, listen. Is there a pulse? If not breathing: start CPR. LOOK IN THE MOUTH before each rescue breath: if you see food, remove it. If breathing but unresponsive: airway assessment, recovery position (left lateral — on the left side — to prevent aspiration of vomit). Consider other causes: stroke, cardiac arrest, hypoglycaemia (low blood sugar — check with a glucometer). Call 999. In a care home context: dementia patients should have a clear plan from SALT regarding safe feeding, appropriate diet texture, and supervision during meals.'),
    ('A 45-year-old pregnant woman at 28 weeks of pregnancy (28 weeks = 7 months pregnant) chokes on a large piece of food. She cannot speak. What do you do differently compared to a non-pregnant adult?',
     'CHEST THRUSTS instead of abdominal thrusts — the Heimlich manoeuvre is contraindicated in pregnancy because it compresses the uterus (womb) and can injure the baby. Management: (1) 5 back blows (same as standard — lean forward, heel of hand between shoulder blades). (2) If back blows fail: chest thrusts — stand BEHIND her, arms under her armpits, hands on the LOWER STERNUM (breastbone, NOT the abdomen), pull SHARPLY BACKWARD. (3) Alternate: 5 back blows + 5 chest thrusts. (4) If she becomes unconscious: lower to the floor, start CPR, apply LEFT LATERAL TILT (raise the right side with a cushion, tilting her 15-30 degrees to the left) so the heavy uterus does not compress the inferior vena cava (the main vein returning blood to the heart from the legs and lower body).'),
    ('A man is choking and loses consciousness before back blows or Heimlich can be effective. He is on the floor. What do you do?',
     'Start CPR immediately. The sequence: (1) Call 999 if not already done. (2) Start CPR: 30 chest compressions (push hard and fast in the centre of the chest, at least 5-6cm deep, at 100-120 per minute), then 2 rescue breaths. (3) BEFORE each rescue breath: look in the mouth. If you CAN SEE a foreign body, remove it with your fingers. If you CANNOT see it: do NOT do a blind finger sweep (pushing your finger in blindly = pushes the object deeper). (4) Chest compressions themselves generate bursts of intrathoracic pressure that may help dislodge the object. (5) After each set of compressions: re-open the airway, look for the object, attempt rescue breaths. (6) If the object becomes visible: remove it. Continue CPR until ambulance arrives.'),
    ('What are the three groups of patients in whom the Heimlich manoeuvre (abdominal thrusts) is contraindicated, and what do you use instead?',
     'Three groups: (1) INFANTS under 1 year — liver is high in the abdomen and unprotected; use 5 back blows + 5 CHEST THRUSTS instead. (2) PREGNANT WOMEN — compresses the uterus and baby; use 5 back blows + 5 CHEST THRUSTS instead (hands on lower sternum, pull backward). (3) OBESE PATIENTS where the rescuer cannot encircle the abdomen — use 5 back blows + 5 CHEST THRUSTS instead (same technique as pregnancy). Memory: "When Heimlich is out, use Chest thrusts." All three groups use the same alternative: back blows + chest thrusts.'),
    ('A 65-year-old man with Parkinson\'s disease (a brain disease affecting movement) has had three episodes of chest infection in the last year. On examination, you notice he drools, speaks quietly, and takes a long time to swallow. What is the underlying problem and how do you manage it?',
     'This man has dysphagia (swallowing difficulty) secondary to Parkinson\'s disease. The recurrent chest infections are ASPIRATION PNEUMONIA — he is repeatedly inhaling food or drink into his lungs. Evidence: drooling (cannot clear saliva efficiently = swallowing impaired), quiet voice (bulbar involvement in Parkinson\'s), slow swallowing. Management: (1) SALT (Speech and Language Therapy) assessment urgently — formal swallowing evaluation to identify the exact problem (which phase of swallowing is impaired, is he silently aspirating). (2) Optimise Parkinson\'s medications — levodopa (the main drug for Parkinson\'s, replaced the missing dopamine) must be given at consistent times, not missed, not near meals. (3) Modified diet: softer texture, thickened fluids. (4) Consider NG tube if aspiration risk too high. (5) Review with gastroenterology/nutrition if long-term feeding tube (PEG) may be needed.'),
    ('What is a "silent aspirator" and why is this patient at high risk?',
     'A silent aspirator is someone who regularly inhales food, fluid, or secretions into their lungs WITHOUT coughing (no protective cough reflex triggered). The cough reflex is absent or severely impaired (e.g. stroke affecting the brain stem, advanced dementia, severe Parkinson\'s). Why high risk: (1) The patient and carers do not know aspiration is happening — there is no warning cough. (2) Each episode deposits food/fluid/bacteria into the lungs. (3) Repeated aspiration causes recurrent pneumonia (chest infections), progressive lung damage, and can be life-threatening. Diagnosis: videofluoroscopic swallow study (VFSS) — watching swallowing on X-ray with barium — is the gold standard to detect silent aspiration. Management: modified diet texture, thickened fluids (Grade 4 — pureed texture or Grade 1-3 thickened fluids per IDDSI), feeding position (sit upright at 90 degrees during and for 30 minutes after eating).'),
    ('A food bolus is stuck in the oesophagus (food pipe). The patient can breathe normally but cannot swallow and is drooling. How does this differ from airway obstruction and how is it managed?',
     'Oesophageal food bolus impaction is NOT the same as choking (FBAO). The key difference: the patient CAN BREATHE NORMALLY because the airway is NOT blocked — food is stuck in the food pipe (oesophagus), not in the breathing tube (trachea). The patient cannot swallow even their own saliva (drooling). This is extremely uncomfortable but not immediately life-threatening (unlike airway obstruction). Management: (1) Do NOT do back blows or Heimlich — this is not airway obstruction. (2) Reassure the patient. (3) Do NOT give more food or drink to try to push it down. (4) IV access. (5) Buscopan (hyoscine butylbromide — a drug that relaxes smooth muscle in the oesophagus) 20mg IV — may allow the bolus to pass. (6) Urgent upper GI endoscopy (camera through the mouth into the oesophagus) to retrieve or push the bolus down. (7) After resolution: investigate for underlying stricture, ring, or motility disorder.'),
    ('After the Heimlich manoeuvre successfully dislodges the food, a 70-year-old woman with osteoporosis (thin brittle bones) complains of left-sided chest pain that is worse on breathing in. What has happened?',
     'Rib fracture from the Heimlich manoeuvre (or chest thrusts). Left-sided chest pain worse on inspiration (breathing in) = classic pleuritic chest pain from a rib fracture. Patients with osteoporosis are at high risk because their bones are thin and brittle — even moderate force can fracture ribs. Note: if CHEST THRUSTS were used (because she may have been obese or pregnant is unclear here, but may have been given chest thrusts by a rescuer who was unfamiliar with technique), the sternum and anterior ribs are particularly vulnerable. Investigation: chest X-ray to confirm rib fractures and exclude pneumothorax (a collapsed lung, which can occur if a fractured rib pierces the lung). Management: regular analgesia (paracetamol + NSAID if tolerated; avoid opiates if possible as they suppress coughing and increase pneumonia risk), deep breathing exercises (using an incentive spirometer — a device that measures breath depth — helps keep the lungs expanded), physiotherapy. Most rib fractures heal in 6 weeks.'),
    ('What is a "cafe coronary" and why is it historically significant?',
     'A "cafe coronary" was the term used before 1974 to describe a situation where a person suddenly collapsed in a restaurant, was assumed to have had a heart attack (coronary = relating to the coronary arteries, which supply blood to the heart muscle), and died — when in fact they had choked to death on food. The term was coined because the presentation (sudden collapse, blue face, unresponsive, death) looked exactly like a cardiac arrest to bystanders. Before the Heimlich manoeuvre was described (in 1974, JAMA — Journal of the American Medical Association), there was no standard treatment, and thousands died annually from choking that could have been prevented. Dr Henry Heimlich published his description of the abdominal thrust technique, and deaths from choking in restaurants dropped dramatically within years. The term is now historical — it serves as a reminder that what looks like a cardiac arrest during a meal may actually be FBAO.'),
]
for i, (q, a) in enumerate(triggers):
    tdata = [
        [Paragraph(f'<b>Scenario {i+1}:</b> {q}',
                   ParagraphStyle(f'QS{i}', fontName='DV-B', fontSize=8.5, leading=12, textColor=NAVY))],
        [Paragraph(f'<b>Answer:</b> {a}',
                   ParagraphStyle(f'AS{i}', fontName='DV', fontSize=8, leading=12, textColor=NAVY))],
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
    story.append(t); story.append(Spacer(1,5))
divider(story)

# ── §15 PACES + MINIMAL RESOURCES ────────────────────────────────────────────
sec_header('15. PACES EXAMINATION &amp; MINIMAL RESOURCES', story)

story.append(Paragraph('A. PACES — Assessing a Patient After Choking or With Dysphagia', sH2))
paces_data = [
    ['Step', 'What To Do', 'What You Are Assessing', 'What to Say to Examiner'],
    ['1. Immediate safety\ncheck',
     'First ensure the acute emergency is over: Is the patient now breathing comfortably? Is the obstruction fully cleared? SpO2 (oxygen level) on pulse oximeter.',
     'Airway patency (is the airway now fully open and clear?). Respiratory rate (how many breaths per minute — normal is 12-20 per minute). SpO2 (normal >95% on room air).',
     '"My first priority is to ensure the airway is now clear and the patient is breathing safely. I note SpO2 is [X]%."'],
    ['2. Vital signs',
     'Full set of observations: blood pressure, pulse, respiratory rate, temperature, SpO2.',
     'Signs of haemodynamic instability (is the patient in shock from internal bleeding after Heimlich?). Tachycardia + hypotension = possible internal injury.',
     '"Blood pressure is [X], pulse [X] — I am concerned about the possibility of internal injury from the abdominal thrusts, given the haemodynamic picture."'],
    ['3. Oral cavity examination',
     'Use a torch and tongue depressor. Look: Is any residual foreign body visible? Is there blood or trauma to the oral mucosa (the skin inside the mouth)? Are all teeth present?',
     'Residual foreign body. Oral/pharyngeal trauma. Missing teeth (could be in the airway).',
     '"I note [finding]. I would request a chest X-ray to exclude a retained foreign body and rib fractures."'],
    ['4. Respiratory examination',
     'Inspection (look at the chest — is it moving symmetrically?). Percussion (tap the chest — resonant = normal; stony dull = fluid; hyper-resonant = air). Auscultation (listen with stethoscope — equal breath sounds?). Check for crackles (crackling sounds = aspiration pneumonia) or absent breath sounds (pneumothorax).',
     'Pneumothorax (collapsed lung from rib fracture). Aspiration pneumonia. Bronchial breathing (a harsh breath sound heard over consolidation = infected lung).',
     '"On auscultation, I note [finding] in the [right/left] base, consistent with possible aspiration pneumonia. I would request a chest X-ray and appropriate antibiotics."'],
    ['5. Abdominal examination',
     'Inspect: any bruising over the upper abdomen from the thrusts? Palpate: all four quadrants for tenderness and guarding (the abdomen going rigid — the muscles contract to protect an injured organ beneath). Auscultate: bowel sounds.',
     'Liver laceration (right upper quadrant tenderness). Splenic injury (left upper quadrant). Gastric perforation (diffuse tenderness + rigidity).',
     '"I note tenderness in the right upper quadrant with guarding, raising concern for hepatic injury. I would request urgent CT abdomen."'],
    ['6. Neurological\nassessment for dysphagia',
     'If the choking was related to dysphagia: assess cranial nerves IX (gag reflex), X (vocal cord movement — is the voice hoarse?), XII (tongue movement — can they stick out the tongue straight and move it side to side?). Assess speech (is it slurred or nasal?). Watch a test swallow.',
     'Signs of neurological cause for dysphagia: bulbar palsy (damage to brain stem = weak tongue, nasal speech, absent gag) vs pseudobulbar palsy (damage above brain stem = brisk jaw jerk, spastic tongue, emotional lability = sudden inappropriate laughing or crying).',
     '"I note [finding] suggesting bulbar/pseudobulbar involvement. I would refer urgently to SALT for swallowing assessment and request appropriate neuroimaging."'],
    ['7. Closing statement',
     'Summarise, propose investigations, propose management.',
     '',
     '"In summary, this patient has had a choking episode. Post-event assessment reveals [findings]. I would request: chest X-ray, CT abdomen if abdominal tenderness, SALT assessment for dysphagia, and appropriate analgesia. I would investigate the underlying cause of choking with upper GI endoscopy or barium swallow."'],
]
story.append(plain_table(paces_data, [CW*0.13, CW*0.27, CW*0.27, CW*0.33]))
story.append(Spacer(1,6))

story.append(Paragraph('B. Minimal Resources Protocol — Managing Choking With Basic Equipment Only', sH2))
story.append(Paragraph(
    '<b>At your facility: clinical examination + X-ray + CBC + medicines. No CT, no bronchoscope, no ITU.</b> '
    'Here is how to manage each choking scenario with these resources.', sBody))
story.append(Spacer(1,3))

min_data = [
    ['Scenario', 'Management With Minimal Resources', 'Investigations Available', 'When to Refer / Transfer'],
    ['Acute choking — object expelled\nby back blows / Heimlich',
     'Full clinical assessment after the event. Vital signs. Oral examination. Chest and abdominal examination. Reassure the patient.',
     'Chest X-ray: check for residual foreign body (visible if metal/bone), rib fractures, aspiration pneumonia (consolidation). CBC: check for signs of haemorrhage (dropping haemoglobin = internal bleeding).',
     'Transfer if: signs of internal injury (falling BP, abdominal tenderness), pneumothorax, or visible retained foreign body on X-ray.'],
    ['Child with suspected inhaled\nforeign body (still breathing)',
     'If coughing effectively = do NOT intervene mechanically. Position upright. Monitor closely. Obtain chest X-ray (both PA and lateral, and decubitus — lying on the side — views to look for air trapping).',
     'Chest X-ray (both inspiratory and expiratory views if child can cooperate — air trapping is clearest on expiratory view). CBC if infection suspected.',
     'ALWAYS TRANSFER to a centre with paediatric bronchoscopy capability. Even if the child seems comfortable, an inhaled foreign body MUST be retrieved bronchoscopically. Do not delay.'],
    ['Patient with dysphagia\n(swallowing difficulty)',
     'Full clinical assessment: history (when did it start, solids or liquids or both, weight loss, voice change, neurological symptoms). Examination (cranial nerves IX, X, XII, examine oropharynx). Assess a test swallow (watch the patient swallow a small amount of water).',
     'CBC (anaemia may suggest malignancy or nutritional deficiency). Chest X-ray (aspiration pneumonia). Blood glucose, thyroid function (thyroid enlargement can compress the oesophagus). If stroke suspected: clinical assessment, refer for CT brain.',
     'Refer: urgent SALT assessment. ENT or gastroenterology referral for endoscopy or barium swallow. Urgent referral if: progressive dysphagia + weight loss (suspect malignancy). Neurological referral if new focal signs.'],
    ['Aspiration pneumonia',
     'Clinical diagnosis: fever + productive cough + reduced breath sounds and crackles in a patient with known or suspected aspiration risk. Treat with antibiotics based on clinical assessment.',
     'Chest X-ray: consolidation (white shadowing) typically in right lower lobe. CBC: raised WBC (leucocytosis = high white blood count, confirming infection). CRP (raised = inflammation/infection). Sputum culture if productive cough (collect before starting antibiotics if possible).',
     'Admit if: SpO2 < 92%, respiratory rate > 25/min, confusion, hypotension, bilateral consolidation on X-ray, or immunocompromised. IV antibiotics if severe.'],
    ['Recurrent choking in an\nelderly or neurological patient',
     'Medication review (anticholinergics causing dry mouth = stop if possible). Dietary modification (soft diet, small pieces, ensure sitting upright). Educate carers in correct feeding technique and emergency back blows/Heimlich.',
     'Blood glucose, thyroid, CBC (exclude systemic causes). Chest X-ray (baseline, prior aspiration pneumonia?).',
     'Refer: SALT for formal swallowing assessment. ENT for laryngoscopy if structural cause suspected. Gastroenterology for endoscopy if oesophageal cause suspected. Nutritional assessment.'],
]
story.append(plain_table(min_data, [CW*0.20, CW*0.32, CW*0.23, CW*0.25]))
story.append(Spacer(1,6))

# Memory hook
sec_header('16. MEMORY HOOK — The Complete Story', story)
hook_text = (
    'Choking — foreign body airway obstruction (FBAO) — kills when food or an object enters '
    'the larynx (the voice box in your throat, just below the epiglottis, the trapdoor that '
    'normally snaps shut when you swallow to protect the airway) and blocks air from reaching '
    'the lungs. The brain begins to die without oxygen in just 4 minutes. Recognise it instantly: '
    'hands clutching the throat, cannot speak, cannot cough effectively (a silent cough means '
    'NO air is moving = complete obstruction = act now), going blue (cyanosis from '
    'deoxygenated blood). MILD = can cough strongly, can speak = encourage to cough. '
    'SEVERE = cannot cough, cannot speak = call 999, then 5 back blows (lean forward, '
    'heel of hand between the shoulder blades), then 5 abdominal thrusts '
    '(Heimlich: stand behind, fist thumb-side on abdomen halfway between navel and '
    'breastbone, pull sharply inward AND upward), alternating until cleared or '
    'patient collapses. If unconscious: CPR (30:2), look in mouth before each breath — '
    'remove the object only if you can SEE it (never blind finger sweep). '
    'Three groups get chest thrusts instead of abdominal thrusts: INFANTS (liver injury risk '
    '— back blows face-down + two-finger chest thrusts face-up), '
    'PREGNANT WOMEN (compresses baby — back blows + hands on lower sternum pulling backward), '
    'OBESE patients (cannot reach — same as pregnancy). Post-event: ALWAYS assess for '
    'complications — liver laceration (right upper abdominal pain), splenic injury, rib '
    'fractures (chest pain on breathing = post-Heimlich rib fracture = chest X-ray), '
    'aspiration pneumonia (fever + right lower lobe consolidation = co-amoxiclav + metronidazole). '
    'Chronic dysphagia (difficulty swallowing) predisposes to choking: stroke (50% have dysphagia '
    '— SALT assessment within 4 hours), Parkinson\'s (bradykinesia impairs swallowing), '
    'pharyngeal pouch (Zenker\'s — food regurgitates hours later, diagnosed with barium swallow, '
    'endoscopic stapling), oesophageal cancer (progressive dysphagia + weight loss = urgent '
    'endoscopy). Silent aspirators are the most dangerous — they inhale food without coughing, '
    'develop recurrent pneumonia, and nobody notices until the damage is done. '
    'In children: sudden onset wheeze in a previously well child = inhaled foreign body until '
    'proven otherwise. Right lung overinflation on chest X-ray = object in right bronchus acting '
    'as a one-way valve. Treatment: rigid bronchoscopy under general anaesthetic.'
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
    '<i>Choking &amp; Heimlich Manoeuvre — MRCP Parts 1, 2 &amp; PACES Revision Note</i>',
    ParagraphStyle('Ft', fontName='DV-I', fontSize=8, leading=11,
                   textColor=HexColor('#888888'), alignment=1)))

# ── BUILD PDF ─────────────────────────────────────────────────────────────────
doc.build(story)
print('SUCCESS: /mnt/user-data/outputs/Choking_Heimlich_MRCP_Note.pdf')
