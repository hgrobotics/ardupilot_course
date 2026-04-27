/*
 * mock_storage.cpp — no-op AP_Param storage backend.
 *
 * AP_Param requires a storage backend for save/load. This stub satisfies
 * the linker without actually persisting anything.  In the test context
 * parameters are initialised to their in-code defaults and never saved.
 *
 * Do not modify unless you hit a linker error for a storage symbol.
 */

// TODO: post-extraction, add AP_Param storage stubs here.
//
// AP_Param/AP_Param.h is intentionally NOT included in this standalone cmake
// context: it transitively pulls in AP_HAL_Boards.h which requires
// CONFIG_HAL_BOARD / CONFIG_HAL_BOARD_SUBTYPE / HAL_PROGRAM_SIZE_LIMIT_KB
// defines that are absent outside the ArduPilot Waf build.
//
// For the capstone exercise, wire up storage stubs in this file once you have
// extracted the target source and identified which AP_Param storage symbols
// your translation unit actually needs.  In practice AP_L1_Control only calls
// setup_object_defaults() and never calls storage_read/storage_write, so this
// file can remain a stub for the initial extraction.
//
// Example stub (add if the linker complains):
//   void AP_Param::setup_object_defaults(const void*, const struct AP_Param::GroupInfo*) {}
//   bool AP_Param::save(bool) { return true; }
