#!/usr/bin/env python3
"""Split approved atlases into one action-only image and one UHD canvas per move."""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "android/app/src/main/assets"
PRODUCTION = ROOT / "assets/imagegen/android/animation-clips-v1"

HERO_ACTIONS = (
    "idle", "walk", "punch", "kick", "heavy_punch", "heavy_kick",
    "jump", "special", "link", "hurt", "knockdown",
)
ENEMY_ACTIONS = ("idle", "walk", "attack_1", "attack_2", "hurt", "knockdown")


def clean_white_boundary(image: Image.Image) -> Image.Image:
    """Remove only neutral bright matte pixels connected to transparent space."""
    rgba = image.convert("RGBA")
    width, height = rgba.size
    px = rgba.load()
    outside = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()
    # Seed every transparent region, including enclosed gaps between arms,
    # equipment, and the torso; matte can otherwise survive inside those gaps.
    for y in range(height):
        for x in range(width):
            if px[x, y][3] <= 12:
                queue.append((x, y))
    while queue:
        x, y = queue.popleft()
        idx = y * width + x
        if outside[idx]:
            continue
        r, g, b, a = px[x, y]
        neutral_matte = a > 0 and min(r, g, b) >= 218 and max(r, g, b) - min(r, g, b) <= 24
        if a > 12 and not neutral_matte:
            continue
        outside[idx] = 1
        px[x, y] = (0, 0, 0, 0)
        if x: queue.append((x - 1, y))
        if x + 1 < width: queue.append((x + 1, y))
        if y: queue.append((x, y - 1))
        if y + 1 < height: queue.append((x, y + 1))
    rgba.putdata([(0, 0, 0, 0) if a <= 12 else (r, g, b, 255)
                  for r, g, b, a in rgba.getdata()])
    return rgba


def save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True, compress_level=9)


def split_atlas(path: Path, rows: int, actions: tuple[str, ...], output: Path) -> list[Image.Image]:
    with Image.open(path) as source:
        atlas = source.convert("RGBA")
    if atlas.height % rows:
        raise ValueError(f"invalid atlas rows: {path} {atlas.size}/{rows}")
    row_height = atlas.height // rows
    clips = []
    for row, action in enumerate(actions):
        clip = clean_white_boundary(atlas.crop((0, row * row_height, atlas.width, (row + 1) * row_height)))
        if not clip.getchannel("A").getbbox():
            raise ValueError(f"empty clip: {path} {action}")
        save(clip, output / f"{action}.png")
        clips.append(clip)
    return clips


def save_uhd_action_canvases(clips: list[Image.Image], actions: tuple[str, ...], output: Path) -> None:
    for clip, action in zip(clips, actions):
        if clip.width > 3744 or clip.height > 2024:
            scale = min(3744 / clip.width, 2024 / clip.height)
            clip = clip.resize((round(clip.width * scale), round(clip.height * scale)), Image.Resampling.LANCZOS)
            clip = clean_white_boundary(clip)
        canvas = Image.new("RGBA", (3840, 2160), (0, 0, 0, 0))
        canvas.alpha_composite(clip, ((3840 - clip.width) // 2, (2160 - clip.height) // 2))
        save(canvas, output / action / "source_uhd.png")


def build_actor(kind: str, name: str, actions: tuple[str, ...], rows: int) -> None:
    tiers = ("", "runtime/", "tv/") if kind == "enemies" else ("", "runtime/", "tv/", "uhd/")
    best = None
    for tier in tiers:
        atlas = ASSETS / tier / kind / f"{name}_anim.png"
        if not atlas.is_file():
            continue
        clips = split_atlas(atlas, rows, actions, ASSETS / tier / "clips" / kind / name)
        if best is None or clips[0].width * clips[0].height > best[0].width * best[0].height:
            best = clips
    if best is None:
        raise FileNotFoundError(f"missing atlas for {kind}/{name}")
    save_uhd_action_canvases(best, actions, PRODUCTION / kind / name)


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
    actors = {
        "parent": ("heroes", HERO_ACTIONS),
        "adam": ("heroes", HERO_ACTIONS),
        "grunt": ("enemies", ENEMY_ACTIONS),
        "lantern_courier": ("enemies", ENEMY_ACTIONS),
    }
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--actor", choices=tuple(actors), action="append",
        help="rebuild only the selected actor; repeat as needed",
    )
    args = parser.parse_args()
    selected = args.actor or list(actors)
    for name in selected:
        kind, actions = actors[name]
        build_actor(kind, name, actions, len(actions))
    refresh_manifest()
    print("Built separate clips for " + ", ".join(selected))


if __name__ == "__main__":
    main()
