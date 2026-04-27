cmake_minimum_required(VERSION 3.16)
project(L1ControlTest CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ---- Paths ----------------------------------------------------------------
# Adjust ARDUPILOT_ROOT if your build is in a different location.
set(ARDUPILOT_ROOT "${CMAKE_SOURCE_DIR}/../../../.." CACHE PATH
    "Root of the ArduPilot repository")
get_filename_component(ARDUPILOT_ROOT "${ARDUPILOT_ROOT}" ABSOLUTE)

set(GTEST_ROOT "${ARDUPILOT_ROOT}/modules/gtest/googletest")

# ---- gtest ----------------------------------------------------------------
add_library(gtest STATIC
    "${GTEST_ROOT}/src/gtest-all.cc"
)
target_include_directories(gtest PUBLIC
    "${GTEST_ROOT}/include"
    "${GTEST_ROOT}"
)
# Workaround for GCC >= 15 / glibc >= 2.43: force time.h before pthread.h.
# Harmless on older toolchains.
target_compile_options(gtest PRIVATE -w -include /usr/include/time.h)

add_library(gtest_main STATIC
    "${GTEST_ROOT}/src/gtest_main.cc"
)
target_include_directories(gtest_main PUBLIC
    "${GTEST_ROOT}/include"
)
target_compile_options(gtest_main PRIVATE -w -include /usr/include/time.h)
target_link_libraries(gtest_main gtest)

# ---- Mock / stub sources --------------------------------------------------
set(MOCK_SOURCES
    mock_hal.cpp
    mock_storage.cpp
)

# ---- Engineer's extracted sources (ADD YOUR FILES HERE) -------------------
# Example:
#   set(EXTRACTED_SOURCES
#       AP_L1_Control/AP_L1_Control.cpp
#   )
# Leave empty until you copy the files in.
set(EXTRACTED_SOURCES
    # AP_L1_Control/AP_L1_Control.cpp   # <-- copy from libraries/ and uncomment
)

# ---- Include paths --------------------------------------------------------
# Note: AP_HAL is included for the AP_HAL:: namespace types used by AP_Param
# and AP_Math, but the mock_hal.cpp only provides the free functions millis()
# and micros(). You do NOT need to compile the full HAL.
include_directories(
    "${CMAKE_SOURCE_DIR}"
    "${ARDUPILOT_ROOT}/libraries"
    "${ARDUPILOT_ROOT}/libraries/AP_Math"
    "${ARDUPILOT_ROOT}/libraries/AP_Common"
    "${ARDUPILOT_ROOT}/libraries/AP_HAL"
    "${ARDUPILOT_ROOT}/libraries/AP_Param"
    "${ARDUPILOT_ROOT}/libraries/AP_Navigation"
    "${ARDUPILOT_ROOT}/libraries/AP_TECS"
    "${ARDUPILOT_ROOT}/libraries/AP_AHRS"
    "${ARDUPILOT_ROOT}/libraries/Filter"
)

# ---- Test executable ------------------------------------------------------
add_executable(l1_test
    test_l1_control.cpp
    ${MOCK_SOURCES}
    ${EXTRACTED_SOURCES}
)

target_compile_options(l1_test PRIVATE -w -include /usr/include/time.h)
target_link_libraries(l1_test gtest_main pthread)

# ---- CTest integration ----------------------------------------------------
enable_testing()
add_test(NAME L1ControlTests COMMAND l1_test)
