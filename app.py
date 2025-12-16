"""Main Streamlit application for web monitoring."""
import streamlit as st
from dotenv import load_dotenv
import logging
import os
from pathlib import Path

from src.storage.storage import Storage
from src.monitoring.scheduler import MonitorScheduler
from src.ui.dashboard import render_dashboard
from src.ui.monitors import render_monitors
from src.ui.results import render_results

# Configure logging to show in console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Print startup diagnostics
print("\n" + "="*60)
print("WEB MONITORING DASHBOARD - STARTUP DIAGNOSTICS")
print("="*60)
print(f"Working Directory: {os.getcwd()}")
print(f"DATA_DIR env var: {os.getenv('DATA_DIR', 'Not set')}")
print(f"RENDER env var: {os.getenv('RENDER', 'Not set')}")
print(f"Running in Docker: {os.path.exists('/.dockerenv')}")

# Check for default monitors in the image
default_monitors_path = "/app/default_monitors.json"
if os.path.exists(default_monitors_path):
    file_size = os.path.getsize(default_monitors_path)
    print(f"✓ Default monitors found: {default_monitors_path} ({file_size} bytes)")
else:
    print(f"✗ Default monitors NOT found at: {default_monitors_path}")
    # Check alternate locations
    alt_path = Path(os.getcwd()) / "default_monitors.json"
    if alt_path.exists():
        print(f"  Found at alternate location: {alt_path}")

# Check data directory
data_dir = os.getenv('DATA_DIR', '/app/data')
print(f"\nData Directory: {data_dir}")
if os.path.exists(data_dir):
    print(f"✓ Data directory exists")
    monitors_file = Path(data_dir) / "monitors.json"
    if monitors_file.exists():
        file_size = monitors_file.stat().st_size
        print(f"✓ monitors.json exists ({file_size} bytes)")
        try:
            import json
            with open(monitors_file) as f:
                monitors_data = json.load(f)
            print(f"✓ monitors.json contains {len(monitors_data)} monitors")
        except Exception as e:
            print(f"✗ Error reading monitors.json: {e}")
    else:
        print(f"✗ monitors.json NOT found at: {monitors_file}")
else:
    print(f"✗ Data directory does NOT exist: {data_dir}")

print("="*60 + "\n")

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
    """Get storage instance - uses Postgres if available, otherwise file storage."""
    logger.info("Initializing storage...")

    # Check if DATABASE_URL is available (Postgres)
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        logger.info("DATABASE_URL found - using PostgreSQL storage")
        print("\n[Storage] Using PostgreSQL for data persistence")
        try:
            from src.storage.postgres_storage import PostgresStorage
            storage = PostgresStorage(database_url)
            print(f"[Storage] PostgreSQL connection successful")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL storage: {e}")
            print(f"[Storage] ERROR: Failed to connect to PostgreSQL: {e}")
            print(f"[Storage] Falling back to file storage")
            from src.storage.storage import Storage
            storage = Storage()
    else:
        logger.info("No DATABASE_URL - using file-based storage")
        print("\n[Storage] Using file-based storage (data will not persist on Render free tier)")
        print("[Storage] To persist data, add a Postgres database in render.yaml")
        from src.storage.storage import Storage
        storage = Storage()

    monitors = storage.get_monitors()
    logger.info(f"Storage initialized with {len(monitors)} monitors")
    print(f"[Storage] Loaded {len(monitors)} monitors")
    for monitor in monitors:
        logger.info(f"  - {monitor.name} (enabled={monitor.enabled})")
        print(f"[Storage]   - {monitor.name} (enabled={monitor.enabled})")
    return storage

storage = get_storage()
logger.info(f"Storage instance created. Monitor count: {len(storage.get_monitors())}")

# Initialize Scheduler (ENABLED for Render - supports background processes)
@st.cache_resource
def get_scheduler(_storage_instance):
    return MonitorScheduler(_storage_instance)

scheduler = get_scheduler(storage)
# Sync jobs on every run to ensure updates are reflected
scheduler.sync_jobs()

# Sidebar
st.sidebar.title("🔍 Web Monitor")
st.sidebar.caption("Automated Browser Testing")

# Scheduler Status
st.sidebar.markdown("---")
st.sidebar.markdown("**System Status**")
st.sidebar.markdown(f"Scheduler: {'🟢 Running' if scheduler.scheduler.running else '🔴 Stopped'}")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation", ["📊 Dashboard", "⚙️ Monitors", "📝 Test Results"], label_visibility="collapsed")

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
elif page == "📝 Test Results":
    render_results(storage)
