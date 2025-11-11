"""
Command line interface
"""

import argparse
import json
import sys
from typing import Optional

from . import AudioDeviceDetector, list_audio_input_devices, list_audio_output_devices
from .exceptions import AudioDetectionError


def format_devices_text(devices, device_type):
    """Format device list as text output"""
    if not devices:
        return f"No {device_type} devices found"
    
    output = []
    output.append(f"Found {len(devices)} {device_type} device(s):")
    for i, device in enumerate(devices, 1):
        output.append(f"  {i}. {device['name']} (UID: {device['id']})")
    
    return "\n".join(output)


def format_devices_json(devices):
    """Format device list as JSON output"""
    return json.dumps(devices, ensure_ascii=False, indent=2)


def main():
    """Main command line function"""
    parser = argparse.ArgumentParser(
        description="AudioMap - Cross-platform audio device mapping tool with UID support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  audio-device-uid                    # List all devices with UIDs
  audio-device-uid --input-only       # List input devices only
  audio-device-uid --output-only      # List output devices only
  audio-device-uid --json             # JSON format output with UIDs
  audio-device-uid --find "MacBook"   # Find devices containing "MacBook"
        """
    )
    
    parser.add_argument(
        "--input-only", 
        action="store_true",
        help="List audio input devices only"
    )
    
    parser.add_argument(
        "--output-only",
        action="store_true", 
        help="List audio output devices only"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    parser.add_argument(
        "--find",
        type=str,
        help="Find devices by name (supports partial matching)"
    )
    
    parser.add_argument(
        "--count-only",
        action="store_true",
        help="Show device count statistics only"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="AudioMap 1.0.1"
    )
    
    args = parser.parse_args()
    
    try:
        detector = AudioDeviceDetector()
        
        if args.count_only:
            # Show count statistics only
            counts = detector.get_device_count()
            if args.json:
                print(json.dumps(counts, ensure_ascii=False, indent=2))
            else:
                print(f"Audio Device Statistics:")
                print(f"  Input devices: {counts['input']} devices")
                print(f"  Output devices: {counts['output']} devices")
                print(f"  Total: {counts['total']} devices")
            return
        
        if args.find:
            # Find specific devices
            devices = detector.find_device_by_name(args.find)
            if args.json:
                print(format_devices_json(devices))
            else:
                if devices:
                    print(f"Found devices containing '{args.find}':")
                    for i, device in enumerate(devices, 1):
                        device_type = device.get('type', 'unknown')
                        print(f"  {i}. {device['name']} ({device_type}) - UID: {device['id']}")
                else:
                    print(f"No devices found containing '{args.find}'")
            return
        
        # Determine which devices to list based on arguments
        if args.input_only:
            devices = {"input": detector.list_input_devices()}
        elif args.output_only:
            devices = {"output": detector.list_output_devices()}
        else:
            devices = {
                "input": detector.list_input_devices(),
                "output": detector.list_output_devices()
            }
        
        # Output results
        if args.json:
            print(format_devices_json(devices))
        else:
            print("Listing audio devices...")
            
            if "input" in devices:
                print(f"\n=== Audio Input Devices ===")
                print(format_devices_text(devices["input"], "Input"))
            
            if "output" in devices:
                print(f"\n=== Audio Output Devices ===")
                print(format_devices_text(devices["output"], "Output"))
            
            if "input" in devices and "output" in devices:
                total = len(devices["input"]) + len(devices["output"])
                print(f"\nTotal {total} audio devices found")
                print(f"Current platform: {detector.current_platform}")
    
    except AudioDetectionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
