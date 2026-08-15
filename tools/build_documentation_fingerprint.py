#!/usr/bin/env python3
"""Build or check the Ludis v1.1.0 customer-documentation fingerprint."""
from __future__ import annotations
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]; VERSION="1.1.0"
ROOT=["README.md","START-HERE.md","DOCUMENTATION.md","EXPORTS-AND-VTT.md","ACCESSIBILITY.md","SECURITY.md","SUPPORT.md","CONTRIBUTING.md","PROVENANCE.md",f"RELEASE-NOTES-v{VERSION}.md"]
SITE=[p.relative_to(REPO).as_posix() for p in sorted((REPO/"docs").rglob("*")) if p.is_file()]
PACKAGE=[f"release-v{VERSION}/{x}" for x in ["README.md","START-HERE.md","HOST-MATRIX.md","PROVENANCE.md","PACKAGE-REFERENCE.md",f"RELEASE-NOTES-v{VERSION}.md"]]
PATHS=sorted(ROOT+SITE+PACKAGE)
def canonical(path):
    b=path.read_bytes()
    if path.suffix.lower() not in {".png",".jpg",".jpeg",".gif",".webp"}:b=b.replace(b"\r\n",b"\n").replace(b"\r",b"\n")
    return b
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
    rows=[{"path":x,"sha256":hashlib.sha256(canonical(REPO/x)).hexdigest()} for x in PATHS]
    h=hashlib.sha256()
    for x in rows:h.update(x["path"].encode()+b"\0"+x["sha256"].encode()+b"\n")
    result={"format":"ludis-documentation-fingerprint/v1","generated_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"product_version":VERSION,"aggregate_sha256":h.hexdigest(),"files":rows,"algorithm":"sha256 over sorted path NUL canonical file-sha256 records; text line endings normalized to LF"}
    targets=[REPO/"verification"/"documentation-fingerprint.json",REPO/"verification"/f"documentation-fingerprint-v{VERSION}.json"]
    if a.check:
        bad=[str(x.relative_to(REPO)) for x in targets if (lambda r:r.get("files")!=rows or r.get("aggregate_sha256")!=result["aggregate_sha256"])(json.loads(x.read_text()))]
        print(json.dumps({"ok":not bad,"files":len(rows),"aggregate_sha256":result["aggregate_sha256"],"mismatches":bad},indent=2));return 0 if not bad else 1
    text=json.dumps(result,indent=2)+"\n"
    for x in targets:x.write_text(text,encoding="utf-8",newline="\n")
    print(json.dumps({"files":len(rows),"aggregate_sha256":result["aggregate_sha256"]},indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
