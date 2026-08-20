#!/usr/bin/env python3
"""Regression guard for fair, visible enemy attack-token allocation."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "app/src/main/java/com/familyforce/neonstreets/GameView.java"


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    assert "countAttackingEnemies() < 2" in text
    assert "countAttackingEnemiesForTarget(targetSlot) < perPlayerAttackLimit" in text
    assert "int perPlayerAttackLimit = difficulty == 2 ? 2 : 1;" in text
    assert "boolean visibleThreat = enemy.x >= cameraX + 18f" in text
    assert "enemy.attackTargetSlot = targetSlot;" in text
    print("Enemy attack-token contract: PASS")


if __name__ == "__main__":
    main()
