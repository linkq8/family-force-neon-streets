#!/usr/bin/env python3
"""Validate Android game assets, formats, transparency, and audio."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import wave

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "android" / "app" / "src" / "main" / "assets"
RES = ROOT / "android" / "app" / "src" / "main" / "res"
MANIFEST = ROOT / "android" / "app" / "src" / "main" / "AndroidManifest.xml"

STYLE_FORMULA = (
    "High-detail retro arcade pixel art rendered at a modern 360p-to-720p game "
    "resolution, with fine 2–4 pixel clusters, crisp edges, selective dithering, "
    "and no oversized block pixels. Athletic readable silhouettes use dark navy "
    "outlines, expressive recognizable faces, dynamic foreshortening, and "
    "slightly exaggerated 1990s beat-’em-up proportions. Night streets use "
    "indigo, teal, and warm amber; heroes use distinct red-gold, green-purple, "
    "pink-ice, and blue-red palettes. Energetic family-friendly lighting and "
    "strong foreground contrast maintain a consistent three-quarter side-view "
    "belt-brawler perspective."
)


IMAGE_CONTRACT = {
    "backgrounds/street.png": ((1376, 768), "RGB"),
    "backgrounds/street_hd.png": ((2048, 1152), "RGB"),
    "backgrounds/street_retro.png": ((1280, 720), "RGB"),
    "backgrounds/stage_market.png": ((1376, 768), "RGB"),
    "backgrounds/stage_transit.png": ((1376, 768), "RGB"),
    "backgrounds/stage_harbor.png": ((1376, 768), "RGB"),
    "backgrounds/stage_palace.png": ((1376, 768), "RGB"),
    "backgrounds/title.png": ((1376, 768), "RGB"),
    "ui/actors.png": ((128, 512), "RGBA"),
    "ui/portraits.png": ((128, 128), "RGBA"),
    "ui/logo.png": ((1024, 384), "RGBA"),
    "ui/panel_9slice.png": ((96, 96), "RGBA"),
    "ui/touch_buttons.png": ((512, 128), "RGBA"),
    "ui/item_icons.png": ((512, 128), "RGBA"),
    "enemies/grunt.png": ((512, 512), "RGBA"),
    "enemies/skater.png": ((512, 512), "RGBA"),
    "enemies/brute.png": ((512, 512), "RGBA"),
    "enemies/boss.png": ((512, 512), "RGBA"),
    "enemies/striker.png": ((512, 512), "RGBA"),
    "enemies/shield_guard.png": ((512, 512), "RGBA"),
    "items/food.png": ((128, 128), "RGBA"),
    "items/energy.png": ((128, 128), "RGBA"),
    "items/token.png": ((128, 128), "RGBA"),
    "items/bat.png": ((128, 128), "RGBA"),
    "fx/hit_fx.png": ((512, 512), "RGBA"),
    "fx/special_fx.png": ((512, 256), "RGBA"),
    "fx/shadow.png": ((128, 64), "RGBA"),
    "fx/weapon_trail_fx.png": ((512, 512), "RGBA"),
    "fx/break_fx.png": ((512, 512), "RGBA"),
    "ui/combat_action_icons.png": ((512, 256), "RGBA"),
    "weapons/bat.png": ((128, 128), "RGBA"),
    "weapons/pipe.png": ((128, 128), "RGBA"),
    "weapons/mallet.png": ((128, 128), "RGBA"),
    "weapons/sign.png": ((128, 128), "RGBA"),
    "props/cone.png": ((128, 128), "RGBA"),
    "props/crate.png": ((192, 192), "RGBA"),
    "props/trashcan.png": ((192, 192), "RGBA"),
}
for hero in range(1, 5):
    IMAGE_CONTRACT[f"heroes/hero_{hero}.png"] = ((256, 512), "RGBA")
    IMAGE_CONTRACT[f"heroes/hero_{hero}_actions.png"] = ((512, 256), "RGBA")
    IMAGE_CONTRACT[f"heroes/hero_{hero}_portrait.png"] = ((256, 256), "RGBA")
for name in ("parent", "adam", "shaikha", "sulaiman"):
    IMAGE_CONTRACT[f"heroes/{name}.png"] = ((256, 384), "RGBA")
    IMAGE_CONTRACT[f"heroes/{name}_portrait.png"] = ((256, 256), "RGBA")

WAV_NAMES = ("punch", "damage", "pickup", "confirm", "victory", "jump", "special")
ICON_DENSITIES = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}

HERO_ANIMATION_CONTRACT = {
    f"heroes/{name}_anim.png": (8, 11, 192, 192)
    for name in ("parent", "adam", "shaikha", "sulaiman")
}
ENEMY_ANIMATION_CONTRACT = {
    f"enemies/{name}_anim.png": (6, 6, 160, 192)
    for name in ("grunt", "skater", "brute", "boss", "striker", "shield_guard")
}

GRID_SHEET_CONTRACT = {
    "fx/hit_fx.png": (4, 4),
    "fx/special_fx.png": (4, 2),
    # These generated sheets intentionally use taller 128x256 cells.
    "fx/weapon_trail_fx.png": (4, 2),
    "fx/break_fx.png": (4, 2),
    "ui/combat_action_icons.png": (4, 2),
}


def validate_image(relative: str, expected_size: tuple[int, int],
                   expected_mode: str) -> None:
    path = ASSETS / relative
    assert path.is_file(), f"missing {relative}"
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        assert image.format == "PNG", (relative, image.format)
        assert image.size == expected_size, (relative, image.size, expected_size)
        assert image.mode == expected_mode, (relative, image.mode, expected_mode)
        if expected_mode == "RGBA":
            alpha = image.getchannel("A")
            minimum, maximum = alpha.getextrema()
            assert minimum == 0 and maximum > 0, (relative, minimum, maximum)
            if relative != "fx/shadow.png":
                assert maximum == 255, (relative, minimum, maximum)
            if relative.startswith(("heroes/", "enemies/", "ui/actors", "ui/portraits")):
                bad_clear_pixels = sum(
                    1 for red, green, blue, opacity in image.getdata()
                    if opacity == 0 and (red != 0 or green != 0 or blue != 0)
                )
                assert bad_clear_pixels == 0, (relative, bad_clear_pixels)
            personalized = relative.startswith(
                ("heroes/parent", "heroes/adam", "heroes/shaikha", "heroes/sulaiman")
            )
            if personalized:
                half = image.resize(
                    (image.width // 2, image.height // 2), Image.Resampling.NEAREST
                ).resize(image.size, Image.Resampling.NEAREST)
                assert half.tobytes() == image.tobytes(), f"non-2px clusters: {relative}"
                visible_rgb = {
                    (red, green, blue)
                    for red, green, blue, opacity in image.getdata()
                    if opacity > 0
                }
                palette_limit = 112 if relative.endswith("_portrait.png") else 96
                assert len(visible_rgb) <= palette_limit, (
                    relative, len(visible_rgb), palette_limit
                )
                if not relative.endswith("_portrait.png"):
                    assert set(alpha.getdata()) <= {0, 255}, f"soft matte: {relative}"
                    bbox = alpha.getbbox()
                    assert bbox is not None
                    left, top, right, bottom = bbox
                    assert min(left, top, image.width - right, image.height - bottom) >= 8, (
                        relative, bbox
                    )


def validate_audio() -> None:
    for name in WAV_NAMES:
        path = ASSETS / "audio" / f"{name}.wav"
        assert path.is_file(), path
        with wave.open(str(path), "rb") as wav_file:
            assert wav_file.getnchannels() == 1, name
            assert wav_file.getsampwidth() == 2, name
            assert wav_file.getframerate() == 44_100, name
            duration = wav_file.getnframes() / wav_file.getframerate()
            assert 0.05 <= duration <= 4.0, (name, duration)

    expected_music_seconds = {"menu": 30.1, "stage": 45.1}
    for name, expected_seconds in expected_music_seconds.items():
        music_path = ASSETS / "audio" / f"{name}.ogg"
        assert music_path.is_file()
        probe = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries",
            "stream=codec_name,sample_rate,channels:format=duration", "-of", "json",
            str(music_path),
        ], check=True, capture_output=True, text=True)
        payload = json.loads(probe.stdout)
        stream = payload["streams"][0]
        assert stream["codec_name"] == "vorbis", stream
        assert int(stream["sample_rate"]) == 48_000, stream
        assert int(stream["channels"]) == 2, stream
        assert abs(float(payload["format"]["duration"]) - expected_seconds) <= 0.15, payload


def validate_grid_sheets() -> None:
    """Keep runtime slicing in lockstep with the packaged effect/icon grids."""
    for relative, (columns, rows) in GRID_SHEET_CONTRACT.items():
        with Image.open(ASSETS / relative) as source:
            image = source.convert("RGBA")
        assert image.width % columns == 0 and image.height % rows == 0, (
            relative, image.size, columns, rows
        )
        cell_width = image.width // columns
        cell_height = image.height // rows
        hashes = set()
        for row in range(rows):
            for column in range(columns):
                cell = image.crop((
                    column * cell_width, row * cell_height,
                    (column + 1) * cell_width, (row + 1) * cell_height,
                ))
                assert cell.getchannel("A").getbbox() is not None, (
                    relative, row, column, "empty cell"
                )
                hashes.add(hashlib.sha256(cell.tobytes()).digest())
        assert len(hashes) == columns * rows, (
            relative, "repeated effect/icon cells", len(hashes)
        )


def validate_animation_atlases() -> int:
    """Validate generated atlases when present; the runtime keeps static fallbacks."""
    contracts = HERO_ANIMATION_CONTRACT | ENEMY_ANIMATION_CONTRACT
    present = [relative for relative in contracts if (ASSETS / relative).is_file()]
    hero_present = [relative for relative in HERO_ANIMATION_CONTRACT if relative in present]
    enemy_present = [relative for relative in ENEMY_ANIMATION_CONTRACT if relative in present]
    assert len(hero_present) in (0, len(HERO_ANIMATION_CONTRACT)), (
        "partial hero atlas pack", hero_present
    )
    assert len(enemy_present) in (0, len(ENEMY_ANIMATION_CONTRACT)), (
        "partial enemy atlas pack", enemy_present
    )
    for relative in present:
        columns, rows, cell_width, cell_height = contracts[relative]
        with Image.open(ASSETS / relative) as source_image:
            image = source_image.convert("RGBA")
        assert image.size == (columns * cell_width, rows * cell_height), (
            relative, image.size
        )
        assert image.width <= 4096 and image.height <= 4096, relative
        for row in range(rows):
            hashes = set()
            for frame in range(columns):
                cell = image.crop((
                    frame * cell_width, row * cell_height,
                    (frame + 1) * cell_width, (row + 1) * cell_height,
                ))
                alpha = cell.getchannel("A")
                assert alpha.getbbox() is not None, (relative, row, frame, "empty")
                hashes.add(hashlib.sha256(cell.tobytes()).digest())
            minimum_unique = 3 if relative.startswith("heroes/") else 2
            assert len(hashes) >= minimum_unique, (
                relative, row, "static row", len(hashes), minimum_unique
            )
    return len(present)


def validate_launcher_icons() -> None:
    for density, scale in ICON_DENSITIES.items():
        directory = RES / f"mipmap-{density}"
        expected = {
            "ic_launcher.png": round(48 * scale),
            "ic_launcher_round.png": round(48 * scale),
            "ic_launcher_foreground.png": round(108 * scale),
            "ic_launcher_monochrome.png": round(108 * scale),
        }
        for filename, side in expected.items():
            path = directory / filename
            assert path.is_file(), path
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                assert image.format == "PNG", (path, image.format)
                assert image.mode == "RGBA", (path, image.mode)
                assert image.size == (side, side), (path, image.size, side)
                assert image.getchannel("A").getbbox() is not None, path

    foreground = Image.open(
        RES / "mipmap-xxxhdpi" / "ic_launcher_foreground.png"
    ).convert("RGBA")
    bbox = foreground.getchannel("A").getbbox()
    assert bbox is not None
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    assert width / foreground.width <= 0.66, ("adaptive icon width", bbox)
    assert height / foreground.height <= 0.66, ("adaptive icon height", bbox)

    adaptive_v26 = (RES / "mipmap-anydpi" / "ic_launcher.xml").read_text(
        encoding="utf-8"
    )
    adaptive_v33 = (RES / "mipmap-anydpi-v33" / "ic_launcher.xml").read_text(
        encoding="utf-8"
    )
    assert "@mipmap/ic_launcher_foreground" in adaptive_v26
    assert "<monochrome" not in adaptive_v26
    assert "@mipmap/ic_launcher_monochrome" in adaptive_v33
    manifest = MANIFEST.read_text(encoding="utf-8")
    assert 'android:icon="@mipmap/ic_launcher"' in manifest
    assert 'android:roundIcon="@mipmap/ic_launcher_round"' in manifest
    assert 'android:resizeableActivity="true"' in manifest


def validate_manifest() -> int:
    manifest_path = ASSETS / "asset_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["visual_formula"] == STYLE_FORMULA
    assert ("no family likeness claims" in payload["status"]
            or "direct-reference family character pack" in payload["status"])
    records = {record["path"]: record for record in payload["files"]}
    disk_files = {
        path.relative_to(ASSETS).as_posix(): path
        for path in ASSETS.rglob("*")
        if path.is_file() and path.name != manifest_path.name
    }
    assert set(records) == set(disk_files), (set(records) ^ set(disk_files))
    for relative, path in disk_files.items():
        assert records[relative]["bytes"] == path.stat().st_size, relative
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert records[relative]["sha256"] == digest, relative
    return len(records)


def main() -> None:
    for relative, (size, mode) in IMAGE_CONTRACT.items():
        validate_image(relative, size, mode)
    validate_grid_sheets()
    validate_audio()
    animation_count = validate_animation_atlases()
    validate_launcher_icons()
    count = validate_manifest()
    print(f"Validated {len(IMAGE_CONTRACT)} base PNGs, {animation_count} animation atlases, "
          f"{len(WAV_NAMES)} WAVs, "
          f"two Vorbis loops, one adaptive launcher icon set, and "
          f"{count} manifested files.")


if __name__ == "__main__":
    main()
