import sys,numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",device="cpu",compute_type="int8")
a=np.fromfile(sys.argv[1],np.float32).reshape(-1,2).mean(1)[::3].copy()  # 16k
for spec in sys.argv[2:]:
    t0,t1=map(float,spec.split(':'))
    seg=a[int(t0*16000):int(t1*16000)]
    segs,_=m.transcribe(np.concatenate([np.zeros(8000,np.float32),seg,np.zeros(8000,np.float32)]),language="ar",beam_size=5)
    print(spec,'|',' '.join(s.text for s in segs))
