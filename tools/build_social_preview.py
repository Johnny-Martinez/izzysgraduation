from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "social-preview.jpg"
HERO = ROOT / "assets" / "photos" / "hero.jpg"

SERIF = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SERIF_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
SANS = "/System/Library/Fonts/Supplemental/Arial.ttf"
SANS_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

W, H = 1200, 630
BLACK = (12, 12, 12)
INK = (25, 23, 22)
CREAM = (255, 244, 223)
PAPER = (255, 250, 241)
RED = (218, 34, 48)
DEEP_RED = (112, 13, 18)
BLUE = (20, 142, 222)
YELLOW = (255, 214, 61)
GREEN = (42, 176, 116)
SHADOW = (0, 0, 0, 95)


def font(path, size):
    return ImageFont.truetype(path, size)


def text_center(draw, box, text, text_font, fill):
    bbox = draw.textbbox((0, 0), text, font=text_font)
    x = box[0] + (box[2] - box[0] - (bbox[2] - bbox[0])) / 2
    y = box[1] + (box[3] - box[1] - (bbox[3] - bbox[1])) / 2 - 2
    draw.text((x, y), text, font=text_font, fill=fill)


def cover_crop(img, size, focus=(0.52, 0.32)):
    target_w, target_h = size
    scale = max(target_w / img.width, target_h / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, min(resized.width - target_w, round(resized.width * focus[0] - target_w / 2)))
    top = max(0, min(resized.height - target_h, round(resized.height * focus[1] - target_h / 2)))
    return resized.crop((left, top, left + target_w, top + target_h))


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def paste_with_shadow(base, layer, xy, blur=18, offset=(10, 12)):
    shadow = Image.new("RGBA", layer.size, SHADOW)
    shadow.putalpha(layer.getchannel("A").filter(ImageFilter.GaussianBlur(blur)))
    base.alpha_composite(shadow, (xy[0] + offset[0], xy[1] + offset[1]))
    base.alpha_composite(layer, xy)


def draw_cap(draw, x, y, scale=1):
    top = [(x, y), (x + 74 * scale, y - 28 * scale), (x + 148 * scale, y), (x + 74 * scale, y + 29 * scale)]
    draw.polygon(top, fill=INK)
    draw.polygon([(x + 34 * scale, y + 12 * scale), (x + 114 * scale, y + 12 * scale),
                  (x + 106 * scale, y + 51 * scale), (x + 42 * scale, y + 51 * scale)], fill=RED)
    draw.line((x + 132 * scale, y + 5 * scale, x + 153 * scale, y + 76 * scale), fill=YELLOW, width=4)
    draw.ellipse((x + 148 * scale, y + 72 * scale, x + 160 * scale, y + 84 * scale), fill=YELLOW)


def draw_confetti(draw):
    # Keep the 90s color moments outside the invitation card so the card stays formal.
    pieces = [
        ("dot", 76, 80, 8, BLUE), ("dot", 1105, 84, 7, YELLOW), ("dot", 1118, 520, 9, RED),
        ("dot", 82, 533, 7, GREEN), ("dot", 1050, 470, 5, BLUE), ("dot", 145, 110, 5, RED),
        ("line", 104, 146, 160, 118, 6, RED), ("line", 998, 110, 1060, 135, 6, BLUE),
        ("line", 68, 446, 118, 480, 5, YELLOW), ("line", 1048, 562, 1112, 540, 5, GREEN),
        ("line", 250, 62, 285, 88, 4, BLUE), ("line", 920, 64, 954, 34, 4, RED),
        ("tri", 64, 270, 14, YELLOW), ("tri", 1138, 292, 15, BLUE),
    ]
    for piece in pieces:
        if piece[0] == "dot":
            _, x, y, r, color = piece
            draw.ellipse((x - r, y - r, x + r, y + r), fill=color)
        elif piece[0] == "line":
            _, x1, y1, x2, y2, width, color = piece
            draw.line((x1, y1, x2, y2), fill=color, width=width)
        elif piece[0] == "tri":
            _, x, y, r, color = piece
            draw.polygon([(x, y - r), (x - r, y + r), (x + r, y + r)], fill=color)


canvas = Image.new("RGBA", (W, H), BLACK + (255,))
draw = ImageDraw.Draw(canvas)

# Black background with subtle red glow.
for radius, alpha in [(420, 18), (300, 24), (190, 30)]:
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W - 330 - radius, 315 - radius, W - 330 + radius, 315 + radius), fill=RED + (alpha,))
    canvas.alpha_composite(glow)

draw_confetti(draw)

# Invitation card.
card = Image.new("RGBA", (1010, 510), (0, 0, 0, 0))
cd = ImageDraw.Draw(card)
cd.rounded_rectangle((0, 0, 1010, 510), radius=34, fill=PAPER)
cd.rounded_rectangle((18, 18, 992, 492), radius=24, outline=RED, width=6)
cd.rounded_rectangle((35, 35, 975, 475), radius=14, outline=INK, width=2)
cd.rectangle((48, 48, 962, 462), outline=CREAM, width=3)

# Red ribbon and formal invitation label.
cd.rounded_rectangle((72, 66, 300, 112), radius=23, fill=INK)
text_center(cd, (72, 66, 300, 112), "YOU'RE INVITED", font(SANS_BOLD, 21), CREAM)
cd.line((84, 145, 430, 145), fill=RED, width=4)
cd.line((84, 156, 350, 156), fill=BLUE, width=3)

cd.text((84, 178), "Isaac Andress", font=font(SERIF_BOLD, 61), fill=INK)
cd.text((84, 254), "Martinez", font=font(SERIF_BOLD, 71), fill=INK)
cd.text((88, 336), "Class of 2026", font=font(SANS_BOLD, 31), fill=DEEP_RED)
cd.text((88, 382), "Graduation Party", font=font(SANS_BOLD, 37), fill=INK)

# Detail row.
detail_y = 430
details = [("JUNE 6, 2026", 88, 236), ("2:00 PM", 255, 360), ("EAGLE MOUNTAIN, UT", 380, 605)]
for text, x1, x2 in details:
    cd.rounded_rectangle((x1, detail_y, x2, detail_y + 44), radius=10, fill=CREAM, outline=INK, width=2)
    text_center(cd, (x1, detail_y, x2, detail_y + 44), text, font(SANS_BOLD, 20), INK)

draw_cap(cd, 412, 78, 0.72)

# Portrait in a keepsake frame.
hero = Image.open(HERO).convert("RGB")
portrait = cover_crop(hero, (310, 390), focus=(0.55, 0.31)).convert("RGBA")
mask = rounded_mask((310, 390), 20)
portrait.putalpha(mask)
cd.rounded_rectangle((642, 72, 928, 430), radius=22, fill=RED)
cd.rounded_rectangle((620, 54, 912, 416), radius=26, fill=INK)
cd.rounded_rectangle((632, 66, 900, 404), radius=22, fill=CREAM)
card.alpha_composite(portrait.resize((256, 326), Image.Resampling.LANCZOS), (638, 72))
cd.rounded_rectangle((638, 72, 894, 398), radius=18, outline=INK, width=4)
text_center(cd, (620, 420, 912, 464), "izzysgraduation.com", font(SANS_BOLD, 21), INK)

paste_with_shadow(canvas, card, (95, 60), blur=18, offset=(12, 14))

# Outside corner stamp.
draw.rounded_rectangle((42, 36, 132, 118), radius=8, fill=RED, outline=CREAM, width=4)
text_center(draw, (42, 36, 132, 84), "26", font(SANS_BOLD, 34), CREAM)
text_center(draw, (42, 78, 132, 113), "GRAD", font(SANS_BOLD, 17), CREAM)

canvas.convert("RGB").save(OUT, quality=93, optimize=True, progressive=True)
print(OUT)
