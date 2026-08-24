#!/usr/bin/env python3
"""Build base/runtime/TV enemy atlases from three approved 6x2 source sheets."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

from PIL import Image, ImageFilter

COLS, SOURCE_ROWS, OUTPUT_ROWS = 6, 2, 6
SHEETS = ("idle_walk.png", "attacks.png", "hurt_knockdown.png")
TIERS = {
    "base": ((160, 192), (132, 164), 12),
    "runtime": ((240, 288), (198, 246), 18),
}


def is_background(pixel: tuple[int, int, int]) -> bool:
    # Generated sheets use light-gray gradients that can fall well below 216.
    # This predicate is only flood-filled from panel edges, so the looser neutral
    # threshold removes the connected studio backdrop without erasing enclosed
    # white costume/paint details.
    return min(pixel) >= 180 and max(pixel) - min(pixel) <= 38


def remove_edge_background(panel: Image.Image) -> Image.Image:
    rgb = panel.convert("RGB")
    width, height = rgb.size
    source = rgb.load()
    outside = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()
    for x in range(width): queue.extend(((x, 0), (x, height - 1)))
    for y in range(height): queue.extend(((0, y), (width - 1, y)))
    while queue:
        x, y = queue.popleft()
        index = y * width + x
        if outside[index] or not is_background(source[x, y]):
            continue
        outside[index] = 1
        if x: queue.append((x - 1, y))
        if x + 1 < width: queue.append((x + 1, y))
        if y: queue.append((x, y - 1))
        if y + 1 < height: queue.append((x, y + 1))
    rgba = rgb.convert("RGBA")
    data = list(rgba.getdata())
    for index, clear in enumerate(outside):
        if clear: data[index] = (0, 0, 0, 0)
    rgba.putdata(data)
    return rgba


def hard_alpha(image: Image.Image, threshold: int = 72) -> Image.Image:
    rgba = image.convert("RGBA")
    rgba.putdata([(r, g, b, 255) if a >= threshold else (0, 0, 0, 0)
                  for r, g, b, a in rgba.getdata()])
    return rgba


def keep_character_and_effects(image: Image.Image) -> Image.Image:
    """Drop panel rules while retaining nearby authored hit/energy effects."""
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    width, height = rgba.size
    pixels = alpha.load()
    seen = bytearray(width * height)
    components: list[list[tuple[int, int]]] = []
    for sy in range(height):
        for sx in range(width):
            index = sy * width + sx
            if seen[index] or not pixels[sx, sy]: continue
            queue = deque([(sx, sy)]); seen[index] = 1; component = []
            while queue:
                x, y = queue.popleft(); component.append((x, y))
                for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                    if 0 <= nx < width and 0 <= ny < height:
                        ni = ny * width + nx
                        if not seen[ni] and pixels[nx, ny]:
                            seen[ni] = 1; queue.append((nx, ny))
            components.append(component)
    if not components: raise ValueError("empty frame")
    main = max(components, key=len)
    left = min(x for x, _ in main); right = max(x for x, _ in main)
    top = min(y for _, y in main); bottom = max(y for _, y in main)
    pad_x, pad_y = max(20, width // 8), max(24, height // 12)
    mask = Image.new("L", rgba.size, 0); out = mask.load()
    for component in components:
        if len(component) < 8: continue
        c_left = min(x for x, _ in component); c_right = max(x for x, _ in component)
        c_top = min(y for _, y in component); c_bottom = max(y for _, y in component)
        c_width, c_height = c_right - c_left + 1, c_bottom - c_top + 1
        # A detached component touching a source-panel edge is usually spill
        # from the neighbouring pose (impact star, speed line, or grid seam).
        if component is not main and (
            c_left <= 3 or c_top <= 3 or c_right >= width - 4 or c_bottom >= height - 4
        ):
            continue
        density = len(component) / (c_width * c_height)
        if density < .08 and (c_width > width * .45 or c_height > height * .45):
            continue
        if (c_width > width * .5 and c_height <= 14) or (c_height > height * .5 and c_width <= 14):
            continue
        nearby = c_right >= left - pad_x and c_left <= right + pad_x \
                and c_bottom >= top - pad_y and c_top <= bottom + pad_y
        if component is main or nearby:
            for x, y in component: out[x, y] = 255
    result = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    result.paste(rgba, (0, 0), mask)
    return result


def split_sheet(path: Path) -> list[Image.Image]:
    image = Image.open(path).convert("RGB")
    # Image generators may return a wide 3:1 sheet or a taller 3:2 sheet.
    # Judge source detail per panel, not by one fixed canvas aspect ratio.
    panel_width = image.width / COLS
    panel_height = image.height / SOURCE_ROWS
    if panel_width < 240 or panel_height < 240:
        raise ValueError(
            f"source cells are below 240x240: {path} {image.size} "
            f"cell={panel_width:.0f}x{panel_height:.0f}"
        )
    frames = []
    for row in range(SOURCE_ROWS):
        top, bottom = round(image.height * row / 2), round(image.height * (row + 1) / 2)
        for column in range(COLS):
            left, right = round(image.width * column / 6), round(image.width * (column + 1) / 6)
            inset_x, inset_y = max(4, (right - left) // 45), max(4, (bottom - top) // 70)
            panel = image.crop((left + inset_x, top + inset_y,
                                right - inset_x, bottom - inset_y))
            clean = keep_character_and_effects(hard_alpha(remove_edge_background(panel)))
            box = clean.getchannel("A").getbbox()
            if not box:
                raise ValueError(f"empty source frame: {path.name} r{row} c{column}")
            frames.append(clean.crop(box))
    return frames


def resize_actor(actor: Image.Image, size: tuple[int, int], clustered: bool) -> Image.Image:
    if clustered:
        half = (max(2, round(size[0] / 2)), max(2, round(size[1] / 2)))
        small = hard_alpha(actor.resize(half, Image.Resampling.LANCZOS))
        return small.resize((half[0] * 2, half[1] * 2), Image.Resampling.NEAREST)
    return hard_alpha(actor.resize(size, Image.Resampling.LANCZOS), 48)


def build_tier(frames: list[Image.Image], tier: str) -> Image.Image:
    cell, safe, bottom = TIERS[tier]
    # Calibrate the actor scale from idle/walk only. Attack effects and prone
    # silhouettes are naturally wider and must not shrink every standing pose.
    standing_widths, standing_heights = zip(*(frame.size for frame in frames[:12]))
    scale = min(safe[0] / max(standing_widths), safe[1] / max(standing_heights))
    atlas = Image.new("RGBA", (cell[0] * COLS, cell[1] * OUTPUT_ROWS), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        target = (max(2, round(frame.width * scale)), max(2, round(frame.height * scale)))
        # Only exceptional wide action/fall poses are reduced enough to retain
        # the mandatory gutter; normal standing scale remains invariant.
        fit = min(1.0, safe[0] / target[0], safe[1] / target[1])
        if fit < 1.0:
            target = (max(2, round(target[0] * fit)), max(2, round(target[1] * fit)))
        actor = resize_actor(frame, target, tier == "base")
        x = (cell[0] - actor.width) // 2
        y = cell[1] - bottom - actor.height
        if tier == "base":
            x &= ~1
            y &= ~1
        if min(x, y, cell[0] - x - actor.width, cell[1] - y - actor.height) < (8 if tier == "base" else 12):
            raise ValueError(f"unsafe {tier} frame {index}: {actor.size} at {(x, y)}")
        atlas.alpha_composite(actor, ((index % COLS) * cell[0] + x,
                                      (index // COLS) * cell[1] + y))
    return atlas


def save_png(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True, compress_level=9)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("enemy")
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("assets", type=Path)
    args = parser.parse_args()
    frames = []
    for sheet in SHEETS: frames.extend(split_sheet(args.source_dir / sheet))
    if len(frames) != 36: raise ValueError(len(frames))
    base = build_tier(frames, "base")
    runtime = build_tier(frames, "runtime")
    tv = runtime.resize((840, 1008), Image.Resampling.LANCZOS)
    rgb = tv.convert("RGB").filter(ImageFilter.UnsharpMask(radius=.65, percent=85, threshold=3))
    rgb.putalpha(tv.getchannel("A").point(lambda a: 255 if a >= 72 else 0))
    tv = rgb
    save_png(base, args.assets / "enemies" / f"{args.enemy}_anim.png")
    save_png(runtime, args.assets / "runtime/enemies" / f"{args.enemy}_anim.png")
    save_png(tv, args.assets / "tv/enemies" / f"{args.enemy}_anim.png")
    print(f"built strict tiers for {args.enemy}: base={base.size} runtime={runtime.size} tv={tv.size}")


if __name__ == "__main__":
    main()
