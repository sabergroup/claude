set -e
cd "$(dirname "$0")"
N=1462
rm -rf fr fi; mkdir fr fi
rf(){ node -e "
const {chromium}=require('/opt/node22/lib/node_modules/playwright');
(async()=>{ const br=await chromium.launch(); const p=await br.newPage({viewport:{width:1080,height:1920}});
 await p.goto('file://$PWD/$1'); await p.evaluate(()=>document.fonts.ready);
 for(let i=$3;i<$4;i++){ await p.evaluate(t=>seek(t),i/25); await p.locator('#st').screenshot({path:'$PWD/$2/f'+String(i).padStart(4,'0')+'.png',omitBackground:true}); }
 await br.close(); })();"; }
for r in "0 366" "366 732" "732 1098" "1098 $N"; do rf page_full.html fr $r & done; wait
echo overlay done $(date +%T)
for r in "348 403" "403 458" "458 513" "513 568"; do rf page_ins.html fi $r & done; wait
echo insert done $(date +%T)
python3 comp709.py src.mp4 fr,fi $N v.mp4 2>/dev/null || true
echo composite done $(date +%T)
SFX_DIR=sfx2 python3 mixsfx6.py src.mp4 0 58.48 mix.f32 "soft reveal/1.MP3@0.72@0.53" "pop/2.MP3@1.32@0.05" "camera shuter.MP3@5.78@0.165" "camera shuter.MP3@13.28@0.165" \
 "whoosh/big.MP3@14.10@0.56" "pop/1.mp4@14.70@0.09" "Hint , notification/solid.MP3@17.28@0.055" "whoosh/light .MP3@21.95@0.56" \
 "pop/4.MP3@23.60@0.065" "Hint , notification/simble notification.MP3@26.03@0.26" "mouse click 1.MP3@44.22@0.115" "camera shuter.MP3@52.20@0.165" \
 "اصوات تنفع لبداية او نهاية الفيديو/whoosh with impact.MP3@55.96@0.795"
ffmpeg -v error -y -i v.mp4 -f f32le -ar 48000 -ac 2 -i mix.f32 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest va.mp4
python3 sg709.py va.mp4 final.mp4 --fonts fonts
echo all done $(date +%T)
