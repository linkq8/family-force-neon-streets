#!/usr/bin/env python3
"""Release gate for consistent visible pixel density on every asset tier."""

from pathlib import Path
import re
import statistics

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app/src/main/assets"
JAVA = (ROOT / "app/src/main/java/com/familyforce/neonstreets/EnemyArchetype.java").read_text()
ACTORS = ("striker", "shield_guard", "market_enforcer", "keeper_7")
TIERS = {
    "base": ("enemies", 1.13, 1.24, 8),
    "runtime": ("runtime/enemies", 1.54, 1.95, 12),
    "tv": ("tv/enemies", 1.03, 1.12, 7),
}


def render_height(actor: str) -> float:
    match = re.search(
        rf'type\("{re.escape(actor)}",\s*"[^"]+",\s*\d+,\s*[\d.]+f,'
        rf'\s*\d+,\s*\d+,\s*\d+,\s*\d+,\s*(\d+(?:\.\d+)?)f,',
        JAVA,
    )
    assert match, f"missing render height: {actor}"
    return float(match.group(1))


def frames(atlas: Image.Image):
    cell_width, cell_height = atlas.width // 6, atlas.height // 6
    for row in range(6):
        for column in range(6):
            yield atlas.crop((column * cell_width, row * cell_height,
                              (column + 1) * cell_width, (row + 1) * cell_height))


density_records = {}
for actor in ACTORS:
    height = render_height(actor)
    for tier, (folder, lower, upper, gutter) in TIERS.items():
        path = ASSETS / folder / f"{actor}_anim.png"
        with Image.open(path).convert("RGBA") as atlas:
            assert atlas.width % 6 == 0 and atlas.height % 6 == 0, path
            cells = list(frames(atlas))
            boxes = [cell.getchannel("A").getbbox() for cell in cells]
            assert all(boxes), (actor, tier, "empty frame")
            cell_width, cell_height = cells[0].size
            for box in boxes:
                assert min(box[0], box[1], cell_width - box[2], cell_height - box[3]) >= gutter, (
                    actor, tier, "unsafe gutter", box
                )
            standing_heights = [box[3] - box[1] for box in boxes[:12]]
            density = statistics.median(standing_heights) / height
            density_records[(actor, tier)] = density
            assert lower <= density <= upper, (
                actor, tier, f"APGU {density:.3f} outside {lower:.2f}–{upper:.2f}"
            )
            if tier == "base":
                half = atlas.resize((atlas.width // 2, atlas.height // 2), Image.Resampling.NEAREST)
                clustered = half.resize(atlas.size, Image.Resampling.NEAREST)
                assert clustered.tobytes() != atlas.tobytes(), (
                    actor, "base is manufactured from coarse exact 2x2 clusters"
                )

for actor, reference in (("market_enforcer", "shield_guard"), ("keeper_7", "striker")):
    for tier in TIERS:
        ratio = density_records[(actor, tier)] / density_records[(reference, tier)]
        assert .96 <= ratio <= 1.04, (actor, tier, reference, f"density ratio {ratio:.3f}")

print(f"Enemy pixel density contract: PASS ({len(ACTORS)} actors × {len(TIERS)} tiers)")
