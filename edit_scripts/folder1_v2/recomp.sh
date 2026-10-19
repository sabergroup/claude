#!/bin/bash
F=/tmp/claude-0/-home-user-claude/e25184d4-7e44-5b51-8336-74c4a252bb1f/scratchpad/f1; K=/home/user/claude/.claude/skills/marwa-brown-close/scripts
cd $F/w
for n in "$@"; do
 dur=$(python3 -c "import json;print(json.load(open('data_$n.json'))['END']['dur'])"); N=$(python3 -c "print(round($dur*25))")
 python3 $F/b/composite.py $F/src/$n.mp4 fr_$n,fi_$n $N reel_$n.mp4
 ffmpeg -v error -y -i reel_$n.mp4 -f f32le -ar 48000 -ac 2 -i mixp_$n.f32 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k reela_$n.mp4
 python3 $K/sg_intro.py reela_$n.mp4 final_$n.mp4 --fonts $F/fonts; echo "$n DONE"
done
