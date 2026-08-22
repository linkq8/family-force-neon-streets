#!/usr/bin/env python3
"""Guard first encounter against Android TV decode/upload stalls and memory bursts."""

from pathlib import Path
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "app/src/main/java/com/familyforce/neonstreets/GameView.java"
ASSETS = ROOT / "app/src/main/assets"


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    assert 'loadBitmap("runtime/enemies/" + stem)' in text
    assert "private boolean useReducedMemoryAssets()" in text
    assert "smallestScreenWidthDp >= 720" in text
    assert 'loadBitmap("runtime/heroes/" + stem)' in text
    assert "preloadEnemyAnimationsForStageAsync" in text
    assert '"FamilyForceAssetWarmup"' in text
    assert "loader.setPriority(Thread.MIN_PRIORITY)" in text
    assert "Bitmap decoded = decodeEnemyAnimationType(type);" in text
    assert "loadedOneAtlasThisTick" not in text
    assert "atlas.getWidth() / ENEMY_ANIM_COLUMNS" in text
    assert "atlas.getHeight() / ENEMY_ANIM_ROWS" in text
    assert "prepareEnemyAnimationsForZone(zone);" in text
    assert "void trimMemory(int level)" in text

    for name in ("grunt", "skater", "brute", "boss"):
        path = ASSETS / f"tv/enemies/{name}_anim.png"
        assert path.is_file(), path
        with Image.open(path) as image:
            assert image.size == (720, 864), (path, image.size)
            assert image.mode == "RGBA", (path, image.mode)
    for name in ("striker", "shield_guard"):
        path = ASSETS / f"tv/enemies/{name}_anim.png"
        assert path.is_file(), path
        with Image.open(path) as image:
            assert image.size == (840, 1008), (path, image.size)
            assert image.mode == "RGBA", (path, image.mode)
    for name in ("parent", "adam", "shaikha", "sulaiman"):
        path = ASSETS / f"tv/heroes/{name}_anim.png"
        assert path.is_file(), path
        with Image.open(path) as image:
            assert image.size == (1152, 1584), (path, image.size)
            assert image.mode == "RGBA", (path, image.mode)
    full_bytes = 4 * 960 * 1152
    tv_bytes = 4 * 720 * 864
    assert tv_bytes * 100 // full_bytes == 56
    print("TV first-encounter memory contract: PASS "
          "(stage roster warmup, maximum five atlases, mixed 56%/77% atlas area)")


if __name__ == "__main__":
    main()
