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
    def start_video_recording(self):
        """Begin video recording if supported by the backend / SDK."""
        raise NotImplementedError

    def stop_video_recording(self):
        """Stop video recording if supported by the backend / SDK."""
        raise NotImplementedError

    def take_photo(self):
        """Take a single photo / trigger camera capture on the backend / SDK."""
        raise NotImplementedError

    def set_rc_override(self, channels):
        raise NotImplementedError
    def set_attitude(self, roll, pitch, yaw, thrust, ctrl_flag=None):
        raise NotImplementedError

    def set_velocity(self, vx, vy, vz, frame="local"):
        raise NotImplementedError

    def control_management(self, obtain=True):
        """Request or release control authority."""
        raise NotImplementedError
    # Optional lifecycle hooks for real backends
    def activate(self, app_id=None, app_key=None, api_level=None):
        """Activate the DJI SDK / app. Optional for mock backends."""
        raise NotImplementedError

    def start_polling(self, state_update_cb=None, interval=0.02):
        """Start polling / receiving broadcast telemetry and call state_update_cb(snapshot)."""
        raise NotImplementedError

    def stop(self):
        """Stop any background threads / resources used by the backend."""
        raise NotImplementedError
    def start_mission(self, mission_id=0, start_seq=0):
        """Begin executing a previously uploaded mission (if supported)."""
        raise NotImplementedError

    # --- Command ACK callback registration --------------------------------
    def set_cmd_send_cb(self, cb):
        """Register a callback to receive SDK-level command ack events.

        The callback signature is expected to be: cb(cmd_id, status_str)
        where `cmd_id` is an integer command identifier and `status_str` is one
        of the status tokens documented in the project TODO (e.g. 'CMD_RECIEVE',
        'STATUS_CMD_EXE_SUCCESS', etc).
        """
        # Default implementation stores callback for backends that want to
        # invoke it later via self._invoke_cmd_send_cb.
        setattr(self, "_cmd_send_cb", cb)
        return True

    def _invoke_cmd_send_cb(self, cmd_id, status_str):
        """Internal helper for backends to call the registered callback."""
        cb = getattr(self, "_cmd_send_cb", None)
        try:
            if cb:
                cb(cmd_id, status_str)
                return True
        except Exception:
            pass
        return False


class MockBackend(HardwareBackend):
    """Simple mock backend used for development and tests."""
    def __init__(self):
        self._has_control = False

    def takeoff(self):
        print("[MockBackend] takeoff() called")
        # simulate immediate SDK ack if requested
        try:
            # prefer MAV_CMD_NAV_TAKEOFF constant if available
            cmd = getattr(self, "_last_cmd_id", None)
            if cmd is None:
                # common default
                cmd = 1
            self._invoke_cmd_send_cb(cmd, "CMD_RECIEVE")
            self._invoke_cmd_send_cb(cmd, "STATUS_CMD_EXECUTING")
            self._invoke_cmd_send_cb(cmd, "STATUS_CMD_EXE_SUCCESS")
        except Exception:
            pass

    def land(self):
        print("[MockBackend] land() called")
        try:
            cmd = getattr(self, "_last_cmd_id", None) or 2
            self._invoke_cmd_send_cb(cmd, "CMD_RECIEVE")
            self._invoke_cmd_send_cb(cmd, "STATUS_CMD_EXECUTING")
            self._invoke_cmd_send_cb(cmd, "STATUS_CMD_EXE_SUCCESS")
        except Exception:
            pass

    def return_to_home(self):
        print("[MockBackend] return_to_home() called")
        try:
            cmd = getattr(self, "_last_cmd_id", None) or 3
            self._invoke_cmd_send_cb(cmd, "CMD_RECIEVE")
            self._invoke_cmd_send_cb(cmd, "STATUS_CMD_EXECUTING")
            self._invoke_cmd_send_cb(cmd, "STATUS_CMD_EXE_SUCCESS")
        except Exception:
            pass

    def upload_mission(self, mission_items):
        print(f"[MockBackend] upload_mission() {len(mission_items)} items")
        for i, m in enumerate(mission_items):
            print(f"  {i}: {m}")

    def pause_mission(self):
        print("[MockBackend] pause_mission() called")

    def start_video_recording(self):
        print("[MockBackend] start_video_recording() called")
        return True

    def stop_video_recording(self):
        print("[MockBackend] stop_video_recording() called")
        return True

    def take_photo(self):
        print("[MockBackend] take_photo() called")
        return True

    def activate(self, app_id=None, app_key=None, api_level=None):
        print("[MockBackend] activate() called")

    def start_polling(self, state_update_cb=None, interval=0.02):
        # MockBackend doesn't produce live telemetry; no-op
        print("[MockBackend] start_polling() called (no-op)")

    def stop(self):
        print("[MockBackend] stop() called (no-op)")
    def start_mission(self, mission_id=0, start_seq=0):
        print(f"[MockBackend] start_mission(mission_id={mission_id}, start_seq={start_seq})")
        return True
    def set_attitude(self, roll, pitch, yaw, thrust, ctrl_flag=None):
        print(
            f"[MockBackend] set_attitude roll={roll} pitch={pitch} yaw={yaw} thrust={thrust} ctrl_flag={ctrl_flag}"
        )
        return True

    def set_velocity(self, vx, vy, vz, frame="local"):
        print(f"[MockBackend] set_velocity vx={vx} vy={vy} vz={vz} frame={frame}")
        return True

    def control_management(self, obtain=True):
        self._has_control = bool(obtain)
        state = "obtained" if self._has_control else "released"
        print(f"[MockBackend] control_management -> {state}")
        return True

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
        # polling is not implemented for the prototype; state updates must be pushed externally
        self._state_polling = False

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
    def activate(self, app_id=None, app_key=None, api_level=None):
        # Prototype does not support real activation
        print("[PureDJIBackend] activate() called (prototype no-op)")

    def start_polling(self, state_update_cb=None, interval=0.02):
        # Prototype backend has no SDK broadcast; leave as no-op
        print("[PureDJIBackend] start_polling() called (no-op)")
    def start_mission(self, mission_id=0, start_seq=0):
        print(f"[PureDJIBackend] start_mission(mission_id={mission_id}, start_seq={start_seq}) (no-op)")
    def set_attitude(self, roll, pitch, yaw, thrust, ctrl_flag=None):
        try:
            payload = f"ATT|{roll}|{pitch}|{yaw}|{thrust}|{ctrl_flag}".encode()
            self._send_cmd("ATTITUDE", payload)
            return True
        except Exception:
            return False

    def set_velocity(self, vx, vy, vz, frame="local"):
        try:
            payload = f"VEL|{vx}|{vy}|{vz}|{frame}".encode()
            self._send_cmd("VELOCITY", payload)
            return True
        except Exception:
            return False

    def control_management(self, obtain=True):
        print("[PureDJIBackend] control_management() called (prototype no-op)")
        return False
    def takeoff(self):
        """Prototype takeoff: send TAKEOFF command via codec/transport."""
        try:
            self._send_cmd("TAKEOFF")
            return True
        except Exception:
            return False

    def land(self):
        """Prototype land: send LAND command via codec/transport."""
        try:
            self._send_cmd("LAND")
            return True
        except Exception:
            return False

    def return_to_home(self):
        """Prototype RTH: send RTH command via codec/transport."""
        try:
            self._send_cmd("RTH")
            return True
        except Exception:
            return False

    def upload_mission(self, mission_items):
        """Send a simple mission upload sequence over the prototype transport."""
        try:
            for item in mission_items:
                payload = f'{item.get("seq")}|{item.get("x")}|{item.get("y")}|{item.get("z")}'.encode()
                self._send_cmd("MISSION_ITEM", payload)
            return True
        except Exception:
            return False

    def pause_mission(self):
        try:
            self._send_cmd("PAUSE_MISSION")
            return True
        except Exception:
            return False

    def gimbal_control(self, pitch=0, roll=0, yaw=0):
        try:
            payload = f"{pitch}|{roll}|{yaw}".encode()
            self._send_cmd("GIMBAL", payload)
            return True
        except Exception:
            return False

    def start_video_recording(self):
        try:
            self._send_cmd("START_VIDEO")
            return True
        except Exception:
            return False

    def stop_video_recording(self):
        try:
            self._send_cmd("STOP_VIDEO")
            return True
        except Exception:
            return False

    def take_photo(self):
        try:
            self._send_cmd("TAKE_PHOTO")
            return True
        except Exception:
            return False

    def set_rc_override(self, channels):
        try:
            payload = "|".join(f"{k}:{v}" for k, v in channels.items()).encode()
            self._send_cmd("RC_OVERRIDE", payload)
            return True
        except Exception:
            return False


class DJIOnboardBackend(HardwareBackend):
    """
    Wrapper for a real DJI Onboard SDK binding. This class expects a Python
    binding named `djisdk` (or similar) to be available. If not present,
    the constructor will raise so callers can fallback to the prototype backend.
    """
    def __init__(self, binding_module: str = "py_mavlink_dji.djibindings"):
        # Lazy import to allow the package to remain optional
        try:
            self._sdk = __import__(binding_module)
        except Exception as e:
            raise RuntimeError(f"DJI SDK bindings '{binding_module}' not available: {e}")
        if getattr(self._sdk, "USING_FALLBACK", False):
            raise RuntimeError(
                "DJI SDK bindings fallback in use; install native module 'py_mavlink_dji.djibindings._djibindings'"
            )
        self._poll_thread = None
        self._running = False
        self._state_cb = None
        # timestamp of last broadcast received from SDK (for watchdog)
        self._last_broadcast = time.time()
        # optional SDK handles
        self._handle = None

    def activate(self, app_id=None, app_key=None, api_level=None):
        """Activate via the underlying SDK binding if supported."""
        try:
            if hasattr(self._sdk, "activate"):
                return self._sdk.activate(app_id=app_id, app_key=app_key, api_level=api_level)
        except Exception:
            pass
        # best-effort success
        return True

    def start_polling(self, state_update_cb=None, interval=0.02):
        """Start a thread that polls SDK broadcast data and calls state_update_cb(snapshot)."""
        if state_update_cb is None:
            raise ValueError("state_update_cb is required for DJIOnboardBackend.start_polling")
        self._state_cb = state_update_cb
        self._running = True
        def _loop():
            while self._running:
                try:
                    # SDK may expose a method to read broadcast telemetry
                    if hasattr(self._sdk, "get_broadcast"):
                        data = self._sdk.get_broadcast()
                        # Expect data to be a dict-like with keys similar to SharedState
                        try:
                            # update last seen timestamp then call state callback
                            try:
                                self._last_broadcast = time.time()
                            except Exception:
                                pass
                            self._state_cb(data)
                        except Exception:
                            pass
                except Exception:
                    # swallow SDK errors to keep polling alive
                    pass
                time.sleep(interval)
        self._poll_thread = threading.Thread(target=_loop, daemon=True)
        self._poll_thread.start()
        return True

    def stop(self):
        self._running = False
        try:
            if self._poll_thread:
                self._poll_thread.join(timeout=1.0)
        except Exception:
            pass

    def health_check(self, timeout: float = 2.0) -> bool:
        """Return True if backend has reported broadcast data within `timeout` seconds."""
        try:
            return (time.time() - float(getattr(self, "_last_broadcast", 0.0))) < float(timeout)
        except Exception:
            return False

    # Basic control wrappers — delegate to SDK if available
    def takeoff(self):
        if hasattr(self._sdk, "takeoff"):
            return self._sdk.takeoff()
        return False

    def land(self):
        if hasattr(self._sdk, "land"):
            return self._sdk.land()
        return False

    def return_to_home(self):
        if hasattr(self._sdk, "return_to_home"):
            return self._sdk.return_to_home()
        return False

    def upload_mission(self, mission_items):
        if hasattr(self._sdk, "upload_mission"):
            return self._sdk.upload_mission(mission_items)
        return False

    def pause_mission(self):
        if hasattr(self._sdk, "pause_mission"):
            return self._sdk.pause_mission()
        return False

    def gimbal_control(self, pitch=0, roll=0, yaw=0):
        if hasattr(self._sdk, "gimbal_control"):
            return self._sdk.gimbal_control(pitch=pitch, roll=roll, yaw=yaw)
        return False

    def set_rc_override(self, channels):
        if hasattr(self._sdk, "set_rc_override"):
            return self._sdk.set_rc_override(channels)
        return False
    def start_mission(self, mission_id=0, start_seq=0):
        if hasattr(self._sdk, "start_mission"):
            return self._sdk.start_mission(mission_id=mission_id, start_seq=start_seq)
        return False
    def set_attitude(self, roll, pitch, yaw, thrust, ctrl_flag=None):
        if hasattr(self._sdk, "set_attitude"):
            try:
                if ctrl_flag is not None:
                    return self._sdk.set_attitude(roll=roll, pitch=pitch, yaw=yaw, thrust=thrust, ctrl_flag=ctrl_flag)
                return self._sdk.set_attitude(roll=roll, pitch=pitch, yaw=yaw, thrust=thrust)
            except Exception:
                return False
        return False

    def set_velocity(self, vx, vy, vz, frame="local"):
        if hasattr(self._sdk, "set_velocity"):
            try:
                return self._sdk.set_velocity(vx=vx, vy=vy, vz=vz, frame=frame)
            except Exception:
                return False
        return False

    def control_management(self, obtain=True):
        if hasattr(self._sdk, "control_management"):
            try:
                return self._sdk.control_management(obtain=obtain)
            except Exception:
                return False
        return False
    def start_video_recording(self):
        if hasattr(self._sdk, "start_video_recording"):
            try:
                return self._sdk.start_video_recording()
            except Exception:
                return False
        return False

    def stop_video_recording(self):
        if hasattr(self._sdk, "stop_video_recording"):
            try:
                return self._sdk.stop_video_recording()
            except Exception:
                return False
        return False

    def take_photo(self):
        if hasattr(self._sdk, "take_photo"):
            try:
                return self._sdk.take_photo()
            except Exception:
                return False
        return False
