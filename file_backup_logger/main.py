from pathlib import Path

from backup.manager import BackupManager


def main() -> None:
    source = Path(input("Enter path to folder to back up: ").strip())
    destination = Path(input("Enter destination root folder: ").strip())
    compress = input("Compress to ZIP? [y/N]: ").strip().lower() == "y"
    version = input("Optional version tag (press Enter to skip): ").strip() or None

    manager = BackupManager(source, destination, compress=compress, version=version)
    try:
        backup_path = manager.run()
        print(f"Backup finished → {backup_path}")
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
