"""Generate one MP3 and real speech boundary timestamps per slide."""
import asyncio, argparse, importlib, json, os, re, subprocess
from pathlib import Path
import edge_tts
ROOT=Path(__file__).resolve().parents[1]
VOICE='en-US-JennyNeural'
RATE='-5%'
def norm(s): return re.sub(r'[^a-z0-9]','',s.lower())
async def one(s, force=False):
    stem=ROOT/'media/audio'/f'slide-{s["id"]:02}'
    mp3=stem.with_suffix('.mp3'); meta=stem.with_suffix('.json')
    text=' '.join(c['en'] for c in s['cues'])
    if not force and mp3.exists() and meta.exists() and json.loads(meta.read_text())['text']==text:
        print(f'cached {s["id"]}',flush=True);return
    # Extend normal public roots with the runtime-provided trusted CA, if supplied.
    ca=os.environ.get('SSL_CERT_FILE')
    if ca: importlib.import_module('edge_tts.communicate')._SSL_CTX.load_verify_locations(ca)
    for attempt in range(3):
        boundaries=[]
        try:
            t=edge_tts.Communicate(text,voice=VOICE,rate=RATE,boundary='SentenceBoundary',proxy=os.environ.get('HTTPS_PROXY'))
            with mp3.open('wb') as f:
                async for chunk in t.stream():
                    if chunk['type']=='audio': f.write(chunk['data'])
                    elif chunk['type']=='SentenceBoundary': boundaries.append(chunk)
            assert len(boundaries)==len(s['cues']), (s['id'],boundaries)
            cues=[]
            for c,b in zip(s['cues'],boundaries):
                assert norm(c['en'])==norm(b['text']), (c,b)
                cues.append(dict(**c,start=b['offset']/1e7,end=(b['offset']+b['duration'])/1e7))
            duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(mp3)]))
            assert cues[-1]['end'] <= duration + .15, f'Incomplete audio: {duration} sec versus final speech timestamp {cues[-1]["end"]}'
            meta.write_text(json.dumps(dict(voice=VOICE,rate=RATE,text=text,cues=cues,boundaries=boundaries),ensure_ascii=False,indent=2),encoding='utf-8')
            print(f'synthesized {s["id"]}: {len(cues)} aligned cues',flush=True)
            return
        except Exception:
            if attempt==2:raise
            await asyncio.sleep(1)
async def main():
    ap=argparse.ArgumentParser();ap.add_argument('--slides',default='all');ap.add_argument('--force',action='store_true');a=ap.parse_args()
    slides=json.loads((ROOT/'source/lesson.json').read_text())
    if a.slides!='all': slides=[s for s in slides if s['id'] in [int(x) for x in a.slides.split(',')]]
    sem=asyncio.Semaphore(3)
    async def limited(s):
        async with sem:await one(s,a.force)
    await asyncio.gather(*(limited(s) for s in slides))
if __name__=='__main__':asyncio.run(main())
