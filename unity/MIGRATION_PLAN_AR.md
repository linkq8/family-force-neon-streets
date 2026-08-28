# خطة نقل Family Force إلى Unity

## المبدأ

الهجرة إعادة تنفيذ تدريجية وليست تحويل Java إلى C# آليًا. يبقى APK الحالي
مرجعًا للسلوك حتى تتجاوز نسخة Unity بوابات التكافؤ. لا يعتمد أي أصل رسومي مرفوض
لمجرد أنه ظهر داخل النموذج.

## المرحلة 1 — الأساس (منفذة)

- Unity 6.3 LTS `6000.3.22f1` وIL2CPP.
- مشروع 2D خفيف على OpenGL ES 3 للهاتف وAndroid TV.
- ARMv7 + ARM64، API 25–36، Leanback launcher، واللمس غير مطلوب.
- Input System مع legacy key fallback للريموت.
- 60 FPS للمحرك و12 إطارًا مرسومًا/ثانية للحركة.
- Point filtering، بلا mipmaps أو ضغط، وNPOT بدون تغيير الأبعاد.
- APK نموذج مستقل يمكن تثبيته بجانب اللعبة الحالية.

## المرحلة 2 — نموذج القتال الرأسي

- تم اعتماد Sprite Atlas الرسمي للدفعة الأولى: Essa وAdam وGrunt وSkater و
  Lantern Courier وMarket Enforcer وKeeper-7، بAtlas مستقل لكل شخصية.
- P1 وP2 اختياريان مع ملكية يد مستقلة.
- اختيار البطل والمرافق لكل لاعب.
- locomotion، jump، punch/kick/heavy/special/link/hurt/knockdown.
- hitbox/hurtbox، input buffer، combo، hit-stop، knockback والسلاح.
- نظام Grab متزامن: اقتراب + زر المسك، إمساك أمامي/خلفي، ضرب أثناء المسك،
  رمية، إفلات، مقاومة العدو، وحماية من بقاء أحد الطرفين عالقًا في الحالة.
- Team Grab Combo للاعبين: عندما يمسك P1 أو P2 العدو تظهر نافذة واضحة قصيرة؛
  ضغط اللاعب الآخر زر الهجوم من المدى الصحيح ينفذ ضربة تعاونية متزامنة، مع
  مسار fallback طبيعي إذا انتهت النافذة أو ابتعد اللاعب الثاني.
- حالات ورسومات مستقلة `grab_start/hold/grab_hit/throw/team_ready/team_combo`
  للبطل والعدو، مع pivot وموضع اتصال موحد ومن دون تحجيم الرسمة أثناء التزامن.
- عدو واحد وMini Boss ومقطع Stage قصير لاختبار التكافؤ.

بوابة القبول: جلسة 20 دقيقة، remote والقوائم، DualSense/Xbox/Joy-Con، بلا
crash/ANR، وP95 frame time أقل من 16.67ms على Shield وأقل من 25ms على Xiaomi.
يجب كذلك اختبار المسك من الجهتين، تبديل دور P1/P2، انقطاع يد أثناء المسك، موت
العدو/اللاعب خلاله، وحافة الشاشة حتى لا تتجمد الشخصيات أو تتداخل.

## المرحلة 3 — المحتوى والقوائم

- القائمة الرئيسية واختيار P1/P2 والشخصيات والمرافق.
- HUD: HP/SP/LINK/score/high score ورسائل الجاهزية.
- القصة والحوار السفلي عربي/إنجليزي.
- المراحل الخمس والمناطق الـ14 وrosters والبوابات والـcheckpoint.
- الموسيقى والمؤثرات والأسلحة والنتائج وبداية/نهاية المرحلة.

## المرحلة 4 — المنتج التجاري

- Customer Pack مستقل عن الكود لتغيير الشخصيات والأيقونة والاسم.
- بناء APK موقّع لكل عميل، R8/IL2CPP stripping، وسلامة الحزمة.
- Updater يتحقق من النسخة والتوقيع وSHA-256 قبل فتح مثبت Android.
- اختبارات Xiaomi Stick وShield وSony/Skyworth والهاتف وFold.

## قواعد نقل الرسومات

- المصدر لا يقل عن 12 رسمة فريدة لكل حركة، وليس تكرارًا زمنيًا.
- أبعاد كل strip تقبل القسمة على عدد الإطارات دون NPOT resize.
- Texture import: Point، mipmaps off، NPOT none، clamp، RGBA32، بلا ضغط.
- Pivot قدم سفلي موحد، pixels-per-unit ثابت، ولا scale متغير بين الحالات.
- FX الكبيرة في textures منفصلة حتى لا توسع خلية جسم الشخصية.
- فحص Alpha فوق خلفيات سوداء/بيضاء/فوشية قبل الدمج.

## ما لا ينقل حرفيًا

- `GameView.java` لا ينقل كملف ضخم؛ يقسم إلى GameFlow، Combat، Camera، UI،
  Stage، Audio وSave systems.
- Android `Canvas` و`BitmapRegionDecoder` يستبدلان بـSpriteRenderer/Texture2D
  وAddressables لاحقًا.
- تعيينات OEM الخاصة بـDualSense تبقى طبقة Android native صغيرة خلف UnifiedInput.
