# Lab L3 Steps — GPS Noise + EKF Lane Switch

## Prerequisites

- Stock SITL binary (debug preferred): `./waf configure --board sitl --debug && ./waf plane`
- SITL launched:
  ```
  Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --map -L KSFO
  ```
- In MAVProxy, load the lab params:
  ```
  param load course/labs/gnc-plane-3day-pilot-l3-gps-ekf-laneswitch/params.parm
  ```

## Steps

### Phase A — Takeoff and cruise

1. **Confirm EKF3 dual-lane is enabled:**
   ```
   param show EK3_IMU_MASK
   ```
   Expected: `EK3_IMU_MASK 3.000000`

2. **Set mode to TAKEOFF and arm:**
   ```
   mode TAKEOFF
   arm throttle
   ```
   The plane will auto-throttle and climb. Watch the GCS altitude indicator.

3. **Wait until altitude > 50 m**, then switch to FBWA for steady cruise:
   ```
   mode FBWA
   ```

4. **Fly in FBWA for ~10 seconds** (watch the map — the plane should be
   flying a heading).

### Phase B — Inject GPS noise

5. **Inject gentle GPS noise:**
   ```
   param set SIM_GPS1_NOISE 5
   ```
   Expected: the plane continues flying; EKF adjusts internally.

6. **Wait 10 seconds.** Watch for any STATUSTEXT messages.

### Phase C — Inject GPS glitch

7. **Inject the GPS position glitch (50 m north offset):**
   ```
   param load course/labs/gnc-plane-3day-pilot-l3-gps-ekf-laneswitch/faults/gps_glitch.parm
   ```
   Or manually:
   ```
   param set SIM_GPS1_GLTCH_X 50
   ```

8. **Watch the GCS console for the lane-switch message.**
   Expected (within 30 s):
   ```
   EKF3 lane switch 1
   ```
   (The number is the new primary lane index.)

### Phase D — Restore and disarm

9. **Restore the GPS to nominal:**
   ```
   param load course/labs/gnc-plane-3day-pilot-l3-gps-ekf-laneswitch/faults/gps_glitch_restore.parm
   ```
   Or manually:
   ```
   param set SIM_GPS1_GLTCH_X 0
   param set SIM_GPS1_NOISE 0
   ```

10. **Set mode to RTL and wait for landing:**
    ```
    mode RTL
    ```
    The plane will return to home and land.

### Phase E — Download and inspect the log

11. **After landing, disarm and download the log:**
    ```
    disarm
    ```
    Then in a second terminal:
    ```
    python3 Tools/autotest/mavlogdump.py --types=XKF1,XKF4,EV logs/00000001.BIN | grep -i 'switch\|lane'
    ```
    Expected: at least one record referencing the lane switch event.

## Fault injection reference

| Fault | Parameter | Restore |
|-------|-----------|---------|
| GPS noise (gentle) | `SIM_GPS1_NOISE 5` | `SIM_GPS1_NOISE 0` |
| GPS glitch 50 m N | `SIM_GPS1_GLTCH_X 50` | `SIM_GPS1_GLTCH_X 0` |
