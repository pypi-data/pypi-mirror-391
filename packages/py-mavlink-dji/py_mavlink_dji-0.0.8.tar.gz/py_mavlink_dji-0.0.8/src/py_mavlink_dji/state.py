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
        # linear acceleration (m/s^2)
        self.acceleration: Dict[str, float] = {"ax": 0.0, "ay": 0.0, "az": 0.0}
        # position in degrees/meters
        self.position: Dict[str, float] = {"lat": 0.0, "lon": 0.0, "alt": 0.0}
        self.velocity: Dict[str, float] = {"vx": 0.0, "vy": 0.0, "vz": 0.0}
        # rc channels
        self.rc: Dict[str, int] = {"pitch": 0, "roll": 0, "yaw": 0, "throttle": 0}
        self.battery: float = 100.0
        self.flight: Dict[str, float] = {
            "ctrl_device": "unknown",
            "ctrl_device_id": 0,
            "flight_status": 0,
            "display_mode": 0,
        }
        self.control: Dict[str, float] = {
            "has_authority": False,
            "last_request": None,
            "last_success": False,
        }
        self.sdk: Dict[str, bool] = {"activated": False, "opened": False}

    def snapshot(self):
        with self._lock:
            return {
                "attitude": dict(self.attitude),
                "angular": dict(self.angular),
                "acceleration": dict(self.acceleration),
                "position": dict(self.position),
                "velocity": dict(self.velocity),
                "rc": dict(self.rc),
                "battery": float(self.battery),
                "flight": dict(self.flight),
                "control": dict(self.control),
                "sdk": dict(self.sdk),
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

    def update_angular(self, wx, wy, wz):
        with self._lock:
            self.angular.update({"wx": wx, "wy": wy, "wz": wz})

    def update_acceleration(self, ax, ay, az):
        with self._lock:
            self.acceleration.update({"ax": ax, "ay": ay, "az": az})

    def update_rc(self, **channels):
        with self._lock:
            self.rc.update(channels)

    def set_battery(self, level):
        with self._lock:
            self.battery = float(level)

    def set_ctrl_device(self, device):
        with self._lock:
            label = "unknown"
            device_id = self.flight.get("ctrl_device_id", 0)
            if isinstance(device, dict):
                label = device.get("label") or device.get("name") or device.get("device") or label
                try:
                    device_id = int(device.get("id", device.get("value", device_id)))
                except Exception:
                    pass
            elif isinstance(device, (int, float)):
                device_id = int(device)
                label = {0: "rc", 1: "mobile", 2: "onboard"}.get(device_id, str(int(device_id)))
            elif device is not None:
                label = str(device)
            self.flight.update({"ctrl_device": str(label), "ctrl_device_id": int(device_id)})

    def set_flight_status(self, status):
        with self._lock:
            try:
                self.flight["flight_status"] = int(status)
            except Exception:
                self.flight["flight_status"] = 0

    def set_display_mode(self, mode):
        with self._lock:
            try:
                self.flight["display_mode"] = int(mode)
            except Exception:
                self.flight["display_mode"] = 0

    def set_control_authority(self, has_authority: bool, requested: bool, success: bool):
        with self._lock:
            self.control.update(
                {
                    "has_authority": bool(has_authority),
                    "last_request": bool(requested),
                    "last_success": bool(success),
                }
            )

    def set_sdk_activation(self, activated: bool):
        with self._lock:
            self.sdk["activated"] = bool(activated)

    def set_sdk_opened(self, opened: bool):
        with self._lock:
            self.sdk["opened"] = bool(opened)


