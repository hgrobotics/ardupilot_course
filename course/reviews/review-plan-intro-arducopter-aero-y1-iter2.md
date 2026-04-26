# Review: plan-intro-arducopter-aero-y1-iter2.md

This is a **plan-stage review** of iter2, audited against the four rubrics in
`course/criteria/` (with the post-iter1-review edits to `audience-fit.md` and
`citation-rigor.md` in force) and against the iter1 review's carry-forward
findings. iter2 supersedes iter1 by compressing 16 h / 4 days → 8 h / 2 days
per the user's locked length decision.

Pinned tree: branch `GNC-0.1`, head `a6fc842e04`, date 2026-04-26 — matches
the plan's own pin and the iter1 reviewer's pin (no drift).

## Verdicts per rubric

| Rubric | Verdict |
|---|---|
| `audience-fit.md` | **pass** |
| `citation-rigor.md` | **pass-with-findings** (Nits only) |
| `scope-discipline.md` | **pass** (plan-stage; full audit deferred to course-draft review) |
| `time-budget.md` | **pass** |

Overall plan-stage verdict: **pass-with-findings**. No blockers, no Major
findings. Three Nit-class findings (all citation-rigor formatting); two
already-recorded mild discrepancies in the plan's own self-audit that do not
rise to a finding under the rubric severity guides.

## Findings

### F1-iter2 — Clickable-rendering: bare `:NNN` short-link displayed text in module body
- **Severity**: Nit.
- **Origin**: introduced in iter2 (this is a consequence of the new clickable-rendering rubric, which iter1 was not subject to).
- **Rubric**: `citation-rigor.md` → "Clickable rendering: every cite is written as a markdown link… Displayed text is the `path:line` form above" and "Bare `path:line` strings without a markdown link are a Nit finding." (The rubric's "displayed text" requirement is the spirit of the bullet; abbreviating displayed text to `:NNN` after a full-form cite has been emitted on the same line is a soft-violation.)
- **Location**: plan line 270 (Module 2.2 body):
  > each axis calls `update_all(...)` on a PID at [libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:473](../../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L473) (roll), `:476` (pitch), `:479` (yaw).
- **Observation**: `:476` and `:479` are bare path-less line shorthands in a non-finding-quote prose context. The rubric exempts only "finding-description quotes"; module body prose is not exempt. The link target is implied (same file as the preceding link), but the displayed text omits the path.
- **Evidence**: `grep -nE \`:[0-9]+\`` on the plan returns these strings as bare-tick shorthand without an enclosing markdown-link bracket pair.
- **Recommended fix**: replace `\`:476\`` and `\`:479\`` with full-form clickable cites: `[libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:476](../../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L476)`, similarly `:479`. Verbose, but matches the rubric's letter. Alternative: introduce all three line numbers in a single linked range `[…:473-479](…#L473-L479)` and call out the per-axis lines in prose (`roll on line 473, pitch on 476, yaw on 479`) without trying to make each line itself clickable.

### F2-iter2 — Clickable-rendering: `[:NNN](…)` form in Verification block uses path-less displayed text
- **Severity**: Nit.
- **Origin**: introduced in iter2.
- **Rubric**: `citation-rigor.md` → "Clickable rendering: …Displayed text is the `path:line` form above."
- **Location**: plan lines 486, 487, 489, 494, 498, 499, 500. Multiple instances of the form `[:83](../../ArduCopter/ekf_check.cpp#L83)`, `[:394](…)`, `[:561](…)`, `[:713](…)`, etc.
- **Observation**: The link *target* is well-formed and resolves; the link *text* is `:NNN`, not `path:NNN`. The intent is the path was just stated in the immediately-preceding sibling link on the same bullet — readable shorthand, but strictly the rubric asks for `path:line` as displayed text.
- **Evidence**: `grep -nE '\[:[0-9]+\]'` on the plan returns these matches; each link target verifies (lines 83/86/89/394/404/561/713/1576/2269 all resolve at the pinned head).
- **Recommended fix**: choose one of:
  1. Inflate every short-form `[:83](…)` to `[ArduCopter/ekf_check.cpp:83](…#L83)` everywhere — most rubric-compliant.
  2. Keep the short form and have course-writer translate to full-form when the cites move into the course file (the course's audience-facing cite is the rubric-binding one; the plan's cites are for the writer/reviewer audit).
  3. Propose a rubric clarification under `citation-rigor.md` that "shorthand `:NNN` is acceptable when emitted on the same Markdown bullet as a preceding full-form cite to the same path" — this is the cleanest long-term fix but is a rubric edit, not a plan edit.

### F3-iter2 — Display-text vs link-target mismatch in the rubric pointer at line 5
- **Severity**: Nit.
- **Origin**: introduced in iter2.
- **Rubric**: `citation-rigor.md` (general clickable-rendering quality; not strictly the displayed-text bullet, but the same family of audit-checking-the-reader's-trust concerns).
- **Location**: plan line 5:
  > All `file:line` cites in this plan are clickable markdown links per the new **Clickable rendering** bullet in [audience-fit.md](../criteria/citation-rigor.md).
- **Observation**: The displayed link text is `audience-fit.md` but the link target is `../criteria/citation-rigor.md`. The clickable-rendering bullet does live in `citation-rigor.md` (the link target is correct), so the displayed text is the typo. A reader scanning this opening assertion sees "audience-fit.md" and may believe the rubric edit landed in the wrong file.
- **Evidence**: lines 5 of the plan, verbatim.
- **Recommended fix**: change `[audience-fit.md]` to `[citation-rigor.md]`. One-character class of edit.

### Below-finding-threshold observations (recorded so the user can decide whether to upgrade to findings)

- `ArduCopter/mode.cpp:313-396` is the cited range for `Copter::set_mode`; the prose at plan line 213 calls out `mode.cpp:404` (`need alt estimate`) as one of the *applied*-depth lines, but `:404` is **outside** the 313-396 range. Each line is separately linked, so the cite resolution is intact, but a reader who follows only the larger range will miss `:404`. Either the larger range should widen to `:313-410`, or the prose should explicitly note that `:404` is the second of two separately-cited applied-depth lines (which is what the plan effectively does today). This is the same shape of issue the iter1 reviewer flagged at the bottom of its mode.cpp row in the citation audit table; iter2 carries it forward in the same posture. Below the Nit threshold per the iter1 reviewer's ruling, recorded here for completeness.
- `ArduCopter/ekf_check.cpp:30-90` cuts mid-function (the function ends at line 111). The iter1 review made the same observation about `mode_loiter.cpp:80-104` (F6 Nit). For ekf_check, the cite covers the load-bearing bad-variance branch and the plan separately emits a tighter `:79-89` cite for the "source-of-truth fingerprint." The mid-function cut here is purposeful, not sloppy. Below the Nit threshold.

## Carry-forward findings status

The user's brief specifies three iter1 findings to verify by name:

### F2 (iter1) — "AP_Mission.cpp:1085-1150 described as execution but is parsing"
- **iter2 planner's claim**: moot-by-cut (mission module dropped).
- **Verification**: confirmed. The mission module (iter1's 4.2) is in D-cut1 (plan lines 100-101). The cite `AP_Mission.cpp:1085-1150` appears in iter2 only:
  - In the Lessons-Applied carry-forward block at plan line 31, *as a quoted finding*, with the iter1-reviewer's verb correction recorded.
  - In the "Cites cut from iter1 because their parent module is dropped in iter2" list at plan line 369, with the cite explicitly retired.
  - It does **not** appear in any iter2 module body. Confirmed by grep across the iter2 module sections (lines 156-306).
- **Forward-only execution-anchor cites** were added by iter2 to record the correct path for any future iteration: `ArduCopter/mode_auto.cpp:698-713` (`ModeAuto::start_command` dispatch), `:1575-1614` (`do_nav_wp`), `:2268-2295` (`verify_nav_wp`). All three resolve at the pinned head; the descriptions match the code (697 is the comment, 699 is the function header for `start_command`; the `MAV_CMD_NAV_WAYPOINT` branch genuinely calls `do_nav_wp(cmd)` at line 713; `do_nav_wp` body opens at 1576; `verify_nav_wp` body opens at 2269). The verb is "execution" and the code is dispatch / setup / completion-check — execution semantics, correct verb.
- **Status**: **moot-by-cut, claim verified.**

### F4 (iter1) — "Prerequisite-chain awareness named in prose but not enumerated"
- **iter2 planner's claim**: addressed via a 15-row assumption-map table.
- **Verification**: confirmed structurally. The table is at plan lines 114-130, has 15 rows numbered 1–15, and each row maps to either a specific iter2 module (rows 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13) or to "deliberately out of scope" with one-sentence justification (rows 11, 12, 14, 15). The "Known gaps" line at plan line 132 names the four out-of-scope items by row number for the course-writer.
- **Sample audit of "established by Module X.Y" rows**:
  - **Row 1** ("autopilot is one binary…SITL") → Module 1.1. Module 1.1 objective 3 (plan line 169) is "Recognise that the *same* ArduPilot binary that flies real hardware also flies in SITL." Row established. ✓
  - **Row 2** ("SITL launched via `Tools/autotest/sim_vehicle.py -v <Vehicle> -f <frame>`") → Module 1.2. Module 1.2 objective 3 (plan line 182) is "Launch SITL: `Tools/autotest/sim_vehicle.py -v ArduCopter --console --map`." Row established (the row generalises to `-v <Vehicle> -f <frame>`; the module establishes the form for ArduCopter). ✓
  - **Row 5** ("parameters … `AP_GROUPINFO`-family macros … `@Param` annotations") → Module 1.5. Module 1.5 objective 2 (plan line 222) is "Read the canonical parameter-doc format and recognise `@Param`, `@DisplayName`, `@Description`, `@Range`, `@Units`." The cite [AGENTS.md:202-234](../../AGENTS.md#L202-L234) carries the `AP_GROUPINFO` worked example. Row established. ✓
  - **Row 6** ("scheduler …") → Module 2.1. Module 2.1 objective 4 (plan line 251) is "Define 'scheduler' as a fixed list of (function, rate, max_micros) tuples that the autopilot runs forever in a loop." Row established. ✓
  - **Row 8** ("control path … mode `run()` → attitude controller → rate controller → PID → motor mixer → ESC") → Module 2.2. Module 2.2 objective 1 (plan line 265) names exactly that data path verbatim. Row established. ✓
  - **Row 9** ("automatic failsafes … RC loss, battery, GCS link, EKF variance") → Module 2.3. Module 2.3 objective 2 (plan line 280) names exactly those four failsafes. Row established. ✓
  - **Row 10** ("Dataflash logs and `MAV_SEVERITY_*` GCS statustext") → Module 2.4 (closing lab). Module 2.4 objective 3 (plan line 293) is "Inspect the dataflash log afterward to identify the moment of failsafe by both the GCS statustext and the dataflash `ERR` row." Row established. ✓
  - **Row 13** ("Build system: `./waf configure --board sitl && ./waf copter`") → Module 1.2. Module 1.2 objective 2 (plan line 181) is verbatim that command. Row established. ✓
- **Mild softness on Row 4** ("a mode is software running at high rate, not a hardware switch position") → Module 1.4. Module 1.4 covers mode buckets and prerequisites at *survey/applied* depth, but does not explicitly contrast "software running at high rate" with "hardware switch position." It does cite [ArduCopter/mode_stabilize.cpp:9-64](../../ArduCopter/mode_stabilize.cpp#L9-L64) which contains the `should be called at 100hz or more` comment, so the rate detail is reachable. The "not a hardware switch position" framing is implicit in the assumption-map row but not explicitly demanded of the module. Below the Nit threshold; recorded so course-writer is aware.
- **Status**: **addressed, claim verified.**

### F9 (iter1) — "Per-day buffer was 15 min; rubric requires ≥ 30 min"
- **iter2 planner's claim**: addressed; 30-min/day buffer declared up front.
- **Verification**: confirmed.
  - Plan lines 67-70 (Lessons Applied → F9 action): "Buffer is declared **up front** at **30 min per day** (= 1 h total course buffer), and is subtracted from the per-day module budget before listing modules: Day 1: 4.0 h total = 3.5 h modules + 0.5 h buffer. Day 2: 4.0 h total = 3.5 h modules + 0.5 h buffer."
  - Plan line 86 (Decisions D9): "Buffer is declared up front at 30 min/day and subtracted from the per-day module budget *before* listing modules. (Addresses F9. Reverses iter1's 15-min/day buffer.)"
  - Plan line 154 (Course Structure narrative): "Buffer per day is 30 min (per F9 / [time-budget.md](../criteria/time-budget.md)) and is the *only* slack — per-module times within a day sum to 3.5 h exactly."
  - Plan line 231 ("#### Day 1 buffer / Q&A (30 min)") and line 303 ("#### Day 2 buffer / Q&A (30 min)") — the buffer line in each day's body is explicitly 30 min, not 15.
  - Per-day arithmetic confirmed below in **Time-budget audit**: each day's modules sum to 3.5 h and add 0.5 h buffer for 4.0 h, with no double-counting (the iter1 F1 double-count is structurally impossible because the buffer is *not* on the per-module list anymore).
- **Status**: **addressed, claim verified.**

### Other iter1 findings — moot-by-cut status

- **F1 (iter1)** — Day-3/Day-4 buffer double-count. Iter2 carries no Day 3 / Day 4. The lesson is also *internalised* (buffer is now declared once outside the per-module sum, so the structural shape that produced F1 is gone). **Moot, lesson carried.**
- **F3 (iter1)** — 1.25 h capstone vs ≥ 2 h floor. Iter2 is 2 days, below the rubric's ≥ 3-day capstone trigger. The strongest-payload module is renamed "Closing lab," not "Capstone," precisely to avoid claiming a rubric-frame the rubric does not impose. **Moot.** (Note: see "Capstone framing under the 2-day budget" below for explicit confirmation that the rubric does not impose any closing-exercise requirement on a 2-day course.)
- **F5 (iter1)** — `AGENTS.md:5-8` is 4 lines wide. Iter2 widens to `AGENTS.md:1-22` (22 lines, well within rubric). Verified at the pinned head: lines 1-22 cover the document title + safety-critical framing + Table of Contents — substantively richer than the iter1 4-line range. **Addressed.**
- **F6 (iter1)** — `mode_loiter.cpp:80-104` ends mid-function. `LOITER` is dropped from the iter2 mode tour (D-cut3); the cite is in the "Cites cut from iter1" list at plan line 365 and not used in any iter2 module. **Moot-by-cut.**
- **F7 (iter1)** — Day-3 hands-on share recomputation. Day 3 does not exist in iter2. **Moot.**
- **F8 (iter1)** — `AC_PID.cpp:13-73` truncates PDMX block. Iter2 compresses PID-as-black-box to *survey* depth and removes the PID parameter-table cite; the cite is in the "Cites cut from iter1" list at plan line 366. **Moot-by-cut.**

**No iter1 finding is left un-addressed in iter2.** This matches the planner's self-claim at plan lines 521-531.

## Clickable-rendering rubric compliance (sampled)

I sampled cites from the body, the citation list, and the Handoff sections. For each, I checked: (a) is it a markdown link? (b) is the relative path correct from `course/plans/`? (c) does the displayed `path:line` match the `#Lstart-Lend` anchor?

| # | Cite (verbatim from plan) | MD link? | Path correct? | Anchor matches displayed range? |
|---|---|---|---|---|
| 1 | `[AGENTS.md:1-22](../../AGENTS.md#L1-L22)` (line 172) | yes | yes (`../../` from `course/plans/`) | yes (`#L1-L22`) |
| 2 | `[CLAUDE.md:14-31](../../CLAUDE.md#L14-L31)` (line 173) | yes | yes | yes |
| 3 | `[ArduCopter/Copter.h:181](../../ArduCopter/Copter.h#L181)` (line 174) | yes | yes | yes (single-line, `#L181`) |
| 4 | `[Tools/autotest/sim_vehicle.py:1073-1085](../../Tools/autotest/sim_vehicle.py#L1073-L1085)` (line 188) | yes | yes | yes |
| 5 | `[ArduCopter/mode.cpp:313-396](../../ArduCopter/mode.cpp#L313-L396)` (line 213) | yes | yes | yes |
| 6 | `[ArduCopter/ekf_check.cpp:30-90](../../ArduCopter/ekf_check.cpp#L30-L90)` (line 283) | yes | yes | yes |
| 7 | `[libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:457-485](../../libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp#L457-L485)` (line 270) | yes | yes | yes |
| 8 | `[libraries/AP_Motors/AP_MotorsMatrix.cpp:592-602](../../libraries/AP_Motors/AP_MotorsMatrix.cpp#L592-L602)` (line 273) | yes | yes | yes |
| 9 | `[ArduCopter/mode_auto.cpp:698-713](../../ArduCopter/mode_auto.cpp#L698-L713)` (line 32, forward-only) | yes | yes | yes |
| 10 | `[ArduCopter/ekf_check.cpp:79-89](../../ArduCopter/ekf_check.cpp#L79-L89)` (line 295, lab) | yes | yes | yes |

All 10 sampled cites pass the structural test. The displayed `path:line` matches the link's `#L…-L…` anchor in every case.

**Bare-cite check** (cites without markdown links, outside finding-description quotes): only two `path:line` strings appear in backticks without an enclosing markdown link:
- Plan line 46 (`AGENTS.md:5-8`) and plan line 51 (`mode_loiter.cpp:80-104`) — both inside finding-description quotes (the F5 and F6 carry-forward Lessons-Applied bullets, where the iter1 review's wording is reproduced verbatim). The clickable-rendering rubric explicitly exempts finding-description quotes.

**Bare short-form cites** (`:NNN` outside markdown brackets): see F1-iter2 above. **Bare short-form linked cites** (`[:NNN](…)` with displayed text omitting path): see F2-iter2 above.

## Capstone framing under the 2-day budget

The user's brief asks me to confirm whether `time-budget.md` imposes any closing-exercise requirement on a 2-day course that the renamed "Closing lab" satisfies or violates.

Re-reading `time-budget.md`:

- The capstone clause (line 11) says "any course **≥ 3 days** must include a capstone exercise consuming ≥ 2 h." The clause is silent on 1-2 day courses.
- The hands-on share clause (line 10) says "each day must include ≥ 25% hands-on time." Day 2 of iter2 hits ~41% (1.45 h hands-on / 3.5 h modules) — comfortably above the floor. Module 2.4 alone is 1.25 h of the 1.45 h hands-on; without it, Day 2 would land at ~6%, well below the floor. The Closing lab is structurally load-bearing for Day 2's hands-on share even though the rubric does not name it as a capstone.
- The Forbidden clauses (lines 14-19) list things that count as time-budget violations; no clause requires a closing exercise for a course < 3 days.

**Conclusion**: the rubric is **silent** on closing-exercise requirements for a 2-day course. The renamed "Closing lab" does not violate any rubric clause and is not required by any rubric clause. The iter2 planner's reasoning at plan line 510 ("Course is 2 days; below the 3-day capstone-floor trigger…") is correct and the rename from "Capstone" to "Closing lab" is rubric-aligned (it avoids implying a capstone-floor obligation that does not apply). **F3 (iter1) is correctly closed by iter2.**

## Citation audit

Cites I `grep -n`-verified at pinned head `a6fc842e04`:

| Cite | Resolves? | Description matches code? |
|---|---|---|
| `AGENTS.md:1-22` | yes | yes — title + safety-critical framing + ToC, 22 lines |
| `AGENTS.md:202-234` | yes | yes — Section 6 "Parameter Documentation" with `@Param/@DisplayName/…` annotations |
| `CLAUDE.md:14-31` | yes | yes — "Big-picture architecture" section |
| `CLAUDE.md:103-107` | yes | yes — apt-mirror guidance (file is 107 lines, cite ends at the last line) |
| `BUILD.md` (existence) | yes | yes |
| `Tools/environment_install/install-prereqs-ubuntu.sh` (existence) | yes | yes (611 lines) |
| `Tools/autotest/sim_vehicle.py:287` | yes | line 287 is `'ArduCopter.elf',` |
| `Tools/autotest/sim_vehicle.py:1073-1085` | yes | `--vehicle` and `--frame` parser block |
| `ArduCopter/Copter.h:181` | yes | `class Copter : public AP_Vehicle {` |
| `ArduCopter/Copter.cpp:113-149` | yes | `FAST_TASK` block opening; comment `// run EKF state estimator (expensive)` at 126; `FAST_TASK(read_AHRS),` at 127 |
| `ArduCopter/Copter.cpp:117` | yes | `FAST_TASK(run_rate_controller_main),` |
| `ArduCopter/Copter.cpp:126` | yes | `// run EKF state estimator (expensive)` comment |
| `ArduCopter/Copter.cpp:127` | yes | `FAST_TASK(read_AHRS),` |
| `ArduCopter/Copter.cpp:151-201` | yes | SCHED_TASK block ending at `SCHED_TASK(ekf_check, 10, 75, 84),` line 201 |
| `ArduCopter/Copter.cpp:201` | yes | `SCHED_TASK(ekf_check, 10, 75, 84),` |
| `ArduCopter/Copter.cpp:998` | yes | `AP_HAL_MAIN_CALLBACKS(&copter);` (last line of file; file is 998 lines) |
| `ArduCopter/Attitude.cpp:10-24` | yes | `Copter::run_rate_controller_main` body |
| `ArduCopter/mode.h:77-109` | yes | `enum class Number : uint8_t { STABILIZE = 0, …, AUTO_RTL = 27, TURTLE = 28 };` |
| `ArduCopter/mode.cpp:313-396` | yes | `Copter::set_mode` opening (full function ends at line 481); `requires position` line is at `:394`, inside the cited range |
| `ArduCopter/mode.cpp:394` | yes | `mode_change_failed(new_flightmode, "requires position");` |
| `ArduCopter/mode.cpp:404` | yes | `mode_change_failed(new_flightmode, "need alt estimate");` (note: outside the larger `:313-396` range, but separately linked) |
| `ArduCopter/mode_stabilize.cpp:9-64` | yes | `ModeStabilize::run` body, fills the entire 64-line file |
| `ArduCopter/mode_althold.cpp:9-22` | yes | `ModeAltHold::init` |
| `ArduCopter/mode_althold.cpp:26-104` | yes | `ModeAltHold::run` body (file is 104 lines) |
| `ArduCopter/Parameters.cpp:33-67` | yes | `Copter::var_info[]` opening — `FORMAT_VERSION`, `PILOT_THR_FILT`, `PILOT_THR_BHV`, `GCS_PID_MASK` |
| `ArduCopter/Parameters.cpp:149-191` | yes | `FLTMODE1`-`FLTMODE6` and `FLTMODE_CH` block |
| `ArduCopter/AP_Arming_Copter.cpp:8-20` | yes | `pre_arm_checks` → `run_pre_arm_checks` → "exit immediately if already armed" |
| `ArduCopter/ekf_check.cpp:30-90` | yes | `Copter::ekf_check` body opening (function ends at 111); cuts mid-function but covers the bad-variance branch |
| `ArduCopter/ekf_check.cpp:79-89` | yes | the bad-variance trigger block — `LOGGER_WRITE_ERROR` at 83, `EKF variance: %s` `MAV_SEVERITY_CRITICAL` statustext at 86, `failsafe_ekf_event()` at 89 |
| `ArduCopter/ekf_check.cpp:83` | yes | `LOGGER_WRITE_ERROR(LogErrorSubsystem::EKFCHECK, LogErrorCode::EKFCHECK_BAD_VARIANCE);` |
| `ArduCopter/ekf_check.cpp:86` | yes | `gcs().send_text(MAV_SEVERITY_CRITICAL,"EKF variance: %s", over_threshold ? …);` |
| `ArduCopter/ekf_check.cpp:89` | yes | `failsafe_ekf_event();` |
| `libraries/AP_HAL/AP_HAL_Main.h:35-41` | yes | `AP_HAL_MAIN_CALLBACKS` macro definition |
| `libraries/AP_Vehicle/AP_Vehicle.cpp:558-566` | yes | `void AP_Vehicle::loop()` opening; `scheduler.loop();` at 561 |
| `libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:457-485` | yes | `rate_controller_run_dt` body |
| `libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:473` | yes | `_motors.set_roll(get_rate_roll_pid().update_all(…));` |
| `libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:476` | yes | `_motors.set_pitch(get_rate_pitch_pid().update_all(…));` |
| `libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp:479` | yes | `_motors.set_yaw(get_rate_yaw_pid().update_all(…));` |
| `libraries/AC_PID/AC_PID.cpp:196-272` | yes | `AC_PID::update_all` body opening (function ends at 311); `P_out = (_error * _kp);` at 269 |
| `libraries/AP_Motors/AP_MotorsMatrix.cpp:213-244` | yes | `output_armed_stabilizing` opening |
| `libraries/AP_Motors/AP_MotorsMatrix.cpp:592-602` | yes | `MOTOR_FRAME_TYPE_X` motor angles +45/-135/-45/+135 |
| Forward-only `ArduCopter/mode_auto.cpp:698-713` | yes | `ModeAuto::start_command` dispatch; comment at 698, function header at 699, `MAV_CMD_NAV_WAYPOINT → do_nav_wp(cmd)` at 713 |
| Forward-only `ArduCopter/mode_auto.cpp:1575-1614` | yes | `ModeAuto::do_nav_wp` opening |
| Forward-only `ArduCopter/mode_auto.cpp:2268-2295` | yes | `ModeAuto::verify_nav_wp` opening |

### Cite resolution summary
- Cites checked: 43 distinct path:line anchors across the plan.
- Cites that fully resolved at the pinned head: 43.
- Cites whose described concept did not match the code at the resolved location: 0.
- Cites with formatting / shorthand-displayed-text issues but correct resolution: F1-iter2 (Module 2.2 body `:476`/`:479`) and F2-iter2 (Verification block `[:NNN](…)` shorthand). Both are Nit.
- Cites with no issues: 41.

The plan's own verification claim at lines 478-501 was honest. iter1's F2 (parsing-vs-execution paraphrase) was a *description* defect at the resolved cite; iter2 dropped that cite and added forward-only cites whose descriptions match the code (verb is "execution" / "dispatch" / "completion-check"; the code does dispatch from `start_command`, set up a waypoint move in `do_nav_wp`, and check completion in `verify_nav_wp` — execution semantics, correct verb).

## Time-budget audit

| Day | Plan-declared total | Reviewer-summed modules + buffer | Delta |
|---|---|---|---|
| 1 | 4.0 h | 0.5 + 1.0 + 0.75 + 0.75 + 0.5 = **3.5 h modules** + 0.5 h buffer = **4.0 h** | 0 |
| 2 | 4.0 h | 0.75 + 0.75 + 0.75 + 1.25 = **3.5 h modules** + 0.5 h buffer = **4.0 h** | 0 |
| **Course** | **8.0 h** | **8.0 h** | **0** |

Buffer per day is 30 min, declared as a separate explicit slot **outside** the per-module sum (the iter1 F1 / F9 lessons applied). No double-counting.

Hands-on share, declared vs reviewer-recomputed:

| Day | Declared | Recomputed | Floor |
|---|---|---|---|
| 1 | ~59% (~2.05 / 3.5) | matches | ≥ 25% ✓ |
| 2 | ~41% (~1.45 / 3.5) | matches | ≥ 25% ✓ |

The Day 2 hands-on share is structurally load-bearing on the 1.25 h closing lab (without it, Day 2 hands-on drops to ~6%). The plan is honest about this in its own Verification block at line 508.

Capstone: **none declared**, no rubric requirement (course is 2 days). See "Capstone framing under the 2-day budget" above.

Buffer floor: each day declares 30 min explicit buffer. Rubric requires ≥ 30 min. **Floor met exactly.**

## Scope-vs-plan audit (plan-stage)

The scope-discipline rubric is mostly course-vs-plan; at plan stage I check internal consistency.

- **Internal consistency**: the Course Structure table (plan lines 148-152) matches the detailed module sections under each day (plan lines 158-305). No drift.
- **Lab spec round-trip**: every hands-on section in a module has a corresponding entry in **Handoff → To lab-builder** (L1, L2, L3); every lab entry has a corresponding lab-tester entry. No orphan labs. Mapping:
  - Module 1.2 hands-on ↔ L1 ↔ lab-tester L1.
  - Module 1.3 hands-on ↔ L2 ↔ lab-tester L2.
  - Module 2.4 hands-on ↔ L3 ↔ lab-tester L3.
  - Modules 1.1, 1.4, 1.5, 2.1, 2.2, 2.3 have only short in-module activities (≤ 10 min, all instructor-led or quick demos), not standalone labs — explicitly compatible with the brief.
- **Lab cuts from iter1**: L3, L4, L5, L6, L7 of iter1 are explicitly retired with rationale (D-cut1/2/3/4) at plan line 456. L1 and L2 carry forward unchanged; L8 carries forward as L3 with the autotest-warmup folded into Step A and tightened time budgets.
- **Sibling course non-import**: plan lines 514-519 assert no prose import from `course/custom_gnc_course_plane.md` or `course/custom_gnc_course_quadplane.md`. Plan stage cannot fully verify (no course draft yet); the design (re-derive operational topics from zero) is sound and the assumption-map table makes the conceptual overlap explicit and bounded.
- **Plan-reference line at end of course file**: plan tells course-writer to add `Generated from course/plans/plan-intro-arducopter-aero-y1-iter2.md` (plan line 144 / 399). Correct.

**No scope-discipline findings at plan stage.**

## Suggested rubric additions (the user may accept or reject)

iter1's review surfaced F3 (capstone-arc framing) and proposed two alternative rubric edits in `time-budget.md`. iter2 dodges F3 entirely by being below the ≥ 3-day trigger, so neither proposed rubric edit is needed for this course's verdict. The user may still want to commit one of them for general-purpose use; that is orthogonal to this review.

iter2's three Nit findings (F1-iter2, F2-iter2, F3-iter2) suggest one possible rubric clarification:

- **Proposed bullet** under `citation-rigor.md` "Clickable rendering": *"When a cite is emitted on the same Markdown bullet immediately after a full-form cite to the same path, the displayed text may shorten to `:NNN` (the link target must still be the full `path#LNNN` form). This is a readability accommodation, not a license to omit paths globally."*

This single bullet would close F1-iter2 and F2-iter2 without inflating verbose link text across the plan. The user decides whether to commit. **The reviewer does not write into `course/criteria/`.**

## Recommended next action

**iter2 is ready for course-writer.** Verdict: pass-with-findings; all findings are Nit-class citation-rigor formatting and do not block the writer. The plan:

- Honours every iter1 finding (carry-forward verified item by item).
- Sums every per-day budget exactly to the declared total, with no double-counting.
- Holds buffer at the rubric floor (30 min/day) explicitly.
- Avoids the capstone framing the rubric does not impose at 2 days.
- Delivers an enumerated 15-row prerequisite-chain assumption-map that the on-ramp identity demands.
- Drops three modules with rationale (D-cut1..D-cut4) that reduces audit surface and removes iter1 description defects (F2, F6, F8) from the load-bearing path.

The three iter2-introduced Nits are cosmetic and can be (a) fixed in passing by course-writer when it lifts the cites into the course file, (b) left as plan-internal shorthand and the course's audience-facing cites written in full form, or (c) closed by the proposed rubric clarification above. **None of the three justifies an iter3.**

Go: course-writer should proceed.

Generated against course/plans/plan-intro-arducopter-aero-y1-iter2.md at branch GNC-0.1, head a6fc842e04, 2026-04-26.
