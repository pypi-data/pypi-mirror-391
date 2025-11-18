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

Notes on real DJI backend
- A `DJIOnboardBackend` wrapper was added that attempts to use a Python DJI SDK binding (import name `djisdk`). If you want to connect to real DJI hardware, install or provide a `djisdk` binding that exposes activation and broadcast APIs (or adapt `mavlink-dji-bridge/src/py_mavlink_dji/backend.py` to your binding). If the binding is not available, the CLI falls back to the prototype `PureDJIBackend` or the `--mock` backend.

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


