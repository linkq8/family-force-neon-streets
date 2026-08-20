# Family image-generation audit

Date: 2026-08-17

## Identity inputs

| Hero | Authorized source photos | Current identity route | Soul status |
|---|---:|---|---|
| Essa | 2 | direct-reference generation | pending more photos |
| Adam | 1 | direct-reference generation | pending more photos |
| Shaikha | 1, with a solo face crop | direct-reference generation | pending more photos |
| Sulaiman | 1, with a solo face crop | direct-reference generation | pending more photos |

Higgsfield Soul training was not submitted. It requires at least five varied,
clear solo photos per person; 8–12 is preferred. The current faces are therefore
a provisional direct-reference pass rather than reusable trained identities.
Source photographs are not packaged in the APK.

## Generation process

- All family prompts contain the same frozen 75-word visual formula
  byte-for-byte. The formula in the design, generator, validator, and packaged
  manifest is identical.
- Primary portraits and masters used Higgsfield Nano Banana 2. Essa's current
  stronger red-and-gold armored master was regenerated at 2K from his front
  photo, three-quarter photo, and finished portrait in one primary attempt,
  then passed once through Higgsfield Image Background Remover. The previous
  Essa master is preserved outside the APK as a rollback source. Shaikha's
  earlier full-body recovery used GPT Image 2 from her finished portrait.
- Sulaiman's initial airborne cape silhouette was rejected during originality
  and gameplay-pose review. The remaining master attempt used GPT Image 2 to
  produce a grounded, non-cape wind guardian with an asymmetrical jacket,
  short scarf tails, and no shield, chest letter, bodysuit, or copied emblem.
- The interrupted Shaikha recovery had already completed; it was downloaded
  and continued without submitting a duplicate image generation.
- Every gameplay master was passed through Higgsfield Image Background
  Remover. Green was used for Essa, Shaikha, and Sulaiman; blue was used for
  Adam because his hero palette already contains green and purple.
- The launcher emblem was generated once with Higgsfield Recraft V4.1 at 2K,
  then packaged as Android legacy, round, adaptive, and Android 13 monochrome
  launcher resources. Its family-power emblem is original and contains no
  words or copied franchise logo.
- Designs are original, family-friendly archetypes. They contain no copied
  superhero logo, chest letter, exact costume, weapon, franchise text, or
  additional person.

## Packaged asset checks

| Asset class | Output | Palette limit | Pixel structure | Alpha checks |
|---|---|---:|---|---|
| gameplay masters | 256×384 RGBA | 96 RGB colors | exact 2×2 clusters | full opaque core, transparent margins, zero RGB under clear pixels |
| selection portraits | 256×256 RGBA | 112 RGB colors | exact 2×2 clusters | rounded transparent corners, zero RGB under clear pixels |

All four gameplay silhouettes retain at least eight pixels of transparent
margin on every side. The converter neutralizes saturated key-color fringe,
uses hard 0/255 pixel-art alpha, anchors each figure at bottom center, and uses
nearest-neighbor pixel scaling. The renderer compensates for each master's
opaque alpha bounds and applies the supplied real standing-height ratios: Essa
177 cm, Adam 108 cm, Shaikha 108 cm, and Sulaiman 124 cm. Essa is drawn at the
exact 128×192 half scale; Adam's crouched source pose is compensated so the two
five-year-olds read at the same standing height.

## Android verification

- Asset contract: 41 PNGs, 7 mono WAV effects, two stereo Vorbis music loops,
  51 manifested files, and the complete launcher icon set passed.
- Android lint, Android 14 install/start, and APK privacy/package checks passed;
  no fatal exception, ANR, or out-of-memory event appeared in logcat.
- Compact 640×360, ultra-wide 720×320, and Fold-style 1080×928 windows were
  inspected. The full scene remains visible, while the Fold layout moves touch
  input into a dedicated lower deck. The relocated joystick was exercised on
  the emulator and moved the hero correctly.
- Ultra-wide combat sample: 190 frames, 0 janky frames, with 5/5/5/6 ms at the
  50th/90th/95th/99th percentiles. Fold combat sample: 268 frames, 0 janky,
  0 missed-vsync frames, and 15/17/18/30 ms at the same percentiles.
- Title, menu, selection, and chapter-intro motion was also tested with Android
  animator scale disabled; every screen settled immediately into a complete
  static layout.
- APK Signature Scheme v2 verification passed.
- Published APK SHA-256:
  `8f359199f9702c9865531ab904e3a4ee8f5086f4f6afdade200afe45ec69c7dd`.

## Known limitation

This APK animates each identity master with runtime bob, lunge, hurt, jump, and
attack transforms. Fully identity-stable multi-frame walk and combat sheets
remain a later pass after each person has enough photos for a separate Soul.
