#!/usr/bin/env python3
"""Validate scale-locked redraws without mutating unrelated fighters."""

import hashlib
from collections import deque
from pathlib import Path
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "android/app/src/main/assets"
GAME_VIEW = (ROOT / "android/app/src/main/java/com/familyforce/neonstreets/GameView.java").read_text()

UNTOUCHED = {
    "runtime/enemies/brute_anim.png": "dac46363fec96d38e623d7401c2ed5b2b9edc7da1fded53e836e36dde0d9d79f",
    "runtime/enemies/boss_anim.png": "f541d825c75661637d369f089d5d67a1784308ca45e4d0de9b8a79fc9e64c6b8",
    "runtime/enemies/shield_guard_anim.png": "062d40e86ad199fae6f046f4074a708e159341ace85c027b2de5ede90b8cc2d1",
}


def enclosed_transparent_pixels(cell: Image.Image) -> int:
    """Count alpha holes that cannot reach the cell edge."""
    alpha = cell.getchannel("A")
    pixels = alpha.load()
    outside = set()
    queue = deque()
    for x in range(cell.width):
        queue.extend(((x, 0), (x, cell.height - 1)))
    for y in range(cell.height):
        queue.extend(((0, y), (cell.width - 1, y)))
    while queue:
        x, y = queue.popleft()
        if (x, y) in outside or pixels[x, y]:
            continue
        outside.add((x, y))
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < cell.width and 0 <= ny < cell.height:
                queue.append((nx, ny))
    return sum(
        1 for y in range(cell.height) for x in range(cell.width)
        if not pixels[x, y] and (x, y) not in outside
    )

for relative, expected in UNTOUCHED.items():
    actual = hashlib.sha256((ASSETS / relative).read_bytes()).hexdigest()
    assert actual == expected, (relative, "unexpected redraw", actual)

# Adam's green body must never be removed by the green-screen key. The old
# global chroma predicate created hundreds of transparent pixels inside every
# chest/arm/leg. Tiny enclosed facial/outline gaps remain legitimate.
adam = Image.open(ASSETS / "heroes/adam_anim.png").convert("RGBA")
for row in (0, 2, 3, 4, 5, 8, 9):
    holes = []
    for column in range(8):
        cell = adam.crop((column * 192, row * 192,
                          (column + 1) * 192, (row + 1) * 192))
        holes.append(enclosed_transparent_pixels(cell))
    assert max(holes) < 100, ("Adam", row, "transparent body holes", holes)

for relative, dimensions, columns, rows in (
    ("heroes/parent_anim.png", (1536, 2112), 8, 11),
    ("runtime/heroes/parent_anim.png", (2272, 3124), 8, 11),
    ("uhd/heroes/parent_anim.png", (3072, 4224), 8, 11),
    ("heroes/adam_anim.png", (1536, 2112), 8, 11),
    ("runtime/heroes/adam_anim.png", (1536, 2112), 8, 11),
    ("uhd/heroes/adam_anim.png", (3072, 4224), 8, 11),
    ("heroes/shaikha_anim.png", (1536, 2112), 8, 11),
    ("runtime/heroes/shaikha_anim.png", (1536, 2112), 8, 11),
    ("uhd/heroes/shaikha_anim.png", (3072, 4224), 8, 11),
    ("heroes/sulaiman_anim.png", (1536, 2112), 8, 11),
    ("runtime/heroes/sulaiman_anim.png", (1584, 2178), 8, 11),
    ("uhd/heroes/sulaiman_anim.png", (3072, 4224), 8, 11),
    ("enemies/striker_anim.png", (960, 1152), 6, 6),
    ("runtime/enemies/striker_anim.png", (1308, 1566), 6, 6),
    ("uhd/enemies/striker_anim.png", (1920, 2304), 6, 6),
):
    image = Image.open(ASSETS / relative).convert("RGBA")
    assert image.size == dimensions, (relative, image.size)
    cell_width, cell_height = image.width // columns, image.height // rows
    for row in range(rows):
        hashes = set()
        for column in range(columns):
            cell = image.crop((column * cell_width, row * cell_height,
                               (column + 1) * cell_width, (row + 1) * cell_height))
            bbox = cell.getchannel("A").getbbox()
            assert bbox is not None, (relative, row, column, "empty")
            # Existing engine cells intentionally keep feet 1–2 px above the
            # cell bottom because the whole cell is anchored to the ground.
            # Side/top gutters protect animation; bottom padding protects feet.
            assert min(bbox[0], bbox[1], cell_width - bbox[2]) >= 5, \
                (relative, row, column, "unsafe side/top margin", bbox)
            assert cell_height - bbox[3] >= 1, \
                (relative, row, column, "clipped foot", bbox)
            hashes.add(hashlib.sha256(cell.tobytes()).digest())
        assert len(hashes) >= 3, (relative, row, "insufficient visible animation")

assert "private boolean useUhdCharacterAssets()" in GAME_VIEW
assert "manager.getMemoryClass() >= 384" in GAME_VIEW
assert 'loadBitmap("uhd/heroes/" + stem)' in GAME_VIEW
assert "enemyAnimationTierForZone" in GAME_VIEW
assert "requestedTier" in GAME_VIEW

for relative, cell_width, cell_height, maximum_height_delta in (
    ("heroes/parent_anim.png", 192, 192, 2),
    ("runtime/heroes/parent_anim.png", 284, 284, 3),
    ("uhd/heroes/parent_anim.png", 384, 384, 5),
    ("heroes/adam_anim.png", 192, 192, 2),
    ("runtime/heroes/adam_anim.png", 192, 192, 2),
    ("uhd/heroes/adam_anim.png", 384, 384, 5),
    ("heroes/shaikha_anim.png", 192, 192, 2),
    ("runtime/heroes/shaikha_anim.png", 192, 192, 2),
    ("uhd/heroes/shaikha_anim.png", 384, 384, 5),
    ("heroes/sulaiman_anim.png", 192, 192, 2),
    ("runtime/heroes/sulaiman_anim.png", 198, 198, 3),
    ("uhd/heroes/sulaiman_anim.png", 384, 384, 5),
):
    atlas = Image.open(ASSETS / relative).convert("RGBA")
    walk_boxes = []
    for column in range(8):
        cell = atlas.crop((column * cell_width, cell_height,
                           (column + 1) * cell_width, cell_height * 2))
        walk_boxes.append(cell.getchannel("A").getbbox())
    heights = [box[3] - box[1] for box in walk_boxes]
    bottoms = [box[3] for box in walk_boxes]
    assert max(heights) - min(heights) <= maximum_height_delta, \
        (relative, "walk scale pumping", heights)
    assert len(set(bottoms)) == 1, (relative, "walk ground-line drift", bottoms)

    row_medians = []
    atlas = Image.open(ASSETS / relative).convert("RGBA")
    for row in range(10):  # all upright/reaction rows; knockdown is horizontal
        heights = []
        for column in range(8):
            cell = atlas.crop((column * cell_width, row * cell_height,
                               (column + 1) * cell_width, (row + 1) * cell_height))
            box = cell.getchannel("A").getbbox()
            heights.append(box[3] - box[1])
        assert max(heights) - min(heights) <= maximum_height_delta, \
            (relative, row, "intra-action scale pumping", heights)
        row_medians.append(sorted(heights)[len(heights) // 2])
    assert max(row_medians) - min(row_medians) <= maximum_height_delta, \
        (relative, "cross-action camera zoom", row_medians)

    down_lengths = []
    for column in range(8):
        cell = atlas.crop((column * cell_width, 10 * cell_height,
                           (column + 1) * cell_width, 11 * cell_height))
        box = cell.getchannel("A").getbbox()
        down_lengths.append(max(box[2] - box[0], box[3] - box[1]))
    assert max(down_lengths) - min(down_lengths) <= maximum_height_delta, \
        (relative, "knockdown body-length pumping", down_lengths)

print("Redraw contract: PASS (four scale-locked heroes, Striker, adaptive UHD)")
