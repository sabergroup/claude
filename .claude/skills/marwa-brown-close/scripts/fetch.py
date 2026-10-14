"""Prepare a work dir: video from Drive, El Messiri fonts, SFX library (from sfx_library/catalog.json).
usage: python3 fetch.py <WORK> <drive_file_id_or_url>"""
import os,sys,re,json,subprocess
W=sys.argv[1]; vid=sys.argv[2]
m=re.search(r"/d/([A-Za-z0-9_-]+)",vid); vid=m.group(1) if m else vid
os.makedirs(f"{W}/src",exist_ok=True); os.makedirs(f"{W}/fonts",exist_ok=True); os.makedirs(f"{W}/sfx",exist_ok=True)
def get(url,dst):
    if not os.path.exists(dst) or os.path.getsize(dst)==0: subprocess.run(["curl","-sSL","-o",dst,url],check=True)
get(f"https://drive.usercontent.google.com/download?id={vid}&export=download&confirm=t",f"{W}/src/vid.mp4")
for w in (500,700):
    css=subprocess.run(["curl","-sS","-A","Mozilla/4.0",f"https://fonts.googleapis.com/css2?family=El+Messiri:wght@{w}"],capture_output=True,text=True).stdout
    get(re.search(r"https://[^)]+",css).group(0),f"{W}/fonts/EM{w}.ttf")
cat=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","..","..","..","sfx_library","catalog.json")))
ev={}
for s in cat["sounds"]:
    ids=s["drive_ids"]; i=ids.get(".wav") or next(iter(ids.values()))
    get(f"https://drive.usercontent.google.com/download?id={i}&export=download&confirm=t",f"{W}/sfx/{s['file']}")
    ev[s["file"]]=dict(len=s["length"],events=s["events"])
json.dump(ev,open(f"{W}/sfx_events.json","w"),ensure_ascii=False)
subprocess.run(["ffprobe","-v","error","-show_entries","stream=codec_name,width,height,r_frame_rate:format=duration","-of","compact",f"{W}/src/vid.mp4"])
print("ready:",W)
