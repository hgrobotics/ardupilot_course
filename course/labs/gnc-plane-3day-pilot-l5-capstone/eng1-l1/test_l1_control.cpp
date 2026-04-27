/*
 * test_l1_control.cpp — initially-failing gtest stub for AP_L1_Control.
 *
 * YOUR TASK:
 *   1. Copy AP_L1_Control.cpp (and AP_L1_Control.h if needed) from
 *      libraries/AP_L1_Control/ into this directory.
 *   2. Update CMakeLists.txt: uncomment the AP_L1_Control.cpp line in
 *      EXTRACTED_SOURCES.
 *   3. Fix any #include path errors that arise.
 *   4. Add stubs for any remaining unresolved symbols.
 *   5. Make this test pass:
 *        [ PASSED ] L1Control.UpdateWaypointTurnsRight
 *
 * WHAT THE TEST CHECKS:
 *   A plane is 200 m south of a waypoint at origin and travelling north at
 *   10 m/s. update_waypoint() should produce a lateral acceleration demand
 *   that is ZERO (heading straight to the waypoint, no turn required) and
 *   nav_bearing_cd() should be very close to 0 centidegrees (due north).
 *
 * INITIALLY this test FAILS because AP_L1_Control sources are not yet
 * copied in.  After you copy them and fix includes, it should PASS.
 */

// The test will not compile until AP_L1_Control is extracted.
// We use a compile-time guard so the stub compiles to an always-failing test.

#include <gtest/gtest.h>

#ifdef AP_L1_CONTROL_EXTRACTED
// Real test — enabled after extraction
#include "mock_ahrs.h"
#include <AP_L1_Control/AP_L1_Control.h>
#include <AP_Common/Location.h>
#include <AP_Math/AP_Math.h>
#include <cmath>

TEST(L1Control, UpdateWaypointTurnsRight) {
    MockAHRS ahrs;

    // Position: 200 m south of origin
    Location current{};
    current.lat = -2000;   // -0.002 deg ≈ 222 m south
    current.lng = 0;
    current.alt = 10000;   // 100 m AMSL in cm

    Location prev_wp{};    // origin
    Location next_wp{};    // also origin (same-waypoint case)

    ahrs.mock_location = current;
    // Heading north at 10 m/s
    ahrs.mock_groundspeed_vector = Vector2f(10.0f, 0.0f);
    ahrs.mock_yaw = 0.0f;

    AP_L1_Control l1(ahrs, nullptr);

    l1.update_waypoint(prev_wp, next_wp);

    // Heading straight to the waypoint (north) — lateral accel should be near 0
    float lat_accel = l1.lateral_acceleration();
    EXPECT_NEAR(lat_accel, 0.0f, 2.0f)
        << "lateral_acceleration should be ~0 when flying straight to waypoint";

    // nav_bearing_cd should be 0 (north) ± 1000 centideg = ±10 deg
    int32_t bearing = l1.nav_bearing_cd();
    EXPECT_NEAR(bearing, 0, 1000)
        << "nav_bearing_cd should be ~0 (north) when waypoint is directly ahead";
}

#else
// Stub: always fails until extraction is done
TEST(L1Control, UpdateWaypointTurnsRight) {
    FAIL() << "AP_L1_Control sources not yet extracted. "
           << "Copy AP_L1_Control.cpp from libraries/AP_L1_Control/ "
           << "into this directory, update CMakeLists.txt, "
           << "and define AP_L1_CONTROL_EXTRACTED.";
}
#endif
