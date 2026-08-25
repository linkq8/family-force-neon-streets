#!/usr/bin/env python3
"""Market Enforcer keeps identity and receives a true 12-frame walk."""

from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "android/app/src/main/assets"
SOURCE = ROOT / "assets/imagegen/android/animation-clips-v2/enemies/market_enforcer/walk/source_uhd.png"
GAME = (ROOT / "android/app/src/main/java/com/familyforce/neonstreets/GameView.java").read_text()
ANIMATOR = (ROOT / "android/app/src/main/java/com/familyforce/neonstreets/SpriteAnimator.java").read_text()

with Image.open(SOURCE) as image:
    assert image.size == (3840, 2160), image.size

for tier in ("", "runtime/", "tv/"):
    directory = ASSETS / tier / "clips/enemies/market_enforcer"
    for action in ("idle", "walk", "attack_1", "attack_2", "hurt", "knockdown"):
        path = directory / f"{action}.png"
        with Image.open(path) as opened:
            image = opened.convert("RGBA")
        columns = 12 if action == "walk" else 6
        assert image.width % columns == 0, (path, image.size)
        cell_width = image.width // columns
        frames = [image.crop((i * cell_width, 0, (i + 1) * cell_width, image.height))
                  for i in range(columns)]
        assert all(frame.getchannel("A").getbbox() for frame in frames), path
        if action == "walk":
            assert len({frame.tobytes() for frame in frames}) == 12, path
            assert set(image.getchannel("A").getdata()) <= {0, 255}, path

assert "new int[]{6, STRICT_ANIM_COLUMNS, 6, 6, 6, 6}" in GAME
assert "type == EnemyArchetype.MARKET_ENFORCER" in GAME
assert "clips != null ? columns" in ANIMATOR
print("Market Enforcer walk contract: PASS (identity retained; 12 distinct walk frames)")
