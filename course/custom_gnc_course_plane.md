# ArduPilot for GNC & Embedded Software Engineers — Fixed-Wing Edition

## Custom Training Course — Detailed Curriculum

**Duration**: ~34 hours (5 days)
**Audience**: GNC and embedded software engineers with C/C++ proficiency, flight code development experience on proprietary stacks, and varying seniority (junior to 10+ year veterans). No prior ArduPilot experience assumed.

**Goal**: Equip the team to understand ArduPilot's internals — architecture, code structure, build tools, debugging — through the lens of **ArduPlane** (fixed-wing aircraft), so they can maintain ArduPilot-based platforms, port to custom hardware, and study ArduPilot's algorithms for potential adaptation.

**Vehicle Focus**: This course uses **ArduPlane** throughout. All examples, exercises, and code walkthroughs reference the fixed-wing vehicle type, its control libraries (`APM_Control`, `AP_TECS`, `AP_L1_Control`), and plane-specific subsystems (airspeed management, servo output, landing, soaring). A companion course exists for ArduCopter (`custom_gnc_course.md`).

---

## Day 1: ArduPilot Foundations & Operations Fast-Track (6h)

Operations content is compressed to a single day. The team needs enough operational fluency to use SITL and GCS tools for the code-focused days that follow, but not the full operator training.

---

### Module 1: ArduPilot Overview & Ecosystem (1.5h) — Lecture + Demo

**Objective**: Understand ArduPilot's scope, community, and tooling landscape before diving into the code.

#### Topics

1. **Project History & Community**
   - Origins (APM → Pixhawk ecosystem), major milestones
   - Governance, release process (stable/beta/dev), contribution model
   - Community resources: discuss.ardupilot.org, Discord, wiki, developer documentation

2. **Vehicle Types & Hardware**
   - Supported vehicle types: ArduCopter, ArduPlane, Rover, ArduSub, AntennaTracker, Blimp
   - Supported hardware families: STM32-based (Pixhawk, CubeBlack, CubeOrange, etc.), Linux boards, ESP32
   - Relationship between vehicle code and hardware abstraction
   - **ArduPlane focus**: conventional fixed-wing, flying wing, V-tail, elevon mixing, QuadPlane (VTOL hybrid)

3. **Software Ecosystem & Ground Control**
   - Mission Planner (Windows, full-featured GCS)
   - QGroundControl (cross-platform)
   - MAVProxy (command-line, scriptable — primary tool for this course)
   - Companion computer software: DroneKit, pymavlink, MAVSDK

4. **MAVLink Protocol Overview**
   - What MAVLink is: binary telemetry/command protocol
   - Message structure: system ID, component ID, message ID, payload
   - Common messages: HEARTBEAT, ATTITUDE, GLOBAL_POSITION_INT, COMMAND_LONG
   - How GCS talks to the autopilot (request/response, streaming, command acknowledgment)
   - Protocol versions (v1 vs v2), message signing

5. **Repository Structure Walkthrough**
   - Top-level directories: vehicle dirs, `libraries/`, `modules/`, `Tools/`
   - Vehicle directories: `ArduCopter/`, `ArduPlane/`, `Rover/`, `ArduSub/`
   - Library organization: 153+ libraries in `libraries/`
   - Submodules: `modules/mavlink`, `modules/ChibiOS`, `modules/gtest`
   - Build system: `waf`, `wscript` files
   - Tools: `Tools/autotest/`, `Tools/scripts/`, `Tools/Frame_params/`

#### Key Files to Show
- `ArduPlane/Plane.h` — main vehicle class header (compare briefly with `ArduCopter/Copter.h` to highlight structural similarity)
- `ArduPlane/Plane.cpp` — main vehicle file, scheduler task table
- `libraries/` directory listing — library naming conventions (note `APM_Control/` for plane, `AC_*` for copter)
- `modules/` — submodule structure
- `Tools/autotest/sim_vehicle.py` — SITL launcher

---

### Module 2: Operations Essentials (2.5h) — Compressed Course 1

**Objective**: Get hands-on with SITL and basic operations so the team can independently test code changes from Day 2 onwards.

#### Topics

1. **SITL Setup & Usage**
   - What SITL is: full ArduPilot code running on the host PC with simulated physics
   - Launching: `Tools/autotest/sim_vehicle.py -v ArduPlane`
   - SITL command-line options: `-L` (location), `--map`, `--console`, `-S` (speedup)
   - MAVProxy commands: `mode`, `arm throttle`, `takeoff`, `wp`, `param`
   - Connecting external GCS (Mission Planner, QGC) to SITL
   - Plane SITL specifics: simulated airspeed, wind (`SIM_WIND_SPD`, `SIM_WIND_DIR`), runway takeoff

2. **Flight Modes Overview**
   - Mode categories: manual, stabilized, autonomous
   - Key modes for ArduPlane:
     - **MANUAL**: direct pass-through of RC inputs to control surfaces, no stabilization
     - **FBWA** (Fly-By-Wire A): stabilized mode, pilot controls bank angle and pitch, autopilot holds attitude limits
     - **FBWB** (Fly-By-Wire B): stabilized mode, pilot controls airspeed and climb rate
     - **CRUISE**: combines heading hold with altitude hold, suitable for long-range flight
     - **AUTO**: mission execution (waypoints, commands)
     - **GUIDED**: programmatic waypoint commands from GCS
     - **LOITER**: circle at a fixed point and altitude
     - **RTL**: return to launch, loiter at home, optionally autoland
     - **TAKEOFF**: automatic runway or hand-launch takeoff to altitude
     - **CIRCLE**: orbit current position
     - **TRAINING**: like MANUAL but with attitude limits enforced
   - Mode prerequisites (what sensors/state each mode requires)
   - How mode switching works at the user level (RC switch, GCS command)
   - Key difference from copter: plane modes prioritize airspeed management; stalling is the primary safety concern (vs. copter's free-fall)

3. **Parameter System (User Perspective)**
   - What parameters are: runtime-configurable values stored in persistent storage
   - Parameter naming convention (e.g., `RLL_RATE_P`, `PTCH_RATE_P`, `AIRSPEED_MAX`)
   - Setting parameters: `param set`, `param show`, `param download`
   - Loading/saving parameter files
   - Plane-specific parameter groups:
     - `ARSPD_*`: airspeed sensor configuration
     - `TECS_*`: Total Energy Control System (altitude/airspeed management)
     - `NAVL1_*`: L1 navigation controller
     - `RLL_RATE_*`, `PTCH_RATE_*`, `YAW_RATE_*`: attitude controller gains
     - `SERVO*_*`: servo channel configuration and mixing
     - `TKOFF_*`: takeoff parameters
     - `LAND_*`: landing approach and flare parameters
   - Parameter trees and groups (preview of the `AP_Param` internals in Day 2)

4. **Mission Planning & Automatic Navigation**
   - Mission items: waypoints, commands (NAV_TAKEOFF, NAV_LAND, DO_CHANGE_SPEED, etc.)
   - Plane-specific mission commands:
     - `NAV_TAKEOFF`: climb to altitude on a heading
     - `NAV_LAND`: approach with glide slope and flare
     - `NAV_LOITER_TURNS`: orbit a point N times
     - `NAV_LOITER_TO_ALT`: loiter while changing altitude
     - `DO_LAND_START`: marks the beginning of a landing sequence
   - Creating missions in MAVProxy and Mission Planner
   - Uploading, downloading, and running missions
   - Rally points and geofence basics

5. **Log Analysis Basics**
   - Log types: dataflash logs (onboard) vs telemetry logs
   - Downloading logs from SITL (`logs/` directory)
   - Viewing logs with MAVExplorer: `mavlogdump.py`, `MAVExplorer.py`
   - Key log messages for plane:
     - `ATT`: attitude (roll, pitch, yaw)
     - `CTUN`: control tuning — **nav_roll, nav_pitch, airspeed, throttle** (different fields from copter's CTUN)
     - `NTUN`: navigation tuning — L1 controller data, lateral acceleration, target bearing
     - `ARSP`: airspeed sensor data (raw, corrected, EAS, TAS)
     - `TECS`: TECS states — total energy error, energy balance, speed/height demands
     - `GPS`, `BAT`, `ERR`: shared with other vehicles
   - Mission Planner log review (brief demo)

6. **Failsafe Configuration**
   - Throttle failsafe (RC loss), GCS failsafe, battery failsafe, geofence failsafe
   - Short vs long failsafe actions: continue mission, RTL, glide-land
   - Airspeed sensor failsafe: what happens when the airspeed sensor fails
   - How failsafes interact with flight modes
   - Configuration parameters: `THR_FAILSAFE`, `FS_SHORT_ACTN`, `FS_LONG_ACTN`

#### Hands-on Exercise (45 min)
- Launch SITL ArduPlane: `sim_vehicle.py -v ArduPlane`
- Connect MAVProxy console and map
- Arm and takeoff using TAKEOFF mode (automatic runway takeoff)
- Switch to FBWA and fly manually (observe attitude limits)
- Switch to CRUISE for heading/altitude hold
- Create and fly an Auto mission with 4+ waypoints including NAV_LAND
- Trigger an RTL
- Download and review the flight log in MAVExplorer
- Identify attitude, airspeed, TECS, and navigation data in logs

---

### Module 3: MAVLink & Application Interface (2h) — Compressed Course 2

**Objective**: Understand how external software communicates with ArduPilot, enabling the team to write test scripts and diagnostic tools.

#### Topics

1. **MAVLink Message Structure (Detail)**
   - Packet format: STX, length, sequence, sysid, compid, msgid, payload, checksum
   - Message definitions: XML files in `modules/mavlink/message_definitions/`
   - Common vs. dialect-specific messages
   - MAVLink microservices: parameter protocol, mission protocol, command protocol

2. **pymavlink & MAVProxy**
   - `pymavlink`: Python library for MAVLink communication
   - Connection strings: `udp:127.0.0.1:14550`, `tcp:`, `serial:`
   - `mavutil.mavlink_connection()` — establishing a connection
   - Receiving messages: `recv_match()`, message types, blocking vs. non-blocking
   - Sending messages: `mav.command_long_send()`, `mav.set_mode()`

3. **Reading Vehicle State**
   - Heartbeat: vehicle type, autopilot type, system status, armed state
   - Attitude: roll, pitch, yaw (ATTITUDE message)
   - Position: lat, lon, alt (GLOBAL_POSITION_INT)
   - **Airspeed**: VFR_HUD message (airspeed, groundspeed, heading, throttle, climb rate)
   - Battery: voltage, current, remaining (SYS_STATUS, BATTERY_STATUS)
   - RC channels, servo outputs
   - Wind estimation: WIND message (direction, speed, vertical component)

4. **Sending Commands**
   - Arm/disarm: COMMAND_LONG with MAV_CMD_COMPONENT_ARM_DISARM
   - Mode changes: SET_MODE message
   - Guided mode waypoints: SET_POSITION_TARGET_GLOBAL_INT
   - **Plane takeoff**: MAV_CMD_NAV_TAKEOFF (specifies pitch angle and altitude, not vertical like copter)
   - **Plane-specific**: no hover capability; commands must account for continuous forward flight
   - Command acknowledgment and error handling

5. **Mission Protocol**
   - Mission count → request → item exchange
   - Uploading a mission programmatically
   - Starting/pausing/resuming missions
   - Plane-specific: including landing sequence in missions

#### Hands-on Exercise (40 min)
Write a Python script (using pymavlink) that:
1. Connects to SITL over UDP
2. Waits for heartbeat
3. Sets mode to TAKEOFF (for automatic takeoff)
4. Arms the vehicle
5. Waits for the plane to reach target altitude
6. Sets mode to GUIDED
7. Commands a waypoint 500m north at current altitude
8. Reads and prints attitude, airspeed, and position at 1 Hz for 10 seconds
9. Waits for arrival (within loiter radius) and commands RTL
10. Monitors descent and landing

**Starter template provided** — students fill in the MAVLink calls.

**Key differences from copter script**: no vertical takeoff command, must use TAKEOFF mode or FBWA with throttle; waypoints are at greater distances (plane can't hover); arrival is defined by loiter radius not position tolerance; landing is a glide approach not vertical descent.

---

## Day 2: Software Architecture Deep-Dive (7h)

The core of the course. This day covers the infrastructure that makes ArduPilot tick: build system, HAL, scheduler, parameters, and logging. Understanding these systems is prerequisite for all subsequent modules.

---

### Module 4: Build System & Development Environment (2h) — Lecture + Hands-on

**Objective**: Master the Waf build system and understand code organization conventions for independent development.

#### Topics

1. **Waf Build System**
   - What Waf is: Python-based build system (similar role to CMake/Make)
   - Two-phase workflow: `configure` then `build`
   - `./waf configure --board <board>`: sets target platform, stored in `build/`
   - `./waf <vehicle>`: builds a vehicle (e.g., `./waf plane`)
   - `./waf --targets <target>`: builds a specific binary or test
   - `./waf list_boards`: available board definitions
   - `./waf list`: all available build targets

2. **Building for Different Targets**
   - SITL build: `./waf configure --board sitl` — native compilation, runs on host
   - Debug build: `--debug` flag — enables debug symbols, disables optimization
   - Hardware build: `./waf configure --board CubeBlack` — cross-compilation with ARM toolchain
   - Build output location: `build/<board>/bin/`
   - Compiler toolchain: where it comes from, how it's selected

3. **Build Options & Feature Flags**
   - `Tools/scripts/build_options.py`: master list of optional features
   - How features are enabled/disabled at compile time
   - `AP_FEATURE_ENABLED` pattern in code
   - Board-specific feature defaults (minimal boards vs. full-featured boards)
   - Impact on binary size and resource usage

4. **Code Structure Conventions**
   - `wscript` files: per-directory build configuration
   - Vehicle directory layout: main class, modes, parameters, config
   - Library directory layout: header, source, backends, examples, tests
   - Naming conventions: `AP_` prefix for general libraries, `AC_` for copter-specific, `AR_` for rover-specific
   - **ArduPlane libraries**: `APM_Control` (attitude controllers), `AP_TECS` (speed/height), `AP_L1_Control` (lateral nav), `AP_Landing` (approach/flare), `AP_Airspeed` (airspeed sensing)
   - Include paths and dependencies between libraries

5. **Development Workflow**
   - Edit → build → run SITL → test cycle
   - Incremental builds (Waf tracks dependencies)
   - `./waf clean` vs `./waf distclean`
   - Common build errors and how to fix them

#### Hands-on Exercise (40 min)
1. Configure and build ArduPlane for SITL (normal and debug)
2. Build ArduPlane for a hardware board (CubeBlack or similar)
3. Build a single test: `./waf --targets tests/test_math`
4. Run the test binary
5. Explore `wscript` files in `ArduPlane/` and a library directory
6. Examine build output directory structure
7. Try enabling/disabling a build feature and observe the impact

---

### Module 5: HAL Architecture (2.5h) — Lecture + Code Walkthrough

**Objective**: Understand the hardware abstraction layer that allows ArduPilot to run on multiple platforms — critical for anyone planning to port to custom hardware.

#### Topics

1. **Why HAL Exists**
   - The portability problem: same flight code on STM32 (ChibiOS), Linux, SITL, ESP32
   - HAL as the boundary between platform-independent and platform-specific code
   - Design philosophy: vehicle and library code never touch hardware directly

2. **AP_HAL Interface (`libraries/AP_HAL/`)**
   - `AP_HAL::HAL` class: the central interface, holds references to all subsystems
   - Key interface classes:
     - `UARTDriver` — serial communication (GPS, telemetry, companion computers)
     - `I2CDevice` / `I2CDeviceManager` — I2C bus access (barometer, compass, airspeed sensor, etc.)
     - `SPIDevice` / `SPIDeviceManager` — SPI bus access (IMU, flash storage)
     - `GPIO` — general-purpose I/O pins
     - `RCInput` — RC receiver input
     - `RCOutput` — servo PWM output (ailerons, elevator, rudder, throttle, flaps)
     - `Storage` — persistent parameter storage (EEPROM emulation)
     - `Scheduler` — thread management, timers, delays
     - `AnalogIn` — ADC channels (battery voltage, current sensing, analog airspeed)
     - `Flash` — on-chip flash access
   - How the HAL singleton is accessed: `AP::hal()` / `hal` global

3. **HAL Implementations**
   - `AP_HAL_ChibiOS/` — the primary hardware HAL (STM32 family)
     - ChibiOS RTOS integration: threads, mutexes, semaphores
     - DMA usage for SPI/UART
     - Timer-based PWM output
   - `AP_HAL_SITL/` — simulation HAL
     - How SITL simulates sensors (JSON or built-in physics models)
     - SITL UARTs: mapped to UDP/TCP sockets
     - SITL storage: file-based parameter storage
   - `AP_HAL_Linux/` — Linux-based boards (Raspberry Pi, BeagleBone, etc.)
     - Linux device access: `/dev/spidev`, `/dev/i2c-*`, sysfs GPIO
   - `AP_HAL_ESP32/` — ESP32 port (brief mention)

4. **HAL Call Flow**
   - Example: reading an I2C barometer
     - `AP_Baro_MS5611::_read()` → `_dev->transfer()` → `I2CDevice::transfer()`
     - ChibiOS: → `I2CDriver::transfer()` → ChibiOS `i2cMasterTransmit/Receive`
     - SITL: → returns simulated pressure data
   - Example: servo output to control surfaces
     - `SRV_Channels::push()` → `hal.rcout->write()` → platform-specific PWM
     - Contrast with copter: plane outputs go to servos (ailerons, elevator, rudder, flaps), not motor ESCs

5. **Board Definitions (`hwdef` files)**
   - Location: `libraries/AP_HAL_ChibiOS/hwdef/`
   - What a hwdef defines: MCU, pin assignments, peripheral buses, UART mapping, default features
   - `hwdef.dat` format and key directives
   - How `hwdef.dat` is processed into `hwdef.h` during build
   - Examining a real board definition (e.g., CubeBlack, Pixhawk6X)

#### Key Files to Examine
```
libraries/AP_HAL/AP_HAL.h                    — main HAL header
libraries/AP_HAL/HAL.h                       — HAL class definition
libraries/AP_HAL/UARTDriver.h                — UART interface
libraries/AP_HAL/I2CDevice.h                 — I2C interface
libraries/AP_HAL/SPIDevice.h                 — SPI interface
libraries/AP_HAL_ChibiOS/HAL_ChibiOS_Class.cpp  — ChibiOS HAL instantiation
libraries/AP_HAL_SITL/HAL_SITL_Class.cpp     — SITL HAL instantiation
libraries/AP_HAL_ChibiOS/hwdef/CubeBlack/hwdef.dat  — example hwdef
```

#### Hands-on Exercise (40 min)
**Trace a sensor read from vehicle code through HAL to SITL backend:**
1. Start in `ArduPlane/Plane.cpp` — find where barometer is read
2. Follow the call into `AP_Baro` library
3. Trace through the backend driver to the HAL I2C/SPI call
4. Find the corresponding SITL implementation
5. Compare with the ChibiOS implementation
6. Document the call chain (whiteboard or notes)

---

### Module 6: Core Infrastructure Libraries (2.5h) — Lecture + Code Walkthrough

**Objective**: Understand the foundational libraries that all vehicle code depends on: scheduling, parameters, logging, and storage.

#### Topics

1. **AP_Scheduler: Task Scheduling**
   - Problem: deterministic real-time loop on a cooperative system
   - Main loop structure: `Plane::fast_loop()` runs at 50 Hz (note: lower than copter's 400 Hz — fixed-wing dynamics are slower)
   - Task table: array of `{function, rate_hz, max_time_us}` entries
   - How the scheduler decides which tasks to run each loop iteration
   - Task priorities and time-slicing
   - Key file: `ArduPlane/Plane.cpp` — `scheduler_tasks[]` array
   - Plane-specific scheduled tasks:
     - `update_speed_height()` at 50 Hz — TECS speed/height controller
     - `navigate()` at 10 Hz — L1 navigation update
     - `update_alt()` at 10 Hz — altitude state update
     - `calc_airspeed_errors()` — airspeed error computation
     - `update_flight_mode()` at 50 Hz — current mode update
   - How to add a new scheduled task

2. **AP_Param: Parameter System (Internals)**
   - Parameter types: `AP_Int8`, `AP_Int16`, `AP_Int32`, `AP_Float`
   - Parameter declaration with `AP_GROUPINFO` macro
   - Parameter groups and group IDs — how the flat storage maps to nested objects
   - Storage layout in EEPROM (or file on SITL)
   - `var_info` table: metadata for each parameter (name, type, default, range)
   - How parameters are loaded at boot: `AP_Param::setup()`, `load_all()`
   - How parameters are set via MAVLink: `GCS_MAVLINK::handle_param_set()`
   - Adding a new parameter: declaration, `var_info` entry, group ID allocation

3. **AP_Logger: Data Logging**
   - Purpose: onboard recording for post-flight analysis and debugging
   - Log backends: file (SD card / filesystem), MAVLink (streaming to GCS)
   - Log message definition: `LogStructure` entries, format strings
   - How to define a new log message: struct, format, labels, units
   - Writing log data: `AP::logger().Write()`, `WriteBlock()`
   - Log message types and categories
   - Pre-defined messages for plane: `ATT`, `CTUN`, `NTUN`, `TECS`, `ARSP`, `GPS`, `BAT`, `ERR`

4. **StorageManager**
   - EEPROM emulation: how parameters and other persistent data are stored
   - Storage layout: parameter area, mission area, rally area, fence area
   - How `StorageManager` allocates and manages storage regions
   - Backend implementations: file (SITL/Linux), flash (ChibiOS)

5. **AP_Vehicle: Base Vehicle Class**
   - What `AP_Vehicle` provides: common subsystem initialization, scheduler setup
   - How vehicle classes (`Copter`, `Plane`, `Rover`) inherit from `AP_Vehicle`
   - Common functionality: failsafe framework, serial port setup, vehicle-independent libraries

#### Key Files to Examine
```
ArduPlane/Plane.cpp                          — scheduler task table
ArduPlane/Parameters.h                       — parameter declarations
ArduPlane/Parameters.cpp                     — parameter var_info tables
libraries/AP_Param/AP_Param.h                — parameter type definitions
libraries/AP_Param/AP_Param.cpp              — parameter storage/retrieval
libraries/AP_Scheduler/AP_Scheduler.h        — scheduler interface
libraries/AP_Scheduler/AP_Scheduler.cpp      — scheduler implementation
libraries/AP_Logger/AP_Logger.h              — logger interface
libraries/AP_Logger/LogStructure.h           — log message definitions
libraries/AP_Vehicle/AP_Vehicle.h            — base vehicle class
```

#### Hands-on Exercise (40 min)
**Add a new parameter and log message to ArduPlane:**
1. Declare a new `AP_Float` parameter in `ArduPlane/Parameters.h`
2. Add the `var_info` entry in `ArduPlane/Parameters.cpp`
3. Set the parameter via MAVProxy: `param set MY_PARAM 42.0`
4. Define a new log message struct and format
5. Write the parameter value to the log periodically (in a scheduled task)
6. Build, run SITL, and verify:
   - Parameter appears in `param show`
   - Log message appears in the dataflash log
   - View the logged data in MAVExplorer

---

## Day 3: Sensors, Navigation & Control Pipeline (7h)

This day traces the full data flow from sensor hardware through state estimation to control surface output — the core of any flight controller. **Fixed-wing aircraft have fundamentally different control architectures from multirotors**, and this is where the courses diverge most significantly.

---

### Module 7: Sensor Drivers & Data Flow (2h) — Lecture + Code Walkthrough

**Objective**: Understand how ArduPilot's sensor driver architecture works, from hardware interface to data consumption, with special attention to airspeed sensing — the most critical plane-specific sensor.

#### Topics

1. **Sensor Driver Architecture: Frontend/Backend Pattern**
   - The pattern: one frontend class (public API), multiple backend drivers
   - Example: `AP_Baro` (frontend) → `AP_Baro_MS5611`, `AP_Baro_BMP280`, `AP_Baro_SITL` (backends)
   - Why: same API regardless of which physical sensor is connected
   - Backend registration: `_add_backend()`, probe/detect mechanisms
   - Driver selection: hwdef specifies which backends to probe

2. **AP_Airspeed: Airspeed Sensing (Plane-Critical Sensor)**
   - **Why airspeed matters for fixed-wing**: stall speed floor, structural speed ceiling, control authority depends on dynamic pressure
   - Frontend API: `get_airspeed()`, `get_airspeed_ratio()`, `healthy()`, `use()`
   - Equivalent airspeed (EAS) vs. true airspeed (TAS): `EAS2TAS` conversion using air density
   - Backend drivers:
     - `AP_Airspeed_MS4525` — common differential pressure sensor (I2C)
     - `AP_Airspeed_MS5525` — higher precision variant
     - `AP_Airspeed_SDP3X` — Sensirion differential pressure
     - `AP_Airspeed_analog` — analog pitot tube
     - `AP_Airspeed_SITL` — simulated airspeed
   - Calibration: `ARSPD_RATIO` (pitot tube constant), auto-calibration using GPS groundspeed
   - Offset calibration: zero-pressure offset at boot, `ARSPD_OFFSET`
   - Airspeed sensor health monitoring and failure handling
   - Multi-airspeed support: primary and secondary sensors
   - Key parameters: `ARSPD_TYPE`, `ARSPD_USE`, `ARSPD_RATIO`, `ARSPD_PIN`, `ARSPD_AUTOCAL`

3. **AP_InertialSensor: IMU**
   - What it provides: accelerometer and gyroscope data
   - Frontend API: `get_accel()`, `get_gyro()`, `get_delta_angle()`, `get_delta_velocity()`
   - Backend drivers: `AP_InertialSensor_Invensense` (MPU6000/ICM series), `AP_InertialSensor_BMI160`, etc.
   - Sampling: high-rate sampling in timer thread, accumulated in ring buffer
   - Filtering: low-pass filter, notch filter (less critical for plane than copter — no propeller vibration through the airframe)
   - Calibration: gyro calibration at boot, accel calibration procedure
   - Multi-IMU support: multiple IMUs for redundancy, EKF lane assignment

4. **AP_Compass: Magnetometer**
   - Purpose: heading reference for EKF
   - Backend pattern: I2C/SPI compass drivers
   - Calibration: offset and motor compensation
   - Multi-compass support and priority

5. **AP_Baro: Barometer**
   - Purpose: altitude estimation (complementary to GPS)
   - Ground pressure calibration at boot
   - Altitude calculation from pressure
   - Important for plane: altitude data feeds into TECS for speed/height control

6. **AP_GPS: GNSS Receiver**
   - Backend pattern: UART-based drivers (u-blox, NMEA, etc.)
   - GPS state machine: no fix → 2D → 3D → RTK
   - Dual-GPS support and switching
   - GPS blending
   - Plane-specific: GPS groundspeed used for wind estimation and airspeed calibration

7. **AP_RangeFinder**
   - Rangefinder for terrain following and landing flare
   - Plane use: `RNGFND_LANDING` — rangefinder assists precision landing by triggering flare at a measured height AGL
   - How rangefinder data feeds into the landing state machine

8. **Data Flow Summary**
   ```
   Hardware → HAL (I2C/SPI/UART) → Backend Driver → Frontend API → Consumers (EKF, TECS, control, logging)
   ```
   - Plane-specific consumers: TECS uses airspeed + baro altitude, L1 uses GPS position/velocity

#### Key Files to Examine
```
libraries/AP_Airspeed/AP_Airspeed.h          — airspeed frontend
libraries/AP_Airspeed/AP_Airspeed.cpp        — airspeed backend registration
libraries/AP_Airspeed/AP_Airspeed_MS4525.cpp — example hardware backend
libraries/AP_Airspeed/AP_Airspeed_SITL.cpp   — SITL backend
libraries/AP_Baro/AP_Baro.h                  — barometer frontend
libraries/AP_Baro/AP_Baro.cpp                — backend registration
libraries/AP_InertialSensor/AP_InertialSensor.h  — IMU frontend
libraries/AP_GPS/AP_GPS.h                    — GPS frontend
```

#### Hands-on Exercise (30 min)
**Trace airspeed data flow in SITL:**
1. Set breakpoints (or add print statements) in the airspeed backend
2. Follow data from SITL physics model → airspeed backend → frontend → TECS
3. Examine airspeed data in logs: `ARSP` message (raw pressure, corrected airspeed, EAS2TAS ratio)
4. Experiment with `ARSPD_RATIO` parameter — observe the effect on airspeed reading vs. GPS groundspeed
5. Simulate airspeed sensor failure (`SIM_ARSPD_FAIL`) and observe autopilot response
6. Compare SITL wind estimation (WIND message) accuracy with and without airspeed sensor

---

### Module 8: AHRS & EKF (2.5h) — Lecture + Code Walkthrough

**Objective**: Understand how ArduPilot fuses sensor data into attitude and position estimates — the core of navigation. Special attention to wind estimation, which is critical for fixed-wing flight.

#### Topics

1. **AP_AHRS: Attitude & Heading Reference System**
   - What AHRS provides: attitude (roll, pitch, yaw), position, velocity estimates
   - AHRS as an interface: multiple backend estimators
   - API: `get_rotation_body_to_ned()`, `get_position()`, `get_velocity_NED()`
   - How vehicle code uses AHRS (consumers don't care which EKF is running)
   - **Plane-specific AHRS consumers**: TECS, L1 navigation, attitude controllers, landing system

2. **AP_NavEKF3: Extended Kalman Filter**
   - Purpose: optimal sensor fusion for state estimation
   - Inputs: IMU (predict step), GPS, baro, compass, rangefinder, airspeed, external nav (update steps)
   - States estimated: position (NED), velocity (NED), attitude (quaternion), gyro biases, accel biases, **wind velocity (NE)**, earth magnetic field, body magnetic field
   - The predict-update cycle:
     - Predict: integrate IMU data forward (high rate, ~400 Hz)
     - Update: correct with GPS (~5-10 Hz), baro (~10 Hz), compass (~10 Hz), **airspeed (~10 Hz)**
   - Covariance matrix and innovation checking
   - Why EKF3 over EKF2 (flexible, multi-source)

3. **Wind Estimation (Plane-Critical EKF Feature)**
   - **Why wind matters**: fixed-wing aircraft fly relative to the air, not the ground; wind directly affects groundtrack, ground speed, and fuel/energy consumption
   - Wind states in EKF3: north and east wind velocity components
   - How wind is estimated: difference between GPS groundspeed and airspeed-derived airspeed vector
   - Airspeed fusion: `EK3_SRC1_VELZ` for airspeed, `AP_NavEKF3_VelPosFusion.cpp`
   - Wind estimation without airspeed sensor: less accurate, relies on GPS speed variations during turns
   - Wind estimation accuracy and convergence
   - How plane control code uses wind: TECS adjusts throttle for headwind/tailwind, L1 adjusts course correction

4. **EKF Lanes & Failover**
   - Multiple EKF instances (lanes), each running on a different IMU
   - Lane scoring: based on innovation consistency, sensor health
   - Automatic failover: if one lane diverges, switch to a healthy lane
   - `EK3_IMU_MASK`: which IMUs are assigned to which lanes

5. **EKF Outputs → Flight Mode Availability**
   - EKF health flags: attitude OK, velocity OK, position OK (horizontal/vertical)
   - How mode prerequisites map to EKF state for plane:
     - **MANUAL / TRAINING**: needs nothing from EKF (direct RC pass-through)
     - **FBWA / FBWB**: needs attitude estimate (roll/pitch stabilization)
     - **CRUISE**: needs attitude + heading (compass/GPS-derived)
     - **LOITER**: needs attitude + horizontal position (GPS)
     - **AUTO / GUIDED**: needs attitude + 3D position + home set
     - **RTL**: needs attitude + 3D position + home set
   - Pre-arm checks related to EKF

6. **Key EKF Parameters & Tuning**
   - `EK3_SRC1_POSXY`, `EK3_SRC1_VELXY`, `EK3_SRC1_POSZ`: source selection
   - Innovation gate parameters: how tightly the EKF trusts each sensor
   - `EK3_GPS_TYPE`: GPS usage mode
   - Process noise parameters
   - `EK3_ARSP_USE`: whether to use airspeed in EKF (highly recommended for plane)

#### Key Files to Examine
```
libraries/AP_AHRS/AP_AHRS.h                 — AHRS interface
libraries/AP_AHRS/AP_AHRS.cpp               — AHRS implementation
libraries/AP_NavEKF3/AP_NavEKF3.h            — EKF3 main class
libraries/AP_NavEKF3/AP_NavEKF3.cpp          — EKF3 initialization, lane management
libraries/AP_NavEKF3/AP_NavEKF3_core.h       — single EKF instance (core)
libraries/AP_NavEKF3/AP_NavEKF3_PosVelFusion.cpp — GPS/position/airspeed fusion
libraries/AP_NavEKF3/AP_NavEKF3_MagFusion.cpp    — compass fusion
```

#### Hands-on Exercise (40 min)
**Examine EKF behavior under stress — with focus on wind estimation:**
1. Fly a normal mission in SITL, download and examine EKF logs
2. Review EKF log messages: `XKF1` (states), `XKF4` (innovations), `NKF5` (covariance)
3. Use MAVExplorer to plot EKF innovations and wind estimate
4. Enable simulated wind: `param set SIM_WIND_SPD 10` and `SIM_WIND_DIR 90`
5. Observe wind estimation convergence in logs (plot estimated wind vs. simulated)
6. Inject sensor noise using SITL parameters:
   - `SIM_BARO_RND`: barometer noise
   - `SIM_GPS_NOISE`: GPS noise
   - `SIM_ARSPD_RND`: airspeed noise
7. Disable airspeed sensor (`ARSPD_USE 0`) and observe degraded wind estimation
8. Intentionally kill GPS in SITL and watch EKF degrade to dead reckoning
9. Discuss: what would happen in each flight mode? How does plane handle GPS loss differently from copter?

---

### Module 9: Flight Modes & Control Pipeline (2.5h) — Lecture + Code Walkthrough

**Objective**: Understand the complete control pipeline from pilot input to servo output — the most code-relevant module for GNC engineers. **This module is completely different from the copter course** because fixed-wing aircraft use fundamentally different control architectures.

#### Topics

1. **Fixed-Wing Aerodynamics Review**
   - Lift, drag, and angle of attack — how wings generate lift
   - Control surfaces: ailerons (roll), elevator (pitch), rudder (yaw), flaps (lift augmentation)
   - How differential deflection of control surfaces produces moments
   - Airspeed as the primary control variable: control authority scales with dynamic pressure (q = ½ρv²)
   - Stall: what happens when angle of attack exceeds the critical angle (loss of lift)
   - **Key difference from copter**: a plane must maintain forward airspeed to fly; thrust is for speed, not direct altitude control

2. **Mode Class Hierarchy**
   - Base class: `Mode` (in `ArduPlane/mode.h`)
   - One subclass per mode: `ModeManual`, `ModeFBWA`, `ModeFBWB`, `ModeCruise`, `ModeAuto`, `ModeGuided`, `ModeRTL`, `ModeLoiter`, `ModeCircle`, `ModeTakeoff`, `ModeTraining`, `ModeQStabilize` (QuadPlane modes), etc.
   - Virtual methods: `update()` (called every loop), `initialised()`, `does_auto_throttle()`, `is_vtol_mode()`
   - Mode number mapping: `set_mode()`

3. **Mode Switching**
   - Sources: RC switch channel, GCS command (SET_MODE), failsafe triggers, internal logic
   - `Plane::set_mode()`: validation, init, logging
   - Mode prerequisites checking (EKF health, GPS availability)
   - Exit cleanup

4. **ArduPlane Control Pipeline (The Big Picture)**
   ```
   Pilot Input (RC/GCS)
       ↓
   Mode::update()              — interprets input, sets nav_roll_cd / nav_pitch_cd / target altitude
       ↓
   AP_RollController           — nav_roll_cd → aileron servo command
   AP_PitchController          — nav_pitch_cd → elevator servo command (with roll feedforward)
   AP_YawController            — yaw damping → rudder servo command
       ↓
   AP_TECS                     — target altitude + target airspeed → throttle demand + pitch demand
       ↓
   SRV_Channels                — servo PWM output (ailerons, elevator, rudder, throttle, flaps)
   ```

   **Contrast with copter pipeline**:
   | Stage | Copter | Plane |
   |-------|--------|-------|
   | Attitude control | `AC_AttitudeControl` (unified roll/pitch/yaw) | `AP_RollController` + `AP_PitchController` + `AP_YawController` (separate) |
   | Altitude/speed | `AC_PosControl` (vertical position) | `AP_TECS` (simultaneous altitude + airspeed via energy balance) |
   | Navigation | `AC_WPNav` (3D position tracking) | `AP_L1_Control` (lateral path following via roll commands) |
   | Output | `AP_Motors` (motor mixing matrix) | `SRV_Channels` (direct servo assignments) |
   | Primary constraint | Battery + motor saturation | Airspeed envelope (stall to Vne) |

5. **APM_Control: Attitude Controllers (`libraries/APM_Control/`)**
   - **AP_RollController**
     - Input: desired roll angle (nav_roll_cd, in centidegrees)
     - Output: aileron servo command
     - PID structure: P on angle error, D on roll rate, I for trim, FF for rate demand
     - Airspeed scaling: gains are scaled by `1/airspeed` so response is consistent across the speed envelope
     - Key parameters: `RLL_RATE_P`, `RLL_RATE_I`, `RLL_RATE_D`, `RLL_RATE_FF`, `RLL2SRV_TCONST`
   - **AP_PitchController**
     - Input: desired pitch angle (nav_pitch_cd)
     - Output: elevator servo command
     - Roll compensation (feedforward): elevator demand increases with bank angle to maintain altitude in turns (load factor = 1/cos(bank))
     - Airspeed scaling: same as roll controller
     - Key parameters: `PTCH_RATE_P`, `PTCH_RATE_I`, `PTCH_RATE_D`, `PTCH_RATE_FF`, `PTCH2SRV_TCONST`
   - **AP_YawController**
     - Purpose: yaw damping (not active yaw control — planes yaw via coordinated turns)
     - Input: yaw rate, sideslip estimate
     - Output: rudder servo command
     - Coordinated turn: rudder deflection proportional to roll rate to minimize sideslip
     - Key parameters: `YAW_RATE_P`, `YAW_RATE_I`, `YAW_RATE_D`

6. **AP_TECS: Total Energy Control System (`libraries/AP_TECS/`)**
   - **The core concept**: manage altitude and airspeed simultaneously through energy balance
   - Total energy = kinetic energy (½mv²) + potential energy (mgh)
   - Throttle controls total energy (adds or removes energy from the system)
   - Pitch controls energy distribution (trades altitude for speed and vice versa)
   - TECS control law:
     - Total energy error → throttle command
     - Energy balance error → pitch command
   - Speed/height priority: `TECS_SPDWEIGHT` — balance between maintaining airspeed vs. altitude
     - 0.0 = pure altitude priority (risky: may stall)
     - 2.0 = pure speed priority (risky: may diverge in altitude)
     - 1.0 = balanced (default)
   - Key parameters:
     - `TECS_CLMB_MAX`: maximum climb rate
     - `TECS_SINK_MIN`: minimum sink rate
     - `TECS_SINK_MAX`: maximum sink rate
     - `TECS_TIME_CONST`: system time constant
     - `TECS_THR_DAMP`: throttle damping
     - `TECS_INTEG_GAIN`: integrator gain
     - `TRIM_THROTTLE`: cruise throttle estimate
     - `TRIM_ARSPD_CM`: target cruise airspeed (cm/s)
   - TECS state machine: normal flight, underspeed protection (prevents stall by pitching down), climbout (takeoff priority)

7. **AP_L1_Control: L1 Navigation (`libraries/AP_L1_Control/`)**
   - Purpose: lateral path following for waypoint navigation
   - The L1 guidance law: determines the required bank angle to follow a path
   - L1 reference point: a point on the desired path at L1 distance ahead of the aircraft
   - Lateral acceleration command → converted to bank angle (via a = v²/r → φ = atan(a/g))
   - L1 period parameter: `NAVL1_PERIOD` — larger = smoother but less precise tracking
   - Damping: `NAVL1_DAMPING`
   - L1 handles: waypoint tracking, loiter circles, cross-track error correction
   - **Contrast with copter**: copter's `AC_WPNav` commands 3D velocity/position; plane's L1 commands lateral bank angle only (vertical handled by TECS separately)

8. **SRV_Channels: Servo Output (`libraries/SRV_Channel/`)**
   - Channel assignment: each servo channel is assigned a function (aileron, elevator, rudder, throttle, flap, etc.)
   - `SRV_Channels::set_output_scaled()`: set output by function, not channel number
   - Servo reversing, min/max/trim configuration
   - Mixing: elevon (combined aileron + elevator on flying wing), V-tail, differential spoilers
   - Throttle handling: different from motor mixing — single throttle channel (or differential for twin-engine)
   - Key parameters: `SERVO1_FUNCTION`, `SERVO1_MIN`, `SERVO1_MAX`, `SERVO1_TRIM`, `SERVO1_REVERSED`

9. **Tracing a Complete Control Loop: FBWA Mode**
   - Pilot moves roll stick → `ModeFBWA::update()` maps stick to desired bank angle (limited by `ROLL_LIMIT_DEG`)
   - Pilot moves pitch stick → mapped to desired pitch angle (limited by `PTCH_LIM_MAX_DEG` / `PTCH_LIM_MIN_DEG`)
   - Pilot throttle → mapped to target airspeed range between `ARSPD_FBW_MIN` and `ARSPD_FBW_MAX`
   - `AP_RollController::get_servo_out()` → PID on roll error → aileron servo value
   - `AP_PitchController::get_servo_out()` → PID on pitch error with roll compensation → elevator servo value
   - `AP_TECS::update_pitch_throttle()` → simultaneous altitude/airspeed → throttle + pitch demand
   - `SRV_Channels::push()` → PWM to servos

#### Key Files to Examine
```
ArduPlane/mode.h                             — Mode base class
ArduPlane/mode_fbwa.cpp                      — FBWA mode implementation
ArduPlane/mode_auto.cpp                      — Auto mode (mission execution)
ArduPlane/mode_rtl.cpp                       — RTL mode
ArduPlane/Plane.cpp                          — main loop, servo output calls
ArduPlane/servos.cpp                         — servo mixing and output logic
libraries/APM_Control/AP_RollController.h    — roll controller interface
libraries/APM_Control/AP_RollController.cpp  — roll controller implementation
libraries/APM_Control/AP_PitchController.cpp — pitch controller implementation
libraries/APM_Control/AP_YawController.cpp   — yaw controller (damper)
libraries/AP_TECS/AP_TECS.h                  — TECS interface
libraries/AP_TECS/AP_TECS.cpp                — TECS implementation
libraries/AP_L1_Control/AP_L1_Control.h      — L1 navigation interface
libraries/AP_L1_Control/AP_L1_Control.cpp    — L1 navigation implementation
libraries/SRV_Channel/SRV_Channel.h          — servo channel management
```

#### Hands-on Exercise (40 min)
**Modify FBWA mode behavior and test in SITL:**
1. Open `ArduPlane/mode_fbwa.cpp`
2. Understand the `ModeFBWA::update()` function
3. Add airspeed-dependent bank angle limiting: reduce maximum bank angle when airspeed is below a threshold (e.g., below 1.3× stall speed, limit bank to 15° instead of `ROLL_LIMIT_DEG`)
   - Read current airspeed from `AP::ahrs()`
   - Compare against `aparm.airspeed_min * 1.3`
   - Clamp `nav_roll_cd` accordingly
4. Build, launch SITL
5. Fly in FBWA mode, verify bank angle is limited at low airspeed
6. Check logs: `CTUN` for nav_roll, `ARSP` for airspeed
7. Discussion: why is this safety-relevant? (Stall speed increases with bank angle due to load factor)

---

## Day 4: Advanced Topics & Board Porting (7h)

---

### Module 10: Mission & Navigation System (1.5h) — Lecture + Code Walkthrough

**Objective**: Understand how ArduPilot stores, manages, and executes autonomous missions, with focus on plane-specific navigation and landing.

#### Topics

1. **AP_Mission: Mission Management**
   - Mission storage: commands stored in persistent storage (`StorageManager`)
   - Command types: navigation commands (NAV), do commands (DO), condition commands
   - Mission state machine: `update()` loop, command execution, advancing to next
   - Key plane commands:
     - `MAV_CMD_NAV_WAYPOINT` — fly to waypoint (L1 path following)
     - `MAV_CMD_NAV_TAKEOFF` — climb to altitude on heading
     - `MAV_CMD_NAV_LAND` — approach with glide slope, flare, touchdown
     - `MAV_CMD_NAV_LOITER_TURNS` — orbit N times
     - `MAV_CMD_NAV_LOITER_TO_ALT` — loiter while climbing/descending
     - `MAV_CMD_DO_LAND_START` — marks beginning of landing sequence
     - `MAV_CMD_DO_CHANGE_SPEED` — adjust target airspeed
   - How mission is uploaded (MAVLink mission protocol) and started (mode switch to Auto)

2. **Navigation: L1 Path Following in Auto Mode**
   - `ModeAuto::update()` → `navigate()` → `AP_L1_Control::update_waypoint()`
   - Waypoint-to-waypoint tracking: L1 computes lateral acceleration to follow the line between waypoints
   - Turn anticipation: L1 begins turning before reaching a waypoint to follow a smooth path
   - Loiter navigation: `AP_L1_Control::update_loiter()` — circle around a point
   - **Contrast with copter**: copter's `AC_WPNav` does 3D spline/straight-line tracking with velocity control; plane's L1 does 2D lateral guidance with separate TECS for vertical

3. **AP_Landing: Approach & Landing (`libraries/AP_Landing/`)**
   - Landing is the most complex plane operation (copter just descends vertically)
   - Landing state machine phases:
     - **Approach**: fly toward landing point, descend on glide slope
     - **Pre-flare**: optional, begin reducing throttle
     - **Flare**: pitch up to reduce descent rate, throttle to idle
     - **Touchdown**: on ground, disable throttle, hold heading
   - Key parameters:
     - `LAND_FLARE_ALT`: altitude to begin flare (m)
     - `LAND_FLARE_SEC`: time-based flare trigger (seconds before touchdown)
     - `LAND_PITCH_DEG`: pitch angle during flare
     - `LAND_TYPE`: normal or deepstall
   - Rangefinder integration: more accurate flare trigger using AGL measurement
   - `AP_Landing_Deepstall`: steep descent landing without engine — aircraft intentionally stalls at controlled point for precision landing in confined areas

4. **AP_Rally & Geofence**
   - Rally points: alternative landing points for RTL
   - How RTL selects its target (home vs. nearest rally point)
   - `AC_Fence`: geofence definitions (circle, polygon, altitude ceiling/floor)
   - Fence breach actions for plane: report, RTL, guided mode to waypoint

#### Key Files to Examine
```
libraries/AP_Mission/AP_Mission.h            — mission class
libraries/AP_Mission/AP_Mission.cpp          — mission state machine
libraries/AP_L1_Control/AP_L1_Control.h      — L1 navigation
libraries/AP_L1_Control/AP_L1_Control.cpp    — L1 navigation impl
libraries/AP_Landing/AP_Landing.h            — landing state machine
libraries/AP_Landing/AP_Landing.cpp          — landing implementation
libraries/AP_Landing/AP_Landing_Deepstall.cpp — deepstall landing
ArduPlane/mode_auto.cpp                      — Auto mode using mission + L1
ArduPlane/mode_rtl.cpp                       — RTL mode
libraries/AC_Fence/AC_Fence.h                — geofencing
```

#### Hands-on Exercise (20 min)
**Trace a mission execution with landing:**
1. Upload a mission to SITL: takeoff → 3 waypoints → DO_LAND_START → approach waypoint → NAV_LAND
2. Switch to Auto mode
3. Set breakpoints or add logging in `AP_Mission::update()` and `AP_L1_Control::update_waypoint()`
4. Observe the state transitions: takeoff → waypoint tracking → landing approach → flare → touchdown
5. Trace the data flow: mission command → L1 lateral guidance → TECS speed/height → attitude controllers → servos
6. Review `CTUN`, `NTUN`, and `TECS` log messages during approach and landing

---

### Module 11: Debugging & Troubleshooting (2h) — Lecture + Hands-on

**Objective**: Master the debugging tools available for ArduPilot development — critical for any software engineering work.

#### Topics

1. **SITL Debugging with GDB**
   - Building with debug symbols: `./waf configure --board sitl --debug`
   - Launching SITL under GDB: `sim_vehicle.py -v ArduPlane --gdb`
   - Setting breakpoints in vehicle code and libraries
   - Stepping through the main loop and scheduled tasks
   - Inspecting variables: parameters, sensor data, controller state
   - Watchpoints for tracking state changes
   - Common GDB commands for ArduPilot debugging

2. **Printf-Style Debugging**
   - `GCS_SEND_TEXT(MAV_SEVERITY_INFO, "...")`: send text to GCS console
   - `AP::logger().Write(...)`: log data for post-analysis
   - `hal.console->printf(...)`: direct console output (SITL only)
   - When to use each method and their limitations

3. **Log Analysis for Code Debugging**
   - Using logs to verify code behavior (not just flight performance)
   - Custom log messages for debugging specific subsystems
   - MAVExplorer graphing: overlaying multiple data streams
   - Time-correlating events across different log messages
   - Using `mavlogdump.py` for text-based log analysis and scripting
   - Plane-specific log debugging: correlating `CTUN` (control outputs), `TECS` (energy states), and `NTUN` (navigation) for full-picture analysis

4. **Common Failure Patterns**
   - EKF divergence: causes, symptoms, diagnosis
   - Watchdog resets: stack overflow, infinite loops, long tasks
   - Parameter corruption: how it happens, how to recover
   - Pre-arm check failures: interpreting and resolving
   - **Plane-specific failures**: airspeed sensor failure mid-flight, TECS oscillation (porpoising), landing flare timing issues

5. **Autotest Framework**
   - Location: `Tools/autotest/`
   - Vehicle test classes: `arducopter.py`, **`arduplane.py`**, `rover.py`
   - How tests work: launch SITL, send commands, assert conditions
   - Writing a simple test: `fly_my_test()` pattern
   - Running tests: `Tools/autotest/autotest.py build.ArduPlane test.ArduPlane.MyTest`
   - Plane-specific test patterns:
     - Takeoff: FBWA with throttle-up and wait for altitude (not vertical takeoff)
     - `wait_level_flight()`: wait until pitch and roll are near zero
     - `fly_mission()`: upload and execute a complete mission file
     - Landing verification: check altitude reaches near-zero
   - Test infrastructure: `wait_ready_to_arm()`, `takeoff()`, `change_mode()`, `wait_altitude()`, etc.

6. **Unit Tests with gtest**
   - Location: `libraries/*/tests/`
   - Building: `./waf --targets tests/test_<name>`
   - Writing a test: gtest macros (`TEST_F`, `EXPECT_EQ`, `ASSERT_NEAR`)
   - Testing math libraries, filter code, parsing functions
   - Running: `./waf check` (changed tests) or `./waf check-all` (all tests)

#### Hands-on Exercise (45 min)
**Three mini-exercises:**

*Exercise A: Debug with GDB (15 min)*
1. Build ArduPlane with debug symbols
2. Launch under GDB: `sim_vehicle.py -v ArduPlane --gdb`
3. Set a breakpoint in `AP_TECS::update_pitch_throttle()`
4. Arm and fly in FBWA, hit the breakpoint
5. Inspect TECS state: total energy error, energy balance, throttle/pitch demands

*Exercise B: Write an autotest (15 min)*
1. Add a simple test method to `arduplane.py`
2. Test: arm, takeoff in FBWA, fly to CRUISE mode, verify altitude hold within tolerance
3. Run the test with `autotest.py build.ArduPlane test.ArduPlane`

*Exercise C: Write a gtest (15 min)*
1. Create a simple unit test for a math function (e.g., vector operations)
2. Build with `./waf --targets tests/test_<name>`
3. Run the test
4. Add a test case that intentionally fails, observe the output

---

### Module 12: Porting ArduPilot to Custom Boards (2.5h) — Lecture + Hands-on

**Objective**: Understand the complete process of adding support for a custom flight controller board — the most directly relevant module for engineers planning to build custom hardware.

#### Topics

1. **hwdef File Structure**
   - Location: `libraries/AP_HAL_ChibiOS/hwdef/<boardname>/hwdef.dat`
   - What hwdef defines: everything the HAL needs to know about the hardware
   - One hwdef per board, can include other hwdef files (layered definitions)

2. **hwdef Syntax & Key Directives**
   - `MCU STM32F4xx STM32F427xx` — MCU family and specific chip
   - `FLASH_SIZE_KB 2048` — flash memory size
   - `RAM_SIZE_KB 256` — RAM size
   - `OSCILLATOR_HZ 24000000` — external crystal frequency
   - `SERIAL_ORDER` — UART assignment order
   - `define HAL_STORAGE_SIZE 16384` — storage allocation

3. **Pin Mapping**
   - GPIO pin definitions: `PA0`, `PB3`, `PC13`, etc. (STM32 naming)
   - Peripheral assignment: `PA0 UART4_TX UART4` — pin, function, peripheral
   - SPI bus definition: `SPIDEV name SPI1 DEVID1 CS_PIN MODE3 1*MHZ 8*MHZ`
   - I2C bus definition: `I2C_ORDER I2C1 I2C2`
   - PWM output: `PB0 TIM3_CH3 TIM3 PWM(1) GPIO(50)` — for servo channels
   - ADC: `PC0 BATT_VOLTAGE_SENS ADC1 SCALE(1)`
   - LED: `PA8 LED_ACTIVITY OUTPUT LOW GPIO(90)`

4. **Peripheral Declarations**
   - IMU: `IMU Invensense SPI:icm20689 ROTATION_NONE`
   - Barometer: `BARO MS56XX SPI:ms5611`
   - Compass: `COMPASS IST8310 I2C:0:0x0e false ROTATION_NONE`
   - Airspeed: `AIRSPEED MS4525 I2C:1:0x28` — plane boards may include an I2C airspeed sensor
   - How the build system uses these to auto-generate driver probe code

5. **hwdef.dat → hwdef.h Pipeline**
   - `libraries/AP_HAL_ChibiOS/hwdef/scripts/chibios_hwdef.py` — the processing script
   - Input: `hwdef.dat` + ChibiOS MCU definitions
   - Output: `hwdef.h` (C header with pin defines, peripheral config)
   - Generated files in `build/<board>/libraries/AP_HAL_ChibiOS/hwdef/`

6. **Bootloader**
   - Bootloader hwdef: separate `hwdef-bl.dat` in the same directory
   - Bootloader functionality: firmware update via USB/serial
   - Building: `./waf configure --board <board> --bootloader && ./waf bootloader`

7. **Testing a New Board**
   - Build firmware for the new board
   - Common build errors and how to fix them
   - Testing with SITL-on-hardware concept
   - Validating peripheral detection and sensor operation

8. **Linux HAL Porting (Overview)**
   - When to use Linux HAL vs ChibiOS HAL
   - Linux board definitions in `libraries/AP_HAL_Linux/`
   - Key differences: device tree, sysfs, userspace I/O
   - Example: Raspberry Pi, BeagleBone configurations

#### Key Files to Examine
```
libraries/AP_HAL_ChibiOS/hwdef/CubeBlack/hwdef.dat       — full-featured board
libraries/AP_HAL_ChibiOS/hwdef/CubeBlack/hwdef-bl.dat     — bootloader hwdef
libraries/AP_HAL_ChibiOS/hwdef/Pixhawk6X/hwdef.dat        — modern board
libraries/AP_HAL_ChibiOS/hwdef/scripts/chibios_hwdef.py   — hwdef processor
libraries/AP_HAL_ChibiOS/hwdef/common/stm32f4_flash.ld    — linker scripts
```

#### Hands-on Exercise (50 min)
**Create a hwdef for a hypothetical custom fixed-wing board:**

Scenario: You have a custom board designed for fixed-wing aircraft with:
- STM32F427 MCU (same as Pixhawk 1)
- ICM-42688 IMU on SPI1
- MS5611 barometer on SPI2
- IST8310 compass on I2C1
- MS4525 airspeed sensor on I2C2 (plane-specific!)
- u-blox GPS on UART2
- Telemetry on UART1
- 8 PWM outputs (aileron L, aileron R, elevator, rudder, throttle, flap L, flap R, spare)
- Battery voltage/current sensing on ADC
- USB for configuration

Steps:
1. Create a new directory: `libraries/AP_HAL_ChibiOS/hwdef/CustomPlaneBoard/`
2. Start from an existing hwdef (CubeBlack) and modify for the custom hardware
3. Define pin mappings for all peripherals (including airspeed sensor)
4. Define SPI and I2C bus assignments
5. Configure UART order
6. Set up sensor declarations (including airspeed)
7. Build firmware: `./waf configure --board CustomPlaneBoard && ./waf plane`
8. Fix any build errors
9. Discussion: what would the bring-up process look like on real hardware? What's different about verifying a plane board vs. a copter board? (Answer: airspeed sensor validation, servo direction checks, control surface travel verification)

---

### Module 13: Lua Scripting (1h) — Lecture + Hands-on

**Objective**: Understand Lua scripting as a rapid-prototyping tool for custom behaviors without modifying C++ code.

#### Topics

1. **AP_Scripting Architecture**
   - Lua VM embedded in ArduPilot
   - Script loading: `APM/scripts/` directory on SD card (or SITL filesystem)
   - Sandbox: limited API surface, resource limits
   - Execution model: cooperative multitasking, called from scheduler
   - Script lifecycle: load → run → sleep → run → ...

2. **Available Lua APIs**
   - `ahrs`: get attitude, position, velocity, **wind estimate**
   - `vehicle`: get/set flight mode
   - `param`: read/write parameters
   - `gcs`: send text messages, receive commands
   - `rc`: read RC channels
   - `serial`: UART access for custom protocols
   - `can`: CAN bus access (DroneCAN)
   - `mission`: mission manipulation
   - `SRV_Channels`: **set servo outputs directly** (useful for plane actuators: flaps, spoilers, gear)
   - Binding generation: `libraries/AP_Scripting/generator/`

3. **Use Cases for Plane**
   - Custom flight behaviors (geofence actions, automated maneuvers)
   - **Airspeed-based flap scheduling**: automatically deploy/retract flaps based on airspeed
   - **Wind-compensated maneuvers**: adjust patterns based on wind estimate
   - Payload control (camera triggers, release mechanisms)
   - Sensor processing (companion computer data parsing)
   - Prototyping features before C++ implementation

4. **Lua vs. C++ Modification**
   - Lua: rapid iteration, no rebuild, safe sandbox, but limited API and performance
   - C++: full access, highest performance, but requires rebuild and deeper knowledge
   - Decision framework: when to use which approach

#### Hands-on Exercise (20 min)
**Write a Lua script that monitors airspeed and controls flaps:**
1. Create a script that:
   - Reads current airspeed from AHRS
   - Implements automatic flap scheduling:
     - Below 15 m/s: full flaps (for landing approach)
     - 15–20 m/s: half flaps
     - Above 20 m/s: flaps retracted (clean configuration)
   - Sends a GCS warning when airspeed drops below a stall threshold
   - Logs the flap state as a custom message
2. Deploy to SITL `scripts/` directory
3. Fly in SITL and observe the flap behavior during different flight phases
4. Modify the speed thresholds without rebuilding ArduPilot

---

## Day 5: Integration, Simulation & Advanced Workshop (7h)

---

### Module 14: Putting It All Together (2h) — Guided Project

**Objective**: Apply all knowledge from Days 1-4 in an end-to-end development exercise, reinforcing the full development cycle.

#### Project Options (choose one per team/individual)

**Option A: Custom Flight Mode**
- Create a new flight mode for plane (e.g., "Heading-Hold with Altitude Step" — maintain a heading while climbing/descending to a target altitude in steps)
- Add mode class in `ArduPlane/`, register in mode table
- Implement using `AP_L1_Control` for heading hold and `AP_TECS` for altitude/airspeed control
- Add parameters for heading, step size, and target airspeed
- Test in SITL, verify in logs

**Option B: Sensor Driver Stub**
- Create a stub driver for a hypothetical sensor (e.g., a custom airspeed sensor with a novel interface)
- Follow the frontend/backend pattern used by `AP_Airspeed`
- Add a SITL backend that generates synthetic airspeed data
- Wire into the vehicle code
- Verify data appears in `ARSP` logs

**Option C: Parameter-Triggered Behavior**
- Add a parameter-triggered automatic flap deployment system:
  - New parameters: `AUTO_FLAP_ENABLE`, `AUTO_FLAP_SPD` (speed threshold), `AUTO_FLAP_DEG` (flap deflection)
  - Monitor airspeed in a scheduled task
  - When airspeed drops below threshold, deploy flaps via `SRV_Channels`
  - Add logging and GCS messaging
  - Write a test for the behavior

#### Development Cycle for All Options
1. Design the feature (whiteboard/document)
2. Write the code
3. Build for SITL: `./waf plane`
4. Test in SITL: `sim_vehicle.py -v ArduPlane`
5. Verify behavior in logs
6. Write an autotest or gtest for the feature
7. Code review discussion: follows ArduPilot conventions?

---

### Module 15: Realistic Simulation with Pegasus Simulator (2h) — Optional Add-on

**Objective**: Explore advanced simulation capabilities for GNC development beyond SITL's basic physics.

**Prerequisites**: NVIDIA RTX GPU, Isaac Sim pre-installed on training workstations.

#### Topics

1. **Limitations of SITL's Built-in Physics**
   - SITL physics: simplified models sufficient for logic testing
   - What SITL lacks: realistic aerodynamics (simplified lift/drag model), environmental effects (wind gusts, turbulence, ground effect), visual rendering
   - When you need more: vision-based navigation, sensor fusion validation, realistic landing simulation

2. **Pegasus Simulator Overview**
   - Based on NVIDIA Isaac Sim (Omniverse platform)
   - Photorealistic rendering with physically-based materials
   - Sensor simulation: camera (RGB, depth), lidar, IMU with realistic noise models
   - Multiple vehicle support, customizable environments
   - Open-source extension for Isaac Sim

3. **Architecture: Pegasus + ArduPilot**
   - Pegasus runs the physics and rendering
   - ArduPilot SITL runs the flight code
   - Communication: MAVLink over UDP (same as standard SITL)
   - Pegasus replaces SITL's physics backend while ArduPilot remains unchanged
   - Configuration: **fixed-wing vehicle model** (different physics from multirotor — lift, drag, control surfaces)

4. **Use Cases for Fixed-Wing GNC Engineers**
   - Realistic aerodynamic simulation (stall behavior, wind response, ground effect during landing)
   - Vision-based navigation testing (optical flow, terrain following)
   - Sensor fusion validation with realistic noise characteristics
   - Landing simulation with terrain models
   - Multi-vehicle formation flying scenarios

5. **Comparison with Other Simulators**
   - Gazebo: open-source, good ROS integration, moderate visuals
   - AirSim/Colosseum: Unreal Engine-based, good visuals, Microsoft heritage
   - Pegasus: best visual fidelity, GPU-heavy, NVIDIA ecosystem
   - **FlightGear / JSBSim**: fixed-wing focused, high-fidelity aerodynamic models, ArduPilot has native JSBSim backend
   - X-Plane: commercial, realistic aerodynamics
   - When to use which simulator

#### Hands-on Exercise (45 min)
1. Launch Isaac Sim with Pegasus extension
2. Configure an ArduPlane vehicle in a photorealistic environment with a runway
3. Start ArduPilot SITL connected to Pegasus
4. Fly a mission (same mission from Day 1, including landing)
5. Compare sensor data: standard SITL vs. Pegasus
6. Test landing approach with more realistic ground effect simulation
7. Discussion: how would you use this for your development workflow?

---

### Module 16: Advanced Topics & Q&A Workshop (3h) — Interactive

**Objective**: Address team-specific questions and explore advanced topics of interest.

#### Prepared Topic Menu (select based on audience interest)

**QuadPlane / VTOL Architecture (45 min)**
- What QuadPlane is: fixed-wing aircraft with vertical takeoff/landing motors
- `ArduPlane/quadplane.h` / `quadplane.cpp` — one of the most complex files in ArduPilot (~191KB)
- How QuadPlane merges copter-style control (for VTOL phases) with plane-style control (for forward flight)
- Transition management: VTOL → forward flight → VTOL
- Modes: `QSTABILIZE`, `QHOVER`, `QLOITER`, `QLAND`, `QRTL`
- Motor mixing: plane servos + VTOL motors active simultaneously during transition
- Key parameters: `Q_ENABLE`, `Q_FRAME_TYPE`, `Q_ASSIST_SPEED`
- Architecture study: how one vehicle class manages two completely different flight regimes

**Soaring: Autonomous Thermal Detection (`libraries/AP_Soaring/`) (30 min)**
- Thermal soaring: detecting rising air and circling to gain altitude
- `AP_Soaring` library: variometer, thermal model, state machine
- How it works: detect positive climb rate → enter loiter → estimate thermal center → adjust circle
- Control interaction: soaring overrides TECS altitude demand when a thermal is detected
- Parameters: `SOAR_ENABLE`, `SOAR_VSPEED`, `SOAR_MIN_THML_S`
- Research applications: long-endurance UAV flight

**Autoland & Deepstall Landing (30 min)**
- Standard autoland: approach on glide slope, flare, touchdown
- `AP_Landing_Deepstall`: intentional stall for steep descent — used for precision landing in confined areas
- Deepstall state machine: approach → positioning → fly-away → stall descent → flare
- Key parameters and tuning
- When to use deepstall vs. normal landing

**Tailsitter & Tiltrotor Configurations (30 min)**
- Tailsitter: entire aircraft rotates between hover (vertical) and forward flight
- Tiltrotor: motors tilt between vertical and horizontal thrust
- How ArduPlane handles frame-relative vs. earth-relative control switching
- `ArduPlane/tailsitter.cpp` — tailsitter-specific code
- Challenges: control surface effectiveness at hover vs. forward flight

**DroneCAN / UAVCAN (45 min)**
- Protocol overview: CAN bus communication for peripherals
- ArduPilot DroneCAN implementation: `libraries/AP_DroneCAN/`
- DroneCAN peripherals: GPS, compass, **airspeed sensor**, ESC, LED
- Configuring DroneCAN devices in ArduPilot

**AP_DDS / ROS 2 Integration (45 min)**
- Micro-XRCE-DDS bridge: how ArduPilot talks to ROS 2
- `libraries/AP_DDS/`: publisher/subscriber implementation
- Available ROS 2 topics and services
- Use cases: companion computer integration, SLAM, path planning

**Contributing to ArduPilot (30 min)**
- Git workflow: fork, branch, commit, PR
- CI system: autotest, build checks
- Code review process and conventions
- Getting changes accepted upstream

#### Open Lab (remaining time)
- Individual experimentation time
- Team-specific questions and debugging
- Work on hands-on exercises not completed earlier
- Deep-dive into specific code areas of interest

#### Wrap-up (15 min)
- Key takeaways review
- Recommended resources:
  - ArduPilot developer documentation: https://ardupilot.org/dev/
  - ArduPilot source: https://github.com/ArduPilot/ardupilot
  - Discussion forum: https://discuss.ardupilot.org
  - Discord developer channels
  - ArduPlane-specific documentation: https://ardupilot.org/plane/
- Next steps for the team
- Feedback collection

---

## Appendices

### A. Pre-Course Setup Requirements

Each workstation needs:
- Linux (Ubuntu 22.04 recommended) or macOS
- ArduPilot source code cloned with submodules
- Build dependencies installed (`Tools/environment_install/install-prereqs-ubuntu.sh`)
- ARM toolchain for hardware builds
- Python 3 with pymavlink, MAVProxy installed
- A code editor/IDE (VS Code recommended with C++ and Python extensions)
- GDB for debugging
- Mission Planner or QGroundControl installed (for log viewing)
- (Optional for Module 15) NVIDIA GPU with RTX, Isaac Sim + Pegasus extension

### B. Reference: Key Source Files by Module

| Module | Key Files |
|--------|-----------|
| 1. Overview | `ArduPlane/Plane.h`, `ArduPlane/Plane.cpp` |
| 4. Build System | `wscript`, `Tools/scripts/build_options.py` |
| 5. HAL | `libraries/AP_HAL/`, `libraries/AP_HAL_ChibiOS/`, `libraries/AP_HAL_SITL/` |
| 6. Infrastructure | `libraries/AP_Scheduler/`, `libraries/AP_Param/`, `libraries/AP_Logger/` |
| 7. Sensors | `libraries/AP_Airspeed/`, `libraries/AP_Baro/`, `libraries/AP_InertialSensor/`, `libraries/AP_GPS/` |
| 8. AHRS/EKF | `libraries/AP_AHRS/`, `libraries/AP_NavEKF3/` |
| 9. Control | `libraries/APM_Control/`, `libraries/AP_TECS/`, `libraries/AP_L1_Control/`, `libraries/SRV_Channel/` |
| 10. Mission | `libraries/AP_Mission/`, `libraries/AP_L1_Control/`, `libraries/AP_Landing/` |
| 11. Debugging | `Tools/autotest/arduplane.py`, `libraries/*/tests/` |
| 12. Porting | `libraries/AP_HAL_ChibiOS/hwdef/` |
| 13. Lua | `libraries/AP_Scripting/` |

### C. Copter vs. Plane: Key Library Mapping

| Component | Copter Library | Plane Library |
|-----------|---------------|--------------|
| Main class | `ArduCopter/Copter.h` | `ArduPlane/Plane.h` |
| Scheduler | `ArduCopter/Copter.cpp` (400 Hz) | `ArduPlane/Plane.cpp` (50 Hz) |
| Mode base | `ArduCopter/mode.h` | `ArduPlane/mode.h` |
| Attitude control | `AC_AttitudeControl` (unified) | `APM_Control` (separate Roll/Pitch/Yaw controllers) |
| Position/altitude | `AC_PosControl` (3D position) | `AP_TECS` (energy-based altitude/airspeed) |
| Navigation | `AC_WPNav` (3D waypoint tracking) | `AP_L1_Control` (lateral path following) |
| Motor/servo output | `AP_Motors/AP_MotorsMatrix` (motor mixing) | `SRV_Channels` (servo assignments) |
| Airspeed | N/A | `AP_Airspeed` (critical sensor) |
| Landing | N/A (vertical descent) | `AP_Landing` (approach/flare/touchdown) |
| Soaring | N/A | `AP_Soaring` (thermal detection) |
| VTOL hybrid | N/A | `ArduPlane/quadplane.h/.cpp` |
| Autotest | `Tools/autotest/arducopter.py` | `Tools/autotest/arduplane.py` |

### D. Comparison: Standard Curriculum vs. This Custom Course

| Aspect | Standard Proposals (10-18h) | This Custom Course (34h) |
|--------|----------------------------|--------------------------|
| **Operations content** | 50-60% of total time | ~12% (Day 1 morning, compressed) |
| **Flight code coverage** | 2h overview (Proposal 4 only) | 20h+ deep code content (Days 2-5) |
| **Build system** | Not covered | Full module (2h) with hands-on |
| **HAL architecture** | Not covered | 2.5h deep-dive with code tracing |
| **Debugging tools** | Not covered | 2h on GDB, logging, autotest, gtest |
| **Board porting** | Not covered | 2.5h with hands-on hwdef creation |
| **Sensor architecture** | Brief mention | 2h with driver tracing exercises (including airspeed) |
| **EKF internals** | Brief mention | 2.5h with noise injection and wind estimation exercises |
| **Control pipeline** | Brief mention | 2.5h covering TECS, L1, APM_Control, servo output |
| **Fixed-wing specifics** | N/A | Full coverage: airspeed, TECS, L1, landing, soaring, QuadPlane |
| **Assembly/indoor flight** | 2-6h | Not included (not relevant) |
| **Hands-on focus** | Fly a drone | Build, modify code, debug, test |
| **Target audience** | Operators/integrators | Software engineers |

### E. Customer Requirements Traceability

Requirements from customer feedback mapped to course modules:

| Customer Need | Module(s) |
|---------------|-----------|
| ArduPilot basics | Module 1 (Overview), Module 2 (Operations) |
| Software architecture overview | Module 5 (HAL), Module 6 (Infrastructure) |
| Getting started developing code | Module 4 (Build System), Module 14 (Integration Project) |
| Compiler tools | Module 4 (Waf Build System) |
| Debug and troubleshoot | Module 11 (Debugging & Troubleshooting) |
| Port to custom board | Module 12 (Board Porting) |
| Where functions are, how they work | Module 7 (Sensors), Module 8 (AHRS/EKF), Module 9 (Control Pipeline), Module 10 (Mission/Nav) |
| Understand flight code structure | Modules 5-9 (full architecture coverage) |
| Study ArduPilot algorithms | Module 8 (EKF + wind estimation), Module 9 (TECS, L1, APM_Control) |
| Support existing ArduPilot platforms | Modules 2, 7, 8, 9, 11 (operations + debugging + internals) |
| Build custom flight controllers | Module 12 (Board Porting) |
| Fixed-wing specific systems | Module 7 (airspeed), Module 9 (TECS/L1/APM_Control), Module 10 (landing), Module 16 (QuadPlane/soaring/deepstall) |
