#!/bin/bash
# usage: run.sh <name>   (overlay + insert frames on 4 cores -> composite -> sfx -> credit)
F=/tmp/claude-0/-home-user-claude/e25184d4-7e44-5b51-8336-74c4a252bb1f/scratchpad/f1; M=/home/user/claude/.claude/skills/montage/scripts; K=/home/user/claude/.claude/skills/marwa-brown-close/scripts
n=$1; cd $F/w; src=$F/src/$n.mp4
dur=$(python3 -c "import json;print(json.load(open('data_$n.json'))['END']['dur'])"); N=$(python3 -c "print(round($dur*25))")
read a b < <(python3 -c "import json;d=json.load(open('ins_$n.json'));print(int((d['open']-0.3)*25), int((d['close']+0.8)*25))")
rm -rf fr_$n fi_$n; mkdir -p fr_$n fi_$n
q=$((N/4)); for r in "0 $q" "$q $((2*q))" "$((2*q)) $((3*q))" "$((3*q)) $N"; do node $M/render_frames.js $F/w/page_$n.html $F/w/fr_$n $r & done; wait
q=$(((b-a)/4)); for r in "$a $((a+q))" "$((a+q)) $((a+2*q))" "$((a+2*q)) $((a+3*q))" "$((a+3*q)) $b"; do node $M/render_frames.js $F/w/ipage_$n.html $F/w/fi_$n $r & done; wait
echo "$n frames $(ls fr_$n | wc -l)/$N insert $(ls fi_$n | wc -l)"
python3 $M/composite.py "$src" fr_$n,fi_$n $N reel_$n.mp4
mapfile -t A < sfx_$n.txt
SFX_DIR=$F/../sfx2 python3 $M/mixsfx.py "$src" 0 $dur mix_$n.f32 "${A[@]}"
python3 -c "
import numpy as np
m=np.fromfile('mix_$n.f32',np.float32); n=int($dur*48000)*2
np.concatenate([m,np.zeros(max(0,n-len(m)),np.float32)])[:n].tofile('mixp_$n.f32')"
ffmpeg -v error -y -i reel_$n.mp4 -f f32le -ar 48000 -ac 2 -i mixp_$n.f32 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k reela_$n.mp4
python3 $K/sg_intro.py reela_$n.mp4 final_$n.mp4 --fonts $F/fonts
ffprobe -v error -show_entries stream=r_frame_rate,nb_frames:format=duration -of compact final_$n.mp4
echo "$n DONE"
