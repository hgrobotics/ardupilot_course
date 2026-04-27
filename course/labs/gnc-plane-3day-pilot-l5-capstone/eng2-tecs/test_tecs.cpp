/*
 * test_tecs.cpp — initially-failing gtest stub for AP_TECS.
 *
 * YOUR TASK:
 *   1. Copy AP_TECS.cpp (and AP_TECS.h if needed) from
 *      libraries/AP_TECS/ into this directory.
 *   2. Update CMakeLists.txt: uncomment the AP_TECS.cpp line in
 *      EXTRACTED_SOURCES.
 *   3. Fix any #include path errors.
 *   4. Add stubs for any remaining unresolved symbols
 *      (e.g., AP_FixedWing::FlightStage, AP_Logger::Write stubs).
 *   5. Make this test pass:
 *        [ PASSED ] TECS.OneCycleProducesBoundedDemands
 *
 * WHAT THE TEST CHECKS:
 *   One call to TECS::update_pitch_throttle() with plausible flight state
 *   (level flight, 15 m/s airspeed, 100 m altitude, 100 m target altitude)
 *   must produce:
 *     - throttle demand in [0.0, 1.0]
 *     - pitch demand in [-3000, 3000] centidegrees (i.e. +-30 degrees)
 *
 * INITIALLY this test FAILS because AP_TECS sources are not yet extracted.
 */

#include <gtest/gtest.h>

#ifdef AP_TECS_EXTRACTED
// Real test — enabled after extraction
#include "mock_ahrs.h"
#include <AP_TECS/AP_TECS.h>
#include <cmath>

TEST(TECS, OneCycleProducesBoundedDemands) {
    MockAHRS ahrs;
    ahrs.mock_airspeed = 15.0f;        // m/s
    ahrs.mock_velocity_NED = Vector3f(15.0f, 0.0f, 0.0f);
    ahrs.mock_pitch = 0.0f;

    AP_TECS tecs(ahrs, nullptr, nullptr);

    // One update call: level flight, 100 m, target 100 m, 15 m/s target
    tecs.update_pitch_throttle(
        /*hgt_dem_cm*/    10000,   // 100 m in cm
        /*EAS_dem*/       15.0f,
        /*ptchMinCO_cd*/  -1500,
        /*ptchMaxCO_cd*/   2500,
        /*throttle_nudge*/ 0.0f,
        /*hgt_afe*/       100.0f,
        /*load_factor*/    1.0f,
        /*soaring_active*/ false
    );

    float thr = tecs.get_throttle_demand();
    int32_t ptch = tecs.get_pitch_demand();

    EXPECT_GE(thr, 0.0f)   << "throttle demand must be >= 0";
    EXPECT_LE(thr, 1.0f)   << "throttle demand must be <= 1";
    EXPECT_GE(ptch, -3000) << "pitch demand must be >= -3000 cd";
    EXPECT_LE(ptch,  3000) << "pitch demand must be <= +3000 cd";
}

#else
// Stub: always fails until extraction is done
TEST(TECS, OneCycleProducesBoundedDemands) {
    FAIL() << "AP_TECS sources not yet extracted. "
           << "Copy AP_TECS.cpp from libraries/AP_TECS/ "
           << "into this directory, update CMakeLists.txt, "
           << "and define AP_TECS_EXTRACTED.";
}
#endif
