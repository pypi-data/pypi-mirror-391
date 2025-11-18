"""
Mission manager: handles mission uploads (MISSION_COUNT/REQUEST/ITEM/ACK)
and provides a simple execution state machine.
"""
from typing import List, Dict
import threading


class MissionItem(dict):
    pass


class MissionManager:
    def __init__(self, backend=None):
        # missions keyed by mission_id (support single default mission 0)
        self.missions: Dict[int, List[MissionItem]] = {0: []}
        self.lock = threading.Lock()
        self.waypoint_ptr = 0
        self.mission_id = 0
        self.state = "standby"  # standby, flying, paused
        # optional backend that will execute missions
        self.backend = backend

        # upload handshake helpers
        self._upload_expected = 0
        self._upload_received = 0

    def clear_mission(self, mission_id=0):
        with self.lock:
            self.missions[mission_id] = []
            self._upload_expected = 0
            self._upload_received = 0

    def start_upload(self, count, mission_id=0):
        with self.lock:
            self._upload_expected = count
            self._upload_received = 0
            self.missions[mission_id] = []
            return True

    def receive_item(self, item: MissionItem, mission_id=0):
        with self.lock:
            # simple append; ensure sequence order by seq if provided
            self.missions[mission_id].append(item)
            self._upload_received += 1
            done = (self._upload_received >= self._upload_expected)
            return done

    def request_next_seq(self):
        with self.lock:
            return self._upload_received

    def begin_fly(self, mission_id=0, start_seq=0):
        with self.lock:
            if mission_id not in self.missions or start_seq >= len(self.missions[mission_id]):
                return False
            self.mission_id = mission_id
            self.waypoint_ptr = start_seq
            self.state = "flying"
            # if backend supports starting mission, notify it
            try:
                if self.backend and hasattr(self.backend, "start_mission"):
                    self.backend.start_mission(mission_id, start_seq)
            except Exception:
                pass
            return True

    def pause(self):
        with self.lock:
            if self.state == "flying":
                self.state = "paused"
                return True
            return False

    def resume(self):
        with self.lock:
            if self.state == "paused":
                self.state = "flying"
                return True
            return False

    def loop_step(self):
        """Should be called periodically to advance missions when appropriate."""
        with self.lock:
            if self.state != "flying":
                return
            mission = self.missions.get(self.mission_id, [])
            if not mission or self.waypoint_ptr >= len(mission):
                self.state = "standby"
                return
            # for prototype, we just advance pointer (no real movement)
            self.waypoint_ptr += 1
            if self.waypoint_ptr >= len(mission):
                self.state = "standby"


