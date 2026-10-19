"""Her footage + slow breathing zoom (±3.5% / 9 s) + transparent overlay PNGs -> video-only mp4 (audio is muxed later, voice untouched).
usage: composite.py <src.mp4> <frames_dir> <n_frames> <out.mp4> [fps=25]
frames beyond the source length hold the last source frame (for a closing move)."""
import numpy as np,subprocess,math,sys
from PIL import Image
src,fr,N,out=sys.argv[1],sys.argv[2],int(sys.argv[3]),sys.argv[4]; fps=float(sys.argv[5]) if len(sys.argv)>5 else 25
W,H=1080,1920
dec=subprocess.Popen(["ffmpeg","-v","error","-i",src,"-vf",f"scale={W}:{H}","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-c:v","libx264","-crf","16","-preset","medium","-pix_fmt","yuv420p",out],stdin=subprocess.PIPE)
last=None
for i in range(N):
    b=dec.stdout.read(W*H*3)
    if len(b)==W*H*3: last=np.frombuffer(b,np.uint8).reshape(H,W,3)
    t=i/fps; z=1.0+0.035*(0.5-0.5*math.cos(2*math.pi*t/9.0))
    im=Image.fromarray(last)
    if z>1.0005:
        x0=(W-W/z)/2; y0=(H-H/z)*0.4
        im=im.transform((W,H),Image.AFFINE,(1/z,0,x0,0,1/z,y0),resample=Image.BICUBIC)
    im=im.convert("RGBA"); im.alpha_composite(Image.open(f"{fr}/f{i:04d}.png").convert("RGBA"))
    enc.stdin.write(im.convert("RGB").tobytes())
enc.stdin.close(); enc.wait()
