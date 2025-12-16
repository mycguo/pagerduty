"""Browser automation wrapper using Playwright."""
from typing import Optional
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
import os
import traceback


class BrowserManager:
    """Manages browser lifecycle for automated testing."""

    def __init__(self, headless: bool = True):
        """
        Initialize the browser manager.

        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def start(self):
        """Start the browser."""
        print(f"[BrowserManager] Starting Playwright...")
        try:
            self.playwright = sync_playwright().start()
            print(f"[BrowserManager] Launching Chromium (headless={self.headless})...")
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            print(f"[BrowserManager] Creating browser context...")
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            print(f"[BrowserManager] Creating new page...")
            self.page = self.context.new_page()
            print(f"[BrowserManager] ✓ Browser started successfully")
        except Exception as e:
            print(f"[BrowserManager] ❌ Failed to start browser: {str(e)}")
            traceback.print_exc()
            raise

    def stop(self):
        """Stop the browser and cleanup."""
        print(f"[BrowserManager] Stopping browser...")
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            print(f"[BrowserManager] ✓ Browser stopped successfully")
        except Exception as e:
            print(f"[BrowserManager] ⚠️  Error during browser cleanup: {str(e)}")
            traceback.print_exc()

    def get_page(self) -> Page:
        """Get the current page."""
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        return self.page

    def take_screenshot(self, path: str, timeout: int = 10000, full_page: bool = False):
        """
        Take a screenshot of the current page.

        Args:
            path: Path to save the screenshot
            timeout: Screenshot timeout in milliseconds (default: 10000)
            full_page: Whether to capture full scrollable page (default: False)
        """
        if self.page:
            print(f"[BrowserManager] Taking screenshot: {path}")
            print(f"[BrowserManager] Screenshot params: full_page={full_page}, timeout={timeout}ms")
            print(f"[BrowserManager] Current URL: {self.page.url}")

            # Create directory
            os.makedirs(os.path.dirname(path), exist_ok=True)

            try:
                # Wait for page to be in a stable state before screenshot
                print(f"[BrowserManager] Waiting for page to be stable (domcontentloaded)...")
                self.page.wait_for_load_state('domcontentloaded', timeout=5000)
                print(f"[BrowserManager] Page stable, capturing screenshot...")

                self.page.screenshot(path=path, full_page=full_page, timeout=timeout)
                print(f"[BrowserManager] ✓ Screenshot saved successfully to {path}")

            except Exception as e:
                # If screenshot fails, try viewport-only as fallback
                print(f"[BrowserManager] ❌ Screenshot failed: {type(e).__name__}: {str(e)}")

                if full_page:
                    print(f"[BrowserManager] Attempting fallback: viewport-only screenshot...")
                    try:
                        self.page.screenshot(path=path, full_page=False, timeout=5000)
                        print(f"[BrowserManager] ✓ Fallback screenshot saved successfully")
                    except Exception as fallback_error:
                        print(f"[BrowserManager] ❌ Fallback screenshot also failed: {str(fallback_error)}")
                        print(f"[BrowserManager] Full traceback:")
                        traceback.print_exc()
                        raise
                else:
                    print(f"[BrowserManager] Full traceback:")
                    traceback.print_exc()
                    raise

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
