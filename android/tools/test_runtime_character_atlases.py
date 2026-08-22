#!/usr/bin/env python3
"""Verify placement-locked high-density atlases and filtered minification."""

from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "android/app/src/main/assets"
JAVA = (ROOT / "android/app/src/main/java/com/familyforce/neonstreets/GameView.java").read_text()

heroes = {"parent": 126, "adam": 77, "shaikha": 77, "sulaiman": 88}
enemies = {"grunt": 120, "skater": 110, "brute": 136, "boss": 160,
           "striker": 116, "shield_guard": 132}
density = 2.25

for name, cell in heroes.items():
    cell = max(192, round(cell * density))
    path = ASSETS / f"runtime/heroes/{name}_anim.png"
    with Image.open(path) as atlas:
        assert atlas.size == (cell * 8, cell * 11) and atlas.mode == "RGBA"
        assert min(atlas.getchannel("A").getdata()) == 0
        first = atlas.crop((0, 0, cell, cell))
        assert any(ImageChops.difference(first, atlas.crop((i * cell, 0, (i + 1) * cell, cell))).getbbox()
                   for i in range(1, 8))

for name, height in enemies.items():
    height = round(height * density)
    width = round(height * 160 / 192)
    path = ASSETS / f"runtime/enemies/{name}_anim.png"
    with Image.open(path) as atlas:
        assert atlas.size == (width * 6, height * 6) and atlas.mode == "RGBA"
        assert min(atlas.getchannel("A").getdata()) == 0

assert 'loadBitmap("runtime/heroes/" + stem)' in JAVA
assert 'loadBitmap("runtime/enemies/" + stem)' in JAVA
assert 'Paint enemyPaint = crispCharacterPaint' in JAVA
assert 'Paint.FILTER_BITMAP_FLAG' in JAVA
animated = JAVA[JAVA.index("private void drawAnimatedHero"):JAVA.index("private void drawHeldWeapon")]
assert "crispCharacterPaint" in animated and "heroPaint" not in animated
print("Runtime character atlas contract: PASS (10 placement-locked 2.25x atlases)")
