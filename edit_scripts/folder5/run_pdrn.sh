#!/bin/bash
set -e
S=/tmp/claude-0/-home-user-claude/2734981a-b9b5-54b9-962c-2e64b7aa8111/scratchpad; P=$S/f5/p; cd $P
src="$S/b5/ال pdrn .mp4"; N=1238; dur=49.52; a=425; b=646
rm -rf fr fi; mkdir -p fr fi
q=$((N/4)); for r in "0 $q" "$q $((2*q))" "$((2*q)) $((3*q))" "$((3*q)) $N"; do node rendp.js $P/pp_pdrn_D.html $P/fr $r & done; wait
q=$(((b-a)/4)); for r in "$a $((a+q))" "$((a+q)) $((a+2*q))" "$((a+2*q)) $((a+3*q))" "$((a+3*q)) $b"; do node rendp.js $P/ipage_pdrn.html $P/fi $r & done; wait
echo "frames $(ls fr|wc -l) insert $(ls fi|wc -l)"
python3 compg2.py "$src" fr fi $N reel.mp4
SFX_DIR=$S/sfx2 python3 /home/user/claude/.claude/skills/montage/scripts/mixsfx.py "$src" 0 $dur mix.f32 \
 "soft reveal/1.MP3@0.45@0.53" "pop/2.MP3@1.2@0.05" "whoosh/light .MP3@8.5@0.56" "whoosh/big.MP3@17.45@0.56" \
 "paper.MP3@20.0@0.275" "Hint , notification/solid.MP3@21.22@0.055" "pop/3.MP3@22.8@0.06" "pop/4.MP3@24.34@0.065" \
 "whoosh/fast paper.MP3@25.05@0.46" "معلومة مهمة في اول اخر الفيديو مش هوك.MP3@37.58@0.075" \
 "اصوات تنفع لبداية او نهاية الفيديو/whoosh with impact.MP3@49.35@0.795" | tail -2
python3 -c "
import numpy as np
m=np.fromfile('mix.f32',np.float32); n=int($dur*48000)*2
np.concatenate([m,np.zeros(max(0,n-len(m)),np.float32)])[:n].tofile('mixp.f32')"
ffmpeg -v error -y -i reel.mp4 -f f32le -ar 48000 -ac 2 -i mixp.f32 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k reel_a.mp4
python3 /home/user/claude/.claude/skills/marwa-brown-close/scripts/sg_intro.py reel_a.mp4 final_pdrn.mp4 --fonts $S/f5/fonts >/dev/null 2>&1
echo DONE $(ffprobe -v error -show_entries format=duration -of csv=p=0 final_pdrn.mp4)
