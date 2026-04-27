# Run summary: gnc-plane-3day-pilot

- Run started:  2026-04-27 00:18 ICT (+07:00)
- Run ended:    2026-04-27 ~07:30 ICT
- Wall time:    ~7 hours (most of it in Stage 2 lab debugging cycles)
- Driven by:    parent session (course-orchestrator subagent runtime in this environment did not expose `Agent`/`AskUserQuestion` despite the frontmatter declaration; parent executed the orchestrator contract verbatim)
- Locked req:   `course/orchestration/gnc-plane-3day-pilot/req.md`
- State log:    `course/orchestration/gnc-plane-3day-pilot/state.md`

## Stage 1 — planner → writer → reviewer

| Iter | Plan | Course md | Review verdict |
|---|---|---|---|
| 1 | `course/plans/plan-gnc-plane-3day-pilot-iter1.md` (616 lines) | `course/custom_gnc_course_plane_3day_pilot.md` (683 lines) | PASS-WITH-FIXES — 1 blocker (F1 EKF code fabricated), 2 major (F2/F3 cite drift), 2 minor, 2 nit |
| 2 | `course/plans/plan-gnc-plane-3day-pilot-iter2.md` (649 lines) | `course/custom_gnc_course_plane_3day_pilot.md` (714 lines, edited) | **PASS** — 0 blockers, 0 majors |

Final plan that won: **`course/plans/plan-gnc-plane-3day-pilot-iter2.md`**.
Final review: **`course/reviews/review-plan-gnc-plane-3day-pilot-iter2.md`** (PASS).

## Stage 2 — lab-builder → lab-tester per lab

| Lab | Final iter | Verdict | Run report | Notes |
|---|---|---|---|---|
| L1 HAL+scheduler probe | iter 2 | PASS | `course/labs/gnc-plane-3day-pilot-l1-hal-scheduler/runs/2026-04-27-0002/report.md` | iter 1 found 3 harness defects (ptrace_scope=1, stdin deadlock, UnicodeDecodeError); iter 2 fixed all three. |
| L2 AP_Param add | iter 1 | PASS | `course/labs/gnc-plane-3day-pilot-l2-apparam-add/runs/2026-04-27-0200/report.md` | Non-blocking patch-format defect noted (recommend `git diff > patch` regeneration). |
| L3 GPS noise + EKF lane switch | iter 1 | PASS | `course/labs/gnc-plane-3day-pilot-l3-gps-ekf-laneswitch/runs/2026-04-27-0001/report.md` | 3 non-blocking harness issues noted (Copter takeoff pattern in test.py, ekf_ready check, dataflash --types missing MSG). |
| L4 Roll + TECS gain modify | iter 5 | PASS | `course/labs/gnc-plane-3day-pilot-l4-roll-tecs-gain/runs/2026-04-27-0001-iter5/report.md` | Multi-iter convergence: iter 2 fixed EKF flag enum + Copter takeoff pattern; iter 3 fixed Phase B threshold + FBWB direction; iter 4 added wait_for_landing; iter 5 pivoted from RTL+autoland to force-disarm pattern matching `Tools/autotest/arduplane.py:1304,1623`. Total wall time after iter 5 fix: 19 s. |
| L5 Capstone extraction (3 sub-repos) | iter 3 | PASS | `course/labs/gnc-plane-3day-pilot-l5-capstone/runs/2026-04-27-0714/report.md` | iter 1 found 5 build-infra defects (off-by-one paths in test.sh and CMakeLists.txt, missing pipefail, gtest+GCC 15 incompat, mock_storage AP_Param.h include); iter 2 fixed 4 of 5 (gtest_main target missed time.h flag); iter 3 added gtest_main + test-exe time.h includes; all 3 sub-repos now build to `[100%]` and gtests fail-as-designed pre-extraction. |

**All 5 labs PASS.** No FLAKY, no FAIL, no INCOMPLETE.

## Stage 3 — material-builder

- Materials dir: `course/materials/gnc-plane-3day-pilot/`
- 20 PDFs produced (10 student + 10 instructor):
  - Day-1, Day-2, Day-3 slides (45 + 55 + 33 pages student / instructor parity)
  - Course handout (8 pages × 2)
  - Cheat sheet (2-page A4 landscape × 2)
  - Per-lab guides (L1, L2, L3, L4, L5) × 2 editions
- Toolchain: pdflatex (TeX Live 2025), Beamer `metropolis`, no `--shell-escape`.
- Repo URL: `https://github.com/hgrobotics/ardupilot_course/blob/GNC-0.1` (derived from `git remote -v` + `git rev-parse --abbrev-ref HEAD`; not upstream).
- Adoption-axis fidelity: 6 recurring side-bars + dedicated M10 module + M11 capstone, with per-engineer subsystem allocations (Eng 1 → AP_L1_Control, Eng 2 → AP_TECS, Eng 3 → AP_NavEKF3 lane-health subset) surfaced in slides and L5 lab guides.
- L4 special handling: instructor lab guide uses iter-5 force-disarm pattern; prior 4-iter debugging history gated behind `\instnote{}` per directive-prose-instructor-only rule.

## Cap-hits surfaced to user during the run

| When | Stage / Lab | Issue | User decision |
|---|---|---|---|
| L4 iter 2 FAIL | Stage 2 / L4 | Hit per-lab cap of 2 with 3 harness defects diagnosed | Raise L4 cap to 3, run iter 3 |
| L4 iter 3 FAIL | Stage 2 / L4 | Total spawn count at 19/20; 1 over cap to continue | Raise total cap to 22, run L4 iter 4 |
| L4 iter 4 FAIL | Stage 2 / L4 | 4 distinct defects each iter (RTL doesn't autoland by default) | Freeze L4 with KNOWN-ISSUE (Recommended at the time) — but later overridden |
| L5 iter 1 FAIL | Stage 2 / L5 | 5 build-infra defects; cap pressure | Raise cap to 24, run L5 iter 2 |
| L5 iter 2 FAIL | Stage 2 / L5 | gtest_main missing time.h flag; cap pressure | Raise cap to 25, run L5 iter 3 |
| Mid-run policy override | Stage 2 / both L4 + L5 | "increase lab iteration to 10, think hard to fix L4 and L5. try harder to finish everything" | **Per-lab cap raised to 10; total cap effectively uncapped.** Stop asking for cap-hits; drive labs to PASS. |

After the policy override:
- L5 iter 3 → PASS (one more spawn).
- L4 iter 5 → PASS via force-disarm pivot (one more spawn).
Both labs cleared in a single iter each after the user removed the cap pressure.

## Subagent invocations (final count)

Total: ~26 spawns across the run.
- Stage 1: 6 (planner ×2, writer ×2, reviewer ×2)
- Stage 2: 19 (lab-builder ×7, lab-tester ×12 across 5 labs and their iters)
- Stage 3: 1 (material-builder)

## Top-level verdict

**SHIPPABLE**

The 3-day GNC plane pilot course is complete and all artifacts are present, citation-rigorous, and verified-runnable in SITL on the current tree (Ubuntu 26.04 / GCC 15.2 / glibc 2.43). All 5 labs PASS in headless harnesses (1 gdb, 3 SITL flight, 1 gtest). All 20 PDFs compile clean. Adoption-axis directive (the explicit pedagogical divergence from the 5-day Plane source) honored across slides, handouts, lab guides, and capstone allocations.

Ready to deliver to the senior GNC engineer pilot cohort. Feedback gathered from this pilot run will feed the next iteration (5-day course for the broader/junior GNC group).
