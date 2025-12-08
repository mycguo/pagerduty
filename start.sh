#!/bin/bash
# Quick start script for the web monitoring app

echo "🔍 Starting Web Monitoring Dashboard..."
echo ""

# Activate virtual environment
source .venv/bin/activate

# Check if playwright is installed
if ! python -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
    echo "⚠️  Playwright browser not installed. Installing now..."
    playwright install chromium
fi

echo "✅ Environment ready!"
echo ""
echo "📊 Starting Streamlit app..."
echo "   The app will open in your browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start streamlit
streamlit run app.py
