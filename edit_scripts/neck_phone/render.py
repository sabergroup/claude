import sys, subprocess, numpy as np, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S="/tmp/claude-0/-home-user-claude/5b00ce15-a751-5c6f-a77b-d1addef998ec/scratchpad"
sys.path.insert(0,S)
from plan import *
OUT=sys.argv[1]; PREVIEW=sys.argv[2] if len(sys.argv)>2 else None
WD,HT,FPS=1080,1920,30
CREAM=(0xF8,0xEE,0xDC); GOLD=(0xE9,0xB8,0x72); BEIGE=(0xF0,0xD9,0xB3); SH=(52,28,12)
FM=f"{S}/fonts/EM500.ttf"; FB=f"{S}/fonts/EM700.ttf"
def font(p,s): return ImageFont.truetype(p,s,layout_engine=ImageFont.Layout.RAQM)
def clamp(x,a=0.0,b=1.0): return max(a,min(b,x))
def eo(x): x=clamp(x); return 1-(1-x)**3
def eio(x): x=clamp(x); return x*x*(3-2*x)
def eback(x,c=1.6): x=clamp(x); return 1+(c+1)*(x-1)**3+c*(x-1)**2
DUR=TOTAL/SR
# ---------------- word timing on output timeline
def wt(i):
    ws,we=W[i][0],W[i][1]; mid=(ws+we)/2; st=src2out(ws)
    for o,s_,e_ in tl:
        if s_<=mid*SR<e_ and not (s_<=ws*SR<e_): st=o/SR
    return st, max(st+0.08, src2out(we-0.001))
CH="""0:دايمًا 1:*أمهاتنا 2:كانوا 3:يقولولنا
4:*ماتوطيش 5:*رقبتك 6:قدّام 7:لفترة 8:طويلة
9:ودلوقتي 10:كلنا 11:ماسكين 12:*الموبايل
13:وموطيين 14:رقبتنا 15:بشكل 16:تلقائي 17:*طول 18:*الوقت
19:والاستمرار 20:في 21:*عادة 22:*زي 23:*دي
24:بتخلي 25:*خطوط 26:*وتجاعيد
27:تبتدي 28:تظهر 29:في 30:*الرقبة
31:ومع 32:*إهمال 33:العناية 34:بيها
35:الخطوط 36:دي 37:ممكن 38:*تبان 39:*أكتر
40:وعلشان 41:كده 42:زي 43:ما 44:*بنهتم
45:ببشرة 46:وشنا 47:*مهم 48:*جدًا
49:إننا 50:نهتم 51:بمنطقة 52:*الرقبة
53:بس 54-55:*ماتقلقيش 56:حتى 57:لو
58:الخطوط 59:دي 60:*بدأت 61:*تظهر
62:فيه 63:*إجراءات 64:*تجميلية
65:ممكن 66:تساعد 67:في 68:*تحسين 69:*المظهر 70:بتاعك
71:زي 72:علاجات 73:*تحفيز 74:*الكولاجين 75:وشد 76:الجلد
77:وطبعًا 78:ده 79:*بيختلف 80:من 81:حالة 82:للتانية
83:علشان 84:كده 85:*نصيحتي 86:ليكي
87:إنك 88-89:*ماتنتظريش 90:لحد 91:ما
92:الخطوط 93:*تبان 94:*أكتر
95:*احجزي 96:*استشارتك 97:معانا
98:واعرفي 99:إيه 100:*المناسب 101:*ليكي"""
chunks=[]
for line in CH.splitlines():
    ws=[]
    for tok in line.split():
        r,w=tok.split(":"); a,b=(r.split("-")+[r])[:2]; a,b=int(a),int(b)
        g=w.startswith("*"); w=w.lstrip("*")
        s,_=wt(a); _,e=wt(b); ws.append(dict(w=w,g=g,s=s-0.04,e=e,i0=a,i1=b))
    chunks.append(dict(words=ws,s=ws[0]["s"],le=ws[-1]["e"]))
for k,c in enumerate(chunks):
    nxt=chunks[k+1]["s"] if k+1<len(chunks) else DUR
    c["end"]=min(nxt, c["le"]+0.45) if k+1<len(chunks) else DUR-0.02
chunks[0]["s"]=0; chunks[0]["words"][0]["s"]=0.0
HOLD=0.62
for c in chunks:
    ws_=c["words"]
    for w in ws_: w["s"]=max(c["s"],w["s"]-0.08)          # appear slightly ahead of the voice
    lim=c["end"]-HOLD
    last=ws_[-1]["s"]
    if last>lim and last>c["s"]:
        f=max(0.0,(lim-c["s"]))/(last-c["s"])
        for w in ws_: w["s"]=c["s"]+(w["s"]-c["s"])*f
# ---------------- word sprites with soft drop shadow (no box, no stroke)
PAD=30
def sprite(w,g,size=58):
    f=font(FB if g else FM,size+(2 if g else 0))
    bb=f.getbbox(w,direction="rtl",language="ar")
    tw,th=bb[2]-bb[0],bb[3]-bb[1]
    Wd,Hd=tw+2*PAD,th+2*PAD
    m=Image.new("L",(Wd,Hd),0); ImageDraw.Draw(m).text((PAD-bb[0],PAD-bb[1]),w,font=f,fill=255,direction="rtl",language="ar")
    ma=np.array(m,np.float32)/255
    s1=np.array(m.filter(ImageFilter.GaussianBlur(4)),np.float32)/255
    s2=np.array(m.filter(ImageFilter.GaussianBlur(13)),np.float32)/255
    s1=np.roll(s1,3,0); s2=np.roll(s2,4,0)
    sh=np.clip(s1*0.85+s2*0.55,0,1)
    col=np.array(GOLD if g else CREAM,np.float32)
    a=ma+sh*(1-ma)
    rgb=(col[None,None,:]*ma[...,None]+np.array(SH,np.float32)[None,None,:]*(sh*(1-ma))[...,None])/np.maximum(a,1e-6)[...,None]
    im=Image.fromarray(np.dstack([rgb,a*255]).clip(0,255).astype(np.uint8),"RGBA")
    return im,tw,th,bb
CAP_CY=1290
for c in chunks:
    sp=font(FM,58).getlength(" ")
    for w in c["words"]:
        w["im"],w["tw"],w["th"],w["bb"]=sprite(w["w"],w["g"])
    tot=sum(w["tw"] for w in c["words"])+sp*(len(c["words"])-1)
    lines=[c["words"]]
    if len(c["words"])>=6 or tot>840:
        best=None
        for k in range(1,len(c["words"])):
            a=sum(w["tw"] for w in c["words"][:k]); b=sum(w["tw"] for w in c["words"][k:])
            if c["words"][k-1]["g"] and c["words"][k]["g"]: continue
            if best is None or abs(a-b)<best[0]: best=(abs(a-b),k)
        lines=[c["words"][:best[1]],c["words"][best[1]:]]
    LH=78; y0=CAP_CY-(len(lines)-1)*LH/2
    for li,l in enumerate(lines):
        lw=sum(w["tw"] for w in l)+sp*(len(l)-1); x=WD/2+lw/2
        for w in l:
            w["cx"]=x-w["tw"]/2; w["cy"]=y0+li*LH; x-=w["tw"]+sp
    c["top"]=y0-40
    gws=[w for w in c["words"] if w["g"]]
    if gws:  # underline under the gold phrase, same line only
        l0=[w for w in gws if w["cy"]==gws[0]["cy"]]
        c["ul"]=(min(w["cx"]-w["tw"]/2 for w in l0),max(w["cx"]+w["tw"]/2 for w in l0),l0[0]["cy"]+34,min(w["s"] for w in l0))
# ---------------- line icons (0..100 box) drawn on
def circle(cx,cy,r,a0=0,a1=360,n=64):
    return [(cx+r*math.cos(math.radians(a)),cy+r*math.sin(math.radians(a))) for a in np.linspace(a0,a1,n)]
def rrect(x0,y0,x1,y1,r):
    p=[]
    for cx,cy,a in [(x1-r,y0+r,-90),(x1-r,y1-r,0),(x0+r,y1-r,90),(x0+r,y0+r,180)]:
        p+=circle(cx,cy,r,a,a+90,10)
    return p+[p[0]]
def wave(y,amp=5):
    return [(x,y+amp*math.sin((x-12)/76*2*math.pi*2)) for x in np.linspace(12,88,40)]
def heart():
    pts=[]
    for t in np.linspace(math.pi,3*math.pi,90):
        x=16*math.sin(t)**3; y=-(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))
        pts.append((50+x*2.6,46+y*2.6))
    return [pts]
def star(cx,cy,r,ri=0.28):
    p=[]
    for k in range(9):
        a=k*math.pi/4-math.pi/2; rr=r if k%2==0 else r*ri
        p.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
    return p
def bez(p0,p1,p2,n=30):
    return [((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0],(1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]) for t in np.linspace(0,1,n)]
ICONS={
 "phone":[rrect(30,6,70,94,9),[(43,83),(57,83)]],
 "clock":[circle(50,50,42,-90,270),[(50,50),(50,24)],[(50,50),(69,60)]],
 "wrinkles":[wave(30),wave(50),wave(70)],
 "warning":[[(50,8),(95,88),(5,88),(50,8)],[(50,36),(50,62)],circle(50,74,2.5)],
 "eye":[bez((6,50),(50,8),(94,50))+bez((94,50),(50,92),(6,50)),circle(50,50,15,-90,270)],
 "heart":heart(),
 "shield":[[(50,6),(88,20),(88,46)]+bez((88,46),(84,80),(50,95))+bez((50,95),(16,80),(12,46))+[(12,20),(50,6)],[(33,50),(46,63),(68,38)]],
 "sparkle":[star(42,56,38),star(80,20,15)],
 "drop":[bez((50,5),(28,36),(22,58))+circle(50,62,29,180,360+0,30)[::-1][::-1]+bez((78,58),(72,36),(50,5)),bez((36,64),(38,78),(52,80))],
 "bulb":[circle(50,38,30,135,405),[(29,59),(36,70),(36,80),(64,80),(64,70),(71,59)],[(40,90),(60,90)]],
 "hourglass":[[(20,6),(80,6)],[(20,94),(80,94)],[(28,6),(28,22),(50,50),(28,78),(28,94)],[(72,6),(72,22),(50,50),(72,78),(72,94)]],
 "calendar":[rrect(8,16,92,92,8),[(8,36),(92,36)],[(30,6),(30,24)],[(70,6),(70,24)],[(34,62),(46,74),(68,52)]],
 "lift":[[(22,58),(50,30),(78,58)],[(22,84),(50,56),(78,84)],[(50,30),(50,6)]],
}
# fix drop: simple teardrop
ICONS["drop"]=[bez((50,4),(30,34),(23,56))+circle(50,62,27.5,190,350+0,40)[::-1]+bez((77,56),(70,34),(50,4)),bez((37,62),(37,76),(50,79))]
ICONS["drop"][0]=bez((50,4),(30,34),(23,58))+circle(50,62,27.6,188,-8,50)+bez((77,58),(70,34),(50,4))
ICON_EV=[(24,30,"wrinkles"),(9,12,"phone"),(13,18,"clock"),(32,34,"warning"),(35,39,"eye"),
         (45,52,"heart"),(53,57,"shield"),(62,70,"sparkle"),(71,74,"drop"),(75,76,"lift"),
         (85,86,"bulb"),(87,94,"hourglass"),(95,97,"calendar")]
def chunk_of(i):
    for c in chunks:
        if any(w["i0"]<=i<=w["i1"] for w in c["words"]): return c
icons=[]
for a,b,n in ICON_EV:
    s=wt(a)[0]-0.08; ca=chunk_of(a); cb=chunk_of(b)
    e=cb["end"]
    icons.append(dict(n=n,s=s,e=e,top=min(ca["top"],cb["top"])))
icons.sort(key=lambda d:d['s'])
for k in range(len(icons)-1):  # never overlap
    icons[k]["e"]=min(icons[k]["e"],icons[k+1]["s"])
ISZ=118; SS=3
def draw_icon(name,p,size=ISZ,width=5.0):
    paths=ICONS[name]; L=[sum(math.dist(q[j],q[j+1]) for j in range(len(q)-1)) for q in paths]
    tot=sum(L); left=p*tot; M=24
    im=Image.new("L",((size+2*M)*SS,)*2,0); d=ImageDraw.Draw(im); k=(size/100)*SS
    for q,l in zip(paths,L):
        if left<=0: break
        pts=[(M*SS+x*k,M*SS+y*k) for x,y in q]; acc=0; out=[pts[0]]
        for j in range(len(pts)-1):
            sl=math.dist(q[j],q[j+1])
            if acc+sl<=left: out.append(pts[j+1]); acc+=sl
            else:
                f=(left-acc)/sl if sl else 0
                out.append((pts[j][0]+(pts[j+1][0]-pts[j][0])*f,pts[j][1]+(pts[j+1][1]-pts[j][1])*f)); acc=left; break
        left-=acc
        if len(out)>1:
            d.line(out,fill=255,width=int(width*SS),joint="curve")
            for x,y in (out[0],out[-1]):
                r=width*SS/2; d.ellipse((x-r,y-r,x+r,y+r),fill=255)
    m=im.resize((size+2*M,)*2,Image.LANCZOS)
    ma=np.array(m,np.float32)/255
    sh=np.roll(np.array(m.filter(ImageFilter.GaussianBlur(5)),np.float32)/255,3,0)*0.9
    sh2=np.array(m.filter(ImageFilter.GaussianBlur(16)),np.float32)/255*0.6
    sh=np.clip(sh+sh2,0,1)
    a=ma+sh*(1-ma)
    rgb=(np.array(GOLD,np.float32)*ma[...,None]+np.array(SH,np.float32)*(sh*(1-ma))[...,None])/np.maximum(a,1e-6)[...,None]
    return Image.fromarray(np.dstack([rgb,a*255]).clip(0,255).astype(np.uint8),"RGBA")
ICON_CACHE={}
def icon_full(n):
    if n not in ICON_CACHE: ICON_CACHE[n]=draw_icon(n,1.0)
    return ICON_CACHE[n]
def put(img,lay,cx,cy,alpha=1.0,scale=1.0):
    if alpha<=0.003 or scale<=0.02: return
    if abs(scale-1)>0.004: lay=lay.resize((max(1,int(lay.width*scale)),max(1,int(lay.height*scale))),Image.BICUBIC)
    if alpha<0.999:
        a=np.array(lay); a[...,3]=(a[...,3]*alpha).astype(np.uint8); lay=Image.fromarray(a)
    img.alpha_composite(lay,(int(round(cx-lay.width/2)),int(round(cy-lay.height/2))))
def sparkle_img(r,a):
    im=Image.new("RGBA",(int(r*2+6),)*2,(0,0,0,0)); c=im.width/2
    ImageDraw.Draw(im).polygon(star(c,c,r,0.2),fill=GOLD+(int(255*a),)); return im
# ---------------- camera: slow push + smooth emphasis + eased cut transitions
CUTS=[o/SR for o,_,_ in tl[1:]]
KINDS=["flash","zoom","blur","flash","zoom","dissolve","blur","zoom","flash"]
TR={c:KINDS[i%len(KINDS)] for i,c in enumerate(CUTS)}
BIG=set()
EMPH=[]
for c in chunks:
    if any(w["g"] for w in c["words"]) and c is not chunks[0]:
        pass
EMPH_IDX=[24,4,13,47,63,73,85,95]   # punch-in on these phrases
for i in EMPH_IDX:
    c=chunk_of(i); EMPH.append((wt(i)[0]-0.1,c["end"]))
def seg_bounds(t):
    a=0; 
    for c in CUTS:
        if t>=c: a=c
    b=DUR
    for c in CUTS:
        if c>t: b=c; break
    return a,b
def zoom(t):
    z=1.0+0.035*(0.5-0.5*math.cos(2*math.pi*t/9.0))   # slow breathing push (kept)
    for s_,e_ in EMPH:
        z+=0.075*eio((t-s_)/0.4)*(1-eio((t-(e_-0.05))/0.4))
    for c,k in TR.items():   # gentle zoom-through: rises into the cut and settles after, no jumps
        if k=="zoom":
            if c-0.3<=t<c: z+=0.045*eio((t-(c-0.3))/0.3)
            elif c<=t<c+0.4: z+=0.045*(1-eio((t-c)/0.4))
    return z
HALF={"flash":0.09,"zoom":0.1,"blur":0.14,"dissolve":0.1}
XF={c:HALF[k] for c,k in TR.items()}
def blur_at(t):
    for c,k in TR.items():
        h=XF[c]
        if k in("blur","zoom") and abs(t-c)<h: return (0.45 if k=="blur" else 0.2)*eio(1-abs(t-c)/h)
    return 0
def flash_at(t):
    for c,k in TR.items():
        if k=="flash" and abs(t-c)<0.16: return 0.2*eio(1-abs(t-c)/0.16)
    return 0
AX,AY=540,560
def frame_zoom(fr,z,bl):
    im=Image.fromarray(fr)
    def crop(zz):
        cw,ch=WD/zz,HT/zz; x0=AX-AX/zz; y0=AY-AY/zz
        return np.asarray(im.resize((WD,HT),Image.BICUBIC,box=(x0,y0,x0+cw,y0+ch)),np.float32)
    if bl<0.02: return Image.fromarray(crop(z).astype(np.uint8))
    acc=np.zeros((HT,WD,3),np.float32); n=7
    for k in range(n): acc+=crop(z*(1+0.03*bl*k))
    return Image.fromarray((acc/n).astype(np.uint8))
class Reader:
    def __init__(s): s.p=None; s.idx=-1
    def get(s,fi):
        if s.p is None or fi<s.idx or fi>s.idx+30:
            if s.p: s.p.kill()
            s.p=subprocess.Popen(["ffmpeg","-v","error","-ss",f"{fi/25:.4f}","-i",f"{S}/src/vid.mp4","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE,bufsize=10**8); s.idx=fi-1
        while s.idx<fi:
            s.fr=np.frombuffer(s.p.stdout.read(WD*HT*3),np.uint8).reshape(HT,WD,3); s.idx+=1
        return s.fr
R=Reader(); R2=Reader()
# ---------------- end name
def name_layer(size=36,track=0.22,line_len=60,y=1415):
    SS=3; f=ImageFont.truetype(FM,size*SS); name="DR. MARWA MAGDY"
    adv=[f.getlength(c) for c in name]; tr=size*SS*track; nw=sum(adv)+tr*(len(name)-1)
    gap=18*SS; ih=size*SS; iw=ih*0.55
    L=Image.new("RGBA",(WD*SS,160*SS),(0,0,0,0)); d=ImageDraw.Draw(L)
    bb=f.getbbox("M"); cy=80*SS
    total=nw+2*(line_len*SS+gap); tx=WD*SS/2-total/2
    d.line((tx,cy,tx+line_len*SS,cy),fill=GOLD+(255,),width=int(1.5*SS)); tx+=line_len*SS+gap
    ty=cy-(bb[1]+bb[3])/2
    for c,a_ in zip(name,adv): d.text((tx,ty),c,font=f,fill=BEIGE+(255,)); tx+=a_+tr
    tx+=gap-tr
    d.line((tx,cy,tx+line_len*SS,cy),fill=GOLD+(255,),width=int(1.5*SS))
    L=L.resize((WD,160),Image.LANCZOS)
    a=L.split()[3]
    s1=np.roll(np.array(a.filter(ImageFilter.GaussianBlur(3)),np.float32),2,0); s2=np.array(a.filter(ImageFilter.GaussianBlur(14)),np.float32)
    sh=np.clip(s1*0.95+s2*0.75,0,255)
    out=Image.fromarray(np.dstack([np.full(sh.shape+(3,),SH,np.uint8),sh.astype(np.uint8)]),"RGBA"); out.alpha_composite(L)
    return out
NAME_L=name_layer(); NAME_Y=1415; NAME_IN=0.3; NAME_OUT=6.2
def draw_name(img,t):
    if not (NAME_IN<=t<NAME_OUT): return
    p=t-NAME_IN; fo=1-eio((t-(NAME_OUT-0.5))/0.5)
    q=eo(p/0.7)                                   # reveal from the centre outward
    arr=np.array(NAME_L); half=int(WD/2*q)
    arr[:,:max(0,WD//2-half),3]=0; arr[:,WD//2+half:,3]=0
    arr[...,3]=(arr[...,3]*clamp(p/0.35)*fo).astype(np.uint8)
    img.alpha_composite(Image.fromarray(arr),(0,int(NAME_Y-80+6*(1-eo(p/0.5))-4*(1-fo))))
# ---------------- render
NF=int(round(DUR*FPS))
if not PREVIEW:
    np.concatenate([A[s:e] for s,e in segs]).astype(np.float32).tofile(f"{S}/mix.f32")
    enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{WD}x{HT}","-r",str(FPS),"-i","-",
        "-f","f32le","-ar",str(SR),"-ac","2","-i",f"{S}/mix.f32","-c:v","libx264","-preset","slow","-crf","16","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","320k","-movflags","+faststart","-shortest",OUT],stdin=subprocess.PIPE)
frames=range(NF) if not PREVIEW else [int(float(x)*FPS) for x in PREVIEW.split(",")]
for fk in frames:
    t=fk/FPS; ts=out2src(t+0.5/FPS); fi=min(int(ts*25),1033)
    z=zoom(t); fr=R.get(fi)
    for c,h in XF.items():
        if c-h<=t<c+h:
            k=[i for i,(o,_,_) in enumerate(tl) if abs(o/SR-c)<1e-6][0]
            if t<c: other=tl[k][1]/SR+(t-c)          # incoming shot, slightly before its start
            else:   other=tl[k-1][2]/SR+(t-c)        # outgoing shot, slightly past its end
            fr2=R2.get(min(max(int(other*25),0),1033))
            w=0.5+0.5*((t-c)/h)  # weight of incoming
            w=eio(w); wi=w if t>=c else w; 
            wa=(1-w) if t>=c else w  # weight of the 'other' frame
            fr=(fr.astype(np.float32)*(1-wa)+fr2.astype(np.float32)*wa).astype(np.uint8)
    bl=blur_at(t)
    if bl>0.01:
        sm=Image.fromarray(fr).resize((WD//10,HT//10),Image.BILINEAR).filter(ImageFilter.GaussianBlur(2.2)).resize((WD,HT),Image.BICUBIC)
        fr=(fr.astype(np.float32)*(1-bl)+np.asarray(sm,np.float32)*bl).astype(np.uint8)
    fl=flash_at(t)
    if fl>0.005:
        fr=(fr.astype(np.float32)*(1-fl)+np.array(CREAM,np.float32)*fl).astype(np.uint8)
    img=frame_zoom(fr,z,0).convert("RGBA")
    # icons
    for ic in icons:
        if ic["s"]<=t<ic["e"]:
            p=t-ic["s"]; out=clamp((t-(ic["e"]-0.18))/0.18)
            cy=ic["top"]-ISZ/2-28
            dp=eo(p/0.55)
            lay=icon_full(ic["n"]) if dp>=0.999 else draw_icon(ic["n"],dp)
            sc=(0.6+0.4*eback(p/0.4))*(1-0.15*out)
            put(img,lay,WD/2,cy-10*out,alpha=clamp(p/0.12)*(1-out),scale=sc)
            if p<0.7:   # tiny sparkle burst
                for k,ang in enumerate((-35,215,95)):
                    q=eo(p/0.7); r=ISZ*0.55+40*q
                    put(img,sparkle_img(9+4*(k==0),1),WD/2+r*math.cos(math.radians(ang)),cy-r*math.sin(math.radians(ang))*0.8,alpha=(1-q)*clamp(p/0.1))
    # captions (word-by-word)
    for c in chunks:
        if not (c["s"]<=t<c["end"]): continue
        out=clamp((t-(c["end"]-0.1))/0.1)
        for w in c["words"]:
            p=(t-w["s"])/0.18
            if p<=0: continue
            if w["g"]: sc=1.18-0.18*eo(p); dy=0
            else: sc=0.85+0.15*eback(p,1.3); dy=22*(1-eo(p))
            put(img,w["im"],w["cx"],w["cy"]+dy-12*eo(out),alpha=clamp(p*1.8)*(1-out),scale=sc*(1-0.06*out))
        if False:
            x0,x1,y,s=c["ul"]; q=eo((t-s-0.18)/0.3)
            if q>0:
                d=ImageDraw.Draw(img); xs=x1-(x1-x0)*q
                a=int(255*(1-out))
                d.line((xs,y,x1,y),fill=GOLD+(a,),width=3)
    draw_name(img,t)
    o=img.convert("RGB")
    if PREVIEW: o.save(f"{S}/prev7/p_{t:06.2f}.png")
    else: enc.stdin.write(o.tobytes())
if not PREVIEW: enc.stdin.close(); enc.wait()
def T(x):
    ms=int(round(x*1000)); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
with open(f"{S}/captions3.srt","w",encoding="utf-8") as f:
    for k,c in enumerate(chunks): f.write(f"{k+1}\n{T(c['s'])} --> {T(c['end'])}\n{' '.join(w['w'] for w in c['words'])}\n\n")
for c in chunks: print(f"{c['s']:6.2f}-{c['end']:6.2f} last word fully on {c['end']-0.1-(c["words"][-1]["s"]+0.18):.2f}s", c['words'][-1]['w'])
print("icons",[(i['n'],round(i['s'],2),round(i['e'],2)) for i in icons])
