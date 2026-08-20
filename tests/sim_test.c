#include <assert.h>
#include <stdio.h>

#include "game.h"

static void tap(GameState *state, GameU16 pad1, GameU16 pad2)
{
    game_update(state, pad1, pad2);
    game_update(state, 0u, 0u);
}

static void advance(GameState *state, GameU16 frames)
{
    GameU16 i;

    for (i = 0u; i < frames; ++i) {
        game_update(state, 0u, 0u);
    }
}

static void start_one_player(GameState *state, GameU16 seed)
{
    game_reset(state, seed);
    tap(state, GAME_INPUT_START, 0u);
    assert(state->mode == GAME_MODE_SELECT);
    tap(state, GAME_INPUT_START, 0u);
    assert(state->mode == GAME_MODE_PLAY);
    assert(state->player_count == 1u);
}

static void test_title_select_join_and_controls(void)
{
    GameState state;
    GameU8 old_health;
    GameS16 paused_x;
    GameU8 paused_enemy_timer;
    GameU8 i;

    game_reset(&state, 0x1234u);
    assert(state.mode == GAME_MODE_TITLE);
    assert(state.rng == 0x1234u);

    tap(&state, GAME_INPUT_START, 0u);
    assert(state.mode == GAME_MODE_SELECT);
    assert(state.player_count == 1u);

    tap(&state, 0u, GAME_INPUT_START);
    assert(state.p2_joined == 1u);
    assert(state.player_count == 2u);
    assert(state.selected_character[0] != state.selected_character[1]);

    tap(&state, GAME_INPUT_RIGHT, 0u);
    assert(state.selected_character[0] == 2u);
    tap(&state, 0u, GAME_INPUT_RIGHT);
    assert(state.selected_character[1] == 3u);

    tap(&state, GAME_INPUT_START, 0u);
    assert(state.mode == GAME_MODE_PLAY);
    assert(state.players[0].active == 1u);
    assert(state.players[1].active == 1u);
    assert(state.players[0].character == 2u);
    assert(state.players[1].character == 3u);

    state.players[0].x = 1;
    state.players[0].y = GAME_BELT_MIN_Y;
    game_update(&state, (GameU16)(GAME_INPUT_LEFT | GAME_INPUT_UP), 0u);
    assert(state.players[0].x == GAME_WORLD_MIN_X);
    assert(state.players[0].y == GAME_BELT_MIN_Y);
    game_update(&state, (GameU16)(GAME_INPUT_LEFT | GAME_INPUT_UP), 0u);
    assert(state.players[0].x == GAME_WORLD_MIN_X);
    assert(state.players[0].y == GAME_BELT_MIN_Y);
    game_update(&state, 0u, 0u);

    state.players[0].x = GAME_WORLD_MAX_X - 1;
    state.players[0].y = GAME_BELT_MAX_Y;
    game_update(&state, (GameU16)(GAME_INPUT_RIGHT | GAME_INPUT_DOWN), 0u);
    assert(state.players[0].x == GAME_WORLD_MAX_X);
    assert(state.players[0].y == GAME_BELT_MAX_Y);
    assert(state.wave_active == 1u);
    game_update(&state, 0u, 0u);

    paused_x = state.players[0].x;
    paused_enemy_timer = state.enemies[0].state_timer;
    game_update(&state, GAME_INPUT_START, 0u);
    assert(state.mode == GAME_MODE_PAUSE);
    for (i = 0u; i < 12u; ++i) {
        game_update(&state, GAME_INPUT_RIGHT, GAME_INPUT_Y);
    }
    assert(state.players[0].x == paused_x);
    assert(state.enemies[0].state_timer == paused_enemy_timer);
    game_update(&state, 0u, 0u);
    game_update(&state, GAME_INPUT_START, 0u);
    assert(state.mode == GAME_MODE_PLAY);
    game_update(&state, 0u, 0u);

    state.players[0].x = (GameS16)(state.enemies[0].x - 10);
    state.players[0].y = state.enemies[0].y;
    state.players[0].facing = GAME_FACE_RIGHT;
    state.players[0].action = GAME_PLAYER_IDLE;
    state.players[0].action_timer = 0u;
    old_health = state.enemies[0].health;
    game_update(&state, GAME_INPUT_Y, 0u);
    assert(state.enemies[0].health < old_health);
    assert(state.players[0].action == GAME_PLAYER_LIGHT);
    game_update(&state, 0u, 0u);

    advance(&state, 8u);
    state.players[0].action = GAME_PLAYER_IDLE;
    state.enemies[0].state = GAME_ENEMY_CHASE;
    state.enemies[0].health = 100u;
    state.enemies[0].max_health = 100u;
    state.enemies[0].x = (GameS16)(state.players[0].x + 10);
    state.enemies[0].y = state.players[0].y;
    tap(&state, GAME_INPUT_B, 0u);
    assert(state.players[0].z > 0);
    old_health = state.enemies[0].health;
    game_update(&state, GAME_INPUT_Y, 0u);
    assert(state.players[0].action == GAME_PLAYER_AERIAL);
    assert(state.enemies[0].health < old_health);
    game_update(&state, 0u, 0u);

    advance(&state, 20u);
    state.players[0].action = GAME_PLAYER_IDLE;
    state.players[0].action_timer = 0u;
    state.enemies[0].state = GAME_ENEMY_CHASE;
    state.enemies[0].health = 100u;
    state.enemies[0].x = (GameS16)(state.players[0].x + 10);
    state.enemies[0].y = state.players[0].y;
    old_health = state.enemies[0].health;
    game_update(&state, GAME_INPUT_X, 0u);
    assert(state.players[0].action == GAME_PLAYER_HEAVY);
    assert(state.enemies[0].health < old_health);
    game_update(&state, 0u, 0u);

    advance(&state, 12u);
    state.players[0].action = GAME_PLAYER_IDLE;
    state.players[0].action_timer = 0u;
    state.players[0].special = 50u;
    state.enemies[0].state = GAME_ENEMY_CHASE;
    state.enemies[0].x = (GameS16)(state.players[0].x - 10);
    state.enemies[0].y = state.players[0].y;
    old_health = state.enemies[0].health;
    game_update(&state, GAME_INPUT_A, 0u);
    assert(state.players[0].action == GAME_PLAYER_SPECIAL);
    assert(state.players[0].special < 50u);
    assert(state.enemies[0].health < old_health);
}

static void defeat_current_wave(GameState *state)
{
    GameU8 i;
    GameU8 wave_before;

    assert(state->mode == GAME_MODE_PLAY);
    assert(state->wave_active == 1u);
    wave_before = state->wave;
    state->players[0].health = 100u;
    state->players[0].invuln_timer = 0u;
    state->players[0].z = 0;
    state->players[0].jump_velocity = 0;
    state->players[0].action = GAME_PLAYER_IDLE;
    state->players[0].action_timer = 0u;
    state->players[0].facing = GAME_FACE_RIGHT;

    for (i = 0u; i < GAME_MAX_ENEMIES; ++i) {
        if (state->enemies[i].active != 0u) {
            state->enemies[i].health = 1u;
            state->enemies[i].state = GAME_ENEMY_CHASE;
            state->enemies[i].state_timer = 0u;
            state->enemies[i].x = (GameS16)(state->players[0].x + 10);
            state->enemies[i].y = state->players[0].y;
        }
    }

    game_update(state, 0u, 0u);
    game_update(state, GAME_INPUT_Y, 0u);
    game_update(state, 0u, 0u);
    advance(state, 16u);
    assert(state->wave == (GameU8)(wave_before + 1u));
}

static void test_three_wave_progression_and_win(void)
{
    GameState state;

    start_one_player(&state, 0x9876u);
    state.players[0].x = 72;
    game_update(&state, 0u, 0u);
    assert(state.wave == 0u);
    assert(state.wave_active == 1u);
    defeat_current_wave(&state);
    assert(state.mode == GAME_MODE_PLAY);

    state.players[0].x = 224;
    game_update(&state, 0u, 0u);
    assert(state.wave == 1u);
    assert(state.wave_active == 1u);
    assert(state.enemies[2].type == GAME_ENEMY_BRUTE);
    defeat_current_wave(&state);
    assert(state.mode == GAME_MODE_PLAY);

    state.players[0].x = 384;
    game_update(&state, 0u, 0u);
    assert(state.wave == 2u);
    assert(state.wave_active == 1u);
    assert(state.enemies[1].type == GAME_ENEMY_BOSS);
    defeat_current_wave(&state);
    assert(state.wave == GAME_WAVE_COUNT);
    assert(state.mode == GAME_MODE_WIN);
    assert(state.players[0].action == GAME_PLAYER_CHEER);
    tap(&state, GAME_INPUT_START, 0u);
    assert(state.mode == GAME_MODE_TITLE);
}

static void test_gameover(void)
{
    GameState state;
    GameEnemy *enemy;

    start_one_player(&state, 0x4567u);
    state.players[0].x = 72;
    game_update(&state, 0u, 0u);
    assert(state.wave_active == 1u);

    state.players[0].health = 8u;
    state.players[0].invuln_timer = 0u;
    enemy = &state.enemies[0];
    enemy->x = (GameS16)(state.players[0].x + 10);
    enemy->y = state.players[0].y;
    enemy->target_player = 0u;
    enemy->state = GAME_ENEMY_WINDUP;
    enemy->state_timer = 1u;
    game_update(&state, 0u, 0u);
    assert(state.players[0].health == 0u);
    assert(state.mode == GAME_MODE_GAMEOVER);
    tap(&state, GAME_INPUT_START, 0u);
    assert(state.mode == GAME_MODE_TITLE);
}

static GameU32 state_crc32(const GameState *state)
{
    const GameU8 *bytes;
    GameU32 crc;
    GameU16 i;
    GameU8 bit;

    bytes = (const GameU8 *)state;
    crc = 0xfffffffful;
    for (i = 0u; i < (GameU16)sizeof(GameState); ++i) {
        crc ^= (GameU32)bytes[i];
        for (bit = 0u; bit < 8u; ++bit) {
            if ((crc & 1ul) != 0ul) {
                crc = (crc >> 1) ^ 0xedb88320ul;
            } else {
                crc >>= 1;
            }
        }
    }
    return crc ^ 0xfffffffful;
}

static void run_deterministic_script(GameState *state)
{
    GameU16 frame;
    GameU16 pad1;
    GameU16 pad2;

    game_reset(state, 0xbeefu);
    for (frame = 0u; frame < 720u; ++frame) {
        pad1 = 0u;
        pad2 = 0u;
        if (frame == 0u) {
            pad1 = GAME_INPUT_START;
        } else if (frame == 2u) {
            pad2 = GAME_INPUT_START;
        } else if (frame == 4u) {
            pad1 = GAME_INPUT_RIGHT;
        } else if (frame == 6u) {
            pad1 = GAME_INPUT_START;
        } else if (frame == 200u || frame == 204u) {
            pad1 = GAME_INPUT_START;
        } else if (frame > 8u) {
            if ((frame & 31u) < 24u) {
                pad1 |= GAME_INPUT_RIGHT;
            }
            if ((frame & 63u) < 12u) {
                pad1 |= GAME_INPUT_UP;
            } else if ((frame & 63u) > 52u) {
                pad1 |= GAME_INPUT_DOWN;
            }
            if ((frame % 29u) == 0u) {
                pad1 |= GAME_INPUT_Y;
            }
            if ((frame % 47u) == 0u) {
                pad1 |= GAME_INPUT_X;
            }
            if ((frame % 61u) == 0u) {
                pad1 |= GAME_INPUT_B;
            }
            if ((frame % 113u) == 0u) {
                pad1 |= GAME_INPUT_A;
            }

            if ((frame & 15u) < 11u) {
                pad2 |= GAME_INPUT_RIGHT;
            }
            if ((frame & 47u) < 8u) {
                pad2 |= GAME_INPUT_DOWN;
            } else if ((frame & 47u) > 39u) {
                pad2 |= GAME_INPUT_UP;
            }
            if ((frame % 31u) == 0u) {
                pad2 |= GAME_INPUT_Y;
            }
            if ((frame % 73u) == 0u) {
                pad2 |= GAME_INPUT_X;
            }
        }
        game_update(state, pad1, pad2);
    }
}

static void test_deterministic_repeat_crc(void)
{
    GameState first;
    GameState second;
    GameU32 first_crc;
    GameU32 second_crc;

    run_deterministic_script(&first);
    run_deterministic_script(&second);
    first_crc = state_crc32(&first);
    second_crc = state_crc32(&second);
    assert(first_crc == second_crc);
    assert(first_crc != 0ul);
    printf("deterministic state CRC32: %08lx\n", (unsigned long)first_crc);
}

int main(void)
{
    test_title_select_join_and_controls();
    test_three_wave_progression_and_win();
    test_gameover();
    test_deterministic_repeat_crc();
    puts("game simulation tests passed");
    return 0;
}
