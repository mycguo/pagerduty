"""Test results and logs UI."""
import streamlit as st
import pandas as pd
from datetime import datetime

from src.storage.storage import Storage


def render_results(storage: Storage):
    """Render the test results page."""
    st.title("📊 Test Results & Logs")

    # Filters
    col1, col2 = st.columns([2, 1])

    with col1:
        monitors = storage.get_monitors()
        monitor_options = {"All Monitors": None}
        monitor_options.update({m.name: m.id for m in monitors})

        selected_monitor_name = st.selectbox("Filter by Monitor", list(monitor_options.keys()))
        selected_monitor_id = monitor_options[selected_monitor_name]

    with col2:
        limit = st.number_input("Number of Results", min_value=10, max_value=500, value=50)

    # Get test runs
    test_runs = storage.get_test_runs(monitor_id=selected_monitor_id, limit=limit)

    if not test_runs:
        st.info("No test results found.")
        return

    # Summary stats
    success_count = len([r for r in test_runs if r.status == 'success'])
    failed_count = len([r for r in test_runs if r.status == 'failed'])
    error_count = len([r for r in test_runs if r.status == 'error'])
    success_rate = (success_count / len(test_runs) * 100) if test_runs else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Runs", len(test_runs))
    with col2:
        st.metric("Success", success_count)
    with col3:
        st.metric("Failed", failed_count + error_count)
    with col4:
        st.metric("Success Rate", f"{success_rate:.1f}%")

    st.divider()

    # Test runs list
    for run in test_runs:
        monitor = storage.get_monitor(run.monitor_id)
        monitor_name = monitor.name if monitor else "Unknown"

        status_icon = "✅" if run.status == 'success' else "❌"
        status_color = "green" if run.status == 'success' else "red"

        with st.expander(
            f"{status_icon} {monitor_name} - {run.started_at.strftime('%Y-%m-%d %H:%M:%S')}",
            expanded=False
        ):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Status:** :{status_color}[{run.status.upper()}]")
                st.write(f"**Duration:** {run.duration_ms / 1000:.2f} seconds")
                st.write(f"**Started:** {run.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
                if run.completed_at:
                    st.write(f"**Completed:** {run.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")

                if run.error_message:
                    st.error(f"**Error:** {run.error_message}")

            with col2:
                # Show screenshot if available
                if run.screenshot_path:
                    try:
                        st.image(run.screenshot_path, caption="Screenshot on failure", width="stretch")
                    except:
                        st.warning("Screenshot not found")

            # Step results
            if run.step_results:
                st.markdown("**Step Results:**")

                step_data = []
                for step_result in run.step_results:
                    step = step_result.get('step', {})
                    step_idx = step_result.get('step_index', 0)
                    status = step_result.get('status', 'unknown')
                    duration_ms = step_result.get('duration_ms', 0)
                    error = step_result.get('error_message', '')

                    step_type = step.get('type', 'unknown')
                    step_icon = "✅" if status == 'success' else "❌"

                    # Build step description
                    if step_type == 'navigate':
                        desc = f"Navigate to {step.get('url')}"
                    elif step_type == 'click':
                        desc = f"Click {step.get('selector')}"
                    elif step_type == 'fill':
                        desc = f"Fill {step.get('selector')}"
                    elif step_type == 'verify':
                        desc = f"Verify {step.get('condition')}"
                    else:
                        desc = step.get('description', step_type)

                    step_data.append({
                        'Step': f"{step_idx + 1}",
                        'Status': step_icon,
                        'Action': desc,
                        'Duration': f"{duration_ms}ms",
                        'Error': error if error else '-'
                    })

                df = pd.DataFrame(step_data)
                st.dataframe(df, width="stretch", hide_index=True)
