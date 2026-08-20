#include "game.h"

#define GAME_NO_TARGET 255u

static GameS16 game_abs16(GameS16 value)
{
    if (value < 0) {
        return (GameS16)(-value);
    }
    return value;
}

static GameS16 game_clamp16(GameS16 value, GameS16 minimum, GameS16 maximum)
{
    if (value < minimum) {
        return minimum;
    }
    if (value > maximum) {
        return maximum;
    }
    return value;
}

static void game_zero_state(GameState *state)
{
    GameU8 *bytes;
    GameU16 i;

    bytes = (GameU8 *)state;
    for (i = 0u; i < (GameU16)sizeof(GameState); ++i) {
        bytes[i] = 0u;
    }
}

GameU16 game_random(GameState *state)
{
    GameU16 value;

    value = state->rng;
    value = (GameU16)(value ^ (GameU16)(value << 7));
    value = (GameU16)(value ^ (GameU16)(value >> 9));
    value = (GameU16)(value ^ (GameU16)(value << 8));
    state->rng = value;
    return value;
}

void game_reset(GameState *state, GameU16 seed)
{
    if (state == 0) {
        return;
    }

    game_zero_state(state);
    if (seed == 0u) {
        seed = 0xace1u;
    }

    state->rng = seed;
    state->mode = GAME_MODE_TITLE;
    state->player_count = 1u;
    state->selected_character[0] = 0u;
    state->selected_character[1] = 1u;
}

static void game_clear_enemies(GameState *state)
{
    GameU8 i;

    for (i = 0u; i < GAME_MAX_ENEMIES; ++i) {
        state->enemies[i].active = 0u;
        state->enemies[i].health = 0u;
        state->enemies[i].state = GAME_ENEMY_WAIT;
        state->enemies[i].state_timer = 0u;
        state->enemies[i].hit_flash = 0u;
    }
}

static void game_enter_select(GameState *state)
{
    state->mode = GAME_MODE_SELECT;
    state->player_count = 1u;
    state->p2_joined = 0u;
    state->selected_character[0] = 0u;
    state->selected_character[1] = 1u;
    state->players[0].active = 0u;
    state->players[1].active = 0u;
    game_clear_enemies(state);
}

static void game_init_player(GamePlayer *player, GameU8 character,
                             GameS16 x, GameS16 y)
{
    player->active = 1u;
    player->character = character;
    player->facing = GAME_FACE_RIGHT;
    player->action = GAME_PLAYER_IDLE;
    player->action_timer = 0u;
    player->combo_step = 0u;
    player->combo_window = 0u;
    player->invuln_timer = 0u;
    player->health = 100u;
    player->max_health = 100u;
    player->special = 50u;
    player->x = x;
    player->y = y;
    player->z = 0;
    player->jump_velocity = 0;
    player->score = 0ul;
}

static void game_start_match(GameState *state)
{
    state->mode = GAME_MODE_PLAY;
    state->wave = 0u;
    state->wave_active = 0u;
    state->camera_x = 0;
    state->screen_shake = 0u;
    game_clear_enemies(state);

    game_init_player(&state->players[0], state->selected_character[0],
                     24, 164);
    if (state->p2_joined != 0u) {
        game_init_player(&state->players[1], state->selected_character[1],
                         38, 184);
        state->player_count = 2u;
    } else {
        state->players[1].active = 0u;
        state->player_count = 1u;
    }
}

static void game_change_character(GameState *state, GameU8 player_index,
                                  GameS8 direction)
{
    GameU8 candidate;
    GameU8 other;
    GameU8 attempts;

    candidate = state->selected_character[player_index];
    other = (GameU8)(player_index ^ 1u);
    for (attempts = 0u; attempts < GAME_CHARACTER_COUNT; ++attempts) {
        if (direction < 0) {
            if (candidate == 0u) {
                candidate = (GameU8)(GAME_CHARACTER_COUNT - 1);
            } else {
                candidate = (GameU8)(candidate - 1u);
            }
        } else {
            candidate = (GameU8)(candidate + 1u);
            if (candidate >= GAME_CHARACTER_COUNT) {
                candidate = 0u;
            }
        }

        if (state->p2_joined == 0u ||
            candidate != state->selected_character[other]) {
            state->selected_character[player_index] = candidate;
            return;
        }
    }
}

static void game_update_select(GameState *state, GameU16 pressed1,
                               GameU16 pressed2)
{
    if ((pressed1 & GAME_INPUT_B) != 0u) {
        state->mode = GAME_MODE_TITLE;
        return;
    }

    if ((pressed2 & GAME_INPUT_START) != 0u && state->p2_joined == 0u) {
        state->p2_joined = 1u;
        state->player_count = 2u;
        if (state->selected_character[1] == state->selected_character[0]) {
            game_change_character(state, 1u, 1);
        }
    } else if ((pressed2 & GAME_INPUT_SELECT) != 0u &&
               state->p2_joined != 0u) {
        state->p2_joined = 0u;
        state->player_count = 1u;
    }

    if ((pressed1 & GAME_INPUT_LEFT) != 0u) {
        game_change_character(state, 0u, -1);
    } else if ((pressed1 & GAME_INPUT_RIGHT) != 0u) {
        game_change_character(state, 0u, 1);
    }

    if (state->p2_joined != 0u) {
        if ((pressed2 & GAME_INPUT_LEFT) != 0u) {
            game_change_character(state, 1u, -1);
        } else if ((pressed2 & GAME_INPUT_RIGHT) != 0u) {
            game_change_character(state, 1u, 1);
        }
    }

    if ((pressed1 &
         (GAME_INPUT_START | GAME_INPUT_Y | GAME_INPUT_A)) != 0u) {
        game_start_match(state);
    }
}

static void game_spawn_enemy(GameState *state, GameU8 slot, GameU8 type,
                             GameS16 x, GameS16 y, GameU8 health)
{
    GameEnemy *enemy;

    enemy = &state->enemies[slot];
    enemy->active = 1u;
    enemy->type = type;
    enemy->state = GAME_ENEMY_WAIT;
    enemy->facing = GAME_FACE_LEFT;
    enemy->health = health;
    enemy->max_health = health;
    enemy->state_timer = (GameU8)(10u + (game_random(state) & 7u));
    enemy->hit_flash = 0u;
    enemy->target_player = 0u;
    enemy->x = x;
    enemy->y = y;
}

static void game_spawn_wave(GameState *state)
{
    game_clear_enemies(state);

    if (state->wave == 0u) {
        game_spawn_enemy(state, 0u, GAME_ENEMY_GRUNT, 100, 158, 24u);
        game_spawn_enemy(state, 1u, GAME_ENEMY_GRUNT, 138, 190, 24u);
    } else if (state->wave == 1u) {
        game_spawn_enemy(state, 0u, GAME_ENEMY_SKATER, 252, 152, 28u);
        game_spawn_enemy(state, 1u, GAME_ENEMY_GRUNT, 286, 184, 32u);
        game_spawn_enemy(state, 2u, GAME_ENEMY_BRUTE, 320, 166, 48u);
    } else {
        game_spawn_enemy(state, 0u, GAME_ENEMY_GRUNT, 410, 196, 32u);
        game_spawn_enemy(state, 1u, GAME_ENEMY_BOSS, 448, 164, 100u);
        game_spawn_enemy(state, 2u, GAME_ENEMY_SKATER, 474, 188, 32u);
    }

    state->wave_active = 1u;
}

static GameS16 game_lead_player_x(const GameState *state)
{
    GameS16 result;
    GameU8 i;

    result = 0;
    for (i = 0u; i < GAME_MAX_PLAYERS; ++i) {
        if (state->players[i].active != 0u &&
            state->players[i].health != 0u &&
            state->players[i].x > result) {
            result = state->players[i].x;
        }
    }
    return result;
}

static void game_maybe_spawn_wave(GameState *state)
{
    static const GameS16 triggers[GAME_WAVE_COUNT] = { 72, 224, 384 };

    if (state->wave_active == 0u && state->wave < GAME_WAVE_COUNT &&
        game_lead_player_x(state) >= triggers[state->wave]) {
        game_spawn_wave(state);
    }
}

static GameU32 game_enemy_score(GameU8 type)
{
    if (type == GAME_ENEMY_BOSS) {
        return 2000ul;
    }
    if (type == GAME_ENEMY_BRUTE) {
        return 500ul;
    }
    if (type == GAME_ENEMY_SKATER) {
        return 300ul;
    }
    return 200ul;
}

static void game_damage_enemy(GameState *state, GameU8 player_index,
                              GameU8 enemy_index, GameU8 damage,
                              GameS8 push_direction)
{
    GamePlayer *player;
    GameEnemy *enemy;
    GameU16 score_add;

    player = &state->players[player_index];
    enemy = &state->enemies[enemy_index];
    if (enemy->active == 0u || enemy->state == GAME_ENEMY_DEFEATED) {
        return;
    }

    score_add = (GameU16)damage * 10u;
    player->score += (GameU32)score_add;
    if (player->special < 97u) {
        player->special = (GameU8)(player->special + 3u);
    } else {
        player->special = 100u;
    }

    enemy->hit_flash = 4u;
    if (enemy->health <= damage) {
        enemy->health = 0u;
        enemy->state = GAME_ENEMY_DEFEATED;
        enemy->state_timer = 14u;
        player->score += game_enemy_score(enemy->type);
    } else {
        enemy->health = (GameU8)(enemy->health - damage);
        enemy->state = GAME_ENEMY_HURT;
        enemy->state_timer = 5u;
        enemy->x = game_clamp16((GameS16)(enemy->x + push_direction * 3),
                                GAME_WORLD_MIN_X, GAME_WORLD_MAX_X);
    }
}

static void game_player_attack(GameState *state, GameU8 player_index,
                               GameU8 damage, GameS16 range_x,
                               GameS16 range_y, GameU8 all_around)
{
    GamePlayer *player;
    GameEnemy *enemy;
    GameS16 dx;
    GameS16 dy;
    GameU8 i;
    GameS8 push;

    player = &state->players[player_index];
    push = player->facing == GAME_FACE_RIGHT ? 1 : -1;

    for (i = 0u; i < GAME_MAX_ENEMIES; ++i) {
        enemy = &state->enemies[i];
        if (enemy->active == 0u || enemy->state == GAME_ENEMY_DEFEATED) {
            continue;
        }

        dx = (GameS16)(enemy->x - player->x);
        dy = game_abs16((GameS16)(enemy->y - player->y));
        if (game_abs16(dx) > range_x || dy > range_y) {
            continue;
        }
        if (all_around == 0u) {
            if (player->facing == GAME_FACE_RIGHT && dx < -6) {
                continue;
            }
            if (player->facing == GAME_FACE_LEFT && dx > 6) {
                continue;
            }
        }

        game_damage_enemy(state, player_index, i, damage, push);
    }
}

static GameU8 game_can_start_attack(const GamePlayer *player)
{
    if (player->action == GAME_PLAYER_IDLE ||
        player->action == GAME_PLAYER_WALK) {
        return 1u;
    }
    if (player->action == GAME_PLAYER_LIGHT && player->action_timer <= 2u) {
        return 1u;
    }
    return 0u;
}

static void game_tick_player_timers(GamePlayer *player)
{
    if (player->invuln_timer != 0u) {
        player->invuln_timer = (GameU8)(player->invuln_timer - 1u);
    }
    if (player->combo_window != 0u) {
        player->combo_window = (GameU8)(player->combo_window - 1u);
        if (player->combo_window == 0u) {
            player->combo_step = 0u;
        }
    }
    if (player->action_timer != 0u) {
        player->action_timer = (GameU8)(player->action_timer - 1u);
        if (player->action_timer == 0u && player->health != 0u) {
            if (player->z > 0) {
                player->action = GAME_PLAYER_JUMP;
            } else {
                player->action = GAME_PLAYER_IDLE;
            }
        }
    }
}

static void game_update_jump(GamePlayer *player, GameU16 tick)
{
    if (player->z > 0 || player->jump_velocity > 0) {
        player->z = (GameS16)(player->z + player->jump_velocity);
        if ((tick & 1u) == 0u) {
            player->jump_velocity = (GameS16)(player->jump_velocity - 1);
        }
        if (player->z <= 0 && player->jump_velocity < 0) {
            player->z = 0;
            player->jump_velocity = 0;
            if (player->action == GAME_PLAYER_JUMP ||
                player->action == GAME_PLAYER_AERIAL) {
                player->action = GAME_PLAYER_IDLE;
                player->action_timer = 0u;
            }
        }
    }
}

static void game_update_player(GameState *state, GameU8 player_index,
                               GameU16 input, GameU16 pressed)
{
    GamePlayer *player;
    GameS16 move_x;
    GameS16 move_y;
    GameU8 damage;

    player = &state->players[player_index];
    if (player->active == 0u || player->health == 0u) {
        return;
    }

    game_tick_player_timers(player);
    move_x = 0;
    move_y = 0;
    if (player->action != GAME_PLAYER_HURT &&
        player->action != GAME_PLAYER_SPECIAL &&
        player->action != GAME_PLAYER_HEAVY) {
        if ((input & GAME_INPUT_LEFT) != 0u &&
            (input & GAME_INPUT_RIGHT) == 0u) {
            move_x = -2;
            player->facing = GAME_FACE_LEFT;
        } else if ((input & GAME_INPUT_RIGHT) != 0u &&
                   (input & GAME_INPUT_LEFT) == 0u) {
            move_x = 2;
            player->facing = GAME_FACE_RIGHT;
        }
        if ((input & GAME_INPUT_UP) != 0u &&
            (input & GAME_INPUT_DOWN) == 0u) {
            move_y = (state->tick & 1u) != 0u ? -2 : -1;
        } else if ((input & GAME_INPUT_DOWN) != 0u &&
                   (input & GAME_INPUT_UP) == 0u) {
            move_y = (state->tick & 1u) != 0u ? 2 : 1;
        }
    }

    if (move_x != 0 || move_y != 0) {
        player->x = game_clamp16((GameS16)(player->x + move_x),
                                 GAME_WORLD_MIN_X, GAME_WORLD_MAX_X);
        player->y = game_clamp16((GameS16)(player->y + move_y),
                                 GAME_BELT_MIN_Y, GAME_BELT_MAX_Y);
        if (player->z == 0 &&
            (player->action == GAME_PLAYER_IDLE ||
             player->action == GAME_PLAYER_WALK)) {
            player->action = GAME_PLAYER_WALK;
        }
    } else if (player->z == 0 && player->action == GAME_PLAYER_WALK) {
        player->action = GAME_PLAYER_IDLE;
    }

    if ((pressed & GAME_INPUT_B) != 0u && player->z == 0 &&
        (player->action == GAME_PLAYER_IDLE ||
         player->action == GAME_PLAYER_WALK)) {
        player->z = 1;
        player->jump_velocity = 6;
        player->action = GAME_PLAYER_JUMP;
        player->action_timer = 0u;
    }

    if ((pressed & GAME_INPUT_A) != 0u && player->special >= 40u &&
        player->action != GAME_PLAYER_HURT) {
        player->special = (GameU8)(player->special - 40u);
        player->action = GAME_PLAYER_SPECIAL;
        player->action_timer = 12u;
        state->screen_shake = 8u;
        game_player_attack(state, player_index, 20u, 58, 32, 1u);
    } else if ((pressed & GAME_INPUT_X) != 0u &&
               game_can_start_attack(player) != 0u) {
        player->action = GAME_PLAYER_HEAVY;
        player->action_timer = 9u;
        game_player_attack(state, player_index, 14u, 34, 20, 0u);
    } else if ((pressed & GAME_INPUT_Y) != 0u) {
        if (player->z > 0 && player->action != GAME_PLAYER_HURT) {
            player->action = GAME_PLAYER_AERIAL;
            player->action_timer = 7u;
            game_player_attack(state, player_index, 10u, 32, 24, 0u);
        } else if (game_can_start_attack(player) != 0u) {
            if (player->combo_window != 0u) {
                player->combo_step = (GameU8)(player->combo_step + 1u);
                if (player->combo_step > 3u) {
                    player->combo_step = 1u;
                }
            } else {
                player->combo_step = 1u;
            }
            player->combo_window = 18u;
            player->action = GAME_PLAYER_LIGHT;
            player->action_timer = 6u;
            damage = (GameU8)(4u + player->combo_step * 2u);
            game_player_attack(state, player_index, damage, 29, 18, 0u);
        }
    }
    game_update_jump(player, state->tick);
}

static GameU8 game_nearest_player(const GameState *state,
                                  const GameEnemy *enemy)
{
    GameU8 best;
    GameU8 i;
    GameS16 distance;
    GameS16 best_distance;

    best = GAME_NO_TARGET;
    best_distance = 32767;
    for (i = 0u; i < GAME_MAX_PLAYERS; ++i) {
        if (state->players[i].active == 0u ||
            state->players[i].health == 0u) {
            continue;
        }
        distance = (GameS16)(game_abs16((GameS16)(state->players[i].x - enemy->x)) +
                   game_abs16((GameS16)(state->players[i].y - enemy->y)));
        if (distance < best_distance) {
            best_distance = distance;
            best = i;
        }
    }
    return best;
}

static void game_damage_player(GameState *state, GameU8 player_index,
                               GameU8 damage, GameS8 push_direction)
{
    GamePlayer *player;

    player = &state->players[player_index];
    if (player->active == 0u || player->health == 0u ||
        player->invuln_timer != 0u) {
        return;
    }

    if (player->health <= damage) {
        player->health = 0u;
        player->action = GAME_PLAYER_DOWN;
        player->action_timer = 0u;
        player->z = 0;
        player->jump_velocity = 0;
    } else {
        player->health = (GameU8)(player->health - damage);
        player->action = GAME_PLAYER_HURT;
        player->action_timer = 10u;
        player->invuln_timer = 40u;
        player->x = game_clamp16((GameS16)(player->x + push_direction * 5),
                                 GAME_WORLD_MIN_X, GAME_WORLD_MAX_X);
    }
    state->screen_shake = 5u;
}

static GameU8 game_enemy_damage(const GameEnemy *enemy)
{
    if (enemy->type == GAME_ENEMY_BOSS) {
        return 18u;
    }
    if (enemy->type == GAME_ENEMY_BRUTE) {
        return 14u;
    }
    if (enemy->type == GAME_ENEMY_SKATER) {
        return 9u;
    }
    return 8u;
}

static void game_enemy_try_hit(GameState *state, GameEnemy *enemy)
{
    GamePlayer *player;
    GameS16 dx;
    GameS16 dy;
    GameS16 range;
    GameS8 push;

    if (enemy->target_player >= GAME_MAX_PLAYERS) {
        return;
    }
    player = &state->players[enemy->target_player];
    dx = (GameS16)(player->x - enemy->x);
    dy = game_abs16((GameS16)(player->y - enemy->y));
    range = enemy->type == GAME_ENEMY_BOSS ? 34 : 24;
    if (game_abs16(dx) <= range && dy <= 18) {
        push = dx < 0 ? -1 : 1;
        game_damage_player(state, enemy->target_player,
                           game_enemy_damage(enemy), push);
    }
}

static void game_update_enemy(GameState *state, GameU8 enemy_index)
{
    GameEnemy *enemy;
    GamePlayer *target;
    GameS16 dx;
    GameS16 dy;
    GameS16 attack_range;
    GameS16 speed;

    enemy = &state->enemies[enemy_index];
    if (enemy->active == 0u) {
        return;
    }
    if (enemy->hit_flash != 0u) {
        enemy->hit_flash = (GameU8)(enemy->hit_flash - 1u);
    }

    if (enemy->state == GAME_ENEMY_DEFEATED) {
        if (enemy->state_timer != 0u) {
            enemy->state_timer = (GameU8)(enemy->state_timer - 1u);
        }
        if (enemy->state_timer == 0u) {
            enemy->active = 0u;
        }
        return;
    }

    if (enemy->state == GAME_ENEMY_HURT) {
        if (enemy->state_timer != 0u) {
            enemy->state_timer = (GameU8)(enemy->state_timer - 1u);
        }
        if (enemy->state_timer == 0u) {
            enemy->state = GAME_ENEMY_CHASE;
        }
        return;
    }

    if (enemy->state == GAME_ENEMY_WAIT ||
        enemy->state == GAME_ENEMY_RECOVER) {
        if (enemy->state_timer != 0u) {
            enemy->state_timer = (GameU8)(enemy->state_timer - 1u);
        }
        if (enemy->state_timer == 0u) {
            enemy->state = GAME_ENEMY_CHASE;
        }
        return;
    }

    if (enemy->state == GAME_ENEMY_WINDUP) {
        if (enemy->state_timer != 0u) {
            enemy->state_timer = (GameU8)(enemy->state_timer - 1u);
        }
        if (enemy->state_timer == 0u) {
            enemy->state = GAME_ENEMY_ATTACK;
            enemy->state_timer = 4u;
            game_enemy_try_hit(state, enemy);
        }
        return;
    }

    if (enemy->state == GAME_ENEMY_ATTACK) {
        if (enemy->state_timer != 0u) {
            enemy->state_timer = (GameU8)(enemy->state_timer - 1u);
        }
        if (enemy->state_timer == 0u) {
            enemy->state = GAME_ENEMY_RECOVER;
            enemy->state_timer = (GameU8)(10u + (game_random(state) & 3u));
        }
        return;
    }

    enemy->target_player = game_nearest_player(state, enemy);
    if (enemy->target_player == GAME_NO_TARGET) {
        return;
    }

    target = &state->players[enemy->target_player];
    dx = (GameS16)(target->x - enemy->x);
    dy = (GameS16)(target->y - enemy->y);
    attack_range = enemy->type == GAME_ENEMY_BOSS ? 28 : 19;
    if (game_abs16(dx) <= attack_range && game_abs16(dy) <= 13) {
        enemy->state = GAME_ENEMY_WINDUP;
        enemy->state_timer = enemy->type == GAME_ENEMY_SKATER ? 5u : 8u;
        return;
    }

    speed = enemy->type == GAME_ENEMY_SKATER ? 2 : 1;
    if (game_abs16(dx) > attack_range) {
        if (dx < 0) {
            enemy->x = (GameS16)(enemy->x - speed);
            enemy->facing = GAME_FACE_LEFT;
        } else {
            enemy->x = (GameS16)(enemy->x + speed);
            enemy->facing = GAME_FACE_RIGHT;
        }
    }
    if (game_abs16(dy) > 4) {
        if (dy < 0) {
            enemy->y = (GameS16)(enemy->y - 1);
        } else {
            enemy->y = (GameS16)(enemy->y + 1);
        }
    }

    enemy->x = game_clamp16(enemy->x, GAME_WORLD_MIN_X, GAME_WORLD_MAX_X);
    enemy->y = game_clamp16(enemy->y, GAME_BELT_MIN_Y, GAME_BELT_MAX_Y);
}

static GameU8 game_any_enemy_active(const GameState *state)
{
    GameU8 i;

    for (i = 0u; i < GAME_MAX_ENEMIES; ++i) {
        if (state->enemies[i].active != 0u) {
            return 1u;
        }
    }
    return 0u;
}

static GameU8 game_any_player_alive(const GameState *state)
{
    GameU8 i;

    for (i = 0u; i < GAME_MAX_PLAYERS; ++i) {
        if (state->players[i].active != 0u &&
            state->players[i].health != 0u) {
            return 1u;
        }
    }
    return 0u;
}

static void game_finish_wave_if_clear(GameState *state)
{
    GameU8 i;
    GamePlayer *player;

    if (state->wave_active == 0u || game_any_enemy_active(state) != 0u) {
        return;
    }

    state->wave_active = 0u;
    state->wave = (GameU8)(state->wave + 1u);
    for (i = 0u; i < GAME_MAX_PLAYERS; ++i) {
        player = &state->players[i];
        if (player->active != 0u && player->health != 0u) {
            if (player->special <= 85u) {
                player->special = (GameU8)(player->special + 15u);
            } else {
                player->special = 100u;
            }
        }
    }

    if (state->wave >= GAME_WAVE_COUNT) {
        state->mode = GAME_MODE_WIN;
        for (i = 0u; i < GAME_MAX_PLAYERS; ++i) {
            if (state->players[i].active != 0u &&
                state->players[i].health != 0u) {
                state->players[i].action = GAME_PLAYER_CHEER;
                state->players[i].action_timer = 0u;
            }
        }
    }
}

static void game_update_camera(GameState *state)
{
    GameS16 target;

    target = (GameS16)(game_lead_player_x(state) - 96);
    target = game_clamp16(target, 0, GAME_CAMERA_MAX_X);
    if (state->camera_x < target) {
        state->camera_x = (GameS16)(state->camera_x + 4);
        if (state->camera_x > target) {
            state->camera_x = target;
        }
    } else if (state->camera_x > target) {
        state->camera_x = (GameS16)(state->camera_x - 4);
        if (state->camera_x < target) {
            state->camera_x = target;
        }
    }
}

static void game_update_play(GameState *state, GameU16 input1,
                             GameU16 input2, GameU16 pressed1,
                             GameU16 pressed2)
{
    GameU8 i;

    if ((pressed1 & GAME_INPUT_START) != 0u ||
        (state->p2_joined != 0u &&
         (pressed2 & GAME_INPUT_START) != 0u)) {
        state->mode = GAME_MODE_PAUSE;
        return;
    }

    if (state->screen_shake != 0u) {
        state->screen_shake = (GameU8)(state->screen_shake - 1u);
    }

    game_update_player(state, 0u, input1, pressed1);
    game_update_player(state, 1u, input2, pressed2);
    game_maybe_spawn_wave(state);

    for (i = 0u; i < GAME_MAX_ENEMIES; ++i) {
        game_update_enemy(state, i);
    }

    game_finish_wave_if_clear(state);
    game_update_camera(state);

    if (state->mode == GAME_MODE_PLAY &&
        game_any_player_alive(state) == 0u) {
        state->mode = GAME_MODE_GAMEOVER;
    }
}

static void game_return_to_title(GameState *state)
{
    GameU16 seed;

    seed = state->rng;
    game_reset(state, seed);
}

void game_update(GameState *state, GameU16 pad1, GameU16 pad2)
{
    GameU16 pressed1;
    GameU16 pressed2;

    if (state == 0) {
        return;
    }

    pressed1 = (GameU16)(pad1 & (GameU16)(~state->previous_input[0]));
    pressed2 = (GameU16)(pad2 & (GameU16)(~state->previous_input[1]));
    state->tick = (GameU16)(state->tick + 1u);

    if (state->mode == GAME_MODE_TITLE) {
        if ((pressed1 & GAME_INPUT_START) != 0u) {
            game_enter_select(state);
        }
    } else if (state->mode == GAME_MODE_SELECT) {
        game_update_select(state, pressed1, pressed2);
    } else if (state->mode == GAME_MODE_PLAY) {
        game_update_play(state, pad1, pad2, pressed1, pressed2);
    } else if (state->mode == GAME_MODE_PAUSE) {
        if ((pressed1 & GAME_INPUT_START) != 0u ||
            (state->p2_joined != 0u &&
             (pressed2 & GAME_INPUT_START) != 0u)) {
            state->mode = GAME_MODE_PLAY;
        }
    } else if (state->mode == GAME_MODE_WIN ||
               state->mode == GAME_MODE_GAMEOVER) {
        if ((pressed1 & GAME_INPUT_START) != 0u) {
            game_return_to_title(state);
        }
    } else {
        game_return_to_title(state);
    }

    state->previous_input[0] = pad1;
    state->previous_input[1] = pad2;
}
