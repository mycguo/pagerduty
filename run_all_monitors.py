"""Run all monitors to populate test results."""
from src.monitoring.runner import MonitorRunner
from src.storage.storage import Storage

storage = Storage()
runner = MonitorRunner(headless=True)

monitors = storage.get_monitors()
print(f"Found {len(monitors)} monitors\n")

for monitor in monitors:
    if monitor.enabled:
        print(f"Running: {monitor.name}...")
        try:
            result = runner.run_monitor(monitor)
            storage.save_test_run(result)

            status_icon = "✅" if result.status == 'success' else "❌"
            print(f"{status_icon} {monitor.name}: {result.status} ({result.duration_ms}ms)")

            if result.error_message:
                print(f"   Error: {result.error_message}")
        except Exception as e:
            print(f"❌ {monitor.name}: Failed with exception: {str(e)}")
        print()

print("All monitors completed!")
print("Run 'streamlit run app.py' to view results in the dashboard.")
