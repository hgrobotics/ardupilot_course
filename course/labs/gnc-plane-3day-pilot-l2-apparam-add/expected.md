# Lab L2 — Expected Outputs (Verdict Spec)

## Verdict signatures

lab-tester checks all of the following. A PASS requires all signatures to match.

### Signature 1 — MY_PARAM visible at default 17.0

After SITL starts with the patched binary, a MAVLink `PARAM_VALUE` message for
`MY_PARAM` must be received with `param_value` in the range `[16.9, 17.1]`.

Exit code `2` if `MY_PARAM` is not found in the parameter list (patch not
applied or binary not rebuilt).

### Signature 2 — MY_PARAM set to 42.0 acknowledged

After sending `PARAM_SET(MY_PARAM=42.0)`, the vehicle must respond with a
`PARAM_VALUE` message where `param_value` is in `[41.9, 42.1]`.

Exit code `3` if set acknowledgement not received within 10 s.

### Signature 3 — MY_PARAM persists to 42.0 after restart

After SITL is stopped and restarted (same EEPROM directory), the first
`PARAM_VALUE` for `MY_PARAM` on the new connection must be in `[41.9, 42.1]`.

Exit code `4` if MY_PARAM reverts to 17.0 after restart (EEPROM not written or
cleared between runs).

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | All signatures pass |
| 1    | SITL failed to start |
| 2    | MY_PARAM not found (patch not applied / binary not rebuilt) |
| 3    | SET acknowledgement not received |
| 4    | MY_PARAM did not persist after restart |
