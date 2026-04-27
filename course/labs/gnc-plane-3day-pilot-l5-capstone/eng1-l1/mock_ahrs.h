/*
 * mock_ahrs.h — minimal AHRS stub for the L1 extraction lab.
 *
 * AP_L1_Control stores a reference to AP_AHRS and calls:
 *   get_location(Location&)     -> bool
 *   groundspeed_vector()        -> Vector2f (NE ground speed m/s)
 *   get_yaw()                   -> float (radians)
 *   get_yaw_sensor()            -> int32_t (centidegrees * 100)
 *
 * APPROACH FOR THIS LAB:
 * Because AP_AHRS is a complex class with many dependencies, the recommended
 * approach is to:
 *   1. Create a thin shim struct that satisfies the AP_L1_Control constructor.
 *   2. Add the four methods above (which are virtual in AP_AHRS).
 *
 * If AP_L1_Control only calls these four methods, you can subclass AP_AHRS
 * and override only those four. The compile will fail if it calls others.
 * Add override stubs for any additional methods the linker demands.
 *
 * Alternatively (simpler seam): modify your copy of AP_L1_Control.cpp to
 * accept an abstract interface instead of AP_AHRS&. This IS the seam-finding
 * exercise.
 *
 * This header provides a starting template. Adjust as needed.
 */

#pragma once

#include <AP_Math/AP_Math.h>
#include <AP_Common/Location.h>

// Forward-declare enough to compile without full AP_AHRS.h if it causes issues.
// Engineers: if including AP_AHRS/AP_AHRS.h causes a cascade of errors,
// try forward-declaring and using the minimal interface pattern instead.

#if __has_include(<AP_AHRS/AP_AHRS.h>)
  #include <AP_AHRS/AP_AHRS.h>

  class MockAHRS final : public AP_AHRS {
  public:
      Location   mock_location{};
      Vector2f   mock_groundspeed_vector{10.0f, 0.0f};
      float      mock_yaw{0.0f};
      int32_t    mock_yaw_sensor{0};

      bool get_location(Location& loc) const override {
          loc = mock_location;
          return true;
      }
      Vector2f groundspeed_vector() const override { return mock_groundspeed_vector; }
      float get_yaw() const override { return mock_yaw; }
      int32_t get_yaw_sensor() const override { return mock_yaw_sensor; }

      // Stub all pure-virtual methods not used by AP_L1_Control
      float get_pitch() const override { return 0.0f; }
      float get_roll() const override { return 0.0f; }
      bool get_velocity_NED(Vector3f& v) const override { v.zero(); return false; }
      bool get_relative_position_NED_home(Vector3f& v) const override { v.zero(); return false; }
      bool airspeed_estimate(float& as) const override { as = 15.0f; return true; }
      bool airspeed_estimate_true(float& as) const override { as = 15.0f; return true; }
      float groundspeed() const override { return mock_groundspeed_vector.length(); }
      bool use_compass() const override { return false; }
      void update() override {}
      void reset_gyro_drift() override {}
      void reset() override {}
      bool healthy() const override { return true; }
      bool initialised() const override { return true; }
      bool get_hagl(float&) const override { return false; }
      bool pre_arm_check(bool, char*, uint8_t) const override { return true; }
      bool get_position(Location& loc) const override { return get_location(loc); }
  };

#else
  // Fallback if AP_AHRS.h cannot be included: define only the methods L1 uses.
  // This requires modifying AP_L1_Control.cpp to accept this struct instead.
  struct MockAHRS {
      Location   mock_location{};
      Vector2f   mock_groundspeed_vector{10.0f, 0.0f};
      float      mock_yaw{0.0f};
      int32_t    mock_yaw_sensor{0};

      bool get_location(Location& loc) const { loc = mock_location; return true; }
      Vector2f groundspeed_vector() const { return mock_groundspeed_vector; }
      float get_yaw() const { return mock_yaw; }
      int32_t get_yaw_sensor() const { return mock_yaw_sensor; }
  };
#endif
