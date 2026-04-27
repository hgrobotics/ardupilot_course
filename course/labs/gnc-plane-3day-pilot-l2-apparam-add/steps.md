# Lab L2 Steps — AP_GROUPINFO Add + Observe

## Prerequisites

- Repository on branch `GNC-0.1`.
- SITL binary already built (previous lab or earlier today).

## Steps

### Phase A — Apply the patch and rebuild

1. **Apply the source patch:**
   ```
   cd /home/mahisorn/repos/ardupilot_course
   git apply course/labs/gnc-plane-3day-pilot-l2-apparam-add/patch/l2-my-param.patch
   ```

   Alternatively, make the changes by hand (see `patch/l2-my-param.patch` for
   exact diffs):
   - In `ArduPlane/Parameters.h`: add `AP_Float my_param;` to the end of the
     `ParametersG2` struct (before `};`).
   - In `ArduPlane/Parameters.cpp`: add the `AP_GROUPINFO("MY_PARAM", 42, ...)`
     block before `AP_GROUPEND` in `ParametersG2::var_info[]`.

2. **Rebuild:**
   ```
   ./waf plane
   ```
   Build should succeed with no errors. If you see a conflict about index 42,
   check that you haven't accidentally duplicated an existing index — scan
   `ArduPlane/Parameters.cpp` for `42,` in `ParametersG2::var_info`.

### Phase B — Verify the default value

3. **Start SITL with MAVProxy:**
   ```
   Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --no-rebuild
   ```

4. **In the MAVProxy console, show MY_PARAM:**
   ```
   param show MY_*
   ```
   Expected output: `MY_PARAM   17.000000`

### Phase C — Change the value and verify persistence

5. **Set MY_PARAM to 42:**
   ```
   param set MY_PARAM 42.0
   ```
   Expected: MAVProxy echoes `Set MY_PARAM to 42.000000`.

6. **Quit SITL** (type `quit` in MAVProxy or press Ctrl-C in the terminal).

7. **Restart SITL from the same working directory** (EEPROM file must persist):
   ```
   Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --no-rebuild
   ```

8. **In the new MAVProxy session, check MY_PARAM again:**
   ```
   param show MY_*
   ```
   Expected: `MY_PARAM   42.000000`

   If instead you see `17.000000`, the EEPROM was cleared (sim was run from a
   different directory, or `--wipe-eeprom` was passed). Repeat from step 3
   without changing directory.

### Phase D — Restore

9. **Reset MY_PARAM to its default:**
   ```
   param set MY_PARAM 17.0
   ```

10. **Quit SITL.**

11. **Revert the patch** (leave the tree clean for subsequent labs):
    ```
    git checkout ArduPlane/Parameters.h ArduPlane/Parameters.cpp
    ```
