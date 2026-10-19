set -e
cd "$(dirname "$0")"
N=1834
rm -rf fr fi; mkdir fr fi
rf(){ node -e "
const {chromium}=require('/opt/node22/lib/node_modules/playwright');
(async()=>{ const br=await chromium.launch(); const p=await br.newPage({viewport:{width:1080,height:1920}});
 await p.goto('file://$PWD/$1'); await p.evaluate(()=>document.fonts.ready);
 for(let i=$3;i<$4;i++){ await p.evaluate(t=>seek(t),i/25); await p.locator('#st').screenshot({path:'$PWD/$2/f'+String(i).padStart(4,'0')+'.png',omitBackground:true}); }
 await br.close(); })();"; }
for r in "0 459" "459 918" "918 1377" "1377 $N"; do rf page_full.html fr $r & done; wait
echo overlay done $(date +%T)
for r in "669 713" "713 757" "757 801" "801 846"; do rf page_ins.html fi $r & done; wait
echo insert done $(date +%T)
python3 ../comp709.py src.mp4 fr,fi $N v.mp4 2>/dev/null || true
echo composite done $(date +%T)
SFX_DIR=sfx2 python3 ../mixsfx6.py src.mp4 0 73.38 mix.f32 "soft reveal/1.MP3@0.66@0.53" "pop/2.MP3@1.34@0.05" "Hint , notification/info.MP3@6.38@0.125" \
 "pop/1.mp4@14.42@0.09" "pop/3.MP3@23.06@0.06" "whoosh/big.MP3@27.08@0.56" "pop/2.MP3@28.34@0.05" "pop/4.MP3@29.42@0.065" "Hint , notification/solid.MP3@30.8@0.055" \
 "whoosh/light .MP3@32.95@0.56" "whoosh/fast paper.MP3@37.73@0.46" "Hint , notification/simble notification.MP3@48.7@0.26" \
 "اصوات تنفع لبداية او نهاية الفيديو/whoosh with impact.MP3@70.86@0.795"
ffmpeg -v error -y -i v.mp4 -f f32le -ar 48000 -ac 2 -i mix.f32 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest va.mp4
python3 ../sg709.py va.mp4 final.mp4 --fonts fonts
echo all done $(date +%T)
