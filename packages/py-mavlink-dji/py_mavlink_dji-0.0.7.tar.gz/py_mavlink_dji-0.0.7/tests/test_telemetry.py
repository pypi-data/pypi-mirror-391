import os
import sys
import types

def make_fake_pymavlink_encoders():
    pymod = types.ModuleType("pymavlink")

    class _Mav:
        @staticmethod
        def attitude_quaternion_encode(*args, **kwargs):
            return b"ATT"

        @staticmethod
        def global_position_int_encode(*args, **kwargs):
            return b"GPI"

        @staticmethod
        def raw_imu_encode(*args, **kwargs):
            return b"RAW"

        @staticmethod
        def scaled_imu_encode(*args, **kwargs):
            return b"SCL"

        @staticmethod
        def statustext_encode(*args, **kwargs):
            return b"TXT"

    class _Mavutil:
        @staticmethod
        def mavlink_connection(uri):
            class Conn:
                def __init__(self):
                    self.written = []
                def write(self, data):
                    self.written.append(data)
            return Conn()

    pymod.mav = _Mav()
    pymod.mavutil = _Mavutil()
    return pymod


def _written_types(buffer):
    out = []
    for item in buffer:
        get_type = getattr(item, "get_type", None)
        if callable(get_type):
            out.append(get_type())
        else:
            out.append(item)
    return out


def test_send_telemetry_writes_msgs(monkeypatch):
    fake = make_fake_pymavlink_encoders()
    monkeypatch.setitem(sys.modules, "pymavlink", fake)

    # ensure adapter imports from src
    here = os.path.dirname(__file__)
    sys.path.insert(0, os.path.abspath(os.path.join(here, "..", "src")))

    from py_mavlink_dji.adapter import Bridge

    b = Bridge(source_uri="udp:0.0.0.0:14550")
    # ensure writer buffer exists
    conn = b.mav
    b.send_telemetry(attitude={"q0": 1.0}, position={"lat": 1.23, "lon": 4.56, "alt": 7.8})
    written = _written_types(conn.written)
    assert any(x in (b"ATT", "ATTITUDE_QUATERNION") for x in written)
    assert any(x in (b"GPI", "GLOBAL_POSITION_INT") for x in written)


def test_send_telemetry_emits_imu_and_status(monkeypatch):
    fake = make_fake_pymavlink_encoders()
    monkeypatch.setitem(sys.modules, "pymavlink", fake)

    here = os.path.dirname(__file__)
    sys.path.insert(0, os.path.abspath(os.path.join(here, "..", "src")))

    from py_mavlink_dji.adapter import Bridge

    b = Bridge(source_uri="udp:0.0.0.0:14550")
    conn = b.mav
    b.send_telemetry(
        acceleration={"ax": 1.0, "ay": 2.0, "az": -9.8},
        angular={"wx": 0.1, "wy": 0.2, "wz": 0.3},
        status_text="sdk ok",
    )
    written = _written_types(conn.written)
    assert any(x in (b"RAW", "RAW_IMU") for x in written)
    assert any(x in (b"SCL", "SCALED_IMU") for x in written)
    assert any(x in (b"TXT", "STATUSTEXT") for x in written)


