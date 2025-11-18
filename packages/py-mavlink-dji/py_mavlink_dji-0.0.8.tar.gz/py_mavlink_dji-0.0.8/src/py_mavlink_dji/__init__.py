"""py_mavlink_dji: MAVLink <-> DJI translator package (prototype)

Expose a simple Bridge class that listens for MAVLink messages and invokes
methods on a HardwareBackend implementation (can be a mock for tests).
"""
from .adapter import Bridge
from .backend import HardwareBackend, MockBackend
from .camera import CameraController

__all__ = ["Bridge", "HardwareBackend", "MockBackend", "CameraController"]


