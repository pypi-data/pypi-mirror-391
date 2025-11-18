"""Lightweight Python shim for DJIBindings used in tests.

This package provides minimal functions expected by tests when the
compiled bindings are not available.
"""


def get_broadcast():
    """Return a minimal broadcast snapshot with expected keys for tests."""
    return {
        "attitude": {"q0": 1.0, "q1": 0.0, "q2": 0.0, "q3": 0.0},
        "position": {"lat": 0.0, "lon": 0.0, "alt": 0.0},
        "velocity": {"vx": 0.0, "vy": 0.0, "vz": 0.0},
        "rc": {},
        "battery": 100.0,
    }


def get_broadcast_normalized():
    """Return a normalized broadcast snapshot compatible with callers."""
    return get_broadcast()

