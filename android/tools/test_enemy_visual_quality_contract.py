#!/usr/bin/env python3
"""Release-blocking visual parity contract for the approved Stage 1 pilot."""

from pathlib import Path
import statistics

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app/src/main/assets"
JAVA = (ROOT / "app/src/main/java/com/familyforce/neonstreets/EnemyArchetype.java").read_text()
SOURCE = ROOT.parent / "assets/imagegen/android/enemies/quality-v1"
STRICT = (
    "grunt", "skater", "lantern_courier", "market_enforcer", "keeper_7",
)


def cells(image: Image.Image):
    width, height = image.width // 6, image.height // 6
    for row in range(6):
        for column in range(6):
            yield image.crop((column * width, row * height,
                              (column + 1) * width, (row + 1) * height))


for enemy in STRICT:
    assert f'type("{enemy}"' in JAVA, enemy
    for sheet in ("idle_walk.png", "attacks.png", "hurt_knockdown.png"):
        path = SOURCE / enemy / sheet
        assert path.is_file(), f"missing high-resolution source: {path}"
        with Image.open(path) as image:
            assert image.width / 6 >= 240 and image.height / 2 >= 240, (
                path, image.size, "source cell below 240x240"
            )
    tiers = {
        "base": (ASSETS / f"enemies/{enemy}_anim.png", (960, 1152), 8),
        "runtime": (ASSETS / f"runtime/enemies/{enemy}_anim.png", (1440, 1728), 12),
        "tv": (ASSETS / f"tv/enemies/{enemy}_anim.png", (840, 1008), 7),
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
            assert max(ratios) - min(ratios) <= .13, (enemy, tier, "scale drift", ratios)
    with Image.open(tiers["base"][0]).convert("RGBA") as base:
        clustered = base.resize((480, 576), Image.Resampling.NEAREST).resize(base.size, Image.Resampling.NEAREST)
        assert clustered.tobytes() == base.tobytes(), (enemy, "base lacks controlled 2px clusters")

print(f"Enemy visual quality contract: PASS ({len(STRICT)} strict enemies, 3 tiers each)")
