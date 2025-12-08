# Alert Setup Guide

This guide will help you configure email and Slack notifications for your monitoring system.

## Overview

The monitoring system can send alerts when tests fail via:
- 📧 **Email** (using SMTP)
- 💬 **Slack** (using webhooks)

Alerts are sent only when tests fail or error out, not for successful tests.

## Email Alerts Setup

### Step 1: Configure SMTP Settings

Email alerts require an SMTP server. Here are instructions for popular providers:

#### Gmail (Recommended for Testing)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to https://myaccount.google.com/security
   - Click on "2-Step Verification"
   - Scroll down to "App passwords"
   - Select "Mail" and your device
   - Copy the 16-character password

3. **Update your `.env` file**:
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your.email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
SMTP_FROM_EMAIL=your.email@gmail.com
```

#### SendGrid

1. Sign up at https://sendgrid.com/
2. Create an API key
3. Update your `.env` file:
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your_sendgrid_api_key
SMTP_FROM_EMAIL=your_verified_sender@yourdomain.com
```

#### Mailgun

1. Sign up at https://www.mailgun.com/
2. Get your SMTP credentials from the dashboard
3. Update your `.env` file:
```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
SMTP_FROM_EMAIL=sender@yourdomain.com
```

#### AWS SES

1. Set up AWS SES in your AWS account
2. Verify your sender email/domain
3. Update your `.env` file:
```bash
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your_ses_username
SMTP_PASSWORD=your_ses_password
SMTP_FROM_EMAIL=verified@yourdomain.com
```

### Step 2: Add Email Recipients to Monitors

1. Go to the "Monitors" page in the app
2. Click "Add/Edit Monitor" tab
3. Expand "🔔 Alert Configuration"
4. Enable alerts
5. Add email addresses (one per line) in the "Email addresses" field
6. Save the monitor

### Step 3: Test Email Alerts

Run a monitor that you know will fail to test email alerts:
```bash
source .venv/bin/activate
python run_all_monitors.py
```

Check your email inbox for alert notifications.

## Slack Alerts Setup

### Step 1: Create a Slack Webhook

1. **Go to your Slack workspace**
2. **Create a Slack App**:
   - Visit https://api.slack.com/apps
   - Click "Create New App" → "From scratch"
   - Name it "Monitor Alerts" and select your workspace

3. **Enable Incoming Webhooks**:
   - In your app settings, click "Incoming Webhooks"
   - Toggle "Activate Incoming Webhooks" to On
   - Click "Add New Webhook to Workspace"
   - Select the channel where you want alerts
   - Click "Allow"

4. **Copy the Webhook URL**:
   - You'll see a webhook URL like: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX`
   - Copy this URL

### Step 2: Add Slack Webhook to Monitors

1. Go to the "Monitors" page in the app
2. Click "Add/Edit Monitor" tab
3. Expand "🔔 Alert Configuration"
4. Enable alerts
5. Paste your Slack webhook URL in the "Slack Webhook URL" field
6. Click "🧪 Test Slack Webhook" to verify it works
7. Save the monitor

### Step 3: Test Slack Alerts

Run a monitor that you know will fail:
```bash
source .venv/bin/activate
python run_all_monitors.py
```

Check your Slack channel for alert notifications.

## Alert Message Format

### Email Alerts

Email alerts include:
- Monitor name and status
- Timestamp and duration
- Full error message
- Link to check the dashboard for screenshots
- Both HTML and plain text versions

### Slack Alerts

Slack alerts include:
- Monitor name with status emoji
- Status, duration, time, and URL
- Error message in code block
- Formatted for easy reading

## Configuring Alerts Per Monitor

Each monitor can have its own alert configuration:

1. **Enable/Disable Alerts**: Toggle alerts on/off per monitor
2. **Multiple Email Recipients**: Add multiple email addresses
3. **Slack Channel**: Each monitor can alert different Slack channels
4. **Mix and Match**: Use email only, Slack only, or both

## Example Monitor with Alerts

```python
from src.monitoring.monitor import Monitor
from src.storage.storage import Storage

storage = Storage()

monitor = Monitor(
    name="Production Login Check",
    url="https://app.example.com",
    steps=[
        {"type": "navigate", "url": "https://app.example.com/login"},
        {"type": "fill", "selector": "#username", "value": "test@example.com"},
        {"type": "fill", "selector": "#password", "value": "${PASSWORD}"},
        {"type": "click", "selector": "button[type='submit']"},
        {"type": "verify", "condition": "url_contains", "expected": "/dashboard"}
    ],
    alert_emails=["admin@example.com", "team@example.com"],
    slack_webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    alerts_enabled=True
)

storage.save_monitor(monitor)
```

## Troubleshooting

### Email Alerts Not Working

1. **Check SMTP credentials**: Verify all environment variables are set correctly
2. **Gmail App Password**: Make sure you're using an App Password, not your regular password
3. **Firewall**: Ensure port 587 is not blocked
4. **Check logs**: Look for error messages in the console when running monitors
5. **Test connection**:
```python
from src.alerts.email_alert import EmailAlert
email_alert = EmailAlert()
print("Email configured:", email_alert.is_configured())
```

### Slack Alerts Not Working

1. **Check webhook URL**: Make sure it starts with `https://hooks.slack.com/services/`
2. **Test webhook**: Use the "Test Slack Webhook" button in the UI
3. **Webhook expired**: Webhooks can expire; create a new one if needed
4. **Channel permissions**: Ensure the Slack app has permission to post to the channel

### Alerts Not Being Sent

1. **Monitor enabled**: Ensure the monitor is enabled
2. **Alerts enabled**: Check that `alerts_enabled` is True for the monitor
3. **Recipients configured**: Verify email addresses or Slack webhook is set
4. **Test actually failed**: Alerts only send on failures, not successes
5. **Check runner settings**: Ensure `send_alerts=True` when creating `MonitorRunner`

## Security Best Practices

1. **Never commit `.env` file**: It contains sensitive credentials
2. **Use App Passwords**: For Gmail, use App Passwords instead of your main password
3. **Limit webhook access**: Only share Slack webhooks with trusted systems
4. **Rotate credentials**: Regularly update SMTP passwords and regenerate webhooks
5. **Use environment variables**: Always store credentials in `.env`, never in code

## Advanced Configuration

### Custom SMTP Port

Some providers use different ports:
- Port 587: TLS (recommended)
- Port 465: SSL
- Port 25: Unencrypted (not recommended)

### Disable TLS

If your SMTP server doesn't support TLS (not recommended):
```python
from src.alerts.email_alert import EmailAlert
email_alert = EmailAlert(use_tls=False)
```

### Multiple Slack Channels

To send alerts to multiple Slack channels, create multiple monitors or use a Slack workflow to forward messages.

## Testing Alerts Without Failing Tests

You can manually trigger alerts for testing:

```python
from src.monitoring.monitor import Monitor
from src.monitoring.runner import MonitorRunner
from src.storage.storage import Storage

storage = Storage()
monitor = storage.get_monitors()[0]  # Get first monitor

# Create a fake failure for testing
from src.monitoring.monitor import TestRun
from datetime import datetime

test_run = TestRun(
    monitor_id=monitor.id,
    status='failed',
    started_at=datetime.now(),
    completed_at=datetime.now(),
    error_message="This is a test alert",
    duration_ms=1000
)

# Manually send alerts
runner = MonitorRunner()
runner._send_alerts(monitor, test_run)
```

## Getting Help

If you're still having issues:
1. Check the error messages in the console
2. Verify your SMTP/Slack credentials
3. Test with a simple monitor first
4. Review the logs in the terminal where you run the app
