import sys,subprocess,numpy as np,json
S="/tmp/claude-0/-home-user-claude/5b00ce15-a751-5c6f-a77b-d1addef998ec/scratchpad"
sys.path.insert(0,S); from plan import A,segs,SR
EV=json.load(open(f"{S}/sfx_events.json"))
def load(f):
    a=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f"{S}/sfx/{f}","-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout,np.float32)
    return a.reshape(-1,2).copy()
# (time in video, file, event indices (first,last) or None=whole, align 'onset'|'peak', target peak dBFS, reason)
PLAN=[
 (0.30,"Swoosh Accent 2.wav",None,"peak",-27,"ظهور اسم الدكتورة"),
 (3.93,"iphone tap 1.MP3",(0,0),"onset",-24,"أيقونة الموبايل: كلنا ماسكين الموبايل"),
 (4.645,"Zoom 5.wav",None,"peak",-27,"ترانزيشن زوم هادي"),
 (6.08,"soundjay_scroll_main__soundjay_scroll_main-04.wav",(0,3),"onset",-27,"أيقونة الساعة: طول الوقت (تكتكة)"),
 (10.29,"Swoosh Accent 4.wav",None,"peak",-28,"أيقونة الخطوط والتجاعيد"),
 (13.27,"pop-up__pop-up.wav",None,"onset",-25,"أيقونة التحذير: إهمال"),
 (14.57,"ui 1.MP3",None,"onset",-27,"أيقونة العين: تبان أكتر"),
 (18.15,"New Text Message Ding.wav",None,"onset",-28,"أيقونة القلب: نهتم"),
 (21.45,"notification.MP3",None,"onset",-28,"أيقونة الدرع: ماتقلقيش"),
 (24.17,"Magic Collect Shimmer Reveal Glitter Particles Tonal Multi Swell High Bright 02.wav",None,"onset",-25,"أيقونة اللمعة: إجراءات تجميلية"),
 (24.445,"Zoom Transition.wav",None,"peak",-29,"ترانزيشن زوم هادي"),
 (27.90,"chat-message__chat-message.wav",None,"onset",-27,"أيقونة النقطة: الكولاجين"),
 (29.82,"Zoom 4.wav",None,"peak",-29,"أيقونة الأسهم: شد الجلد"),
 (33.56,"Click 3.wav",(0,0),"onset",-23,"أيقونة اللمبة: نصيحتي (كليك لمبة)"),
 (34.24,"soundjay_scroll_main__soundjay_scroll_main-03.wav",(0,2),"onset",-28,"أيقونة الساعة الرملية: ماتنتظريش"),
 (36.84,"Chat Notification.wav",None,"onset",-26,"أيقونة النتيجة: احجزي استشارتك"),
]
voice=np.concatenate([A[s:e] for s,e in segs]).astype(np.float32)
vm=voice.mean(1); fr=vm[:len(vm)//480*480].reshape(-1,480); r=np.sqrt((fr**2).mean(1))
VOICE_RMS=20*np.log10(np.sqrt((r[r>np.percentile(r,40)]**2).mean()))
REL=float(sys.argv[1]) if len(sys.argv)>1 else -6
print("voice speaking RMS dBFS",round(VOICE_RMS,1))
mix=voice.copy(); log=[]
for t,f,ev,al,tgt,why in PLAN:
    a=load(f); E=EV[f]["events"]
    if ev:
        s0=E[ev[0]]["start"]; e0=E[ev[1]]["end"]+0.06
    else: s0=E[0]["start"]; e0=E[-1]["end"]+0.25
    seg=a[max(0,int((s0-0.01)*SR)):int(e0*SR)].copy()
    fo=min(len(seg),int(0.04*SR)); seg[-fo:]*=np.linspace(1,0,fo)[:,None]
    env=np.abs(seg).max(1)
    off=0.01 if al=="onset" else np.argmax(np.convolve(env,np.ones(480)/480,"same"))/SR
    e1=np.abs(seg).max(1); act=seg[e1>e1.max()*0.1]
    srms=20*np.log10(np.sqrt((act**2).mean())+1e-9); spk=20*np.log10(np.abs(seg).max()+1e-9)
    gdb=min(VOICE_RMS+REL+(tgt+27)-srms, -4-spk)   # tgt now = small per-effect trim around -27
    g=10**(gdb/20); seg*=g
    st=int(round((t-off)*SR)); en=min(len(mix),st+len(seg))
    mix[st:en]+=seg[:en-st]
    log.append(dict(t=round(t,2),file=f,events=ev,gain_db=round(float(20*np.log10(g)),1),why=why))
    print(f"{t:6.2f} {f[:40]:40s} ev={ev} gain {20*np.log10(g):+.1f} dB")
print("mix peak dBFS",round(20*np.log10(np.abs(mix).max()),2),"voice peak",round(20*np.log10(np.abs(voice).max()),2))
assert np.abs(mix).max()<0.99
mix.tofile(f"{S}/mix_sfx.f32"); json.dump(log,open(f"{S}/sfx_used.json","w"),ensure_ascii=False,indent=1)
