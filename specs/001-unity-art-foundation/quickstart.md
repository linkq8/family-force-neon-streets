# Quickstart — تنفيذ المرحلة الأولى لاحقًا

هذه الصفحة تحدد ترتيب التنفيذ والتحقق. الأوامر أسماء واجهات مخططة؛ لا تعد ناجحة
حتى تنفذ الأدوات في tasks اللاحقة.

## 1. Capture baseline

```bash
cd unity
python3 tools/art_qa/capture_baseline.py --actors Essa Grunt --resolutions 1280x720 1920x1080
```

Expected: JSON يحفظ FPS، P50/P95/P99، PSS، texture residency، actor screen bounds،
first-spawn/attack timings وhash الأصول الحالية. يسجل ملف الجهاز: model/RAM/OS/
render resolution/Hz. لا يستبدل هذا القياس اختبار الجهاز الحقيقي.

## 2. Validate fixtures before real art

```bash
python3 tools/art_qa/validate_art.py --contract ../specs/001-unity-art-foundation/contracts/qa-rules.md --fixtures tools/art_qa/fixtures
```

Expected: valid fixtures PASS؛ كل invalid fixture يفشل بالـrule ID المتوقع. إذا
تعطلت الأداة أو غاب contract فالنتيجة FAIL، لا skip.

## 3. Prove Animator with fallback art

Create Clips and Overrides using current sprites first. Run the full input/combat
regression: remote, DualSense, touch, 1P/2P, pickup/swing/throw/re-pickup, grab/team,
score/results. Hit-stop must freeze combat animation while UI remains responsive.

## 4. Calibrate runtime tier

```bash
python3 tools/art_qa/build_calibration_set.py --sizes 320 384 512 --actor Essa
```

Build three development APKs or mutually exclusive Atlas tiers. Run exact-size
still comparisons at 720p and1080p, then capture Memory Profiler and ADB evidence.
Record the selected size/variant in Art Contract before generating full motion.

## 5. Essa gates

1. Generate/import only four style-lock poses.
2. Produce `idle`, `walk`, `punch`, 12 independent Frames each.
3. Run static validation and blind visual review.
4. Build Clips/Override and replay them in the current combat slice.
5. Do not begin Grunt until Essa is approved.

## 6. Grunt gates

Repeat with `idle`, `walk`, `attack`, including multiple simultaneous Grunts and
first-spawn preload verification.

## 7. Planned Unity batch checks

```bash
UNITY_BIN="/path/to/Unity"
"$UNITY_BIN" -batchmode -nographics -quit -projectPath unity -runTests -testPlatform EditMode
"$UNITY_BIN" -batchmode -nographics -quit -projectPath unity -runTests -testPlatform PlayMode
"$UNITY_BIN" -batchmode -nographics -quit -projectPath unity -executeMethod FamilyForce.Unity.Editor.BuildFamilyForce.BuildAndroidAtlasPrototype
```

Expected: importer/manifest/clip/fallback tests PASS and production APK builds.

## 8. Device matrix

| Device | 720/1080 | 1P 30m | 2P 30m | Cold/warm | Memory | 1% low | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| Xiaomi Stick baseline | required | required | required | required | required | >=50 | pending |
| Nvidia Shield Pro | required | required | required | required | required | >=50 | pending |
| Android phone 20:9 | native | 15m | optional | required | required | >=50 | pending |
| Fold | folded/unfolded | 15m | optional | required | required | >=50 | pending |

## 9. Exit

The pilot can replace fallback art only when validator PASS, owner APPROVED,
device matrix PASS and package hashes match the approval record. Any mismatch
restores the whole actor package fallback; individual old/new Clips are never mixed.
