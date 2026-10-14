import json,sys
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",device="cpu",compute_type="int8")
import numpy as np,soundfile as sf
aud,_sr=sf.read(sys.argv[1],dtype="float32")
segs,_=m.transcribe(aud,language="ar",word_timestamps=True,vad_filter=False,beam_size=5,initial_prompt="ماما دايما تقولك ماتوطيش رقبتك وانتي ماسكة الموبايل")
out=[]
for s in segs:
  for w in s.words: out.append((round(w.start,2),round(w.end,2),w.word.strip()))
  print(f"{s.start:.2f}-{s.end:.2f} {s.text}")
json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False)
