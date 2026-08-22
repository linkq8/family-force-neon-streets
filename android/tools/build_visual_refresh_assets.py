#!/usr/bin/env python3
"""Build the v0.34 visual refresh from approved still-image masters."""

from __future__ import annotations

from collections import deque
from pathlib import Path
import shutil

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "android/app/src/main/assets"
GENERATED = Path("/Users/essa/.codex/generated_images/01a00986-8925-76e1-bc45-900310ee9065")

PANORAMAS = {
    "exec-242fc468-aae1-4b8d-8a29-7c82f5f36320.png": "stage_market.png",
    "exec-c18565e1-94e5-46e5-b02c-1adc2e5466fb.png": "stage_transit.png",
    "exec-35b4ceec-481e-431a-9043-472ad44a7526.png": "stage_harbor.png",
    "exec-1303ea67-f74a-4426-9330-9fe257ba0c7b.png": "stage_palace.png",
}
PORTRAITS = {
    "exec-6a1535f2-1330-4e3f-97e0-3b671647ecdb.png": "parent",
    "exec-7dfebc2b-3cbc-486e-9047-f4ab04b4c482.png": "adam",
    "exec-8d24404a-5bcb-4b89-8667-a1646205c013.png": "shaikha",
    "exec-9adb98c8-c6a5-45cf-8b2f-9ebcf876e4e3.png": "sulaiman",
}
ENEMIES = {
    "exec-bc32f70d-972a-4794-ba71-fe22776292d7.png": "striker",
    "exec-b8bdd31d-5eda-4a04-bc99-665968566f78.png": "shield_guard",
}


def neutral_checker(pixel: tuple[int, int, int]) -> bool:
    return max(pixel) - min(pixel) <= 24 and min(pixel) >= 155


def remove_checker(image: Image.Image) -> Image.Image:
    """Remove bright neutral checker paper while preserving colored highlights."""
    rgb = image.convert("RGB")
    width, height = rgb.size
    src = rgb.load()
    outside = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()

    def seed(x: int, y: int) -> None:
        index = y * width + x
        if not outside[index] and neutral_checker(src[x, y]):
            outside[index] = 1
            queue.append((x, y))

    for x in range(width):
        seed(x, 0)
        seed(x, height - 1)
    for y in range(height):
        seed(0, y)
        seed(width - 1, y)
    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height:
                index = ny * width + nx
                if not outside[index] and neutral_checker(src[nx, ny]):
                    outside[index] = 1
                    queue.append((nx, ny))

    # Grid paper is made from several disconnected neutral squares. Clear all
    # bright neutral pixels, then slightly close the subject mask to retain thin
    # antialiased outlines without letting checker fragments survive.
    alpha = Image.new("L", rgb.size, 255)
    alpha.putdata([
        0 if outside[i] or neutral_checker(pixel) else 255
        for i, pixel in enumerate(rgb.getdata())
    ])
    alpha = alpha.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    rgba = rgb.convert("RGBA")
    rgba.putalpha(alpha)
    return rgba


def normalize_enemy_sheet(source: Path, output: Path) -> None:
    image = remove_checker(Image.open(source))
    if output.stem == "striker_anim":
        # The approved Striker sheet returned on a 2:3 canvas although its
        # actual 6x6 board occupies a 1:1.2 region near the top.
        image = image.crop((0, 120, image.width, 1320))
    canvas = Image.new("RGBA", (960, 1152), (0, 0, 0, 0))
    for row in range(6):
        for col in range(6):
            x0 = round(col * image.width / 6)
            x1 = round((col + 1) * image.width / 6)
            y0 = round(row * image.height / 6)
            y1 = round((row + 1) * image.height / 6)
            cell = image.crop((x0, y0, x1, y1))
            bbox = cell.getchannel("A").getbbox()
            if bbox is None:
                continue
            actor = cell.crop(bbox)
            scale = min(132 / actor.width, 160 / actor.height, 1.0)
            size = (max(1, round(actor.width * scale)), max(1, round(actor.height * scale)))
            actor = actor.resize(size, Image.Resampling.LANCZOS)
            # Fine local contrast survives the 75% TV atlas without returning
            # to the oversized nearest-neighbour blocks of the old enemies.
            color = actor.convert("RGB").filter(
                ImageFilter.UnsharpMask(radius=0.55, percent=110, threshold=2)
            )
            color.putalpha(actor.getchannel("A"))
            actor = color
            hard_alpha = actor.getchannel("A").point(lambda value: 255 if value >= 96 else 0)
            actor.putalpha(hard_alpha)
            clean_actor = Image.new("RGBA", actor.size, (0, 0, 0, 0))
            clean_actor.alpha_composite(actor)
            actor = clean_actor
            dx = col * 160 + (160 - actor.width) // 2
            dy = row * 192 + 177 - actor.height
            canvas.alpha_composite(actor, (dx, dy))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, optimize=True)

    idle = canvas.crop((0, 0, 160, 192))
    fallback = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    bbox = idle.getchannel("A").getbbox()
    if bbox:
        actor = idle.crop(bbox)
        scale = min(390 / actor.width, 440 / actor.height)
        actor = actor.resize((round(actor.width * scale), round(actor.height * scale)),
                             Image.Resampling.LANCZOS)
        fallback.alpha_composite(actor, ((512 - actor.width) // 2, 476 - actor.height))
    fallback.save(output.with_name(output.stem.replace("_anim", "") + ".png"), optimize=True)


def centered_square(image: Image.Image) -> Image.Image:
    edge = min(image.width, image.height)
    left = (image.width - edge) // 2
    top = (image.height - edge) // 2
    return image.crop((left, top, left + edge, top + edge))


def split_portraits(source: Path, name: str) -> None:
    image = Image.open(source).convert("RGBA")
    # Most masters are 2:1. Essa was returned as a square with the two cards in
    # its central horizontal band, so crop the band before the equal split.
    if image.width / image.height < 1.65:
        band_h = image.width // 2
        top = (image.height - band_h) // 2
        image = image.crop((0, top, image.width, top + band_h))
    mid = image.width // 2
    halves = (image.crop((0, 0, mid, image.height)),
              image.crop((mid, 0, image.width, image.height)))
    for suffix, half in zip(("", "_ready"), halves):
        portrait = centered_square(half).resize((256, 256), Image.Resampling.LANCZOS)
        portrait = portrait.filter(ImageFilter.UnsharpMask(radius=0.55, percent=95, threshold=2))
        # A compact 192-color palette keeps the modern-retro finish coherent
        # without imposing the old 2x2 blocks that erased facial expressions.
        portrait = portrait.convert("RGB").quantize(colors=192, method=Image.Quantize.MEDIANCUT,
                                                      dither=Image.Dither.FLOYDSTEINBERG).convert("RGBA")
        mask = Image.new("L", (256, 256), 0)
        ImageDraw.Draw(mask).rounded_rectangle((8, 8, 247, 247), radius=22, fill=255)
        portrait.putalpha(mask)
        clean = Image.new("RGBA", portrait.size, (0, 0, 0, 0))
        clean.alpha_composite(portrait)
        portrait = clean
        output = ASSETS / f"heroes/{name}_portrait{suffix}.png"
        output.parent.mkdir(parents=True, exist_ok=True)
        portrait.save(output, optimize=True)


def main() -> None:
    for source_name, output_name in PANORAMAS.items():
        source = GENERATED / source_name
        output = ASSETS / "backgrounds/panoramas" / output_name
        output.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(source) as image:
            assert image.size == (2172, 724)
            image.convert("RGB").save(output, optimize=True)

    for source_name, hero in PORTRAITS.items():
        split_portraits(GENERATED / source_name, hero)

    for source_name, enemy in ENEMIES.items():
        normalize_enemy_sheet(GENERATED / source_name,
                              ASSETS / f"enemies/{enemy}_anim.png")

    icon_source = ROOT / "android/tools/visual_refresh_sources/icon_master.png"
    icon_source.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(GENERATED / "exec-3209d786-db2d-40a3-bc14-c9b018cc1e30.png",
                    icon_source)
    print("Built 4 panoramas, 8 portraits, 2 enemy atlases, and the icon master")


if __name__ == "__main__":
    main()
