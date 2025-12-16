"""PostgreSQL storage backend for monitors and test results."""
import json
import os
from typing import List, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

from src.monitoring.monitor import Monitor, TestRun


class PostgresStorage:
    """Handles persistence of monitors and test results using PostgreSQL."""

    def __init__(self, database_url: str = None):
        """
        Initialize PostgreSQL storage.

        Args:
            database_url: PostgreSQL connection URL. If None, uses DATABASE_URL env var.
        """
        import logging
        logger = logging.getLogger(__name__)

        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required for PostgreSQL storage")

        logger.info(f"Initializing PostgreSQL storage")
        print(f"[PostgresStorage] Connecting to database...")

        # Initialize database schema
        self._init_schema()

        logger.info("PostgreSQL storage initialized successfully")
        print(f"[PostgresStorage] Database schema initialized")

    def _get_connection(self):
        """Get a database connection."""
        return psycopg2.connect(self.database_url)

    def _init_schema(self):
        """Initialize database schema if it doesn't exist."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # Create monitors table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS monitors (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        url TEXT NOT NULL,
                        steps JSONB NOT NULL,
                        enabled BOOLEAN DEFAULT TRUE,
                        schedule TEXT DEFAULT '*/5 * * * *',
                        alert_emails JSONB DEFAULT '[]'::jsonb,
                        slack_webhook_url TEXT,
                        alerts_enabled BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL
                    )
                """)

                # Create test_runs table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS test_runs (
                        id TEXT PRIMARY KEY,
                        monitor_id TEXT NOT NULL REFERENCES monitors(id) ON DELETE CASCADE,
                        status TEXT NOT NULL,
                        started_at TIMESTAMP NOT NULL,
                        completed_at TIMESTAMP,
                        duration_ms INTEGER,
                        error_message TEXT,
                        screenshot_path TEXT,
                        step_results JSONB DEFAULT '[]'::jsonb
                    )
                """)

                # Create index on monitor_id for faster queries
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_test_runs_monitor_id
                    ON test_runs(monitor_id)
                """)

                # Create index on started_at for sorting
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_test_runs_started_at
                    ON test_runs(started_at DESC)
                """)

                conn.commit()

    def save_monitor(self, monitor: Monitor):
        """Save or update a monitor."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO monitors (
                        id, name, url, steps, enabled, schedule,
                        alert_emails, slack_webhook_url, alerts_enabled,
                        created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        url = EXCLUDED.url,
                        steps = EXCLUDED.steps,
                        enabled = EXCLUDED.enabled,
                        schedule = EXCLUDED.schedule,
                        alert_emails = EXCLUDED.alert_emails,
                        slack_webhook_url = EXCLUDED.slack_webhook_url,
                        alerts_enabled = EXCLUDED.alerts_enabled,
                        updated_at = EXCLUDED.updated_at
                """, (
                    monitor.id,
                    monitor.name,
                    monitor.url,
                    json.dumps(monitor.steps),
                    monitor.enabled,
                    monitor.schedule,
                    json.dumps(monitor.alert_emails),
                    monitor.slack_webhook_url,
                    monitor.alerts_enabled,
                    monitor.created_at,
                    monitor.updated_at
                ))
                conn.commit()
                print(f"[PostgresStorage] Saved monitor: {monitor.name}")

    def get_monitors(self) -> List[Monitor]:
        """Get all monitors."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM monitors ORDER BY created_at")
                rows = cur.fetchall()
                return [self._row_to_monitor(row) for row in rows]

    def get_monitor(self, monitor_id: str) -> Optional[Monitor]:
        """Get a specific monitor by ID."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM monitors WHERE id = %s", (monitor_id,))
                row = cur.fetchone()
                return self._row_to_monitor(row) if row else None

    def delete_monitor(self, monitor_id: str):
        """Delete a monitor."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM monitors WHERE id = %s", (monitor_id,))
                conn.commit()
                print(f"[PostgresStorage] Deleted monitor: {monitor_id}")

    def save_test_run(self, test_run: TestRun):
        """Save a test run result."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO test_runs (
                        id, monitor_id, status, started_at, completed_at,
                        duration_ms, error_message, screenshot_path, step_results
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    test_run.id,
                    test_run.monitor_id,
                    test_run.status,
                    test_run.started_at,
                    test_run.completed_at,
                    test_run.duration_ms,
                    test_run.error_message,
                    test_run.screenshot_path,
                    json.dumps(test_run.step_results)
                ))
                conn.commit()

    def get_test_runs(self, monitor_id: Optional[str] = None, limit: int = 100) -> List[TestRun]:
        """Get test run results."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if monitor_id:
                    cur.execute("""
                        SELECT * FROM test_runs
                        WHERE monitor_id = %s
                        ORDER BY started_at DESC
                        LIMIT %s
                    """, (monitor_id, limit))
                else:
                    cur.execute("""
                        SELECT * FROM test_runs
                        ORDER BY started_at DESC
                        LIMIT %s
                    """, (limit,))

                rows = cur.fetchall()
                return [self._row_to_test_run(row) for row in rows]

    def get_latest_test_run(self, monitor_id: str) -> Optional[TestRun]:
        """Get the most recent test run for a monitor."""
        runs = self.get_test_runs(monitor_id=monitor_id, limit=1)
        return runs[0] if runs else None

    def _row_to_monitor(self, row: dict) -> Monitor:
        """Convert database row to Monitor object."""
        return Monitor(
            id=row['id'],
            name=row['name'],
            url=row['url'],
            steps=row['steps'] if isinstance(row['steps'], list) else json.loads(row['steps']),
            enabled=row['enabled'],
            schedule=row['schedule'],
            alert_emails=row['alert_emails'] if isinstance(row['alert_emails'], list) else json.loads(row['alert_emails']),
            slack_webhook_url=row['slack_webhook_url'],
            alerts_enabled=row['alerts_enabled'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def _row_to_test_run(self, row: dict) -> TestRun:
        """Convert database row to TestRun object."""
        return TestRun(
            id=row['id'],
            monitor_id=row['monitor_id'],
            status=row['status'],
            started_at=row['started_at'],
            completed_at=row['completed_at'],
            duration_ms=row['duration_ms'],
            error_message=row['error_message'],
            screenshot_path=row['screenshot_path'],
            step_results=row['step_results'] if isinstance(row['step_results'], list) else json.loads(row['step_results']) if row.get('step_results') else []
        )
