"""Update existing monitors to include new alert fields."""
from src.storage.storage import Storage

storage = Storage()
monitors = storage.get_monitors()

print(f"Updating {len(monitors)} monitors...")

for monitor in monitors:
    # The Monitor.from_dict will automatically add default values for missing fields
    # Just re-save each monitor
    storage.save_monitor(monitor)
    print(f"✅ Updated: {monitor.name}")

print("\nAll monitors updated successfully!")
print("They now have default alert configuration:")
print("  - Alerts enabled: True")
print("  - Email addresses: [] (empty)")
print("  - Slack webhook: None")
