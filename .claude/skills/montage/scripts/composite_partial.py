# re-composite only the changed frame ranges; every other frame is copied from the previous reel (same overlay, same zoom)
import numpy as np,subprocess,math,sys,os
from PIL import Image
src,old,frs,N,out,ranges=sys.argv[1],sys.argv[2],sys.argv[3].split(","),int(sys.argv[4]),sys.argv[5],sys.argv[6]
R=[tuple(int(float(x)*25) for x in r.split("-")) for r in ranges.split(",")]
inR=lambda i:any(a<=i<b for a,b in R)
W,H,fps=1080,1920,25
dec=subprocess.Popen(["ffmpeg","-v","error","-i",src,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
dol=subprocess.Popen(["ffmpeg","-v","error","-i",old,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-c:v","libx264","-crf","16","-preset","medium","-pix_fmt","yuv420p",out],stdin=subprocess.PIPE)
last=None; lastold=None; n_new=0
for i in range(N):
    b=dec.stdout.read(W*H*3)
    if len(b)==W*H*3: last=np.frombuffer(b,np.uint8).reshape(H,W,3)
    bo=dol.stdout.read(W*H*3)
    if len(bo)==W*H*3: lastold=bo
    if not inR(i) and len(bo)==W*H*3: enc.stdin.write(bo); continue
    t=i/fps; z=1.0+0.035*(0.5-0.5*math.cos(2*math.pi*t/9.0)); im=Image.fromarray(last)
    if z>1.0005: im=im.transform((W,H),Image.AFFINE,(1/z,0,(W-W/z)/2,0,1/z,(H-H/z)*0.4),resample=Image.BICUBIC)
    im=im.convert("RGBA")
    for d in frs:
        f=f"{d}/f{i:04d}.png"
        if os.path.exists(f): im.alpha_composite(Image.open(f).convert("RGBA"))
    enc.stdin.write(im.convert("RGB").tobytes()); n_new+=1
enc.stdin.close(); enc.wait(); print("recomposited",n_new,"of",N)
