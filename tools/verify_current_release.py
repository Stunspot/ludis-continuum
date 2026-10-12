#!/usr/bin/env python3
"""Verify the frozen current Ludis kit against canonical source and deterministic bytes."""
from __future__ import annotations
import argparse, copy, hashlib, io, json, unicodedata, zipfile
from pathlib import Path, PurePosixPath

SLUG = "ludis-continuum"
RUNTIME_FILES = {"SKILL.md", "LICENSE.md", "EXPORTS-AND-VTT.md", "SECURITY.md", "SUPPORT.md"}
RUNTIME_DIRS = {"agents", "assets", "examples", "fallbacks", "knowledge", "schemas", "scripts", "workspace"}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def safe_name(name):
    require(bool(name) and "\\" not in name and "\x00" not in name, "Unsafe member name")
    parts = name.split("/")
    require(all(p not in ("", ".", "..") and ":" not in p for p in parts), "Unsafe member path: " + name)
    return name

def local_path(root, name):
    safe_name(name)
    result = root.joinpath(*PurePosixPath(name).parts)
    require(result.resolve().is_relative_to(root.resolve()), "Path leaves its root: " + name)
    return result

def unpack(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        infos = archive.infolist()
        names = [safe_name(item.filename) for item in infos]
        keys = [unicodedata.normalize("NFC", name).casefold() for name in names]
        require(len(keys) == len(set(keys)), "Duplicate or normalized member collision")
        require(all(not item.is_dir() and not item.flag_bits & 1 for item in infos), "Unexpected directory/encryption")
        return {item.filename: archive.read(item) for item in infos}, {item.filename: copy.copy(item) for item in infos}, archive.comment

def pack(payload, infos, comment):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.comment = comment
        for name in sorted(payload):
            archive.writestr(copy.copy(infos[name]), payload[name])
    return buffer.getvalue()

def inventory(payload, stem):
    return [{"path": name[len(stem):], "bytes": len(data), "sha256": sha(data)}
            for name, data in sorted(payload.items()) if name.startswith(stem)]

def tree(records):
    return sha(json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())

def verify(root, source_root=None):
    root = root.resolve()
    source_root = (source_root or root).resolve()
    contract = json.loads((root / "release-current.json").read_text(encoding="utf-8"))
    require(contract["schema"] == "cd-ludis-current-release/v1", "Unknown current-release contract")
    raw = local_path(root, contract["package"]).read_bytes()
    require(sha(raw) == contract["package_sha256"], "Current artifact digest differs")
    index_raw = local_path(root, contract["source_index"]).read_bytes()
    require(sha(index_raw) == contract["source_index_sha256"], "Current source-index digest differs")
    index = json.loads(index_raw)
    require(index["schema"] == "cd-canonical-source-index/v1" and index["version"] == contract["version"], "Source identity differs")
    source = {}
    for record in index["files"]:
        name = safe_name(record["path"])
        require(name not in source, "Duplicate canonical source record")
        data = local_path(source_root, name).read_bytes()
        require(len(data) == record["bytes"] and sha(data) == record["sha256"], "Canonical source differs: " + name)
        source[name] = data

    payload, infos, comment = unpack(raw)
    prefix = SLUG + "-v" + contract["version"] + "/"
    require(all(name.startswith(prefix) for name in payload), "Unexpected outer namespace")
    manifest_name = prefix + "release-manifest.json"
    manifest = json.loads(payload[manifest_name])
    require(manifest["schema"] == "collaborative-dynamics.customer-skill-family/v2" and
            manifest["slug"] == SLUG and manifest["version"] == contract["version"], "Package identity differs")
    require(manifest["files"] == inventory({k: v for k, v in payload.items() if k != manifest_name}, prefix), "Complete manifest differs")
    cutoff = json.loads(payload[prefix + "SOURCE-CUTOFF.json"])
    require(cutoff["version"] == contract["version"] and cutoff["files"] == index["files"] and
            cutoff["source_manifest_sha256"] == sha(index_raw), "Source cutoff differs")

    runtime = {name: data for name, data in source.items()
               if name in RUNTIME_FILES or name.split("/")[0] in RUNTIME_DIRS}
    replay = dict(payload)
    for stem, expected in (("source/" + SLUG + "-v" + contract["version"] + "/", source),
                           ("source-cutoff/" + SLUG + "/", source),
                           ("codex/" + SLUG + "/", runtime)):
        require({n[len(prefix + stem):] for n in payload if n.startswith(prefix + stem)} == set(expected), "Source/runtime closure differs: " + stem)
        for name, data in expected.items():
            require(payload[prefix + stem + name] == data, "Archived source differs: " + name)
            replay[prefix + stem + name] = data
        mode = infos[prefix + stem + "workspace/Open Ludis.command"].external_attr >> 16 & 0o777
        require(mode == 0o755, "Mac command lost executable mode")

    runtime_records = inventory(replay, prefix + "codex/" + SLUG + "/")
    source_records = inventory(replay, prefix + "source/" + SLUG + "-v" + contract["version"] + "/")
    for role, records in (("codex", runtime_records), ("source", source_records)):
        distribution = manifest["distributions"][role]
        require(distribution["file_count"] == len(records) and distribution["tree_sha256"] == tree(records), "Distribution tree differs: " + role)
    require(manifest["runtime_tree_sha256"] == tree(runtime_records), "Runtime tree digest differs")

    nested_name = prefix + manifest["distributions"]["claude"]["path"]
    nested, nested_infos, nested_comment = unpack(payload[nested_name])
    require(set(nested) == {SLUG + "/" + name for name in runtime}, "Claude runtime closure differs")
    for name, data in runtime.items():
        require(nested[SLUG + "/" + name] == data, "Claude body differs: " + name)
    require(nested_infos[SLUG + "/workspace/Open Ludis.command"].external_attr >> 16 & 0o777 == 0o755, "Claude Mac mode differs")
    rebuilt_nested = pack({SLUG + "/" + name: data for name, data in runtime.items()}, nested_infos, nested_comment)
    require(rebuilt_nested == payload[nested_name], "Canonical Claude reconstruction is not byte-deterministic")
    claude = manifest["distributions"]["claude"]
    require(claude["bytes"] == len(rebuilt_nested) and claude["sha256"] == sha(rebuilt_nested), "Claude artifact binding differs")
    require(payload[prefix + "SHA256SUMS.txt"].decode() == sha(rebuilt_nested) + "  " + claude["path"] + "\n", "Public checksum differs")
    replay[nested_name] = rebuilt_nested
    version = contract["version"]
    for name in ("Ludis Continuum.png", f"Ludis Continuum v{version}.md", f"Ludis Continuum v{version} Extra.md"):
        current = (root / ("delivery-sidecars-v" + version) / name).read_bytes()
        require(payload[prefix + "delivery-sidecars/" + name] == current, "Current sidecar differs: " + name)
        replay[prefix + "delivery-sidecars/" + name] = current
    rebuilt_manifest = dict(manifest)
    rebuilt_manifest["files"] = inventory({k: v for k, v in replay.items() if k != manifest_name}, prefix)
    replay[manifest_name] = (json.dumps(rebuilt_manifest, ensure_ascii=False, indent=2) + "\n").encode()
    rebuilt = pack(replay, infos, comment)
    require(rebuilt == raw, "Canonical current-kit reconstruction is not byte-deterministic")
    return {"ok": True, "version": contract["version"], "package_sha256": sha(rebuilt),
            "members": len(payload), "runtime_files": len(runtime), "source_files": len(source),
            "scope": "Frozen current artifact/source/sidecars and deterministic canonical reconstruction; historical releases untouched"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.root, args.source_root)
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1
    print(json.dumps(result))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
