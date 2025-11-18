import threading
import time


class HardwareBackend:
    """Abstract backend that executes DJI actions. Implement this for real hardware."""
    def takeoff(self):
        raise NotImplementedError

    def land(self):
        raise NotImplementedError

    def return_to_home(self):
        raise NotImplementedError

    def upload_mission(self, mission_items):
        """Receive a list of mission item dicts"""
        raise NotImplementedError

    def pause_mission(self):
        raise NotImplementedError
    def gimbal_control(self, pitch=0, roll=0, yaw=0):
        raise NotImplementedError

    def set_rc_override(self, channels):
        raise NotImplementedError


class MockBackend(HardwareBackend):
    """Simple mock backend used for development and tests."""
    def takeoff(self):
        print("[MockBackend] takeoff() called")

    def land(self):
        print("[MockBackend] land() called")

    def return_to_home(self):
        print("[MockBackend] return_to_home() called")

    def upload_mission(self, mission_items):
        print(f"[MockBackend] upload_mission() {len(mission_items)} items")
        for i, m in enumerate(mission_items):
            print(f"  {i}: {m}")

    def pause_mission(self):
        print("[MockBackend] pause_mission() called")

class PureDJIBackend(HardwareBackend):
    """Prototype pure-Python backend that encodes simple DJI commands and sends them
    over a transport (UDP or serial) using the simple codec.
    This is a prototype and does not implement the real DJI Onboard SDK protocol.
    """
    def __init__(self, transport, codec):
        self.transport = transport
        self.codec = codec
        # optional receive handler
        if hasattr(self.transport, "on_recv"):
            self.transport.on_recv = self._on_recv
        try:
            self.transport.start_recv()
        except Exception:
            pass
        # start keepalive thread
        self._keepalive = True
        self._keep_thread = None
        try:
            self._keep_thread = threading.Thread(target=self._keepalive_loop, daemon=True)
            self._keep_thread.start()
        except Exception:
            self._keep_thread = None

    def _on_recv(self, data: bytes):
        # parse frames and handle responses (placeholder)
        name, payload = self.codec.parse_frame(data)
        print("[PureDJIBackend] recv:", name, payload)

    def _send_cmd(self, name: str, payload: bytes = b""):
        frame = self.codec.build_command(name, payload)
        self.transport.send(frame)

    def _keepalive_loop(self):
        while getattr(self, "_keepalive", False):
            try:
                self._send_cmd("KEEPALIVE")
            except Exception:
                pass
            time.sleep(1.0)

    def stop(self):
        try:
            self._keepalive = False
            if self._keep_thread:
                self._keep_thread.join(timeout=1.0)
        except Exception:
            pass

    def takeoff(self):
        self._send_cmd("TAKEOFF")
        return True

    def land(self):
        self._send_cmd("LAND")
        return True

    def return_to_home(self):
        self._send_cmd("RTH")
        return True

    def upload_mission(self, mission_items):
        # send a simple mission upload; in real implementation handshake is needed
        for item in mission_items:
            payload = f'{item.get("seq")}|{item.get("x")}|{item.get("y")}|{item.get("z")}'.encode()
            self._send_cmd("MISSION_ITEM", payload)
        return True

    def pause_mission(self):
        self._send_cmd("PAUSE_MISSION")
        return True

    def gimbal_control(self, pitch=0, roll=0, yaw=0):
        payload = f"{pitch}|{roll}|{yaw}".encode()
        self._send_cmd("GIMBAL", payload)
        return True

    def set_rc_override(self, channels):
        payload = "|".join(f"{k}:{v}" for k, v in channels.items()).encode()
        self._send_cmd("RC_OVERRIDE", payload)
        return True

