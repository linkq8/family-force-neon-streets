#!/usr/bin/env python3
"""Build action-only clips with twelve real image cells per movement."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "android/app/src/main/assets"
PRODUCTION = ROOT / "assets/imagegen/android/animation-clips-v1"

HERO_ACTIONS = (
    "idle", "walk", "punch", "kick", "heavy_punch", "heavy_kick",
    "jump", "special", "link", "hurt", "knockdown",
)
ENEMY_ACTIONS = ("idle", "walk", "attack_1", "attack_2", "hurt", "knockdown")
TARGET_FRAMES = 12


def clean_white_boundary(image: Image.Image) -> Image.Image:
    """Remove only neutral bright matte pixels connected to transparent space."""
    rgba = np.asarray(image.convert("RGBA")).copy()
    rgb = rgba[..., :3]
    alpha = rgba[..., 3]
    outside = alpha <= 12
    matte = ((alpha > 0) & (rgb.min(axis=2) >= 218)
             & ((rgb.max(axis=2) - rgb.min(axis=2)) <= 24))
    while True:
        adjacent = (np.roll(outside, 1, 0) | np.roll(outside, -1, 0)
                    | np.roll(outside, 1, 1) | np.roll(outside, -1, 1))
        added = matte & adjacent & ~outside
        if not added.any():
            break
        outside |= added
    rgba[outside] = (0, 0, 0, 0)
    rgba[~outside, 3] = 255
    return Image.fromarray(rgba, "RGBA")


def save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True, compress_level=9)


def brighten_adam_body(frame: Image.Image) -> Image.Image:
    """Replace the oversized near-black body fills while preserving hair/face."""
    rgba = np.asarray(frame.convert("RGBA")).copy()
    alpha = rgba[..., 3] > 0
    ys, _ = np.nonzero(alpha)
    if not len(ys):
        return frame
    top, bottom = int(ys.min()), int(ys.max())
    body_start = top + max(1, round((bottom - top) * 0.20))
    r, g, b = rgba[..., 0], rgba[..., 1], rgba[..., 2]
    green = alpha & (g > 38) & (g > r * 1.18) & (g > b * 1.05)
    dark = alpha & (r < 42) & (g < 46) & (b < 52)
    dark[:body_start, :] = False
    reached = green.copy()
    # Grow only through dark pixels connected to the approved green body. This
    # fills black torso/limb plates but does not touch the separated black hair.
    for _ in range(14):
        adjacent = (np.roll(reached, 1, 0) | np.roll(reached, -1, 0)
                    | np.roll(reached, 1, 1) | np.roll(reached, -1, 1))
        added = dark & adjacent & ~reached
        if not added.any():
            break
        reached |= added
    yy, xx = np.indices(alpha.shape)
    xs = np.nonzero(alpha)[1]
    left, right = int(xs.min()), int(xs.max())
    body_height = max(1, bottom - top)
    body_width = max(1, right - left)
    body_region = ((yy >= top + body_height * 0.31)
                   | ((yy >= top + body_height * 0.18)
                      & ((xx <= left + body_width * 0.36)
                         | (xx >= left + body_width * 0.64))))
    # The old Adam atlas also contains transparent holes inside the outlined
    # chest, shoulders and boots. Flood only the true exterior from a corner;
    # remaining transparent islands are enclosed body holes, not background.
    transparency = Image.fromarray((~alpha).astype(np.uint8) * 255).copy()
    for seed in ((0, 0), (transparency.width - 1, 0),
                 (0, transparency.height - 1),
                 (transparency.width - 1, transparency.height - 1)):
        if transparency.getpixel(seed) == 255:
            ImageDraw.floodfill(transparency, seed, 128, thresh=0)
    enclosed_holes = (np.asarray(transparency) == 255) & body_region
    rgba[enclosed_holes, 0] = 20
    rgba[enclosed_holes, 1] = 135
    rgba[enclosed_holes, 2] = 55
    rgba[enclosed_holes, 3] = 255
    alpha = rgba[..., 3] > 0
    transparent = ~alpha
    boundary = dark & (np.roll(transparent, 1, 0) | np.roll(transparent, -1, 0)
                       | np.roll(transparent, 1, 1) | np.roll(transparent, -1, 1))
    # Also cover isolated black interior plates that are encircled by green
    # linework, while preserving the outer silhouette and the face/eyes.
    fill = dark & body_region & ~boundary
    rgba[fill, 0] = 20
    rgba[fill, 1] = 135
    rgba[fill, 2] = 55
    return Image.fromarray(rgba, "RGBA")


def shifted(frame: Image.Image, dx: int, dy: int) -> Image.Image:
    result = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    result.alpha_composite(frame, (dx, dy))
    return result


def expand_to_twelve(clip: Image.Image, source_columns: int, actor: str) -> Image.Image:
    if clip.width % source_columns:
        raise ValueError(f"invalid source columns: {clip.size}/{source_columns}")
    cell_width = clip.width // source_columns
    frames = [clip.crop((i * cell_width, 0, (i + 1) * cell_width, clip.height))
              for i in range(source_columns)]
    if actor == "adam":
        frames = [brighten_adam_body(frame) for frame in frames]
    output = Image.new("RGBA", (cell_width * TARGET_FRAMES, clip.height), (0, 0, 0, 0))
    previous_source = -1
    for target in range(TARGET_FRAMES):
        # Preserve the authored key poses, adding clean one-pixel in-betweens
        # rather than blurred cross-fades or duplicate bitmap cells.
        source = round(target * (source_columns - 1) / (TARGET_FRAMES - 1))
        frame = frames[source]
        if source == previous_source:
            direction = -1 if target % 2 else 1
            frame = shifted(frame, direction, -1)
        output.alpha_composite(frame, (target * cell_width, 0))
        previous_source = source
    return clean_white_boundary(output)


def resize_clip_cells(clip: Image.Image, cell_size: tuple[int, int]) -> Image.Image:
    source_width = clip.width // TARGET_FRAMES
    target_width, target_height = cell_size
    output = Image.new("RGBA", (target_width * TARGET_FRAMES, target_height), (0, 0, 0, 0))
    for index in range(TARGET_FRAMES):
        cell = clip.crop((index * source_width, 0, (index + 1) * source_width, clip.height))
        cell = cell.resize(cell_size, Image.Resampling.LANCZOS)
        output.alpha_composite(clean_white_boundary(cell), (index * target_width, 0))
    return output


def split_atlas(path: Path, rows: int, columns: int, actor: str,
                actions: tuple[str, ...], output: Path) -> list[Image.Image]:
    with Image.open(path) as source:
        atlas = source.convert("RGBA")
    if atlas.height % rows:
        raise ValueError(f"invalid atlas rows: {path} {atlas.size}/{rows}")
    row_height = atlas.height // rows
    clips = []
    for row, action in enumerate(actions):
        source = clean_white_boundary(atlas.crop(
            (0, row * row_height, atlas.width, (row + 1) * row_height)))
        clip = expand_to_twelve(source, columns, actor)
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


def build_actor(kind: str, name: str, actions: tuple[str, ...], rows: int,
                source_columns: int) -> None:
    tiers = ("", "runtime/", "tv/") if kind == "enemies" else ("", "runtime/", "tv/", "uhd/")
    best = None
    for tier in tiers:
        atlas = ASSETS / tier / kind / f"{name}_anim.png"
        if not atlas.is_file():
            continue
        clips = split_atlas(atlas, rows, source_columns, name, actions,
                            ASSETS / tier / "clips" / kind / name)
        if kind == "enemies" and tier == "tv/":
            clips = [resize_clip_cells(clip, (180, 154)) for clip in clips]
            for clip, action in zip(clips, actions):
                save(clip, ASSETS / tier / "clips" / kind / name / f"{action}.png")
        if best is None or clips[0].width * clips[0].height > best[0].width * best[0].height:
            best = clips
    if best is None:
        raise FileNotFoundError(f"missing atlas for {kind}/{name}")
    save_uhd_action_canvases(best, actions, PRODUCTION / kind / name)


def refresh_manifest() -> None:
    manifest = ASSETS / "asset_manifest.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    records = []
    for path in sorted(ASSETS.rglob("*")):
        if not path.is_file() or path == manifest:
            continue
        data = path.read_bytes()
        record = {
            "path": path.relative_to(ASSETS).as_posix(),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
        try:
            with Image.open(path) as image:
                record.update(width=image.width, height=image.height, mode=image.mode)
        except (OSError, ValueError):
            pass
        records.append(record)
    payload["files"] = records
    manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    for hero in ("parent", "adam"):
        build_actor("heroes", hero, HERO_ACTIONS, len(HERO_ACTIONS), 8)
    for enemy in ("grunt", "lantern_courier"):
        build_actor("enemies", enemy, ENEMY_ACTIONS, len(ENEMY_ACTIONS), 6)
    refresh_manifest()
    print("Built separate clips for Essa, Adam, Grunt, and Lantern Courier")


if __name__ == "__main__":
    main()
