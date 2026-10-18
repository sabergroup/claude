"""Saber Group credit for the first 5 s of every reel:  ■ CREATED BY / sabergroupstudios © / logo.
usage: python3 sg_intro.py <in.mp4> <out.mp4> [--top 1490] [--only5]  (square logo under the name)   (logo PNG used as-is: no recolour, no re-layout)"""
import sys,os,subprocess,numpy as np,math,argparse
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ap=argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--top",type=int,default=1490)   # bottom area, under the doctor's name
ap.add_argument("--only5",action="store_true"); ap.add_argument("--fonts",default=os.environ.get("FONTS","fonts"))
ap.add_argument("--logo_w",type=int,default=175); ap.add_argument("--logo",default="saber-group-vertical.png"); ap.add_argument("--color",default="F8EEDC",help="text colour per video background (default cream)"); a=ap.parse_args()
HERE=os.path.dirname(os.path.abspath(__file__)); ASSETS=os.path.join(HERE,"..","assets")
WD,HT,FPS=1080,1920,30; RED=(0xE4,0x2E,0x2B); TXT=tuple(int(a.color[i:i+2],16) for i in (0,2,4)); SH=(30,15,8)
IN_T,OUT_T=0.15,5.0
def clamp(x): return max(0.0,min(1.0,x))
def eo(x): x=clamp(x); return 1-(1-x)**3
def eio(x): x=clamp(x); return x*x*(3-2*x)
def shadow(im,r=6,op=0.7,dy=2):
    al=np.array(im.split()[3].filter(ImageFilter.GaussianBlur(r)),np.float32)*op
    al=np.roll(al,dy,0); s=Image.fromarray(np.dstack([np.full(al.shape+(3,),SH,np.uint8),al.astype(np.uint8)]),"RGBA"); s.alpha_composite(im); return s
# --- pieces
fB=ImageFont.truetype(f"{a.fonts}/BebasNeue.ttf",36); fO=ImageFont.truetype(f"{a.fonts}/Oswald300.ttf",29)
def letters(text,font,track):
    out=[]; x=0
    for c in text:
        w=font.getlength(c)
        if c!=" ":
            m=Image.new("RGBA",(int(w)+40,font.size*2),(0,0,0,0)); ImageDraw.Draw(m).text((20,font.size*0.3),c,font=font,fill=TXT+(255,))
            out.append((shadow(m),x+w/2))
        x+=w+track
    return out,x-track
L1,w1=letters("CREATED BY",fB,36*0.22)
SQ=16; GAP=14; row1_w=SQ+GAP+w1
L2=Image.new("RGBA",(700,80),(0,0,0,0)); d=ImageDraw.Draw(L2)
t2="sabergroupstudios ©"; w2=fO.getlength(t2)+0.06*29*(len(t2)-1)
x=(700-w2)/2
for c in t2: d.text((x,14),c,font=fO,fill=TXT+(235,)); x+=fO.getlength(c)+0.06*29
L2=shadow(L2)
logo=Image.open(os.path.join(ASSETS,a.logo)).convert("RGBA")
lh=int(logo.height*a.logo_w/logo.width); LOGO=shadow(logo.resize((a.logo_w,lh),Image.LANCZOS),r=10,op=0.55,dy=4)
Y1=a.top; Y2=Y1+42; Y3=Y2+40
def put(img,lay,cx,cy,al=1.0,sc=1.0,clipx=None):
    if al<=0.004: return
    if abs(sc-1)>0.003: lay=lay.resize((max(1,int(lay.width*sc)),max(1,int(lay.height*sc))),Image.BICUBIC)
    arr=np.array(lay); arr[...,3]=(arr[...,3]*al).astype(np.uint8)
    if clipx is not None:   # reveal from the centre outwards
        half=int(arr.shape[1]/2*clipx); c=arr.shape[1]//2; arr[:,:max(0,c-half),3]=0; arr[:,c+half:,3]=0
    img.alpha_composite(Image.fromarray(arr),(int(cx-lay.width/2),int(cy-lay.height/2)))
def draw(img,t):
    if t>=OUT_T: return
    out=eio((t-(OUT_T-0.6))/0.6); fo=1-out; dy=-10*out
    p=t-IN_T
    # red square pops first
    s=eo(p/0.35)
    if s>0:
        x0=WD/2-row1_w/2; sq=Image.new("RGBA",(SQ,SQ),RED+(255,))
        put(img,shadow(sq,3,0.5,1),x0+SQ/2+3,Y1+dy+2,al=fo,sc=0.2+0.8*s)
    for k,(m,cx) in enumerate(L1):
        q=eo((p-0.12-k*0.035)/0.35)
        put(img,m,WD/2-row1_w/2+SQ+GAP+cx,Y1+dy+12*(1-q)+8,al=q*fo)
    q=eo((p-0.45)/0.45); put(img,L2,WD/2,Y2+dy+10*(1-q)+20,al=q*fo)
    q=eo((p-0.75)/0.6); put(img,LOGO,WD/2,Y3+dy+lh/2+8,al=clamp(q*1.5)*fo,sc=0.94+0.06*q,clipx=q)
if __name__=="__main__":
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
