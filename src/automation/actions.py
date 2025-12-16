"""Action handlers for browser automation."""
from typing import Dict, Any
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
import time
import os
import traceback


class ActionExecutor:
    """Executes actions on a browser page."""

    def __init__(self, page: Page):
        """
        Initialize the action executor.

        Args:
            page: Playwright page object
        """
        self.page = page

    def execute(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step.

        Args:
            step: Step configuration dictionary

        Returns:
            Result dictionary with status, duration, and optional error
        """
        start_time = time.time()
        step_type = step.get('type')

        print(f"[ActionExecutor] Executing step type: {step_type}")

        try:
            if step_type == 'navigate':
                self._navigate(step)
            elif step_type == 'click':
                self._click(step)
            elif step_type == 'fill':
                self._fill(step)
            elif step_type == 'select':
                self._select(step)
            elif step_type == 'wait':
                self._wait(step)
            elif step_type == 'verify':
                self._verify(step)
            elif step_type == 'screenshot':
                self._screenshot(step)
            elif step_type == 'execute_script':
                self._execute_script(step)
            else:
                raise ValueError(f"Unknown step type: {step_type}")

            duration_ms = int((time.time() - start_time) * 1000)
            print(f"[ActionExecutor] ✓ Step completed successfully in {duration_ms}ms")
            return {
                'status': 'success',
                'duration_ms': duration_ms,
                'error_message': None
            }

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)

            print(f"[ActionExecutor] ❌ Step failed after {duration_ms}ms")
            print(f"[ActionExecutor] Error type: {type(e).__name__}")
            print(f"[ActionExecutor] Error message: {error_msg}")

            # Log timeout errors with more detail
            if isinstance(e, PlaywrightTimeoutError):
                print(f"[ActionExecutor] This was a Playwright timeout error")
                print(f"[ActionExecutor] Current URL: {self.page.url}")

            print(f"[ActionExecutor] Full traceback:")
            traceback.print_exc()

            return {
                'status': 'failed',
                'duration_ms': duration_ms,
                'error_message': error_msg
            }

    def _navigate(self, step: Dict[str, Any]):
        """Navigate to a URL."""
        url = step.get('url')
        if not url:
            raise ValueError("Navigate step requires 'url' parameter")
        self.page.goto(url, wait_until='networkidle', timeout=30000)

    def _click(self, step: Dict[str, Any]):
        """Click an element."""
        selector = step.get('selector')
        if not selector:
            raise ValueError("Click step requires 'selector' parameter")

        # Wait for element to be visible and clickable
        self.page.wait_for_selector(selector, state='visible', timeout=10000)
        self.page.click(selector, timeout=10000)

    def _fill(self, step: Dict[str, Any]):
        """Fill a form field."""
        selector = step.get('selector')
        value = step.get('value', '')

        if not selector:
            raise ValueError("Fill step requires 'selector' parameter")

        # Support environment variable substitution
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            value = os.getenv(env_var, '')

        self.page.wait_for_selector(selector, state='visible', timeout=10000)
        self.page.fill(selector, str(value), timeout=10000)

    def _select(self, step: Dict[str, Any]):
        """Select an option from a dropdown."""
        selector = step.get('selector')
        value = step.get('value')

        if not selector or value is None:
            raise ValueError("Select step requires 'selector' and 'value' parameters")

        self.page.wait_for_selector(selector, state='visible', timeout=10000)
        self.page.select_option(selector, value, timeout=10000)

    def _wait(self, step: Dict[str, Any]):
        """Wait for a condition or time."""
        wait_type = step.get('wait_type', 'time')

        if wait_type == 'time':
            duration = step.get('duration', 1000)  # milliseconds
            time.sleep(duration / 1000)
        elif wait_type == 'selector':
            selector = step.get('selector')
            if not selector:
                raise ValueError("Wait for selector requires 'selector' parameter")
            state = step.get('state', 'visible')
            self.page.wait_for_selector(selector, state=state, timeout=30000)
        elif wait_type == 'url':
            url_pattern = step.get('url_pattern')
            if not url_pattern:
                raise ValueError("Wait for URL requires 'url_pattern' parameter")
            self.page.wait_for_url(url_pattern, timeout=30000)

    def _verify(self, step: Dict[str, Any]):
        """Verify a condition."""
        condition = step.get('condition')

        if condition == 'url_contains':
            expected = step.get('expected')
            current_url = self.page.url
            if expected not in current_url:
                raise AssertionError(f"Expected URL to contain '{expected}', but got '{current_url}'")

        elif condition == 'url_equals':
            expected = step.get('expected')
            current_url = self.page.url
            if expected != current_url:
                raise AssertionError(f"Expected URL to equal '{expected}', but got '{current_url}'")

        elif condition == 'element_exists':
            selector = step.get('selector')
            if not selector:
                raise ValueError("Verify element_exists requires 'selector' parameter")
            try:
                self.page.wait_for_selector(selector, state='attached', timeout=10000)
            except PlaywrightTimeoutError:
                raise AssertionError(f"Element '{selector}' does not exist")

        elif condition == 'element_visible':
            selector = step.get('selector')
            if not selector:
                raise ValueError("Verify element_visible requires 'selector' parameter")
            try:
                self.page.wait_for_selector(selector, state='visible', timeout=10000)
            except PlaywrightTimeoutError:
                raise AssertionError(f"Element '{selector}' is not visible")

        elif condition == 'text_contains':
            selector = step.get('selector')
            expected = step.get('expected')
            if not selector or not expected:
                raise ValueError("Verify text_contains requires 'selector' and 'expected' parameters")

            element = self.page.locator(selector)
            text = element.inner_text(timeout=10000)
            if expected not in text:
                raise AssertionError(f"Expected text to contain '{expected}', but got '{text}'")

        elif condition == 'text_equals':
            selector = step.get('selector')
            expected = step.get('expected')
            if not selector or expected is None:
                raise ValueError("Verify text_equals requires 'selector' and 'expected' parameters")

            element = self.page.locator(selector)
            text = element.inner_text(timeout=10000)
            if expected != text:
                raise AssertionError(f"Expected text to equal '{expected}', but got '{text}'")

        else:
            raise ValueError(f"Unknown verification condition: {condition}")

    def _screenshot(self, step: Dict[str, Any]):
        """Take a screenshot."""
        path = step.get('path', 'screenshots/screenshot.png')
        full_page = step.get('full_page', False)
        timeout = step.get('timeout', 10000)

        os.makedirs(os.path.dirname(path), exist_ok=True)

        try:
            # Wait for page to be stable before screenshot
            self.page.wait_for_load_state('domcontentloaded', timeout=5000)
            self.page.screenshot(path=path, full_page=full_page, timeout=timeout)
        except Exception as e:
            # If full_page screenshot fails, try viewport-only as fallback
            if full_page:
                print(f"[ActionExecutor] Full page screenshot failed, trying viewport-only: {str(e)}")
                self.page.screenshot(path=path, full_page=False, timeout=5000)
            else:
                raise

    def _execute_script(self, step: Dict[str, Any]):
        """Execute JavaScript on the page."""
        script = step.get('script')
        if not script:
            raise ValueError("Execute script step requires 'script' parameter")
        self.page.evaluate(script)
