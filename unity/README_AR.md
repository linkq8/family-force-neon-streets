# Family Force — مشروع الهجرة إلى Unity

هذا المشروع هو البديل الجاري بناؤه لمحرك Android Java/Canvas الحالي. يبقى
المشروع القديم داخل `android/` مرجعًا قابلًا للعب إلى أن يحقق إصدار Unity تكافؤ
الميزات والاستقرار.

## إصدار المحرك

- Unity 6.3 LTS `6000.3.22f1`.
- Android Build Support + SDK/NDK/OpenJDK المرفقة مع Unity Hub.
- Built-in 2D rendering خفيف وOpenGL ES 3، من دون HDRP.
- Input System `1.17.0`.

## بناء النموذج

```sh
/Applications/Unity/Hub/Editor/6000.3.22f1/Unity.app/Contents/MacOS/Unity \
  -batchmode -nographics -quit -projectPath "$PWD/unity" \
  -executeMethod FamilyForce.Unity.Editor.BuildFamilyForce.BuildAndroidPrototype \
  -logFile "$PWD/unity-build.log"
```

الناتج المحلي غير المتعقب:
`unity/Builds/Android/FamilyForceUnityPrototype.apk`.

## ما يعمل في `0.5.0-stage-one-slice`

- مشهد 2D عند 60 FPS.
- حركة Sprite Atlas بسرعة 12 FPS مع Point filtering ومن دون ضغط Android.
- قائمة واضحة بإطار اختيار تعمل عبر D-pad/العصا/ريموت لوحة المفاتيح.
- 1P أو 2P اختياريان، وشاشة اختيار Essa/Adam لا تبدأ 2P قبل تأكيد اللاعبين.
- لمس كامل للحركة وPunch/Kick/Heavy/Special/Grab/Team/Jump/Weapon/Throw.
- ثلاث موجات Grunt ثم Mini Boss من نوع Market Enforcer.
- مضرب قابل للالتقاط والضرب والرمي وإعادة الالتقاط في 1P/2P.
- hurtbox ثابت، input buffer، combo من ثلاث ضربات، hit-stop وknockback.
- مقدمة Stage 1 وStage Clear وScore ووقت وHigh Score محفوظ.
- حزمة مستقلة تسمح بتثبيته بجانب APK الحالي.

## أطالس الشخصيات المعتمدة

يعتمد المشروع الآن `Sprite Atlas` الرسمي بدل إنشاء Sprites من الشرائط وقت
التشغيل. الدفعة الأولى محصورة في Essa وAdam وأعداء Stage 1 الخمسة. لكل شخصية
Atlas مستقل داخل `Assets/FamilyForce/Resources/Atlases` حتى يستطيع المحرك تحميل
الشخصيات المقيمة في المواجهة فقط.

- 406 Sprites من أصول النسخة المنشورة `d6c317d`.
- PPU ثابت 192 وPivot سفلي مركزي.
- Point filtering، mipmaps off، rotation off، tight packing off، padding 8.
- Android RGBA32 وmax page 2048 في بوابة الجودة الأولى؛ يعاد تقييم الضغط بعد
  قياس الذاكرة بصريًا على Xiaomi Stick حتى لا نستبدل الوضوح بتوفير نظري.

```sh
python3 unity/tools/test_sprite_atlas_contract.py
```

هذا Vertical Slice قابل للاختبار، لكنه لا يستبدل بعد لعبة Android Canvas المنشورة؛
ما زالت المراحل الخمس والقصة والصوت والتكافؤ الكامل واختبارات العتاد الحقيقي مطلوبة.
