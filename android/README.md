# Family Force: Neon Streets (Android)

This is the primary successor to the SNES prototype: an original landscape
Android belt brawler with a fixed 60 Hz simulation and a 640×360 logical
canvas that scales cleanly to phones, tablets, TVs, and Android handhelds.

## Current playable vertical slice

- title, neighborhood-map, character-select, stage-intro, pause, settings,
  game-over, results, and gallery screens;
- animated neon title, menu-route, selection, and chapter-intro transitions
  that respect Android's Remove Animations setting;
- four selectable family heroes with distinct portraits, powers, stats, and
  high-detail retro pixel palettes;
- one scrolling three-encounter chapter and Junk King boss;
- atlas-driven idle, walk, punch, kick, heavy-punch, heavy-kick, jump, hurt,
  knockdown, special, and Family Link animation states;
- food, energy, score-token, bat, pipe, mallet, sign, and throwable-cone
  pickups, plus breakable crates and trash cans with arcade bounce physics;
- hit stop, screen shake, particles, warning tells, health/special/link HUD,
  haptics, touch controls, keyboard controls, and Android gamepad input;
- original Higgsfield environment art and two original Higgsfield Sonilo music
  loops, plus original effects;
- offline settings and best-score persistence, with no ads, analytics, network
  permission, account, or in-app purchases.
- adaptive layouts for compact landscape phones, ultra-wide devices, and
  unfolded Fold-style windows; expanded Fold windows use a dedicated touch
  control deck instead of stretching or clipping the 640×360 playfield.

The current family pack uses authorized photos as direct Higgsfield references.
It is a playable likeness preview: Essa is a red-and-gold armored titan, Adam
an organic green Hulk-style powerhouse, Shaikha a pink ice princess, and
Sulaiman a blue-and-red caped Superman-style hero with an `S` chest emblem.
For stronger identity consistency across full animation sheets, provide at
least five clear solo photos per person so a separate Higgsfield Soul can be
trained for each family member.

## Build

```sh
export JAVA_HOME="/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
export ANDROID_HOME="/Users/essa/Library/Android/sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"

cd android
./gradlew --no-daemon :app:assembleDebug
```

Debug APK:

```text
android/app/build/outputs/apk/debug/app-debug.apk
```

The workspace build wrapper validates every packaged image/audio contract,
checks the APK signature, publishes a convenient copy, and installs it when
an emulator or Android device is connected:

```sh
./tools/test_apk.sh
```

Published test APK:

```text
dist/family-force-neon-streets.apk
```

Install on a connected device or emulator:

```sh
"$ANDROID_HOME/platform-tools/adb" install -r \
  app/build/outputs/apk/debug/app-debug.apk
```

## Controls

Touch controls show eight direct picture buttons during gameplay. Keyboard,
emulator, and standard Android gamepad controls are:

| Keyboard | Gamepad | Action |
|---|---|---|
| WASD / arrows | left stick / D-pad | move |
| Z | X | punch |
| X | B | kick |
| C | Y | heavy punch |
| V | R2 | heavy kick |
| Space | A | jump |
| E | R1 | special |
| Q | L1 | Family Link assist |
| R | L2 | throw held weapon |
| Shift | left-stick click | dash |
| Escape | Start | pause/back |

See [`design/game-design.md`](design/game-design.md) for the product scope and
[`design/assets.csv`](design/assets.csv) for the generation manifest. The
photo/model/keying/pixel and emulator checks are recorded in
[`design/generation-audit.md`](design/generation-audit.md).
