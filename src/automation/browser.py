"""Browser automation wrapper using Playwright."""
from typing import Optional
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
import os


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
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        self.page = self.context.new_page()

    def stop(self):
        """Stop the browser and cleanup."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def get_page(self) -> Page:
        """Get the current page."""
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        return self.page

    def take_screenshot(self, path: str):
        """
        Take a screenshot of the current page.

        Args:
            path: Path to save the screenshot
        """
        if self.page:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.page.screenshot(path=path, full_page=True)

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
