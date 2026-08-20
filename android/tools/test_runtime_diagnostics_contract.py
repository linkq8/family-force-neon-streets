#!/usr/bin/env python3
"""Static guardrails for the low-overhead runtime crash flight recorder."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
game = (ROOT / "app/src/main/java/com/familyforce/neonstreets/GameView.java").read_text()
diagnostics = (ROOT / "app/src/main/java/com/familyforce/neonstreets/RuntimeDiagnostics.java").read_text()
activity = (ROOT / "app/src/main/java/com/familyforce/neonstreets/MainActivity.java").read_text()

for token in ("zone", "p1_health", "p2_health", "enemy_count", "weapon", "action",
              "java_used_kb", "native_heap_kb", "session_active"):
    assert token in diagnostics, token
assert "stageFrames % 120" in game
assert 'diagnostics.failure("update"' in game
assert 'diagnostics.failure("render"' in game
assert "BuildConfig.DEBUG && enabled" in game
assert "familyforce.fullStageTest" in activity
assert "STAGE_COMPLETE" in game
assert "previous_interrupted_report" in diagnostics
print("runtime diagnostics contract: PASS")
