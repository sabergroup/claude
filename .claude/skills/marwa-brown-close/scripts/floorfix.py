import numpy as np
from PIL import Image, ImageFilter
def clean_floor(fr, y0=1000):
    """smooth low-contrast creases in the brown backdrop floor; leave legs, shoes, chair (strong edges / non-floor colours) alone"""
    H,W,_=fr.shape; reg=fr[y0:].astype(np.float32)
    im=Image.fromarray(fr[y0:])
    small=im.resize((W//6,(H-y0)//6),Image.BILINEAR)
    blur=np.asarray(small.filter(ImageFilter.GaussianBlur(5)).resize((W,H-y0),Image.BICUBIC),np.float32)
    g=np.asarray(im.convert("L").filter(ImageFilter.GaussianBlur(1.2)),np.float32)
    gx=np.abs(np.diff(g,axis=1,prepend=g[:,:1])); gy=np.abs(np.diff(g,axis=0,prepend=g[:1]))
    edge=np.asarray(Image.fromarray(((gx+gy)>6).astype(np.uint8)*255).filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(6)),np.float32)/255
    # floor-like colour: close to the local smooth colour and not dark (legs) / not bright (skin, chair seat)
    diff=np.abs(reg-blur).sum(2)
    lum=reg.mean(2)
    floorish=np.clip(1-(diff-10)/18,0,1)*np.clip((lum-35)/20,0,1)*np.clip((160-lum)/25,0,1)
    m=np.clip(floorish*(1-edge),0,1)[...,None]
    out=fr.copy(); out[y0:]=(reg*(1-m)+blur*m).clip(0,255).astype(np.uint8)
    return out
if __name__=="__main__":
    import sys
    a=np.asarray(Image.open(sys.argv[1]).convert("RGB")); b=clean_floor(a)
    Image.fromarray(b).save(sys.argv[2])
