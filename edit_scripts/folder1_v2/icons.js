
// ---------- gold line icons above the caption (desk shots) ----------
const ICONS=ICONDATA, IC=[];
(D.icons||[]).forEach(ic=>{ const g=document.createElementNS('http://www.w3.org/2000/svg','g'); $('Lsvg').appendChild(g);
  const sz=92, ox=540-sz/2, oy=-sz-26, k=sz/100;
  const ps=ICONS[ic.n].map(pl=>{ const p=document.createElementNS('http://www.w3.org/2000/svg','path');
    p.setAttribute('d','M'+pl.map(q=>(ox+q[0]*k).toFixed(1)+' '+(oy+q[1]*k).toFixed(1)).join(' L'));
    p.setAttribute('fill','none'); p.setAttribute('stroke','#E9B872'); p.setAttribute('stroke-width','4.2'); p.setAttribute('stroke-linecap','round'); p.setAttribute('stroke-linejoin','round'); g.appendChild(p); return p; });
  const st=[[ox-30,oy+18,11],[ox+sz+26,oy+8,8],[ox+sz+14,oy+sz-6,6]].map(([x,y,r])=>{ const p=document.createElementNS('http://www.w3.org/2000/svg','path');
    p.setAttribute('fill','#E9B872'); g.appendChild(p); return {p,x,y,r}; });
  ps.forEach(p=>p.L=p.getTotalLength()); IC.push({ic,g,ps,st}); });
function star4(x,y,r){ const q=r*0.28; return `M${x} ${y-r} Q${x+q} ${y-q} ${x+r} ${y} Q${x+q} ${y+q} ${x} ${y+r} Q${x-q} ${y+q} ${x-r} ${y} Q${x-q} ${y-q} ${x} ${y-r}Z`; }
function iconSeek(t,inIns){ IC.forEach(({ic,g,ps,st})=>{ const on=!inIns && t>ic.s-pre-0.02 && t<ic.e+0.5; g.style.visibility=on?'visible':'hidden'; if(!on) return;
  const a=cl(spr(t-(ic.s-pre),.5),0,1), x=cl(spx(t-ic.e,.3),0,1), p=a*(1-x), tot=ps.reduce((s,q)=>s+q.L,0); let left=p*tot;
  ps.forEach(q=>{ const u=Math.max(0,Math.min(q.L,left)); left-=q.L; q.setAttribute('stroke-dasharray',`${u.toFixed(1)} ${q.L+1}`); q.style.opacity=u>0.3?1:0; });
  st.forEach((s,i)=>{ const b=cl(spr(t-(ic.s-pre+.25+.08*i),.35),0,1)*(1-x); s.p.setAttribute('d',b>0.01?star4(s.x,s.y,s.r*b):''); }); }); }
