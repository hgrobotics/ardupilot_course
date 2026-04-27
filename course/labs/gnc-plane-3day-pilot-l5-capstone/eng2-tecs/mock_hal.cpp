/*
 * mock_hal.cpp — minimal HAL stubs for the TECS extraction lab.
 * Same structure as eng1-l1/mock_hal.cpp.
 */

#include <chrono>
#include <cstdint>

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

extern "C" void gcs_send_text_P(uint8_t, const char*) {}
