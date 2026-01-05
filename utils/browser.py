"""Browser utilities for Playwright automation."""

import logging
import os
from playwright.sync_api import sync_playwright, Browser, Page

logger = logging.getLogger(__name__)


def is_ci_environment() -> bool:
    """Check if running in a CI environment (GitHub Actions, etc.)."""
    return os.environ.get("CI", "").lower() == "true" or os.environ.get("GITHUB_ACTIONS", "").lower() == "true"


class BrowserSession:
    """Context manager for Playwright browser sessions."""
    
    def __init__(self, headless: bool = False):
        # Force headless mode in CI environments
        if is_ci_environment() and not headless:
            logger.info("CI environment detected, forcing headless mode")
            headless = True
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
    
    def __enter__(self) -> "BrowserSession":
        logger.info("Launching browser")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ]
        )
        # Create a context with realistic browser settings to avoid bot detection
        context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True,
            locale="en-AU",
            timezone_id="Australia/Sydney",
        )
        self.page = context.new_page()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser closed")
    
    def goto(self, url: str, wait_time: int = 3000, retries: int = 3):
        """Navigate to a URL and wait for page to settle."""
        logger.info(f"Navigating to {url}")
        
        last_error = None
        for attempt in range(retries):
            try:
                self.page.goto(url, timeout=30000, wait_until="domcontentloaded")
                self.page.wait_for_timeout(wait_time)
                return
            except Exception as e:
                last_error = e
                if attempt < retries - 1:
                    logger.warning(f"Navigation failed (attempt {attempt + 1}/{retries}): {e}")
                    self.page.wait_for_timeout(2000)  # Wait before retry
        
        raise last_error
    
    def click(self, selector: str, wait_after: int = 500):
        """Click an element and wait."""
        logger.info(f"Clicking: {selector}")
        self.page.click(selector, timeout=5000)
        self.page.wait_for_timeout(wait_after)
    
    def fill(self, selector: str, value: str, wait_after: int = 500):
        """Fill an input field."""
        logger.info(f"Filling '{selector}' with: {value}")
        self.page.fill(selector, value, timeout=5000)
        self.page.wait_for_timeout(wait_after)
    
    def press_key(self, key: str, wait_after: int = 300):
        """Press a keyboard key."""
        self.page.keyboard.press(key)
        self.page.wait_for_timeout(wait_after)
    
    def get_html(self) -> str:
        """Get the current page HTML."""
        return self.page.content()
    
    def screenshot(self, path: str, full_page: bool = False):
        """Take a screenshot."""
        self.page.screenshot(path=path, full_page=full_page)
        logger.info(f"Screenshot saved to {path}")
    
    def wait_for_network_idle(self, timeout: int = 15000):
        """Wait for network to be idle."""
        self.page.wait_for_load_state("networkidle", timeout=timeout)
