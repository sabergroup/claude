const {chromium}=require('/opt/node-tools/node_modules/playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();await p.goto('file://'+process.argv[2]);
const r=await p.evaluate(()=>blocks.map(B=>({s:+B.start.toFixed(2),l:+B.leave.toFixed(2),w:B.c.map(o=>o.w+' '+o.t.toFixed(2)+'→'+o.ta.toFixed(2)).join(' | ')})));
console.log(r.map(x=>JSON.stringify(x)).join('\n'));await b.close();})();
