import json,subprocess,numpy as np,sys
S=sys.argv[1]; SR=48000
EV=json.load(open(f"{S}/sfx_events.json")); cat=json.load(open("/home/user/claude/sfx_library/catalog.json"))
ban={s["file"] for s in cat["sounds"] if s.get("banned")}
rows=[]
for f,info in EV.items():
    if f in ban: continue
    a=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f"{S}/sfx/{f}","-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout,np.float32)
    for k,e in enumerate(info["events"]):
        seg=a[int(e["start"]*SR):int(e["end"]*SR)]
        if len(seg)<1024: continue
        sp=np.abs(np.fft.rfft(seg*np.hanning(len(seg))))+1e-9; fq=np.fft.rfftfreq(len(seg),1/SR)
        band=(fq>200)&(fq<12000); s=sp[band]
        flat=float(np.exp(np.log(s).mean())/s.mean())          # 0=pure tone, 1=noise
        # tonal peak share: energy in top 1% bins
        srt=np.sort(s**2)[::-1]; peak_share=float(srt[:max(1,len(srt)//100)].sum()/srt.sum())
        f0=float(fq[band][np.argmax(s)])
        env=np.abs(seg); att=np.argmax(env)/SR
        rows.append((f,k,e["start"],e["end"],round(e["dur"],2),round(flat,3),round(peak_share,2),int(f0),int(e["centroid"]),round(att,3)))
rows.sort(key=lambda r:-r[6])
print("file | ev | start-end | dur | flatness | tonal_share | main_freq | centroid | attack")
for r in rows[:60]: print(" | ".join(map(str,r)))
json.dump(rows,open(f"{S}/tonal.json","w"))
