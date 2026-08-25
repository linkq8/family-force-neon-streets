#!/usr/bin/env python3
"""Build strict 12-frame action clips for the pilot Essa/Market upgrade."""

from __future__ import annotations

from collections import deque
import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "android/app/src/main/assets"
ESSA_SOURCE = ROOT / "assets/imagegen/android/character-redraw-v5/essa/actions"
MARKET_SOURCE = ROOT / "assets/imagegen/android/enemies/quality-v5/market_enforcer/actions"
PRODUCTION = ROOT / "assets/imagegen/android/animation-clips-v2"
COLS, ROWS = 6, 2
ESSA_ACTIONS = (
    "idle", "walk", "punch", "kick", "heavy_punch", "heavy_kick",
    "jump", "special", "link", "hurt", "knockdown",
)
ESSA_TIERS = {
    "": ((192, 192), 161),
    "runtime/": ((284, 284), 239),
    "tv/": ((144, 144), 122),
    "uhd/": ((384, 384), 323),
}
MARKET_TIERS = {
    "": ((224, 192), 161),
    "runtime/": ((336, 288), 242),
    "tv/": ((196, 168), 142),
}
MARKET_ACTIONS = ("idle", "walk", "attack_1", "attack_2", "hurt", "knockdown")


def is_background(pixel: tuple[int, int, int]) -> bool:
    return min(pixel) >= 166 and max(pixel) - min(pixel) <= 58


def remove_edge_background(panel: Image.Image) -> Image.Image:
    rgb = panel.convert("RGB")
    width, height = rgb.size
    source = rgb.load()
    outside = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()
    for x in range(width):
        queue.extend(((x, 0), (x, height - 1)))
    for y in range(height):
        queue.extend(((0, y), (width - 1, y)))
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
        if clear:
            data[index] = (0, 0, 0, 0)
    rgba.putdata(data)
    return rgba


def hard_alpha(image: Image.Image, threshold: int = 72) -> Image.Image:
    rgba = image.convert("RGBA")
    rgba.putdata([
        (r, g, b, 255) if a >= threshold else (0, 0, 0, 0)
        for r, g, b, a in rgba.getdata()
    ])
    return rgba


def strip_light_matte(image: Image.Image) -> Image.Image:
    """Remove neutral light pixels connected to transparency (gray/white halo)."""
    result = image.convert("RGBA")
    px = result.load()
    queue = deque()
    seen = bytearray(result.width * result.height)
    for y in range(result.height):
        for x in range(result.width):
            if not px[x, y][3]:
                queue.append((x, y))
                seen[y * result.width + x] = 1
    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if not (0 <= nx < result.width and 0 <= ny < result.height):
                continue
            index = ny * result.width + nx
            if seen[index]:
                continue
            r, g, b, a = px[nx, ny]
            if a and min(r, g, b) >= 218 and max(r, g, b) - min(r, g, b) <= 24:
                px[nx, ny] = (0, 0, 0, 0)
                seen[index] = 1
                queue.append((nx, ny))
    return result


def authored_column_bounds(row_image: Image.Image) -> list[int]:
    """Use real generated grid rules when present; otherwise equal 6 columns."""
    rgb = row_image.convert("RGB")
    candidates = []
    for x in range(rgb.width):
        dark = sum(1 for y in range(rgb.height) if max(rgb.getpixel((x, y))) < 72)
        if dark >= rgb.height * .80:
            candidates.append(x)
    clusters: list[list[int]] = []
    for x in candidates:
        if not clusters or x > clusters[-1][-1] + 1:
            clusters.append([x])
        else:
            clusters[-1].append(x)
    internal = [round(sum(cluster) / len(cluster)) for cluster in clusters
                if 12 < cluster[0] < rgb.width - 12]
    if len(internal) == COLS - 1:
        return [0, *internal, rgb.width]
    return [round(index * rgb.width / COLS) for index in range(COLS + 1)]


def split_actor_components(row_image: Image.Image, bounds: list[int]) -> list[Image.Image]:
    """Assign disconnected limbs/effects to the nearest authored frame center."""
    work = row_image.convert("RGB")
    px = work.load()
    # Open all generated grid rules to the outside background before flood fill.
    for boundary in bounds[1:-1]:
        for x in range(max(0, boundary - 4), min(work.width, boundary + 5)):
            for y in range(work.height):
                px[x, y] = (235, 235, 235)
    for x in range(work.width):
        for y in range(3):
            px[x, y] = px[x, work.height - 1 - y] = (235, 235, 235)
    clean = hard_alpha(remove_edge_background(work))
    alpha = clean.getchannel("A")
    opaque = alpha.load()
    seen = bytearray(clean.width * clean.height)
    centers = [(bounds[i] + bounds[i + 1]) / 2 for i in range(COLS)]
    components_found: list[list[tuple[int, int]]] = []
    for sy in range(clean.height):
        for sx in range(clean.width):
            index = sy * clean.width + sx
            if seen[index] or not opaque[sx, sy]:
                continue
            queue = deque([(sx, sy)])
            seen[index] = 1
            component: list[tuple[int, int]] = []
            while queue:
                x, y = queue.popleft()
                component.append((x, y))
                for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                    if 0 <= nx < clean.width and 0 <= ny < clean.height:
                        ni = ny * clean.width + nx
                        if not seen[ni] and opaque[nx, ny]:
                            seen[ni] = 1
                            queue.append((nx, ny))
            if len(component) >= 6:
                components_found.append(component)
    if not components_found:
        raise ValueError("row contains no actor components")
    # Generated sheets occasionally contain thin orphaned slivers between
    # panels. Real limbs, shields and authored effects are substantial parts
    # of the actor silhouette; discard only components below 3% of a body.
    minimum_component = max(6, round(max(map(len, components_found)) * .03))
    groups: list[list[list[tuple[int, int]]]] = [[] for _ in range(COLS)]
    for component in components_found:
            if len(component) < minimum_component:
                continue
            centroid = sum(x for x, _ in component) / len(component)
            owner = min(range(COLS), key=lambda i: abs(centroid - centers[i]))
            groups[owner].append(component)

    frames = []
    source_px = clean.load()
    for index, components in enumerate(groups):
        if not components:
            raise ValueError(f"empty component frame {index}")
        points = [point for component in components for point in component]
        left = min(x for x, _ in points); right = max(x for x, _ in points) + 1
        top = min(y for _, y in points); bottom = max(y for _, y in points) + 1
        frame = Image.new("RGBA", (right - left, bottom - top), (0, 0, 0, 0))
        frame_px = frame.load()
        for x, y in points:
            frame_px[x - left, y - top] = source_px[x, y]
        frames.append(frame)
    return frames


def keep_nearby_components(image: Image.Image) -> Image.Image:
    """Remove grid fragments while retaining hands and compact authored effects."""
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    width, height = rgba.size
    px = alpha.load()
    seen = bytearray(width * height)
    components: list[list[tuple[int, int]]] = []
    for sy in range(height):
        for sx in range(width):
            index = sy * width + sx
            if seen[index] or not px[sx, sy]:
                continue
            queue = deque([(sx, sy)])
            seen[index] = 1
            component = []
            while queue:
                x, y = queue.popleft()
                component.append((x, y))
                for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                    if 0 <= nx < width and 0 <= ny < height:
                        ni = ny * width + nx
                        if not seen[ni] and px[nx, ny]:
                            seen[ni] = 1
                            queue.append((nx, ny))
            components.append(component)
    if not components:
        raise ValueError("empty generated panel")
    main = max(components, key=len)
    left = min(x for x, _ in main); right = max(x for x, _ in main)
    top = min(y for _, y in main); bottom = max(y for _, y in main)
    mask = Image.new("L", rgba.size, 0); out = mask.load()
    for component in components:
        if len(component) < 6:
            continue
        c_left = min(x for x, _ in component); c_right = max(x for x, _ in component)
        c_top = min(y for _, y in component); c_bottom = max(y for _, y in component)
        nearby = c_right >= left - width // 5 and c_left <= right + width // 5 \
            and c_bottom >= top - height // 7 and c_top <= bottom + height // 7
        if component is main or nearby:
            for x, y in component:
                out[x, y] = 255
    result = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    result.paste(rgba, (0, 0), mask)
    return result


def remove_grid_rules(image: Image.Image) -> Image.Image:
    """Clear generated full-height black panel rules before adaptive splitting."""
    result = image.copy()
    px = result.load()
    for x in range(result.width):
        dark = sum(1 for y in range(result.height)
                   if px[x, y][3] and max(px[x, y][:3]) < 72)
        if dark >= result.height * .82:
            for y in range(result.height):
                px[x, y] = (0, 0, 0, 0)
    return result


def adaptive_column_bounds(clean_row: Image.Image) -> list[int]:
    # Both approved sources use an exact 6-column composition.  Looking for a
    # low-alpha cut is unsafe because it can choose the gap between an actor's
    # arm and torso, splitting the actor instead of the authored panel.
    return [round(index * clean_row.width / COLS) for index in range(COLS + 1)]


def split_sheet(path: Path) -> list[Image.Image]:
    image = Image.open(path).convert("RGB")
    if image.width < 1500 or image.height < 900:
        raise ValueError(f"source below 1500x900: {path} {image.size}")
    frames = []
    for row in range(ROWS):
        top, bottom = round(row * image.height / ROWS), round((row + 1) * image.height / ROWS)
        row_image = image.crop((0, top, image.width, bottom))
        bounds = authored_column_bounds(row_image)
        frames.extend(split_actor_components(row_image, bounds))
    if len(frames) != 12:
        raise ValueError((path, len(frames)))
    return frames


def action_scale(frames: list[Image.Image], target_height: int) -> float:
    # Generated sheets vary their camera framing. Calibrate from beginning/end
    # ready poses, then apply one scale to every frame so crouches/falls remain real.
    anchors = [frames[i].height for i in (0, 10, 11)]
    reference = sorted(anchors)[1]
    return target_height / reference


def build_clip(frames: list[Image.Image], cell: tuple[int, int], target_height: int) -> Image.Image:
    scale = action_scale(frames, target_height)
    output = Image.new("RGBA", (cell[0] * 12, cell[1]), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        target = (max(2, round(frame.width * scale)), max(2, round(frame.height * scale)))
        fit = min(1.0, (cell[0] - 16) / target[0], (cell[1] - 16) / target[1])
        target = (max(2, round(target[0] * fit)), max(2, round(target[1] * fit)))
        actor = strip_light_matte(hard_alpha(
            frame.resize(target, Image.Resampling.LANCZOS), 48
        ))
        x = index * cell[0] + (cell[0] - actor.width) // 2
        y = cell[1] - 8 - actor.height
        local_x = x - index * cell[0]
        if min(local_x, y, cell[0] - local_x - actor.width, cell[1] - y - actor.height) < 7:
            raise ValueError(f"unsafe output frame {index}: {actor.size} in {cell}")
        output.alpha_composite(actor, (x, y))
    # A tightly cropped actor has no transparent neighbor outside its own
    # bitmap. Run the matte pass once more after placement in the padded clip.
    return strip_light_matte(output)


def save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True, compress_level=9)


def save_source_uhd(path: Path, destination: Path) -> None:
    image = Image.open(path).convert("RGB")
    scale = min(3744 / image.width, 2024 / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.NEAREST)
    canvas = Image.new("RGB", (3840, 2160), (224, 224, 224))
    canvas.paste(resized, ((3840 - resized.width) // 2, (2160 - resized.height) // 2))
    save(canvas, destination)


def build_essa() -> None:
    for action in ESSA_ACTIONS:
        source = ESSA_SOURCE / f"{action}.png"
        frames = split_sheet(source)
        for tier, (cell, height) in ESSA_TIERS.items():
            save(build_clip(frames, cell, height),
                 ASSETS / tier / "clips/heroes/parent" / f"{action}.png")
        save_source_uhd(source, PRODUCTION / "heroes/parent" / action / "source_uhd.png")


def build_market() -> None:
    # Preserve Market Enforcer's approved identity and five existing actions;
    # only the anatomically incorrect walk is replaced by the new 12-frame art.
    for tier in MARKET_TIERS:
        atlas = Image.open(ASSETS / tier / "enemies/market_enforcer_anim.png").convert("RGBA")
        cell_width = atlas.width // 6
        cell_height = atlas.height // 6
        for row, action in enumerate(MARKET_ACTIONS):
            if action == "walk":
                continue
            clip = atlas.crop((0, row * cell_height, atlas.width, (row + 1) * cell_height))
            save(clip, ASSETS / tier / "clips/enemies/market_enforcer" / f"{action}.png")
    source = MARKET_SOURCE / "walk.png"
    frames = split_sheet(source)
    for tier, (cell, height) in MARKET_TIERS.items():
        save(build_clip(frames, cell, height),
             ASSETS / tier / "clips/enemies/market_enforcer/walk.png")
    save_source_uhd(source, PRODUCTION / "enemies/market_enforcer/walk/source_uhd.png")


def refresh_manifest() -> None:
    path = ASSETS / "asset_manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = []
    for asset in sorted(ASSETS.rglob("*")):
        if not asset.is_file() or asset == path:
            continue
        data = asset.read_bytes()
        record = {
            "path": asset.relative_to(ASSETS).as_posix(),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
        try:
            with Image.open(asset) as image:
                record.update(width=image.width, height=image.height, mode=image.mode)
        except (OSError, ValueError):
            pass
        records.append(record)
    payload["files"] = records
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build_essa()
    build_market()
    refresh_manifest()
    print("Built 12-frame clips: Essa 11 actions + Market walk")
