"""Dr. Ahmed Ashraf's logo (white box «د.أحمد أشرف» + «أستاذ جراحة التجميل») right after the Saber Group credit.
In: 5.15 s (the credit is gone at 5.0) - the white box opens from its centre (0.45 s), then the title rises in behind a mask.
Out: 8.9 s - same moves in reverse. Size 0.62 of the source PNG, centred, top at y=1455 (under the captions, above the credit spot).
Use inside the compositor, per frame:  lg=logo_anim.frame(t);  if lg: im.alpha_composite(lg)   (im = RGBA 1080x1920)"""
# doctor's logo after the Saber Group credit: the white box opens from its centre, the title rises in behind a mask; it leaves the same way
import numpy as np,math
from PIL import Image
import os
L=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","assets","dr_ahmed_ashraf_logo.png")).convert("RGBA").crop((245,853,835,1067))
SC=0.62; L=L.resize((int(L.width*SC),int(L.height*SC)),Image.LANCZOS); Wl,Hl=L.size
split=int((990-853)*SC)                       # box above, subtitle below
BOX,SUB=L.crop((0,0,Wl,split)),L.crop((0,split,Wl,Hl))
CX,TOP=540,1455
T_IN,T_OUT=5.15,8.9
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def frame(t):
    if t<T_IN or t>T_OUT+0.6: return None
    a1=ease((t-T_IN)/0.45)*(1-ease((t-T_OUT-0.12)/0.4)); a2=ease((t-T_IN-0.25)/0.45)*(1-ease((t-T_OUT)/0.35))
    im=Image.new("RGBA",(1080,1920),(0,0,0,0)); x0=CX-Wl//2
    if a1>0.002:                               # box: horizontal mask from the centre
        w=int(Wl*a1); b=BOX.crop(((Wl-w)//2,0,(Wl+w)//2,split)); im.alpha_composite(b,(x0+(Wl-w)//2,TOP))
    if a2>0.002:                               # subtitle: rises from under its line, masked
        h=SUB.height; dy=int((1-a2)*h); s=SUB.crop((0,0,Wl,h-dy)); im.alpha_composite(s,(x0,TOP+split+dy))
    return im
