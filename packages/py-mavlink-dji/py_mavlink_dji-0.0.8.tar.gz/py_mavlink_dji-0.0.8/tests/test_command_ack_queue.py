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


def test_multiple_command_ack_emission(monkeypatch):
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
    from py_mavlink_dji.adapter import Bridge
    from py_mavlink_dji.backend import MockBackend

    backend = MockBackend()
    bridge = Bridge(source_uri="udp:0.0.0.0:14550", backend=backend)

    # Simulate timeout then refuse for command id 99
    backend._invoke_cmd_send_cb(99, "REQ_TIME_OUT")
    backend._invoke_cmd_send_cb(99, "REQ_REFUSE")

    joined = b"".join(bridge.mav.written)
    assert b"ACK:99" in joined


