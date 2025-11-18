import os
import sys
import types

here = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(here, "..", "src")))


class FakeTransport:
    def __init__(self):
        self.sent = []
        self.on_recv = None

    def send(self, data: bytes):
        self.sent.append(data)

    def start_recv(self):
        pass

    def stop_recv(self):
        pass


def test_codec_build_parse_roundtrip():
    from py_mavlink_dji import codec
    data = codec.build_command("TAKEOFF", b"")
    name, payload = codec.parse_frame(data)
    assert name == "TAKEOFF"
    assert payload == b""


def test_pure_backend_sends_commands_and_mission_items():
    tr = FakeTransport()
    from py_mavlink_dji import codec
    from py_mavlink_dji.backend import PureDJIBackend
    be = PureDJIBackend(tr, codec)
    # takeoff should send a framed TAKEOFF
    be.takeoff()
    assert any(b"TAKEOFF" in s for s in tr.sent)
    # land
    be.land()
    assert any(b"LAND" in s for s in tr.sent)
    # upload mission items
    tr.sent.clear()
    items = [{"seq": 0, "x": 1.0, "y": 2.0, "z": 3.0}]
    be.upload_mission(items)
    # expect at least one MISSION_ITEM frame
    assert any(b"MISSION_ITEM" in s or b"MISSION_ITEM" in codec.parse_frame(s)[0].encode() for s in tr.sent)


