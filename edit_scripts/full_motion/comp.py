# breathing zoom on her footage + transparent overlay frames; voice untouched (audio handled separately)
import numpy as np,subprocess,math,sys
from PIL import Image
S="/tmp/claude-0/-home-user-claude/5b00ce15-a751-5c6f-a77b-d1addef998ec/scratchpad"
src=f"{S}/b3/القشره.mp4"; N=1555; W,H=1080,1920
dec=subprocess.Popen(["ffmpeg","-v","error","-i",src,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","25","-i","-","-c:v","libx264","-crf","16","-preset","medium","-pix_fmt","yuv420p","reel.mp4"],stdin=subprocess.PIPE)
last=None
for i in range(N):
    b=dec.stdout.read(W*H*3)
    if len(b)==W*H*3: last=np.frombuffer(b,np.uint8).reshape(H,W,3)
    t=i/25; z=1.0+0.035*(0.5-0.5*math.cos(2*math.pi*t/9.0))
    im=Image.fromarray(last)
    if z>1.0005:
        cw,ch=W/z,H/z; x0=(W-cw)/2; y0=(H-ch)*0.4
        im=im.transform((W,H),Image.AFFINE,(1/z,0,x0,0,1/z,y0),resample=Image.BICUBIC)
    im=im.convert("RGBA"); im.alpha_composite(Image.open(f"fr/f{i:04d}.png").convert("RGBA"))
    enc.stdin.write(im.convert("RGB").tobytes())
    if i%250==0: print(i,flush=True)
enc.stdin.close(); enc.wait(); print("done")
