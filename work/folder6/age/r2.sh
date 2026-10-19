set -e
cd "$(dirname "$0")"
N=1710
rm -rf fr fi; mkdir fr fi
rf(){ node -e "
const {chromium}=require('/opt/node22/lib/node_modules/playwright');
(async()=>{ const br=await chromium.launch(); const p=await br.newPage({viewport:{width:1080,height:1920}});
 await p.goto('file://$PWD/$1'); await p.evaluate(()=>document.fonts.ready);
 for(let i=$3;i<$4;i++){ await p.evaluate(t=>seek(t),i/25); await p.locator('#st').screenshot({path:'$PWD/$2/f'+String(i).padStart(4,'0')+'.png',omitBackground:true}); }
 await br.close(); })();"; }
for r in "0 428" "428 856" "856 1284" "1284 $N"; do rf page_full.html fr $r & done; wait
echo overlay done $(date +%T)
for r in "711 770" "770 829" "829 888" "888 945"; do rf page_ins.html fi $r & done; wait
echo insert done $(date +%T)
python3 ../comp709.py src.mp4 fr,fi $N v.mp4 2>/dev/null || true
echo composite done $(date +%T)
SFX_DIR=sfx2 python3 ../mixsfx6.py src.mp4 0 68.42 mix.f32 "soft reveal/1.MP3@0.42@0.53" "pop/2.MP3@1.06@0.05" "معلومة مهمة في اول اخر الفيديو مش هوك.MP3@6.31@0.075" \
 "pop/1.mp4@13.82@0.09" "Hint , notification/solid.MP3@15.38@0.055" "clock ticking.MP3@17.88@0.055@1.35@2.6" "whoosh/big.MP3@28.75@0.56" "pop/3.MP3@31.32@0.06" \
 "Hint , notification/info.MP3@35.41@0.125" "whoosh/light .MP3@36.95@0.56" "pop/4.MP3@49.24@0.065" "Hint , notification/simble notification.MP3@52.16@0.26" \
 "اصوات تنفع لبداية او نهاية الفيديو/whoosh with impact.MP3@65.90@0.795"
ffmpeg -v error -y -i v.mp4 -f f32le -ar 48000 -ac 2 -i mix.f32 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest va.mp4
python3 ../sg709.py va.mp4 final.mp4 --fonts fonts
echo all done $(date +%T)
