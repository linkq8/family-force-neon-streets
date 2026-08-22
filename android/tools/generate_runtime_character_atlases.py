#!/usr/bin/env python3
"""Bake every animation atlas at its exact 640x360 logical render size."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "android/app/src/main/assets"

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


def clean_resize(cell: Image.Image, size: tuple[int, int]) -> Image.Image:
    # One deterministic nearest sample per final logical pixel. Filtering here
    # caused the exact haze the user reported; filtering later caused uneven
    # cluster sizes. At exact runtime dimensions nearest means no live scaling.
    resized = cell.convert("RGBA").resize(size, Image.Resampling.NEAREST)
    alpha = resized.getchannel("A").point(lambda value: 255 if value >= 80 else 0)
    rgb = resized.convert("RGB")
    # A finite non-dithered palette keeps every pixel deliberate without
    # inventing gray transition pixels around faces, armor, or outlines.
    rgb = rgb.quantize(colors=192, method=Image.Quantize.MEDIANCUT,
                       dither=Image.Dither.NONE).convert("RGB")
    result = rgb.convert("RGBA")
    result.putalpha(alpha)
    clean = Image.new("RGBA", size, (0, 0, 0, 0))
    clean.alpha_composite(result)
    return clean


def normalize_highres(frame: Image.Image, size: tuple[int, int]) -> Image.Image:
    frame = frame.convert("RGBA")
    bbox = frame.getchannel("A").point(lambda value: 255 if value >= 16 else 0).getbbox()
    if bbox is None:
        return Image.new("RGBA", size, (0, 0, 0, 0))
    actor = frame.crop(bbox)
    max_width = max(1, size[0] - 8)
    max_height = max(1, size[1] - 8)
    scale = min(max_width / actor.width, max_height / actor.height)
    target = (max(1, round(actor.width * scale)), max(1, round(actor.height * scale)))
    actor = actor.resize(target, Image.Resampling.LANCZOS)
    alpha = actor.getchannel("A").point(lambda value: 255 if value >= 72 else 0)
    rgb = actor.convert("RGB").filter(
        ImageFilter.UnsharpMask(radius=0.58, percent=155, threshold=2)
    ).quantize(colors=160, method=Image.Quantize.MEDIANCUT,
               dither=Image.Dither.NONE).convert("RGB")
    actor = rgb.convert("RGBA")
    actor.putalpha(alpha)
    clean_actor = Image.new("RGBA", actor.size, (0, 0, 0, 0))
    clean_actor.alpha_composite(actor)
    output = Image.new("RGBA", size, (0, 0, 0, 0))
    output.alpha_composite(clean_actor, ((size[0] - actor.width) // 2,
                                         size[1] - 4 - actor.height))
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
                cell = normalize_highres(frame, cell_size)
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
    for name, cell in HEROES.items():
        build_from_frames(RAW_ROOT / HERO_RAW[name],
                          ASSETS / f"runtime/heroes/{name}_anim.png",
                          HERO_ACTIONS, 8, (cell, cell))
    for name, height in ENEMIES.items():
        width = round(height * 160 / 192)
        output = ASSETS / f"runtime/enemies/{name}_anim.png"
        if name in ENEMY_RAW:
            build_from_frames(RAW_ROOT / ENEMY_RAW[name], output,
                              ENEMY_ACTIONS, 6, (width, height))
        else:
            build(ASSETS / f"enemies/{name}_anim.png", output, 6, 6, (width, height))
    refresh_manifest()
    print("Generated 10 exact-scale crisp runtime atlases and refreshed manifest")


if __name__ == "__main__":
    main()
