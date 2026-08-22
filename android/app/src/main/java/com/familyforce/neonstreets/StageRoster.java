package com.familyforce.neonstreets;

/** Enemy atlas packs retained per encounter; keeps high-detail TV art bounded. */
final class StageRoster {
    private static final int[][] TYPES = {
            {EnemyArchetype.GRUNT, EnemyArchetype.SKATER, EnemyArchetype.STRIKER},
            {EnemyArchetype.GRUNT, EnemyArchetype.SKATER, EnemyArchetype.STRIKER},
            {EnemyArchetype.GRUNT, EnemyArchetype.SHIELD_GUARD},
            {EnemyArchetype.SHIELD_GUARD, EnemyArchetype.BRUTE, EnemyArchetype.STRIKER},
            {EnemyArchetype.BOSS, EnemyArchetype.SHIELD_GUARD, EnemyArchetype.BRUTE},
            {EnemyArchetype.SHIELD_GUARD, EnemyArchetype.SKATER, EnemyArchetype.BOSS},
            {EnemyArchetype.SKATER, EnemyArchetype.SHIELD_GUARD, EnemyArchetype.BRUTE},
            {EnemyArchetype.GRUNT, EnemyArchetype.BRUTE, EnemyArchetype.SHIELD_GUARD},
            {EnemyArchetype.GRUNT, EnemyArchetype.BRUTE, EnemyArchetype.BOSS,
                    EnemyArchetype.STRIKER},
    };

    private StageRoster() {}

    static boolean includesZone(int zone, int type) {
        int safeZone = Math.max(0, Math.min(TYPES.length - 1, zone));
        for (int candidate : TYPES[safeZone]) if (candidate == type) return true;
        return false;
    }

    static int decodedAtlasCount(int zone) {
        return TYPES[Math.max(0, Math.min(TYPES.length - 1, zone))].length;
    }
}
