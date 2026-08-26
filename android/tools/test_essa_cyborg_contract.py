#!/usr/bin/env python3
"""Strict production contract for the heavy iron-cyborg Essa redesign."""

from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "android/app/src/main/assets"
SOURCE = ROOT / "assets/imagegen/android/character-redraw-v6/essa"
PRODUCTION = ROOT / "assets/imagegen/android/animation-clips-v3/heroes/parent"
ACTIONS = ("idle", "walk", "punch", "kick", "heavy_punch", "heavy_kick",
           "jump", "special", "link", "hurt", "knockdown")

with Image.open(SOURCE / "model_sheet.png") as image:
    assert image.size == (1536, 1024), image.size

for action in ACTIONS:
    with Image.open(SOURCE / "actions" / f"{action}.png") as image:
        assert image.size == (1536, 1024), (action, image.size)
    with Image.open(PRODUCTION / action / "source_uhd.png") as image:
        assert image.size == (3840, 2160), (action, image.size)
    for tier in ("", "runtime/", "tv/", "uhd/"):
        path = ASSETS / tier / "clips/heroes/parent" / f"{action}.png"
        with Image.open(path) as opened:
            clip = opened.convert("RGBA")
        assert clip.width % 12 == 0, (path, clip.size)
        assert set(clip.getchannel("A").getdata()) <= {0, 255}, path
        cell = clip.width // 12
        assert all(clip.crop((i * cell, 0, (i + 1) * cell, clip.height))
                   .getchannel("A").getbbox() for i in range(12)), path

for name in ("parent_portrait.png", "parent_portrait_ready.png"):
    with Image.open(ASSETS / "heroes" / name) as opened:
        portrait = opened.convert("RGBA")
    assert portrait.size == (256, 256), (name, portrait.size)
    assert portrait.getchannel("A").getbbox(), name
    assert set(portrait.getchannel("A").getdata()) <= {0, 255}, name

for path, size in ((ASSETS / "heroes/parent.png", (256, 384)),
                   (ASSETS / "tv/heroes/parent_hd.png", (384, 576))):
    with Image.open(path) as image:
        assert image.size == size, (path, image.size)
        assert image.mode == "RGBA", (path, image.mode)

print("Essa cyborg contract: PASS (model + 132 action drawings + portraits + fallback)")
