"""sg0hann Skin Changer - Windows launcher prototype. No game files modified."""
import csv
import io
import json
import os
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox, filedialog
from safety import create_backup, restore_backup, validate_package, inspect_folder, SafetyError
from urllib.request import Request, urlopen

VERSION = "0.3.0"
REPO = "samimustafaa/skin-changer-cd"
BASE = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "sg0hann" / "SkinChanger"
CONFIG = BASE / "settings.json"
SKINS = {
    "gohan": ("SON GOHAN", "Fortnite / Dragon Ball", "https://fortnite.gg/cosmetics?id=9068"),
    "steve": ("STEVE", "Minecraft / Classic", "https://www.minecraftskins.com/skin/23262893/steve/")
}
GAME_PROCESSES = {"client.exe", "creativedestruction.exe", "creative destruction.exe"}
BG, PANEL, MUTED, FG, GOLD = "#0c1019", "#1c2534", "#9ca9bd", "#f3f6ff", "#f8c63e"

def game_running():
    if sys.platform != "win32":
        return False
    try:
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        p = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True,
                           text=True, creationflags=flags, timeout=5)
        return any(r and r[0].strip().lower() in GAME_PROCESSES
                   for r in csv.reader(io.StringIO(p.stdout)))
    except (OSError, subprocess.TimeoutExpired):
        return False

def read_settings():
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}

def write_settings(data):
    BASE.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(data, indent=2), encoding="utf-8")

def newer(latest, current):
    def parse(value):
        parts = value.lstrip("v").split(".")
        return tuple(int(x.split("-")[0]) for x in parts[:3])
    try:
        return parse(latest) > parse(current)
    except ValueError:
        return False

def get_update():
    req = Request("https://api.github.com/repos/" + REPO + "/releases/latest",
                  headers={"Accept": "application/vnd.github+json", "User-Agent": "sg0hann-SkinChanger/" + VERSION})
    with urlopen(req, timeout=10) as response:
        release = json.load(response)
    tag = release.get("tag_name", "")
    if not newer(tag, VERSION):
        return None
    for item in release.get("assets", []):
        if item.get("name", "").lower().endswith("-setup.exe"):
            return tag, item["browser_download_url"]
    return None

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("sg0hann Skin Changer")
        self.geometry("780x690")
        self.minsize(740, 650)
        self.configure(bg=BG)
        self.settings = read_settings()
        self.selected = self.settings.get("selected", "")
        self.buttons = {}
        self.game_folder = Path(self.settings.get("game_folder", "C:/Creative Destruction"))
        self.package_path = None
        self.label("SG0HANN  /  SKIN CHANGER", 24, FG, True).pack(anchor="w", padx=30, pady=(25, 3))
        self.label("VERSION " + VERSION + "  •  Fashion Guru concept launcher", 11, MUTED).pack(anchor="w", padx=30)
        self.status = self.label("Checking for Creative Destruction...", 12, MUTED, True)
        self.status.pack(anchor="w", padx=30, pady=(22, 14))
        cards = tk.Frame(self, bg=BG)
        cards.pack(fill="both", expand=True, padx=24)
        for key, (name, subtitle, url) in SKINS.items():
            card = tk.Frame(cards, bg=PANEL, padx=18, pady=18, highlightthickness=1,
                            highlightbackground="#394658")
            card.pack(side="left", fill="both", expand=True, padx=6)
            art = tk.Canvas(card, height=125, bg="#28354a", highlightthickness=0)
            art.pack(fill="x", pady=(0, 15))
            art.create_text(130, 62, text="STEVE" if key == "steve" else "GOHAN",
                            fill=GOLD, font=("Segoe UI", 23, "bold"))
            self.label(name, 19, FG, True, card).pack(anchor="w")
            self.label(subtitle, 10, MUTED, False, card).pack(anchor="w", pady=(0, 18))
            btn = tk.Button(card, command=lambda k=key: self.select(k), relief="flat",
                            font=("Segoe UI", 11, "bold"), cursor="hand2", pady=12)
            btn.pack(fill="x")
            self.buttons[key] = btn
            tk.Button(card, text="View original skin ↗", command=lambda u=url: webbrowser.open(u),
                      fg=MUTED, bg=PANEL, bd=0, cursor="hand2").pack(pady=(13, 0))
        self.message = self.label("Select a concept. In-game replacement is not implemented.", 10, MUTED)
        self.message.pack(anchor="w", padx=30, pady=(15, 5))
        safety = tk.Frame(self, bg=PANEL, padx=12, pady=12)
        safety.pack(fill="x", padx=30, pady=(4, 5))
        self.label("SAFE INSTALLATION CONTROLS", 12, FG, True, safety).pack(anchor="w")
        self.folder_label = self.label("Game folder: " + str(self.game_folder), 10, MUTED, False, safety)
        self.folder_label.pack(anchor="w", pady=(5, 5))
        actions = tk.Frame(safety, bg=PANEL)
        actions.pack(fill="x")
        for title, callback in [("GAME FOLDER", self.pick_folder), ("CHECK PACKAGE", self.pick_package),
                                ("BACK UP", self.backup), ("RESTORE", self.restore)]:
            tk.Button(actions, text=title, command=callback, bg="#354257", fg=FG, relief="flat",
                      padx=9, pady=8).pack(side="left", padx=(0, 7))
        self.apply_button = tk.Button(safety, text="APPLY SKIN — UNAVAILABLE (NO VERIFIED GAME ADAPTER)",
                                      state="disabled", disabledforeground=MUTED, bg="#344052",
                                      relief="flat", padx=12, pady=10)
        self.apply_button.pack(fill="x", pady=(10, 0))
        self.label("No memory hooks, injection or anti-cheat workarounds. Backups are read-only copies.",
                   9, MUTED, False, safety).pack(anchor="w", pady=(8, 0))
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=30, pady=(8, 26))
        for title, callback in [("RESET SELECTION", self.reset),
                                 ("CHECK FOR UPDATES", lambda: self.check_updates(True))]:
            tk.Button(bar, text=title, command=callback, relief="flat", fg=FG,
                      bg=PANEL, font=("Segoe UI", 10, "bold"), padx=15, pady=10).pack(side="left", padx=(0, 10))
        self.paint()
        self.after(100, self.scan)
        self.after(1500, lambda: self.check_updates(False))

    def label(self, text, size, fg, bold=False, parent=None):
        return tk.Label(parent or self, text=text, font=("Segoe UI", size, "bold" if bold else "normal"),
                        bg=PANEL if parent else BG, fg=fg, anchor="w")

    def paint(self):
        for key, btn in self.buttons.items():
            active = self.selected == key
            btn.config(text="✓ SELECTED" if active else "SELECT",
                       bg=GOLD if active else "#354257", fg=BG if active else FG)

    def select(self, key):
        self.selected = key
        self.settings["selected"] = key
        write_settings(self.settings)
        self.paint()
        self.message.config(text=SKINS[key][0] + " saved. No game assets were changed.")

    def reset(self):
        self.selected = ""
        self.settings.pop("selected", None)
        write_settings(self.settings)
        self.paint()
        self.message.config(text="Selection cleared. Original game files remain untouched.")

    def pick_folder(self):
        folder = filedialog.askdirectory(initialdir=str(self.game_folder), title="Select Creative Destruction folder")
        if folder:
            self.game_folder = Path(folder)
            self.settings["game_folder"] = str(self.game_folder)
            write_settings(self.settings)
            self.folder_label.config(text="Game folder: " + str(self.game_folder))
            self.message.config(text="Folder selected. Original files have not been changed.")

    def pick_package(self):
        path = filedialog.askopenfilename(title="Inspect skin package", filetypes=[("Skin package", "*.zip")])
        if not path:
            return
        try:
            info = validate_package(Path(path))
            self.package_path = Path(path)
            messagebox.showinfo("Package verified (metadata only)",
                                "Package: " + info["name"] + "\\nTarget: " + info["target"] +
                                "\\nAssets: " + str(info["asset_count"]) +
                                "\\nNo game installation support is available yet.")
            self.message.config(text="Package metadata validated. Apply remains disabled.")
        except SafetyError as err:
            messagebox.showerror("Invalid package", str(err))

    def backup(self):
        if game_running():
            messagebox.showwarning("Game running", "Close Creative Destruction before making a backup.")
            return
        try:
            files = inspect_folder(self.game_folder)
            if not files:
                messagebox.showwarning("No files", "No recognized game archives were found in the selected folder.")
                return
            dest = create_backup(self.game_folder, BASE / "backups", files)
            self.message.config(text="Backup created: " + str(dest))
            messagebox.showinfo("Backup complete", "Read-only backup created at:\\n" + str(dest))
        except (OSError, SafetyError) as err:
            messagebox.showerror("Backup failed", str(err))

    def restore(self):
        if game_running():
            messagebox.showwarning("Game running", "Close Creative Destruction before restoring.")
            return
        folder = filedialog.askdirectory(initialdir=str(BASE / "backups"), title="Select a backup folder")
        if not folder:
            return
        try:
            restore_backup(Path(folder), self.game_folder)
            self.message.config(text="Backup successfully restored.")
            messagebox.showinfo("Restore complete", "Verified archive copies restored.")
        except (OSError, SafetyError) as err:
            messagebox.showerror("Restore blocked", str(err))

    def scan(self):
        running = game_running()
        self.status.config(text="●  GAME DETECTED — CLOSE BEFORE EDITING" if running else "●  GAME NOT DETECTED",
                           fg="#55dca1" if running else "#f18188")
        self.after(2500, self.scan)

    def check_updates(self, manual):
        self.message.config(text="Checking GitHub Releases for updates..." if manual else self.message.cget("text"))
        def work():
            try:
                update = get_update()
                self.after(0, lambda: self.show_update(update, manual))
            except Exception as error:
                if manual:
                    self.after(0, lambda: messagebox.showwarning("Update check failed", str(error)))
        threading.Thread(target=work, daemon=True).start()

    def show_update(self, update, manual):
        if not update:
            if manual:
                messagebox.showinfo("Up to date", "You already have the latest available release.")
            return
        tag, url = update
        if not messagebox.askyesno("Update available", "Version " + tag + " is available. Download and install now?"):
            return
        self.message.config(text="Downloading " + tag + " securely from GitHub...")
        def download():
            try:
                import tempfile
                target = Path(tempfile.gettempdir()) / "sg0hann-SkinChanger-update-setup.exe"
                request = Request(url, headers={"User-Agent": "sg0hann-SkinChanger/" + VERSION})
                with urlopen(request, timeout=60) as source, target.open("wb") as destination:
                    import shutil
                    shutil.copyfileobj(source, destination)
                subprocess.Popen([str(target), "/SILENT", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS"])
                self.after(0, self.destroy)
            except Exception as error:
                self.after(0, lambda: messagebox.showerror("Update failed", str(error)))
        threading.Thread(target=download, daemon=True).start()

if __name__ == "__main__":
    App().mainloop()
