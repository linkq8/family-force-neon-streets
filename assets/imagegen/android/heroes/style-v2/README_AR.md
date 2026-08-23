# مرشحات أسلوب الأبطال v2

هذه الملفات أُنتجت بأداة ImageGen المدمجة في Codex من أوراق الشخصيات الحالية،
ولا تستبدل أطالس اللعب في هذه المرحلة.

## المراجع والنتائج المختارة

| الشخصية | مرجع الهوية/التصميم | المرشح المختار |
|---|---|---|
| Essa | `assets/higgsfield/android/animation_v2/model_sheets/hero_1.png` | `essa-model-sheet-candidate.png` |
| Adam | `assets/higgsfield/android/animation_v2/model_sheets/hero_2.png` | `adam-model-sheet-candidate.png` |
| Shaikha | `assets/higgsfield/android/animation_v2/model_sheets/hero_3.png` | `shaikha-model-sheet-candidate.png` |
| Sulaiman | `assets/higgsfield/android/animation_v2/model_sheets/hero_4.png` | `sulaiman-model-sheet-candidate.png` |

`style-lineup-preview.png` يعرض الوضعية المحايدة بالنسب الحقيقية داخل اللعب.

## معادلة الأسلوب المستخدمة

> Polished modern-retro arcade sprite illustration; clean 1–2 intended-pixel
> clusters at final 192px character-cell scale; dark navy outer contour equal
> to 2.5–3px at 192px and internal contour equal to 1–1.5px; three controlled
> cel-shading bands per material; warm upper-left key light and subtle cool
> lower-right rim; crisp edges; no blur, airbrush, halftone, noisy dithering or
> oversized square pixels; readable expressive face; fixed three-quarter
> screen-right facing; full-body safe margins.

## ثوابت الطلب

- إعادة رسم fidelity فقط، لا redesign.
- الوجه والعمر الظاهري والشعر واللون والزي والإكسسوارات والنسب ثابتة.
- شبكة 4×3: neutral، walk، punch، kick، heavy punch، heavy kick، jump، special،
  link، hurt، knockdown، victory.
- جسم كامل في كل خلية، لا قص ولا panel bleed ولا أجزاء إضافية.
- خلفية Adam حُولت محليًا من chroma green إلى `#0000FF` من دون تعديل جسمه،
  لأن الأخضر لا يصلح خلفية فصل لشخصية خضراء.

## قرار الدمج

الحالة: **مرشحات شكل معتمدة للمرحلة التالية، غير مدمجة في Runtime**. الدمج
يتطلب بناء 88 إطارًا حقيقيًا لكل بطل وفق
`android/docs/CHARACTER_ART_STYLE_GUIDE_AR.md`، ثم contact sheets واختبار حركة
وذاكرة Android TV. يمنع تحويل هذه الورقة مباشرة إلى حركة بتكرار الوضعيات.

