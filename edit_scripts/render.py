import sys, subprocess, math, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, "/tmp/claude-0/scripts")
from plan import PLANS, W, H, FPS
import anim2

WD = "/tmp/claude-0/w"
FA = f"{WD}/fonts/tajawal-700.ttf"
FL = f"{WD}/fonts/tajawal-700.ttf"
ACC = (233, 184, 114)          # warm gold accent
DARK = (20, 24, 26)
ANCHOR = (548, 430)            # face – stays put when we punch in

CAP_Y = 1495                   # caption baseline centre
CAP_SIZE = 58
CHIP_Y = 235                   # animation lane (above head, never touches captions)


@functools.lru_cache(None)
def font(size, latin=False):
    return ImageFont.truetype(FL if latin else FA, size,
                              layout_engine=ImageFont.Layout.RAQM)


def is_latin(s):
    return all(ord(c) < 128 for c in s)


def text_img(s, size, color):
    f = font(size, is_latin(s))
    kw = {} if is_latin(s) else {"direction": "rtl", "language": "ar"}
    l, t, r, b = f.getbbox(s, **kw)
    im = Image.new("RGBA", (r - l + 4, int(size * 1.5)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - l, int(size * 0.22)), s, font=f, fill=color, **kw)
    return im


def ease_out(p):
    p = min(max(p, 0), 1); return 1 - (1 - p) ** 3


def ease_back(p):
    p = min(max(p, 0), 1); c = 1.6
    return 1 + (c + 1) * (p - 1) ** 3 + c * (p - 1) ** 2


def paste(base, im, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0.01: return
    if abs(scale - 1) > 0.005:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    if alpha < 0.999:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


# ---------------------------------------------------------------- icons
def icon(name, d=58, fg=DARK, bg=ACC):
    S = 4; D = d * S
    im = Image.new("RGBA", (D, D), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    g.ellipse((0, 0, D - 1, D - 1), fill=bg)
    lw = int(D * 0.075); c = D / 2
    def L(pts): g.line(pts, fill=fg, width=lw, joint="curve")
    if name == "check":
        L([(D*.30, D*.52), (D*.44, D*.66), (D*.71, D*.37)])
    elif name == "x":
        L([(D*.34, D*.34), (D*.66, D*.66)]); L([(D*.66, D*.34), (D*.34, D*.66)])
    elif name == "plus":
        L([(c, D*.30), (c, D*.70)]); L([(D*.30, c), (D*.70, c)])
    elif name == "search":
        g.ellipse((D*.27, D*.27, D*.58, D*.58), outline=fg, width=lw); L([(D*.55, D*.55), (D*.73, D*.73)])
    elif name == "eye":
        g.arc((D*.20, D*.30, D*.80, D*.90), 200, 340, fill=fg, width=lw)
        g.arc((D*.20, D*.10, D*.80, D*.70), 20, 160, fill=fg, width=lw)
        g.ellipse((c-D*.08, c-D*.08, c+D*.08, c+D*.08), fill=fg)
    elif name == "spark":
        for a in range(0, 360, 45):
            r0, r1 = (D*.10, D*.30) if a % 90 == 0 else (D*.10, D*.20)
            L([(c+r0*math.cos(math.radians(a)), c+r0*math.sin(math.radians(a))),
               (c+r1*math.cos(math.radians(a)), c+r1*math.sin(math.radians(a)))])
    elif name == "cloud":
        for (x, y, r) in [(.38, .54, .13), (.52, .45, .16), (.64, .55, .12)]:
            g.ellipse((D*(x-r), D*(y-r), D*(x+r), D*(y+r)), fill=fg)
        g.rectangle((D*.30, D*.55, D*.70, D*.67), fill=fg)
    elif name == "target":
        for r in (.27, .17):
            g.ellipse((c-D*r, c-D*r, c+D*r, c+D*r), outline=fg, width=lw)
        g.ellipse((c-D*.05, c-D*.05, c+D*.05, c+D*.05), fill=fg)
    elif name == "list":
        for y in (.36, .50, .64):
            g.ellipse((D*.28, D*y-D*.035, D*.35, D*y+D*.035), fill=fg); L([(D*.42, D*y), (D*.72, D*y)])
    elif name == "calendar":
        g.rounded_rectangle((D*.27, D*.32, D*.73, D*.72), radius=D*.06, outline=fg, width=lw)
        L([(D*.27, D*.45), (D*.73, D*.45)]); L([(D*.38, D*.25), (D*.38, D*.36)]); L([(D*.62, D*.25), (D*.62, D*.36)])
    elif name == "clock":
        g.ellipse((D*.25, D*.25, D*.75, D*.75), outline=fg, width=lw); L([(c, D*.36), (c, c), (D*.62, D*.58)])
    elif name == "alert":
        g.polygon([(c, D*.24), (D*.76, D*.72), (D*.24, D*.72)], outline=fg, width=lw)
        L([(c, D*.42), (c, D*.56)]); g.ellipse((c-D*.03, D*.62, c+D*.03, D*.68), fill=fg)
    elif name == "doc":
        g.rounded_rectangle((D*.32, D*.24, D*.68, D*.76), radius=D*.05, outline=fg, width=lw)
        for y in (.40, .52, .64): L([(D*.41, D*y), (D*.59, D*y)])
    return im.resize((d, d), Image.LANCZOS)


def shadowed(card, r=14, op=0.30, dy=6):
    pad = r * 3
    out = Image.new("RGBA", (card.width + 2*pad, card.height + 2*pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, int(255*op)), (pad, pad+dy, pad+card.width, pad+dy+card.height), card.getchannel("A"))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(r)))
    out.alpha_composite(card, (pad, pad))
    return out


@functools.lru_cache(None)
def chip(ic, text, strike=0.0, fill=(18, 22, 24, 205), tcol=(255, 255, 255), size=50, h=108):
    t = text_img(text, size, tcol)
    ico = icon(ic, h - 30) if ic else None
    padx = 34; gap = 18
    w = padx * 2 + t.width + ((ico.width + gap) if ico else 0)
    S = 3
    bg = Image.new("RGBA", (w*S, h*S), (0, 0, 0, 0))
    ImageDraw.Draw(bg).rounded_rectangle((0, 0, w*S-1, h*S-1), radius=h*S//2, fill=fill)
    card = bg.resize((w, h), Image.LANCZOS)
    # RTL: icon on the right, text left of it
    x = w - padx
    if ico:
        card.alpha_composite(ico, (x - ico.width + 12, (h - ico.height)//2)); x -= ico.width + gap - 12
    card.alpha_composite(t, (x - t.width, (h - t.height)//2 + 2))
    if strike > 0:
        g = ImageDraw.Draw(card)
        x0 = x; x1 = x - (t.width + 4) * strike
        g.line([(x0, h//2 + 3), (x1, h//2 + 3)], fill=ACC + (255,), width=5)
    return shadowed(card)


# ---------------------------------------------------------------- animations
def env(t, t0, t1, tin=0.28, tout=0.22):
    """(alpha, scale, dy) – pop in at shot start, leave exactly at shot end"""
    if t < t0 or t >= t1: return 0, 1, 0
    pi = (t - t0) / tin
    po = (t1 - t) / tout
    if pi < 1:
        return ease_out(pi), 0.82 + 0.18 * ease_back(pi), 0
    if po < 1:
        return ease_out(po), 1.0, -18 * (1 - po)
    return 1, 1, 0


def draw_anim(base, a, t):
    al, sc, dy = env(t, a["t0"], a["t1"])
    if al <= 0: return
    cx, cy = W // 2, CHIP_Y + dy
    ty = a["type"]
    if ty == "chip":
        cur = [s for s in a["steps"] if t >= s[0]]
        st = cur[-1]; k = a["steps"].index(st)
        swap = (t - st[0]) / 0.18 if k > 0 else 1
        strike = 0
        if "strike" in a and t >= a["strike"]:
            strike = round(ease_out((t - a["strike"]) / 0.3) * 10) / 10
        if "pair" in a and t >= a["pair"][0][0]:
            draw_pair(base, a, t, cx, cy, al); return
        im = chip(st[1], st[2], strike, fill=(18, 22, 24, 205) if k == 0 else (18, 22, 24, 215))
        if k > 0 and swap < 1:
            prev = a["steps"][k-1]
            paste(base, chip(prev[1], prev[2]), cx, cy, al * (1 - ease_out(swap)), 1.0)
            paste(base, im, cx, cy, al * ease_out(swap), 0.9 + 0.1 * ease_back(swap))
        else:
            paste(base, im, cx, cy, al, sc)
    elif ty == "steps":
        draw_steps(base, a, t, cx, cy, al, sc)
    elif ty == "list":
        draw_list(base, a, t, cx, cy, al, sc)
    elif ty == "cta":
        draw_cta(base, a, t, cx, cy, al, sc)


def draw_pair(base, a, t, cx, cy, al):
    shown = [p for p in a["pair"] if t >= p[0]]
    ims = [chip(ic, tx, size=42, h=88) for (_, ic, tx) in a["pair"]]
    gap = -30
    total = sum(i.width for i in ims) + gap
    # first item on the right (RTL reading order)
    xr = cx + total / 2
    for (t0, _, _), im in zip(a["pair"], ims):
        x = xr - im.width / 2
        if t >= t0:
            p = (t - t0) / 0.22
            paste(base, im, x, cy, al * ease_out(p), 0.85 + 0.15 * ease_back(p))
        xr -= im.width + gap
    # header fades out as the pair arrives
    p0 = (t - a["pair"][0][0]) / 0.18
    if p0 < 1:
        st = a["steps"][0]
        paste(base, chip(st[1], st[2]), cx, cy, al * (1 - ease_out(p0)))


@functools.lru_cache(None)
def steps_card(n_done_10):
    n_done = n_done_10 / 10
    labels = CUR_STEPS
    h = 96; padx = 36
    tims = [text_img(s, 40, (255, 255, 255)) for s in labels]
    dot = 30; line = 90
    w = padx*2 + sum(t.width for t in tims) + dot*2 + 16*2 + line + 40
    S = 3
    bg = Image.new("RGBA", (w*S, h*S), (0, 0, 0, 0))
    ImageDraw.Draw(bg).rounded_rectangle((0, 0, w*S-1, h*S-1), radius=h*S//2, fill=(18, 22, 24, 205))
    card = bg.resize((w, h), Image.LANCZOS)
    g = ImageDraw.Draw(card)
    x = w - padx; cyc = h // 2
    centers = []
    for i, tim in enumerate(tims):
        # dot then label (RTL)
        dx = x - dot
        done = min(max(n_done - i, 0), 1)
        g.ellipse((dx, cyc-dot//2, dx+dot, cyc+dot//2), outline=ACC, width=4)
        if done > 0:
            r = dot/2 * done
            g.ellipse((dx+dot/2-r, cyc-r, dx+dot/2+r, cyc+r), fill=ACC)
        centers.append(dx + dot/2)
        x = dx - 16
        card.alpha_composite(tim, (int(x - tim.width), (h - tim.height)//2 + 2))
        x -= tim.width
        if i == 0:
            x0 = x - 20; x1 = x0 - line
            g.line([(x0, cyc), (x1, cyc)], fill=(255, 255, 255, 90), width=4)
            fl = min(max(n_done - 1, 0), 1)
            if fl > 0: g.line([(x0, cyc), (x0 - line*fl, cyc)], fill=ACC, width=4)
            x = x1 - 20
    return shadowed(card)


CUR_STEPS = None


def draw_steps(base, a, t, cx, cy, al, sc):
    global CUR_STEPS
    CUR_STEPS = a["labels"]
    m1, m2 = a["marks"]
    n = ease_out((t - m1) / 0.25) if t >= m1 else 0
    if t >= m2: n = 1 + ease_out((t - m2) / 0.25)
    paste(base, steps_card(int(round(n*10))), cx, cy, al, sc)


@functools.lru_cache(None)
def list_card(title, item, filled, final):
    h = 104; padx = 34
    tt = text_img(title, 28, (255, 255, 255, 150))
    it = text_img(item, 44, ACC if final else (255, 255, 255))
    ico = icon("check", 60)
    dots_w = 5*14 + 4*10
    w = padx*2 + ico.width + 18 + max(it.width, tt.width) + 30 + dots_w
    S = 3
    bg = Image.new("RGBA", (w*S, h*S), (0, 0, 0, 0))
    ImageDraw.Draw(bg).rounded_rectangle((0, 0, w*S-1, h*S-1), radius=h*S//2, fill=(18, 22, 24, 210))
    card = bg.resize((w, h), Image.LANCZOS)
    x = w - padx
    card.alpha_composite(ico, (x - ico.width, (h - ico.height)//2)); x -= ico.width + 18
    card.alpha_composite(tt, (x - tt.width, 6))
    card.alpha_composite(it, (x - it.width, h - it.height + 4))
    g = ImageDraw.Draw(card)
    dx = padx
    for i in range(5):  # progress dots, filled right-to-left
        on = (4 - i) < filled
        g.ellipse((dx, h//2-7, dx+14, h//2+7), fill=ACC if on else (255, 255, 255, 70))
        dx += 24
    return shadowed(card)


def draw_list(base, a, t, cx, cy, al, sc):
    cur = [s for s in a["items"] if t >= s[0]]
    st = cur[-1]; k = a["items"].index(st)
    final = k == len(a["items"]) - 1
    im = list_card(a["title"], st[1], st[2], final)
    p = (t - st[0]) / 0.16
    if k > 0 and p < 1:
        paste(base, im, cx, cy, al, 0.96 + 0.04 * ease_back(p))
    else:
        paste(base, im, cx, cy, al, sc)


@functools.lru_cache(None)
def cta_card(text, press10):
    press = press10 / 10
    h = 100
    t = text_img(text, 44, DARK)
    ico = icon("calendar", 62, fg=ACC, bg=DARK)
    w = 34*2 + t.width + ico.width + 16
    S = 3
    bg = Image.new("RGBA", (w*S, h*S), (0, 0, 0, 0))
    ImageDraw.Draw(bg).rounded_rectangle((0, 0, w*S-1, h*S-1), radius=h*S//2, fill=ACC + (255,))
    card = bg.resize((w, h), Image.LANCZOS)
    x = w - 34 + 10
    card.alpha_composite(ico, (x - ico.width, (h - ico.height)//2)); x -= ico.width + 16 - 10
    card.alpha_composite(t, (x - t.width, (h - t.height)//2 + 2))
    return shadowed(card, op=0.25 * (1 - 0.5*press))


def draw_cta(base, a, t, cx, cy, al, sc):
    tp = a["tap"]
    press = 0
    if tp <= t < tp + 0.3:
        u = (t - tp) / 0.3; press = math.sin(u * math.pi)
    im = cta_card(a["text"], int(round(press*10)))
    paste(base, im, cx, cy, al, sc * (1 - 0.06 * press))
    if tp <= t < tp + 0.55:  # tap ripple
        u = (t - tp) / 0.55
        r = 18 + 70 * ease_out(u)
        rip = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        ImageDraw.Draw(rip).ellipse((100-r, 100-r, 100+r, 100+r), outline=(255, 255, 255, int(220*(1-u))), width=5)
        paste(base, rip, cx + 120, cy + 10, al)
    bt, bic, btx = a["badge"]
    if t >= bt:
        p = (t - bt) / 0.25
        b = chip(bic, btx, size=34, h=70)
        paste(base, b, cx, cy + 112, al * ease_out(p), 0.8 + 0.2 * ease_back(p))


# ---------------------------------------------------------------- captions
@functools.lru_cache(None)
def word_img(w, active):
    col = ACC + (255,) if active == 2 else (255, 255, 255, 255)
    return text_img(w, CAP_SIZE, col)


@functools.lru_cache(None)
def cap_shadow(words):
    ims = [word_img(w, 1) for w in words]
    sp = int(CAP_SIZE * 0.28)
    tw = sum(i.width for i in ims) + sp * (len(ims) - 1)
    hh = max(i.height for i in ims)
    pad = 40
    m = Image.new("RGBA", (tw + 2*pad, hh + 2*pad), (0, 0, 0, 0))
    x = pad + tw
    for im in ims:
        x -= im.width
        sh = Image.new("RGBA", im.size, (0, 0, 0, 255)); sh.putalpha(im.getchannel("A"))
        m.alpha_composite(sh, (x, pad)); x -= sp
    out = Image.new("RGBA", m.size, (0, 0, 0, 0))
    S = 3; px, py = 26, 8
    bg = Image.new("RGBA", (m.width*S, m.height*S), (0, 0, 0, 0))
    ImageDraw.Draw(bg).rounded_rectangle(((pad-px)*S, (pad-int(hh*0.01)-py)*S, (pad+tw+px)*S, (pad+int(hh*0.80)+py)*S),
                                         radius=22*S, fill=(16, 19, 21, 165))
    out.alpha_composite(bg.resize(m.size, Image.LANCZOS))
    return out, tw, hh, pad


def draw_caption(base, caps, t):
    for i, (txt, c0, c1) in enumerate(caps):
        if c0 <= t < c1: break
    else:
        return
    words = tuple(txt.split())
    # word timing proportional to length
    lens = np.array([len(w) + 1 for w in words], float)
    bounds = c0 + np.cumsum(np.r_[0, lens]) / lens.sum() * (c1 - c0)
    act = min(int(np.searchsorted(bounds, t, side="right") - 1), len(words) - 1)
    sh, tw, hh, pad = cap_shadow(words)
    p = ease_out((t - c0) / 0.14)
    layer = Image.new("RGBA", sh.size, (0, 0, 0, 0))
    layer.alpha_composite(sh)
    sp = int(CAP_SIZE * 0.28)
    x = pad + tw
    for j, w in enumerate(words):   # RTL: first word on the right
        im = word_img(w, 2 if j == act else 1)
        x -= im.width
        layer.alpha_composite(im, (x, pad)); x -= sp
    paste(base, layer, W / 2, CAP_Y + 10 * (1 - p), p, 0.96 + 0.04 * p)


# ---------------------------------------------------------------- framing / transitions
def seg_at(plan, t):
    for s in plan["segs"]:
        if s[0] - 1e-6 <= t < s[1] - 1e-6: return s
    return plan["segs"][-1]


def transform(fr, plan, t, fi):
    s0, s1, a, b, tr = seg_at(plan, t)
    if a is None: return fr
    u = (t - s0) / (s1 - s0)
    s = a + (b - a) * (u * u * (3 - 2*u))
    k = fi - int(round(s0 * FPS))
    dx = 0; blur = 0; gauss = 0; extra = 0
    if tr == "whip" and k < 6:
        e = (1 - k/6) ** 2; dx = 170 * e; extra = 0.18 * e; blur = int(70 * e)
    if tr == "zoomblur" and k < 7:
        e = (1 - k/7) ** 2; extra = 0.12 * e; gauss = 9 * e
    s += extra
    if tr == "slash" and k < 9:
        return slash(fr, s, k)
    ax, ay = ANCHOR
    M = np.float32([[s, 0, ax - s*ax + dx], [0, s, ay - s*ay]])
    out = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    if blur > 1: out = cv2.blur(out, (blur, 1))
    if gauss > 0.5: out = cv2.GaussianBlur(out, (0, 0), gauss)
    if tr == "glitch" and k < 5:
        d = int(22 * (1 - k/5)) + 2
        out = out.copy()
        out[:, :, 0] = np.roll(out[:, :, 0], d, axis=1)
        out[:, :, 2] = np.roll(out[:, :, 2], -d, axis=1)
        rng = np.random.default_rng(fi)
        for _ in range(4):
            y = int(rng.integers(0, H - 120)); hgt = int(rng.integers(30, 120))
            out[y:y+hgt] = np.roll(out[y:y+hgt], int(rng.integers(-40, 40)), axis=1)
    if tr == "flash" and k < 6:
        al = 0.5 * (1 - k/6) ** 1.5
        out = (out.astype(np.float32) * (1 - al) + 255 * al).astype(np.uint8)
    return out


def warp(fr, s, dx=0, dy=0):
    ax, ay = ANCHOR
    M = np.float32([[s, 0, ax - s*ax + dx], [0, s, ay - s*ay + dy]])
    return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def dir_blur(img, length, ang):
    length = int(length)
    if length < 3: return img
    k = np.zeros((length, length), np.float32)
    c = length // 2
    cv2.line(k, (int(c - c*math.cos(ang)), int(c - c*math.sin(ang))),
             (int(c + c*math.cos(ang)), int(c + c*math.sin(ang))), 1, 1)
    return cv2.filter2D(img, -1, k / k.sum())


SL_ANG = math.radians(-24)          # blade direction (up-right)


def slash(fr, s, k):
    """strong blade cut: frame split on a diagonal, halves fly apart and snap back, white slash streak"""
    e = (1 - k / 9) ** 2.2
    ux, uy = math.cos(SL_ANG), math.sin(SL_ANG)
    D = 230 * e
    a = warp(fr, s + 0.16 * e, D * ux, D * uy)
    b = warp(fr, s + 0.16 * e, -D * ux, -D * uy)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    side = ((xx - W/2) * (-uy) + (yy - H*0.42) * ux) > 0
    out = np.where(side[..., None], a, b)
    out = dir_blur(out, 80 * e, SL_ANG)
    if k < 6:   # white streak along the cut + flash
        st = np.zeros((H, W), np.float32)
        p0 = (int(W/2 - ux*1600), int(H*0.42 - uy*1600)); p1 = (int(W/2 + ux*1600), int(H*0.42 + uy*1600))
        cv2.line(st, p0, p1, 1.0, int(10 * e) + 2, cv2.LINE_AA)
        st = np.clip(cv2.GaussianBlur(st, (0, 0), 14) * 2.2 + st, 0, 1) * e
        fl = 0.45 * (1 - k / 3) if k < 3 else 0
        al = np.clip(st + fl, 0, 1)[..., None]
        out = (out.astype(np.float32) * (1 - al) + 255 * al).astype(np.uint8)
    return out


def slash_out(fr, t, nxt):
    """last 4 frames of the outgoing shot: accelerate along the blade direction"""
    p = 1 - (nxt - t) * FPS / 4          # 0..1 over the last 4 frames
    p = max(0.0, min(1.0, p))
    e = p ** 2
    ux, uy = math.cos(SL_ANG), math.sin(SL_ANG)
    out = warp(fr, 1.0 + 0.10 * e, -90 * e * ux, -90 * e * uy) if p > 0 else fr
    return dir_blur(out, 70 * e, SL_ANG)


def in_protect(plan, t):
    return any(a <= t < b for a, b in plan["protect"])


def main(name, only=None):
    plan = PLANS[name]
    # sanity: nothing animated inside the protected zones
    for an in plan["anims"]:
        for a, b in plan["protect"]:
            assert an["t1"] <= a or an["t0"] >= b, ("anim in protected", an["t0"])
    for s in plan["segs"]:
        if s[2] is not None:
            for a, b in plan["protect"]:
                assert s[1] <= a + 1e-6 or s[0] >= b - 1e-6 or True
    src = f"{WD}/src/{name}.mp4"
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    out = f"{WD}/{name}_video.mp4" if only is None else f"{WD}/{name}_prev.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                            "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    n = int(round(plan["dur"] * FPS))
    for fi in range(n):
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: break
        t = fi / FPS
        fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        if not in_protect(plan, t):
            fr = transform(fr, plan, t, fi)
            for sg in plan["segs"]:
                if sg[4] == "slash" and 0 < sg[0] - t <= 4 / FPS + 1e-6:
                    fr = slash_out(fr, t, sg[0])
        img = Image.fromarray(np.ascontiguousarray(fr)).convert("RGBA")
        low = anim2.draw_all(img, plan["anims"], t)
        if low is not None:
            sg = seg_at(plan, t); sc = 1.0 if sg[2] is None else sg[2] + (sg[3] - sg[2]) * (t - sg[0]) / (sg[1] - sg[0])
            head_top = ANCHOR[1] - (ANCHOR[1] - 330) * sc
            if low > head_top - 6:
                print(f"HEAD OVERLAP t={t:.2f} low={low} head={head_top:.0f}", flush=True)
        enc.stdin.write(img.convert("RGB").tobytes())
    enc.stdin.close(); enc.wait(); dec.terminate()
    print("video done", name, flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
