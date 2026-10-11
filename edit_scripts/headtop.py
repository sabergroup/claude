import subprocess, numpy as np, sys, json
n=sys.argv[1]; W,H=1080,1920
raw=subprocess.run(["ffmpeg","-v","error","-i",f"/tmp/claude-0/w/src/{n}.mp4","-vf","format=gray","-f","rawvideo","-"],capture_output=True).stdout
f=np.frombuffer(raw,np.uint8).reshape(-1,H,W)
tops=[]
for fr in f:
    reg=fr[:900,330:780]
    cnt=(reg<95).sum(1)
    rows=np.where(cnt>14)[0]
    tops.append(int(rows[0]) if len(rows) else 900)
json.dump(tops,open(f"/tmp/claude-0/w/{n}_head.json","w"))
t=np.array(tops); print(n, "min",t.min(),"p5",np.percentile(t,5),"median",np.median(t))
for a in range(0,len(t),25): print(f"{a/25:.0f}:{t[a:a+25].min()}",end=" ")
print()
