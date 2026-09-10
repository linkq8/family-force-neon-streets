"""Higher-resolution source pages, constant world scale, explicit playback rates."""
import json,shutil,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'art-pipeline/builds/Essa/video-220-v2'
DEST=ROOT/'unity/Assets/FamilyForce/Resources/PracticalRetro/Essa222'
DEST.mkdir(parents=True,exist_ok=True)
rates={'idle':1.15,'walk':1.35,'punch_combo':2.0,'kick':2.2,'knockdown':1.8,'block':1.6}
m=json.loads((SRC/'manifest.json').read_text());clips=[]
for name,rate in rates.items():
    c=m['clips'][name];v=c['variants']['384'];pages=[]
    for j,page in enumerate(v['pages']):
        source=SRC/c['path']/page['file'];filename=f'{name}_{j:02}.png'
        assert hashlib.sha256(source.read_bytes()).hexdigest()==page['sha256']
        shutil.copy2(source,DEST/filename);pages.append(filename[:-4])
    clips.append(dict(action='punch' if name=='punch_combo' else name,pages=pages,playbackRate=rate,
        frames=[dict(page=f['page'],rect=f['rectBottomLeft'],seconds=f['durationMs']/1000/rate,sourceSeconds=f['durationMs']/1000) for f in v['frames']],sourceSha256=c['sourceVideoSha256']))
(DEST/'clips.json').write_text(json.dumps(dict(version=222,alpha='processed',pixelsPerUnit=225,pivot=[7/12,.125],clips=clips),indent=2)+'\n')
print('Imported 384px clips; rates',rates)
