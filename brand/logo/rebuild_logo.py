# Stand-in rebuild of the Saber Group mark (from the image the client shared in chat).
# Replace sabergroup.png with the official file whenever available; brand.py loads it automatically.
import os
from PIL import Image, ImageDraw, ImageFont
H = os.path.dirname(os.path.abspath(__file__))
S = 1200; RED = (225, 48, 42, 255); WH = (255, 255, 255, 255)
im = Image.new("RGBA", (S, S), WH); d = ImageDraw.Draw(im)
d.rectangle((10, 10, S - 11, S - 11), fill=RED)
d.rectangle((28, 28, S - 29, S - 29), outline=WH, width=4)
L = ImageFont.Layout.RAQM
def fit(text, path, x0, x1, ytop, h, track=0):
    f = ImageFont.truetype(path, 400, layout_engine=L)
    l, t, r, b = f.getbbox(text)
    sc_h = h / (b - t)
    f = ImageFont.truetype(path, int(400 * sc_h), layout_engine=L)
    tmp = Image.new("L", (S * 2, int(h * 1.6)), 0)
    ImageDraw.Draw(tmp).text((0, 0), text, font=f, fill=255)
    tmp = tmp.crop(tmp.getbbox()); tmp = tmp.resize((x1 - x0, h), Image.LANCZOS)
    im.paste(WH, (x0, ytop), tmp)
fit("SABER", f"{H}/BebasNeue-400.ttf", 185, 1020, 163, 330)
fit("GROUP", f"{H}/BebasNeue-400.ttf", 185, 1020, 503, 325)
fit("MARKETING AGENCY", f"{H}/Oswald-200.ttf", 305, 905, 880, 75)
f = ImageFont.truetype(f"{H}/Tajawal-200.ttf", 70, layout_engine=L)
ar = "وكـــالـة تـــســـويـــق"
tmp = Image.new("L", (900, 160), 0); ImageDraw.Draw(tmp).text((10, 10), ar, font=f, fill=255, direction="rtl", language="ar")
tmp = tmp.crop(tmp.getbbox()); tmp = tmp.resize((600, int(tmp.height * 600 / tmp.width)), Image.LANCZOS)
im.paste(WH, (305, 975), tmp)
f = ImageFont.truetype(f"{H}/Oswald-200.ttf", 70, layout_engine=L)
d.ellipse((1005, 113, 1067, 175), outline=WH, width=5); d.text((1036, 146), "R", font=f, fill=WH, anchor="mm")
im.save(f"{H}/sabergroup.png")
