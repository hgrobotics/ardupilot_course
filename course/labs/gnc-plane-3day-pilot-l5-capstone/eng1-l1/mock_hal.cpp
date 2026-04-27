/*
 * mock_hal.cpp — minimal HAL stubs for the L1 extraction lab.
 *
 * Provides the three HAL symbols most extraction exercises need:
 *   AP_HAL::millis()    — monotonic ms counter
 *   AP_HAL::micros()    — monotonic us counter
 *   AP_HAL::millis64()  — 64-bit ms counter
 *   AP_HAL::micros64()  — 64-bit us counter
 *
 * This file does NOT provide the full `hal` singleton (which requires all
 * HAL subsystems). If AP_L1_Control.cpp transitively requires `hal.scheduler`
 * or `hal.console`, add a stub for the specific call in a new file.
 *
 * Engineers: do not modify this file. If you need additional HAL stubs,
 * add them in mock_hal_extras.cpp.
 */

#include <chrono>
#include <cstdint>

// AP_HAL free function declarations (match AP_HAL/AP_HAL.h)
namespace AP_HAL {

static auto s_epoch = std::chrono::steady_clock::now();

uint32_t millis()
{
    auto now = std::chrono::steady_clock::now();
    return static_cast<uint32_t>(
        std::chrono::duration_cast<std::chrono::milliseconds>(now - s_epoch).count()
    );
}

uint64_t millis64()
{
    return static_cast<uint64_t>(millis());
}

uint32_t micros()
{
    auto now = std::chrono::steady_clock::now();
    return static_cast<uint32_t>(
        std::chrono::duration_cast<std::chrono::microseconds>(now - s_epoch).count()
    );
}

uint64_t micros64()
{
    return static_cast<uint64_t>(micros());
}

} // namespace AP_HAL

/*
 * GCS_SEND_TEXT stub — AP_L1_Control does not call this directly,
 * but AP_Param may. Provide a no-op to avoid link errors.
 */
extern "C" void gcs_send_text_P(uint8_t, const char*) {}
