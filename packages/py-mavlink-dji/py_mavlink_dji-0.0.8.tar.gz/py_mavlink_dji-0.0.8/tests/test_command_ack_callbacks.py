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


def test_adapter_receives_and_writes_command_acks(monkeypatch):
    from py_mavlink_dji.adapter import Bridge
    from py_mavlink_dji.backend import MockBackend

    backend = MockBackend()
    bridge = Bridge(source_uri="udp:0.0.0.0:14550", backend=backend)

    # simulate backend invoking command ack callback directly
    backend._invoke_cmd_send_cb(1, "STATUS_CMD_EXE_SUCCESS")

    # Ensure that an ack was written to the fake mav connection
    assert len(bridge.mav.written) >= 1


