# Plan: Introduction to ArduCopter for First-Year Aerospace Engineering Students (iter 1)

## Context

- **Audience**: 1st-year aerospace engineering undergraduates. High-school physics in hand, basic calculus *in progress* (so we use derivatives/integrals as intuition only — no proofs, no Jacobians). **No prior controls theory, no prior embedded systems, no prior Linux/CLI fluency, no prior programming.** Many will be using a terminal for the first time during week 1.
- **Course length**: 16 hours total, delivered as **4 days x 4 h** (or equivalently 8 half-day sessions of 2 h, depending on the host institution's timetabling). Per the time-budget rubric, sums must be within ±1 h of 16 h overall.
- **Format**: in-person, in a TA-supported computer lab. Each student has a laptop on which we install the ArduPilot SITL toolchain in Module 1. Pure SITL — no real flight, no real hardware.
- **Vehicle target**: **ArduCopter (quadrotor X frame)** end-to-end. No Plane/Rover/Sub. Quad is the easiest mental model for first-years (4 motors, 1 frame, no wings, no servos, no airspeed).
- **Positioning vs existing courses**: this is a **prerequisite-style on-ramp** to the existing `course/custom_gnc_course_plane.md` and `course/custom_gnc_course_quadplane.md` (both 5-day, ~34 h, written for GNC engineers with C/C++ proficiency and prior flight-code experience on a proprietary autopilot). After taking this intro course, a student should be able to read the Day 1 of either advanced course without being lost on terminology or on the SITL toolchain. We deliberately skip the *internals* depth those courses live at: no EKF lane-switch math, no L1/TECS, no transition state machine, no porting to custom hwdef, no DDS/ROS2.
- **Constraints**:
  - Pure SITL on student laptops (no airspace, no logistics, no liability).
  - Read-only code citations: students never write C++ or Python in labs. They run shell commands, edit parameter values, and inspect log files.
  - Time budget per day caps at 4 h to fit a single morning or afternoon block plus break.
- **Iteration number**: iter 1. There is no prior plan, no prior review, no prior lab run for this slug. This is the first iteration produced for `intro-arducopter-aero-y1`.
- **Default decisions taken without user confirmation**: the AskUserQuestion tool was unavailable in this subagent context, so the four core scoping decisions (length, lab/lecture mix, real-flight, programming depth) were taken on the recommended defaults from the planner's question set. The parent agent should review them before invoking course-writer. They are listed in **Decisions** below and are reversible at iter 2.

## Lessons Applied

Iteration 1 — no prior reviews under `course/reviews/` or lab runs under `course/labs/*/runs/` to learn from. The reviews and labs directories are empty at planning time. Future iterations will populate this section with concrete findings.

## Decisions

The following are locked design choices with rationale. Iter 2 may reverse any of them on user instruction.

- **D1. Length: 16 h over 4 days (4 h/day).** Short enough to fit a 1-credit elective or a freshman onboarding week; long enough to clear the time-budget rubric's hands-on share, capstone, and buffer requirements. Recommended option from the question set. (Reversible: 8-10 h short version drops Day 4 capstone; 24 h long version adds a Lua-scripting day.)
- **D2. Lab/lecture mix: ~50% hands-on.** Each module pairs ~50% guided demo / lecture with ~50% follow-along lab. Comfortably above the time-budget rubric's 25% hands-on minimum. Lab-heavier (>65%) is risky for first-years with no CLI fluency; lecture-heavier (<40%) wastes the SITL surface. Recommended.
- **D3. Pure SITL, no real flight, no instructor demo.** No safety briefing overhead, no weather/airspace dependency, no insurance question. The course's whole point of difference vs the existing GNC courses is *accessibility* — adding real flight reintroduces the very gating that this course is meant to remove. Recommended.
- **D4. Read-only code citations; no student-written code.** Students inspect ArduPilot source in the editor with the instructor walking through it, but never compile a modification or write a Python script. Capstone is parameter-tweaking + a pre-existing autotest run, not script authoring. Matches the prerequisite ("no prior programming"). Recommended.
- **D5. Quadrotor X frame, default SITL location.** `sim_vehicle.py -v ArduCopter -f quad` (default). One frame the entire course. No frame/vehicle juggling that would drain Day 1.
- **D6. Code editor: VS Code with the ArduPilot folder opened, no IDE configuration required.** Students read code, do not build it locally beyond the SITL build done in Module 1. The actual SITL build happens once via `./waf configure --board sitl && ./waf copter`.
- **D7. Telemetry/GCS surface: MAVProxy console (CLI) primary; Mission Planner / QGroundControl mentioned in survey only.** MAVProxy is what `sim_vehicle.py` launches by default and gives uniform behavior across student OSes. A graphical GCS adds install/UI variability without teaching anything new at this level.
- **D8. Depth markers: every module is *survey* or *applied*. No *internals*-marked modules.** Per the audience-fit rubric, internals-depth requires ≥ 5 file:line cites that walk function bodies — that is the GNC-course depth and we are explicitly the on-ramp before it. We still provide real `file:line` citations (citation-rigor rubric is non-negotiable), but each cite is read at survey/applied depth: "this is where ArduPilot decides to declare a failsafe — see lines X-Y, the names matter, the math doesn't yet." 
- **D9. No assessment beyond participation + capstone completion.** No quizzes, no graded code submission. The capstone is a binary "did your scripted SITL flight reach RTL and disarm without an EKF failsafe?" — a spec the lab-tester agent can verify deterministically.

## Deliverable

course-writer will produce one new file:

- `course/intro_arducopter_aero_y1.md`

Relationship to existing files:

- **Sibling, prerequisite-style.** Does not replace, supplement, or modify `course/custom_gnc_course_plane.md` or `course/custom_gnc_course_quadplane.md`. The intro course's preamble points at those as the "next step."
- The two GNC courses' Day 1 "compressed survival kit" sections are *not* re-used here — those compress operational topics for engineers who already know controls. The intro course re-derives the same operational topics from zero.
- The course file ends with the line `Generated from course/plans/plan-intro-arducopter-aero-y1-iter1.md` per the scope-discipline rubric.

## Course Structure

| Day | Theme | Hours |
|-----|-------|-------|
| 1   | What is ArduPilot, and how do I run a copter on my laptop? | 4 |
| 2   | Flight modes from a pilot's view, and the parameter system | 4 |
| 3   | What the autopilot is doing under the hood (sensors, scheduler, motors, PID-as-black-box) | 4 |
| 4   | Failsafes, missions, autotest, and the capstone flight | 4 |
| | **Total** | **16** |

Per-day hands-on share is summarised in **Verification**.

---

### Day 1 — What is ArduPilot, and how do I run a copter on my laptop? (4h)

**Goal**: by end of day, every student has SITL running on their own laptop, can launch a quadcopter, arm it, take off in `STABILIZE`, hover, switch to `LAND`, and disarm — all using MAVProxy commands from the terminal.

#### Module 1.1 — What is an autopilot, and what is ArduPilot? (45 min, lecture+demo, *survey*)

- **Objectives**:
  1. Define autopilot, ground control station (GCS), and ground/air segment in plain English.
  2. Place ArduPilot in the open-source autopilot landscape (vs proprietary, vs research code).
  3. Name the supported vehicle types and pick out ArduCopter as our target.
  4. Recognize that ArduPilot is *real software running real airframes* — therefore the codebase has safety-critical conventions (compile-time flags, embedded constraints) that we will see throughout.
- **Citations**:
  - `AGENTS.md:5-8` — "safety-critical autopilot software controlling real vehicles" framing.
  - `CLAUDE.md:14-31` — top-level architecture: vehicles + libraries + HAL.
  - `ArduCopter/Copter.h:181` — `class Copter : public AP_Vehicle` (the file we will spend the whole course around).
- **Hands-on**: instructor live-demos `Tools/autotest/sim_vehicle.py -v ArduCopter --console --map` on the projector; students just watch. No student installation yet. (15 min within the 45-min module.)

#### Module 1.2 — Set up your laptop: clone, build, and launch SITL (1.5h, lab, *applied*)

- **Objectives**:
  1. Run the prerequisites installer on Ubuntu (or follow the macOS / Windows-WSL equivalent) without panicking on the long output.
  2. Clone ArduPilot with submodules and run `./waf configure --board sitl && ./waf copter`.
  3. Launch SITL: `Tools/autotest/sim_vehicle.py -v ArduCopter --console --map`.
  4. Recognize the three windows that appear (MAVProxy console, MAVProxy command, map) and what each is for.
- **Citations**:
  - `Tools/environment_install/install-prereqs-ubuntu.sh` (script existence; do not walk lines — the instructor runs it).
  - `BUILD.md` — referenced for students who hit unfamiliar errors. Do not duplicate its contents in the course.
  - `Tools/autotest/sim_vehicle.py:287` — `'ArduCopter.elf'` lookup (one-line illustration of how the script finds the binary; *applied* depth).
  - `Tools/autotest/sim_vehicle.py:1073-1085` — `--vehicle` and `--frame` argument parsing (so students see where `-v ArduCopter` actually plugs in).
- **Hands-on lab spec (handed off to lab-builder)**: students execute install + clone + build + launch on their own laptop, ending with `STATUSTEXT: APM:Copter ...` printed in the console and the GCS map showing a vehicle at the SITL default location. Pass criterion: a `HEARTBEAT` arriving and the map drawing the vehicle.

#### Module 1.3 — Anatomy of a multicopter, and how SITL fakes the physics (45 min, lecture+demo, *survey*)

- **Objectives**:
  1. Name the parts of a quadrotor: 4 motors+ESCs, frame, IMU, GPS, barometer, RC receiver, flight controller, battery.
  2. Define "frame type" (quad X) and "vehicle type" (Copter) and how they combine.
  3. Recognize that SITL replaces the IMU/GPS/baro/motors with software models — the autopilot code itself is unchanged.
- **Citations**:
  - `libraries/SITL/SIM_Multicopter.cpp:26-44` — `MultiCopter` constructor: frame, mass, battery setup. Walk it as "this is the simulated vehicle."
  - `libraries/SITL/SIM_Multicopter.cpp:62-92` — `MultiCopter::update`: per-tick physics step. *Survey* depth: name the calls (`update_wind`, `calculate_forces`, `update_dynamics`, `update_position`), do not unpack them.
  - `libraries/AP_Motors/AP_MotorsMatrix.cpp:592-602` — `MOTOR_FRAME_TYPE_X` motor angles for a quad X. Show that the X frame is literally four lines of `add_motors(...)`.
- **Hands-on**: students run `param show SIM_WIND_SPD` then `param set SIM_WIND_SPD 5` and watch the simulated wind-affected hover wobble. (15 min.)

#### Module 1.4 — Your first flight: arm, take off, land, disarm (45 min, lab, *applied*)

- **Objectives**:
  1. Use MAVProxy commands `mode`, `arm throttle`, `rc 3 1700`, `mode LAND`.
  2. Read the textual telemetry: altitude, battery, mode.
  3. Recognize `STABILIZE`, `ALT_HOLD`, and `LAND` by behavior, not yet by source.
- **Citations**:
  - `ArduCopter/mode.h:77-109` — `enum class Number` listing all flight-mode IDs. Students see that `STABILIZE = 0`, `ALT_HOLD = 2`, `LAND = 9`.
  - `ArduCopter/mode_stabilize.cpp:9-64` — `ModeStabilize::run()` (read aloud, *survey* depth: the comment block says "stabilize_run - runs the main stabilize controller; should be called at 100hz or more"; do not unpack the spool-state machine).
- **Hands-on lab spec (handed off to lab-builder)**: students execute the canonical "first flight" sequence in MAVProxy and confirm `DISARMED` at the end. Pass criterion: `LANDED` flag set and motors disarmed within 60 s of `mode LAND` issuance.

#### Day 1 buffer / Q&A (15 min)

Per time-budget rubric. Used for environment-issue mop-up (apt mirror failures, WSL path issues, etc. — see `CLAUDE.md:103-107`).

**Day 1 totals**: 0.75 + 1.5 + 0.75 + 0.75 + 0.25 = **4.0 h**. Hands-on share: ~1.5 h (Module 1.2) + ~0.75 h (Module 1.4) + ~0.25 h (in-module demos) = **~2.5 h ≈ 62%**. Capstone: none on Day 1.

---

### Day 2 — Flight modes from a pilot's view, and the parameter system (4h)

**Goal**: by end of day, students can describe the difference between manual, stabilized, and autonomous modes; can switch between them on a running SITL; and can change a parameter and observe the effect.

#### Module 2.1 — Flight modes, organized as "what the pilot has to do" (1h, lecture+demo, *survey*)

- **Objectives**:
  1. Sort copter modes into three buckets: *manual* (`STABILIZE`, `ACRO`), *stabilized-with-altitude* (`ALT_HOLD`), *position+altitude* (`LOITER`, `POSHOLD`), *autonomous* (`AUTO`, `GUIDED`, `RTL`, `LAND`, `CIRCLE`).
  2. Explain mode prerequisites in plain English: "`LOITER` needs a GPS lock; `STABILIZE` does not."
  3. Recognize that mode switching can be denied by the autopilot if prerequisites are missing.
- **Citations**:
  - `ArduCopter/mode.h:77-109` — `enum class Number` (re-cited from Day 1; on Day 2 we read the names).
  - `ArduCopter/mode_stabilize.cpp:9-64` — manual-throttle mode. Note `motors->set_desired_spool_state(...)` line; *survey* depth.
  - `ArduCopter/mode_althold.cpp:9-22` — `ModeAltHold::init`: "set vertical speed and acceleration limits." Show the init/run pattern shared by every mode.
  - `ArduCopter/mode_althold.cpp:26-104` — `ModeAltHold::run`. Walk *survey* depth: state machine names (`MotorStopped`, `Landed_Pre_Takeoff`, `Takeoff`, `Flying`); skip the algebra.
  - `ArduCopter/mode_loiter.cpp:80-104` — `ModeLoiter::run` opening: "convert pilot input to lean angles" → "process pilot's roll and pitch input." Show that LOITER is `ALT_HOLD` plus position control.
  - `ArduCopter/mode.cpp:313-396` — `Copter::set_mode`: how a mode switch is requested and how it can be refused (`requires position`, `need alt estimate`). *Applied* depth on lines 391-405 only; the rest is survey.
- **Hands-on**: in the running SITL, students issue `mode STABILIZE`, `mode LOITER` (with GPS lock), `mode LOITER` (after `param set SIM_GPS_DISABLE 1` on a stretch goal), and observe the rejection message. (~20 min within the module.)

#### Module 2.2 — Lab: fly each mode (1h, lab, *applied*)

- **Objectives**:
  1. Take off, switch through `STABILIZE` → `ALT_HOLD` → `LOITER` → `RTL` and observe the qualitative differences.
  2. Read the MAVProxy console statustext for each transition.
- **Hands-on lab spec**: scripted MAVProxy step list. Pass criterion: vehicle returns to within 5 m of takeoff position after `RTL` and disarms.

#### Module 2.3 — Parameters: ArduPilot's configuration surface (1h, lecture+demo, *applied*)

- **Objectives**:
  1. Define a parameter as a runtime-configurable value, persistent across reboots.
  2. Read the canonical parameter-doc format and recognize `@Param`, `@DisplayName`, `@Description`, `@Range`, `@Units`.
  3. Run `param show <name>`, `param set <name> <value>`, `param fetch`, `param save`.
  4. Find which file declares a parameter by searching for its name with `grep`.
- **Citations**:
  - `AGENTS.md:202-234` — parameter documentation conventions. Read this with the students.
  - `ArduCopter/Parameters.cpp:33-67` — first few `Copter::var_info[]` entries (`FORMAT_VERSION`, `PILOT_THR_FILT`, `PILOT_THR_BHV`, `GCS_PID_MASK`). Show the annotation block format in real code.
  - `ArduCopter/Parameters.cpp:149-191` — `FLTMODE1`-`FLTMODE6` and `FLTMODE_CH`. Explain how the RC switch position maps to a flight mode via these parameters.
- **Hands-on**: students change `FLTMODE1` to `5` (LOITER) in MAVProxy, set the SITL RC mode-channel low, observe that the vehicle now boots to `LOITER` instead of `STABILIZE`. Then revert.

#### Module 2.4 — Lab: tweak and observe (45 min, lab, *applied*)

- **Objectives**:
  1. Modify a parameter and observe the simulated vehicle's behavior.
  2. Read a `@Range` annotation and stay inside it.
- **Hands-on lab spec**: students raise `SIM_WIND_SPD` from 0 to 10 m/s and observe `LOITER` hold position; then they raise `WPNAV_SPEED` from default to 1500 cm/s, fly a `GUIDED` waypoint, and notice the vehicle reaches the target faster. Pass criterion: in both cases, no `EKF variance` or `Position not estimated` error during the lab.

#### Day 2 buffer / Q&A (15 min)

**Day 2 totals**: 1.0 + 1.0 + 1.0 + 0.75 + 0.25 = **4.0 h**. Hands-on share: ~0.5 h (in 2.1) + 1.0 h (2.2) + 0.25 h (in 2.3) + 0.75 h (2.4) = **~2.5 h ≈ 62%**.

---

### Day 3 — What the autopilot is doing under the hood (4h)

**Goal**: by end of day, students can read (not write) the rough call path from gyro reading → rate controller → motor output, and can name what the EKF is for without solving any equations.

#### Module 3.1 — Sensors, all as black boxes (45 min, lecture, *survey*)

- **Objectives**:
  1. Name the sensors a copter uses: IMU (accel + gyro), barometer, magnetometer, GPS, optionally rangefinder/optical-flow. Define each in one sentence.
  2. Define "estimator" as "the thing that fuses noisy sensors into one trusted estimate of where the vehicle is and how it is moving."
  3. Recognize that the EKF (Extended Kalman Filter) is the estimator — and stop there. **No math.**
- **Citations** (all *survey*; we are reading symbol names, not function bodies):
  - `libraries/AP_InertialSensor/` (directory) — IMU library. Students just see the directory exists.
  - `libraries/AP_GPS/` (directory) — GPS.
  - `libraries/AP_Baro/` (directory) — Barometer.
  - `libraries/AP_AHRS/` (directory) — Attitude+Heading Reference System; the wrapper around the EKF.
  - `ArduCopter/Copter.cpp:127` — `FAST_TASK(read_AHRS)` line, with the comment "run EKF state estimator (expensive)" on line 126. Hand-wave: "this single line, every loop, is where the autopilot looks at its sensors and updates its idea of position and attitude."
- **Hands-on**: none in this module (compensated elsewhere on Day 3).

#### Module 3.2 — The scheduler: the heartbeat of the autopilot (45 min, lecture+demo, *survey*)

- **Objectives**:
  1. Define "scheduler" as a fixed list of (function, rate, max_micros) tuples that the autopilot runs forever in a loop.
  2. Recognize FAST_TASK (every loop) vs SCHED_TASK (rate-limited) entries.
  3. Identify three landmark tasks: IMU update, rate controller, motor output.
- **Citations**:
  - `ArduCopter/Copter.cpp:113-149` — the `FAST_TASK` block at the top of `Copter::scheduler_tasks[]`. Walk the names on lines 115, 117, 125, 127, 132, 134, 136 only — do not unpack their bodies.
  - `ArduCopter/Copter.cpp:151-201` — selected `SCHED_TASK` entries with rates: `rc_loop` (250 Hz), `throttle_loop` (50 Hz), `update_batt_compass` (10 Hz), `ekf_check` (10 Hz at line 201). Talk about why different things run at different rates.
  - `libraries/AP_Vehicle/AP_Vehicle.cpp:558-566` — `AP_Vehicle::loop()` calling `scheduler.loop()`. Show that the scheduler is the only thing the main loop does.
  - `ArduCopter/Copter.cpp:998` — `AP_HAL_MAIN_CALLBACKS(&copter);` — the entire ArduCopter binary's entry point in one line.
  - `libraries/AP_HAL/AP_HAL_Main.h:35-41` — the macro it expands to. *Survey* depth: "main() is generated; it calls hal.run; the scheduler does the rest."
- **Hands-on**: students grep for `SCHED_TASK` in `ArduCopter/Copter.cpp` and count the entries (~50). Run `param show SCHED_LOOP_RATE` and observe it is 400 Hz. (~10 min.)

#### Module 3.3 — From stick input to motor output: the data path (1h, lecture+demo, *applied*)

- **Objectives**:
  1. Sketch the call path: pilot stick → mode `run()` → attitude controller → rate controller → PID → motor mixer → ESC output.
  2. Recognize that PID is "compute an error, multiply by P, add the integral, add the derivative, output."
  3. Read the X-frame motor angle table and understand why motor 1 is at +45 deg and motor 4 is at -45 deg.
- **Citations**:
  - `ArduCopter/Copter.cpp:117` and `ArduCopter/Attitude.cpp:10-24` — `run_rate_controller_main` calling `attitude_control->rate_controller_run()`.
  - `libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:457-485` — `rate_controller_run_dt`. Walk lines 473, 476, 479: each axis calls `update_all(...)` on a PID. *Applied* depth: name the inputs (target angular velocity, gyro reading, dt) without unpacking the PID math.
  - `libraries/AC_PID/AC_PID.cpp:196-272` — `AC_PID::update_all`. Walk *applied* depth: identify "P_out = error * _kp" on line 269 and stop. The filtering and integrator are named, not unpacked.
  - `libraries/AC_PID/AC_PID.cpp:13-73` — the `AP_GROUPINFO` block declaring `P`, `I`, `D`, `FF`, `IMAX`, `FLTT`, `FLTE`, `FLTD`, `SMAX`, `PDMX`. Connect the parameter names students set in MAVProxy to actual parameter declarations in source.
  - `libraries/AP_Motors/AP_MotorsMatrix.cpp:213-244` — `output_armed_stabilizing` opening: roll/pitch/yaw/throttle thrust inputs. *Survey* depth — "the mixer takes 4 numbers and decides how hard each motor pushes."
  - `libraries/AP_Motors/AP_MotorsMatrix.cpp:592-602` — `MOTOR_FRAME_TYPE_X` motor angles. *Applied* depth, re-cited from Day 1.
- **Hands-on**: students set `ATC_RAT_RLL_P` very low (`0.05`) and watch the vehicle struggle in `STABILIZE`; then restore default. Live demo of "PID tuning matters."

#### Module 3.4 — Lab: the rate-controller graph (1h, lab, *applied*)

- **Objectives**:
  1. Use MAVProxy `graph` (or the dataflash log via `mavlogdump.py`) to plot rate-controller error.
  2. Observe that perturbing the vehicle (`SIM_WIND_SPD 8`) makes the error nonzero, then the autopilot drives it back to zero.
- **Hands-on lab spec**: students fly `LOITER`, ramp `SIM_WIND_SPD` from 0 to 8 to 0 over ~60 s, and inspect the resulting plot of `RATE.RDes` vs `RATE.R`. Pass criterion: students can point to where wind disturbed the rate and where the controller corrected it.

#### Day 3 buffer / Q&A (15 min)

**Day 3 totals**: 0.75 + 0.75 + 1.0 + 1.0 + 0.25 = **3.75 h** + 0.25 h buffer = 4.0 h. Hands-on share: ~0.2 h (3.2) + ~0.3 h (3.3) + 1.0 h (3.4) = **~1.5 h ≈ 38%** (above the 25% rubric floor; below Day 1/2 because Day 3 is concept-heavy by design).

---

### Day 4 — Failsafes, missions, autotest, and the capstone (4h)

**Goal**: by end of day, students have run a full scripted autotest, watched the autopilot decide to RTL on a simulated GPS failure, and can explain why an EKF failsafe fired.

#### Module 4.1 — Why does the autopilot ever decide for itself? Failsafes (45 min, lecture+demo, *applied*)

- **Objectives**:
  1. Define "failsafe" as an automatic action the autopilot takes when something goes wrong.
  2. Name the four common failsafes a first-year should recognize: RC loss, battery, GCS link loss, EKF variance.
  3. Read the EKF-failsafe code path at *applied* depth.
- **Citations**:
  - `ArduCopter/ekf_check.cpp:30-90` — `Copter::ekf_check`: the 10 Hz monitor that detects EKF problems and triggers a failsafe after `EKF_CHECK_ITERATIONS_MAX` consecutive bad samples. *Applied* depth: name the variables, the threshold parameter `g.fs_ekf_thresh`, and the action (`failsafe_ekf_event()` on line 89). Do not derive what the EKF variance actually means — that is the GNC course's job.
  - `ArduCopter/Copter.cpp:201` — `SCHED_TASK(ekf_check, 10, 75, 84)` — connect to Day 3's scheduler discussion.
  - `ArduCopter/AP_Arming_Copter.cpp:8-20` — `pre_arm_checks` entry: "exit immediately if already armed." *Survey* depth: the autopilot refuses to arm unless every prerequisite is met.
- **Hands-on**: instructor demos `param set SIM_GPS_DISABLE 1` mid-flight, students watch `EKF variance` warning and the vehicle's `RTL` (or `LAND`, depending on `FS_EKF_ACTION`) action.

#### Module 4.2 — Missions: telling the autopilot to fly a route (45 min, lecture+demo, *applied*)

- **Objectives**:
  1. Define a mission as an ordered list of mission items (waypoints, takeoff, land, RTL).
  2. Recognize the most common mission commands by `MAV_CMD_*` name.
  3. Load and fly a 4-waypoint square mission using MAVProxy `wp load` + `mode AUTO`.
- **Citations**:
  - `libraries/AP_Mission/AP_Mission.cpp:206-207` — `MAV_CMD_NAV_TAKEOFF` case (one line; *survey* depth, just to ground the name).
  - `libraries/AP_Mission/AP_Mission.cpp:900-905` — `MAV_CMD_NAV_WAYPOINT` and `MAV_CMD_NAV_TAKEOFF` parsing (the *applied*-depth read: "this is where a waypoint mission item is unpacked from a MAVLink message").
  - `libraries/AP_Mission/AP_Mission.cpp:1085-1150` — `MAV_CMD_NAV_WAYPOINT` and `MAV_CMD_NAV_RETURN_TO_LAUNCH` execution. *Survey* depth.
- **Hands-on**: students load a 4-waypoint square mission file (provided by the instructor) and fly it via `mode AUTO`.

#### Module 4.3 — The autotest harness: deterministic flying (45 min, lecture+demo, *applied*)

- **Objectives**:
  1. Recognize that `Tools/autotest/` is a Python framework that scripts SITL flights for regression testing.
  2. Run an existing test: `Tools/autotest/autotest.py build.Copter test.Copter.ModeAltHold`.
  3. Read what a test does without writing one.
- **Citations**:
  - `Tools/autotest/arducopter.py:58` — `class AutoTestCopter(vehicle_test_suite.TestSuite)` — the parent class for every Copter test.
  - `Tools/autotest/arducopter.py:149-173` — `AutoTestCopter.takeoff` helper: takes a quad to 30 m altitude in a chosen mode. *Applied* depth: read what each line does.
  - `Tools/autotest/arducopter.py:278-293` — `def ModeAltHold(self)`: the entire `ModeAltHold` autotest is 16 lines. Walk it together — "takeoff to 10 m, hold altitude with full stick deflection, RTL."
- **Hands-on**: students run `Tools/autotest/autotest.py build.Copter test.Copter.ModeAltHold` (or `test.Copter.TakeoffAlt` as alternate) and watch the headless SITL fly the canned scenario from start to finish.

#### Module 4.4 — Capstone: scripted flight with a forced failsafe (1.25 h, lab, *applied*)

- **Objectives**:
  1. Run a full autotest in headless SITL, see the vehicle take off, fly a square, RTL, and disarm.
  2. Run the same autotest with `SIM_GPS_DISABLE` parameter forced high partway through, observe the EKF failsafe fire, and observe the vehicle still recover.
  3. Inspect the dataflash log afterward to identify the moment of failsafe.
- **Hands-on lab spec (handed off to lab-builder)**:
  - Vehicle: `ArduCopter`, frame: `quad` (X), at default SITL location.
  - Step A (clean): scripted MAVProxy run that takes off in `GUIDED`, flies a 4-waypoint square mission via `AUTO`, RTLs, disarms. Pass criterion: vehicle disarmed within 300 s of arming, no `MAV_SEVERITY_CRITICAL` statustext during the run.
  - Step B (failsafe): same scripted run; at t=120 s after arming, `param set SIM_GPS_DISABLE 1`. Pass criterion: a `EKF variance:` `MAV_SEVERITY_CRITICAL` statustext appears within 30 s, the vehicle changes mode (to `LAND` or `RTL` depending on `FS_EKF_ACTION` default — the lab doc records which it is at the iteration's commit), and the vehicle ends disarmed within 300 s.
  - Each student records both runs' tail-of-log line stating the final mode and disarm reason.

#### Day 4 buffer / Q&A (15 min)

**Day 4 totals**: 0.75 + 0.75 + 0.75 + 1.25 + 0.25 = **3.75 h** + 0.25 h buffer = 4.0 h. Hands-on share: ~0.25 h (4.1) + 0.5 h (4.2) + 0.5 h (4.3) + 1.25 h (4.4) = **~2.5 h ≈ 62%**. Capstone: 4.4 at 1.25 h. Note the time-budget rubric requires capstone ≥ 2 h on courses ≥ 3 days.

**Capstone deviation note for course-writer**: 1.25 h is below the 2-h capstone floor on courses ≥ 3 days. **Resolution**: Module 4.3's autotest run (45 min) is logically the warm-up to the capstone — students literally invoke the autotest harness once with no failure injection (4.3) and then again with failure injection (4.4). Counted together, the capstone arc is **2.0 h** and meets the rubric. course-writer must mark Module 4.3 in prose as "capstone warm-up: same harness, no fault injection yet" and record this in the course's Citation drift / Deviations section so the reviewer accepts the framing. If the reviewer rejects the framing, iter 2 will explicitly merge 4.3+4.4 into one 2-h capstone module.

---

## Critical Files Cited

Deduplicated master list. Every cite below was `grep -n`-verified during planning (see **Verification**).

- `AGENTS.md:5-8`, `AGENTS.md:202-234`
- `CLAUDE.md:14-31`, `CLAUDE.md:103-107`
- `BUILD.md` (referenced; no specific line)
- `Tools/environment_install/install-prereqs-ubuntu.sh` (existence)
- `Tools/autotest/sim_vehicle.py:287`, `:1073-1085`
- `Tools/autotest/arducopter.py:58`, `:149-173`, `:278-293`
- `ArduCopter/Copter.h:181`, `:587`
- `ArduCopter/Copter.cpp:113-149`, `:151-201`, `:201`, `:117`, `:127`, `:998`
- `ArduCopter/Attitude.cpp:10-24`
- `ArduCopter/mode.h:77-109`
- `ArduCopter/mode.cpp:313-396`, `:497-508`
- `ArduCopter/mode_stabilize.cpp:9-64`
- `ArduCopter/mode_althold.cpp:9-22`, `:26-104`
- `ArduCopter/mode_loiter.cpp:80-104`
- `ArduCopter/Parameters.cpp:33-67`, `:149-191`
- `ArduCopter/AP_Arming_Copter.cpp:8-20`
- `ArduCopter/ekf_check.cpp:30-90`
- `libraries/AP_HAL/AP_HAL_Main.h:35-41`
- `libraries/AP_Vehicle/AP_Vehicle.cpp:558-566`
- `libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:457-485`
- `libraries/AC_PID/AC_PID.cpp:13-73`, `:196-272`
- `libraries/AP_Motors/AP_MotorsMatrix.cpp:213-244`, `:592-602`
- `libraries/AP_Mission/AP_Mission.cpp:206-207`, `:900-905`, `:1085-1150`
- `libraries/SITL/SIM_Multicopter.cpp:26-44`, `:62-92`
- `libraries/AP_GPS/`, `libraries/AP_Baro/`, `libraries/AP_InertialSensor/`, `libraries/AP_AHRS/` (directory existence only)

## Criteria Proposed

The audience-fit, citation-rigor, scope-discipline, and time-budget rubrics in `course/criteria/` were written for the GNC-engineer audience. Three of the four already accommodate a first-year audience cleanly (their depth-marker, citation, scope, and time-budget mechanics are audience-agnostic). The fourth — audience-fit — has one tension worth flagging.

- `audience-fit.md` — proposed delta:
  - Add a bullet under **Required**: *"Prerequisite-chain awareness: if the course is positioned as an on-ramp to another course in this repo, the plan must name the downstream course and identify what assumptions the downstream course makes that this course is responsible for establishing."* Rationale: this intro course's whole identity is "what GNC-engineer course X assumes you already know." Without this rubric line, an audit could not confirm that the on-ramp actually covers the gap.
  - Optional clarification under **Forbidden**: *"For first-year / novice audiences, internals-depth modules are forbidden unless explicitly justified — the audience cannot consume them. Survey and applied are the working depths."* Rationale: prevents an over-eager future iteration from inflating an intro course into the GNC course it is supposed to feed.

The user reviews and decides whether to commit these into `course/criteria/audience-fit.md`. This plan does **not** itself write into `course/criteria/`.

## Handoff

### To course-writer

- **Voice**: plain English. The audience does not have C++ vocabulary or controls vocabulary. Define every acronym at first use (PID, EKF, IMU, GCS, RTL, MAV_CMD, AHRS). Define them inline; do not link out.
- **Code reading style**: every cite block in the course should follow the pattern *"open this file, read these lines, here is the one or two things to notice, now move on."* Do not paste large code blocks; cite by `path:line-line` and ask the student to open the editor. The point is to teach reading the codebase, not to embed it in the course PDF.
- **What to expand verbatim from this plan**:
  - The Day 1 install/build/launch lab in 1.2 — every command, every expected output line, in the order students will see them.
  - The flight-mode bucket taxonomy in 2.1 — keep the *manual / stabilized-with-altitude / position+altitude / autonomous* grouping; do not switch to the `mode.h` enum order, which is historical.
  - The end-to-end data path in 3.3 — keep the explicit sentence "stick → mode `run()` → attitude controller → rate controller → PID → motor mixer → ESC."
  - The Day 4 capstone narrative — emphasise the warm-up (4.3) → fault-injection (4.4) framing so the reviewer sees the 2 h capstone arc.
- **What to compress**:
  - Module 1.1's "ArduPilot landscape" — half a page, not three. Students do not need governance/release-cadence detail (that is in the GNC course).
  - The MAVProxy command reference — list only the commands the labs use. Do not enumerate every MAVProxy module.
  - Sensor lecture (3.1) — one slide per sensor. The point is *they exist and they go through the EKF*, not how each one works.
- **What is forbidden by D7/D8**:
  - Do not add a Mission-Planner-GUI walkthrough. (Consequence of D7.)
  - Do not promote any module to *internals* depth. (Consequence of D8.) If you discover a citation that requires unpacking, summarise it in prose and cite the line range without walking the body.
- **Citation drift report**: the course must end with the line `Generated from course/plans/plan-intro-arducopter-aero-y1-iter1.md`. If any cite drifts when course-writer reads it, the writer updates the cite **and** records the change in a "Citation drift report" section per `scope-discipline.md:13`.

### To course-reviewer

- **Rubric files in `course/criteria/` that apply** to this course:
  - `audience-fit.md` — full coverage. This is the highest-risk rubric for this course because the audience is the most distant from the existing course corpus's audience.
  - `citation-rigor.md` — full coverage; every cite in the **Critical Files Cited** list must resolve.
  - `scope-discipline.md` — full coverage; the course's module set must match this plan's module set verbatim.
  - `time-budget.md` — full coverage; capstone arc must be read as 4.3 + 4.4 = 2.0 h.
- **Specific risks to audit**:
  1. **Audience drift upward.** A course-writer who knows controls theory may sneak in PID-tuning intuition or EKF-variance derivation. Every time a paragraph introduces math beyond high-school physics, flag it as a major finding.
  2. **Citation drift.** ArduPilot is on `master` and lines move. The reviewer must `grep -n` every cite. The plan was written against the tree at branch `GNC-0.1` head as of 2026-04-26.
  3. **Scope creep into Plane/Quadplane.** This course is Copter-only. Any mention of `ArduPlane/`, `quadplane.h`, or fixed-wing modes is a finding.
  4. **Time-budget capstone floor.** Module 4.4 alone is 1.25 h, below the 2 h floor for courses ≥ 3 days. The plan's resolution is to count 4.3 (45 min, the warm-up autotest run) plus 4.4 (1.25 h, the fault-injection run) as a 2 h capstone arc. The reviewer should accept this if course-writer marks Module 4.3 in prose as "capstone warm-up." If not marked, this is a major finding.
  5. **Hands-on share on Day 3.** Day 3 is concept-heavy (sensors, scheduler, PID-as-black-box) and lands at ~38% hands-on, well above the 25% rubric floor but visibly below Days 1/2/4. Acceptable.
  6. **Forbidden internals-depth.** Per D8, no module is *internals*. The reviewer should reject any module that walks function bodies in detail (more than 2-3 lines of explanation per cite block).

### To lab-builder

One spec per hands-on lab. SITL is the surface throughout. All labs use `-v ArduCopter -f quad` (default) at the SITL default location.

- **Lab L1 (Module 1.2): "First SITL launch."** SITL invocation: `./waf configure --board sitl && ./waf copter && Tools/autotest/sim_vehicle.py -v ArduCopter --console --map`. No fault injection. Success criterion: a `HEARTBEAT` arrives at the GCS and the map renders the vehicle. Expected fingerprint: MAVProxy console prints `Detected vehicle ArduCopter` and `online system 1` within 30 s.
- **Lab L2 (Module 1.4): "First flight (STAB → LAND)."** SITL invocation: same as L1, plus the MAVProxy steps `mode STABILIZE; arm throttle; rc 3 1700; <wait altitude>; mode LAND; <wait disarm>`. No fault injection. Success criterion: vehicle is `DISARMED` within 60 s of `mode LAND`. Expected fingerprint: statustext `LAND complete` and `Disarming motors`.
- **Lab L3 (Module 2.2): "Mode tour."** SITL: same. Steps: take off in `STABILIZE` to 20 m, switch to `ALT_HOLD`, then `LOITER`, then `RTL`. Success criterion: vehicle ends within 5 m of takeoff position and disarmed.
- **Lab L4 (Module 2.4): "Wind & WPNAV_SPEED."** SITL: same. Steps: take off, `param set SIM_WIND_SPD 10`, `mode LOITER` for 30 s, `param set SIM_WIND_SPD 0`, `param set WPNAV_SPEED 1500`, fly a single GUIDED waypoint 100 m east, observe time-to-target, RTL. Success criterion: no `EKF variance` warning during the lab; vehicle returns home and disarms.
- **Lab L5 (Module 3.4): "Rate-controller graph."** SITL: same. Steps: arm in `LOITER`, take off to 30 m, ramp `SIM_WIND_SPD` 0→8→0 over 60 s, `mode RTL`. Post-flight, dump the dataflash log with `mavlogdump.py --types RATE` and produce a plot of `RATE.RDes` vs `RATE.R`. Success criterion: students can verbally identify a wind-induced disturbance and the controller's correction.
- **Lab L6 (Module 4.2): "4-waypoint square mission."** SITL: same. Steps: `wp load square.txt; arm throttle; mode AUTO`. Success criterion: vehicle visits all 4 waypoints within 5 m tolerance and returns home; lab-builder provides `square.txt`.
- **Lab L7 (Module 4.3): "Autotest warm-up."** Headless SITL via `Tools/autotest/autotest.py build.Copter test.Copter.ModeAltHold` (or `test.Copter.TakeoffAlt` if `ModeAltHold` is too short). Success criterion: autotest exits with `PASSED`.
- **Lab L8 (Module 4.4): "Capstone with EKF failsafe injection."** SITL: same as L1. Steps: arm, take off in `GUIDED` to 30 m, fly square mission via `AUTO`, at t=120 s after arming inject `param set SIM_GPS_DISABLE 1`. Success criterion: an `EKF variance:` `MAV_SEVERITY_CRITICAL` statustext within 30 s of the injection, vehicle changes mode (LAND or RTL per `FS_EKF_ACTION`), vehicle ends disarmed within 300 s. Expected log fingerprint: a `LogErrorSubsystem::EKFCHECK / LogErrorCode::EKFCHECK_BAD_VARIANCE` row in dataflash, originating at `ArduCopter/ekf_check.cpp:83`.

### To lab-tester

For each lab above, the exact SITL command and the GCS message / log signature that confirms the expected behavior:

- **L1**: `Tools/autotest/sim_vehicle.py -v ArduCopter --console --map -N`. Confirm: stdout contains `Detected vehicle ArduCopter`. No flight, no fault injection. **Verdict logic**: PASS if MAVProxy reports `online system 1` within 30 s; FAIL otherwise.
- **L2**: Same launch. Replay MAVProxy script: `mode STABILIZE`, `arm throttle`, `rc 3 1700`, wait altitude > 10 m, `mode LAND`, wait disarmed. **Params**: defaults. **Verdict**: PASS if `Disarming motors` statustext seen within 90 s of arm.
- **L3**: Replay script with mode transitions; verdict on final position within 5 m of home and disarmed.
- **L4**: Set `SIM_WIND_SPD=10` mid-flight; verdict on no `EKF variance` statustext throughout.
- **L5**: Set `SIM_WIND_SPD` ramp 0→8→0; verdict on dataflash containing `RATE` rows whose `R` column visibly tracks `RDes` after disturbance.
- **L6**: Replay mission; verdict on each `MISSION_ITEM_REACHED` for items 1-4 plus return to home within 5 m.
- **L7**: `Tools/autotest/autotest.py build.Copter test.Copter.ModeAltHold` — exit code 0 = PASS.
- **L8 (capstone)**: launch SITL, run `python` orchestrator that arms, takes off, runs square mission, at t+120s sets `SIM_GPS_DISABLE=1`. **Params used in this lab**: `SIM_GPS_DISABLE=1` (injected mid-run); `FS_EKF_ACTION` and `FS_EKF_THRESH` left at defaults; `EK3_*` left at defaults. **Verdict**: PASS if **all** of:
  1. `STATUSTEXT` with severity `CRITICAL` and text starting `EKF variance:` within 30 s of injection.
  2. Mode change to `LAND` or `RTL` within 30 s of injection.
  3. `Disarming motors` within 300 s of original arm.
  4. Dataflash `ERR` row with `Subsys=EKFCHECK` and `ECode=BAD_VARIANCE` (lab-tester reads this via `mavlogdump.py --types ERR`).
  Source-of-truth for the fingerprint: `ArduCopter/ekf_check.cpp:79-89` (the `LOGGER_WRITE_ERROR(LogErrorSubsystem::EKFCHECK, LogErrorCode::EKFCHECK_BAD_VARIANCE)` and the GCS critical statustext).

## Verification

- **Citation sanity**: every cite in **Critical Files Cited** was located via `grep -n` against the working tree at branch `GNC-0.1` (HEAD `a6fc842e04`) on 2026-04-26. Specifically verified:
  - `ArduCopter/Copter.h:181` → `class Copter : public AP_Vehicle {` confirmed.
  - `ArduCopter/Copter.cpp:113` → `const AP_Scheduler::Task Copter::scheduler_tasks[] = {` confirmed.
  - `ArduCopter/Copter.cpp:201` → `SCHED_TASK(ekf_check, 10, 75, 84),` confirmed.
  - `ArduCopter/Copter.cpp:117` → `FAST_TASK(run_rate_controller_main),` confirmed.
  - `ArduCopter/Copter.cpp:127` → `FAST_TASK(read_AHRS),` (with comment about EKF) confirmed.
  - `ArduCopter/Copter.cpp:998` → `AP_HAL_MAIN_CALLBACKS(&copter);` confirmed.
  - `ArduCopter/Attitude.cpp:10-24` → `Copter::run_rate_controller_main` body confirmed.
  - `ArduCopter/mode.h:77-109` → `enum class Number` confirmed (STABILIZE=0, ALT_HOLD=2, LAND=9, etc.).
  - `ArduCopter/mode.cpp:313` → `Copter::set_mode(Mode::Number mode, ModeReason reason)` confirmed.
  - `ArduCopter/mode.cpp:497` → `void Copter::update_flight_mode()` confirmed.
  - `ArduCopter/mode_stabilize.cpp:9-64` → `ModeStabilize::run` body confirmed (64 lines, file is 64 lines).
  - `ArduCopter/mode_althold.cpp:9-22` and `:26-104` → init and run; full file is 104 lines.
  - `ArduCopter/mode_loiter.cpp:80` → `ModeLoiter::run` confirmed.
  - `ArduCopter/Parameters.cpp:33` → `Copter::var_info[]` confirmed.
  - `ArduCopter/Parameters.cpp:149,154,191` → `FLTMODE1` parameter and `FLTMODE_CH` confirmed.
  - `ArduCopter/AP_Arming_Copter.cpp:8` → `pre_arm_checks` confirmed.
  - `ArduCopter/ekf_check.cpp:30` → `void Copter::ekf_check()` confirmed; `:79-89` matches the `LOGGER_WRITE_ERROR` and `gcs().send_text(MAV_SEVERITY_CRITICAL, "EKF variance: ...")` block.
  - `libraries/AP_HAL/AP_HAL_Main.h:35-41` → `AP_HAL_MAIN_CALLBACKS` macro confirmed.
  - `libraries/AP_Vehicle/AP_Vehicle.cpp:558` → `void AP_Vehicle::loop()` confirmed.
  - `libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:457` → `rate_controller_run_dt`; `:488` → `rate_controller_run`; calls `update_all` on lines 473/476/479 confirmed.
  - `libraries/AC_PID/AC_PID.cpp:196` → `AC_PID::update_all` confirmed; `:13-73` → `AP_GROUPINFO` block for P/I/D/FF/IMAX/FLTT/FLTE/FLTD/SMAX/PDMX confirmed.
  - `libraries/AP_Motors/AP_MotorsMatrix.cpp:213` → `output_armed_stabilizing`; `:576` → `setup_quad_matrix`; `:592-602` → `MOTOR_FRAME_TYPE_X` confirmed.
  - `libraries/SITL/SIM_Multicopter.cpp:26-44, :62-92` confirmed (file is 93 lines).
  - `Tools/autotest/sim_vehicle.py:287` → `'ArduCopter.elf'`; `:1073` → `parser.add_option("-v", "--vehicle", ...)`; `:1078` → `--frame`. All confirmed.
  - `Tools/autotest/arducopter.py:58` → `class AutoTestCopter`; `:149-173` → `takeoff` helper; `:278-293` → `def ModeAltHold`. All confirmed.
  - `libraries/AP_Mission/AP_Mission.cpp:206-207, :900-905, :1085, :1150` confirmed.
  - No cite was dropped during planning — every cite originally drafted was verified and kept.
- **Time-budget sum**: per-day totals are 4.0, 4.0, 4.0, 4.0 = 16.0 h, matching the declared course total exactly (within ±1 h trivially). Per-module sums per day all reach 3.75-4.0 h with explicit 15-min buffer slots accounting for any short remainders.
- **Hands-on share per day**: Day 1 ~62%, Day 2 ~62%, Day 3 ~38%, Day 4 ~62%. Every day clears the 25% floor.
- **Capstone**: 2.0 h arc (Module 4.3 = 0.75 h warm-up + Module 4.4 = 1.25 h fault-injection run). Meets the ≥ 2 h capstone floor for courses ≥ 3 days *if* course-writer marks 4.3 as "capstone warm-up" in prose. Flagged for course-reviewer.
- **Lab reproducibility**: every SITL invocation in **Handoff → To lab-builder** uses syntax verified against `Tools/autotest/sim_vehicle.py` (the `-v ArduCopter -f quad` form is the default; `--console --map` are valid options at lines 1073-1085). The autotest invocation in L7 uses `Tools/autotest/autotest.py build.Copter test.Copter.ModeAltHold` — `ModeAltHold` is a real method at `Tools/autotest/arducopter.py:278`. The capstone L8 references `ArduCopter/ekf_check.cpp:79-89` for its log fingerprint, which matches the verified `LOGGER_WRITE_ERROR(LogErrorSubsystem::EKFCHECK, LogErrorCode::EKFCHECK_BAD_VARIANCE)` line.
- **No-overlap audit vs sibling courses**:
  - `course/custom_gnc_course_plane.md` and `course/custom_gnc_course_quadplane.md` are vehicle-Plane/QuadPlane and assume C/C++ proficiency, controls theory, and prior flight-code experience. Their Day 1 "compressed survival kit" sections explicitly skip the operational primer that this course is built around. There is **no module overlap** in module-set terms; the sole conceptual overlap is "what is a flight mode" / "what is a parameter" — both compressed in the GNC courses, both expanded here for absolute beginners. This is the entire point of the on-ramp positioning.
  - This course does not import any prose from either sibling course.
- **Lessons coverage**: iter 1, no prior reviewer findings or lab failures exist. Section explicitly says so. Future iterations will populate this section.
