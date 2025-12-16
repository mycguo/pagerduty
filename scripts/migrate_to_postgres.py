#!/usr/bin/env python3
"""Migrate default monitors to PostgreSQL database."""
import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.monitoring.monitor import Monitor
from src.storage.postgres_storage import PostgresStorage


def migrate_default_monitors():
    """Migrate default monitors from JSON file to PostgreSQL."""
    print("=" * 60)
    print("Migrating Default Monitors to PostgreSQL")
    print("=" * 60)

    # Check if DATABASE_URL is set
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        print("Cannot migrate to PostgreSQL")
        sys.exit(1)

    print(f"Database URL: {database_url[:20]}...")

    # Initialize Postgres storage
    try:
        storage = PostgresStorage(database_url)
        print("✓ Connected to PostgreSQL database")
    except Exception as e:
        print(f"✗ Failed to connect to PostgreSQL: {e}")
        sys.exit(1)

    # Check if monitors already exist
    existing_monitors = storage.get_monitors()
    if existing_monitors:
        print(f"\n⚠ Database already contains {len(existing_monitors)} monitors")
        print("Skipping migration to avoid duplicates")
        for monitor in existing_monitors:
            print(f"  - {monitor.name}")
        return

    # Load default monitors from JSON
    default_monitors_path = Path(__file__).parent.parent / "default_monitors.json"
    if not default_monitors_path.exists():
        print(f"✗ Default monitors file not found: {default_monitors_path}")
        print("Creating empty database (no default monitors to migrate)")
        return

    print(f"\nLoading default monitors from: {default_monitors_path}")
    with open(default_monitors_path, 'r') as f:
        monitors_data = json.load(f)

    print(f"✓ Found {len(monitors_data)} monitors to migrate")

    # Migrate each monitor
    migrated_count = 0
    for monitor_dict in monitors_data:
        try:
            monitor = Monitor.from_dict(monitor_dict)
            storage.save_monitor(monitor)
            print(f"  ✓ Migrated: {monitor.name}")
            migrated_count += 1
        except Exception as e:
            print(f"  ✗ Failed to migrate {monitor_dict.get('name', 'unknown')}: {e}")

    print(f"\n{'='*60}")
    print(f"Migration Complete: {migrated_count}/{len(monitors_data)} monitors migrated")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    migrate_default_monitors()
