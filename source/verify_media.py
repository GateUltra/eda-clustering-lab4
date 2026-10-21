"""Validate frozen outputs: decode, timing, font coverage and all slide images."""
import json,subprocess,tempfile
from pathlib import Path
from PIL import Image,ImageChops,ImageStat,ImageFont
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
movie=ROOT/'media/lab04-lesson.mp4'
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]))
ss=json.loads((ROOT/'source/lesson.json').read_text());times=json.loads((ROOT/'media/lab04-lesson.timings.json').read_text());cues=json.loads((ROOT/'media/lab04-lesson.cues.json').read_text());info=probe(movie)
v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
assert v['codec_name']=='h264' and a['codec_name']=='aac'
assert (v['width'],v['height'],v['pix_fmt'])==(1280,720,'yuv420p')
assert abs(float(v['duration'])-times[-1]['end'])<.05
assert abs(float(a['duration'])-float(v['duration']))<.1
assert len(times)==len(ss)==16 and len(cues)==sum(len(s['cues']) for s in ss)
font=TTFont(ROOT/'assets/fonts/NotoSansCJKsc-Regular.otf');chars=set().union(*(set(t.cmap) for t in font['cmap'].tables))
assert not {c for q in cues for c in q['zh'] if ord(c) not in chars}
for x,y in zip(cues,cues[1:]):assert x['end']<=y['start']+.001
for s,t in zip(ss,times):
    meta=json.loads((ROOT/f'media/audio/slide-{s["id"]:02}.json').read_text())
    assert meta['text']==' '.join(c['en'] for c in s['cues'])
    assert abs(float(probe(ROOT/f'media/audio/slide-{s["id"]:02}.mp3')['format']['duration'])-meta['cues'][-1]['end'])<.2
    own=[c for c in cues if c['slide']==s['id']]
    assert len(own)==len(s['cues']) and own[0]['start']>=t['start'] and own[-1]['end']<t['end']
    assert all(c['end']>c['start'] for c in own)
# Decode the entire media, not only the container headers.
subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'],check=True)
checks=[]
points=[(t['slide'],(t['start']+t['end'])/2) for t in times]
points += [(1,.2),(8,times[7]['end']-.12),(9,times[8]['start']+.12),(16,times[-1]['end']-.12)]
with tempfile.TemporaryDirectory() as temp:
    for n,t in points:
        p=Path(temp)/'frame.png'
        subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(movie),'-frames:v','1','-y',str(p)],check=True)
        actual=Image.open(p).convert('RGB').crop((0,0,1280,590));expected=Image.open(ROOT/f'media/frames/slide-{n:02}.png').convert('RGB').crop((0,0,1280,590))
        error=sum(ImageStat.Stat(ImageChops.difference(actual,expected)).mean)/3
        assert error<5,(n,t,error) # H.264 chroma subsampling changes RGB values slightly.
        distances=[]
        for candidate in range(1,17):
            frame=Image.open(ROOT/f'media/frames/slide-{candidate:02}.png').convert('RGB').crop((0,0,1280,590))
            distances.append(sum(ImageStat.Stat(ImageChops.difference(actual,frame)).mean)/3)
        assert distances.index(min(distances))+1==n,(n,t,distances)
        checks.append(dict(slide=n,time=round(t,3),mean_absolute_pixel_error=round(error,4)))
report=dict(passed=True,duration_seconds=float(v['duration']),audio_duration_seconds=float(a['duration']),slides=len(ss),bilingual_cues=len(cues),video_codec=v['codec_name'],audio_codec=a['codec_name'],full_decode=True,no_caption_overlap=True,chinese_glyph_coverage=True,slide_frame_checks=checks)
(ROOT/'qa/media-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='slide_frame_checks'},indent=2))
