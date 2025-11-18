# mavlink-dji-bridge — FULL GUIDE

Comprehensive guide to the mavlink-dji-bridge project: design, installation, usage, developer API, backends, testing, and troubleshooting.

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

Notes on real DJI backend
- A `DJIOnboardBackend` wrapper was added that attempts to use a Python DJI SDK binding (import name `djisdk`). If you want to connect to real DJI hardware, install or provide a `djisdk` binding that exposes activation and broadcast APIs (or adapt `mavlink-dji-bridge/src/py_mavlink_dji/backend.py` to your binding). If the binding is not available, the CLI falls back to the prototype `PureDJIBackend` or the `--mock` backend.

Camera API
----------

Camera and video control APIs are documented in `docs/camera.md`. See `py_mavlink_dji.camera.CameraController`
for high-level usage and `py_mavlink_dji.backend.HardwareBackend` for required backend methods (`start_video_recording`,
`stop_video_recording`, `take_photo`).

Building the native binding (Linux)
---------------------------------

This repository includes a small pybind11 scaffold for a native DJI binding. The scaffold exports basic functions and is optional.

Quick local build (recommended for Linux):

- Ensure build deps are installed (Ubuntu example):
  ```bash
  sudo apt-get update
  sudo apt-get install -y build-essential cmake
  ```
- Build with pip (installs pybind11 as part of the process):
  ```bash
  python -m pip install --upgrade pip setuptools wheel pybind11 build
  python -m build --wheel
  ```
- The wheel will appear in `dist/`. Install it via `pip install dist/your_wheel.whl`.

Configuring DJI SDK include/libs
--------------------------------

If you have the DJI Onboard SDK installed and want the binding to link against it, set environment variables before building:

- `DJI_SDK_INCLUDE` — colon-separated extra include directories (e.g. `/opt/dji/include`)
- `DJI_SDK_LIB_DIR` — colon-separated library directories (e.g. `/opt/dji/lib`)
- `DJI_SDK_LIBS` — comma-separated libraries to link (e.g. `djisdk,otherlib`)

Example:

```bash
export DJI_SDK_INCLUDE=/opt/dji/include
export DJI_SDK_LIB_DIR=/opt/dji/lib
export DJI_SDK_LIBS=djisdk
python -m build --wheel
```

CI
--

A GitHub Actions workflow `./github/workflows/build-linux.yml` is included to build wheels on `ubuntu-latest` for Python 3.9-3.11. It uploads built wheels as workflow artifacts.

Notes
-----
- The current C++ binding is a safe stub by default; replace stub implementations in `py_mavlink_dji/djibindings/bindings.cpp` with real SDK calls once the SDK and headers are available.
- If you prefer not to build native extensions, continue using the `PureDJIBackend` or `MockBackend`.

Enabling real DJI SDK linkage
-----------------------------

To compile the extension so it links against the real DJI SDK, set `DJI_SDK_ENABLED=1` (or provide `DJI_SDK_LIBS`) in the environment when building. Example:

```bash
export DJI_SDK_ENABLED=1
export DJI_SDK_INCLUDE=/opt/dji/include
export DJI_SDK_LIB_DIR=/opt/dji/lib
export DJI_SDK_LIBS=djisdk
python -m build --wheel
```

When `DJI_SDK_ENABLED=1` the C++ binding will compile with `DJI_SDK_AVAILABLE` defined and attempt to call SDK symbols. You must ensure the SDK headers and libraries provide the expected symbols (or adapt `bindings.cpp` to your SDK API).


## IMPORTANT: How this package uses the DJI Onboard SDK (READ CAREFULLY)

- **This package does NOT include DJI's Onboard SDK**. The native SDK is proprietary and must be installed separately by you or linked at build time. The Python package provides a *binding scaffold* and a safe prototype fallback so the package is usable for development without DJI hardware.

- **Two integration modes (choose one):**
  - **Build-time native binding (recommended for production)** — compile the pybind11 extension against the DJI SDK on your machine or in CI. Use the environment variables documented above (`DJI_SDK_ENABLED`, `DJI_SDK_INCLUDE`, `DJI_SDK_LIB_DIR`, `DJI_SDK_LIBS`) before running `python -m build` or `pip install .[djibindings]`. This produces a compiled extension (`py_mavlink_dji.djibindings._djibindings`) that the package will prefer at runtime.
  - **Runtime Python binding or subprocess (optional)** — install a separate Python binding package (an importable module named `djisdk`) or run a helper subprocess that links the DJI SDK and exposes a simple JSON/UDP API. If `djisdk` is importable, `DJIOnboardBackend` will use it.

- **Autodetection behavior (runtime):**
  - At runtime the package attempts the following (in order) when choosing a hardware backend:
    1. If the compiled extension `py_mavlink_dji.djibindings._djibindings` is importable, it is used. You can check with:
       ```bash
       python -c "import py_mavlink_dji.djibindings as d; print(bool(getattr(d, '_core', None)))"
       ```
    2. Otherwise the package tries to import a Python SDK binding named `djisdk` (so `import djisdk` must succeed).
    3. If neither the compiled extension nor `djisdk` are available, the CLI/application falls back to the safe prototype backends: `PureDJIBackend` or `MockBackend`. These are for development/testing only and do NOT control real DJI hardware.

- **Safety & development guidance**
  - Always test first in `--mock` mode or using `MockBackend` before attempting hardware builds or flight.
  - Never store activation keys or credentials in the repository. Use environment variables or an encrypted secrets store for CI.
  - If you build the native binding locally, run the simple import test shown above before starting the bridge.

## Publishing & PyPI notes

- If you intend to publish to PyPI, DO NOT bundle DJI SDK binaries or headers in your wheel. Instead:
  - Publish pure-Python wheels that work with the prototype backends (these are safe and hardware-free), and separately publish platform-specific wheels that include the compiled binding only if your CI can legally and technically link the DJI SDK on that runner.
  - Recommended: use `cibuildwheel` to build manylinux/macos/windows wheels and upload them to GitHub Releases or PyPI. For wheels that link the DJI SDK, ensure licensing allows automated linking on the CI runner and that required SDK artifacts are available to the build (often not possible for proprietary SDKs).

- For users, the simplest install paths are:
  - Development (no SDK): `pip install .` — uses prototype backends.
  - Development with compiled binding (Linux): set env vars, then `python -m build --wheel` and `pip install dist/*.whl`.
  - Production (recommended): install a wheel built on a controlled CI environment that was linked against the appropriate SDK.

## Troubleshooting checklist

- If the bridge falls back to prototype mode unexpectedly:
  1. Confirm compiled binding is importable:
     ```bash
     python -c "import py_mavlink_dji.djibindings as d; print(getattr(d, '_core', None))"
     ```
  2. If it's `None`, check that you built the extension with `DJI_SDK_ENABLED=1` and correct `DJI_SDK_INCLUDE`/`DJI_SDK_LIB_DIR`/`DJI_SDK_LIBS`.
  3. Check the CLI startup output: it prints which backend was selected.

- If you need a no-build option for production (avoid compiling on user machines), consider the subprocess helper approach — contact the maintainers or request that option and we can add a packaged helper.

## Summary (one-liner)
- The package is a normal Python package installable with pip; to control real DJI hardware you must either install a Python SDK binding named `djisdk` or build the compiled pybind11 extension against DJI's SDK (env-vars + build). Otherwise the package runs in safe prototype/mock mode suitable for development and CI.

## Developer reference (expanded)

The following sections expand the quick overview above with concrete developer-focused details, API surface, and actionable examples.

### API & internals (detailed)

Bridge
- Location: `src/py_mavlink_dji/adapter.py`
- Purpose: central routing between incoming MAVLink messages and the configured backend. Holds:
  - `self.backend` — instance of `HardwareBackend`
  - `self.state` — `SharedState` instance with telemetry and SDK flags
  - `self.commands` — `Commands` wrapper providing safe, queued command execution
  - `self.mission_mgr` — `MissionManager` for mission uploads/execution state
- Lifecycle:
  - `start()` attempts to obtain control authority and start backend polling when available
  - `stop()` releases authority and stops backend resources
  - `_handle(msg)` receives parsed MAVLink messages and maps them into actions (takeoff/land/RTH, mission items, velocity messages). This function now contains the routing logic used by tests and quick integrations.

Commands & SafetyController
- Location: `src/py_mavlink_dji/commands.py`
- `Commands` provides a small command queue and avoids overlap by:
  - Using an internal `_cmd_send_flag` and `_cmd_queue`
  - Calling `backend` methods via `_enqueue_or_send(...)`
  - Expecting backends to register command ack callbacks via `set_cmd_send_cb(cb)` and forward ack tokens to `Commands.notify_cmd_status(cmd_id, status_str)` so the queue can proceed.
- `SafetyController` enforces:
  - Battery preflight thresholds (blocks takeoff)
  - Geofence center/radius and altitude bounds
  - Velocity and altitude delta validations
  - Emergency stop / failsafe behavior (allow recovery-only actions such as landing/RTH)

Motion controls
- Location: `src/py_mavlink_dji/motion_controls.py`
- Helpers:
  - `fly_to_localpos(backend, x, y, z, safety=None)` — uses `set_velocity` if available otherwise falls back to `set_attitude`
  - `fly_to_globalpos(backend, lat, lon, alt, reference=None, safety=None)` — projects lat/lon deltas to local meters and calls `fly_to_localpos`
  - `set_velocity(backend, vx, vy, vz, frame="local", safety=None)` — validates velocity via safety then calls backend

Mission manager
- Location: `src/py_mavlink_dji/missions.py`
- API:
  - `start_upload(count, mission_id=0)` — prepares to receive `count` mission items
  - `receive_item(item, mission_id=0)` — append item and returns `done` boolean when upload complete
  - `begin_fly(mission_id=0, start_seq=0)` — set mission running and call backend `start_mission` if present

Transport
- Location: `src/py_mavlink_dji/transport.py`
- `UDPTransport` and `SerialTransport` provide simple send/receive primitives consumed by `PureDJIBackend`.

### Examples (expanded)

Programmatic bridge with mock backend

```python
from py_mavlink_dji.adapter import Bridge
from py_mavlink_dji.backend import MockBackend

backend = MockBackend()
bridge = Bridge(source_uri="udp:0.0.0.0:14550", backend=backend)
bridge.activate_backend()   # optional activation step
bridge.start()
bridge.commands.takeoff()
bridge.commands.land()
bridge.stop()
```

Send a velocity command via MAVLink parsing (adapter flow)

1. Ensure your MAVLink handler exposes a message object with `get_type()` returning `SET_POSITION_TARGET_LOCAL_NED` or a similar type and with `vx`, `vy`, `vz` attributes.
2. The adapter will extract velocities and enqueue a `set_velocity` call to the backend respecting safety checks.

Manual enqueue (direct)

```python
bridge.commands._enqueue_or_send(lambda: backend.set_velocity(2.0, 0.0, 0.0, frame="local"))
```

Mission upload (programmatic)

```python
items = [{"seq": 0, "x": 37.0, "y": -122.0, "z": 30.0, "command": 16}]
bridge.mission_mgr.start_upload(len(items), mission_id=0)
for it in items:
    bridge.mission_mgr.receive_item(it, mission_id=0)
bridge.backend.upload_mission(bridge.mission_mgr.missions[0])
```

### Command ack / backend responsibilities

- Backends that speak to real SDKs should:
  - Implement `set_cmd_send_cb(cb)` so the adapter can register `Commands.notify_cmd_status`.
  - When SDK reports command lifecycle events, call the stored callback with `(cmd_id, status_str)` where `status_str` matches tokens documented in `docs/commands.md`.
  - Use terminal tokens (`STATUS_CMD_EXE_SUCCESS`, `STATUS_CMD_EXE_FAIL`, `REQ_TIME_OUT`, `REQ_REFUSE`) to allow queued commands to progress.

### Testing

- Unit tests are in `tests/`. Use `pytest -q` to run the suite locally.
- For creating new tests:
  - Prefer `MockBackend` or small recorder backends that assert calls.
  - Keep tests deterministic; do not rely on real hardware.

### Roadmap and suggested next work

- Precise `SET_POSITION_TARGET_*` parsing: read `type_mask` and honor which fields are present (position vs velocity vs acceleration).
- Implement `MAV_CMD_DO_CHANGE_SPEED` (MAV command 178) mapping to backend speed controls or throttle adjustments.
- Add integration tests with a subprocess helper that bridges to a compiled DJI binding or hardware emulator.

If you want, I will:

- Split this README into `docs/` pages and add a navigable index.
- Add concrete code snippets for `type_mask` parsing and a unit test demonstrating velocity mapping.

