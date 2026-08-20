# Animation and combat implementation notes

Date: 2026-08-17

The weak-motion diagnosis is structural: the initial runtime draws one bitmap
per fighter and changes only its scale/position. The replacement uses actual
atlas frames, fighter states, frame-timed events, and visible reactions.

## Applied animation model

- Every clip has a fixed atlas row, frame count, playback rate, loop mode, and
  ground-foot pivot.
- Combat moves separate startup, active, and recovery time. Hit detection fires
  from the active animation frames, once per target per attack serial.
- Strong attacks preserve anticipation and follow-through instead of playing
  every drawing for equal time. Input buffering keeps those poses from making
  the controls feel delayed.
- Heroes and robots share idle, locomotion, attack, hurt, and knockdown states.
  The Link move visibly calls another family hero into the scene.
- Final body cells remain fixed-size and bottom-center anchored so animation
  cannot jitter when the opaque silhouette changes between frames.

Primary references:

- Mariel Cartwright, *Fluid and Powerful Character Animation* (GDC):
  https://www.gdcvault.com/play/1020017/Animation-Bootcamp-Fluid-and-Powerful
- Godot AnimationTree state-machine documentation:
  https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html

## Applied combat and prop physics

- Fighter simulation uses horizontal X, lane Y, elevation Z, and independent
  velocities. Shadows stay on lane Y while the visible sprite subtracts Z.
- Attacks first test lane-depth overlap, then directional attack range. Thrown
  props use impulses, gravity, ground friction, restitution, angular velocity,
  and one-hit-per-target serials.
- Held, dropped, and thrown weapons use image assets rather than Canvas lines.
  Breakable props react immediately and can release food, energy, or weapons.
- Enemy wind-up drawings provide the primary telegraph; warning overlays remain
  an accessibility aid.

Primary references:

- Box2D simulation manual (fixed stepping, impulses, restitution, filtering,
  and continuous collision concepts):
  https://box2d.org/documentation/md_simulation.html
- Santa Monica Studio, *Evolving Combat in God of War* (GDC):
  https://media.gdcvault.com/gdc2019/presentations/Sheth_Mihir_EvolvingCombat.pdf

## Android and Fold targets

- The game keeps deterministic 60 Hz simulation and measures frame pacing
  against the 16.7 ms display budget.
- Atlases are decoded outside the frame loop; only the selected hero and needed
  enemy sets are retained. Paint and rectangle objects are reused.
- Layout decisions use the measured app window. Fold-style near-square windows
  keep the complete scene above a dedicated control deck; ultra-wide windows
  move controls into side gutters.

Primary references:

- Android game-loop guidance:
  https://developer.android.com/games/develop/gameloops
- Android rendering and frame-pacing guidance:
  https://developer.android.com/topic/performance/vitals/render
- Android foldable guidance:
  https://developer.android.com/develop/adaptive-apps/guides/foldables/learn-about-foldables

