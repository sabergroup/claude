# One persistent container: appears once, morphs between contents, leaves only when nothing else is coming.
import math
import numpy as np
from PIL import Image, ImageDraw
import anim2 as A
from anim2 import SS, ACC, DARK, BODY, cl, eo, eb, eio, txt, text_w, icon, put, kinetic, PH, TS, ICD, envelope

RED = (176, 72, 62)
GOLD_FILL = ACC + (255,)
DARK_FILL = BODY + (230,)
MORPH = 0.38


# ---------------------------------------------------------------- content builders (return width, draw)
def icontext(ic, text, t_in, badge=None, strike=None, dark=False):
    bd = 70
    w = 30 + text_w(text, TS) + 22 + ICD + 13 + ((bd + 22) if badge else 0)
    col = (DARK + (255,)) if dark else (255, 255, 255, 255)

    def draw(cv, W_, H_, t):
        cy = H_ / 2
        name, ilt = ic, t - t_in
        if strike is not None and t >= strike + 0.25:
            name, ilt = "x", t - strike - 0.25
        d = ICD * (0.6 + 0.4 * eo((t - t_in) / 0.3))
        bg = RED if name == "x" else (DARK if dark else ACC)
        fg = (255, 255, 255) if name == "x" else (ACC if dark else DARK)
        im = icon(name, d, ilt, fg=fg, bg=bg)
        put(cv, im, W_ - (13 + ICD / 2) * SS - im.width / 2, cy - im.height / 2)
        right = W_ - (13 + ICD + 22) * SS
        kinetic(cv, text, TS, col, right, cy, t - t_in - 0.10)
        if strike is not None and t >= strike:
            p = eo((t - strike) / 0.3); tw = text_w(text, TS) * SS
            ImageDraw.Draw(cv).line([(right + 4 * SS, cy + 4 * SS), (right - (tw + 8 * SS) * p, cy + 4 * SS)], fill=ACC, width=5 * SS)
        if badge:
            n0, n1, roll_t = badge
            bx = (30 + bd / 2) * SS
            D = int(bd * SS)
            b = Image.new("RGBA", (D, D), (0, 0, 0, 0)); g = ImageDraw.Draw(b)
            g.ellipse((0, 0, D - 1, D - 1), fill=ACC)
            roll = eio((t - roll_t - 0.1) / 0.35) if t >= roll_t else 0.0
            dig = Image.new("RGBA", (D, D), (0, 0, 0, 0))
            for val, off in ((n0, -roll), (n1, 1 - roll)):
                ti = txt(str(val), 46, DARK + (255,))
                put(dig, ti, D / 2 - ti.width / 2, D / 2 - ti.height / 2 + 4 * SS + off * D * 0.8)
            m = Image.new("L", (D, D), 0); ImageDraw.Draw(m).ellipse((0, 0, D - 1, D - 1), fill=255)
            dig.putalpha(Image.fromarray(np.minimum(np.asarray(dig.getchannel("A")), np.asarray(m))))
            b.alpha_composite(dig)
            sc = eo((t - t_in) / 0.3)
            if sc < .99: b = b.resize((max(1, int(D * sc)), max(1, int(D * sc))), Image.BICUBIC)
            put(cv, b, bx - b.width / 2, cy - b.height / 2)
    return w, draw


def steps(l1, l2, m1, m2, t_in):
    dot, line, LS = 34, 120, 42
    w = 40 + text_w(l1, LS) + 18 + dot + 20 + line + 20 + dot + 18 + text_w(l2, LS) + 40

    def draw(cv, W_, H_, t):
        g = ImageDraw.Draw(cv); cy = H_ / 2
        x = W_ - 40 * SS
        kinetic(cv, l1, LS, (255, 255, 255, 255), x, cy, t - t_in - 0.1); x -= text_w(l1, LS) * SS + 18 * SS
        d1 = x - dot * SS / 2; x -= dot * SS + 20 * SS
        lx0 = x; x -= line * SS; lx1 = x; x -= 20 * SS
        d2 = x - dot * SS / 2; x -= dot * SS + 18 * SS
        kinetic(cv, l2, LS, (255, 255, 255, 255), x, cy, t - t_in - 0.3)
        g.line([(lx0, cy), (lx1, cy)], fill=(255, 255, 255, 70), width=4 * SS)
        fp = cl((t - m1) / (m2 - m1)) if t >= m1 else 0
        if fp > 0:
            xe = lx0 + (lx1 - lx0) * eio(fp)
            g.line([(lx0, cy), (xe, cy)], fill=ACC, width=4 * SS)
            if fp < 1:
                r = 7 * SS * (1 + .3 * math.sin(t * 20)); g.ellipse((xe - r, cy - r, xe + r, cy + r), fill=(255, 236, 200))
        for dc, mk in ((d1, m1), (d2, m2)):
            r = dot * SS / 2
            g.ellipse((dc - r, cy - r, dc + r, cy + r), outline=ACC, width=3 * SS)
            if t >= mk:
                rr = r * eb((t - mk) / 0.3)
                if rr > 1: g.ellipse((dc - rr, cy - rr, dc + rr, cy + rr), fill=ACC)
                ck = icon("check", dot, t - mk - .12, bg=(0, 0, 0, 0)); put(cv, ck, dc - ck.width / 2, cy - ck.height / 2)
    return w, draw


def pair(items):
    """items: [(icon, text, t_in)] laid out RTL inside one pill with a thin divider"""
    LS = 46
    parts = [ICD + 18 + text_w(tx, LS) for _, tx, _ in items]
    w = 26 + sum(parts) + 50 * (len(items) - 1) + 30

    def draw(cv, W_, H_, t):
        g = ImageDraw.Draw(cv); cy = H_ / 2
        x = W_ - 18 * SS
        for i, (ic, tx, t_in) in enumerate(items):
            if i > 0:
                g.line([(x - 25 * SS, cy - 24 * SS), (x - 25 * SS, cy + 24 * SS)], fill=(255, 255, 255, int(80 * eo((t - t_in) / 0.3))), width=2 * SS)
                x -= 50 * SS
            if t >= t_in:
                d = ICD * (0.6 + 0.4 * eo((t - t_in) / 0.3))
                im = icon(ic, d, t - t_in, fg=(255, 255, 255) if ic == "x" else DARK, bg=RED if ic == "x" else ACC)
                put(cv, im, x - ICD * SS / 2 - im.width / 2, cy - im.height / 2)
            kinetic(cv, tx, LS, (255, 255, 255, 255), x - (ICD + 18) * SS, cy, t - t_in - 0.1)
            x -= (ICD + 18 + text_w(tx, LS)) * SS
    return w, draw


def cta(text, t_in, tap, later=None):
    w1 = 30 + text_w(text, TS) + 22 + ICD + 13
    w = w1 + ((50 + ICD + 18 + text_w(later[1], 44) + 30) if later else 0)

    def draw(cv, W_, H_, t):
        g = ImageDraw.Draw(cv); cy = H_ / 2
        im = icon("calendar", ICD * (0.6 + 0.4 * eo((t - t_in) / 0.3)), t - t_in, fg=ACC, bg=DARK)
        put(cv, im, W_ - (13 + ICD / 2) * SS - im.width / 2, cy - im.height / 2)
        kinetic(cv, text, TS, DARK + (255,), W_ - (13 + ICD + 22) * SS, cy, t - t_in - 0.1)
        if tap <= t < tap + 0.6:
            u = (t - tap) / 0.6; R = (16 + 60 * eo(u)) * SS; px = W_ - w1 * SS * 0.45
            g.ellipse((px - R, cy - R, px + R, cy + R), outline=(255, 255, 255, int(230 * (1 - u))), width=4 * SS)
        if later:
            lt_, ltx, lic = later
            x = W_ - w1 * SS - 25 * SS
            g.line([(x, cy - 24 * SS), (x, cy + 24 * SS)], fill=DARK + (int(120 * eo((t - lt_) / 0.3)),), width=2 * SS)
            x -= 25 * SS
            if t >= lt_:
                im2 = icon(lic, ICD * (0.6 + 0.4 * eo((t - lt_) / 0.3)), t - lt_, fg=ACC, bg=DARK)
                put(cv, im2, x - ICD * SS / 2 - im2.width / 2, cy - im2.height / 2)
            kinetic(cv, ltx, 44, DARK + (255,), x - (ICD + 18) * SS, cy, t - lt_ - 0.1)
    return w, draw


# ---------------------------------------------------------------- the dock
def lerp_col(a, b, u): return tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(4))


def draw_dock(layer, t, chain):
    t0, t1, cy = chain["t0"], chain["t1"], chain["cy"]
    if not (t0 <= t < t1): return
    st = chain["states"]
    k = max(i for i, s in enumerate(st) if t >= s["t"])
    cur = st[k]; prev = st[k - 1] if k > 0 else None
    m = eo((t - cur["t"]) / MORPH) if prev else 1.0
    w = cur["w"] if not prev else prev["w"] + (cur["w"] - prev["w"]) * m
    fill = cur["fill"] if not prev else lerp_col(prev["fill"], cur["fill"], m)
    lt, ic, gr, tx = envelope(t, t0, t1)
    w = PH + (w - PH) * gr
    leave = 1 - eo((t - (t1 - 0.45)) / 0.22) if t > t1 - 0.45 else 1.0

    def content(cv, W_, H_):
        def layer_of(s, al):
            if al <= 0.01: return
            tmp = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
            s["draw"](tmp, W_, H_, t)
            put(cv, tmp, 0, 0, al * leave)
        if prev and not cur.get("cont"):
            layer_of(prev, 1 - eo((t - cur["t"]) / 0.18))
            layer_of(cur, eo((t - cur["t"] - 0.08) / 0.2))
        else:
            layer_of(cur, 1.0)
    A.draw_pill(layer, 540, cy, w, PH, fill, min(1, ic * 1.5), content)


def build(spec):
    """spec: {"t0","t1","states":[{"t", "kind", ...}]} -> chain with widths and draw fns"""
    states = []
    for s in spec["states"]:
        kind = s["kind"]
        if kind == "icontext":
            w, d = icontext(s["icon"], s["text"], s["t"], s.get("badge"), s.get("strike"))
        elif kind == "steps":
            w, d = steps(s["l1"], s["l2"], s["m1"], s["m2"], s["t"])
        elif kind == "pair":
            w, d = pair(s["items"])
        elif kind == "cta":
            w, d = cta(s["text"], s.get("t_in", s["t"]), s["tap"], s.get("later"))
        states.append({"t": s["t"], "w": w, "draw": d, "cont": s.get("cont", False),
                       "fill": GOLD_FILL if kind == "cta" else DARK_FILL, "text": s.get("text") or s.get("l1")})
    return {"t0": spec["t0"], "t1": spec["t1"], "cy": spec.get("cy", A.CY), "states": states}
