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

## ما يعمل في النموذج الأول

- مشهد 2D عند 60 FPS.
- عرض strip من 12 صورة بسرعة 12 FPS مع Point filtering ومن دون ضغط Android.
- قائمة واضحة بإطار اختيار تعمل عبر D-pad/العصا/ريموت لوحة المفاتيح.
- حركة P1 ودعم ضربة اختبارية.
- حزمة مستقلة تسمح بتثبيته بجانب APK الحالي.

هذا النموذج ليس Release ولا يحتوي بعد على القتال الكامل أو المراحل أو P2.
