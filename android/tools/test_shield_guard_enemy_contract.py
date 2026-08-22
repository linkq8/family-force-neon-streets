#!/usr/bin/env python3
"""Release contract for Shield Guard art, roster loading, and directional guard."""

from pathlib import Path
from PIL import Image, ImageChops

ANDROID = Path(__file__).resolve().parents[1]
ASSETS = ANDROID / "app/src/main/assets"
JAVA = ANDROID / "app/src/main/java/com/familyforce/neonstreets"

game = (JAVA / "GameView.java").read_text(encoding="utf-8")
archetypes = (JAVA / "EnemyArchetype.java").read_text(encoding="utf-8")
rosters = (JAVA / "StageRoster.java").read_text(encoding="utf-8")
builder = (ANDROID / "tools/build_shield_guard_enemy.py").read_text(encoding="utf-8")

assert "ENEMY_TYPE_COUNT = EnemyArchetype.COUNT" in game
assert 'loadBitmapSampled("enemies/shield_guard.png"' in game
assert "enemy.type == ENEMY_SHIELD_GUARD && enemy.guard > 0" in game
assert "if (hitFromFront)" in game
assert 'diagnostics.event("GUARD_BREAK z="' in game
assert 'new EnemyArchetype("shield_guard", "SHIELD GUARD"' in archetypes
assert "EnemyArchetype.STRIKER, EnemyArchetype.SHIELD_GUARD}" in rosters
assert "StageRoster.includes(requestedStage, type)" in game
assert "spawnEnemy(8, ENEMY_STRIKER, 5760, 270);" in game
assert "component_boxes(foreground_candidates(image))" in builder
assert "if len(selected) == COLS" in builder

for relative, expected in (
    ("enemies/shield_guard.png", (512, 512)),
    ("enemies/shield_guard_anim.png", (960, 1152)),
    ("tv/enemies/shield_guard_anim.png", (720, 864)),
):
    with Image.open(ASSETS / relative) as image:
        assert image.size == expected, (relative, image.size)
        assert image.mode == "RGBA", (relative, image.mode)

with Image.open(ASSETS / "enemies/shield_guard_anim.png") as source:
    atlas = source.convert("RGBA")
for row in range(6):
    frames = [atlas.crop((column * 160, row * 192, (column + 1) * 160, (row + 1) * 192))
              for column in range(6)]
    assert all(frame.getchannel("A").getbbox() for frame in frames)
    assert max(
        ImageChops.difference(frames[0].getchannel("A"), frame.getchannel("A")).getbbox()
        is not None for frame in frames[1:]
    )
    for column, frame in enumerate(frames):
        bbox = frame.getchannel("A").getbbox()
        assert bbox is not None
        assert min(bbox[0], bbox[1], 160 - bbox[2], 192 - bbox[3]) >= 12, (
            row, column, "unsafe motion margin", bbox)

with Image.open(ASSETS / "tv/enemies/shield_guard_anim.png") as source:
    tv = source.convert("RGBA")
for row in range(6):
    for column in range(6):
        bbox = tv.crop((column * 120, row * 144, (column + 1) * 120,
                        (row + 1) * 144)).getchannel("A").getbbox()
        assert bbox is not None
        assert min(bbox[0], bbox[1], 120 - bbox[2], 144 - bbox[3]) >= 8, (
            row, column, "unsafe TV margin", bbox)

print("Shield Guard enemy contract: PASS (36 frames, 12px/8px safe gutters, guard)")
