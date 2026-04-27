# Lab L1 Student Guide — HAL + Scheduler Probe

## What you will do

In this lab you will attach the GNU debugger to a running ArduPlane SITL process
and read two live values straight out of the flight-control loop: the HAL
monotonic clock (`AP_HAL::millis()`) and the active scheduler loop rate
(`AP::scheduler().get_loop_rate_hz()`). This is not a flying lab — the plane
does not take off. The goal is to confirm that the Hardware Abstraction Layer
(HAL) is a real, callable interface, not just documentation, and that the
scheduler truly runs at 50 Hz for a fixed-wing vehicle. After this lab you will
have a mental model of how ArduPilot maps "main loop tick" to the HAL clock, a
skill you will build on in every subsequent lab.

## Before you start

- You must have completed the build step from Module M3:
  `./waf configure --board sitl --debug && ./waf plane`.
  Check that `build/sitl/bin/arduplane` exists and was built recently.
- `gdb` must be installed. Verify: `gdb --version`.
- Open two terminal windows side by side, both `cd`'d to the repository root
  (`/home/mahisorn/repos/ardupilot_course`).
- You do not need MAVProxy, a GCS, or a display server for this lab.

## The steps

### Step 1 — Build the debug binary (if not already built)

In Terminal A:

```
./waf configure --board sitl --debug
./waf plane
```

### Step 2 — Start SITL without MAVProxy

In Terminal A:

```
Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --debug --no-mavproxy
```

You will see text like `SIM_VEHICLE: Starting ArduPlane SITL ...`. Leave this
terminal running.

### Step 3 — Find the process ID

In Terminal B:

```
pgrep arduplane
```

Note the number printed (for example, `12345`). That is the PID.

### Step 4 — Attach gdb

In Terminal B:

```
gdb build/sitl/bin/arduplane -p $(pgrep arduplane)
```

You will see the gdb banner and then the `(gdb)` prompt.

### Step 5 — Set a breakpoint on the HAL update function

At the `(gdb)` prompt:

```
(gdb) b Plane::ahrs_update
```

gdb should respond with something like:
```
Breakpoint 1 at 0x5555557c8abc: file ArduPlane/Plane.cpp, line 167.
```

### Step 6 — Continue until the breakpoint fires

```
(gdb) c
```

Within a second or two (the function runs at 50 Hz), you will see:
```
Breakpoint 1, Plane::ahrs_update () at ArduPlane/Plane.cpp:167
```

### Step 7 — Read the HAL clock

```
(gdb) print AP_HAL::millis()
```

You should see something like `$1 = 3471`. The exact value does not matter; what
matters is that it is greater than zero.

### Step 8 — Read the scheduler loop rate

```
(gdb) print AP::scheduler().get_loop_rate_hz()
```

You should see `$2 = 50`. This is the plane-default value defined in
`libraries/AP_Scheduler/AP_Scheduler.cpp:46`.

### Step 9 — Detach and quit

```
(gdb) detach
(gdb) quit
```

### Step 10 — Stop SITL

Switch to Terminal A and press Ctrl-C.

## What success looks like

- gdb says `Breakpoint 1 at ... ArduPlane/Plane.cpp, line 167`
  (or a nearby line — the exact line may shift between builds).
- After `c`, gdb stops and prints `Breakpoint 1, Plane::ahrs_update`.
- `print AP_HAL::millis()` prints a positive integer.
- `print AP::scheduler().get_loop_rate_hz()` prints `50`.

If instead you see `no symbol "Plane::ahrs_update" in current context`, the
binary was not built with debug symbols. Go back to Step 1 and make sure you
used `--debug` in the configure step.

If `print AP_HAL::millis()` prints `0`, gdb is evaluating the function in a
context where the HAL is not yet live. Let the breakpoint fire once more with
another `(gdb) c`, then try again.

## Common mistakes and quick fixes

1. **"no symbol Plane::ahrs_update"** — you forgot `--debug` in `./waf configure`.
   Run `./waf configure --board sitl --debug && ./waf plane` and restart.

2. **gdb attaches but immediately shows a stopped state (SIGSTOP)** — this is
   normal; SITL is paused while gdb attaches. Just type `c` to resume.

3. **pgrep prints nothing** — SITL is not running. Switch to Terminal A and check
   it started. If `sim_vehicle.py` is still building, wait for the `Starting`
   message before running pgrep.

4. **gdb says "ptrace: Operation not permitted"** — your OS requires ptrace
   permission. Run:
   ```
   echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
   ```
   Then retry the gdb attach command.

5. **The breakpoint fires too fast and gdb floods the screen** — type `(gdb) c 1`
   to single-step through one invocation, take your readings, then detach.

## Where to go next

Next is Lab L2 (Module M5 — AP_GROUPINFO add + observe), where you will add a
new parameter to `ArduPlane/Parameters.{h,cpp}`, rebuild, and watch it persist
across SITL restarts. The same debug build you just confirmed is the starting
point for L2.
