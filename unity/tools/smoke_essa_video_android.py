"""Operate the installed test APK on the connected Android emulator."""
from pathlib import Path
import subprocess,time,json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'unity/Builds/EssaVideo221'
ADB='/Applications/Unity/Hub/Editor/6000.3.22f1/PlaybackEngines/AndroidPlayer/SDK/platform-tools/adb'
def call(*args):return subprocess.check_output([ADB,*args])
def tap(x,y):call('shell','input','tap',str(x),str(y))
rec=subprocess.Popen([ADB,'shell','screenrecord','--time-limit','20','/sdcard/essa221-actions.mp4'])
time.sleep(1)
call('shell','input','swipe','80','560','80','560','1300')
call('shell','input','swipe','250','560','250','560','1500')
tap(1073,620);time.sleep(1.5)
tap(953,620);time.sleep(1.7)
call('shell','input','swipe','80','560','80','560','1000')
tap(1073,620);time.sleep(1.5)
tap(953,620);time.sleep(1.7)
rec.wait(timeout=30)
call('pull','/sdcard/essa221-actions.mp4',str(OUT/'android-actions.mp4'))
(OUT/'android-after.png').write_bytes(call('exec-out','screencap','-p'))
logs=call('logcat','-d','-s','Unity').decode(errors='replace')
(OUT/'android-unity.log').write_text(logs)
assert 'idle=12 walk=12 sprite=True' in logs
assert 'NullReferenceException' not in logs and 'Missing Essa220 atlas' not in logs
report=dict(status='SMOKE_COMMANDS_PASS',installedVersion='0.5.3-essa-video',touchCommands=['left','right','punch','kick'],newIdleAndWalkLoaded=True,missingAtlasOrNullExceptions=False,visualReviewRequired=True,physicalDeviceTested=False)
(OUT/'android-smoke.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
