"""Capture quick attacks in the actual APK; inspect video, not just frame count."""
import subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Builds/Arcade234';OUT.mkdir(parents=True,exist_ok=True)
ADB='/Applications/Unity/Hub/Editor/6000.3.22f1/PlaybackEngines/AndroidPlayer/SDK/platform-tools/adb'
def adb(*args):return subprocess.check_output([ADB,'-s','emulator-5554',*args],timeout=30)
adb('shell','input','tap','640','248');time.sleep(.6)
adb('shell','input','tap','450','395');time.sleep(3.1)
record=subprocess.Popen([ADB,'-s','emulator-5554','shell','screenrecord','--time-limit','6','/sdcard/arcade234.mp4'])
time.sleep(.4)
for x in [1073,1073,953,1073,953]:
    adb('shell','input','tap',str(x),'620');time.sleep(.36)
record.wait(timeout=15)
adb('pull','/sdcard/arcade234.mp4',str(OUT/'android-attacks.mp4'))
logs=adb('logcat','-d','-s','Unity').decode(errors='replace');(OUT/'android-attacks.log').write_text(logs)
assert 'NullReferenceException' not in logs
print('Attack video captured; visual review required.')
