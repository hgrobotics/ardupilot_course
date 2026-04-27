/*
 * mock_NavEKF3_core.h — configurable mock NavEKF3_core for the lane-switch test.
 *
 * The lane-switch logic in NavEKF3::checkLaneSwitch() calls:
 *   core[i].errorScore()       -> float (0 = perfect, >1 = very bad)
 *   core[i].healthy()          -> bool
 *   core[i].have_aligned_yaw() -> bool
 *   core[i].have_aligned_tilt()-> bool
 *
 * This mock provides configurable return values so your test can set up
 * arbitrary scenarios without needing the full EKF state machine.
 *
 * IMPORTANT: the mock does NOT inherit from the real NavEKF3_core because
 * that would drag in the full EKF dependency chain. Instead, the extracted
 * lane_switch.cpp must be refactored to work against this interface.
 * That refactoring IS the capstone exercise — it teaches you where the
 * coupling seam is.
 */

#pragma once
#include <cstdint>

// A configurable stand-in for NavEKF3_core's observable interface.
struct MockCoreState {
    float  error_score{0.5f};   // returned by errorScore()
    bool   is_healthy{true};    // returned by healthy()
    bool   yaw_aligned{true};   // returned by have_aligned_yaw()
    bool   tilt_aligned{true};  // returned by have_aligned_tilt()
};

// Thin interface adapter the extracted lane_switch.cpp can call.
// Replace calls to core[i].errorScore() etc. in your extracted slice with
// calls through this interface.
class IEKFCoreObservable {
public:
    virtual float  errorScore() const = 0;
    virtual bool   healthy() const = 0;
    virtual bool   have_aligned_yaw() const = 0;
    virtual bool   have_aligned_tilt() const = 0;
    virtual ~IEKFCoreObservable() = default;
};

class MockEKFCore final : public IEKFCoreObservable {
public:
    MockCoreState state;

    float errorScore() const override { return state.error_score; }
    bool  healthy() const override { return state.is_healthy; }
    bool  have_aligned_yaw() const override { return state.yaw_aligned; }
    bool  have_aligned_tilt() const override { return state.tilt_aligned; }
};
