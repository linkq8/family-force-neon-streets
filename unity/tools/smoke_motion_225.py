"""Record actual render submissions and touch movement on the Android emulator."""
from pathlib import Path
import subprocess,time,json,re
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Builds/Motion225'
ADB='/Applications/Unity/Hub/Editor/6000.3.22f1/PlaybackEngines/AndroidPlayer/SDK/platform-tools/adb'
def call(*args):return subprocess.check_output([ADB,*args],timeout=30)
def hold(x,y,ms):call('shell','input','swipe',str(x),str(y),str(x),str(y),str(ms))
record=subprocess.Popen([ADB,'shell','screenrecord','--time-limit','16','/sdcard/motion225.mp4'])
time.sleep(.5)
# A small stick deflection (~25%) must remain a walk, not slow motion.
hold(140,560,1100);hold(193,560,1300)
hold(80,560,850);hold(250,560,1000)
hold(167,520,700);hold(167,600,700)
call('shell','input','tap','1073','620');time.sleep(.8)
call('shell','input','tap','953','620');time.sleep(.9)
record.wait(timeout=25);call('pull','/sdcard/motion225.mp4',str(OUT/'android-motion.mp4'))
logs=call('logcat','-d','-s','Unity').decode(errors='replace');(OUT/'render.log').write_text(logs)
assert 'idle=12 walk=35 sprite=True' in logs
assert 'NullReferenceException' not in logs
rows=re.findall(r'FF_RENDER Render (\d+) FPS \| poses (\d+)/s sprite=(\S+) frame=(\d+)/(\d+) moving=(\w+)',logs)
walk=[dict(renderFps=int(r[0]),poseChanges=int(r[1]),sprite=r[2],frame=int(r[3])) for r in rows if r[2].startswith('Essa225_walk') and r[-1]=='True']
assert walk,'No actual walking render samples captured'
(OUT/'android-render-validation.json').write_text(json.dumps(dict(status='PASS',installedVersion='0.5.6-smooth',walkFrames=35,walkSamples=walk,measurement='camera render submissions; video recorded separately',physicalUserDevice=False),indent=2)+'\n')
print(json.dumps(walk))
