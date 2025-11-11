"""
Audio device detector core class
"""

import platform
import subprocess
from typing import List, Dict, Optional

from .exceptions import (
    AudioDetectionError, 
    PlatformNotSupportedError, 
    DependencyMissingError, 
    DeviceAccessError
)


class AudioDeviceDetector:
    """Cross-platform audio device detector"""
    
    def __init__(self):
        self.current_platform = platform.system()
        
    def list_input_devices(self) -> List[Dict[str, str]]:
        """List all audio input devices"""
        return self._list_devices("input")
    
    def list_output_devices(self) -> List[Dict[str, str]]:
        """List all audio output devices"""
        return self._list_devices("output")
    
    def list_all_devices(self) -> Dict[str, List[Dict[str, str]]]:
        """List all audio devices (input and output)"""
        return {
            "input": self.list_input_devices(),
            "output": self.list_output_devices()
        }
    
    def get_device_count(self) -> Dict[str, int]:
        """Get device count statistics"""
        devices = self.list_all_devices()
        return {
            "input": len(devices["input"]),
            "output": len(devices["output"]),
            "total": len(devices["input"]) + len(devices["output"])
        }
    
    def find_device_by_name(self, name: str, device_type: str = "both") -> List[Dict[str, str]]:
        """Find devices by name"""
        results = []
        
        if device_type in ["input", "both"]:
            for device in self.list_input_devices():
                if name.lower() in device["name"].lower():
                    device["type"] = "input"
                    results.append(device)
        
        if device_type in ["output", "both"]:
            for device in self.list_output_devices():
                if name.lower() in device["name"].lower():
                    device["type"] = "output"
                    results.append(device)
        
        return results
    
    def _list_devices(self, device_type: str) -> List[Dict[str, str]]:
        """Internal method: list devices of specified type"""
        if device_type not in ["input", "output"]:
            raise ValueError("device_type must be 'input' or 'output'")
        
        try:
            if self.current_platform == "Windows":
                return self._detect_windows_devices(device_type)
            elif self.current_platform == "Darwin":
                return self._detect_macos_devices(device_type)
            elif self.current_platform == "Linux":
                return self._detect_linux_devices(device_type)
            else:
                raise PlatformNotSupportedError(f"Unsupported platform: {self.current_platform}")
        
        except Exception as e:
            if isinstance(e, AudioDetectionError):
                raise
            else:
                raise AudioDetectionError(f"Device detection failed: {str(e)}")
    
    def _detect_windows_devices(self, device_type: str) -> List[Dict[str, str]]:
        """Windows platform device detection"""
        devices = []
        
        try:
            import comtypes
            from pycaw.pycaw import AudioUtilities, IMMDeviceEnumerator, EDataFlow, DEVICE_STATE
            from pycaw.constants import CLSID_MMDeviceEnumerator
        except ImportError as e:
            raise DependencyMissingError("Windows platform requires pycaw and comtypes: pip install pycaw comtypes")
        
        try:
            def get_audio_devices(direction="in", state=DEVICE_STATE.ACTIVE.value):
                audio_devices = []
                
                try:
                    # Method 1: Use advanced enumerator
                    if direction == "in":
                        flow = EDataFlow.eCapture.value     # 1
                    else:
                        flow = EDataFlow.eRender.value      # 0
                    
                    device_enumerator = comtypes.CoCreateInstance(
                        CLSID_MMDeviceEnumerator,
                        IMMDeviceEnumerator,
                        comtypes.CLSCTX_INPROC_SERVER)
                    
                    if device_enumerator is not None:
                        collection = device_enumerator.EnumAudioEndpoints(flow, state)
                        if collection is not None:
                            count = collection.GetCount()
                            for i in range(count):
                                dev = collection.Item(i)
                                if dev is not None:
                                    try:
                                        audio_device = AudioUtilities.CreateDevice(dev)
                                        if audio_device:
                                            audio_devices.append(audio_device)
                                    except Exception:
                                        continue
                
                except Exception:
                    # Method 1 failed, try Method 2
                    pass
                
                # Method 2: Use basic method as fallback
                if not audio_devices:
                    try:
                        all_devices = AudioUtilities.GetAllDevices()
                        for device in all_devices:
                            try:
                                # Simple check if device is valid
                                device_str = str(device)
                                if device_str and ": None" not in device_str:
                                    audio_devices.append(device)
                            except Exception:
                                continue
                    except Exception:
                        pass
                
                return audio_devices

            # Get devices and process them
            if device_type == "input":
                target_devices = get_audio_devices("in")
            else:
                target_devices = get_audio_devices("out")
            
            for i, device in enumerate(target_devices):
                try:
                    device_name = getattr(device, 'FriendlyName', f'Device_{i+1}')
                    device_id = getattr(device, 'id', f"device_{id(device)}")
                    
                    # If device name is empty, use string representation
                    if not device_name or device_name.strip() == "":
                        device_name = str(device) if str(device) != str(type(device)) else f'Audio_Device_{i+1}'
                    
                    devices.append({
                        "id": device_id,
                        "name": device_name,
                        "platform": "Windows"
                    })
                except Exception as e:
                    # Still try to add device with basic info
                    try:
                        devices.append({
                            "id": f"unknown_device_{i+1}",
                            "name": f"Unknown_Audio_Device_{i+1}",
                            "platform": "Windows"
                        })
                    except:
                        continue
                
        except Exception as e:
            raise DeviceAccessError(f"Windows audio device access failed: {str(e)}")
        
        return devices
    
    def _detect_macos_devices(self, device_type: str) -> List[Dict[str, str]]:
        """macOS platform device detection"""
        devices = []
        
        try:
            import ctypes
            from ctypes import c_uint32, c_void_p, Structure, POINTER, byref, c_char_p, c_uint8
        except ImportError as e:
            raise DependencyMissingError("macOS platform requires ctypes (usually built-in)")
        
        try:
            # Load CoreAudio framework
            core_audio = ctypes.CDLL('/System/Library/Frameworks/CoreAudio.framework/CoreAudio')
            core_foundation = ctypes.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
            
            # Define AudioObjectPropertyAddress structure
            class AudioObjectPropertyAddress(Structure):
                _fields_ = [
                    ('mSelector', c_uint32),
                    ('mScope', c_uint32),
                    ('mElement', c_uint32)
                ]
            
            # Define AudioBufferList structure
            class AudioBuffer(Structure):
                _fields_ = [
                    ('mNumberChannels', c_uint32),
                    ('mDataByteSize', c_uint32),
                    ('mData', c_void_p)
                ]
            
            class AudioBufferList(Structure):
                _fields_ = [
                    ('mNumberBuffers', c_uint32),
                    ('mBuffers', AudioBuffer * 1)  # Actually a variable-length array
                ]
            
            # CoreAudio constants - corrected version
            kAudioObjectSystemObject = 1
            kAudioHardwarePropertyDevices = 1684370979  # 'dev#'
            kAudioObjectPropertyScopeGlobal = 1735159650  # 'glob'
            kAudioObjectPropertyElementMain = 0
            kAudioDevicePropertyStreamConfiguration = 1936482681  # 'slay'
            kAudioDevicePropertyScopeInput = 1768845428  # 'inpt'
            kAudioDevicePropertyScopeOutput = 1869968496  # 'outp'
            kAudioDevicePropertyDeviceUID = 1969841184  # 'uid '
            kAudioDevicePropertyDeviceNameCFString = 1819173229  # 'lnam'
            kAudioHardwareNoError = 0
            kCFStringEncodingUTF8 = 0x08000100
            
            # Set function prototypes
            AudioObjectGetPropertyDataSize = core_audio.AudioObjectGetPropertyDataSize
            AudioObjectGetPropertyDataSize.argtypes = [c_uint32, POINTER(AudioObjectPropertyAddress), c_uint32, c_void_p, POINTER(c_uint32)]
            AudioObjectGetPropertyDataSize.restype = c_uint32
            
            AudioObjectGetPropertyData = core_audio.AudioObjectGetPropertyData
            AudioObjectGetPropertyData.argtypes = [c_uint32, POINTER(AudioObjectPropertyAddress), c_uint32, c_void_p, POINTER(c_uint32), c_void_p]
            AudioObjectGetPropertyData.restype = c_uint32
            
            # CFStringGetCString for string conversion
            CFStringGetCString = core_foundation.CFStringGetCString
            CFStringGetCString.argtypes = [c_void_p, c_char_p, c_uint32, c_uint32]
            CFStringGetCString.restype = c_uint8
            
            # CFRelease for releasing CoreFoundation objects
            CFRelease = core_foundation.CFRelease
            CFRelease.argtypes = [c_void_p]
            CFRelease.restype = None
            
            # Set property address to get all devices
            propertyAddress = AudioObjectPropertyAddress()
            propertyAddress.mSelector = kAudioHardwarePropertyDevices
            propertyAddress.mScope = kAudioObjectPropertyScopeGlobal
            propertyAddress.mElement = kAudioObjectPropertyElementMain
            
            # Get device list size
            dataSize = c_uint32(0)
            status = AudioObjectGetPropertyDataSize(
                kAudioObjectSystemObject,
                byref(propertyAddress),
                0,
                None,
                byref(dataSize)
            )
            
            if status != kAudioHardwareNoError:
                raise RuntimeError(f"AudioObjectGetPropertyDataSize failed: {status}")
            
            # Calculate device count and allocate memory
            deviceCount = dataSize.value // 4  # AudioDeviceID is 4 bytes
            AudioDeviceIDArray = c_uint32 * deviceCount
            audioDevices = AudioDeviceIDArray()
            
            # Get device list
            status = AudioObjectGetPropertyData(
                kAudioObjectSystemObject,
                byref(propertyAddress),
                0,
                None,
                byref(dataSize),
                audioDevices
            )
            
            if status != kAudioHardwareNoError:
                raise RuntimeError(f"AudioObjectGetPropertyData failed: {status}")
            
            # Iterate through all devices to find specified type devices
            for i in range(deviceCount):
                deviceID = audioDevices[i]
                
                # Check if this is a device of the specified type (check stream configuration)
                propertyAddress.mSelector = kAudioDevicePropertyStreamConfiguration
                if device_type == "input":
                    propertyAddress.mScope = kAudioDevicePropertyScopeInput
                else:
                    propertyAddress.mScope = kAudioDevicePropertyScopeOutput
                
                streamDataSize = c_uint32(0)
                status = AudioObjectGetPropertyDataSize(
                    deviceID,
                    byref(propertyAddress),
                    0,
                    None,
                    byref(streamDataSize)
                )
                
                if status != kAudioHardwareNoError:
                    continue
                
                # Allocate buffer and get stream configuration
                buffer = ctypes.create_string_buffer(streamDataSize.value)
                status = AudioObjectGetPropertyData(
                    deviceID,
                    byref(propertyAddress),
                    0,
                    None,
                    byref(streamDataSize),
                    buffer
                )
                
                if status != kAudioHardwareNoError:
                    continue
                
                # Check if there are input channels
                bufferList = ctypes.cast(buffer, POINTER(AudioBufferList)).contents
                if bufferList.mNumberBuffers == 0:
                    continue
                
                # Get device UID
                propertyAddress.mSelector = kAudioDevicePropertyDeviceUID
                if device_type == "input":
                    propertyAddress.mScope = kAudioDevicePropertyScopeInput
                else:
                    propertyAddress.mScope = kAudioDevicePropertyScopeOutput
                
                uidDataSize = c_uint32(8)  # CFStringRef size
                deviceUID = c_void_p()
                
                status = AudioObjectGetPropertyData(
                    deviceID,
                    byref(propertyAddress),
                    0,
                    None,
                    byref(uidDataSize),
                    byref(deviceUID)
                )
                
                uid_str = f"device_{deviceID}"
                if status == kAudioHardwareNoError and deviceUID.value:
                    try:
                        # Convert CFString to C string
                        uidBuffer = ctypes.create_string_buffer(256)
                        if CFStringGetCString(deviceUID.value, uidBuffer, 256, kCFStringEncodingUTF8):
                            uid_str = uidBuffer.value.decode('utf-8')
                        # Release CFString
                        CFRelease(deviceUID.value)
                    except Exception as e:
                        print(f"UID conversion error: {e}")
                
                # Get device name
                propertyAddress.mSelector = kAudioDevicePropertyDeviceNameCFString
                
                nameDataSize = c_uint32(8)
                deviceName = c_void_p()
                
                status = AudioObjectGetPropertyData(
                    deviceID,
                    byref(propertyAddress),
                    0,
                    None,
                    byref(nameDataSize),
                    byref(deviceName)
                )
                
                name_str = f"Audio Device {deviceID}"
                if status == kAudioHardwareNoError and deviceName.value:
                    try:
                        nameBuffer = ctypes.create_string_buffer(256)
                        if CFStringGetCString(deviceName.value, nameBuffer, 256, kCFStringEncodingUTF8):
                            name_str = nameBuffer.value.decode('utf-8')
                        # Release CFString
                        CFRelease(deviceName.value)
                    except Exception as e:
                        print(f"Name conversion error: {e}")
                
                devices.append({
                    "id": uid_str,
                    "name": name_str,
                    "platform": "Darwin",
                    "device_id": deviceID
                })
                        
        except Exception as e:
            raise DeviceAccessError(f"CoreAudio API detection failed: {str(e)}")
        
        return devices
    
    def _detect_linux_devices(self, device_type: str) -> List[Dict[str, str]]:
        """Linux platform device detection"""
        devices = []
        
        try:
            if device_type == "input":
                command = ["arecord", "-L"]
            else:
                command = ["aplay", "-L"]
                
            output = subprocess.check_output(command, text=True)
            lines = output.splitlines()
            
            current_device = None
            current_description = None
            
            for line in lines:
                # Device ID line (doesn't start with space)
                if line and not line.startswith(' ') and not line.startswith('\t'):
                    # If there's a previous device, add it first
                    if current_device is not None:
                        # Filter out unwanted devices
                        if not current_device.startswith("null") and not current_device.startswith("sys"):
                            device_name = current_description if current_description else current_device
                            devices.append({
                                "id": current_device,
                                "name": device_name,
                                "platform": "Linux"
                            })
                    
                    # Start new device
                    current_device = line.strip()
                    current_description = None
                
                # Device description line (starts with space)
                elif line.strip() and (line.startswith(' ') or line.startswith('\t')):
                    description = line.strip()
                    # Only take the first line of description as device name
                    if current_description is None:
                        current_description = description
            
            # Process the last device
            if current_device is not None:
                if not current_device.startswith("null") and not current_device.startswith("sys"):
                    device_name = current_description if current_description else current_device
                    devices.append({
                        "id": current_device,
                        "name": device_name,
                        "platform": "Linux"
                    })
                    
        except subprocess.CalledProcessError:
            # If command failed, add an error device
            command_name = "arecord" if device_type == "input" else "aplay"
            raise DependencyMissingError(f"Linux platform requires alsa-utils installation, {command_name} command failed")
        except Exception as e:
            raise DeviceAccessError(f"Linux audio device detection failed: {str(e)}")
        
        return devices
