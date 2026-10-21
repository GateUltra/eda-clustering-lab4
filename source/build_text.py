import html,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ss=json.loads((ROOT/'source/lesson.json').read_text())
(ROOT/'assets/lesson-data.js').write_text('const LESSON_DATA='+json.dumps(ss,ensure_ascii=False)+';',encoding='utf-8')
(ROOT/'assets/graphs.js').write_text('const GRAPHS='+(ROOT/'source/graphs.json').read_text()+';',encoding='utf-8')
body=''
plain='Lab 4: Size-constrained agglomerative clustering\nEnglish narration transcript\nVoice: en-US-JennyNeural; rate: -5%\n\n'
for s in ss:
    title=s['title'].replace('\n',' ')
    body+=f'<article><h2>{s["id"]}: {html.escape(title)}</h2><audio controls preload="none" src="media/audio/slide-{s["id"]:02}.mp3"></audio>'
    plain+=f'Slide {s["id"]}: {title}\n'
    for c in s['cues']:
        body+=f'<p>{html.escape(c["en"])}</p>';plain+=c['en']+'\n'
    plain+='\n';body+='</article>'
(ROOT/'transcript.txt').write_text(plain,encoding='utf-8')
(ROOT/'transcript.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>English transcript · Lab 4</title><link rel="stylesheet" href="assets/site.css"><header><strong>Lab 4 / English transcript</strong><nav><a href="index.html">Course</a><a href="slides.html">Slides</a><a href="handout.html">Handout</a></nav></header><main class="lesson-transcript"><h1>English narration transcript</h1><p>Final narration, organized by slide. Each audio player contains that slide’s synthesized English speech.</p><a href="transcript.txt" download>Download plain-text transcript</a>'''+body+'</main></html>',encoding='utf-8')
print('Text pages and website data built')
