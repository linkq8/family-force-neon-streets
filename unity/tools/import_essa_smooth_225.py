"""Restore 35 original walk frames with request220's unchanged matte/transform."""
import importlib.util,json,hashlib,math
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('video220',ROOT/'art-pipeline/build_video_package_220.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
src=ROOT/'art-pipeline/builds/Essa/video-220-v2';old=json.loads((src/'manifest.json').read_text())['clips']['walk']
video=src/'sources/walk.mp4';assert p.sha(video)==old['sourceVideoSha256']
dest=ROOT/'unity/Assets/FamilyForce/Resources/PracticalRetro/Essa225';dest.mkdir(parents=True,exist_ok=True)
review=ROOT/'unity/Builds/Motion225';review.mkdir(parents=True,exist_ok=True)
t=old['fixedSourceTransform'];s=t['scale384'];ax,ay=t['anchorSourcePx'];frames=[]
for i,rgb in p.decode_selected(video,list(range(24,59)),p.probe(video)).items():
    f=p.matte(rgb).transform((384,384),Image.Transform.AFFINE,(1/s,0,ax-224/s,0,1/s,ay-336/s),Image.Resampling.BICUBIC)
    box=f.getchannel('A').getbbox();assert box and min(box)>0 and max(box)<384
    frames.append(f);print('Source frame',i,flush=True)
assert len({hashlib.sha256(f.tobytes()).hexdigest() for f in frames})==35
for j,r in enumerate(old['frames']):
    assert frames[r['sourceFrame']-24].tobytes()==Image.open(src/old['path']/'frames-384'/f'{j:03}.png').tobytes()
pages=[];cells=[]
for start in range(0,35,16):
    chunk=frames[start:start+16];height=math.ceil(len(chunk)/4)*384
    sheet=Image.new('RGBA',(1536,height));name=f'walk_{len(pages):02}';pages.append(name)
    for j,f in enumerate(chunk):
        x,y=j%4*384,j//4*384;sheet.paste(f,(x,y))
        cells.append(dict(page=len(pages)-1,rect=[x,height-y-384,384,384],seconds=1/24/1.35,sourceFrame=24+start+j))
        assert sheet.crop((x,y,x+384,y+384)).tobytes()==f.tobytes()
    sheet.save(dest/(name+'.png'))
(dest/'walk.json').write_text(json.dumps(dict(clips=[dict(action='walk',pages=pages,frames=cells)]),indent=2)+'\n')
p.preview(frames,[1000/24/1.35/1.35]*35,review/'walk-preview.gif',True)
(review/'source-validation.json').write_text(json.dumps(dict(status='PASS',sourceSha256=p.sha(video),frames=35,uniqueFrames=35,original12PixelIdentical=True,constantTransform=t,alpha='processed request220 method',packedPixelEquality=True),indent=2)+'\n')
