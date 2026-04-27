/*
 * mock_storage.cpp — no-op AP_Param storage backend.
 *
 * AP_Param/AP_Param.h is intentionally NOT included in this standalone cmake
 * context: it transitively pulls in AP_HAL_Boards.h which requires
 * CONFIG_HAL_BOARD / CONFIG_HAL_BOARD_SUBTYPE / HAL_PROGRAM_SIZE_LIMIT_KB
 * defines that are absent outside the ArduPilot Waf build.
 *
 * TODO: post-extraction, add AP_Param storage stubs here once you have
 * identified which storage symbols AP_TECS actually requires.  In practice
 * AP_TECS only calls setup_object_defaults() and never calls
 * storage_read/storage_write, so this file can remain a stub for the initial
 * extraction.
 *
 * Example stub (add if the linker complains):
 *   void AP_Param::setup_object_defaults(const void*, const struct AP_Param::GroupInfo*) {}
 *   bool AP_Param::save(bool) { return true; }
 */
