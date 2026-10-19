from build import *
v=V("neck","خطوط_وتجاعيد_الرقبة_config.py",{})
t=v.t
blocks=[[(0,4),(4,9)],[(9,13)],[(13,15),(15,19)],[(19,24),(24,27)],[(27,31)],[(31,35),(35,40)],[(53,57),(57,61)],[(82,86)],[(86,88),(88,93)]]
devices=[
 {"type":"cmp","start":t(40)-0.05,"end":t(52)+1.0,"sections":[{"head":v.ws(40,44,set()),"traits":[v.ws(44,47,{45,46})]},{"head":v.ws(47,49,{47,48}),"traits":[v.ws(49,51,set()),v.ws(51,53,{52})]}]},
 {"type":"pair","start":t(93)-0.05,"end":t(99)+1.0,"items":[{"num":"١","t":t(93),"words":v.ws(93,96,{93,94})},{"num":"٢","t":t(96),"words":v.ws(96,100,{98,99})}]}]
o=t(61)-0.05
insert={"start":o-0.05,"end":t(81)+1.2}
cards=[
 {"x":90,"y":260,"w":900,"h":300,"t":t(61),"titles":[v.line(61,64,40,58,True)],"subs":[v.line(64,70,150)]},
 {"x":570,"y":610,"w":420,"h":260,"t":t(72),"num":"١","titles":[v.line(70,72,90,44),v.line(72,74,165,46,True)]},
 {"x":90,"y":610,"w":420,"h":260,"t":t(74),"num":"٢","titles":[v.line(74,76,120,50,True)]},
 {"x":90,"y":920,"w":900,"h":220,"t":t(76),"titles":[v.line(76,79,40,56,True)],"subs":[v.line(79,82,135)]}]
cards[1]["t"]=t(70)
ins={"open":o,"close":t(81)+0.9,"cards":cards,
 "cam":[[0,540,960,1.0],[o,540,420,1.3],[t(70)-0.3,540,740,1.3],[t(76)-0.3,540,1030,1.3],[t(81)+0.4,540,700,0.95]],
 "ball":[[o-0.05,None],[t(61),{"w":{"x":540,"y":270}}],[t(70),{"w":{"x":931,"y":669}}],[t(74),{"w":{"x":451,"y":669}}],[t(76),{"w":{"x":540,"y":930}}],[t(81)+0.8,{"w":{"x":540,"y":700}}],[t(81)+1.0,None]]}
icons=[(9,12,"phone"),(13,18,"clock"),(24,30,"wrinkles"),(31,34,"warning"),(35,39,"eye"),(53,57,"shield"),(84,85,"bulb"),(86,92,"hourglass")]
N=v.name_times()
fx=[sfx("soft reveal/1.MP3",N["split"]),sfx("pop/2.MP3",N["magdy"]),
 sfx("paper.MP3",t(40)),sfx("whoosh/fast paper.MP3",t(47)),sfx("pop/1.mp4",t(51)),
 sfx("whoosh/big.MP3",o+0.07),sfx("pop/3.MP3",t(70)),sfx("pop/4.MP3",t(74)),sfx("Hint , notification/simble notification.MP3",t(76)),sfx("whoosh/light .MP3",t(81)+0.93),
 sfx("معلومة مهمة في اول اخر الفيديو مش هوك.MP3",t(84)),sfx("clock ticking.MP3",t(87),(0.0,0.6,0.1)),
 sfx("mouse click 1.MP3",t(93)),sfx("correct answer.MP3",t(96))]
d=build(v,blocks,devices,insert,ins,icons,fx,shots("neck"))
