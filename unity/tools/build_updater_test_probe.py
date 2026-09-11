"""Build a LOCAL-ONLY v0.5.4 probe of the real updater to test upgrade to v0.5.5.

Installed only on the disposable emulator. Same game ID/debug signing preserves its
existing data. This APK is not the game and MUST NOT be published or user-delivered.
"""
from pathlib import Path
import subprocess, tempfile, zipfile, os

ROOT=Path(__file__).resolve().parents[1]
SDK=Path('/Applications/Unity/Hub/Editor/6000.3.22f1/PlaybackEngines/AndroidPlayer')
BT=SDK/'SDK/build-tools/36.0.0'
JDK=SDK/'OpenJDK/bin'
ANDROID=SDK/'SDK/platforms/android-36/android.jar'
OUT=ROOT/'Builds/Updater223'
OUT.mkdir(parents=True,exist_ok=True)
def run(*args):subprocess.run(list(map(str,args)),check=True,env={**os.environ,'JAVA_HOME':str(SDK/'OpenJDK')})
with tempfile.TemporaryDirectory(prefix='ff-update-probe-') as tmp:
    p=Path(tmp);classes=p/'classes';classes.mkdir()
    run(JDK/'javac','-source','8','-target','8','-classpath',ANDROID,'-d',classes,
        *(ROOT/'android-updater/src').glob('**/*.java'),ROOT/'android-updater/tests/PolicyTests.java')
    jar=p/'classes.jar';run(JDK/'jar','cf',jar,'-C',classes,'.')
    run(BT/'d8','--lib',ANDROID,'--min-api','25','--output',p,jar)
    manifest=(ROOT/'android-updater/AndroidManifest.xml').read_text().replace('package="com.familyforce.updates"','package="com.familyforce.neonstreets.unityprototype" android:versionCode="5" android:versionName="0.5.4-updater-QA"')
    manifest=manifest.replace('<application>','<uses-sdk android:minSdkVersion="25" android:targetSdkVersion="34"/><instrumentation android:name="com.familyforce.updates.PolicyTests" android:targetPackage="com.familyforce.neonstreets.unityprototype"/><application android:debuggable="true" android:label="Family Force updater QA">')
    manifest=manifest.replace('${applicationId}','com.familyforce.neonstreets.unityprototype')
    # Explicit test launch from adb; provider remains non-exported.
    manifest=manifest.replace('android:exported="false"\n            android:theme','android:exported="true"\n            android:theme')
    (p/'AndroidManifest.xml').write_text(manifest)
    unsigned=p/'unsigned.apk';run(BT/'aapt','package','-f','-M',p/'AndroidManifest.xml','-I',ANDROID,'-F',unsigned)
    with zipfile.ZipFile(unsigned,'a') as z:z.write(p/'classes.dex','classes.dex')
    apk=OUT/'LOCAL-ONLY-UpdaterProbe-0.5.4.apk'
    run(BT/'zipalign','-f','4',unsigned,apk)
    run(BT/'apksigner','sign','--ks','/Users/essa/.android/debug.keystore','--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android',apk)
print(apk)
