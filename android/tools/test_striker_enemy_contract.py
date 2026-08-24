#!/usr/bin/env python3
"""Release guard for the first expanded enemy archetype."""

from collections import deque
from pathlib import Path
from PIL import Image


ANDROID = Path(__file__).resolve().parents[1]
ASSETS = ANDROID / "app/src/main/assets"
SOURCE = (ANDROID / "app/src/main/java/com/familyforce/neonstreets/GameView.java").read_text()
ARCHETYPES = (ANDROID / "app/src/main/java/com/familyforce/neonstreets/EnemyArchetype.java").read_text()
BUILDER = (ANDROID / "tools/build_striker_enemy.py").read_text()

required_code = (
    "private static final int ENEMY_STRIKER = EnemyArchetype.STRIKER;",
    "private static final int ENEMY_TYPE_COUNT = EnemyArchetype.COUNT;",
    'enemyArt[ENEMY_STRIKER] = loadBitmapSampled("enemies/striker.png"',
    "EnemyArchetype archetype = EnemyArchetype.of(type);",
    "EnemyArchetype.of(enemy.type).speed",
    "EnemyArchetype archetype = EnemyArchetype.of(enemy.type);",
    "EnemyArchetype.of(lastHitEnemy.type).displayName",
)
for snippet in required_code:
    assert snippet in SOURCE, f"missing Striker runtime contract: {snippet}"
assert 'type("striker", "STRIKER"' in ARCHETYPES
assert "complete_component_rows" in BUILDER
assert "component_boxes" in BUILDER
assert "if component_rows[row] is not None" in BUILDER

assert SOURCE.count("spawnEnemy(") >= 1
assert SOURCE.count("spawnEnemy(2, EnemyArchetype.STRIKER") >= 1
assert SOURCE.count("ENEMY_STRIKER") >= 3

for relative, dimensions in (
    ("enemies/striker.png", (512, 512)),
    ("enemies/striker_anim.png", (960, 1152)),
    ("tv/enemies/striker_anim.png", (840, 1008)),
):
    with Image.open(ASSETS / relative) as image:
        assert image.size == dimensions, (relative, image.size)
        assert image.mode == "RGBA", (relative, image.mode)
        assert image.getchannel("A").getbbox() is not None, relative

atlas = Image.open(ASSETS / "enemies/striker_anim.png").convert("RGBA")
for row in range(6):
    cells = [
        atlas.crop((column * 160, row * 192, (column + 1) * 160, (row + 1) * 192))
        for column in range(6)
    ]
    hashes = {
        cell.tobytes() for cell in cells
    }
    assert len(hashes) >= 3, (row, "static Striker animation")
    for column, cell in enumerate(cells):
        alpha = cell.getchannel("A")
        bbox = alpha.getbbox()
        assert bbox is not None
        margins = (bbox[0], bbox[1], 160 - bbox[2], 192 - bbox[3])
        assert min(margins) >= 12, (row, column, "unsafe motion margin", margins)
        pixels = alpha.load()
        seen = set()
        components = 0
        for y in range(192):
            for x in range(160):
                if pixels[x, y] == 0 or (x, y) in seen:
                    continue
                components += 1
                queue = deque([(x, y)])
                seen.add((x, y))
                while queue:
                    px, py = queue.popleft()
                    for nx, ny in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
                        if (0 <= nx < 160 and 0 <= ny < 192
                                and pixels[nx, ny] and (nx, ny) not in seen):
                            seen.add((nx, ny))
                            queue.append((nx, ny))
        assert components == 1, (row, column, "detached panel-overflow fragments", components)

walk_cells = [atlas.crop((column * 160, 192, (column + 1) * 160, 384)).tobytes()
              for column in range(6)]
assert len(set(walk_cells)) == 6, "walk bob timing must keep six visible frames"
attack_cells = [atlas.crop((column * 160, 384, (column + 1) * 160, 576)).tobytes()
                for column in range(6)]
assert len(set(attack_cells)) >= 5, "new compact punch must keep readable anticipation and recoil"
for column in range(6):
    cell = atlas.crop((column * 160, 192, (column + 1) * 160, 384))
    bbox = cell.getchannel("A").getbbox()
    assert bbox is not None and bbox[2] <= 148, ("walk glove clipped at right edge", column, bbox)

tv = Image.open(ASSETS / "tv/enemies/striker_anim.png").convert("RGBA")
for row in range(6):
    for column in range(6):
        bbox = tv.crop((column * 140, row * 168, (column + 1) * 140,
                        (row + 1) * 168)).getchannel("A").getbbox()
        assert bbox is not None
        assert min(bbox[0], bbox[1], 140 - bbox[2], 168 - bbox[3]) >= 8, (
            row, column, "unsafe TV margin", bbox)

runtime = Image.open(ASSETS / "runtime/enemies/striker_anim.png").convert("RGBA")
runtime_clustered = runtime.resize((runtime.width // 2, runtime.height // 2),
                                   Image.Resampling.NEAREST).resize(
    runtime.size, Image.Resampling.NEAREST
)
assert runtime_clustered.tobytes() != runtime.tobytes(), (
    "runtime Striker must be rebuilt from source without 2px clusters"
)

print("Striker enemy contract: PASS (36 frames, dense runtime source, safe gutters)")
