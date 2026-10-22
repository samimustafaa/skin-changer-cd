# sg0hann Skin Changer

A lightweight Windows launcher **prototype** for Creative Destruction.

- Son Gohan and Steve skin selections
- Automatically detects whether Creative Destruction is running
- Saves preferences locally
- Checks GitHub Releases for updates at startup, with a manual update button
- Windows installer built by GitHub Actions

**Important:** Does not yet modify in-game character models or detect whether Fashion Guru is equipped. Actual in-game replacement requires approved game assets and integration.

## Install
Download the newest `-setup.exe` from [Releases](https://github.com/samimustafaa/skin-changer-cd/releases).

## Build
Run `pip install -r requirements-build.txt`, then `pyinstaller --onefile --windowed --name sg0hann-SkinChanger main.py`. The release workflow packages the executable using Inno Setup.

Updates: the app checks the latest published GitHub Release, asks permission, then downloads and starts its installer. Your local selections persist in `%LOCALAPPDATA%\sg0hann\SkinChanger\settings.json`.
