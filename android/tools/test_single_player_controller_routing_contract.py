#!/usr/bin/env python3
"""Keep Android TV remotes from stealing the single-player gamepad slot."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "app/src/main/java/com/familyforce/neonstreets/GameView.java"


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    assert "if (state == PLAY && !twoPlayerMode)" in text
    assert "primaryControllerId = deviceId;" in text
    assert "secondaryControllerId = -1;" in text
    assert text.count(
        "boolean p2ByDevice = twoPlayerMode && hasCompanionController() && controllerSlot == 1;"
    ) == 2
    assert "? (twoPlayerMode && controllerSlot == 1 && isDedicatedCompanion())" in text
    print("Single-player TV remote/DualSense routing contract: PASS")


if __name__ == "__main__":
    main()
