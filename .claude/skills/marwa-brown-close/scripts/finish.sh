#!/bin/bash
# usage: finish.sh <WORK>  -> render overlays, keep the ORIGINAL audio stream (copy), add Saber Group credit, verify audio
set -e
S=/tmp/claude-0/-home-user-claude/5b00ce15-a751-5c6f-a77b-d1addef998ec/scratchpad; K=/home/user/claude/.claude/skills/marwa-brown-close; W=$1
cd $W && WORK=$W python3 $K/scripts/render.py $W/reel.mp4 2>&1 | grep -E "Trace|Error:|cuts found" || true
ffmpeg -v error -y -i $W/reel.mp4 -i $W/src/vid.mp4 -map 0:v -map 1:a -c copy $W/reel_a.mp4
python3 $K/scripts/sg_intro.py $W/reel_a.mp4 $W/final.mp4 --fonts $S/fonts >/dev/null
python3 - "$W" <<'PY'
import subprocess,numpy as np,sys
W=sys.argv[1]
def pcm(f): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f,"-map","0:a","-f","s16le","-"],capture_output=True).stdout,np.int16)
print(W.split("/")[-1],"audio bit-identical:",np.array_equal(pcm(W+"/src/vid.mp4"),pcm(W+"/final.mp4")))
PY
