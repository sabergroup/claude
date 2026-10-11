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
STAG, WIN = 0.12, 0.38          # stagger between words, duration of one word's entrance
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
        a = eo(p * 1.8); sc = 1 + 0.35 * (1 - eo(p)); dy = (1 - eo(p)) * 10 * SS
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
    bob = 0
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
    imp = None
    if imp:   # slam-in: oversize -> settle, burst ring
        u = (t - t0) / 0.35
        if u < 1:
            shake += 10 * math.sin(u * 40) * (1 - u)
            glow_ring(layer, cx, cy + bob, w, PH, eo(u), 1.0)
    draw_pill(layer, cx + shake, cy + bob, w, PH, fill, min(1, ic * 1.5), content, shimmer=sh)
    return wf


# ------------------------------------------------------------------ composite elements
def steps_pill(layer, t, a, cy_=CY):
    t0, t1 = a["t0"], a["t1"]; m1, m2 = a["marks"]
    lt, ic, gr, tx = envelope(t, t0, t1)
    if ic <= .01: return
    l1, l2 = a["labels"]; dot = 34; line = 120
    wf = 40 + text_w(l1, 42) + 18 + dot + 20 + line + 20 + dot + 18 + text_w(l2, 42) + 40
    w = PH + (wf - PH) * gr
    bob = 0
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
    draw_pill(layer, 540, cy_ + bob, w, PH, BODY + (225,), min(1, ic*1.5), content)


def list_pill(layer, t, a, cy_=CY):
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
    bob = 0
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
    draw_pill(layer, 540, cy_ + bob, w, h, BODY + (230,), min(1, ic*1.5), content)


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


def cta(layer, t, a, CY=CY):
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
        text_pill(layer, t, bt, t1, [(bt, bic, btx)], cx=cx_b, cy=CY)
    # breathing glow ring
    _, ic, gr, _ = envelope(t, t0, t1)
    if False:
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
    import typo
    act = [a for a in anims if a["t0"] <= t < a["t1"]]
    if not act: return None
    layer = Image.new("RGBA", (BW * SS, BH * SS), (0, 0, 0, 0))
    for a in act:
        ty = a["type"]
        if ty == "chip" and "pair" in a: pair(layer, t, a)
        elif ty == "chip": bar_label(layer, t, a, a.get("cy", CY))
        elif ty == "steps": steps_pill(layer, t, a, a.get("cy", CY))
        elif ty == "flow": flow_pill(layer, t, a, a.get("cy", CY))
        elif ty == "mirror": mirror_anim(layer, t, a)
        elif ty == "list": list_pill(layer, t, a, a.get("cy", CY))
        elif ty == "cta": cta(layer, t, a, a.get("cy", CY))
        elif ty == "hook": typo.hook(layer, t, a)
    small = layer.resize((BW, BH), Image.LANCZOS)
    frame_rgba.alpha_composite(small, (0, 0))
    al = np.asarray(small.getchannel("A"))
    return al.max(1) > 24          # painted rows (for the head check)


# ================================================================== premium bar-wipe typography
BAR_R = 12


def _bar_img(text, size, h, pad, col=(255, 255, 255, 255), fill=BODY + (238,), wf=None, extra=None):
    tw = text_w(text, size)
    wf = wf or tw + 2 * pad
    W_, H_ = int(wf * SS), int(h * SS)
    im = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, W_ - 1, H_ - 1), radius=BAR_R * SS, fill=fill)
    t = txt(text, size, col)
    im.alpha_composite(t, (int(W_ - pad * SS - t.width), int(H_ / 2 - t.height / 2 + 2 * SS)))
    if extra: extra(im, W_, H_)
    return im


def bar_line(layer, t, te, tx, text, cx, cy, size=56, h=100, pad=36, col=(255, 255, 255, 255),
             fill=BODY + (238,), wf=None, extra=None):
    """gold bar sweeps in from the right, retracts and leaves the dark bar + text; reverse on exit.
    te = entry start, tx = exit start (None = no exit yet)."""
    if t < te: return
    tw = text_w(text, size); wf = wf or tw + 2 * pad
    right = cx + wf / 2; left = cx - wf / 2
    pa = eio((t - te) / 0.30); pb = eio((t - te - 0.26) / 0.36)
    gl, gr = right - wf * pa, right - wf * pb               # entry gold span
    he = left; ge = left
    if tx is not None and t >= tx:
        qa = eio((t - tx) / 0.20); qb = eio((t - tx - 0.14) / 0.20)
        ge, he = left + wf * qa, left + wf * qb              # exit gold span [he, ge]
    lo = max(gr, he)
    if lo < right - 0.5:
        slide = (1 - pb) * 26 * SS            # parallax: text settles while being revealed
        x0 = int((lo - left) * SS)
        bg = Image.new("RGBA", (int(wf * SS), int(h * SS)), (0, 0, 0, 0))
        ImageDraw.Draw(bg).rounded_rectangle((0, 0, bg.width - 1, bg.height - 1), radius=BAR_R * SS, fill=fill)
        bg.alpha_composite(_bar_txt_only(text, size, h, pad, col, wf, extra, slide))
        crop = bg.crop((x0, 0, bg.width, bg.height))
        layer.alpha_composite(crop, (int(lo * SS), int((cy - h / 2) * SS)))
    g = ImageDraw.Draw(layer)
    y0, y1 = (cy - h / 2) * SS, (cy + h / 2) * SS
    if pb < 1 and gl < gr - .5:
        g.rounded_rectangle((gl * SS, y0, gr * SS, y1), radius=BAR_R * SS, fill=ACC)
    if ge > he + .5:
        g.rounded_rectangle((he * SS, y0, ge * SS, y1), radius=BAR_R * SS, fill=ACC)


def _bar_txt_only(text, size, h, pad, col, wf, extra, slide):
    W_, H_ = int(wf * SS), int(h * SS)
    im = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    t = txt(text, size, col)
    im.alpha_composite(t, (int(W_ - pad * SS - t.width - slide), int(H_ / 2 - t.height / 2 + 2 * SS)))
    if extra: extra(im, W_, H_)
    return im


def bar_label(layer, t, a, cy):
    """chip replacement: sequence of labels, each swap = wipe out + wipe in; strike option"""
    steps = a["steps"]; t0, t1 = a["t0"], a["t1"]
    for i, (ts, _ic, label) in enumerate(steps):
        te = t0 + 0.05 if i == 0 else ts + 0.28
        nxt = steps[i + 1][0] if i + 1 < len(steps) else None
        tx = nxt if nxt is not None else t1 - 0.40
        if t >= (nxt + 0.40 if nxt else t1): continue
        extra = None
        if "strike" in a and i == len(steps) - 1 and t >= a["strike"]:
            p = eio((t - a["strike"]) / 0.45)
            def extra(im, W_, H_, p=p, label=label):
                tw = text_w(label, 56) * SS
                x1 = W_ - 36 * SS; x0 = x1 - tw * p
                ImageDraw.Draw(im).line([(x1, H_ / 2 + 3 * SS), (x0, H_ / 2 + 3 * SS)], fill=ACC, width=6 * SS)
        bar_line(layer, t, te, tx, label, 540, cy, extra=extra)


def hook_bars(layer, t, a):
    t1 = a["t1"]; tx_all = t1 - 0.42
    for ln in a["bars"]:
        te = ln["t"]; tx = ln.get("out", tx_all)
        size = ln.get("size", 64); h = ln.get("h", 112)
        col = ACC + (255,) if ln.get("gold") else (255, 255, 255, 255)
        extra = None; wf = None
        if "count" in ln:          # number counting up next to the words
            c0, c1 = ln["count"]
            n = int(round(100 * eio((t - c0) / (c1 - c0)))) if t >= c0 else None
            num_w = text_w("100%", size)
            wf = text_w(ln["text"], size) + 22 + num_w + 2 * 36
            def extra(im, W_, H_, n=n, size=size):
                if n is None: return
                s = f"{n}%"; ti = txt(s, size, ACC + (255,))
                x = 36 * SS + (text_w("100%", size) * SS - ti.width)
                im.alpha_composite(ti, (int(x), int(H_ / 2 - ti.height / 2 + 2 * SS)))
        bar_line(layer, t, te, tx, ln["text"], 540, ln["cy"], size=size, h=h, pad=36, col=col, wf=wf, extra=extra)


# ================================================================== flow infographic (same language as the steps pill)
RED = (176, 72, 62)


def flow_pill(layer, t, a, cy_=CY):
    """items (RTL): {"icon": name | None, "label": str, "on": time, "x": time (optional)}.
    Each node lights up at its time; the track between two nodes fills as he speaks, with a travelling spark."""
    t0, t1 = a["t0"], a["t1"]
    lt, ic, gr, tx = envelope(t, t0, t1)
    if ic <= .01: return
    items = a["items"]; LSZ = 40; dot = 36; icd = 56; gap = 14; track = 74; pad = 40
    widths = []
    for it in items:
        nd = icd if it.get("icon") else dot
        widths.append(nd + gap + text_w(it["label"], LSZ))
    wf = pad * 2 + sum(widths) + track * (len(items) - 1) + 16 * (len(items) - 1)
    w = PH + (wf - PH) * gr

    def content(cv, W_, H_):
        g = ImageDraw.Draw(cv); cy = H_ / 2
        x = W_ / 2 + wf * SS / 2 - pad * SS
        centers = []
        for k, it in enumerate(items):
            nd = icd if it.get("icon") else dot
            c = x - nd * SS / 2
            on = t >= it["on"]
            # label: dim until its moment, then bright (gold if it is the "answer")
            lab_col = (ACC + (255,)) if (on and it.get("gold")) else (255, 255, 255, 255)
            la = tx * (1.0 if on else 0.32)
            if on:
                u = eo((t - it["on"]) / 0.3); la = tx * (0.32 + 0.68 * u)
            im = txt(it["label"], LSZ, lab_col)
            lx = x - nd * SS - gap * SS - im.width
            put(cv, im, lx, cy - im.height / 2 + 2 * SS, la)
            centers.append((c, x - nd * SS - gap * SS - im.width, nd, it))
            x = lx - 16 * SS - track * SS
        # tracks (from node k's left edge area to node k+1)
        for k in range(len(items) - 1):
            c, lx_end, nd, it = centers[k]
            c2, _, nd2, it2 = centers[k + 1]
            x0 = lx_end - 8 * SS; x1 = c2 + nd2 * SS / 2 + 8 * SS
            g.line([(x0, cy), (x1, cy)], fill=(255, 255, 255, int(60 * tx)), width=4 * SS)
            a0, a1 = it["on"], it2["on"]
            if t >= a0 and a1 > a0:
                f = cl((t - a0) / (a1 - a0)); xe = x0 + (x1 - x0) * eio(f)
                g.line([(x0, cy), (xe, cy)], fill=ACC, width=4 * SS)
                if f < 1:
                    r = 7 * SS * (1 + .3 * math.sin(t * 20))
                    g.ellipse((xe - r, cy - r, xe + r, cy + r), fill=(255, 236, 200))
        # nodes
        for c, _, nd, it in centers:
            r = nd * SS / 2; on = t >= it["on"]
            xed = "x" in it and t >= it["x"]
            if it.get("icon"):
                ilt = t - it["on"] if on else 0
                bg = ACC if on else (90, 92, 94)
                if xed: bg = RED
                p = eb((t - it["on"]) / 0.35) if on else 1
                d = nd * (0.8 + 0.2 * p) if on else nd * .8
                im = icon("x" if xed else it["icon"], d, (t - it["x"]) if xed else ilt,
                          fg=(255, 255, 255) if xed else DARK, bg=bg)
                put(cv, im, c - im.width / 2, cy - im.height / 2, tx)
            else:
                pend = (not on) and any(t >= o["on"] for o in items if o is not it)
                pulse = 1 + .08 * math.sin(t * 7) if pend else 1
                g.ellipse((c - r * pulse, cy - r * pulse, c + r * pulse, cy + r * pulse),
                          outline=ACC + (int(255 * tx * (1 if on else .5)),), width=3 * SS)
                if on:
                    p = eb((t - it["on"]) / 0.3); rr = r * p
                    if rr > 1: g.ellipse((c - rr, cy - rr, c + rr, cy + rr), fill=RED if xed else ACC)
                    if xed:
                        mk = icon("x", nd, t - it["x"], fg=(255, 255, 255), bg=(0, 0, 0, 0))
                    else:
                        mk = icon("check", nd, t - it["on"] - .12, bg=(0, 0, 0, 0)) if it.get("check", True) else None
                    if mk is not None: put(cv, mk, c - mk.width / 2, cy - mk.height / 2)
            if on:   # ripple when a node lights up
                u = (t - (it["x"] if xed else it["on"])) / 0.6
                if 0 <= u < 1:
                    R = r * (1 + 1.6 * eo(u))
                    g.ellipse((c - R, cy - R, c + R, cy + R), outline=(RED if xed else ACC) + (int(200 * (1 - u)),), width=2 * SS)
    draw_pill(layer, 540, cy_, w, PH, BODY + (225,), min(1, ic * 1.5), content)


# ================================================================== mirror (one problem) – annotated illustration
def _ellipse_pts(cx, cy, rx, ry, n=120, start=-90):
    return [(cx + rx * math.cos(math.radians(start - 360 * i / n)), cy + ry * math.sin(math.radians(start - 360 * i / n)))
            for i in range(n + 1)]


def mirror_anim(layer, t, a):
    t0, t1, mk = a["t0"], a["t1"], a["mark"]
    lt, rt = t - t0, t1 - t
    S = SS
    out = 1 - eio((0.35 - rt) / 0.35) if rt < 0.35 else 1.0     # global exit
    if out <= 0: return
    mx, my = a.get("x", 735), a.get("cy", 190)                    # mirror centre (output px)
    rx, ry = 62, 86
    g = ImageDraw.Draw(layer)
    # glass (fades in after the frame starts drawing)
    ga = eo((lt - 0.25) / 0.4) * out
    if ga > 0.01:
        glass = Image.new("RGBA", (int(rx * 2 * S), int(ry * 2 * S)), (0, 0, 0, 0))
        gy = np.linspace(0, 1, glass.height)[:, None]
        col = (np.array([206, 218, 226]) * (1 - gy[..., None]) + np.array([240, 244, 247]) * gy[..., None]).repeat(glass.width, 1)
        glass = Image.fromarray(col.astype(np.uint8)).convert("RGBA")
        gd = ImageDraw.Draw(glass)
        # patient silhouette
        hx, hy = glass.width / 2, glass.height * 0.42
        sil = (170, 182, 191)
        gd.ellipse((hx - 22 * S, hy - 28 * S, hx + 22 * S, hy + 28 * S), fill=sil)
        gd.rounded_rectangle((hx - 52 * S, hy + 34 * S, hx + 52 * S, glass.height + 40 * S), radius=44 * S, fill=sil)
        # shine sweep (every 1.8 s)
        u = ((lt - 0.6) % 1.8) / 0.7
        if lt > 0.6 and u <= 1:
            sx = -glass.width * 0.6 + u * glass.width * 2.2
            sh = Image.new("L", glass.size, 0); sd = ImageDraw.Draw(sh)
            for i in range(-18, 19):
                sd.line([(sx + i * S + 60 * S, 0), (sx + i * S - 60 * S, glass.height)], fill=int(150 * (1 - abs(i) / 18)), width=S)
            wh = Image.new("RGBA", glass.size, (255, 255, 255, 0)); wh.putalpha(sh); glass.alpha_composite(wh)
        m = Image.new("L", glass.size, 0); ImageDraw.Draw(m).ellipse((0, 0, glass.width - 1, glass.height - 1), fill=int(255 * ga))
        glass.putalpha(m)
        layer.alpha_composite(glass, (int((mx - rx) * S), int((my - ry) * S)))
    # frame draws itself around the glass
    fp = eio(lt / 0.55)
    pts = _ellipse_pts(mx * S, my * S, (rx + 6) * S, (ry + 6) * S)
    n = max(2, int(len(pts) * fp))
    fa = int(255 * out)
    g.line(pts[:n], fill=DARK + (fa,), width=11 * S, joint="curve")
    g.line(pts[:n], fill=ACC + (fa,), width=5 * S, joint="curve")
    # little stand under the mirror
    if fp >= 1:
        sa = eo((lt - 0.55) / 0.25) * out
        g.line([(mx * S, (my + ry + 10) * S), (mx * S, (my + ry + 10 + 14 * sa) * S)], fill=DARK + (int(255 * out),), width=6 * S)
    # the one problem: marker on the face + leader line + annotation text
    if t >= mk:
        u = t - mk
        px, py = mx + 10, my - 18                       # on the silhouette's face
        p = eb(u / 0.35)
        r = 13 * p
        g.ellipse(((px - r) * S, (py - r) * S, (px + r) * S, (py + r) * S), outline=ACC + (fa,), width=4 * S)
        rr = 5 * p
        g.ellipse(((px - rr) * S, (py - rr) * S, (px + rr) * S, (py + rr) * S), fill=ACC + (fa,))
        q = (u % 1.1) / 1.1                               # pulse
        R = 13 + 26 * eo(q)
        g.ellipse(((px - R) * S, (py - R) * S, (px + R) * S, (py + R) * S), outline=ACC + (int(200 * (1 - q) * out),), width=2 * S)
        # leader: from the marker straight out to the left, then it becomes the gold underline of the text
        lp = eio((u - 0.10) / 0.30)
        x_tip = mx - rx - 40                                 # where the text's right edge sits
        if lp > 0:
            x_end = (px - 14) - ((px - 14) - x_tip) * lp
            g.line([((px - 14) * S, py * S), (x_end * S, py * S)], fill=DARK + (fa,), width=4 * S)
            g.ellipse(((x_end - 5) * S, (py - 5) * S, (x_end + 5) * S, (py + 5) * S), fill=DARK + (fa,))
        ta = a.get("text_at", mk + 0.35)
        tp = eo((t - ta) / 0.45)
        if tp > 0:
            im = reveal(txt(a["label"], 56, DARK + (255,)), tp)
            put(layer, im, x_tip * S - 10 * S - im.width, py * S - im.height + 4 * S, out)
            ul = eio((t - ta - 0.1) / 0.45)
            if ul > 0:
                xr = (x_tip - 10) * S; xl = xr - im.width * ul
                g.line([(xr, py * S), (xl, py * S)], fill=ACC + (fa,), width=6 * S)
