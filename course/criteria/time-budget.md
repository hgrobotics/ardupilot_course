# Rubric: Time budget

A course is a real schedule. The total declared length, the per-day totals, and the per-module times must add up and must be defensible.

## Required

- **Course total**: stated up front (e.g. "5 days / ~34 h"). Per-day totals must sum to within ±1 h of this total.
- **Per-day total**: stated at the start of each day section. Per-module times within that day must sum to within ±15 min of the day total.
- **Per-module time**: every module declares a time budget in hours or half-hours (`1h`, `1.5h`, `2.5h`). No "approximately" — pick a number.
- **Hands-on share**: each day must include ≥ 25% hands-on time (lab, build, debug, log analysis). A theory-only day is a finding.
- **Capstone**: any course ≥ 3 days must include a capstone exercise consuming ≥ 2 h.
- **Buffer**: each day must include ≥ 30 min of buffer (Q&A, breaks, slippage). Stated explicitly, not absorbed into other modules.

## Forbidden

- Modules with no declared time.
- Per-day totals that diverge from the sum of their modules by > 15 min without an explicit "buffer / Q&A" line accounting for the gap.
- Course totals that diverge from per-day sums by > 1 h.
- Hands-on time ratios computed implicitly. Each day's hands-on share must be visible.

## Severity guide for the reviewer

- **Blocker**: per-day totals do not sum to the course total within ±1 h, OR a day claims a duration the modules cannot fill.
- **Major**: per-module times do not sum to the per-day total within ±30 min, OR hands-on share < 15% on any day.
- **Minor**: hands-on share 15–25%, OR buffer time absent on a day < 4 h.
- **Nit**: time format inconsistency (`90 min` vs `1.5h`).

## Verification recipe

The reviewer extracts every `(time)` declaration per day, sums them, and compares to the day total and to the course total.
