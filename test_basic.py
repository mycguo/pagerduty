"""Basic test to verify the monitoring system works."""
import sys
from src.monitoring.monitor import Monitor
from src.monitoring.runner import MonitorRunner
from src.storage.storage import Storage

# Create a simple monitor
monitor = Monitor(
    name="Test Example.com",
    url="https://example.com",
    steps=[
        {
            "type": "navigate",
            "url": "https://example.com"
        },
        {
            "type": "verify",
            "condition": "element_exists",
            "selector": "h1"
        }
    ]
)

print(f"Created monitor: {monitor.name}")
print(f"Monitor ID: {monitor.id}")

# Run the monitor
print("\nRunning monitor...")
runner = MonitorRunner(headless=True)

try:
    result = runner.run_monitor(monitor)

    print(f"\nTest Result: {result.status}")
    print(f"Duration: {result.duration_ms}ms")

    if result.error_message:
        print(f"Error: {result.error_message}")

    print("\nStep Results:")
    for step_result in result.step_results:
        step_idx = step_result['step_index']
        status = step_result['status']
        duration = step_result['duration_ms']
        print(f"  Step {step_idx + 1}: {status} ({duration}ms)")
        if step_result.get('error_message'):
            print(f"    Error: {step_result['error_message']}")

    # Save to storage
    storage = Storage()
    storage.save_monitor(monitor)
    storage.save_test_run(result)
    print("\nMonitor and test result saved to storage!")

    sys.exit(0 if result.status == 'success' else 1)

except Exception as e:
    print(f"\nTest failed with exception: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
