"""Test alert notifications."""
import os
from datetime import datetime
from src.monitoring.monitor import Monitor, TestRun
from src.alerts.email_alert import EmailAlert
from src.alerts.slack_alert import SlackAlert

def test_email_configuration():
    """Test if email alerts are configured."""
    print("Testing Email Configuration...")
    email_alert = EmailAlert()

    if email_alert.is_configured():
        print("✅ Email alerts are configured!")
        print(f"   SMTP Host: {email_alert.smtp_host}")
        print(f"   SMTP Port: {email_alert.smtp_port}")
        print(f"   Username: {email_alert.smtp_username}")
        print(f"   From Email: {email_alert.from_email}")
    else:
        print("❌ Email alerts not configured.")
        print("   Set these environment variables:")
        print("   - SMTP_HOST")
        print("   - SMTP_USERNAME")
        print("   - SMTP_PASSWORD")
        print("   - SMTP_FROM_EMAIL")
    print()

def test_email_alert():
    """Test sending an email alert."""
    print("Testing Email Alert...")

    email_alert = EmailAlert()
    if not email_alert.is_configured():
        print("❌ Skipping: Email not configured\n")
        return

    # Get test email address
    test_email = input("Enter your email address to test (or press Enter to skip): ").strip()
    if not test_email:
        print("⏭️  Skipped\n")
        return

    # Create a fake test run
    test_run = {
        'monitor_id': 'test-123',
        'status': 'failed',
        'started_at': datetime.now().isoformat(),
        'completed_at': datetime.now().isoformat(),
        'duration_ms': 1500,
        'error_message': 'Test alert: This is a simulated failure for testing purposes.',
        'url': 'https://example.com',
        'alert_emails': [test_email]
    }

    success = email_alert.send_alert("Test Monitor", test_run)

    if success:
        print("✅ Email alert sent successfully!")
        print(f"   Check {test_email} for the alert email.")
    else:
        print("❌ Failed to send email alert.")
        print("   Check your SMTP credentials and network connection.")
    print()

def test_slack_webhook():
    """Test Slack webhook."""
    print("Testing Slack Webhook...")

    webhook_url = input("Enter your Slack webhook URL (or press Enter to skip): ").strip()
    if not webhook_url:
        print("⏭️  Skipped\n")
        return

    if not webhook_url.startswith('https://hooks.slack.com/'):
        print("❌ Invalid webhook URL. It should start with https://hooks.slack.com/\n")
        return

    slack_alert = SlackAlert()

    # Send test message
    print("Sending test message...")
    if slack_alert.send_test_message(webhook_url):
        print("✅ Test message sent to Slack successfully!")
        print("   Check your Slack channel.")
    else:
        print("❌ Failed to send test message.")
        print("   Check your webhook URL.")
    print()

    # Send failure alert
    send_failure = input("Send a test failure alert? (y/n): ").strip().lower()
    if send_failure == 'y':
        test_run = {
            'monitor_id': 'test-123',
            'status': 'failed',
            'started_at': datetime.now().isoformat(),
            'completed_at': datetime.now().isoformat(),
            'duration_ms': 1500,
            'error_message': 'Test alert: This is a simulated failure for testing purposes.',
            'url': 'https://example.com',
            'slack_webhook_url': webhook_url
        }

        if slack_alert.send_alert("Test Monitor", test_run):
            print("✅ Failure alert sent to Slack successfully!")
            print("   Check your Slack channel for the formatted alert.")
        else:
            print("❌ Failed to send failure alert.")
    print()

def main():
    print("=" * 60)
    print("Alert System Test")
    print("=" * 60)
    print()

    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found. Create one from .env.example:")
        print("   cp .env.example .env")
        print()

    # Test email configuration
    test_email_configuration()

    # Test email alert
    test_email_alert()

    # Test Slack webhook
    test_slack_webhook()

    print("=" * 60)
    print("Testing Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. If email failed, check SMTP credentials in .env")
    print("2. If Slack failed, verify your webhook URL")
    print("3. Configure monitors with alert settings in the UI")
    print("4. Run monitors to receive real failure alerts")
    print()

if __name__ == "__main__":
    main()
