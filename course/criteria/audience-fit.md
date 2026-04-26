# Rubric: Audience fit

Course depth must match the audience the plan declares. Material that is too shallow wastes their time; too deep loses them.

## Required

- **Audience declaration**: the plan's Context section names the audience explicitly — role, prior tools, target vehicle. The course preamble repeats this declaration verbatim.
- **Prerequisite list**: things the course assumes the learner already knows. Concrete (e.g. "C++ proficiency, MAVLink message protocol, basic Kalman filter intuition"), not vague ("software experience").
- **Compression discipline**: topics the audience already knows are compressed to a survival-kit reference, not re-taught. The plan must declare which topics are compressed.
- **Depth markers**: every module declares its depth as one of:
  - *survey* — name and purpose, no internals
  - *applied* — how to use it, with one or two internals callouts
  - *internals* — code-as-implementation, file:line walks, edge cases
- **Depth consistency**: the depth marker matches the prose. An "internals" module that does not cite ≥ 5 file:line anchors is a finding. A "survey" module that walks function bodies is a finding.
- **Vocabulary calibration**: jargon used without definition must be on the prerequisite list. New jargon introduced in-course must be defined inline at first use.
- **Prerequisite-chain awareness**: if the course is positioned as an on-ramp to another course in this repo, the plan must name the downstream course and identify what assumptions the downstream course makes that this course is responsible for establishing.

## Forbidden

- Re-teaching material the prerequisite list already assumes.
- Mixing depths within a module without flagging the shift ("this module is mostly applied, with a 20-min internals dive into errorScore()").
- Audience drift: a course declared for "GNC engineers familiar with proprietary autopilots" that opens with "what is a flight controller?".
- For first-year / novice audiences, internals-depth modules are forbidden unless explicitly justified — the audience cannot consume them. Survey and applied are the working depths.
- Citations to AI/agent coordination files (`AGENTS.md`, `CLAUDE.md`, `.claude/`, `MEMORY.md`, repo-root meta docs) as pedagogical material. These files coordinate AI agents on the codebase; they are not autopilot teaching material. If the *substance* of such a file matters, inline it as the course author's voice or redirect the cite to the actual source it describes (e.g., a real `@Param` block in `ArduCopter/Parameters.cpp`, not the example in `AGENTS.md`).
- Meta-curriculum directives in student-visible prose: sentences telling the instructor what NOT to teach ("do not derive", "do not unpack", "we are at survey", "out of scope here", "resist deepening") belong in instructor-only blocks (slides: `\instnote{}`; handouts: instructor-edition `tcolorbox`), not in the body that students read. A student-facing "stop reading at this line — that is enough" is course content; an instructor-facing "do not unpack the algebra — we are at survey" is curriculum framing. Reviewers must treat directive prose appearing in a student build as a finding.

## Severity guide for the reviewer

- **Blocker**: course preamble's audience does not match the plan's audience, OR a full day is taught at a depth that contradicts its modules' depth markers.
- **Major**: a module's depth marker does not match its content, OR > 20% of a day re-teaches prerequisite material.
- **Minor**: occasional jargon-without-definition, OR depth shifts within a module that aren't flagged.
- **Nit**: depth markers absent on individual modules but inferable from context.

## Verification recipe

The reviewer reads the plan's Context, then samples 3 modules per day:
- Does the prose's vocabulary level match the declared audience?
- Does the depth marker match the file:line citation density?
- Are introduced terms defined inline or covered by prerequisites?
