
import argparse
import json
import sys
from src.automation.recorder import MonitorRecorder

def main():
    parser = argparse.ArgumentParser(description="Record test steps for PagerDuty Monitor")
    parser.add_argument("--url", required=True, help="URL to start recording from")
    parser.add_argument("--output", default="recorded_steps.json", help="Output JSON file for steps")
    
    args = parser.parse_args()
    
    recorder = MonitorRecorder()
    try:
        steps = recorder.start(args.url)
        
        with open(args.output, "w") as f:
            json.dump(steps, f, indent=2)
            
        print(f"\nRecording finished! Steps saved to {args.output}")
        print("You can copy these steps into the 'Add Monitor' page.")
        
    except KeyboardInterrupt:
        print("\nRecording cancelled.")
    except Exception as e:
        print(f"\nError during recording: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
