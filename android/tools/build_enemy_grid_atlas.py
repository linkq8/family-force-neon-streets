#!/usr/bin/env python3
"""Turn one ImageGen 6x6 enemy sheet into a stable Android runtime atlas.

The source may contain a baked neutral checker.  The builder removes only the
checker connected to each panel edge, locks one global scale across all poses,
anchors every sprite to the same floor line, and rejects panel clipping.
"""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
from pathlib import Path

from PIL import Image


COLS = ROWS = 6
CELL_W, CELL_H = 160, 192
SAFE_W, SAFE_H = 132, 164
SAFE_BOTTOM = 12


def neutral_checker(pixel: tuple[int, int, int]) -> bool:
    red, green, blue = pixel
    return min(pixel) >= 208 and max(pixel) - min(pixel) <= 22


def remove_edge_checker(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()
    outside = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()
    for x in range(width):
        queue.extend(((x, 0), (x, height - 1)))
    for y in range(height):
        queue.extend(((0, y), (width - 1, y)))
    while queue:
        x, y = queue.popleft()
        index = y * width + x
        if outside[index] or not neutral_checker(pixels[x, y]):
            continue
        outside[index] = 1
        if x: queue.append((x - 1, y))
        if x + 1 < width: queue.append((x + 1, y))
        if y: queue.append((x, y - 1))
        if y + 1 < height: queue.append((x, y + 1))
    rgba = rgb.convert("RGBA")
    data = list(rgba.getdata())
    for index, is_outside in enumerate(outside):
        if is_outside:
            data[index] = (0, 0, 0, 0)
    rgba.putdata(data)
    return rgba


def hard_alpha(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    rgba.putdata([(r, g, b, 255) if a >= 80 else (0, 0, 0, 0)
                  for r, g, b, a in rgba.getdata()])
    return rgba


def largest_component(image: Image.Image) -> Image.Image:
    rgba = hard_alpha(image)
    alpha = rgba.getchannel("A")
    pixels = alpha.load()
    width, height = rgba.size
    seen = bytearray(width * height)
    largest: list[tuple[int, int]] = []
    for sy in range(height):
        for sx in range(width):
            start = sy * width + sx
            if seen[start] or not pixels[sx, sy]:
                continue
            component: list[tuple[int, int]] = []
            queue = deque([(sx, sy)])
            seen[start] = 1
            while queue:
                x, y = queue.popleft()
                component.append((x, y))
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if not (0 <= nx < width and 0 <= ny < height):
                        continue
                    index = ny * width + nx
                    if seen[index] or not pixels[nx, ny]:
                        continue
                    seen[index] = 1
                    queue.append((nx, ny))
            if len(component) > len(largest):
                largest = component
    if not largest:
        raise ValueError("empty frame after checker removal")
    mask = Image.new("L", rgba.size, 0)
    mask_pixels = mask.load()
    for x, y in largest:
        mask_pixels[x, y] = 255
    result = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    result.paste(rgba, (0, 0), mask)
    return result


def split_grid(source: Image.Image) -> list[Image.Image]:
    frames = []
    for row in range(ROWS):
        top = round(source.height * row / ROWS)
        bottom = round(source.height * (row + 1) / ROWS)
        for column in range(COLS):
            left = round(source.width * column / COLS)
            right = round(source.width * (column + 1) / COLS)
            panel = remove_edge_checker(source.crop((left, top, right, bottom)))
            inset_x = max(2, round(panel.width * .025))
            inset_y = max(2, round(panel.height * .018))
            clean = Image.new("RGBA", panel.size, (0, 0, 0, 0))
            clean.alpha_composite(panel.crop((inset_x, inset_y,
                                              panel.width - inset_x,
                                              panel.height - inset_y)),
                                  (inset_x, inset_y))
            frames.append(largest_component(clean))
    return frames


def build(source_path: Path) -> Image.Image:
    frames = split_grid(Image.open(source_path))
    boxes = [frame.getchannel("A").getbbox() for frame in frames]
    if not all(boxes):
        raise ValueError("one or more empty frames")
    widths = [box[2] - box[0] for box in boxes if box]
    heights = [box[3] - box[1] for box in boxes if box]
    scale = min(SAFE_W / max(widths), SAFE_H / max(heights))
    atlas = Image.new("RGBA", (CELL_W * COLS, CELL_H * ROWS), (0, 0, 0, 0))
    for index, (frame, box) in enumerate(zip(frames, boxes)):
        assert box is not None
        actor = frame.crop(box)
        target = (max(2, round(actor.width * scale)), max(2, round(actor.height * scale)))
        actor = hard_alpha(actor.resize(target, Image.Resampling.LANCZOS))
        cell = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
        x = (CELL_W - actor.width) // 2
        y = CELL_H - SAFE_BOTTOM - actor.height
        if min(x, y, CELL_W - x - actor.width, CELL_H - y - actor.height) < 12:
            raise ValueError(f"unsafe frame {index}: actor={actor.size} at {(x, y)}")
        cell.alpha_composite(actor, (x, y))
        atlas.alpha_composite(cell, ((index % COLS) * CELL_W, (index // COLS) * CELL_H))
    validate(atlas)
    return atlas


def validate(atlas: Image.Image) -> None:
    if atlas.size != (960, 1152) or atlas.mode != "RGBA":
        raise ValueError(f"bad atlas contract: {atlas.mode} {atlas.size}")
    if any(a not in (0, 255) for *_, a in atlas.getdata()):
        raise ValueError("soft alpha present")
    for row in range(ROWS):
        hashes = set()
        for column in range(COLS):
            cell = atlas.crop((column * CELL_W, row * CELL_H,
                               (column + 1) * CELL_W, (row + 1) * CELL_H))
            box = cell.getchannel("A").getbbox()
            if not box or min(box[0], box[1], CELL_W - box[2], CELL_H - box[3]) < 12:
                raise ValueError(f"clipped cell {(row, column)}: {box}")
            hashes.add(hashlib.sha256(cell.tobytes()).digest())
        if len(hashes) < 3:
            raise ValueError(f"row {row} has only {len(hashes)} distinct frames")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--portrait", type=Path)
    args = parser.parse_args()
    atlas = build(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(args.output, optimize=True, compress_level=9)
    if args.portrait:
        idle = atlas.crop((0, 0, CELL_W, CELL_H))
        portrait = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        portrait.alpha_composite(idle.resize((320, 384), Image.Resampling.LANCZOS), (96, 104))
        args.portrait.parent.mkdir(parents=True, exist_ok=True)
        portrait.save(args.portrait, optimize=True, compress_level=9)
    print(f"built {args.output} from {args.source}")


if __name__ == "__main__":
    main()
