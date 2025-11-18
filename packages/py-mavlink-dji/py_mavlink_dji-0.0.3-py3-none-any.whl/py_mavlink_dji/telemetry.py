"""
Telemetry helpers: encode DJI internal state into MAVLink messages.
This module prefers using the pymavlink encoder if available; otherwise
it returns None so callers can provide fallbacks.
"""
import sys
from typing import Optional, Dict


def encode_attitude_quaternion(mav_conn, attitude: Dict) -> Optional[bytes]:
    """
    Encode an attitude_quaternion MAVLink message using mav_conn.mav if possible.
    attitude: dict with keys q0,q1,q2,q3, pitchspeed,rollspeed,yawspeed
    """
    try:
        # connection-based encoder
        if hasattr(mav_conn, "mav") and hasattr(mav_conn.mav, "attitude_quaternion_encode"):
            msg = mav_conn.mav.attitude_quaternion_encode(
                0, 0,
                float(attitude.get("q0", 1.0)),
                float(attitude.get("q1", 0.0)),
                float(attitude.get("q2", 0.0)),
                float(attitude.get("q3", 0.0)),
                float(attitude.get("pitchspeed", 0.0)),
                float(attitude.get("rollspeed", 0.0)),
                float(attitude.get("yawspeed", 0.0)),
            )
            return msg
    except Exception:
        pass
    # try global pymavlink module
    pym = sys.modules.get("pymavlink")
    if pym and hasattr(pym, "mav") and hasattr(pym.mav, "attitude_quaternion_encode"):
        try:
            return pym.mav.attitude_quaternion_encode(
                0, 0,
                float(attitude.get("q0", 1.0)),
                float(attitude.get("q1", 0.0)),
                float(attitude.get("q2", 0.0)),
                float(attitude.get("q3", 0.0)),
                float(attitude.get("pitchspeed", 0.0)),
                float(attitude.get("rollspeed", 0.0)),
                float(attitude.get("yawspeed", 0.0)),
            )
        except Exception:
            pass
    return None


def encode_global_position_int(mav_conn, pos: Dict) -> Optional[bytes]:
    """
    Encode a GLOBAL_POSITION_INT message. pos: dict with lat, lon, alt (float degrees/meters)
    """
    try:
        if hasattr(mav_conn, "mav") and hasattr(mav_conn.mav, "global_position_int_encode"):
            lat = int(pos.get("lat", 0.0) * 1e7)
            lon = int(pos.get("lon", 0.0) * 1e7)
            alt = int(pos.get("alt", 0.0) * 1000)
            msg = mav_conn.mav.global_position_int_encode(
                0, 0, lat, lon, alt, 0, 0, 0, 0, 0
            )
            return msg
    except Exception:
        pass
    pym = sys.modules.get("pymavlink")
    if pym and hasattr(pym, "mav") and hasattr(pym.mav, "global_position_int_encode"):
        try:
            lat = int(pos.get("lat", 0.0) * 1e7)
            lon = int(pos.get("lon", 0.0) * 1e7)
            alt = int(pos.get("alt", 0.0) * 1000)
            return pym.mav.global_position_int_encode(0, 0, lat, lon, alt, 0, 0, 0, 0, 0)
        except Exception:
            pass
    return None


