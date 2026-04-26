# Lab L1 — Steps: First SITL Launch

**Total estimated time**: 15 minutes.
**Goal**: confirm SITL is running and a MAVProxy heartbeat is visible.

---

## Pre-conditions

- SITL binary exists: `build/sitl/bin/arducopter`
- If missing, run from the repo root:
  ```
  ./waf configure --board sitl
  ./waf copter
  ```

---

## Step 1 — Launch SITL

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

## Step 2 — Verify the console

In the MAVProxy console window, confirm:
- A line containing `APM:Copter V` (the firmware version banner).
- Mode shown as `STABILIZE`.
- Battery reading (simulated; should be around 12.6 V).

---

## Step 3 — Verify the map

Check the map window:
- A vehicle icon appears near Canberra, Australia (approximately -35.36, 149.17).
- The icon does not move (vehicle is on the ground, disarmed).

---

## Step 4 — Record

Write down in your lab notebook:
- The ArduCopter firmware version string (from `APM:Copter V...`).
- The current time shown in the MAVProxy console.

---

## Step 5 — Exit SITL (end of lab)

In the MAVProxy command terminal, type:

```
exit
```

This terminates the MAVProxy session and the SITL process.

---

## Fault injection

None in this lab.

---

## Restoring state

No state changes are made. Each SITL launch starts fresh.
