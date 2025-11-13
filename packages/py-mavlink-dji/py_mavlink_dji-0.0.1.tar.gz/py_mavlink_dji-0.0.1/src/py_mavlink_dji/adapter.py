import threading
from pymavlink import mavutil

from .backend import MockBackend


class Bridge:
    """Simple MAVLink -> DJI bridge.

    Example:
        from py_mavlink_dji import Bridge, MockBackend
        b = Bridge(source_uri='udp:0.0.0.0:14550', backend=MockBackend())
        b.start()
    """
    def __init__(self, source_uri="udp:0.0.0.0:14550", backend=None):
        self.source_uri = source_uri
        self.mav = mavutil.mavlink_connection(source_uri)
        self.backend = backend or MockBackend()
        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

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
                # keep loop alive; backend should handle errors
                print("Bridge: handler error:", e)

    def _handle(self, msg):
        t = msg.get_type()
        # COMMAND_LONG -> high level commands like TAKEOFF/LAND
        if t == "COMMAND_LONG":
            cmd = msg.command
            if cmd == mavutil.mavlink.MAV_CMD_NAV_TAKEOFF:
                self.backend.takeoff()
            elif cmd == mavutil.mavlink.MAV_CMD_NAV_LAND:
                self.backend.land()
            elif cmd == mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH:
                self.backend.return_to_home()
            else:
                print("Bridge: unhandled COMMAND_LONG", cmd)
        # MISSION_ITEM -> waypoint uploaded from GCS
        elif t in ("MISSION_ITEM", "MISSION_ITEM_INT"):
            # build a simple waypoint dict
            wp = {
                "seq": getattr(msg, "seq", None),
                "x": getattr(msg, "x", None),
                "y": getattr(msg, "y", None),
                "z": getattr(msg, "z", None),
                "command": getattr(msg, "command", None),
            }
            # delegate to backend (real backend should collect sequence)
            self.backend.upload_mission([wp])
        elif t == "MISSION_COUNT":
            # initial mission upload start - client should request items
            print("Bridge: MISSION_COUNT received")
        else:
            # ignore other message types by default
            pass


