cmake_minimum_required(VERSION 3.16)
project(EKF3LaneSwitchTest CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(ARDUPILOT_ROOT "${CMAKE_SOURCE_DIR}/../../../.." CACHE PATH
    "Root of the ArduPilot repository")
get_filename_component(ARDUPILOT_ROOT "${ARDUPILOT_ROOT}" ABSOLUTE)

set(GTEST_ROOT "${ARDUPILOT_ROOT}/modules/gtest/googletest")

# ---- gtest ----------------------------------------------------------------
add_library(gtest STATIC "${GTEST_ROOT}/src/gtest-all.cc")
target_include_directories(gtest PUBLIC
    "${GTEST_ROOT}/include" "${GTEST_ROOT}")
# Workaround for GCC >= 15 / glibc >= 2.43: force time.h before pthread.h.
# Harmless on older toolchains.
target_compile_options(gtest PRIVATE -w -include /usr/include/time.h)

add_library(gtest_main STATIC "${GTEST_ROOT}/src/gtest_main.cc")
target_include_directories(gtest_main PUBLIC "${GTEST_ROOT}/include")
target_compile_options(gtest_main PRIVATE -w -include /usr/include/time.h)
target_link_libraries(gtest_main gtest)

# ---- Mock sources ---------------------------------------------------------
set(MOCK_SOURCES
    mock_hal.cpp
)

# ---- Engineer's extracted sources (ADD YOUR FILES HERE) -------------------
# The lane-switch slice consists of:
#   - The LaneSwitch class or the relevant functions extracted into a
#     standalone translation unit (lane_switch.cpp)
# You do NOT extract the full NavEKF3 — only the lane-switch slice.
set(EXTRACTED_SOURCES
    # lane_switch.cpp   # <-- your extracted slice (see instructions)
)

# ---- Include paths --------------------------------------------------------
include_directories(
    "${CMAKE_SOURCE_DIR}"
    "${ARDUPILOT_ROOT}/libraries"
    "${ARDUPILOT_ROOT}/libraries/AP_Math"
    "${ARDUPILOT_ROOT}/libraries/AP_HAL"
    "${ARDUPILOT_ROOT}/libraries/AP_Common"
    "${ARDUPILOT_ROOT}/libraries/AP_Param"
)

# ---- Test executable ------------------------------------------------------
add_executable(ekf3_lane_test
    test_ekf3_lane_switch.cpp
    ${MOCK_SOURCES}
    ${EXTRACTED_SOURCES}
)
target_compile_options(ekf3_lane_test PRIVATE -w -include /usr/include/time.h)
target_link_libraries(ekf3_lane_test gtest_main pthread)

enable_testing()
add_test(NAME EKF3LaneSwitchTests COMMAND ekf3_lane_test)
