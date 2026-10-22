# sg0hann Skin Changer (v0.3.0)

A lightweight Python Windows launcher for Creative Destruction.

## What works
- Detects game process `client.exe`, and warns against editing while running
- Son Gohan / Steve **selection only** (no actual in-game skin replacement)
- Read-only archive backup of recognized `res/*.npk` files, with SHA-256 verification
- Restore verified backup copies when the game is closed
- Inspect user-selected ZIP package manifests; validate safe paths, limits, checksums, and `fashion-guru` target
- GitHub Release update checking and installer download (requires user confirmation)

## Important
**Apply Skin is deliberately disabled.** No supported game asset adapter or Fashion Guru mesh/rig mapping has been established. Nothing injects into the game, modifies its memory, bypasses anti-cheat, or secretly edits NPK archives. A valid package is NOT proof of game compatibility. Do not test unapproved asset changes in anti-cheat protected sessions.

## Install
Download Windows `-setup.exe` from [Releases](https://github.com/samimustafaa/skin-changer-cd/releases).

## Build
```powershell
pip install -r requirements-build.txt
python -m unittest discover -s tests -v
pyinstaller --noconfirm --clean --onefile --windowed --name sg0hann-SkinChanger main.py
```

Backups and preferences: `%LOCALAPPDATA%\sg0hann\SkinChanger`. Keep enough disk space: backing up large NPK archives can require 1+ GB.

## Example package format (metadata validation only)
```json
{"format":1,"name":"Example","target":"fashion-guru","assets":[{"path":"assets/model.glb","sha256":"<sha256-of-model>"}]}
```
The package inspector never unpacks assets into the game. Asset installation support needs an explicitly verified owner-approved loader.
