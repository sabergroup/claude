# frosted + fluted glass under the caption pill: blur, lift, and bend the picture inside each 16px rib
import numpy as np
from PIL import Image,ImageFilter,ImageEnhance
RIB=16
def glass(v,ov):
    a=np.asarray(ov)[:,:,3]; ys,xs=np.nonzero(a>40)
    if not len(ys): return v
    W,H=v.size; x0,y0,x1,y1=max(0,xs.min()-30),max(0,ys.min()-30),min(W,xs.max()+30),min(H,ys.max()+30)
    reg=v.crop((x0,y0,x1,y1)); g=np.asarray(ImageEnhance.Brightness(reg.filter(ImageFilter.GaussianBlur(9))).enhance(1.05))
    xx=np.arange(x1-x0); ph=((xx+x0)%RIB)/RIB; src=np.clip((xx+(ph-0.5)*RIB*0.9).round().astype(int),0,x1-x0-1)   # each rib shows a squeezed slice, like fluted glass
    g=Image.fromarray(g[:,src])
    m=Image.fromarray(((a[y0:y1,x0:x1]>40)*255).astype('uint8')).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(1.5))
    v=v.copy(); v.paste(g,(x0,y0),m); return v
