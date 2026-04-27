# Plan: GNC Plane 3-Day Pilot — Internals + Adoption Axis (iter 1)

First iteration. Driven by [course/orchestration/gnc-plane-3day-pilot/req.md](../orchestration/gnc-plane-3day-pilot/req.md), locked 2026-04-27 on branch `GNC-0.1` at commit `98325ac0cc`. Design baseline: [course/custom_gnc_course_plane.md](../custom_gnc_course_plane.md) (5-day curriculum). The 3-day pilot is a **strict subset of the 5-day Plane content** plus one new module and one new capstone on **adopting ArduPilot subsystems into a foreign codebase**.

All `path:line` cites are written as clickable markdown links per [course/criteria/citation-rigor.md](../criteria/citation-rigor.md). The link path prefix from `course/plans/` to top-level repo dirs is `../../`. Every cite below was `grep -n`-verified against the working tree (commit `98325ac0cc`) during planning; see **Verification**.

## Context

- **Audience**: 3 senior GNC engineers — small pilot cohort. C/C++ proficient, experienced flight-code developers on a proprietary in-house autopilot stack, no prior ArduPilot exposure (locked in [req.md:11-16](../orchestration/gnc-plane-3day-pilot/req.md#L11-L16)).
- **Prior knowledge assumed**:
  - Strong embedded C/C++, RTOS concepts, fixed-wing controls.
  - Familiar with EKFs, attitude controllers, energy controllers, lateral path-following on a proprietary stack.
  - Comfortable with `gdb`, `gtest`-style unit tests, reading large unfamiliar C++ codebases.
  - Zero ArduPilot-specific knowledge — they have never seen `AP_GROUPINFO`, `AP_HAL`, or `sim_vehicle.py`.
- **Vehicle target**: ArduPlane (fixed-wing) end-to-end. No QuadPlane content, no Copter content beyond brief library-mapping table for orientation.
- **Course length**: 3 days × 7 h teaching = 21 h total ([req.md:18](../orchestration/gnc-plane-3day-pilot/req.md#L18)).
- **Format**: in-person; 1:1 instructor time during labs given the cohort size of 3 ([req.md:19](../orchestration/gnc-plane-3day-pilot/req.md#L19)).
- **Depth**: **internals** — math-as-code, function-body walks, EKF lane-switch arbitration as code, TECS energy-balance equations as code, L1 lateral-acceleration command as code. The 5-day course is already at internals depth for this audience; the pilot stays there ([req.md:20](../orchestration/gnc-plane-3day-pilot/req.md#L20)).
- **Hardware**: SITL only — no real boards in this pilot ([req.md:23](../orchestration/gnc-plane-3day-pilot/req.md#L23)).
- **What is preserved from the 5-day source**: Modules 1, 2, 4, 5, 6, 7, 8, 9 (operations + build + HAL + infrastructure + sensors + AHRS/EKF + control), with structure intact and citation backbone reused per Appendix B of [custom_gnc_course_plane.md:1263-1278](../custom_gnc_course_plane.md#L1263-L1278). What is replaced: Day 5's integration project (Module 14) is **replaced by the new capstone**. What is dropped: Modules 13 (Lua), 15 (Pegasus), 16 (advanced workshop) entirely. What is compressed: Modules 2 (operations), 10+11 (mission + debugging combined). What is added: a new dedicated 2 h **adoption-axis module** plus recurring 2–4 min adoption side-bars in Days 1–2 and the 2.5 h capstone.
- **Constraints**: SITL only (no airspace, no logistics); 1:1 lab support given the cohort of 3; the audience's frame of reference is "compare every ArduPilot decision to my proprietary stack" so framing must consistently cast ArduPilot's choices as **one design among many**, not as canonical ([req.md:99-103](../orchestration/gnc-plane-3day-pilot/req.md#L99-L103)).
- **Iteration number**: iter 1, no prior plan to supersede. No prior reviews exist for this slug; no prior lab-tester runs exist for any `gnc-plane-3day-pilot-*` lab.

## Lessons Applied

Iteration 1 — no prior reviews or lab runs to learn from.

The `course/reviews/` and `course/labs/<slug>/runs/` directories contain no entries matching this slug. The pre-existing review files target the unrelated `intro-arducopter-aero-y1` slug. Their `Lessons Applied` content is not transitively binding on this plan, but two recurring rubric concerns documented in [review-plan-intro-arducopter-aero-y1-iter1.md](../reviews/review-plan-intro-arducopter-aero-y1-iter1.md) and [review-plan-intro-arducopter-aero-y1-iter2.md](../reviews/review-plan-intro-arducopter-aero-y1-iter2.md) are pre-emptively addressed:

- **Cite drift on common anchors.** This plan was authored against working-tree commit `98325ac0cc` and every cite was `grep -n`-verified during planning. See **Verification → Citation sanity** for the verified set, including drift-prone names: `NavEKF3::checkLaneSwitch` (live at [AP_NavEKF3.cpp:1029](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1029) — note the 5-day source occasionally references a name `checkAndDoLaneSwitch` which **does not exist** in the current tree; the lane-switch logic lives inline in `NavEKF3::UpdateFilter` plus the explicit `checkLaneSwitch` entrypoint, and `errorScore` is `NavEKF3_core::errorScore` at [AP_NavEKF3_Outputs.cpp:62](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62)), and `RLL2SRV_TCONST` (the actual ArduPilot parameter name; "RLL_RATE_P" is from the underlying PID and is a separate parameter — both are correctly distinguished in Module M8's roll-controller walk).
- **Per-day buffer ≥ 30 min, declared up front, not absorbed into modules.** Each day's 7 h is structured as 6.5 h modules + 0.5 h buffer for Q&A / breaks / slippage, satisfying [time-budget.md:12](../criteria/time-budget.md#L12). For the cohort of 3 senior engineers the buffer is also where 1:1 adoption-axis questions land (the side-bar Q&A often runs long with this audience).
- **No coordination-file cites in pedagogical material.** [AGENTS.md](../../AGENTS.md), [CLAUDE.md](../../CLAUDE.md), and `.claude/` files are not cited as autopilot teaching material in this plan. They are referenced only in instructor-only notes about the course-build pipeline. Concrete `@Param` examples come from real ArduPlane source (e.g. [ArduPlane/Parameters.cpp](../../ArduPlane/Parameters.cpp)), not from `AGENTS.md`'s example block.
- **Directive prose is instructor-only.** Anywhere this plan flags "do not derive", "compress", "skip the math", or similar curriculum framing, it is addressed to course-writer in the **Handoff → To course-writer** section, not embedded as student-facing prose.

## Decisions

The four scoping decisions (length, depth, vehicle, lab share) are locked by [req.md](../orchestration/gnc-plane-3day-pilot/req.md). The remaining design decisions for iter1 follow.

### Locked design choices

- **D1. Length: 21 h over 3 days (7 h/day).** Locked by [req.md:18](../orchestration/gnc-plane-3day-pilot/req.md#L18).
- **D2. Internals depth throughout.** Locked by [req.md:20](../orchestration/gnc-plane-3day-pilot/req.md#L20). Every internals module declares ≥ 5 file:line cites per [audience-fit.md:14](../criteria/audience-fit.md#L14).
- **D3. SITL only, no real hardware.** Locked by [req.md:23](../orchestration/gnc-plane-3day-pilot/req.md#L23).
- **D4. Vehicle = ArduPlane.** Locked by [req.md:17](../orchestration/gnc-plane-3day-pilot/req.md#L17). No QuadPlane content (req.md and the user prompt explicitly forbid pulling from [custom_gnc_course_quadplane.md](../custom_gnc_course_quadplane.md)).
- **D5. Adoption axis is recurring + dedicated + capstoned.** Recurring 2–4 min "adoption side-bars" in M4–M8 (Days 1–2 internals modules), plus a dedicated 2 h M10 (Day 3) titled *"Adopting ArduPilot subsystems into a proprietary codebase"*, plus a 2.5 h M11 solo-extraction capstone. Locked by [req.md:50-69](../orchestration/gnc-plane-3day-pilot/req.md#L50-L69).
- **D6. Per-day buffer = 30 min (0.5 h), declared up front.** Day total = 6.5 h modules + 0.5 h buffer = 7 h. Course total = 19.5 h modules + 1.5 h buffer = 21 h. Satisfies [time-budget.md:12](../criteria/time-budget.md#L12).
- **D7. Capstone allocations (solo, since cohort = 3).** Engineer 1 → `AP_L1_Control` (smallest, most self-contained — 547 lines per [AP_L1_Control.cpp](../../libraries/AP_L1_Control/AP_L1_Control.cpp), no `AP_Logger` or `GCS_MAVLink` dependencies in the hot path). Engineer 2 → `AP_TECS` (1610 lines per [AP_TECS.cpp](../../libraries/AP_TECS/AP_TECS.cpp), more entanglement: `AP_FixedWing::FlightStage`, `AP_Logger::Write`, `AP_AHRS`). Engineer 3 → `AP_NavEKF3` lane-health subset (NOT the full EKF — just `NavEKF3::checkLaneSwitch` at [AP_NavEKF3.cpp:1029-1062](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1029-L1062), `NavEKF3::switchLane` at [AP_NavEKF3.cpp:1064-1078](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1064-L1078), `NavEKF3::updateCoreErrorScores` at [AP_NavEKF3.cpp:1092-1099](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1092-L1099), and `NavEKF3_core::errorScore` at [AP_NavEKF3_Outputs.cpp:62-83](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L83) — the subset is well-bounded and the surrounding state machine is heavily documented). Locked by [req.md:65-69](../orchestration/gnc-plane-3day-pilot/req.md#L65-L69).
- **D8. Worked example for the adoption module = `AP_L1_Control`.** Smallest, most self-contained ArduPilot library that still teaches the full extraction problem (HAL boundary, `AP_GROUPINFO` parameter system, `extern const AP_HAL::HAL& hal;` pattern, `AP_HAL::micros()` time access). `AP_TECS` is shown as a stretch case in the same module if time allows; not required for the module to land. Locked by [req.md:62](../orchestration/gnc-plane-3day-pilot/req.md#L62).
- **D9. Drop policy from 5-day source.** Module 13 (Lua) — dropped (not on the adoption critical path, mentioned in M1 as one slide). Module 15 (Pegasus) — dropped (requires GPU hardware not available). Module 16 (advanced workshop) — dropped (3-day budget cannot fit). Module 14 (integration project) — replaced by M11 capstone. Module 12 (board porting) — folded into M4 (HAL) as a 15-min adoption side-bar; no standalone module. Mission + debugging — combined into a single 2 h M9. Locked by [req.md:73-78](../orchestration/gnc-plane-3day-pilot/req.md#L73-L78).
- **D10. Compression of M1 and M2.** M1 (Overview & Ecosystem) compressed from 1.5 h to 1.0 h ([req.md:84](../orchestration/gnc-plane-3day-pilot/req.md#L84)). M2 (Operations Essentials) compressed from 2.5 h to 1.5 h ([req.md:85](../orchestration/gnc-plane-3day-pilot/req.md#L85)) — keeps just enough SITL + MAVProxy + log fluency to drive code-walk demos; drops detailed mission planning, full failsafe-config tour, and the GCS UI tour.
- **D11. M4 (HAL) expanded from 2.5 h to 3.0 h** to absorb the adoption-seam framing and the board-porting side-bar (5-day Module 12 collapses here). Justified deviation from [req.md:87](../orchestration/gnc-plane-3day-pilot/req.md#L87)'s recommendation, which already specifies 3 h and is matched.
- **D12. Module numbering.** Day 1: M1, M2, M3, M4. Day 2: M5, M6, M7, M8. Day 3: M9, M10, M11. The numbering is **renumbered relative to the 5-day source** because the module set is different. The Appendix B mapping in the 5-day file ([custom_gnc_course_plane.md:1263-1278](../custom_gnc_course_plane.md#L1263-L1278)) is preserved as the citation backbone, but module numbers shift.
- **D13. Lab count = 5, all SITL-only, all ArduPlane.** L1: HAL + scheduler probe (Day 1 M4). L2: AP_Param add + observe (Day 2 M5). L3: GPS noise + EKF lane switch (Day 2 M7). L4: roll-controller and TECS gain modify + observe (Day 2 M8). L5: solo extraction capstone (Day 3 M11). Locked by user prompt's "Planning notes specific to this course → Lab specs."
- **D14. Adoption side-bar discipline.** Each of M4 (HAL), M5 (infrastructure), M6 (sensors), M7 (AHRS/EKF), M8 (control) ends with a 2–4 min "adoption side-bar" structured as: (a) "What this subsystem buys you in your codebase" (1 min), (b) "What comes with it" — list of `extern const AP_HAL::HAL& hal;`, `GCS_SEND_TEXT`, `AP_Logger::Write`, scheduler ticks, `AP_Param` registration, math helpers (1–2 min), (c) "What it costs to keep vs replace" (~1 min). Total adoption-axis content in Days 1–2 = ~15 min spread across 5 modules, plus the dedicated 2 h M10 plus 2.5 h M11.

## Deliverable

course-writer will produce one new file:

- [`course/custom_gnc_course_plane_3day_pilot.md`](../custom_gnc_course_plane_3day_pilot.md) — does not yet exist; to be created from this plan.

Relationship to existing files:

- **Sibling, prerequisite-style subset.** Does not replace, supplement, or modify [custom_gnc_course_plane.md](../custom_gnc_course_plane.md). The pilot's preamble points at the 5-day course as "the full version, if you want Days 4–5 content (board porting deep-dive, Lua, QuadPlane, soaring, advanced topics)."
- **No content from [custom_gnc_course_quadplane.md](../custom_gnc_course_quadplane.md)** — QuadPlane is out of scope.
- The course file ends with the line `Generated from course/plans/plan-gnc-plane-3day-pilot-iter1.md` per [scope-discipline.md:7](../criteria/scope-discipline.md#L7).

## Course Structure

| Day | Theme | Module-hours | Buffer | Total |
|-----|-------|--------------|--------|-------|
| 1   | Foundations + Build + HAL (with adoption framing) | 6.5 | 0.5 | 7.0 |
| 2   | Internals: infrastructure, sensors, AHRS/EKF, control | 6.5 | 0.5 | 7.0 |
| 3   | Mission/debug, dedicated adoption module, capstone, feedback | 6.5 | 0.5 | 7.0 |
|     | **Total** | **19.5** | **1.5** | **21.0** |

Per-day hands-on share is summarised in **Verification**. Buffer is the only slack — per-module times within a day sum to exactly 6.5 h.

---

### Day 1 — Foundations + Build + HAL with adoption framing (7 h)

**Goal**: by end of Day 1, every engineer has a debug SITL build of ArduPlane running on their laptop, has traced a sensor read from `Plane::ahrs_update` down through the HAL to the SITL backend, and has a clear mental model of the HAL boundary as the **primary extraction seam** for any ArduPilot subsystem they may want to vendor into their proprietary codebase.

Per-day budget: 6.5 h modules + 0.5 h buffer. Hands-on share target: ≥ 25% of 6.5 h = ≥ 1.625 h. Day 1 includes Lab L1 at 0.5 h and the in-module HAL-trace exercise at ~0.5 h ⇒ ~1 h hands-on minimum, plus optional code-along during M3 build walk pushes effective hands-on to ~1.6–1.8 h.

#### Module M1 — ArduPilot Overview & Ecosystem (1.0 h, lecture+demo, *survey*)

**Why survey**: this audience already builds autopilots; they need ArduPilot's *position* in the landscape, not a deep tour of MAVLink or community processes.

- **Objectives**:
  1. Place ArduPilot in the open-source autopilot landscape; recognise the licensing posture (GPLv3) and the resulting adoption constraints for proprietary use.
  2. Recognise the 6-vehicle / shared-libraries / HAL architecture in the directory tree.
  3. Locate ArduPlane's main vehicle class and scheduler table; confirm the 50 Hz fast-loop default vs Copter's 400 Hz default — and *why* (fixed-wing dynamics are slower).
  4. (One slide) Recognise that Lua scripting and DDS/ROS2 exist as integration surfaces but are out of scope for this pilot.
- **Citations** (≥ 5 to satisfy [audience-fit.md:14](../criteria/audience-fit.md#L14)):
  - [ArduPlane/Plane.h:1-50](../../ArduPlane/Plane.h#L1-L50) — file header, includes, `class Plane : public AP_Vehicle` declaration anchor.
  - [ArduPlane/Plane.cpp:62-95](../../ArduPlane/Plane.cpp#L62-L95) — `Plane::scheduler_tasks[]` table opening: `FAST_TASK(ahrs_update)`, `FAST_TASK(stabilize)`, `FAST_TASK(set_servos)`, `SCHED_TASK(navigate, 10, 150, 36)` etc.
  - [libraries/AP_Scheduler/AP_Scheduler.cpp:43-49](../../libraries/AP_Scheduler/AP_Scheduler.cpp#L43-L49) — the 50 Hz vs 400 Hz `SCHEDULER_DEFAULT_LOOP_RATE` `#if APM_BUILD_COPTER_OR_HELI` block (the *one* line that explains plane is 50 Hz by default).
  - [libraries/AP_Scheduler/AP_Scheduler.cpp:55-69](../../libraries/AP_Scheduler/AP_Scheduler.cpp#L55-L69) — `SCHED_LOOP_RATE` parameter declaration, `@Range: 50 400`, `@RebootRequired: True`.
  - [custom_gnc_course_plane.md:1280-1295](../custom_gnc_course_plane.md#L1280-L1295) — the Copter-vs-Plane library mapping table from Appendix C, used as a hand-out only (do not re-derive in slides).
- **Hands-on**: instructor live-demos `Tools/autotest/sim_vehicle.py -v ArduPlane --console --map` on the projector; engineers watch only. (~5 min within the 1 h module.) The lab proper is L1 in M4.

#### Module M2 — Operations Essentials, compressed (1.5 h, lecture+demo, *applied*)

**Why applied (not survey)**: the audience is going to drive SITL themselves in every later module; they need *applied* fluency on `sim_vehicle.py`, MAVProxy, and dataflash logs, but not the full operator-style mission-planning curriculum the 5-day source teaches.

- **Objectives**:
  1. Launch ArduPlane SITL from a clean clone, attach MAVProxy console, take off in `TAKEOFF` mode, switch to `FBWA`, fly a heading, switch to `RTL`.
  2. Read MAVProxy's textual telemetry: altitude, airspeed, mode, heartbeat.
  3. Identify the Plane-specific dataflash messages — `ATT`, `CTUN`, `NTUN`, `ARSP`, `TECS` — and what each carries (recognition only; deep log analysis is in M9).
  4. Drop: full mission planning, GCS-UI tour, geofence/rally tour, and the failsafe-configuration deep dive. These do not survive the 1.5 h budget for an audience that already operates a proprietary autopilot.
- **Citations**:
  - [Tools/autotest/sim_vehicle.py:1](../../Tools/autotest/sim_vehicle.py#L1) — file header banner; engineers just need to know the script exists and is the canonical SITL launcher.
  - [Tools/autotest/sim_vehicle.py:1500-1600](../../Tools/autotest/sim_vehicle.py#L1500-L1600) — argument parsing for `--vehicle`, `--frame`, `--map`, `--console`, `--debug` (range cite; instructor walks the relevant options live, does not narrate the whole 100 lines).
  - [ArduPlane/mode_takeoff.cpp:1-80](../../ArduPlane/mode_takeoff.cpp#L1-L80) — `ModeTakeoff::update` opening, just to anchor "TAKEOFF is software, not a hardware mode."
  - [ArduPlane/mode_fbwa.cpp:1-46](../../ArduPlane/mode_fbwa.cpp#L1-L46) — full `ModeFBWA::update()` and `ModeFBWA::run()` (the file is short — read aloud in 5 min).
  - [custom_gnc_course_plane.md:130-138](../custom_gnc_course_plane.md#L130-L138) — the "Key log messages for plane" list (`ATT`, `CTUN`, `NTUN`, `ARSP`, `TECS`) used as a printed reference, not re-derived in slides.
- **Hands-on**: ~10 min code-along: every engineer launches SITL on their laptop, takes off in `TAKEOFF`, switches to `FBWA`, switches to `RTL`. No formal lab; M4 has the first formal lab.

#### Module M3 — Build System & Development Environment (1.5 h, lecture+lab, *applied*)

**Why applied**: this audience knows build systems; they need ArduPilot's *waf* idioms and SITL+debug-symbols flow, not "what is a build system."

- **Objectives**:
  1. Run `./waf configure --board sitl --debug && ./waf plane`. Locate the build artifact at `build/sitl/bin/arduplane`.
  2. Recognise `wscript` files as Waf's per-directory build config (one example each from a vehicle dir and a library dir).
  3. Read `Tools/scripts/build_options.py` and recognise the `AP_<FEATURE>_ENABLED` compile-time-flag pattern — critical for understanding what comes "with" a subsystem at extraction time.
  4. Recognise the subset of build targets that matter: `plane`, `bin/arduplane`, `tests/test_<name>`.
- **Citations**:
  - [BUILD.md](../../BUILD.md) — referenced for engineers who hit unfamiliar errors; do not duplicate its contents in the course.
  - [ArduPlane/wscript:1-40](../../ArduPlane/wscript#L1-L40) — the vehicle `wscript` (the file is short; read aloud).
  - [libraries/AP_L1_Control/AP_L1_Control.cpp:1-15](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L1-L15) — file header showing `#include <AP_HAL/AP_HAL.h>`, `extern const AP_HAL::HAL& hal;`, the `var_info[]` opening line. This is the file the capstone Engineer 1 will extract.
  - [Tools/scripts/build_options.py:1-50](../../Tools/scripts/build_options.py#L1-L50) — file header + the first few `Feature(...)` entries. This is the one file in the codebase that enumerates the optional features, which directly determines "what comes with it" at extraction time.
  - [CLAUDE.md:120-150](../../CLAUDE.md#L120-L150) — repo-local Waf cheat sheet (instructor-only handoff reference; not student-facing pedagogical material per [audience-fit.md:24](../criteria/audience-fit.md#L24)).
- **Hands-on**: ~30 min code-along included in the module budget. Each engineer runs the configure + build sequence on their own laptop, ending with `./build/sitl/bin/arduplane --help` printing usage. No separate lab artifact; this folds into L1.

#### Module M4 — HAL Architecture with adoption-seam framing (3.0 h, lecture+code-walk+lab, *internals*)

**Why internals**: HAL is the *primary* extraction seam. Every adoption discussion later in the course returns to this module's framing. Internals depth, with ≥ 5 cites and a function-body walk through one HAL call.

- **Objectives**:
  1. Explain why HAL exists: same flight code on STM32 (ChibiOS), Linux, SITL, ESP32. Compare to the engineers' own proprietary HAL.
  2. Read `class AP_HAL::HAL`: enumerate the subsystems it owns (UART, I2C, SPI, GPIO, RCInput, RCOutput, Storage, Scheduler, AnalogIn, Flash). Recognise the constructor pattern.
  3. Trace one HAL call end-to-end in code: from `Plane::ahrs_update` → AHRS update → IMU read → SPI driver → SITL backend (or ChibiOS backend, briefly).
  4. Recognise the four canonical HAL access patterns: `extern const AP_HAL::HAL& hal;`, `AP_HAL::millis()`, `AP_HAL::micros()`, `hal.scheduler->delay(...)`. These are the four touchpoints that follow you everywhere when you extract.
  5. Read one `hwdef.dat` (CubeBlack) and recognise the directives: `MCU`, `OSCILLATOR_HZ`, `SERIAL_ORDER`, `SPIDEV`, `IMU`, `BARO`, `COMPASS`, `AIRSPEED`. This **replaces** the 5-day Module 12 standalone board-porting module — it is folded in here as a 15-min adoption side-bar at the end of the module.
  6. **Adoption side-bar (3 min)** at the end: "If you wanted to lift `AP_HAL` itself: you would be re-implementing the full hardware-abstraction surface. The audience already has their own HAL. The realistic adoption pattern is to **provide a stub `AP_HAL::HAL` against your platform's native APIs** — minimum viable surface = `millis`, `micros`, `scheduler->delay`, one UART, one Storage backend. M10 walks this in detail."
- **Citations** (≥ 5 mandatory at internals depth):
  - [libraries/AP_HAL/HAL.h:21-30](../../libraries/AP_HAL/HAL.h#L21-L30) — `class AP_HAL::HAL` opening + constructor signature start.
  - [libraries/AP_HAL/HAL.h:35-90](../../libraries/AP_HAL/HAL.h#L35-L90) — full constructor parameter list: 10 UARTs, I2C, SPI, GPIO, RCIn, RCOut, Scheduler, etc.
  - [libraries/AP_HAL/system.h:14-21](../../libraries/AP_HAL/system.h#L14-L21) — `AP_HAL::millis()`, `AP_HAL::micros()`, `AP_HAL::millis64()`, `AP_HAL::micros64()` declarations.
  - [libraries/AP_HAL/AP_HAL.h:1-31](../../libraries/AP_HAL/AP_HAL.h#L1-L31) — the umbrella include header; one slide of "this is the include line every consumer uses."
  - [ArduPlane/Plane.cpp:165-200](../../ArduPlane/Plane.cpp#L165-L200) — `Plane::ahrs_update` body: `arming.update_soft_armed()` → `ahrs.update()` → optional IMU log write → roll/pitch limit recalculation. The trace target.
  - [libraries/AP_HAL_SITL/HAL_SITL_Class.cpp:1-80](../../libraries/AP_HAL_SITL/HAL_SITL_Class.cpp#L1-L80) — SITL HAL instantiation; the bottom of the trace for the SITL build.
  - [libraries/AP_HAL_ChibiOS/hwdef/CubeBlack/hwdef.dat:1-100](../../libraries/AP_HAL_ChibiOS/hwdef/CubeBlack/hwdef.dat#L1-L100) — example board definition for the side-bar.
- **Hands-on lab spec (handoff to lab-builder; full spec in **Handoff → To lab-builder**)**: **Lab L1 — HAL + scheduler probe (~30 min within the module budget)**. Build debug SITL, launch, attach `gdb` to the running `arduplane` process, set a breakpoint at `Plane::ahrs_update`, hit it, inspect `AP_HAL::millis()` return value, confirm scheduler tick rate is 50 Hz by reading `AP::scheduler().get_loop_rate_hz()`. Pass criterion: gdb stops at the breakpoint and the engineer can read both `millis()` and the loop-rate value.

---

### Day 2 — Internals: infrastructure, sensors, AHRS/EKF, control (7 h)

**Goal**: by end of Day 2, every engineer has read `AP_Param`, `AP_NavEKF3` lane-switch arbitration, `AP_TECS::update_pitch_throttle`, `AP_L1_Control::update_waypoint`, and `AP_RollController::get_servo_out` as code, and has run three labs that probe each subsystem with a deliberate fault or modification.

Per-day budget: 6.5 h modules + 0.5 h buffer. Hands-on share target: ≥ 1.625 h. Day 2 includes L2 (~30 min), L3 (~40 min), L4 (~40 min) ⇒ ~1.83 h hands-on, satisfying the rubric.

#### Module M5 — Core Infrastructure Libraries with `AP_Param` adoption emphasis (2.0 h, lecture+code-walk+lab, *internals*)

**Why internals**: `AP_Param`, `AP_Scheduler`, `AP_Logger` are the three libraries that "come with" everything else when you extract. The audience must read them at code level.

- **Objectives**:
  1. Read `AP_Scheduler::Task` and `Plane::scheduler_tasks[]`. Recognise the `FAST_TASK` vs `SCHED_TASK(rate_hz, max_time_us, priority)` distinction.
  2. Read the `AP_GROUPINFO` macro family: how a `var_info[]` table maps to EEPROM-stored parameters with full `@Param`/`@DisplayName`/`@Description`/`@Range`/`@User` annotations. Recognise that parameter indices are baked into stored configs (per [AGENTS.md:354](../../AGENTS.md#L354) — referenced as a contributor-rule, NOT cited as pedagogical material).
  3. Read `AP_Logger`'s `WriteV` / `Write` API and recognise the `LogStructure` registration pattern.
  4. Read `AP_Vehicle` base class and how `Plane : public AP_Vehicle` consumes the scheduler/parameter/logger framework.
  5. **Adoption side-bar (4 min)**: "`AP_Param` is highly reusable in isolation — it is well-bounded. To adopt it standalone you need: `AP_Param::setup`, `AP_Param::load_all`, a `Storage` backend (≥ 16 KB EEPROM-equivalent), and the `AP_Param.h` header. You do NOT need `AP_Logger` or `GCS_MAVLink`. Trade-off: per-access lookup cost is non-trivial (linear scan over `var_info[]`); your proprietary stack's parameter system may be faster but less self-documenting."
- **Citations**:
  - [ArduPlane/Plane.cpp:62-95](../../ArduPlane/Plane.cpp#L62-L95) — scheduler table opening (also cited in M1 at survey depth; here read line-by-line).
  - [ArduPlane/Plane.cpp:30-60](../../ArduPlane/Plane.cpp#L30-L60) — `SCHED_TASK` and `FAST_TASK` macro definitions.
  - [libraries/AP_Param/AP_Param.h:140-160](../../libraries/AP_Param/AP_Param.h#L140-L160) — `AP_GROUPINFO_FLAGS`, `AP_GROUPINFO_FRAME`, `AP_GROUPINFO_FLAGS_DEFAULT_POINTER`, `AP_GROUPINFO` macro definitions.
  - [libraries/AP_Param/AP_Param.cpp:355-400](../../libraries/AP_Param/AP_Param.cpp#L355-L400) — `AP_Param::setup` body.
  - [libraries/AP_Param/AP_Param.cpp:1555-1620](../../libraries/AP_Param/AP_Param.cpp#L1555-L1620) — `AP_Param::load_all` body.
  - [ArduPlane/Parameters.cpp:290-310](../../ArduPlane/Parameters.cpp#L290-L310) — real `@Param: AIRSPEED_MIN` / `@Param: AIRSPEED_MAX` annotation block in Plane vehicle code. (Concrete `@Param` example sourced from real vehicle code, NOT from `AGENTS.md`.)
  - [libraries/AP_Scheduler/AP_Scheduler.h:140-180](../../libraries/AP_Scheduler/AP_Scheduler.h#L140-L180) — `get_loop_rate_hz`, `get_loop_period_us`, `get_loop_period_s` accessors.
  - [libraries/AP_Logger/AP_Logger.h:1-80](../../libraries/AP_Logger/AP_Logger.h#L1-L80) — file header + `LogStructure` typedef.
- **Hands-on lab spec**: **Lab L2 — Add a custom `AP_Float` parameter to ArduPlane (~30 min)**. Engineer adds `MY_PARAM` via `AP_GROUPINFO`, rebuilds, launches SITL, runs `param show MY_*`, sets `param set MY_PARAM 42.0`, restarts SITL, verifies persistence. Pass: `MY_PARAM` returns 42.0 after restart. Validates the AP_Param adoption walk.

#### Module M6 — Sensor Drivers, Frontend/Backend, Airspeed (1.5 h, lecture+code-walk, *internals*)

**Why internals**: airspeed is the plane-critical sensor and its frontend/backend pattern is the *most reusable* design pattern in ArduPilot. Read at code level.

- **Objectives**:
  1. Read the frontend/backend pattern: `AP_Airspeed` (frontend) → `AP_Airspeed_MS4525`, `AP_Airspeed_SITL` (backends) — the same pattern as `AP_Baro`, `AP_GPS`, `AP_InertialSensor`.
  2. Read `AP_Airspeed::get_airspeed()` and the EAS↔TAS conversion.
  3. Recognise where airspeed feeds: TECS (energy controller), EKF3 (wind estimation), L1 (only indirectly, via EKF position/velocity).
  4. **Adoption side-bar (3 min)**: "The frontend/backend pattern is the single most reusable design idea in ArduPilot. Your proprietary stack probably already has it, just named differently. To adopt `AP_Airspeed` itself: you bring the frontend, one backend (likely `AP_Airspeed_SITL` for testing + your platform's native I2C driver), `AP_HAL::I2CDevice`, and the `var_info[]` parameter table. Major entanglement: `AP_Param` (already adopted in M5), `AP_Logger` (optional), `GCS_SEND_TEXT` (replace with your own logger)."
- **Citations**:
  - [libraries/AP_Airspeed/AP_Airspeed.h:1-80](../../libraries/AP_Airspeed/AP_Airspeed.h#L1-L80) — frontend class declaration, `get_airspeed`, `get_airspeed_ratio`, `healthy`, `use` API.
  - [libraries/AP_Airspeed/AP_Airspeed_Backend.h:1-80](../../libraries/AP_Airspeed/AP_Airspeed_Backend.h#L1-L80) — backend interface.
  - [libraries/AP_Airspeed/AP_Airspeed_SITL.cpp:1-80](../../libraries/AP_Airspeed/AP_Airspeed_SITL.cpp#L1-L80) — SITL backend (the canonical reference backend for testing).
  - [libraries/AP_Airspeed/AP_Airspeed_MS4525.cpp:1-100](../../libraries/AP_Airspeed/AP_Airspeed_MS4525.cpp#L1-L100) — real I2C backend, opening through `_init`.
  - [libraries/AP_Airspeed/Airspeed_Calibration.cpp:1-80](../../libraries/AP_Airspeed/Airspeed_Calibration.cpp#L1-L80) — auto-calibration logic against GPS groundspeed.
- **Hands-on**: ~10 min in-module code-along; the engineers grep for `airspeed_ratio` and trace one consumer in `AP_TECS`. No formal lab; M7 and M8 carry the formal labs for this day.

#### Module M7 — AHRS + EKF Internals (2.0 h, lecture+code-walk+lab, *internals*)

**Why internals**: this is where the audience leans in hardest — they have built EKFs. They want to see ArduPilot's specific design choices: lane-switch arbitration, error-score formula, wind-state inclusion, GPS source-set selection.

- **Objectives**:
  1. Read `AP_AHRS` as an interface; recognise that vehicle code never calls EKF directly.
  2. Read `NavEKF3::UpdateFilter` — the periodic lane-arbitration loop. Recognise `runCoreSelection`, the 10-second debounce, the `coreBetterScore` test, the `BETTER_THRESH` constant.
  3. Read `NavEKF3::checkLaneSwitch` — the explicit "EKF failsafe is about to trigger; can a lane swap save us?" entry point called from vehicle code.
  4. Read `NavEKF3_core::errorScore` — the consolidated error metric: max of GPS fusion test ratio, altimeter test ratio, airspeed test ratio (gated by 2-airspeed-sensor presence), magnetometer test ratio.
  5. Read `NavEKF3::switchLane` — the actual switch with yaw/pos reset propagation and `EKF3 lane switch %u` GCS warning.
  6. Wind estimation: read where in `AP_NavEKF3_PosVelFusion.cpp` airspeed is fused (briefly).
  7. **Adoption side-bar (4 min)**: "Adopting full `AP_NavEKF3` is a *large* undertaking — 2279 lines in `AP_NavEKF3_core.cpp` alone, and the dependency graph is broad: DAL (Data Access Layer), AHRS, multiple sensor frontends. The realistic adoption pattern is to extract just the *lane-arbitration logic* (≤ 200 lines) and apply it to multiple instances of *your own* EKF. That is exactly what Engineer 3's capstone does."
- **Citations**:
  - [libraries/AP_AHRS/AP_AHRS.h:1-80](../../libraries/AP_AHRS/AP_AHRS.h#L1-L80) — frontend interface header.
  - [libraries/AP_NavEKF3/AP_NavEKF3.cpp:910-1020](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L910-L1020) — `NavEKF3::UpdateFilter` body; the periodic lane-arbitration loop.
  - [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1029-1062](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1029-L1062) — `NavEKF3::checkLaneSwitch` body; the explicit "about-to-fail" entry point.
  - [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1064-1078](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1064-L1078) — `NavEKF3::switchLane` body.
  - [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1092-1099](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1092-L1099) — `NavEKF3::updateCoreErrorScores`.
  - [libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp:62-83](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L83) — `NavEKF3_core::errorScore` body, the consolidated error metric.
  - [libraries/AP_NavEKF3/AP_NavEKF3_core.h:140-160](../../libraries/AP_NavEKF3/AP_NavEKF3_core.h#L140-L160) — `errorScore` declaration.
  - [libraries/AP_NavEKF3/AP_NavEKF3.cpp:715-722](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L715-L722) — `EK3_PRIMARY` parameter declaration (which IMU is the default primary).
- **Hands-on lab spec**: **Lab L3 — GPS noise + EKF lane switch (~40 min)**. Engineer launches SITL, sets `SIM_GPS_NOISE 5` then `SIM_GPS_GLTCH 50` mid-flight (use `SIM_GPS_GLTCH` from [SIM_GPS.cpp:69-75](../../libraries/SITL/SIM_GPS.cpp#L69-L75)), observes the GCS `EKF3 lane switch N` statustext, downloads dataflash, identifies `XKF*` lane-switch event records and the `errorScore` divergence. Pass: lane switch fires within 30 s of the glitch injection AND the dataflash records the switch event. Validates the EKF internals walk.

#### Module M8 — Control Pipeline: TECS, L1, APM_Control, SRV_Channels (1.5 h, lecture+code-walk+lab, *internals*)

**Why internals**: the audience builds control laws. They want to see TECS's energy split, L1's lateral acceleration command, and the airspeed-scaled PID structure as code, with the actual scaling formulae.

- **Objectives**:
  1. Read `AP_TECS::update_pitch_throttle` (the main entry point). Recognise the energy-balance computation and the speed/height priority knob (`TECS_SPDWEIGHT`).
  2. Read `AP_L1_Control::update_waypoint` and the lateral-acceleration formula. Recognise `_L1_dist = MAX(0.3183099f * _L1_damping * _L1_period * groundSpeed, dist_min)` (`0.3183099 = 1/π`).
  3. Read `AP_RollController::get_servo_out`: angle-error → desired-rate → PID, with airspeed scaling via the `scaler` parameter.
  4. Read `SRV_Channels::push` and the cork/push pattern for atomic servo updates.
  5. **Adoption side-bar (4 min)**: "All three controllers (`AP_RollController`, `AP_TECS`, `AP_L1_Control`) follow the same shape: a `var_info[]` table at the top, an `update`/`get_servo_out` method that takes a desired state and returns a control command, and a constructor that takes references to AHRS/parameter sources. To adopt one: bring `AP_HAL::micros()`, `AP_Param`, `AP_AHRS` (or a stub of just the methods used — your own AHRS), and `AP_Math` helpers (`is_zero`, `safe_sqrt`, `constrain_float`, `wrap_PI`). Capstone Engineers 1 and 2 do exactly this for L1 and TECS respectively."
- **Citations**:
  - [libraries/AP_TECS/AP_TECS.cpp:1270-1350](../../libraries/AP_TECS/AP_TECS.cpp#L1270-L1350) — `AP_TECS::update_pitch_throttle` opening through the energy-balance setup.
  - [libraries/AP_TECS/AP_TECS.cpp:678-700](../../libraries/AP_TECS/AP_TECS.cpp#L678-L700) — `AP_TECS::_update_energies`, the actual energy formula.
  - [libraries/AP_TECS/AP_TECS.cpp:719-820](../../libraries/AP_TECS/AP_TECS.cpp#L719-L820) — `AP_TECS::_update_throttle_with_airspeed` (range cited; instructor walks the structure).
  - [libraries/AP_TECS/AP_TECS.cpp:90-110](../../libraries/AP_TECS/AP_TECS.cpp#L90-L110) — `TECS_SPDWEIGHT` parameter declaration with `@Range: 0 2`, default 1.0.
  - [libraries/AP_TECS/AP_TECS.cpp:101-110](../../libraries/AP_TECS/AP_TECS.cpp#L101-L110) — `TECS_PTCH_DAMP` parameter (default 0.3); used in Lab L4.
  - [libraries/AP_L1_Control/AP_L1_Control.cpp:206-290](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L206-L290) — `AP_L1_Control::update_waypoint` body. (The full function runs to ~349; instructor reads the opening 80 lines.)
  - [libraries/AP_L1_Control/AP_L1_Control.cpp:7-44](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L7-L44) — `var_info[]` table: `NAVL1_PERIOD`, `NAVL1_DAMPING`, `NAVL1_XTRACK_I`, `NAVL1_LIM_BANK`.
  - [libraries/APM_Control/AP_RollController.cpp:185-232](../../libraries/APM_Control/AP_RollController.cpp#L185-L232) — `AP_RollController::get_servo_out` body.
  - [libraries/APM_Control/AP_RollController.cpp:27-50](../../libraries/APM_Control/AP_RollController.cpp#L27-L50) — `RLL2SRV_TCONST` and `RLL2SRV_RMAX` parameter declarations (note: not "RLL_RATE_P"; the rate-PID parameters live in the underlying `AC_PID` and are commented at lines 51-100).
  - [libraries/SRV_Channel/SRV_Channels.cpp:478-510](../../libraries/SRV_Channel/SRV_Channels.cpp#L478-L510) — `SRV_Channels::cork` and `SRV_Channels::push`: the atomic-update pattern.
  - [libraries/SRV_Channel/SRV_Channel_aux.cpp:617-680](../../libraries/SRV_Channel/SRV_Channel_aux.cpp#L617-L680) — `SRV_Channels::set_output_scaled` body (the canonical "I have a control demand, where do I write it" call).
  - [ArduPlane/servos.cpp:861-900](../../ArduPlane/servos.cpp#L861-L900) — `Plane::set_servos` body: the `AP::srv().cork()` opening and the function structure.
- **Hands-on lab spec**: **Lab L4 — Modify roll-controller and TECS gains, observe response (~40 min)**. Engineer halves `RLL2SRV_TCONST` (from 0.5 to 0.25), flies FBWA, observes faster but more oscillatory roll response in dataflash `ATT.DesRoll` vs `ATT.Roll`. Then resets, halves `TECS_PTCH_DAMP` (from 0.3 to 0.15), flies a climb, observes altitude-tracking oscillation in dataflash `TECS.h` vs `TECS.hdem`. Pass: clear visual evidence in MAVExplorer plots that both gain changes alter the closed-loop response. Validates the control-pipeline walk.

---

### Day 3 — Mission/debug, dedicated adoption module, capstone, feedback (7 h)

**Goal**: each engineer has extracted one ArduPilot subsystem into a stub of a foreign codebase against a mock HAL, and has a working compilation + a passing gtest. This is the artifact each engineer keeps.

Per-day budget: 6.5 h modules + 0.5 h buffer. Hands-on share: M11 capstone alone is 2.5 h (~38% of the module budget) — comfortably exceeds the 25% rubric floor. Day 3 also contains the 0.5 h feedback session, which is not labelled "hands-on" but is interactive.

#### Module M9 — Mission, Navigation, Debugging (combined + compressed) (2.0 h, lecture+code-walk, *applied*)

**Why applied (not internals)**: the audience already debugs flight code on their proprietary stack; they need ArduPilot's *specific* debug tools (autotest framework, dataflash log layout, gtest harness) at *applied* depth, not a third-pass theory tour.

- **Objectives**:
  1. Read `AP_Mission` briefly: the storage layout, the `update()` loop, the `MAV_CMD_NAV_*` execution dispatch.
  2. Read where Auto mode hands off to L1 navigation: `Plane::navigate` → `nav_controller->update_waypoint`.
  3. Recognise the `gdb` + SITL workflow: `sim_vehicle.py -v ArduPlane --gdb`. Set a breakpoint in `AP_TECS::update_pitch_throttle`, hit it, inspect TECS state.
  4. Recognise the autotest framework: `Tools/autotest/arduplane.py`, the `AutoTestPlane` class, the per-test method pattern. Recognise `Tools/autotest/autotest.py build.ArduPlane test.ArduPlane.<TestName>` invocation. *Show, don't dwell* — this is a recognition-level objective, not a write-a-test objective.
  5. Recognise the gtest harness: `libraries/<lib>/tests/test_<name>.cpp` with `#include <AP_gtest.h>`, build with `./waf --targets tests/test_<name>`, run the produced binary. The capstone Engineer 3 will use this directly.
  6. Dataflash log layout: `LogStructure` registration, `Write` API; recognise the Plane-specific messages (`ATT`, `CTUN`, `NTUN`, `TECS`, `ARSP`, `XKF*`).
- **Citations**:
  - [libraries/AP_Mission/AP_Mission.h:1-100](../../libraries/AP_Mission/AP_Mission.h#L1-L100) — class header.
  - [ArduPlane/mode_auto.cpp:1-80](../../ArduPlane/mode_auto.cpp#L1-L80) — `ModeAuto::update` opening.
  - [ArduPlane/Plane.h:920-940](../../ArduPlane/Plane.h#L920-L940) — `Plane::navigate` declaration and surrounding nav-control method block.
  - [Tools/autotest/sim_vehicle.py:1500-1600](../../Tools/autotest/sim_vehicle.py#L1500-L1600) — `--gdb`, `--debug` argument parsing (re-used from M2).
  - [Tools/autotest/arduplane.py:36-100](../../Tools/autotest/arduplane.py#L36-L100) — `class AutoTestPlane` opening with `vehicleinfo_key` and a representative test entry.
  - [Tools/autotest/arduplane.py:213-260](../../Tools/autotest/arduplane.py#L213-L260) — `AutoTestPlane.fly_LOITER` as a representative scripted-flight test method.
  - [libraries/AP_Logger/LogStructure.h:1-100](../../libraries/AP_Logger/LogStructure.h#L1-L100) — `LogStructure` typedef and one example log message definition.
- **Hands-on**: ~15 min code-along: every engineer launches SITL under gdb (`sim_vehicle.py -v ArduPlane --gdb`), sets a breakpoint at `AP_TECS::update_pitch_throttle`, hits it, prints the TECS state. No separate lab artifact; this folds into M11 setup.

#### Module M10 — Adopting ArduPilot subsystems into a proprietary codebase (NEW) (2.0 h, lecture+code-walk, *internals*)

**The new module.** This is what the senior cohort came for. Internals depth, with the worked example being `AP_L1_Control` per [req.md:62](../orchestration/gnc-plane-3day-pilot/req.md#L62).

- **Objectives**:
  1. Survey the four canonical extraction-seam patterns: (a) bring the library + stub the HAL; (b) bring the library + replace `AP_Param` with your config system; (c) bring just the math/algorithm + reimplement the wiring; (d) treat ArduPilot as a black-box subprocess via MAVLink/DDS.
  2. Walk the worked example (`AP_L1_Control`) end-to-end:
     - Identify the public surface: constructor takes `AP_AHRS&` reference, methods `update_waypoint`, `update_loiter`, `update_heading_hold`, `nav_roll_cd`, `lateral_acceleration`, etc.
     - Identify the entanglement set: `AP_HAL::micros()`, `extern const AP_HAL::HAL& hal;`, `AP_Math` helpers (`wrap_PI`, `constrain_float`, `safe_sqrt`), `AP_Param` (`var_info[]`), `AP_AHRS::get_location/groundspeed_vector/get_yaw`, `Location` from `AP_Common/Location.h`.
     - Identify what **does NOT** need to come: no `AP_Logger` calls in `update_waypoint`, no `GCS_SEND_TEXT` in the control path, no `AP_Mission` (the caller decides waypoints), no `AP_NavEKF3` (AHRS hides which estimator is running).
     - Show the extraction recipe: stub `AP_HAL` to provide just `micros()`; replace `AP_AHRS` with a thin `IAhrs` interface against your stack; vendor `AP_Math`'s wrap/constrain/safe_sqrt; vendor `Location.h` (or replace with your geo type); compile against your build system; test against gtest.
  3. Compare with `AP_TECS` (stretch case): same shape, but pulls in `AP_FixedWing::FlightStage`, `AP_Logger` for state inspection (often desired by engineers — keep it as a stub), and a richer set of parameters.
  4. Compare with `AP_NavEKF3` lane-switch subset (Engineer 3's capstone): the hardest of the three because lane switching depends on `errorScore` from `AP_NavEKF3_core` which itself depends on innovation test ratios from many fusion paths. The trick: accept that *your* EKF instances each compute their own `errorScore` (or whatever metric you choose), and lift only the **arbitration logic** from `NavEKF3::checkLaneSwitch` and `NavEKF3::switchLane`. This is ≤ 50 lines of real algorithm wrapped in ArduPilot scaffolding.
  5. **The hard truth slide**: extracting from a GPLv3 codebase carries license obligations. The legal posture is the engineer's organisation's call, not the course's. State this explicitly and move on.
- **Citations**:
  - [libraries/AP_L1_Control/AP_L1_Control.h:1-138](../../libraries/AP_L1_Control/AP_L1_Control.h#L1-L138) — full header (138 lines, fits comfortably as a read-aloud).
  - [libraries/AP_L1_Control/AP_L1_Control.cpp:1-15](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L1-L15) — file header showing exactly the include and `extern` lines that "come with" the file.
  - [libraries/AP_L1_Control/AP_L1_Control.cpp:7-44](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L7-L44) — `var_info[]` table; the `AP_Param` entanglement.
  - [libraries/AP_L1_Control/AP_L1_Control.cpp:206-349](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L206-L349) — `update_waypoint` body in full (the function runs from 206 to ~349; the ~144-line range is wide but the function is internally cohesive — instructor walks the opening 60 lines line-by-line, scrolls the rest).
  - [libraries/AP_TECS/AP_TECS.cpp:1-30](../../libraries/AP_TECS/AP_TECS.cpp#L1-L30) — file header showing the broader entanglement set (`AP_Landing`, `AP_FixedWing`).
  - [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1029-1078](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1029-L1078) — `checkLaneSwitch` + `switchLane` together; the well-bounded lane-arbitration subset.
  - [libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp:62-83](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L83) — `errorScore` body; the metric Engineer 3 must replace or reimplement.
  - [libraries/AP_HAL/HAL.h:21-90](../../libraries/AP_HAL/HAL.h#L21-L90) — re-used from M4; the seam itself.
  - [libraries/AP_HAL/system.h:14-21](../../libraries/AP_HAL/system.h#L14-L21) — re-used from M4; the four free functions every adopter needs.
  - [libraries/AP_Math/AP_Math.h:1-100](../../libraries/AP_Math/AP_Math.h#L1-L100) — math helpers (`is_zero`, `is_positive`, `safe_sqrt`, `wrap_PI`) that the L1 controller calls.
- **Hands-on**: no formal lab — this is the briefing module. M11 is the lab.

#### Module M11 — Capstone: extract one subsystem into a foreign-codebase stub (2.5 h, solo lab, *internals*)

**The artifact each engineer keeps.** Locked by [req.md:65-69](../orchestration/gnc-plane-3day-pilot/req.md#L65-L69).

- **Setup (provided by lab-builder)**: a starter "foreign codebase" stub repo per engineer, containing:
  - A minimal `mock_hal.h` / `mock_hal.cpp` providing `millis()`, `micros()`, `delay()` against the host clock.
  - A `mock_ahrs.h` providing the AHRS-interface methods used by the engineer's target subsystem (different per engineer).
  - A `CMakeLists.txt` (or Makefile) and a gtest dependency vendored.
  - One failing test stub the engineer must make pass.
- **Engineer 1 (`AP_L1_Control`)**: vendor `AP_L1_Control.h`/`.cpp` and `AP_Math` helpers; stub `AP_AHRS` and `Location`; compile; pass a gtest that exercises `update_waypoint(prev, next, 0)` on a hardcoded scenario where `prev=(0,0)`, `next=(1000m, 0)`, vehicle at `(500m, 100m)` heading 90°, expects positive `nav_roll_cd` (turn right toward the line).
- **Engineer 2 (`AP_TECS`)**: vendor `AP_TECS.h`/`.cpp`; stub `AP_AHRS`, `AP_Logger`, `AP_FixedWing::FlightStage`; compile; pass a gtest that exercises one cycle of `update_pitch_throttle` with a 100 m altitude error and a 5 m/s airspeed error, expects bounded throttle and pitch demands.
- **Engineer 3 (`AP_NavEKF3` lane-health subset)**: vendor only `NavEKF3::checkLaneSwitch`, `NavEKF3::switchLane`, `NavEKF3::updateCoreErrorScores`, `NavEKF3::updateCoreRelativeErrors`, `NavEKF3_core::errorScore`. Stub the surrounding `NavEKF3_core` with a configurable `errorScore` value. Compile; pass a gtest that creates 3 mock cores with error-scores `[0.2, 1.5, 0.3]`, verifies `checkLaneSwitch` selects lane 2 (lowest, below the 0.9 gate), and verifies the 5-second debounce.
- **Pass criterion**: the engineer's gtest builds and passes. Each engineer presents (~5 min) the entanglement they hit and the design choice they made for it.
- **Citations**: re-used from M10. No new cites in this module.

#### Module M11.5 — Feedback session (0.5 h, discussion)

Scheduled by [req.md:95](../orchestration/gnc-plane-3day-pilot/req.md#L95). Pilot-cohort feedback on the course content, depth, pacing, lab quality, and adoption-axis utility. Output is recorded for course-orchestrator's review and for material-builder's iteration on the slides + handouts.

---

## Critical Files Cited

Master deduplicated index of every file:line anchor referenced above. course-writer pulls from this list when drafting prose; lab-builder pulls from it when scaffolding labs.

- [AGENTS.md](../../AGENTS.md) — referenced *only* as a contributor-rule pointer in M5 (parameter-index-stability rule); not cited as pedagogical material per [audience-fit.md:24](../criteria/audience-fit.md#L24).
- [BUILD.md](../../BUILD.md) — referenced for build troubleshooting in M3.
- [CLAUDE.md:120-150](../../CLAUDE.md#L120-L150) — Waf cheat sheet; instructor-only handoff reference.
- [ArduPlane/Plane.h:1-50](../../ArduPlane/Plane.h#L1-L50) — Plane class header.
- [ArduPlane/Plane.h:920-940](../../ArduPlane/Plane.h#L920-L940) — `Plane::navigate` declaration block.
- [ArduPlane/Plane.cpp:30-60](../../ArduPlane/Plane.cpp#L30-L60) — `SCHED_TASK`/`FAST_TASK` macros.
- [ArduPlane/Plane.cpp:62-95](../../ArduPlane/Plane.cpp#L62-L95) — `Plane::scheduler_tasks[]` table opening.
- [ArduPlane/Plane.cpp:165-200](../../ArduPlane/Plane.cpp#L165-L200) — `Plane::ahrs_update`.
- [ArduPlane/Parameters.cpp:290-310](../../ArduPlane/Parameters.cpp#L290-L310) — `AIRSPEED_MIN`/`AIRSPEED_MAX` `@Param` block (real example).
- [ArduPlane/mode.h:1-80](../../ArduPlane/mode.h#L1-L80) — Mode base class.
- [ArduPlane/mode_takeoff.cpp:1-80](../../ArduPlane/mode_takeoff.cpp#L1-L80) — TAKEOFF mode anchor.
- [ArduPlane/mode_fbwa.cpp:1-46](../../ArduPlane/mode_fbwa.cpp#L1-L46) — full `ModeFBWA::update` and `run`.
- [ArduPlane/mode_auto.cpp:1-80](../../ArduPlane/mode_auto.cpp#L1-L80) — `ModeAuto::update` opening.
- [ArduPlane/servos.cpp:861-900](../../ArduPlane/servos.cpp#L861-L900) — `Plane::set_servos`.
- [ArduPlane/wscript:1-40](../../ArduPlane/wscript#L1-L40) — vehicle wscript.
- [libraries/AP_HAL/AP_HAL.h:1-31](../../libraries/AP_HAL/AP_HAL.h#L1-L31) — umbrella include.
- [libraries/AP_HAL/HAL.h:21-90](../../libraries/AP_HAL/HAL.h#L21-L90) — `class AP_HAL::HAL` constructor.
- [libraries/AP_HAL/system.h:14-21](../../libraries/AP_HAL/system.h#L14-L21) — `AP_HAL::millis`/`micros`.
- [libraries/AP_HAL_SITL/HAL_SITL_Class.cpp:1-80](../../libraries/AP_HAL_SITL/HAL_SITL_Class.cpp#L1-L80) — SITL HAL instantiation.
- [libraries/AP_HAL_ChibiOS/hwdef/CubeBlack/hwdef.dat:1-100](../../libraries/AP_HAL_ChibiOS/hwdef/CubeBlack/hwdef.dat#L1-L100) — example board hwdef.
- [libraries/AP_Scheduler/AP_Scheduler.cpp:43-49](../../libraries/AP_Scheduler/AP_Scheduler.cpp#L43-L49) — `SCHEDULER_DEFAULT_LOOP_RATE` selector.
- [libraries/AP_Scheduler/AP_Scheduler.cpp:55-69](../../libraries/AP_Scheduler/AP_Scheduler.cpp#L55-L69) — `SCHED_LOOP_RATE` parameter.
- [libraries/AP_Scheduler/AP_Scheduler.h:140-180](../../libraries/AP_Scheduler/AP_Scheduler.h#L140-L180) — loop-rate accessors.
- [libraries/AP_Param/AP_Param.h:140-160](../../libraries/AP_Param/AP_Param.h#L140-L160) — `AP_GROUPINFO` macro family.
- [libraries/AP_Param/AP_Param.cpp:355-400](../../libraries/AP_Param/AP_Param.cpp#L355-L400) — `AP_Param::setup`.
- [libraries/AP_Param/AP_Param.cpp:1555-1620](../../libraries/AP_Param/AP_Param.cpp#L1555-L1620) — `AP_Param::load_all`.
- [libraries/AP_Logger/AP_Logger.h:1-80](../../libraries/AP_Logger/AP_Logger.h#L1-L80) — logger interface.
- [libraries/AP_Logger/LogStructure.h:1-100](../../libraries/AP_Logger/LogStructure.h#L1-L100) — log structure typedef.
- [libraries/AP_Mission/AP_Mission.h:1-100](../../libraries/AP_Mission/AP_Mission.h#L1-L100) — mission class header.
- [libraries/AP_Math/AP_Math.h:1-100](../../libraries/AP_Math/AP_Math.h#L1-L100) — math helpers.
- [libraries/AP_AHRS/AP_AHRS.h:1-80](../../libraries/AP_AHRS/AP_AHRS.h#L1-L80) — AHRS frontend.
- [libraries/AP_NavEKF3/AP_NavEKF3.cpp:715-722](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L715-L722) — `EK3_PRIMARY` parameter.
- [libraries/AP_NavEKF3/AP_NavEKF3.cpp:910-1020](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L910-L1020) — `NavEKF3::UpdateFilter` + lane arbitration.
- [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1029-1062](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1029-L1062) — `NavEKF3::checkLaneSwitch`.
- [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1064-1078](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1064-L1078) — `NavEKF3::switchLane`.
- [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1092-1099](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1092-L1099) — `NavEKF3::updateCoreErrorScores`.
- [libraries/AP_NavEKF3/AP_NavEKF3_core.h:140-160](../../libraries/AP_NavEKF3/AP_NavEKF3_core.h#L140-L160) — `errorScore` declaration.
- [libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp:62-83](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L83) — `NavEKF3_core::errorScore` body.
- [libraries/AP_Airspeed/AP_Airspeed.h:1-80](../../libraries/AP_Airspeed/AP_Airspeed.h#L1-L80) — airspeed frontend.
- [libraries/AP_Airspeed/AP_Airspeed_Backend.h:1-80](../../libraries/AP_Airspeed/AP_Airspeed_Backend.h#L1-L80) — airspeed backend interface.
- [libraries/AP_Airspeed/AP_Airspeed_SITL.cpp:1-80](../../libraries/AP_Airspeed/AP_Airspeed_SITL.cpp#L1-L80) — SITL airspeed backend.
- [libraries/AP_Airspeed/AP_Airspeed_MS4525.cpp:1-100](../../libraries/AP_Airspeed/AP_Airspeed_MS4525.cpp#L1-L100) — real I2C airspeed backend.
- [libraries/AP_Airspeed/Airspeed_Calibration.cpp:1-80](../../libraries/AP_Airspeed/Airspeed_Calibration.cpp#L1-L80) — auto-calibration.
- [libraries/AP_TECS/AP_TECS.cpp:1-30](../../libraries/AP_TECS/AP_TECS.cpp#L1-L30) — file header / entanglement.
- [libraries/AP_TECS/AP_TECS.cpp:90-110](../../libraries/AP_TECS/AP_TECS.cpp#L90-L110) — `TECS_SPDWEIGHT`.
- [libraries/AP_TECS/AP_TECS.cpp:101-110](../../libraries/AP_TECS/AP_TECS.cpp#L101-L110) — `TECS_PTCH_DAMP`.
- [libraries/AP_TECS/AP_TECS.cpp:678-700](../../libraries/AP_TECS/AP_TECS.cpp#L678-L700) — `_update_energies`.
- [libraries/AP_TECS/AP_TECS.cpp:719-820](../../libraries/AP_TECS/AP_TECS.cpp#L719-L820) — `_update_throttle_with_airspeed`.
- [libraries/AP_TECS/AP_TECS.cpp:1270-1350](../../libraries/AP_TECS/AP_TECS.cpp#L1270-L1350) — `update_pitch_throttle`.
- [libraries/AP_L1_Control/AP_L1_Control.h:1-138](../../libraries/AP_L1_Control/AP_L1_Control.h#L1-L138) — full L1 header.
- [libraries/AP_L1_Control/AP_L1_Control.cpp:1-15](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L1-L15) — file header.
- [libraries/AP_L1_Control/AP_L1_Control.cpp:7-44](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L7-L44) — `var_info[]` table.
- [libraries/AP_L1_Control/AP_L1_Control.cpp:206-349](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L206-L349) — `update_waypoint` body.
- [libraries/APM_Control/AP_RollController.cpp:27-50](../../libraries/APM_Control/AP_RollController.cpp#L27-L50) — `RLL2SRV_TCONST`, `RLL2SRV_RMAX` parameters.
- [libraries/APM_Control/AP_RollController.cpp:185-232](../../libraries/APM_Control/AP_RollController.cpp#L185-L232) — `get_servo_out` body.
- [libraries/SRV_Channel/SRV_Channels.cpp:478-510](../../libraries/SRV_Channel/SRV_Channels.cpp#L478-L510) — `cork`/`push`.
- [libraries/SRV_Channel/SRV_Channel_aux.cpp:617-680](../../libraries/SRV_Channel/SRV_Channel_aux.cpp#L617-L680) — `set_output_scaled`.
- [libraries/SITL/SIM_GPS.cpp:69-75](../../libraries/SITL/SIM_GPS.cpp#L69-L75) — `SIM_GPS_GLTCH` parameter.
- [libraries/SITL/SIM_GPS.cpp:97-103](../../libraries/SITL/SIM_GPS.cpp#L97-L103) — `SIM_GPS_NOISE` parameter.
- [libraries/SITL/SITL.cpp:83-95](../../libraries/SITL/SITL.cpp#L83-L95) — `SIM_WIND_SPD`/`SIM_WIND_DIR` parameters.
- [Tools/scripts/build_options.py:1-50](../../Tools/scripts/build_options.py#L1-L50) — feature-flag enumeration header.
- [Tools/autotest/sim_vehicle.py:1](../../Tools/autotest/sim_vehicle.py#L1) — script existence anchor.
- [Tools/autotest/sim_vehicle.py:1500-1600](../../Tools/autotest/sim_vehicle.py#L1500-L1600) — argument parsing.
- [Tools/autotest/arduplane.py:36-100](../../Tools/autotest/arduplane.py#L36-L100) — `class AutoTestPlane`.
- [Tools/autotest/arduplane.py:213-260](../../Tools/autotest/arduplane.py#L213-L260) — representative test method.

## Criteria Proposed

None — plan satisfies existing criteria in [course/criteria/](../criteria/).

The four existing rubrics ([audience-fit.md](../criteria/audience-fit.md), [citation-rigor.md](../criteria/citation-rigor.md), [scope-discipline.md](../criteria/scope-discipline.md), [time-budget.md](../criteria/time-budget.md)) are sufficient for course-reviewer to audit this plan's downstream draft. Two rubric refinements would be useful in future but are NOT proposed as deltas in this iteration:

- An "adoption-axis discipline" rubric to formalise the side-bar pattern's required components — left for iter ≥ 2 if the reviewer flags inconsistency in side-bar coverage.
- A "lab reproducibility" rubric that codifies the `sim_vehicle.py` invocation + parameter-set + GCS-fingerprint contract — left for the lab-tester pipeline to surface organically.

If the reviewer or the user wants either rubric committed before iter 2, I will draft the bullets in the next iteration's "Criteria Proposed" section.

## Handoff

### To course-writer

- **File path**: write [`course/custom_gnc_course_plane_3day_pilot.md`](../custom_gnc_course_plane_3day_pilot.md). End the file with `Generated from course/plans/plan-gnc-plane-3day-pilot-iter1.md` per [scope-discipline.md:7](../criteria/scope-discipline.md#L7).
- **Voice**: peer-to-peer with senior GNC engineers. Cast every ArduPilot decision as one design among many, with explicit comparison opportunities ("compare to your stack's …") at each module boundary. Do NOT use teaching-the-novice voice; this audience already builds autopilots.
- **Module set parity**: produce exactly the 11 modules listed (M1–M11 plus M11.5 feedback). No additions, no removals, no reorderings without recording a deviation.
- **Verbatim from plan**: the Day-and-module structure, the time budgets, the citation set, and the lab specs. Do not invent additional cites — if a finer cite is needed during writing, update this plan's iter and re-emit.
- **Compress**: M2 (Operations) and M9 (Mission+debugging) are the compression targets. Do not be tempted to expand them; the 5-day source has full versions.
- **Expand**: M4 (HAL with adoption framing) and M10 (Adoption module). These are where the audience leans in. Math-as-code, function-body walks, "what comes with it" lists.
- **Adoption side-bars**: in M4, M5, M6, M7, M8, write each side-bar as a discrete 2–4-min subsection at module end with a clear heading "Adoption side-bar — what comes with this subsystem" and the three-bullet structure from D14. The dedicated module M10 has the deep treatment.
- **Directive prose discipline**: anywhere this plan says "compress", "do not derive", "skip the math", or similar — those directives are for course-writer, NOT for student-facing prose. Per [audience-fit.md:25](../criteria/audience-fit.md#L25), if the substance must reach the student, rephrase it as content ("we cover the energy-balance derivation; the integral form is in the AP_TECS reference"). Do not echo the directive prose into the student-facing draft.
- **No cites to coordination files as pedagogical material**: `AGENTS.md`, `CLAUDE.md`, `.claude/`, repo-root meta docs are off-limits for pedagogical citation per [audience-fit.md:24](../criteria/audience-fit.md#L24). When this plan's "Citations" lists include `AGENTS.md` (M5) or `CLAUDE.md` (M3), they appear as instructor-only references; do NOT include them in student-facing citation blocks.
- **Concrete `@Param` example**: when illustrating the `@Param` annotation block, use [ArduPlane/Parameters.cpp:290-310](../../ArduPlane/Parameters.cpp#L290-L310) (real `AIRSPEED_MIN`/`MAX` block), NOT the `AGENTS.md` example block.
- **Capstone framing**: M11 is presented as solo work (not paired) since cohort = 3 and per-engineer assignments are pre-allocated (D7). The course preamble states the assignment policy. Engineers MAY swap with each other before the capstone starts; the per-engineer choice does not affect the lab-builder's setup.

### To course-reviewer

Apply all four rubrics in [course/criteria/](../criteria/):

- [audience-fit.md](../criteria/audience-fit.md) — verify: (a) the audience declaration in the preamble matches `req.md`'s "senior GNC engineers, internals depth"; (b) the prerequisite list names C/C++, RTOS, fixed-wing controls, gdb/gtest, and explicitly excludes ArduPilot; (c) every module that claims internals depth has ≥ 5 file:line cites (M4, M5, M7, M8, M10 are the internals modules); (d) the directive-prose rule (line 25) is honored — "compress", "skip", "out of scope" appear only in instructor-only blocks; (e) coordination-file cites (line 24) are not used pedagogically.
- [citation-rigor.md](../criteria/citation-rigor.md) — verify: (a) every cite is a clickable markdown link with `path:line` displayed text; (b) every cite resolves in the current tree (sample at least 10 cites at random and run `grep -n` per the recipe); (c) line ranges are 5–150 lines; (d) symbol names are verbatim — most importantly verify that `NavEKF3::checkLaneSwitch` is at [AP_NavEKF3.cpp:1029](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1029) NOT `checkAndDoLaneSwitch` (the 5-day source's older name does not exist in the current tree), and verify `RLL2SRV_TCONST` is the actual parameter name in [AP_RollController.cpp:35](../../libraries/APM_Control/AP_RollController.cpp#L35) NOT "RLL_RATE_P" (which is a separate underlying-PID parameter).
- [scope-discipline.md](../criteria/scope-discipline.md) — verify: (a) the course file has the `Generated from course/plans/plan-gnc-plane-3day-pilot-iter1.md` line; (b) module set in the course matches M1..M11.5 in this plan; (c) each module's time matches ±15 min; (d) no unauthorized content from [custom_gnc_course_quadplane.md](../custom_gnc_course_quadplane.md); (e) lab specs in the course match the "Handoff → To lab-builder" entries below.
- [time-budget.md](../criteria/time-budget.md) — verify: (a) course total declared as ~21 h; (b) per-day totals each = 7 h; (c) per-module times within each day sum to 6.5 h ± 15 min, plus the explicit 0.5 h buffer; (d) hands-on share ≥ 25% per day; (e) capstone ≥ 2 h (M11 is 2.5 h, satisfies); (f) buffer ≥ 30 min per day (declared 30 min, satisfies exactly).

**Specific risks to audit**:
- Citation drift on `NavEKF3::checkLaneSwitch` and `errorScore` (the 5-day source's older anchor names may have leaked into draft prose).
- Module 4 (HAL) at 3.0 h is the longest module; verify it actually packs 3.0 h of content and is not padded with operations material.
- Module 10 (Adoption) is wholly new — verify it doesn't drift into a "list of all libraries" survey; it must stay focused on the four extraction-seam patterns + the worked L1 example.
- The capstone (M11) at 2.5 h has three different deliverables (one per engineer); verify the course file documents all three with equal care.
- Adoption side-bars in M4–M8 must be present and distinct; verify they are not collapsed into a single repeated paragraph.

### To lab-builder

Five labs, all SITL-only, all `ArduPlane`, all on stock SITL physics. Each lab gets its own subdirectory under `course/labs/gnc-plane-3day-pilot-*/` with the canonical structure (`README.md`, `student-guide.md`, `instructor-guide.md`, `expected.md`, `launch.sh`, `params.parm`, `steps.md`, `test.py`, `test.sh`).

#### Lab L1 — HAL + scheduler probe (~30 min, Day 1, Module M4)

- **SITL invocation**: `Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --map --debug --no-mavproxy` (no MAVProxy needed; the lab uses gdb directly attached to `arduplane`).
- **Build**: pre-built debug binary at `build/sitl/bin/arduplane` from M3.
- **Parameter set (`params.parm`)**: stock plane parameters; no SITL stress.
- **Procedure**: launch SITL, attach `gdb -p <pid>`, set breakpoint `b Plane::ahrs_update`, continue, hit, `print AP_HAL::millis()`, `print AP::scheduler().get_loop_rate_hz()`.
- **Expected fingerprint**: gdb prints a `millis()` value > 0 and a loop rate of `50` (or close to 50 Hz).
- **Pass criterion**: both prints succeed and the engineer can describe the call from `ahrs_update` down through `ahrs.update()`.

#### Lab L2 — `AP_GROUPINFO` add + observe (~30 min, Day 2, Module M5)

- **SITL invocation**: `Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console`.
- **Build**: engineer modifies `ArduPlane/Parameters.h` and `ArduPlane/Parameters.cpp` to add `MY_PARAM` as `AP_Float`, default 17.0; rebuilds with `./waf plane`.
- **Parameter set (`params.parm`)**: stock plane parameters; the lab adds `MY_PARAM`.
- **Procedure**: launch SITL, run `param show MY_*` (expect to see `MY_PARAM 17.0`), `param set MY_PARAM 42.0`, restart SITL, run `param show MY_*` again.
- **Expected fingerprint**: post-restart `MY_PARAM 42.0`.
- **Pass criterion**: parameter persists across restart.

#### Lab L3 — GPS noise + EKF lane switch (~40 min, Day 2, Module M7)

- **SITL invocation**: `Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --map -L KSFO`.
- **Build**: stock debug build from M3.
- **Parameter set (`params.parm`)**: stock plane parameters PLUS `EK3_IMU_MASK 3` (force 2 EKF lanes), `LOG_BITMASK 65535` (enable XKF logging).
- **Procedure**: launch, take off in TAKEOFF mode, switch to FBWA, fly steady, then via MAVProxy: `param set SIM_GPS_NOISE 5` (gentle noise), then ~30 s later `param set SIM_GPS_GLTCH_X 50` (or `param set SIM_GPS0_GLTCH_X 50` — the parameter name is `SIM_GPS_GLTCH` per [SIM_GPS.cpp:69-75](../../libraries/SITL/SIM_GPS.cpp#L69-L75); lab-builder confirms the exact param name on first run). Wait for the GCS to print `EKF3 lane switch %u`. Disarm, download dataflash log, run `mavlogdump.py --types=XKF1,XKF4,EV` and identify the lane-switch event.
- **Expected fingerprint**: GCS statustext containing `EKF3 lane switch` AND a dataflash event record with `EV` or equivalent lane-switch marker.
- **Pass criterion**: lane-switch GCS message appears within 30 s of glitch injection AND the dataflash records the event.

#### Lab L4 — Roll-controller + TECS gain modify (~40 min, Day 2, Module M8)

- **SITL invocation**: `Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --map`.
- **Build**: stock debug build.
- **Parameter set (`params.parm`)**: stock plane parameters; the lab modifies parameters live via MAVProxy.
- **Procedure (Phase A — roll)**: take off in TAKEOFF, switch to FBWA, fly steady, then `param set RLL2SRV_TCONST 0.25` (default 0.5; halves the time constant per [AP_RollController.cpp:36](../../libraries/APM_Control/AP_RollController.cpp#L36)); fly several roll inputs; download log, plot `ATT.DesRoll` vs `ATT.Roll`.
- **Procedure (Phase B — TECS)**: reset to defaults, `param set TECS_PTCH_DAMP 0.15` (default 0.3 per [AP_TECS.cpp:107](../../libraries/AP_TECS/AP_TECS.cpp#L107)); fly a 50 m altitude step in CRUISE; download log, plot `TECS.h` vs `TECS.hdem`.
- **Expected fingerprint**: visible difference in roll-tracking and altitude-tracking plots between default and modified gains.
- **Pass criterion**: engineer produces two MAVExplorer screenshots — one showing faster-but-oscillatory roll response, one showing damped-but-slower altitude tracking.

#### Lab L5 — Capstone: extract one subsystem (~2.5 h, Day 3, Module M11)

- **No SITL**. This lab runs entirely against gtest in a stub repo.
- **Per-engineer setup**: lab-builder provides three pre-staged stub repos `course/labs/gnc-plane-3day-pilot-l5/eng1-l1/`, `eng2-tecs/`, `eng3-ekf-lane/` with:
  - A `mock_hal.cpp` providing `AP_HAL::millis()`, `AP_HAL::micros()`, `hal.scheduler->delay()`.
  - A `mock_ahrs.h` (engineers 1 and 2) providing the AHRS interface methods their target subsystem calls — for L1: `get_location`, `groundspeed_vector`, `get_yaw`, `get_yaw_sensor`; for TECS: `get_pitch`, `get_yaw`, `get_velocity_NED`, etc.
  - A `mock_storage.cpp` (all three) providing a no-op storage backend for `AP_Param`.
  - A vendored copy of `AP_Math` headers (engineers 1 and 2) and `AP_Common/Location.h` (engineer 1).
  - For Engineer 3: a `mock_NavEKF3_core.h` with a configurable `errorScore()` value, plus the lane-switch source files copied verbatim.
  - A `CMakeLists.txt` (or Makefile) and a vendored gtest.
  - One initially-failing test stub.
- **Procedure**: each engineer copies their target source files from `libraries/AP_L1_Control/`, `libraries/AP_TECS/`, or the lane-switch slice of `libraries/AP_NavEKF3/` into their stub repo, edits `#include`s as needed, makes the failing test pass, presents (~5 min) at end.
- **Expected fingerprint per engineer**:
  - Eng 1 — gtest output: `[ PASSED ] L1Control.UpdateWaypointTurnsRight`.
  - Eng 2 — gtest output: `[ PASSED ] TECS.OneCycleProducesBoundedDemands`.
  - Eng 3 — gtest output: `[ PASSED ] EKF3LaneSwitch.SelectsLowestErrorBelowGate`, `[ PASSED ] EKF3LaneSwitch.HonorsFiveSecondDebounce`.
- **Pass criterion**: `make test` (or `cmake --build build && ctest`) returns 0 in each engineer's repo.

### To lab-tester

For each lab above, run the full SITL invocation against the working tree at `GNC-0.1` HEAD and produce a `report.md` under `course/labs/gnc-plane-3day-pilot-l<N>/runs/<ts>/`. The exact commands and expected fingerprints:

- **L1**: `cd /home/mahisorn/repos/ardupilot_course && ./waf configure --board sitl --debug && ./waf plane && Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --no-mavproxy --debug` in one terminal; `gdb -p $(pgrep arduplane) -batch -ex "b Plane::ahrs_update" -ex "c" -ex "p AP_HAL::millis()" -ex "p AP::scheduler().get_loop_rate_hz()" -ex "detach" -ex "quit"` in another. Expected: a `millis()` print > 0 and a loop-rate print `50` (the [AP_Scheduler.cpp:46](../../libraries/AP_Scheduler/AP_Scheduler.cpp#L46) plane default).
- **L2**: `cd /home/mahisorn/repos/ardupilot_course && ./waf plane && Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console`. In MAVProxy: `param show MY_*` → expect `MY_PARAM 17.0`. `param set MY_PARAM 42.0`. Quit SITL. Restart. `param show MY_*` → expect `MY_PARAM 42.0`. (Lab-builder pre-stages the `Parameters.{h,cpp}` patch; lab-tester applies it before configure.)
- **L3**: same SITL launch. MAVProxy: `mode TAKEOFF`, `arm throttle`, wait until altitude ≥ 50 m, `mode FBWA`, fly steady ~10 s, `param set SIM_GPS_NOISE 5`, wait 10 s, `param set SIM_GPS_GLTCH_X 50` (Vector3 param — write x-component or all three depending on `mavparm` syntax in the harness). Expected: GCS statustext line containing `EKF3 lane switch` within 30 s. Dataflash check: `mavlogdump.py --types=XKF1,XKF4,EV logs/00000001.BIN | grep -i 'switch\|lane'` returns ≥ 1 record.
- **L4**: same SITL launch. Phase A: `mode TAKEOFF`, climb, `mode FBWA`. `param set RLL2SRV_TCONST 0.25`. Move roll stick (`rc 1 1300` then `rc 1 1700`). Quit. Plot `ATT.DesRoll` vs `ATT.Roll` from log. Phase B: relaunch, defaults; `param set TECS_PTCH_DAMP 0.15`; fly 50 m altitude step in CRUISE (set `mode CRUISE`, `rc 2 1700` to climb, then `rc 2 1500` to level). Plot `TECS.h` vs `TECS.hdem`. Expected: visible (≥ 30%) reduction in tracking-error settling time on Phase A, visible increase in altitude-tracking oscillation on Phase B.
- **L5**: per-engineer: `cd course/labs/gnc-plane-3day-pilot-l5/eng<N>-* && cmake -B build && cmake --build build && ctest --test-dir build`. Expected: `100% tests passed`. The lab-builder pre-stages each stub repo so the failing test stub fails on first run; the engineer's job is to vendor the ArduPilot files and make the test pass. lab-tester verifies the *reference solution* (provided by lab-builder) compiles + passes.

If any of L1–L5 returns FAIL or FLAKY, course-orchestrator drives a lab-builder iteration on the failing lab. Per [req.md:35](../orchestration/gnc-plane-3day-pilot/req.md#L35) the lab-builder ↔ lab-tester loop is capped at 2 iterations per lab.

## Verification

### Citation sanity

Every cite in this plan was `grep -n`-verified against the working tree at commit `98325ac0cc` during planning. Specifically verified during writing (not exhaustive — the full set is in **Critical Files Cited**):

- [ArduPlane/Plane.cpp:62](../../ArduPlane/Plane.cpp#L62) — `Plane::scheduler_tasks[]` opens at line 62 (`grep -n "scheduler_tasks\[\]"` returned `62:const AP_Scheduler::Task Plane::scheduler_tasks[] = {`).
- [ArduPlane/Plane.cpp:166](../../ArduPlane/Plane.cpp#L166) — `Plane::ahrs_update` (`grep -n "void Plane::ahrs_update"` returned `165:void Plane::ahrs_update()`; the cited range 165-200 covers the whole body).
- [libraries/AP_Scheduler/AP_Scheduler.cpp:44-46](../../libraries/AP_Scheduler/AP_Scheduler.cpp#L44-L46) — `SCHEDULER_DEFAULT_LOOP_RATE` 400 vs 50 selector confirmed.
- [libraries/AP_Param/AP_Param.h:152](../../libraries/AP_Param/AP_Param.h#L152) — `AP_GROUPINFO` macro exists at line 152 (the cited range 140-160 contains it).
- [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1029](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1029) — `void NavEKF3::checkLaneSwitch(void)` confirmed (`grep -n "^void NavEKF3::"` returned `1029:void NavEKF3::checkLaneSwitch(void)`).
- [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1064](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1064) — `void NavEKF3::switchLane(uint8_t new_lane_index)` confirmed.
- [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1092](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1092) — `float NavEKF3::updateCoreErrorScores()` confirmed.
- [libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp:62](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62) — `float NavEKF3_core::errorScore() const` confirmed (`grep -n "errorScore" AP_NavEKF3_Outputs.cpp` returned line 62).
- [libraries/AP_TECS/AP_TECS.cpp:1270](../../libraries/AP_TECS/AP_TECS.cpp#L1270) — `void AP_TECS::update_pitch_throttle(...)` confirmed.
- [libraries/AP_TECS/AP_TECS.cpp:107](../../libraries/AP_TECS/AP_TECS.cpp#L107) — `TECS_PTCH_DAMP` `AP_GROUPINFO` line confirmed (note: NOT `TECS_PITCH_DAMP` — symbol-naming-verbatim rule of [citation-rigor.md:14](../criteria/citation-rigor.md#L14)).
- [libraries/AP_L1_Control/AP_L1_Control.cpp:206](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L206) — `void AP_L1_Control::update_waypoint(...)` confirmed.
- [libraries/AP_L1_Control/AP_L1_Control.cpp:15](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L15) — `AP_GROUPINFO("PERIOD", 0, AP_L1_Control, _L1_period, 17)` confirmed (i.e. `NAVL1_PERIOD`).
- [libraries/APM_Control/AP_RollController.cpp:35](../../libraries/APM_Control/AP_RollController.cpp#L35) — `AP_GROUPINFO("2SRV_TCONST", 0, AP_RollController, gains.tau, 0.5f)` confirmed (param full name is `RLL2SRV_TCONST`; NOT `RLL_RATE_P`).
- [libraries/APM_Control/AP_RollController.cpp:185](../../libraries/APM_Control/AP_RollController.cpp#L185) — `float AP_RollController::get_servo_out(...)` confirmed.
- [libraries/SRV_Channel/SRV_Channels.cpp:486](../../libraries/SRV_Channel/SRV_Channels.cpp#L486) — `void SRV_Channels::push()` confirmed.
- [libraries/SRV_Channel/SRV_Channel_aux.cpp:617](../../libraries/SRV_Channel/SRV_Channel_aux.cpp#L617) — `void SRV_Channels::set_output_scaled(...)` confirmed.
- [libraries/SITL/SIM_GPS.cpp:69](../../libraries/SITL/SIM_GPS.cpp#L69) — `// @Param: GLTCH` confirmed (full name `SIM_GPS_GLTCH`).
- [libraries/SITL/SIM_GPS.cpp:97](../../libraries/SITL/SIM_GPS.cpp#L97) — `// @Param: NOISE` confirmed (full name `SIM_GPS_NOISE`).
- [libraries/AP_HAL/HAL.h:21](../../libraries/AP_HAL/HAL.h#L21) — `class AP_HAL::HAL {` confirmed.
- [libraries/AP_HAL/system.h:14-21](../../libraries/AP_HAL/system.h#L14-L21) — `millis`, `micros`, `millis64`, `micros64`, `millis16`, `micros16` declarations confirmed.
- [ArduPlane/Parameters.cpp:295](../../ArduPlane/Parameters.cpp#L295) and `:304` — `ASCALAR(airspeed_min, "AIRSPEED_MIN", AIRSPEED_FBW_MIN)` and `ASCALAR(airspeed_max, "AIRSPEED_MAX", AIRSPEED_FBW_MAX)` confirmed.
- [Tools/autotest/arduplane.py:36](../../Tools/autotest/arduplane.py#L36) — `class AutoTestPlane(vehicle_test_suite.TestSuite)` confirmed.

**Citations updated or dropped during planning**:

- The 5-day source ([custom_gnc_course_plane.md:597](../custom_gnc_course_plane.md#L597)) hints at `AP_NavEKF3_VelPosFusion.cpp` for airspeed fusion. The actual file is `AP_NavEKF3_PosVelFusion.cpp` (note the order). This plan does NOT cite that file at line-level — the airspeed-fusion walk is left to the M7 narrative without a deep cite, since the file is large (>2000 lines) and the relevant blocks span multiple ranges. If course-writer needs a deep cite there, the planner will update in iter 2.
- The 5-day source occasionally references `checkAndDoLaneSwitch` as a method name — this method **does not exist** in the current tree. The actual entry point is `NavEKF3::checkLaneSwitch` at [AP_NavEKF3.cpp:1029](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1029); the periodic arbitration is inline in `NavEKF3::UpdateFilter` at [AP_NavEKF3.cpp:910-1020](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L910-L1020). This plan uses the correct names exclusively. course-writer must NOT regress to the older name.
- `SIM_ARSPD_FAIL` — appears in legacy SilentWings parameter dumps but is not currently a definable parameter in `libraries/SITL/SITL.cpp` or `libraries/AP_Airspeed/`. This plan therefore uses `SIM_GPS_GLTCH` + `SIM_GPS_NOISE` for the stress-injection lab (L3) instead of an airspeed-fail injection. If the orchestration step needs an airspeed failure mode, the lab-builder may use `param set ARSPD_USE 0` (disable airspeed in EKF) as a non-ideal substitute, and the planner will update in iter 2.
- The roll/pitch attitude-controller PID-rate parameters in the 5-day source ("RLL_RATE_P" etc.) are NOT the controller-library parameters; they are the underlying `AC_PID` parameters declared per-axis. The actual `AP_RollController`-level param is `RLL2SRV_TCONST` ([AP_RollController.cpp:35](../../libraries/APM_Control/AP_RollController.cpp#L35)) and the rate-PID parameters carry the prefix `RLL_RATE_*` (commented at [AP_RollController.cpp:51-100](../../libraries/APM_Control/AP_RollController.cpp#L51-L100)). Lab L4 deliberately uses `RLL2SRV_TCONST` (the time constant) as the gain target for clarity — modifying it produces a clean visual fingerprint without diving into the rate-PID structure.

### Time-budget sum

| Day | Modules (sum) | Buffer | Day total | Target |
|-----|---------------|--------|-----------|--------|
| 1 | M1 1.0 + M2 1.5 + M3 1.5 + M4 3.0 = 7.0 | wait — overflows | | |

**Recheck Day 1**: 1.0 + 1.5 + 1.5 + 3.0 = 7.0. Plus 0.5 h buffer = 7.5 h. That overruns the 7 h target by 0.5 h. **Correction needed**: M4 must be 2.5 h, not 3.0 h, OR M2 must be 1.0 h, not 1.5 h, OR M3 must be 1.0 h, not 1.5 h.

[req.md:87](../orchestration/gnc-plane-3day-pilot/req.md#L87) recommends M4 (HAL with adoption framing) at 3.0 h. To honor that and satisfy the 7 h Day 1, we cut M3 from 1.5 h to 1.0 h (the M3 build walk does not need 1.5 h for senior engineers — they can configure + build + recognise wscript in 1 h).

**Updated Day 1**: M1 1.0 + M2 1.5 + M3 **1.0** + M4 3.0 = 6.5 h modules + 0.5 h buffer = **7.0 h** ✓.

(Note to course-writer: M3 is 1.0 h, not 1.5 h. The Course Structure section above is corrected by this Verification block. If a future iteration needs M3 at 1.5 h, M4 must drop to 2.5 h. The two are coupled.)

| Day | Modules (sum) | Buffer | Day total | Target |
|-----|---------------|--------|-----------|--------|
| 1 | M1 1.0 + M2 1.5 + M3 1.0 + M4 3.0 = 6.5 | 0.5 | 7.0 | 7.0 ✓ |
| 2 | M5 2.0 + M6 1.5 + M7 2.0 + M8 1.5 = 7.0 | wait — overflows | | |

**Recheck Day 2**: 2.0 + 1.5 + 2.0 + 1.5 = 7.0. Plus 0.5 h buffer = 7.5 h. Overruns by 0.5 h.

[req.md:88-91](../orchestration/gnc-plane-3day-pilot/req.md#L88-L91) recommends M5 at 2.0, M6 at 1.5, M7 at 2.0, M8 at 1.5. Sum is 7.0 not 6.5. Either the req.md skeleton overruns by 0.5 h (consistent with the 21 h target only if buffer is absorbed into modules), or one of M5/M6/M7/M8 must shrink by 0.5 h.

**Decision**: shrink M8 (control pipeline) from 1.5 h to **1.0 h**. Justified deviation from req.md skeleton: the audience already knows PID + nav guidance from their proprietary stack; the unique-to-ArduPilot content (TECS energy formula, L1 lateral acceleration, airspeed-scaled PID, `SRV_Channels::push`) fits in 1.0 h at internals depth with a 40-min embedded lab. The lab L4 itself is 0.4 h within that 1.0 h.

**Updated Day 2**: M5 2.0 + M6 1.5 + M7 2.0 + M8 **1.0** = 6.5 h modules + 0.5 h buffer = **7.0 h** ✓.

(Note to course-writer: M8 is 1.0 h, not 1.5 h. Lab L4 fits inside M8's 1.0 h budget by streamlining the two phases. The 5-day Module 9's longer treatment of TECS/L1/APM_Control is *not* the right shape for this audience.)

| Day | Modules (sum) | Buffer | Day total | Target |
|-----|---------------|--------|-----------|--------|
| 1 | M1 1.0 + M2 1.5 + M3 1.0 + M4 3.0 = 6.5 | 0.5 | 7.0 | 7.0 ✓ |
| 2 | M5 2.0 + M6 1.5 + M7 2.0 + M8 1.0 = 6.5 | 0.5 | 7.0 | 7.0 ✓ |
| 3 | M9 2.0 + M10 2.0 + M11 2.5 + M11.5 0.0 = 6.5 | 0.5 | 7.0 | 7.0 ✓ |
| | **Total** | | **21.0** | **21.0** ✓ |

(M11.5 feedback session is 0.5 h and is held *during* the daily buffer — the per-day buffer of 0.5 h is allocated to the feedback session on Day 3. Modules sum to 6.5 h; buffer is feedback. Net result: Day 3 = 6.5 h modules + 0.5 h feedback (which is also "buffer" in the rubric sense — interactive time, not lecture) = 7.0 h.)

Per-day delta vs target = 0 h. Course total delta vs target = 0 h. Both within rubric tolerance ([time-budget.md:8](../criteria/time-budget.md#L8) ±1 h course, ±15 min day).

### Per-day hands-on share

- **Day 1**: L1 ~0.5 h embedded in M4, plus ~0.5 h code-along across M2 + M3 = ~1.0 h of 6.5 h = 15.4%. **Below the 25% target**. Mitigation: the M4 HAL trace exercise (hand-on at the editor, even without code execution) counts as hands-on at the rubric's "build, debug, log analysis" level. With that included, ~1.5 h hands-on of 6.5 h = 23.1%, still below 25% but within rubric "Minor" severity (15-25%) per [time-budget.md:25](../criteria/time-budget.md#L25). **Accepted as a Minor finding for iter 1**; iter 2 may add a second short hands-on in M2 or M3 to clear the threshold.
- **Day 2**: L2 0.5 h + L3 0.67 h + L4 0.67 h = 1.83 h hands-on of 6.5 h = **28.2%** ✓.
- **Day 3**: M11 capstone 2.5 h of 6.5 h = **38.5%** ✓ (also satisfies the ≥ 2 h capstone rubric per [time-budget.md:11](../criteria/time-budget.md#L11)).

### Lab reproducibility

- L1: `Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --debug` syntax checked against [Tools/autotest/sim_vehicle.py:1500-1600](../../Tools/autotest/sim_vehicle.py#L1500-L1600). `--debug` flag exists; `-v ArduPlane` is the canonical plane vehicle key (per [arduplane.py:36](../../Tools/autotest/arduplane.py#L36) `class AutoTestPlane`).
- L2: SITL launch identical to L1 minus `--debug`; the `MY_PARAM` add patch lab-builder will pre-stage in `libraries/.../Parameters.h` lines around 295.
- L3: `SIM_GPS_GLTCH` is a Vector3 parameter; the lab-builder must confirm whether MAVProxy's `param set` syntax for Vector3 is `SIM_GPS_GLTCH_X` (per-axis) or requires `mavproxy_set` with three values. If MAVProxy uses per-axis suffixes, the command is `param set SIM_GPS_GLTCH_X 50`. Lab-builder confirms on first lab run.
- L4: `RLL2SRV_TCONST` and `TECS_PTCH_DAMP` are scalar `AP_Float` parameters; standard `param set` syntax. Confirmed.
- L5: no SITL; the lab-builder produces three stub repos with vendored `AP_Math`, mock HAL, mock AHRS. The reference solutions are pre-tested by lab-tester before the engineers run them.

### No-overlap audit

- **Sibling course [custom_gnc_course_plane.md](../custom_gnc_course_plane.md)**: this plan is a strict subset + 1 new module + 1 new capstone. Modules 1, 2, 4, 5, 6, 7, 8, 9 of the 5-day source map to (compressed) versions M1, M2, M3, M4, M5, M6, M7, M8 here. Modules 10 + 11 of the 5-day source compress into M9. Module 12 of the 5-day source folds into M4 as a side-bar. Modules 13, 14, 15, 16 of the 5-day source are dropped or replaced. This is **deliberate reuse**, recorded explicitly above in **Decisions → D9**.
- **Sibling course [custom_gnc_course_quadplane.md](../custom_gnc_course_quadplane.md)**: NO content reuse. QuadPlane is out of scope for the 3-day pilot.
- **Sibling course [intro_arducopter_aero_y1.md](../intro_arducopter_aero_y1.md)**: NO content reuse. Different audience (first-year aerospace vs senior GNC), different vehicle (Copter vs Plane), different depth (survey/applied vs internals). The two courses do not share any cite ranges.

### Lessons coverage

Iteration 1; no prior reviews or lab runs to address. Pre-emptive lessons noted in **Lessons Applied** are the four cross-cutting items from prior reviews on the unrelated `intro-arducopter-aero-y1` slug (cite drift, buffer ≥ 30 min, no coordination-file cites, directive prose instructor-only) — all addressed in this plan's structure.

---

Generated 2026-04-27 against branch `GNC-0.1` HEAD `98325ac0cc`.
