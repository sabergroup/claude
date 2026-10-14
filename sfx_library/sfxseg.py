import os,sys,subprocess,numpy as np,json
D=sys.argv[1]; SR=48000; out={}
for f in sorted(os.listdir(D)):
    a=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",os.path.join(D,f),"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout,np.float32)
    h=240; n=len(a)//h; db=20*np.log10(np.sqrt((a[:n*h].reshape(n,h)**2).mean(1))+1e-9)  # 5ms frames
    pk=db.max(); thr=max(pk-40,-72); on=db>thr
    segs=[]; i=0
    while i<n:
        if on[i]:
            j=i
            while j<n and (on[j] or (j+1<n and on[min(n-1,j+1)])): j+=1
            segs.append([i,j]); i=j
        else: i+=1
    # merge segments separated by < 0.15 s
    m=[]
    for s in segs:
        if m and (s[0]-m[-1][1])*h/SR<0.035: m[-1][1]=s[1]
        else: m.append(s)
    res=[]
    for s,e in m:
        seg=db[s:e]; dur=(e-s)*h/SR
        if dur<0.008 or seg.max()<pk-30: continue
        sp=np.abs(np.fft.rfft(a[s*h:e*h]*np.hanning((e-s)*h))); fq=np.fft.rfftfreq((e-s)*h,1/SR)
        res.append(dict(start=round(s*h/SR,2),end=round(e*h/SR,2),dur=round(dur,2),peak_at=round((s+int(np.argmax(seg)))*h/SR,2),
                        peak_db=round(float(seg.max()),1),centroid=int((sp*fq).sum()/(sp.sum()+1e-9)),low=round(float(sp[fq<250].sum()/(sp.sum()+1e-9)),2)))
    out[f]=dict(len=round(len(a)/SR,2),events=res)
    print(f"{f[:60]:60s} len {len(a)/SR:5.2f}  events {len(res)}: "+"; ".join(f"{r['start']}-{r['end']}" for r in res[:12])+(" ..." if len(res)>12 else ""))
json.dump(out,open(sys.argv[2],"w"),indent=1,ensure_ascii=False)
