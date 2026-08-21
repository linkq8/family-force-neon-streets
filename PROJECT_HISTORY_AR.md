# السجل المشترك للمشروع — Family Force: Neon Streets

> هذا الملف هو المصدر المركزي لتبادل السياق بين **Codex** و**Claude Code**.
> يجب على كل وكيل قراءته قبل تعديل المشروع، وتحديثه بعد كل طلب أو تعديل أو
> اختبار أو Release. سجل الأحداث أدناه تراكمي؛ لا تُحذف الإدخالات القديمة.

آخر تحديث: 21 أغسطس 2026 — Codex

## حالة العمل الحالية

- المنتج الأساسي: لعبة Android أصلية بنمط beat-'em-up ريترو حديث، وليست Emulator.
- المنصة: الهاتف، Fold، Android TV، والريموت/يد التحكم.
- النسخة الجاري تجهيزها للنشر: `v0.24.0-alpha`، `versionCode 24`.
- الفرع المشترك: `main`.
- آخر commit وظيفي: `812dddfc893835ade902d0c0dd46d92fe64c9f90`.
- الحزمة الحالية: `com.familyforce.neonstreets.event.familycurrent`.
- Release: https://github.com/linkq8/family-force-neon-streets/releases/tag/v0.23.0-alpha
- APK: https://github.com/linkq8/family-force-neon-streets/releases/download/v0.23.0-alpha/family-force-family-current.apk
- SHA-256: `6dc3ca197716d9e7d2be26faa21be3825fe47c82d642d61e47f1fe912d9d3933`.
- حالة QA: بناء Release وLint وفحوص الهاتف/Fold/Android TV ومسار لاعبين ناجحة.
- اختبار المناطق: مسار تطويري آلي مرّ بالمناطق 1–9 حتى شاشة النتائج بنجاح.
- التشخيص: يوجد Flight Recorder محلي خفيف يحفظ آخر منطقة، P1/P2، العدو،
  السلاح، الحركة والذاكرة، ويحفظ تقرير الجلسة السابقة إذا انقطعت.
- نتيجة اختبار Shield Pro: المناطق 1–9، الموت/الإحياء، الإغلاق/الفتح، فصل اليد،
  الريموت والتقاط الأسلحة تعمل دون خروج غير طبيعي.
- إصلاح قيد تحقق المستخدم: توسيع توافق DualSense على Xiaomi ليشمل Firmware الذي
  لا يعلن نطاق trigger المكسور أو يرسل الأزرار كمصدر Keyboard.
- الاختبارات المتبقية: Checkpoint/Continue بعد خسارة أو إعادة تشغيل، وXiaomi Stick.
- العمل التالي الموصى به: تثبيت `v0.22.0-alpha` على Xiaomi Stick الحقيقي وفحص
  كل أزرار DualSense والرمي؛ ثم اعتماد الجهاز أو جمع key-event trace إن بقي اختلاف.

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
- Release: `v0.24.0-alpha` قيد الرفع؛ سيضاف الرابط وSHA بعد النشر.
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
- الحالة: تحسين السلاسة الشامل مكتمل ومختبر آليًا، وجارٍ نشر v0.24؛ يبقى قياس
  Xiaomi Stick الحقيقي.
- آخر عمل: إنشاء نظام السجل المشترك وتعليمات Codex/Claude Code.
- آخر قرار: `v0.21.0-alpha` لم يحل مشكلة Xiaomi؛ يجري توسيع الاكتشاف ليشمل
  مضيف Xiaomi وأحداث Keyboard مع فصل تصحيح الأزرار عن تصحيح المحاور.
- الملفات المتوقع أن يقرأها الوكيل التالي أولًا:
  1. `PROJECT_HISTORY_AR.md`
  2. `android/README.md`
  3. `android/app/src/main/java/com/familyforce/neonstreets/GameView.java`
  4. `android/tools/test_customer_release.sh`
- الإجراء التالي المقترح: تثبيت `v0.22.0-alpha` على Xiaomi Stick وتجربة Cross/
  Circle/Square/Triangle وL1/R1/L2/R2 وOptions وD-pad والعصا وTouchpad.
