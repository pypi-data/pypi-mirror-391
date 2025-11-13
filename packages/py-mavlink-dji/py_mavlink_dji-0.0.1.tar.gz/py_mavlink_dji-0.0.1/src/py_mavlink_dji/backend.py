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


