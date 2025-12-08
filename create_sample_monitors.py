"""Create sample monitors for testing the application."""
from src.monitoring.monitor import Monitor
from src.storage.storage import Storage

storage = Storage()

# Sample Monitor 1: Basic Wikipedia Check
monitor1 = Monitor(
    name="Wikipedia Health Check",
    url="https://www.wikipedia.org",
    steps=[
        {
            "type": "navigate",
            "url": "https://www.wikipedia.org"
        },
        {
            "type": "verify",
            "condition": "element_exists",
            "selector": "#searchInput"
        },
        {
            "type": "fill",
            "selector": "#searchInput",
            "value": "Python programming"
        },
        {
            "type": "click",
            "selector": "button[type='submit']"
        },
        {
            "type": "wait",
            "wait_type": "time",
            "duration": 2000
        },
        {
            "type": "verify",
            "condition": "url_contains",
            "expected": "wikipedia.org"
        }
    ]
)

# Sample Monitor 2: GitHub Homepage Check
monitor2 = Monitor(
    name="GitHub Homepage Check",
    url="https://github.com",
    steps=[
        {
            "type": "navigate",
            "url": "https://github.com"
        },
        {
            "type": "verify",
            "condition": "element_visible",
            "selector": "a[href='/login']"
        }
    ]
)

# Sample Monitor 3: Example.com Simple Check
monitor3 = Monitor(
    name="Example.com Basic Test",
    url="https://example.com",
    steps=[
        {
            "type": "navigate",
            "url": "https://example.com"
        },
        {
            "type": "verify",
            "condition": "text_contains",
            "selector": "h1",
            "expected": "Example Domain"
        }
    ]
)

# Save monitors
for monitor in [monitor1, monitor2, monitor3]:
    storage.save_monitor(monitor)
    print(f"Created monitor: {monitor.name}")

print("\nAll sample monitors created successfully!")
print("Run 'streamlit run app.py' to view them in the dashboard.")
