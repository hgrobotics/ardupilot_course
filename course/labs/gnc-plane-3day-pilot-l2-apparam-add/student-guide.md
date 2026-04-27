# Lab L2 Student Guide — AP_GROUPINFO Add + Observe

## What you will do

In this lab you will modify two ArduPlane source files to add a brand-new
parameter (`MY_PARAM`) to the `ParametersG2` struct, rebuild SITL, and watch
the parameter show up live in the running sim at its default value of 17.0. You
will then change it to 42.0 and restart SITL to confirm the value survives
the restart — demonstrating ArduPilot's NVM persistence mechanism. This is the
fastest way to understand why `AP_GROUPINFO` index numbers matter and how the
parameter table drives both MAVLink exposure and EEPROM storage. Every
subsystem you look at in later modules uses this exact pattern.

## Before you start

- You must have a working SITL binary from Module M3. A standard (non-debug)
  build is fine: `./waf configure --board sitl && ./waf plane`.
- `pymavlink` must be installed: `pip3 install pymavlink`.
- Both `ArduPlane/Parameters.h` and `ArduPlane/Parameters.cpp` must be in their
  unmodified state (`git status` should show no changes to these files).
- Open one terminal window in the repository root.

## The steps

### Step 1 — Apply the source patch

From the repository root:

```
git apply course/labs/gnc-plane-3day-pilot-l2-apparam-add/patch/l2-my-param.patch
```

This adds `AP_Float my_param;` to `ParametersG2` in `Parameters.h` and one
`AP_GROUPINFO("MY_PARAM", 42, ...)` entry in `Parameters.cpp`.

You can also apply the changes by hand — open the patch file and follow the
`+` lines exactly.

### Step 2 — Rebuild

```
./waf plane
```

This typically takes 10–20 seconds (incremental build, only the changed files).
Confirm you see `[2/2]` or similar and no compilation errors.

### Step 3 — Start SITL

```
Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --no-rebuild
```

### Step 4 — Show MY_PARAM at its default

In the MAVProxy console:

```
param show MY_*
```

You should see:
```
MY_PARAM          17.000000
```

### Step 5 — Change MY_PARAM

```
param set MY_PARAM 42.0
```

MAVProxy should echo: `Set MY_PARAM to 42.000000`.

### Step 6 — Quit SITL

In MAVProxy: type `quit` or press Ctrl-C in the terminal.

### Step 7 — Restart SITL (same directory)

```
Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --no-rebuild
```

Wait for the console to finish loading.

### Step 8 — Verify persistence

```
param show MY_*
```

You should now see:
```
MY_PARAM          42.000000
```

### Step 9 — Restore default and clean up

Reset the parameter:
```
param set MY_PARAM 17.0
```

Quit SITL. Then revert your source changes so later labs start from a clean tree:
```
git checkout ArduPlane/Parameters.h ArduPlane/Parameters.cpp
```

## What success looks like

- After Step 4: `MY_PARAM 17.000000` in MAVProxy.
- After Steps 5–8: `MY_PARAM 42.000000` in MAVProxy on the new session.

If you see `MY_PARAM` is not in the list at all, the binary was not rebuilt
after patching. Stop SITL, run `./waf plane`, and retry.

If after the restart you still see `17.0`, the EEPROM was not written (or was
cleared). The most common cause is running SITL from a different working
directory on the second launch. Make sure both `sim_vehicle.py` invocations
are run from the same directory (the repo root).

## Common mistakes and quick fixes

1. **MY_PARAM not visible at all** — you forgot to run `./waf plane` after
   applying the patch. The running binary is the old one. Rebuild and re-launch.

2. **Compilation error about index 42 already used** — two `AP_GROUPINFO`
   entries share index 42. Open `ArduPlane/Parameters.cpp`, search for `42,`
   in `ParametersG2::var_info`, and assign your entry a different index
   (43, 44, …) that is not already used.

3. **MY_PARAM reverts to 17.0 after restart** — SITL was launched from a
   different directory, so the EEPROM file is a different file. Launch both
   sessions from the same directory (the repo root) with the same `--no-rebuild`
   flag.

4. **`param show MY_*` returns nothing, even after rebuild** — your patch may
   have a typo. Check that the `AP_GROUPINFO` line reads exactly
   `AP_GROUPINFO("MY_PARAM", 42, ParametersG2, my_param, 17.0f)` and that
   `my_param` is declared in the class body in `Parameters.h`.

5. **`git apply` fails with "already applied"** — the patch was applied before.
   Run `git status`; if `Parameters.h` and `Parameters.cpp` are already modified,
   the patch is already in. Skip Step 1.

## Where to go next

Lab L3 (Module M7 — GPS noise + EKF lane switch) uses a stock build with no
source modifications. Revert your patch changes first (`git checkout
ArduPlane/Parameters.h ArduPlane/Parameters.cpp`) before proceeding.
