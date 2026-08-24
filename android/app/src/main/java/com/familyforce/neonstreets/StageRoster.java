package com.familyforce.neonstreets;

/** Enemy atlas packs retained per encounter; every row stays at four atlases or fewer. */
final class StageRoster {
    private static final int[][] TYPES = {
            {EnemyArchetype.GRUNT, EnemyArchetype.SKATER, EnemyArchetype.LANTERN_COURIER},
            {EnemyArchetype.GRUNT, EnemyArchetype.MARKET_ENFORCER, EnemyArchetype.KEEPER_7},
            {EnemyArchetype.STRIKER, EnemyArchetype.SHIELD_GUARD, EnemyArchetype.RAIL_RUNNER},
            {EnemyArchetype.STRIKER, EnemyArchetype.SIGNAL_WARDEN, EnemyArchetype.RAILMASTER_9},
            {EnemyArchetype.BRUTE, EnemyArchetype.CARGO_LOADER, EnemyArchetype.HARPOON_DRONE},
            {EnemyArchetype.CARGO_LOADER, EnemyArchetype.HARPOON_DRONE},
            {EnemyArchetype.BRUTE, EnemyArchetype.DOCK_CRUSHER, EnemyArchetype.TIDEBREAKER},
            {EnemyArchetype.SCRAP_STALKER, EnemyArchetype.CORE_JAMMER, EnemyArchetype.FURNACE_BRAWLER},
            {EnemyArchetype.FURNACE_BRAWLER, EnemyArchetype.PALACE_SENTINEL, EnemyArchetype.BOSS},
            {EnemyArchetype.GRUNT, EnemyArchetype.SKATER, EnemyArchetype.LANTERN_COURIER, EnemyArchetype.KEEPER_7},
            {EnemyArchetype.STRIKER, EnemyArchetype.SHIELD_GUARD, EnemyArchetype.RAIL_RUNNER, EnemyArchetype.RAILMASTER_9},
            {EnemyArchetype.BRUTE, EnemyArchetype.CARGO_LOADER, EnemyArchetype.HARPOON_DRONE, EnemyArchetype.TIDEBREAKER},
            {EnemyArchetype.SCRAP_STALKER, EnemyArchetype.CORE_JAMMER, EnemyArchetype.FURNACE_BRAWLER, EnemyArchetype.BOSS},
            {EnemyArchetype.VOX_AVATAR, EnemyArchetype.SHADOW_PRIME},
    };

    private StageRoster() {}

    static boolean includesZone(int zone, int type) {
        if (zone < 0 || zone >= TYPES.length) return false;
        for (int candidate : TYPES[zone]) if (candidate == type) return true;
        return false;
    }

    static int decodedAtlasCount(int zone) {
        return zone < 0 || zone >= TYPES.length ? 0 : TYPES[zone].length;
    }

    static int zoneCount() { return TYPES.length; }
}
