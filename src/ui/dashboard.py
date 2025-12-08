"""Dashboard UI for monitoring overview."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List

from src.monitoring.monitor import Monitor, TestRun
from src.storage.storage import Storage


def render_dashboard(storage: Storage):
    """Render the main dashboard page."""
    st.title("🔍 Web App Monitoring Dashboard")

    monitors = storage.get_monitors()

    if not monitors:
        st.info("No monitors configured yet. Go to 'Monitors' page to add your first monitor.")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    total_monitors = len(monitors)
    enabled_monitors = len([m for m in monitors if m.enabled])

    # Get latest test runs for each monitor
    latest_runs = []
    for monitor in monitors:
        latest_run = storage.get_latest_test_run(monitor.id)
        if latest_run:
            latest_runs.append(latest_run)

    passing = len([r for r in latest_runs if r.status == 'success'])
    failing = len([r for r in latest_runs if r.status in ['failed', 'error']])

    with col1:
        st.metric("Total Monitors", total_monitors)
    with col2:
        st.metric("Enabled", enabled_monitors)
    with col3:
        st.metric("✅ Passing", passing)
    with col4:
        st.metric("❌ Failing", failing)

    st.divider()

    # Monitor status table
    st.subheader("Monitor Status")

    monitor_data = []
    for monitor in monitors:
        latest_run = storage.get_latest_test_run(monitor.id)

        if latest_run:
            status_icon = "✅" if latest_run.status == 'success' else "❌"
            last_run = latest_run.started_at.strftime("%Y-%m-%d %H:%M:%S")
            duration = f"{latest_run.duration_ms / 1000:.2f}s"
            status = latest_run.status
        else:
            status_icon = "⚪"
            last_run = "Never"
            duration = "-"
            status = "No runs"

        monitor_data.append({
            'Status': status_icon,
            'Name': monitor.name,
            'URL': monitor.url,
            'Last Run': last_run,
            'Duration': duration,
            'Result': status,
            'Enabled': '✓' if monitor.enabled else '✗'
        })

    if monitor_data:
        df = pd.DataFrame(monitor_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

    # Recent test runs
    st.divider()
    st.subheader("Recent Test Runs")

    all_runs = storage.get_test_runs(limit=50)

    if all_runs:
        # Success rate over time
        run_data = []
        for run in all_runs:
            monitor = storage.get_monitor(run.monitor_id)
            run_data.append({
                'Timestamp': run.started_at,
                'Monitor': monitor.name if monitor else 'Unknown',
                'Status': run.status,
                'Duration (s)': run.duration_ms / 1000
            })

        runs_df = pd.DataFrame(run_data)

        # Plot success rate
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Success Rate (Last 50 Runs)**")
            status_counts = runs_df['Status'].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                color=status_counts.index,
                color_discrete_map={'success': '#28a745', 'failed': '#dc3545', 'error': '#ffc107'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Response Time Trend**")
            fig = px.line(
                runs_df,
                x='Timestamp',
                y='Duration (s)',
                color='Monitor',
                markers=True
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        # Recent runs table
        st.markdown("**Latest Test Runs**")
        display_df = runs_df.copy()
        display_df['Timestamp'] = display_df['Timestamp'].dt.strftime("%Y-%m-%d %H:%M:%S")
        display_df['Duration (s)'] = display_df['Duration (s)'].round(2)
        st.dataframe(display_df.head(20), use_container_width=True, hide_index=True)
    else:
        st.info("No test runs yet. Run a monitor to see results.")
