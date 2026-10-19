from build import *
v=V("collagen","تحفيز_الكولاجين_config.py",{})
t=v.t
blocks=[[(0,3),(3,6)],[(6,10),(10,11)],[(11,16)],[(22,26),(26,29)],[(29,31)],[(49,53),(53,57)],[(57,60)],[(60,64),(64,67)],[(67,70)],[(70,73)]]
devices=[
 {"type":"pair","start":t(16)-0.05,"end":t(21)+1.0,"items":[{"num":"١","t":t(16),"words":v.ws(16,20,{18,19})},{"num":"٢","t":t(20),"words":v.ws(20,22,{21})}]},
 {"type":"counter","start":t(73)-0.05,"end":t(79)+1.0,"items":[{"num":"١","t":t(73),"words":v.ws(73,75,{73})},{"num":"٢","t":t(75),"words":v.ws(75,80,{77,78,79})}]}]
o=t(31)-0.05
insert={"start":o-0.05,"end":t(48)+1.2}
cards=[
 {"x":90,"y":260,"w":900,"h":170,"t":t(31),"titles":[v.line(31,34,44,52)]},
 {"x":90,"y":480,"w":900,"h":330,"t":t(34),"num":"١","titles":[v.line(34,36,40,58,True)],"subs":[v.line(36,40,140)],"chips":[{"text":"والمسام الواسعة","y":222,"t":t(40)}]},
 {"x":90,"y":860,"w":900,"h":200,"t":t(42),"num":"٢","titles":[v.line(42,45,62,58,True)]},
 {"x":90,"y":1110,"w":900,"h":250,"t":t(45),"num":"٣","titles":[v.line(45,47,40,58,True)],"subs":[v.line(47,49,140)]}]
ins={"open":o,"close":t(48)+0.9,"cards":cards,
 "cam":[[0,540,960,1.0],[o,540,520,1.3],[t(42)-0.3,540,960,1.3],[t(45)-0.3,540,1160,1.3],[t(48)+0.4,540,810,0.95]],
 "ball":[[o-0.05,None],[t(31),{"w":{"x":540,"y":270}}],[t(34),{"w":{"x":931,"y":539}}],[t(40),{"w":{"x":540,"y":770}}],[t(42),{"w":{"x":931,"y":919}}],[t(45),{"w":{"x":931,"y":1169}}],[t(48)+0.8,{"w":{"x":540,"y":820}}],[t(48)+1.0,None]]}
icons=[(10,11,"sparkle"),(22,26,"sun"),(29,31,"lift"),(49,59,"warning"),(60,69,"check")]
N=v.name_times()
fx=[sfx("soft reveal/1.MP3",N["split"]),sfx("pop/2.MP3",N["magdy"]),
 sfx("pop/1.mp4",t(16)),sfx("Hint , notification/solid.MP3",t(20)),
 sfx("whoosh/big.MP3",o+0.07),sfx("pop/3.MP3",t(34)),sfx("paper.MP3",t(42)),sfx("pop/4.MP3",t(45)),sfx("whoosh/light .MP3",t(48)+0.93),
 sfx("معلومة مهمة في اول اخر الفيديو مش هوك.MP3",t(49)),
 sfx("mouse click 1.MP3",t(73)),sfx("Hint , notification/info.MP3",t(75))]
d=build(v,blocks,devices,insert,ins,icons,fx,shots("collagen"))
