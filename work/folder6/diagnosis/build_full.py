import json
W=json.load(open('words_ref.json')); P=3/25
FIX={6:'ليها',7:'تقريبًا',25:'لحالتي',34:'أبدًا',35:'بصورة',38:'History',54:'بتاعنا',61:'أقرر',74:'قدامي',75:'مهم',76:'جدًا',96:'التشخيص',109:'Online',112:'الـHistory',113:'الصح',120:'الصح',129:'إيه'}
MERGE={13:(14,'يبعتلي'),17:(18,'يبعتلي'),20:(21,'ويقولي')}
G={4,9,15,19,24,30,35,56,58,64,71,76,78,83,89,96,98,101,104,109,113,117,120,123,127}
def w(i,t=None):
    j,txt=MERGE.get(i,(i,FIX.get(i,W[i]['w'].strip('.،'))))
    return {"w":txt,"t":round(t if t is not None else W[i]['s'],3),"e":W[j]['e'],"g":i in G}
B=[[[0,1],[2,3,4]],[[5,6],[7,8,9]],[[10,11,12],[13,15]],[[16,17],[19]],[[20,22,23],[24,25]],
   [[26,27],[28,29,30]],[[31,32,33],[34,35]],[[55,56],[57,58,59]],
   [[75,76],[77,78]],[[79,80,81],[82,83]],[[84,85,86],[87,88,89]],[[90,91,92]],[[93,94,95],[96]],
   [[97,98],[99,100,101]],[[110,111,112],[113]],[[114,115],[116,117]],[[118,119,120]],[[121,122,123],[124,125,126]],[[127,128,129]]]
chunks=[[dict(w(i),r=ri) for ri,row in enumerate(b) for i in row] for b in B]
# insert: «لازم ناخد History … ولازم نفحص الجلد … قبل ما نقول التشخيص»
OPEN,CLOSE=14.10,21.95
def L(ix,y,size=None,g=False,t0=None):
    ws=[w(i) for i in ix]
    if t0: ws[0]['t']=max(ws[0]['t'],t0)
    d={"text":" ".join(o['w'] for o in ws),"y":y,"t":ws[0]['t'],"wt":[o['t'] for o in ws]}
    if size: d["size"]=size
    if g: d["g"]=True
    return d
cards=[{"x":130,"y":300,"w":820,"h":290,"t":14.2,"num":"١","titles":[L([36,37,38],70,56,t0=14.2)],"subs":[L([39,40,41,42,43],176)]},
       {"x":130,"y":650,"w":820,"h":250,"t":17.28,"num":"٢","titles":[L([44,45,46],70,56)],"subs":[L([47],160)]},
       {"x":130,"y":960,"w":820,"h":260,"t":19.35,"titles":[L([48,49,50],56,46),L([51,52,53,54],140,54,g=True)]}]
cam=[[0,540,950,1.0],[OPEN,540,445,1.12],[17.0,540,775,1.12],[19.1,540,1090,1.12],[21.0,540,760,0.92]]
ball=[[OPEN,{"s":{"x":540,"y":990}}],[14.44,{"wd":[0,"t",0,1]}],[14.7,{"wd":[0,"t",0,2]}],[15.48,{"wd":[0,"s",0,1]}],[16.36,{"wd":[0,"s",0,4]}],
      [17.28,{"wd":[1,"t",0,0]}],[18.0,{"wd":[1,"t",0,2]}],[18.34,{"wd":[1,"s",0,0]}],[19.35,{"wd":[2,"t",0,0]}],[20.6,{"wd":[2,"t",1,2]}],
      [21.02,{"wd":[2,"t",1,3]}],[CLOSE,{"s":{"x":540,"y":990}}]]
INS={"open":OPEN,"close":CLOSE,"cards":cards,"cam":cam,"ball":ball}
iend=round(CLOSE+0.6,3)
# devices
def sh(o,t): o['t']=round(max(o['t'],t),3); return o
d1={"type":"num","num":"١","start":23.55,"ringT":23.6,"title":[sh(w(60),23.6),sh(w(61),23.66)],"items":[{"t":23.88,"words":[w(i) for i in (62,63,64,65)]}],"end":25.95}
d2={"type":"num","num":"٢","start":25.99,"ringT":26.03,"title":[sh(w(66),26.03),sh(w(67),26.09),w(68)],
    "items":[{"t":26.75,"words":[w(i) for i in (69,70,71)]},{"t":28.14,"words":[w(i) for i in (72,73,74)]}],"end":29.54}
s2=[sh(w(105),43.14),sh(w(106),43.2),w(107)]
d3={"type":"cmp","start":41.56,"end":45.22,"sections":[{"head":[sh(w(102),41.6),sh(w(103),41.66),w(104)],"traits":[]},{"head":s2,"traits":[[w(108),w(109)]]}]}
d3['sections'][1]['traits'][0][0]['t']=max(d3['sections'][1]['traits'][0][0]['t'],43.54)
END=round(54.36+0.8,2); CL=round(END+0.80,2); DUR=round(CL+(3.16-0.795)+0.15,2)
D={"lap":[950,950,950,950],"cuts":[10.04,29.12,33.28],"chunks":chunks,"devices":[d1,d2,d3],"insert":{"start":OPEN,"end":iend},
   "trans":[[10.04,"flash"],[29.12,"sweep"],[33.28,"flash"],[5.78,"cam"],[13.28,"cam"],[52.2,"cam"]],
   "END":{"start":END,"close":CL,"dur":DUR,"cy":620},"capBase":110,"nameY":272,
   "N":{"appear":0.29,"stretch":0.40,"split":0.72,"dr":0.72,"marwa":0.9,"magdy":1.32,"title":1.82,"exit":6.16}}
json.dump(D,open('data_full.json','w'),ensure_ascii=False); json.dump(INS,open('ins_full.json','w'),ensure_ascii=False)
open('page_full.html','w').write(open('f6_overlay_full.html').read().replace('DATA',json.dumps(D,ensure_ascii=False)))
open('page_ins.html','w').write(open('f6_insert.html').read().replace('DATA',json.dumps(INS,ensure_ascii=False)))
print('dur',DUR,'frames',round(DUR*25))
