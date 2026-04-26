# Introduction to ArduCopter for First-Year Aerospace Engineering Students

## Course Total: 8 hours / 2 days (4 h/day)

This course is the entry-level on-ramp to ArduPilot for students who have never touched an autopilot, a terminal, or production C++ before. By the end of two half-days, every student has the ArduPilot software-in-the-loop simulator running on their own laptop, has flown a simulated quadrotor through a full take-off / hover / land / disarm cycle from the command line, and has watched the autopilot detect a forced sensor failure and recover the vehicle on its own.

Acronyms used throughout this course are defined inline at first use. The shortlist:

- **PID** — Proportional-Integral-Derivative controller. The standard feedback-control building block ArduPilot uses everywhere it must drive a measured value to a target.
- **EKF** — Extended Kalman Filter. The "estimator" — the piece of code that fuses noisy sensor readings into one trusted answer for "where am I, how fast am I going, which way am I pointing."
- **IMU** — Inertial Measurement Unit. The chip that contains accelerometers (linear-acceleration sensors) and gyroscopes (angular-rate sensors).
- **GCS** — Ground Control Station. The laptop / tablet program that talks to the autopilot over a radio (or, in our case, a simulated link). MAVProxy is the GCS we use in this course.
- **MAVLink** — the binary message protocol used between an autopilot and a GCS.
- **MAV_CMD** — a MAVLink command identifier (e.g. `MAV_CMD_NAV_WAYPOINT`). You will see the names but will not write any.
- **RTL** — Return To Launch. A flight mode that flies the vehicle back to its take-off point automatically.
- **AHRS** — Attitude and Heading Reference System. Inside ArduPilot, the AHRS is the abstraction layer that hands "current attitude" to the rest of the code; the EKF is the implementation behind it.
- **SITL** — Software In The Loop. The simulator that runs the *exact same* autopilot binary on your laptop instead of on a real flight controller, with simulated physics in place of real sensors.

## Audience

First-year aerospace engineering undergraduates. High-school physics is in hand; basic calculus is *in progress* (so we use derivatives and integrals as intuition only — no proofs, no Jacobians). **No prior controls theory, no prior embedded systems, no prior Linux command-line fluency, no prior programming.** Many students will be opening a terminal for the first time during Module 1.2. The course is delivered in person, in a TA-supported computer lab.

## Vehicle and surface

Quadrotor X-frame ArduCopter, default SITL location, the entire course. No real flight, no bench hardware, no instructor demo flight. The autopilot runs in the SITL simulator on your laptop and nowhere else.

## Programming surface

Read-only code citations. You will inspect ArduPilot source in an editor; you will not compile a modification, write Python, or author a script. Every code reference in this course is a clickable link to the file and lines you should open. The pattern is always: *open this file, read these lines, here is the one or two things to notice, now move on.*

## Where this course sits in the path

This course is a prerequisite-style on-ramp to the two advanced courses already in this repo:

- [course/custom_gnc_course_plane.md](custom_gnc_course_plane.md) — fixed-wing ArduPlane for GNC engineers.
- [course/custom_gnc_course_quadplane.md](custom_gnc_course_quadplane.md) — VTOL QuadPlane for GNC engineers.

Both advanced courses assume the student already knows what an autopilot is, how to launch SITL, what a flight mode is, what a parameter is, what the scheduler is, what the EKF is for (as a black box), and what a failsafe is. This course establishes those topics from zero. After this course, a student should be able to read Day 1 of either advanced course without being lost on terminology or on the SITL toolchain.

### Prerequisite-chain assumption map

Below is the verbatim mapping the planner produced. For every operational topic the downstream GNC courses assume incoming students know, this table records either *which module establishes it* in this intro, or *"deliberately out of scope"* with a one-sentence justification. If you reach the end of this course and arrive at the GNC quadplane Day 1, the four "deliberately out of scope" rows tell you exactly what you have *not* yet been taught.

| # | Downstream-course assumption | Where this intro establishes it | Notes |
|---|---|---|---|
| 1 | The autopilot is one binary that runs on flight hardware and in SITL — same source code on both surfaces | Module 1.1 (What is an autopilot, what is ArduPilot, what is SITL) | Established at *survey* depth. |
| 2 | SITL is launched via `Tools/autotest/sim_vehicle.py -v <Vehicle> -f <frame>` and a MAVProxy console comes up | Module 1.2 (Set up your laptop and launch SITL) | Established at *applied* depth. The downstream course launches `-v ArduPlane -f quadplane`; this intro launches `-v ArduCopter -f quad`. The invocation pattern is identical. |
| 3 | MAVProxy idioms: `param show/set`, `mode <NAME>`, `arm throttle`, `rc <ch> <pwm>` | Modules 1.3 (first flight) and 1.5 (parameters) | Established at *applied* depth. |
| 4 | Flight modes are named (e.g. `STABILIZE`, `ALT_HOLD`, `RTL`); a mode is software running at high rate, not a hardware switch position | Module 1.4 (Flight modes from a pilot's view) | Established at *survey/applied* depth. The downstream course skips this; this intro re-derives it from zero. |
| 5 | Parameters are persistent runtime configuration, declared with `AP_GROUPINFO`-family macros, documented inline with `@Param` annotations | Module 1.5 (Parameters) | Established at *applied* depth, including a real `@Param` block read in source. |
| 6 | The autopilot is a fixed-rate scheduler running a list of tasks (FAST_TASK every loop, SCHED_TASK rate-limited) | Module 2.1 (Sensors + scheduler) | Established at *survey* depth. |
| 7 | Sensors (IMU/baro/mag/GPS) feed an EKF that produces the state estimate; the EKF is a black box at this stage | Module 2.1 (Sensors + scheduler) | Established at *survey* depth. The downstream course goes from zero to `errorScore()` and lane-switch internals — this intro deliberately stops at "the EKF exists and is fed by sensors." |
| 8 | The control path is mode `run()` → attitude controller → rate controller → PID → motor mixer → ESC | Module 2.2 (PID-as-black-box, briefly) | Established at *survey* depth. The mathematical detail (P/I/D/FF/IMAX, slew limit, target/error/derivative filters) is **deliberately out of scope** — the downstream course re-derives PID for engineers who already know it from another stack; this intro names the data path and stops. |
| 9 | The autopilot has automatic failsafes that fire when something goes wrong (RC loss, battery, GCS link, EKF variance) | Module 2.3 (Why does the autopilot ever decide for itself? Failsafes) | Established at *applied* depth, focused on the EKF failsafe because that is what the closing lab triggers. |
| 10 | Dataflash logs and `MAV_SEVERITY_*` GCS statustext are how you confirm what the autopilot did | Module 2.4 (Closing lab — observed in passing during the lab walkthrough) | Established at *applied* depth in the lab itself. The downstream course's MAVExplorer survey is cross-referenced but not taught. |
| 11 | Missions: ordered lists of `MAV_CMD_NAV_*` items, loaded with `wp load`, executed in `AUTO` | **Deliberately out of scope.** | The downstream GNC courses re-derive missions from zero in their own Day 1. At 8 h, mission content does not survive the budget; the on-ramp leaves this gap and flags it explicitly. |
| 12 | The autotest framework is a Python harness that scripts SITL flights for regression | **Deliberately out of scope** beyond a one-line mention in the closing lab. | Folded into the closing lab's setup. The downstream GNC courses do not assume autotest fluency in their Day 1 — they introduce it on Day 5. |
| 13 | Build system: `./waf configure --board sitl && ./waf copter` is the SITL build | Module 1.2 (Set up your laptop) | Established at *applied* depth. |
| 14 | ArduPilot code conventions (`AP_HAL::millis()`, `is_zero()`, `GCS_SEND_TEXT()`, snake_case methods, `AP_`/`AC_`/`AR_` class prefixes) | **Deliberately out of scope.** | The downstream course reaches these in its Module 3 (Build System & Code Conventions). The intro does not write code; teaching code conventions to non-coders wastes the budget. The intro does *show* `AP_GROUPINFO` blocks in source so you recognise the shape when you see them in Day 1 of the downstream course. |
| 15 | `AP_<FEATURE>_ENABLED` compile-time flags exist | **Deliberately out of scope.** | Same rationale as #14. |

**Known gaps this course deliberately leaves**: items 11, 12, 14, 15. When you start the GNC quadplane Day 1, expect to meet missions, autotest, code conventions, and compile-time feature flags as new material there.

## Course structure

| Day | Theme | Module-hours | Buffer | Total |
|-----|-------|--------------|--------|-------|
| 1 | Set up SITL, first flight, flight modes, parameters | 3.5 | 0.5 | 4.0 |
| 2 | Under the hood: sensors, scheduler, PID-as-black-box, failsafes, closing lab | 3.5 | 0.5 | 4.0 |
| | **Total** | **7.0** | **1.0** | **8.0** |

Buffer per day is 30 min and is the only slack; per-module times within a day sum to 3.5 h exactly.

---

## Day 1 — Set up SITL, first flight, flight modes, parameters (4 h)

**Goal**: by the end of Day 1, every student has SITL running on their own laptop, can launch a simulated quadcopter, arm it, take off in `STABILIZE`, hover, switch to `ALT_HOLD`, switch to `LAND`, and disarm — using MAVProxy commands typed at the terminal — and can change a parameter and watch the simulator behave differently.

Per-day budget: 3.5 h modules + 0.5 h buffer = 4.0 h. Hands-on share: ≈ 2.05 h / 3.5 h modules = **~59 %**.

### Module 1.1 — What is an autopilot, what is ArduPilot, what is SITL? (30 min, lecture+demo, *survey*)

**Learning objectives**:

1. Define autopilot, ground control station (GCS), and ground/air segment in plain English.
2. Place ArduPilot in the open-source autopilot landscape (vs. proprietary, vs. research code) at one slide of depth.
3. Recognise that the *same* ArduPilot binary that flies real hardware also flies in SITL — the difference is only the hardware abstraction layer (HAL) backend underneath.
4. Recognise that the codebase has safety-critical conventions (compile-time feature flags, embedded RAM/flash constraints) that we will see throughout, even though every lab is pure simulation.

**The autopilot.** An autopilot is the piece of software that decides, at hundreds of times per second, what each motor on a vehicle should do so the vehicle behaves the way the pilot — or the mission — asked for. On a quadrotor, the autopilot reads sensors (gyro, accelerometer, barometer, GPS), works out where the vehicle is and how it is moving, compares that against what was requested, and writes four numbers (one per motor) out to the speed controllers. Every fraction of a second. Forever, while powered.

**The ground/air split.** ArduPilot lives on the *air* side (the flight controller bolted to the airframe). The *ground* side is the laptop or tablet running a GCS that lets a human watch telemetry, change parameters, and send commands. In this course the GCS is **MAVProxy**, a command-line program. There are graphical GCSs (Mission Planner, QGroundControl); we do not use them in this course.

**ArduPilot in the landscape.** Half a slide of depth, no more. ArduPilot is one of the two large open-source autopilot stacks (the other is PX4); both target small unmanned vehicles. ArduPilot supports many vehicle types — Copter, Plane, Sub, Rover, AntennaTracker, Blimp — out of one source tree. We will spend the entire course in the Copter half. Do not worry about governance, release cadence, or community structure; one slide is enough.

**SITL is the same binary.** The single most important conceptual handoff in this module: the ArduPilot code that we read together also runs *unchanged* on a real flight controller. The difference between "running on a Pixhawk" and "running on your laptop" is only the HAL backend that sits underneath the autopilot — `AP_HAL_ChibiOS` for STM32 flight controllers, `AP_HAL_SITL` for the simulator. This is why a SITL-only course teaches you something useful about the real flight stack.

**Two pieces of context to carry forward.**

*ArduPilot is safety-critical software.* The code we will read together flies real vehicles. The community's working rule is that every change must be correct, tested, and reviewable by a human maintainer before it ships. That posture is why the codebase looks the way it does — verbose names, compile-time feature flags, a hardware abstraction layer between the autopilot and the silicon. None of that is decoration; it is the cost of running on something that can fall out of the sky.

*Big-picture architecture: vehicles + libraries + HAL.* The repo has six vehicle directories at the top level (`ArduCopter/`, `ArduPlane/`, `ArduSub/`, `Rover/`, `AntennaTracker/`, `Blimp/`); a large `libraries/` tree with the sensor drivers, controllers, and shared services; and a *hardware abstraction layer* (HAL) that lets the same code run on different hardware. The HAL has four backends: `AP_HAL_ChibiOS` (STM32 flight controllers), `AP_HAL_ESP32`, `AP_HAL_Linux` (single-board computers like Navio2), and `AP_HAL_SITL` (the simulator we will use all course). Throughout the codebase you will see lines that begin with `#if AP_<FEATURE>_ENABLED` — these are *compile-time feature flags*. They are why the same source tree can produce a tiny embedded firmware for an STM32 chip and a fat simulator binary for your laptop.

**Code-reading**: open one file and look only at what the heading line tells you.

- [ArduCopter/Copter.h:181](../ArduCopter/Copter.h#L181) — one line: `class Copter : public AP_Vehicle {`. This is the file you will return to over and over. Every Copter feature you meet in this course hangs off this class.

**Hands-on (in module)**: the instructor live-demos `Tools/autotest/sim_vehicle.py -v ArduCopter --console --map` on the projector. Students watch only. About 5 min.

### Module 1.2 — Set up your laptop: install, build, and launch SITL (1 h, lab, *applied*)

**Learning objectives**:

1. Run the prerequisites installer on Ubuntu (or the macOS / Windows-WSL equivalent) without panicking on the long output.
2. Clone ArduPilot with submodules and run `./waf configure --board sitl && ./waf copter`.
3. Launch SITL with `Tools/autotest/sim_vehicle.py -v ArduCopter --console --map`.
4. Recognise the three windows that appear (MAVProxy console, MAVProxy command, map) and what each is for.

**Frame for the hour.** This is a one-hour lab. Most of the hour is waiting for the installer and the build. Do not panic at long output; the script tells you what it is doing. If something fails, the most common cause on a fresh Ubuntu install is a stale apt mirror — your TA will diagnose this for you and switch the mirror if needed.

**The reference docs.** Two repo-root files exist for installation and build trouble. Do not read them end-to-end during the lab; bookmark them.

- [BUILD.md](../BUILD.md) — Waf build system in depth (boards, build groups, debug, Docker workflow). The reference for any unfamiliar build error.
- [Tools/environment_install/install-prereqs-ubuntu.sh](../Tools/environment_install/install-prereqs-ubuntu.sh) — the Ubuntu prerequisites installer. The TAs run this for you; you do not need to read it line-by-line.

**Code-reading the launcher.** SITL is launched by a Python script. Two anchors are enough to see what `-v ArduCopter` actually plugs into.

- [Tools/autotest/sim_vehicle.py:287](../Tools/autotest/sim_vehicle.py#L287) — the literal string `'ArduCopter.elf',`. This is one entry in a small list of binary names the launcher knows how to find. When you pass `-v ArduCopter`, *this* is the file the launcher will look for under `build/sitl/bin/`.
- [Tools/autotest/sim_vehicle.py:1073-1085](../Tools/autotest/sim_vehicle.py#L1073-L1085) — the option-parser block that defines `-v`/`--vehicle` and `-f`/`--frame`. Open these lines and just read the `help=` strings. You do not need to know what `optparse` is. You need to recognise that this is where the command-line option you will type lands inside the script.

**Lab spec — Lab L1 "First SITL launch"** (handoff to lab-builder; full runnable lab will live under `course/labs/intro-arducopter-aero-y1/`).

Step by step, in order, on your own laptop:

1. **Run the prerequisites installer.** On Ubuntu: `Tools/environment_install/install-prereqs-ubuntu.sh`. Expect 5–15 min of apt traffic. macOS / Windows-WSL students follow the equivalent script in the same directory; TAs will direct you. If apt errors cascade across unrelated packages, raise your hand — the TA will switch your apt mirror.
2. **Clone with submodules.** `git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git && cd ardupilot`. (TA may have a local mirror; ask.)
3. **Configure and build for SITL.** From the repo root:

       ./waf configure --board sitl
       ./waf copter

   Expect the configure step to take ~30 s and the `copter` build to take 2–5 min on first run. On reruns it is incremental and fast. Never run waf with `sudo`.
4. **Launch SITL with the GCS attached.** From the same repo root:

       Tools/autotest/sim_vehicle.py -v ArduCopter --console --map

   Three windows appear: the **MAVProxy console** (text status — altitude, mode, battery), the **MAVProxy command** terminal (where you type), and the **map** (a vehicle marker at the SITL default location).

**Pass criterion** (the verdict the TA reads): a `HEARTBEAT` MAVLink message arrives at the GCS and the map renders the vehicle. The MAVProxy console will print a `STATUSTEXT: APM:Copter ...` line and then `online system 1` within ~30 s of launch. If both happen, you pass this lab.

**MAVProxy commands you will use.** This course uses only a small subset of MAVProxy. We list them as we need them, not all up front.

- `mode <NAME>` — request a flight mode change (used in Module 1.3).
- `arm throttle` — arm motors (Module 1.3).
- `rc 3 1700` — push the simulated throttle stick to 1700 µs PWM (Module 1.3).
- `param show <NAME>` and `param set <NAME> <VALUE>` — read and write parameters (Modules 1.5 and 2.4).

There is no other MAVProxy command in this course's labs.

### Module 1.3 — Your first flight: arm, take off, land, disarm (45 min, lab, *applied*)

**Learning objectives**:

1. Use the MAVProxy commands `mode`, `arm throttle`, `rc 3 1700`, `mode LAND`.
2. Read the textual telemetry: altitude, battery, mode.
3. Recognise `STABILIZE` and `LAND` by behaviour, not yet by source.

**The mode you start in is `STABILIZE`.** When you launch SITL, the simulated copter sits on the ground in `STABILIZE`. `STABILIZE` keeps the vehicle level when you let go of the roll/pitch sticks; the throttle stick goes straight through to motor thrust. There is no altitude hold. There is no position hold. If you push the stick forward, the vehicle tilts forward and accelerates; if you let go, it stops tilting but keeps drifting. This is the closest copter mode to "manual flight."

**The mode IDs.** Open [ArduCopter/mode.h:77-109](../ArduCopter/mode.h#L77-L109). This is the master enumeration of every Copter flight mode. Notice three things: each mode is a name plus a number (`STABILIZE = 0`, `ALT_HOLD = 2`, `LAND = 9`); the comments next to each mode describe in one phrase what the mode does; the mode number is what gets stored in the parameter `FLTMODE1` etc. (which we meet in Module 1.5). Do not memorise the table — recognise its shape.

**The mode body, at survey depth.** Open [ArduCopter/mode_stabilize.cpp:9-64](../ArduCopter/mode_stabilize.cpp#L9-L64). Read the comment at line 11: *"stabilize_run - runs the main stabilize controller; should be called at 100hz or more."* That is the contract. Every flight mode has a `run()` method called at high rate. Inside `run()`, the mode reads pilot stick input, decides on a target attitude or thrust, and hands it down to the attitude controller. **Do not unpack the spool-state machine** in the lower half of the function — that is internals depth and we are at *survey*. The one thing to notice: the function is built around a `switch` on motor spool state (`SHUT_DOWN`, `GROUND_IDLE`, `THROTTLE_UNLIMITED`, …). Spool state is the autopilot's safety gate between "motors off" and "motors free to spin." That is enough.

**Lab spec — Lab L2 "First flight (STAB → LAND)"** (handoff to lab-builder).

In your already-running SITL session (from Lab L1), in the MAVProxy command terminal, type these commands one at a time, watching the console for the response after each:

1. `mode STABILIZE` — should report mode change accepted (you usually start there already).
2. `arm throttle` — motors arm. Expect a `Motors armed` (or equivalent) statustext.
3. `rc 3 1700` — throttle stick to 1700 µs. The simulated copter lifts off; watch altitude rise on the console.
4. Wait until altitude > 10 m on the console.
5. `mode LAND` — autopilot now flies the descent itself.
6. Wait. The console will print `LAND complete` and then `Disarming motors`.

**Pass criterion**: a `Disarming motors` statustext arrives within 90 s of `arm throttle`.

If something feels wrong (the vehicle drifts off the screen, the simulator hangs), close the SITL window and relaunch via Lab L1 step 4. SITL is cheap to restart.

### Module 1.4 — Flight modes from a pilot's view (45 min, lecture+demo, *survey*)

**Learning objectives**:

1. Sort copter modes into three buckets — *manual*, *stabilized-with-altitude*, *autonomous* — and place at least one mode in each bucket from memory.
2. Explain a mode prerequisite in plain English: "`RTL` needs a position estimate; `STABILIZE` does not."
3. Recognise that mode switching can be denied by the autopilot if prerequisites are not met.

**The three-bucket taxonomy.** Verbatim from the plan:

- **Manual** — `STABILIZE`, `ACRO`. The pilot's stick goes (almost) straight to motor outputs; the autopilot levels but does not hold position or altitude. If you let go and walk away, the vehicle drifts.
- **Stabilized-with-altitude** — `ALT_HOLD`. The autopilot holds altitude using the barometer (and, when available, GPS), but the pilot is still flying horizontally with the stick. If you let go of pitch and roll, the vehicle does not drift vertically; horizontally it does.
- **Autonomous** — `AUTO`, `GUIDED`, `RTL`, `LAND`. The autopilot decides what to do on its own. `AUTO` follows a stored mission; `GUIDED` follows commands from the GCS; `RTL` flies home; `LAND` performs a controlled descent at the current location.

The historical mode list at [ArduCopter/mode.h:77-109](../ArduCopter/mode.h#L77-L109) (re-cited from Module 1.3) does not group modes this way — it lists them in numerical order, which is historical. Use the three-bucket taxonomy above when you reason about modes.

**`LOITER` is intentionally not in this course.** The 8-hour budget does not have room for a third stop on the mode tour. You will meet `LOITER` in the downstream GNC courses.

**The init / run pattern, shared by every mode.** Open [ArduCopter/mode_althold.cpp:9-22](../ArduCopter/mode_althold.cpp#L9-L22). Notice the function name `ModeAltHold::init` and the comment at line 12: *"althold_init - initialise althold controller."* `init()` is called once when the mode is entered; `run()` is called at high rate while the mode is active. Notice the calls into `pos_control` (the position controller) — `D_init_controller`, `D_set_max_speed_accel_m`. You do not need to know what those do; notice that `init()` is the place where the mode hands speed and acceleration limits to the controller it will use.

Then open [ArduCopter/mode_althold.cpp:26-104](../ArduCopter/mode_althold.cpp#L26-L104) — the `run()` body. Walk this at survey depth: notice the four-state machine names (`MotorStopped`, `Landed_Pre_Takeoff`, `Takeoff`, `Flying`). Each state decides differently what to do with the pilot's stick. Do *not* unpack the algebra in any branch — we are at survey.

**Mode switching can be refused.** Open [ArduCopter/mode.cpp:313-396](../ArduCopter/mode.cpp#L313-L396). This is `Copter::set_mode`, the function the autopilot calls every time anything — pilot, GCS, or RC switch — asks for a mode change. Read at survey depth. The two prerequisite checks to notice are at *applied* depth:

- [ArduCopter/mode.cpp:394](../ArduCopter/mode.cpp#L394) — `mode_change_failed(new_flightmode, "requires position");`. If you ask for a mode that needs to know where it is (for example `RTL`) but the EKF cannot give a position, the mode change is denied, and you get this exact message in the console.
- [ArduCopter/mode.cpp:404](../ArduCopter/mode.cpp#L404) — `mode_change_failed(new_flightmode, "need alt estimate");`. Same shape, for altitude.

The behavioural takeaway: when MAVProxy reports a mode-change failure, the autopilot is doing exactly what you would want — it refuses to enter a mode whose prerequisites it cannot satisfy.

**Hands-on (in module)**: in the running SITL, the instructor types on the projector copy:

    param set SIM_GPS_DISABLE 1
    mode RTL

Expect the autopilot to refuse the mode change with `requires position`. Students try the same on their own SITL session. Then on the projector:

    param set SIM_GPS_DISABLE 0

restores the simulated GPS so the rest of the day works. About 10 min total inside this module.

### Module 1.5 — Parameters: ArduPilot's configuration surface (30 min, lecture+demo, *applied*)

**Learning objectives**:

1. Define a parameter as a runtime-configurable value, persistent across reboots.
2. Read the canonical parameter-doc format and recognise `@Param`, `@DisplayName`, `@Description`, `@Range`, `@Units`.
3. Run `param show <NAME>` and `param set <NAME> <VALUE>` from MAVProxy.
4. Find which file declares a parameter by searching for its name with `grep`.

**What a parameter is.** A parameter is a named variable whose value is stored on the autopilot, survives a reboot, and can be read or changed from the GCS at runtime. Parameters are *not* compiled into the binary. The binary reads them from non-volatile storage at boot and applies them. This is why two flight controllers running the same firmware can fly very differently: same code, different parameters.

**The `@Param` annotation block.** Every parameter is documented next to its declaration in source, in a comment block the documentation tooling parses. Open [ArduCopter/Parameters.cpp:44-51](../ArduCopter/Parameters.cpp#L44-L51) and read the eight lines that declare `PILOT_THR_FILT`. The seven `// @...` comment lines and the `GSCALAR(...)` line below them are the canonical shape: `@Param` (the short name, capped at 16 characters), `@DisplayName`, `@Description`, `@User` (`Standard` or `Advanced`), `@Units`, `@Range`, `@Increment`. (Other parameters use `@Values` or `@Bitmask` instead of `@Range` when the parameter is an enum or a bitmask.) When you read a parameter's documentation in the wiki or in Mission Planner, *this* is where the text comes from.

**A real parameter table.** Open [ArduCopter/Parameters.cpp:33-67](../ArduCopter/Parameters.cpp#L33-L67). This is the start of the master `Copter::var_info[]` array — every parameter the Copter vehicle owns. Read the first few entries: `FORMAT_VERSION` (Eeprom format version), `PILOT_THR_FILT` (throttle filter cutoff in Hz), `PILOT_THR_BHV` (throttle stick behavior bitmask), `GCS_PID_MASK` (which PID-tuning streams to send to the GCS). Notice how every entry has a full `@Param` block above it. Notice `GSCALAR(...)` — a macro that registers the variable into the parameter system. You do not need to memorise the macro; recognise its shape.

**How RC switch positions become flight modes.** Open [ArduCopter/Parameters.cpp:149-191](../ArduCopter/Parameters.cpp#L149-L191). This is the `FLTMODE1`–`FLTMODE6` and `FLTMODE_CH` block. The mechanism: the autopilot watches the PWM value on RC channel `FLTMODE_CH` and maps it into one of six bands; each band reads the corresponding `FLTMODE<n>` parameter, which holds a flight-mode number from the enum we read in Module 1.3. So if `FLTMODE1 = 0` and you put your transmitter switch into the lowest band, you fly in `STABILIZE = 0`. This is how a single 3-position switch becomes "six modes I can choose from."

**Hands-on (in module)**: in the running SITL, type in the MAVProxy command terminal:

    param show SIM_WIND_SPD

Notice the value is `0` by default. Then:

    param set SIM_WIND_SPD 5

Watch the simulated copter's hover wobble change as the simulator fakes a 5 m/s wind. Then:

    param set SIM_WIND_SPD 0

to restore. About 5 min total inside this module. This single activity is the "parameters change behaviour" payload — there is no separate wind/`WPNAV_SPEED` lab in this course.

### Day 1 buffer / Q&A (30 min)

Used for environment-issue mop-up: apt-mirror failures, Windows-WSL path issues, students whose build did not finish in time. TAs handle apt-mirror diagnostics directly.

**Day 1 totals**: 0.5 + 1.0 + 0.75 + 0.75 + 0.5 = **3.5 h modules** + 0.5 h buffer = **4.0 h**.
Hands-on share: ~0.05 h (1.1) + 1.0 h (1.2) + 0.75 h (1.3) + ~0.15 h (1.4) + ~0.1 h (1.5) ≈ **2.05 h / 3.5 h ≈ 59 %**.

---

## Day 2 — Under the hood: sensors, scheduler, PID-as-black-box, failsafes, closing lab (4 h)

**Goal**: by the end of Day 2, you can read (not write) the rough call path from sensor reading → scheduler tick → mode `run()` → PID → motor output, you can name what the EKF is for without solving any equations, and you have run a SITL flight in which an injected GPS failure triggers the EKF failsafe — and you can identify the moment of failure in the dataflash log.

Per-day budget: 3.5 h modules + 0.5 h buffer = 4.0 h. Hands-on share: ≈ 1.45 h / 3.5 h modules = **~41 %**.

### Module 2.1 — Sensors and the scheduler: the heartbeat of the autopilot (45 min, lecture+demo, *survey*)

**Learning objectives**:

1. Name the sensors a copter uses — IMU, barometer, magnetometer, GPS — in one sentence each.
2. Define "estimator" as the thing that fuses noisy sensors into one trusted estimate of where the vehicle is and how it is moving.
3. Recognise that the EKF (Extended Kalman Filter) is the estimator — and stop there. **No math.**
4. Define "scheduler" as a fixed list of `(function, rate, max_micros)` tuples that the autopilot runs forever in a loop.
5. Identify three landmark scheduler entries: IMU update, rate controller, EKF state estimator.

**The sensors, one sentence each.**

- **IMU (Inertial Measurement Unit)** — accelerometers (linear acceleration, three axes) plus gyroscopes (angular rate, three axes). The IMU is sampled fastest (every loop iteration); everything downstream depends on it.
- **Barometer** — atmospheric pressure, used to estimate altitude.
- **Magnetometer (compass)** — Earth's magnetic field, used to estimate heading.
- **GPS** — global position and ground velocity.

You do not need to know how any of these work as physical devices. The point is *they exist and they go through the EKF*. The library directories are `libraries/AP_InertialSensor/`, `libraries/AP_Baro/`, `libraries/AP_Compass/`, `libraries/AP_GPS/` (and `libraries/AP_AHRS/` for the abstraction that hands "current attitude" to the rest of the code). Open them in your file browser if you are curious; we will not cite line-by-line into them.

**The estimator and the EKF.** All four sensors are noisy. The autopilot must turn them into one trusted answer for "where am I, how fast am I going, which way am I pointing." That job is the *estimator*. The estimator ArduPilot uses is an Extended Kalman Filter (EKF). For this course the EKF is a black box: sensors go in, an estimate comes out. The downstream GNC courses go from zero to internals (variances, lane switches). We stop at "the EKF exists and is fed by sensors."

**The scheduler is one list, run forever.** Open [ArduCopter/Copter.cpp:113-149](../ArduCopter/Copter.cpp#L113-L149). This is the start of `Copter::scheduler_tasks[]`: a hard-coded array of every function the autopilot wants to run, with each entry tagged either `FAST_TASK` (run on every main-loop iteration) or `SCHED_TASK(func, rate_hz, max_us, prio)` (run at a fixed rate). The whole autopilot, conceptually, is "iterate through this list forever."

Read the `FAST_TASK` block at the top. Three lines to notice:

- [ArduCopter/Copter.cpp:117](../ArduCopter/Copter.cpp#L117) — `FAST_TASK(run_rate_controller_main),`. The rate controller runs every loop. Hold this thought; we walk into it in Module 2.2.
- [ArduCopter/Copter.cpp:126](../ArduCopter/Copter.cpp#L126) — the comment `// run EKF state estimator (expensive)`.
- [ArduCopter/Copter.cpp:127](../ArduCopter/Copter.cpp#L127) — `FAST_TASK(read_AHRS),`. This call is what runs the EKF. The EKF runs every loop iteration. (`AHRS` is the public interface; the EKF is the implementation behind it.)

Now scroll to [ArduCopter/Copter.cpp:151-201](../ArduCopter/Copter.cpp#L151-L201). These are `SCHED_TASK` entries — rate-limited tasks. Notice the rates in the second column: 50 Hz, 10 Hz, 1 Hz. Different things run at different rates because they need different freshness; the IMU must be sampled fast or the controller flies blind, but the EKF check (next paragraph) only needs to decide once every 100 ms. At [ArduCopter/Copter.cpp:201](../ArduCopter/Copter.cpp#L201) read `SCHED_TASK(ekf_check, 10, 75, 84),` — the 10 Hz monitor that triggers the EKF failsafe in Module 2.3 and the closing lab.

**One line of `main()`.** Open [ArduCopter/Copter.cpp:998](../ArduCopter/Copter.cpp#L998) — `AP_HAL_MAIN_CALLBACKS(&copter);`. This single macro line *is* the entire ArduCopter binary's entry point. The macro is at [libraries/AP_HAL/AP_HAL_Main.h:35-41](../libraries/AP_HAL/AP_HAL_Main.h#L35-L41); read it but do not unpack. The shape: it generates a `main()` that hands control to `hal.run()`, which calls back into the vehicle. Survey depth: *`main()` is generated; it calls `hal.run`; the scheduler does the rest.*

The "rest" — the loop the scheduler runs — is at [libraries/AP_Vehicle/AP_Vehicle.cpp:558-566](../libraries/AP_Vehicle/AP_Vehicle.cpp#L558-L566). Notice line 561: `scheduler.loop();`. The main loop of the autopilot does literally one thing: ask the scheduler for one iteration. Forever.

**Hands-on (in module)**: in the running SITL, type:

    param show SCHED_LOOP_RATE

Confirm the value is `400` (Hz). That is the rate at which `FAST_TASK`s run. Optionally, in your terminal, run `grep -c SCHED_TASK ArduCopter/Copter.cpp` and notice how many rate-limited tasks the Copter scheduler manages. About 5 min.

### Module 2.2 — From stick input to motor output: the data path (45 min, lecture+demo, *survey* with one *applied* cite)

**Learning objectives**:

1. Sketch the call path: pilot stick → mode `run()` → attitude controller → rate controller → PID → motor mixer → ESC. Memorise this sentence verbatim — it is the single most-load-bearing handoff to the downstream GNC course.
2. Recognise that PID is "compute an error, multiply by P, add the integral, add the derivative, output." Do not derive — name the term and stop.
3. Read the X-frame motor angle table and understand why a quad X has motors at +45° / -135° / -45° / +135°.

**The verbatim sentence**. Stick → mode `run()` → attitude controller → rate controller → PID → motor mixer → ESC. Every word stands for one stage in the pipeline that turns a pilot input into a motor command.

**Stage 1 — mode `run()` reads sticks.** We saw this in Modules 1.3 and 1.4. The mode's `run()` function decides what target attitude or thrust the pilot is asking for.

**Stage 2 — attitude controller.** Mode `run()` hands a target attitude (or angular rate) to `attitude_control->...`. The attitude controller turns "I want to be tilted 5° forward" into "I need this much pitch *rate* right now."

**Stage 3 — rate controller, called every loop.** Open [ArduCopter/Copter.cpp:117](../ArduCopter/Copter.cpp#L117) — re-cited from Module 2.1. The `FAST_TASK(run_rate_controller_main)` line is the entry. The body is at [ArduCopter/Attitude.cpp:10-24](../ArduCopter/Attitude.cpp#L10-L24); read it. Notice it does almost nothing — sets `dt`, then calls `attitude_control->rate_controller_run()`. The actual rate-controller body is in [libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:457-485](../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L457-L485) — `AC_AttitudeControl_Multi::rate_controller_run_dt`. **This is the only *applied* cite in this module.** Read it carefully:

- [libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:473](../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L473) — `_motors.set_roll(get_rate_roll_pid().update_all(ang_vel_body.x, gyro_rads.x, dt, …) …);`. Roll axis: target angular rate goes in, gyro reading goes in, `dt` goes in, a PID output comes out.
- [libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:476](../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L476) — same shape on pitch.
- [libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:479](../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L479) — same shape on yaw.

Three PIDs, one per axis, each called once per loop. Name the inputs (target angular velocity, gyro reading, `dt`) without unpacking the PID math.

**Stage 4 — PID, as a black box.** Open [libraries/AC_PID/AC_PID.cpp:196-272](../libraries/AC_PID/AC_PID.cpp#L196-L272) — `AC_PID::update_all`. We are at *survey* depth. Identify the line `float P_out = (_error * _kp);` and stop. PID is "compute an error (target minus measurement), multiply by P, add the integral, add the derivative, output." That is the sentence. The filtering and integrator branches are named — `get_filt_T_alpha`, `get_filt_E_alpha`, `get_filt_D_alpha`, `update_i` — but we do not unpack any of them. The downstream GNC course re-derives PID for engineers; we name the data path and stop.

**Stage 5 — motor mixer.** Open [libraries/AP_Motors/AP_MotorsMatrix.cpp:213-244](../libraries/AP_Motors/AP_MotorsMatrix.cpp#L213-L244) — the opening of `AP_MotorsMatrix::output_armed_stabilizing`. *Survey* depth: the mixer takes 4 numbers (roll, pitch, yaw, throttle) and decides how hard each of the four motors should push.

**Why a quad X has motors at +45° / -135° / -45° / +135°.** Open [libraries/AP_Motors/AP_MotorsMatrix.cpp:592-602](../libraries/AP_Motors/AP_MotorsMatrix.cpp#L592-L602) — the `MOTOR_FRAME_TYPE_X` branch. Notice the table:

       {   45, AP_MOTORS_MATRIX_YAW_FACTOR_CCW,  1 },
       { -135, AP_MOTORS_MATRIX_YAW_FACTOR_CCW,  3 },
       {  -45, AP_MOTORS_MATRIX_YAW_FACTOR_CW,   4 },
       {  135, AP_MOTORS_MATRIX_YAW_FACTOR_CW,   2 },

Four entries, one per motor. Each entry is `{ angle (degrees from forward), yaw direction, motor number }`. The angles +45°, -135°, -45°, +135° place the four motors at the corners of a square that is rotated 45° from the body-forward axis — that is the "X" frame, as opposed to the "+" frame (which would have motors directly forward, back, left, right). The yaw-factor column alternates CCW/CW: half the motors spin one way, half the other. That cancellation is what lets a quadrotor yaw at all without spinning around the prop torque.

**Stage 6 — ESC.** The mixer's four numbers go out as PWM (or DShot, or CAN) to the four electronic speed controllers. We do not look at HAL output paths in this course.

**Hands-on**: none. The closing lab in Module 2.4 is the day's main hands-on payload.

### Module 2.3 — Why does the autopilot ever decide for itself? Failsafes (45 min, lecture+demo, *applied*)

**Learning objectives**:

1. Define "failsafe" as an automatic action the autopilot takes when something goes wrong.
2. Name four common failsafes a first-year should recognise: RC loss, battery, GCS link loss, **EKF variance**.
3. Read the EKF-failsafe code path at *applied* depth, in preparation for the closing lab.

**Failsafe, plainly.** A failsafe is what the autopilot does on its own when the operator has not asked for anything, or has asked for something the autopilot cannot trust. Failsafes are the autopilot's "do something sensible" reflex. Four to recognise:

- **RC loss** — the link to the RC transmitter dies. Default action: continue mission, or `RTL`, depending on configuration.
- **Battery** — voltage drops below a threshold. Default action: `RTL` or `LAND`.
- **GCS link loss** — the link to the ground station dies (in modes where the GCS is steering, like `GUIDED`). Default action: `RTL` or `LAND`.
- **EKF variance** — the estimator stops trusting itself. *This is what the closing lab triggers.* Default action: depends on `FS_EKF_ACTION`.

**The EKF failsafe code path.** Open [ArduCopter/ekf_check.cpp:30-90](../ArduCopter/ekf_check.cpp#L30-L90) — `Copter::ekf_check`. This function runs at 10 Hz (per the scheduler entry at [ArduCopter/Copter.cpp:201](../ArduCopter/Copter.cpp#L201) we read in Module 2.1). At *applied* depth, name these elements as you read:

- `ekf_check_state.fail_count` — counter of consecutive bad samples.
- `ekf_check_state.bad_variance` — sticky flag: once raised, the autopilot has declared an EKF problem.
- `g.fs_ekf_thresh` — the parameter `FS_EKF_THRESH` (a numeric variance threshold). If set to zero, the check is disabled.
- `EKF_CHECK_ITERATIONS_MAX` — how many consecutive bad samples in a row before the failsafe fires.
- [ArduCopter/ekf_check.cpp:83](../ArduCopter/ekf_check.cpp#L83) — `LOGGER_WRITE_ERROR(LogErrorSubsystem::EKFCHECK, LogErrorCode::EKFCHECK_BAD_VARIANCE);`. This writes an `ERR` row to the dataflash log with `Subsys = EKFCHECK` and `ECode = BAD_VARIANCE`. **This is the line you will read out of the log in the closing lab.**
- [ArduCopter/ekf_check.cpp:86](../ArduCopter/ekf_check.cpp#L86) — `gcs().send_text(MAV_SEVERITY_CRITICAL, "EKF variance: %s", …);`. This sends the `EKF variance:` `MAV_SEVERITY_CRITICAL` statustext that you will see live in the MAVProxy console during Step B of the closing lab.
- [ArduCopter/ekf_check.cpp:89](../ArduCopter/ekf_check.cpp#L89) — `failsafe_ekf_event();`. The actual action — change mode according to `FS_EKF_ACTION`.

**What the EKF "variance" actually means is out of scope for this course.** The downstream GNC course derives `errorScore()` and the lane-switch logic from zero. For us: the EKF runs a self-test; when its self-confidence drops below `FS_EKF_THRESH` for `EKF_CHECK_ITERATIONS_MAX` consecutive samples, the autopilot declares a problem.

**Pre-arm checks: the same posture, before take-off.** Open [ArduCopter/AP_Arming_Copter.cpp:8-20](../ArduCopter/AP_Arming_Copter.cpp#L8-L20). `pre_arm_checks()` and `run_pre_arm_checks()`. Read at survey depth. The first thing `run_pre_arm_checks` does at line 17 is `exit immediately if already armed`. The point of pre-arm checks is the same as the point of failsafes: the autopilot refuses to leave the ground unless every prerequisite is met. Same code-base personality — better to refuse than to be wrong.

**Hands-on (in module)**: instructor demos on the projector copy of SITL: arm, take off in `STABILIZE`, hover, then `param set SIM_GPS_DISABLE 1`. Watch the `EKF variance` `CRITICAL` warning appear and the vehicle's mode change. Students do not run this themselves yet — they will in Module 2.4. About 5 min.

### Module 2.4 — Closing lab: scripted flight with a forced EKF failsafe (1.25 h, lab, *applied*)

**Learning objectives**:

1. Run a full scripted SITL flight: take off, hover, RTL, disarm — with **no fault**.
2. Run the same scripted flight with `SIM_GPS_DISABLE 1` injected mid-flight; observe the EKF failsafe fire; observe the vehicle still recover (`LAND` or `RTL` depending on the default value of `FS_EKF_ACTION`).
3. Inspect the dataflash log afterward to identify the moment of failsafe by both the GCS statustext and the dataflash `ERR` row.

**Reference fingerprint.** The single source-of-truth code block for this lab is [ArduCopter/ekf_check.cpp:79-89](../ArduCopter/ekf_check.cpp#L79-L89) — the inner block of `ekf_check` that fires when `fail_count >= EKF_CHECK_ITERATIONS_MAX`. Re-cited from Module 2.3. Three lines you will see triggered in real time:

- Line 83 — the `LOGGER_WRITE_ERROR(EKFCHECK, BAD_VARIANCE)` row in the dataflash log.
- Line 86 — the `EKF variance:` `MAV_SEVERITY_CRITICAL` statustext in the MAVProxy console.
- Line 89 — the `failsafe_ekf_event()` call that changes mode.

**Lab spec — Lab L3 "Closing lab: clean run + EKF-failsafe injection"** (handoff to lab-builder; the runnable lab will live under `course/labs/intro-arducopter-aero-y1/`). Two steps in a single SITL session.

- **Vehicle**: `ArduCopter`, frame: `quad` (X), at the SITL default location.
- **SITL invocation**: same as Lab L1 — `Tools/autotest/sim_vehicle.py -v ArduCopter --console --map`.
- **Parameters**: defaults except `SIM_GPS_DISABLE` (toggled in Step B). Leave `FS_EKF_ACTION`, `FS_EKF_THRESH`, and the `EK3_*` family at their defaults; the lab document for this iteration will record the `FS_EKF_ACTION` default value at the iteration's commit so you know which mode (`LAND` or `RTL`) to expect.

**Step A — clean run (~25 min including launch and walkthrough)**:

A scripted MAVProxy run. From a freshly-launched SITL:

    arm throttle
    mode GUIDED
    takeoff 30
    <hover 30 s>
    mode RTL
    <wait disarm>

**Pass criterion**: vehicle disarmed within 180 s of `arm throttle`; **no** `MAV_SEVERITY_CRITICAL` statustext during the run. (The autotest framework would normally orchestrate this; for this course the orchestration is just the MAVProxy script above. The standalone autotest module is out of scope per the assumption-map item 12 — the autotest invocation is a one-line mention here, not its own module.)

**Step B — failsafe injection (~50 min including post-flight log inspection)**:

Same launch, fresh arm. Same arm-takeoff-hover prefix as Step A. **At t = 60 s after `arm throttle`**, in the MAVProxy command terminal:

    param set SIM_GPS_DISABLE 1

The simulator now stops feeding GPS to the autopilot. The EKF's self-confidence drops; after `EKF_CHECK_ITERATIONS_MAX` consecutive bad 10 Hz samples, the failsafe fires.

**Pass criteria** (all required):

1. A `STATUSTEXT` with severity `CRITICAL` and text starting `EKF variance:` appears in the MAVProxy console within 30 s of the injection.
2. The vehicle changes mode to `LAND` or `RTL` (whichever `FS_EKF_ACTION` default is in this commit) within 30 s of the injection.
3. The vehicle ends `Disarming motors` within 240 s of the original `arm throttle`.
4. After the run, inspect the dataflash log (the `mavlogdump.py --types ERR` invocation will be in the lab harness) and find a row with `Subsys = EKFCHECK` and `ECode = BAD_VARIANCE`.

Each student records, on paper or in a text file:

- The MAVProxy statustext at the moment of failure (line 86 in `ekf_check.cpp`, watched live).
- The final mode the vehicle was in when it disarmed.
- The dataflash `ERR` row from line 83 (read out of the log file).

Those three items are the deliverable for this course.

### Day 2 buffer / Q&A (30 min)

For any students whose Step B injection did not fire on the first run; for inspection of edge cases (what if you inject GPS disable while still on the ground? what does the console look like in Step A versus Step B?); for parameter-system review questions left over from Day 1.

**Day 2 totals**: 0.75 + 0.75 + 0.75 + 1.25 = **3.5 h modules** + 0.5 h buffer = **4.0 h**.
Hands-on share: ~0.1 h (2.1) + 0 h (2.2) + ~0.1 h (2.3) + 1.25 h (2.4) ≈ **1.45 h / 3.5 h ≈ 41 %**.

---

## What you have not been taught (deliberate gaps)

If you are continuing on to [course/custom_gnc_course_quadplane.md](custom_gnc_course_quadplane.md) or [course/custom_gnc_course_plane.md](custom_gnc_course_plane.md), you will meet these as new material there:

- **Missions** — `MAV_CMD_NAV_WAYPOINT` and friends, `wp load`, `mode AUTO`. Not covered in this course; the downstream GNC Day 1 starts from zero on this.
- **The autotest framework** — `Tools/autotest/autotest.py`, scripted regression flights. Mentioned only as a one-liner in the closing lab here; the downstream course introduces it on its Day 5.
- **ArduPilot code conventions** — `AP_HAL::millis()`, `is_zero()`, `GCS_SEND_TEXT()`, `snake_case` methods, `AP_`/`AC_`/`AR_` class prefixes. You have *seen* an `AP_GROUPINFO`-style block in Module 1.5 so you recognise the shape, but conventions for *writing* code are out of scope.
- **`AP_<FEATURE>_ENABLED` compile-time flags** — out of scope. The downstream course covers these in its Build System & Code Conventions module.

You have been taught: that the autopilot is one binary running on hardware or in SITL; how to launch SITL and fly a quadrotor through arm / take-off / mode change / land / disarm; the three-bucket mode taxonomy; what a parameter is and how to read or write one; the FAST_TASK / SCHED_TASK shape of the scheduler; the stick-to-ESC data path; what failsafes are and what the EKF failsafe in particular looks like in code, in the MAVProxy console, and in the dataflash log.

That is the on-ramp. Go fly something.

---

Generated from course/plans/plan-intro-arducopter-aero-y1-iter2.md

## Citation drift report

No drift. All cites in the plan resolved verbatim against branch `GNC-0.1`, head `a6fc842e04`, on 2026-04-26 at course-writing time. Specifically re-`grep -n`-verified:

- [ArduCopter/Copter.h:181](../ArduCopter/Copter.h#L181) → `class Copter : public AP_Vehicle {`.
- [ArduCopter/Copter.cpp:113](../ArduCopter/Copter.cpp#L113) → `const AP_Scheduler::Task Copter::scheduler_tasks[] = {`.
- [ArduCopter/Copter.cpp:117](../ArduCopter/Copter.cpp#L117) → `FAST_TASK(run_rate_controller_main),`.
- [ArduCopter/Copter.cpp:126](../ArduCopter/Copter.cpp#L126) → `// run EKF state estimator (expensive)` comment.
- [ArduCopter/Copter.cpp:127](../ArduCopter/Copter.cpp#L127) → `FAST_TASK(read_AHRS),`.
- [ArduCopter/Copter.cpp:201](../ArduCopter/Copter.cpp#L201) → `SCHED_TASK(ekf_check, 10, 75, 84),`.
- [ArduCopter/Copter.cpp:998](../ArduCopter/Copter.cpp#L998) → `AP_HAL_MAIN_CALLBACKS(&copter);`.
- [ArduCopter/ekf_check.cpp:83](../ArduCopter/ekf_check.cpp#L83), [ArduCopter/ekf_check.cpp:86](../ArduCopter/ekf_check.cpp#L86), [ArduCopter/ekf_check.cpp:89](../ArduCopter/ekf_check.cpp#L89) → `LOGGER_WRITE_ERROR(EKFCHECK, BAD_VARIANCE);`, `gcs().send_text(MAV_SEVERITY_CRITICAL, "EKF variance: %s", …);`, `failsafe_ekf_event();`.
- [ArduCopter/mode.cpp:394](../ArduCopter/mode.cpp#L394) → `mode_change_failed(new_flightmode, "requires position");`.
- [ArduCopter/mode.cpp:404](../ArduCopter/mode.cpp#L404) → `mode_change_failed(new_flightmode, "need alt estimate");`.
- [libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:473](../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L473), [libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:476](../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L476), [libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:479](../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L479) → roll/pitch/yaw `update_all` calls.
- [libraries/AP_Motors/AP_MotorsMatrix.cpp:592-602](../libraries/AP_Motors/AP_MotorsMatrix.cpp#L592-L602) → `MOTOR_FRAME_TYPE_X` motor angles `{45, -135, -45, 135}`.
- [Tools/autotest/sim_vehicle.py:287](../Tools/autotest/sim_vehicle.py#L287) → `'ArduCopter.elf',`.
- [Tools/autotest/sim_vehicle.py:1073](../Tools/autotest/sim_vehicle.py#L1073) → `parser.add_option("-v", "--vehicle", …)`.

All other cites in the plan's **Critical Files Cited** master list were spot-checked and matched. No line range was adjusted.

Generated from course/plans/plan-intro-arducopter-aero-y1-iter2.md

