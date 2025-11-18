# mavlink-dji-bridge

Lightweight MAVLink ↔ DJI bridge (prototype)

Overview
- Receive MAVLink commands (e.g., TAKEOFF, LAND, MISSION uploads) and translate to DJI actions.
- Emit MAVLink telemetry from the DJI state.
- Pure-Python prototype: `pymavlink`, `pyserial` optional.

Quickstart
1. Install:
   pip install pymavlink pyserial
2. Run in mock mode:
   python -m py_mavlink_dji.cli --mock
3. Configure with TOML:
   Create `config.toml` and run:
   python -m py_mavlink_dji.cli --config config.toml

Notes
- This is a prototype. See `README.md` for limitations and to-dos.


