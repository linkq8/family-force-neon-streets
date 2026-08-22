#!/usr/bin/env python3
"""Static release gates for continuous panoramas and reactive portraits."""

from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "android/app/src/main/assets"
JAVA = (ROOT / "android/app/src/main/java/com/familyforce/neonstreets/GameView.java").read_text()

for stage in ("market", "transit", "harbor", "palace"):
    with Image.open(ASSETS / f"backgrounds/panoramas/stage_{stage}.png") as image:
        assert image.size == (2172, 724) and image.mode == "RGB"
    with Image.open(ASSETS / f"tv/backgrounds/panoramas/stage_{stage}.png") as image:
        assert image.size == (1800, 600) and image.mode == "RGB"

for hero in ("parent", "adam", "shaikha", "sulaiman"):
    neutral = Image.open(ASSETS / f"heroes/{hero}_portrait.png").convert("RGBA")
    ready = Image.open(ASSETS / f"heroes/{hero}_portrait_ready.png").convert("RGBA")
    assert neutral.size == ready.size == (256, 256)
    assert ImageChops.difference(neutral.convert("RGB"), ready.convert("RGB")).getbbox(), \
        f"static portrait pair: {hero}"

assert 'backgrounds/panoramas/stage_market.png' in JAVA
assert 'int cropWidth = Math.min(scene.getWidth()' in JAVA
assert 'drawSelectionPortrait(canvas, hero, selected' in JAVA
assert 'heroReadyPortraits' in JAVA
assert 'Shader.TileMode.REPEAT' not in JAVA[JAVA.index('private void drawBackdrop'):JAVA.index('private float stagePanProgress')]
print("Visual refresh contract passed: continuous panoramas, reactive portraits, no tiling")
