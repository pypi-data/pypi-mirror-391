import os
import sys
import types

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


# Tests assume `pymavlink` is installed and available; no fake factory required.


def test_command_long_takeoff_calls_backend_takeoff(monkeypatch):
    # import after ensuring pymavlink is available
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


def test_request_control_authority_updates_state(monkeypatch):
    from py_mavlink_dji.adapter import Bridge
    from py_mavlink_dji.backend import HardwareBackend

    class ControlBackend(HardwareBackend):
        def __init__(self):
            self.calls = []

        def takeoff(self):
            return True

        def land(self):
            return True

        def return_to_home(self):
            return True

        def upload_mission(self, mission_items):
            return True

        def pause_mission(self):
            return True

        def set_velocity(self, vx, vy, vz, frame="local"):
            return True

        def set_attitude(self, roll, pitch, yaw, thrust, ctrl_flag=None):
            return True

        def control_management(self, obtain=True):
            self.calls.append(obtain)
            return True

        def start_polling(self, state_update_cb=None, interval=0.02):
            self.cb = state_update_cb

    backend = ControlBackend()
    bridge = Bridge(source_uri="udp:0.0.0.0:14550", backend=backend)
    bridge.request_control_authority(True)
    snap = bridge.state.snapshot()
    assert backend.calls == [True]
    assert snap["control"]["has_authority"] is True
    bridge.request_control_authority(False)
    snap = bridge.state.snapshot()
    assert backend.calls == [True, False]
    assert snap["control"]["has_authority"] is False


def test_bridge_start_and_stop_manage_control_authority(monkeypatch):
    import py_mavlink_dji.adapter as adapter_mod

    class DummyThread:
        def __init__(self, target=None, daemon=False):
            self.target = target
            self.daemon = daemon

        def start(self):
            return None

        def join(self, timeout=None):
            return None

    monkeypatch.setattr(adapter_mod.threading, "Thread", DummyThread)

    from py_mavlink_dji.adapter import Bridge
    from py_mavlink_dji.backend import HardwareBackend

    class ControlBackend(HardwareBackend):
        def __init__(self):
            self.calls = []

        def takeoff(self):
            return True

        def land(self):
            return True

        def return_to_home(self):
            return True

        def upload_mission(self, mission_items):
            return True

        def pause_mission(self):
            return True

        def set_velocity(self, vx, vy, vz, frame="local"):
            return True

        def set_attitude(self, roll, pitch, yaw, thrust, ctrl_flag=None):
            return True

        def control_management(self, obtain=True):
            self.calls.append(obtain)
            return True

        def start_polling(self, state_update_cb=None, interval=0.02):
            self.cb = state_update_cb

    backend = ControlBackend()
    bridge = Bridge(source_uri="udp:0.0.0.0:14550", backend=backend)
    bridge.start()
    bridge.stop()
    assert backend.calls[:2] == [True, False]


def test_bridge_tracks_activation_and_opened(monkeypatch):
    import py_mavlink_dji.adapter as adapter_mod

    class DummyThread:
        def __init__(self, target=None, daemon=False):
            self.target = target
            self.daemon = daemon

        def start(self):
            return None

        def join(self, timeout=None):
            return None

    monkeypatch.setattr(adapter_mod.threading, "Thread", DummyThread)

    from py_mavlink_dji.backend import HardwareBackend

    class Backend(HardwareBackend):
        def __init__(self):
            self.activations = 0

        def takeoff(self):
            return True

        def land(self):
            return True

        def return_to_home(self):
            return True

        def upload_mission(self, mission_items):
            return True

        def pause_mission(self):
            return True

        def activate(self, app_id=None, app_key=None, api_level=None):
            self.activations += 1
            return True

    backend = Backend()
    bridge = adapter_mod.Bridge(source_uri="udp:0.0.0.0:14550", backend=backend)
    bridge.activate_backend()
    snap = bridge.state.snapshot()
    assert snap["sdk"]["activated"] is True
    bridge.start()
    snap = bridge.state.snapshot()
    assert snap["sdk"]["opened"] is True
    bridge.stop()
    snap = bridge.state.snapshot()
    assert snap["sdk"]["opened"] is False


def test_backend_callback_updates_flight_state(monkeypatch):
    from py_mavlink_dji.adapter import Bridge
    from py_mavlink_dji.backend import HardwareBackend

    class CallbackBackend(HardwareBackend):
        def __init__(self):
            self.cb = None

        def takeoff(self):
            return True

        def land(self):
            return True

        def return_to_home(self):
            return True

        def upload_mission(self, mission_items):
            return True

        def pause_mission(self):
            return True

        def set_velocity(self, vx, vy, vz, frame="local"):
            return True

        def set_attitude(self, roll, pitch, yaw, thrust, ctrl_flag=None):
            return True

        def control_management(self, obtain=True):
            return True

        def start_polling(self, state_update_cb=None, interval=0.02):
            self.cb = state_update_cb

    backend = CallbackBackend()
    bridge = Bridge(source_uri="udp:0.0.0.0:14550", backend=backend)
    sample = {
        "attitude": {"q0": 1.0, "q1": 0.0, "q2": 0.0, "q3": 0.0},
        "position": {"lat": 1.0, "lon": 2.0, "alt": 3.0},
        "velocity": {"vx": 0.0, "vy": 0.0, "vz": 0.0},
        "rc": {},
        "battery": 77.0,
        "ctrl_device": {"id": 2, "label": "onboard"},
        "flight_status": 3,
    }
    backend.cb(sample)
    snap = bridge.state.snapshot()
    assert snap["flight"]["ctrl_device_id"] == 2
    assert snap["flight"]["flight_status"] == 3


