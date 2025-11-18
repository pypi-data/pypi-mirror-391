from setuptools import setup, Extension
import sys

def read_requirements():
    return []

try:
    import pybind11
    include_dirs = [pybind11.get_include()]
except Exception:
    include_dirs = []

import os

# Allow configuring DJI SDK include/lib paths via environment variables:
# DJI_SDK_INCLUDE -> additional include directories (colon-separated)
# DJI_SDK_LIB_DIR -> additional library directories (colon-separated)
# DJI_SDK_LIBS -> libraries to link (comma-separated)
extra_include_dirs = []
extra_library_dirs = []
libraries = []
extra_compile_args = ["-std=c++14"]

if "DJI_SDK_INCLUDE" in os.environ:
    extra_include_dirs += os.environ["DJI_SDK_INCLUDE"].split(":")
if "DJI_SDK_LIB_DIR" in os.environ:
    extra_library_dirs += os.environ["DJI_SDK_LIB_DIR"].split(":")
if "DJI_SDK_LIBS" in os.environ:
    libraries += [s.strip() for s in os.environ["DJI_SDK_LIBS"].split(",") if s.strip()]

# merge include dirs
all_include_dirs = include_dirs + extra_include_dirs
define_macros = []
if os.environ.get("DJI_SDK_ENABLED", "") == "1" or len(libraries) > 0:
    define_macros.append(("DJI_SDK_AVAILABLE", "1"))
# Determine correct source path for the optional C++ binding. The project
# historically used a flat layout but the package now lives under `src/`.
possible_source_paths = [
    "py_mavlink_dji/djibindings/bindings.cpp",
    "src/py_mavlink_dji/djibindings/bindings.cpp",
]
source_file = None
for p in possible_source_paths:
    if os.path.exists(p):
        source_file = p
        break

# If the C++ source is not present, skip building the extension so editable
# installs and CI that don't include compiled sources won't fail.
ext_modules = []
if source_file is None:
    # Avoid failing builds when the native binding source isn't included.
    print("C++ binding source not found; skipping extension build.")
else:
    ext_modules = [
        Extension(
            "py_mavlink_dji.djibindings._djibindings",
            [source_file],
            include_dirs=all_include_dirs,
            library_dirs=extra_library_dirs,
            libraries=libraries,
            extra_compile_args=extra_compile_args,
            define_macros=define_macros,
            language="c++",
        )
    ]

setup(
    name="py_mavlink_dji",
    version="0.0.3",
    description="MAVLink to DJI translator bridge (prototype)",
    ext_modules=ext_modules,
)


