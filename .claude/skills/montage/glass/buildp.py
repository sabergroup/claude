# folder 4 glass style: caption lines (<=4 words, cut by meaning), glass insert data, trimmed sounds
import json,statistics,sys
S='/tmp/claude-0/-home-user-claude/5b00ce15-a751-5c6f-a77b-d1addef998ec/scratchpad'
ROWS={
 'goose':[[0,3],[3,7],[7,10],[10,13],[13,17],[17,20],[20,22],[22,26],
          [53,56],[56,60],[60,63],[63,66],[66,69],[69,71],[71,74],[74,78],[78,82],[82,86],[86,90],[90,94],[94,96],
          [96,100],[100,104],[104,107],[107,110],[110,112],[112,115],[115,118]],
 'anemia':[[0,2],[2,5],[5,8],[8,10],[10,14],[14,17],[17,19],[19,21],[21,23],[23,25],[25,29],
          [55,58],[58,61],[61,64],[64,65],[65,68],[68,70],[70,74],[74,78],[78,80],[80,82],[82,86],[86,90],[90,92],[92,95],[95,98],[98,101],
          [101,105],[105,108],[108,110],[110,113],[113,115],[115,119],[119,122],[122,124],[124,127],[127,130],[130,133],[133,136]]}
MERGE={'goose':[(8,9)]}
NUM={'anemia':{61:'١',64:'٢',65:'٣',82:'١',95:'٢'}}
KEEP={'goose':[0.45,1.20,5.48,11.20,12.70,13.78,17.20,20.34,20.78,21.91,47.64,51.84],
      'anemia':[0.45,1.20,7.46,11.70,14.38,15.82,18.74,20.68,21.93,49.68,57.64]}
n=sys.argv[1]
w=json.load(open(f'{S}/w4_{n}/words.json')); E=json.load(open(f'{S}/w4_{n}/edits.json')); fix=E['fix']; drop=set(E.get('drop',[]))
W=[{'w':fix.get(str(i),x[2]),'t':x[0],'e':x[1],'g':False} for i,x in enumerate(w)]
for a,b in MERGE.get(n,[]): W[a]=dict(W[a],w=W[a]['w']+' '+W[b]['w'],e=W[b]['e']); W[b]=None
d=json.load(open(f'data_{n}.json'))
d['chunks']=[[W[i] for i in range(a,b) if W[i] is not None and i not in drop] for a,b in ROWS[n]]
for c in d['chunks']: assert 1<=len(c)<=4,c
for (a,b),c in zip(ROWS[n],d['chunks']):
    if a in NUM.get(n,{}): c[0]=dict(c[0],num=NUM[n][a])
y=round(statistics.median(d['lap'])); d['lap']=[y]*len(d['lap']); d['xs']=[540]*len(d['xs'])
d['devices']=[]; d['nameHold']=None; d['nameBase']=150; d['nameCap']=40; d['N']['exit']=4.6
d['insert']['drop_to']=d['insert']['end']-0.3
p=open('pill.html').read(); open(f'pp_{n}.html','w').write(p.replace('DATA',json.dumps(d,ensure_ascii=False)))
# glass insert: key line in a navy glass tag, lead-in line light, nothing wider than the screen
i=json.load(open(f'ins_{n}.json'))
for k,c in enumerate(i['cards']):
    for L in c.get('titles',[]):
        if L.get('g') and not (k==0 and len(c['titles'])==1):
            L.update(tag=True,size=min(L.get('size',52),44)); L['g']=False; L['y']+=4
        elif len(c['titles'])>1: L.update(lt=True,size=min(L.get('size',52),40))
        else: L['g']=False
for C in i['cam'][1:]:
    C[1]=540; C[3]=min(C[3],1.1)   # the camera only travels up/down: every card stays whole on screen
i['ball'][-1]=[i['ball'][-1][0],{"s":{"x":540,"y":y}}]
json.dump(i,open(f'ins5_{n}.json','w'),ensure_ascii=False)
open(f'ipage5_{n}.html','w').write(open('ins5.html').read().replace('DATA',json.dumps(i,ensure_ascii=False)))
L=[l.strip() for l in open(f'sfx_{n}.txt') if l.strip()]
keep=[l for l in L if any(abs(float(l.split('@')[1])-k)<0.005 for k in KEEP[n])]
open(f'sfxp_{n}.txt','w').write('\n'.join(keep)+'\n')
print(n,'y',y,'lines',len(d['chunks']),'sfx',len(keep),'frames',round(d['END']['dur']*25),'ins',int((i['open']-0.3)*25),int((i['close']+0.8)*25))
