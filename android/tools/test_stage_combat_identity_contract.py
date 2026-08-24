#!/usr/bin/env python3
"""Release guard for four distinct, allocation-free stage combat identities."""

from pathlib import Path

ANDROID = Path(__file__).resolve().parents[1]
JAVA = ANDROID / "app/src/main/java/com/familyforce/neonstreets"
game = (JAVA / "GameView.java").read_text(encoding="utf-8")
rules = (JAVA / "StageCombatRule.java").read_text(encoding="utf-8")
rosters = (JAVA / "StageRoster.java").read_text(encoding="utf-8")

for label in ("STREET RUSH", "BREAK THE LINE", "HARBOR HOLD", "BOSS GAUNTLET"):
    assert f'"{label}"' in rules, label
for hint in ("KEEP THE COMBO MOVING", "FLANK SHIELDS", "CONTROL THE LANE",
             "BREAK THE GUARD"):
    assert hint in rules, hint

assert rules.count("new StageCombatRule(") == 4
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
    'enemy.type == EnemyArchetype.BOSS ? ui("stage_boss", "STAGE BOSS") : ui("mini_boss", "MINI-BOSS")',
    "stageObjective(nextStage)",
    "stageHint(nextStage)",
):
    assert snippet in game, snippet

for weapon in ("WEAPON_BAT", "WEAPON_PIPE", "WEAPON_MALLET", "WEAPON_SIGN"):
    assert f"spawnWorldObject({weapon}" in game, weapon

# Encounter-specific loading must remain bounded even with denser art.
assert "static int decodedAtlasCount(int zone)" in rosters
assert "static boolean includesZone(int zone, int type)" in rosters
assert "EnemyArchetype.BOSS," in rosters
assert "EnemyArchetype.STRIKER}" in rosters

print("Stage combat identity contract: PASS (4 rules, elites, rewards, bounded rosters)")
