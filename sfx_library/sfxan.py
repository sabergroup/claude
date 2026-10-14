import os,sys,subprocess,numpy as np,json
D=sys.argv[1]; SR=48000; rows=[]
for f in sorted(os.listdir(D)):
    a=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",os.path.join(D,f),"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout,np.float32)
    if len(a)==0: rows.append(dict(f=f,err=1)); continue
    h=480; n=len(a)//h; fr=a[:n*h].reshape(n,h); rms=np.sqrt((fr**2).mean(1))+1e-9; db=20*np.log10(rms)
    pk=db.max(); act=np.where(db>pk-30)[0]
    on=act[0]*0.01; off=act[-1]*0.01; pkt=np.argmax(db)*0.01
    # tail: time from peak until -20dB
    after=np.where(db[np.argmax(db):]<pk-20)[0]; dec=(after[0]*0.01) if len(after) else (n*0.01-pkt)
    seg=a[int(on*SR):int(off*SR)+1]
    sp=np.abs(np.fft.rfft(seg*np.hanning(len(seg)))) if len(seg)>64 else np.ones(10)
    fq=np.fft.rfftfreq(len(seg),1/SR) if len(seg)>64 else np.arange(10)
    cen=float((sp*fq).sum()/sp.sum())
    lo=float(sp[fq<250].sum()/sp.sum())
    # rough shape: rise time to peak
    rows.append(dict(f=f,dur=round(len(a)/SR,2),on=round(on,2),peak=round(pkt,2),end=round(off,2),rise=round(pkt-on,2),decay=round(dec,2),
        peak_db=round(float(pk),1),loud_db=round(float(20*np.log10(np.sqrt((seg**2).mean())+1e-9)),1),centroid=int(cen),low=round(lo,2)))
json.dump(rows,open(sys.argv[2],"w"),indent=0)
for r in rows: print(r)
