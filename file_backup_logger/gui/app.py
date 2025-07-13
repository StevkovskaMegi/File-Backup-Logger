from __future__ import annotations

import json
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from backup.manager import BackupManager

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "default.json"


def load_config() -> dict[str, str | bool]:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    return {"source": "", "destination": "", "compress": False}


def save_config(cfg: dict[str, str | bool]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2)


class BackupGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("File Backup Logger")
        self.geometry("520x220")
        self.resizable(False, False)

        # Load prefs
        cfg = load_config()
        self.var_source = tk.StringVar(value=str(cfg.get("source", "")))
        self.var_dest = tk.StringVar(value=str(cfg.get("destination", "")))
        self.var_compress = tk.BooleanVar(value=bool(cfg.get("compress", False)))

        # --- Layout -----------------------------------------------------
        paddings = {"padx": 8, "pady": 4}

        tk.Label(self, text="Source folder:").grid(row=0, column=0, sticky="e", **paddings)
        tk.Entry(self, textvariable=self.var_source, width=40).grid(row=0, column=1, **paddings)
        tk.Button(self, text="Browse…", command=self.browse_source).grid(row=0, column=2, **paddings)

        tk.Label(self, text="Destination root:").grid(row=1, column=0, sticky="e", **paddings)
        tk.Entry(self, textvariable=self.var_dest, width=40).grid(row=1, column=1, **paddings)
        tk.Button(self, text="Browse…", command=self.browse_dest).grid(row=1, column=2, **paddings)

        tk.Checkbutton(self, text="Compress to ZIP", variable=self.var_compress).grid(
            row=2, column=1, sticky="w", **paddings
        )

        self.btn_backup = tk.Button(self, text="Start Backup", command=self.start_backup)
        self.btn_backup.grid(row=3, column=1, **paddings)

        self.status = tk.StringVar(value="Ready.")
        tk.Label(self, textvariable=self.status).grid(row=4, column=0, columnspan=3, sticky="w", **paddings)

        # Save prefs on close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # -----------------------------------------------------------------
    # UI callbacks
    # -----------------------------------------------------------------
    def browse_source(self) -> None:
        folder = filedialog.askdirectory(title="Select source folder")
        if folder:
            self.var_source.set(folder)

    def browse_dest(self) -> None:
        folder = filedialog.askdirectory(title="Select destination root")
        if folder:
            self.var_dest.set(folder)

    def start_backup(self) -> None:
        src = Path(self.var_source.get())
        dest_root = Path(self.var_dest.get())
        compress = self.var_compress.get()

        if not src.exists():
            messagebox.showerror("Error", "Source folder does not exist.")
            return
        if not dest_root.exists():
            messagebox.showerror("Error", "Destination folder does not exist.")
            return

        self.btn_backup.config(state="disabled")
        self.status.set("Backing up… please wait.")

        def task() -> None:
            try:
                mgr = BackupManager(src, dest_root, compress=compress)
                backup_path = mgr.run()
                self.status.set(f"Success → {backup_path}")
                messagebox.showinfo("Backup completed", f"Backup created at: {backup_path}")
                
            except Exception as exc:  
                self.status.set(f"Error: {exc}")
                messagebox.showerror("Backup failed", str(exc))
            finally:
                self.btn_backup.config(state="normal")

        threading.Thread(target=task, daemon=True).start()

    def on_close(self) -> None:
        save_config({
            "source": self.var_source.get(),
            "destination": self.var_dest.get(),
            "compress": self.var_compress.get(),
        })
        self.destroy()


if __name__ == "__main__":
    BackupGUI().mainloop()