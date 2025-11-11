"""
Utility functions providing simple API interface
"""

from .detector import AudioDeviceDetector
from .exceptions import AudioDetectionError

# Global detector instance
_detector = AudioDeviceDetector()

def list_audio_input_devices():
    """List all audio input devices
    
    Returns:
        List[Dict[str, str]]: Device list, each device contains id, name, platform keys
    
    Raises:
        AudioDetectionError: When device detection fails
    """
    return _detector.list_input_devices()

def list_audio_output_devices():
    """List all audio output devices
    
    Returns:
        List[Dict[str, str]]: Device list, each device contains id, name, platform keys
    
    Raises:
        AudioDetectionError: When device detection fails
    """
    return _detector.list_output_devices()

def get_audio_device_count():
    """Get audio device count statistics
    
    Returns:
        Dict[str, int]: Dictionary containing input, output, total keys
    """
    return _detector.get_device_count()

def find_audio_device(name, device_type="both"):
    """Find audio devices by name
    
    Args:
        name (str): Device name (supports partial matching)
        device_type (str): Device type, options: "input", "output", "both"
    
    Returns:
        List[Dict[str, str]]: List of matching devices
    """
    return _detector.find_device_by_name(name, device_type)
