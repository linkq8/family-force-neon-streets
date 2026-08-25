#!/usr/bin/env python3
"""Prevent Android TV from silently degrading animated heroes to still art."""

from pathlib import Path
import hashlib

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app/src/main/assets"
GAME = (ROOT / "app/src/main/java/com/familyforce/neonstreets/GameView.java").read_text()


def method(name: str) -> str:
    start = GAME.index(f" {name}(")
    brace = GAME.index("{", start)
    depth = 0
    for index in range(brace, len(GAME)):
        if GAME[index] == "{": depth += 1
        elif GAME[index] == "}":
            depth -= 1
            if depth == 0: return GAME[brace:index + 1]
    raise AssertionError(name)


atlas_loader = method("loadHeroAnimationAtlas")
clip_loader = method("loadHeroAnimationClips")
tier_selector = method("heroAnimationTier")

# TV is not synonymous with weak hardware. Low-memory sticks retain the compact
# tier, ordinary TVs receive Base, and Shield-class devices can use Runtime.
assert "manager.isLowRamDevice() || memoryMb < 192" in tier_selector
assert "memoryMb >= 384 ? HERO_TIER_RUNTIME : HERO_TIER_BASE" in tier_selector
assert "memoryMb >= 512" in tier_selector and "HERO_TIER_UHD" in tier_selector
assert "HERO_ATLAS_TIER_DIRS[tier]" in atlas_loader
assert "HERO_CLIP_TIER_DIRS[tier]" in clip_loader
assert "tier >= HERO_TIER_TV" in atlas_loader
assert "tier >= HERO_TIER_TV" in clip_loader
assert 'loadBitmap("heroes/" + stem)' in atlas_loader
assert 'loadClipSet("clips/heroes/"' in clip_loader

for actor in ("parent", "adam", "shaikha", "sulaiman"):
    path = ASSETS / "tv/heroes" / f"{actor}_anim.png"
    with Image.open(path).convert("RGBA") as atlas:
        assert atlas.width % 8 == 0 and atlas.height % 11 == 0, path
        cell_width, cell_height = atlas.width // 8, atlas.height // 11
        for row in range(11):
            frames = [atlas.crop((column * cell_width, row * cell_height,
                                  (column + 1) * cell_width, (row + 1) * cell_height))
                      for column in range(8)]
            digests = {hashlib.sha256(frame.tobytes()).digest() for frame in frames}
            assert len(digests) >= 3, (actor, row, "static animation row")

print("TV hero animation loading: PASS (adaptive tiers + 4 heroes × 11 moving rows)")
