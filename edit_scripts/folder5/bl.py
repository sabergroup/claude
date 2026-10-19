# folder 5 · PDRN: corrected words, caption lines by meaning (<=4), smoked glass page
import json,sys
LATF={'A':('Playfair700.ttf',700),'B':('Cormorant600.ttf',600),'C':('BebasNeue.ttf',400),'D':('JosefinSans.ttf',600)}
lf=sys.argv[1] if len(sys.argv)>1 else 'A'
w=json.load(open('/home/user/claude/work/folder5/lip/words.json'))
FIX={20:'أو',71:'أو',92:'أو',86:'إيه',2:'بييجوا',7:'إنهم',8:'أصلًا',11:'لأن',12:'فيه',15:'إننا',21:'إننا',23:'نحسّن',24:'ترطيبها',35:'أقولك',36:'إن',40:'الأساسي',42:'إضافة',43:'حجم',47:'أما',63:'بنات',67:'الأساسي',69:'تكبير',72:'إضافة',73:'حجم',74:'وعلشان',80:'فيلر',81:'والأهم',82:'إننا',84:'إنتي',87:'فعلًا',99:'تناسبك'}
MERGE={(4,5):'Lip Filler',(30,31):'Lip Filler',(32,33):'Lip Booster',(37,38):'Lip Filler',(48,49):'Lip Booster',(90,91):'Lip Filler',(93,94):'Lip Booster'}
W=[{'w':FIX.get(i,x[2]),'t':x[0],'e':x[1],'g':False} for i,x in enumerate(w)]
for (a,b),txt in MERGE.items():
    W[a]=dict(W[a],w=txt,e=W[b]['e'])
    for k in range(a+1,b+1): W[k]=None
ROWS=[[0,4],[4,8],[8,11],[11,14],[14,17],[17,20],[20,23],[23,26],[26,29],[29,34],[34,36],
      [36,39],[39,42],[42,44],[44,47],[47,50],[50,52],[52,55],[55,57],[57,60],[60,63],
      [63,67],[67,71],[71,74],[74,77],[77,81],[81,84],[84,88],[88,92],[92,95],[95,97],[97,100]]
assert [r[0] for r in ROWS[1:]]==[r[1] for r in ROWS[:-1]] and ROWS[-1][1]==len(w)
KEY=set()
chunks=[[dict(W[i],w=W[i]['w'].rstrip('،.:'),key=i in KEY) for i in range(a,b) if W[i]] for a,b in ROWS]
json.dump([x for x in W if x],open('words_fixed_lip.json','w'),ensure_ascii=False)
for c in chunks: assert 1<=len(c)<=4,c
cuts=[4.12,10.64,13.72,19.2,22.24,25.84,30.48]
LAP=1070
d={'chunks':chunks,'devices':[],'cuts':cuts,'lap':[LAP]*(len(cuts)+1),'xs':[540]*(len(cuts)+1),
   'N':{'appear':0.0,'stretch':0.25,'split':0.45,'dr':0.6,'marwa':0.9,'magdy':1.2,'title':1.6,'exit':4.6},
   'END':{'start':39.5,'close':40.08,'dur':40.16},
   'trans':[[4.12,'flash'],[10.64,'sweep'],[13.72,'flash'],[30.48,'sweep']],
   'insert':{'start':14.7,'end':25.75,'drop_from':14.4,'drop_to':25.7},'nameHold':None,'nameBase':150,'nameCap':40}
json.dump(d,open('data_lip.json','w'),ensure_ascii=False)
f,wt=LATF[lf]
open(f'pp_lip.html','w').write(open('p7.html').read().replace('LATFILE',f).replace('LATW',str(wt)).replace('DATA',json.dumps(d,ensure_ascii=False)))
print('\n'.join(' '.join(o['w'] for o in c) for c in chunks))
