"""Validate version, update signature and packaged integration evidence."""
from pathlib import Path
import hashlib,json,os,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[2]
SDK=Path('/Applications/Unity/Hub/Editor/6000.3.22f1/PlaybackEngines/AndroidPlayer')
APK=ROOT/'unity/Builds/Android/FamilyForceUnity-EssaVideo-0.5.3.apk'
BT=SDK/'SDK/build-tools/36.0.0'
badging=subprocess.check_output([str(BT/'aapt2'),'dump','badging',str(APK)],text=True)
for value in ["package: name='com.familyforce.neonstreets.unityprototype'","versionCode='4'","versionName='0.5.3-essa-video'","arm64-v8a","armeabi-v7a",'leanback-launchable-activity']:
    assert value in badging,value
sig=subprocess.check_output([str(BT/'apksigner'),'verify','--verbose','--print-certs',str(APK)],text=True,env={**os.environ,'JAVA_HOME':str(SDK/'OpenJDK')})
assert '3507d2bf0998bc4e792740b9770cc4620f4112c85c2855e453a54999b7de97a0' in sig
with zipfile.ZipFile(APK) as z:
    assert z.testzip() is None
    assert all('lib/'+abi+'/libil2cpp.so' in z.namelist() for abi in ['arm64-v8a','armeabi-v7a'])
    assert not any('/photos/' in n or 'front.JPG' in n or '.keystore' in n for n in z.namelist())
    metadata=z.read('assets/bin/Data/Managed/Metadata/global-metadata.dat')
    assert b'PracticalRetro/Essa220/clips' in metadata
    assert b'VideoStrike' in metadata and b'PlayKnockdown' in metadata
result=dict(status='PASS',version='0.5.3-essa-video',versionCode=4,sha256=hashlib.sha256(APK.read_bytes()).hexdigest(),sizeBytes=APK.stat().st_size,signatureMatchesPrevious=True,signing='Existing Android debug certificate; test release',abis=['arm64-v8a','armeabi-v7a'],newVideoLoaderAndCombatMethodsPresent=True)
out=ROOT/'unity/Builds/EssaVideo221/apk-validation.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
