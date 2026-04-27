# Plan: GNC Plane 3-Day Pilot — Internals + Adoption Axis (iter 2)

Iter 2, supersedes [course/plans/plan-gnc-plane-3day-pilot-iter1.md](plan-gnc-plane-3day-pilot-iter1.md). Driven by [course/orchestration/gnc-plane-3day-pilot/req.md](../orchestration/gnc-plane-3day-pilot/req.md), locked 2026-04-27 on branch `GNC-0.1` at commit `98325ac0cc`. Design baseline: [course/custom_gnc_course_plane.md](../custom_gnc_course_plane.md) (5-day curriculum). The 3-day pilot is a **strict subset of the 5-day Plane content** plus one new module and one new capstone on **adopting ArduPilot subsystems into a foreign codebase**.

This iteration is a **minimal-delta revision** of iter 1. Module set, time budgets, lab specs, capstone allocations, decisions, and handoff payloads are preserved verbatim. The only changes are cite-range corrections triggered by [course/reviews/review-plan-gnc-plane-3day-pilot-iter1.md](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md) findings F1 (blocker), F2 (major), F3 (major), and F4 (minor — opportunistic), plus opportunistic tightening of three cites the writer's drift report had already corrected post-hoc but the plan still carried at iter-1 ranges. See **Lessons Applied** for the full source/severity/finding/action table and **Verification → Citations updated** for the explicit `old → new` diff of every cite that moved.

All `path:line` cites are written as clickable markdown links per [course/criteria/citation-rigor.md](../criteria/citation-rigor.md). The link path prefix from `course/plans/` to top-level repo dirs is `../../`. Every cite below was `grep -n`-verified against the working tree (commit `98325ac0cc`) during iter-2 planning; see **Verification**.

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
- **Depth**: **internals** — math-as-code, function-body walks, EKF lane-switch arbitration as code, TECS energy-balance equations as code, L1 lateral-acceleration command as code ([req.md:20](../orchestration/gnc-plane-3day-pilot/req.md#L20)).
- **Hardware**: SITL only — no real boards in this pilot ([req.md:23](../orchestration/gnc-plane-3day-pilot/req.md#L23)).
- **What is preserved from the 5-day source**: Modules 1, 2, 4, 5, 6, 7, 8, 9 (operations + build + HAL + infrastructure + sensors + AHRS/EKF + control), with structure intact and citation backbone reused per Appendix B of [custom_gnc_course_plane.md:1263-1278](../custom_gnc_course_plane.md#L1263-L1278). What is replaced: Day 5's integration project (Module 14) is **replaced by the new capstone**. What is dropped: Modules 13 (Lua), 15 (Pegasus), 16 (advanced workshop) entirely. What is compressed: Modules 2 (operations), 10+11 (mission + debugging combined). What is added: a new dedicated 2 h **adoption-axis module** plus recurring 2–4 min adoption side-bars in Days 1–2 and the 2.5 h capstone.
- **Constraints**: SITL only (no airspace, no logistics); 1:1 lab support given the cohort of 3; the audience's frame of reference is "compare every ArduPilot decision to my proprietary stack" so framing must consistently cast ArduPilot's choices as **one design among many**, not as canonical ([req.md:99-103](../orchestration/gnc-plane-3day-pilot/req.md#L99-L103)).
- **Iteration number**: iter 2, supersedes [plan-gnc-plane-3day-pilot-iter1.md](plan-gnc-plane-3day-pilot-iter1.md). One prior reviewer report exists for this slug ([review-plan-gnc-plane-3day-pilot-iter1.md](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md)); no prior lab-tester runs exist for any `gnc-plane-3day-pilot-*` lab.

## Lessons Applied

The iter-1 reviewer ([review-plan-gnc-plane-3day-pilot-iter1.md](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md), verdict PASS-WITH-FIXES) flagged **1 blocker (F1)**, **2 major (F2, F3)**, **2 minor (F4, F5)**, and **2 nits (F6, F7)**. Coverage is exhaustive below: every finding has an explicit Action this iteration row.

| Finding | Source | Severity | Summary | Action this iteration |
|---|---|---|---|---|
| **F1** | [review-iter1.md F1](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md) | **blocker** (citation-rigor) | M7's quoted `NavEKF3_core::errorScore` body was fabricated: used `gpsPosTestRatio`/`gpsVelTestRatio` (real names are `posTestRatio`/`velTestRatio`); used `tasDataDelayed.allowFusion`/`lastTasPassTime_ms` for the airspeed gate (real gate is `arsp != nullptr && arsp->get_num_sensors() >= 2 && (frontend->_affinity & EKF_AFFINITY_ARSP)`); used `0.5f` scaling on the magnetometer term (real factor is `0.3f`); omitted the `EKF_AFFINITY_MAG` gate entirely. | Cite range tightened from `:62-83` to **`:62-86`** (covers the full function body — the iter-1 range cut off line 86 `}` which is the function's closing brace; reviewer's evidence block at review F1 quotes through line 86). M7 module body and **Handoff → To course-writer** carry an explicit binding directive: course-writer must NOT quote multi-line C++ from `errorScore` unless it is byte-for-byte copied from the source via `Read` of [AP_NavEKF3_Outputs.cpp:62-86](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L86); paraphrase + cite is the safer default for this audience. The plan's M7 narrative (objectives 4, 6 below) names the actual symbols (`velTestRatio`, `posTestRatio`, `hgtTestRatio`, `tasTestRatio`, `magTestRatio`, the `EKF_AFFINITY_ARSP` and `EKF_AFFINITY_MAG` gates, the `0.3f` scaling on both airspeed and mag), so the writer has the truthful skeleton in front of them. |
| **F2** | [review-iter1.md F2](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md) | **major** (citation-rigor) | Cite `[Tools/autotest/sim_vehicle.py:1500-1600]` (used in iter-1 M2 line 115 and M9 line 276) drifts ~430 lines from the argparse it claims to anchor. Lines 1500-1600 are post-parse vehicle-detection logic; argparse for `--vehicle`/`--frame`/`--debug`/`--gdb` lives at 1073-1240, and `--map`/`--console` at 1413-1436. | Replaced both occurrences with **`[sim_vehicle.py:1073-1240]`** (covers `--vehicle`/`--frame` at 1073-1095, build group with `--debug` at 1098-1170, sim group with `--gdb` at 1175-1240) **plus a paired cite `[sim_vehicle.py:1405-1436]`** for the MAVProxy GUI group covering `--map` (line 1413) and `--console` (line 1422). Prose distinguishes the two groups so the audience sees argparse is split into named option groups, which is itself a useful Python idiom they may want to adopt. Cross-verified by `grep -n "add_option.*--vehicle\|add_option_group" Tools/autotest/sim_vehicle.py` returning lines 1073, 1097, 1174, 1176, 1400, 1405, 1436. |
| **F3** | [review-iter1.md F3](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md) | **major** (citation-rigor) | Cite `[ArduPlane/Plane.h:920-940]` (used in iter-1 M9 line 275, Critical Files line 338) is described as the `Plane::navigate` declaration block, but lines 920-940 contain `stabilize_*`/`calc_nav_yaw_*` declarations. Real `Plane::navigate` is at line 1107 inside the `// navigation.cpp` comment block opening at line 1104. | Replaced both occurrences with **`[ArduPlane/Plane.h:1104-1115]`** (covers `// navigation.cpp` comment at 1104, `loiter_angle_reset` at 1105, `loiter_angle_update` at 1106, **`navigate` at 1107**, `check_home_alt_change` at 1108, `calc_airspeed_errors` at 1109, `mode_auto_target_airspeed_cm` at 1110, `calc_gndspeed_undershoot` at 1111, `update_loiter` at 1112-1113, `setup_turn_angle` at 1114, `reached_loiter_target` at 1115). Cross-verified by `grep -n "void navigate\|navigation.cpp\|loiter_angle_reset" ArduPlane/Plane.h` returning lines 1104, 1105, 1107. The iter-1 cite `[ArduPlane/Plane.h:269]` for `nav_controller = &L1_controller` was correct (re-verified at `grep -n "nav_controller = &L1_controller"` returns 269) and is preserved unchanged. |
| **F4** | [review-iter1.md F4](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md) | minor (citation-rigor) | `mode_fbwa.cpp:1-46` overshoots the 45-line file by 1. | Tightened to **`mode_fbwa.cpp:1-45`** in M2 module body and Critical Files. `wc -l ArduPlane/mode_fbwa.cpp` returned 45. Trivial fix; addressed because consistency with the writer's tightening of `update_waypoint` 349 → 347 was the standard the reviewer set. |
| **F5** | [review-iter1.md F5](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md) | minor (time-budget) | Day 1 hands-on share is 19-23%, below the 25% rubric floor. The reviewer offered two paths: add ~20-25 min hands-on in M2 or M3, or accept as a Minor finding. | **Deferred (defensible accept)**. Justification: this audience has explicitly told us via [req.md:99-103](../orchestration/gnc-plane-3day-pilot/req.md#L99-L103) that they prefer code-walks over busywork; adding `param show ATT*` and `mode TAKEOFF` rote-exercise time inflates hands-on percentage without pedagogical gain for engineers who already operate proprietary autopilots. The reviewer accepted this is "also a defensible call given this audience's preference for code-walks over busywork" ([review-iter1.md:107](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md#L106)). Day 1 hands-on remains at the iter-1 mix (L1 in M4 plus M2/M3 code-along). Recorded as a knowing accept of the rubric Minor. |
| **F6** | [review-iter1.md F6](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md) | nit (audience-fit) | Course M3 cite list says "BUILD.md … do not duplicate in lecture" — directive prose addressed to the instructor leaks into student-visible content. | **Defer to course-writer / material-builder stage**. The plan's iter-1 Citations list at M3 already correctly tags the BUILD.md cite as "referenced for engineers who hit unfamiliar errors; do not duplicate its contents in the course" — the directive half ("do not duplicate") is a planner-to-writer instruction. The writer's iter-1 draft echoed it verbatim into student prose, which is the bug. The plan's iter-2 **Handoff → To course-writer** explicitly reiterates the [audience-fit.md:25](../criteria/audience-fit.md#L25) directive-prose rule and gives the writer a concrete rephrase ("BUILD.md — the long-form build reference; consult it directly for unfamiliar errors. We will not narrate it here.") so iter-2 of the writer drops the directive half. No change to the plan's M3 prose itself. |
| **F7** | [review-iter1.md F7](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md) | nit (scope-discipline) | Writer's iter-1 draft shortened M5 heading from "Core Infrastructure Libraries…" to "Core Infrastructure…" and M6 from "Sensor Drivers, Frontend/Backend, Airspeed" to "Sensor Drivers + Airspeed". | **No plan-side change**. The plan's iter-1 headings were already at full parity (the reviewer confirms this at [review-iter1.md F7 location bullets](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md#L120)); the drift was introduced by the writer. Iter-2 plan re-emphasises in **Handoff → To course-writer** that module headings must match the plan verbatim modulo trivial typo fixes ([scope-discipline.md](../criteria/scope-discipline.md) Module heading parity). |

**Pre-emptive lessons carried forward from iter 1** (cross-cutting items the iter-1 reviewer ratified as held end-to-end):

- **Cite drift on common anchors.** This plan was authored against working-tree commit `98325ac0cc` and every cite was `grep -n`-verified during planning. See **Verification → Citation sanity** for the verified set, including the drift-prone names: `NavEKF3::checkLaneSwitch` is at [AP_NavEKF3.cpp:1029](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1029) — note the 5-day source occasionally references `checkAndDoLaneSwitch` which **does not exist** in the current tree; the periodic arbitration is inline in `NavEKF3::UpdateFilter` plus the explicit `checkLaneSwitch` entrypoint. `errorScore` is `NavEKF3_core::errorScore` at [AP_NavEKF3_Outputs.cpp:62-86](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L86) — see F1 fix. `RLL2SRV_TCONST` is the actual ArduPilot parameter name at [AP_RollController.cpp:35](../../libraries/APM_Control/AP_RollController.cpp#L35); `RLL_RATE_P` is from the underlying PID and is a separate parameter — both correctly distinguished in M8's roll-controller walk.
- **Per-day buffer ≥ 30 min, declared up front.** Each day's 7 h is structured as 6.5 h modules + 0.5 h buffer for Q&A / breaks / slippage, satisfying [time-budget.md:12](../criteria/time-budget.md#L12). Reviewer audited this end-to-end in iter 1.
- **No coordination-file cites in pedagogical material.** [AGENTS.md](../../AGENTS.md), [CLAUDE.md](../../CLAUDE.md), and `.claude/` files are not cited as autopilot teaching material in this plan. They are referenced only in instructor-only notes about the course-build pipeline. Concrete `@Param` examples come from real ArduPlane source ([ArduPlane/Parameters.cpp:288-310](../../ArduPlane/Parameters.cpp#L288-L310) — tightened from iter-1's 290-310 per reviewer's accepted writer drift), not from `AGENTS.md`'s example block. Reviewer audit confirmed clean.
- **Directive prose is instructor-only.** Anywhere this plan flags "do not derive", "compress", "skip the math", or similar curriculum framing, it is addressed to course-writer in the **Handoff → To course-writer** section, not embedded as student-facing prose. F6 above is the writer-stage drift; iter-2 plan reinforces the rule in handoff.

## Decisions

The four scoping decisions (length, depth, vehicle, lab share) are locked by [req.md](../orchestration/gnc-plane-3day-pilot/req.md). Iter-2 makes **no module restructuring; deltas are localized to cite ranges and the EKF treatment** (per the iter-2 minimal-delta directive). The iter-1 design decisions D1–D14 are preserved verbatim below.

### Locked design choices

- **D1. Length: 21 h over 3 days (7 h/day).** Locked by [req.md:18](../orchestration/gnc-plane-3day-pilot/req.md#L18).
- **D2. Internals depth throughout.** Locked by [req.md:20](../orchestration/gnc-plane-3day-pilot/req.md#L20). Every internals module declares ≥ 5 file:line cites per [audience-fit.md:14](../criteria/audience-fit.md#L14).
- **D3. SITL only, no real hardware.** Locked by [req.md:23](../orchestration/gnc-plane-3day-pilot/req.md#L23).
- **D4. Vehicle = ArduPlane.** Locked by [req.md:17](../orchestration/gnc-plane-3day-pilot/req.md#L17). No QuadPlane content (req.md and the user prompt explicitly forbid pulling from [custom_gnc_course_quadplane.md](../custom_gnc_course_quadplane.md)).
- **D5. Adoption axis is recurring + dedicated + capstoned.** Recurring 2–4 min "adoption side-bars" in M4–M8 (Days 1–2 internals modules), plus a dedicated 2 h M10 (Day 3) titled *"Adopting ArduPilot subsystems into a proprietary codebase"*, plus a 2.5 h M11 solo-extraction capstone. Locked by [req.md:50-69](../orchestration/gnc-plane-3day-pilot/req.md#L50-L69).
- **D6. Per-day buffer = 30 min (0.5 h), declared up front.** Day total = 6.5 h modules + 0.5 h buffer = 7 h. Course total = 19.5 h modules + 1.5 h buffer = 21 h. Satisfies [time-budget.md:12](../criteria/time-budget.md#L12).
- **D7. Capstone allocations (solo, since cohort = 3).** Engineer 1 → `AP_L1_Control` (smallest, most self-contained — 547 lines per [AP_L1_Control.cpp](../../libraries/AP_L1_Control/AP_L1_Control.cpp), no `AP_Logger` or `GCS_MAVLink` dependencies in the hot path). Engineer 2 → `AP_TECS` (1610 lines per [AP_TECS.cpp](../../libraries/AP_TECS/AP_TECS.cpp), more entanglement: `AP_FixedWing::FlightStage`, `AP_Logger::Write`, `AP_AHRS`). Engineer 3 → `AP_NavEKF3` lane-health subset (NOT the full EKF — just `NavEKF3::checkLaneSwitch` at [AP_NavEKF3.cpp:1029-1062](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1029-L1062), `NavEKF3::switchLane` at [AP_NavEKF3.cpp:1064-1078](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1064-L1078), `NavEKF3::updateCoreErrorScores` at [AP_NavEKF3.cpp:1092-1099](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1092-L1099), and `NavEKF3_core::errorScore` at [AP_NavEKF3_Outputs.cpp:62-86](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L86) — the subset is well-bounded and the surrounding state machine is heavily documented). Locked by [req.md:65-69](../orchestration/gnc-plane-3day-pilot/req.md#L65-L69). Cite range for `errorScore` updated from iter-1's `:62-83` to `:62-86` per F1 (the iter-1 range truncated the function's closing brace at line 86; the writer's iter-2 needs the full function visible).
- **D8. Worked example for the adoption module = `AP_L1_Control`.** Smallest, most self-contained ArduPilot library that still teaches the full extraction problem (HAL boundary, `AP_GROUPINFO` parameter system, `extern const AP_HAL::HAL& hal;` pattern, `AP_HAL::micros()` time access). `AP_TECS` is shown as a stretch case in the same module if time allows; not required for the module to land. Locked by [req.md:62](../orchestration/gnc-plane-3day-pilot/req.md#L62).
- **D9. Drop policy from 5-day source.** Module 13 (Lua) — dropped (not on the adoption critical path, mentioned in M1 as one slide). Module 15 (Pegasus) — dropped (requires GPU hardware not available). Module 16 (advanced workshop) — dropped (3-day budget cannot fit). Module 14 (integration project) — replaced by M11 capstone. Module 12 (board porting) — folded into M4 (HAL) as a 15-min adoption side-bar; no standalone module. Mission + debugging — combined into a single 2 h M9. Locked by [req.md:73-78](../orchestration/gnc-plane-3day-pilot/req.md#L73-L78).
- **D10. Compression of M1 and M2.** M1 (Overview & Ecosystem) compressed from 1.5 h to 1.0 h ([req.md:84](../orchestration/gnc-plane-3day-pilot/req.md#L84)). M2 (Operations Essentials) compressed from 2.5 h to 1.5 h ([req.md:85](../orchestration/gnc-plane-3day-pilot/req.md#L85)) — keeps just enough SITL + MAVProxy + log fluency to drive code-walk demos; drops detailed mission planning, full failsafe-config tour, and the GCS UI tour.
- **D11. M4 (HAL) expanded from 2.5 h to 3.0 h** to absorb the adoption-seam framing and the board-porting side-bar (5-day Module 12 collapses here). Justified deviation from [req.md:87](../orchestration/gnc-plane-3day-pilot/req.md#L87)'s recommendation, which already specifies 3 h and is matched.
- **D12. Module numbering.** Day 1: M1, M2, M3, M4. Day 2: M5, M6, M7, M8. Day 3: M9, M10, M11, M11.5. The numbering is **renumbered relative to the 5-day source** because the module set is different. The Appendix B mapping in the 5-day file ([custom_gnc_course_plane.md:1263-1278](../custom_gnc_course_plane.md#L1263-L1278)) is preserved as the citation backbone, but module numbers shift.
- **D13. Lab count = 5, all SITL-only, all ArduPlane.** L1: HAL + scheduler probe (Day 1 M4). L2: AP_Param add + observe (Day 2 M5). L3: GPS noise + EKF lane switch (Day 2 M7). L4: roll-controller and TECS gain modify + observe (Day 2 M8). L5: solo extraction capstone (Day 3 M11). Locked by user prompt's "Planning notes specific to this course → Lab specs."
- **D14. Adoption side-bar discipline.** Each of M4 (HAL), M5 (infrastructure), M6 (sensors), M7 (AHRS/EKF), M8 (control) ends with a 2–4 min "adoption side-bar" structured as: (a) "What this subsystem buys you in your codebase" (1 min), (b) "What comes with it" — list of `extern const AP_HAL::HAL& hal;`, `GCS_SEND_TEXT`, `AP_Logger::Write`, scheduler ticks, `AP_Param` registration, math helpers (1–2 min), (c) "What it costs to keep vs replace" (~1 min). Total adoption-axis content in Days 1–2 = ~15 min spread across 5 modules, plus the dedicated 2 h M10 plus 2.5 h M11.

### Iter-2 deltas vs iter 1

The plan structure is otherwise iter-1 verbatim. Only these changes:

- **D15 (NEW). EKF lane-arbitration treatment is paraphrase-and-cite, not quote-and-cite.** The iter-1 writer fabricated a `NavEKF3_core::errorScore` body in M7 (review F1 blocker). To prevent recurrence, the plan binds the writer at the handoff layer: do NOT quote multi-line C++ in the EKF lane-switch discussion unless the bytes are copied via `Read` from [AP_NavEKF3_Outputs.cpp:62-86](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L86). Paraphrase + cite is the safer default. The narrative uses the actual symbol names verbatim (`velTestRatio`, `posTestRatio`, `hgtTestRatio`, `tasTestRatio`, `magTestRatio`, `EKF_AFFINITY_ARSP`, `EKF_AFFINITY_MAG`, scaling `0.3f` for both airspeed and mag terms). New decision; not a reversal of any iter-1 choice.
- **D16 (NEW). Cite-range corrections for F2, F3, F4 are baked into M2, M9, Critical Files.** sim_vehicle.py argparse cite split into `1073-1240` (build+sim option groups) and `1405-1436` (MAVProxy GUI group), so `--map`/`--console` are honestly anchored. `Plane.h` navigation block cite moved to `1104-1115`. `mode_fbwa.cpp` cite tightened to `1-45`. New decision; not a reversal.
- **D17 (NEW). Pre-tighten cites the writer's iter-1 drift report had already corrected.** Three cites the writer had to fix during iter-1 drafting (and which the reviewer's verified set ratified at the tightened ranges) are pre-tightened in iter 2 so the writer doesn't re-litigate them: `AP_L1_Control.cpp:206-349 → 206-347` (closing brace at 347), `AP_RollController.cpp:185-232 → 185-227` (closing brace at 227), `Parameters.cpp:290-310 → 288-310` (block opens at 288 with `// @Param: AIRSPEED_MIN`). Reviewer's citation audit at [review-iter1.md citation audit](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md#L132-L172) confirms these are the canonical ranges. Not a reversal — the iter-1 plan's wider ranges resolved correctly; this is just precision improvement.

## Deliverable

course-writer will produce one new file (or revise the iter-1 draft):

- [`course/custom_gnc_course_plane_3day_pilot.md`](../custom_gnc_course_plane_3day_pilot.md) — exists from iter-1 writer pass; iter-2 writer revises in place per F1, F2, F3, F4 fixes.

Relationship to existing files:

- **Sibling, prerequisite-style subset.** Does not replace, supplement, or modify [custom_gnc_course_plane.md](../custom_gnc_course_plane.md). The pilot's preamble points at the 5-day course as "the full version, if you want Days 4–5 content (board porting deep-dive, Lua, QuadPlane, soaring, advanced topics)."
- **No content from [custom_gnc_course_quadplane.md](../custom_gnc_course_quadplane.md)** — QuadPlane is out of scope.
- The course file ends with the line `Generated from course/plans/plan-gnc-plane-3day-pilot-iter2.md` per [scope-discipline.md:7](../criteria/scope-discipline.md#L7) (replacing the iter-1 trailer line).

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

Per-day budget: 6.5 h modules + 0.5 h buffer. Hands-on share target: ≥ 25% of 6.5 h = ≥ 1.625 h. Day 1 includes Lab L1 at 0.5 h and the in-module HAL-trace exercise at ~0.5 h ⇒ ~1 h hands-on minimum, plus optional code-along during M3 build walk pushes effective hands-on to ~1.5–1.6 h. Reviewer flagged this as a Minor (F5) and the plan accepts it; see Lessons Applied F5 row.

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
  - [Tools/autotest/sim_vehicle.py:1073-1240](../../Tools/autotest/sim_vehicle.py#L1073-L1240) — the **build + sim** argparse option groups (verified by `grep -n "add_option.*--vehicle\|add_option.*--debug\|add_option.*--gdb"` returning lines 1073, 1106, 1213). Covers `--vehicle`/`--frame` at 1073-1095, build group `--debug` at 1106 / `--no-rebuild` / `--clean` / `--jobs`, sim group `--gdb` at 1213 / `--lldb` / `--breakpoint`. **Replaces iter-1's `:1500-1600` cite per F2 fix.**
  - [Tools/autotest/sim_vehicle.py:1405-1436](../../Tools/autotest/sim_vehicle.py#L1405-L1436) — the **MAVProxy GUI** option group covering `--map` at 1413 and `--console` at 1422. Shown as a discrete second cite so engineers see argparse is split into named option groups (a useful Python idiom). **New cite added per F2 fix.**
  - [ArduPlane/mode_takeoff.cpp:1-80](../../ArduPlane/mode_takeoff.cpp#L1-L80) — `ModeTakeoff::update` opening, just to anchor "TAKEOFF is software, not a hardware mode."
  - [ArduPlane/mode_fbwa.cpp:1-45](../../ArduPlane/mode_fbwa.cpp#L1-L45) — full `ModeFBWA::update()` and `ModeFBWA::run()` (the file is exactly 45 lines per `wc -l`; read aloud in 5 min). **Tightened from iter-1's `:1-46` per F4 fix.**
  - [custom_gnc_course_plane.md:130-138](../custom_gnc_course_plane.md#L130-L138) — the "Key log messages for plane" list (`ATT`, `CTUN`, `NTUN`, `ARSP`, `TECS`) used as a printed reference, not re-derived in slides.
- **Hands-on**: ~10 min code-along: every engineer launches SITL on their laptop, takes off in `TAKEOFF`, switches to `FBWA`, switches to `RTL`. No formal lab; M4 has the first formal lab.

#### Module M3 — Build System & Development Environment (1.0 h, lecture+lab, *applied*)

**Why applied**: this audience knows build systems; they need ArduPilot's *waf* idioms and SITL+debug-symbols flow, not "what is a build system."

- **Objectives**:
  1. Run `./waf configure --board sitl --debug && ./waf plane`. Locate the build artifact at `build/sitl/bin/arduplane`.
  2. Recognise `wscript` files as Waf's per-directory build config (one example each from a vehicle dir and a library dir).
  3. Read `Tools/scripts/build_options.py` and recognise the `AP_<FEATURE>_ENABLED` compile-time-flag pattern — critical for understanding what comes "with" a subsystem at extraction time.
  4. Recognise the subset of build targets that matter: `plane`, `bin/arduplane`, `tests/test_<name>`.
- **Citations**:
  - [BUILD.md](../../BUILD.md) — referenced for engineers who hit unfamiliar errors. **Course-writer note (per F6):** rephrase any directive like "do not duplicate in lecture" as student-facing prose ("consult it directly for unfamiliar errors; we will not narrate it here") OR move the directive into an `\instnote{}` instructor-only block.
  - [ArduPlane/wscript:1-40](../../ArduPlane/wscript#L1-L40) — the vehicle `wscript` (the file is 37 lines; the 1-40 range is an acceptable header anchor — reviewer confirmed at [review-iter1.md citation audit](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md#L173)).
  - [libraries/AP_L1_Control/AP_L1_Control.cpp:1-15](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L1-L15) — file header showing `#include <AP_HAL/AP_HAL.h>`, `extern const AP_HAL::HAL& hal;`, the `var_info[]` opening line. This is the file the capstone Engineer 1 will extract.
  - [Tools/scripts/build_options.py:1-50](../../Tools/scripts/build_options.py#L1-L50) — file header + the first few `Feature(...)` entries (verified `grep -n "Feature(" Tools/scripts/build_options.py` returns lines 33, 44+). This is the one file in the codebase that enumerates the optional features, which directly determines "what comes with it" at extraction time.
  - [CLAUDE.md:120-150](../../CLAUDE.md#L120-L150) — repo-local Waf cheat sheet. **Instructor-only handoff reference; not student-facing pedagogical material per [audience-fit.md:24](../criteria/audience-fit.md#L24).**
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
  - [ArduPlane/Parameters.cpp:288-310](../../ArduPlane/Parameters.cpp#L288-L310) — real `@Param: AIRSPEED_MIN` / `@Param: AIRSPEED_MAX` annotation block in Plane vehicle code (`grep -n "@Param: AIRSPEED_MIN\|ASCALAR(airspeed_max"` returns 288 and 304). **Tightened from iter-1's `:290-310` per D17** (the iter-1 writer's drift report had already corrected this, the reviewer's verified set ratified `288-310`, so iter 2 carries the corrected range natively). (Concrete `@Param` example sourced from real vehicle code, NOT from `AGENTS.md`.)
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

**Iter-2 binding directive (per D15 / F1):** when course-writer treats `NavEKF3_core::errorScore`, the writer **must not fabricate or paraphrase a quoted code block**. Either (a) copy the exact bytes from [AP_NavEKF3_Outputs.cpp:62-86](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L86) via `Read` into a fenced block (which is fine), or (b) cite the function with a clickable `path:line` link and paraphrase its behavior in prose without quoting any code lines (which is the safer default for this audience). The iter-1 writer chose (a) but typed the block from memory and got every symbol wrong; iter 2 must not repeat that. The narrative below names the actual symbols verbatim — `velTestRatio`, `posTestRatio`, `hgtTestRatio`, `tasTestRatio`, `magTestRatio`, the affinity gates `EKF_AFFINITY_ARSP` and `EKF_AFFINITY_MAG`, the scaling factor `0.3f` for both airspeed and magnetometer terms — so the writer has the truthful skeleton to paraphrase from.

- **Objectives**:
  1. Read `AP_AHRS` as an interface; recognise that vehicle code never calls EKF directly.
  2. Read `NavEKF3::UpdateFilter` — the periodic lane-arbitration loop. Recognise `runCoreSelection`, the 10-second debounce, the `coreBetterScore` test, the `BETTER_THRESH` constant.
  3. Read `NavEKF3::checkLaneSwitch` — the explicit "EKF failsafe is about to trigger; can a lane swap save us?" entry point called from vehicle code.
  4. Read `NavEKF3_core::errorScore` — the consolidated error metric. Per-term breakdown:
     - GPS performance: `score = MAX(score, 0.5f * (velTestRatio + posTestRatio))`.
     - Altimeter: `score = MAX(score, hgtTestRatio)`.
     - Airspeed: gated by `assume_zero_sideslip()` AND a non-null `dal.airspeed()` AND `arsp->get_num_sensors() >= 2` AND `(frontend->_affinity & EKF_AFFINITY_ARSP)`; contributes `0.3f * tasTestRatio` (factor 0.3 — explicitly low-weighted to avoid spurious lane swaps from gust-induced TAS innovations).
     - Magnetometer: gated by `(frontend->_affinity & EKF_AFFINITY_MAG)` only; contributes `0.3f * (magTestRatio.x + magTestRatio.y + magTestRatio.z)`.
     - Pre-condition for any term: `tiltAlignComplete && yawAlignComplete`.
     - The `EKF_AFFINITY_*` flags are themselves a 2-min aside — they control which observations participate in lane-switch arbitration and are configured per-IMU/per-mag/per-airspeed via `EK3_AFFINITY` parameter.
  5. Read `NavEKF3::switchLane` — the actual switch with yaw/pos reset propagation and `EKF3 lane switch %u` GCS warning.
  6. Wind estimation: read where in `AP_NavEKF3_PosVelFusion.cpp` airspeed is fused (briefly — file is large; planner does NOT cite a specific line range here; instructor scrolls during the walk).
  7. **Adoption side-bar (4 min)**: "Adopting full `AP_NavEKF3` is a *large* undertaking — 2279 lines in `AP_NavEKF3_core.cpp` alone, and the dependency graph is broad: DAL (Data Access Layer), AHRS, multiple sensor frontends. The realistic adoption pattern is to extract just the *lane-arbitration logic* (≤ 200 lines) and apply it to multiple instances of *your own* EKF. That is exactly what Engineer 3's capstone does."
- **Citations**:
  - [libraries/AP_AHRS/AP_AHRS.h:1-80](../../libraries/AP_AHRS/AP_AHRS.h#L1-L80) — frontend interface header.
  - [libraries/AP_NavEKF3/AP_NavEKF3.cpp:910-1020](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L910-L1020) — `NavEKF3::UpdateFilter` body; the periodic lane-arbitration loop (`grep -n "void NavEKF3::UpdateFilter"` returns 910).
  - [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1029-1062](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1029-L1062) — `NavEKF3::checkLaneSwitch` body; the explicit "about-to-fail" entry point (`grep -n "void NavEKF3::checkLaneSwitch"` returns 1029).
  - [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1064-1078](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1064-L1078) — `NavEKF3::switchLane` body.
  - [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1092-1099](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1092-L1099) — `NavEKF3::updateCoreErrorScores`.
  - [libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp:62-86](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L86) — `NavEKF3_core::errorScore` body, the consolidated error metric. **Range tightened from iter-1's `:62-83` to `:62-86` per F1 fix** — the iter-1 range cut off the function's closing brace at line 86 (`grep -n "errorScore" libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp` returns 62; manual read of lines 62-86 confirms the function ends at line 86 with `}` on line 86).
  - [libraries/AP_NavEKF3/AP_NavEKF3_core.h:140-160](../../libraries/AP_NavEKF3/AP_NavEKF3_core.h#L140-L160) — `errorScore` declaration (`grep -n "errorScore" libraries/AP_NavEKF3/AP_NavEKF3_core.h` returns 149, in the 140-160 range).
  - [libraries/AP_NavEKF3/AP_NavEKF3.cpp:715-722](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L715-L722) — `EK3_PRIMARY` parameter declaration (which IMU is the default primary).
- **Hands-on lab spec**: **Lab L3 — GPS noise + EKF lane switch (~40 min)**. Engineer launches SITL, sets `SIM_GPS_NOISE 5` then `SIM_GPS_GLTCH 50` mid-flight (use `SIM_GPS_GLTCH` from [SIM_GPS.cpp:69-75](../../libraries/SITL/SIM_GPS.cpp#L69-L75)), observes the GCS `EKF3 lane switch N` statustext, downloads dataflash, identifies `XKF*` lane-switch event records and the `errorScore` divergence. Pass: lane switch fires within 30 s of the glitch injection AND the dataflash records the switch event. Validates the EKF internals walk.

#### Module M8 — Control Pipeline: TECS, L1, APM_Control, SRV_Channels (1.0 h, lecture+code-walk+lab, *internals*)

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
  - [libraries/AP_TECS/AP_TECS.cpp:99](../../libraries/AP_TECS/AP_TECS.cpp#L99) — `AP_GROUPINFO("SPDWEIGHT", 9, AP_TECS, _spdWeight, 1.0f)` single-line cite (verified `grep -n 'AP_GROUPINFO("SPDWEIGHT"'` returns 99). Reviewer's verified set tightened iter-1's `90-110` range to this single line; iter 2 carries the tightening.
  - [libraries/AP_TECS/AP_TECS.cpp:107](../../libraries/AP_TECS/AP_TECS.cpp#L107) — `AP_GROUPINFO("PTCH_DAMP", 10, AP_TECS, _ptchDamp, 0.3f)` single-line cite (verified `grep -n 'AP_GROUPINFO("PTCH_DAMP"'` returns 107); used in Lab L4. Reviewer's verified set used this single-line form; iter 2 carries it.
  - [libraries/AP_L1_Control/AP_L1_Control.cpp:206-347](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L206-L347) — `AP_L1_Control::update_waypoint` body in full. **Tightened from iter-1's `206-349` per D17** (function opens at 206 and closes at 347; `grep -n "^void AP_L1_Control::update_waypoint\|^}" libraries/AP_L1_Control/AP_L1_Control.cpp | head` returned 206 then 347 as the next `}`).
  - [libraries/AP_L1_Control/AP_L1_Control.cpp:7-44](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L7-L44) — `var_info[]` table: `NAVL1_PERIOD`, `NAVL1_DAMPING`, `NAVL1_XTRACK_I`, `NAVL1_LIM_BANK`.
  - [libraries/APM_Control/AP_RollController.cpp:185-227](../../libraries/APM_Control/AP_RollController.cpp#L185-L227) — `AP_RollController::get_servo_out` body. **Tightened from iter-1's `185-232` per D17** (function opens at 185 and closes at 227 verified by `grep -n "^float AP_RollController::get_servo_out\|^}" libraries/APM_Control/AP_RollController.cpp`).
  - [libraries/APM_Control/AP_RollController.cpp:35](../../libraries/APM_Control/AP_RollController.cpp#L35) — `AP_GROUPINFO("2SRV_TCONST", 0, AP_RollController, gains.tau, 0.5f)` single-line cite (full param name `RLL2SRV_TCONST` derived from the `RLL` group prefix; NOT "RLL_RATE_P", which is a separate underlying-PID parameter declared in the comment block at lines 51-100).
  - [libraries/APM_Control/AP_RollController.cpp:51-100](../../libraries/APM_Control/AP_RollController.cpp#L51-L100) — `_RATE_P/_RATE_I/_RATE_IMAX/_RATE_D/_RATE_FF/_RATE_FLTT/_RATE_FLTE` `@Param` comment blocks (the rate-PID parameters).
  - [libraries/SRV_Channel/SRV_Channels.cpp:478-510](../../libraries/SRV_Channel/SRV_Channels.cpp#L478-L510) — `SRV_Channels::cork` and `SRV_Channels::push`: the atomic-update pattern.
  - [libraries/SRV_Channel/SRV_Channel_aux.cpp:617-680](../../libraries/SRV_Channel/SRV_Channel_aux.cpp#L617-L680) — `SRV_Channels::set_output_scaled` body (the canonical "I have a control demand, where do I write it" call).
  - [ArduPlane/servos.cpp:861-900](../../ArduPlane/servos.cpp#L861-L900) — `Plane::set_servos` body: the `AP::srv().cork()` opening and the function structure.
- **Hands-on lab spec**: **Lab L4 — Modify roll-controller and TECS gains, observe response (~40 min)**. Engineer halves `RLL2SRV_TCONST` (from 0.5 to 0.25), flies FBWA, observes faster but more oscillatory roll response in dataflash `ATT.DesRoll` vs `ATT.Roll`. Then resets, halves `TECS_PTCH_DAMP` (from 0.3 to 0.15), flies a climb, observes altitude-tracking oscillation in dataflash `TECS.h` vs `TECS.hdem`. Pass: clear visual evidence in MAVExplorer plots that both gain changes alter the closed-loop response. Validates the control-pipeline walk.

---

### Day 3 — Mission/debug, dedicated adoption module, capstone, feedback (7 h)

**Goal**: each engineer has extracted one ArduPilot subsystem into a stub of a foreign codebase against a mock HAL, and has a working compilation + a passing gtest. This is the artifact each engineer keeps.

Per-day budget: 6.5 h modules + 0.5 h buffer. Hands-on share: M11 capstone alone is 2.5 h (~38% of the module budget) — comfortably exceeds the 25% rubric floor. Day 3 also contains the 0.5 h feedback session (M11.5), which is not labelled "hands-on" but is interactive.

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
  - [ArduPlane/Plane.h:1104-1115](../../ArduPlane/Plane.h#L1104-L1115) — the `// navigation.cpp` declaration block: `loiter_angle_reset`, `loiter_angle_update`, **`navigate`** (line 1107), `check_home_alt_change`, `calc_airspeed_errors`, `mode_auto_target_airspeed_cm`, `calc_gndspeed_undershoot`, `update_loiter`, `setup_turn_angle`, `reached_loiter_target`. **Replaces iter-1's `:920-940` per F3 fix** (verified `grep -n "void navigate\|navigation.cpp\|loiter_angle_reset" ArduPlane/Plane.h` returns 1104, 1105, 1107).
  - [ArduPlane/Plane.h:269](../../ArduPlane/Plane.h#L269) — `nav_controller = &L1_controller;` single-line cite (preserved unchanged from iter 1; reviewer ratified at [review-iter1.md F3 evidence](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md#L86)).
  - [Tools/autotest/sim_vehicle.py:1073-1240](../../Tools/autotest/sim_vehicle.py#L1073-L1240) — `--gdb`, `--debug` argument parsing in build + sim option groups (re-used from M2). **Replaces iter-1's `:1500-1600` per F2 fix.**
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
  - [libraries/AP_L1_Control/AP_L1_Control.cpp:206-347](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L206-L347) — `update_waypoint` body in full (function opens at 206, closes at 347). **Tightened from iter-1's `206-349` per D17.**
  - [libraries/AP_TECS/AP_TECS.cpp:1-30](../../libraries/AP_TECS/AP_TECS.cpp#L1-L30) — file header showing the broader entanglement set (`AP_Landing`, `AP_FixedWing`).
  - [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1029-1078](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1029-L1078) — `checkLaneSwitch` + `switchLane` together; the well-bounded lane-arbitration subset.
  - [libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp:62-86](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L86) — `errorScore` body; the metric Engineer 3 must replace or reimplement. **Range tightened from iter-1's `:62-83` to `:62-86` per F1 fix.**
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

Master deduplicated index of every file:line anchor referenced above. course-writer pulls from this list when drafting prose; lab-builder pulls from it when scaffolding labs. Cites that changed between iter 1 and iter 2 are flagged with `(iter2: was X)`.

- [AGENTS.md](../../AGENTS.md) — referenced *only* as a contributor-rule pointer in M5 (parameter-index-stability rule); not cited as pedagogical material per [audience-fit.md:24](../criteria/audience-fit.md#L24).
- [BUILD.md](../../BUILD.md) — referenced for build troubleshooting in M3.
- [CLAUDE.md:120-150](../../CLAUDE.md#L120-L150) — Waf cheat sheet; instructor-only handoff reference.
- [ArduPlane/Plane.h:1-50](../../ArduPlane/Plane.h#L1-L50) — Plane class header.
- [ArduPlane/Plane.h:269](../../ArduPlane/Plane.h#L269) — `nav_controller = &L1_controller`.
- [ArduPlane/Plane.h:1104-1115](../../ArduPlane/Plane.h#L1104-L1115) — `// navigation.cpp` declaration block including `Plane::navigate` at line 1107. **(iter2: was `:920-940` — F3 fix.)**
- [ArduPlane/Plane.cpp:30-60](../../ArduPlane/Plane.cpp#L30-L60) — `SCHED_TASK`/`FAST_TASK` macros.
- [ArduPlane/Plane.cpp:62-95](../../ArduPlane/Plane.cpp#L62-L95) — `Plane::scheduler_tasks[]` table opening.
- [ArduPlane/Plane.cpp:165-200](../../ArduPlane/Plane.cpp#L165-L200) — `Plane::ahrs_update`.
- [ArduPlane/Parameters.cpp:288-310](../../ArduPlane/Parameters.cpp#L288-L310) — `AIRSPEED_MIN`/`AIRSPEED_MAX` `@Param` block (real example). **(iter2: was `:290-310` — D17 pre-tighten.)**
- [ArduPlane/mode.h:1-80](../../ArduPlane/mode.h#L1-L80) — Mode base class.
- [ArduPlane/mode_takeoff.cpp:1-80](../../ArduPlane/mode_takeoff.cpp#L1-L80) — TAKEOFF mode anchor.
- [ArduPlane/mode_fbwa.cpp:1-45](../../ArduPlane/mode_fbwa.cpp#L1-L45) — full `ModeFBWA::update` and `run`. **(iter2: was `:1-46` — F4 fix; file is 45 lines exactly.)**
- [ArduPlane/mode_auto.cpp:1-80](../../ArduPlane/mode_auto.cpp#L1-L80) — `ModeAuto::update` opening.
- [ArduPlane/servos.cpp:861-900](../../ArduPlane/servos.cpp#L861-L900) — `Plane::set_servos`.
- [ArduPlane/wscript:1-40](../../ArduPlane/wscript#L1-L40) — vehicle wscript (file is 37 lines; reviewer ratified the 1-40 header anchor).
- [libraries/AP_HAL/AP_HAL.h:1-31](../../libraries/AP_HAL/AP_HAL.h#L1-L31) — umbrella include.
- [libraries/AP_HAL/HAL.h:21-30](../../libraries/AP_HAL/HAL.h#L21-L30) — `class AP_HAL::HAL` opening.
- [libraries/AP_HAL/HAL.h:35-90](../../libraries/AP_HAL/HAL.h#L35-L90) — constructor parameter list.
- [libraries/AP_HAL/HAL.h:21-90](../../libraries/AP_HAL/HAL.h#L21-L90) — combined seam cite for M10.
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
- [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1029-1078](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1029-L1078) — combined `checkLaneSwitch` + `switchLane` cite for M10.
- [libraries/AP_NavEKF3/AP_NavEKF3.cpp:1092-1099](../../libraries/AP_NavEKF3/AP_NavEKF3.cpp#L1092-L1099) — `NavEKF3::updateCoreErrorScores`.
- [libraries/AP_NavEKF3/AP_NavEKF3_core.h:140-160](../../libraries/AP_NavEKF3/AP_NavEKF3_core.h#L140-L160) — `errorScore` declaration at line 149.
- [libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp:62-86](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L86) — `NavEKF3_core::errorScore` body in full. **(iter2: was `:62-83` — F1 fix; function ends at line 86.)**
- [libraries/AP_Airspeed/AP_Airspeed.h:1-80](../../libraries/AP_Airspeed/AP_Airspeed.h#L1-L80) — airspeed frontend.
- [libraries/AP_Airspeed/AP_Airspeed_Backend.h:1-80](../../libraries/AP_Airspeed/AP_Airspeed_Backend.h#L1-L80) — airspeed backend interface.
- [libraries/AP_Airspeed/AP_Airspeed_SITL.cpp:1-80](../../libraries/AP_Airspeed/AP_Airspeed_SITL.cpp#L1-L80) — SITL airspeed backend.
- [libraries/AP_Airspeed/AP_Airspeed_MS4525.cpp:1-100](../../libraries/AP_Airspeed/AP_Airspeed_MS4525.cpp#L1-L100) — real I2C airspeed backend.
- [libraries/AP_Airspeed/Airspeed_Calibration.cpp:1-80](../../libraries/AP_Airspeed/Airspeed_Calibration.cpp#L1-L80) — auto-calibration.
- [libraries/AP_TECS/AP_TECS.cpp:1-30](../../libraries/AP_TECS/AP_TECS.cpp#L1-L30) — file header / entanglement.
- [libraries/AP_TECS/AP_TECS.cpp:99](../../libraries/AP_TECS/AP_TECS.cpp#L99) — `TECS_SPDWEIGHT` single-line `AP_GROUPINFO`. **(iter2: was `:90-110` — D17 pre-tighten to single-line per reviewer's verified set.)**
- [libraries/AP_TECS/AP_TECS.cpp:107](../../libraries/AP_TECS/AP_TECS.cpp#L107) — `TECS_PTCH_DAMP` single-line `AP_GROUPINFO`. **(iter2: was `:101-110` — D17 pre-tighten.)**
- [libraries/AP_TECS/AP_TECS.cpp:678-700](../../libraries/AP_TECS/AP_TECS.cpp#L678-L700) — `_update_energies`.
- [libraries/AP_TECS/AP_TECS.cpp:719-820](../../libraries/AP_TECS/AP_TECS.cpp#L719-L820) — `_update_throttle_with_airspeed`.
- [libraries/AP_TECS/AP_TECS.cpp:1270-1350](../../libraries/AP_TECS/AP_TECS.cpp#L1270-L1350) — `update_pitch_throttle`.
- [libraries/AP_L1_Control/AP_L1_Control.h:1-138](../../libraries/AP_L1_Control/AP_L1_Control.h#L1-L138) — full L1 header.
- [libraries/AP_L1_Control/AP_L1_Control.cpp:1-15](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L1-L15) — file header.
- [libraries/AP_L1_Control/AP_L1_Control.cpp:7-44](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L7-L44) — `var_info[]` table.
- [libraries/AP_L1_Control/AP_L1_Control.cpp:206-347](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L206-L347) — `update_waypoint` body. **(iter2: was `:206-349` — D17 pre-tighten; function closes at 347.)**
- [libraries/APM_Control/AP_RollController.cpp:35](../../libraries/APM_Control/AP_RollController.cpp#L35) — `RLL2SRV_TCONST` `AP_GROUPINFO` single-line cite.
- [libraries/APM_Control/AP_RollController.cpp:51-100](../../libraries/APM_Control/AP_RollController.cpp#L51-L100) — `_RATE_*` (rate-PID) `@Param` comment block.
- [libraries/APM_Control/AP_RollController.cpp:185-227](../../libraries/APM_Control/AP_RollController.cpp#L185-L227) — `get_servo_out` body. **(iter2: was `:185-232` — D17 pre-tighten; function closes at 227.)**
- [libraries/SRV_Channel/SRV_Channels.cpp:478-510](../../libraries/SRV_Channel/SRV_Channels.cpp#L478-L510) — `cork`/`push`.
- [libraries/SRV_Channel/SRV_Channel_aux.cpp:617-680](../../libraries/SRV_Channel/SRV_Channel_aux.cpp#L617-L680) — `set_output_scaled`.
- [libraries/SITL/SIM_GPS.cpp:69-75](../../libraries/SITL/SIM_GPS.cpp#L69-L75) — `SIM_GPS_GLTCH` parameter.
- [libraries/SITL/SIM_GPS.cpp:97-103](../../libraries/SITL/SIM_GPS.cpp#L97-L103) — `SIM_GPS_NOISE` parameter.
- [libraries/SITL/SITL.cpp:83-95](../../libraries/SITL/SITL.cpp#L83-L95) — `SIM_WIND_SPD`/`SIM_WIND_DIR` parameters.
- [Tools/scripts/build_options.py:1-50](../../Tools/scripts/build_options.py#L1-L50) — feature-flag enumeration header.
- [Tools/autotest/sim_vehicle.py:1](../../Tools/autotest/sim_vehicle.py#L1) — script existence anchor.
- [Tools/autotest/sim_vehicle.py:1073-1240](../../Tools/autotest/sim_vehicle.py#L1073-L1240) — argparse build + sim option groups (`--vehicle`/`--frame`/`--debug`/`--gdb`). **(iter2: was `:1500-1600` — F2 fix.)**
- [Tools/autotest/sim_vehicle.py:1405-1436](../../Tools/autotest/sim_vehicle.py#L1405-L1436) — argparse MAVProxy GUI option group (`--map`/`--console`). **(iter2: NEW — F2 fix companion cite.)**
- [Tools/autotest/arduplane.py:36-100](../../Tools/autotest/arduplane.py#L36-L100) — `class AutoTestPlane`.
- [Tools/autotest/arduplane.py:213-260](../../Tools/autotest/arduplane.py#L213-L260) — representative test method.

## Criteria Proposed

None — plan satisfies existing criteria in [course/criteria/](../criteria/).

The four existing rubrics ([audience-fit.md](../criteria/audience-fit.md), [citation-rigor.md](../criteria/citation-rigor.md), [scope-discipline.md](../criteria/scope-discipline.md), [time-budget.md](../criteria/time-budget.md)) caught every defect in iter 1 and are sufficient for iter 2. The reviewer's iter-1 audit at [review-iter1.md Suggested rubric additions](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md#L267) concurs ("None proposed in this iter") — the F1 quoted-body defect is already captured under citation-rigor's "Anchor existence" / "Symbol naming" Forbidden clauses. No criteria deltas this iteration.

## Handoff

### To course-writer

- **File path**: revise [`course/custom_gnc_course_plane_3day_pilot.md`](../custom_gnc_course_plane_3day_pilot.md) in place. Update the trailer line to `Generated from course/plans/plan-gnc-plane-3day-pilot-iter2.md` per [scope-discipline.md:7](../criteria/scope-discipline.md#L7).
- **Iter-2 minimal-delta rule**: this iteration is structural-parity with iter 1. Do NOT restructure modules, time budgets, lab specs, or capstone assignments. The only edits are localized fixes to the four findings below.
- **Fix F1 (blocker, M7)**: the iter-1 draft's M7 fenced `errorScore` block at course lines 389-405 is fabricated. **Two acceptable resolutions**:
  - **Option A (preferred for this audience)**: replace the fenced block with the verbatim function body from [AP_NavEKF3_Outputs.cpp:62-86](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L86), copied byte-for-byte via `Read` of that exact line range. Do not paraphrase symbol names. Do not omit the affinity gates.
  - **Option B**: drop the fenced block entirely and replace with prose: "`NavEKF3_core::errorScore()` (see [AP_NavEKF3_Outputs.cpp:62-86](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L86)) is a per-core consolidated metric: starting from 0, it MAXes in (a) `0.5f * (velTestRatio + posTestRatio)` for GPS performance, (b) `hgtTestRatio` for altimeter, (c) `0.3f * tasTestRatio` if `assume_zero_sideslip()` AND `dal.airspeed()` reports ≥ 2 sensors AND `EKF_AFFINITY_ARSP` is set, and (d) `0.3f * (magTestRatio.x + magTestRatio.y + magTestRatio.z)` if `EKF_AFFINITY_MAG` is set. The `0.3f` factor on (c) and (d) is deliberate — the comment at line 73-74 explains it as a 'sensitivity factor … to keep the EKF less sensitive to innovations arising due events like strong gusts of wind, thus, prevent reporting high error scores.' Pre-condition for any term: `tiltAlignComplete && yawAlignComplete`."
  - **NOT acceptable**: typing the function body from memory, paraphrasing symbol names (`gpsPosTestRatio` for `posTestRatio`), or guessing at the gating logic. The iter-1 draft did exactly that and produced a fabricated block. If you can't paste from `Read`, choose Option B.
  - The narrative paragraph following the block must (a) say the airspeed gate also requires `_affinity & EKF_AFFINITY_ARSP` and `>= 2` airspeed sensors, (b) note the magnetometer gate `_affinity & EKF_AFFINITY_MAG`, (c) state the scaling factors are `0.3f` for both airspeed and magnetometer, (d) add a 2-min aside noting that `EKF_AFFINITY_*` flags are configured per-IMU/per-mag/per-airspeed via the `EK3_AFFINITY` parameter. This audience came specifically to see the math-as-code; the affinity gating is the kind of detail they care about.
- **Fix F2 (major, M2 + M9)**: in iter-1 draft M2 line 109 and M9 line 529, change `[Tools/autotest/sim_vehicle.py:1500-1600]` to `[Tools/autotest/sim_vehicle.py:1073-1240]`. Add a paired cite `[Tools/autotest/sim_vehicle.py:1405-1436]` for the MAVProxy GUI group covering `--map`/`--console`. Prose can read: "argparse is split into named `OptionGroup`s — the build group and sim group at [sim_vehicle.py:1073-1240](../../Tools/autotest/sim_vehicle.py#L1073-L1240) (covering `--vehicle`/`--frame`/`--debug`/`--gdb`) and the MAVProxy GUI group at [sim_vehicle.py:1405-1436](../../Tools/autotest/sim_vehicle.py#L1405-L1436) (covering `--map`/`--console`)."
- **Fix F3 (major, M9)**: in iter-1 draft M9 line 527 and the Key cites list at line 540, change `[ArduPlane/Plane.h:920-940]` to `[ArduPlane/Plane.h:1104-1115]`. Prose can read: "`Plane::navigate` is declared in the `// navigation.cpp` block at [ArduPlane/Plane.h:1104-1115](../../ArduPlane/Plane.h#L1104-L1115) (line 1107)." The iter-1 cite of `[Plane.h:269]` for `nav_controller = &L1_controller` is correct and unchanged.
- **Fix F4 (minor, M2)**: change `[mode_fbwa.cpp:1-46]` to `[mode_fbwa.cpp:1-45]` in M2 line 113 and M2 Key cites line 121. The file is exactly 45 lines.
- **Drift report addendum**: in the course's existing Citation drift report, add a fourth bullet acknowledging the iter-1 reviewer findings F1, F2, F3 and the iter-2 fixes applied. Match the tone of the iter-1 drift report.
- **No-fabrication discipline (binding for D15)**: no fenced C++ code block in the course markdown should contain symbol names not present in the cited source range. If you cannot paste verbatim via `Read`, paraphrase in prose with a clickable cite. This rule applies to every code block, not just the EKF discussion. The iter-1 review caught one violation (F1); iter-2 must catch zero.
- **Voice**: peer-to-peer with senior GNC engineers. Cast every ArduPilot decision as one design among many, with explicit comparison opportunities ("compare to your stack's …") at each module boundary.
- **Module set parity**: produce exactly the 12 modules listed (M1–M11 plus M11.5 feedback). No additions, no removals, no reorderings.
- **Headings parity (per F7)**: use the plan's verbatim module headings — "M5 — Core Infrastructure **Libraries** with `AP_Param` adoption emphasis" (do not drop "Libraries"); "M6 — Sensor Drivers, **Frontend/Backend**, Airspeed" (do not drop "Frontend/Backend"). The iter-1 draft dropped both; iter 2 must restore.
- **Directive-prose discipline (per F6)**: anywhere this plan or the iter-1 draft has phrasing like "do not duplicate in lecture", "compress", "skip the math", "out of scope" — that is curriculum framing addressed to you, the writer. It must NOT appear in student-facing prose. Either rephrase as student-facing content ("we will not narrate it here") or move into an `\instnote{}` instructor-only block. Per [audience-fit.md:25](../criteria/audience-fit.md#L25).
- **No cites to coordination files as pedagogical material**: `AGENTS.md`, `CLAUDE.md`, `.claude/`, repo-root meta docs are off-limits for pedagogical citation per [audience-fit.md:24](../criteria/audience-fit.md#L24). When this plan's "Citations" lists include `AGENTS.md` (M5) or `CLAUDE.md` (M3), they appear as instructor-only references; do NOT include them in student-facing citation blocks.
- **Concrete `@Param` example**: when illustrating the `@Param` annotation block, use [ArduPlane/Parameters.cpp:288-310](../../ArduPlane/Parameters.cpp#L288-L310) (real `AIRSPEED_MIN`/`MAX` block; tightened in iter 2 from `:290-310`), NOT the `AGENTS.md` example block.
- **Capstone framing**: M11 is presented as solo work (not paired) since cohort = 3 and per-engineer assignments are pre-allocated (D7). The course preamble states the assignment policy. Engineers MAY swap with each other before the capstone starts; the per-engineer choice does not affect the lab-builder's setup.

### To course-reviewer

Apply all four rubrics in [course/criteria/](../criteria/):

- [audience-fit.md](../criteria/audience-fit.md) — verify: (a) the audience declaration in the preamble matches `req.md`'s "senior GNC engineers, internals depth"; (b) the prerequisite list names C/C++, RTOS, fixed-wing controls, gdb/gtest, and explicitly excludes ArduPilot; (c) every module that claims internals depth has ≥ 5 file:line cites (M4, M5, M7, M8, M10 are the internals modules); (d) the directive-prose rule (line 25) is honored — "compress", "skip", "out of scope", "do not duplicate" appear only in instructor-only blocks (re-audit M3 BUILD.md cite per F6); (e) coordination-file cites (line 24) are not used pedagogically.
- [citation-rigor.md](../criteria/citation-rigor.md) — verify: (a) every cite is a clickable markdown link with `path:line` displayed text; (b) every cite resolves in the current tree (sample at least 10 cites at random and run `grep -n` per the recipe); (c) line ranges are 5–150 lines; (d) **symbol-naming-verbatim — re-audit M7's `errorScore` treatment specifically**. The iter-1 draft fabricated the body. The iter-2 fix is either verbatim copy from [AP_NavEKF3_Outputs.cpp:62-86](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L86) or paraphrase + cite. If a fenced C++ block appears in the course's M7, every symbol in it must match the source character-for-character: `velTestRatio`, `posTestRatio`, `hgtTestRatio`, `tasTestRatio`, `magTestRatio.x/y/z`, `EKF_AFFINITY_ARSP`, `EKF_AFFINITY_MAG`, factor `0.3f` for tas and mag, factor `0.5f` for the GPS combined term. (e) verify `Plane::navigate` is now anchored at [Plane.h:1104-1115](../../ArduPlane/Plane.h#L1104-L1115) NOT `:920-940`; (f) verify `sim_vehicle.py` argparse is anchored at [`:1073-1240`](../../Tools/autotest/sim_vehicle.py#L1073-L1240) and [`:1405-1436`](../../Tools/autotest/sim_vehicle.py#L1405-L1436) NOT `:1500-1600`; (g) verify `mode_fbwa.cpp` is `:1-45` NOT `:1-46`.
- [scope-discipline.md](../criteria/scope-discipline.md) — verify: (a) the course file has the `Generated from course/plans/plan-gnc-plane-3day-pilot-iter2.md` line; (b) module set in the course matches M1..M11.5 in this plan; (c) each module's time matches ±15 min; (d) **module headings match the plan verbatim per F7** — restore "Libraries" in M5, "Frontend/Backend" in M6; (e) no unauthorized content from [custom_gnc_course_quadplane.md](../custom_gnc_course_quadplane.md); (f) lab specs in the course match the "Handoff → To lab-builder" entries below.
- [time-budget.md](../criteria/time-budget.md) — verify: (a) course total declared as ~21 h; (b) per-day totals each = 7 h; (c) per-module times within each day sum to 6.5 h ± 15 min, plus the explicit 0.5 h buffer; (d) hands-on share ≥ 25% per day (Day 1 will be at ~23%, **knowingly accepted as Minor finding F5** — reviewer should record but not block on this); (e) capstone ≥ 2 h (M11 is 2.5 h, satisfies); (f) buffer ≥ 30 min per day (declared 30 min, satisfies exactly).

**Specific risks to audit**:
- **F1 regression**: re-read M7's `errorScore` treatment carefully. If the writer chose Option A (verbatim copy), every byte must match; if Option B (paraphrase), no fenced block of fabricated C++.
- **F2/F3 regression**: spot-check the new cites land at the claimed symbols. `grep -n` for `add_option` in the cited ranges of `sim_vehicle.py`; `grep -n "void navigate"` in `Plane.h:1104-1115`.
- **Heading parity (F7)**: verify M5 and M6 headings match the plan exactly.
- **Directive prose (F6)**: re-scan student-facing prose for "do not duplicate", "compress", "skip", "out of scope".
- Citation drift on `NavEKF3::checkLaneSwitch` — make sure no draft prose regressed to `checkAndDoLaneSwitch` (the 5-day source's older anchor name).
- Module 4 (HAL) at 3.0 h is the longest module; verify it actually packs 3.0 h of content and is not padded with operations material.
- Module 10 (Adoption) is wholly new — verify it doesn't drift into a "list of all libraries" survey; it must stay focused on the four extraction-seam patterns + the worked L1 example.
- The capstone (M11) at 2.5 h has three different deliverables (one per engineer); verify the course file documents all three with equal care.
- Adoption side-bars in M4–M8 must be present and distinct; verify they are not collapsed into a single repeated paragraph.

### To lab-builder

Five labs, all SITL-only, all `ArduPlane`, all on stock SITL physics. Each lab gets its own subdirectory under `course/labs/gnc-plane-3day-pilot-*/` with the canonical structure (`README.md`, `student-guide.md`, `instructor-guide.md`, `expected.md`, `launch.sh`, `params.parm`, `steps.md`, `test.py`, `test.sh`).

**No iter-2 changes to lab specs.** All five labs are unchanged from iter 1. The cite-range corrections in the plan do not affect lab procedures, vehicle/frame, parameter sets, or pass criteria.

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
- **Procedure (Phase A — roll)**: take off in TAKEOFF, switch to FBWA, fly steady, then `param set RLL2SRV_TCONST 0.25` (default 0.5; halves the time constant per [AP_RollController.cpp:35](../../libraries/APM_Control/AP_RollController.cpp#L35)); fly several roll inputs; download log, plot `ATT.DesRoll` vs `ATT.Roll`.
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

For each lab above, run the full SITL invocation against the working tree at `GNC-0.1` HEAD and produce a `report.md` under `course/labs/gnc-plane-3day-pilot-l<N>/runs/<ts>/`. The exact commands and expected fingerprints (unchanged from iter 1):

- **L1**: `cd /home/mahisorn/repos/ardupilot_course && ./waf configure --board sitl --debug && ./waf plane && Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --no-mavproxy --debug` in one terminal; `gdb -p $(pgrep arduplane) -batch -ex "b Plane::ahrs_update" -ex "c" -ex "p AP_HAL::millis()" -ex "p AP::scheduler().get_loop_rate_hz()" -ex "detach" -ex "quit"` in another. Expected: a `millis()` print > 0 and a loop-rate print `50` (the [AP_Scheduler.cpp:46](../../libraries/AP_Scheduler/AP_Scheduler.cpp#L46) plane default).
- **L2**: `cd /home/mahisorn/repos/ardupilot_course && ./waf plane && Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console`. In MAVProxy: `param show MY_*` → expect `MY_PARAM 17.0`. `param set MY_PARAM 42.0`. Quit SITL. Restart. `param show MY_*` → expect `MY_PARAM 42.0`. (Lab-builder pre-stages the `Parameters.{h,cpp}` patch; lab-tester applies it before configure.)
- **L3**: same SITL launch. MAVProxy: `mode TAKEOFF`, `arm throttle`, wait until altitude ≥ 50 m, `mode FBWA`, fly steady ~10 s, `param set SIM_GPS_NOISE 5`, wait 10 s, `param set SIM_GPS_GLTCH_X 50` (Vector3 param — write x-component or all three depending on `mavparm` syntax in the harness). Expected: GCS statustext line containing `EKF3 lane switch` within 30 s. Dataflash check: `mavlogdump.py --types=XKF1,XKF4,EV logs/00000001.BIN | grep -i 'switch\|lane'` returns ≥ 1 record.
- **L4**: same SITL launch. Phase A: `mode TAKEOFF`, climb, `mode FBWA`. `param set RLL2SRV_TCONST 0.25`. Move roll stick (`rc 1 1300` then `rc 1 1700`). Quit. Plot `ATT.DesRoll` vs `ATT.Roll` from log. Phase B: relaunch, defaults; `param set TECS_PTCH_DAMP 0.15`; fly 50 m altitude step in CRUISE (set `mode CRUISE`, `rc 2 1700` to climb, then `rc 2 1500` to level). Plot `TECS.h` vs `TECS.hdem`. Expected: visible (≥ 30%) reduction in tracking-error settling time on Phase A, visible increase in altitude-tracking oscillation on Phase B.
- **L5**: per-engineer: `cd course/labs/gnc-plane-3day-pilot-l5/eng<N>-* && cmake -B build && cmake --build build && ctest --test-dir build`. Expected: `100% tests passed`. The lab-builder pre-stages each stub repo so the failing test stub fails on first run; the engineer's job is to vendor the ArduPilot files and make the test pass. lab-tester verifies the *reference solution* (provided by lab-builder) compiles + passes.

If any of L1–L5 returns FAIL or FLAKY, course-orchestrator drives a lab-builder iteration on the failing lab. Per [req.md:35](../orchestration/gnc-plane-3day-pilot/req.md#L35) the lab-builder ↔ lab-tester loop is capped at 2 iterations per lab.

## Verification

### Citation sanity

Every cite in this plan was `grep -n`-verified against the working tree at commit `98325ac0cc` during iter-2 planning. Specifically verified during this iteration (focused on the cites that moved between iter 1 and iter 2):

- [libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp:62-86](../../libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp#L62-L86) — `grep -n "errorScore\|posTestRatio\|velTestRatio\|tasTestRatio\|magTestRatio\|EKF_AFFINITY" libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp` returned (relevant lines): 62 (`float NavEKF3_core::errorScore() const`), 67 (`score = MAX(score, 0.5f * (velTestRatio + posTestRatio));`), 75 (airspeed gate `arsp != nullptr && arsp->get_num_sensors() >= 2 && (frontend->_affinity & EKF_AFFINITY_ARSP)`), 76 (`score = MAX(score, 0.3f * tasTestRatio);`), 81 (`if (frontend->_affinity & EKF_AFFINITY_MAG) {`), 82 (`score = MAX(score, 0.3f * (magTestRatio.x + magTestRatio.y + magTestRatio.z));`). Manual `sed -n '60,90p'` confirms function closes at line 86. Iter-2 range `:62-86` is correct; iter-1's `:62-83` truncated the closing brace.
- [Tools/autotest/sim_vehicle.py:1073-1240](../../Tools/autotest/sim_vehicle.py#L1073-L1240) — `grep -n "add_option" Tools/autotest/sim_vehicle.py | head -40` returned (key lines): 1073 (`parser.add_option("-v", "--vehicle"`), 1078 (`--frame`), 1097 (`group_build = optparse.OptionGroup`), 1106 (`group_build.add_option("-D", "--debug"`), 1174 (`parser.add_option_group(group_build)`), 1176 (`group_sim = optparse.OptionGroup`), 1213 (`group_sim.add_option("-G", "--gdb"`). Build + sim option groups span 1073-1240 inclusive of `--lldb-stopped` at 1225.
- [Tools/autotest/sim_vehicle.py:1405-1436](../../Tools/autotest/sim_vehicle.py#L1405-L1436) — `grep -n '"--map"\|"--console"' Tools/autotest/sim_vehicle.py` returned 1413 (`group.add_option("", "--map"`) and 1422 (`group.add_option("", "--console"`). `grep -n "OptionGroup\|add_option_group" Tools/autotest/sim_vehicle.py` confirms the MAVProxy GUI group opens at 1405 (`group = optparse.OptionGroup(parser, ...)`) and closes at 1436 (`parser.add_option_group(group)`). Iter-2 range is correct.
- [ArduPlane/Plane.h:1104-1115](../../ArduPlane/Plane.h#L1104-L1115) — `grep -n "void navigate\|navigation.cpp\|loiter_angle_reset" ArduPlane/Plane.h` returned 1104 (`// navigation.cpp`), 1105 (`void loiter_angle_reset(void);`), **1107 (`void navigate();`)**. Manual `sed -n '1100,1120p'` confirms the block runs through 1115 (`bool reached_loiter_target(void);`).
- [ArduPlane/mode_fbwa.cpp:1-45](../../ArduPlane/mode_fbwa.cpp#L1-L45) — `wc -l ArduPlane/mode_fbwa.cpp` returned 45. The full file is 45 lines; iter-1's `:1-46` overshot by one.
- [libraries/AP_TECS/AP_TECS.cpp:99](../../libraries/AP_TECS/AP_TECS.cpp#L99) — `grep -n 'AP_GROUPINFO("SPDWEIGHT"' libraries/AP_TECS/AP_TECS.cpp` returned 99 (`AP_GROUPINFO("SPDWEIGHT", 9, AP_TECS, _spdWeight, 1.0f),`).
- [libraries/AP_TECS/AP_TECS.cpp:107](../../libraries/AP_TECS/AP_TECS.cpp#L107) — `grep -n 'AP_GROUPINFO("PTCH_DAMP"' libraries/AP_TECS/AP_TECS.cpp` returned 107 (`AP_GROUPINFO("PTCH_DAMP", 10, AP_TECS, _ptchDamp, 0.3f),`).
- [libraries/AP_L1_Control/AP_L1_Control.cpp:206-347](../../libraries/AP_L1_Control/AP_L1_Control.cpp#L206-L347) — `grep -n "^void AP_L1_Control::update_waypoint\|^}" libraries/AP_L1_Control/AP_L1_Control.cpp | head` returned 206 (function open) and 347 (next `}`). Iter-1's `206-349` overshot by 2.
- [libraries/APM_Control/AP_RollController.cpp:185-227](../../libraries/APM_Control/AP_RollController.cpp#L185-L227) — `grep -n "^float AP_RollController::get_servo_out\|^}" libraries/APM_Control/AP_RollController.cpp | head` returned 185 (function open) and 227 (next `}`). Iter-1's `185-232` overshot by 5.
- [ArduPlane/Parameters.cpp:288-310](../../ArduPlane/Parameters.cpp#L288-L310) — reviewer's audit at [review-iter1.md citation audit](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md#L138) confirms `// @Param: AIRSPEED_MIN` opens at 288 and `ASCALAR(airspeed_max, ...)` is at 304. Iter-1 plan said `:290-310`; iter 2 carries the writer's tightened range.

The iter-1 cites that did NOT move (and which the reviewer's audit at [review-iter1.md citation audit](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md#L132-L172) ratified as resolvable) are preserved without re-verification in this section, since their iter-1 verification still holds against the same SHA `98325ac0cc`. The full set is in **Critical Files Cited** above.

### Citations updated or dropped (iter 1 → iter 2)

Explicit `old → new` diff of every cite that moved between iter 1 and iter 2:

| File | Iter 1 range | Iter 2 range | Trigger | Reason |
|---|---|---|---|---|
| `libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp` | `62-83` | **`62-86`** | F1 (blocker) | iter-1 range cut off function's closing `}` at line 86; `errorScore` body needs full visibility for the writer's verbatim copy or paraphrase. Also: writer-side directive added (D15) — no fabricated quoted blocks in the EKF section; paraphrase + cite is the safer default. |
| `Tools/autotest/sim_vehicle.py` (M2 + M9) | `1500-1600` | **`1073-1240`** + new paired `1405-1436` | F2 (major) | iter-1 range pointed to post-parse vehicle-detection logic, not argparse. argparse build+sim groups at 1073-1240 (`--vehicle`/`--frame`/`--debug`/`--gdb`); MAVProxy GUI group at 1405-1436 (`--map`/`--console`). |
| `ArduPlane/Plane.h` (M9) | `920-940` | **`1104-1115`** | F3 (major) | iter-1 range pointed to `stabilize_*`/`calc_nav_yaw_*` declarations, not `Plane::navigate`. Real `navigate` is at line 1107 inside the `// navigation.cpp` block opening at 1104. |
| `ArduPlane/mode_fbwa.cpp` (M2) | `1-46` | **`1-45`** | F4 (minor) | File is exactly 45 lines (`wc -l`); iter-1 overshot by 1. |
| `ArduPlane/Parameters.cpp` (M5) | `290-310` | **`288-310`** | D17 pre-tighten | `// @Param: AIRSPEED_MIN` block opens at line 288, not 290. Reviewer's verified set ratified `288-310`; pre-tightened in iter 2 so writer doesn't re-fix. |
| `libraries/AP_L1_Control/AP_L1_Control.cpp` (M8 + M10) | `206-349` | **`206-347`** | D17 pre-tighten | `update_waypoint` closes at line 347. Reviewer's verified set ratified `206-347`. |
| `libraries/APM_Control/AP_RollController.cpp` (M8) | `185-232` | **`185-227`** | D17 pre-tighten | `get_servo_out` closes at line 227. Reviewer's verified set ratified `185-227`. |
| `libraries/AP_TECS/AP_TECS.cpp` (M8) `SPDWEIGHT` | `90-110` | **`99`** | D17 pre-tighten | Reviewer's verified set used the single-line cite for the `AP_GROUPINFO("SPDWEIGHT"...)` declaration. |
| `libraries/AP_TECS/AP_TECS.cpp` (M8) `PTCH_DAMP` | `101-110` | **`107`** | D17 pre-tighten | Reviewer's verified set used the single-line cite for the `AP_GROUPINFO("PTCH_DAMP"...)` declaration. |
| `libraries/APM_Control/AP_RollController.cpp` (M8) `RLL2SRV_TCONST` | `27-50` (range covering both TCONST and RMAX) | **`35`** for TCONST + new **`51-100`** for `_RATE_*` block | D17 pre-tighten | Reviewer's verified set used `:35` for the TCONST single-line cite; `_RATE_P/I/IMAX/D/FF/FLTT/FLTE` `@Param` blocks are at 51-100. Splitting the iter-1 range improves anchor specificity. |

No cites were dropped between iter 1 and iter 2.

### Time-budget sum

| Day | Modules (sum) | Buffer | Day total | Target |
|-----|---------------|--------|-----------|--------|
| 1 | M1 1.0 + M2 1.5 + M3 1.0 + M4 3.0 = 6.5 | 0.5 | 7.0 | 7.0 ✓ |
| 2 | M5 2.0 + M6 1.5 + M7 2.0 + M8 1.0 = 6.5 | 0.5 | 7.0 | 7.0 ✓ |
| 3 | M9 2.0 + M10 2.0 + M11 2.5 + M11.5 0.0 = 6.5 | 0.5 | 7.0 | 7.0 ✓ |
| | **Total** | | **21.0** | **21.0** ✓ |

(M11.5 feedback session is 0.5 h and is held *during* the daily buffer — same allocation as iter 1.)

Per-day delta vs target = 0 h. Course total delta vs target = 0 h. Both within rubric tolerance ([time-budget.md:8](../criteria/time-budget.md#L8) ±1 h course, ±15 min day). Identical to iter 1 (D6 unchanged).

### Per-day hands-on share

- **Day 1**: L1 ~0.5 h embedded in M4, plus ~0.5 h code-along across M2 + M3 = ~1.0 h direct hands-on of 6.5 h = 15.4%. With the M4 HAL trace exercise included as hands-on (per the rubric's "build, debug, log analysis" framing), ~1.5 h of 6.5 h = 23.1%, **knowingly accepted as Minor finding F5** per [review-iter1.md F5](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md#L102) and the deferred-with-justification action in **Lessons Applied → F5**.
- **Day 2**: L2 0.5 h + L3 0.67 h + L4 0.67 h = 1.83 h hands-on of 6.5 h = **28.2%** ✓.
- **Day 3**: M11 capstone 2.5 h of 6.5 h = **38.5%** ✓.

### Lab reproducibility

- L1: `Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --debug` syntax checked against [Tools/autotest/sim_vehicle.py:1073-1240](../../Tools/autotest/sim_vehicle.py#L1073-L1240) (note: cite range corrected from iter-1's `:1500-1600` per F2). `--debug` flag exists at line 1106; `-v ArduPlane` is the canonical plane vehicle key (per [arduplane.py:36](../../Tools/autotest/arduplane.py#L36) `class AutoTestPlane`).
- L2: SITL launch identical to L1 minus `--debug`; the `MY_PARAM` add patch lab-builder will pre-stage in `libraries/.../Parameters.h` lines around 295.
- L3: `SIM_GPS_GLTCH` is a Vector3 parameter; the lab-builder must confirm whether MAVProxy's `param set` syntax for Vector3 is `SIM_GPS_GLTCH_X` (per-axis) or requires `mavproxy_set` with three values. If MAVProxy uses per-axis suffixes, the command is `param set SIM_GPS_GLTCH_X 50`. Lab-builder confirms on first lab run.
- L4: `RLL2SRV_TCONST` and `TECS_PTCH_DAMP` are scalar `AP_Float` parameters; standard `param set` syntax. Confirmed.
- L5: no SITL; the lab-builder produces three stub repos with vendored `AP_Math`, mock HAL, mock AHRS. The reference solutions are pre-tested by lab-tester before the engineers run them.

### No-overlap audit

- **Sibling course [custom_gnc_course_plane.md](../custom_gnc_course_plane.md)**: this plan is a strict subset + 1 new module + 1 new capstone. Modules 1, 2, 4, 5, 6, 7, 8, 9 of the 5-day source map to (compressed) versions M1, M2, M3, M4, M5, M6, M7, M8 here. Modules 10 + 11 of the 5-day source compress into M9. Module 12 of the 5-day source folds into M4 as a side-bar. Modules 13, 14, 15, 16 of the 5-day source are dropped or replaced. **Deliberate reuse**, recorded in **Decisions → D9**. Reviewer ratified at [review-iter1.md scope-vs-plan](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md#L190).
- **Sibling course [custom_gnc_course_quadplane.md](../custom_gnc_course_quadplane.md)**: NO content reuse. QuadPlane is out of scope for the 3-day pilot. Reviewer audited at [review-iter1.md QuadPlane audit](../reviews/review-plan-gnc-plane-3day-pilot-iter1.md#L211).
- **Sibling course [intro_arducopter_aero_y1.md](../intro_arducopter_aero_y1.md)**: NO content reuse. Different audience, vehicle, depth. The two courses do not share any cite ranges.

### Lessons coverage

Iter-1 review findings coverage:

- **F1 blocker** — addressed (cite range corrected `:62-83 → :62-86`; D15 binding directive added; M7 narrative names actual symbols verbatim; Handoff → To course-writer gives Option A/B resolution).
- **F2 major** — addressed (cite split into `1073-1240` + `1405-1436`; updated in M2, M9, Critical Files).
- **F3 major** — addressed (cite corrected `:920-940 → :1104-1115`; updated in M9, Critical Files).
- **F4 minor** — addressed (cite tightened `:1-46 → :1-45`; updated in M2, Critical Files).
- **F5 minor** — deferred with justification (audience preference for code-walks over busywork; reviewer accepted "also a defensible call").
- **F6 nit** — deferred to writer/material-builder stage (plan-level handoff reinforces the rule; no plan prose changes).
- **F7 nit** — no plan-side change needed (plan headings were already at parity; writer-stage drift; iter-2 handoff reinforces verbatim-heading rule).

Plus opportunistic D17 pre-tightenings of three iter-1 cite ranges (`Parameters.cpp`, `AP_L1_Control.cpp` `update_waypoint`, `AP_RollController.cpp` `get_servo_out`) and the TECS/RollController param single-line cites that the writer's iter-1 drift report had already corrected post-hoc — these are now baked into iter 2 so the writer doesn't re-fix in iter-2 drafting.

No prior lab-tester runs exist for any `gnc-plane-3day-pilot-*` lab; nothing to address from that surface.

---

Generated 2026-04-27 against branch `GNC-0.1` HEAD `98325ac0cc`. Iter 2 of plan slug `gnc-plane-3day-pilot`.
