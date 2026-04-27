# Lab L2 — AP_GROUPINFO Add + Observe

## Purpose

You will add a new `AP_Float` parameter (`MY_PARAM`, default 17.0) to ArduPlane's
`ParametersG2` class, rebuild SITL, and verify that the parameter appears as
`MY_PARAM 17.0` in the running sim. You will then change it to 42.0, restart
SITL, and confirm it persists across restarts. This exercise teaches the full
lifecycle of an ArduPilot parameter: source annotation, `AP_GROUPINFO` table
entry, NVM storage, MAVLink exposure.

## Module reference

Day 2, Module M5 — Core Infrastructure Libraries (`AP_Param`, `AP_GROUPINFO`).

## Prerequisites

- SITL binary already built (a non-debug build is fine for this lab):
  `./waf configure --board sitl && ./waf plane`
- `pymavlink` installed: `pip3 install pymavlink`
- All commands from the repository root.

## Estimated duration

30 minutes.

## Success criteria

1. After adding `MY_PARAM` to `ParametersG2` and rebuilding:
   `param show MY_*` in MAVProxy prints `MY_PARAM 17.0`.
2. After `param set MY_PARAM 42.0` and SITL restart (from the same working
   directory so the EEPROM persists), `param show MY_*` prints `MY_PARAM 42.0`.
3. The headless test harness (`test.sh` + `test.py`) confirms both states via
   MAVLink `PARAM_VALUE` messages.

## Source patch location

The patch adds:
- `ArduPlane/Parameters.h` — `AP_Float my_param;` in the `ParametersG2` struct,
  plus `k_param_my_param` enum entry (not strictly required for g2 but good practice).
- `ArduPlane/Parameters.cpp` — one `AP_GROUPINFO` entry at index 42 in
  `ParametersG2::var_info[]`.

The patch is provided as `patch/l2-my-param.patch` in this lab directory.
Apply it with: `git apply course/labs/gnc-plane-3day-pilot-l2-apparam-add/patch/l2-my-param.patch`
Then rebuild: `./waf plane`.
