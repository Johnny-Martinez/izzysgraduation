from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "social-preview.jpg"
HERO = ROOT / "assets" / "photos" / "hero.jpg"

W, H = 1200, 630
BLACK = (9, 10, 11)
CHARCOAL = (18, 19, 21)
GRID = (46, 48, 52)
PAPER = (255, 247, 231)
CREAM = (255, 238, 203)
INK = (18, 18, 18)
RED = (226, 28, 42)
DARK_RED = (95, 0, 10)
BLUE = (15, 134, 216)
DEEP_BLUE = (10, 62, 112)
YELLOW = (245, 200, 52)
GREEN = (44, 178, 118)
WHITE = (255, 252, 245)

SERIF = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SERIF_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
SANS = "/System/Library/Fonts/Supplemental/Arial.ttf"
SANS_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
SANS_BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_text(draw, text, max_width, path, start_size):
    size = start_size
    while size > 12:
        f = font(path, size)
        box = draw.textbbox((0, 0), text, font=f)
        if box[2] - box[0] <= max_width:
            return f
        size -= 2
    return font(path, size)


def cover_crop(img, size, focus=(0.55, 0.32)):
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


def center_text(draw, box, text, text_font, fill):
    bbox = draw.textbbox((0, 0), text, font=text_font)
    x = box[0] + (box[2] - box[0] - (bbox[2] - bbox[0])) / 2
    y = box[1] + (box[3] - box[1] - (bbox[3] - bbox[1])) / 2 - 2
    draw.text((x, y), text, font=text_font, fill=fill)


def paste_rotated(base, layer, xy, degrees):
    rotated = layer.rotate(degrees, expand=True, resample=Image.Resampling.BICUBIC)
    base.alpha_composite(rotated, xy)


def draw_slash(base, xy, width, height, color, degrees=-12, alpha=255):
    layer = Image.new("RGBA", (width, height), color + (alpha,))
    paste_rotated(base, layer, xy, degrees)


def duotone_portrait():
    source = Image.open(HERO).convert("RGB")
    crop = cover_crop(source, (460, 560), focus=(0.56, 0.30))
    gray = ImageOps.grayscale(crop)
    gray = ImageOps.autocontrast(gray).filter(ImageFilter.UnsharpMask(radius=2, percent=145, threshold=3))
    poster = gray.point(lambda p: 0 if p < 52 else 94 if p < 132 else 176 if p < 205 else 255)

    palette = {
        0: (8, 8, 8),
        94: DARK_RED,
        176: RED,
        255: CREAM,
    }
    out = Image.new("RGBA", poster.size)
    src = poster.load()
    dst = out.load()
    for y in range(out.height):
        for x in range(out.width):
            dst[x, y] = palette[src[x, y]] + (255,)

    halftone = Image.new("RGBA", out.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(halftone)
    for y in range(8, out.height, 16):
        for x in range(8, out.width, 16):
            value = gray.getpixel((x, y))
            if value > 110:
                r = 2 if value > 185 else 3
                hd.ellipse((x - r, y - r, x + r, y + r), fill=BLACK + (70,))
    out.alpha_composite(halftone)
    out.putalpha(rounded_mask(out.size, 26))
    return out


def draw_background(draw, canvas):
    draw.rectangle((0, 0, W, H), fill=BLACK)
    for x in range(0, W, 72):
        draw.line((x, 0, x, H), fill=GRID, width=1)
    for y in range(0, H, 72):
        draw.line((0, y, W, y), fill=GRID, width=1)

    draw.rectangle((0, 0, W, 20), fill=RED)
    draw.rectangle((0, H - 20, W, H), fill=RED)
    draw.rectangle((0, 20, 24, H - 20), fill=RED)

    draw_slash(canvas, (660, -130), 84, 920, DEEP_BLUE, degrees=11, alpha=220)
    draw_slash(canvas, (722, -110), 54, 880, CREAM, degrees=11, alpha=210)
    draw_slash(canvas, (772, -105), 92, 870, RED, degrees=11, alpha=245)
    draw_slash(canvas, (858, -120), 220, 900, DARK_RED, degrees=11, alpha=180)

    # A few precise 90s notes, restrained to the black field.
    for x, y, r, color in [
        (76, 78, 8, BLUE), (158, 538, 7, GREEN), (512, 84, 7, YELLOW),
        (590, 518, 8, RED), (1112, 128, 7, BLUE), (1080, 540, 9, RED),
    ]:
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)
    draw.line((92, 486, 150, 522), fill=YELLOW, width=6)
    draw.line((410, 70, 480, 110), fill=BLUE, width=6)
    draw.line((1020, 84, 1075, 55), fill=RED, width=6)


def build_card():
    card = Image.new("RGBA", (650, 500), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, 650, 500), radius=26, fill=PAPER)
    d.rounded_rectangle((18, 18, 632, 482), radius=18, outline=INK, width=2)
    d.line((44, 94, 606, 94), fill=RED, width=5)
    d.line((44, 110, 410, 110), fill=BLUE, width=4)

    d.rounded_rectangle((44, 42, 242, 76), radius=17, fill=INK)
    center_text(d, (44, 42, 242, 76), "CLASS OF 2026", font(SANS_BOLD, 18), CREAM)

    d.text((44, 142), "Isaac", font=font(SERIF_BOLD, 70), fill=INK)
    d.text((44, 222), "Andress Martinez", font=fit_text(d, "Andress Martinez", 552, SERIF_BOLD, 56), fill=INK)
    d.text((48, 305), "Graduation Party", font=font(SANS_BLACK, 38), fill=RED)

    d.text((50, 368), "Saturday", font=font(SANS_BOLD, 21), fill=INK)
    d.text((50, 399), "June 6, 2026", font=font(SERIF_BOLD, 31), fill=INK)
    d.rounded_rectangle((284, 372, 418, 424), radius=12, fill=INK)
    center_text(d, (284, 372, 418, 424), "2:00 PM", font(SANS_BOLD, 25), CREAM)
    d.rounded_rectangle((438, 372, 604, 424), radius=12, fill=CREAM, outline=INK, width=2)
    center_text(d, (438, 372, 604, 424), "EAGLE MTN, UT", font(SANS_BOLD, 18), INK)

    d.text((50, 450), "izzysgraduation.com", font=font(SANS_BOLD, 21), fill=INK)
    d.rectangle((468, 444, 604, 449), fill=RED)
    d.rectangle((468, 456, 570, 461), fill=BLUE)
    return card


canvas = Image.new("RGBA", (W, H), BLACK + (255,))
draw = ImageDraw.Draw(canvas)
draw_background(draw, canvas)

# Card shadow and card.
card = build_card()
shadow = Image.new("RGBA", card.size, BLACK + (120,))
shadow.putalpha(card.getchannel("A").filter(ImageFilter.GaussianBlur(18)))
canvas.alpha_composite(shadow, (74, 75))
canvas.alpha_composite(card, (58, 58))

# Portrait module.
portrait = duotone_portrait()
panel = Image.new("RGBA", (444, 548), (0, 0, 0, 0))
pd = ImageDraw.Draw(panel)
pd.rounded_rectangle((16, 18, 440, 544), radius=34, fill=BLACK)
pd.rounded_rectangle((0, 0, 424, 524), radius=34, fill=CREAM)
pd.rounded_rectangle((16, 16, 408, 508), radius=26, fill=BLACK)
panel.alpha_composite(portrait.resize((374, 456), Image.Resampling.LANCZOS), (25, 27))
pd.rounded_rectangle((25, 27, 399, 483), radius=26, outline=CREAM, width=4)
canvas.alpha_composite(panel, (722, 48))

# Small motorsport date badge overlapping both modules.
badge = Image.new("RGBA", (214, 118), (0, 0, 0, 0))
bd = ImageDraw.Draw(badge)
bd.rounded_rectangle((12, 14, 210, 114), radius=16, fill=RED)
bd.rounded_rectangle((0, 0, 198, 100), radius=16, fill=CREAM, outline=INK, width=4)
bd.text((24, 13), "06", font=font(IMPACT, 66), fill=INK)
bd.text((112, 60), "SAT", font=font(SANS_BLACK, 24), fill=INK)
paste_rotated(canvas, badge, (630, 464), -4)

# Professional corner mark.
draw.rounded_rectangle((42, 32, 128, 112), radius=8, fill=RED, outline=CREAM, width=4)
center_text(draw, (42, 35, 128, 78), "26", font(SANS_BLACK, 34), CREAM)
center_text(draw, (42, 78, 128, 108), "GRAD", font(SANS_BOLD, 17), CREAM)

canvas.convert("RGB").save(OUT, quality=94, optimize=True, progressive=True)
print(OUT)
