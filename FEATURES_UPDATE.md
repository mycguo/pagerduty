# New Feature: Email & Slack Alerts

## What's New

The monitoring system now supports automatic notifications when tests fail!

### Alert Features

- 📧 **Email Alerts**: Receive formatted email notifications via SMTP
- 💬 **Slack Alerts**: Get instant Slack messages via webhooks
- 🔔 **Per-Monitor Configuration**: Each monitor can have its own alert settings
- ✅ **Test Webhooks**: Test your Slack integration directly from the UI
- 🎨 **Rich Formatting**: Beautiful HTML emails and structured Slack messages

## Quick Setup

### 1. Email Alerts

Edit `.env` file:
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your.email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your.email@gmail.com
```

For Gmail: [Create an App Password](https://myaccount.google.com/apppasswords)

### 2. Slack Alerts

1. Create a Slack webhook: https://api.slack.com/messaging/webhooks
2. Copy the webhook URL
3. Add it to your monitor in the UI

### 3. Configure Monitors

In the Streamlit UI:
1. Go to "Monitors" → "Add/Edit Monitor"
2. Expand "🔔 Alert Configuration"
3. Enable alerts
4. Add email addresses (one per line)
5. Add Slack webhook URL
6. Test the Slack webhook
7. Save monitor

## Testing Alerts

Run the interactive test script:
```bash
source .venv/bin/activate
python test_alerts.py
```

This will guide you through testing both email and Slack alerts.

## Documentation

- **Full Setup Guide**: See `ALERTS_SETUP.md` for detailed configuration
- **Email Providers**: Gmail, SendGrid, Mailgun, AWS SES supported
- **Slack Setup**: Step-by-step webhook creation guide
- **Troubleshooting**: Common issues and solutions

## Example

Create a monitor with alerts:
```bash
source .venv/bin/activate
python create_monitor_with_alerts.py
```

Then modify it to fail and run:
```bash
python run_all_monitors.py
```

You'll receive alerts via email and/or Slack!

## What Gets Alerted

Alerts are sent when:
- ❌ Test fails (step execution error)
- ⚠️ Test errors (unexpected exception)

Alerts are NOT sent when:
- ✅ Test passes successfully

## Alert Content

### Email Includes:
- Monitor name and status
- Timestamp and duration
- Full error message
- Note to check dashboard for screenshots

### Slack Includes:
- Status emoji and monitor name
- Duration, time, and URL
- Error message in code block
- Formatted for easy scanning

## Integration with Existing Monitors

All existing monitors have been updated with default alert settings:
- Alerts enabled: ✅ Yes
- Email addresses: [] (empty - add yours)
- Slack webhook: None (add yours)

Simply edit each monitor to add your notification channels!

## Next Steps

1. ✅ Configure SMTP in `.env`
2. ✅ Create Slack webhook
3. ✅ Add alert settings to your monitors
4. ✅ Test with `python test_alerts.py`
5. ✅ Run monitors and receive alerts!

For detailed setup instructions, see `ALERTS_SETUP.md`.
