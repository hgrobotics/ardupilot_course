# Lab L1 — First SITL Launch: Instructor Guide

## Lab summary for the instructor

**What the student is supposed to learn**: that the ArduPilot SITL toolchain is correctly installed on their own machine; that `sim_vehicle.py` starts a real autopilot binary whose MAVLink heartbeat is visible to a GCS. The lab has no flight; the entire pedagogical payload is environmental confidence.

**Depth marker**: *survey*. Students are not expected to understand what `sim_vehicle.py` does internally — [Tools/autotest/sim_vehicle.py:1073-1085](../../../../Tools/autotest/sim_vehicle.py#L1073-L1085) is read at survey depth in the module lecture. At this point they only need to know that typing one command produces a working simulator. Do not unpack the argument-parsing code, the SITL physics models, or the MAVLink dialect at this stage.

**How this lab feeds later modules**: every downstream lab (L2, L3, and all plane/quadplane labs) assumes `sim_vehicle.py` works. A student who leaves L1 with a broken environment will silently fail L2 and take lab time to diagnose. L1 is the cheapest place to catch environment problems. Plan for this lab to absorb environment failures that slipped through the Module 1.2 install.

**Downstream course connection**: the downstream GNC plane and quadplane courses ([course/custom_gnc_course_plane.md](../../../../course/custom_gnc_course_plane.md), [course/custom_gnc_course_quadplane.md](../../../../course/custom_gnc_course_quadplane.md)) use the identical `sim_vehicle.py -v ArduPlane -f quadplane` invocation pattern. A student who completes L1 successfully knows the pattern; only the vehicle name and frame flag change.

---

## Pacing

The headless agent test runs in approximately 1 second (binary start + heartbeat). The student-facing lab is budgeted at 15 minutes:

| Step | Expected wall-clock time | Notes |
|------|--------------------------|-------|
| Pre-condition check (binary exists?) | 1–2 min | Most students who completed Module 1.2 already have the binary. |
| Step 1 — Launch SITL | 1–2 min | Includes time for windows to open; SITL init to heartbeat is typically < 10 s. |
| Step 2 — Verify console | 2–3 min | Students need time to locate the firmware version string. |
| Step 3 — Verify map | 1–2 min | Map tile download may add latency on first launch if tiles are not cached. |
| Step 4 — Record | 2–3 min | Encourage students to actually write the version string; they will reference it in Step B.6 of L3. |
| Step 5 — Exit | < 1 min | |

**Total**: ~10 min typical; 15 min budgeted (buffer absorbs environment issues).

**Buffer**: if a student has not built the binary, `./waf copter` on a fresh configured tree takes 5–10 minutes on a typical laptop. If this happens, direct the student to start the build immediately and work with a neighbour's console for Steps 2–4 while waiting.

---

## Pre-arm setup checklist

Before students start:

- [ ] Confirm the ArduCopter SITL binary is already built on each student machine (`ls build/sitl/bin/arducopter`). If not, direct the student to run `./waf configure --board sitl && ./waf copter` from the repository root immediately.
- [ ] Confirm `mavproxy.py --version` succeeds (checks that MAVProxy is on PATH).
- [ ] Confirm `python3 -c "from pymavlink import mavutil; print('OK')"` succeeds.
- [ ] Confirm no stale SITL processes are running (`ps aux | grep arducopter`; kill any found).
- [ ] On machines with low RAM (< 4 GB), warn students that the map window may be slow.
- [ ] If students are on WSL2, verify the Windows X server (VcXsrv or similar) is running before the lab. The `--console` and `--map` flags require a display.

---

## Common student failures and what to say

**Exit code 10 from `test.sh` / "SITL binary not found"**

Diagnostic: `ls build/sitl/bin/arducopter`

What to say: "The binary was not built yet. Run `./waf configure --board sitl && ./waf copter` from the repository root — no sudo. Come back when the build finishes."

**Exit code 1 from `test.py` / no heartbeat within 30 s**

Diagnostic: `ps aux | grep arducopter` — look for a stale process holding port 5760.

What to say: "There is probably an old SITL instance still running. Kill it, then re-run the launch command."

**`ImportError: No module named pymavlink` in `test.py`**

Diagnostic: `python3 -c "from pymavlink import mavutil"`

What to say: "The Python prerequisites are not installed in the active Python environment. Re-run `Tools/environment_install/install-prereqs-ubuntu.sh` and open a new terminal."

**Map window does not open or shows blank tiles**

This is a display issue, not a SITL issue. The lab pass criterion is the heartbeat only — the map is an observation aid. Tell the student to verify Steps 2 and 4 (console and heartbeat) and move on.

**`sim_vehicle.py` exits immediately with `waf: error:`**

`sim_vehicle.py` without `-N` tries to rebuild. Without `-N` and with a misconfigured `waf`, it can fail. Confirm the student is using `-N` (no rebuild) or that the binary already exists.

---

## Verdict signatures

The automated harness (`test.sh` + `test.py`) checks exactly one thing:

| Signal | Check | Pass value |
|--------|-------|------------|
| TCP connection to `127.0.0.1:5760` | `socket.connect` succeeds within 10 s | connected |
| MAVLink HEARTBEAT | `mav.wait_heartbeat(timeout=30)` | received within 30 s |

Exit codes:

| Code | Meaning |
|------|---------|
| `0` | PASS — heartbeat received |
| `1` | FAIL — heartbeat not received within 30 s |
| `10` | FAIL — binary not found or pymavlink import error |

Student-visible GCS checks (not tested by the harness, but expected by the lab spec):

- `APM:Copter V` in the MAVProxy console (STATUSTEXT at `MAV_SEVERITY_INFO`)
- Mode `STABILIZE`, armed state `DISARMED`
- No `MAV_SEVERITY_CRITICAL` or `MAV_SEVERITY_EMERGENCY` STATUSTEXT during this lab

---

## Pointers to advanced material

- The `sim_vehicle.py` argument-parsing block at [Tools/autotest/sim_vehicle.py:1073-1085](../../../../Tools/autotest/sim_vehicle.py#L1073-L1085) is where `-v ArduCopter` and `-f quad` are handled. The downstream GNC courses use `-v ArduPlane -f quadplane`; the code path is identical.
- The single-line binary lookup at [Tools/autotest/sim_vehicle.py:287](../../../../Tools/autotest/sim_vehicle.py#L287) shows how `sim_vehicle.py` finds `ArduCopter.elf`. This is the entry point for a deeper `--help` walk in Module 1.2.
- The downstream GNC quadplane course's Day 1 introduces `sim_vehicle.py` flags for custom locations (`--home`) and speedup (`--speedup`). Students will reuse their L1 confidence with the basic invocation.
