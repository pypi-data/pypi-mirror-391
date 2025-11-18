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


# Tests assume `pymavlink` is installed and available; no fake factory required.


def test_commands_queue_when_backend_delays_ack(monkeypatch):
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


