#!/usr/bin/env python3
"""Release gate for TV asset sizes and no blocking asset work during PLAY."""

from pathlib import Path
import re
from PIL import Image


ANDROID = Path(__file__).resolve().parents[1]
ASSETS = ANDROID / "app/src/main/assets"
SOURCE = ANDROID / "app/src/main/java/com/familyforce/neonstreets/GameView.java"
text = SOURCE.read_text(encoding="utf-8")


def method_body(name: str) -> str:
    match = re.search(rf"\b{name}\s*\([^)]*\)\s*\{{", text)
    if not match:
        raise AssertionError(f"missing method: {name}")
    start = match.end()
    depth = 1
    pos = start
    while pos < len(text) and depth:
        depth += (text[pos] == "{") - (text[pos] == "}")
        pos += 1
    if depth:
        raise AssertionError(f"unterminated method: {name}")
    return text[start:pos - 1]


for method in ("update", "updateGame", "updateEncounter", "prepareEnemyAnimationsForZone",
               "startAssist", "updateAssist"):
    body = method_body(method)
    for forbidden in ("BitmapFactory", "decodeStream", "decodeRegion", "loadBitmap(",
                      "loadEnemyAnimationType", "loadAssistAnimationRow"):
        assert forbidden not in body, f"{method} contains blocking runtime work: {forbidden}"

warmup = method_body("preloadAllEnemyAnimationsAsync")
assert "new Thread" in warmup and "Thread.MIN_PRIORITY" in warmup
assert "decodeEnemyAnimationType" in warmup

spawn_enemy = method_body("spawnEnemy")
assert "atlas.getWidth() / ENEMY_ANIM_COLUMNS" in spawn_enemy
assert "atlas.getHeight() / ENEMY_ANIM_ROWS" in spawn_enemy
assert "ENEMY_ANIM_CELL_WIDTH, ENEMY_ANIM_CELL_HEIGHT" not in spawn_enemy, (
    "TV atlases must never be sliced with the 160x192 authoring-cell constants"
)

expected = {
    "tv/backgrounds/street.png": (960, 536),
    "tv/backgrounds/street_retro.png": (960, 540),
}
for stem in ("parent", "adam", "shaikha", "sulaiman"):
    expected[f"tv/heroes/{stem}_anim.png"] = (1152, 1584)
for stem in ("grunt", "skater", "brute", "boss"):
    expected[f"tv/enemies/{stem}_anim.png"] = (720, 864)

for relative, dimensions in expected.items():
    path = ASSETS / relative
    assert path.is_file(), f"missing TV asset: {relative}"
    with Image.open(path) as image:
        assert image.size == dimensions, f"unexpected dimensions for {relative}: {image.size}"

# Peak animated combat textures for low-RAM TV: two hero atlases, two Link rows,
# four enemy atlases, and both RGB_565 backgrounds. Keep under Android TV's
# recommended 30–40 MiB graphics target with a small tolerance for two-player mode.
hero_bytes = 2 * 1152 * 1584 * 4
assist_bytes = 2 * 1152 * (1584 // 11) * 4
enemy_bytes = 4 * 720 * 864 * 4
background_bytes = (960 * 536 + 960 * 540) * 2
combat_mib = (hero_bytes + assist_bytes + enemy_bytes + background_bytes) / (1024 * 1024)
assert combat_mib < 27.0, f"animated TV combat texture budget too high: {combat_mib:.2f} MiB"

print(f"Runtime smoothness/TV asset contract: PASS ({combat_mib:.2f} MiB animated budget)")
