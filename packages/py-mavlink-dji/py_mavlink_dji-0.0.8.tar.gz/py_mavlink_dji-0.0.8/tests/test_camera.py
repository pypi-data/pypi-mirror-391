import os
import sys

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


def test_camera_controller_with_mock_backend():
    from py_mavlink_dji import CameraController
    from py_mavlink_dji.backend import MockBackend

    backend = MockBackend()
    cam = CameraController(backend)

    assert cam.is_recording() is False
    assert cam.start_recording() is True
    assert cam.is_recording() is True
    assert cam.stop_recording() is True
    assert cam.is_recording() is False
    assert cam.take_photo() is True


