#!/usr/bin/env python3
"""Static guard for the final-stage wave -> spectator boss state machine."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "app/src/main/java/com/familyforce/neonstreets"
game = (JAVA / "GameView.java").read_text(encoding="utf-8")
roster = (JAVA / "StageRoster.java").read_text(encoding="utf-8")
archetypes = (JAVA / "EnemyArchetype.java").read_text(encoding="utf-8")

assert "private static final int[] STAGE_START_ZONE = {0, 2, 4, 7, 9}" in game
assert "private static final int[] STAGE_END_ZONE = {1, 3, 6, 8, 13}" in game
assert "430f, 1080f, 1730f, 2380f, 2980f, 3560f, 4180f, 4820f, 5480f" in game
assert game.count("spawnSpectator(") >= 8  # definition + 4 main bosses + 4 echoes + final
assert game.count("enemy.spectator") >= 8
assert "promoteSpectatorBoss(watchingBoss, playerLimit)" in game
assert "boss.spectator = false" in game
assert "EnemyArchetype.SHADOW_PRIME" in game and "EnemyArchetype.SHADOW_PRIME" in roster
assert 'type("shadow_prime", "SHADOW PRIME", 760' in archetypes
assert "rank == RANK_FINAL_BOSS" in archetypes
assert "if (zone < 0 || zone >= TYPES.length) return false" in roster
assert "zone < 0 || zone >= TYPES.length ? 0" in roster

# Every encounter row remains within the four-atlas Android TV decode budget.
inside = roster.split("private static final int[][] TYPES = {", 1)[1].split("};", 1)[0]
rows = [line for line in inside.splitlines() if line.strip().startswith("{")]
assert len(rows) == 14, len(rows)
for number, row in enumerate(rows):
    assert row.count("EnemyArchetype.") <= 4, (number, row)

print("Final gauntlet contract: PASS (4 echo waves, protected spectators, strongest final boss)")
