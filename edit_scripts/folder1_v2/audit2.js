const {chromium}=require('/opt/node-tools/node_modules/playwright');
(async()=>{ const br=await chromium.launch(); const p=await br.newPage({viewport:{width:1080,height:1920}}); const errs=[]; p.on('pageerror',e=>errs.push(String(e)));
 await p.goto('file://'+process.argv[2]); await p.evaluate(()=>document.fonts.ready); await p.evaluate(()=>seek(1));
 const a=await p.evaluate(()=>audit()); const bad=a.filter(r=>r[2]<(r[0]=='cap'?0.8:0.8));
 // widest caption row / device group
 const wmax=await p.evaluate(()=>{ let m=[]; document.querySelectorAll('.row,.grp').forEach(r=>{ const ks=[...r.children].map(c=>c.getBoundingClientRect()); const v=ks.length?Math.max(...ks.map(k=>k.right))-Math.min(...ks.map(k=>k.left)):0; if(v>800) m.push([Math.round(v),r.textContent]); }); return m; });
 console.log(process.argv[2].split('/').pop(),'words',a.length,'short',JSON.stringify(bad),'wide',JSON.stringify(wmax)); if(errs.length) console.log('ERR',errs); await br.close(); })();
