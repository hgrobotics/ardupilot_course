# ArduPilot for GNC Engineers — QuadPlane Edition

## Custom Training Course — Detailed Curriculum

**Duration**: ~34 hours (5 days)
**Audience**: GNC engineers with C/C++ proficiency and significant flight-code experience on a proprietary autopilot stack. Comfortable with Kalman filtering, control theory, and embedded debugging. New to ArduPilot.
**Target platform**: **QuadPlane** (fixed-wing VTOL). Engineers will fly, tune, and modify a QuadPlane in production.
**Goal**: Make the team productive in ArduPilot's source — architecture, build, navigation filtering, sensor-error handling, EKF lane management, and the QuadPlane transition state machine — by walking real `file:line` citations rather than abstract concepts.

**Relationship to other course files**: The fixed-wing-only baseline lives in [`custom_gnc_course_plane.md`](custom_gnc_course_plane.md) (untouched). This QuadPlane edition is the canonical course for teams whose target platform is VTOL. Topics that are pure fixed-wing (e.g., deep TECS internals, soaring, deepstall) are summarized here and cross-referenced to the baseline.

---

## What This Course Assumes (and What It Skips)

Because the audience already operates a proprietary autopilot, this course **skips**:

- MAVLink packet structure, mission protocol theory, command-vs-message taxonomy.
- Generic sensor concepts (what an IMU is, what differential pressure measures).
- Kalman filter derivation, covariance update math, Jacobian theory.
- "How to fly a drone" / RC operations.
- Indoor flight, vehicle assembly, tuning-by-feel.

It **focuses on**:

1. ArduPilot's specific code organization and build system.
2. **Navigation filtering as code**: AP_NavEKF3 layout, innovation gates, source sets, wind-state estimation.
3. **EKF lane-switch logic**: `errorScore()`, hysteresis, `checkLaneSwitch()`, source failover, GSF yaw fallback.
4. **Navigation-sensor error detection and handling**: airspeed health, GPS glitch, IMU consistency, compass anomaly, baro/rangefinder, with the `ekf_check` → lane-switch → failsafe action ladder.
5. **QuadPlane internals**: dual control-system architecture, Q-modes, the `SLT_Transition` state machine, motor blending, `VTOL_Assist`, thrust-loss handling, Q-failsafe.
6. Custom-board porting tailored to a quadplane hwdef (4 VTOL motors + plane servos + airspeed + dual-IMU).
7. A capstone fault-injection lab on QuadPlane-in-SITL that synthesizes everything.

---

## Day-by-Day Outline

| Day | Theme | Hours |
|-----|-------|-------|
| 1 | ArduPilot Orientation for Experienced Engineers | 5 |
| 2 | Architecture & Infrastructure (HAL, scheduler, params, sensors) | 7 |
| 3 | Navigation Filtering, Sensor Errors & Failsafes | 7 |
| 4 | QuadPlane: Architecture, Transitions & Failure Modes | 7 |
| 5 | Custom Hardware, Capstone & Q&A | 8 |
| | **Total** | **34** |

---

## Day 1 — ArduPilot Orientation for Experienced Engineers (5h)

The compressed survival kit. Drops generic operations material; keeps only what is genuinely ArduPilot-specific.

### Module 1 — ArduPilot Ecosystem & Vehicle Class Map (1h, lecture)

**Objective**: Place ArduPilot in the autopilot landscape and frame QuadPlane as a hybrid before any code is shown.

- Project history and governance (release cadence, dev/beta/stable, contribution model).
- Vehicle types: Copter, Plane, Rover, Sub, AntennaTracker, Blimp.
- **QuadPlane is a hybrid**: it lives inside `ArduPlane/` (`ArduPlane/quadplane.h`, `ArduPlane/quadplane.cpp` ~5000 LOC). The `Plane` vehicle class owns a `QuadPlane` member; both fixed-wing and VTOL controllers run within one binary.
- Repo tour: vehicle dirs, `libraries/` (~150 dirs), `modules/` (submodules, do not modify), `Tools/` (autotest, scripts).
- Naming prefixes: `AP_*` general, `AC_*` copter-flavored (used by QuadPlane VTOL stack), `AR_*` rover.

**Files shown**: `ArduPlane/Plane.h`, `ArduPlane/quadplane.h:34-770`, `libraries/` listing.

### Module 2 — SITL & Tooling Survival Kit (2h, lecture + hands-on)

**Objective**: Get every engineer running QuadPlane SITL and reading dataflash logs by lunch.

- SITL launch for QuadPlane: `Tools/autotest/sim_vehicle.py -v ArduPlane -f quadplane --console --map`. Frame string `quadplane` selects the QuadPlane physics model.
- MAVProxy idioms specific to ArduPilot: `param set/show`, `mode QHOVER`, `arm throttle`, `wp list`, `module load map`. Loading a mission file into SITL.
- MAVExplorer dataflash conventions — log message names you will see all week:
  - **Attitude/control**: `ATT`, `CTUN`, `NTUN`.
  - **EKF3**: `XKF1` (states), `XKF2` (more states), `XKF3` (innovations), `XKF4` (variances + lane index), `XKF5` (output predictor), `XKFD` (drag).
  - **QuadPlane**: `QTUN` (`ArduPlane/quadplane.cpp` log writers near `:3761`), `QPOS` (position-controller state, near `:3812`).
  - **Sensors**: `ARSP` (airspeed + health probability), `BARO`, `GPS`, `MAG`, `IMU`, `VIBE` (vibration), `RFND` (rangefinder).
  - **Errors/events**: `ERR`, `MSG`, `EV`.
- Skipped (in pre-read handout): MAVLink packet format, generic mission protocol, MAVProxy install. Engineers already understand the protocol equivalents from their stack.

**Hands-on (45 min)**:
1. Launch QuadPlane SITL.
2. Take off in QHOVER, transition to FBWA, fly a square, transition back, QLAND.
3. Download the dataflash log, open in MAVExplorer.
4. Plot `XKF4.SS` (lane index over time), `QTUN.ThI` (motor throttle in), `CTUN.NavRoll`, `ARSP.Health` simultaneously. Identify the transition timestamps from the data alone.

### Module 3 — Build System & Code Conventions (2h, lecture + hands-on)

**Objective**: Make every engineer fluent enough in Waf and ArduPilot's idioms to navigate and modify code by themselves.

- Waf two-phase: `./waf configure --board <board>` then `./waf plane`. Never run with `sudo`.
- Targets: `./waf list_boards`, `./waf list`, `./waf --targets <name>`, `./waf check` (changed gtest), `./waf check-all`.
- SITL: `./waf configure --board sitl`. Add `--debug` for GDB symbols.
- Hardware: `./waf configure --board CubeOrange` (most representative current Pixhawk-class board).
- `Tools/scripts/build_options.py` is the master feature-flag list. `AP_<FEATURE>_ENABLED` macros gate every optional subsystem.
- ArduPilot-isms that bite engineers from other stacks:
  - `AP_HAL::millis()` / `AP_HAL::micros()` for time. **Never** `std::chrono` or platform headers in shared code.
  - `is_zero(x)`, `is_positive(x)`, `is_negative(x)` for float comparisons.
  - `GCS_SEND_TEXT(MAV_SEVERITY_INFO, "...")` for user-facing messages — not `printf`.
  - `AP_GROUPINFO(...)` declares params; **indices are stored in EEPROM, never renumber**.
  - Singletons via `AP::xxx()` (e.g., `AP::ahrs()`, `AP::gps()`, `AP::baro()`).
  - Per-`#pragma once` headers (no include guards).
  - astyle-formatted, K&R braces, 4-space indent. Format only the lines you change.

**Hands-on (45 min)**:
1. Configure SITL and build QuadPlane: `./waf configure --board sitl && ./waf plane`.
2. Configure CubeOrange and build: `./waf configure --board CubeOrange && ./waf plane`. Note cross-toolchain auto-fetch.
3. Build and run a unit test: `./waf --targets tests/test_math && ./build/sitl/tests/test_math`.
4. Open `ArduPlane/wscript` and `libraries/AP_NavEKF3/wscript`. Identify dependencies.
5. Find one `AP_<FEATURE>_ENABLED` macro in `build_options.py`, toggle it, rebuild, observe binary-size delta in `build/sitl/bin/`.

---

## Day 2 — Architecture & Infrastructure (7h)

### Module 4 — HAL Architecture (2.5h, lecture + code walkthrough)

**Objective**: Understand the boundary between portable flight code and platform code — prerequisite for every later module and for board porting on Day 5.

- The portability problem: same flight code on STM32 (ChibiOS), Linux (Raspberry Pi/Navio), SITL, ESP32.
- `AP_HAL::HAL` (`libraries/AP_HAL/HAL.h`) is the central interface. Reach hardware via:
  ```cpp
  extern const AP_HAL::HAL& hal;
  hal.scheduler->delay(10);
  hal.console->printf("...");
  hal.rcout->write(chan, pwm);
  ```
- Key interface classes: `UARTDriver`, `I2CDevice` / `I2CDeviceManager`, `SPIDevice` / `SPIDeviceManager`, `GPIO`, `RCInput`, `RCOutput`, `Storage`, `Scheduler`, `AnalogIn`, `Flash`.
- Implementations:
  - **`AP_HAL_ChibiOS/`** — production STM32 path. ChibiOS RTOS threads, mutexes, DMA, timer-based PWM.
  - **`AP_HAL_SITL/`** — host-native, UARTs over UDP/TCP, file-backed parameter storage, simulated sensor backends.
  - **`AP_HAL_Linux/`** — Raspberry Pi/BeagleBone via `/dev/spidev`, `/dev/i2c-*`, sysfs GPIO.
  - **`AP_HAL_ESP32/`** — newer port; brief mention.
- **QuadPlane lens — `RCOutput` is over-subscribed**: a quadplane runs **4 VTOL motor PWMs and a full set of plane servos (aileron L/R, elevator, rudder, flaps) and a forward-thrust throttle simultaneously**. STM32 timer groups share clock/period across channels — bad pin allocation forces every channel on a timer group to the same PWM rate, which conflicts between OneShot125-style ESCs (high rate) and analog servos (50 Hz). This will become hands-on in Module 15 (board porting).
- Board definitions (`hwdef.dat`): MCU, pin assignments, peripherals, serial order, default features. Processed by `libraries/AP_HAL_ChibiOS/hwdef/scripts/chibios_hwdef.py` into a generated `hwdef.h`.

**Files**: `libraries/AP_HAL/HAL.h`, `libraries/AP_HAL/UARTDriver.h`, `libraries/AP_HAL_ChibiOS/HAL_ChibiOS_Class.cpp`, `libraries/AP_HAL_SITL/HAL_SITL_Class.cpp`, `libraries/AP_HAL_ChibiOS/hwdef/CubeOrange/hwdef.dat`.

**Hands-on (40 min)**: trace a barometer read from `AP_Baro_MS5611::_read()` through `I2CDevice::transfer()` to both the ChibiOS and SITL backends. Document the call chain.

### Module 5 — Core Infrastructure: Scheduler, Params, Logger, Storage (2.5h)

**Objective**: Understand the platform underneath every module on Days 3 and 4.

- **`AP_Scheduler`** (`libraries/AP_Scheduler/`): cooperative scheduler with a task table per vehicle. ArduPlane main loop runs at 50 Hz (vs Copter 400 Hz — fixed-wing dynamics are slower). Task entries are `{function, rate_hz, max_time_us}` arrays in `ArduPlane/Plane.cpp`.
- **QuadPlane scheduling**: `quadplane.update()` is called from `ArduPlane/servos.cpp:882`, **after** the fixed-wing control runs and before servo PWM is pushed. This is the single per-loop entry point for all VTOL logic. `quadplane.update_throttle_hover()` is also called from `servos.cpp:1069`. Q-mode entry hooks exist via `mode_enter()` (`quadplane.cpp:174`).
- **`AP_Param`** (`libraries/AP_Param/`): typed parameters (`AP_Int8/16/32`, `AP_Float`, `AP_Vector3f`). `AP_GROUPINFO("NAME", index, Class, member, default)` declares them. The 16-char name cap and the never-renumber-an-index rule are **hard constraints**; renumbering corrupts user configs. `var_info[]` tables describe parameter trees.
- **QuadPlane parameter footprint**: `ArduPlane/quadplane.cpp` carries two AP_GROUPINFO tables: `var_info[]` near `:7-286` and `var_info2[]` near `:296-600`. The `Q_*` family covers motors, frame, transition, assist, thrust-loss, options, position-control.
- **`AP_Logger`** (`libraries/AP_Logger/`): file-backed dataflash logging. New log messages: define a `struct PACKED` + `LogStructure` entry + format string + units. Write via `AP::logger().Write("NAME", "labels", "fmt", ...)`.
- **`StorageManager`**: EEPROM emulation. Layouts a parameter area, mission area, rally area, fence area on persistent storage.
- **`AP_Vehicle`** (base class): common subsystem init. `Plane` inherits from it.

**Hands-on (40 min)**: add a new `AP_Float` parameter `Q_DEMO_PARAM` in `ArduPlane/Parameters.h`/`.cpp`, plumb it into a new dataflash message, log its value at 5 Hz from a scheduled task, verify in MAVExplorer.

### Module 6 — Sensor Drivers & Data Flow (2h)

**Objective**: Explain the frontend/backend pattern. Set up the sensor-error material on Day 3.

- **Frontend/backend pattern**: one frontend class with the public API (e.g., `AP_Baro`, `AP_GPS`, `AP_Airspeed`, `AP_InertialSensor`, `AP_Compass`), multiple backend driver classes for each chip family. Backend probe/registration at construction; the frontend chooses healthy backends at runtime.
- **`AP_Airspeed`** (still plane-critical on a quadplane — drives `Q_ASSIST_SPEED`, TECS, EKF airspeed fusion):
  - Frontend: `libraries/AP_Airspeed/AP_Airspeed.h`. Backends: `AP_Airspeed_MS4525.cpp`, `AP_Airspeed_MS5525.cpp`, `AP_Airspeed_SDP3X.cpp`, `AP_Airspeed_DroneCAN.cpp`, `AP_Airspeed_SITL.cpp`.
  - EAS vs TAS conversion via density.
  - Health monitoring lives in `libraries/AP_Airspeed/AP_Airspeed_Health.cpp` — covered in depth on Day 3.
- **`AP_InertialSensor`**: high-rate sampling in a timer thread; ring-buffered samples consumed by EKF predict step. Multi-IMU support is the substrate for EKF lane redundancy on Day 3.
- **`AP_Compass`**: I2C/SPI mag drivers, offset calibration, motor-current compensation, world magnetic model checks.
- **`AP_Baro`**: pressure to altitude, ground-pressure calibration at boot. Primary baro selectable via `BARO_PRIMARY` (`libraries/AP_Baro/AP_Baro.cpp:964-965`).
- **`AP_GPS`**: u-blox/NMEA/SBF backends, dual-GPS blending, GPS yaw (RTK dual-antenna). Frontend health at `libraries/AP_GPS/AP_GPS.cpp:1775-1811`; blending at `:1089-1112`.
- **`AP_RangeFinder`**: status enum (Out of Range, No Data, Good Data); EKF consumes only `Good`.

**Hands-on (30 min)**: trace airspeed from `AP_Airspeed_SITL::get_pressure()` through the frontend into TECS and EKF3.

---

## Day 3 — Navigation Filtering, Sensor Errors & Failsafes (7h)

The biggest delta vs the fixed-wing baseline. Three modules instead of one.

### Module 7 — EKF3 as Code (3h, lecture + code walkthrough)

**Objective**: Make every engineer comfortable navigating `libraries/AP_NavEKF3/` and identifying where each conceptual operation (predict, fuse-this-sensor, source-select, gate-innovation, output-attitude) lives in the source. Math derivation is **out of scope** — the team already knows EKF math from their stack.

#### 7.1 Multi-core architecture

- `MAX_EKF_CORES = 3` is hard-coded at `libraries/AP_NavEKF/AP_Nav_Common.h:22`. ArduPilot can run up to 3 EKF3 cores ("lanes"), each on its own IMU.
- `NavEKF3::InitialiseFilter()` at `libraries/AP_NavEKF3/AP_NavEKF3.cpp:759-877` allocates cores from `EK3_IMU_MASK`. Each set bit triggers one `NavEKF3_core` instance (line 798 loop, line 842 `setup_core(coreImuIndex[core_index], core_index)`).
- 1:1 IMU↔core mapping. The "primary" core (selected by `EK3_PRIMARY`, default 0) is the one whose outputs feed AHRS consumers (TECS, L1, AC_PosControl in Q-modes, control law, mavlink telemetry).
- Each core is a 24-state Kalman filter. State layout in `libraries/AP_NavEKF3/AP_NavEKF3_core.h`:
  - 0–3: attitude quaternion
  - 4–6: velocity NED
  - 7–9: position NED
  - 10–12: gyro biases
  - 13–15: accel biases
  - 16–18: earth magnetic field NED
  - 19–21: body magnetic field
  - **22–23: wind velocity NE** ← the plane-critical states.

#### 7.2 Predict / fuse pipeline

- Predict step: high-rate IMU integration (forward-propagates the state and covariance).
- Update steps live in dedicated files in `libraries/AP_NavEKF3/`:
  - **GPS pos/vel**: `AP_NavEKF3_PosVelFusion.cpp`, function `FuseVelPosNED()` near line 746. Innovations vs `varInnovVelPos[]`, gated by `_gpsVelInnovGate` (param `EK3_VEL_I_GATE`) and `_gpsPosInnovGate` (`EK3_POS_I_GATE`).
  - **Baro/height**: same file, `FuseBaroHeight()`. Gated by `EK3_HGT_I_GATE`.
  - **Magnetometer**: `AP_NavEKF3_MagFusion.cpp`. Mag fusion gates each axis; if any axis test ratio > 1.0, fusion is rejected for that axis.
  - **Airspeed**: `AP_NavEKF3_AirDataFusion.cpp`, `FuseAirspeed()` near lines 20–150. **This is the function that updates the wind states** — Jacobian rows for states 22–23. Gated by `EK3_EAS_I_GATE`.
  - **Optical flow**: `AP_NavEKF3_OptFlowFusion.cpp`.
  - **Range/beacon**: `AP_NavEKF3_RngBcnFusion.cpp`.
- Each fusion path computes a normalized innovation test ratio (innovation² / (gate_size² × innovation_variance)). Test ratio < 1 ⇒ accept; ≥ 1 ⇒ reject (or attenuate, depending on the path). These ratios feed into the lane-switch scoring on Module 8.

#### 7.3 Source selection — `AP_NavEKF_Source`

- File: `libraries/AP_NavEKF/AP_NavEKF_Source.h`, `.cpp`.
- Three independent **source sets** indexed 1/2/3 (header line 136). Each set is a struct of:
  ```cpp
  struct SourceSet {
      AP_Enum<SourceXY>  posxy;   // GPS, BEACON, OPTFLOW, EXTNAV, WHEEL_ENCODER
      AP_Enum<SourceXY>  velxy;
      AP_Enum<SourceZ>   posz;    // BARO, RANGEFINDER, GPS, BEACON, EXTNAV
      AP_Enum<SourceZ>   velz;
      AP_Enum<SourceYaw> yaw;     // COMPASS, GPS, GPS_COMPASS_FALLBACK, EXTNAV, GSF
  };
  ```
- AP_GROUPINFO entries at `libraries/AP_NavEKF/AP_NavEKF_Source.cpp:32-141`: `EK3_SRC1_POSXY..YAW`, `EK3_SRC2_*`, `EK3_SRC3_*`, `EK3_SRC_OPTIONS`.
- **Runtime switching**: `AP_NavEKF_Source::setPosVelYawSourceSet(SourceSetSelection idx)` at `libraries/AP_NavEKF/AP_NavEKF_Source.cpp:152`. Vehicle code or Lua scripts call this to swap source sets in flight (e.g., switch to rangefinder for terminal landing, switch to external nav for indoor flight).
- **Legacy migration**: the deprecated `EK3_GPS_TYPE` parameter is converted to source-set assignments at boot (`AP_NavEKF3.cpp` near `:517-554`).
- For QuadPlane production: typically `EK3_SRC1_*` is GPS+BARO+COMPASS (default), and `EK3_SRC2_*`/`EK3_SRC3_*` are configured for rangefinder-on-landing or external-nav fallbacks. The team will choose a policy in Module 9.

#### 7.4 Wind state estimation (plane-critical EKF feature)

- Wind NE = states 22–23. Initialized to zero, converges via airspeed + GPS-velocity fusion.
- `FuseAirspeed()` writes wind: airspeed observation predicts ground velocity minus wind = body-x velocity in earth frame. Innovation drives wind states.
- Without an airspeed sensor, wind estimation falls back to GPS-velocity-during-turns. Slower, less accurate, **but a quadplane in VTOL has no aerodynamic frame to estimate from** — wind only converges in forward flight. This is the reason `Q_ASSIST_SPEED` and `EK3_ARSP_USE` matter together.
- Wind state is consumed by TECS (climb-rate management with headwind/tailwind), L1 (crosswind crab), and the QuadPlane controller (e.g., position-hold accuracy in QLOITER).
- Access via `AP::ahrs().wind_estimate(Vector3f &)` → backed by `NavEKF3::getWind()`.

#### 7.5 Hands-on (45 min) — Wind & innovation under stress

1. Fly a QuadPlane mission in SITL with simulated wind: `param set SIM_WIND_SPD 8`, `param set SIM_WIND_DIR 90`.
2. Plot `XKF1.VWN`, `XKF1.VWE` (wind NE estimates) — observe convergence in forward flight, freeze in VTOL.
3. Plot `XKF3.IPN`, `XKF3.IPE` (position innovations), `XKF3.IVN`, `XKF3.IVE` (velocity innovations).
4. Inject sensor noise: `SIM_BARO_RND`, `SIM_GPS_NOISE`, `SIM_ARSPD_RND`. Observe innovation gates.
5. Disable airspeed (`ARSPD_USE 0`). Watch wind convergence degrade. Discuss: why does this matter more on a quadplane than on a copter?

### Module 8 — EKF Lane Switching & Source Failover (1.5h)

**Objective**: Cover the actual mechanism by which ArduPilot survives single-sensor and single-IMU failures. The fixed-wing baseline summarizes this in a paragraph; this module walks the code.

#### 8.1 The error score

- `NavEKF3_core::errorScore()` at `libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp:62`. Returns a single float per core that drives lane selection.
- The score is the **maximum** of the candidate terms below (not a sum) — read the function carefully:
  - `0.5 * (velTestRatio + posTestRatio)` — GPS velocity & position consistency.
  - `hgtTestRatio` — altitude (baro/rng/GPS-z).
  - `0.3 * tasTestRatio` if `assume_zero_sideslip()` (forward-flight vehicles), ≥2 airspeed sensors, AND `EK3_AFFINITY` bit `EKF_AFFINITY_ARSP` set.
  - `0.3 * (magTestRatio.x + magTestRatio.y + magTestRatio.z)` if `EK3_AFFINITY` bit `EKF_AFFINITY_MAG` set.
- Computed only when `tiltAlignComplete && yawAlignComplete`; otherwise score is 0 (lane is in alignment, not eligible for primary).
- **Read this number in logs as `XKF4.SS` per core.** Higher = worse. < 0.9 considered acceptable.
- `EK3_AFFINITY` controls per-sensor specialization across cores: with two airspeed sensors and the bit set, each core becomes "the lane that trusts airspeed sensor N" — magnetic/airspeed faults can be isolated to a single lane rather than corrupting all.

#### 8.2 Routine lane selection — `UpdateFilter()`

- At `libraries/AP_NavEKF3/AP_NavEKF3.cpp:936-1005`.
- Three hysteresis layers protect against thrash:
  1. **Boot freeze**: `runCoreSelection` stays false until `imuSampleTime_us - lastUnhealthyTime_us > 1E7` (10 s after boot or after a healthy sample). Line 941.
  2. **Was-primary cooldown**: a candidate that was primary < 10 s ago cannot be re-selected (line ~978).
  3. **Margin gate**: the candidate's relative error must be below `BETTER_THRESH` *worse* than primary's, i.e., the candidate must be **substantially** better. `betterCore = altCoreError <= -BETTER_THRESH;` at line 983.
- A switch logs "EKF3 lane switch N" via `gcs_send_text` and updates yaw/position reset propagators (`updateLaneSwitchYawResetData`, `updateLaneSwitchPosResetData`) so downstream consumers (TECS, L1, AC_PosControl) see the discontinuity correctly.

#### 8.3 Emergency lane change — `checkLaneSwitch()`

- Public method at `AP_NavEKF3.cpp:1029`. Called by vehicle code (not by EKF itself) when a failsafe is imminent.
- Bypasses the 5 s switch debounce. Picks the lowest-`errorScore` core with `altErrorScore < 0.9`.
- The vehicle-side caller for ArduPlane is `Plane::ekf_check()` in `ArduPlane/ekf_check.cpp` — covered in Module 9.

#### 8.4 GSF yaw fallback

- Gaussian-Sum-Filter yaw estimator (no compass needed) lives alongside mag fusion at `libraries/AP_NavEKF3/AP_NavEKF3_MagFusion.cpp`.
- When mag fusion fails, EKF3 can request a yaw reset using GSF output: `EKFGSF_resetMainFilterYaw()` at line 177; full GSF-only yaw mode at lines 249–270.
- For fixed-wing/quadplane, GSF works in forward flight (uses GPS-velocity vs body-x velocity inferred from accel). In VTOL hover, GSF cannot converge — **this is why a quadplane mag failure is more dangerous in QHOVER than in CRUISE**.

#### 8.5 Hands-on (30 min) — Forced lane switch in SITL

1. Launch QuadPlane SITL with two IMUs: default config has IMU1 + IMU2.
2. Enable both lanes: `param set EK3_IMU_MASK 3`. Restart.
3. Take off, transition to forward flight, enter CRUISE.
4. Inject IMU1 fault: `param set SIM_IMU_FAIL 1`.
5. Watch `XKF4.SS` for both lanes; the corrupted lane's score climbs.
6. After hysteresis fires, GCS prints "EKF3 lane switch 1". Confirm `XKF*` log shows core swap and that vehicle attitude/position do not glitch (lane reset propagators did their job).
7. Repeat with `SIM_GPS_GLITCH` to see source-side disagreement; note `EK3_AFFINITY` effect.

### Module 9 — Sensor Error Detection & Failsafe Ladder (2.5h)

**Objective**: Walk the detection mechanisms for each navigation sensor and the ArduPlane action ladder that fires when EKF or RC/GCS/battery health degrades.

#### 9.1 Airspeed health (the most plane-specific check)

- `AP_Airspeed::check_sensor_failures()` at `libraries/AP_Airspeed/AP_Airspeed_Health.cpp:14`, which calls `check_sensor_ahrs_wind_max_failures(i)` per instance (`:23`).
- Two parallel detectors:
  - **EKF consistency gate**: if `ARSPD_OPTIONS` bit `USE_EKF_CONSISTENCY` is set and `ARSPD_WIND_GATE > 0` (line 63–64), compare the airspeed innovation against EKF wind+velocity prediction. Default gate is **5 σ** (`AP_Airspeed.cpp:160`).
  - **Absolute discrepancy**: if `ARSPD_WIND_MAX > 0` (`AP_Airspeed.cpp:144`), fail if `|airspeed - groundspeed| > ARSPD_WIND_MAX` (line 74).
- A `health_probability` low-pass filter (`Health.cpp:78,83`, decay coeff 0.90 on bad data, recovery 0.98 on good data) gives hysteresis.
- Auto-disable threshold `DISABLE_PROB_THRESH_CRIT = 0.1` (`Health.cpp:90`); auto-re-enable threshold `RE_ENABLE_PROB_THRESH_OK = 0.95` (`Health.cpp:91`).
- `ARSPD_OPTIONS` controls disable/re-enable behavior. GPS loss (no 3D fix) re-enables airspeed even if previously disabled (safety net).
- **TECS synthetic airspeed fallback**: parameter `TECS_SYNAIRSPEED` (`AP_TECS.cpp:244,1609`). When the pitot is rejected, TECS estimates airspeed from pitch + GPS + wind state — degraded, but enough for an emergency landing.
- For QuadPlane: airspeed loss in cruise → TECS synthetic; airspeed loss during transition → `Q_ASSIST_SPEED` may keep VTOL motors spooled if `Q_ASSIST_OPTIONS` is configured for it; airspeed loss in VTOL → no impact (VTOL doesn't use airspeed).

#### 9.2 GPS health & glitch

- `AP_GPS::is_healthy()` at `libraries/AP_GPS/AP_GPS.cpp:1775-1811` — frame rate (≤2 lost frames, ≤215 ms average) and backend health.
- Blending of dual GPSs at `AP_GPS.cpp:1089-1112`. `GPS_AUTO_SWITCH` and weights computed from reported accuracy.
- GPS glitch is detected at the **EKF level**, not the GPS frontend: position innovation runs through `EK3_POS_I_GATE`. The result feeds `errorScore` (Module 8) and ultimately `Plane::ekf_over_threshold()` (next).
- GPS yaw (dual-antenna) age limit: rejected if > 15 s old.

#### 9.3 IMU consistency

- `AP_InertialSensor` (`libraries/AP_InertialSensor/AP_InertialSensor.cpp`):
  - Per-instance error counters at `:1945-1960`.
  - Vibration & clipping at `:2217-2241`. `calc_vibration_and_clipping()` produces `VIBE.VibeX/Y/Z` (5 Hz filtered residual squared, 2 Hz output) and `VIBE.Clip0/1/2` (per-axis clip counts).
- ArduPlane pre-arm rejects unhealthy IMUs. In flight, IMU degradation manifests as elevated `errorScore` in the affected lane → lane switch.

#### 9.4 Compass / mag anomaly

- `AP_Compass::healthy()` checks update timing and field strength.
- World-mag-model check rejects compasses whose readings disagree with the World Magnetic Model at the GPS-reported location.
- `EK3_MAG_MASK` per-compass enable; `EK3_MAG_CAL` controls when the EKF re-learns mag offsets in flight.
- Failed mag → GSF yaw fallback (Module 8.4). Compass anomalies near steel runways or Q_GROUND_EFFECT_COMP areas are common; document a compass-cal SOP.

#### 9.5 Baro / rangefinder for altitude

- `BARO_PRIMARY` selects which baro is preferred (`AP_Baro.cpp:964-965`); auto-select first healthy if not set.
- `EK3_RNG_USE_HGT` enables rangefinder as a height source. Values: 0 = off, low number = use only when AGL < threshold (good for landing), high = always.
- For QuadPlane landing (`QPOS_LAND_FINAL`), rangefinder dramatically improves flare/touchdown precision.

#### 9.6 The ArduPlane action ladder — `ekf_check.cpp` and `failsafe.cpp`

This is the single most important page of code on Day 3. Walk it line-by-line:

- `ArduPlane/ekf_check.cpp`:
  - `EKF_CHECK_ITERATIONS_MAX = 10` (line 11) — 1 second at 10 Hz.
  - `Plane::ekf_check()` (the actual function, called periodically): if `ekf_over_threshold()` returns true, increment `fail_count`. Each threshold step in the ladder triggers a different action:
    - `fail_count == EKF_CHECK_ITERATIONS_MAX - 2` (8 iterations bad) → **request yaw reset**: `ahrs.request_yaw_reset();` at line 65.
    - `fail_count == EKF_CHECK_ITERATIONS_MAX - 1` (9 iterations bad) → **request lane switch**: `ahrs.check_lane_switch();` at line 70 — this is the public entry that calls `NavEKF3::checkLaneSwitch()` (Module 8.3).
    - `fail_count >= EKF_CHECK_ITERATIONS_MAX` (10 iterations bad, ~1 s sustained) → **fail**: `failsafe_ekf_event()` at line 83.
  - `ekf_over_threshold()` at line 108: variance metrics vs `g2.fs_ekf_thresh`. Mag variance, velocity variance, position variance — position is debounced (`over_thresh_count >= 1` at line 140).
  - `failsafe_ekf_event()` at line 149: switches mode based on `FS_EKF_ACTION` and the current vehicle state. **For QuadPlane** the action is QLAND in VTOL modes, RTL/glide in fixed-wing modes — read this function carefully with the team.
- `ArduPlane/failsafe.cpp` is the watchdog/lockup detector (~115 lines). Short and worth reading end-to-end.
- `ArduPlane/events.cpp`:
  - `Plane::rc_failsafe_short_on_event()` at line 21 — RC/throttle failsafe short action via `FS_SHORT_ACTN`.
  - `Plane::failsafe_long_on_event()` at line 111 — long action via `FS_LONG_ACTN` after `FS_LONG_TIMEOUT`.
- Parameter map: `FS_SHORT_ACTN` (CIRCLE/FBWA/FBWB), `FS_LONG_ACTN` (RTL/FBWA/parachute/AUTO/AUTOLAND), `FS_LONG_TIMEOUT`, `FS_EKF_THRESH`, `FS_EKF_ACTION`, `FS_GCS_ENABL`, `THR_FS_VALUE`.

#### 9.7 Hands-on (45 min) — Sensor faults end-to-end

1. **Airspeed kill in cruise**: `param set SIM_ARSPD_FAIL 1`. Predict: `health_probability` decay → auto-disable at 0.1 → TECS switches to synthetic airspeed (set `TECS_SYNAIRSPEED 1`). Verify in `ARSP` and `TECS` logs.
2. **GPS glitch in cruise**: `param set SIM_GPS_GLITCH 1`. Predict: position innovation gate trips → `errorScore` climbs on affected lane → after ~1 s, `ekf_check.cpp` requests yaw reset, then lane switch. If both lanes glitch, `failsafe_ekf_event()` fires. Confirm sequence from logs.
3. **Compass kill**: `param set COMPASS_USE 0`. Predict: GSF yaw fallback. Note degraded yaw quality in VTOL.

---

## Day 4 — QuadPlane: Architecture, Transitions & Failure Modes (7h)

The full QuadPlane day. Replaces the existing Day 4 (mission/nav, debugging, porting, Lua) — those topics fold elsewhere.

### Module 10 — QuadPlane Architecture (1.5h, lecture + walkthrough)

**Objective**: Understand the dual-controller model and its update flow before entering modes/transitions.

- **Class layout**: `ArduPlane/quadplane.h:34-770`. `class QuadPlane` is a member of `Plane` and a friend (`quadplane.h:37`), so it can read/modify Plane internals. Members include:
  - `AP_MotorsMulticopter *motors` — copter-style motor mixer.
  - `AC_AttitudeControl_Multi *attitude_control` — copter attitude controller (rate + angle).
  - `AC_PosControl *pos_control` — copter-style position controller.
  - `AC_WPNav *wp_nav` — copter waypoint nav (used in QLOITER, QRTL, auto VTOL waypoints).
  - `Transition *transition` — polymorphic transition state machine (SLT / Tailsitter / Tiltrotor implementations).
  - `Tailsitter tailsitter`, `Tiltrotor tiltrotor`, `VTOL_Assist assist` — feature submodules.
- **Update flow**:
  - The fixed-wing control runs first (mode `update()`, attitude controllers, TECS, L1).
  - Then `quadplane.update()` is called from `ArduPlane/servos.cpp:882`.
  - Then servos are pushed.
  - This means: at any instant in flight, **both control systems have produced outputs**. Whether motor PWMs and servo PWMs are sent depends on `in_vtol_mode()`, `in_assisted_flight()`, transition state, and `Q_OPTIONS` bits. Concretely, the mode logic at `quadplane.cpp:1764` (`if (!in_vtol_mode() && !in_vtol_airbrake()) {}`) and `:1801,1813` decides which outputs are committed.
- **Two attitude controllers active simultaneously**: `APM_Control` for FW pitch/roll/yaw produces servo deflections; `AC_AttitudeControl_Multi` for VTOL produces motor commands. **Blending** during transition is in `QuadPlane::update_throttle_mix()` at `quadplane.cpp:4144`. The blend is time- and speed-dependent.
- **Q_* parameter footprint**:
  - `var_info[]` near `quadplane.cpp:7-286` — Q_ENABLE, Q_M_*, Q_ASSIST_SPEED, Q_TRANSITION_MS, Q_FRAME_CLASS/TYPE, Q_OPTIONS, Q_PILOT_*, Q_LAND_*.
  - `var_info2[]` near `quadplane.cpp:296-600` — Q_TRANS_DECEL, Q_LOIT_*, Q_ASSIST_ALT, Q_ASSIST_DELAY, Q_TRANS_FAIL, Q_TRANS_FAIL_ACT, Q_BACKTRANS_MS, Q_THRST_LOSS_OPT.
- **Mode-state queries** used throughout the codebase:
  - `quadplane.in_vtol_mode()` — currently in a Q-mode (used at `Plane.cpp:250, 544, 549, 735, 860`).
  - `quadplane.in_assisted_flight()` — fixed-wing mode but VTOL motors are providing assist.
  - `quadplane.in_vtol_airbrake()` — auto-mission VTOL approach airbrake phase.
  - These determine whether servo throttle slew is applied (`servos.cpp:28`).

### Module 11 — Q-Modes & VTOL Navigation (1h)

**Objective**: Inventory the seven Q-modes and the position-controller stack used in VTOL.

- **Q-mode files** (all under `ArduPlane/`):
  - `mode_qstabilize.cpp` — pilot stick → angle target, no position hold.
  - `mode_qhover.cpp` — angle target + altitude hold, pilot climbs/descends with throttle stick.
  - `mode_qloiter.cpp` — full position hold, pilot moves stick → velocity command.
  - `mode_qland.cpp` — auto descent to ground.
  - `mode_qrtl.cpp` — return to launch then QLAND.
  - `mode_qacro.cpp` — pilot rate target.
  - `mode_qautotune.cpp` — automatic gain tuning for Q-mode PIDs.
- **Mode entry**: `Plane::set_mode()` calls `quadplane.mode_enter()` (`quadplane.cpp:174`), which initializes `pos_control` speed/accel limits.
- **Q-mode controller stack** (different from fixed-wing):
  - Lateral guidance: `AC_WPNav` (3D) instead of `AP_L1_Control` (2D).
  - Altitude/speed: `AC_PosControl` (vertical + horizontal velocity) instead of `AP_TECS`.
  - Attitude: `AC_AttitudeControl_Multi` (unified angle+rate, quaternion-based) instead of `APM_Control` (separate roll/pitch/yaw PIDs).
- **Speed parameters** (all per-mode and tunable):
  - `Q_WP_SPEED` — max horizontal velocity in auto VTOL waypoints.
  - `Q_WP_SPEED_DN` — separate descending velocity.
  - `Q_LOIT_SPEED` — pilot-commanded velocity ceiling in QLOITER.
  - `Q_PILOT_SPD_UP` / `Q_PILOT_SPD_DN` — pilot climb/descent ceilings.
- **Auto-mission VTOL items**:
  - `MAV_CMD_NAV_VTOL_TAKEOFF` → `QuadPlane::do_vtol_takeoff(cmd)` near `quadplane.cpp:3367`.
  - `MAV_CMD_NAV_VTOL_LAND` → `QuadPlane::do_vtol_land(cmd)` near `quadplane.cpp:3433`.
  - `MAV_CMD_DO_VTOL_TRANSITION` → `handle_do_vtol_transition()` near `quadplane.cpp:117`. Forces FW↔VTOL mid-mission.
  - Mission code dispatch lives near `quadplane.cpp:2097-2130`.
- **Landing position-controller state machine** (`quadplane.h:495-539`):
  ```
  QPOS_NONE → QPOS_APPROACH → QPOS_AIRBRAKE → QPOS_POSITION1
            → QPOS_POSITION2 → QPOS_LAND_DESCEND → (optional QPOS_LAND_ABORT)
            → QPOS_LAND_FINAL → QPOS_LAND_COMPLETE
  ```
  Each transition is conditional on horizontal distance, altitude, descent rate, rangefinder if available.

### Module 12 — Transition State Machine (2h, code walkthrough + hands-on)

**Objective**: Make the team fluent in the most operationally critical and error-prone subsystem on a quadplane.

#### 12.1 Polymorphic transition base

- `class Transition` at `ArduPlane/transition.h:21-72`. Abstract base. Subclasses:
  - **`SLT_Transition`** — Separate-Lift-Thrust (the typical quadplane: 4 vertical motors + 1 forward thruster + plane control surfaces). State enum at `transition.h:111-115`:
    ```cpp
    enum class State {
        AIRSPEED_WAIT = 0,
        TIMER         = 1,
        DONE          = 2,
    };
    ```
  - **`Tailsitter_Transition`** — entire airframe rotates between hover and forward flight. Different state names (`ANGLE_WAIT_FW`, `ANGLE_WAIT_VTOL`, `RATE_WAIT_FW`, `RATE_WAIT_VTOL`).
  - **Tiltrotor logic** — motor tilt servo, in `ArduPlane/tiltrotor.cpp`. Combined with SLT_Transition.

#### 12.2 SLT_Transition::update() — the forward and back transitions

- Function at `ArduPlane/quadplane.cpp:1478`. Walk it line by line in class.
- Forward transition (VTOL → fixed-wing):
  1. Pilot/auto requests forward flight. State starts at `AIRSPEED_WAIT`.
  2. Motors continue providing lift; forward throttle ramps up.
  3. Once airspeed exceeds `Q_ASSIST_SPEED` (or a derived threshold), state advances to `TIMER`.
  4. In `TIMER`, fixed-wing controllers gain authority while motors decel. Duration = `Q_TRANSITION_MS` (default 5000 ms).
  5. After `Q_TRANSITION_MS` elapses, state becomes `DONE` and motors spool down to idle.
- Back transition (fixed-wing → VTOL): triggered by entering a Q-mode or `DO_VTOL_TRANSITION`. Motors spool up first, vehicle decelerates, position controller takes over. `Q_BACKTRANS_MS` controls the back-transition timing window.
- **Failure path**: if `Q_TRANS_FAIL > 0` and the forward transition does not complete within `Q_TRANS_FAIL` seconds, `Q_TRANS_FAIL_ACT` decides the action — typically QLAND (param `:452`). `Q_OPTIONS` bit 19 (`CompleteTransition` per `quadplane.cpp:280`) inverts this: instead of QLAND, finish the transition forcibly.
- Motor blending during transition: `QuadPlane::update_throttle_mix()` at `quadplane.cpp:4144`. `allow_update_throttle_mix()` at `quadplane.cpp:4493` gates whether the blend can proceed. Motor output execution is `QuadPlane::motors_output()` at `quadplane.cpp:1964`.
- The transition called `motors_output()` directly at `quadplane.cpp:1687,1786` to push PWMs at the right scheduler tick.

#### 12.3 VTOL_Assist — when fixed-wing borrows the motors

- `class VTOL_Assist` at `ArduPlane/VTOL_Assist.h:6`. Header is the public API (~91 lines).
- Implementation at `ArduPlane/VTOL_Assist.cpp`:
  - `should_assist(float aspeed, bool have_airspeed)` at line 59 — top-level decision.
  - `Assist_Hysteresis::update()` at line 16 — debounces individual triggers.
  - `check_VTOL_recovery()` at line 149 and `output_spin_recovery()` at line 215 — recovery from upset attitude (motors assist to right the aircraft).
- Three trigger paths, each with hysteresis:
  - **Speed assist**: airspeed < `Q_ASSIST_SPEED`. If `Q_ASSIST_SPEED == 0`, this trigger is disabled.
  - **Angle assist**: attitude error > `Q_ASSIST_ANGLE` for `Q_ASSIST_DELAY` seconds (param descriptions at `:227,452`). Only active if `Q_ASSIST_SPEED > 0`.
  - **Altitude assist**: AGL < `Q_ASSIST_ALT` (param at `:404`). AGL source: rangefinder if `RNGFND_LANDING=1`, else terrain if enabled, else height-above-home.
- When `should_assist()` returns true, the motors spool up (`motors->set_desired_spool_state(THROTTLE_UNLIMITED)`) while the vehicle stays in the fixed-wing mode. `quadplane.in_assisted_flight()` becomes true.

#### 12.4 Hands-on (45 min) — Transition behavior under stress

1. Reduce `Q_TRANSITION_MS` to 500 ms. Take off, request forward flight. Observe truncated transition; vehicle may stall — this is the SOP for tuning `Q_TRANSITION_MS` (start short, lengthen until stable).
2. Set `Q_TRANS_FAIL 5`, restore `Q_TRANSITION_MS 5000`. Throttle the forward thruster to never reach `Q_ASSIST_SPEED`: `param set SIM_ESC_TELEM 1; param set Q_ASSIST_SPEED 18` and observe transition timeout → `Q_TRANS_FAIL_ACT`.
3. Toggle `Q_OPTIONS` bit 19 and re-run; vehicle now completes the transition at the timeout instead of QLAND.
4. Trigger angle assist: in CRUISE, push pitch with RC override beyond `Q_ASSIST_ANGLE`. Observe `QTUN.AssistFlags` go non-zero and motors spool up.

### Module 13 — Frame Types, Motor Mixing & Servo Allocation (1h)

**Objective**: Understand how QuadPlane allocates 8–16 PWM channels across motors + control surfaces and what tradeoffs the engineer makes when picking a frame.

- `Q_FRAME_CLASS` — Quad (1), Hexa (2), Octa (3), OctaQuad, Y6, Tri (7), DodecaHexa (12), Heli single/dual (10), Scripting Matrix (15), Dynamic Scripting Matrix (17), and Tailsitter via specific configs.
- `Q_FRAME_TYPE` — Plus, X, V, H, V-tail, A-tail; per-class motor layout.
- `Q_TILT_*` family for tiltrotor configurations.
- `TAILSIT_*` for tailsitters.
- **Servo function enum** (`libraries/SRV_Channel/SRV_Channel.h:82-171`):
  - `k_motor1..k_motor8` (33–40), `k_motor9..k_motor32` (82–115).
  - `k_motor_tilt = 41` — tiltrotor tilt actuator.
  - `k_tiltMotorLeft = 75`, `k_tiltMotorRight = 76` — vectored thrust.
  - `k_throttle = 70` — forward thruster on a quadplane.
  - `k_aileron`, `k_elevator`, `k_rudder`, `k_flap`, `k_flap_auto` — fixed-wing control surfaces.
- **Default channel mapping** for QuadPlane (`quadplane.cpp` near `:712-715`): CH_5 → k_motor1, CH_6 → k_motor2, CH_8 → k_motor4, CH_11 → k_motor7. Engineers will overwrite these on a custom board; covered in Module 15.
- **Timer-group allocation tradeoff**: 4 motor PWMs at OneShot125 + 4 servo PWMs at 50 Hz cannot share a single STM32 timer. The hwdef `PWMx` directives must place them on separate timer groups. This is the single biggest "you'll get this wrong on first hwdef" failure mode.

### Module 14 — QuadPlane Failure Handling (1.5h)

**Objective**: Cover thrust loss, transition failure, EKF-failsafe-in-VTOL, and the `Q_OPTIONS` bits that change failure semantics.

#### 14.1 Thrust loss detection

- `QuadPlane::thrust_loss_check(bool reset)` at `quadplane.cpp:4911`. Called from `motors_output()` at `quadplane.cpp:2032`.
- Skips check while `motors->get_thrust_boost()` is active (motors already compensating).
- Detection: angle error vs commanded attitude exceeds threshold for ~1 s → calls `motors->set_thrust_loss_detected()` so the motor mixer redistributes. `Q_THRST_LOSS_OPT` controls bit options:
  - bit 0: disable detection entirely.
  - bit 1: only detect in VTOL modes (not transitions/FW).

#### 14.2 Transition failure

- Covered in Module 12.2. `Q_TRANS_FAIL` + `Q_TRANS_FAIL_ACT` + `Q_OPTIONS` bit 19. Reiterate here that for **production**, set `Q_TRANS_FAIL` to a generous but finite value (e.g., 2× nominal `Q_TRANSITION_MS / 1000`) and verify the failure action matches your safety case.

#### 14.3 EKF failsafe in VTOL

- `Plane::failsafe_ekf_event()` (`ArduPlane/ekf_check.cpp:149`) selects an action based on `FS_EKF_ACTION` and current mode.
- **In QHOVER/QLOITER**: typically transitions to QLAND (motor-driven descent — safest with degraded EKF).
- **In QRTL**: falls back to QLAND.
- **In auto VTOL waypoint**: aborts navigation and lands.
- **Mid-transition**: if EKF fails *during* transition, the vehicle is in the worst possible state — neither pure-VTOL nor pure-FW. `Q_TRANS_FAIL_ACT` interaction with `FS_EKF_ACTION` deserves an explicit decision in your safety case.

#### 14.4 GPS loss in QuadPlane

- VTOL position hold (QLOITER, QRTL) requires absolute position health — GPS loss → drop to QHOVER (attitude-only) or QLAND.
- Forward flight tolerates short GPS dropouts via dead-reckoning from airspeed + heading.
- `Q_OPTIONS` controls some specific GPS-loss behaviors; read the parameter description at `quadplane.cpp:280` end-to-end with the team.

#### 14.5 Logging & diagnosis

- **`QTUN`** (writers near `quadplane.cpp:3761-3771`): throttle in, angle boost, transition state, assist flags, desired vs actual climb rate.
- **`QPOS`** (writers near `quadplane.cpp:3812-3817`): position-controller state, target altitude, target velocity.
- **`XKF*`**: lane scores, innovations, wind, source set in use.
- **`MSG`**: GCS text incl. "EKF3 lane switch N", "Q_TRANS_FAIL: timeout", etc.
- For every QuadPlane bug investigation: open `QTUN`, `QPOS`, `XKF4`, `ARSP`, `CTUN`, `MSG` together and time-align.

#### 14.6 Hands-on (30 min)

- Force a thrust-loss scenario with `SIM_ENGINE_FAIL` on motor 1; observe `QTUN` and motor mixer redistribution.
- Force EKF failure during transition and discuss: what's the right `FS_EKF_ACTION` for our airframe?

---

## Day 5 — Custom Hardware, Capstone & Q&A (8h)

### Module 15 — QuadPlane Board Porting (2.5h, hands-on)

**Objective**: Walk a complete hwdef for a custom quadplane flight controller, paying attention to the dual-IMU + 4-VTOL-motor + plane-servo allocation that distinguishes a QP board from a pure-copter or pure-plane board.

- `hwdef.dat` → `hwdef.h` pipeline. Script: `libraries/AP_HAL_ChibiOS/hwdef/scripts/chibios_hwdef.py`. Output lands in `build/<board>/libraries/AP_HAL_ChibiOS/hwdef/`.
- Reference boards:
  - `libraries/AP_HAL_ChibiOS/hwdef/CubeOrange/hwdef.dat` — STM32H7, full-featured, dual-IMU.
  - `libraries/AP_HAL_ChibiOS/hwdef/Pixhawk6X/hwdef.dat` — modern reference.
- Bootloader hwdef (`hwdef-bl.dat`) covered as discussion only.

**Hands-on (90 min) — Define a CustomQP board**

Spec:
- STM32H743 MCU.
- **Dual IMU**: ICM-42688 on SPI1 (primary), ICM-20689 on SPI2 (redundant). Engineers from Day 3 know why this matters: it makes EKF lane redundancy real on this board.
- MS5611 baro on SPI3.
- IST8310 compass on I2C1.
- MS4525DO airspeed on I2C2.
- u-blox GPS on UART2.
- Telemetry on UART1.
- USB for config/log download.
- **8 PWM outputs**, allocated as:
  - PWM 1–4: VTOL motors 1–4 (OneShot125-capable timer group).
  - PWM 5–6: aileron L, aileron R (50 Hz timer group).
  - PWM 7: elevator (same group as 5–6 or a third group).
  - PWM 8: rudder.
  - (Throttle, flap, etc. via aux outputs if available.)
- Battery V/I sensing on ADC1.

Steps:
1. Copy `CubeOrange/` to `CustomQP/` and edit.
2. Set `MCU STM32H7xx STM32H743xx`, flash/RAM sizes.
3. Configure SPI bus order, declare both IMUs in the `IMU` directives.
4. Configure I2C buses; declare MS4525DO airspeed.
5. Allocate PWM channels to **two timer groups**: motors on a high-rate group, servos on 50 Hz. Walk why this matters using Module 13 background.
6. Build: `./waf configure --board CustomQP && ./waf plane`.
7. Discuss: what bring-up looks like on real hardware (USB-connected boot, parameter download, IMU detection log line, motor direction check via "Motor Test" SOP, servo travel verification).

### Module 16 — Debugging & Test Infrastructure (1h)

**Objective**: Cover the debugging primitives compressed from the original course.

- **GDB on SITL**: `./waf configure --board sitl --debug && ./waf plane`. Launch under GDB: `sim_vehicle.py -v ArduPlane -f quadplane --gdb`. Useful breakpoints: `QuadPlane::motors_output`, `Plane::ekf_check`, `NavEKF3::checkLaneSwitch`, `AP_Airspeed::check_sensor_failures`.
- **GCS messages**: `GCS_SEND_TEXT(MAV_SEVERITY_INFO, "fmt", args...)`.
- **Logger**: `AP::logger().Write("NAME", "labels", "fmt", args...)`. Writes appear in dataflash log.
- **`hal.console->printf()`**: SITL only; use sparingly.
- **Autotest framework**: `Tools/autotest/arduplane.py` carries the QuadPlane test cases. Run with `Tools/autotest/autotest.py build.ArduPlane test.ArduPlane.QuadPlane`. Pattern: `wait_ready_to_arm()`, `change_mode("QHOVER")`, `arm_vehicle()`, `wait_altitude(...)`, `wait_groundspeed(...)`, `do_RTL()`.
- **gtest**: `libraries/<lib>/tests/test_*.cpp` with `TEST_F`/`EXPECT_*`. Build via `./waf --targets tests/<name>`. Run via `./build/sitl/tests/<name>`. Suitable for filter math, frame transforms, parsing — NOT for control loops (no time integration).

### Module 17 — Capstone: QuadPlane Fault-Injection Lab (3h)

**Objective**: Synthesize Days 2–4 in a single guided exercise. Each engineer produces a short report mapping observed log fingerprints to file:line of the detection/recovery mechanism.

#### 17.1 Setup (30 min)

1. Build QuadPlane SITL with debug symbols.
2. Configure dual IMU and dual GPS:
   - `param set EK3_IMU_MASK 3` (use both IMUs → 2 EKF lanes).
   - `param set GPS_TYPE2 1` (enable second simulated GPS).
   - `param set EK3_AFFINITY 7` (mag/airspeed/yaw affinity across lanes).
   - `param set FS_EKF_ACTION 2` (QLAND on EKF failure in VTOL — confirm with team).
   - `param set TECS_SYNAIRSPEED 1` (enable synthetic airspeed fallback).
3. Upload a mission: `MAV_CMD_NAV_VTOL_TAKEOFF` at home → 3 forward-flight waypoints (altitude 80 m, leg ~1 km) → `MAV_CMD_DO_VTOL_TRANSITION` (VTOL) → `MAV_CMD_NAV_VTOL_LAND` 100 m east of home.

#### 17.2 Fault-injection script (90 min)

Each fault is injected via `param set` at a specific waypoint; the engineer predicts the response, runs the mission, then verifies from logs:

| WP / phase | Fault | Predicted response | Verification (file:line for mechanism) |
|---|---|---|---|
| Mid-forward-transition | `SIM_ARSPD_FAIL 1` | `health_probability` decays past 0.1 (`AP_Airspeed_Health.cpp:90`) → ARSPD auto-disables → TECS switches to synthetic airspeed (`AP_TECS.cpp:244,1609`) → `Q_ASSIST_SPEED` may briefly hold motors. Vehicle continues forward flight. | `ARSP.Health` plot, `MSG` log, `XKF4` lane scores stable. |
| Cruise after WP1 | `SIM_GPS_GLITCH 1` on GPS1 | Position innovation gate trips (`AP_NavEKF3_PosVelFusion.cpp:746+`) → `errorScore()` (`AP_NavEKF3_Outputs.cpp:62`) climbs on lane 1 → after hysteresis (`AP_NavEKF3.cpp:936-1005`), routine lane-switch fires; if both lanes glitch, `Plane::ekf_check()` (`ArduPlane/ekf_check.cpp:57`) ladder fires (yaw reset at `:65`, `check_lane_switch` at `:70`, `failsafe_ekf_event` at `:83`). | `XKF4.SS` (per-lane scores), `MSG` "EKF3 lane switch N". |
| Cruise after WP2 | `SIM_IMU_FAIL 1` on IMU1 | Lane 1 `errorScore` climbs (gyro/accel divergence). After 10 s + 10 s hysteresis, primary changes to lane 2. Vehicle attitude stable through switch (lane reset propagators applied). | `XKF4.SS`, `XKF4.PI` (primary index), `MSG`. |
| Compass kill mid-cruise | `param set COMPASS_USE 0` | EKF mag fusion degrades → GSF yaw fallback engages (`AP_NavEKF3_MagFusion.cpp:177,249-270`). Yaw remains good in forward flight. | `XKF1.YAW`, `XKF*` GSF status. |
| During back-transition | Force `Q_TRANSITION_MS 30000` so back-transition does not finish in time, with `Q_TRANS_FAIL 3`, `Q_TRANS_FAIL_ACT QLAND` | Timeout fires → vehicle drops to QLAND (`quadplane.cpp:1478` state machine + parameter at `:452`). | `QTUN.TState`, `MSG` "Q_TRANS_FAIL". |
| Final descent | `SIM_ENGINE_FAIL 1` (motor 1) | `QuadPlane::thrust_loss_check()` (`quadplane.cpp:4911`) detects sustained angle error → `motors->set_thrust_loss_detected()` redistributes; vehicle yaws but lands. | `QTUN.AngBst`, motor PWM redistribution in `RCOU`. |

#### 17.3 Reporting (60 min)

Each engineer produces a 2-page log analysis: for each fault, paste the relevant `XKF*`/`QTUN`/`ARSP`/`MSG` snippet and link to the file:line of the detection/recovery code.

### Module 18 — Open Q&A & Advanced Topics Menu (1.5h)

Short on-demand topics, instructor-led based on team interest:

- **AC_Fence** for QuadPlane (different breach actions in VTOL vs FW).
- **DroneCAN** sensors (CAN GPS, CAN airspeed, CAN ESC). `libraries/AP_DroneCAN/`.
- **AP_DDS / ROS 2 bridge**. `libraries/AP_DDS/`.
- **Lua scripting** for one-off custom behaviors (e.g., custom assist heuristic without rebuild). `libraries/AP_Scripting/`.
- **Tailsitter / Tiltrotor** if your team's airframe is one of these. `ArduPlane/tailsitter.cpp`, `ArduPlane/tiltrotor.cpp`.
- **Pegasus / Isaac Sim** photorealistic simulation, if hardware is available.
- **Contributing upstream**: PR conventions, CI, autotest gating.

Wrap-up:
- Recommended reading: ArduPilot dev docs (https://ardupilot.org/dev/), Plane wiki (https://ardupilot.org/plane/), QuadPlane wiki sections.
- Course feedback collection.

---

## Appendices

### A. Pre-Course Setup

Each workstation needs:
- Linux (Ubuntu 22.04+ recommended) or macOS.
- ArduPilot source cloned with `--recurse-submodules`.
- Build deps installed via `Tools/environment_install/install-prereqs-ubuntu.sh`.
- ARM toolchain (auto-fetched by Waf for hardware boards).
- Python 3 with `pymavlink` and `MAVProxy`.
- VS Code or equivalent with C++/Python extensions; GDB.
- Mission Planner or QGroundControl for log review.
- For Module 15, no real hardware needed; for Module 18 Pegasus topic, an NVIDIA RTX GPU and Isaac Sim install.

### B. Critical Files Cited (master list)

```
ArduPlane/Plane.h
ArduPlane/Plane.cpp
ArduPlane/quadplane.h           (~770 lines, class declaration)
ArduPlane/quadplane.cpp         (~5000 lines, the VTOL implementation)
ArduPlane/transition.h          (transition base + SLT_Transition state enum)
ArduPlane/tailsitter.cpp
ArduPlane/tiltrotor.cpp
ArduPlane/VTOL_Assist.h, VTOL_Assist.cpp
ArduPlane/mode_qstabilize.cpp
ArduPlane/mode_qhover.cpp
ArduPlane/mode_qloiter.cpp
ArduPlane/mode_qland.cpp
ArduPlane/mode_qrtl.cpp
ArduPlane/mode_qacro.cpp
ArduPlane/mode_qautotune.cpp
ArduPlane/ekf_check.cpp         (variance ladder + failsafe_ekf_event)
ArduPlane/failsafe.cpp          (watchdog/lockup)
ArduPlane/events.cpp            (rc_failsafe_short_on_event, failsafe_long_on_event)
ArduPlane/servos.cpp:882        (quadplane.update() call site)

libraries/AP_NavEKF/AP_Nav_Common.h:22                 (MAX_EKF_CORES = 3)
libraries/AP_NavEKF/AP_NavEKF_Source.h                 (SourceSet struct)
libraries/AP_NavEKF/AP_NavEKF_Source.cpp:32-141        (EK3_SRC* AP_GROUPINFO)
libraries/AP_NavEKF/AP_NavEKF_Source.cpp:152           (setPosVelYawSourceSet)
libraries/AP_NavEKF3/AP_NavEKF3.cpp:759                (InitialiseFilter)
libraries/AP_NavEKF3/AP_NavEKF3.cpp:936-1005           (routine lane selection + BETTER_THRESH)
libraries/AP_NavEKF3/AP_NavEKF3.cpp:1029               (checkLaneSwitch — emergency)
libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp:62         (errorScore)
libraries/AP_NavEKF3/AP_NavEKF3_PosVelFusion.cpp       (FuseVelPosNED)
libraries/AP_NavEKF3/AP_NavEKF3_AirDataFusion.cpp      (FuseAirspeed — wind state update)
libraries/AP_NavEKF3/AP_NavEKF3_MagFusion.cpp:177,249  (GSF yaw fallback)

libraries/AP_Airspeed/AP_Airspeed_Health.cpp:14,23,78,83,90,91   (check + thresholds)
libraries/AP_Airspeed/AP_Airspeed.cpp:144,160          (ARSPD_WIND_MAX, ARSPD_WIND_GATE)
libraries/AP_GPS/AP_GPS.cpp:1775-1811,1089-1112        (health, blending)
libraries/AP_InertialSensor/AP_InertialSensor.cpp:1945-1960,2217-2241  (health, vibration)
libraries/AP_Baro/AP_Baro.cpp:964-965                  (BARO_PRIMARY)
libraries/AP_TECS/AP_TECS.cpp:244,1609                 (synthetic airspeed)
libraries/SRV_Channel/SRV_Channel.h:82-171             (k_motor*/k_throttle/k_tiltMotor* enum)

libraries/AP_HAL_ChibiOS/hwdef/CubeOrange/hwdef.dat
libraries/AP_HAL_ChibiOS/hwdef/Pixhawk6X/hwdef.dat
libraries/AP_HAL_ChibiOS/hwdef/scripts/chibios_hwdef.py
```

### C. Key Parameter Map (cheat-sheet)

| Subsystem | Key parameters |
|---|---|
| EKF3 cores | `EK3_IMU_MASK`, `EK3_PRIMARY`, `EK3_AFFINITY`, `EK3_OPTIONS` |
| EKF3 innovation gates | `EK3_POS_I_GATE`, `EK3_VEL_I_GATE`, `EK3_HGT_I_GATE`, `EK3_MAG_I_GATE`, `EK3_EAS_I_GATE` |
| EKF3 sources | `EK3_SRC1_POSXY/VELXY/POSZ/VELZ/YAW`, `EK3_SRC2_*`, `EK3_SRC3_*`, `EK3_SRC_OPTIONS` |
| EKF3 mag/range/airspeed | `EK3_MAG_CAL`, `EK3_MAG_MASK`, `EK3_RNG_USE_HGT`, `EK3_ARSP_USE` |
| Airspeed health | `ARSPD_USE`, `ARSPD_OPTIONS`, `ARSPD_WIND_MAX`, `ARSPD_WIND_GATE`, `ARSPD_WIND_WARN` |
| TECS fallback | `TECS_SYNAIRSPEED` |
| Plane failsafe | `FS_SHORT_ACTN`, `FS_LONG_ACTN`, `FS_LONG_TIMEOUT`, `FS_GCS_ENABL`, `FS_EKF_THRESH`, `FS_EKF_ACTION`, `THR_FS_VALUE` |
| QuadPlane base | `Q_ENABLE`, `Q_FRAME_CLASS`, `Q_FRAME_TYPE`, `Q_OPTIONS` |
| QuadPlane transition | `Q_TRANSITION_MS`, `Q_TRANS_DECEL`, `Q_TRANS_FAIL`, `Q_TRANS_FAIL_ACT`, `Q_BACKTRANS_MS` |
| QuadPlane assist | `Q_ASSIST_SPEED`, `Q_ASSIST_ANGLE`, `Q_ASSIST_ALT`, `Q_ASSIST_DELAY` |
| QuadPlane navigation | `Q_WP_SPEED`, `Q_WP_SPEED_DN`, `Q_LOIT_SPEED`, `Q_PILOT_SPD_UP`, `Q_PILOT_SPD_DN` |
| QuadPlane failure | `Q_THRST_LOSS_OPT`, `Q_M_PWM_*` |

### D. Comparison: This Course vs the Fixed-Wing Baseline

| Aspect | `custom_gnc_course_plane.md` (baseline) | This QuadPlane edition |
|---|---|---|
| Target platform | ArduPlane fixed-wing | QuadPlane (VTOL) |
| Operations content | Day 1, ~6h | Compressed to ~2h survival kit + pre-read |
| EKF coverage | 1 module, 2.5h, concept-level | 2 modules, 4.5h, code-level (`errorScore`, `checkLaneSwitch`, source sets, GSF) |
| Sensor error handling | Bullet-point mention | Dedicated 2.5h module with `ekf_check.cpp` walk + airspeed health + failsafe ladder |
| QuadPlane | 45-min stub in optional menu | Full Day 4 (~7h): architecture, modes, transition state machine, VTOL_Assist, thrust loss, Q-failsafe |
| Capstone | Three-option menu, fixed-wing | Single guided fault-injection lab on QuadPlane |
| Board porting | Generic plane hwdef | Quadplane hwdef with dual-IMU + 4 motors + plane servos + airspeed |
| Total length | 5 days / ~34h | 5 days / ~34h |
