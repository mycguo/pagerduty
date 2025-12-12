"""Recorder module for generating test steps."""
from playwright.sync_api import sync_playwright, Page
import json
import time
from typing import List, Dict, Any

class MonitorRecorder:
    def __init__(self):
        self.steps: List[Dict[str, Any]] = []
        self._is_recording = False

    def start(self, url: str):
        """Start the recording session."""
        print(f"Starting recorder at {url}...")
        print("Interact with the browser window to record steps.")
        print("Close the browser window to finish recording.")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            # Expose the recording function to the browser
            page.expose_function("record_action", self._record_action)

            # Inject the recording script
            self._inject_recorder(page)

            # Navigate to the initial URL
            self.steps.append({
                "type": "navigate",
                "url": url
            })
            page.goto(url)

            # Keep the script running until the browser is closed
            try:
                # We interpret "browser closed" as the page processing being done
                # A simple way to keep it open is checking if page is not closed
                while not page.is_closed():
                    page.wait_for_timeout(100)
            except Exception:
                pass  # Browser closed

            browser.close()
            
        return self.steps

    def _record_action(self, action_type: str, details: Dict[str, Any]):
        """Callback for recorded actions from the browser."""
        if action_type == 'click':
            step = {
                "type": "click",
                "selector": details['selector']
            }
            # Avoid duplicate clicks if they happen too fast, or just log it
            self.steps.append(step)
            print(f"Recorded click: {details['selector']}")

        elif action_type == 'input':
            step = {
                "type": "fill",
                "selector": details['selector'],
                "value": details['value']
            }
            # Strategy: update the last step if it was a fill for the same selector
            # to avoid creating a step for every keystroke if 'input' fires often
            # Ideally we listen to 'change' or use a debounce in JS. 
            # Here we'll handle 'change' events mostly, or 'focusout'.
            # Let's say we rely on the JS sending 'change' events.
            self.steps.append(step)
            print(f"Recorded fill: {details['selector']} = {details['value']}")

    def _inject_recorder(self, page: Page):
        """Inject JavaScript to capture user interactions."""
        # Simple selector generator logic + event listeners
        js_script = """
            function getSelector(el) {
                if (el.id) return '#' + el.id;
                if (el.getAttribute('data-testid')) return `[data-testid="${el.getAttribute('data-testid')}"]`;
                if (el.getAttribute('name')) return `[name="${el.getAttribute('name')}"]`;
                if (el.getAttribute('placeholder')) return `[placeholder="${el.getAttribute('placeholder')}"]`;
                if (el.getAttribute('aria-label')) return `[aria-label="${el.getAttribute('aria-label')}"]`;
                
                // For buttons, try to find a submit type
                if (el.tagName.toLowerCase() === 'button' && el.type) {
                    return `button[type="${el.type}"]`;
                }

                if (el.className && typeof el.className === 'string') {
                    const classes = el.className.split(' ').filter(c => c).map(c => CSS.escape(c)).join('.');
                    if (classes) return '.' + classes;
                }
                
                // Fallback to tag name
                return el.tagName.toLowerCase();
            }

            document.addEventListener('click', (e) => {
                // We might click an inner element (like a span in a button). 
                // We should find the closest interactive element.
                const interactive = e.target.closest('button, a, input, select, [role="button"]');
                const target = interactive || e.target;
                
                const selector = getSelector(target);
                window.record_action('click', { selector: selector });
            }, true);

            document.addEventListener('change', (e) => {
                const selector = getSelector(e.target);
                window.record_action('input', { 
                    selector: selector,
                    value: e.target.value 
                });
            }, true);
        """
        page.add_init_script(js_script)
