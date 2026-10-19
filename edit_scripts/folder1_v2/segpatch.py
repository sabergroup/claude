# re-encode only frames [f0,f1) of a finished reel: source + slow zoom + overlay dirs (same x264 settings as sg_intro), then splice with -c copy
import numpy as np,subprocess,math,sys,os
from PIL import Image
src,f0,f1,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]; dirs=sys.argv[5].split(","); W,H,fps=1080,1920,25
dec=subprocess.Popen(["ffmpeg","-v","error","-ss",str(f0/fps),"-i",src,"-frames:v",str(f1-f0),"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-c:v","libx264","-preset","slow","-crf","16","-pix_fmt","yuv420p",out],stdin=subprocess.PIPE)
for i in range(f0,f1):
    b=dec.stdout.read(W*H*3); t=i/fps; z=1.0+0.035*(0.5-0.5*math.cos(2*math.pi*t/9.0)); im=Image.frombytes("RGB",(W,H),b)
    if z>1.0005: im=im.transform((W,H),Image.AFFINE,(1/z,0,(W-W/z)/2,0,1/z,(H-H/z)*0.4),resample=Image.BICUBIC)
    im=im.convert("RGBA")
    for d in dirs:
        f=f"{d}/f{i:04d}.png"
        if os.path.exists(f): im.alpha_composite(Image.open(f).convert("RGBA"))
    enc.stdin.write(im.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); print("frames",f1-f0)
