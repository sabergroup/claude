import re,sys,subprocess,json,html
def ls(fid):
    h=subprocess.run(["curl","-sSL",f"https://drive.google.com/embeddedfolderview?id={fid}"],capture_output=True,text=True).stdout
    items=re.findall(r'<a href="https://drive.google.com/(file/d|drive/folders)/([A-Za-z0-9_-]+)[^"]*"[^>]*>.*?<div class="flip-entry-title">([^<]+)</div>',h,re.S)
    return [(k,i,html.unescape(n)) for k,i,n in items]
out=[]
def walk(fid,path):
    for k,i,n in ls(fid):
        if k=="drive/folders": walk(i,path+n+"/")
        else: out.append((i,path+n))
walk(sys.argv[1],"")
json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False,indent=0)
print(len(out))
for i,n in out: print(n)
