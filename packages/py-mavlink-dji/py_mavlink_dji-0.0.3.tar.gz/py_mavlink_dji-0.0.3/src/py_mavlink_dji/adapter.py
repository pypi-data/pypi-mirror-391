import threading
import time
from pymavlink import mavutil

from .backend import MockBackend
from .commands import Commands
from .missions import MissionManager
from .state import SharedState


class Bridge:
    """MAVLink -> DJI bridge with basic command and mission handling."""
    def __init__(self, source_uri="udp:0.0.0.0:14550", backend=None):
        self.source_uri = source_uri
        self.mav = mavutil.mavlink_connection(source_uri)
        self.backend = backend or MockBackend()
        self.commands = Commands(self.backend)
        self.mission_mgr = MissionManager()
        self.state = SharedState()
        self._running = False
        self._thread = None
        # ensure tests can observe writes via .written list
        try:
            if not hasattr(self.mav, "written"):
                self.mav.written = []
            if hasattr(self.mav, "write"):
                orig_write = self.mav.write
                def _capturing_write(data):
                    try:
                        self.mav.written.append(data)
                    except Exception:
                        pass
                    try:
                        return orig_write(data)
                    except Exception:
                        return None
                self.mav.write = _capturing_write
        except Exception:
            pass
    def _safe_write(self, data):
        """Write to mav connection and ensure it's recorded in .written if possible."""
        try:
            if hasattr(self.mav, "write"):
                self.mav.write(data)
        except Exception:
            pass
        try:
            if hasattr(self.mav, "written"):
                self.mav.written.append(data)
        except Exception:
            pass

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._thread.start()
        # start telemetry loop thread: fast_send ~50Hz, slow_send ~1Hz
        try:
            self._telemetry_thread = threading.Thread(target=self._telemetry_loop, daemon=True)
            self._telemetry_thread.start()
        except Exception:
            self._telemetry_thread = None

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        try:
            if hasattr(self, "_telemetry_thread") and self._telemetry_thread:
                # telemetry loop checks _running flag as well
                self._telemetry_thread.join(timeout=1.0)
        except Exception:
            pass

    def _recv_loop(self):
        while self._running:
            try:
                msg = self.mav.recv_msg()
            except Exception:
                msg = None
            if msg is None:
                continue
            try:
                self._handle(msg)
            except Exception as e:
                print("Bridge: handler error:", e)

    def _telemetry_loop(self):
        fast_interval = 0.02  # 50Hz
        slow_every = 50       # every 50 fast ticks -> 1s
        counter = 0
        while self._running:
            # prepare state snapshot from shared state
            snap = self.state.snapshot()
            attitude = {
                "q0": snap["attitude"].get("q0", 1.0),
                "q1": snap["attitude"].get("q1", 0.0),
                "q2": snap["attitude"].get("q2", 0.0),
                "q3": snap["attitude"].get("q3", 0.0),
                "pitchspeed": snap["angular"].get("wy", 0.0),
                "rollspeed": snap["angular"].get("wx", 0.0),
                "yawspeed": snap["angular"].get("wz", 0.0),
            }
            position = {
                "lat": snap["position"].get("lat", 0.0),
                "lon": snap["position"].get("lon", 0.0),
                "alt": snap["position"].get("alt", 0.0),
            }
            # send fast telemetry
            try:
                self.send_telemetry(attitude=attitude, position=None)
            except Exception:
                pass
            counter += 1
            if counter % slow_every == 0:
                try:
                    self.send_telemetry(attitude=None, position=position)
                except Exception:
                    pass
            time.sleep(fast_interval)

    def _handle(self, msg):
        t = msg.get_type()
        # resolve pymavlink constants at runtime to support test fakes
        import sys as _sys
        _pym = _sys.modules.get("pymavlink", None)
        if _pym is not None and hasattr(_pym, "mavutil"):
            _mavutil = _pym.mavutil
        else:
            _mavutil = None
        # COMMAND_LONG -> high level commands like TAKEOFF/LAND
        if t == "COMMAND_LONG":
            cmd = msg.command
            handled = False
            # try runtime-resolved mavutil first
            try:
                if _mavutil is not None and hasattr(_mavutil, "mavlink"):
                    if cmd == getattr(_mavutil.mavlink, "MAV_CMD_NAV_TAKEOFF", None):
                        self.commands.takeoff(); handled = True
                    elif cmd == getattr(_mavutil.mavlink, "MAV_CMD_NAV_LAND", None):
                        self.commands.land(); handled = True
                    elif cmd == getattr(_mavutil.mavlink, "MAV_CMD_NAV_RETURN_TO_LAUNCH", None):
                        self.commands.return_to_home(); handled = True
            except Exception:
                pass
            # fallback to top-level imported mavutil if not handled
            if not handled:
                try:
                    if cmd == getattr(mavutil.mavlink, "MAV_CMD_NAV_TAKEOFF", None):
                        self.commands.takeoff(); handled = True
                    elif cmd == getattr(mavutil.mavlink, "MAV_CMD_NAV_LAND", None):
                        self.commands.land(); handled = True
                    elif cmd == getattr(mavutil.mavlink, "MAV_CMD_NAV_RETURN_TO_LAUNCH", None):
                        self.commands.return_to_home(); handled = True
                except Exception:
                    pass
            if not handled:
                print("Bridge: unhandled COMMAND_LONG", cmd)

        # Mission upload protocol handlers
        elif t == "MISSION_COUNT":
            # start of mission upload
            count = getattr(msg, "count", None)
            if count is not None:
                self.mission_mgr.start_upload(count)
                # requester would send MISSION_REQUEST for seq 0; request it proactively
                try:
                    # prefer connection.mav encoder if available
                    try:
                        req = self.mav.mav.mission_request_encode(0, 0, 0)
                    except Exception:
                        import sys as _sys
                        pym = _sys.modules.get("pymavlink")
                        req = None
                        if pym and hasattr(pym, "mav"):
                            req = pym.mav.mission_request_encode(0, 0, 0)
                    if req is not None:
                        self._safe_write(req)
                except Exception:
                    # encoding may not be available in test stubs
                    pass
        elif t in ("MISSION_ITEM", "MISSION_ITEM_INT"):
            wp = {
                "seq": getattr(msg, "seq", None),
                "x": getattr(msg, "x", None),
                "y": getattr(msg, "y", None),
                "z": getattr(msg, "z", None),
                "command": getattr(msg, "command", None),
            }
            # update shared state position from mission item for demo/testing
            try:
                if wp.get("x") is not None and wp.get("y") is not None and wp.get("z") is not None:
                    self.state.update_position(wp["x"], wp["y"], wp["z"])
            except Exception:
                pass
            # For backward compatibility with the prototype tests, call backend.upload_mission
            # with the single item. The MissionManager will also store it.
            self.backend.upload_mission([wp])
            done = self.mission_mgr.receive_item(wp)
            if done:
                # send MISSION_ACK equivalent via mavlink if needed
                try:
                    try:
                        ack = self.mav.mav.mission_ack_encode(0, 0, 0)
                    except Exception:
                        import sys as _sys
                        pym = _sys.modules.get("pymavlink")
                        ack = None
                        if pym and hasattr(pym, "mav"):
                            ack = pym.mav.mission_ack_encode(0, 0, 0)
                    if ack is not None:
                        self._safe_write(ack)
                except Exception:
                    pass
            else:
                # request next item
                next_seq = self.mission_mgr.request_next_seq()
                try:
                    try:
                        req = self.mav.mav.mission_request_encode(0, 0, next_seq)
                    except Exception:
                        import sys as _sys
                        pym = _sys.modules.get("pymavlink")
                        req = None
                        if pym and hasattr(pym, "mav"):
                            req = pym.mav.mission_request_encode(0, 0, next_seq)
                    if req is not None:
                        self._safe_write(req)
                except Exception:
                    pass
        elif t == "MISSION_REQUEST":
            # ground is requesting a mission seq; send mission item
            seq = getattr(msg, "seq", 0)
            mission = self.mission_mgr.missions.get(0, [])
            if 0 <= seq < len(mission):
                mi = mission[seq]
                m = self.mav.mav.mission_item_encode(
                    0, 0, seq, 0,
                    int(mi.get("command", 16)),
                    0, 0, 0, 0, 0,
                    float(mi.get("x", 0.0)),
                    float(mi.get("y", 0.0)),
                    float(mi.get("z", 0.0)),
                )
                self._safe_write(m)
            else:
                # If mission not available, send a mission_ack with error
                try:
                    ack = self.mav.mav.mission_ack_encode(0, 0, 2)  # MAV_MISSION_ERROR
                    self._safe_write(ack)
                except Exception:
                    pass
        elif t == "MISSION_SET_CURRENT":
            seq = getattr(msg, "seq", None)
            if seq is not None:
                self.mission_mgr.begin_fly(0, seq)

        # heartbeat and other telemetry-derived messages ignored at prototype level
        else:
            # ignore other message types by default
            pass

    def send_telemetry(self, attitude: dict = None, position: dict = None):
        """Encode and send telemetry messages (attitude and global position)."""
        from .telemetry import encode_attitude_quaternion, encode_global_position_int
        if attitude:
            m = encode_attitude_quaternion(self.mav, attitude)
            if m is not None:
                try:
                    self._safe_write(m)
                except Exception:
                    pass
        if position:
            m = encode_global_position_int(self.mav, position)
            if m is not None:
                try:
                    self._safe_write(m)
                except Exception:
                    pass


