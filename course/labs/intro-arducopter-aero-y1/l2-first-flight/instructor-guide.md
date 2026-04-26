# Lab L2 — First Flight: Instructor Guide

## Lab summary for the instructor

**What the student is supposed to learn**: the complete arm-to-disarm lifecycle from the operator's perspective: how to arm in STABILIZE mode, how throttle RC override produces a climb, how to switch to LAND, and how to read the disarm confirmation in the GCS console. The student also encounters, briefly, the concept that some mode changes require a position estimate — a seed that Lab L3 grows into the full EKF failsafe sequence.

**Depth marker**: *applied*. Students drive the vehicle manually via MAVProxy RC overrides and observe real GCS statustext messages. They are NOT expected to read the STABILIZE mode source at this stage. The arming check source ([ArduCopter/AP_Arming_Copter.cpp:8-20](../../../../ArduCopter/AP_Arming_Copter.cpp#L8-L20)) and the mode-change refusal path ([ArduCopter/mode.cpp:313-396](../../../../ArduCopter/mode.cpp#L313-L396)) are introduced in Module 1.3 at survey depth only. Do not walk the code bodies here — that is Module 2.3's job.

**Important implementation divergence — STABILIZE vs GUIDED in the automated test**

The student-facing recipe in `steps.md` uses STABILIZE mode with `rc 3 1700` (manual throttle). The automated harness (`test.py`) uses GUIDED mode and `MAV_CMD_NAV_TAKEOFF`. This divergence is intentional and is documented in `test.py`'s module docstring: in bare SITL with a fixed RC throttle override, STABILIZE produces motor spin but not a reliable sustained climb because there is no altitude-hold logic. GUIDED + NAV_TAKEOFF is the only scriptable path that reliably produces `GLOBAL_POSITION_INT.relative_alt > 10 m` in headless testing.

When a TA asks why the test harness uses GUIDED while the student guide says STABILIZE, the correct answer is: the student recipe teaches manual throttle control, which requires a human watching the console; the test harness uses a scriptable command that does not require human intervention. Both paths confirm the arm-to-land-to-disarm lifecycle.

**How this lab feeds later modules**: Lab L3 (the capstone) uses GUIDED + `MAV_CMD_NAV_TAKEOFF` directly, mirroring the automated test path. Students who have completed L2 understand what "arm, take off, land, disarm" looks like as GCS events; L3 adds the fault injection and log-inspection payload on top of that baseline.

**Downstream course connection**: the downstream GNC plane and quadplane courses assume that students can read `STATUSTEXT`, interpret mode changes, and understand that LAND mode is an autonomous descending mode. L2 establishes all three. The `ARSPD_FBW_MIN`, `Q_TRANSITION_MS`, and EKF3 lane-switch concepts in the downstream courses are new; the GCS-side event vocabulary is not.

---

## Pacing

The headless agent test runs in approximately 15–20 seconds wall-clock at `--speedup 10`. Student-facing budget:

| Step | Expected wall-clock time | Notes |
|------|--------------------------|-------|
| Pre-condition check + SITL launch | 2–3 min | Reuse L1 SITL session if still running. |
| Step 1 — STABILIZE mode | < 1 min | Mode change is instantaneous. |
| Step 2 — Arm | 1–3 min | May need to wait for EKF alignment. Budget extra if EKF is slow. |
| Step 3 — Climb to 10 m | 1–2 min | At `rc 3 1700`, climb rate is ~2–3 m/s in STABILIZE. |
| Step 4 — Return throttle | < 1 min | |
| Step 5 — Switch to LAND | < 1 min | |
| Step 6 — Wait for disarm | 3–5 min | Depends on altitude at LAND command; budget 5 min. |
| Step 7 — Record | 2 min | |
| Step 8 — Optional GPS disable | 3–5 min | Skip if class is running late. |
| Step 9 — Exit | < 1 min | |

**Total**: ~15 min typical; 20 min budgeted.

The automated test's `LAND_DISARM_TIMEOUT` is 90 seconds from arm, which at `--speedup 10` is 9 seconds wall-clock. The student-facing 90-second limit is in real time and is generous — typical disarm from a 10–15 m altitude is well under 45 seconds.

---

## Pre-arm setup checklist

Before students start:

- [ ] Lab L1 completed and verified (SITL launches and shows `online system 1` on each machine).
- [ ] Confirm SITL is running with MAVProxy connected. If reusing L1's session, confirm mode is `STABILIZE` and vehicle is disarmed.
- [ ] Confirm MAVProxy command terminal is focused (not the console window). Students type commands in the terminal, not the console.
- [ ] Remind students: `rc 3 1700` sends a throttle override. `rc 3 1500` is mid-stick (hover). `rc 3 1000` is throttle-off. In STABILIZE the vehicle will descend at `rc 3 1400` and fall out of the sky at `rc 3 1000` — tell students to switch to LAND instead of cutting throttle.
- [ ] Warn students: if they issue `param set SIM_GPS1_ENABLE 0` while airborne and armed (Step 8 variant), the EKF failsafe will fire and the vehicle will enter LAND mode autonomously. This is expected and is the preview of Lab L3.

---

## Common student failures and what to say

**Exit code 3 from `test.py` — vehicle did not arm within 30 s**

Diagnostic: `ps aux | grep arducopter` — check the SITL process is alive. Check that the EKF alignment messages appeared.

What to say: "The EKF is still initialising or the arm command was rejected. Watch for `EKF2 IMU0 initial yaw alignment complete` in the console, then retry `arm throttle`."

**Exit code 4 from `test.py` — altitude never exceeded 10 m within 30 s**

In the automated test this means the NAV_TAKEOFF command was not executed correctly. In the student path this means `rc 3 1700` did not produce enough climb. Check that the vehicle is actually armed and that STABILIZE mode is confirmed.

What to say: "Confirm the `ARMED` message appeared and mode is `STABILIZE`. Then re-send `rc 3 1700` and watch the `Alt` reading."

**Exit code 5 from `test.py` — vehicle not disarmed within 90 s of arm**

Either the LAND mode switch was not issued, or the altitude at switch was so high that the 90-second clock expired before touchdown.

What to say: "Issue `mode LAND` sooner, or from a lower altitude. The automated test uses a 90-second window from arm; the vehicle needs enough time to descend."

**`ARMED` appears but vehicle does not climb**

The throttle override command was not sent, or was sent at too low a value. Confirm `rc 3 1700` was typed in the MAVProxy terminal (not the console window). Also confirm the vehicle is not in a GUIDED or ALT_HOLD mode — those modes ignore RC channel 3 overrides differently.

**`Mode change failed: requires position` on `mode LAND`**

LAND does not require a position estimate; it only requires an altitude estimate. This message should not appear for LAND. If it does, the SITL environment is degraded (possibly a parameter from a previous session). Restart SITL with `-w` (wipe EEPROM).

**Student accidentally cuts throttle to 1000 µs and the vehicle crashes**

This is recoverable in SITL — restart SITL with the launch script. Explain that on real hardware, cutting throttle mid-flight is fatal. LAND mode is always the right way to stop the flight.

---

## Verdict signatures

The automated harness checks this sequence (see `test.py` exit codes):

| Code | Meaning | Primary signal |
|------|---------|----------------|
| `0` | PASS — full sequence | HEARTBEAT `base_mode & MAV_MODE_FLAG_SAFETY_ARMED` clears after LAND |
| `1` | FAIL — no heartbeat | `mav.wait_heartbeat()` timeout |
| `2` | FAIL — mode change timeout | HEARTBEAT mode string did not match |
| `3` | FAIL — arm timeout | HEARTBEAT `SAFETY_ARMED` flag never set |
| `4` | FAIL — altitude not reached | `GLOBAL_POSITION_INT.relative_alt` < 10 000 mm (10 m) |
| `5` | FAIL — disarm timeout | HEARTBEAT `SAFETY_ARMED` still set after 90 s from arm |
| `6` | FAIL — EKF not healthy | `EKF_STATUS_REPORT` health conditions not met within 60 s |
| `10` | FAIL — connection or binary error | TCP connection refused or import error |

GCS STATUSTEXT sequence (manual student path):

| Text | Severity | When |
|------|----------|------|
| `Flight mode change successful` | INFO | After `mode STABILIZE` |
| `ARMED` | EMERGENCY | After `arm throttle` |
| `Flight mode change successful` | INFO | After `mode LAND` |
| `LAND complete` | INFO | After touchdown |
| `Disarming motors` | INFO | After auto-disarm |

For Step 8 (optional mode rejection):

| Text | Severity | Condition |
|------|----------|-----------|
| `Mode change failed: requires position` | WARNING | `mode RTL` with `SIM_GPS1_ENABLE 0` |

Source: [ArduCopter/mode.cpp:394](../../../../ArduCopter/mode.cpp#L394) — `mode_change_failed(new_flightmode, "requires position")`.

---

## Pointers to advanced material

- The mode-change refusal logic at [ArduCopter/mode.cpp:313-396](../../../../ArduCopter/mode.cpp#L313-L396) is walked at *applied* depth in Module 1.3 and *applied* depth again in Module 1.4 (mode tour). The downstream GNC plane course revisits this path for quadplane transition-mode refusals.
- The STABILIZE mode run loop at [ArduCopter/mode_stabilize.cpp:9-64](../../../../ArduCopter/mode_stabilize.cpp#L9-L64) explains why throttle is a direct pass-through (no altitude hold). Students who ask "why doesn't the vehicle hold altitude in STABILIZE?" can be pointed here — but this is Module 2.2 material (stick-to-ESC data path), not a L2 discussion.
- The automated test's GUIDED + NAV_TAKEOFF path (see `test.py`) is the same pattern used in the Lab L3 orchestrator and in the downstream GNC courses' scripted test flights. Students who are curious about how automated testing works can read `test.py` directly.
- The EKF healthy check in `test.py` (waiting for `EKF_STATUS_REPORT` with `EKF_POS_HORIZ_ABS` set) is the same pattern used in `run_lab.py` for Lab L3 and in the downstream course's quadplane transition-readiness checks.
