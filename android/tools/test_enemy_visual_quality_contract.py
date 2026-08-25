#!/usr/bin/env python3
"""Release-blocking visual parity contract for every Stage 1 enemy."""

from pathlib import Path
import importlib.util
import statistics

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app/src/main/assets"
JAVA = (ROOT / "app/src/main/java/com/familyforce/neonstreets/EnemyArchetype.java").read_text()
GAME = (ROOT / "app/src/main/java/com/familyforce/neonstreets/GameView.java").read_text()
SOURCE_ROOT = ROOT.parent / "assets/imagegen/android/enemies"
STRICT = (
    "grunt", "skater", "lantern_courier", "market_enforcer", "keeper_7",
)

BUILDER_PATH = ROOT / "tools/build_strict_enemy_atlas.py"
SPEC = importlib.util.spec_from_file_location("strict_enemy_builder", BUILDER_PATH)
assert SPEC and SPEC.loader
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


def cells(image: Image.Image):
    width, height = image.width // 6, image.height // 6
    for row in range(6):
        for column in range(6):
            yield image.crop((column * width, row * height,
                              (column + 1) * width, (row + 1) * height))


for enemy in STRICT:
    assert f'type("{enemy}"' in JAVA, enemy
    # Individually approved redraws may advance without forcing untouched
    # enemies onto the same source generation. Prefer the newest available
    # source pack while retaining the accepted v2 pack for the other actors.
    source = SOURCE_ROOT / "quality-v3" / enemy
    if not source.is_dir():
        source = SOURCE_ROOT / "quality-v2" / enemy
    model_sheet = source / "model_sheet.png"
    assert model_sheet.is_file(), f"missing identity model sheet: {model_sheet}"
    with Image.open(model_sheet) as model:
        assert model.width >= 1536 and model.height >= 900, (
            model_sheet, model.size, "model sheet below 1536x900"
        )
    for sheet in ("idle_walk.png", "attacks.png", "hurt_knockdown.png"):
        path = source / sheet
        assert path.is_file(), f"missing high-resolution source: {path}"
        with Image.open(path) as image:
            assert image.width >= 1536 and image.height >= 900, (
                path, image.size, "source sheet below 1536x900"
            )
            assert image.width / 6 >= 250 and image.height / 2 >= 450, (
                path, image.size, "source cell below 250x450"
            )
        # Runs the same adaptive split and crop guard used by production. A
        # visually attractive sheet cannot pass if any actor/effect touches
        # the real gutter or would wrap into the neighbouring game frame.
        assert len(BUILDER.split_sheet(path)) == 12, path
    tiers = {
        "base": (ASSETS / f"enemies/{enemy}_anim.png", (1344, 1152), 8),
        "runtime": (ASSETS / f"runtime/enemies/{enemy}_anim.png", (2016, 1728), 12),
        "tv": (ASSETS / f"tv/enemies/{enemy}_anim.png", (1176, 1008), 7),
    }
    for tier, (path, expected, gutter) in tiers.items():
        with Image.open(path).convert("RGBA") as atlas:
            assert atlas.size == expected, (enemy, tier, atlas.size)
            assert all(a in (0, 255) for *_, a in atlas.getdata()), (enemy, tier, "soft alpha")
            boxes = [cell.getchannel("A").getbbox() for cell in cells(atlas)]
            assert all(boxes), (enemy, tier, "empty frame")
            cell_w, cell_h = atlas.width // 6, atlas.height // 6
            for box in boxes:
                assert min(box[0], box[1], cell_w - box[2], cell_h - box[3]) >= gutter, (enemy, tier, box)
            # Idle and walk must stay large and stable; falling frames are excluded.
            standing = boxes[:12]
            ratios = [(box[3] - box[1]) / cell_h for box in standing]
            assert statistics.median(ratios) >= .64, (enemy, tier, "too small", statistics.median(ratios))
            assert max(ratios) - min(ratios) <= .05, (enemy, tier, "scale drift", ratios)
            lengths = [max(box[2] - box[0], box[3] - box[1]) for box in boxes]
            reference = statistics.median(lengths[:12])
            assert min(lengths[12:24]) >= reference * .78, (enemy, tier, "small action", lengths)
            assert min(lengths[24:]) >= reference * .82, (enemy, tier, "small reaction", lengths)
    fallback = ASSETS / f"enemies/{enemy}.png"
    with Image.open(fallback).convert("RGBA") as idle:
        assert idle.size == (512, 512), (enemy, idle.size)
        assert idle.getchannel("A").getbbox(), (enemy, "empty fallback")
    with Image.open(tiers["base"][0]).convert("RGBA") as base:
        clustered = base.resize((672, 576), Image.Resampling.NEAREST).resize(base.size, Image.Resampling.NEAREST)
        assert clustered.tobytes() == base.tobytes(), (enemy, "base lacks controlled 2px clusters")

assert '"enemies/" + EnemyArchetype.of(type).asset + ".png"' in GAME
assert "height * enemy.animator.cellAspectRatio()" in GAME

print(f"Enemy visual quality contract: PASS ({len(STRICT)} strict enemies, 3 tiers each)")
