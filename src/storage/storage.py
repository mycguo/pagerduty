"""Storage for monitors and test results."""
import json
import os
from typing import List, Optional
from pathlib import Path

from src.monitoring.monitor import Monitor, TestRun


class Storage:
    """Handles persistence of monitors and test results."""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize storage.

        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.monitors_file = self.data_dir / "monitors.json"
        self.results_file = self.data_dir / "test_results.json"

        # Initialize files if they don't exist
        if not self.monitors_file.exists():
            self._save_json(self.monitors_file, [])
        if not self.results_file.exists():
            self._save_json(self.results_file, [])

    def _save_json(self, file_path: Path, data: list):
        """Save data to JSON file."""
        # Use atomic write: write to temp file first, then rename
        # This ensures data integrity and prevents partial writes
        temp_file = file_path.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())  # Force write to disk
        
        # Atomic rename (works on most filesystems)
        temp_file.replace(file_path)

    def _load_json(self, file_path: Path) -> list:
        """Load data from JSON file."""
        with open(file_path, 'r') as f:
            return json.load(f)

    def save_monitor(self, monitor: Monitor):
        """Save or update a monitor."""
        monitors = self._load_json(self.monitors_file)

        # Check if monitor exists
        existing_idx = None
        for idx, m in enumerate(monitors):
            if m['id'] == monitor.id:
                existing_idx = idx
                break

        monitor_dict = monitor.to_dict()

        if existing_idx is not None:
            monitors[existing_idx] = monitor_dict
        else:
            monitors.append(monitor_dict)

        self._save_json(self.monitors_file, monitors)

    def get_monitors(self) -> List[Monitor]:
        """Get all monitors."""
        monitors_data = self._load_json(self.monitors_file)
        return [Monitor.from_dict(m) for m in monitors_data]

    def get_monitor(self, monitor_id: str) -> Optional[Monitor]:
        """Get a specific monitor by ID."""
        monitors = self.get_monitors()
        for monitor in monitors:
            if monitor.id == monitor_id:
                return monitor
        return None

    def delete_monitor(self, monitor_id: str):
        """Delete a monitor."""
        monitors = self._load_json(self.monitors_file)
        monitors = [m for m in monitors if m['id'] != monitor_id]
        self._save_json(self.monitors_file, monitors)

    def save_test_run(self, test_run: TestRun):
        """Save a test run result."""
        results = self._load_json(self.results_file)
        results.append(test_run.to_dict())

        # Keep only last 1000 results to avoid file growing too large
        if len(results) > 1000:
            results = results[-1000:]

        self._save_json(self.results_file, results)

    def get_test_runs(self, monitor_id: Optional[str] = None, limit: int = 100) -> List[TestRun]:
        """
        Get test run results.

        Args:
            monitor_id: Optional monitor ID to filter by
            limit: Maximum number of results to return

        Returns:
            List of TestRun objects
        """
        results = self._load_json(self.results_file)

        # Filter by monitor_id if provided
        if monitor_id:
            results = [r for r in results if r['monitor_id'] == monitor_id]

        # Sort by started_at descending (most recent first)
        results.sort(key=lambda x: x['started_at'], reverse=True)

        # Limit results
        results = results[:limit]

        return [TestRun.from_dict(r) for r in results]

    def get_latest_test_run(self, monitor_id: str) -> Optional[TestRun]:
        """Get the most recent test run for a monitor."""
        runs = self.get_test_runs(monitor_id=monitor_id, limit=1)
        return runs[0] if runs else None
