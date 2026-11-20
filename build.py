#!/usr/bin/env python3
"""Build the news-image-20261120 variant A front page.

Composites five generated images (hero + four story panels) with all text
drawn in code (PIL + Noto Sans), so no text can garble inside generated art.
Deterministic: fixed inputs, fixed layout, fixed JPEG quality.
Writes assets/final.png (JPEG bytes; the entry program copies it verbatim).
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

W, H = 1024, 1024
PAPER = (251, 248, 241)
NAVY = (18, 35, 61)
GOLD = (216, 169, 78)
RED = (176, 42, 30)
INK = (26, 26, 26)
GREY = (90, 90, 90)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/noto"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_KICKER = font("NotoSans-Bold.ttf", 20)
F_DATE = font("NotoSans-Bold.ttf", 54)
F_HERO_HEAD = font("NotoSans-Bold.ttf", 33)
F_HERO_SUB = font("NotoSans-Regular.ttf", 20)
F_P_KICKER = font("NotoSans-Bold.ttf", 14)
F_P_HEAD = font("NotoSans-Bold.ttf", 21)
F_P_SUB = font("NotoSans-Regular.ttf", 15)
F_TICKER = font("NotoSans-Regular.ttf", 17)
F_TICKER_B = font("NotoSans-Bold.ttf", 17)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by measured pixel width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def crop_to(img, tw, th, focus_x=0.5, focus_y=0.5):
    """Crop an image to the target aspect (around a focus point), then resize."""
    iw, ih = img.size
    ta, ia = tw / th, iw / ih
    if ia > ta:  # too wide: crop sides
        nw = int(ih * ta)
        cx = int(iw * focus_x)
        x0 = max(0, min(iw - nw, cx - nw // 2))
        img = img.crop((x0, 0, x0 + nw, ih))
    else:  # too tall: crop top/bottom
        nh = int(iw / ta)
        cy = int(ih * focus_y)
        y0 = max(0, min(ih - nh, cy - nh // 2))
        img = img.crop((0, y0, iw, y0 + nh))
    return img.resize((tw, th), Image.LANCZOS)


def main():
    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page, "RGBA")

    # ---- Masthead -------------------------------------------------------
    d.rectangle([0, 0, W, 104], fill=NAVY)
    kicker = "THE WORLD IN ONE DAY"
    d.text(((W - d.textlength(kicker, font=F_KICKER)) / 2, 12),
           kicker, font=F_KICKER, fill=GOLD)
    date = "FRIDAY 20 NOVEMBER 2026"
    d.text(((W - d.textlength(date, font=F_DATE)) / 2, 38),
           date, font=F_DATE, fill=WHITE)
    d.rectangle([0, 104, W, 108], fill=GOLD)

    # ---- Hero -----------------------------------------------------------
    hero = Image.open(os.path.join(ASSETS, "media-generation-hero-summit-0-1928f595-3a7b-4c00-86e3-c9e9c98973b0.webp")).convert("RGB")
    hero = crop_to(hero, 1024, 448)
    page.paste(hero, (0, 108))
    # caption strip over the bottom of the hero
    d.rectangle([0, 470, W, 556], fill=(10, 18, 32, 215))
    head = "TRUMP, XI & PUTIN MEET IN SHENZHEN"
    d.text((28, 480), head, font=F_HERO_HEAD, fill=WHITE)
    sub = "First-ever trilateral summit — global security and nuclear arms control on the agenda"
    d.text((28, 520), sub, font=F_HERO_SUB, fill=(225, 225, 225))

    # ---- Story panels (2 x 2) -------------------------------------------
    panels = [
        ("media-generation-panel-whitehouse-0-4064be10-e17e-44f6-bd2d-f824d8e3d4ae.webp",
         "WASHINGTON",
         "TRUMP PUSHES IRAN DECISION TO 2027",
         "He'll \u201csee what happens\u201d after Jan 1 \u2014 no rush on the call.",
         0.5),
        ("media-generation-panel-icj-0-4e192a44-1857-426f-beab-a9ecc57e6544.webp",
         "THE HAGUE",
         "ICJ: MYANMAR COMMITTED GENOCIDE",
         "Top UN court finds the military likely meant to destroy a substantial part of the Rohingya in 2017.",
         0.5),
        ("media-generation-panel-voyager-0-2fef72ca-e2db-4a60-9472-db8b3bb6a75b.webp",
         "DEEP SPACE",
         "VOYAGER 1 REACHES A LIGHT-DAY",
         "NASA confirms the probe is now a light-day from Earth, almost 50 years after launch.",
         0.22),
        ("media-generation-panel-cyclone-0-aa3564dc-f00f-44bf-8234-d9ed0597516a.webp",
         "INDIA",
         "CYCLONE AKVAN BEARS DOWN ON ODISHA",
         "About 300,000 people evacuated as the storm nears landfall.",
         0.5),
    ]
    # panel grid: x0 in {0, 512}, y0 in {556, 772}; each 512 x 216
    for i, (fname, kicker, head, sub, focus) in enumerate(panels):
        x0 = (i % 2) * 512
        y0 = 556 + (i // 2) * 216
        img = Image.open(os.path.join(ASSETS, fname)).convert("RGB")
        img = crop_to(img, 196, 216, focus_x=focus)
        page.paste(img, (x0, y0))
        tx = x0 + 212
        tw = 512 - 212 - 16
        d.text((tx, y0 + 12), kicker, font=F_P_KICKER, fill=RED)
        y = y0 + 36
        for line in wrap(d, head, F_P_HEAD, tw):
            d.text((tx, y), line, font=F_P_HEAD, fill=INK)
            y += 25
        y += 4
        for line in wrap(d, sub, F_P_SUB, tw):
            d.text((tx, y), line, font=F_P_SUB, fill=GREY)
            y += 20
    # panel dividers
    d.line([512, 556, 512, 988], fill=(200, 192, 178), width=2)
    d.line([0, 772, W, 772], fill=(200, 192, 178), width=2)
    d.line([0, 556, W, 556], fill=(200, 192, 178), width=2)

    # ---- Footer ticker --------------------------------------------------
    d.rectangle([0, 988, W, H], fill=NAVY)
    label = "ALSO TODAY:  "
    body = ("GTA 6 sales pass $1.8bn   \u00b7   Europe ready for talks with Russia on Ukraine"
            "   \u00b7   Houthis attack Riyadh")
    lw = d.textlength(label, font=F_TICKER_B)
    bw = d.textlength(body, font=F_TICKER)
    x = (W - lw - bw) / 2
    d.text((x, 1003), label, font=F_TICKER_B, fill=GOLD)
    d.text((x + lw, 1003), body, font=F_TICKER, fill=WHITE)

    out = os.path.join(ASSETS, "final.png")
    page.save(out, format="JPEG", quality=88, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
