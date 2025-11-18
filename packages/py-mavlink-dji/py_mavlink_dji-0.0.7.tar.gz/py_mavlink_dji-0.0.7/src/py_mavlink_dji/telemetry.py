"""
Telemetry helpers: encode DJI internal state into MAVLink messages.
This module prefers using the pymavlink encoder if available; otherwise
it returns None so callers can provide fallbacks.
"""
import sys
from typing import Optional, Dict


def _as_milligravity(value: float) -> int:
    """Convert m/s^2 into milli-g units expected by RAW_IMU/SCALED_IMU."""
    try:
        g = float(value)
    except Exception:
        g = 0.0
    # convert to g then milli-g
    return int((g / 9.80665) * 1000.0)


def _as_millirad(value: float) -> int:
    """Convert rad/s into milli-radians per second."""
    try:
        r = float(value)
    except Exception:
        r = 0.0
    return int(r * 1000.0)


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


def encode_heartbeat(mav_conn, custom_mode: int = 0, base_mode: int = 0, system_status: int = 0, mav_type: int = 2) -> Optional[bytes]:
    """Encode a HEARTBEAT message."""
    try:
        if hasattr(mav_conn, "mav") and hasattr(mav_conn.mav, "heartbeat_encode"):
            return mav_conn.mav.heartbeat_encode(custom_mode, base_mode, mav_type, 0, system_status)
    except Exception:
        pass
    pym = sys.modules.get("pymavlink")
    if pym and hasattr(pym, "mav") and hasattr(pym.mav, "heartbeat_encode"):
        try:
            return pym.mav.heartbeat_encode(custom_mode, base_mode, mav_type, 0, system_status)
        except Exception:
            pass
    return None


def encode_gps_raw_int(mav_conn, pos: Dict) -> Optional[bytes]:
    """Encode a GPS_RAW_INT / GLOBAL_POSITION_INT-like message for degrees/meters pos."""
    try:
        if hasattr(mav_conn, "mav") and hasattr(mav_conn.mav, "gps_raw_int_encode"):
            lat = int(pos.get("lat", 0.0) * 1e7)
            lon = int(pos.get("lon", 0.0) * 1e7)
            alt = int(pos.get("alt", 0.0) * 1000)
            # fields: time_usec,fix_type,lat,lon,alt,hdop,vdop,vvel,vel,course
            return mav_conn.mav.gps_raw_int_encode(0, 3, lat, lon, alt, 0, 0, 0, 0, 0)
    except Exception:
        pass
    pym = sys.modules.get("pymavlink")
    if pym and hasattr(pym, "mav") and hasattr(pym.mav, "gps_raw_int_encode"):
        try:
            lat = int(pos.get("lat", 0.0) * 1e7)
            lon = int(pos.get("lon", 0.0) * 1e7)
            alt = int(pos.get("alt", 0.0) * 1000)
            return pym.mav.gps_raw_int_encode(0, 3, lat, lon, alt, 0, 0, 0, 0, 0)
        except Exception:
            pass
    return None


def encode_battery_status(mav_conn, battery_level: float) -> Optional[bytes]:
    """Encode a BATTERY_STATUS message using percent (0-100)."""
    try:
        if hasattr(mav_conn, "mav") and hasattr(mav_conn.mav, "battery_status_encode"):
            # rudimentary mapping: battery_remaining, voltages array
            batt = int(battery_level)
            voltages = [int((batt / 100.0) * 3700)] * 6
            return mav_conn.mav.battery_status_encode(0, voltages, 0, 0, batt)
    except Exception:
        pass
    pym = sys.modules.get("pymavlink")
    if pym and hasattr(pym, "mav") and hasattr(pym.mav, "battery_status_encode"):
        try:
            batt = int(battery_level)
            voltages = [int((batt / 100.0) * 3700)] * 6
            return pym.mav.battery_status_encode(0, voltages, 0, 0, batt)
        except Exception:
            pass
    return None


def encode_rc_channels_scaled(mav_conn, rc: Dict) -> Optional[bytes]:
    """Encode RC_CHANNELS_SCALED using rc dict with pitch/roll/yaw/throttle keys (0-1000)."""
    try:
        if hasattr(mav_conn, "mav") and hasattr(mav_conn.mav, "rc_channels_scaled_encode"):
            chan1 = int(rc.get("roll", 0))
            chan2 = int(rc.get("pitch", 0))
            chan3 = int(rc.get("throttle", 0))
            chan4 = int(rc.get("yaw", 0))
            chan5 = int(rc.get("mode", 0))
            chan6 = int(rc.get("gear", 0))
            return mav_conn.mav.rc_channels_scaled_encode(0, 0, chan1, chan2, chan3, chan4, chan5, chan6)
    except Exception:
        pass
    pym = sys.modules.get("pymavlink")
    if pym and hasattr(pym, "mav") and hasattr(pym.mav, "rc_channels_scaled_encode"):
        try:
            chan1 = int(rc.get("roll", 0))
            chan2 = int(rc.get("pitch", 0))
            chan3 = int(rc.get("throttle", 0))
            chan4 = int(rc.get("yaw", 0))
            chan5 = int(rc.get("mode", 0))
            chan6 = int(rc.get("gear", 0))
            return pym.mav.rc_channels_scaled_encode(0, 0, chan1, chan2, chan3, chan4, chan5, chan6)
        except Exception:
            pass
    return None


def encode_local_position_ned(mav_conn, local: Dict) -> Optional[bytes]:
    """Encode LOCAL_POSITION_NED message from local x/y/z in meters and vx/vy/vz."""
    try:
        if hasattr(mav_conn, "mav") and hasattr(mav_conn.mav, "local_position_ned_encode"):
            x = float(local.get("x", 0.0))
            y = float(local.get("y", 0.0))
            z = float(local.get("z", 0.0))
            vx = float(local.get("vx", 0.0))
            vy = float(local.get("vy", 0.0))
            vz = float(local.get("vz", 0.0))
            return mav_conn.mav.local_position_ned_encode(0, 0, x, y, z, vx, vy, vz)
    except Exception:
        pass
    pym = sys.modules.get("pymavlink")
    if pym and hasattr(pym, "mav") and hasattr(pym.mav, "local_position_ned_encode"):
        try:
            x = float(local.get("x", 0.0))
            y = float(local.get("y", 0.0))
            z = float(local.get("z", 0.0))
            vx = float(local.get("vx", 0.0))
            vy = float(local.get("vy", 0.0))
            vz = float(local.get("vz", 0.0))
            return pym.mav.local_position_ned_encode(0, 0, x, y, z, vx, vy, vz)
        except Exception:
            pass
    return None


def encode_raw_imu(mav_conn, sensors: Dict) -> Optional[bytes]:
    """Encode RAW_IMU message using acceleration/gyro readings."""
    try:
        if hasattr(mav_conn, "mav") and hasattr(mav_conn.mav, "raw_imu_encode"):
            ax = _as_milligravity(sensors.get("ax", 0.0))
            ay = _as_milligravity(sensors.get("ay", 0.0))
            az = _as_milligravity(sensors.get("az", 0.0))
            gx = _as_millirad(sensors.get("gx", 0.0))
            gy = _as_millirad(sensors.get("gy", 0.0))
            gz = _as_millirad(sensors.get("gz", 0.0))
            return mav_conn.mav.raw_imu_encode(0, ax, ay, az, gx, gy, gz, 0, 0, 0)
    except Exception:
        pass
    pym = sys.modules.get("pymavlink")
    if pym and hasattr(pym, "mav") and hasattr(pym.mav, "raw_imu_encode"):
        try:
            ax = _as_milligravity(sensors.get("ax", 0.0))
            ay = _as_milligravity(sensors.get("ay", 0.0))
            az = _as_milligravity(sensors.get("az", 0.0))
            gx = _as_millirad(sensors.get("gx", 0.0))
            gy = _as_millirad(sensors.get("gy", 0.0))
            gz = _as_millirad(sensors.get("gz", 0.0))
            return pym.mav.raw_imu_encode(0, ax, ay, az, gx, gy, gz, 0, 0, 0)
        except Exception:
            pass
    return None


def encode_scaled_imu(mav_conn, sensors: Dict) -> Optional[bytes]:
    """Encode SCALED_IMU message mirroring the RAW_IMU payload for compatibility."""
    try:
        if hasattr(mav_conn, "mav") and hasattr(mav_conn.mav, "scaled_imu_encode"):
            ax = _as_milligravity(sensors.get("ax", 0.0))
            ay = _as_milligravity(sensors.get("ay", 0.0))
            az = _as_milligravity(sensors.get("az", 0.0))
            gx = _as_millirad(sensors.get("gx", 0.0))
            gy = _as_millirad(sensors.get("gy", 0.0))
            gz = _as_millirad(sensors.get("gz", 0.0))
            return mav_conn.mav.scaled_imu_encode(0, ax, ay, az, gx, gy, gz, 0, 0, 0)
    except Exception:
        pass
    pym = sys.modules.get("pymavlink")
    if pym and hasattr(pym, "mav") and hasattr(pym.mav, "scaled_imu_encode"):
        try:
            ax = _as_milligravity(sensors.get("ax", 0.0))
            ay = _as_milligravity(sensors.get("ay", 0.0))
            az = _as_milligravity(sensors.get("az", 0.0))
            gx = _as_millirad(sensors.get("gx", 0.0))
            gy = _as_millirad(sensors.get("gy", 0.0))
            gz = _as_millirad(sensors.get("gz", 0.0))
            return pym.mav.scaled_imu_encode(0, ax, ay, az, gx, gy, gz, 0, 0, 0)
        except Exception:
            pass
    return None


def encode_statustext(mav_conn, text: str) -> Optional[bytes]:
    """Encode STATUSTEXT v1 message conveying SDK state."""
    if not text:
        return None
    try:
        if hasattr(mav_conn, "mav") and hasattr(mav_conn.mav, "statustext_encode"):
            return mav_conn.mav.statustext_encode(6, text[:50])
    except Exception:
        pass
    pym = sys.modules.get("pymavlink")
    if pym and hasattr(pym, "mav") and hasattr(pym.mav, "statustext_encode"):
        try:
            return pym.mav.statustext_encode(6, text[:50])
        except Exception:
            pass
    return None

