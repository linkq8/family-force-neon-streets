#!/usr/bin/env python3
"""Build only the approved Essa and Striker redraw atlases."""

from __future__ import annotations

import hashlib
import json
import math
from collections import deque
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "android/app/src/main/assets"
SOURCE = ROOT / "assets/imagegen/android/character-redraw-v3"

ESSA_ACTIONS = ("idle", "walk", "punch", "kick", "heavy_punch",
                "heavy_kick", "jump", "special", "link", "hurt", "knockdown")
STRIKER_ACTIONS = ("idle", "walk", "attack1", "attack2", "hurt", "knockdown")

# The generated heavy-kick sheet contains the right keys but not chronological
# panel order. Reorder, never interpolate, to keep one readable action.
FRAME_REMAP = {
    ("essa", "walk"): (0, 1, 2, 3, 5, 6, 7, 0),
    ("essa", "heavy_kick"): (1, 4, 2, 0, 5, 6, 3, 7),
}


def is_chroma(red: int, green: int, blue: int) -> bool:
    return green > 138 and green > red * 1.35 and green > blue * 1.20


def split_sheet(path: Path, columns: int, rows: int) -> list[Image.Image]:
    image = Image.open(path).convert("RGB")
    frames = []
    for index in range(columns * rows):
        column, row = index % columns, index // columns
        # Image generators often make nominal 2px dividers 4–7px wide after
        # resizing. Exclude a fixed safe gutter so a divider can never become
        # part of the fighter bbox and shrink the actual character.
        left = round(image.width * column / columns) + 9
        right = round(image.width * (column + 1) / columns) - 9
        top = round(image.height * row / rows) + 9
        bottom = round(image.height * (row + 1) / rows) - 9
        cell = image.crop((left, top, right, bottom))
        pixels = cell.load()
        rgba = Image.new("RGBA", cell.size, (0, 0, 0, 0))
        output = rgba.load()
        for y in range(cell.height):
            for x in range(cell.width):
                red, green, blue = pixels[x, y]
                if not is_chroma(red, green, blue):
                    output[x, y] = (red, green, blue, 255)
        # Remove residual grid/background components. Real body/effect pixels
        # are isolated inside the chroma margin and never touch a crop edge.
        alpha = rgba.getchannel("A")
        alpha_pixels = alpha.load()
        seen = set()
        keep = set()
        largest = []
        for sy in range(cell.height):
            for sx in range(cell.width):
                if (sx, sy) in seen or not alpha_pixels[sx, sy]:
                    continue
                queue = deque([(sx, sy)])
                component = []
                touches_edge = False
                while queue:
                    x, y = queue.popleft()
                    if (x, y) in seen or not alpha_pixels[x, y]:
                        continue
                    seen.add((x, y))
                    component.append((x, y))
                    touches_edge |= x == 0 or y == 0 or x == cell.width - 1 or y == cell.height - 1
                    for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
                        if 0 <= nx < cell.width and 0 <= ny < cell.height:
                            queue.append((nx, ny))
                if not touches_edge and len(component) >= 12:
                    keep.update(component)
                if len(component) > len(largest):
                    largest = component
        if not keep:
            # Allow the caller's explicit remap to discard a generated panel
            # whose actor touches an edge, while keeping parsing deterministic.
            keep.update(largest)
        for y in range(cell.height):
            for x in range(cell.width):
                if (x, y) not in keep:
                    output[x, y] = (0, 0, 0, 0)
        bbox = rgba.getchannel("A").getbbox()
        if bbox is None:
            raise ValueError(f"empty generated cell: {path} #{index}")
        frames.append(rgba.crop(bbox))
    return frames


def guide_boxes(path: Path, columns: int, rows: int) -> list[tuple[int, int, int, int]]:
    """Read immutable placement from the pre-redraw 384px pose guide."""
    image = Image.open(path).convert("RGB")
    boxes = []
    for index in range(columns * rows):
        column, row = index % columns, index // columns
        left = round(image.width * column / columns)
        right = round(image.width * (column + 1) / columns)
        top = round(image.height * row / rows)
        bottom = round(image.height * (row + 1) / rows)
        cell = image.crop((left, top, right, bottom))
        mask = Image.new("L", cell.size, 0)
        pixels, output = cell.load(), mask.load()
        for y in range(9, cell.height - 9):
            for x in range(9, cell.width - 9):
                red, green, blue = pixels[x, y]
                if not is_chroma(red, green, blue):
                    output[x, y] = 255
        bbox = mask.getbbox()
        if bbox is None:
            raise ValueError(f"empty guide cell: {path} #{index}")
        boxes.append(bbox)
    return boxes


def retain_largest_component(frame: Image.Image) -> Image.Image:
    """Remove detached generator spark flecks without altering the fighter."""
    alpha = frame.getchannel("A")
    pixels = alpha.load()
    seen = set()
    largest = []
    for sy in range(frame.height):
        for sx in range(frame.width):
            if not pixels[sx, sy] or (sx, sy) in seen:
                continue
            queue = deque([(sx, sy)])
            component = []
            while queue:
                x, y = queue.popleft()
                if (x, y) in seen or not pixels[x, y]:
                    continue
                seen.add((x, y))
                component.append((x, y))
                for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
                    if 0 <= nx < frame.width and 0 <= ny < frame.height:
                        queue.append((nx, ny))
            if len(component) > len(largest):
                largest = component
    keep = set(largest)
    output = frame.copy()
    data = output.load()
    for y in range(output.height):
        for x in range(output.width):
            if (x, y) not in keep:
                data[x, y] = (0, 0, 0, 0)
    bbox = output.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("component cleanup removed entire frame")
    return output.crop(bbox)


def retain_largest_on_canvas(frame: Image.Image) -> Image.Image:
    alpha = frame.getchannel("A")
    pixels = alpha.load()
    seen = set()
    largest = []
    for sy in range(frame.height):
        for sx in range(frame.width):
            if not pixels[sx, sy] or (sx, sy) in seen:
                continue
            queue = deque([(sx, sy)])
            component = []
            while queue:
                x, y = queue.popleft()
                if (x, y) in seen or not pixels[x, y]:
                    continue
                seen.add((x, y))
                component.append((x, y))
                for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
                    if 0 <= nx < frame.width and 0 <= ny < frame.height:
                        queue.append((nx, ny))
            if len(component) > len(largest):
                largest = component
    keep = set(largest)
    output = frame.copy()
    data = output.load()
    for y in range(output.height):
        for x in range(output.width):
            if (x, y) not in keep:
                data[x, y] = (0, 0, 0, 0)
    return output


def place(frame: Image.Image, box: tuple[int, int, int, int],
          reference_cell: tuple[int, int], target_cell: tuple[int, int],
          y_adjust: int = 0) -> Image.Image:
    scale_x = target_cell[0] / reference_cell[0]
    scale_y = target_cell[1] / reference_cell[1]
    target_box = (round(box[0] * scale_x), round(box[1] * scale_y),
                  round(box[2] * scale_x), round(box[3] * scale_y))
    available_width = max(1, target_box[2] - target_box[0])
    available_height = max(1, target_box[3] - target_box[1])
    ratio = min(available_width / frame.width, available_height / frame.height)
    size = (max(1, round(frame.width * ratio)), max(1, round(frame.height * ratio)))
    actor = frame.resize(size, Image.Resampling.LANCZOS)
    alpha = actor.getchannel("A").point(lambda value: 255 if value >= 96 else 0)
    actor.putalpha(alpha)
    clean = Image.new("RGBA", actor.size, (0, 0, 0, 0))
    clean.paste(actor, (0, 0), alpha)
    x = target_box[0] + (available_width - actor.width) // 2
    y = target_box[3] - actor.height + round(y_adjust * scale_y)
    output = Image.new("RGBA", target_cell, (0, 0, 0, 0))
    output.alpha_composite(clean, (x, y))
    return output


def place_striker_standing(frame: Image.Image, box: tuple[int, int, int, int],
                            reference_cell: tuple[int, int],
                            target_cell: tuple[int, int], y_adjust: int = 0) -> Image.Image:
    """Keep Striker's body scale stable while allowing a compact punch arc.

    The legacy guide's per-frame width described the old art silhouette. Using
    it as a hard resize box made the newly drawn extended gloves shrink the
    entire fighter. Standing actions instead use a fixed visual height and the
    cell's safe width; the guide still owns the ground contact position.
    """
    scale_x = target_cell[0] / reference_cell[0]
    scale_y = target_cell[1] / reference_cell[1]
    safe_side = max(6, math.ceil(target_cell[0] * 0.075))
    desired_height = round(target_cell[1] * 0.70)
    ratio = desired_height / frame.height
    if frame.width * ratio > target_cell[0] - safe_side * 2:
        ratio = (target_cell[0] - safe_side * 2) / frame.width
    size = (max(1, round(frame.width * ratio)), max(1, round(frame.height * ratio)))
    actor = frame.resize(size, Image.Resampling.LANCZOS)
    alpha = actor.getchannel("A").point(lambda value: 255 if value >= 96 else 0)
    actor.putalpha(alpha)
    clean = Image.new("RGBA", actor.size, (0, 0, 0, 0))
    clean.paste(actor, (0, 0), alpha)
    clean = retain_largest_component(clean)
    actor = clean
    guide_center = (box[0] + box[2]) / 2
    x = round(guide_center * scale_x - actor.width / 2)
    x = max(safe_side, min(target_cell[0] - actor.width - safe_side, x))
    ground = round(box[3] * scale_y + y_adjust * scale_y)
    y = max(2, min(target_cell[1] - actor.height - 2, ground - actor.height))
    output = Image.new("RGBA", target_cell, (0, 0, 0, 0))
    output.alpha_composite(clean, (x, y))
    return output


def build_actor(name: str, actions: tuple[str, ...], source_columns: int,
                output_specs: tuple[tuple[Path, tuple[int, int]], ...]) -> None:
    columns, rows = source_columns, len(actions)
    reference_cell = (384, 384)
    boxes = []
    source_rows = []
    for row, action in enumerate(actions):
        frames = split_sheet(SOURCE / name / "actions" / f"{action}.png",
                             4 if name == "essa" else 3, 2)
        placement = guide_boxes(SOURCE / name / "guides" / f"{action}.png",
                                4 if name == "essa" else 3, 2)
        remap = FRAME_REMAP.get((name, action))
        if remap:
            frames = [frames[index] for index in remap]
            placement = [placement[index] for index in remap]
        if name == "striker" and action == "attack1":
            frames = [retain_largest_component(frame) for frame in frames]
        if len(frames) != columns:
            raise ValueError((name, action, len(frames), columns))
        source_rows.append(frames)
        boxes.append(placement)

    for output_path, target_cell in output_specs:
        atlas = Image.new("RGBA", (target_cell[0] * columns, target_cell[1] * rows),
                          (0, 0, 0, 0))
        for row, action in enumerate(actions):
            for column, frame in enumerate(source_rows[row]):
                # Generated idle frames are intentionally restrained. A one
                # pixel breath keeps the loop visibly alive without rubber scaling.
                adjust = (0, -1, -1, 0, -1, -1, 0, 0)[column] \
                    if name == "essa" and action == "idle" else 0
                adjust = (0, -1, 0, -1, 0, -1)[column] \
                    if name == "striker" and action == "idle" else adjust
                if name == "striker" and action != "knockdown":
                    cell = place_striker_standing(
                        frame, boxes[row][column], reference_cell, target_cell, adjust)
                else:
                    cell = place(frame, boxes[row][column], reference_cell, target_cell, adjust)
                if name == "striker":
                    cell = retain_largest_on_canvas(cell)
                atlas.alpha_composite(cell, (column * target_cell[0], row * target_cell[1]))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        atlas.save(output_path, optimize=True, compress_level=9)


def refresh_manifest() -> None:
    path = ASSETS / "asset_manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = []
    for asset in sorted(ASSETS.rglob("*")):
        if not asset.is_file() or asset == path:
            continue
        data = asset.read_bytes()
        record = {"path": asset.relative_to(ASSETS).as_posix(), "bytes": len(data),
                  "sha256": hashlib.sha256(data).hexdigest()}
        try:
            with Image.open(asset) as image:
                record.update(width=image.width, height=image.height, mode=image.mode)
        except (OSError, ValueError):
            pass
        records.append(record)
    payload["files"] = records
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    build_actor("essa", ESSA_ACTIONS, 8, (
        (ASSETS / "heroes/parent_anim.png", (192, 192)),
        (ASSETS / "tv/heroes/parent_anim.png", (144, 144)),
        (ASSETS / "runtime/heroes/parent_anim.png", (284, 284)),
        # 3072x4224: UHD/4K-class atlas used only on large-heap devices.
        (ASSETS / "uhd/heroes/parent_anim.png", (384, 384)),
    ))
    build_actor("striker", STRIKER_ACTIONS, 6, (
        (ASSETS / "enemies/striker_anim.png", (160, 192)),
        (ASSETS / "tv/enemies/striker_anim.png", (140, 168)),
        (ASSETS / "runtime/enemies/striker_anim.png", (218, 261)),
        # 1920x2304 with 2x the authored width for cleaner 4K-TV sampling.
        (ASSETS / "uhd/enemies/striker_anim.png", (320, 384)),
    ))
    # Static Striker fallback comes from the new neutral runtime frame.
    runtime = Image.open(ASSETS / "runtime/enemies/striker_anim.png").convert("RGBA")
    neutral = runtime.crop((0, 0, 218, 261))
    master = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    scale = min(420 / neutral.width, 440 / neutral.height)
    neutral = neutral.resize((round(neutral.width * scale), round(neutral.height * scale)),
                             Image.Resampling.LANCZOS)
    master.alpha_composite(neutral, ((512 - neutral.width) // 2, 480 - neutral.height))
    master.save(ASSETS / "enemies/striker.png", optimize=True, compress_level=9)
    refresh_manifest()
    print("Built redraws for Essa and Striker only")


if __name__ == "__main__":
    main()
