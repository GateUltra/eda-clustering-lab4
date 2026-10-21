import argparse, json, os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--slides',default='all');a=ap.parse_args()
ids=[s['id'] for s in json.loads((ROOT/'source/lesson.json').read_text())] if a.slides=='all' else list(map(int,a.slides.split(',')))
with sync_playwright() as p:
    opts=dict(headless=True,args=['--no-sandbox'])
    if os.environ.get('CHROME_PATH'): opts['executable_path']=os.environ['CHROME_PATH']
    browser=p.chromium.launch(**opts);page=browser.new_page(viewport=dict(width=1280,height=720),device_scale_factor=1)
    page.goto((ROOT/'slides.html').as_uri()+'?render=1')
    errors=[]
    for i in ids:
        page.evaluate('i=>showSlide(i-1)',i);page.evaluate('document.fonts.ready')
        over=page.evaluate('''() => [...document.querySelectorAll('.point,h1,table,pre,.metric')].map(e=>({text:e.textContent,box:e.getBoundingClientRect().toJSON(),scroll:e.scrollWidth>e.clientWidth+1})).filter(e=>e.box.right>1230 || e.box.bottom>548 || e.scroll)''')
        if over:errors.append(dict(slide=i,overflow=over))
        page.screenshot(path=str(ROOT/'media/frames'/f'slide-{i:02}.png'))
    browser.close()
    (ROOT/'qa/render-check.json').write_text(json.dumps(dict(slides=ids,errors=errors),indent=2))
    print(json.dumps(dict(rendered=len(ids),errors=errors),indent=2))
