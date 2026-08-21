#!/usr/bin/env python3
"""Guard the no-I/O-on-Link runtime contract for low-power Android TV."""

from pathlib import Path
import re


SOURCE = Path(__file__).resolve().parents[1] / "app/src/main/java/com/familyforce/neonstreets/GameView.java"
text = SOURCE.read_text(encoding="utf-8")


def method_body(name: str) -> str:
    match = re.search(rf"\b{name}\s*\([^)]*\)\s*\{{", text)
    if not match:
        raise AssertionError(f"missing method: {name}")
    start = match.end()
    depth = 1
    pos = start
    while pos < len(text) and depth:
        if text[pos] == "{":
            depth += 1
        elif text[pos] == "}":
            depth -= 1
        pos += 1
    if depth:
        raise AssertionError(f"unterminated method: {name}")
    return text[start:pos - 1]


start_assist = method_body("startAssist")
assert "loadAssistAnimationRow" not in start_assist, "Link must never decode an atlas at summon time"
assert "bindPreloadedAssistAnimation" in start_assist, "Link must bind a preloaded row"

preload = method_body("preloadAssistAnimationRows")
assert "loadAssistAnimationRow(0" in preload, "P1 companion must preload"
assert "loadAssistAnimationRow(1" in preload, "P2 companion must preload when enabled"

selection = method_body("tryConfirmSelectionToStart")
assert selection.index("preloadAssistAnimationRows") < selection.index("enterState(INTRO)"), (
    "companion rows must be ready before the intro/play transition"
)

reset = method_body("resetGame")
assert "preloadAssistAnimationRows" in reset, "checkpoint/retry must restore the preload contract"

update_assist = method_body("updateAssist")
assert "recycle" not in update_assist and "loadAssistAnimationRow" not in update_assist, (
    "active Link animation must not allocate, decode, or recycle"
)

print("Link preload/no-runtime-I/O contract: PASS")
