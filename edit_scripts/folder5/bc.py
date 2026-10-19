# folder 5 · PDRN: corrected words, caption lines by meaning (<=4), smoked glass page
import json,sys
LATF={'A':('Playfair700.ttf',700),'B':('Cormorant600.ttf',600),'C':('BebasNeue.ttf',400),'D':('JosefinSans.ttf',600)}
lf=sys.argv[1] if len(sys.argv)>1 else 'A'
w=json.load(open('/home/user/claude/work/folder5/collagen5/words.json'))
FIX={3:'مشدودة',7:'تعتمدي',7:'تعتمدي',12:'Volume',20:'Biostimulators',29:'دايمًا',32:'Sculptra',34:'Sculptra',43:'Radiesse',61:'وببساطة',74:'أساسي',93:'المفقود',104:'الفيلر',96:'إننا',22:'أشهر',113:'طبيعي'}
SPLIT={33:[('و',12.76,12.92),('Radiesse',12.92,13.46)]}
MERGE={(39,41):'Poly-L-Lactic Acid',(48,50):'Calcium Hydroxylapatite',(62,63):'الاتنين'}
W=[{'w':FIX.get(i,x[2]),'t':x[0],'e':x[1],'g':False} for i,x in enumerate(w)]
for (a,b),txt in MERGE.items():
    W[a]=dict(W[a],w=txt,e=W[b]['e'])
    for k in range(a+1,b+1): W[k]=None
ROWS=[[0,3],[3,7],[7,10],[10,13],[13,17],[17,19],[19,21],[21,24],[24,28],[28,31],[31,34],
      [34,36],[36,39],[39,42],[42,44],[44,48],[48,51],
      [51,55],[55,57],[57,61],[61,65],[65,68],[68,71],[71,75],[75,79],[79,83],
      [83,87],[87,91],[91,94],[94,98],[98,102],[102,105],[105,107],[107,111],[111,114]]
assert [r[0] for r in ROWS[1:]]==[r[1] for r in ROWS[:-1]] and ROWS[-1][1]==len(w)
KEY=set()
chunks=[[x for i in range(a,b) if W[i] for x in ([{'w':w_,'t':t_,'e':e_,'g':False} for w_,t_,e_ in SPLIT[i]] if i in SPLIT else [dict(W[i],w=W[i]['w'].rstrip('،.:؟'))])] for a,b in ROWS]
json.dump([x for x in W if x],open('words_fixed_col.json','w'),ensure_ascii=False)
for c in chunks: assert 1<=len(c)<=4,c
cuts=[4.68,8.28,11.76,13.56,17.8,21.6,26.48,31.04,37.28,41.92,45.88]
LAP=1070
d={'chunks':chunks,'devices':[],'cuts':cuts,'lap':[LAP]*(len(cuts)+1),'xs':[540]*(len(cuts)+1),
   'N':{'appear':0.0,'stretch':0.25,'split':0.45,'dr':0.6,'marwa':0.9,'magdy':1.2,'title':1.6,'exit':4.6},
   'END':{'start':50.98,'close':51.78,'dur':53.6},
   'trans':[[4.68,'flash'],[8.28,'sweep'],[11.76,'flash'],[26.48,'sweep'],[31.04,'flash'],[37.28,'sweep'],[41.92,'flash']],
   'insert':{'start':13.46,'end':22.25,'drop_from':13.4,'drop_to':21.5},'nameHold':None,'nameBase':150,'nameCap':40}
json.dump(d,open('data_col.json','w'),ensure_ascii=False)
f,wt=LATF[lf]
open(f'pp_col.html','w').write(open('p7.html').read().replace('LATFILE',f).replace('LATW',str(wt)).replace('DATA',json.dumps(d,ensure_ascii=False)))
print('\n'.join(' '.join(o['w'] for o in c) for c in chunks))
