# السجل المشترك للمشروع — Family Force: Neon Streets

> هذا الملف هو المصدر المركزي لتبادل السياق بين **Codex** و**Claude Code**.
> يجب على كل وكيل قراءته قبل تعديل المشروع، وتحديثه بعد كل طلب أو تعديل أو
> اختبار أو Release. سجل الأحداث أدناه تراكمي؛ لا تُحذف الإدخالات القديمة.

آخر تحديث: 21 أغسطس 2026 — Codex

## حالة العمل الحالية

- المنتج الأساسي: لعبة Android أصلية بنمط beat-'em-up ريترو حديث، وليست Emulator.
- المنصة: الهاتف، Fold، Android TV، والريموت/يد التحكم.
- النسخة المنشورة: `v0.31.0-alpha`، `versionCode 36`.
- الفرع المشترك: `main`.
- آخر commit وظيفي: `285c6faf2c2cba4873687236e193df15d7e0cf8f`.
- الحزمة الحالية: `com.familyforce.neonstreets.event.familycurrent`.
- Release: https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.31.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.31.0-alpha/family-force-family-current.apk
- SHA-256: `18b767fcae9b516467d2dad47541fa2ac4fc2ad1cf6434340e00142e28471b85`.
- حالة QA: بناء Release وR8 وLint والتوقيع والأرشيف و10 أطالس والتحكم وعقود
  ذاكرة/سلاسة TV ناجحة؛ لم يكن جهاز أو Emulator متصلًا لهذه النسخة.
- نتيجة Xiaomi Stick الحقيقية لـv0.25: جلسة كاملة بلا تقطيع للاعبين، مع نجاح
  استدعاء الشخصيات الإضافية ونظافة الرسومات والحركة.
- اختبار المناطق: مسار تطويري آلي مرّ بالمناطق 1–9 حتى شاشة النتائج بنجاح.
- التشخيص: يوجد Flight Recorder محلي خفيف يحفظ آخر منطقة، P1/P2، العدو،
  السلاح، الحركة والذاكرة، ويحفظ تقرير الجلسة السابقة إذا انقطعت.
- نتيجة اختبار Shield Pro: المناطق 1–9، الموت/الإحياء، الإغلاق/الفتح، فصل اليد،
  الريموت والتقاط الأسلحة تعمل دون خروج غير طبيعي.
- إصلاح قيد تحقق المستخدم: DualSense على Shield أصبح يُكتشف بمعرّف Sony ويقبل
  أحداث الأزرار التي يعلنها OEM كمصدر Keyboard، مع إبقاء fallback الخاص بـXiaomi.
- الاختبارات المتبقية: Checkpoint/Continue بعد خسارة أو إعادة تشغيل، وXiaomi Stick.
- العمل التالي الموصى به: اختبار توازن هويات المراحل في `v0.31`، ثم إضافة عدو
  بعيد المدى واحد بحزمة مرحلة محدودة من دون تجاوز خمسة أطالس على Android TV.

## بروتوكول التحديث الإلزامي

ينطبق هذا البروتوكول على Codex وClaude Code وأي وكيل آخر يعمل على المشروع:

1. اقرأ هذا الملف و`git status` و`git log -5` قبل بدء أي عمل.
2. لا تفترض أن آخر محادثة كانت معك؛ اعتبر قسم **حالة العمل الحالية** هو نقطة البدء.
3. عند استلام طلب جديد، أضف إدخالًا جديدًا في **سجل الطلبات والتعديلات** يتضمن
   نص الطلب أو ملخصًا قريبًا منه، واسم المنفذ، وحالة `قيد التنفيذ`.
4. بعد العمل، حدّث الإدخال نفسه إلى `مكتمل` أو `متوقف`، وسجّل الملفات والاختبارات
   والنتيجة والمشاكل المتبقية. لا تدّع نجاح اختبار لم يتم تشغيله.
5. حدّث **حالة العمل الحالية** عندما تتغير النسخة أو الـcommit أو الأولوية التالية.
6. لا تمسح تاريخ وكيل آخر ولا تعيد كتابة قراراته. التصحيح يضاف كإدخال جديد يشير
   بوضوح إلى الإدخال المصحح.
7. لا تُسجّل صور العملاء أو الأسرار أو كلمات مرور التوقيع أو محتوى حساسًا.
8. أي Release جديد يجب أن يُرفع مباشرة إلى GitHub Releases مع APK ورابط مباشر
   وSHA-256 وcommit، ثم تُسجّل هذه البيانات هنا.
9. التعديلات التوثيقية فقط لا تتطلب Release APK جديدًا؛ تُضمّن في commit عادي.
10. قبل تسليم الدور لوكيل آخر، املأ **تسليم العمل الحالي** في نهاية الملف.

### قالب الإدخال الجديد

```md
### YYYY-MM-DD-NN — عنوان مختصر

- المنفذ: Codex | Claude Code | اسم آخر
- طلب المستخدم: "نص مختصر قريب من الطلب الأصلي"
- الحالة: قيد التنفيذ | مكتمل | متوقف
- نقطة البداية: commit/نسخة
- ما تم:
  - ...
- الملفات المعدلة:
  - `path`
- الاختبارات:
  - `command` — PASS/FAIL/SKIPPED مع السبب
- Release: لا يوجد | tag + URL + SHA-256
- ملاحظات/مخاطر: ...
- التالي: ...
```

## سجل المراحل والنسخ المستعاد

هذا القسم أعيد بناؤه من ملفات المشروع، تقارير QA، سجل Git، GitHub Releases،
وسياق العمل المتاح. الطلبات القديمة ملخصة وليست اقتباسًا حرفيًا كاملًا.

### المرحلة A — نموذج SNES الأولي

- طلب المستخدم: إنشاء لعبة SNES شبيهة بألعاب قتال الشوارع العائلية، تعمل من
  خرطوشة SD، وتستخدم صور العائلة للشخصيات.
- النتيجة: نموذج SNES Homebrew مبني بـPVSnesLib، مع ROM قابل للاختبار، شخصيات
  مؤقتة، موسيقى/SFX أصلية، وقوائم وقتال أولي.
- سبب الانتقال: حدود دقة SNES، صعوبة إظهار الوجوه، حجم الشخصيات والحركة المحدودة.
- المرجع: `README.md` و`PLAY_ON_SNES.md`.

### المرحلة B — الانتقال إلى Android APK

- طلب المستخدم: تحويل الاتجاه من SNES إلى APK ريترو أعلى دقة، بروح Streets of
  Rage، مع قوائم وعناصر وموسيقى وشخصيات تشبه أفراد العائلة.
- النتيجة: مشروع Android Java/Canvas بمنطق 60Hz ولوحة 640×360 قابلة للتوسع، مع
  دعم اللمس وAndroid TV وFold وGamepad.
- الشخصيات: Essa، Adam، Shaikha، Sulaiman مع نسب الأطوال 177/108/108/124 سم.
- لم تُستخدم الصور الخام داخل APK.

### المرحلة C — هوية الشخصيات والحركة

- طلبات المستخدم: جعل Essa أقوى، Adam بطابع قوة خضراء عضوية، Shaikha أميرة
  جليدية وردية، وSulaiman بطلًا أزرق/أحمر بحرف S؛ وإظهار حركة حقيقية لكل فعل.
- النتيجة: Atlases حقيقية لأربع شخصيات وأربعة أنواع أعداء.
- عقد البطل: 11 حركة × 8 إطارات، خلايا 192×192، Atlas بحجم 1536×2112.
- الحركات: idle، walk، punch، kick، heavy punch، heavy kick، jump، special،
  Link، hurt، knockdown.
- عقد العدو: 6 حالات × 6 إطارات، Atlas بحجم 960×1152.
- قرار دائم: إنتاج الشخصيات التجاري يعتمد صور/Model Sheets ثابتة، وليس الفيديو.
- المرجع: `android/design/generation-audit.md` وأدوات character asset factory.

### المرحلة D — لاعبان والتحكم والتلفاز

- طلبات المستخدم: لعب P1/P2 اختياري، اختيار companion لكل لاعب، تحريك P2
  بحركة كاملة، والتنقل في كل القوائم بريموت Android TV وDualSense.
- توسع الدعم لاحقًا إلى Xbox وNintendo Switch Pro وJoy-Con وJoy-Con 2.
- النتيجة: هوية مستقلة ليد P1/P2، قوائم قابلة للتصفح، دعم D-pad/analog/dead
  zones، وإيقاف آمن عند فصل اليد.
- المرجع: `android/CONTROLLER_COMPATIBILITY_REPORT_AR.md`.

### المرحلة E — إصلاحات الأعطال والذاكرة

- المشكلة المتكررة: خروج اللعبة من اختيار اللاعبين أو عند أول مواجهة/التقاط
  المضرب، خصوصًا على Android TV منخفض الذاكرة.
- الإصلاحات التراكمية: تحميل lazy للأطالس، تحرير صور غير مستخدمة، نسخ TV مصغرة
  بنسبة 75%، حماية دورة حياة الصوت، منع تعارض تحرير Bitmap، R8 وتصغير الموارد،
  وتحسين مسار الالتقاط والأسلحة.
- الأجهزة المستهدفة: Xiaomi Stick، Nvidia Shield، Sony، Skyworth، Android TV.
- النتيجة: اختبارات الهاتف، ultrawide، Fold و1920×1080 تمر دون FATAL/ANR/OOM.

### `v0.3.0-alpha` — نظام الحركة والقتال الموسع

- أضيف Animator للأبطال والأعداء، الحركات المباشرة، Link assist، أسلحة/Props
  بصور فعلية، وفيزياء الرمي والارتداد.
- استبدلت حركة الصورة الثابتة بأطالس فعلية للشخصيات والأعداء.
- تم اختبار الحركة وFold والأداء، مع بقاء النسخة Alpha.

### `v0.4.0-alpha` — المرحلتان 1 و2 والنظام التجاري

- المرحلة 1: ثبات Android TV، تحميل وإخلاء الأطالس حسب الحاجة، وحفظ الإعدادات.
- المرحلة 2: Attack/Hurt boxes، input buffering، combos، hit-stop وknockdown.
- أضيف customer pack، مصنع APK، توقيع RSA-4096 خارج المشروع، فحص سلامة صامت،
  applicationId مستقل، وR8/resource shrinking.
- المرجع: `android/PHASE_1_2_REPORT_AR.md` و
  `android/COMMERCIAL_APK_IMPLEMENTATION_REPORT_AR.md`.

### المراحل التجارية 6–12

- طلب المستخدم: تحويل اللعبة إلى منتج مناسبات يُسلّم APK مباشرة، مع تبديل
  شخصيات العميل دون تعقيد عليه وحماية معقولة من إعادة التغليف.
- أضيفت قوالب الطلب والموافقة والخصوصية، مصنع شخصيات بالصور فقط، branding،
  مصنع APK، لوحة طلبات، وإرشادات حماية/استعادة المفتاح.
- أضيف دليل HTML متعدد التبويبات للإنتاج والطلب والبيع.
- المرجع: `android/COMMERCIAL_PIPELINE_FINAL_REPORT_AR.md` و`commercial-guide/`.

### `v0.18.0-alpha` — إصدار الثبات الشامل

- commit: `31a2e3c30da0352c3e45030080c13fca227c982e`.
- تحسين نسخ أطالس Android TV وتقليل ضغط الذاكرة.
- تقوية دورة حياة الصوت والإيقاف/الاستئناف.
- إضافة اختبارات الذاكرة والالتقاط والـcheckpoint والقتال والتحكم.
- Release: https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.18.0-alpha

### `v0.19.0-alpha` — إصلاح بوابة CLEAR

- طلب المستخدم: P1 يعلق عند CLEAR بينما P2 يتجاوزها.
- السبب: تطبيق حد بوابة المواجهة على P1 دون P2، ما يسمح بسحب عدو خلف الحاجز.
- الإصلاح: توحيد حد P1/P2 والأعداء، وتغيير الرسالة إلى `DEFEAT ENEMIES`.
- commit: `3cc36183ecbca8e69162947f928d7cfbba09804a`.
- Release: https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.19.0-alpha

### `v0.20.0-alpha` — اختبار المناطق والتشخيص

- طلب المستخدم: تنفيذ (1) فحص المناطق 1–9 و(2) نظام تشخيص محلي للأعطال.
- أضيف اختبار Debug-only يمر بكل المناطق حتى شاشة النتائج ولا يعمل في Release.
- أضيف `RuntimeDiagnostics` ليسجل حالة اللعبة والذاكرة ويحفظ تقرير الانقطاع السابق.
- نجح Build/Lint، واختبار المناطق 1–9، وفحوص الهاتف/Fold/Android TV/لاعبين.
- commit: `e845b66202d563ef9aa1bb2075cc04ac5b001125`.
- Release: https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.20.0-alpha
- APK SHA-256: `3151c4916946588e6278a812870160bf1259fc02ed8dbd9f90e56ec0cf06879f`.

## سجل الطلبات والتعديلات المشترك

### 2026-08-22-31 — الخطوة التالية بعد هويات المراحل

- المنفذ: Codex
- طلب المستخدم: «ما التالي؟» بعد إصدار `v0.31.0-alpha`.
- الحالة: مكتمل — تخطيط فقط.
- نقطة البداية: `v0.31.0-alpha` / commit `285c6fa`.
- القرار:
  - اختبار توازن سريع للمراحل الأربع في لاعب/لاعبين: HP، عدد المهاجمين، recovery،
    Mini-boss والمكافآت؛ أي تعديل أرقام فقط يصدر كـ`v0.31.1`.
  - التطوير التالي المقترح `v0.32.0-alpha`: عدو Ranged Drone يضيف تهديدًا بعيدًا
    وتلغرافًا واضحًا ومقذوفًا يمكن تفاديه أو ضربه، بدل عدو melee سابع مشابه.
  - إنتاجه بصور ثابتة فقط: Model Sheet + ثلاث Action Sheets، أطلس 36 إطارًا،
    projectile/effect sprite؛ لا فيديو.
  - تحميله في Stage 3 و4 فقط مع إخراج نوع غير مستخدم من الحزمة لإبقاء حد TV
    خمسة أطالس وميزانية القتال الحالية تقريبًا.
  - بعده: مخاطر بيئية خفيفة قابلة للكسر، ثم تطوير Phase ثانية للـJunk King.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات: Runtime — SKIPPED؛ هذا طلب تخطيط فقط.
- Release: لا يوجد؛ توثيق فقط.
- ملاحظات/مخاطر: لا يُنصح بإنتاج صور العدو قبل تثبيت عقد المقذوف والـsafe box،
  حتى لا تتكرر مشكلة قص الأطراف أو يُهدر إنتاج الصور.
- التالي: عند طلب التنفيذ، بناء projectile/state contract أولًا، ثم صور Ranged
  Drone الثابتة، ثم دمجه في Stage 3/4 وإصدار `v0.32.0-alpha`.

### 2026-08-22-30 — تنفيذ هوية المراحل القتالية

- المنفذ: Codex
- طلب المستخدم: تنفيذ الخطوة التالية المقترحة.
- الحالة: مكتمل.
- نقطة البداية: `v0.30.2-alpha` / commit `bc337a0`.
- ما تم:
  - إضافة `StageCombatRule` ثابتة للمراحل الأربع: HP/damage/attack pressure،
    recovery، Link، bonus، Elite zone/type، objective وhint.
  - Stage 1 STREET RUSH، Stage 2 BREAK THE LINE، Stage 3 HARBOR HOLD،
    Stage 4 BOSS GAUNTLET بقواعد فعلية مختلفة.
  - إضافة Mini-boss/Stage Boss وتسميات واضحة، ومكافآت bat/pipe/mallet/sign.
  - تطبيق recovery وLink على P1 وP2، وإضافة bonus للمرحلة الأخيرة أيضًا.
  - إبقاء تحميل الأطالس حسب Stage بحد أقصى خمسة وميزانية TV `30.09 MiB`.
  - رفع `versionCode 36` / `0.31.0-alpha` دون صور أو فيديو جديد.
- الملفات المعدلة:
  - `android/app/src/main/java/com/familyforce/neonstreets/StageCombatRule.java`
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/tools/test_stage_combat_identity_contract.py`
  - `android/tools/test_enemy_attack_tokens_contract.py`
  - `android/tools/test_customer_release.sh`
  - `android/app/build.gradle`.
- الاختبارات:
  - Stage combat identity contract — PASS: 4 rules/elites/rewards/bounded rosters.
  - Build Debug + Lint — PASS.
  - `test_customer_release.sh` — PASS؛ Release/R8/Lint/signature/archive/controller/
    encounters/checkpoints/weapons/10 atlases/TV memory+smoothing نجحت.
  - Runtime جهاز/Emulator — SKIPPED؛ لم يكن جهاز متصلًا.
- Release: `v0.31.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.31.0-alpha
  - APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.31.0-alpha/family-force-family-current.apk
  - SHA-256: `18b767fcae9b516467d2dad47541fa2ac4fc2ad1cf6434340e00142e28471b85`.
  - commit: `285c6faf2c2cba4873687236e193df15d7e0cf8f`.
- ملاحظات/مخاطر: يلزم ضبط صعوبة القواعد بعد جلسة فعلية لاعب/لاعبين، خصوصًا
  ضغط Stage 3 وStage 4؛ لم يُدع اختبار عتاد هنا.
- التالي: GAME UPDATE ثم لعب المراحل الأربع وتسجيل ملاحظات الصعوبة والمكافآت.

### 2026-08-22-29 — الخطوة التالية بعد إصلاح العدوين

- المنفذ: Codex
- طلب المستخدم: «جيد، ما التالي؟»
- الحالة: مكتمل — تخطيط فقط.
- نقطة البداية: `v0.30.2-alpha` / commit `bc337a0`.
- القرار:
  - بوابة قصيرة أولًا على الجهاز: Striker وShield Guard يمينًا/يسارًا، كل حالات
    الحركة، وكسر GUARD؛ ثم اعتبار `v0.30.2` خط أساس بصري ثابت.
  - التطوير الأعلى قيمة بعد ذلك هو إعطاء المراحل الأربع هوية لعب حقيقية باستخدام
    الأنواع الستة الحالية: تشكيلات موجات مختلفة، قواعد دخول، Mini-boss، ومكافآت.
  - بعدها إضافة عدو بعيد واحد `Ranged Drone` بصور ثابتة و36 إطارًا، مع projectile
    واضح وتلغراف هجوم، وتحميله في حزمة مرحلة واحدة أولًا لحماية ذاكرة TV.
  - يلي ذلك تحسين الزعماء: مرحلتان للهجوم لكل Boss ونتيجة/مكافأة مميزة لكل Stage.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات: Runtime — SKIPPED؛ هذا طلب تخطيط فقط.
- Release: لا يوجد؛ توثيق فقط.
- ملاحظات/مخاطر: إضافة أعداء آخرين قبل تنويع الموجات ستزيد حجم الأصول دون أن
  تغيّر إحساس المراحل بما يكفي؛ لذلك نستخدم الأنواع الحالية أولًا.
- التالي: تنفيذ «هوية المراحل القتالية» كحزمة `v0.31.0-alpha` من دون صور جديدة.

### 2026-08-22-28 — استعادة مقدمة قفاز Striker ودرع Shield Guard

- المنفذ: Codex
- طلب المستخدم: لا يزال القفاز والدرع يُقصان من المقدمة أثناء الحركة.
- الحالة: مكتمل.
- نقطة البداية: `v0.30.1-alpha` / commit `f12a8d3`.
- ما تم:
  - ثبت أن الرسومات الكاملة موجودة، لكن تقسيم Action Sheet إلى أعمدة متساوية
    كان يقطع مقدمة القفاز والدرع قبل إضافة الهامش الشفاف.
  - استبدل التقسيم الحسابي باكتشاف كل silhouette متصل واستخراج حدوده الحقيقية.
  - أعيد بناء masters وأطالس الهاتف وTV للعدوين مع إبقاء هامش 12px/8px.
  - أضيفت بوابة اختبار تلزم component-aware extraction؛ لم تُنتج صور أو فيديوهات.
- الملفات المعدلة:
  - `android/tools/build_striker_enemy.py`
  - `android/tools/build_shield_guard_enemy.py`
  - `android/tools/test_striker_enemy_contract.py`
  - `android/tools/test_shield_guard_enemy_contract.py`
  - masters/atlases الهاتف وTV للعدوين و`asset_manifest.json`.
  - `android/app/build.gradle` (`versionCode 35` / `0.30.2-alpha`).
- الاختبارات:
  - الفحص البصري للأطلسين — PASS؛ القفاز والدرع كاملان داخل Safe Box.
  - `validate_assets.py` و10/10 atlas QA — PASS.
  - `test_customer_release.sh customers/family-current` — PASS؛ Release/R8/Lint/
    signature/archive/controller/TV memory/smoothness نجحت.
  - Latest API — PASS؛ الاسمان العام واسم العميل موجودان بنفس SHA والحجم.
  - Runtime جهاز/Emulator — SKIPPED؛ لم يكن جهاز متصلًا.
- Release: `v0.30.2-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.30.2-alpha
  - APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.30.2-alpha/family-force-family-current.apk
  - SHA-256: `1fc0a4fce3c210f399952563e60802095d518b2d84c684292c39377dc8dbc82d`.
  - commit: `bc337a0ce0d1887dd4b5cf80d8c682da89a13062`.
- ملاحظات/مخاطر: يلزم تأكيد بصري على الجهاز؛ هذه النسخة تعالج القص قبل التطبيع،
  لا مجرد إضافة padding بعده.
- التالي: استخدام GAME UPDATE، ثم اختبار المشي والهجوم للعدوين يمينًا ويسارًا.

### 2026-08-22-27 — إصلاح أصل التحديث داخل GitHub Release

- المنفذ: Codex
- طلب المستخدم: تنفيذ إصلاح `CHECK FAILED`.
- الحالة: مكتمل.
- نقطة البداية: `v0.30.1-alpha` / commit `f12a8d3`.
- ما تم:
  - رفع الـAPK الموقّع نفسه إلى `v0.30.1-alpha` باسم
    `family-force-family-current.apk` الذي يطلبه `UpdateManager`.
  - أبقي الأصل العام أيضًا؛ الأصلان متطابقان byte-for-byte ولا توجد إعادة بناء.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات:
  - GitHub Latest API asset lookup — PASS؛ الاسم المطلوب موجود.
  - الحجم — PASS: `44,245,233` bytes لكلا الأصلين.
  - SHA-256 — PASS: `a86935bbff5b9510862d6f6cf087dd3b6378ebbd96824d9514f4c12f9f8b496f`.
- Release: أصل مصحح داخل `v0.30.1-alpha`:
  https://github.com/linkq8/family-force-neon-streets/releases/download/v0.30.1-alpha/family-force-family-current.apk
- ملاحظات/مخاطر: النسخة `v0.30.1` ستعرض `UP TO DATE`؛ النسخ الأقدم ستجد
  الأصل وتبدأ التنزيل. ما زال تثبيت APK يحتاج موافقة Android النظامية.
- التالي: تجربة GAME UPDATE على الجهاز؛ لا حاجة لتنزيل APK يدويًا لهذا الإصلاح.

### 2026-08-22-26 — تشخيص CHECK FAILED في تحديث اللعبة

- المنفذ: Codex
- طلب المستخدم: لماذا أصبح GAME UPDATE يعرض `CHECK FAILED`؟
- الحالة: مكتمل — تشخيص فقط.
- نقطة البداية: `v0.30.1-alpha` / commit `f12a8d3`.
- ما تم:
  - فحص `UpdateManager` وManifest وBuildConfig وGitHub Latest Release API.
  - ثبت أن الاتصال والإصدار والـSHA موجودة، لكن التطبيق يطلب أصلًا باسم
    `family-force-family-current.apk` بينما Release الحالي يحتوي
    `family-force-neon-streets.apk`؛ فيفشل `findAsset` برسالة
    `No matching customer APK` وتعرض الواجهة `CHECK FAILED`.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات:
  - `gh api .../releases/latest` — PASS؛ أحدث tag هو `v0.30.1-alpha` والأصل
    الوحيد اسمه `family-force-neon-streets.apk`.
  - مطابقة `UpdateManager.wantedName` مع `BuildConfig.CUSTOMER_ID` — FAIL متوقع؛
    الاسم المطلوب `family-force-family-current.apk` غير موجود في Release.
- Release: لا يوجد؛ لم يُغيّر GitHub Release لأن الطلب كان تشخيصًا.
- ملاحظات/مخاطر: إصلاح Release بإضافة APK نفسه بالاسم المتوقع يعيد التحديث
  للنسخ المثبتة فورًا، ولا يحتاج إصدار تطبيق جديد.
- التالي: عند طلب الإصلاح، رفع الأصل الموقّع نفسه إلى `v0.30.1-alpha` باسم
  `family-force-family-current.apk` والتحقق من digest وLatest API.

### 2026-08-22-25 — إصلاح قص آخر عدوين

- المنفذ: Codex
- طلب المستخدم: إصلاح Striker وShield Guard لأن الحركة تُقص الرسم من إحدى الجهات.
- الحالة: مكتمل.
- نقطة البداية: `v0.30.0-alpha` / commit `71594e3`.
- ما تم:
  - ثبت أن المصدر كامل، وأن السبب هو تطبيع قديم يترك 4–6px فقط حول الحركة.
  - أعيد بناء 36 إطار Striker و36 إطار Shield Guard داخل الخلايا الأصلية
    `160×192` مع هامش لا يقل عن 12px من الجهات الأربع.
  - أعيدت نسخ TV بنسبة 75% مع هامش فعلي لا يقل عن 8px بكل خلية.
  - أزيل اندفاع لكمة Striker غير الآمن واستبدل باندفاع 4px داخل صندوق أضيق.
  - أعيدت fallback masters والـmanifest، ولم تُنشأ صور مصدر أو فيديوهات جديدة.
- الملفات المعدلة:
  - `android/tools/build_striker_enemy.py`
  - `android/tools/build_shield_guard_enemy.py`
  - `android/tools/test_striker_enemy_contract.py`
  - `android/tools/test_shield_guard_enemy_contract.py`
  - أطالس/masters الهاتف وTV للعدوين و`asset_manifest.json`.
  - `android/app/build.gradle` (`versionCode 34` / `0.30.1-alpha`).
- الاختبارات:
  - فحص هوامش 72 إطارًا — PASS: 12px للهاتف و8px لـTV كحد أدنى.
  - `validate_assets.py` — PASS: 55 PNG، 10 أطالس، 92 ملف manifest.
  - `validate_animation_atlases.py --allow-nonclustered` — PASS: 10/10.
  - `test_customer_release.sh customers/family-current` — PASS؛ Release/R8/Lint/
    signature/archive/controller/TV memory والسلاسة نجحت.
  - Runtime على جهاز/Emulator — SKIPPED؛ لم يكن جهاز متصلًا.
- Release: `v0.30.1-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.30.1-alpha
  - APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.30.1-alpha/family-force-neon-streets.apk
  - SHA-256: `a86935bbff5b9510862d6f6cf087dd3b6378ebbd96824d9514f4c12f9f8b496f`.
  - commit: `f12a8d3b40019636587b53dc64f7045463617580`.
- ملاحظات/مخاطر: يلزم تأكيد بصري على جهاز المستخدم في الاتجاهين؛ لا يوجد قص
  حسابيًا داخل أطالس الهاتف أو TV بعد الإصلاح.
- التالي: اختبار كل صف حركة للعدوين يمينًا ويسارًا على Xiaomi Stick أو Shield.

### 2026-08-21-24 — تجهيز v0.30.0-alpha

- المنفذ: Codex
- طلب المستخدم: تجهيز `v0.30.0-alpha`.
- الحالة: مكتمل.
- نقطة البداية: `v0.29.3-alpha` / commit `ea1b71c`.
- ما تم:
  - فصل خصائص الأعداء إلى `EnemyArchetype` وتشكيلات التحميل إلى `StageRoster`.
  - تحميل أطالس أعداء المرحلة الحالية فقط؛ الحد الأقصى خمسة من ستة أنواع.
  - إنشاء Shield Guard بصور ImageGen ثابتة فقط: Model Sheet وثلاثة Action Sheets،
    ثم بناء أطلس 36 إطارًا ونسخة TV بنسبة 75% دون أي فيديو.
  - إضافة حراسة اتجاهية: صد أمامي، عداد GUARD واضح، كسر حراسة، وضرب كامل من الخلف.
  - توزيع Shield Guard في المراحل 2–4 والإبقاء على كل تشكيلة ضمن حزمة مرحلتها.
  - رفع النسخة إلى `versionCode 33` / `0.30.0-alpha` ونشرها على GitHub.
- الملفات المعدلة:
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/app/src/main/java/com/familyforce/neonstreets/EnemyArchetype.java`
  - `android/app/src/main/java/com/familyforce/neonstreets/StageRoster.java`
  - `android/app/src/main/assets/enemies/shield_guard*.png`
  - `android/app/src/main/assets/tv/enemies/shield_guard_anim.png`
  - `android/tools/build_shield_guard_enemy.py`
  - `android/tools/test_shield_guard_enemy_contract.py`
  - validators/TV generator/tests/manifest/assets contract و`android/app/build.gradle`.
- الاختبارات:
  - `:app:compileDebugJavaWithJavac :app:lintDebug :app:assembleDebug` — PASS.
  - `android/tools/test_customer_release.sh customers/family-current` — PASS؛
    Release/R8/Lint/signature/archive/metadata والعقود الثابتة نجحت.
  - `validate_assets.py` — PASS: 55 PNG أساسيًا، 10 أطالس، 92 ملف manifest.
  - `validate_animation_atlases.py --allow-nonclustered` — PASS: 10/10.
  - اختبارات Controller/TV memory/smoothness/companion/weapons/checkpoint/audio/
    encounter/diagnostics/Striker/Shield Guard — PASS؛ ميزانية القتال `30.09 MiB`.
  - Runtime على جهاز/Emulator — SKIPPED؛ لم يكن جهاز متصلًا.
- Release: `v0.30.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.30.0-alpha
  - APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.30.0-alpha/family-force-neon-streets.apk
  - SHA-256: `75f9c7b0d0c254f7f1c42ea06d819d5ebd1d81bf2d1d63c188d95f5cde57eac3`.
  - commit: `71594e31659b69490a35b5db92e2579ecd26660f`.
- ملاحظات/مخاطر: يلزم اختبار فعلي على Xiaomi Stick وShield للتأكد من انتقال
  حزم المراحل وميكانيكية الحراسة تحت ضغط جلسة طويلة؛ لم يُدع نجاح ذلك هنا.
- التالي: اختبار ميداني للمراحل 1–4، الضرب من الأمام/الخلف وكسر GUARD، ثم قراءة
  Flight Recorder والذاكرة بعد جلسة لاعب ولاعبين.

### 2026-08-21-23 — الخطوة التالية بعد تثبيت Striker

- المنفذ: Codex
- طلب المستخدم: «ما التالي؟» بعد إصلاح التفاف Striker والقفاز.
- الحالة: مكتمل — تخطيط فقط، دون تعديل اللعبة أو إنتاج أصول.
- نقطة البداية: `v0.29.3-alpha` / commit `ea1b71c`.
- القرار:
  - بوابة قبول قصيرة أولًا لـStriker على الجهاز الحقيقي: المشي واللكمة والسقوط
    يمينًا ويسارًا، للتأكد من القفاز وعدم وجود التفاف في نسخة TV المخفضة.
  - المرحلة البرمجية التالية هي فصل بيانات الأعداء عن `GameView` إلى تعريفات
    `EnemyArchetype` وتشكيلات `StageRoster`، ثم تحميل أطالس المرحلة الحالية فقط.
  - بعدها يُنتج Shield Guard كعدو سادس عبر ImageGen بصور ثابتة/Model Sheets فقط،
    بلا فيديو، ويُدمج بصد أمامي وكسر حراسة بالHeavy/Special وضعف من الخلف.
  - الإصدار المستهدف لهذه الحزمة `v0.30.0-alpha`، مع قياس الذاكرة والسلاسة على
    Android TV وعدم تجاوز ميزانية الأطالس الحالية في الذاكرة.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات: Runtime — SKIPPED؛ هذا طلب تخطيط فقط.
- Release: لا يوجد؛ تحديث توثيقي فقط.
- ملاحظات/مخاطر: إضافة Shield إلى preload الحالي قبل stage roster ستراكم الأطالس
  وتعيد خطر التقطيع على Xiaomi Stick؛ لذلك البنية تسبق الصور الجديدة.
- التالي: عند طلب التنفيذ، البدء بـEnemyArchetype/StageRoster وتحميل حزم المراحل،
  ثم إنتاج ودمج Shield Guard وإصدار v0.30 بعد QA.

### 2026-08-21-22 — انضغاط مقدمة قفاز Striker بعد إزالة الالتفاف

- المنفذ: Codex
- طلب المستخدم: التفاف أجزاء Striker اختفى، لكن مقدمة القفاز أصبحت مقصوصة أو
  مضغوطة في الحركة.
- الحالة: مكتمل — أُعيد اختيار مفاتيح الحركة ونُشر التصحيح.
- نقطة البداية: `v0.29.2-alpha` / commit `bdf30f6`.
- ما تم:
  - إنشاء معاينة للمفاتيح الأصلية قبل remap؛ أكدت أن مفتاح المشي المستخدم في
    v0.29.2 كان قفازه الأمامي مقطوعًا داخل صورة المصدر نفسها.
  - استبعاد كل مفاتيح المشي واللكمة ذات القفاز المقطوع بدل تركيب أو رسم قفاز مصطنع.
  - بناء المشي من ثلاثة gait keys ذات قفازين كاملين مع bob بمقدار 2px، وبناء
    اللكمة من guard/coil كاملين مع lunge للأمام وعودة؛ لا صور أو فيديو جديد.
  - إضافة فحص يمنع اقتراب silhouette المشي من الحد الأيمن للخلية.
  - إعادة أطلس الهاتف وTV ورفع النسخة إلى `versionCode 32` / `0.29.3-alpha`.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
  - `android/app/build.gradle`
  - `android/app/src/main/assets/asset_manifest.json`
  - `android/app/src/main/assets/enemies/striker_anim.png`
  - `android/app/src/main/assets/tv/enemies/striker_anim.png`
  - `android/tools/build_striker_enemy.py`
  - `android/tools/test_striker_enemy_contract.py`
- الاختبارات:
  - `test_striker_enemy_contract.py` — PASS؛ قفاز المشي ضمن الهامش، 36 خلية.
  - `validate_animation_atlases.py` ضمن Release — PASS؛ 9/9.
  - `validate_assets.py` — PASS؛ 89 ملفًا.
  - TV memory/smoothness وبقية العقود — PASS؛ 30.09 MiB.
  - Release build + Lint — PASS.
  - Runtime emulator — SKIPPED؛ لا يوجد emulator/device متصل في هذه الجولة.
- Release:
  - tag: `v0.29.3-alpha`
  - commit: `ea1b71c1830dca5b683fb016d93b080fe46688bd`
  - https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.29.3-alpha
  - https://github.com/linkq8/family-force-neon-streets/releases/download/v0.29.3-alpha/family-force-family-current.apk
  - SHA-256: `1f08dadcb60235ab93cba453e35d5cc89be3751ed989944a53dc3775dd61d6a7`
- ملاحظات/مخاطر: تم QA بصريًا للأطلس وعقديًا، لكن تجربة الحركة الفعلية على جهاز
  المستخدم هي بوابة القبول لأن المحاكي غير متصل الآن.
- التالي: تثبيت v0.29.3 وتجربة قفاز Striker في المشي واللكمة.

### 2026-08-21-21 — التفاف أجزاء Striker بين خلايا التحريك

- المنفذ: Codex
- طلب المستخدم: العدو الجديد يُقص من الأعلى وتظهر أجزاؤه في الأسفل، كما تختفي
  أجزاء من اليمين/اليسار وتظهر من الجهة المقابلة أثناء الحركة.
- الحالة: مكتمل — أُعيد بناء الأطلس ونُشر Release إصلاح.
- نقطة البداية: `v0.29.1-alpha` / commit `1b42008`.
- ما تم:
  - تأكيد أن المحرك يقرأ خلايا نسخة TV بأبعادها الفعلية؛ الخلل داخل صور المصدر:
    بعض الوضعيات والمؤثرات تجاوزت حدود panel والتصقت بجسم الوضعية المجاورة.
  - تعديل البناء لمسح gutters، واستخراج أكبر مكوّن متصل يمثل جسم Striker، ومنع
    الشظايا الصغيرة المنفصلة من دخول الخلية النهائية.
  - استبدال مفاتيح المشي/الضرب المتداخلة بمفاتيح سليمة من الصور الأصلية نفسها،
    مع bob بمقدار 2px للحفاظ على ستة إطارات مرئية؛ لم تُنتج صور أو فيديوهات جديدة.
  - إضافة اختبار يفحص كل خلية من 36 ويشترط مكوّنًا متصلًا واحدًا، ثم إعادة إنتاج
    أطلس الهاتف 960×1152 وأطلس TV 720×864 وتحديث manifest.
  - رفع `versionCode` إلى 31 و`versionName` إلى `0.29.2-alpha`.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
  - `android/app/build.gradle`
  - `android/app/src/main/assets/asset_manifest.json`
  - `android/app/src/main/assets/enemies/striker.png`
  - `android/app/src/main/assets/enemies/striker_anim.png`
  - `android/app/src/main/assets/tv/enemies/striker_anim.png`
  - `android/tools/build_striker_enemy.py`
  - `android/tools/test_striker_enemy_contract.py`
- الاختبارات:
  - `test_striker_enemy_contract.py` — PASS؛ 36 خلية نظيفة/مكوّن واحد/2px.
  - `validate_assets.py` — PASS؛ 89 ملفًا manifest مطابقًا.
  - `validate_animation_atlases.py` ضمن Release gate — PASS؛ 9/9 أطالس.
  - `test_runtime_smoothness_contract.py` — PASS؛ ميزانية التحريك 30.09 MiB.
  - `test_tv_encounter_memory_contract.py` — PASS؛ تخفيض أطلس TV 43.75%.
  - `test_customer_release.sh` — PASS؛ Release/Lint والهاتف/Fold/Android TV
    ومسار الريموت للاعبين، بلا FATAL/ANR/OOM.
- Release:
  - tag: `v0.29.2-alpha`
  - commit: `bdf30f6312e5aad2d88268cc17a0a2743d5b5b9f`
  - https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.29.2-alpha
  - https://github.com/linkq8/family-force-neon-streets/releases/download/v0.29.2-alpha/family-force-family-current.apk
  - SHA-256: `954ce0dabc5abc2db877a6102901a648b2ea25496d0a2b8c0dda7b472711531d`
- ملاحظات/مخاطر: اختبار الأطلس يمنع عودة القطع المنفصلة؛ القبول المرئي النهائي
  يبقى تجربة Striker الفعلية على جهاز المستخدم في المشي والهجوم والسقوط.
- التالي: تثبيت `v0.29.2-alpha` وتجربة Striker؛ ثم استكمال بنية قوائم المراحل.

### 2026-08-21-20 — تراجع DualSense على Nvidia Shield Pro

- المنفذ: Codex
- طلب المستخدم: وحدة تحكم PS5 أصبحت لا تعمل على Nvidia Shield Pro.
- الحالة: مكتمل — نُشر تصحيح عاجل مستقل.
- نقطة البداية: `v0.29.0-alpha` / commit `7af42f2`.
- ما تم:
  - تحديد سببين للتراجع: الاعتماد على اسم الجهاز وحده، والاعتماد على مصدر الحدث
    اللحظي بدل قدرات InputDevice؛ كلاهما غير موثوق على بعض نسخ Shield OEM.
  - التعرف على PlayStation بمعرّف Sony `0x054c` إضافة إلى الاسم.
  - دمج مصادر الجهاز الفعلية مع مصدر الحدث، كي يُعامل زر DualSense المعلن كـ
    Keyboard كزر Gamepad ويحافظ على هوية P1/P2.
  - تطبيع scan codes القياسية 304–317 على Shield والتخطيطات القديمة؛ وهي تطابق
    خريطة AOSP الرسمية لـDualSense ولا تغيّر Xbox/Joy-Con أو الريموت.
  - رفع `versionCode` إلى 30 و`versionName` إلى `0.29.1-alpha`.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
  - `android/app/build.gradle`
  - `android/app/src/main/java/com/familyforce/neonstreets/ControllerCompat.java`
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/tests/ControllerCompatMain.java`
- الاختبارات:
  - `bash android/tools/test_controller_compat.sh` — PASS؛ يتضمن Sony vendor/OEM
    name وKeyboard-source scan codes وShield لا يستخدم Xiaomi fallback.
  - `:app:assembleDebug :app:lintDebug` — PASS.
  - `bash android/tools/test_customer_release.sh ../customers/family-current` —
    PASS؛ Release/Lint والأصول والهاتف وFold وAndroid TV ومسار الريموت للاعبين.
- Release:
  - tag: `v0.29.1-alpha`
  - commit: `1b420082ff5e030abfa1e530012e15a9add09d43`
  - https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.29.1-alpha
  - https://github.com/linkq8/family-force-neon-streets/releases/download/v0.29.1-alpha/family-force-family-current.apk
  - SHA-256: `ddf07a0355f04b40536e1b75ade913eb3c46c335174d7741b101c3715cc4b4de`
- ملاحظات/مخاطر: المحاكي لا يستطيع انتحال Bluetooth HID الحقيقي؛ تبقى تجربة
  DualSense الفعلية على Shield بوابة قبول المستخدم، لكن مسارات التراجع مغطاة آليًا.
- التالي: تثبيت `v0.29.1-alpha` على Shield وتجربة D-pad والعصا وCross/Options
  والقائمة والقتال؛ ثم العودة لخطة EnemyArchetype/StageRoster.

### 2026-08-21-19 — تحديد الخطوة التالية بعد Striker

- المنفذ: Codex
- طلب المستخدم: «الآن ما التالي؟» بعد تنفيذ أول عدو جديد.
- الحالة: مكتمل — تخطيط فقط، دون تعديل اللعبة أو إنتاج صور.
- نقطة البداية: `v0.29.0-alpha` / commit `7af42f2`.
- القرار:
  - بوابة القبول الأولى هي تجربة Striker على Xiaomi Stick في لاعب واحد ولاعبين،
    ومراقبة التحريك والقتال والذاكرة وعدم ظهور تقطيع عند دخوله.
  - قبل مضاعفة عدد الأعداء، تفصل بياناتهم إلى `EnemyArchetype` وتشكيلاتهم إلى
    `StageRoster`، مع تحميل أطالس أعداء المرحلة الحالية فقط وإخلائها عند الانتقال.
    هذا يمنع إبقاء 16 أطلسًا في الذاكرة مستقبلًا ويحافظ على نتيجة Xiaomi الجيدة.
  - بعد تأسيس ذلك، يكون Shield Guard هو العدو السادس: 36 إطارًا عبر أربع صور
    ImageGen بلا فيديو، مع صد أمامي وكسر حراسة بالضربة الثقيلة أو Special وضعف من الخلف.
  - يأتي Blaster بعده، لكن فقط بعد إضافة مقذوفات مجمعة وtelegraph واضح للهجوم.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات:
  - Runtime — SKIPPED؛ هذا طلب تخطيط فقط.
- Release: لا يوجد؛ تحديث توثيقي فقط.
- المخاطر المتبقية: إضافة الأطالس بالتتابع إلى preload الحالي سترفع ضغط الذاكرة
  على أجهزة TV منخفضة الإمكانات حتى لو بقي حجم APK مقبولًا.
- التالي: تنفيذ بنية `EnemyArchetype` و`StageRoster` وحزم أطالس المراحل، ثم دمج
  Shield Guard وإصدار `v0.30.0-alpha` بعد QA كامل.

### 2026-08-21-18 — تنفيذ أول عدو جديد: Striker

- المنفذ: Codex
- طلب المستخدم: البدء الآن بتنفيذ عدو واحد من الخطة الجديدة.
- الحالة: مكتمل ومختبر ومنشور.
- نقطة البداية: `v0.28.0-alpha` / commit `b6617f8`.
- ما تم:
  - اختيار Striker كأول عدو لأنه يضيف هجوم combo سريعًا مع أقل مخاطرة على
    البنية مقارنة بالمقذوفات أو الطيران.
  - اعتماد ImageGen المدمج للصور فقط، دون فيديو ودون Higgsfield credits.
  - إنتاج Model Sheet وألواح Idle/Walk وAttack1/Attack2 وHurt/Knockdown، ثم
    بناء Atlas حقيقي 6×6 / 36 إطارًا بخلايا 160×192 و2-pixel clusters.
  - إضافة نسخة static 512×512 ونسخة TV 720×864 تحتفظ بكل الإطارات وتخفض
    decoded memory بنسبة 43.75% عن Atlas التأليف.
  - توسيع Runtime إلى خمسة أنواع وإضافة Striker إلى أربع مواجهات؛ HP 76، سرعة
    1.48، هجومان jab-cross/rising-hook، cooldown وضرر ونقاط مستقلة.
  - تصحيح منطق heavy launch حتى لا يُعامل النوع رقم 4 تلقائيًا كـBrute لمجرد
    أن رقمه أكبر من 2.
  - تحديث عقود الأصول والـTV والذاكرة ورفع النسخة إلى `0.29.0-alpha`.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
  - `android/app/build.gradle`
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/app/src/main/assets/enemies/striker.png`
  - `android/app/src/main/assets/enemies/striker_anim.png`
  - `android/app/src/main/assets/tv/enemies/striker_anim.png`
  - `android/app/src/main/assets/asset_manifest.json`
  - `assets/imagegen/android/enemies/striker/*`
  - `android/tools/build_striker_enemy.py`
  - `android/tools/test_striker_enemy_contract.py`
  - `android/tools/generate_tv_optimized_assets.py`
  - `android/tools/validate_assets.py`
  - `android/tools/validate_animation_atlases.py`
  - `android/tools/test_runtime_smoothness_contract.py`
  - `android/tools/test_tv_encounter_memory_contract.py`
  - `android/design/assets.csv`
- الاختبارات:
  - `python3 android/tools/build_striker_enemy.py` — PASS؛ 36 إطارًا وhard alpha
    و2-pixel clusters.
  - `python3 android/tools/validate_assets.py` — PASS؛ 54 PNG أساسيًا، 9 Atlases،
    و89 ملفًا مطابقًا للـmanifest.
  - `validate_animation_atlases.py --allow-nonclustered` — PASS 9/9؛ استُخدم
    الاستثناء للأبطال legacy، بينما اختبار Striker المستقل يفرض 2px فعلًا.
  - `python3 android/tools/test_striker_enemy_contract.py` — PASS.
  - اختبارات TV memory/smoothness/attack tokens/encounter gate — PASS؛ ميزانية
    الرسومات المتحركة TV أصبحت 30.09 MiB.
  - `./gradlew :app:assembleDebug :app:lintDebug` — PASS.
  - `android/tools/test_full_stage_runtime.sh` — PASS؛ المراحل/الموجات التسع.
  - Runtime Emulator لمواجهة Stage 1 — PASS؛ ظهر Striker وتحرك/هاجم، دون
    FATAL/ANR/OOM.
  - `android/tools/test_customer_release.sh` — PASS؛ Release/Lint والهاتف وFold
    وAndroid TV والريموت واللاعبان والعقود الكاملة.
  - اختبار updater فعلي من `v0.28` إلى `v0.29` — PASS؛ نزّل وتحقق وفتح إذن
    المصدر ثم Package Installer، وبعد التأكيد أصبحت النسخة المثبتة 29.
- Release: `v0.29.0-alpha`، commit
  `7af42f21e1beab663911a3746840debad23aa8d7`:
  - https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.29.0-alpha
  - https://github.com/linkq8/family-force-neon-streets/releases/download/v0.29.0-alpha/family-force-family-current.apk
  - SHA-256: `8b3de3e44b4ad702eba62484921243177f15d0c2560c4c957453ba155f8f939d`.
- ملاحظات/مخاطر: لن يدمج Atlas قبل فحص وضوح الإطارات وثبات الاتجاه والقدم،
  ولن تُحمّل أصول إضافية على TV خارج Stage pack المطلوب.
- التالي: اختبار Striker يدويًا على Xiaomi Stick، ثم إنتاج Shield Guard بالطريقة نفسها.

### 2026-08-21-17 — اعتماد ImageGen كمسار أعداء أقل تكلفة

- المنفذ: Codex
- طلب المستخدم: تقديم خيار أرخص، وشرح لماذا لا تُولد صور الأعداء داخل ChatGPT.
- الحالة: مكتمل — قرار إنتاج فقط، دون توليد صور أو تعديل Runtime.
- نقطة البداية: `v0.28.0-alpha` / commit `9f11427`.
- ما تم:
  - اعتماد أداة ImageGen المدمجة في ChatGPT كالمسار الأساسي للأعداء الجدد؛ لا
    تحتاج API key ولا تستهلك رصيد Higgsfield، مع خضوعها لحدود خطة ChatGPT.
  - تخفيض الخطة من 84 إلى 48 صورة مولدة: لكل عدو Model Sheet واحد وثلاثة
    Action Sheets، كل Sheet يحتوي حركتين × ستة إطارات؛ الناتج النهائي يبقى
    36 إطارًا وAtlas 6×6 لكل عدو.
  - اعتماد استخدام Higgsfield فقط كخيار احتياطي لحالة فشل محددة، وليس خط الإنتاج.
  - اعتماد تنظيف alpha/defringe والتثبيت والتحجيم وبناء Atlas والتحقق محليًا.
  - توضيح أن ImageGen مناسب أكثر للأعداء لأنهم لا يحتاجون مطابقة هوية عائلية
    دقيقة مثل الأبطال، ويمكن تثبيت هويتهم عبر Model Sheet مرجعي واحد.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات:
  - قراءة عقد أداة `imagegen` المدمجة — PASS؛ تدعم generation/edit/transparent
    ولا تحتاج `OPENAI_API_KEY` في المسار الافتراضي.
  - Runtime/Build/Image generation — SKIPPED؛ المستخدم طلب الخيار فقط.
- Release: لا يوجد؛ تعديل توثيقي فقط.
- ملاحظات/مخاطر: توليد 36 خلية في صورة واحدة غير موصى به بسبب صغر التفاصيل
  وتداخل الخلايا؛ ثلاث Action Sheets لكل عدو هي الحد العملي الأرخص مع جودة قابلة
  للفصل. يجب قبول Model Sheet قبل توليد الحركات لتجنب هدر الحصة.
- التالي: عند الموافقة على التنفيذ، إنتاج ثلاثة أعداء للدفعة الأولى عبر ImageGen
  المدمج: 3 Model Sheets + 9 Action Sheets، ثم دمجها واختبارها قبل بقية الأنواع.

### 2026-08-21-16 — مضاعفة خطة الأعداء وتحديد أدوات الصور

- المنفذ: Codex
- طلب المستخدم: مضاعفة عدد الأعداء الجدد المقترحين، وتحديد الأداة التي ستولد
  الشخصيات.
- الحالة: مكتمل — تخطيط وتحقق أدوات فقط، دون توليد أو تعديل Runtime.
- نقطة البداية: `v0.28.0-alpha` / commit `7c1d993`.
- ما تم:
  - توسيع الخطة من 6 إلى 12 نوعًا جديدًا، ليصبح الإجمالي 16 نوعًا مع الأنواع
    الأربعة الحالية.
  - الأنواع الجديدة: Striker، Shield Guard، Blaster، Grappler، Hover Drone،
    Lieutenant، Acrobat، Repair Medic، Bomber، Charger، Magnet Controller،
    وSoundwave DJ.
  - اعتماد Higgsfield للصور فقط بلا فيديو: `nano_banana_flash` لإنشاء
    Character Model Sheet ثابت لكل نوع، و`gpt_image_2` لإنشاء ستة Action Sheets
    4×2 لكل نوع، ثم اختيار ستة إطارات لكل حالة وبناء Atlas 6×6 محليًا.
  - اعتماد إزالة chroma-key والتنظيف والـdefringe والتثبيت bottom-center محليًا؛
    استخدام `image_background_remover` فقط للحالات الصعبة، لتوفير الرصيد.
  - التحقق من الكتالوج الحي: Nano Banana 2 وGPT Image 2 وImage Background
    Remover متاحة؛ AutoSprite غير ظاهر في الكتالوج الحالي.
  - تقدير الإنتاج الأساسي: 12 Model Sheets + 72 Action Sheets = 84 طلب صورة،
    432 إطار Runtime، وتكلفة Higgsfield تقريبية 162 credit قبل الإعادات؛ مع
    احتياطي مستهدف 30–40 credit، من الرصيد الحالي 305.96.
  - تقسيم التنفيذ إلى أربع دفعات، ثلاثة أنواع جديدة في كل إصدار، مع Stage
    asset packs تمنع تحميل الأطالس الستة عشر معًا على Xiaomi Stick.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات:
  - `higgsfield account status` — PASS؛ Ultra، رصيد 305.96.
  - `higgsfield model list --json` — PASS؛ نماذج الصور المطلوبة متاحة.
  - `higgsfield generate cost ...` — PASS؛ Nano 1K = 1.5، GPT Image 2 1K
    medium = 2، Background Remover = 1 credit.
  - Runtime/Build — SKIPPED؛ هذا طلب خطة فقط.
- Release: لا يوجد؛ تعديل توثيقي فقط.
- ملاحظات/مخاطر: 84 صورة تحتاج بوابة قبول قبل أي retry؛ يمنع إرسال دفعات عمياء.
  جودة Action Sheets يجب أن تعتمد إطارًا كاملًا واتجاهًا ثابتًا وهوية مستقرة؛
  ويُرفض النوع قبل الدمج إذا لم تمر الحالات الست.
- التالي: عند طلب التنفيذ، البدء بثلاثة أنواع فقط: Striker وShield وBlaster،
  ثم اختبار الذاكرة/الحركة على Xiaomi Stick قبل إنتاج الدفعة الثانية.

### 2026-08-21-15 — خطة توسيع أنواع الأعداء

- المنفذ: Codex
- طلب المستخدم: اللعبة قصيرة وتحتاج أنواع أعداء أكثر؛ المطلوب خطة قبل التنفيذ.
- الحالة: مكتمل — تخطيط فقط، دون تعديل اللعبة أو الأصول.
- نقطة البداية: `v0.28.0-alpha` / commit `5613e06`.
- ما تم:
  - مراجعة الأنواع الحالية: Grunt وSkater وBrute وJunk King، وعقد Atlas العدو
    الحالي 6 حالات × 6 إطارات بخلايا 160×192.
  - اعتماد إضافة ستة أدوار قتالية حقيقية على ثلاث دفعات: Striker وShield، ثم
    Ranged وGrappler، ثم Drone وStage Lieutenant؛ مع إبقاء Junk King زعيمًا نهائيًا.
  - اعتماد EnemyArchetype/StageRoster بدل الشروط الرقمية المتفرقة، مع HP وسرعة
    ومدى وضرر ووزن وAI وdrop مستقل لكل نوع.
  - اعتماد Stage asset packs: لا يحمل الجهاز جميع الأطالس الجديدة معًا؛ يحمل
    فقط تشكيلة المرحلة الحالية ويحرر السابقة، لحماية Xiaomi Stick.
  - اعتماد إنتاج صور ثابتة/Model Sheets وإطارات حركة فقط، دون فيديو: Model Sheet
    واحد + 36 إطارًا لكل عدو عادي، وModel Sheet + 48–60 إطارًا للملازم إن أعطي
    هجمات خاصة إضافية.
  - تقسيم التنفيذ إلى `v0.29` للبنية ونوعين، `v0.30` لنوعين، و`v0.31` لنوعين
    وموازنة التشكيلات، مع بوابة ذاكرة وأداء Android TV لكل إصدار.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات:
  - مراجعة عقد الأعداء والتوزيع والتحميل الحاليين في `GameView.java` — PASS.
  - Runtime/Build — SKIPPED؛ هذا طلب خطة فقط.
- Release: لا يوجد؛ تعديل توثيقي فقط.
- ملاحظات/مخاطر: إضافة الأطالس الستة دفعة واحدة إلى الذاكرة قد تعيد التقطيع أو
  OOM؛ لذلك Stage packs والتحميل المسبق المحدود شرطان وليسا تحسينًا اختياريًا.
- التالي: تنفيذ دفعة `v0.29`: EnemyArchetype + StageRoster + Striker + Shield،
  بالصور فقط، ثم اختبار Xiaomi Stick قبل متابعة بقية الأنواع.

### 2026-08-21-14 — التحديث الآمن من داخل التطبيق

- المنفذ: Codex
- طلب المستخدم: تنفيذ ميزة فحص وتنزيل آخر نسخة من GitHub من داخل اللعبة وإصدار
  نسخة جديدة بها.
- الحالة: مكتمل ومختبر ومنشور.
- نقطة البداية: `v0.27.0-alpha` / commit `839a488`.
- ما تم:
  - التحقق أن الميزة السابقة كانت خطة فقط وليست موجودة في الكود.
  - إضافة خيار `GAME UPDATE` قابل للتحديد بالريموت/يد التحكم واللمس داخل Settings،
    مع حالات واضحة للفحص والتنزيل والتحقق وعدم وجود تحديث.
  - إضافة فحص GitHub Latest Release واختيار أصل APK المطابق لـ`customerId` فقط.
  - تنزيل الملف إلى Cache خاص، ورفضه ما لم يتطابق الحجم وSHA-256 واسم الحزمة
    وversionCode الأعلى ومجموعة شهادات التوقيع وcertificate pin عند توفره.
  - إضافة ContentProvider خاص محدود القراءة لملف APK المتحقق منه فقط، من دون
    AndroidX أو زيادة اعتماديات Runtime.
  - فتح إعداد السماح بالتثبيت عند الحاجة ثم مثبت Android الرسمي؛ لا تثبيت صامت.
  - رفع النسخة إلى `versionCode 28` / `0.28.0-alpha`.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
  - `android/app/build.gradle`
  - `android/app/src/main/AndroidManifest.xml`
  - `android/app/src/main/java/com/familyforce/neonstreets/MainActivity.java`
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/app/src/main/java/com/familyforce/neonstreets/UpdateManager.java`
  - `android/app/src/main/java/com/familyforce/neonstreets/UpdateFileProvider.java`
  - `android/tools/test_in_app_update_contract.py`
- الاختبارات:
  - `python3 android/tools/test_in_app_update_contract.py` — PASS (18/18).
  - `./gradlew :app:assembleDebug :app:lintDebug` — PASS؛ Android Lint بلا أخطاء.
  - `python3 android/tools/validate_assets.py` — PASS (86 ملفًا في Manifest).
  - `bash android/tools/test_controller_compat.sh` — PASS.
  - `bash android/tools/test_customer_release.sh` — PASS؛ Release build/Lint،
    الهاتف وultrawide وFold وAndroid TV ومسار لاعبين والعقود الكاملة.
  - اختبار Emulator بريموت TV من Title إلى Settings ثم `GAME UPDATE` — PASS؛
    ظهرت `UP TO DATE` وبقيت العملية حية دون FATAL/ANR/OOM.
- Release: `v0.28.0-alpha`، commit
  `975c9043c6c94f39d5ea8df3ce923a37705c6fb0`:
  - https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.28.0-alpha
  - https://github.com/linkq8/family-force-neon-streets/releases/download/v0.28.0-alpha/family-force-family-current.apk
  - SHA-256: `ef27f8b8c0fe7d735a90dae7eabca2dd739f3466b315cbf4e8bc109dd5bda9ab`.
- ملاحظات/مخاطر: Android لا يسمح بتحديث صامت؛ يجب أن يؤكد المستخدم التثبيت،
  وقد يفعّل السماح لهذا التطبيق بتثبيت APK مرة واحدة.
- التالي: تثبيت النسخة الحالية يدويًا؛ زر التحديث سيستقبل النسخ التالية بدءًا
  من `v0.29` لأن `v0.27` لا يحتوي الزر أصلًا.

### 2026-08-21-13 — تحويل الفصول إلى أربع مراحل مستقلة

- المنفذ: Codex
- طلب المستخدم: الخلفيات الحالية لا تزال ضمن مرحلة واحدة؛ المطلوب `STAGE 1`
  إلى `STAGE 4` كـمراحل جديدة فعلية، مع إعادة تلوين الأعداء عبر Hue لإعطاء
  إحساس بشخصيات جديدة من دون تغيير الرسومات.
- الحالة: مكتمل ومختبر ومنشور.
- نقطة البداية: `v0.26.0-alpha` / commit `909837a`.
- ما تم:
  - اعتماد تعديل برمجي فقط، بلا صور أو فيديو جديد.
  - بدء مراجعة تقدم المناطق، انتقالات المرحلة، حفظ checkpoint، ورسم ألوان الأعداء.
  - تحويل المواجهات التسع إلى أربع مراحل مستقلة: مرحلتان بموجتين، مرحلة بثلاث
    موجات، ومرحلة نهائية بموجتين والزعيم.
  - إضافة شاشة `STAGE CLEAR` ثم شاشة استعداد للمرحلة التالية مع إيقاف اللعب
    مؤقتًا، واستعادة 20% من صحة الفريق عند إكمال كل مرحلة.
  - استبدال عرض `AREA 1/9` بعرض `STAGE 1–4` و`WAVE`، وإعادة ترتيب أسماء المواقع
    واللافتات لتتوافق مع كل مرحلة.
  - إضافة أربعة اتجاهات لونية للأعداء عبر `ColorMatrixColorFilter` ثابتة؛ نفس
    الأطالس والحركة لكن ألوان مختلفة لكل Stage، بلا إنشاء Bitmap أو تخصيص داخل الإطار.
  - إبقاء ألوان الأبطال الأصلية لحماية هوية أفراد العائلة، وتطبيق التنويع على
    الأعداء فقط.
  - رفع النسخة إلى `versionCode 27` / `0.27.0-alpha`.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
  - `android/app/build.gradle`
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/tools/test_checkpoint_contract.py`
  - `android/tools/test_runtime_smoothness_contract.py`
- الاختبارات:
  - `test_runtime_smoothness_contract.py` — PASS؛ أربع مراحل وفلاتر ثابتة وميزانية
    الصور `27.72 MiB`.
  - `:app:assembleDebug :app:lintDebug` — PASS.
  - `test_full_stage_runtime.sh` — PASS؛ المراحل الأربع/الموجات التسع حتى النتائج.
  - فحص Runtime بصري للمراحل 1–4 — PASS؛ الأسماء والخلفية/الـHue تتبدل.
  - `test_checkpoint_contract.py` — PASS؛ الحفظ يحدث قبل انتقال المرحلة.
  - `test_customer_release.sh` — PASS؛ Release والهاتف/Fold/Android TV والريموت
    واللاعبان والذاكرة دون FATAL/ANR/OOM.
- Release: `v0.27.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.27.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.27.0-alpha/family-force-family-current.apk
- SHA-256: `2446baa91e2b0608934f085c82a5d3175424468f6566eadff0d9c879fb08966c`.
- commit: `4d85d0464b3fb3b6c6a3e4c0029eefc16f86b1a7`.
- ملاحظات/مخاطر: المرحلة الرابعة تستخدم خلفية قصر الخردة المشتركة مع نهاية
  المرحلة الثالثة لكن مع لون بيئة وردي/بنفسجي أقوى؛ يمكن لاحقًا إنتاج خلفية مستقلة.
- التالي: commit ثم GitHub Release، وبعده اختبار انتقالات STAGE على Xiaomi Stick.

### 2026-08-21-12 — تنويع المراحل بصريًا

- المنفذ: Codex
- طلب المستخدم: "لنبدأ تنويع المراحل، لأنها هي التي ستبين أننا طورنا اللعبة فعلاً."
- الحالة: مكتمل ومختبر ومنشور.
- نقطة البداية: `v0.25.0-alpha` / commit `57893a0`.
- ما تم:
  - بدء مراجعة نظام رسم العالم والمناطق التسع وعقد أصول Android TV.
  - اعتماد صور ثابتة فقط ومنع أي إنتاج فيديو، مع إبقاء القتال والمنطق الحاليين.
  - تقسيم المسار إلى ثلاثة فصول بصرية: السوق للمناطق 1–3، محطة/نفق النقل
    للمناطق 4–6، والميناء/قصر الخردة للمناطق 7–9.
  - إنشاء خلفيتي النقل والميناء كصور ثابتة، مع محاولة تصحيح واحدة لإزالة النصوص
    والشخصيات غير المطلوبة، وفحص النتيجة بصريًا قبل الدمج.
  - إضافة أسماء وألوان الفصول ولافتات صحيحة لكل منطقة، مع انتقال فوري بلا فك صور
    أو I/O أثناء القتال.
  - إنشاء نسخ TV بقياس `800×450` وتحميل الخلفيات الثلاث بصيغة `RGB_565`؛ أصبحت
    ميزانية صور القتال المتحركة `27.72 MiB`.
  - رفع النسخة إلى `versionCode 26` / `0.26.0-alpha`.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
  - `android/app/build.gradle`
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/app/src/main/assets/backgrounds/stage_transit.png`
  - `android/app/src/main/assets/backgrounds/stage_harbor.png`
  - `android/app/src/main/assets/tv/backgrounds/stage_market.png`
  - `android/app/src/main/assets/tv/backgrounds/stage_transit.png`
  - `android/app/src/main/assets/tv/backgrounds/stage_harbor.png`
  - `android/app/src/main/assets/asset_manifest.json`
  - `android/design/assets.csv`
  - `android/tools/generate_tv_optimized_assets.py`
  - `android/tools/validate_assets.py`
  - `android/tools/test_runtime_smoothness_contract.py`
- الاختبارات:
  - `validate_assets.py` — PASS؛ 53 PNG أساسيًا و8 Atlases و86 ملف manifest.
  - `test_runtime_smoothness_contract.py` — PASS؛ `27.72 MiB`.
  - `:app:assembleDebug :app:lintDebug` — PASS.
  - `test_full_stage_runtime.sh` — PASS؛ المناطق 1–9 حتى النتائج.
  - فحص صور Runtime للفصول الثلاث — PASS؛ السوق/النقل/قصر الخردة تظهر منفصلة.
  - `test_customer_release.sh` — PASS؛ الهاتف/Fold/Android TV/ريموت/لاعبان
    والذاكرة دون FATAL/ANR/OOM.
- Release: `v0.26.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.26.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.26.0-alpha/family-force-family-current.apk
- SHA-256: `8377dc0c27bcb931036fb32734c844fbd73bcede761a4628071dd516238e856c`.
- commit: `ccf2512a8a187e8ec203100f24f8983c580d589c`.
- تصحيح 2026-08-21: استبدال SHA مكتوب خطأ في تحديث السجل الأول بالـSHA الفعلي
  أعلاه كما يثبته `git rev-parse ccf2512`؛ لا يوجد اختلاف في كود الإصدار.
- ملاحظات/مخاطر: اختبار المناطق آلي على المحاكي؛ يبقى الاختبار البصري الحقيقي
  للمراحل الجديدة على Xiaomi Stick مفيدًا، لكنه ليس حاجزًا برمجيًا.
- التالي: commit ثم GitHub Release، وبعده اختبار بصري للاعبين على Xiaomi Stick.

### 2026-08-21-11 — اعتماد v0.25 على Xiaomi والمرحلة التالية

- المنفذ: Codex
- طلب المستخدم: اللعبة جيدة؛ جلسة كاملة للاعبين بلا تقطيع مع استدعاء المساعدين،
  وكل شيء نظيف. ما الخطوة التالية؟
- الحالة: مكتمل — اعتماد نتيجة الاختبار وترتيب خارطة الطريق، دون تغيير اللعبة.
- نقطة البداية: `v0.25.0-alpha` / commit `c2648a4`.
- ما تم:
  - اعتماد اختبار Xiaomi Stick الحقيقي كـPASS للعب الثنائي الكامل، السلاسة، Link
    ورسومات الأعداء بعد hotfix.
  - إغلاق مخاطر DualSense والتقطيع وانقلاب Atlas المفتوحة للإصدار الحالي.
  - التوصية التالية: تجميد v0.25 كمرشح استقرار، ثم إضافة تحسينات على دفعات صغيرة
    تبدأ بتجربة القتال والمحتوى لا بالبنية أو الرسومات الأساسية.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات:
  - Xiaomi Stick / جلسة كاملة / لاعبان / Link — USER PASS.
- Release: لا يوجد؛ تحديث توثيقي فقط، وآخر Release هو `v0.25.0-alpha`.
- ملاحظات/مخاطر: كل إضافة لاحقة يجب أن تمر بنفس بوابات TV/لاعبين/ذاكرة وألا
  تعيد تحميل الصور داخل القتال.
- التالي: مرحلة gameplay polish: إصلاح/تحسين رمي السلاح، تنويع الأعداء والزعيم،
  ثم checkpoints/updater، كل ميزة في إصدار مستقل قابل للرجوع.

### 2026-08-21-10 — انقلاب أنصاف رسومات الأعداء في v0.24

- المنفذ: Codex
- طلب المستخدم: الأعداء يظهر نصفهم السفلي في الأعلى والعلوي في الأسفل، مع حركة
  غير واضحة وغريبة.
- الحالة: مكتمل برمجيًا ومختبر؛ جارٍ نشر hotfix.
- نقطة البداية: `v0.24.0-alpha` / commit `e2a35a9`.
- ما تم:
  - تحديد regression: بعد التحميل المسبق أصبح `spawnEnemy()` يرى Atlas TV جاهزًا
    ويربطه بخلايا الأصل الثابتة `160×192`، رغم أن Atlas TV خلاياه `120×144`.
  - هذا يجعل `SpriteAnimator` يقص مناطق تتجاوز الصف/العمود الصحيح، فيخلط أنصاف
    الإطارات والصفوف. المسار اللاحق كان يحسب الأبعاد ديناميكيًا بصورة صحيحة.
  - استبدال الثوابت في `spawnEnemy()` بحساب `atlas width/6` و`height/6`، فيعمل
    كل من Atlas TV `720×864` والأصل `960×1152` بنفس المسار الصحيح.
  - إضافة regression gate يرفض أي عودة لثوابت `160×192` في ربط العدو.
  - فحص Atlas TV بصريًا وفحص لقطة Runtime بعد الإصلاح؛ الجسم والإطارات كاملة.
  - رفع النسخة إلى `versionCode 25` / `0.25.0-alpha`.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
  - `android/app/build.gradle`
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/tools/test_runtime_smoothness_contract.py`
- الاختبارات:
  - `test_runtime_smoothness_contract.py` — PASS؛ أبعاد spawn ديناميكية.
  - `:app:assembleDebug :app:lintDebug` — PASS.
  - `test_customer_release.sh` — PASS مع محاكي متصل؛ Runtime/TV/remote/مواجهة/
    ذاكرة وأصول دون FATAL/ANR/OOM.
  - لقطة Runtime `/tmp/enemy-fix.png` — PASS بصريًا؛ العدو كامل وغير مقلوب.
- Release: `v0.25.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.25.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.25.0-alpha/family-force-family-current.apk
- SHA-256: `81b1cd41d0af2f79a2a5ce5c64ef7dc4345afef8204688097d918e0f83548e45`.
- commit: `72987a48b4b33d8b333df9548f3026116c7ab08a`.
- ملاحظات/مخاطر: الصور نفسها سليمة؛ الخلل في حساب source rectangles، فلا حاجة
  لإعادة إنتاج أو ضغط الرسومات.
- التالي: نشر APK ثم التحقق على Xiaomi Stick الحقيقي.

### 2026-08-21-09 — تحسين سلاسة اللعبة كاملة على Android TV

- المنفذ: Codex
- طلب المستخدم: عدم الاكتفاء بإصلاح Link؛ مراجعة حجم اللعبة والصور والتحريك
  والبكسلات والاستدعاءات ومنع التعليقات في جميع أجزاء اللعبة، خصوصًا Xiaomi Stick.
- الحالة: مكتمل برمجيًا ومختبر؛ جارٍ تجهيز الإصدار.
- نقطة البداية: `v0.23.0-alpha` / commit `fdf375b`.
- ما تم:
  - بدء تدقيق دورة الإطار ومسارات تحميل الأصول والذاكرة والصوت والمؤثرات.
  - نقل فك أطالس الأعداء الأربعة إلى Thread خلفي منخفض الأولوية يبدأ في شاشة
    الاختيار، مع إبقائها جاهزة طوال المرحلة.
  - إزالة فك/تحميل/تحرير أطالس الأعداء من بوابات المجموعات و`updateEncounter()`؛
    إذا لم يكتمل warmup يُستخدم العدو الثابت مؤقتًا بلا حجب لخيط اللعب.
  - استبدال `getPixel()` المتكرر في فحص حدود إطارات الأبطال بقراءة `getPixels()`
    كتلية، مع الحفاظ على نفس القص والوضوح.
  - إضافة بوابة تمنع Bitmap decode/I/O داخل update والقتال وLink، وتثبت أبعاد
    أصول TV وميزانية قتال متحركة قصوى `26.65 MiB`.
  - مراجعة الأبعاد: خلايا الأبطال `144×144` والأعداء `120×144` في نسخة TV
    مناسبة لحجم عرض `640×360`؛ لم تُصغّر أكثر لتجنب خسارة تفاصيل.
  - توثيق الميزانية والمراجع الرسمية في تقرير Android TV مستقل.
  - رفع النسخة إلى `versionCode 24` / `0.24.0-alpha`.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
  - `android/ANDROID_TV_SMOOTHNESS_REPORT_AR.md`
  - `android/app/build.gradle`
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/tools/test_customer_release.sh`
  - `android/tools/test_runtime_smoothness_contract.py`
  - `android/tools/test_tv_encounter_memory_contract.py`
- الاختبارات:
  - `test_runtime_smoothness_contract.py` — PASS؛ 26.65 MiB ولا decode داخل PLAY.
  - `test_tv_encounter_memory_contract.py` — PASS؛ warmup خلفي وتقليل 43.75%.
  - `test_link_preload_contract.py` — PASS.
  - `:app:assembleDebug :app:lintDebug` — PASS.
  - `test_customer_release.sh` — PASS مع محاكي متصل؛ Build/Lint/assets/TV/remote/
    لاعبان/أول مواجهة/ذاكرة/صوت/checkpoint/Runtime دون FATAL/ANR/OOM.
- Release: `v0.24.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.24.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.24.0-alpha/family-force-family-current.apk
- SHA-256: `ed08fd254c9b5fc129112c9d22f9f87596dec3c3370dfab9af4dd025858c562a`.
- commit: `bb61b23d1b263829597d9149ecc5314cbe475d9e`.
- ملاحظات/مخاطر: الهدف إزالة العمل الثقيل من وقت القتال مع الحفاظ على وضوح
  640×360 والأطالس التلفزيونية وعدم زيادة خطر OOM.
- التالي: نشر APK ثم جلسة Xiaomi فعلية لقياس Link وبدايات المجموعات والمراحل.

### 2026-08-21-08 — إزالة تعليق استدعاء Link جذريًا

- المنفذ: Codex
- طلب المستخدم: حل تعليق استدعاء البطل المساعد على Xiaomi Stick بشكل جذري.
- الحالة: مكتمل برمجيًا ومختبر؛ جارٍ نشر الإصدار.
- نقطة البداية: `v0.22.0-alpha` / commit `db70be0`.
- ما تم:
  - اعتماد الحل: تجهيز صفوف Link قبل القتال والاحتفاظ بها طوال الجولة، ومنع أي
    فك PNG أو مسح بكسلات داخل `startAssist()`.
  - إضافة cache مستقل لصف المساعد الخاص بـP1 وصف المساعد الخاص بـP2، مع حدود
    الإطارات المحسوبة مسبقًا.
  - أصبح `startAssist()` يربط Bitmap جاهزًا فقط بلا I/O أو decode أو pixel scan.
  - الاحتفاظ بالصفوف طوال الجولة وإعادة استخدامها؛ تحريرها عند العودة للقائمة.
  - عند ضغط الذاكرة أثناء اللعب تُحرر الصفوف فقط إذا لم يكن المساعد نشطًا، وبعدها
    يستخدم الاستدعاء الرسم الاحتياطي بلا إعادة تحميل متزامنة أو تعليق.
  - رفع النسخة إلى `versionCode 23` / `0.23.0-alpha`.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
  - `android/app/build.gradle`
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/tools/test_customer_release.sh`
  - `android/tools/test_link_preload_contract.py`
- الاختبارات:
  - `tools/test_link_preload_contract.py` — PASS؛ يمنع decode/recycle داخل مسار Link.
  - `:app:assembleDebug :app:lintDebug` — PASS؛ Lint نظيف.
  - `tools/test_customer_release.sh ../customers/family-current` — PASS مع محاكي
    Android متصل؛ البناء والتوقيع والأصول والذاكرة وأول مواجهة والسلاح والصوت
    والـcheckpoint وRuntime QA كلها ناجحة.
- Release: `v0.23.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.23.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.23.0-alpha/family-force-family-current.apk
- SHA-256: `6dc3ca197716d9e7d2be26faa21be3825fe47c82d642d61e47f1fe912d9d3933`.
- commit: `812dddfc893835ade902d0c0dd46d92fe64c9f90`.
- ملاحظات/مخاطر: يجب موازنة ذاكرة صفين صغيرين للاعبين مع ضغط الذاكرة؛ عند trim
  ستستخدم اللعبة fallback جاهزًا بدل إعادة التحميل داخل القتال.
- التالي: نشر APK ثم قياس الاستدعاء على Xiaomi Stick الحقيقي.

### 2026-08-21-07 — تشخيص تعليق Link على Xiaomi Stick

- المنفذ: Codex
- طلب المستخدم: يوجد تعليق خفيف عند استدعاء البطل المساعد في وضع اللاعب الواحد
  على Xiaomi TV Stick؛ تحديد السبب.
- الحالة: مكتمل — تشخيص فقط، دون تعديل سلوك اللعبة.
- نقطة البداية: `v0.22.0-alpha` / commit `f9167fb`.
- ما تم:
  - تتبع مسار `startAssist()` إلى `loadAssistAnimationRow()`.
  - تبيّن أن أول إطار للاستدعاء ينفذ بصورة متزامنة على خيط اللعب: فتح PNG، إنشاء
    `BitmapRegionDecoder`، فك صف Link، `prepareToDraw()`، ثم مسح شفافية كل بكسل
    عبر `cacheHeroAnimSourceRects()`.
  - نسخة TV تخفّض الـAtlas إلى `1152×1584`، لكن صف Link ما زال `1152×144`
    RGBA ويستلزم فكًا ومسحًا ورفع texture لحظة الضغط.
  - عند انتهاء المساعد يعاد تدوير `assistAnimArt` ويُصفّر `loadedAssistHero`، لذلك
    تتكرر الكلفة عند كل استدعاء لاحق بدل دفعها مرة واحدة.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات:
  - مراجعة مسار الكود وأبعاد/أحجام أطالس TV — PASS كتشخيص ساكن.
  - قياس frame-time على Xiaomi الحقيقي — NOT AVAILABLE؛ يحتاج عتاد المستخدم.
- Release: لا يوجد؛ توثيق تشخيصي فقط.
- ملاحظات/مخاطر: السبب CPU/I/O/texture-upload متزامن، وليس حجم APK ولا منطق حركة Link.
- التالي: تحميل صف Link مسبقًا قبل اللعب والاحتفاظ به طوال الجولة، مع حدود إطارات
  مولدة مسبقًا بدل مسح البكسلات وقت الاستدعاء.

### 2026-08-21-06 — استمرار خلل DualSense على Xiaomi بعد v0.21

- المنفذ: Codex
- طلب المستخدم: المشكلة لا تزال موجودة بعد تثبيت إصلاح DualSense الأول.
- الحالة: مكتمل برمجيًا؛ بانتظار تحقق المستخدم على Xiaomi Stick الحقيقي.
- نقطة البداية: `v0.21.0-alpha` / commit `d68ac9a`.
- ما تم:
  - الاستنتاج الأولي: Firmware Xiaomi لا يعلن trigger ranges بالتوقيع الذي اعتمد
    عليه Auto-detection، أو يرسل KeyEvent للأزرار بمصدر Keyboard.
  - إضافة fallback ضيق لأسماء مضيف Xiaomi/Mi Box/Mi Stick/Mi TV، ولا يعمل إلا
    عندما تكون اليد PlayStation ورمز المسح ضمن تعيين AOSP.
  - تمرير أحداث DualSense عبر التطبيع حتى إن أعلنها النظام كمصدر Keyboard.
  - فصل اكتشاف محاور L2/R2 القديمة عن fallback الأزرار؛ لا تُحوّل Z/RZ إلا عند
    وجود نطاق signed فعليًا، حمايةً لإصدارات Xiaomi الحديثة.
  - رفع النسخة إلى `versionCode 22` / `0.22.0-alpha`.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
  - `android/app/build.gradle`
  - `android/app/src/main/java/com/familyforce/neonstreets/ControllerCompat.java`
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/tests/ControllerCompatMain.java`
  - `android/CONTROLLER_COMPATIBILITY_REPORT_AR.md`
- الاختبارات:
  - `tools/test_controller_compat.sh` — PASS؛ Xiaomi/Mi Box موجب وShield/Sony سالب.
  - `:app:assembleDebug :app:lintDebug` — PASS؛ Lint نظيف.
  - `tools/test_customer_release.sh ../customers/family-current` — PASS؛ بناء
    Release والأصول والذاكرة وأول مواجهة والسلاح والـcheckpoint والصوت ومسار TV.
- Release: `v0.22.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.22.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.22.0-alpha/family-force-family-current.apk
- SHA-256: `31805a102da8bd7e2c5c56b8fd0f74bbcab4fdf49ae2a87409583198e584cac1`.
- commit: `13783bff59d9bdac55d51a77e9fdab837660af8a`.
- ملاحظات/مخاطر: يلزم تفعيل fallback بحسب هوية مضيف Xiaomi مع إبقاء تصحيح
  المحاور منفصلًا حتى لا يتضرر Firmware حديث بتخطيط triggers صحيح.
- التالي: اختبار APK المنشور على Xiaomi Stick الحقيقي؛ المحاكي لا يحاكي Firmware Bluetooth.

### 2026-08-21-05 — خلل أزرار DualSense على Xiaomi Stick

- المنفذ: Codex
- طلب المستخدم: ليست كل أزرار PS5 DualSense تعمل بشكل صحيح على Xiaomi Stick؛
  فحص التوافق وإصلاحه.
- الحالة: مكتمل برمجيًا؛ بانتظار تحقق المستخدم على Xiaomi Stick الحقيقي.
- نقطة البداية: `v0.20.0-alpha` / commit `2cb0810`.
- ما تم:
  - تبيّن من AOSP أن Android أضاف ملف DualSense fallback للأجهزة التي لا تحمل
    `CONFIG_HID_PLAYSTATION`، بينما صور TV القديمة قد تفتقده.
  - إضافة اكتشاف ديناميكي للتخطيط المكسور من نطاق L2/R2 الموقع `-1..1` بدل `0..1`.
  - إعادة تعيين scan codes `304..317` لأزرار الوجه والكتف وOptions/Share والعصوين.
  - تصحيح L2/R2 من محوري Z/RZ في التخطيط القديم، مع إبقاء المسار القياسي كما هو.
  - إضافة ضغط Touchpad كاختصار احتياطي للرمي على DualSense.
  - عدم تطبيق fallback على Xbox/Joy-Con أو DualSense ذي التخطيط القياسي.
  - جعل اختبار Android TV للاعبين حتميًا بمسح checkpoint السابق قبل المسار.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
  - `android/app/build.gradle`
  - `android/app/src/main/java/com/familyforce/neonstreets/ControllerCompat.java`
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/tests/ControllerCompatMain.java`
  - `android/tools/test_customer_release.sh`
  - `android/CONTROLLER_COMPATIBILITY_REPORT_AR.md`
- الاختبارات:
  - `tools/test_controller_compat.sh` — PASS، بما فيها legacy DualSense وعدم تغيير Xbox.
  - `:app:assembleDebug :app:lintDebug` — PASS.
  - `tools/test_customer_release.sh` — PASS على البناء والتوقيع والأصول والهاتف
    وultrawide وFold وAndroid TV ومسار ريموت/لاعبين؛ لا FATAL/ANR/OOM.
  - Xiaomi Stick + DualSense حقيقي — PENDING USER TEST.
- Release: `v0.21.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.21.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.21.0-alpha/family-force-family-current.apk
- SHA-256: `4f73a484bab163f033e45c75d9ee7223d9bee1bfd379a12a80dfcdb9543aee8f`.
- commit: `94c42afbe0c215db3b1f8a3666283de29efadeb7`.
- ملاحظات/مخاطر: المحاكي لا يستطيع تقليد key layout الخاص بFirmware Xiaomi؛
  التعيين واكتشاف المحاور مختبران آليًا لكن يلزم تأكيد المستخدم على الجهاز الحقيقي.
- التالي: رفع `v0.21.0-alpha`، ثم تجربة جميع أزرار DualSense وL2/Touchpad على Xiaomi.

### 2026-08-21-04 — نتائج اختبار Shield وخريطة التطوير التالية

- المنفذ: Codex
- طلب المستخدم: تسجيل نجاح اللعب والمناطق 1–9 والأسلحة عدا الرمي، والموت/الإحياء،
  والإغلاق/الفتح، والريموت/إعادة توصيل اليد على Nvidia Shield Pro؛ ثم اقتراح
  التطويرات التالية.
- الحالة: مكتمل — تسجيل نتيجة وترتيب خارطة طريق، دون إصلاح برمجي في هذا الطلب.
- نقطة البداية: `v0.20.0-alpha` / commit `b641f21`.
- ما تم:
  - اعتماد اختبار Nvidia Shield Pro كـPASS للمناطق 1–9، الالتقاط، الموت والإحياء،
    دورة الإغلاق/الفتح، فصل اليد وإعادتها، والتنقل بالريموت، دون crash غير طبيعي.
  - تسجيل رمي السلاح كـBug مفتوح؛ وجود كود L2/THROW لا يكفي لأن المسار لم يعمل
    للمستخدم فعليًا.
  - تسجيل Checkpoint كغير مختبر لأن المستخدم لم يخسر، وXiaomi Stick كمؤجل لوقت لاحق.
  - اعتماد ترتيب التطوير: (1) إصلاح الرمي ووضوح زرّه، (2) اختبار Checkpoint/Xiaomi،
    (3) updater، (4) توسعة القتال والأعداء والمراحل والزعيم.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات:
  - Nvidia Shield Pro — USER PASS وفق النتائج المذكورة أعلاه.
  - Weapon throw — USER FAIL.
  - Checkpoint — NOT TESTED.
  - Xiaomi Stick — PENDING.
  - اختبارات كود جديدة — SKIPPED؛ لم يطلب المستخدم التنفيذ بعد.
- Release: لا يوجد؛ تحديث توثيقي فقط.
- ملاحظات/مخاطر: يجب اختبار الرمي عبر L2 digital وanalog، زر اللمس، P1/P2،
  DualSense/Xbox/Joy-Con، مع ارتداد السلاح وإصابته وإعادة التقاطه.
- التالي: تنفيذ إصلاح رمي السلاح كأول تعديل في `v0.21.0-alpha`.

### 2026-08-21-03 — تحديد الخطوة التالية بعد الوصول إلى شبه الاستقرار

- المنفذ: Codex
- طلب المستخدم: اللعبة شبه مستقرة حاليًا؛ تحديد الخطوة التالية.
- الحالة: مكتمل — توصية وترتيب أولويات، دون تعديل برمجي.
- نقطة البداية: `v0.20.0-alpha` / commit `18c1c12`.
- ما تم:
  - اعتماد مرحلة Release Candidate للثبات قبل إضافة محتوى جديد.
  - الأولوية الأولى: جلسة لعب قتالية حقيقية 30–45 دقيقة على Android TV منخفض
    الذاكرة، للاعب واحد ولاعبين، عبر المناطق 1–9 والزعيم والأسلحة والـContinue.
  - تشمل البوابة تعليق/استئناف التطبيق، فصل اليد وإعادتها، التنقل بالريموت، فحص
    التشخيص بعد الإغلاق، وقياس الذاكرة والإطارات.
  - بعد اجتيازها: تنفيذ updater الداخلي الآمن مع fallback إلى GitHub Releases.
  - يؤجل المحتوى الجديد إلى ما بعد تثبيت نسخة RC ناجحة.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات:
  - Runtime — SKIPPED؛ هذا طلب تخطيط فقط.
- Release: لا يوجد؛ تحديث توثيقي فقط.
- ملاحظات/مخاطر: الاختبار الآلي الحالي يثبت مسار المناطق، لكنه لا يعوض جلسة
  قتال حقيقية طويلة على عتاد TV منخفض الذاكرة.
- التالي: تنفيذ بوابة RC للاستقرار وإصدار `v0.21.0-alpha/rc` عند نجاحها.

### 2026-08-21-02 — دراسة زر تحديث اللعبة من GitHub

- المنفذ: Codex
- طلب المستخدم: إضافة زر داخل اللعبة يفحص آخر إصدار على GitHub وينزّل التحديث
  بدل البحث اليدوي، أو على الأقل يفتح صفحة Releases مباشرة.
- الحالة: مكتمل — دراسة وقرار معماري، دون تنفيذ برمجي بعد.
- نقطة البداية: `v0.20.0-alpha` / commit `281195b`.
- ما تم:
  - فحص Manifest الحالي؛ التطبيق بلا صلاحية Internet أو تثبيت حزم.
  - التحقق أن مستودع GitHub عام وأن Latest Release API يعرض APK وSHA-256.
  - التحقق من قيود Android: التطبيق العادي لا يثبت تحديثًا بصمت؛ يحتاج موافقة
    المستخدم من Package Installer، وقد يحتاج تفعيل مصدر التثبيت مرة واحدة.
  - اعتماد الاقتراح: زر `CHECK FOR UPDATE` يفحص versionCode، ينزّل APK الصحيح،
    يتحقق من SHA-256 واسم الحزمة وشهادة التوقيع، ثم يفتح مثبت Android؛ مع زر
    احتياطي `OPEN RELEASE PAGE` عند فشل التنزيل أو عدم توفر المثبت.
  - تسجيل ضرورة ربط كل نسخة تجارية بـcustomerId/applicationId وأصل APK خاص بها؛
    لا يجوز أن تنزّل نسخة عميل APK عميل آخر.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات:
  - فحص GitHub Latest Release API — PASS (`v0.20.0-alpha` وأصل APK موجودان).
  - مراجعة AndroidManifest وصلاحيات الشبكة/التثبيت — PASS؛ الصلاحيات غير موجودة حاليًا.
  - اختبار Runtime — SKIPPED؛ لم يُنفذ كود جديد.
- Release: لا يوجد؛ دراسة توثيقية فقط.
- ملاحظات/مخاطر: إضافة updater تلغي وصف التطبيق بأنه بلا اتصال إنترنت. التحديث
  الصامت غير متاح لتطبيق عادي؛ التأكيد النظامي مطلوب للحماية. فتح صفحة GitHub فقط
  أبسط، لكن بعض أجهزة Android TV لا تحتوي متصفحًا مناسبًا.
- التالي: عند موافقة المستخدم، تنفيذ updater داخلي آمن مع fallback لصفحة Releases،
  ثم اختباره على الهاتف وAndroid TV ورفع Release جديد.

### 2026-08-21-01 — إنشاء ذاكرة مشتركة بين Codex وClaude Code

- المنفذ: Codex
- طلب المستخدم: إنشاء ملف يسجل كل تحديث ونسخة وطلب، ليعرف Codex وClaude Code
  ما أنجزه الطرف الآخر وأين توقف العمل.
- الحالة: مكتمل
- نقطة البداية: `v0.20.0-alpha` / commit `e845b66`.
- ما تم:
  - إنشاء هذا السجل المركزي مع تاريخ مستعاد وحالة حالية وقالب موحد.
  - إضافة تعليمات مشروع لـCodex في `AGENTS.md`.
  - إضافة تعليمات مشروع لـClaude Code في `CLAUDE.md`.
  - اعتماد تحديث السجل بعد كل طلب أو تعديل أو اختبار أو Release.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
  - `AGENTS.md`
  - `CLAUDE.md`
  - `README.md`
- الاختبارات:
  - `git diff --check` — PASS.
  - فحص وجود تعليمات القراءة والتحديث في `AGENTS.md` و`CLAUDE.md` — PASS.
  - فحص وجود أقسام الحالة والبروتوكول والسجل والتسليم في الملف المركزي — PASS.
- Release: لا يوجد؛ هذا تحديث توثيقي فقط.
- ملاحظات/مخاطر: لا يمكن استعادة النص الحرفي الكامل لكل المحادثات القديمة من
  Git؛ جرى تمييز التاريخ القديم كملخص مستعاد من الأدلة المتاحة.
- التالي: على الوكيل القادم قراءة هذا الملف وتسجيل أول طلب جديد قبل تعديله.

## تسليم العمل الحالي

- المالك الأخير: Codex.
- الحالة: `v0.31.0-alpha` منشور؛ المراحل الأربع تملك هويات قتال ومكافآت مختلفة.
- آخر عمل: إضافة قواعد Stage مستقلة وMini-boss وأهداف/HUD ومكافآت، مع إبقاء
  الأطالس والذاكرة ضمن الحد السابق ودون أصول جديدة.
- آخر قرار: إبقاء التحميل حسب المرحلة وعدم الاحتفاظ بالأنواع الستة معًا، والاستمرار
  بصورة Model/Action Sheets فقط من دون فيديو.
- الملفات المتوقع أن يقرأها الوكيل التالي أولًا:
  1. `PROJECT_HISTORY_AR.md`
  2. `android/README.md`
  3. `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  4. `android/app/src/main/java/com/familyforce/neonstreets/EnemyArchetype.java`
  5. `android/app/src/main/java/com/familyforce/neonstreets/StageRoster.java`
  6. `android/tools/test_shield_guard_enemy_contract.py`
- الإجراء التالي المقترح: تحديث إلى `v0.31.0-alpha` ولعب المراحل الأربع في نمطي
  لاعب/لاعبين، ثم ضبط HP/pressure/recovery من ملاحظات الجهاز الحقيقي.
