import sys, json
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[2], device="cpu", compute_type="int8")
import numpy as np, subprocess
audio = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",sys.argv[1],"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout, np.float32)
segs, info = m.transcribe(audio, language="ar", word_timestamps=True, beam_size=5, vad_filter=False,
    initial_prompt="فيديو لدكتور تجميل بيتكلم بالعامية المصرية عن التصبغات والبشرة")
out = []
for s in segs:
    for w in s.words:
        out.append((round(w.start,2), round(w.end,2), w.word.strip()))
        print(f"{w.start:6.2f} {w.end:6.2f} {w.word}", flush=True)
json.dump(out, open(sys.argv[3], "w"), ensure_ascii=False)
