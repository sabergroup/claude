import json,sys,subprocess,copy
sys.path.insert(0,"/tmp/claude-0/-home-user-claude/e25184d4-7e44-5b51-8336-74c4a252bb1f/scratchpad/f1/b")
import align,holds
S=align.S; F=f"{S}/f1"; OLD=align.OLD; PRE=3/25
PK=json.load(open("/home/user/claude/sfx_library/saber_v2/peaks.json"))
ICONS=json.load(open(f"{S}/icons.json"))
ANCHOR=1192; NAMEY=232; CAPY=70
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
    def chunks(s,blocks): return [[dict(s.W(k),r=ri) for ri,(a,b) in enumerate(bl) for k in range(a,b)] for bl in blocks]
    def line(s,a,b,y,size=None,g=False,text=None):
        L={"text":text or " ".join(s.tk[k]["w"] for k in range(a,b)),"y":y,"t":s.t(a),"wt":[s.t(k) for k in range(a,b) for _ in s.tk[k]["w"].split()]}
        if size: L["size"]=size
        if g: L["g"]=True
        assert len(L["text"].split())==len(L["wt"]),L["text"]
        return L
    def name_times(s):
        ts=[]; last=0.15
        for k in range(1,12):
            if s.t(k)>=max(0.45,last+0.3): ts.append(s.t(k)); last=s.t(k)
            if len(ts)==4: break
        ex=next(s.t(k) for k in range(len(s.tk)) if s.t(k)>=5.9)
        return {"appear":0.0,"stretch":0.30,"split":round(min(0.6,ts[0]-0.05),2),"dr":ts[0],"marwa":ts[1],"magdy":ts[2],"title":ts[3],"exit":round(ex-0.05,2)}
def build(v,blocks,devices,insert,ins,icons,fx,cuts):
    chunks=v.chunks(blocks)
    # every spoken word appears exactly once outside the insert
    used=sorted([k for bl in blocks for a,b in bl for k in range(a,b)])
    holds.devices_wait(chunks,devices,None); holds.apply_holds(devices,None,insert,ins)
    if insert:
        # the insert also waits for a device that is still on (its last word keeps >= 1 s)
        ch=list(chunks)
        for d in devices:
            if d["start"]<ins["open"]<d["end"]+0.05: ch.append([{"t":ins["open"]-0.2},{"t":d["end"]+PRE-0.8-0.03}])
        ch.sort(key=lambda c:c[0]["t"])
        holds.insert_timing(ins,insert,ch)
    last=v.tk[-1]; srcdur=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",v.src],capture_output=True,text=True).stdout)
    END={"start":round(max(last["e"]+0.12,last["t"]-PRE+1.0),2)}; END["close"]=round(END["start"]+0.8,2); END["dur"]=round(max(srcdur,END["close"]+0.5),2)
    if devices and devices[-1]["end"]>END["start"]-0.05: END["start"]=round(devices[-1]["end"]+0.3,2); END["close"]=round(END["start"]+0.8,2); END["dur"]=round(max(srcdur,END["close"]+0.5),2)
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
        e=min(e,END["start"]-0.1)
        if e-s0>=0.9: IC.append({"n":n,"s":round(s0,2),"e":round(e,2)})
    data={"chunks":chunks,"devices":devices,"cuts":[],"lap":[ANCHOR],"anchor":ANCHOR,"nameY":NAMEY,"capY":CAPY,"N":v.name_times(),"END":END,"trans":trans,"insert":insert,"icons":IC,"endY":560}
    if ins:
        ins["ball"][0][1]={"s":{"x":540,"y":ANCHOR+60}}; ins["ball"][-1][1]={"s":{"x":540,"y":ANCHOR+60}}
    # sounds follow the words that a hold moved
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
    out.append(sfx("اصوات تنفع لبداية او نهاية الفيديو/whoosh with impact.MP3",END["close"]))
    W=f"{F}/w"; n=v.name
    h=open(f"{F}/b/reel_f1.html").read().replace("ICONDATA",json.dumps(ICONS)).replace("DATA",json.dumps(data,ensure_ascii=False))
    open(f"{W}/page_{n}.html","w").write(h)
    if ins: open(f"{W}/ipage_{n}.html","w").write(open(f"{F}/b/ins_f1.html").read().replace("DATA",json.dumps(ins,ensure_ascii=False)))
    json.dump(data,open(f"{W}/data_{n}.json","w"),ensure_ascii=False); json.dump(ins,open(f"{W}/ins_{n}.json","w"),ensure_ascii=False)
    open(f"{W}/sfx_{n}.txt","w").write("\n".join(out)+"\n")
    # srt from the corrected words, by caption block / device / insert line
    print(n,"END",END,"N",data["N"],"trans",trans,"icons",IC,"ins",insert)
    return data
def shots(n): return json.load(open(f"{F}/{n}_shots.json"))["cuts"][1:-1]
