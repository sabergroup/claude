# Full edit for one video: branded opening, top captions OR icon chips (never both),
# soft transitions on the jump cuts, added SFX on top of the untouched original voice.
# usage: python3 make_video.py <plan_name> <src.mp4> <out.mp4>
import sys, json, math, subprocess, functools
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
import brand as B
from brand import eo, cl
import sfx

FPS = 25
CAP_Y = 262                # caption centre line, above her head in both framings
CHIP_Y = 262


# ------------------------------------------------------------------ plans
PLANS = {
    "hair": dict(
        theme="cocoa",
        cuts=[2.12, 7.04, 9.48, 12.24, 14.08, 16.76, 19.24, 21.52, 26.12, 28.32, 33.20],
        # (text, t_in, t_out, accent words)
        caps=[
            ("شعرك بيقع", 0.00, 1.00, {"بيقع"}),
            ("أكتر من الطبيعي؟", 1.00, 2.20, {"الطبيعي؟"}),
            ("قبل ما تجربي", 2.20, 3.26, set()),
            ("أي أمبولات", 3.26, 4.16, {"أمبولات"}),
            ("أو جلسات للشعر", 4.16, 5.30, {"جلسات"}),
            ("مهم تسمعي", 5.54, 6.40, {"مهم"}),
            ("الكلام ده الأول", 6.40, 7.04, set()),
            ("والأهم من العلاج", 7.08, 8.32, {"والأهم"}),
            ("إننا نفهم السبب", 8.32, 9.48, {"السبب"}),
            ("لأن تساقط الشعر", 9.52, 11.04, {"تساقط"}),
            ("مش بس مشكلة واحدة", 11.04, 12.24, {"واحدة"}),
            ("ومش كل الحالات", 12.26, 13.10, set()),
            ("بتحتاج نفس العلاج", 13.10, 14.08, {"نفس"}),
            ("ممكن يكون السبب", 14.12, 15.50, {"السبب"}),
            # 15.54-21.52: cause chips replace captions
            ("وعشان كده", 21.54, 22.60, set()),
            ("علاج الشعر الصح", 22.60, 24.24, {"الصح"}),
            ("بيبدأ بتحديد", 24.24, 25.44, set()),
            ("السبب الأول", 25.44, 26.12, {"السبب"}),
            ("وبعدها بنختار", 26.14, 27.56, set()),
            ("الخطة المناسبة", 27.56, 28.32, {"المناسبة"}),
            # 28.52-33.20: treatment chips replace captions
            ("وخلي بالك", 33.24, 33.96, set()),
            ("كل ما بنحدد السبب", 33.96, 35.24, {"السبب"}),
            ("بدري", 35.24, 36.24, {"بدري"}),
            ("العلاج بيكون أبسط", 36.24, 37.60, {"أبسط"}),
            ("والنتيجة بتكون أحسن", 37.60, 39.20, {"أحسن"}),
        ],
        # (icon, label, t_in, t_out)
        chips=[
            ("pill", "نقص فيتامينات", 15.54, 16.80),
            ("drop-half", "اضطراب هرموني", 16.82, 18.00),
            ("dna", "عوامل وراثية", 18.02, 19.24),
            ("baby", "بعد الحمل والولادة", 19.26, 21.52),
            ("pill", "علاج دوائي", 28.52, 29.86),
            ("syringe", "جلسات", 29.86, 31.26),
            ("drop", "PRP", 31.26, 32.32),
            ("sparkle", "الخلايا الجذعية", 32.32, 33.20),
        ],
        sparkle_end=37.6,
    ),
}


# ------------------------------------------------------------------ captions (top)
@functools.lru_cache(None)
def cap_img(text, th_name, key):
    return B.caption(text, th_name, key=key, px=60)


def credit_alpha(t):
    return eo((t - 0.3) / 0.45) * (1 - eo((t - 2.7) / 0.45))


def cap_cx(t, w):
    """while the top-right credit block is up, captions sit left of it, then glide to centre"""
    left = max(B.SAFE_X + w / 2, 64 + 620 / 2)
    k = cl(credit_alpha(t) / 1.0) if t < 3.2 else 0.0
    if t < 0.3: k = 1.0                              # block is about to arrive
    return 540 + (left - 540) * eo(k)


def draw_cap(L, t, text, t0, t1, key, th_name):
    if not (t0 - 0.01 <= t < t1 + 0.18): return
    im = cap_img(text, th_name, frozenset(key))
    p = eo((t - t0) / 0.28); q = eo((t - t1) / 0.18) if t > t1 else 0
    a = p * (1 - q)
    if a <= 0.01: return
    sc = 0.92 + 0.08 * p
    if sc < 0.995:
        im = im.resize((int(im.width * sc), int(im.height * sc)), Image.BICUBIC)
    if p < 0.6:
        im = im.filter(ImageFilter.GaussianBlur(6 * (1 - p / 0.6)))
    cx = cap_cx(t, im.width)
    B.put(L, im, cx - im.width / 2, CAP_Y - im.height / 2 + 14 * (1 - p) - 8 * q, a)


# ------------------------------------------------------------------ chips (replace captions)
@functools.lru_cache(None)
def chip_img(name, label, th_name):
    return B.icon_chip(name, label, th_name, px=72)


def draw_chip(L, t, name, label, t0, t1, th_name, idx):
    if not (t0 - 0.01 <= t < t1 + 0.2): return
    im = chip_img(name, label, th_name)
    p = eo((t - t0) / 0.35); q = eo((t - t1) / 0.2) if t > t1 else 0
    a = p * (1 - q)
    if a <= 0.01: return
    sc = 0.8 + 0.2 * B.eio(p)
    im2 = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    B.put(L, im2, 540 - im2.width / 2, CHIP_Y - im2.height / 2, a)
    # sparkle accent that twinkles at the chip's corner on entry
    th = B.theme(th_name)
    s = eo((t - t0) / 0.5) * (1 - eo((t - t0 - 0.5) / 0.4))
    if s > 0.02:
        sp = B.icon("sparkle", 30 + 10 * s, th["accent"], "fill").rotate(-60 * s, Image.BICUBIC)
        side = 1 if idx % 2 == 0 else -1
        x = 540 + side * (im2.width / 2 - 6) - sp.width / 2
        B.put(L, sp, x, CHIP_Y - im2.height / 2 - sp.height / 2 - 4, s)


def draw_sparkles(L, t, t0, th_name):
    th = B.theme(th_name)
    for i, (dx, dy, d) in enumerate([(-250, -40, 0.0), (240, 30, 0.25), (-180, 60, 0.5)]):
        u = (t - t0 - d) / 0.9
        if 0 < u < 1:
            s = math.sin(math.pi * u)
            sp = B.icon("sparkle", 26 + 18 * s, th["accent"], "fill").rotate(-90 * u, Image.BICUBIC)
            B.put(L, sp, 540 + dx - sp.width / 2, CAP_Y + dy - sp.height / 2, s * 0.9)


# ------------------------------------------------------------------ transitions on cuts
LEAK = None


def leak(th_name):
    global LEAK
    if LEAK is None:
        th = B.theme(th_name)
        g = Image.new("L", (B.W // 4, B.H // 4), 0); d = ImageDraw.Draw(g)
        d.ellipse((-60, -80, B.W // 4 + 20, B.H // 8 + 40), fill=255)
        g = g.filter(ImageFilter.GaussianBlur(70)).resize((B.W, B.H), Image.BICUBIC)
        col = Image.new("RGB", (B.W, B.H), th["accent"][:3])
        LEAK = (col, g)
    return LEAK


def transition(fr, t, cuts, th_name, big):
    """push + defocus into the cut, settle out of it, with a warm champagne bloom."""
    for c in cuts:
        dt = t - c
        span = 0.20 if not big.get(c) else 0.28
        if -span <= dt < span:
            u = 1 - abs(dt) / span                 # 0 far, 1 at the cut
            e = u * u * (3 - 2 * u)
            sc = 1 + (0.045 if dt < 0 else 0.035) * e
            w, h = fr.size
            nw, nh = int(w * sc), int(h * sc)
            fr = fr.resize((nw, nh), Image.BICUBIC).crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))
            if e > 0.08:
                fr = fr.filter(ImageFilter.GaussianBlur(5 * e))
            col, m = leak(th_name)
            fr = Image.composite(Image.blend(fr, col, 0.55), fr, m.point(lambda v, e=e: int(v * 0.32 * e)))
            # lift exposure a touch at the exact cut
            if e > 0.5:
                fr = Image.blend(fr, Image.new("RGB", fr.size, (255, 246, 236)), 0.06 * (e - 0.5) * 2)
            break
    return fr


# ------------------------------------------------------------------ main
def main(plan_name, src, dst):
    P = PLANS[plan_name]; th = P["theme"]
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                               capture_output=True, text=True).stdout)
    n = int(round(dur * FPS))
    big = {P["cuts"][0]: True}

    # audio: original voice untouched + SFX layer
    mix_path = dst + ".sfx.wav"
    events = [("whoosh", c - 0.16) for c in P["cuts"]]
    events += [("chime", c[2] + 0.02) for c in P["chips"]]
    events += [("shimmer", 0.55), ("shimmer", P["sparkle_end"])]
    sfx.render_layer(events, dur, mix_path)

    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{B.W}x{B.H}", "-r", str(FPS), "-i", "-",
                            "-i", src, "-i", mix_path,
                            "-filter_complex", "[1:a][2:a]amix=inputs=2:duration=first:normalize=0[a]",
                            "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", dst],
                           stdin=subprocess.PIPE)
    fsz = B.W * B.H * 3
    for i in range(n):
        raw = dec.stdout.read(fsz)
        if len(raw) < fsz: break
        t = i / FPS
        fr = Image.frombuffer("RGB", (B.W, B.H), raw, "raw", "RGB", 0, 1)
        fr = transition(fr, t, P["cuts"], th, big)
        L = B.intro_frame(t, th) if t < B.INTRO_LEN else Image.new("RGBA", (B.W, B.H), (0, 0, 0, 0))
        for text, t0, t1, key in P["caps"]:
            draw_cap(L, t, text, t0, t1, key, th)
        for k, (ic, lab, t0, t1) in enumerate(P["chips"]):
            draw_chip(L, t, ic, lab, t0, t1, th, k)
        draw_sparkles(L, t, P["sparkle_end"], th)
        fr = fr.convert("RGBA"); fr.alpha_composite(L)
        enc.stdin.write(fr.convert("RGB").tobytes())
        if i % 100 == 0: print(f"{t:5.1f}s", flush=True)
    enc.stdin.close(); enc.wait(); dec.wait()
    print(dst, "rc", enc.returncode)


if __name__ == "__main__":
    main(*sys.argv[1:4])
