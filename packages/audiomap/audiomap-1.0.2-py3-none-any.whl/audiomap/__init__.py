"""
AudioMap - Cross-platform Audio Device Mapping Library with UID Support

Comprehensive audio input and output device mapping for macOS, Windows, and Linux platforms.
Features native device UID extraction for precise device targeting and identification.

Key Features:
- Cross-platform audio device mapping
- Native device UID support on all platforms
- Unified API interface
- Minimal dependencies with high performance
"""

from .detector import AudioDeviceDetector
from .exceptions import AudioDetectionError
from .utils import (
    list_audio_input_devices, 
    list_audio_output_devices,
    get_audio_device_count,
    find_audio_device
)

__version__ = "1.0.0"
__author__ = "Andy Lee"
__description__ = "Cross-platform audio device detection library"

__all__ = [
    "AudioDeviceDetector",
    "AudioDetectionError", 
    "list_audio_input_devices",
    "list_audio_output_devices",
    "get_audio_device_count",
    "find_audio_device"
]
