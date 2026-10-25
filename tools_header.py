"""ヘッダー画像（キャラ絵なし）。夜空のグラデーション＋星とハート＋サイト名"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random, json, math
W, H = 1200, 630
S = json.load(open("data/site.json"))
im = Image.new("RGB", (W, H))
px = im.load()
for y in range(H):
    for x in range(0, W):
        t = y / H; u = x / W
        px[x, y] = (int(20 + 50 * u * (1 - t)), int(18 + 12 * t), int(43 + 60 * (1 - t) * u + 20 * t))
d = ImageDraw.Draw(im, "RGBA")
random.seed(7)
for _ in range(220):
    x, y, r = random.randint(0, W), random.randint(0, H), random.choice([1, 1, 1, 2, 2, 3])
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, random.randint(80, 220)))
def heart(cx, cy, s, col):
    pts = [(cx + s * 16 * math.sin(t) ** 3 / 16, cy - s * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16)
           for t in [i * math.pi / 60 for i in range(121)]]
    d.polygon(pts, fill=col)
for _ in range(18):
    heart(random.randint(40, W - 40), random.randint(40, H - 40), random.randint(10, 34),
          random.choice([(255, 111, 165, 120), (255, 209, 102, 110), (139, 123, 255, 120)]))
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
g.ellipse((200, 120, 1000, 520), fill=(255, 111, 165, 70)); glow = glow.filter(ImageFilter.GaussianBlur(90))
im = Image.alpha_composite(im.convert("RGBA"), glow); d = ImageDraw.Draw(im)
F = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"; F2 = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
l1, l2 = S["name"].split("。", 1); l1 += "。"
for txt, size, y, col in [(l1, 64, 170, (255, 255, 255)), (l2, 64, 270, (255, 154, 193)), (S["catch"], 38, 400, (255, 209, 102))]:
    f = ImageFont.truetype(F if size > 40 else F2, size)
    w = d.textlength(txt, font=f)
    d.text(((W - w) / 2, y), txt, font=f, fill=col, stroke_width=4 if size > 40 else 2, stroke_fill=(30, 20, 60))
f = ImageFont.truetype(F2, 26); txt = "配信ランキング上位アニメのヒロインを、公式PVと人気の数字で"
d.text(((W - d.textlength(txt, font=f)) / 2, 480), txt, font=f, fill=(230, 225, 255))
im.convert("RGB").save("assets/header_drawn.jpg", quality=90)  # 本人の画像 assets/header.jpg を上書きしない
