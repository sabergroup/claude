import numpy as np, json
S="/tmp/claude-0/-home-user-claude/5b00ce15-a751-5c6f-a77b-d1addef998ec/scratchpad"
SR=48000
A=np.fromfile(f"{S}/src/a48.f32",np.float32).reshape(-1,2)
mono=A.mean(1); h=480; n=len(mono)//h
db=20*np.log10(np.sqrt((mono[:n*h].reshape(n,h)**2).mean(1))+1e-9)
W=json.load(open(f"{S}/words.json"))
def zc(t, side=0.004):
    """snap to nearest zero crossing of both channels' mean within ±4ms"""
    i=int(round(t*SR)); w=int(side*SR); seg=mono[i-w:i+w]
    cand=np.where(np.sign(seg[:-1])!=np.sign(seg[1:]))[0]
    if len(cand)==0: return i
    return i-w+cand[np.argmin(np.abs(cand-w))]+1
PIECES=[(9.335,13.57),(0.12,9.335),(13.57,41.36)]
KEEP=0.065; MINRUN=0.20
def trim(a,b,last):
    out=[]; cur=a; i0,i1=int(a*100),int(b*100)
    q=db[i0:i1]<-55; j=0
    while j<len(q):
        if q[j]:
            k=j
            while k<len(q) and q[k]: k+=1
            s,e=(i0+j)/100,(i0+k)/100
            if e-s>MINRUN and s>a+0.05 and not (last and k>=len(q)-1):
                out.append((cur,s+KEEP)); cur=e-KEEP
            j=k
        else: j+=1
    out.append((cur,b)); return out
segs=[]
for pi,(a,b) in enumerate(PIECES):
    for s,e in trim(a,b,pi==len(PIECES)-1): segs.append((zc(s),zc(e)))
# output timeline
tl=[]; t=0
for s,e in segs:
    tl.append((t,s,e)); t+=(e-s)
TOTAL=t  # samples
def src2out(ts):
    """map a source time to output time (first matching segment)"""
    i=ts*SR
    for o,s,e in tl:
        if s-1e-6<=i<e: return (o+i-s)/SR
    # if inside a removed gap, snap to next segment start
    best=None
    for o,s,e in tl:
        if s>=i and (best is None or s<best[1]): best=(o,s)
    return best[0]/SR
def out2src(to):
    i=to*SR
    for o,s,e in tl:
        if o<=i<o+(e-s): return (s+i-o)/SR
    o,s,e=tl[-1]; return e/SR
if __name__=="__main__":
    for o,s,e in tl: print(f"out {o/SR:6.3f}  src {s/SR:6.3f}-{e/SR:6.3f}  len {(e-s)/SR:.3f}")
    print("total",TOTAL/SR)
