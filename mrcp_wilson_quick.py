"""
Wilson's Disease – Visual Quick Note (Presentation-Style)
PassMedicine-style: 22-year-old, tremor + dysarthria + transaminitis → Decreased serum caeruloplasmin
"""
import os, textwrap
from reportlab.lib.pagesizes import A3
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, PageBreak, Image as RLImage)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from PIL import Image, ImageDraw, ImageFont

# ── OUTPUT ──────────────────────────────────────────────────────────────────
OUT = '/mnt/user-data/outputs/Wilsons_Disease_Quick_Note.pdf'
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# ── FONTS ────────────────────────────────────────────────────────────────────
FONT_DIR = '/usr/share/fonts/truetype/dejavu/'
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
for nm, fn in [('DV','DejaVuSans.ttf'),('DV-B','DejaVuSans-Bold.ttf'),
               ('DV-I','DejaVuSansMono-Oblique.ttf'),('DV-BI','DejaVuSansMono-BoldOblique.ttf')]:
    pdfmetrics.registerFont(TTFont(nm, FONT_DIR+fn))

# ── PAGE ──────────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A3
MARGIN = 22*mm
CW = PAGE_W - 2*MARGIN

# ── COLOURS ──────────────────────────────────────────────────────────────────
TEAL    = '#0d5c63'; TEAL_M  = '#1a8a94'; TEAL_L  = '#e0f4f5'; TEAL_XL = '#f0fafb'
AMBER   = '#fff3cd'; AMBER_B = '#e6a817'
GREEN_L = '#d4edda'; GREEN_D = '#28a745'
RED_L   = '#fde8e8'; RED_D   = '#c0392b'
ORA_L   = '#fef3e2'; ORA_D   = '#d4640a'
BLUE_L  = '#e8f4fd'; BLUE_D  = '#2471a3'
PUR_L   = '#f5eef8'; PUR_D   = '#7d3c98'
NAVY    = '#1a1a2e'; WHITE   = '#ffffff'
GOLD_L  = '#fffaed'; GOLD_D  = '#b8860b'

def c(h): return colors.HexColor(h)

# ── STYLES ───────────────────────────────────────────────────────────────────
def S(name,font='DV',size=11,leading=16,color=NAVY,after=6,align=TA_LEFT,before=0):
    return ParagraphStyle(name,fontName=font,fontSize=size,leading=leading,
                          textColor=c(color),spaceAfter=after,spaceBefore=before,alignment=align)

sTitle = S('Ti','DV-B',26,32,WHITE,8,TA_CENTER)
sSub   = S('Su','DV-B',16,22,TEAL_L,6,TA_CENTER)
sH1    = S('H1','DV-B',17,22,TEAL,8,TA_LEFT)
sH2    = S('H2','DV-B',13,18,TEAL_M,6,TA_LEFT)
sBody  = S('Bo','DV',12,18,NAVY,4,TA_LEFT)
sPro   = S('Pr','DV-B',12,18,PUR_D,4,TA_LEFT)
sImg   = S('Im','DV-I',10,14,'#555555',4,TA_CENTER)
sAlert = S('Al','DV-B',12,17,RED_D,4,TA_LEFT)
sMem   = S('Me','DV-B',12,18,GREEN_D,4,TA_LEFT)
sQ     = S('Q' ,'DV-B',12,18,BLUE_D,4,TA_LEFT)
sHint  = S('Hi','DV-I',11,16,'#555555',2,TA_LEFT)
sAns   = S('An','DV-B',12,18,GREEN_D,4,TA_LEFT)
sQNum  = S('QN','DV-B',12,18,NAVY,2,TA_LEFT)
sVig   = S('Vi','DV',12,18,NAVY,6,TA_LEFT)
sOpt   = S('Op','DV',12,18,NAVY,3,TA_LEFT)
# Extra for visual style
sBIG   = S('BG','DV-B',22,28,GREEN_D,4,TA_CENTER)
sANSW  = S('AN','DV-B',14,20,NAVY,4,TA_CENTER)
sGrnB  = S('GB','DV-B',12,18,GREEN_D,4,TA_LEFT)
sGrn   = S('GN','DV',12,18,NAVY,4,TA_LEFT)
sRED   = S('RE','DV-B',12,17,RED_D,4,TA_LEFT)
sCOP   = S('CO','DV-B',13,18,GOLD_D,4,TA_LEFT)

# ── HELPERS ──────────────────────────────────────────────────────────────────
def bp(story): story.append(PageBreak())
def divider(story, color=TEAL_M):
    story.append(Spacer(1,4))
    story.append(HRFlowable(width=CW, thickness=1.5, color=c(color)))
    story.append(Spacer(1,6))

def sec_header(txt, story, bg=TEAL, fg=WHITE):
    t = Table([[Paragraph(txt, ParagraphStyle('SH',fontName='DV-B',fontSize=14,
               leading=20,textColor=c(fg),spaceAfter=0,alignment=TA_LEFT))]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),c(bg)),
        ('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),14),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('ROUNDEDCORNERS',[4])]))
    story.append(t); story.append(Spacer(1,8))

def plain_table(headers, rows, story, col_w=None):
    if col_w is None:
        n = len(headers); col_w = [CW/n]*n
    data = [[Paragraph(str(h), ParagraphStyle('TH',fontName='DV-B',fontSize=11,
              leading=15,textColor=c(WHITE),spaceAfter=0)) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(cell), ParagraphStyle('TD',fontName='DV',fontSize=11,
                     leading=15,textColor=c(NAVY),spaceAfter=0)) for cell in row])
    t = Table(data, colWidths=col_w)
    ts = [('BACKGROUND',(0,0),(-1,0),c(TEAL)),('ROWBACKGROUNDS',(0,1),(-1,-1),[c(TEAL_XL),c(WHITE)]),
          ('GRID',(0,0),(-1,-1),0.5,c(TEAL_M)),
          ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
          ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
          ('VALIGN',(0,0),(-1,-1),'TOP')]
    t.setStyle(TableStyle(ts)); story.append(t); story.append(Spacer(1,10))

def alert_box(txt, story, bg=AMBER, border=AMBER_B):
    t = Table([[Paragraph(txt, sAlert)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),c(bg)),('BOX',(0,0),(-1,-1),2,c(border)),
        ('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),14),
        ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,8))

def info_box(txt, story, bg=BLUE_L, border=BLUE_D):
    t = Table([[Paragraph(txt, sBody)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),c(bg)),('BOX',(0,0),(-1,-1),2,c(border)),
        ('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),14),
        ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,8))

def big_answer(text, story):
    t = Table([[Paragraph(text, sBIG)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),c(GREEN_L)),('BOX',(0,0),(-1,-1),3,c(GREEN_D)),
        ('LEFTPADDING',(0,0),(-1,-1),20),('RIGHTPADDING',(0,0),(-1,-1),20),
        ('TOPPADDING',(0,0),(-1,-1),16),('BOTTOMPADDING',(0,0),(-1,-1),16)]))
    story.append(t); story.append(Spacer(1,10))

def image_search_box(query, story):
    txt = f'<b>[IMAGE]</b> Search: "{query}" — add to Notability'
    t = Table([[Paragraph(txt, sImg)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),c('#f8f9fa')),('BOX',(0,0),(-1,-1),1,c('#aaaaaa')),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(t); story.append(Spacer(1,6))

def mem(txt, story):
    t = Table([[Paragraph('🔑  ' + txt, sMem)]], colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),c(GREEN_L)),('BOX',(0,0),(-1,-1),2,c(GREEN_D)),
        ('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),14),
        ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,8))

# ── PIL TEXT-SAFE TOOLKIT ────────────────────────────────────────────────────
CARD_FONTS = {'T':24,'B':17,'XS':14}
PAD_X = 46

def load_fonts():
    fnt = {}
    for k,sz in CARD_FONTS.items():
        path = FONT_DIR + ('DejaVuSans-Bold.ttf' if 'B' in k else 'DejaVuSans.ttf')
        fnt[k] = ImageFont.truetype(path, sz)
    return fnt

def text_w(draw, text, font):
    bb = draw.textbbox((0,0), text, font=font)
    return bb[2]-bb[0]

def wrap_text(draw, text, font, max_w):
    words = text.split(); lines = []; cur = ''
    for w in words:
        test = (cur+' '+w).strip()
        if text_w(draw, test, font) <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def lh(font): return font.size + 6

def draw_block(draw, text, font, x, y, max_w, color='#1a1a2e', center=False):
    lines = wrap_text(draw, text, font, max_w)
    for line in lines:
        if center:
            tw = text_w(draw, line, font)
            draw.text(((max_w - tw)//2 + x, y), line, font=font, fill=color)
        else:
            draw.text((x, y), line, font=font, fill=color)
        y += lh(font)
    return y

def card(draw, fnt, x, y, w, title, bullets, bg_h, bg_b, border, title_col=WHITE):
    PAD = 12
    draw.rectangle([x,y,x+w,y+9999], fill=bg_h, outline=border, width=2)
    cy = y+PAD
    cy = draw_block(draw,title,fnt['B'],x+PAD,cy,w-2*PAD,title_col,center=True)
    cy += 4
    draw.line([x+8,cy,x+w-8,cy],fill=border,width=1); cy += 6
    for b in bullets:
        cy = draw_block(draw,b,fnt['XS'],x+PAD+10,cy,w-2*PAD-10,'#1a1a2e')
        cy += 3
    draw.rectangle([x,y,x+w,cy+PAD],fill=bg_b,outline=border,width=2)
    return cy+PAD

def header_band(draw, fnt, x, y, w, text, bg, fg=WHITE):
    PAD=12
    lines = wrap_text(draw, text, fnt['B'], w-2*PAD)
    h = len(lines)*lh(fnt['B'])+2*PAD
    draw.rectangle([x,y,x+w,y+h],fill=bg,outline=bg,width=0)
    cy = y+PAD
    for line in lines:
        tw = text_w(draw, line, fnt['B'])
        draw.text(((w-tw)//2+x, cy), line, font=fnt['B'], fill=fg); cy+=lh(fnt['B'])
    return y+h

def finish(img, max_h=None):
    w,h = img.size
    if max_h and h>max_h: img = img.crop((0,0,w,max_h))
    return img

def i2r(img, cw):
    import io
    buf = io.BytesIO()
    img.save(buf,'PNG')
    buf.seek(0)
    ri = RLImage(buf)
    ri.drawWidth  = cw
    ri.drawHeight = cw * img.height / img.width
    return ri

# ═══════════════════════════════════════════════════════════════════════════════
# DIAGRAM 1 — Copper Options Visual (Why Each Option Right/Wrong)
# ═══════════════════════════════════════════════════════════════════════════════
def make_options():
    W=900; fnt=load_fonts()
    OPTIONS = [
        ('A',  '↓ Decreased serum caeruloplasmin',  True,
         ["ATP7B mutation → copper can't attach to caeruloplasmin",
          "Result: low caeruloplasmin, low TOTAL serum copper",
          "But FREE copper is HIGH → toxic to organs",
          "THE ANSWER ✓"]),
        ('B',  '↑ Increased serum caeruloplasmin',  False,
         ["Wrong direction — Wilson's = DECREASED caeruloplasmin",
          "Caeruloplasmin rises in acute inflammation, pregnancy",
          "Normal/high caeruloplasmin rules against Wilson's"]),
        ('C',  '↑ Increased total serum copper',    False,
         ["Counterintuitive trap! Total serum copper is LOW/normal",
          "Because caeruloplasmin (copper carrier) is low",
          "FREE copper is high, but total measured = low",
          "24h URINE copper is HIGH — that's the correct marker"]),
        ('D',  '↓ Decreased serum ferritin',        False,
         ["Ferritin = iron storage protein — not a copper disorder",
          "Ferritin may be high in Wilson's (liver inflammation)",
          "Low ferritin suggests iron deficiency anaemia"]),
        ('E',  '↑ Increased serum alpha-1-antitrypsin', False,
         ["Alpha-1-antitrypsin is a protease inhibitor",
          "Deficiency (not excess) causes liver + lung disease",
          "Phenotype ZZ = most severe liver disease",
          "Young liver disease: think Wilson's + A1AT deficiency"]),
    ]
    rows=[]; PAD=16
    for letter, label, correct, bullets in OPTIONS:
        cols=[]; cols.append((letter, label, correct, bullets))
        rows.append(cols)

    bgs_h = {True: GREEN_D, False: RED_D}
    bgs_b = {True: GREEN_L, False: RED_L}
    borders= {True: GREEN_D, False: RED_D}

    # estimate height
    tmpImg = Image.new('RGB',(W,50)); tmpD = ImageDraw.Draw(tmpImg)
    total_h = PAD
    for letter, label, correct, bullets in OPTIONS:
        tmp_h = 28+8+8  # header
        for b in bullets: tmp_h += lh(fnt['XS'])*len(wrap_text(tmpD,b,fnt['XS'],W-4*PAD-40))+3
        tmp_h += 2*PAD
        total_h += tmp_h + 10
    total_h += 40

    img = Image.new('RGB',(W,min(total_h+80,1600)),WHITE)
    d   = ImageDraw.Draw(img)

    # header
    y = header_band(d,fnt,0,0,W,'ANSWER OPTIONS — WHY CORRECT / WHY WRONG',TEAL)
    y += PAD

    for letter, label, correct, bullets in OPTIONS:
        bh = bgs_h[correct]; bb = bgs_b[correct]; br = borders[correct]
        full = f'{letter}.  {label}'
        cy = card(d,fnt,PAD,y,W-2*PAD,full,bullets,bh,bb,br,title_col=WHITE)
        y = cy + 10

    img = finish(img, y+20)
    return img

# ═══════════════════════════════════════════════════════════════════════════════
# DIAGRAM 2 — Wilson's Disease Key Facts
# ═══════════════════════════════════════════════════════════════════════════════
def make_keyfacts():
    W=900; H_MAX=1400; fnt=load_fonts(); PAD=16
    img = Image.new('RGB',(W,H_MAX),WHITE)
    d   = ImageDraw.Draw(img)

    y = header_band(d,fnt,0,0,W,"WILSON'S DISEASE — KEY FACTS FOR MRCP",TEAL)
    y += PAD

    SECTIONS = [
        (BLUE_D, BLUE_L, BLUE_D, "THE BASICS",
         ["Autosomal recessive copper metabolism disorder",
          "Gene: ATP7B mutation (chromosome 13)",
          "ATP7B = copper-transporting ATPase in hepatocytes",
          "Result: copper accumulates in liver, brain, eyes, kidneys",
          "Age of onset: usually 5–35 years (young person key!)"]),
        (GOLD_D, GOLD_L, GOLD_D, "INVESTIGATIONS — THE COPPER PATTERN",
         ["↓ Serum caeruloplasmin (< 0.2 g/L) — KEY FINDING",
          "↓ Total serum copper — copper carrier is low",
          "↑ FREE (unbound) serum copper — the toxic form",
          "↑ 24-hour urine copper (> 100 µg/day) — most useful",
          "Liver biopsy: ↑ hepatic copper (> 250 µg/g dry weight)"]),
        (PUR_D, PUR_L, PUR_D, "CLINICAL FEATURES — THE TRIAD",
         ["LIVER: Hepatitis → cirrhosis → acute liver failure",
          "NEUROLOGICAL: Tremor (postural/intention), dysarthria, dysphagia",
          "PSYCHIATRIC: Personality change, depression, psychosis",
          "EYES: Kayser-Fleischer (KF) rings — green-brown ring at corneal periphery",
          "RENAL: Fanconi syndrome (RTA type 2, glycosuria, aminoaciduria)"]),
        (TEAL, TEAL_L, TEAL_M, "DIAGNOSIS — CONFIRMED BY",
         ["KF rings on slit-lamp examination (present in 95% neuro Wilson's)",
          "Caeruloplasmin < 0.2 g/L + 24h urine copper > 100 µg/day",
          "Leipzig score ≥ 4 = confirmed Wilson's disease",
          "Liver biopsy if diagnosis uncertain"]),
    ]

    for bg_h, bg_b, border, title, bullets in SECTIONS:
        cy = card(d,fnt,PAD,y,W-2*PAD,title,bullets,bg_h,bg_b,border,title_col=WHITE)
        y = cy+10

    img = finish(img, y+20)
    return img

# ═══════════════════════════════════════════════════════════════════════════════
# DIAGRAM 3 — Management Ladder
# ═══════════════════════════════════════════════════════════════════════════════
def make_treatment():
    W=900; H_MAX=1200; fnt=load_fonts(); PAD=16
    img = Image.new('RGB',(W,H_MAX),WHITE)
    d   = ImageDraw.Draw(img)

    y = header_band(d,fnt,0,0,W,'TREATMENT LADDER — WILSON\'S DISEASE',TEAL)
    y += PAD

    STEPS = [
        (RED_D,    RED_L,    RED_D,    "STEP 1: SYMPTOMATIC (Liver / Neuro Presentation)",
         ["D-Penicillamine — copper chelator, first-line",
          "Removes copper via urine (increases urinary excretion)",
          "Side effects: rash, nephropathy, lupus-like, worsening neuro (initial)",
          "Pyridoxine (B6) given alongside to prevent deficiency"]),
        (ORA_D,    ORA_L,    ORA_D,    "STEP 2: ALTERNATIVE CHELATOR (If penicillamine intolerant)",
         ["Trientine (triethylenetetramine) — preferred alternative",
          "Fewer side effects than D-penicillamine",
          "Also copper chelator — promotes urinary excretion",
          "Can be used in pregnancy (D-penicillamine teratogenic)"]),
        (BLUE_D,   BLUE_L,   BLUE_D,   "STEP 3: MAINTENANCE / PRESYMPTOMATIC",
         ["Zinc acetate — blocks intestinal copper absorption",
          "Induces metallothionein → binds copper in gut epithelium",
          "Used for presymptomatic patients (siblings of cases)",
          "Used for maintenance after chelation therapy",
          "Safe in pregnancy (treatment of choice when pregnant)"]),
        (GREEN_D,  GREEN_L,  GREEN_D,  "STEP 4: ACUTE LIVER FAILURE",
         ["Liver transplant — curative (corrects metabolic defect)",
          "Transplant restores normal ATP7B function",
          "KF rings regress post-transplant",
          "Neuro Wilson's is NOT an indication alone"]),
    ]

    for bg_h, bg_b, border, title, bullets in STEPS:
        cy = card(d,fnt,PAD,y,W-2*PAD,title,bullets,bg_h,bg_b,border,title_col=WHITE)
        y = cy+12

    img = finish(img, y+20)
    return img

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD PDF
# ═══════════════════════════════════════════════════════════════════════════════
doc = SimpleDocTemplate(OUT, pagesize=A3,
      leftMargin=MARGIN, rightMargin=MARGIN,
      topMargin=MARGIN, bottomMargin=MARGIN)

story = []
ANSWER_KEY = []

# ── PAGE 1: COVER ─────────────────────────────────────────────────────────────
cover_bg = Table([[Paragraph("WILSON'S DISEASE", sTitle)]], colWidths=[CW])
cover_bg.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),c(TEAL)),
    ('LEFTPADDING',(0,0),(-1,-1),24),('RIGHTPADDING',(0,0),(-1,-1),24),
    ('TOPPADDING',(0,0),(-1,-1),18),('BOTTOMPADDING',(0,0),(-1,-1),18),
    ('ROUNDEDCORNERS',[6])]))
story.append(cover_bg); story.append(Spacer(1,10))

sub_bg = Table([[Paragraph('Visual Quick Note  |  PassMedicine MRCP', sSub)]], colWidths=[CW])
sub_bg.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),c(TEAL_M)),
    ('LEFTPADDING',(0,0),(-1,-1),16),('RIGHTPADDING',(0,0),(-1,-1),16),
    ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
story.append(sub_bg); story.append(Spacer(1,18))

# Clinical vignette
info_box('<b>QUESTION STEM:</b> A 22-year-old man is referred to the neurology clinic with '
         '<b>new-onset postural tremor</b> and <b>mild dysarthria</b>. No past medical history. '
         'Bloods show: <b>ALT 85 IU/L, AST 72 IU/L</b> (mild transaminitis). What is the '
         'most likely biochemical abnormality?', story, BLUE_L, BLUE_D)

story.append(Paragraph('<b>THE ANSWER IS:</b>', sANSW))
big_answer('(A)  Decreased serum caeruloplasmin', story)

rule_bg = Table([[Paragraph('WHY? ATP7B mutation → copper cannot attach to caeruloplasmin '
                             '→ ↓ caeruloplasmin, ↑ FREE copper (toxic)', sANSW)]], colWidths=[CW])
rule_bg.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),c(TEAL)),
    ('LEFTPADDING',(0,0),(-1,-1),16),('RIGHTPADDING',(0,0),(-1,-1),16),
    ('TOPPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),12)]))
story.append(rule_bg); story.append(Spacer(1,14))

alert_box('⚠  COPPER TRAP: Total serum copper is LOW (because carrier protein is low). '
          'But FREE copper is HIGH and that is what damages organs. '
          '24h urine copper is HIGH = the most useful test.', story, AMBER, AMBER_B)

mem('YOUNG + Liver + Neuro/Psych + KF rings = WILSON\'S disease until proven otherwise', story)
image_search_box("Kayser-Fleischer ring slit lamp Wilson's disease", story)

divider(story)
story.append(Paragraph(
    '<b>Remember the COPPER equation:</b>  '
    '↓ Caeruloplasmin  |  ↓ Total serum Cu  |  ↑ FREE Cu  |  ↑ 24h urine Cu  |  ↑ Liver Cu', sBody))

bp(story)

# ── PAGE 2: OPTIONS DIAGRAM ───────────────────────────────────────────────────
sec_header('ALL 5 OPTIONS EXPLAINED — RIGHT & WRONG', story)
opts_img = make_options()
story.append(i2r(opts_img, CW))
story.append(Spacer(1,8))
story.append(Paragraph(
    '<b>Key distinction:</b> Alpha-1-antitrypsin deficiency causes liver disease too '
    '(young person!), but the clue is neuro symptoms + copper findings.', sBody))

bp(story)

# ── PAGE 3: KEY FACTS DIAGRAM ─────────────────────────────────────────────────
sec_header("WILSON'S DISEASE — KEY FACTS", story)
facts_img = make_keyfacts()
story.append(i2r(facts_img, CW))
story.append(Spacer(1,8))

# Copper Pattern summary table
plain_table(
    ['Test', 'Wilson\'s Disease', 'Normal'],
    [['Serum caeruloplasmin',  '↓ LOW (< 0.2 g/L)', '0.2–0.6 g/L'],
     ['Total serum copper',    '↓ LOW or normal',    '11–22 µmol/L'],
     ['Free serum copper',     '↑ HIGH (toxic)',     '< 1.6 µmol/L'],
     ['24h urine copper',      '↑ HIGH (> 100 µg/day)', '< 40 µg/day'],
     ['Liver copper',          '↑ HIGH (> 250 µg/g dry wt)', '< 50 µg/g'],
     ['KF rings (slit lamp)',  'Present (95% neuro Wilson\'s)', 'Absent']],
    story,
    col_w=[CW*0.38, CW*0.31, CW*0.31])

bp(story)

# ── PAGE 4: TREATMENT DIAGRAM ─────────────────────────────────────────────────
sec_header('TREATMENT — STEP-BY-STEP', story)
tx_img = make_treatment()
story.append(i2r(tx_img, CW))
story.append(Spacer(1,10))

alert_box('⚠  D-Penicillamine may WORSEN neurological symptoms initially — '
          'paradoxical worsening occurs in ~25% at start of treatment. '
          'DO NOT stop! Reduce dose if severe.', story, AMBER, AMBER_B)

plain_table(
    ['Drug', 'Mechanism', 'Use Case'],
    [['D-Penicillamine', 'Chelates copper → urine', 'First-line symptomatic'],
     ['Trientine',       'Chelates copper → urine', 'Penicillamine intolerance'],
     ['Zinc acetate',    'Blocks gut absorption',   'Maintenance / pregnancy'],
     ['Liver transplant','Corrects ATP7B defect',   'Acute liver failure']],
    story)

bp(story)

# ── PAGE 5: MEMORY CARD ───────────────────────────────────────────────────────
sec_header("MASTER MEMORY CARD — WILSON'S DISEASE", story, NAVY, WHITE)

gTS1 = TableStyle([('BACKGROUND',(0,0),(-1,0),c(GREEN_D)),('ROWBACKGROUNDS',(0,1),(-1,-1),[c(GREEN_L),c(WHITE)]),
       ('GRID',(0,0),(-1,-1),0.5,c(GREEN_D)),('LEFTPADDING',(0,0),(-1,-1),10),
       ('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),6),
       ('BOTTOMPADDING',(0,0),(-1,-1),6),('BOX',(0,0),(-1,-1),2.5,c(GREEN_D)),
       ('VALIGN',(0,0),(-1,-1),'TOP')])

mem_data = [
    [Paragraph('CONCEPT', ParagraphStyle('MH',fontName='DV-B',fontSize=12,leading=16,textColor=c(WHITE),spaceAfter=0)),
     Paragraph('REMEMBER THIS', ParagraphStyle('MH',fontName='DV-B',fontSize=12,leading=16,textColor=c(WHITE),spaceAfter=0))],
    [Paragraph('<b>Gene / Inheritance</b>', sGrnB), Paragraph('ATP7B mutation — Autosomal Recessive', sGrn)],
    [Paragraph('<b>Pathology</b>', sGrnB), Paragraph('Copper accumulates: Liver → Brain → Eyes → Kidneys', sGrn)],
    [Paragraph('<b>Key biochemistry</b>', sGrnB), Paragraph('↓ Caeruloplasmin, ↓ Total Cu, ↑ Free Cu, ↑ Urine Cu', sGrn)],
    [Paragraph('<b>The Trap</b>', sGrnB), Paragraph('Total serum copper is LOW (not high!) — FREE copper is the culprit', sGrn)],
    [Paragraph('<b>Clinical Triad</b>', sGrnB), Paragraph('Liver disease + Neuro (tremor/dysarthria) + Psychiatric', sGrn)],
    [Paragraph('<b>Eye Sign</b>', sGrnB), Paragraph('Kayser-Fleischer rings (slit lamp) — absent if only liver disease', sGrn)],
    [Paragraph('<b>Age group</b>', sGrnB), Paragraph('Typically 5–35 years — any young person with liver + neuro', sGrn)],
    [Paragraph('<b>Treatment 1st line</b>', sGrnB), Paragraph('D-Penicillamine (chelator) — may worsen neuro initially', sGrn)],
    [Paragraph('<b>Treatment if intolerant</b>', sGrnB), Paragraph('Trientine → then Zinc (maintenance) → Transplant (ALF)', sGrn)],
    [Paragraph('<b>Pregnancy drug</b>', sGrnB), Paragraph('Zinc acetate — safe. Penicillamine and trientine: discuss risk', sGrn)],
    [Paragraph('<b>Exam tip</b>', sGrnB), Paragraph('Young + liver + neuro = Wilson\'s. KF rings absent ≠ rules out Wilson\'s', sGrn)],
]
mem_t = Table(mem_data, colWidths=[CW*0.30, CW*0.70])
mem_t.setStyle(gTS1)
story.append(mem_t); story.append(Spacer(1,12))

mem('MNEMONIC  W.I.L.S.O.N:  Wilson\'s = Inherited (AR), Liver disease, Slit-lamp rings, '
    'Out (excreted via urine copper), Neuropsych', story)

alert_box('⚠  Minimal Resources:  PassMedicine | Oxford Handbook of Clinical Medicine '
          '(OHCM) Ch. Gastroenterology → Wilson\'s Disease | Ganesh & Kuruvilla: '
          'The Medicine Guide pp. 312–314', story, ORA_L, ORA_D)

story.append(Spacer(1,10))
story.append(Paragraph(
    'Wilson\'s disease is one of the most commonly tested MRCP genetics-meets-metabolics topics. '
    'The key is knowing the copper pattern: caeruloplasmin DOWN, free copper UP, urine copper UP.', sHint))

# ── BUILD ─────────────────────────────────────────────────────────────────────
doc.build(story)
print("PDF built →", OUT)
