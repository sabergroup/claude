import json,math,re
W=json.load(open('words_ref.json')); P=3/25; NB=' '
FIX={4:'بيضا',6:'الجلد',16:'بهاق',22:'بيضا',27:'بهاق',31:'جدًا',34:'جدًا',40:'بيضا',43:'النخالة',44:'البيضا',46:'غالبًا',50:'خصوصًا',60:'كتير',67:'التينيا',69:'التينيا',70:'الملونة',75:'الإكزيما',78:'التهابات',88:'الجلد',96:'بلون',97:'غامق',98:'أحيانًا',105:'البهاق',106:'شوية',120:'الضوء',122:"Wood's"+NB+'Light',128:'المناسبة',132:'بهاق',133:'فحاليًا',138:'جدًا',146:'البهاق',153:'البيت',157:'نتخضش',158:'ونستعين',159:'بالطبيب',169:'لينا'}
MERGE={122:(123,"Wood's"+NB+'Light')}
G={4,16,22,27,31,36,44,49,53,59,70,75,79,84,97,103,105,111,113,122,128,138,144,151,160,166}
W[28]['s']=min(W[28]['s'],W[29]['s']-0.05)
def w(i,t=None):
    j,txt=MERGE.get(i,(i,FIX.get(i,W[i]['w'].strip('.،'))))
    txt=re.sub("تى(?=$|\\u00a0)","تي",txt)   # Plex draws «تى» like «ق» (حتى→حق): final ي reads right
    return {"w":txt,"t":round(t if t is not None else W[i]['s'],3),"e":W[j]['e'],"g":i in G}
def sh(o,t): o['t']=round(max(o['t'],t),3); return o
B=[[[0,1,2],[3,4]],[[5,6]],[[7,8,9],[10,11]],[[12,13],[14,15,16]],[[17,18]],[[19,20],[21,22]],[[23,24],[25,26,27]],
   [[28,29],[30,31]],[[32,33,34],[35,36]],[[37,38],[39,40]],
   [[107,108],[109,110]],[[111,112,113]],[[114,115],[116,117,118]],[[119,120],[121,122]],
   [[124,125],[126,127,128]],[[129,130],[131,132]],[[133,134,135],[136,137,138]],[[139,140],[141,142,143]],[[144,145,146]],
   [[147,148],[149,150,151]],[[152,153]],[[154,155],[156,157]],[[158,159],[160]],[[161,162,163]],[[164,165,166]],[[167,168,169]]]
chunks=[[dict(w(i),r=ri) for ri,row in enumerate(b) for i in row] for b in B]
# ---- devices: ١ النخالية البيضا, ٢ التينيا الملونة (num), then the comparison after the insert
def items_hold(groups,t0):
    out=[]; prev=None
    for g in groups:
        ws=[w(i) for i in g]
        if prev is not None:
            tt=max(ws[0]['t'],prev+0.8); 
            for o in ws: sh(o,tt)
        if out==[] : 
            for o in ws: sh(o,t0)
        out.append({"t":ws[0]['t'],"words":ws}); prev=max(o['t'] for o in ws)
    return out,prev
it1,l1=items_hold([[45,46,47],[48,49],[50,51,52],[53,54,55],[56,57],[58,59,60]],15.38)
d1={"type":"num","num":"١","start":14.38,"ringT":14.42,"title":[sh(w(41),14.42),w(42),w(43),w(44)],"items":it1,"end":round(l1+1.0,3)}
s2=d1['end']+0.04
it2,l2=items_hold([[64,65,66,67],[68,69,70]],s2)
d2={"type":"num","num":"٢","start":round(s2,3),"ringT":round(s2+0.04,3),"title":[sh(w(61),s2+0.04),sh(w(62),s2+0.08),sh(w(63),s2+0.12)],"items":it2,"end":round(l2+1.0,3)}
# insert (٣): كمان ممكن تظهر بعد الإكزيما / أو بعد التهابات الجلد / أو حتى بعد الجروح السطحية
OPEN=round(d2['end']+0.04,3); CLOSE=32.95
def L(ix,y,size=None,g=False,t0=None):
    ws=[w(i) for i in ix]
    if t0:
        for o in ws: sh(o,t0)
    d={"text":" ".join(o['w'] for o in ws),"y":y,"t":ws[0]['t'],"wt":[o['t'] for o in ws]}
    if size: d["size"]=size
    if g: d["g"]=True
    return d
X,CW=130,820
cards=[{"x":X,"y":270,"w":CW,"h":190,"t":OPEN+0.06,"num":"٣","titles":[L([71,72,73],64,54,t0=OPEN+0.06)]},
       {"x":X,"y":510,"w":CW,"h":220,"t":28.34,"titles":[L([74],46,40),L([75],112,60,g=True)]},
       {"x":X,"y":780,"w":CW,"h":220,"t":29.42,"titles":[L([76,77],46,40),L([78,79],112,58,g=True)]},
       {"x":X,"y":1050,"w":CW,"h":220,"t":30.8,"titles":[L([80,81,82],46,40),L([83,84],112,58,g=True)]}]
def P2(x,y): return f"{x:.1f} {y:.1f}"
def circ(cx,cy,r): return f"M{P2(cx,cy-r)} A{r} {r} 0 1 1 {P2(cx-0.1,cy-r)}"
def off(cmds,cx,cy):   # cmds: list of (letter, [x,y,...]) relative to icon centre
    return " ".join(c+" "+" ".join(P2(cx+a,cy+b) for a,b in zip(v[0::2],v[1::2])) for c,v in cmds)
def rot(pts,cx,cy,deg):
    a=math.radians(deg); return [(cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a)) for x,y in pts]
def poly(pts): return "M"+" L".join(P2(x,y) for x,y in pts)+" Z"
IC=lambda c: (X+105, c['y']+c['h']/2)
marks=[]
cx,cy=IC(cards[0]); marks+= [{"d":circ(cx,cy,40),"t":cards[0]['t']},{"d":circ(cx,cy,14),"t":cards[0]['t']+0.2}]          # white spot
cx,cy=IC(cards[1]); marks+= [{"d":off([("M",[-38,-10]),("C",[-40,-34,-10,-44,8,-36]),("C",[34,-30,42,-6,34,14]),("C",[26,36,-6,42,-24,30]),("C",[-38,22,-36,6,-38,-10])],cx,cy),"t":28.34},
                             {"d":circ(cx-10,cy-8,4)+" "+circ(cx+10,cy+4,4)+" "+circ(cx-4,cy+16,4),"t":28.58,"ts":.3}]   # eczema patch
cx,cy=IC(cards[2]); marks+= [{"d":off([("M",[0,-42]),("C",[14,-24,30,-12,30,10]),("C",[30,30,16,42,0,42]),("C",[-16,42,-30,30,-30,10]),("C",[-30,-6,-18,-14,-14,-26]),("C",[-8,-14,-4,-10,0,-6]),("C",[2,-20,0,-30,0,-42])],cx,cy),"t":29.82}]   # inflammation
cx,cy=IC(cards[3]); marks+= [{"d":poly(rot([(-48,-17),(48,-17),(48,17),(-48,17)],cx,cy,-40)),"t":31.4},{"d":poly(rot([(-15,-17),(15,-17),(15,17),(-15,17)],cx,cy,-40)),"t":31.6,"ts":.3}]   # plaster
cam=[[0,540,955,1.0],[OPEN,540,365,1.12],[28.1,540,620,1.12],[29.2,540,890,1.12],[30.6,540,1160,1.12],[32.15,540,770,0.9]]
ball=[[OPEN,{"s":{"x":540,"y":955}}],[27.6,{"wd":[0,"t",0,1]}],[28.34,{"wd":[1,"t",0,0]}],[28.58,{"wd":[1,"t",1,0]}],[29.58,{"wd":[2,"t",0,1]}],[29.82,{"wd":[2,"t",1,0]}],
      [31.24,{"wd":[3,"t",0,2]}],[31.4,{"wd":[3,"t",1,0]}],[31.86,{"wd":[3,"t",1,1]}],[CLOSE,{"s":{"x":540,"y":955}}]]
for m in marks: m["sw"]=4
INS={"open":OPEN,"close":CLOSE,"cards":cards,"cam":cam,"ball":ball,"marks":marks}
iend=round(CLOSE+0.6,3)
# comparison after the insert: «مش كل الجروح لازم تسيب أثر بلون غامق» ← «أحيانًا الجروح بتسيب أثر بلون فاتح يشبه البهاق شوية»
c1=[sh(w(89),iend+0.04),sh(w(90),iend+0.08),w(91),w(92)]
d3={"type":"cmp","start":round(iend+0.02,3),"sections":[{"head":c1,"traits":[[w(93),w(94)],[w(95),w(96),w(97)]]},
     {"head":[sh(w(98),37.73),w(99),w(100)],"traits":[[w(101),w(102),w(103)],[w(104),w(105),w(106)]]}]}
d3["end"]=round(max(42.22,41.52+1.0),3)
END=70.10; CL=70.86; DUR=round(CL+(3.16-0.795)+0.15,2)
D={"lap":[915]*5,"cuts":[9.04,34.0,40.72,70.92],"chunks":chunks,"devices":[d1,d2,d3],"insert":{"start":OPEN,"end":iend},
   "trans":[[9.04,"flash"],[34.0,"sweep"],[40.72,"flash"]],
   "END":{"start":END,"close":CL,"dur":DUR,"cy":640},"capBase":110,"nameY":265,
   "N":{"appear":0.38,"stretch":0.54,"split":0.66,"dr":0.66,"marwa":1.12,"magdy":1.34,"title":1.82,"exit":5.25}}
json.dump(D,open('data_full.json','w'),ensure_ascii=False); json.dump(INS,open('ins_full.json','w'),ensure_ascii=False)
open('page_full.html','w').write(open('../f6_overlay_full.html').read().replace('DATA',json.dumps(D,ensure_ascii=False)))
open('page_ins.html','w').write(open('ins3.html').read().replace('DATA',json.dumps(INS,ensure_ascii=False)))
print('dur',DUR,'frames',round(DUR*25),'d1',d1['start'],d1['end'],'d2',d2['start'],d2['end'],'ins',OPEN,CLOSE,iend)
