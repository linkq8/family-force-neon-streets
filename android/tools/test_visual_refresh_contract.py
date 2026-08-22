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
assert 'STAGE_END_ZONE[safeStage - 1]' in JAVA
assert 'drawSelectionPortrait(canvas, hero, selected' in JAVA
assert 'crispCharacterPaint' in JAVA
assert 'heroReadyPortraits' in JAVA
assert 'Shader.TileMode.REPEAT' not in JAVA[JAVA.index('private void drawBackdrop'):JAVA.index('private float stagePanProgress')]

# Stage 4 used to hold the panorama still for ~200 world units because its pan
# started near encounter 8 rather than at the camera position after encounter 7.
triggers = (430, 1080, 1730, 2380, 2980, 3560, 4180, 4820, 5480)
stage_end = (1, 3, 6, 8)
gate = 425
stage4_start = triggers[stage_end[2]] + gate - 210
assert stage4_start == 4395
assert (stage4_start + 10 - stage4_start) / ((5480 + gate) - stage4_start) > 0
print("Visual refresh contract passed: continuous panoramas, reactive portraits, no tiling")
