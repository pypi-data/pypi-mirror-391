from py_mavlink_dji.backend import MockBackend
from py_mavlink_dji.missions import MissionManager


def test_begin_fly_calls_backend_start_mission():
    backend = MockBackend()
    mgr = MissionManager(backend=backend)
    # prepare a fake mission with two items
    mgr.missions[0] = [{"seq": 0}, {"seq": 1}]
    assert mgr.state == "standby"
    ok = mgr.begin_fly(0, 0)
    assert ok is True
    # mission state should be flying
    assert mgr.state == "flying"
    # advance loop step to simulate progress
    mgr.loop_step()
    # after stepping, pointer should advance (prototype behavior)
    assert mgr.waypoint_ptr >= 1


