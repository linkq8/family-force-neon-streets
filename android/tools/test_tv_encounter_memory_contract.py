#!/usr/bin/env python3
"""Guard first encounter against Android TV decode/upload stalls and memory bursts."""

from pathlib import Path
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "app/src/main/java/com/familyforce/neonstreets/GameView.java"
ASSETS = ROOT / "app/src/main/assets"


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    assert "enemyAnimationTierForZone" in text
    assert 'enemyAtlasAssetExists("runtime/enemies/", type)' in text
    assert "private boolean useReducedMemoryAssets()" in text
    assert "smallestScreenWidthDp >= 720" in text
    assert 'loadBitmap("runtime/heroes/" + stem)' in text
    assert "preloadEnemyAnimationsForZoneAsync" in text
    assert '"FamilyForceAssetWarmup"' in text
    assert "loader.setPriority(Thread.MIN_PRIORITY)" in text
    assert "Bitmap decoded = decodeEnemyAnimationType(type, requestedTier);" in text
    assert "loadedOneAtlasThisTick" not in text
    assert "atlas.getWidth() / ENEMY_ANIM_COLUMNS" in text
    assert "atlas.getHeight() / ENEMY_ANIM_ROWS" in text
    assert "prepareEnemyAnimationsForZone(zone);" in text
    assert "void trimMemory(int level)" in text

    enemy_names = (
        "grunt", "skater", "brute", "boss", "striker", "shield_guard",
        "lantern_courier", "market_enforcer", "keeper_7", "rail_runner",
        "signal_warden", "railmaster_9", "cargo_loader", "harpoon_drone",
        "dock_crusher", "tidebreaker", "scrap_stalker", "core_jammer",
        "furnace_brawler", "palace_sentinel", "vox_avatar", "shadow_prime",
    )
    for name in enemy_names:
        path = ASSETS / f"tv/enemies/{name}_anim.png"
        assert path.is_file(), path
        with Image.open(path) as image:
            strict = name in {
                "grunt", "skater", "lantern_courier", "market_enforcer", "keeper_7"
            }
            expected = (1176, 1008) if strict else (840, 1008)
            assert image.size == expected, (path, image.size)
            assert image.mode == "RGBA", (path, image.mode)
    for name in ("parent", "adam", "shaikha", "sulaiman"):
        path = ASSETS / f"tv/heroes/{name}_anim.png"
        assert path.is_file(), path
        with Image.open(path) as image:
            assert image.size == (1152, 1584), (path, image.size)
            assert image.mode == "RGBA", (path, image.mode)
    full_bytes = 4 * 960 * 1152
    tv_bytes = 4 * 1176 * 1008
    assert tv_bytes < full_bytes * 2
    print("TV first-encounter memory contract: PASS "
          "(zone roster warmup, maximum four atlases, strict wide-cell pilot within budget)")


if __name__ == "__main__":
    main()
