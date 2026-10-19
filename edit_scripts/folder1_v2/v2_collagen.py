from build2 import *
v=V("collagen","تحفيز_الكولاجين_config.py",{})
t=v.t
sentences=[(0,16),(22,31),(49,73)]
def num(n,items,gold):
    its=[{"t":t(a),"words":v.ws(a,b,gold)} for a,b in items]
    return {"type":"num","num":n,"ringT":its[0]["t"],"start":its[0]["t"]-0.05,"end":t(items[-1][1]-1)+1.0,"items":its}
devices=[
 {"type":"pair","start":t(16)-0.05,"end":t(21)+1.0,"items":[{"num":"١","t":t(16),"words":v.ws(16,20,{18,19})},{"num":"٢","t":t(20),"words":v.ws(20,22,{21})}]},
 num("٢",[(42,45)],{43}),
 num("٣",[(45,47),(47,49)],{46}),
 num("١",[(73,75)],{73}),
 num("٢",[(75,78),(78,80)],{75,77})]
o=t(31)-0.05
insert={"start":o-0.05,"end":t(41)+1.2}
cards=[{"x":160,"y":700,"w":760,"h":410,"t":t(31),"num":"١","titles":[v.line(31,34,44,48)],
        "subs":[v.line(34,36,135,None),v.line(36,40,215),v.line(40,42,295)]}]
cards[0]["subs"][0]["g"]=True; cards[0]["subs"][0]["size"]=52
ins={"open":o,"close":t(41)+0.9,"cards":cards,
 "cam":[[0,540,960,1.0],[o,540,820,1.22],[t(34),548,860,1.21],[t(36),532,900,1.22],[t(38),546,930,1.21],[t(40),534,970,1.22],[t(41)+0.4,540,905,1.05]],
 "ball":[[o-0.05,None],[t(31),{"wd":[0,"t",0,0]}],[t(34),{"wd":[0,"s",0,0]}],[t(36),{"wd":[0,"s",1,0]}],[t(40),{"wd":[0,"s",2,0]}],[t(41)+0.8,{"w":{"x":540,"y":1205}}],[t(41)+1.0,None]]}
icons=[(10,11,"sparkle"),(22,26,"sun"),(29,31,"lift"),(49,59,"warning"),(60,69,"check")]
N=v.name_times()
fx=[sfx("soft reveal/1.MP3",N["split"]),sfx("pop/2.MP3",N["magdy"]),
 sfx("pop/1.mp4",t(16)),sfx("Hint , notification/solid.MP3",t(20)),
 sfx("whoosh/big.MP3",o+0.07),sfx("photo insert.MP3",t(36)),sfx("whoosh/light .MP3",t(41)+0.93),
 sfx("pop/3.MP3",t(42)),sfx("pop/4.MP3",t(45)),
 sfx("معلومة مهمة في اول اخر الفيديو مش هوك.MP3",t(49)),
 sfx("mouse click 1.MP3",t(73)),sfx("Hint , notification/info.MP3",t(75))]
d=build(v,sentences,devices,insert,ins,icons,fx,shots("collagen"))
