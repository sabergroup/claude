# folder 5 · PDRN: corrected words, caption lines by meaning (<=4), smoked glass page
import json,sys
LATF={'A':('Playfair700.ttf',700),'B':('Cormorant600.ttf',600),'C':('BebasNeue.ttf',400),'D':('JosefinSans.ttf',600)}
lf=sys.argv[1] if len(sys.argv)>1 else 'A'
w=json.load(open('/home/user/claude/work/folder5/pdrn/words.json'))
FIX={52:'أو',7:'جاية',20:'بروتين',27:'الهدف',28:'الأساسي',30:'إننا',31:'نملا',33:'الفراغات،',40:'إصلاح',41:'الأنسجة',44:'البشرة.',
     47:'إننا',50:'تغيير',53:'إضافة',55:'للوش،',59:'نضارة',62:'حيويتها،',64:'تفضلي',67:'الطبيعية.',75:'للوجه،',76:'لأن',84:'والإيدين',
     92:'منطقة.',96:'جدًا',98:'تعرفي:',99:'إن',107:'الناس،',119:'الأنسب',120:'ليكي.',5:'فيلر،',10:'بينهم.',8:'أقولك',6:'وأنا'}
MERGE={(0,3):'PDRN',(15,18):'PDRN',(23,25):'DNA',(68,71):'PDRN',(100,103):'PDRN'}
W=[{'w':FIX.get(i,x[2]),'t':x[0],'e':x[1],'g':False} for i,x in enumerate(w)]
for (a,b),txt in MERGE.items():
    W[a]=dict(W[a],w=txt,e=W[b]['e'])
    for k in range(a+1,b+1): W[k]=None
ROWS=[[0,6],[6,8],[8,11],[11,15],[15,21],[21,26],[26,30],[30,34],[34,36],[36,39],[39,42],[42,45],
      [45,47],[47,50],[50,52],[52,56],[56,58],[58,61],[61,63],[63,66],[66,68],
      [68,74],[74,76],[76,80],[80,82],[82,85],[85,87],[87,90],[90,93],
      [93,97],[97,104],[104,108],[108,111],[111,113],[113,117],[117,121]]
assert [r[0] for r in ROWS[1:]]==[r[1] for r in ROWS[:-1]] and ROWS[-1][1]==len(w)
KEY={0,9,20,33,40,67,75,80,95,105,112}
chunks=[[dict(W[i],w=W[i]['w'].rstrip('،.:'),key=i in KEY) for i in range(a,b) if W[i]] for a,b in ROWS]
json.dump([x for x in W if x],open('words_fixed_pdrn.json','w'),ensure_ascii=False)
for c in chunks: assert 1<=len(c)<=4,c
cuts=[3.48,8.44,11.28,17.16,21.32,25.0,27.92,30.36,34.44,37.4,39.76]
LAP=1070
d={'chunks':chunks,'devices':[],'cuts':cuts,'lap':[LAP]*(len(cuts)+1),'xs':[540]*(len(cuts)+1),
   'N':{'appear':0.0,'stretch':0.25,'split':0.45,'dr':0.6,'marwa':0.9,'magdy':1.2,'title':1.6,'exit':4.6},
   'END':{'start':48.62,'close':49.42,'dur':49.52},
   'trans':[[3.48,'flash'],[8.44,'sweep'],[11.28,'flash'],[27.92,'sweep'],[34.44,'flash'],[39.76,'sweep']],
   'insert':{'start':17.3,'end':25.45,'drop_from':17.0,'drop_to':24.9},'nameHold':None,'nameBase':150,'nameCap':40}
json.dump(d,open('data_pdrn.json','w'),ensure_ascii=False)
f,wt=LATF[lf]
open(f'pp_pdrn_{lf}.html','w').write(open('p7.html').read().replace('LATFILE',f).replace('LATW',str(wt)).replace('DATA',json.dumps(d,ensure_ascii=False)))
print('\n'.join(' '.join(o['w'] for o in c) for c in chunks))
