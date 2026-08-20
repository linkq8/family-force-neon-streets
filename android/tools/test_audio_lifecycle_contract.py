#!/usr/bin/env python3
"""Guard Android TV audio lifecycle against MediaPlayer state races."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "app/src/main/java/com/familyforce/neonstreets/AudioController.java"


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    for signature in (
        "synchronized void ensureMusic",
        "synchronized void pauseMusic",
        "synchronized void resumeMusic",
        "synchronized void setMusicEnabled",
        "synchronized void setMusicVolume",
        "synchronized void release()",
    ):
        assert signature in text, signature
    assert "catch (IOException | IllegalStateException | SecurityException ignored)" in text
    assert text.count("catch (IllegalStateException ignored)") >= 4
    print("Audio lifecycle race contract: PASS")


if __name__ == "__main__":
    main()
