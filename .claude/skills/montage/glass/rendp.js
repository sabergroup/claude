const {chromium}=require('/opt/node-tools/node_modules/playwright');
(async()=>{ const [,,page,out,a,b]=process.argv;
 const br=await chromium.launch(); const p=await br.newPage({viewport:{width:1080,height:1920}});
 await p.goto('file://'+page); await p.evaluate(()=>document.fonts.ready);
 for(let i=+a;i<+b;i++){ await p.evaluate(t=>seek(t),i/25);
   await p.locator('#st').screenshot({path:`${out}/f${String(i).padStart(4,'0')}.png`,omitBackground:true}); }
 await br.close(); })();
