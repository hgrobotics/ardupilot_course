# Plan: Introduction to ArduCopter for First-Year Aerospace Engineering Students (iter 2)

Supersedes [plan-intro-arducopter-aero-y1-iter1.md](plan-intro-arducopter-aero-y1-iter1.md). Cuts D-cut1..D-cut3 to fit the user's rescoped 8 h / 2-day budget. Carries forward F2, F4, F9 from [review-plan-intro-arducopter-aero-y1-iter1.md](../reviews/review-plan-intro-arducopter-aero-y1-iter1.md). Findings F1, F3, F7 from that review are made moot by the day-count compression and are not addressed here. Findings F5, F6, F8 (citation-rigor nits) are addressed in passing where the underlying cite survives.

All `file:line` cites in this plan are clickable markdown links per the new **Clickable rendering** bullet in [citation-rigor.md](../criteria/citation-rigor.md). The link path prefix from `course/plans/` to top-level repo dirs is `../../`.

Pinned tree: branch `GNC-0.1`, head `a6fc842e04`, date 2026-04-26.

## Context

- **Audience**: 1st-year aerospace engineering undergraduates. High-school physics in hand, basic calculus *in progress* (so we use derivatives/integrals as intuition only — no proofs, no Jacobians). **No prior controls theory, no prior embedded systems, no prior Linux/CLI fluency, no prior programming.** Many will be using a terminal for the first time during the course.
- **Course length**: **8 hours total, delivered as 2 days × 4 h** (locked by user). Per [time-budget.md](../criteria/time-budget.md), per-day totals must sum to within ±1 h of the course total (i.e. course total declared as 8 h; reviewer tolerance allows 7–9 h).
- **Format**: in-person, in a TA-supported computer lab. Each student has a laptop on which we install the ArduPilot SITL toolchain in Module 1.2. **Pure SITL — no real flight, no bench hardware, no instructor demo flight** (locked).
- **Vehicle target**: **ArduCopter (quadrotor X frame)** end-to-end. No Plane/Rover/Sub. Quad is the easiest mental model for first-years (4 motors, 1 frame, no wings, no servos, no airspeed).
- **Programming surface**: **read-only code citations**. Students inspect ArduPilot source in an editor with the instructor; they never compile a modification, write Python, or author a script (locked).
- **Positioning**: **prerequisite-style on-ramp** to [`course/custom_gnc_course_plane.md`](../custom_gnc_course_plane.md) and [`course/custom_gnc_course_quadplane.md`](../custom_gnc_course_quadplane.md). After taking this intro, a student should be able to read Day 1 of either advanced course without being lost on terminology or on the SITL toolchain. The downstream-assumption mapping is enumerated below in **Decisions → Prerequisite-chain assumption map** (addresses F4).
- **Constraints**: pure SITL on student laptops; no airspace, no logistics, no liability; per-day cap = 4 h to fit a single morning or afternoon block plus break.
- **Iteration number**: iter 2, supersedes [plan-intro-arducopter-aero-y1-iter1.md](plan-intro-arducopter-aero-y1-iter1.md). One prior review exists ([review-plan-intro-arducopter-aero-y1-iter1.md](../reviews/review-plan-intro-arducopter-aero-y1-iter1.md)). No prior lab runs (the `course/labs/` directory is empty).

## Lessons Applied

Findings carried forward from [review-plan-intro-arducopter-aero-y1-iter1.md](../reviews/review-plan-intro-arducopter-aero-y1-iter1.md):

- **Source**: review F1.
  - **Severity**: Major.
  - **Finding**: Day-3 / Day-4 buffer counted twice in the per-day arithmetic.
  - **Action this iteration**: **Moot under iter2 compression** — the day structure is rebuilt from scratch. Lesson carried: each day's per-module times are summed once and the explicit buffer line is the *only* slack; no double-counting.

- **Source**: review F2.
  - **Severity**: Major.
  - **Finding**: [`libraries/AP_Mission/AP_Mission.cpp:1085-1150`](../../libraries/AP_Mission/AP_Mission.cpp#L1085-L1150) was described as `MAV_CMD_NAV_WAYPOINT` *execution* but is mission-item *parsing* (`packet.*` → `cmd.*`).
  - **Action this iteration**: **Mission content is dropped entirely (D-cut1)**, so the cite does not appear in iter2. If a future iteration restores mission content, the correct *execution* anchors are [`ArduCopter/mode_auto.cpp:698-713`](../../ArduCopter/mode_auto.cpp#L698-L713) (`ModeAuto::start_command` dispatch table where `cmd.id == MAV_CMD_NAV_WAYPOINT` calls `do_nav_wp(cmd)`), [`ArduCopter/mode_auto.cpp:1575-1614`](../../ArduCopter/mode_auto.cpp#L1575-L1614) (`do_nav_wp`), and [`ArduCopter/mode_auto.cpp:2268-2295`](../../ArduCopter/mode_auto.cpp#L2268-L2295) (`verify_nav_wp`). Recorded here so a future planner does not re-litigate the verb.

- **Source**: review F3.
  - **Severity**: Major (in iter1 context).
  - **Finding**: Capstone was 1.25 h alone; the rubric requires ≥ 2 h on courses ≥ 3 days.
  - **Action this iteration**: **Moot under iter2 compression** — [time-budget.md](../criteria/time-budget.md) line 11 only triggers the 2-h capstone floor for courses ≥ 3 days. An 8 h / 2-day course has no capstone obligation. iter2 does not declare a "capstone" module; the EKF-failsafe-injection lab is retained as the strongest hands-on payload but is named "Closing lab" not "Capstone."

- **Source**: review F4.
  - **Severity**: Minor.
  - **Finding**: Prerequisite-chain awareness was named in prose but not enumerated as a topic-by-topic assumption map.
  - **Action this iteration**: **Addressed.** A bulleted assumption map appears below in **Decisions → Prerequisite-chain assumption map**. Each topic the GNC quadplane / plane Day 1 compresses on the assumption that students already know it is mapped to either an iter2 module that establishes it, or to an explicit "deliberately out of scope; the GNC course re-derives it from zero" note with one-sentence justification.

- **Source**: review F5.
  - **Severity**: Nit.
  - **Finding**: `AGENTS.md:5-8` is a 4-line range (rubric floor 5).
  - **Action this iteration**: Cite widened to [AGENTS.md:1-22](../../AGENTS.md#L1-L22) (header + safety-critical framing + table of contents — 22 lines, well within the 5-150 line rubric range).

- **Source**: review F6.
  - **Severity**: Nit.
  - **Finding**: `mode_loiter.cpp:80-104` ends mid-function (file is 200 lines).
  - **Action this iteration**: **Moot under iter2 compression** — `LOITER` is dropped from the mode tour (D-cut3 below). If reintroduced, the cite would be re-labelled as "ModeLoiter::run, opening only."

- **Source**: review F7.
  - **Severity**: Minor.
  - **Finding**: Day-3 hands-on share computed against an inflated denominator.
  - **Action this iteration**: **Moot** — Day 3 is gone in iter2.

- **Source**: review F8.
  - **Severity**: Nit.
  - **Finding**: [libraries/AC_PID/AC_PID.cpp:13-73](../../libraries/AC_PID/AC_PID.cpp#L13-L73) was described as covering the P/I/D/FF/IMAX/FLTT/FLTE/FLTD/SMAX/PDMX block but ends at the PDMX `AP_GROUPINFO` macro line — the PDMX `@Param` *comment* block starts at line 69.
  - **Action this iteration**: **Moot** — PID-as-black-box is significantly compressed in iter2 (see Module 2.2 below); the PID parameter table is no longer cited. The PID body cite at [libraries/AC_PID/AC_PID.cpp:196-272](../../libraries/AC_PID/AC_PID.cpp#L196-L272) survives at *survey* depth only.

- **Source**: review F9.
  - **Severity**: Minor.
  - **Finding**: Per-day buffer was 15 min; rubric requires ≥ 30 min.
  - **Action this iteration**: **Addressed.** Buffer is declared **up front** at **30 min per day** (= 1 h total course buffer), and is subtracted from the per-day module budget before listing modules:
    - Day 1: 4.0 h total = 3.5 h modules + 0.5 h buffer.
    - Day 2: 4.0 h total = 3.5 h modules + 0.5 h buffer.
    - Course: 8.0 h total = 7.0 h modules + 1.0 h buffer.

## Decisions

The four scoping decisions (length, lab share, real-flight, programming depth) are locked by the user prompt and are not re-litigated here. The remaining design decisions for iter2 follow.

### Locked design choices

- **D1. Length: 8 h over 2 days (4 h/day).** Locked by user. (Reverses iter1's D1 of 16 h / 4 days.)
- **D2. Lab/lecture mix: ~50% hands-on.** Inherited from iter1 D2 — comfortably above the 25% rubric floor in [time-budget.md](../criteria/time-budget.md); appropriate for first-years with no CLI fluency.
- **D3. Pure SITL, no real flight, no instructor demo flight.** Inherited from iter1 D3.
- **D4. Read-only code citations; no student-written code.** Inherited from iter1 D4.
- **D5. Quadrotor X frame, default SITL location.** Inherited from iter1 D5. Single frame the entire course.
- **D6. MAVProxy CLI primary; no graphical GCS.** Inherited from iter1 D7.
- **D7. Depth markers: every module is *survey* or *applied*. No *internals*-marked modules.** Inherited from iter1 D8 — directly enforces the new **Forbidden** bullet in [audience-fit.md](../criteria/audience-fit.md) about novice-internals depth.
- **D8. No assessment beyond participation + closing-lab completion.** Inherited from iter1 D9. The 2-day course has no capstone obligation, so the closing lab's binary pass/fail (EKF failsafe fired? vehicle disarmed?) is sufficient.
- **D9. Buffer is declared up front at 30 min/day** and subtracted from the per-day module budget *before* listing modules. (Addresses F9. Reverses iter1's 15-min/day buffer.)
- **D10. Closing lab is iter1's L8 (EKF-failsafe injection) with reduced scaffolding.** Iter1's L7 (autotest warm-up) is folded into the same module's Step A: the same SITL launch + scripted MAVProxy run with no fault, then the same harness re-run with `SIM_GPS_DISABLE 1` injected mid-flight. This is a single module, ~75 min. Not framed as a "capstone" — the 2-day course is below the rubric's capstone-floor trigger. (Carries the strongest iter1 payload forward; rationale: the EKF-failsafe lab is the most concrete demonstration that "the autopilot is software making decisions" the course can produce in pure SITL.)

### D-cuts (rubric-grounded justification)

iter1 had four day-themes:

1. What is ArduPilot + first SITL flight
2. Flight modes + parameters
3. Sensors / scheduler / PID-as-black-box
4. Failsafes / missions / autotest closing lab

iter2 collapses these to two days. The cuts:

- **D-cut1 — Missions module (iter1 Module 4.2) is dropped.** Rationale: missions are a downstream-course-Day-1 *re-derive-from-zero* topic per the GNC quadplane course's existing structure (see assumption map below). At 8 h there is no margin to teach `MAV_CMD_*` taxonomy + `wp load` + `mode AUTO` honestly without it stealing time from the EKF-failsafe lab, which is the higher-leverage payload for an "introduction to ArduCopter" identity. Side benefit: drops F2 entirely. Justified under [audience-fit.md](../criteria/audience-fit.md) "Compression discipline" — topics the downstream course re-teaches at zero are not first-priority for an on-ramp.
- **D-cut2 — Standalone autotest-harness module (iter1 Module 4.3) is dropped.** Rationale: at 8 h, demonstrating the `Tools/autotest/autotest.py` invocation is a 5-minute "show, don't dwell" item folded into the closing lab's setup, not a 45-min lecture+lab module. Justified under [time-budget.md](../criteria/time-budget.md) "Per-module time" requirement — module budgets must be defensible; 45 min for a `python autotest.py …` invocation is not.
- **D-cut3 — Deep PID-tuning lab and rate-controller graph (iter1 Modules 3.3 partial + 3.4) are dropped.** Rationale: iter1 already marked PID as black-box / *survey*; the dataflash-graph lab (L5 in iter1) at *applied* depth is a comfortable 1 h on a 16 h course but is the wrong shape on an 8 h course where the closing-lab fingerprint is `EKF variance:` not `RATE.RDes`. The iter1 D8 (no internals depth) constraint is preserved. PID is named, the X-frame motor angles are still cited, but no rate-controller-error plotting lab is run. Justified under [audience-fit.md](../criteria/audience-fit.md) **Forbidden** "novice-internals depth" — pushing first-years from naming `_kp` to interpreting a closed-loop response plot drifts the audience upward.
- **D-cut4 — Wind / WPNAV_SPEED parameter-tweak lab (iter1 Module 2.4) is dropped as a standalone module.** Rationale: a 45-min standalone "tweak and observe" lab is the right shape on 16 h; on 8 h the same payload is delivered as a 10-min in-module activity (`SIM_WIND_SPD` is set once during the mode tour to show that LOITER holds against wind; we do not also do `WPNAV_SPEED` because there is no `AUTO`/mission lab — see D-cut1). Justified under [time-budget.md](../criteria/time-budget.md) — module count is bounded by total hours, and the lab's pedagogical novelty (parameter changes affect the simulation) is already established in Module 1.4.

Surviving day shape:

- **Day 1**: SITL setup + first flight + flight modes + the parameter system (compresses iter1's Days 1 and 2 into one day; drops `LOITER` as a third stop on the mode tour and drops the standalone wind/WPNAV lab).
- **Day 2**: Sensors / scheduler / PID-as-black-box + failsafes + the EKF-failsafe closing lab (compresses iter1's Days 3 and 4; drops the missions module and the standalone autotest-harness module; folds the autotest invocation into the closing lab).

### Prerequisite-chain assumption map (addresses F4)

The downstream courses' "compressed survival kit" sections — [`custom_gnc_course_plane.md`](../custom_gnc_course_plane.md) Day 1 and [`custom_gnc_course_quadplane.md`](../custom_gnc_course_quadplane.md) Day 1 — assume their incoming students already know the following operational topics. For each topic, this iter2 plan names the module that establishes it, OR records "deliberately out of scope; the downstream course re-derives it" with a one-sentence justification.

| # | Downstream-course assumption | Where iter2 establishes it | Notes |
|---|---|---|---|
| 1 | The autopilot is one binary that runs on flight hardware and in SITL — same source code on both surfaces | Module 1.1 (What is an autopilot, what is ArduPilot, what is SITL) | Established at *survey* depth. |
| 2 | SITL is launched via `Tools/autotest/sim_vehicle.py -v <Vehicle> -f <frame>` and a MAVProxy console comes up | Module 1.2 (Set up your laptop and launch SITL) | Established at *applied* depth. The downstream course launches `-v ArduPlane -f quadplane`; the intro launches `-v ArduCopter -f quad`. The invocation pattern is identical. |
| 3 | MAVProxy idioms: `param show/set`, `mode <NAME>`, `arm throttle`, `rc <ch> <pwm>` | Modules 1.3 (first flight) and 1.5 (parameters) | Established at *applied* depth. |
| 4 | Flight modes are named (e.g. `STABILIZE`, `ALT_HOLD`, `RTL`); a mode is software running at high rate, not a hardware switch position | Module 1.4 (Flight modes from a pilot's view) | Established at *survey/applied* depth. The downstream course skips this; this intro re-derives it from zero. |
| 5 | Parameters are persistent runtime configuration, declared with `AP_GROUPINFO`-family macros, documented inline with `@Param` annotations | Module 1.5 (Parameters) | Established at *applied* depth, including a real `@Param` block read in source. |
| 6 | The autopilot is a fixed-rate scheduler running a list of tasks (FAST_TASK every loop, SCHED_TASK rate-limited) | Module 2.1 (Sensors + scheduler) | Established at *survey* depth. |
| 7 | Sensors (IMU/baro/mag/GPS) feed an EKF that produces the state estimate; the EKF is a black box at this stage | Module 2.1 (Sensors + scheduler) | Established at *survey* depth. The downstream course goes from zero to `errorScore()` and lane-switch internals — this intro deliberately stops at "the EKF exists and is fed by sensors." |
| 8 | The control path is mode `run()` → attitude controller → rate controller → PID → motor mixer → ESC | Module 2.2 (PID-as-black-box, briefly) | Established at *survey* depth. The mathematical detail (P/I/D/FF/IMAX, slew limit, target/error/derivative filters) is **deliberately out of scope** — the downstream course re-derives PID for engineers who already know it from another stack; this intro names the data path and stops. |
| 9 | The autopilot has automatic failsafes that fire when something goes wrong (RC loss, battery, GCS link, EKF variance) | Module 2.3 (Why does the autopilot ever decide for itself? Failsafes) | Established at *applied* depth, focused on the EKF failsafe because that is what the closing lab triggers. |
| 10 | Dataflash logs and `MAV_SEVERITY_*` GCS statustext are how you confirm what the autopilot did | Module 2.4 (Closing lab — observed in passing during the lab walkthrough) | Established at *applied* depth in the lab itself. The downstream course's MAVExplorer survey is cross-referenced but not taught. |
| 11 | Missions: ordered lists of `MAV_CMD_NAV_*` items, loaded with `wp load`, executed in `AUTO` | **Deliberately out of scope.** | The downstream GNC courses re-derive missions from zero in their own Day 1 (see iter1 review F2 for the correct execution-path cites). At 8 h, mission content does not survive the budget; the on-ramp leaves this gap and flags it explicitly. |
| 12 | The autotest framework is a Python harness that scripts SITL flights for regression | **Deliberately out of scope** beyond a one-line mention in the closing lab. | Folded into the closing lab's setup (D-cut2). The downstream GNC courses do not assume autotest fluency in their Day 1 — they introduce it on Day 5. |
| 13 | Build system: `./waf configure --board sitl && ./waf copter` is the SITL build | Module 1.2 (Set up your laptop) | Established at *applied* depth. |
| 14 | ArduPilot code conventions (`AP_HAL::millis()`, `is_zero()`, `GCS_SEND_TEXT()`, snake_case methods, `AP_`/`AC_`/`AR_` class prefixes) | **Deliberately out of scope.** | The downstream course reaches these in its Module 3 (Build System & Code Conventions). The intro does not write code; teaching code conventions to non-coders wastes the budget. The intro does *show* `AP_GROUPINFO` blocks in source so students recognise the shape when they see them in Day 1 of the downstream course. |
| 15 | `AP_<FEATURE>_ENABLED` compile-time flags exist | **Deliberately out of scope.** | Same rationale as #14. |

**Known gaps the on-ramp deliberately leaves**: items 11, 12, 14, 15 above. course-writer must include this list verbatim in the course preamble so a student arriving at the GNC quadplane Day 1 sees what they have not yet been taught.

## Deliverable

course-writer will produce one new file:

- [`course/intro_arducopter_aero_y1.md`](../intro_arducopter_aero_y1.md) (does not yet exist — to be created by course-writer).

Relationship to existing files:

- **Sibling, prerequisite-style.** Does not replace, supplement, or modify [`course/custom_gnc_course_plane.md`](../custom_gnc_course_plane.md) or [`course/custom_gnc_course_quadplane.md`](../custom_gnc_course_quadplane.md). The intro course's preamble points at those as the "next step."
- The two GNC courses' Day 1 "compressed survival kit" sections are *not* re-used here — those compress operational topics for engineers who already know controls. The intro course re-derives the same operational topics from zero where it can in 8 h, and explicitly flags the gaps (assumption-map items 11/12/14/15) where it cannot.
- The course file ends with the line `Generated from course/plans/plan-intro-arducopter-aero-y1-iter2.md` per [scope-discipline.md](../criteria/scope-discipline.md).

## Course Structure

| Day | Theme | Module-hours | Buffer | Total |
|-----|-------|--------------|--------|-------|
| 1   | Set up SITL, first flight, flight modes, parameters | 3.5 | 0.5 | 4.0 |
| 2   | Under the hood: sensors, scheduler, PID-as-black-box, failsafes, closing lab | 3.5 | 0.5 | 4.0 |
| | **Total** | **7.0** | **1.0** | **8.0** |

Per-day hands-on share is summarised in **Verification**. Buffer per day is 30 min (per F9 / [time-budget.md](../criteria/time-budget.md)) and is the *only* slack — per-module times within a day sum to 3.5 h exactly.

---

### Day 1 — Set up SITL, first flight, flight modes, parameters (4h)

**Goal**: by end of Day 1, every student has SITL running on their own laptop, can launch a quadcopter, arm it, take off in `STABILIZE`, hover, switch to `ALT_HOLD`, switch to `LAND`, and disarm — using MAVProxy commands from the terminal — and can change a parameter and observe the effect.

Per-day budget: 3.5 h modules + 0.5 h buffer = 4.0 h. Hands-on share target: ≥ 50% of 3.5 h = ~1.75 h.

#### Module 1.1 — What is an autopilot, what is ArduPilot, what is SITL? (30 min, lecture+demo, *survey*)

- **Objectives**:
  1. Define autopilot, ground control station (GCS), and ground/air segment in plain English.
  2. Place ArduPilot in the open-source autopilot landscape (vs proprietary, vs research code) at one slide of depth.
  3. Recognise that the *same* ArduPilot binary that flies real hardware also flies in SITL — the difference is only the HAL backend.
  4. Recognise that the codebase has safety-critical conventions (compile-time flags, embedded constraints) that we will see throughout, even though the labs are pure simulation.
- **Citations**:
  - [AGENTS.md:1-22](../../AGENTS.md#L1-L22) — header + safety-critical framing + table of contents (widened from iter1's `:5-8` per F5).
  - [CLAUDE.md:14-31](../../CLAUDE.md#L14-L31) — top-level architecture: vehicles + libraries + HAL.
  - [ArduCopter/Copter.h:181](../../ArduCopter/Copter.h#L181) — `class Copter : public AP_Vehicle {` (the file we will spend the whole course around).
- **Hands-on**: instructor live-demos `Tools/autotest/sim_vehicle.py -v ArduCopter --console --map` on the projector; students watch only. (~5 min within the 30-min module.)

#### Module 1.2 — Set up your laptop: install, build, and launch SITL (1 h, lab, *applied*)

- **Objectives**:
  1. Run the prerequisites installer on Ubuntu (or the macOS / Windows-WSL equivalent) without panicking on the long output.
  2. Clone ArduPilot with submodules and run `./waf configure --board sitl && ./waf copter`.
  3. Launch SITL: `Tools/autotest/sim_vehicle.py -v ArduCopter --console --map`.
  4. Recognise the three windows that appear (MAVProxy console, MAVProxy command, map) and what each is for.
- **Citations**:
  - [Tools/environment_install/install-prereqs-ubuntu.sh](../../Tools/environment_install/install-prereqs-ubuntu.sh) (script existence; the instructor runs it — no specific line walk).
  - [BUILD.md](../../BUILD.md) — referenced for students who hit unfamiliar errors. Do not duplicate its contents in the course.
  - [Tools/autotest/sim_vehicle.py:287](../../Tools/autotest/sim_vehicle.py#L287) — `'ArduCopter.elf'` lookup (single-line illustration of how the script finds the binary).
  - [Tools/autotest/sim_vehicle.py:1073-1085](../../Tools/autotest/sim_vehicle.py#L1073-L1085) — `--vehicle` and `--frame` argument parsing (so students see where `-v ArduCopter` actually plugs in).
- **Hands-on lab spec (handoff to lab-builder)**: students execute install + clone + build + launch on their own laptop, ending with `STATUSTEXT: APM:Copter ...` printed in the console and the GCS map showing a vehicle at the SITL default location. Pass criterion: a `HEARTBEAT` arrives at the GCS and the map renders the vehicle.

#### Module 1.3 — Your first flight: arm, take off, land, disarm (45 min, lab, *applied*)

- **Objectives**:
  1. Use MAVProxy commands `mode`, `arm throttle`, `rc 3 1700`, `mode LAND`.
  2. Read the textual telemetry: altitude, battery, mode.
  3. Recognise `STABILIZE` and `LAND` by behaviour, not yet by source.
- **Citations**:
  - [ArduCopter/mode.h:77-109](../../ArduCopter/mode.h#L77-L109) — `enum class Number` listing all flight-mode IDs. Students see that `STABILIZE = 0`, `ALT_HOLD = 2`, `LAND = 9`.
  - [ArduCopter/mode_stabilize.cpp:9-64](../../ArduCopter/mode_stabilize.cpp#L9-L64) — `ModeStabilize::run()` (read aloud at *survey* depth: the comment block says "stabilize_run - runs the main stabilize controller; should be called at 100hz or more"; do not unpack the spool-state machine).
- **Hands-on lab spec**: students execute the canonical "first flight" sequence in MAVProxy and confirm `DISARMED` at the end. Pass criterion: `Disarming motors` statustext within 60 s of `mode LAND`.

#### Module 1.4 — Flight modes from a pilot's view (45 min, lecture+demo, *survey*)

- **Objectives**:
  1. Sort copter modes into three buckets: *manual* (`STABILIZE`, `ACRO`), *stabilized-with-altitude* (`ALT_HOLD`), *autonomous* (`AUTO`, `GUIDED`, `RTL`, `LAND`).
  2. Explain a mode prerequisite in plain English: "`RTL` needs a position estimate; `STABILIZE` does not."
  3. Recognise that mode switching can be denied by the autopilot if prerequisites are missing.
- **Citations**:
  - [ArduCopter/mode.h:77-109](../../ArduCopter/mode.h#L77-L109) — `enum class Number` (re-cited from 1.3; on this module we read the names).
  - [ArduCopter/mode_stabilize.cpp:9-64](../../ArduCopter/mode_stabilize.cpp#L9-L64) — manual-throttle mode (re-cited from 1.3).
  - [ArduCopter/mode_althold.cpp:9-22](../../ArduCopter/mode_althold.cpp#L9-L22) — `ModeAltHold::init`: "set vertical speed and acceleration limits." Show the init/run pattern shared by every mode.
  - [ArduCopter/mode_althold.cpp:26-104](../../ArduCopter/mode_althold.cpp#L26-L104) — `ModeAltHold::run`. Walk *survey* depth: state machine names (`MotorStopped`, `Landed_Pre_Takeoff`, `Takeoff`, `Flying`); skip the algebra.
  - [ArduCopter/mode.cpp:313-396](../../ArduCopter/mode.cpp#L313-L396) — `Copter::set_mode`: how a mode switch is requested and how it can be refused. *Applied* depth on the `requires position` check at [ArduCopter/mode.cpp:394](../../ArduCopter/mode.cpp#L394) and the `need alt estimate` check at [ArduCopter/mode.cpp:404](../../ArduCopter/mode.cpp#L404); rest is *survey*.
- **Hands-on**: short in-module activity. In the running SITL students issue `mode STABILIZE`, `mode ALT_HOLD`, then `mode RTL` while `param set SIM_GPS_DISABLE 1` is set on the projector copy, and observe the rejection statustext. (~10 min.)

**Note**: `LOITER` is intentionally **not** included on the iter2 mode tour (D-cut3 + budget; iter1's [`mode_loiter.cpp:80-104`](../../ArduCopter/mode_loiter.cpp#L80-L104) cite is dropped, which moots F6).

#### Module 1.5 — Parameters: ArduPilot's configuration surface (30 min, lecture+demo, *applied*)

- **Objectives**:
  1. Define a parameter as a runtime-configurable value, persistent across reboots.
  2. Read the canonical parameter-doc format and recognise `@Param`, `@DisplayName`, `@Description`, `@Range`, `@Units`.
  3. Run `param show <name>`, `param set <name> <value>`.
  4. Find which file declares a parameter by searching for its name with `grep`.
- **Citations**:
  - [AGENTS.md:202-234](../../AGENTS.md#L202-L234) — parameter documentation conventions. Read this with the students.
  - [ArduCopter/Parameters.cpp:33-67](../../ArduCopter/Parameters.cpp#L33-L67) — first few `Copter::var_info[]` entries (`FORMAT_VERSION`, `PILOT_THR_FILT`, `PILOT_THR_BHV`, `GCS_PID_MASK`). Show the annotation block format in real code.
  - [ArduCopter/Parameters.cpp:149-191](../../ArduCopter/Parameters.cpp#L149-L191) — `FLTMODE1`-`FLTMODE6` and `FLTMODE_CH`. Explain how the RC switch position maps to a flight mode via these parameters.
- **Hands-on**: in the running SITL students run `param show SIM_WIND_SPD`, then `param set SIM_WIND_SPD 5`, and observe the simulated wind-affected hover wobble. (~5 min within the 30-min module.) This consolidates "parameters change behaviour" without a standalone wind/WPNAV lab (D-cut4).

#### Day 1 buffer / Q&A (30 min)

Per [time-budget.md](../criteria/time-budget.md). Used for environment-issue mop-up (apt mirror failures, WSL path issues — see [CLAUDE.md:103-107](../../CLAUDE.md#L103-L107)).

**Day 1 totals**: 0.5 + 1.0 + 0.75 + 0.75 + 0.5 = **3.5 h modules** + 0.5 h buffer = **4.0 h**. Hands-on share: ~0.05 h (1.1) + 1.0 h (1.2) + 0.75 h (1.3) + ~0.15 h (1.4) + ~0.1 h (1.5) = ~2.05 h hands-on / 3.5 h modules = **~59%**, well above the 25% rubric floor.

---

### Day 2 — Under the hood: sensors, scheduler, PID-as-black-box, failsafes, closing lab (4h)

**Goal**: by end of Day 2, students can read (not write) the rough call path from sensor reading → scheduler tick → mode `run()` → PID → motor output, can name what the EKF is for without solving any equations, and have run a SITL flight in which an injected GPS failure triggers an EKF-failsafe action they can identify in the logs.

Per-day budget: 3.5 h modules + 0.5 h buffer = 4.0 h. Hands-on share target: ≥ 50% of 3.5 h = ~1.75 h.

#### Module 2.1 — Sensors and the scheduler: the heartbeat of the autopilot (45 min, lecture+demo, *survey*)

- **Objectives**:
  1. Name the sensors a copter uses: IMU (accel + gyro), barometer, magnetometer, GPS. Define each in one sentence.
  2. Define "estimator" as "the thing that fuses noisy sensors into one trusted estimate of where the vehicle is and how it is moving."
  3. Recognise that the EKF (Extended Kalman Filter) is the estimator — and stop there. **No math.**
  4. Define "scheduler" as a fixed list of (function, rate, max_micros) tuples that the autopilot runs forever in a loop.
  5. Identify three landmark scheduler entries: IMU update, rate controller, EKF state estimator.
- **Citations** (all *survey*; we read symbol names, not function bodies):
  - `libraries/AP_InertialSensor/`, `libraries/AP_GPS/`, `libraries/AP_Baro/`, `libraries/AP_AHRS/` — directory existence only, not code-cites (not link-rendered; rubric is silent on directory references).
  - [ArduCopter/Copter.cpp:113-149](../../ArduCopter/Copter.cpp#L113-L149) — the `FAST_TASK` block at the top of `Copter::scheduler_tasks[]`. Walk only the named tasks: `run_rate_controller_main` ([ArduCopter/Copter.cpp:117](../../ArduCopter/Copter.cpp#L117)), `read_AHRS` ([ArduCopter/Copter.cpp:127](../../ArduCopter/Copter.cpp#L127), preceded by the comment `// run EKF state estimator (expensive)` on [ArduCopter/Copter.cpp:126](../../ArduCopter/Copter.cpp#L126)).
  - [ArduCopter/Copter.cpp:151-201](../../ArduCopter/Copter.cpp#L151-L201) — selected `SCHED_TASK` entries with rates, ending at `SCHED_TASK(ekf_check, 10, 75, 84)` on [ArduCopter/Copter.cpp:201](../../ArduCopter/Copter.cpp#L201). Talk about why different things run at different rates.
  - [ArduCopter/Copter.cpp:998](../../ArduCopter/Copter.cpp#L998) — `AP_HAL_MAIN_CALLBACKS(&copter);` — the entire ArduCopter binary's entry point in one line.
  - [libraries/AP_HAL/AP_HAL_Main.h:35-41](../../libraries/AP_HAL/AP_HAL_Main.h#L35-L41) — the macro `AP_HAL_MAIN_CALLBACKS` expands to. *Survey* depth: "main() is generated; it calls hal.run; the scheduler does the rest."
  - [libraries/AP_Vehicle/AP_Vehicle.cpp:558-566](../../libraries/AP_Vehicle/AP_Vehicle.cpp#L558-L566) — `AP_Vehicle::loop()` calling `scheduler.loop()`. Show that the scheduler is the only thing the main loop does.
- **Hands-on**: short in-module activity. Students grep for `SCHED_TASK` in `ArduCopter/Copter.cpp` and count the entries. Run `param show SCHED_LOOP_RATE` in the running SITL and observe it is 400 Hz. (~5 min within the 45-min module.)

#### Module 2.2 — From stick input to motor output: the data path (45 min, lecture+demo, *survey* with one *applied* cite)

- **Objectives**:
  1. Sketch the call path: pilot stick → mode `run()` → attitude controller → rate controller → PID → motor mixer → ESC output. Keep this sentence verbatim — it is the single most-load-bearing handoff to the GNC course (assumption-map item 8).
  2. Recognise that PID is "compute an error, multiply by P, add the integral, add the derivative, output." Do not derive — name the term and stop.
  3. Read the X-frame motor angle table and understand why a quad X has motors at +45° / -135° / -45° / +135°.
- **Citations**:
  - [ArduCopter/Copter.cpp:117](../../ArduCopter/Copter.cpp#L117) and [ArduCopter/Attitude.cpp:10-24](../../ArduCopter/Attitude.cpp#L10-L24) — `run_rate_controller_main` calling `attitude_control->rate_controller_run()`.
  - [libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:457-485](../../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L457-L485) — `rate_controller_run_dt`. *Applied* depth (the only *applied* cite in this module): each axis calls `update_all(...)` on a PID at [libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:473](../../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L473) (roll), [libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:476](../../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L476) (pitch), [libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:479](../../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L479) (yaw). Name the inputs (target angular velocity, gyro reading, dt) without unpacking the PID math.
  - [libraries/AC_PID/AC_PID.cpp:196-272](../../libraries/AC_PID/AC_PID.cpp#L196-L272) — `AC_PID::update_all`. *Survey* depth in iter2 (compressed from iter1's *applied*): identify that "P_out" is computed first and stop. The filtering and integrator are named, not unpacked. (PID parameter table is not cited in iter2; F8 moot.)
  - [libraries/AP_Motors/AP_MotorsMatrix.cpp:213-244](../../libraries/AP_Motors/AP_MotorsMatrix.cpp#L213-L244) — `output_armed_stabilizing` opening. *Survey* depth: "the mixer takes 4 numbers and decides how hard each motor pushes."
  - [libraries/AP_Motors/AP_MotorsMatrix.cpp:592-602](../../libraries/AP_Motors/AP_MotorsMatrix.cpp#L592-L602) — `MOTOR_FRAME_TYPE_X` motor angles. *Applied* depth retained from iter1.
- **Hands-on**: none in this module (the closing lab is the day's main hands-on payload).

#### Module 2.3 — Why does the autopilot ever decide for itself? Failsafes (45 min, lecture+demo, *applied*)

- **Objectives**:
  1. Define "failsafe" as an automatic action the autopilot takes when something goes wrong.
  2. Name four common failsafes a first-year should recognise: RC loss, battery, GCS link loss, **EKF variance**.
  3. Read the EKF-failsafe code path at *applied* depth, in preparation for the closing lab.
- **Citations**:
  - [ArduCopter/ekf_check.cpp:30-90](../../ArduCopter/ekf_check.cpp#L30-L90) — `Copter::ekf_check`: the 10 Hz monitor that detects EKF problems and triggers a failsafe after `EKF_CHECK_ITERATIONS_MAX` consecutive bad samples. *Applied* depth: name the variables (`ekf_check_state.fail_count`, `ekf_check_state.bad_variance`), the threshold parameter `g.fs_ekf_thresh`, the `LOGGER_WRITE_ERROR(LogErrorSubsystem::EKFCHECK, LogErrorCode::EKFCHECK_BAD_VARIANCE)` at [ArduCopter/ekf_check.cpp:83](../../ArduCopter/ekf_check.cpp#L83), the `gcs().send_text(MAV_SEVERITY_CRITICAL,"EKF variance: …")` at [ArduCopter/ekf_check.cpp:86](../../ArduCopter/ekf_check.cpp#L86), and the action `failsafe_ekf_event()` at [ArduCopter/ekf_check.cpp:89](../../ArduCopter/ekf_check.cpp#L89). Do not derive what the EKF variance actually means — that is the GNC course's job.
  - [ArduCopter/Copter.cpp:201](../../ArduCopter/Copter.cpp#L201) — `SCHED_TASK(ekf_check, 10, 75, 84)` — connect to Module 2.1's scheduler discussion.
  - [ArduCopter/AP_Arming_Copter.cpp:8-20](../../ArduCopter/AP_Arming_Copter.cpp#L8-L20) — `pre_arm_checks` entry plus `run_pre_arm_checks` opening "exit immediately if already armed." *Survey* depth: the autopilot refuses to arm unless every prerequisite is met.
- **Hands-on**: short in-module activity. Instructor demos `param set SIM_GPS_DISABLE 1` mid-flight on the projector; students watch `EKF variance` warning and the vehicle's mode change. Students do not run this themselves yet — they will in 2.4. (~5 min within the 45-min module.)

#### Module 2.4 — Closing lab: scripted flight with a forced EKF failsafe (1.25 h, lab, *applied*)

- **Objectives**:
  1. Run a full scripted SITL flight: take off, hover, RTL, disarm — with **no fault**.
  2. Run the same scripted flight with `SIM_GPS_DISABLE 1` injected mid-flight; observe the EKF failsafe fire; observe the vehicle still recover (LAND or RTL depending on `FS_EKF_ACTION` default).
  3. Inspect the dataflash log afterward to identify the moment of failsafe by both the GCS statustext and the dataflash `ERR` row.
- **Citations** (re-cited from Module 2.3 for the lab walk-through):
  - [ArduCopter/ekf_check.cpp:79-89](../../ArduCopter/ekf_check.cpp#L79-L89) — the source-of-truth fingerprint block for the lab's pass criterion.
- **Hands-on lab spec (handoff to lab-builder)**:
  - Vehicle: `ArduCopter`, frame: `quad` (X), at default SITL location.
  - **Step A (clean run, ~25 min including launch and walkthrough)**: scripted MAVProxy run — arm, take off in `GUIDED` to 30 m, hover 30 s, `mode RTL`, disarm. Pass criterion: vehicle disarmed within 180 s of arming, no `MAV_SEVERITY_CRITICAL` statustext during the run.
  - **Step B (failsafe, ~50 min including post-flight log inspection)**: same launch and same arm-takeoff-hover prefix; at t = 60 s after arming, `param set SIM_GPS_DISABLE 1`. Pass criterion: a `EKF variance:` `MAV_SEVERITY_CRITICAL` statustext appears within 30 s of the injection; the vehicle changes mode (to `LAND` or `RTL` depending on `FS_EKF_ACTION` default — the lab doc records which it is at the iteration's commit); the vehicle ends disarmed within 240 s of arming. Each student records the tail-of-log line stating the final mode and the disarm reason, and confirms a dataflash `ERR` row with `Subsys=EKFCHECK` and `ECode=BAD_VARIANCE`.

(Iter1's L7 "autotest warm-up" is folded into Step A as a single MAVProxy script; the standalone autotest-harness module is dropped per D-cut2.)

#### Day 2 buffer / Q&A (30 min)

**Day 2 totals**: 0.75 + 0.75 + 0.75 + 1.25 = **3.5 h modules** + 0.5 h buffer = **4.0 h**. Hands-on share: ~0.1 h (2.1) + 0 h (2.2) + ~0.1 h (2.3) + 1.25 h (2.4) = ~1.45 h hands-on / 3.5 h modules = **~41%**, comfortably above the 25% rubric floor. (Day 2 is concept-heavier than Day 1 by design: sensors, scheduler, and the data path are read-the-source modules.)

---

## Critical Files Cited

Master list of every `file:line` anchor referenced in the plan, deduplicated. Every cite below was `grep -n`-verified against the pinned tree (branch `GNC-0.1`, head `a6fc842e04`, 2026-04-26) — see **Verification**.

- [AGENTS.md:1-22](../../AGENTS.md#L1-L22) (header + safety-critical framing + ToC; iter2 widening per F5)
- [AGENTS.md:202-234](../../AGENTS.md#L202-L234) (Parameter Documentation section)
- [CLAUDE.md:14-31](../../CLAUDE.md#L14-L31) (Big-picture architecture)
- [CLAUDE.md:103-107](../../CLAUDE.md#L103-L107) (apt mirror guidance — referenced in Day 1 buffer note)
- [BUILD.md](../../BUILD.md) (file existence; no specific line)
- [Tools/environment_install/install-prereqs-ubuntu.sh](../../Tools/environment_install/install-prereqs-ubuntu.sh) (file existence)
- [Tools/autotest/sim_vehicle.py:287](../../Tools/autotest/sim_vehicle.py#L287)
- [Tools/autotest/sim_vehicle.py:1073-1085](../../Tools/autotest/sim_vehicle.py#L1073-L1085)
- [ArduCopter/Copter.h:181](../../ArduCopter/Copter.h#L181)
- [ArduCopter/Copter.cpp:113-149](../../ArduCopter/Copter.cpp#L113-L149)
- [ArduCopter/Copter.cpp:117](../../ArduCopter/Copter.cpp#L117)
- [ArduCopter/Copter.cpp:126](../../ArduCopter/Copter.cpp#L126)
- [ArduCopter/Copter.cpp:127](../../ArduCopter/Copter.cpp#L127)
- [ArduCopter/Copter.cpp:151-201](../../ArduCopter/Copter.cpp#L151-L201)
- [ArduCopter/Copter.cpp:201](../../ArduCopter/Copter.cpp#L201)
- [ArduCopter/Copter.cpp:998](../../ArduCopter/Copter.cpp#L998)
- [ArduCopter/Attitude.cpp:10-24](../../ArduCopter/Attitude.cpp#L10-L24)
- [ArduCopter/mode.h:77-109](../../ArduCopter/mode.h#L77-L109)
- [ArduCopter/mode.cpp:313-396](../../ArduCopter/mode.cpp#L313-L396)
- [ArduCopter/mode.cpp:394](../../ArduCopter/mode.cpp#L394)
- [ArduCopter/mode.cpp:404](../../ArduCopter/mode.cpp#L404)
- [ArduCopter/mode_stabilize.cpp:9-64](../../ArduCopter/mode_stabilize.cpp#L9-L64)
- [ArduCopter/mode_althold.cpp:9-22](../../ArduCopter/mode_althold.cpp#L9-L22)
- [ArduCopter/mode_althold.cpp:26-104](../../ArduCopter/mode_althold.cpp#L26-L104)
- [ArduCopter/Parameters.cpp:33-67](../../ArduCopter/Parameters.cpp#L33-L67)
- [ArduCopter/Parameters.cpp:149-191](../../ArduCopter/Parameters.cpp#L149-L191)
- [ArduCopter/AP_Arming_Copter.cpp:8-20](../../ArduCopter/AP_Arming_Copter.cpp#L8-L20)
- [ArduCopter/ekf_check.cpp:30-90](../../ArduCopter/ekf_check.cpp#L30-L90)
- [ArduCopter/ekf_check.cpp:79-89](../../ArduCopter/ekf_check.cpp#L79-L89)
- [ArduCopter/ekf_check.cpp:83](../../ArduCopter/ekf_check.cpp#L83)
- [ArduCopter/ekf_check.cpp:86](../../ArduCopter/ekf_check.cpp#L86)
- [ArduCopter/ekf_check.cpp:89](../../ArduCopter/ekf_check.cpp#L89)
- [libraries/AP_HAL/AP_HAL_Main.h:35-41](../../libraries/AP_HAL/AP_HAL_Main.h#L35-L41)
- [libraries/AP_Vehicle/AP_Vehicle.cpp:558-566](../../libraries/AP_Vehicle/AP_Vehicle.cpp#L558-L566)
- [libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:457-485](../../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L457-L485)
- [libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:473](../../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L473)
- [libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:476](../../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L476)
- [libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:479](../../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L479)
- [libraries/AC_PID/AC_PID.cpp:196-272](../../libraries/AC_PID/AC_PID.cpp#L196-L272)
- [libraries/AP_Motors/AP_MotorsMatrix.cpp:213-244](../../libraries/AP_Motors/AP_MotorsMatrix.cpp#L213-L244)
- [libraries/AP_Motors/AP_MotorsMatrix.cpp:592-602](../../libraries/AP_Motors/AP_MotorsMatrix.cpp#L592-L602)

Forward-only "the right anchor if anyone restores mission content" cites (recorded for the future planner per F2; **not** referenced in any iter2 module):

- [ArduCopter/mode_auto.cpp:698-713](../../ArduCopter/mode_auto.cpp#L698-L713) — `ModeAuto::start_command` dispatch.
- [ArduCopter/mode_auto.cpp:1575-1614](../../ArduCopter/mode_auto.cpp#L1575-L1614) — `ModeAuto::do_nav_wp`.
- [ArduCopter/mode_auto.cpp:2268-2295](../../ArduCopter/mode_auto.cpp#L2268-L2295) — `ModeAuto::verify_nav_wp`.

Cites cut from iter1 because their parent module is dropped in iter2 (recorded for traceability):

- [ArduCopter/Copter.h:587](../../ArduCopter/Copter.h#L587) (cut with iter1's scheduler-task-array exposition; iter2 cites the array definition in `Copter.cpp` directly).
- [ArduCopter/mode.cpp:497-508](../../ArduCopter/mode.cpp#L497-L508) (cut with iter1's `update_flight_mode` walk; iter2 stays at `set_mode` only).
- [ArduCopter/mode_loiter.cpp:80-104](../../ArduCopter/mode_loiter.cpp#L80-L104) (cut with `LOITER` from D-cut3; moots F6).
- [libraries/AC_PID/AC_PID.cpp:13-73](../../libraries/AC_PID/AC_PID.cpp#L13-L73) (cut with iter1's PID parameter-table walk; moots F8).
- [libraries/SITL/SIM_Multicopter.cpp:26-44](../../libraries/SITL/SIM_Multicopter.cpp#L26-L44) and [libraries/SITL/SIM_Multicopter.cpp:62-92](../../libraries/SITL/SIM_Multicopter.cpp#L62-L92) (cut with iter1's "anatomy + how SITL fakes the physics" module — compressed into Module 1.1's definition of SITL).
- [Tools/autotest/arducopter.py:58](../../Tools/autotest/arducopter.py#L58), [Tools/autotest/arducopter.py:149-173](../../Tools/autotest/arducopter.py#L149-L173), [Tools/autotest/arducopter.py:278-293](../../Tools/autotest/arducopter.py#L278-L293) (cut with the standalone autotest-harness module per D-cut2).
- [libraries/AP_Mission/AP_Mission.cpp:206-207](../../libraries/AP_Mission/AP_Mission.cpp#L206-L207), [libraries/AP_Mission/AP_Mission.cpp:900-905](../../libraries/AP_Mission/AP_Mission.cpp#L900-L905), [libraries/AP_Mission/AP_Mission.cpp:1085-1150](../../libraries/AP_Mission/AP_Mission.cpp#L1085-L1150) (cut with the missions module per D-cut1; moots F2).

## Criteria Proposed

iter1 proposed two new bullets for [audience-fit.md](../criteria/audience-fit.md). Both have since been adopted by the user (visible in the current `audience-fit.md`). No further criteria changes are needed for iter2.

[citation-rigor.md](../criteria/citation-rigor.md)'s new **Clickable rendering** bullet is also already in force; iter2 conforms by writing every cite as a `[path:line](relative/path#Lline)` markdown link from the plan file's directory (`course/plans/`), which is `../../<repo-top-level>/...`.

Net: **None — plan satisfies existing criteria in [course/criteria/](../criteria/).** No deltas proposed.

## Handoff

### To course-writer

- **Voice**: plain English. The audience does not have C++ vocabulary or controls vocabulary. Define every acronym at first use (PID, EKF, IMU, GCS, RTL, AHRS). Define them inline; do not link out.
- **Code-reading style**: every cite block in the course should follow the pattern *"open this file, read these lines, here is the one or two things to notice, now move on."* Do not paste large code blocks; cite by `path:line` (rendered as a clickable markdown link) and ask the student to open the editor.
- **Citation format**: every cite in the course must be a markdown link of the form `[path:line](relative/path#Lline)`. The course file lives at `course/intro_arducopter_aero_y1.md`, so the relative prefix to a top-level dir like `ArduCopter/` is `../`. (Differs from this plan, which lives one level deeper — the plan uses `../../`.)
- **What to expand verbatim from this plan**:
  - **The assumption-map table** (Decisions → Prerequisite-chain assumption map) — paste it into the course preamble verbatim, including the four "deliberately out of scope" items. This is the single load-bearing handoff to a student arriving at the GNC quadplane Day 1; cutting it would re-introduce F4.
  - **The sentence "stick → mode `run()` → attitude controller → rate controller → PID → motor mixer → ESC"** in Module 2.2. Keep verbatim.
  - **The Day 1 install/build/launch lab in 1.2** — every command, every expected output line, in the order students will see them.
  - **The flight-mode bucket taxonomy in 1.4** — keep the *manual / stabilized-with-altitude / autonomous* grouping; do not switch to the [`ArduCopter/mode.h`](../../ArduCopter/mode.h) enum order, which is historical. (Note: the iter1 4-bucket taxonomy was *manual / stabilized-with-altitude / position+altitude / autonomous*; iter2 collapses to 3 buckets because `LOITER` and `POSHOLD` are not on the mode tour.)
- **What to compress**:
  - Module 1.1's "ArduPilot landscape" — half a slide, not three. Students do not need governance or release-cadence detail.
  - The MAVProxy command reference — list only the commands the labs use. Do not enumerate every MAVProxy module.
  - Sensor lecture (2.1) — one sentence per sensor. The point is *they exist and they go through the EKF*, not how each one works.
- **What is forbidden by D6 / D7**:
  - Do not add a Mission-Planner-GUI walkthrough (D6 — MAVProxy CLI primary).
  - Do not promote any module to *internals* depth (D7 — directly enforced by the new **Forbidden** bullet on novice-internals depth in [audience-fit.md](../criteria/audience-fit.md)). If you discover a citation that requires unpacking, summarise it in prose and cite the line range without walking the body.
  - Do not introduce mission content (D-cut1). If a student asks how `AUTO` works, the answer is "the GNC course covers that — for now, accept that `RTL` is what you'll see in this course's only autonomous transition."
- **Citation drift report**: the course must end with the line `Generated from course/plans/plan-intro-arducopter-aero-y1-iter2.md`. If any cite drifts when course-writer reads it, the writer updates the cite **and** records the change in a "Citation drift report" section per [scope-discipline.md](../criteria/scope-discipline.md).

### To course-reviewer

- **Rubrics that apply**:
  - [audience-fit.md](../criteria/audience-fit.md) — full coverage. Highest-risk rubric for this course because the audience is the most distant from the existing course corpus's audience. Pay specific attention to the **Required → Prerequisite-chain awareness** bullet: the assumption-map table must be present in the course file and must enumerate items #1–#15 with each one mapped to a module or to an "out of scope" justification. (This addresses iter1's F4.)
  - [citation-rigor.md](../criteria/citation-rigor.md) — full coverage; every cite in **Critical Files Cited** must resolve, and every cite in the course must be a clickable markdown link with the correct `../<dir>` relative prefix. Bare `path:line` strings without a markdown link are a Nit.
  - [scope-discipline.md](../criteria/scope-discipline.md) — full coverage; the course's module set must match this plan's module set verbatim.
  - [time-budget.md](../criteria/time-budget.md) — full coverage; per-day buffer is 30 min; per-day modules sum to 3.5 h; the course is below the 3-day capstone-floor trigger and does not declare a capstone module.
- **Specific risks to audit**:
  1. **Audience drift upward.** A course-writer who knows controls theory may sneak in PID-tuning intuition or EKF-variance derivation. Every time a paragraph introduces math beyond high-school physics, flag it as a Major finding (per the new [audience-fit.md](../criteria/audience-fit.md) **Forbidden** novice-internals bullet).
  2. **Citation drift.** ArduPilot is on `master` and lines move. The reviewer must `grep -n` every cite. The plan was written against branch `GNC-0.1` head `a6fc842e04` on 2026-04-26.
  3. **Scope creep into Plane/Quadplane.** This course is Copter-only. Any mention of [`ArduPlane/`](../../ArduPlane/), `quadplane.h`, or fixed-wing modes is a finding — *except* in the assumption-map table, where the GNC quadplane / plane courses are deliberately named as the on-ramp's destination.
  4. **Mission content reintroduction.** D-cut1 drops missions entirely. If course-writer reintroduces mission content (e.g. a 4-waypoint square via `AUTO`), it is a scope-discipline finding *and* re-introduces F2 (the parsing-vs-execution paraphrase). Reject.
  5. **Capstone framing.** The course must **not** name any module a "capstone." The 2-day total is below the 3-day capstone-floor trigger in [time-budget.md](../criteria/time-budget.md). Module 2.4 is the "closing lab," not the capstone. (This explicitly closes out F3 from iter1.)
  6. **Buffer time.** Each day must include ≥ 30 min explicit buffer (per [time-budget.md](../criteria/time-budget.md) and F9). If course-writer compresses buffer to 15 min to free up module time, it is a finding.
  7. **Forbidden internals-depth.** Per D7 + the new [audience-fit.md](../criteria/audience-fit.md) **Forbidden** bullet, no module is *internals*. The reviewer should reject any module that walks function bodies in detail (more than 2-3 lines of explanation per cite block) — *except* the EKF-failsafe walk in 2.3, which is *applied* by design and is bounded to the named variables / threshold / log fingerprint.
  8. **Clickable-cite rendering.** Every `path:line` reference in the course file must be a markdown link. Reviewer applies the new **Clickable rendering** bullet in [citation-rigor.md](../criteria/citation-rigor.md) and reports any bare cite as a Nit.
  9. **Assumption-map table presence.** The course file's preamble must contain the assumption-map table verbatim from this plan's **Decisions → Prerequisite-chain assumption map** section. If absent or partial, this is a Major finding under [audience-fit.md](../criteria/audience-fit.md) **Required → Prerequisite-chain awareness**.

### To lab-builder

Two hands-on labs survive in iter2. SITL is the surface throughout. All labs use `-v ArduCopter -f quad` (default) at the SITL default location.

- **Lab L1 (Module 1.2): "First SITL launch."**
  - SITL invocation: `./waf configure --board sitl && ./waf copter` (one-time), then `Tools/autotest/sim_vehicle.py -v ArduCopter --console --map`.
  - Parameters: defaults.
  - Fault injection: none.
  - Success criterion: a `HEARTBEAT` arrives at the GCS and the map renders the vehicle.
  - Expected fingerprint: MAVProxy console prints `Detected vehicle ArduCopter` and `online system 1` within 30 s.
  - Source-of-truth: [Tools/autotest/sim_vehicle.py:287](../../Tools/autotest/sim_vehicle.py#L287) (binary lookup), [Tools/autotest/sim_vehicle.py:1073-1085](../../Tools/autotest/sim_vehicle.py#L1073-L1085) (option parsers).

- **Lab L2 (Module 1.3): "First flight (STAB → LAND)."**
  - SITL invocation: same as L1.
  - Parameters: defaults.
  - Fault injection: none.
  - MAVProxy steps: `mode STABILIZE; arm throttle; rc 3 1700; <wait altitude > 10 m>; mode LAND; <wait disarm>`.
  - Success criterion: vehicle is `DISARMED` within 90 s of `arm throttle`.
  - Expected fingerprint: statustext `LAND complete` and `Disarming motors`.

- **Lab L3 (Module 2.4): "Closing lab — clean run + EKF-failsafe injection."** Two-step lab, single SITL session.
  - SITL invocation: same as L1, plus a small Python or shell orchestrator that drives MAVProxy commands.
  - Parameters used in this lab: `SIM_GPS_DISABLE` (toggled in Step B); `FS_EKF_ACTION`, `FS_EKF_THRESH`, `EK3_*` left at defaults.
  - **Step A** — clean run:
    - Steps: `arm throttle; mode GUIDED; takeoff 30; <hover 30 s>; mode RTL; <wait disarm>`.
    - Fault injection: none.
    - Success criterion: `Disarming motors` statustext within 180 s of `arm throttle`; no `MAV_SEVERITY_CRITICAL` statustext during the run.
  - **Step B** — failsafe injection:
    - Steps: same as Step A through hover; at t = 60 s after `arm throttle`, issue `param set SIM_GPS_DISABLE 1`.
    - Fault injection: `SIM_GPS_DISABLE = 1` at t+60 s.
    - Success criteria (all required):
      1. `STATUSTEXT` with severity `CRITICAL` and text starting `EKF variance:` within 30 s of injection.
      2. Mode change to `LAND` or `RTL` within 30 s of injection.
      3. `Disarming motors` within 240 s of original `arm throttle`.
      4. Dataflash `ERR` row with `Subsys=EKFCHECK` and `ECode=BAD_VARIANCE` (read via `mavlogdump.py --types ERR`).
    - Expected log fingerprint: source-of-truth at [ArduCopter/ekf_check.cpp:79-89](../../ArduCopter/ekf_check.cpp#L79-L89) — specifically the `LOGGER_WRITE_ERROR(LogErrorSubsystem::EKFCHECK, LogErrorCode::EKFCHECK_BAD_VARIANCE)` at [ArduCopter/ekf_check.cpp:83](../../ArduCopter/ekf_check.cpp#L83), the `gcs().send_text(MAV_SEVERITY_CRITICAL, "EKF variance: …")` at [ArduCopter/ekf_check.cpp:86](../../ArduCopter/ekf_check.cpp#L86), and the action `failsafe_ekf_event()` at [ArduCopter/ekf_check.cpp:89](../../ArduCopter/ekf_check.cpp#L89).

(Iter1's L3, L4, L5, L6, L7 are dropped per D-cut1/2/3/4. L1 and L2 carry forward unchanged. L8 carries forward as L3 with the autotest-warmup folded into Step A as a MAVProxy script and a tighter time budget (Step B injection at t+60s, disarm-by t+240s, instead of iter1's t+120s / t+300s) to fit the 1.25 h module.)

### To lab-tester

For each lab, the exact invocation and the message / log signature that confirms the expected behavior:

- **L1**: `Tools/autotest/sim_vehicle.py -v ArduCopter --console --map -N`. Confirm: stdout contains `Detected vehicle ArduCopter`. **Verdict logic**: PASS if MAVProxy reports `online system 1` within 30 s; FAIL otherwise.
- **L2**: Same launch as L1. Replay MAVProxy script: `mode STABILIZE`, `arm throttle`, `rc 3 1700`, wait altitude > 10 m, `mode LAND`, wait disarmed. **Params**: defaults. **Verdict**: PASS if `Disarming motors` statustext seen within 90 s of `arm throttle`.
- **L3 (closing lab)**: Launch SITL via `Tools/autotest/sim_vehicle.py -v ArduCopter --console --map`. Run a Python orchestrator that:
  - **Step A**: arms via `arm throttle`, sets `mode GUIDED`, issues `takeoff 30`, holds 30 s, sets `mode RTL`, waits for `Disarming motors`. Records timestamps.
  - **Step B** (in same SITL session, fresh arm): repeats arm + takeoff + hover; at t = 60 s after `arm throttle`, issues `param set SIM_GPS_DISABLE 1`. Captures all `STATUSTEXT` and the dataflash log.
  - **Params used in this lab**: `SIM_GPS_DISABLE=1` (injected mid-run, Step B only); `FS_EKF_ACTION` and `FS_EKF_THRESH` at defaults; `EK3_*` at defaults.
  - **Verdict**: PASS if **all** of:
    1. Step A: no `MAV_SEVERITY_CRITICAL` statustext; `Disarming motors` within 180 s of arm.
    2. Step B: `STATUSTEXT` with severity `CRITICAL` and text starting `EKF variance:` within 30 s of injection.
    3. Step B: mode change to `LAND` or `RTL` within 30 s of injection.
    4. Step B: `Disarming motors` within 240 s of original arm.
    5. Step B: dataflash `ERR` row with `Subsys=EKFCHECK` and `ECode=BAD_VARIANCE` (via `mavlogdump.py --types ERR`).
  - **Source-of-truth fingerprint**: [ArduCopter/ekf_check.cpp:79-89](../../ArduCopter/ekf_check.cpp#L79-L89).

## Verification

- **Citation sanity**: every cite in **Critical Files Cited** was located via `grep -n` against the working tree at branch `GNC-0.1` (HEAD `a6fc842e04`) on 2026-04-26. The reviewer's iter1 audit confirmed all 47 cite ranges resolved at this same head; iter2 reuses the subset of those cites that survive the redesign and adds three new forward-only mission-execution cites in [`ArduCopter/mode_auto.cpp`](../../ArduCopter/mode_auto.cpp) (recorded but not used in any module).
  - Re-verified at iter2 planning time:
    - [ArduCopter/Copter.h:181](../../ArduCopter/Copter.h#L181) → `class Copter : public AP_Vehicle {` (line 181 in this tree).
    - [ArduCopter/Copter.cpp:113](../../ArduCopter/Copter.cpp#L113) → `const AP_Scheduler::Task Copter::scheduler_tasks[] = {`.
    - [ArduCopter/Copter.cpp:117](../../ArduCopter/Copter.cpp#L117) → `FAST_TASK(run_rate_controller_main),`.
    - [ArduCopter/Copter.cpp:127](../../ArduCopter/Copter.cpp#L127) → `FAST_TASK(read_AHRS),` preceded by the `// run EKF state estimator (expensive)` comment at line 126.
    - [ArduCopter/Copter.cpp:201](../../ArduCopter/Copter.cpp#L201) → `SCHED_TASK(ekf_check, 10, 75, 84),`.
    - [ArduCopter/Copter.cpp:998](../../ArduCopter/Copter.cpp#L998) → `AP_HAL_MAIN_CALLBACKS(&copter);`.
    - [ArduCopter/ekf_check.cpp:30](../../ArduCopter/ekf_check.cpp#L30) → `void Copter::ekf_check()`; [ArduCopter/ekf_check.cpp:83](../../ArduCopter/ekf_check.cpp#L83) → `LOGGER_WRITE_ERROR(LogErrorSubsystem::EKFCHECK, LogErrorCode::EKFCHECK_BAD_VARIANCE);`; [ArduCopter/ekf_check.cpp:86](../../ArduCopter/ekf_check.cpp#L86) → `gcs().send_text(MAV_SEVERITY_CRITICAL,"EKF variance: %s", …);`; [ArduCopter/ekf_check.cpp:89](../../ArduCopter/ekf_check.cpp#L89) → `failsafe_ekf_event();`.
    - [ArduCopter/mode.cpp:313](../../ArduCopter/mode.cpp#L313) → `bool Copter::set_mode(Mode::Number mode, ModeReason reason)`; [ArduCopter/mode.cpp:394](../../ArduCopter/mode.cpp#L394) → `mode_change_failed(new_flightmode, "requires position");`; [ArduCopter/mode.cpp:404](../../ArduCopter/mode.cpp#L404) → `mode_change_failed(new_flightmode, "need alt estimate");`.
    - [ArduCopter/AP_Arming_Copter.cpp:8](../../ArduCopter/AP_Arming_Copter.cpp#L8) → `bool AP_Arming_Copter::pre_arm_checks(bool display_failure)`.
    - [ArduCopter/Parameters.cpp:34](../../ArduCopter/Parameters.cpp#L34), [ArduCopter/Parameters.cpp:44](../../ArduCopter/Parameters.cpp#L44), [ArduCopter/Parameters.cpp:149](../../ArduCopter/Parameters.cpp#L149), [ArduCopter/Parameters.cpp:186](../../ArduCopter/Parameters.cpp#L186) → `@Param: FORMAT_VERSION` / `PILOT_THR_FILT` / `FLTMODE1` / `FLTMODE_CH` confirmed.
    - [libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:457](../../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L457) → `void AC_AttitudeControl_Multi::rate_controller_run_dt(...)`; `:473`/`:476`/`:479` → `update_all` calls on roll/pitch/yaw confirmed.
    - [libraries/AC_PID/AC_PID.cpp:196](../../libraries/AC_PID/AC_PID.cpp#L196) → `float AC_PID::update_all(float target, float measurement, float dt, …)`.
    - [libraries/AP_Motors/AP_MotorsMatrix.cpp:213](../../libraries/AP_Motors/AP_MotorsMatrix.cpp#L213) → `void AP_MotorsMatrix::output_armed_stabilizing()`; `:592` → `case MOTOR_FRAME_TYPE_X:` (within `setup_quad_matrix`).
    - [libraries/AP_HAL/AP_HAL_Main.h:35](../../libraries/AP_HAL/AP_HAL_Main.h#L35) → `#define AP_HAL_MAIN_CALLBACKS(CALLBACKS) extern "C" { \`.
    - [libraries/AP_Vehicle/AP_Vehicle.cpp:558](../../libraries/AP_Vehicle/AP_Vehicle.cpp#L558) → `void AP_Vehicle::loop()` (calls `scheduler.loop();` at [libraries/AP_Vehicle/AP_Vehicle.cpp:561](../../libraries/AP_Vehicle/AP_Vehicle.cpp#L561)).
    - [Tools/autotest/sim_vehicle.py:287](../../Tools/autotest/sim_vehicle.py#L287) → `'ArduCopter.elf',`.
    - [Tools/autotest/sim_vehicle.py:1073](../../Tools/autotest/sim_vehicle.py#L1073) → `parser.add_option("-v", "--vehicle", …)`.
  - Forward-only cites added in iter2 (verified for accurate description, not used in any iter2 module):
    - [ArduCopter/mode_auto.cpp:698](../../ArduCopter/mode_auto.cpp#L698) → `// start_command - this function will be called when the ap_mission lib wishes to start a new command` followed by `bool ModeAuto::start_command(const AP_Mission::Mission_Command& cmd)` at [ArduCopter/mode_auto.cpp:699](../../ArduCopter/mode_auto.cpp#L699), with the `case MAV_CMD_NAV_WAYPOINT` branch calling `do_nav_wp(cmd)` at [ArduCopter/mode_auto.cpp:713](../../ArduCopter/mode_auto.cpp#L713).
    - [ArduCopter/mode_auto.cpp:1575](../../ArduCopter/mode_auto.cpp#L1575) → `// do_nav_wp - initiate move to next waypoint` followed by `void ModeAuto::do_nav_wp(...)` at [ArduCopter/mode_auto.cpp:1576](../../ArduCopter/mode_auto.cpp#L1576).
    - [ArduCopter/mode_auto.cpp:2268](../../ArduCopter/mode_auto.cpp#L2268) → `// verify_nav_wp - check if we have reached the next way point` followed by `bool ModeAuto::verify_nav_wp(...)` at [ArduCopter/mode_auto.cpp:2269](../../ArduCopter/mode_auto.cpp#L2269).
  - Drift report: **no cite drifted** between the iter1-review pinned head and the iter2 planning head (same head, `a6fc842e04`). Iter1's F2/F5/F6/F8 were *description* defects, not resolution defects; iter2 addresses each by either widening, dropping, or relabelling the cite, not by changing line numbers.

- **Time-budget sum**: declared up-front at the top of **Course Structure**. Per-day totals: Day 1 = 4.0 h (3.5 modules + 0.5 buffer); Day 2 = 4.0 h (3.5 modules + 0.5 buffer). Course total = 8.0 h, exact match to the user-locked 8 h. Per-module sums per day:
  - Day 1: 0.5 + 1.0 + 0.75 + 0.75 + 0.5 = 3.5 h modules, +0.5 h buffer = 4.0 h. ✓
  - Day 2: 0.75 + 0.75 + 0.75 + 1.25 = 3.5 h modules, +0.5 h buffer = 4.0 h. ✓
  - The buffer is *not* inside the per-module sum (lesson from F1).

- **Hands-on share per day**: Day 1 ~59% (2.05 h / 3.5 h modules), Day 2 ~41% (1.45 h / 3.5 h modules). Both clear the 25% rubric floor with margin. Day 2 is intentionally lower because it carries the read-the-source content that the GNC course's audience already knows but this audience does not.

- **Capstone**: **none declared**. Course is 2 days; below the 3-day capstone-floor trigger in [time-budget.md](../criteria/time-budget.md). The EKF-failsafe lab (Module 2.4, 1.25 h) is the day's main hands-on payload but is named "Closing lab," not "Capstone." This is the explicit resolution of iter1's F3.

- **Lab reproducibility**: every SITL invocation in **Handoff → To lab-builder** uses syntax verified against [Tools/autotest/sim_vehicle.py:1073-1085](../../Tools/autotest/sim_vehicle.py#L1073-L1085) (the `-v ArduCopter -f quad` form is the default; `--console --map` are valid options at the same option-parser block; `-N` is a valid headless option). The closing-lab fingerprint at [ArduCopter/ekf_check.cpp:79-89](../../ArduCopter/ekf_check.cpp#L79-L89) was re-verified to contain the `LOGGER_WRITE_ERROR(LogErrorSubsystem::EKFCHECK, LogErrorCode::EKFCHECK_BAD_VARIANCE)` and `EKF variance:` `MAV_SEVERITY_CRITICAL` statustext that the lab-tester verdict logic reads.

- **No-overlap audit vs sibling courses**:
  - [`course/custom_gnc_course_plane.md`](../custom_gnc_course_plane.md) and [`course/custom_gnc_course_quadplane.md`](../custom_gnc_course_quadplane.md) are vehicle-Plane / QuadPlane and assume C/C++ proficiency, controls theory, and prior flight-code experience. Their Day 1 "compressed survival kit" sections explicitly skip the operational primer that this course is built around.
  - There is **no module overlap** in module-set terms.
  - Conceptual overlap (intentional, this is the on-ramp): "what is a flight mode" / "what is a parameter" / "what is the scheduler" / "what is the EKF (as a black box)" / "what is a failsafe" — all compressed in the GNC courses, all expanded here for absolute beginners.
  - The assumption-map table (Decisions → Prerequisite-chain assumption map) makes the overlap explicit and bounded.
  - No prose is imported from either sibling course.

- **Lessons coverage** (addresses the iter2 brief's hard requirement that every blocker / Major from the iter1 review be addressed or explicitly deferred):
  - F1 (Major): moot under iter2 compression. ✓ (Lesson carried: buffer is declared once and not inside the per-module sum.)
  - F2 (Major): moot — mission module dropped (D-cut1). Forward-only correct cites recorded. ✓
  - F3 (Major in iter1 framing): moot — 2-day course has no capstone obligation. ✓
  - F4 (Minor): addressed — assumption-map table added. ✓
  - F5 (Nit): addressed — cite widened to [AGENTS.md:1-22](../../AGENTS.md#L1-L22). ✓
  - F6 (Nit): moot — `LOITER` dropped. ✓
  - F7 (Minor): moot — Day 3 gone. ✓
  - F8 (Nit): moot — PID parameter table not cited. ✓
  - F9 (Minor): addressed — buffer declared at 30 min/day up front. ✓
  - **No iter1 finding is left un-addressed.**

Generated against [course/plans/plan-intro-arducopter-aero-y1-iter1.md](plan-intro-arducopter-aero-y1-iter1.md) at branch `GNC-0.1`, head `a6fc842e04`, 2026-04-26.
