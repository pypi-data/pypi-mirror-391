"""
High-level command wrappers that call into a backend implementation.
These mirror the dji_commands.cpp behavior at a high level.
"""
from typing import Optional


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


