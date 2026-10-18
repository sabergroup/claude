import numpy as np
from PIL import Image, ImageFilter
def clean_floor(fr, y0=1000, q=4):
    """smooth low-contrast creases in the brown backdrop floor; leave legs, shoes, chair (strong edges / non-floor colours) alone.
    masks are computed at 1/q resolution (fast), the blend is done at full resolution."""
    H,W,_=fr.shape; h=H-y0
    im=Image.fromarray(fr[y0:])
    sm=im.resize((W//q,h//q),Image.BILINEAR)                                   # quarter-res working copy
    blur_s=sm.resize((W//6,h//6),Image.BILINEAR).filter(ImageFilter.GaussianBlur(5)).resize(sm.size,Image.BICUBIC)
    g=np.asarray(sm.convert("L"),np.float32)
    gx=np.abs(np.diff(g,axis=1,prepend=g[:,:1])); gy=np.abs(np.diff(g,axis=0,prepend=g[:1]))
    edge=Image.fromarray(((gx+gy)>6*q/2.2).astype(np.uint8)*255).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.5))
    a=np.asarray(sm,np.float32); b=np.asarray(blur_s,np.float32)
    diff=np.abs(a-b).sum(2); lum=a.mean(2)
    floorish=np.clip(1-(diff-10)/18,0,1)*np.clip((lum-35)/20,0,1)*np.clip((160-lum)/25,0,1)
    m=np.clip(floorish*(1-np.asarray(edge,np.float32)/255),0,1)
    m=np.asarray(Image.fromarray((m*255).astype(np.uint8)).resize((W,h),Image.BILINEAR),np.float32)[...,None]/255
    blur=np.asarray(blur_s.resize((W,h),Image.BICUBIC),np.float32)
    reg=fr[y0:].astype(np.float32)
    out=fr.copy(); out[y0:]=(reg*(1-m)+blur*m).clip(0,255).astype(np.uint8)
    return out
if __name__=="__main__":
    import sys
    a=np.asarray(Image.open(sys.argv[1]).convert("RGB")); Image.fromarray(clean_floor(a)).save(sys.argv[2])
