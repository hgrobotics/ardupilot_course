/*
 * mock_ahrs.h — minimal AHRS stub for the TECS extraction lab.
 *
 * AP_TECS calls:
 *   get_pitch()                -> float (radians)
 *   get_velocity_NED()         -> bool, Vector3f out
 *   airspeed_estimate()        -> bool, float out (m/s)
 *   airspeed_estimate_true()   -> bool, float out
 *   get_location()             -> bool, Location out
 *
 * Same pattern as eng1-l1/mock_ahrs.h — subclass AP_AHRS if available,
 * fall back to a plain struct if the AP_AHRS include cascade is too heavy.
 */

#pragma once

#include <AP_Math/AP_Math.h>
#include <AP_Common/Location.h>

#if __has_include(<AP_AHRS/AP_AHRS.h>)
  #include <AP_AHRS/AP_AHRS.h>

  class MockAHRS final : public AP_AHRS {
  public:
      float    mock_pitch{0.0f};
      float    mock_yaw{0.0f};
      Vector3f mock_velocity_NED{15.0f, 0.0f, 0.0f};
      float    mock_airspeed{15.0f};
      Location mock_location{};

      float get_pitch() const override { return mock_pitch; }
      float get_yaw() const override { return mock_yaw; }
      float get_roll() const override { return 0.0f; }

      bool get_velocity_NED(Vector3f& v) const override {
          v = mock_velocity_NED; return true;
      }
      bool airspeed_estimate(float& as) const override { as = mock_airspeed; return true; }
      bool airspeed_estimate_true(float& as) const override { as = mock_airspeed; return true; }
      float groundspeed() const override { return mock_velocity_NED.length(); }
      bool get_location(Location& loc) const override { loc = mock_location; return true; }
      Vector2f groundspeed_vector() const override {
          return Vector2f(mock_velocity_NED.x, mock_velocity_NED.y);
      }

      int32_t get_yaw_sensor() const override { return 0; }
      bool get_relative_position_NED_home(Vector3f& v) const override { v.zero(); return false; }
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
  struct MockAHRS {
      float    mock_pitch{0.0f};
      float    mock_yaw{0.0f};
      Vector3f mock_velocity_NED{15.0f, 0.0f, 0.0f};
      float    mock_airspeed{15.0f};
      Location mock_location{};

      float get_pitch() const { return mock_pitch; }
      float get_yaw() const { return mock_yaw; }
      bool get_velocity_NED(Vector3f& v) const { v = mock_velocity_NED; return true; }
      bool airspeed_estimate(float& as) const { as = mock_airspeed; return true; }
      bool airspeed_estimate_true(float& as) const { as = mock_airspeed; return true; }
      bool get_location(Location& loc) const { loc = mock_location; return true; }
  };
#endif
