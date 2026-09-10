"""Copy only reviewed runtime atlases, preserving page bytes and provenance."""
import json, shutil, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'art-pipeline/builds/Essa/video-220-v2/runtime-256'
DEST=ROOT/'unity/Assets/FamilyForce/Resources/PracticalRetro/Essa220'
DEST.mkdir(parents=True,exist_ok=True)
m=json.loads((SRC/'manifest.json').read_text())
clips=[]
for name,c in m['clips'].items():
    v=c['variants']['256'];pages=[]
    for j,page in enumerate(v['pages']):
        source=SRC/c['path']/page['file'];filename=f'{name}_{j:02}.png'
        assert hashlib.sha256(source.read_bytes()).hexdigest()==page['sha256']
        shutil.copy2(source,DEST/filename)
        pages.append(filename[:-4])
    clips.append(dict(action='punch' if name=='punch_combo' else name,pages=pages,
        frames=[dict(page=f['page'],rect=f['rectBottomLeft'],seconds=f['durationMs']/1000) for f in v['frames']],
        sourceSha256=c['sourceVideoSha256']))
(DEST/'clips.json').write_text(json.dumps(dict(version=220,alpha='processed',pixelsPerUnit=150,pivot=[7/12,0.125],clips=clips),indent=2)+'\n')
print('Imported',len(clips),'clips,',sum(len(c['frames']) for c in clips),'frames')
