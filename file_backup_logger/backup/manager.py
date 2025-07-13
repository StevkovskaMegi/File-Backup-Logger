from __future__ import annotations

import os
import shutil
import time
import zipfile
from datetime import datetime
from pathlib import Path
import logging

class BackupManager:
    """Core backup engine with optional ZIP compression and detailed logging."""

    def __init__(
        self,
        source: Path,
        destination_root: Path,
        *,
        compress: bool = False,
        version: str | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.source = source.expanduser().resolve()
        self.destination_root = destination_root.expanduser().resolve()
        self.compress = compress
        self.version = version
        self.logger = logger or self._configure_logger()

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def run(self) -> Path:
        """Execute the backup and return the created archive/folder path."""
        start_ts = time.perf_counter()
        ts_readable = datetime.now().isoformat(sep=" ", timespec="seconds")

        if not self.source.exists():
            msg = f"Source path does not exist: {self.source}"
            self.logger.error(msg)
            raise FileNotFoundError(msg)

        # Count files beforehand so we can report even if copy fails midway.
        file_count = self._count_files(self.source)
        backup_name = self._generate_backup_name(self.source, version=self.version)

        try:
            if self.compress:
                dest = self.destination_root / f"{backup_name}.zip"
                self._zip_directory(self.source, dest)
            else:
                dest = self.destination_root / backup_name
                shutil.copytree(self.source, dest, dirs_exist_ok=False)
        except PermissionError as exc:
            self.logger.exception("Permission denied during backup.")
            raise
        except Exception as exc:  # noqa: BLE001
            self.logger.exception("Unhandled error during backup.")
            raise
        finally:
            duration = time.perf_counter() - start_ts
            self.logger.info(
                "Backup summary | time=%s | src=%s | dest=%s | files=%s | duration=%.2fs",
                ts_readable,
                self.source,
                dest if 'dest' in locals() else 'N/A',
                file_count,
                duration,
            )

        return dest

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _count_files(directory: Path) -> int:
        return sum(len(files) for _, _, files in os.walk(directory))

    @staticmethod
    def _generate_backup_name(source: Path, *, version: str | None = None) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base = f"{source.stem}_backup_{timestamp}"
        if version:
            base += f"_v{version}"
        return base

    def _configure_logger(self) -> logging.Logger:
        log_dir = Path(__file__).resolve().parents[2] / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "backup.log"

        logger = logging.getLogger("backup")
        logger.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
        return logger

    def _zip_directory(self, source: Path, dest_zip: Path) -> None:
        """Create a compressed ZIP archive from *source* at *dest_zip*."""
        self.logger.info("Creating ZIP archive → %s", dest_zip)
        with zipfile.ZipFile(dest_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(source):
                for file in files:
                    full_path = Path(root) / file
                    rel_path = full_path.relative_to(source.parent)
                    zf.write(full_path, arcname=rel_path)