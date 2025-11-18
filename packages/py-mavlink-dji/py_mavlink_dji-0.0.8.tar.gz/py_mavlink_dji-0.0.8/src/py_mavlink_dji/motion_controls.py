"""Motion control helpers mapping higher-level commands to backend calls."""
from typing import Optional, Dict, TYPE_CHECKING
import math

from .commands import SafetyError

if TYPE_CHECKING:
    from .commands import SafetyController


CTRL_FLAGS = {
    "angle": 0x90,
    "position": 0x90,
    "velocity": 0x44,
    "rate": 0x44,
}


def fly_to_localpos(backend, x: float, y: float, z: float, safety: Optional["SafetyController"] = None):
    """Request movement to local position — prototype maps to set_attitude or set_velocity depending on backend."""
    if safety:
        safety.validate_local_target(x, y, z)
    # Prefer velocity-based movement if supported
    try:
        vx = x
        vy = y
        vz = z
        if hasattr(backend, "set_velocity"):
            if safety:
                safety.validate_velocity(vx, vy, vz)
            return backend.set_velocity(vx, vy, vz, frame="local")
    except Exception:
        pass
    # fallback to attitude control if available
    try:
        if hasattr(backend, "set_attitude"):
            return set_attitude(backend, 0.0, 0.0, 0.0, 0.0, safety=safety)
    except Exception:
        pass
    return False


def set_velocity(backend, vx: float, vy: float, vz: float, frame: str = "local", safety: Optional["SafetyController"] = None):
    if safety:
        safety.validate_velocity(vx, vy, vz)
    try:
        return backend.set_velocity(vx, vy, vz, frame=frame)
    except Exception:
        return False


def gimbal_look_at(backend, pitch: float, roll: float, yaw: float):
    try:
        if hasattr(backend, "gimbal_control"):
            return backend.gimbal_control(pitch=pitch, roll=roll, yaw=yaw)
    except Exception:
        pass
    return False


def fly_to_globalpos(
    backend,
    lat: float,
    lon: float,
    alt: float,
    reference: Optional[Dict[str, float]] = None,
    safety: Optional["SafetyController"] = None,
):
    """Approximate GPS -> local frame movement by projecting into meters and delegating to fly_to_localpos."""
    ref = reference or {}
    ref_lat = float(ref.get("lat", 0.0))
    ref_lon = float(ref.get("lon", 0.0))
    ref_alt = float(ref.get("alt", 0.0))
    if safety:
        safety.validate_global_target(lat, lon, alt)
    delta_lat = float(lat) - ref_lat
    delta_lon = float(lon) - ref_lon
    # Rough meters-per-degree conversions (good enough for small deltas)
    meters_per_deg_lat = 111_139.0
    meters_per_deg_lon = 111_139.0 * math.cos(math.radians(ref_lat))
    north = delta_lat * meters_per_deg_lat
    east = delta_lon * meters_per_deg_lon
    down = ref_alt - float(alt)
    return fly_to_localpos(backend, north, east, down, safety=safety)


def set_attitude(
    backend,
    roll: float,
    pitch: float,
    yaw: float,
    thrust: float,
    *,
    mode: str = "angle",
    safety: Optional["SafetyController"] = None,
):
    """Send an attitude command with DJI ctrl_flag semantics."""
    if safety:
        safety.check_preflight("set_attitude")
    flag = CTRL_FLAGS.get(mode.lower(), CTRL_FLAGS["angle"])
    try:
        if hasattr(backend, "set_attitude"):
            return backend.set_attitude(roll, pitch, yaw, thrust, ctrl_flag=flag)
    except SafetyError:
        raise
    except Exception:
        pass
    return False


