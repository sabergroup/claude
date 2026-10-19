import sys,json
sys.path.insert(0,".")
import align
def ts(x): h=int(x//3600); m=int(x%3600//60); s=x%60; return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s-int(s))*1000)):03d}"
for n,cfg,fix,out in [("mounjaro","المونجارو_config.py",{0:"حسيتي"},"المونجارو_وتأثيره_على_الوش.srt"),("collagen","تحفيز_الكولاجين_config.py",{},"تحفيز_الكولاجين.srt"),("neck","خطوط_وتجاعيد_الرقبة_config.py",{},"خطوط_وتجاعيد_الرقبة.srt")]:
    W=json.load(open(f"{align.S}/f1/words_{n}.json")); toks,_=align.parse_ch(align.OLD+cfg); toks,_=align.align(toks,W)
    for k,w in fix.items(): toks[k]["w"]=w
    L={}
    for t in toks: L.setdefault(t["line"],[]).append(t)
    ls=list(L.values()); o=[]
    for i,l in enumerate(ls):
        a=l[0]["t"]; b=ls[i+1][0]["t"] if i+1<len(ls) else l[-1]["e"]+0.6
        o.append(f"{i+1}\n{ts(a)} --> {ts(b)}\n{' '.join(t['w'] for t in l)}\n")
    open(f"{align.S}/f1/w/{out}","w").write("\n".join(o)); print(out,len(o))
