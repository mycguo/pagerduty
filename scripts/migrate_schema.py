#!/usr/bin/env python3
"""Migrate database schema to fix TestRun fields."""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2


def migrate_schema():
    """Migrate test_runs table schema."""
    print("=" * 60)
    print("Database Schema Migration")
    print("=" * 60)

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)

    print(f"Database URL: {database_url[:30]}...")

    try:
        conn = psycopg2.connect(database_url)
        print("✓ Connected to database")

        with conn.cursor() as cur:
            # Check if test_runs table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'test_runs'
                )
            """)
            table_exists = cur.fetchone()[0]

            if not table_exists:
                print("✓ test_runs table doesn't exist yet - no migration needed")
                conn.close()
                return

            # Check if old columns exist
            cur.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'test_runs'
                AND column_name IN ('steps_completed', 'total_steps', 'step_results')
            """)
            existing_columns = [row[0] for row in cur.fetchall()]

            has_old_schema = 'steps_completed' in existing_columns or 'total_steps' in existing_columns
            has_new_schema = 'step_results' in existing_columns

            if has_new_schema and not has_old_schema:
                print("✓ Schema is already up to date")
                conn.close()
                return

            if has_old_schema:
                print("\nMigrating schema from old format to new format...")

                # Drop old columns if they exist
                if 'steps_completed' in existing_columns:
                    print("  - Dropping 'steps_completed' column")
                    cur.execute("ALTER TABLE test_runs DROP COLUMN IF EXISTS steps_completed")

                if 'total_steps' in existing_columns:
                    print("  - Dropping 'total_steps' column")
                    cur.execute("ALTER TABLE test_runs DROP COLUMN IF EXISTS total_steps")

            if not has_new_schema:
                # Add new column
                print("  - Adding 'step_results' column")
                cur.execute("""
                    ALTER TABLE test_runs
                    ADD COLUMN IF NOT EXISTS step_results JSONB DEFAULT '[]'::jsonb
                """)

            conn.commit()
            print("\n✓ Schema migration completed successfully")

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if conn:
            conn.close()

    print("=" * 60)
    print("Migration Complete")
    print("=" * 60)


if __name__ == "__main__":
    migrate_schema()
