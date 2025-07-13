# File Backup Logger

A simple, cross-platform backup utility that

* copies **files and folders** (plain or ZIP-compressed)
* adds an automatic **timestamp** and optional **version tag**
* writes a detailed **log file** (status, file count, duration)
* remembers your last paths in a tiny **JSON config**
* ships with both a **command-line interface** and a **Tkinter GUI**


---

## Table of contents
1. [Screenshots](#screenshots)
2. [Quick start](#quick-start)
3. [CLI usage](#cli-usage)
4. [GUI usage](#gui-usage)
5. [Configuration file](#configuration-file)
6. [Log file](#log-file)
7. [Project layout](#project-layout)

---

## Screenshots
| GUI – ready | GUI – success |
|-------------|---------------|
| ![Source / destination picker](/file_backup_logger/docs/img/gui_idle.png) | ![Backup finished](/file_backup_logger/docs/img/gui_done.png) |


---

## Quick start

```bash
# clone & enter the repo
git clone https://github.com/StevkovskaMegi/File-Backup-Logger
cd file-backup-logger        

python3 -m venv .venv
source .venv/bin/activate           

# install dev requirements (only pytest)
pip install -r requirements.txt
``` 

---

## CLI usage
```bash
python main.py
```
You’ll be prompted for
source – the folder to back up
destination – where to store backups
compress – y for .zip, anything else for plain copy
version tag – free-form text (e.g. v2.3.1); leave blank to skip

---

## GUI usage
```bash
python -m gui.app
```
Browse… to pick source & destination
Tick Compress to ZIP if desired
Click Start Backup – progress runs on a background thread so the UI stays responsive.

---

## Configuration file
config/default.json
{
  "source": "/last/used/source",
  "destination": "/last/used/destination",
  "compress": false
}

---

## Log file
All operations are appended to logs/backup.log, e.g.
2025-07-14 00:55:02 | INFO | Creating ZIP archive → /backups/myproject_backup_2025-07-14_00-55-02.zip
2025-07-14 00:55:05 | INFO | Backup summary | time=2025-07-14 00:55:05 | src=/Users/me/myproject | dest=/backups/myproject_backup_2025-07-14_00-55-02.zip | files=128 | duration=2.73s

---

## Project layout
file_backup_logger/
├── backup/            ← core engine (BackupManager)
│   └── manager.py
├── gui/               ← Tkinter front-end
│   └── app.py
├── logs/              ← backup.log + generated backups
├── main.py            ← CLI entry-point
├── requirements.txt   ← dev-only deps (pytest)
└── README.md
config/            ← default.json (saved prefs)

