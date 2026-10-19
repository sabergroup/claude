# snap word onsets to the real voice onset when whisper starts a word inside a pause
import numpy as np,subprocess,json,sys
a=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i','src.mp4','-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout,np.float32)
h=160; e=20*np.log10(np.sqrt((a[:len(a)//h*h].reshape(-1,h)**2).mean(1))+1e-6)   # 10 ms frames
W=json.load(open(sys.argv[1]))
for o in W:
    i0,i1=int(round(o['s']*100)),int(o['e']*100)
    # a real pause (>=120 ms, < -40 dB) that begins in the first 0.15 s of the word = whisper glued the pause onto it
    j=next((j for j in range(i0,min(i0+15,i1)) if max(e[j:j+12])<-40),None)
    if j is not None:
        k=j
        while k<i1+8 and not (e[k]>-28 and e[k+1]>-28 and e[k+2]>-28): k+=1
        if k<i1+8 and k/100-o['s']>0.04: print(o['w'],o['s'],'->',k/100); o['s']=round(k/100,3)
json.dump(W,open(sys.argv[2],'w'),ensure_ascii=False,indent=0)
