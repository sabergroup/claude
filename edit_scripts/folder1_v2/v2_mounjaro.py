from build2 import *
v=V("mounjaro","المونجارو_config.py",{0:"حسيتي"})
t=v.t
sentences=[(0,7),(7,23),(23,40),(40,54),(54,70),(105,112)]
def num(n,items,gold):
    its=[{"t":t(a),"words":v.ws(a,b,gold)} for a,b in items]
    return {"type":"num","num":n,"ringT":its[0]["t"],"start":its[0]["t"]-0.05,"end":t(items[-1][1]-1)+1.0,"items":its}
devices=[
 num("٢",[(80,82),(82,85),(85,87),(87,89),(89,91)],{81,84,86,88}),
 num("٣",[(91,94),(94,95),(95,98),(98,100),(100,103),(103,105)],{94,96,97,101,104}),
 {"type":"cmp","start":t(112)-0.05,"end":t(119)+1.0,"sections":[{"head":v.ws(112,115,set()),"traits":[v.ws(115,117,{115,116}),v.ws(117,120,{118,119})]}]}]
o=t(70)-0.05
insert={"start":o-0.05,"end":t(79)+1.2}
# one card, 760 wide (zoom <= 1.3 keeps it whole), every word on its own time
cards=[{"x":160,"y":700,"w":760,"h":410,"t":t(70),"num":"١","titles":[v.line(70,71,44,64,True)],
        "subs":[v.line(71,74,165),v.line(74,77,245),v.line(77,80,325,None)]}]
cards[0]["subs"][2]["g"]=True
ins={"open":o,"close":t(79)+0.9,"cards":cards,
 "cam":[[0,540,960,1.0],[o,540,820,1.22],[t(71),548,880,1.21],[t(73),532,900,1.22],[t(74),546,940,1.21],[t(77),534,990,1.22],[t(79)+0.4,540,935,1.05]],
 "ball":[[o-0.05,None],[t(70),{"wd":[0,"t",0,0]}],[t(71),{"wd":[0,"s",0,0]}],[t(74),{"wd":[0,"s",1,0]}],[t(77),{"wd":[0,"s",2,0]}],[t(79)+0.8,{"w":{"x":540,"y":1235}}],[t(79)+1.0,None]]}
icons=[(13,22,"scale"),(48,53,"wrinkles"),(54,60,"sparkle"),(105,111,"warning")]
N=v.name_times()
fx=[sfx("soft reveal/1.MP3",N["split"]),sfx("pop/2.MP3",N["magdy"]),
 sfx("whoosh/big.MP3",o+0.07),sfx("photo insert.MP3",t(77)),sfx("whoosh/light .MP3",t(79)+0.93),
 sfx("pop/1.mp4",t(80)),sfx("Hint , notification/solid.MP3",t(91)),
 sfx("معلومة مهمة في اول اخر الفيديو مش هوك.MP3",t(112)),sfx("correct answer.MP3",t(115))]
d=build(v,sentences,devices,insert,ins,icons,fx,shots("mounjaro"))
