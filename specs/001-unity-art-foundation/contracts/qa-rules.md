# Family Force Art Contract v1.0-candidate

هذه القواعد حاجبة ما لم توصف صراحة بأنها بوابة معايرة. الأرقام على شبكة منطقية
`512×512`؛ عند اختيار Runtime أصغر تضرب القيم في scale نفسه وتبقى world size ثابتة.

## A. Source and traceability

| ID | القاعدة | النتيجة عند الفشل |
|---|---|---|
| SRC-001 | كل Frame ملف PNG RGBA مستقل، long side >=2048px | Blocker |
| SRC-002 | الخلفية شفافة أصلًا؛ يمنع chroma key أو إزالة لون آلية كمسار معتمد | Blocker |
| SRC-003 | لا يدخل Master إلى `Assets/**/Runtime` أو APK | Blocker |
| SRC-004 | يلزم hash، source tool، rights، actor/action/frame وcontract version | Blocker |
| SRC-005 | لا تحفظ صور العملاء الخام أو أسرار/Prompts حساسة في Git أو التقرير | Blocker |

## B. Logical geometry

| ID | القاعدة | الحد |
|---|---|---|
| GEO-001 | PPU موحد | candidate 128، يقفل بعد Calibration |
| GEO-002 | Transform scale لكل شخصية | `(1,1,1)` |
| GEO-003 | Ground/pivot line | `y=24`، drift للقدم `±1px` |
| GEO-004 | Essa standing body height | `368±4px` |
| GEO-005 | Grunt standing body height | `334±6px` |
| GEO-006 | idle/walk body-height coefficient of variation | `<=1.5%`؛ الحد المطلق `<=2%` |
| GEO-007 | neutral hip center | `x=256±4px` |
| GEO-008 | head/torso drift غير المقصود | head `<=3px`، torso `<=4px` |
| GEO-009 | transparent safety border before trim | target `24px`، absolute minimum `16px` |
| GEO-010 | weapon/FX يخالف الهامش | يفصل Sprite مستقل، لا يقص الجسم |

Offline trim يحفظ موضع `(256,24)` كـcustom pivot بعد القص. يقارن validator كل
Frame بعد إعادة بنائه إلى canvas المنطقي، ولذلك لا تسمح أبعاد PNG المتغيرة بتغير
الحجم أو القفز على الأرض. تستثنى jump/knockdown من خط القدم فقط بannotation صريح
وanchor بديل؛ لا تستثنى من القص أو ثبات النسب.

## C. Pixel structure and style

- لا يستخدم PPI؛ المعيار PPU وحجم الجسم وscreen-pixel ratio.
- إضاءة ثابتة من أعلى اليسار.
- outline الخارجي `3–5px` على شبكة 512، والداخلي `1–3px`.
- أصغر تفصيل مقصود `2px`؛ يمنع noise منفرد 1px خارج whitelist العين/لمعة المعدن.
- الوجه والعينان والشعر والزي والدرع لا تتغير نسبها أو ألوانها بين Frames.
- العين منفصلة لونيًا عن البشرة ومقروءة في Review 1080p.
- palette drift لنفس المادة لا يتجاوز `DeltaE 2000 = 3` في swatches المرجعية،
  مع استثناء موثق للإضاءة/الضربة.
- يمنع blur وsoft antialias وmotion blur داخل Sprite الشخصية.
- الرموز الدينية والمذهبية والوطنية والحضارية والرونية والطلاسم والشعارات غير
  المعتمدة ممنوعة. لا يكفي classifier آلي؛ المراجعة البشرية حاجبة.
- حرف `S` محصور بسليمان، مع رسم يسار مستقل حتى لا يعكس الحرف.

## D. Alpha and edges

| ID | القاعدة | النتيجة |
|---|---|---|
| ALP-001 | Straight RGBA؛ Character alpha يساوي 0 أو255 | Blocker؛ partial alpha للـFX فقط |
| ALP-002 | RGB تحت alpha=0 تنظفه recipe إلى قيمة محايدة ثابتة | Blocker إذا أنتج fringe |
| ALP-003 | لا opaque pixel في آخر 16px من logical boundary | Blocker |
| ALP-004 | لا white/gray fringe غير مصرح ضمن 3px من silhouette | Blocker بعد review |
| ALP-005 | فحص فوق black/white/magenta وStage background | مطلوب لكل Frame |

الأبيض داخل العين أو الدرع يسمح به فقط إن كان متصلًا بتفصيل معتمد ولا يتحول إلى
حلقة تحيط بالشخصية. Alpha dilation في Atlas لا يصلح مصدرًا ذا matte سيئ.

## E. Animation

- كل action >=12 Frame فريدة؛ blank/duplicate/mirrored duplicate لا يحتسب.
- كل action playback >=12 fps؛ Render يبقى 60 fps.
- hold Frame مسموح زمنيًا لكنه يوسم ولا يحتسب رسمة فريدة إضافية.
- نقاط بدء مقترحة: idle/walk 12fps، punch 18fps، kick 15–18fps، heavy/special
  12–15fps، hurt 18fps. التوقيت النهائي يطابق gameplay timeline.
- Walk 12-frame structure:
  1. right contact
  2. right load
  3. approach pass
  4. right passing
  5. left high/up
  6. left pre-contact
  7. left contact
  8. left load
  9. approach pass
  10. left passing
  11. right high/up
  12. right pre-contact
- الرجلان تتبادلان التقدم، swing الذراع المقابل منطقي، ولا يتحرك السلاح/الدرع
  عشوائيًا بين Frames.
- لا يكرر Frame 0 في النهاية لرفع العدد.
- لا root motion؛ translation من PlayerMotor/Enemy motor.
- hitbox/damage timing من ActionDefinition، لا من شكل Frame وحده.
- hit-stop يجمّد Animator والقتال؛ UI/pause وحدهما يستخدمان unscaled time.

## F. Unity import and Atlas

- Sprite Mode Single لكل Runtime Frame.
- Custom pivot مشتق من manifest؛ Mesh Full Rect في المرجع.
- PPU موحد، sRGB on، Wrap Clamp، mipmaps off، Read/Write off.
- Atlas لكل actor؛ FX وweapons منفصلة.
- Max page 2048، padding>=8، rotation off، tight packing off في المرجع.
- لا يعتمد tight packing أو alpha dilation إلا بعد regression test للحواف/pivot.
- Hero pilot page count: <=2 لثلاث حركات Pilot؛ regular enemy <=2.
- لا يحمل سوى Atlas الأبطال المختارين وأعداء Stage 1 الحاليين.

## G. Compression and clarity

- RGBA32 produces the reference render.
- Compare ETC2 RGBA8 and ASTC 4x4 on target hardware.
- No ASTC 6x6/8x8 for Phase 1 character art.
- Automated gate: silhouette mismatch=0, SSIM>=0.98 and PSNR>=38dB on opaque
  actor region. Human review can still reject.
- If no compressed candidate passes, reduce packed area/residency before allowing
  selective RGBA32; never solve it by loading every Atlas uncompressed.

## H. Device and runtime acceptance

- Review: 720p and1080p, 1P and2P, black/white/magenta/Stage 1.
- Phone 20:9، Fold folded/unfolded و1080-to-4K TV upscale يحصلون screenshot
  regression؛ الأداء الحاجب يبقى Xiaomi/Shield.
- 30-minute session **per mode per device** on Xiaomi then Shield: no crash/ANR/OOM.
- Target render 60fps; 1% low>=50fps on Xiaomi test baseline.
- After warm preload, first visible use load spike<=50ms and no main-thread file decode.
- Pilot resident memory increase<=20% over v0.5 baseline unless explicitly approved.
- On 1GB low-RAM profile, target Graphics 30–40MB and total<=280MB; record actual
  even if hardware counters are incomplete.
- Approval bound to hashes of PNG, meta, manifest, recipe, clips, controllers,
  Atlas/import/compression, prefab/material/scale and camera/PPU.

## I. Calibration-only decision

Before Art Contract becomes `1.0-active`, compare logical 320/384/512 or equivalent
Atlas Variants. Select the smallest tier with:

- texel-to-screen ratio between 0.75 and1.25 at the reference actor size,
- no loss of eyes, armor seams or silhouette,
- no shimmer during camera/player motion,
- memory and FPS gates passing.

This is the only unlocked numeric rule. Once chosen it is recorded in the contract
and becomes a blocking importer setting.
