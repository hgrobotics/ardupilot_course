# Lab L3 — Closing Lab: Instructor Guide

## Lab summary for the instructor

**What the student is supposed to learn**:

1. How to run a fully scripted autonomous flight (arm, GUIDED takeoff, hover, RTL, land) without manual input and confirm it succeeded from the GCS console.
2. How a GPS failure propagates through the EKF check loop to a `MAV_SEVERITY_CRITICAL` STATUSTEXT, a mode change, and a dataflash `ERR` row — and how to trace each of those events back to a specific line in `ArduCopter/ekf_check.cpp`.
3. How to use `mavlogdump.py --types ERR` to extract the relevant rows from a binary dataflash log.

**Depth marker**: *applied*. Students read the three-line block at [ArduCopter/ekf_check.cpp:83-89](../../../../ArduCopter/ekf_check.cpp#L83-L89) and match each line to a live event. They do not derive what EKF variance means, what the Kalman gain is, or how the innovation covariance is computed. That is the GNC course's job. Do not unpack the `ekf_over_threshold()` function body ([ArduCopter/ekf_check.cpp:105-165](../../../../ArduCopter/ekf_check.cpp#L105-L165)) or the EKF3 lane-switch machinery — those are internals-depth material reserved for the downstream GNC course.

**How this lab feeds later modules**: Lab L3 is the capstone. It confirms that the student can connect a live observable (console text), a binary artifact (dataflash log), and a source location (file:line) for the same event. This triple-confirmation skill is the entry-level prerequisite for the downstream GNC courses, where every module has associated log fingerprints and source citations.

**Downstream course connection**: the EKF3 multi-lane architecture is introduced in the downstream GNC plane/quadplane course (`custom_gnc_course_plane.md`, `custom_gnc_course_quadplane.md`) starting from the `checkLaneSwitch()` function. The EKF failsafe path students observe here (`failsafe_ekf_event()` at [ArduCopter/ekf_check.cpp:89](../../../../ArduCopter/ekf_check.cpp#L89)) is a different, higher-level mechanism — it fires after the EKF is already confirmed bad, whereas the lane switch fires preemptively when a secondary lane is healthier. The downstream course will distinguish these two; this lab only establishes that the failsafe path exists.

---

## Pacing

The headless agent test runs in approximately 30–60 seconds wall-clock at `--speedup 10` (both steps in sequence). Student-facing budget:

### Step A (~25 min total)

| Sub-step | Expected wall-clock time | Notes |
|----------|--------------------------|-------|
| A.1 SITL launch + online | 2–3 min | `-w` wipes EEPROM; EKF init adds ~5 s at speedup 10. |
| A.2 Load params.parm | < 1 min | Three non-default params. |
| A.3 Run orchestrator | 10–12 min | EKF healthy wait (~5 s), arm, takeoff to 30 m, 30 s hover, RTL, land, disarm — all at speedup 10. Wall-clock ~3 min actual; budget 5 min for students reading console. |
| A.4 Observe + record log path | 3–5 min | Encourage students to watch every STATUSTEXT. |
| A.5 Post-flight buffer | 5 min | Questions on Step A before moving to Step B. |

### Step B (~50 min total)

| Sub-step | Expected wall-clock time | Notes |
|----------|--------------------------|-------|
| B.1 SITL reset + launch | 2–3 min | |
| B.2 Load params again | < 1 min | |
| B.3 Run orchestrator | 10–15 min | Includes 6 s wall-clock (60 s simulated) hover before GPS injection, then failsafe watch, then LAND+disarm. |
| B.4 Observe failsafe | 5 min | Students watch console for `EKF variance: over thresholds`. |
| B.5 Inspect log | 15–20 min | Running `mavlogdump.py --types ERR` and locating `Subsys : 16, ECode : 2`. Budget extra for students unfamiliar with the command line. |
| B.6 Record findings | 5–10 min | Students write three items: STATUSTEXT, mode at disarm, ERR row. |

**Total**: ~75 min. The Day 2 30-minute buffer is immediately after this lab — it exists specifically for students who need a second attempt on Step B or who want to explore edge cases.

**Speedup note**: the orchestrator uses `HOVER_SECONDS = 3` and `GPS_INJECT_T = 6` (both in wall-clock seconds at `--speedup 10`), corresponding to 30 simulated seconds of hover and 60 simulated seconds before GPS injection. This is deliberate: the student guide describes the sim-time values (30 s hover, 60 s before fault) so students understand what they are observing; the actual wall-clock wait is much shorter.

---

## Pre-arm setup checklist

Before students start:

- [ ] Labs L1 and L2 verified on each machine.
- [ ] `python3 -c "from pymavlink import DFReader; print('OK')"` succeeds (needed for log parsing in Step B).
- [ ] `mavlogdump.py --help` succeeds.
- [ ] Confirm the launch command includes `--out udp:127.0.0.1:14550` — the orchestrator connects via UDP, not TCP. Without this flag the orchestrator cannot connect.
- [ ] Confirm no stale SITL processes: `ps aux | grep arducopter`.
- [ ] Warn students: the orchestrator in Step B sets `SIM_GPS1_ENABLE = 0` automatically. They should not also set it manually from the MAVProxy terminal during the orchestrated run, or the timing will be off.
- [ ] Confirm students are running both commands from the repository root. The orchestrator's `find_latest_log()` searches for `logs/*.BIN` relative to the current working directory.

---

## Common student failures and what to say

**Exit code 6 — "EKF did not become healthy within timeout"**

Diagnostic: `python3 -c "from pymavlink import mavutil; m = mavutil.mavlink_connection('udp:127.0.0.1:14550'); print(m.recv_match(type='EKF_STATUS_REPORT', blocking=True, timeout=10))"` while SITL is running.

What to say: "SITL was not launched with `--out udp:127.0.0.1:14550`, or the EKF never acquired GPS lock. Restart SITL with the L3 launch script (`-w` to wipe EEPROM) and wait for `online system 1` before running the orchestrator."

**Exit code 2 — "EKF variance: STATUSTEXT not seen"**

Diagnostic: check the orchestrator output for `param SIM_GPS1_ENABLE = 0.0000` — if this line is missing, the GPS disable did not take effect.

What to say: "The GPS disable parameter was not written or acknowledged. The most common cause is that the SITL UDP port was not open when the orchestrator tried to send the param. Restart both SITL and the orchestrator."

**Exit code 3 — "mode did not change to LAND"**

Diagnostic: `param show FS_EKF_ACTION` in the MAVProxy terminal should read `1.0`. If it reads `0.0` (disabled), the failsafe is off.

What to say: "The `params.parm` file was not loaded, or was loaded with an error. Run `param load course/labs/intro-arducopter-aero-y1/l3-closing-lab/params.parm` in the MAVProxy terminal and confirm `FS_EKF_ACTION = 1.0`."

**Exit code 5 — "ERR row Subsys=16/ECode=2 not found in log"**

Diagnostic: `ls -la logs/*.BIN` from the repository root. If the directory does not exist or the file is zero bytes, the SITL binary did not write a log.

What to say: "SITL was not run from the repository root, so `logs/` was not created there. Run both `sim_vehicle.py` and the orchestrator from the repository root. The orchestrator's `find_latest_log()` function looks for `logs/*.BIN` relative to the current directory."

**Exit code 1 during Step A — "unexpected CRITICAL statustext"**

This usually means a parameter from a crashed Step B is still in EEPROM (e.g., `SIM_GPS1_ENABLE = 0`). Restart SITL with `-w` (wipe EEPROM) and reload `params.parm`.

**`mavlogdump.py` cannot open the log file**

Confirm the path uses the uppercase `.BIN` extension and that the file was written during the current SITL session. Stale logs from previous sessions in `logs/` will also appear; use the path printed by the orchestrator, which always points to the most recently modified file.

---

## Verdict signatures

### Step A

| Criterion | Signal | Pass threshold |
|-----------|--------|----------------|
| No CRITICAL statustext | STATUSTEXT.severity > 2 throughout | No `severity <= 2` message except `ARMED` |
| `Disarming motors` | STATUSTEXT.text contains `Disarming motors` | Within 180 s of arm |

### Step B

| Criterion | Signal | Pass threshold |
|-----------|--------|----------------|
| `EKF variance:` STATUSTEXT | STATUSTEXT.severity == 2, text starts `EKF variance:` | Within 30 s of `SIM_GPS1_ENABLE = 0` |
| Mode change to LAND | HEARTBEAT mode string == `LAND` | Within 30 s of injection |
| `Disarming motors` | HEARTBEAT `SAFETY_ARMED` flag clears | Within 240 s of original arm |
| ERR row in log | `DFReader` finds `ERR` with `Subsys=16, ECode=2` | Present in `logs/*.BIN` |

Exact STATUSTEXT strings:

| Text | Severity value | Source |
|------|---------------|--------|
| `EKF variance: over thresholds` | `2` (CRITICAL) | [ArduCopter/ekf_check.cpp:86](../../../../ArduCopter/ekf_check.cpp#L86) |
| `Disarming motors` | `6` (INFO) | ArduCopter disarm path |
| `LAND complete` | `6` (INFO) | ArduCopter LAND mode |

Dataflash ERR row:

```
ERR  {TimeUS : <N>, Subsys : 16, ECode : 2}
```

Source of `Subsys = 16`: `LogErrorSubsystem::EKFCHECK = 16` ([libraries/AP_Logger/AP_Logger.h:128](../../../../libraries/AP_Logger/AP_Logger.h#L128)).
Source of `ECode = 2`: `LogErrorCode::EKFCHECK_BAD_VARIANCE = 2` ([libraries/AP_Logger/AP_Logger.h:180](../../../../libraries/AP_Logger/AP_Logger.h#L180)).
Written at: [ArduCopter/ekf_check.cpp:83](../../../../ArduCopter/ekf_check.cpp#L83).

Orchestrator exit codes (for full reference):

| Code | Meaning |
|------|---------|
| `0` | All pass criteria met |
| `1` | Step A: CRITICAL statustext or disarm timeout |
| `2` | Step B: `EKF variance:` not seen within 30 s |
| `3` | Step B: mode did not change to LAND within 30 s |
| `4` | Step B: disarm timeout (> 240 s from arm) |
| `5` | Step B: `ERR Subsys=16/ECode=2` not found in log |
| `6` | EKF not healthy within timeout — hard fail, both steps |
| `10` | Connection or arm failure |

---

## Pointers to advanced material

- The full `ekf_check()` function at [ArduCopter/ekf_check.cpp:30-90](../../../../ArduCopter/ekf_check.cpp#L30-L90) is walked at *applied* depth in Module 2.3 before this lab. The scheduler entry `SCHED_TASK(ekf_check, 10, 75, 84)` at [ArduCopter/Copter.cpp:201](../../../../ArduCopter/Copter.cpp#L201) connects the 10 Hz rate to the `EKF_CHECK_ITERATIONS_MAX = 10` constant, explaining the ~1 s latency from variance threshold crossing to failsafe fire.

- The downstream GNC plane course introduces the EKF3 multi-lane architecture and the `checkLaneSwitch()` function. That mechanism (proactive lane switching when a secondary IMU lane is healthier) is distinct from the failsafe path (reactive LAND when the primary EKF is confirmed bad). Prepare students for the distinction: "what you observed here is the failsafe — the EKF told the autopilot it was broken and the autopilot reacted. The downstream course covers a different path: the EKF proactively switching lanes before anything breaks."

- The `FS_EKF_THRESH` parameter (set to `0.8` in `params.parm`) is defined at `ArduCopter/config.h:106` as `FS_EKF_THRESH_DEFAULT`. Students who ask "how bad does it have to get?" can look at the `ekf_over_threshold()` function — but do not walk it in class; it is internals depth. Point them to it as optional reading.

- `mavlogdump.py` is the same tool used by the downstream course's MAVExplorer-based log inspection modules. The `--types ERR` flag is one instance of a general pattern: `--types CTUN`, `--types GPS`, `--types XKF4` are all used in the downstream courses. Students who are curious can run `mavlogdump.py --help` to see the full list.
