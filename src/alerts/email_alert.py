"""Email alert handler."""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from datetime import datetime

from src.alerts.base import AlertHandler


class EmailAlert(AlertHandler):
    """Sends email alerts using SMTP."""

    def __init__(
        self,
        smtp_host: str = None,
        smtp_port: int = None,
        smtp_username: str = None,
        smtp_password: str = None,
        from_email: str = None,
        use_tls: bool = True
    ):
        """
        Initialize email alert handler.

        Args:
            smtp_host: SMTP server host (default: from SMTP_HOST env var)
            smtp_port: SMTP server port (default: from SMTP_PORT env var or 587)
            smtp_username: SMTP username (default: from SMTP_USERNAME env var)
            smtp_password: SMTP password (default: from SMTP_PASSWORD env var)
            from_email: From email address (default: from SMTP_FROM_EMAIL env var)
            use_tls: Whether to use TLS (default: True)
        """
        self.smtp_host = smtp_host or os.getenv('SMTP_HOST')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = smtp_username or os.getenv('SMTP_USERNAME')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD')
        self.from_email = from_email or os.getenv('SMTP_FROM_EMAIL')
        self.use_tls = use_tls

    def is_configured(self) -> bool:
        """Check if email alerts are properly configured."""
        return all([
            self.smtp_host,
            self.smtp_username,
            self.smtp_password,
            self.from_email
        ])

    def send_alert(self, monitor_name: str, test_run: Dict[str, Any]) -> bool:
        """
        Send an email alert for a failed test run.

        Args:
            monitor_name: Name of the monitor that failed
            test_run: Test run result dictionary

        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.is_configured():
            print("Email alerts not configured. Set SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, and SMTP_FROM_EMAIL.")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🚨 Monitor Failed: {monitor_name}"
            msg['From'] = self.from_email
            msg['To'] = ', '.join(test_run.get('alert_emails', []))

            # Create HTML content
            html_content = self._create_html_content(monitor_name, test_run)
            text_content = self._create_text_content(monitor_name, test_run)

            # Attach both text and HTML versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            print(f"✅ Email alert sent for {monitor_name}")
            return True

        except Exception as e:
            print(f"❌ Failed to send email alert: {str(e)}")
            return False

    def _create_text_content(self, monitor_name: str, test_run: Dict[str, Any]) -> str:
        """Create plain text email content."""
        status = test_run.get('status', 'unknown')
        error_message = test_run.get('error_message', 'No error message')
        started_at = test_run.get('started_at', '')
        duration_ms = test_run.get('duration_ms', 0)

        content = f"""
Monitor Alert: {monitor_name}

Status: {status.upper()}
Time: {started_at}
Duration: {duration_ms}ms

Error:
{error_message}

Please check the monitoring dashboard for more details.
"""
        return content

    def _create_html_content(self, monitor_name: str, test_run: Dict[str, Any]) -> str:
        """Create HTML email content."""
        status = test_run.get('status', 'unknown')
        error_message = test_run.get('error_message', 'No error message')
        started_at = test_run.get('started_at', '')
        duration_ms = test_run.get('duration_ms', 0)

        status_color = '#dc3545' if status == 'failed' else '#ffc107'
        status_emoji = '❌' if status == 'failed' else '⚠️'

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: {status_color};
            color: white;
            padding: 20px;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: #f8f9fa;
            padding: 20px;
            border: 1px solid #dee2e6;
            border-top: none;
            border-radius: 0 0 5px 5px;
        }}
        .info-row {{
            margin: 10px 0;
            padding: 10px;
            background-color: white;
            border-radius: 3px;
        }}
        .label {{
            font-weight: bold;
            color: #666;
        }}
        .error-box {{
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 3px;
            padding: 15px;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
        }}
        .footer {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            font-size: 0.9em;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h2>{status_emoji} Monitor Failed: {monitor_name}</h2>
    </div>
    <div class="content">
        <div class="info-row">
            <span class="label">Status:</span> {status.upper()}
        </div>
        <div class="info-row">
            <span class="label">Time:</span> {started_at}
        </div>
        <div class="info-row">
            <span class="label">Duration:</span> {duration_ms}ms
        </div>
        <div class="error-box">
            <strong>Error:</strong><br>
            {error_message}
        </div>
        <div class="footer">
            Please check the monitoring dashboard for more details and screenshots.
        </div>
    </div>
</body>
</html>
"""
        return html
