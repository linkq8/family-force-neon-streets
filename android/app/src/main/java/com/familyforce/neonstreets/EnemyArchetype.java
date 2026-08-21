package com.familyforce.neonstreets;

/** Immutable, allocation-free enemy tuning table shared by spawn, AI and UI. */
final class EnemyArchetype {
    static final int GRUNT = 0;
    static final int SKATER = 1;
    static final int BRUTE = 2;
    static final int BOSS = 3;
    static final int STRIKER = 4;
    static final int SHIELD_GUARD = 5;
    static final int COUNT = 6;

    static final EnemyArchetype[] ALL = {
            new EnemyArchetype("grunt", "GRUNT", 82, 1.12f, 8, 48, 26, 350, 120f, 11, 14, 0),
            new EnemyArchetype("skater", "SKATER", 70, 1.75f, 8, 48, 26, 350, 110f, 15, 14, 0),
            new EnemyArchetype("brute", "BRUTE", 115, .82f, 13, 62, 26, 650, 136f, 11, 14, 0),
            new EnemyArchetype("boss", "JUNK KING", 330, .72f, 18, 88, 34, 3000, 160f, 11, 11, 0),
            new EnemyArchetype("striker", "STRIKER", 76, 1.48f, 9, 56, 26, 500, 116f, 11, 16, 0),
            new EnemyArchetype("shield_guard", "SHIELD GUARD", 128, .88f, 11, 58, 29, 800, 132f, 10, 12, 42),
    };

    final String asset;
    final String displayName;
    final int maxHp;
    final float speed;
    final int damage;
    final int attackRange;
    final int laneHalf;
    final int score;
    final float renderHeight;
    final int walkFps;
    final int attackFps;
    final int guard;

    private EnemyArchetype(String asset, String displayName, int maxHp, float speed,
                           int damage, int attackRange, int laneHalf, int score,
                           float renderHeight, int walkFps, int attackFps, int guard) {
        this.asset = asset;
        this.displayName = displayName;
        this.maxHp = maxHp;
        this.speed = speed;
        this.damage = damage;
        this.attackRange = attackRange;
        this.laneHalf = laneHalf;
        this.score = score;
        this.renderHeight = renderHeight;
        this.walkFps = walkFps;
        this.attackFps = attackFps;
        this.guard = guard;
    }

    static EnemyArchetype of(int type) {
        return ALL[type >= 0 && type < ALL.length ? type : GRUNT];
    }
}
