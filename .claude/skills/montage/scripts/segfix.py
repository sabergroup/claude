import numpy as np,subprocess,math,sys,os
from PIL import Image
src,seg,out,f0,a,b=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6])
W,H,fps=1080,1920,25
n=int(subprocess.run(["ffprobe","-v","error","-count_frames","-select_streams","v","-show_entries","stream=nb_read_frames","-of","csv=p=0",seg],capture_output=True,text=True).stdout.strip())
dseg=subprocess.Popen(["ffmpeg","-v","error","-i",seg,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
dsrc=subprocess.Popen(["ffmpeg","-v","error","-ss",str(f0/fps),"-i",src,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-c:v","libx264","-preset","slow","-crf","16","-pix_fmt","yuv420p",out],stdin=subprocess.PIPE)
for j in range(n):
    bo=dseg.stdout.read(W*H*3); bs=dsrc.stdout.read(W*H*3); i=f0+j
    if not (a<=i<b): enc.stdin.write(bo); continue
    t=i/fps; z=1.0+0.035*(0.5-0.5*math.cos(2*math.pi*t/9.0)); im=Image.frombytes("RGB",(W,H),bs)
    if z>1.0005: im=im.transform((W,H),Image.AFFINE,(1/z,0,(W-W/z)/2,0,1/z,(H-H/z)*0.4),resample=Image.BICUBIC)
    im=im.convert("RGBA"); im.alpha_composite(Image.open(f"fr_dandruff/f{i:04d}.png").convert("RGBA")); enc.stdin.write(im.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); print("segment frames",n)
