#ifndef FAMILY_FORCE_GAME_H
#define FAMILY_FORCE_GAME_H

/*
 * The input values deliberately match the serial SNES joypad bit layout.
 * A platform front end can therefore pass the native pad word directly to
 * game_update().
 */
#define GAME_INPUT_B       0x8000u
#define GAME_INPUT_Y       0x4000u
#define GAME_INPUT_SELECT  0x2000u
#define GAME_INPUT_START   0x1000u
#define GAME_INPUT_UP      0x0800u
#define GAME_INPUT_DOWN    0x0400u
#define GAME_INPUT_LEFT    0x0200u
#define GAME_INPUT_RIGHT   0x0100u
#define GAME_INPUT_A       0x0080u
#define GAME_INPUT_X       0x0040u
#define GAME_INPUT_L       0x0020u
#define GAME_INPUT_R       0x0010u

#define GAME_MAX_PLAYERS      2
#define GAME_MAX_ENEMIES      3
#define GAME_CHARACTER_COUNT  4
#define GAME_WAVE_COUNT       3

#define GAME_WORLD_MIN_X      0
#define GAME_WORLD_MAX_X      480
#define GAME_BELT_MIN_Y       112
#define GAME_BELT_MAX_Y       200
#define GAME_CAMERA_MAX_X     224

/* Keep 816-tcc free of host-only C99 headers while fixing host widths. */
#ifdef SNES_TARGET
typedef unsigned char GameU8;
typedef signed char GameS8;
typedef unsigned short GameU16;
typedef signed short GameS16;
typedef unsigned long GameU32;
#else
#include <stdint.h>
typedef uint8_t GameU8;
typedef int8_t GameS8;
typedef uint16_t GameU16;
typedef int16_t GameS16;
typedef uint32_t GameU32;
#endif

enum GameMode {
    GAME_MODE_TITLE = 0,
    GAME_MODE_SELECT = 1,
    GAME_MODE_PLAY = 2,
    GAME_MODE_PAUSE = 3,
    GAME_MODE_WIN = 4,
    GAME_MODE_GAMEOVER = 5
};

enum GameFacing {
    GAME_FACE_LEFT = 0,
    GAME_FACE_RIGHT = 1
};

enum GamePlayerAction {
    GAME_PLAYER_IDLE = 0,
    GAME_PLAYER_WALK = 1,
    GAME_PLAYER_LIGHT = 2,
    GAME_PLAYER_HEAVY = 3,
    GAME_PLAYER_JUMP = 4,
    GAME_PLAYER_AERIAL = 5,
    GAME_PLAYER_SPECIAL = 6,
    GAME_PLAYER_HURT = 7,
    GAME_PLAYER_DOWN = 8,
    GAME_PLAYER_CHEER = 9
};

enum GameEnemyType {
    GAME_ENEMY_GRUNT = 0,
    GAME_ENEMY_SKATER = 1,
    GAME_ENEMY_BRUTE = 2,
    GAME_ENEMY_BOSS = 3
};

enum GameEnemyState {
    GAME_ENEMY_WAIT = 0,
    GAME_ENEMY_CHASE = 1,
    GAME_ENEMY_WINDUP = 2,
    GAME_ENEMY_ATTACK = 3,
    GAME_ENEMY_RECOVER = 4,
    GAME_ENEMY_HURT = 5,
    GAME_ENEMY_DEFEATED = 6
};

typedef struct GamePlayer {
    GameU8 active;
    GameU8 character;
    GameU8 facing;
    GameU8 action;
    GameU8 action_timer;
    GameU8 combo_step;
    GameU8 combo_window;
    GameU8 invuln_timer;
    GameU8 health;
    GameU8 max_health;
    GameU8 special;
    GameS16 x;
    GameS16 y;
    GameS16 z;
    GameS16 jump_velocity;
    GameU32 score;
} GamePlayer;

typedef struct GameEnemy {
    GameU8 active;
    GameU8 type;
    GameU8 state;
    GameU8 facing;
    GameU8 health;
    GameU8 max_health;
    GameU8 state_timer;
    GameU8 hit_flash;
    GameU8 target_player;
    GameS16 x;
    GameS16 y;
} GameEnemy;

typedef struct GameState {
    GameU8 mode;
    GameU8 player_count;
    GameU8 p2_joined;
    GameU8 selected_character[GAME_MAX_PLAYERS];
    GameU8 wave;
    GameU8 wave_active;
    GameU8 screen_shake;
    GameU8 reserved;
    GameU16 rng;
    GameU16 tick;
    GameU16 previous_input[GAME_MAX_PLAYERS];
    GameS16 camera_x;
    GamePlayer players[GAME_MAX_PLAYERS];
    GameEnemy enemies[GAME_MAX_ENEMIES];
} GameState;

/* Reset always returns to the title screen. A zero seed selects a default. */
void game_reset(GameState *state, GameU16 seed);

/* One call advances exactly one 60 Hz simulation step. */
void game_update(GameState *state, GameU16 pad1, GameU16 pad2);

/* Public for deterministic host tools and optional cosmetic front-end use. */
GameU16 game_random(GameState *state);

#endif
