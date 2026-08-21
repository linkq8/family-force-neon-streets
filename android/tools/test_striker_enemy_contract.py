#!/usr/bin/env python3
"""Release guard for the first expanded enemy archetype."""

from pathlib import Path
from PIL import Image


ANDROID = Path(__file__).resolve().parents[1]
ASSETS = ANDROID / "app/src/main/assets"
SOURCE = (ANDROID / "app/src/main/java/com/familyforce/neonstreets/GameView.java").read_text()

required_code = (
    "private static final int ENEMY_STRIKER = 4;",
    "private static final int ENEMY_TYPE_COUNT = 5;",
    '"grunt", "skater", "brute", "boss", "striker"',
    'enemyArt[ENEMY_STRIKER] = loadBitmapSampled("enemies/striker.png"',
    "type == ENEMY_STRIKER ? 76",
    "enemy.type == ENEMY_STRIKER ? 1.48f",
    "enemy.type == ENEMY_STRIKER ? 16",
    'lastHitEnemy.type == ENEMY_STRIKER ? "STRIKER"',
)
for snippet in required_code:
    assert snippet in SOURCE, f"missing Striker runtime contract: {snippet}"

assert SOURCE.count("spawnEnemy(") >= 1
assert SOURCE.count("spawnEnemy(0, ENEMY_STRIKER") == 1
assert SOURCE.count("ENEMY_STRIKER") >= 16

for relative, dimensions in (
    ("enemies/striker.png", (512, 512)),
    ("enemies/striker_anim.png", (960, 1152)),
    ("tv/enemies/striker_anim.png", (720, 864)),
):
    with Image.open(ASSETS / relative) as image:
        assert image.size == dimensions, (relative, image.size)
        assert image.mode == "RGBA", (relative, image.mode)
        assert image.getchannel("A").getbbox() is not None, relative

atlas = Image.open(ASSETS / "enemies/striker_anim.png").convert("RGBA")
clustered = atlas.resize((480, 576), Image.Resampling.NEAREST).resize(
    atlas.size, Image.Resampling.NEAREST
)
assert clustered.tobytes() == atlas.tobytes(), "Striker atlas lost exact 2px clusters"
for row in range(6):
    hashes = {
        atlas.crop((column * 160, row * 192, (column + 1) * 160, (row + 1) * 192)).tobytes()
        for column in range(6)
    }
    assert len(hashes) >= 3, (row, "static Striker animation")

print("Striker enemy contract: PASS (runtime, 36 frames, TV variant, 2px clusters)")
