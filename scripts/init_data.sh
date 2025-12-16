#!/bin/bash
# Initialize persistent data directory with default monitors if empty

DATA_DIR="/app/data"
DEFAULT_MONITORS="/app/default_data/monitors.json"
TARGET_MONITORS="$DATA_DIR/monitors.json"

echo "Checking data directory initialization..."

# Create data directory if it doesn't exist
mkdir -p "$DATA_DIR"

# If monitors.json doesn't exist in the persistent volume, copy from defaults
if [ ! -f "$TARGET_MONITORS" ]; then
    echo "No monitors.json found in persistent storage."
    if [ -f "$DEFAULT_MONITORS" ]; then
        echo "Copying default monitors.json to persistent storage..."
        cp "$DEFAULT_MONITORS" "$TARGET_MONITORS"
        echo "Default monitors copied successfully."
    else
        echo "No default monitors found, creating empty monitors file..."
        echo "[]" > "$TARGET_MONITORS"
    fi
else
    echo "monitors.json already exists in persistent storage."
fi

echo "Data directory initialization complete."
