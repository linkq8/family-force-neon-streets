# Unity0.5.1 — عيسى C-retro

APK تجريبية جديدة لحزمة عيسى198، وليست تحديثًا لمحركAndroid Canvas القديم.
تُثبّت فوق نسخةUnity السابقة بنفس معرفالتطبيق والتوقيع، معversionCode2.

- عيسى:20 رسمة متميزة للمشي والقتال، بشفافية معالجة ومحاور ثابتة.
- دعمARM64 وARMv7، الهاتف وAndroidTV، مع بقاء التحكم والمرحلة الحالية.
- حركات القتال تعتمد مفاتيح رترو مختصرة؛ بعض الحركات تشارك الوضعيات.
- يبقى صقل المشي وتفاصيل الشعر وقبضةالسلاح مطلوبًا؛ لا ادعاء برسومنهائية.

البناء بالمحررUnity6000.3.22f1 عبر:
`FamilyForce.Unity.Editor.BuildFamilyForce.BuildEssaRetroRelease`
والناتج`unity/Builds/Android/FamilyForceUnity-EssaRetro-0.5.1.apk`.
فحصAPK المستقل: `python3 unity/tools/test_essa_retro_apk.py`.
تستخدم النسخة توقيعAndroid Debug نفسه المستخدم فيAPKUnityالسابقة؛ ليستحزمةPlayStore.

تصحيح تجهيز البناء: دعمAndroid المثبت موجود تحت مجلدالمحرر
`6000.3.22f1/PlaybackEngines/AndroidPlayer` خارجUnity.app، وليسداخله.
لم يتطلبالإصدارشراءخدمةأوتوليدصورإضافية.
