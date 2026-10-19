import json,sys,subprocess
S="/tmp/claude-0/-home-user-claude/5b00ce15-a751-5c6f-a77b-d1addef998ec/scratchpad"
PK=json.load(open(f"{S}/sfx2_peaks.json"))
def load(n,fix,gold):
    w=json.load(open(f"{S}/w_{n}/words.json"))
    return w,(lambda i,txt=None,g=None:{"w":txt or fix.get(i,w[i][2]),"t":w[i][0],"e":w[i][1],"g":(i in gold) if g is None else g})
def rows_to_chunks(W,blocks): return [[dict(W(i),r=ri) for ri,(a,b) in enumerate(bl) for i in range(a,b) ] for bl in blocks]
def lap_at(sh,t):
    k=max(i for i,c in enumerate(sh["cuts"][:-1]) if c<=t); return sh["lap"][k]
def trans_for(sh,skip):
    kinds=["flash","sweep","line"]; out=[]; j=0
    for c in sh["cuts"][1:-1]:
        if any(a-0.25<=c<=b+0.25 for a,b in skip): continue
        out.append([c,kinds[j%3]]); j+=1
    return out
def sfx(f,t,seg=None):
    p=PK[f] if not seg else seg[2]
    return f"{f}@{t:.2f}@{p}"+(f"@{seg[0]}@{seg[1]}" if seg else "")
def finish(name,src,W,w,chunks,devices,N,insert,ins,sfxl,split=None,extra_skip=()):
    sh=json.load(open(f"{S}/f3/{name}_shots.json")) if name!="dandruff" else json.load(open(f"{S}/dd/shots.json"))
    cuts=sh["cuts"]; lap=sh["lap"][:]
    if len(cuts)>2 and cuts[-1]-cuts[-2]<0.2: cuts=cuts[:-2]+[cuts[-1]]; lap=lap[:-1]
    sh={"cuts":cuts,"lap":lap}
    last_e=w[-1][1]; srcdur=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",src],capture_output=True,text=True).stdout)
    END={"start":round(last_e+0.12,2)}; END["close"]=round(END["start"]+0.8,2); END["dur"]=round(max(srcdur,END["close"]+0.5),2)
    skip=[(insert["start"],insert["end"])] if insert else []
    data={"chunks":chunks,"devices":devices,"cuts":cuts[1:-1],"lap":lap,"N":N,"END":END,"trans":trans_for(sh,skip),"insert":insert}
    if split: data["split"]=split
    json.dump(data,open(f"{S}/f3/data_{name}.json","w"),ensure_ascii=False)
    if ins:
        ins["ball"][0][1]={"s":{"x":540,"y":lap_at(sh,ins["open"])+70}}; ins["ball"][-1][1]={"s":{"x":540,"y":lap_at(sh,ins["close"])+70}}
        json.dump(ins,open(f"{S}/f3/ins_{name}.json","w"),ensure_ascii=False)
    sfxl.append(sfx("اصوات تنفع لبداية او نهاية الفيديو/whoosh with impact.MP3",END["close"]))
    open(f"{S}/f3/sfx_{name}.txt","w").write("\n".join(sfxl)+"\n")
    print(name,"END",END,"trans",data["trans"],"blocks",len(chunks))

# ======================= تساقط الشعر =======================
hf={21:"إننا",43:"اضطراب",44:"هرموني",47:"وراثية",66:"المناسبة",75:"PRP",79:"الجذعية"}
w,W=load("hairloss",hf,{2,23,36,58,87,93})
chunks=rows_to_chunks(W,[[(0,2),(2,5)],[(5,8),(8,10)],[(10,13),(13,15)],[(15,18)],[(18,21),(21,24)],[(24,27),(27,31)],[(31,34),(34,37)],
  [(54,57),(57,59)],[(80,82),(82,85)],[(85,88)],[(88,91),(91,94)]])
devices=[
 {"type":"pair","start":24.40,"end":28.80,"items":[{"num":"١","t":w[60][0],"words":[W(60,"تحديد"),W(61,g=True)]},{"num":"٢","t":w[65][0],"words":[W(65),W(66,g=True)]}]},
 {"type":"cmp","start":28.85,"end":33.70,"sections":[{"head":[W(69),W(70,g=True)],"traits":[]},{"head":[W(72,g=True)],"traits":[[W(75)],[W(78),W(79)]]}]}]
N={"appear":0.0,"stretch":0.30,"split":1.08,"dr":1.46,"marwa":1.82,"magdy":2.02,"title":2.60,"exit":6.40}
insert={"start":14.50,"end":22.20}
ins={"open":14.55,"close":21.85,"cards":[
  {"x":90,"y":300,"w":900,"h":200,"t":w[37][0],"titles":[{"text":"ممكن يكون السبب","y":56,"t":w[37][0],"size":56}]},
  {"x":570,"y":560,"w":420,"h":300,"t":w[40][0],"num":"١","titles":[{"text":"نقص","y":100,"t":w[40][0]},{"text":"الفيتامينات","y":175,"t":w[42][0],"g":True,"size":46}]},
  {"x":90,"y":560,"w":420,"h":300,"t":w[43][0],"num":"٢","titles":[{"text":"اضطراب","y":100,"t":w[43][0]},{"text":"هرموني","y":175,"t":w[44][0],"g":True,"size":46}]},
  {"x":570,"y":900,"w":420,"h":300,"t":w[46][0],"num":"٣","titles":[{"text":"عوامل","y":100,"t":w[46][0]},{"text":"وراثية","y":175,"t":w[47][0],"g":True,"size":46}]},
  {"x":90,"y":900,"w":420,"h":300,"t":w[49][0],"num":"٤","titles":[{"text":"تساقط مؤقت","y":100,"t":w[49][0],"size":46}],"subs":[{"text":"بعد الحمل والولادة","y":180,"t":w[51][0]}]}],
 "cam":[[0,540,880,1.0],[14.5,540,420,1.45],[w[40][0]-0.3,780,710,1.6],[w[43][0]-0.3,300,710,1.6],[w[46][0]-0.3,780,1050,1.6],[w[49][0]-0.3,300,1050,1.6],[21.1,540,780,0.95]],
 "ball":[[14.5,None],[w[39][0],{"w":{"x":540,"y":300}}],[w[40][0],{"w":{"x":931,"y":619}}],[w[43][0],{"w":{"x":451,"y":619}}],[w[46][0],{"w":{"x":931,"y":959}}],[w[49][0],{"w":{"x":451,"y":959}}],[21.3,{"w":{"x":540,"y":780}}],[22.2,None]]}
fx=[sfx("soft reveal/1.MP3",N["split"]),sfx("pop/2.MP3",N["magdy"]),
 sfx("معلومة مهمة في اول اخر الفيديو مش هوك.MP3",w[18][0]),
 sfx("whoosh/big.MP3",14.62),sfx("pop/1.mp4",w[40][0]),sfx("Hint , notification/solid.MP3",w[43][0]),sfx("pop/3.MP3",w[46][0]),sfx("Hint , notification/simble notification.MP3",w[49][0]),sfx("whoosh/light .MP3",21.95),
 sfx("paper.MP3",w[60][0]),sfx("Hint , notification/info.MP3",w[65][0]),
 sfx("photo insert.MP3",w[69][0]),sfx("whoosh/fast paper.MP3",w[72][0]),sfx("camera shuter.MP3",w[75][0]),sfx("soft reveal/1.MP3",w[78][0]),
 sfx("correct answer.MP3",w[93][0])]
finish("hairloss",f"{S}/b3/تساقط الشعر.mp4",W,w,chunks,devices,N,insert,ins,fx)

# ======================= تساقط الشعر بعد الولادة =======================
pf={0:"لاحظتي",1:"إن",9:"ماتقلقيش",16:"وليه",18:"علمي",20:"الحمل",36:"الطبيعية",54:"إن",81:"لفترة",94:"الحالة",98:"ماتستنيش",106:"ارجعي",116:"ليكي",72:"تدريجيًا",92:"فورًا",112:"فورًا",7:"الولادة؟",57:"خفيف؟"}
w,W=load("postpartum",pf,{5,9,18,57,92,98,107,108,115})
chunks=rows_to_chunks(W,[[(0,3),(3,6)],[(6,8),(9,11)],[(11,13),(13,16)],[(16,19)],[(50,54),(54,58)],[(58,61),(61,65)],
  [(87,90),(90,92)],[(92,95)],[(95,97),(98,99)],[(99,103),(103,106)],[(106,109),(109,112)],[(112,114),(114,117)]])
devices=[
 {"type":"cmp","start":26.75,"end":31.30,"sections":[{"head":[W(66),W(67,g=True)],"traits":[[W(70),W(71)],[W(73),W(74)]]}]},
 {"type":"counter","start":31.35,"end":35.85,"items":[{"num":"١","t":w[77][0],"words":[W(77),W(78,g=True)]},{"num":"٢","t":w[80][0],"words":[W(80,g=True),W(81),W(82)]},{"num":"٣","t":w[85][0],"words":[W(85,g=True),W(86)]}]}]
N={"appear":0.0,"stretch":0.30,"split":0.54,"dr":1.18,"marwa":1.82,"magdy":2.38,"title":2.88,"exit":6.30}
insert={"start":7.25,"end":21.20}
ins={"open":7.30,"close":20.95,"cards":[
  {"x":90,"y":300,"w":900,"h":440,"t":w[19][0],"titles":[{"text":"أثناء الحمل","y":36,"t":w[19][0],"g":True,"size":60}],"subs":[{"text":"التغيرات الهرمونية","y":140,"t":w[21][0]},{"text":"لفترة أطول","y":345,"t":w[27][0]}],
   "chips":[{"text":"الشعر بيحتفظ بكثافته","y":235,"t":w[24][0]}]},
  {"x":90,"y":880,"w":900,"h":560,"t":w[30][0],"titles":[{"text":"بعد الولادة","y":36,"t":w[30][0],"g":True,"size":60}],"subs":[{"text":"الهرمونات بترجع لمعدلاتها الطبيعية","y":140,"t":w[32][0]},{"text":"في نفس الوقت","y":470,"t":w[47][0]}],
   "chips":[{"text":"كمية كبيرة من الشعر","y":250,"t":w[39][0]},{"text":"تدخل مرحلة التساقط","y":360,"t":w[43][0]}]}],
 "marks":[{"d":"M540 742 L540 878","t":w[29][0],"ts":.5}],
 "cam":[[0,540,960,1.0],[7.3,540,520,1.35],[w[29][0]-0.1,540,1170,1.3],[20.3,540,880,0.92]],
 "ball":[[7.25,None],[w[20][0],{"w":{"x":540,"y":318}}],[w[24][0],{"w":{"x":540,"y":535}}],[w[30][0],{"w":{"x":540,"y":898}}],[w[39][0],{"w":{"x":540,"y":1130}}],[w[43][0],{"w":{"x":540,"y":1240}}],[w[47][0],{"w":{"x":540,"y":1348}}],[21.3,None]]}
fx=[sfx("soft reveal/1.MP3",N["split"]),sfx("pop/2.MP3",N["magdy"]),
 sfx("Hint , notification/simble notification.MP3",w[9][0]),
 sfx("whoosh/big.MP3",7.38),sfx("pop/1.mp4",w[24][0]),sfx("whoosh/light .MP3",w[30][0]),sfx("pop/3.MP3",w[39][0]),sfx("Hint , notification/info.MP3",w[43][0]),sfx("clock ticking.MP3",w[47][0],(0.0,0.6,0.1)),sfx("whoosh/big.MP3",20.98),
 sfx("paper.MP3",w[67][0]),sfx("pop/4.MP3",w[70][0]),sfx("clock ticking.MP3",w[73][0],(0.0,1.0,0.1)),
 sfx("pop/2.MP3",w[77][0]),sfx("Hint , notification/solid.MP3",w[80][0]),sfx("Hint , notification/1.mp4",w[85][0]),
 sfx("correct answer.MP3",w[89][0]),sfx("معلومة مهمة في اول اخر الفيديو مش هوك.MP3",w[106][0])]
finish("postpartum",f"{S}/b3/تساقط الشعر بعد الولاده.mp4",W,w,chunks,devices,N,insert,ins,fx)

# ======================= القشرة =======================
dd=json.load(open(f"{S}/dd/data.json"))
df={1:"إن",2:"الشتا",21:"مهم",32:"فيه",65:"فبتظهر",122:"بتعاني",129:"احمرار"}
w,W=load("dandruff",df,{2,19,52,64,93,94,116,117,135,136})
cp=dd["cmp"]
devices=[{"type":"cmp","start":cp["start"],"end":cp["end"],"sections":[{"head":cp["h1"],"traits":[cp["t1"]]},{"head":cp["h2"],"traits":cp["t2"]}]}]
insert={"start":38.92,"end":49.40}
ins={"open":38.95,"close":48.95,"cards":[
  {"x":90,"y":300,"w":900,"h":260,"t":w[97][0],"titles":[{"text":"مش كل قشرة","y":34,"t":w[97][0],"size":56},{"text":"بينفع معاها نفس نوع العلاج","y":140,"t":w[100][0],"g":True,"size":46}]},
  {"x":700,"y":620,"w":290,"h":380,"t":w[105][0],"num":"١","titles":[{"text":"حالة","y":100,"t":w[106][0]}],"subs":[{"text":"سبب مختلف","y":180,"t":w[108][0]}],"chips":[{"text":"علاج مختلف","y":262,"t":w[112][0]}]},
  {"x":395,"y":620,"w":290,"h":380,"t":w[106][0],"num":"٢","titles":[{"text":"حالة","y":100,"t":w[106][0]+0.3}],"subs":[{"text":"سبب مختلف","y":180,"t":w[108][0]+0.15}],"chips":[{"text":"علاج مختلف","y":262,"t":w[113][0]}]},
  {"x":90,"y":620,"w":290,"h":380,"t":w[107][0],"num":"٣","titles":[{"text":"حالة","y":100,"t":w[107][0]}],"subs":[{"text":"سبب مختلف","y":180,"t":w[108][0]+0.3}],"chips":[{"text":"علاج مختلف","y":262,"t":w[114][0]}]},
  {"x":90,"y":1070,"w":900,"h":300,"t":w[115][0],"titles":[{"text":"العلاج الغلط","y":40,"t":w[116][0],"g":True,"size":60}],"subs":[{"text":"ممكن يزود المشكلة","y":160,"t":w[118][0]}]}],
 "marks":[{"d":"M160 1112 L230 1182 M230 1112 L160 1182","t":w[117][0],"ts":.35}],
 "cam":[[0,540,880,1.0],[38.9,540,430,1.35],[w[105][0]-0.25,540,810,1.12],[w[115][0]-0.1,540,1220,1.15],[48.6,540,860,0.92]],
 "ball":[[38.9,None],[w[97][0],{"w":{"x":540,"y":300}}],[w[105][0],{"w":{"x":931,"y":679}}],[w[106][0]+0.3,{"w":{"x":626,"y":679}}],[w[107][0],{"w":{"x":321,"y":679}}],
         [w[112][0],{"w":{"x":845,"y":882}}],[w[113][0],{"w":{"x":540,"y":882}}],[w[114][0],{"w":{"x":235,"y":882}}],[w[117][0],{"w":{"x":195,"y":1100}}],[49.3,None]]}
sp=dd["split"]
fx=[sfx("soft reveal/1.MP3",dd["N"]["split"]),sfx("pop/2.MP3",dd["N"]["magdy"]),
 sfx("معلومة مهمة في اول اخر الفيديو مش هوك.MP3",w[19][0]),
 sfx("pop/1.mp4",sp["f1"]),sfx("Hint , notification/solid.MP3",sp["f2"]),sfx("whoosh/light .MP3",sp["merge"]),sfx("Hint , notification/simble notification.MP3",sp["tt"]),
 sfx("camera shuter.MP3",w[47][0]),sfx("soft reveal/1.MP3",w[50][0]),
 sfx("paper.MP3",w[51][0]),sfx("mouse click 1.MP3",w[56][0]),sfx("whoosh/hard paper turn.MP3",w[62][0]),sfx("pop/3.MP3",w[67][0]),sfx("pop/4.MP3",w[72][0]),sfx("Hint , notification/1.mp4",w[74][0]),
 sfx("Hint , notification/info.MP3",w[93][0]),
 sfx("whoosh/big.MP3",38.98),sfx("photo insert.MP3",w[105][0]),sfx("whoosh/fast paper.MP3",w[112][0]),sfx("whoosh/حاجة مهمة بتختفي او جليتش.MP3",w[117][0]),sfx("whoosh/light .MP3",48.98),
 sfx("correct answer.MP3",w[133][0])]
finish("dandruff",f"{S}/b3/القشره.mp4",W,w,dd["chunks"],devices,dd["N"],insert,ins,fx,split=sp,extra_skip=[(sp["start"],sp["end"])])
