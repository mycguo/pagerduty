#!/usr/bin/env python3
"""Backup monitors from database to JSON file."""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.storage import Storage
from src.storage.postgres_storage import PostgresStorage


def backup_monitors():
    """Backup all monitors to a timestamped JSON file."""
    print("=" * 60)
    print("Monitor Backup Tool")
    print("=" * 60)

    # Determine which storage backend to use
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        print("Using PostgreSQL storage")
        try:
            storage = PostgresStorage(database_url)
        except Exception as e:
            print(f"Failed to connect to PostgreSQL: {e}")
            print("Falling back to file storage")
            storage = Storage()
    else:
        print("Using file-based storage")
        storage = Storage()

    # Get all monitors
    monitors = storage.get_monitors()

    if not monitors:
        print("\nNo monitors found to backup")
        return

    print(f"\nFound {len(monitors)} monitors to backup:")
    for monitor in monitors:
        print(f"  - {monitor.name} (enabled={monitor.enabled})")

    # Create backup
    backup_data = [monitor.to_dict() for monitor in monitors]

    # Create backups directory
    backup_dir = Path(__file__).parent.parent / "backups"
    backup_dir.mkdir(exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"monitors_backup_{timestamp}.json"

    # Save backup
    with open(backup_file, 'w') as f:
        json.dump(backup_data, f, indent=2, default=str)

    print(f"\n✓ Backup saved to: {backup_file}")
    print(f"  File size: {backup_file.stat().st_size} bytes")

    # Also save as latest
    latest_file = backup_dir / "monitors_backup_latest.json"
    with open(latest_file, 'w') as f:
        json.dump(backup_data, f, indent=2, default=str)

    print(f"✓ Latest backup: {latest_file}")

    print(f"\n{'='*60}")
    print("Backup Complete")
    print(f"{'='*60}\n")

    return backup_file


def restore_monitors(backup_file: str):
    """Restore monitors from a backup file."""
    print("=" * 60)
    print("Monitor Restore Tool")
    print("=" * 60)

    backup_path = Path(backup_file)
    if not backup_path.exists():
        print(f"ERROR: Backup file not found: {backup_file}")
        return

    print(f"Loading backup from: {backup_path}")

    with open(backup_path, 'r') as f:
        backup_data = json.load(f)

    print(f"Found {len(backup_data)} monitors in backup")

    # Determine which storage backend to use
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        print("Using PostgreSQL storage")
        try:
            storage = PostgresStorage(database_url)
        except Exception as e:
            print(f"Failed to connect to PostgreSQL: {e}")
            return
    else:
        print("Using file-based storage")
        storage = Storage()

    # Import monitors
    from src.monitoring.monitor import Monitor

    restored_count = 0
    for monitor_dict in backup_data:
        try:
            monitor = Monitor.from_dict(monitor_dict)
            storage.save_monitor(monitor)
            print(f"  ✓ Restored: {monitor.name}")
            restored_count += 1
        except Exception as e:
            print(f"  ✗ Failed to restore {monitor_dict.get('name', 'unknown')}: {e}")

    print(f"\n{'='*60}")
    print(f"Restore Complete: {restored_count}/{len(backup_data)} monitors restored")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Backup and restore monitors")
    parser.add_argument("--restore", metavar="FILE", help="Restore monitors from backup file")

    args = parser.parse_args()

    if args.restore:
        restore_monitors(args.restore)
    else:
        backup_monitors()
