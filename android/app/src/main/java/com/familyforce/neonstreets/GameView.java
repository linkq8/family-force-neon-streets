package com.familyforce.neonstreets;

import android.animation.ValueAnimator;
import android.app.ActivityManager;
import android.content.Context;
import android.content.res.Configuration;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.BitmapRegionDecoder;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.PorterDuff;
import android.graphics.PorterDuffColorFilter;
import android.graphics.Rect;
import android.graphics.RectF;
import android.graphics.Shader;
import android.os.SystemClock;
import android.view.HapticFeedbackConstants;
import android.view.InputDevice;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.util.Log;

import java.io.IOException;
import java.io.InputStream;
import java.util.Arrays;
import java.util.Locale;
import java.util.Random;

/*
 * MENU DIRECTION CONTRACT — seed 5eb5140e
 * THESIS: a joyful midnight transit mural turns every game choice into a clear route; it refuses a plain stack of generic cards.
 * OWN-WORLD: enamel navy, porcelain labels, four hero-line colors, bright station rings, disciplined 45/90-degree routes.
 * STORY: choose party size, trace the route, assign each player and companion, then depart only when required riders are ready.
 * FIRST VIEWPORT: brand station above four route rows; the active route burns brightest and its destination board owns the right half.
 * FORM: fifth grounded structure, a neon metropolitan route board adapted to an arcade cabinet.
 * FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, and DESIGN.md
 */
public final class GameView extends SurfaceView implements SurfaceHolder.Callback, Runnable {
    private static final String TAG = "FamilyForceGame";
    private static final int W = 640;
    private static final int H = 360;
    private static final float WORLD_END = 6150f;

    private static final int TITLE = 0;
    private static final int MENU = 1;
    private static final int SELECT = 2;
    private static final int INTRO = 3;
    private static final int PLAY = 4;
    private static final int PAUSE = 5;
    private static final int SETTINGS = 6;
    private static final int RESULTS = 7;
    private static final int GAME_OVER = 8;
    private static final int GALLERY = 9;
    private static final int HERO_SLOT_COUNT = 4;

    private static final int ITEM_FOOD = 0;
    private static final int ITEM_ENERGY = 1;
    private static final int ITEM_TOKEN = 2;
    private static final int ITEM_BAT = 3;

    private static final int ACTION_NONE = 0;
    private static final int ACTION_PUNCH = 1;
    private static final int ACTION_KICK = 2;
    private static final int ACTION_HEAVY_PUNCH = 3;
    private static final int ACTION_HEAVY_KICK = 4;
    private static final int ACTION_JUMP = 5;
    private static final int ACTION_SPECIAL = 6;
    private static final int ACTION_LINK = 7;
    private static final int ACTION_AIR_ATTACK = 8;
    private static final int ACTION_WEAPON = 9;
    private static final int ACTION_THROW = 10;
    private static final MoveSpec[] MOVE_SPECS = {
            new MoveSpec("NONE", 8, 0, 0f, 0f, 0f, 0, 0, false),
            new MoveSpec("PUNCH", 18, 3, 54f, 28f, 1.00f, 3, 3, false),
            new MoveSpec("KICK", 16, 4, 70f, 33f, 1.15f, 3, 4, false),
            new MoveSpec("HEAVY PUNCH", 12, 4, 76f, 30f, 1.75f, 4, 6, false),
            new MoveSpec("HEAVY KICK", 12, 5, 92f, 39f, 1.95f, 4, 7, true),
            new MoveSpec("JUMP", 14, 0, 0f, 0f, 0f, 0, 4, false),
            new MoveSpec("SPECIAL", 16, 4, 128f, 62f, 2.10f, 5, 10, true),
            new MoveSpec("LINK", 14, 4, 128f, 62f, 1.65f, 5, 10, true),
            new MoveSpec("AIR ATTACK", 18, 4, 70f, 33f, 1.30f, 3, 4, false),
            new MoveSpec("WEAPON", 12, 4, 96f, 31f, 1.00f, 4, 6, true),
            new MoveSpec("THROW", 12, 3, 72f, 30f, 0f, 3, 6, true)
    };

    private static final int HERO_IDLE = 0;
    private static final int HERO_WALK = 1;
    private static final int HERO_PUNCH = 2;
    private static final int HERO_KICK = 3;
    private static final int HERO_HEAVY_PUNCH = 4;
    private static final int HERO_HEAVY_KICK = 5;
    private static final int HERO_JUMP = 6;
    private static final int HERO_SPECIAL = 7;
    private static final int HERO_LINK = 8;
    private static final int HERO_HURT = 9;
    private static final int HERO_KNOCKDOWN = 10;
    private static final int HERO_ANIM_COLUMNS = 8;
    private static final int HERO_ANIM_ROWS = 11;
    private static final int HERO_ANIM_CELL_WIDTH = 192;
    private static final int HERO_ANIM_CELL_HEIGHT = 192;
    private static final int HERO_ANIM_ATLAS_WIDTH = HERO_ANIM_COLUMNS * HERO_ANIM_CELL_WIDTH;
    private static final int HERO_ANIM_ATLAS_HEIGHT = HERO_ANIM_ROWS * HERO_ANIM_CELL_HEIGHT;

    private static final int ENEMY_IDLE = 0;
    private static final int ENEMY_WALK = 1;
    private static final int ENEMY_ATTACK_1 = 2;
    private static final int ENEMY_ATTACK_2 = 3;
    private static final int ENEMY_HURT = 4;
    private static final int ENEMY_KNOCKDOWN = 5;
    private static final int ENEMY_ANIM_COLUMNS = 6;
    private static final int ENEMY_ANIM_ROWS = 6;
    private static final int ENEMY_ANIM_CELL_WIDTH = 160;
    private static final int ENEMY_ANIM_CELL_HEIGHT = 192;
    private static final int ENEMY_ANIM_ATLAS_WIDTH = ENEMY_ANIM_COLUMNS * ENEMY_ANIM_CELL_WIDTH;
    private static final int ENEMY_ANIM_ATLAS_HEIGHT = ENEMY_ANIM_ROWS * ENEMY_ANIM_CELL_HEIGHT;

    private static final int WEAPON_BAT = 0;
    private static final int WEAPON_PIPE = 1;
    private static final int WEAPON_MALLET = 2;
    private static final int WEAPON_SIGN = 3;
    private static final int WEAPON_CONE = 4;
    private static final int PROP_CRATE = 5;
    private static final int PROP_TRASH_CAN = 6;
    private static final int WORLD_OBJECT_COUNT = 24;
    private static final int CHECKPOINT_VERSION = 2;
    private static final float PICKUP_PROMPT_X = 70f;
    private static final float PICKUP_PROMPT_Y = 48f;
    private static final float PICKUP_AUTO_X = 42f;
    private static final float PICKUP_AUTO_Y = 40f;
    private static final long CONTROLLER_COMBO_STALE_MS = 45_000L;

    private static final int ENEMY_STATE_IDLE = 0;
    private static final int ENEMY_STATE_WALK = 1;
    private static final int ENEMY_STATE_ATTACK = 2;
    private static final int ENEMY_STATE_HURT = 3;
    private static final int ENEMY_STATE_KNOCKDOWN = 4;
    private static final String[] ENEMY_STATE_LABELS = {
            "IDLE", "WALK", "ATTACK", "HURT", "DOWN"
    };

    private static final int LAYOUT_COMPACT = 0;
    private static final int LAYOUT_CONTROL_DECK = 1;
    private static final int LAYOUT_SIDE_GUTTERS = 2;

    private static final float ESSA_HEIGHT_CM = 177f;
    private static final float ADAM_HEIGHT_CM = 108f;
    private static final float SHAIKHA_HEIGHT_CM = 108f;
    private static final float SULAIMAN_HEIGHT_CM = 124f;
    private static final float ESSA_RENDER_HEIGHT = 192f;
    private static final float ESSA_VISIBLE_ART_PX = 360f;
    private static final float ADAM_VISIBLE_ART_PX = 342f;
    private static final float SHAIKHA_VISIBLE_ART_PX = 360f;
    private static final float SULAIMAN_VISIBLE_ART_PX = 360f;
    // Slightly smaller for TV layouts so sprites fit with more scene context.
    private static final float CHARACTER_SCREEN_SCALE = 0.81f * 0.90f;
    private static final Rect HERO_ANIM_FULL_CELL =
            new Rect(0, 0, HERO_ANIM_CELL_WIDTH, HERO_ANIM_CELL_HEIGHT);
    /*
     * The generated masters have different transparent margins. These canvas
     * heights compensate for those bounds so the visible silhouettes match the
     * family's real standing-height ratios, including Adam's crouched master.
     */
    private static final float[] HERO_RENDER_HEIGHT = {
            ESSA_RENDER_HEIGHT * 0.90f,
            ESSA_RENDER_HEIGHT * (ADAM_HEIGHT_CM / ESSA_HEIGHT_CM)
                    * (ESSA_VISIBLE_ART_PX / ADAM_VISIBLE_ART_PX) * 0.90f,
            ESSA_RENDER_HEIGHT * (SHAIKHA_HEIGHT_CM / ESSA_HEIGHT_CM)
                    * (ESSA_VISIBLE_ART_PX / SHAIKHA_VISIBLE_ART_PX) * 0.90f,
            ESSA_RENDER_HEIGHT * (SULAIMAN_HEIGHT_CM / ESSA_HEIGHT_CM)
                    * (ESSA_VISIBLE_ART_PX / SULAIMAN_VISIBLE_ART_PX) * 0.90f
    };
    private static final float[] HERO_ANIM_RENDER_HEIGHT = {
            ESSA_RENDER_HEIGHT * 0.90f,
            ESSA_RENDER_HEIGHT * (ADAM_HEIGHT_CM / ESSA_HEIGHT_CM) * 0.90f,
            ESSA_RENDER_HEIGHT * (SHAIKHA_HEIGHT_CM / ESSA_HEIGHT_CM) * 0.90f,
            ESSA_RENDER_HEIGHT * (SULAIMAN_HEIGHT_CM / ESSA_HEIGHT_CM) * 0.90f
    };

    private static final int[] HERO_COLORS = {
            Color.rgb(255, 76, 74), Color.rgb(83, 220, 92),
            Color.rgb(255, 110, 190), Color.rgb(69, 142, 255)
    };
    private static final String[] HERO_NAMES = {"ESSA", "ADAM", "SHAIKHA", "SULAIMAN"};
    private static final String[] HERO_ROLES = {"ARMORED TITAN", "GREEN POWER", "ICE PRINCESS", "SKY HERO"};
    private static final String[] HERO_MOVES = {"CORE BURST", "GREEN SMASH", "PINK BLIZZARD", "SKY DASH"};
    private static final float[] HERO_SPEED = {2.58f, 2.35f, 2.78f, 3.08f};
    private static final float[] HERO_POWER = {1.42f, 1.30f, 0.90f, 1.02f};
    private static final int[] HERO_HP = {160, 138, 106, 114};
    private static final float MENU_NAV_AXIS_THRESHOLD = 0.33f;
    private static final long MENU_NAV_REPEAT_DELAY_MS = 150L;
    private static final long MENU_NAV_AXIS_REARM_MS = 80L;
    private static final String[] ACTION_BUTTON_LABELS = {
            "PUNCH", "KICK", "H-P", "H-K", "JUMP", "STAR", "LINK", "THROW"
    };
    private static final int[] ACTION_BUTTON_COLORS = {
            Color.rgb(255, 83, 92), Color.rgb(255, 136, 72),
            Color.rgb(255, 197, 70), Color.rgb(234, 105, 196),
            Color.rgb(75, 220, 230), Color.rgb(181, 104, 255),
            Color.rgb(217, 255, 85), Color.rgb(92, 174, 255)
    };
    private static final float[] ZONE_TRIGGERS = {
            430f, 1080f, 1730f, 2380f, 2980f, 3560f, 4180f, 4820f, 5480f
    };
    private static final float[] STAGE_SIGN_X = {
            510f, 1015f, 1665f, 2150f, 2760f, 3300f, 3650f, 4260f, 4900f, 5560f
    };
    private static final String[] AREA_NAMES = {
            "MARKET WALK", "POCKET PARK", "SERVICE ALLEY", "ROOFTOP RUN",
            "NEON DEPOT", "TUNNEL RUSH", "HARBOR YARD", "SCRAP FREEWAY",
            "JUNK PALACE", "FINAL DISTRICT"
    };
    private static final String[] AREA_PROGRESS = {
            "AREA 1/9", "AREA 2/9", "AREA 3/9", "AREA 4/9", "AREA 5/9",
            "AREA 6/9", "AREA 7/9", "AREA 8/9", "AREA 9/9"
    };
    private static final String[] ENCOUNTER_NAMES = {
            "ENCOUNTER 1", "ENCOUNTER 2", "ENCOUNTER 3", "ENCOUNTER 4", "ENCOUNTER 5",
            "ENCOUNTER 6", "ENCOUNTER 7", "ENCOUNTER 8", "ENCOUNTER 9"
    };
    private static final int[] MAP_ROUTE_COLORS = {
            HERO_COLORS[0], Color.rgb(255, 199, 72), Color.rgb(217, 255, 85)
    };
    private static final int[] MENU_ROUTE_COLORS = {
            Color.rgb(217, 255, 85), Color.rgb(255, 83, 92),
            Color.rgb(83, 144, 255), Color.rgb(63, 221, 172),
            Color.rgb(255, 192, 65)
    };
    private static final float[] MAP_ROUTE_X = {382f, 470f, 520f, 577f};
    private static final float[] MAP_ROUTE_Y = {154f, 154f, 204f, 204f};

    private final SurfaceHolder holder;
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG | Paint.FILTER_BITMAP_FLAG);
    private final Paint pixelPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    /*
     * Character art is authored at a compact pixel resolution but is displayed
     * on high-density phones and Fold screens.  Nearest-neighbour magnification
     * turns every authored 2px cluster into a distracting 5px+ block.  Keep the
     * retro palette and hard alpha, but use a dedicated filtered paint for hero
     * bodies so eyes, hair and armor details survive the final device scale.
     */
    private final Paint heroPaint = new Paint(Paint.ANTI_ALIAS_FLAG
            | Paint.FILTER_BITMAP_FLAG | Paint.DITHER_FLAG);
    private final Paint portraitPaint = new Paint(Paint.FILTER_BITMAP_FLAG | Paint.DITHER_FLAG);
    private final Rect source = new Rect();
    private final RectF dest = new RectF();
    private final Path path = new Path();
    private final LinearGradient backdropGradient = new LinearGradient(0, 0, 0, H,
            Color.rgb(18, 15, 62), Color.rgb(5, 30, 45), Shader.TileMode.CLAMP);
    private LinearGradient viewportGradient = new LinearGradient(0, 0, 0, H,
            Color.rgb(19, 14, 61), Color.rgb(4, 28, 42), Shader.TileMode.CLAMP);
    private final AudioController audio;
    private final SharedPreferences prefs;
    private final CustomerProfile customerProfile;
    private final Random random = new Random(0xF4A11L);

    private Bitmap background;
    private Bitmap stageBackground;
    private Bitmap actorAtlas;
    private Bitmap portraits;
    private Bitmap logo;
    private final Bitmap[] heroArt = new Bitmap[4];
    private final Bitmap[] heroHdArt = new Bitmap[4];
    private final Bitmap[] heroPortraits = new Bitmap[4];
    private final Bitmap[] enemyArt = new Bitmap[4];
    private final Bitmap[] itemArt = new Bitmap[4];
    private final Bitmap[] enemyAnimArt = new Bitmap[4];
    private final Bitmap[] weaponArt = new Bitmap[5];
    private final Bitmap[] propArt = new Bitmap[2];
    private Bitmap actionIcons;
    private Bitmap hitFxArt;
    private Bitmap specialFxArt;
    private Bitmap weaponTrailFxArt;
    private Bitmap breakFxArt;
    private Bitmap selectedHeroAnimArt;
    private Bitmap assistAnimArt;
    private final Rect[] selectedHeroAnimSources = new Rect[HERO_ANIM_ROWS * HERO_ANIM_COLUMNS];
    private final Rect[] assistAnimSources = new Rect[HERO_ANIM_COLUMNS];
    private int loadedHeroAnim = -1;
    private int loadedPlayer2Anim = -1;
    private boolean player2AnimSharesPlayerAnim = false;
    private int loadedAssistHero = -1;
    private final SpriteAnimator playerAnimator = new SpriteAnimator();
    private final SpriteAnimator assistAnimator = new SpriteAnimator();
    private final SpriteAnimator player2Animator = new SpriteAnimator();
    private final Rect[] player2AnimSources = new Rect[HERO_ANIM_ROWS * HERO_ANIM_COLUMNS];
    private Bitmap player2AnimArt;

    private volatile boolean running;
    private volatile boolean appActive = true;
    private Thread loopThread;
    private volatile int state = TITLE;
    private volatile boolean selectionTransitionInProgress;
    private int settingsReturn = MENU;
    private int selectedHero;
    private int selectedHero2 = 1;
    private int selectedCompanion1 = 1;
    private int selectedCompanion2;
    private int activeSelectionSlot;
    private boolean p1Ready;
    private boolean p2Ready;
    private int menuChoice;
    private int pauseOption;
    private int settingsOption;
    private int resultsOption;
    private int gameOverOption;
    private int menuHatX;
    private int menuHatY;
    private int menuHatXPlayer2;
    private int menuHatYPlayer2;
    private long lastMenuNavAt;
    private long lastMenuNavAtPlayer2;
    private long lastMenuActionAt = -150L;
    private int lastMenuActionCode = Integer.MIN_VALUE;
    private boolean trainingMode;
    private boolean musicEnabled;
    private boolean sfxEnabled;
    private boolean hapticsEnabled;
    private boolean shakeEnabled;
    private int difficulty;
    private float touchOpacity;
    private int bestScore;
    private boolean hasCheckpoint;
    private boolean debugOverlay;
    private long lastPrimaryControllerInputMs = -1L;
    private long lastSecondaryControllerInputMs = -1L;
    private int cachedScore = Integer.MIN_VALUE;
    private String cachedScoreText = "0000000";
    private int cachedWeaponType = Integer.MIN_VALUE;
    private int cachedWeaponDurability = Integer.MIN_VALUE;
    private String cachedWeaponText = "";
    private int cachedCombo = Integer.MIN_VALUE;
    private String cachedComboText = "";

    private float scale = 1f;
    private float offsetX;
    private float offsetY;
    private int viewportWidth = W;
    private int viewportHeight = H;
    private float virtualWidth = W;
    private float virtualHeight = H;
    private float sceneX;
    private float menuSceneY;
    private float gameSceneY;
    private int responsiveLayout = LAYOUT_COMPACT;
    private float stickCenterX = 90f;
    private float stickCenterY = 285f;
    private final float[] touchButtonX = {
            557f, 500f, 604f, 551f, 607f, 500f, 444f, 447f
    };
    private final float[] touchButtonY = {
            299f, 317f, 257f, 246f, 201f, 270f, 280f, 225f
    };
    private final float[] touchButtonRadius = {
            29f, 27f, 24f, 23f, 24f, 23f, 21f, 20f
    };
    private float controlScale = 1f;
    private float pauseCenterX = 616f;
    private float pauseCenterY = 88f;

    private boolean uiAnimationsEnabled = true;
    private int animatedState = -1;
    private int animatedHero = -1;
    private long stateEnteredAt;
    private long selectionChangedAt;

    private float playerX;
    private float playerY;
    private float playerZ;
    private float jumpVelocity;
    private float playerVx;
    private float playerVy;
    private float cameraX;
    private Enemy lastHitEnemy;
    private int lastHitEnemyTicks;
    private int p2AiCooldown;
    private boolean gamepadUiActive;
    private boolean twoPlayerMode = true;
    private int health;
    private int maxHealth;
    private int energy;
    private int linkMeter;
    private int score;
    private int combo;
    private int comboWindow;
    private int attackTimer;
    private int attackKind;
    private int attackSerial;
    private int bufferedAction;
    private int bufferedActionTicks;
    private int actionRecoveryTicks;
    private int punchChainStep;
    private int punchChainWindow;
    private boolean actionHitFired;
    private boolean actionObjectFired;
    private int invulnerable;
    private int hurtTimer;
    private int knockoutTimer;
    private int weaponDurability;
    private int heldWeaponType = -1;
    private boolean facingRight = true;
    private float player2X;
    private float player2Y;
    private float player2Z;
    private float player2JumpVelocity;
    private boolean p2FacingRight = true;
    private boolean p2Left, p2Right, p2Up, p2Down;
    private boolean p2LightQueued, p2KickQueued, p2HeavyQueued, p2HeavyKickQueued;
    private boolean p2JumpQueued, p2SpecialQueued, p2LinkQueued, p2ThrowQueued;
    private int p2AttackTimer;
    private int p2AttackKind;
    private int p2PunchChainStep;
    private int p2PunchChainWindow;
    private int p2Health;
    private int p2Energy = 55;
    private int p2Link = 60;
    private int p1ReviveProgress;
    private int p2ReviveProgress;
    private int p2Invulnerable;
    private int p2HurtTimer;
    private int primaryControllerId = -1;
    private int secondaryControllerId = -1;
    private int zone;
    private boolean zoneActive;
    private int zoneBanner;
    private int stageFrames;
    private int hitStop;
    private int shakeFrames;
    private int totalHits;
    private int damageTaken;
    private int teamComboBanner;
    private int teamComboCount;
    private boolean dashAttackActive;

    private volatile float moveX;
    private volatile float moveY;
    private volatile boolean keyLeft;
    private volatile boolean keyRight;
    private volatile boolean keyUp;
    private volatile boolean keyDown;
    private volatile boolean lightQueued;
    private volatile boolean kickQueued;
    private volatile boolean heavyQueued;
    private volatile boolean heavyKickQueued;
    private volatile boolean jumpQueued;
    private volatile boolean specialQueued;
    private volatile boolean assistQueued;
    private volatile boolean throwQueued;
    private volatile boolean dashHeld;
    private volatile boolean leftTriggerDown;
    private volatile boolean rightTriggerDown;
    private volatile boolean p2LeftTriggerDown;
    private volatile boolean p2RightTriggerDown;

    private int stickPointer = -1;
    private volatile float stickX;
    private volatile float stickY;
    private final int[] buttonPointers = {-1, -1, -1, -1, -1, -1, -1, -1};

    private final Enemy[] enemies = new Enemy[40];
    private final Item[] items = new Item[12];
    private final Particle[] particles = new Particle[72];
    private final WorldObject[] worldObjects = new WorldObject[WORLD_OBJECT_COUNT];
    private final SpriteEffect[] spriteEffects = new SpriteEffect[32];
    private final AssistActor assist = new AssistActor();
    private int particleCursor;
    private int effectCursor;
    private int worldObjectSerial;

    public GameView(Context context) {
        super(context);
        setFocusable(true);
        setFocusableInTouchMode(true);
        requestFocus();
        holder = getHolder();
        holder.addCallback(this);
        holder.setKeepScreenOn(true);
        audio = new AudioController(context);
        customerProfile = CustomerProfile.load(context);
        System.arraycopy(customerProfile.heroNames, 0, HERO_NAMES, 0, HERO_NAMES.length);
        prefs = context.getSharedPreferences("family_force_settings", Context.MODE_PRIVATE);
        musicEnabled = prefs.getBoolean("music", true);
        sfxEnabled = prefs.getBoolean("sfx", true);
        hapticsEnabled = prefs.getBoolean("haptics", true);
        shakeEnabled = prefs.getBoolean("shake", true);
        difficulty = prefs.getInt("difficulty", 1);
        touchOpacity = prefs.getFloat("touch_opacity", 0.72f);
        bestScore = prefs.getInt("best_score", 0);
        selectedHero = sanitizeHeroIndex(prefs.getInt("selected_hero_p1", 0));
        selectedHero2 = sanitizeHeroIndex(prefs.getInt("selected_hero_p2", 1));
        selectedCompanion1 = sanitizeCompanionIndex(
                prefs.getInt("selected_companion_p1", 1), selectedHero);
        selectedCompanion2 = sanitizeCompanionIndex(
                prefs.getInt("selected_companion_p2", 0), selectedHero2);
        hasCheckpoint = validateCheckpoint();
        menuChoice = hasCheckpoint ? 0 : 1;
        uiAnimationsEnabled = ValueAnimator.areAnimatorsEnabled();
        stateEnteredAt = selectionChangedAt = SystemClock.uptimeMillis();
        audio.setMusicEnabled(musicEnabled);
        audio.setSfxEnabled(sfxEnabled);
        loadAssets();
        for (int i = 0; i < enemies.length; i++) enemies[i] = new Enemy();
        for (int i = 0; i < items.length; i++) items[i] = new Item();
        for (int i = 0; i < particles.length; i++) particles[i] = new Particle();
        for (int i = 0; i < worldObjects.length; i++) worldObjects[i] = new WorldObject();
        for (int i = 0; i < spriteEffects.length; i++) spriteEffects[i] = new SpriteEffect();
        pixelPaint.setStrokeWidth(2f);
    }

    private int sanitizeHeroIndex(int hero) {
        if (HERO_SLOT_COUNT <= 0) return 0;
        int wrapped = hero % HERO_SLOT_COUNT;
        if (wrapped < 0) wrapped += HERO_SLOT_COUNT;
        return wrapped;
    }

    private int sanitizeCompanionIndex(int companion, int ownerHero) {
        companion = sanitizeHeroIndex(companion);
        ownerHero = sanitizeHeroIndex(ownerHero);
        return companion == ownerHero ? (ownerHero + 1) % HERO_SLOT_COUNT : companion;
    }

    private void cycleCompanion(int playerSlot, int direction) {
        if (playerSlot == 1) {
            do {
                selectedCompanion2 = sanitizeHeroIndex(selectedCompanion2 + direction);
            } while (selectedCompanion2 == safeHeroIndex(selectedHero2));
        } else {
            do {
                selectedCompanion1 = sanitizeHeroIndex(selectedCompanion1 + direction);
            } while (selectedCompanion1 == safeHeroIndex(selectedHero));
        }
        selectionChangedAt = SystemClock.uptimeMillis();
    }

    private int safeHeroIndex(int hero) {
        if (HERO_SLOT_COUNT <= 0) return 0;
        if (hero >= 0 && hero < HERO_SLOT_COUNT) return hero;
        return sanitizeHeroIndex(hero);
    }

    private String safeHeroName(int hero) {
        int index = safeHeroIndex(hero);
        return HERO_NAMES[index];
    }

    private String safeHeroRole(int hero) {
        int index = safeHeroIndex(hero);
        return HERO_ROLES[index];
    }

    private String safeHeroMove(int hero) {
        int index = safeHeroIndex(hero);
        return HERO_MOVES[index];
    }

    private int safeHeroColor(int hero) {
        return HERO_COLORS[safeHeroIndex(hero)];
    }

    private float safeHeroSpeed(int hero) {
        return HERO_SPEED[safeHeroIndex(hero)];
    }

    private float safeHeroPower(int hero) {
        return HERO_POWER[safeHeroIndex(hero)];
    }

    private int safeHeroMaxHealth(int hero) {
        return HERO_HP[safeHeroIndex(hero)];
    }

    private void syncHeroSlotsForSafety() {
        selectionTransitionInProgress = false;
        selectedHero = sanitizeHeroIndex(selectedHero);
        selectedHero2 = sanitizeHeroIndex(selectedHero2);
        activeSelectionSlot = activeSelectionSlot == 1 ? 1 : 0;
        if (menuChoice < 0) menuChoice = 0;
        else if (menuChoice > 4) menuChoice = 4;
        if (pauseOption < 0) pauseOption = 0;
        else if (pauseOption > 3) pauseOption = 3;
        if (settingsOption < 0) settingsOption = 0;
        else if (settingsOption > 5) settingsOption = 5;
        if (resultsOption < 0) resultsOption = 0;
        if (resultsOption > 1) resultsOption = 1;
        if (gameOverOption < 0) gameOverOption = 0;
        if (gameOverOption > 1) gameOverOption = 1;
    }

    private void syncControllerInputSlots() {
        if (hasCompanionController()) return;
        activeSelectionSlot = p1Ready ? (p2Ready ? 0 : 1) : 0;
        menuHatX = menuHatY = 0;
        menuHatXPlayer2 = menuHatYPlayer2 = 0;
    }

    private synchronized void enterState(int nextState) {
        if (state == nextState) return;
        int previousState = state;
        resetStaleCompanionController();
        try {
            state = nextState;
            syncHeroSlotsForSafety();
            if (nextState == MENU) {
                selectionTransitionInProgress = false;
                prepareEnemyAnimationsForZone(-1);
                pauseOption = 0;
                resultsOption = 0;
                gameOverOption = 0;
                settingsOption = 0;
                unloadPlayer2Animation(false);
                if (selectedHeroAnimArt != null && !selectedHeroAnimArt.isRecycled()) {
                    selectedHeroAnimArt.recycle();
                }
                selectedHeroAnimArt = null;
                playerAnimator.clear();
                loadedHeroAnim = -1;
            } else if (nextState == SELECT) {
                selectionTransitionInProgress = false;
                clearInputs();
                beginCharacterSelect();
            } else if (nextState == PAUSE) {
                pauseOption = 0;
            } else if (nextState == SETTINGS) {
                settingsOption = 0;
            } else if (nextState == RESULTS) {
                resultsOption = 0;
            } else if (nextState == GAME_OVER) {
                gameOverOption = 0;
            } else if (nextState == INTRO || nextState == PLAY) {
                selectionTransitionInProgress = false;
                selectionChangedAt = SystemClock.uptimeMillis();
            }
        } catch (Throwable runtimeError) {
            Log.e(TAG, "enterState failed " + previousState + " -> " + nextState, runtimeError);
            clearInputs();
            state = MENU;
            try {
                syncHeroSlotsForSafety();
                menuChoice = 0;
                pauseOption = 0;
                settingsOption = 0;
                resultsOption = 0;
                gameOverOption = 0;
            } catch (Throwable ignore) {
            }
        }
    }

    public void enterStateSafe() {
        try {
            clearInputs();
            enterState(MENU);
        } catch (Throwable runtimeError) {
            Log.e(TAG, "EnterStateSafe failed", runtimeError);
        }
    }

    private void clampHeroIndexesForPlay() {
        selectedHero = sanitizeHeroIndex(selectedHero);
        selectedHero2 = sanitizeHeroIndex(selectedHero2);
    }

    private static boolean isNavigationSource(int source) {
        return (source & InputDevice.SOURCE_DPAD) != 0
                || (source & InputDevice.SOURCE_GAMEPAD) != 0
                || (source & InputDevice.SOURCE_JOYSTICK) != 0;
    }

    private static boolean isGamepadSource(int source) {
        return (source & InputDevice.SOURCE_GAMEPAD) != 0
                || (source & InputDevice.SOURCE_JOYSTICK) != 0;
    }

    private static boolean isControllerSource(int source) {
        return isGamepadSource(source)
                || (source & InputDevice.SOURCE_KEYBOARD) != 0;
    }

    private static boolean isControllerDirectionalKey(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_DPAD_LEFT || keyCode == KeyEvent.KEYCODE_DPAD_RIGHT
                || keyCode == KeyEvent.KEYCODE_DPAD_UP || keyCode == KeyEvent.KEYCODE_DPAD_DOWN;
    }

    private static boolean isDpadNavigationKey(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_DPAD_LEFT || keyCode == KeyEvent.KEYCODE_DPAD_RIGHT
                || keyCode == KeyEvent.KEYCODE_DPAD_UP || keyCode == KeyEvent.KEYCODE_DPAD_DOWN
                || keyCode == KeyEvent.KEYCODE_DPAD_CENTER || keyCode == KeyEvent.KEYCODE_ENTER
                || keyCode == KeyEvent.KEYCODE_NUMPAD_ENTER;
    }

    private static boolean isMenuConfirmAlias(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_BUTTON_A || keyCode == KeyEvent.KEYCODE_BUTTON_1
                || keyCode == KeyEvent.KEYCODE_ENTER
                || keyCode == KeyEvent.KEYCODE_DPAD_CENTER || keyCode == KeyEvent.KEYCODE_BUTTON_16
                || keyCode == KeyEvent.KEYCODE_NUMPAD_ENTER || keyCode == KeyEvent.KEYCODE_SPACE
                || keyCode == KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE || keyCode == KeyEvent.KEYCODE_MEDIA_PLAY
                || keyCode == KeyEvent.KEYCODE_BUTTON_START || keyCode == KeyEvent.KEYCODE_BUTTON_15
                || keyCode == KeyEvent.KEYCODE_BUTTON_4
                || keyCode == KeyEvent.KEYCODE_MEDIA_NEXT || keyCode == KeyEvent.KEYCODE_MEDIA_PREVIOUS
                || keyCode == KeyEvent.KEYCODE_BUTTON_THUMBL || keyCode == KeyEvent.KEYCODE_BUTTON_THUMBR;
    }

    private static boolean isMenuCancelAlias(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_BUTTON_B || keyCode == KeyEvent.KEYCODE_BACK
                || keyCode == KeyEvent.KEYCODE_ESCAPE || keyCode == KeyEvent.KEYCODE_MENU
                || keyCode == KeyEvent.KEYCODE_BUTTON_SELECT || keyCode == KeyEvent.KEYCODE_BUTTON_5
                || keyCode == KeyEvent.KEYCODE_BUTTON_2 || keyCode == KeyEvent.KEYCODE_BUTTON_3
                || keyCode == KeyEvent.KEYCODE_BUTTON_6 || keyCode == KeyEvent.KEYCODE_BUTTON_7
                || keyCode == KeyEvent.KEYCODE_MEDIA_REWIND || keyCode == KeyEvent.KEYCODE_MEDIA_STOP
                || keyCode == KeyEvent.KEYCODE_BUTTON_MODE || keyCode == KeyEvent.KEYCODE_BUTTON_9;
    }

    private static boolean isMenuNavigationAlias(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_DPAD_UP || keyCode == KeyEvent.KEYCODE_DPAD_DOWN
                || keyCode == KeyEvent.KEYCODE_DPAD_LEFT || keyCode == KeyEvent.KEYCODE_DPAD_RIGHT
                || keyCode == KeyEvent.KEYCODE_W || keyCode == KeyEvent.KEYCODE_A
                || keyCode == KeyEvent.KEYCODE_S || keyCode == KeyEvent.KEYCODE_D
                || keyCode == KeyEvent.KEYCODE_CHANNEL_UP || keyCode == KeyEvent.KEYCODE_CHANNEL_DOWN
                || keyCode == KeyEvent.KEYCODE_NUMPAD_8 || keyCode == KeyEvent.KEYCODE_NUMPAD_2
                || keyCode == KeyEvent.KEYCODE_NUMPAD_4 || keyCode == KeyEvent.KEYCODE_NUMPAD_6;
    }

    private static boolean isMenuMoveUp(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_DPAD_UP || keyCode == KeyEvent.KEYCODE_W
                || keyCode == KeyEvent.KEYCODE_CHANNEL_UP || keyCode == KeyEvent.KEYCODE_NUMPAD_8;
    }

    private static boolean isMenuMoveDown(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_DPAD_DOWN || keyCode == KeyEvent.KEYCODE_S
                || keyCode == KeyEvent.KEYCODE_CHANNEL_DOWN || keyCode == KeyEvent.KEYCODE_NUMPAD_2;
    }

    private static boolean isMenuMoveLeft(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_DPAD_LEFT || keyCode == KeyEvent.KEYCODE_A
                || keyCode == KeyEvent.KEYCODE_NUMPAD_4;
    }

    private static boolean isMenuMoveRight(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_DPAD_RIGHT || keyCode == KeyEvent.KEYCODE_D
                || keyCode == KeyEvent.KEYCODE_NUMPAD_6;
    }

    private static boolean isP1LightKey(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_Z
                || keyCode == KeyEvent.KEYCODE_BUTTON_X
                || keyCode == KeyEvent.KEYCODE_BUTTON_1;
    }

    private static boolean isP1KickKey(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_X
                || keyCode == KeyEvent.KEYCODE_BUTTON_B
                || keyCode == KeyEvent.KEYCODE_BUTTON_2;
    }

    private static boolean isP1HeavyPunchKey(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_C
                || keyCode == KeyEvent.KEYCODE_BUTTON_Y
                || keyCode == KeyEvent.KEYCODE_BUTTON_3;
    }

    private static boolean isP1HeavyKickKey(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_V || keyCode == KeyEvent.KEYCODE_BUTTON_R2
                || keyCode == KeyEvent.KEYCODE_BUTTON_13 || keyCode == KeyEvent.KEYCODE_BUTTON_14;
    }

    private static boolean isP1JumpKey(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_SPACE || keyCode == KeyEvent.KEYCODE_BUTTON_A
                || keyCode == KeyEvent.KEYCODE_ENTER
                || keyCode == KeyEvent.KEYCODE_NUMPAD_ENTER;
    }

    private static boolean isP1SpecialKey(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_E || keyCode == KeyEvent.KEYCODE_BUTTON_R1
                || keyCode == KeyEvent.KEYCODE_BUTTON_4
                || keyCode == KeyEvent.KEYCODE_BUTTON_12;
    }

    private static boolean isP1LinkKey(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_Q || keyCode == KeyEvent.KEYCODE_BUTTON_L1
                || keyCode == KeyEvent.KEYCODE_BUTTON_11;
    }

    private static boolean isP1ThrowKey(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_R || keyCode == KeyEvent.KEYCODE_BUTTON_10
                || keyCode == KeyEvent.KEYCODE_BUTTON_L2;
    }

    private static boolean isP1AnyMovementKey(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_DPAD_LEFT || keyCode == KeyEvent.KEYCODE_DPAD_RIGHT
                || keyCode == KeyEvent.KEYCODE_DPAD_UP || keyCode == KeyEvent.KEYCODE_DPAD_DOWN
                || keyCode == KeyEvent.KEYCODE_A || keyCode == KeyEvent.KEYCODE_D
                || keyCode == KeyEvent.KEYCODE_W || keyCode == KeyEvent.KEYCODE_S;
    }

    private static int resolveP1QueuedAction(int keyCode) {
        if (isP1HeavyKickKey(keyCode)) return ACTION_HEAVY_KICK;
        if (isP1HeavyPunchKey(keyCode)) return ACTION_HEAVY_PUNCH;
        if (isP1KickKey(keyCode)) return ACTION_KICK;
        if (isP1LightKey(keyCode)) return ACTION_PUNCH;
        if (isP1SpecialKey(keyCode)) return ACTION_SPECIAL;
        if (isP1LinkKey(keyCode)) return ACTION_LINK;
        if (isP1ThrowKey(keyCode)) return ACTION_THROW;
        if (isP1JumpKey(keyCode)) return ACTION_JUMP;
        return ACTION_NONE;
    }

    private static int resolveP2QueuedAction(int keyCode) {
        if (keyCode == KeyEvent.KEYCODE_BUTTON_R2 || keyCode == KeyEvent.KEYCODE_V) {
            return ACTION_HEAVY_KICK;
        }
        if (keyCode == KeyEvent.KEYCODE_BUTTON_Y || keyCode == KeyEvent.KEYCODE_BUTTON_3
                || keyCode == KeyEvent.KEYCODE_C) {
            return ACTION_HEAVY_PUNCH;
        }
        if (keyCode == KeyEvent.KEYCODE_BUTTON_B || keyCode == KeyEvent.KEYCODE_BUTTON_2
                || keyCode == KeyEvent.KEYCODE_X) {
            return ACTION_KICK;
        }
        if (keyCode == KeyEvent.KEYCODE_BUTTON_X || keyCode == KeyEvent.KEYCODE_BUTTON_1
                || keyCode == KeyEvent.KEYCODE_Z) {
            return ACTION_PUNCH;
        }
        if (keyCode == KeyEvent.KEYCODE_BUTTON_R1 || keyCode == KeyEvent.KEYCODE_BUTTON_4
                || keyCode == KeyEvent.KEYCODE_E) {
            return ACTION_SPECIAL;
        }
        if (keyCode == KeyEvent.KEYCODE_BUTTON_L1 || keyCode == KeyEvent.KEYCODE_BUTTON_11
                || keyCode == KeyEvent.KEYCODE_Q) {
            return ACTION_LINK;
        }
        if (keyCode == KeyEvent.KEYCODE_BUTTON_L2 || keyCode == KeyEvent.KEYCODE_R
                || keyCode == KeyEvent.KEYCODE_BUTTON_10) {
            return ACTION_THROW;
        }
        if (keyCode == KeyEvent.KEYCODE_BUTTON_A || keyCode == KeyEvent.KEYCODE_SPACE
                || keyCode == KeyEvent.KEYCODE_ENTER) {
            return ACTION_JUMP;
        }
        return ACTION_NONE;
    }

    private boolean queueP1ActionByKey(int keyCode) {
        int action = resolveP1QueuedAction(keyCode);
        if (action == ACTION_NONE) return false;
        if (action == ACTION_PUNCH) {
            lightQueued = true;
        } else if (action == ACTION_KICK) {
            kickQueued = true;
        } else if (action == ACTION_HEAVY_PUNCH) {
            heavyQueued = true;
        } else if (action == ACTION_HEAVY_KICK) {
            heavyKickQueued = true;
        } else if (action == ACTION_JUMP) {
            jumpQueued = true;
        } else if (action == ACTION_SPECIAL) {
            specialQueued = true;
        } else if (action == ACTION_LINK) {
            assistQueued = true;
        } else if (action == ACTION_THROW) {
            throwQueued = true;
        }
        return true;
    }

    private boolean queueP2ActionByKey(int keyCode) {
        int action = resolveP2QueuedAction(keyCode);
        if (action == ACTION_NONE) return false;
        if (action == ACTION_PUNCH) {
            p2LightQueued = true;
        } else if (action == ACTION_KICK) {
            p2KickQueued = true;
        } else if (action == ACTION_HEAVY_PUNCH) {
            p2HeavyQueued = true;
        } else if (action == ACTION_HEAVY_KICK) {
            p2HeavyKickQueued = true;
        } else if (action == ACTION_JUMP) {
            p2JumpQueued = true;
        } else if (action == ACTION_SPECIAL) {
            p2SpecialQueued = true;
        } else if (action == ACTION_LINK) {
            p2LinkQueued = true;
        } else if (action == ACTION_THROW) {
            p2ThrowQueued = true;
        }
        return true;
    }

    private void clearP1ActionStateByKey(int keyCode) {
        int action = resolveP1QueuedAction(keyCode);
        if (action == ACTION_NONE) return;
        if (action == ACTION_PUNCH) {
            lightQueued = false;
        } else if (action == ACTION_KICK) {
            kickQueued = false;
        } else if (action == ACTION_HEAVY_PUNCH) {
            heavyQueued = false;
        } else if (action == ACTION_HEAVY_KICK) {
            heavyKickQueued = false;
        } else if (action == ACTION_JUMP) {
            jumpQueued = false;
        } else if (action == ACTION_SPECIAL) {
            specialQueued = false;
        } else if (action == ACTION_LINK) {
            assistQueued = false;
        } else if (action == ACTION_THROW) {
            throwQueued = false;
        }
    }

    private void clearP2ActionStateByKey(int keyCode) {
        int action = resolveP2QueuedAction(keyCode);
        if (action == ACTION_NONE) return;
        if (action == ACTION_PUNCH) {
            p2LightQueued = false;
        } else if (action == ACTION_KICK) {
            p2KickQueued = false;
        } else if (action == ACTION_HEAVY_PUNCH) {
            p2HeavyQueued = false;
        } else if (action == ACTION_HEAVY_KICK) {
            p2HeavyKickQueued = false;
        } else if (action == ACTION_JUMP) {
            p2JumpQueued = false;
        } else if (action == ACTION_SPECIAL) {
            p2SpecialQueued = false;
        } else if (action == ACTION_LINK) {
            p2LinkQueued = false;
        } else if (action == ACTION_THROW) {
            p2ThrowQueued = false;
        }
    }

    private static boolean isAnyDpadOrThumbPad(int source) {
        return isGamepadSource(source)
                || (source & InputDevice.SOURCE_DPAD) != 0
                || (source & InputDevice.SOURCE_KEYBOARD) != 0;
    }

    private boolean isMenuActionRepeatAllowed(int keyCode, long now) {
        if (lastMenuActionCode != keyCode) {
            lastMenuActionCode = keyCode;
            lastMenuActionAt = now;
            return true;
        }
        if (now - lastMenuActionAt >= 150L) {
            lastMenuActionAt = now;
            return true;
        }
        return false;
    }

    private boolean shouldAcceptMenuAxisStep(int requestedDir, int previousDir,
                                            boolean playerTwo, long now) {
        if (requestedDir == 0) return false;
        if (requestedDir != previousDir) {
            if (previousDir == 0) return true;
            long lastAt = playerTwo ? lastMenuNavAtPlayer2 : lastMenuNavAt;
            return now - lastAt >= MENU_NAV_AXIS_REARM_MS;
        }
        long lastAt = playerTwo ? lastMenuNavAtPlayer2 : lastMenuNavAt;
        return now - lastAt >= MENU_NAV_REPEAT_DELAY_MS;
    }

    private void updateControllerIds(int deviceId, int source, int playerSlot) {
        if (deviceId < 0 || !isGamepadSource(source)) return;
        if (playerSlot == 0) {
            primaryControllerId = deviceId;
            lastPrimaryControllerInputMs = SystemClock.uptimeMillis();
            if (secondaryControllerId == primaryControllerId) {
                secondaryControllerId = -1;
                lastSecondaryControllerInputMs = -1L;
            }
            if (primaryControllerId == secondaryControllerId) secondaryControllerId = -1;
        } else if (deviceId != primaryControllerId) {
            secondaryControllerId = deviceId;
            lastSecondaryControllerInputMs = SystemClock.uptimeMillis();
        }
    }

    private int resolveControllerSlot(int deviceId, int source) {
        if (!isGamepadSource(source) || deviceId < 0) return 0;
        if (primaryControllerId < 0 || !isControllerIdConnected(primaryControllerId)) {
            primaryControllerId = deviceId;
            lastPrimaryControllerInputMs = SystemClock.uptimeMillis();
            secondaryControllerId = -1;
            lastSecondaryControllerInputMs = -1L;
        }
        if (primaryControllerId == deviceId) return 0;
        if (secondaryControllerId < 0) secondaryControllerId = deviceId;
        if (secondaryControllerId == deviceId) lastSecondaryControllerInputMs = SystemClock.uptimeMillis();
        return secondaryControllerId == deviceId ? 1 : 0;
    }

    private boolean isControllerIdConnected(int deviceId) {
        if (deviceId < 0) return false;
        InputDevice device = InputDevice.getDevice(deviceId);
        return device != null && (device.getSources() & (
                InputDevice.SOURCE_GAMEPAD | InputDevice.SOURCE_JOYSTICK | InputDevice.SOURCE_DPAD)) != 0;
    }

    private boolean isDedicatedCompanion() {
        boolean valid = secondaryControllerId >= 0
                && secondaryControllerId != primaryControllerId
                && primaryControllerId >= 0;
        if (!valid) return false;
        if (!isControllerIdConnected(primaryControllerId) || !isControllerIdConnected(secondaryControllerId)) {
            secondaryControllerId = -1;
            lastSecondaryControllerInputMs = -1L;
            return false;
        }
        long now = SystemClock.uptimeMillis();
        return lastSecondaryControllerInputMs < 0
                || (now - lastSecondaryControllerInputMs) < CONTROLLER_COMBO_STALE_MS;
    }

    private void resetStaleCompanionController() {
        if (secondaryControllerId < 0 || lastSecondaryControllerInputMs < 0) return;
        if (!isControllerIdConnected(secondaryControllerId)) {
            secondaryControllerId = -1;
            lastSecondaryControllerInputMs = -1L;
            return;
        }
        if (SystemClock.uptimeMillis() - lastSecondaryControllerInputMs > CONTROLLER_COMBO_STALE_MS) {
            secondaryControllerId = -1;
            lastSecondaryControllerInputMs = -1L;
        }
    }

    private boolean hasCompanionController() {
        return isDedicatedCompanion();
    }

    private int resolveSelectSlot(int deviceId, int source) {
        if (!isControllerSource(source) || !isDedicatedCompanion()) return activeSelectionSlot;
        int controllerSlot = resolveControllerSlot(deviceId, source);
        return controllerSlot == 1 ? 1 : 0;
    }

    private boolean tryConfirmSelectionToStart() {
        if (!canStartBattle()) {
            return false;
        }
        if (selectionTransitionInProgress) {
            return false;
        }
        beginSelectionTransition();
        syncHeroSlotsForSafety();
        if (!p1Ready || (isP2RequiredForBattle() && !p2Ready)) {
            finishSelectionTransition();
            return false;
        }
        if (!twoPlayerMode) {
            selectedHero2 = sanitizeHeroIndex(selectedHero);
        }
        try {
            selectedHero = sanitizeHeroIndex(selectedHero);
            selectedHero2 = sanitizeHeroIndex(selectedHero2);
            loadSelectedHeroAnimations();
            if (twoPlayerMode) loadPlayer2Animations();
            else unloadPlayer2Animation(false);
            if ((selectedHeroAnimArt == null && heroArt[selectedHero] == null)
                    && (heroHdArt[selectedHero] == null)) {
                finishSelectionTransition();
                return false;
            }
            if (twoPlayerMode && (selectedHero2 < 0 || selectedHero2 >= HERO_SLOT_COUNT
                    || (player2AnimArt == null && heroArt[selectedHero2] == null
                    && heroHdArt[selectedHero2] == null))) {
                finishSelectionTransition();
                return false;
            }
            selectedCompanion1 = sanitizeCompanionIndex(selectedCompanion1, selectedHero);
            selectedCompanion2 = sanitizeCompanionIndex(selectedCompanion2, selectedHero2);
            prefs.edit()
                    .putInt("selected_hero_p1", selectedHero)
                    .putInt("selected_hero_p2", selectedHero2)
                    .putInt("selected_companion_p1", selectedCompanion1)
                    .putInt("selected_companion_p2", selectedCompanion2)
                    .apply();
            enterState(INTRO);
            return true;
        } catch (Throwable runtimeError) {
            Log.e(TAG, "Start transition blocked by asset issue", runtimeError);
            finishSelectionTransition();
            return false;
        }
    }

    private void beginCharacterSelect() {
        try {
            selectionTransitionInProgress = false;
            syncHeroSlotsForSafety();
            p1Ready = false;
            p2Ready = false;
            activeSelectionSlot = 0;
            selectedHero = safeHeroIndex(selectedHero);
            selectedHero2 = selectedHero;
            unloadPlayer2Animation(false);
            unloadSelectedHeroAnimation();
            // Character selection only needs the compact portraits.  The
            // 12+ MiB decoded animation atlases are loaded once, after every
            // required player has confirmed and the battle is starting.
            resetMenuHats();
            menuHatX = 0;
            menuHatY = 0;
            menuHatXPlayer2 = 0;
            menuHatYPlayer2 = 0;
            lastMenuNavAt = 0L;
            lastMenuNavAtPlayer2 = 0L;
            lastMenuActionCode = Integer.MIN_VALUE;
            lastMenuActionAt = SystemClock.uptimeMillis();
            selectionChangedAt = SystemClock.uptimeMillis();
        } catch (Throwable runtimeError) {
            Log.e(TAG, "beginCharacterSelect failed", runtimeError);
            p1Ready = false;
            p2Ready = false;
            activeSelectionSlot = 0;
            selectedHero = safeHeroIndex(selectedHero);
            selectedHero2 = selectedHero;
            selectionTransitionInProgress = false;
            resetInputsForSelectFailure();
            throw runtimeError;
        }
    }

    private void resetInputsForSelectFailure() {
        menuHatX = 0;
        menuHatY = 0;
        menuHatXPlayer2 = 0;
        menuHatYPlayer2 = 0;
        lastMenuNavAt = 0L;
        lastMenuNavAtPlayer2 = 0L;
        lastMenuActionAt = -150L;
        lastMenuActionCode = Integer.MIN_VALUE;
        clearInputs();
    }

    private void selectHeroForActiveSlot(int heroIndex) {
        if (activeSelectionSlot == 0) {
            selectedHero = sanitizeHeroIndex(heroIndex);
            selectedCompanion1 = sanitizeCompanionIndex(selectedCompanion1, selectedHero);
        } else {
            selectedHero2 = sanitizeHeroIndex(heroIndex);
            selectedCompanion2 = sanitizeCompanionIndex(selectedCompanion2, selectedHero2);
        }
    }

    private void toggleSelectionSlotAfterConfirm() {
        if (hasCompanionController()) {
            activeSelectionSlot = 0;
        } else if (!p1Ready) {
            activeSelectionSlot = 0;
        } else if (!p2Ready) {
            activeSelectionSlot = 1;
        } else {
            activeSelectionSlot = 0;
        }
    }

    private boolean isBattleReady() {
        return p1Ready && (!twoPlayerMode || p2Ready);
    }

    private boolean isP2RequiredForBattle() {
        return twoPlayerMode;
    }

    private boolean canStartBattle() {
        return isBattleReady() && !selectionTransitionInProgress;
    }

    private void beginSelectionTransition() {
        selectionTransitionInProgress = true;
    }

    private void finishSelectionTransition() {
        selectionTransitionInProgress = false;
    }

    private void setReadyForSlot(int controllerSlot, boolean ready) {
        if (controllerSlot == 1) p2Ready = ready;
        else p1Ready = ready;
    }

    private boolean isReadyForSlot(int controllerSlot) {
        return controllerSlot == 1 ? p2Ready : p1Ready;
    }

    private void loadAssets() {
        // The game renders into a 640x360 logical canvas. The 960px masters
        // retain 1.5x detail on phones and TVs while RGB_565 avoids wasting
        // twice the memory on opaque background alpha channels.
        background = loadOpaqueBitmap("tv/backgrounds/street.png");
        if (background == null) background = loadBitmap("backgrounds/street.png");
        stageBackground = loadOpaqueBitmap("tv/backgrounds/street_retro.png");
        if (stageBackground == null) stageBackground = loadBitmap("backgrounds/street_retro.png");
        if (stageBackground == null) stageBackground = loadBitmap("backgrounds/street_hd.png");
        actorAtlas = loadBitmap("ui/actors.png");
        portraits = loadBitmap("ui/portraits.png");
        logo = loadBitmapSampled(customerProfile.logoAsset, 512, 192);
        if (logo == null && !CustomerProfile.DEFAULT_LOGO_ASSET.equals(customerProfile.logoAsset)) {
            logo = loadBitmap(CustomerProfile.DEFAULT_LOGO_ASSET);
        }
        String[] heroNames = customerProfile.heroAssetStems;
        for (int i = 0; i < heroNames.length; i++) {
            heroArt[i] = loadBitmap("heroes/" + heroNames[i] + ".png");
            heroPortraits[i] = loadBitmap("heroes/" + heroNames[i] + "_portrait.png");
        }
        // 384x576 is still 2x the maximum on-screen idle height. Loading the
        // 1373x2048 authoring master here cost 10.7 MiB for no visible gain.
        heroHdArt[0] = loadBitmap("tv/heroes/parent_hd.png");
        enemyArt[0] = loadBitmapSampled("enemies/grunt.png", 256, 256);
        enemyArt[1] = loadBitmapSampled("enemies/skater.png", 256, 256);
        enemyArt[2] = loadBitmapSampled("enemies/brute.png", 256, 256);
        enemyArt[3] = loadBitmapSampled("enemies/boss.png", 256, 256);
        // Enemy animation atlases are intentionally loaded when an encounter
        // starts. Keeping every type decoded from boot costs roughly 18 MB and
        // is a common source of low-memory Android TV process deaths.
        itemArt[0] = loadBitmap("items/food.png");
        itemArt[1] = loadBitmap("items/energy.png");
        itemArt[2] = loadBitmap("items/token.png");
        itemArt[3] = loadBitmap("items/bat.png");
        weaponArt[WEAPON_BAT] = loadBitmap("weapons/bat.png");
        weaponArt[WEAPON_PIPE] = loadBitmap("weapons/pipe.png");
        weaponArt[WEAPON_MALLET] = loadBitmap("weapons/mallet.png");
        weaponArt[WEAPON_SIGN] = loadBitmap("weapons/sign.png");
        weaponArt[WEAPON_CONE] = loadBitmap("props/cone.png");
        propArt[0] = loadBitmap("props/crate.png");
        propArt[1] = loadBitmap("props/trashcan.png");
        actionIcons = loadBitmap("ui/combat_action_icons.png");
        hitFxArt = loadBitmap("fx/hit_fx.png");
        specialFxArt = loadBitmap("fx/special_fx.png");
        weaponTrailFxArt = loadBitmap("fx/weapon_trail_fx.png");
        breakFxArt = loadBitmap("fx/break_fx.png");
    }

    private Bitmap loadBitmap(String name) {
        try (InputStream input = getContext().getAssets().open(name)) {
            BitmapFactory.Options options = new BitmapFactory.Options();
            options.inPreferredConfig = Bitmap.Config.ARGB_8888;
            options.inDither = true;
            Bitmap bitmap = BitmapFactory.decodeStream(input, null, options);
            if (bitmap != null) bitmap.prepareToDraw();
            return bitmap;
        } catch (IOException | OutOfMemoryError | RuntimeException ignored) {
            return null;
        }
    }

    private Bitmap loadBitmapSampled(String name, int requestedWidth, int requestedHeight) {
        try {
            BitmapFactory.Options bounds = new BitmapFactory.Options();
            bounds.inJustDecodeBounds = true;
            try (InputStream input = getContext().getAssets().open(name)) {
                BitmapFactory.decodeStream(input, null, bounds);
            }
            int sample = 1;
            while (bounds.outWidth / (sample * 2) >= requestedWidth
                    && bounds.outHeight / (sample * 2) >= requestedHeight) {
                sample *= 2;
            }
            BitmapFactory.Options options = new BitmapFactory.Options();
            options.inPreferredConfig = Bitmap.Config.ARGB_8888;
            options.inSampleSize = sample;
            options.inDither = true;
            try (InputStream input = getContext().getAssets().open(name)) {
                Bitmap bitmap = BitmapFactory.decodeStream(input, null, options);
                if (bitmap != null) bitmap.prepareToDraw();
                return bitmap;
            }
        } catch (IOException | OutOfMemoryError | RuntimeException ignored) {
            return null;
        }
    }

    private Bitmap loadOpaqueBitmap(String name) {
        try (InputStream input = getContext().getAssets().open(name)) {
            BitmapFactory.Options options = new BitmapFactory.Options();
            options.inPreferredConfig = Bitmap.Config.RGB_565;
            options.inDither = true;
            Bitmap bitmap = BitmapFactory.decodeStream(input, null, options);
            if (bitmap != null) bitmap.prepareToDraw();
            return bitmap;
        } catch (IOException | OutOfMemoryError | RuntimeException ignored) {
            return null;
        }
    }

    private boolean isTelevisionDevice() {
        return (getResources().getConfiguration().uiMode & Configuration.UI_MODE_TYPE_MASK)
                == Configuration.UI_MODE_TYPE_TELEVISION;
    }

    private boolean hasLargeBitmapBudget() {
        ActivityManager manager = (ActivityManager) getContext()
                .getSystemService(Context.ACTIVITY_SERVICE);
        return manager == null || (!manager.isLowRamDevice() && manager.getMemoryClass() >= 192);
    }

    private boolean useReducedMemoryAssets() {
        // Some inexpensive TV firmware and sideload launchers report a normal
        // UI mode. The large-window check keeps those devices on the same
        // memory-safe path without reducing phone assets.
        return isTelevisionDevice()
                || getResources().getConfiguration().smallestScreenWidthDp >= 720
                || !hasLargeBitmapBudget();
    }

    private boolean isValidHeroAtlas(Bitmap bitmap) {
        if (bitmap == null || bitmap.isRecycled()) return false;
        return bitmap.getWidth() % HERO_ANIM_COLUMNS == 0
                && bitmap.getHeight() % HERO_ANIM_ROWS == 0
                && bitmap.getWidth() / HERO_ANIM_COLUMNS >= 96
                && bitmap.getHeight() / HERO_ANIM_ROWS >= 96;
    }

    private Bitmap loadHeroAnimationAtlas(int hero) {
        String stem = customerProfile.heroAssetStems[safeHeroIndex(hero)] + "_anim.png";
        Bitmap atlas = null;
        if (useReducedMemoryAssets()) atlas = loadBitmap("tv/heroes/" + stem);
        if (atlas == null) atlas = loadBitmap("heroes/" + stem);
        return atlas;
    }

    private synchronized void loadEnemyAnimationType(int type) {
        if (type < 0 || type >= enemyAnimArt.length) return;
        Bitmap current = enemyAnimArt[type];
        if (current != null && !current.isRecycled()) return;
        String[] names = {"grunt", "skater", "brute", "boss"};
        boolean reducedMemory = useReducedMemoryAssets();
        Bitmap atlas = loadBitmap((reducedMemory ? "tv/enemies/" : "enemies/")
                + names[type] + "_anim.png");
        if (atlas != null && atlas.getWidth() % ENEMY_ANIM_COLUMNS == 0
                && atlas.getHeight() % ENEMY_ANIM_ROWS == 0) {
            enemyAnimArt[type] = atlas;
        } else if (atlas != null && !atlas.isRecycled()) {
            atlas.recycle();
        }
    }

    private synchronized void prepareEnemyAnimationsForZone(int encounterZone) {
        boolean[] required = new boolean[enemyAnimArt.length];
        for (Enemy enemy : enemies) {
            if (enemy.alive && enemy.zone == encounterZone
                    && enemy.type >= 0 && enemy.type < required.length) {
                required[enemy.type] = true;
            }
        }
        boolean loadedOneAtlasThisTick = false;
        for (int type = 0; type < required.length; type++) {
            if (required[type]) {
                Bitmap current = enemyAnimArt[type];
                if ((current == null || current.isRecycled()) && !loadedOneAtlasThisTick) {
                    loadEnemyAnimationType(type);
                    loadedOneAtlasThisTick = true;
                }
            } else if (enemyAnimArt[type] != null) {
                for (Enemy enemy : enemies) {
                    if (enemy.type == type) enemy.animator.clear();
                }
                if (!enemyAnimArt[type].isRecycled()) enemyAnimArt[type].recycle();
                enemyAnimArt[type] = null;
            }
        }
        for (Enemy enemy : enemies) {
            if (!enemy.alive || enemy.zone != encounterZone) continue;
            Bitmap atlas = enemy.type >= 0 && enemy.type < enemyAnimArt.length
                    ? enemyAnimArt[enemy.type] : null;
            if (atlas != null && !atlas.isRecycled()
                    && enemy.animator.bitmap() != atlas) {
                enemy.animator.clear();
                enemy.animator.bind(atlas, ENEMY_ANIM_COLUMNS, ENEMY_ANIM_ROWS,
                        atlas.getWidth() / ENEMY_ANIM_COLUMNS,
                        atlas.getHeight() / ENEMY_ANIM_ROWS);
                enemy.animator.play(ENEMY_IDLE, ENEMY_ANIM_COLUMNS, 8, true, true);
            }
        }
    }

    private synchronized void loadSelectedHeroAnimations() {
        clampHeroIndexesForPlay();
        if (loadedHeroAnim == selectedHero) return;
        if (selectedHeroAnimArt != null && !selectedHeroAnimArt.isRecycled()) {
            selectedHeroAnimArt.recycle();
        }
        if (loadedPlayer2Anim == selectedHero) {
            unloadPlayer2Animation(false);
        }
        Arrays.fill(selectedHeroAnimSources, null);
        selectedHeroAnimArt = null;
        playerAnimator.clear();
        loadedHeroAnim = -1;
        boolean loaded = false;
        Bitmap candidate = null;
        try {
            candidate = loadHeroAnimationAtlas(selectedHero);
        } catch (OutOfMemoryError ignored) {
            // Keep game alive on low-memory TV devices. Fallback will use
            // static idle/full-body art for this session.
            playerAnimator.clear();
        }
        if (isValidHeroAtlas(candidate)) {
            try {
                selectedHeroAnimArt = candidate;
                cacheHeroAnimSourceRects(selectedHeroAnimArt, selectedHeroAnimSources,
                        HERO_ANIM_ROWS, HERO_ANIM_COLUMNS);
                playerAnimator.bind(selectedHeroAnimArt, HERO_ANIM_COLUMNS, HERO_ANIM_ROWS,
                        selectedHeroAnimArt.getWidth() / HERO_ANIM_COLUMNS,
                        selectedHeroAnimArt.getHeight() / HERO_ANIM_ROWS);
                playerAnimator.play(HERO_IDLE, 8, 8, true, true);
                loaded = true;
            } catch (RuntimeException | OutOfMemoryError ignored) {
                if (selectedHeroAnimArt != null && !selectedHeroAnimArt.isRecycled()) {
                    selectedHeroAnimArt.recycle();
                }
                selectedHeroAnimArt = null;
                playerAnimator.clear();
            }
        } else if (candidate != null) {
            candidate.recycle();
        }
        loadedHeroAnim = loaded ? selectedHero : -1;
        selectedCompanion1 = sanitizeCompanionIndex(selectedCompanion1, selectedHero);
    }

    private synchronized void unloadPlayer2Animation(boolean forceRecycleShared) {
        if (!forceRecycleShared && player2AnimSharesPlayerAnim) {
            player2AnimArt = null;
            player2Animator.clear();
            loadedPlayer2Anim = selectedHero2;
            return;
        }
        if (player2AnimArt != null && !player2AnimArt.isRecycled()) {
            player2AnimArt.recycle();
        }
        player2AnimArt = null;
        player2Animator.clear();
        loadedPlayer2Anim = -1;
        Arrays.fill(player2AnimSources, null);
        player2AnimSharesPlayerAnim = false;
    }

    private synchronized void unloadSelectedHeroAnimation() {
        // Detach a shared P2 reference before recycling the P1 atlas.
        if (player2AnimSharesPlayerAnim) {
            unloadPlayer2Animation(false);
        }
        if (selectedHeroAnimArt != null && !selectedHeroAnimArt.isRecycled()) {
            selectedHeroAnimArt.recycle();
        }
        selectedHeroAnimArt = null;
        playerAnimator.clear();
        loadedHeroAnim = -1;
        Arrays.fill(selectedHeroAnimSources, null);
    }

    private synchronized void loadPlayer2Animations() {
        selectedHero2 = sanitizeHeroIndex(selectedHero2);
        if (loadedPlayer2Anim == selectedHero2
                && player2AnimArt != null
                && !player2AnimArt.isRecycled()) {
            return;
        }
        unloadPlayer2Animation(selectedHero2 == selectedHero);
        if (selectedHero2 == selectedHero && selectedHeroAnimArt != null && !selectedHeroAnimArt.isRecycled()) {
            player2AnimArt = selectedHeroAnimArt;
            player2Animator.bind(player2AnimArt, HERO_ANIM_COLUMNS, HERO_ANIM_ROWS,
                    player2AnimArt.getWidth() / HERO_ANIM_COLUMNS,
                    player2AnimArt.getHeight() / HERO_ANIM_ROWS);
            player2AnimSharesPlayerAnim = true;
            loadedPlayer2Anim = selectedHero2;
            return;
        }
        boolean loaded = false;
        Bitmap candidate;
        try {
            candidate = loadHeroAnimationAtlas(selectedHero2);
            if (candidate == null) {
                player2Animator.clear();
                player2AnimSharesPlayerAnim = false;
                loadedPlayer2Anim = -1;
                return;
            }
            if (isValidHeroAtlas(candidate)) {
                player2AnimArt = candidate;
                cacheHeroAnimSourceRects(player2AnimArt, player2AnimSources,
                        HERO_ANIM_ROWS, HERO_ANIM_COLUMNS);
                player2Animator.bind(player2AnimArt, HERO_ANIM_COLUMNS, HERO_ANIM_ROWS,
                        player2AnimArt.getWidth() / HERO_ANIM_COLUMNS,
                        player2AnimArt.getHeight() / HERO_ANIM_ROWS);
                player2AnimSharesPlayerAnim = false;
                loadedPlayer2Anim = selectedHero2;
                loaded = true;
            } else {
                candidate.recycle();
                player2Animator.clear();
                player2AnimSharesPlayerAnim = false;
                loadedPlayer2Anim = -1;
            }
        } catch (OutOfMemoryError | RuntimeException ignored) {
            // A TV can have a much smaller graphics heap than a phone. Keep
            // the game alive and render P2 from the compact fallback art.
            player2AnimSharesPlayerAnim = false;
            player2Animator.clear();
            loadedPlayer2Anim = -1;
        }
        if (!loaded) {
            Arrays.fill(player2AnimSources, null);
        }
    }

    private boolean isConfirmActionKey(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_ENTER || keyCode == KeyEvent.KEYCODE_SPACE
                || keyCode == KeyEvent.KEYCODE_BUTTON_START
                || keyCode == KeyEvent.KEYCODE_BUTTON_MODE
                || keyCode == KeyEvent.KEYCODE_BUTTON_A || keyCode == KeyEvent.KEYCODE_BUTTON_1
                || keyCode == KeyEvent.KEYCODE_DPAD_CENTER || keyCode == KeyEvent.KEYCODE_BUTTON_X
                || keyCode == KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE || keyCode == KeyEvent.KEYCODE_Z
                || keyCode == KeyEvent.KEYCODE_NUMPAD_ENTER || keyCode == KeyEvent.KEYCODE_BUTTON_15;
    }

    private boolean isCancelActionKey(int keyCode) {
        return keyCode == KeyEvent.KEYCODE_BACK || keyCode == KeyEvent.KEYCODE_ESCAPE
                || keyCode == KeyEvent.KEYCODE_BUTTON_B || keyCode == KeyEvent.KEYCODE_BUTTON_SELECT
                || keyCode == KeyEvent.KEYCODE_BUTTON_MODE || keyCode == KeyEvent.KEYCODE_MEDIA_REWIND
                || keyCode == KeyEvent.KEYCODE_MENU;
    }

    private void resetMenuHats() {
        menuHatX = 0;
        menuHatY = 0;
        menuHatXPlayer2 = 0;
        menuHatYPlayer2 = 0;
    }

    private static void cacheHeroAnimSourceRects(Bitmap source, Rect[] cache, int rows, int columns) {
        Arrays.fill(cache, null);
        int cellWidth = source.getWidth() / Math.max(1, columns);
        int cellHeight = source.getHeight() / Math.max(1, rows);
        int frameLimit = Math.min(cache.length, rows * columns);
        for (int frame = 0; frame < frameLimit; frame++) {
            int row = frame / columns;
            int col = frame % columns;
            int sx = col * cellWidth;
            int sy = row * cellHeight;
            int minX = cellWidth;
            int minY = cellHeight;
            int maxX = -1;
            int maxY = -1;
            for (int y = 0; y < cellHeight; y++) {
                int oy = sy + y;
                for (int x = 0; x < cellWidth; x++) {
                    if ((source.getPixel(sx + x, oy) >>> 24) > 12) {
                        if (x < minX) minX = x;
                        if (x > maxX) maxX = x;
                        if (y < minY) minY = y;
                        if (y > maxY) maxY = y;
                    }
                }
            }
            if (maxX < 0 || maxY < 0) {
                cache[frame] = new Rect(sx, sy, sx + cellWidth, sy + cellHeight);
            } else {
                cache[frame] = new Rect(sx + minX, sy + minY, sx + maxX + 1, sy + maxY + 1);
            }
        }
    }

    private synchronized void loadAssistAnimationRow(int hero) {
        hero = sanitizeHeroIndex(hero);
        if (loadedAssistHero == hero) return;
        if (assistAnimArt != null && !assistAnimArt.isRecycled()) assistAnimArt.recycle();
        assistAnimArt = null;
        assistAnimator.clear();
        BitmapRegionDecoder decoder = null;
        String stem = customerProfile.heroAssetStems[hero] + "_anim.png";
        String path = useReducedMemoryAssets() ? "tv/heroes/" + stem : "heroes/" + stem;
        try (InputStream input = getContext().getAssets().open(path)) {
            decoder = BitmapRegionDecoder.newInstance(input, false);
            if (decoder != null && decoder.getWidth() % HERO_ANIM_COLUMNS == 0
                    && decoder.getHeight() % HERO_ANIM_ROWS == 0) {
                int cellHeight = decoder.getHeight() / HERO_ANIM_ROWS;
                Rect row = new Rect(0, HERO_LINK * cellHeight,
                        decoder.getWidth(), (HERO_LINK + 1) * cellHeight);
                assistAnimArt = decoder.decodeRegion(row, null);
                if (assistAnimArt != null) assistAnimArt.prepareToDraw();
            }
        } catch (IOException | IllegalArgumentException ignored) {
            assistAnimArt = null;
        } catch (OutOfMemoryError ignored) {
            assistAnimArt = null;
        } finally {
            if (decoder != null && !decoder.isRecycled()) decoder.recycle();
        }
        if (assistAnimArt != null) {
            try {
                Arrays.fill(assistAnimSources, null);
                cacheHeroAnimSourceRects(assistAnimArt, assistAnimSources, 1, HERO_ANIM_COLUMNS);
                assistAnimator.bind(assistAnimArt, HERO_ANIM_COLUMNS, 1,
                        assistAnimArt.getWidth() / HERO_ANIM_COLUMNS,
                        assistAnimArt.getHeight());
                assistAnimator.play(0, 8, 14, false, true);
            } catch (RuntimeException | OutOfMemoryError loadFailure) {
                Log.w(TAG, "Companion animation fell back to compact art", loadFailure);
                if (!assistAnimArt.isRecycled()) assistAnimArt.recycle();
                assistAnimArt = null;
                assistAnimator.clear();
                Arrays.fill(assistAnimSources, null);
            }
        }
        loadedAssistHero = hero;
    }

    @Override
    public void surfaceCreated(SurfaceHolder surfaceHolder) {
        startLoop();
    }

    @Override
    public void surfaceChanged(SurfaceHolder surfaceHolder, int format, int width, int height) {
        viewportWidth = width;
        viewportHeight = height;
        uiAnimationsEnabled = ValueAnimator.areAnimatorsEnabled();
        updateResponsiveLayout(width, height);
    }

    private void updateResponsiveLayout(int width, int height) {
        if (width <= 0 || height <= 0) return;
        float aspect = width / (float) height;
        float gameAspect = W / (float) H;
        if (aspect >= gameAspect) {
            scale = height / (float) H;
            virtualWidth = width / scale;
            virtualHeight = H;
            sceneX = (virtualWidth - W) * 0.5f;
            menuSceneY = gameSceneY = 0f;
            responsiveLayout = virtualWidth >= 760f
                    ? LAYOUT_SIDE_GUTTERS : LAYOUT_COMPACT;
        } else {
            scale = width / (float) W;
            virtualWidth = W;
            virtualHeight = height / scale;
            sceneX = 0f;
            menuSceneY = (virtualHeight - H) * 0.5f;
            responsiveLayout = virtualHeight >= 444f
                    ? LAYOUT_CONTROL_DECK : LAYOUT_COMPACT;
            gameSceneY = responsiveLayout == LAYOUT_CONTROL_DECK
                    ? Math.min(12f, (virtualHeight - H) * 0.08f) : menuSceneY;
        }
        // The logical viewport always covers the complete SurfaceView, so no
        // physical letterbox region is left black.
        offsetX = 0f;
        offsetY = 0f;
        viewportGradient = new LinearGradient(0, 0, 0, virtualHeight,
                Color.rgb(19, 14, 61), Color.rgb(4, 28, 42), Shader.TileMode.CLAMP);
        updateControlLayout();
    }

    private void updateControlLayout() {
        pauseCenterX = sceneX + 616f;
        pauseCenterY = gameSceneY + 88f;
        controlScale = 1f;
        if (responsiveLayout == LAYOUT_CONTROL_DECK) {
            float deckTop = gameSceneY + H;
            float deckHeight = Math.max(80f, virtualHeight - deckTop);
            float centerY = deckTop + deckHeight * 0.52f;
            controlScale = clamp((deckHeight - 14f) / 150f, 0.78f, 1f);
            stickCenterX = 90f;
            stickCenterY = centerY;
            float[] deckX = {605f, 547f, 489f, 431f, 605f, 547f, 489f, 431f};
            for (int i = 0; i < touchButtonX.length; i++) {
                touchButtonX[i] = deckX[i];
                touchButtonY[i] = centerY + (i < 4 ? 27f : -31f) * controlScale;
            }
        } else if (responsiveLayout == LAYOUT_SIDE_GUTTERS) {
            float gutter = sceneX;
            float rightCenter = sceneX + W + gutter * 0.5f;
            controlScale = clamp((gutter - 8f) / 105f, 0.72f, 0.94f);
            stickCenterX = gutter * 0.5f;
            stickCenterY = 278f;
            for (int i = 0; i < touchButtonX.length; i++) {
                boolean rightColumn = (i & 1) == 0;
                touchButtonX[i] = rightCenter + (rightColumn ? 20f : -20f) * controlScale;
                touchButtonY[i] = 304f - (i / 2) * 54f * controlScale;
            }
        } else {
            stickCenterX = sceneX + 90f;
            stickCenterY = gameSceneY + 285f;
            float[] compactX = {557f, 500f, 604f, 551f, 607f, 500f, 444f, 447f};
            float[] compactY = {299f, 317f, 257f, 246f, 201f, 270f, 280f, 225f};
            for (int i = 0; i < touchButtonX.length; i++) {
                touchButtonX[i] = sceneX + compactX[i];
                touchButtonY[i] = gameSceneY + compactY[i];
            }
        }
    }

    @Override
    public void surfaceDestroyed(SurfaceHolder surfaceHolder) {
        stopLoop();
    }

    private synchronized void startLoop() {
        if (running || !appActive || !holder.getSurface().isValid()) return;
        running = true;
        loopThread = new Thread(this, "FamilyForceLoop");
        loopThread.start();
        audio.resumeMusic();
    }

    private void stopLoop() {
        Thread thread;
        synchronized (this) {
            running = false;
            thread = loopThread;
            loopThread = null;
        }
        if (thread != null && thread != Thread.currentThread()) {
            try {
                thread.join(500);
            } catch (InterruptedException ignored) {
                Thread.currentThread().interrupt();
            }
        }
    }

    void resumeGame() {
        appActive = true;
        uiAnimationsEnabled = ValueAnimator.areAnimatorsEnabled();
        primaryControllerId = -1;
        secondaryControllerId = -1;
        startLoop();
        audio.resumeMusic();
    }

    void pauseGame() {
        appActive = false;
        if (state == PLAY && !zoneActive) saveCheckpoint(zone);
        if (state == PLAY) enterState(PAUSE);
        savePersistentState();
        clearInputs();
        stopLoop();
        audio.pauseMusic();
    }

    synchronized void trimMemory(int level) {
        if (level < android.content.ComponentCallbacks2.TRIM_MEMORY_RUNNING_LOW) return;
        if (!assist.active && assistAnimArt != null) {
            assistAnimator.clear();
            recycleBitmap(assistAnimArt);
            assistAnimArt = null;
            loadedAssistHero = -1;
        }
        if (state != PLAY) {
            unloadPlayer2Animation(false);
            unloadSelectedHeroAnimation();
            for (int type = 0; type < enemyAnimArt.length; type++) {
                for (Enemy enemy : enemies) {
                    if (enemy.type == type) enemy.animator.clear();
                }
                recycleBitmap(enemyAnimArt[type]);
                enemyAnimArt[type] = null;
            }
        }
    }

    void shutdown() {
        appActive = false;
        stopLoop();
        savePersistentState();
        audio.release();
        releaseBitmaps();
    }

    private void savePersistentState() {
        prefs.edit()
                .putInt("selected_hero_p1", safeHeroIndex(selectedHero))
                .putInt("selected_hero_p2", safeHeroIndex(selectedHero2))
                .putBoolean("last_two_player", twoPlayerMode)
                .apply();
    }

    private int checkpointHash(int savedZone, int hero1, int hero2, boolean coop,
                               int savedHealth, int savedEnergy, int savedLink,
                               int savedScore, int savedWeapon, int savedDurability) {
        int hash = 0x46F04CE;
        hash = hash * 31 + CHECKPOINT_VERSION;
        hash = hash * 31 + savedZone;
        hash = hash * 31 + hero1;
        hash = hash * 31 + hero2;
        hash = hash * 31 + (coop ? 1 : 0);
        hash = hash * 31 + savedHealth;
        hash = hash * 31 + savedEnergy;
        hash = hash * 31 + savedLink;
        hash = hash * 31 + savedScore;
        hash = hash * 31 + savedWeapon;
        return hash * 31 + savedDurability;
    }

    private int checkpointTeamHash(int companion1, int companion2, int savedDifficulty,
                                   int savedP2Health, int savedP2Energy, int savedP2Link) {
        int hash = 0x2317A9B;
        hash = hash * 31 + CHECKPOINT_VERSION;
        hash = hash * 31 + companion1;
        hash = hash * 31 + companion2;
        hash = hash * 31 + savedDifficulty;
        hash = hash * 31 + savedP2Health;
        hash = hash * 31 + savedP2Energy;
        return hash * 31 + savedP2Link;
    }

    private boolean validateCheckpoint() {
        if (!prefs.getBoolean("checkpoint_valid", false)
                || prefs.getInt("checkpoint_version", -1) != CHECKPOINT_VERSION) return false;
        int savedZone = prefs.getInt("checkpoint_zone", -1);
        int hero1 = prefs.getInt("checkpoint_hero1", -1);
        int hero2 = prefs.getInt("checkpoint_hero2", -1);
        boolean coop = prefs.getBoolean("checkpoint_coop", false);
        int savedHealth = prefs.getInt("checkpoint_health", -1);
        int savedEnergy = prefs.getInt("checkpoint_energy", -1);
        int savedLink = prefs.getInt("checkpoint_link", -1);
        int savedScore = prefs.getInt("checkpoint_score", -1);
        int savedWeapon = prefs.getInt("checkpoint_weapon", -2);
        int savedDurability = prefs.getInt("checkpoint_durability", -1);
        int companion1 = prefs.getInt("checkpoint_companion1", -1);
        int companion2 = prefs.getInt("checkpoint_companion2", -1);
        int savedDifficulty = prefs.getInt("checkpoint_difficulty", -1);
        int savedP2Health = prefs.getInt("checkpoint_p2_health", -1);
        int savedP2Energy = prefs.getInt("checkpoint_p2_energy", -1);
        int savedP2Link = prefs.getInt("checkpoint_p2_link", -1);
        int expected = checkpointHash(savedZone, hero1, hero2, coop, savedHealth,
                savedEnergy, savedLink, savedScore, savedWeapon, savedDurability);
        int expectedTeam = checkpointTeamHash(companion1, companion2, savedDifficulty,
                savedP2Health, savedP2Energy, savedP2Link);
        boolean valid = savedZone >= 0 && savedZone < ZONE_TRIGGERS.length
                && hero1 >= 0 && hero1 < HERO_SLOT_COUNT
                && hero2 >= 0 && hero2 < HERO_SLOT_COUNT
                && savedHealth > 0 && savedHealth <= 999
                && savedEnergy >= 0 && savedEnergy <= 100
                && savedLink >= 0 && savedLink <= 100
                && savedScore >= 0
                && savedWeapon >= -1 && savedWeapon < PROP_CRATE
                && savedDurability >= 0 && savedDurability <= 99
                && companion1 >= 0 && companion1 < HERO_SLOT_COUNT && companion1 != hero1
                && companion2 >= 0 && companion2 < HERO_SLOT_COUNT && companion2 != hero2
                && savedDifficulty >= 0 && savedDifficulty <= 2
                && savedP2Health > 0 && savedP2Health <= 999
                && savedP2Energy >= 0 && savedP2Energy <= 100
                && savedP2Link >= 0 && savedP2Link <= 100
                && prefs.getInt("checkpoint_hash", 0) == expected
                && prefs.getInt("checkpoint_team_hash", 0) == expectedTeam;
        if (!valid) prefs.edit().remove("checkpoint_valid").apply();
        return valid;
    }

    private void saveCheckpoint(int safeZone) {
        if (trainingMode || safeZone < 0 || safeZone >= ZONE_TRIGGERS.length) return;
        int hero1 = safeHeroIndex(selectedHero);
        int hero2 = safeHeroIndex(selectedHero2);
        int safeHealth = clampInt(health, 1, safeHeroMaxHealth(hero1));
        int safeEnergy = clampInt(energy, 0, 100);
        int safeLink = clampInt(linkMeter, 0, 100);
        int safeScore = Math.max(0, score);
        int safeWeapon = heldWeaponType >= 0 && heldWeaponType < PROP_CRATE
                ? heldWeaponType : -1;
        int safeDurability = safeWeapon >= 0 ? clampInt(weaponDurability, 1, 99) : 0;
        int companion1 = sanitizeCompanionIndex(selectedCompanion1, hero1);
        int companion2 = sanitizeCompanionIndex(selectedCompanion2, hero2);
        int safeDifficulty = clampInt(difficulty, 0, 2);
        int safeP2Health = clampInt(p2Health, 1, safeHeroMaxHealth(hero2));
        int safeP2Energy = clampInt(p2Energy, 0, 100);
        int safeP2Link = clampInt(p2Link, 0, 100);
        int hash = checkpointHash(safeZone, hero1, hero2, twoPlayerMode, safeHealth,
                safeEnergy, safeLink, safeScore, safeWeapon, safeDurability);
        int teamHash = checkpointTeamHash(companion1, companion2, safeDifficulty,
                safeP2Health, safeP2Energy, safeP2Link);
        boolean committed = prefs.edit()
                .putInt("checkpoint_version", CHECKPOINT_VERSION)
                .putInt("checkpoint_zone", safeZone)
                .putInt("checkpoint_hero1", hero1)
                .putInt("checkpoint_hero2", hero2)
                .putBoolean("checkpoint_coop", twoPlayerMode)
                .putInt("checkpoint_health", safeHealth)
                .putInt("checkpoint_energy", safeEnergy)
                .putInt("checkpoint_link", safeLink)
                .putInt("checkpoint_score", safeScore)
                .putInt("checkpoint_weapon", safeWeapon)
                .putInt("checkpoint_durability", safeDurability)
                .putInt("checkpoint_companion1", companion1)
                .putInt("checkpoint_companion2", companion2)
                .putInt("checkpoint_difficulty", safeDifficulty)
                .putInt("checkpoint_p2_health", safeP2Health)
                .putInt("checkpoint_p2_energy", safeP2Energy)
                .putInt("checkpoint_p2_link", safeP2Link)
                .putInt("checkpoint_hash", hash)
                .putInt("checkpoint_team_hash", teamHash)
                .putBoolean("checkpoint_valid", true)
                .commit();
        hasCheckpoint = committed && validateCheckpoint();
    }

    private void clearCheckpoint() {
        prefs.edit().remove("checkpoint_valid").commit();
        hasCheckpoint = false;
    }

    private boolean restoreCheckpoint() {
        if (!validateCheckpoint()) {
            hasCheckpoint = false;
            return false;
        }
        selectedHero = prefs.getInt("checkpoint_hero1", 0);
        selectedHero2 = prefs.getInt("checkpoint_hero2", 1);
        twoPlayerMode = prefs.getBoolean("checkpoint_coop", false);
        selectedCompanion1 = prefs.getInt("checkpoint_companion1", 1);
        selectedCompanion2 = prefs.getInt("checkpoint_companion2", 0);
        difficulty = prefs.getInt("checkpoint_difficulty", 1);
        trainingMode = false;
        resetGame();
        zone = prefs.getInt("checkpoint_zone", 0);
        health = clampInt(prefs.getInt("checkpoint_health", maxHealth), 1, maxHealth);
        energy = clampInt(prefs.getInt("checkpoint_energy", 55), 0, 100);
        linkMeter = clampInt(prefs.getInt("checkpoint_link", 60), 0, 100);
        p2Health = clampInt(prefs.getInt("checkpoint_p2_health", p2Health), 1,
                safeHeroMaxHealth(selectedHero2));
        p2Energy = clampInt(prefs.getInt("checkpoint_p2_energy", 55), 0, 100);
        p2Link = clampInt(prefs.getInt("checkpoint_p2_link", 60), 0, 100);
        score = Math.max(0, prefs.getInt("checkpoint_score", 0));
        heldWeaponType = prefs.getInt("checkpoint_weapon", -1);
        weaponDurability = heldWeaponType >= 0
                ? clampInt(prefs.getInt("checkpoint_durability", 1), 1, 99) : 0;
        for (Enemy enemy : enemies) {
            if (enemy.alive && enemy.zone < zone) {
                enemy.alive = false;
                enemy.active = false;
            }
        }
        playerX = zone == 0 ? 185f : Math.max(185f, ZONE_TRIGGERS[zone] - 92f);
        playerY = 278f;
        if (twoPlayerMode) {
            player2X = playerX - 50f;
            player2Y = 300f;
        }
        cameraX = clamp(playerX - 210f, 0f, WORLD_END - W + 100f);
        zoneActive = false;
        zoneBanner = 150;
        clearInputs();
        return true;
    }

    private static void recycleBitmap(Bitmap bitmap) {
        if (bitmap != null && !bitmap.isRecycled()) bitmap.recycle();
    }

    private void releaseBitmaps() {
        playerAnimator.clear();
        player2Animator.clear();
        assistAnimator.clear();
        for (Enemy enemy : enemies) if (enemy != null) enemy.animator.clear();
        recycleBitmap(background);
        recycleBitmap(stageBackground);
        recycleBitmap(actorAtlas);
        recycleBitmap(portraits);
        recycleBitmap(logo);
        for (Bitmap bitmap : heroArt) recycleBitmap(bitmap);
        for (Bitmap bitmap : heroHdArt) recycleBitmap(bitmap);
        for (Bitmap bitmap : heroPortraits) recycleBitmap(bitmap);
        for (Bitmap bitmap : enemyArt) recycleBitmap(bitmap);
        for (Bitmap bitmap : enemyAnimArt) recycleBitmap(bitmap);
        for (Bitmap bitmap : itemArt) recycleBitmap(bitmap);
        for (Bitmap bitmap : weaponArt) recycleBitmap(bitmap);
        for (Bitmap bitmap : propArt) recycleBitmap(bitmap);
        recycleBitmap(actionIcons);
        recycleBitmap(hitFxArt);
        recycleBitmap(specialFxArt);
        recycleBitmap(weaponTrailFxArt);
        recycleBitmap(breakFxArt);
        recycleBitmap(selectedHeroAnimArt);
        recycleBitmap(player2AnimArt);
        recycleBitmap(assistAnimArt);
    }

    boolean handleBack() {
        if (state == PLAY) {
            enterState(PAUSE);
            audio.play(AudioController.CONFIRM);
            return true;
        }
        if (state == PAUSE || state == SELECT || state == INTRO || state == RESULTS
                || state == GAME_OVER || state == GALLERY) {
            enterState(MENU);
            return true;
        }
        if (state == SETTINGS) {
            enterState(settingsReturn);
            return true;
        }
        if (state == MENU) {
            enterState(TITLE);
            return true;
        }
        return state != TITLE;
    }

    @Override
    public void run() {
        final long step = 1_000_000_000L / 60L;
        long previous = System.nanoTime();
        long accumulator = 0;
        while (running) {
            long now = System.nanoTime();
            long elapsed = Math.min(now - previous, step * 6);
            previous = now;
            accumulator += elapsed;
            int updates = 0;
            while (accumulator >= step && updates < 5) {
                try {
                    synchronized (this) {
                        update();
                    }
                } catch (Throwable runtimeError) {
                    Log.e(TAG, "Update crash, returning to menu", runtimeError);
                    clearInputs();
                    enterState(MENU);
                    accumulator = 0;
                    break;
                }
                accumulator -= step;
                updates++;
            }
                try {
                    synchronized (this) {
                        renderFrame();
                    }
                } catch (Throwable runtimeError) {
                    Log.e(TAG, "Render crash, returning to menu", runtimeError);
                    clearInputs();
                    enterState(MENU);
                // Keep loop alive to avoid closing the app when TV drivers
                // briefly reject one frame (common on some Leanback devices).
                // A hard-stop here would look like a crash/exit.
                accumulator = 0;
            }
            long remaining = step - (System.nanoTime() - now);
            if (remaining > 1_000_000L) SystemClock.sleep(remaining / 1_000_000L);
        }
    }

    private void update() {
        audio.ensureMusic(state == PLAY || state == PAUSE ? "audio/stage.ogg" : "audio/menu.ogg");
        if (state == PLAY) {
            clampHeroIndexesForPlay();
            updateGame();
        }
        for (Particle particle : particles) {
            if (!particle.active) continue;
            particle.x += particle.vx;
            particle.y += particle.vy;
            particle.vy += 0.08f;
            if (--particle.life <= 0) particle.active = false;
        }
    }

    private void resetGame() {
        clampHeroIndexesForPlay();
        int p1 = safeHeroIndex(selectedHero);
        int p2 = safeHeroIndex(selectedHero2);
        loadSelectedHeroAnimations();
        if (twoPlayerMode) loadPlayer2Animations();
        else unloadPlayer2Animation(false);
        if (playerAnimator.isBound()) {
            playerAnimator.play(HERO_IDLE, HERO_ANIM_COLUMNS, 8, true, true);
        }
        playerX = 185f;
        playerY = 278f;
        player2X = 135f;
        player2Y = 300f;
        player2Z = 0f;
        player2JumpVelocity = 0f;
        p2FacingRight = true;
        p2AttackTimer = 0;
        p2AttackKind = ACTION_NONE;
        p2PunchChainStep = 0;
        p2PunchChainWindow = 0;
        p2Health = HERO_HP[p2];
        p2Energy = 55;
        p2Link = 60;
        p1ReviveProgress = 0;
        p2ReviveProgress = 0;
        p2Invulnerable = 0;
        p2HurtTimer = 0;
        p2LightQueued = p2KickQueued = p2HeavyQueued = p2HeavyKickQueued = false;
        p2JumpQueued = p2SpecialQueued = p2LinkQueued = p2ThrowQueued = false;
        if (twoPlayerMode && player2Animator.isBound()) {
            player2Animator.play(HERO_IDLE, HERO_ANIM_COLUMNS, 8, true, true);
        }
        playerZ = 0f;
        jumpVelocity = 0f;
        playerVx = playerVy = 0f;
        cameraX = 0f;
        lastHitEnemy = null;
        lastHitEnemyTicks = 0;
        maxHealth = HERO_HP[p1];
        health = maxHealth;
        energy = 55;
        linkMeter = 60;
        score = 0;
        combo = 0;
        comboWindow = 0;
        attackTimer = 0;
        attackKind = 0;
        attackSerial = 0;
        bufferedAction = ACTION_NONE;
        bufferedActionTicks = 0;
        actionRecoveryTicks = 0;
        punchChainStep = 0;
        punchChainWindow = 0;
        actionHitFired = false;
        actionObjectFired = false;
        invulnerable = 0;
        hurtTimer = 0;
        knockoutTimer = 0;
        weaponDurability = 0;
        heldWeaponType = -1;
        facingRight = true;
        zone = 0;
        zoneActive = false;
        zoneBanner = 150;
        stageFrames = 0;
        hitStop = 0;
        shakeFrames = 0;
        totalHits = 0;
        damageTaken = 0;
        teamComboBanner = 0;
        teamComboCount = 0;
        dashAttackActive = false;
        clearInputs();
        for (Enemy enemy : enemies) enemy.alive = false;
        for (Item item : items) item.active = false;
        for (Particle particle : particles) particle.active = false;
        for (WorldObject object : worldObjects) object.active = false;
        for (SpriteEffect effect : spriteEffects) effect.active = false;
        assist.active = false;
        spawnEnemy(0, 0, 650, 264);
        spawnEnemy(0, 1, 735, 305);
        spawnEnemy(0, 0, 800, 238);
        spawnEnemy(1, 1, 1260, 252);
        spawnEnemy(1, 0, 1325, 310);
        spawnEnemy(1, 2, 1410, 278);
        spawnEnemy(2, 0, 1900, 235);
        spawnEnemy(2, 3, 2010, 278);
        spawnEnemy(2, 0, 2110, 315);
        spawnEnemy(3, 1, 2480, 258);
        spawnEnemy(3, 2, 2570, 300);
        spawnEnemy(3, 0, 2680, 238);
        spawnEnemy(4, 3, 3070, 278);
        spawnEnemy(4, 1, 3160, 310);
        spawnEnemy(4, 2, 3260, 250);
        spawnEnemy(5, 0, 3500, 246);
        spawnEnemy(5, 1, 3610, 305);
        spawnEnemy(5, 3, 3720, 279);
        spawnEnemy(6, 1, 4300, 246);
        spawnEnemy(6, 0, 4380, 302);
        spawnEnemy(6, 2, 4470, 268);
        spawnEnemy(6, 1, 4550, 315);
        spawnEnemy(7, 0, 4930, 240);
        spawnEnemy(7, 2, 5010, 300);
        spawnEnemy(7, 1, 5100, 258);
        spawnEnemy(7, 2, 5190, 312);
        spawnEnemy(8, 2, 5600, 250);
        spawnEnemy(8, 0, 5680, 308);
        spawnEnemy(8, 1, 5760, 270);
        spawnEnemy(8, 3, 5850, 285);
        spawnWorldObject(WEAPON_BAT, 365, 296);
        spawnWorldObject(PROP_CRATE, 545, 244);
        spawnWorldObject(WEAPON_PIPE, 990, 310);
        spawnWorldObject(WEAPON_CONE, 1185, 244);
        spawnWorldObject(PROP_TRASH_CAN, 1510, 304);
        spawnWorldObject(WEAPON_MALLET, 1790, 260);
        spawnWorldObject(WEAPON_SIGN, 2075, 316);
        spawnWorldObject(PROP_CRATE, 3950, 250);
        spawnWorldObject(WEAPON_BAT, 4210, 300);
        spawnWorldObject(PROP_TRASH_CAN, 4700, 260);
        spawnWorldObject(WEAPON_PIPE, 4860, 312);
        spawnWorldObject(PROP_CRATE, 5350, 246);
        spawnWorldObject(WEAPON_MALLET, 5520, 296);
    }

    private void spawnEnemy(int enemyZone, int type, float x, float y) {
        for (Enemy enemy : enemies) {
            if (enemy.alive) continue;
            enemy.alive = true;
            enemy.active = false;
            enemy.zone = enemyZone;
            enemy.type = type;
            enemy.x = x;
            enemy.y = y;
            enemy.hp = type == 3 ? 330 : type == 2 ? 115 : type == 1 ? 70 : 82;
            enemy.maxHp = enemy.hp;
            enemy.attackCooldown = 30 + random.nextInt(60);
            enemy.attackTimer = 0;
            enemy.stun = 0;
            enemy.flash = 0;
            enemy.lastHitSerial = -1;
            enemy.lastObjectHitSerial = -1;
            enemy.facingRight = false;
            enemy.state = ENEMY_STATE_IDLE;
            enemy.stateTicks = 0;
            enemy.attackHitFired = false;
            enemy.lastP1HitFrame = -1000;
            enemy.lastP2HitFrame = -1000;
            enemy.lastTeamComboFrame = -1000;
            enemy.defeated = false;
            enemy.z = enemy.vx = enemy.vy = enemy.vz = 0f;
            enemy.animator.clear();
            Bitmap atlas = enemyAnimArt[type];
            if (atlas != null) {
                enemy.animator.bind(atlas, ENEMY_ANIM_COLUMNS, ENEMY_ANIM_ROWS,
                        ENEMY_ANIM_CELL_WIDTH, ENEMY_ANIM_CELL_HEIGHT);
                enemy.animator.play(ENEMY_IDLE, 6, 8, true, true);
            }
            return;
        }
    }

    private void updateGame() {
        int p1 = safeHeroIndex(selectedHero);
        int p2 = safeHeroIndex(selectedHero2);
        if (pauseForDisconnectedController()) return;
        stageFrames++;
        if (hitStop > 0) {
            hitStop--;
            return;
        }
        if (zoneBanner > 0) zoneBanner--;
        if (teamComboBanner > 0) teamComboBanner--;
        if (comboWindow > 0 && --comboWindow == 0) combo = 0;
        if (punchChainWindow > 0 && --punchChainWindow == 0) punchChainStep = 0;
        if (p2PunchChainWindow > 0 && --p2PunchChainWindow == 0) p2PunchChainStep = 0;
        if (invulnerable > 0) invulnerable--;
        if (p2Invulnerable > 0) p2Invulnerable--;
        if (hurtTimer > 0) hurtTimer--;
        if (p2HurtTimer > 0) p2HurtTimer--;
        if (knockoutTimer > 0) knockoutTimer--;
        if (shakeFrames > 0) shakeFrames--;

        captureBufferedAction();

        float horizontal = moveX + (keyRight ? 1f : 0f) - (keyLeft ? 1f : 0f);
        float vertical = moveY + (keyDown ? 1f : 0f) - (keyUp ? 1f : 0f);
        float length = (float) Math.sqrt(horizontal * horizontal + vertical * vertical);
        if (length > 1f) {
            horizontal /= length;
            vertical /= length;
        }

        boolean airControl = playerZ > 0f && attackTimer > 0;
        if (hurtTimer == 0 && (attackTimer == 0 || airControl)) {
            float speed = HERO_SPEED[p1] * (dashHeld ? 1.55f : 1f);
            if (airControl) speed *= 0.62f;
            playerX += horizontal * speed;
            playerY += vertical * speed * 0.72f;
            if (Math.abs(horizontal) > 0.15f) facingRight = horizontal > 0;
        }
        playerX += playerVx;
        playerY += playerVy;
        playerVx *= playerZ > 0f ? 0.94f : 0.80f;
        playerVy *= playerZ > 0f ? 0.92f : 0.76f;
        playerX = clamp(playerX, 35f, WORLD_END);
        playerY = clamp(playerY, 218f, 320f);

        if (playerZ > 0f || jumpVelocity != 0f) {
            playerZ += jumpVelocity;
            jumpVelocity -= 0.42f;
            if (playerZ <= 0f) {
                playerZ = 0f;
                jumpVelocity = 0f;
                spawnDust(playerX, playerY, HERO_COLORS[p1], 5);
            }
        }

        consumeBufferedAction();
        updatePlayerAnimation(horizontal, vertical);
        if (twoPlayerMode) updatePlayerTwo();
        if (twoPlayerMode) updateCoopRevives();
        updateAssist();

        updateEncounter();
        updateEnemies();
        updateItems();
        updateWorldObjects();
        updateSpriteEffects();
        float focusX = twoPlayerMode ? (playerX + player2X) * 0.5f : playerX;
        cameraX += (clamp(focusX - 210f, 0f, WORLD_END - W + 100f) - cameraX) * 0.1f;
        // Streets-of-Rage-style frame lock: neither player may leave the visible frame.
        float frameLeft = Math.max(35f, cameraX + 18f);
        float frameRight = Math.min(WORLD_END, cameraX + W - 18f);
        playerX = clamp(playerX, frameLeft, frameRight);
        if (twoPlayerMode) {
            player2X = clamp(player2X, frameLeft, frameRight);
            // Leash: P2 may never range far ahead of (or behind) P1.
            player2X = clamp(player2X, playerX - 250f, playerX + 250f);
        }
        if (lastHitEnemyTicks > 0 && --lastHitEnemyTicks == 0) lastHitEnemy = null;

        if (health <= 0) {
            health = 0;
            if ((!twoPlayerMode || p2Health <= 0) && knockoutTimer == 0) {
                enterState(GAME_OVER);
                clearInputs();
            }
        }
    }

    private void updateCoopRevives() {
        float playerDistance = distance(playerX, playerY, player2X, player2Y);
        if (health <= 0 && p2Health > 0 && playerDistance <= 58f && p2AttackTimer == 0) {
            p1ReviveProgress = Math.min(120, p1ReviveProgress + 1);
            if (p1ReviveProgress >= 120) {
                health = Math.max(1, Math.round(maxHealth * 0.35f));
                invulnerable = 120;
                knockoutTimer = 0;
                p1ReviveProgress = 0;
                spawnRing(playerX, playerY - 38f, HERO_COLORS[safeHeroIndex(selectedHero)]);
                audio.play(AudioController.VICTORY);
            }
        } else if (health > 0 || playerDistance > 72f) {
            p1ReviveProgress = 0;
        }
        if (p2Health <= 0 && health > 0 && playerDistance <= 58f && attackTimer == 0) {
            p2ReviveProgress = Math.min(120, p2ReviveProgress + 1);
            if (p2ReviveProgress >= 120) {
                p2Health = Math.max(1, Math.round(
                        safeHeroMaxHealth(safeHeroIndex(selectedHero2)) * 0.35f));
                p2Invulnerable = 120;
                p2ReviveProgress = 0;
                player2Animator.play(HERO_IDLE, HERO_ANIM_COLUMNS, 8, true, true);
                spawnRing(player2X, player2Y - 38f, HERO_COLORS[safeHeroIndex(selectedHero2)]);
                audio.play(AudioController.VICTORY);
            }
        } else if (p2Health > 0 || playerDistance > 72f) {
            p2ReviveProgress = 0;
        }
    }

    private boolean pauseForDisconnectedController() {
        boolean primaryLost = primaryControllerId >= 0
                && !isControllerIdConnected(primaryControllerId);
        boolean secondaryLost = twoPlayerMode && secondaryControllerId >= 0
                && !isControllerIdConnected(secondaryControllerId);
        if (!primaryLost && !secondaryLost) return false;
        primaryControllerId = primaryLost ? -1 : primaryControllerId;
        secondaryControllerId = secondaryLost ? -1 : secondaryControllerId;
        lastPrimaryControllerInputMs = primaryLost ? -1L : lastPrimaryControllerInputMs;
        lastSecondaryControllerInputMs = secondaryLost ? -1L : lastSecondaryControllerInputMs;
        clearInputs();
        enterState(PAUSE);
        return true;
    }

    private void updatePlayerTwo() {
        int p2 = safeHeroIndex(selectedHero2);
        if (p2Health <= 0) {
            p2Health = 0;
            if (player2Animator.isBound() && player2Animator.row() != HERO_KNOCKDOWN) {
                player2Animator.play(HERO_KNOCKDOWN, HERO_ANIM_COLUMNS, 10, false, true);
            }
            if (player2Animator.isBound()) player2Animator.step();
            return;
        }
        if (p2HurtTimer > 0) {
            if (player2Animator.isBound() && player2Animator.row() != HERO_HURT) {
                player2Animator.play(HERO_HURT, HERO_ANIM_COLUMNS, 14, false, true);
            }
            if (player2Animator.isBound()) player2Animator.step();
            return;
        }
        float horizontal = (p2Right ? 1f : 0f) - (p2Left ? 1f : 0f);
        float vertical = (p2Down ? 1f : 0f) - (p2Up ? 1f : 0f);
        float length = (float) Math.sqrt(horizontal * horizontal + vertical * vertical);
        if (length > 1f) { horizontal /= length; vertical /= length; }
        int requested = p2LinkQueued ? ACTION_LINK : p2SpecialQueued ? ACTION_SPECIAL
                : p2ThrowQueued ? ACTION_THROW : p2JumpQueued ? ACTION_JUMP
                : p2HeavyKickQueued ? ACTION_HEAVY_KICK : p2HeavyQueued ? ACTION_HEAVY_PUNCH
                : p2KickQueued ? ACTION_KICK : p2LightQueued ? ACTION_PUNCH : ACTION_NONE;
        p2LightQueued = p2KickQueued = p2HeavyQueued = p2HeavyKickQueued = false;
        p2JumpQueued = p2SpecialQueued = p2LinkQueued = p2ThrowQueued = false;
        if (requested == ACTION_SPECIAL && p2Energy < 30) requested = ACTION_NONE;
        if (requested == ACTION_LINK && (p2Link < 50 || assist.active)) requested = ACTION_NONE;
        if (requested != ACTION_NONE && p2AttackTimer == 0) {
            p2AttackKind = requested;
            if (requested == ACTION_PUNCH || requested == ACTION_KICK) {
                p2PunchChainStep = p2PunchChainWindow > 0
                        ? p2PunchChainStep % 3 + 1 : 1;
                p2PunchChainWindow = 24;
            } else {
                p2PunchChainStep = 0;
            }
            p2AttackTimer = actionDuration(requested);
            if (requested == ACTION_SPECIAL) p2Energy -= 30;
            if (requested == ACTION_LINK) p2Link -= 50;
            if (requested == ACTION_JUMP && player2Z == 0f) player2JumpVelocity = 6.8f;
            player2Animator.play(heroRowForAction(requested), HERO_ANIM_COLUMNS,
                        requested == ACTION_SPECIAL || requested == ACTION_LINK ? 12 : 10, false, true);
            audio.play(requested == ACTION_SPECIAL || requested == ACTION_LINK
                    ? AudioController.SPECIAL : AudioController.PUNCH);
        }
        if (p2AttackTimer > 0) {
            p2AttackTimer--;
            int activeAt = Math.max(2, actionDuration(p2AttackKind) / 2);
            if (p2AttackTimer == activeAt) {
                if (p2AttackKind == ACTION_LINK) startAssist(1);
                else hitEnemiesForPlayer2();
            }
            if (p2AttackTimer == 0) {
                if (p2AttackKind == ACTION_PUNCH) p2PunchChainWindow = 24;
                player2Animator.play(HERO_IDLE, HERO_ANIM_COLUMNS, 8, true, true);
            }
        } else {
            if (!hasCompanionController() && horizontal == 0f && vertical == 0f) {
                // Companion AI: engage the nearest active enemy, otherwise shadow P1.
                Enemy aiTarget = null;
                float bestDistance = Float.MAX_VALUE;
                for (Enemy enemy : enemies) {
                    if (!enemy.alive || !enemy.active || enemy.defeated) continue;
                    float distance = Math.abs(enemy.x - player2X);
                    if (distance < 300f && distance < bestDistance) {
                        bestDistance = distance;
                        aiTarget = enemy;
                    }
                }
                if (p2AiCooldown > 0) p2AiCooldown--;
                float tx;
                float ty;
                if (aiTarget != null) {
                    tx = aiTarget.x + (aiTarget.x > player2X ? -44f : 44f);
                    ty = aiTarget.y;
                    if (Math.abs(aiTarget.x - player2X) < 62f
                            && Math.abs(aiTarget.y - player2Y) < 40f && p2AiCooldown == 0) {
                        p2FacingRight = aiTarget.x > player2X;
                        p2LightQueued = true;
                        p2AiCooldown = 34 + random.nextInt(28);
                    }
                } else {
                    tx = playerX + (facingRight ? -52f : 52f);
                    ty = clamp(playerY + 24f, 218f, 320f);
                }
                if (Math.abs(tx - player2X) > 14f) horizontal = tx > player2X ? 1f : -1f;
                if (Math.abs(ty - player2Y) > 10f) vertical = ty > player2Y ? 1f : -1f;
            }
            player2X += horizontal * HERO_SPEED[p2];
            player2Y += vertical * HERO_SPEED[p2] * 0.72f;
            player2X = clamp(player2X, 35f, WORLD_END);
            player2Y = clamp(player2Y, 218f, 320f);
            if (Math.abs(horizontal) > 0.15f) p2FacingRight = horizontal > 0f;
            if (Math.abs(horizontal) + Math.abs(vertical) > 0.15f) {
                player2Animator.play(HERO_WALK, HERO_ANIM_COLUMNS, 8, true, false);
            } else {
                player2Animator.play(HERO_IDLE, HERO_ANIM_COLUMNS, 8, true, false);
            }
        }
        if (player2Z > 0f || player2JumpVelocity != 0f) {
            player2Z += player2JumpVelocity;
            player2JumpVelocity -= 0.42f;
            if (player2Z <= 0f) { player2Z = 0f; player2JumpVelocity = 0f; }
        }
        // P2 owns an independent animator. Its clip was selected above, but it
        // also has to advance once per fixed 60 Hz simulation tick. Without
        // this step P2 remained forever on frame zero while still moving.
        if (player2Animator.isBound()) player2Animator.step();
    }

    private void navigateMenu(int horizontal, int vertical, boolean playerTwo) {
        if (state == TITLE) return;
        if (state == SELECT && horizontal != 0) {
            if (playerTwo) {
                selectedHero2 = sanitizeHeroIndex(selectedHero2 + (horizontal > 0 ? 1 : -1));
            } else {
                selectedHero = sanitizeHeroIndex(selectedHero + (horizontal > 0 ? 1 : -1));
            }
            return;
        }
        moveMenuCursor(horizontal, vertical);
    }

    private float attackReach(int action, int chainStep) {
        MoveSpec spec = moveSpec(action);
        return spec.reach + (action == ACTION_PUNCH ? Math.max(0, chainStep - 1) * 7f : 0f);
    }

    private float attackLaneHalfHeight(int action) {
        return moveSpec(action).laneHalfHeight;
    }

    private float enemyHurtHalfWidth(int type) {
        return type == 3 ? 34f : type == 2 ? 27f : 20f;
    }

    private float enemyHurtLaneHalfHeight(int type) {
        return type == 3 ? 22f : type == 2 ? 19f : 16f;
    }

    private boolean attackBoxOverlapsEnemy(float attackerX, float attackerY,
                                           boolean attackerFacesRight, int action,
                                           int chainStep, Enemy enemy) {
        float reach = attackReach(action, chainStep);
        float rear = action == ACTION_SPECIAL || action == ACTION_LINK ? reach : 12f;
        float left = attackerFacesRight ? attackerX - rear : attackerX - reach;
        float right = attackerFacesRight ? attackerX + reach : attackerX + rear;
        float lane = attackLaneHalfHeight(action);
        return right >= enemy.x - enemyHurtHalfWidth(enemy.type)
                && left <= enemy.x + enemyHurtHalfWidth(enemy.type)
                && attackerY + lane >= enemy.y - enemyHurtLaneHalfHeight(enemy.type)
                && attackerY - lane <= enemy.y + enemyHurtLaneHalfHeight(enemy.type)
                && (action != ACTION_AIR_ATTACK || Math.abs(playerZ - enemy.z) <= 72f);
    }

    private void hitEnemiesForPlayer2() {
        int p2 = safeHeroIndex(selectedHero2);
        MoveSpec spec = moveSpec(p2AttackKind);
        float damage = 13f * HERO_POWER[p2] * spec.damageMultiplier;
        if (p2AttackKind == ACTION_PUNCH) {
            damage *= p2PunchChainStep == 3 ? 1.45f : p2PunchChainStep == 2 ? 1.16f : 1f;
        }
        if (p2AttackKind == ACTION_KICK) {
            damage *= p2PunchChainStep == 3 ? 1.37f : p2PunchChainStep == 2 ? 1.09f : 1f;
        }
        boolean hit = false;
        for (Enemy enemy : enemies) {
            if (!enemy.alive || !enemy.active || enemy.defeated) continue;
            if (!attackBoxOverlapsEnemy(player2X, player2Y, p2FacingRight,
                    p2AttackKind, p2PunchChainStep, enemy)) continue;
            damageEnemy(enemy, Math.round(damage), p2FacingRight ? 1f : -1f,
                    spec.launches);
            enemy.lastP2HitFrame = stageFrames;
            if (stageFrames - enemy.lastP1HitFrame <= 24) triggerTeamCombo(enemy);
            spawnHit(enemy.x, enemy.y - 48f, HERO_COLORS[p2]);
            p2Energy = Math.min(100, p2Energy + 2);
            p2Link = Math.min(100, p2Link + 4);
            hit = true;
        }
        if (hit) {
            hitStop = spec.hitPauseTicks;
            shakeFrames = shakeEnabled ? 6 : 0;
        }
    }

    private void captureBufferedAction() {
        int requested = ACTION_NONE;
        if (assistQueued) requested = ACTION_LINK;
        else if (specialQueued) requested = ACTION_SPECIAL;
        else if (throwQueued) requested = ACTION_THROW;
        else if (jumpQueued) requested = ACTION_JUMP;
        else if (heavyKickQueued) requested = ACTION_HEAVY_KICK;
        else if (heavyQueued) requested = ACTION_HEAVY_PUNCH;
        else if (kickQueued) requested = ACTION_KICK;
        else if (lightQueued) {
            if (attackTimer == 0 && playerZ == 0f && heldWeaponType < 0
                    && tryPickupNearbyWeapon(PICKUP_PROMPT_X, PICKUP_PROMPT_Y)) {
                requested = ACTION_NONE;
            } else {
                requested = ACTION_PUNCH;
            }
        }
        lightQueued = kickQueued = heavyQueued = heavyKickQueued = false;
        jumpQueued = specialQueued = assistQueued = throwQueued = false;
        if (requested != ACTION_NONE) {
            bufferedAction = requested;
            bufferedActionTicks = 8;
        } else if (bufferedActionTicks > 0 && --bufferedActionTicks == 0) {
            bufferedAction = ACTION_NONE;
        }
    }

    private boolean canCancelCurrentAction() {
        if (attackTimer <= 0) return true;
        int frame = playerAnimator.frame();
        return (attackKind == ACTION_PUNCH || attackKind == ACTION_KICK) && frame >= 5
                || (attackKind == ACTION_HEAVY_PUNCH || attackKind == ACTION_HEAVY_KICK
                || attackKind == ACTION_WEAPON) && frame >= 6;
    }

    private void consumeBufferedAction() {
        if (bufferedAction == ACTION_NONE || hurtTimer > 0 || health <= 0) return;
        int requested = bufferedAction;
        dashAttackActive = false;
        if (requested == ACTION_PUNCH && dashHeld && playerZ == 0f) {
            requested = ACTION_HEAVY_PUNCH;
            dashAttackActive = true;
            playerVx = (facingRight ? 1f : -1f) * 5.8f;
        }
        if (requested == ACTION_JUMP) {
            if (playerZ == 0f && attackTimer == 0) {
                jumpVelocity = 7.2f;
                playerZ = 0.1f;
                playerAnimator.play(HERO_JUMP, 8, 14, false, true);
                audio.play(AudioController.JUMP);
                bufferedAction = ACTION_NONE;
                bufferedActionTicks = 0;
            }
            return;
        }
        if (actionRecoveryTicks > 0) return;
        if (attackTimer > 0 && !canCancelCurrentAction()) return;
        if (requested == ACTION_SPECIAL) {
            if (energy < 30) {
                bufferedAction = ACTION_NONE;
                return;
            }
            energy -= 30;
            invulnerable = Math.max(invulnerable, 34);
            audio.play(AudioController.SPECIAL);
        } else if (requested == ACTION_LINK) {
            if (linkMeter < 50 || assist.active) {
                bufferedAction = ACTION_NONE;
                return;
            }
            linkMeter -= 50;
            audio.play(AudioController.SPECIAL);
        } else if (requested == ACTION_THROW && heldWeaponType < 0) {
            bufferedAction = ACTION_NONE;
            return;
        }

        if (playerZ > 0f && (requested == ACTION_PUNCH || requested == ACTION_KICK
                || requested == ACTION_HEAVY_PUNCH || requested == ACTION_HEAVY_KICK)) {
            beginAttack(ACTION_AIR_ATTACK, requested == ACTION_KICK
                    || requested == ACTION_HEAVY_KICK ? HERO_KICK : HERO_PUNCH);
        } else if (requested == ACTION_HEAVY_PUNCH && heldWeaponType >= 0) {
            beginAttack(ACTION_WEAPON, HERO_HEAVY_PUNCH);
        } else {
            beginAttack(requested, heroRowForAction(requested));
        }
        bufferedAction = ACTION_NONE;
        bufferedActionTicks = 0;
    }

    private int heroRowForAction(int action) {
        if (action == ACTION_PUNCH) return HERO_PUNCH;
        if (action == ACTION_KICK) return HERO_KICK;
        if (action == ACTION_HEAVY_PUNCH || action == ACTION_WEAPON
                || action == ACTION_THROW) return HERO_HEAVY_PUNCH;
        if (action == ACTION_HEAVY_KICK) return HERO_HEAVY_KICK;
        if (action == ACTION_SPECIAL) return HERO_SPECIAL;
        if (action == ACTION_LINK) return HERO_LINK;
        return HERO_IDLE;
    }

    private int actionFps(int action) {
        return moveSpec(action).fps;
    }

    private int actionDuration(int action) {
        int fps = actionFps(action);
        return (8 * 60 + fps - 1) / fps + 2;
    }

    private int hitFrameForAction(int action) {
        return moveSpec(action).hitFrame;
    }

    private MoveSpec moveSpec(int action) {
        return MOVE_SPECS[clampInt(action, ACTION_NONE, ACTION_THROW)];
    }

    private boolean isPlayerAttackBoxActive() {
        if (attackTimer <= 0) return false;
        if (playerAnimator.isBound()) {
            return playerAnimator.frame() == hitFrameForAction(attackKind);
        }
        int elapsed = actionDuration(attackKind) - attackTimer;
        int activeTick = Math.max(3, Math.round((hitFrameForAction(attackKind) + 0.5f)
                * 60f / actionFps(attackKind)));
        return Math.abs(elapsed - activeTick) <= 1;
    }

    private void beginAttack(int kind, int animationRow) {
        int hero = safeHeroIndex(selectedHero);
        attackKind = kind;
        if (kind == ACTION_PUNCH || kind == ACTION_KICK) {
            punchChainStep = punchChainWindow > 0 ? punchChainStep % 3 + 1 : 1;
            punchChainWindow = 24;
        } else {
            punchChainStep = 0;
        }
        attackSerial++;
        actionHitFired = false;
        actionObjectFired = false;
        actionRecoveryTicks = 0;
        attackTimer = actionDuration(kind);
        playerAnimator.play(animationRow, 8, actionFps(kind), false, true);
        if (kind == ACTION_SPECIAL) {
            spawnRing(playerX, playerY - 32, HERO_COLORS[hero]);
        }
    }

    private void updatePlayerAnimation(float horizontal, float vertical) {
        if (health <= 0) {
            if (playerAnimator.isBound() && playerAnimator.row() != HERO_KNOCKDOWN) {
                attackKind = ACTION_NONE;
                attackTimer = 0;
                playerAnimator.play(HERO_KNOCKDOWN, 8, 10, false, true);
            }
            playerAnimator.step();
            return;
        }
        if (hurtTimer > 0) {
            if (playerAnimator.row() != HERO_HURT) {
                attackKind = ACTION_NONE;
                attackTimer = 0;
                playerAnimator.play(HERO_HURT, 8, 14, false, true);
            }
            playerAnimator.step();
            return;
        }
        if (attackTimer > 0) {
            playerAnimator.step();
            int hitFrame = hitFrameForAction(attackKind);
            boolean atlasEvent = playerAnimator.isBound() && playerAnimator.enteredFrame(hitFrame);
            int elapsed = actionDuration(attackKind) - attackTimer;
            int fallbackEventTick = Math.max(3, Math.round((hitFrame + 0.5f) * 60f
                    / actionFps(attackKind)));
            if (!actionHitFired && (atlasEvent || !playerAnimator.isBound()
                    && elapsed >= fallbackEventTick)) {
                actionHitFired = true;
                if (attackKind == ACTION_THROW) throwHeldWeapon();
                else if (attackKind == ACTION_LINK) startAssist(0);
                else {
                    if (attackKind == ACTION_SPECIAL) {
                        spawnSpriteEffect(specialFxArt, 4, 2, 8,
                                playerX, playerY - 48f, 0f, 1.35f);
                    } else if (attackKind == ACTION_WEAPON) {
                        spawnWeaponTrailEffect(
                                playerX + (facingRight ? 48f : -48f),
                                playerY - 54f, 0f, 0.82f);
                    }
                    resolvePlayerAttack();
                }
            }
            if ((attackKind == ACTION_PUNCH || attackKind == ACTION_KICK
                    || attackKind == ACTION_HEAVY_PUNCH || attackKind == ACTION_HEAVY_KICK
                    || attackKind == ACTION_WEAPON) && playerAnimator.frame() >= 2
                    && playerAnimator.frame() <= hitFrame) {
                playerX += (facingRight ? 1f : -1f)
                        * (attackKind == ACTION_PUNCH ? 0.55f : 0.82f);
            }
            attackTimer--;
            if (attackTimer <= 0 || playerAnimator.isBound() && playerAnimator.finished()) {
                if (attackKind == ACTION_PUNCH) punchChainWindow = 24;
                int completedAction = attackKind;
                attackTimer = 0;
                attackKind = ACTION_NONE;
                actionRecoveryTicks = moveSpec(completedAction).recoveryTicks;
            }
            return;
        }
        if (actionRecoveryTicks > 0) actionRecoveryTicks--;
        if (playerZ > 0f) {
            if (playerAnimator.row() != HERO_JUMP || playerAnimator.finished()) {
                playerAnimator.play(HERO_JUMP, 8, 14, false, true);
            }
        } else if (Math.abs(horizontal) + Math.abs(vertical) > 0.15f) {
            playerAnimator.play(HERO_WALK, 8, dashHeld ? 16 : 12, true, false);
        } else {
            playerAnimator.play(HERO_IDLE, 8, 8, true, false);
        }
        playerAnimator.step();
    }

    private void autoFaceNearestEnemy(float range) {
        float best = Float.MAX_VALUE;
        float bestDx = 0f;
        for (Enemy enemy : enemies) {
            if (!enemy.alive || !enemy.active) continue;
            float dx = enemy.x - playerX;
            if (Math.abs(dx) <= range + 26f && Math.abs(enemy.y - playerY) <= 48f
                    && Math.abs(dx) < best) {
                best = Math.abs(dx);
                bestDx = dx;
            }
        }
        if (best != Float.MAX_VALUE && Math.abs(bestDx) > 6f) facingRight = bestDx > 0;
    }

    private void resolvePlayerAttack() {
        int hero = safeHeroIndex(selectedHero);
        float range = attackReach(attackKind, punchChainStep);
        MoveSpec spec = moveSpec(attackKind);
        float damage = 15f * HERO_POWER[hero] * spec.damageMultiplier;
        if (attackKind == ACTION_PUNCH) {
            damage *= punchChainStep == 3 ? 1.5f : punchChainStep == 2 ? 1.18f : 1f;
        }
        if (attackKind == ACTION_KICK) {
            damage *= punchChainStep == 3 ? 1.41f : punchChainStep == 2 ? 1.11f : 1f;
        }
        if (attackKind == ACTION_WEAPON) damage *= weaponDamageMultiplier(heldWeaponType);
        if (attackKind != ACTION_SPECIAL) autoFaceNearestEnemy(range);
        boolean hit = false;
        for (Enemy enemy : enemies) {
            if (!enemy.alive || !enemy.active || enemy.lastHitSerial == attackSerial) continue;
            if (attackBoxOverlapsEnemy(playerX, playerY, facingRight,
                    attackKind, punchChainStep, enemy)) {
                enemy.lastHitSerial = attackSerial;
                damageEnemy(enemy, Math.round(damage), facingRight ? 1f : -1f,
                        spec.launches);
                enemy.lastP1HitFrame = stageFrames;
                if (twoPlayerMode && stageFrames - enemy.lastP2HitFrame <= 24) {
                    triggerTeamCombo(enemy);
                }
                hit = true;
                totalHits++;
                combo = comboWindow > 0 ? Math.min(99, combo + 1) : 1;
                comboWindow = 72;
                score += 90 + combo * 25;
                energy = Math.min(100, energy + 2);
                linkMeter = Math.min(100, linkMeter + 3);
                spawnHit(enemy.x, enemy.y - enemyHeight(enemy.type) * 0.45f,
                        attackKind == ACTION_SPECIAL ? Color.rgb(217, 255, 85) : HERO_COLORS[hero]);
                spawnSpriteEffect(hitFxArt, 4, 4, 16, enemy.x,
                        enemy.y - enemyHeight(enemy.type) * 0.48f, 0f, 0.62f);
            }
        }
        hit |= hitWorldObjects(range, damage);
        if (hit) {
            audio.play(AudioController.PUNCH);
            hitStop = spec.hitPauseTicks;
            shakeFrames = shakeEnabled ? (attackKind == ACTION_SPECIAL ? 12 : 6) : 0;
            if (hapticsEnabled) performHapticFeedback(HapticFeedbackConstants.CONTEXT_CLICK);
            if (heldWeaponType >= 0 && attackKind == ACTION_WEAPON
                    && --weaponDurability <= 0) {
                dropHeldWeapon(true);
            }
        }
    }

    private float weaponDamageMultiplier(int type) {
        if (type == WEAPON_PIPE) return 2.05f;
        if (type == WEAPON_MALLET) return 2.55f;
        if (type == WEAPON_SIGN) return 2.2f;
        if (type == WEAPON_CONE) return 1.35f;
        return 1.85f;
    }

    private void triggerTeamCombo(Enemy enemy) {
        if (enemy.lastTeamComboFrame >= 0 && stageFrames - enemy.lastTeamComboFrame < 30) return;
        enemy.lastTeamComboFrame = stageFrames;
        int bonusDamage = Math.round(8f * (HERO_POWER[safeHeroIndex(selectedHero)]
                + HERO_POWER[safeHeroIndex(selectedHero2)]));
        damageEnemy(enemy, bonusDamage, enemy.x >= (playerX + player2X) * 0.5f ? 1f : -1f, true);
        teamComboBanner = 90;
        teamComboCount++;
        combo = Math.min(99, Math.max(2, combo + 1));
        comboWindow = 90;
        score += 350 + teamComboCount * 25;
        linkMeter = Math.min(100, linkMeter + 5);
        p2Link = Math.min(100, p2Link + 5);
        hitStop = Math.max(hitStop, 5);
        shakeFrames = shakeEnabled ? Math.max(shakeFrames, 10) : 0;
        spawnRing(enemy.x, enemy.y - 45f, Color.rgb(217, 255, 85));
        spawnSpriteEffect(specialFxArt, 4, 2, 8,
                enemy.x, enemy.y - 48f, enemy.z, 0.75f);
    }

    private void damageEnemy(Enemy enemy, int damage, float direction, boolean launch) {
        enemy.hp -= damage;
        lastHitEnemy = enemy;
        lastHitEnemyTicks = 180;
        enemy.flash = 6;
        enemy.attackTimer = 0;
        enemy.attackHitFired = false;
        enemy.vx += direction * (launch ? 3.9f : 2.2f);
        enemy.vy += (enemy.y < playerY ? -0.45f : 0.45f);
        if (launch) enemy.vz = Math.max(enemy.vz, 3.5f);
        enemy.stun = launch ? 42 : 24;
        setEnemyState(enemy, launch || enemy.hp <= 0
                ? ENEMY_STATE_KNOCKDOWN : ENEMY_STATE_HURT, true);
        if (enemy.hp <= 0) {
            enemy.hp = 0;
            enemy.defeated = true;
            enemy.stun = Math.max(enemy.stun, 48);
        }
    }

    private boolean hitWorldObjects(float range, float damage) {
        boolean hit = false;
        for (WorldObject object : worldObjects) {
            if (!object.active || object.held || object.z > 52f
                    || object.lastHitSerial == attackSerial) continue;
            float dx = object.x - playerX;
            if (!(attackKind == ACTION_SPECIAL)
                    && (facingRight ? dx < -14f : dx > 14f)) continue;
            if (Math.abs(dx) > range + 18f || Math.abs(object.y - playerY) > 38f) continue;
            object.lastHitSerial = attackSerial;
            float direction = attackKind == ACTION_SPECIAL
                    ? Math.signum(dx == 0 ? (facingRight ? 1f : -1f) : dx)
                    : facingRight ? 1f : -1f;
            object.vx += direction * (object.type >= PROP_CRATE ? 2.8f : 5.2f);
            object.vy += (object.y < playerY ? -1f : 1f) * 0.65f;
            object.vz = Math.max(object.vz, object.type >= PROP_CRATE ? 2.4f : 4.6f);
            object.angularVelocity += direction * (object.type >= PROP_CRATE ? 3f : 12f);
            if (object.type < PROP_CRATE && !object.thrown) {
                object.throwSerial = ++worldObjectSerial;
                object.thrown = true;
            }
            if (object.type >= PROP_CRATE) {
                object.hp -= Math.max(1, Math.round(damage * 0.65f));
                if (object.hp <= 0) breakWorldObject(object);
            }
            hit = true;
        }
        return hit;
    }

    private void setEnemyState(Enemy enemy, int nextState, boolean restart) {
        if (!restart && enemy.state == nextState) return;
        enemy.state = nextState;
        enemy.stateTicks = 0;
        int row = ENEMY_IDLE;
        int fps = 8;
        boolean loop = true;
        if (nextState == ENEMY_STATE_WALK) {
            row = ENEMY_WALK;
            fps = enemy.type == 1 ? 15 : 11;
        } else if (nextState == ENEMY_STATE_ATTACK) {
            row = enemy.attackVariant == 0 ? ENEMY_ATTACK_1 : ENEMY_ATTACK_2;
            fps = enemy.type == 3 ? 11 : 14;
            loop = false;
        } else if (nextState == ENEMY_STATE_HURT) {
            row = ENEMY_HURT;
            fps = 15;
            loop = false;
        } else if (nextState == ENEMY_STATE_KNOCKDOWN) {
            row = ENEMY_KNOCKDOWN;
            fps = 10;
            loop = false;
        }
        enemy.animator.play(row, 6, fps, loop, true);
    }

    private void defeatEnemy(Enemy enemy) {
        enemy.active = false;
        enemy.alive = false;
        score += enemy.type == 3 ? 3000 : enemy.type == 2 ? 650 : 350;
        spawnDust(enemy.x, enemy.y - 24, Color.rgb(217, 255, 85), enemy.type == 3 ? 20 : 10);
        spawnBreakEffect(enemy.x, enemy.y - 54f, 0f,
                enemy.type == 3 ? 1.2f : 0.78f);
    }

    private void updateEncounter() {
        if (!zoneActive && zone < ZONE_TRIGGERS.length && playerX >= ZONE_TRIGGERS[zone]) {
            zoneActive = true;
            zoneBanner = 100;
            prepareEnemyAnimationsForZone(zone);
            for (Enemy enemy : enemies) {
                if (enemy.alive && enemy.zone == zone) enemy.active = true;
            }
        }
        if (zoneActive) {
            // Decode at most one missing enemy atlas per simulation tick. This
            // avoids the first-encounter allocation/GPU-upload burst that can
            // kill low-memory Android TV processes before enemies appear.
            prepareEnemyAnimationsForZone(zone);
            playerX = Math.min(playerX, ZONE_TRIGGERS[zone] + 405f);
            boolean any = false;
            for (Enemy enemy : enemies) {
                if (enemy.alive && enemy.zone == zone) {
                    any = true;
                    break;
                }
            }
            if (!any) {
                dropZoneRewards(zone);
                zone++;
                zoneActive = false;
                zoneBanner = 110;
                health = Math.min(maxHealth, health + 8);
                linkMeter = Math.min(100, linkMeter + 15);
                if (zone >= ZONE_TRIGGERS.length) finishStage();
                else saveCheckpoint(zone);
            }
        }
    }

    private void dropZoneRewards(int clearedZone) {
        float x = playerX + 70f;
        spawnItem(clearedZone == 1 ? ITEM_BAT : ITEM_FOOD, x, playerY - 18f);
        spawnItem(clearedZone == 2 ? ITEM_TOKEN : ITEM_ENERGY, x + 55f, playerY + 22f);
    }

    private void spawnItem(int type, float x, float y) {
        for (Item item : items) {
            if (item.active) continue;
            item.active = true;
            item.type = type;
            item.x = x;
            item.y = y;
            item.z = 30f;
            item.vx = random.nextFloat() * 1.4f - 0.7f;
            item.vy = random.nextFloat() * 0.8f - 0.4f;
            item.vz = 2.8f;
            item.life = 60 * 22;
            return;
        }
    }

    private void updateItems() {
        for (Item item : items) {
            if (!item.active) continue;
            item.x += item.vx;
            item.y += item.vy;
            if (item.z > 0f || item.vz != 0f) {
                item.z += item.vz;
                item.vz -= 0.36f;
                if (item.z <= 0f) {
                    item.z = 0f;
                    if (Math.abs(item.vz) > 1.25f) item.vz = -item.vz * 0.34f;
                    else item.vz = 0f;
                }
            }
            item.vx *= 0.94f;
            item.vy *= 0.92f;
            if (--item.life <= 0) {
                item.active = false;
                continue;
            }
            if (Math.abs(item.x - playerX) < 34f && Math.abs(item.y - playerY) < 28f) {
                collectItem(item);
            }
        }
    }

    private void collectItem(Item item) {
        item.active = false;
        if (item.type == ITEM_FOOD) health = Math.min(maxHealth, health + 35);
        else if (item.type == ITEM_ENERGY) energy = Math.min(100, energy + 45);
        else if (item.type == ITEM_TOKEN) {
            score += 1000;
            linkMeter = Math.min(100, linkMeter + 30);
        } else {
            if (heldWeaponType >= 0) dropHeldWeapon(false);
            heldWeaponType = WEAPON_BAT;
            weaponDurability = weaponDurabilityFor(heldWeaponType);
        }
        audio.play(AudioController.PICKUP);
        spawnRing(item.x, item.y - 15, Color.rgb(217, 255, 85));
    }

    private int weaponDurabilityFor(int type) {
        if (type == WEAPON_MALLET) return 8;
        if (type == WEAPON_SIGN) return 7;
        if (type == WEAPON_CONE) return 2;
        if (type == WEAPON_PIPE) return 12;
        return 10;
    }

    private WorldObject spawnWorldObject(int type, float x, float y) {
        for (WorldObject object : worldObjects) {
            if (object.active) continue;
            object.active = true;
            object.held = false;
            object.thrown = false;
            object.type = type;
            object.x = x;
            object.y = y;
            object.z = 0f;
            object.vx = object.vy = object.vz = 0f;
            object.angle = type == WEAPON_SIGN ? -8f : 0f;
            object.angularVelocity = 0f;
            object.hp = type == PROP_CRATE ? 56 : type == PROP_TRASH_CAN ? 72 : 1;
            object.durability = type < PROP_CRATE ? weaponDurabilityFor(type) : 0;
            object.lastHitSerial = -1;
            object.throwSerial = ++worldObjectSerial;
            object.life = -1;
            return object;
        }
        return null;
    }

    private void updateWorldObjects() {
        for (WorldObject object : worldObjects) {
            if (!object.active || object.held) continue;
            if (object.life > 0 && --object.life == 0) {
                object.active = false;
                continue;
            }
            object.x += object.vx;
            object.y += object.vy;
            if (object.z > 0f || object.vz != 0f) {
                object.z += object.vz;
                object.vz -= 0.38f;
                if (object.z <= 0f) {
                    float impact = Math.abs(object.vz);
                    object.z = 0f;
                    if (impact > 1.55f) {
                        object.vz = impact * 0.34f;
                        spawnDust(object.x, object.y, Color.rgb(176, 205, 215), 3);
                    } else {
                        object.vz = 0f;
                    }
                    object.vx *= 0.72f;
                    object.vy *= 0.68f;
                    object.angularVelocity *= 0.68f;
                }
            } else {
                object.vx *= object.type >= PROP_CRATE ? 0.78f : 0.91f;
                object.vy *= object.type >= PROP_CRATE ? 0.76f : 0.89f;
            }
            object.angle += object.angularVelocity;
            object.angularVelocity *= 0.985f;
            object.x = clamp(object.x, 28f, WORLD_END + 20f);
            object.y = clamp(object.y, 218f, 322f);

            if (object.thrown) {
                resolveThrownObjectHits(object);
                if (object.z == 0f && Math.abs(object.vx) + Math.abs(object.vy) < 0.45f) {
                    object.thrown = false;
                }
            }
            if (heldWeaponType < 0) {
                tryPickupNearbyWeapon(PICKUP_AUTO_X, PICKUP_AUTO_Y);
            }
        }
    }

    private WorldObject nearestPickupWeapon(float maxX, float maxY) {
        WorldObject nearest = null;
        float nearestScore = Float.MAX_VALUE;
        for (WorldObject object : worldObjects) {
            if (!object.active || object.held || object.thrown
                    || object.type >= PROP_CRATE || object.z >= 10f) continue;
            float dx = Math.abs(object.x - playerX);
            float dy = Math.abs(object.y - playerY);
            if (dx >= maxX || dy >= maxY) continue;
            float score = dx / Math.max(1f, maxX) + dy / Math.max(1f, maxY);
            if (score < nearestScore) {
                nearestScore = score;
                nearest = object;
            }
        }
        return nearest;
    }

    private boolean tryPickupNearbyWeapon(float maxX, float maxY) {
        if (heldWeaponType >= 0) return false;
        WorldObject object = nearestPickupWeapon(maxX, maxY);
        if (object == null) return false;
        heldWeaponType = object.type;
        weaponDurability = Math.max(1, object.durability);
        object.active = false;
        audio.play(AudioController.PICKUP);
        spawnRing(playerX, playerY - 28f, Color.rgb(255, 202, 75));
        return true;
    }

    private void resolveThrownObjectHits(WorldObject object) {
        float speed = Math.abs(object.vx) + Math.abs(object.vy) + Math.abs(object.vz);
        if (speed < 1.1f || object.z > 92f) return;
        for (Enemy enemy : enemies) {
            if (!enemy.alive || !enemy.active || enemy.lastObjectHitSerial == object.throwSerial) continue;
            if (Math.abs(enemy.x - object.x) > 32f || Math.abs(enemy.y - object.y) > 28f) continue;
            enemy.lastObjectHitSerial = object.throwSerial;
            int damage = Math.round(13f * weaponDamageMultiplier(object.type)
                    + Math.min(18f, speed * 2.2f));
            damageEnemy(enemy, damage, object.vx >= 0f ? 1f : -1f, true);
            spawnHit(enemy.x, enemy.y - 48f, Color.rgb(255, 211, 75));
            spawnWeaponTrailEffect(enemy.x, enemy.y - 50f, 0f, 0.7f);
            audio.play(AudioController.PUNCH);
            object.vx *= -0.42f;
            object.vy *= 0.55f;
            object.vz = Math.max(2f, Math.abs(object.vz) * 0.45f);
            object.angularVelocity *= -0.55f;
            object.durability--;
            if (object.durability <= 0) {
                spawnDust(object.x, object.y - object.z, Color.rgb(255, 202, 75), 12);
                spawnBreakEffect(object.x, object.y - object.z, 0f, 0.65f);
                object.active = false;
            }
            return;
        }

        for (WorldObject prop : worldObjects) {
            if (!prop.active || prop.type < PROP_CRATE || prop == object) continue;
            if (Math.abs(prop.x - object.x) > 34f || Math.abs(prop.y - object.y) > 30f) continue;
            prop.hp -= Math.round(8f + speed * 2f);
            prop.vx += object.vx * 0.35f;
            prop.vz = Math.max(prop.vz, 2.1f);
            object.vx *= -0.35f;
            if (prop.hp <= 0) breakWorldObject(prop);
            return;
        }
    }

    private void throwHeldWeapon() {
        if (heldWeaponType < 0 || actionObjectFired) return;
        actionObjectFired = true;
        int type = heldWeaponType;
        int durability = weaponDurability;
        heldWeaponType = -1;
        weaponDurability = 0;
        WorldObject object = spawnWorldObject(type,
                playerX + (facingRight ? 24f : -24f), playerY - 2f);
        if (object == null) return;
        object.z = Math.max(30f, playerZ + 34f);
        object.vx = (facingRight ? 1f : -1f) * (type == WEAPON_MALLET ? 5.2f : 7.1f);
        object.vy = moveY * 1.3f;
        object.vz = type == WEAPON_MALLET ? 3.6f : 4.4f;
        object.angularVelocity = (facingRight ? 1f : -1f) * 17f;
        object.thrown = true;
        object.durability = Math.max(1, durability);
        object.throwSerial = ++worldObjectSerial;
        spawnWeaponTrailEffect(object.x, object.y - object.z, 0f, 0.72f);
    }

    private void dropHeldWeapon(boolean broken) {
        if (heldWeaponType < 0) return;
        int type = heldWeaponType;
        int durability = weaponDurability;
        heldWeaponType = -1;
        weaponDurability = 0;
        if (broken) {
            spawnDust(playerX, playerY - 35f, Color.rgb(255, 199, 73), 10);
            spawnBreakEffect(playerX, playerY - 43f, 0f, 0.68f);
            return;
        }
        WorldObject object = spawnWorldObject(type, playerX, playerY + 8f);
        if (object == null) return;
        object.z = 24f;
        object.vx = facingRight ? 1.8f : -1.8f;
        object.vz = 2.2f;
        object.angularVelocity = facingRight ? 7f : -7f;
        object.durability = Math.max(1, durability);
    }

    private void breakWorldObject(WorldObject object) {
        int brokenType = object.type;
        float x = object.x;
        float y = object.y;
        object.active = false;
        spawnDust(x, y - 25f, brokenType == PROP_CRATE
                ? Color.rgb(222, 154, 78) : Color.rgb(120, 221, 216), 16);
        spawnBreakEffect(x, y - 42f, 0f, 0.92f);
        spawnItem(random.nextBoolean() ? ITEM_FOOD : ITEM_ENERGY, x, y);
        if (brokenType == PROP_CRATE && random.nextBoolean()) {
            spawnWorldObject(random.nextBoolean() ? WEAPON_PIPE : WEAPON_CONE, x + 16f, y + 4f);
        }
    }

    private void updateEnemies() {
        float enemyDamageScale = difficulty == 0 ? 0.72f : difficulty == 2 ? 1.35f : 1f;
        for (Enemy enemy : enemies) {
            if (!enemy.alive || !enemy.active) continue;
            if (enemy.flash > 0) enemy.flash--;
            enemy.stateTicks++;
            enemy.animator.step();
            updateEnemyPhysics(enemy);

            if (enemy.defeated) {
                if (enemy.stun > 0) enemy.stun--;
                if (enemy.stun <= 0 && enemy.z == 0f
                        && (!enemy.animator.isBound() || enemy.animator.finished())) {
                    defeatEnemy(enemy);
                }
                continue;
            }
            if (enemy.stun > 0) {
                enemy.stun--;
                if (enemy.stun == 0) setEnemyState(enemy, ENEMY_STATE_IDLE, true);
                continue;
            }
            if (enemy.state == ENEMY_STATE_ATTACK) {
                if (!enemy.attackHitFired && (enemy.animator.enteredFrame(3)
                        || !enemy.animator.isBound() && enemy.stateTicks == 11)) {
                    enemy.attackHitFired = true;
                    resolveEnemyAttack(enemy, enemyDamageScale);
                }
                if (enemy.animator.isBound() ? enemy.animator.finished() : enemy.stateTicks >= 24) {
                    enemy.attackCooldown = enemy.type == 1 ? 55 : 80 + random.nextInt(45);
                    setEnemyState(enemy, ENEMY_STATE_IDLE, true);
                }
                continue;
            }
            if (--enemy.attackCooldown <= 0) {
                boolean targetP2 = twoPlayerMode && p2Health > 0
                        && (health <= 0 || distance(enemy.x, enemy.y, player2X, player2Y)
                        < distance(enemy.x, enemy.y, playerX, playerY));
                float targetX = targetP2 ? player2X : playerX;
                float targetY = targetP2 ? player2Y : playerY;
                float dx = Math.abs(enemy.x - targetX);
                float dy = Math.abs(enemy.y - targetY);
                int targetSlot = targetP2 ? 1 : 0;
                int perPlayerAttackLimit = difficulty == 2 ? 2 : 1;
                boolean visibleThreat = enemy.x >= cameraX + 18f
                        && enemy.x <= cameraX + W - 18f;
                if (dx < (enemy.type == 3 ? 95f : 57f) && dy < 36f
                        && visibleThreat && countAttackingEnemies() < 2
                        && countAttackingEnemiesForTarget(targetSlot) < perPlayerAttackLimit) {
                    enemy.attackVariant = enemy.type == 3 || random.nextInt(4) == 0 ? 1 : 0;
                    enemy.attackHitFired = false;
                    enemy.attackTargetSlot = targetSlot;
                    setEnemyState(enemy, ENEMY_STATE_ATTACK, true);
                    continue;
                }
                enemy.attackCooldown = 20;
            }
            boolean targetP2 = twoPlayerMode && p2Health > 0
                    && (health <= 0 || distance(enemy.x, enemy.y, player2X, player2Y)
                    < distance(enemy.x, enemy.y, playerX, playerY));
            float dx = (targetP2 ? player2X : playerX) - enemy.x;
            float dy = (targetP2 ? player2Y : playerY) - enemy.y;
            enemy.facingRight = dx > 0;
            float typeSpeed = enemy.type == 1 ? 1.75f : enemy.type == 2 ? 0.82f : enemy.type == 3 ? 0.72f : 1.12f;
            boolean moving = false;
            if (Math.abs(dx) > 42f) {
                enemy.x += Math.signum(dx) * typeSpeed;
                moving = true;
            }
            if (Math.abs(dy) > 13f) {
                enemy.y += Math.signum(dy) * typeSpeed * 0.62f;
                moving = true;
            }
            enemy.y = clamp(enemy.y, 218f, 320f);
            setEnemyState(enemy, moving ? ENEMY_STATE_WALK : ENEMY_STATE_IDLE, false);
        }
    }

    private int countAttackingEnemies() {
        int count = 0;
        for (Enemy enemy : enemies) {
            if (enemy.alive && enemy.active && enemy.state == ENEMY_STATE_ATTACK) count++;
        }
        return count;
    }

    private int countAttackingEnemiesForTarget(int targetSlot) {
        int count = 0;
        for (Enemy enemy : enemies) {
            if (enemy.alive && enemy.active && enemy.state == ENEMY_STATE_ATTACK
                    && enemy.attackTargetSlot == targetSlot) count++;
        }
        return count;
    }

    private void updateEnemyPhysics(Enemy enemy) {
        enemy.x += enemy.vx;
        enemy.y += enemy.vy;
        if (enemy.z > 0f || enemy.vz != 0f) {
            enemy.z += enemy.vz;
            enemy.vz -= 0.36f;
            if (enemy.z <= 0f) {
                float impact = Math.abs(enemy.vz);
                enemy.z = 0f;
                if (impact > 2f && enemy.state == ENEMY_STATE_KNOCKDOWN) {
                    enemy.vz = impact * 0.22f;
                    spawnDust(enemy.x, enemy.y, Color.rgb(135, 218, 211), 4);
                } else enemy.vz = 0f;
            }
            enemy.vx *= 0.94f;
            enemy.vy *= 0.91f;
        } else {
            enemy.vx *= 0.78f;
            enemy.vy *= 0.75f;
        }
        enemy.x = clamp(enemy.x, 24f, WORLD_END + 30f);
        enemy.y = clamp(enemy.y, 218f, 320f);
    }

    private void resolveEnemyAttack(Enemy enemy, float damageScale) {
        float range = enemy.type == 3 ? 88f : enemy.type == 2 ? 62f : 48f;
        float left = enemy.facingRight ? enemy.x - 10f : enemy.x - range;
        float right = enemy.facingRight ? enemy.x + range : enemy.x + 10f;
        float laneHalf = enemy.type == 3 ? 34f : 26f;
        boolean overlapsPlayer = health > 0 && right >= playerX - 18f && left <= playerX + 18f
                && enemy.y + laneHalf >= playerY - 15f
                && enemy.y - laneHalf <= playerY + 15f;
        boolean overlapsPlayer2 = twoPlayerMode && p2Health > 0
                && right >= player2X - 18f && left <= player2X + 18f
                && enemy.y + laneHalf >= player2Y - 15f
                && enemy.y - laneHalf <= player2Y + 15f;
        if (overlapsPlayer2 && p2Invulnerable == 0 && player2Z <= 48f
                && (!overlapsPlayer || distance(enemy.x, enemy.y, player2X, player2Y)
                <= distance(enemy.x, enemy.y, playerX, playerY))) {
            damagePlayerTwo(enemy, damageScale);
            return;
        }
        if (!overlapsPlayer || invulnerable > 0 || playerZ > 48f) return;
        int damage = Math.max(1, Math.round((enemy.type == 3 ? 18 : enemy.type == 2 ? 13 : 8)
                * damageScale * (enemy.attackVariant == 1 ? 1.18f : 1f)));
        health -= damage;
        damageTaken += damage;
        // Longer window after launches so wakeup isn't an instant re-juggle.
        invulnerable = (enemy.type >= 2 || enemy.attackVariant == 1) ? 80 : 52;
        hurtTimer = health <= 0 ? 0 : 22;
        if (health <= 0) knockoutTimer = 50;
        float direction = playerX < enemy.x ? -1f : 1f;
        playerVx = direction * (enemy.type >= 2 ? 5.1f : 3.4f);
        playerVy = (playerY < enemy.y ? -1f : 1f) * 0.8f;
        if (enemy.type >= 2 || enemy.attackVariant == 1) {
            playerZ = Math.max(playerZ, 0.1f);
            jumpVelocity = 2.8f;
        }
        combo = 0;
        comboWindow = 0;
        attackKind = ACTION_NONE;
        attackTimer = 0;
        playerAnimator.play(health <= 0 ? HERO_KNOCKDOWN : HERO_HURT,
                8, health <= 0 ? 10 : 14, false, true);
        audio.play(AudioController.DAMAGE);
        shakeFrames = shakeEnabled ? 8 : 0;
        spawnHit(playerX, playerY - 48, Color.rgb(255, 80, 94));
        spawnSpriteEffect(hitFxArt, 4, 4, 16, playerX, playerY - 48f, 0f, 0.65f);
        if (hapticsEnabled) performHapticFeedback(HapticFeedbackConstants.LONG_PRESS);
    }

    private void damagePlayerTwo(Enemy enemy, float damageScale) {
        int damage = Math.max(1, Math.round((enemy.type == 3 ? 18 : enemy.type == 2 ? 13 : 8)
                * damageScale * (enemy.attackVariant == 1 ? 1.18f : 1f)));
        p2Health = Math.max(0, p2Health - damage);
        p2Invulnerable = (enemy.type >= 2 || enemy.attackVariant == 1) ? 80 : 52;
        p2HurtTimer = p2Health <= 0 ? 0 : 22;
        p2AttackKind = ACTION_NONE;
        p2AttackTimer = 0;
        player2JumpVelocity = enemy.type >= 2 || enemy.attackVariant == 1 ? 2.8f : 0f;
        if (player2JumpVelocity > 0f) player2Z = Math.max(player2Z, 0.1f);
        player2Animator.play(p2Health <= 0 ? HERO_KNOCKDOWN : HERO_HURT,
                HERO_ANIM_COLUMNS, p2Health <= 0 ? 10 : 14, false, true);
        audio.play(AudioController.DAMAGE);
        shakeFrames = shakeEnabled ? 8 : 0;
        spawnHit(player2X, player2Y - 48f, Color.rgb(255, 80, 94));
        spawnSpriteEffect(hitFxArt, 4, 4, 16, player2X, player2Y - 48f, 0f, 0.65f);
    }

    private void startAssist(int ownerSlot) {
        if (assist.active) return;
        int ownerHero = ownerSlot == 1 ? safeHeroIndex(selectedHero2) : safeHeroIndex(selectedHero);
        int companion = ownerSlot == 1
                ? sanitizeCompanionIndex(selectedCompanion2, ownerHero)
                : sanitizeCompanionIndex(selectedCompanion1, ownerHero);
        loadAssistAnimationRow(companion);
        assist.active = true;
        assist.ownerSlot = ownerSlot;
        assist.hero = companion;
        assist.phase = 0;
        assist.ticks = 0;
        assist.hitFired = false;
        assist.facingRight = ownerSlot == 1 ? p2FacingRight : facingRight;
        float ownerX = ownerSlot == 1 ? player2X : playerX;
        float ownerY = ownerSlot == 1 ? player2Y : playerY;
        assist.x = ownerX + (assist.facingRight ? -145f : 145f);
        assist.y = clamp(ownerY + 17f, 222f, 318f);
        assist.targetX = ownerX + (assist.facingRight ? 48f : -48f);
        assistAnimator.play(0, 8, 14, false, true);
        spawnRing(assist.x, assist.y - 34f, HERO_COLORS[assist.hero]);
    }

    private void updateAssist() {
        if (!assist.active) return;
        assist.ticks++;
        if (assist.phase == 0) {
            assist.x += (assist.targetX - assist.x) * 0.24f;
            if (assist.ticks >= 11) {
                assist.phase = 1;
                assist.ticks = 0;
                assistAnimator.play(0, 8, 14, false, true);
            }
            return;
        }
        if (assist.phase == 1) {
            assistAnimator.step();
            if (!assist.hitFired && (assistAnimator.enteredFrame(4)
                    || !assistAnimator.isBound() && assist.ticks >= 15)) {
                assist.hitFired = true;
                resolveAssistAttack();
            }
            if (assistAnimator.isBound() ? assistAnimator.finished() : assist.ticks >= 34) {
                assist.phase = 2;
                assist.ticks = 0;
            }
            return;
        }
        assist.x += assist.facingRight ? 7.4f : -7.4f;
        if (assist.ticks >= 21 || assist.x < cameraX - 100f || assist.x > cameraX + W + 100f) {
            assist.active = false;
        }
    }

    private void resolveAssistAttack() {
        attackSerial++;
        boolean hit = false;
        for (Enemy enemy : enemies) {
            if (!enemy.alive || !enemy.active || enemy.lastHitSerial == attackSerial) continue;
            float dx = enemy.x - assist.x;
            if (Math.abs(dx) > 126f || Math.abs(enemy.y - assist.y) > 62f) continue;
            if (assist.facingRight ? dx < -18f : dx > 18f) continue;
            enemy.lastHitSerial = attackSerial;
            damageEnemy(enemy, Math.round(24f * HERO_POWER[assist.hero]),
                    assist.facingRight ? 1f : -1f, true);
            spawnHit(enemy.x, enemy.y - 50f, HERO_COLORS[assist.hero]);
            totalHits++;
            combo = comboWindow > 0 ? Math.min(99, combo + 1) : 1;
            comboWindow = 72;
            score += 180 + combo * 30;
            if (assist.ownerSlot == 1) {
                p2Energy = Math.min(100, p2Energy + 3);
                p2Link = Math.min(100, p2Link + 2);
            } else {
                energy = Math.min(100, energy + 3);
                linkMeter = Math.min(100, linkMeter + 2);
            }
            hit = true;
        }
        spawnRing(assist.x + (assist.facingRight ? 54f : -54f),
                assist.y - 42f, HERO_COLORS[assist.hero]);
        spawnSpriteEffect(specialFxArt, 4, 2, 8,
                assist.x + (assist.facingRight ? 56f : -56f), assist.y - 47f,
                0f, 0.9f);
        if (hit) {
            audio.play(AudioController.PUNCH);
            hitStop = 4;
            shakeFrames = shakeEnabled ? 8 : 0;
        }
    }

    private void finishStage() {
        score += Math.max(0, 5000 - stageFrames / 3);
        if (health > maxHealth * 0.65f) score += 1200;
        bestScore = Math.max(bestScore, score);
        prefs.edit().putInt("best_score", bestScore).apply();
        clearCheckpoint();
        audio.play(AudioController.VICTORY);
        enterState(RESULTS);
        clearInputs();
    }

    private void clearInputs() {
        moveX = moveY = stickX = stickY = 0f;
        keyLeft = keyRight = keyUp = keyDown = false;
        lightQueued = kickQueued = heavyQueued = heavyKickQueued = false;
        jumpQueued = specialQueued = assistQueued = throwQueued = false;
        bufferedAction = ACTION_NONE;
        bufferedActionTicks = 0;
        dashHeld = false;
        leftTriggerDown = rightTriggerDown = false;
        p2LeftTriggerDown = p2RightTriggerDown = false;
        p2Left = p2Right = p2Up = p2Down = false;
        p2LightQueued = p2KickQueued = p2HeavyQueued = p2HeavyKickQueued = false;
        p2JumpQueued = p2SpecialQueued = p2LinkQueued = p2ThrowQueued = false;
        stickPointer = -1;
        Arrays.fill(buttonPointers, -1);
    }

    private void renderFrame() {
        if (!holder.getSurface().isValid()) return;
        Canvas canvas = null;
        try {
            canvas = holder.lockHardwareCanvas();
        } catch (IllegalArgumentException ignored) {
            // Surface may be recreated while the app is backgrounded.
        }
        if (canvas == null) return;
        try {
            syncUiMotion();
            canvas.drawColor(Color.rgb(5, 7, 24));
            canvas.save();
            canvas.scale(scale, scale);
            canvas.clipRect(0, 0, virtualWidth, virtualHeight);
            drawViewportExtension(canvas);
            float contentY = sceneYForState();
            canvas.save();
            canvas.translate(sceneX, contentY);
            canvas.clipRect(0, 0, W, H);
            if (shakeFrames > 0 && shakeEnabled) {
                canvas.translate((shakeFrames & 1) == 0 ? 2f : -2f,
                        (shakeFrames % 3) - 1f);
            }
            if (state == TITLE) drawTitle(canvas);
            else if (state == MENU) drawMenu(canvas);
            else if (state == SELECT) drawSelect(canvas);
            else if (state == INTRO) drawIntro(canvas);
            else if (state == PLAY || state == PAUSE) {
                drawGame(canvas);
                if (state == PAUSE) drawPause(canvas);
            } else if (state == SETTINGS) drawSettings(canvas);
            else if (state == RESULTS) drawResults(canvas);
            else if (state == GAME_OVER) drawGameOver(canvas);
            else drawGallery(canvas);
            drawStateTransition(canvas);
            canvas.restore();
            if (state == PLAY && !gamepadUiActive) drawTouchControls(canvas);
            else if (state == PAUSE && responsiveLayout != LAYOUT_COMPACT) {
                drawInactiveControlSurface(canvas);
            }
            canvas.restore();
        } finally {
            holder.unlockCanvasAndPost(canvas);
        }
    }

    private float sceneYForState() {
        return state == PLAY || state == PAUSE || state == GAME_OVER
                ? gameSceneY : menuSceneY;
    }

    private void syncUiMotion() {
        long now = SystemClock.uptimeMillis();
        if (animatedState != state) {
            animatedState = state;
            stateEnteredAt = now;
            if (state == SELECT) selectionChangedAt = now;
        }
        if (animatedHero != selectedHero) {
            animatedHero = selectedHero;
            selectionChangedAt = now;
        }
    }

    private float stateMotion(long durationMs) {
        if (!uiAnimationsEnabled) return 1f;
        return easeOut(clamp((SystemClock.uptimeMillis() - stateEnteredAt) / (float) durationMs, 0f, 1f));
    }

    private float selectionMotion(long durationMs) {
        if (!uiAnimationsEnabled) return 1f;
        return easeOut(clamp((SystemClock.uptimeMillis() - selectionChangedAt) / (float) durationMs, 0f, 1f));
    }

    private static float easeOut(float t) {
        float inverse = 1f - t;
        return 1f - inverse * inverse * inverse;
    }

    private void drawViewportExtension(Canvas canvas) {
        paint.setShader(viewportGradient);
        canvas.drawRect(0, 0, virtualWidth, virtualHeight, paint);
        paint.setShader(null);
        Bitmap scene = (state == PLAY || state == PAUSE || state == GAME_OVER) && stageBackground != null
                ? stageBackground : background;
        if (scene != null) {
            paint.setAlpha(72);
            dest.set(0, 0, virtualWidth, virtualHeight);
            canvas.drawBitmap(scene, null, dest, paint);
            paint.setAlpha(255);
        }
        paint.setColor(Color.argb(164, 5, 7, 27));
        canvas.drawRect(0, 0, virtualWidth, virtualHeight, paint);
        paint.setColor(Color.argb(110, 72, 218, 208));
        if (sceneX > 1f) {
            canvas.drawRect(sceneX - 2f, 0, sceneX, virtualHeight, paint);
            canvas.drawRect(sceneX + W, 0, sceneX + W + 2f, virtualHeight, paint);
        }
        if (virtualHeight > H + 1f) {
            float y = state == PLAY || state == PAUSE || state == GAME_OVER
                    ? gameSceneY + H : menuSceneY + H;
            paint.setColor(Color.argb(80, 217, 255, 85));
            canvas.drawRect(0, y, virtualWidth, y + 2f, paint);
        }
    }

    private void drawStateTransition(Canvas canvas) {
        if (!uiAnimationsEnabled) return;
        long elapsed = SystemClock.uptimeMillis() - stateEnteredAt;
        if (elapsed >= 280) return;
        float t = easeOut(elapsed / 280f);
        float y = -12f + (H + 24f) * t;
        paint.setColor(Color.argb(Math.round(90 * (1f - t)), 80, 235, 224));
        canvas.drawRect(0, y - 8, W, y + 8, paint);
        paint.setColor(Color.argb(Math.round(210 * (1f - t)), 217, 255, 85));
        canvas.drawRect(0, y, W, y + 2, paint);
    }

    private void drawInactiveControlSurface(Canvas canvas) {
        drawControlSurface(canvas, 88);
        text(canvas, "PAUSED  •  CONTROLS LOCKED", virtualWidth * 0.5f,
                responsiveLayout == LAYOUT_CONTROL_DECK
                        ? gameSceneY + H + 27f : 40f,
                11, Color.argb(185, 217, 255, 85), true, Paint.Align.CENTER);
    }

    private void drawBackdrop(Canvas canvas, float scroll) {
        paint.setShader(backdropGradient);
        canvas.drawRect(0, 0, W, H, paint);
        paint.setShader(null);
        Bitmap scene = (state == PLAY || state == PAUSE || state == GAME_OVER) && stageBackground != null
                ? stageBackground : background;
        if (scene != null) {
            float tileWidth = 640f;
            float base = -(scroll * 0.34f) % tileWidth;
            for (int i = -1; i < 3; i++) {
                dest.set(base + i * tileWidth, 0, base + (i + 1) * tileWidth, 360);
                canvas.save();
                if ((i & 1) != 0 && scene == stageBackground) {
                    float center = base + (i + 0.5f) * tileWidth;
                    canvas.scale(-1f, 1f, center, 0f);
                }
                canvas.drawBitmap(scene, null, dest, paint);
                canvas.restore();
            }
        } else {
            paint.setColor(Color.rgb(23, 78, 92));
            canvas.drawRect(0, 110, W, 242, paint);
            paint.setColor(Color.rgb(255, 190, 73));
            for (int i = 0; i < 8; i++) canvas.drawRect(i * 92 - scroll % 92, 150, i * 92 + 34 - scroll % 92, 220, paint);
        }
        paint.setColor(Color.argb(82, 4, 5, 25));
        canvas.drawRect(0, 0, W, H, paint);
        paint.setColor(Color.rgb(31, 35, 58));
        canvas.drawRect(0, 312, W, 360, paint);
        paint.setColor(Color.argb(100, 108, 116, 148));
        for (int i = -1; i < 14; i++) {
            float x = i * 64 - (scroll * 0.72f) % 64;
            canvas.drawRect(x, 335, x + 26, 338, paint);
        }
    }

    private void drawTitle(Canvas canvas) {
        float reveal = stateMotion(720);
        float titleScroll = uiAnimationsEnabled
                ? (SystemClock.uptimeMillis() / 52f) % 2000f : 240f;
        drawBackdrop(canvas, titleScroll);
        paint.setColor(Color.argb(200, 7, 8, 30));
        roundRect(canvas, 72, 44, 568, 290, 20, paint);
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(4);
        paint.setStrokeCap(Paint.Cap.ROUND);
        paint.setColor(Color.argb(210, 39, 208, 191));
        dest.set(78, 50, 562, 284);
        canvas.drawArc(dest, -90f, 359.5f * reveal, false, paint);
        paint.setStrokeCap(Paint.Cap.BUTT);
        paint.setStyle(Paint.Style.FILL);
        if (logo != null) {
            float logoScale = 0.90f + reveal * 0.10f;
            canvas.save();
            canvas.scale(logoScale, logoScale, W * 0.5f, 139f);
            dest.set(101, 62, 539, 226);
            pixelPaint.setAlpha(Math.round(90 + 165 * reveal));
            canvas.drawBitmap(logo, null, dest, pixelPaint);
            pixelPaint.setAlpha(255);
            canvas.restore();
        } else {
            text(canvas, customerProfile.eventTitle, W / 2f, 130, 34,
                    customerProfile.theme.accentColor, true, Paint.Align.CENTER);
        }
        text(canvas, "AN ORIGINAL FAMILY ARCADE BRAWLER", W / 2f, 221, 12,
                Color.rgb(130, 233, 226), true, Paint.Align.CENTER);
        pulseButton(canvas, 205, 236, 435, 279, "TAP TO START");
        text(canvas, "ANDROID ALPHA  •  NO ADS  •  OFFLINE", W / 2f, 335, 11,
                Color.argb(190, 255, 255, 255), false, Paint.Align.CENTER);
    }

    private void drawMenu(Canvas canvas) {
        drawBackdrop(canvas, 330f);
        paint.setColor(Color.argb(224, 6, 13, 38));
        canvas.drawRect(0, 0, W, H, paint);
        text(canvas, customerProfile.eventTitle, 28, 34, 18,
                Color.WHITE, true, Paint.Align.LEFT);
        text(canvas, "CHOOSE YOUR NIGHT ROUTE", 28, 55, 10,
                Color.rgb(144, 221, 224), true, Paint.Align.LEFT);
        paint.setColor(Color.rgb(46, 65, 102));
        canvas.drawRect(28, 65, 612, 67, paint);
        float reveal = stateMotion(430);
        canvas.save();
        canvas.translate(-20f * (1f - reveal), 0f);
        paint.setColor(Color.argb(238, 9, 19, 48));
        roundRect(canvas, 28, 82, 318, 312, 14, paint);
        paint.setColor(Color.rgb(64, 87, 123));
        canvas.drawRect(53, 103, 57, 291, paint);
        canvas.drawRect(73, 126, 300, 128, paint);
        canvas.drawRect(73, 172, 300, 174, paint);
        canvas.drawRect(73, 218, 300, 220, paint);
        canvas.drawRect(73, 264, 300, 266, paint);
        menuCard(canvas, 28, 82, 318, 124, "CONTINUE", hasCheckpoint ? "RESUME SAFE CHECKPOINT" : "NO SAVED ROUTE", MENU_ROUTE_COLORS[0], menuChoice == 0);
        menuCard(canvas, 28, 128, 318, 170, "1 PLAYER", "NEW SOLO FAMILY RUN", MENU_ROUTE_COLORS[1], menuChoice == 1);
        menuCard(canvas, 28, 174, 318, 216, "2 PLAYERS", "NEW LOCAL CO-OP TEAM", MENU_ROUTE_COLORS[2], menuChoice == 2);
        menuCard(canvas, 28, 220, 318, 262, "TRAINING", "MOVES & WEAPONS", MENU_ROUTE_COLORS[3], menuChoice == 3);
        menuCard(canvas, 28, 266, 318, 308, "SETTINGS", "SOUND & COMFORT", MENU_ROUTE_COLORS[4], menuChoice == 4);
        canvas.restore();
        canvas.save();
        canvas.translate(20f * (1f - reveal), 0f);
        int routeColor = MENU_ROUTE_COLORS[clampInt(menuChoice, 0, MENU_ROUTE_COLORS.length - 1)];
        paint.setColor(Color.argb(242, 9, 19, 48));
        roundRect(canvas, 339, 82, 612, 312, 16, paint);
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(2f);
        paint.setColor(Color.argb(220, Color.red(routeColor), Color.green(routeColor), Color.blue(routeColor)));
        roundRect(canvas, 339, 82, 612, 312, 16, paint);
        paint.setStyle(Paint.Style.FILL);
        text(canvas, menuChoice == 0 ? "SAFE CHECKPOINT" : menuChoice == 1
                        ? "SOLO DEPARTURE" : menuChoice == 2 ? "CO-OP INTERCHANGE"
                        : menuChoice == 3 ? "TRAINING DEPOT" : "CONTROL ROOM",
                365, 111, 15, Color.WHITE, true, Paint.Align.LEFT);
        text(canvas, menuChoice == 0 ? (hasCheckpoint ? "CONTINUE FROM A CLEAN ENCOUNTER" : "START A NEW ROUTE FIRST")
                        : menuChoice == 1 ? "ONE HERO + ONE LINK COMPANION"
                        : menuChoice == 2 ? "TWO HEROES • TWO COMPANIONS"
                        : menuChoice == 3 ? "SAFE PRACTICE • ALL COMMANDS"
                        : "AUDIO • TOUCH • ACCESSIBILITY",
                365, 132, 9, routeColor, true, Paint.Align.LEFT);
        drawMapRoute(canvas);
        paint.setColor(Color.argb(210, 16, 31, 65));
        roundRect(canvas, 357, 249, 594, 296, 11, paint);
        text(canvas, "BEST RUN", 372, 269, 9, Color.rgb(144, 221, 224), true, Paint.Align.LEFT);
        text(canvas, String.format(Locale.US, "%07d", bestScore), 579, 282, 21,
                Color.WHITE, true, Paint.Align.RIGHT);
        canvas.restore();
        text(canvas, "D-PAD  NAVIGATE     A / OK  SELECT     B / BACK  RETURN",
                W / 2f, 341, 9, Color.rgb(190, 207, 222), true, Paint.Align.CENTER);
    }

    private void drawMapRoute(Canvas canvas) {
        paint.setStrokeWidth(6);
        paint.setStrokeCap(Paint.Cap.ROUND);
        paint.setStyle(Paint.Style.STROKE);
        paint.setColor(Color.rgb(70, 71, 119));
        path.reset();
        if (MAP_ROUTE_X.length >= 2 && MAP_ROUTE_Y.length == MAP_ROUTE_X.length) {
            path.moveTo(MAP_ROUTE_X[0], MAP_ROUTE_Y[0]);
            for (int i = 1; i < MAP_ROUTE_X.length; i++) {
                path.lineTo(MAP_ROUTE_X[i], MAP_ROUTE_Y[i]);
            }
        } else {
            path.moveTo(382, 154);
            path.lineTo(514, 171);
            path.lineTo(577, 214);
        }
        canvas.drawPath(path, paint);
        paint.setStyle(Paint.Style.FILL);
        int routePointCount = Math.min(3, MAP_ROUTE_X.length);
        for (int i = 0; i < routePointCount; i++) {
            paint.setColor(MAP_ROUTE_COLORS[i]);
            canvas.drawCircle(MAP_ROUTE_X[i], MAP_ROUTE_Y[i], 11, paint);
            paint.setColor(Color.rgb(14, 15, 45));
            canvas.drawCircle(MAP_ROUTE_X[i], MAP_ROUTE_Y[i], 5, paint);
        }
        float route = stateMotion(760);
        float routeX = MAP_ROUTE_X.length > 0 ? MAP_ROUTE_X[0] : 382f;
        float routeY = MAP_ROUTE_Y.length > 0 ? MAP_ROUTE_Y[0] : 154f;
        if (MAP_ROUTE_X.length >= 2 && MAP_ROUTE_Y.length == MAP_ROUTE_X.length) {
            float totalDistance = 0f;
            for (int i = 0; i < MAP_ROUTE_X.length - 1; i++) {
                float sx = MAP_ROUTE_X[i + 1] - MAP_ROUTE_X[i];
                float sy = MAP_ROUTE_Y[i + 1] - MAP_ROUTE_Y[i];
                totalDistance += (float) Math.hypot(sx, sy);
            }
            float distanceTarget = totalDistance * Math.max(0f, Math.min(1f, route));
            float covered = 0f;
            for (int i = 0; i < MAP_ROUTE_X.length - 1; i++) {
                float sx = MAP_ROUTE_X[i + 1] - MAP_ROUTE_X[i];
                float sy = MAP_ROUTE_Y[i + 1] - MAP_ROUTE_Y[i];
                float segmentLength = (float) Math.hypot(sx, sy);
                if (segmentLength <= 0f) continue;
                if (covered + segmentLength >= distanceTarget) {
                    float ratio = (distanceTarget - covered) / segmentLength;
                    float clamped = Math.max(0f, Math.min(1f, ratio));
                    routeX = MAP_ROUTE_X[i] + sx * clamped;
                    routeY = MAP_ROUTE_Y[i] + sy * clamped;
                    break;
                }
                covered += segmentLength;
                routeX = MAP_ROUTE_X[i + 1];
                routeY = MAP_ROUTE_Y[i + 1];
            }
        }
        paint.setColor(Color.argb(70, 217, 255, 85));
        canvas.drawCircle(routeX, routeY, 14, paint);
        paint.setColor(Color.rgb(217, 255, 85));
        canvas.drawCircle(routeX, routeY, 5, paint);
        paint.setStrokeCap(Paint.Cap.BUTT);
    }

    private void drawSelect(Canvas canvas) {
        drawBackdrop(canvas, 620f);
        paint.setColor(Color.argb(226, 6, 13, 38));
        canvas.drawRect(0, 0, W, H, paint);
        text(canvas, twoPlayerMode ? "BUILD YOUR CO-OP LINE" : "CHOOSE YOUR HERO",
                24, 31, 19, Color.WHITE, true, Paint.Align.LEFT);
        text(canvas, twoPlayerMode ? "Both players confirm before departure"
                        : "Choose a hero and a Link companion",
                24, 51, 10, Color.rgb(144, 221, 224), true, Paint.Align.LEFT);
        paint.setColor(Color.rgb(46, 65, 102));
        canvas.drawRect(24, 62, 616, 64, paint);
        float reveal = stateMotion(380);
        int activeCard = safeHeroIndex(activeSelectionSlot == 0 ? selectedHero : selectedHero2);
        int selectedCardP1 = safeHeroIndex(selectedHero);
        int selectedCardP2 = safeHeroIndex(selectedHero2);
        canvas.save();
        canvas.translate(0f, 13f * (1f - reveal));
        for (int i = 0; i < 4; i++) drawHeroCard(canvas, i, 16 + i * 153, 72,
                i == selectedCardP1, twoPlayerMode && i == selectedCardP2);
        for (int i = 0; i < 4; i++) {
            float cx = 16f + i * 153f;
            float cy = 72f;
            if (i == activeCard) {
                paint.setColor(activeSelectionSlot == 0 ? Color.rgb(217, 255, 85) : Color.rgb(255, 197, 70));
                paint.setStyle(Paint.Style.STROKE);
                paint.setStrokeWidth(6f);
                roundRect(canvas, cx, cy, cx + 140f, cy + 175f, 15f, paint);
                paint.setStyle(Paint.Style.FILL);
            }
        }
        canvas.restore();
        drawSelectionRoute(canvas);
        drawPlayerBoard(canvas, 0, 18, 272, selectedCardP1, selectedCompanion1, p1Ready,
                activeSelectionSlot == 0);
        drawPlayerBoard(canvas, 1, 266, 272, selectedCardP2, selectedCompanion2,
                twoPlayerMode && p2Ready, activeSelectionSlot == 1);
        int readyColor = isBattleReady() ? Color.rgb(217, 255, 85) : Color.rgb(72, 88, 108);
        button(canvas, 504, 272, 622, 337, isBattleReady() ? "DEPART" : "READY",
                readyColor, Color.rgb(8, 20, 35));
        text(canvas, isBattleReady() ? "TEAM LOCKED" : twoPlayerMode
                        ? (p1Ready ? "WAITING FOR P2" : "CONFIRM P1 FIRST")
                        : "CONFIRM HERO",
                563, 356, 9, isBattleReady() ? Color.rgb(217, 255, 85)
                        : Color.rgb(183, 201, 216), true, Paint.Align.CENTER);
    }

    private void drawSelectionRoute(Canvas canvas) {
        float y = 255f;
        float[] stops = {69f, 217f, 317f, 465f, 563f};
        int[] colors = {Color.rgb(217, 255, 85), Color.rgb(63, 221, 172),
                Color.rgb(255, 192, 65), Color.rgb(83, 144, 255), Color.rgb(255, 83, 92)};
        paint.setColor(Color.rgb(67, 86, 122));
        canvas.drawRect(stops[0], y - 2f, stops[stops.length - 1], y + 2f, paint);
        for (int i = 0; i < stops.length; i++) {
            paint.setColor(colors[i]);
            canvas.drawCircle(stops[i], y, i == stops.length - 1 ? 8f : 6f, paint);
            paint.setColor(Color.rgb(7, 16, 38));
            canvas.drawCircle(stops[i], y, i == stops.length - 1 ? 3.5f : 2.5f, paint);
        }
        text(canvas, "P1", stops[0], 267, 7, colors[0], true, Paint.Align.CENTER);
        text(canvas, "LINK", stops[1], 267, 7, colors[1], true, Paint.Align.CENTER);
        text(canvas, "P2", stops[2], 267, 7, colors[2], true, Paint.Align.CENTER);
        text(canvas, "LINK", stops[3], 267, 7, colors[3], true, Paint.Align.CENTER);
        text(canvas, "GO", stops[4], 267, 7, colors[4], true, Paint.Align.CENTER);
    }

    private void drawPlayerBoard(Canvas canvas, int slot, float left, float top,
                                 int hero, int companion, boolean ready, boolean active) {
        boolean enabled = slot == 0 || twoPlayerMode;
        int color = slot == 0 ? Color.rgb(217, 255, 85) : Color.rgb(255, 192, 65);
        paint.setColor(Color.argb(enabled ? 242 : 150, 9, 19, 48));
        roundRect(canvas, left, top, left + 230, top + 84, 14, paint);
        if (active && enabled) {
            paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeWidth(3f);
            paint.setColor(color);
            roundRect(canvas, left, top, left + 230, top + 84, 14, paint);
            paint.setStyle(Paint.Style.FILL);
        }
        paint.setColor(enabled ? color : Color.rgb(73, 84, 103));
        canvas.drawCircle(left + 28, top + 27, 17, paint);
        text(canvas, "P" + (slot + 1), left + 28, top + 32, 11,
                Color.rgb(8, 20, 35), true, Paint.Align.CENTER);
        text(canvas, enabled ? safeHeroName(hero) : "OPTIONAL", left + 55, top + 22,
                13, enabled ? Color.WHITE : Color.rgb(126, 143, 160), true, Paint.Align.LEFT);
        text(canvas, enabled ? "LINK  " + safeHeroName(companion) : "ENABLE 2 PLAYERS IN MENU",
                left + 55, top + 41, 9, enabled ? color : Color.rgb(100, 117, 136),
                true, Paint.Align.LEFT);
        paint.setColor(ready ? Color.rgb(80, 220, 135) : Color.rgb(42, 59, 82));
        roundRect(canvas, left + 12, top + 55, left + 218, top + 76, 8, paint);
        text(canvas, !enabled ? "OFF" : ready ? "READY — PRESS AGAIN TO DEPART" : "L1 / R1 LINK  •  A / OK READY",
                left + 115, top + 70, 8, ready ? Color.rgb(5, 29, 29) : Color.WHITE,
                true, Paint.Align.CENTER);
    }

    private void drawHeroCard(Canvas canvas, int hero, float x, float y, boolean selectedForP1, boolean selectedForP2) {
        hero = safeHeroIndex(hero);
        int accent = HERO_COLORS[hero];
        boolean selected = selectedForP1 || selectedForP2;
        if (selected) {
            paint.setColor(Color.argb(90, Color.red(accent), Color.green(accent), Color.blue(accent)));
            roundRect(canvas, x - 2f, y - 2f, x + 142f, y + 190f, 16f, paint);
        }
        paint.setColor(selected ? Color.argb(248, 25, 34, 70) : Color.argb(228, 9, 19, 48));
        roundRect(canvas, x, y, x + 140, y + 175, 14, paint);
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(selected ? 4 : 2);
        paint.setColor(selected ? accent : Color.rgb(77, 79, 121));
        roundRect(canvas, x, y, x + 140, y + 175, 14, paint);
        paint.setStyle(Paint.Style.FILL);
        drawPortrait(canvas, hero, x + 22, y + 6, 96, 96);
        paint.setColor(accent);
        canvas.drawRect(x + 12, y + 105, x + 128, y + 109, paint);
        text(canvas, safeHeroName(hero), x + 70, y + 130, hero == 3 ? 12 : 15, Color.WHITE, true, Paint.Align.CENTER);
        text(canvas, safeHeroRole(hero), x + 70, y + 146, 9, accent, true, Paint.Align.CENTER);
        statBar(canvas, x + 18, y + 155, "P", Math.round(safeHeroPower(hero) * 65), accent);
        statBar(canvas, x + 18, y + 168, "S", Math.round(safeHeroSpeed(hero) * 22), accent);
        if (selected) {
            paint.setColor(Color.rgb(217, 255, 85));
            canvas.drawCircle(x + 126, y + 13, 10, paint);
            text(canvas, "✓", x + 126, y + 18, 13, Color.rgb(11, 25, 30), true, Paint.Align.CENTER);
            float focus = selectionMotion(320);
            paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeWidth(3f);
            paint.setStrokeCap(Paint.Cap.ROUND);
            paint.setColor(Color.argb(Math.round(80 + 175 * (1f - focus)),
                    Color.red(accent), Color.green(accent), Color.blue(accent)));
            dest.set(x + 12, y - 2, x + 128, y + 114);
            canvas.drawArc(dest, -90f, 360f * focus, false, paint);
            paint.setStrokeCap(Paint.Cap.BUTT);
            paint.setStyle(Paint.Style.FILL);
            if (selectedForP1) {
                paint.setColor(Color.rgb(217, 255, 85));
                roundRect(canvas, x + 10, y + 6, x + 45, y + 22, 8, paint);
                text(canvas, "P1", x + 28, y + 18, 9, Color.rgb(11, 25, 30), true, Paint.Align.CENTER);
            }
            if (selectedForP2) {
                paint.setColor(Color.rgb(255, 197, 70));
                roundRect(canvas, x + 95, y + 6, x + 130, y + 22, 8, paint);
                text(canvas, "P2", x + 113, y + 18, 9, Color.rgb(11, 25, 30), true, Paint.Align.CENTER);
            }
        }
    }

    private void drawIntro(Canvas canvas) {
        int hero = safeHeroIndex(selectedHero);
        drawBackdrop(canvas, 980f);
        float reveal = stateMotion(520);
        paint.setColor(Color.argb(230, 12, 13, 42));
        roundRect(canvas, 54, 40, 586, 322, 20, paint);
        text(canvas, "CHAPTER 1", W / 2f, 72, 14, Color.rgb(217, 255, 85), true, Paint.Align.CENTER);
        text(canvas, trainingMode ? "TRAINING BLOCK" : "NIGHT MARKET RESCUE", W / 2f, 108, 27,
                Color.WHITE, true, Paint.Align.CENTER);
        paint.setColor(safeHeroColor(hero));
        canvas.drawRect(104, 125, 104 + 432f * reveal, 131, paint);
        canvas.save();
        canvas.translate(-12f * (1f - reveal), 0f);
        drawPortrait(canvas, hero, 91, 151, 92, 92);
        text(canvas, safeHeroName(hero), 137, 262, hero == 3 ? 12 : 15,
                safeHeroColor(hero), true, Paint.Align.CENTER);
        canvas.restore();
        text(canvas, safeHeroRole(hero) + "  •  " + safeHeroMove(hero),
                214, 160, 13, safeHeroColor(hero), true, Paint.Align.LEFT);
        text(canvas, customerProfile.introMessage, 214, 177, 9,
                customerProfile.theme.accentColor, true, Paint.Align.LEFT);
        text(canvas, trainingMode
                        ? "Learn movement, combos, items\nand the Family Link assist."
                        : "The market lights are out. Clear the route,\nhelp the neighbors, and stop the Junk King.",
                214, 190, 13, Color.rgb(195, 215, 226), false, Paint.Align.LEFT);
        text(canvas, "MARKET  →  PARK  →  ALLEY", 214, 247, 11,
                Color.rgb(109, 226, 217), true, Paint.Align.LEFT);
        button(canvas, 222, 276, 418, 311, "BEGIN", Color.rgb(217, 255, 85), Color.rgb(15, 24, 35));
    }

    private void drawGame(Canvas canvas) {
        drawBackdrop(canvas, cameraX);
        drawStageProps(canvas);
        for (int pass = 0; pass < 3; pass++) {
            float low = 214 + pass * 37;
            float high = low + 38;
            for (Item item : items) if (item.active && item.y >= low && item.y < high) drawItem(canvas, item);
            for (WorldObject object : worldObjects) {
                if (object.active && !object.held && object.y >= low && object.y < high) {
                    drawWorldObject(canvas, object);
                }
            }
            for (Enemy enemy : enemies) if (enemy.alive && enemy.active && enemy.y >= low && enemy.y < high) drawEnemy(canvas, enemy);
            if (assist.active && assist.y >= low && assist.y < high) drawAssist(canvas);
            if (twoPlayerMode && player2Y >= low && player2Y < high) drawPlayerTwo(canvas);
            if (playerY >= low && playerY < high) drawPlayer(canvas);
        }
        for (Particle particle : particles) if (particle.active) drawParticle(canvas, particle);
        for (SpriteEffect effect : spriteEffects) if (effect.active) drawSpriteEffect(canvas, effect);
        drawHud(canvas);
        drawPickupPrompt(canvas);
        if (debugOverlay) drawDebugOverlay(canvas);
        if (zoneBanner > 0) drawZoneBanner(canvas);
    }

    private void drawStageProps(Canvas canvas) {
        for (int i = 0; i < STAGE_SIGN_X.length; i++) {
            float x = STAGE_SIGN_X[i] - cameraX;
            if (x < -80 || x > 700) continue;
            paint.setColor(Color.rgb(18, 20, 48));
            canvas.drawRect(x, 203, x + 5, 315, paint);
            paint.setColor(i == 3 ? Color.rgb(255, 83, 92) : Color.rgb(255, 194, 70));
            roundRect(canvas, x - 34, 188, x + 39, 214, 4, paint);
            String sign = i == 0 ? "MARKET" : i == 1 ? "PARK" : i == 2 ? "ALLEY"
                    : i == 3 ? "JUNK" : i == 4 ? "ROOFTOP" : "DEPOT";
            text(canvas, sign, x + 2, 206,
                    10, Color.rgb(20, 20, 44), true, Paint.Align.CENTER);
        }
        if (zoneActive && zone < ZONE_TRIGGERS.length) {
            float gate = ZONE_TRIGGERS[zone] + 425f - cameraX;
            if (gate > 0 && gate < W) {
                paint.setColor(Color.argb(150, 217, 255, 85));
                canvas.drawRect(gate, 210, gate + 4, 335, paint);
                text(canvas, "CLEAR!", gate - 5, 226, 10, Color.rgb(217, 255, 85), true, Paint.Align.RIGHT);
            }
        }
    }

    private void drawPlayer(Canvas canvas) {
        int hero = safeHeroIndex(selectedHero);
        float x = playerX - cameraX;
        float baseY = playerY;
        float heroHeight = Math.round((playerAnimator.isBound()
                ? HERO_ANIM_RENDER_HEIGHT[hero] : HERO_RENDER_HEIGHT[hero]) * CHARACTER_SCREEN_SCALE);
        float shadowHalfWidth = 20f + heroHeight * 0.083f;
        paint.setColor(Color.argb(90, 0, 0, 0));
        canvas.drawOval(x - shadowHalfWidth, baseY - 7, x + shadowHalfWidth, baseY + 7, paint);
        paint.setAlpha(255);
        if (invulnerable > 0 && (invulnerable / 3) % 2 == 0) paint.setAlpha(110);
        int pose = hurtTimer > 0 || health <= 0 ? 3 : attackTimer > 0 ? 2
                : Math.abs(moveX) + Math.abs(moveY) > 0.15f || keyLeft || keyRight || keyUp || keyDown
                ? 1 : 0;
        if (playerAnimator.isBound()) {
            drawAnimatedHero(canvas, playerAnimator, hero, x,
                    baseY - playerZ, !facingRight, paint.getAlpha());
        } else if (heroArt[hero] != null) {
            drawPersonalHero(canvas, hero, pose, x, baseY - playerZ, !facingRight);
        } else {
            drawTallActor(canvas, hero, pose, x, baseY - playerZ,
                    heroHeight / 64f, !facingRight);
        }
        paint.setAlpha(255);
        if (heldWeaponType >= 0) drawHeldWeapon(canvas, x, baseY - playerZ, heroHeight);
    }

    private void drawPlayerTwo(Canvas canvas) {
        int hero = safeHeroIndex(selectedHero2);
        float x = player2X - cameraX;
        float baseY = player2Y;
        float height = HERO_ANIM_RENDER_HEIGHT[hero] * CHARACTER_SCREEN_SCALE;
        paint.setColor(Color.argb(78, 0, 0, 0));
        canvas.drawOval(x - 22f, baseY - 7, x + 22f, baseY + 7, paint);
        if (player2Animator.isBound()) {
            drawAnimatedHero(canvas, player2Animator, hero, x, baseY - player2Z,
                    !p2FacingRight, 255);
        } else if (heroArt[hero] != null) {
            drawPersonalHero(canvas, hero, p2AttackTimer > 0 ? 2 : 0, x,
                    baseY - player2Z, !p2FacingRight);
        }
        int accent = safeHeroColor(hero);
        paint.setColor(accent);
        text(canvas, "P2", x, baseY - height - 5f, 8, accent, true,
                Paint.Align.CENTER);
    }

    private void drawTallActor(Canvas canvas, int actor, int pose, float x, float baseY,
                               float actorScale, boolean flip) {
        actor = safeHeroIndex(actor);
        if (actorAtlas == null) {
            drawFallbackHero(canvas, actor, x, baseY, actorScale * (64f / 90f), flip);
            return;
        }
        int topBlock = actor * 8 + pose;
        int bottomBlock = actor * 8 + 4 + pose;
        float size = 32f * actorScale;
        canvas.save();
        if (flip) canvas.scale(-1f, 1f, x, 0f);
        drawAtlasBlock(canvas, topBlock, x - size * 0.5f, baseY - size * 2f, size);
        drawAtlasBlock(canvas, bottomBlock, x - size * 0.5f, baseY - size, size);
        canvas.restore();
    }

    private void drawPersonalHero(Canvas canvas, int hero, int pose, float x, float baseY, boolean flip) {
        hero = safeHeroIndex(hero);
        Bitmap bitmap = heroArt[hero];
        if (bitmap == null || bitmap.isRecycled()) {
            drawFallbackHero(canvas, hero, x, baseY, HERO_RENDER_HEIGHT[hero] / 64f, flip);
            return;
        }
        float height = Math.round(HERO_RENDER_HEIGHT[hero] * CHARACTER_SCREEN_SCALE);
        float width = height * bitmap.getWidth() / Math.max(1f, (float) Math.max(1, bitmap.getHeight()));
        float bob = pose == 1 ? (float) Math.sin(stageFrames * 0.42f) * 2f : 0f;
        float lunge = pose == 2 ? (flip ? -8f : 8f) : 0f;
        float attackMotion = 0f;
        if (attackTimer > 0 && attackKind != ACTION_NONE) {
            float progress = 1f - attackTimer / (float) Math.max(1, actionDuration(attackKind));
            attackMotion = (float) Math.sin(Math.min(1f, progress / 0.72f) * Math.PI);
            float reach = attackKind == ACTION_HEAVY_PUNCH || attackKind == ACTION_HEAVY_KICK
                    || attackKind == ACTION_WEAPON ? 18f : 11f;
            lunge = (flip ? -1f : 1f) * reach * attackMotion;
        }
        float rotation = 0f;
        if (attackKind == ACTION_KICK || attackKind == ACTION_HEAVY_KICK) {
            rotation = (flip ? -1f : 1f) * attackMotion
                    * (attackKind == ACTION_HEAVY_KICK ? 8f : 5f);
        } else if (pose == 3 && hero == selectedHero) {
            if (health <= 0) {
                float fall = clamp((50f - knockoutTimer) / 30f, 0f, 1f);
                rotation = (flip ? -1f : 1f) * 72f * fall;
            } else {
                rotation = (flip ? 1f : -1f)
                        * (5f + (float) Math.sin(hurtTimer * 0.9f) * 2.5f);
            }
        }
        float scaleX = 1f + attackMotion * (attackKind == ACTION_SPECIAL ? 0.10f : 0.035f);
        float scaleY = 1f - attackMotion * (attackKind == ACTION_HEAVY_PUNCH ? 0.06f : 0.02f);
        canvas.save();
        canvas.translate(x + lunge, baseY + bob);
        canvas.rotate(rotation);
        canvas.scale((flip ? -1f : 1f) * scaleX, scaleY);
        dest.set(-width * 0.5f, -height, width * 0.5f, 0);
        heroPaint.setAlpha(paint.getAlpha());
        canvas.drawBitmap(bitmap, null, dest, heroPaint);
        heroPaint.setAlpha(255);
        canvas.restore();
    }

    private void drawAnimatedHero(Canvas canvas, SpriteAnimator animator, int hero,
                                  float x, float baseY, boolean flip, int alpha) {
        float height = Math.round(HERO_ANIM_RENDER_HEIGHT[hero] * CHARACTER_SCREEN_SCALE);
        int row = animator.row();
        int frame = animator.frame();
        Bitmap sourceBitmap = animator == playerAnimator ? selectedHeroAnimArt
                : animator == player2Animator ? player2AnimArt : assistAnimArt;
        Rect[] sourceCache = animator == playerAnimator ? selectedHeroAnimSources
                : animator == player2Animator ? player2AnimSources : assistAnimSources;
        if (sourceBitmap == null || sourceBitmap.isRecycled()) return;
        if (hero == 0 && animator == playerAnimator && animator.row() == HERO_IDLE
                && attackTimer <= 0 && heroHdArt[0] != null && !heroHdArt[0].isRecycled()) {
            Bitmap hd = heroHdArt[0];
            float hdHeight = height;
            float hdWidth = hdHeight * hd.getWidth() / Math.max(1f, hd.getHeight());
            canvas.save();
            canvas.translate(x, baseY);
            if (flip) canvas.scale(-1f, 1f);
            dest.set(-hdWidth * 0.5f, -hdHeight, hdWidth * 0.5f, 0f);
            heroPaint.setAlpha(alpha);
            canvas.drawBitmap(hd, null, dest, heroPaint);
            heroPaint.setAlpha(255);
            canvas.restore();
            return;
        }
        int sourceIndex = animator == assistAnimator ? frame : row * HERO_ANIM_COLUMNS + frame;
        if (sourceIndex < 0 || sourceIndex >= sourceCache.length) sourceIndex = 0;
        Rect sourceRect = sourceCache[sourceIndex];
        if (sourceRect == null || sourceRect.isEmpty()) sourceRect = HERO_ANIM_FULL_CELL;
        float atlasCellWidth = sourceBitmap.getWidth() / (float) HERO_ANIM_COLUMNS;
        float atlasCellHeight = animator == assistAnimator ? sourceBitmap.getHeight()
                : sourceBitmap.getHeight() / (float) HERO_ANIM_ROWS;
        float frameHeight = sourceRect.height();
        float frameWidth = sourceRect.width();
        if (frameHeight <= 0f) {
            frameHeight = atlasCellHeight;
            frameWidth = atlasCellWidth;
            sourceRect = HERO_ANIM_FULL_CELL;
        }
        float width = height * frameWidth / frameHeight;
        float sourceCenterX = sourceRect.centerX() - (float) sourceRect.left;
        float xOffset = (sourceCenterX - (atlasCellWidth * 0.5f)) / frameWidth * width;
        canvas.save();
        canvas.translate(x, baseY);
        if (flip) canvas.scale(-1f, 1f);
        dest.set(-width * 0.5f - xOffset, -height, width * 0.5f - xOffset, 0f);
        heroPaint.setAlpha(alpha);
        canvas.drawBitmap(sourceBitmap, sourceRect, dest, heroPaint);
        heroPaint.setAlpha(255);
        canvas.restore();
    }

    private void drawHeldWeapon(Canvas canvas, float x, float baseY, float heroHeight) {
        Bitmap bitmap = weaponBitmap(heldWeaponType);
        if (bitmap == null) return;
        float bodyScale = heroHeight / ESSA_RENDER_HEIGHT;
        float direction = facingRight ? 1f : -1f;
        int frame = playerAnimator.frame();
        if (!playerAnimator.isBound() && attackTimer > 0) {
            int elapsed = actionDuration(attackKind) - attackTimer;
            frame = Math.min(7, elapsed * 8 / Math.max(1, actionDuration(attackKind)));
        }
        float angle = -34f;
        float handX = x + direction * 22f * bodyScale;
        float handY = baseY - 66f * bodyScale;
        if (attackKind == ACTION_WEAPON || attackKind == ACTION_THROW) {
            angle = -72f + frame * 22f;
            handX += direction * frame * 2.4f * bodyScale;
            handY += Math.abs(3 - frame) * 2f * bodyScale;
        } else if (attackKind == ACTION_HEAVY_KICK || attackKind == ACTION_KICK) {
            angle = -48f;
        }
        angle *= direction;
        float size = (heldWeaponType == WEAPON_MALLET || heldWeaponType == WEAPON_SIGN
                ? 64f : 52f) * bodyScale;
        canvas.save();
        canvas.translate(handX, handY);
        canvas.rotate(angle);
        if (!facingRight) canvas.scale(-1f, 1f);
        dest.set(-size * 0.32f, -size * 0.82f, size * 0.68f, size * 0.18f);
        canvas.drawBitmap(bitmap, null, dest, pixelPaint);
        canvas.restore();
    }

    private Bitmap weaponBitmap(int type) {
        if (type >= 0 && type < weaponArt.length && weaponArt[type] != null) {
            return weaponArt[type];
        }
        return itemArt[ITEM_BAT];
    }

    private void drawAtlasBlock(Canvas canvas, int block, float x, float y, float size) {
        int sx = (block & 3) * 32;
        int sy = (block >> 2) * 32;
        if (actorAtlas == null || actorAtlas.isRecycled()) return;
        source.set(sx, sy, sx + 32, sy + 32);
        dest.set(x, y, x + size, y + size);
        pixelPaint.setAlpha(paint.getAlpha());
        canvas.drawBitmap(actorAtlas, source, dest, pixelPaint);
        pixelPaint.setAlpha(255);
    }

    private void drawFallbackHero(Canvas canvas, int actor, float x, float baseY, float s, boolean flip) {
        int accent = HERO_COLORS[actor];
        paint.setColor(Color.argb(95, 0, 0, 0));
        canvas.drawOval(x - 24, baseY - 5, x + 24, baseY + 6, paint);
        paint.setColor(Color.rgb(29, 29, 57));
        roundRect(canvas, x - 18, baseY - 65 * s, x + 18, baseY - 26 * s, 8, paint);
        paint.setColor(accent);
        roundRect(canvas, x - 15, baseY - 61 * s, x + 15, baseY - 29 * s, 6, paint);
        paint.setColor(Color.rgb(225, 171, 122));
        canvas.drawCircle(x, baseY - 75 * s, 14 * s, paint);
        paint.setColor(Color.rgb(21, 20, 45));
        canvas.drawCircle(x + (flip ? -4 : 4), baseY - 77 * s, 2.5f * s, paint);
        paint.setStrokeWidth(7 * s);
        canvas.drawLine(x - 9, baseY - 27 * s, x - 10, baseY, paint);
        canvas.drawLine(x + 9, baseY - 27 * s, x + 10, baseY, paint);
    }

    private void drawEnemy(Canvas canvas, Enemy enemy) {
        float x = enemy.x - cameraX;
        float height = enemyHeight(enemy.type);
        float width = enemy.animator.isBound() ? height * 160f / 192f
                : height * (enemy.type == 3 ? 0.9f : enemy.type == 2 ? 0.8f : 0.7f);
        paint.setColor(Color.argb(100, 0, 0, 0));
        canvas.drawOval(x - width * 0.34f, enemy.y - 6, x + width * 0.34f, enemy.y + 7, paint);
        Bitmap bitmap = enemyArt[enemy.type];
        if (enemy.flash > 0) {
            pixelPaint.setColorFilter(new PorterDuffColorFilter(Color.WHITE, PorterDuff.Mode.SRC_ATOP));
        }
        if (enemy.animator.isBound()) {
            canvas.save();
            if (!enemy.facingRight) canvas.scale(-1f, 1f, x, 0f);
            dest.set(x - width * 0.5f, enemy.y - enemy.z - height,
                    x + width * 0.5f, enemy.y - enemy.z);
            enemy.animator.draw(canvas, pixelPaint, source, dest);
            canvas.restore();
        } else if (bitmap != null) {
            float bob = enemy.state == ENEMY_STATE_WALK
                    ? (float) Math.sin((stageFrames + enemy.type * 9) * 0.42f) * 2.4f : 0f;
            float lunge = 0f;
            float rotation = 0f;
            float scaleX = 1f;
            float scaleY = 1f;
            if (enemy.state == ENEMY_STATE_ATTACK) {
                float progress = clamp(enemy.stateTicks / 24f, 0f, 1f);
                float motion = (float) Math.sin(progress * Math.PI);
                lunge = (enemy.facingRight ? 1f : -1f)
                        * (enemy.type == 3 ? 25f : 15f) * motion;
                rotation = (enemy.facingRight ? 1f : -1f) * 7f * motion;
                scaleX += motion * 0.08f;
                scaleY -= motion * 0.04f;
            } else if (enemy.state == ENEMY_STATE_HURT) {
                rotation = ((enemy.stateTicks & 2) == 0 ? -1f : 1f) * 5f;
            } else if (enemy.state == ENEMY_STATE_KNOCKDOWN) {
                rotation = (enemy.facingRight ? 1f : -1f)
                        * Math.min(72f, enemy.stateTicks * 4.5f);
                scaleY = 1f - Math.min(0.12f, enemy.stateTicks * 0.008f);
            }
            canvas.save();
            canvas.translate(x + lunge, enemy.y - enemy.z + bob);
            canvas.rotate(rotation);
            canvas.scale((enemy.facingRight ? 1f : -1f) * scaleX, scaleY);
            dest.set(-width * 0.5f, -height, width * 0.5f, 0f);
            canvas.drawBitmap(bitmap, null, dest, pixelPaint);
            canvas.restore();
        } else {
            paint.setColor(enemy.type == 3 ? Color.rgb(166, 83, 224) : Color.rgb(20, 157, 148));
            roundRect(canvas, x - width * 0.42f, enemy.y - enemy.z - height * 0.78f,
                    x + width * 0.42f, enemy.y - enemy.z, 12, paint);
            paint.setColor(Color.rgb(217, 255, 85));
            canvas.drawCircle(x - 7, enemy.y - enemy.z - height * 0.68f, 3, paint);
            canvas.drawCircle(x + 7, enemy.y - enemy.z - height * 0.68f, 3, paint);
        }
        pixelPaint.setColorFilter(null);
        if (enemy.hp < enemy.maxHp || enemy.type == 3) {
            float barW = enemy.type == 3 ? 92f : 54f;
            paint.setColor(Color.argb(190, 10, 10, 25));
            canvas.drawRect(x - barW / 2, enemy.y - enemy.z - height - 10,
                    x + barW / 2, enemy.y - enemy.z - height - 5, paint);
            paint.setColor(enemy.type == 3 ? Color.rgb(255, 82, 92) : Color.rgb(217, 255, 85));
            canvas.drawRect(x - barW / 2, enemy.y - enemy.z - height - 10,
                    x - barW / 2 + barW * Math.max(0, enemy.hp) / enemy.maxHp,
                    enemy.y - enemy.z - height - 5, paint);
        }
        if (enemy.state == ENEMY_STATE_ATTACK && !enemy.attackHitFired
                && (!enemy.animator.isBound() || enemy.animator.frame() < 3)) {
            paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeWidth(2);
            paint.setColor(Color.argb(180, 255, 85, 92));
            canvas.drawCircle(x, enemy.y - enemy.z - height * 0.55f,
                    15 + (enemy.stateTicks & 3), paint);
            paint.setStyle(Paint.Style.FILL);
        }
        if (debugOverlay) {
            text(canvas, ENEMY_STATE_LABELS[enemy.state], x,
                    enemy.y - enemy.z - height - 14f, 7f,
                    enemy.state == ENEMY_STATE_ATTACK ? Color.rgb(255, 85, 92)
                            : enemy.state == ENEMY_STATE_KNOCKDOWN
                            ? Color.rgb(255, 202, 64) : Color.WHITE,
                    true, Paint.Align.CENTER);
        }
    }

    private float enemyHeight(int type) {
        return type == 3 ? 160f : type == 2 ? 136f : type == 1 ? 110f : 120f;
    }

    private void drawItem(Canvas canvas, Item item) {
        float x = item.x - cameraX;
        float bob = (float) Math.sin((stageFrames + item.x) * 0.08f) * 3f;
        paint.setColor(Color.argb(110, 0, 0, 0));
        canvas.drawOval(x - 18, item.y - 4, x + 18, item.y + 6, paint);
        Bitmap bitmap = itemArt[item.type];
        if (bitmap != null) {
            dest.set(x - 20, item.y - item.z - 43 + bob,
                    x + 20, item.y - item.z - 3 + bob);
            canvas.drawBitmap(bitmap, null, dest, pixelPaint);
        } else drawFallbackItem(canvas, item.type, x, item.y - item.z - 22 + bob);
        if (item.life < 180 && (item.life / 8) % 2 == 0) {
            paint.setColor(Color.argb(130, 255, 255, 255));
            canvas.drawCircle(x, item.y - item.z - 22 + bob, 24, paint);
        }
    }

    private void drawFallbackItem(Canvas canvas, int type, float x, float y) {
        int color = type == ITEM_FOOD ? Color.rgb(255, 113, 96)
                : type == ITEM_ENERGY ? Color.rgb(67, 221, 230)
                : type == ITEM_TOKEN ? Color.rgb(217, 255, 85) : Color.rgb(255, 199, 72);
        paint.setColor(Color.rgb(17, 18, 45));
        canvas.drawCircle(x, y, 19, paint);
        paint.setColor(color);
        canvas.drawCircle(x, y, 14, paint);
        text(canvas, type == ITEM_FOOD ? "+" : type == ITEM_ENERGY ? "⚡" : type == ITEM_TOKEN ? "★" : "!",
                x, y + 6, 16, Color.rgb(20, 25, 40), true, Paint.Align.CENTER);
    }

    private void drawWorldObject(Canvas canvas, WorldObject object) {
        float x = object.x - cameraX;
        float shadowWidth = object.type >= PROP_CRATE ? 28f : 20f;
        paint.setColor(Color.argb(95, 0, 0, 0));
        canvas.drawOval(x - shadowWidth, object.y - 5f,
                x + shadowWidth, object.y + 6f, paint);
        Bitmap bitmap;
        float size;
        if (object.type == PROP_CRATE) {
            bitmap = propArt[0];
            size = 66f;
        } else if (object.type == PROP_TRASH_CAN) {
            bitmap = propArt[1];
            size = 72f;
        } else {
            bitmap = weaponBitmap(object.type);
            size = object.type == WEAPON_MALLET || object.type == WEAPON_SIGN ? 61f : 48f;
        }
        if (bitmap != null) {
            canvas.save();
            canvas.translate(x, object.y - object.z - size * 0.48f);
            canvas.rotate(object.angle);
            dest.set(-size * 0.5f, -size * 0.5f, size * 0.5f, size * 0.5f);
            canvas.drawBitmap(bitmap, null, dest, pixelPaint);
            canvas.restore();
        } else {
            paint.setColor(object.type == PROP_CRATE
                    ? Color.rgb(206, 132, 68) : Color.rgb(88, 188, 187));
            roundRect(canvas, x - size * 0.42f, object.y - object.z - size,
                    x + size * 0.42f, object.y - object.z, 8f, paint);
        }
    }

    private void drawPickupPrompt(Canvas canvas) {
        if (heldWeaponType >= 0 || attackTimer > 0 || playerZ > 0f) return;
        WorldObject object = nearestPickupWeapon(PICKUP_PROMPT_X, PICKUP_PROMPT_Y);
        if (object == null) return;
        float x = clamp(object.x - cameraX, 58f, W - 58f);
        float y = clamp(object.y - object.z - 67f, 74f, H - 60f);
        paint.setColor(Color.argb(226, 7, 16, 38));
        roundRect(canvas, x - 48f, y - 18f, x + 48f, y + 10f, 9f, paint);
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(2f);
        paint.setColor(Color.rgb(255, 202, 75));
        roundRect(canvas, x - 48f, y - 18f, x + 48f, y + 10f, 9f, paint);
        paint.setStyle(Paint.Style.FILL);
        text(canvas, gamepadUiActive ? "A  PICK UP" : "PICK UP", x, y + 1f, 9,
                Color.WHITE, true, Paint.Align.CENTER);
    }

    private void drawAssist(Canvas canvas) {
        float x = assist.x - cameraX;
        float height = (assistAnimator.isBound()
                ? HERO_ANIM_RENDER_HEIGHT[assist.hero] : HERO_RENDER_HEIGHT[assist.hero])
                * CHARACTER_SCREEN_SCALE;
        paint.setColor(Color.argb(90, 0, 0, 0));
        canvas.drawOval(x - 19f, assist.y - 6f, x + 19f, assist.y + 6f, paint);
        int alpha = assist.phase == 2 ? Math.max(70, 255 - assist.ticks * 9) : 255;
        if (assistAnimator.isBound() && assist.phase == 1) {
            drawAnimatedHero(canvas, assistAnimator, assist.hero, x, assist.y,
                    !assist.facingRight, alpha);
        } else if (heroArt[assist.hero] != null) {
            paint.setAlpha(alpha);
            int pose = assist.phase == 1 ? 2 : 1;
            drawPersonalHero(canvas, assist.hero, pose, x,
                    assist.y + (float) Math.sin(assist.ticks * 0.5f) * 1.5f,
                    !assist.facingRight);
            paint.setAlpha(255);
        } else {
            drawFallbackHero(canvas, assist.hero, x, assist.y,
                    height / 90f, !assist.facingRight);
        }
    }

    private void drawSpriteEffect(Canvas canvas, SpriteEffect effect) {
        if (effect.bitmap == null || effect.bitmap.isRecycled()) return;
        int cellWidth = effect.bitmap.getWidth() / effect.columns;
        int cellHeight = effect.bitmap.getHeight() / effect.rows;
        int sx = (effect.frame % effect.columns) * cellWidth;
        int sy = (effect.frame / effect.columns) * cellHeight;
        source.set(sx, sy, sx + cellWidth, sy + cellHeight);
        float width = 96f * effect.scale;
        float height = width * cellHeight / Math.max(1f, cellWidth);
        float x = effect.x - cameraX;
        float y = effect.y - effect.z;
        dest.set(x - width * 0.5f, y - height * 0.5f,
                x + width * 0.5f, y + height * 0.5f);
        canvas.drawBitmap(effect.bitmap, source, dest, pixelPaint);
    }

    private void drawParticle(Canvas canvas, Particle particle) {
        paint.setColor(particle.color);
        float x = particle.x - cameraX;
        if (particle.kind == 1) {
            paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeWidth(3);
            canvas.drawCircle(x, particle.y, particle.size * (1f + (particle.maxLife - particle.life) * 0.14f), paint);
            paint.setStyle(Paint.Style.FILL);
        } else {
            canvas.save();
            canvas.rotate(particle.rotation, x, particle.y);
            canvas.drawRect(x - particle.size, particle.y - 1.5f, x + particle.size, particle.y + 1.5f, paint);
            canvas.restore();
        }
    }

    private void drawHud(Canvas canvas) {
        clampHeroIndexesForPlay();
        int p1 = safeHeroIndex(selectedHero);
        int p2 = safeHeroIndex(selectedHero2);
        paint.setColor(Color.argb(220, 8, 9, 31));
        roundRect(canvas, 14, 13, 310, 74, 12, paint);
        drawPortrait(canvas, p1, 20, 18, 48, 48);
        text(canvas, safeHeroName(p1), 77, 31, 12, safeHeroColor(p1), true, Paint.Align.LEFT);
        bar(canvas, 77, 38, 207, 49, health / (float) maxHealth, Color.rgb(255, 76, 91), "HP");
        bar(canvas, 77, 54, 207, 63, energy / 100f, Color.rgb(67, 219, 230), "SP");
        bar(canvas, 216, 38, 292, 49, linkMeter / 100f, Color.rgb(217, 255, 85), "LINK");
        text(canvas, health + "/" + maxHealth, 204, 47, 7, Color.WHITE, true, Paint.Align.RIGHT);
        text(canvas, energy + "%", 204, 62, 7, Color.WHITE, true, Paint.Align.RIGHT);
        if (linkMeter >= 50) {
            paint.setColor(Color.argb(255, 217, 255, 85));
            roundRect(canvas, 214, 34, 294, 61, 5, paint);
            paint.setColor(Color.argb(90, 20, 30, 45));
            roundRect(canvas, 217, 37, 291, 58, 4, paint);
            paint.setColor(Color.rgb(8, 14, 24));
            text(canvas, "LINK READY", 254, 53, 9, Color.WHITE, true, Paint.Align.CENTER);
            paint.setColor(Color.rgb(217, 255, 85));
            if (energy >= 30) text(canvas, "SP READY", 150, 17, 9, Color.WHITE, true, Paint.Align.LEFT);
        } else {
            paint.setColor(Color.WHITE);
            text(canvas, linkMeter + "%", 289, 47, 7, Color.WHITE, true, Paint.Align.RIGHT);
        }
        if (twoPlayerMode) {
            paint.setColor(Color.argb(220, 8, 9, 31));
            roundRect(canvas, 318, 13, 468, 61, 10, paint);
            int p2Color = safeHeroColor(p2);
            text(canvas, "P2 " + safeHeroName(p2), 330, 29, 10,
                    p2Color, true, Paint.Align.LEFT);
            bar(canvas, 330, 34, 460, 42, p2Health / (float) Math.max(1, safeHeroMaxHealth(p2)),
                    p2Color, "HP");
            text(canvas, p2Health + "/" + safeHeroMaxHealth(p2), 458, 32, 7,
                    Color.WHITE, true, Paint.Align.RIGHT);
            bar(canvas, 330, 46, 395, 54, p2Energy / 100f, Color.rgb(67, 219, 230), "SP");
            bar(canvas, 402, 46, 460, 54, p2Link / 100f, Color.rgb(217, 255, 85), "LINK");
            if (p2Link >= 50) {
                paint.setColor(Color.argb(255, 217, 255, 85));
                roundRect(canvas, 398, 42, 464, 60, 5, paint);
                paint.setColor(Color.argb(90, 20, 30, 45));
                roundRect(canvas, 401, 45, 461, 57, 4, paint);
                paint.setColor(Color.rgb(8, 14, 24));
                text(canvas, "LINK READY", 429, 55, 8, Color.WHITE, true, Paint.Align.CENTER);
                paint.setColor(Color.rgb(217, 255, 85));
                if (p2Energy >= 30) text(canvas, "SP READY", 330, 17, 9, Color.WHITE, true, Paint.Align.LEFT);
            }
        }
        if (twoPlayerMode && (p1ReviveProgress > 0 || p2ReviveProgress > 0)) {
            int revive = Math.max(p1ReviveProgress, p2ReviveProgress);
            paint.setColor(Color.argb(235, 8, 9, 31));
            roundRect(canvas, 230, 82, 410, 108, 8, paint);
            bar(canvas, 242, 96, 398, 104, revive / 120f,
                    Color.rgb(255, 202, 80), "REVIVE");
            text(canvas, "STAY CLOSE TO REVIVE", 320, 93, 9,
                    Color.WHITE, true, Paint.Align.CENTER);
        }
        if (cachedScore != score) {
            cachedScore = score;
            cachedScoreText = String.format(Locale.US, "%07d", score);
        }
        text(canvas, cachedScoreText, 216, 65, 14, Color.WHITE, true, Paint.Align.LEFT);
        paint.setColor(Color.argb(210, 8, 9, 31));
        roundRect(canvas, 480, 13, 626, 61, 10, paint);
        text(canvas, zone >= ZONE_TRIGGERS.length ? "ROUTE CLEAR" : AREA_NAMES[Math.min(zone, AREA_NAMES.length - 1)], 553, 33, 12,
                Color.rgb(255, 202, 80), true, Paint.Align.CENTER);
        text(canvas, AREA_PROGRESS[Math.min(zone, AREA_PROGRESS.length - 1)], 553, 50, 11,
                Color.LTGRAY, false, Paint.Align.CENTER);
        if (combo >= 2 && comboWindow > 0) {
            String rating = combo >= 3 ? "IN SYNC!" : "SPARK!";
            text(canvas, rating, 614, 112, 20, Color.rgb(217, 255, 85), true, Paint.Align.RIGHT);
            if (cachedCombo != combo) {
                cachedCombo = combo;
                cachedComboText = combo + " HIT";
            }
            text(canvas, cachedComboText, 614, 132, 13, Color.WHITE, true, Paint.Align.RIGHT);
        }
        if (teamComboBanner > 0) {
            float pulse = 1f + 0.05f * (float) Math.sin(teamComboBanner * 0.35f);
            canvas.save();
            canvas.scale(pulse, pulse, 320f, 143f);
            paint.setColor(Color.argb(220, 8, 9, 31));
            roundRect(canvas, 232, 118, 408, 154, 10, paint);
            text(canvas, "TEAM COMBO!", 320, 141, 18,
                    Color.rgb(217, 255, 85), true, Paint.Align.CENTER);
            canvas.restore();
        } else if (dashAttackActive && attackTimer > 0) {
            text(canvas, "DASH STRIKE", 320, 140, 13,
                    Color.rgb(67, 219, 230), true, Paint.Align.CENTER);
        }
        if (lastHitEnemy != null && lastHitEnemyTicks > 0) {
            paint.setColor(Color.argb(210, 8, 9, 31));
            roundRect(canvas, 14, 80, 214, 108, 8, paint);
            int enemyColor = lastHitEnemy.type == 3 ? Color.rgb(255, 92, 92)
                    : lastHitEnemy.type == 2 ? Color.rgb(255, 158, 66)
                    : lastHitEnemy.type == 1 ? Color.rgb(120, 200, 255)
                    : Color.rgb(190, 190, 210);
            String enemyName = lastHitEnemy.type == 3 ? "JUNK KING"
                    : lastHitEnemy.type == 2 ? "BRUTE"
                    : lastHitEnemy.type == 1 ? "SKATER" : "GRUNT";
            text(canvas, enemyName, 22, 93, 10, enemyColor, true, Paint.Align.LEFT);
            bar(canvas, 22, 97, 206, 104,
                    Math.max(0, lastHitEnemy.hp) / (float) Math.max(1, lastHitEnemy.maxHp),
                    enemyColor, "");
            text(canvas, Math.max(0, lastHitEnemy.hp) + "/" + lastHitEnemy.maxHp,
                    206, 93, 7, Color.WHITE, true, Paint.Align.RIGHT);
        }
        if (heldWeaponType >= 0) {
            if (cachedWeaponType != heldWeaponType
                    || cachedWeaponDurability != weaponDurability) {
                cachedWeaponType = heldWeaponType;
                cachedWeaponDurability = weaponDurability;
                cachedWeaponText = weaponName(heldWeaponType) + " " + weaponDurability;
            }
            text(canvas, cachedWeaponText,
                    322, 64, 11, Color.rgb(255, 201, 72), true, Paint.Align.LEFT);
        }
    }

    private void drawDebugOverlay(Canvas canvas) {
        float x = playerX - cameraX;
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(1.5f);
        paint.setColor(Color.argb(220, 84, 235, 224));
        canvas.drawRect(x - 16f, playerY - playerZ - 72f,
                x + 16f, playerY - playerZ, paint);
        canvas.drawRect(x - 18f, playerY - 15f, x + 18f, playerY + 15f, paint);
        if (twoPlayerMode) {
            float p2x = player2X - cameraX;
            paint.setColor(Color.argb(220, 83, 144, 255));
            canvas.drawRect(p2x - 18f, player2Y - 15f,
                    p2x + 18f, player2Y + 15f, paint);
        }
        if (isPlayerAttackBoxActive()) {
            float range = attackReach(attackKind, punchChainStep);
            float laneReach = attackLaneHalfHeight(attackKind);
            float rear = attackKind == ACTION_SPECIAL || attackKind == ACTION_LINK ? range : 12f;
            float left = facingRight ? x - rear : x - range;
            float right = facingRight ? x + range : x + rear;
            paint.setColor(Color.argb(220, 255, 82, 92));
            canvas.drawRect(left, playerY - laneReach, right, playerY + laneReach, paint);
        }
        paint.setColor(Color.argb(190, 255, 207, 72));
        for (Enemy enemy : enemies) {
            if (!enemy.alive || !enemy.active) continue;
            float enemyX = enemy.x - cameraX;
            canvas.drawRect(enemyX - enemyHurtHalfWidth(enemy.type),
                    enemy.y - enemyHurtLaneHalfHeight(enemy.type),
                    enemyX + enemyHurtHalfWidth(enemy.type),
                    enemy.y + enemyHurtLaneHalfHeight(enemy.type), paint);
            if (enemy.state == ENEMY_STATE_ATTACK
                    && (enemy.animator.frame() == 3 || !enemy.animator.isBound()
                    && enemy.stateTicks >= 10 && enemy.stateTicks <= 12)) {
                float range = enemy.type == 3 ? 88f : enemy.type == 2 ? 62f : 48f;
                float rear = 10f;
                float left = enemy.facingRight ? enemyX - rear : enemyX - range;
                float right = enemy.facingRight ? enemyX + range : enemyX + rear;
                float lane = enemy.type == 3 ? 34f : 26f;
                paint.setColor(Color.argb(225, 255, 70, 82));
                canvas.drawRect(left, enemy.y - lane, right, enemy.y + lane, paint);
                paint.setColor(Color.argb(190, 255, 207, 72));
            }
        }
        paint.setStyle(Paint.Style.FILL);
        paint.setColor(Color.argb(220, 7, 9, 27));
        roundRect(canvas, 13, 82, 310, 102, 4, paint);
        MoveSpec spec = moveSpec(attackKind);
        text(canvas, "ACTION " + spec.name + "  ROW " + playerAnimator.row()
                        + "  FRAME " + playerAnimator.frame() + "  CHAIN " + punchChainStep
                        + "  BOX " + Math.round(attackReach(attackKind, punchChainStep))
                        + "x" + Math.round(spec.laneHalfHeight * 2f),
                19, 96, 9, Color.WHITE, true, Paint.Align.LEFT);
    }

    private int activeWorldObjects() {
        int count = 0;
        for (WorldObject object : worldObjects) if (object.active) count++;
        return count;
    }

    private String weaponName(int type) {
        if (type == WEAPON_PIPE) return "PIPE";
        if (type == WEAPON_MALLET) return "MALLET";
        if (type == WEAPON_SIGN) return "SIGN";
        if (type == WEAPON_CONE) return "CONE";
        return "BAT";
    }

    private void drawTouchControls(Canvas canvas) {
        int alpha = Math.round(255 * touchOpacity);
        drawControlSurface(canvas, alpha);
        float stickOuter = 56f * controlScale;
        float stickRing = 50f * controlScale;
        float knobRadius = 21f * controlScale;
        paint.setColor(Color.argb(alpha / 2, 8, 10, 34));
        canvas.drawCircle(stickCenterX, stickCenterY, stickOuter, paint);
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(Math.max(2f, 3f * controlScale));
        paint.setColor(Color.argb(alpha, 83, 224, 216));
        canvas.drawCircle(stickCenterX, stickCenterY, stickRing, paint);
        paint.setStyle(Paint.Style.FILL);
        paint.setColor(Color.argb(alpha, 173, 246, 239));
        canvas.drawCircle(stickCenterX + stickX * 27f * controlScale,
                stickCenterY + stickY * 27f * controlScale, knobRadius, paint);
        for (int i = 0; i < touchButtonX.length; i++) {
            drawActionButton(canvas, i, alpha);
        }
        paint.setColor(Color.argb(alpha, 15, 16, 48));
        roundRect(canvas, pauseCenterX - 13f, pauseCenterY - 13f,
                pauseCenterX + 13f, pauseCenterY + 13f, 6, paint);
        text(canvas, "Ⅱ", pauseCenterX, pauseCenterY + 6f, 15, Color.WHITE, true, Paint.Align.CENTER);
    }

    private void drawActionButton(Canvas canvas, int index, int alpha) {
        float x = touchButtonX[index];
        float y = touchButtonY[index];
        float radius = touchButtonRadius[index] * controlScale;
        paint.setColor(Color.argb(alpha / 2, 8, 10, 34));
        canvas.drawCircle(x, y, radius + 3f, paint);
        paint.setColor(Color.argb(alpha, Color.red(ACTION_BUTTON_COLORS[index]),
                Color.green(ACTION_BUTTON_COLORS[index]), Color.blue(ACTION_BUTTON_COLORS[index])));
        canvas.drawCircle(x, y, radius, paint);
        if (actionIcons != null && actionIcons.getWidth() >= 512 && actionIcons.getHeight() >= 256) {
            int sx = (index & 3) * 128;
            int sy = (index >> 2) * 128;
            source.set(sx, sy, sx + 128, sy + 128);
            float iconSize = radius * 1.52f;
            dest.set(x - iconSize * 0.5f, y - iconSize * 0.5f,
                    x + iconSize * 0.5f, y + iconSize * 0.5f);
            pixelPaint.setAlpha(alpha);
            canvas.drawBitmap(actionIcons, source, dest, pixelPaint);
            pixelPaint.setAlpha(255);
        } else {
            float fontSize = index >= 2 ? 7f : 8f;
            text(canvas, ACTION_BUTTON_LABELS[index], x, y + 3f,
                    fontSize * controlScale, Color.WHITE, true, Paint.Align.CENTER);
        }
    }

    private void drawControlSurface(Canvas canvas, int alpha) {
        if (responsiveLayout == LAYOUT_CONTROL_DECK) {
            float top = gameSceneY + H;
            paint.setColor(Color.argb(Math.min(232, alpha + 80), 8, 10, 32));
            canvas.drawRect(0, top, virtualWidth, virtualHeight, paint);
            paint.setColor(Color.argb(Math.min(210, alpha), 66, 214, 204));
            canvas.drawRect(0, top, virtualWidth, top + 2f, paint);
            text(canvas, "MOVE", 90f, top + 20f, 9,
                    Color.argb(Math.min(210, alpha), 130, 233, 226), true, Paint.Align.CENTER);
            text(canvas, "ACTION DECK", virtualWidth * 0.5f, top + 20f, 9,
                    Color.argb(Math.min(210, alpha), 217, 255, 85), true, Paint.Align.CENTER);
        } else if (responsiveLayout == LAYOUT_SIDE_GUTTERS) {
            paint.setColor(Color.argb(Math.min(220, alpha + 65), 8, 10, 32));
            canvas.drawRect(0, 0, sceneX, virtualHeight, paint);
            canvas.drawRect(sceneX + W, 0, virtualWidth, virtualHeight, paint);
            paint.setColor(Color.argb(Math.min(190, alpha), 66, 214, 204));
            canvas.drawRect(sceneX - 2f, 0, sceneX, virtualHeight, paint);
            canvas.drawRect(sceneX + W, 0, sceneX + W + 2f, virtualHeight, paint);
        }
    }

    private void drawZoneBanner(Canvas canvas) {
        float t = Math.min(1f, (110 - Math.abs(zoneBanner - 55)) / 35f);
        int alpha = Math.round(220 * Math.max(0.35f, t));
        paint.setColor(Color.argb(alpha, 8, 9, 31));
        roundRect(canvas, 154, 102, 486, 163, 12, paint);
        if (zone < ZONE_TRIGGERS.length && zoneActive) {
            text(canvas, ENCOUNTER_NAMES[zone], W / 2f, 125, 12,
                    Color.rgb(217, 255, 85), true, Paint.Align.CENTER);
            text(canvas, AREA_NAMES[zone], W / 2f, 151, 22, Color.WHITE, true, Paint.Align.CENTER);
        } else if (zone < ZONE_TRIGGERS.length) {
            text(canvas, "ROUTE OPEN", W / 2f, 140, 22, Color.rgb(217, 255, 85), true, Paint.Align.CENTER);
        }
    }

    private void drawPause(Canvas canvas) {
        paint.setColor(Color.argb(205, 5, 5, 25));
        canvas.drawRect(0, 0, W, H, paint);
        paint.setColor(Color.argb(245, 20, 21, 58));
        roundRect(canvas, 178, 49, 462, 323, 18, paint);
        text(canvas, "PAUSED", W / 2f, 82, 26, Color.WHITE, true, Paint.Align.CENTER);
        String controllerStatus = controllerLabel(primaryControllerId, "P1");
        if (twoPlayerMode) controllerStatus += "  •  " + controllerLabel(secondaryControllerId, "P2");
        text(canvas, controllerStatus, W / 2f, 105, 8,
                Color.rgb(144, 221, 224), true, Paint.Align.CENTER);
        button(canvas, 218, 118, 422, 158, "RESUME", Color.rgb(217, 255, 85), Color.rgb(14, 24, 34),
                pauseOption == 0);
        button(canvas, 218, 171, 422, 211, "SETTINGS", Color.rgb(66, 214, 224), Color.rgb(14, 24, 34),
                pauseOption == 1);
        button(canvas, 218, 224, 422, 264, "RESTART", Color.rgb(255, 197, 70), Color.rgb(14, 24, 34),
                pauseOption == 2);
        button(canvas, 218, 277, 422, 310, "QUIT TO MAP", Color.rgb(255, 85, 94), Color.rgb(255, 255, 255),
                pauseOption == 3);
    }

    private String controllerLabel(int deviceId, String player) {
        if (deviceId < 0) return player + " PRESS ANY BUTTON";
        InputDevice device = InputDevice.getDevice(deviceId);
        if (device == null) return player + " DISCONNECTED";
        String name = device.getName();
        if (name == null || name.trim().isEmpty()) name = "CONTROLLER";
        name = name.toUpperCase(Locale.US);
        if (name.length() > 14) name = name.substring(0, 14);
        return player + " " + name;
    }

    private void drawSettings(Canvas canvas) {
        drawBackdrop(canvas, 250f);
        drawTopBrand(canvas, "SETTINGS & ACCESSIBILITY");
        paint.setColor(Color.argb(235, 13, 14, 43));
        roundRect(canvas, 76, 78, 564, 316, 18, paint);
        settingRow(canvas, 104, 111, "MUSIC", musicEnabled ? "ON" : "OFF", musicEnabled, settingsOption == 0);
        settingRow(canvas, 104, 151, "SOUND EFFECTS", sfxEnabled ? "ON" : "OFF", sfxEnabled, settingsOption == 1);
        settingRow(canvas, 104, 191, "HAPTICS", hapticsEnabled ? "ON" : "OFF", hapticsEnabled, settingsOption == 2);
        settingRow(canvas, 104, 231, "SCREEN SHAKE", shakeEnabled ? "ON" : "OFF", shakeEnabled, settingsOption == 3);
        String diff = difficulty == 0 ? "EASY" : difficulty == 2 ? "HARD" : "NORMAL";
        settingRow(canvas, 104, 271, "DIFFICULTY", diff, true, settingsOption == 4);
        button(canvas, 445, 321, 555, 349, "BACK", Color.rgb(217, 255, 85), Color.rgb(15, 24, 35),
                settingsOption == 5);
    }

    private void drawResults(Canvas canvas) {
        drawBackdrop(canvas, WORLD_END);
        paint.setColor(Color.argb(232, 10, 11, 37));
        roundRect(canvas, 65, 36, 575, 326, 22, paint);
        text(canvas, "NEIGHBORHOOD SAVED!", W / 2f, 79, 30, Color.rgb(217, 255, 85), true, Paint.Align.CENTER);
        text(canvas, customerProfile.outroMessage, W / 2f, 101, 9,
                customerProfile.theme.accentColor, true, Paint.Align.CENTER);
        int stars = 1 + (damageTaken < maxHealth / 2 ? 1 : 0) + (totalHits >= 10 ? 1 : 0);
        for (int i = 0; i < 3; i++) {
            text(canvas, "★", 260 + i * 60, 133, 42, i < stars ? Color.rgb(255, 199, 72) : Color.rgb(58, 59, 91), true, Paint.Align.CENTER);
        }
        resultRow(canvas, 132, 167, "SCORE", String.format(Locale.US, "%07d", score));
        resultRow(canvas, 132, 195, "HITS", Integer.toString(totalHits));
        resultRow(canvas, 132, 223, "DAMAGE TAKEN", Integer.toString(damageTaken));
        resultRow(canvas, 132, 251, "BEST", String.format(Locale.US, "%07d", bestScore));
        button(canvas, 126, 280, 309, 315, "PLAY AGAIN", Color.rgb(66, 214, 224), Color.rgb(13, 25, 35),
                resultsOption == 0);
        button(canvas, 331, 280, 514, 315, "MAP", Color.rgb(217, 255, 85), Color.rgb(13, 25, 35),
                resultsOption == 1);
    }

    private void drawGameOver(Canvas canvas) {
        drawBackdrop(canvas, cameraX);
        paint.setColor(Color.argb(225, 10, 8, 30));
        canvas.drawRect(0, 0, W, H, paint);
        text(canvas, "THE ROUTE NEEDS YOU", W / 2f, 111, 30, Color.rgb(255, 91, 99), true, Paint.Align.CENTER);
        text(canvas, "Try a new hero, grab the health drops, and watch enemy warnings.", W / 2f, 151, 13,
                Color.LTGRAY, false, Paint.Align.CENTER);
        button(canvas, 153, 202, 313, 247, "RETRY", Color.rgb(217, 255, 85), Color.rgb(14, 24, 34),
                gameOverOption == 0);
        button(canvas, 327, 202, 487, 247, "MAP", Color.rgb(66, 214, 224), Color.rgb(14, 24, 34),
                gameOverOption == 1);
    }

    private void drawGallery(Canvas canvas) {
        drawBackdrop(canvas, 700f);
        drawTopBrand(canvas, "FAMILY HEROES");
        text(canvas, "Four original heroes, inspired by your family.", W / 2f, 92, 13,
                Color.LTGRAY, false, Paint.Align.CENTER);
        for (int i = 0; i < 4; i++) {
            float x = 44 + i * 145;
            paint.setColor(Color.argb(225, 17, 18, 52));
            roundRect(canvas, x, 116, x + 126, 276, 12, paint);
            drawPortrait(canvas, i, x + 12, 126, 102, 102);
            text(canvas, HERO_NAMES[i], x + 63, 250, i == 3 ? 11 : 14, HERO_COLORS[i], true, Paint.Align.CENTER);
            text(canvas, HERO_MOVES[i], x + 63, 267, 8, Color.LTGRAY, true, Paint.Align.CENTER);
        }
        button(canvas, 493, 314, 606, 345, "BACK", Color.rgb(217, 255, 85), Color.rgb(15, 24, 35),
                false);
    }

    private void drawPortrait(Canvas canvas, int hero, float x, float y, float width, float height) {
        hero = safeHeroIndex(hero);
        paint.setColor(Color.rgb(25, 27, 65));
        roundRect(canvas, x, y, x + width, y + height, 8, paint);
        if (heroPortraits[hero] != null) {
            dest.set(x, y, x + width, y + height);
            canvas.drawBitmap(heroPortraits[hero], null, dest, portraitPaint);
        } else if (portraits != null) {
            int sx = (hero & 1) * 64;
            int sy = (hero >> 1) * 64;
            source.set(sx, sy, sx + 64, sy + 64);
            dest.set(x, y, x + width, y + height);
            canvas.drawBitmap(portraits, source, dest, pixelPaint);
        } else {
            paint.setColor(HERO_COLORS[hero]);
            canvas.drawCircle(x + width / 2, y + height * 0.48f, Math.min(width, height) * 0.31f, paint);
            paint.setColor(Color.rgb(28, 28, 56));
            canvas.drawCircle(x + width * 0.43f, y + height * 0.45f, 3, paint);
            canvas.drawCircle(x + width * 0.57f, y + height * 0.45f, 3, paint);
        }
    }

    private void drawTopBrand(Canvas canvas, String heading) {
        paint.setColor(Color.argb(225, 8, 9, 30));
        canvas.drawRect(0, 0, W, 62, paint);
        text(canvas, customerProfile.eventTitle, 24, 29, 18,
                customerProfile.theme.accentColor, true, Paint.Align.LEFT);
        text(canvas, heading, 24, 50, 12, Color.rgb(113, 229, 219), true, Paint.Align.LEFT);
        text(canvas, customerProfile.appDisplayName, 616, 37, 11,
                customerProfile.theme.textColor, true, Paint.Align.RIGHT);
    }

    private void menuCard(Canvas canvas, float left, float top, float right, float bottom,
                          String title, String subtitle, int accent, boolean selected) {
        if (selected) {
            paint.setColor(Color.argb(205, 20, 34, 68));
            roundRect(canvas, left + 8f, top + 3f, right - 8f, bottom - 3f, 8, paint);
        }
        if (selected) {
            paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeWidth(3f);
            paint.setColor(accent);
            roundRect(canvas, left, top, right, bottom, 12f, paint);
            paint.setStyle(Paint.Style.FILL);
        }
        paint.setColor(accent);
        canvas.drawCircle(left + 27, (top + bottom) * 0.5f, selected ? 12f : 9f, paint);
        paint.setColor(Color.rgb(7, 16, 38));
        canvas.drawCircle(left + 27, (top + bottom) * 0.5f, selected ? 5f : 4f, paint);
        paint.setColor(accent);
        canvas.drawRect(left + 39, (top + bottom) * 0.5f - 2f, right - 24,
                (top + bottom) * 0.5f + 2f, paint);
        text(canvas, title, left + 55, top + 16, 12, Color.WHITE, true, Paint.Align.LEFT);
        text(canvas, subtitle, left + 55, top + 32, 7, Color.rgb(182, 211, 221), true, Paint.Align.LEFT);
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(2f);
        canvas.drawCircle(right - 18, (top + bottom) * 0.5f, 7f, paint);
        paint.setStyle(Paint.Style.FILL);
    }

    private void settingRow(Canvas canvas, float x, float y, String label, String value, boolean on) {
        text(canvas, label, x, y + 18, 15, Color.WHITE, true, Paint.Align.LEFT);
        paint.setColor(on ? Color.rgb(54, 204, 186) : Color.rgb(75, 75, 103));
        roundRect(canvas, 417, y, 535, y + 28, 14, paint);
        text(canvas, value, 476, y + 19, 12, on ? Color.rgb(10, 25, 34) : Color.LTGRAY, true, Paint.Align.CENTER);
        paint.setColor(Color.rgb(53, 55, 88));
        canvas.drawRect(x, y + 34, 535, y + 35, paint);
    }

    private void resultRow(Canvas canvas, float x, float y, String label, String value) {
        text(canvas, label, x, y, 13, Color.rgb(126, 222, 216), true, Paint.Align.LEFT);
        text(canvas, value, 508, y, 16, Color.WHITE, true, Paint.Align.RIGHT);
        paint.setColor(Color.rgb(48, 49, 82));
        canvas.drawRect(x, y + 8, 508, y + 9, paint);
    }

    private void statBar(Canvas canvas, float x, float y, String label, int amount, int color) {
        text(canvas, label, x, y + 8, 8, Color.LTGRAY, true, Paint.Align.LEFT);
        paint.setColor(Color.rgb(49, 50, 82));
        canvas.drawRect(x + 13, y + 2, x + 106, y + 8, paint);
        paint.setColor(color);
        canvas.drawRect(x + 13, y + 2, x + 13 + Math.min(93, amount), y + 8, paint);
    }

    private void bar(Canvas canvas, float left, float top, float right, float bottom, float value, int color, String label) {
        paint.setColor(Color.rgb(44, 45, 76));
        roundRect(canvas, left, top, right, bottom, 4, paint);
        paint.setColor(color);
        roundRect(canvas, left, top, left + (right - left) * clamp(value, 0, 1), bottom, 4, paint);
        text(canvas, label, left + 4, bottom - 1, 8, Color.WHITE, true, Paint.Align.LEFT);
    }

    private void pulseButton(Canvas canvas, float l, float t, float r, float b, String label) {
        float pulse = uiAnimationsEnabled
                ? 0.82f + 0.18f * (float) Math.sin(SystemClock.uptimeMillis() * 0.005)
                : 1f;
        int green = Color.rgb(217, 255, 85);
        paint.setColor(Color.argb(Math.round(210 + pulse * 40), Color.red(green), Color.green(green), Color.blue(green)));
        roundRect(canvas, l, t, r, b, 12, paint);
        text(canvas, label, (l + r) / 2, t + 28, 17, Color.rgb(16, 22, 35), true, Paint.Align.CENTER);
    }

    private void button(Canvas canvas, float l, float t, float r, float b, String label, int bg, int fg) {
        paint.setColor(bg);
        roundRect(canvas, l, t, r, b, 9, paint);
        text(canvas, label, (l + r) * 0.5f, (t + b) * 0.5f + 6, 14, fg, true, Paint.Align.CENTER);
    }

    private void button(Canvas canvas, float l, float t, float r, float b, String label, int bg, int fg,
                        boolean selected) {
        button(canvas, l, t, r, b, label, bg, fg);
        if (!selected) return;
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(3f);
        paint.setColor(Color.WHITE);
        roundRect(canvas, l - 2f, t - 2f, r + 2f, b + 2f, 11f, paint);
        paint.setStyle(Paint.Style.FILL);
    }

    private void settingRow(Canvas canvas, float x, float y, String label, String value, boolean on,
                           boolean selected) {
        if (selected) {
            paint.setColor(Color.argb(140, 217, 255, 85));
            roundRect(canvas, 96, y - 3, 540, y + 33, 14, paint);
            paint.setColor(Color.rgb(217, 255, 85));
            paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeWidth(2f);
            roundRect(canvas, 96, y - 3, 540, y + 33, 14, paint);
            paint.setStyle(Paint.Style.FILL);
        }
        settingRow(canvas, x, y, label, value, on);
    }

    private void text(Canvas canvas, String value, float x, float y, float size, int color,
                      boolean bold, Paint.Align align) {
        paint.setShader(null);
        paint.setColor(color);
        paint.setTextSize(size);
        paint.setTextAlign(align);
        paint.setTypeface(bold ? android.graphics.Typeface.DEFAULT_BOLD : android.graphics.Typeface.DEFAULT);
        int newline = value.indexOf('\n');
        if (newline < 0) {
            canvas.drawText(value, x, y, paint);
            return;
        }
        int start = 0;
        int line = 0;
        while (newline >= 0) {
            canvas.drawText(value.substring(start, newline), x,
                    y + line++ * (size + 4), paint);
            start = newline + 1;
            newline = value.indexOf('\n', start);
        }
        canvas.drawText(value.substring(start), x, y + line * (size + 4), paint);
    }

    private void roundRect(Canvas canvas, float l, float t, float r, float b, float radius, Paint p) {
        dest.set(l, t, r, b);
        canvas.drawRoundRect(dest, radius, radius, p);
    }

    private void spawnHit(float x, float y, int color) {
        for (int i = 0; i < 10; i++) {
            Particle p = nextParticle();
            p.kind = 0;
            p.x = x;
            p.y = y;
            float angle = (float) (Math.PI * 2 * i / 10.0 + random.nextFloat() * 0.3);
            float speed = 1.5f + random.nextFloat() * 3.6f;
            p.vx = (float) Math.cos(angle) * speed;
            p.vy = (float) Math.sin(angle) * speed - 1.5f;
            p.size = 4 + random.nextFloat() * 8;
            p.rotation = random.nextInt(180);
            p.life = p.maxLife = 16 + random.nextInt(10);
            p.color = color;
        }
    }

    private void spawnDust(float x, float y, int color, int count) {
        for (int i = 0; i < count; i++) {
            Particle p = nextParticle();
            p.kind = 0;
            p.x = x + random.nextFloat() * 24 - 12;
            p.y = y + random.nextFloat() * 8 - 4;
            p.vx = random.nextFloat() * 2 - 1;
            p.vy = -0.5f - random.nextFloat() * 2.4f;
            p.size = 2 + random.nextFloat() * 5;
            p.rotation = random.nextInt(180);
            p.life = p.maxLife = 18 + random.nextInt(14);
            p.color = color;
        }
    }

    private void spawnRing(float x, float y, int color) {
        Particle p = nextParticle();
        p.kind = 1;
        p.x = x;
        p.y = y;
        p.vx = p.vy = 0;
        p.size = 15;
        p.rotation = 0;
        p.life = p.maxLife = 18;
        p.color = color;
    }

    private void spawnSpriteEffect(Bitmap bitmap, int columns, int rows, int frames,
                                   float x, float y, float z, float effectScale) {
        if (bitmap == null || bitmap.isRecycled()) return;
        SpriteEffect effect = spriteEffects[effectCursor++ % spriteEffects.length];
        effect.active = true;
        effect.bitmap = bitmap;
        effect.columns = Math.max(1, columns);
        effect.rows = Math.max(1, rows);
        effect.frames = Math.max(1, Math.min(frames, effect.columns * effect.rows));
        effect.frame = 0;
        effect.ticks = 0;
        effect.x = x;
        effect.y = y;
        effect.z = z;
        effect.scale = effectScale;
    }

    private void spawnWeaponTrailEffect(float x, float y, float z, float effectScale) {
        if (weaponTrailFxArt != null && !weaponTrailFxArt.isRecycled()) {
            spawnSpriteEffect(weaponTrailFxArt, 4, 2, 8, x, y, z, effectScale);
        } else {
            spawnSpriteEffect(hitFxArt, 4, 4, 16, x, y, z, effectScale);
        }
    }

    private void spawnBreakEffect(float x, float y, float z, float effectScale) {
        if (breakFxArt != null && !breakFxArt.isRecycled()) {
            spawnSpriteEffect(breakFxArt, 4, 2, 8, x, y, z, effectScale);
        } else {
            spawnSpriteEffect(hitFxArt, 4, 4, 16, x, y, z, effectScale);
        }
    }

    private void updateSpriteEffects() {
        for (SpriteEffect effect : spriteEffects) {
            if (!effect.active) continue;
            if (++effect.ticks >= 3) {
                effect.ticks = 0;
                if (++effect.frame >= effect.frames) effect.active = false;
            }
        }
    }

    private Particle nextParticle() {
        Particle particle = particles[particleCursor++ % particles.length];
        particle.active = true;
        return particle;
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        if (event == null) return false;
        try {
        gamepadUiActive = false;
        float x = (event.getX(event.getActionIndex()) - offsetX) / scale;
        float y = (event.getY(event.getActionIndex()) - offsetY) / scale;
        int action = event.getActionMasked();
        int pointerId = event.getPointerId(event.getActionIndex());
        if (action == MotionEvent.ACTION_DOWN || action == MotionEvent.ACTION_POINTER_DOWN) {
            if (state == PLAY) handleGameTouchDown(pointerId, x, y);
            else handleMenuTap(x - sceneX, y - sceneYForState());
            return true;
        }
        if (action == MotionEvent.ACTION_MOVE && state == PLAY) {
            if (stickPointer >= 0) {
                int index = event.findPointerIndex(stickPointer);
                if (index >= 0) updateStick((event.getX(index) - offsetX) / scale,
                        (event.getY(index) - offsetY) / scale);
            }
            return true;
        }
        if (action == MotionEvent.ACTION_CANCEL) {
            clearInputs();
            return true;
        }
        if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_POINTER_UP) {
            if (action == MotionEvent.ACTION_UP) performClick();
            releasePointer(pointerId);
            return true;
        }
        return true;
        } catch (Throwable runtimeError) {
            Log.e(TAG, "onTouchEvent crashed", runtimeError);
            clearInputs();
            enterState(MENU);
            return true;
        }
    }

    @Override
    public boolean performClick() {
        super.performClick();
        return true;
    }

    private void handleMenuTap(float x, float y) {
        try {
        audio.play(AudioController.CONFIRM);
        if (state == TITLE) {
            menuChoice = hasCheckpoint ? 0 : 1;
            enterState(MENU);
            return;
        }
        if (state == MENU) {
            if (inside(x, y, 28, 82, 318, 124)) {
                if (restoreCheckpoint()) enterState(PLAY);
            } else if (inside(x, y, 28, 128, 318, 170)) {
                trainingMode = false;
                twoPlayerMode = false;
                menuChoice = 1;
                enterState(SELECT);
            } else if (inside(x, y, 28, 174, 318, 216)) {
                trainingMode = false;
                twoPlayerMode = true;
                menuChoice = 2;
                enterState(SELECT);
            } else if (inside(x, y, 28, 220, 318, 262)) {
                trainingMode = true;
                twoPlayerMode = false;
                menuChoice = 3;
                enterState(SELECT);
            } else if (inside(x, y, 28, 266, 318, 308)) {
                menuChoice = 4;
                settingsReturn = MENU;
                enterState(SETTINGS);
            } else if (inside(x, y, 342, 84, 604, 306)) {
                enterState(GALLERY);
            }
            return;
        }
        if (state == SELECT) {
            if (inside(x, y, 18, 272, 248, 360)) {
                cycleCompanion(0, 1);
                p1Ready = false;
                return;
            }
            if (twoPlayerMode && inside(x, y, 266, 272, 496, 360)) {
                cycleCompanion(1, 1);
                p2Ready = false;
                return;
            }
            if (inside(x, y, 504, 272, 622, 360)) {
                keyboardConfirm();
                return;
            }
            if (y >= 72 && y <= 247) {
                int card = (int) ((x - 16) / 153);
                if (card >= 0 && card < 4) {
                    if (!p1Ready) {
                        selectedHero = card;
                        selectedCompanion1 = sanitizeCompanionIndex(selectedCompanion1, selectedHero);
                    } else if (!p2Ready) {
                        selectedHero2 = card;
                        selectedCompanion2 = sanitizeCompanionIndex(selectedCompanion2, selectedHero2);
                    } else {
                        selectedHero = card;
                    }
                }
            }
            if (!hasCompanionController()) {
                if (!p1Ready) {
                    selectHeroForActiveSlot(selectedHero);
                } else if (!p2Ready) {
                    selectHeroForActiveSlot(selectedHero2);
                } else {
                    selectHeroForActiveSlot(selectedHero);
                }
            }
            return;
        }
        if (state == INTRO) {
            if (inside(x, y, 190, 245, 450, 330)) {
                safeEnterPlayFromIntro();
            }
            return;
        }
        if (state == PAUSE) {
            if (inside(x, y, 218, 112, 422, 164)) safeResumePlay();
            else if (inside(x, y, 218, 165, 422, 217)) {
                settingsReturn = PAUSE;
                enterState(SETTINGS);
            } else if (inside(x, y, 218, 218, 422, 270)) {
                safeEnterPlayFromIntro();
            } else if (inside(x, y, 218, 270, 422, 322)) {
                enterState(MENU);
            }
            return;
        }
        if (state == SETTINGS) {
            if (inside(x, y, 90, 101, 545, 143)) {
                musicEnabled = !musicEnabled;
                audio.setMusicEnabled(musicEnabled);
            } else if (inside(x, y, 90, 143, 545, 183)) {
                sfxEnabled = !sfxEnabled;
                audio.setSfxEnabled(sfxEnabled);
            } else if (inside(x, y, 90, 183, 545, 223)) hapticsEnabled = !hapticsEnabled;
            else if (inside(x, y, 90, 223, 545, 263)) shakeEnabled = !shakeEnabled;
            else if (inside(x, y, 90, 263, 545, 305)) difficulty = (difficulty + 1) % 3;
            else if (inside(x, y, 430, 305, 575, 360)) {
                saveSettings();
                enterState(settingsReturn);
            }
            return;
        }
        if (state == RESULTS) {
            if (inside(x, y, 110, 267, 320, 330)) {
                enterState(INTRO);
            } else if (inside(x, y, 320, 267, 530, 330)) {
                enterState(MENU);
            }
            return;
        }
        if (state == GAME_OVER) {
            if (inside(x, y, 140, 188, 320, 260)) {
                safeEnterPlayFromIntro();
            } else if (inside(x, y, 320, 188, 500, 260)) {
                enterState(MENU);
            }
            return;
        }
        if (state == GALLERY && inside(x, y, 470, 295, 630, 360)) {
            enterState(MENU);
        }
        } catch (Throwable runtimeError) {
            Log.e(TAG, "handleMenuTap crashed", runtimeError);
            clearInputs();
            enterState(MENU);
        }
    }

    private void handleGameTouchDown(int pointerId, float x, float y) {
        if (distance(x, y, pauseCenterX, pauseCenterY) < 31f) {
            enterState(PAUSE);
            clearInputs();
            return;
        }
        if (distance(x, y, stickCenterX, stickCenterY) < 70f * controlScale
                && stickPointer < 0) {
            stickPointer = pointerId;
            updateStick(x, y);
            return;
        }
        int closestButton = -1;
        float closestNormalizedDistance = Float.MAX_VALUE;
        for (int i = 0; i < touchButtonX.length; i++) {
            float hitRadius = Math.max(27f, touchButtonRadius[i] + 9f) * controlScale;
            float dx = x - touchButtonX[i];
            float dy = y - touchButtonY[i];
            float normalizedDistance = (dx * dx + dy * dy) / (hitRadius * hitRadius);
            if (normalizedDistance < 1f && normalizedDistance < closestNormalizedDistance) {
                closestNormalizedDistance = normalizedDistance;
                closestButton = i;
            }
        }
        if (closestButton >= 0) pressButtonPointer(closestButton, pointerId);
    }

    private void pressButtonPointer(int button, int pointerId) {
        buttonPointers[button] = pointerId;
        if (button == 0) lightQueued = true;
        else if (button == 1) kickQueued = true;
        else if (button == 2) heavyQueued = true;
        else if (button == 3) heavyKickQueued = true;
        else if (button == 4) jumpQueued = true;
        else if (button == 5) specialQueued = true;
        else if (button == 6) assistQueued = true;
        else throwQueued = true;
    }

    private void updateStick(float x, float y) {
        float dx = x - stickCenterX;
        float dy = y - stickCenterY;
        float len = (float) Math.sqrt(dx * dx + dy * dy);
        float range = 42f * controlScale;
        if (len > range) {
            dx *= range / len;
            dy *= range / len;
        }
        stickX = dx / range;
        stickY = dy / range;
        moveX = Math.abs(stickX) < 0.16f ? 0f : stickX;
        moveY = Math.abs(stickY) < 0.16f ? 0f : stickY;
    }

    private void releasePointer(int pointerId) {
        if (pointerId == stickPointer) {
            stickPointer = -1;
            stickX = stickY = moveX = moveY = 0f;
        }
        for (int i = 0; i < buttonPointers.length; i++) {
            if (buttonPointers[i] == pointerId) buttonPointers[i] = -1;
        }
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        try {
            if (event == null) return super.onKeyDown(keyCode, event);
            InputDevice inputDevice = event.getDevice();
            if (isGamepadSource(event.getSource())) {
                keyCode = ControllerCompat.normalizeKey(
                        inputDevice == null ? "" : inputDevice.getName(), keyCode);
            }
            int source = event.getSource();
            long now = SystemClock.uptimeMillis();
            int controllerSlot = resolveControllerSlot(event.getDeviceId(), source);
            if (isGamepadSource(source) || isNavigationSource(source)) {
                updateControllerIds(event.getDeviceId(), source, controllerSlot);
                if ((source & (InputDevice.SOURCE_GAMEPAD | InputDevice.SOURCE_JOYSTICK)) != 0) {
                    gamepadUiActive = true;
                }
            }
            boolean p2ByDevice = hasCompanionController() && controllerSlot == 1;
            if (state == SELECT && (keyCode == KeyEvent.KEYCODE_BUTTON_L1
                    || keyCode == KeyEvent.KEYCODE_BUTTON_R1)) {
                if (!isMenuActionRepeatAllowed(keyCode, now)) return true;
                int slot = hasCompanionController() ? (p2ByDevice ? 1 : 0) : activeSelectionSlot;
                cycleCompanion(slot, keyCode == KeyEvent.KEYCODE_BUTTON_L1 ? -1 : 1);
                setReadyForSlot(slot, false);
                return true;
            }
                if (state == SELECT && isMenuNavigationAlias(keyCode)) {
                    int selectionSlot = resolveSelectSlot(event.getDeviceId(), source);
                    if (selectionSlot != 0 && selectionSlot != 1) selectionSlot = activeSelectionSlot;
                    boolean moveLeft = keyCode == KeyEvent.KEYCODE_DPAD_LEFT || isMenuMoveLeft(keyCode);
                    boolean moveRight = keyCode == KeyEvent.KEYCODE_DPAD_RIGHT || isMenuMoveRight(keyCode);
                    if (moveLeft || moveRight) {
                    if (!isMenuActionRepeatAllowed(keyCode, now)) return true;
                    if (selectionSlot == 1) {
                        p2Ready = false;
                        selectedHero2 = sanitizeHeroIndex(selectedHero2 + (moveLeft ? -1 : 1));
                        selectedCompanion2 = sanitizeCompanionIndex(selectedCompanion2, selectedHero2);
                    } else {
                        p1Ready = false;
                        selectedHero = sanitizeHeroIndex(selectedHero + (moveLeft ? -1 : 1));
                        selectedCompanion1 = sanitizeCompanionIndex(selectedCompanion1, selectedHero);
                    }
                    if (hasCompanionController() && isDedicatedCompanion()) {
                        activeSelectionSlot = selectionSlot;
                    }
                    return true;
                }
            }
            if (state == SELECT && isMenuConfirmAlias(keyCode)) {
                if (!isMenuActionRepeatAllowed(keyCode, now)) return true;
                if (!twoPlayerMode) {
                    keyboardConfirm();
                    return true;
                }
                if (!hasCompanionController()) {
                    if (!p1Ready) {
                        p1Ready = true;
                        activeSelectionSlot = 1;
                        syncControllerInputSlots();
                        return true;
                    }
                    p2Ready = true;
                } else {
                    setReadyForSlot(p2ByDevice ? 1 : 0, true);
                    syncControllerInputSlots();
                }
                if (canStartBattle()) {
                    keyboardConfirm();
                }
                return true;
            }
            if (state == SELECT && isMenuCancelAlias(keyCode)) {
                keyboardCancel();
                return true;
            }
                if (state == PLAY && p2ByDevice) {
                    if (keyCode == KeyEvent.KEYCODE_DPAD_LEFT || keyCode == KeyEvent.KEYCODE_A) p2Left = true;
                    else if (keyCode == KeyEvent.KEYCODE_DPAD_RIGHT || keyCode == KeyEvent.KEYCODE_D) p2Right = true;
                    else if (keyCode == KeyEvent.KEYCODE_DPAD_UP || keyCode == KeyEvent.KEYCODE_W) p2Up = true;
                    else if (keyCode == KeyEvent.KEYCODE_DPAD_DOWN || keyCode == KeyEvent.KEYCODE_S) p2Down = true;
                    else if (queueP2ActionByKey(keyCode)) return true;
                    return true;
                }
                if (state != PLAY) {
                    if (isMenuNavigationAlias(keyCode) && isMenuConfirmAlias(keyCode) && event.getRepeatCount() > 0) {
                        return true;
                    }
                    if (isMenuConfirmAlias(keyCode) || isConfirmActionKey(keyCode)) {
                        keyboardConfirm();
                    } else if (isCancelActionKey(keyCode) || isMenuCancelAlias(keyCode)) {
                        keyboardCancel();
                    } else if (isMenuMoveUp(keyCode) || isMenuMoveDown(keyCode)
                            || isMenuMoveLeft(keyCode) || isMenuMoveRight(keyCode)) {
                    if (!isMenuActionRepeatAllowed(keyCode, now)) return true;
                    int horizontal = isMenuMoveRight(keyCode) ? 1 : (isMenuMoveLeft(keyCode) ? -1 : 0);
                    int vertical = isMenuMoveDown(keyCode) ? 1 : (isMenuMoveUp(keyCode) ? -1 : 0);
                    if (state == SELECT && twoPlayerMode && !hasCompanionController()
                            && (!p1Ready || !p2Ready)
                            && (horizontal != 0 || vertical != 0)) {
                        if (vertical != 0 && horizontal == 0) {
                            activeSelectionSlot = (activeSelectionSlot == 0) ? 1 : 0;
                            syncControllerInputSlots();
                        } else {
                            moveMenuCursor(horizontal, 0);
                        }
                    } else {
                        moveMenuCursor(horizontal, vertical);
                    }
                } else if (state == MENU && (isMenuConfirmAlias(keyCode) || isMenuCancelAlias(keyCode)
                        || keyCode == KeyEvent.KEYCODE_BUTTON_START)) {
                    return true;
                }
                return true;
            }
            if (keyCode == KeyEvent.KEYCODE_F3) {
                debugOverlay = !debugOverlay;
                return true;
            }
            if (debugOverlay && keyCode == KeyEvent.KEYCODE_F4) {
                energy = 100;
                linkMeter = 100;
                return true;
            }
            if (keyCode == KeyEvent.KEYCODE_F1) return true;
            if (event.getRepeatCount() > 0 && !isControllerDirectionalKey(keyCode)
                    && keyCode != KeyEvent.KEYCODE_DPAD_RIGHT
                    && keyCode != KeyEvent.KEYCODE_DPAD_UP
                    && keyCode != KeyEvent.KEYCODE_DPAD_DOWN) return true;
            if (keyCode == KeyEvent.KEYCODE_ESCAPE || keyCode == KeyEvent.KEYCODE_BACK) {
                if (state == PLAY) enterState(PAUSE);
                else if (state == PAUSE) safeResumePlay();
                else handleMenuTap(320, 320);
                return true;
            }
            if (keyCode == KeyEvent.KEYCODE_BUTTON_START) {
                if (state == PLAY) {
                    enterState(PAUSE);
                } else if (state == PAUSE) {
                    safeResumePlay();
                } else {
                    keyboardConfirm();
                }
                return true;
            }
            switch (keyCode) {
                case KeyEvent.KEYCODE_DPAD_LEFT:
                case KeyEvent.KEYCODE_A: keyLeft = true; break;
                case KeyEvent.KEYCODE_DPAD_RIGHT:
                case KeyEvent.KEYCODE_D: keyRight = true; break;
                case KeyEvent.KEYCODE_DPAD_UP:
                case KeyEvent.KEYCODE_W: keyUp = true; break;
                case KeyEvent.KEYCODE_DPAD_DOWN:
                case KeyEvent.KEYCODE_S: keyDown = true; break;
                default:
                    if (!queueP1ActionByKey(keyCode)) return super.onKeyDown(keyCode, event);
                    return true;
                case KeyEvent.KEYCODE_SHIFT_LEFT:
                case KeyEvent.KEYCODE_SHIFT_RIGHT:
                case KeyEvent.KEYCODE_BUTTON_THUMBL: dashHeld = true; break;
            }
            return true;
        } catch (Throwable runtimeError) {
            Log.e(TAG, "onKeyDown crashed", runtimeError);
            enterState(MENU);
            clearInputs();
            return true;
        }
    }

    @Override
    public boolean onKeyUp(int keyCode, KeyEvent event) {
        try {
            if (event == null) return super.onKeyUp(keyCode, event);
            InputDevice inputDevice = event.getDevice();
            if (isGamepadSource(event.getSource())) {
                keyCode = ControllerCompat.normalizeKey(
                        inputDevice == null ? "" : inputDevice.getName(), keyCode);
            }
            int source = event.getSource();
            int controllerSlot = resolveControllerSlot(event.getDeviceId(), source);
            if (isGamepadSource(source) || isNavigationSource(source)) {
                updateControllerIds(event.getDeviceId(), source, controllerSlot);
                if ((source & (InputDevice.SOURCE_GAMEPAD | InputDevice.SOURCE_JOYSTICK)) != 0) {
                    gamepadUiActive = true;
                }
            }
            boolean p2ByDevice = hasCompanionController() && controllerSlot == 1;
            if (state == PLAY && p2ByDevice) {
                switch (keyCode) {
                    case KeyEvent.KEYCODE_DPAD_LEFT: p2Left = false; break;
                    case KeyEvent.KEYCODE_DPAD_RIGHT: p2Right = false; break;
                    case KeyEvent.KEYCODE_DPAD_UP: p2Up = false; break;
                    case KeyEvent.KEYCODE_DPAD_DOWN: p2Down = false; break;
                    default:
                        clearP2ActionStateByKey(keyCode);
                        break;
                }
                return true;
            }
            switch (keyCode) {
                case KeyEvent.KEYCODE_DPAD_LEFT:
                case KeyEvent.KEYCODE_A: keyLeft = false; break;
                case KeyEvent.KEYCODE_DPAD_RIGHT:
                case KeyEvent.KEYCODE_D: keyRight = false; break;
                case KeyEvent.KEYCODE_DPAD_UP:
                case KeyEvent.KEYCODE_W: keyUp = false; break;
                case KeyEvent.KEYCODE_DPAD_DOWN:
                case KeyEvent.KEYCODE_S: keyDown = false; break;
                case KeyEvent.KEYCODE_SHIFT_LEFT:
                case KeyEvent.KEYCODE_SHIFT_RIGHT:
                case KeyEvent.KEYCODE_BUTTON_THUMBL: dashHeld = false; break;
                case KeyEvent.KEYCODE_BUTTON_L2: leftTriggerDown = false; break;
                case KeyEvent.KEYCODE_BUTTON_R2: rightTriggerDown = false; break;
                default:
                    clearP1ActionStateByKey(keyCode);
                    break;
            }
            return true;
        } catch (Throwable runtimeError) {
            Log.e(TAG, "onKeyUp crashed", runtimeError);
            return super.onKeyUp(keyCode, event);
        }
    }

    private void keyboardConfirm() {
        try {
            audio.play(AudioController.CONFIRM);
            resetMenuHats();
            if (state == TITLE) {
                menuChoice = hasCheckpoint ? 0 : 1;
                enterState(MENU);
            } else if (state == MENU) {
                if (menuChoice == 0) {
                    if (restoreCheckpoint()) enterState(PLAY);
                    else menuChoice = 1;
                } else if (menuChoice == 4) {
                    settingsReturn = MENU;
                    enterState(SETTINGS);
                } else {
                    trainingMode = menuChoice == 3;
                    twoPlayerMode = menuChoice == 2;
                    enterState(SELECT);
                }
            } else if (state == SELECT) {
                if (!twoPlayerMode) {
                    p1Ready = true;
                    selectedHero2 = sanitizeHeroIndex(selectedHero);
                    if (canStartBattle() && tryConfirmSelectionToStart()) {
                        clampHeroIndexesForPlay();
                    }
                    return;
                }
                if (!hasCompanionController()) {
                    if (!p1Ready) {
                        p1Ready = true;
                        activeSelectionSlot = 1;
                        syncControllerInputSlots();
                        return;
                    } else {
                        selectedHero2 = sanitizeHeroIndex(selectedHero2);
                        p2Ready = true;
                        activeSelectionSlot = 1;
                    }
                    syncControllerInputSlots();
                    if (canStartBattle() && tryConfirmSelectionToStart()) {
                        clampHeroIndexesForPlay();
                    }
                    return;
                } else if (!isBattleReady()) {
                    if (activeSelectionSlot == 0) p1Ready = true;
                    else p2Ready = true;
                    syncControllerInputSlots();
                    return;
                }
                if (!isBattleReady()) return;
                if (canStartBattle() && tryConfirmSelectionToStart()) {
                    clampHeroIndexesForPlay();
                }
            } else if (state == INTRO) {
                safeEnterPlayFromIntro();
            } else if (state == PAUSE || state == SETTINGS || state == RESULTS
                    || state == GAME_OVER || state == GALLERY) {
                activateSelectedMenuAction();
            }
        } catch (Throwable runtimeError) {
            Log.e(TAG, "keyboardConfirm failed", runtimeError);
            p1Ready = false;
            p2Ready = false;
            syncControllerInputSlots();
            enterState(MENU);
        }
    }

    private void safeEnterPlayFromIntro() {
        try {
            if (!tryConfirmSelectionToStart()) {
                finishSelectionTransition();
                enterState(SELECT);
                return;
            }
            beginSelectionTransition();
            clearCheckpoint();
            resetGame();
            saveCheckpoint(0);
            enterState(PLAY);
            finishSelectionTransition();
        } catch (Throwable runtimeError) {
            Log.e(TAG, "Failed to enter PLAY", runtimeError);
            clearInputs();
            enterState(MENU);
            finishSelectionTransition();
        }
    }

    private void safeResumePlay() {
        try {
            enterState(PLAY);
        } catch (Throwable runtimeError) {
            Log.e(TAG, "Failed to resume PLAY", runtimeError);
            clearInputs();
            enterState(MENU);
        }
    }

    private void keyboardCancel() {
        try {
            p1Ready = false;
            p2Ready = false;
            if (state == PAUSE || state == SELECT || state == INTRO || state == RESULTS
                    || state == GAME_OVER || state == GALLERY) {
                menuChoice = 0;
                if (!hasCheckpoint) menuChoice = 1;
                enterState(MENU);
            } else if (state == SETTINGS) {
                enterState(settingsReturn);
            } else if (state == MENU) {
                enterState(TITLE);
            }
        } catch (Throwable runtimeError) {
            Log.e(TAG, "keyboardCancel failed", runtimeError);
            enterState(MENU);
        }
    }

    private void activateSelectedMenuAction() {
        switch (state) {
            case TITLE:
                menuChoice = hasCheckpoint ? 0 : 1;
                enterState(MENU);
                break;
            case MENU:
                if (menuChoice == 0) {
                    if (restoreCheckpoint()) enterState(PLAY);
                    else menuChoice = 1;
                } else if (menuChoice == 4) {
                    settingsReturn = MENU;
                    enterState(SETTINGS);
                } else {
                    trainingMode = menuChoice == 3;
                    twoPlayerMode = menuChoice == 2;
                    enterState(SELECT);
                }
                break;
            case SELECT:
                if (!twoPlayerMode) {
                    p1Ready = true;
                    selectedHero2 = sanitizeHeroIndex(selectedHero);
                    if (canStartBattle() && tryConfirmSelectionToStart()) {
                        clampHeroIndexesForPlay();
                    }
                    break;
                }
                if (!hasCompanionController()) {
                    if (!p1Ready) {
                        p1Ready = true;
                        activeSelectionSlot = 1;
                        syncControllerInputSlots();
                        break;
                    }
                    selectedHero2 = sanitizeHeroIndex(selectedHero2);
                    p2Ready = true;
                    activeSelectionSlot = 1;
                    syncControllerInputSlots();
                    if (canStartBattle() && tryConfirmSelectionToStart()) {
                        clampHeroIndexesForPlay();
                    }
                    break;
                } else {
                    int activeSlot = activeSelectionSlot;
                    if (!p1Ready || !p2Ready) {
                        if (activeSlot == 0) {
                            p1Ready = true;
                        } else {
                            p2Ready = true;
                        }
                        syncControllerInputSlots();
                        break;
                    }
                }
                if (!tryConfirmSelectionToStart()) {
                    break;
                }
                break;
            case INTRO:
                safeEnterPlayFromIntro();
                break;
            case PAUSE:
                if (pauseOption == 0) {
                    safeResumePlay();
                } else if (pauseOption == 1) {
                    settingsReturn = PAUSE;
                    enterState(SETTINGS);
                } else if (pauseOption == 2) {
                    safeEnterPlayFromIntro();
                } else if (pauseOption == 3) {
                    enterState(MENU);
                }
                break;
            case SETTINGS:
                if (settingsOption == 0) {
                    musicEnabled = !musicEnabled;
                    audio.setMusicEnabled(musicEnabled);
                    break;
                }
                if (settingsOption == 1) {
                    sfxEnabled = !sfxEnabled;
                    audio.setSfxEnabled(sfxEnabled);
                    break;
                }
                if (settingsOption == 2) {
                    hapticsEnabled = !hapticsEnabled;
                    break;
                }
                if (settingsOption == 3) {
                    shakeEnabled = !shakeEnabled;
                    break;
                }
                if (settingsOption == 4) {
                    difficulty = (difficulty + 1) % 3;
                    break;
                }
                if (settingsOption == 5) {
                    saveSettings();
                    enterState(settingsReturn);
                }
                break;
            case RESULTS:
                if (resultsOption == 0) {
                    enterState(INTRO);
                } else if (resultsOption == 1) {
                    enterState(MENU);
                }
                break;
            case GAME_OVER:
                if (gameOverOption == 0) {
                    safeEnterPlayFromIntro();
                } else if (gameOverOption == 1) {
                    enterState(MENU);
                }
                break;
            case GALLERY:
                enterState(MENU);
                break;
            default:
                break;
        }
    }

    private void moveMenuCursor(int horizontal, int vertical) {
        if (state == MENU && (vertical != 0 || horizontal != 0)) {
            if (horizontal != 0) menuChoice = (menuChoice + (horizontal > 0 ? 1 : -1) + 5) % 5;
            else if (vertical != 0) menuChoice = (menuChoice + (vertical > 0 ? 1 : -1) + 5) % 5;
            return;
        }
        if (state == SELECT && horizontal != 0) {
            if (hasCompanionController()) {
                if (activeSelectionSlot == 1) {
                    selectedHero2 = sanitizeHeroIndex(selectedHero2 + (horizontal > 0 ? 1 : -1));
                    p2Ready = false;
                } else {
                    selectedHero = sanitizeHeroIndex(selectedHero + (horizontal > 0 ? 1 : -1));
                    p1Ready = false;
                }
                return;
            }
            if (activeSelectionSlot == 1) {
                selectedHero2 = sanitizeHeroIndex(selectedHero2 + (horizontal > 0 ? 1 : -1));
                p2Ready = false;
            } else {
                selectedHero = sanitizeHeroIndex(selectedHero + (horizontal > 0 ? 1 : -1));
                p1Ready = false;
            }
            syncControllerInputSlots();
            return;
        }
        if (state == PAUSE) {
            pauseOption += vertical != 0 ? (vertical > 0 ? 1 : -1) : 0;
            pauseOption = clampInt(pauseOption, 0, 3);
            if (horizontal < 0 && pauseOption > 0) pauseOption--;
            else if (horizontal > 0 && pauseOption < 3) pauseOption++;
            return;
        }
        if (state == SETTINGS) {
            if (vertical != 0 || horizontal != 0) {
                settingsOption += vertical != 0 ? (vertical > 0 ? 1 : -1) : 0;
                settingsOption = clampInt(settingsOption, 0, 5);
            }
        }
        if (state == RESULTS) {
            if (horizontal != 0 || vertical != 0) resultsOption = (resultsOption + 1) % 2;
        }
        if (state == GAME_OVER) {
            if (horizontal != 0 || vertical != 0) gameOverOption = (gameOverOption + 1) % 2;
        }
    }

    private void applyDirectionalActionForMenu(int horizontal, int vertical) {
        moveMenuCursor(horizontal, vertical);
    }

    @Override
    public boolean onGenericMotionEvent(MotionEvent event) {
        try {
        if (event == null || !isNavigationSource(event.getSource())
                || event.getAction() != MotionEvent.ACTION_MOVE) {
            return super.onGenericMotionEvent(event);
        }
        int source = event.getSource();
        long now = SystemClock.uptimeMillis();
        int controllerSlot = resolveControllerSlot(event.getDeviceId(), source);
        updateControllerIds(event.getDeviceId(), source, controllerSlot);
        if ((source & (InputDevice.SOURCE_GAMEPAD | InputDevice.SOURCE_JOYSTICK)) != 0) {
            gamepadUiActive = true;
        }
        if (!isGamepadSource(source) && primaryControllerId < 0) {
            return super.onGenericMotionEvent(event);
        }
        if (!isGamepadSource(source) && controllerSlot == 0) {
            return super.onGenericMotionEvent(event);
        }
        boolean isSecond = hasCompanionController()
                ? (controllerSlot == 1 && isDedicatedCompanion())
                : (! (state == PLAY) && activeSelectionSlot == 1);
        if (isSecond) {
            float p2x = readHorizontalAxis(event);
            float p2y = readVerticalAxis(event);
            float p2hatX = centeredAxis(event, MotionEvent.AXIS_HAT_X);
            float p2hatY = centeredAxis(event, MotionEvent.AXIS_HAT_Y);
            if (state != PLAY) {
                if (Math.abs(p2hatX) <= 0.17f && Math.abs(p2x) > MENU_NAV_AXIS_THRESHOLD) {
                    p2hatX = p2x;
                }
                if (Math.abs(p2hatY) <= 0.17f && Math.abs(p2y) > MENU_NAV_AXIS_THRESHOLD) {
                    p2hatY = p2y;
                }
                int hx = Math.abs(p2hatX) > MENU_NAV_AXIS_THRESHOLD ? (p2hatX > 0f ? 1 : -1) : 0;
                int hy = Math.abs(p2hatY) > MENU_NAV_AXIS_THRESHOLD ? (p2hatY > 0f ? 1 : -1) : 0;
                if (!hasCompanionController() && state == SELECT && hy != 0) {
                    if (shouldAcceptMenuAxisStep(hy, menuHatYPlayer2, true, now)) {
                        activeSelectionSlot = (activeSelectionSlot == 0) ? 1 : 0;
                        syncControllerInputSlots();
                        lastMenuNavAtPlayer2 = now;
                    }
                    menuHatXPlayer2 = hx;
                    menuHatYPlayer2 = hy;
                    return true;
                }
                if (hx != 0) {
                    if (shouldAcceptMenuAxisStep(hx, menuHatXPlayer2, true, now)) {
                        navigateMenu(hx, 0, true);
                        lastMenuNavAtPlayer2 = now;
                    }
                }
                if (hy != 0) {
                    if (shouldAcceptMenuAxisStep(hy, menuHatYPlayer2, true, now)) {
                        navigateMenu(0, hy, true);
                        lastMenuNavAtPlayer2 = now;
                    }
                }
                menuHatXPlayer2 = hx;
                menuHatYPlayer2 = hy;
                return true;
            }
            p2Left = p2x < -0.2f; p2Right = p2x > 0.2f;
            p2Up = p2y < -0.2f; p2Down = p2y > 0.2f;
            boolean nextP2LeftTrigger = Math.max(
                    event.getAxisValue(MotionEvent.AXIS_LTRIGGER),
                    event.getAxisValue(MotionEvent.AXIS_BRAKE)) > 0.55f;
            boolean nextP2RightTrigger = Math.max(
                    event.getAxisValue(MotionEvent.AXIS_RTRIGGER),
                    event.getAxisValue(MotionEvent.AXIS_GAS)) > 0.55f;
            if (nextP2LeftTrigger && !p2LeftTriggerDown) p2ThrowQueued = true;
            if (nextP2RightTrigger && !p2RightTriggerDown) p2HeavyKickQueued = true;
            p2LeftTriggerDown = nextP2LeftTrigger;
            p2RightTriggerDown = nextP2RightTrigger;
            return true;
        }
        moveX = readHorizontalAxis(event);
        moveY = readVerticalAxis(event);
        float hatX = centeredAxis(event, MotionEvent.AXIS_HAT_X);
        float hatY = centeredAxis(event, MotionEvent.AXIS_HAT_Y);
        if (state != PLAY) {
            if (Math.abs(hatX) <= 0.17f && Math.abs(moveX) > MENU_NAV_AXIS_THRESHOLD) {
                hatX = moveX;
            }
            if (Math.abs(hatY) <= 0.17f && Math.abs(moveY) > MENU_NAV_AXIS_THRESHOLD) {
                hatY = moveY;
            }
            int hx = Math.abs(hatX) > MENU_NAV_AXIS_THRESHOLD ? (hatX > 0f ? 1 : -1) : 0;
            int hy = Math.abs(hatY) > MENU_NAV_AXIS_THRESHOLD ? (hatY > 0f ? 1 : -1) : 0;
            if (hx != 0) {
                if (shouldAcceptMenuAxisStep(hx, menuHatX, false, now)) {
                    navigateMenu(hx, 0, false);
                    lastMenuNavAt = now;
                }
            }
            if (hy != 0) {
                if (shouldAcceptMenuAxisStep(hy, menuHatY, false, now)) {
                    navigateMenu(0, hy, false);
                    lastMenuNavAt = now;
                }
            }
            menuHatX = hx;
            menuHatY = hy;
            return true;
        }
        if (Math.abs(hatX) > Math.abs(moveX)) moveX = hatX;
        if (Math.abs(hatY) > Math.abs(moveY)) moveY = hatY;
        boolean nextLeftTrigger = Math.max(
                event.getAxisValue(MotionEvent.AXIS_LTRIGGER),
                event.getAxisValue(MotionEvent.AXIS_BRAKE)) > 0.55f;
        boolean nextRightTrigger = Math.max(
                event.getAxisValue(MotionEvent.AXIS_RTRIGGER),
                event.getAxisValue(MotionEvent.AXIS_GAS)) > 0.55f;
        if (state == PLAY) {
            if (nextLeftTrigger && !leftTriggerDown) throwQueued = true;
            if (nextRightTrigger && !rightTriggerDown) heavyKickQueued = true;
        }
        leftTriggerDown = nextLeftTrigger;
        rightTriggerDown = nextRightTrigger;
        return true;
        } catch (Throwable runtimeError) {
            Log.w(TAG, "Motion event rejected", runtimeError);
            return false;
        }
    }

    private float readHorizontalAxis(MotionEvent event) {
        return centeredAxis(event, MotionEvent.AXIS_X);
    }

    private float readVerticalAxis(MotionEvent event) {
        return centeredAxis(event, MotionEvent.AXIS_Y);
    }

    private float centeredAxis(MotionEvent event, int axis) {
        InputDevice device = event.getDevice();
        if (device == null) return 0f;
        InputDevice.MotionRange range = device.getMotionRange(axis, event.getSource());
        if (range == null) return 0f;
        float value = event.getAxisValue(axis);
        float center = (range.getMin() + range.getMax()) * 0.5f;
        float halfRange = Math.max(0.0001f, (range.getMax() - range.getMin()) * 0.5f);
        float normalized = Math.max(-1f, Math.min(1f, (value - center) / halfRange));
        float normalizedFlat = Math.min(0.45f, Math.max(0.16f, range.getFlat() / halfRange));
        return Math.abs(normalized) > normalizedFlat ? normalized : 0f;
    }

    private void saveSettings() {
        prefs.edit()
                .putBoolean("music", musicEnabled)
                .putBoolean("sfx", sfxEnabled)
                .putBoolean("haptics", hapticsEnabled)
                .putBoolean("shake", shakeEnabled)
                .putInt("difficulty", difficulty)
                .putFloat("touch_opacity", touchOpacity)
                .apply();
    }

    private static boolean inside(float x, float y, float l, float t, float r, float b) {
        return x >= l && x <= r && y >= t && y <= b;
    }

    private static float distance(float x, float y, float cx, float cy) {
        float dx = x - cx;
        float dy = y - cy;
        return (float) Math.sqrt(dx * dx + dy * dy);
    }

    private static float clamp(float value, float min, float max) {
        return Math.max(min, Math.min(max, value));
    }

    private static int clampInt(int value, int min, int max) {
        if (value < min) return min;
        if (value > max) return max;
        return value;
    }

    private static final class MoveSpec {
        final String name;
        final int fps;
        final int hitFrame;
        final float reach;
        final float laneHalfHeight;
        final float damageMultiplier;
        final int hitPauseTicks;
        final int recoveryTicks;
        final boolean launches;

        MoveSpec(String name, int fps, int hitFrame, float reach, float laneHalfHeight,
                 float damageMultiplier, int hitPauseTicks, int recoveryTicks,
                 boolean launches) {
            this.name = name;
            this.fps = fps;
            this.hitFrame = hitFrame;
            this.reach = reach;
            this.laneHalfHeight = laneHalfHeight;
            this.damageMultiplier = damageMultiplier;
            this.hitPauseTicks = hitPauseTicks;
            this.recoveryTicks = recoveryTicks;
            this.launches = launches;
        }
    }

    private static final class Enemy {
        boolean alive;
        boolean active;
        boolean facingRight;
        int zone;
        int type;
        int hp;
        int maxHp;
        int attackCooldown;
        int attackTimer;
        int attackVariant;
        int attackTargetSlot;
        int state;
        int stateTicks;
        int stun;
        int flash;
        int lastHitSerial;
        int lastObjectHitSerial;
        int lastP1HitFrame;
        int lastP2HitFrame;
        int lastTeamComboFrame;
        boolean attackHitFired;
        boolean defeated;
        float x;
        float y;
        float z;
        float vx;
        float vy;
        float vz;
        final SpriteAnimator animator = new SpriteAnimator();
    }

    private static final class Item {
        boolean active;
        int type;
        int life;
        float x;
        float y;
        float z;
        float vx;
        float vy;
        float vz;
    }

    private static final class WorldObject {
        boolean active;
        boolean held;
        boolean thrown;
        int type;
        int hp;
        int durability;
        int life;
        int lastHitSerial;
        int throwSerial;
        float x;
        float y;
        float z;
        float vx;
        float vy;
        float vz;
        float angle;
        float angularVelocity;
    }

    private static final class SpriteEffect {
        boolean active;
        Bitmap bitmap;
        int columns;
        int rows;
        int frames;
        int frame;
        int ticks;
        float x;
        float y;
        float z;
        float scale;
    }

    private static final class AssistActor {
        boolean active;
        boolean facingRight;
        boolean hitFired;
        int hero;
        int ownerSlot;
        int phase;
        int ticks;
        float x;
        float y;
        float targetX;
    }

    private static final class Particle {
        boolean active;
        int kind;
        int life;
        int maxLife;
        int color;
        float x;
        float y;
        float vx;
        float vy;
        float size;
        float rotation;
    }
}
