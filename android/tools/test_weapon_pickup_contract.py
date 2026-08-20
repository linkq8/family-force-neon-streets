#!/usr/bin/env python3
"""Regression guard for the visible belt-brawler weapon pickup envelope."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "app/src/main/java/com/familyforce/neonstreets/GameView.java"


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    assert "PICKUP_AUTO_X = 42f" in text
    assert "PICKUP_AUTO_Y = 40f" in text
    assert "PICKUP_PROMPT_X = 70f" in text
    assert "PICKUP_PROMPT_Y = 48f" in text
    assert "tryPickupNearbyWeapon(PICKUP_PROMPT_X, PICKUP_PROMPT_Y)" in text
    assert "drawPickupPrompt(canvas);" in text
    assert "WorldObject object = nearestPickupWeapon(maxX, maxY);" in text
    assert "heldWeaponType = object.type;" in text
    assert "object.active = false;" in text
    assert "weaponDurability = Math.max(1, object.durability);" in text
    print("Weapon pickup contract: PASS")


if __name__ == "__main__":
    main()
