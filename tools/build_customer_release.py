#!/usr/bin/env python3
"""Build the reconciled Ludis Continuum v1.1.0 customer release deterministically."""
from __future__ import annotations
import hashlib, json, shutil, subprocess, zipfile
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
VERSION="1.1.0"; SLUG="ludis-continuum"; TITLE="Ludis Continuum"
SOURCE_BASIS="6c6c2e560952b647e814bd4730465488334c4bb7"
STAMP=(2026,8,14,0,0,0)
IGNORE=shutil.ignore_patterns("__pycache__","*.pyc","*.pyo")
RUNTIME_DIRS=("agents","assets","examples","fallbacks","knowledge","schemas","scripts")
RUNTIME_FILES=("SKILL.md","LICENSE.md","EXPORTS-AND-VTT.md","SECURITY.md","SUPPORT.md")
SOURCE_EXCLUDED=(".github/","release-v","release-assets/","tools/")

def sha(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def files(root:Path): return sorted((p for p in root.rglob("*") if p.is_file()),key=lambda p:p.relative_to(root).as_posix())
def inventory(root:Path): return [{"path":p.relative_to(root).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p.read_bytes())} for p in files(root)]
def tree(root:Path)->str: return sha(json.dumps(inventory(root),ensure_ascii=False,sort_keys=True,separators=(",",":")).encode())
def write(path:Path,text:str): path.write_text(text,encoding="utf-8",newline="\n")
def write_json(path:Path,value): write(path,json.dumps(value,ensure_ascii=False,indent=2)+"\n")
def recreate(path:Path,parent:Path):
    if path.resolve().parent!=parent.resolve(): raise RuntimeError(f"unsafe target {path}")
    if path.exists(): shutil.rmtree(path)
    path.mkdir(parents=True)
def zip_tree(path:Path,root:Path,prefix:str=""):
    with zipfile.ZipFile(path,"w",compression=zipfile.ZIP_STORED) as z:
        for src in files(root):
            rel=src.relative_to(root).as_posix()
            info=zipfile.ZipInfo(f"{prefix}/{rel}" if prefix else rel,STAMP)
            info.compress_type=zipfile.ZIP_STORED; info.external_attr=0o100644<<16; info.create_system=3
            z.writestr(info,src.read_bytes())
def copy_runtime(dest:Path):
    dest.mkdir(parents=True)
    for name in RUNTIME_FILES: shutil.copy2(REPO/name,dest/name)
    for name in RUNTIME_DIRS: shutil.copytree(REPO/name,dest/name,ignore=IGNORE)
def copy_source(dest:Path):
    dest.mkdir(parents=True)
    tracked=subprocess.check_output(["git","ls-files"],cwd=REPO,text=True).splitlines()
    for rel in tracked:
        posix=rel.replace("\\","/")
        if posix.startswith(SOURCE_EXCLUDED): continue
        src=REPO/rel
        if not src.is_file() or "__pycache__" in src.parts or src.suffix in {".pyc",".pyo"}: continue
        out=dest/rel; out.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,out)

def main()->int:
    release=REPO/f"release-v{VERSION}"; recreate(release,REPO)
    skill=release/"codex"/SLUG; copy_runtime(skill)
    source=release/"source"/f"{SLUG}-v{VERSION}"; copy_source(source)
    source_runtime=release/".source-runtime"; copy_runtime(source_runtime)
    if inventory(skill)!=inventory(source_runtime): raise RuntimeError("runtime copy mismatch")
    shutil.rmtree(source_runtime)

    notes=f"""# {TITLE} v{VERSION} release notes

Version {VERSION} publishes the maintained 1.1 source candidate that was merged after the older central v0.1.0 package.

## Added

- Governed campaign-ledger v2 operation and non-destructive legacy migration.
- Deterministic neutral GM/player Tonight Packs with exact-byte player approval.
- Offline Alchemy and Foundry v14 handoff bundles with explicit loss and compatibility boundaries.
- Import-observation receipts, race-safe persistence, generated examples, schemas, and 126 regression tests.
- Current tabletop-RPG identity, public documentation, and presentation repairs.

## Evidence boundary

Local and cross-platform static checks establish the exact package, tests, source/distribution parity, and deterministic bytes. They do not establish fresh-host discovery or invocation, live Alchemy or Foundry import, representative accessibility, rules accuracy, balance, rights clearance, live-table quality, or Discord deployment.
"""
    write(REPO/f"RELEASE-NOTES-v{VERSION}.md",notes); write(release/f"RELEASE-NOTES-v{VERSION}.md",notes)
    shutil.copy2(REPO/"LICENSE.md",release/"LICENSE.md")
    write(release/"README.md",f"""# {TITLE} v{VERSION}

This is the complete public customer package.

Start with [START-HERE.md](START-HERE.md). The exact maintained customer documentation is under [source/{SLUG}-v{VERSION}/](source/{SLUG}-v{VERSION}/README.md). Install only the Codex folder or Claude ZIP; source and release records are custody material.
""")
    write(release/"START-HERE.md",f"""# Start here

1. Read the maintained [orientation](source/{SLUG}-v{VERSION}/README.md) and [installation journey](source/{SLUG}-v{VERSION}/START-HERE.md).
2. For Codex, install the complete `codex/{SLUG}/` folder as one skill root.
3. For Claude, install the untouched `claude/{SLUG}-v{VERSION}.zip`.
4. Restart or reload the host, confirm discovery, and invoke Ludis explicitly once.
5. Run `python -B scripts/self_check.py` from the installed skill root.
6. Keep campaign material outside the installed skill. Back it up before migration, export, or import work.

Do not install `source/`, manifests, checksums, or release notes as runtime cargo.
""")
    write(release/"HOST-MATRIX.md","""# Host matrix

| Host | Distribution | Exact package evidence | Live evidence |
| --- | --- | --- | --- |
| Codex | `codex/ludis-continuum/` | Complete and byte-bound | Fresh-host discovery and invocation untested |
| Claude | `claude/ludis-continuum-v1.1.0.zip` | Byte-identical runtime | Fresh-host discovery and invocation untested |
| Chat-only | Maintained fallback documents | Present in both runtimes | Attachment/project behavior varies by host |

Live Alchemy and Foundry imports remain unverified.
""")
    write(release/"PROVENANCE.md",f"""# Provenance

- Repository: https://github.com/Stunspot/{SLUG}
- Source basis before release construction: `{SOURCE_BASIS}`
- Release version: `{VERSION}`
- Maintained source snapshot: `source/{SLUG}-v{VERSION}/`
- Runtime copies: exact parity across source selection, Codex, and Claude

The older central `v0.1.0` ZIP predates the merged 1.1 export/VTT system and is historical evidence, not the current release.
""")
    write(release/"PACKAGE-REFERENCE.md",f"""# Package reference

| Path | Purpose |
| --- | --- |
| `codex/{SLUG}/` | Complete Codex runtime |
| `claude/{SLUG}-v{VERSION}.zip` | Complete Claude runtime |
| `source/{SLUG}-v{VERSION}/` | Exact maintained source snapshot |
| `release-manifest.json` | Complete file custody |
| `SHA256SUMS.txt` | Runtime and archive digests |
| `RELEASE-NOTES-v{VERSION}.md` | Changes and evidence limits |
""")

    claude_dir=release/"claude"; claude_dir.mkdir()
    claude_zip=claude_dir/f"{SLUG}-v{VERSION}.zip"; stage=REPO/f".{SLUG}-claude"
    if stage.exists(): shutil.rmtree(stage)
    shutil.copytree(skill,stage/SLUG,ignore=IGNORE); zip_tree(claude_zip,stage); shutil.rmtree(stage)
    codex_hash=tree(skill); claude_hash=sha(claude_zip.read_bytes())
    write(release/"SHA256SUMS.txt",f"{codex_hash}  codex/{SLUG}/\n{claude_hash}  claude/{claude_zip.name}\n")
    manifest={"schema":"collaborative-dynamics.customer-skill-family/v2","product":TITLE,"slug":SLUG,"version":VERSION,
      "source_repository":f"https://github.com/Stunspot/{SLUG}","source_basis_commit":SOURCE_BASIS,
      "runtime_tree_sha256":codex_hash,"tree_digest_algorithm":"sha256(canonical JSON inventory sorted by relative path; fields path, bytes, sha256)",
      "claim_boundary":"Exact static package custody; live hosts, VTTs, people, and Discord require separate observation.",
      "distributions":{"codex":{"path":f"codex/{SLUG}","file_count":len(files(skill)),"tree_sha256":codex_hash},
        "claude":{"path":f"claude/{claude_zip.name}","bytes":claude_zip.stat().st_size,"sha256":claude_hash},
        "source":{"path":f"source/{SLUG}-v{VERSION}","file_count":len(files(source)),"tree_sha256":tree(source)}},
      "files":inventory(release)}
    write_json(release/"release-manifest.json",manifest)
    assets=REPO/"release-assets"/f"v{VERSION}"; recreate(assets,REPO/"release-assets")
    outer=assets/f"Ludis-Continuum-v{VERSION}.zip"; zip_tree(outer,release,f"{SLUG}-v{VERSION}")
    digest=sha(outer.read_bytes()); write(assets/f"{outer.name}.sha256",f"{digest}  {outer.name}\n")
    write_json(assets/"receipt.json",{"schema":"cd-settled-family-build-receipt/v1","family":SLUG,"version":VERSION,
      "status":"canonical-built-backup-pending","canonical_zip":outer.name,"canonical_zip_sha256":digest,
      "canonical_zip_member_count":len(zipfile.ZipFile(outer).infolist()),"backup":None})
    print(json.dumps({"archive":str(outer),"sha256":digest,"members":len(zipfile.ZipFile(outer).infolist()),
      "runtime_files":len(files(skill)),"source_files":len(files(source))},indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
