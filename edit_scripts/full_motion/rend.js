const {chromium}=require('/opt/node-tools/node_modules/playwright');
(async()=>{ const [,,page,out,dur,only]=process.argv;
 const b=await chromium.launch();
 const p=await b.newPage({viewport:{width:1080,height:1920}});
 await p.goto('file://'+page); await p.evaluate(()=>document.fonts.ready);
 const ts= only? only.split(',').map(Number) : [...Array(Math.round(+dur*25)).keys()].map(i=>i/25);
 for(let i=0;i<ts.length;i++){ await p.evaluate(t=>seek(t),ts[i]);
   await p.locator('#st').screenshot({path:`${out}/f${String(i).padStart(4,'0')}.png`,omitBackground:true}); }
 await b.close(); })();
