from build import *
v=V("mounjaro","المونجارو_config.py",{0:"حسيتي"})
t=v.t
blocks=[[(0,5),(5,7)],[(7,12),(12,16)],[(16,19),(19,23)],[(23,27),(27,31)],[(31,35),(35,40)],[(40,44),(44,48)],[(48,51),(51,54)],[(54,59),(59,61)],
        [(105,109),(109,112)]]
devices=[
 {"type":"pair","start":t(61)-0.05,"end":t(69)+1.0,"items":[{"num":"١","t":t(61),"words":v.ws(61,66,{62,63})},{"num":"٢","t":t(66),"words":v.ws(66,70,{67,68})}]},
 {"type":"cmp","start":t(112)-0.05,"end":t(119)+1.0,"sections":[{"head":v.ws(112,115,set()),"traits":[v.ws(115,117,{115,116}),v.ws(117,120,{118,119})]}]}]
o=t(70)-0.05
insert={"start":o-0.05,"end":t(104)+1.2}
cards=[
 {"x":90,"y":260,"w":900,"h":350,"t":t(70),"num":"١","titles":[v.line(70,71,40,60,True)],"subs":[v.line(71,77,140)],"chips":[{"text":"استعادة امتلاء الوجه","y":236,"t":t(77)}]},
 {"x":90,"y":660,"w":900,"h":350,"t":t(80),"num":"٢","titles":[v.line(81,82,40,60,True)],"subs":[v.line(82,87,140)],"chips":[{"text":"مرونة الجلد وجودته","y":236,"t":t(88)}]},
 {"x":90,"y":1060,"w":900,"h":350,"t":t(94),"num":"٣","titles":[v.line(94,98,40,54,True)],"subs":[v.line(98,103,140)],"chips":[{"text":"وزيادة نضارتها","y":236,"t":t(103)}]}]
# title of card 3: first word appears when she starts the sentence, the card itself on "Skin Boosters"
ins={"open":o,"close":t(104)+0.9,"cards":cards,
 "cam":[[0,540,960,1.0],[o,540,440,1.32],[t(80)-0.3,540,840,1.32],[t(94)-0.3,540,1240,1.32],[t(104)+0.4,540,840,0.9]],
 "ball":[[o-0.05,None],[t(70),{"w":{"x":931,"y":319}}],[t(77),{"w":{"x":540,"y":580}}],[t(80),{"w":{"x":931,"y":719}}],[t(88),{"w":{"x":540,"y":980}}],[t(94),{"w":{"x":931,"y":1119}}],[t(103),{"w":{"x":540,"y":1380}}],[t(104)+0.8,{"w":{"x":540,"y":860}}],[t(104)+1.0,None]]}
icons=[(13,22,"scale"),(48,53,"wrinkles"),(54,60,"sparkle"),(105,111,"warning")]
N=v.name_times()
fx=[sfx("soft reveal/1.MP3",N["split"]),sfx("pop/2.MP3",N["magdy"]),
 sfx("pop/1.mp4",t(61)),sfx("Hint , notification/solid.MP3",t(66)),
 sfx("whoosh/big.MP3",o+0.07),sfx("paper.MP3",t(80)),sfx("pop/4.MP3",t(94)),sfx("whoosh/light .MP3",t(104)+0.93),
 sfx("معلومة مهمة في اول اخر الفيديو مش هوك.MP3",t(112)),sfx("correct answer.MP3",t(115))]
d=build(v,blocks,devices,insert,ins,icons,fx,shots("mounjaro"))
