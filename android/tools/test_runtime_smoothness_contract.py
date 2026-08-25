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

warmup = method_body("preloadEnemyAnimationsForZoneAsync")
assert "new Thread" in warmup and "Thread.MIN_PRIORITY" in warmup
assert "decodeEnemyAnimationType" in warmup

spawn_enemy = method_body("spawnEnemy")
assert "atlas.getWidth() / ENEMY_ANIM_COLUMNS" in spawn_enemy
assert "atlas.getHeight() / ENEMY_ANIM_ROWS" in spawn_enemy
assert "ENEMY_ANIM_CELL_WIDTH, ENEMY_ANIM_CELL_HEIGHT" not in spawn_enemy, (
    "TV atlases must never be sliced with the 160x192 authoring-cell constants"
)

# Five real stages use encounter-scoped atlases and distinct progress,
# transitions, and allocation-free enemy palettes.
assert 'STAGE_START_ZONE = {0, 2, 4, 7, 9}' in text
assert 'STAGE_END_ZONE = {1, 3, 6, 8, 13}' in text
assert '"SHADOW CONVERGENCE"' in text
assert 'diagnostics.event("STAGE_CLEAR "' in text
assert 'drawStageTransition(canvas)' in text
draw_enemy = method_body("drawEnemy")
assert "STAGE_ENEMY_FILTERS[stageForZone(enemy.zone)]" in draw_enemy
assert "new ColorMatrix" not in draw_enemy and "new ColorMatrixColorFilter" not in draw_enemy
draw_backdrop = method_body("drawBackdrop")
assert "stagePanProgress" in draw_backdrop
assert "tileWidth" not in draw_backdrop
assert "canvas.scale(-1f" not in draw_backdrop
assert "new Bitmap[5]" in SOURCE.read_text(encoding="utf-8")

expected = {
    "tv/backgrounds/street.png": (960, 536),
    "tv/backgrounds/street_retro.png": (960, 540),
    "tv/backgrounds/stage_market.png": (800, 450),
    "tv/backgrounds/stage_transit.png": (800, 450),
    "tv/backgrounds/stage_harbor.png": (800, 450),
    "tv/backgrounds/stage_palace.png": (800, 450),
    "tv/backgrounds/panoramas/stage_market.png": (1800, 600),
    "tv/backgrounds/panoramas/stage_transit.png": (1800, 600),
    "tv/backgrounds/panoramas/stage_harbor.png": (1800, 600),
    "tv/backgrounds/panoramas/stage_palace.png": (1800, 600),
    "tv/backgrounds/panoramas/stage_final.png": (1800, 600),
}
hero_runtime = {"parent": 126, "adam": 77, "shaikha": 77, "sulaiman": 88}
enemy_runtime = {"brute": (113, 136), "boss": (133, 160), "striker": (97, 116),
                 "shield_guard": (110, 132)}
density = 2.25
for stem, cell in hero_runtime.items():
    cell = max(192, round(cell * density))
    expected[f"runtime/heroes/{stem}_anim.png"] = (cell * 8, cell * 11)
for stem, (cell_width, cell_height) in enemy_runtime.items():
    cell_height = round(cell_height * density)
    cell_width = round(cell_height * 160 / 192)
    expected[f"runtime/enemies/{stem}_anim.png"] = (cell_width * 6, cell_height * 6)
strict_stage_one = ("grunt", "skater", "lantern_courier", "market_enforcer", "keeper_7")
for stem in strict_stage_one:
    expected[f"runtime/enemies/{stem}_anim.png"] = (2016, 1728)
for stem in ("parent", "adam", "shaikha", "sulaiman"):
    expected[f"tv/heroes/{stem}_anim.png"] = (1152, 1584)
enemy_tv_stems = (
    "grunt", "skater", "brute", "boss", "striker", "shield_guard",
    "lantern_courier", "market_enforcer", "keeper_7", "rail_runner",
    "signal_warden", "railmaster_9", "cargo_loader", "harpoon_drone",
    "dock_crusher", "tidebreaker", "scrap_stalker", "core_jammer",
    "furnace_brawler", "palace_sentinel", "vox_avatar", "shadow_prime",
)
for stem in enemy_tv_stems:
    expected[f"tv/enemies/{stem}_anim.png"] = (
        (1176, 1008) if stem in strict_stage_one else (840, 1008)
    )

for relative, dimensions in expected.items():
    path = ASSETS / relative
    assert path.is_file(), f"missing TV asset: {relative}"
    with Image.open(path) as image:
        assert image.size == dimensions, f"unexpected dimensions for {relative}: {image.size}"

# Peak animated combat textures: two hero atlases, two Link rows, at most four
# encounter-roster enemy atlases, and RGB_565 backgrounds. Higher source density
# is deliberate; encounter-scoped loading prevents all six enemy atlases coexisting.
# Worst distinct hero pair is Essa + Sulaiman; same-hero P2 shares the bitmap.
hero_dimensions = {stem: (max(192, round(cell * density)) * 8,
                           max(192, round(cell * density)) * 11)
                   for stem, cell in hero_runtime.items()}
hero_bytes = sum(w * h * 4 for w, h in
                 (hero_dimensions["parent"], hero_dimensions["sulaiman"]))
assist_bytes = sum(max(192, round(hero_runtime[stem] * density)) * 8
                   * max(192, round(hero_runtime[stem] * density)) * 4
                   for stem in ("parent", "sulaiman"))
# Stage 1 can hold at most four of its wider strict atlases concurrently.
enemy_bytes = 4 * 1176 * 1008 * 4
background_bytes = (960 * 536 + 4 * 1800 * 600) * 2
combat_mib = (hero_bytes + assist_bytes + enemy_bytes + background_bytes) / (1024 * 1024)
assert combat_mib < 98.0, f"animated TV combat texture budget too high: {combat_mib:.2f} MiB"

print(f"Runtime smoothness/TV asset contract: PASS ({combat_mib:.2f} MiB animated budget)")
