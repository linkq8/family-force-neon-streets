# إعادة رسم Essa وStriker — Character Redraw V3

هذا المصدر خاص بإصدار يعيد رسم **Essa** و**Striker فقط**. لا تُستبدل منه أي
شخصية أخرى.

## طريقة الإنتاج

- استُخدمت صور ثابتة مولدة داخل Codex/ImageGen؛ لم يُنشأ أو يُستخدم أي فيديو.
- `master.png` يثبت هوية الشخصية والألوان والخطوط.
- `guides/` تحفظ موضع وتوقيت كل حركة من الأطالس المعتمدة قبل إعادة الرسم.
- `actions/` هي لوحات الحركة الثابتة الجديدة ذات الخلفية الخضراء الموحدة.
- `android/tools/build_two_character_redraw.py` يقص اللوحات ويبني أطالس الهاتف
  والتلفاز ونسخ runtime عالية الكثافة بصورة حتمية.

## الحركات

- Essa: idle, walk, punch, kick, heavy punch, heavy kick, jump, special, link,
  hurt, knockdown — ثمانية إطارات لكل حركة.
- Striker: idle, walk, attack1, attack2, hurt, knockdown — ستة إطارات لكل حركة.

## تصحيحات الترتيب

- مشي Essa: استُبعد الإطار الرابع المولد لأنه كان مقصوصًا من الأعلى، والترتيب
  المعتمد هو `(0, 1, 2, 3, 5, 6, 7, 0)`.
- ركلة Essa الثقيلة: الترتيب الزمني المعتمد هو `(1, 4, 2, 0, 5, 6, 3, 7)`.
- لكمة Striker أعيد إنتاجها بذراع ممدودة قصيرة ومسافة أمان كي لا يصغر الجسم أو
  يُقص القفاز داخل خلية الأطلس.

## حدود الدمج

اختبار `android/tools/test_two_character_redraw_contract.py` يثبت أن أطالس Adam
وShaikha وSulaiman وgrunt وskater وbrute وboss وshield_guard لم تتغير بايتًا واحدًا.
