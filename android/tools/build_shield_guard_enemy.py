#!/usr/bin/env python3
"""Build the Shield Guard's TV-safe 36-frame runtime atlas from still sheets."""

from __future__ import annotations

from collections import deque
from pathlib import Path
import hashlib

from PIL import Image, ImageChops, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets/imagegen/android/enemies/shield_guard"
OUTPUT = ROOT / "android/app/src/main/assets/enemies"
ATLAS_SIZE = (960, 1152)
CELL_SIZE = (160, 192)
COLS, ROWS = 6, 6
SAFE_WIDTH = 132
SAFE_HEIGHT = 164
SAFE_BOTTOM = 12
SHEETS = (
    ("idle_walk.png", 0, 1),
    ("attacks.png", 2, 3),
    ("hurt_knockdown.png", 4, 5),
)

# The last baton frame contains a decorative detached baton. Hold the clean
# recovery key instead; this prevents a disconnected fragment in the atlas.
SAFE_FRAME_REMAP = {2: (0, 1, 2, 3, 3, 5)}


def foreground_candidates(image: Image.Image) -> Image.Image:
    """Return all likely enamel-art pixels before choosing a pose."""
    rgb = image.convert("RGB")
    rough = Image.new("L", rgb.size, 0)
    source = rgb.load()
    target = rough.load()
    for y in range(rgb.height):
        for x in range(rgb.width):
            r, g, b = source[x, y]
            saturation = max(r, g, b) - min(r, g, b)
            # Cyan/mint/coral/gold armour is separated strongly from the
            # low-luminance blue backdrop. Include light neutral highlights.
            if max(r, g, b) >= 88 and (saturation >= 28 or min(r, g, b) >= 92):
                target[x, y] = 255
    # Close small gaps, include the dark ink outline, then fill enclosed holes.
    rough = rough.filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.MinFilter(7))
    return rough


def foreground_mask(image: Image.Image) -> Image.Image:
    return largest_component(foreground_candidates(image))


def component_boxes(mask: Image.Image) -> list[tuple[int, int, int, int]]:
    width, height = mask.size
    pixels = mask.load()
    seen = bytearray(width * height)
    boxes = []
    for sy in range(height):
        for sx in range(width):
            index = sy * width + sx
            if seen[index] or pixels[sx, sy] == 0:
                continue
            queue = deque([(sx, sy)])
            seen[index] = 1
            count = 0
            left = right = sx
            top = bottom = sy
            while queue:
                x, y = queue.popleft()
                count += 1
                left, right = min(left, x), max(right, x)
                top, bottom = min(top, y), max(bottom, y)
                for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                    if 0 <= nx < width and 0 <= ny < height:
                        ni = ny * width + nx
                        if not seen[ni] and pixels[nx, ny]:
                            seen[ni] = 1
                            queue.append((nx, ny))
            if count >= 5000:
                boxes.append((left, top, right + 1, bottom + 1))
    return boxes


def largest_component(mask: Image.Image) -> Image.Image:
    pixels = mask.load()
    width, height = mask.size
    seen = bytearray(width * height)
    largest: list[tuple[int, int]] = []
    for sy in range(height):
        for sx in range(width):
            index = sy * width + sx
            if seen[index] or pixels[sx, sy] == 0:
                continue
            component: list[tuple[int, int]] = []
            queue = deque([(sx, sy)])
            seen[index] = 1
            while queue:
                x, y = queue.popleft()
                component.append((x, y))
                for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                    if 0 <= nx < width and 0 <= ny < height:
                        ni = ny * width + nx
                        if not seen[ni] and pixels[nx, ny]:
                            seen[ni] = 1
                            queue.append((nx, ny))
            if len(component) > len(largest):
                largest = component
    assert largest, "empty Shield Guard frame"
    result = Image.new("L", mask.size, 0)
    out = result.load()
    for x, y in largest:
        out[x, y] = 255
    # Fill transparent holes enclosed by the character silhouette.
    inverse = Image.eval(result, lambda value: 255 - value)
    outside = edge_component(inverse)
    holes = Image.eval(outside, lambda value: 255 - value)
    return ImageChops.lighter(result, holes)


def edge_component(mask: Image.Image) -> Image.Image:
    pixels = mask.load()
    width, height = mask.size
    output = Image.new("L", mask.size, 0)
    out = output.load()
    queue: deque[tuple[int, int]] = deque()
    for x in range(width):
        queue.extend(((x, 0), (x, height - 1)))
    for y in range(height):
        queue.extend(((0, y), (width - 1, y)))
    while queue:
        x, y = queue.popleft()
        if out[x, y] or not pixels[x, y]:
            continue
        out[x, y] = 255
        if x: queue.append((x - 1, y))
        if x + 1 < width: queue.append((x + 1, y))
        if y: queue.append((x, y - 1))
        if y + 1 < height: queue.append((x, y + 1))
    return output


def extract_frame(frame: Image.Image) -> Image.Image:
    rgb = frame.convert("RGB")
    mask = foreground_mask(rgb)
    rgba = Image.new("RGBA", rgb.size, (0, 0, 0, 0))
    rgba.paste(rgb, (0, 0), mask)
    return rgba


def split_sheet(path: Path) -> list[list[Image.Image]]:
    image = Image.open(path).convert("RGB")
    boxes = component_boxes(foreground_candidates(image))
    result = []
    for row in range(2):
        selected = [box for box in boxes
                    if ((box[1] + box[3]) * 0.5 < image.height * 0.5) == (row == 0)]
        selected.sort(key=lambda box: box[0])
        if len(selected) == COLS:
            frames = []
            for left, top, right, bottom in selected:
                pad = 8
                frames.append(extract_frame(image.crop((max(0, left-pad), max(0, top-pad),
                                                        min(image.width, right+pad),
                                                        min(image.height, bottom+pad)))))
            result.append(frames)
            continue
        frames = []
        top = round(image.height * row / 2)
        bottom = round(image.height * (row + 1) / 2)
        for column in range(COLS):
            left = round(image.width * column / COLS)
            right = round(image.width * (column + 1) / COLS)
            inset_x = max(3, round((right - left) * 0.025))
            inset_y = max(3, round((bottom - top) * 0.02))
            panel = image.crop((left + inset_x, top + inset_y, right - inset_x, bottom - inset_y))
            frames.append(extract_frame(panel))
        result.append(frames)
    return result


def normalize_row(frames: list[Image.Image]) -> list[Image.Image]:
    boxes = [frame.getchannel("A").getbbox() for frame in frames]
    assert all(boxes)
    widths = [box[2] - box[0] for box in boxes if box]
    heights = [box[3] - box[1] for box in boxes if box]
    # Reserve motion-safe gutters. The prior 148x178 normalization left only
    # 4-6px, which became visually cropped after TV scaling and animation.
    scale = min(SAFE_WIDTH / max(widths), SAFE_HEIGHT / max(heights))
    normalized = []
    for frame, box in zip(frames, boxes):
        assert box is not None
        cropped = frame.crop(box)
        small_size = (max(2, round(cropped.width * scale / 2)),
                      max(2, round(cropped.height * scale / 2)))
        small = cropped.resize(small_size, Image.Resampling.LANCZOS)
        alpha = small.getchannel("A").point(lambda a: 255 if a >= 96 else 0)
        small.putalpha(alpha)
        sprite = small.resize((small.width * 2, small.height * 2), Image.Resampling.NEAREST)
        data = [(r, g, b, a) if a else (0, 0, 0, 0) for r, g, b, a in sprite.getdata()]
        sprite.putdata(data)
        cell = Image.new("RGBA", CELL_SIZE, (0, 0, 0, 0))
        x = ((CELL_SIZE[0] - sprite.width) // 2) & ~1
        y = (CELL_SIZE[1] - SAFE_BOTTOM - sprite.height) & ~1
        assert x >= 12 and y >= 12, (sprite.size, x, y)
        cell.alpha_composite(sprite, (x, y))
        normalized.append(cell)
    return normalized


def validate(atlas: Image.Image) -> None:
    assert atlas.size == ATLAS_SIZE and atlas.mode == "RGBA"
    assert all(a in (0, 255) for *_, a in atlas.getdata())
    assert all(a or not (r or g or b) for r, g, b, a in atlas.getdata())
    down = atlas.resize((480, 576), Image.Resampling.NEAREST)
    assert down.resize(ATLAS_SIZE, Image.Resampling.NEAREST).tobytes() == atlas.tobytes()
    for row in range(ROWS):
        hashes = set()
        for column in range(COLS):
            cell = atlas.crop((column*160, row*192, (column+1)*160, (row+1)*192))
            bbox = cell.getchannel("A").getbbox()
            assert bbox and min(bbox[0], bbox[1], 160-bbox[2], 192-bbox[3]) >= 12, (row, column, bbox)
            hashes.add(hashlib.sha256(cell.tobytes()).digest())
        assert len(hashes) >= 3, (row, len(hashes))


def main() -> None:
    rows: list[list[Image.Image] | None] = [None] * ROWS
    for filename, first, second in SHEETS:
        pair = split_sheet(SOURCE / filename)
        rows[first] = normalize_row(pair[0])
        rows[second] = normalize_row(pair[1])
    for row, mapping in SAFE_FRAME_REMAP.items():
        assert rows[row]
        rows[row] = [rows[row][index].copy() for index in mapping]
    atlas = Image.new("RGBA", ATLAS_SIZE, (0, 0, 0, 0))
    for row, frames in enumerate(rows):
        assert frames
        for column, frame in enumerate(frames):
            atlas.alpha_composite(frame, (column * 160, row * 192))
    validate(atlas)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    atlas.save(OUTPUT / "shield_guard_anim.png", optimize=True, compress_level=9)
    idle = atlas.crop((0, 0, 160, 192))
    master = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    master.alpha_composite(idle.resize((320, 384), Image.Resampling.NEAREST), (96, 104))
    master.save(OUTPUT / "shield_guard.png", optimize=True, compress_level=9)
    print("Built Shield Guard: 36 still-image frames, hard alpha, 2-pixel clusters")


if __name__ == "__main__":
    main()
