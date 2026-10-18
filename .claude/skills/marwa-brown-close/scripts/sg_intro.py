"""Saber Group credit for the first 5 s of every reel — matches the agency's reference layout:
   CREATED BY (Montserrat ExtraBold) / SABERGROUPSTUDIO © (Montserrat Medium) / square logo, white, bottom centre.
usage: python3 sg_intro.py <in.mp4> <out.mp4> [--top 1622] [--only5] [--color FFFFFF] [--fonts DIR]
       python3 sg_intro.py --still <frame.png> <out.png>      (static preview of the finished block)
The logo PNG is used as-is: never recolour or re-layout it."""
import sys,os,subprocess,numpy as np,argparse
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ap=argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--top",type=int,default=1622,help="top of the CREATED BY capitals")
ap.add_argument("--corner",choices=["bottom","tr"],default="bottom",help="tr = top-right corner (wide shots where her legs show)")
ap.add_argument("--only5",action="store_true"); ap.add_argument("--still",action="store_true")
ap.add_argument("--fonts",default=os.environ.get("FONTS","fonts")); ap.add_argument("--color",default="FFFFFF")
a=ap.parse_args()
HERE=os.path.dirname(os.path.abspath(__file__)); ASSETS=os.path.join(HERE,"..","assets")
WD,HT,FPS=1080,1920,30; TXT=tuple(int(a.color[i:i+2],16) for i in (0,2,4)); SH=(0,0,0)
# proportions measured from the reference (scaled to a 1080-wide frame)
CAP1,W1,CAP2,GAP12,GAP2L,LOGO=16,161,13,10,6,152
IN_T,OUT_T=0.15,5.0
def clamp(x): return max(0.0,min(1.0,x))
def eo(x): x=clamp(x); return 1-(1-x)**3
def eio(x): x=clamp(x); return x*x*(3-2*x)
def shadow(im,r=4,op=0.45,dy=2):
    al=np.roll(np.array(im.split()[3].filter(ImageFilter.GaussianBlur(r)),np.float32)*op,dy,0)
    s=Image.fromarray(np.dstack([np.full(al.shape+(3,),SH,np.uint8),al.astype(np.uint8)]),"RGBA"); s.alpha_composite(im); return s
def fit(path,text,cap,width=None):
    f=ImageFont.truetype(path,20); bb=f.getbbox("H"); f=ImageFont.truetype(path,max(6,round(20*cap/(bb[3]-bb[1]))))
    w=f.getlength(text); tr=0 if width is None else (width-w)/(len(text)-1)
    return f,tr,w+tr*(len(text)-1)
f1,tr1,w1=fit(f"{a.fonts}/MontserratXB.ttf","CREATED BY",CAP1,W1)
f2,tr2,w2=fit(f"{a.fonts}/MontserratM.ttf","SABERGROUPSTUDIO ©",CAP2)
def glyphs(text,f,tr):
    out=[];x=0
    for c in text:
        w=f.getlength(c)
        if c!=" ":
            m=Image.new("RGBA",(int(w)+16,f.size*2),(0,0,0,0)); ImageDraw.Draw(m).text((8,f.size*1.4),c,font=f,fill=TXT+(255,),anchor="ls")
            out.append((shadow(m),x+w/2))
        x+=w+tr
    return out
G1=glyphs("CREATED BY",f1,tr1)
L2=Image.new("RGBA",(int(w2)+24,f2.size*2),(0,0,0,0)); ImageDraw.Draw(L2).text((12,f2.size*1.4),"SABERGROUPSTUDIO ©",font=f2,fill=TXT+(255,),anchor="ls"); L2=shadow(L2)
def load_logo(size):
    """scale the logo without losing its thin outer red frame: draw at 4x, keep the frame's own position
    (outer edge of the canvas, 1.5/1104 inset) but never thinner than 1 final pixel, then downsample"""
    src=Image.open(os.path.join(ASSETS,"saber-group-vertical.png")).convert("RGBA")
    big=src.resize((size*4,size*4),Image.LANCZOS); d=ImageDraw.Draw(big)
    sw=max(4,round(size*4*3/1104)); inset=round(size*4*1.5/1104)
    d.rectangle((inset,inset,size*4-1-inset,size*4-1-inset),outline=(0xE4,0x2E,0x2B,255),width=sw)
    return big.resize((size,size),Image.LANCZOS)
logo=load_logo(LOGO)
LOGO_L=shadow(logo,6,0.35,3)
CX=WD/2
if a.corner=="tr":   # block keeps its own centre line, tucked into the top-right corner under Instagram's top bar
    CX=WD-56-max(W1,w2,LOGO)/2
    if a.top==1622: a.top=56
B1=a.top+CAP1; B2=B1+GAP12+CAP2; LT=B2+GAP2L          # baselines and logo top
def put(img,lay,cx,cy_base,al=1.0,sc=1.0,clipx=None,base_off=None):
    if al<=0.004: return
    if abs(sc-1)>0.003: lay=lay.resize((max(1,int(lay.width*sc)),max(1,int(lay.height*sc))),Image.BICUBIC)
    arr=np.array(lay); arr[...,3]=(arr[...,3]*al).astype(np.uint8)
    if clipx is not None:
        half=int(arr.shape[1]/2*clipx); c=arr.shape[1]//2; arr[:,:max(0,c-half),3]=0; arr[:,c+half:,3]=0
    oy=base_off if base_off is not None else lay.height/2
    img.alpha_composite(Image.fromarray(arr),(int(round(cx-lay.width/2)),int(round(cy_base-oy*sc))))
def draw(img,t):
    if t>=OUT_T: return
    out=eio((t-(OUT_T-0.6))/0.6); fo=1-out; dy=8*out; p=t-IN_T
    x0=CX-w1/2
    for k,(m,cx) in enumerate(G1):
        q=eo((p-k*0.035)/0.35)
        put(img,m,x0+cx,B1+dy+10*(1-q),al=q*fo,base_off=m.height*0.7)
    q=eo((p-0.4)/0.45); put(img,L2,CX,B2+dy+8*(1-q),al=q*fo,base_off=L2.height*0.7)
    q=eo((p-0.7)/0.6); put(img,LOGO_L,CX,LT+dy+LOGO_L.height/2,al=clamp(q*1.5)*fo,sc=0.94+0.06*q,clipx=q)
if __name__=="__main__":
    if a.still:
        im=Image.open(a.inp).convert("RGBA").resize((WD,HT)); draw(im,2.5); im.convert("RGB").save(a.out); sys.exit()
    dur=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",a.inp],capture_output=True,text=True).stdout)
    if a.only5: dur=min(dur,5.0)
    dec=subprocess.Popen(["ffmpeg","-v","error","-i",a.inp,"-t",f"{dur}","-vf",f"scale={WD}:{HT},fps={FPS}","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
    enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{WD}x{HT}","-r",str(FPS),"-i","-","-i",a.inp,"-t",f"{dur}",
        "-map","0:v","-map","1:a","-c:v","libx264","-preset","slow","-crf","16","-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart","-shortest",a.out],stdin=subprocess.PIPE)
    k=0
    while True:
        b=dec.stdout.read(WD*HT*3)
        if len(b)<WD*HT*3: break
        t=k/FPS
        if t<OUT_T:
            im=Image.frombytes("RGB",(WD,HT),b).convert("RGBA"); draw(im,t); b=im.convert("RGB").tobytes()
        enc.stdin.write(b); k+=1
    enc.stdin.close(); enc.wait(); print("frames",k)
