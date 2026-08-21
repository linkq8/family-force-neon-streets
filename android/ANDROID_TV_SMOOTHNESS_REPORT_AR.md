# تقرير سلاسة Android TV

## الهدف

الحفاظ على عرض اللعبة المنطقي `640×360` ووضوح الشخصيات، مع منع فك الصور أو
قراءة الملفات أو مسح البكسلات داخل دورة القتال على أجهزة Android TV محدودة
المعالج والذاكرة مثل Xiaomi TV Stick.

## ميزانية الرسومات

- بطل TV: Atlas بحجم `1152×1584`، خلية `144×144`، مع الاحتفاظ ببطل واحد في
  وضع اللاعب الواحد وبطلين في وضع اللاعبين.
- عدو TV: Atlas بحجم `720×864`، خلية `120×144`؛ قريب من حجم العرض الفعلي
  `92×110` حتى `133×160`، لذلك لا يُنصح بتصغيره أكثر.
- الخلفيات: `960×536/540` بصيغة `RGB_565` في الذاكرة، أي 1.5× الدقة المنطقية.
- ميزانية القتال المتحركة القصوى للاعبين: `26.65 MiB` للأبطال وصفّي Link وكل
  الأعداء والخلفيتين، قبل الصور الصغيرة. بوابة الإصدار ترفض تجاوز `27 MiB`.
- قياس المحاكي بعد مسار TV: `TOTAL PSS` قرابة 57–69 MiB حسب الشاشة، وأقل من
  أهداف Android TV منخفض الذاكرة بفارق كبير.

## الإصلاحات المنفذة

1. تحميل أطالس الأعداء الأربعة في Thread منخفض الأولوية أثناء شاشة الاختيار.
2. الاحتفاظ بالأطالس طوال المرحلة؛ بوابات المجموعات تربط Bitmap جاهزًا فقط.
3. منع `BitmapFactory` و`decodeStream` و`decodeRegion` وعمليات تحميل الصور من
   `update/updateGame/updateEncounter/startAssist/updateAssist` باختبار Release.
4. تجهيز صفّي Link الخاصين بـP1/P2 قبل القتال وإعادة استخدامهما طوال الجولة.
5. استبدال آلاف استدعاءات `getPixel()` بقراءة كتلية واحدة `getPixels()` لكل إطار.
6. استخدام `prepareToDraw()` فور فك الصور، قبل عرضها، لتقديم texture upload.
7. عند ضغط الذاكرة لا تعود اللعبة إلى فك الصور داخل القتال؛ تستخدم fallback
   جاهزًا بينما يُعاد التحميل خلفيًا بعد الاستئناف.

## مراجع Android الرسمية

- Slow rendering ورفع Bitmap المبكر:
  https://developer.android.com/topic/performance/vitals/render
- ذاكرة Android TV وأهداف أجهزة 1 GB:
  https://developer.android.com/training/tv/playback/memory
- تحليل GPU rendering وSync/Upload:
  https://developer.android.com/topic/performance/rendering/profile-gpu

## بوابات منع التراجع

- `tools/test_runtime_smoothness_contract.py`
- `tools/test_link_preload_contract.py`
- `tools/test_tv_encounter_memory_contract.py`
- `tools/test_customer_release.sh`

هذه البوابات لا تدعي أن كل Firmware سيعطي زمن الإطار نفسه؛ لكنها تمنع الأسباب
المعروفة للتوقفات المفاجئة من العودة، وتبقي القياس الحقيقي على Xiaomi Stick
جزءًا إلزاميًا من اعتماد الإصدار.
