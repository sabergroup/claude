import json
PRE=3/25
def _words(x):
    if isinstance(x,dict): return [x] if "w" in x else [w for v in x.values() if isinstance(v,(list,dict)) for w in _words(v)]
    if isinstance(x,list): return [w for v in x for w in _words(v)]
    return []
def _shift(ws,t0):
    for o in ws:
        o.setdefault("t0",o["t"]); o["t"]=max(o["t"],round(t0,3))
def apply_holds(devices,split,insert,ins):
    """skill rules: last word of any device stays >=1 s; numbers/sections don't flip before the current last word stayed >=0.8 s;
    the next device (and the captions, in the page) wait; the insert ends only after its circle has fully closed."""
    evs=[("dev",d) for d in devices]+([("split",split)] if split else [])
    evs.sort(key=lambda e:e[1]["start"]); prev_end=-1
    for kind,d in evs:
        if d["start"]<prev_end+0.05:
            d["start"]=round(prev_end+0.05,3); _shift(_words(d),d["start"]+0.12)
        if kind=="split":
            last2=max(o["t"] for o in d["c2"]); m=max(d["merge"],last2+0.8)
            if m>d["merge"]: d["merge"]=round(m,3); _shift(d["cap"][0],m)
            c1=max(o["t"] for o in d["cap"][0])+0.8
            if d["cap"][1][0]["t"]<c1: _shift(d["cap"][1],c1)
            t2=max(o["t"] for o in d["cap"][1])+0.8
            if d["tt"]<t2: d["tt"]=round(t2,3); _shift(d["title"],t2)
            lastT=max(o["t"] for o in _words({k:d[k] for k in ("c1","c2","cap","title","chips")}))
        elif d["type"]=="counter":
            for k in range(1,len(d["items"])):
                pl=max(o["t"] for o in d["items"][k-1]["words"]); t0=max(d["items"][k]["t"],pl+0.8)
                d["items"][k]["t"]=round(t0,3); _shift(d["items"][k]["words"],t0)
            lastT=max(o["t"] for o in _words(d["items"]))
        elif d["type"]=="cmp":
            for k in range(1,len(d["sections"])):
                pl=max(o["t"] for o in _words(d["sections"][k-1])); t0=max(d["sections"][k]["head"][0]["t"],pl+0.8)
                _shift(_words(d["sections"][k]),t0)
            lastT=max(o["t"] for o in _words(d["sections"]))
        else: lastT=max(o["t"] for o in _words(d["items"]))
        d["end"]=round(max(d["end"],lastT+1.0),3); prev_end=d["end"]
    if insert and ins:
        insert["end"]=round(ins["close"]+0.6,3)
        ins["ball"][-1][0]=ins["close"]                     # ball is back on her lap before the circle closes
        ins["cam"][-1][0]=round(ins["close"]-1.0,3)          # camera settled before the close

PRE=3/25
def _caption_wait(chunks,start):
    """latest moment a device/insert may start so the caption block right before it keeps its last word >= 0.8 s"""
    prev=[c for c in chunks if c[0]["t"]<start-0.05]
    if not prev: return start
    last=max(o["t"] for o in prev[-1]); return max(start,last-PRE+0.8)
def insert_timing(ins,insert,chunks):
    ins["_open0"],ins["_close0"]=ins["open"],ins["close"]
    # 1) the insert waits for the caption before it
    insert["drop_from"]=insert["start"]
    o2=_caption_wait(chunks,ins["open"])+0.08
    d=round(o2-ins["open"],3)
    if d>0:
        ins["open"]=round(ins["open"]+d,3); insert["start"]=round(insert["start"]+d,3); fl=ins["open"]+0.5
        for c in ins["cards"]:
            c["t"]=max(c["t"],fl)
            for L in c.get("titles",[])+c.get("subs",[])+c.get("chips",[]):
                L["t"]=max(L["t"],fl)
                if L.get("wt"): L["wt"]=[max(x,fl) for x in L["wt"]]
        for m in ins.get("marks",[]): m["t"]=max(m["t"],fl)
        for b in ins["ball"][1:]: b[0]=max(b[0],fl)
        for k in ins["cam"][1:]: k[0]=max(k[0],ins["open"]-0.05)
    # 2) camera pulls back only after the last word inside the insert; ball returns after the camera settles; then the circle closes
    tl=0
    for c in ins["cards"]:
        for L in c.get("titles",[])+c.get("subs",[]): tl=max(tl,L["wt"][-1] if L.get("wt") else L["t"]+0.12*(len(L["text"].split())-1))
        for L in c.get("chips",[]): tl=max(tl,L["t"])
    for m in ins.get("marks",[]): tl=max(tl,m["t"])
    pull=round(tl+0.35,3); ins["cam"][-1]=[pull]+ins["cam"][-1][1:4]+[0.45]
    ins["close"]=round(max(ins["close"],pull+0.75),3)
    ins["ball"][-1][0]=ins["close"]
    if ins["ball"][-2][0]>pull: ins["ball"][-2][0]=pull
    insert["end"]=round(ins["close"]+0.6,3)
def devices_wait(chunks,devices,split):
    for d in devices+([split] if split else []):
        s2=_caption_wait(chunks,d["start"])
        if s2>d["start"]+0.001:
            d["start"]=round(s2,3); _shift(_words(d),s2+0.12)
            if d is split:
                d.setdefault("f1_0",d["f1"]); d["f1"]=max(d["f1"],round(s2+0.12,3))

