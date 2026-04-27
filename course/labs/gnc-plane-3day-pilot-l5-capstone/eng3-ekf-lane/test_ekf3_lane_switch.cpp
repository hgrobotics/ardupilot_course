/*
 * test_ekf3_lane_switch.cpp — initially-failing gtest stub for EKF3 lane switch.
 *
 * YOUR TASK:
 *   1. Read AP_NavEKF3.cpp:1029-1078 (checkLaneSwitch, switchLane).
 *   2. Extract the lane-switch logic into a new file: lane_switch.cpp.
 *      Your extracted class must use IEKFCoreObservable (from mock_NavEKF3_core.h)
 *      instead of calling core[i] directly — that is the seam you are finding.
 *   3. Update CMakeLists.txt: uncomment the lane_switch.cpp line.
 *   4. Make these two tests pass:
 *        [ PASSED ] EKF3LaneSwitch.SelectsLowestErrorBelowGate
 *        [ PASSED ] EKF3LaneSwitch.HonorsFiveSecondDebounce
 *
 * WHAT THE TESTS CHECK:
 *
 *   Test 1 (SelectsLowestErrorBelowGate):
 *     Given 2 cores where core 0 has errorScore=0.8 and core 1 has
 *     errorScore=0.3 (both < 0.9 gate), checkLaneSwitch() must switch
 *     the primary to core 1 (the lower score).
 *
 *   Test 2 (HonorsFiveSecondDebounce):
 *     After a lane switch, a second call to checkLaneSwitch() within 5000 ms
 *     must NOT switch again (even if another core would otherwise win).
 *
 * SOURCE REFERENCE:
 *   checkLaneSwitch: libraries/AP_NavEKF3/AP_NavEKF3.cpp:1029-1061
 *   switchLane:      libraries/AP_NavEKF3/AP_NavEKF3.cpp:1064-1078
 *   errorScore gate: 0.9 (line 1052)
 *   debounce:        5000 ms (line 1038)
 */

#include <gtest/gtest.h>

#ifdef EKF3_LANE_SWITCH_EXTRACTED
// Real tests — enabled after extraction
#include "mock_NavEKF3_core.h"
#include "lane_switch.h"   // your extracted header

TEST(EKF3LaneSwitch, SelectsLowestErrorBelowGate) {
    // Setup: 2 cores; primary=0, core1 is healthier
    MockEKFCore cores[2];
    cores[0].state.error_score = 0.8f;  // primary — bad but below 0.9
    cores[1].state.error_score = 0.3f;  // backup — clearly better

    LaneSwitchLogic ls;
    ls.setCores(cores, 2);
    ls.setPrimary(0);
    ls.setLastSwitchTime(0);       // no recent switch
    ls.setCurrentTime(10000);      // 10 s into flight

    ls.checkLaneSwitch();

    EXPECT_EQ(ls.getPrimary(), 1)
        << "Expected lane switch to core 1 (lowest error 0.3 vs 0.8)";
}

TEST(EKF3LaneSwitch, HonorsFiveSecondDebounce) {
    MockEKFCore cores[2];
    cores[0].state.error_score = 0.8f;
    cores[1].state.error_score = 0.3f;

    LaneSwitchLogic ls;
    ls.setCores(cores, 2);
    ls.setPrimary(0);
    ls.setLastSwitchTime(0);
    ls.setCurrentTime(10000);

    // First call should switch
    ls.checkLaneSwitch();
    EXPECT_EQ(ls.getPrimary(), 1) << "First switch should succeed";

    uint32_t switch_time = ls.getLastSwitchTime();

    // Now make core0 even better — but only 2 s later (within 5s debounce)
    cores[0].state.error_score = 0.1f;
    ls.setCurrentTime(switch_time + 2000);  // 2 s later
    ls.checkLaneSwitch();

    // Should NOT have switched back
    EXPECT_EQ(ls.getPrimary(), 1)
        << "Lane switch within 5 s debounce window should be suppressed";
}

#else
// Stub: always fails until extraction is done

TEST(EKF3LaneSwitch, SelectsLowestErrorBelowGate) {
    FAIL() << "EKF3 lane-switch logic not yet extracted. "
           << "Read AP_NavEKF3.cpp:1029-1078, extract the logic "
           << "into lane_switch.cpp using IEKFCoreObservable, "
           << "update CMakeLists.txt, and define EKF3_LANE_SWITCH_EXTRACTED.";
}

TEST(EKF3LaneSwitch, HonorsFiveSecondDebounce) {
    FAIL() << "EKF3 lane-switch logic not yet extracted. "
           << "See SelectsLowestErrorBelowGate for instructions.";
}
#endif
