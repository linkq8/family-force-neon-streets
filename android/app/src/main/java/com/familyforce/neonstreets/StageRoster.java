package com.familyforce.neonstreets;

/** Enemy atlas packs retained per stage; keeps low-memory Android TV bounded. */
final class StageRoster {
    private static final int[][] TYPES = {
            {EnemyArchetype.GRUNT, EnemyArchetype.SKATER, EnemyArchetype.STRIKER},
            {EnemyArchetype.GRUNT, EnemyArchetype.BRUTE, EnemyArchetype.STRIKER,
                    EnemyArchetype.SHIELD_GUARD},
            {EnemyArchetype.SKATER, EnemyArchetype.BRUTE, EnemyArchetype.BOSS,
                    EnemyArchetype.SHIELD_GUARD},
            {EnemyArchetype.GRUNT, EnemyArchetype.BRUTE, EnemyArchetype.BOSS,
                    EnemyArchetype.STRIKER, EnemyArchetype.SHIELD_GUARD},
    };

    private StageRoster() {}

    static boolean includes(int stage, int type) {
        int safeStage = Math.max(0, Math.min(TYPES.length - 1, stage));
        for (int candidate : TYPES[safeStage]) if (candidate == type) return true;
        return false;
    }

    static int decodedAtlasCount(int stage) {
        return TYPES[Math.max(0, Math.min(TYPES.length - 1, stage))].length;
    }
}
