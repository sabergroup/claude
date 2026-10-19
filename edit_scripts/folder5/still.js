const {chromium}=require('/opt/node-tools/node_modules/playwright');
(async()=>{ const [,,page,out,...ts]=process.argv;
 const br=await chromium.launch(); const p=await br.newPage({viewport:{width:1080,height:1920}});
 await p.goto('file://'+page); await p.evaluate(()=>document.fonts.ready);
 for(const t of ts){ await p.evaluate(t=>seek(t),+t);
   await p.locator('#st').screenshot({path:`${out}_${t}.png`,omitBackground:true}); }
 await br.close(); })();
