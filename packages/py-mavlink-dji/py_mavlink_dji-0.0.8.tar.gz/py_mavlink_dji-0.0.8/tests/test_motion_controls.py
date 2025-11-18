import math
import os
import sys

import pytest

here = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(here, "..", "src")))

from py_mavlink_dji.motion_controls import fly_to_globalpos, set_attitude
from py_mavlink_dji.commands import SafetyController, SafetyError
from py_mavlink_dji.state import SharedState


class RecorderBackend:
    def __init__(self):
        self.calls = []

    def set_velocity(self, vx, vy, vz, frame="local"):
        self.calls.append((vx, vy, vz, frame))
        return True


def test_fly_to_globalpos_projects_to_local_reference():
    backend = RecorderBackend()
    reference = {"lat": 47.0, "lon": 8.0, "alt": 500.0}
    fly_to_globalpos(backend, lat=47.0001, lon=8.0002, alt=495.0, reference=reference)
    assert backend.calls, "set_velocity should be invoked"
    vx, vy, vz, frame = backend.calls[-1]
    assert frame == "local"
    expected_north = 0.0001 * 111_139.0
    expected_east = 0.0002 * 111_139.0 * math.cos(math.radians(47.0))
    expected_down = 500.0 - 495.0
    assert vx == pytest.approx(expected_north, rel=1e-4)
    assert vy == pytest.approx(expected_east, rel=1e-4)
    assert vz == pytest.approx(expected_down, rel=1e-4)


def test_fly_to_globalpos_defaults_to_zero_reference():
    backend = RecorderBackend()
    fly_to_globalpos(backend, lat=0.001, lon=0.002, alt=-10.0)
    vx, vy, vz, frame = backend.calls[-1]
    assert frame == "local"
    assert vx != 0.0 and vy != 0.0


def test_geofence_blocks_global_target():
    backend = RecorderBackend()
    state = SharedState()
    state.update_position(47.0, 8.0, 500.0)
    safety = SafetyController(state)
    safety.configure_geofence(radius_m=5.0)
    with pytest.raises(SafetyError):
        fly_to_globalpos(backend, lat=47.001, lon=8.0, alt=500.0, safety=safety)


def test_set_attitude_applies_ctrl_flag():
    class AttRecorder:
        def __init__(self):
            self.calls = []

        def set_attitude(self, roll, pitch, yaw, thrust, ctrl_flag=None):
            self.calls.append({
                "roll": roll,
                "pitch": pitch,
                "yaw": yaw,
                "thrust": thrust,
                "ctrl_flag": ctrl_flag,
            })
            return True

    backend = AttRecorder()
    set_attitude(backend, 0.1, 0.2, 0.3, 0.4, mode="velocity")
    assert backend.calls[-1]["ctrl_flag"] == 0x44
