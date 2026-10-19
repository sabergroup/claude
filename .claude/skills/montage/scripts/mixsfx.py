"""mix saber_v2 sounds ~6 dB under her voice; her samples are never altered (only summed with the effects).
usage: SFX_DIR=<dir> mixsfx.py <video> <start> <dur> <out.f32> "file@time@peak[@seg_start@seg_end]" ...
time = moment the sound's peak should land (s, relative to <start>); peak = peak offset inside the file (see sfx_library/saber_v2/analysis.json)"""
import sys,numpy as np,subprocess
import os
SFX=os.environ.get("SFX_DIR","sfx2")   # local copy of Saber's v2 sound folder (drive_listdir.py + curl)
def dec(f,ss=None,t=None):
    cmd=["ffmpeg","-v","error"]+(["-ss",str(ss)] if ss is not None else [])+(["-t",str(t)] if t else [])+["-i",f,"-ac","2","-ar","48000","-f","f32le","-"]
    return np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,np.float32).reshape(-1,2).copy()
v=dec(sys.argv[1],float(sys.argv[2]),float(sys.argv[3])); hop=480
n_out=int(float(sys.argv[3])*48000)   # the video can run past her audio (ending card): pad with silence so the effects are never cut before the picture ends
e=np.sqrt((v[:len(v)//hop*hop].mean(1).reshape(-1,hop)**2).mean(1)); vr=np.percentile(e[e>np.percentile(e,40)],75)
out=np.concatenate([v,np.zeros((max(0,n_out-len(v)),2),np.float32)])
for spec in sys.argv[5:]:
    parts=spec.split("@"); f,t,pk=parts[:3]; s=dec(f"{SFX}/{f}")
    if len(parts)==5: s=s[int(float(parts[3])*48000):int(float(parts[4])*48000)]
    a=s.mean(1); nn=len(a)//hop
    se=np.sqrt((a[:nn*hop].reshape(nn,hop)**2).mean(1)); sr=se[se>se.max()*0.3].mean()
    g=vr/sr*10**(-6/20); i0=max(0,int((float(t)-float(pk))*48000)); seg=(s*g)[:len(out)-i0]; out[i0:i0+len(seg)]+=seg
    print(f,"@",t,"gain",round(20*np.log10(g),1),"dB")
print("peak",round(float(np.abs(out).max()),3)); out.astype(np.float32).tofile(sys.argv[4])
