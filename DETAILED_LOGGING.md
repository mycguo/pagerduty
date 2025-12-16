# Detailed Logging for Render.com Console

## Overview

The application now includes comprehensive logging to help debug issues on Render.com's console logs. All logging uses print statements (rather than Python's logging module) to ensure immediate visibility in Render's console.

## What's Logged

### 1. MonitorRunner (`src/monitoring/runner.py`)
- **Monitor Start**: Monitor name, ID, URL, and step count
- **Step Execution**: Each step's type, details, result, and duration
- **Step Success/Failure**: Clear ✓ or ❌ indicators with timing
- **Screenshot Attempts**: When screenshots are taken, including success/failure with fallback attempts
- **Test Completion**: Final status, duration, steps executed
- **Alert Sending**: Whether alerts are sent and to which channels (Email/Slack)
- **Full Tracebacks**: Complete stack traces for all errors

### 2. ActionExecutor (`src/automation/actions.py`)
- **Step Type**: What action is being executed
- **Success/Failure**: Result and duration for each step
- **Playwright Timeouts**: Special handling for timeout errors with current URL
- **Full Tracebacks**: Complete stack traces for step failures

### 3. BrowserManager (`src/automation/browser.py`)
- **Browser Lifecycle**: Starting/stopping Playwright and Chromium
- **Browser Initialization**: Each stage of browser setup
- **Screenshot Operations**:
  - Screenshot parameters (full_page, timeout)
  - Current URL being captured
  - Page stability checks
  - Success/failure with detailed error messages
  - Fallback attempts (full-page → viewport-only)
- **Full Tracebacks**: Complete stack traces for browser errors

### 4. MonitorScheduler (`src/monitoring/scheduler.py`)
- **Scheduler Initialization**: When the scheduler starts
- **Job Scheduling**: Which monitors are scheduled with their cron expressions
- **Job Execution**: When scheduled jobs are triggered
- **Job Sync**: How many monitors found and how many jobs are active
- **Job Cleanup**: When stale jobs are removed

## Log Prefixes

All logs use consistent prefixes to make them easy to grep:
- `[MonitorRunner]` - Monitor execution logs
- `[ActionExecutor]` - Step execution logs
- `[BrowserManager]` - Browser management logs
- `[MonitorScheduler]` - Scheduler logs
- `[Storage]` - File storage logs (existing)
- `[PostgresStorage]` - Database storage logs (existing)

## Status Indicators

- ✓ - Success
- ❌ - Error/Failure
- ⚠️  - Warning

## Example Log Output

### Successful Monitor Run
```
[MonitorRunner] ========================================
[MonitorRunner] Starting monitor: Wikipedia Health Check (ID: 1b90b4a8...)
[MonitorRunner] URL: https://www.wikipedia.org
[MonitorRunner] Steps count: 6
[MonitorRunner] ========================================

[MonitorRunner] Initializing browser (headless=True)...
[BrowserManager] Starting Playwright...
[BrowserManager] Launching Chromium (headless=True)...
[BrowserManager] ✓ Browser started successfully

[MonitorRunner] -------- Step 1/6 --------
[MonitorRunner] Step type: navigate
[ActionExecutor] Executing step type: navigate
[ActionExecutor] ✓ Step completed successfully in 761ms
[MonitorRunner] ✓ Step 1 succeeded

[MonitorRunner] ✓ All steps completed successfully
[MonitorRunner] Status: success
[MonitorRunner] Duration: 4017ms
```

### Failed Monitor Run with Screenshot Timeout
```
[MonitorRunner] -------- Step 3/5 --------
[MonitorRunner] Step type: click
[ActionExecutor] Executing step type: click
[ActionExecutor] ❌ Step failed after 30123ms
[ActionExecutor] Error type: TimeoutError
[ActionExecutor] Error message: Timeout 30000ms exceeded
[ActionExecutor] This was a Playwright timeout error
[ActionExecutor] Current URL: https://example.com/page
[ActionExecutor] Full traceback:
Traceback (most recent call last):
  ...

[MonitorRunner] ❌ Step 3 FAILED: Timeout 30000ms exceeded
[MonitorRunner] Attempting to capture failure screenshot: screenshots/abc123_xyz789.png
[BrowserManager] Taking screenshot: screenshots/abc123_xyz789.png
[BrowserManager] Screenshot params: full_page=False, timeout=10000ms
[BrowserManager] Current URL: https://example.com/page
[BrowserManager] Waiting for page to be stable (domcontentloaded)...
[BrowserManager] Page stable, capturing screenshot...
[BrowserManager] ✓ Screenshot saved successfully
```

## Screenshot Improvements

In addition to logging, screenshots now have:

1. **Reduced Default Timeout**: 10 seconds instead of 30
2. **Viewport-Only by Default**: Faster, more reliable than full-page
3. **Fallback Mechanism**: If full-page fails, automatically retries with viewport-only
4. **Page Stability Check**: Waits for DOM to be ready before capturing
5. **Error Isolation**: Screenshot failures don't override the original test error

## Debugging on Render

When viewing Render console logs, search for:
- Monitor failures: `❌`
- Specific monitor: `[MonitorRunner] Starting monitor: YourMonitorName`
- Screenshot issues: `[BrowserManager] Taking screenshot`
- Timeout errors: `TimeoutError` or `Timeout.*exceeded`
- Scheduled runs: `[MonitorScheduler] Scheduled job triggered`

## Testing Locally

Run `python test_logging.py` to see the detailed logging output locally before deploying to Render.

## Files Modified

- `src/monitoring/runner.py` - Added detailed monitor execution logging
- `src/automation/actions.py` - Added step execution logging with tracebacks
- `src/automation/browser.py` - Added browser lifecycle and screenshot logging
- `src/monitoring/scheduler.py` - Added scheduler job logging
- All files now import `traceback` for full stack traces
