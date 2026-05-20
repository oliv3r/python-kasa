"""Modules for SMARTCAM devices."""

from .alarm import Alarm
from .audioconfig import AudioConfig
from .cameraalarm import CameraAlarm
from .daynightmode import DayNightMode
from .babycrydetection import BabyCryDetection
from .barkdetection import BarkDetection
from .battery import Battery
from .camera import Camera
from .childdevice import ChildDevice
from .childsetup import ChildSetup
from .device import DeviceModule
from .firmware import Firmware
from .glassdetection import GlassDetection
from .homekit import HomeKit
from .imageflip import ImageFlip
from .led import Led
from .lightfrequency import LightFrequency
from .lensmask import LensMask
from .linecrossingdetection import LineCrossingDetection
from .matter import Matter
from .meowdetection import MeowDetection
from .motiondetection import MotionDetection
from .nightboost import NightBoost
from .nightvision import NightVision
from .notifications import Notifications
from .osd import OSD
from .pantilt import PanTilt
from .persondetection import PersonDetection
from .recordingconfig import RecordingConfig
from .recordings import Recording, Recordings
from .petdetection import PetDetection
from .sdcard import SDCard
from .spotlight import Spotlight
from .tamperdetection import TamperDetection
from .time import Time
from .vehicledetection import VehicleDetection
from .videoquality import VideoQuality

__all__ = [
    "Alarm",
    "AudioConfig",
    "CameraAlarm",
    "DayNightMode",
    "BabyCryDetection",
    "BarkDetection",
    "Battery",
    "Camera",
    "ChildDevice",
    "ChildSetup",
    "DeviceModule",
    "Firmware",
    "GlassDetection",
    "HomeKit",
    "ImageFlip",
    "Led",
    "LightFrequency",
    "LensMask",
    "LineCrossingDetection",
    "Matter",
    "MeowDetection",
    "MotionDetection",
    "NightBoost",
    "NightVision",
    "Notifications",
    "OSD",
    "PanTilt",
    "PersonDetection",
    "RecordingConfig",
    "Recording",
    "Recordings",
    "PetDetection",
    "SDCard",
    "Spotlight",
    "TamperDetection",
    "Time",
    "VehicleDetection",
    "VideoQuality",
]
