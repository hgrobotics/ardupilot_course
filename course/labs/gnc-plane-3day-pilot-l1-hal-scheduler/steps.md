# Lab L1 Steps — HAL + Scheduler Probe

## Prerequisites

- Debug binary built: `./waf configure --board sitl --debug && ./waf plane`
- Terminal A: SITL is running via `course/labs/gnc-plane-3day-pilot-l1-hal-scheduler/launch.sh`
  (or `Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --debug --no-mavproxy`)

## Steps

1. **Build the debug binary** (if not already built):
   ```
   cd /home/mahisorn/repos/ardupilot_course
   ./waf configure --board sitl --debug
   ./waf plane
   ```

2. **Terminal A — start SITL (no MAVProxy):**
   ```
   Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --debug --no-mavproxy
   ```
   Leave this terminal running. You should see log output like
   `SIM_VEHICLE: Starting ArduPlane ...`.

3. **Terminal B — find the PID of the running arduplane process:**
   ```
   pgrep arduplane
   ```
   Note the PID (e.g., `12345`).

4. **Terminal B — attach gdb:**
   ```
   gdb build/sitl/bin/arduplane -p $(pgrep arduplane)
   ```
   You should see the gdb prompt `(gdb)`.

5. **Set a breakpoint on the HAL update function:**
   ```
   (gdb) b Plane::ahrs_update
   ```
   Expected output: `Breakpoint 1 at 0x...: file ArduPlane/Plane.cpp, line 167.`

6. **Continue execution until the breakpoint fires:**
   ```
   (gdb) c
   ```
   The breakpoint fires roughly every 20 ms (50 Hz). You should see:
   `Breakpoint 1, Plane::ahrs_update () at ArduPlane/Plane.cpp:167`

7. **Read the HAL monotonic clock:**
   ```
   (gdb) print AP_HAL::millis()
   ```
   Expected: a value greater than 0 (e.g., `$1 = 2471`). This is milliseconds
   since SITL boot.

8. **Read the scheduler loop rate:**
   ```
   (gdb) print AP::scheduler().get_loop_rate_hz()
   ```
   Expected: `$2 = 50` (the plane default from
   `libraries/AP_Scheduler/AP_Scheduler.cpp:46`).

9. **Detach and quit:**
   ```
   (gdb) detach
   (gdb) quit
   ```

10. **Back in Terminal A — press Ctrl-C to stop SITL.**

## Fault injection

None in this lab.

## What to record

- The value printed for `AP_HAL::millis()` (must be > 0).
- The value printed for `get_loop_rate_hz()` (should be 50).
- The source line gdb resolved for `Plane::ahrs_update` (should be
  `ArduPlane/Plane.cpp:167`).
