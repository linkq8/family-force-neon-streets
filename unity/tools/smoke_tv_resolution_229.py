"""Verify the 720p render cap on an emulated 1080p display; no TV certification."""
import subprocess,time
from pathlib import Path
ADB='/Applications/Unity/Hub/Editor/6000.3.22f1/PlaybackEngines/AndroidPlayer/SDK/platform-tools/adb'
OUT=Path(__file__).resolve().parents[1]/'Builds/TVInput229'
def adb(*args):return subprocess.check_output([ADB,*args],timeout=40)
try:
    adb('shell','wm','size','1080x1920')
    adb('shell','am','force-stop','com.familyforce.neonstreets.unityprototype')
    adb('shell','am','start','-n','com.familyforce.neonstreets.unityprototype/com.unity3d.player.UnityPlayerGameActivity')
    time.sleep(15)
    adb('shell','input','tap','960','548');time.sleep(1)
    (OUT/'1080-display-input-test.png').write_bytes(adb('exec-out','screencap','-p'))
    (OUT/'1080-display-surface.txt').write_bytes(adb('shell','dumpsys','SurfaceFlinger'))
finally:
    adb('shell','wm','size','reset')
print('Captured resolution evidence; inspect Render dimensions in Input Test.')
