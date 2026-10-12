# التصبغات – captions, shot-locked animations, cut transitions, sfx from the user's folder only.
# Rules: every animation enters on the first frame of its shot and finishes leaving on the cut;
# transitions only on real cuts; the speaker is never covered (cards sit above the head in wide
# shots, over the shins in medium shots) and captions keep their own lane below the cards.
import sys, json, math, functools, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WD = "/tmp/claude-0/w"
W, H, FPS = 1080, 1920, 25
DUR = 52.76
SR = 48000
ACC = (233, 184, 114)
DARK = (20, 24, 26)
GLASS = (18, 22, 24, 205)
F_B = f"{WD}/fonts/tajawal-700.ttf"
F_XB = f"{WD}/fonts/tajawal-800.ttf"

# ------------------------------------------------------------------ edit decision list
# real cuts in the source (first frame of the new shot) + the user's own zooms (left untouched)
SHOTS = [  # (start, end, framing)
    (0.00, 3.64, "W"), (3.64, 6.80, "M"), (6.80, 11.52, "W"), (11.52, 15.40, "M"),
    (15.40, 18.10, "W"), (18.10, 18.28, "Z"), (18.28, 20.60, "C"), (20.60, 27.32, "W"),
    (27.32, 32.12, "M"), (32.12, 35.84, "W"), (35.84, 36.00, "Z"), (36.00, 36.96, "C"),
    (36.96, 40.40, "W"), (40.40, 44.04, "M"), (44.04, 48.20, "W"), (48.20, 52.76, "M"),
]
USER_ZOOMS = [(18.10, 18.28), (35.84, 36.00)]
TRANSITIONS = [3.64, 11.52, 20.60, 27.32, 40.40, 48.20]   # soft zoom-blur in, only on hard cuts
DRIFT = 0.035                                             # slow push-in on wide shots
FACE_W = (540, 540)

TOP_Y, LOW_Y = 222, 1372      # card lanes
CAP_Y, CAP_SIZE = 1650, 64    # caption lane

# ------------------------------------------------------------------ captions
FIX = {"أن": "إن", "تاني": "تانية", "أثار": "آثار", "حب": "حب", "شباب": "الشباب", "وأحياناً": "وأحيانًا",
       "التأشير": "التقشير", "الدرما": "الديرمابن", "بين": "", "الحال": "الحالة",
       "وطبعاً": "وطبعًا", "واقع": "واقي", "نقل": "نقلل", "الفرص": "فرص", "ربوع": "رجوع",
       "أنك": "إنك", "تاني؟": "تاني؟"}
GROUPS = [
    "بتعالجي التصبغات", "وتختفي", "وبعد فترة", "بترجع تاني؟",
    "مهم تعرفي", "إن التصبغات", "مش بس سببها", "الشمس",
    "لكن ممكن تكون", "نتيجة آثار التهابات", "أو حب الشباب", "أو تغيرات هرمونية",
    "وأحيانًا بتكون", "نتيجة استخدامك لمنتجات", "مش مناسبة لبشرتك",
    "بدون ما ترجعي", "لطبيب الجلدية", "علشان كده", "أول خطوة", "في العلاج", "هي التشخيص",
    "نفحص الجلد", "ونشوف التصبغات", "ونحدد نوعها", "وسبب ظهورها", "ونختار مع بعض", "العلاج المناسب ليه",
    "سواء هنكتفي", "بكريمات التفتيح", "الموضعية", "أو هنحدد", "الجلسة المناسبة",
    "زي التقشير", "أو الديرمابن", "أو أنواع الليزر", "المختلفة", "حسب الحالة",
    "وطبعًا واقي الشمس", "شيء أساسي", "مش بس", "أثناء العلاج",
    "لكن كمان", "علشان نقلل", "فرص رجوع", "التصبغات مرة تانية",
    "والمهم إنك", "ما تستعجليش النتيجة", "باستخدام كذا منتج", "مختلف",
    "ابدأي بتشخيص صح", "علشان نختار", "العلاج المناسب", "لبشرتك",
]
CUTS = sorted({s for s, _, _ in SHOTS} | {DUR})


def build_captions():
    raw = json.load(open(f"{WD}/pigment_words.json"))
    words = []
    for s, e, w in raw:
        w = FIX.get(w, w)
        if w == "":
            words[-1][1] = e; continue
        words.append([s, e, w])
    caps, i = [], 0
    for g in GROUPS:
        ws = g.split()
        seg = words[i:i + len(ws)]
        assert [w for _, _, w in seg] == ws, (g, seg)
        caps.append({"words": [tuple(x) for x in seg]}); i += len(ws)
    assert i == len(words), words[i:]
    for k, c in enumerate(caps):
        st = c["words"][0][0] if k else 0.0
        near = [x for x in CUTS if abs(x - st) <= 0.16]
        c["t0"] = near[0] if near else st
    for k, c in enumerate(caps):
        nxt = caps[k + 1]["t0"] if k + 1 < len(caps) else DUR
        c["t1"] = min(nxt, c["words"][-1][1] + 0.6) if nxt - c["words"][-1][1] > 0.6 else nxt
    return caps


# ------------------------------------------------------------------ drawing helpers
@functools.lru_cache(None)
def font(size, xb=False):
    return ImageFont.truetype(F_XB if xb else F_B, size, layout_engine=ImageFont.Layout.RAQM)


@functools.lru_cache(None)
def text_img(s, size, color, xb=False):
    f = font(size, xb)
    l, t, r, b = f.getbbox(s, direction="rtl", language="ar")
    im = Image.new("RGBA", (r - l + 6, int(size * 1.55)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((3 - l, int(size * 0.24)), s, font=f, fill=color, direction="rtl", language="ar")
    return im


def clamp(p): return min(max(p, 0.0), 1.0)
def ease_out(p): p = clamp(p); return 1 - (1 - p) ** 3
def ease_back(p):
    p = clamp(p); c = 1.5
    return 1 + (c + 1) * (p - 1) ** 3 + c * (p - 1) ** 2


def paste(base, im, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0.01: return
    if abs(scale - 1) > 0.004:
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.BICUBIC)
    if alpha < 0.999:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    base.alpha_composite(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))))


def shadowed(card, r=14, op=0.30, dy=6):
    pad = r * 3
    out = Image.new("RGBA", (card.width + 2 * pad, card.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, int(255 * op)), (pad, pad + dy, pad + card.width, pad + dy + card.height), card.getchannel("A"))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(r)))
    out.alpha_composite(card, (pad, pad))
    return out


def rrect(w, h, fill, radius=None, outline=None, width=0):
    S = 3
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w * S - 1, h * S - 1), radius=(radius or h // 2) * S,
                                         fill=fill, outline=outline, width=width * S)
    return im.resize((w, h), Image.LANCZOS)


# ------------------------------------------------------------------ icons
@functools.lru_cache(None)
def icon(name, d=62, fg=DARK, bg=ACC, k10=10):
    """k10: 0..10 animation parameter for icons with an internal state"""
    k = k10 / 10
    S = 4; D = d * S; c = D / 2
    im = Image.new("RGBA", (D, D), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    if bg: g.ellipse((0, 0, D - 1, D - 1), fill=bg)
    lw = int(D * 0.075)
    def L(pts, w=lw): g.line(pts, fill=fg, width=w, joint="curve")
    def E(x, y, r, **kw): g.ellipse((D*x - D*r, D*y - D*r, D*x + D*r, D*y + D*r), **kw)
    if name == "check":
        L([(D*.30, D*.52), (D*.44, D*.66), (D*.71, D*.37)])
    elif name == "x":
        L([(D*.34, D*.34), (D*.66, D*.66)]); L([(D*.66, D*.34), (D*.34, D*.66)])
    elif name == "spots":                      # skin patch with spots that fade (k = visibility)
        g.rounded_rectangle((D*.24, D*.24, D*.76, D*.76), radius=D*.16, outline=fg, width=lw)
        col = fg[:3] + (int(255 * k),)
        for x, y, r in [(.40, .42, .07), (.60, .50, .055), (.45, .62, .045)]:
            E(x, y, r, fill=col)
    elif name == "repeat":
        g.arc((D*.24, D*.24, D*.76, D*.76), 30, 300, fill=fg, width=lw)
        ax, ay = c + D*.26*math.cos(math.radians(300)), c + D*.26*math.sin(math.radians(300))
        g.polygon([(ax + D*.10, ay - D*.02), (ax - D*.05, ay - D*.10), (ax - D*.02, ay + D*.08)], fill=fg)
    elif name == "sun":
        E(.5, .5, .13, fill=fg)
        for a in range(0, 360, 45):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            L([(c + D*.21*ca, c + D*.21*sa), (c + D*.30*ca, c + D*.30*sa)], int(lw * .8))
    elif name == "bottle":
        g.rounded_rectangle((D*.35, D*.38, D*.65, D*.76), radius=D*.07, outline=fg, width=lw)
        g.rectangle((D*.43, D*.24, D*.57, D*.36), fill=fg)
        L([(D*.42, D*.56), (D*.58, D*.56)])
    elif name == "jar":
        g.rounded_rectangle((D*.27, D*.44, D*.73, D*.74), radius=D*.08, outline=fg, width=lw)
        g.rounded_rectangle((D*.30, D*.30, D*.70, D*.42), radius=D*.04, fill=fg)
    elif name == "spark":
        pts = []
        for i in range(8):
            r = D*.27 if i % 2 == 0 else D*.09
            a = math.radians(i * 45 - 90)
            pts.append((c + r*math.cos(a), c + r*math.sin(a)))
        g.polygon(pts, fill=fg)
    elif name == "shield":
        g.polygon([(c, D*.22), (D*.73, D*.31), (D*.70, D*.55), (c, D*.79), (D*.30, D*.55), (D*.27, D*.31)],
                  outline=fg, width=lw)
        E(.5, .48, .07, fill=fg)
    elif name == "down":
        L([(c, D*.27), (c, D*.70)]); L([(D*.33, D*.53), (c, D*.71), (D*.67, D*.53)])
    elif name == "hourglass":
        L([(D*.32, D*.26), (D*.68, D*.26)]); L([(D*.32, D*.74), (D*.68, D*.74)])
        g.polygon([(D*.36, D*.28), (D*.64, D*.28), (c, D*.50), (D*.64, D*.72), (D*.36, D*.72), (c, D*.50)],
                  outline=fg, width=int(lw*.8))
        g.polygon([(D*.42, D*.70), (D*.58, D*.70), (c, D*.58)], fill=fg)
    elif name == "search":
        g.ellipse((D*.27, D*.27, D*.58, D*.58), outline=fg, width=lw); L([(D*.55, D*.55), (D*.73, D*.73)])
    elif name == "one":
        f = font(int(D * .52), True)
        g.text((c, c + D*.03), "1", font=f, fill=fg, anchor="mm")
    return im.resize((d, d), Image.LANCZOS)


# ------------------------------------------------------------------ card builders
@functools.lru_cache(None)
def pill(ic, text, size=48, h=104, tcol=(255, 255, 255), fill=GLASS, ik10=10, strike10=0):
    t = text_img(text, size, tcol)
    ico = icon(ic, h - 30, k10=ik10) if ic else None
    padx, gap = 32, 16
    w = padx * 2 + t.width + ((ico.width + gap) if ico else 0)
    card = rrect(w, h, fill)
    x = w - padx + (10 if ico else 0)
    if ico:
        card.alpha_composite(ico, (x - ico.width, (h - ico.height) // 2)); x -= ico.width + gap
    card.alpha_composite(t, (x - t.width, (h - t.height) // 2 + 2))
    if strike10:
        ImageDraw.Draw(card).line([(x, h // 2 + 3), (x - (t.width + 2) * strike10 / 10, h // 2 + 3)],
                                  fill=ACC + (255,), width=5)
    return shadowed(card)


@functools.lru_cache(None)
def badge(ic, d=50):
    return shadowed(icon(ic, d, fg=DARK, bg=ACC), r=8, op=0.35, dy=3)


@functools.lru_cache(None)
def small_pill(text, lit, size=36, h=78):
    t = text_img(text, size, DARK if lit else (255, 255, 255))
    w = t.width + 52
    card = rrect(w, h, ACC + (255,) if lit else GLASS)
    card.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2 + 2))
    return shadowed(card, r=10)


@functools.lru_cache(None)
def label(text, size=30):
    t = text_img(text, size, (255, 255, 255, 230))
    w = t.width + 40; h = int(size * 1.7)
    card = rrect(w, h, (18, 22, 24, 170))
    card.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2 + 2))
    return shadowed(card, r=8, op=0.2)


# ------------------------------------------------------------------ animations (each locked to one shot)
OUT = 0.24


def env(t, t0, t1, tin=0.30):
    if t < t0 or t >= t1: return 0.0, 1.0
    if t - t0 < tin:
        p = (t - t0) / tin; return ease_out(p), 0.86 + 0.14 * ease_back(p)
    if t1 - t < OUT:
        p = (t1 - t) / OUT; return ease_out(p), 0.95 + 0.05 * p
    return 1.0, 1.0


def pop(t, ts, d=0.26):
    p = (t - ts) / d
    return ease_out(p), 0.8 + 0.2 * ease_back(p)


def row(base, items, cy, t, al, sc, gap=16):
    """items: [(image, appear_t)] laid out right-to-left, centred on final width"""
    tot = sum(im.width for im, _ in items) - 2 * 30 * len(items) + gap * (len(items) - 1)
    x = W / 2 + tot / 2
    for im, ts in items:
        w = im.width - 60
        if t >= ts:
            a, s = pop(t, ts)
            paste(base, im, x - w / 2, cy, al * a, sc * s)
        x -= w + gap


def a_hook(base, t, a, cy, al, sc):
    # spots fade out on "وتختفي", come back on "بترجع"
    k = 1.0
    if t >= 1.42: k = 1 - ease_out((t - 1.42) / 0.5)
    if t >= 2.86: k = ease_out((t - 2.86) / 0.4)
    im = pill("spots", "التصبغات", ik10=int(round(k * 10)))
    paste(base, im, W / 2, cy, al, sc)
    if t >= 2.86:
        p, s = pop(t, 2.86)
        paste(base, badge("repeat"), W / 2 + (im.width - 60) / 2 - 6, cy - 44, al * p, s)


def a_chip(base, t, a, cy, al, sc):
    st = a.get("strike")
    sk = int(round(ease_out((t - st) / 0.35) * 10)) if st and t >= st else 0
    im = pill(a["icon"], a["text"], strike10=sk)
    paste(base, im, W / 2, cy, al, sc)
    if "badge" in a and t >= a["badge"][1]:
        p, s = pop(t, a["badge"][1])
        paste(base, badge(a["badge"][0]), W / 2 + (im.width - 60) / 2 - 6, cy - 44, al * p, s)


def a_swap(base, t, a, cy, al, sc):
    ts = a["swap"]
    if t < ts:
        paste(base, pill(a["icon"], a["text"]), W / 2, cy, al, sc); return
    p = ease_out((t - ts) / 0.22)
    paste(base, pill(a["icon"], a["text"]), W / 2, cy - 30 * p, al * (1 - p), sc)
    paste(base, pill(a["icon"], a["text2"], tcol=ACC), W / 2, cy + 30 * (1 - p), al * p, sc)


def a_list(base, t, a, cy, al, sc):
    paste(base, label(a["title"]), W / 2, cy - 66, al, sc)
    row(base, [(small_pill(s, False), ts) for s, ts in a["items"]], cy + 14, t, al, sc)


def a_steps(base, t, a, cy, al, sc):
    paste(base, label(a["title"]), W / 2, cy - 66, al, sc)
    items = [(small_pill(s, t >= ts), a["t0"]) for s, ts in a["items"]]
    # lit-state changes get a small bump
    tot = sum(im.width - 60 for im, _ in items) + 16 * (len(items) - 1)
    x = W / 2 + tot / 2
    for (s, ts), (im, _) in zip(a["items"], items):
        w = im.width - 60
        bump = 1 + 0.08 * math.sin(math.pi * clamp((t - ts) / 0.25)) if t >= ts else 1
        paste(base, im, x - w / 2, cy + 14, al, sc * bump)
        x -= w + 16


def a_pair(base, t, a, cy, al, sc):
    (i1, t1_, ts1), (i2, t2_, ts2) = a["items"]
    p1 = pill(i1, t1_, size=42, h=94); p2 = pill(i2, t2_, size=42, h=94)
    sep = text_img(a.get("sep", "أو"), 38, ACC)
    w1, w2 = p1.width - 60, p2.width - 60
    gap = 22
    tot = w1 + w2 + sep.width + 2 * gap
    x = W / 2 + tot / 2
    paste(base, p1, x - w1 / 2, cy, al, sc)
    if t >= ts2:
        a2, s2 = pop(t, ts2)
        paste(base, sep, x - w1 - gap - sep.width / 2, cy, al * a2, sc)
        paste(base, p2, x - w1 - 2 * gap - sep.width - w2 / 2, cy, al * a2, sc * s2)


@functools.lru_cache(None)
def cta(press10):
    t = text_img("التشخيص أولًا", 46, DARK)
    ico = icon("check", 64, fg=ACC, bg=DARK)
    h = 104; w = 32 * 2 + t.width + ico.width + 16
    card = rrect(w, h, ACC + (255,))
    x = w - 32 + 8
    card.alpha_composite(ico, (x - ico.width, (h - ico.height) // 2)); x -= ico.width + 16 - 8
    card.alpha_composite(t, (x - t.width, (h - t.height) // 2 + 2))
    return shadowed(card, op=0.28 * (1 - 0.5 * press10 / 10))


def a_cta(base, t, a, cy, al, sc):
    tp = a["tap"]; press = math.sin(math.pi * clamp((t - tp) / 0.3)) if t >= tp else 0
    im = cta(int(round(press * 10)))
    paste(base, im, W / 2, cy, al, sc * (1 - 0.05 * press))
    if tp <= t < tp + 0.6:
        u = (t - tp) / 0.6; r = 16 + 70 * ease_out(u)
        rip = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
        ImageDraw.Draw(rip).ellipse((110 - r, 110 - r, 110 + r, 110 + r), outline=(255, 255, 255, int(230 * (1 - u))), width=5)
        paste(base, rip, W / 2 + (im.width - 60) / 2 - 70, cy + 10, al)


ANIMS = [
    {"f": a_hook, "t0": 0.00, "t1": 3.64},
    {"f": a_chip, "t0": 3.64, "t1": 6.80, "icon": "sun", "text": "مش بس الشمس"},
    {"f": a_list, "t0": 6.80, "t1": 11.52, "title": "أسباب تانية",
     "items": [("آثار التهابات", 7.68), ("حب الشباب", 9.34), ("تغيرات هرمونية", 10.24)]},
    {"f": a_chip, "t0": 11.52, "t1": 15.40, "icon": "bottle", "text": "منتجات مش مناسبة", "badge": ("x", 14.32)},
    {"f": a_swap, "t0": 18.28, "t1": 20.60, "icon": "one", "text": "الخطوة الأولى", "text2": "التشخيص", "swap": 19.94},
    {"f": a_steps, "t0": 20.60, "t1": 27.32, "title": "التشخيص",
     "items": [("فحص", 20.60), ("النوع", 22.72), ("السبب", 24.00), ("العلاج", 25.16)]},
    {"f": a_pair, "t0": 27.32, "t1": 32.12, "items": [("jar", "كريمات تفتيح", 27.32), ("spark", "جلسات", 30.76)]},
    {"f": a_list, "t0": 32.12, "t1": 35.84, "title": "الجلسات",
     "items": [("تقشير", 32.12), ("ديرمابن", 33.04), ("ليزر", 34.08)]},
    {"f": a_chip, "t0": 36.96, "t1": 40.40, "icon": "shield", "text": "واقي الشمس", "badge": ("check", 38.22)},
    {"f": a_chip, "t0": 40.40, "t1": 44.04, "icon": "down", "text": "نقلل فرص الرجوع"},
    {"f": a_pair, "t0": 44.04, "t1": 48.20, "sep": "·",
     "items": [("hourglass", "متستعجليش", 44.04), ("x", "كذا منتج", 46.28)]},
    {"f": a_cta, "t0": 48.20, "t1": 52.76, "tap": 49.10},
]

SFX = [  # (file, time, align, max_len)
    ("ui 1", 0.05, "onset", None), ("ui 2", 1.42, "onset", None), ("alert", 2.86, "onset", None),
    ("notification", 3.64, "onset", None),
    ("data 1", 6.80, "onset", None), ("iphone tap 1", 7.68, "onset", None),
    ("iphone tab 2", 9.34, "peak", None), ("iphone tap 1", 10.24, "onset", None),
    ("ui 1", 11.52, "onset", None), ("fail", 14.32, "onset", None),
    ("notification 2", 18.28, "onset", None), ("ui 2", 19.94, "onset", None),
    ("data 1", 20.60, "onset", None), ("iphone tap 1", 22.72, "onset", None),
    ("iphone tab 2", 24.00, "peak", None), ("iphone tap 1", 25.16, "onset", None),
    ("ui 1", 27.32, "onset", None), ("ui 2", 30.76, "onset", None),
    ("iphone tap 1", 32.12, "onset", None), ("iphone tab 2", 33.04, "peak", None), ("iphone tap 1", 34.08, "onset", None),
    ("notification", 36.96, "onset", None), ("iphone tab 2", 38.22, "peak", None),
    ("data 1", 40.40, "onset", None),
    ("clock", 44.04, "onset", None), ("alert", 46.28, "onset", None),
    ("iphone mix tabs", 48.20, "onset", 1.1),
]


def shot_at(t):
    for s in SHOTS:
        if s[0] - 1e-6 <= t < s[1] - 1e-6: return s
    return SHOTS[-1]


def check_plan():
    starts = {s for s, _, _ in SHOTS}; ends = {e for _, e, _ in SHOTS}
    for a in ANIMS:
        assert a["t0"] in starts and a["t1"] in ends, ("anim not on shot boundaries", a["t0"], a["t1"])
        for z0, z1 in USER_ZOOMS:
            assert a["t1"] <= z0 or a["t0"] >= z1, ("anim overlaps user zoom", a["t0"])
        fr = {shot_at(x)[2] for x in np.arange(a["t0"], a["t1"] - 1e-3, 0.04)}
        assert len(fr) == 1, ("anim spans two framings", a["t0"], fr)
        a["cy"] = TOP_Y if fr == {"W"} else LOW_Y
    for c in TRANSITIONS:
        assert c in starts
    for _, ts, _, _ in SFX:
        for z0, z1 in USER_ZOOMS:
            assert not (z0 - 0.1 < ts < z1), ("sfx on user zoom", ts)
        assert any(a["t0"] <= ts < a["t1"] for a in ANIMS) or ts < 0.1, ("sfx without visual event", ts)


# ------------------------------------------------------------------ captions drawing
@functools.lru_cache(None)
def cap_word(w, active):
    return text_img(w, CAP_SIZE, ACC + (255,) if active else (255, 255, 255, 255), True)


@functools.lru_cache(None)
def cap_shadow(words):
    ims = [cap_word(w, False) for w in words]
    sp = int(CAP_SIZE * 0.26)
    tw = sum(i.width for i in ims) + sp * (len(ims) - 1); hh = max(i.height for i in ims)
    pad = 36
    m = Image.new("RGBA", (tw + 2 * pad, hh + 2 * pad), (0, 0, 0, 0))
    x = pad + tw
    for im in ims:
        x -= im.width
        sh = Image.new("RGBA", im.size, (0, 0, 0, 255)); sh.putalpha(im.getchannel("A"))
        m.alpha_composite(sh, (x, pad + 3)); x -= sp
    a = np.array(m.filter(ImageFilter.GaussianBlur(9)))
    a[..., 3] = np.clip(a[..., 3].astype(np.float32) * 1.25, 0, 255).astype(np.uint8)
    return Image.fromarray(a), tw, pad


def draw_caption(base, caps, t):
    c = next((c for c in caps if c["t0"] <= t < c["t1"]), None)
    if c is None: return
    words = tuple(w for _, _, w in c["words"])
    act = 0
    for j, (s, _, _) in enumerate(c["words"]):
        if t >= s - 0.04: act = j
    sh, tw, pad = cap_shadow(words)
    layer = sh.copy()
    sp = int(CAP_SIZE * 0.26); x = pad + tw
    for j, w in enumerate(words):
        im = cap_word(w, j == act and len(words) > 1)
        x -= im.width; layer.alpha_composite(im, (x, pad)); x -= sp
    p = ease_out((t - c["t0"]) / 0.14)
    paste(base, layer, W / 2, CAP_Y + 12 * (1 - p), p)


# ------------------------------------------------------------------ frame transform
def transform(fr, t, fi):
    s0, s1, kind = shot_at(t)
    if any(z0 <= t < z1 for z0, z1 in USER_ZOOMS) or kind not in "WM": return fr
    s = 1.0; extra = 0.0; gauss = 0.0
    if kind == "W":
        u = (t - s0) / (s1 - s0); s = 1 + DRIFT * (u * u * (3 - 2 * u))
    k = fi - int(round(s0 * FPS))
    if s0 in TRANSITIONS and k < 6:
        e = (1 - k / 6) ** 2; extra = 0.10 * e; gauss = 8 * e
    s += extra
    if abs(s - 1) < 1e-4 and gauss == 0: return fr
    ax, ay = FACE_W if kind == "W" else (520, 420)
    M = np.float32([[s, 0, ax - s * ax], [0, s, ay - s * ay]])
    out = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    if gauss > 0.5: out = cv2.GaussianBlur(out, (0, 0), gauss)
    return out


# ------------------------------------------------------------------ audio
def load_audio(path):
    a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR),
                                      "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
    return a.reshape(-1, 2).copy()


def mix_audio():
    mix = load_audio(f"{WD}/src/pigment.mp4")
    for fn, t, align, maxlen in SFX:
        s = load_audio(f"{WD}/sfx/{fn}.MP3")
        m = np.abs(s).mean(1); e = np.convolve(m, np.ones(480) / 480, "same")
        on, pk = np.argmax(e > 0.1 * e.max()) / SR, np.argmax(e) / SR
        off = on if align == "onset" else pk
        st = int(round((t - off) * SR))
        if st < 0: s = s[-st:]; st = 0
        if maxlen:
            s = s[:int((off + maxlen) * SR)].copy(); fl = int(0.25 * SR); s[-fl:] *= np.linspace(1, 0, fl)[:, None]
        rms = 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-9); pkdb = 20 * np.log10(np.abs(s).max() + 1e-9)
        g = min(-27 - rms, -6 - pkdb)
        s = s * 10 ** (g / 20)
        end = min(len(mix), st + len(s)); mix[st:end] += s[:end - st]
    if np.abs(mix).max() > 0.98: mix = np.tanh(mix / 0.98) * 0.98
    mix.astype(np.float32).tofile(f"{WD}/pigment_mix.f32")


# ------------------------------------------------------------------ main
def render(t_from=0.0, t_to=DUR, out=f"{WD}/pigment_video.mp4"):
    check_plan()
    caps = build_captions()
    for c in caps:
        print(f"{c['t0']:6.2f}-{c['t1']:6.2f}  {' '.join(w for _, _, w in c['words'])}")
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{t_from}", "-i", f"{WD}/src/pigment.mp4", "-t", f"{t_to - t_from}",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                            "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    fi = int(round(t_from * FPS))
    while True:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: break
        t = fi / FPS
        fr = transform(np.frombuffer(buf, np.uint8).reshape(H, W, 3), t, fi)
        img = Image.fromarray(np.ascontiguousarray(fr)).convert("RGBA")
        for a in ANIMS:
            al, sc = env(t, a["t0"], a["t1"])
            if al > 0: a["f"](img, t, a, a["cy"], al, sc)
        draw_caption(img, caps, t)
        enc.stdin.write(img.convert("RGB").tobytes())
        fi += 1
    enc.stdin.close(); enc.wait(); dec.terminate()


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "audio": mix_audio()
    elif cmd == "video": render()
    elif cmd == "check": check_plan(); [print(c["t0"], c["t1"], [w for *_, w in c["words"]]) for c in build_captions()]
    elif cmd == "stills":
        check_plan(); caps = build_captions()
        ts = [float(x) for x in sys.argv[2:]]
        tiles = []
        for t in ts:
            fi = int(round(t * FPS))
            raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", f"{WD}/src/pigment.mp4", "-frames:v", "1",
                                  "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
            fr = transform(np.frombuffer(raw[:W * H * 3], np.uint8).reshape(H, W, 3), t, fi)
            img = Image.fromarray(np.ascontiguousarray(fr)).convert("RGBA")
            for a in ANIMS:
                al, sc = env(t, a["t0"], a["t1"])
                if al > 0: a["f"](img, t, a, a["cy"], al, sc)
            draw_caption(img, caps, t)
            tiles.append(img.convert("RGB").resize((360, 640)))
        sheet = Image.new("RGB", (360 * len(tiles), 640))
        for i, im in enumerate(tiles): sheet.paste(im, (360 * i, 0))
        sheet.save(f"{WD}/look/stills.jpg", quality=88)
