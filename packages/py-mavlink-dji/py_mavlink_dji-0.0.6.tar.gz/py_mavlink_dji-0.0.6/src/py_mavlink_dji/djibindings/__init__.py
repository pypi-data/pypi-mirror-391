try:
    # compiled extension
    from . import _djibindings as _core  # type: ignore
except Exception:
    _core = None


def activate(app_id=None, app_key=None, api_level=None):
    if _core is None:
        raise ImportError("djibindings extension not built")
    return _core.activate(app_id, app_key, api_level)


def get_broadcast():
    if _core is None:
        raise ImportError("djibindings extension not built")
    return _core.get_broadcast()


def get_broadcast_normalized():
    """Return a normalized broadcast dict matching SharedState schema."""
    raw = get_broadcast()
    out = {}
    # attitude quaternion
    att = raw.get("attitude", {})
    out["attitude"] = {
        "q0": float(att.get("q0", 1.0)),
        "q1": float(att.get("q1", 0.0)),
        "q2": float(att.get("q2", 0.0)),
        "q3": float(att.get("q3", 0.0)),
    }
    # angular rates may be under 'angular' or 'w'
    angular = raw.get("angular", raw.get("w", {}))
    out["angular"] = {
        "wx": float(angular.get("wx", 0.0)),
        "wy": float(angular.get("wy", 0.0)),
        "wz": float(angular.get("wz", 0.0)),
    }
    pos = raw.get("position", {})
    out["position"] = {
        "lat": float(pos.get("lat", 0.0)),
        "lon": float(pos.get("lon", 0.0)),
        "alt": float(pos.get("alt", 0.0)),
    }
    vel = raw.get("velocity", {})
    out["velocity"] = {
        "vx": float(vel.get("vx", 0.0)),
        "vy": float(vel.get("vy", 0.0)),
        "vz": float(vel.get("vz", 0.0)),
    }
    out["rc"] = raw.get("rc", {})
    out["battery"] = float(raw.get("battery", 0.0))
    return out


def takeoff():
    if _core is None:
        raise ImportError("djibindings extension not built")
    return _core.takeoff()


def land():
    if _core is None:
        raise ImportError("djibindings extension not built")
    return _core.land()


def return_to_home():
    if _core is None:
        raise ImportError("djibindings extension not built")
    return _core.return_to_home()


def upload_mission(mission_items):
    if _core is None:
        raise ImportError("djibindings extension not built")
    return _core.upload_mission(mission_items)


def start_mission(mission_id=0, start_seq=0):
    if _core is None:
        raise ImportError("djibindings extension not built")
    return _core.start_mission(mission_id, start_seq)


def pause_mission():
    if _core is None:
        raise ImportError("djibindings extension not built")
    return _core.pause_mission()


def gimbal_control(pitch=0, roll=0, yaw=0):
    if _core is None:
        raise ImportError("djibindings extension not built")
    return _core.gimbal_control(pitch, roll, yaw)


def set_rc_override(channels):
    if _core is None:
        raise ImportError("djibindings extension not built")
    return _core.set_rc_override(channels)


