# Lab L3 — GPS Noise + EKF Lane Switch

## Purpose

You will fly ArduPlane SITL in FBWA mode, inject a GPS glitch via the SITL
parameter `SIM_GPS1_GLTCH_X`, and observe the EKF3 lane-switch event in both
the GCS STATUSTEXT and the dataflash log. The lab demonstrates that EKF3's
lane-health arbitration (driven by `NavEKF3_core::errorScore` in
`libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp:62-86`) is a runtime observable,
not just a design note.

## Parameter name resolution (required note for lab-builder)

The GPS glitch parameter group is registered in `libraries/SITL/SITL.cpp` as:
```
AP_SUBGROUPINFO(gps[0], "GPS1_", 50, SIM, GPSParms)
```
and in `libraries/SITL/SIM_GPS.cpp:75`:
```
AP_GROUPINFO("GLTCH", 6, GPSParms, glitch, 0)
```
The full parameter name for the first GPS glitch X-component is therefore
`SIM_GPS1_GLTCH_X`. The plan's parenthetical "`SIM_GPS_GLTCH_X` vs
`SIM_GPS0_GLTCH_X`" has been resolved: the correct canonical name is
`SIM_GPS1_GLTCH_X`. Similarly, GPS noise is `SIM_GPS1_NOISE`.

Older autotest scripts used `GPS2_GLTCH` for the second GPS sensor (now
`SIM_GPS2_GLTCH_X`). The `GPS_NOISE` (no index) and `GPS2_NOISE` entries
at lines 678/695 of `SITL.cpp` are commented out as historical — do not use them.

## Module reference

Day 2, Module M7 — AHRS/EKF3 (internals + lane switch).

## Prerequisites

- Stock debug build: `./waf configure --board sitl --debug && ./waf plane`
- `pymavlink` installed: `pip3 install pymavlink`
- `mavlogdump.py` available (`Tools/autotest/mavlogdump.py` or system PATH).
- All commands from the repository root.

## Estimated duration

40 minutes.

## Success criteria

1. Plane arms, takes off in TAKEOFF mode, and transitions to FBWA above 50 m.
2. After `SIM_GPS1_NOISE 5` injection, the plane continues flying.
3. After `SIM_GPS1_GLTCH_X 50` injection, the GCS prints a STATUSTEXT
   containing `EKF3 lane switch` within 30 s.
4. Dataflash log contains an `EV` message or equivalent lane-switch marker.
5. After restoring `SIM_GPS1_GLTCH_X 0` and `SIM_GPS1_NOISE 0`, flight
   continues normally.
