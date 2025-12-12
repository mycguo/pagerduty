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
        new_step = None

        if action_type == 'click':
            new_step = {
                "type": "click",
                "selector": details['selector']
            }
            print(f"Recorded click: {details['selector']}")

        elif action_type == 'input':
            new_step = {
                "type": "fill",
                "selector": details['selector'],
                "value": details['value']
            }
            print(f"Recorded fill: {details['selector']} = {details['value']}")

        # Deduplication logic
        if new_step:
            if self.steps:
                last_step = self.steps[-1]
                # If same type and selector
                if last_step.get('type') == new_step['type'] and \
                   last_step.get('selector') == new_step['selector']:
                    
                    # For input, we just update the value of the last step (capture final text)
                    if new_step['type'] == 'fill':
                        last_step['value'] = new_step['value']
                        print(f"Updated previous fill step value to: {new_step['value']}")
                        return
                    
                    # For click, strict duplication check (ignore rapid double clicks usually)
                    # But checking timestamps might be better. For now, strict identity is safer to avoid spam.
                    print("Duplicate step detected, ignoring.")
                    return

            self.steps.append(new_step)

    def _inject_recorder(self, page: Page):
        """Inject JavaScript to capture user interactions."""
        # Improved selector generator logic + event listeners
        js_script = """
            function getSelector(el) {
                // 1. ID
                if (el.id) return '#' + CSS.escape(el.id);
                
                // 2. Test Attributes
                if (el.getAttribute('data-testid')) return `[data-testid="${el.getAttribute('data-testid')}"]`;
                if (el.getAttribute('data-test')) return `[data-test="${el.getAttribute('data-test')}"]`;

                // 3. Text Content (for buttons, links, labels) - Powerful & Human Readable
                const tag = el.tagName.toLowerCase();
                if (['button', 'a', 'label', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div'].includes(tag)) {
                    // Get direct text content, trimmed
                    const text = el.innerText ? el.innerText.trim() : '';
                    if (text && text.length < 50 && text.length > 0) {
                        // Check if text is unique-ish (heuristc) or just use it.
                        // Playwright 'text=' engine is robust.
                        // We need to escape quotes in text.
                        const safeText = text.replace(/"/g, '\\\\"');
                        
                        // For links and buttons, just text is usually great
                        if (['button', 'a'].includes(tag)) {
                            return `text="${safeText}"`;
                        }
                        
                        // For others, maybe ensure tag specificity
                        // return `${tag}:has-text("${safeText}")`; // Standard CSS way-ish in Playwright
                        return `text="${safeText}"`;
                    }
                }
                
                // 4. Form Attributes
                if (el.getAttribute('name')) return `[name="${el.getAttribute('name')}"]`;
                if (el.getAttribute('placeholder')) return `[placeholder="${el.getAttribute('placeholder')}"]`;
                if (el.getAttribute('aria-label')) return `[aria-label="${el.getAttribute('aria-label')}"]`;
                
                // 5. Button type
                if (tag === 'button' && el.type) {
                    return `button[type="${el.type}"]`;
                }

                // 6. Classes (Fallback, improved escaping)
                if (el.className && typeof el.className === 'string') {
                    const classes = el.className.split(' ')
                        .filter(c => c)
                        .map(c => CSS.escape(c))
                        .join('.');
                    if (classes) return '.' + classes;
                }
                
                // 7. Fallback to tag name
                return tag;
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
