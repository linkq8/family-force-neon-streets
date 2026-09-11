"""Validate version, update signature and packaged integration evidence."""
from pathlib import Path
import hashlib,json,os,subprocess,zipfile,sys
ROOT=Path(__file__).resolve().parents[2]
SDK=Path('/Applications/Unity/Hub/Editor/6000.3.22f1/PlaybackEngines/AndroidPlayer')
clear='--clear' in sys.argv
updates='--updates' in sys.argv
smooth='--smooth' in sys.argv
controllers='--controllers' in sys.argv
tv_install='--tv-install' in sys.argv
tv_input='--tv-input' in sys.argv
repairs='--repairs' in sys.argv
arcade='--arcade' in sys.argv
filename='FamilyForceUnity-EssaClear-0.5.4.apk' if clear else 'FamilyForceUnity-EssaVideo-0.5.3.apk'
version='0.5.4-essa-clear-fast' if clear else '0.5.3-essa-video'
code=5 if clear else 4
if updates:
    filename='FamilyForceUnity-Updates-0.5.5.apk';version='0.5.5-updates';code=6;clear=True
if smooth:
    filename='FamilyForceUnity-Smooth-0.5.6.apk';version='0.5.6-smooth';code=7;clear=True;updates=True
APK=ROOT/'unity/Builds/Android'/filename
if controllers:
    filename='FamilyForceUnity-Controllers-0.5.7.apk';version='0.5.7-controllers';code=8;clear=True;updates=True;smooth=True
    APK=ROOT/'unity/Builds/Android'/filename
BT=SDK/'SDK/build-tools/36.0.0'
if tv_install:
    filename='FamilyForceUnity-TVInstall-0.5.8.apk';version='0.5.8-tv-install';code=9
    clear=updates=smooth=controllers=True
    APK=ROOT/'unity/Builds/Android'/filename
if tv_input:
    filename='FamilyForceUnity-TVInput-0.5.9.apk';version='0.5.9-tv-input';code=10
    clear=updates=smooth=controllers=tv_install=True
    APK=ROOT/'unity/Builds/Android'/filename
if repairs:
    filename='FamilyForceUnity-Repairs-0.5.10.apk';version='0.5.10-repairs';code=11
    clear=updates=smooth=controllers=tv_install=True
    APK=ROOT/'unity/Builds/Android'/filename
if arcade:
    filename='FamilyForceUnity-Arcade-0.5.11.apk';version='0.5.11-arcade';code=12
    clear=updates=smooth=controllers=tv_install=repairs=True
    APK=ROOT/'unity/Builds/Android'/filename
badging=subprocess.check_output([str(BT/'aapt2'),'dump','badging',str(APK)],text=True)
if tv_install: assert "install-location:'internalOnly'" in badging
for value in ["package: name='com.familyforce.neonstreets.unityprototype'",f"versionCode='{code}'",f"versionName='{version}'","arm64-v8a","armeabi-v7a",'leanback-launchable-activity']:
    assert value in badging,value
sig=subprocess.check_output([str(BT/'apksigner'),'verify','--verbose','--print-certs',str(APK)],text=True,env={**os.environ,'JAVA_HOME':str(SDK/'OpenJDK')})
assert '3507d2bf0998bc4e792740b9770cc4620f4112c85c2855e453a54999b7de97a0' in sig
with zipfile.ZipFile(APK) as z:
    assert z.testzip() is None
    assert all('lib/'+abi+'/libil2cpp.so' in z.namelist() for abi in ['arm64-v8a','armeabi-v7a'])
    assert not any('/photos/' in n or 'front.JPG' in n or '.keystore' in n for n in z.namelist())
    metadata=z.read('assets/bin/Data/Managed/Metadata/global-metadata.dat')
    assert (b'PracticalRetro/Essa222/clips' if clear else b'PracticalRetro/Essa220/clips') in metadata
    assert b'VideoStrike' in metadata and b'PlayKnockdown' in metadata
    if smooth: assert b'PracticalRetro/Essa225/walk' in metadata and b'FF_RENDER' in metadata
    if controllers: assert b'ControllerRouter' in metadata and b'ExtraMove' in metadata
    if updates:
        dex=b''.join(z.read(n) for n in z.namelist() if n.endswith('.dex'))
        for value in [b'Check New Updates',b'com/familyforce/updates/UpdateActivity',b'com/familyforce/updates/UpdateProvider',b'canRequestPackageInstalls',b'SHA-256']:
            assert value in dex,value
        assert b'PolicyTests' not in dex
        if tv_install: assert b'Low internal storage:' in dex
        if repairs: assert b'com/familyforce/updates/InstallResultReceiver' in dex
        assert 'android.permission.REQUEST_INSTALL_PACKAGES' in badging
result=dict(status='PASS',version=version,versionCode=code,sha256=hashlib.sha256(APK.read_bytes()).hexdigest(),sizeBytes=APK.stat().st_size,signatureMatchesPrevious=True,signing='Existing Android debug certificate; test release',abis=['arm64-v8a','armeabi-v7a'],newVideoLoaderAndCombatMethodsPresent=True)
out=ROOT/'unity/Builds'/('Arcade234' if arcade else 'Repairs232' if repairs else 'TVInput229' if tv_input else 'TVInstall228' if tv_install else 'Controller226' if controllers else 'Motion225' if smooth else 'Updater223' if updates else 'EssaClear222' if clear else 'EssaVideo221')/'apk-validation.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
