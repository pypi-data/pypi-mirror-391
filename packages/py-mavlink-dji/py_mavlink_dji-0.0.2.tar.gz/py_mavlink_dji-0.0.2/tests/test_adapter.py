import os
import sys
import types
import pytest

# Ensure package in src/ is importable when running tests in repo root or CI.
# Try several candidate locations (repo/src, repo, repo/src/py_mavlink_dji).
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
    """Create a fake pymavlink module with the minimal structure adapter expects."""
    pymod = types.ModuleType("pymavlink")

    class _Mavutil:
        class mavlink:
            MAV_CMD_NAV_TAKEOFF = 1
            MAV_CMD_NAV_LAND = 2
            MAV_CMD_NAV_RETURN_TO_LAUNCH = 3

        @staticmethod
        def mavlink_connection(uri):
            class Conn:
                def recv_msg(self):
                    return None

            return Conn()

    pymod.mavutil = _Mavutil()
    return pymod


def test_command_long_takeoff_calls_backend_takeoff(monkeypatch):
    fake = make_fake_pymavlink()
    monkeypatch.setitem(sys.modules, "pymavlink", fake)

    # import after installing fake pymavlink
    from py_mavlink_dji.adapter import Bridge
    from py_mavlink_dji.backend import HardwareBackend

    class Recorder(HardwareBackend):
        def __init__(self):
            self.calls = []

        def takeoff(self):
            self.calls.append("takeoff")

        def land(self):
            self.calls.append("land")

        def return_to_home(self):
            self.calls.append("rth")

        def upload_mission(self, mission_items):
            self.calls.append(("mission", mission_items))

        def pause_mission(self):
            self.calls.append("pause")

    backend = Recorder()
    bridge = Bridge(source_uri="udp:0.0.0.0:14550", backend=backend)

    # craft a fake COMMAND_LONG message
    class Msg:
        def get_type(self):
            return "COMMAND_LONG"

    msg = Msg()
    msg.command = sys.modules["pymavlink"].mavutil.mavlink.MAV_CMD_NAV_TAKEOFF

    bridge._handle(msg)
    assert backend.calls == ["takeoff"]


def test_mission_item_calls_upload_mission(monkeypatch):
    fake = make_fake_pymavlink()
    monkeypatch.setitem(sys.modules, "pymavlink", fake)

    from py_mavlink_dji.adapter import Bridge
    from py_mavlink_dji.backend import HardwareBackend

    class Recorder(HardwareBackend):
        def __init__(self):
            self.calls = []

        def takeoff(self):
            self.calls.append("takeoff")

        def land(self):
            self.calls.append("land")

        def return_to_home(self):
            self.calls.append("rth")

        def upload_mission(self, mission_items):
            self.calls.append(("mission", mission_items))

        def pause_mission(self):
            self.calls.append("pause")

    backend = Recorder()
    bridge = Bridge(source_uri="udp:0.0.0.0:14550", backend=backend)

    class Msg:
        def get_type(self):
            return "MISSION_ITEM"

    msg = Msg()
    msg.seq = 0
    msg.x = 12.34
    msg.y = 56.78
    msg.z = 100.0
    msg.command = 99

    bridge._handle(msg)
    assert len(backend.calls) == 1
    kind, items = backend.calls[0]
    assert kind == "mission"
    assert isinstance(items, list)
    assert items[0]["x"] == 12.34


