"""Local tabletop workspace. User-selected sources are read without changing originals."""
from pathlib import Path
import sys
import base64, hashlib, json, mimetypes, os, re, secrets, subprocess, tempfile, threading, time, urllib.parse, uuid, zipfile
import xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
LOCK=threading.RLock()
CONFIG=Path(os.environ.get('LUDIS_SETTINGS_HOME', str(Path(os.environ.get('LOCALAPPDATA',str(Path.home()/'.local'/'share')))/'LudisContinuum')))
EXTENSIONS={'.pdf','.docx','.txt','.md','.rst','.csv','.png','.jpg','.jpeg','.webp','.gif','.svg','.mp3','.wav','.ogg','.json','.html','.htm','.rtf','.odt','.doc','.zip'}
def read_json(path,default):
    try:return json.loads(path.read_text(encoding='utf-8'))
    except (OSError,ValueError):return default

def config():return read_json(CONFIG/'settings.json',{})
def atomic(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.'+secrets.token_hex(5)+'.tmp')
    try:
        tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        os.replace(tmp,path)
    finally:tmp.unlink(missing_ok=True)
def remember(root):
    value=config();value['last_campaign']=str(root)
    value['recent']=[str(root)]+[x for x in value.get('recent',[]) if x!=str(root)][:11]
    atomic(CONFIG/'settings.json',value)
def initial_root():
    value=os.environ.get('LUDIS_DATA_HOME') or config().get('last_campaign')
    if value:return Path(value).expanduser().resolve()
    legacy=Path.home()/'Documents'/'LudisContinuum'
    if (legacy/'campaign-ledger.json').is_file():return legacy.resolve()
    # A proposed destination, not a silently created or assumed-accessible source.
    return (CONFIG/'campaigns'/'My campaign').resolve()
def checked_root(value,create=False):
    raw=Path(value).expanduser()
    if not raw.is_absolute():raise ValueError('Choose a full folder path, such as E:\\Games\\My campaign.')
    root=raw.resolve()
    if root==HERE.parent or HERE.parent in root.parents:raise ValueError('Choose a campaign folder outside the installed Ludis files.')
    if create:root.mkdir(parents=True,exist_ok=True)
    if not root.is_dir():raise ValueError('That folder does not exist. Choose an existing campaign, or create a new one here.')
    try:
        with tempfile.TemporaryFile(dir=root):pass
    except OSError as exc:raise ValueError('Ludis cannot save in this folder. Choose a writable campaign folder; sources can be linked separately.') from exc
    return root

def suggested_sources():
    found=[]
    if os.environ.get('LUDIS_LIBRARY_HOME'):found.append(os.environ['LUDIS_LIBRARY_HOME'])
    nova=os.environ.get('NOVA_DATA_ROOT') or os.environ.get('NOVA_HOME')
    if nova:
        pointer=read_json(Path(nova)/'estate'/'rpg-library.json',{})
        path=pointer.get('resolved_path') or str(Path(nova)/'archive'/'RPG Library')
        if Path(path).is_dir():found.append(path)
    return list(dict.fromkeys(found))
def table_default():return {'sources':[],'material_pins':[],'characters':[],'combatants':[],'round':1,'turn':0,'rolls':[],'session_log':[],'clocks':[],'role':'gm','session_title':'','session_notes':'','opening':'','next_question':'','prep':[]}
def table(root):
    value=table_default()
    if not (root/'table-state.json').exists():
        ledger=read_json(root/'campaign-ledger.json',{});sessions=ledger.get('sessions',[])
        value['prep']=[{'text':x if isinstance(x,str) else json.dumps(x),'done':False} for x in ledger.get('next_prep',[])]
        if sessions:value.update({'session_title':sessions[-1].get('title',''),'session_notes':sessions[-1].get('notes','')})
        value['opening']=ledger.get('campaign',{}).get('premise') or ''
        value['next_question']=ledger.get('campaign',{}).get('current_horizon') or ''
    value.update(read_json(root/'table-state.json',{}));return value
def validate_table(value):
    if not isinstance(value,dict):raise ValueError('This backup has no readable table workspace.')
    for key in ('sources','material_pins','characters','combatants','rolls','session_log','clocks','prep'):
        if not isinstance(value.get(key,[]),list) or any(not isinstance(x,dict) for x in value.get(key,[])):raise ValueError('The table workspace has an unreadable '+key.replace('_',' ')+'.')
    for key in ('session_title','session_notes','opening','next_question'):
        if not isinstance(value.get(key,''),str):raise ValueError('The table workspace has unreadable session text.')
    for key in ('round','turn'):
        if not isinstance(value.get(key,1 if key=='round' else 0),int):raise ValueError('The encounter position is unreadable.')
    result=table_default();result.update(value);return result
def stamp(root):
    return hashlib.sha256(b''.join((root/n).read_bytes() if (root/n).exists() else b'' for n in ('table-state.json','campaign-ledger.json'))).hexdigest()
def snapshot(desk):
    root=desk.ROOT;error=None;ledger=None;writable=False
    try:
        if (root/'campaign-ledger.json').exists():ledger=desk.load_with_digest(root/'campaign-ledger.json')[0]
        if root.is_dir():checked_root(str(root));writable=True
    except (ValueError,OSError) as exc:error=str(exc)
    recent=[]
    for value in config().get('recent',[]):
        path=Path(value);record=read_json(path/'campaign-ledger.json',{})
        recent.append({'path':value,'title':record.get('campaign',{}).get('title') or path.name,'available':path.is_dir()})
    return {'root':str(root),'ledger':ledger,'table':table(root),'etag':stamp(root),'token':desk.TOKEN,'error':error,'writable':writable,'recent':recent,'suggested_sources':suggested_sources(),'version':'1.5.0'}
def folder_dialog(initial):
    if os.name=='nt':
        script="Add-Type -AssemblyName System.Windows.Forms; $d=New-Object System.Windows.Forms.FolderBrowserDialog; $d.Description='Choose a campaign or source folder for Ludis'; $d.ShowNewFolderButton=$true; if($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK){[Console]::Write($d.SelectedPath)}"
        run=subprocess.run(['powershell.exe','-NoProfile','-STA','-Command',script],capture_output=True,text=True,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
        if run.returncode:raise ValueError('The folder browser could not open. Paste a full folder path instead.')
        return run.stdout.strip()
    try:
        import tkinter as tk
        from tkinter import filedialog
        win=tk.Tk();win.withdraw();win.attributes('-topmost',True)
        value=filedialog.askdirectory(title='Choose a folder for Ludis',initialdir=initial);win.destroy();return value
    except Exception as exc:raise ValueError('The folder browser is unavailable. Paste a full folder path instead.') from exc

def source_for(root,source_id):
    item=next((x for x in table(root)['sources'] if x['id']==source_id),None)
    if not item:raise ValueError('This source is no longer linked. Choose it again in Materials.')
    base=(root/item['relative']).resolve() if item.get('relative') else Path(item['path']).resolve()
    return item,base
def material_path(root,source_id,relative):
    item,base=source_for(root,source_id);path=(base/relative).resolve()
    if path==base or not path.is_relative_to(base):raise ValueError('That file is outside the linked source.')
    if not path.is_file():raise ValueError('This file is unavailable. Check its source folder or reconnect the drive.')
    return path

def scan(root,source_id,query=''):
    item,base=source_for(root,source_id)
    if not base.is_dir():raise ValueError('Source folder is unavailable. Reconnect the drive or change the source.')
    results=[];count=0;errors=[];query=query.casefold()
    def walk(folder,depth=0):
        nonlocal count
        if depth>8:return
        try:
            children=sorted(folder.iterdir(),key=lambda p:(not p.is_dir(),p.name.casefold()))
        except OSError:errors.append(str(folder));return
        for path in children:
            if path.is_symlink() or not path.resolve().is_relative_to(base) or path.name.startswith('.') or path.name in ('node_modules','__pycache__'):continue
            if count>=5000:return
            if path.is_dir():yield from walk(path,depth+1)
            elif path.suffix.lower() in EXTENSIONS:
                count+=1;yield path
    for path in walk(base):
        rel=path.relative_to(base).as_posix()
        if query and query not in rel.casefold():continue
        try:results.append({'source':source_id,'path':rel,'name':path.name,'extension':path.suffix.lower(),'bytes':path.stat().st_size})
        except OSError:continue
    return {'items':results,'limited':count>=5000,'unreadable_folders':len(errors),'source':item}
def preview(path):
    suffix=path.suffix.lower()
    if suffix in ('.png','.jpg','.jpeg','.webp','.gif'):return {'kind':'image'}
    if suffix=='.pdf':return {'kind':'pdf'}
    if suffix in ('.mp3','.wav','.ogg'):return {'kind':'audio'}
    if path.stat().st_size>12000000:return {'kind':'external','message':'This large file opens in your usual application.'}
    if suffix=='.docx':
        try:
            with zipfile.ZipFile(path) as archive:
                info=archive.getinfo('word/document.xml')
                if info.file_size>12000000:raise ValueError('This document is too large to preview here. Open the original.')
                doc=ET.fromstring(archive.read(info))
            ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            text='\n'.join(''.join(p.itertext()) for p in doc.findall('.//w:p',ns))
            return {'kind':'text','text':text,'message':'Document text preview. Open the original to see its formatting and illustrations.'}
        except (zipfile.BadZipFile,KeyError,ET.ParseError):return {'kind':'external','message':'This document could not be previewed. Open the original in your document application.'}
    if suffix in ('.txt','.md','.rst','.csv','.json'):
        return {'kind':'text','text':path.read_text(encoding='utf-8-sig',errors='replace')[:250000]}
    return {'kind':'external','message':'Open the original in its usual application. Ludis keeps it available beside your session.'}
def get(desk,handler,path,query):
    if path=='/api/table':return snapshot(desk)
    if path=='/api/library':return scan(desk.ROOT,query.get('source',[''])[0],query.get('q',[''])[0])
    if path in ('/api/material','/api/material-file'):
        file=material_path(desk.ROOT,query.get('source',[''])[0],query.get('path',[''])[0])
        if path=='/api/material':return preview(file)
        if file.stat().st_size>100000000:raise ValueError('Open this large file in its usual application.')
        kind=mimetypes.guess_type(file.name)[0] or 'application/octet-stream'
        if file.suffix.lower() not in ('.pdf','.png','.jpg','.jpeg','.webp','.gif','.mp3','.wav','.ogg'):kind='application/octet-stream'
        handler.answer(file.read_bytes(),kind=kind);return False
    return None

def post(desk,path,obj):
    with LOCK:
        if path not in ('/api/location/browse','/api/location/use','/api/location/create','/api/campaign/restore','/api/table/save','/api/library/add','/api/library/import','/api/open-file'):return None
        if path=='/api/location/browse':return {'path':folder_dialog(str(desk.ROOT))}
        if path in ('/api/location/use','/api/location/create'):
            root=checked_root(obj.get('path',''),create=path.endswith('/create'))
            if path.endswith('/create'):
                if (root/'campaign-ledger.json').exists():raise ValueError('A campaign is already here. Use Open campaign to resume it.')
                title=str(obj.get('title','')).strip()
                if not title:raise ValueError('Name the campaign so you can find it again.')
                value=read_json(HERE.parent/'assets'/'campaign.template'/'campaign-ledger.json',{})
                value['campaign'].update({'id':'campaign-'+uuid.uuid4().hex,'title':title,'system':str(obj.get('system','')).strip(),'premise':str(obj.get('premise','')).strip()})
                desk.save(root/'campaign-ledger.json',value,expected_sha256=None);atomic(root/'table-state.json',table_default())
            elif not (root/'campaign-ledger.json').is_file():raise ValueError('This folder has no Ludis campaign yet. Create a campaign here, or link this folder as a material source inside a campaign.')
            desk.ROOT=root;remember(root);return snapshot(desk)
        if path=='/api/campaign/restore':
            raw=base64.b64decode(obj['data'],validate=True);incoming=json.loads(raw)
            if not isinstance(incoming,dict):raise ValueError('Choose a Ludis campaign backup or native v2 campaign file.')
            value=incoming.get('ledger') if incoming.get('format')=='cd-ludis-table-backup/v1' else incoming
            if not isinstance(value,dict) or value.get('format')!='cd-ludis-campaign-ledger/v2':raise ValueError('Choose a Ludis campaign backup or native v2 campaign file. Ordinary documents belong in Materials & maps.')
            errors=desk.validate(value)
            if errors:raise ValueError('This campaign backup could not open: '+'; '.join(errors[:3]))
            data=validate_table(incoming.get('table',table_default())) if incoming.get('format')=='cd-ludis-table-backup/v1' else table_default()
            root=checked_root(obj.get('path',''),create=True)
            if (root/'campaign-ledger.json').exists():raise ValueError('A campaign is already here. Choose an empty folder for this restored campaign.')
            desk.save(root/'campaign-ledger.json',value,expected_sha256=None)
            atomic(root/'table-state.json',data);(root/'imports').mkdir(exist_ok=True);(root/'imports'/'original-campaign-backup.json').write_bytes(raw)
            desk.ROOT=root;remember(root);return snapshot(desk)
        root=checked_root(str(desk.ROOT))
        if not (root/'campaign-ledger.json').exists():raise ValueError('Create or open a campaign first.')
        if path=='/api/table/save':
            if obj.get('etag')!=stamp(root):raise ValueError('This campaign changed in another window. Reload before saving; your current draft is still on screen.')
            new_table=validate_table(obj['table']);value=obj['ledger'];errors=desk.validate(value)
            if errors:raise ValueError('The campaign could not be saved: '+'; '.join(errors[:3]))
            old,etag=desk.load_with_digest(root/'campaign-ledger.json')
            if value['campaign']['id']!=old['campaign']['id']:raise ValueError('Choose another campaign from Campaigns instead of changing its identity.')
            with desk.exclusive_ledger_lock(root/'campaign-ledger.json'):
                if value!=old:
                    history=root/'history';history.mkdir(exist_ok=True)
                    (history/(str(time.time_ns())+'-campaign-ledger.json')).write_bytes((root/'campaign-ledger.json').read_bytes())
                    desk.save(root/'campaign-ledger.json',value,expected_sha256=etag)
                atomic(root/'table-state.json',new_table)
            return snapshot(desk)
        if path=='/api/library/add':
            base=Path(obj.get('path','')).expanduser()
            if not base.is_absolute() or not base.is_dir():raise ValueError('Choose an existing, readable source folder.')
            try:next(base.iterdir(),None)
            except OSError as exc:raise ValueError('Ludis cannot read this folder. Choose another source or reconnect the drive.') from exc
            data=table(root);resolved=str(base.resolve())
            if not any(x['path']==resolved for x in data['sources']):data['sources'].append({'id':uuid.uuid4().hex,'path':resolved,'name':base.name})
            atomic(root/'table-state.json',data);return snapshot(desk)
        if path=='/api/library/import':
            files=obj.get('files',[])
            if not files:raise ValueError('Choose one or more documents, maps, images, or audio files.')
            dest=root/'materials';dest.mkdir(exist_ok=True)
            for item in files:
                name=Path(item['name']).name
                if not name or name in ('.','..') or any(c in name for c in '\\/:'):raise ValueError('This file name cannot be imported.')
                if Path(name).suffix.lower() not in EXTENSIONS:raise ValueError('Choose a document, image, map, audio file, or ZIP of gaming material. This file type is not supported here.')
                raw=base64.b64decode(item['data'],validate=True)
                if len(raw)>50000000:raise ValueError('Each imported file can be up to 50 MB. Link its folder for larger files.')
                target=dest/name
                if target.exists():target=dest/(target.stem+'-'+secrets.token_hex(3)+target.suffix)
                target.write_bytes(raw)
            data=table(root)
            if not any(Path(x['path']).resolve()==dest.resolve() for x in data['sources']):data['sources'].append({'id':uuid.uuid4().hex,'path':str(dest.resolve()),'name':'Imported materials','relative':'materials'})
            atomic(root/'table-state.json',data);return snapshot(desk)
        if path=='/api/open-file':
            file=material_path(root,obj['source'],obj['path'])
            if file.suffix.lower() not in EXTENSIONS:raise ValueError('This file type cannot be opened from Ludis.')
            if os.name=='nt':os.startfile(str(file))
            else:subprocess.Popen(['open' if sys.platform=='darwin' else 'xdg-open',str(file)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            return {'opened':True}
        return None
