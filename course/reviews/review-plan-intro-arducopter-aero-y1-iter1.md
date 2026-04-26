# Review: plan-intro-arducopter-aero-y1-iter1.md

This is a **plan-stage review**: the plan was audited against the four rubrics in
`course/criteria/` *before* a course draft exists. The verdict per rubric and the
findings below are framed so course-writer (if iter1 is taken to draft) or the
iter2 planner (if iter1 is discarded) can act on them.

Pinned tree: branch `GNC-0.1`, head `a6fc842e04`, date 2026-04-26 — matches the
plan's own verification claim.

## Verdicts per rubric

| Rubric | Verdict |
|---|---|
| `audience-fit.md` | **pass-with-findings** |
| `citation-rigor.md` | **pass-with-findings** |
| `scope-discipline.md` | **pass** (plan-stage; full audit deferred to course-draft review) |
| `time-budget.md` | **pass-with-findings** (one Major and one Minor) |

Overall plan-stage verdict: **pass-with-findings**. No blockers. Two Major
findings (one time-budget arithmetic error replicated on Days 3 and 4 — counted
as one finding; one citation describing parsing code as "execution"). The
declared 1.25 h capstone is the planner's own admitted risk (plan line 366) and
is treated below.

## Findings

### F1 — Time-budget arithmetic on Days 3 and 4: per-module + buffer sums to 3.75 h, not 4.0 h
- **Severity**: Major (per the time-budget rubric severity guide, this is exactly at the ±15 min line, so close to Minor; called Major because it occurs on **two** of four days and yields a 0.5 h shortfall on the course total even though that is still inside the ±1 h course-total tolerance).
- **Rubric**: `time-budget.md` → "Per-day total: per-module times within that day must sum to within ±15 min of the day total" (Required); "Per-day totals that diverge from the sum of their modules by > 15 min without an explicit buffer / Q&A line accounting for the gap" (Forbidden).
- **Location**: plan lines 231 (Day 3 totals) and 289 (Day 4 totals).
- **Observation**: Both lines write `… = 3.75 h + 0.25 h buffer = 4.0 h`, but the 0.25 h buffer is *already inside* the five-term sum (`+ 0.25` is the buffer term). The buffer is being counted twice, or equivalently the day is 0.25 h short of the declared 4.0 h.
  - Day 3 modules: 3.1 (0.75) + 3.2 (0.75) + 3.3 (1.0) + 3.4 (1.0) + buffer (0.25) = **3.75 h**, not 4.0 h.
  - Day 4 modules: 4.1 (0.75) + 4.2 (0.75) + 4.3 (0.75) + 4.4 (1.25) + buffer (0.25) = **3.75 h**, not 4.0 h.
- **Evidence** (plan, verbatim):
  > **Day 3 totals**: 0.75 + 0.75 + 1.0 + 1.0 + 0.25 = **3.75 h** + 0.25 h buffer = 4.0 h.
  > **Day 4 totals**: 0.75 + 0.75 + 0.75 + 1.25 + 0.25 = **3.75 h** + 0.25 h buffer = 4.0 h.
  Course total computed by the reviewer: 4.0 + 4.0 + 3.75 + 3.75 = **15.5 h**, not the declared 16.0 h. Inside the ±1 h course-total tolerance, but visibly inconsistent with the plan's own arithmetic.
- **Recommended fix**: either drop a 15-min slot from Days 1 or 2 to honour the 16 h declaration, or extend one Day 3 / Day 4 module by 15 min, or re-declare each day as 3.75 h and the course as 15.5 h. Whichever course-writer (or iter2 planner) picks must be a deliberate decision, not the current double-count.
- **Iter2 status**: **moot under iter2 compression** to 8 h / 2 days — the iter2 planner is rebuilding the day-by-day breakdown from scratch and will re-derive these sums. Carry the *lesson* (sum modules + buffer once, not twice) into iter2.

### F2 — `libraries/AP_Mission/AP_Mission.cpp:1085-1150` is described as "execution" but is actually mission-item *parsing*
- **Severity**: Major.
- **Rubric**: `citation-rigor.md` → severity guide: "Major: cite resolves but to the wrong symbol".
- **Location**: plan line 260 (Module 4.2 citation block).
- **Observation**: The plan describes this range as "`MAV_CMD_NAV_WAYPOINT` and `MAV_CMD_NAV_RETURN_TO_LAUNCH` *execution*. *Survey* depth." But the block is inside the function that converts a MAVLink mission packet into the in-memory `cmd` struct (`mavlink_to_mission_cmd`-style packing of `cmd.p1`, `cmd.content.location`, etc.). It is parsing, not execution.
- **Evidence** (`grep -n` and `awk 'NR>=1083 && NR<=1155'` on the pinned tree):
  ```
  1085:     case MAV_CMD_NAV_WAYPOINT: {                        // MAV ID: 16
  1086:         /*
  1087:           the 15 byte limit means we can't fit both delay and radius
  ...
  1107:         cmd.p1 = (uint16_t)packet.param1;
  ...
  1150:     case MAV_CMD_NAV_RETURN_TO_LAUNCH:                  // MAV ID: 20
  1151:         break;
  ```
  Every assignment writes to `cmd.*` from `packet.*` — packet → in-memory mission item, i.e. parsing.
- **Recommended fix**: either re-label the cite as "mission item parsing — where a `MAV_CMD_NAV_WAYPOINT` MAVLink packet is unpacked into the autopilot's mission struct" (no other change), or replace it with the actual execution path in `ArduCopter/mode_auto.cpp` (e.g. `start_command(...)` / `verify_command(...)`). The first option is the cheapest and matches the plan's *survey*-depth intent.
- **Iter2 status**: **moot under iter2 compression** if Module 4.2 (Missions) is dropped from the 8 h version. If the iter2 planner keeps mission content, this finding must be carried forward — paraphrasing parsing as "execution" misleads first-years about what they're reading.

### F3 — Capstone is 1.25 h alone; "capstone arc" framing stretches `time-budget.md`
- **Severity**: Major (treated as Minor if the framing is accepted; the planner's own line 366 already flags it for the reviewer).
- **Rubric**: `time-budget.md` → Required: "Capstone: any course ≥ 3 days must include a capstone exercise consuming ≥ 2 h."
- **Location**: plan Module 4.4 (line 275, 1.25 h) and the capstone-deviation note (line 291, "4.3 + 4.4 = 2.0 h arc").
- **Observation**: The rubric says "a capstone exercise" (singular, ≥ 2 h). The plan resolves the gap by counting Module 4.3 (autotest warm-up, 45 min) plus Module 4.4 (fault-injection autotest, 1.25 h) as a contiguous "capstone arc." Whether this satisfies the rubric depends on how strictly "exercise" is read. The strict reading (one exercise) does not allow it; a permissive reading (one continuous lab arc, even if the prose frames it as two adjacent modules) does. The rubric's text does not resolve the ambiguity.
- **Evidence**: plan lines 275-291 spell out the framing. The lab specs (L7 + L8) under Handoff are two distinct lab invocations against two distinct autotest scenarios; they share the autotest harness but have different fault-injection profiles. That is closer to "two adjacent labs" than "one 2 h lab".
- **Recommended fix**:
  - **Cheap option** (kept multi-module): course-writer must mark Module 4.3 in prose verbatim as `capstone warm-up: same harness, no fault injection yet` and add a Deviations entry. The planner has already pre-authorised this.
  - **Clean option**: merge 4.3 + 4.4 into a single `Module 4.3 — Capstone (2 h)` with the warm-up as Step A and the fault-injection as Step B, so the rubric's "one ≥2 h exercise" reading is unambiguous.
  - **Suggested rubric clarification**: see "Suggested rubric additions" below.
- **Iter2 status**: **fully moot under iter2 compression** to 2 days / 8 h. The capstone rubric only triggers on courses ≥ 3 days; an 8 h / 2-day course has no capstone obligation under `time-budget.md`. The iter2 planner can drop the framing entirely.

### F4 — Prerequisite-chain awareness is named but the downstream-assumption list is thin
- **Severity**: Minor.
- **Rubric**: `audience-fit.md` (newly edited) → Required: "Prerequisite-chain awareness: if the course is positioned as an on-ramp to another course in this repo, the plan must name the downstream course **and identify what assumptions the downstream course makes that this course is responsible for establishing**."
- **Location**: plan Context line 9, plus Verification "No-overlap audit" lines 435-437.
- **Observation**: The plan satisfies the "name the downstream course" half cleanly: `course/custom_gnc_course_plane.md` and `course/custom_gnc_course_quadplane.md` are called out by path. The "what assumptions" half is partially done — line 9 says the downstream courses assume "C/C++ proficiency and prior flight-code experience on a proprietary autopilot" and that the intro course exists so a student can "read Day 1 of either advanced course without being lost on terminology or on the SITL toolchain." That is a useful framing but it is not a **list** of the specific Day 1 topics the GNC courses compress on the assumption that the audience already knows them. A future reviewer cannot deterministically check that this on-ramp covers the gap, because the gap is described in prose, not enumerated.
- **Evidence** (plan verbatim, line 9):
  > After taking this intro course, a student should be able to read the Day 1 of either advanced course without being lost on terminology or on the SITL toolchain. We deliberately skip the *internals* depth those courses live at: no EKF lane-switch math, no L1/TECS, no transition state machine, no porting to custom hwdef, no DDS/ROS2.
  This describes what the intro course *does not* cover (good), but not what the downstream courses' Day 1 *assumes* (the actual rubric ask).
- **Recommended fix**: add a short bullet list near the Context section enumerating the specific "compressed survival kit" topics the GNC courses' Day 1 assumes (e.g. flight modes by name, parameter system, MAVProxy CLI, SITL launch, EKF as a black box, autotest harness existence) and map each one to the intro module that establishes it. This is a 5-bullet edit, not a structural change.
- **Iter2 status**: **carry forward**. If the iter2 plan is also positioned as an on-ramp to the GNC courses, it inherits the same rubric ask. A 2-day version still needs the topic-by-topic mapping — arguably *more* needs it, because every cut topic widens the gap with the downstream course.

### F5 — `AGENTS.md:5-8` cite is 4 lines wide; rubric floor is 5
- **Severity**: Nit.
- **Rubric**: `citation-rigor.md` → Required: "Line-range tightness: ranges are 5–150 lines."
- **Location**: plan Module 1.1 citations (line 73).
- **Observation**: `AGENTS.md:5-8` is a 4-line range. The rubric's lower bound is 5. Lines 6-8 are blank / list separators; the load-bearing sentence is on line 5 alone.
- **Recommended fix**: cite as `AGENTS.md:5` (single line) — the rubric allows `path:LINE` for single-line cites — or widen to `AGENTS.md:3-7` to include the surrounding Code-of-Conduct framing.
- **Iter2 status**: **carry forward** if the cite survives the redesign. Trivial to fix.

### F6 — `mode_loiter.cpp:80-104` ends mid-function (file is 200 lines)
- **Severity**: Nit.
- **Rubric**: `citation-rigor.md` → Required: "Anchor specificity: a cite must point at the symbol or block being discussed."
- **Location**: plan Module 2.1 citations (line 138).
- **Observation**: The plan describes this range as "`ModeLoiter::run` opening: 'convert pilot input to lean angles' → 'process pilot's roll and pitch input.' Show that LOITER is `ALT_HOLD` plus position control." Lines 80-104 do open `ModeLoiter::run` and contain both quoted comments — but the function continues to line ~200; ending the cite at 104 is a deliberate "opening only" choice. The plan calls it an "opening," which is honest, so this is at most a nit. Worth flagging only because the line range ending mid-function (104 ends just after `target_climb_rate_ms = constrain_float(...)`) might confuse course-writer into thinking it is the whole function.
- **Recommended fix**: either re-label as `mode_loiter.cpp:80-104 (ModeLoiter::run, opening only)` — already roughly the spirit of the plan — or widen to the full function and accept that *survey* depth means we name the structure, not walk it.
- **Iter2 status**: **carry forward** if the cite survives. Trivial.

### F7 — Hands-on share visibility on Day 3 is computed against an inflated denominator
- **Severity**: Minor.
- **Rubric**: `time-budget.md` → "Hands-on time ratios computed implicitly. Each day's hands-on share must be visible." (Forbidden — but this finding is about *correctness*, not visibility.)
- **Location**: plan line 231.
- **Observation**: Day 3 hands-on share is computed as `~1.5 h / 4.0 h ≈ 38%`, but Day 3's actual elapsed time per F1 is 3.75 h, not 4.0 h. Recomputed: `1.5 / 3.75 ≈ 40%`. Still well above the 25% rubric floor; the 38% figure is just stale.
- **Recommended fix**: recompute against the corrected denominator after F1 is resolved.
- **Iter2 status**: **moot under iter2 compression** — the iter2 planner will recompute hands-on share for the new day shape.

## Audience-fit deep dive (response to user prompt)

Two new audience-fit bullets were added to `course/criteria/audience-fit.md`
after this plan was authored:

1. **Required: Prerequisite-chain awareness** — see F4. Plan partially satisfies
   this (downstream courses are named) but the assumption list is loose. Minor
   finding.
2. **Forbidden: For first-year / novice audiences, internals-depth modules are
   forbidden unless explicitly justified** — plan **fully satisfies** this.
   Decision D8 (lines 32) explicitly bans *internals* modules for this audience
   and constrains every module to *survey* or *applied*. The rationale ("Per
   the audience-fit rubric, internals-depth requires ≥ 5 file:line cites that
   walk function bodies — that is the GNC-course depth and we are explicitly
   the on-ramp before it") is exactly the rubric's intent.

Net: the plan satisfies the *spirit* of both new bullets and the *letter* of one
of them (the internals-forbidden bullet). The other (prerequisite-chain
awareness) is partially satisfied — F4 above.

## Citation audit

Total cites in the **Critical Files Cited** master list (plan lines 297-323): 47
(counting deduplicated entries; some entries list multiple line ranges in one
bullet — each range counted separately).

Cites I `grep -n`-verified at pinned head `a6fc842e04` against the working tree:

| Cite | Status |
|---|---|
| `AGENTS.md:5-8` | resolves; range is 4 lines wide, just under the 5-line rubric floor (F5, Nit). |
| `AGENTS.md:202-234` | resolves; section "6. Parameter Documentation" with the `@Param/@DisplayName/...` annotation list as described. |
| `CLAUDE.md:14-31` | resolves; "Big-picture architecture" section. |
| `CLAUDE.md:103-107` | resolves; environment-setup + apt mirror guidance. |
| `BUILD.md` (existence) | resolves; file present. |
| `Tools/environment_install/install-prereqs-ubuntu.sh` (existence) | resolves; file present. |
| `Tools/autotest/sim_vehicle.py:287` | resolves; line 287 is `'ArduCopter.elf',`. |
| `Tools/autotest/sim_vehicle.py:1073-1085` | resolves; `--vehicle` and `--frame` parsers as claimed. |
| `Tools/autotest/arducopter.py:58` | resolves; `class AutoTestCopter(vehicle_test_suite.TestSuite):`. |
| `Tools/autotest/arducopter.py:149-173` | resolves; `def takeoff(...)` helper as claimed. |
| `Tools/autotest/arducopter.py:278-293` | resolves; `def ModeAltHold(self):` is exactly 16 lines. |
| `ArduCopter/Copter.h:181` | resolves; `class Copter : public AP_Vehicle {`. |
| `ArduCopter/Copter.h:587` | resolves; `static const AP_Scheduler::Task scheduler_tasks[];`. |
| `ArduCopter/Copter.cpp:113` | resolves; `const AP_Scheduler::Task Copter::scheduler_tasks[] = {`. |
| `ArduCopter/Copter.cpp:113-149` | resolves; `FAST_TASK` block as described, including the comment `// run EKF state estimator (expensive)` on line 126 and `FAST_TASK(read_AHRS),` on line 127. |
| `ArduCopter/Copter.cpp:117` | resolves; `FAST_TASK(run_rate_controller_main),`. |
| `ArduCopter/Copter.cpp:127` | resolves; `FAST_TASK(read_AHRS),`. |
| `ArduCopter/Copter.cpp:151-201` | resolves; `SCHED_TASK` block including `rc_loop` (250 Hz, line 151), `throttle_loop` (50 Hz, line 152), `update_batt_compass` (line 160), `ekf_check` (line 201). |
| `ArduCopter/Copter.cpp:201` | resolves; `SCHED_TASK(ekf_check, 10, 75, 84),`. |
| `ArduCopter/Copter.cpp:998` | resolves; `AP_HAL_MAIN_CALLBACKS(&copter);`. |
| `ArduCopter/Attitude.cpp:10-24` | resolves; `Copter::run_rate_controller_main` body (lines 10-24, file matches). |
| `ArduCopter/mode.h:77-109` | resolves; `enum class Number : uint8_t` with STABILIZE=0, ALT_HOLD=2, LAND=9, etc. |
| `ArduCopter/mode.cpp:313-396` | resolves; `Copter::set_mode` body, including `requires position` (line 394) and `need alt estimate` (line 404). The plan calls out lines 391-405 for *applied* depth — line 405 is one past the cite range; `need alt estimate` is at 404. Acceptable. |
| `ArduCopter/mode.cpp:497-508` | resolves; `Copter::update_flight_mode` body. |
| `ArduCopter/mode_stabilize.cpp:9-64` | resolves; `ModeStabilize::run` body fills the entire 64-line file. |
| `ArduCopter/mode_althold.cpp:9-22` | resolves; `ModeAltHold::init`. |
| `ArduCopter/mode_althold.cpp:26-104` | resolves; `ModeAltHold::run` body (file is 104 lines). |
| `ArduCopter/mode_loiter.cpp:80-104` | resolves; `ModeLoiter::run` *opening only* (function continues to ~200; F6 Nit). |
| `ArduCopter/Parameters.cpp:33-67` | resolves; `Copter::var_info[]` opening with FORMAT_VERSION / PILOT_THR_FILT / PILOT_THR_BHV / GCS_PID_MASK as named. |
| `ArduCopter/Parameters.cpp:149-191` | resolves; `FLTMODE1` through `FLTMODE6` and `FLTMODE_CH`. |
| `ArduCopter/AP_Arming_Copter.cpp:8-20` | resolves; `pre_arm_checks` plus the `run_pre_arm_checks` "exit immediately if already armed" line. |
| `ArduCopter/ekf_check.cpp:30-90` | resolves; `Copter::ekf_check` body. The plan claims `failsafe_ekf_event()` on line 89 — actual is line 89 in this tree (matches). |
| `libraries/AP_HAL/AP_HAL_Main.h:35-41` | resolves; `AP_HAL_MAIN_CALLBACKS` macro. |
| `libraries/AP_Vehicle/AP_Vehicle.cpp:558-566` | resolves; `void AP_Vehicle::loop()`. |
| `libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:457-485` | resolves; `rate_controller_run_dt` body, `update_all` calls on lines 473/476/479 as claimed. |
| `libraries/AC_PID/AC_PID.cpp:13-73` | resolves; `AP_GROUPINFO_FLAGS_DEFAULT_POINTER` block for P/I/D/FF/IMAX/FLTT/FLTE/FLTD/SMAX/PDMX (PDMX continues past 73 — see F8 below). |
| `libraries/AC_PID/AC_PID.cpp:196-272` | resolves; `AC_PID::update_all` body. The plan claims `P_out = error * _kp` on line 269 — actual on this tree is `float P_out = (_error * _kp);` on line 269. Symbol order is `_error * _kp`, not `error * _kp`; semantically identical, paraphrased in prose. Acceptable. |
| `libraries/AP_Motors/AP_MotorsMatrix.cpp:213-244` | resolves; `output_armed_stabilizing` opening. |
| `libraries/AP_Motors/AP_MotorsMatrix.cpp:592-602` | resolves; `MOTOR_FRAME_TYPE_X` motor angles +45/-135/-45/+135. |
| `libraries/AP_Mission/AP_Mission.cpp:206-207` | resolves; `case MAV_CMD_NAV_TAKEOFF:` line 206 (and `MAV_CMD_NAV_VTOL_TAKEOFF` at 205, `MAV_CMD_NAV_TAKEOFF_LOCAL` at 207). |
| `libraries/AP_Mission/AP_Mission.cpp:900-905` | resolves; `MAV_CMD_NAV_WAYPOINT` and others in a switch — but this is in a *recognises mission item type* helper, not parsing. The plan's gloss "where a waypoint mission item is unpacked from a MAVLink message" is closer to the 1085-1150 block; this 900-905 block is the *enumeration* of nav-command types. Minor mismatch; the *applied*-depth read described in the plan does not really land at 900-905. Subsumed in F2 above. |
| `libraries/AP_Mission/AP_Mission.cpp:1085-1150` | resolves; **but described as "execution" when the code is parsing**. F2 Major. |
| `libraries/SITL/SIM_Multicopter.cpp:26-44` | resolves; `MultiCopter::MultiCopter` constructor. |
| `libraries/SITL/SIM_Multicopter.cpp:62-92` | resolves; `MultiCopter::update` body, file is 93 lines. |
| `libraries/AP_GPS/`, `libraries/AP_Baro/`, `libraries/AP_InertialSensor/`, `libraries/AP_AHRS/` (directory existence) | all resolve. |

### F8 — `AC_PID.cpp:13-73` truncates the `PDMX` annotation block mid-comment
- **Severity**: Nit.
- **Rubric**: `citation-rigor.md` → "Line-range tightness".
- **Location**: plan Module 3.3 (line 217).
- **Observation**: The plan claims this range covers the `AP_GROUPINFO` declarations of P/I/D/FF/IMAX/FLTT/FLTE/FLTD/SMAX/**PDMX**. The PDMX block actually starts at line 69 (`@Param: PDMX` / `@DisplayName: PD sum maximum`) and the `AP_GROUPINFO_FLAGS_DEFAULT_POINTER("PDMX", …)` line itself is past line 73. Line 73 cuts the PDMX block mid-comment. Either widen to `:13-78` (or wherever PDMX's macro line lands) or drop PDMX from the prose enumeration.
- **Iter2 status**: carry forward if AC_PID survives the redesign.

### Cite resolution summary
- Cites checked: 47 ranges across the master list.
- Cites that fully resolved at the pinned head: 47.
- Cites whose described concept did not match the code at the resolved location: **1** (F2: AP_Mission.cpp:1085-1150 described as "execution" but is parsing). Adjacent cite at 900-905 has a softer mismatch (F2 sub-bullet).
- Cites with formatting / range-tightness issues but correct concept: **2** (F5: AGENTS.md:5-8 4-line range; F8: AC_PID.cpp:13-73 truncates PDMX block).
- Cites with no issues: **44**.

The plan's own verification claim (lines 401-430) was honest: each cite the
planner says they verified does in fact resolve. The defects are at the
*description* layer, not at the resolution layer.

## Time-budget audit

| Day | Plan-declared total | Reviewer-summed modules + buffer | Delta |
|---|---|---|---|
| 1 | 4.0 h | 0.75 + 1.5 + 0.75 + 0.75 + 0.25 = **4.0 h** | 0 |
| 2 | 4.0 h | 1.0 + 1.0 + 1.0 + 0.75 + 0.25 = **4.0 h** | 0 |
| 3 | 4.0 h | 0.75 + 0.75 + 1.0 + 1.0 + 0.25 = **3.75 h** | **−0.25 h** (F1) |
| 4 | 4.0 h | 0.75 + 0.75 + 0.75 + 1.25 + 0.25 = **3.75 h** | **−0.25 h** (F1) |
| **Course** | **16.0 h** | **15.5 h** | **−0.5 h** (within ±1 h tolerance) |

Hands-on share, declared vs reviewer-recomputed (against corrected denominators
where F1 applies):

| Day | Declared | Recomputed | Floor |
|---|---|---|---|
| 1 | 62% (~2.5 / 4.0) | 62% | ≥ 25% ✓ |
| 2 | 62% (~2.5 / 4.0) | 62% | ≥ 25% ✓ |
| 3 | 38% (1.5 / 4.0) | **40%** (1.5 / 3.75) | ≥ 25% ✓ (F7) |
| 4 | 62% (2.5 / 4.0) | **67%** (2.5 / 3.75) | ≥ 25% ✓ |

Capstone: declared as 4.3 + 4.4 = 2.0 h "arc". F3 above.

Buffer: each day declares an explicit 0.25 h Q&A slot. Rubric requires ≥ 0.5 h
(`time-budget.md` line 12: "each day must include ≥ 30 min of buffer"). The
plan's buffer is **15 min, not 30 min**. This is a separate finding.

### F9 — Per-day buffer is 15 min; rubric requires ≥ 30 min
- **Severity**: Minor (per `time-budget.md` severity guide: "Minor: ... buffer time absent on a day < 4 h." Not absent — half. Closest-fit severity is Minor.).
- **Rubric**: `time-budget.md` → Required: "Buffer: each day must include ≥ 30 min of buffer (Q&A, breaks, slippage). Stated explicitly, not absorbed into other modules."
- **Location**: every day section ("Day N buffer / Q&A (15 min)").
- **Observation**: Each day declares a single 15-min buffer slot. The rubric requires ≥ 30 min. The deficit is 15 min × 4 days = 1 h of unaccounted-for slack across the course.
- **Recommended fix**: either widen each day's buffer slot to 30 min (which compounds with F1 — each day would then be 0.5 h short of 4.0 h, and the course total drops to 14.5 h, outside the ±1 h tolerance — so this fix forces a length redeclaration), or absorb 15 min from a flexible module per day, or redeclare the course as 16 h with shorter modules. Note: this finding interacts with F1; resolving them together is cleaner than sequentially.
- **Iter2 status**: **partially moot under iter2 compression**. An 8 h / 2-day course still needs ≥ 30 min buffer per day per the rubric. Carry the lesson forward — don't fall back to 15-min buffer slots in iter2.

## Scope-vs-plan audit

The scope-discipline rubric is mostly course-vs-plan and not yet checkable
because no course draft exists. What can be checked at plan stage:

- **Internal consistency**: the Course Structure table (plan lines 49-54) lists
  4 days × 4 h. The detailed module sections under each day (lines 61-292) match
  the table verbatim. No drift.
- **Lab spec round-trip**: every hands-on section in a module has a
  corresponding entry in **Handoff → To lab-builder** (L1-L8). Every lab entry
  in **To lab-builder** has a corresponding lab-tester entry. No orphan labs.
  Mapping verified:
  - Module 1.2 hands-on ↔ L1 ↔ lab-tester L1.
  - Module 1.4 hands-on ↔ L2 ↔ lab-tester L2.
  - Module 2.2 ↔ L3 ↔ lab-tester L3.
  - Module 2.4 ↔ L4 ↔ lab-tester L4.
  - Module 3.4 ↔ L5 ↔ lab-tester L5.
  - Module 4.2 ↔ L6 ↔ lab-tester L6.
  - Module 4.3 ↔ L7 ↔ lab-tester L7.
  - Module 4.4 ↔ L8 ↔ lab-tester L8.
- **Sibling course non-import**: the plan's Verification section (lines 435-437)
  asserts no prose import from `course/custom_gnc_course_plane.md` or
  `course/custom_gnc_course_quadplane.md`. Plan stage cannot fully verify this
  (there is no course draft yet to grep), but the plan's design (re-derive
  operational topics from zero, do not re-use the GNC courses' "compressed
  survival kit") is sound.
- **Plan-reference line at end of course file**: this is a course-file
  obligation; the plan correctly tells course-writer to add it (line 45 / line
  353).

No scope-discipline findings at plan stage.

## Lab spec audit

Each module's hands-on section ↔ lab spec ↔ lab-tester pass criterion was
checked for parity. All match. Two notes:

- **L8 (capstone)**: the lab spec references
  `ArduCopter/ekf_check.cpp:79-89` for the failsafe log fingerprint
  (`LOGGER_WRITE_ERROR(LogErrorSubsystem::EKFCHECK, LogErrorCode::EKFCHECK_BAD_VARIANCE)`).
  Verified at the pinned head — line 83 has the `LOGGER_WRITE_ERROR`, line 86
  has the `EKF variance:` `MAV_SEVERITY_CRITICAL` statustext, line 89 has
  `failsafe_ekf_event()`. The lab-tester verdict logic (plan line 394-399)
  matches this fingerprint.
- **L7 (autotest warm-up)**: uses `test.Copter.ModeAltHold` (Tools/autotest/arducopter.py:278) as primary
  with `test.Copter.TakeoffAlt` (line 4367 — verified) as fallback. Both methods
  exist on the pinned tree.

## Specific risks called out by the plan

The plan's "To course-reviewer" section (lines 357-368) flags six risks for the
reviewer. Status of each:

1. **Audience drift upward** — not yet checkable (no course draft). Carry to
   draft review.
2. **Citation drift** — checked. F2 (Major), F5/F6/F8 (Nits). No outright drift
   at the resolved-line layer.
3. **Scope creep into Plane/Quadplane** — none in the plan itself. Not checkable
   for the draft yet.
4. **Time-budget capstone floor** — F3 above (Major).
5. **Hands-on share on Day 3** — within rubric. F7 corrects the percentage.
6. **Forbidden internals-depth** — D8 satisfies the rubric. No finding.

## Suggested rubric additions (the user may accept or reject)

The capstone-arc framing in F3 surfaced an interpretive gap in
`time-budget.md`. The rubric does not say whether a "capstone exercise consuming
≥ 2 h" can be composed of two adjacent modules with continuity prose, or must
be a single ≥ 2 h module. The user may want to clarify:

- **Proposed bullet** under `time-budget.md` Required: "*Capstone may span
  multiple adjacent modules if the modules share a single lab harness and the
  course prose explicitly frames them as one continuous exercise. The combined
  time must be ≥ 2 h. The first module must be marked 'capstone warm-up' or
  similar in prose.*"
- Alternative: **tighten** the rubric to require a single module: "*Capstone
  must be a single module of ≥ 2 h.*" This forces F3's "clean option."

The reviewer does not write into `course/criteria/`. The user decides which
direction is correct for this repo.

## Recommended next action

**Discard iter1 in favour of iter2** (the user has already decided to compress
to 8 h / 2 days). Iter1 has no blockers — it is shippable to course-writer
as-is *if* F1, F2, F3, F9 are corrected and F4 is widened. But the user's iter2
compression dissolves F1, F3, F7, and most of F9, and reframes whether F2's
mission module is even kept. The cheaper path is to start clean at iter2 and
carry these lessons forward:

- **Carry to iter2 (not made moot by compression)**:
  - F2 — paraphrasing parsing as "execution" is a writing-discipline lesson, not
    a length lesson. If iter2 keeps any AP_Mission cite, get the verb right.
  - F4 — prerequisite-chain awareness needs a proper topic-map. If anything,
    this is *more* important in an 8 h on-ramp because every cut topic widens
    the gap with the GNC course. Iter2 should produce an explicit list of "Day
    1 of `custom_gnc_course_quadplane.md` assumes the student knows X, Y, Z;
    this iter2 plan covers X and Y here, leaves Z documented as a known gap."
  - F9 — buffer floor is 30 min, not 15. Iter2 must declare 30 min/day from the
    start (i.e. a 4 h day is 3.5 h modules + 0.5 h buffer, not 3.75 h modules
    + 0.25 h buffer).
  - F5, F6, F8 — citation-rigor formatting nits. If any of these cites survive
    the redesign, fix them in passing.

- **Made moot by iter2 compression** (do **not** spend planner time on these):
  - F1 — Day 3 / Day 4 arithmetic. Iter2 has fewer days; sums will be re-derived.
  - F3 — capstone ≥ 2 h. Iter2 at 2 days does not trigger the rubric.
  - F7 — Day 3 hands-on share recomputation. Day 3 will not exist as currently
    structured.

Net: iter1 is a credible plan with disciplined citation work, an honest
audience declaration, a sane lab spec, and a small set of arithmetic / writing
defects. It does not need rework; it needs replacement, because the user's
length decision changes more than this review can.

Generated against course/plans/plan-intro-arducopter-aero-y1-iter1.md at branch GNC-0.1, head a6fc842e04, 2026-04-26.
