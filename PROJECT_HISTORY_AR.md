# السجل المشترك للمشروع — Family Force: Neon Streets

> هذا الملف هو المصدر المركزي لتبادل السياق بين **Codex** و**Claude Code**.
> يجب على كل وكيل قراءته قبل تعديل المشروع، وتحديثه بعد كل طلب أو تعديل أو
> اختبار أو Release. سجل الأحداث أدناه تراكمي؛ لا تُحذف الإدخالات القديمة.

آخر تحديث: 25 أغسطس 2026 — Codex

## حالة العمل الحالية

- المنتج الأساسي: لعبة Android أصلية بنمط beat-'em-up ريترو حديث، وليست Emulator.
- المنصة: الهاتف، Fold، Android TV، والريموت/يد التحكم.
- النسخة المنشورة: `v0.49.1-alpha`، `versionCode 61`.
- الفرع المشترك: `main`.
- آخر commit وظيفي: `514f988f3facc6be6165f8cbc5d48c77c7e98e1a`.
- الحزمة الحالية: `com.familyforce.neonstreets.event.familycurrent`.
- Release: https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.49.1-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.49.1-alpha/family-force-family-current.apk
- SHA-256: `0eb16fd3fb797fe3c3491573642d58e8f3548f028c319ca731d3d06574f6196c`.
- حالة QA: واجهة Canvas والقصة ثنائيتا اللغة عبر 241 مفتاحًا متطابقًا؛ نجح
  Build/Release/R8/Lint والتوقيع والتحقق من الأصول والتحكم وعقود الأداء وذاكرة
  TV. أكمل Android TV Emulator المسار الكامل للمناطق الـ14 والمراحل الخمس، ونجحت ملفات
  phone/ultrawide/Fold/TV ومسار الريموت دون FATAL/ANR/OOM.
- نتيجة Xiaomi Stick الحقيقية لـv0.25: جلسة كاملة بلا تقطيع للاعبين، مع نجاح
  استدعاء الشخصيات الإضافية ونظافة الرسومات والحركة.
- اختبار المناطق: مسار تطويري آلي مرّ بالمناطق 1–14 حتى شاشة النتائج بنجاح.
- التشخيص: يوجد Flight Recorder محلي خفيف يحفظ آخر منطقة، P1/P2، العدو،
  السلاح، الحركة والذاكرة، ويحفظ تقرير الجلسة السابقة إذا انقطعت.
- نتيجة اختبار Shield Pro: المناطق 1–9، الموت/الإحياء، الإغلاق/الفتح، فصل اليد،
  الريموت والتقاط الأسلحة تعمل دون خروج غير طبيعي.
- إصلاح قيد تحقق المستخدم: أعيدت رسومات `v0.48` المقبولة وأُلغي توليد الإطارات
  المزاحة؛ وفي اللعب الفردي أصبحت أحدث يد Gamepad تملك P1 حتى لو عرّف الجهاز
  ريموت TV كمصدر Gamepad، مع إبقاء فصل اليدين في طور لاعبين.
- الاختبارات المتبقية: جلسة لعب بشرية كاملة للنسخة الجديدة على Xiaomi Stick وShield.
- العمل التالي الموصى به: اختبار `v0.49.1-alpha` بصريًا على Shield لحركات Essa
  وAdam والأعداء، واختبار DualSense داخل PLAY الفردي ولاعبين. لا يعاد شرط 12
  صورة إلا بعد إنتاج 12 رسمة حقيقية مستقلة لكل حركة وقبول عينة شخصية واحدة.
- أداة الإنتاج: `asset-vault/` تفهرس 101 سجل و181 ملفًا (تغطية Manifest كاملة)،
  وتشغّل الأطالس الـ26 بقيم المحرك الفعلية، مع عقود QA لكل العائلات، حجر وفك
  ترميز حقيقي، اعتماد مرتبط بالبصمة والحقوق، وتجهيز آمن يبدأ بمعاينة Dry-run.

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

### 2026-08-25-84 — Regression بصري وتحكم DualSense في v0.49

- المنفذ: Codex
- طلب المستخدم: جميع الشخصيات، خصوصًا Essa وAdam، والأعداء أصبحت أسوأ وأكبر
  قليلًا في `v0.49`، ويد PS5 لا تستجيب داخل اللعب بينما الريموت يعمل.
- الحالة: مكتمل ومنشور في `v0.49.1-alpha`.
- نقطة البداية: `v0.49.0-alpha` / commit
  `99b3b1a233d3508f4021f570d91361a516550eec`.
- ما تم:
  - ثبتت المقارنة أن `v0.49` صنع 12 خلية عبر تكرار الوضعيات وتحريكها بمقدار
    بكسل واحد، كما فعّل مسار clips جديدًا للأعداء؛ النتيجة كانت اهتزازًا بصريًا
    وتغيرًا في الحجم/الوضوح، وليست حركة مرسومة حقيقية.
  - استرجاع أصول Essa وAdam وGrunt وLantern ونسخ Base/Runtime/TV/UHD ومصادر
    الإنتاج حرفيًا من `v0.48.0-alpha` المقبولة، مع استرجاع محمل الأطالس القديم.
  - إصلاح توجيه Android TV في اللاعب الواحد: بعض أجهزة TV قد تعرّف الريموت
    كمصدر Gamepad، فكانت DualSense تُدفع إلى P2 ولا تحرك البطل؛ الآن أحدث يد
    لعب في PLAY الفردي تملك P1 دائمًا، بينما يبقى فصل P1/P2 في طور لاعبين.
  - رفع الإصدار محليًا إلى `v0.49.1-alpha` / `versionCode 61`.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
  - `android/app/build.gradle`
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/app/src/main/java/com/familyforce/neonstreets/SpriteAnimator.java`
  - `android/app/src/main/assets/{clips,runtime/clips,tv/clips,uhd/clips}/...`
  - `assets/imagegen/android/animation-clips-v1/...`
  - `android/app/src/main/assets/asset_manifest.json`
  - `android/tools/{build_separate_animation_clips.py,test_separate_animation_clips.py,test_tv_encounter_memory_contract.py,test_runtime_smoothness_contract.py,test_single_player_controller_routing_contract.py,test_customer_release.sh}`
  - `android/docs/SEPARATE_ANIMATION_CLIP_STANDARD_AR.md`
- الاختبارات:
  - `./android/tools/test_controller_compat.sh` — PASS.
  - `python3 android/tools/test_single_player_controller_routing_contract.py` — PASS.
  - اختبارات separate clips وTV encounter وruntime smoothness — PASS؛ ميزانية
    الصور المتحركة المحملة `71.20 MiB`.
  - `./gradlew :app:assembleDebug` — PASS.
  - `./android/tools/test_customer_release.sh` — PASS كامل: Release/R8/Lint،
    التوقيع والأصول، phone/ultrawide/Fold/TV، مسار الريموت واللعب حتى المواجهة
    دون FATAL/ANR/OOM.
  - `validate_animation_atlases.py` المنفرد — FAIL معروف على شرط محاذاة 2px
    لـ`parent_anim.png` المستعاد؛ مدقق الإصدار الفعلي قبل الـAPK مرر الأطالس
    `26/26`. لم نعد تشكيل الصورة بهذا الشرط لأنه يزيد مظهر البكسل الذي رفضه المستخدم.
- Release: `v0.49.1-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.49.1-alpha
  - APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.49.1-alpha/family-force-family-current.apk
  - SHA-256: `0eb16fd3fb797fe3c3491573642d58e8f3548f028c319ca731d3d06574f6196c`.
  - commit: `514f988f3facc6be6165f8cbc5d48c77c7e98e1a`.
- ملاحظات/مخاطر: عقد 12 **صورة مرسومة حقيقية** مؤجل؛ لا تُقبل إطارات مكررة
  أو مزاحة آليًا مرة أخرى. اختبار DualSense الحالي يغطي mapping والتوجيه منطقيًا،
  ويبقى تأكيد اليد الحقيقية على Shield بعد تنزيل الإصدار.
- التالي: اختبار Essa وAdam وDualSense على Shield قبل أي محاولة جديدة لزيادة
  عدد إطارات الحركة.

### 2026-08-25-83 — تصحيح عقد الحركة إلى 12 إطارًا حقيقيًا لكل حركة

- المنفذ: Codex
- طلب المستخدم: "لا زلت تذكر 11 و6 إطارات وأنا طلبت أقل شيء 12"؛ المطلوب أن
  تحتوي **كل حركة** لـEssa وAdam وGrunt وLantern على 12 إطارًا مختلفًا على الأقل،
  وليس مجرد تشغيل عدد أقل من الصور بسرعة 12FPS.
- الحالة: مكتمل ومنشور في `v0.49.0-alpha`.
- نقطة البداية: `v0.48.0-alpha` / commit
  `8e8bc8e5f9641aaf2ef2072f048a20ee04705f90`.
- ما تم:
  - تأكيد أن الإصدار السابق خلط بين عدد الإطارات داخل الحركة ومعدل تشغيلها؛
    الأبطال كانوا 8 إطارات للحركة والأعداء 6 فقط، ولذلك لا يحقق الطلب.
  - إعادة بناء 34 ملف حركة لتحتوي كل حركة 12 خلية صورة مختلفة: 11 حركة لكل
    من Essa وAdam، و6 حركات لكل من Grunt وLantern، مع بقاء كل حركة في ملف UHD
    إنتاج مستقل `3840×2160` ونسخ Base/Runtime/TV مستقلة.
  - إبقاء الرسومات المقبولة وهوية الوجوه، وإنشاء in-betweens نظيفة من دون
    cross-fade أو blur؛ المحرك يستخدم كل الخانات الـ12 ولا يقتطعها إلى 8/6.
  - اكتشاف أن السواد في تجربة Adam كان ثقوب Alpha وكتلًا داكنة داخل الجسم؛
    حُجرت كل تجارب ImageGen المرفوضة خارج المشروع، وأُغلقت الثقوب الداخلية فقط
    مع الحفاظ على الوجه والشعر والفراغات الخارجية، فأصبح الجسم أخضر داخل اللعبة.
  - إصلاح اختيار tier: Android TV يحمل ملفات TV ذات 12 إطارًا بدل Runtime،
    ومسار الأعداء يحول `tv/enemies/` و`runtime/enemies/` إلى مجلد clips الصحيح.
  - تصغير clips أعداء TV قليلًا إلى خلية `180×154`، فبلغت ميزانية textures
    لمسار الـ12 إطارًا `56.27 MiB` بدل تحميل مصادر أعلى من حاجة التلفاز.
- الملفات المعدلة:
  - `android/app/src/main/java/com/familyforce/neonstreets/{GameView,SpriteAnimator}.java`.
  - `android/app/src/main/assets/{clips,runtime/clips,tv/clips,uhd/clips}/`.
  - `assets/imagegen/android/animation-clips-v1/`.
  - `android/tools/{build_separate_animation_clips.py,test_separate_animation_clips.py}`.
  - `android/tools/{test_tv_encounter_memory_contract.py,test_runtime_smoothness_contract.py}`.
  - `android/docs/SEPARATE_ANIMATION_CLIP_STANDARD_AR.md`.
  - `android/app/src/main/assets/asset_manifest.json`.
  - `android/app/build.gradle` و`PROJECT_HISTORY_AR.md`.
- الاختبارات:
  - `test_separate_animation_clips.py` — PASS؛ 34 مصدر UHD و12 خلية مختلفة/حركة.
  - `validate_assets.py` — PASS؛ 305 ملفات Manifest.
  - `:app:assembleDebug :app:lintDebug` — PASS.
  - `test_tv_encounter_memory_contract.py` — PASS.
  - `test_runtime_smoothness_contract.py` — PASS؛ clip budget `56.27 MiB`.
  - `test_animation_runtime.sh` — PASS على 640×360 وUltrawide وFold؛ كل حركات
    Essa المختبرة تغيرت بصريًا، وAdam ظهر أخضر في لقطة Runtime.
  - `test_customer_release.sh` — PASS؛ Release/R8/Lint/توقيع/TV/ريموت/لاعبان
    والذاكرة والمواجهة والسلاح والـcheckpoint والصوت دون FATAL/ANR/OOM.
- Release: `v0.49.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.49.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.49.0-alpha/family-force-family-current.apk
- SHA-256: `0d15eb8566feaa9025ef70c2879619540ed502e92f2289a19f2ce68c452c63d0`.
- commit: `99b3b1a233d3508f4021f570d91361a516550eec`.
- ملاحظات/مخاطر: تجارب ImageGen ذات جسم Adam الأسود لم تدخل الأصول أو APK؛
  نُقلت النسخ المرفوضة إلى مخزن Codex خارج المشروع ويمكن استعادتها للمراجعة.
- التالي: نشر APK ثم اختبار بصري بشري للحركات الأربع على Xiaomi Stick وShield.

### 2026-08-25-82 — دفعة الحركة المنفصلة الأولى: Essa وAdam وGrunt وLantern

- المنفذ: Codex
- طلب المستخدم: بدء تنفيذ معيار الحركة الجديد على `Essa + Adam + Grunt + Lantern`.
- الحالة: مكتمل ومنشور في `v0.48.0-alpha`.
- نقطة البداية: `v0.47.0-alpha` / commit
  `a558db823fdb15dcabdd46609b1b3b2177067e56`.
- ما تم:
  - تحويل حركات الشخصيات الأربع إلى ملفات مستقلة حسب الحركة بدل أطلس يجمع عدة حركات.
  - فرض حد أدنى `12 FPS` لكل clip مع بقاء العرض والمحاكاة عند هدف `60 FPS`.
  - إنشاء 34 مصدر إنتاج مستقلًا بقياس `3840×2160`: 11 حركة لكل من Essa وAdam،
    و6 حركات لكل من Grunt وLantern، مع ملفات Base/Runtime/TV/UHD منفصلة.
  - إزالة الـwhite matte المتصل بالشفافية، وتصفير RGB الشفاف وفرض Alpha ثنائي.
  - إضافة loader يحمّل clip-set مسبقًا، مع fallback آمن للأطلس القديم للشخصيات الأخرى.
  - إصلاح اختبار الحركة القديم لاسم حزمة العميل وتجاوز القصة في وضع Debug فقط.
- الملفات المعدلة:
  - `android/app/src/main/java/com/familyforce/neonstreets/SpriteAnimator.java`.
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`.
  - `android/app/src/main/assets/{clips,runtime/clips,tv/clips,uhd/clips}/`.
  - `assets/imagegen/android/animation-clips-v1/`.
  - `android/tools/build_separate_animation_clips.py`.
  - `android/tools/test_separate_animation_clips.py`.
  - `android/tools/test_animation_runtime.sh`.
  - `android/tools/test_tv_encounter_memory_contract.py`.
  - `android/docs/SEPARATE_ANIMATION_CLIP_STANDARD_AR.md`.
  - `android/app/src/main/assets/asset_manifest.json` و`android/app/build.gradle`.
  - `PROJECT_HISTORY_AR.md`.
- الاختبارات:
  - `test_separate_animation_clips.py` — PASS؛ 34 مصدر UHD، بلا حواف بيضاء ملوثة.
  - `validate_assets.py` — PASS؛ 305 ملفات Manifest.
  - `validate_animation_atlases.py --allow-nonclustered` — PASS؛ 26/26.
  - `:app:assembleDebug :app:lintDebug` — PASS.
  - `test_animation_runtime.sh` — PASS على 640×360 و720×320 وFold 1080×928،
    مع تغير بصري مثبت لكل حركات Essa المختبرة ولقطات Essa/Adam.
  - `test_full_stage_runtime.sh` — PASS لكل المناطق الـ14 بلا FATAL/ANR/OOM.
  - `test_customer_release.sh customers/family-current` — PASS شامل البناء الموقّع،
    R8/Lint، الأصول، الذاكرة، الهاتف/Fold/Android TV ومسار الريموت للاعبين.
- Release: `v0.48.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.48.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.48.0-alpha/family-force-family-current.apk
- SHA-256: `36122fa577f8abe22b99c81f864142ef4172f00530f651173f69b3d472537dbd`.
- commit: `8e8bc8e5f9641aaf2ef2072f048a20ee04705f90`.
- ملاحظات/مخاطر: لم تولد صور AI جديدة ولم يستخدم Higgsfield أو فيديو؛ فُصلت
  الرسومات المقبولة نفسها وحُفظت الهوية. الاختبار البشري على Xiaomi/Shield مطلوب
  للحكم النهائي على الإيقاع البصري، وعداد Actual FPS/P90/P99 داخل اللعبة لم ينفذ بعد.
- التالي: نشر `v0.48.0-alpha` ثم اختبار Essa/Adam/Grunt/Lantern على الجهازين قبل التعميم.

### 2026-08-25-81 — عقد 12FPS وUHD مستقل لكل حركة

- المنفذ: Codex
- طلب المستخدم: ألا يقل FPS أي شخصية عن 12، وأن تكون كل حركة في صورة UHD
  مستقلة دون دمج عدة حركات في صورة واحدة.
- الحالة: مكتمل — تثبيت متطلبات وخطة فقط؛ بانتظار أمر التنفيذ.
- نقطة البداية: `v0.47.0-alpha` / commit
  `a558db823fdb15dcabdd46609b1b3b2177067e56`.
- ما تم:
  - اعتماد 60FPS للعرض والمحاكاة، و12FPS كحد أدنى مستقل لكل clip فني، بما فيه
    idle وwalk وhurt وknockdown.
  - اعتماد ملف مصدر UHD مستقل لكل حركة؛ يمنع استمرار صيغ مثل
    `idle_walk.png` و`hurt_knockdown.png` أو ورقة attacks مشتركة.
  - فصل مصدر الإنتاج عن Runtime: المصدر لا يقل عن `3840×2160`، بينما يشتق منه
    Runtime/TV بالحجم الآمن دون شحن كل مصادر UHD على أجهزة Xiaomi.
  - اقتراح بقاء ملفات Runtime مستقلة لكل حركة أيضًا، مع preload لحركات أبطال
    الجولة وأعداء المواجهة لمنع I/O أو decoding أثناء القتال.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md` فقط.
- الاختبارات:
  - مراجعة عقد الحركة والتحميل الحالي — PASS تشخيصيًا؛ يتطلب تغييرًا في
    `SpriteAnimator` وAsset loading لأن البنية الحالية تجمع الحركات في Atlas واحد.
- Release: لا يوجد.
- ملاحظات/مخاطر: رفع clip من 8 إلى 12FPS دون إضافة وضعيات فريدة لا يحسن السلاسة؛
  يجب أن تفرض البوابة عددًا أدنى من الإطارات المختلفة وعدم التكرار الصوري.
- التالي: عند أمر التنفيذ، يبدأ Pilot بـAdam وGrunt فقط، ثم مقارنة داخل اللعبة
  قبل إنتاج بقية الملفات المستقلة.

### 2026-08-25-80 — مقارنة FPS بألعاب beat-'em-up الحديثة

- المنفذ: Codex
- طلب المستخدم: دراسة FPS في ألعاب أخرى مشابهة وعدم قبول معدل منخفض.
- الحالة: مكتمل — دراسة وقرار هدف فقط؛ لا تعديل APK.
- نقطة البداية: `v0.47.0-alpha` / commit
  `a558db823fdb15dcabdd46609b1b3b2177067e56`.
- ما تم:
  - مراجعة وثائق Android الرسمية ومصادر المطورين لـStreets of Rage 4 وRiver
    City Girls 2، مع فصل FPS العرض عن عدد صور الحركة الفنية.
  - اعتماد `60 FPS` ثابتًا كهدف إلزامي للعب؛ لا يُستخدم 30FPS كحل على Xiaomi،
    بل تخفض المؤثرات/كلفة الرسم إذا لزم للحفاظ على 60.
  - ثبت أن حلقة اللعبة تستهدف 60، لكن `SystemClock.sleep` لا يثبت frame pacing
    ولا يقيس الناتج، لذلك يلزم قياس Actual/P90/P99 ومزامنة Surface قبل الادعاء.
  - شخصيات اللعبة الحالية تملك 88 خانة حركة (11×8)، بينما ذكر فريق Streets of
    Rage 4 قرابة 1000 frame للبطل و300–400 لكل عدو؛ الفرق الأساسي في كثافة
    الوضعيات الفنية، لا في رفع رقم تشغيل الأطلس إلى 60 آليًا.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md` فقط.
- الاختبارات:
  - بحث مصادر رسمية وقراءة عقود التوقيت المحلية — PASS كدراسة.
  - قياس FPS على عتاد حقيقي — SKIPPED؛ يحتاج instrumentation وجهازًا متصلًا.
- Release: لا يوجد.
- ملاحظات/مخاطر: تحويل 8 صور مكررة إلى 60FPS لا يضيف سلاسة؛ تحسين الحركة يتطلب
  توقيتًا أفضل ووضعيات فنية أكثر، مع بقاء عرض اللعبة نفسه 60FPS.
- التالي: تنفيذ عداد/P90/P99 وSurface 60Hz أولًا، ثم قياس Xiaomi وShield قبل
  تقرير عدد الوضعيات الإضافية المطلوبة لكل حركة.

### 2026-08-25-79 — خطة الوضوح وإزالة الحواف وقياس FPS

- المنفذ: Codex
- طلب المستخدم: مراجعة لقطة Stage 1؛ الرسومات جيدة لكنها تحتاج وضوحًا أعلى،
  ومعالجة أفضل للحواف البيضاء، ومعرفة FPS الحالي والمعيار، مع التخطيط قبل التنفيذ.
- الحالة: مكتمل — تشخيص وخطة فقط؛ لم تُعدّل أصول اللعبة أو APK.
- نقطة البداية: `v0.47.0-alpha` / commit
  `a558db823fdb15dcabdd46609b1b3b2177067e56`.
- ما تم:
  - فُحصت لقطة `Screenshot_20260825_111153.jpg` بالحجم الأصلي وأطلس Adam في
    Runtime وTV ومسار العرض والفلترة والتوقيت داخل المحرك.
  - يظهر على Adam حد فاتح/ملون ملتصق بالـsilhouette؛ الاحتمال الأقوى بقايا
    matte RGB في بكسلات الحد تحولت إلى hard alpha ثم أبرزتها الفلترة الثنائية.
  - المحاكاة وحلقة الرسم تستهدفان `60Hz`، لكن لا يوجد عداد FPS فعلي أو P90/P99
    ولا طلب صريح لتردد Surface؛ لذلك لا يمكن اعتبار الهدف قياسًا فعليًا للجهاز.
  - حركة Sprites منفصلة عن FPS الشاشة: الأبطال `8–18fps` حسب الحركة، وأعداء
    Stage 1: idle `8`، walk `10–15`، attack `12–15`، hurt `15`، knockdown `10`.
  - وُضعت خطة تبدأ بقياس Baseline، ثم إصلاح matte على Adam وعدو واحد تجريبيًا،
    ثم بوابة edge contamination، وبعد القبول تعميمها على أبطال وأعداء Stage 1.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md` فقط.
- الاختبارات:
  - مراجعة `GameView.run()` و`SpriteAnimator` وPaint/atlas loading — PASS تشخيصيًا.
  - فحص بصري للقطة وأطلس Adam Runtime/TV — كشف halo فاتح على الحدود.
  - قياس FPS فعلي على جهاز — SKIPPED؛ لا يوجد جهاز ADB متصل ولا telemetry حالي.
- Release: لا يوجد؛ طلب تخطيط فقط.
- ملاحظات/مخاطر: زيادة الدقة أو sharpen قبل إزالة الـmatte ستجعل الهالة أوضح.
  يجب فصل FPS الرسم الفعلي عن FPS حركة الـsprite وعدم تحويل كل حركة إلى 60 صورة.
- التالي: بعد موافقة المستخدم، تنفيذ عداد القياس وبوابة الحواف وPilot Adam + Grunt
  دون توليد صور جديدة، ثم عرض مقارنة قبل/بعد قبل التعميم.

### 2026-08-25-78 — إعادة بناء أعداء Stage 1 وفق بوابة UHD صارمة

- المنفذ: Codex + ImageGen
- طلب المستخدم: وضع قوانين صارمة وإعادة بناء جميع أعداء المرحلة الأولى بجودة
  تضاهي `Striker` و`Shield Guard`.
- الحالة: مكتمل؛ منشور في `v0.47.0-alpha`.
- نقطة البداية: `v0.46.1-alpha` / commit
  `cc156f9605422a50c6bd52e5108e21448b4057f6`.
- ما تم:
  - أُعيد إنتاج الأعداء الخمسة عبر ImageGen المدمج فقط، بلا Higgsfield أو فيديو؛
    لكل عدو Model Sheet وثلاث أوراق `6×2` للحركة والهجوم والضرر/السقوط.
  - رُفضت ورقة Skater أولى بسبب جزء منفصل، ثم رفضت بوابة القص أوراق هجوم
    `Grunt` و`Skater` و`Keeper-7` وأُعيدت بهوامش أكبر بدل تخفيف القانون.
  - أصلحت أداة البناء لتبحث عن الفواصل البيضاء الحقيقية تكيفيًا بدل تقسيم رياضي
    قد يقطع قبضة أو درعًا، وأزيل القص المسبق الذي كان يأكل حواف الإطار.
  - فُرض Model Sheet ومصدر `1536×900` على الأقل وخلية `250×450`، Alpha ثنائي،
    هوامش آمنة، 36 إطارًا حقيقيًا، وثبات الوقوف/المشي ضمن 5%.
  - بُنيت Base `1344×1152` وRuntime `2016×1728` وTV `1176×1008` مباشرة من
    المصدر المقبول لكل عدو، مع تحديث Manifest وfallbacks.
  - فُحصت contact sheets للأعداء الخمسة بصريًا بعد بناء الأطالس؛ الأجسام
    والمعدات كاملة ولا توجد أجزاء ملتفة بين الخلايا.
- الملفات المعدلة:
  - `assets/imagegen/android/enemies/quality-v2/` — 20 مصدرًا معتمدًا.
  - `android/tools/build_strict_enemy_atlas.py`.
  - `android/tools/test_enemy_visual_quality_contract.py`.
  - `android/docs/ENEMY_VISUAL_QUALITY_STANDARD_AR.md`.
  - `android/app/src/main/assets/enemies/` و`runtime/enemies/` و`tv/enemies/`
    للأنواع الخمسة، و`asset_manifest.json`.
  - `android/app/build.gradle` — `versionCode 58` / `0.47.0-alpha`.
- الاختبارات:
  - `python3 android/tools/test_enemy_visual_quality_contract.py` — PASS
    (5 أعداء × 36 إطارًا × 3 طبقات).
  - `validate_animation_atlases.py --allow-nonclustered` — PASS، 26/26 أطلسًا.
  - `validate_assets.py` — PASS، 181 ملفًا في Manifest.
  - عقود Stage combat وRuntime smoothness وTV encounter memory — PASS؛ ميزانية
    الأطالس المتحركة `71.20 MiB` وحد أقصى أربعة أطالس في المواجهة.
  - `test_customer_release.sh customers/family-current` — PASS للبناء الموقّع،
    R8/Lint، التحكم، الأصول، الذاكرة، الأسلحة والقصة؛ Runtime على محاكي/جهاز
    SKIPPED لعدم اتصال ADB.
  - الفحص العام من دون `--allow-nonclustered` — FAIL قديم وغير متعلق بأعداء
    Stage 1 لأن `heroes/parent_anim.png` لا يطابق عقد 2px الصارم.
- Release: `v0.47.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.47.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.47.0-alpha/family-force-family-current.apk
- SHA-256: `48ab52bdbca670c93a89c704fe41e71b30909cdc166d3ca680123c5c40249f6e`.
- commit: `a558db823fdb15dcabdd46609b1b3b2177067e56`.
- ملاحظات/مخاطر: القياس العالي هنا لمصدر الإنتاج؛ لم تُحمّل اللعبة Texture 4K
  كاملة على Xiaomi. يبقى القبول البصري الحقيقي مطلوبًا على Xiaomi Stick وShield.
- التالي: اختبار Stage 1 بالحجم الفعلي على الجهازين، ثم تعميم البوابة على Stage 2
  عدوًا واحدًا في كل مرة فقط بعد موافقة المستخدم.

### 2026-08-25-77 — تشخيص تفاوت جودة الأعداء وتحديد بوابة UHD

- المنفذ: Codex
- طلب المستخدم: دراسة سبب تفوق `Striker` و`Guard` بصريًا على بقية الشخصيات
  الجديدة، واقتراح إعادة توليد UHD وعدم إدخال ما دون المعيار إلى اللعبة.
- الحالة: مكتمل — تشخيص فقط دون استبدال أصول.
- نقطة البداية: `v0.46.1-alpha` / commit
  `cc156f9605422a50c6bd52e5108e21448b4057f6`.
- ما تم:
  - قورنت مصادر وmasters وأطالس Base/Runtime/TV/UHD لكل خط الأعداء، مع فحص
    contact sheets وأبعاد الخلايا وحجم العرض الحقيقي ومسار الاختيار في المحرك.
  - ثبت أن `Striker` و`Shield Guard` مبنيان من ثلاث أوراق حركة مخصصة عبر
    builders منفصلين، مع معالجة يدوية للخلايا المعيبة وSafe Remap وهوامش ثابتة
    ونسخة Runtime كثيفة مبنية مباشرة من المصدر.
  - بقية `campaign-v1` مبنية غالبًا من ورقة `6×6` واحدة بمولد عام يحتفظ بأكبر
    component فقط؛ هذا قد يحذف سلاحًا منفصلًا أو يقبل نصف شخصية طالما الخلية
    غير فارغة. ظهر ذلك بوضوح في `Cargo Loader` و`Furnace Brawler`، كما ظهرت
    وضعيات مقصوصة في `Market Enforcer` و`Keeper-7` و`Signal Warden` و
    `Tidebreaker`.
  - `Shield Guard` لا يملك ملف UHD حاليًا وStriker UHD حجمه `1920×2304` فقط؛
    لذلك تفوقهما لا ينتج من وسم UHD بل من وضوح silhouette، كتل ألوان كبيرة،
    خطوط مقروءة، ثبات الهوية، وتنظيف كل إطار على حدة.
  - الأعداء الأحدث يستخدمون micro-detail وألوانًا أكثر عند ارتفاع عرض فعلي
    يقارب `78–141px` للجسم؛ فتتحول الخطوط الرفيعة إلى noise/blur بعد التصغير.
  - لا توجد Runtime atlases للأنواع من Stage 2 المتأخرة حتى Stage 5، لذلك تهبط
    المواجهة كلها إلى Base/TV عند وجود أحدها. كما تطبق مراحل 2–4 hue filters
    إضافية تزيد تفاوت اللون ولا تعالج ضعف المصدر.
  - اعتماد مبدأ البوابة المقترحة: مصدر UHD مولد أصلًا لا upscale، كل وضعية
    كاملة ومستقلة، ثم اشتقاق Runtime/TV مرة واحدة واختبارها بالحجم الفعلي؛
    أبعاد الملف وحدها ليست معيار قبول.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md` فقط؛ لم تتغير أصول اللعبة.
- الاختبارات:
  - فحص أبعاد جميع مصادر وأطالس الأعداء — PASS تشخيصيًا؛ كشف غياب Runtime/UHD.
  - مراجعة contact sheets لـ20 نوعًا — FAIL بصري متوقع للخط غير المعتمد؛
    `Striker` و`Shield Guard` فقط مرجع قبول حاليًا.
  - تحليل حجم الجسم النهائي والكثافة اللونية/الحواف — كشف أن بعض الرسومات تحمل
    micro-detail أعلى بكثير من قدرة حجم العرض الفعلي.
  - Build/Runtime — SKIPPED؛ لم يُغيّر الكود أو الأصول.
- Release: لا يوجد؛ الدراسة لا تغيّر APK.
- ملاحظات/مخاطر: رفع الأطالس المشحونة نفسها إلى 4K سيزيد الذاكرة ولا يعيد
  التفاصيل المفقودة. يجب أن تكون UHD في مصدر الإنتاج، لا Texture محملة كاملة
  داخل APK على Xiaomi Stick.
- التالي: حجر جميع الأعداء غير المعتمدين عن الإصدارات الجديدة، ثم إعادة إنتاج
  عدو Stage 1 واحد فقط كمثال UHD واختباره قبل متابعة النوع التالي.

### 2026-08-25-76 — تنفيذ بوابة إنتاج وفحص جميع الموارد

- المنفذ: Codex + Impeccable
- طلب المستخدم: تنفيذ خطة تحسينات الإنتاج والفحص لكل الموارد.
- الحالة: مكتمل
- نقطة البداية: خطة الإدخال 74 وخزنة الموارد بعد تقرير السلامة وتثبيت المعاينة.
- المنجز:
  - إضافة سجل عقود موحد ومحرك QA بملفات تعريف للصور والأطالس والخلفيات والواجهة
    والمؤثرات والصوت والموسيقى والفيديو وJSON والملفات العامة، مع فك ترميز فعلي
    وقياسات alpha/crop/duplicate frames وWAV peak/RMS و`ffprobe` عند توفره.
  - رفع الفهرس إلى 101 سجل و181 ملفًا وتغطية كل Manifest، مع بطاقات للملفات
    اليتيمة وربط نسخ SOURCE/RUNTIME/TV/UHD وحالة إنتاج لكل سجل.
  - جعل الاستيراد حجرًا فعليًا: كتابة `.part`، فحص المحتوى، رفض الامتداد الزائف،
    ثم النقل فقط بعد النجاح؛ مع order ID والحقوق ومسار هدف مقيّد حسب العائلة.
  - فرض انتقالات validate/request changes/approve/revoke؛ الاعتماد يتطلب حقوقًا
    مصرحًا بها وفحصًا ناجحًا وبصمة مطابقة، ولا يمكن تجاوزه عبر تعديل metadata.
  - إضافة Staging allowlist ومعاينة dry-run تعرض المصدر والوجهة وSHA-256 دون
    كتابة، مع مسار كتابة منفصل داخل `asset-vault/staging/` عند طلبه من API فقط.
  - تطوير واجهة بوابة الإنتاج وتقرير التغطية (مفحوص/متخطى/غير منطبق)، وتوثيق
    المكوّن في نظام Impeccable مع تثبيت شاشة المعاينة ونظام RTL المتجاوب.
- الملفات:
  - `asset-vault/qa_engine.py`, `asset-vault/data/contracts.json`.
  - `asset-vault/catalog.py`, `asset-vault/audit.py`, `asset-vault/server.py`.
  - `asset-vault/index.html`, `asset-vault/app.js`, `asset-vault/styles.css`.
  - `asset-vault/tests/test_qa_engine.py`, `test_server.py`, `test_catalog.py`,
    `test_frontend.py`, و`asset-vault/.gitignore`.
  - `asset-vault/README_AR.md`, `asset-vault/DESIGN.md`,
    `asset-vault/.impeccable/design.json`.
  - لقطات QA: `reports/production-gate-desktop.png`,
    `production-gate-mobile.png`, `production-deep-report.png`.
- النتائج:
  - الفحص السريع الحي: 101 سجل/181 ملفًا، 0 أخطاء و0 تحذيرات، 180 مفحوصًا
    و1 غير منطبق، في نحو 663ms.
  - الفحص العميق: 0 أخطاء و26 تحذيرًا غير حاجب (24 soft-alpha ومجموعتا gutter
    ضيقتان في TV)، 180 مفحوصًا و1 غير منطبق؛ أول تشغيل نحو 5.8s ثم 111ms من cache.
  - `python3 -m unittest discover -s tests -v`: نجاح 29/29.
  - `node --check app.js`, `python3 -m json.tool .impeccable/design.json`,
    و`git diff --check`: نجاح.
  - مدققا Android: نجاح 181 ملف Manifest، ونجاح 26/26 أطلسًا مع hero scale.
  - فحص Selenium لسطح المكتب والهاتف والتقرير العميق: سليم، بلا أخطاء console
    مؤثرة وبلا تداخل أو تغيّر في هندسة المعاينة.
- Release: لا APK ولا GitHub Release؛ التغيير محصور في أداة الإنتاج ولا توجد
  حزمة موارد محددة للنشر.
- المخاطر المتبقية:
  - واجهة المستخدم تعرض Staging dry-run فقط عمدًا؛ لا Publish/rollback إلى Runtime.
  - تحليل الفيديو المتقدم (black/freeze/contact sheet) وLUFS/loop للموسيقى مرحلة
    لاحقة؛ الموجود الآن فك ترميز/metadata وقياسات WAV الأساسية.
  - التحذيرات الـ26 تحتاج مراجعة بصرية بشرية، لكنها ليست أخطاء حاجبة.
- التالي الموصى به: مراجعة التحذيرات الـ26، ثم إضافة LUFS/loop وتحليل إطارات
  الفيديو قبل فتح نشر فعلي لحزمة موارد محددة.

### 2026-08-25-75 — تحديد المسار التالي بعد إصلاح التحديث

- المنفذ: Codex
- طلب المستخدم: ما التالي؟
- الحالة: مكتمل — توصية وخطة دون تعديل APK.
- نقطة البداية: `v0.46.1-alpha` / commit
  `cc156f9605422a50c6bd52e5108e21448b4057f6`.
- ما تم:
  - اعتماد اختبار التحديث على TV حقيقي كبوابة قصيرة، ثم إصدار Stability RC قبل
    إدخال محتوى أو أطالس جديدة.
  - ترتيب التطوير المرئي التالي: تحسين انتقالات بداية/نهاية المرحلة والنتائج
    والـScore، ثم Pilot رسومات Stage 2 وفق معيار الأطالس الصارم شخصيةً بعد أخرى.
  - إبقاء إعادة كتابة القصة والحوارات دفعة مستقلة حتى لا تختلط بأعمال الاستقرار.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md` فقط.
- الاختبارات: Runtime — SKIPPED؛ هذا طلب تخطيط فقط.
- Release: لا يوجد؛ آخر نسخة تبقى `v0.46.1-alpha`.
- ملاحظات/مخاطر: إدخال أطالس متعددة قبل بوابة RC سيصعّب عزل أي تقطيع أو crash.
- التالي: اعتماد مرحلة Stability RC، ثم تنفيذ حزمة Arcade Flow والنتائج.

### 2026-08-24-74 — تخطيط تحسينات الإنتاج والفحص التالية

- المنفذ: Codex + Impeccable
- طلب المستخدم: تحديد الخطوة التالية واقتراح تحسينات مفيدة فعلًا للإنتاج والفحص.
- قرار المستخدم: تشمل الخطة كل الموارد، ويريد خطة الآن دون تنفيذ.
- الحالة: مكتمل — خطة فقط دون تنفيذ.
- نقطة البداية: خزنة الموارد بعد تقرير السلامة وتثبيت قياسات المعاينة.
- ما تم:
  - تحليل الفجوة بين خزنة العرض الحالية وخط إنتاج محكوم لكل الموارد.
  - اعتماد مسار: استيراد وحجر، فحص سريع/عميق/Release، مراجعة بشرية، اعتماد مرتبط
    بالبصمة، توليد في Staging، Release Candidate، نشر وتراجع.
  - شملت الخطة الأطالس والصور والخلفيات وUI/FX والصوت والفيديو وStory/JSON
    وموارد Android branding، مع عقد صريح لكل نوع ونسخة.
  - اعتماد محرك QA مشترك يعيد استخدام `validate_assets.py` و
    `validate_animation_atlases.py` بدل نسخ القواعد داخل الخزنة.
  - ترتيب سبع دفعات: Inventory V2، Quarantine، QA المرئي، Audio/Video، Review &
    Approval، Staged Generation، ثم Publish & Rollback/Hardening.
  - تثبيت قاعدة الأمان: لا إصلاح تلقائي ولا كتابة داخل Runtime؛ الاقتراح أولًا،
    وكل تحويل في Staging وبموافقة صريحة.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`.
- الاختبارات: Runtime — SKIPPED؛ طلب تخطيطي فقط. جرى فحص الأدوات والعقود الحالية
  قراءةً لتأسيس الخطة، دون تشغيل أو تعديل كود.
- Release: لا يوجد.
- ملاحظات/مخاطر: يجب تشغيل المدققات الجديدة في Shadow Mode أولًا لمنع إنذارات
  كاذبة، وعدم اعتبار `skipped` أو غياب ffmpeg نجاحًا.
- التالي: عند طلب التنفيذ، تبدأ الدفعة الأولى بـInventory V2 + Quarantine +
  المحرك المشترك، دون نشر أو تعديل أصول اللعبة.

### 2026-08-24-73 — إصلاح فشل Game Update في الإصدارات الأخيرة

- المنفذ: Codex
- طلب المستخدم: زر `GAME UPDATE` يعرض `FAILED` في آخر إصدارين أو ثلاثة.
- الحالة: مكتمل.
- نقطة البداية: `v0.46.0-alpha` / commit
  `1df26ecb2d70cf8943e3a390085d779a23de9748`.
- ما تم:
  - فُحص مسار GitHub API واختيار أصل APK والتحقق من SHA والتوقيع والمثبت.
  - ثبت أن أحدث ثلاثة Releases احتوت APK باسم الإصدار فقط، بينما التطبيق يبحث
    عن الاسم الثابت الخاص بالعميل `family-force-family-current.apk`.
  - أضيف الاسم الثابت إلى `v0.46.0-alpha` فورًا، فأصبحت النسخ القديمة تجد الأصل
    الصحيح دون الحاجة إلى تغيير التطبيق أولًا.
  - أصبح `UpdateManager` يفضّل الاسم الثابت، ثم يقبل اسم
    `Family-Force-Neon-Streets-vX.apk` كـfallback محصور؛ ويبقى رفض أي APK آخر.
  - بقيت حماية SHA-256 والحجم واسم الحزمة وارتفاع versionCode وتطابق شهادة
    التوقيع والـcertificate pin إلزامية قبل فتح مثبت Android.
- الملفات المعدلة:
  - `android/app/src/main/java/com/familyforce/neonstreets/UpdateManager.java`.
  - `android/tools/test_in_app_update_contract.py`.
  - `android/app/build.gradle` (`versionCode 57` / `0.46.1-alpha`).
  - `PROJECT_HISTORY_AR.md`.
- الاختبارات:
  - `test_in_app_update_contract.py` — PASS (19/19).
  - `compileDebugJavaWithJavac` — PASS.
  - `test_customer_release.sh customers/family-current` — PASS كامل؛ Release/R8/
    Lint/توقيع وفحوص الأصول والتحكم والذاكرة وRuntime QA.
  - GitHub Latest API — PASS؛ الاسمان الثابت والمرتبط بالإصدار موجودان بنفس SHA.
  - Runtime فعلي على Android Emulator من `v0.46.0`: PASS؛ ظهر `DOWNLOADING` ثم
    انتقل إلى شاشة Android الرسمية `Install unknown apps` بعد اكتمال التحقق.
- Release: `v0.46.1-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.46.1-alpha
  - APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.46.1-alpha/family-force-family-current.apk
  - SHA-256: `369a6ea4391bc332bd93fb90d971e54579c8da81e3254b739e34219e61c81087`.
  - commit: `cc156f9605422a50c6bd52e5108e21448b4057f6`.
- ملاحظات/مخاطر: أول تثبيت من داخل التطبيق يحتاج تفعيل `Allow from this source`
  مرة واحدة حسب سياسة Android؛ لا يمكن للتطبيق تجاوز شاشة النظام أو التثبيت صامتًا.
- التالي: اختبار الزر على Xiaomi Stick أو Shield وتأكيد موافقة المثبت النظامي.

### 2026-08-24-72 — الخطوة التالية بعد الشريط الحواري

- المنفذ: Codex
- طلب المستخدم: ما التالي الآن؟
- الحالة: مكتمل — توصية وخطة دون تعديل APK.
- نقطة البداية: `v0.46.0-alpha` / commit
  `1df26ecb2d70cf8943e3a390085d779a23de9748`.
- ما تم:
  - ترتيب العمل التالي: قبول v0.46 على جهاز TV حقيقي، ثم Stability RC، ثم Pilot
    رسومات Stage 2، ثم تحسين محتوى القصة ودخول الرؤساء.
  - اعتماد عدم خلط إصلاحات الاستقرار مع إعادة الرسم في Release واحد.
- الملفات المعدلة: `PROJECT_HISTORY_AR.md` فقط.
- الاختبارات: Runtime — SKIPPED؛ هذا طلب تخطيط فقط.
- Release: لا يوجد؛ آخر نسخة تبقى `v0.46.0-alpha`.
- ملاحظات/مخاطر: لا يبدأ توسيع الرسومات قبل اعتماد الشريط الحواري على Xiaomi/Shield.
- التالي: تنفيذ Stability RC أولًا بعد اختبار الجهاز الحقيقي.

### 2026-08-24-71 — تحويل الحوارات إلى شريط سفلي

- المنفذ: Codex
- طلب المستخدم: الحوارات تكون جزءًا أسفل الشاشة وليست بملء الشاشة.
- الحالة: مكتمل
- نقطة البداية: `v0.45.1-alpha` / commit وظيفي
  `d9d52d084dc84de7cd8a126800363f10c3bb518b`.
- ما تم:
  - إعادة تصميم عرض STORY كشريط سينمائي سفلي يبقي المشهد والشخصيات ظاهرين.
  - الحفاظ على العربية/الإنجليزية وصورة المتحدث ومؤشر المتابعة والتحكم الكامل.
  - فحص حوارات المراحل والرؤساء على الهاتف وFold وAndroid TV.
  - استبدال البطاقة السابقة `560×238` بشريط سفلي `612×136` دون تعتيم الشاشة.
  - إظهار ساحة اللعب المجمدة خلف حوارات منتصف المرحلة والرئيس والخاتمة، مع بقاء
    STORY مالكًا للإدخال لمنع القتال العرضي أثناء الحوار.
  - عكس الصورة والنص تلقائيًا بين RTL العربية وLTR الإنجليزية.
- الملفات المعدلة:
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`.
  - `android/tools/test_story_content_contract.py`.
  - `android/app/build.gradle` (`versionCode 56` / `0.46.0-alpha`).
- الاختبارات:
  - جميع `android/tools/test_*.py` و`validate_assets.py` — PASS.
  - عقد القصة — PASS: 22 مشهدًا و67 سطرًا لكل لغة وشريط سفلي إلزامي.
  - لقطتا Runtime بالعربية والإنجليزية على 1280×720 — PASS دون قص أو تداخل.
  - `test_customer_release.sh` — PASS كامل: Release/R8/Lint/توقيع وphone/
    ultrawide/Fold/Android TV ومسار remote للاعبين.
- Release: `v0.46.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.46.0-alpha
  — APK مباشر:
  https://github.com/linkq8/family-force-neon-streets/releases/download/v0.46.0-alpha/Family-Force-Neon-Streets-v0.46.0-alpha.apk
  — SHA-256 `25ac72ef050e4572359b261001b6e3acf8f124d594687f906e37ec266d90fbb5`
  — commit `1df26ecb2d70cf8943e3a390085d779a23de9748`.
- ملاحظات/مخاطر: تسلسل القصة والقتال لم يتغير؛ التغيير تخطيط بصري فقط.
- التالي: اختبار حوار رئيس فعلي على Xiaomi Stick/Shield واعتماد ارتفاع الشريط.

### 2026-08-24-70 — تثبيت قياسات شاشة المعاينة

- المنفذ: Codex + Impeccable
- طلب المستخدم: تثبيت قياسات شاشة المعاينة حتى لا يتغير شكل المورد عند تغيير
  حجم النافذة أو الجهاز.
- الحالة: مكتمل
- نقطة البداية: خزنة الموارد مع تقرير السلامة في الإدخال 68.
- ما تم:
  - تثبيت معاينة الحركة على `720×340` منطقيًا ونسبة `36:17` في كل المقاسات.
  - تثبيت خريطة الأطلس على عقد `960×420` ونسبة `16:7`.
  - تثبيت عارض الصور والفيديو على `16:9` مع `object-fit: contain` لمنع القص والتمدد.
  - إزالة ارتفاعات `vh` وقيود الهاتف التي كانت تغيّر شكل Canvas مستقلًا عن عرضه.
  - إضافة اختبارات عقد CSS تمنع إعادة إدخال ارتفاعات تشوّه المعاينة.
  - توثيق عقد القياسات في نظام التصميم واجتياز مراجعة Impeccable بحكم `SHIP`.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`.
  - `asset-vault/styles.css`.
  - `asset-vault/tests/test_frontend.py`.
  - `asset-vault/README_AR.md`.
  - `asset-vault/DESIGN.md`.
  - `asset-vault/.impeccable/design.json`.
  - `asset-vault/reports/preview-fixed-desktop.png`.
  - `asset-vault/reports/preview-fixed-tablet.png`.
  - `asset-vault/reports/preview-fixed-mobile.png`.
  - `asset-vault/reports/preview-fixed-mobile-stage.png`.
- الاختبارات:
  - `python3 -m unittest discover -s tests -v` — PASS، 19/19.
  - `node --check app.js` — PASS.
  - `git diff --check` — PASS.
  - Selenium عند 1600×1000 و1000×800 و500×900 — PASS؛ نسبة الحركة ضمن
    `±0.02` من `36:17` ونسبة الأطلس ضمن `±0.02` من `16:7`.
  - الفحص البصري desktop/tablet/mobile — PASS بلا قص أو تمدد.
  - Impeccable detector — advisory قديمة فقط.
  - Impeccable finish review — `SHIP`.
- Release: لا يوجد؛ تعديل أداة مستقلة عن APK.
- ملاحظات/مخاطر: على الشاشات الضيقة تصغر المعاينة ككتلة واحدة، لكن شكل المورد
  ونسبته وموضعه داخل Canvas تبقى ثابتة. لا تغيير في APK أو أصول Android.
- التالي: استخدام المعاينة أثناء ضبط الأطالس، واعتماد العقد نفسه لأي عارض جديد.

### 2026-08-24-69 — خطة الاستقرار والإتقان البصري التالية

- المنفذ: Codex
- طلب المستخدم: ما التالي؟ أريد استقرارًا أكثر ورسومات أتقن.
- الحالة: مكتمل — خطة دون تنفيذ في هذا الطلب.
- نقطة البداية: `v0.45.1-alpha` بعد نجاح جولة الفحص في الإدخال 67.
- ما تم:
  - اعتماد Sprint استقرار مستقل قبل أي توسيع فني، مع Soak واختبارات أجهزة ضعيفة
    وحدود أداء وذاكرة ورصد تقطيع كل منطقة.
  - اعتماد Art Bible وعقود عرض موحدة، ثم تحسين مورد واحد في كل مرة وقبوله داخل
    اللعبة قبل الانتقال لغيره، بدل إعادة رسم جماعية.
  - ترتيب التطوير: Stability RC، ثم الشخصيات الرئيسية، ثم أعداء المراحل بالتتابع،
    ثم الخلفيات وUI/VFX مع اختبارات مقارنة بصرية ثابتة.
- الملفات المعدلة: `PROJECT_HISTORY_AR.md` فقط.
- الاختبارات: Runtime — SKIPPED؛ هذا طلب تخطيط ولم يتغير APK.
- Release: لا يوجد؛ توثيق خطة فقط.
- ملاحظات/مخاطر: زيادة دقة المصدر إلى 4K وحدها لا تحسن العرض؛ المطلوب هو ثبات
  الحجم والمحور والـoutline والتصفية ونسبة الخلية عند دقة العرض الفعلية.
- التالي: تنفيذ Sprint الاستقرار أولًا، ثم تقرير قبول قبل بدء Sprint الرسومات.

### 2026-08-24-68 — تقرير فحص الموارد والأخطاء

- المنفذ: Codex + Impeccable
- طلب المستخدم: إضافة ميزة Report للفحص والأخطاء إلى خزنة الموارد.
- الحالة: مكتمل
- نقطة البداية: خزنة الموارد المطورة في الإدخال 65، مع الحفاظ على تغييرات اللعبة
  والأعداء غير المنشورة خارج `asset-vault/`.
- ما تم:
  - إضافة محرك تدقيق للقراءة فقط يفحص وجود الملفات، الحجم، SHA-256 الاختياري،
    صلاحية شبكة الأطلس، توفر نسخة TV، metadata والعلاقات.
  - إضافة API للفحص السريع والعميق مع نتيجة موحدة ودرجات `error/warning/info`.
  - إضافة درج تقرير RTL بملخص، فلاتر، حالات تحميل/خطأ/فراغ، إعادة فحص وتصدير JSON.
  - ربط كل مشكلة بالمورد المتأثر لفتحه مباشرة من التقرير.
  - إضافة دلالات dialog وعزل الخلفية وfocus trap دائري واستعادة التركيز.
  - توثيق مكونات التقرير وتوكناته في نظام تصميم Asset Vault المحلي.
  - اجتازت مراجعة Impeccable المستقلة بحكم `SHIP`.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`.
  - `asset-vault/audit.py`.
  - `asset-vault/server.py`.
  - `asset-vault/index.html`.
  - `asset-vault/styles.css`.
  - `asset-vault/app.js`.
  - `asset-vault/tests/test_audit.py`.
  - `asset-vault/tests/test_server.py`.
  - `asset-vault/README_AR.md`.
  - `asset-vault/DESIGN.md`.
  - `asset-vault/.impeccable/design.json`.
  - `asset-vault/reports/report-desktop.png`.
  - `asset-vault/reports/report-mobile.png`.
- الاختبارات:
  - `python3 -m unittest discover -s tests -v` — PASS، 17/17.
  - `node --check app.js` — PASS.
  - `git diff --check` — PASS.
  - API report سريع — PASS: 84 موردًا و153 ملفًا، 24.3ms، 0 أخطاء/تحذيرات.
  - API report عميق SHA-256 — PASS: 167.6ms، 0 أخطاء/تحذيرات.
  - Selenium desktop/mobile — PASS للفتح والتحميل والنتيجة السليمة والعزل.
  - Selenium keyboard — PASS: Tab وShift+Tab محصوران داخل الحوار.
  - Impeccable detector — advisory توثيقية فقط، ووثقت التوكنات الجديدة.
  - Impeccable finish review — `SHIP`.
- Release: لا يوجد؛ الأداة مستقلة ولا تغيّر APK.
- ملاحظات/مخاطر: الفحص لا يصلح الملفات تلقائيًا عمدًا؛ يعرض الإجراء المقترح ويترك
  قرار التعديل للمنتج. لا يوجد تغيير في APK أو Release.
- التالي: تشغيل التقرير قبل كل حزمة أصول أو Release، ثم معالجة أي مورد يظهر
  بالأحمر قبل اعتماده.

### 2026-08-24-67 — جولة فحص v0.45.1

- المنفذ: Codex
- طلب المستخدم: "جولة فحص" للنسخة الحالية بعد إصلاح الرسومات.
- الحالة: مكتمل
- نقطة البداية: `v0.45.1-alpha` / commit وظيفي
  `d9d52d084dc84de7cd8a126800363f10c3bb518b`.
- ما تم:
  - فحص آلي لكل أطالس وإطارات اللعبة، مع تدقيق خاص للأنواع الخمسة في Stage 1.
  - تشغيل عقود الأصول والذاكرة والتحكم والبناء والإصدار الموقّع.
  - تشغيل المسار الكامل على Android TV Emulator وفحص FATAL/ANR/OOM واللقطات.
  - نجح فحص 26/26 أطلسًا؛ لا توجد خلايا فارغة أو حركات ثابتة.
  - كل الإطارات الـ36 للأنواع الخمسة موجودة في Base/Runtime/TV، وأقل gutter
    هو 8px Base و12px Runtime و7px TV وفق العقود.
  - نجح الفحص البصري داخل Stage 1 على 1920×1080 للموجتين؛ ظهر Grunt وSkater
    وLantern Courier وMarket Enforcer وKeeper-7 كاملين وواضحين.
  - ظهور Keeper جزئيًا في لقطة الدخول كان دخوله الطبيعي من حافة الكاميرا؛ ظهر
    كاملًا بعد تقدمه ولم يكن قصًا داخل الأطلس.
  - لم يظهر خلل مؤكد يستدعي تعديل الكود أو الرسومات أو Release جديدًا.
- الملفات المعدلة: `PROJECT_HISTORY_AR.md` فقط (توثيق الجولة).
- الاختبارات:
  - `validate_assets.py` — PASS: 82 PNG و181 ملف Manifest.
  - `validate_animation_atlases.py --allow-nonclustered` — PASS: 26/26؛ هذا
    عقد الدقة الحديثة نفسه المستخدم في Release.
  - جميع `android/tools/test_*.py` و`:app:assembleDebug` — PASS.
  - `test_customer_release.sh` — PASS كامل: Build/Release/R8/Lint/توقيع، phone،
    ultrawide، Fold، Android TV، ومسار remote للاعبين؛ ملفات failure كلها 0 بايت.
  - PSS: هاتف 48.1MB، ultrawide 47.9MB، Fold 50.4MB، Android TV 56.8MB،
    ومسار TV ثنائي اللاعبين 89.6MB.
  - `test_full_stage_runtime.sh` — PASS: المناطق 1–14 حتى `STAGE_COMPLETE` بلا
    FATAL/ANR/OOM.
- Release: لا يوجد؛ `v0.45.1-alpha` بقيت النسخة المنشورة لأن الجولة لم تتطلب تعديلًا.
- ملاحظات/مخاطر: الفحص الآلي والمحاكي نجحا؛ يبقى القبول البصري البشري على
  Xiaomi Stick/Shield مطلوبًا قبل تعميم خط Stage 1 على المرحلة التالية.
- التالي: اختبار المستخدم للمرحلة الأولى على جهاز حقيقي ثم قرار القبول.

### 2026-08-24-66 — فشل بصري في Pilot أعداء المرحلة الأولى

- المنفذ: Codex
- طلب المستخدم: النسخة الجديدة تحتوي رسومات لا تظهر نهائيًا ورسومات غير واضحة.
- الحالة: مكتمل
- نقطة البداية: `v0.45.0-alpha` / commit وظيفي
  `608592b4dbc13850b47cff1046d2f3558ce36064`.
- ما تم:
  - ثبت أن الأطالس لا تحتوي خلايا فارغة، لكن الأنواع الجديدة لم تكن تملك صورة
    احتياطية؛ أثناء فك الأطلس غير المتزامن على TV كان يمكن أن يظهر العدو بلا رسم.
  - أضيف تحميل fallback صغير لكل Enemy Archetype متاح بدل ستة أنواع قديمة فقط.
  - استبدلت نسبة الرسم الثابتة `160/192` بنسبة خلية الأطلس الحقيقية لمنع ضغط
    الإطارات العريضة وتشويه الهجمات.
  - أعيد بناء Grunt وSkater وLantern Courier وMarket Enforcer وKeeper-7 من
    مصادرهم الحالية فقط، دون توليد جديد أو فيديو، بخلايا عريضة: Base
    `224×192` وRuntime `336×288` وTV `196×168`.
  - أصبحت طبقة TV تبنى مباشرة من المصدر بدل تصغير أطلس كامل، مع حد أدنى لحجم
    كل Action/Hurt/Knockdown، وهوامش آمنة، وصورة fallback `512×512` لكل نوع.
  - وسعت بوابات الإصدار لتمنع الإطار الفارغ، والتصغير المفرط في كل الصفوف،
    والمقاسات القديمة، والكتابة فوق أطالس Stage 1 من مولد TV العام.
- الملفات المعدلة:
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/app/src/main/java/com/familyforce/neonstreets/SpriteAnimator.java`
  - `android/tools/build_strict_enemy_atlas.py`
  - `android/tools/generate_tv_optimized_assets.py`
  - `android/tools/validate_assets.py`
  - `android/tools/validate_animation_atlases.py`
  - اختبارات عقود الأطالس/TV/الذاكرة، والأطالس والـfallback للأنواع الخمسة.
- الاختبارات:
  - `validate_assets.py` — PASS: 82 PNG و26 Atlas و181 ملف Manifest.
  - جميع `android/tools/test_*.py` — PASS.
  - `:app:assembleDebug` — PASS.
  - `test_full_stage_runtime.sh` — PASS: المناطق 1–14 حتى `STAGE_COMPLETE` دون
    FATAL/ANR/OOM؛ ذروة صور القتال المحسوبة `71.20 MiB`.
  - `test_customer_release.sh` — PASS للأصول و26/26 Atlas وBuild/Release/R8/Lint
    والتوقيع والتحقق؛ جزء المحاكي في الإعادة الأخيرة SKIPPED بعد انقطاع ADB،
    بينما اختبار المسار الكامل Debug كان قد نجح قبل ذلك على نفس المحاكي.
- Release: `v0.45.1-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.45.1-alpha
  — APK مباشر:
  https://github.com/linkq8/family-force-neon-streets/releases/download/v0.45.1-alpha/Family-Force-Neon-Streets-v0.45.1-alpha.apk
  — SHA-256 `ddc5a7f1d245846bb2da71ca6bbc6080a73f6824e4fd6e8dd2607812f03dfbb3`
  — commit `d9d52d084dc84de7cd8a126800363f10c3bb518b`.
- المخاطر: القبول البصري الحقيقي يبقى مطلوبًا على Xiaomi Stick/Shield؛ لا تطبق
  هذه المعايير على مراحل أخرى قبل مشاهدة كل حركات المرحلة الأولى على جهاز حقيقي.
- التالي: اختبار Stage 1 يدويًا ثم اعتماد أو رفض الرسم قبل الانتقال للمرحلة الثانية.

### 2026-08-24-65 — تطوير خزنة الموارد وتحسين الأداء والقوائم

- المنفذ: Codex + Impeccable
- طلب المستخدم: تطوير موقع وأداة خزنة الموارد وتحسين القوائم والأداء والتصميم
  باستخدام Impeccable، مع الاستفادة من تقييم الاستخدام السابق.
- الحالة: مكتمل
- نقطة البداية: تنفيذ `asset-vault` في الإدخال 63 وتوثيقه في الإدخال 64، مع
  الحفاظ على عمل جودة أعداء المرحلة الأولى الجاري في الإدخال 62.
- ما تم:
  - جعل البحث شاملًا لكل الفئات مع إبقاء مرشح الحالة وإظهار سياق نتيجة المورد.
  - إعادة تنظيم شريط الحركات بتمرير مرئي وأزرار اتجاه، وإضافة شرح اختلاف FPS.
  - إثراء الأبطال بقيم الحياة والسرعة والقوة والحركة الخاصة الفعلية من المحرك.
  - إضافة مقارنة حية بين نسخ الأطلس وتصدير JSON للإطارات والحركات والمحور.
  - إضافة سجل تغييرات لكل مورد وتسجيل الحقول قبل الحفظ وبعده والاستيراد الجديد.
  - تخزين صور الواجهة وكتالوج الخادم مؤقتًا، وبناء صورة الأطلس الأساسية مرة واحدة،
    وإيقاف التحديث عندما تكون الصفحة مخفية، وإضافة ETag وطلبات 304 للملفات.
  - إصلاح تداخل التنبيه السفلي، وتحسين تخطيط الهاتف، وحصر تركيز لوحة الاستيراد
    عبر `inert` وfocus trap وإعادة التركيز لزر الفتح عند الإغلاق.
  - اجتازت مراجعة Impeccable النهائية المستقلة بحكم `SHIP` بلا ملاحظات مادية.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`.
  - `asset-vault/index.html`.
  - `asset-vault/styles.css`.
  - `asset-vault/app.js`.
  - `asset-vault/catalog.py`.
  - `asset-vault/server.py`.
  - `asset-vault/tests/test_catalog.py`.
  - `asset-vault/tests/test_server.py`.
  - `asset-vault/data/history.json`.
  - `asset-vault/README_AR.md`.
  - `asset-vault/reports/v2-desktop-final.png`.
  - `asset-vault/reports/v2-mobile-final.png`.
  - `asset-vault/DESIGN.md` و`asset-vault/.impeccable/design.json`.
- الاختبارات:
  - `python3 -m unittest discover -s tests -v` داخل `asset-vault` — PASS، 14/14.
  - `node --check app.js` — PASS.
  - `git diff --check` — PASS.
  - فحص كتالوج حي على المنفذ 8766 — PASS: 84 موردًا، 150 ملفًا، 26 أطلسًا؛
    22.63ms لأول قراءة و7.33ms للقراءة الدافئة.
  - `HEAD` و`If-None-Match` لمورد أطلس — PASS: ETag و`max-age=300` واستجابة 304.
  - لقطتا Chrome Headless عند 1600×1000 و500×900 — PASS بصريًا.
  - Impeccable detector — تنبيهات توثيقية فقط للألوان/أحجام الخط؛ وثقت محليًا.
  - Impeccable finish review — `SHIP`.
- Release: لا يوجد؛ الأداة مستقلة ولا تغيّر APK.
- ملاحظات/مخاطر: لم تتغير أصول Android أو APK، وبقيت تعديلات الأعداء غير
  المنشورة كما هي. الفيديو يظهر كفئة فارغة إلى أن يستورد المستخدم أول ملف.
- التالي: استخدام الأداة في جلسة إنتاج فعلية، ثم إضافة تحرير pivot/hitbox إذا
  ثبتت الحاجة أثناء ضبط الأطالس.

### 2026-08-24-64 — توثيق النظام البصري لخزنة الموارد

- المنفذ: Codex — Impeccable documenter
- طلب المستخدم: "توثيق التصميم المشحون لخزنة الموارد في ملف محلي دائم، اعتمادًا
  على الواجهة المبنية ولقطات سطح المكتب والهاتف، دون تعديل DESIGN.md الجذري."
- الحالة: مكتمل
- نقطة البداية: `v0.44.0-alpha` / commit `be25e6d`، ضمن عمل خزنة الموارد الجاري
  في الإدخال 63 ومع الحفاظ على تعديلات جودة الأعداء غير المنشورة.
- ما تم:
  - استخراج لوحة الألوان والخطوط والمسافات والزوايا والمكونات من الواجهة المبنية.
  - تثبيت اتجاه «طاولة فحص الموارد الليلية» وعقد التدفق RTL ثلاثي الأجزاء.
  - توثيق الاستجابة عند `1220px` و`900px` و`620px`، والطباعة وتقليل الحركة.
  - إنشاء ملحق Impeccable محلي يتضمن الظلال والحركة ونقاط التوقف وسبعة نماذج
    مكونات مستقلة، دون نسخ الرموز المعيارية خارج frontmatter.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`.
  - `asset-vault/DESIGN.md`.
  - `asset-vault/.impeccable/design.json`.
- الاختبارات:
  - `ruby -ryaml ...` — PASS؛ frontmatter صالح والاسم المتوقع موجود.
  - فحص ترتيب الأقسام الثمانية canonical عبر Python — PASS.
  - `python3 -m json.tool asset-vault/.impeccable/design.json` — PASS.
  - `git diff --check -- asset-vault/DESIGN.md asset-vault/.impeccable/design.json PROJECT_HISTORY_AR.md` — PASS.
  - `git diff --quiet -- DESIGN.md` — PASS؛ ملف التصميم الجذري لم يتغير.
- Release: لا يوجد؛ تعديل توثيقي محلي ولا يغير APK.
- ملاحظات/مخاطر: التوثيق يصف الواجهة المشحونة الحالية؛ أي تغيير مرئي لاحق في
  `asset-vault/styles.css` يجب أن يحدّث الملف والملحق المحليين معًا. يبقى
  `DESIGN.md` في الجذر خاصًا بالدليل التجاري ودون تغيير.
- التالي: استخدام `asset-vault/DESIGN.md` كمرجع لأي شاشة أو مكوّن جديد في الخزنة.

### 2026-08-24-63 — تنفيذ مكتبة الموارد وعارض الأطالس

- المنفذ: Codex
- طلب المستخدم: تنفيذ خطة نظام حفظ وعرض الشخصيات والأدوات والخلفيات والموسيقى
  والفيديو، مع معلومات كل شخصية وأطلسها وعرض حركة الأطلس.
- الحالة: مكتمل — أداة محلية مستقلة، دون تعديل Runtime أو إصدار APK.
- نقطة البداية: `v0.44.0-alpha` / commit `be25e6d`، مع الحفاظ على تعديلات
  إصلاح جودة الأعداء غير المنشورة والمسجلة في الإدخال 62.
- ما تم:
  - إنشاء `Family Force Asset Vault` كأداة Web محلية عربية RTL تعمل بلا شبكة
    عبر خادم Python قياسي، ولا تكتب داخل أصول Android الحالية.
  - فهرسة الحالة الفعلية ديناميكيًا: 84 موردًا و150 ملفًا بحجم `149.3 MiB`،
    تشمل 4 أبطال و22 عدوًا و26 أطلسًا و4 أسلحة و4 أدوات و9 خلفيات و26 صوتًا
    وUI/FX/Props. قسم الفيديو جاهز والاستيراد الحالي صفر بصدق.
  - استخراج بيانات الأعداء القتالية مباشرة من `EnemyArchetype.java`، وتجميع
    طبقات `source/runtime/tv/uhd` والبورتريه والصور الساكنة في بطاقة الشخصية.
  - بناء عارض أطلس فعلي: تشغيل/إيقاف، إطار سابق/لاحق، سرعة، اختيار 11 حركة للبطل
    أو 6 للعدو، شبكة وخلية محددة، مقارنة النسخ، SHA-256 وحساب ذاكرة RGBA.
  - بناء معاينة حركة داخل مشهد `720×340` تدعم المشي والقفز والمقياس والسرعة،
    إلى جانب عارض صور وصوت وفيديو وسجل الملفات.
  - إضافة بحث وفلاتر وحفظ الاسم والوصف والدور والحالة والوسوم والملاحظات بكتابة
    JSON ذرية، واستيراد محدود النوع والحجم إلى `asset-vault/uploads/` كمسودة.
  - إضافة تصدير JSON، تنقل لوحة مفاتيح، حالات تحميل/خطأ/فراغ، تحذير تغييرات غير
    محفوظة، reduced-motion، طباعة، واستجابة من سطح المكتب إلى الهاتف.
  - فحص بصري مستقل من Impeccable انتهى بقرار `ship` ودون إصلاحات مادية مطلوبة.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`.
  - `asset-vault/index.html`, `styles.css`, `app.js`.
  - `asset-vault/catalog.py`, `server.py`, `run.command`.
  - `asset-vault/data/overrides.json`, `.gitignore`, `uploads/.gitkeep`.
  - `asset-vault/tests/test_catalog.py`, `tests/test_server.py`.
  - `asset-vault/README_AR.md`, `DESIGN.md`, `.impeccable/design.json`.
  - `asset-vault/reports/desktop-final.png`, `reports/mobile-final.png` ولقطتا الفحص الأولي.
- الاختبارات:
  - `python3 -m unittest discover -s asset-vault/tests -v` — PASS: `11/11`.
  - `node --check asset-vault/app.js` — PASS.
  - `python3 -m py_compile ...` — PASS.
  - `git diff --check` — PASS.
  - `/api/health` و`/api/catalog` — PASS؛ `84` موردًا و`26` أطلسًا.
  - Chrome Headless desktop `1600×1000` وmobile `500×900` — PASS بصريًا.
  - فحص DOM: الأطلس ظاهر، Canvas `960px`، الحفظ مفعّل ولا overflow في الجسم — PASS.
  - Impeccable detector — PASS وظيفيًا؛ advisories فقط لأن `DESIGN.md` الجذري
    خاص بـ`commercial-guide`، ثم وُثّق نظام مستقل داخل `asset-vault/DESIGN.md`.
  - Impeccable finish review — `ship`؛ لا findings مادية.
- Release: لا يوجد؛ الأداة مستقلة ولا تغيّر APK اللعبة.
- ملاحظات/مخاطر: العمل الجاري في الإدخال 62 يغير أطالس المرحلة الأولى؛ الفهرس
  يقرأ الحالة الفعلية عند كل تحديث ولا يكتب فوقها. الملفات المستوردة محلية وغير
  منشورة، ولا تدخل APK حتى يضاف لاحقًا مسار اعتماد/نشر صريح.
- التالي: تشغيل `asset-vault/run.command` ومراجعة الأطالس الحالية؛ المرحلة التالية
  الاختيارية هي إضافة Hit/Hurt boxes وإصدارات غير قابلة للتغيير ثم ناشر Android.

### 2026-08-24-62 — إصلاح جذري ومعيار صارم لوضوح الأعداء

- المنفذ: Codex
- طلب المستخدم: حل تفاوت وضوح الأعداء جذريًا ووضع معايير صارمة تمنع تكراره.
- تحديث النطاق بطلب المستخدم: عدم توليد جميع الشخصيات دفعة واحدة؛ يقتصر هذا
  الإصدار التجريبي على شخصيات المرحلة الأولى فقط: `Grunt` و`Skater`
  و`Lantern Courier` و`Market Enforcer` و`Keeper-7`، ولا تدخل أصول المراحل
  اللاحقة في البناء حتى يعتمد المستخدم نتيجة الاختبار.
- الحالة: مكتمل — Pilot المرحلة الأولى فقط.
- نقطة البداية: `v0.44.0-alpha` / commit `be25e6d`، مع إدخالي التخطيط والتشخيص
  رقم 60 و61 غير المنشورين بعد في سجل العمل المشترك.
- ما تم:
  - توحيد سياسة اختيار طبقة الدقة داخل المحرك ومنع خلط UHD/Runtime/TV في Encounter.
  - إنشاء عقد جودة قابل للقياس لدقة الخلية، امتلاء الجسم، ثبات المقياس، الهوامش،
    حدة الحواف، Alpha، وعدد الإطارات الحقيقية.
  - إنشاء ثلاث أوراق حركة ثابتة عالية الدقة لكل عدو في المرحلة الأولى، ثم بناء
    أطالس Base `960×1152` وRuntime `1440×1728` وTV `840×1008` مباشرة من المصدر.
  - إعادة بناء `Grunt` و`Skater` و`Lantern Courier` و`Market Enforcer`
    و`Keeper-7` فقط؛ لم تدخل أي إعادة رسم للمرحلة الثانية أو ما بعدها في الإصدار.
  - إصلاح إزالة الخلفية المتدرجة وتسرب المؤثرات بين الخلايا، وتثبيت مقياس الوقوف
    والمشي بمعزل عن اتساع وضعيات السقوط والهجوم.
  - جعل اختيار طبقة الأطلس على مستوى Encounter كاملًا؛ Runtime لا تستخدم إلا إذا
    توفرت لكل الأنواع، وإلا تهبط المواجهة كلها إلى TV أوBase دون خلط في الوضوح.
  - توثيق معيار منع إصدار قابل للقياس، وتحديث مولد TV ليشتق الخمسة من Runtime
    مباشرة مع Alpha ثنائي بدل التصغير المتكرر.
- الملفات الأساسية المعدلة:
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`.
  - أطالس `enemies/` و`runtime/enemies/` و`tv/enemies/` للأنواع الخمسة فقط.
  - `assets/imagegen/android/enemies/quality-v1/` للأنواع الخمسة فقط.
  - `android/tools/build_strict_enemy_atlas.py`.
  - `android/tools/test_enemy_visual_quality_contract.py`.
  - `android/tools/generate_tv_optimized_assets.py` وملفات التحقق المرتبطة.
  - `android/docs/ENEMY_VISUAL_QUALITY_STANDARD_AR.md`.
  - `android/app/build.gradle` و`asset_manifest.json`.
- الاختبارات:
  - جميع `android/tools/test_*.py` — PASS: 24 ملف اختبار، ومنها عقد الجودة
    `5 enemies × 36 frames × 3 tiers`.
  - `validate_assets.py` — PASS: 79 PNG و26 أطلسًا و178 ملف Manifest.
  - Gradle compile + `lintDebug` + `assembleDebug` — PASS.
  - Release/R8/`lintRelease` والتوقيع والتحقق من APK — PASS.
  - Android TV emulator full-stage — PASS: المناطق 1–14 حتى النتائج دون
    FATAL/ANR/OOM.
  - النسخة الموقعة بعد clean emulator boot — PASS: cold launch `676ms`، ثم
    مسار الريموت إلى القصة دون crash/ANR/OOM.
  - مراجعة لقطة المرحلة الأولى — PASS: Grunt واضح بحجم العرض الفعلي بلا قص.
- Release: `v0.45.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.45.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.45.0-alpha/Family-Force-Neon-Streets-v0.45.0-alpha.apk
- SHA-256: `88b52e4ed00cdfedd0bea36ba4f09c9d799b027ad666c40d9d5ccfdfd6ce05fb`.
- commit: `608592b4dbc13850b47cff1046d2f3558ce36064`.
- المخاطر: يلزم اعتماد بصري بشري على Xiaomi Stick وShield؛ المحاكي لا يحاكي
  معالجة شاشة التلفاز الفعلية. المراحل 2–5 ما زالت بأصول `v0.44.0` عمدًا.
- التالي: اختبار المرحلة الأولى على الجهازين واعتمادها، ثم إعادة بناء شخصيات
  المرحلة الثانية فقط بالخط نفسه إن كانت النتيجة مقبولة.

### 2026-08-24-61 — تشخيص تفاوت جودة الأعداء الجدد داخل اللعب

- المنفذ: Codex
- طلب المستخدم: تفسير سبب ظهور الأعداء الجدد بجودة سيئة داخل اللعبة مقارنة
  بـStriker وShield Guard رغم توحيد مقاس الأطالس.
- الحالة: مكتمل — تشخيص فقط، دون تعديل Runtime أو الأصول.
- نقطة البداية: `v0.44.0-alpha` / commit `be25e6d`.
- ما تم:
  - مقارنة أطالس الهاتف وTV ومسار التحميل والرسم داخل `GameView`.
  - اكتشاف تفاوت طبقة الدقة: على Shield يُحمّل Striker من UHD بخلايا `320×384`
    وGuard من Runtime بخلايا تقارب `248×297`، بينما لا توجد للأعداء الجدد نسخ
    UHD/Runtime فيهبطون إلى TV بخلايا `140×168`.
  - اكتشاف اختلاف مسار التأليف: Striker/Guard بُنيا من ثلاث أوراق حركة متخصصة
    ثم معالجة مخصصة، بينما جُمعت 36 وضعية لكل عدو جديد داخل Model Sheet واحدة؛
    أصبحت كل وضعية في المصدر صغيرة وفقدت تفاصيل قبل بناء الأطلس.
  - قياس تفاوت امتلاء الخلية؛ بعض الجدد مثل Furnace Brawler يملأ نحو 29% فقط
    من مساحة الخلية مقابل 48–55% تقريبًا للمراجع، فتقل تفاصيله المرئية أكثر.
  - تحديد أن LANCZOS عند إنتاج TV ثم `FILTER_BITMAP_FLAG` أثناء الرسم يسببان
    Resampling مزدوجًا للأطالس منخفضة المصدر، فيظهر blur لا يظهر بنفس الدرجة
    في أطلس Striker عالي الدقة.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md` فقط.
- الاختبارات:
  - تدقيق أبعاد طبقات `enemies/` و`runtime/enemies/` و`uhd/enemies/` و
    `tv/enemies/` — PASS وأثبت التفاوت.
  - قياس حدود Alpha وامتلاء الخلايا وتغير المقياس لكل 22 نوعًا — PASS كتدقيق.
  - Runtime — SKIPPED؛ لا يوجد تعديل وظيفي في هذا الطلب.
- Release: لا يوجد؛ تشخيص توثيقي فقط.
- ملاحظات/مخاطر: تكبير أطلس `960×1152` إلى 4K لن يصنع تفاصيل حقيقية. يلزم
  إعادة إنتاج مصادر الحركة بحجم أكبر، وإضافة طبقات Runtime متكافئة، وتصحيح ترتيب
  التحميل كي لا يجمع Encounter واحد بين UHD وTV.
- التالي: اعتماد Striker/Guard كخط إنتاج فعلي: ثلاث أوراق حركة لكل عدو، Runtime
  موحد، TV مشتق، ثم استبدال عدو واحد واختباره داخل مشهد اللعب قبل تعميم البقية.

### 2026-08-24-60 — تخطيط نظام مكتبة الموارد ومعاينة الأطالس

- المنفذ: Codex
- طلب المستخدم: تصميم خطة فقط لنظام يحفظ ويعرض الشخصيات والأدوات والخلفيات
  والموسيقى والفيديو، مع حفظ أطلس كل شخصية ومعلوماتها ودورها وكل ما يتعلق بها،
  وعرض الأطلس وتشغيل حركاته، واقتراح مزايا إضافية؛ دون تنفيذ.
- الحالة: مكتمل — خطة معمارية فقط، دون تنفيذ في اللعبة أو إنشاء نظام.
- نقطة البداية: `v0.44.0-alpha` / commit `be25e6d`.
- ما تم:
  - جرد فئات الأصول الحالية: 4 أبطال و22 نوع عدو و26 أطلسًا متحركًا، إضافة إلى
    الأدوات والأسلحة والخلفيات والصوت وUI/FX؛ لا توجد ملفات فيديو حاليًا.
  - تحديد قصور `asset_manifest.json` الحالي: يحفظ المسار والحجم وSHA-256 وأبعاد
    الصور، لكنه لا يحفظ معنى الأصل أو علاقاته أو تعريف حركات الأطلس.
  - تصميم `Family Force Asset Vault` كلوحة إنتاج مستقلة عن APK، بثلاث طبقات:
    المصادر الأصلية، كتالوج المعلومات والإصدارات، ثم المخرجات المشتقة للهاتف/TV/UHD.
  - تصميم نموذج بيانات للشخصيات والأطالس والحركات والأسلحة والأدوات والخلفيات
    والصوت والفيديو، مع علاقات الاستخدام بالمراحل والمواجهات والإصدارات.
  - اعتماد عارض أطلس يشغل الحركة داخل الخلية وداخل مشهد لعب، مع تحكم بالإطار
    والسرعة والتكرار، شبكة الأطلس، نقاط الارتكاز وHit/Hurt boxes والمقارنة بين النسخ.
  - وضع مراحل تنفيذ تبدأ بكتالوج قراءة فقط، ثم الاستيراد والإصدارات، ثم النشر
    الآمن إلى حزمة Android، وبعدها QA المتقدم والنسخ الاحتياطي/المزامنة الاختيارية.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات:
  - Runtime — SKIPPED؛ المطلوب تخطيط فقط.
  - مراجعة `asset_manifest.json` و`SpriteAnimator.java` وأداة معاينة GIF وبنية
    مجلدات الأصول — PASS كتدقيق تصميمي ساكن.
- Release: لا يوجد؛ تخطيط توثيقي فقط.
- ملاحظات/مخاطر: يجب فصل مكتبة الإنتاج الثقيلة عن APK، وعدم تضمين الصور الخام
  أو الفيديوهات المصدرية أو بيانات العملاء الحساسة داخل اللعبة النهائية. تحفظ
  الملفات خارج قاعدة البيانات، مع سجل JSON قابل للمراجعة وفهرس SQLite قابل لإعادة البناء.
- التالي: عند اعتماد الخطة، كتابة Asset Catalog Schema نهائي وتنفيذ المرحلة الأولى
  كعارض محلي Read-only قبل السماح بالاستيراد أو تعديل الأصول.

### 2026-08-24-59 — توحيد رسومات الأعداء وتوسعة الحملة بمرحلة ختامية

- المنفذ: Codex
- طلب المستخدم: إعادة رسم كل الأعداء ما عدا Striker وShield Guard بنفس الوضوح
  والأسلوب، وإنشاء أعداء وMini Boss وBoss مخصصين لكل مرحلة، وإضافة مرحلة ختامية
  تجمع موجات المراحل ورؤساءها؛ يظهر كل رئيس مراقبًا وغير قابل للضرب أثناء موجته،
  ثم تبدأ مواجهته، وتنتهي الحملة برئيس أخير هو الأقوى.
- الحالة: مكتمل ومنشور في `v0.44.0-alpha`.
- نقطة البداية: `v0.43.0-alpha` / commit `c473b1f` (آخر commit وظيفي
  `8600fa14cb7d11faa04fd953c965d5180633f686`).
- ما تم:
  - إعادة رسم Grunt وSkater وBrute وJunk King بأطالس موحدة `960×1152`، مع
    تثبيت المقياس والقدم وهوامش الحركة؛ بقي Striker وShield Guard دون إعادة رسم.
  - إضافة 16 نوعًا جديدًا: Lantern Courier وMarket Enforcer وKeeper-7 وRail
    Runner وSignal Warden وRailmaster-9 وCargo Loader وHarpoon Drone وDock
    Crusher وTidebreaker وScrap Stalker وCore Jammer وFurnace Brawler وPalace
    Sentinel وVox Avatar وShadow Prime. أصبح الإجمالي 22 نوع عدو.
  - توزيع أعداء خاصين وMini Boss وBoss على كل مرحلة، وتوسيع العالم إلى خمس
    مراحل و14 منطقة، مع بانوراما `SHADOW CONVERGENCE` مستقلة للمرحلة الخامسة.
  - بناء حالة الرئيس المراقب: لا AI أو تصادم أو استهداف أو ضرر أثناء الموجة، ثم
    يتحول إلى رئيس مقاتل بعد سقوط آخر عدو. المرحلة الأخيرة تعيد أربع موجات
    ورؤساء المراحل، ثم Vox Avatar وShadow Prime الأقوى (`760 HP`/`27 damage`).
  - إبقاء كل Encounter عند أربعة أطالس أو أقل، وتحرير جميع أطالس العدو عند
    تجاوز آخر منطقة. ميزانية الرسوم المتحركة المقاسة `66.04 MiB`.
  - إضافة 22 مشهدًا ثنائي اللغة و241 مفتاح واجهة، وتصحيح رئيس المرحلة الرابعة
    إلى Junk King، وإضافة معيار الإنتاج ومولد أطالس قابل لإعادة الاستخدام.
  - رفع `versionCode 53` و`versionName 0.44.0-alpha`.
- الملفات المعدلة:
  - Runtime: `GameView.java` و`EnemyArchetype.java` و`StageRoster.java`
    و`StageCombatRule.java` و`app/build.gradle`.
  - الأصول: `assets/enemies/` و`assets/tv/enemies/` و`backgrounds/panoramas/stage_final.png`
    ونسخة TV و`asset_manifest.json` وملفا القصة العربية والإنجليزية.
  - الأدوات: `build_enemy_grid_atlas.py` و`generate_tv_optimized_assets.py`
    و`test_final_gauntlet_contract.py` وبقية عقود الأصول/الذاكرة/المراحل.
  - المصادر والتوثيق: `assets/imagegen/android/enemies/` و
    `android/docs/ENEMY_CAMPAIGN_EXPANSION_AR.md` و`PROJECT_HISTORY_AR.md`.
- الاختبارات:
  - `validate_animation_atlases.py --allow-nonclustered` — PASS: `26/26`.
  - كل `test_*_contract.py` — PASS، ومنها المرحلة الخامسة وذاكرة TV والتعريب.
  - `assembleRelease` + R8 + Lint + توقيع والتحقق من الحزمة — PASS.
  - phone/ultrawide/Fold/Android TV ومسار ريموت لاعبين — PASS دون crash/ANR/OOM.
  - `test_full_stage_runtime.sh` — PASS للمناطق 1–14 حتى `ALL 5 STAGES CLEAR`.
- Release: `v0.44.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.44.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.44.0-alpha/family-force-family-current.apk
- APK SHA-256: `6e7db57809ddb6de51f5f91f14b45e6491eb1fa032dbfbe6eef6d5239d0f01da`.
- Commit: `48b69463bd785a3473b9120dd32c8a7878c72442`.
- ملاحظات/مخاطر: اختبار المحاكي يثبت سلامة المنطق والذاكرة، لكن الموازنة
  والإحساس البصري لكل الأنواع الجديدة يحتاجان جلسة فعلية على Xiaomi Stick وShield.
- التالي: جلسة لعب كاملة على الجهازين، وتسجيل أي عدو يحتاج ضبط سرعة/حجم/HP بدل
  إعادة رسم جماعية غير ضرورية.

### 2026-08-24-58 — دراسة مراجع Golden Axe وStreets of Rage وTMNT

- المنفذ: Codex
- طلب المستخدم: دراسة كيفية البداية والنهاية والقصة والقوائم والحوارات وبداية
  ونهاية المرحلة والفوز والخسارة ومدة المراحل وعدد الأعداء وأنواعهم وصعوبتهم
  وتنوعهم في Golden Axe وStreets of Rage وTMNT.
- الحالة: مكتمل — دراسة وتوصيات فقط، دون تعديل Runtime.
- نقطة البداية: `v0.43.0-alpha` / commit `8cf19e9`.
- ما تم:
  - دراسة Golden Axe (Genesis)، Streets of Rage 2 و4، وTMNT: Turtles in Time
    وShredder's Revenge عبر كتيبات Sega/Konami، صفحات الناشرين، مقابلات التصميم
    وLongplays ذات Timecodes.
  - تحديد نقاط القوة: Golden Axe في إحساس الرحلة والاستراحة بين المراحل؛ SOR2
    في الدخول المباشر والـStage Clear/bonuses/continues؛ SOR4 في عمق القتال
    وتركيب موجات fodder/advanced/elite والـrank؛ TMNT في المرح وبطاقات الحلقة
    وظل الرئيس والتنوع المستمر والمواقع التفاعلية.
  - قياس الإيقاع المرجعي: Turtles in Time نحو 10 مشاهد في قرابة ساعة؛ SOR4
    12 مرحلة في قرابة ساعتين؛ Shredder's Revenge 16 حلقة في نحو ساعتين، أي أن
    المدى الشائع للمراحل الحديثة 6–12 دقيقة مع رئيس في النهاية.
  - فحص Family Force الحالية: 4 مراحل/9 موجات، 30 عدوًا إجمالًا موزعين
    6/6/10/8، وستة Archetypes فقط، مع استخدام قالب Boss نفسه أكثر من مرة.
  - التوصية الرقمية: حملة 40–50 دقيقة؛ مراحل 8/10/11/13 دقيقة تقريبًا؛
    22/28/32/36 عدوًا في الفردي (118 إجمالًا) مع زيادة عددية موزونة للتعاوني،
    وحد أقصى متزامن 4–5 في الفردي و6–7 في لاعبين لحماية Xiaomi Stick.
  - التوصية بالمحتوى: 12 نوع عدو عادي على الأقل + 4 زعماء مستقلين؛ تقديم نوعين
    جديدين تقريبًا بكل مرحلة، وصناعة الصعوبة من تركيب الموجة والتوقيت والخطر
    البيئي بدل تضخيم HP.
  - اعتماد Flow: عنوان قصير، دخول الأبطال، حوار سفلي أثناء المشي، أول اشتباك
    سريع، 5–8 مواجهات متنوعة، دخول رئيس وحوار سفلي، ضربة نهاية واحتفال، ثم
    Stage Clear وScore/Time/Combo/Damage/Rank ودليل قصصي وخريطة المرحلة التالية.
  - اعتماد خسارة غير مفاجئة: سقوط/عد تنازلي للإحياء، ثم Continue واضح بخيارات
    checkpoint أو إعادة المرحلة أو الخريطة، مع Arcade Mode محدود credits.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات:
  - مراجعة يدوية لـ`GameView.java` و`StageRoster.java` و`EnemyArchetype.java`
    و`StageCombatRule.java` — PASS؛ تم عد 30 spawn وستة archetypes.
  - بحث الويب والكتيبات والـlongplays — PASS كتقييم تصميمي.
  - Runtime — SKIPPED؛ لا يوجد تعديل في اللعبة.
- Release: لا يوجد؛ دراسة فقط.
- ملاحظات/مخاطر: 118 عدوًا لا يعني تحميلهم معًا؛ تُنشأ الموجة لحظيًا وتبقى
  ميزانية الأطالس مرتبطة بالمرحلة. العدد النهائي يحتاج Playtest على Xiaomi.
- التالي: تحويل الدراسة إلى Campaign Design Spec مفصلة لكل مرحلة وموجة وعدو
  ورئيس، ثم تنفيذ Stage 1 كنموذج واعتماده قبل تعميم المراحل الأربع.

### 2026-08-24-57 — خطة الهوية الأيقونية والأصول الجديدة

- المنفذ: Codex
- طلب المستخدم: "ما الإضافات والتحسينات والصور الجديدة في الخطوة السابقة؟
  أريد أن تكون اللعبة أيقونية."
- الحالة: مكتمل — جرد وتصور وخطة فقط، دون إنشاء صور أو تعديل اللعبة.
- نقطة البداية: `v0.43.0-alpha` / commit `829d16d`.
- ما تم:
  - توضيح أن الخطوة السابقة لم تنشئ صورًا؛ اعتمدت فقط صندوق الحوار السفلي ودخول
    الزعماء كتصميم قادم.
  - جرد الأصول الحالية: توجد صور وتعابير جاهزية للأبطال، لكن لا توجد مجموعة
    تعابير حوار كاملة ولا صور شخصية حقيقية لفوكس والزعماء؛ الخصوم غير الأبطال
    يظهرون في الحوار حاليًا برمز عام.
  - اعتماد ركيزتين بصريتين متكررتين: شارة `Family Link` بألوان الأبطال الأربعة،
    وختم `Shadow Grid` بنفسجي/أسود يظهر على الشاشات والروبوتات والزعماء.
  - تحديد Iconic Pack: Key Art رئيسي، شعار/أيقونة محسنان، أربع أوراق تعابير
    للأبطال، خمس أوراق لفوكس والزعماء، أربع بطاقات مراحل، أربع شرائح دليل، لوحة
    انتصار عائلية، وعناصر UI للحوار ودخول الرئيس.
  - اقتراح مرحلة لاحقة لأربعة Boss Model Sheets وأطالس حركة منفصلة حتى تختلف
    Silhouettes الزعماء داخل اللعب، مع تحميل أطلس زعيم المرحلة الحالية فقط.
  - أداة الإنتاج المقترحة عند التنفيذ: ChatGPT ImageGen للصور الثابتة وModel
    Sheets بالاعتماد على الأصول المعتمدة، ثم أدوات المشروع المحلية للقص والتوحيد
    والتصغير والأطالس؛ لا Higgsfield ولا فيديو.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات: جرد أحجام وأبعاد صور PNG الحالية — PASS؛ Runtime — SKIPPED لأن
  الطلب تخطيط فقط.
- Release: لا يوجد؛ طلب تصور وخطة فقط.
- ملاحظات/مخاطر: الدقة المصدرية العالية لا تُحمّل مباشرة في Runtime؛ تُحفظ
  المصادر خارج الحزمة وتُشتق منها صور 256–512px وأطالس TV محسّنة لمنع التقطيع.
- التالي: اعتماد Iconic Core، ثم كتابة Visual Bible ومطالب التوليد قبل إنتاج
  الصور واحدة تلو الأخرى.

### 2026-08-24-56 — اعتماد حوار سفلي داخل اللعب ودخول الزعماء

- المنفذ: Codex
- طلب المستخدم: "الحوارات لا تكون بشاشة كاملة؛ تكون أسفل الشاشة، وحوار
  الرؤساء يظهر أسفل الشاشة عندما يظهرون."
- الحالة: مكتمل — اعتماد تصميم وخطة فقط، دون تعديل Runtime.
- نقطة البداية: `v0.43.0-alpha` / commit `1fd718f`.
- ما تم:
  - إلغاء شاشة القصة الكاملة كاتجاه للحملة الجديدة؛ تبقى شاشة كاملة فقط لعناوين
    المراحل والنتائج، لا للحوار.
  - اعتماد صندوق Lower-third شفاف داخل مشهد اللعب: صورة صغيرة للمتحدث، اسمه،
    سطر أو سطران، RTL عربي/LTR إنجليزي، ومؤشر تخطٍ واضح.
  - الحوار العادي لا يقطع المشي؛ يُعرض لوقت قصير ويُصف في Queue حتى لا يتراكب.
  - عند دخول الرئيس: يظهر الرئيس أولًا، تُقفل الحركة والضرر لحظيًا، يدور الحوار
    السفلي، ثم تظهر إشارة بدء المواجهة وتُعاد السيطرة للاعبين معًا.
  - في الهاتف/Fold يرتفع الصندوق فوق أزرار اللمس، وفي TV يبقى ضمن Safe Area ولا
    يغطي HUD أو شريط صحة الرئيس.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات: SKIPPED؛ قرار تصميمي فقط ولا يوجد تغيير في اللعبة.
- Release: لا يوجد؛ توثيق فقط.
- ملاحظات/مخاطر: يجب أن يوقف حوار الرئيس العدادات والضرر دون إيقاف الصوت، وأن
  يسمح P1 أو P2 أو الريموت بالتقديم من دون تنفيذ ضربة بالخطأ.
- التالي: تضمين النظام في Beat Sheet الجديد، ثم تنفيذ مكوّن الحوار السفلي قبل
  إدخال النص النهائي.

### 2026-08-24-55 — تقييم القصة والحوارات وتحديد الخطوة التالية

- المنفذ: Codex
- طلب المستخدم: "ما التالي مع العلم أن القصة والحوارات ليست جيدة؟"
- الحالة: مكتمل — مراجعة وخطة فقط، دون تغيير محتوى اللعبة.
- نقطة البداية: `v0.43.0-alpha` / commit `c6542ef`.
- ما تم:
  - مراجعة Story Bible وجميع المشاهد الـ18 والأسطر الـ55 بالعربية والإنجليزية.
  - تحديد أن الخلل كتابي لا تقني: المشاهد قصيرة جدًا، معظم الحوار يشرح معلومات
    الشبكة، أصوات الأطفال متقاربة، الصراع شخصيّته ضعيفة، فوكس والزعماء مسطحون،
    والنهايات تنقل معلومة المرحلة التالية بدل صنع لحظة درامية.
  - اعتماد إعادة كتابة عربية أولًا، ثم تكييف إنجليزي طبيعي، مع بقاء IDs وبنية
    JSON الحالية لتقليل مخاطر التنفيذ.
  - اقتراح حبكة أقوى: فوكس يستخدم مفتاح صيانة خفيًا، يلفق لعيسى تهمة الاختراق،
    والعائلة تنقذ الناس وتجمع الدليل وتحرر الروبوتات بدل تدميرها.
  - اعتماد أصوات واضحة: عيسى هادئ وحاسم بلا خطب، آدم شجاع ومرح يتعلم ضبط القوة،
    شيخة دقيقة وذكية بروح فكاهة هادئة، سليمان قائد متفائل، وفوكس لبق ومتلاعب.
  - الخطة المقترحة: Beat sheet جديد، ثم Script عربي، ثم تكييف إنجليزي، ثم
    حوارات قصيرة داخل القتال، ثم تكامل واختبارات النص والتصفح والأداء.
- الملفات المعدلة:
  - `PROJECT_HISTORY_AR.md`
- الاختبارات: مراجعة يدوية للمشاهد والأسطر — PASS كتقييم؛ اختبارات Runtime —
  SKIPPED لأن الطلب تخطيط فقط ولا يوجد تغيير في اللعبة.
- Release: لا يوجد؛ طلب تقييم وخطة فقط.
- ملاحظات/مخاطر: مضاعفة النص بلا ضبط الإيقاع ستبطئ اللعبة؛ يجب إبقاء المشاهد
  قابلة للتخطي وقصيرة، ونقل جزء من الشخصية إلى تعليقات أثناء اللعب.
- التالي: تنفيذ المرحلة الأولى: Story Bible وBeat Sheet جديدان واعتمادهما قبل
  استبدال JSON داخل اللعبة.

### 2026-08-24-54 — استكمال التعريب الشامل لواجهة اللعبة

- المنفذ: Codex
- طلب المستخدم: "ابدأ إكمال التعريب".
- الحالة: مكتمل ومنشور.
- نقطة البداية: `v0.42.0-alpha` / commit `3314531`.
- ما تم:
  - توسيع قاموس الواجهة إلى 215 مفتاحًا متطابقًا في العربية والإنجليزية وربطه
    بالقائمة الرئيسية واختيار الشخصيات وبداية المرحلة والقصة وHUD والأسلحة
    ورسائل المواجهات والإيقاف والإعدادات والتحديث والنتائج وGame Over/Gallery.
  - جعل خيار اللغة يغيّر الواجهة والقصة معًا فورًا، مع RTL للنصوص القصصية.
  - تعريب أسماء الأبطال الافتراضية وأدوارهم وحركاتهم، مع الحفاظ على أي أسماء
    عملاء مخصصة بدل استبدالها تلقائيًا.
  - تعريب أسماء المراحل والمواقع والأهداف والتلميحات والأعداء وحالات الحوار،
    وإضافة معالجة محلية لحالات Game Update.
  - إضافة عقد آلي يمنع اختلاف مفاتيح العربية والإنجليزية أو سقوط شاشة من التغطية.
  - رفع `versionCode` إلى 52 و`versionName` إلى `0.43.0-alpha`.
  - نشر الإصدار كـGitHub Latest غير Pre-release حتى يراه زر Game Update داخل التطبيق.
- الملفات المعدلة/المضافة:
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/app/src/main/assets/story/story_ar.json`
  - `android/app/src/main/assets/story/story_en.json`
  - `android/app/src/main/assets/asset_manifest.json`
  - `android/app/build.gradle`
  - `android/tools/test_ui_localization_contract.py`
  - `android/tools/test_customer_release.sh`
  - `android/tools/test_encounter_gate_contract.py`
  - `android/tools/test_in_app_update_contract.py`
  - `android/tools/test_stage_combat_identity_contract.py`
- الاختبارات:
  - `./gradlew --no-daemon :app:assembleDebug :app:lintDebug test` — PASS.
  - `python3 tools/test_ui_localization_contract.py` — PASS، 215 مفتاحًا.
  - `python3 tools/test_story_content_contract.py` — PASS، 18 مشهدًا و55 سطرًا لكل لغة.
  - جميع عقود Python للأداء والذاكرة والأسلحة والقتال والأطالس والتحديث — PASS.
  - `tools/test_controller_compat.sh` — PASS.
  - `tools/test_full_stage_runtime.sh` — PASS للمناطق 1–9 دون crash/ANR/OOM.
  - `tools/test_customer_release.sh` — PASS للبناء والتوقيع والتحقق وملفات
    phone/ultrawide/Fold/Android TV ومسار الريموت.
  - فحص بصري بالمحاكي — PASS للقائمة والإعدادات واختيار البطل والقصة وبداية
    المرحلة وHUD بالعربية، دون قص للنصوص الأساسية.
- Release: `v0.43.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.43.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.43.0-alpha/family-force-family-current.apk
- SHA-256: `d824ea22a67b4f07a14a571598c32805f42c5cd366aabcdbb4daec5ec57ccccf`.
- commit: `8600fa14cb7d11faa04fd953c965d5180633f686`.
- ملاحظات/مخاطر: الأسماء والعلامة التجارية المخصصة تبقى كما أدخلها العميل؛
  يلزم اختبار لغوي وسمعي نهائي على Shield وXiaomi Stick الحقيقيين.
- التالي: لعب الحملة كاملة بالعربية والإنجليزية على الجهازين وتسجيل أي مصطلح
  يحتاج تحسينًا دون تغيير منطق القتال.

### 2026-08-23-53 — تنفيذ الحملة القصصية والآركيد بالتتابع محليًا

- المنفذ: Codex
- طلب المستخدم: تنفيذ جميع المراحل المتفق عليها بالتتابع، ثم التأكيد على عدم
  استخدام Higgsfield لأن الرصيد انتهى، وإكمال البناء محليًا.
- الحالة: مكتمل ومنشور.
- نقطة البداية: `v0.41.0-alpha` / commit `5d7907d`.
- النطاق: Story Bible ثنائية اللغة، localization/dialogue، Intro/Outro وحوارات
  الزعماء، احتفال الفوز، Score/Tally/Top 10، أصول خفيفة، موسيقى أصلية محلية، QA وRelease.
- قرار الأدوات: ممنوع استخدام Higgsfield أو أي رصيد خارجي؛ لا فيديو. الموسيقى
  والأصول المساندة ستُنشأ محليًا بأدوات قابلة لإعادة البناء.
- ما تم:
  - كتابة Story Bible كاملة لحبكة `Shadow Grid` تحافظ على عيسى بطلًا أخلاقيًا
    وقدوة، مع الشرير Adrian Vox وبرنامج التحكم الخبيث في الروبوتات المنزلية.
  - إضافة 18 مشهدًا متطابقًا بالعربية والإنجليزية، و55 سطر حوار لكل لغة:
    مقدمة، Intro/Mid/Boss/Outro لكل واحدة من المراحل الأربع، ونهاية كاملة.
  - إضافة حالة Story قابلة للتصفح باللمس وريموت Android TV وDualSense، مع
    محاذاة RTL وتغليف نص عربي وخيار تبديل اللغة من Settings.
  - ربط حوار الزعيم قبل موجة الزعيم، وحوار منتصف المرحلة ونهايتها ببنية اللعب،
    دون تغيير القتال أو اللاعبين أو الأطالس المعتمدة.
  - استبدال النهاية المفاجئة باحتفال وشاشة Stage Tally بعد كل مرحلة تعرض Combat
    وTime وHealth bonus وRank من S إلى D، مع Score popup عند إسقاط عدو/التقاط Token.
  - إضافة قائمة Top 10 محلية آمنة ونتيجة نهائية تشمل Rank وTop 3.
  - إنشاء موسيقى محلية أصلية وخفيفة للقصة والمراحل الأربع والزعماء والـTally
    والنهاية، و8 شارات صوتية لبداية/نهاية المراحل؛ لا Higgsfield ولا فيديو.
  - تحويل MediaPlayer من `prepare()` المتزامن إلى `prepareAsync()` مع حماية
    generation لمنع التقطيع والسباق عند تبديل المسارات على Android TV.
  - تحديث asset manifest إلى 141 ملفًا ورفع النسخة `v0.42.0-alpha` إلى GitHub.
- الملفات المعدلة/المضافة:
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/app/src/main/java/com/familyforce/neonstreets/StoryContent.java`
  - `android/app/src/main/java/com/familyforce/neonstreets/ArcadeLeaderboard.java`
  - `android/app/src/main/java/com/familyforce/neonstreets/AudioController.java`
  - `android/app/src/main/assets/story/story_ar.json`
  - `android/app/src/main/assets/story/story_en.json`
  - `android/app/src/main/assets/audio/` (17 أصلًا جديدًا: 9 OGG و8 WAV)
  - `android/app/src/main/assets/asset_manifest.json`
  - `android/docs/STORY_BIBLE_AR_EN.md`
  - `android/design/campaign_assets.csv`
  - `android/tools/build_campaign_audio.py`
  - `android/tools/test_story_content_contract.py`
  - `android/tools/test_customer_release.sh`
  - `android/tools/test_link_preload_contract.py`
  - `android/app/build.gradle`
- الاختبارات:
  - `python3 tools/test_story_content_contract.py` — PASS: 18 مشهدًا و55 سطرًا لكل لغة.
  - `python3 tools/validate_assets.py` — PASS: 75 PNG و10 أطالس و141 ملفًا في manifest.
  - `:app:assembleDebug :app:lintDebug test` — PASS.
  - `tools/test_controller_compat.sh` — PASS.
  - عقود Audio lifecycle وLink preload وruntime smoothness وTV memory والأسلحة
    والـcheckpoint والبوابات والأعداء وهوية المراحل — PASS.
  - `tools/test_full_stage_runtime.sh` — PASS للمناطق 1–9 حتى Results على Android TV.
  - `tools/test_customer_release.sh` — PASS للبناء الموقع وR8/Lint والهاتف وultrawide
    وFold وAndroid TV ومسار الريموت/لاعبين؛ لا FATAL/ANR/OOM.
  - مسار قصة فعلي عبر A/OK من Title حتى اللعب ثم حركة — PASS على المحاكي.
- Release: `v0.42.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.42.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.42.0-alpha/family-force-family-current.apk
- SHA-256: `d3c18e5c3c7c820914c67358e870838cf10c77d1b0a5c74e810926d03002a42a`.
- commit: `2f00e35aca72cac5b58d18b6d89d6066cfc1f692`.
- ملاحظات/مخاطر: لم تُنشأ صور جديدة لأن الرسومات الحالية المعتمدة تكفي لشاشات
  القصة والاحتفال من دون ذاكرة إضافية. يبقى التقييم السمعي والجمالي للموسيقى
  والنص العربي على Shield/Xiaomi اختبار مستخدم حقيقي، وليس خطر استقرار معروفًا.
- التالي: اختبار الحملة كاملة بالعربية والإنجليزية على Shield/Xiaomi، ثم ضبط
  مستوى الموسيقى أو سرعة الحوار بناءً على الملاحظة بدل إعادة بناء الأصول.

### 2026-08-23-52 — خطة شاملة للقصة والحوارات والمراحل والصوت والنتائج

- المنفذ: Codex
- طلب المستخدم: قصة وفواصل لكل مرحلة، حوارات بين الأبطال والأشرار وخصوصًا
  الزعماء، موسيقى لبداية ونهاية كل مرحلة وثيم خاص بكل مرحلة، وخطة شاملة لكل
  طلبات الانتقالات والـScore السابقة.
- الحالة: مكتمل — تخطيط إنتاجي دون تنفيذ.
- نقطة البداية: `v0.41.0-alpha` / commit `e58bfac`.
- ما تم:
  - توحيد المسارات في خطة واحدة: Story Bible ثنائية اللغة، localization data،
    state machine للمقدمة/الحوار/الـKO/الاحتفال/التجميع، وأربع مراحل قصصية.
  - تخطيط حوارات البداية والمنتصف والزعيم والهزيمة والنهاية لكل مرحلة، مع بقاء
    الأبطال الأربعة في القصة مهما كان اختيار P1/P2.
  - تخطيط 11–15 أصلًا صوتيًا: قصة، أربع ثيمات مراحل loop، intro/clear stings،
    boss/final boss، tally، ending وhigh-score، مع preload وcrossfade آمن لـTV.
  - دمج نظام Score popups وStage Tally ورتب S–D وTop 10 محلي ضمن الخطة.
  - تحديد بوابات QA للغة العربية RTL، اليد/الريموت، lifecycle الصوت، الحفظ،
    منع احتساب clear مرتين، وذاكرة Xiaomi/Shield.
- الملفات المعدلة: `PROJECT_HISTORY_AR.md` فقط.
- الاختبارات: فحص AudioController والأصول الحالية — PASS (حلقتان OGG و7 WAV)؛
  Runtime — SKIPPED لأن الطلب تخطيط فقط.
- Release: لا يوجد؛ تحديث توثيقي فقط.
- ملاحظات/مخاطر: `MediaPlayer.prepare()` الحالي متزامن؛ يجب عدم تبديل موسيقى
  المراحل على خيط اللعب. النصوص والصوت والفواصل يجب أن تكون data-driven لتخصيص العملاء.
- التالي: اعتماد أسماء الشرير والشركة والزعماء، ثم كتابة Story Bible والنص الكامل
  بالعربية والإنجليزية قبل بدء كود الحالات أو إنتاج الموسيقى.

### 2026-08-23-51 — اعتماد شبكة الروبوتات المنزلية الخبيثة

- المنفذ: Codex
- طلب المستخدم: الشرير يبيع روبوتات منزلية تحتوي برنامجًا خبيثًا نائمًا، أو
  يهكر شبكة الروبوتات لاحقًا ويتحكم بها لتصبح شريرة.
- الحالة: مكتمل — تطوير حبكة دون تنفيذ.
- نقطة البداية: commit `825cbbb`.
- ما تم: دمج الفكرتين في حبكة واحدة؛ شركة الشرير تبيع روبوتات منزلية موثوقة،
  لكنها تحتوي Backdoor مخفيًا يتصل بـShadow Grid. عند انتشارها يفعل الشرير
  البرنامج تدريجيًا، بينما يكتشف عيسى حركة الشبكة غير الطبيعية ويبلغ عنها.
- الملفات المعدلة: `PROJECT_HISTORY_AR.md` فقط.
- الاختبارات: Runtime — SKIPPED؛ تطوير قصصي فقط.
- Release: لا يوجد.
- ملاحظات/مخاطر: يجب إبقاء المصطلحات التقنية مبسطة للأطفال، مع إظهار أن الخلل
  من البرنامج والشرير لا من فكرة التقنية نفسها.
- التالي: تثبيت اسم الشرير والشركة ودافعه، ثم كتابة أحداث المراحل والحوار ثنائي اللغة.

### 2026-08-23-50 — تثبيت عيسى كبطل وقدوة أخلاقية

- المنفذ: Codex
- طلب المستخدم: رفض فكرة أن يسرق عيسى مفتاح التحكم لأنه يجب أن يكون بطلًا
  وقدوة جيدة.
- الحالة: مكتمل — تصحيح قصصي دون تنفيذ.
- نقطة البداية: commit `c82dbd9`.
- ما تم: إلغاء فعل السرقة بالكامل؛ عيسى مهندس سلامة يبلغ الجهات الرسمية، يرفض
  أمرًا خطرًا، ينقذ المدنيين أثناء التخريب، ثم يُؤتمن رسميًا على مفتاح الطوارئ
  لحماية المدينة. الخصم يلفق له تهمة ويطارده، بينما يثبت عيسى الحقيقة دون انتقام.
- الملفات المعدلة: `PROJECT_HISTORY_AR.md` فقط.
- الاختبارات: Runtime — SKIPPED؛ تعديل قصصي فقط.
- Release: لا يوجد.
- التالي: كتابة الحبكة الكاملة على أساس المسؤولية والشجاعة والتعاون وحماية الناس.

### 2026-08-23-49 — رفض فكرة الاحتفال وإعادة توجيه القصة

- المنفذ: Codex
- طلب المستخدم: رفض قصة الاحتفال العائلي لضعف الرابط المنطقي بينها وبين إنقاذ
  المدينة، وطلب اتجاه قصصي أقوى.
- الحالة: مكتمل — تصحيح إبداعي دون تنفيذ.
- نقطة البداية: commit `b01e1a1`.
- ما تم: إلغاء ترشيح الاحتفال كدافع رئيسي، واعتماد مبدأ أن يبدأ الصراع بسبب
  شخصي مباشر للعائلة ثم يتسع لكشف مؤامرة المدينة، مع خصم ودافع ونتائج واضحة.
- الملفات المعدلة: `PROJECT_HISTORY_AR.md` فقط.
- الاختبارات: Runtime — SKIPPED؛ طلب قصصي فقط.
- Release: لا يوجد.
- ملاحظات/مخاطر: الإدخال السابق محفوظ تاريخيًا لكنه لم يعد توصية معتمدة.
- التالي: اختيار حبكة قوية من البدائل الجديدة ثم كتابة Story Bible ثنائية اللغة.

### 2026-08-23-48 — اقتراح قصة ثنائية اللغة ومواضيع أصلية

- المنفذ: Codex
- طلب المستخدم: بدء كتابة قصة للعبة بالعربية والإنجليزية بدل اللعب العشوائي،
  واقتراح مواضيع مناسبة.
- الحالة: مكتمل — تصور قصصي فقط دون تنفيذ.
- نقطة البداية: `v0.41.0-alpha` / commit `263745e`.
- ما تم:
  - ربط القصة المقترحة بالمراحل الحالية: Neon Market وTransit Terminal وMoon
    Harbor وJunk Palace، وبنظام Intro/Outro المقترح في الإدخال السابق.
  - ترشيح موضوع أصلي بعنوان `قلب النيون / Heart of Neon`: سرقة أربع شرارات
    عائلية من المدينة واستعادتها مرحلة بعد مرحلة قبل مواجهة Dr. Static.
  - اقتراح بدائل: احتفال المدينة المسروق، مدينة الألعاب الحية، بوابة الزمن،
    وبطولة حماة المدينة.
  - اعتماد عرض ثنائي اللغة عبر Story Cards ثابتة، حوار قصير، دعم RTL، وخيار
    تخطي؛ بلا فيديو وبلا حاجة لتعليق صوتي في النسخة الأولى.
- الملفات المعدلة: `PROJECT_HISTORY_AR.md` فقط.
- الاختبارات: مراجعة أسماء المراحل وحقول intro/outro الحالية — PASS؛ Runtime —
  SKIPPED لأن الطلب تخطيط إبداعي فقط.
- Release: لا يوجد؛ تحديث توثيقي فقط.
- ملاحظات/مخاطر: للمشروع التجاري يجب استخدام عالم وأسماء أصلية وعدم ذكر أسماء
  أبطال أو أفلام محمية؛ يمكن تخصيص أسماء الأسرة والمناسبة لكل عميل.
- التالي: اعتماد موضوع واحد، ثم كتابة Story Bible ونصوص الشاشات الأربع بالعربية
  والإنجليزية قبل تنفيذ واجهات القصة.

### 2026-08-23-47 — خطة انتقالات المراحل ونظام Score آركيد

- المنفذ: Codex
- طلب المستخدم: تحسين البداية والنهاية المفاجئة للمراحل، إضافة احتفال وردود فعل
  بعد آخر عدو، ونظام Score/High Score/قائمة نتائج نهائية، مع اقتراحات وخطة.
- الحالة: مكتمل — تخطيط فقط دون تنفيذ.
- نقطة البداية: `v0.41.0-alpha` / commit `7e9a904`.
- ما تم:
  - فحص منطق الانتقالات الحالي؛ البداية تستخدم `zoneBanner` فقط، المرحلة الوسطية
    تستخدم مؤقت overlay واحد، والنهاية الأخيرة تستدعي `finishStage()` ثم RESULTS
    فورًا، ولذلك تغيب لحظة الفوز ورد فعل الأبطال.
  - تأكيد أن score وbestScore موجودان بالفعل، لكن عرض الـscore غير مسمى في HUD،
    ولا توجد قائمة محلية أو breakdown لكل مرحلة أو count-up آركيد.
  - إعداد خطة حالات مستقلة: Stage Intro، Last Enemy KO، Victory Moment، Stage
    Tally، Next Stage Intro، ثم Final Leaderboard، مع تنقل كامل باليد والريموت.
  - اقتراح نظام نقاط قابل للتفسير، رتب S/A/B/C، سجل Top 10 محلي، ومكافآت
    الوقت/الطاقة/no-hit/combo/weapons/co-op.
- الملفات المعدلة: `PROJECT_HISTORY_AR.md` فقط.
- الاختبارات: مراجعة ساكنة لـ`GameView.java` و`AudioController.java` — PASS؛
  Runtime — SKIPPED لأن الطلب تخطيط فقط.
- Release: لا يوجد؛ تحديث توثيقي فقط.
- ملاحظات/مخاطر: يفضل عدم ربط الانتقال بمؤقت واحد؛ state machine منفصلة أقل عرضة
  لتكرار clear أو حفظ checkpoint مرتين. صور Victory ثابتة جديدة اختيارية، بلا فيديو.
- التالي: عند موافقة المستخدم، تنفيذ المرحلة الأولى: state machine للـIntro/Outro
  واحتفال الفوز، ثم نظام score والتجميع في دفعة ثانية.

### 2026-08-23-46 — إعادة رسم Shaikha وSulaiman بمعيار V5

- المنفذ: Codex
- طلب المستخدم: "التالي Shaikha + Sulaiman" بعد اعتماد Adam V5.
- الحالة: مكتمل.
- نقطة البداية: `v0.40.0-alpha` / commit `9a4683c`.
- النطاق: Shaikha ثم Sulaiman فقط، في مسارين منفصلين؛ لا تغيير لـEssa أو Adam
  أو الأعداء، ولا إنتاج فيديو.
- الخطة: Master مستقل لكل شخصية، 11 لوحة × 8 إطارات، منع أي حرف على Shaikha،
  وحرف S واحد ثابت لسليمان فقط، ثم scale lock ونسب 108/124 سم واختبارات TV.
- ما تم:
  - إنتاج Shaikha وSulaiman كلٌ في مسار مستقل: Master و11 حركة × 8 إطارات،
    باستخدام صور ثابتة فقط بلا فيديو.
  - تثبيت Shaikha بزخارف ثلجية فقط ومنع أي حرف أو شعار في كل اللوحات.
  - تثبيت حرف `S` أسود واحد لسليمان في كل إطار يظهر فيه الصدر، دون رموز إضافية.
  - إصلاح استخراج مؤثر سليمان عندما يلامس شعاع الطاقة طرف الخلية؛ يحتفظ الآن
    بأكبر مكوّن متصل بدل حذف الشخصية مع الشعاع.
  - تطبيق scale lock بنسبة تعبئة 92% للأطفال مع نسب 108/108/124 سم، وإضافة
    أطالس UHD 384px، مع إبقاء Runtime/TV منخفض الذاكرة بالحجم السابق.
- الملفات المعدلة:
  - `assets/imagegen/android/hero-redraw-v5/{shaikha,sulaiman}/`
  - أطالس Shaikha/Sulaiman في `heroes/` و`tv/heroes/` و`runtime/heroes/`
    و`uhd/heroes/`.
  - `android/tools/build_two_character_redraw.py`
  - `android/tools/test_two_character_redraw_contract.py`
  - `android/app/build.gradle`
- الاختبارات:
  - redraw/scale-lock contract — PASS للأبطال الأربعة.
  - animation atlas + نسب الأطوال — PASS (10/10).
  - runtime atlas/smoothness/TV encounter memory — PASS (`97.12 MiB`).
  - customer Release build + R8 + Lint + signing + APK verification — PASS.
  - جهاز/Emulator — SKIPPED؛ لا يوجد جهاز متصل.
- Release: `v0.41.0-alpha` — commit `5a9e3dc` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.41.0-alpha
  — SHA-256 `758290a79904adfdc30a9954f78c54663d94336eb3f992aa4a54a10c43cd77a1`.
- ملاحظات/مخاطر: الفحص الآلي والبصري ناجح، لكن يلزم اختبار الحركة الإدراكية على
  TV حقيقي، خصوصًا special لسليمان والقفز للشخصيتين.
- التالي: تثبيت النسخة على Shield/Xiaomi وفحص الأبطال الأربعة قبل رسم محتوى آخر.

### 2026-08-23-45 — تطبيق معيار Essa V4 على Adam وShaikha وSulaiman

- المنفذ: Codex
- طلب المستخدم: بعد نجاح ثبات وجودة Essa، تطبيق الطريقة نفسها على بقية
  الشخصيات الرئيسية.
- الحالة: مكتمل — نُفذ Adam وحده بناءً على توجيه المستخدم.
- نقطة البداية: `v0.39.1-alpha` / commit `f9e287d`.
- النطاق النهائي لهذه الدفعة: إعادة رسم Adam فقط؛ Essa وShaikha وSulaiman
  وجميع الأعداء مقفلة دون تغيير.
- الخطة: اعتماد Masters تحفظ الهوية والعمر والزي، إنتاج 11×8 إطارًا ثابتًا لكل
  بطل بلا فيديو، تطبيق scale lock نفسه مع نسب الأطوال 108/108/124 سم، فحص
  الأطالس والذاكرة وTV ثم إصدار APK واحد ورفعه.
- ما تم:
  - إنتاج Master واضح لآدم و11 لوحة ثابتة × 8 إطارات، بلا فيديو.
  - رفض اللوحات الجماعية التي تسرب إليها حرف S؛ إعادة إنتاج آدم منفردًا، مع
    صدر أخضر بلا أي حرف أو شعار وفحص بصري لكل لوحة قبل الدمج.
  - تطبيق scale lock على الوقوف والمشي والقفز والقتال والتعافي، مع تثبيت خط
    الأرض وتطبيع طول knockdown.
  - إبقاء Adam وShaikha متساويين في الإسقاط لأن كليهما 108 سم.
  - إضافة UHD 384px للأجهزة ذات الذاكرة الكبيرة، مع Runtime 192px للأجهزة
    الضعيفة كي تبقى ميزانية Android TV عند `97.12 MiB`.
- الملفات المعدلة:
  - `assets/imagegen/android/hero-redraw-v5/adam/`
  - `android/app/src/main/assets/{heroes,tv/heroes,runtime/heroes,uhd/heroes}/adam_anim.png`
  - `android/tools/build_two_character_redraw.py`
  - `android/tools/test_two_character_redraw_contract.py`
  - `android/tools/test_runtime_character_atlases.py`
  - `android/app/build.gradle`
- الاختبارات:
  - redraw/scale-lock contract — PASS.
  - animation atlas + family-height contract — PASS (10/10).
  - runtime atlas/smoothness/TV encounter memory — PASS (`97.12 MiB`).
  - customer Release build + R8 + Lint + signing + APK asset verification — PASS.
  - جهاز/Emulator — SKIPPED؛ لا يوجد جهاز متصل.
- Release: `v0.40.0-alpha` — commit `4aa3d83` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.40.0-alpha
  — APK SHA-256 `d82231dbb33b730f7b4baa19646d1dd6bcb53e127e4195224b4c6f1ec23f0766`.
- ملاحظات/مخاطر: نُقلت محاولات Shaikha/Sulaiman غير المعتمدة خارج المشروع ولم
  تدخل APK. يلزم فحص آدم على TV الحقيقي للحكم على الحركة الإدراكية.
- التالي: بعد موافقة المستخدم على آدم، تنفيذ Shaikha وحدها بالطريقة نفسها.

### 2026-08-23-44 — تثبيت مقياس Essa عبر كل الحركات والقفز

- المنفذ: Codex
- طلب المستخدم: Essa ما زال غير مستقر؛ يتغير حجمه عند الحركة والمشي والقفز.
- الحالة: مكتمل.
- نقطة البداية: `v0.39.0-alpha` / commit `ef2559a`.
- التشخيص الأولي: صف المشي نفسه ثابت (`161–162px`) لكن الانتقال بين الصفوف غير
  ثابت؛ idle يقارب `162px` بينما heavy actions `130–146px` والقفز `72–111px`،
  لذلك يبدو الجسم وكأنه يصغر عند تغيير الحالة رغم ثبات مربع العرض في المحرك.
- ما تم:
  - استبدال التطبيع على مستوى الصف بتطبيع جسم كل إطار إلى ارتفاع تشريحي واحد
    لكل الحالات القائمة، مع ضغط أفقي محدود للحركات العريضة بدل تصغير الجسم كله.
  - تثبيت خط القدم للحركات الأرضية، وحفظ إزاحة Y فقط لمسار القفز دون تغيير حجمه.
  - تطبيع knockdown حسب البعد الأطول كي يبقى طول الجسم الأفقي ثابتًا.
  - إضافة عقد شامل يقيس التذبذب داخل الصف، وبين الصفوف العشرة، وطول knockdown
    في author/runtime/UHD؛ جميعها ناجحة بفارق ارتفاع `0–1px` فعليًا.
  - لم تُنتج صور جديدة ولم تتغير أي شخصية أخرى.
- الملفات:
  - `android/tools/build_two_character_redraw.py`
  - `android/tools/test_two_character_redraw_contract.py`
  - أطالس Essa الأربعة فقط و`asset_manifest.json`.
- الاختبارات:
  - two-character/cross-action scale contract — PASS.
  - animation/runtime/smoothness/TV memory/Striker/assets — PASS.
  - `test_customer_release.sh customers/family-current` — PASS؛ Build/R8/Lint/
    signature/controller/combat/TV contracts ناجحة.
  - اختبار جهاز/Emulator — SKIPPED؛ لا يوجد جهاز متصل.
- commit: `bcbd909`.
- Release: https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.39.1-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.39.1-alpha/family-force-family-current.apk
- SHA-256: `6338e2fe756a330a868ae7dfcdf607730c191289a43a4d6a3467d50fe35345d4`.
- ملاحظات/مخاطر: يلزم اختبار بصري فعلي؛ القياس الآلي يثبت أبعاد الألفا لكنه لا
  يقيس الإحساس البصري الناتج من اختلاف وضع الأطراف.
- التالي: اختبار الانتقالات المذكورة على TV قبل أي تعديل رسم جديد.

### 2026-08-23-43 — إعادة رسم أطلس Essa بثبات وجودة Striker/Guard

- المنفذ: Codex
- طلب المستخدم: Striker وGuard ممتازان؛ أطلس Essa يكبر ويصغر أثناء المشي،
  الملامح والعيون غير واضحة، وإعادة رسمه بدقة أعلى وبأسلوب متناسق معهما.
- الحالة: مكتمل.
- نقطة البداية: `v0.38.0-alpha` / commit `224b53a`.
- النطاق المقفل: Essa فقط؛ يمنع تعديل Striker وShield Guard أو بقية الشخصيات.
- ما تم:
  - إنشاء Master جديد لـEssa بوجه ونظارة ولحية أوضح، وقزحية بنية داكنة وبؤبؤ
    شبه أسود وبياض عين منفصل عن لون البشرة.
  - إعادة إنتاج الحركات الإحدى عشرة، ثمانية إطارات لكل حركة، بصور ثابتة فقط.
  - مطابقة الخط الخارجي والتباين والتظليل وعناقيد البكسل الصغيرة مع مستوى
    Striker وShield Guard دون تعديل ملفاتهما.
  - تغيير الباني ليحافظ على مساحة لوحة Essa الكاملة ويطبّق مقياسًا واحدًا للصف
    بدل قص الجسم وتكبيره لكل إطار، مع خط أرض ثابت وهوامش تمنع القص.
  - دعم إزالة خلفية chroma والخلفيات المتدرجة من الحواف دون إبقائها في الأطلس.
  - إضافة عقد يمنع رجوع scale pumping: فرق ارتفاع المشي `0–1px` في author،
    `3px` كحد أقصى في runtime، و`4px` في UHD، مع خط قدم واحد.
- الملفات:
  - `assets/imagegen/android/character-redraw-v4/`
  - `android/app/src/main/assets/{heroes,runtime/heroes,tv/heroes,uhd/heroes}/parent_anim.png`
  - `android/tools/build_two_character_redraw.py`
  - `android/tools/test_two_character_redraw_contract.py`
- الاختبارات:
  - visual atlas QA — PASS؛ لا خلفيات مستطيلة ولا قص، والمشي ثابت.
  - two-character/animation/runtime/smoothness/TV memory/Striker/stage/assets — PASS.
  - `test_customer_release.sh customers/family-current` — PASS؛ Build/R8/Lint/
    signature/controller/combat/TV contracts ناجحة.
  - اختبار جهاز/Emulator — SKIPPED؛ لا يوجد جهاز متصل.
- commit: `cae6709`.
- Release: https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.39.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.39.0-alpha/family-force-family-current.apk
- SHA-256: `95aa9cf595cc9d799e63e545273ef02e35ac51234a17ba907d69fb0756d70e8d`.
- ملاحظات/مخاطر: يلزم التحقق البصري الفعلي من العين والوجه على TV؛ الاختبارات
  الآلية تثبت المقاس والقص والحركة لكنها لا تعوّض حكم المستخدم على الشبه.
- التالي: اعتماد Essa V4 على Shield/Xiaomi قبل الانتقال إلى بطل آخر.

### 2026-08-23-42 — رفع وضوح Essa وStriker من مصادر 4K

- المنفذ: Codex
- طلب المستخدم: جودة الصور ضعيفة؛ رفع دقة الوضوح إلى 4K.
- الحالة: مكتمل.
- نقطة البداية: `v0.37.0-alpha` / commit `02b00ec`.
- النطاق: Essa وStriker فقط استمرارًا للقفل السابق؛ إنشاء Masters/Action Sheets
  عالية التفاصيل بدقة مصدر تصل إلى 4K، مع إبقاء أطالس التشغيل ضمن ميزانية Android
  TV الآمنة بدل تحميل أطلس 4K خام كامل في الذاكرة.
- ما تم:
  - حُدد سبب الضعف: خلايا runtime السابقة (`284×284` لـEssa و`218×261`
    لـStriker) تُكبّر فوق دقتها على شاشات 4K.
  - إضافة أطلس Essa بدقة `3072×4224` وخلايا `384×384`، وأطلس Striker بدقة
    `1920×2304` وخلايا `320×384`، مبنيين من المصادر الأصلية الأعلى دقة.
  - إضافة تحميل UHD متكيف عند `memoryClass >= 384 MiB` والجهاز غير Low-RAM؛
    الأجهزة الضعيفة وTV sticks تستخدم runtime الآمن لتجنب OOM والتقطيع.
  - لم تُنشأ صور أو فيديوهات جديدة؛ التعديل رفع دقة أطلس التشغيل من المصادر الحالية.
- الملفات:
  - `android/app/src/main/assets/uhd/heroes/parent_anim.png`
  - `android/app/src/main/assets/uhd/enemies/striker_anim.png`
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/tools/build_two_character_redraw.py`
  - `android/tools/test_two_character_redraw_contract.py`
- الاختبارات:
  - UHD/two-character contract — PASS، مع ثبات بقية الشخصيات byte-for-byte.
  - animation/runtime/smoothness/TV memory/Striker/assets contracts — PASS.
  - `test_customer_release.sh customers/family-current` — PASS؛ Build/R8/Lint/
    signature/controller/combat/TV contracts ناجحة.
  - فحص وجود أصلي UHD داخل APK — PASS.
  - اختبار جهاز/Emulator — SKIPPED؛ لا يوجد جهاز متصل.
- commit: `f086613`.
- Release: https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.38.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.38.0-alpha/family-force-family-current.apk
- SHA-256: `662defb04ec90db600edb48c413fb67e6a5041c6b3e577d0d5f4d2172a7c3d82`.
- ملاحظات/مخاطر: UHD المفكوك يستهلك نحو `49.50 MiB` لـEssa و`16.88 MiB`
  لـStriker؛ لذلك لا يُفرض على Xiaomi Stick. يلزم فحص بصري فعلي على شاشة 4K.
- التالي: اختبار Shield مقابل Xiaomi، ثم تعديل threshold فقط إذا أثبت القياس الحاجة.

### 2026-08-23-41 — دمج رسومات جديدة لـEssa وStriker فقط

- المنفذ: Codex
- طلب المستخدم: عدم استبدال جميع الشخصيات؛ تنفيذ الرسومات الجديدة لـEssa
  وStriker فقط، ثم بناء النسخة ورفعها.
- الحالة: مكتمل.
- نقطة البداية: `v0.36.0-alpha` / commit `f00194b`.
- النطاق المقفل: أطلسا Essa وStriker وصورهما المساندة فقط؛ Adam وShaikha
  وSulaiman وبقية الأعداء يجب أن تبقى byte-for-byte بلا تغيير.
- ما تم:
  - إنتاج action sheets ثابتة بلا فيديو لجميع حركات Essa الإحدى عشرة وحركات
    Striker الست، مع Masters وأدلة وضعيات قابلة لإعادة البناء.
  - بناء أطالس الهاتف وTV وruntime لـEssa وStriker فقط؛ ثبت اختبار SHA أن Adam
    وShaikha وSulaiman وgrunt وskater وbrute وboss وshield_guard لم تتغير.
  - إعادة لكمة Striker بذراع أقصر، وتثبيت مقياسه أثناء الحركة، وإضافة هوامش أمان
    تمنع قص القفاز أو ظهور شظايا من خلية مجاورة.
  - إضافة باني حتمي واختبار عقد خاص بنطاق الشخصيتين.
- الملفات الرئيسية المعدلة:
  - `android/app/src/main/assets/{heroes,runtime/heroes,tv/heroes}/parent_anim.png`
  - `android/app/src/main/assets/{enemies,runtime/enemies,tv/enemies}/striker_anim.png`
  - `android/tools/build_two_character_redraw.py`
  - `android/tools/test_two_character_redraw_contract.py`
  - `assets/imagegen/android/character-redraw-v3/`
- الاختبارات:
  - `test_two_character_redraw_contract.py` — PASS.
  - `validate_animation_atlases.py` — PASS، 10/10.
  - runtime atlas/smoothness/TV memory/Striker/stage/assets contracts — PASS.
  - `test_customer_release.sh customers/family-current` — PASS؛ Build/R8/Lint/
    signature/assets/controller/combat/TV contracts ناجحة.
  - `test_full_stage_runtime.sh` — SKIPPED؛ لا يوجد جهاز أو Emulator متصل.
- commit: `499e228`.
- Release: https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.37.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.37.0-alpha/family-force-family-current.apk
- SHA-256: `97abd345f6a7aeb40c652296c1fbd44e9b4058974da0b7b6a35d64eb10b68a48`.
- المخاطر المتبقية: يلزم فحص بصري فعلي على Xiaomi Stick وShield؛ لم يكن جهاز
  أو محاكي متصلًا في وقت الإصدار.
- التالي: اعتماد أو رفض أسلوب Essa وStriker على التلفاز قبل تطبيقه على أي شخصية أخرى.

### 2026-08-23-40 — توحيد المعيار البصري وإعادة رسم الأبطال

- المنفذ: Codex
- طلب المستخدم: إنشاء guideline موحد للرسومات لأن سماكة الحدود والأحجام
  وكثافة التفاصيل تختلف، ثم إعادة رسم الشخصيات الرئيسية بوضوح أعلى مع الحفاظ
  التام على أشكالهم ووجوههم وتصاميمهم الأساسية.
- الحالة: مكتمل كمرحلة معيار ومرجع؛ غير مدمج في Runtime.
- نقطة البداية: `v0.36.0-alpha` / commit `fba5cf0` (توثيق `48572d2`).
- الخطة: قياس أوراق الشخصيات الأربعة الحالية، تثبيت style bible رقمي قابل
  للاختبار، ثم إنتاج Masters/Model Sheets جديدة غير مدمرة من المراجع الحالية
  فقط، وفحص الهوية والزي والعمر والنسب قبل أي دمج في أطالس الحركة أو APK.
- ما تم:
  - إنشاء دليل رقمي موحد لسماكة الخط، التظليل، الضوء، الأحجام، الهوامش، كثافة
    البكسل، نسب الأطوال وعقد أطلس الحركة.
  - إنشاء عقد JSON قابل للفحص آليًا للأبعاد والنسب وسماكة الحدود ومنع texture/blur.
  - توليد أربع Character Model Sheets جديدة من مراجع الشخصيات الحالية نفسها
    باستخدام ImageGen المدمج، مع ثبات الوجه والزي والعمر والتصميم.
  - استخدام ورقة Essa كمرجع finish مشترك للثلاثة الآخرين. صُححت خلفية Adam
    محليًا إلى cobalt blue بدل chroma green لمنع فقد جسمه الأخضر أثناء الفصل.
  - إنتاج lineup عند النسب الحقيقية: Essa 177، Sulaiman 124، Adam/Shaikha 108 سم.
- الملفات:
  - `android/docs/CHARACTER_ART_STYLE_GUIDE_AR.md`
  - `android/design/character-style-standard.json`
  - `android/docs/VISUAL_ASSET_STANDARD_AR.md`
  - `assets/imagegen/android/heroes/style-v2/`
- الاختبارات:
  - `python3 -m json.tool android/design/character-style-standard.json` — PASS.
  - `git diff --check` — PASS.
  - فحص بصري للأوراق الأربع والـlineup — PASS كمرجع شكل؛ لم تُختبر كحركة.
- Release: لا يوجد؛ لم تتغير اللعبة أو أطالس Runtime أو APK.
- ملاحظات/مخاطر: محاولة ImageGen إضافية لتنظيف Adam رُفضت من مزود الأداة؛
  لم تُعتمد ولم تُدمج. المرشح الحالي يحافظ هويته وتصميمه، والخلفية الزرقاء
  تتيح استخراجًا آمنًا في مرحلة الإطارات. الأوراق ليست بديلًا عن 88 إطار حركة.
- التالي: إنتاج action sheets بالصور فقط لشخصية واحدة كـvertical slice، ثم
  اختبارها في اللعبة قبل إعادة بناء بقية الأبطال، لمنع إعادة عمل 352 إطارًا.

### 2026-08-22-39 — تدقيق جذري لسلسلة عرض الشخصيات

- المنفذ: Codex
- طلب المستخدم: لا تزال البكسلات كبيرة والـblur سيئًا؛ المطلوب دراسة الأطالس
  وأحجام اللاعبين ونسبهم وطريقة العرض، وتحديد أصل المشكلة وحلها جذريًا لكل الشخصيات.
- الحالة: مكتمل ومنشور.
- نقطة البداية: `v0.35.1-alpha` / commit `294eb44`.
- الخطة: قياس كل مرحلة من source frame إلى atlas cell إلى physical TV pixels،
  ومقارنتها بإصدارات ما قبل تراجع الوضوح؛ ثم إزالة أي downscale/upscale مزدوج
  واعتماد مسار رسم واحد ثابت مع ميزانية ذاكرة واختبار حركة 1080p فعلي.
- التالي: تدقيق Git/code/assets بالأرقام، إثبات السبب، نموذج بصري مقارن، ثم تنفيذ
  الإصلاح واختبار الهاتف/TV/Xiaomi profile قبل Release.
- التشخيص المثبت:
  - كانت اللعبة ترسم على مساحة منطقية `640×360` ثم تكبرها إلى التلفاز؛ كثافة
    الأطلس السابقة `1.5×` جعلت بكسل المصدر الواحد يقارب بكسلين فعليين في 1080p.
  - خلايا الطفلين هبطت إلى `116×116` بدل أصل التأليف `192×192`، فضاعت ملامح الوجه.
  - مولدا Striker وShield Guard كانا يصغران الرسمة ثم يكبرانها بـnearest لتصنيع
    عناقيد `2×2`؛ لذلك لم تكن زيادة حجم أطلس Runtime تستعيد أي تفصيل.
  - التطبيع المستقل لكل إطار غيّر مقياس الشخصية بين الحركات، وتحميل أعداء المرحلة
    كاملة كان يضغط ذاكرة أجهزة TV عند رفع الدقة.
- ما تم:
  - إعادة بناء أطالس Runtime للأبطال الأربعة والأعداء الستة من المصادر المعتمدة
    بكثافة `2.25×`، وحد أدنى `192px` لخلية البطل، مع ألوان كاملة وحواف منزوعة.
  - قفل موضع وحجم كل إطار على alpha bounds في أطلس التأليف المعتمد؛ لا يوجد
    تكبير مستقل أو scale pumping بين idle/walk/attack.
  - بناء Striker وShield Guard مباشرة من الصور الكثيفة وإلغاء عناقيد `2×2`
    الصناعية في Runtime، وإزالة أثر منفصل في ضربة Striker بعد الحركة.
  - تثبيت النسب المرئية: Essa `177cm`، Sulaiman `124cm`، Adam وShaikha `108cm`.
  - إبقاء التصغير المفلتر النهائي لأنه صار تصغيرًا طفيفًا من مصدر كثيف، مع تغيير
    warmup الأعداء من كامل المرحلة إلى المنطقة الحالية وبحد أقصى أربعة أطالس.
- الملفات الرئيسية: `android/tools/generate_runtime_character_atlases.py`،
  `android/tools/build_striker_enemy.py`، `android/tools/build_shield_guard_enemy.py`،
  `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`،
  `android/app/src/main/java/com/familyforce/neonstreets/StageRoster.java`، أطالس
  `android/app/src/main/assets/runtime/`، وعقود الاختبار/المعيار البصري.
- الاختبارات:
  - `test_runtime_character_atlases.py` — PASS، 10 أطالس placement-locked `2.25×`.
  - `validate_animation_atlases.py --allow-nonclustered` — PASS، `10/10` وكل صف متحرك.
  - `validate_assets.py` — PASS، 117 ملفًا مطابقًا للـmanifest.
  - عقود smoothness/TV memory/Stage identity/Striker/Shield/visual refresh — PASS؛
    ميزانية الرسوم `97.12 MiB` وأقصى warmup أربعة أطالس.
  - `test_full_stage_runtime.sh` — PASS لمسار المناطق التسع على Android TV Emulator.
  - `test_customer_release.sh customers/family-current` — PASS للبناء والتوقيع
    والتثبيت/التحديث وملفات phone/ultrawide/Fold/TV بلا crash/ANR/OOM.
- commit: `fba5cf0`.
- Release: `v0.36.0-alpha` —
  https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.36.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.36.0-alpha/family-force-family-current.apk
- SHA-256: `6487ecda1befb4ec0fe60c27258a444e9673a2eaa2c5d8c8509e33096a363036`.
- ملاحظات/مخاطر: تم إثبات الجودة والثبات على Emulator؛ يبقى الحكم النهائي على
  معالجة شاشة Xiaomi/Shield الفعلية اختبارًا بصريًا للمستخدم، وليس ادعاءً مخبريًا.
- التالي: مقارنة idle/walk/attack لكل شخصية على Xiaomi Stick وShield بالنسخة الجديدة.

### 2026-08-22-38 — تصحيح مسار كثافة رسومات الشخصيات

- المنفذ: Codex
- طلب المستخدم: النسخة الأخيرة جعلت جميع اللاعبين والأعداء أسوأ؛ البكسلات
  أكبر والتربيش/التغبيش أكثر، والمطلوب التراجع عن المسار الخاطئ وإصلاحه.
- الحالة: مكتمل ومنشور.
- نقطة البداية: `v0.35.0-alpha` / commit `a9730d7`.
- التشخيص الأولي: أطالس Runtime المطابقة تمامًا لحجم العرض خفّضت الدقة المصدرية
  أكثر من اللازم، ثم كبّرها Surface التلفاز من 640×360 إلى 1080p/4K؛ فظهرت
  عناقيد البكسل أكبر رغم نجاح اختبارات الأبعاد والذاكرة.
- الخطة: إعادة بناء أطالس متوسطة/عالية الكثافة من الإطارات الأصلية، استخدام
  downsampling مفلتر أثناء الرسم بدل 1:1 منخفض الدقة، ثم مقارنة لقطات فعلية
  للحركة قبل إصدار APK. لا صور AI جديدة ولا فيديو.
- ما تم:
  - استبدال أطالس 1× المرفوضة بأطالس Runtime بكثافة `1.5×` لكل الأبطال
    والأعداء العشرة، مع بقاء الحجم المرئي داخل اللعب بلا تغيير.
  - إلغاء تقليل الألوان القاسي والـnearest 1:1، واعتماد تصغير مفلتر من مصدر
    أعلى كثافة إلى الشاشة للحفاظ على الوجه والدروع والتفاصيل.
  - إضافة defringe يعيد بناء حافة كل إطار من ألوان جسم الشخصية الداخلية، وإزالة
    الهالة الخضراء القديمة من إطارات Essa من دون قص الأطراف.
  - مقارنة 1080p فعلية داخل اللعب أثناء الوقوف والمشي والوصول لأول مواجهة.
- الاختبارات:
  - أطالس Runtime وmanifest وanimation rows — PASS، 10/10.
  - `test_full_stage_runtime.sh` — PASS، المناطق التسع كاملة على Android TV.
  - `test_customer_release.sh customers/family-current` — PASS، Release/R8/Lint
    والهاتف/Fold/TV/remote والقتال والذاكرة.
  - مسار TV المسرّع: `87.6 MB PSS`، jank `0.36%`، بلا crash/OOM/ANR.
- Release: `v0.35.1-alpha` / commit `294eb44`:
  - https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.35.1-alpha
  - APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.35.1-alpha/family-force-family-current.apk
  - SHA-256: `0bdf47007e40c28f07465e461819fcc93825d5094402fb18aeae4b1c0c069043`.
- ملاحظات/مخاطر: الميزانية الرسومية ارتفعت من 28.09 إلى `51.70 MiB` مقابل
  استعادة التفاصيل، لكنها بقيت مستقرة في المسار الكامل. لا صور AI ولا فيديو.
- التالي: التحقق البصري على Xiaomi Stick وShield الحقيقيين.

### 2026-08-22-37 — إعادة بناء دقة Runtime لكل الشخصيات

- المنفذ: Codex
- طلب المستخدم: رسومات الأعداء الجديدة ما زالت الأسوأ؛ البكسلات كبيرة وباهتة
  ومغبشة. المطلوب معالجة عامة لكل الشخصيات وإعادة الأطالس إذا لزم.
- الحالة: مكتمل ومنشور.
- نقطة البداية: `v0.34.1-alpha` / commit `3c634ae`.
- القرار: الإبقاء على أطالس التأليف الأصلية، وبناء أطالس Runtime بخلايا تساوي
  حجم العرض المنطقي لكل بطل/عدو، مع حواف alpha صلبة ولوحة محدودة ورسم 1:1.
- القيود: لا فيديو، لا sharpen قاسٍ، والذاكرة تحت سقف TV الآمن.
- ما تم:
  - بناء 10 أطالس Runtime بالحجم المنطقي الفعلي بدل تصغير أطالس كبيرة كل إطار.
  - اشتقاق الأبطال والأعداء الثمانية القدامى مباشرة من الإطارات عالية الدقة،
    مع downscale عالي الجودة وalpha صلب وتحديد خفيف.
  - تحويل Striker وShield Guard إلى خلايا Runtime مطابقة للحجم عبر nearest
    للحفاظ على التفاصيل ومنع الضبابية وتضخم عناقيد البكسل.
  - رسم كل الأبطال والأعداء 1:1 بلا bitmap filtering، وإلغاء مسار Essa الخاص
    الذي كان يجعل وضوح الوقوف مختلفًا عن بقية الحركات.
  - خفض ميزانية الصور المتحركة من `37.99 MiB` إلى `28.09 MiB`.
- الملفات المعدلة:
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/app/src/main/assets/runtime/heroes/*.png`
  - `android/app/src/main/assets/runtime/enemies/*.png`
  - `android/tools/generate_runtime_character_atlases.py`
  - `android/tools/test_runtime_character_atlases.py`
  - `android/tools/validate_assets.py`
  - `android/docs/VISUAL_ASSET_STANDARD_AR.md`
  - `android/app/build.gradle`
- الاختبارات:
  - `validate_assets.py` — PASS، 117 ملفًا موثقًا.
  - `test_runtime_character_atlases.py` — PASS، 10/10 أطالس exact-scale.
  - `validate_animation_atlases.py --allow-nonclustered` — PASS.
  - `test_runtime_smoothness_contract.py` — PASS، `28.09 MiB`.
  - `test_full_stage_runtime.sh` — PASS، المسار الكامل للمناطق التسع على TV.
  - `test_customer_release.sh customers/family-current` — PASS، Release/R8/Lint
    واختبارات phone/Fold/TV/remote والذاكرة والقتال.
- Release: `v0.35.0-alpha` / commit `a9730d7`:
  - https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.35.0-alpha
  - APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.35.0-alpha/family-force-family-current.apk
  - SHA-256: `86e94a995c64330f75d729b03dc8db9444cf17ae217224a0d333e3abf2bf17d3`.
- ملاحظات/مخاطر: لم تُنتج صور AI أو فيديوهات جديدة. إعادة التوليد الكاملة للأطالس
  الثمانية القديمة تعتمد على مكتبة الإطارات عالية الدقة المحلية غير المنشورة.
- التالي: فحص بصري قصير على Xiaomi Stick وShield؛ لا يوجد crash أو مانع آلي معروف.

### 2026-08-22-36 — إصلاح وضوح العدوين وحركة/دقة البانوراما

- المنفذ: Codex
- طلب المستخدم: Striker وShield Guard أصبحا أسوأ، وخلفية Stage 4 تبقى ثابتة
  في بداية المشي ولا تتحرك إلا عند ظهور الأعداء؛ المطلوب تحسين وضوح الأعداء
  والخلفيات وإصلاح حجمها وحركتها.
- الحالة: مكتمل ومنشور.
- نقطة البداية: `v0.34.0-alpha` / commit `8219c8b`.
- القيود: صور ثابتة فقط؛ اختبار Android TV Emulator قبل الإصدار.
- التشخيص:
  - Stage 4 كانت تبدأ pan عند `4820-224=4596` بينما الكاميرا تدخلها عند `4395`؛
    لذلك بقيت الخلفية ثابتة لنحو 200 وحدة حتى اقتراب Encounter التالي.
  - العدوّان كانا يصغران إلى `720×864` ثم يرسمان بـnearest-neighbour، مع sharpen
    ثانٍ قوي؛ فصارت التفاصيل بكسلات سميكة وغير متجانسة.
  - غطاء ليلي alpha=82 كان يخفي تفاصيل البانوراما أكثر من اللازم.
- ما تم:
  - حساب بداية كل panorama من موضع كاميرا بوابة المرحلة السابقة؛ Stage 4 تبدأ
    عند `4180+425-210=4395` وتتحرك من أول تقدم للكاميرا.
  - خفض غطاء المراحل إلى alpha=34 لإظهار الأرض واللافتات والعمارة بوضوح أكبر.
  - رفع نسختي TV للعدوين إلى `840×1008` (خلية `140×168`) بدل `720×864`،
    وإلغاء sharpen القاسي، واستخدام Paint مفلتر ودقيق لهما فقط.
  - إبقاء الأعداء القدامى على مسار pixelPaint الأصلي حتى لا تتغير هويتهم.
- الملفات الأساسية:
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/app/src/main/assets/tv/enemies/{striker,shield_guard}_anim.png`
  - `android/tools/generate_tv_optimized_assets.py`
  - `android/tools/test_visual_refresh_contract.py`
  - `android/tools/test_runtime_smoothness_contract.py`
  - `android/tools/test_tv_encounter_memory_contract.py`
- الاختبارات:
  - `validate_assets.py` و10/10 atlases — PASS.
  - Visual refresh/camera math — PASS؛ Stage 4 start=`4395` وحركة أولية موجبة.
  - Shield Guard — PASS: 36 إطارًا وهوامش 12px/9px.
  - TV budget — PASS: `37.99 MiB` تحت حد 40 MiB.
  - `test_full_stage_runtime.sh` على Android TV Emulator — PASS: المناطق 1–9،
    لا FATAL/ANR/OOM، مع لقطة Stage 4 واضحة.
  - `test_customer_release.sh` — PASS: phone/ultrawide/Fold/TV ومسار remote.
  - Release/R8/Lint/signature/APK verification — PASS.
- Release: `v0.34.1-alpha`، commit `3c634ae`:
  - https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.34.1-alpha
  - APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.34.1-alpha/family-force-family-current.apk
  - الحجم: `69,117,058` bytes.
  - SHA-256: `50e5d1eb69b0f91af737e22ee0c67c5a12e5f9f33ddd74bf1e4c9a865138e6c2`.
- ملاحظات/مخاطر: Emulator أثبت المسار والأداء؛ تبقى مراجعة حسية نهائية على لوحة
  TV الحقيقية لأن معالجة الحركة/الحدة تختلف بين الشركات.
- التالي: تثبيت النسخة على Xiaomi Stick وShield ومقارنة العدوين وStage 4.

### 2026-08-22-35 — بانوراما عريضة ومعيار فني موحد وصور اختيار تفاعلية

- المنفذ: Codex
- طلب المستخدم: رفض حركة اللوحة الواحدة البطيئة، وطلب خلفيات بانورامية طويلة
  متكاملة، إعادة إنتاج Striker/Shield Guard ببكسل أدق، صور اختيار عادية ومتحمسة
  للأبطال الأربعة، وأيقونة موحدة للهاتف وAndroid TV مع معيار جودة ثابت.
- الحالة: مكتمل ومنشور.
- نقطة البداية: `v0.33.1-alpha` / commit `cc060dd`.
- القرار:
  - إنشاء بانوراما ثابتة بعرض عدة شاشات لكل Stage وربط pan بتقدم اللاعب.
  - إعادة رسم العدوين الجديدين من جديد بدل تكبير/شحذ الأطالس الحالية.
  - إضافة 8 صور اختيار: 4 neutral + 4 battle-ready مع تبديل لحظي عند الاختيار.
  - إنشاء Master icon واحد ثم اشتقاق legacy/adaptive/TV منه.
  - توثيق Standard رسومي واختبارات للأبعاد والذاكرة والتجانس.
- القيود: صور ثابتة فقط؛ لا فيديو؛ الحفاظ على Android TV والاستجابة بالريموت.
- ما تم:
  - إضافة أربع بانورامات حقيقية `2172×724` ونسخ TV `1800×600`؛ المحرك يعرض
    نافذة 16:9 تتحرك داخل الصورة بحسب تقدم العالم، بلا tile أو mirror أو تبديل.
  - إعادة بناء أطلسي Striker وShield Guard ببكسل أدق، `960×1152`، وضبط كل خلية
    داخل هامش آمن ثم إنتاج نسخة TV `720×864`؛ 36/36 إطار لكل عدو.
  - استبدال صور الاختيار الأربع وإضافة أربع صور `_ready` تتبدل عند اختيار البطل.
  - إنشاء أيقونات Legacy/Adaptive جديدة وإعلان Android TV مستقل `320×180`.
  - إضافة معيار رسومي عربي، مصدر أيقونة محفوظ، وأدوات بناء/اختبار قابلة للإعادة.
- الملفات الأساسية:
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/app/src/main/assets/backgrounds/panoramas/`
  - `android/app/src/main/assets/tv/backgrounds/panoramas/`
  - `android/app/src/main/assets/enemies/{striker,shield_guard}_anim.png`
  - `android/app/src/main/assets/heroes/*_portrait_ready.png`
  - `android/app/src/main/res/drawable-nodpi/tv_banner.png`
  - `android/docs/VISUAL_ASSET_STANDARD_AR.md`
  - `android/tools/build_visual_refresh_assets.py`
  - `android/tools/package_visual_icon.py`
  - `android/tools/test_visual_refresh_contract.py`
- الاختبارات:
  - `validate_assets.py` — PASS: 65 PNG أساسي، 10 أطالس، 107 ملفات manifested.
  - `validate_animation_atlases.py --allow-nonclustered` — PASS: 10/10.
  - `test_shield_guard_enemy_contract.py` — PASS: 36 إطارًا وهوامش 12px/8px.
  - `test_visual_refresh_contract.py` — PASS: بانوراما/صور Ready/منع التكرار.
  - `test_runtime_smoothness_contract.py` — PASS: `36.27 MiB` تحت حد 40 MiB.
  - Debug/Release + R8 + Lint + توقيع + APK verification — PASS.
  - Runtime جهاز فعلي — SKIPPED؛ لا جهاز أو Emulator متصل.
- Release: `v0.34.0-alpha`، commit `8219c8b`:
  - https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.34.0-alpha
  - APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.34.0-alpha/family-force-family-current.apk
  - الحجم: `68,507,918` bytes.
  - SHA-256: `828a004a220d5f0c3912cc0e61c4d448198f3f2de8c65661f47549238c871edc`.
- ملاحظات/مخاطر: ملف الطلب ما زال Draft لأن سجل الموافقة التجاري غير granted؛
  هذا لا يغيّر التوقيع أو قابلية تثبيت APK، لكنه يمنع وسمه كتسليم تجاري نهائي.
- التالي: اختبار بصري على Xiaomi Stick/Shield للحركة العكسية وReady portraits.

### 2026-08-22-34 — بانوراما المراحل وتوحيد وضوح الأعداء وإعادة ترتيب القوائم

- المنفذ: Codex
- طلب المستخدم: إصلاح قطع/تكرار الخلفيات وعدم تجانس الأرضية، تحسين وضوح
  الأعداء الجدد، وإعادة بناء القوائم بشكل أجمل وأكثر ترتيبًا.
- الحالة: مكتمل ومنشور.
- نقطة البداية: `v0.33.0-alpha` / commit `4192a3a`.
- التشخيص الأولي:
  - الخلفية تُضغط إلى 640×360 ثم تتكرر وتنعكس كل 640px، فتظهر وصلة وتبدل عند
    الرجوع/التقدم؛ كما تُرسم أرضية عامة فوق أرضية الصورة من y=312.
  - Striker وShield Guard يستخدمان نسخة TV بحجم 75% مثل بقية الأعداء رغم أن
    تفاصيلهما أدق وأكثر حساسية للتصغير.
  - القوائم محسنة جزئيًا لكنها لا تزال كتلتين كثيفتين وتدفن الفن خلف ألواح كثيرة.
- ما تم:
  - إزالة تكرار/عكس الخلفية كل 640px؛ كل Stage الآن لوحة واحدة مستمرة مع pan
    محدود 50px مربوط بتقدم المرحلة، لذلك لا توجد وصلة أو تبدل عند الرجوع.
  - إزالة أرضية y=312 العامة وخطوطها من مشاهد المراحل؛ أرضية الرسم الأصلية تصل
    إلى أسفل الشاشة بلا طبقة غريبة فوقها.
  - إعادة معالجة نسخ TV لـStriker وShield Guard بشحذ ثانٍ مضبوط بعد التصغير؛
    زادت وضوح الحواف والتفاصيل من دون زيادة أبعاد الأطلس أو ذاكرته المفكوكة.
  - تنظيم القائمة: الخيار النشط أصبح سطحًا واحدًا قويًا، غير النشط أخف، وحُذفت
    الخطوط والحدود المتنافسة مع النص مع إبقاء مؤشر واضح للريموت/يد التحكم.
  - إضافة عقد اختبار يمنع عودة tile/mirror ويثبت وجود أربع خلفيات مستقلة.
- الملفات المعدلة:
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/app/src/main/assets/tv/enemies/striker_anim.png`
  - `android/app/src/main/assets/tv/enemies/shield_guard_anim.png`
  - `android/tools/generate_tv_optimized_assets.py`
  - `android/tools/test_runtime_smoothness_contract.py`
  - `android/app/build.gradle`
- الاختبارات:
  - Debug + Lint — PASS.
  - مراجعة contact sheet لوضوح الأعداء — PASS.
  - Release/R8/Lint/signature/archive/assets/controller contracts — PASS.
  - TV memory/smoothness — PASS؛ بقيت `30.78 MiB`.
  - Runtime جهاز فعلي — SKIPPED؛ لا جهاز أو Emulator متصل.
- Release: `v0.33.1-alpha`، commit
  `cc060ddcb2c1b6eeb21dd8536fe89161cbb93cb0`:
  - https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.33.1-alpha
  - APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.33.1-alpha/family-force-family-current.apk
  - الحجم: `48,783,107` bytes.
  - SHA-256: `5804999b6d3b28a31a81c0224a9436d1b40c5a9149a06713128b718bd06bb312`.
- التالي: اختبار backtracking في كل Stage والقوائم ووضوح العدوين على Xiaomi/Shield.

### 2026-08-22-33 — إعادة بناء بصرية كبيرة للمراحل والقوائم

- المنفذ: Codex
- طلب المستخدم: رفض التحسينات السطحية السابقة وطلب تحسينات كبيرة وجميلة فعلًا
  للشارع والخلفيات واللافتات والقوائم.
- الحالة: مكتمل ومنشور.
- نقطة البداية: `v0.32.0-alpha` / commit `99855dc`.
- القرار:
  - استبدال طبقات الإضاءة/الانعكاسات الإجرائية الضعيفة بأصول خلفية مرسومة حقيقية.
  - إنشاء أربع مراحل ذات تكوينات مختلفة، لا مجرد ألوان مختلفة للمشهد نفسه.
  - إعادة بناء لغة اللافتات والقوائم حول هوية Arcade/Transit واحدة.
  - صور ثابتة فقط، مع ضبط أحجام TV واختبار الذاكرة والأداء قبل الإصدار.
- ما تم:
  - أربع خلفيات مرسومة جديدة فعلًا: Night Market، Transit Terminal، Moon Harbor،
    Junk Palace؛ لكل واحدة تكوين وعمارة وأرضية وإضاءة مستقلة.
  - إصلاح بنيوي: Stage 4 لم تعد تعيد استخدام خلفية Stage 3.
  - إزالة طبقات النوافذ/الانعكاسات الإجرائية السابقة بالكامل.
  - تحويل لوحة القائمة إلى أربعة Stage previews حقيقية، وتخفيف الغطاء الداكن حتى
    يظهر الفن بدل إخفائه، مع الإبقاء على وضوح التركيز والتحكم.
  - إضافة أصل 1376×768 لكل مرحلة ونسخة TV محسنة 800×450.
- الملفات الأساسية المعدلة:
  - `android/app/src/main/assets/backgrounds/stage_*.png`
  - `android/app/src/main/assets/tv/backgrounds/stage_*.png`
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/tools/generate_tv_optimized_assets.py`
  - `android/tools/validate_assets.py`
  - `android/tools/test_runtime_smoothness_contract.py`
  - `android/app/build.gradle`
- الاختبارات:
  - مراجعة contact sheet للأصول الأربع — PASS.
  - Debug + Lint — PASS.
  - Release/R8/Lint/signature/archive/assets/controller contracts — PASS.
  - TV memory/smoothness — PASS؛ الميزانية `30.78 MiB` وحد أطالس الأعداء خمسة.
  - Runtime جهاز فعلي — SKIPPED؛ لا جهاز أو Emulator متصل.
- Release: `v0.33.0-alpha`، commit
  `4192a3ac0705feec48659df78c3fda2002d87005`:
  - https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.33.0-alpha
  - APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.33.0-alpha/family-force-family-current.apk
  - الحجم: `48,766,719` bytes.
  - SHA-256: `3b40609350d4081edcefe333834d3f3593b03e580ef92e72ec9ca635c42a670d`.
- ملاحظات: الصور أُنتجت بأداة ImageGen المدمجة، من دون أي فيديو.
- التالي: اختبار المشاهد الأربعة والقائمة على Xiaomi Stick/Shield من مسافة التلفاز.

### 2026-08-22-32 — تحسين الشارع والخلفيات واللافتات والقوائم

- المنفذ: Codex
- طلب المستخدم: تحسينات للشارع والخلفية واللافتات والقوائم ثم التنفيذ.
- الحالة: مكتمل ومنشور.
- نقطة البداية: `v0.31.0-alpha` / commit `285c6fa`.
- ما تم:
  - تحسين عمق الشارع وتنوعه بصريًا من دون رفع ميزانية أطالس Android TV.
  - تطوير لافتات المراحل والبوابات والمؤشرات داخل اللعب.
  - صقل القائمة الرئيسية واختيار الشخصيات والإيقاف مع وضوح تحكم التلفاز.
  - استخدام رسوم إجرائية خفيفة وأصول المشروع الحالية فقط؛ لا فيديو.
  - إضافة نوافذ بعيدة، أحواض ضوء، انعكاسات طريق وعلامة حي مميزة لكل Stage.
  - إعادة رسم لافتات الشارع وبوابة المواجهة بلوحات مقروءة من مسافة التلفاز.
  - صقل القائمة الرئيسية وشريط المراحل وحالة لاعب الاختيار وقائمة الإيقاف.
- الملفات المعدلة:
  - `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  - `android/app/build.gradle`
  - `android/tools/test_encounter_gate_contract.py`
  - `PROJECT_HISTORY_AR.md`
- الاختبارات:
  - Debug build + Lint — PASS.
  - Release/R8/Lint/signature/archive/assets — PASS.
  - Controller compatibility + encounter gate + pickup + stage identity — PASS.
  - TV memory/smoothness — PASS؛ الميزانية بقيت `30.09 MiB` وحد الأطالس خمسة.
  - Runtime جهاز فعلي — SKIPPED؛ لا جهاز أو Emulator متصل.
- Release: `v0.32.0-alpha`، commit
  `99855dc13b612c6372ba85bbe8a219aac4f4bc66`:
  - https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.32.0-alpha
  - APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.32.0-alpha/family-force-family-current.apk
  - الحجم: `44,215,185` bytes.
  - SHA-256: `f06773def76e074507c8e4e628e25550b5e5041604061d0510a0b90e45f4972f`.
- التالي: اختبار بصري سريع على Xiaomi/Shield، ثم نقل عدو Ranged Drone المخطط
  إلى `v0.33.0-alpha` لأن `v0.32` أصبحت حزمة التحسين البصري.

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
- الحالة: `v0.49.1-alpha` منشور؛ خمس مراحل و14 منطقة و22 نوع عدو، مع Mini Boss
  وBoss لكل مرحلة ومرحلة ختامية تعتمد موجات ورؤساء مراقبين ثم Shadow Prime.
- آخر عمل: hotfix أعاد أصول Essa وAdam وGrunt وLantern ومحمل الحركة إلى نسخة
  `v0.48` المقبولة، وأصلح استحواذ DualSense على P1 داخل اللعب الفردي بعد الريموت.
- آخر قرار: إطارات `v0.49.0` الوسيطة المزاحة آليًا مرفوضة؛ لا يطبق شرط 12 صورة
  مجددًا إلا بصور مستقلة مرسومة فعليًا وبعد قبول عينة واحدة داخل اللعبة.
- الملفات المتوقع أن يقرأها الوكيل التالي أولًا:
  1. `PROJECT_HISTORY_AR.md`
  2. `android/README.md`
  3. `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  4. `android/app/src/main/java/com/familyforce/neonstreets/SpriteAnimator.java`
  5. `android/docs/SEPARATE_ANIMATION_CLIP_STANDARD_AR.md`
  6. `android/tools/test_separate_animation_clips.py`
  7. `android/app/src/main/java/com/familyforce/neonstreets/EnemyArchetype.java`
  8. `android/app/src/main/java/com/familyforce/neonstreets/StageRoster.java`
- الإجراء التالي المقترح: تثبيت APK `v0.49.1-alpha` وتجربة Essa وAdam والأعداء
  بصريًا، ثم DualSense داخل PLAY فردي ولاعبين على Shield. لا يبدأ أي redraw شامل
  قبل قبول هذه نقطة الرجوع المستقرة.
