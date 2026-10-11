# Renders brand preview stills: intro overlay + caption + icon chip on each backdrop.
# usage: python3 preview.py <out_dir> [cocoa_frame.png]
import sys, os
from PIL import Image, ImageDraw
import brand as B

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
frame = sys.argv[2] if len(sys.argv) > 2 else None
BG = {"cocoa": (92, 52, 30), "ivory_navy": (240, 238, 236), "ivory_grey": (236, 235, 233), "rouge": (150, 22, 34)}


def backdrop(name):
    if name == "cocoa" and frame: return Image.open(frame).convert("RGBA").resize((B.W, B.H))
    im = Image.new("RGBA", (B.W, B.H), BG[name] + (255,)); d = ImageDraw.Draw(im)
    for y in range(B.H):                          # soft studio vignette
        k = 1 - 0.18 * abs(y - B.H * 0.4) / B.H
        d.line((0, y, B.W, y), fill=tuple(int(c * k) for c in BG[name]) + (255,))
    return im


for name in B.THEMES:
    im = backdrop(name)
    im.alpha_composite(B.intro_frame(1.9, name))
    cap = B.caption("التصبغات مش بتختفي لوحدها", name, key={"التصبغات"})
    im.alpha_composite(cap, ((B.W - cap.width) // 2, 1470))
    chip = B.icon_chip("sun", "واقي الشمس كل يوم", name)
    im.alpha_composite(chip, ((B.W - chip.width) // 2, 1640))
    im.convert("RGB").save(f"{out}/{name}.jpg", quality=90)
    im.convert("RGB").resize((360, 640)).save(f"{out}/{name}_sm.jpg", quality=85)
print("ok")
