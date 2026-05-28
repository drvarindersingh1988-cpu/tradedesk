import io, os
from PIL import Image, ImageDraw, ImageFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, Image as RLImage, PageBreak)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
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

TEAL  = HexColor('#0d5c63'); TEAL_M = HexColor('#1a8a94')
TEAL_L= HexColor('#e0f4f5'); TEAL_XL= HexColor('#f0fafb')
AMBER = HexColor('#fff3cd'); AMBER_B= HexColor('#e6a817')
GREEN_L=HexColor('#d4edda'); GREEN_D= HexColor('#28a745')
RED_L = HexColor('#fde8e8'); RED_D  = HexColor('#c0392b')
ORA_L = HexColor('#fef3e2'); ORA_D  = HexColor('#d4640a')
BLUE_L= HexColor('#e8f4fd'); BLUE_D = HexColor('#2471a3')
PUR_L = HexColor('#f5eef8'); PUR_D  = HexColor('#7d3c98')
NAVY  = HexColor('#1a1a2e'); WHITE  = HexColor('#ffffff')

PAGE_W, PAGE_H = A4; MARGIN = 18*mm; CW = PAGE_W - 2*MARGIN
doc = SimpleDocTemplate('/mnt/user-data/outputs/Bleeding_Trauma_MRCP_Note.pdf',
    pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=MARGIN, bottomMargin=MARGIN)

def S(n, **k):
    return ParagraphStyle(n, fontName=k.get('font','DV'),
        fontSize=k.get('sz',10), leading=k.get('lead',14),
        textColor=k.get('color',NAVY), spaceAfter=k.get('sa',4),
        spaceBefore=k.get('sb',2), alignment=k.get('align',0),
        leftIndent=k.get('li',0))

sTitle=S('T', font='DV-B',sz=22,color=TEAL, sa=6,align=1)
sSub  =S('Su',font='DV-I',sz=10,color=TEAL_M,sa=4,align=1)
sH1   =S('H1',font='DV-B',sz=13,color=TEAL, sa=4)
sH2   =S('H2',font='DV-B',sz=11,color=TEAL_M,sa=3)
sBody =S('Bo',font='DV',  sz=9, lead=14,    sa=3)
sHook =S('Hk',font='DV',  sz=9, lead=14,color=HexColor('#1a5c2a'),sa=0)
sAlert=S('Al',font='DV-B',sz=9, lead=13,color=RED_D, sa=3)
sImg  =S('Im',font='DV-I',sz=8, lead=12,color=BLUE_D,sa=2)
sPro  =S('Pr',font='DV-I',sz=9, lead=14,color=HexColor('#2c3e50'),sa=3,li=12)

def sec_header(t, story):
    story.append(Spacer(1,6)); story.append(Paragraph(t, sH1)); story.append(Spacer(1,3))

def divider(story):
    story.append(Spacer(1,4))
    t = Table([['']],colWidths=[CW])
    t.setStyle(TableStyle([('LINEABOVE',(0,0),(0,0),1,TEAL_M),
        ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
    story.append(t); story.append(Spacer(1,4))

def plain_table(data, cws, alt=True):
    sth=ParagraphStyle('PTH',fontName='DV-B',fontSize=8,leading=11,
        textColor=WHITE,spaceAfter=0,spaceBefore=0)
    std=ParagraphStyle('PTD',fontName='DV',fontSize=7.5,leading=11,
        textColor=NAVY,spaceAfter=0,spaceBefore=0)
    def w(c,h):
        if isinstance(c,str): return Paragraph(c.replace('\n','<br/>'),sth if h else std)
        return c
    pd=[[w(c,ri==0) for c in row] for ri,row in enumerate(data)]
    t=Table(pd,colWidths=cws,repeatRows=1)
    base=[('BACKGROUND',(0,0),(-1,0),TEAL),('GRID',(0,0),(-1,-1),0.5,TEAL_M),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5)]
    if alt: base.append(('ROWBACKGROUNDS',(0,1),(-1,-1),[TEAL_XL,TEAL_L]))
    t.setStyle(TableStyle(base)); return t

def alert_box(text, story, color=RED_L, border=RED_D):
    t=Table([[Paragraph(text,sAlert)]],colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),color),
        ('BOX',(0,0),(-1,-1),1.5,border),('TOPPADDING',(0,0),(-1,-1),6),
        ('BOTTOMPADDING',(0,0),(-1,-1),6),('LEFTPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,4))

def info_box(text, story, color=AMBER, border=AMBER_B):
    t=Table([[Paragraph(text,sBody)]],colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),color),
        ('BOX',(0,0),(-1,-1),1.5,border),('TOPPADDING',(0,0),(-1,-1),6),
        ('BOTTOMPADDING',(0,0),(-1,-1),6),('LEFTPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,4))

def image_search_box(term, site, story):
    txt=f'IMAGE: Search <b>"{term}"</b> on <b>{site}</b> to visualise this concept.'
    t=Table([[Paragraph(txt,sImg)]],colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),BLUE_L),
        ('BOX',(0,0),(-1,-1),1,BLUE_D),('TOPPADDING',(0,0),(-1,-1),4),
        ('BOTTOMPADDING',(0,0),(-1,-1),4),('LEFTPADDING',(0,0),(-1,-1),8)]))
    story.append(t); story.append(Spacer(1,3))

def professor_says(text, story):
    t=Table([[Paragraph(f'<i>Professor: {text}</i>',sPro)]],colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),TEAL_XL),
        ('BOX',(0,0),(-1,-1),1,TEAL_M),('TOPPADDING',(0,0),(-1,-1),6),
        ('BOTTOMPADDING',(0,0),(-1,-1),6),('LEFTPADDING',(0,0),(-1,-1),12),
        ('RIGHTPADDING',(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,4))

def memory_hook(text, story):
    sM=ParagraphStyle('MI',fontName='DV-B',fontSize=8.5,leading=13,
        textColor=HexColor('#7b3f00'),spaceAfter=0)
    t=Table([[Paragraph(f'MEMORY: {text}',sM)]],colWidths=[CW])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),AMBER),
        ('BOX',(0,0),(-1,-1),1.5,AMBER_B),('TOPPADDING',(0,0),(-1,-1),5),
        ('BOTTOMPADDING',(0,0),(-1,-1),5),('LEFTPADDING',(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,4))

# PIL helpers
def pf(sz):
    try: return ImageFont.truetype(FD+'DejaVuSans.ttf',sz)
    except: return ImageFont.load_default()
def pfb(sz):
    try: return ImageFont.truetype(FD+'DejaVuSans-Bold.ttf',sz)
    except: return ImageFont.load_default()
def ts(draw,text,font):
    bb=draw.textbbox((0,0),text,font=font); return bb[2]-bb[0],bb[3]-bb[1]
def wt(draw,text,font,mw):
    words=text.split(); lines,cur=[],''
    for w in words:
        t=(cur+' '+w).strip()
        if ts(draw,t,font)[0]<=mw: cur=t
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines
def arr_d(draw,cx,y1,y2,col='#555555',w=2,hs=8):
    draw.line([(cx,y1),(cx,y2)],fill=col,width=w)
    draw.polygon([(cx,y2),(cx-hs//2,y2-hs),(cx+hs//2,y2-hs)],fill=col)
def arr_r(draw,x1,x2,cy,col='#555555',w=2,hs=8):
    draw.line([(x1,cy),(x2,cy)],fill=col,width=w)
    draw.polygon([(x2,cy),(x2-hs,cy-hs//2),(x2-hs,cy+hs//2)],fill=col)
def draw_box(draw,cx,y,lines,border,fill,px=14,py=10,lg=5,mw=160,acc=True):
    ld=[]; cw=mw-2*px-(6 if acc else 0)
    for txt,font,col in lines:
        for wl in wt(draw,txt,font,cw):
            ww,wh=ts(draw,wl,font); cw=max(cw,ww); ld.append((wl,font,col,ww,wh))
    bw=cw+2*px+(6 if acc else 0)
    bh=sum(h for _,_,_,_,h in ld)+(len(ld)-1)*lg+2*py
    bx=cx-bw//2
    draw.rectangle([bx,y,bx+bw,y+bh],fill=fill,outline=border,width=2)
    if acc: draw.rectangle([bx,y,bx+6,y+bh],fill=border)
    ty=y+py; off=3 if acc else 0
    for txt,font,col,ww,wh in ld:
        draw.text((cx-ww//2+off,ty),txt,font=font,fill=col); ty+=wh+lg
    return y+bh
def i2r(img,w):
    buf=io.BytesIO(); img.save(buf,'PNG'); buf.seek(0)
    return RLImage(buf,width=w,height=w*img.height/img.width)

# =============================================================================
# PIL DIAGRAM 1 — ATLS Classification of Haemorrhagic Shock
# =============================================================================
def make_atls_diagram():
    W=900
    classes=[
        ('CLASS I','Up to 750 ml','Up to 15%','<100','Normal','Normal or raised',
         '14-20','Normal / anxious','#28a745','#d4edda',
         'Like donating blood. Body compensates easily. No treatment needed beyond stop the bleeding.'),
        ('CLASS II','750-1500 ml','15-30%','100-120','Normal or slightly low','Raised',
         '20-30','Anxious, restless','#f9a825','#fff9c4',
         'Car accident with leg wound. IV fluids. Stop the bleeding. Watch closely.'),
        ('CLASS III','1500-2000 ml','30-40%','120-140','LOW (BP starts falling)','Very raised',
         '30-40','Confused','#ef6c00','#fef3e2',
         'Ruptured spleen. Immediate IV fluids, blood products, surgery likely.'),
        ('CLASS IV','>2000 ml','>40%','>140 or undetectable','VERY LOW','Weak/thready',
         '>35','Lethargic, unconscious','#c62828','#fde8e8',
         'IMMEDIATE life threat. Massive transfusion protocol. Surgery NOW.'),
    ]
    row_h=115; H=len(classes)*row_h+110
    img=Image.new('RGB',(W,H),'#ffffff')
    draw=ImageDraw.Draw(img)
    draw.rectangle([0,0,W,45],fill='#0d5c63')
    t='ATLS CLASSIFICATION OF HAEMORRHAGIC SHOCK (Advanced Trauma Life Support)'
    tw,_=ts(draw,t,pfb(13)); draw.text(((W-tw)//2,13),t,font=pfb(13),fill='#ffffff')
    # Column headers
    hdrs=['CLASS','BLOOD LOSS','% BLOOD\nVOLUME','HEART\nRATE','BLOOD\nPRESSURE',
          'PULSE\nPRESSURE','RESP\nRATE','MENTAL\nSTATUS']
    col_xs=[45,145,240,330,415,500,590,670]
    col_ws=[90,90,85,80,80,85,80,115]
    draw.rectangle([0,48,W,78],fill='#1a1a2e')
    for i,(h,cx,cw) in enumerate(zip(hdrs,col_xs,col_ws)):
        hw,hh=ts(draw,h.split('\n')[0],pfb(9))
        draw.text((cx-hw//2,52),h.split('\n')[0],font=pfb(9),fill='#ffffff')
        if '\n' in h:
            h2=h.split('\n')[1]; hw2,_=ts(draw,h2,pfb(9))
            draw.text((cx-hw2//2,64),h2,font=pfb(9),fill='#ffffff')
    for i,(cls,ml,pct,hr,bp,pp,rr,ms,col,bg,note) in enumerate(classes):
        y=82+i*row_h
        draw.rectangle([5,y,W-5,y+row_h-4],fill=bg,outline=col,width=2)
        draw.rectangle([5,y,12,y+row_h-4],fill=col)
        vals=[cls,ml,pct,hr,bp,pp,rr,ms]
        for j,(v,cx,cw) in enumerate(zip(vals,col_xs,col_ws)):
            fn=pfb(11) if j==0 else pf(10)
            fc=col if j==0 else '#1a1a2e'
            vlines=wt(draw,v,fn,cw-4)
            vy=y+8
            for vl in vlines:
                vw,vh=ts(draw,vl,fn)
                draw.text((cx-vw//2,vy),vl,font=fn,fill=fc); vy+=vh+2
        # Note at bottom of row
        nlines=wt(draw,note,pf(8),W-30)
        ny=y+row_h-22
        for nl in nlines[:1]:
            nw,_=ts(draw,nl,pf(8))
            draw.text((20,ny),nl,font=pf(8),fill='#555555'); ny+=12
    # Blood volume note at bottom
    draw.rectangle([5,H-55,W-5,H-5],fill='#f0fafb',outline='#1a8a94',width=1)
    note='NORMAL BLOOD VOLUME: Adult = 70ml per kg body weight. 70kg person = 4900ml (~5 litres). Child = 80ml/kg. Infant = 90ml/kg.'
    nlines=wt(draw,note,pf(10),W-30)
    ny=H-48
    for nl in nlines:
        draw.text((15,ny),nl,font=pf(10),fill='#0d5c63'); ny+=14
    img=img.crop((0,0,W,H)); return img

# =============================================================================
# PIL DIAGRAM 2 — Primary Survey ABCDE + Haemorrhage Control
# =============================================================================
def make_abcde_diagram():
    W=900
    steps=[
        ('A','AIRWAY','Open and maintain the airway.',
         'Chin lift / jaw thrust. Suction if blood/vomit. Oropharyngeal airway (OPA). Intubate if GCS < 8.',
         '#0d5c63','#d4edda'),
        ('B','BREATHING','Ensure adequate ventilation.',
         'Look: chest rise symmetrical? Feel: trachea central? Listen: breath sounds equal? '
         'Treat tension pneumothorax IMMEDIATELY (needle thoracostomy 2nd intercostal space).',
         '#1a8a94','#e0f4f5'),
        ('C','CIRCULATION\n(STOP THE BLEEDING)',
         'Identify and control haemorrhage. This is where most trauma deaths occur.',
         'Direct pressure on external wounds. Tourniquet for limb bleeding. '
         'IV access (2 large-bore cannulas). Bloods: FBC, U&E, coagulation, crossmatch. '
         'Fluid resuscitation. Activate massive transfusion protocol if Class III/IV.',
         '#c0392b','#fde8e8'),
        ('D','DISABILITY\n(NEUROLOGICAL)',
         'Assess the level of consciousness (how awake the patient is).',
         'AVPU: Alert / Voice / Pain / Unresponsive. GCS (Glasgow Coma Scale: eyes 4, verbal 5, motor 6 = total 15). '
         'Pupils: equal and reactive? Blood glucose (exclude hypoglycaemia as a cause of altered consciousness).',
         '#7d3c98','#f5eef8'),
        ('E','EXPOSURE\n(EXAMINE FULLY)',
         'Undress the patient completely to find ALL injuries.',
         'Log roll (turn patient as a unit, maintaining spinal alignment) to examine the back. '
         'Prevent hypothermia (low body temperature): cover with blanket after exposure. '
         'Temperature check. Rectal examination if pelvic injury.',
         '#2471a3','#e8f4fd'),
    ]
    row_h=105; H=len(steps)*row_h+100
    img=Image.new('RGB',(W,H),'#f8fffe'); draw=ImageDraw.Draw(img)
    draw.rectangle([0,0,W,45],fill='#c0392b')
    t='PRIMARY SURVEY — ABCDE APPROACH TO TRAUMA &amp; HAEMORRHAGE'
    tw,_=ts(draw,t,pfb(14)); draw.text(((W-tw)//2,13),t,font=pfb(14),fill='#ffffff')
    for i,(letter,title,goal,action,col,bg) in enumerate(steps):
        y=50+i*row_h
        draw.rectangle([10,y,W-10,y+row_h-5],fill=bg,outline=col,width=2)
        # Letter badge
        draw.ellipse([18,y+10,70,y+62],fill=col)
        lw,lh=ts(draw,letter,pfb(22)); draw.text((44-lw//2,y+36-lh//2),letter,font=pfb(22),fill='#ffffff')
        # Title
        for j,tl in enumerate(title.split('\n')):
            tw2,_=ts(draw,tl,pfb(13)); draw.text((85,y+8+j*18),tl,font=pfb(13),fill=col)
        # Goal
        glines=wt(draw,goal,pfb(10),W-200)
        gy=y+8
        for gl in glines:
            draw.text((W-180,gy),gl,font=pfb(10),fill=col); gy+=13
        # Action lines
        alines=wt(draw,action,pf(9),W-110)
        ay=y+46
        for al in alines:
            draw.text((85,ay),al,font=pf(9),fill='#333333'); ay+=13
        if i<len(steps)-1:
            arr_d(draw,50,y+row_h-5,y+row_h+2,col=col,w=3,hs=8)
    # Bottom box
    y=H-48
    draw.rectangle([10,y,W-10,H-5],fill='#fff3cd',outline='#e6a817',width=2)
    note='REMEMBER: C = Stop the Bleeding comes THIRD — but in major trauma, haemorrhage is the #1 preventable cause of death. Think C-ABC in massive haemorrhage.'
    nlines=wt(draw,note,pfb(10),W-30)
    ny=y+8
    for nl in nlines:
        draw.text((20,ny),nl,font=pfb(10),fill='#7b3f00'); ny+=14
    img=img.crop((0,0,W,H)); return img

# =============================================================================
# PIL DIAGRAM 3 — Coagulation Cascade (simplified)
# =============================================================================
def make_coag_diagram():
    W,H=900,620
    img=Image.new('RGB',(W,H),'#ffffff'); draw=ImageDraw.Draw(img)
    draw.rectangle([0,0,W,42],fill='#0d5c63')
    t='HAEMOSTASIS — HOW THE BODY STOPS BLEEDING (Simplified)'
    tw,_=ts(draw,t,pfb(14)); draw.text(((W-tw)//2,11),t,font=pfb(14),fill='#ffffff')

    # Three columns: Primary, Secondary (coagulation), Fibrinolysis
    cols=[
        (150,'PRIMARY HAEMOSTASIS\n(First 1-3 minutes)','#c0392b',
         [('VESSEL INJURY','Blood vessel wall torn','#c0392b','#fde8e8'),
          ('VASOCONSTRICTION','Vessel squeezes shut\n(reduces blood flow)','#c0392b','#fde8e8'),
          ('PLATELET PLUG','Platelets (tiny blood cells)\nstick to the damaged wall\nand clump together\n= temporary plug','#c0392b','#fde8e8')]),
        (450,'SECONDARY HAEMOSTASIS\n(Coagulation Cascade)','#1a8a94',
         [('EXTRINSIC PATHWAY','Tissue Factor released\nfrom damaged cells\n-> activates Factor VII','#1a8a94','#e0f4f5'),
          ('COMMON PATHWAY','Factor X activated\n-> Prothrombin -> THROMBIN\n(the key enzyme)','#0d5c63','#d4edda'),
          ('FIBRIN CLOT FORMED','Thrombin converts\nFibrinogen -> FIBRIN\nFibrin strands weave through\nthe platelet plug\n= STABLE CLOT','#0d5c63','#d4edda')]),
        (750,'FIBRINOLYSIS\n(Clot Dissolution)','#7d3c98',
         [('PLASMINOGEN','Converted to PLASMIN\nby tPA\n(tissue plasminogen activator)','#7d3c98','#f5eef8'),
          ('PLASMIN','Breaks down FIBRIN\ninto fibrin degradation\nproducts (D-dimers)\n= clot dissolves\nonce healing complete','#7d3c98','#f5eef8'),
          ('TXA ACTS HERE','Tranexamic acid blocks\nplasminogen -> plasmin\n= preserves the clot\n= STOPS BLEEDING','#28a745','#d4edda')]),
    ]
    for cx,header,col,items in cols:
        # Header
        hw,hh=ts(draw,header.split('\n')[0],pfb(11))
        draw.text((cx-hw//2,48),header.split('\n')[0],font=pfb(11),fill=col)
        if '\n' in header:
            h2=header.split('\n')[1]; hw2,_=ts(draw,h2,pf(9))
            draw.text((cx-hw2//2,64),h2,font=pf(9),fill=col)
        y=90
        for title,sub,bcol,bg in items:
            y=draw_box(draw,cx,y,
                [(title,pfb(11),bcol),(sub,pf(9),'#333333')],
                bcol,bg,acc=True,mw=220,px=12,py=8,lg=4)+15
            if items.index((title,sub,bcol,bg))<len(items)-1:
                arr_d(draw,cx,y-12,y-2,col=bcol,w=2,hs=7)

    # Key at bottom
    draw.rectangle([10,H-75,W-10,H-5],fill='#fff3cd',outline='#e6a817',width=2)
    keys=[
        'DRUGS AFFECTING COAGULATION:',
        'Warfarin: blocks Vitamin K-dependent factors (II, VII, IX, X). Reversal: Vitamin K + FFP.',
        'DOACs (e.g. rivaroxaban, apixaban): block Factor Xa directly. Reversal: Andexanet alfa.',
        'Heparin/LMWH: boosts antithrombin III to block thrombin + Xa. Reversal: Protamine sulphate.',
        'TXA (Tranexamic Acid): blocks fibrinolysis. CRASH-2 trial: saves lives in trauma bleeding.',
    ]
    ky=H-72
    for k in keys:
        fn=pfb(9) if k.endswith(':') else pf(9)
        draw.text((20,ky),k,font=fn,fill='#7b3f00'); ky+=13
    img=img.crop((0,0,W,H)); return img

# =============================================================================
# PIL DIAGRAM 4 — Blood Loss by Fracture Site
# =============================================================================
def make_fracture_blood_loss():
    W,H=900,360
    img=Image.new('RGB',(W,H),'#ffffff'); draw=ImageDraw.Draw(img)
    draw.rectangle([0,0,W,42],fill='#0d5c63')
    t='ESTIMATED BLOOD LOSS BY FRACTURE SITE'
    tw,_=ts(draw,t,pfb(15)); draw.text(((W-tw)//2,12),t,font=pfb(15),fill='#ffffff')

    fractures=[
        ('Pelvis','1500-3000 ml','Up to 60% blood volume','#c0392b'),
        ('Femur (thigh)','1000-2000 ml','20-40% blood volume','#d4640a'),
        ('Tibia (shin)','500-1000 ml','10-20% blood volume','#e6a817'),
        ('Humerus (upper arm)','500-1000 ml','10-20% blood volume','#1a8a94'),
        ('Radius/Ulna (forearm)','250-500 ml','5-10% blood volume','#2471a3'),
        ('Rib (each)','100-200 ml','per rib','#7d3c98'),
        ('Spine','500-1500 ml','variable','#28a745'),
    ]
    bar_max=W-150; max_ml=3000
    y=55
    for bone,ml_text,pct,col in fractures:
        # Bar proportional to max
        try: ml_val=int(ml_text.split('-')[1].replace(' ml','').replace('>',''))
        except: ml_val=1000
        bar_w=int((ml_val/max_ml)*bar_max*0.85)
        draw.rectangle([140,y,140+bar_w,y+28],fill=col,outline=col)
        bw,_=ts(draw,bone,pfb(10)); draw.text((5,y+7),bone,font=pfb(10),fill='#1a1a2e')
        draw.text((145+bar_w+5,y+7),ml_text,font=pfb(10),fill=col)
        pw,_=ts(draw,pct,pf(9))
        draw.text((145+bar_w+5+ts(draw,ml_text,pfb(10))[0]+8,y+9),pct,font=pf(9),fill='#555555')
        y+=38

    draw.rectangle([10,H-48,W-10,H-5],fill='#fde8e8',outline='#c0392b',width=2)
    note=('WARNING: These are CLOSED fracture estimates. Open fractures (bone through skin) lose '
          'significantly MORE. Pelvic fractures can exsanguinate (drain all blood) without visible external bleeding.')
    nlines=wt(draw,note,pfb(9),W-30)
    ny=H-44
    for nl in nlines:
        draw.text((18,ny),nl,font=pfb(9),fill='#7b0000'); ny+=13
    img=img.crop((0,0,W,H)); return img

# =============================================================================
# BUILD STORY
# =============================================================================
story=[]

# TITLE
story.append(Spacer(1,8))
story.append(Paragraph('BLEEDING — TRAUMA &amp; NON-TRAUMA', sTitle))
story.append(Paragraph(
    'Complete Guide to Recognition, Assessment, Classification &amp; Management of All Types of Bleeding',sSub))
story.append(Paragraph(
    'External wounds • Intracranial • Chest • Abdomen • Pelvis • Fractures '
    '• GI Bleeding • Obstetric • Haematological • Prehospital to ICU',sSub))
divider(story)

# §1 OVERVIEW
sec_header('1. OVERVIEW — Why Bleeding Kills and How We Stop It', story)
professor_says(
    'Bleeding — or haemorrhage (from the Greek haima = blood, rhegnynai = to burst) — is the '
    'commonest preventable cause of death in trauma worldwide. '
    'Think of the body as a sealed container of 5 litres of fluid under pressure. '
    'Cut a hole in it and the pressure escapes. The heart speeds up to compensate. '
    'The blood vessels squeeze down to maintain pressure. But if you keep losing fluid '
    'faster than you replace it, eventually the engine stops. '
    'Thirty percent of all trauma deaths are caused by haemorrhage — and most of them '
    'are preventable if you recognise the signs early and act fast. '
    'This note covers every type of bleeding you will encounter, from a nosebleed to '
    'a ruptured aorta, using the same logical framework each time.', story)

info_box(
    '<b>HAEMORRHAGE</b> (HAM-oh-rij) = abnormal, uncontrolled bleeding from a damaged blood vessel. '
    'Can be EXTERNAL (visible blood coming out of the body) or INTERNAL (blood pooling '
    'inside the body — hidden, which makes it more dangerous because it is easy to miss). '
    'The body has 5 litres of blood in total (70ml per kg body weight). '
    'Losing 30% (about 1.5 litres) starts to cause shock. '
    'Losing 40% (2 litres) is immediately life-threatening.', story)

kf_data=[
    ['Key Number','What It Means','Clinical Relevance'],
    ['5 litres','Average adult blood volume (70ml/kg body weight)','Reference for all calculations. 70kg person = 4,900ml blood.'],
    ['750 ml (15%)','Class I haemorrhage — body compensates, no shock','Like donating blood. Heart rate may be slightly elevated.'],
    ['1500 ml (30%)','Class II — blood pressure falls, heart races','Needs IV fluids immediately. Surgery may be needed.'],
    ['2000 ml (40%)','Class III/IV — life-threatening shock','Massive transfusion protocol. Immediate surgery.'],
    ['30%','Trauma deaths caused by preventable haemorrhage','More lives saved by faster bleeding control than any other intervention.'],
    ['10 minutes','Time for a femoral artery injury to cause death without tourniquet','The artery in the thigh (femoral) pumps out 500ml per minute if cut.'],
    ['3 hours','Window for tranexamic acid (TXA) to save lives after trauma','CRASH-2 trial: TXA given within 3 hours = 1.5% reduction in mortality.'],
    ['1:1:1','Ratio of red blood cells : fresh frozen plasma : platelets in massive haemorrhage','Replaces all components of blood lost, not just red cells.'],
]
story.append(plain_table(kf_data,[CW*0.22,CW*0.38,CW*0.40]))
divider(story)

# §2 ANATOMY & PHYSIOLOGY
sec_header('2. ANATOMY &amp; PHYSIOLOGY — What Blood Is and How the Body Stops Bleeding', story)
professor_says(
    'Before we can understand bleeding, you need to know what blood actually is. '
    'Blood is not just a red liquid. It is a transport system, an immune army, a repair kit, '
    'and a communication network — all in one. And it has its own built-in repair mechanism: '
    'haemostasis (from the Greek haima = blood, stasis = stopping). '
    'Haemostasis is the process by which your body seals a cut within minutes. '
    'Understanding haemostasis tells you why clotting drugs work, '
    'why anticoagulants (blood-thinning medicines) cause dangerous bleeding, '
    'and what DIC (disseminated intravascular coagulation — a catastrophic failure of '
    'the clotting system) actually is.', story)

story.append(Paragraph('A. What Blood Is Made Of', sH2))
blood_comp=[
    ['Component','What It Is (Plain English)','Normal Level','Function','Why It Matters in Bleeding'],
    ['Red blood cells\n(Erythrocytes — RBC)',
     'Disc-shaped cells filled with haemoglobin (HEE-mo-glo-bin) — a protein that carries oxygen. They are what makes blood red.',
     'Male: 4.5-6.5 x10^12/L\nFemale: 3.8-5.8 x10^12/L\nHaemoglobin: M 130-170 g/L, F 120-160 g/L',
     'Carry oxygen from the lungs to every cell in the body, and carry carbon dioxide (waste gas) back to the lungs.',
     'When you bleed, you lose red cells = less oxygen delivered to organs = organs start to fail. This is what kills in haemorrhagic shock.'],
    ['Platelets\n(Thrombocytes)',
     'Tiny cell fragments (not full cells) that circulate in the blood. When a vessel is damaged, platelets are the first responders — they rush to the site and clump together to form a plug.',
     '150-400 x10^9/L',
     'Form the primary platelet plug (the first seal over a wound). Activate the clotting cascade. Release chemicals that attract more platelets.',
     'Thrombocytopenia (throm-bo-sigh-toe-PEE-nee-ah) = too few platelets = cannot form a platelet plug = easy bruising and bleeding. Platelet count <50 x10^9/L = spontaneous bleeding risk.'],
    ['Plasma',
     'The straw-coloured liquid part of blood (55% of total blood volume). Contains water, proteins, glucose, hormones, clotting factors, and antibodies.',
     '55% of blood volume',
     'Transports all dissolved substances. Contains all the clotting factors (proteins numbered I-XIII that form the coagulation cascade).',
     'In massive bleeding, plasma is lost along with red cells. Replacing only red cells (without plasma) = dilutional coagulopathy (the remaining clotting factors become too diluted to work).'],
    ['Clotting factors\n(Coagulation factors I-XIII)',
     'Proteins floating in the plasma. They are enzymes (biological catalysts — substances that speed up chemical reactions) arranged in a cascade (a sequence where each step activates the next, like dominoes falling).',
     'Various — checked by PT/INR (prothrombin time) and APTT (activated partial thromboplastin time)',
     'When activated by vessel injury, they create thrombin (the key enzyme) which converts fibrinogen to fibrin — the mesh that holds the clot together.',
     'Warfarin blocks Factors II, VII, IX, X. Liver disease reduces all clotting factor production. DIC consumes all factors at once.'],
    ['White blood cells\n(Leucocytes)',
     'The immune cells — neutrophils (fight bacteria), lymphocytes (make antibodies), monocytes (clean up debris). They are not directly involved in clotting but become crucial in wound healing.',
     '4-11 x10^9/L (total)\nNeutrophils 2-7.5 x10^9/L',
     'Fight infection. Clear debris from wounds. Orchestrate the inflammatory response that leads to tissue repair.',
     'Not the primary issue in acute bleeding, but infected wounds bleed more and heal poorly.'],
]
story.append(plain_table(blood_comp,[CW*0.15,CW*0.22,CW*0.17,CW*0.22,CW*0.24]))
story.append(Spacer(1,5))

story.append(Paragraph('B. Haemostasis — How the Body Stops Bleeding (Three Steps)', sH2))
professor_says(
    'Imagine a pipe in a wall bursts. The repair team has three phases: '
    '(1) Someone puts their thumb over the hole immediately (primary haemostasis = platelet plug). '
    '(2) While the thumb is there, a permanent repair crew arrives and lays down cement (secondary haemostasis = fibrin clot). '
    '(3) Once the pipe is permanently repaired, the cement dissolves slowly (fibrinolysis = clot breakdown). '
    'This is exactly what happens in your blood vessels within minutes of an injury.', story)

haem_data=[
    ['Phase','Time','What Happens','Key Players','Medical Significance'],
    ['PRIMARY HAEMOSTASIS\n(Platelet plug)',
     '1-3 minutes',
     'Damaged vessel wall exposes collagen (a structural protein — the scaffolding of tissues). '
     'Platelets immediately stick to collagen (via von Willebrand factor — vWF, a sticky protein that acts as glue). '
     'Platelets activate and release chemical signals (ADP, thromboxane A2) that recruit more platelets. '
     'A soft, temporary platelet plug forms.',
     'Platelets. von Willebrand factor (vWF). Collagen. ADP. Thromboxane A2.',
     'von Willebrand disease (vWD) = deficiency of vWF = platelets cannot stick = prolonged bleeding time = heavy periods, nosebleeds. '
     'Aspirin + clopidogrel block platelet activation (antiplatelet drugs).'],
    ['SECONDARY HAEMOSTASIS\n(Coagulation cascade)',
     '3-10 minutes',
     'The coagulation cascade is activated — a series of clotting factors (numbered proteins) activate each other in sequence, '
     'like dominoes. The cascade produces THROMBIN (a key enzyme = a protein that speeds up a reaction). '
     'Thrombin converts fibrinogen (a soluble protein dissolved in plasma) into FIBRIN '
     '(insoluble strands of protein). Fibrin strands weave through the platelet plug like a net, '
     'creating a hard, stable clot.',
     'Clotting factors I-XIII. Thrombin. Fibrinogen. Fibrin. Calcium (essential cofactor for the cascade). Vitamin K (needed to make Factors II, VII, IX, X).',
     'Haemophilia A = Factor VIII deficiency. Haemophilia B = Factor IX deficiency. '
     'Warfarin blocks Vitamin K = blocks Factors II, VII, IX, X. '
     'PT/INR checks the extrinsic pathway (Factors VII, X, V, II, fibrinogen). '
     'APTT checks the intrinsic pathway (VIII, IX, XI, XII, X, V, II, fibrinogen).'],
    ['FIBRINOLYSIS\n(Clot dissolution)',
     'Days to weeks',
     'Once the wound has healed, the clot is no longer needed. Plasminogen (a protein in the blood) is converted to PLASMIN '
     '(an enzyme) by tPA (tissue plasminogen activator — produced by the blood vessel wall). '
     'Plasmin breaks fibrin down into fragments called D-dimers. The clot dissolves and blood flow is restored.',
     'Plasminogen. tPA (tissue plasminogen activator). Plasmin. D-dimers.',
     'D-dimer blood test: if fibrin is being broken down somewhere in the body = D-dimers are raised = suspect DVT/PE. '
     'Tranexamic acid (TXA) BLOCKS plasminogen from converting to plasmin = preserves the clot = used to STOP bleeding.'],
]
story.append(plain_table(haem_data,[CW*0.16,CW*0.09,CW*0.28,CW*0.20,CW*0.27]))
story.append(Spacer(1,5))

diag3=make_coag_diagram()
story.append(i2r(diag3,CW))
story.append(Paragraph(
    'Diagram 1: Simplified haemostasis pathway — primary (platelet plug), secondary (coagulation cascade → fibrin clot), '
    'fibrinolysis (clot dissolution). TXA acts on the fibrinolysis step.',
    ParagraphStyle('Cp',fontName='DV-I',fontSize=8,leading=11,
        textColor=HexColor('#555555'),alignment=1)))
story.append(Spacer(1,4))
memory_hook(
    'Haemostasis = THREE steps: (1) Platelet plug (minutes), (2) Fibrin clot (minutes-hours), '
    '(3) Fibrinolysis = dissolve the clot (days). '
    'TXA blocks step 3 to preserve the clot. Warfarin blocks step 2 (Vitamin K factors).', story)
divider(story)

# §3 ATLS CLASSIFICATION
sec_header('3. CLASSIFICATION OF HAEMORRHAGE — How Much Blood Has Been Lost?', story)
professor_says(
    'The ATLS system (Advanced Trauma Life Support — the international gold standard for managing '
    'trauma, taught worldwide) divides haemorrhage into four classes based on how much blood '
    'has been lost and how the body is responding. Think of it as a traffic light system that '
    'gets progressively worse: Green (Class I) → Yellow (Class II) → Amber (Class III) → Red (Class IV). '
    'The most important skill is recognising which class a patient is in '
    'from their vital signs alone — even before you know exactly where they are bleeding.', story)

diag1=make_atls_diagram()
story.append(i2r(diag1,CW))
story.append(Paragraph(
    'Diagram 2: ATLS classification of haemorrhagic shock — Classes I-IV with blood loss volumes, '
    'vital signs, and mental status.',
    ParagraphStyle('Cp2',fontName='DV-I',fontSize=8,leading=11,
        textColor=HexColor('#555555'),alignment=1)))
story.append(Spacer(1,5))

story.append(Paragraph('Understanding Shock — What Happens to the Body When It Loses Blood', sH2))
shock_data=[
    ['Stage of Shock','What Is Happening','Vital Signs Change','What the Patient Looks Like'],
    ['COMPENSATED SHOCK\n(Class I-II)',
     'The body\'s emergency systems kick in automatically. The heart beats faster (tachycardia — fast heart, tachy = fast, cardia = heart) to pump the remaining blood around more quickly. Blood vessels squeeze down (vasoconstriction = blood vessels narrow = increases resistance = maintains blood pressure). Blood is redirected away from non-essential areas (skin, gut, kidneys) toward the brain and heart.',
     'Heart rate rises (first sign!). Blood pressure may still be NORMAL. Pulse pressure (the difference between the top and bottom blood pressure numbers) narrows. Respiratory rate rises (breathing faster). Skin becomes pale and cold (blood redirected away from skin).',
     'The patient looks pale, feels cold and clammy (cold + sweaty). Anxious. Thirsty. Pupils slightly dilated. "They don\'t look right" — trust this instinct. Blood pressure can be NORMAL in Class II — do NOT use a normal blood pressure to reassure yourself that everything is fine.'],
    ['DECOMPENSATED SHOCK\n(Class III-IV)',
     'The body can no longer compensate. Blood pressure falls (hypotension = hypo meaning low, tension meaning pressure). Heart rate is very fast but the pulse feels weak and thready (thin, barely palpable) because there is not enough blood to push. Organs start to fail: kidneys produce no urine (oliguria = olig meaning scanty, uria meaning urine), the brain becomes confused then unconscious.',
     'Blood pressure FALLS (systolic < 90 mmHg). Heart rate > 120. Respiratory rate > 30. Urine output < 0.5ml/kg/hour. GCS (Glasgow Coma Scale — the tool we use to measure level of consciousness) drops.',
     'Confused, agitated, then drowsy. Skin is grey, mottled (patchy). Very cold to the touch. May vomit. Losing consciousness. This is a surgical emergency — immediate blood transfusion and surgical haemostasis are the only treatments.'],
]
story.append(plain_table(shock_data,[CW*0.18,CW*0.32,CW*0.24,CW*0.26]))
story.append(Spacer(1,4))

story.append(Paragraph('How to Calculate Blood Loss', sH2))
story.append(Paragraph(
    'Calculating blood loss is an estimate — not an exact science. '
    'Use ALL available information together: vital signs (the ATLS class), '
    'clinical appearance, mechanism of injury (how the injury happened), '
    'and direct measurement where possible.', sBody))
story.append(Spacer(1,3))

calc_data=[
    ['Method','How to Do It','What It Tells You','Limitation'],
    ['ATLS vital signs\n(most practical)',
     'Measure: heart rate, blood pressure, respiratory rate, capillary refill time (press toenail for 5 sec — normal refill <2 sec), urine output. Match to ATLS Class I-IV table.',
     'Gives the class of haemorrhage: I (<15%), II (15-30%), III (30-40%), IV (>40%). Most importantly: heart rate rises BEFORE blood pressure falls — the first clinical sign of significant blood loss.',
     'Vital signs can be normal (compensated shock) until 30% blood is lost. Elderly patients, athletes, and beta-blocker users may not show tachycardia even with significant blood loss.'],
    ['Injury-based estimation\n(fracture sites)',
     'Use the fracture blood loss chart: Pelvis = 1.5-3L, Femur = 1-2L, Tibia = 0.5-1L. Add these up if multiple fractures.',
     'Estimates internal blood loss that you cannot see. A man with a broken pelvis and two broken femurs may have lost 4-7 litres before he arrives at the hospital — before a single drop of visible external bleeding.',
     'Estimates only — actual loss may be higher (especially in open fractures or pelvic fractures with arterial involvement).'],
    ['Direct weighing of\nwound dressings',
     'Weigh blood-soaked dressings before and after use. 1ml blood = 1g. Weigh swabs, dressings, suction containers in the operating theatre.',
     'Accurate measurement of EXTERNAL and surgical blood loss. Standard practice in operating theatres.',
     'Measures blood already outside the body. Does NOT measure ongoing internal haemorrhage.'],
    ['Haemoglobin\n(blood test)',
     'FBC (full blood count): check haemoglobin level. Normal: male 130-170 g/L, female 120-160 g/L.',
     'Reflects blood loss AFTER haemodilution (the body draws fluid into the blood vessels to compensate, diluting the remaining blood).',
     'In ACUTE massive haemorrhage, the haemoglobin may be NORMAL for the first 30-60 minutes because the blood has not yet been diluted. Do not use haemoglobin alone to diagnose acute haemorrhage — it is most useful for monitoring ongoing or slower bleeding.'],
    ['FAST scan\n(Focused Assessment with Sonography in Trauma)',
     'An ultrasound scan (sound wave imaging) done at the bedside in the emergency department, taking 3-5 minutes. The doctor places the ultrasound probe on 4 points: right upper abdomen (looking for blood around the liver), left upper abdomen (looking for blood around the spleen), pelvis (looking for blood around the bladder), and the heart (looking for blood around the heart — pericardial effusion).',
     'Detects FREE FLUID (blood) in the abdomen and chest in 70-90% of cases. A POSITIVE FAST (fluid seen) in a haemodynamically unstable patient = immediate surgery (no time for CT). A NEGATIVE FAST does not rule out bleeding (up to 30% of significant injuries are missed).',
     'Operator-dependent (the skill of the person doing the scan matters). Cannot identify the exact source of bleeding. Misses retroperitoneal (behind the abdominal cavity) haemorrhage reliably.'],
]
story.append(plain_table(calc_data,[CW*0.17,CW*0.28,CW*0.28,CW*0.27]))
story.append(Spacer(1,5))

diag4=make_fracture_blood_loss()
story.append(i2r(diag4,CW))
story.append(Paragraph(
    'Diagram 3: Estimated blood loss by fracture site. Internal bleeding from fractures is invisible — '
    'a pelvic fracture alone can cause fatal haemorrhage with no external blood visible.',
    ParagraphStyle('Cp3',fontName='DV-I',fontSize=8,leading=11,
        textColor=HexColor('#555555'),alignment=1)))
story.append(Spacer(1,4))
memory_hook(
    'Blood loss landmarks: 750ml (15%) = donate blood level. 1500ml (30%) = BP starts to fall. '
    '2000ml (40%) = immediately life-threatening. '
    'First sign of significant blood loss = TACHYCARDIA (fast heart rate) — NOT low blood pressure. '
    'By the time BP falls, you have already lost 30% of blood volume.', story)
divider(story)

# §4 RECOGNITION & ABCDE
sec_header('4. RECOGNITION &amp; INITIAL ASSESSMENT — The ABCDE Approach', story)
professor_says(
    'In any bleeding patient — whether from trauma or not — use the ABCDE framework every time. '
    'In the same order. Without skipping steps. '
    'Why? Because if you go straight to the wound and ignore the airway, '
    'you might perfectly close the wound of a person who is dying from a blocked airway '
    'that takes 10 seconds to fix. The ABCDE approach prevents you from treating the dramatic '
    'finding while missing the lethal one. '
    '"C — Stop the Bleeding" is the third step, but in massive haemorrhage, '
    'you must start haemorrhage control simultaneously with A and B.', story)

diag2=make_abcde_diagram()
story.append(i2r(diag2,CW))
story.append(Paragraph(
    'Diagram 4: ABCDE primary survey for trauma and haemorrhage — each step with the exact actions required.',
    ParagraphStyle('Cp4',fontName='DV-I',fontSize=8,leading=11,
        textColor=HexColor('#555555'),alignment=1)))
story.append(Spacer(1,5))

story.append(Paragraph('Vital Signs: What to Measure, Normal Values, and What Abnormal Means', sH2))
vitals_data=[
    ['Vital Sign','How to Measure','Normal Adult Value','In Haemorrhagic Shock','Clinical Pearl'],
    ['Heart rate (HR)\n= pulse',
     'Feel the radial pulse (at the wrist, thumb side) or brachial pulse (inside the elbow). Count for 30 seconds and double it. In an emergency, feel the carotid pulse (side of neck) if radial is absent.',
     '60-100 beats per minute (bpm)',
     'Class II onwards: > 100 bpm (tachycardia). Class IV: > 140 bpm or thready/absent (barely palpable).',
     'First vital sign to change in haemorrhage. Rises BEFORE blood pressure falls. An elderly patient on beta-blockers (heart rate-slowing drugs) may NOT develop tachycardia even with major blood loss — be extra cautious.'],
    ['Blood pressure (BP)',
     'Sphygmomanometer (BP cuff) on the upper arm. Inflate until the pulse disappears, then slowly release. The pressure at which the pulse returns = systolic (top number). Diastolic (bottom number) from when the sound disappears.',
     'Systolic 90-140 mmHg. Diastolic 60-90 mmHg. MAP (mean arterial pressure) 65-100 mmHg.',
     'Falls in Class III/IV. Systolic < 90 mmHg = hypotension = CLASS III at minimum. In young fit people, blood pressure may be maintained until 30-40% of blood is lost.',
     'Pulse pressure (systolic - diastolic) narrows early: if systolic 110 and diastolic 90 = pulse pressure only 20 mmHg (normal 40mmHg) = significant vasoconstriction = early haemorrhagic shock even with a "normal" systolic.'],
    ['Respiratory rate (RR)',
     'Count chest rises in 60 seconds while appearing to take the pulse (patients breathe faster if they know you are watching). Look at the chest moving.',
     '12-20 breaths per minute',
     'Rises with shock: Class II >20, Class III >30, Class IV >35. Also rises with pain, pneumothorax (collapsed lung), haemothorax (blood in the chest).',
     'Often overlooked but one of the most sensitive early signs of deterioration. A respiratory rate of 25-30 = patient is working hard to compensate. Document and reassess frequently.'],
    ['SpO2\n(oxygen saturation)',
     'Pulse oximeter — a clip on the finger. Measures the % of haemoglobin carrying oxygen (normal = 94-100%). Requires a pulsatile signal.',
     '94-100% on room air',
     'May be falsely normal in early haemorrhage (the remaining red cells are fully saturated). Falls when there is significant lung injury (haemothorax, pneumothorax, pulmonary contusion).',
     'May be unreliable in poor perfusion states (cold peripheries, vasoconstriction) — the probe cannot detect a signal. Try the earlobe or forehead probe instead.'],
    ['Urine output (UO)',
     'Urinary catheter (a thin tube inserted into the bladder through the urethra) connected to a urine bag. Measure ml/hour.',
     '0.5-1 ml/kg/hour (for a 70kg person = 35-70ml/hour)',
     '< 0.5ml/kg/hour = oliguria = kidneys not being perfused adequately = Class III/IV shock.',
     'Urine output is the most sensitive indicator of end-organ perfusion. Falling urine output is often the first sign that fluid resuscitation is inadequate. Insert catheter early in any significant trauma or bleeding.'],
    ['GCS\n(Glasgow Coma Scale)',
     'Score out of 15: Eyes (1-4: 4=opens spontaneously), Voice (1-5: 5=oriented and talking normally), Motor (1-6: 6=obeys commands). Add all three = GCS score.',
     'GCS 15 = fully alert and oriented',
     'GCS 13-15 = mild impairment (Class II-III). GCS 9-12 = moderate (Class III). GCS 8 or below = severe = intubate immediately (airway at risk).',
     'Rule of thumb: GCS < 8 = intubate (secure the airway with a breathing tube). Confusion in a trauma patient = treat as haemorrhagic shock until proven otherwise.'],
    ['Capillary refill time\n(CRT)',
     'Press a fingernail firmly for 5 seconds, then release. Count seconds until the pink colour returns.',
     '< 2 seconds',
     '> 2 seconds = reduced skin perfusion = vasoconstriction = compensation for blood loss.',
     'Quick, bedside test requiring no equipment. Less reliable in cold environments (vasoconstriction for temperature reasons).'],
]
story.append(plain_table(vitals_data,[CW*0.14,CW*0.20,CW*0.14,CW*0.24,CW*0.28]))
divider(story)

# ── SECTION 5: EXTERNAL BLEEDING ────────────────────────────────────────────
sec_header('Section 5: External Bleeding — Wounds, Lacerations & Fractures', story)
professor_says('Think of a cut like a dam breaking. Your job is to plug the dam FAST. The body has seconds to minutes before catastrophic loss. Every second you delay direct pressure, the lake empties a little more.', story)

story.append(Paragraph('External bleeding is the <b>most visible</b> and <b>most immediately treatable</b> form of haemorrhage (blood loss). '
               'Yet it kills thousands every year — mostly because bystanders and first responders hesitate instead of acting. '
               'The rule is simple: <b>STOP THE BLEEDING FIRST. Nothing else matters until the bleeding stops.</b>'))
story.append(Spacer(1,6))

ext_types = [
    ['Type', 'What it looks like', 'Source vessel', 'How dangerous?', 'First-line treatment'],
    ['Capillary bleeding\n(tiny blood vessels just under skin)',
     'Oozing, dark red blood. Slow and steady. Like a graze on the road.',
     'Capillaries — the smallest blood vessels, thinner than a hair.',
     'Rarely life-threatening. Stops on its own with simple pressure.',
     'Direct pressure × 5 min. Clean wound. Simple dressing.'],
    ['Venous bleeding\n(from a vein)',
     'Dark red, steady flow. Does NOT pulse. Constant stream like water from a tap.',
     'Veins carry deoxygenated (used) blood back to the heart. Dark colour due to low oxygen.',
     'Significant risk. Large veins (femoral, jugular) can cause Class III shock rapidly.',
     'Firm direct pressure × 10-15 min without lifting. Elevation of limb. Wound packing if deep.'],
    ['Arterial bleeding\n(from an artery)',
     'Bright red, SPURTING blood that pulses in time with the heartbeat. Dramatic. Cannot be missed.',
     'Arteries carry oxygenated (fresh) blood from the heart at high pressure. Bright red = high oxygen.',
     'IMMEDIATELY life-threatening. Femoral artery transection: unconscious in 3 minutes, dead in 5.',
     'TOURNIQUET for limb arteries. Direct pressure for trunk/neck. Wound packing. CALL HELP NOW.'],
]
story.append(plain_table(ext_types, [CW*0.15, CW*0.20, CW*0.20, CW*0.20, CW*0.25]))

story.append(Spacer(1,8))
story.append(Paragraph('<b>The STOP THE BLEED 3-step protocol (taught worldwide for civilian first responders):</b>'))
stop_bleed = [
    ['Step', 'Action', 'Plain English explanation', 'Common mistake'],
    ['1 — CALL',
     'Call emergency services (999 / 112 / 911)',
     'More help is coming. You are buying time, not solving everything.',
     'Forgetting to call because you are focused on the wound.'],
    ['2 — COMPRESS',
     'Apply firm direct pressure using both hands, a cloth, or gloved hands. Push HARD and do NOT let go.',
     'Imagine pressing down on a garden hose to stop the flow. The harder and longer you press, the more clot forms.',
     'Pressing lightly, or lifting every 30 seconds to check — this breaks the forming clot every time.'],
    ['3 — TOURNIQUET\n(if limb)',
     'If bleeding is from an arm or leg and direct pressure fails: apply tourniquet 5-8cm above the wound. Tighten until bleeding stops. Write time on patient\'s skin.',
     'A tourniquet (a tight band that compresses the whole limb, stopping blood flow entirely) is life-saving. Modern military evidence shows: used early, it saves lives. Temporary limb ischaemia (loss of blood supply) is acceptable to save a life.',
     'Applying too loosely — venous bleeding continues, arterial bleeding continues, and swelling worsens. Must be tight enough to stop ALL flow.'],
]
story.append(plain_table(stop_bleed, [CW*0.12, CW*0.22, CW*0.36, CW*0.30]))

story.append(Spacer(1,8))
story.append(Paragraph('<b>Wound packing technique</b> (for deep wounds, junctional wounds like groin/axilla where tourniquet cannot be placed):'))
packing_steps = [
    ['Step', 'Action'],
    ['1', 'Expose the wound fully — cut clothing away. Good lighting.'],
    ['2', 'If available: apply haemostatic (clot-promoting) gauze (e.g., Combat Gauze, QuikClot) deep into the wound cavity.'],
    ['3', 'Pack tightly — push gauze all the way to the bottom of the wound. Do not leave air pockets.'],
    ['4', 'Apply direct pressure from above with both hands for minimum 3 minutes continuously.'],
    ['5', 'DO NOT remove the packing — this breaks the forming clot. Leave in place until surgeon reviews.'],
    ['6', 'Bandage firmly over the packing. Reassess regularly for rebleeding.'],
]
story.append(plain_table(packing_steps, [CW*0.06, CW*0.94]))
divider(story)

story.append(Paragraph('<b>Fracture-associated blood loss — Hidden bleeding you cannot see</b>'))
story.append(Paragraph('When a bone breaks, blood vessels running through and around the bone tear. This blood leaks into surrounding muscle and soft tissue. '
               'You may see NO external bleeding at all — yet the patient is losing litres internally. '
               'Key rule: <b>never dismiss a fracture as "just a broken bone."</b>'))
story.append(Spacer(1,4))

frac_table = [
    ['Fracture site', 'Estimated blood loss', 'Clinical clue', 'Action'],
    ['Radius / Ulna (forearm bones)', '100–500 ml', 'Swelling of forearm', 'Splint, monitor vitals'],
    ['Humerus (upper arm bone)', '500–1000 ml', 'Arm swelling, tenderness', 'Splint, analgesia'],
    ['Tibia / Fibula (shin bones)', '500–1500 ml', 'Lower leg swelling, deformity', 'Splint, check distal pulses'],
    ['Femur (thigh bone — the longest, strongest bone in the body)', '1000–2000 ml', 'Thigh grossly swollen, may be shortened/rotated', 'Traction splint, IV access, fluids'],
    ['Pelvis (the bony ring supporting the spine and hip joints)', '1500–4000+ ml', 'Pelvic instability on gentle compression, haematuria (blood in urine), scrotal/labial bruising', 'Pelvic binder immediately, NO repeated springing of pelvis, activate MTP'],
    ['Multiple rib fractures', '100–200 ml per rib', 'Chest wall tenderness, paradoxical movement', 'Analgesia, monitor for haemothorax'],
]
story.append(plain_table(frac_table, [CW*0.22, CW*0.18, CW*0.30, CW*0.30]))
memory_hook('PELVIS KILLS QUIETLY: A pelvic fracture can hide 4 litres of blood in the retroperitoneum (the space behind the abdominal organs) — equal to losing your entire blood volume. No external bleeding, no obvious wound. Just shock. Always apply a pelvic binder early in any pelvic trauma.', story)
divider(story)

# ── SECTION 6: INTRACRANIAL BLEEDING ────────────────────────────────────────
sec_header('Section 6: Intracranial Bleeding — Inside the Skull', story)
professor_says('Picture the brain as a jelly inside a rigid box (the skull). You cannot expand a rigid box. So when blood leaks inside, the pressure rises and squeezes the very organ it surrounds. The race is against time — every millilitre of blood that accumulates is squeezing neurons (brain cells) to death.', story)

story.append(Paragraph('The skull (cranium) is a hard bony container. Inside, in order from outside to inside, are four layers:'))
story.append(Paragraph('1. <b>Skull bone</b> 2. <b>Epidural space</b> (potential space between skull and dura) '
               '3. <b>Dura mater</b> (tough outer membrane — Latin: "hard mother") '
               '4. <b>Subdural space</b> (between dura and arachnoid) '
               '5. <b>Arachnoid mater</b> (middle membrane) '
               '6. <b>Subarachnoid space</b> (filled with CSF — cerebrospinal fluid, the clear protective liquid) '
               '7. <b>Pia mater</b> (innermost thin membrane directly on brain surface) '
               '8. <b>Brain parenchyma</b> (the actual brain tissue).'))
story.append(Spacer(1,6))

icb_types = [
    ['Type', 'Where the blood goes', 'Typical cause', 'Classic clinical pattern', 'Urgent treatment'],
    ['Extradural / Epidural haematoma\n(EDH)',
     'Between skull bone and dura mater. An artery (the middle meningeal artery, running in a groove on the inside of the temporal bone) tears when the temporal bone fractures.',
     'Temporal bone fracture from a blow to the side of the head (e.g., cricket ball, assault).',
     'CLASSIC LUCID INTERVAL: patient is knocked out briefly, then wakes up and seems fine ("lucid" = awake and coherent). Then as blood accumulates over 2-6 hours, they deteriorate rapidly — headache, confusion, unconscious, fixed dilated pupil on the SAME side as injury (ipsilateral). WITHOUT surgery = death.',
     'EMERGENCY craniotomy (surgical opening of skull) to evacuate the blood clot. Call neurosurgery immediately. If GCS falling and pupil fixed: intubate, give mannitol (osmotic diuretic to reduce brain swelling), urgent CT head.'],
    ['Subdural haematoma\n(SDH — acute vs chronic)',
     'Between dura and arachnoid. Bridging veins (thin veins crossing from brain surface to dura) tear.',
     'ACUTE: High-energy trauma (road traffic accident, fall from height). CHRONIC: Minor or no trauma in elderly patients on anticoagulants (blood thinners). The brain shrinks with age, stretching bridging veins.',
     'ACUTE SDH: No lucid interval. Immediate deterioration. Much worse prognosis than EDH. CHRONIC SDH: Weeks after minor head injury, gradual confusion, headache, fluctuating consciousness. Often mistaken for dementia or stroke in elderly.',
     'ACUTE: Craniotomy if significant. CHRONIC: Burr holes (small holes drilled in skull) to drain blood. Both: reverse anticoagulation urgently. Admit to neurosurgical unit.'],
    ['Subarachnoid haemorrhage\n(SAH)',
     'Into the CSF space between arachnoid and pia. Spreads around the whole brain rapidly in the CSF.',
     'TRAUMATIC: Any significant head injury. SPONTANEOUS: Rupture of a berry aneurysm (a blueberry-shaped bulge on a brain artery that bursts) — NOT from trauma.',
     'THUNDERCLAP HEADACHE: The worst headache of my life, coming on in seconds. Like being struck by lightning in the head. Nausea, vomiting, neck stiffness (meningism), photophobia (light sensitivity), collapse. 30% die before reaching hospital.',
     'CT head (shows blood as bright white in subarachnoid space in 95% within first 6h). If CT negative but clinical suspicion high: lumbar puncture at 12h for xanthochromia (yellow colour of CSF = old blood breakdown products). Neurosurgical referral for aneurysm coiling or clipping.'],
    ['Intracerebral haemorrhage\n(ICH)',
     'Directly inside the brain tissue (parenchyma). Bleeding from small perforating arteries within the brain substance itself.',
     'HYPERTENSIVE ICH: Most common. Hypertension (high blood pressure) damages small vessels over years until they rupture. Common sites: basal ganglia, thalamus, pons, cerebellum. TRAUMATIC ICH: Direct brain contusion (bruising).',
     'Sudden focal neurological deficit: sudden arm/leg weakness, sudden speech difficulty, sudden face droop, sudden ataxia (unsteady walking) or vertigo if cerebellar. Often with headache, raised BP, vomiting. GCS may be reduced.',
     'Reverse anticoagulation URGENTLY. Control BP carefully (too low worsens ischaemia, too high worsens haemorrhage). Neurosurgical assessment. Cerebellar ICH >3cm = surgical evacuation. Supportive care: ITU level, glucose control, DVT prophylaxis after 48h.'],
]
story.append(plain_table(icb_types, [CW*0.14, CW*0.18, CW*0.16, CW*0.26, CW*0.26]))

story.append(Spacer(1,6))
story.append(Paragraph('<b>Cushing\'s triad — the brain\'s last SOS signal:</b> When intracranial pressure (ICP) is critically high, the brainstem is being compressed. The body makes one final attempt to push blood into the brain:'))
cushing = [
    ['Sign', 'What you see', 'Why it happens'],
    ['1. Hypertension (very high blood pressure)', 'Systolic BP > 180 mmHg, rising rapidly', 'Body raises BP to try to force blood past the high ICP into the brain'],
    ['2. Bradycardia (slow heart rate)', 'Pulse < 60 beats/min, getting slower', 'The baroreceptor (pressure sensor) response to extreme hypertension. Vagal reflex slows heart.'],
    ['3. Irregular breathing (Cheyne-Stokes pattern)', 'Breathing becomes irregular, deep, then apnoeic (stops), then starts again', 'Brainstem respiratory centre being compressed. Pre-terminal sign.'],
]
story.append(plain_table(cushing, [CW*0.28, CW*0.28, CW*0.44]))
alert_box('Cushing\'s Triad = HIGH BP + SLOW PULSE + IRREGULAR BREATHING = Brain about to herniate (brainstem pushed through skull base). CALL NEUROSURGERY NOW. Intubate, hyperventilate (target PaCO2 35mmHg to vasoconstrict cerebral vessels), give mannitol 0.25-1g/kg IV. This buys minutes, not hours.', story)
image_search_box('Intracranial bleeding types diagram', 'Google Images: extradural haematoma vs subdural CT scan biconvex vs crescent / subarachnoid haemorrhage CT bright white cisterns / intracerebral haemorrhage hypertensive basal ganglia', story)
divider(story)

# ── SECTION 7: THORACIC BLEEDING ────────────────────────────────────────────
sec_header('Section 7: Thoracic Bleeding — Blood in the Chest', story)
professor_says('The chest cavity (thorax) is like a sealed bag containing your lungs and heart. Blood filling that bag from a torn vessel is like a slow flood filling a room — eventually the lungs cannot expand because the room is full, and the heart cannot beat properly because it is being squeezed.', story)

thorax_types = [
    ['Condition', 'What is it?', 'Mechanism / Cause', 'Clinical signs', 'Treatment'],
    ['Haemothorax\n(blood in the pleural space)',
     'The pleural space (the small gap between the lung and the chest wall) fills with blood. The lung is compressed and cannot inflate.',
     'Torn intercostal vessels (the blood vessels running between ribs), lung laceration, aortic or subclavian artery injury, rib fractures.',
     'Decreased air entry on affected side (lung compressed, not ventilating). Dull on percussion (tapping the chest — blood is solid, gives dull note unlike hollow air-filled lung). Respiratory distress, tachycardia, hypotension if massive (>1500ml = massive haemothorax).',
     'Large-bore chest drain (intercostal tube thoracostomy) inserted in 5th intercostal space, mid-axillary line. If >1500ml drained immediately OR >200ml/hour ongoing → thoracotomy (surgical chest opening). Blood via drain can be autotransfused (collected and given back to patient).'],
    ['Tension pneumothorax\n(air under pressure — closely related emergency)',
     'Air (not blood) enters the chest but cannot escape. Pressure builds. The mediastinum (the central chest structures including heart, trachea, great vessels) shifts to the opposite side. Compresses the opposite lung and kinks the great veins.',
     'Rib fracture with one-way valve tear of lung. Also a complication of positive pressure ventilation (mechanical breathing support). Can occur after chest drain removal or penetrating chest wound.',
     'Absent breath sounds one side. Tracheal deviation AWAY from affected side (late sign). Distended neck veins (JVD — jugular venous distension) due to obstructed venous return. Hypotension. Cyanosis (blue lips). Near-cardiac arrest.',
     'DO NOT wait for X-ray. Immediate needle decompression: 2nd intercostal space, mid-clavicular line, with a 14G cannula. Then chest drain insertion. This is a clinical diagnosis — you decompress first, image second.'],
    ['Traumatic aortic injury\n(aorta = the largest artery)',
     'The aorta (the main pipeline from the heart carrying all oxygenated blood to the body) tears, partially or completely, usually at the aortic isthmus (just after the point where the left subclavian artery branches off) — the most common site of shear force.',
     'High-speed deceleration: road traffic accident, fall from >3m. The heart continues moving forward inside the chest while the aorta is tethered at the ligamentum arteriosum — the shear force tears the vessel.',
     '80% die at scene. Survivors: widened mediastinum on CXR (>8cm), left haemothorax, fractured 1st/2nd ribs, tracheal deviation to right, NG tube (nasogastric tube) deviation to right. CT angiography confirms. May present with upper limb hypertension vs lower limb hypotension.',
     'Permissive hypotension (target SBP 80-100mmHg) to reduce haemorrhagic force. Avoid aggressive fluids. URGENT cardiothoracic surgery (TEVAR — thoracic endovascular aortic repair — preferred over open surgery). Beta-blocker to reduce aortic wall stress.'],
    ['Pulmonary contusion\n(bruised lung)',
     'Direct trauma bruises the lung tissue. The alveoli (tiny air sacs where gas exchange happens) fill with blood and fluid — like bruised fruit, the tissue becomes oedematous (swollen with fluid) and cannot exchange oxygen.',
     'Blunt chest trauma — steering wheel, blast, fall. Often accompanies rib fractures or flail chest.',
     'Initially may be subtle. Progressive respiratory failure over 24-72 hours as oedema worsens. Hypoxia (low blood oxygen) disproportionate to apparent injury. Crackles on auscultation. CXR: patchy opacification (white fluffy shadows).',
     'Supplemental O2. Careful fluid balance (avoid overload as worsens oedema). Analgesia for rib fractures (inadequate pain relief → poor ventilation → pneumonia). May need NIV (non-invasive ventilation) or intubation/ITU.'],
    ['Cardiac tamponade\n(blood around the heart)',
     'Blood fills the pericardial sac (the fibrous bag surrounding the heart). The bag cannot stretch. Blood squeezes the heart chambers — they cannot fill properly, so they cannot pump. Cardiac output collapses.',
     'Penetrating trauma (stab wound, gunshot to chest). Also: aortic dissection rupturing into pericardium, myocardial infarction (very rarely), iatrogenic (during cardiac procedures).',
     'BECK\'S TRIAD: (1) Low blood pressure (2) Distended neck veins / raised JVP (3) Muffled heart sounds on auscultation. Also: pulsus paradoxus (blood pressure drops >10mmHg during inspiration). Kussmaul\'s sign (JVP rises on inspiration rather than falling). ECG: electrical alternans (QRS size alternates beat to beat).', 
     'EMERGENCY pericardiocentesis: insert a long needle below the xiphisternum (bottom of breastbone) angled towards the left shoulder, aspirate blood. Even 20ml removed can be life-saving. Definitive: surgical pericardiotomy or thoracotomy. In cardiac arrest from tamponade: resuscitative thoracotomy (emergency department chest opening).'],
]
story.append(plain_table(thorax_types, [CW*0.14, CW*0.17, CW*0.18, CW*0.24, CW*0.27]))
memory_hook('CARDIAC TAMPONADE = BECK\'S TRIAD: Low BP + High JVP + Quiet heart. Think "the heart is being HUSHED and STRANGLED." Quiet (muffled sounds) + Strangled (raised JVP) + Weak (low BP). Needle below the breastbone. NOW.', story)
divider(story)

# ── SECTION 8: ABDOMINAL & PELVIC BLEEDING ──────────────────────────────────
sec_header('Section 8: Abdominal & Pelvic Bleeding — The Silent Killers', story)
professor_says('The abdomen is like a large shopping bag. You can stuff litres of blood in there before the outside gives any obvious clue. A patient can look deceptively stable, then crash. Your index of suspicion must always be HIGH for abdominal injury in any trauma patient.', story)

story.append(Paragraph('<b>Key solid organs at risk</b> (solid organs bleed more than hollow organs):'))
abd_organs = [
    ['Organ', 'Location / Anatomy', 'Injury mechanism', 'Clinical clues', 'Investigation & Management'],
    ['Spleen\n(most commonly injured abdominal organ)',
     'Left upper quadrant (left side, under ribs). A soft, fragile, highly vascular organ the size of a fist. Holds a reservoir of blood and filters old red cells.',
     'LEFT lower rib fractures (ribs 9-11). Left flank blunt trauma. Seatbelt injury. Spontaneous rupture in infectious mononucleosis (glandular fever — the Epstein-Barr virus makes spleen enlarged and friable).',
     'LEFT upper quadrant pain. KEHR\'S SIGN: left shoulder tip pain — blood under the left diaphragm irritates the phrenic nerve (which also supplies the shoulder). Tenderness in the left flank. Hypovolaemic shock (blood pressure falling, pulse rising).',
     'FAST scan: free fluid (black crescents) around spleen. CT abdomen with IV contrast: gold standard. Grades I-V. Grades I-III: non-operative management (NOM) in haemodynamically stable patients. Grade IV-V or haemodynamic instability: angioembolisation (blocking the bleeding vessel via catheter) or splenectomy (removal of spleen — requires lifelong vaccination against encapsulated bacteria: pneumococcus, meningococcus, Haemophilus influenzae).'],
    ['Liver\n(largest solid organ in the body)',
     'Right upper quadrant (right side, under ribs). The liver receives blood from TWO sources: the hepatic artery (oxygenated blood) and the portal vein (nutrient-rich blood from gut). Extremely vascular.',
     'RIGHT lower rib fractures (ribs 7-11). Seatbelt. Steering wheel. Right flank trauma. Penetrating injury.',
     'RIGHT upper quadrant pain. Referred pain to right shoulder (similar mechanism to Kehr\'s sign). Peritonism (rigid abdomen). Shock. May have visible bruising or seatbelt mark across right abdomen.',
     'FAST scan: fluid in Morison\'s pouch (the space between liver and right kidney — first place blood collects in right-sided abdominal injury). CT abdomen: grade and plan. Most liver injuries managed non-operatively. Major liver lacerations with bleeding: hepatic angioembolisation or damage control surgery (perihepatic packing — putting swabs around the liver to compress, then closing abdomen temporarily and returning 48h later to remove packs).'],
    ['Mesentery & Bowel',
     'The mesentery is the fan-shaped membrane that suspends the small intestine from the back of the abdominal wall. Contains all the blood vessels supplying the intestines.',
     'High-speed deceleration. Seatbelt (classic: horizontal band bruise across abdomen = "seatbelt sign"). Burst fractures of lumbar spine. Direct blows.',
     'Often initially subtle. Progressive abdominal pain and tenderness. Signs of peritonism develop over hours as bowel contents leak. Seatbelt sign highly predictive. Lumbar Chance fracture on X-ray (horizontal fracture through vertebral body from seatbelt).',
     'CT abdomen essential. Free air (pneumoperitoneum) under diaphragm on erect CXR = bowel perforation = immediate surgery. Mesenteric injury: may need bowel resection. DELAY in diagnosis of bowel injury significantly worsens mortality.'],
    ['Retroperitoneal haematoma\n(blood behind the abdominal cavity)',
     'The retroperitoneum is the space behind the peritoneal cavity (the main abdominal cavity). Contains the kidneys, ureters, aorta, inferior vena cava (IVC), pancreas, and major blood vessels.',
     'Pelvic fractures (Zone III — central pelvic haematoma). Renal injury (Zone I — perirenal). Major vessel injury.',
     'Often clinically silent until very large. Grey Turner\'s sign: flank bruising appearing 24-48h later. Cullen\'s sign: periumbilical (around the navel) bruising. Haematuria (blood in urine) from renal injury. Haemodynamic instability without obvious external source.',
     'CT abdomen/pelvis with IV contrast. Pelvic retroperitoneal haematoma: do NOT explore surgically (disrupts tamponade). Apply pelvic binder. Angioembolisation for arterial bleeding. REBOA (Resuscitative Endovascular Balloon Occlusion of the Aorta) in extremis.'],
    ['Pelvic fractures',
     'The pelvis (bony ring: ilium, ischium, pubic bones, sacrum) is a rigid ring — it usually fractures in two or more places. The internal iliac vessels (hypogastric artery and vein) and pelvic venous plexus (a network of veins) run along the inner pelvic walls.',
     'High-energy trauma: road accidents, falls from height, crush injuries. Open book (AP compression), lateral compression, vertical shear patterns.',
     'Gross pelvic instability (feel the pelvis gently — do this ONCE only; repeated springing of the pelvis disrupts haemostasis). Scrotal/labial bruising. Perineal lacerations. Urethral injury: blood at urethral meatus (opening), high-riding prostate on PR exam (do NOT insert urinary catheter without urology advice). Haematuria.',
     'Pelvic binder IMMEDIATELY (close the pelvic ring → reduce volume → tamponade venous bleeding). Activate massive transfusion protocol. CT pelvis with contrast. Angioembolisation for arterial bleeding (visible contrast extravasation on CT). Pelvic packing (preperitoneal) if angiography not available. Definitive fixation once haemodynamically stable.'],
]
story.append(plain_table(abd_organs, [CW*0.14, CW*0.18, CW*0.17, CW*0.23, CW*0.28]))
image_search_box('Abdominal bleeding FAST scan views', 'Google Images: FAST scan Morrison\'s pouch free fluid ultrasound / FAST scan free fluid splenorenal / pelvic binder application technique', story)
divider(story)

# ── SECTION 9: GASTROINTESTINAL BLEEDING ────────────────────────────────────
sec_header('Section 9: Gastrointestinal (GI) Bleeding — Upper and Lower', story)
professor_says('The gut is a 9-metre tube running from mouth to anus. Anything along that tube can bleed. The KEY divide is whether the bleeding is above or below the ligament of Treitz (a small muscular band where the small intestine joins the duodenum to the jejunum, at the level of L1/L2). Above = UPPER GI bleed. Below = LOWER GI bleed. This matters because causes, presentation, and management differ completely.', story)

story.append(Paragraph('<b>Upper GI Bleeding (UGIB)</b> — from oesophagus (food pipe), stomach, or first part of small intestine (duodenum):'))
ugib_table = [
    ['Cause', 'Mechanism', 'Typical presentation', 'Key investigation', 'Management'],
    ['Peptic ulcer disease\n(PUD) — most common UGIB cause (35-50%)',
     'H. pylori bacteria (lives in stomach, damages mucosal lining) or NSAIDs (ibuprofen, aspirin, diclofenac — reduce the protective prostaglandin layer) → ulcer erodes into a blood vessel.',
     'Haematemesis (vomiting blood — fresh red or coffee-ground appearance). Melaena (black, tarry, foul-smelling stools — digested blood = black pigment = haem). Epigastric pain. Syncope (fainting).',
     'OGD (oesophagogastroduodenoscopy = camera down the throat into the stomach, called "upper scope" or "gastroscopy"). Rockford-Forrest score classifies risk of rebleed.',
     'RESUSCITATE FIRST. IV access, bloods (FBC, U&E, coagulation, group & save/crossmatch), IV fluids cautiously. PPI (Proton Pump Inhibitor — omeprazole/pantoprazole 80mg IV bolus then infusion) reduces gastric acid. Endoscopic haemostasis (injection of adrenaline, clips, argon plasma coagulation). H. pylori eradication if confirmed. STOP NSAIDs.'],
    ['Oesophageal varices\n(varicose veins in the food pipe)',
     'Portal hypertension (raised blood pressure in the portal venous system, usually from liver cirrhosis) → blood backs up into oesophageal veins → they dilate and become tortuous (varicose) → rupture → catastrophic bleeding.',
     'Massive bright red haematemesis. Patient often known to have liver disease (cirrhosis, alcoholic liver disease, hepatitis B/C). May have signs of chronic liver disease: spider naevi, palmar erythema, jaundice, ascites, splenomegaly.',
     'OGD urgently. Also: TIPSS score (Transjugular Intrahepatic Porto-Systemic Shunt score to predict 6-week mortality).',
     'ABC resuscitation. Terlipressin 2mg IV immediately (vasoconstricts the portal circulation, reduces portal pressure and variceal bleeding — only drug proven to reduce mortality). Antibiotics: ciprofloxacin or ceftriaxone (reduces bacterial translocation and infection risk in cirrhosis). Urgent OGD for band ligation (rubber bands placed around varices to strangle them). Sengstaken-Blakemore tube if uncontrolled (a tube with two balloons inflated in the oesophagus/stomach as a bridge to more definitive treatment). TIPSS (radiological procedure creating a channel through the liver) for refractory cases.'],
    ['Mallory-Weiss tear',
     'Forceful vomiting or retching tears the mucosa (inner lining) at the gastro-oesophageal junction (where the food pipe meets the stomach).',
     'Haematemesis after prolonged vomiting episode. Often in alcoholics after a drinking binge. Usually small amount of fresh blood.',
     'OGD: linear tear at the GEJ.',
     'Usually self-limiting — stops spontaneously. PPI. If ongoing: endoscopic treatment.'],
    ['Gastric cancer',
     'Tumour erodes blood vessels.',
     'Insidious (slow) blood loss. Iron deficiency anaemia. Weight loss. Early satiety. Dysphagia (difficulty swallowing). Epigastric mass.',
     'OGD + biopsy. CT staging.',
     'Surgical/oncological referral. Endoscopic haemostasis for acute bleeding.'],
    ['Aorto-enteric fistula\n(rare but immediately fatal)',
     'After previous aortic surgery (e.g., aortic aneurysm repair with a graft), the graft erodes through the bowel wall, creating a communication between the aorta and the duodenum.',
     'HERALD BLEED: a small initial haematemesis/melaena, followed hours later by EXSANGUINATING haemorrhage. Often missed at initial presentation.',
     'Urgent CT angiography. Upper scope.',
     'EMERGENCY vascular surgery. This is a surgical emergency with near-100% mortality if not operated.'],
]
story.append(plain_table(ugib_table, [CW*0.16, CW*0.19, CW*0.19, CW*0.16, CW*0.30]))

story.append(Spacer(1,8))
story.append(Paragraph('<b>Glasgow-Blatchford Score (GBS)</b> — used in A&E to decide if patient needs urgent endoscopy or can be managed outpatient:'))
gbs_table = [
    ['Variable', 'Value', 'Score'],
    ['Blood Urea Nitrogen (BUN) — marker of blood digested in the gut (raised in UGIB)', '≥ 6.5 mmol/L', '+2 to +6 depending on level'],
    ['Haemoglobin (Hb) — blood concentration', 'Men: <130g/L; Women: <120g/L', '+1 to +6 depending on level'],
    ['Systolic BP', '100-109 mmHg = +1; 90-99 = +2; <90 = +3', '+1 to +3'],
    ['Heart rate ≥100 bpm', '', '+1'],
    ['Presentation with melaena (black stool)', '', '+1'],
    ['Presentation with syncope (fainting)', '', '+2'],
    ['Liver disease', '', '+2'],
    ['Heart failure', '', '+2'],
    ['SCORE = 0', 'LOW RISK — can consider outpatient management', ''],
    ['SCORE ≥ 1', 'NEEDS ADMISSION & urgent endoscopy within 24h', ''],
]
story.append(plain_table(gbs_table, [CW*0.44, CW*0.34, CW*0.22]))

story.append(Spacer(1,8))
story.append(Paragraph('<b>Lower GI Bleeding (LGIB)</b> — from the colon (large bowel), rectum, or anus. Presents as bright red blood per rectum (PR bleeding = blood from the back passage):'))
lgib_table = [
    ['Cause', 'Age group', 'Key features', 'Management'],
    ['Haemorrhoids (piles) — dilated veins in the rectum/anus', 'Any, commoner with age, pregnancy', 'Bright red blood on tissue paper or dripping after defecation. Painless (internal) or painful (external/thrombosed). Perianal pruritus.', 'High fibre diet, stool softeners, topical treatments. Rubber band ligation or haemorrhoidectomy for persistent cases.'],
    ['Diverticular disease — small pouches (diverticula) in the colonic wall bulge out and their blood vessels rupture', '> 50 years', 'Painless LARGE VOLUME bright red or dark red PR bleeding. Often stops spontaneously (80%). May be haemodynamically significant.', 'Colonoscopy (camera into large bowel from below) once stabilised. Endoscopic haemostasis. CT angiography + embolisation. Surgery rarely needed.'],
    ['Colorectal cancer', '> 50 years', 'Change in bowel habit (constipation/diarrhoea alternating). Blood mixed with stool (not just on surface). Weight loss. Iron deficiency anaemia. Rectal mass on PR examination.', 'Urgent 2-week-wait colonoscopy. CT staging. Surgical/oncological referral.'],
    ['Inflammatory Bowel Disease (IBD) — Crohn\'s disease or Ulcerative colitis (UC)', 'Young adults 15-40', 'UC: bloody diarrhoea (blood and mucus mixed with stool), cramping abdominal pain, urgency, tenesmus (feeling of incomplete emptying). Crohn\'s: transmural inflammation, can affect anywhere mouth to anus.', 'Aminosalicylates (mesalazine), corticosteroids, immunosuppressants (azathioprine), biologics (infliximab). Surgical colectomy in severe/refractory UC.'],
    ['Angiodysplasia — abnormal blood vessel tangles in colonic wall', 'Elderly, renal failure, aortic stenosis (Heyde syndrome)', 'Recurrent painless PR bleeding. Often chronic occult (hidden) blood loss causing iron deficiency anaemia.', 'Colonoscopy with argon plasma coagulation (APC) — a plasma beam that seals the abnormal vessels.'],
    ['Meckel\'s diverticulum — remnant of foetal gut in small intestine', 'Children / young adults', 'Rule of 2s: 2% of population, 2 inches long, 2 feet from ileocaecal valve, 2:1 male, presents by age 2. Painless PR bleeding from ectopic gastric mucosa producing acid which ulcerates the adjacent bowel.', 'Technetium-99m Meckel\'s scan (nuclear medicine scan detects gastric mucosa). Surgical resection.'],
    ['Ischaemic colitis — bowel starved of blood supply', 'Elderly, atherosclerosis, post-aortic surgery', 'Sudden onset left-sided abdominal pain then bloody diarrhoea within 24h. Often in splenic flexure (watershed area — furthest from blood supply).', 'Supportive (most resolve). CT or colonoscopy. Surgery if necrosis (tissue death).'],
]
story.append(plain_table(lgib_table, [CW*0.22, CW*0.13, CW*0.35, CW*0.30]))
memory_hook('UPPER GI bleed: HAEMATEMESIS (vomiting blood) + MELAENA (black tarry stool). LOWER GI bleed: BRIGHT RED BLOOD from the back passage. Exception: very rapid UPPER GI bleed can also cause bright red PR blood (blood moves through gut so fast it has no time to turn black).', story)
divider(story)

# ── SECTION 10: OBSTETRIC & GYNAECOLOGICAL BLEEDING ────────────────────────
sec_header('Section 10: Obstetric & Gynaecological Bleeding', story)
professor_says('The uterus (womb) has an extraordinary blood supply — at term (the end of pregnancy), the uterine arteries carry 800ml of blood per minute. When something goes wrong, haemorrhage can be faster and more catastrophic than almost any other clinical situation. This is why obstetric haemorrhage is the leading cause of maternal (motherly) mortality worldwide.', story)

obs_table = [
    ['Condition', 'Definition', 'Risk factors & mechanism', 'Clinical features', 'Management'],
    ['Postpartum haemorrhage\n(PPH)\n— bleeding after childbirth',
     'PRIMARY PPH: loss of ≥500ml within 24h of delivery (or ≥1000ml after caesarean section). MAJOR PPH: >1000ml. MASSIVE PPH: >2000ml or any haemodynamically significant loss.',
     '4 Ts: TONE (80%) — uterine atony (uterus fails to contract after delivery, most common cause), TRAUMA (20%) — genital tract lacerations/uterine rupture, TISSUE (retained placenta or products of conception), THROMBIN (coagulopathy). Risk factors: prolonged labour, multiple pregnancy, grand multiparity (many previous births), placenta praevia.',
     'Bleeding from vagina/perineum after delivery. Uterus soft and "boggy" (poorly contracted — feels like a soft bag of water rather than firm) in atony. Haemodynamic instability. Pallor, tachycardia, hypotension.',
     'HAEMOSTASIS TEAM APPROACH: Call for help. IV access ×2, FBC, coagulation, group & crossmatch. OXYTOCIN (10 units IV or IM — first-line drug to contract uterus). ERGOMETRINE if no contraindication (contraindicated in hypertension). Carboprost (15-methyl PGF2α — prostaglandin that contracts uterus, 250mcg IM every 15 min up to 8 doses). Misoprostol 800mcg sublingual. UTERINE MASSAGE. Bimanual compression. Surgical: B-Lynch suture (compresses uterus), intrauterine balloon tamponade (Bakri balloon). LAST RESORT: hysterectomy (removal of uterus) to save life.'],
    ['Placenta praevia\n(placenta lying low)',
     'The placenta (the organ connecting mother and baby, attached to the uterine wall) implants over or near the cervical os (the opening of the womb). As the lower uterine segment stretches in late pregnancy, the placenta tears.',
     'Previous caesarean section (scarring attracts low implantation). Multiple pregnancy. Increasing maternal age. Smoking.',
     'PAINLESS bright red vaginal bleeding after 28 weeks, often recurrent. May be provoked by intercourse or vaginal examination. DO NOT perform digital vaginal examination (could cause catastrophic haemorrhage by separating the placenta further).',
     'Hospital admission. IV access. FBC, group & save (or crossmatch). Antenatal steroids if <34 weeks (to mature fetal lungs). Planned caesarean section at 36-37 weeks (or emergency section if major haemorrhage). Blood transfusion as needed.'],
    ['Placental abruption\n(placenta separating early)',
     'Premature separation of the normally situated placenta from the uterine wall. Bleeding occurs between the placenta and uterine wall — may be concealed (no external bleeding) or revealed (external bleeding).',
     'Hypertension / pre-eclampsia. Trauma (domestic violence, road accident). Cocaine use. Smoking. Previous abruption.',
     'PAINFUL (contrasting with placenta praevia which is painless). Dark red vaginal bleeding (may be minimal despite massive concealed abruption). HARD, TENDER, "WOODY" UTERUS (uterus in constant contraction/spasm = Couvelaire uterus). Fetal distress or death. Maternal DIC (disseminated intravascular coagulation — massive clotting factor consumption from tissue factor release).',
     'Emergency delivery (caesarean if fetal distress, normal delivery if fetus dead and mother stable). Aggressive resuscitation. Watch for DIC (clotting studies, replace factors with FFP, cryoprecipitate, platelets). Blood transfusion.'],
    ['Ectopic pregnancy\n(pregnancy outside the womb)',
     'A fertilised egg implants outside the uterine cavity — 95% in the fallopian tube (the tube connecting the ovary to the uterus). The tube cannot expand like the uterus → it ruptures → catastrophic intraperitoneal (inside the abdomen) haemorrhage.',
     'Previous pelvic inflammatory disease (PID), previous ectopic, IUD in-situ, previous tubal surgery, IVF, smoking.',
     'CLASSIC TRIAD: amenorrhoea (missed period) + abdominal/pelvic pain + vaginal bleeding. Shoulder tip pain (blood under diaphragm — same mechanism as Kehr\'s sign). SHOCKED patient (disproportionate shock for apparently small blood loss — because the bleeding is internal and massive). Cervical excitation (pain on moving the cervix during pelvic examination = positive "chandelier sign").',
     'RESUSCITATE. Positive beta-hCG confirms pregnancy. TRANSVAGINAL ULTRASOUND (TVS): no intrauterine pregnancy + free fluid + adnexal mass = ectopic until proven otherwise. EMERGENCY SURGERY: laparoscopic salpingectomy (keyhole removal of affected tube). Medical (methotrexate) ONLY in stable, small unruptured ectopics. Anti-D immunoglobulin if Rh-negative (Rhesus negative) patient.'],
    ['Menorrhagia\n(heavy periods)\nand dysfunctional uterine bleeding (DUB)',
     'Menorrhagia: loss of >80ml per menstrual cycle (difficult to measure — practically defined as socially disruptive bleeding, soaking pads, clots, flooding). DUB: abnormal uterine bleeding without identifiable pathological cause (often anovulatory cycles).',
     'Fibroids (leiomyomata — benign smooth muscle tumours of the uterus). Endometrial polyps. Endometriosis. Hypothyroidism. Coagulopathy (von Willebrand disease — most common inherited bleeding disorder). Anticoagulant medications.',
     'Prolonged, heavy periods. Passage of large clots. Iron deficiency anaemia (pallor, fatigue, dyspnoea, brittle nails, koilonychia — spoon-shaped nails, pica — craving to eat ice/clay). Dysmenorrhoea (painful periods). Impact on quality of life.',
     'Bloods: FBC (anaemia), TFTs (thyroid function), coagulation, hormonal profile (LH/FSH/oestrogen/progesterone), transvaginal USS, endometrial biopsy if >45 or risk factors. MEDICAL: Levonorgestrel IUS (Mirena coil — first line, reduces bleeding 85-90%). NSAIDs (tranexamic acid 1g three times daily during period, reduces blood loss 50%). COC (combined oral contraceptive pill). Norethisterone. SURGICAL: endometrial ablation (destroys lining), myomectomy (fibroid removal), hysterectomy.'],
]
story.append(plain_table(obs_table, [CW*0.13, CW*0.15, CW*0.18, CW*0.23, CW*0.31]))
alert_box('OBSTETRIC HAEMORRHAGE EMERGENCY: Call obstetric team + anaesthetics + haematology together. Use the HAEMOSTASIS mnemonic: H-seek Help, A-Assess and resuscitate, E-Establish cause, M-Massage uterus, O-Oxytocin infusion, S-Shift to theatre, T-Tamponade or surgical haemostasis, A-Apply compression sutures, S-Systemic pelvic devascularisation, I-Interventional radiology, S-Subtotal/total hysterectomy as last resort.', story)
divider(story)

# ── SECTION 11: PREHOSPITAL & FIRST AID MANAGEMENT ──────────────────────────
sec_header('Section 11: Prehospital & First Aid Management — Before Hospital', story)
professor_says('The "platinum 10 minutes" at the scene of an accident are the most critical. What you do (or fail to do) in those first minutes directly determines survival. The modern approach is: stop the bleeding, keep the airway open, call for help, and move the patient FAST to definitive care. Do NOT stay at scene trying to treat everything — "load and go."', story)

pre_table = [
    ['Priority', 'Action', 'Why it matters', 'Practical tip'],
    ['1 — PERSONAL SAFETY',
     'Do NOT enter an unsafe scene. DRABCD = Danger first. Survey the scene for ongoing hazards (traffic, fire, electricity, violence, gas, structural collapse).',
     'A second casualty (rescuer) multiplies the problem. Emergency services cannot help others if they are also injured.',
     'Universal precautions: gloves (if available). Hand hygiene even without gloves. A rescuer who collapses from electric shock is another problem.'],
    ['2 — CALL FOR HELP',
     '999 (UK) / 112 (EU) / 911 (US). Give: location (what3words app gives precise 3-word GPS address), number of casualties, mechanism, apparent injuries, your phone number.',
     'Advanced life support is on its way. You are buying time.',
     'Stay on the line with the dispatcher — they will guide you step by step. Speaker mode leaves hands free.'],
    ['3 — MASSIVE HAEMORRHAGE CONTROL (C-ABCDE in military framework: C = catastrophic haemorrhage first)',
     'Direct pressure on any visible wound immediately. Tourniquet for limb bleeding that soaks through pressure dressings. Wound packing for junctional wounds.',
     'Haemorrhage kills faster than any other injury in the first hour. Airway, breathing, circulation — but C (catastrophic haemorrhage) comes FIRST in modern trauma protocols.',
     'Improvised tourniquet if no commercial device: belt, scarf, tie — tighten until all distal bleeding stops. Write time on patient with pen/lipstick/dirt.'],
    ['4 — AIRWAY',
     'Head-tilt chin-lift if no suspected spinal injury. Jaw thrust if spinal injury suspected. Recovery position if unconscious but breathing.',
     'An unconscious patient\'s tongue falls back and blocks the airway. The tongue is the most common cause of airway obstruction in an unconscious person.',
     'Look, listen, feel for breathing for 10 seconds. Gurgling = fluid in airway = position patient. Snoring = tongue = jaw thrust.'],
    ['5 — BREATHING',
     'If not breathing normally: CPR (30 chest compressions : 2 rescue breaths). AED (automated external defibrillator) as soon as available.',
     'CPR maintains minimal perfusion to brain and heart, buying time until defibrillation or advanced care.',
     'Chest seal for sucking chest wound (air entering through chest wall hole): 3-sided seal initially to allow air to escape but not enter.'],
    ['6 — HYPOTHERMIA PREVENTION',
     'Cover the patient with anything available: coats, foil blanket, plastic sheeting. Get them off the cold ground. Do NOT give anything by mouth.',
     'Hypothermia (body temperature <35°C) impairs clotting — makes bleeding WORSE. Part of the "lethal triad." Even mild hypothermia doubles mortality in trauma patients.',
     '"Keep them warm, keep them alive." The ground conducts heat away 25 times faster than cold air. Insulate from below first.'],
    ['7 — SPINAL PROTECTION',
     'Manual in-line stabilisation for suspected spinal injury (high-energy mechanism, unconscious patient, neck pain, neurological symptoms).',
     'An unstable cervical spine fracture with spinal cord intact can become a devastating cord injury if the neck is moved carelessly.',
     'Do NOT apply cervical collar if it causes pain or airway compromise. Manual stabilisation is safer than a poorly applied collar.'],
    ['8 — POSITION & TRANSPORT',
     'Supine (flat) for hypotensive patients. Recovery position for unconscious. PREGNANT PATIENTS: left lateral tilt (manual displacement of uterus or pillow under right hip) to prevent aortocaval compression.',
     'In late pregnancy, the uterus compresses the inferior vena cava (the large vein returning blood from legs to heart) when patient is flat — reducing cardiac output by up to 40%.',
     '"Scoop and run" for penetrating trauma. "Stay and play" (stabilise at scene) for prolonged entrapment. Modern evidence favours shorter scene times for most trauma.'],
]
story.append(plain_table(pre_table, [CW*0.15, CW*0.25, CW*0.30, CW*0.30]))
memory_hook('MARCH protocol (military prehospital): M=Massive haemorrhage (stop it first), A=Airway, R=Respiration, C=Circulation, H=Hypothermia. MARCH replaces ABC in major trauma because uncontrolled haemorrhage kills in minutes while airway problems kill in seconds — but you can stop bleeding faster than you can intubate.', story)
divider(story)

# ── SECTION 12: IN-HOSPITAL MANAGEMENT ──────────────────────────────────────
sec_header('Section 12: In-Hospital Management — Emergency Department to ICU', story)
professor_says('The emergency department receives the patient in the "golden hour." Everything in hospital management is designed to answer one question rapidly: WHERE is the bleeding and HOW do we stop it? Resuscitation and diagnosis happen simultaneously — not one after the other.', story)

story.append(Paragraph('<b>MASSIVE TRANSFUSION PROTOCOL (MTP)</b> — activated when a patient requires ≥10 units of packed red cells in 24 hours, or is predicted to need this:'))
mtp_table = [
    ['Component', 'Ratio', 'What it provides', 'Why this ratio?'],
    ['Packed Red Blood Cells (pRBC)\n— the red cells that carry oxygen', '1 part', 'Haemoglobin and oxygen-carrying capacity. Each unit raises Hb by approximately 10 g/L in a 70kg adult.', 'The oxygen carrier — the most obvious replacement.'],
    ['Fresh Frozen Plasma (FFP)\n— the liquid part of blood containing ALL clotting factors', '1 part', 'All coagulation factors (I to XIII), fibrinogen, protein C, protein S, vWF. Thaws in ~20-30 minutes.', 'Haemorrhage consumes clotting factors (dilution + consumption). Replacing 1:1 prevents coagulopathy and breaks the lethal triad.'],
    ['Platelets\n— the tiny cell fragments that form the first clot plug', '1 part', 'Platelet count restoration. One apheresis unit OR one pool of 4 random donor units.', '1:1:1 ratio is the "damage control resuscitation" target — evidence from PROPPR trial (2015) shows improved 24h and 30-day survival.'],
    ['Cryoprecipitate\n(cold precipitate — fibrinogen-rich fraction)', 'Additional', 'Very high concentration of fibrinogen, factor VIII, vWF, factor XIII. Indicated when fibrinogen <1.5 g/L.', 'Fibrinogen is consumed fastest in massive haemorrhage. Low fibrinogen = clot falls apart. Cryoprecipitate replaces specifically.'],
    ['Tranexamic Acid (TXA)\n— a drug, not a blood product', '1g IV over 10 min then 1g over 8h', 'Blocks plasmin (the enzyme that dissolves clots). Prevents fibrinolysis (breakdown of clots).', 'CRASH-2 trial: reduces haemorrhagic death by 15% if given within 3 hours of injury. After 3h = may worsen outcome (procoagulant risk). Must give within 3 hours.'],
    ['Calcium', '10ml of 10% calcium chloride IV', 'Restores ionised calcium depleted by citrate preservative in blood products.', 'Citrate in stored blood chelates (binds) calcium → hypocalcaemia → reduced cardiac contractility → further cardiovascular compromise.'],
]
story.append(plain_table(mtp_table, [CW*0.22, CW*0.12, CW*0.33, CW*0.33]))

story.append(Spacer(1,8))
story.append(Paragraph('<b>PERMISSIVE HYPOTENSION</b> — counterintuitive but evidence-based:'))
info_box('<b>Permissive hypotension (also called hypotensive resuscitation):</b> In penetrating trauma and uncontrolled haemorrhage, AIM for a systolic BP of 80-90 mmHg rather than "normal" 120 mmHg UNTIL surgical haemostasis is achieved. RATIONALE: Raising BP higher disrupts forming clots (hydrostatic pressure cracks the platelet plug), dilutes clotting factors (if you give lots of saline/Hartmann\'s to reach "normal" BP), and causes hypothermia. EXCEPTION: Traumatic brain injury (TBI) — maintain SBP ≥90mmHg (or MAP ≥65mmHg) because the brain needs adequate perfusion pressure. Also exception: elderly patients with chronic hypertension (their autoregulation is set higher).', story)

story.append(Spacer(1,6))
story.append(Paragraph('<b>Damage Control Surgery (DCS)</b> — a 3-stage surgical approach for the most critically injured:'))
dcs_table = [
    ['Stage', 'What happens', 'Goal', 'Duration'],
    ['Stage I — Damage Control Operation',
     'Brief initial surgery (< 60 minutes). Control haemorrhage (perihepatic packing, clamping, ligation). Control contamination (staple/tie bowel ends). Close abdomen temporarily (VAC dressing, "Bogota bag" — a sterile IV bag sutured in as temporary closure).',
     'STOP THE BLEEDING. STOP THE CONTAMINATION. Leave definitive repair for later.',
     '45-90 minutes maximum — operating in a cold, acidotic, coagulopathic patient is futile and worsens physiology.'],
    ['Stage II — ICU Resuscitation',
     'Patient transferred to ICU. Correct the lethal triad: warm the patient (warm IV fluids, warm blankets, warm environment), correct acidosis (IV bicarbonate if pH <7.1, ensure adequate perfusion), correct coagulopathy (FFP, platelets, cryoprecipitate, TXA). Optimise ventilation, nutrition.',
     'RESTORE NORMAL PHYSIOLOGY so the patient can survive a definitive second operation.',
     '24-72 hours in ICU until: pH >7.35, temperature >36°C, lactate normalising, coagulation correcting.'],
    ['Stage III — Definitive Surgery',
     'Return to theatre. Remove packing. Achieve definitive haemostasis (arterial repair, vascular grafts). Restore bowel continuity. Close abdomen primarily or with mesh.',
     'FIX EVERYTHING PROPERLY now the patient can tolerate it.',
     'Variable — the full repair operation.'],
]
story.append(plain_table(dcs_table, [CW*0.10, CW*0.32, CW*0.32, CW*0.26]))
image_search_box('Damage control resuscitation diagram', 'Google Images: damage control resuscitation 1:1:1 ratio flowchart / massive transfusion protocol activation criteria / permissive hypotension trauma evidence', story)
divider(story)

# ── SECTION 13: PHARMACOLOGY OF HAEMORRHAGE ─────────────────────────────────
sec_header('Section 13: Pharmacology — Drugs in Haemorrhage Management', story)
professor_says('Drugs in haemorrhage fall into two categories: drugs that HELP STOP bleeding (haemostatic agents), and drugs that CAUSED or WORSENED the bleeding (anticoagulants that need reversing). You need to know both directions. Think of it as having a tap and a drain — some drugs turn off the drain (TXA), others plug the tap that someone left running (reversal agents).', story)

pharm_table = [
    ['Drug / Agent', 'Class & Mechanism', 'Indication', 'Dose & Route', 'Key points / Side effects'],
    ['Tranexamic acid\n(TXA)',
     'Anti-fibrinolytic. Inhibits plasminogen activators, preventing conversion of plasminogen to plasmin. Plasmin dissolves clots — TXA preserves them.',
     'Trauma-associated haemorrhage (CRASH-2 trial). Post-partum haemorrhage (WOMAN trial — reduces PPH deaths). Menorrhagia (oral). GI bleed (some evidence). Surgery.',
     '1g IV over 10 minutes, then 1g IV over 8 hours. MUST be given within 3h of injury/onset of PPH. PPH: 1g IV, repeat if needed. Menorrhagia: 1g TDS orally during period.',
     'Safe and cheap. After 3h in trauma: risk of thrombosis (DVT, PE) may outweigh benefit. Do NOT give if >3h post-injury in trauma. Contraindicated in active thromboembolic disease.'],
    ['Vitamin K\n(phytomenadione)',
     'Cofactor for hepatic synthesis of clotting factors II, VII, IX, X (and anticoagulant proteins C and S). Reverses warfarin effect over 6-12 hours.',
     'Reversal of warfarin (or vitamin K deficiency) when haemorrhage is present.',
     'URGENT reversal: 5-10mg IV slow injection. Non-urgent: 1-5mg oral. IV takes 6-12h to work. Full reversal over 24h.',
     'IV anaphylaxis risk — give slowly with resuscitation facilities. Oral works for non-urgent. Does NOT reverse DOACs. Parenteral route faster but risks anaphylaxis.'],
    ['Prothrombin Complex Concentrate\n(PCC, e.g., Beriplex, Octaplex)',
     'Concentrated clotting factors II, VII, IX, X (± protein C and S). "4-factor PCC" contains all four vitamin-K-dependent factors.',
     'URGENT reversal of warfarin in life-threatening haemorrhage. Also used in DOAC reversal and factor replacement.',
     'Dose based on patient\'s weight and INR: typically 25-50 units/kg IV. Given with vitamin K (as PCC effect wears off but warfarin persists).',
     'Immediate effect (minutes). Thrombosis risk. Must give WITH vitamin K to maintain reversal (PCC lasts hours, warfarin lasts days).'],
    ['Idarucizumab\n(Praxbind)',
     'Monoclonal antibody fragment that binds dabigatran (a direct thrombin inhibitor DOAC) with very high affinity. Immediately neutralises it.',
     'Reversal of dabigatran (Pradaxa) in life-threatening bleeding or emergency surgery.',
     '5g IV (as two 2.5g vials given sequentially). Single dose sufficient.',
     'Specific only to dabigatran. Fast onset (<5 minutes). Very expensive. May need redosing rarely if dabigatran redistributes from tissues.'],
    ['Andexanet alfa\n(Ondexxya)',
     'Modified factor Xa molecule (decoy) that binds and sequesters factor Xa inhibitors (rivaroxaban, apixaban) away from their target.',
     'Reversal of rivaroxaban (Xarelto) or apixaban (Eliquis) in life-threatening haemorrhage.',
     'Weight-based dosing: "low dose" 400mg IV bolus + 480mg infusion OR "high dose" 800mg + 960mg infusion depending on DOAC dose and timing.',
     'Extremely expensive (>£15,000 per dose). Thrombosis risk. Alternative in resourced-limited settings: PCC 50 units/kg (off-label but widely used).'],
    ['Protamine sulphate',
     'Positively charged protein that binds negatively charged heparin molecules, neutralising anticoagulant effect immediately.',
     'Reversal of unfractionated heparin (UFH). Partial reversal of LMWH (low molecular weight heparin e.g. enoxaparin).',
     'UFH: 1mg protamine per 100 units heparin given in last 2-3h, max 50mg IV slow. LMWH: 1mg per 1mg enoxaparin (maximum 60% reversal of anti-Xa activity).',
     'Anaphylaxis risk (especially in fish allergy, previous protamine exposure, vasectomy). Bradycardia, hypotension if given too fast. Only partially reverses LMWH.'],
    ['Desmopressin\n(DDAVP — 1-deamino-8-D-arginine vasopressin)',
     'Synthetic analogue of ADH (antidiuretic hormone). Causes release of stored von Willebrand Factor (vWF) and factor VIII from endothelial cells (cells lining blood vessels).',
     'Haemophilia A (mild-moderate, factor VIII deficiency). von Willebrand disease type 1. Platelet dysfunction (uraemia, aspirin effect).',
     '0.3 mcg/kg IV or intranasal. Intranasal: 150 mcg per nostril (300 mcg total).',
     'Tachyphylaxis (reduced effect with repeat doses as vWF stores are depleted). Risk of hyponatraemia (low sodium — retains water). Avoid in cardiovascular disease. Ineffective in haemophilia B (factor IX deficiency).'],
    ['Vasopressors\n(noradrenaline, adrenaline, vasopressin)',
     'Vasopressin-like agents that cause arterial vasoconstriction (narrowing), raising blood pressure by increasing peripheral vascular resistance.',
     'Haemorrhagic or distributive (septic) shock unresponsive to volume resuscitation. As a bridge while surgical haemostasis is obtained.',
     'Noradrenaline: 0.01-3 mcg/kg/min IV via central line (central venous catheter). Adrenaline: 0.01-0.3 mcg/kg/min in cardiac arrest/severe shock. Vasopressin: 0.03-0.04 units/min (fixed dose).',
     'MUST NOT replace volume resuscitation — vasopressors on an empty tank constrict vessels but do not restore cardiac output. Cause tissue ischaemia if prolonged. Require central line and ICU monitoring. Noradrenaline is first-choice vasopressor in haemorrhagic shock.'],
]
story.append(plain_table(pharm_table, [CW*0.14, CW*0.19, CW*0.15, CW*0.17, CW*0.35]))
memory_hook('ANTICOAGULANT REVERSAL: WARFARIN = Vitamin K + PCC (immediate). DABIGATRAN (the thrombin inhibitor) = Idarucizumab ("I-da-roo-sizz-oo-mab" — think "I deactivate dabigatran"). RIVAROXABAN/APIXABAN (factor Xa inhibitors) = Andexanet alfa ("anti-Xa antidote"). HEPARIN = Protamine. No antidote for fondaparinux — use PCC off-label.', story)
divider(story)

# ── SECTION 14: COMPLICATIONS ───────────────────────────────────────────────
sec_header('Section 14: Complications — The Lethal Triad and DIC', story)
professor_says('Three killers conspire against every severely bleeding patient. Each makes the others worse in a vicious circle that accelerates death. Understanding this triangle is the key to understanding why we resuscitate the way we do.', story)

story.append(Paragraph('<b>The Lethal Triad of Trauma (also called the "Triad of Death"):</b>'))
triad_table = [
    ['Component', 'Definition', 'How it develops', 'How it kills', 'How to reverse it'],
    ['HYPOTHERMIA\n(body temperature < 35°C)',
     'The body\'s core temperature falls below the normal range of 36.5-37.5°C. Severe = <32°C.',
     'Blood loss → reduced perfusion → less metabolic heat generation. Cold IV fluids and blood products. Cold environment at scene, in A&E. Wet clothing.',
     'Hypothermia inhibits clotting enzymes (all enzymes work best at 37°C — each 1°C drop below 37°C reduces enzymatic activity by ~10%). Impairs platelet function. Causes cardiac arrhythmias (VF below 28°C).',
     'Warm IV fluids (fluid warmer device). Warm blankets. Warm environment. Remove wet clothing. For severe: warmed humidified inspired air, bladder irrigation, or ECMO (extracorporeal membrane oxygenation) in extremis.'],
    ['ACIDOSIS\n(blood pH < 7.35)',
     'The blood becomes too acidic. Normal blood pH is 7.35-7.45 (slightly alkaline). Metabolic acidosis: the blood\'s bicarbonate falls and lactate rises.',
     'Poor perfusion → anaerobic metabolism (cells burning fuel without oxygen) → lactic acid production → pH falls. Each unit of stored blood is also mildly acidic (citrate preservative).',
     'Acidosis impairs cardiac contractility (the heart pumps weakly). Impairs clotting factor function. Worsens coagulopathy in synergy with hypothermia.',
     'Restore perfusion (stop the bleeding!). Adequate ventilation (CO2 removal). IV sodium bicarbonate if pH <7.1 (temporary bridge). Correct lactate by improving cardiac output and tissue perfusion.'],
    ['COAGULOPATHY\n(inability to clot normally)',
     'The clotting system fails. Can be measured by: prolonged PT/APTT, low fibrinogen (<1.5 g/L), low platelets (<100), raised INR, positive TEG/ROTEM (viscoelastic haemostasis tests).',
     'Consumption of clotting factors (haemorrhage uses up factors faster than the liver can make them). Dilution (crystalloid fluids have no clotting factors). Hypothermia and acidosis impair remaining factors. DIC (see below).',
     'No clots form despite ongoing bleeding. Wounds bleed continuously. Surgical haemostasis fails. Wound oozes from ALL surfaces — this is called "coagulopathic haemorrhage."',
     'Replace factors: FFP, cryoprecipitate (fibrinogen), platelets. TXA (prevent fibrinolysis). Correct underlying hypothermia and acidosis. 1:1:1 ratio transfusion strategy.'],
]
story.append(plain_table(triad_table, [CW*0.14, CW*0.15, CW*0.20, CW*0.22, CW*0.29]))
alert_box('THE LETHAL TRIAD IS SELF-AMPLIFYING: Hypothermia worsens coagulopathy → more bleeding → worse acidosis → worse coagulopathy → worse hypothermia. The ONLY way to break this cycle is: (1) STOP THE BLEEDING surgically, and (2) CORRECT ALL THREE simultaneously. This is why 1:1:1 transfusion, TXA, and active warming are started together, not sequentially.', story)

story.append(Spacer(1,8))
story.append(Paragraph('<b>Disseminated Intravascular Coagulation (DIC)</b> — "the clotting system eating itself":'))
professor_says('DIC is like a forest fire that started in one place but has now spread everywhere out of control. The body\'s clotting system, triggered by massive tissue damage or infection, activates uncontrollably throughout the entire bloodstream. Tiny clots form in small vessels everywhere, using up all the clotting factors and platelets. Then the patient paradoxically BLEEDS from everywhere because there is nothing left to clot with.', story)

dic_table = [
    ['Aspect', 'Detail'],
    ['Definition',
     'A pathological (disease-caused) state in which the normal clotting system is activated simultaneously throughout the body — initially causing widespread microvascular thrombosis (tiny clots in small blood vessels), then consuming all clotting factors and platelets, leading to SIMULTANEOUS CLOTTING AND BLEEDING.'],
    ['Triggers in trauma & haemorrhage context',
     'Massive trauma (tissue damage releases tissue factor, which triggers the extrinsic pathway throughout the circulation). Massive blood transfusion. Amniotic fluid embolism (AF enters maternal circulation at delivery — extremely potent activator of clotting). Placental abruption. Sepsis (bacterial toxins activate endothelium). Burns. Malignancy (chronic DIC).'],
    ['Laboratory findings',
     'Raised PT and APTT (clotting time prolonged — factors consumed). LOW FIBRINOGEN (<1.5 g/L, often <0.5 g/L = critical). LOW PLATELETS (consumed, typically <50). Raised D-dimer (breakdown product of fibrin clots — very high). Raised FDPs (fibrinogen degradation products). Low factor V and VIII. Blood film (on microscopy): schistocytes (fragmented red cells being shredded by fibrin strands in small vessels) = microangiopathic haemolytic anaemia (MAHA).'],
    ['Clinical findings',
     'BLEEDING from ALL sites simultaneously: IV lines, surgical wounds, venepuncture (blood test) sites, gums, nose, gut. PLUS ischaemic complications from microvascular thrombosis: renal failure, ARDS (adult respiratory distress syndrome — lungs fail), hepatic failure, gangrene of digits. This paradox (bleeding + clotting simultaneously) is pathognomonic of DIC.'],
    ['Management',
     'TREAT THE UNDERLYING CAUSE (stop the bleeding, control infection, deliver the baby). Clotting factor replacement: FFP, cryoprecipitate (fibrinogen — MOST important), platelets. Target: fibrinogen >2g/L, platelets >50, PT ratio <1.5. Cryoprecipitate dose: 2 pools (10 units) IV. Fibrinogen concentrate (RiaSTAP) 3-4g IV as alternative. TXA (tranexamic acid) is controversial in DIC (may worsen if predominantly thrombotic phase) — use only if predominantly haemorrhagic DIC with high fibrinolysis on ROTEM. Heparin is NOT routinely recommended in acute DIC.'],
    ['MRCP exam key',
     'DIC is a common exam scenario. Key distinguishing features: LOW fibrinogen (most specific) + raised D-dimer + raised PT/APTT + low platelets. Chronic DIC (malignancy) may have normal PT but raised D-dimer and thrombosis. Therapeutic heparin in DIC = only in specific purpura fulminans or arterial/venous thrombosis-dominant DIC (specialist haematology advice).'],
]
story.append(plain_table(dic_table, [CW*0.18, CW*0.82]))
divider(story)

# ── SECTION 15: MRCP EXAM HIGH-YIELD TRIGGERS ───────────────────────────────
sec_header('Section 15: MRCP Exam — High-Yield Scenarios & Triggers', story)
story.append(Paragraph('These are the classic question patterns in MRCP Part 1, Part 2 Written, and PACES. '
               'If you recognise the stem and know the answer instantly, you pick up the mark. '
               'Drill these until they are reflexes.'))
mrcp_table = [
    ['Stem / Trigger', 'The key diagnosis', 'The specific answer the examiner wants'],
    ['35-year-old, blow to temple, brief loss of consciousness, now "woken up" and talking normally, GCS 15. 2 hours later: headache, GCS falling, right pupil fixed and dilated.',
     'Extradural haematoma (EDH) — middle meningeal artery tear',
     'LUCID INTERVAL = EDH. CT head: biconvex (lens-shaped) hyperdense (white) haematoma. Emergency craniotomy. The fixed dilated pupil is on the SAME side as the injury (ipsilateral) — CN III (3rd cranial nerve) is compressed by the expanding haematoma.'],
    ['Worst headache of my life, sudden onset, vomiting. CT head normal. What next?',
     'Subarachnoid haemorrhage (SAH) — CT negative in ~5% within first 6h.',
     'LUMBAR PUNCTURE at 12 hours (to allow red cell breakdown to xanthochromia — yellow CSF colour). Do NOT miss SAH. "Worst headache ever" = SAH until proven otherwise. Negative CT + LP at 12h = safe to discharge with neurovascular follow-up.'],
    ['Shocked patient after pelvic fracture. No obvious external bleeding. FAST scan negative.',
     'Retroperitoneal haematoma — pelvic venous plexus / internal iliac arterial injury. FAST scan cannot reliably detect retroperitoneal blood.',
     'Apply pelvic binder immediately. Activate MTP. CT pelvis with contrast (to identify arterial extravasation). Angioembolisation. FAST negative does NOT exclude significant haemorrhage.'],
    ['Patient on warfarin, INR 8.2, brain haemorrhage on CT, needs URGENT reversal.',
     'Over-anticoagulation causing intracranial haemorrhage.',
     'PCC (prothrombin complex concentrate) 25-50 units/kg IV IMMEDIATELY + Vitamin K 5-10mg IV. PCC reverses in minutes. Warfarin alone takes 24h even with vitamin K. Do NOT use FFP as first-line in intracranial haemorrhage (slower, larger volume, variable factor content).'],
    ['Patient on dabigatran (Pradaxa), catastrophic GI bleed.',
     'Dabigatran — direct thrombin inhibitor DOAC.',
     'Idarucizumab (Praxbind) 5g IV. Specific antidote. Immediate reversal. Also: activated charcoal if taken within 2h. Dialysis can remove dabigatran (renally cleared) but too slow for emergency.'],
    ['Cirrhotic patient, massive haematemesis, haemodynamically unstable.',
     'Oesophageal variceal haemorrhage — portal hypertension.',
     'Terlipressin 2mg IV (only drug proven to reduce mortality) + Ceftriaxone 1g IV (antibiotic prophylaxis, reduces bacterial translocation and mortality) + Urgent OGD for band ligation. Sengstaken-Blakemore tube if uncontrolled as bridge. Do NOT give beta-blocker acutely (causes hypotension).'],
    ['Young woman, missed period, right-sided pelvic pain, vaginal spotting, shocked out of proportion to apparently minor blood loss.',
     'Ruptured ectopic pregnancy.',
     'Beta-hCG positive + TVS (transvaginal ultrasound) showing no intrauterine pregnancy + free pelvic fluid = ruptured ectopic until proven otherwise. EMERGENCY LAPAROSCOPY. Give anti-D immunoglobulin if Rh-negative. IV access ×2, blood products, nil by mouth for theatre.'],
    ['Postpartum patient, 900ml blood loss, uterus soft and boggy on examination.',
     'Primary postpartum haemorrhage due to uterine atony.',
     'Oxytocin 10 units IV/IM (first-line). Then ergometrine (if not hypertensive). Bimanual uterine compression. Carboprost 250mcg IM. If pharmacological measures fail: intrauterine balloon (Bakri), B-Lynch suture, hysterectomy.'],
    ['Trauma patient: low BP + raised JVP + muffled heart sounds. No obvious wound.',
     'Cardiac tamponade (Beck\'s triad).',
     'Pericardiocentesis immediately (needle below xiphisternum angled to left shoulder). ECG: electrical alternans. ECHO confirms. Cardiac surgery for definitive drainage.'],
    ['Right-sided chest injury, absent breath sounds right, tracheal deviation to LEFT, JVD, hypotensive, tachycardic.',
     'Tension pneumothorax (or massive haemothorax — differentiate: tension = hyperresonant on percussion, haemothorax = dull).',
     'Tension pneumo: IMMEDIATE needle decompression (2nd ICS, MCL), then chest drain. DO NOT wait for CXR. This is a clinical diagnosis. Haemothorax: chest drain ± thoracotomy if output >1500ml.'],
    ['Diffuse oozing from all wound sites + IV line sites. INR very high. Fibrinogen <0.5 g/L. Schistocytes on blood film.',
     'Disseminated Intravascular Coagulation (DIC).',
     'Treat underlying cause + replace: Cryoprecipitate (fibrinogen — most urgent) + FFP + Platelets. Target fibrinogen >2 g/L. D-dimer very high in DIC. Do NOT use heparin routinely. TXA controversial.'],
    ['PACES station: Patient with pallor, dyspnoea, tachycardia. History reveals NSAID use. Stool is black and tarry. What do you examine and what do you find?',
     'Upper GI bleed (likely peptic ulcer, NSAID-related). Iron deficiency anaemia from chronic blood loss.',
     'PR examination for melaena (mandatory in PACES for any GI history). Periumbilical examination for stigmata of chronic liver disease. Epigastric tenderness. Calculate Glasgow-Blatchford Score. Urgent OGD. Bloods: FBC (low Hb, low MCV, low ferritin), raised urea:creatinine ratio (>100:1 = blood digested in gut, raises BUN). Stop NSAIDs. PPI.'],
]
story.append(plain_table(mrcp_table, [CW*0.30, CW*0.22, CW*0.48]))
divider(story)

# ── SECTION 16: MINIMAL RESOURCES + PACES GUIDE ─────────────────────────────
sec_header('Section 16: Minimal Resources Protocol & PACES Examination Guide', story)
story.append(Paragraph('<b>How to manage bleeding with only clinical examination and basic investigations</b> — '
               'resource-limited settings, remote areas, mass casualty situations:'))

minimal_data = [
    ['Situation', 'Available resources', 'What to do', 'When to refer/transfer'],
    ['External haemorrhage\n(any wound)',
     'Hands + cloth/bandage only',
     '1. Direct pressure — hard, continuous, 10-15 min minimum. Do NOT lift. 2. Elevation of limb. 3. Improvised tourniquet (belt/scarf) above wound if arterial. 4. Wound packing with cloth if deep. 5. Monitor: pulse rate (finger on radial pulse), skin colour and temperature, consciousness level.',
     'If bleeding not controlled after 15 min of correct technique. Any arterial bleed. Signs of shock (rapid weak pulse, pallor, confusion).'],
    ['Abdominal/thoracic trauma\n(suspected internal bleeding)',
     'Clinical exam + CBC + blood pressure/pulse',
     '1. FAST if ultrasound available (even basic portable). 2. If no FAST: percuss flanks (dull = fluid). 3. Haemodynamic monitoring every 5 min (HR, RR, BP, GCS, urine output). 4. If deteriorating: supine position, IV access if available, fluid cautiously 250ml boluses to maintain systolic 80-90. 5. Pelvic binder for pelvic fracture suspicion (any cloth/sheet around pelvis).',
     'Any haemodynamic instability. Positive FAST. Peritonism (rigid abdomen). Falling GCS. Gross pelvic instability.'],
    ['Head injury\n(suspected intracranial bleeding)',
     'GCS assessment + pupil torch',
     '1. Assess GCS every 15 minutes. 2. Check pupils (size, equality, light reaction). 3. Cushing\'s triad check (BP, HR, respiratory pattern). 4. Elevate head of bed 30 degrees (reduces ICP). 5. Keep airway open (jaw thrust, recovery position if GCS <8 and breathing). 6. Avoid hypotension (SBP < 90mmHg worsens TBI outcome). 7. Avoid hypoxia (oxygen by any means). 8. Control agitation (to prevent Valsalva/raised ICP) — use IV morphine if available.',
     'Any drop in GCS. Pupillary change. Cushing\'s triad. GCS <13. Seizures. Penetrating injury. IMMEDIATE transfer to neurosurgical centre.'],
    ['Upper GI bleeding\n(suspected)',
     'Clinical exam + PR exam + CBC',
     '1. PR examination: melaena = UGIB confirmed. 2. NG tube (nasogastric tube — tube through nose into stomach): if bloody aspirate = active UGIB. 3. IV access if available: give PPI (omeprazole if oral available: 40mg, give max dose available). 4. Careful fluid resuscitation (target systolic > 90mmHg). 5. Upright positioning. 6. Nil by mouth. 7. Monitor haemodynamic status closely.',
     'Any haemodynamic instability. Melaena plus tachycardia/hypotension. Suspected variceal bleed (cirrhotic, jaundiced patient) — needs terlipressin and urgent endoscopy.'],
    ['Obstetric haemorrhage\n(PPH)',
     'Hands + oxytocin + clinical exam',
     '1. Uterine massage immediately — bimanual. 2. Oxytocin (if available) 10 units IM/IV. 3. Ergometrine (if no hypertension) 0.5mg IM. 4. Aortic compression (manual pressure on abdominal aorta between umbilicus and xiphisternum against the spine — slows pelvic blood flow as bridge to surgery). 5. Bimanual uterine compression. 6. Manual removal of retained placenta if suspected (under anaesthesia ideally). 7. IV access, position flat.',
     'Bleeding not controlled with above. Signs of shock. Any resource for surgical intervention should be activated: laparotomy, B-Lynch suture, hysterectomy.'],
]
story.append(plain_table(minimal_data, [CW*0.16, CW*0.15, CW*0.43, CW*0.26]))

story.append(Spacer(1,8))
story.append(Paragraph('<b>PACES Station — Haemorrhage/Bleeding Cases</b>'))
story.append(Paragraph('PACES (Practical Assessment of Clinical Examination Skills) tests your ability to examine, present findings, and show clinical reasoning. For bleeding-related stations:'))
paces_table = [
    ['PACES Station', 'Likely scenario', 'What to examine', 'Key things to say to examiner'],
    ['Station 1 or 3 —\nAbdominal examination',
     'Cirrhotic patient with known GI bleeds (varices). Or anaemic patient with GI blood loss.',
     'Hands: leuconychia (white nails, hypoalbuminaemia), palmar erythema (liver disease), clubbing, asterixis (flap — metabolic encephalopathy). Face: jaundice, parotid enlargement (alcohol), xanthelasma. Chest: spider naevi (>5 is abnormal), gynaecomastia. Abdomen: hepatomegaly (liver enlargement), splenomegaly (portal hypertension), ascites (fluid wave + shifting dullness), caput medusae (dilated veins around umbilicus from portal hypertension). PR examination: melaena, rectal mass.',
     '"I would like to complete my examination by checking the blood pressure, performing a PR examination, and checking urine dipstick for haematuria. My findings suggest chronic liver disease with portal hypertension, most likely secondary to..." (state cause: alcohol/viral hepatitis).'],
    ['Station 5 — Integrated\nClinical Assessment',
     'Young woman, pallor, breathless, fatigue. Heavy periods. Or acute GI bleed presentation.',
     'General: pallor (conjunctival, palmar). Koilonychia (spoon nails — iron deficiency). Angular stomatitis (cracks at corners of mouth). Glossitis (smooth beefy red tongue). Tachycardia. Postural hypotension (systolic drops >20mmHg on standing). Rectal examination (for melaena or rectal mass).',
     '"This presentation is consistent with iron deficiency anaemia, likely secondary to menorrhagia. I would investigate with FBC (hypochromic microcytic anaemia, low MCV), serum ferritin (low), transferrin saturation (low), and an upper and lower GI endoscopy to exclude GI blood loss. I would refer to gynaecology and start oral iron replacement."'],
    ['Communication\nStation',
     'Explaining a diagnosis to patient: e.g., explaining SAH diagnosis, or explaining warfarin reversal, or explaining a procedure (pericardiocentesis).',
     'Not an examination station — communication skills assessed.',
     'Use lay language. Acknowledge patient\'s concerns. Chunk and check (give a piece of information, ask if understood). Show empathy. Safety-net (tell them when to return if worse). For SAH explanation: "You have had a bleed around the brain — it is called a subarachnoid haemorrhage. We need to do further tests to find the source and a specialist brain surgeon will review you today."'],
    ['History taking',
     'Patient with acute onset chest pain + haemoptysis (coughing blood) — pulmonary embolism vs aortic dissection vs TB.',
     'Not examination — history. Key discriminating questions.',
     'SOCRATES for pain. Ask about anticoagulants (warfarin, apixaban, rivaroxaban) — directly affects management. Ask about previous DVT/PE, malignancy, long haul travel, immobility. PACES examiners want to see you THINK ALOUD: "My differential includes PE, aortic dissection, and TB. I am asking about asymmetric leg swelling to help distinguish PE..."'],
]
story.append(plain_table(paces_table, [CW*0.15, CW*0.18, CW*0.34, CW*0.33]))

story.append(Spacer(1,10))
# ── COMPREHENSIVE MEMORY HOOK ────────────────────────────────────────────────
sGreen = ParagraphStyle('GH', fontName='DV', fontSize=9, leading=14,
    textColor=HexColor('#155724'), spaceAfter=0)
sGreenB = ParagraphStyle('GHB', fontName='DV-B', fontSize=10, leading=15,
    textColor=HexColor('#155724'), spaceAfter=2)
gTS = TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), HexColor('#d4edda')),
    ('LEFTPADDING', (0,0), (-1,-1), 14),
    ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ('TOPPADDING', (0,0), (0,0), 8),
    ('BOTTOMPADDING', (0,-1), (0,-1), 8),
])
gTSbox = TableStyle([
    ('BOX', (0,0), (-1,-1), 2, HexColor('#28a745')),
    ('BACKGROUND', (0,0), (-1,-1), HexColor('#d4edda')),
    ('LEFTPADDING', (0,0), (-1,-1), 0),
    ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ('TOPPADDING', (0,0), (-1,-1), 0),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
])
green_rows = [
    [Paragraph('COMPREHENSIVE BLEEDING MASTER SUMMARY', sGreenB)],
    [Paragraph('BLOOD VOLUME: Adult = 70 ml/kg (70kg person = 4.9L). Children = 80 ml/kg.', sGreen)],
    [Paragraph('ATLS CLASSES: I=&lt;15%, II=15-30%, III=30-40%, IV=&gt;40%. Class III = tachycardia + falling BP + confused. Class IV = no BP + unconscious.', sGreen)],
    [Paragraph('HAEMOSTASIS: Primary (platelet plug in seconds) then Secondary (fibrin net in minutes) then Fibrinolysis (clean-up in hours).', sGreen)],
    [Paragraph('LETHAL TRIAD: HYPOTHERMIA + ACIDOSIS + COAGULOPATHY. Each worsens the others. Break all three simultaneously with 1:1:1 + TXA + warming.', sGreen)],
    [Paragraph('TXA (TRANEXAMIC ACID): Give within 3 hours of trauma OR PPH. 1g IV then 1g over 8h. CRASH-2 trial. Anti-fibrinolytic.', sGreen)],
    [Paragraph('INTRACRANIAL BLEEDS: EDH (biconvex, lucid interval, temporal) vs SDH (crescent, no lucid interval, elderly/bridging veins) vs SAH (thunderclap headache, LP at 12h) vs ICH (hypertensive, basal ganglia).', sGreen)],
    [Paragraph("CUSHING'S TRIAD: HIGH BP + SLOW PULSE + IRREGULAR BREATHING = impending brainstem herniation. Mannitol + intubate + hyperventilate + neurosurgery NOW.", sGreen)],
    [Paragraph("CHEST EMERGENCIES: Haemothorax (dull + absent sounds) = chest drain. Tension pneumo (hyperresonant + absent sounds + trachea deviation) = needle decompression FIRST. Tamponade (BECK'S TRIAD: low BP + high JVP + muffled heart) = pericardiocentesis.", sGreen)],
    [Paragraph("ABDOMINAL: Kehr's sign (left shoulder tip pain) = splenic injury. Morrison's pouch free fluid on FAST = hepatic injury. Retroperitoneal haematoma: pelvic binder first, no surgery, angioembolisation.", sGreen)],
    [Paragraph('GI BLEEDING: UGIB (Glasgow-Blatchford score) = PPI + OGD. Varices = Terlipressin + antibiotics + band ligation. LGIB: diverticular = painless large volume; cancer = change in bowel habit + weight loss.', sGreen)],
    [Paragraph('OBSTETRIC: ECTOPIC = SHOCK + positive hCG + no IUP on TVS = emergency surgery. PPH = 4Ts: Tone/Trauma/Tissue/Thrombin. Rx: Oxytocin then Ergometrine then Carboprost then Bakri balloon then Hysterectomy.', sGreen)],
    [Paragraph('ANTICOAGULANT REVERSAL: Warfarin = PCC + Vit K. Dabigatran = Idarucizumab. Xa inhibitors = Andexanet alfa. Heparin = Protamine.', sGreen)],
    [Paragraph('DIC: Bleed AND clot simultaneously. LOW fibrinogen (most specific). HIGH D-dimer. Treat cause + cryoprecipitate (fibrinogen) + FFP + platelets.', sGreen)],
    [Paragraph('PREHOSPITAL: MARCH not ABC. M = Massive haemorrhage first. Tourniquet early for limb arterial bleeding. Write time on tourniquet. Permissive hypotension SBP 80-90 until surgery. Keep WARM.', sGreen)],
]
inner_t = Table(green_rows, colWidths=[CW-4])
inner_t.setStyle(gTS)
outer_t = Table([[inner_t]], colWidths=[CW])
outer_t.setStyle(gTSbox)
story.append(outer_t)
story.append(Spacer(1,8))

# ── BUILD ────────────────────────────────────────────────────────────────────
doc.build(story)
print('SUCCESS: /mnt/user-data/outputs/Bleeding_Trauma_MRCP_Note.pdf generated.')
