# Implementation Plan: Unity Art Foundation

**Branch**: `001-unity-art-foundation` | **Date**: 2026-08-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-unity-art-foundation/spec.md`

## Summary

المرحلة الأولى لا تعيد رسم جميع الشخصيات. هدفها إنشاء خط إنتاج رسومي صارم
وقابل للتكرار، ثم إثباته على `Essa` و`Grunt` فقط. يبدأ العمل بقياس النسخة
الحالية، ثم يقفل عقدًا فنيًا واحدًا، ويفحص كل Frame آليًا وبشريًا، ويحوّل
الحركة تدريجيًا من `SpriteStripAnimator` إلى `AnimationClip` مع إبقاء منطق
الحركة والقتال الحالي هو المرجع. لا يستبدل الأصل القديم إلا بعد نجاح الوضوح،
الثبات، الذاكرة والأداء على 720p و1080p وعلى Xiaomi Stick وShield.

## Technical Context

**Language/Version**: C# مع Unity `6000.3.22f1`، وأدوات QA محلية بـPython 3

**Primary Dependencies**: Unity 6.3 LTS، 2D Sprite، Sprite Atlas، Animator،
Unity Test Framework، Pillow للأدوات الساكنة، Android SDK/ADB

**Storage**: ملفات PNG RGBA منفصلة، JSON manifests، Unity assets ونتائج QA؛
مصادر الإنتاج العالية خارج مجلدات Runtime ولا تدخل APK

**Testing**: Unity EditMode/PlayMode، اختبارات Python للعقد، بناء IL2CPP، ADB،
Unity Profiler/Memory Profiler، واختبار ميداني Xiaomi Stick وNvidia Shield Pro

**Target Platform**: Android API 25+، OpenGL ES 3، ARMv7/ARM64؛ هاتف وFold
وAndroid TV عند 720p و1080p، دون استهداف رسم gameplay أصلي بدقة 4K في هذه المرحلة

**Project Type**: لعبة Android ثنائية الأبعاد داخل مشروع Unity مستقل تحت `unity/`

**Performance Goals**: عرض 60 FPS؛ كل حركة 12 صورة فريدة على الأقل وتعمل بسرعة
مرئية لا تقل عن 12 صورة/ثانية؛ `1% low >= 50 FPS` على الجهاز المرجعي المنخفض؛
لا spike تحميل يتجاوز 50ms عند أول ظهور/هجوم بعد مرحلة الإحماء

**Constraints**: لا Higgsfield ولا فيديو؛ لا صور عملاء خام في المستودع؛ لا 4K
داخل APK؛ `Scale=1` وPPU موحد بعد المعايرة؛ لا توسيع لأكثر من Essa وGrunt؛
الأصول القديمة تبقى fallback؛ لا تغيير في الضرر أو السرعة أو hitboxes في مرحلة الفن

**Scale/Scope**: عقد فني v1، validator، importer/manifest، حزمة إثبات Essa ثم
Grunt، واختبارات 1P/2P؛ لا تشمل بقية أبطال أو أعداء Stage 1

## Constitution Check

ملف `.specify/memory/constitution.md` الحالي قالب غير مصادق عليه، لذلك لا توجد
منه بوابات قابلة للإنفاذ. تطبق بدلًا منه حوكمة المستودع الإلزامية التالية:

- قراءة وتحديث `PROJECT_HISTORY_AR.md` في كل دورة عمل.
- تغييرات صغيرة قابلة للرجوع، مع إبقاء `0.5.0-stage-one-slice` fallback.
- لا يدمج أصل لم يجتز الفحص الآلي والقبول البصري المرتبط بالـhash.
- لا ادعاء باختبار جهاز لم يجر فعليًا، ولا Release بلا APK وSHA-256 ورابط GitHub.
- لا أسرار أو صور عملاء خام في السجل أو Git.

**نتيجة البوابة قبل البحث**: PASS وفق AGENTS.md، مع تسجيل أن Constitution غير مصادق.

## Project Structure

### Documentation (this feature)

```text
specs/001-unity-art-foundation/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── checklists/
│   └── requirements.md
└── contracts/
    ├── art-manifest.schema.json
    ├── approval-record.schema.json
    ├── qa-rules.md
    └── visual-review.md
```

### Source Code (implementation target)

```text
unity/
├── Assets/FamilyForce/
│   ├── Art/
│   │   ├── SourceManifests/
│   │   ├── Runtime/Characters/{Essa,Grunt}/
│   │   ├── Atlases/
│   │   └── ReferenceFallback/
│   ├── Animation/
│   │   ├── BaseControllers/
│   │   ├── Overrides/
│   │   └── Clips/{Essa,Grunt}/
│   ├── Scripts/
│   │   ├── Editor/ArtPipeline/
│   │   └── Runtime/Animation/
│   └── Tests/
│       ├── EditMode/ArtPipeline/
│       └── PlayMode/ArtPilot/
└── tools/
    └── art_qa/
        ├── fixtures/{valid,invalid}/
        └── reports/
```

**Structure Decision**: أدوات الفحص الساكنة تبقى خارج Runtime، بينما importer
وإنشاء Clips/Atlases داخل Editor فقط. ملفات التشغيل المشتقة وحدها تدخل Unity
Player. لا تنقل أصول Android القديمة ولا تعدلها خلال هذه المرحلة.

## Phase 0 — Baseline and Research

### 0.1 تجميد المرجع

- تثبيت commit وAPK وhash لـUnity `0.5.0-stage-one-slice`.
- تسجيل موديل كل جهاز، RAM، Android version، render resolution وrefresh rate.
- قياس cold start وwarm run، `P50/P95/P99 frame time`، `1% low`، PSS، Texture
  Memory، first-spawn/first-attack spike وعدد صفحات Atlas.
- القياس يكون 30 دقيقة **لكل** 1P و2P على Xiaomi، ثم يكرر على Shield.
- التقاط صور ثابتة فقط — لا فيديو مولد — لـEssa وGrunt في idle/walk/punch عند
  720p و1080p وفوق الأسود والأبيض والفوشي وخلفية Stage 1.

### 0.2 معايرة كثافة العرض قبل قفلها

لا يستخدم PPI لأنه خاص بالبوصة الفعلية للشاشة ولا يعرفه Unity بشكل موثوق. تجرّب
ثلاث مشتقات Runtime من Master واحد: 320 و384 و512 logical pixels، أو ما يكافئها
من Sprite Atlas Variant. تعرض كلها بالحجم العالمي نفسه عبر PPU/Camera ثابتين.

قرار القفل يعتمد على:

1. عدم تكبير texel بأكثر من `1.25 screen pixels` في حجم العرض المرجعي.
2. عدم تصغيره دون `0.75 screen pixels` إن أدى ذلك لفقدان العين أو حواف الدرع.
3. عدم ظهور shimmer أثناء الحركة الأفقية.
4. نجاح ميزانية الذاكرة والـ1% low على Xiaomi.
5. اختيار أصغر مشتق يطابق بصريًا المرشح الأعلى في لقطات 720p/1080p.

النقطة الابتدائية المرشحة للاختبار: شبكة عالية `512 / PPU 128 / Scale 1`،
Variant `0.75` لـ1080p و`0.5` لـ720p. هذا **مرشح قياس** وليس قانونًا نهائيًا
حتى تنجح المقارنة الميدانية.

### 0.3 مخرج Phase 0

- `research.md` مكتمل.
- تقرير baseline قابل لإعادة التشغيل.
- قرار Runtime Resolution واحد موثق بالأرقام، أو Variants بمصفوفة أجهزة واضحة.
- يمنع بدء إنتاج جميع Frames قبل هذا القرار.

## Phase 1 — Art Contract and Design

### 1.1 Style Bible v1

- Model sheet مرجعي لكل من Essa وGrunt: الوجه، النسب، الزي، الألوان، الضوء،
  سماكات الخطوط، زوايا العرض ومناطق لا يجوز تغييرها.
- لوحة ألوان مرقمة، إضاءة من أعلى اليسار، وحد أدنى للتفاصيل المقروءة.
- حظر صريح للرموز الدينية/المذهبية/الوطنية/الحضارية/الرونية والشعارات غير
  المعتمدة. حرف `S` لا يظهر إلا على Sulaiman لاحقًا.
- تعريف الحجم النسبي داخل الشبكة المنطقية بدل تكبير Transform لكل شخصية.

### 1.2 Source-to-Runtime Contract

- كل Frame مصدر مستقل `RGBA PNG` بخلفية شفافة أصلًا؛ لا sheets ولا chroma key.
- Master طويل الضلع 2048px على الأقل، محفوظ خارج Runtime؛ مشتق Runtime فقط يدخل APK.
- التحويل deterministic ومثبت الإصدار: توحيد palette، downsample، alpha cleanup،
  reconstruction على canvas منطقي، trim آمن، pivot metadata وhash.
- Straight alpha ثابت في المصدر والمشتق؛ الشخصية alpha ثنائي، والـsemi-alpha
  للـFX المنفصل فقط. لون RGB تحت alpha=0 تنظفه recipe ولا يستخدم لإخفاء matte.
- السلاح/الوهج/FX المنفصل لا يوسع جسم الشخصية أو يخرق حافة الأمان؛ ينفصل إلى
  Sprite/Atlas مستقل عند الحاجة.

### 1.3 Animation Contract

- 12 Frame فريدة على الأقل لكل حركة؛ التكرار وmirror لا يحتسبان.
- Render 60 FPS منفصل تمامًا عن animation sampling.
- walk يجب أن يثبت تعاقب Right contact ثم passing/up ثم Left contact؛ لا تبقى
  الرجل نفسها في المقدمة ولا تتحرك الأطراف عشوائيًا.
- خط القدم والحوض وطول الجسم مقيدة بالقيم في `contracts/qa-rules.md`.
- Animator للعرض فقط؛ PlayerMotor/Combat data يبقيان مصدر الحركة والضرر.
- Base Animator Controller وOverride لكل شخصية؛ transition exit time normalized.
- hit-stop يجمّد Sprite animation والقتال معًا، بينما UI/pause فقط unscaled.
- Hit windows تبقى في ActionDefinition؛ SFX/attach/VFX يولد توقيتها من timeline نفسه.

### 1.4 Action Matrix المقفلة قبل الرسم الكامل

Pilot إثبات الأسلوب والحركة يبدأ بثلاثة actions فقط لكل شخصية، لكنه لا يدّعي
اكتمالها. مجموعة Essa النهائية المطلوبة للمرحلة: idle، walk، punch combo، kick،
heavy punch، heavy kick، jump takeoff/air/land، aerial attack، special، link،
hurt، knockdown، get-up، grab start/hold/strike، team combo، weapon pickup/hold/
swing/throw، stage entry، victory. مجموعة Grunt: idle، walk، attack، heavy attack،
hurt، knockdown، get-up، grab victim، weapon reaction، stage entry وdefeat.

كل action في المصفوفة يصرح إن كان يحتاج 12 Frame كاملة أو مراحل فرعية كل منها
12 Frame؛ لا يسمح باستعارة صورة action آخر في النسخة النهائية.

### 1.5 Automated Gate

يبنى validator يفشل مغلقًا ويصدر JSON + HTML/PNG contact sheets. تشمل القواعد:

- الأبعاد/التسمية/تسلسل الأرقام/12 unique.
- exact hash وperceptual similarity؛ hold Frame المصرح به يوسم ولا يحتسب Unique.
- alpha الحقيقي، الأطر الفارغة، matte والحواف البيضاء.
- safe margin والقص في كل الجهات.
- ثبات الجسم، القدم، الحوض والهوية/الألوان.
- دورة مشي صحيحة: القيم الآلية ترشح الخلل والمراجع البشري يحكم التشريح.
- رموز محظورة بحاجة مراجعة بشرية عند الاشتباه.
- صفحة Atlas والضغط والذاكرة المتوقعة.
- عدم قبول تقرير أو موافقة إذا تغيّر أي hash أو إعداد importer.

### 1.6 Human Gate

الآلة لا تعتمد الشكل النهائي. ينشأ Review Pack ثابت دون فيديو مولد يحتوي:

- مقارنة blind A/B بين القديم والجديد بالحجم الفعلي.
- contact sheet للحركة كاملة والاتجاهين.
- لقطات black/white/magenta/Stage 1.
- 720p و1080p، 1P و2P، وتراكب silhouette لقياس الاهتزاز.
- Rubric من 5 لكل: الهوية، وضوح الوجه، ثبات الحجم، طبيعية الحركة، الحواف،
  تطابق الأسلوب. يلزم 5/5 للحواف والقص والرموز، و>=4/5 لكل بقية محور.
- قرار المستخدم: `APPROVED` أو `REJECTED` مرتبط بالـhash.

## Phase 2 — Pilot Execution Order (خطة التنفيذ اللاحقة)

### Gate A — Animator regression with old art

قبل إدخال أي رسم جديد، يشغل Animator/Clip pipeline بالأصول الحالية. يجب أن يمر
الريموت وDualSense واللمس و1P/2P confirm والقتال والمسك وTeam Combo والتقاط bat
وضربه ورميه وإعادة التقاطه والـscore/results. لا ينتقل للرسم إذا تغير gameplay.

### Gate B — Essa style lock

ينتج فقط 4 وضعيات مرجعية لـEssa: idle، contact walk، punch impact، jump apex.
لا تنتج بقية الحركة قبل قبول الوجه والدرع والنسب والخط واللون.

### Gate C — Essa motion proof

ينتج `idle + walk + punch`، كل منها 12 Frame مستقلة. بعد نجاح العقد تعرض داخل
Unity بالحجم الحقيقي. أي تغير وجه/حجم/قدم يعيد هذه الدفعة فقط.

### Gate D — Grunt proof

يكرر المسار على `idle + walk + attack` لـGrunt. الغرض إثبات أن العقد يعمل على
عدو وليس على بطل واحد فقط، واختبار أول تحميل وعدة نسخ متزامنة منه.

### Gate E — Runtime integration

- Clips آلية من manifest وليس أعدادًا hard-coded.
- Animator Override منفصل لـEssa وGrunt.
- لا root motion؛ لا تغيير hitboxes أو damage أو input.
- Preload في transition قبل الجولة، warm-up للـmaterials/first clip، unload عند
  مغادرة المرحلة؛ فشل التحميل يعيد actor package كاملًا إلى fallback، ولا يمزج
  Clips قديمة وجديدة بصمت.
- مشهدا اختبار: comparison scene مع Essa/Grunt الجديدين، وStage 1 regression
  مختلط واقعيًا مع Adam legacy لقياس worst-case residency أثناء الهجرة.

### Gate F — Full Pilot set

بعد اعتماد Gates A–E فقط، تستكمل حركات Essa وGrunt في Action Matrix. كل حركة
تسلم دفعة مستقلة وتخضع لنفس البوابات، ولا تنتج دفعة كل الشخصيات.

## Performance and Device Acceptance

### Atlas settings under test

- Max page: 2048.
- Rotation: off.
- Tight packing: off في المرجع؛ لا يفعل إلا بعد اختبار pivot/geometry كامل.
- Offline trim مع 24px safe border على الشبكة 512 المكافئة.
- Padding: 8px على الأقل، mipmaps off، Read/Write off، Wrap Clamp.
- Point هو المرجع الحاد؛ أي Variant/filter بديل يحتاج A/B ولا يعتمد إذا أحدث blur.
- Atlas مستقل لكل شخصية، وFX/weapon Atlas منفصل.

### Compression decision

- `RGBA32` مرجع بصري فقط.
- `ETC2 RGBA8` خط توافق أول لأن المشروع GLES3.
- `ASTC 4x4` مرشح جودة/ذاكرة لا يعتمد إلا بعد اختبار كل الأجهزة المستهدفة.
- يمنع ASTC 6x6/8x8 للشخصيات الدقيقة في المرحلة الأولى.
- يفشل الضغط إذا غيّر silhouette alpha أو أحدث halo، أو كان `SSIM < 0.98` أو
  `PSNR < 38 dB` داخل منطقة الشخصية؛ النجاح الآلي لا يلغي الرفض البصري.

### Runtime gates

- لا synchronous load عند أول ظهور؛ preload قبل بداية الجولة.
- لا GC allocation مستمر من animator في الحلقة الحرجة.
- جلسة 30 دقيقة لكل من 1P و2P على كل جهاز baseline بلا crash/ANR/OOM.
- Render target 60، و1% low لا يقل عن 50 على Xiaomi المرجعي.
- low-RAM TV: الهدف المحافظ من Android هو Graphics `30–40MB` ومجموع الذاكرة
  `<=280MB` لجهاز 1GB؛ إذا لم يبلغ baseline الحالي هذا الهدف، يسجل الانحراف
  ويمنع أي زيادة Pilot تتجاوز 20% بلا قرار صريح وخطة خفض.
- لا يُقبل Texture Variant بناء على حجم APK؛ الحكم على resident graphics memory
  وframe time والوضوح الفعلي.

## Approval Fingerprint

بصمة الاعتماد تشمل PNG masters/derivatives و`.meta` وmanifest وconverter recipe
وAnimator Controllers وClips وAtlas settings/compression وPrefab scale/material
وcamera/PPU settings وvalidator report. تغيير أي عنصر يبطل الاعتماد.

## Deliverables and Exit Criteria

تكتمل المرحلة الأولى فقط عند توفر جميع الآتي:

1. عقد `qa-rules.md` برقم إصدار واحد بعد قفل Calibration.
2. Manifest schema وvalidator مع fixtures سليمة ومعيبة، ونسبة كشف 100% للحالات المتعمدة.
3. Style Bible وModel Sheets معتمدة لـEssa وGrunt.
4. Action Matrix كاملة، وEssa/Grunt Pilot مع 12 Frame فريدة لكل حركة Pilot.
5. AnimationClips وOverrides تعمل دون تغيير منطق القتال.
6. قبول بصري صريح من المستخدم مرتبط بالhash.
7. اختبارات 720p/1080p و1P/2P و30 دقيقة وXiaomi/Shield موثقة.
8. تقرير memory/atlas/compression، وfallback كامل يعمل.
9. تحديث `PROJECT_HISTORY_AR.md` ونتائج الاختبارات وقرار الانتقال للمرحلة التالية.

لا تُعد المرحلة مكتملة عند نجاح الصور الثابتة وحدها، ولا يبدأ Adam أو بقية أعداء
Stage 1 قبل تحقق هذه البنود. قبل التنفيذ الفعلي يجب توليد `tasks.md` عبر
`speckit-tasks`؛ عدم وجوده الآن مقصود لأن هذا التسليم خطة وليس تنفيذًا.

## Constitution Re-check After Design

**PASS وفق حوكمة المستودع البديلة**: التصميم تدريجي، قابل للرجوع، يفشل مغلقًا،
يحمي بيانات العملاء، يفصل المصادر عن Runtime، ويشترط الاختبار الحقيقي. لا توجد
مخالفة مسجلة لأن Constitution الرسمية ما زالت قالبًا غير مصادق.

## Complexity Tracking

لا توجد مخالفة Constitution معروفة. تعدد Atlas Variants مبرر فقط إذا أثبتت
معايرة 720p/1080p أن نسخة واحدة لا تحقق الوضوح والذاكرة معًا؛ وإلا يعتمد مشتق
Runtime واحد لتقليل التعقيد.
