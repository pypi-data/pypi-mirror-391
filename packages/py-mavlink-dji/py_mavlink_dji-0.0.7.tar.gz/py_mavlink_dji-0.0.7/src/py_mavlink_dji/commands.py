"""High-level command wrappers that add safety protections before delegating to a backend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
import math


class SafetyError(RuntimeError):
    """Raised when a command is rejected for safety reasons."""


@dataclass
class Geofence:
    center: Optional[Tuple[float, float, float]] = None  # lat, lon, alt
    radius_m: float = 500.0
    altitude_bounds: Tuple[float, float] = (-100.0, 500.0)


class SafetyController:
    """Centralized guard rails for command execution."""

    def __init__(self, state=None, *, low_battery_pct: float = 15.0, max_velocity: float = 15.0):
        self.state = state
        self.low_battery_pct = float(low_battery_pct)
        self.max_velocity = float(max_velocity)
        self.geofence = Geofence()
        self._emergency_stop = False
        self._failsafe_reason: Optional[str] = None

    # --- Status helpers -------------------------------------------------
    def status(self) -> dict:
        return {
            "geofence": {
                "center": self.geofence.center,
                "radius_m": self.geofence.radius_m,
                "altitude_bounds": self.geofence.altitude_bounds,
            },
            "emergency_stop": self._emergency_stop,
            "failsafe_reason": self._failsafe_reason,
            "low_battery_pct": self.low_battery_pct,
        }

    # --- Configuration --------------------------------------------------
    def configure_geofence(self, *, center=None, radius_m=None, altitude_bounds=None):
        if center is not None:
            self.geofence.center = center
        if radius_m is not None:
            self.geofence.radius_m = float(radius_m)
        if altitude_bounds is not None:
            self.geofence.altitude_bounds = tuple(altitude_bounds)

    def engage_emergency_stop(self):
        self._emergency_stop = True

    def clear_emergency_stop(self):
        self._emergency_stop = False

    def trigger_failsafe(self, reason: str = "failsafe"):
        self._failsafe_reason = reason or "failsafe"

    def clear_failsafe(self):
        self._failsafe_reason = None

    # --- Checks ---------------------------------------------------------
    def _ensure_home_reference(self):
        if self.geofence.center is None and self.state is not None:
            snap = self.state.snapshot()
            pos = snap.get("position", {})
            self.geofence.center = (pos.get("lat", 0.0), pos.get("lon", 0.0), pos.get("alt", 0.0))

    def ensure_motion_allowed(self, *, allow_recovery: bool = False):
        if self._emergency_stop and not allow_recovery:
            raise SafetyError("Emergency stop engaged")
        if self._failsafe_reason and not allow_recovery:
            raise SafetyError(f"Failsafe active: {self._failsafe_reason}")

    def check_preflight(self, action: str):
        self.ensure_motion_allowed()
        if action in {"takeoff", "start_mission", "set_attitude"} and self.state is not None:
            try:
                battery = float(self.state.snapshot().get("battery", 0.0))
            except Exception:
                battery = 0.0
            if battery < self.low_battery_pct:
                raise SafetyError(f"Battery level {battery:.1f}% below threshold {self.low_battery_pct}%")

    def validate_velocity(self, vx: float, vy: float, vz: float):
        self.ensure_motion_allowed()
        horizontal = math.hypot(vx, vy)
        if horizontal > self.max_velocity:
            raise SafetyError("Velocity exceeds allowed magnitude")
        self._validate_altitude_delta(vz)

    def validate_local_target(self, x: float, y: float, z: float):
        self.ensure_motion_allowed()
        if self.geofence.radius_m is not None:
            if math.hypot(x, y) > self.geofence.radius_m:
                raise SafetyError("Local target outside geofence radius")
        self._validate_altitude_delta(z)

    def validate_global_target(self, lat: float, lon: float, alt: float):
        self.ensure_motion_allowed()
        self._ensure_home_reference()
        if self.geofence.center is not None and self.geofence.radius_m is not None:
            dist = self._distance_m(self.geofence.center[0], self.geofence.center[1], lat, lon)
            if dist > self.geofence.radius_m:
                raise SafetyError("Global target outside geofence")
        self._validate_absolute_altitude(alt)

    # --- Internal helpers -----------------------------------------------
    def _validate_altitude_delta(self, delta_z: float):
        low, high = self.geofence.altitude_bounds
        if delta_z < low or delta_z > high:
            raise SafetyError("Vertical target outside altitude bounds")

    def _validate_absolute_altitude(self, alt: float):
        low, high = self.geofence.altitude_bounds
        if alt < low or alt > high:
            raise SafetyError("Absolute altitude outside altitude bounds")

    @staticmethod
    def _distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6371000.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c


class Commands:
    def __init__(self, backend, state=None, safety: Optional[SafetyController] = None):
        self.backend = backend
        self.state = state
        self.safety = safety or SafetyController(state)
        # command send flag and queue to prevent overlapping command sends
        self._cmd_send_flag = False
        self._cmd_queue = []
        self._current_cmd_id = None

    def _enqueue_or_send(self, send_callable):
        """If a command is already in-flight, enqueue `send_callable`, otherwise send now."""
        if self._cmd_send_flag:
            self._cmd_queue.append(send_callable)
            return "queued"
        # set flag and current cmd id if backend provided a last cmd id
        self._cmd_send_flag = True
        try:
            self._current_cmd_id = getattr(self.backend, "_last_cmd_id", None)
        except Exception:
            self._current_cmd_id = None
        try:
            return send_callable()
        except Exception:
            # on immediate failure, clear flag so queue can proceed
            self._cmd_send_flag = False
            self._current_cmd_id = None
            raise

    def notify_cmd_status(self, cmd_id, status_str):
        """Called by adapter when SDK-level command status updates arrive.

        When a terminal status is observed (success/fail/timeout/refuse), clear the
        cmd_send_flag and dispatch the next queued command if any.
        """
        terminal_tokens = {"STATUS_CMD_EXE_SUCCESS", "STATUS_CMD_EXE_FAIL", "REQ_TIME_OUT", "REQ_REFUSE"}
        try:
            if cmd_id is None or self._current_cmd_id is None or int(cmd_id) == int(self._current_cmd_id):
                if status_str in terminal_tokens:
                    # clear current
                    self._cmd_send_flag = False
                    self._current_cmd_id = None
                    # dispatch next queued command if present
                    if self._cmd_queue:
                        next_callable = self._cmd_queue.pop(0)
                        # send next (will set flag/current)
                        try:
                            self._enqueue_or_send(next_callable)
                        except Exception:
                            # swallow to avoid cascading failures
                            pass
                    return True
        except Exception:
            pass
        return False

    def takeoff(self):
        """Initiate takeoff via backend."""
        self.safety.check_preflight("takeoff")
        return self._enqueue_or_send(lambda: self.backend.takeoff())

    def land(self):
        """Initiate landing via backend."""
        self.safety.ensure_motion_allowed(allow_recovery=True)
        return self._enqueue_or_send(lambda: self.backend.land())

    def return_to_home(self):
        """Initiate return-to-home via backend."""
        self.safety.ensure_motion_allowed(allow_recovery=True)
        return self._enqueue_or_send(lambda: self.backend.return_to_home())

    def pause_mission(self):
        self.safety.ensure_motion_allowed(allow_recovery=True)
        return self._enqueue_or_send(lambda: self.backend.pause_mission())

    def upload_mission(self, mission_items):
        return self.backend.upload_mission(mission_items)

    def start_mission(self, mission_id=0, start_seq=0):
        self.safety.check_preflight("start_mission")
        return self._enqueue_or_send(lambda: getattr(self.backend, "start_mission", lambda *_: False)(mission_id, start_seq))

    def gimbal_control(self, pitch=0, roll=0, yaw=0):
        self.safety.ensure_motion_allowed()
        return self._enqueue_or_send(lambda: getattr(self.backend, "gimbal_control", lambda *_: False)(pitch, roll, yaw))

    def set_rc_override(self, channels):
        self.safety.ensure_motion_allowed()
        return self._enqueue_or_send(lambda: getattr(self.backend, "set_rc_override", lambda *_: False)(channels))

    # --- Safety plumbing -------------------------------------------------
    def configure_geofence(self, *, center=None, radius_m=None, altitude_bounds=None):
        self.safety.configure_geofence(center=center, radius_m=radius_m, altitude_bounds=altitude_bounds)

    def engage_emergency_stop(self):
        self.safety.engage_emergency_stop()

    def clear_emergency_stop(self):
        self.safety.clear_emergency_stop()

    def trigger_failsafe(self, reason: str = "failsafe"):
        self.safety.trigger_failsafe(reason)

    def clear_failsafe(self):
        self.safety.clear_failsafe()

    def safety_status(self) -> dict:
        return self.safety.status()


