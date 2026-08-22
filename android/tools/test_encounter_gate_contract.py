#!/usr/bin/env python3
"""Prevent P2/enemies from crossing the active encounter gate and trapping P1."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "app/src/main/java/com/familyforce/neonstreets/GameView.java"


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    assert "ENCOUNTER_GATE_OFFSET = 425f" in text
    assert "ENCOUNTER_GATE_MARGIN = 20f" in text
    assert "playerX = Math.min(playerX, playerLimit);" in text
    assert "if (twoPlayerMode) player2X = Math.min(player2X, playerLimit);" in text
    assert "enemy.x = Math.min(enemy.x, playerLimit - 8f);" in text
    assert 'text(canvas, "ROUTE LOCKED"' in text
    assert 'text(canvas, "CLEAR THE WAVE"' in text
    assert "zoneActive = false;" in text
    print("Encounter gate/P1-P2 progression contract: PASS")


if __name__ == "__main__":
    main()
