"""Burn real-timed bilingual captions into a standard H.264/AAC MP4."""
import argparse,json,math,subprocess
from pathlib import Path
from PIL import ImageFont
ROOT=Path(__file__).resolve().parents[1]
FPS=25
def run(args):subprocess.run(args,check=True)
def duration(p):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(p)]))
def stamp(t,ass=False,vtt=False):
    if ass:
        n=round(t*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
    n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02}'+('.' if vtt else ',')+f'{n%1000:03}'
def assfile(cues,path):
    head='''[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: English,DejaVu Sans,24,&H00FFFFFF,&H00FFFFFF,&H00102B3B,&H00102B3B,0,0,0,0,100,100,0,0,1,0,0,2,45,45,68,1
Style: Chinese,Noto Sans CJK SC,32,&H00E7EEEE,&H00E7EEEE,&H00102B3B,&H00102B3B,0,0,0,0,100,100,0,0,1,0,0,2,45,45,22,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    for c in cues:
        for lang,style in [('en','English'),('zh','Chinese')]:
            head+=f'Dialogue: 0,{stamp(c["start"],True)},{stamp(c["end"],True)},{style},,0,0,0,,{{\\an5\\pos(640,{628 if lang=='en' else 677})}}{c[lang]}\n'
    path.write_text(head,encoding='utf-8')
def subtitle_files(cues,prefix):
    for lang in ['en','zh','bilingual']:
        for ext in ['srt','vtt']:
            vtt=ext=='vtt';out='WEBVTT\n\n' if vtt else ''
            for i,c in enumerate(cues,1):
                text=c['en']+'\n'+c['zh'] if lang=='bilingual' else c[lang]
                out+=f'{i}\n{stamp(c["start"],vtt=vtt)} --> {stamp(c["end"],vtt=vtt)}\n{text}\n\n'
            (ROOT/'media/captions'/f'{prefix}.{lang}.{ext}').write_text(out,encoding='utf-8')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--slides',default='all');ap.add_argument('--output',default='lab04-lesson.mp4');a=ap.parse_args()
    ss=json.loads((ROOT/'source/lesson.json').read_text())
    if a.slides!='all':ss=[s for s in ss if s['id'] in list(map(int,a.slides.split(','))) ]
    outdir=ROOT/'media/segments';outdir.mkdir(exist_ok=True)
    allcues=[];timings=[];offset=0;segments=[]
    for s in ss:
        name=f'slide-{s["id"]:02}';mp3=ROOT/'media/audio'/f'{name}.mp3'
        raw=duration(mp3);pad=.45;total=math.ceil((raw+pad)*FPS)/FPS
        meta=json.loads(mp3.with_suffix('.json').read_text());cues=meta['cues']
        for j in range(len(cues)-1): cues[j]['end']=min(cues[j]['end'],cues[j+1]['start'])
        assert cues[-1]['end']<=raw+.15
        ass=ROOT/'media/captions'/f'{name}.ass';assfile(cues,ass)
        output=outdir/f'{name}.mp4'
        vf=f"ass=filename='{ass.as_posix()}':fontsdir='{(ROOT/'assets/fonts').as_posix()}'"
        run(['ffmpeg','-hide_banner','-loglevel','error','-y','-loop','1','-framerate',str(FPS),'-i',str(ROOT/'media/frames'/f'{name}.png'),'-i',str(mp3),'-vf',vf,'-af','apad','-t',str(total),'-c:v','libx264','-preset','veryfast','-tune','stillimage','-crf','22','-pix_fmt','yuv420p','-r',str(FPS),'-c:a','aac','-b:a','128k','-ar','48000','-ac','1','-video_track_timescale','25000',str(output)])
        segments.append(output)
        for c in cues:allcues.append(dict(**{k:v for k,v in c.items() if k not in ['start','end']},start=c['start']+offset,end=c['end']+offset,slide=s['id']))
        timings.append(dict(slide=s['id'],start=offset,end=offset+total,speech_file_duration=raw,video_duration=total,captions=len(cues)))
        offset+=total;print(f'{name}: {total:.2f} sec',flush=True)
    concat=outdir/'concat.txt';concat.write_text('\n'.join(f"file '{p.as_posix()}'" for p in segments))
    # Re-encode audio once at concatenation to avoid AAC priming gaps per segment.
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-c:v','copy','-c:a','aac','-b:a','128k','-movflags','+faststart',str(ROOT/'media'/a.output)])
    prefix=Path(a.output).stem;subtitle_files(allcues,prefix)
    assfile(allcues,ROOT/'media/captions'/f'{prefix}.ass')
    (ROOT/'media'/f'{prefix}.timings.json').write_text(json.dumps(timings,indent=2))
    (ROOT/'media'/f'{prefix}.cues.json').write_text(json.dumps(allcues,ensure_ascii=False,indent=2))
    print(f'VIDEO_OK {offset:.2f}s {len(ss)} slides {len(allcues)} bilingual cues')
if __name__=='__main__':main()
