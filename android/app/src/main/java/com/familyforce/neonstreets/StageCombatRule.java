package com.familyforce.neonstreets;

/** Immutable stage identity/tuning table; no allocations occur in the game loop. */
final class StageCombatRule {
    static final StageCombatRule[] ALL = {
            new StageCombatRule("STREET RUSH", "KEEP THE COMBO MOVING",
                    100, 95, 1, 8, 12, 1000, 1, EnemyArchetype.STRIKER),
            new StageCombatRule("BREAK THE LINE", "FLANK SHIELDS • USE HEAVY HITS",
                    108, 102, 2, 7, 18, 1500, 3, EnemyArchetype.SHIELD_GUARD),
            new StageCombatRule("HARBOR HOLD", "CONTROL THE LANE • SAVE YOUR LINK",
                    112, 106, 2, 10, 20, 2200, 6, EnemyArchetype.BRUTE),
            new StageCombatRule("BOSS GAUNTLET", "BREAK THE GUARD • DEFEAT THE KING",
                    120, 112, 2, 12, 25, 3500, 8, EnemyArchetype.BOSS),
    };

    final String objective;
    final String hint;
    final int hpPercent;
    final int damagePercent;
    final int maxAttackers;
    final int clearHeal;
    final int clearLink;
    final int clearBonus;
    final int eliteZone;
    final int eliteType;

    private StageCombatRule(String objective, String hint, int hpPercent, int damagePercent,
                            int maxAttackers, int clearHeal, int clearLink, int clearBonus,
                            int eliteZone, int eliteType) {
        this.objective = objective;
        this.hint = hint;
        this.hpPercent = hpPercent;
        this.damagePercent = damagePercent;
        this.maxAttackers = maxAttackers;
        this.clearHeal = clearHeal;
        this.clearLink = clearLink;
        this.clearBonus = clearBonus;
        this.eliteZone = eliteZone;
        this.eliteType = eliteType;
    }

    static StageCombatRule forStage(int stage) {
        return ALL[Math.max(0, Math.min(ALL.length - 1, stage))];
    }

    boolean isElite(int zone, int type) {
        return zone == eliteZone && type == eliteType;
    }
}
