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


def test_commands_queue_when_backend_delays_ack(monkeypatch):
    fake = make_fake_pymavlink()
    monkeypatch.setitem(sys.modules, "pymavlink", fake)

    from py_mavlink_dji.adapter import Bridge
    from py_mavlink_dji.backend import HardwareBackend

    class BackendNoAck(HardwareBackend):
        def __init__(self):
            self.calls = []
            self._cmd_send_cb = None

        def takeoff(self):
            self.calls.append("takeoff")
            return True

        def land(self):
            self.calls.append("land")
            return True

        def set_cmd_send_cb(self, cb):
            self._cmd_send_cb = cb
            return True

        def _invoke_cmd_send_cb(self, cmd_id, status_str):
            cb = getattr(self, "_cmd_send_cb", None)
            if cb:
                cb(cmd_id, status_str)
                return True
            return False

    backend = BackendNoAck()
    bridge = Bridge(source_uri="udp:0.0.0.0:14550", backend=backend)

    class Msg:
        def __init__(self, cmd):
            self.command = cmd
        def get_type(self):
            return "COMMAND_LONG"

    # send two commands; backend will not ack automatically
    bridge._handle(Msg(1))
    bridge._handle(Msg(2))

    # Only first should have been dispatched to backend immediately
    assert backend.calls == ["takeoff"]

    # Now simulate ack for first command; this should trigger dispatch of queued command
    backend._invoke_cmd_send_cb(1, "STATUS_CMD_EXE_SUCCESS")
    assert backend.calls == ["takeoff", "land"]


