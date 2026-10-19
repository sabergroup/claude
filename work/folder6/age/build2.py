import json
W=json.load(open('words_ref.json')); P=3/25

NB=' '
FIX={4:'بتجيلي',5:'إمتى',12:'Botox',13:'والـFiller',15:'إنه',16:'ما',17:'فيش',22:'فيه',31:'المشكلة',33:'مثلًا',38:'مضايقاني',42:'العين',46:'إن',51:'التلاتين',56:'دي',57:'خصوصًا',58:'إن',68:'مثلًا',72:'Botox',81:'الخطوط',82:'الثابتة',94:'جدًا',96:'كده',98:'الـFiller',102:'دايمًا',108:'Filler',112:'Filler',115:'Filler',117:'طول؟',119:'برضه',120:'إن',121:'الـFiller',128:'Volume',137:'الوجه',140:'إني',152:'محتاجاه',156:'إني',164:'أيًّا',165:'كان'}
MERGE={78:(79,'Static'+NB+'Lines')}
G={2,12,13,19,31,45,51,61,63,72,93,98,105,117,121,141,142,163,164}
def w(i,t=None):
    j,txt=MERGE.get(i,(i,FIX.get(i,W[i]['w'].strip('.،'))))
    return {"w":txt,"t":round(t if t is not None else W[i]['s'],3),"e":W[j]['e'],"g":i in G}
B=[[[0,1],[2,3,4]],[[5,6,7],[8,9,10]],[[11,12,13]],[[14,15],[16,17,18,19]],[[20,21,22]],[[23,24,25,26]],[[27,28,29],[30,31]],
   [[32,33]],
   [[43,44,45],[46,47,48]],[[49,50,51]],[[52,53],[54,55,56]],
   [[57,58,59],[60,61]],[[62,63],[64,65,66,67]],[[68,69,70],[71,72]],
   [[91,92],[93,94]],[[95,96]],
   [[97,98],[99,100]],[[101,102,103]],[[104,105],[106,107,108]],[[109,110],[111,112]],[[113,114,115],[116,117]],
   [[118,119],[120,121]],[[122,123]],
   [[138,139],[140,141,142]],[[143,144,145],[146,147]],[[148,149],[150,151,152]],[[153,154,155],[156,157,158]],[[159,160],[161,162,163],[164,165]]]
W[148]['s']=min(W[148]['s'],W[149]['s']-0.05)   # whisper swapped «في» and «الإجراء»
chunks=[[dict(w(i),r=ri) for ri,row in enumerate(b) for i in row] for b in B]
OPEN,CLOSE=28.75,36.95
def L(ix,y,size=None,g=False,t0=None):
    ws=[w(i) for i in ix]
    if t0: ws[0]['t']=max(ws[0]['t'],t0)
    d={"text":" ".join(o['w'] for o in ws),"y":y,"t":ws[0]['t'],"wt":[o['t'] for o in ws]}
    if size: d["size"]=size
    if g: d["g"]=True
    return d
cards=[{"x":130,"y":300,"w":820,"h":200,"t":28.81,"titles":[L([73,74,75],66,54)]},
       {"x":130,"y":560,"w":820,"h":340,"t":30.62,"titles":[L([76,77],62,46),L([78],150,70,g=True)],"subs":[L([80,81,82],258)]},
       {"x":130,"y":960,"w":820,"h":320,"t":33.97,"titles":[L([83,84,85],62,48),L([86,87,88],150,58,g=True)],"subs":[L([89,90],250)]}]
cam=[[0,540,960,1.0],[OPEN,540,400,1.12],[30.3,540,730,1.12],[33.6,540,1120,1.12],[36.2,540,790,0.92]]
ball=[[OPEN,{"s":{"x":540,"y":960}}],[29.2,{"wd":[0,"t",0,1]}],[29.74,{"wd":[0,"t",0,2]}],[30.8,{"wd":[1,"t",0,1]}],[31.32,{"wd":[1,"t",1,0]}],
      [32.42,{"wd":[1,"s",0,1]}],[32.94,{"wd":[1,"s",0,2]}],[34.82,{"wd":[2,"t",0,2]}],[35.46,{"wd":[2,"t",1,1]}],[36.32,{"wd":[2,"s",0,1]}],[CLOSE,{"s":{"x":540,"y":960}}]]
INS={"open":OPEN,"close":CLOSE,"cards":cards,"cam":cam,"ball":ball}
iend=round(CLOSE+0.6,3)
def sh(o,t): o['t']=round(max(o['t'],t),3); return o
d1={"type":"pair","start":13.78,"end":17.32,"items":[{"num":"١","t":13.82,"words":[sh(w(34),13.82),w(35),w(36),w(37),w(38)]},{"num":"٢","t":15.38,"words":[w(i) for i in (39,40,41,42)]}]}
d2={"type":"cmp","start":49.0,"end":55.18,"sections":[{"head":[sh(w(124),49.04),w(125),w(126)],"traits":[[w(127),w(128),w(129),w(130)]]},
    {"head":[w(131),sh(w(132),52.16),w(133)],"traits":[[w(134),w(135),w(136),w(137)]]}]}
END=65.12; CL=65.90
DUR=round(CL+(3.16-0.795)+0.15,2)
D={"lap":[920]*7,"cuts":[6.24,8.8,12.72,21.72,39.24,65.96],"chunks":chunks,"devices":[d1,d2],"insert":{"start":OPEN,"end":iend},
   "trans":[[6.24,"flash"],[8.8,"sweep"],[12.72,"flash"],[21.72,"sweep"],[39.24,"flash"]],
   "END":{"start":END,"close":CL,"dur":DUR,"cy":640},"capBase":110,"nameY":265,
   "N":{"appear":0.0,"stretch":0.08,"split":0.42,"dr":0.42,"marwa":0.92,"magdy":1.06,"title":2.29,"exit":6.05}}
json.dump(D,open('data_full.json','w'),ensure_ascii=False); json.dump(INS,open('ins_full.json','w'),ensure_ascii=False)
open('page_full.html','w').write(open('../f6_overlay_full.html').read().replace('DATA',json.dumps(D,ensure_ascii=False)))
open('page_ins.html','w').write(open('../f6_insert.html').read().replace('DATA',json.dumps(INS,ensure_ascii=False)))
print('dur',DUR,'frames',round(DUR*25))
