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
    assert any(x == b"ATT" for x in conn.written)
    assert any(x == b"GPI" for x in conn.written)


