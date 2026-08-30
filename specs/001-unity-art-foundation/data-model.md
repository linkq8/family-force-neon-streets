# Data Model — Unity Art Foundation

## 1. ArtContractVersion

- `id`: semantic identifier such as `ff-art-1.0.0`
- `logical_canvas`: width/height used to compare all Frames
- `ppu`, `pivot`, `ground_line`
- `runtime_tiers`: scale, render range and memory tier
- `atlas_profile_id`, `palette_profile_id`
- `minimum_unique_frames`, timing limits
- `forbidden_symbol_policy_version`
- `validator_version`
- `created_at`, `approved_by`, `status`

States: `draft -> calibrated -> active -> superseded`. Only one active contract
can approve new art.

## 2. ActorArtProfile

- `actor_id`, `display_name`, `class` (`hero`, `regular_enemy`, `elite`, `boss`)
- `identity_reference_ids`
- body height range, shoulder/hip/head anchors and allowed drift
- palette and outline ranges
- approved costume/equipment details
- allowed marks and forbidden marks
- left-facing policy
- required action IDs
- source/rights metadata

## 3. AnimationDefinition

- `action_id`, `actor_id`
- ordered `frame_ids`
- `playback_fps`, loop flag, normalized duration
- logical phases: anticipation, active, recovery
- gait/contact annotations where relevant
- gameplay timeline reference
- visual event annotations for SFX/VFX/attachment
- expected body/foot exceptions with reason

An action cannot become `validated` with fewer than 12 unique Frames.

## 4. FrameMaster

- `frame_id`, `actor_id`, `action_id`, `sequence`
- source file hash, dimensions, RGBA mode
- source tool and rights record
- identity reference version and prompt recipe version
- review status

Masters never receive a Unity Runtime address and never ship in APK.

## 5. RuntimeSprite

- `frame_id`, derivative hash and contract version
- tier and conversion recipe hash
- logical canvas size
- trim rectangle and reconstructed bounds
- pivot in pixels and normalized coordinates
- alpha bounds, body bounds, foot/head/hip anchors
- palette statistics and perceptual hash
- destination Unity asset path

## 6. AtlasProfile / PackedAtlasResult

AtlasProfile:

- page max size, padding, rotation/tight/mipmap/read-write flags
- filter, wrap and sRGB settings
- platform compression candidates

PackedAtlasResult:

- actor/tier, atlas hashes, page count and dimensions
- predicted and measured decoded memory
- compression format and quality metrics
- loaded/unloaded residency evidence

## 7. ValidationFinding / ValidationReport

Finding fields:

- `rule_id`, severity (`blocker`, `error`, `warning`, `info`)
- actor/action/frame/tier
- expected, actual and numeric delta
- evidence artifact path
- waiver ID if allowed; blockers cannot be waived silently

Report fields:

- contract/validator/importer versions
- complete input hash tree
- findings and summary
- generated contact sheets
- deterministic command and environment
- status `pass` or `fail`

## 8. VisualApproval

- approval ID and status (`pending`, `approved`, `rejected`, `invalidated`)
- exact input hash tree and ValidationReport ID
- reviewer and timestamp
- devices/resolutions/backgrounds reviewed
- notes and comparison artifact hashes

Any changed input, importer setting, contract, Atlas result or clip invalidates the
approval and returns the package to `draft`.

## State flow

```text
FrameMaster draft
  -> static validation
  -> runtime derivation
  -> Atlas/Clip build
  -> automated report PASS
  -> human review APPROVED
  -> device QA PASS
  -> integrated candidate
  -> release eligible
```

Any failure returns only the affected actor/action batch to draft. Existing approved
fallback assets remain active until the final `integrated candidate` gate passes.
