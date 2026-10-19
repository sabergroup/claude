# one composited still: video frame at t (with breathing zoom) + glass + overlay [+ insert overlay]
import sys,math,subprocess,os,numpy as np
from PIL import Image,ImageFilter
from glass import glass
def frame(src,t,ov,ins=None):
    b=subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',src,'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    im=Image.fromarray(np.frombuffer(b,np.uint8).reshape(1920,1080,3)); W,H=1080,1920
    z=1.0+0.035*(0.5-0.5*math.cos(2*math.pi*t/9.0))
    im=im.transform((W,H),Image.AFFINE,(1/z,0,(W-W/z)/2,0,1/z,(H-H/z)*0.4),resample=Image.BICUBIC)
    o=Image.open(ov).convert('RGBA'); im=glass(im,o).convert('RGBA'); im.alpha_composite(o)
    if ins and os.path.exists(ins):
        io=Image.open(ins).convert('RGBA'); m=io.split()[3].point(lambda a:255 if a>0 else 0)
        if m.getbbox(): rgb=im.convert('RGB'); rgb.paste(rgb.filter(ImageFilter.GaussianBlur(30)),(0,0),m); im=rgb.convert('RGBA')
        im.alpha_composite(io)
    return im.convert('RGB')
if __name__=='__main__':
    frame(sys.argv[1],float(sys.argv[2]),sys.argv[3],sys.argv[5] if len(sys.argv)>5 else None).save(sys.argv[4])
