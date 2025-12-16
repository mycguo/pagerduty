#!/bin/bash
# Initialize persistent data directory with default monitors if empty

DATA_DIR="/app/data"
DEFAULT_MONITORS="/app/default_monitors.json"
TARGET_MONITORS="$DATA_DIR/monitors.json"
INIT_MARKER="$DATA_DIR/.init_marker"

echo "========================================="
echo "Data Directory Initialization"
echo "========================================="
echo "Timestamp: $(date)"
echo "Data directory: $DATA_DIR"
echo "Default monitors: $DEFAULT_MONITORS"
echo "Target file: $TARGET_MONITORS"

# Create data directory if it doesn't exist
mkdir -p "$DATA_DIR"
echo "Created/verified data directory: $DATA_DIR"

# Check if this is a persistent disk by looking for mount point
echo ""
echo "Checking if $DATA_DIR is a mounted volume:"
if mount | grep -q "$DATA_DIR"; then
    echo "✓ $DATA_DIR is a MOUNTED VOLUME (persistent disk)"
    mount | grep "$DATA_DIR"
else
    echo "⚠ WARNING: $DATA_DIR is NOT a mounted volume!"
    echo "   This means data will NOT persist across deployments/restarts!"
    echo "   (This is expected on Render free tier - persistent disks require paid plan)"
fi

# Check for init marker to see if this disk has been initialized before
if [ -f "$INIT_MARKER" ]; then
    echo ""
    echo "Init marker found - this disk was previously initialized:"
    cat "$INIT_MARKER"
else
    echo ""
    echo "No init marker found - first time initializing this disk"
fi

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

# Create/update init marker with timestamp
echo "$(date): Initialization completed" >> "$INIT_MARKER"
echo ""
echo "Updated init marker file"

# List data directory contents
echo ""
echo "Data directory contents:"
ls -lha "$DATA_DIR/"

# Show last few lines of init marker to see history
if [ -f "$INIT_MARKER" ]; then
    echo ""
    echo "Initialization history (last 5 entries):"
    tail -5 "$INIT_MARKER"
fi

echo ""
echo "========================================="
echo "Initialization Complete"
echo "========================================="
