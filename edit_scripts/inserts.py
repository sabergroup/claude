# Full-screen motion-graphics inserts (doctor stays in a small live circle).
import math, functools
import numpy as np, cv2
from PIL import Image, ImageDraw
import anim2 as A
from anim2 import SS, ACC, DARK, BODY, cl, eo, eb, ei, eio

W, H = 1080, 1920
BG_TOP, BG_BOT = np.array([246, 241, 234]), np.array([234, 225, 212])


@functools.lru_cache(None)
def background():
    g = np.linspace(0, 1, H)[:, None, None]
    bg = (BG_TOP * (1 - g) + BG_BOT * g).repeat(W, 1).astype(np.uint8)
    return bg


@functools.lru_cache(None)
def dots_tile():
    T = 60 * SS
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((T/2 - 3*SS, T/2 - 3*SS, T/2 + 3*SS, T/2 + 3*SS), fill=(40, 40, 40, 22))
    return im


@functools.lru_cache(None)
def dots_big():
    T = 60 * SS; tile = dots_tile()
    big = Image.new("RGBA", (W * SS + T, H * SS + T), (0, 0, 0, 0))
    for y in range(0, big.height, T):
        for x in range(0, big.width, T):
            big.alpha_composite(tile, (x, y))
    return big


def draw_dots(layer, t):
    T = 60 * SS; off = int((t * 18 * SS) % T)
    layer.alpha_composite(dots_big().crop((T - off, T - off, T - off + W * SS, T - off + H * SS)))


def title(layer, s, t, lin, y=360, size=74, col=DARK + (255,)):
    w = A.text_w(s, size) * SS
    A.kinetic(layer, s, size, col, W * SS / 2 + w / 2, y * SS, lin)


def pip(frame_rgb, lt):
    """live doctor circle, bottom-right"""
    d = 260
    p = eb(lt / 0.35)
    if p <= 0.02: return None
    crop = frame_rgb[430 - 300:430 + 260, 548 - 280:548 + 280]
    crop = cv2.resize(crop, (d * SS, d * SS), interpolation=cv2.INTER_AREA)
    im = Image.fromarray(crop).convert("RGBA")
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).ellipse((0, 0, im.width - 1, im.height - 1), fill=255)
    im.putalpha(m)
    ring = Image.new("RGBA", ((d + 20) * SS, (d + 20) * SS), (0, 0, 0, 0)); g = ImageDraw.Draw(ring)
    g.ellipse((0, 0, ring.width - 1, ring.height - 1), outline=ACC, width=5 * SS)
    a0 = (lt * 90) % 360
    g.arc((0, 0, ring.width - 1, ring.height - 1), a0, a0 + 60, fill=BODY, width=5 * SS)
    ring.alpha_composite(im, (10 * SS, 10 * SS))
    sc = max(0.01, p)
    ring = ring.resize((max(1, int(ring.width * sc)), max(1, int(ring.height * sc))), Image.BICUBIC)
    return ring


def iris(base_rgb, ins_rgb, lt):
    """circular reveal of the insert over the talking-head frame (first 0.32 s)"""
    p = eio(lt / 0.32)
    if p >= 1: return ins_rgb
    R = int(p * 1150)
    m = np.zeros((H, W), np.uint8); cv2.circle(m, (540, 960), max(R, 1), 255, -1, cv2.LINE_AA)
    m = m[..., None].astype(np.float32) / 255
    out = (ins_rgb * m + base_rgb * (1 - m)).astype(np.uint8)
    if R > 0:
        cv2.circle(out, (540, 960), R, ACC, 10, cv2.LINE_AA)
    return out


# ------------------------------------------------------------------ insert scenes
def mirror_scene(layer, t, a):
    lt = t - a["t0"]
    title(layer, a["title"], t, lt - 0.15)
    cx, cy = 540, 1000 + (1 - eb(lt / 0.5)) * 90 + 6 * math.sin(lt * 2.2)
    al = eo(lt / 0.35)
    mw, mh = 500, 700
    S = SS
    # frame
    fr = Image.new("RGBA", ((mw + 40) * S, (mh + 40) * S), (0, 0, 0, 0)); g = ImageDraw.Draw(fr)
    g.rounded_rectangle((0, 0, fr.width - 1, fr.height - 1), radius=(mw + 40) * S // 2, fill=ACC + (255,))
    inner = Image.new("RGBA", (mw * S, mh * S), (0, 0, 0, 0))
    gy = np.linspace(0, 1, mh * S)[:, None]
    grad = (np.array([214, 224, 230]) * (1 - gy[..., None]) + np.array([243, 246, 248]) * gy[..., None]).repeat(mw * S, 1)
    inner = Image.fromarray(grad.astype(np.uint8)).convert("RGBA")
    gi = ImageDraw.Draw(inner)
    # patient silhouette (opaque)
    hx, hy = mw * S / 2, mh * S * 0.40
    gi.ellipse((hx - 85*S, hy - 105*S, hx + 85*S, hy + 105*S), fill=(178, 189, 197))
    gi.rounded_rectangle((hx - 200*S, hy + 120*S, hx + 200*S, mh*S + 200*S), radius=170*S, fill=(178, 189, 197))
    # moving shine
    ph = ((lt % 2.0) / 2.0)
    sx = -mw*S*0.5 + ph * mw*S*2
    shine = Image.new("L", inner.size, 0); sd = ImageDraw.Draw(shine)
    for i in range(-40, 41):
        sd.line([(sx + i*S + 300*S, 0), (sx + i*S - 300*S, mh*S)], fill=int(120 * (1 - abs(i)/40)), width=S)
    wh = Image.new("RGBA", inner.size, (255, 255, 255, 0)); wh.putalpha(shine); inner.alpha_composite(wh)
    # problem marker
    mk = a["mark"]
    mo = Image.new("RGBA", inner.size, (0, 0, 0, 0)); gi = ImageDraw.Draw(mo)
    if t >= mk:
        u = t - mk; p = eb(u / 0.35)
        mx, my = hx + 60*S, hy + 10*S
        r = 48*S*p
        gi.ellipse((mx - r, my - r, mx + r, my + r), outline=ACC + (255,), width=9*S)
        rr = 14*S*p; gi.ellipse((mx - rr, my - rr, mx + rr, my + rr), fill=ACC)
        q = (u % 1.0)
        R = 48*S + 80*S*eo(q)
        gi.ellipse((mx - R, my - R, mx + R, my + R), outline=ACC + (int(220*(1-q)),), width=5*S)
    inner.alpha_composite(mo)
    mask = Image.new("L", inner.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, inner.width - 1, inner.height - 1), radius=mw*S//2, fill=255)
    inner.putalpha(mask)
    fr.alpha_composite(inner, (20*S, 20*S))
    A.put(layer, fr, cx*S - fr.width/2, cy*S - fr.height/2, al)
    if t >= mk:
        A.text_pill(layer, t, mk, a["t1"] + 10, [(mk, "eye", a["label"])], cy=1470)


def options_scene(layer, t, a):
    lt = t - a["t0"]
    title(layer, a["title"], t, lt - 0.15)
    ok_t, no_t = a["ok"], a["no"]
    pos = [(780, 860), (300, 860), (780, 1200), (300, 1200)]   # RTL: right column first
    good = {0, 2}
    icons = ["target", "spark", "plus", "doc"]
    cw, ch = 400, 290
    for i, (x, y) in enumerate(pos):
        p = eb((lt - 0.15 - i * 0.09) / 0.45)
        if p <= 0.01: continue
        bob = 7 * math.sin(lt * 2.3 + i * 1.3)
        sc = p; al = 1.0; fill = BODY + (240,)
        is_good = i in good
        if is_good and t >= ok_t:
            u = eo((t - ok_t) / 0.3); fill = tuple(int(BODY[k] * (1 - u * .2) + ACC[k] * u * .2) for k in range(3)) + (245,)
        if not is_good and t >= no_t:
            u = eo((t - no_t) / 0.35); al = 1 - 0.6 * u; sc *= 1 - 0.08 * u
        card = Image.new("RGBA", (cw * SS, ch * SS), (0, 0, 0, 0)); g = ImageDraw.Draw(card)
        g.rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=44 * SS, fill=fill)
        if is_good and t >= ok_t:
            u = eo((t - ok_t) / 0.3)
            g.rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=44 * SS, outline=ACC + (int(255*u),), width=6 * SS)
        ic = A.icon(icons[i], 120, lt + i)
        card.alpha_composite(ic, (card.width // 2 - ic.width // 2, card.height // 2 - ic.height // 2))
        if is_good and t >= ok_t:
            st = A.icon("check", 84 * eb((t - ok_t) / 0.3) + 1, t - ok_t, fg=DARK, bg=ACC)
            card.alpha_composite(st, (card.width - st.width - 18 * SS, 18 * SS))
        if not is_good and t >= no_t:
            st = A.icon("x", 84 * eb((t - no_t) / 0.3) + 1, t - no_t, fg=(255, 255, 255), bg=(150, 60, 55))
            card.alpha_composite(st, (card.width - st.width - 18 * SS, 18 * SS))
        if abs(sc - 1) > .01:
            card = card.resize((max(1, int(card.width * sc)), max(1, int(card.height * sc))), Image.BICUBIC)
        A.put(layer, card, x * SS - card.width / 2, (y + bob) * SS - card.height / 2, al)
    gap = 24
    if t >= ok_t:
        w1 = 30 + A.text_w(a["ok_label"], 46) + 22 + 74 + 13
        w2 = 30 + A.text_w(a["no_label"], 46) + 22 + 74 + 13
        p = eo((t - no_t) / 0.45) if t >= no_t else 0
        A.text_pill(layer, t, ok_t, a["t1"] + 10, [(ok_t, "check", a["ok_label"])], cx=540 + (w2 + gap) / 2 * p, cy=1500)
        if t >= no_t:
            A.text_pill(layer, t, no_t, a["t1"] + 10, [(no_t, "x", a["no_label"])], cx=540 - (w1 + gap) / 2 * p, cy=1500)


def implant_scene(layer, t, a):
    lt = t - a["t0"]
    title(layer, a["title"], t, lt - 0.1)
    cy0 = 1010 + (1 - eb(lt / 0.5)) * 110
    al = eo(lt / 0.3)
    cw, chh = 900, 960
    card = Image.new("RGBA", (cw * SS, chh * SS), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=56 * SS, fill=BODY + (255,))
    ov = Image.new("RGBA", card.size, (0, 0, 0, 0)); g = ImageDraw.Draw(ov)
    # implant (silicone dome) with moving highlight
    ix, iy = cw * SS / 2, 170 * SS
    pul = 1 + 0.03 * math.sin(lt * 4)
    rw, rh = 170 * SS * pul, 95 * SS * pul
    g.ellipse((ix - rw, iy - rh, ix + rw, iy + rh), fill=(236, 214, 178))
    g.ellipse((ix - rw * .8, iy - rh * .55, ix + rw * .8, iy + rh * .75), fill=(242, 225, 195))
    hx = ix - rw * .5 + rw * 1.0 * ((math.sin(lt * 1.8) + 1) / 2)
    g.ellipse((hx - 40 * SS, iy - rh * .7, hx + 30 * SS, iy - rh * .35), fill=(255, 250, 240))
    g.ellipse((ix - rw, iy - rh, ix + rw, iy + rh), outline=ACC, width=4 * SS)
    # rows
    rows = a["rows"]
    y = 330 * SS
    for i, (rt, label) in enumerate(rows):
        rp = eb((lt - 0.2 - i * 0.07) / 0.4)
        if rp <= 0.01: y += 118 * SS; continue
        on = t >= rt
        cxr = cw * SS - 70 * SS
        # active highlight bar slides in
        if on:
            u = eo((t - rt) / 0.3)
            g.rounded_rectangle((40 * SS, y - 46 * SS, 40 * SS + (cw - 80) * SS * u, y + 46 * SS), radius=30 * SS,
                                fill=(255, 255, 255, 18))
        card.alpha_composite(ov); ov = Image.new("RGBA", card.size, (0, 0, 0, 0)); g = ImageDraw.Draw(ov)
        # check circle
        r = 26 * SS
        g.ellipse((cxr - r, y - r, cxr + r, y + r), outline=ACC + (int(255 * rp),), width=4 * SS)
        if on:
            ck = A.icon("check", 52, t - rt, fg=DARK, bg=ACC)
            card.alpha_composite(ck, (int(cxr - ck.width / 2), int(y - ck.height / 2)))
        A.kinetic(card, label, 42, (255, 255, 255, 255), cxr - 50 * SS, y, lt - 0.25 - i * 0.07)
        # value field: dashed until filled, then "types" in
        fx0, fx1 = 70 * SS, 420 * SS
        if not on:
            for k in range(10):
                xx = fx0 + k * (fx1 - fx0) / 10
                g.line([(xx, y + 14 * SS), (xx + 14 * SS, y + 14 * SS)], fill=(255, 255, 255, int(70 * rp)), width=3 * SS)
        else:
            u = cl((t - rt) / 0.5)
            n = int(9 * u)
            for k in range(n):
                xx = fx0 + k * 38 * SS
                hh = 14 * SS
                g.rounded_rectangle((xx, y - hh, xx + 28 * SS, y + hh), radius=6 * SS, fill=ACC + (230,))
            if u < 1 and int(t * 8) % 2 == 0:
                xx = fx0 + n * 38 * SS
                g.line([(xx, y - 20 * SS), (xx, y + 20 * SS)], fill=ACC, width=3 * SS)
        card.alpha_composite(ov); ov = Image.new("RGBA", card.size, (0, 0, 0, 0)); g = ImageDraw.Draw(ov)
        y += 118 * SS
    card.alpha_composite(ov)
    A.put(layer, card, 540 * SS - card.width / 2, cy0 * SS - card.height / 2, al)


SCENES = {"mirror": mirror_scene, "options": options_scene, "implant": implant_scene}


def render(base_rgb, src_rgb, a, t):
    """base_rgb: talking-head frame (for the reveal); src_rgb: untouched source (for the live circle)"""
    lt = t - a["t0"]
    layer = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    draw_dots(layer, t)
    SCENES[a["scene"]](layer, t, a)
    small = layer.resize((W, H), Image.LANCZOS)
    bg = Image.fromarray(background()).convert("RGBA")
    bg.alpha_composite(small)
    ins = np.asarray(bg.convert("RGB"))
    return iris(base_rgb, ins, lt)
