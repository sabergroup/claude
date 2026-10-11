# Motion-graphics layer: every element is keyframed and keeps moving while on screen.
import math, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SS = 2                         # supersampling for the overlay band
BW, BH = 1080, 1700            # overlay band in output pixels
CY = 212                       # pill centre line
PH = 100                       # pill height
ACC = (233, 184, 114)
DARK = (20, 24, 26)
BODY = (18, 22, 24)
FONT = "/tmp/claude-0/w/fonts/tajawal-700.ttf"


def cl(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def eo(p): p = cl(p); return 1 - (1 - p) ** 3
def ei(p): p = cl(p); return p ** 3
def eio(p): p = cl(p); return 4*p**3 if p < .5 else 1 - (-2*p + 2) ** 3 / 2
def eb(p, c=1.7): p = cl(p); return 1 + (c + 1) * (p - 1) ** 3 + c * (p - 1) ** 2


@functools.lru_cache(None)
def font(px): return ImageFont.truetype(FONT, px, layout_engine=ImageFont.Layout.RAQM)


@functools.lru_cache(None)
def txt(s, size, col=(255, 255, 255, 255)):
    f = font(size * SS)
    kw = {"direction": "rtl", "language": "ar"} if any(ord(c) > 127 for c in s) else {}
    l, t, r, b = f.getbbox(s, **kw)
    im = Image.new("RGBA", (r - l + 4, int(size * SS * 1.45)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - l, int(size * SS * 0.2)), s, font=f, fill=col, **kw)
    return im




# ------------------------------------------------------------------ icons (animated)
def icon(name, d, lt, fg=DARK, bg=ACC, prog=1.0):
    """d in output px; lt = seconds since this icon state started; prog = draw-on progress."""
    S = SS * 3; D = int(d * S)
    im = Image.new("RGBA", (D, D), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    g.ellipse((0, 0, D - 1, D - 1), fill=bg)
    lw = max(2, int(D * 0.08)); c = D / 2
    def L(pts, w=lw): g.line([(x*D, y*D) for x, y in pts], fill=fg, width=w, joint="curve")
    def partial(pts, p):          # draw a polyline up to fraction p of its length
        segs = list(zip(pts[:-1], pts[1:])); lens = [math.dist(a, b) for a, b in segs]; tot = sum(lens)
        rem = tot * cl(p); out = [pts[0]]
        for (a, b), ln in zip(segs, lens):
            if rem >= ln: out.append(b); rem -= ln
            else:
                f = rem / ln if ln else 0; out.append((a[0]+(b[0]-a[0])*f, a[1]+(b[1]-a[1])*f)); break
        if len(out) > 1: L(out)
    if name == "check":
        partial([(.29, .52), (.44, .67), (.72, .37)], eo(lt / 0.35) * prog)
    elif name == "x":
        p = eo(lt / 0.4)
        partial([(.34, .34), (.66, .66)], p * 2); partial([(.66, .34), (.34, .66)], p * 2 - 1)
    elif name == "plus":
        a = math.radians(180 * (1 - eo(lt / 0.5))); s = 1 + 0.08 * math.sin(lt * 6)
        for ang in (a, a + math.pi/2):
            dx, dy = math.cos(ang) * .2 * s, math.sin(ang) * .2 * s
            L([(.5 - dx, .5 - dy), (.5 + dx, .5 + dy)])
    elif name == "search":
        ox = .05 * math.cos(lt * 5); oy = .05 * math.sin(lt * 5)
        g.ellipse(((.27+ox)*D, (.27+oy)*D, (.57+ox)*D, (.57+oy)*D), outline=fg, width=lw)
        L([(.54+ox, .54+oy), (.72+ox, .72+oy)])
    elif name == "eye":
        ph = (lt % 1.7) / 1.7
        op = 1 - math.sin(math.pi * (ph - .82) / .18) if ph > .82 else 1
        h = .22 * max(op, .08)
        g.chord((.18*D, (.5-h)*D, .82*D, (.5+h)*D), 0, 360, outline=fg, width=lw)
        px = .5 + .07 * math.sin(lt * 2.6)
        if op > .3:
            r = .085 * min(1, op)
            g.ellipse(((px-r)*D, (.5-r)*D, (px+r)*D, (.5+r)*D), fill=fg)
    elif name == "spark":
        rot = lt * 1.6; pul = 1 + .18 * math.sin(lt * 9)
        for i in range(8):
            a = rot + i * math.pi / 4; r1 = (.30 if i % 2 == 0 else .21) * pul
            L([(c/D + .10*math.cos(a), c/D + .10*math.sin(a)), (c/D + r1*math.cos(a), c/D + r1*math.sin(a))])
    elif name == "cloud":
        by = .03 * math.sin(lt * 4)
        for (x, y, r) in [(.37, .47, .12), (.51, .40, .15), (.63, .48, .11)]:
            g.ellipse(((x-r)*D, (y-r+by)*D, (x+r)*D, (y+r+by)*D), fill=fg)
        g.rectangle((.28*D, (.47+by)*D, .72*D, (.58+by)*D), fill=fg)
        n = int(lt * 4) % 4
        for i in range(min(n, 3)):
            x = .38 + i * .12
            g.ellipse(((x-.035)*D, .66*D, (x+.035)*D, .73*D), fill=fg)
    elif name == "target":
        for r in (.27, .16):
            g.ellipse(((.5-r)*D, (.5-r)*D, (.5+r)*D, (.5+r)*D), outline=fg, width=lw)
        g.ellipse(((.5-.05)*D, (.5-.05)*D, (.5+.05)*D, (.5+.05)*D), fill=fg)
        ph = (lt % 1.0); r = .05 + .4 * eo(ph)
        a = int(255 * (1 - ph))
        g.ellipse(((.5-r)*D, (.5-r)*D, (.5+r)*D, (.5+r)*D), outline=fg + (a,), width=max(1, lw//2))
    elif name == "list":
        ph = (lt % 2.0) / 2.0
        for i, y in enumerate((.36, .50, .64)):
            p = cl((ph * 2.2 - i * .3) / .5)
            g.ellipse((.27*D, (y-.04)*D, .35*D, (y+.04)*D), fill=fg)
            if p > 0: L([(.42, y), (.42 + .30 * eo(p), y)])
    elif name == "calendar":
        g.rounded_rectangle((.26*D, .30*D, .74*D, .74*D), radius=.06*D, outline=fg, width=lw)
        L([(.26, .43), (.74, .43)]); L([(.38, .23), (.38, .34)]); L([(.62, .23), (.62, .34)])
        ph = (lt % 1.8) / 1.8
        partial([(.38, .58), (.47, .66), (.62, .51)], eo(ph / .4))
    elif name == "clock":
        g.ellipse((.24*D, .24*D, .76*D, .76*D), outline=fg, width=lw)
        a = lt * 2 * math.pi * 1.2 - math.pi/2; b = lt * 2 * math.pi * .1 - math.pi/2
        L([(.5, .5), (.5 + .19*math.cos(a), .5 + .19*math.sin(a))])
        L([(.5, .5), (.5 + .12*math.cos(b), .5 + .12*math.sin(b))])
    elif name == "alert":
        s = 1 + .10 * max(0, math.sin(lt * 7))
        pts = [(.5, .5 - .27*s), (.5 + .27*s, .5 + .22*s), (.5 - .27*s, .5 + .22*s)]
        g.polygon([(x*D, y*D) for x, y in pts], outline=fg, width=lw)
        if (lt * 3) % 1 < .7:
            L([(.5, .41), (.5, .55)]); g.ellipse((.47*D, .61*D, .53*D, .67*D), fill=fg)
    elif name == "doc":
        g.rounded_rectangle((.31*D, .23*D, .69*D, .77*D), radius=.05*D, outline=fg, width=lw)
        ph = (lt % 2.0) / 2.0
        for i, y in enumerate((.39, .51, .63)):
            p = cl((ph * 2.2 - i * .3) / .5)
            if p > 0: L([(.40, y), (.40 + .20 * eo(p), y)])
    im = im.resize((int(d * SS), int(d * SS)), Image.LANCZOS)
    return im


# ------------------------------------------------------------------ pill renderer
@functools.lru_cache(64)
def pill_mask(w, h):
    m = Image.new("L", (w * 2, h * 2), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w*2 - 1, h*2 - 1), radius=h, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def draw_pill(layer, cx, cy, w, h, fill, alpha, content=None, glow=0.0, shimmer=None, shadow=False):
    """cx,cy,w,h in output px; content(canvas, w, h) draws in SS units; alpha 0..1"""
    if alpha <= 0.01 or w < 2: return
    W_, H_ = int(w * SS), int(h * SS)
    x0, y0 = int((cx - w/2) * SS), int((cy - h/2) * SS)
    m = pill_mask(W_, H_)
    if shadow:
        sm = m.resize((max(1, W_//6), max(1, H_//6))).filter(ImageFilter.GaussianBlur(2)).resize((W_, H_))
        sh = Image.new("RGBA", (W_, H_), (0, 0, 0, 0)); sh.putalpha(sm.point(lambda v: int(v * .28 * alpha)))
        layer.alpha_composite(sh, (x0, y0 + 6 * SS)) if 0 <= y0 else None
    if glow > 0:   # breathing outline ring
        pad = int(glow * 26 * SS)
        gm = pill_mask(W_ + 2*pad, H_ + 2*pad)
        ring = Image.new("RGBA", gm.size, fill[:3] + (0,))
        ring.putalpha(gm.point(lambda v: int(v * .30 * (1 - glow) * alpha)))
        layer.alpha_composite(ring, (x0 - pad, y0 - pad))
    fa = fill[3] / 255 if len(fill) == 4 else 1
    body = Image.new("RGBA", (W_, H_), fill[:3] + (int(255 * fa),))
    cv = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    if content: content(cv, W_, H_)
    if shimmer is not None and 0 <= shimmer <= 1:
        sx = int(-0.4 * W_ + 1.8 * W_ * shimmer)
        band = Image.new("L", (W_, H_), 0); bd = ImageDraw.Draw(band)
        for i in range(-30, 31):
            bd.line([(sx + i*SS + H_*0.35, 0), (sx + i*SS - H_*0.35, H_)], fill=int(60 * (1 - abs(i) / 30)), width=SS)
        white = Image.new("RGBA", (W_, H_), (255, 255, 255, 0)); white.putalpha(band)
        body.alpha_composite(white)
    body.alpha_composite(cv)
    a = np.asarray(body.getchannel("A")).astype(np.float32) * (np.asarray(m).astype(np.float32) / 255) * alpha
    body.putalpha(Image.fromarray(a.astype(np.uint8)))
    layer.alpha_composite(body, (x0, y0))


def put(canvas, im, x, y, alpha=1.0):
    if alpha <= 0.01: return
    if alpha < .999:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    canvas.alpha_composite(im, (int(x), int(y))) if x >= 0 and y >= 0 else canvas.paste(im, (int(x), int(y)), im)


def reveal(im, f):
    """RTL wipe: keep right-most fraction f of the text image, soft edge"""
    if f >= .999: return im
    w = im.width; edge = 26 * SS
    xs = np.arange(w)[None, :]
    cut = w - (w + edge) * f
    m = np.clip((xs - cut) / edge, 0, 1)
    a = (np.asarray(im.getchannel("A")).astype(np.float32) * m).astype(np.uint8)
    out = im.copy(); out.putalpha(Image.fromarray(a)); return out


# ------------------------------------------------------------------ kinetic words
STAG, WIN = 0.13, 0.42          # stagger between words, duration of one word's entrance
SPACE = 0.28


def kinetic(cv, s, size, col, right, cy, lin, lout=None, n_out_total=None):
    """Draw text RTL word by word. lin = seconds since words started entering.
    lout = seconds since words started leaving (None while on screen)."""
    words = s.split(); ims = [txt(w, size, col) for w in words]
    sp = size * SS * SPACE
    x = right
    n = len(words)
    for i, im in enumerate(ims):
        p = (lin - i * STAG) / WIN
        if p <= 0: x -= im.width + sp; continue
        a = eo(p * 1.6); sc = 0.55 + 0.45 * eb(p); dy = (1 - eo(p)) * 38 * SS
        if lout is not None:          # leave in reverse order, rising up
            q = cl((lout - (n - 1 - i) * 0.06) / 0.22)
            a *= 1 - eo(q); dy -= eo(q) * 30 * SS
        if a > 0.01:
            w_, h_ = max(1, int(im.width * sc)), max(1, int(im.height * sc))
            sim = im.resize((w_, h_), Image.BICUBIC) if abs(sc - 1) > .01 else im
            cx_ = x - im.width / 2
            put(cv, sim, cx_ - w_ / 2, cy - h_ / 2 + 2 * SS + dy, a)
        x -= im.width + sp


def words_time(s): return (len(s.split()) - 1) * STAG + WIN


def text_w(s, size):
    ws = s.split()
    return (sum(txt(w, size).width for w in ws) + size * SS * SPACE * (len(ws) - 1)) / SS


# ------------------------------------------------------------------ envelope shared by all elements
def envelope(t, t0, t1):
    lt, rt = t - t0, t1 - t
    ic = eb(lt / 0.26)
    gr = eo((lt - 0.12) / 0.36)
    tx = eo((lt - 0.30) / 0.40)
    if rt < 0.30:
        gr *= 1 - eio((0.30 - rt) / 0.20)
        ic *= 1 - ei((0.12 - rt) / 0.12)
    return lt, ic, gr, tx


OUT = 0.62     # words start leaving this long before the element ends
def lout_of(t, t1): return (t - (t1 - OUT)) if t1 - t < OUT else None


TS = 46                       # pill text size
ICD = PH - 26                 # icon diameter
TS_DEF, PH_DEF = TS, PH


def text_pill(layer, t, t0, t1, steps, cx=540, cy=CY, extra=None, palette="dark", ts_=None, ph=None):
    TS = ts_ or TS_DEF; PH = ph or PH_DEF; ICD = PH - 26
    """steps: [(time, icon, text)] – icon flips & text rolls on each step"""
    lt, ic, gr, tx = envelope(t, t0, t1)
    if ic <= 0.01: return 0
    k = max(i for i, s in enumerate(steps) if t >= s[0])
    ts, ico, label = steps[k]
    swap = eo((t - ts) / 0.34) if k > 0 else 1.0
    fg_txt = (255, 255, 255, 255) if palette == "dark" else DARK + (255,)
    w_full = lambda s: 30 + text_w(s, TS) + 22 + ICD + 13
    wf = w_full(label) if swap >= 1 else w_full(steps[k-1][2]) + (w_full(label) - w_full(steps[k-1][2])) * swap
    w = PH + (wf - PH) * gr
    bob = 5 * math.sin(2 * math.pi * lt / 2.4) * gr
    shake = 0
    if extra and "strike" in extra and t >= extra["strike"]:
        u = t - extra["strike"]; shake = 9 * math.sin(u * 55) * math.exp(-u * 9)
    sh = None
    if lt > 0.8:
        u = ((lt - 0.8) % 2.6) / 0.7
        sh = u if u <= 1 else None
    fill = BODY + (225,) if palette == "dark" else ACC + (255,)

    def content(cv, W_, H_):
        # icon at the right end, flipping on step change
        d = ICD * ic
        if d > 2:
            if k > 0 and swap < 1:
                fl = abs(math.cos(math.pi * swap)); nm = steps[k-1][1] if swap < .5 else ico
                ilt = (t - steps[k-1][0]) if swap < .5 else (t - ts)
            else:
                fl, nm, ilt = 1, ico, t - ts
            if extra and "strike" in extra and t >= extra["strike"] + 0.25:
                nm, ilt = "x", t - extra["strike"] - 0.25
            bgc, fgc = (ACC, DARK) if palette == "dark" else (DARK, ACC)
            im = icon(nm, d, ilt, fg=fgc, bg=bgc)
            if fl < .999: im = im.resize((max(1, int(im.width * fl)), im.height))
            put(cv, im, W_ - (13 + ICD/2) * SS - im.width/2, H_/2 - im.height/2)
        # text
        right = W_ - (13 + ICD + 22) * SS
        lo = lout_of(t, t1)
        if k > 0 and t - ts < 0.34:      # previous text leaves word by word
            kinetic(cv, steps[k-1][2], TS, fg_txt, right, H_/2, 9, t - ts)
        lin = (t - t0 - 0.30) if k == 0 else (t - ts - 0.16)
        kinetic(cv, label, TS, fg_txt, right, H_/2, lin, lo)
        if extra and "strike" in extra and t >= extra["strike"]:
            p = eo((t - extra["strike"]) / 0.3); tw = text_w(label, TS) * SS
            ImageDraw.Draw(cv).line([(right + 4*SS, H_/2 + 4*SS), (right - (tw + 8*SS) * p, H_/2 + 4*SS)],
                                    fill=ACC, width=5*SS)
    imp = (extra or {}).get("impact")
    if imp:   # slam-in: oversize -> settle, burst ring
        u = (t - t0) / 0.35
        if u < 1:
            shake += 10 * math.sin(u * 40) * (1 - u)
            glow_ring(layer, cx, cy + bob, w, PH, eo(u), 1.0)
    draw_pill(layer, cx + shake, cy + bob, w, PH, fill, min(1, ic * 1.5), content, shimmer=sh)
    return wf


# ------------------------------------------------------------------ composite elements
def steps_pill(layer, t, a):
    t0, t1 = a["t0"], a["t1"]; m1, m2 = a["marks"]
    lt, ic, gr, tx = envelope(t, t0, t1)
    if ic <= .01: return
    l1, l2 = a["labels"]; dot = 34; line = 120
    wf = 40 + text_w(l1, 42) + 18 + dot + 20 + line + 20 + dot + 18 + text_w(l2, 42) + 40
    w = PH + (wf - PH) * gr
    bob = 5 * math.sin(2 * math.pi * lt / 2.4) * gr
    fill_p = cl((t - m1) / (m2 - m1)) if t >= m1 else 0

    def content(cv, W_, H_):
        g = ImageDraw.Draw(cv); cy = H_ / 2
        x = W_ / 2 + wf * SS / 2 - 40 * SS
        lo = lout_of(t, t1); lin = t - t0 - 0.30
        kinetic(cv, l1, 42, (255, 255, 255, 255), x, cy, lin, lo); x -= text_w(l1, 42) * SS + 18*SS
        d1c = x - dot*SS/2; x -= dot*SS + 20*SS
        lx0 = x; x -= line*SS; lx1 = x; x -= 20*SS
        d2c = x - dot*SS/2; x -= dot*SS + 18*SS
        kinetic(cv, l2, 42, (255, 255, 255, 255), x, cy, lin - 0.25, lo)
        # track
        g.line([(lx0, cy), (lx1, cy)], fill=(255, 255, 255, int(70 * tx)), width=4*SS)
        if fill_p > 0:
            xe = lx0 + (lx1 - lx0) * eio(fill_p)
            g.line([(lx0, cy), (xe, cy)], fill=ACC, width=4*SS)
            if fill_p < 1:      # travelling spark
                r = 7*SS*(1 + .3*math.sin(t*20)); g.ellipse((xe-r, cy-r, xe+r, cy+r), fill=(255, 236, 200))
        for dc, mk in ((d1c, m1), (d2c, m2)):
            r = dot*SS/2
            pulse = 1 + .08 * math.sin(t * 7) if t < mk else 1
            g.ellipse((dc - r*pulse, cy - r*pulse, dc + r*pulse, cy + r*pulse), outline=ACC + (int(255*tx),), width=3*SS)
            if t >= mk:
                p = eb((t - mk) / 0.3); rr = r * p
                if rr > 1: g.ellipse((dc - rr, cy - rr, dc + rr, cy + rr), fill=ACC)
                ck = icon("check", dot, t - mk - .12, bg=(0, 0, 0, 0))
                put(cv, ck, dc - ck.width/2, cy - ck.height/2)
                u = (t - mk) / 0.6
                if u < 1:
                    R = r * (1 + 1.6 * eo(u))
                    g.ellipse((dc - R, cy - R, dc + R, cy + R), outline=ACC + (int(200*(1-u)),), width=2*SS)
    draw_pill(layer, 540, CY + bob, w, PH, BODY + (225,), min(1, ic*1.5), content)


def list_pill(layer, t, a):
    t0, t1 = a["t0"], a["t1"]
    lt, ic, gr, tx = envelope(t, t0, t1)
    if ic <= .01: return
    items = a["items"]
    k = max(i for i, s in enumerate(items) if t >= s[0])
    ts, label, filled = items[k]
    final = k == len(items) - 1
    swap = eo((t - ts) / 0.30) if k > 0 else 1
    h = 112; icd = h - 30
    maxw = max(text_w(s[1], 44) for s in items)
    barw = 150
    wf = 34 + barw + 30 + max(maxw, text_w(a["title"], 26)) + 20 + icd + 15
    w = h + (wf - h) * gr
    bob = 5 * math.sin(2 * math.pi * lt / 2.4) * gr
    prevfilled = items[k-1][2] if k > 0 else filled - 1

    def content(cv, W_, H_):
        g = ImageDraw.Draw(cv)
        d = icd * ic
        if d > 2:
            im = icon("check", d, t - ts)
            if final:   # burst ring on the final state
                u = (t - ts) / .6
                if u < 1:
                    R = d*SS/2 * (1 + .8*eo(u)); c = (W_ - (15 + icd/2)*SS, H_/2)
                    g.ellipse((c[0]-R, c[1]-R, c[0]+R, c[1]+R), outline=ACC + (int(220*(1-u)),), width=3*SS)
            put(cv, im, W_ - (15 + icd/2)*SS - im.width/2, H_/2 - im.height/2)
        right = W_ - (15 + icd + 20) * SS
        tt = reveal(txt(a["title"], 26, (255, 255, 255, 150)), tx)
        put(cv, tt, right - tt.width, 10*SS, tx)
        col = ACC + (255,) if final else (255, 255, 255, 255)
        ty = H_ * 0.66; lo = lout_of(t, t1)
        if k > 0 and t - ts < 0.3:
            kinetic(cv, items[k-1][1], 44, (255, 255, 255, 255), right, ty, 9, t - ts)
        lin = (t - t0 - 0.30) if k == 0 else (t - ts - 0.12)
        kinetic(cv, label, 44, col, right, ty, lin, lo)
        # 5-segment progress bar, fills right-to-left with animation
        bx1 = 34*SS + barw*SS; seg = (barw*SS - 4*6*SS) / 5; y = H_/2
        f = prevfilled + (filled - prevfilled) * swap
        for i in range(5):
            xr = bx1 - i * (seg + 6*SS); xl = xr - seg
            g.rounded_rectangle((xl, y - 5*SS, xr, y + 5*SS), radius=5*SS, fill=(255, 255, 255, int(60*tx)))
            fi = cl(f - i)
            if fi > 0:
                g.rounded_rectangle((xr - seg*fi, y - 5*SS, xr, y + 5*SS), radius=5*SS, fill=ACC)
        if final:
            u = (t - ts) % 1.2 / 1.2
            g.rounded_rectangle((34*SS - 4*SS, y - 9*SS, bx1 + 4*SS, y + 9*SS), radius=9*SS,
                                outline=ACC + (int(160*(1-u)),), width=2*SS)
    draw_pill(layer, 540, CY + bob, w, h, BODY + (230,), min(1, ic*1.5), content)


def pair(layer, t, a):
    """main chip; at pair time it turns into ✓ممكن and a second chip ✕ grows out to its left"""
    (tp1, ic1, s1), (tp2, ic2, s2) = a["pair"]
    steps = a["steps"] + [(tp1, ic1, s1)]
    gap = 22
    if t < tp2:
        text_pill(layer, t, a["t0"], a["t1"], steps)
        return
    w1 = 30 + text_w(s1, TS) + 22 + ICD + 13
    w2 = 30 + text_w(s2, TS) + 22 + ICD + 13
    p = eo((t - tp2) / 0.45)
    c1 = 540 + (w2 + gap) / 2 * p
    c2 = 540 - (w1 + gap) / 2 * p
    # second chip has its own entry, shared exit
    text_pill(layer, t, tp2, a["t1"], [(tp2, ic2, s2)], cx=c2)
    text_pill(layer, t, a["t0"], a["t1"], steps, cx=c1)


def cta(layer, t, a):
    t0, t1 = a["t0"], a["t1"]
    lt = t - t0
    rise = (1 - eb(lt / 0.5)) * 70
    bt, bic, btx = a["badge"]
    tp = a["tap"]
    wb = 30 + text_w(btx, TS) + 22 + ICD + 13
    wc = 30 + text_w(a["text"], TS) + 22 + ICD + 13
    gap = 22
    pb = eo((t - bt) / 0.45) if t >= bt else 0
    cx_c = 540 + (wb + gap) / 2 * pb
    cx_b = 540 - (wc + gap) / 2 * pb
    press = math.sin(math.pi * cl((t - tp) / 0.28)) if t >= tp else 0
    if t >= bt:
        text_pill(layer, t, bt, t1, [(bt, bic, btx)], cx=cx_b)
    # breathing glow ring
    _, ic, gr, _ = envelope(t, t0, t1)
    if lt > 0.9 and gr > .5:
        u = ((lt - 0.9) % 1.3) / 1.3
        glow_ring(layer, cx_c, CY + rise, wc, PH, u, gr)
    text_pill(layer, t, t0, t1, [(t0, "calendar", a["text"])], cx=cx_c, cy=CY + rise + press * 4,
              palette="gold")
    if t >= tp and t < tp + 0.6:   # tap ripple
        u = (t - tp) / 0.6
        R = (16 + 60 * eo(u)) * SS; x, y = (cx_c - wc * .15) * SS, (CY + 8) * SS
        ImageDraw.Draw(layer).ellipse((x - R, y - R, x + R, y + R), outline=(255, 255, 255, int(230 * (1 - u))), width=4*SS)
        r = 14 * SS * (1 - u)
        ImageDraw.Draw(layer).ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, int(160 * (1 - u))))


def glow_ring(layer, cx, cy, w, h, u, a):
    pad = 4 + 22 * eo(u)
    W_, H_ = int((w + 2*pad) * SS), int((h + 2*pad) * SS)
    m = pill_mask(W_, H_)
    inner = pill_mask(max(1, W_ - 6*SS), max(1, H_ - 6*SS))
    ring = Image.new("L", (W_, H_), 0); ring.paste(m, (0, 0))
    hole = Image.new("L", (W_, H_), 0); hole.paste(inner, (3*SS, 3*SS))
    ra = np.clip(np.asarray(ring).astype(int) - np.asarray(hole), 0, 255) * (1 - u) * .8 * a
    im = Image.new("RGBA", (W_, H_), ACC + (0,)); im.putalpha(Image.fromarray(ra.astype(np.uint8)))
    layer.alpha_composite(im, (int((cx - w/2 - pad) * SS), int((cy - h/2 - pad) * SS)))


def hook(layer, t, a):
    global OUT
    t0, t1 = a["t0"], a["t1"]
    (s1,), (s2, ic2) = a["lines"]
    keep = OUT; OUT = 0.34                     # short exit: the hook must read for as long as possible
    text_pill(layer, t, t0, t1, [(t0, None, s1)], cy=1330, ts_=52, ph=98)
    t2 = t0 + 0.38
    if t >= t2:
        text_pill(layer, t, t2, t1, [(t2, ic2, s2)], cy=1460, ts_=68, ph=132, palette="gold",
                  extra={"impact": True})
    OUT = keep


# ------------------------------------------------------------------ entry point
def draw_all(frame_rgba, anims, t):
    act = [a for a in anims if a["t0"] <= t < a["t1"]]
    if not act: return None
    layer = Image.new("RGBA", (BW * SS, BH * SS), (0, 0, 0, 0))
    for a in act:
        ty = a["type"]
        if ty == "chip" and "pair" in a: pair(layer, t, a)
        elif ty == "chip": text_pill(layer, t, a["t0"], a["t1"], a["steps"], extra=a)
        elif ty == "steps": steps_pill(layer, t, a)
        elif ty == "list": list_pill(layer, t, a)
        elif ty == "cta": cta(layer, t, a)
        elif ty == "hook": hook(layer, t, a)
    small = layer.resize((BW, BH), Image.LANCZOS)
    frame_rgba.alpha_composite(small, (0, 0))
    al = np.asarray(small.getchannel("A"))
    return al.max(1) > 24          # painted rows (for the head check)
