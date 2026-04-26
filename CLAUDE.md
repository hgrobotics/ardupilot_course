# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Authoritative references

This repo already ships extensive contributor and AI-agent docs. Read these first; do not duplicate or contradict them.

- `AGENTS.md` — full AI contribution rules (style, testing, commit format, what *not* to do). **Treat this as binding** for any code change.
- `BUILD.md` — Waf build system in depth (boards, groups, `--targets`, Docker, debugging).
- `.github/CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md` — PR expectations.
- `Tools/CodeStyle/astylerc` — canonical C++ formatting.

## Big-picture architecture

ArduPilot is a multi-vehicle autopilot. The top level is structured as **vehicles + shared libraries + a hardware abstraction layer**:

- **Vehicle dirs** (`ArduCopter/`, `ArduPlane/`, `ArduSub/`, `Rover/`, `AntennaTracker/`, `Blimp/`) — each contains a main vehicle class inheriting from `AP_Vehicle`, mode implementations (`mode_*.cpp`), `Parameters.cpp/.h`, a `GCS_*` MAVLink interface, and a `wscript` declaring required libraries. Vehicle code is the orchestrator; it should stay thin and call into libraries.
- **`libraries/`** (~150 dirs) — the bulk of the codebase. Naming prefixes carry meaning:
  - `AP_*` — general ArduPilot libraries (sensors, peripherals, common services): `AP_GPS`, `AP_Baro`, `AP_AHRS`, `AP_Terrain`, etc.
  - `AC_*` — Copter-flavored controls and quadplane: `AC_PID`, `AC_WPNav`, `AC_AttitudeControl`.
  - `AR_*` — Rover-specific: `AR_Motors`, `AR_WPNav`.
  - Each library typically exposes a main class plus a `*_Backend` interface with concrete driver subclasses, a `*_config.h` of compile-time flags, and optional `tests/` and `examples/` subdirs.
- **HAL** — `libraries/AP_HAL/` defines the platform-independent interface. Concrete implementations live in `AP_HAL_ChibiOS/` (STM32 flight hardware), `AP_HAL_ESP32/`, `AP_HAL_Linux/` (Linux SBCs like Navio2), and `AP_HAL_SITL/` (the simulator). Shared libraries must go through HAL — never include platform headers directly. Use `AP_HAL::millis()` / `AP_HAL::micros()` for time, and `extern const AP_HAL::HAL& hal;` to reach hardware.
- **`libraries/GCS_MAVLink/`** + `modules/mavlink/` — telemetry / ground-station protocol, woven into every vehicle.
- **`libraries/SITL/`** — physics models for the simulator; SITL is the primary development target.
- **`Tools/autotest/`** — Python integration test framework that drives SITL through scripted flights (`arducopter.py`, `arduplane.py`, `rover.py`, `ardusub.py`, plus `vehicle_test_suite.py` as the base).
- **`Tools/AP_Periph/`** — separate firmware for CAN peripherals (compass nodes, GPS nodes, etc.).
- **`modules/`** — git submodules (ChibiOS, mavlink, gtest, waf, …). **Do not modify.**

Compile-time feature flags are pervasive (`#if AP_<FEATURE>_ENABLED`). Options are catalogued in `Tools/scripts/build_options.py`. A core, non-optional component must never depend on an optional one — the base build must succeed when optional features are disabled.

## Build & run

Build system is **Waf**. Always run `./waf` from the repo root and **never with `sudo`**.

```sh
# Configure once per board change
./waf configure --board sitl          # SITL = software-in-the-loop simulator (dev default)
./waf configure --board sitl --debug  # with debug symbols for gdb
./waf configure --board CubeBlack     # example flight-hardware target
./waf list_boards                     # see all supported boards

# Build a vehicle (after configure)
./waf copter      # also: plane, rover, sub, heli, antennatracker, blimp, AP_Periph
./waf             # build the default 'bin' group

# Build a single binary or test
./waf --targets bin/arducopter
./waf --targets tests/test_math

# Upload to a connected board (Pixhawk / Linux boards)
./waf --targets bin/arducopter --upload

# Clean
./waf clean        # current board only
./waf distclean    # everything, including configure state
```

Build artifacts land in `build/<board>/<group>/`. Incremental builds are fast — avoid `clean` unless needed.

`make <board>` and `make <board>-<vehicle>` (see `Makefile`) are thin wrappers over waf for convenience.

To use clang on Linux: `CXX=clang++ CC=clang ./waf configure --board=sitl`.

## Running and testing in SITL

```sh
# Start a simulated vehicle with MAVProxy attached (interactive dev)
Tools/autotest/sim_vehicle.py -v ArduCopter --console --map
Tools/autotest/sim_vehicle.py -v ArduPlane -f quadplane

# Run a specific autotest (rebuilds as needed)
Tools/autotest/autotest.py build.Copter test.Copter.RTLYaw

# Run all tests for a vehicle
Tools/autotest/autotest.py build.Copter test.Copter
```

Three testing layers exist:

1. **SITL autotest** (`Tools/autotest/`) — primary integration tests; scripted flights against simulated vehicles. Slow but high-fidelity.
2. **C++ unit tests** in `libraries/<lib>/tests/` using `#include <AP_gtest.h>`. Run via `./waf --targets tests/<name>` then `./build/sitl/tests/<name>`, or `./waf check` / `./waf check-all`.
3. **Python tests** in `Tools/autotest/unittest/` and `tests/` — run with `pytest`.

## Lint / format

- C++ style is enforced by **astyle** with `Tools/CodeStyle/astylerc` (4-space indent, K&R braces, LF endings, `#pragma once` over include guards). Format only the lines you change — do not reformat untouched code; it breaks `git blame`.
- Python files opted into linting carry the marker comment `AP_FLAKE8_CLEAN`. New Python files should add it. Config: `.flake8` (max line 127), `pyproject.toml` (ruff, isort, black). `black` (line 120) only applies to `libraries/AP_DDS/` and `Tools/ros2/`.
- Pre-commit hooks (`.pre-commit-config.yaml`) cover line endings, codespell, large files, XML/YAML validity, ruff. Install with `pre-commit install`.

## Conventions that bite if ignored

- **Method names**: `snake_case`. **Classes**: `AP_`/`AC_`/`AR_` prefix, PascalCase. **Member variables**: leading `_`. **Compile flags**: `AP_<NAME>_ENABLED`.
- **Float comparisons**: use `is_zero()`, `is_positive()`, `is_negative()` — not `== 0.0f`.
- **User-facing messages**: `GCS_SEND_TEXT(...)` — not `printf` or direct `gcs().send_text`.
- **Singletons**: `get_singleton()` + `CLASS_NO_COPY()` macro where applicable.
- **Parameter indices in `AP_GROUPINFO` are baked into stored user configs — never renumber existing entries.** Only append new ones at unused indices. Document parameters with the full `@Param/@DisplayName/@Description/@Values/@Range/@Units/@User` annotation block; full param names cap at 16 chars.
- **Commit subject must contain a `:`** subsystem prefix (e.g., `AP_GPS: …`, `Copter: …`, `Tools: …`). CI rejects merge commits and `fixup!` commits — rebase, don't merge; squash fixups.
- **Do not edit `modules/`** — those are upstream submodules.
- **Embedded constraints are real** — RAM and flash matter. Don't pull in heavy dependencies or speculative abstractions.

## Environment setup

`Tools/environment_install/install-prereqs-ubuntu.sh` installs the toolchain on Ubuntu (similar scripts exist for other OSes in the same dir). A `Dockerfile` and `Vagrantfile` are provided for isolated environments — see `BUILD.md` for the Docker workflow.

If the script fails on a pre-release Ubuntu (e.g. `resolute` / 26.04 in development) with cascading apt dependency errors across unrelated packages (`Depends X (= a.b) but X.next is to be installed`), the configured apt mirror is almost always **stale**, not the script. Compare `apt-cache madison <pkg>` against the primary archive's `Packages.gz` on `archive.ubuntu.com`; if versions differ, switch the mirror in `/etc/apt/sources.list.d/ubuntu.sources` to `archive.ubuntu.com` before patching the script.
