#!/usr/bin/env python3
"""Regression guard for centralized player combat move data."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "app/src/main/java/com/familyforce/neonstreets/GameView.java"


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    assert "private static final MoveSpec[] MOVE_SPECS" in text
    for move in ("PUNCH", "KICK", "HEAVY PUNCH", "HEAVY KICK", "SPECIAL",
                 "LINK", "AIR ATTACK", "WEAPON", "THROW"):
        assert f'new MoveSpec("{move}"' in text
    assert "return moveSpec(action).laneHalfHeight;" in text
    assert "return moveSpec(action).fps;" in text
    assert "return moveSpec(action).hitFrame;" in text
    assert "actionRecoveryTicks = moveSpec(completedAction).recoveryTicks;" in text
    assert "hitStop = spec.hitPauseTicks;" in text
    assert "spec.launches" in text
    assert "enemy.animator.frame() == 3" in text
    print("Move specs and combat debug contract: PASS")


if __name__ == "__main__":
    main()
