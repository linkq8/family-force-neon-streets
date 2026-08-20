# Family Force: Street Rescue

> **Current direction:** the project has moved to a native Android successor,
> `Family Force: Neon Streets`, with modern menus, items, touch/gamepad input,
> higher-resolution artwork, and Higgsfield music. See
> [`android/README.md`](android/README.md). The SNES version below remains as a
> preserved playable prototype.

`Family Force: Street Rescue` is an original SNES homebrew belt brawler for
one or two local players. It is inspired by the feel of 16-bit arcade
beat-'em-ups, while using original characters, enemies, stage art, music, and
code.

## Playable alpha

The current alpha includes:

- four selectable family hero slots;
- a four-card character-select screen with large face portraits and separate
  Player 1/Player 2 cursors;
- one- or two-player couch co-op;
- 32x64 gameplay fighters assembled from two native SNES objects, with
  two-frame walking, attack, and hurt poses;
- eight-way-feeling belt movement using the D-pad;
- light combos, heavy attacks, jumping/aerial attacks, and a family special;
- three street encounters with grunt, skater, brute, and Junk King enemies;
- title, character select, pause, victory, and game-over states;
- an original looping SNES tracker song and six original BRR sound effects;
- NTSC/PAL timing adaptation;
- a standard, chipless 4 MiB FastROM LoROM image for SD-card flash carts.

The playable family sprites and face portraits are temporary original
placeholders; they are deliberately not presented as your family's likeness.
The photo-derived character pass begins after the family reference photos are
added. The generated enemy/background/logo concepts are in
`assets/higgsfield/`; the hardware-safe development art is in `assets/dev/`.

## Controls

| Control | Action |
|---|---|
| D-pad | Move left/right and up/down the street |
| Y | Light attack; press again to continue a combo |
| X | Heavy attack |
| B | Jump; press Y in the air for an aerial attack |
| A | Family special when the special meter has enough energy |
| Start | Confirm, pause, or resume |
| Player 2 Start | Join on the character-select screen |
| Player 2 Select | Leave on the character-select screen |

## Personalizing the four heroes

Place authorized, clear photos in the layout described in
[`photos/README.md`](photos/README.md). One clear image per person is enough
to start; a straight-on face plus a three-quarter or full-body photo is much
better. Please also provide the four display names and, optionally, a favorite
outfit color or recognizable accessory for each person.

At SNES sprite scale, hairstyle, silhouette, outfit color, and accessories
carry more likeness than tiny facial details. The character-select portraits
preserve the faces at a larger scale. Photos are reference inputs;
they are converted into game art and are never loaded by the console from the
SD card.

## Build and test

The project is pinned to PVSnesLib 4.6.0. Because that SDK cannot build from a
physical path containing spaces, the wrapper safely stages the source in a
temporary no-space directory and copies only validated release artifacts back
to `dist/`.

```sh
./tools/build.sh
./tools/test.sh
```

Release ROM:

```text
dist/family-force-street-rescue.sfc
```

See [`PLAY_ON_SNES.md`](PLAY_ON_SNES.md) for SD-card and console steps.

## Project layout

```text
src/                    portable deterministic game core + SNES front end
assets/dev/             indexed, tile-safe development art
assets/higgsfield/      Higgsfield concept outputs
audio/                  original IT, WAV, and BRR audio
design/assets.csv       asset manifest and family-reference slots
photos/                 local, Git-ignored family reference inputs
tests/                  host simulation, audio, ROM, and emulator QA
tools/                  art/audio generation, build, and validation tools
dist/                   flash-cart ROM and debug symbols
```

PVSnesLib, Mesen, and Higgsfield remain separate tools/services with their own
licenses and terms. The procedural audio pack's license is documented in
[`audio/LICENSE.txt`](audio/LICENSE.txt).
