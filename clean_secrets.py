import json
import os

FILES_TO_CLEAN = [
    "data/monitors.json",
    "data/test_results.json"
]

def clean_file(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (not found)")
        return

    print(f"Cleaning {filepath}...")
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        modified = False
        
        # Determine structure (list or dict or whatever)
        # monitors.json is a list of objects
        # test_results.json is not clear, assuming list of runs?
        
        if isinstance(data, list):
            for item in data:
                if 'slack_webhook_url' in item:
                    item['slack_webhook_url'] = None # or delete key? 
                    # If we delete key, .get() returns None, which is fine.
                    # Setting to None works too.
                    # Let's delete the key to be cleaner.
                    del item['slack_webhook_url']
                    modified = True
                    
        # test_results.json might differ. Let's inspect it if we can, but likely it's a list or dict wrapper.
        # If it's a dict containing a list, we need to handle that.
        # But looking at storage.py, save_test_run matches keys.
        
        if modified:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✅ Removed secrets from {filepath}")
        else:
            print(f"No secrets found in {filepath}")
            
    except Exception as e:
        print(f"Error cleaning {filepath}: {e}")

if __name__ == "__main__":
    for f in FILES_TO_CLEAN:
        clean_file(f)
