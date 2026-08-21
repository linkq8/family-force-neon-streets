#!/usr/bin/env python3
"""Regression guard for versioned, corruption-safe encounter checkpoints."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "app/src/main/java/com/familyforce/neonstreets/GameView.java"


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    assert "CHECKPOINT_VERSION = 2" in text
    assert "private boolean validateCheckpoint()" in text
    assert "private void saveCheckpoint(int safeZone)" in text
    assert "private boolean restoreCheckpoint()" in text
    assert '.putInt("checkpoint_hash", hash)' in text
    assert '.putInt("checkpoint_team_hash", teamHash)' in text
    for key in ("checkpoint_companion1", "checkpoint_companion2", "checkpoint_difficulty",
                "checkpoint_p2_health", "checkpoint_p2_energy", "checkpoint_p2_link"):
        assert key in text
    assert '.putBoolean("checkpoint_valid", true)' in text
    assert "if (!valid) prefs.edit().remove(\"checkpoint_valid\").apply();" in text
    assert "if (enemy.alive && enemy.zone < zone)" in text
    encounter = text[text.index("private void updateEncounter()"):
                     text.index("private void dropZoneRewards")]
    assert "saveCheckpoint(zone);" in encounter
    assert encounter.index("saveCheckpoint(zone);") < encounter.index("stageTransitionTimer =")
    assert "if (state == PLAY && !zoneActive) saveCheckpoint(zone);" in text
    assert '"CONTINUE"' in text
    print("Checkpoint/continue contract: PASS")


if __name__ == "__main__":
    main()
