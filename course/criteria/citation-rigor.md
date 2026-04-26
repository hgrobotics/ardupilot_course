# Rubric: Citation rigor

Every reference to ArduPilot source code in a course or plan must be verifiable, current, and load-bearing.

## Required

- **Format**: `path/to/file.cpp:LINE` or `path/to/file.cpp:START-END`. Always relative to the repo root. Never bare filenames, never `~` paths, never line-less references when a specific line is meant.
- **Clickable rendering**: every cite is written as a markdown link so it resolves to the actual code on GitHub (and in editors that follow markdown links). Displayed text is the `path:line` form above; the link target is the same path with a GitHub-compatible line anchor:
  - Single line: `[ArduCopter/mode.cpp:42](../ArduCopter/mode.cpp#L42)`
  - Range: `[ArduCopter/mode.cpp:42-58](../ArduCopter/mode.cpp#L42-L58)`
  - The link's path is **relative to the markdown file's directory** (e.g., from `course/foo.md` use `../ArduCopter/...`; from `course/plans/plan.md` use `../../ArduCopter/...`). Bare `path:line` strings without a markdown link are a Nit finding.
- **Anchor existence**: every cite must resolve in the current tree. The reviewer will run `grep -n` (or read the file at the line) for each cite. A cite that does not match — wrong file, wrong symbol, drifted line range — is a finding.
- **Anchor specificity**: a cite must point at the symbol or block being discussed, not the top of the file. `AP_NavEKF3.cpp:759-877 (InitialiseFilter)` is correct; `AP_NavEKF3.cpp` alone is not.
- **Symbol naming**: when a cite identifies a function, class, or parameter, use the source name verbatim. `errorScore()`, `checkLaneSwitch()`, `Q_TRANSITION_MS`, `EK3_IMU_MASK`. No paraphrasing.
- **Line-range tightness**: ranges are 5–150 lines. Wider ranges are vague; narrower ranges drift faster. If the discussed block is larger, cite the function header line and describe the structure in prose.
- **Submodules**: cites into `modules/` are forbidden. Reference upstream by symbol name only.
- **Drift handling**: if a cite drifted between planning and writing, the writer must update the cite and record the change in the course's "Citation drift report" section.

## Forbidden

- Cites that paraphrase symbol names (`error_score` when the source has `errorScore`).
- Round-numbered ranges that suggest the cite was guessed (`AP_NavEKF3.cpp:1000-2000`).
- Cites to deleted code, with a note like "this used to be at...". Either the current cite resolves or the cite is removed.
- Cites without line numbers when the discussion is about a specific block.

## Severity guide for the reviewer

- **Blocker**: any cite that does not resolve in the current tree, OR ≥ 10% of cites in a module fail to resolve.
- **Major**: cite resolves but to the wrong symbol, OR line range is off by > 50 lines.
- **Minor**: line range off by ≤ 50 lines but symbol matches.
- **Nit**: formatting (path style, range punctuation).

## Verification recipe

```sh
# Symbol exists in the cited file?
grep -n '<symbol>' <path>

# Line range still bounds the symbol?
sed -n '<start>,<end>p' <path> | head -20
```
