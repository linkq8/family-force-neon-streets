#!/usr/bin/env python3
"""Turn the keyed Higgsfield emblem into Android legacy and adaptive icons."""

from __future__ import annotations

from collections import deque
from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "assets" / "higgsfield" / "android" / "icon"
RES_DIR = ROOT / "android" / "app" / "src" / "main" / "res"
SOURCE = SOURCE_DIR / "icon_master_keyed.png"
MODERN_SOURCE = SOURCE_DIR / "icon_master_source.png"
TRACKED_MODERN_SOURCE = ROOT / "android/tools/visual_refresh_sources/icon_master.png"

DENSITIES = {
    "mdpi": (48, 108),
    "hdpi": (72, 162),
    "xhdpi": (96, 216),
    "xxhdpi": (144, 324),
    "xxxhdpi": (192, 432),
}


def is_key_blue(pixel: tuple[int, int, int]) -> bool:
    red, green, blue = pixel
    return blue >= 118 and blue - red >= 62 and blue - green >= 62


def remove_connected_key(image: Image.Image) -> Image.Image:
    """Clear only blue-screen pixels connected to an edge, preserving blue art."""
    rgb = image.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()
    background = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()

    def seed(x: int, y: int) -> None:
        index = y * width + x
        if not background[index] and is_key_blue(pixels[x, y]):
            background[index] = 1
            queue.append((x, y))

    for x in range(width):
        seed(x, 0)
        seed(x, height - 1)
    for y in range(1, height - 1):
        seed(0, y)
        seed(width - 1, y)

    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if nx < 0 or ny < 0 or nx >= width or ny >= height:
                continue
            index = ny * width + nx
            if not background[index] and is_key_blue(pixels[nx, ny]):
                background[index] = 1
                queue.append((nx, ny))

    rgba = rgb.convert("RGBA")
    rgba.putdata([
        (0, 0, 0, 0) if background[index] else (*pixel, 255)
        for index, pixel in enumerate(rgb.getdata())
    ])
    bbox = rgba.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("Blue-screen removal erased the complete emblem")
    return rgba.crop(bbox)


def place_subject(subject: Image.Image, extent: int) -> Image.Image:
    canvas = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    scale = min(extent / subject.width, extent / subject.height)
    size = (max(1, round(subject.width * scale)), max(1, round(subject.height * scale)))
    resized = subject.resize(size, Image.Resampling.NEAREST)
    x = (1024 - resized.width) // 2
    y = (1024 - resized.height) // 2
    canvas.alpha_composite(resized, (x, y))
    return canvas


def city_background() -> Image.Image:
    image = Image.new("RGBA", (1024, 1024), (9, 11, 38, 255))
    pixels = image.load()
    for y in range(1024):
        for x in range(1024):
            distance = min(1.0, ((x - 512) ** 2 + (y - 450) ** 2) ** 0.5 / 720)
            glow = 1.0 - distance
            pixels[x, y] = (
                round(9 + 10 * glow),
                round(11 + 25 * glow),
                round(38 + 56 * glow),
                255,
            )

    draw = ImageDraw.Draw(image)
    rng = random.Random(0x464F524345)
    x = 0
    while x < 1024:
        width = rng.choice((54, 66, 78, 90, 108))
        top = rng.choice((650, 690, 730, 770, 810))
        draw.rectangle((x, top, x + width, 1024), fill=(5, 7, 25, 255))
        if rng.random() < 0.35:
            draw.rectangle((x + width // 2 - 3, top - 34, x + width // 2 + 3, top),
                           fill=(10, 16, 51, 255))
        for wy in range(top + 24, 970, 48):
            for wx in range(x + 15, x + width - 8, 28):
                if rng.random() < 0.42:
                    draw.rectangle((wx, wy, wx + 7, wy + 10), fill=(245, 169, 66, 255))
        x += width
    return image


def rounded_legacy(subject: Image.Image) -> Image.Image:
    icon = city_background()
    icon.alpha_composite(place_subject(subject, 804))
    mask = Image.new("L", icon.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((18, 18, 1005, 1005), radius=218, fill=255)
    icon.putalpha(mask)
    return icon


def round_legacy(subject: Image.Image) -> Image.Image:
    icon = city_background()
    icon.alpha_composite(place_subject(subject, 760))
    mask = Image.new("L", icon.size, 0)
    ImageDraw.Draw(mask).ellipse((12, 12, 1011, 1011), fill=255)
    icon.putalpha(mask)
    return icon


def monochrome(source: Image.Image) -> Image.Image:
    alpha = source.getchannel("A")
    output = Image.new("RGBA", source.size, (255, 255, 255, 0))
    output.putalpha(alpha)
    return output


def save_png(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)


def main() -> None:
    modern_source = TRACKED_MODERN_SOURCE if TRACKED_MODERN_SOURCE.is_file() else MODERN_SOURCE
    if modern_source.is_file():
        master = Image.open(modern_source).convert("RGBA")
        # The approved master already contains the full enamel badge. Preserve
        # it as one subject and mask only its outer square corners.
        subject = master
        mask = Image.new("L", master.size, 0)
        inset = round(master.width * 0.035)
        ImageDraw.Draw(mask).ellipse((inset, inset, master.width - inset, master.height - inset), fill=255)
        subject.putalpha(mask)
    else:
        subject = remove_connected_key(Image.open(SOURCE))
    adaptive = place_subject(subject, 624)
    mono = monochrome(adaptive)
    legacy = rounded_legacy(subject)
    legacy_round = round_legacy(subject)

    save_png(subject, SOURCE_DIR / "icon_master.png")
    save_png(legacy, SOURCE_DIR / "icon_legacy_1024.png")
    save_png(adaptive.resize((432, 432), Image.Resampling.LANCZOS).filter(
                 ImageFilter.UnsharpMask(radius=0.55, percent=90, threshold=2)),
             SOURCE_DIR / "icon_adaptive_foreground_432.png")
    save_png(mono.resize((432, 432), Image.Resampling.LANCZOS),
             SOURCE_DIR / "icon_monochrome_432.png")
    save_png(legacy.resize((512, 512), Image.Resampling.LANCZOS),
             SOURCE_DIR / "icon_preview.png")

    for density, (legacy_size, adaptive_size) in DENSITIES.items():
        folder = RES_DIR / f"mipmap-{density}"
        save_png(legacy.resize((legacy_size, legacy_size), Image.Resampling.LANCZOS),
                 folder / "ic_launcher.png")
        save_png(legacy_round.resize((legacy_size, legacy_size), Image.Resampling.LANCZOS),
                 folder / "ic_launcher_round.png")
        save_png(adaptive.resize((adaptive_size, adaptive_size), Image.Resampling.LANCZOS),
                 folder / "ic_launcher_foreground.png")
        save_png(mono.resize((adaptive_size, adaptive_size), Image.Resampling.LANCZOS),
                 folder / "ic_launcher_monochrome.png")

    # Android TV launcher artwork has its own 16:9 contract and must not reuse
    # a square phone icon. Keep the badge at left and the existing transparent
    # game wordmark at right for legibility at couch distance.
    banner = city_background().resize((320, 180), Image.Resampling.LANCZOS)
    badge = legacy.resize((132, 132), Image.Resampling.LANCZOS)
    banner.alpha_composite(badge, (8, 24))
    logo_path = ROOT / "android/app/src/main/assets/ui/logo.png"
    if logo_path.is_file():
        logo = Image.open(logo_path).convert("RGBA")
        logo.thumbnail((174, 92), Image.Resampling.LANCZOS)
        banner.alpha_composite(logo, (140 + (174 - logo.width) // 2, (180 - logo.height) // 2))
    save_png(banner, RES_DIR / "drawable-nodpi/tv_banner.png")


if __name__ == "__main__":
    main()
