"""Small adb helper for the disposable emulator's native updater UI tests."""
import subprocess,sys,re,xml.etree.ElementTree as ET
from pathlib import Path
ADB='/Applications/Unity/Hub/Editor/6000.3.22f1/PlaybackEngines/AndroidPlayer/SDK/platform-tools/adb'
OUT=Path(__file__).resolve().parents[1]/'Builds/Updater223'
def adb(*args):return subprocess.check_output([ADB,*args])
adb('shell','uiautomator','dump','/sdcard/ff223-ui.xml')
xml=adb('shell','cat','/sdcard/ff223-ui.xml');root=ET.fromstring(xml)
if len(sys.argv)>2 and sys.argv[1]=='tap':
    wanted=sys.argv[2].casefold()
    matches=[n for n in root.iter('node') if n.get('text','').casefold()==wanted and n.get('enabled')=='true']
    assert len(matches)==1,[(n.get('text'),n.get('bounds')) for n in root.iter('node') if n.get('text')]
    b=list(map(int,re.findall(r'\d+',matches[0].get('bounds'))));adb('shell','input','tap',str((b[0]+b[2])//2),str((b[1]+b[3])//2))
else:
    name=sys.argv[1] if len(sys.argv)>1 else 'native-state'
    (OUT/(name+'.xml')).write_bytes(xml);(OUT/(name+'.png')).write_bytes(adb('exec-out','screencap','-p'))
    for n in root.iter('node'):
        if n.get('text'):print(n.get('text'),n.get('bounds'))
