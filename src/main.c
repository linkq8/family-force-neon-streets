#include <snes.h>
#include <string.h>

#include "game.h"
#include "strings.h"
#include "assets/dev/actors.inc"
#include "assets/dev/enemy_wave0.inc"
#include "assets/dev/enemy_wave1.inc"
#include "assets/dev/enemy_wave2.inc"
#include "assets/dev/select_bg.inc"
#include "assets/dev/street.inc"
#include "assets/dev/font.inc"
#include "audio/soundbank.h"

#define MAX_RENDER_ACTORS 5

#define ACTOR_BANK_BYTES 0x1000u
#define ENEMY_PACK_BYTES 0x2000u

/* VRAM addresses are words. OBJ graphics occupy physical bytes $0000-$7fff. */
#define VRAM_HERO_1 0x0000u
#define VRAM_HERO_2 0x0800u
#define VRAM_ENEMY_WAVE_0 0x1000u
#define VRAM_ENEMY_WAVE_1 0x2000u
#define VRAM_ENEMY_WAVE_2 0x3000u
#define VRAM_BG_TILES 0x4000u
#define VRAM_FONT_TILES 0x5000u
#define VRAM_TEXT_MAP 0x6000u
#define VRAM_BG_MAP 0x6800u

#define TEXT_ATTRIBUTE 0x24u

enum VideoScene {
    VIDEO_SCENE_TITLE = 0,
    VIDEO_SCENE_SELECT = 1,
    VIDEO_SCENE_GAME = 2
};

enum ActorPose {
    ACTOR_POSE_IDLE = 0,
    ACTOR_POSE_WALK = 1,
    ACTOR_POSE_ATTACK = 2,
    ACTOR_POSE_HURT = 3
};

enum SoundEffectId {
    SFX_CONFIRM = 0,
    SFX_PUNCH = 1,
    SFX_JUMP = 2,
    SFX_DAMAGE = 3,
    SFX_PICKUP = 4,
    SFX_VICTORY = 5,
    SFX_COUNT = 6
};

typedef struct RenderItem {
    GameU8 kind;
    GameU8 index;
    GameS16 y;
} RenderItem;

static GameState game;
static GameU8 pal_accumulator;
static GameU8 video_scene;
static GameU8 displayed_wave;
static GameU8 pending_wave;
static GameU8 screen_enable_pending;

static GameU8 ui_mode;
static GameU8 ui_select_p1;
static GameU8 ui_select_p2;
static GameU8 ui_p2_joined;
static GameU8 ui_health[GAME_MAX_PLAYERS];
static GameU8 ui_player_count;
static GameU8 ui_wave;
static GameU16 ui_score;

static GameU16 audio_previous_pad1;
static GameU16 audio_previous_pad2;
static GameU8 audio_previous_mode;
static GameU8 audio_previous_wave;
static GameU8 audio_previous_health[GAME_MAX_PLAYERS];
static brrsamples audio_sfx[SFX_COUNT];

extern char SOUNDBANK__;
extern char sfx_punch, sfx_punch_end;
extern char sfx_jump, sfx_jump_end;
extern char sfx_damage, sfx_damage_end;
extern char sfx_pickup, sfx_pickup_end;
extern char sfx_confirm, sfx_confirm_end;
extern char sfx_victory, sfx_victory_end;

/* Each row is idle, walk, attack, hurt. Values index an eight-pose pack. */
static const GameU8 ENEMY_POSES[GAME_WAVE_COUNT][4][4] = {
    {
        { 0u, 1u, 2u, 3u },
        { 0u, 1u, 2u, 3u },
        { 0u, 1u, 2u, 3u },
        { 0u, 1u, 2u, 3u }
    },
    {
        { 3u, 3u, 4u, 3u },
        { 0u, 1u, 2u, 0u },
        { 5u, 6u, 7u, 5u },
        { 5u, 6u, 7u, 5u }
    },
    {
        { 0u, 0u, 1u, 0u },
        { 6u, 6u, 7u, 6u },
        { 2u, 3u, 4u, 5u },
        { 2u, 3u, 4u, 5u }
    }
};

static void clear_text_layer(void)
{
    memset(scr_txt_font_map, 0, 0x800u);
    scr_txt_dirty = 1u;
}

static void ui_clear_row(GameU8 row)
{
    if (row >= 32u) {
        return;
    }
    memset(&scr_txt_font_map[(GameU16)row * 64u], 0, 64u);
    scr_txt_dirty = 1u;
}

static void ui_put_char(GameU8 column, GameU8 row, char value)
{
    GameU16 offset;
    GameU8 glyph;

    if (column >= 32u || row >= 32u) {
        return;
    }
    glyph = (GameU8)value;
    if (glyph < 32u || glyph >= 128u) {
        glyph = 32u;
    }
    offset = (GameU16)(((GameU16)row * 32u + column) * 2u);
    scr_txt_font_map[offset] = (GameU8)(glyph - 32u);
    scr_txt_font_map[offset + 1u] = TEXT_ATTRIBUTE;
    scr_txt_dirty = 1u;
}

static void ui_write(GameU8 column, GameU8 row, const char *text)
{
    while (*text != '\0' && column < 32u) {
        ui_put_char(column, row, *text);
        column = (GameU8)(column + 1u);
        text++;
    }
}

static void ui_write_u8_3(GameU8 column, GameU8 row, GameU8 value)
{
    ui_put_char(column, row, (char)('0' + (value / 100u)));
    ui_put_char((GameU8)(column + 1u), row,
                (char)('0' + ((value / 10u) % 10u)));
    ui_put_char((GameU8)(column + 2u), row,
                (char)('0' + (value % 10u)));
}

static void ui_write_u16_5(GameU8 column, GameU8 row, GameU16 value)
{
    ui_put_char(column, row, (char)('0' + ((value / 10000u) % 10u)));
    ui_put_char((GameU8)(column + 1u), row,
                (char)('0' + ((value / 1000u) % 10u)));
    ui_put_char((GameU8)(column + 2u), row,
                (char)('0' + ((value / 100u) % 10u)));
    ui_put_char((GameU8)(column + 3u), row,
                (char)('0' + ((value / 10u) % 10u)));
    ui_put_char((GameU8)(column + 4u), row,
                (char)('0' + (value % 10u)));
}

static void invalidate_ui_cache(void)
{
    ui_select_p1 = 0xffu;
    ui_select_p2 = 0xffu;
    ui_p2_joined = 0xffu;
    ui_health[0] = 0xffu;
    ui_health[1] = 0xffu;
    ui_player_count = 0xffu;
    ui_wave = 0xffu;
    ui_score = 0xffffu;
}

static GameU8 player_pose(const GamePlayer *player)
{
    if (player->action == GAME_PLAYER_WALK) {
        return ((game.tick >> 2) & 1u) != 0u ?
               ACTOR_POSE_WALK : ACTOR_POSE_IDLE;
    }
    if (player->action == GAME_PLAYER_LIGHT ||
        player->action == GAME_PLAYER_HEAVY ||
        player->action == GAME_PLAYER_AERIAL ||
        player->action == GAME_PLAYER_SPECIAL ||
        player->action == GAME_PLAYER_CHEER) {
        return ACTOR_POSE_ATTACK;
    }
    if (player->action == GAME_PLAYER_HURT ||
        player->action == GAME_PLAYER_DOWN) {
        return ACTOR_POSE_HURT;
    }
    return ACTOR_POSE_IDLE;
}

static GameU8 enemy_pose_state(const GameEnemy *enemy)
{
    if (enemy->state == GAME_ENEMY_CHASE) {
        return ((game.tick >> 2) & 1u) != 0u ?
               ACTOR_POSE_WALK : ACTOR_POSE_IDLE;
    }
    if (enemy->state == GAME_ENEMY_WINDUP ||
        enemy->state == GAME_ENEMY_ATTACK) {
        return ACTOR_POSE_ATTACK;
    }
    if (enemy->state == GAME_ENEMY_HURT ||
        enemy->state == GAME_ENEMY_DEFEATED) {
        return ACTOR_POSE_HURT;
    }
    return ACTOR_POSE_IDLE;
}

static GameU8 enemy_pack_pose(GameU8 enemy_index, const GameEnemy *enemy)
{
    GameU8 wave;
    GameU8 type;
    GameU8 state;
    GameU8 pose;

    wave = game.wave < GAME_WAVE_COUNT ? game.wave :
           (GameU8)(GAME_WAVE_COUNT - 1u);
    type = enemy->type < 4u ? enemy->type : 0u;
    state = enemy_pose_state(enemy);
    pose = ENEMY_POSES[wave][type][state];
    if (wave == 0u && enemy_index == 1u && pose < 2u) {
        pose = (GameU8)(pose + 4u);
    }
    return pose;
}

static void sort_render_items(RenderItem *items, GameU8 count)
{
    GameU8 i;
    GameU8 j;
    RenderItem key;

    for (i = 1u; i < count; i++) {
        key = items[i];
        j = i;
        while (j > 0u && items[j - 1u].y < key.y) {
            items[j] = items[j - 1u];
            j--;
        }
        items[j] = key;
    }
}

static void draw_actor(GameU8 rank, const RenderItem *item)
{
    GameS16 screen_x;
    GameS16 top_y;
    GameU16 top_tile;
    GameU16 bottom_tile;
    GameU16 oam_id;
    GameU8 facing;

    if (item->kind == 0u) {
        const GamePlayer *player;
        GameU8 pose;

        player = &game.players[item->index];
        pose = player_pose(player);
        screen_x = (GameS16)(player->x - game.camera_x - 16);
        top_y = (GameS16)(player->y - player->z - 64);
        top_tile = (GameU16)(((GameU16)item->index << 7) |
                            ((GameU16)pose << 2));
        facing = player->facing;
    } else {
        const GameEnemy *enemy;
        GameU8 pose;

        enemy = &game.enemies[item->index];
        pose = enemy_pack_pose(item->index, enemy);
        screen_x = (GameS16)(enemy->x - game.camera_x - 16);
        top_y = (GameS16)(enemy->y - 64);
        top_tile = (GameU16)(0x100u |
                   ((GameU16)(pose >> 2) << 7) |
                   ((GameU16)(pose & 3u) << 2));
        facing = enemy->facing;
    }

    bottom_tile = (GameU16)(top_tile + 0x40u);
    oam_id = (GameU16)rank * 8u;
    oamSet(oam_id, (GameU16)screen_x, (GameU16)top_y, 2u,
           facing == GAME_FACE_LEFT, 0u, top_tile, 0u);
    oamSetEx(oam_id, OBJ_LARGE, OBJ_SHOW);
    oamSet((GameU16)(oam_id + 4u), (GameU16)screen_x,
           (GameU16)(top_y + 32), 2u,
           facing == GAME_FACE_LEFT, 0u, bottom_tile, 0u);
    oamSetEx((GameU16)(oam_id + 4u), OBJ_LARGE, OBJ_SHOW);
}

static void draw_actors(void)
{
    RenderItem items[MAX_RENDER_ACTORS];
    GameU8 count;
    GameU8 i;

    count = 0u;
    for (i = 0u; i < GAME_MAX_PLAYERS; i++) {
        GameS16 screen_x;

        screen_x = (GameS16)(game.players[i].x - game.camera_x);
        if (game.players[i].active != 0u &&
            screen_x >= -32 && screen_x <= 288 &&
            count < MAX_RENDER_ACTORS) {
            items[count].kind = 0u;
            items[count].index = i;
            items[count].y = game.players[i].y;
            count++;
        }
    }
    for (i = 0u; i < GAME_MAX_ENEMIES; i++) {
        GameS16 screen_x;

        screen_x = (GameS16)(game.enemies[i].x - game.camera_x);
        if (game.enemies[i].active != 0u &&
            screen_x >= -32 && screen_x <= 288 &&
            count < MAX_RENDER_ACTORS) {
            items[count].kind = 1u;
            items[count].index = i;
            items[count].y = game.enemies[i].y;
            count++;
        }
    }

    sort_render_items(items, count);
    for (i = 0u; i < count; i++) {
        draw_actor(i, &items[i]);
    }
    for (i = count; i < MAX_RENDER_ACTORS; i++) {
        oamSetVisible((GameU16)i * 8u, OBJ_HIDE);
        oamSetVisible((GameU16)i * 8u + 4u, OBJ_HIDE);
    }
}

static void draw_title_ui(void)
{
    ui_write(10u, 6u, STR_TITLE_LINE_1);
    ui_write(9u, 8u, STR_TITLE_LINE_2);
    ui_write(2u, 12u, STR_TITLE_TAGLINE);
    ui_write(10u, 17u, STR_TITLE_PROMPT);
    ui_write(1u, 23u, STR_CONTROLS_1);
    ui_write(1u, 24u, STR_CONTROLS_2);
}

static void draw_select_ui(void)
{
    GameU8 p1_column;
    GameU8 p2_column;

    if (ui_select_p1 == game.selected_character[0] &&
        ui_select_p2 == game.selected_character[1] &&
        ui_p2_joined == game.p2_joined) {
        return;
    }

    ui_clear_row(4u);
    ui_clear_row(19u);
    p1_column = (GameU8)(game.selected_character[0] * 8u + 1u);
    ui_write(p1_column, 4u, "P1");
    if (game.p2_joined != 0u) {
        p2_column = (GameU8)(game.selected_character[1] * 8u + 5u);
        ui_write(p2_column, 19u, "P2");
    }
    ui_select_p1 = game.selected_character[0];
    ui_select_p2 = game.selected_character[1];
    ui_p2_joined = game.p2_joined;
}

static void draw_hud(void)
{
    GameU16 score;

    if (ui_health[0] != game.players[0].health ||
        ui_player_count != game.player_count) {
        ui_clear_row(0u);
        ui_write(0u, 0u, "P1 ");
        ui_write(3u, 0u, GAME_CHARACTER_NAMES[game.players[0].character]);
        ui_write(14u, 0u, "HP:");
        ui_write_u8_3(17u, 0u, game.players[0].health);
        ui_health[0] = game.players[0].health;
    }

    if (ui_health[1] != game.players[1].health ||
        ui_player_count != game.player_count) {
        ui_clear_row(1u);
        if (game.players[1].active != 0u) {
            ui_write(0u, 1u, "P2 ");
            ui_write(3u, 1u,
                     GAME_CHARACTER_NAMES[game.players[1].character]);
            ui_write(14u, 1u, "HP:");
            ui_write_u8_3(17u, 1u, game.players[1].health);
        }
        ui_health[1] = game.players[1].health;
    }

    score = (GameU16)(game.players[0].score & 0xfffful);
    if (ui_score != score || ui_wave != game.wave) {
        ui_clear_row(2u);
        ui_write(0u, 2u, "SCORE:");
        ui_write_u16_5(6u, 2u, score);
        ui_write(13u, 2u, "AREA:");
        ui_put_char(18u, 2u, (char)('1' + game.wave));
        ui_write(19u, 2u, "/3");
        if (game.wave == 2u && game.wave_active != 0u) {
            ui_write(22u, 2u, STR_HUD_BOSS);
        }
        ui_score = score;
        ui_wave = game.wave;
    }
    ui_player_count = game.player_count;
}

static void draw_pause_ui(void)
{
    ui_write(12u, 11u, STR_PAUSED);
    ui_write(8u, 13u, STR_PAUSE_PROMPT);
}

static void draw_ending_ui(GameU8 won)
{
    if (won != 0u) {
        ui_write(8u, 8u, STR_WIN_TITLE);
        ui_write(1u, 12u, STR_WIN_MESSAGE);
    } else {
        ui_write(11u, 9u, STR_GAMEOVER_TITLE);
    }
    ui_write(6u, 17u, STR_RESTART_PROMPT);
}

static void update_ui(void)
{
    if (ui_mode != game.mode) {
        clear_text_layer();
        invalidate_ui_cache();
        ui_mode = game.mode;
        if (game.mode == GAME_MODE_TITLE) {
            draw_title_ui();
        } else if (game.mode == GAME_MODE_SELECT) {
            draw_select_ui();
        } else if (game.mode == GAME_MODE_PLAY) {
            draw_hud();
        } else if (game.mode == GAME_MODE_PAUSE) {
            draw_hud();
            draw_pause_ui();
        } else if (game.mode == GAME_MODE_WIN) {
            draw_ending_ui(1u);
        } else if (game.mode == GAME_MODE_GAMEOVER) {
            draw_ending_ui(0u);
        }
        return;
    }

    if (game.mode == GAME_MODE_SELECT) {
        draw_select_ui();
    } else if (game.mode == GAME_MODE_PLAY ||
               game.mode == GAME_MODE_PAUSE) {
        draw_hud();
    }
}

static void load_street_background(void)
{
    bgInitTileSet(0, &street_til, &street_pal, 0,
                  (&street_tilend - &street_til),
                  (&street_palend - &street_pal),
                  BG_16COLORS, VRAM_BG_TILES);
    bgInitMapSet(0, (u8 *)&street_map,
                 (u16)((&street_mapend - &street_map) * 2),
                 SC_64x32, VRAM_BG_MAP);
}

static void load_select_background(void)
{
    bgInitTileSet(0, &select_bg_til, &select_bg_pal, 0,
                  (&select_bg_tilend - &select_bg_til),
                  (&select_bg_palend - &select_bg_pal),
                  BG_16COLORS, VRAM_BG_TILES);
    bgInitMapSet(0, (u8 *)&select_bg_map,
                 (u16)((&select_bg_mapend - &select_bg_map) * 2),
                 SC_32x32, VRAM_BG_MAP);
}

static void load_selected_heroes(void)
{
    u8 *hero_source;

    hero_source = (u8 *)(&actors_til +
                  ((GameU16)game.selected_character[0] << 12));
    dmaCopyVram(hero_source, VRAM_HERO_1, ACTOR_BANK_BYTES);
    hero_source = (u8 *)(&actors_til +
                  ((GameU16)game.selected_character[1] << 12));
    dmaCopyVram(hero_source, VRAM_HERO_2, ACTOR_BANK_BYTES);
}

static void set_enemy_wave_page(GameU8 wave)
{
    if (wave >= GAME_WAVE_COUNT) {
        return;
    }
    REG_OBSEL = (u8)(OBJ_SIZE16_L32 | (wave << 3));
    displayed_wave = wave;
}

static void enter_video_scene(GameU8 scene)
{
    setScreenOff();
    pending_wave = 0xffu;
    oamClear(0u, 0u);
    bgSetScroll(0, 0, 0);
    bgSetScroll(1, 0, 0);

    if (scene == VIDEO_SCENE_SELECT) {
        load_select_background();
    } else {
        load_street_background();
        if (scene == VIDEO_SCENE_GAME) {
            load_selected_heroes();
            oamInitGfxAttr(0x0000u, OBJ_SIZE16_L32);
            set_enemy_wave_page(game.wave);
        }
    }
    video_scene = scene;
    screen_enable_pending = 1u;
}

static void update_video_scene(void)
{
    GameU8 desired_scene;

    if (game.mode == GAME_MODE_SELECT) {
        desired_scene = VIDEO_SCENE_SELECT;
    } else if (game.mode == GAME_MODE_TITLE) {
        desired_scene = VIDEO_SCENE_TITLE;
    } else {
        desired_scene = VIDEO_SCENE_GAME;
    }

    if (video_scene != desired_scene) {
        enter_video_scene(desired_scene);
    }
    if (desired_scene == VIDEO_SCENE_GAME &&
        game.wave < GAME_WAVE_COUNT && displayed_wave != game.wave) {
        pending_wave = game.wave;
    }
}

static void init_audio(void)
{
    spcBoot();
    spcSetBank(&SOUNDBANK__);
    spcAllocateSoundRegion(16);
    spcLoad(MOD_STAGE_LOOP);

    spcSetSoundDataEntry(15, 8, 4,
                         &sfx_confirm_end - &sfx_confirm,
                         &sfx_confirm, &audio_sfx[SFX_CONFIRM]);
    spcSetSoundDataEntry(15, 8, 4,
                         &sfx_punch_end - &sfx_punch,
                         &sfx_punch, &audio_sfx[SFX_PUNCH]);
    spcSetSoundDataEntry(15, 8, 4,
                         &sfx_jump_end - &sfx_jump,
                         &sfx_jump, &audio_sfx[SFX_JUMP]);
    spcSetSoundDataEntry(15, 8, 4,
                         &sfx_damage_end - &sfx_damage,
                         &sfx_damage, &audio_sfx[SFX_DAMAGE]);
    spcSetSoundDataEntry(15, 8, 4,
                         &sfx_pickup_end - &sfx_pickup,
                         &sfx_pickup, &audio_sfx[SFX_PICKUP]);
    spcSetSoundDataEntry(15, 8, 4,
                         &sfx_victory_end - &sfx_victory,
                         &sfx_victory, &audio_sfx[SFX_VICTORY]);
    spcSetSoundTableEntry(&audio_sfx[0]);

    spcPlay(0);
    spcSetModuleVolume(80);
    audio_previous_pad1 = 0u;
    audio_previous_pad2 = 0u;
    audio_previous_mode = game.mode;
    audio_previous_wave = game.wave;
    audio_previous_health[0] = game.players[0].health;
    audio_previous_health[1] = game.players[1].health;
}

static void update_audio(GameU16 pad1, GameU16 pad2)
{
    GameU16 pressed1;
    GameU16 pressed2;
    GameU8 i;

    pressed1 = pad1 & (GameU16)(~audio_previous_pad1);
    pressed2 = pad2 & (GameU16)(~audio_previous_pad2);

    if (game.mode != audio_previous_mode) {
        if (game.mode == GAME_MODE_SELECT || game.mode == GAME_MODE_PLAY) {
            spcPlaySound(SFX_CONFIRM);
        } else if (game.mode == GAME_MODE_WIN) {
            spcPlaySound(SFX_VICTORY);
        }
    }

    if (game.mode == GAME_MODE_PLAY) {
        if (((pressed1 | pressed2) &
             (GAME_INPUT_Y | GAME_INPUT_X | GAME_INPUT_A)) != 0u) {
            spcPlaySound(SFX_PUNCH);
        } else if (((pressed1 | pressed2) & GAME_INPUT_B) != 0u) {
            spcPlaySound(SFX_JUMP);
        }

        for (i = 0u; i < GAME_MAX_PLAYERS; i++) {
            if (game.players[i].active != 0u &&
                game.players[i].health < audio_previous_health[i]) {
                spcPlaySound(SFX_DAMAGE);
            }
        }
        if (game.wave > audio_previous_wave &&
            game.wave < GAME_WAVE_COUNT) {
            spcPlaySound(SFX_PICKUP);
        }
    }

    audio_previous_pad1 = pad1;
    audio_previous_pad2 = pad2;
    audio_previous_mode = game.mode;
    audio_previous_wave = game.wave;
    audio_previous_health[0] = game.players[0].health;
    audio_previous_health[1] = game.players[1].health;
}

static void init_video(void)
{
    setScreenOff();
    consoleSetTextMapPtr(VRAM_TEXT_MAP);
    consoleSetTextGfxPtr(VRAM_FONT_TILES);
    consoleSetTextOffset(0u);
    consoleInitText(1u, (&font_palend - &font_pal),
                    &font_til, &font_pal);
    bgSetGfxPtr(1, VRAM_FONT_TILES);
    bgSetMapPtr(1, VRAM_TEXT_MAP, SC_32x32);

    dmaCopyVram(&enemy_wave0_til, VRAM_ENEMY_WAVE_0,
                ENEMY_PACK_BYTES);
    dmaCopyVram(&enemy_wave1_til, VRAM_ENEMY_WAVE_1,
                ENEMY_PACK_BYTES);
    dmaCopyVram(&enemy_wave2_til, VRAM_ENEMY_WAVE_2,
                ENEMY_PACK_BYTES);
    setPalette(&actors_pal, 128u, 16u * 2u);

    oamInitGfxAttr(0x0000u, OBJ_SIZE16_L32);
    oamClear(0u, 0u);
    setMode(BG_MODE1, 0u);
    bgSetDisable(2u);
    video_scene = 0xffu;
    displayed_wave = 0xffu;
    pending_wave = 0xffu;
    screen_enable_pending = 0u;
    enter_video_scene(VIDEO_SCENE_TITLE);
}

int main(void)
{
    GameU16 pad1;
    GameU16 pad2;
    GameS16 scroll_x;

    game_reset(&game, 0x4646u);
    pal_accumulator = 0u;
    ui_mode = 0xffu;
    invalidate_ui_cache();
    init_audio();
    init_video();
    clear_text_layer();

    while (1) {
        pad1 = padsCurrent(0u);
        pad2 = padsCurrent(1u);

        game_update(&game, pad1, pad2);
        if (snes_50hz != 0u) {
            pal_accumulator = (GameU8)(pal_accumulator + 10u);
            if (pal_accumulator >= 50u) {
                pal_accumulator = (GameU8)(pal_accumulator - 50u);
                game_update(&game, pad1, pad2);
            }
        }

        update_audio(pad1, pad2);
        update_video_scene();
        update_ui();

        if (video_scene == VIDEO_SCENE_GAME) {
            scroll_x = game.camera_x;
            if (game.screen_shake != 0u) {
                if ((game.screen_shake & 1u) != 0u) {
                    scroll_x = (GameS16)(scroll_x + 2);
                } else {
                    scroll_x = (GameS16)(scroll_x - 2);
                }
            }
            bgSetScroll(0, scroll_x, 0);
            draw_actors();
        }

        spcProcess();
        WaitForVBlank();
        if (pending_wave < GAME_WAVE_COUNT) {
            set_enemy_wave_page(pending_wave);
            pending_wave = 0xffu;
        }
        if (screen_enable_pending != 0u) {
            setScreenOn();
            screen_enable_pending = 0u;
        }
    }

    return 0;
}
