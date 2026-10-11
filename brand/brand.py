# Dr. Marwa Magdy — video design system (tokens, fonts, icons, intro overlay).
# Every video uses the same fonts / icons / layout; only the colour theme changes per shoot.
import os, io, math, functools
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
SS = 2                                     # supersampling

# ------------------------------------------------------------------ fonts
FONTS = {
    "name":    "CormorantGaramond-600i.ttf",   # Dr. Marwa Magdy  (Latin display, italic serif)
    "serif":   "CormorantGaramond-600.ttf",
    "label":   "Jost-400.ttf",                 # tracked caps: AESTHETIC DERMATOLOGIST, CREATED BY
    "label_l": "Jost-300.ttf",
    "script":  "PinyonScript-400.ttf",         # rare accent word only (glow, skin...)
    "ar_head": "ElMessiri-700.ttf",            # Arabic titles / hooks
    "ar_soft": "ElMessiri-600.ttf",
    "ar_cap":  "Almarai-800.ttf",              # Arabic captions (max readability)
    "ar_cap_b": "Almarai-700.ttf",
}


@functools.lru_cache(None)
def font(role, px):
    return ImageFont.truetype(os.path.join(HERE, "fonts", FONTS[role]), int(px),
                              layout_engine=ImageFont.Layout.RAQM)


# ------------------------------------------------------------------ colour themes (one per shoot)
def rgb(h, a=255): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)

THEMES = {
    # brown backdrop, cream/beige outfit
    "cocoa": dict(ink="#F7EEE3", accent="#D9B98C", soft="#EBCFC3", chip="#3B2418", chip_a=150,
                  line="#D9B98C", shadow="#2A170E", shadow_a=150),
    # white backdrop, navy outfit
    "ivory_navy": dict(ink="#1E2A47", accent="#93505A", soft="#6F7A94", chip="#FFFFFF", chip_a=190,
                       line="#93505A", shadow="#1E2A47", shadow_a=40),
    # white backdrop, grey outfit
    "ivory_grey": dict(ink="#3A3A41", accent="#82594B", soft="#8E8790", chip="#FFFFFF", chip_a=190,
                       line="#82594B", shadow="#3A3A41", shadow_a=40),
    # red backdrop, white outfit
    "rouge": dict(ink="#FFFFFF", accent="#F6D6C8", soft="#F2B9AE", chip="#5A1420", chip_a=140,
                  line="#F6D6C8", shadow="#3D0A12", shadow_a=150),
}


def theme(name):
    t = THEMES[name]
    return {k: (rgb(v) if isinstance(v, str) else v) for k, v in t.items()}


# ------------------------------------------------------------------ icons (Phosphor, light + fill)
@functools.lru_cache(None)
def icon(name, px, color, style="light"):
    import cairosvg
    svg = open(os.path.join(HERE, "icons", style, name + ".svg")).read()
    svg = svg.replace("currentColor", "#%02x%02x%02x" % color[:3])
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=int(px), output_height=int(px))
    im = Image.open(io.BytesIO(png)).convert("RGBA")
    if len(color) == 4 and color[3] < 255:
        im.putalpha(im.getchannel("A").point(lambda v: v * color[3] // 255))
    return im


# ------------------------------------------------------------------ helpers
def cl(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def eo(p): p = cl(p); return 1 - (1 - p) ** 3
def eio(p): p = cl(p); return 4 * p ** 3 if p < .5 else 1 - (-2 * p + 2) ** 3 / 2


def text_img(s, role, px, fill, tracking=0.0):
    """tight RGBA image of a string; tracking in em (Latin caps only)."""
    f = font(role, px)
    kw = {"direction": "rtl", "language": "ar"} if any(ord(c) > 1500 for c in s) else {}
    if tracking and not kw:
        adv = [f.getlength(c) + tracking * px for c in s]
        w = int(sum(adv) - tracking * px) + 8
        im = Image.new("RGBA", (w, int(px * 1.5)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 4
        for c, a in zip(s, adv): d.text((x, int(px * .15)), c, font=f, fill=fill); x += a
        return im.crop(im.getbbox() or (0, 0, 1, 1))
    l, t, r, b = f.getbbox(s, **kw)
    im = Image.new("RGBA", (r - l + 8, b - t + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - l, 4 - t), s, font=f, fill=fill, **kw)
    return im


def with_alpha(im, a):
    if a >= .999: return im
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a))); return im


def soft_shadow(im, col, alpha, r):
    sh = Image.new("RGBA", im.size, col[:3] + (0,))
    sh.putalpha(im.getchannel("A").point(lambda v: v * alpha // 255))
    pad = r * 3
    big = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    big.alpha_composite(sh, (pad, pad)); big = big.filter(ImageFilter.GaussianBlur(r))
    big.alpha_composite(im, (pad, pad)); return big, pad


def put(layer, im, x, y, a=1.0):
    if a <= 0.01: return
    layer.alpha_composite(with_alpha(im, a), (int(round(x)), int(round(y))))


# ------------------------------------------------------------------ logo
def logo(px_w, th):
    """Saber Group logo; drop the real file at brand/logo/sabergroup.png (transparent PNG)."""
    p = os.path.join(HERE, "logo", "sabergroup.png")
    if os.path.exists(p):
        im = Image.open(p).convert("RGBA")
        return im.resize((int(px_w), int(im.height * px_w / im.width)), Image.LANCZOS)
    # placeholder wordmark until the real logo is supplied
    a = text_img("SABER", "serif", px_w * 0.30, th["ink"], tracking=0.18)
    b = text_img("GROUP", "label", px_w * 0.12, th["ink"], tracking=0.6)
    im = Image.new("RGBA", (max(a.width, b.width), a.height + b.height + 10), (0, 0, 0, 0))
    im.alpha_composite(a, ((im.width - a.width) // 2, 0)); im.alpha_composite(b, ((im.width - b.width) // 2, a.height + 10))
    return im


# ------------------------------------------------------------------ intro overlay (first ~4 s)
# Layout (1080x1920, IG/TikTok safe zones respected):
#   top-right  : CREATED BY / SABERGROUPSTUDIOS © / Saber Group logo, centred stack, 0.3 s → 3.1 s (≈2 s+ fully visible)
#   lower-left : name card  Dr. Marwa Magdy / AESTHETIC DERMATOLOGIST   0.6 s → 4.2 s
SAFE_TOP, SAFE_X = 150, 64
NAME_Y = 1210                     # top of name card; captions live lower (≈1450-1600)
INTRO_LEN = 4.6
LOGO_W = 128                      # logo is the largest item of the credit block


def intro_frame(t, theme_name):
    th = theme(theme_name)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # --- credit block, top-right: CREATED BY / SABERGROUPSTUDIOS © / logo, centred on one axis
    a = eo((t - 0.3) / 0.45) * (1 - eo((t - 2.7) / 0.45))
    if a > 0:
        c1 = text_img("CREATED BY", "label_l", 13, th["ink"], tracking=0.42)
        c2 = text_img("SABERGROUPSTUDIOS ©", "label", 15, th["ink"], tracking=0.22)
        lg = logo(LOGO_W, th)
        gap = 8; colw = max(c1.width, c2.width, lg.width)
        blk = Image.new("RGBA", (colw, c1.height + c2.height + lg.height + gap * 3), (0, 0, 0, 0))
        y = 0
        for im, op in ((c1, 0.8), (c2, 0.9)):
            blk.alpha_composite(with_alpha(im, op), ((colw - im.width) // 2, y)); y += im.height + gap
        y += gap; blk.alpha_composite(lg, ((colw - lg.width) // 2, y))
        bs, pad = soft_shadow(blk, th["shadow"], th["shadow_a"], 8)
        rise = 10 * (1 - eo((t - 0.3) / 0.6))
        put(L, bs, W - SAFE_X - colw - pad, SAFE_TOP - pad + rise, a)

    # --- name card, lower-left
    t0 = 0.6
    out = 1 - eo((t - 4.0) / 0.5)
    if t > t0 and out > 0:
        x0, y0 = SAFE_X + 6, NAME_Y
        # hairline draws from left
        lw = int(300 * eio((t - t0) / 0.7))
        if lw > 2:
            ln = Image.new("RGBA", (lw, 2), th["line"]); put(L, ln, x0 + 44, y0 + 2, out)
        sp = icon("sparkle", 34, th["accent"], "fill")
        rot = sp.rotate(-90 * (1 - eo((t - t0) / 0.8)), Image.BICUBIC)
        put(L, rot, x0, y0 - 15, eo((t - t0) / 0.4) * out)
        nm = text_img("Dr. Marwa Magdy", "name", 78, th["ink"])
        nms, pad = soft_shadow(nm, th["shadow"], th["shadow_a"], 10)
        p = eo((t - t0 - 0.2) / 0.7)
        put(L, nms, x0 - pad + 24 * (1 - p), y0 + 22 - pad, p * out)
        sub = text_img("AESTHETIC DERMATOLOGIST", "label", 22, th["accent"], tracking=0.32)
        subs, pad = soft_shadow(sub, th["shadow"], th["shadow_a"], 6)
        p = eo((t - t0 - 0.5) / 0.6)
        put(L, subs, x0 + 4 - pad + 16 * (1 - p), y0 + 22 + nm.height + 14 - pad, p * out)
    return L


# ------------------------------------------------------------------ caption / title / icon-chip samples
def caption(text, theme_name, key=None, px=58):
    """Arabic caption: Almarai ExtraBold, key word in accent colour. Returns RGBA (centered use)."""
    th = theme(theme_name)
    words = text.split(); f = font("ar_cap", px); sp = px * 0.28
    imgs = [text_img(w, "ar_cap", px, th["accent"] if key and w in key else th["ink"]) for w in words]
    hgt = max(i.height for i in imgs); wid = int(sum(i.width for i in imgs) + sp * (len(imgs) - 1))
    im = Image.new("RGBA", (wid, hgt), (0, 0, 0, 0)); x = wid
    for i in imgs: x -= i.width; im.alpha_composite(i, (int(x), hgt - i.height)); x -= sp
    s, _ = soft_shadow(im, th["shadow"], th["shadow_a"] if th["shadow_a"] < 100 else 170, 9)
    return s


def icon_chip(name, label, theme_name, px=44):
    """frosted pill: line icon + Arabic label (El Messiri)."""
    th = theme(theme_name)
    ic = icon(name, px, th["accent"]); tx = text_img(label, "ar_soft", px * 0.78, th["ink"])
    h = int(px * 1.75); w = tx.width + ic.width + int(px * 1.4)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=th["chip"][:3] + (th["chip_a"],),
                        outline=th["line"][:3] + (120,), width=2)
    im.alpha_composite(ic, (w - ic.width - int(px * .5), (h - ic.height) // 2))
    im.alpha_composite(tx, (int(px * .55), (h - tx.height) // 2))
    return im
