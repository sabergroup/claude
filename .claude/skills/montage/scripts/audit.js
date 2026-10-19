const {chromium}=require('/opt/node-tools/node_modules/playwright');
(async()=>{ const br=await chromium.launch(); const p=await br.newPage({viewport:{width:1080,height:1920}}); const errs=[]; p.on('pageerror',e=>errs.push(String(e)));
 await p.goto('file://'+process.argv[2]); await p.evaluate(()=>document.fonts.ready); await p.evaluate(()=>seek(1));
 const a=await p.evaluate(()=>audit()); const bad=a.filter(r=>r[2]<0.8); console.log(process.argv[2].split('/').pop(),'words',a.length,'short',JSON.stringify(bad)); if(errs.length) console.log('ERR',errs); await br.close(); })();
