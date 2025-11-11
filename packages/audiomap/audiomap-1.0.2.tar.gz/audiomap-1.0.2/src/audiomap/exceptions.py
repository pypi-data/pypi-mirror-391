"""
Custom exception classes
"""

class AudioDetectionError(Exception):
    """Error occurred during audio device detection"""
    pass

class PlatformNotSupportedError(AudioDetectionError):
    """Unsupported platform error"""
    pass

class DependencyMissingError(AudioDetectionError):
    """Missing dependency package error"""
    pass

class DeviceAccessError(AudioDetectionError):
    """Device access error"""
    pass
