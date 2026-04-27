# Lab L2 Instructor Guide — AP_GROUPINFO Add + Observe

## Lab summary for the instructor

**Learning objective:** The engineer can add a typed parameter to a live
ArduPilot vehicle class, annotate it correctly with `@Param`, add an
`AP_GROUPINFO` entry at a unique index, rebuild, and observe the parameter
through the MAVLink `PARAM_VALUE` stream. The secondary objective is to confirm
NVM persistence via the EEPROM re-read on restart.

**Depth:** internals — engineers are reading `Parameters.cpp` and
`AP_PARAM_FLAG_*` defines, not just clicking in a GCS.

**Feed-forward:** `AP_GROUPINFO` is the universal parameter registration
mechanism across all ArduPilot subsystems. Every subsequent lab modifies or
observes parameters from this same table. Understanding the index-is-baked-in
constraint here prevents confusion when the engineers look at real subsystems
in M5's code walk.

## Pacing

| Step | Expected wall time |
|------|--------------------|
| Patch apply + rebuild | 1–3 min |
| SITL launch + param show | < 1 min |
| param set + restart + verify | 2–3 min |
| Discussion: how EEPROM maps to NVM on real hardware | 5–10 min |
| Clean-up (git checkout) | < 1 min |
| **Total** | **~15 min** |

Budget 30 min including M5's code walk of `AP_GROUPINFO` internals. If you are
at minute 25 and still on Step 6, compress the discussion — the data point
(42.0 persists) is the essential outcome.

## Pre-arm setup checklist

- [ ] `git status` shows a clean tree (no pending modifications to `ArduPlane/`).
- [ ] SITL binary built: `build/sitl/bin/arduplane` exists.
- [ ] `pymavlink` installed in the Python env the test harness will use.
- [ ] Projector shows `ArduPlane/Parameters.cpp` around line 1290 so students
  can see the `AP_GROUPEND` they are inserting before.

## Common student failures and what to say

| Symptom / exit code | Diagnostic command | What to say |
|---|---|---|
| `MY_PARAM` not in list (exit code 2) | `file build/sitl/bin/arduplane; strings build/sitl/bin/arduplane | grep MY_PARAM` | "The binary was not rebuilt after patching. Run `./waf plane` and re-launch SITL." |
| Compilation error: `error: no member named 'my_param' in 'ParametersG2'` | `grep my_param ArduPlane/Parameters.h` | "The `.h` file change is missing. Check the patch applied to both files: `git diff --stat`." |
| Index conflict error | `grep '42,' ArduPlane/Parameters.cpp \| head` | "Index 42 is already used. Open Parameters.cpp, find a gap (e.g. 43 is free), and change the patch." |
| MY_PARAM reverts after restart (exit code 4) | `ls -t *.bin eeprom.bin 2>/dev/null` from the SITL working dir | "The EEPROM file is in a different directory. Run both launches from the repo root with `--no-rebuild`." |
| SET not acknowledged (exit code 3) | Check SITL stdout for `param set` error | "Rare. Restart SITL; occasionally the first session exits before flushing the EEPROM." |

## Verdict signatures

The headless harness checks:

1. `PARAM_VALUE` for `MY_PARAM` in `[16.9, 17.1]` on the first connection.
2. `PARAM_VALUE` for `MY_PARAM` in `[41.9, 42.1]` after SET.
3. `PARAM_VALUE` for `MY_PARAM` in `[41.9, 42.1]` on the second connection
   (persistence check).

An engineer who reports "42.0 persisted" has passed the lab.

## Pointers to advanced material

When an engineer asks "what happens if two subsystems accidentally use the same
index?": the compile-time check is a static assert in `AP_Param.cpp` that
catches duplicates within the same group. But mismatched indices across restarts
— i.e. a firmware upgrade that inserts a parameter at an existing index —
silently writes the wrong value. This is the "indices are baked into user
configs" constraint from `AGENTS.md`; it matters when migrating a production
fleet. The downstream GNC adoption module revisits this when the engineers
extract `AP_TECS` and see how to isolate the parameter table from the vehicle
binary.
