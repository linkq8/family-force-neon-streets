#!/usr/bin/env python3
"""Render every packaged animation-atlas row as a labelled QA GIF."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ASSETS = ROOT / "android" / "app" / "src" / "main" / "assets"
DEFAULT_OUTPUT = ROOT / "android" / "app" / "build" / "reports" / "animation-atlas-gifs"

HERO_ROWS = (
    "idle", "walk", "punch", "kick", "heavy_punch", "heavy_kick",
    "jump", "special", "link", "hurt", "knockdown",
)
ENEMY_ROWS = ("idle", "walk", "attack1", "attack2", "hurt", "knockdown")

CONTRACTS = (
    *((f"heroes/{name}_anim.png", 8, 192, HERO_ROWS)
      for name in ("parent", "adam", "shaikha", "sulaiman")),
    *((f"enemies/{name}_anim.png", 6, 160, ENEMY_ROWS)
      for name in ("grunt", "skater", "brute", "boss")),
)


def checker(width: int, height: int, tile: int = 16) -> Image.Image:
    image = Image.new("RGBA", (width, height), (30, 34, 48, 255))
    draw = ImageDraw.Draw(image)
    for top in range(0, height, tile):
        for left in range(0, width, tile):
            if (left // tile + top // tile) % 2:
                draw.rectangle(
                    (left, top, left + tile - 1, top + tile - 1),
                    fill=(49, 54, 72, 255),
                )
    return image


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=DEFAULT_ASSETS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--scale", type=int, default=2)
    args = parser.parse_args()
    if args.scale < 1:
        raise SystemExit("--scale must be positive")

    records = []
    for relative, columns, cell_width, rows in CONTRACTS:
        path = args.assets / relative
        with Image.open(path) as source:
            atlas = source.convert("RGBA")
        actor = Path(relative).stem.removesuffix("_anim")
        actor_dir = args.output / actor
        actor_dir.mkdir(parents=True, exist_ok=True)
        for row, action in enumerate(rows):
            frames = []
            frame_hashes = []
            for column in range(columns):
                cell = atlas.crop((
                    column * cell_width,
                    row * 192,
                    (column + 1) * cell_width,
                    (row + 1) * 192,
                ))
                frame_hashes.append(hashlib.sha256(cell.tobytes()).hexdigest())
                cell = cell.resize(
                    (cell.width * args.scale, cell.height * args.scale),
                    Image.Resampling.NEAREST,
                )
                canvas = checker(cell.width, cell.height)
                canvas.alpha_composite(cell)
                frames.append(canvas.convert("P", palette=Image.Palette.ADAPTIVE))
            destination = actor_dir / f"{row:02d}_{action}.gif"
            duration = 110 if action in {"idle", "walk"} else 90
            durations = [duration] * len(frames)
            if action not in {"idle", "walk"}:
                durations[-1] = 360
            frames[0].save(
                destination,
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,
                disposal=2,
                optimize=False,
            )
            # GIF encoders legally coalesce identical held frames while adding
            # their durations. Record both the atlas contract and encoded count.
            with Image.open(destination) as encoded:
                encoded_frames = getattr(encoded, "n_frames", 1)
            records.append({
                "actor": actor,
                "action": action,
                "row": row,
                "source_frames": columns,
                "encoded_frames": encoded_frames,
                "unique_rgba_frames": len(set(frame_hashes)),
                "path": destination.relative_to(args.output).as_posix(),
                "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
            })

    index = {
        "assets": str(args.assets.resolve()),
        "rows": len(records),
        "gifs": records,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "index.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Rendered {len(records)} atlas-row GIFs to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
