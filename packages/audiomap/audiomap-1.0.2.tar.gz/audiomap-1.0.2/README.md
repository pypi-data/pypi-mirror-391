# AudioMap

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)](https://github.com/yourusername/audiomap)

Cross-platform audio device mapping library for macOS, Windows, and Linux with comprehensive device UID support for both input and output audio devices.

## Features

- 🔍 **Cross-platform**: Support for macOS, Windows, and Linux
- 🎤 **Input Device Detection**: Detect microphones, line inputs, and other audio input devices
- 🔊 **Output Device Detection**: Detect speakers, headphones, and other audio output devices
- 🆔 **Device UID Support**: Get unique device identifiers (UIDs) for precise device targeting
- 📝 **Unified API**: Same API interface across all platforms
- 🛠️ **Native Implementation**: 
  - macOS: Uses CoreAudio API with native UID support
  - Windows: Uses pycaw + comtypes with device ID extraction
  - Linux: Uses ALSA tools with device identifier mapping
- 🎯 **Lightweight**: Minimal dependencies, high performance
- 📱 **Command Line Tool**: Built-in CLI interface

## Installation

### Basic Installation

```bash
pip install audiomap
```

### Platform-specific Dependencies

**Windows:**
```bash
pip install audiomap[windows]
```

**Development:**
```bash
pip install audiomap[dev]
```

### Platform-specific Dependencies

**Windows users need additional packages:**
```bash
pip install audiomap[windows]
```

**Developer installation:**
```bash
pip install audiomap[dev]
```

## Quick Start

### Basic Usage

```python
from audiomap import list_audio_input_devices, list_audio_output_devices

# List all input devices
input_devices = list_audio_input_devices()
for device in input_devices:
    print(f"Input device: {device['name']} (UID: {device['id']})")

# List all output devices
output_devices = list_audio_output_devices()
for device in output_devices:
    print(f"Output device: {device['name']} (UID: {device['id']})")
```

### Using Class Interface

```python
from audiomap import AudioDeviceDetector

detector = AudioDeviceDetector()

# Get all devices with UIDs
all_devices = detector.list_all_devices()
print(f"Input devices: {len(all_devices['input'])}")
print(f"Output devices: {len(all_devices['output'])}")

# Display device information including UIDs
for device in all_devices['input']:
    print(f"Input: {device['name']} (UID: {device['id']})")
    
for device in all_devices['output']:
    print(f"Output: {device['name']} (UID: {device['id']})")

# Find specific devices by name
macbook_devices = detector.find_device_by_name("MacBook")
for device in macbook_devices:
    print(f"Found device: {device['name']} - UID: {device['id']}")

# Get device statistics
stats = detector.get_device_count()
print(f"Total: {stats['total']} audio devices")
```

### Command Line Usage

```bash
# List all devices with UIDs
audiomap

# List input devices only
audiomap --input-only

# List output devices only
audiomap --output-only

# JSON format output with UIDs
audiomap --json

# Find devices containing "MacBook"
audiomap --find "MacBook"

# Show device count only
audiomap --count-only
```

## API Documentation

### Utility Functions

#### `list_audio_input_devices()`
Returns a list of all audio input devices with their unique identifiers.

**Returns:**
- `List[Dict[str, str]]`: Device list, each device contains:
  - `id`: Device unique identifier (UID) - platform-specific format
  - `name`: Human-readable device name
  - `platform`: Platform name ("Windows", "Darwin", "Linux")

#### `list_audio_output_devices()`
Returns a list of all audio output devices with their unique identifiers.

**Returns:**
- `List[Dict[str, str]]`: Device list (same format as above)

### AudioDeviceDetector Class

#### `list_input_devices()`
List all audio input devices.

#### `list_output_devices()`
List all audio output devices.

#### `list_all_devices()`
List all audio devices.

**Returns:**
```python
{
    "input": List[Dict[str, str]],
    "output": List[Dict[str, str]]
}
```

#### `get_device_count()`
Get device count statistics.

**Returns:**
```python
{
    "input": int,    # Number of input devices
    "output": int,   # Number of output devices  
    "total": int     # Total number of devices
}
```

#### `find_device_by_name(name, device_type="both")`
Find devices by name.

**Parameters:**
- `name (str)`: Device name (supports partial matching)
- `device_type (str)`: Device type, options: "input", "output", "both"

## Platform Requirements

### macOS
- No additional dependencies (uses built-in CoreAudio)
- Supports all audio device types
- **UID Format**: CoreAudio device UID (e.g., "BuiltInSpeakers", "AppleUSBAudioEngine:...")

### Windows  
- Requires installation: `pip install pycaw comtypes`
- Supports WASAPI devices
- **UID Format**: Windows device ID (e.g., "{0.0.0.00000000}.{12345678-...}")

### Linux
- Requires ALSA tools: `sudo apt-get install alsa-utils`
- Supports ALSA and PulseAudio/PipeWire devices  
- **UID Format**: ALSA device name (e.g., "default", "hw:0,0", "pulse")

## Device UID Support

AudioMap provides comprehensive device UID support across all platforms:

### What are Device UIDs?
Device UIDs (Unique Identifiers) are platform-specific strings that uniquely identify audio devices. Unlike device names which can change or be duplicated, UIDs provide a reliable way to target specific audio hardware.

### Platform-Specific UID Implementation
- **macOS**: Uses CoreAudio's native device UID system
- **Windows**: Extracts Windows device IDs through WASAPI
- **Linux**: Uses ALSA device identifiers

### Using UIDs in Your Application
```python
devices = list_audio_input_devices()
for device in devices:
    uid = device['id']          # Platform-specific unique identifier
    name = device['name']       # Human-readable name
    platform = device['platform']  # Platform identifier
    
    print(f"Device: {name}")
    print(f"UID: {uid}")
    print(f"Platform: {platform}")
```

## Error Handling

```python
from audiomap import AudioDeviceDetector
from audiomap.exceptions import AudioDetectionError, DependencyMissingError

try:
    detector = AudioDeviceDetector()
    devices = detector.list_input_devices()
except DependencyMissingError as e:
    print(f"Missing dependency: {e}")
except AudioDetectionError as e:
    print(f"Detection error: {e}")
```

## Output Examples

### macOS Output Example
```
=== Audio Input Devices ===
Found 3 input devices:
  1. MacBook Pro Microphone (UID: BuiltInMicrophoneDevice)
  2. WH-1000XM6 (UID: 58-18-62-13-51-61:input)
  3. BlackHole 2ch (UID: BlackHole2ch_UID)

=== Audio Output Devices ===
Found 4 output devices:
  1. MacBook Pro Speakers (UID: BuiltInSpeakerDevice)
  2. WH-1000XM6 (UID: 58-18-62-13-51-61:output)
  3. BlackHole 2ch (UID: BlackHole2ch_UID)
  4. Multi-Output Device (UID: ~:AMS2_StackedOutput:0)
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/audiomap.git
cd audiomap
pip install -e .[dev]
```

### Run Tests

```bash
pytest tests/
```

### Build Package

```bash
python -m build
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Issues and Pull Requests are welcome!

## Changelog

### v1.0.0
- Initial release
- Support for macOS, Windows, and Linux
- Command line tool included
- Complete error handling
