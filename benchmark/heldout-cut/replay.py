"""Run from any directory. Requires Python numpy, pillow, playwright, Chrome, ffmpeg."""
import argparse
import base64
import functools
import hashlib
import http.server
import json
import os
import subprocess
import tempfile
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright
from score import summarize

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--three', type=Path, default=ROOT/'node_modules/three')
parser.add_argument('--out', type=Path, default=ROOT/'output/heldout-cut')
parser.add_argument('--shot', type=Path, default=HERE/'shot.json')
parser.add_argument('--patch', type=Path, default=HERE/'challenger.patch')
parser.add_argument('--clip-label', default='Challenger  ·  Gallery brightness guard')
args = parser.parse_args()
S = json.loads(args.shot.read_text())
S['clip_label'] = args.clip_label
out = args.out.resolve()
out.mkdir(parents=True, exist_ok=True)
for line in (HERE/'freeze.sha256').read_text().splitlines():
    digest, path = line.split()
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

with tempfile.TemporaryDirectory() as tmp, sync_playwright() as pw:
    site = Path(tmp)
    with subprocess.Popen(['git','archive',S['baseline'],'index.html','src','assets','contact-bvh.js','radiance-grid.js'],cwd=ROOT,stdout=subprocess.PIPE) as arc:
        subprocess.run(['tar','-x','-C',tmp],stdin=arc.stdout,check=True)
        assert arc.wait()==0
    base = (site/'index.html').read_bytes()
    shipping_contact = (site/'contact-bvh.js').read_bytes()
    subprocess.run(['patch','-p1','-i',str(args.patch.resolve())],cwd=site,check=True)
    for name,html in [('challenger',(site/'index.html').read_bytes()),('shipping',base)]:
        variant_site = site/name
        variant_site.mkdir()
        for shared in ['src','assets','radiance-grid.js']:
            (variant_site/shared).symlink_to(site/shared)
        contact = shipping_contact if name=='shipping' else (site/'contact-bvh.js').read_bytes()
        (variant_site/'contact-bvh.js').write_bytes(contact)
        if args.three.exists():
            assert json.loads((args.three/'package.json').read_text())['version']=='0.170.0'
            html=html.replace(b'https://cdn.jsdelivr.net/npm/three@0.170.0/',b'./three-local/')
            (variant_site/'three-local').symlink_to(args.three.resolve())
        (variant_site/'index.html').write_bytes(html)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=tmp))
    threading.Thread(target=srv.serve_forever,daemon=True).start()
    browser = pw.chromium.launch(channel='chrome',args=['--use-gl=angle','--use-angle=metal','--enable-webgl','--ignore-gpu-blocklist','--disable-background-timer-throttling','--disable-renderer-backgrounding'])
    pages={}
    def capture(p,i,mode,path):
        path.write_bytes(base64.b64decode(p.evaluate('a=>draw(a)',[i,mode])))
    for name in ['shipping','challenger']:
        p=browser.new_page(viewport={'width':1360,'height':980})
        pages[name]=p
        p.on('pageerror',lambda e:print('Page error',e,flush=True))
        p.goto(f'http://127.0.0.1:{srv.server_port}/{name}/index.html')
        p.wait_for_function('window.aoDemo !== undefined',timeout=90000)
        gpu=p.evaluate((HERE/'capture.js').read_text(),S)
        assert 'M1' in gpu, gpu
        print(name,gpu,flush=True)
        for mode in ['beauty','ao']:
            p.evaluate('m=>start(m)',mode=='ao')
            for i in range(1-S['pre_frames'],1+S['post_frames']):
                if mode=='ao' and i<=0:
                    p.evaluate('a=>draw(a)',[i,'discard'])
                else:
                    capture(p,i,'capture',site/f'{name}-{mode}-{i}.png')
    p=pages['shipping']
    p.bring_to_front()
    p.evaluate('()=>start(false)')
    for i in range(1,S['post_frames']+1):
        capture(p,i,'reference',site/f'ref-{i}.png')
    timings=[]
    for block in range(6):
        pair={}
        for name in list(pages)[::1 if block%2==0 else -1]:
            p=pages[name]
            p.bring_to_front()
            p.evaluate('()=>start(false)')
            pair[name]=[p.evaluate('a=>draw(a)',[i,'time']) for i in range(1-S['pre_frames'],1+S['post_frames'])][S['pre_frames']:]
        timings.append(pair)
    browser.close()
    srv.shutdown()
    summarize(site,out,S,gpu,timings)
