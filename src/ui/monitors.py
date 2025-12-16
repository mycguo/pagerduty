"""Monitor configuration UI."""
import streamlit as st
import json
import os
from datetime import datetime

from src.monitoring.monitor import Monitor
from src.monitoring.runner import MonitorRunner
from src.storage.storage import Storage


def render_monitors(storage: Storage):
    """Render the monitors configuration page."""
    # Initialize session state for navigation
    if 'monitor_view' not in st.session_state:
        st.session_state.monitor_view = 'list'
    if 'editing_monitor_id' not in st.session_state:
        st.session_state.editing_monitor_id = None

    if st.session_state.monitor_view == 'list':
        render_monitor_list(storage)
    elif st.session_state.monitor_view in ['create', 'edit']:
        render_monitor_editor(storage)


def render_monitor_list(storage: Storage):
    """Render the list of monitors."""
    st.title("⚙️ Monitor Configuration")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Create New Monitor", use_container_width=True):
            st.session_state.monitor_view = 'create'
            st.session_state.editing_monitor_id = None
            st.rerun()

    monitors = storage.get_monitors()

    if not monitors:
        st.info("No monitors configured yet. Click 'Create New Monitor' to add one.")
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
                # Action buttons
                
                # Edit button
                if st.button("✏️ Edit", key=f"edit_{monitor.id}", use_container_width=True):
                    st.session_state.monitor_view = 'edit'
                    st.session_state.editing_monitor_id = monitor.id
                    st.rerun()

                # Run button
                if st.button(f"▶️ Run", key=f"run_{monitor.id}", use_container_width=True):
                    with st.spinner(f"Running {monitor.name}..."):
                        # Reload monitor from storage to get latest changes
                        current_monitor = storage.get_monitor(monitor.id)
                        if not current_monitor:
                            st.error(f"Monitor {monitor.name} not found")
                            st.rerun()
                            return
                        
                        runner = MonitorRunner(headless=True)
                        result = runner.run_monitor(current_monitor)
                        storage.save_test_run(result)

                        if result.status == 'success':
                            st.success(f"✅ Test passed in {result.duration_ms / 1000:.2f}s")
                        else:
                            st.error(f"❌ Test failed: {result.error_message}")

                # Toggle enable/disable
                btn_label = "⏸️ Disable" if monitor.enabled else "▶️ Enable"
                if st.button(btn_label, key=f"toggle_{monitor.id}", use_container_width=True):
                    monitor.enabled = not monitor.enabled
                    monitor.updated_at = datetime.now()
                    storage.save_monitor(monitor)
                    st.rerun()

                # Delete button
                if st.button(f"🗑️ Delete", key=f"delete_{monitor.id}", use_container_width=True):
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
    
    if st.button("← Back to List"):
        st.session_state.monitor_view = 'list'
        st.session_state.editing_monitor_id = None
        st.rerun()

    is_editing = st.session_state.monitor_view == 'edit'
    title = "Edit Monitor" if is_editing else "Create New Monitor"
    st.subheader(title)

    selected_monitor = None
    if is_editing and st.session_state.editing_monitor_id:
        selected_monitor = storage.get_monitor(st.session_state.editing_monitor_id)

    key_suffix = selected_monitor.id if selected_monitor else "new"

    # Defaults
    default_name = ""
    default_url = ""
    default_steps = '[\n  {\n    "type": "navigate",\n    "url": "https://example.com"\n  }\n]'
    default_schedule = "*/5 * * * *"
    default_enabled = True
    default_alerts_enabled = True
    default_emails = ""
    default_slack = ""

    # Override defaults if editing
    if selected_monitor:
        default_name = selected_monitor.name
        default_url = selected_monitor.url
        default_steps = json.dumps(selected_monitor.steps, indent=2)
        default_schedule = selected_monitor.schedule
        default_enabled = selected_monitor.enabled
        default_alerts_enabled = selected_monitor.alerts_enabled
        default_emails = "\n".join(selected_monitor.alert_emails)
        default_slack = selected_monitor.slack_webhook_url or ""

    # Basic information
    monitor_name = st.text_input("Monitor Name", value=default_name, placeholder="Production Login Check", key=f"monitor_name_{key_suffix}")
    monitor_url = st.text_input("Base URL", value=default_url, placeholder="https://app.example.com", key=f"monitor_url_{key_suffix}")

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
        value=default_steps,
        height=400,
        key=f"monitor_steps_{key_suffix}"
    )

    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        schedule = st.text_input("Schedule (cron format)", value=default_schedule,
                                 help="Default: Every 5 minutes", key=f"monitor_schedule_{key_suffix}")
        enabled = st.checkbox("Enable monitor", value=default_enabled, key=f"monitor_enabled_{key_suffix}")

    # Alert configuration
    with st.expander("🔔 Alert Configuration"):
        st.markdown("Configure notifications for test failures.")

        alerts_enabled = st.checkbox("Enable alerts", value=default_alerts_enabled,
                                      help="Send notifications when tests fail", key=f"monitor_alerts_enabled_{key_suffix}")

        st.markdown("**Email Alerts**")
        email_addresses = st.text_area(
            "Email addresses (one per line)",
            value=default_emails,
            placeholder="admin@example.com\nteam@example.com",
            height=100,
            help="Enter email addresses to notify on failures",
            key=f"monitor_emails_{key_suffix}"
        )

        st.markdown("**Slack Alerts**")
        
        # Check if configured in environment or secrets
        secret_webhook = os.getenv("SLACK_WEBHOOK_URL")  # Railway/Docker
        if not secret_webhook:
            try:
                secret_webhook = st.secrets.get("slack_webhook_url")  # Local development
            except (FileNotFoundError, KeyError):
                pass

        if secret_webhook:
            st.info("✅ Using Slack Webhook from secrets configuration.")
            slack_webhook = secret_webhook # Use secret for testing/saving logic locally if needed, 
                                           # or better: don't save it to the object if it matches secret.
                                           # For simplicity, we can leave the field empty in UI and logic handles it?
                                           # But we need to be able to test it.
            
            # If we want to allow overriding, we could show the input still. 
            # But request was to remove from JSON. So we should NOT save it if it's the secret.
            
            use_override = st.checkbox("Override secret webhook")
            if use_override:
                 slack_webhook_input = st.text_input(
                    "Slack Webhook URL (Override)",
                    value=default_slack if default_slack != secret_webhook else "",
                    placeholder="https://hooks.slack.com/...",
                    key=f"monitor_slack_{key_suffix}"
                )
                 slack_webhook = slack_webhook_input
            else:
                 slack_webhook = None # Don't save it to the monitor object
                 
        else:
            slack_webhook = st.text_input(
                "Slack Webhook URL",
                value=default_slack,
                placeholder="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
                help="Enter your Slack webhook URL to send notifications to a Slack channel",
                key=f"monitor_slack_{key_suffix}"
            )

        # Test button logic
        test_url = slack_webhook or secret_webhook
        if test_url:
            from src.alerts.slack_alert import SlackAlert
            if st.button("🧪 Test Slack Webhook", key=f"test_slack_{key_suffix}"):
                slack_alert = SlackAlert()
                # If we have a local override/input, test that. Otherwise test the secret.
                if slack_alert.send_test_message(test_url):
                    st.success("✅ Test message sent to Slack!")
                else:
                    st.error("❌ Failed to send test message. Check your webhook URL.")

    # Save button
    if st.button("💾 Save Monitor", type="primary", key=f"save_monitor_{key_suffix}"):
        try:
            # Parse steps JSON
            steps_data = json.loads(steps_json)

            if not isinstance(steps_data, list):
                st.error("Steps must be a JSON array")
                return

            # Parse email addresses
            alert_emails = [email.strip() for email in email_addresses.split('\n') if email.strip()]

            # Determine ID and Created At
            monitor_id = None
            created_at = datetime.now()
            
            if selected_monitor:
                monitor_id = selected_monitor.id
                created_at = selected_monitor.created_at

            # Create monitor (updates if ID exists)
            monitor = Monitor(
                name=monitor_name,
                url=monitor_url,
                steps=steps_data,
                enabled=enabled,
                schedule=schedule,
                alert_emails=alert_emails,
                slack_webhook_url=slack_webhook if slack_webhook else None,
                alerts_enabled=alerts_enabled,
                created_at=created_at,
                updated_at=datetime.now()
            )
            
            if monitor_id:
                monitor.id = monitor_id

            # Save to storage
            try:
                storage.save_monitor(monitor)
                
                # Verify save by reading back
                saved_monitor = storage.get_monitor(monitor.id)
                if not saved_monitor:
                    st.error(f"❌ Failed to save: Monitor not found after save")
                    return
                
                # Check if the saved data matches
                if saved_monitor.name != monitor_name or saved_monitor.url != monitor_url:
                    st.warning(f"⚠️ Save completed but data may not match. Please refresh and check.")
                else:
                    st.success(f"✅ Monitor '{monitor_name}' saved successfully!")
                
                # Return to list view
                st.session_state.monitor_view = 'list'
                st.session_state.editing_monitor_id = None
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error saving monitor: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            st.error(f"Error saving monitor: {str(e)}")
