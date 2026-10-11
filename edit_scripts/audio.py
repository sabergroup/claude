import sys, subprocess, numpy as np
sys.path.insert(0, "/tmp/claude-0/scripts")
from plan import PLANS
WD = "/tmp/claude-0/w"; SR = 48000
def load(path):
    a = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",path,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout, np.float32)
    return a.reshape(-1, 2).copy()
def env_info(a):
    m = np.abs(a).mean(1); e = np.convolve(m, np.ones(480)/480, "same")
    return np.argmax(e > 0.1*e.max())/SR, np.argmax(e)/SR
name = sys.argv[1]; plan = PLANS[name]
voice = load(f"{WD}/src/{name}.mp4"); mix = voice.copy()
for fn, t, align, maxlen in plan["sfx"]:
    for a, b in plan["protect"]:
        assert not (a - 0.05 < t < b), (fn, t)
    s = load(f"{WD}/sfx/{fn}.MP3")
    on, pk = env_info(s)
    off = on if align == "onset" else pk
    st = int(round((t - off) * SR))
    if st < 0: s = s[-st:]; st = 0
    if maxlen:
        L = int((off + maxlen) * SR); s = s[:L].copy()
        fl = int(0.25 * SR); s[-fl:] *= np.linspace(1, 0, fl)[:, None]
    rms = 20*np.log10(np.sqrt((s**2).mean()) + 1e-9); pkdb = 20*np.log10(np.abs(s).max() + 1e-9)
    g = min(-27 - rms, -6 - pkdb)
    s = s * 10**(g/20)
    end = min(len(mix), st + len(s))
    for a, b in plan["protect"]:
        assert end/SR <= a + 0.05 or st/SR >= b, ("sfx spills into protected zone", fn)
    mix[st:end] += s[:end-st]
    print(f"{fn:16s} at {t:6.2f} start {st/SR:6.2f} gain {g:+.1f}dB")
pk = np.abs(mix).max()
if pk > 0.98:  # soft limit only the sfx-heavy peaks
    mix = np.tanh(mix / 0.98) * 0.98
mix.astype(np.float32).tofile(f"{WD}/{name}_mix.f32")
