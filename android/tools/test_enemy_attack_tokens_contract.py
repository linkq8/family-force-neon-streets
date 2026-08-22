#!/usr/bin/env python3
"""Regression guard for fair, visible enemy attack-token allocation."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "app/src/main/java/com/familyforce/neonstreets/GameView.java"
RULES = Path(__file__).resolve().parents[1] / "app/src/main/java/com/familyforce/neonstreets/StageCombatRule.java"


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    rules = RULES.read_text(encoding="utf-8")
    assert "countAttackingEnemies() < stageRule.maxAttackers" in text
    # Stage identity may vary pressure, but never exceed two simultaneous attacks.
    assert "100, 95, 1," in rules
    assert rules.count(", 2,") >= 3
    assert "countAttackingEnemiesForTarget(targetSlot) < perPlayerAttackLimit" in text
    assert "int perPlayerAttackLimit = difficulty == 2 ? 2 : 1;" in text
    assert "boolean visibleThreat = enemy.x >= cameraX + 18f" in text
    assert "enemy.attackTargetSlot = targetSlot;" in text
    print("Enemy attack-token contract: PASS")


if __name__ == "__main__":
    main()
