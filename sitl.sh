#!/usr/bin/env bash
# Build and launch ArduPlane SITL, wired for QGroundControl.
#
# SITL talks to QGC directly over UDP 14550 (QGC's auto-connect port) and keeps
# TCP 5760 free for MAVProxy or any other tool. Ctrl-C stops it.
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DIR="$ROOT/sitl-run"
LOCATIONS="$ROOT/Tools/autotest/locations.txt"
BIN="$ROOT/build/sitl/bin/arduplane"

# waf deadlocks under python 3.12; 3.10 is the known-good interpreter here.
WAF_PY="${WAF_PYTHON:-python3.10}"

FRAME=quadplane
LOC=CMAC
LAT=; LON=; ALT=; YAW=
SPEEDUP=1
INSTANCE=0
QGC_PORT=14550
REBUILD=0; NO_BUILD=0; WIPE=0; DRY_RUN=0

log() { printf '[sitl] %s\n' "$*" >&2; }
die() { printf '[sitl] error: %s\n' "$*" >&2; exit 1; }

usage() {
  cat <<'EOF'
./sitl.sh [options]      launch ArduPlane SITL for QGroundControl

  --frame F        quadplane (default) | plane
  --loc NAME       home from Tools/autotest/locations.txt (default CMAC)
  --lat/--lon      explicit home; overrides --loc
  --alt/--yaw      absolute altitude (m) and heading (deg), default 0
  --speedup N      simulation speed multiplier (default 1)
  --instance N     shifts every port by 10*N (default 0)
  --qgc-port N     UDP port QGC listens on (default 14550)
  --wipe           reset the simulated EEPROM to the default parameters
  --rebuild        reconfigure and rebuild before launching
  --no-build       fail instead of building a missing binary
  --dry-run        print the SITL command and exit
  -h, --help

Start QGroundControl and it will find the vehicle on its own.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --frame)     FRAME="$2"; shift 2 ;;
    --loc)       LOC="$2"; shift 2 ;;
    --lat)       LAT="$2"; shift 2 ;;
    --lon)       LON="$2"; shift 2 ;;
    --alt)       ALT="$2"; shift 2 ;;
    --yaw)       YAW="$2"; shift 2 ;;
    --speedup)   SPEEDUP="$2"; shift 2 ;;
    --instance)  INSTANCE="$2"; shift 2 ;;
    --qgc-port)  QGC_PORT="$2"; shift 2 ;;
    --wipe)      WIPE=1; shift ;;
    --rebuild)   REBUILD=1; shift ;;
    --no-build)  NO_BUILD=1; shift ;;
    --dry-run)   DRY_RUN=1; shift ;;
    -h|--help)   usage; exit 0 ;;
    *)           usage >&2; die "unknown option: $1" ;;
  esac
done

case "$FRAME" in
  quadplane) MODEL=quadplane; FRAME_PARM="$ROOT/Tools/autotest/default_params/quadplane.parm" ;;
  plane)     MODEL=plane;     FRAME_PARM="$ROOT/Tools/autotest/models/plane.parm" ;;
  *)         die "unknown frame: $FRAME (expected quadplane or plane)" ;;
esac

if [[ -n "$LAT" && -n "$LON" ]]; then
  ALT="${ALT:-0}"; YAW="${YAW:-0}"; LOC="explicit"
else
  [[ -f "$LOCATIONS" ]] || die "locations file not found: $LOCATIONS"
  home="$(awk -F= -v n="$LOC" '$1==n {print $2; exit}' "$LOCATIONS")"
  [[ -n "$home" ]] || die "unknown location '$LOC' (names are listed in $LOCATIONS)"
  IFS=, read -r LAT LON ALT YAW <<<"$home"
fi

if [[ $REBUILD -eq 1 || ! -x "$BIN" ]]; then
  [[ $NO_BUILD -eq 1 ]] && die "no binary at $BIN and --no-build was given"
  command -v "$WAF_PY" >/dev/null || die "$WAF_PY not on PATH (override with WAF_PYTHON=...)"

  # boards.py sets with_can=True for the sitl board, so DroneCAN codegen runs
  # even for a SITL build. A shallow clone leaves these empty and waf dies in
  # dronecangen with an error that looks like a linker problem.
  missing=()
  for m in DSDL dronecan_dsdlc libcanard pydronecan; do
    [[ -n "$(ls -A "$ROOT/modules/DroneCAN/$m" 2>/dev/null)" ]] || missing+=("modules/DroneCAN/$m")
  done
  (( ${#missing[@]} )) && die "empty submodules. run:
  git submodule update --init ${missing[*]}"

  log "building arduplane with $WAF_PY"

  # Never pipe waf: a piped exit status belongs to the pipe, so a failed build
  # would report success.
  if [[ $REBUILD -eq 1 || ! -f "$ROOT/build/c4che/sitl_cache.py" ]]; then
    ( cd "$ROOT" && "$WAF_PY" ./waf configure --board sitl )
    rc=$?; (( rc == 0 )) || die "waf configure failed (rc=$rc)"
  fi
  ( cd "$ROOT" && "$WAF_PY" ./waf plane )
  rc=$?; (( rc == 0 )) || die "waf plane failed (rc=$rc)"
fi

BASE_PORT=$((5760 + 10 * INSTANCE))

# serial0 defaults to "tcp:0:wait" (AP_HAL_SITL/SITL_State.h), which blocks the
# whole boot until a GCS opens the TCP port. Dropping ":wait" lets SITL run and
# stream to QGC immediately, whether or not anything ever attaches to TCP.
cmd=( "$BIN"
      "--model=$MODEL"
      "--home=$LAT,$LON,$ALT,$YAW"
      "--speedup=$SPEEDUP"
      "--instance=$INSTANCE"
      "--defaults=$FRAME_PARM,$ROOT/config/sitl-extra.parm"
      "--serial0=tcp:0"
      "--serial1=udpclient:127.0.0.1:$QGC_PORT" )
(( WIPE )) && cmd+=( "--wipe" )

if (( DRY_RUN )); then printf '%s\n' "${cmd[*]}"; exit 0; fi

mkdir -p "$RUN_DIR"
log "frame    $FRAME (model=$MODEL)"
log "home     $LAT,$LON,$ALT,$YAW ($LOC)"
log "QGC      UDP 127.0.0.1:$QGC_PORT — start QGroundControl, it auto-connects"
log "tools    TCP 127.0.0.1:$BASE_PORT — mavproxy.py --master=tcp:127.0.0.1:$BASE_PORT"
log "run dir  $RUN_DIR — eeprom.bin, logs/, terrain/"

# SITL writes eeprom.bin, logs/ and terrain/ into its working directory.
cd "$RUN_DIR" || die "cannot enter $RUN_DIR"
exec "${cmd[@]}"
