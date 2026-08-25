#!/usr/bin/env python3
"""Strict contract for action-only UHD/runtime/TV animation clips."""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "android/app/src/main/assets"
PRODUCTION = ROOT / "assets/imagegen/android/animation-clips-v1"
JAVA = (ROOT / "android/app/src/main/java/com/familyforce/neonstreets/SpriteAnimator.java").read_text()

HEROES = {
    "parent": ("idle", "walk", "punch", "kick", "heavy_punch", "heavy_kick",
               "jump", "special", "link", "hurt", "knockdown"),
    "adam": ("idle", "walk", "punch", "kick", "heavy_punch", "heavy_kick",
             "jump", "special", "link", "hurt", "knockdown"),
}
ENEMIES = {
    "grunt": ("idle", "walk", "attack_1", "attack_2", "hurt", "knockdown"),
    "lantern_courier": ("idle", "walk", "attack_1", "attack_2", "hurt", "knockdown"),
}


def contaminated_edge_count(image: Image.Image) -> int:
    px = image.load()
    count = 0
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = px[x, y]
            if not a or min(r, g, b) < 218 or max(r, g, b) - min(r, g, b) > 24:
                continue
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < image.width and 0 <= ny < image.height and px[nx, ny][3] == 0:
                    count += 1
                    break
    return count


def validate_actor(kind: str, actor: str, actions: tuple[str, ...], columns: int,
                   legacy_columns: int) -> None:
    for action in actions:
        source = PRODUCTION / kind / actor / action / "source_uhd.png"
        with Image.open(source) as image:
            assert image.size == (3840, 2160), (source, image.size)
            assert image.mode == "RGBA", (source, image.mode)
            assert image.getchannel("A").getbbox(), source
        for tier in ("", "runtime/", "tv/"):
            path = ASSETS / tier / "clips" / kind / actor / f"{action}.png"
            atlas_path = ASSETS / tier / kind / f"{actor}_anim.png"
            assert path.is_file(), path
            assert atlas_path.is_file(), atlas_path
            with Image.open(path) as opened:
                image = opened.convert("RGBA")
            with Image.open(atlas_path) as atlas:
                expected_cell_width = atlas.width // legacy_columns
                expected_cell_height = atlas.height // len(actions)
            expected_size = ((2160, 154) if kind == "enemies" and tier == "tv/"
                             else (expected_cell_width * columns, expected_cell_height))
            assert image.size == expected_size, (
                path, image.size, expected_size
            )
            assert set(image.getchannel("A").getdata()) <= {0, 255}, f"soft alpha: {path}"
            assert all(a or (r == g == b == 0) for r, g, b, a in image.getdata()), (
                f"dirty transparent RGB: {path}"
            )
            assert contaminated_edge_count(image) == 0, f"white matte edge: {path}"
            cell_width = image.width // columns
            cells = [image.crop((i * cell_width, 0, (i + 1) * cell_width, image.height))
                     for i in range(columns)]
            assert all(cell.getchannel("A").getbbox() for cell in cells), f"empty frame: {path}"
            unique = {cell.tobytes() for cell in cells}
            assert len(unique) == columns, f"all 12 frames must be distinct: {path}"
            if actor == "adam":
                for cell in cells:
                    opaque = [pixel for pixel in cell.getdata() if pixel[3]]
                    dark_ratio = sum(max(pixel[:3]) < 60 for pixel in opaque) / len(opaque)
                    assert dark_ratio < 0.19, f"Adam body has oversized black fills: {path}"
                    assert any(g >= 120 and g > r * 1.5 and g > b * 1.5
                               for r, g, b, _ in opaque), f"Adam green fill missing: {path}"


for actor, actions in HEROES.items():
    validate_actor("heroes", actor, actions, 12, 8)
for actor, actions in ENEMIES.items():
    validate_actor("enemies", actor, actions, 12, 6)

assert "MIN_CHARACTER_CLIP_FPS = 12" in JAVA
assert "Math.max(MIN_CHARACTER_CLIP_FPS" in JAVA
assert "void bindClips(" in JAVA
print("Separate animation contract: PASS (34 UHD action sources, 12 distinct frames/action, minimum 12 FPS)")
