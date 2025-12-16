# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **web application monitoring system** built with Streamlit that uses Playwright for browser automation. It allows users to create monitors that run automated test flows against web applications to verify functionality (e.g., login flows, form submissions, page navigation). The system supports scheduled execution, alerting, and result tracking.

## Key Commands

### Local Development

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the Streamlit app
streamlit run app.py

# Install/reinstall Playwright browsers
playwright install chromium

# Run all monitors manually
python run_all_monitors.py

# Create sample monitors
python create_sample_monitors.py
```

### Testing Individual Monitors

```python
# From Python REPL or script
from src.storage.storage import Storage
from src.monitoring.runner import MonitorRunner

storage = Storage()
monitor = storage.get_monitors()[0]  # Get first monitor

runner = MonitorRunner(headless=False)  # headless=False to see browser
result = runner.run_monitor(monitor)
print(f"Status: {result.status}")
```

### Deployment (Render)

The application is configured for deployment on Render.com. The deployment process:

1. Push to main branch triggers automatic deployment
2. `scripts/init_data.sh` runs to check for persistent storage
3. If `DATABASE_URL` exists, `scripts/migrate_to_postgres.py` migrates default monitors to Postgres
4. App starts and auto-detects storage backend (Postgres vs file-based)

## Architecture

### Storage Backend Strategy

The application uses a **dual storage backend** pattern:

- **PostgreSQL** (`src/storage/postgres_storage.py`): Used when `DATABASE_URL` environment variable is present (Render deployment)
- **File-based** (`src/storage/storage.py`): Used for local development, stores data in `data/monitors.json` and `data/test_results.json`

Both backends implement the same interface, so the application code is storage-agnostic. The selection happens in `app.py` at startup based on the presence of `DATABASE_URL`.

**Important**: Render's free tier does NOT support persistent disks, so we use their free PostgreSQL database (90-day expiration) instead. The persistent disk configuration in `render.yaml` is commented out.

### Monitor Execution Flow

1. **Monitor Definition** (`src/monitoring/monitor.py`): Defines `Monitor` (configuration) and `TestRun` (execution result) models
2. **Action Execution** (`src/automation/actions.py`): `ActionExecutor` interprets step definitions and executes them via Playwright
3. **Browser Management** (`src/automation/browser.py`): `BrowserManager` handles Playwright lifecycle
4. **Runner** (`src/monitoring/runner.py`): `MonitorRunner` orchestrates execution, screenshots on failure, and alert triggering
5. **Scheduler** (`src/monitoring/scheduler.py`): `MonitorScheduler` uses APScheduler to run monitors on cron schedules

### Step Type System

Monitors are defined as JSON arrays of steps. Each step has a `type` field:

- `navigate`: Navigate to a URL
- `click`: Click an element (CSS selector or text selector like `text="Button"`)
- `fill`: Fill a form field
- `select`: Select dropdown option
- `wait`: Wait for time or element state
- `verify`: Assert conditions (url_contains, element_exists, text_contains, etc.)
- `screenshot`: Capture screenshot
- `execute_script`: Run arbitrary JavaScript

Steps are executed sequentially by `ActionExecutor.execute()`. If any step fails, execution stops and a screenshot is captured.

### Alert System

Alerts (`src/alerts/`) use a base class pattern:

- `base.py`: `AlertBase` abstract class
- `email_alert.py`: SMTP email alerts (requires environment variables: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`)
- `slack_alert.py`: Slack webhook alerts

Alerts are triggered by `MonitorRunner._send_alerts()` only when:
1. `monitor.alerts_enabled = True`
2. Test status is `'failed'` or `'error'`
3. `MonitorRunner.send_alerts = True` (constructor parameter)

### Streamlit UI Structure

The UI (`src/ui/`) is split across three pages:

- `dashboard.py`: Overview charts, monitor status summary, recent runs
- `monitors.py`: Monitor CRUD interface with JSON step editor, includes alert configuration UI
- `results.py`: Test run history with filtering and screenshots

Streamlit caching:
- `@st.cache_resource` is used for storage and scheduler instances (singleton pattern)
- Scheduler jobs are synced on every app rerun via `scheduler.sync_jobs()`

### Environment Variable Substitution

Monitors support environment variable substitution in step values using `${VARIABLE_NAME}` syntax. This is handled by `ActionExecutor` when executing steps, allowing secure storage of passwords/API keys in `.env` files.

## Critical Implementation Details

### Slack Webhook Configuration

Slack webhooks are **always loaded from environment variables** (`SLACK_WEBHOOK_URL`) and are **never stored in monitor configurations**. The `monitor.slack_webhook_url` field is always `None`.

This design:
- Prevents webhook URLs from being committed to version control
- Avoids storing sensitive URLs in the database
- Simplifies configuration (one webhook for all monitors)
- Enhances security

See `src/alerts/slack_alert.py` for webhook loading logic and `src/ui/monitors.py` for the UI that displays webhook configuration status.

### Postgres Migration on First Deployment

The migration script (`scripts/migrate_to_postgres.py`) checks if monitors already exist in the database before migrating from `default_monitors.json`. This prevents duplicate monitors on redeployments.

The script is executed conditionally in the Dockerfile CMD based on whether `DATABASE_URL` is set.

### Scheduler Job Synchronization

The scheduler must synchronize jobs with monitor configuration on every Streamlit rerun. This is handled by:

1. `scheduler.sync_jobs()` called in `app.py` after initializing the scheduler
2. The method compares current jobs with monitors from storage
3. Adds/removes/updates jobs based on monitor enabled state and schedule changes

Jobs are keyed by monitor ID to track which jobs correspond to which monitors.

### Screenshot Storage

Screenshots are saved to `screenshots/{monitor_id}_{test_run_id}.png`. The directory is created automatically by `BrowserManager.take_screenshot()`. Screenshots are referenced in `TestRun.screenshot_path` and displayed in the UI.

**Note**: Screenshots are excluded from Docker images via `.dockerignore` to keep image size down.

## Common Development Patterns

### Adding a New Step Type

1. Add step execution logic to `ActionExecutor.execute()` in `src/automation/actions.py`
2. Update the step type examples in `src/ui/monitors.py` (the example configuration expander)
3. Document the new step type in `readme.md`

### Adding a New Alert Channel

1. Create a new alert class in `src/alerts/` inheriting from `AlertBase`
2. Implement `send()` and `is_configured()` methods
3. Initialize the alert instance in `MonitorRunner.__init__()`
4. Add alert sending logic to `MonitorRunner._send_alerts()`
5. Add UI configuration in `src/ui/monitors.py` alert expander

### Storage Backend Modifications

When modifying storage backends, ensure BOTH `Storage` and `PostgresStorage` implement the same interface:

- `save_monitor(monitor: Monitor)`
- `get_monitors() -> List[Monitor]`
- `get_monitor(monitor_id: str) -> Optional[Monitor]`
- `delete_monitor(monitor_id: str)`
- `save_test_run(test_run: TestRun)`
- `get_test_runs(monitor_id: Optional[str], limit: int) -> List[TestRun]`
- `get_latest_test_run(monitor_id: str) -> Optional[TestRun]`

## Environment Configuration

### Local Development (.env)

```bash
# Test credentials (for monitor step substitution)
TEST_USERNAME=user@example.com
TEST_PASSWORD=secure_password

# Email alerts (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your.email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your.email@gmail.com

# Slack alerts (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Render Deployment

Required environment variables in Render Dashboard:
- `DATABASE_URL`: Auto-injected by Render when database is provisioned (see `render.yaml`)
- `SLACK_WEBHOOK_URL`: Must be added manually in Render Dashboard
- SMTP variables: Must be added manually if email alerts are needed

Optional:
- `DATA_DIR`: Defaults to `/app/data` in Docker, `./data` locally
- `RENDER`: Set to `"true"` in `render.yaml` to help detect Render environment

## File Organization Notes

- `default_monitors.json`: Default monitors copied to persistent storage on first deployment
- `data/`: Local file storage (gitignored, not persisted on Render free tier)
- `screenshots/`: Screenshot storage (gitignored, excluded from Docker images)
- `scripts/`: Deployment and migration scripts
  - `init_data.sh`: Checks for persistent disk mounting and initializes data directory
  - `migrate_to_postgres.py`: One-time migration of default monitors to Postgres

## Important: Database Expiration (90 Days)

**Critical limitation**: Render's free PostgreSQL database expires after 90 days and is permanently deleted.

### What Happens
- Database is deleted with all monitor data
- App falls back to file storage (not persistent on Render free tier)
- You lose all custom monitors and test history

### Solutions
1. **Renew free database** every 90 days (manual process)
2. **Upgrade to paid database** ($7/month) - no expiration
3. **Use external free database** (Supabase, Neon - no expiration)

### Backup/Restore
```bash
# Backup monitors before expiration
python scripts/backup_monitors.py

# Restore after creating new database
python scripts/backup_monitors.py --restore backups/monitors_backup_latest.json
```

**See `DATABASE_EXPIRATION.md` for complete details and recovery procedures.**

## Debugging Tips

### Detailed Console Logging

The app includes **comprehensive detailed logging** throughout the entire monitor execution pipeline. All logs use print statements (not Python's logging module) to ensure they appear immediately in Render's console logs.

**See `DETAILED_LOGGING.md` for complete documentation.**

Log prefixes to search for in Render console:
- `[MonitorRunner]` - Monitor execution, step-by-step progress, errors
- `[ActionExecutor]` - Individual step execution with timing and errors
- `[BrowserManager]` - Browser lifecycle and screenshot operations
- `[MonitorScheduler]` - Scheduled job triggers and sync operations
- `[Storage]` - File-based storage operations
- `[PostgresStorage]` - Database storage operations

Key features:
- Full stack traces for all errors
- Step-by-step execution logs with timing
- Screenshot operation details (timeout, fallback attempts)
- Clear status indicators (✓ success, ❌ failure, ⚠️  warning)
- Playwright timeout detection with current URL

Example searches in Render logs:
- `❌` - Find all errors
- `[MonitorRunner] Starting monitor: YourMonitorName` - Track specific monitor
- `TimeoutError` - Find timeout issues
- `[BrowserManager] Taking screenshot` - Debug screenshot problems

### Test Monitors Locally with Browser Visible

```python
from src.monitoring.runner import MonitorRunner
runner = MonitorRunner(headless=False)  # See browser window
result = runner.run_monitor(monitor)
```

### Verify Storage Backend Selection

Check app startup logs for:
```
[Storage] Using PostgreSQL for data persistence
```
or
```
[Storage] Using file-based storage (data will not persist on Render free tier)
```
