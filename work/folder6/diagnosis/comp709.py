import numpy as np,subprocess,math,sys,os
from PIL import Image
src,frs,N,out=sys.argv[1],sys.argv[2].split(","),int(sys.argv[3]),sys.argv[4]; fps=25; W,H=1080,1920
dec=subprocess.Popen(["ffmpeg","-v","error","-i",src,"-vf","scale=in_color_matrix=bt709:in_range=tv","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-c:v","libx264","-crf","16","-preset","medium","-vf","scale=out_color_matrix=bt709:out_range=tv","-pix_fmt","yuv420p","-colorspace","bt709","-color_primaries","bt709","-color_trc","bt709","-color_range","tv",out],stdin=subprocess.PIPE)
last=None
for i in range(N):
    b=dec.stdout.read(W*H*3)
    if len(b)==W*H*3:
        fr=np.frombuffer(b,np.uint8).reshape(H,W,3)
        if last is None or fr[::40,::40].mean()>20: last=fr   # Saber's exports end on one black frame: hold the last real picture
    t=i/fps; z=1.0+0.035*(0.5-0.5*math.cos(2*math.pi*t/9.0)); im=Image.fromarray(last)
    if z>1.0005: im=im.transform((W,H),Image.AFFINE,(1/z,0,(W-W/z)/2,0,1/z,(H-H/z)*0.4),resample=Image.BICUBIC)
    im=im.convert("RGBA")
    for d in frs:
        f=f"{d}/f{i:04d}.png"
        if os.path.exists(f): im.alpha_composite(Image.open(f).convert("RGBA"))
    enc.stdin.write(im.convert("RGB").tobytes())
enc.stdin.close(); enc.wait()
