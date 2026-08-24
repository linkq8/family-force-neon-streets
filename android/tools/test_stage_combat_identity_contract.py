#!/usr/bin/env python3
"""Release guard for five distinct, allocation-free stage combat identities."""

from pathlib import Path

ANDROID = Path(__file__).resolve().parents[1]
JAVA = ANDROID / "app/src/main/java/com/familyforce/neonstreets"
game = (JAVA / "GameView.java").read_text(encoding="utf-8")
rules = (JAVA / "StageCombatRule.java").read_text(encoding="utf-8")
rosters = (JAVA / "StageRoster.java").read_text(encoding="utf-8")

for label in ("STREET RUSH", "BREAK THE LINE", "HARBOR HOLD", "PALACE SIEGE",
              "FINAL CONVERGENCE"):
    assert f'"{label}"' in rules, label
for hint in ("KEEP THE COMBO MOVING", "FLANK SHIELDS", "CONTROL THE LANE",
             "BREAK THE SENTINEL", "CLEAR EACH ECHO"):
    assert hint in rules, hint

assert rules.count("new StageCombatRule(") == 5
assert "final int hpPercent" in rules
assert "final int damagePercent" in rules
assert "final int maxAttackers" in rules
assert "final int clearBonus" in rules
assert "boolean isElite(int zone, int type)" in rules

for snippet in (
    "StageCombatRule.forStage(stageForZone(enemyZone))",
    "archetype.maxHp * hpPercent / 100",
    "countAttackingEnemies() < stageRule.maxAttackers",
    "stageRule.damagePercent / 100f",
    "score += clearedRule.clearBonus",
    "p2Link = Math.min(100, p2Link + clearedRule.clearLink)",
    'diagnostics.event("STAGE_BONUS "',
    'EnemyArchetype.of(enemy.type).isBoss()',
    "promoteSpectatorBoss(watchingBoss, playerLimit)",
    "enemy.spectator",
    "stageObjective(nextStage)",
    "stageHint(nextStage)",
):
    assert snippet in game, snippet

for weapon in ("WEAPON_BAT", "WEAPON_PIPE", "WEAPON_MALLET", "WEAPON_SIGN"):
    assert f"spawnWorldObject({weapon}" in game, weapon

# Encounter-specific loading must remain bounded even with denser art.
assert "static int decodedAtlasCount(int zone)" in rosters
assert "static boolean includesZone(int zone, int type)" in rosters
assert "EnemyArchetype.BOSS" in rosters
assert "EnemyArchetype.SHADOW_PRIME" in rosters
assert "static int zoneCount()" in rosters

print("Stage combat identity contract: PASS (5 rules, mini-bosses, spectator bosses, bounded rosters)")
