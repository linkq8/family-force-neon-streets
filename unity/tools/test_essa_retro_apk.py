"""Verify the new APK, not an older APK left in Builds/Android."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[2]
SDK=Path('/Applications/Unity/Hub/Editor/6000.3.22f1/PlaybackEngines/AndroidPlayer')
APK=ROOT/'unity/Builds/Android/FamilyForceUnity-EssaRetro-0.5.1.apk'
BUILD_TOOLS=SDK/'SDK/build-tools/36.0.0'
env=dict(os.environ,JAVA_HOME=str(SDK/'OpenJDK'))
badging=subprocess.check_output([str(BUILD_TOOLS/'aapt2'),'dump','badging',str(APK)],text=True)
for required in ["package: name='com.familyforce.neonstreets.unityprototype'",
                 "versionCode='2'","versionName='0.5.1-essa-retro'",
                 'leanback-launchable-activity',"arm64-v8a","armeabi-v7a","uses-gl-es: '0x30000'"]:
    assert required in badging,required
signature=subprocess.check_output([str(BUILD_TOOLS/'apksigner'),'verify','--verbose','--print-certs',str(APK)],text=True,env=env)
assert '3507d2bf0998bc4e792740b9770cc4620f4112c85c2855e453a54999b7de97a0' in signature,'Certificate changed; update compatibility must be reviewed'
with zipfile.ZipFile(APK) as z:
    assert z.testzip() is None
    names=z.namelist()
    assert 'lib/arm64-v8a/libil2cpp.so' in names
    assert 'lib/armeabi-v7a/libil2cpp.so' in names
    assert not any('/photos/' in n or 'front.JPG' in n or '.keystore' in n for n in names)
    metadata=z.read('assets/bin/Data/Managed/Metadata/global-metadata.dat')
    # This Unity IL2CPP metadata stores resource-path literal data as UTF-8.
    assert b'PracticalRetro/Essa198/Essa_walk' in metadata
    assert b'PracticalRetro/Essa198/Essa_combat' in metadata
data={'status':'PASS','package':'com.familyforce.neonstreets.unityprototype',
      'version_name':'0.5.1-essa-retro','version_code':2,'abis':['arm64-v8a','armeabi-v7a'],
      'sha256':hashlib.sha256(APK.read_bytes()).hexdigest(),'size_bytes':APK.stat().st_size,
      'signature_matches_previous_unity_apk':True,'signing':'Android debug certificate, test release',
      'new_essa_resource_paths_in_il2cpp':True,'zip_integrity':'PASS'}
(ROOT/'unity/Builds/EssaRetro199/apk-validation.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data))
