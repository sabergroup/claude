import json,re,difflib
S="/tmp/claude-0/-home-user-claude/e25184d4-7e44-5b51-8336-74c4a252bb1f/scratchpad"
OLD="/home/user/claude/output/batch/01_الطقم_البني_المكتب/"
def norm(s):
    s=re.sub(r"[ً-ْـ؟?.,!ـ]","",s.lower()); s=re.sub("[أإآ]","ا",s); s=s.replace("ة","ه").replace("ى","ي")
    return s
def parse_ch(path):
    g={}; exec(open(path).read(),g); toks=[]
    for li,line in enumerate(g["CH"].strip().split("\n")):
        parts=re.split(r"(?:^|\s)\d+(?:-\d+)?:",line)[1:]
        for p in parts:
            p=p.strip(); toks.append(dict(w=p.lstrip("*"),g=p.startswith("*"),line=li))
    return toks,g
def sim(a,b):
    a,b=norm(a),norm(b)
    return difflib.SequenceMatcher(None,a,b).ratio()
def align(toks,W):
    # subwords
    sub=[(k,p) for k,t in enumerate(toks) for p in t["w"].split(" ")]
    n,m=len(sub),len(W); INF=-1e9
    D=[[INF]*(m+1) for _ in range(n+1)]; B=[[None]*(m+1) for _ in range(n+1)]; D[0][0]=0
    for i in range(n+1):
        for j in range(m+1):
            if D[i][j]==INF: continue
            if i<n and j<m:
                s=sim(sub[i][1],W[j][2])*2-0.6
                if D[i][j]+s>D[i+1][j+1]: D[i+1][j+1]=D[i][j]+s; B[i+1][j+1]=(i,j,"m")
            if i<n and D[i][j]-0.5>D[i+1][j]: D[i+1][j]=D[i][j]-0.5; B[i+1][j]=(i,j,"d")   # display word w/o whisper word (split word)
            if j<m and D[i][j]-0.5>D[i][j+1]: D[i][j+1]=D[i][j]-0.5; B[i][j+1]=(i,j,"w")   # extra whisper word
    i,j=n,m; mp={}; extra=[]
    while i or j:
        pi,pj,k=B[i][j]
        if k=="m": mp[pi]=pj
        elif k=="w": extra.append(pj)
        i,j=pi,pj
    # extra whisper words attach to the previous sub (merged words like ما توطيش)
    att={}
    for j in sorted(extra):
        prev=[i for i,jj in mp.items() if jj<j]; nxt=[i for i,jj in mp.items() if jj>j]
        if j>=len(W)-3 and not nxt: continue          # trailing whisper hallucination after her last word
        pi=max(prev,key=lambda i:mp[i]) if prev else None; ni=min(nxt,key=lambda i:mp[i]) if nxt else None
        if ni is not None and (pi is None or sim(W[j][2]+W[mp[ni]][2],sub[ni][1])>sim(W[mp[pi]][2]+W[j][2],sub[pi][1])): att.setdefault(ni,[]).append(j)
        elif pi is not None: att.setdefault(pi,[]).append(j)
    for k,t in enumerate(toks):
        js=[mp[i] for i,(kk,_) in enumerate(sub) if kk==k and i in mp]+[j for i,(kk,_) in enumerate(sub) if kk==k for j in att.get(i,[])]
        t["js"]=sorted(js)
    for k,t in enumerate(toks):
        if t["js"]: t["t"],t["e"]=W[t["js"][0]][0],W[t["js"][-1]][1]
        else:
            nb=next(toks[q] for q in range(k-1,-1,-1) if toks[q]["js"]); t["t"],t["e"]=W[nb["js"][-1]][0],W[nb["js"][-1]][1]
    return toks,extra
if __name__=="__main__":
    for n,cfg in [("mounjaro","المونجارو_config.py"),("collagen","تحفيز_الكولاجين_config.py"),("neck","خطوط_وتجاعيد_الرقبة_config.py")]:
        W=json.load(open(f"{S}/f1/words_{n}.json")); toks,g=parse_ch(OLD+cfg); toks,ex=align(toks,W)
        print(n,len(toks),"extra",[(j,W[j][2]) for j in ex])
        for k,t in enumerate(toks): print(f"{k}:{t['w']}={'+'.join(W[j][2] for j in t['js'])}@{t['t']}",end="  ")
        print()
