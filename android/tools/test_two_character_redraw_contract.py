#!/usr/bin/env python3
"""Ensure the two-character redraw does not mutate any other fighter atlas."""

import hashlib
from pathlib import Path
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "android/app/src/main/assets"

UNTOUCHED = {
    "runtime/heroes/adam_anim.png": "6dbe7cb5e7186f6dca77f5a8d7d4da6d7491c7df2563f46d081c7016ecdb5aeb",
    "runtime/heroes/shaikha_anim.png": "434a995cff6735f36410c815cdc720e040c9d139375fd31b490f99e0ac89f1ff",
    "runtime/heroes/sulaiman_anim.png": "ab5e1c3e5137ff593ce16f962b5d68d68fc6bc93a615d07402d8864a5aa57ed1",
    "runtime/enemies/grunt_anim.png": "05e6b13b4c94c106a54fb15b8b9bbd0e016f754a7ef892992b36bfeab4a3126d",
    "runtime/enemies/skater_anim.png": "ed0aa76495750858b57fc5531c41760bba540c25f543aa01e827b4a2161e3d00",
    "runtime/enemies/brute_anim.png": "dac46363fec96d38e623d7401c2ed5b2b9edc7da1fded53e836e36dde0d9d79f",
    "runtime/enemies/boss_anim.png": "f541d825c75661637d369f089d5d67a1784308ca45e4d0de9b8a79fc9e64c6b8",
    "runtime/enemies/shield_guard_anim.png": "062d40e86ad199fae6f046f4074a708e159341ace85c027b2de5ede90b8cc2d1",
}

for relative, expected in UNTOUCHED.items():
    actual = hashlib.sha256((ASSETS / relative).read_bytes()).hexdigest()
    assert actual == expected, (relative, "unexpected redraw", actual)

for relative, dimensions, columns, rows in (
    ("heroes/parent_anim.png", (1536, 2112), 8, 11),
    ("runtime/heroes/parent_anim.png", (2272, 3124), 8, 11),
    ("enemies/striker_anim.png", (960, 1152), 6, 6),
    ("runtime/enemies/striker_anim.png", (1308, 1566), 6, 6),
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

print("Two-character redraw contract: PASS (Essa + Striker only)")
