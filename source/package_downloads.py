from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
def pack(name,paths):
    with zipfile.ZipFile(ROOT/'downloads'/name,'w',zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            if p.is_file() and '__pycache__' not in str(p):z.write(p,p.relative_to(ROOT))
pack('per-slide-audio.zip',sorted((ROOT/'media/audio').glob('slide-*'))+[ROOT/'transcript.txt',ROOT/'source/lesson.json'])
pack('subtitles.zip',sorted((ROOT/'media/captions').glob('lab04-lesson.*')))
with zipfile.ZipFile(ROOT/'downloads/slides-editable.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in ['slides.html','source/slides-template.html']:
        z.writestr(name,(ROOT/name).read_text().replace('<a href="index.html">Course</a>',''))
    for p in [ROOT/'source/build_slides.py',ROOT/'source/make_lesson.py',ROOT/'source/lesson.json']+sorted((ROOT/'media/audio').glob('slide-*.mp3')):
        z.write(p,p.relative_to(ROOT))
    z.writestr('README.txt','Open slides.html. Left/Right arrows change slides; Listen plays the current slide. Edit source/make_lesson.py and source/slides-template.html, then run make_lesson.py and build_slides.py. Regenerate changed narration using the complete course package.')
pack('implementation.zip',[ROOT/'source'/n for n in ['reference.py','exercise.py','check_exercise.py','verify.py','graphs.json','goldens.json']]+[ROOT/'assets/engine.js',ROOT/'handout.html',ROOT/'assets/site.css'])
print('Download archives updated')
