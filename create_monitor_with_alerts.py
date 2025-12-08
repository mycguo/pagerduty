"""Example: Create a monitor with alert configuration."""
from src.monitoring.monitor import Monitor
from src.storage.storage import Storage

storage = Storage()

# Example monitor with both email and Slack alerts
monitor = Monitor(
    name="Production API Health Check",
    url="https://api.example.com",
    steps=[
        {
            "type": "navigate",
            "url": "https://api.example.com/health"
        },
        {
            "type": "verify",
            "condition": "element_exists",
            "selector": "body"
        },
        {
            "type": "verify",
            "condition": "text_contains",
            "selector": "body",
            "expected": "healthy"
        }
    ],
    # Alert configuration
    alert_emails=[
        "admin@example.com",
        "oncall@example.com"
    ],
    slack_webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    alerts_enabled=True,
    # Monitor settings
    enabled=True,
    schedule="*/5 * * * *"  # Every 5 minutes
)

storage.save_monitor(monitor)

print(f"✅ Monitor created: {monitor.name}")
print(f"   Monitor ID: {monitor.id}")
print(f"   Alerts enabled: {monitor.alerts_enabled}")
print(f"   Email recipients: {len(monitor.alert_emails)}")
print(f"   Slack configured: {'Yes' if monitor.slack_webhook_url else 'No'}")
print()
print("To test alerts:")
print("1. Update SMTP settings in .env (for email)")
print("2. Update Slack webhook URL in the monitor")
print("3. Modify the monitor to make it fail (e.g., wrong expected text)")
print("4. Run: python run_all_monitors.py")
print("5. Check your email and Slack for alerts!")
