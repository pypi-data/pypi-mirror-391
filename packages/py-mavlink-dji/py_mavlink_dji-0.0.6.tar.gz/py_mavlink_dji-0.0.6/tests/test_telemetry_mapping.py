from py_mavlink_dji.djibindings import get_broadcast


def test_broadcast_schema():
    b = get_broadcast()
    assert "attitude" in b and "position" in b and "velocity" in b
    att = b["attitude"]
    assert all(k in att for k in ("q0", "q1", "q2", "q3"))
    pos = b["position"]
    assert all(k in pos for k in ("lat", "lon", "alt"))

