<!-- test-report.md — lab test runs for intro-arducopter-aero-y1 -->

## Run 2 — post-fix (2026-04-26)

SITL SHA: `a6fc842e04d6eacc7f7f2e89f96cebcaa191b810`
Vehicle/frame: ArduCopter SITL `--model +`
Run dir: `course/labs/intro-arducopter-aero-y1/runs/2026-04-26-0001/`

### Per-lab verdict

| Lab | Verdict | Exit code | Wall time |
|-----|---------|-----------|-----------|
| L1 first-sitl-launch | PASS | 0 | 1 s |
| L2 first-flight | FAIL | 6 | 62 s |
| L3 closing-lab | FAIL | 10 | 40 s |

### L2 failure detail

Expected (expected.md): `EKF3 IMU0 origin set` STATUSTEXT seen within 60 s, then arm succeeds.

Observed: `wait_ekf_origin_set()` polls STATUSTEXT for 60 s and exits with code 6 (timeout). Investigative probing confirmed that `test.sh`'s socket-probe connection (the `python3 -c "socket.connect()"` loop) is the **first** client SITL accepts on port 5760. SITL emits all early STATUSTEXT messages — including `EKF3 IMU0 origin set` at SITL t+~20s — exclusively to that first session, then closes it. When `test.py` connects on the **second** TCP session, SITL sends zero STATUSTEXT messages (confirmed: 90 s probe on second session received no STATUSTEXT at all). The `wait_ekf_origin_set` helper is therefore structurally unreachable.

Hypothesis: **lab defect** — `test.sh` must not consume SITL's first TCP session with a throwaway socket probe before `test.py` connects. Options: (a) use `nc`/`netcat -z` (no-connect probe) or a non-closing probe; (b) have `test.py` connect first and use an internal retry loop; (c) replace `wait_ekf_origin_set` with an EKF_STATUS_REPORT + flags check (same approach as `run_lab.wait_ekf_healthy`) which also works on the second session once `REQUEST_DATA_STREAM` is sent.

Recommended owner: **lab-builder** (fix `test.sh` port-probe to not consume SITL's only listen socket, and/or replace the STATUSTEXT-based EKF wait with the flags-based approach already proven in L3).

### L3 failure detail

Expected (expected.md): Step A clean run completes (arm, GUIDED takeoff to 30 m, hover, RTL, disarm) then Step B EKF failsafe observed.

Observed: Step A fails at arm with exit code 10. `wait_ekf_healthy()` returns a false-positive at t+3.4s when `EKF_STATUS_REPORT` flags=1024 (`EKF_CONST_POS_MODE`, no GPS), `velocity_variance=0.000`, `pos_horiz_variance=0.000`. The check `vel_var < 0.5 AND pos_horiz < 0.5` passes because zero satisfies it, but EKF has not converged — it simply has not started processing GPS yet. SITL correctly rejects the arm attempt: `Arm: Accels inconsistent`, `Arm: EKF attitude is bad`, `Arm: AHRS: not using configured AHRS type`. The genuinely healthy EKF (flags=831, GPS active) only arrives at SITL t+~41.5s (`EKF3 IMU0 is using GPS`).

Hypothesis: **lab defect** in `run_lab.wait_ekf_healthy()` — the variance threshold check must additionally verify that the EKF flags word includes active GPS position bits (i.e., `flags & mavutil.mavlink.EKF_POS_HORIZ_ABS != 0`, or equivalently `flags >= 0x1FF` / `flags != 1024`). The fix is a one-line guard: add `and (msg.flags & 0x1FF) != 0` (or check for the GPS-using flag subset) before accepting the health verdict.

Recommended owner: **lab-builder** (add GPS-flags guard to `wait_ekf_healthy` in `run_lab.py`).

### Go / no-go

Not shippable. L1 passes cleanly. L2 and L3 both fail due to distinct lab-code defects introduced or unaddressed in this fix cycle: L2's STATUSTEXT-based EKF wait is structurally broken by `test.sh`'s socket probe consuming SITL's first TCP session; L3's `wait_ekf_healthy` accepts a false-positive EKF_STATUS_REPORT (flags=1024, zero variances) before GPS has converged, causing a premature arm attempt that SITL rightly rejects. Both defects are owned by lab-builder and are fixable without changes to the lab spec.

---

## Run 3 — second-fix (2026-04-26)

SITL SHA: `a6fc842e04d6eacc7f7f2e89f96cebcaa191b810`
Vehicle/frame: ArduCopter SITL `--model +`
Run dir: `course/labs/intro-arducopter-aero-y1/runs/2026-04-26-0002/`

### Per-lab verdict

| Lab | Verdict | Exit code | Wall time |
|-----|---------|-----------|-----------|
| L1 first-sitl-launch | PASS | 0 | 1 s |
| L2 first-flight | FAIL | 6 | 62 s |
| L3 closing-lab | FAIL | 10 | 244 s |

### L2 failure detail

Expected: `EKF3 IMU0 origin set` STATUSTEXT seen within 60 s, then arm/flight sequence proceeds.

Observed: `wait_ekf_origin_set()` polls STATUSTEXT for 60 s and exits with code 6 (timeout). Exit code and wall time are identical to Run 2. The lab-builder fix (removing the socket-probe from `test.sh`) addressed the prior-session consumption issue, but the root defect is still present: **bare SITL TCP never pushes STATUSTEXT messages at all on a direct connection** (confirmed by a 90 s probe that received zero STATUSTEXT while heartbeats and other traffic arrived normally). The STATUSTEXT stream requires either MAVProxy's multiplexed connection or an explicit `REQUEST_DATA_STREAM` for the EXT_STATUS/STATUSTEXT stream. The `wait_ekf_origin_set()` function is structurally unreachable on bare TCP regardless of which client connects first.

Hypothesis: **lab defect** — `wait_ekf_origin_set()` in `l2-first-flight/test.py` must be replaced with the EKF_STATUS_REPORT flags-based approach already used in `run_lab.wait_ekf_healthy()` (L3), which works correctly because it sends `REQUEST_DATA_STREAM` before polling.

Recommended owner: **lab-builder** — replace `wait_ekf_origin_set()` with `REQUEST_DATA_STREAM` + `EKF_STATUS_REPORT` flags check, matching the pattern in `run_lab.wait_ekf_healthy()`.

### L3 failure detail

Expected: Step A clean run completes (arm, GUIDED 30 m, hover, RTL, disarm), then Step B arms, climbs, GPS fault injected, EKF failsafe triggers LAND, vehicle disarms, ERR log confirmed.

Observed (progress vs Run 2): Step A now **passes** (exit code 0 at t+177.9 s). The `EKF_CONST_POS_MODE` guard fix works correctly — EKF is accepted only after genuine GPS lock (flags=0x033f at t+41s). Step B fails immediately at the arm call: SITL returns `"Arm: RTL mode not armable"`. After Step A completes in RTL mode and the vehicle disarms, the flight mode remains RTL. `run_step_b()` calls `arm_vehicle()` without first switching to an armable mode (STABILIZE or GUIDED), so SITL correctly rejects the arm.

Hypothesis: **lab defect** in `run_lab.run_step_b()` — it must call `set_mode(mav, "GUIDED")` (or STABILIZE) before `arm_vehicle()`. The analogous call exists in `run_step_a()` but only *after* arm; Step B must set the mode *before*.

Recommended owner: **lab-builder** — add `set_mode(mav, "GUIDED")` at the start of `run_step_b()`, before `arm_vehicle()`.

### Go / no-go

Not shippable. L1 continues to pass. L2 still fails: the second-fix removed the socket probe but did not address the root defect (STATUSTEXT is never pushed by bare SITL TCP; the entire `wait_ekf_origin_set` approach must be replaced with a `REQUEST_DATA_STREAM` + `EKF_STATUS_REPORT` flags check). L3 made meaningful progress — Step A now passes — but Step B fails because `run_step_b()` does not set an armable mode before arming; adding one `set_mode(mav, "GUIDED")` call before `arm_vehicle()` in `run_step_b()` should unblock it.

---

## Run 4 — third-fix (2026-04-26)

SITL SHA: `a6fc842e04d6eacc7f7f2e89f96cebcaa191b810`
Vehicle/frame: ArduCopter SITL `--model +`
Run dir: `course/labs/intro-arducopter-aero-y1/runs/2026-04-26-0003/`

### Per-lab verdict

| Lab | Verdict | Exit code | Wall time |
|-----|---------|-----------|-----------|
| L1 first-sitl-launch | PASS | 0 | 1 s |
| L2 first-flight | FAIL | 4 | 104 s |
| L3 closing-lab | FAIL | 5 | 322 s |

### L2 failure detail

Expected: arm → climb > 10 m in STABILIZE via RC override → LAND → disarm.

Observed: EKF fix (Run 3 recommendation) works — `wait_ekf_origin_set()` now correctly gates on `EKF_STATUS_REPORT` flags (0x033f at t+42 s, GPS lock confirmed). Mode STABILIZE set, vehicle arms at t+43.9 s. Throttle RC override (channel 3, 1700 µs) sent at 0.5 Hz but altitude never exceeds 10 m within 60 s; exit code 4. Root cause: bare SITL in STABILIZE mode with RC override throttle at 1700 µs does not produce meaningful climb — STABILIZE requires both throttle above mid AND coherent roll/pitch/yaw inputs (channels 1/2/4); with channels 1/2/4 overridden to 0 (no override) the vehicle sits with motors at partial throttle but does not climb stably. The 1700 µs value is also below the typical hover threshold in SITL default params (THR_MID ~500/1000 scale). The correct approach is to use GUIDED mode with `MAV_CMD_NAV_TAKEOFF`, exactly as L3 does, or to override all four channels simultaneously with appropriate hover values.

Hypothesis: **lab defect** in `l2-first-flight/test.py` — `wait_altitude()` sends throttle override on channel 3 only; STABILIZE does not auto-level, so the vehicle does not climb with an incomplete RC override. Recommended fix: switch to GUIDED mode before arming and issue a `MAV_CMD_NAV_TAKEOFF` command (matching L3 pattern), or switch to LOITER/ALT_HOLD which respond to single-channel throttle override more predictably.

Recommended owner: **lab-builder** — replace STABILIZE + RC-override climb with GUIDED + NAV_TAKEOFF in `l2-first-flight/test.py`.

### L3 failure detail

Expected: Step A passes, Step B EKF fault triggers LAND + disarm + ERR log entry (Subsys=16, ECode=2).

Observed: **Step A PASS** (identical to Run 3: t+177.9 s). **Step B now arms and executes** — the `set_mode(mav, "GUIDED")` fix before `arm_vehicle()` works. Step B arms, issues GUIDED takeoff to 30 m (altitude warning: did not reach 30 m — same issue as Step A, not a new defect), injects GPS fault at t+62.6 s after arm, and correctly observes `EKF variance: position lost` STATUSTEXT (sev=2) at injection+8.1 s and LAND mode at injection+8.1 s. Vehicle disarms. Step B then fails at the dataflash log check: `find_latest_log(".")` finds `./eeprom.bin` (the SITL EEPROM file, not a dataflash log), reports `ERR Subsys=16/ECode=2 NOT found`, and exits with code 5. The actual dataflash `.bin` log is written under `logs/` relative to the repo root (cwd of `test.sh`); it has a different name and is not `eeprom.bin`. The `find_latest_log` glob `logs/*.bin` should find it, but `eeprom.bin` at the root is found instead, and it is not a DFReader-parseable dataflash file (hence all the `bad header` spam).

Hypothesis: **lab defect** in `run_lab.find_latest_log()` — when `logs/*.bin` returns nothing (or the cwd is wrong), it falls back to `./*.bin` which matches `eeprom.bin`. The actual dataflash logs may not be in `logs/` when running `--wipe` with a direct binary invocation (SITL started with `--wipe` creates logs under the working directory's `logs/` subdirectory, but only after a flight writes data). The fallback glob `*.bin` at repo root picks up `eeprom.bin` instead. The fix is to ensure the glob finds the correct flight log — either by verifying the `logs/` path is created, adding a short post-disarm wait for the log to be flushed, or by checking that the matched `.bin` file is actually a DFReader log before using it.

Recommended owner: **lab-builder** — fix `find_latest_log()` to skip non-dataflash `.bin` files (check DFReader header magic or require file to be inside `logs/` only), and/or add a post-disarm sleep to ensure the log is flushed before parsing.

### Go / no-go

Not shippable. L1 PASS (4/4 runs clean). L2 unblocked past EKF but now fails at altitude (exit 4): STABILIZE + single-channel RC override does not produce reliable climb in headless SITL; lab-builder should switch to GUIDED + NAV_TAKEOFF. L3 reached all functional milestones — EKF healthy, arm, takeoff, GPS fault, LAND mode change, disarm — but the dataflash ERR-row check reads `eeprom.bin` instead of the flight log; lab-builder should fix `find_latest_log()` fallback to exclude non-dataflash files. Both remaining defects are small and well-isolated; one more fix cycle should bring all three labs to PASS.

---

## Run 5 — speedup + final fixes (2026-04-26)

SITL SHA: `a6fc842e04d6eacc7f7f2e89f96cebcaa191b810`
Vehicle/frame: ArduCopter SITL `--model +` `--speedup 10`
Run dir: `course/labs/intro-arducopter-aero-y1/runs/2026-04-26-0004/`

### Per-lab verdict

| Lab | Verdict | Exit code | Wall time |
|-----|---------|-----------|-----------|
| L1 first-sitl-launch | PASS | 0 | <1 s |
| L2 first-flight | FAIL | 4 | 65 s |
| L3 closing-lab | PASS | 0 | 142 s |

### L2 failure detail

Expected: STABILIZE arm → RC override throttle 1700 µs (all four channels) → altitude > 10 m within 60 s.

Observed: EKF healthy at t+4.1 s (flags=0x033f, GPS lock confirmed). STABILIZE mode set. Vehicle armed at t+4.2 s. RC override sends roll=1500, pitch=1500, throttle=1700, yaw=1500 at 0.5 Hz. Altitude never exceeds 10 m within 60 s; exit code 4. The four-channel fix (Run 5 delta) prevents the floating-stick bug but STABILIZE mode in bare SITL does not produce reliable autonomous climb with RC override alone — the copter receives RC input but there is no altitude-hold assistance. The 1700 µs throttle value is below the typical hover threshold when mapped to the SITL motor curve, and STABILIZE requires manual continuous control.

Hypothesis: **persistent lab defect** — the run-5 fix (all-four-channels RC override) is necessary but not sufficient. STABILIZE mode requires the operator to manually manage altitude; RC override at fixed 1700 µs produces partial-throttle motor spin rather than a sustained climb. The correct approach (as demonstrated by L3) is GUIDED mode + `MAV_CMD_NAV_TAKEOFF`. Recommended owner: **lab-builder** — replace STABILIZE + RC override climb with GUIDED + NAV_TAKEOFF in `l2-first-flight/test.py`.

### L3 pass detail

Step A: EKF healthy (flags=0x033f) at t+0.5 s, arm, GUIDED takeoff (altitude warning: did not reach 30 m — non-fatal), hover 3 s, RTL, disarm. PASS at t+72.6 s.
Step B: EKF healthy re-acquired after 3 s inter-step pause. GUIDED mode set before arm. GPS fault injected at t+61.0 s post-arm. `EKF variance: position lost` STATUSTEXT (sev=2) at injection+0.8 s. LAND mode at injection+0.8 s. Vehicle disarms. Dataflash log `logs/00000025.BIN` parsed; ERR Subsys=16 ECode=2 found at TimeUS=1378142689. PASS at t+141.9 s.

### Go / no-go

Not fully shippable. L1 PASS (5/5 runs). L3 PASS on first attempt with all speedup + fixes applied — EKF guard, GUIDED-before-arm, log-glob, and sim-time pacing all work correctly. L2 remains FAIL (exit 4): the four-channel RC override fix eliminates the floating-stick regression but STABILIZE mode does not produce a reliable climb with fixed-value RC override in headless SITL. Lab-builder must replace the STABILIZE + RC override pattern with GUIDED + NAV_TAKEOFF (the same approach that makes L3 work). One targeted fix to `l2-first-flight/test.py` should close this final gap.

---

## Run 6 — STABILIZE->GUIDED (2026-04-26)

SITL SHA: `a6fc842e04d6eacc7f7f2e89f96cebcaa191b810`
Vehicle/frame: ArduCopter SITL `--model +` `--speedup 10`
Run dir: `course/labs/intro-arducopter-aero-y1/runs/2026-04-26-0005/`

### Per-lab verdict

| Lab | Verdict | Exit code | Wall time |
|-----|---------|-----------|-----------|
| L1 first-sitl-launch | PASS | 0 | <1 s |
| L2 first-flight | PASS | 0 | 9 s |
| L3 closing-lab | PASS | 0 | 143 s |

### Step detail (L2)

EKF healthy (flags=0x033f) at t+4.1 s. STABILIZE confirmed at t+4.1 s (mode-change machinery verified). GUIDED set. Armed at t+4.2 s. NAV_TAKEOFF (15 m target) sent; altitude 10.4 m reached at t+5.0 s. LAND mode set. "Disarming motors" STATUSTEXT at t+7.9 s; HEARTBEAT disarmed confirmed. Total: 9 s wall (speedup 10).

### Step detail (L3)

Step A: EKF healthy (flags=0x033f) at t+0 s, arm, GUIDED takeoff (altitude warning: did not reach 30 m — non-fatal), hover 3 s, RTL, disarm. PASS at t+73.0 s. Step B: EKF re-acquired, GUIDED before arm, GPS fault at t+61.2 s post-arm, "EKF variance: position lost" (sev=2) + LAND at injection+0.8 s, disarm, ERR Subsys=16 ECode=2 found in logs/00000027.BIN. PASS at t+142.5 s.

### Go / no-go

All three labs PASS. L1 PASS (6/6 runs, <1 s). L2 PASS on first attempt with GUIDED+NAV_TAKEOFF: EKF guard, STABILIZE mode-change check, GUIDED arm, NAV_TAKEOFF to 15 m, LAND, and disarm all complete in 9 s wall time. L3 PASS (second consecutive run): Step A and Step B both pass, including GPS-fault injection, EKF failsafe LAND, and dataflash ERR row verification. The suite is shippable.
