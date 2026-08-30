# Visual Review Contract

## Required still-image pack

No generated video is required or permitted for this phase. Review uses live Unity
playback plus still evidence:

1. Blind A/B old vs candidate at exact gameplay size, no zoom.
2. 12-frame contact sheet per action, labels visible.
3. Reconstructed logical-canvas overlay with pivot, ground line and safe border.
4. Silhouette onion-skin for Frame 0 against every other Frame.
5. Four backgrounds: black, white, magenta `#FF00FF`, actual Stage 1 crop.
6. Left/right facing, with equipment and any text-bearing element checked.
7. 720p and1080p screenshots for 1P and2P.
8. Phone 20:9, Fold folded/unfolded and 1080-to-4K TV upscale screenshots.
9. RGBA32 vs ETC2 vs ASTC 4x4 crops at 100% scale.

## Reviewer rubric

Score each category from 1 to5:

- identity/face recognition: >=4
- face detail at actual size: >=4
- body/equipment stability: >=4
- natural motion and gait: >=4
- consistency with approved style: >=4
- crop/edge/halo: exactly5
- forbidden symbols/accidental letters: exactly5

An average cannot hide a failed category. Crop, edge or symbol failure is an
automatic rejection.

## Reviewer checklist

- Face remains the same person/type in every Frame.
- Armor/clothing silhouette, panels and palette remain stable.
- No body growth/shrink, foot sliding or baseline jump.
- Walk alternates both feet and opposite arms naturally.
- Punch has anticipation, impact and recovery; it does not merely move the whole image.
- No crop, wraparound, white edge, transparent hole or blur.
- Essa reads as a heavy iron cyborg, not astronaut.
- Grunt reads consistently with the approved Stage 1 visual family.
- No prohibited symbols or accidental letters.
- Candidate is clearer than v0.5 at actual size, not only when zoomed.

## Approval rule

All automated blockers must be zero. The owner then records exactly one of:

- `APPROVED`: eligible for device QA and integration.
- `REJECTED`: return the named actor/action batch only.
- `CONDITIONAL`: not integration-eligible; list corrections and repeat the full hash-bound review.

Approval is invalid if any Frame, manifest, importer, Atlas, clip, palette, prefab,
camera setting or contract hash changes.
