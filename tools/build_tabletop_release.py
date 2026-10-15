"""Build the1.5 gaming-table update against the accepted source selection."""
import hashlib,io,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];VERSION='1.5.0';SLUG='ludis-continuum';PREFIX=f'{SLUG}-v{VERSION}/';DEST=ROOT/'release-candidates'/f'v{VERSION}-final-r2'
def sha(data):return hashlib.sha256(data).hexdigest()
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def inventory(values):return [{'path':p,'bytes':len(b),'sha256':sha(b)} for p,b in sorted(values.items())]
def tree(values):return sha(json.dumps(inventory(values),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def pack(values):
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',compression=zipfile.ZIP_STORED) as z:
        for name,data in sorted(values.items()):
            info=zipfile.ZipInfo(name,(2026,10,15,0,0,0));info.compress_type=zipfile.ZIP_STORED;info.create_system=3;info.external_attr=(0o100755 if name.endswith('Open Ludis.command') else 0o100644)<<16;z.writestr(info,data)
    return buffer.getvalue()
def main():
    DEST.mkdir(parents=True,exist_ok=True)
    previous=json.loads((ROOT/'release-candidates/v1.4.1/source-index.json').read_text(encoding='utf-8'))
    names={r['path'] for r in previous['files']}|{'workspace/tabletop.py','workspace/tabletop.js','workspace/tabletop.css','RELEASE-NOTES-v1.5.0.md','verification/tabletop-v15/DESIGN.md','verification/tabletop-v15/result.json','verification/tabletop-v15.cjs','tools/build_tabletop_release.py'}
    names.discard('workspace/Open Ludis.lnk')  # Host-bound shortcuts are created by their installer, not shipped.
    names.update({'verification/launch-immutability.cjs','verification/launch-immutability-source/result.json'})
    source={n:(ROOT/n).read_bytes() for n in sorted(names)}
    index={'schema':'cd-canonical-source-index/v1','component':SLUG,'version':VERSION,'revision':'purpose-led-gaming-table-r2-immutable-startup','selection_basis':'Accepted1.4.1 source selection plus substantive1.5 workflow implementation and bounded first-use evidence','files':inventory(source)}
    index_raw=encoded(index);(DEST/'source-index.json').write_bytes(index_raw)
    runtime_files={'SKILL.md','LICENSE.md','EXPORTS-AND-VTT.md','SECURITY.md','SUPPORT.md'};runtime_dirs={'agents','assets','examples','fallbacks','knowledge','schemas','scripts','workspace'}
    runtime={n:b for n,b in source.items() if n in runtime_files or n.split('/')[0] in runtime_dirs}
    payload={}
    for stem,values in ((f'source/{SLUG}-v{VERSION}/',source),(f'source-cutoff/{SLUG}/',source),(f'codex/{SLUG}/',runtime)):
        payload.update({stem+n:b for n,b in values.items()})
    nested=pack({SLUG+'/'+n:b for n,b in runtime.items()});claude=f'claude/{SLUG}-v{VERSION}.zip';payload[claude]=nested
    payload['SOURCE-CUTOFF.json']=encoded({'version':VERSION,'files':index['files'],'source_manifest_sha256':sha(index_raw)})
    payload['SHA256SUMS.txt']=(sha(nested)+'  '+claude+'\n').encode()
    for p in (ROOT/f'delivery-sidecars-v{VERSION}').iterdir():
        if p.is_file():payload['delivery-sidecars/'+p.name]=p.read_bytes()
    payload['README.md']=f'# Ludis Continuum {VERSION}\n\nOpen START-HERE.md to install or use the gaming table. The complete Codex runtime and equivalent Claude ZIP are included.\n'.encode()
    payload['START-HERE.md']=f'# Start here\n\nFor Codex install codex/{SLUG}; for Claude install claude/{SLUG}-v{VERSION}.zip. Open workspace/Open Ludis.cmd on Windows or Open Ludis.command on macOS (Python3.10+). Choose or create a campaign; link your RPG folders in Materials & maps. Read workspace/README.md for actual first use, sources, session tools and recovery. Keep user campaign folders outside the installation.\n\nUpdating: retain a recoverable copy of an existing installation before replacing product files. Keep the campaign folder and materials in place; this release reads existing native v2 campaigns and adds table-state.json on the first table save. Source/ and source-cutoff/ are maintainer material, not additional installations.\n'.encode()
    payload[f'RELEASE-NOTES-v{VERSION}.md']=(ROOT/f'RELEASE-NOTES-v{VERSION}.md').read_bytes()
    payload['release-decision.json']=encoded({'baseline':'1.4.1','version':VERSION,'treatment':'update','reason':'Adds user-selected campaign/source workflows and substantive player/GM session tools; preserves native v2 and original32 creative cores.'})
    manifest={'schema':'collaborative-dynamics.customer-skill-family/v2','product':'Ludis Continuum','slug':SLUG,'version':VERSION,'runtime_tree_sha256':tree(runtime),'distributions':{'codex':{'path':f'codex/{SLUG}','file_count':len(runtime),'tree_sha256':tree(runtime)},'source':{'path':f'source/{SLUG}-v{VERSION}','file_count':len(source),'tree_sha256':tree(source)},'claude':{'path':claude,'bytes':len(nested),'sha256':sha(nested)}},'files':inventory(payload)}
    payload['release-manifest.json']=encoded(manifest)
    raw=pack({PREFIX+n:b for n,b in payload.items()});filename=f'{SLUG}-v{VERSION}-complete.zip';(DEST/filename).write_bytes(raw);(DEST/(filename+'.sha256')).write_text(sha(raw)+'  '+filename+'\n',encoding='ascii')
    contract={'schema':'cd-ludis-current-release/v1','version':VERSION,'package':str((DEST/filename).relative_to(ROOT)).replace('\\','/'),'package_sha256':sha(raw),'source_index':str((DEST/'source-index.json').relative_to(ROOT)).replace('\\','/'),'source_index_sha256':sha(index_raw)}
    (ROOT/'release-current.json').write_bytes(encoded(contract));print(json.dumps(contract))
if __name__=='__main__':main()
