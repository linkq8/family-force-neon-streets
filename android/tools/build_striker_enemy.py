#!/usr/bin/env python3
"""Build the Striker runtime atlas from the approved ImageGen action sheets."""

from __future__ import annotations

from collections import deque
from pathlib import Path
import hashlib

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets/imagegen/android/enemies/striker"
OUTPUT = ROOT / "android/app/src/main/assets/enemies"
ATLAS_SIZE = (960, 1152)
CELL_SIZE = (160, 192)
COLS, ROWS = 6, 6

SHEETS = (
    ("idle_walk_raw.png", 0, 1),
    ("attacks_raw.png", 2, 3),
    ("hurt_knockdown_clean.png", 4, 5),
)

# The source generator let adjacent poses overlap in two rows. Reuse the clean
# authored poses to form coherent held timing rather than shipping a severed
# glove/effect from the neighboring panel.
SAFE_FRAME_REMAP = {
    1: (3, 3, 4, 4, 5, 5),       # walk: three clean gait keys with 2px bob timing
    2: (0, 1, 2, 3, 2, 5),       # light attack: anticipation, hit, retract
}

WALK_BOB_Y = (0, -2, 0, -2, 0, -2)


def remove_light_checker(image: Image.Image) -> Image.Image:
    """Remove only the light neutral checker connected to the canvas edge."""
    rgb = image.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()
    background = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()

    def candidate(x: int, y: int) -> bool:
        red, green, blue = pixels[x, y]
        return min(red, green, blue) >= 222 and max(red, green, blue) - min(red, green, blue) <= 16

    for x in range(width):
        if candidate(x, 0): queue.append((x, 0))
        if candidate(x, height - 1): queue.append((x, height - 1))
    for y in range(height):
        if candidate(0, y): queue.append((0, y))
        if candidate(width - 1, y): queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        index = y * width + x
        if background[index] or not candidate(x, y):
            continue
        background[index] = 1
        if x: queue.append((x - 1, y))
        if x + 1 < width: queue.append((x + 1, y))
        if y: queue.append((x, y - 1))
        if y + 1 < height: queue.append((x, y + 1))

    rgba = rgb.convert("RGBA")
    data = list(rgba.getdata())
    for index, is_background in enumerate(background):
        if is_background:
            data[index] = (0, 0, 0, 0)
    rgba.putdata(data)
    return rgba


def hard_alpha(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    cleaned = []
    for red, green, blue, alpha in rgba.getdata():
        if alpha <= 24:
            cleaned.append((0, 0, 0, 0))
        else:
            cleaned.append((red, green, blue, 255))
    rgba.putdata(cleaned)
    return rgba


def keep_character_component(image: Image.Image) -> Image.Image:
    """Discard panel-overflow fragments while preserving the connected fighter."""
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    width, height = rgba.size
    pixels = alpha.load()
    seen = bytearray(width * height)
    largest: list[tuple[int, int]] = []
    for start_y in range(height):
        for start_x in range(width):
            index = start_y * width + start_x
            if seen[index] or pixels[start_x, start_y] == 0:
                continue
            component: list[tuple[int, int]] = []
            queue = deque([(start_x, start_y)])
            seen[index] = 1
            while queue:
                x, y = queue.popleft()
                component.append((x, y))
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if not (0 <= nx < width and 0 <= ny < height):
                        continue
                    neighbor = ny * width + nx
                    if seen[neighbor] or pixels[nx, ny] == 0:
                        continue
                    seen[neighbor] = 1
                    queue.append((nx, ny))
            if len(component) > len(largest):
                largest = component
    assert largest, "empty character component"
    mask = Image.new("L", rgba.size, 0)
    mask_pixels = mask.load()
    for x, y in largest:
        mask_pixels[x, y] = 255
    clean = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    clean.paste(rgba, (0, 0), mask)
    return clean


def clear_panel_edges(image: Image.Image) -> Image.Image:
    """Cut the sheet gutters before connectivity can join two neighboring poses."""
    rgba = image.convert("RGBA")
    inset_x = max(4, round(rgba.width * 0.05))
    inset_y = max(4, round(rgba.height * 0.03))
    pixels = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            if x < inset_x or x >= rgba.width - inset_x \
                    or y < inset_y or y >= rgba.height - inset_y:
                pixels[x, y] = (0, 0, 0, 0)
    return rgba


def translate_cell(image: Image.Image, dx: int, dy: int) -> Image.Image:
    shifted = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shifted.alpha_composite(image, (dx, dy))
    return shifted


def split_sheet(path: Path) -> list[list[Image.Image]]:
    image = Image.open(path)
    if image.mode != "RGBA":
        image = remove_light_checker(image)
    else:
        image = image.convert("RGBA")
    result: list[list[Image.Image]] = []
    for row in range(2):
        frames = []
        top = round(image.height * row / 2)
        bottom = round(image.height * (row + 1) / 2)
        for column in range(COLS):
            left = round(image.width * column / COLS)
            right = round(image.width * (column + 1) / COLS)
            frame = keep_character_component(
                clear_panel_edges(hard_alpha(image.crop((left, top, right, bottom))))
            )
            assert frame.getchannel("A").getbbox(), (path.name, row, column, "empty")
            frames.append(frame)
        result.append(frames)
    return result


def normalize_row(frames: list[Image.Image]) -> list[Image.Image]:
    boxes = [frame.getchannel("A").getbbox() for frame in frames]
    assert all(boxes)
    widths = [box[2] - box[0] for box in boxes if box]
    heights = [box[3] - box[1] for box in boxes if box]
    scale = min(148 / max(widths), 178 / max(heights))
    normalized = []
    for frame, box in zip(frames, boxes):
        assert box is not None
        cropped = frame.crop(box)
        target = (max(2, round(cropped.width * scale / 2)),
                  max(2, round(cropped.height * scale / 2)))
        # Downsample once, then restore exact 2-pixel clusters for the game's
        # modern-retro rendering and low-memory TV texture path.
        small = cropped.resize(target, Image.Resampling.LANCZOS)
        small = hard_alpha(small)
        sprite = small.resize((target[0] * 2, target[1] * 2), Image.Resampling.NEAREST)
        cell = Image.new("RGBA", CELL_SIZE, (0, 0, 0, 0))
        x = ((CELL_SIZE[0] - sprite.width) // 2) & ~1
        y = CELL_SIZE[1] - 4 - sprite.height
        assert x >= 4 and y >= 4, (sprite.size, x, y)
        cell.alpha_composite(sprite, (x, y))
        normalized.append(keep_character_component(cell))
    return normalized


def validate(atlas: Image.Image) -> None:
    assert atlas.size == ATLAS_SIZE and atlas.mode == "RGBA"
    raw = list(atlas.getdata())
    assert all(alpha in (0, 255) for _, _, _, alpha in raw), "soft alpha"
    assert all(alpha or (red == green == blue == 0) for red, green, blue, alpha in raw), "RGB under alpha"
    clustered = atlas.resize((atlas.width // 2, atlas.height // 2), Image.Resampling.NEAREST)
    clustered = clustered.resize(atlas.size, Image.Resampling.NEAREST)
    assert clustered.tobytes() == atlas.tobytes(), "not aligned to global 2-pixel clusters"
    for row in range(ROWS):
        hashes = set()
        for column in range(COLS):
            cell = atlas.crop((column * 160, row * 192, (column + 1) * 160, (row + 1) * 192))
            bbox = cell.getchannel("A").getbbox()
            assert bbox is not None, (row, column, "empty")
            assert min(bbox[0], bbox[1], 160 - bbox[2], 192 - bbox[3]) >= 4, (row, column, bbox)
            hashes.add(hashlib.sha256(cell.tobytes()).digest())
        assert len(hashes) >= 3, (row, "insufficient motion", len(hashes))


def main() -> None:
    rows: list[list[Image.Image] | None] = [None] * ROWS
    for filename, first_row, second_row in SHEETS:
        source_rows = split_sheet(SOURCE / filename)
        rows[first_row] = normalize_row(source_rows[0])
        rows[second_row] = normalize_row(source_rows[1])
    assert all(rows)

    for row, mapping in SAFE_FRAME_REMAP.items():
        source_frames = rows[row]
        assert source_frames is not None
        rows[row] = [source_frames[index].copy() for index in mapping]
    assert rows[1] is not None
    rows[1] = [translate_cell(frame, 0, WALK_BOB_Y[index])
               for index, frame in enumerate(rows[1])]

    atlas = Image.new("RGBA", ATLAS_SIZE, (0, 0, 0, 0))
    for row, frames in enumerate(rows):
        assert frames is not None
        for column, frame in enumerate(frames):
            atlas.alpha_composite(frame, (column * CELL_SIZE[0], row * CELL_SIZE[1]))
    validate(atlas)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    atlas.save(OUTPUT / "striker_anim.png", optimize=True, compress_level=9)

    idle = atlas.crop((0, 0, 160, 192))
    master = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    enlarged = idle.resize((320, 384), Image.Resampling.NEAREST)
    master.alpha_composite(enlarged, ((512 - enlarged.width) // 2, 512 - enlarged.height - 24))
    master.save(OUTPUT / "striker.png", optimize=True, compress_level=9)
    print("Built Striker: 6x6 atlas, 36 frames, hard alpha, 2-pixel clusters")


if __name__ == "__main__":
    main()
