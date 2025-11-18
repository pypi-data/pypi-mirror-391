from typing import Any


class CameraController:
    """Simple camera abstraction that delegates to a HardwareBackend implementation.

    The controller keeps a small local recording state to make tests and callers
    easier to reason about; the authoritative state depends on the backend/SDK.
    """

    def __init__(self, backend: Any):
        self.backend = backend
        self._recording = False

    def start_recording(self) -> bool:
        """Start video recording via backend; returns True on success."""
        if hasattr(self.backend, "start_video_recording"):
            ok = bool(self.backend.start_video_recording())
            if ok:
                self._recording = True
            return ok
        raise NotImplementedError("Backend does not support start_video_recording")

    def stop_recording(self) -> bool:
        """Stop video recording via backend; returns True on success."""
        if hasattr(self.backend, "stop_video_recording"):
            ok = bool(self.backend.stop_video_recording())
            if ok:
                self._recording = False
            return ok
        raise NotImplementedError("Backend does not support stop_video_recording")

    def take_photo(self) -> bool:
        """Trigger a photo capture; returns True on success."""
        if hasattr(self.backend, "take_photo"):
            return bool(self.backend.take_photo())
        raise NotImplementedError("Backend does not support take_photo")

    def is_recording(self) -> bool:
        """Return the controller's recording flag (best-effort)."""
        return bool(self._recording)


