#!/bin/bash
set -e
S=/tmp/claude-0/-home-user-claude/2734981a-b9b5-54b9-962c-2e64b7aa8111/scratchpad; P=$S/f5/p; cd $P
src="$S/b5/الليب فيلر و الليب بوستر.mp4"; N=1004; dur=40.16; a=360; b=652
rm -rf frl fil; mkdir -p frl fil
q=$((N/4)); for r in "0 $q" "$q $((2*q))" "$((2*q)) $((3*q))" "$((3*q)) $N"; do node rendp.js $P/pp_lip.html $P/frl $r & done; wait
q=$(((b-a)/4)); for r in "$a $((a+q))" "$((a+q)) $((a+2*q))" "$((a+2*q)) $((a+3*q))" "$((a+3*q)) $b"; do node rendp.js $P/ipage_lip.html $P/fil $r & done; wait
echo "frames $(ls frl|wc -l) insert $(ls fil|wc -l)"
python3 compg2.py "$src" frl fil $N reel_l.mp4
SFX_DIR=$S/sfx2 python3 /home/user/claude/.claude/skills/montage/scripts/mixsfx.py "$src" 0 $dur mixl.f32 \
 "soft reveal/1.MP3@0.45@0.53" "pop/1.mp4@1.2@0.09" "whoosh/fast paper.MP3@10.7@0.46" "whoosh/big.MP3@14.85@0.56" \
 "pop/3.MP3@16.7@0.06" "pop/4.MP3@17.66@0.065" "Hint , notification/simble notification.MP3@19.34@0.26" \
 "Hint , notification/1.mp4@24.22@0.09" "whoosh/hard paper turn.MP3@25.3@0.43" \
 "اصوات تنفع لبداية او نهاية الفيديو/whoosh with impact.MP3@40.06@0.795" | tail -2
python3 -c "
import numpy as np
m=np.fromfile('mixl.f32',np.float32); n=int($dur*48000)*2
np.concatenate([m,np.zeros(max(0,n-len(m)),np.float32)])[:n].tofile('mixlp.f32')"
ffmpeg -v error -y -i reel_l.mp4 -f f32le -ar 48000 -ac 2 -i mixlp.f32 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k reel_la.mp4
python3 /home/user/claude/.claude/skills/marwa-brown-close/scripts/sg_intro.py reel_la.mp4 final_lip.mp4 --fonts $S/f5/fonts >/dev/null 2>&1
echo DONE $(ffprobe -v error -show_entries format=duration -of csv=p=0 final_lip.mp4)
