"""
High-level command wrappers that call into a backend implementation.
These mirror the dji_commands.cpp behavior at a high level.
"""
 
class Commands:
    def __init__(self, backend):
        self.backend = backend

    def takeoff(self):
        """Initiate takeoff via backend."""
        return self.backend.takeoff()

    def land(self):
        """Initiate landing via backend."""
        return self.backend.land()

    def return_to_home(self):
        """Initiate return-to-home via backend."""
        return self.backend.return_to_home()

    def pause_mission(self):
        return self.backend.pause_mission()

    def upload_mission(self, mission_items):
        return self.backend.upload_mission(mission_items)

    def start_mission(self, mission_id=0, start_seq=0):
        return getattr(self.backend, "start_mission", lambda *_: False)(mission_id, start_seq)

    def gimbal_control(self, pitch=0, roll=0, yaw=0):
        return getattr(self.backend, "gimbal_control", lambda *_: False)(pitch, roll, yaw)

    def set_rc_override(self, channels):
        return getattr(self.backend, "set_rc_override", lambda *_: False)(channels)


