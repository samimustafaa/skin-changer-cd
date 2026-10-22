"""Read-only archive backup and package validation; no in-game skin modification."""
import hashlib
import json
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath

class SafetyError(ValueError):
    pass

RECOGNIZED = ("char.npk", "model.npk", "model_regular.npk", "item.npk", "common.npk", "script.npk")
MAX_PACKAGE_BYTES = 350 * 1024 * 1024

def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as src:
        for chunk in iter(lambda: src.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()

def inspect_folder(folder):
    folder = Path(folder)
    if not folder.is_dir():
        raise SafetyError("Select an existing Creative Destruction installation folder.")
    res = folder / "res"
    if not res.is_dir():
        raise SafetyError("Missing res folder. Select the main Creative Destruction directory.")
    return [res / name for name in RECOGNIZED if (res / name).is_file()]

def create_backup(game_folder, backup_root, files):
    root = Path(game_folder).resolve()
    backup_root = Path(backup_root)
    folder = backup_root / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    folder.mkdir(parents=True, exist_ok=False)
    entries = []
    try:
        for src in files:
            src = Path(src).resolve()
            if not src.is_relative_to(root) or src.parent != root / "res" or src.name not in RECOGNIZED:
                raise SafetyError("Unexpected backup source: " + str(src))
            dst = folder / "res" / src.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            checksum = digest(dst)
            if checksum != digest(src):
                raise SafetyError("File verification failed: " + src.name)
            entries.append({"relative_path": "res/" + src.name, "sha256": checksum})
        (folder / "manifest.json").write_text(json.dumps({"format": 1, "files": entries}, indent=2))
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)
        raise
    return folder

def restore_backup(backup_folder, game_folder):
    backup_folder = Path(backup_folder).resolve()
    root = Path(game_folder).resolve()
    inspect_folder(root)  # verify correct root and res folder
    manifest = backup_folder / "manifest.json"
    if not manifest.is_file():
        raise SafetyError("This folder is not a backup created by sg0hann Skin Changer.")
    data = json.loads(manifest.read_text())
    entries = data.get("files")
    if data.get("format") != 1 or not isinstance(entries, list) or not entries:
        raise SafetyError("Invalid backup manifest.")
    validated = []
    for item in entries:
        rel = item.get("relative_path", "")
        if rel not in ["res/" + name for name in RECOGNIZED]:
            raise SafetyError("Unexpected file in backup manifest.")
        src = backup_folder / Path(rel)
        dst = root / Path(rel)
        if not src.is_file() or not dst.is_file() or not isinstance(item.get("sha256"), str):
            raise SafetyError("Backup or destination is missing: " + rel)
        if digest(src) != item["sha256"]:
            raise SafetyError("Backup checksum failed: " + rel)
        validated.append((src, dst))
    # Restore is intended only for known-original backups; reject unexpected modifications.
    for src, dst in validated:
        temp = dst.with_name(dst.name + ".sg0hann-restore.tmp")
        try:
            shutil.copy2(src, temp)
            if digest(temp) != digest(src):
                raise SafetyError("Restore checksum mismatch.")
            os.replace(temp, dst)
        finally:
            temp.unlink(missing_ok=True)

def validate_package(path):
    path = Path(path)
    if not zipfile.is_zipfile(path):
        raise SafetyError("Choose a valid ZIP package.")
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if len(names) > 100 or len(set(names)) != len(names):
            raise SafetyError("Unreasonable or duplicate ZIP entries.")
        for entry in z.infolist():
            p = PurePosixPath(entry.filename)
            if p.is_absolute() or ".." in p.parts or "\\" in entry.filename or entry.file_size > MAX_PACKAGE_BYTES:
                raise SafetyError("Unsafe path or oversized package entry.")
        if sum(i.file_size for i in z.infolist()) > MAX_PACKAGE_BYTES:
            raise SafetyError("Package exceeds unpacked-size limit.")
        if "manifest.json" not in names:
            raise SafetyError("Missing manifest.json.")
        manifest = json.loads(z.read("manifest.json"))
        if manifest.get("format") != 1 or manifest.get("target") != "fashion-guru":
            raise SafetyError("Only Fashion Guru-targeted manifests are accepted.")
        assets = manifest.get("assets", [])
        if not isinstance(assets, list) or not assets:
            raise SafetyError("Package manifest must list at least one asset.")
        for asset in assets:
            rel = asset.get("path", "")
            if rel not in names or not rel.startswith("assets/") or not isinstance(asset.get("sha256"), str):
                raise SafetyError("Invalid asset reference.")
            with z.open(rel) as stream:
                h = hashlib.sha256()
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    h.update(chunk)
            if h.hexdigest() != asset["sha256"]:
                raise SafetyError("Package asset checksum mismatch.")
        return {"name": str(manifest.get("name", "Unnamed"))[:80], "target": "Fashion Guru", "asset_count": len(assets)}
