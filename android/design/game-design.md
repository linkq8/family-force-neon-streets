# Family Force: Neon Streets — Android vertical slice

## Product

`Family Force: Neon Streets` is an original landscape Android belt brawler for
phones, tablets, and Android handhelds. It keeps the family-friendly identity
of the SNES prototype while moving to a fluid, hand-drawn retro-modern arcade
presentation. It does not copy another game's characters, story, interface,
levels, music, or other protected assets.

## Frozen visual formula

High-detail retro arcade pixel art rendered at a modern 360p-to-720p game resolution, with fine 2–4 pixel clusters, crisp edges, selective dithering, and no oversized block pixels. Athletic readable silhouettes use dark navy outlines, expressive recognizable faces, dynamic foreshortening, and slightly exaggerated 1990s beat-’em-up proportions. Night streets use indigo, teal, and warm amber; heroes use distinct red-gold, green-purple, pink-ice, and blue-red palettes. Energetic family-friendly lighting and strong foreground contrast maintain a consistent three-quarter side-view belt-brawler perspective.

This paragraph is inserted byte-for-byte into every Higgsfield visual prompt.

## Release slice

- Landscape Android APK, minimum Android 8.0 (API 26), with measured-window
  layouts for compact phones, ultra-wide screens, multi-window, and unfolded
  Fold-style displays.
- Title, main menu, character select, settings, story stage, pause, victory,
  game-over, and results screens.
- Purposeful title, menu, selection, and chapter-intro motion that settles to
  an immediate static state when Android's Remove Animations setting is active.
- Four selectable family hero slots with different speed, power, reach, and
  special stats.
- One long neighborhood stage split into market, alley, and rooftop encounter
  zones, culminating in the original Junk King boss.
- Belt movement, dash, jump/air attack, direct punch and kick, direct heavy
  punch and heavy kick, meter-powered special, and visible Family Link assist.
- Pickups: food restores health, battery restores special meter, family token
  increases score, and bat/pipe/mallet/sign/cone tools can be equipped,
  swung, thrown, bounced, and broken. Crates and trash cans react to impacts
  and release rewards.
- Touch layout for one player, keyboard support for emulator QA, and Android
  gamepad input. The architecture leaves player two/controller two as a later
  expansion without changing the save or combat model.
- Music/SFX sliders, haptics toggle, difficulty, touch-control opacity, pause,
  retry, and quit-to-menu.
- Local settings and best score saved with Android SharedPreferences. No
  account, advertising, analytics, network permission, or in-app purchase.

## Screen flow

```text
Boot -> Title -> Main Menu -> Character Select -> Stage Intro -> Gameplay
                    |              |                         |-> Pause
                    |              |                         |-> Game Over -> Retry
                    |              |                         `-> Victory -> Results
                    `-> Settings <-'                                      `-> Menu
```

## Combat and controls

| Action | Touch | Gamepad / keyboard |
|---|---|---|
| Move | virtual stick | D-pad / left stick / arrows |
| Punch | PUNCH | gamepad X / Z |
| Kick | KICK | gamepad B / X |
| Heavy punch | H-P | gamepad Y / C |
| Heavy kick | H-K | gamepad R2 / V |
| Jump / air attack | JUMP, then an attack | gamepad A / Space |
| Family special | STAR | gamepad R1 / E |
| Family Link assist | LINK | gamepad L1 / Q |
| Throw held weapon | THROW | gamepad L2 / R |
| Dash | virtual-stick direction + dash modifier | left-stick click / Shift |
| Pause | pause icon | Start / Escape |

Combat uses a fixed 60 Hz simulation, forgiving input buffering, brief hit
stop, camera shake, knockback, invulnerability flashes, foreground sorting by
ground Y, and object pooling to avoid mobile frame-time spikes.

## Heroes

- `Essa` — original red-and-gold open-face armored titan with layered plating
  and the highest power/health; no protected logo or exact existing
  superhero costume.
- `Adam` — organic muscular green Hulk-style powerhouse with purple shorts,
  a clearly human face, and no metal plating or robotic parts.
- `Shaikha` — original pink ice princess in an age-appropriate coat-dress,
  leggings, boots, and snowflake motifs; not an existing animated character.
- `Sulaiman` — blue-and-red caped Superman-style sky hero with a prominent
  letter `S` chest emblem and a recognizable, age-appropriate face.

Gameplay silhouette scale follows the supplied standing heights rather than
giving every bitmap the same size:

| Hero | Age | Height | Relative to Essa |
|---|---:|---:|---:|
| Essa | adult | 177 cm | 1.000 |
| Adam | 5 | 108 cm | 0.610 |
| Shaikha | 5 | 108 cm | 0.610 |
| Sulaiman | 8 | 124 cm | 0.701 |

Adam's crouched source pose is compensated in the renderer so Adam and
Shaikha still read at the same standing height.

Direct-reference Higgsfield art is used for the current photo set. Reusable
Soul identities remain pending because Soul training needs at least five
varied photos per person. Generated art must preserve recognizable hairstyle,
face shape, skin tone, and age-appropriate proportions in the large selection
portrait; gameplay silhouettes remain readable at phone scale.

## Asset gate

The APK uses supplied authorized photos through direct-reference Higgsfield
generation. Each playable hero consumes an 8-column atlas with separate idle,
walk, punch, kick, heavy-punch, heavy-kick, jump, special, Link, hurt, and
knockdown rows. Each robot consumes a six-row idle/walk/two-attack/hurt/
knockdown atlas. Static masters remain a safe fallback if an atlas is missing;
source photos are never packaged in the APK.
