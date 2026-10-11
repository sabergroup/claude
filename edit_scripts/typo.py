# Kinetic typography: every word animates by itself (slam-in, settle, gold light sweep, staggered exit).
import math, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import anim2 as A
from anim2 import SS, ACC, DARK, cl, eo, eb, eio

WHITE = (255, 255, 255, 255)
GOLD = ACC + (255,)


@functools.lru_cache(None)
def word(w, size, gold=False):
    f = A.font(size * SS)
    kw = {"direction": "rtl", "language": "ar"} if any(ord(c) > 127 for c in w) else {}
    sw = max(2, int(size * SS * 0.075))
    l, t, r, b = f.getbbox(w, stroke_width=sw, **kw)
    im = Image.new("RGBA", (r - l + 8, int(size * SS * 1.6)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - l, int(size * SS * 0.25)), w, font=f, fill=GOLD if gold else WHITE,
                            stroke_width=sw, stroke_fill=DARK + (255,), **kw)
    return im


SP = 0.26


def line_width(words, size):
    return sum(word(w, size).width for w, *_ in words) + size * SS * SP * (len(words) - 1)


def draw_line(layer, t, words, cx, cy, size, exit_t=None, lsc=1.0, lal=1.0, sweep_t=None, slam=1.35):
    """words: [(text, t_in, gold)] in reading order. cx, cy in output px."""
    n = len(words)
    tot = line_width(words, size) * lsc
    x = cx * SS + tot / 2                          # RTL: start at the right edge
    for i, (w, ti, gold) in enumerate(words):
        im = word(w, size, gold)
        ww = im.width * lsc
        p = (t - ti) / 0.36
        if p > 0:
            sc = (1 + (slam - 1) * (1 - eo(p))) * lsc
            al = eo(p * 2.2) * lal
            blur = 9 * SS * (1 - eo(p * 1.8))
            if exit_t is not None and t >= exit_t:
                q = cl((t - exit_t - (n - 1 - i) * 0.05) / 0.2)
                al *= 1 - eo(q); sc *= 1 - 0.35 * eo(q)
            if al > 0.01:
                src = im
                if sweep_t is not None and 0 <= t - sweep_t < 0.7 and not gold:
                    src = sweep(im, w, size, (t - sweep_t) / 0.7, i, n)
                if blur > 1.5:
                    src = src.filter(ImageFilter.GaussianBlur(blur))
                tw, th = max(1, int(src.width * sc)), max(1, int(src.height * sc))
                src = src.resize((tw, th), Image.BICUBIC) if abs(sc - 1) > .01 else src
                if al < .999:
                    src = src.copy(); src.putalpha(src.getchannel("A").point(lambda v: int(v * al)))
                wc = x - ww / 2
                A.put(layer, src, wc - tw / 2, cy * SS - th / 2)
        x -= ww + size * SS * SP * lsc


def sweep(im, w, size, u, i, n):
    """gold light passing over the letters (right to left across the whole line)"""
    g = word(w, size, True)
    band_x = im.width * (1.3 - 1.6 * cl(u * (n + 0.6) - i))
    xs = np.arange(im.width)[None, :]
    m = np.clip(1 - np.abs(xs - band_x) / (im.width * 0.35 + 1), 0, 1)
    ga = (np.asarray(g.getchannel("A")).astype(np.float32) * m).astype(np.uint8)
    g2 = g.copy(); g2.putalpha(Image.fromarray(ga))
    out = im.copy(); out.alpha_composite(g2)
    return out


# ------------------------------------------------------------------ labels (replace the bars)
LS = 66


def label(layer, t, a, cy):
    steps = a["steps"]; t0, t1 = a["t0"], a["t1"]
    gold_words = set(a.get("gold", []))
    for k, (ts, _ic, text) in enumerate(steps):
        nxt = steps[k + 1][0] if k + 1 < len(steps) else None
        ws = text.split(); n = len(ws)
        te = (t0 + 0.04) if k == 0 else ts + 0.22
        ex = nxt if nxt is not None else t1 - 0.22 - 0.05 * (n - 1) - 0.02
        if t >= ex + 0.22 + 0.05 * (n - 1) + 0.01: continue
        words = [(w, te + i * 0.12, w in gold_words) for i, w in enumerate(ws)]
        draw_line(layer, t, words, 540, cy, LS, exit_t=ex, sweep_t=te + 0.12 * n + 0.45)
        if "strike" in a and k == len(steps) - 1 and t >= a["strike"]:
            p = eio((t - a["strike"]) / 0.45)
            wdt = line_width(words, LS)
            xr = 540 * SS + wdt / 2; xl = xr - wdt * p
            if t < ex:
                ImageDraw.Draw(layer).line([(xr, cy * SS + 4 * SS), (xl, cy * SS + 4 * SS)], fill=ACC, width=8 * SS)


# ------------------------------------------------------------------ hook
def hook(layer, t, a):
    for ln in a["lines"]:
        if t < ln["words"][0][1]: continue
        # keyframed line position: [(time, y, scale, alpha)]
        y, sc, al = ln["y"], 1.0, 1.0
        for (kt, ky, ks, ka) in ln.get("moves", []):
            if t >= kt:
                u = eio((t - kt) / 0.38)
                y, sc, al = y + (ky - y) * u, sc + (ks - sc) * u, al + (ka - al) * u
        words = [(w, ti, g) for (w, ti, g) in ln["words"]]
        cnt = ln.get("count")
        if cnt:
            c0, c1 = cnt
            nval = int(round(100 * eio((t - c0) / (c1 - c0))))
            words = [(f"{nval}%", c0, True)]
            if t >= c0:   # burst ring behind the number
                u = (t - c0) / 0.6
                if u < 1:
                    R = (60 + 260 * eo(u)) * SS
                    ImageDraw.Draw(layer).ellipse((540 * SS - R, y * SS - R, 540 * SS + R, y * SS + R),
                                                  outline=ACC + (int(230 * (1 - u)),), width=int(6 * SS * (1 - u)) + 1)
        draw_line(layer, t, words, 540, y, ln["size"], exit_t=ln.get("out", a["t1"] - 0.32),
                  lsc=sc, lal=al, slam=ln.get("slam", 1.35))
