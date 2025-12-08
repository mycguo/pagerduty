"""Main Streamlit application for web monitoring."""
import streamlit as st
from dotenv import load_dotenv

from src.storage.storage import Storage
from src.ui.dashboard import render_dashboard
from src.ui.monitors import render_monitors
from src.ui.results import render_results

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Web Monitoring Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize storage
@st.cache_resource
def get_storage():
    """Get storage instance."""
    return Storage()

storage = get_storage()

# Sidebar navigation
st.sidebar.title("🔍 Web Monitor")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "⚙️ Monitors", "📋 Test Results"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "**Web Monitoring App**\n\n"
    "Monitor your web applications by automating login flows and verifying critical functionality.\n\n"
    "Built with Streamlit and Playwright."
)

# Quick stats in sidebar
monitors = storage.get_monitors()
if monitors:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Quick Stats")
    enabled_count = len([m for m in monitors if m.enabled])
    st.sidebar.metric("Monitors", f"{enabled_count}/{len(monitors)} enabled")

    all_runs = storage.get_test_runs(limit=100)
    if all_runs:
        success_count = len([r for r in all_runs if r.status == 'success'])
        success_rate = (success_count / len(all_runs) * 100)
        st.sidebar.metric("Success Rate", f"{success_rate:.1f}%")

# Render selected page
if page == "📊 Dashboard":
    render_dashboard(storage)
elif page == "⚙️ Monitors":
    render_monitors(storage)
elif page == "📋 Test Results":
    render_results(storage)
