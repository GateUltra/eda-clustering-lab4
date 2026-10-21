"""Exercise the real static site under a project subpath, with a temporary server."""
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
import json,os,threading,re
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        path=Path(self.translate_path(self.path))
        match=re.fullmatch(r'bytes=(\d+)-(\d*)',self.headers.get('Range',''))
        if path.is_file() and match:
            total=path.stat().st_size;start=int(match[1]);end=min(int(match[2]) if match[2] else total-1,total-1)
            self.send_response(206);self.send_header('Content-Type',self.guess_type(str(path)));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Range',f'bytes {start}-{end}/{total}');self.send_header('Content-Length',str(end-start+1));self.end_headers()
            try:
                with path.open('rb') as f:
                    f.seek(start);left=end-start+1
                    while left:
                        chunk=f.read(min(65536,left));self.wfile.write(chunk);left-=len(chunk)
            except (BrokenPipeError,ConnectionResetError):pass
        else:
            try:super().do_GET()
            except (BrokenPipeError,ConnectionResetError):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT.parent)))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/{ROOT.name}/'
with sync_playwright() as p:
    opts=dict(headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
    if os.environ.get('CHROME_PATH'):opts['executable_path']=os.environ['CHROME_PATH']
    b=p.chromium.launch(**opts);page=b.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(base+'lab.html');page.locator('#run').click()
    assert 'no legal positive' in page.locator('#status').inner_text()
    assert page.locator('#parts').inner_text()=='{A, B} · size 2{C} · size 1{D, E} · size 2'
    for cap in ['3','none']:
        page.locator('#cap').select_option(cap);page.locator('#reset').click();page.locator('#run').click()
        assert page.locator('#parts').inner_text()=='{A, B, C} · size 3{D, E} · size 2'
    page.locator('#cap').select_option('2');page.locator('#k').fill('3');page.locator('#reset').click();page.locator('#run').click();assert 'target K reached' in page.locator('#status').inner_text()
    for case in ['greedy_trap','suboptimal']:
        page.locator('#case').select_option(case);page.locator('#run').click()
        assert ('no legal positive' if case=='greedy_trap' else 'target K reached') in page.locator('#status').inner_text()
    page.locator('#case').select_option('original');page.locator('#prediction').select_option('0');page.locator('#check-prediction').click();assert page.locator('#prediction-feedback').inner_text().startswith('Correct')
    for i,n in enumerate([18,5,3,8,3,3,3,3,5,3]):page.locator(f'#challenge-{i}').fill(str(n))
    page.locator('#check-all').click();assert page.locator('#score').inner_text()=='10 / 10 correct'
    page.goto(base+'quiz.html')
    for i,a in enumerate([1,1,2,1,2,3]):page.locator(f'input[name=q{i}][value="{a}"]').check()
    page.locator('#grade').click();assert page.locator('#result').inner_text()=='6 / 6 correct'
    page.goto(base+'index.html');page.wait_for_function('document.querySelector("video").readyState >= 1')
    meta=page.locator('video').evaluate('(v)=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,error:v.error})')
    assert meta['width']==1280 and meta['error'] is None
    page.locator('video').evaluate('(v)=>v.play()');page.wait_for_function('document.querySelector("video").currentTime > 0.5');page.locator('video').evaluate('(v)=>v.pause()')
    # Seek to a middle transition and near the end, then confirm decoded frames.
    for t in [212,437]:
        page.locator('video').evaluate('(v,t)=>{v.currentTime=t}',t);page.wait_for_function('(t)=>Math.abs(document.querySelector("video").currentTime-t)<.15 && document.querySelector("video").readyState>=2',arg=t)
    page.screenshot(path='/tmp/lab04-website.png',full_page=False)
    page.set_viewport_size({'width':390,'height':844});page.screenshot(path='/tmp/lab04-mobile.png',full_page=False);assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
    assert not errors,errors
    report=dict(passed=True,project_subpath='/'+ROOT.name+'/',settings=4,counterexamples=2,prediction=True,calculation_challenges='10/10 automated test, not user progress',quiz='6/6 automated test, not user progress',video_metadata=meta,video_playback=True,video_seek_middle_end=True,mobile_no_horizontal_overflow=True,page_errors=errors)
    (ROOT/'qa/browser-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));b.close()
server.shutdown()
