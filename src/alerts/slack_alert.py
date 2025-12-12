import streamlit as st
import requests
import os
from typing import Dict, Any
from datetime import datetime

from src.alerts.base import AlertHandler


class SlackAlert(AlertHandler):
    """Sends alerts to Slack using webhooks."""

    def __init__(self, webhook_url: str = None):
        """
        Initialize Slack alert handler.

        Args:
            webhook_url: Slack webhook URL (default: from monitor config or secrets)
        """
        self.webhook_url = webhook_url

    def send_alert(self, monitor_name: str, test_run: Dict[str, Any]) -> bool:
        """
        Send a Slack alert for a failed test run.

        Args:
            monitor_name: Name of the monitor that failed
            test_run: Test run result dictionary

        Returns:
            True if alert was sent successfully, False otherwise
        """
        # Priority: 1. Constructor arg 2. Run/Monitor config 3. Environment variable 4. Streamlit secrets
        webhook_url = self.webhook_url or test_run.get('slack_webhook_url')
        
        if not webhook_url:
            # Try environment variable (for Railway, Docker, etc.)
            webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        
        if not webhook_url:
            # Try Streamlit secrets (for local development)
            try:
                webhook_url = st.secrets.get("slack_webhook_url")
            except (FileNotFoundError, KeyError):
                pass # Secrets file might not exist or key missing

        if not webhook_url:
            # Silent fail if just not configured
            return False

        try:
            payload = self._create_slack_payload(monitor_name, test_run)
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                print(f"✅ Slack alert sent for {monitor_name}")
                return True
            else:
                print(f"❌ Slack alert failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"❌ Failed to send Slack alert: {str(e)}")
            return False

    def _create_slack_payload(self, monitor_name: str, test_run: Dict[str, Any]) -> Dict[str, Any]:
        """Create Slack message payload."""
        status = test_run.get('status', 'unknown')
        error_message = test_run.get('error_message', 'No error message')
        started_at = test_run.get('started_at', '')
        duration_ms = test_run.get('duration_ms', 0)
        monitor_url = test_run.get('url', '')

        # Determine color and emoji based on status
        if status == 'failed':
            color = '#dc3545'
            emoji = ':x:'
        elif status == 'error':
            color = '#ffc107'
            emoji = ':warning:'
        else:
            color = '#6c757d'
            emoji = ':grey_question:'

        # Create Slack blocks format for better formatting
        payload = {
            "attachments": [
                {
                    "color": color,
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": f"{emoji} Monitor Failed: {monitor_name}",
                                "emoji": True
                            }
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Status:*\n{status.upper()}"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Duration:*\n{duration_ms}ms"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Time:*\n{started_at}"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*URL:*\n{monitor_url if monitor_url else 'N/A'}"
                                }
                            ]
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Error:*\n```{error_message}```"
                            }
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": "Check the monitoring dashboard for detailed logs and screenshots."
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        return payload

    def send_test_message(self, webhook_url: str) -> bool:
        """
        Send a test message to verify Slack webhook is working.

        Args:
            webhook_url: Slack webhook URL to test

        Returns:
            True if test message was sent successfully
        """
        try:
            payload = {
                "text": "🔍 Test message from Web Monitoring App",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "✅ *Slack integration is working!*\n\nYou will receive notifications here when monitors fail."
                        }
                    }
                ]
            }

            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            return response.status_code == 200

        except Exception as e:
            print(f"Failed to send test message: {str(e)}")
            return False
