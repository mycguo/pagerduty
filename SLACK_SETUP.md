# Slack Alert Setup

Slack alerts are configured via environment variables, making it easy to set up and keeping webhook URLs secure.

## Quick Setup

### Step 1: Create Slack Webhook

1. **Go to Slack API**: https://api.slack.com/apps
2. **Create New App** → "From scratch"
3. **Name it**: "Monitor Alerts" (or your preference)
4. **Select workspace**: Choose your Slack workspace
5. **Enable Incoming Webhooks**:
   - Click "Incoming Webhooks" in the sidebar
   - Toggle "Activate Incoming Webhooks" to **On**
6. **Add Webhook to Workspace**:
   - Click "Add New Webhook to Workspace"
   - Select the channel for alerts (e.g., #monitoring, #alerts)
   - Click "Allow"
7. **Copy Webhook URL**:
   ```
   https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
   ```

### Step 2: Add to Render Environment

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Select your service**: `web-monitoring-dashboard`
3. **Click "Environment" tab**
4. **Click "Add Environment Variable"**
5. **Add:**
   - **Key:** `SLACK_WEBHOOK_URL`
   - **Value:** Your webhook URL from Step 1
6. **Click "Save Changes"**

Render will automatically redeploy with Slack alerts enabled.

### Step 3: Test Slack Alerts

1. Open your deployed app
2. Go to **Monitors** page
3. Click **Add/Edit Monitor** tab or edit an existing monitor
4. Expand **🔔 Alert Configuration**
5. You should see: ✅ "Slack webhook configured via environment variables"
6. Click **🧪 Test Slack Webhook**
7. Check your Slack channel for the test message!

## Local Development Setup

For local development, add to your `.env` file:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

Or use Streamlit secrets (`.streamlit/secrets.toml`):

```toml
slack_webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

## How It Works

- **Webhook URL is never stored in monitor configurations** - it's loaded from environment variables
- **All monitors share the same Slack channel** - configured once via environment variable
- **Secure** - webhook URL is not exposed in the UI or stored in the database
- **Simple** - no per-monitor configuration needed

## Alert Format

When a monitor fails, Slack receives a formatted message with:

- ❌ Monitor name and failure status
- ⏱️ Duration and timestamp
- 🔗 Monitor URL
- 📝 Error message
- 💡 Link to check dashboard for screenshots

## Troubleshooting

### "⚠️ Slack webhook not configured"

**Solution:** Add `SLACK_WEBHOOK_URL` environment variable in Render Dashboard (see Step 2 above)

### Test button fails

**Common causes:**
- Webhook URL is incorrect
- Webhook was deleted/revoked in Slack
- Slack app doesn't have permission to post to the channel

**Fix:**
1. Verify webhook URL in Render environment variables
2. Test the webhook with curl:
   ```bash
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Test message"}' \
     YOUR_WEBHOOK_URL
   ```
3. If curl fails, recreate the webhook in Slack

### Not receiving alerts for failed monitors

**Check:**
1. Monitor has "Enable alerts" checked
2. Monitor is enabled
3. Test actually failed (not success)
4. Check Render logs for "Slack alert sent" or error messages

## Multiple Channels

To send alerts to multiple Slack channels, you have two options:

**Option 1: Use Slack workflow to forward messages**
- Keep one webhook
- Create a Slack workflow that forwards messages from the alert channel to other channels

**Option 2: Run multiple instances**
- Deploy separate instances with different `SLACK_WEBHOOK_URL` values
- Each instance monitors different services and alerts different channels

## Security Best Practices

✅ **Do:**
- Store webhook URL in environment variables (Render Dashboard)
- Rotate webhook URLs periodically
- Use separate webhooks for production/staging

❌ **Don't:**
- Commit webhook URLs to Git
- Share webhook URLs in chat or documentation
- Store webhook URLs in monitor configurations (app prevents this)

## Webhook URL Format

Slack webhook URLs always follow this format:
```
https://hooks.slack.com/services/T[WORKSPACE_ID]/B[CHANNEL_ID]/[SECRET_TOKEN]
```

If your URL doesn't match this pattern, it's not a valid Slack webhook URL.

## Customizing Alert Messages

The alert format is defined in `src/alerts/slack_alert.py`. To customize:

1. Edit the `_create_slack_payload()` method
2. Use Slack's [Block Kit Builder](https://app.slack.com/block-kit-builder) to design custom layouts
3. Update the payload structure in the code

## Need Help?

- Slack Webhook Documentation: https://api.slack.com/messaging/webhooks
- Render Environment Variables: https://render.com/docs/environment-variables
- Check app logs in Render Dashboard for detailed error messages
