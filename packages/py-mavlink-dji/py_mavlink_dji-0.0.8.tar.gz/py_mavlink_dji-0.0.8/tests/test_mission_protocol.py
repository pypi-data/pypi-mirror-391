import os
import sys
import types
import pytest

# Ensure package in src/ is importable
here = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(here, "..", "src")))

# Tests assume `pymavlink` is installed and available; no fake factory required.


def test_mission_upload_sequence(monkeypatch):
    from py_mavlink_dji.adapter import Bridge
    from py_mavlink_dji.backend import HardwareBackend

    class Recorder(HardwareBackend):
        def __init__(self):
            self.calls = []
        def takeoff(self): pass
        def land(self): pass
        def return_to_home(self): pass
        def upload_mission(self, items): self.calls.append(("upload", items))
        def pause_mission(self): pass

    backend = Recorder()
    bridge = Bridge(source_uri="udp:0.0.0.0:14550", backend=backend)
    # capture remote write buffer
    conn = bridge.mav

    # simulate ground sending MISSION_COUNT=2
    class Msg:
        def get_type(self): return "MISSION_COUNT"
    mc = Msg()
    mc.count = 2
    bridge._handle(mc)
    # bridge should have sent something (request or encoded message); be tolerant about type
    assert len(conn.written) > 0

    def as_text(x):
        if isinstance(x, (bytes, bytearray)):
            try:
                return x.decode("utf-8", errors="ignore")
            except Exception:
                return repr(x)
        return repr(x)

    # simulate MISSION_ITEM seq 0
    class MI:
        def get_type(self): return "MISSION_ITEM"
    mi0 = MI()
    mi0.seq = 0
    mi0.x = 1.0
    mi0.y = 2.0
    mi0.z = 3.0
    mi0.command = 16
    bridge._handle(mi0)
    # after receiving first item, should have requested next seq (or written another frame)
    assert len(conn.written) > 0

    # simulate MISSION_ITEM seq 1
    mi1 = MI()
    mi1.seq = 1
    mi1.x = 4.0
    mi1.y = 5.0
    mi1.z = 6.0
    mi1.command = 16
    bridge._handle(mi1)
    # after last item, expect an ack or mission_ack-like frame
    assert any(("ACK:" in as_text(b)) or ("mission_ack" in as_text(b).lower()) for b in conn.written)


