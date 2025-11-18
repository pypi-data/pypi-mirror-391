import os
import sys

import pytest

here = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(here, "..", "src")))

from py_mavlink_dji.backend import HardwareBackend
from py_mavlink_dji.commands import Commands, SafetyError
from py_mavlink_dji.state import SharedState


class RecorderBackend(HardwareBackend):
    def __init__(self):
        self.calls = []

    def takeoff(self):
        self.calls.append("takeoff")
        return True

    def land(self):
        self.calls.append("land")
        return True

    def return_to_home(self):
        self.calls.append("rth")
        return True

    def upload_mission(self, mission_items):
        self.calls.append(("mission", mission_items))
        return True

    def pause_mission(self):
        self.calls.append("pause")
        return True


def test_low_battery_blocks_takeoff():
    state = SharedState()
    state.set_battery(5.0)
    backend = RecorderBackend()
    cmds = Commands(backend, state=state)
    with pytest.raises(SafetyError):
        cmds.takeoff()
    assert "takeoff" not in backend.calls


def test_emergency_stop_allows_recovery_land_only():
    state = SharedState()
    backend = RecorderBackend()
    cmds = Commands(backend, state=state)
    cmds.engage_emergency_stop()
    with pytest.raises(SafetyError):
        cmds.gimbal_control(pitch=0, roll=0, yaw=0)
    # Land should still go through to let the vehicle recover
    cmds.land()
    assert backend.calls == ["land"]


def test_failsafe_blocks_commands_but_not_rth():
    state = SharedState()
    backend = RecorderBackend()
    cmds = Commands(backend, state=state)
    cmds.trigger_failsafe("lost link")
    with pytest.raises(SafetyError):
        cmds.set_rc_override({"roll": 100})
    cmds.return_to_home()
    assert backend.calls[-1] == "rth"
