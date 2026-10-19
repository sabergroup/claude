# re-composite only the changed frame ranges (with the glass under the pill); other frames copied from the delivered reel
import numpy as np,subprocess,math,sys
from PIL import Image
from glass import glass
src,old,fr,N,out,a,b=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),sys.argv[5],int(sys.argv[6]),int(sys.argv[7])
W,H,fps=1080,1920,25
dec=subprocess.Popen(["ffmpeg","-v","error","-i",src,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
dol=subprocess.Popen(["ffmpeg","-v","error","-i",old,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-c:v","libx264","-crf","16","-preset","medium","-pix_fmt","yuv420p",out],stdin=subprocess.PIPE)
last=None
for i in range(N):
    bs=dec.stdout.read(W*H*3)
    if len(bs)==W*H*3: last=np.frombuffer(bs,np.uint8).reshape(H,W,3)
    bo=dol.stdout.read(W*H*3)
    if not (a<=i<b): enc.stdin.write(bo); continue
    t=i/fps; z=1.0+0.035*(0.5-0.5*math.cos(2*math.pi*t/9.0)); im=Image.fromarray(last)
    im=im.transform((W,H),Image.AFFINE,(1/z,0,(W-W/z)/2,0,1/z,(H-H/z)*0.4),resample=Image.BICUBIC)
    ov=Image.open(f"{fr}/f{i:04d}.png").convert("RGBA"); im=glass(im,ov).convert("RGBA"); im.alpha_composite(ov)
    enc.stdin.write(im.convert("RGB").tobytes())
enc.stdin.close(); enc.wait()
