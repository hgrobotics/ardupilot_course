# Lab L1 — First SITL Launch: Student Guide

## What you will do

In this lab you will launch the ArduCopter Software-In-The-Loop (SITL) simulator on your own laptop and confirm that the simulated vehicle is alive and talking MAVLink. There is no flying — you are checking that the environment is correctly installed and that the autopilot binary starts, opens its telemetry port, and announces itself to a ground-control station. Getting this smoke test to pass is the foundation everything else in the course depends on, so take your time and read each step carefully.

---

## Before you start

**Previous labs required**: none — this is the first lab.

**Software that must already be installed** (done in Module 1.2):

- Ubuntu 22.04 or 24.04 (native or WSL2 on Windows).
- ArduPilot prerequisites installed via `Tools/environment_install/install-prereqs-ubuntu.sh`.
- The ArduPilot repository cloned with submodules (`git clone --recurse-submodules`).
- `python3` and `mavproxy.py` on your PATH (the prerequisites script installs both).

**What must be true before you run Step 1**:

- The SITL binary exists at `build/sitl/bin/arducopter` inside the repository. If you see a "file not found" error, build it first:

  ```
  ./waf configure --board sitl
  ./waf copter
  ```

  Run those two commands from the repository root. Do **not** use `sudo`.

**Windows open**: you need at least one terminal window open at the repository root. The `sim_vehicle.py` script will open the MAVProxy console and map windows for you automatically.

---

## The steps

**Total estimated time**: 15 minutes.
**Goal**: confirm SITL is running and a MAVProxy heartbeat is visible.

---

### Pre-conditions

- SITL binary exists: `build/sitl/bin/arducopter`
- If missing, run from the repo root:
  ```
  ./waf configure --board sitl
  ./waf copter
  ```

---

### Step 1 — Launch SITL

From the repository root, run:

```
python3 Tools/autotest/sim_vehicle.py -v ArduCopter -f quad -N --console --map
```

Or use the provided launch script:

```
bash course/labs/intro-arducopter-aero-y1/l1-first-sitl-launch/launch.sh
```

**What you will see**:
- A terminal window labelled "MAVProxy" appears.
- A second window showing the MAVProxy command prompt appears.
- A map window opens.
- The terminal shows lines like:
  ```
  Detected vehicle ArduCopter
  online system 1
  ```

**Wait**: up to 30 seconds for the heartbeat line `online system 1`.

---

### Step 2 — Verify the console

In the MAVProxy console window, confirm:
- A line containing `APM:Copter V` (the firmware version banner).
- Mode shown as `STABILIZE`.
- Battery reading (simulated; should be around 12.6 V).

---

### Step 3 — Verify the map

Check the map window:
- A vehicle icon appears near Canberra, Australia (approximately -35.36, 149.17).
- The icon does not move (vehicle is on the ground, disarmed).

---

### Step 4 — Record

Write down in your lab notebook:
- The ArduCopter firmware version string (from `APM:Copter V...`).
- The current time shown in the MAVProxy console.

---

### Step 5 — Exit SITL (end of lab)

In the MAVProxy command terminal, type:

```
exit
```

This terminates the MAVProxy session and the SITL process.

---

### Fault injection

None in this lab.

---

### Restoring state

No state changes are made. Each SITL launch starts fresh.

---

## What success looks like

You have passed this lab when all of the following are true:

1. The `sim_vehicle.py` command ran without printing any Python traceback or `ERROR:` line.
2. Within 30 seconds of launch, the MAVProxy terminal printed `online system 1`.
3. Within 30 seconds of launch, the MAVProxy terminal printed `Detected vehicle ArduCopter`.
4. The MAVProxy console showed `APM:Copter V` (the firmware version line).
5. The map window rendered a vehicle icon near Canberra, Australia.

You do not need to fly anything. The vehicle stays on the ground, disarmed, throughout the lab.

---

## Common mistakes and quick fixes

**1. "SITL binary not found" or `build/sitl/bin/arducopter` is missing**

You have not built the SITL binary yet, or the build failed. From the repository root:

```
./waf configure --board sitl
./waf copter
```

If `waf` is not on your PATH, use `./waf` (there is a `waf` script at the repository root). Never run `waf` with `sudo`.

**2. The MAVProxy windows do not open (no console, no map)**

On Ubuntu, the `--console` and `--map` windows require a display. If you are in a headless SSH session, you will need to either work at a physical terminal or use X forwarding (`ssh -X`). The automated lab test is designed to run headlessly — that is a separate path for the grading agent, not for your interactive session.

**3. `online system 1` never appears after 30 seconds**

The most common cause is that a previous SITL session is still running and holding the port. Check with:

```
ps aux | grep arducopter
```

Kill any stray processes (`kill <PID>`), then re-run Step 1.

**4. MAVProxy says `no module named ...` or `ImportError`**

The Python prerequisites are not installed, or your terminal is using the wrong Python. Run:

```
python3 -c "import pymavlink; print('OK')"
```

If that fails, re-run `Tools/environment_install/install-prereqs-ubuntu.sh` and open a fresh terminal so the updated `PATH` takes effect.

**5. Working directory error — "no such file or directory" for `sim_vehicle.py`**

You must run commands from the repository root (the directory containing `ArduCopter/`, `libraries/`, `Tools/`, etc.). Use `pwd` to confirm your location. If you are inside a subdirectory, `cd` back to the root:

```
cd ~/ardupilot   # or wherever you cloned the repo
```

---

## Where to go next

**Next lab**: [Lab L2 — First Flight](../l2-first-flight/student-guide.md) — arm the vehicle, climb to 10 m, and land.

**Module reference**: this lab is the hands-on portion of **Module 1.2 — Set up your laptop: install, build, and launch SITL** in [course/intro_arducopter_aero_y1.md](../../../../course/intro_arducopter_aero_y1.md).
