# Course requirements: gnc-plane-3day-pilot (locked 2026-04-27)

## Identity
- slug: `gnc-plane-3day-pilot`
- course type: greenfield (new file; do NOT edit `course/custom_gnc_course_plane.md`)
- target deliverable: `course/custom_gnc_course_plane_3day_pilot.md`
- iteration of orchestration run: 1
- driven by: parent session (course-orchestrator agent's runtime in this environment did not expose `Agent`/`AskUserQuestion`; parent session executes the orchestrator contract verbatim)

## Audience & length
- audience: senior GNC engineers — small pilot cohort. C/C++ proficient, experienced flight-code developers on a proprietary stack, no prior ArduPilot exposure.
- prior knowledge:
  - Strong embedded C/C++, RTOS, fixed-wing controls.
  - Familiar with EKFs, attitude controllers, energy controllers, lateral path-following on a proprietary in-house stack.
  - Comfortable with gdb, gtest-style unit testing, and reading large unfamiliar C++ codebases.
  - Zero ArduPilot-specific knowledge.
- vehicle: Plane (ArduPlane, fixed-wing).
- length: 3 days, 7h teaching/day = 21h total.
- format: in-person.
- depth: internals (math-as-code; EKF lane switch, TECS energy controller as code, L1 lateral controller as code, transition state machines where directly relevant).

## Hardware & labs
- hardware target: SITL only (no real boards in this pilot).
- group size: 3 engineers — solo capstones, 1:1 instructor time during labs.
- lab depth: standard — one lab per module that has hands-on (HAL trace, parameter add, EKF stress, FBWA modify, capstone extraction).

## Outputs
- emit course markdown: yes (`course/custom_gnc_course_plane_3day_pilot.md`).
- emit labs: yes (`course/labs/gnc-plane-3day-pilot-*/`).
- emit materials: yes (slides + student handout + instructor handout + per-lab guides under `course/materials/gnc-plane-3day-pilot/`).

## Pass policy
- min review verdict to advance: PASS-WITH-FIXES.
- max planner-writer-reviewer iterations: 3.
- max lab-builder-lab-tester iterations per lab: **10** (raised from 2 by user 2026-04-27 mid-run; user directive: "try harder to finish everything").
- total subagent invocation cap: **effectively uncapped for the rest of this run** (raised by user 2026-04-27 mid-run; pipeline must drive labs to PASS within the per-lab cap of 10, no further cap-hit prompts unless per-lab cap of 10 is itself exhausted).

## Source artifacts referenced
- design baseline: `course/custom_gnc_course_plane.md` (1331 lines, 5-day Plane curriculum). The 3-day pilot is a strict subset of this course's structure, NOT a different course. Use Appendix B (key files by module), Appendix C (Copter↔Plane library mapping) and Appendix E (customer-requirements traceability) as the citation backbone.
- sibling course: `course/custom_gnc_course_quadplane.md` (do NOT pull content from this; QuadPlane is out of scope for the 3-day pilot).
- prior plans / reviews: none for this slug (iter 1).

## Locked at
- date: 2026-04-27
- branch: `GNC-0.1`
- commit: `98325ac0cc`

---

## Special instruction to course-planner — adoption axis (binding)

The 3-day pilot diverges from `course/custom_gnc_course_plane.md` on **one explicit pedagogical axis** that the planner MUST honor:

> Senior engineers want to **adopt selected ArduPilot subsystems into their own proprietary (non-ArduPilot) flight stack**. This is distinct from "port ArduPilot to a custom board" (Module 12 in the 5-day source, which keeps ArduPilot as the host). The new angle is **algorithm/library extraction**: vendoring a portion of `AP_NavEKF3`, `AP_TECS`, `AP_L1_Control`, `AP_Param`, or the HAL-boundary pattern into a foreign codebase.

### Concrete planner guidance

1. **One dedicated module** (target ~2h on Day 3) titled along the lines of *"Adopting ArduPilot subsystems into a proprietary codebase"*. It must cover:
   - HAL boundary (`libraries/AP_HAL/`) as an extraction seam.
   - Parameter-system reusability (`AP_Param` + `AP_GROUPINFO` macros) and its dependencies.
   - What bleeds across libraries when you try to lift a subsystem: singletons, `extern const AP_HAL::HAL& hal;`, `GCS_SEND_TEXT`, `AP_Logger` calls, scheduler ticks, `is_zero()`/`is_positive()`/`safe_sqrt()` from `AP_Math`, the param tree, `AP_HAL::millis()`/`AP_HAL::micros()`.
   - A worked example walking through extracting one subsystem. **Recommend `AP_L1_Control` as the worked example** (smaller and more self-contained than `AP_TECS` or `AP_NavEKF3`; the file is `libraries/AP_L1_Control/AP_L1_Control.cpp`/`.h`). `AP_TECS` may be used as a stretch case if time allows.

2. **Recurring "adoption side-bar"** in Modules 5–9 (HAL, infrastructure, sensors, EKF, control). Every code walk in those modules should call out **dependency entanglement** explicitly: "if you wanted to lift this into a non-ArduPilot codebase, here's what comes with it." Make this a recurring 2–4 minute side-bar at the end of each code walk, not a single concentrated module.

3. **Capstone in Day 3 final slot** (~2.5h): each engineer (solo since group = 3) extracts one ArduPilot library into a stub of a foreign codebase and gets it to compile against a mock HAL. This is the artifact each engineer keeps and shows their team. Suggested extractions:
   - Engineer 1: `AP_L1_Control` (lateral path-following).
   - Engineer 2: `AP_TECS` (energy controller for altitude+airspeed).
   - Engineer 3: a `AP_NavEKF3` lane-health subset (NOT the full EKF — too large; just the lane-switch arbitration logic in `AP_NavEKF3_core::checkAndDoLaneSwitch()` and friends).

### Drop or compress vs the 5-day source

The 3-day pilot is content-dense. Cut, do not just compress:
- **Drop** Day 5 of the 5-day source entirely (Module 14 integration project, Module 15 Pegasus, Module 16 advanced workshop). Capstone in the new Day 3 supersedes the integration project.
- **Drop** Module 13 (Lua scripting) — not on the adoption critical path. Mention in passing in the Module 1 ecosystem overview.
- **Compress** Module 2 (operations essentials) to ~1.5h — just enough to drive SITL for code-walk demos. The audience already operates a proprietary autopilot; they do not need the full GCS/MAVProxy/mission-planning fluency the 5-day course teaches.
- **Compress** Module 12 (board porting) — covered tangentially through the HAL boundary discussion. Do not allocate a standalone module; the adoption-axis module replaces it for this audience.
- **Trim** Module 10 (mission/navigation) and Module 11 (debugging) into a single 2h block on Day 3 — the audience has equivalent debugging fluency on their proprietary stack and only needs ArduPilot-specific tooling (autotest framework, dataflash log layout, gtest harness).

### Recommended 3-day skeleton (planner may revise but must justify deviations)

| Day | Time | Module | Mapped to 5-day source |
|---|---|---|---|
| 1 | 1.0h | M1: Overview & Ecosystem (compressed) | 5-day Module 1 (1.5h → 1h) |
| 1 | 1.5h | M2: Operations Essentials (compressed for code-walk readiness only) | 5-day Module 2 (2.5h → 1.5h) |
| 1 | 1.5h | M3: Build System & Dev Environment (light hands-on) | 5-day Module 4 (2h → 1.5h) |
| 1 | 3.0h | M4: HAL Architecture **with adoption-seam framing** | 5-day Module 5 (2.5h → 3h, expanded with adoption side-bar) |
| 2 | 2.0h | M5: Core Infrastructure Libraries (Scheduler, AP_Param, AP_Logger) **with AP_Param adoption emphasis** | 5-day Module 6 (2.5h → 2h) |
| 2 | 1.5h | M6: Sensor Drivers + Airspeed | 5-day Module 7 (2h → 1.5h) |
| 2 | 2.0h | M7: AHRS + EKF Internals | 5-day Module 8 (2.5h → 2h) |
| 2 | 1.5h | M8: Control Pipeline (TECS, L1, APM_Control, SRV_Channels) | 5-day Module 9 (2.5h → 1.5h) |
| 3 | 2.0h | M9: Mission, Navigation, Debugging (combined + compressed) | 5-day Modules 10+11 (3.5h → 2h) |
| 3 | 2.0h | M10: **Adopting ArduPilot subsystems into a proprietary codebase** (NEW) | not in 5-day source |
| 3 | 2.5h | M11: Capstone — extract one subsystem into a foreign-codebase stub (NEW) | replaces 5-day Module 14 |
| 3 | 0.5h | Feedback session for the senior pilot cohort | NEW — pilot-specific |

Total: ~21h. Per-day: 7h.

### Pedagogical framing this audience needs

- They will compare every ArduPilot decision to their proprietary stack. The course must explicitly frame ArduPilot's choices as *one design among many* — not as "the right answer" — and call out the trade-offs (e.g. ArduPilot's parameter system is highly flexible but pays a per-access lookup cost; the singleton pattern is convenient but creates static-init ordering hazards; the scheduler is cooperative which means a 50ms task overrun is silent).
- Math-as-code, not math-on-slides. They can read the math; they want to see how ArduPilot expressed it (e.g. EKF state vector layout, TECS energy split formula, L1 lateral acceleration command).
- Every code walk should include the question "what would this look like extracted into your codebase?" at least once.

---

## Pipeline behavior overrides

- This run is **driven from the parent session**, not from the orchestrator agent, because the orchestrator subagent runtime in this environment does not expose the `Agent` or `AskUserQuestion` tools despite the frontmatter declaration. The parent session writes `req.md`, `state.md`, and `summary.md`, and spawns each downstream agent sequentially. Future environments that grant subagents the full toolset can let `course-orchestrator` execute autonomously by reading this file from disk and resuming.
- If a subagent reports it cannot complete its task within its turn budget, the parent session truncates and surfaces a `STAGE-X CAP-HIT` event in `state.md` rather than silently retrying.
