import sys, subprocess, numpy as np, math
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, sys.argv[1] if len(sys.argv)>1 else ".")
from plan import *
OUT=sys.argv[2] if len(sys.argv)>2 else f"{S}/out.mp4"
PREVIEW=sys.argv[3] if len(sys.argv)>3 else None
WD,HT,FPS=1080,1920,30
CREAM=(0xF8,0xEE,0xDC); GOLD=(0xE9,0xB8,0x72); BEIGE=(0xF0,0xD9,0xB3); SHADOW=(52,28,12)
FM=f"{S}/fonts/EM500.ttf"; FB=f"{S}/fonts/EM700.ttf"
def font(p,s): return ImageFont.truetype(p,s,layout_engine=ImageFont.Layout.RAQM)

# ---------- captions: (first word idx, last word idx, text, gold phrase)
CH=[
 (19,23,"والاستمرار في عادة زي دي","عادة زي دي"),
 (24,26,"بتخلي خطوط وتجاعيد","خطوط وتجاعيد"),
 (27,30,"تبتدي تظهر في الرقبة","الرقبة"),
 (0,3,"دايمًا أمهاتنا كانوا يقولولنا","أمهاتنا"),
 (4,8,"ماتوطيش رقبتك قدّام لفترة طويلة","ماتوطيش رقبتك"),
 (9,12,"ودلوقتي كلنا ماسكين الموبايل","الموبايل"),
 (13,18,"وموطيين رقبتنا بشكل تلقائي طول الوقت","طول الوقت"),
 (31,34,"ومع إهمال العناية بيها","إهمال"),
 (35,39,"الخطوط دي ممكن تبان أكتر","تبان أكتر"),
 (40,44,"وعلشان كده زي ما بنهتم","بنهتم"),
 (45,48,"ببشرة وشنا مهم جدًا","مهم جدًا"),
 (49,52,"إننا نهتم بمنطقة الرقبة","الرقبة"),
 (53,57,"بس ماتقلقيش حتى لو","ماتقلقيش"),
 (58,61,"الخطوط دي بدأت تظهر","بدأت تظهر"),
 (62,64,"فيه إجراءات تجميلية","إجراءات تجميلية"),
 (65,70,"ممكن تساعد في تحسين المظهر بتاعك","تحسين المظهر"),
 (71,76,"زي علاجات تحفيز الكولاجين وشد الجلد","تحفيز الكولاجين"),
 (77,82,"وطبعًا ده بيختلف من حالة للتانية","بيختلف"),
 (83,86,"علشان كده نصيحتي ليكي","نصيحتي"),
 (87,91,"إنك ماتنتظريش لحد ما","ماتنتظريش"),
 (92,94,"الخطوط تبان أكتر","تبان أكتر"),
 (95,97,"احجزي استشارتك معانا","احجزي استشارتك"),
 (98,101,"واعرفي إيه المناسب ليكي","المناسب ليكي"),
]
caps=[]
for i,(a,b,txt,kw) in enumerate(CH):
    ws,we=W[a][0],W[a][1]; mid=(ws+we)/2
    st0=src2out(ws)
    # clamp to the start of the piece containing the word middle
    for o,s_,e_ in tl:
        if s_<=mid*SR<e_ and not (s_<=ws*SR<e_): st0=o/SR
    st=0.0 if i==0 else max(0,st0-0.05)
    caps.append([st,None,txt,kw,a,b])
for i in range(len(caps)):
    caps[i][1]=caps[i+1][0] if i+1<len(caps) and abs(caps[i+1][0]-src2out(W[caps[i][5]][1]))<0.6 else src2out(W[caps[i][5]][1])+0.35
    if caps[i][0]>=caps[i][1]: raise SystemExit(f"bad cap {caps[i]}")
DUR=TOTAL/SR
caps[-1][1]=DUR
def cstart(idx): return [c[0] for c in caps if c[4]==idx][0]
ZOOM=[(0,1.0),(cstart(24),1.1),(4.235,1.0),(6.049,1.1),(8.879,1.0),(10.379,1.1),(13.119,1.0),
      (cstart(35),1.1),(cstart(40),1.0),(cstart(45),1.1),(cstart(53),1.0),(22.515,1.1),(24.445,1.0),
      (cstart(71),1.1),(30.795,1.0),(33.624,1.1),(cstart(95),1.0)]
# snap to cut times exactly where given in plan
def zoom_at(t):
    z=1.0
    for a,s in ZOOM:
        if t+1e-6>=a: z=s
    return z

# ---------- drawing helpers
def glow(w,h,rx,ry,amax=0.86,inner=0.45):
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    d=np.sqrt(((xx-w/2)/rx)**2+((yy-h/2)/ry)**2)
    x=np.clip((d-inner)/(1-inner),0,1); s=1-(x*x*(3-2*x))
    return (s*amax)
def rgba_layer(w,h): return Image.new("RGBA",(w,h),(0,0,0,0))
def text_runs(txt,kw):
    """split text into runs [(str,color)] with kw gold"""
    i=txt.find(kw) if kw else -1
    if i<0: return [(txt,CREAM)]
    r=[]
    if txt[:i].strip(): r.append((txt[:i].strip(),CREAM))
    r.append((kw,GOLD))
    if txt[i+len(kw):].strip(): r.append((txt[i+len(kw):].strip(),CREAM))
    return r
def layout_line(words, size):
    """words: [(w,color,bold)] RTL; returns image of the line"""
    fs={b:font(FB if b else FM,size) for b in (0,1)}
    sp=fs[0].getlength(" ")
    widths=[fs[b].getlength(w) for w,c,b in words]
    tw=int(sum(widths)+sp*(len(words)-1))+4
    asc,desc=fs[0].getmetrics(); lh=asc+desc
    im=rgba_layer(tw,lh+20); d=ImageDraw.Draw(im)
    x=tw-2
    for (w,c,b),wd in zip(words,widths):
        x-=wd; d.text((x,10),w,font=fs[b],fill=c+(255,),direction="rtl",language="ar"); x-=sp
    return im
def caption_img(txt,kw,size=56):
    words=[]
    for run,c in text_runs(txt,kw):
        for w in run.split(): words.append((w,c,1 if c==GOLD else 0))
    lines=[words]
    f=font(FM,size)
    if len(words)>=6 or f.getlength(txt)>840:
        best=None
        for k in range(1,len(words)):
            a=f.getlength(" ".join(w for w,_,_ in words[:k])); b=f.getlength(" ".join(w for w,_,_ in words[k:]))
            # don't split the gold phrase
            if words[k-1][1]==GOLD and words[k][1]==GOLD: continue
            sc=abs(a-b)
            if best is None or sc<best[0]: best=(sc,k)
        k=best[1]; lines=[words[:k],words[k:]]
    ims=[layout_line(l,size) for l in lines]
    gap=-44
    w=max(i.width for i in ims); h=sum(i.height for i in ims)+gap*(len(ims)-1)
    im=rgba_layer(w,h); y=0
    for i in ims: im.alpha_composite(i,((w-i.width)//2,y)); y+=i.height+gap
    return im
def split_glow(im,padx=170,pady=110,amax=0.86):
    W2,H2=im.width+2*padx,im.height+2*pady
    g=glow(W2,H2,im.width/2+padx*0.95,im.height/2+pady*0.95,amax)
    base=np.zeros((H2,W2,4),np.float32); base[...,:3]=SHADOW; base[...,3]=g*255
    t=rgba_layer(W2,H2); t.alpha_composite(im,(padx,pady))
    return Image.fromarray(base.astype(np.uint8),"RGBA"),t
def with_glow(im,padx=170,pady=110,amax=0.86):
    W2,H2=im.width+2*padx,im.height+2*pady
    g=glow(W2,H2,im.width/2+padx*0.95,im.height/2+pady*0.95,amax)
    base=np.zeros((H2,W2,4),np.float32); base[...,:3]=SHADOW; base[...,3]=g*255
    out=Image.fromarray(base.astype(np.uint8),"RGBA"); out.alpha_composite(im,(padx,pady))
    return out
def sparkle(d,cx,cy,r,col):
    pts=[]
    for k in range(8):
        ang=k*math.pi/4-math.pi/2; rr=r if k%2==0 else r*0.18
        pts.append((cx+rr*math.cos(ang),cy+rr*math.sin(ang)))
    d.polygon(pts,fill=col)
def phone_icon(d,cx,cy,h,col,wid=2):
    w=h*0.55
    d.rounded_rectangle((cx-w/2,cy-h/2,cx+w/2,cy+h/2),radius=h*0.14,outline=col,width=wid)
    d.line((cx-w*0.16,cy+h*0.33,cx+w*0.16,cy+h*0.33),fill=col,width=wid)
def name_row(size=27, track=0.42, line_len=78, icon=True):
    f=font(FM,size); name="DR. MARWA MAGDY"
    adv=[f.getlength(c) for c in name]; tr=size*track
    nw=sum(adv)+tr*(len(name)-1)
    gap=26; ih=size*1.05; iw=ih*0.55
    total=line_len+gap+nw+(gap+iw if icon else 0)+gap+line_len
    S2=3  # supersample for crisp thin lines
    im=rgba_layer(int((total+8)*S2),int(size*2*S2)); d=ImageDraw.Draw(im)
    cy=im.height/2; x=4*S2
    d.line((x,cy,x+line_len*S2,cy),fill=GOLD+(255,),width=int(1.6*S2)); x+=(line_len+gap)*S2
    fS=font(FM,size*S2); asc,_=fS.getmetrics(); bb=fS.getbbox("M")
    ty=cy-(bb[1]+bb[3])/2
    for c,a in zip(name,adv):
        d.text((x,ty),c,font=fS,fill=BEIGE+(255,)); x+=(a+tr)*S2
    x+=(gap-tr)*S2
    if icon:
        phone_icon(d,x+iw*S2/2,cy,ih*S2,GOLD+(255,),wid=int(1.7*S2)); x+=(iw+gap)*S2
    d.line((x,cy,x+line_len*S2,cy),fill=GOLD+(255,),width=int(1.6*S2))
    return im.resize((im.width//S2,im.height//S2),Image.LANCZOS)
def title_block():
    l1=layout_line([(w,CREAM,0) for w in "ماما دايما تقولك".split()],46)
    l2=layout_line([(w,GOLD,1) for w in "ماتوطيش رقبتك".split()],96)
    l3=layout_line([(w,CREAM,0) for w in "وانتي ماسكة الموبايل".split()],48)
    nm=name_row()
    parts=[(l1,0),(l2,-34),(l3,-30),(nm,6)]
    w=max(p.width for p,_ in parts); h=sum(p.height+g for p,g in parts)
    im=rgba_layer(w,h); y=0
    for p,g in parts: y+=g; im.alpha_composite(p,((w-p.width)//2,y)); y+=p.height
    return im
TITLE=with_glow(title_block(),padx=200,pady=140,amax=0.88)
NAME_END=with_glow(name_row(size=30,line_len=90),padx=150,pady=70,amax=0.84)
CAPS=[split_glow(caption_img(c[2],c[3])) for c in caps]
# title placement (like the cover: block centred around y≈960)
TX=(WD-TITLE.width)//2; TY=955-TITLE.height//2
CAP_CY=1325  # caption centre; bottom of text stays above 1450
for c,im in zip(caps,CAPS):
    pass
SPARKS=[(-335,-112,21,0.0),(-358,-62,11,0.9),(312,-165,13,1.7)]  # relative to title text centre (x), name of offsets
TITLE_END=4.235
def ease(x): x=min(max(x,0),1); return x*x*(3-2*x)

class Reader:
    def __init__(s): s.p=None; s.idx=-1; s.frame=None
    def open(s,fi):
        if s.p: s.p.kill()
        t=fi/25
        s.p=subprocess.Popen(["ffmpeg","-v","error","-ss",f"{t:.4f}","-i",f"{S}/src/vid.mp4","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE,bufsize=10**8)
        s.idx=fi-1
    def get(s,fi):
        if s.p is None or fi<s.idx or fi>s.idx+30: s.open(fi)
        while s.idx<fi:
            b=s.p.stdout.read(WD*HT*3); s.idx+=1
            s.frame=np.frombuffer(b,np.uint8).reshape(HT,WD,3)
        return s.frame
R=Reader()
AX,AY=540,560  # punch-in anchor (face)
def zoomed(fr,z):
    if z==1.0: return Image.fromarray(fr)
    cw,ch=WD/z,HT/z; x0=AX-AX/z; y0=AY-AY/z
    return Image.fromarray(fr).resize((WD,HT),Image.BICUBIC,box=(x0,y0,x0+cw,y0+ch))
def paste(img,lay,x,y,a):
    if a<=0: return
    if a<1:
        arr=np.array(lay); arr[...,3]=(arr[...,3]*a).astype(np.uint8); lay=Image.fromarray(arr)
    img.alpha_composite(lay,(int(x),int(y)))
NF=int(round(DUR*FPS))
enc=None
if not PREVIEW:
    enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{WD}x{HT}","-r",str(FPS),"-i","-",
        "-f","f32le","-ar",str(SR),"-ac","2","-i",f"{S}/mix.f32",
        "-c:v","libx264","-preset","slow","-crf","16","-pix_fmt","yuv420p","-profile:v","high","-r",str(FPS),
        "-c:a","aac","-b:a","320k","-movflags","+faststart","-shortest",OUT],stdin=subprocess.PIPE)
    # audio: exact concatenation of source samples, untouched
    np.concatenate([A[s:e] for s,e in segs]).astype(np.float32).tofile(f"{S}/mix.f32")
frames=range(NF) if not PREVIEW else [int(float(x)*FPS) for x in PREVIEW.split(",")]
for k in frames:
    t=k/FPS; ts=out2src(t+0.5/FPS)
    fi=min(int(ts*25),1033)
    img=zoomed(R.get(fi),zoom_at(t)).convert("RGBA")
    # title (hook)
    if t<TITLE_END:
        a=1.0-ease((t-(TITLE_END-0.3))/0.3)
        paste(img,TITLE,TX,TY,a)
        d=ImageDraw.Draw(img)
        cxt=WD/2; cyt=TY+TITLE.height/2
        for dx,dy,r,ph in SPARKS:
            tw=0.82+0.18*math.sin(2*math.pi*(t*0.9+ph/3))
            sp=rgba_layer(80,80); sparkle(ImageDraw.Draw(sp),40,40,r*tw,GOLD+(int(255*a*(0.75+0.25*tw)),))
            img.alpha_composite(sp,(int(cxt+dx-40),int(cyt+dy-40)))
    # end name
    if t>DUR-2.0:
        a=ease((t-(DUR-2.0))/0.35)
        paste(img,NAME_END,(WD-NAME_END.width)//2,1150-NAME_END.height//2,a)
    # captions
    for i,(c,(gl,tx)) in enumerate(zip(caps,CAPS)):
        if c[0]<=t<c[1]:
            p=ease((t-c[0])/0.14)
            cont=i>0 and abs(caps[i-1][1]-c[0])<0.02
            paste(img,gl,(WD-gl.width)/2,CAP_CY-gl.height/2,1.0 if cont else p)
            sc=0.95+0.05*p
            lay=tx if sc>=0.999 else tx.resize((int(tx.width*sc),int(tx.height*sc)),Image.BICUBIC)
            paste(img,lay,(WD-lay.width)/2,CAP_CY-lay.height/2,p)
    out=img.convert("RGB")
    if PREVIEW: out.save(f"{S}/prev2/p_{t:06.2f}.png")
    else: enc.stdin.write(out.tobytes())
if enc: enc.stdin.close(); enc.wait()
# srt + caption table
def ts_(x):
    ms=int(round(x*1000)); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
with open(f"{S}/captions.srt","w",encoding="utf-8") as f:
    for i,c in enumerate(caps): f.write(f"{i+1}\n{ts_(c[0])} --> {ts_(c[1])}\n{c[2]}\n\n")
print("frames",NF,"dur",DUR)
for c in caps: print(f"{c[0]:6.2f}-{c[1]:6.2f} {c[2]}")
