import json,sys,subprocess,copy
sys.path.insert(0,"/tmp/claude-0/-home-user-claude/e25184d4-7e44-5b51-8336-74c4a252bb1f/scratchpad/f1/b")
import align,holds
S=align.S; F=f"{S}/f1"; OLD=align.OLD; PRE=3/25
PK=json.load(open("/home/user/claude/sfx_library/saber_v2/peaks.json"))
ICONS=json.load(open(f"{S}/icons.json"))
ANCHOR=1192; NAMEY=232; CAPY=70
END_SND=("اصوات تنفع لبداية او نهاية الفيديو/whoosh with impact.MP3",3.16,0.795)
PREP={"في","على","من","عن","بين","مع","لحد","زي","ما","إن","إنك","اللي","لأن","لأي","لنفس","بعد","تحت","علشان","والـ","أو","و"}
def sfx(f,t,seg=None):
    p=PK[f] if not seg else seg[2]
    return f"{f}@{t:.2f}@{p}"+(f"@{seg[0]}@{seg[1]}" if seg else "")
class V:
    def __init__(s,name,cfg,fix):
        Wd=json.load(open(f"{F}/words_{name}.json")); toks,_=align.parse_ch(OLD+cfg); s.tk,_=align.align(toks,Wd)
        for k,w in fix.items(): s.tk[k]["w"]=w
        s.name=name; s.src=f"{F}/src/{name}.mp4"
    def W(s,k,g=None): t=s.tk[k]; return {"w":t["w"],"t":t["t"],"e":t["e"],"g":t["g"] if g is None else g}
    def ws(s,a,b,gold=None): return [s.W(k,None if gold is None else (k in gold)) for k in range(a,b)]
    def t(s,k): return s.tk[k]["t"]
    def nw(s,k): return len(s.tk[k]["w"].split())
    def rows(s,a,b,mx=3,mn=2):
        """split a sentence into caption rows of 2-3 words (never ending on a preposition), balanced, fewest rows"""
        ks=list(range(a,b)); n=len(ks); best={n:(0,0,[])}
        for i in range(n-1,-1,-1):
            cands=[]
            for j in range(i+1,n+1):
                w=sum(s.nw(k) for k in ks[i:j])
                if w>mx: break
                if j<n and s.tk[ks[j-1]]["w"] in PREP: continue
                if w<mn and not (i==0 and j==n): 
                    if j-i==1 and s.nw(ks[i])>=2: pass
                    else: continue
                if j in best: cands.append((best[j][0]+1, best[j][1]+abs(w-2.5), [(ks[i],ks[j-1]+1)]+best[j][2]))
            if cands: best[i]=min(cands)
        if 0 not in best:
            assert mx<4,(a,b,[s.tk[k]["w"] for k in ks]); return s.rows(a,b,3,1) if mn==2 else s.rows(a,b,4,1)
        return best[0][2]
    def phrases(s,a,b):
        """the approved CH lines (meaningful phrases) inside [a,b)"""
        L={}
        for k in range(a,b): L.setdefault(s.tk[k]["line"],[]).append(k)
        return [(ks[0],ks[-1]+1) for ks in L.values()]
    def blocks(s,sentences):
        sentences=[p for x in sentences for p in ([x[1:]] if x[0]=="p" else s.phrases(*x))]
        out=[]
        for a,b in sentences:
            r=s.rows(a,b)
            # pairs of rows; an odd last row joins as a single-row block (a 1-row tail merges back when it is 1 word)
            for i in range(0,len(r),2): out.append(r[i:i+2])
        return out
    def chunks(s,blocks): return [[dict(s.W(k),r=ri) for ri,(a,b) in enumerate(bl) for k in range(a,b)] for bl in blocks]
    def line(s,a,b,y,size=None,g=False):
        L={"text":" ".join(s.tk[k]["w"] for k in range(a,b)),"y":y,"t":s.t(a),"wt":[s.t(k) for k in range(a,b) for _ in s.tk[k]["w"].split()]}
        if size: L["size"]=size
        if g: L["g"]=True
        return L
    def name_times(s):
        ts=[]; last=0.15
        for k in range(1,12):
            if s.t(k)>=max(0.45,last+0.3): ts.append(s.t(k)); last=s.t(k)
            if len(ts)==4: break
        ex=next(s.t(k) for k in range(len(s.tk)) if s.t(k)>=5.9)
        return {"appear":0.0,"stretch":0.30,"split":round(min(0.6,ts[0]-0.05),2),"dr":ts[0],"marwa":ts[1],"magdy":ts[2],"title":ts[3],"exit":round(ex-0.05,2)}
def _shift_dev(d,t0):
    d["start"]=round(t0,3); holds._shift(holds._words(d),t0+0.12)
    for it in d.get("items",[]):
        if "t" in it: it["t"]=max(it["t"],round(t0+0.12,3))
    if "ringT" in d: d["ringT"]=max(d["ringT"],round(t0+0.12,3))
def schedule(chunks,devices,insert,ins):
    """one pass in time order: each device / the insert waits for the caption before it (>=0.8 s) and for whatever was on before it"""
    evs=[("dev",d) for d in devices]+([("ins",None)] if insert else []); evs.sort(key=lambda e:(e[1]["start"] if e[1] else insert["start"]))
    prev_end=-1
    for kind,d in evs:
        if kind=="dev":
            s0=max(holds._caption_wait(chunks,d["start"]),prev_end+0.05,d.pop("min_start",0))
            if s0>d["start"]+0.001: _shift_dev(d,s0)
            holds.apply_holds([d] if d["type"]!="num" else [],None,None,None)
            if d["type"]=="num":
                for k in range(1,len(d["items"])):
                    pl=max(o["t"] for o in d["items"][k-1]["words"]); t0=max(d["items"][k]["t"],pl+0.8)
                    d["items"][k]["t"]=round(t0,3); holds._shift(d["items"][k]["words"],t0)
                lastT=max(o["t"] for o in holds._words(d))
                d["end"]=round(max(d["end"],lastT+1.0),3)
            prev_end=d["end"]
        else:
            ch=list(chunks)
            if prev_end>0: ch.append([{"t":ins["open"]-0.2},{"t":prev_end+PRE-0.8-0.03}])
            ch.sort(key=lambda c:c[0]["t"]); holds.insert_timing(ins,insert,ch); prev_end=insert["end"]
def build(v,sentences,devices,insert,ins,icons,fx,cuts):
    blocks=v.blocks(sentences); chunks=v.chunks(blocks)
    schedule(chunks,devices,insert,ins)
    last=v.tk[-1]
    st=max(last["t"]-PRE+0.8, max([d["end"] for d in devices if d["end"]>last["t"]-1]+[0]))
    END={"start":round(st,2)}; END["close"]=round(END["start"]+0.8,2); srcdur=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",v.src],capture_output=True,text=True).stdout)
    if END["close"]>srcdur-0.1: END["start"]=round(srcdur-0.9,2); END["close"]=round(END["start"]+0.8,2)   # raw length wins: the ring still closes before the last frame
    END["dur"]=round(srcdur,2)   # Saber: never lengthen the video for the ending
    skip=[(insert["start"],insert["end"])] if insert else []
    trans=[]; j=0
    for c in cuts:
        if c<0.3 or c>END["start"]-0.3 or any(a-0.25<=c<=b+0.25 for a,b in skip): continue
        trans.append([c,["flash","sweep"][j%2]]); j+=1
    busy=[(d["start"],d["end"]) for d in devices]+skip
    IC=[]
    for i,(a,b,n) in enumerate(icons):
        s0=v.t(a); e=v.tk[b]["e"]+1.0
        if i+1<len(icons): e=min(e,v.t(icons[i+1][0])-0.15)
        for x,y in busy:
            if x>s0: e=min(e,x-0.1)
            if x<=s0<y: e=-1
        e=min(e,END["start"]-0.1)
        if e-s0>=0.9: IC.append({"n":n,"s":round(s0,2),"e":round(e,2)})
    data={"chunks":chunks,"devices":devices,"cuts":[],"lap":[ANCHOR],"anchor":ANCHOR,"nameY":NAMEY,"capY":CAPY,"N":v.name_times(),"END":END,"trans":trans,"insert":insert,"icons":IC,"endY":560}
    if ins:
        ins["ball"][0][1]={"s":{"x":540,"y":ANCHOR+60}}; ins["ball"][-1][1]={"s":{"x":540,"y":ANCHOR+60}}
    mp={}
    for o in holds._words(devices):
        if "t0" in o and o["t"]!=o["t0"]: mp[round(o["t0"],2)]=o["t"]
    out=[]
    for x in fx:
        p=x.split("@"); t=round(float(p[1]),2)
        if ins and "_open0" in ins and abs(t-ins["_open0"])<0.2: p[1]=f'{t+ins["open"]-ins["_open0"]:.2f}'
        elif ins and "_close0" in ins and abs(t-ins["_close0"])<0.2: p[1]=f'{ins["close"]+0.03:.2f}'
        elif t in mp: p[1]=f"{mp[t]:.2f}"
        out.append("@".join(p))
    out.append(sfx(END_SND[0],END["close"]))
    W=f"{F}/w"; n=v.name
    h=open(f"{F}/b/reel_f1.html").read().replace("ICONDATA",json.dumps(ICONS)).replace("DATA",json.dumps(data,ensure_ascii=False))
    open(f"{W}/page_{n}.html","w").write(h)
    if ins: open(f"{W}/ipage_{n}.html","w").write(open(f"{F}/b/ins_f1.html").read().replace("DATA",json.dumps(ins,ensure_ascii=False)))
    json.dump(data,open(f"{W}/data_{n}.json","w"),ensure_ascii=False); json.dump(ins,open(f"{W}/ins_{n}.json","w"),ensure_ascii=False)
    open(f"{W}/sfx_{n}.txt","w").write("\n".join(out)+"\n")
    print(n,"END",END,"ins",insert,ins and (ins["open"],ins["close"]))
    for bl in blocks: print("   |".join(" ".join(v.tk[k]["w"] for k in range(a,b)) for a,b in bl))
    for d in devices: print(d["type"],round(d["start"],2),round(d["end"],2))
    return data
def shots(n): return json.load(open(f"{F}/{n}_shots.json"))["cuts"][1:-1]
