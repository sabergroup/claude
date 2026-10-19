import sys,subprocess,math,os
from PIL import Image
src,pg,ipg,out=sys.argv[1:5]; ts=sys.argv[5:]; d=os.path.dirname(out)+"/st"; os.makedirs(d,exist_ok=True)
subprocess.run(["node",os.path.dirname(os.path.abspath(__file__))+"/stills.js",pg,d]+ts)
if ipg!="-": os.makedirs(d+"i",exist_ok=True); subprocess.run(["node",os.path.dirname(os.path.abspath(__file__))+"/stills.js",ipg,d+"i"]+ts)
ims=[]
for t in ts:
    subprocess.run(["ffmpeg","-v","error","-y","-ss",t,"-i",src,"-frames:v","1",d+"/bg.png"])
    im=Image.open(d+"/bg.png").convert("RGB"); W,H=im.size; z=1.0+0.035*(0.5-0.5*math.cos(2*math.pi*float(t)/9.0))
    im=im.transform((W,H),Image.AFFINE,(1/z,0,(W-W/z)/2,0,1/z,(H-H/z)*0.4),resample=Image.BICUBIC).convert("RGBA")
    im.alpha_composite(Image.open(f"{d}/s_{t}.png").convert("RGBA"))
    if ipg!="-" and os.path.exists(f"{d}i/s_{t}.png"): im.alpha_composite(Image.open(f"{d}i/s_{t}.png").convert("RGBA"))
    ims.append(im.convert("RGB"))
w=360; c=Image.new("RGB",(w*len(ims),640))
for i,im in enumerate(ims): c.paste(im.resize((w,640)),(i*w,0))
c.save(out); [im.save(out.replace(".png",f"_{t}.png")) for im,t in zip(ims,ts)] if "--full" in os.environ.get("FULL","") else None
