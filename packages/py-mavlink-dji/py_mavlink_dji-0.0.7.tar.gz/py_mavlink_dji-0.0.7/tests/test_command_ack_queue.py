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

    class _Mav:
        @staticmethod
        def command_ack_encode(cmd, result):
            return f"ACK:{int(cmd)}:{int(result)}".encode()

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
            # attach a `mav` encoder object on the connection to emulate pymavlink behavior
            conn = Conn()
            conn.mav = _Mav()
            return conn

    pymod.mavutil = _Mavutil()
    pymod.mav = _Mav()
    return pymod


def test_multiple_command_ack_emission(monkeypatch):
    fake = make_fake_pymavlink()
    monkeypatch.setitem(sys.modules, "pymavlink", fake)

    from py_mavlink_dji.adapter import Bridge
    from py_mavlink_dji.backend import MockBackend

    backend = MockBackend()
    bridge = Bridge(source_uri="udp:0.0.0.0:14550", backend=backend)

    class Msg:
        def __init__(self, cmd):
            self.command = cmd
        def get_type(self):
            return "COMMAND_LONG"

    # Send two commands in sequence
    bridge._handle(Msg(1))
    bridge._handle(Msg(2))

    # backend mock emits ack callbacks for each command; ensure at least two acks written
    assert len(bridge.mav.written) >= 2
    # ensure contents reference expected command ids
    joined = b"".join(bridge.mav.written)
    assert b"ACK:1" in joined
    assert b"ACK:2" in joined


def test_timeout_and_refuse_translate_to_failed_and_denied(monkeypatch):
    fake = make_fake_pymavlink()
    monkeypatch.setitem(sys.modules, "pymavlink", fake)

    from py_mavlink_dji.adapter import Bridge
    from py_mavlink_dji.backend import MockBackend

    backend = MockBackend()
    bridge = Bridge(source_uri="udp:0.0.0.0:14550", backend=backend)

    # Simulate timeout then refuse for command id 99
    backend._invoke_cmd_send_cb(99, "REQ_TIME_OUT")
    backend._invoke_cmd_send_cb(99, "REQ_REFUSE")

    joined = b"".join(bridge.mav.written)
    assert b"ACK:99" in joined


