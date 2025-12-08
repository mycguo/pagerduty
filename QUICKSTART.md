# Quick Start Guide

## Setup (Already Completed!)

The application is ready to use. Here's what's been set up:

1. ✅ Virtual environment created (`.venv/`)
2. ✅ Dependencies installed
3. ✅ Playwright browser installed
4. ✅ Sample monitors created
5. ✅ Test data populated

## Running the Application

### Start the Streamlit app:

```bash
source .venv/bin/activate
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## What You'll See

### 📊 Dashboard
- Overview of all monitors
- Success/failure metrics
- Recent test runs with charts
- Response time trends

### ⚙️ Monitors
- **All Monitors Tab**: View, run, enable/disable, or delete monitors
- **Add/Edit Monitor Tab**: Create new monitors using JSON configuration

### 📋 Test Results
- Detailed logs of all test runs
- Step-by-step execution results
- Screenshots of failures
- Error messages and debugging info

## Sample Monitors Included

The following monitors are already configured:

1. **Test Example.com** - Basic navigation test
2. **Wikipedia Health Check** - Search functionality test
3. **GitHub Homepage Check** - Element visibility check (this one may fail - that's expected!)
4. **Example.com Basic Test** - Text verification test

## Running Monitors

### From the UI:
1. Go to "Monitors" page
2. Expand a monitor
3. Click "▶️ Run" button

### From Command Line:
```bash
# Run all monitors
source .venv/bin/activate
python run_all_monitors.py
```

## Creating Your Own Monitor

### Method 1: Use the UI
1. Go to "Monitors" page → "Add/Edit Monitor" tab
2. Fill in the name and URL
3. Edit the JSON steps configuration
4. Click "Save Monitor"

### Method 2: Create a Script
```python
from src.monitoring.monitor import Monitor
from src.storage.storage import Storage

storage = Storage()

monitor = Monitor(
    name="My Custom Monitor",
    url="https://yourapp.com",
    steps=[
        {
            "type": "navigate",
            "url": "https://yourapp.com/login"
        },
        {
            "type": "fill",
            "selector": "#username",
            "value": "your-username"
        },
        {
            "type": "fill",
            "selector": "#password",
            "value": "${PASSWORD}"  # Use env variable
        },
        {
            "type": "click",
            "selector": "button[type='submit']"
        },
        {
            "type": "verify",
            "condition": "url_contains",
            "expected": "/dashboard"
        }
    ]
)

storage.save_monitor(monitor)
print(f"Monitor '{monitor.name}' created!")
```

## Environment Variables

For sensitive data (passwords, API keys), use environment variables:

1. Copy `.env.example` to `.env`
2. Add your variables:
```bash
TEST_USERNAME=user@example.com
TEST_PASSWORD=your_secure_password
API_KEY=your_api_key
```

3. Reference in monitors with `${VARIABLE_NAME}`:
```json
{
  "type": "fill",
  "selector": "#password",
  "value": "${TEST_PASSWORD}"
}
```

## Common Actions

### Navigate to URL
```json
{
  "type": "navigate",
  "url": "https://example.com"
}
```

### Click Element
```json
{
  "type": "click",
  "selector": "#submit-button"
}
```

### Fill Input
```json
{
  "type": "fill",
  "selector": "#email",
  "value": "user@example.com"
}
```

### Verify Condition
```json
{
  "type": "verify",
  "condition": "element_exists",
  "selector": ".success-message"
}
```

Available conditions:
- `url_contains` - Check if URL contains text
- `url_equals` - Check if URL equals text
- `element_exists` - Check if element exists
- `element_visible` - Check if element is visible
- `text_contains` - Check if element text contains value
- `text_equals` - Check if element text equals value

### Wait
```json
{
  "type": "wait",
  "wait_type": "time",
  "duration": 2000
}
```

## Tips

1. **Finding Selectors**: Use browser DevTools (F12) to inspect elements and get CSS selectors
2. **Debug Mode**: Set `headless=False` in runner code to see the browser in action
3. **Screenshots**: Automatically captured on failures in `screenshots/` directory
4. **Test First**: Always test your monitor configuration before relying on it

## Troubleshooting

**Can't find element:**
- Verify your CSS selector using browser DevTools
- Add a wait step before interacting with dynamic elements

**Module not found:**
- Make sure virtual environment is activated: `source .venv/bin/activate`

**Playwright errors:**
- Reinstall browser: `playwright install chromium`

## Next Steps

1. Create monitors for your own applications
2. Customize step configurations for your use cases
3. Check the README.md for more advanced features
4. Consider implementing Phase 3 & 4 (scheduling and alerts)

## Need Help?

Check the full documentation in `README.md` for:
- Complete step type reference
- Advanced configurations
- Project structure
- Future enhancements
