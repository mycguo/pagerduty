#!/bin/bash
# Initialize persistent data directory with default monitors if empty

DATA_DIR="/app/data"
DEFAULT_MONITORS="/app/default_monitors.json"
TARGET_MONITORS="$DATA_DIR/monitors.json"

echo "========================================="
echo "Data Directory Initialization"
echo "========================================="
echo "Data directory: $DATA_DIR"
echo "Default monitors: $DEFAULT_MONITORS"
echo "Target file: $TARGET_MONITORS"

# Create data directory if it doesn't exist
mkdir -p "$DATA_DIR"
echo "Created/verified data directory: $DATA_DIR"

# Check if monitors.json exists in persistent volume
if [ ! -f "$TARGET_MONITORS" ]; then
    echo ""
    echo "No monitors.json found in persistent storage."

    if [ -f "$DEFAULT_MONITORS" ]; then
        echo "Copying default monitors.json to persistent storage..."
        cp "$DEFAULT_MONITORS" "$TARGET_MONITORS"

        # Verify the copy
        if [ -f "$TARGET_MONITORS" ]; then
            echo "✓ Default monitors copied successfully!"
            echo "  File size: $(stat -c%s "$TARGET_MONITORS" 2>/dev/null || stat -f%z "$TARGET_MONITORS" 2>/dev/null) bytes"
        else
            echo "✗ ERROR: Failed to copy default monitors!"
            exit 1
        fi
    else
        echo "No default monitors found at $DEFAULT_MONITORS"
        echo "Creating empty monitors file..."
        echo "[]" > "$TARGET_MONITORS"
    fi
else
    echo "✓ monitors.json already exists in persistent storage."
    echo "  File size: $(stat -c%s "$TARGET_MONITORS" 2>/dev/null || stat -f%z "$TARGET_MONITORS" 2>/dev/null) bytes"
fi

# List data directory contents
echo ""
echo "Data directory contents:"
ls -lh "$DATA_DIR/"

echo ""
echo "========================================="
echo "Initialization Complete"
echo "========================================="
