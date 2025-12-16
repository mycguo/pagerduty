"""Monitor runner for executing tests."""
from typing import List, Dict, Any
from datetime import datetime
import time
import os
import traceback

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
        print(f"\n[MonitorRunner] ========================================")
        print(f"[MonitorRunner] Starting monitor: {monitor.name} (ID: {monitor.id})")
        print(f"[MonitorRunner] URL: {monitor.url}")
        print(f"[MonitorRunner] Steps count: {len(monitor.steps)}")
        print(f"[MonitorRunner] ========================================\n")

        started_at = datetime.now()
        test_run = TestRun(
            monitor_id=monitor.id,
            status='running',
            started_at=started_at
        )

        screenshot_path = None
        step_results: List[Dict[str, Any]] = []

        try:
            print(f"[MonitorRunner] Initializing browser (headless={self.headless})...")
            with BrowserManager(headless=self.headless) as browser:
                page = browser.get_page()
                executor = ActionExecutor(page)
                print(f"[MonitorRunner] Browser initialized successfully")

                # Execute each step
                for idx, step in enumerate(monitor.steps):
                    print(f"\n[MonitorRunner] -------- Step {idx + 1}/{len(monitor.steps)} --------")
                    print(f"[MonitorRunner] Step type: {step.get('type')}")
                    print(f"[MonitorRunner] Step details: {step}")

                    step_result = executor.execute(step)
                    step_results.append({
                        'step_index': idx,
                        'step': step,
                        **step_result
                    })

                    print(f"[MonitorRunner] Step result: {step_result['status']} ({step_result['duration_ms']}ms)")

                    # If step failed, stop execution
                    if step_result['status'] == 'failed':
                        test_run.status = 'failed'
                        test_run.error_message = f"Step {idx + 1} failed: {step_result['error_message']}"

                        print(f"[MonitorRunner] ❌ Step {idx + 1} FAILED: {step_result['error_message']}")

                        # Take screenshot on failure (don't let screenshot errors override test error)
                        try:
                            screenshot_path = f"screenshots/{monitor.id}_{test_run.id}.png"
                            print(f"[MonitorRunner] Attempting to capture failure screenshot: {screenshot_path}")
                            browser.take_screenshot(screenshot_path)
                            print(f"[MonitorRunner] ✓ Screenshot captured successfully")
                        except Exception as screenshot_error:
                            print(f"[MonitorRunner] ⚠️  Failed to capture screenshot: {str(screenshot_error)}")
                            print(f"[MonitorRunner] Screenshot error traceback:")
                            traceback.print_exc()
                            screenshot_path = None
                        break
                    else:
                        print(f"[MonitorRunner] ✓ Step {idx + 1} succeeded")

                # If all steps passed
                if test_run.status == 'running':
                    test_run.status = 'success'
                    print(f"\n[MonitorRunner] ✓ All steps completed successfully")

        except Exception as e:
            test_run.status = 'error'
            test_run.error_message = f"Test execution error: {str(e)}"

            print(f"\n[MonitorRunner] ❌ CRITICAL ERROR during test execution:")
            print(f"[MonitorRunner] Error type: {type(e).__name__}")
            print(f"[MonitorRunner] Error message: {str(e)}")
            print(f"[MonitorRunner] Full traceback:")
            traceback.print_exc()

        # Calculate duration
        completed_at = datetime.now()
        test_run.completed_at = completed_at
        test_run.duration_ms = int((completed_at - started_at).total_seconds() * 1000)
        test_run.screenshot_path = screenshot_path
        test_run.step_results = step_results

        print(f"\n[MonitorRunner] ========================================")
        print(f"[MonitorRunner] Test run completed")
        print(f"[MonitorRunner] Status: {test_run.status}")
        print(f"[MonitorRunner] Duration: {test_run.duration_ms}ms")
        print(f"[MonitorRunner] Steps executed: {len(step_results)}/{len(monitor.steps)}")
        if test_run.error_message:
            print(f"[MonitorRunner] Error: {test_run.error_message}")
        if screenshot_path:
            print(f"[MonitorRunner] Screenshot: {screenshot_path}")
        print(f"[MonitorRunner] ========================================\n")

        # Send alerts if enabled and test failed
        if self.send_alerts and monitor.alerts_enabled and test_run.status in ['failed', 'error']:
            print(f"[MonitorRunner] Sending alerts (alerts_enabled={monitor.alerts_enabled}, status={test_run.status})")
            self._send_alerts(monitor, test_run)
        elif not self.send_alerts:
            print(f"[MonitorRunner] Alerts disabled via send_alerts flag")
        elif not monitor.alerts_enabled:
            print(f"[MonitorRunner] Alerts disabled for this monitor")

        return test_run

    def _send_alerts(self, monitor: Monitor, test_run: TestRun):
        """
        Send alerts for a failed test run.

        Args:
            monitor: Monitor configuration
            test_run: Test run result
        """
        print(f"[MonitorRunner] Preparing to send alerts...")

        test_run_dict = test_run.to_dict()
        test_run_dict['url'] = monitor.url
        test_run_dict['alert_emails'] = monitor.alert_emails

        # Send email alerts
        if monitor.alert_emails and self.email_alert.is_configured():
            print(f"[MonitorRunner] Sending email alerts to: {monitor.alert_emails}")
            try:
                self.email_alert.send_alert(monitor.name, test_run_dict)
                print(f"[MonitorRunner] ✓ Email alerts sent successfully")
            except Exception as e:
                print(f"[MonitorRunner] ❌ Failed to send email alerts: {str(e)}")
                traceback.print_exc()
        elif not monitor.alert_emails:
            print(f"[MonitorRunner] No email recipients configured")
        elif not self.email_alert.is_configured():
            print(f"[MonitorRunner] Email alerts not configured (missing SMTP settings)")

        # Send Slack alerts (webhook configured via SLACK_WEBHOOK_URL environment variable)
        if self.slack_alert.is_configured():
            print(f"[MonitorRunner] Sending Slack alert...")
            try:
                self.slack_alert.send_alert(monitor.name, test_run_dict)
                print(f"[MonitorRunner] ✓ Slack alert sent successfully")
            except Exception as e:
                print(f"[MonitorRunner] ❌ Failed to send Slack alert: {str(e)}")
                traceback.print_exc()
        else:
            print(f"[MonitorRunner] Slack alerts not configured (missing SLACK_WEBHOOK_URL)")

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
