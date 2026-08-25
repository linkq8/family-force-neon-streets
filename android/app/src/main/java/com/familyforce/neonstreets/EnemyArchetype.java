package com.familyforce.neonstreets;

/** Immutable, allocation-free enemy tuning table shared by spawn, AI and UI. */
final class EnemyArchetype {
    static final int GRUNT = 0, SKATER = 1, BRUTE = 2, BOSS = 3;
    static final int STRIKER = 4, SHIELD_GUARD = 5;
    static final int LANTERN_COURIER = 6, MARKET_ENFORCER = 7, KEEPER_7 = 8;
    static final int RAIL_RUNNER = 9, SIGNAL_WARDEN = 10, RAILMASTER_9 = 11;
    static final int CARGO_LOADER = 12, HARPOON_DRONE = 13;
    static final int DOCK_CRUSHER = 14, TIDEBREAKER = 15;
    static final int SCRAP_STALKER = 16, CORE_JAMMER = 17;
    static final int FURNACE_BRAWLER = 18, PALACE_SENTINEL = 19;
    static final int VOX_AVATAR = 20, SHADOW_PRIME = 21;
    static final int COUNT = 22;

    static final int RANK_REGULAR = 0, RANK_MINI_BOSS = 1;
    static final int RANK_BOSS = 2, RANK_FINAL_BOSS = 3;

    static final EnemyArchetype[] ALL = {
            type("grunt", "GRUNT", 82, 1.12f, 8, 48, 26, 350, 120f, 11, 14, 0, 0),
            type("skater", "SKATER", 70, 1.75f, 8, 48, 26, 350, 110f, 15, 14, 0, 0),
            type("brute", "BRUTE", 115, .82f, 13, 62, 26, 650, 136f, 11, 14, 0, 0),
            type("boss", "JUNK KING", 380, .72f, 18, 88, 34, 3200, 160f, 11, 11, 0, RANK_BOSS),
            type("striker", "STRIKER", 76, 1.48f, 9, 56, 26, 500, 116f, 11, 16, 0, 0),
            type("shield_guard", "SHIELD GUARD", 128, .88f, 11, 58, 29, 800, 132f, 10, 12, 42, 0),
            type("lantern_courier", "LANTERN COURIER", 74, 1.62f, 9, 54, 25, 520, 116f, 14, 15, 0, 0),
            // These heights are part of the pixel-density contract. Enlarging
            // the same source figure here would manufacture visibly larger
            // pixels even when the atlas file itself has high dimensions.
            type("market_enforcer", "MARKET ENFORCER", 210, .82f, 15, 66, 31, 1450, 132f, 10, 12, 55, RANK_MINI_BOSS),
            type("keeper_7", "KEEPER-7", 430, .75f, 20, 92, 35, 3800, 128f, 10, 12, 0, RANK_BOSS),
            type("rail_runner", "RAIL RUNNER", 80, 1.82f, 10, 60, 25, 580, 118f, 15, 16, 0, 0),
            type("signal_warden", "SIGNAL WARDEN", 225, .86f, 16, 70, 32, 1550, 150f, 10, 12, 60, RANK_MINI_BOSS),
            type("railmaster_9", "RAILMASTER-9", 470, .74f, 21, 96, 36, 4100, 166f, 10, 12, 0, RANK_BOSS),
            type("cargo_loader", "CARGO LOADER", 138, .86f, 14, 66, 30, 760, 140f, 10, 13, 0, 0),
            type("harpoon_drone", "HARPOON DRONE", 88, 1.38f, 12, 82, 27, 680, 124f, 13, 15, 0, 0),
            type("dock_crusher", "DOCK CRUSHER", 250, .76f, 18, 74, 34, 1750, 154f, 9, 12, 65, RANK_MINI_BOSS),
            type("tidebreaker", "TIDEBREAKER", 520, .70f, 23, 100, 38, 4500, 170f, 9, 12, 0, RANK_BOSS),
            type("scrap_stalker", "SCRAP STALKER", 96, 1.34f, 12, 60, 27, 700, 126f, 13, 15, 0, 0),
            type("core_jammer", "CORE JAMMER", 84, 1.58f, 12, 72, 25, 720, 120f, 14, 16, 0, 0),
            type("furnace_brawler", "FURNACE BRAWLER", 160, .78f, 17, 70, 32, 900, 146f, 10, 13, 0, 0),
            type("palace_sentinel", "PALACE SENTINEL", 285, .78f, 19, 78, 35, 1950, 158f, 9, 12, 70, RANK_MINI_BOSS),
            type("vox_avatar", "VOX AVATAR", 340, 1.18f, 21, 84, 31, 2600, 150f, 12, 15, 45, RANK_MINI_BOSS),
            type("shadow_prime", "SHADOW PRIME", 760, .84f, 27, 112, 40, 7500, 178f, 10, 13, 80, RANK_FINAL_BOSS),
    };

    final String asset, displayName;
    final int maxHp, damage, attackRange, laneHalf, score, walkFps, attackFps, guard, rank;
    final float speed, renderHeight;

    private EnemyArchetype(String asset, String displayName, int maxHp, float speed,
                           int damage, int attackRange, int laneHalf, int score,
                           float renderHeight, int walkFps, int attackFps, int guard,
                           int rank) {
        this.asset = asset; this.displayName = displayName; this.maxHp = maxHp;
        this.speed = speed; this.damage = damage; this.attackRange = attackRange;
        this.laneHalf = laneHalf; this.score = score; this.renderHeight = renderHeight;
        this.walkFps = walkFps; this.attackFps = attackFps; this.guard = guard;
        this.rank = rank;
    }

    private static EnemyArchetype type(String asset, String name, int hp, float speed,
                                       int damage, int range, int lane, int score,
                                       float height, int walkFps, int attackFps,
                                       int guard, int rank) {
        return new EnemyArchetype(asset, name, hp, speed, damage, range, lane,
                score, height, walkFps, attackFps, guard, rank);
    }

    boolean isMiniBoss() { return rank == RANK_MINI_BOSS; }
    boolean isBoss() { return rank >= RANK_BOSS; }
    boolean isFinalBoss() { return rank == RANK_FINAL_BOSS; }

    static EnemyArchetype of(int type) {
        return ALL[type >= 0 && type < ALL.length ? type : GRUNT];
    }
}
