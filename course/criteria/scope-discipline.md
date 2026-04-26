# Rubric: Scope discipline

A course must follow its plan. Drift between plan and draft is the failure mode that quietly inflates length, mismatches audience, and breaks downstream lab specs.

## Required

- **Plan reference**: the course file ends with a `Generated from course/plans/plan-<slug>.md` line. Without it, the reviewer cannot run a scope audit and the verdict is FAIL.
- **Module set parity**: the set of modules in the course matches the set in the plan. No additions, no removals, no reorderings, unless explicitly recorded as a deviation.
- **Module heading parity**: each course module's heading matches the plan's heading verbatim (modulo trivial typo fixes).
- **Time-budget parity**: each module's stated time matches the plan's time within ±15 min.
- **Lab spec parity**: each module's hands-on section matches the plan's lab spec — same fault injections, same success criteria, same vehicle/frame.
- **Deviation record**: any deviation from the plan must appear in the course file's "Citation drift report" or a sibling "Deviations" section, with the rationale. Silent deviations are findings.

## Forbidden

- Adding a module the plan did not list, even a small one.
- Splitting one planned module into two, or merging two into one, without a deviation record.
- Promoting an "optional" plan item to required, or demoting a required item to optional.
- Bringing in content from a sibling course (e.g. material from `custom_gnc_course_plane.md` into `custom_gnc_course_quadplane.md`) that the plan did not authorize.
- Expanding a module's time by > 15 min to fit the writer's research, without a deviation record.

## Severity guide for the reviewer

- **Blocker**: plan reference is missing, OR a module exists in the course but not the plan (or vice versa) with no deviation record, OR > 1 h of time-budget drift across the course.
- **Major**: module headings drift in meaning (not just typos), OR a lab spec in the course materially differs from the plan's spec.
- **Minor**: time-budget drift 15–30 min on individual modules, OR ordering swap within a day with no deviation record.
- **Nit**: trivial heading wording differences.

## Verification recipe

The reviewer:
1. Extracts the module list from the plan and from the course (heading + time).
2. Diffs them. Any non-trivial diff is a finding unless covered by a deviation record.
3. Sums course-side and plan-side time budgets per day; flags any per-day delta > 30 min.
4. For each module's hands-on section, compares the spec text against the plan's "Handoff → To lab-builder" entry.
