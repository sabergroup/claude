# composite: breathing zoom, fluted glass under the caption pill, frosted video under the glass insert
import numpy as np,subprocess,math,sys,os
from PIL import Image,ImageFilter
from glass import glass
src,cap,ins,N,out=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),sys.argv[5]; fps=25; W,H=1080,1920
dec=subprocess.Popen(["ffmpeg","-v","error","-i",src,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-c:v","libx264","-crf","16","-preset","medium","-pix_fmt","yuv420p",out],stdin=subprocess.PIPE)
last=None
for i in range(N):
    b=dec.stdout.read(W*H*3)
    if len(b)==W*H*3: last=np.frombuffer(b,np.uint8).reshape(H,W,3)
    t=i/fps; z=1.0+0.035*(0.5-0.5*math.cos(2*math.pi*t/9.0)); im=Image.fromarray(last)
    if z>1.0005: im=im.transform((W,H),Image.AFFINE,(1/z,0,(W-W/z)/2,0,1/z,(H-H/z)*0.4),resample=Image.BICUBIC)
    ov=Image.open(f"{cap}/f{i:04d}.png").convert("RGBA")
    im=glass(im,ov).convert("RGBA"); im.alpha_composite(ov)
    f=f"{ins}/f{i:04d}.png"
    if os.path.exists(f):
        io=Image.open(f).convert("RGBA"); m=io.split()[3].point(lambda a:255 if a>0 else 0)
        if m.getbbox():
            rgb=im.convert("RGB"); rgb.paste(rgb.filter(ImageFilter.GaussianBlur(30)),(0,0),m); im=rgb.convert("RGBA")
        im.alpha_composite(io)
    enc.stdin.write(im.convert("RGB").tobytes())
enc.stdin.close(); enc.wait()
