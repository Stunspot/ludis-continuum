#!/usr/bin/env python3
"""Verify the Ludis Continuum v1.1.0 customer release and optional outer ZIP."""
from __future__ import annotations
import argparse,hashlib,io,json,re,zipfile
from pathlib import Path,PurePosixPath
SLUG="ludis-continuum"
RUNTIME_DIRS=("agents","assets","examples","fallbacks","knowledge","schemas","scripts")
RUNTIME_FILES=("SKILL.md","LICENSE.md","EXPORTS-AND-VTT.md","SECURITY.md","SUPPORT.md")
PRIVATE=re.compile(r"(?i)(?:C:[\\/]+Users[\\/]+user|E:[\\/]+(?:Github|Indranet))")
LINK=re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FORBIDDEN=re.compile(r"(?i)(?:^|/)(?:__pycache__(?:/|$)|[^/]+\.(?:pyc|pyo)$)")
def sha(b): return hashlib.sha256(b).hexdigest()
def inv(root): return [{"path":p.relative_to(root).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p.read_bytes())} for p in sorted((x for x in root.rglob("*") if x.is_file()),key=lambda x:x.relative_to(root).as_posix())]
def safe(name):
    if not name or "\\" in name or name.startswith("/") or "\x00" in name:return False
    return all(x not in {"",".",".."} and ":" not in x for x in PurePosixPath(name).parts)
def inspect(data,label,out):
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names=z.namelist()
            if len(names)!=len({x.casefold() for x in names}):out.append(f"{label}: duplicate/case collision")
            for i in z.infolist():
                if not safe(i.filename):out.append(f"{label}: unsafe {i.filename}")
                if FORBIDDEN.search(i.filename):out.append(f"{label}: generated cargo {i.filename}")
                b=z.read(i)
                try:
                    if PRIVATE.search(b.decode()):out.append(f"{label}: private topology {i.filename}")
                except UnicodeDecodeError:pass
            return len(names)
    except Exception as e:out.append(f"{label}: {e}");return 0
def verify(root,outer=None):
    root=root.resolve(); out=[]
    manifest=json.loads((root/"release-manifest.json").read_text())
    version=manifest["version"]
    expected={x["path"]:x for x in manifest["files"]}
    actual={x["path"]:x for x in inv(root) if x["path"]!="release-manifest.json"}
    if set(expected)!=set(actual):out.append("manifest file set differs")
    for p in set(expected)&set(actual):
        if expected[p]!=actual[p]:out.append(f"manifest mismatch {p}")
    skill=root/"codex"/SLUG
    source=root/"source"/f"{SLUG}-v{version}"
    source_map={}
    for name in RUNTIME_FILES: source_map[name]=(source/name).read_bytes()
    for name in RUNTIME_DIRS:
        for p in (source/name).rglob("*"):
            if p.is_file():source_map[p.relative_to(source).as_posix()]=p.read_bytes()
    codex={p.relative_to(skill).as_posix():p.read_bytes() for p in skill.rglob("*") if p.is_file()}
    if source_map!=codex:out.append("source/Codex runtime parity differs")
    claude=root/"claude"/f"{SLUG}-v{version}.zip"
    with zipfile.ZipFile(claude) as z:
        prefix=f"{SLUG}/"; archived={n[len(prefix):]:z.read(n) for n in z.namelist() if n.startswith(prefix)}
    if archived!=codex:out.append("Claude/Codex runtime parity differs")
    for p in actual:
        if FORBIDDEN.search(p):out.append(f"generated cargo {p}")
    for p in root.rglob("*.md"):
        text=p.read_text(encoding="utf-8")
        if PRIVATE.search(text):out.append(f"private topology {p.relative_to(root)}")
        for raw in LINK.findall(text):
            target=raw.split("#",1)[0].strip(" <>")
            if target and not target.startswith(("http://","https://","mailto:","tel:","data:")) and not (p.parent/target).exists():
                out.append(f"broken link {p.relative_to(root)} -> {raw}")
    count=inspect(claude.read_bytes(),"Claude ZIP",out)
    if outer:
        count+=inspect(outer.read_bytes(),"outer ZIP",out)
        prefix=f"{SLUG}-v{version}/"
        with zipfile.ZipFile(outer) as z: archived={n[len(prefix):]:z.read(n) for n in z.namelist() if n.startswith(prefix)}
        expanded={p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob("*") if p.is_file()}
        if archived!=expanded:out.append("outer/expanded parity differs")
    out=sorted(set(out))
    return {"schema":"cd-ludis-release-verification/v1","ok":not out,"counts":{"manifest_files":len(actual),"runtime_files":len(codex),"zip_members":count},"findings":out}
def main():
    p=argparse.ArgumentParser();p.add_argument("root",type=Path);p.add_argument("--outer",type=Path);a=p.parse_args()
    result=verify(a.root,a.outer);print(json.dumps(result,indent=2));return 0 if result["ok"] else 1
if __name__=="__main__":raise SystemExit(main())
