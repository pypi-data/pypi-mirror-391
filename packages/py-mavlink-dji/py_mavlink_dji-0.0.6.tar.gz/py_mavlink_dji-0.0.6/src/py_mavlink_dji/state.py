"""
Thread-safe shared state for DJI variables.
"""
import threading
from typing import Dict


class SharedState:
    def __init__(self):
        self._lock = threading.RLock()
        # attitude quaternion
        self.attitude: Dict[str, float] = {"q0": 1.0, "q1": 0.0, "q2": 0.0, "q3": 0.0}
        # angular rates
        self.angular: Dict[str, float] = {"wx": 0.0, "wy": 0.0, "wz": 0.0}
        # position in degrees/meters
        self.position: Dict[str, float] = {"lat": 0.0, "lon": 0.0, "alt": 0.0}
        self.velocity: Dict[str, float] = {"vx": 0.0, "vy": 0.0, "vz": 0.0}
        # rc channels
        self.rc: Dict[str, int] = {"pitch": 0, "roll": 0, "yaw": 0, "throttle": 0}
        self.battery: float = 0.0

    def snapshot(self):
        with self._lock:
            return {
                "attitude": dict(self.attitude),
                "angular": dict(self.angular),
                "position": dict(self.position),
                "velocity": dict(self.velocity),
                "rc": dict(self.rc),
                "battery": float(self.battery),
            }

    def update_attitude(self, q0, q1, q2, q3):
        with self._lock:
            self.attitude.update({"q0": q0, "q1": q1, "q2": q2, "q3": q3})

    def update_position(self, lat, lon, alt):
        with self._lock:
            self.position.update({"lat": lat, "lon": lon, "alt": alt})

    def update_velocity(self, vx, vy, vz):
        with self._lock:
            self.velocity.update({"vx": vx, "vy": vy, "vz": vz})

    def update_rc(self, **channels):
        with self._lock:
            self.rc.update(channels)

    def set_battery(self, level):
        with self._lock:
            self.battery = float(level)


