# folder-1 copies of the skill templates: El Messiri + folder colours, fixed lower-third anchor (desk), gold line icons
import json
T="/home/user/claude/.claude/skills/montage/templates/"; B="/tmp/claude-0/-home-user-claude/e25184d4-7e44-5b51-8336-74c4a252bb1f/scratchpad/f1/b/"
h=open(T+"reel_overlay.html").read()
rep=[("Alexandria500.ttf","EM500.ttf"),("Alexandria800.ttf","EM700.ttf"),
 ("#F0C98A","#E9B872"),("#F6EAD6","#F8EEDC"),("rgba(74,42,20,","rgba(52,28,12,"),
 (".w{display:inline-block;font:54px/1.25 A5;color:#F8EEDC;text-shadow:0 3px 10px rgba(52,28,12,.65),0 1px 2px rgba(52,28,12,.5)}",
  ".w{display:inline-block;font:58px/1.25 A5;color:#F8EEDC;text-shadow:0 4px 16px rgba(52,28,12,.8),0 0 30px rgba(52,28,12,.45)}"),
 (".w.g{font-family:A8;color:#E9B872}",".w.g{font-family:A8;font-size:60px;color:#E9B872}"),
 (".w.chip{font-size:46px}",".w.chip{font-size:48px}"),
 (".nw{position:absolute;font:36px/50px MS;color:#F8EEDC;",".nw{position:absolute;font:36px/50px MS;color:#F0D9B3;"),
 (".tt{position:absolute;font:26px/40px MM;color:#F8EEDC;",".tt{position:absolute;font:26px/40px MM;color:#F0D9B3;"),
 ('<path id="mask" fill="#2E1A0D"','<path id="mask" fill="#341C0C"'),
 ("function lap(t){ let y=D.lap[0]; for(let i=0;i<D.cuts.length;i++) y+=(D.lap[i+1]-D.lap[i])*spr(t-D.cuts[i],.22); return y; }","function lap(t){ return D.anchor; }"),
 ("nameSeek(t,{dot:'ndot',path:'np',w:'n',tt:'ntt'},NM,300,150,{});","nameSeek(t,{dot:'ndot',path:'np',w:'n',tt:'ntt'},NM,D.nameY,D.capY,{});\n  iconSeek(t,inIns);"),
 ("const E=D.END, cx=540, cy=760;","const E=D.END, cx=540, cy=D.endY||560;"),
]
for a,b in rep:
    assert a in h,a[:60]; h=h.replace(a,b)
a="if(D.insert) D.chunks=D.chunks.filter("; i=h.index(a); j=h.index("\n",i); h=h[:i]+"// folder 1: blocks never hold insert words, so none is dropped"+h[j:]
icon_js=open(B+"icons.js").read()
h=h.replace("// ---------- name intro:",icon_js+"// ---------- name intro:")
open(B+"reel_f1.html","w").write(h)
i=open(T+"insert_cards.html").read()
for a,b in [("Alexandria500.ttf","EM500.ttf"),("Alexandria800.ttf","EM700.ttf"),("#F0C98A","#E9B872"),("rgba(240,201,138,","rgba(233,184,114,"),("#F6EAD6","#F8EEDC"),("rgba(246,234,214,","rgba(248,238,220,"),("#2E1A0D","#341C0C")]:
    assert a in i,a; i=i.replace(a,b)
# ball placement beside the line comes from the skill template itself
open(B+"ins_f1.html","w").write(i)
print("ok")
