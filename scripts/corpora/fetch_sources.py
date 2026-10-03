#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "contracts/v1.1/corpus-source-registry.json"
DEFAULT_DEST = ROOT / ".local/corpora"

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

def source_by_key(registry: dict, key: str) -> dict:
    for source in registry["sources"]:
        if source["sourceKey"] == key:
            return source
    raise SystemExit(f"Unknown sourceKey: {key}")

def safe_member_path(name: str) -> PurePosixPath:
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts:
        raise ValueError(f"Unsafe archive path: {name}")
    return p

def configured_match(rel: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, pattern) for pattern in patterns)

def fetch_url(url: str, target: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "hebrew-chinese-bible-research/1.0"})
    with urllib.request.urlopen(req, timeout=120) as response, target.open("wb") as out:
        shutil.copyfileobj(response, out)

def fetch_archive_subset(source: dict, stage: Path) -> None:
    repo = source["repository"]
    commit = source["pin"]["commitSha"]
    patterns = source["acquisition"]["paths"]
    archive_url = f"https://codeload.github.com/{repo}/tar.gz/{commit}"
    archive_path = stage / "upstream.tar.gz"
    fetch_url(archive_url, archive_path)
    extracted = 0
    with tarfile.open(archive_path, "r:gz") as tf:
        for member in tf.getmembers():
            if not member.isfile():
                continue
            p = safe_member_path(member.name)
            if len(p.parts) < 2:
                continue
            rel = PurePosixPath(*p.parts[1:]).as_posix()
            if not configured_match(rel, patterns):
                continue
            src = tf.extractfile(member)
            if src is None:
                continue
            target = stage / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            with src, target.open("wb") as out:
                shutil.copyfileobj(src, out)
            extracted += 1
    archive_path.unlink(missing_ok=True)
    if extracted == 0:
        raise RuntimeError(f"{source['sourceKey']}: archive subset matched no configured files")

def fetch_raw_files(source: dict, stage: Path) -> None:
    repo = source["repository"]
    commit = source["pin"]["commitSha"]
    for rel in source["acquisition"]["paths"]:
        if "*" in rel or "?" in rel or "[" in rel:
            raise RuntimeError(f"{source['sourceKey']}: RAW_FILES does not allow glob path {rel}")
        target = stage / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://raw.githubusercontent.com/{repo}/{commit}/{rel}"
        fetch_url(url, target)

def write_manifest(source: dict, dest: Path) -> None:
    files = []
    for path in sorted(p for p in dest.rglob("*") if p.is_file() and p.name != "source-manifest.json"):
        rel = path.relative_to(dest).as_posix()
        files.append({"path": rel, "sha256": sha256_file(path), "bytes": path.stat().st_size})
    manifest = {
        "schemaVersion": "1.0",
        "sourceKey": source["sourceKey"],
        "repository": source["repository"],
        "commitSha": source["pin"]["commitSha"],
        "datasetVersion": source["pin"].get("datasetVersion"),
        "registrySchemaVersion": load_registry()["schemaVersion"],
        "files": files,
    }
    (dest / "source-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def verify_cache(source: dict, dest: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    manifest_path = dest / "source-manifest.json"
    if not manifest_path.exists():
        return False, ["source-manifest.json missing"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, [f"invalid manifest: {exc}"]
    for field, expected in (
        ("sourceKey", source["sourceKey"]),
        ("repository", source["repository"]),
        ("commitSha", source["pin"]["commitSha"]),
        ("datasetVersion", source["pin"].get("datasetVersion")),
    ):
        if manifest.get(field) != expected:
            errors.append(f"{field} mismatch: {manifest.get(field)!r} != {expected!r}")
    for item in manifest.get("files", []):
        path = dest / item["path"]
        if not path.is_file():
            errors.append(f"missing cached file: {item['path']}")
            continue
        if sha256_file(path) != item["sha256"]:
            errors.append(f"sha256 mismatch: {item['path']}")
    return not errors, errors

def fetch_source(source: dict, root: Path, force: bool) -> None:
    final = root / source["acquisition"]["localSubdir"]
    if final.exists() and not force:
        ok, errors = verify_cache(source, final)
        if ok:
            print(f"{source['sourceKey']}: cache verified at {final}")
            return
        raise SystemExit(
            f"{source['sourceKey']}: existing cache does not match the pinned registry. "
            f"Review before replacement or rerun with --force. Details: {'; '.join(errors)}"
        )
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"{source['sourceKey'].lower()}-", dir=root) as tmp:
        stage = Path(tmp) / "content"
        stage.mkdir()
        method = source["acquisition"]["method"]
        if method == "GITHUB_ARCHIVE_SUBSET":
            fetch_archive_subset(source, stage)
        elif method == "RAW_FILES":
            fetch_raw_files(source, stage)
        else:
            raise RuntimeError(f"Unsupported acquisition method: {method}")
        write_manifest(source, stage)
        if final.exists():
            shutil.rmtree(final)
        shutil.move(str(stage), str(final))
    ok, errors = verify_cache(source, final)
    if not ok:
        raise RuntimeError(f"{source['sourceKey']}: post-fetch verification failed: {errors}")
    print(f"{source['sourceKey']}: fetched and verified at {final}")

def current_default_branch_sha(repository: str) -> str:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "hebrew-chinese-bible-research/1.0"}
    req = urllib.request.Request(f"https://api.github.com/repos/{repository}", headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        meta = json.load(response)
    req = urllib.request.Request(f"https://api.github.com/repos/{repository}/branches/{meta['default_branch']}", headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)["commit"]["sha"]

def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch version-pinned Hebrew corpus sources into a gitignored local cache.")
    parser.add_argument("--source", action="append", help="sourceKey to fetch; repeatable; default = all")
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    parser.add_argument("--force", action="store_true", help="replace a mismatched cache after explicit review")
    parser.add_argument("--list", action="store_true", help="list configured sources and exit")
    parser.add_argument("--check-upstream", action="store_true", help="compare pins with current upstream heads; never changes pins")
    args = parser.parse_args()
    registry = load_registry()
    sources = registry["sources"]
    if args.list:
        for s in sources:
            print(f"{s['sourceKey']}\t{s['repository']}\t{s['pin']['commitSha']}\t{s['pin'].get('datasetVersion') or '-'}")
        return 0
    selected = [source_by_key(registry, k) for k in args.source] if args.source else sources
    if args.check_upstream:
        for s in selected:
            current = current_default_branch_sha(s["repository"])
            pinned = s["pin"]["commitSha"]
            status = "PIN_CURRENT" if current == pinned else "UPSTREAM_MOVED_REVIEW_REQUIRED"
            print(f"{s['sourceKey']}\t{status}\tpinned={pinned}\tupstream={current}")
        return 0
    for source in selected:
        fetch_source(source, args.dest.resolve(), args.force)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
