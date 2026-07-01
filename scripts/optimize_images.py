#!/usr/bin/env python3
"""Compress gallery images and generate favicon + OG preview."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"


def compress_jpegs():
    for path in sorted(IMAGES.glob("photo-*.jpg")):
        img = Image.open(path).convert("RGB")
        img.save(path, "JPEG", quality=82, optimize=True, progressive=True)
        print(f"compressed {path.name}")


def crop_cover(img: Image.Image, width: int, height: int) -> Image.Image:
    src_w, src_h = img.size
    target_ratio = width / height
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        box = (left, 0, left + new_w, src_h)
    else:
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        box = (0, top, src_w, top + new_h)

    return img.crop(box).resize((width, height), Image.Resampling.LANCZOS)


def create_og_image():
    base = Image.open(IMAGES / "photo-01.jpg").convert("RGB")
    canvas = crop_cover(base, 1200, 630)

    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, 1200, 630), fill=(20, 16, 14, 70))

    title = "Вероника Мочалова"
    subtitle = "Личная страница · Фотогалерея"

    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    except OSError:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    draw.text((72, 250), title, font=title_font, fill=(255, 255, 255, 255))
    draw.text((72, 340), subtitle, font=subtitle_font, fill=(245, 235, 225, 255))

    result = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    out = IMAGES / "og-image.jpg"
    result.save(out, "JPEG", quality=88, optimize=True, progressive=True)
    print(f"created {out.name}")


def create_icons():
    base = Image.open(IMAGES / "photo-01.jpg").convert("RGB")
    square = crop_cover(base, 512, 512)

    square.resize((180, 180), Image.Resampling.LANCZOS).save(
        IMAGES / "apple-touch-icon.png", "PNG", optimize=True
    )

    for size in (32, 16):
        square.resize((size, size), Image.Resampling.LANCZOS).save(
            IMAGES / f"favicon-{size}x{size}.png", "PNG", optimize=True
        )

    favicon = Image.open(IMAGES / "favicon-32x32.png")
    favicon.save(IMAGES / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32)])
    print("created favicon + apple-touch-icon")


if __name__ == "__main__":
    compress_jpegs()
    create_og_image()
    create_icons()