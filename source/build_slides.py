"""Build editable, self-contained English HTML slides (no external JS dependencies)."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
data=(ROOT/'source/lesson.json').read_text()
template=(ROOT/'source/slides-template.html').read_text()
(ROOT/'slides.html').write_text(template.replace('/*LESSON_DATA*/',data),encoding='utf-8')
print('Built slides.html')
