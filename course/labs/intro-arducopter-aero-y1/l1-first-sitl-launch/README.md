# Lab L1 — First SITL Launch

## Purpose

This lab establishes that ArduCopter SITL runs on the student's own laptop and that the MAVProxy console, MAVProxy terminal, and map window all appear and receive a live heartbeat from the simulated vehicle. It is the practical completion of Module 1.2 ("Set up your laptop: install, build, and launch SITL").

## Module reference

Day 1 Module 1.2 — Set up your laptop: install, build, and launch SITL.

## Prerequisites

- Ubuntu 22.04 / 24.04 (or WSL2 on Windows) with the ArduPilot prerequisites installed via `Tools/environment_install/install-prereqs-ubuntu.sh`.
- ArduPilot repository cloned with submodules (`git clone --recurse-submodules`).
- SITL binary already built: `build/sitl/bin/arducopter` must exist. If it does not, run `./waf configure --board sitl && ./waf copter` from the repository root.
- `python3`, `mavproxy.py` available on PATH (installed by the prerequisite script).
- No hardware required.

## Estimated duration

15 minutes (5 min build verify + 5 min launch + 5 min observation).

The full Module 1.2 is 1 hour because it includes the initial install and build; this lab covers only the verification and launch step.

## Success criteria

1. The `sim_vehicle.py` process starts without error.
2. Within 30 seconds of launch, the MAVProxy console window prints a line containing `online system 1`.
3. Within 30 seconds of launch, the MAVProxy terminal prints a line containing `Detected vehicle ArduCopter`.
4. The map window renders a vehicle icon at the SITL default location (near Canberra, Australia: approximately -35.36, 149.17).
5. `STATUSTEXT` `APM:Copter V` appears in the MAVProxy console (firmware version banner).

lab-tester pass condition: stdout of `sim_vehicle.py` (captured with `-N` / `--no-rebuild`) contains `online system 1` within 30 seconds.
