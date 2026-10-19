#!/bin/bash
# partial.sh <name> <src> <ranges "a-b,c-d">
S=/tmp/claude-0/-home-user-claude/5b00ce15-a751-5c6f-a77b-d1addef998ec/scratchpad; K=/home/user/claude/.claude/skills/marwa-brown-close/scripts; cd $S/f3
n=$1; src="$2"; ranges=$3
dur=$(python3 -c "import json;print(json.load(open('data_$n.json'))['END']['dur'])"); N=$(python3 -c "print(round($dur*25))")
# main overlay frames only inside the ranges (4 workers per range)
for r in ${ranges//,/ }; do a=$(python3 -c "print(int(${r%-*}*25))"); b=$(python3 -c "print(min($N,int(${r#*-}*25)+1))"); q=$(((b-a)/4+1))
  for k in 0 1 2 3; do s=$((a+k*q)); e=$((s+q)); [ $e -gt $b ] && e=$b; [ $s -lt $e ] && node rendp.js $S/f3/page_$n.html $S/f3/fr_$n $s $e & done; wait; done
# insert frames: timing moved, so the whole insert window is redrawn
rm -rf fi_$n; mkdir -p fi_$n
read a b < <(python3 -c "import json;d=json.load(open('ins_$n.json'));print(int((d['open']-0.3)*25), int((d['close']+0.8)*25))")
q=$(((b-a)/4+1)); for k in 0 1 2 3; do s=$((a+k*q)); e=$((s+q)); [ $e -gt $b ] && e=$b; node rendp.js $S/f3/ipage_$n.html $S/f3/fi_$n $s $e & done; wait
python3 comp3.py "$src" reel_${n}_v1.mp4 fr_$n,fi_$n $N reel_$n.mp4 "$ranges"
mapfile -t A < sfx_$n.txt
SFX_DIR=$S/sfx2 python3 /home/user/claude/.claude/skills/montage/scripts/mixsfx.py "$src" 0 $dur mix_$n.f32 "${A[@]}" | tail -1
python3 -c "
import numpy as np
m=np.fromfile('mix_$n.f32',np.float32); n=int($dur*48000)*2
np.concatenate([m,np.zeros(max(0,n-len(m)),np.float32)])[:n].tofile('mixp_$n.f32')"
ffmpeg -v error -y -i reel_$n.mp4 -f f32le -ar 48000 -ac 2 -i mixp_$n.f32 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k reela_$n.mp4
python3 $K/sg_intro.py reela_$n.mp4 final_$n.mp4 --fonts $S/fonts --fps 25 >/dev/null 2>&1 || echo "SGFAIL"
echo "$n DONE $(ffprobe -v error -select_streams v -show_entries stream=r_frame_rate -of csv=p=0 final_$n.mp4) $(ffprobe -v error -show_entries format=duration -of csv=p=0 final_$n.mp4)"
