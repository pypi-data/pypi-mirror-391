"""Motion control helpers mapping higher-level commands to backend calls."""
from typing import Optional


def fly_to_localpos(backend, x: float, y: float, z: float):
    """Request movement to local position — prototype maps to set_attitude or set_velocity depending on backend."""
    # Prefer velocity-based movement if supported
    try:
        vx = x
        vy = y
        vz = z
        if hasattr(backend, "set_velocity"):
            return backend.set_velocity(vx, vy, vz, frame="local")
    except Exception:
        pass
    # fallback to attitude control if available
    try:
        if hasattr(backend, "set_attitude"):
            return backend.set_attitude(0.0, 0.0, 0.0, 0.0)
    except Exception:
        pass
    return False


def set_velocity(backend, vx: float, vy: float, vz: float, frame: str = "local"):
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


