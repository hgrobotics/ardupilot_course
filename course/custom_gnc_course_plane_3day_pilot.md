# GNC Plane 3-Day Pilot — Internals + Adoption Axis

## Custom Training — Senior GNC Pilot Cohort

**Duration**: 21 hours over 3 days (7 h/day teaching + breaks/lunch handled outside the schedule).
**Audience**: 3 senior GNC engineers fluent in C/C++ and embedded flight code on a proprietary in-house autopilot stack. Strong in fixed-wing controls, EKF design, attitude control, energy control, lateral path-following, `gdb`, gtest. Zero ArduPilot exposure.
**Vehicle**: ArduPlane (fixed-wing). No QuadPlane content. No Copter content beyond a one-slide library mapping.
**Format**: in-person; 1:1 instructor time during labs given cohort = 3.
**Depth**: internals — math-as-code, function-body walks, lane-switch arbitration as code, TECS energy split as code, L1 lateral acceleration as code.
**Hardware**: SITL only.

This pilot is a strict subset of the 5-day course at [course/custom_gnc_course_plane.md](custom_gnc_course_plane.md), plus one new dedicated module and one new capstone on **adopting ArduPilot subsystems into a proprietary codebase**. If you want Day 4–5 content (board-porting deep dive, Lua, QuadPlane, soaring, advanced workshop), the 5-day file is the long form.

### Prerequisites (assumed, not taught)

- C and C++ proficiency, comfortable reading large unfamiliar codebases.
- RTOS concepts: cooperative vs pre-emptive scheduling, priority, jitter.
- Fixed-wing GNC: EKF design, attitude controllers, energy controllers (TECS-class), lateral path-following (L1, NLG, pursuit-class).
- `gdb` at the level of breakpoints, attach-by-pid, inspecting frames.
- `gtest` or equivalent unit-test framework.
- Python at the read-and-modify level (the autotest framework is Python).

### What we explicitly do not teach

- Anything in the 5-day source's Day 5 (Module 14 integration project, Module 15 Pegasus, Module 16 advanced workshop) — superseded by the Day 3 capstone in this pilot.
- Lua scripting (5-day Module 13) — mentioned in M1 ecosystem only.
- QuadPlane / VTOL transition state machines — covered in the 5-day source, not in this pilot.
- Real-hardware bring-up — the pilot is SITL only.
- Full mission-planning / GCS UI fluency — the audience already operates a proprietary autopilot.

### Framing this audience needs

You will compare every ArduPilot decision to your own stack. The course casts ArduPilot's choices as **one design among many**, not as the correct answer. We call out trade-offs explicitly:

- The parameter system (`AP_Param` + `AP_GROUPINFO`) is highly flexible and self-documenting, but pays a per-access lookup cost (linear scan over `var_info[]`).
- The singleton pattern (`AP::scheduler()`, `AP::ins()`, etc.) is convenient but creates static-init ordering hazards and makes test isolation harder.
- The cooperative scheduler is fast and predictable, but a 50 ms task overrun is silent — there is no pre-emptive watchdog above the task layer.
- The HAL is the cleanest extraction seam in the codebase, but it is wide (10 UARTs, I²C, SPI, WSPI, GPIO, RCIn/RCOut, Storage, Scheduler, AnalogIn). A minimum viable adoption HAL is a small fraction of the surface, and we walk that minimum in M4 and M10.

Math-as-code, not math-on-slides. The math is in the code; we read the code.

### Per-engineer capstone allocation (assigned, swappable before M11 starts)

- Engineer 1 → `AP_L1_Control` (lateral path-following, smallest extraction surface).
- Engineer 2 → `AP_TECS` (energy controller, richer entanglement).
- Engineer 3 → `AP_NavEKF3` lane-arbitration subset (`checkLaneSwitch` + `switchLane` + `errorScore`, ≤ 200 lines of real algorithm).

---

## Course Structure at a Glance

| Day | Theme                                                                 | Module hours | Buffer | Total |
|-----|-----------------------------------------------------------------------|--------------|--------|-------|
| 1   | Foundations + build + HAL with adoption framing                       | 6.5          | 0.5    | 7.0   |
| 2   | Internals: infrastructure, sensors, AHRS/EKF, control                 | 6.5          | 0.5    | 7.0   |
| 3   | Mission/debug, dedicated adoption module, capstone, feedback          | 6.5          | 0.5    | 7.0   |
|     | **Total**                                                             | **19.5**     | **1.5**| **21.0** |

Buffer is the only slack. Per-day modules sum to exactly 6.5 h.

---

## Day 1 — Foundations + Build + HAL with Adoption Framing (7 h)

**Goal**: by end of Day 1 every engineer has a debug SITL build of ArduPlane on their laptop, has traced a sensor read from `Plane::ahrs_update` down through the HAL to the SITL backend, and has a working mental model of the HAL boundary as the **primary extraction seam** for any ArduPilot subsystem they may want to vendor into their proprietary codebase.

Day 1 hands-on: Lab L1 (~30 min in M4) + ~30 min build code-along in M3 + ~15 min HAL trace exercise in M4 = ~1.25 h direct hands-on, ~1.5 h with editor-side reading time included.

---

### Module M1 — ArduPilot Overview & Ecosystem (1.0 h, lecture+demo, *survey*)

**Why survey**: the audience already builds autopilots. They need ArduPilot's *position in the landscape* and the architecture invariants they will see for the next three days, not a deep tour of MAVLink semantics or community processes.

**Learning objectives**:

1. Place ArduPilot in the open-source autopilot landscape; recognise the GPLv3 licensing posture and the resulting adoption constraints for proprietary use.
2. Recognise the 6-vehicle / shared-libraries / HAL architecture in the directory tree.
3. Locate ArduPlane's main vehicle class and scheduler table; confirm the **50 Hz default fast-loop** for plane vs Copter's 400 Hz default — and *why* (fixed-wing dynamics are slower).
4. Recognise that Lua scripting and DDS/ROS2 exist as integration surfaces; the pilot points at where they live but does not walk them as code (the 5-day source does).

**The architecture in one sentence**: ArduPilot is a multi-vehicle autopilot built as **vehicles + shared libraries + a HAL**. Vehicle directories (`ArduPlane/`, `ArduCopter/`, `Rover/`, …) inherit from `AP_Vehicle`, register a scheduler table, and orchestrate calls into `libraries/`. Shared libraries (~150 of them) carry naming prefixes that matter: `AP_*` are general-purpose, `AC_*` are Copter-flavoured, `AR_*` are Rover-flavoured, `APM_Control` is the plane-specific attitude PID family. The HAL (`libraries/AP_HAL/`) defines the platform-independent interface; concrete implementations live in `AP_HAL_ChibiOS` (STM32 flight hardware), `AP_HAL_Linux`, `AP_HAL_ESP32`, and `AP_HAL_SITL` (the simulator we live in for three days).

**The Plane fast-loop and why it is 50 Hz**: open [ArduPlane/Plane.cpp:62-95](../ArduPlane/Plane.cpp#L62-L95) and read the `scheduler_tasks[]` array. The first four entries are `FAST_TASK(ahrs_update)`, `FAST_TASK(update_control_mode)`, `FAST_TASK(stabilize)`, `FAST_TASK(set_servos)` — these run on every tick of the fast loop. The fast loop's default rate is set by `SCHEDULER_DEFAULT_LOOP_RATE` at [libraries/AP_Scheduler/AP_Scheduler.cpp:43-49](../libraries/AP_Scheduler/AP_Scheduler.cpp#L43-L49), which selects 400 Hz under `APM_BUILD_COPTER_OR_HELI` and **50 Hz** otherwise. Plane gets the 50 Hz default because fixed-wing dynamics are an order of magnitude slower than a multirotor's; the Nyquist budget is comfortable at 50 Hz for attitude and far more comfortable for guidance. The user can override via the `SCHED_LOOP_RATE` parameter declared at [libraries/AP_Scheduler/AP_Scheduler.cpp:55-69](../libraries/AP_Scheduler/AP_Scheduler.cpp#L55-L69) (`@Range: 50 400`, `@RebootRequired: True`).

**Key cites**:
- [ArduPlane/Plane.h:1-50](../ArduPlane/Plane.h#L1-L50) — Plane class header anchor.
- [ArduPlane/Plane.cpp:62-95](../ArduPlane/Plane.cpp#L62-L95) — `scheduler_tasks[]` opening with the FAST_TASK / SCHED_TASK entries.
- [libraries/AP_Scheduler/AP_Scheduler.cpp:43-49](../libraries/AP_Scheduler/AP_Scheduler.cpp#L43-L49) — `SCHEDULER_DEFAULT_LOOP_RATE` 400-vs-50 selector.
- [libraries/AP_Scheduler/AP_Scheduler.cpp:55-69](../libraries/AP_Scheduler/AP_Scheduler.cpp#L55-L69) — `SCHED_LOOP_RATE` parameter.
- [course/custom_gnc_course_plane.md:1280-1295](custom_gnc_course_plane.md#L1280-L1295) — Copter↔Plane library mapping table (printed handout).

**Compare to your stack**: most proprietary stacks have an equivalent of the scheduler table; the question worth thinking about is whether yours is statically declared at compile time (ArduPilot) or built up at runtime (some stacks). ArduPilot's static table is small, fast, and inspectable; it costs you the ability to add a task without recompiling.

**Hands-on**: instructor live-demos `Tools/autotest/sim_vehicle.py -v ArduPlane --console --map` on the projector. Engineers watch only. The first formal lab is L1 in M4.

---

### Module M2 — Operations Essentials, compressed (1.5 h, lecture+demo, *applied*)

**Why applied (not survey)**: you will drive SITL yourselves in every later module. You need *applied* fluency on `sim_vehicle.py`, MAVProxy, and dataflash logs — not the full operator-style mission-planning curriculum.

**Learning objectives**:

1. Launch ArduPlane SITL from a clean clone, attach MAVProxy, take off in `TAKEOFF`, switch to `FBWA`, fly a heading, switch to `RTL`.
2. Read MAVProxy's textual telemetry: altitude, airspeed, mode, heartbeat.
3. Recognise the Plane-specific dataflash messages — `ATT`, `CTUN`, `NTUN`, `ARSP`, `TECS` — and what each carries (recognition only; deep log analysis is in M9).

**The launch sequence**: `Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --map` is the canonical SITL launcher. The script lives at [Tools/autotest/sim_vehicle.py:1](../Tools/autotest/sim_vehicle.py#L1); the argparse is split into named `OptionGroup`s — the build group and sim group at [Tools/autotest/sim_vehicle.py:1073-1240](../Tools/autotest/sim_vehicle.py#L1073-L1240) (covering `--vehicle`/`--frame`/`--debug`/`--gdb`) and the MAVProxy compatibility group at [Tools/autotest/sim_vehicle.py:1405-1436](../Tools/autotest/sim_vehicle.py#L1405-L1436) (covering `--map`/`--console`). The `--debug` flag turns on debug symbols (we will use it in L1); `--gdb` runs the binary under gdb (M9). You do not need MAVProxy expertise — you need the four commands `mode`, `arm throttle`, `takeoff`, `param`.

**TAKEOFF is software, not a hardware mode**: open [ArduPlane/mode_takeoff.cpp:1-80](../ArduPlane/mode_takeoff.cpp#L1-L80). It is a `Mode` subclass with `update()`, `verify_takeoff()`, and configuration parameters. There is no special path through the firmware for takeoff — the mode runs the same control pipeline, parametrised differently. This is worth internalising: every ArduPilot flight mode is a class that overrides `update()` (and a few other hooks) on the `Mode` base. There is no compile-time mode dispatch.

**FBWA in 45 lines**: read [ArduPlane/mode_fbwa.cpp:1-45](../ArduPlane/mode_fbwa.cpp#L1-L45) aloud. `ModeFBWA::update()` clamps stick inputs to attitude limits and writes desired roll and pitch into `nav_roll_cd` and `nav_pitch_cd`; that is the entire mode. The actual stabilisation runs in `Plane::stabilize` (called from the fast-loop scheduler table). Note the unit: `*_cd` is **centi-degrees** — the canonical integer angle unit in ArduPilot vehicle code, signed `int32_t`.

**Key log messages for plane**: `ATT` (attitude — `Roll`, `Pitch`, `Yaw`, `DesRoll`, `DesPitch`, `DesYaw`), `CTUN` (control tuning — throttle output, target altitude vs barometric altitude), `NTUN` (nav tuning — L1 lateral state), `ARSP` (airspeed — raw, calibrated, EAS↔TAS scale), `TECS` (energy controller state — `h`, `hdem`, `dh`, `dhdem`, `spdem`, `sp`). We will lean on `ATT` and `TECS` in Lab L4 and on the EKF-related `XKF*` messages in Lab L3. The full reference list is at [course/custom_gnc_course_plane.md:130-138](custom_gnc_course_plane.md#L130-L138) — used as a printed handout.

**Key cites**:
- [Tools/autotest/sim_vehicle.py:1](../Tools/autotest/sim_vehicle.py#L1)
- [Tools/autotest/sim_vehicle.py:1073-1240](../Tools/autotest/sim_vehicle.py#L1073-L1240) — build + sim argparse groups (`--vehicle`/`--frame`/`--debug`/`--gdb`).
- [Tools/autotest/sim_vehicle.py:1405-1436](../Tools/autotest/sim_vehicle.py#L1405-L1436) — MAVProxy compatibility argparse group (`--map`/`--console`).
- [ArduPlane/mode_takeoff.cpp:1-80](../ArduPlane/mode_takeoff.cpp#L1-L80)
- [ArduPlane/mode_fbwa.cpp:1-45](../ArduPlane/mode_fbwa.cpp#L1-L45)

**Compare to your stack**: most proprietary stacks dispatch flight mode behaviour through a dedicated state machine. ArduPilot pushes the dispatch into virtual methods on the `Mode` base. The trade-off is dynamic-dispatch cost on every fast-loop tick versus the simplicity of "mode = polymorphic object." The cost is bounded — a single vtable indirection — and the readability gain is large.

**Hands-on**: ~10 min code-along — every engineer launches SITL, takes off in `TAKEOFF`, switches to `FBWA`, switches to `RTL`. No formal lab artifact; M4 carries the first formal lab.

---

### Module M3 — Build System & Development Environment (1.0 h, lecture+lab, *applied*)

**Why applied**: you know build systems. You need ArduPilot's *waf* idioms and the SITL+debug-symbols flow, not "what is a build system."

**Learning objectives**:

1. Run `./waf configure --board sitl --debug && ./waf plane`. Locate the artifact at `build/sitl/bin/arduplane`.
2. Recognise `wscript` files as Waf's per-directory build config.
3. Read [Tools/scripts/build_options.py:1-50](../Tools/scripts/build_options.py#L1-L50) and recognise the `AP_<FEATURE>_ENABLED` compile-time-flag pattern — critical for understanding what comes "with" a subsystem at extraction time.
4. Recognise the build targets that matter: `plane`, `bin/arduplane`, `tests/test_<name>`.

**Waf in three lines**: `./waf configure --board sitl --debug` writes `build/sitl/c4che/_cache.py` with the toolchain and feature flags; `./waf plane` builds the plane vehicle target into `build/sitl/bin/arduplane`; `./waf --targets tests/test_math` builds a single gtest binary into `build/sitl/tests/test_math`. The `--debug` flag preserves debug symbols; without it, gdb is much less useful and L1 will be harder than necessary. Never run `waf` with `sudo` (file ownership in `build/` will then bite you on the next non-sudo build).

**`wscript` is small**: read [ArduPlane/wscript:1-40](../ArduPlane/wscript#L1-L40). It declares vehicle-specific build options and the libraries this vehicle pulls in. Each library directory has its own `wscript` describing its sources; the top-level `wscript` orchestrates the lot.

**`AP_<FEATURE>_ENABLED` is how you find out what a subsystem drags in**: feature flags are catalogued in [Tools/scripts/build_options.py:1-50](../Tools/scripts/build_options.py#L1-L50). When you read code and see `#if AP_TERRAIN_AVAILABLE` or `#if HAL_QUADPLANE_ENABLED`, that flag is in `build_options.py`. The hard rule the codebase observes: **a core, non-optional component must never depend on an optional one.** The base build must succeed when optional features are disabled.

**The file you will extract first**: open [libraries/AP_L1_Control/AP_L1_Control.cpp:1-15](../libraries/AP_L1_Control/AP_L1_Control.cpp#L1-L15). Three lines define the contract with the rest of the codebase: `#include <AP_HAL/AP_HAL.h>`, `extern const AP_HAL::HAL& hal;`, and the opening of `var_info[]`. Engineer 1's capstone (M11) starts from exactly this file.

**Key cites**:
- [BUILD.md](../BUILD.md) — the long-form build reference; consult it directly for unfamiliar errors. We do not narrate it here.
- [ArduPlane/wscript:1-40](../ArduPlane/wscript#L1-L40)
- [libraries/AP_L1_Control/AP_L1_Control.cpp:1-15](../libraries/AP_L1_Control/AP_L1_Control.cpp#L1-L15)
- [Tools/scripts/build_options.py:1-50](../Tools/scripts/build_options.py#L1-L50)

**Compare to your stack**: Waf is a Python-based build system, like SCons or Bazel. If your stack uses CMake or Make, the `waf configure → waf <target>` flow maps directly to `cmake -B build && cmake --build build --target <target>`. The `--board` flag is the analogue of CMake's toolchain file.

**Hands-on (≈ 30 min, folded into module budget)**: each engineer runs `./waf configure --board sitl --debug && ./waf plane` on their laptop, and confirms `./build/sitl/bin/arduplane --help` prints usage. This artifact is the input to Lab L1.

---

### Module M4 — HAL Architecture with adoption-seam framing (3.0 h, lecture+code-walk+lab, *internals*)

**Why internals**: HAL is the *primary* extraction seam. Every adoption discussion later in the course returns to this module's framing. Internals depth — function-body walk through one HAL call, board hwdef tour, and the first formal lab.

**Learning objectives**:

1. Explain why HAL exists: same flight code on STM32 (ChibiOS), Linux, SITL, ESP32. Compare to your own platform abstraction.
2. Read `class AP_HAL::HAL`: enumerate the subsystems it owns (UART, I²C, SPI, GPIO, RCInput, RCOutput, Storage, Scheduler, AnalogIn, Flash). Recognise the constructor pattern.
3. Trace one HAL call end-to-end in code: from `Plane::ahrs_update` → `ahrs.update()` → IMU read → SITL backend.
4. Recognise the four canonical HAL access patterns: `extern const AP_HAL::HAL& hal;`, `AP_HAL::millis()`, `AP_HAL::micros()`, `hal.scheduler->delay(...)`. These are the four touchpoints that follow you everywhere when you extract.
5. Read one `hwdef.dat` (CubeBlack) and recognise the directives: `MCU`, `OSCILLATOR_HZ`, `SERIAL_ORDER`, `SPIDEV`, `IMU`, `BARO`, `COMPASS`, `AIRSPEED`. Treated as a 15-min adoption side-bar at the end of the module — enough to recognise board definitions when you encounter them.

**The class in one paragraph**: `AP_HAL::HAL` is a struct of pointers to subsystem driver objects, declared at [libraries/AP_HAL/HAL.h:21-30](../libraries/AP_HAL/HAL.h#L21-L30). The constructor takes one pointer per subsystem — 10 UARTs, an I²C manager, an SPI manager, a WSPI manager, an `AnalogIn`, a `Storage`, a console, a `GPIO`, an `RCInput`, an `RCOutput`, a `Scheduler`, a `Util`, a `Flash`, etc. Read the full constructor signature at [libraries/AP_HAL/HAL.h:35-90](../libraries/AP_HAL/HAL.h#L35-L90). One concrete instance is constructed per build — for SITL it is in [libraries/AP_HAL_SITL/HAL_SITL_Class.cpp:1-80](../libraries/AP_HAL_SITL/HAL_SITL_Class.cpp#L1-L80); for ChibiOS hardware the analogue lives under `libraries/AP_HAL_ChibiOS/`. Every consumer reaches the singleton through `extern const AP_HAL::HAL& hal;`.

**The four free functions**: every adopter will need these and only these from the time-and-scheduling surface. They are declared at [libraries/AP_HAL/system.h:14-21](../libraries/AP_HAL/system.h#L14-L21):

```
uint16_t micros16();
uint32_t micros();
uint32_t millis();
uint16_t millis16();
uint64_t micros64();
uint64_t millis64();
```

`AP_HAL::millis()` returns milliseconds since boot as a 32-bit unsigned integer — wraps every ~49 days. `AP_HAL::micros()` is microseconds since boot, same width — wraps every ~71 minutes. This wrap-time is real and shows up in long-running differences; ArduPilot code consistently uses the subtract-and-let-it-wrap idiom, e.g. `(now - last) * 1.0e-6f`. The 64-bit variants exist for paths that need to compare wall-clock-relative times without wrap concerns.

**Trace target — `Plane::ahrs_update`**: the first FAST_TASK in the scheduler table runs every fast-loop tick. Read it at [ArduPlane/Plane.cpp:165-200](../ArduPlane/Plane.cpp#L165-L200):

```
void Plane::ahrs_update()
{
    arming.update_soft_armed();

    ahrs.update();

#if HAL_LOGGING_ENABLED
    if (should_log(MASK_LOG_IMU)) {
        AP::ins().Write_IMU();
    }
#endif

    // calculate a scaled roll limit based on current pitch
    roll_limit_cd = aparm.roll_limit*100;
    pitch_limit_min = aparm.pitch_limit_min;
    ...
}
```

`ahrs.update()` is the single line that drives the full estimator stack on each tick. From there we drop into `AP_AHRS::update`, then into the active EKF backend (`NavEKF3` by default for plane), then into the IMU read in `AP_InertialSensor`, then into the platform-specific IMU driver. On SITL, the IMU driver receives synthetic data from the physics model in `libraries/SITL/`; on hardware, it reads the I²C/SPI sensor directly.

**The umbrella include**: every consumer of HAL writes `#include <AP_HAL/AP_HAL.h>` — that single header (declared at [libraries/AP_HAL/AP_HAL.h:1-31](../libraries/AP_HAL/AP_HAL.h#L1-L31)) pulls in the full HAL surface plus the `extern const AP_HAL::HAL& hal;` declaration.

**Board hwdef tour (≈ 15 min)**: read [libraries/AP_HAL_ChibiOS/hwdef/CubeBlack/hwdef.dat:1-100](../libraries/AP_HAL_ChibiOS/hwdef/CubeBlack/hwdef.dat#L1-L100). The directives `MCU`, `OSCILLATOR_HZ`, `SERIAL_ORDER`, `SPIDEV`, `IMU`, `BARO`, `COMPASS`, `AIRSPEED` describe the board to the ChibiOS HAL build. A new board is, to first approximation, a new `hwdef.dat`. Treated as an adoption side-bar here because your stack's primary interest is extracting algorithms into your own HAL rather than maintaining ArduPilot as the host runtime.

**Key cites**:
- [libraries/AP_HAL/HAL.h:21-30](../libraries/AP_HAL/HAL.h#L21-L30) — class opening.
- [libraries/AP_HAL/HAL.h:35-90](../libraries/AP_HAL/HAL.h#L35-L90) — constructor signature.
- [libraries/AP_HAL/system.h:14-21](../libraries/AP_HAL/system.h#L14-L21) — free time functions.
- [libraries/AP_HAL/AP_HAL.h:1-31](../libraries/AP_HAL/AP_HAL.h#L1-L31) — umbrella include.
- [ArduPlane/Plane.cpp:165-200](../ArduPlane/Plane.cpp#L165-L200) — `Plane::ahrs_update` body.
- [libraries/AP_HAL_SITL/HAL_SITL_Class.cpp:1-80](../libraries/AP_HAL_SITL/HAL_SITL_Class.cpp#L1-L80) — SITL HAL instantiation.
- [libraries/AP_HAL_ChibiOS/hwdef/CubeBlack/hwdef.dat:1-100](../libraries/AP_HAL_ChibiOS/hwdef/CubeBlack/hwdef.dat#L1-L100) — example board hwdef.

**Compare to your stack**: the HAL boundary is the most common abstraction in flight software. The interesting comparison is *width*: ArduPilot's HAL is wide (≈ 20 subsystems). Wide HALs make porting a board easier (the contract is exhaustive) but make a *minimum-viable* extraction harder (you have to know which subsystems your target subsystem actually touches). In M10 we walk a minimum-viable mock HAL for `AP_L1_Control` — it needs only `AP_HAL::micros()` plus a degenerate scheduler.

#### Adoption side-bar — what comes with `AP_HAL`

- **What this subsystem buys you in your codebase**: a clean, idiomatic abstraction over time, scheduler delay, UART, storage, and bus drivers. If you adopt it whole, you are committing to ArduPilot's view of platform abstraction.
- **What comes with it**: the full `AP_HAL::HAL` constructor surface (≈ 20 subsystems), `extern const AP_HAL::HAL& hal;` reaching everywhere, and the `AP_HAL::millis()`/`micros()` free functions. Adopting it whole is rare — the audience already has a HAL.
- **The realistic adoption pattern**: provide a stub `AP_HAL::HAL` against your platform's native APIs. Minimum viable surface for an algorithm-only extraction is `AP_HAL::millis()` + `AP_HAL::micros()` + a single `Scheduler::delay()`. M10 walks the worked example.
- **Cost to keep vs replace**: keeping ArduPilot's HAL means owning a wide compatibility surface forever. Replacing it (writing a thin shim) means owning a narrow one — but you must update it any time your extracted algorithm starts touching a new HAL function.

#### Lab L1 — HAL + scheduler probe (~30 min, embedded in M4)

Detailed runnable version: `course/labs/gnc-plane-3day-pilot-l1/`.

- **Setup**: pre-built debug SITL binary at `build/sitl/bin/arduplane` from M3.
- **SITL invocation**: `Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --map --debug --no-mavproxy`.
- **Procedure**: launch SITL; in a second terminal `gdb -p $(pgrep arduplane)`; `b Plane::ahrs_update`; `c`; on hit, `print AP_HAL::millis()` and `print AP::scheduler().get_loop_rate_hz()`; `detach`; `quit`.
- **Expected fingerprint**: a `millis()` value > 0 and a loop-rate of `50` (the plane default per [libraries/AP_Scheduler/AP_Scheduler.cpp:46](../libraries/AP_Scheduler/AP_Scheduler.cpp#L46)).
- **Pass criterion**: both prints succeed and the engineer can describe the call from `ahrs_update` down through `ahrs.update()`.

---

## Day 2 — Internals: Infrastructure, Sensors, AHRS/EKF, Control (7 h)

**Goal**: by end of Day 2 every engineer has read `AP_Param`, `NavEKF3::checkLaneSwitch`, `AP_TECS::update_pitch_throttle`, `AP_L1_Control::update_waypoint`, and `AP_RollController::get_servo_out` as code, and has run three labs that probe each subsystem with a deliberate fault or modification.

Day 2 hands-on: L2 (~30 min) + L3 (~40 min) + L4 (~40 min) = 1.83 h of 6.5 h = 28% — comfortably above the 25% rubric floor.

---

### Module M5 — Core Infrastructure Libraries with `AP_Param` adoption emphasis (2.0 h, lecture+code-walk+lab, *internals*)

**Why internals**: `AP_Param`, `AP_Scheduler`, `AP_Logger` are the three libraries that "come with" everything else when you extract. Read at code level, not survey level.

**Learning objectives**:

1. Read `AP_Scheduler::Task` and `Plane::scheduler_tasks[]`. Recognise the `FAST_TASK` vs `SCHED_TASK(rate_hz, max_time_us, priority)` distinction.
2. Read the `AP_GROUPINFO` macro family: how a `var_info[]` table maps to EEPROM-stored parameters with full `@Param`/`@DisplayName`/`@Description`/`@Range`/`@User` annotations. Recognise that **parameter indices are baked into stored configs** — once an index is in the wild, you may never renumber it.
3. Read `AP_Logger`'s `WriteV` / `Write` API and recognise the `LogStructure` registration pattern.
4. Read `AP_Vehicle` base class and how `Plane : public AP_Vehicle` consumes the scheduler/parameter/logger framework.

**The scheduler table**: revisit [ArduPlane/Plane.cpp:62-95](../ArduPlane/Plane.cpp#L62-L95). Two macros build entries: `FAST_TASK(func)` defined at [ArduPlane/Plane.cpp:30-60](../ArduPlane/Plane.cpp#L30-L60) for tasks that run on every fast-loop tick, and `SCHED_TASK(func, rate_hz, max_time_us, priority)` for rate-limited tasks. The fields `rate_hz` and `max_time_us` are advisory: the cooperative scheduler will skip a task on a given tick if the budget is tight, and the `max_time_us` is what the scheduler uses to decide. There is no pre-emption — a task that overruns silently steals time from the next tick. This is one of the key trade-offs versus a pre-emptive RTOS: simple, predictable, and unforgiving.

The accessors you will use in L1 and elsewhere are at [libraries/AP_Scheduler/AP_Scheduler.h:140-180](../libraries/AP_Scheduler/AP_Scheduler.h#L140-L180): `get_loop_rate_hz()`, `get_loop_period_us()`, `get_loop_period_s()`. They read the cached value computed at scheduler init from `SCHED_LOOP_RATE`.

**The parameter system — `AP_GROUPINFO` family**: open [libraries/AP_Param/AP_Param.h:140-160](../libraries/AP_Param/AP_Param.h#L140-L160). The macros `AP_GROUPINFO`, `AP_GROUPINFO_FLAGS`, `AP_GROUPINFO_FRAME`, `AP_GROUPINFO_FLAGS_DEFAULT_POINTER` all expand into a `GroupInfo` struct entry that carries: short name (≤ 16 chars), index, class+member offset, default value, type. The full `@Param` documentation block is parsed by an offline tool to produce the parameter manifests that GCSes consume. The base macro is one line:

```
#define AP_GROUPINFO(name, idx, clazz, element, def) \
    AP_GROUPINFO_FLAGS(name, idx, clazz, element, def, 0)
```

A real concrete example, not synthesised — `AIRSPEED_MIN` and `AIRSPEED_MAX` from ArduPlane at [ArduPlane/Parameters.cpp:288-310](../ArduPlane/Parameters.cpp#L288-L310):

```
// @Param: AIRSPEED_MIN
// @DisplayName: Minimum Airspeed
...
ASCALAR(airspeed_min, "AIRSPEED_MIN",  AIRSPEED_FBW_MIN),

// @Param: AIRSPEED_MAX
// @DisplayName: Maximum Airspeed
...
ASCALAR(airspeed_max, "AIRSPEED_MAX",  AIRSPEED_FBW_MAX),
```

The hard rule: **never renumber `AP_GROUPINFO` indices**. The index is baked into stored user configs in EEPROM/SD. Renumbering an existing index silently corrupts user parameter sets across firmware upgrade. Only append new entries at unused indices.

**The setup → load_all → save lifecycle**: `AP_Param::setup()` at [libraries/AP_Param/AP_Param.cpp:355-400](../libraries/AP_Param/AP_Param.cpp#L355-L400) walks the registered top-level table and prepares the in-memory parameter graph. `AP_Param::load_all()` at [libraries/AP_Param/AP_Param.cpp:1555-1620](../libraries/AP_Param/AP_Param.cpp#L1555-L1620) reads stored values out of the EEPROM/Storage backend at boot. Saves are deferred and batched. Every set operation goes through `AP_Param::save_sync` (in the same file, lower in the body); from outside the library you reach it transparently through `param_object.set_and_save(...)`.

**Logger**: `AP_Logger.h` at [libraries/AP_Logger/AP_Logger.h:1-80](../libraries/AP_Logger/AP_Logger.h#L1-L80) declares the public surface. Logging is structured: each message type is registered via a `LogStructure` typedef and given a fixed binary layout. The vehicle code calls `logger.WriteV("ATT", ...)` and the binary message lands in the dataflash. M9 has the recognition-level tour of the log layout.

**Key cites**:
- [ArduPlane/Plane.cpp:30-60](../ArduPlane/Plane.cpp#L30-L60) — `SCHED_TASK`/`FAST_TASK` macros.
- [ArduPlane/Plane.cpp:62-95](../ArduPlane/Plane.cpp#L62-L95) — scheduler table.
- [libraries/AP_Param/AP_Param.h:140-160](../libraries/AP_Param/AP_Param.h#L140-L160) — `AP_GROUPINFO` family.
- [libraries/AP_Param/AP_Param.cpp:355-400](../libraries/AP_Param/AP_Param.cpp#L355-L400) — `AP_Param::setup`.
- [libraries/AP_Param/AP_Param.cpp:1555-1620](../libraries/AP_Param/AP_Param.cpp#L1555-L1620) — `AP_Param::load_all`.
- [ArduPlane/Parameters.cpp:288-310](../ArduPlane/Parameters.cpp#L288-L310) — real `@Param` block.
- [libraries/AP_Scheduler/AP_Scheduler.h:140-180](../libraries/AP_Scheduler/AP_Scheduler.h#L140-L180) — loop-rate accessors.
- [libraries/AP_Logger/AP_Logger.h:1-80](../libraries/AP_Logger/AP_Logger.h#L1-L80) — logger interface.

**Compare to your stack**: most proprietary parameter systems use either a hand-maintained struct or a code-generated table from a schema. ArduPilot uses runtime macro expansion into a compile-time-built table. The trade-off: `AP_Param` access is `O(N)` over the table because lookup is a linear scan, but it scales to thousands of parameters because N stays modest (a few hundred per vehicle). The self-documenting `@Param` annotation is the real win — the parameter manifest the GCS consumes is generated from these comments by an offline tool.

#### Adoption side-bar — what comes with `AP_Param`

- **What this subsystem buys you in your codebase**: a self-documenting, GCS-discoverable, EEPROM-backed parameter system with bounded memory, range checking, and free `@Param` documentation pipelines.
- **What comes with it**: the `AP_Param.h` header (the `var_info[]` macros), an EEPROM-equivalent `Storage` backend (≥ 16 KB), and the call sites for `setup()` and `load_all()`. You do **not** need `AP_Logger` or `GCS_MAVLink` to use `AP_Param` standalone.
- **What it costs to keep vs replace**: keeping `AP_Param` is the single best adoption ROI in the library set — it is well-bounded and the `@Param` annotation pipeline is genuinely useful. The cost is the per-access linear-scan lookup (mitigable by caching pointers) and the rule that you can never renumber an index.

#### Lab L2 — Add a custom `AP_Float` parameter to ArduPlane (~30 min)

Detailed runnable version: `course/labs/gnc-plane-3day-pilot-l2/`.

- **Build**: modify `ArduPlane/Parameters.h` and `ArduPlane/Parameters.cpp` to add `MY_PARAM` as `AP_Float`, default 17.0; rebuild with `./waf plane`.
- **SITL invocation**: `Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console`.
- **Procedure**: in MAVProxy, `param show MY_*` (expect `MY_PARAM 17.0`); `param set MY_PARAM 42.0`; quit SITL; relaunch; `param show MY_*` again.
- **Expected fingerprint**: post-restart `MY_PARAM 42.0`.
- **Pass criterion**: parameter persists across restart. Validates the `AP_Param` walk.

---

### Module M6 — Sensor Drivers, Frontend/Backend, Airspeed (1.5 h, lecture+code-walk, *internals*)

**Why internals**: airspeed is the plane-critical sensor and the frontend/backend pattern is the *most reusable* design in ArduPilot. Read at code level.

**Learning objectives**:

1. Read the frontend/backend pattern: `AP_Airspeed` (frontend) → `AP_Airspeed_MS4525`, `AP_Airspeed_SITL` (backends) — the same shape as `AP_Baro`, `AP_GPS`, `AP_InertialSensor`.
2. Read `AP_Airspeed::get_airspeed()` and the EAS↔TAS conversion.
3. Recognise where airspeed feeds: TECS (energy controller), EKF3 (wind estimation), L1 (only indirectly, via EKF position/velocity).

**The frontend/backend shape**: open [libraries/AP_Airspeed/AP_Airspeed.h:1-80](../libraries/AP_Airspeed/AP_Airspeed.h#L1-L80). The frontend exposes `get_airspeed()`, `get_airspeed_ratio()`, `healthy()`, `use()`, and a few status accessors. Backends inherit from `AP_Airspeed_Backend` ([libraries/AP_Airspeed/AP_Airspeed_Backend.h:1-80](../libraries/AP_Airspeed/AP_Airspeed_Backend.h#L1-L80)) and implement `init()` and `get_differential_pressure()`. The frontend selects a backend per-instance from a `TYPE` parameter and owns the EAS↔TAS conversion, calibration, and outlier-rejection logic.

The SITL backend at [libraries/AP_Airspeed/AP_Airspeed_SITL.cpp:1-80](../libraries/AP_Airspeed/AP_Airspeed_SITL.cpp#L1-L80) is the canonical reference for any new backend you might write — minimal, no platform dependencies. The MS4525DO I²C backend at [libraries/AP_Airspeed/AP_Airspeed_MS4525.cpp:1-100](../libraries/AP_Airspeed/AP_Airspeed_MS4525.cpp#L1-L100) is the reference for a real I²C device.

**Auto-calibration against GPS groundspeed**: read [libraries/AP_Airspeed/Airspeed_Calibration.cpp:1-80](../libraries/AP_Airspeed/Airspeed_Calibration.cpp#L1-L80). The basic idea: with no wind, airspeed equals groundspeed, so a regression of indicated airspeed against GPS groundspeed (gated on adequate variability) refines the airspeed sensor's calibration ratio. ArduPilot runs this online and writes it back to the `ARSPD_RATIO` parameter.

**Where airspeed lands downstream**: TECS uses it for the speed half of the energy balance (M8). EKF3 uses it as a wind-estimation observation when both airspeed sensors and at least one of the other position sources are valid. L1 does **not** consume airspeed directly — it consumes ground speed and bearing through AHRS. This independence is part of why L1 is the cleanest extraction (Engineer 1's capstone).

**Key cites**:
- [libraries/AP_Airspeed/AP_Airspeed.h:1-80](../libraries/AP_Airspeed/AP_Airspeed.h#L1-L80)
- [libraries/AP_Airspeed/AP_Airspeed_Backend.h:1-80](../libraries/AP_Airspeed/AP_Airspeed_Backend.h#L1-L80)
- [libraries/AP_Airspeed/AP_Airspeed_SITL.cpp:1-80](../libraries/AP_Airspeed/AP_Airspeed_SITL.cpp#L1-L80)
- [libraries/AP_Airspeed/AP_Airspeed_MS4525.cpp:1-100](../libraries/AP_Airspeed/AP_Airspeed_MS4525.cpp#L1-L100)
- [libraries/AP_Airspeed/Airspeed_Calibration.cpp:1-80](../libraries/AP_Airspeed/Airspeed_Calibration.cpp#L1-L80)

**Compare to your stack**: the frontend/backend split is the single most portable design idea in ArduPilot. Your proprietary stack almost certainly has it under different names. The interesting question is whether the frontend owns the calibration and conversion (ArduPilot) or the backend does (some stacks). ArduPilot's choice keeps backends small and replaceable — which is exactly what you want when porting a sensor.

#### Adoption side-bar — what comes with `AP_Airspeed`

- **What this subsystem buys you in your codebase**: a frontend/backend split with seven backends, online auto-calibration against GPS, EAS↔TAS conversion, and outlier rejection — all gated by the parameter system.
- **What comes with it**: the frontend, one backend (most likely `AP_Airspeed_SITL` for testing plus your platform's native I²C driver), `AP_HAL::I2CDevice`, the `var_info[]` table, and a small set of math helpers.
- **What it costs to keep vs replace**: lifting `AP_Airspeed` whole pulls in `AP_Param` (already adopted in M5), `AP_Logger` (optional — the auto-calibration writes to log), and a `GCS_SEND_TEXT` for status reports. The `GCS_SEND_TEXT` calls are easy to stub. The frontend itself is small and worth keeping.

**Hands-on**: ~10 min in-module code-along — `grep airspeed_ratio` and trace one consumer in `AP_TECS`. No formal lab; M7 and M8 carry the labs.

---

### Module M7 — AHRS + EKF Internals (2.0 h, lecture+code-walk+lab, *internals*)

**Why internals**: this is where the audience leans in hardest. You have built EKFs. You want to see ArduPilot's specific design choices: lane-switch arbitration, error-score formula, wind-state inclusion, GPS source-set selection.

**Learning objectives**:

1. Read `AP_AHRS` as an interface; recognise that vehicle code never calls EKF directly.
2. Read `NavEKF3::UpdateFilter` — the periodic lane-arbitration loop. Recognise `runCoreSelection`, the 10-second debounce, the `coreBetterScore` test, the `BETTER_THRESH` constant.
3. Read `NavEKF3::checkLaneSwitch` — the explicit "EKF failsafe is about to trigger; can a lane swap save us?" entry point called from vehicle code.
4. Read `NavEKF3_core::errorScore` — the consolidated error metric: max of GPS fusion test ratio, altimeter test ratio, airspeed test ratio (gated by 2-airspeed-sensor presence), magnetometer test ratio.
5. Read `NavEKF3::switchLane` — the actual switch with yaw/pos reset propagation and `EKF3 lane switch %u` GCS warning.

**AHRS hides which estimator is running**: the Plane vehicle never calls `NavEKF3` directly. It calls `ahrs.update()`, `ahrs.get_location()`, `ahrs.groundspeed_vector()`, `ahrs.get_yaw()`. The AHRS frontend at [libraries/AP_AHRS/AP_AHRS.h:1-80](../libraries/AP_AHRS/AP_AHRS.h#L1-L80) declares the interface; the active backend (EKF2, EKF3, External, DCM-only fallback) is selected at runtime. This indirection is what lets `AP_L1_Control` survive an estimator change.

**The lane-arbitration loop — `NavEKF3::UpdateFilter`**: open [libraries/AP_NavEKF3/AP_NavEKF3.cpp:910-1020](../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L910-L1020). The structure is:

1. Run all configured cores' state-and-covariance update.
2. For each core, accumulate an `errorScore` (the consolidated test-ratio metric).
3. Periodically (debounced to 10 s) compare cores. If a non-primary core's `errorScore` is below the primary's by `BETTER_THRESH`, switch the primary lane.
4. On switch, propagate yaw and position resets so downstream consumers see a continuous state.

The key call inside is `switchLane(newPrimaryIndex)` at line 1001 inside the periodic check. This is one of two paths that can trigger a lane switch.

**The explicit failsafe path — `NavEKF3::checkLaneSwitch`**: at [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1029-1062](../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1029-L1062), this function is called from vehicle code when the EKF failsafe is about to trigger ("we are seconds from declaring no estimate"). It runs an immediate (debounce-bypass) lane comparison and switches if any non-primary core has a lower `errorScore` and is below the absolute health gate. This is the path that saves the aircraft when GPS glitches inject a bad innovation into the primary lane.

**The actual switch — `NavEKF3::switchLane`**: at [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1064-1078](../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1064-L1078). Stores the new primary index, requests a yaw reset and a position reset to be propagated through AHRS so that `ahrs.get_location()` returns a continuous value rather than jumping by the inter-lane bias, and emits the `GCS_SEND_TEXT` `EKF3 lane switch %u`. The yaw and position reset propagation is the subtle part — without it, an L1 controller would see a step in cross-track error and command a sharp roll.

**The error metric — `NavEKF3_core::errorScore`**: at [libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp:62-86](../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L86). Read it as code:

```
float NavEKF3_core::errorScore() const
{
    float score = 0.0f;
    if (tiltAlignComplete && yawAlignComplete) {
        // Check GPS fusion performance
        score = MAX(score, 0.5f * (velTestRatio + posTestRatio));
        // Check altimeter fusion performance
        score = MAX(score, hgtTestRatio);
        if (assume_zero_sideslip()) {
            const auto *arsp = dal.airspeed();
            if (arsp != nullptr && arsp->get_num_sensors() >= 2 && (frontend->_affinity & EKF_AFFINITY_ARSP)) {
                score = MAX(score, 0.3f * tasTestRatio);
            }
        }
        if (frontend->_affinity & EKF_AFFINITY_MAG) {
            score = MAX(score, 0.3f * (magTestRatio.x + magTestRatio.y + magTestRatio.z));
        }
    }
    return score;
}
```

The score starts at zero and is gated overall by `tiltAlignComplete && yawAlignComplete` — pre-alignment, the score stays at zero and the lane is not eligible for arbitration. Inside the gate, the score is `MAX`-folded over four observation channels:

- **GPS** — `0.5f * (velTestRatio + posTestRatio)`. Average of the velocity and horizontal-position innovation test ratios. Always evaluated.
- **Altimeter** — `hgtTestRatio`. The barometric height innovation test ratio, applied at unit weight.
- **Airspeed** — `0.3f * tasTestRatio`, but only when (a) `assume_zero_sideslip()` is true (a fixed-wing forward-flight regime), (b) `dal.airspeed()` reports `>= 2` airspeed sensors, and (c) the EKF affinity flag `EKF_AFFINITY_ARSP` is set. The 0.3 scale factor and the multi-sensor gate are documented in the source comment as a deliberate sensitivity reduction: the EKF must be less reactive to airspeed innovations driven by gusts than to GPS innovations, because gust-driven innovations would otherwise force false lane switches in cruise.
- **Magnetometer** — `0.3f * (magTestRatio.x + magTestRatio.y + magTestRatio.z)`, but only when the affinity flag `EKF_AFFINITY_MAG` is set. Same 0.3 sensitivity factor as airspeed; the affinity gate exists because the magnetometer has its own independent switching mechanism that the affinity flag overrides.

Each test ratio is the squared-Mahalanobis innovation normalised by the gate; ≤ 1 means the innovation passed the gate. A consolidated score above ≈ 1 means at least one observation is rejecting consistently — the lane is unhealthy and is a candidate to be deselected by `checkLaneSwitch`.

A two-minute aside worth taking: `EKF_AFFINITY_*` flags are a per-observation-type opt-in, configured by the `EK3_AFFINITY` parameter. They control which observations participate in the lane-switch arbitration metric. The default (`EK3_AFFINITY = 0`) disables both airspeed and magnetometer terms — the consolidated score then collapses to `MAX(0.5f * (velTestRatio + posTestRatio), hgtTestRatio)`. For a fixed-wing platform with redundant airspeed and magnetometers, enabling `EKF_AFFINITY_ARSP` and `EKF_AFFINITY_MAG` bits on `EK3_AFFINITY` is what brings airspeed and mag into the arbitration. This is exactly the kind of detail Engineer 3's capstone has to confront when reimplementing the metric against a different sensor stack.

The declaration is at [libraries/AP_NavEKF3/AP_NavEKF3_core.h:140-160](../libraries/AP_NavEKF3/AP_NavEKF3_core.h#L140-L160), and the per-tick aggregation `NavEKF3::updateCoreErrorScores` is at [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1092-1099](../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1092-L1099).

**Which core is primary at boot**: parameter `EK3_PRIMARY` at [libraries/AP_NavEKF3/AP_NavEKF3.cpp:715-722](../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L715-L722) selects the initial primary; arbitration takes over thereafter.

**Wind estimation**: airspeed-fused wind state is part of the EKF3 core's state vector when both an airspeed sensor and an alternative position source are valid. The fusion code lives in `AP_NavEKF3_PosVelFusion.cpp` (the file is large; we walk the structure in narrative rather than line-cite).

**Key cites**:
- [libraries/AP_AHRS/AP_AHRS.h:1-80](../libraries/AP_AHRS/AP_AHRS.h#L1-L80) — frontend.
- [libraries/AP_NavEKF3/AP_NavEKF3.cpp:910-1020](../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L910-L1020) — `UpdateFilter` arbitration loop.
- [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1029-1062](../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1029-L1062) — `checkLaneSwitch`.
- [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1064-1078](../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1064-L1078) — `switchLane`.
- [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1092-1099](../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1092-L1099) — `updateCoreErrorScores`.
- [libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp:62-86](../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L86) — `errorScore` body (function ends at line 86).
- [libraries/AP_NavEKF3/AP_NavEKF3_core.h:140-160](../libraries/AP_NavEKF3/AP_NavEKF3_core.h#L140-L160) — `errorScore` declaration.
- [libraries/AP_NavEKF3/AP_NavEKF3.cpp:715-722](../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L715-L722) — `EK3_PRIMARY`.

**Compare to your stack**: lane arbitration is the cross-cutting concern that varies most across proprietary EKFs. ArduPilot's choice — a single scalar consolidated `errorScore`, max-of-test-ratios, with a 10-second debounce on the periodic path and a debounce-bypass on the failsafe path — is one of several reasonable designs. The alternative your stack may use (per-axis health, vector-valued comparison, hysteresis on a different time constant) is comparable; the question is whether you can defend the choice in flight-test logs.

#### Adoption side-bar — what comes with `AP_NavEKF3`

- **What this subsystem buys you in your codebase**: a multi-lane 24-state EKF with magnetometer-yaw alignment, wind-state, airspeed fusion, optical flow, range finder, GPS-pos and GPS-vel fusion, and a defensible lane-arbitration policy.
- **What comes with it**: a *broad* dependency graph — the Data Access Layer (DAL), `AP_AHRS`, multiple sensor frontends, `AP_Logger`, `AP_Param`, `GCS_SEND_TEXT`, `AP_Math`. `AP_NavEKF3_core.cpp` alone is several thousand lines.
- **What it costs to keep vs replace**: adopting *full* `AP_NavEKF3` is a large undertaking — multi-quarter effort to integrate against a proprietary sensor stack. The realistic adoption pattern is to lift only the **lane-arbitration logic** (≤ 200 lines: `checkLaneSwitch`, `switchLane`, `updateCoreErrorScores`, `errorScore`) and apply it to multiple instances of *your own* EKF. That is exactly Engineer 3's capstone in M11.

#### Lab L3 — GPS noise + EKF lane switch (~40 min)

Detailed runnable version: `course/labs/gnc-plane-3day-pilot-l3/`.

- **SITL invocation**: `Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --map -L KSFO`.
- **Parameter set**: stock plane PLUS `EK3_IMU_MASK 3` (force two EKF lanes), `LOG_BITMASK 65535` (enable XKF logging).
- **Procedure**: take off in TAKEOFF, switch to FBWA, fly steady. In MAVProxy: `param set SIM_GPS_NOISE 5` (gentle noise — see the parameter at [libraries/SITL/SIM_GPS.cpp:97-103](../libraries/SITL/SIM_GPS.cpp#L97-L103)); ~30 s later `param set SIM_GPS_GLTCH_X 50` (the glitch parameter is `SIM_GPS_GLTCH` per [libraries/SITL/SIM_GPS.cpp:69-75](../libraries/SITL/SIM_GPS.cpp#L69-L75)). Wait for GCS statustext `EKF3 lane switch %u`. Disarm; download dataflash; `mavlogdump.py --types=XKF1,XKF4,EV` and identify the lane-switch event.
- **Pass criterion**: lane-switch GCS message appears within 30 s of glitch injection AND the dataflash records the switch event.

---

### Module M8 — Control Pipeline: TECS, L1, APM_Control, SRV_Channels (1.0 h, lecture+code-walk+lab, *internals*)

**Why internals**: you build control laws. You want TECS's energy split, L1's lateral-acceleration command, and the airspeed-scaled PID structure as code, with the actual scaling formulae.

**Why 1.0 h** (versus the 1.5 h slot in the requirements skeleton): the audience already knows PID + nav guidance. The unique-to-ArduPilot content (TECS energy formula, L1 lateral acceleration, airspeed-scaled PID, `SRV_Channels::push`) fits in 1.0 h at internals depth with Lab L4 inside.

**Learning objectives**:

1. Read `AP_TECS::update_pitch_throttle` (the main entry point). Recognise the energy-balance computation and the speed/height priority knob (`TECS_SPDWEIGHT`).
2. Read `AP_L1_Control::update_waypoint` and the lateral-acceleration formula. Recognise `_L1_dist = MAX(0.3183099f * _L1_damping * _L1_period * groundSpeed, dist_min)` (`0.3183099 = 1/π`).
3. Read `AP_RollController::get_servo_out`: angle-error → desired-rate → PID, with airspeed scaling via the `scaler` parameter.
4. Read `SRV_Channels::push` and the cork/push pattern for atomic servo updates.

**TECS — energy split as code**: open [libraries/AP_TECS/AP_TECS.cpp:1270-1350](../libraries/AP_TECS/AP_TECS.cpp#L1270-L1350) for the entry point `update_pitch_throttle(int32_t hgt_dem_cm, ...)`. Inside, it computes a per-tick `_DT`, calls `_update_energies()` at [libraries/AP_TECS/AP_TECS.cpp:678-700](../libraries/AP_TECS/AP_TECS.cpp#L678-L700), then dispatches to `_update_throttle_with_airspeed()` at [libraries/AP_TECS/AP_TECS.cpp:719-820](../libraries/AP_TECS/AP_TECS.cpp#L719-L820) (or the without-airspeed variant). The energy formula is the canonical TECS split: total specific energy `STE = h + V²/(2g)` and balance `SEB = h - V²/(2g)`, with throttle commanded against `STE` and pitch commanded against a weighted blend of `STE` and `SEB`. The blend weight is `TECS_SPDWEIGHT` ([libraries/AP_TECS/AP_TECS.cpp:99](../libraries/AP_TECS/AP_TECS.cpp#L99), default `1.0`, range 0–2): 1 is the canonical 50/50 split, 0 ignores speed error and prioritises altitude (good for a glider final), 2 ignores altitude and prioritises speed (rare).

The pitch damping gain `TECS_PTCH_DAMP` at [libraries/AP_TECS/AP_TECS.cpp:107](../libraries/AP_TECS/AP_TECS.cpp#L107) (default 0.3) is what we will perturb in Lab L4 to surface visible altitude-tracking oscillation.

**L1 — lateral acceleration as code**: open [libraries/AP_L1_Control/AP_L1_Control.cpp:206-347](../libraries/AP_L1_Control/AP_L1_Control.cpp#L206-L347). The function `update_waypoint(prev_WP, next_WP, dist_min)` computes the L1 reference vector and outputs `_latAccDem` (lateral acceleration demand) plus `_nav_bearing` and `_bearing_error`. The damping factor is `0.3183099 = 1/π`, applied to the L1 distance as `_L1_dist = MAX(1/π · damping · period · groundSpeed, dist_min)`; the `update_waypoint` body computes the line-of-sight angle Nu from velocity and reference vectors and converts to lateral acceleration.

The four parameters that govern L1 are at [libraries/AP_L1_Control/AP_L1_Control.cpp:7-44](../libraries/AP_L1_Control/AP_L1_Control.cpp#L7-L44): `NAVL1_PERIOD` (default 17 s — the dominant tuning knob), `NAVL1_DAMPING` (default 0.75), `NAVL1_XTRACK_I` (default 0.02), `NAVL1_LIM_BANK` (default 0, meaning no extra bank limit beyond global aircraft limits).

**Roll controller — airspeed-scaled PID**: open [libraries/APM_Control/AP_RollController.cpp:185-227](../libraries/APM_Control/AP_RollController.cpp#L185-L227) for `get_servo_out`. The structure is: angle error (centi-degrees) → desired rate (deg/s) via a time-constant `tau` (the `RLL2SRV_TCONST` parameter at [libraries/APM_Control/AP_RollController.cpp:35](../libraries/APM_Control/AP_RollController.cpp#L35), default 0.5 s) → rate-PID call with the `scaler` argument multiplying both proportional and feed-forward terms. The `scaler` is `(reference_airspeed / current_airspeed)²`, computed by the caller — it makes the controller behave consistently across the airspeed envelope without re-tuning.

`RLL2SRV_TCONST` is the parameter we will halve in Lab L4 to surface a faster-but-oscillatory roll response. The underlying rate-PID parameters (`RLL_RATE_P`, `RLL_RATE_I`, `RLL_RATE_D`, `RLL_RATE_FF`) are declared in the rate-PID block immediately after, commented at [libraries/APM_Control/AP_RollController.cpp:51-100](../libraries/APM_Control/AP_RollController.cpp#L51-L100); they are a separate PID with its own indices.

**SRV_Channels — atomic output**: read [libraries/SRV_Channel/SRV_Channels.cpp:478-510](../libraries/SRV_Channel/SRV_Channels.cpp#L478-L510). The pattern is `cork()` at the start of a control cycle (latches all subsequent writes), then any number of `set_output_*` calls (which update internal channel buffers but do not push to the hardware), then `push()` at the end (atomically writes all latched channels to the RCOutput backend). The vehicle wrapper for "I have a control demand, where do I write it?" is `SRV_Channels::set_output_scaled` at [libraries/SRV_Channel/SRV_Channel_aux.cpp:617-680](../libraries/SRV_Channel/SRV_Channel_aux.cpp#L617-L680) — it takes a `SRV_Channel::Function` enum and a value, then writes through.

The Plane vehicle's call site is at [ArduPlane/servos.cpp:861-900](../ArduPlane/servos.cpp#L861-L900): `Plane::set_servos` opens with `AP::srv().cork();` (or equivalent), runs the per-axis output computation, and ends with `AP::srv().push();`.

**Key cites**:
- [libraries/AP_TECS/AP_TECS.cpp:1270-1350](../libraries/AP_TECS/AP_TECS.cpp#L1270-L1350) — `update_pitch_throttle`.
- [libraries/AP_TECS/AP_TECS.cpp:678-700](../libraries/AP_TECS/AP_TECS.cpp#L678-L700) — `_update_energies`.
- [libraries/AP_TECS/AP_TECS.cpp:719-820](../libraries/AP_TECS/AP_TECS.cpp#L719-L820) — `_update_throttle_with_airspeed`.
- [libraries/AP_TECS/AP_TECS.cpp:99](../libraries/AP_TECS/AP_TECS.cpp#L99) — `TECS_SPDWEIGHT`.
- [libraries/AP_TECS/AP_TECS.cpp:107](../libraries/AP_TECS/AP_TECS.cpp#L107) — `TECS_PTCH_DAMP`.
- [libraries/AP_L1_Control/AP_L1_Control.cpp:206-347](../libraries/AP_L1_Control/AP_L1_Control.cpp#L206-L347) — `update_waypoint`.
- [libraries/AP_L1_Control/AP_L1_Control.cpp:7-44](../libraries/AP_L1_Control/AP_L1_Control.cpp#L7-L44) — L1 `var_info[]`.
- [libraries/APM_Control/AP_RollController.cpp:185-227](../libraries/APM_Control/AP_RollController.cpp#L185-L227) — `get_servo_out`.
- [libraries/APM_Control/AP_RollController.cpp:27-50](../libraries/APM_Control/AP_RollController.cpp#L27-L50) — `RLL2SRV_TCONST`, `RLL2SRV_RMAX`.
- [libraries/SRV_Channel/SRV_Channels.cpp:478-510](../libraries/SRV_Channel/SRV_Channels.cpp#L478-L510) — `cork`/`push`.
- [libraries/SRV_Channel/SRV_Channel_aux.cpp:617-680](../libraries/SRV_Channel/SRV_Channel_aux.cpp#L617-L680) — `set_output_scaled`.
- [ArduPlane/servos.cpp:861-900](../ArduPlane/servos.cpp#L861-L900) — `Plane::set_servos`.

**Compare to your stack**: the `cork`/`push` pattern is one of several solutions to the "all servos must move on the same tick edge" problem. Alternatives include double-buffered DMA on the RCOut driver itself, or a dedicated transaction object passed into each setter. ArduPilot's choice keeps the call sites simple at the cost of a stateful contract (you must `push` what you `cork`) — the cooperative scheduler makes the contract easy to honour.

#### Adoption side-bar — what comes with the control pipeline

- **What this subsystem buys you in your codebase**: three battle-tested controllers with the same idiomatic shape — `var_info[]` table at the top, `update`/`get_servo_out` method that takes a desired state and returns a control command, constructor that takes references to AHRS/parameter sources.
- **What comes with it**: `AP_HAL::micros()`, `AP_Param`, `AP_AHRS` (or a stub of just the methods you call — your own AHRS), and `AP_Math` helpers (`is_zero`, `safe_sqrt`, `constrain_float`, `wrap_PI`). For TECS specifically: also `AP_FixedWing::FlightStage` and (optionally) `AP_Logger` for state inspection.
- **What it costs to keep vs replace**: the L1 controller is the cheapest extraction in the codebase (Engineer 1's capstone); TECS is one tier up (Engineer 2's capstone) because of `AP_FixedWing::FlightStage` and richer parameters; the roll/pitch/yaw `APM_Control` family is the same shape as L1 and TECS but glued into the vehicle's mode-and-stabiliser machinery, so adoption usually means lifting just the math.

#### Lab L4 — Modify roll-controller and TECS gains, observe response (~40 min)

Detailed runnable version: `course/labs/gnc-plane-3day-pilot-l4/`.

- **SITL invocation**: `Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --map`.
- **Phase A (roll)**: take off in TAKEOFF, switch to FBWA, fly steady. `param set RLL2SRV_TCONST 0.25` (default 0.5, halves the time constant). Move roll stick. Quit. Plot `ATT.DesRoll` vs `ATT.Roll`.
- **Phase B (TECS)**: relaunch, defaults. `param set TECS_PTCH_DAMP 0.15` (default 0.3 — half the damping). Switch to CRUISE; command a 50 m altitude step. Quit. Plot `TECS.h` vs `TECS.hdem`.
- **Pass criterion**: two MAVExplorer screenshots — one showing faster-but-oscillatory roll response, one showing damped-but-slower altitude tracking.

---

## Day 3 — Mission/Debug, Adoption Module, Capstone, Feedback (7 h)

**Goal**: each engineer has extracted one ArduPilot subsystem into a stub of a foreign codebase against a mock HAL, and has a working compilation plus a passing gtest. This is the artifact each engineer keeps.

Day 3 hands-on: M11 capstone is 2.5 h = 38% of the 6.5 h module budget; comfortably above the 25% rubric floor and the ≥ 2 h capstone rule.

---

### Module M9 — Mission, Navigation, Debugging (combined + compressed) (2.0 h, lecture+code-walk, *applied*)

**Why applied (not internals)**: you already debug flight code on your proprietary stack. You need ArduPilot's *specific* debug tools (autotest framework, dataflash log layout, gtest harness) at *applied* depth, not a third-pass theory tour.

**Learning objectives**:

1. Read `AP_Mission` briefly: the storage layout, the `update()` loop, the `MAV_CMD_NAV_*` execution dispatch.
2. Read where Auto mode hands off to L1 navigation: `Plane::navigate` → `nav_controller->update_waypoint`.
3. Recognise the `gdb` + SITL workflow: `sim_vehicle.py -v ArduPlane --gdb`. Set a breakpoint in `AP_TECS::update_pitch_throttle`, hit it, inspect TECS state.
4. Recognise the autotest framework: `Tools/autotest/arduplane.py`, the `AutoTestPlane` class, the per-test method pattern.
5. Recognise the gtest harness: `libraries/<lib>/tests/test_<name>.cpp` with `#include <AP_gtest.h>`, build with `./waf --targets tests/test_<name>`, run the produced binary. The capstone Engineer 3 will use this directly.
6. Dataflash log layout: `LogStructure` registration, `Write` API; recognise the Plane-specific messages.

**Mission storage and dispatch**: the `AP_Mission` class header at [libraries/AP_Mission/AP_Mission.h:1-100](../libraries/AP_Mission/AP_Mission.h#L1-L100) declares the public surface — start, stop, advance, retrieve current/next command. Mission items are stored in EEPROM/SD as a packed array of `Mission_Command` structs and indexed by sequence number. Auto mode's `update()` (at [ArduPlane/mode_auto.cpp:1-80](../ArduPlane/mode_auto.cpp#L1-L80)) dispatches on the current command's `MAV_CMD_NAV_*` ID — `WAYPOINT`, `LOITER_UNLIM`, `LOITER_TURNS`, `RTL`, `LAND` — into the matching handler. The handler sets up the navigation target; the actual cross-track control is L1.

**Auto → L1 hand-off**: `Plane::navigate` is declared in the `// navigation.cpp` block at [ArduPlane/Plane.h:1104-1115](../ArduPlane/Plane.h#L1104-L1115) (the function declaration is at line 1107, immediately after `loiter_angle_reset`/`loiter_angle_update`). It is the function Auto mode calls each tick to update L1. Inside, it calls `nav_controller->update_waypoint(prev_WP, next_WP)` — `nav_controller` is set to `&L1_controller` at construction (declared at [ArduPlane/Plane.h:269](../ArduPlane/Plane.h#L269)).

**`gdb` + SITL**: `sim_vehicle.py -v ArduPlane --gdb` launches the binary under gdb in a console window. Breakpoints persist across vehicle resets. The argument parsing for `--gdb` is in the sim option group at [Tools/autotest/sim_vehicle.py:1073-1240](../Tools/autotest/sim_vehicle.py#L1073-L1240) (same block we walked in M2; `--gdb` is at line 1213).

**Autotest framework**: open [Tools/autotest/arduplane.py:36-100](../Tools/autotest/arduplane.py#L36-L100) — `class AutoTestPlane(vehicle_test_suite.TestSuite)` with `vehicleinfo_key`, default mode, and entry points. Each test is a method on the class, e.g. `fly_LOITER` at [Tools/autotest/arduplane.py:213-260](../Tools/autotest/arduplane.py#L213-L260) — it takes off, enters LOITER, validates a circle, and disarms. Invocation is `Tools/autotest/autotest.py build.ArduPlane test.ArduPlane.<TestName>`. We are at recognition depth here — you have your own integration tests; you need to know that ArduPilot's tests are scripted Python flights against SITL, that they live in `Tools/autotest/`, and that they are how you would prove a fix to flight-relevant code.

**gtest harness**: tests live under `libraries/<lib>/tests/test_<name>.cpp` and include `<AP_gtest.h>`. Build with `./waf --targets tests/test_<name>`. The produced binary is at `build/sitl/tests/test_<name>` and runs standalone. Engineer 3's capstone uses exactly this harness against a stub repo.

**Log layout**: `LogStructure` is declared at [libraries/AP_Logger/LogStructure.h:1-100](../libraries/AP_Logger/LogStructure.h#L1-L100). Each message type has a fixed binary record format described by a `LogStructure` entry registered at logger init. Plane-specific messages: `ATT` (attitude), `CTUN` (control tuning), `NTUN` (nav tuning), `TECS` (energy controller), `ARSP` (airspeed), `XKF1`-`XKF5` (EKF3 internals). MAVExplorer / `mavlogdump.py` decode the records using the embedded format definitions.

**Key cites**:
- [libraries/AP_Mission/AP_Mission.h:1-100](../libraries/AP_Mission/AP_Mission.h#L1-L100)
- [ArduPlane/mode_auto.cpp:1-80](../ArduPlane/mode_auto.cpp#L1-L80)
- [ArduPlane/Plane.h:1104-1115](../ArduPlane/Plane.h#L1104-L1115) — `// navigation.cpp` declaration block (`navigate` at line 1107).
- [ArduPlane/Plane.h:269](../ArduPlane/Plane.h#L269) — `nav_controller = &L1_controller`.
- [Tools/autotest/sim_vehicle.py:1073-1240](../Tools/autotest/sim_vehicle.py#L1073-L1240) — argparse build + sim groups (re-used from M2).
- [Tools/autotest/arduplane.py:36-100](../Tools/autotest/arduplane.py#L36-L100)
- [Tools/autotest/arduplane.py:213-260](../Tools/autotest/arduplane.py#L213-L260)
- [libraries/AP_Logger/LogStructure.h:1-100](../libraries/AP_Logger/LogStructure.h#L1-L100)

**Compare to your stack**: SITL + gdb + Python autotest is one of three families of integration testing for flight code (the other two: hardware-in-the-loop with a dedicated rig; pure software in a unit-test-style framework). ArduPilot's autotest is closer to a system test than a unit test — each test takes seconds to minutes. The trade-off is fidelity (very high) vs speed (slower than unit tests). The C++ gtest layer fills the unit-test gap.

**Hands-on**: ~15 min code-along — every engineer launches `sim_vehicle.py -v ArduPlane --gdb`, sets a breakpoint at `AP_TECS::update_pitch_throttle`, hits it, prints the TECS state. No formal lab artifact; this folds into M11 setup.

---

### Module M10 — Adopting ArduPilot subsystems into a proprietary codebase (NEW) (2.0 h, lecture+code-walk, *internals*)

**The new module.** This is what you came for. We walk the four canonical extraction-seam patterns, then walk one worked example — `AP_L1_Control` — end-to-end, then compare with `AP_TECS` (stretch case) and the `AP_NavEKF3` lane-arbitration subset (Engineer 3's capstone target).

**Learning objectives**:

1. Survey the four canonical extraction-seam patterns: (a) bring the library + stub the HAL; (b) bring the library + replace `AP_Param` with your config system; (c) bring just the math/algorithm + reimplement the wiring; (d) treat ArduPilot as a black-box subprocess via MAVLink/DDS.
2. Walk the worked example (`AP_L1_Control`) end-to-end: identify the public surface, identify the entanglement set, identify what does *not* need to come, and execute the extraction recipe.
3. Compare with `AP_TECS` (stretch case) and with `AP_NavEKF3` lane-switch subset. Same shape; different entanglement weight.
4. Recognise the GPLv3 obligation explicitly. Your organisation owns the legal call.

**The four extraction-seam patterns**:

- **(a) Library + stub HAL.** Vendor the source files; provide a thin mock HAL implementing only the functions the library actually calls (typically `AP_HAL::micros()`, sometimes `Scheduler::delay()`). The library still believes it is running inside ArduPilot. Used for `AP_L1_Control`, `AP_TECS`, and most controllers and small libraries.
- **(b) Library + replace `AP_Param`.** Vendor the source; either keep `AP_Param` and stub a `Storage` backend, or replace `var_info[]` access with your own config system's accessors. The latter requires a sed pass over the source plus discipline, but removes a major dependency. Used when your config system is incompatible (e.g. yours is JSON-backed).
- **(c) Math/algorithm only + reimplement the wiring.** Read the algorithm, reimplement it in your codebase using your idioms. Best for cases where the ArduPilot file is short and the algorithm is what you want, not the wiring (e.g. lifting just the lane-switch arbitration logic from `NavEKF3::checkLaneSwitch`). Used for Engineer 3's capstone.
- **(d) Black-box ArduPilot via MAVLink/DDS.** Run unmodified ArduPilot in a companion process; talk to it over MAVLink or DDS. Not extraction in the strict sense — useful when you want ArduPilot's behaviour without integrating its source.

**Worked example — `AP_L1_Control`** (smallest, most self-contained library that still teaches the full extraction problem):

**Public surface**: open the header at [libraries/AP_L1_Control/AP_L1_Control.h:1-138](../libraries/AP_L1_Control/AP_L1_Control.h#L1-L138). The class takes a constructor of `(AP_AHRS &ahrs, const AP_FixedWing &parms)`, exposes `update_waypoint(prev, next, dist_min)`, `update_loiter(center, radius, direction)`, `update_heading_hold(navigation_heading_cd)`, plus accessors for `nav_roll_cd()`, `lateral_acceleration()`, `nav_bearing_cd()`, `bearing_error_cd()`, `crosstrack_error()`, etc. The full header is 138 lines — fits comfortably as a read-aloud.

**Entanglement set**: open [libraries/AP_L1_Control/AP_L1_Control.cpp:1-15](../libraries/AP_L1_Control/AP_L1_Control.cpp#L1-L15). The file declares `#include <AP_HAL/AP_HAL.h>`, `extern const AP_HAL::HAL& hal;`, then the `var_info[]` table. The actual function bodies use:

- `AP_HAL::micros()` for `_last_update_waypoint_us` differencing.
- `AP_Param` for the four `NAVL1_*` parameters at [libraries/AP_L1_Control/AP_L1_Control.cpp:7-44](../libraries/AP_L1_Control/AP_L1_Control.cpp#L7-L44).
- `AP_AHRS::get_location`, `groundspeed_vector`, `get_yaw`, `get_yaw_sensor` (4 methods).
- `Location` from `AP_Common/Location.h` for waypoint type and great-circle math.
- `AP_Math` helpers — `wrap_PI`, `constrain_float`, `safe_sqrt`, `is_zero`, `is_positive`. The full math header is at [libraries/AP_Math/AP_Math.h:1-100](../libraries/AP_Math/AP_Math.h#L1-L100).

**What does NOT need to come**:

- No `AP_Logger` calls in `update_waypoint` — the controller is silent in the hot path.
- No `GCS_SEND_TEXT` in the control path — error reporting goes through return values.
- No `AP_Mission` — the caller passes waypoints in.
- No `AP_NavEKF3` — `AP_AHRS` hides which estimator is running. The caller's `AHRS` may be a thin shim around their own EKF.

**Extraction recipe**:

1. Stub `AP_HAL::HAL` in a `mock_hal.cpp` with just `AP_HAL::micros()` against your platform's clock. Provide a no-op `Scheduler::delay()` if anything needs it.
2. Replace `AP_AHRS &ahrs` parameter with a thin `IAhrs` interface that exposes the four methods L1 actually calls. Implement against your stack's AHRS.
3. Vendor `AP_Math` `wrap_PI` / `constrain_float` / `safe_sqrt` (small functions; copy or inline them).
4. Vendor `AP_Common/Location.h` (or replace with your geo type and adjust `update_waypoint`'s signature).
5. Compile against your build system (CMake or whatever your stack uses). Test against gtest.

This is exactly Engineer 1's capstone in M11.

**Stretch case — `AP_TECS`**: same shape as L1, but the file header at [libraries/AP_TECS/AP_TECS.cpp:1-30](../libraries/AP_TECS/AP_TECS.cpp#L1-L30) shows additional includes — `AP_Landing.h`, `AP_FixedWing.h`. Inside the class, `update_pitch_throttle` uses `AP_FixedWing::FlightStage` to gate landing-vs-cruise behaviour. There are also `AP_Logger::Write` calls scattered through the body for state inspection — you can keep them as no-op stubs (recommended for debugging) or remove them. Engineer 2's capstone walks this.

**Hardest case — `AP_NavEKF3` lane-switch subset**: the lane-arbitration logic is at [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1029-1078](../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1029-L1078) (`checkLaneSwitch` plus `switchLane`). The error metric it depends on is `errorScore` at [libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp:62-86](../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L86). The trick is that `errorScore` reads internal core state (innovation test ratios from many fusion paths). For the extraction, **accept that *your* EKF instances each compute their own `errorScore`** (or whatever metric you choose — it does not have to be the max-of-test-ratios formula). Lift only the **arbitration logic** from `checkLaneSwitch` and `switchLane`. That is ≤ 50 lines of real algorithm wrapped in ArduPilot scaffolding. Engineer 3's capstone walks this.

**The seam itself**: the HAL boundary, revisited. Class at [libraries/AP_HAL/HAL.h:21-90](../libraries/AP_HAL/HAL.h#L21-L90); free functions at [libraries/AP_HAL/system.h:14-21](../libraries/AP_HAL/system.h#L14-L21). For an algorithm-only extraction, the minimum-viable HAL is two free functions (`micros`, `millis`) plus a degenerate `Scheduler` (delay only). Everything else can be stubbed.

**The hard truth**: extracting from a GPLv3 codebase carries license obligations. The legal posture is your organisation's call, not the course's. State this explicitly and move on.

**Key cites**:
- [libraries/AP_L1_Control/AP_L1_Control.h:1-138](../libraries/AP_L1_Control/AP_L1_Control.h#L1-L138) — full header.
- [libraries/AP_L1_Control/AP_L1_Control.cpp:1-15](../libraries/AP_L1_Control/AP_L1_Control.cpp#L1-L15) — file header / dependencies.
- [libraries/AP_L1_Control/AP_L1_Control.cpp:7-44](../libraries/AP_L1_Control/AP_L1_Control.cpp#L7-L44) — `var_info[]` table.
- [libraries/AP_L1_Control/AP_L1_Control.cpp:206-347](../libraries/AP_L1_Control/AP_L1_Control.cpp#L206-L347) — `update_waypoint` body.
- [libraries/AP_TECS/AP_TECS.cpp:1-30](../libraries/AP_TECS/AP_TECS.cpp#L1-L30) — TECS file header.
- [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1029-1078](../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1029-L1078) — lane-switch subset.
- [libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp:62-86](../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L86) — `errorScore`.
- [libraries/AP_HAL/HAL.h:21-90](../libraries/AP_HAL/HAL.h#L21-L90) — the seam.
- [libraries/AP_HAL/system.h:14-21](../libraries/AP_HAL/system.h#L14-L21) — the four free functions.
- [libraries/AP_Math/AP_Math.h:1-100](../libraries/AP_Math/AP_Math.h#L1-L100) — math helpers.

**Compare to your stack**: every adoption decision is a build vs buy decision. ArduPilot is in a third category — it is open-source, GPLv3, and well-tested. The cost of "buy" is the GPLv3 obligation; the cost of "build" is the multi-quarter integration work plus the loss of the ArduPilot community's flight-test coverage. Pattern (a) is build for the wiring, buy for the algorithm — usually the right answer.

**Hands-on**: no formal lab here — this is the briefing module. M11 is the lab.

---

### Module M11 — Capstone: extract one subsystem into a foreign-codebase stub (2.5 h, solo lab, *internals*)

**The artifact each engineer keeps.** Each engineer extracts their pre-allocated subsystem into a stub repo, makes a failing gtest pass, and presents the entanglement they hit at the end.

**Setup (provided by lab-builder under `course/labs/gnc-plane-3day-pilot-l5/`)**: three pre-staged stub repos (`eng1-l1/`, `eng2-tecs/`, `eng3-ekf-lane/`) with:

- A minimal `mock_hal.cpp` providing `AP_HAL::millis()`, `AP_HAL::micros()`, `hal.scheduler->delay()` against the host clock.
- A `mock_ahrs.h` (engineers 1 and 2) providing the AHRS-interface methods their target subsystem calls — for L1: `get_location`, `groundspeed_vector`, `get_yaw`, `get_yaw_sensor`; for TECS: `get_pitch`, `get_yaw`, `get_velocity_NED`, etc.
- A `mock_storage.cpp` (all three) providing a no-op storage backend for `AP_Param`.
- A vendored copy of `AP_Math` headers (engineers 1 and 2) and `AP_Common/Location.h` (engineer 1).
- For Engineer 3: a `mock_NavEKF3_core.h` with a configurable `errorScore()` value, plus the lane-switch source files copied verbatim.
- A `CMakeLists.txt` (or Makefile) and a vendored gtest.
- One initially-failing test stub.

**Per-engineer assignments**:

- **Engineer 1 (`AP_L1_Control`)**: vendor `AP_L1_Control.h`/`.cpp` plus `AP_Math` helpers; stub `AP_AHRS` and `Location`; compile; pass a gtest that exercises `update_waypoint(prev, next, 0)` on a hardcoded scenario where `prev=(0,0)`, `next=(1000m, 0)`, vehicle at `(500m, 100m)` heading 90°, and expects positive `nav_roll_cd` (turn right toward the line).
- **Engineer 2 (`AP_TECS`)**: vendor `AP_TECS.h`/`.cpp`; stub `AP_AHRS`, `AP_Logger`, `AP_FixedWing::FlightStage`; compile; pass a gtest that exercises one cycle of `update_pitch_throttle` with a 100 m altitude error and a 5 m/s airspeed error, and expects bounded throttle and pitch demands.
- **Engineer 3 (`AP_NavEKF3` lane-health subset)**: vendor only `NavEKF3::checkLaneSwitch`, `NavEKF3::switchLane`, `NavEKF3::updateCoreErrorScores`, `NavEKF3::updateCoreRelativeErrors`, and `NavEKF3_core::errorScore`. Stub the surrounding `NavEKF3_core` with a configurable `errorScore` value. Compile; pass a gtest that creates 3 mock cores with error-scores `[0.2, 1.5, 0.3]`, verifies `checkLaneSwitch` selects lane 2 (lowest, below the 0.9 gate), and verifies the 5-second debounce.

**Pass criterion**: the engineer's gtest builds and passes. Each engineer presents (~5 min) the entanglement they hit and the design choice they made for it.

**Citations**: re-used from M10. No new cites in this module.

---

### Module M11.5 — Feedback session (0.5 h, discussion)

Pilot-cohort feedback on course content, depth, pacing, lab quality, and adoption-axis utility. Held during the Day 3 buffer slot. Output is captured for course-orchestrator's review and for material-builder's iteration on slides + handouts.

Topics for the session:

- Per-module: was the depth right? Was the time budget right?
- Per-lab: did the lab teach what M-of-day intended? Where did setup break?
- Adoption axis: did the M4–M8 side-bars accumulate into a useful framework? Did M10 land? Did the capstone produce an artifact each engineer expects to use?
- What would make the pilot run as a 2-day course? As a 4-day course?

---

## Plan reference

Generated from course/plans/plan-gnc-plane-3day-pilot-iter2.md.

## Citation drift report

The plan cites were re-verified with `grep -n` against the working tree at branch `GNC-0.1` during writing. Adjustments versus plan anchors are listed below; iter-1 entries that the iter-2 plan supersedes are removed; iter-2 fixes (F1, F2, F3, F4 from [review-iter1.md](reviews/review-plan-gnc-plane-3day-pilot-iter1.md)) are listed as a final group.

Carried forward from iter 1 (still relevant; verified again against the working tree):

- `AP_L1_Control::update_waypoint` body: plan iter1 range `206-349` → course range `206-347`. The function closing brace is at line 347, not 349. Plan iter2 ratifies this tightening at [plan-iter2.md:331](plans/plan-gnc-plane-3day-pilot-iter2.md#L331).
- `AP_RollController::get_servo_out` body: plan iter1 range `185-232` → course range `185-227`. Function closes at line 227. Ratified by plan iter2 at [plan-iter2.md:424](plans/plan-gnc-plane-3day-pilot-iter2.md#L424).
- `AP_TECS::TECS_SPDWEIGHT` declaration: plan iter1 range `90-110` → course single-line cite `99`. Ratified by plan iter2 at [plan-iter2.md:413](plans/plan-gnc-plane-3day-pilot-iter2.md#L413).
- `AP_TECS::TECS_PTCH_DAMP` declaration: plan iter1 range `101-110` → course single-line cite `107`. Ratified by plan iter2 at [plan-iter2.md:414](plans/plan-gnc-plane-3day-pilot-iter2.md#L414).
- `AP_RollController::RLL2SRV_TCONST`: plan range `27-50` preserved at the `var_info` block level; the course also adds a single-line cite to line `35` for M8 precision. Unchanged in iter 2.
- `ArduPlane/Parameters.cpp` `AIRSPEED_MIN`/`MAX` block: plan iter1 range `290-310` → course range `288-310`. The `// @Param: AIRSPEED_MIN` comment opens on line 288. Ratified by plan iter2 at [plan-iter2.md:374](plans/plan-gnc-plane-3day-pilot-iter2.md#L374).
- `Plane.h` `nav_controller = &L1_controller` cite at line 269: confirmed against the working tree. Plan iter1 did not give an exact line; plan iter2 carries it explicitly at [plan-iter2.md:306](plans/plan-gnc-plane-3day-pilot-iter2.md#L306).
- `SRV_Channels::push`/`cork` body: range `478-510` — `cork` opens at line 478, `push` at line 486. The cited range covers both for the pedagogical grouping. Unchanged.

Iter-2 fixes applied to course markdown (responding to iter-1 review findings F1-F4):

- **F1 (M7, blocker)**: the iter-1 draft's fenced `errorScore` body used fabricated symbol names (`gpsPosTestRatio`, `gpsVelTestRatio`, `tasDataDelayed.allowFusion`, `lastTasPassTime_ms`) and the wrong scaling factors (`0.5f` instead of `0.3f` on the magnetometer term). The body has been replaced with a verbatim copy of [AP_NavEKF3_Outputs.cpp:62-86](../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L86), and the surrounding prose updated to (a) cite the `0.3f` scaling factor for both airspeed and magnetometer terms, (b) note the airspeed gate also requires `arsp->get_num_sensors() >= 2` and `EKF_AFFINITY_ARSP`, (c) note the magnetometer gate `EKF_AFFINITY_MAG`, (d) include a 2-min aside on `EK3_AFFINITY` parameter that controls which observations participate. Cite range tightened from `:62-83` → `:62-86` (function actually ends at line 86) per [plan-iter2.md:334](plans/plan-gnc-plane-3day-pilot-iter2.md#L334).
- **F2 (M2, M9, major)**: replaced the fabricated argparse anchor `[Tools/autotest/sim_vehicle.py:1500-1600]` (which actually points at post-parse vehicle-detection code) with `[:1073-1240]` (build + sim option groups containing `--vehicle`/`--frame`/`--debug`/`--gdb`) at both M2 and M9. Added a paired cite `[:1405-1436]` for the MAVProxy compatibility group covering `--map`/`--console` per [plan-iter2.md:307,432-433](plans/plan-gnc-plane-3day-pilot-iter2.md#L307). Verified `grep -n "add_option" Tools/autotest/sim_vehicle.py` returns matches at lines 1073, 1078, 1106, 1213, 1408+ in the cited ranges.
- **F3 (M9, major)**: replaced `[ArduPlane/Plane.h:920-940]` (which actually contains `stabilize_*` declarations) with `[:1104-1115]` (the `// navigation.cpp` declaration block opening at line 1104, with `void navigate();` at line 1107) per [plan-iter2.md:305](plans/plan-gnc-plane-3day-pilot-iter2.md#L305). Verified `grep -n "void navigate\|navigation.cpp" ArduPlane/Plane.h` returns 1104, 1107.
- **F4 (M2, minor)**: tightened `[ArduPlane/mode_fbwa.cpp:1-46]` to `[:1-45]` (file is exactly 45 lines; range was off-by-one past EOF) per [plan-iter2.md:377](plans/plan-gnc-plane-3day-pilot-iter2.md#L377).
- **F6 (M3, nit)**: rephrased the M3 `BUILD.md` cite from "do not duplicate in lecture" (instructor-directive prose) to "consult it directly for unfamiliar errors. We do not narrate it here." (student-facing voice). Also rephrased two preamble disclosures ("out of scope for the pilot" → "covered in the 5-day source, not in this pilot"; "out of scope for this pilot" → "the pilot points at where they live but does not walk them as code") and the M4 hwdef tour framing to match the same discipline.
- **F7 (headings, nit)**: restored "Libraries" to M5 heading and "Frontend/Backend" to M6 heading per plan iter2 verbatim parity. Also normalised case on M2/M4/M10/M11 headings to match plan iter2 ("compressed", "adoption-seam framing", "Adopting ArduPilot subsystems into a proprietary codebase (NEW)", "extract one subsystem into a foreign-codebase stub"). M11.5 case normalised to "Feedback session".

Coordination-file cites: no coordination files (`AGENTS.md`, `CLAUDE.md`, `.claude/`, repo-root meta docs) appear in the student-facing body of this course, per [course/criteria/audience-fit.md:24](criteria/audience-fit.md#L24). Plan iter2's M3/M5 references to these files as instructor handoff are **not** echoed into student prose; only the substantive rule (e.g. "never renumber `AP_GROUPINFO` indices") is restated as course content.

Time-budget summary: Day 1 = M1 1.0 + M2 1.5 + M3 1.0 + M4 3.0 = 6.5 h modules + 0.5 h buffer = 7.0 h. Day 2 = M5 2.0 + M6 1.5 + M7 2.0 + M8 1.0 = 6.5 h modules + 0.5 h buffer = 7.0 h. Day 3 = M9 2.0 + M10 2.0 + M11 2.5 = 6.5 h modules + 0.5 h M11.5 feedback (held during the daily buffer slot) = 7.0 h. Course total = 21.0 h. No deviation from plan iter2 final figures.
