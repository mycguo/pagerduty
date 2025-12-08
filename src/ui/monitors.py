"""Monitor configuration UI."""
import streamlit as st
import json
from datetime import datetime

from src.monitoring.monitor import Monitor
from src.monitoring.runner import MonitorRunner
from src.storage.storage import Storage


def render_monitors(storage: Storage):
    """Render the monitors configuration page."""
    st.title("⚙️ Monitor Configuration")

    tab1, tab2 = st.tabs(["📋 All Monitors", "➕ Add/Edit Monitor"])

    with tab1:
        render_monitor_list(storage)

    with tab2:
        render_monitor_editor(storage)


def render_monitor_list(storage: Storage):
    """Render the list of monitors."""
    monitors = storage.get_monitors()

    if not monitors:
        st.info("No monitors configured yet. Use the 'Add/Edit Monitor' tab to create one.")
        return

    for monitor in monitors:
        with st.expander(f"{'✅' if monitor.enabled else '⏸️'} {monitor.name}", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**URL:** {monitor.url}")
                st.write(f"**Schedule:** {monitor.schedule}")
                st.write(f"**Steps:** {len(monitor.steps)}")
                st.write(f"**Created:** {monitor.created_at.strftime('%Y-%m-%d %H:%M')}")

                # Alert status
                if monitor.alerts_enabled:
                    alert_methods = []
                    if monitor.alert_emails:
                        alert_methods.append(f"📧 {len(monitor.alert_emails)} email(s)")
                    if monitor.slack_webhook_url:
                        alert_methods.append("💬 Slack")
                    if alert_methods:
                        st.write(f"**Alerts:** {', '.join(alert_methods)}")
                    else:
                        st.write("**Alerts:** ⚠️ Enabled but not configured")
                else:
                    st.write("**Alerts:** 🔕 Disabled")

            with col2:
                # Run button
                if st.button(f"▶️ Run", key=f"run_{monitor.id}"):
                    with st.spinner(f"Running {monitor.name}..."):
                        runner = MonitorRunner(headless=True)
                        result = runner.run_monitor(monitor)
                        storage.save_test_run(result)

                        if result.status == 'success':
                            st.success(f"✅ Test passed in {result.duration_ms / 1000:.2f}s")
                        else:
                            st.error(f"❌ Test failed: {result.error_message}")

                # Toggle enable/disable
                if st.button(f"{'⏸️ Disable' if monitor.enabled else '▶️ Enable'}", key=f"toggle_{monitor.id}"):
                    monitor.enabled = not monitor.enabled
                    monitor.updated_at = datetime.now()
                    storage.save_monitor(monitor)
                    st.rerun()

                # Delete button
                if st.button(f"🗑️ Delete", key=f"delete_{monitor.id}"):
                    storage.delete_monitor(monitor.id)
                    st.success(f"Deleted {monitor.name}")
                    st.rerun()

            # Show steps
            st.markdown("**Steps:**")
            for idx, step in enumerate(monitor.steps):
                step_type = step.get('type', 'unknown')
                description = step.get('description', '')

                if step_type == 'navigate':
                    st.text(f"{idx + 1}. Navigate to: {step.get('url')}")
                elif step_type == 'click':
                    st.text(f"{idx + 1}. Click: {step.get('selector')}")
                elif step_type == 'fill':
                    st.text(f"{idx + 1}. Fill: {step.get('selector')}")
                elif step_type == 'verify':
                    st.text(f"{idx + 1}. Verify: {step.get('condition')}")
                else:
                    st.text(f"{idx + 1}. {step_type}" + (f" - {description}" if description else ""))

            # Show recent runs
            recent_runs = storage.get_test_runs(monitor_id=monitor.id, limit=5)
            if recent_runs:
                st.markdown("**Recent Runs:**")
                for run in recent_runs:
                    status_icon = "✅" if run.status == 'success' else "❌"
                    st.text(f"{status_icon} {run.started_at.strftime('%Y-%m-%d %H:%M:%S')} - {run.duration_ms / 1000:.2f}s")


def render_monitor_editor(storage: Storage):
    """Render the monitor editor form."""
    st.subheader("Create or Edit Monitor")

    # Basic information
    monitor_name = st.text_input("Monitor Name", placeholder="Production Login Check")
    monitor_url = st.text_input("Base URL", placeholder="https://app.example.com")

    st.divider()

    # Steps configuration
    st.subheader("Test Steps")
    st.markdown("Configure the steps to test your application. You can use JSON format for complex configurations.")

    # Example template
    with st.expander("📖 View Example Configuration"):
        example_config = {
            "steps": [
                {
                    "type": "navigate",
                    "url": "https://app.example.com/login"
                },
                {
                    "type": "fill",
                    "selector": "#username",
                    "value": "user@example.com"
                },
                {
                    "type": "fill",
                    "selector": "#password",
                    "value": "${PASSWORD_ENV}"
                },
                {
                    "type": "click",
                    "selector": "button[type='submit']"
                },
                {
                    "type": "verify",
                    "condition": "url_contains",
                    "expected": "/dashboard"
                },
                {
                    "type": "click",
                    "selector": "a[href='/reports']"
                },
                {
                    "type": "verify",
                    "condition": "element_exists",
                    "selector": ".report-table"
                }
            ]
        }
        st.json(example_config)

    # Step configuration
    steps_json = st.text_area(
        "Steps (JSON format)",
        value='[\n  {\n    "type": "navigate",\n    "url": "https://example.com"\n  }\n]',
        height=400
    )

    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        schedule = st.text_input("Schedule (cron format)", value="*/5 * * * *",
                                 help="Default: Every 5 minutes")
        enabled = st.checkbox("Enable monitor", value=True)

    # Alert configuration
    with st.expander("🔔 Alert Configuration"):
        st.markdown("Configure notifications for test failures.")

        alerts_enabled = st.checkbox("Enable alerts", value=True,
                                      help="Send notifications when tests fail")

        st.markdown("**Email Alerts**")
        email_addresses = st.text_area(
            "Email addresses (one per line)",
            placeholder="admin@example.com\nteam@example.com",
            height=100,
            help="Enter email addresses to notify on failures"
        )

        st.markdown("**Slack Alerts**")
        slack_webhook = st.text_input(
            "Slack Webhook URL",
            placeholder="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
            help="Enter your Slack webhook URL to send notifications to a Slack channel"
        )

        if slack_webhook:
            from src.alerts.slack_alert import SlackAlert
            if st.button("🧪 Test Slack Webhook"):
                slack_alert = SlackAlert()
                if slack_alert.send_test_message(slack_webhook):
                    st.success("✅ Test message sent to Slack!")
                else:
                    st.error("❌ Failed to send test message. Check your webhook URL.")

    # Save button
    if st.button("💾 Save Monitor", type="primary"):
        try:
            # Parse steps JSON
            steps_data = json.loads(steps_json)

            if not isinstance(steps_data, list):
                st.error("Steps must be a JSON array")
                return

            # Parse email addresses
            alert_emails = [email.strip() for email in email_addresses.split('\n') if email.strip()]

            # Create monitor
            monitor = Monitor(
                name=monitor_name,
                url=monitor_url,
                steps=steps_data,
                enabled=enabled,
                schedule=schedule,
                alert_emails=alert_emails,
                slack_webhook_url=slack_webhook if slack_webhook else None,
                alerts_enabled=alerts_enabled
            )

            # Save to storage
            storage.save_monitor(monitor)
            st.success(f"✅ Monitor '{monitor_name}' saved successfully!")

            # Offer to run it
            if st.button("▶️ Run Now"):
                with st.spinner(f"Running {monitor_name}..."):
                    runner = MonitorRunner(headless=True)
                    result = runner.run_monitor(monitor)
                    storage.save_test_run(result)

                    if result.status == 'success':
                        st.success(f"✅ Test passed in {result.duration_ms / 1000:.2f}s")
                    else:
                        st.error(f"❌ Test failed: {result.error_message}")

        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            st.error(f"Error saving monitor: {str(e)}")
