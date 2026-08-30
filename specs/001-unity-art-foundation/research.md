# Phase 0 Research — Unity Art Foundation

## نطاق البحث

تمت مراجعة مصادر رسمية فقط من Unity وAndroid في 2026-08-30. لا يوجد في هذه
المصادر رقم سحري لدقة شخصية beat-'em-up؛ أفضل ممارسة مشتركة هي اختيار أصغر
texture يطابق حجم العرض الفعلي، ضغطها بتنسيق مدعوم فعليًا، ثم قياس الذاكرة
والـframe pacing على الجهاز المستهدف. لذلك تفصل هذه الخطة بين القواعد الثابتة
وبين القيم التي يجب قفلها بعد A/B.

## المصادر الرسمية

1. Unity 6 — Sprite Atlas Reference:
   https://docs.unity3d.com/6000.0/Documentation/Manual/sprite/atlas/sprite-atlas-reference.html
2. Unity 6 — Sprite texture import settings:
   https://docs.unity3d.com/6000.0/Documentation/Manual/texture-type-sprite.html
3. Unity 6 — GPU texture format selection by platform:
   https://docs.unity3d.com/6000.0/Documentation/Manual/texture-choose-format-by-platform.html
4. Unity 6 — GPU texture formats reference:
   https://docs.unity3d.com/6000.0/Documentation/Manual/texture-formats-reference.html
5. Unity 6 — Animator Override Controller:
   https://docs.unity3d.com/6000.0/Documentation/Manual/AnimatorOverrideController.html
6. Unity 6 — 2D Pixel Perfect package:
   https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.2d.pixel-perfect.html
7. Unity 6 — Memory Profiler:
   https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.memoryprofiler.html
8. Android Developers — Optimize memory usage on TV:
   https://developer.android.com/training/tv/playback/memory
9. Android Developers — Reduce game size / inspect textures:
   https://developer.android.com/games/optimize/game-size
10. Android Developers — Slow Sessions and Unity frame pacing:
    https://developer.android.com/games/optimize/vitals/slow-session
11. Android Developers — Unity game setup and frame pacing:
    https://developer.android.com/games/engines/unity/start-in-unity

## Decision 1 — PPI is rejected as the production unit

**Decision**: use `PPU + camera world height + render resolution + actor body
bounds`, not PPI.

**Rationale**: PPI needs the physical screen size in inches and varies between
phones and televisions. Unity's Sprite importer defines `Pixels Per Unit`, which
maps source pixels to world units. Visual density must then be verified in screen
pixels at 720p/1080p.

**Alternatives rejected**:

- One PPI value for all screens: cannot guarantee the same world or visual size.
- Transform scale per actor: reproduces the current inconsistent texel density.

## Decision 2 — Separate high-resolution masters from Runtime

**Decision**: one transparent Master file per Frame, long side at least 2048px,
outside Runtime; create deterministic runtime derivatives and ship derivatives only.

**Rationale**: Android recommends avoiding textures larger than their eventual
display size. A UHD source is useful for redrawing, facial consistency and future
exports, but loading it in the APK wastes GPU memory. The master is evidence, not
the runtime texture.

**Alternatives rejected**:

- Put 2K/4K Frames directly in Sprite Atlas: excessive decoded texture memory.
- Generate a sheet containing multiple poses: violates per-Frame traceability and
  makes identity/crop errors harder to isolate.

## Decision 3 — Runtime resolution is calibrated, not guessed

**Decision**: A/B 320, 384 and 512 logical derivatives before locking Art Contract
v1. Candidate architecture is 512 high plus 0.75/0.5 Sprite Atlas Variants, loaded
mutually exclusively by render tier.

**Rationale**: a 512 source can be clearer on 1080p but can also be downsampled on
720p and waste memory. A Variant can preserve the same world size while lowering
texture density. The smallest visually equivalent derivative wins.

**Alternatives rejected**:

- Lock 512 immediately: not justified until Xiaomi memory and shimmer are measured.
- Use one 192px source and enlarge it: this caused visible coarse pixels already.

## Decision 4 — Sprite Atlas is retained with conservative packing

**Decision**: Atlas per actor, max page 2048, rotation off, offline alpha trim,
padding >=8, mipmaps off, Read/Write off. Tight packing remains off until geometry
and pivot parity tests pass.

**Rationale**: Unity documents padding as the guard against neighboring sprite
overlap and notes that Read/Write creates a texture copy, increasing memory. Atlas
packing reduces texture switches, but aggressive packing must not reintroduce crop
or pivot errors.

**Alternatives rejected**:

- One Atlas for every actor/stage: forces unrelated art to stay resident.
- Runtime trimming: risks first-use CPU spikes and nondeterministic results.
- Read/Write enabled permanently: unnecessary duplicate texture memory.

## Decision 5 — Compression is an acceptance test

**Decision**: use RGBA32 as visual reference, ETC2 RGBA8 as GLES3 compatibility
candidate, and ASTC 4x4 as a device-tested quality candidate. Reject ASTC 6x6/8x8
for fine character art in Phase 1. Select per build/atlas only after image and device
A/B.

**Rationale**: Unity states ETC2 is supported by GLES3 devices; ASTC is supported
by most modern Android GPUs but not universally. Unsupported formats may be
decompressed at runtime, increasing load time and memory. The project builds GLES3
and distributes APK directly, so a single unsupported choice is risky.

**Alternatives rejected**:

- RGBA32 for all characters: highest fidelity but may exceed low-RAM TV graphics memory.
- ASTC 6x6/8x8: stronger compression can soften one-pixel facial and outline detail.
- Choose by APK size alone: compressed file size does not prove resident memory or clarity.

## Decision 6 — Animator presentation does not own gameplay

**Decision**: Base Animator Controllers plus an Animator Override per actor.
`PlayerMotor` and combat action data remain authoritative; no root motion.
Normalized transition times are used. Animation Events are limited to presentation
or generated from the same action timeline.

**Rationale**: Unity's Override Controller preserves state-machine structure while
replacing clips, which fits customer-specific actors. Unity warns that transition
exit times should be normalized when clip lengths differ. Keeping mechanics outside
the clip prevents art replacement from changing damage or movement.

**Alternatives rejected**:

- A distinct hand-built state machine for every customer: expensive and prone to drift.
- Root motion from sprite frames: changes established controls and collision timing.
- Fixed 12 FPS for every action: produces wrong duration when frame counts differ.

## Decision 7 — 60 render FPS and >=12 unique animation Frames are separate rules

**Decision**: target render at 60 FPS with Android Optimized Frame Pacing enabled;
every approved action contains at least 12 unique Frames and its own playback rate
of at least 12 frames/sec.

**Rationale**: Android describes 30 or 60 FPS as common game targets and Unity can
use Android Frame Pacing to reduce uneven presentation. Animation sample rate does
not need to equal render rate, but it must not be used to inflate uniqueness.

**Alternatives rejected**:

- 12 render FPS: unacceptable input and camera smoothness.
- Duplicate six drawings to claim 12 frames: no additional motion information.

## Decision 8 — True alpha and human edge review are both mandatory

**Decision**: character pixels use alpha 0/255; partial alpha belongs to separate
FX. Source background is transparent from creation. Validate over black, white and
magenta, then require human sign-off.

**Rationale**: automated alpha checks cannot tell whether an opaque white edge is
intentional armor shine or an unwanted matte. This project previously had binary
alpha yet still displayed white painted edge pixels, so both structural and visual
checks are required.

**Alternatives rejected**:

- Chroma-key removal: destroys green actors such as Adam and causes halos.
- Validator-only approval: cannot judge face identity or unwanted iconography reliably.

## Decision 9 — Low-RAM TV is the release baseline

**Decision**: measure on Xiaomi Stick first, then Shield. Preload active actor
Atlases before gameplay and unload inactive stage/actor content. Use Memory Profiler
and `dumpsys meminfo`, not estimates alone.

**Rationale**: Android documents that TV devices can have 1GB RAM even when video
resolution is 1080p and gives conservative 1GB targets of 30–40MB Graphics and
280MB total. Memory pressure can cause frame drops, reclaim pauses or process death.

**Alternatives rejected**:

- Optimize only for Shield: hides failures on the commercial minimum device.
- Lazy-load at first enemy/attack: repeats the hitch already seen in the old engine.

## Open measurement resolved during implementation

Only one technical value remains intentionally unlocked: the selected Runtime
derivative/Variant tier. It is not a product ambiguity; Phase 0 defines the exact
A/B and pass/fail criteria that resolve it before asset production.
