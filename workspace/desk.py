#!/usr/bin/env python3
"""Ludis session desk around the governed native v2 ledger."""
import sys
sys.dont_write_bytecode = True
import argparse,base64,hashlib,html,json,os,re,secrets,subprocess,tempfile,time,urllib.parse,urllib.request,webbrowser
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent/'scripts'))
from ledgerlib import validate,load_with_digest,save,exclusive_ledger_lock,LedgerWriteConflictError,LedgerBusyError
from exportlib import project_ledger,ExportError
sys.path.insert(0,str(HERE))
import tabletop
PRODUCT='ludis-continuum';TITLE='Ludis Continuum';PORT=8771
ROOT=tabletop.initial_root();TOKEN=secrets.token_urlsafe(24)
BUILD=hashlib.sha256(b''.join(p.name.encode()+p.read_bytes() for p in sorted(HERE.iterdir()) if p.is_file() and p.suffix!='.lnk')).hexdigest()
def digest(data):return hashlib.sha256(data).hexdigest()
def ledger_path():return ROOT/'campaign-ledger.json'
def state():
    if not ledger_path().exists():return {'ledger':None,'etag':None,'root':str(ROOT),'token':TOKEN}
    ledger,etag=load_with_digest(ledger_path());errors=validate(ledger)
    if errors:raise ValueError('Native ledger validation failed: '+'; '.join(errors[:8]))
    return {'ledger':ledger,'etag':etag,'root':str(ROOT),'token':TOKEN}
def player_html():
    value=state();ledger=value['ledger']
    if not ledger:raise ValueError('Create or import a campaign first')
    projection=project_ledger(ledger,'player');objects=projection['objects']
    # Campaign metadata, table contract, provenance, assets and arbitrary data are
    # intentionally absent from this standalone reading projection.
    cards=''.join('<article><small>'+html.escape(o.get('kind',''))+'</small><h2>'+html.escape(o.get('title') or o['id'])+'</h2><pre>'+html.escape(o.get('content') or '')+'</pre></article>' for o in objects)
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ludis Â· Player reading candidate</title><style>body{margin:0;background:#f0e9d7;color:#342c22;font:18px/1.6 Georgia}main{max-width:850px;margin:50px auto;padding:25px}h1{font-size:42px}article{padding:25px 0;border-top:1px solid #b9a888}small{font:12px system-ui;letter-spacing:.15em}pre{font:inherit;white-space:pre-wrap;overflow-wrap:anywhere}@media print{body{background:white}}</style><main><small>LUDIS CONTINUUM / PLAYER READING</small><h1>At the table</h1><p>Filtered reading candidate. Only active, eligible player-safe objects are included. GM must review the exact content before sharing; visibility labels cannot detect prose spoilers.</p>'+cards+'</main></html>').encode()
def health(port):
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/health',timeout=.3) as r:return json.load(r)
    except Exception:return None
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*a):pass
    def answer(self,value,status=200,kind='application/json'):
        data=value if isinstance(value,bytes) else json.dumps(value).encode() if kind=='application/json' else value;self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(data)
    def do_GET(self):
        try:
            expected=f'http://127.0.0.1:{self.server.server_port}'
            if self.headers.get('Host')!=f'127.0.0.1:{self.server.server_port}' or self.headers.get('Origin',expected)!=expected:return self.answer({'error':'Use the workspace loopback address'},403)
            parsed=urllib.parse.urlsplit(self.path);path=parsed.path
            result=tabletop.get(sys.modules[__name__],self,path,urllib.parse.parse_qs(parsed.query))
            if result is False:return
            if result is not None:return self.answer(result)
            if path=='/health':return self.answer({'product':PRODUCT,'root':str(ROOT),'ui':str(HERE),'build':BUILD,'port':self.server.server_port,'pid':os.getpid()})
            if path=='/api/state':return self.answer(state())
            if path=='/player':return self.answer(player_html(),kind='text/html; charset=utf-8')
            if path=='/api/export-player':
                data=player_html();self.send_response(200);self.send_header('Content-Type','text/html');self.send_header('Content-Disposition','attachment; filename="ludis-player-reading.candidate.html"');self.end_headers();return self.wfile.write(data)
            if path=='/api/export-ledger':return self.answer(ledger_path().read_bytes(),kind='application/json')
            name='index.html' if path=='/' else path.lstrip('/')
            if name not in ('index.html','app.js','style.css','skins.css','night-routes.png','patchwork-world.png','ludis.ico','ludis-icon.png','tabletop.js','tabletop.css'):return self.answer({'error':'Not found'},404)
            return self.answer((HERE/name).read_bytes(),kind={'index.html':'text/html','app.js':'text/javascript','tabletop.js':'text/javascript','tabletop.css':'text/css','style.css':'text/css','skins.css':'text/css','night-routes.png':'image/png','patchwork-world.png':'image/png','ludis.ico':'image/x-icon','ludis-icon.png':'image/png'}[name])
        except (ValueError,ExportError) as e:self.answer({'error':str(e)},400)
        except OSError as e:self.answer({'error':str(e)},404)
    def do_POST(self):
        try:
            if self.headers.get('Host')!=f'127.0.0.1:{self.server.server_port}' or self.headers.get('X-Desk-Token')!=TOKEN or self.headers.get('Origin')!=f'http://127.0.0.1:{self.server.server_port}':return self.answer({'error':'Refresh the desk to renew authorization'},403)
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=75000000:raise ValueError('Choose files totaling less than 50 MB, or link their folder.')
            obj=json.loads(self.rfile.read(size))
            result=tabletop.post(sys.modules[__name__],self.path,obj)
            if result is not None:return self.answer(result)
            if self.path=='/api/validate':
                errors=validate(obj['ledger'])
                if errors:raise ValueError('Native ledger validation failed: '+'; '.join(errors[:8]))
                return self.answer({'valid':True})
            ROOT.mkdir(parents=True,exist_ok=True)
            with exclusive_ledger_lock(ledger_path()):
                old,etag=load_with_digest(ledger_path()) if ledger_path().exists() else (None,None)
                if obj.get('etag')!=etag:return self.answer({'error':'Campaign changed. Export your draft and reload before saving.'},409)
                if self.path=='/api/init':
                    if old:raise ValueError('Campaign already exists')
                    value=json.loads((HERE.parent/'assets'/'campaign.template'/'campaign-ledger.json').read_text(encoding='utf-8'));value['campaign']['id']=obj['id'];value['campaign']['title']=obj['title']
                elif self.path=='/api/save':
                    value=obj['ledger']
                    if old and value.get('campaign',{}).get('id')!=old['campaign']['id']:raise ValueError('Campaign identity cannot change here')
                    if old:
                        approved={o['id']:o for o in old['objects'] if o['status']=='active_canon'}
                        incoming={o.get('id'):o for o in value.get('objects',[]) if isinstance(o,dict)}
                        if any(incoming.get(id)!=record for id,record in approved.items()):raise ValueError('Existing active canon cannot be changed, removed, or demoted here. Use governed GM tools.')
                        for o in value.get('objects',[]):
                            if isinstance(o,dict) and o.get('status')=='active_canon' and o.get('id') not in approved:raise ValueError('Use governed GM promotion tools for new active canon. Capture changes as proposals here.')
                        if value.get('approvals')!=old.get('approvals'):raise ValueError('Governed approvals cannot be edited in the desk')
                    if obj.get('import'):
                        original=base64.b64decode(obj['original'],validate=True)
                        if json.loads(original)!=value:raise ValueError('Imported original bytes do not match the submitted ledger')
                else:raise ValueError('Unknown action')
                errors=validate(value)
                if errors:raise ValueError('Native ledger validation failed: '+'; '.join(errors[:8]))
                if obj.get('import'):
                    p=ROOT/'imports'/f'{time.time_ns()}-campaign-ledger.json';p.parent.mkdir(exist_ok=True);p.write_bytes(original)
                if old:
                    p=ROOT/'history'/f'{time.time_ns()}-campaign-ledger.json';p.parent.mkdir(exist_ok=True);p.write_bytes(ledger_path().read_bytes())
                save(ledger_path(),value,expected_sha256=etag)
            return self.answer(state())
        except (LedgerWriteConflictError,LedgerBusyError) as e:self.answer({'error':str(e)},409)
        except (ValueError,KeyError,TypeError,OSError) as e:self.answer({'error':str(e)},400)
def main():
    p=argparse.ArgumentParser();p.add_argument('--serve',action='store_true');p.add_argument('--port',type=int,default=PORT);p.add_argument('--no-browser',action='store_true');p.add_argument('--data-root');a=p.parse_args()
    global ROOT
    if a.data_root:ROOT=Path(a.data_root).expanduser().resolve()
    if ROOT==HERE.parent or HERE.parent in ROOT.parents:raise SystemExit('Choose a data root outside the product installation; runtime records must remain portable.')
    if a.serve:ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever();return
    for port in range(a.port,a.port+20):
        found=health(port)
        if found and found.get('product')==PRODUCT and found.get('root')==str(ROOT) and found.get('ui')==str(HERE) and found.get('build')==BUILD:
            if not a.no_browser:webbrowser.open(f'http://127.0.0.1:{port}')
            print(f'http://127.0.0.1:{port}');return
        if found:continue
        opts={'stdin':subprocess.DEVNULL,'stdout':subprocess.DEVNULL,'stderr':subprocess.DEVNULL}
        if os.name=='nt':opts['creationflags']=subprocess.CREATE_NO_WINDOW|subprocess.DETACHED_PROCESS
        else:opts['start_new_session']=True
        child=subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),'--serve','--port',str(port),'--data-root',str(ROOT)],**opts)
        for _ in range(40):
            time.sleep(.1);found=health(port)
            if found and found.get('product')==PRODUCT and found.get('root')==str(ROOT) and found.get('ui')==str(HERE) and found.get('build')==BUILD:
                if not a.no_browser:webbrowser.open(f'http://127.0.0.1:{port}')
                print(f'http://127.0.0.1:{port}');return
            if child.poll() is not None:break
    raise SystemExit('No free local port; close an old desk or use --port NUMBER.')
if __name__=='__main__':main()
