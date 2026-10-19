import json
Y=1110; NB=' '
i={"open":13.46,"close":21.8,
 "cards":[
  {"x":90,"y":300,"w":900,"h":320,"t":13.5,"titles":[{"text":"Sculptra","y":36,"t":13.5,"wt":[13.5],"size":58},
     {"text":"بتعتمد على مادة اسمها","y":118,"t":14.36,"wt":[14.36,15.08,15.2,15.62],"size":40,"lt":True}],
   "chips":[{"text":"Poly-L-Lactic"+NB+"Acid","y":212,"t":16.18,"cx":450}]},
  {"x":90,"y":670,"w":900,"h":320,"t":17.68,"titles":[{"text":"أما Radiesse","y":36,"t":17.68,"wt":[17.68,17.98],"size":58},
     {"text":"فهو بيعتمد على مادة","y":118,"t":18.5,"wt":[18.5,18.82,19.46,19.6],"size":40,"lt":True}],
   "chips":[{"text":"Calcium"+NB+"Hydroxylapatite","y":212,"t":20.0,"cx":450}]}],
 "cam":[[0,540,960,1.0],[13.46,540,470,1.1],[17.5,540,830,1.1],[21.3,540,650,0.95,0.4]],
 "ball":[[13.0,{"s":{"x":540,"y":Y}}],[13.5,{"w":{"x":540,"y":266}}],[16.18,{"w":{"x":540,"y":492}}],[17.68,{"w":{"x":540,"y":636}}],[20.0,{"w":{"x":540,"y":862}}],[21.8,{"s":{"x":540,"y":Y}}]],
 "marks":[]}
json.dump(i,open('ins_col.json','w'),ensure_ascii=False)
open('ipage_col.html','w').write(open('ins6.html').read().replace('DATA',json.dumps(i,ensure_ascii=False)))
