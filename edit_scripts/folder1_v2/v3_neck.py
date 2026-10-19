from build2 import *
v=V("neck","خطوط_وتجاعيد_الرقبة_config.py",{})
t=v.t
sentences=[(0,40),(53,64),(76,86),("p",86,93)]
devices=[
 {"type":"cmp","start":t(40)-0.05,"end":t(52)+1.0,"sections":[{"head":v.ws(40,44,set()),"traits":[v.ws(44,47,{45,46})]},{"head":v.ws(47,49,{47,48}),"traits":[v.ws(49,51,set()),v.ws(51,53,{52})]}]},
 {"type":"pair","start":t(93)-0.05,"min_start":t(91)+1.16,"end":t(99)+1.0,"items":[{"num":"١","t":t(93),"words":v.ws(93,96,{93,94})},{"num":"٢","t":t(96),"words":v.ws(96,100,{98,99})}]}]
o=t(64)-0.05
insert={"start":o-0.05,"end":t(75)+1.2}
cards=[{"x":160,"y":540,"w":760,"h":250,"t":t(64),"titles":[v.line(64,67,36,40),v.line(67,70,112,66,True)]},
       {"x":550,"y":830,"w":370,"h":230,"t":t(70),"num":"١","titles":[v.line(70,72,95,38),v.line(72,74,160,46,True)]},
       {"x":160,"y":830,"w":370,"h":230,"t":t(74),"num":"٢","titles":[v.line(74,76,125,50,True)]}]
ins={"open":o,"close":t(75)+0.9,"cards":cards,
 "marks":[{"d":"M400 770 L680 770","t":t(68),"ts":.45,"sw":3}],
 "cam":[[0,540,960,1.0],[o,540,680,1.2],[t(66),546,700,1.22],[t(68),534,730,1.2],[t(70),544,840,1.21],[t(72),536,880,1.22],[t(74),542,900,1.21],[t(75)+0.4,540,810,1.05]],
 "ball":[[o-0.05,None],[t(64),{"wd":[0,"t",0,0]}],[t(67),{"wd":[0,"t",1,0]}],[t(70),{"wd":[1,"t",0,0]}],[t(72),{"wd":[1,"t",1,0]}],[t(74),{"wd":[2,"t",0,0]}],[t(75)+0.8,{"w":{"x":540,"y":1130}}],[t(75)+1.0,None]]}
icons=[(9,12,"phone"),(13,18,"clock"),(24,30,"wrinkles"),(31,34,"warning"),(35,39,"eye"),(53,57,"shield"),(84,85,"bulb"),(86,92,"hourglass")]
N=v.name_times()
fx=[sfx("soft reveal/1.MP3",N["split"]),sfx("pop/2.MP3",N["magdy"]),
 sfx("paper.MP3",t(40)),sfx("whoosh/fast paper.MP3",t(47)),sfx("pop/1.mp4",t(51)),
 sfx("whoosh/big.MP3",o+0.07),sfx("pop/3.MP3",t(70)),sfx("pop/4.MP3",t(74)),sfx("whoosh/light .MP3",t(75)+0.93),
 sfx("معلومة مهمة في اول اخر الفيديو مش هوك.MP3",t(84)),sfx("clock ticking.MP3",t(87),(0.0,0.6,0.1)),
 sfx("mouse click 1.MP3",t(93)),sfx("correct answer.MP3",t(96))]
d=build(v,sentences,devices,insert,ins,icons,fx,shots("neck"))
