"""Android kernel uinput smoke; virtual controller, NOT physical certification."""
import subprocess,time,json
from pathlib import Path
ADB='/Applications/Unity/Hub/Editor/6000.3.22f1/PlaybackEngines/AndroidPlayer/SDK/platform-tools/adb'
OUT=Path(__file__).resolve().parents[1]/'Builds/Controller226'
OUT.mkdir(parents=True,exist_ok=True)
def adb(*args):return subprocess.check_output([ADB,*args],timeout=40)
def shot(name):(OUT/name).write_bytes(adb('exec-out','screencap','-p'))
p=subprocess.Popen([ADB,'shell','uinput','-'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
def send(command,**kw):p.stdin.write(json.dumps(dict(id=1,command=command,**kw))+'\n');p.stdin.flush()
def event(kind,code,value):send('inject',events=[kind,code,value,0,0,0])
try:
    send('register',name='FF226 Virtual Xbox',vid=0x045e,pid=0x028e,bus='usb',configuration=[dict(type=100,data=[1,3]),dict(type=101,data=[304,305,307,308,310,311,314,315,317,318]),dict(type=103,data=[0,1,16,17])],abs_info=[dict(code=c,info=dict(value=0,minimum=-32768 if c<2 else -1,maximum=32767 if c<2 else 1,fuzz=0,flat=0,resolution=0)) for c in [0,1,16,17]])
    time.sleep(4)
    (OUT/'android-input-devices.txt').write_bytes(adb('shell','dumpsys','input'))
    adb('shell','input','tap','640','365');time.sleep(1)
    event(3,0,32767);time.sleep(1);shot('controller-right.png')
    event(3,0,-32768);time.sleep(1);shot('controller-left.png')
    event(3,0,0);event(1,304,1);time.sleep(.4);shot('controller-button.png');event(1,304,0)
    adb('shell','input','tap','640','547');time.sleep(.5)
    adb('shell','input','tap','640','248');time.sleep(.5)
    event(1,304,1);time.sleep(.2);event(1,304,0);time.sleep(5)
    event(3,0,32767);time.sleep(2);shot('controller-gameplay-right.png')
    event(3,0,-32768);time.sleep(2);shot('controller-gameplay-left.png')
    event(3,0,0)
finally:
    p.stdin.close()
    p.wait(timeout=15)
    (OUT/'uinput.log').write_text(p.stdout.read())
    (OUT/'android-unity.log').write_bytes(adb('logcat','-d','-s','Unity'))
print('Captured virtual-controller evidence; inspect screenshots and logs before marking PASS.')
