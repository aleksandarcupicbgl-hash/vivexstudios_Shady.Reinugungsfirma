#!/usr/bin/env python3
"""
Bereitet das Logo für die Website vor.

Aufruf (im Projektordner):   python3 tools/logo-vorbereiten.py
Voraussetzung:               pip install pillow

Was passiert:
  1. liest logo.png (Projektordner) ein
  2. ermittelt die exakte Blau-Farbe (häufigste gesättigte Blau-Farbe im Logo)
     und trägt sie als --accent in assets/css/style.css ein
  3. erzeugt:
       assets/img/logo.png              Logo für das dunkle Badge im Header
       assets/img/logo-transparent.png  freigestellte Version (schwarz -> transparent)
       assets/img/favicon-32.png, favicon-192.png, apple-touch-icon.png
       assets/img/og-image.png          Vorschaubild für Social Media (1200x630)

Ohne logo.png wird ein neutrales Platzhalter-Monogramm „CD“ erzeugt.
"""
import colorsys
import re
import sys
from collections import Counter
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow fehlt – bitte zuerst ausführen:  pip install pillow")

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "logo.png"
OUT = ROOT / "assets" / "img"
CSS = ROOT / "assets" / "css" / "style.css"
FONT = ROOT / "assets" / "fonts" / "inter-latin-var.woff2"
BLACK = (11, 13, 18)          # Badge-Hintergrund (#0B0D12)
TEXT = (26, 31, 43)           # #1A1F2B
DEFAULT_ACCENT = (0x4A, 0x8F, 0xE7)


def font(size, weight=700):
    try:
        f = ImageFont.truetype(str(FONT), size)
        f.set_variation_by_axes([weight])
        return f
    except Exception:
        return ImageFont.load_default()


def placeholder_logo():
    img = Image.new("RGBA", (512, 512), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    d.text((256, 256), "CD", font=font(250, 800), fill=DEFAULT_ACCENT + (255,), anchor="mm")
    return img


def find_blue(img):
    small = img.convert("RGBA").copy()
    small.thumbnail((400, 400), Image.NEAREST)  # NEAREST: keine Mischfarben
    counts = Counter()
    data = small.tobytes()
    for i in range(0, len(data), 4):
        r, g, b, a = data[i:i + 4]
        if a < 200:
            continue
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if 0.52 <= h <= 0.72 and s >= 0.35 and v >= 0.35:
            counts[(r, g, b)] += 1
    if not counts:
        return None
    # häufigste Farbe; nahe Nachbarn (Kantenglättung) zusammenfassen
    top, _ = counts.most_common(1)[0]
    near = [(c, n) for c, n in counts.items() if sum(abs(c[i] - top[i]) for i in range(3)) <= 12]
    total = sum(n for _, n in near)
    return tuple(round(sum(c[i] * n for c, n in near) / total) for i in range(3))


def content_bbox(img, threshold=28):
    """Begrenzungsrahmen aller nicht-schwarzen / nicht-transparenten Pixel."""
    rgba = img.convert("RGBA")
    mask = Image.new("L", rgba.size, 0)
    px, mp = rgba.load(), mask.load()
    w, h = rgba.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 20 and max(r, g, b) > threshold:
                mp[x, y] = 255
    return mask.getbbox() or (0, 0, w, h)


def emblem_bbox(img, threshold=40):
    """Größter zusammenhängender Zeilenblock (Bildmarke ohne Schriftzug darunter)."""
    gray = img.convert("L").point(lambda v: 255 if v > threshold else 0)
    w, h = gray.size
    rows = [gray.crop((0, y, w, y + 1)).getbbox() is not None for y in range(h)]
    bands, start = [], None
    for y, on in enumerate(rows + [False]):
        if on and start is None:
            start = y
        elif not on and start is not None:
            bands.append((start, y))
            start = None
    if not bands:
        return (0, 0, w, h)
    top, bottom = max(bands, key=lambda b: b[1] - b[0])
    box = gray.crop((0, top, w, bottom)).getbbox()
    return (box[0], top, box[2], bottom)


def make_transparent(img):
    """Schwarzen Hintergrund entfernen (Alpha aus Helligkeit, Farben entmultipliziert)."""
    rgba = img.convert("RGBA")
    out = Image.new("RGBA", rgba.size)
    src, dst = rgba.load(), out.load()
    w, h = rgba.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = src[x, y]
            m = max(r, g, b)
            if m < 10 or a == 0:
                dst[x, y] = (0, 0, 0, 0)
                continue
            alpha = m / 255
            dst[x, y] = (min(255, round(r / alpha)), min(255, round(g / alpha)),
                         min(255, round(b / alpha)), round(a * alpha))
    return out


def on_black_square(img, size, pad_ratio=0.12, radius_ratio=0.0):
    w, h = img.size
    side = max(w, h)
    canvas = Image.new("RGBA", (side, side), BLACK + (255,))
    canvas.alpha_composite(img, ((side - w) // 2, (side - h) // 2))
    inner = round(size * (1 - 2 * pad_ratio))
    canvas = canvas.resize((inner, inner), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg = Image.new("RGBA", (size, size), BLACK + (255,))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius=round(size * radius_ratio), fill=255)
    out.paste(bg, (0, 0), mask)
    off = (size - inner) // 2
    out.alpha_composite(canvas, (off, off))
    return out


def og_image(logo_trans, accent):
    W, H = 1200, 630
    img = Image.new("RGBA", (W, H), (247, 249, 252, 255))
    d = ImageDraw.Draw(img)
    d.rectangle((0, H - 14, W, H), fill=accent + (255,))
    badge = on_black_square(logo_trans, 300, pad_ratio=0.1, radius_ratio=0.16)
    img.alpha_composite(badge, (110, (H - 300) // 2 - 7))
    x = 470
    d.text((x, 225), "CD Reinigungsservice", font=font(64, 750), fill=TEXT + (255,))
    d.text((x, 315), "Sauberkeit, auf die Sie zählen können.", font=font(34, 500), fill=(90, 98, 114, 255))
    d.text((x, 385), "0176 72883621", font=font(34, 650), fill=accent + (255,))
    return img.convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if SRC.exists():
        src = Image.open(SRC).convert("RGBA")
        is_placeholder = False
        print(f"Logo gefunden: {SRC.name} ({src.width}x{src.height})")
    else:
        src = placeholder_logo()
        is_placeholder = True
        print("Keine logo.png gefunden – erzeuge Platzhalter-Monogramm „CD“.")

    accent = find_blue(src) or DEFAULT_ACCENT
    hex_accent = "#{:02X}{:02X}{:02X}".format(*accent)
    print(f"Blau-Farbe aus dem Logo: {hex_accent}")

    if not is_placeholder:
        css = CSS.read_text(encoding="utf-8")
        css, n = re.subn(r"--accent:\s*#[0-9A-Fa-f]{6};\s*/\* LOGO-BLAU \*/",
                         f"--accent: {hex_accent}; /* LOGO-BLAU */", css)
        if n:
            CSS.write_text(css, encoding="utf-8")
            print(f"--accent in style.css auf {hex_accent} gesetzt.")

    cropped = src.crop(content_bbox(src))
    transparent = make_transparent(cropped)
    transparent.save(OUT / "logo-transparent.png", optimize=True)

    # Vollständiges Logo (Hero), auf Badge-Schwarz
    pad = round(max(cropped.size) * 0.07)
    full = Image.new("RGBA", (cropped.width + 2 * pad, cropped.height + 2 * pad), BLACK + (255,))
    full.alpha_composite(transparent, (pad, pad))
    full.thumbnail((1000, 1000), Image.LANCZOS)
    full.convert("RGB").save(OUT / "logo-full.jpg", quality=86, optimize=True)

    # Bildmarke ohne Schriftzug (Header-Badge, Favicons), max. 192px hoch für Retina
    emblem = make_transparent(cropped.crop(emblem_bbox(cropped)))
    badge = Image.new("RGBA", emblem.size, BLACK + (255,))
    badge.alpha_composite(emblem)
    badge.thumbnail((576, 192), Image.LANCZOS)
    badge.convert("RGB").save(OUT / "logo.png", optimize=True)

    on_black_square(emblem, 32, pad_ratio=0.02, radius_ratio=0.2).save(OUT / "favicon-32.png", optimize=True)
    on_black_square(emblem, 192, pad_ratio=0.05, radius_ratio=0.2).save(OUT / "favicon-192.png", optimize=True)
    on_black_square(emblem, 180, pad_ratio=0.08).convert("RGB").save(OUT / "apple-touch-icon.png", optimize=True)
    og_image(emblem, accent).save(OUT / "og-image.png", optimize=True)
    print("Bilder erzeugt in assets/img/.")


if __name__ == "__main__":
    main()
