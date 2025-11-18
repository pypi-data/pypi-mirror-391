import os
import sys
import types

here = os.path.dirname(__file__)
candidates = [
    os.path.abspath(os.path.join(here, "..", "src")),
    os.path.abspath(os.path.join(here, "..")),
    os.path.abspath(os.path.join(here, "..", "src", "py_mavlink_dji")),
]
for p in candidates:
    if os.path.exists(p):
        sys.path.insert(0, p)
        break


def make_fake_pymavlink():
    pymod = types.ModuleType("pymavlink")

    class _Mavutil:
        class mavlink:
            MAV_CMD_NAV_TAKEOFF = 1
            MAV_CMD_NAV_LAND = 2
            MAV_CMD_NAV_RETURN_TO_LAUNCH = 3
            MAV_RESULT_ACCEPTED = 0
            MAV_RESULT_DENIED = 2
            MAV_RESULT_FAILED = 4

        @staticmethod
        def mavlink_connection(uri):
            class Conn:
                def __init__(self):
                    self.written = []

                def recv_msg(self):
                    return None

            return Conn()

    pymod.mavutil = _Mavutil()
    return pymod


def test_adapter_receives_and_writes_command_acks(monkeypatch):
    fake = make_fake_pymavlink()
    monkeypatch.setitem(sys.modules, "pymavlink", fake)

    from py_mavlink_dji.adapter import Bridge
    from py_mavlink_dji.backend import MockBackend

    backend = MockBackend()
    bridge = Bridge(source_uri="udp:0.0.0.0:14550", backend=backend)

    # simulate backend invoking command ack callback directly
    backend._invoke_cmd_send_cb(1, "STATUS_CMD_EXE_SUCCESS")

    # Ensure that an ack was written to the fake mav connection
    assert len(bridge.mav.written) >= 1


