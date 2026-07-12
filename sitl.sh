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
EXTRA_PARM="$ROOT/config/sitl-extra.parm"
TERRAIN_PARM="$ROOT/config/sitl-terrain.parm"
TERRAIN_PY="$ROOT/sitl-terrain.py"

# waf deadlocks under python 3.12; 3.10 is the known-good interpreter here.
WAF_PY="${WAF_PYTHON:-python3.10}"

FRAME=quadplane
LOC=CMAC
LAT=; LON=; ALT=; YAW=
SPEEDUP=1
INSTANCE=0
QGC_PORT=14550
REBUILD=0; NO_BUILD=0; WIPE=0; DRY_RUN=0; TERRAIN=0; ALT_EXPLICIT=0

log() { printf '[sitl] %s\n' "$*" >&2; }
die() { printf '[sitl] error: %s\n' "$*" >&2; exit 1; }

# --defaults sets DEFAULTS, and a value already stored in the EEPROM beats a
# default: AP_Param only takes a default for a parameter it has never seen. So any
# eeprom.bin left by an earlier session -- or one stray write from QGC -- makes a
# line in config/*.parm a silent no-op. There is no command line option to force a
# value -- -P does not help and is a trap: SITL's _set_param_default() actually calls
# set_and_save(), so on a fresh eeprom it WRITES the value permanently, and on an
# existing one load_all() overwrites it afterwards. --wipe is the only lever, so say
# it out loud instead of pretending.
warn_eeprom_overrides() {
  [[ -f "$RUN_DIR/eeprom.bin" ]] && (( ! WIPE )) || return 0

  log "eeprom   NOTE: $RUN_DIR/eeprom.bin exists, and a parameter STORED in it beats"
  log "eeprom         the config/*.parm defaults. Only params something explicitly"
  log "eeprom         wrote are stored -- QGC, MAVProxy, -P -- so a plain run saves"
  log "eeprom         none of these and this is usually nothing. But if you have ever"
  log "eeprom         set one by hand, confirm it in QGC after boot, or just --wipe:"
  log "eeprom           RNGFND_LANDING 1 -- at 0 the TF03's correction never reaches"
  log "eeprom                              TECS and 'Rangefinder engaged' never arms,"
  log "eeprom                              so the landing flies on the biased baro."
  if (( TERRAIN )); then
    log "eeprom           TERRAIN_ENABLE 1 -- at 0 --terrain did nothing: home is"
    log "eeprom                              still anchored on the terrain, so the"
    log "eeprom                              launch looks right while height_agl"
    log "eeprom                              quietly stays flat-earth."
  fi
}

usage() {
  cat <<'EOF'
./sitl.sh [options]      launch ArduPlane SITL for QGroundControl

  --frame F        quadplane (default) | plane
  --loc NAME       home from Tools/autotest/locations.txt (default CMAC)
  --lat/--lon      explicit home; overrides --loc
  --alt/--yaw      absolute altitude (m) and heading (deg), default 0
  --terrain        read elevation from the terrain database, and take the home
                   altitude from it so the rangefinder reads 0 on the ground
  --speedup N      simulation speed multiplier (default 1)
  --instance N     shifts every port by 10*N (default 0)
  --qgc-port N     UDP port QGC listens on (default 14550)
  --wipe           reset the simulated EEPROM to the default parameters
  --rebuild        reconfigure and rebuild before launching
  --no-build       fail instead of building a missing binary
  --dry-run        print the SITL command and exit
  -h, --help

A downward Benewake TF03 lidar is always simulated (0.1-180 m, used for landing,
and quadplane VTOL height checks). Without --terrain it measures height above
HOME, not above ground.

Start QGroundControl and it will find the vehicle on its own.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --frame)     FRAME="$2"; shift 2 ;;
    --loc)       LOC="$2"; shift 2 ;;
    --lat)       LAT="$2"; shift 2 ;;
    --lon)       LON="$2"; shift 2 ;;
    --alt)       ALT="$2"; ALT_EXPLICIT=1; shift 2 ;;
    --yaw)       YAW="$2"; shift 2 ;;
    --terrain)   TERRAIN=1; shift ;;
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
  IFS=, read -r LAT LON loc_alt loc_yaw <<<"$home"
  # an explicit --alt/--yaw beats the locations file rather than being clobbered
  (( ALT_EXPLICIT )) || ALT="$loc_alt"
  [[ -n "$YAW" ]] || YAW="$loc_yaw"
fi

DEFAULTS="$FRAME_PARM,$EXTRA_PARM"

# SITL anchors the simulated ground plane at the home altitude passed below,
# but the simulated rangefinder measures against the absolute terrain database
# (set_height_agl(), AP_HAL_SITL/SITL_State.cpp). Disagree on the two and the
# rangefinder shows a constant (home alt - terrain alt) offset while the
# vehicle is parked, so default the home altitude to what the database says.
if (( TERRAIN )); then
  [[ -f "$TERRAIN_PARM" ]] || die "missing $TERRAIN_PARM"
  [[ -f "$TERRAIN_PY" ]]   || die "missing $TERRAIN_PY"
  command -v python3 >/dev/null || die "--terrain needs python3 to read the terrain tiles"
  DEFAULTS="$DEFAULTS,$TERRAIN_PARM"

  spacing="$(awk '$1=="TERRAIN_SPACING" {print $2; exit}' "$TERRAIN_PARM")"
  if terrain_alt="$(python3 "$TERRAIN_PY" "$LAT" "$LON" \
                      --terrain-dir "$RUN_DIR/terrain" --spacing "${spacing:-100}" 2>&1)"; then
    if (( ALT_EXPLICIT )); then
      bias="$(awk -v a="$ALT" -v t="$terrain_alt" 'BEGIN{printf "%.1f", a-t}')"
      log "terrain  ground at home is ${terrain_alt}m AMSL; keeping --alt ${ALT}m"
      if [[ "$(awk -v b="$bias" 'BEGIN{print (b>=1 || b<=-1) ? 1 : 0}')" == 1 ]]; then
        log "terrain  WARNING: parked on the ground the rangefinder will read ${bias}m,"
        log "terrain           not 0. Drop --alt to anchor home on the terrain."
      fi
    else
      log "terrain  home altitude ${ALT}m -> ${terrain_alt}m AMSL (from the terrain database)"
      ALT="$terrain_alt"
    fi
  else
    # A failed lookup is not fatal, and that is the danger: SITL silently falls
    # back to a flat-earth model rather than erroring, so say so loudly here.
    log "terrain  WARNING: $terrain_alt"
    log "terrain           No tile covers $LAT,$LON, so height_agl falls back to a flat"
    log "terrain           earth model: the rangefinder will report height above HOME"
    log "terrain           and never see a hill, with no error at any point."
    log "terrain           Attach QGroundControl and fly the area once -- it streams"
    log "terrain           tiles over MAVLink into $RUN_DIR/terrain -- then rerun."
  fi
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
      "--defaults=$DEFAULTS"
      "--serial0=tcp:0"
      "--serial1=udpclient:127.0.0.1:$QGC_PORT" )
(( WIPE )) && cmd+=( "--wipe" )

warn_eeprom_overrides

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
