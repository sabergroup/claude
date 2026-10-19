import numpy as np,subprocess,json,sys
from PIL import Image, ImageDraw
src,name=sys.argv[1],sys.argv[2]; w,h=270,480
raw=subprocess.run(["ffmpeg","-v","error","-i",src,"-vf",f"scale={w}:{h}","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
fr=np.frombuffer(raw,np.uint8).reshape(-1,h,w,3); n=len(fr); fps=float(eval(subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",src],capture_output=True,text=True).stdout.strip()))
d=np.abs(fr[1:].astype(np.int16)-fr[:-1]).mean((1,2,3)); med=np.median(d)
cuts=[0]+[round((i+1)/fps,2) for i in range(len(d)) if d[i]>max(12,6*med)]+[round(n/fps,2)]
laps=[]; c=Image.new("RGB",(270*8,480*((len(cuts)+6)//8)),"black"); dr=ImageDraw.Draw(c)
for i in range(len(cuts)-1):
    a,b=int(cuts[i]*fps),min(n-1,int(cuts[i+1]*fps)-1); ys=[]
    for k in np.linspace(a,b,7).astype(int)[1:-1]:
        f=fr[k].astype(np.float32); dark=(f.mean(2)<40)&((f.max(2)-f.min(2))<30); band=dark[:,85:185].mean(1)
        y=next((y for y in range(170,360) if band[y:y+6].min()>0.55),None)
        if y: ys.append(y)
    lap=int(np.median(ys))*4 if ys else (laps[-1] if laps else 1000); laps.append(lap)
    m=int((cuts[i]+cuts[i+1])/2*fps); x0,y0=(i%8)*270,(i//8)*480; c.paste(Image.fromarray(fr[m]),(x0,y0))
    dr.text((x0+5,y0+5),f"{i}: {cuts[i]} lap {lap}",fill=(255,255,0)); dr.line([(x0,y0+lap//4),(x0+270,y0+lap//4)],fill=(0,255,0))
c.save(f"{name}_laps.png"); json.dump({"cuts":cuts,"lap":laps,"fps":fps,"n":n},open(f"{name}_shots.json","w")); print(name,fps,n,cuts,laps)
