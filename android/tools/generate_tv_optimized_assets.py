#!/usr/bin/env python3
"""Create deterministic, memory-conscious Android TV image variants."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app/src/main/assets"

VARIANTS = (
    ("backgrounds/street.png", "tv/backgrounds/street.png", (960, 536), "RGB"),
    ("backgrounds/street_retro.png", "tv/backgrounds/street_retro.png", (960, 540), "RGB"),
    # Five chapter backgrounds stay resident to make transitions instant. At
    # 800x450 RGB_565 they retain 1.25x logical detail while remaining cheap
    # enough for low-memory Android TV devices.
    ("backgrounds/stage_market.png", "tv/backgrounds/stage_market.png", (800, 450), "RGB"),
    ("backgrounds/stage_transit.png", "tv/backgrounds/stage_transit.png", (800, 450), "RGB"),
    ("backgrounds/stage_harbor.png", "tv/backgrounds/stage_harbor.png", (800, 450), "RGB"),
    ("backgrounds/stage_palace.png", "tv/backgrounds/stage_palace.png", (800, 450), "RGB"),
    # True 3:1 continuous stage plates. Runtime takes a moving 16:9 crop;
    # unlike the old 800px plates these expose more than one full screen of
    # scenery and never tile, mirror, or jump when the player backtracks.
    ("backgrounds/panoramas/stage_market.png", "tv/backgrounds/panoramas/stage_market.png", (1800, 600), "RGB"),
    ("backgrounds/panoramas/stage_transit.png", "tv/backgrounds/panoramas/stage_transit.png", (1800, 600), "RGB"),
    ("backgrounds/panoramas/stage_harbor.png", "tv/backgrounds/panoramas/stage_harbor.png", (1800, 600), "RGB"),
    ("backgrounds/panoramas/stage_palace.png", "tv/backgrounds/panoramas/stage_palace.png", (1800, 600), "RGB"),
    ("backgrounds/panoramas/stage_final.png", "tv/backgrounds/panoramas/stage_final.png", (1800, 600), "RGB"),
    # The idle master is rendered at at most 192 logical pixels. A 384x576
    # source retains 2x vertical detail without keeping the 10.7 MiB decode.
    ("heroes/parent_hd.png", "tv/heroes/parent_hd.png", (384, 576), "RGBA"),
    # Full 8x11 hero atlases at 144px cells. Every action and frame remains;
    # decoded memory drops from 12.4 MiB to 7.0 MiB per active hero.
    ("heroes/parent_anim.png", "tv/heroes/parent_anim.png", (1152, 1584), "RGBA"),
    ("heroes/adam_anim.png", "tv/heroes/adam_anim.png", (1152, 1584), "RGBA"),
    ("heroes/shaikha_anim.png", "tv/heroes/shaikha_anim.png", (1152, 1584), "RGBA"),
    ("heroes/sulaiman_anim.png", "tv/heroes/sulaiman_anim.png", (1152, 1584), "RGBA"),
    # Stage 1 strict atlases are intentionally absent here. Their dedicated
    # builder owns wider 196x168 TV cells and must never be overwritten by a
    # generic whole-atlas resize.
    ("enemies/brute_anim.png", "tv/enemies/brute_anim.png", (840, 1008), "RGBA"),
    ("enemies/boss_anim.png", "tv/enemies/boss_anim.png", (840, 1008), "RGBA"),
    ("enemies/striker_anim.png", "tv/enemies/striker_anim.png", (840, 1008), "RGBA"),
    ("enemies/shield_guard_anim.png", "tv/enemies/shield_guard_anim.png", (840, 1008), "RGBA"),
    ("enemies/rail_runner_anim.png", "tv/enemies/rail_runner_anim.png", (840, 1008), "RGBA"),
    ("enemies/signal_warden_anim.png", "tv/enemies/signal_warden_anim.png", (840, 1008), "RGBA"),
    ("enemies/railmaster_9_anim.png", "tv/enemies/railmaster_9_anim.png", (840, 1008), "RGBA"),
    ("enemies/cargo_loader_anim.png", "tv/enemies/cargo_loader_anim.png", (840, 1008), "RGBA"),
    ("enemies/harpoon_drone_anim.png", "tv/enemies/harpoon_drone_anim.png", (840, 1008), "RGBA"),
    ("enemies/dock_crusher_anim.png", "tv/enemies/dock_crusher_anim.png", (840, 1008), "RGBA"),
    ("enemies/tidebreaker_anim.png", "tv/enemies/tidebreaker_anim.png", (840, 1008), "RGBA"),
    ("enemies/scrap_stalker_anim.png", "tv/enemies/scrap_stalker_anim.png", (840, 1008), "RGBA"),
    ("enemies/core_jammer_anim.png", "tv/enemies/core_jammer_anim.png", (840, 1008), "RGBA"),
    ("enemies/furnace_brawler_anim.png", "tv/enemies/furnace_brawler_anim.png", (840, 1008), "RGBA"),
    ("enemies/palace_sentinel_anim.png", "tv/enemies/palace_sentinel_anim.png", (840, 1008), "RGBA"),
    ("enemies/vox_avatar_anim.png", "tv/enemies/vox_avatar_anim.png", (840, 1008), "RGBA"),
    ("enemies/shadow_prime_anim.png", "tv/enemies/shadow_prime_anim.png", (840, 1008), "RGBA"),
)


def generate_variant(source_rel: str, output_rel: str, size: tuple[int, int], mode: str) -> None:
    source = ASSETS / source_rel
    output = ASSETS / output_rel
    if not source.is_file():
        raise FileNotFoundError(source)
    with Image.open(source) as image:
        converted = image.convert(mode)
        resized = converted.resize(size, Image.Resampling.LANCZOS)
        # Restore local edge contrast after reduction without changing identity,
        # palette direction, pose, or transparency.
        if mode == "RGBA":
            rgb = resized.convert("RGB").filter(
                ImageFilter.UnsharpMask(radius=0.8, percent=115, threshold=3)
            )
            # Do not add a second aggressive sharpen pass to the detailed
            # enemies; it created thick crunchy pixels and uneven outlines.
            alpha = resized.getchannel("A")
            if source_rel.startswith("runtime/enemies/"):
                alpha = alpha.point(lambda value: 255 if value >= 72 else 0)
            rgb.putalpha(alpha)
            resized = rgb
        else:
            resized = resized.filter(ImageFilter.UnsharpMask(radius=0.7, percent=90, threshold=3))
        output.parent.mkdir(parents=True, exist_ok=True)
        resized.save(output, format="PNG", optimize=True, compress_level=9)


def refresh_manifest() -> None:
    manifest_path = ASSETS / "asset_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = []
    for path in sorted(ASSETS.rglob("*")):
        if not path.is_file() or path == manifest_path:
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
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    for spec in VARIANTS:
        generate_variant(*spec)
    refresh_manifest()
    print(f"Generated {len(VARIANTS)} Android TV variants and refreshed manifest")


if __name__ == "__main__":
    main()
