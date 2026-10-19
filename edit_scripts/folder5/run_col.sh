#!/bin/bash
set -e
S=/tmp/claude-0/-home-user-claude/2734981a-b9b5-54b9-962c-2e64b7aa8111/scratchpad; P=$S/f5/p; cd $P
src="$S/b5/محفزات الكولاجين.mp4"; N=1340; dur=53.6; a=329; b=565
rm -rf frc fic; mkdir -p frc fic
q=$((N/4)); for r in "0 $q" "$q $((2*q))" "$((2*q)) $((3*q))" "$((3*q)) $N"; do node rendp.js $P/pp_col.html $P/frc $r & done; wait
q=$(((b-a)/4)); for r in "$a $((a+q))" "$((a+q)) $((a+2*q))" "$((a+2*q)) $((a+3*q))" "$((a+3*q)) $b"; do node rendp.js $P/ipage_col.html $P/fic $r & done; wait
echo "frames $(ls frc|wc -l) insert $(ls fic|wc -l)"
python3 compg2.py "$src" frc fic $N reel_c.mp4
SFX_DIR=$S/sfx2 python3 /home/user/claude/.claude/skills/montage/scripts/mixsfx.py "$src" 0 $dur mixc.f32 \
 "soft reveal/1.MP3@0.45@0.53" "pop/4.MP3@1.2@0.065" "whoosh/light .MP3@8.35@0.56" "whoosh/big.MP3@13.6@0.56" \
 "Hint , notification/info.MP3@16.18@0.125" "pop/3.MP3@17.98@0.06" "Hint , notification/solid.MP3@20.0@0.055" \
 "whoosh/fast paper.MP3@21.8@0.46" "اصوات تنفع لبداية او نهاية الفيديو/whoosh with impact.MP3@51.74@0.795" | tail -2
python3 -c "
import numpy as np
m=np.fromfile('mixc.f32',np.float32); n=int($dur*48000)*2
np.concatenate([m,np.zeros(max(0,n-len(m)),np.float32)])[:n].tofice('mixcp.f32')"
ffmpeg -v error -y -i reel_c.mp4 -f f32le -ar 48000 -ac 2 -i mixcp.f32 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k reel_ca.mp4
python3 /home/user/claude/.claude/skills/marwa-brown-close/scripts/sg_intro.py reel_ca.mp4 final_col.mp4 --fonts $S/f5/fonts >/dev/null 2>&1
echo DONE $(ffprobe -v error -show_entries format=duration -of csv=p=0 final_col.mp4)
