# Burns the branded intro (logo, credit, name card) onto the start of a video.
# usage: python3 intro.py <in.mp4> <out.mp4> <theme> [seconds_to_keep]
import sys, subprocess
import brand as B

src, dst, th = sys.argv[1:4]
keep = sys.argv[4] if len(sys.argv) > 4 else None
FPS = 25
n = int(B.INTRO_LEN * FPS) + 1
cmd = ["ffmpeg", "-v", "error", "-y", "-i", src,
       "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{B.W}x{B.H}", "-r", str(FPS), "-i", "-",
       "-filter_complex", "[0:v][1:v]overlay=0:0:eof_action=pass:format=auto,format=yuv420p[v]",
       "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "copy"]
if keep: cmd += ["-t", keep]
p = subprocess.Popen(cmd + [dst], stdin=subprocess.PIPE)
for i in range(n):
    p.stdin.write(B.intro_frame(i / FPS, th).tobytes())
p.stdin.close(); p.wait()
print(dst, "rc", p.returncode)
