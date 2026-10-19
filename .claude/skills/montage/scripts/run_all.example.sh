#!/bin/bash
S=/tmp/claude-0/-home-user-claude/5b00ce15-a751-5c6f-a77b-d1addef998ec/scratchpad; K=/home/user/claude/.claude/skills/marwa-brown-close/scripts; cd $S/f3
declare -A SRC=([hairloss]="$S/b3/تساقط الشعر.mp4" [postpartum]="$S/b3/تساقط الشعر بعد الولاده.mp4" [dandruff]="$S/b3/القشره.mp4")
for n in hairloss postpartum dandruff; do
  src="${SRC[$n]}"; dur=$(python3 -c "import json;print(json.load(open('data_$n.json'))['END']['dur'])"); N=$(python3 -c "print(round($dur*25))")
  read a b < <(python3 -c "import json;d=json.load(open('ins_$n.json'));print(int((d['open']-0.3)*25), int((d['close']+0.8)*25))")
  rm -rf fr_$n fi_$n; mkdir -p fr_$n fi_$n
  q=$((N/4)); for r in "0 $q" "$q $((2*q))" "$((2*q)) $((3*q))" "$((3*q)) $N"; do node rendp.js $S/f3/page_$n.html $S/f3/fr_$n $r & done; wait
  q=$(((b-a)/4)); for r in "$a $((a+q))" "$((a+q)) $((a+2*q))" "$((a+2*q)) $((a+3*q))" "$((a+3*q)) $b"; do node rendp.js $S/f3/ipage_$n.html $S/f3/fi_$n $r & done; wait
  echo "$n frames $(ls fr_$n | wc -l) insert $(ls fi_$n | wc -l)"
  python3 comp2.py "$src" fr_$n,fi_$n $N reel_$n.mp4
  mapfile -t A < sfx_$n.txt
  SFX_DIR=$S/sfx2 python3 /home/user/claude/.claude/skills/montage/scripts/mixsfx.py "$src" 0 $dur mix_$n.f32 "${A[@]}" | tail -1
  python3 -c "
import numpy as np
m=np.fromfile('mix_$n.f32',np.float32); n=int($dur*48000)*2
np.concatenate([m,np.zeros(max(0,n-len(m)),np.float32)])[:n].tofile('mixp_$n.f32')"
  ffmpeg -v error -y -i reel_$n.mp4 -f f32le -ar 48000 -ac 2 -i mixp_$n.f32 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k reela_$n.mp4
  python3 $K/sg_intro.py reela_$n.mp4 final_$n.mp4 --fonts $S/fonts >/dev/null 2>&1
  echo "$n DONE $(ffprobe -v error -show_entries format=duration -of csv=p=0 final_$n.mp4)"
done
