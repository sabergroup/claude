import sys,subprocess,numpy as np,json
import os, sys
S=os.environ.get("WORK") or sys.exit("set WORK=<work dir with src/vid.mp4, words.json, config.py>")
sys.path.insert(0,S); sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import config as CFG
from plan import A,segs,SR
LIB=os.environ.get("SFX",f"{S}/sfx")
EV=json.load(open(os.environ.get("SFX_EVENTS",f"{S}/sfx_events.json")))
def load(f):
    a=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f"{LIB}/{f}","-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout,np.float32)
    return a.reshape(-1,2).copy()
# (time in video, file, event indices (first,last) or None=whole, align 'onset'|'peak', target peak dBFS, reason)
PLAN=CFG.SFX  # (time, file, events|('sec',a,b)|None, 'onset'|'peak'|'end', trim≈-27, reason)
_cat=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','..','sfx_library','catalog.json')))
_ban={s['file'] for s in _cat['sounds'] if s.get('banned')}
for _p in PLAN: assert _p[1] not in _ban, ('BANNED SFX',_p[1])
voice=np.concatenate([A[s:e] for s,e in segs]).astype(np.float32)
vm=voice.mean(1); fr=vm[:len(vm)//480*480].reshape(-1,480); r=np.sqrt((fr**2).mean(1))
VOICE_RMS=20*np.log10(np.sqrt((r[r>np.percentile(r,40)]**2).mean()))
REL=float(sys.argv[1]) if len(sys.argv)>1 else -6
print("voice speaking RMS dBFS",round(VOICE_RMS,1))
mix=voice.copy(); log=[]
for t,f,ev,al,tgt,why in PLAN:
    a=load(f); E=EV[f]["events"]
    if ev and ev[0]=="sec": s0,e0=ev[1],ev[2]
    elif ev:
        s0=E[ev[0]]["start"]; e0=E[ev[1]]["end"]+0.06
    else: s0=E[0]["start"]; e0=E[-1]["end"]+0.25
    seg=a[max(0,int((s0-0.01)*SR)):int(e0*SR)].copy()
    fo=min(len(seg),int(0.04*SR)); seg[-fo:]*=np.linspace(1,0,fo)[:,None]
    fi=min(len(seg),int(0.008*SR)); seg[:fi]*=np.linspace(0,1,fi)[:,None]
    env=np.abs(seg).max(1)
    off=0.01 if al=="onset" else (len(seg)/SR-0.02) if al=="end" else np.argmax(np.convolve(env,np.ones(480)/480,"same"))/SR
    e1=np.abs(seg).max(1); act=seg[e1>e1.max()*0.1]
    srms=20*np.log10(np.sqrt((act**2).mean())+1e-9); spk=20*np.log10(np.abs(seg).max()+1e-9)
    gdb=min(VOICE_RMS+REL+(tgt+27)-srms, -4-spk)   # tgt now = small per-effect trim around -27
    g=10**(gdb/20); seg*=g
    st=int(round((t-off)*SR))
    if st<0: seg=seg[-st:]; st=0
    en=min(len(mix),st+len(seg))
    mix[st:en]+=seg[:en-st]
    log.append(dict(t=round(t,2),file=f,events=list(ev) if ev else None,gain_db=round(float(20*np.log10(g)),1),why=why))
    print(f"{t:6.2f} {f[:40]:40s} ev={ev} gain {20*np.log10(g):+.1f} dB")
# iPhone tap on every word as it appears (rotating through all 16 taps in the library)
TAPS=[("iphone mix tabs.MP3",i) for i in range(12)]+[("iphone tab 2.MP3",0),("iphone tap 1.MP3",0),("iphone tab 2.MP3",1),("iphone tap 1.MP3",1)]
TAP_REL=float(sys.argv[2]) if len(sys.argv)>2 else -3
cache={}
words=[w for w in json.load(open(f"{S}/word_times.json")) if w["line_start"]]   # tap only on the first word of each caption line
for k,wd in enumerate(words):
    f,i=TAPS[k%len(TAPS)]
    if f not in cache: cache[f]=load(f)
    E=EV[f]["events"][i]; a=cache[f]
    seg=a[int((E["start"]-0.005)*SR):int((E["end"]+0.12)*SR)].copy()
    fo=int(0.03*SR); seg[-fo:]*=np.linspace(1,0,fo)[:,None]
    pk=20*np.log10(np.abs(seg).max()+1e-9)
    g=10**((VOICE_RMS+TAP_REL+12-pk)/20)   # taps are clicks: level them by peak (peak ≈ speech RMS + 12 + TAP_REL)
    st=int(round(wd["t"]*SR)); en=min(len(mix),st+len(seg)); mix[st:en]+=seg[:en-st]*g
log.append(dict(t="أول كل سطر",file="iphone mix tabs / iphone tab 2 / iphone tap 1",events="16 تاب بالتناوب",gain_db=None,why=f"تاب آيفون مع أول كلمة في كل سطر ({len(words)} سطر)"))
print("taps:",len(words))
print("mix peak dBFS",round(20*np.log10(np.abs(mix).max()),2),"voice peak",round(20*np.log10(np.abs(voice).max()),2))
assert np.abs(mix).max()<0.99
mix.tofile(f"{S}/mix_sfx.f32"); json.dump(log,open(f"{S}/sfx_used.json","w"),ensure_ascii=False,indent=1)
