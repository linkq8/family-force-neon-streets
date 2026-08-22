#!/usr/bin/env python3
"""Bake TV-safe animation atlases above logical render size for clean sampling."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "android/app/src/main/assets"

SOURCE_DENSITY = 1.5

HEROES = {
    "parent": 126,
    "adam": 77,
    "shaikha": 77,
    "sulaiman": 88,
}
ENEMIES = {
    "grunt": 120,
    "skater": 110,
    "brute": 136,
    "boss": 160,
    "striker": 116,
    "shield_guard": 132,
}
RAW_ROOT = ROOT / "assets/higgsfield/android/animation_v2/actors"
HERO_RAW = {"parent": "hero_1", "adam": "hero_2", "shaikha": "hero_3", "sulaiman": "hero_4"}
ENEMY_RAW = {"grunt": "enemy_grunt", "skater": "enemy_skater",
             "brute": "enemy_brute", "boss": "boss_junk_king"}
HERO_ACTIONS = ("idle", "walk", "punch", "kick", "heavy_punch", "heavy_kick",
                "jump", "special", "link", "hurt", "knockdown")
ENEMY_ACTIONS = ("idle", "walk", "attack1", "attack2", "hurt", "knockdown")


def defringe(frame: Image.Image, remove_green: bool = False) -> Image.Image:
    """Replace chroma-contaminated edge RGB from the nearest opaque interior."""
    pixels = np.array(frame.convert("RGBA"), dtype=np.uint8)
    alpha = pixels[:, :, 3]
    visible = alpha > 8
    core = visible.copy()
    # The remover left a 6–10 source-pixel chroma rim on some clips. Rebuild
    # that rim from interior colours; at runtime this is still sub-pixel detail.
    for _ in range(8):
        padded = np.pad(core, 1, constant_values=False)
        core = core & padded[:-2, 1:-1] & padded[2:, 1:-1] \
            & padded[1:-1, :-2] & padded[1:-1, 2:]
    rgb = pixels[:, :, :3].copy()
    known = core.copy()
    if remove_green:
        green_spill = (rgb[:, :, 1] > 40) \
            & (rgb[:, :, 1] > rgb[:, :, 0] * 1.22) \
            & (rgb[:, :, 1] > rgb[:, :, 2] * 1.22)
        known &= ~green_spill
    for _ in range(20):
        unresolved = visible & ~known
        if not unresolved.any():
            break
        changed = np.zeros_like(known)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1),
                       (-1, -1), (-1, 1), (1, -1), (1, 1)):
            source_known = np.roll(np.roll(known, dy, axis=0), dx, axis=1)
            take = unresolved & source_known & ~changed
            shifted = np.roll(np.roll(rgb, dy, axis=0), dx, axis=1)
            rgb[take] = shifted[take]
            changed |= take
        if not changed.any():
            break
        known |= changed
    pixels[:, :, :3] = rgb
    pixels[~visible, :3] = 0
    return Image.fromarray(pixels)


def clean_resize(cell: Image.Image, size: tuple[int, int]) -> Image.Image:
    # The authored Striker/Guard sheets are already clean raster art. Preserve
    # their colour range and sample into the 1.5x runtime grid only once.
    result = cell.convert("RGBA").resize(size, Image.Resampling.LANCZOS)
    alpha = result.getchannel("A").point(lambda value: 0 if value < 10 else value)
    result.putalpha(alpha)
    clean = Image.new("RGBA", size, (0, 0, 0, 0))
    clean.alpha_composite(result)
    return clean


def normalize_highres(frame: Image.Image, size: tuple[int, int],
                       remove_green: bool = False) -> Image.Image:
    frame = frame.convert("RGBA")
    bbox = frame.getchannel("A").point(lambda value: 255 if value >= 16 else 0).getbbox()
    if bbox is None:
        return Image.new("RGBA", size, (0, 0, 0, 0))
    actor = defringe(frame.crop(bbox), remove_green=remove_green)
    safe_inset = max(6, round(min(size) * 0.04))
    max_width = max(1, size[0] - safe_inset * 2)
    max_height = max(1, size[1] - safe_inset * 2)
    scale = min(max_width / actor.width, max_height / actor.height)
    target = (max(1, round(actor.width * scale)), max(1, round(actor.height * scale)))
    actor = actor.resize(target, Image.Resampling.LANCZOS)
    alpha = actor.getchannel("A").point(lambda value: 0 if value < 10 else value)
    rgb = actor.convert("RGB")
    actor = rgb.convert("RGBA")
    actor.putalpha(alpha)
    clean_actor = Image.new("RGBA", actor.size, (0, 0, 0, 0))
    clean_actor.alpha_composite(actor)
    output = Image.new("RGBA", size, (0, 0, 0, 0))
    output.alpha_composite(clean_actor, ((size[0] - actor.width) // 2,
                                         size[1] - safe_inset - actor.height))
    return output


def build_from_frames(root: Path, output: Path, actions: tuple[str, ...],
                      columns: int, cell_size: tuple[int, int]) -> None:
    atlas = Image.new("RGBA", (cell_size[0] * columns, cell_size[1] * len(actions)),
                      (0, 0, 0, 0))
    for row, action in enumerate(actions):
        frames = sorted((root / "removed" / action).glob("*.png"))
        if not frames:
            raise FileNotFoundError(root / "removed" / action)
        indices = [round(i * (len(frames) - 1) / max(1, columns - 1)) for i in range(columns)]
        for column, index in enumerate(indices):
            with Image.open(frames[index]) as frame:
                cell = normalize_highres(frame, cell_size,
                                         remove_green=root.name == "hero_1")
            atlas.alpha_composite(cell, (column * cell_size[0], row * cell_size[1]))
    output.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(output, optimize=True, compress_level=9)


def build(source: Path, output: Path, columns: int, rows: int,
          cell_size: tuple[int, int]) -> None:
    with Image.open(source) as master:
        master = master.convert("RGBA")
        source_w = master.width // columns
        source_h = master.height // rows
        assert source_w * columns == master.width
        assert source_h * rows == master.height
        target_w, target_h = cell_size
        atlas = Image.new("RGBA", (target_w * columns, target_h * rows), (0, 0, 0, 0))
        for row in range(rows):
            for column in range(columns):
                cell = master.crop((column * source_w, row * source_h,
                                    (column + 1) * source_w, (row + 1) * source_h))
                atlas.alpha_composite(clean_resize(cell, cell_size),
                                      (column * target_w, row * target_h))
    output.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(output, optimize=True, compress_level=9)


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


def main() -> None:
    for name, logical_cell in HEROES.items():
        cell = round(logical_cell * SOURCE_DENSITY)
        build_from_frames(RAW_ROOT / HERO_RAW[name],
                          ASSETS / f"runtime/heroes/{name}_anim.png",
                          HERO_ACTIONS, 8, (cell, cell))
    for name, logical_height in ENEMIES.items():
        height = round(logical_height * SOURCE_DENSITY)
        width = round(height * 160 / 192)
        output = ASSETS / f"runtime/enemies/{name}_anim.png"
        if name in ENEMY_RAW:
            build_from_frames(RAW_ROOT / ENEMY_RAW[name], output,
                              ENEMY_ACTIONS, 6, (width, height))
        else:
            build(ASSETS / f"enemies/{name}_anim.png", output, 6, 6, (width, height))
    refresh_manifest()
    print("Generated 10 1.5x-density runtime atlases and refreshed manifest")


if __name__ == "__main__":
    main()
