"""Monitor runner for executing tests."""
from typing import List, Dict, Any
from datetime import datetime
import time
import os

from src.automation.browser import BrowserManager
from src.automation.actions import ActionExecutor
from src.monitoring.monitor import Monitor, TestRun
from src.alerts.email_alert import EmailAlert
from src.alerts.slack_alert import SlackAlert


class MonitorRunner:
    """Executes monitor tests."""

    def __init__(self, headless: bool = True, send_alerts: bool = True):
        """
        Initialize the monitor runner.

        Args:
            headless: Whether to run browser in headless mode
            send_alerts: Whether to send alerts on failures
        """
        self.headless = headless
        self.send_alerts = send_alerts
        self.email_alert = EmailAlert()
        self.slack_alert = SlackAlert()

    def run_monitor(self, monitor: Monitor) -> TestRun:
        """
        Run a single monitor and return the results.

        Args:
            monitor: Monitor configuration to execute

        Returns:
            TestRun object with results
        """
        started_at = datetime.now()
        test_run = TestRun(
            monitor_id=monitor.id,
            status='running',
            started_at=started_at
        )

        screenshot_path = None
        step_results: List[Dict[str, Any]] = []

        try:
            with BrowserManager(headless=self.headless) as browser:
                page = browser.get_page()
                executor = ActionExecutor(page)

                # Execute each step
                for idx, step in enumerate(monitor.steps):
                    step_result = executor.execute(step)
                    step_results.append({
                        'step_index': idx,
                        'step': step,
                        **step_result
                    })

                    # If step failed, stop execution
                    if step_result['status'] == 'failed':
                        test_run.status = 'failed'
                        test_run.error_message = f"Step {idx + 1} failed: {step_result['error_message']}"

                        # Take screenshot on failure
                        screenshot_path = f"screenshots/{monitor.id}_{test_run.id}.png"
                        browser.take_screenshot(screenshot_path)
                        break

                # If all steps passed
                if test_run.status == 'running':
                    test_run.status = 'success'

        except Exception as e:
            test_run.status = 'error'
            test_run.error_message = f"Test execution error: {str(e)}"

        # Calculate duration
        completed_at = datetime.now()
        test_run.completed_at = completed_at
        test_run.duration_ms = int((completed_at - started_at).total_seconds() * 1000)
        test_run.screenshot_path = screenshot_path
        test_run.step_results = step_results

        # Send alerts if enabled and test failed
        if self.send_alerts and monitor.alerts_enabled and test_run.status in ['failed', 'error']:
            self._send_alerts(monitor, test_run)

        return test_run

    def _send_alerts(self, monitor: Monitor, test_run: TestRun):
        """
        Send alerts for a failed test run.

        Args:
            monitor: Monitor configuration
            test_run: Test run result
        """
        test_run_dict = test_run.to_dict()
        test_run_dict['url'] = monitor.url
        test_run_dict['alert_emails'] = monitor.alert_emails
        test_run_dict['slack_webhook_url'] = monitor.slack_webhook_url

        # Send email alerts
        if monitor.alert_emails and self.email_alert.is_configured():
            self.email_alert.send_alert(monitor.name, test_run_dict)

        # Send Slack alerts
        # Always call send_alert; the handler will check for secrets if url is missing
        self.slack_alert.send_alert(monitor.name, test_run_dict)

    def run_monitors(self, monitors: List[Monitor]) -> List[TestRun]:
        """
        Run multiple monitors sequentially.

        Args:
            monitors: List of monitors to execute

        Returns:
            List of TestRun objects
        """
        results = []
        for monitor in monitors:
            if monitor.enabled:
                result = self.run_monitor(monitor)
                results.append(result)
        return results
