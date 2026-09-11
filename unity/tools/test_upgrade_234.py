"""Upgrade the full game on the disposable emulator; never uninstall or clear data."""
import subprocess, json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ADB='/Applications/Unity/Hub/Editor/6000.3.22f1/PlaybackEngines/AndroidPlayer/SDK/platform-tools/adb'
PACKAGE='com.familyforce.neonstreets.unityprototype'
OUT=ROOT/'Builds/Arcade234';OUT.mkdir(parents=True,exist_ok=True)
def adb(*args):return subprocess.check_output([ADB,'-s','emulator-5554',*args],timeout=120)
assert adb('shell','getprop','ro.kernel.qemu').strip()==b'1','Emulator only'
adb('shell','am','force-stop',PACKAGE)
before=adb('shell','dumpsys','package',PACKAGE).decode()
assert 'versionName=0.5.10-repairs' in before,'Require actual full 0.5.10 game'
prefs='/data/user/0/'+PACKAGE+'/shared_prefs/'
names=adb('shell','ls',prefs).decode().splitlines()
player=[name for name in names if 'playerprefs' in name.lower()]
assert player,'Require real game save evidence, not an empty probe'
saved={name:hashlib.sha256(adb('shell','cat',prefs+name)).hexdigest() for name in player}
install=adb('install','-r',str(ROOT/'Builds/Android/FamilyForceUnity-Arcade-0.5.11.apk')).decode()
assert 'Success' in install,install
after=adb('shell','dumpsys','package',PACKAGE).decode()
assert 'versionName=0.5.11-arcade' in after and 'versionCode=12' in after
for name,digest in saved.items():assert hashlib.sha256(adb('shell','cat',prefs+name)).hexdigest()==digest,'Save changed: '+name
result=dict(status='PASS',fromVersion='0.5.10-repairs',toVersion='0.5.11-arcade',method='ADB package installer -r; actual full game',uninstalled=False,savesPreserved=saved,physicalDevice=False)
(OUT/'full-game-upgrade.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
