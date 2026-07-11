#!/usr/bin/env python3
"""Report the terrain-database height AMSL at a lat/lon, reading the same
.DAT tiles ArduPilot's AP_Terrain reads.

./sitl.sh --terrain uses this to set the SITL home altitude to the ground
height the firmware believes is there. Getting that wrong is not cosmetic:
SITL anchors the simulated ground plane at the home altitude you pass on the
command line (SIM_Aircraft.cpp, ground_height_difference()), while the
simulated rangefinder measures against the absolute terrain database
(AP_HAL_SITL/SITL_State.cpp, set_height_agl()). A mismatch shows up as a
constant rangefinder bias of (home_alt - terrain_amsl) with the vehicle
sitting still on the ground.

Exit status: 0 and the height on stdout, or 1 with a reason on stderr. A
missing tile is a normal outcome, not a crash -- the caller decides.

The grid maths mirrors AP_Terrain::calculate_grid_info() and
AP_Terrain::height_amsl(); the constants come from AP_Terrain.h.
"""

import argparse
import math
import struct
import sys

GRID_MAVLINK_SIZE = 4
BLOCK_MUL_X, BLOCK_MUL_Y = 7, 8
BLOCK_SPACING_X = (BLOCK_MUL_X - 1) * GRID_MAVLINK_SIZE  # 24
BLOCK_SPACING_Y = (BLOCK_MUL_Y - 1) * GRID_MAVLINK_SIZE  # 28
BLOCK_SIZE_X = GRID_MAVLINK_SIZE * BLOCK_MUL_X           # 28
BLOCK_SIZE_Y = GRID_MAVLINK_SIZE * BLOCK_MUL_Y           # 32
GRID_FORMAT_VERSION = 1
IO_BLOCK_BYTES = 2048

LATLON_TO_M = 0.011131884502145034  # AP_Math/definitions.h

# PACKED struct grid_block, AP_Terrain.h
_HEAD = struct.Struct("<Qii HHH")                       # bitmap, lat, lon, crc, version, spacing
_HEIGHTS = struct.Struct("<%dh" % (BLOCK_SIZE_X * BLOCK_SIZE_Y))
_TAIL = struct.Struct("<HH hb")                         # grid_idx_x, grid_idx_y, lon_degrees, lat_degrees
_TAIL_OFF = _HEAD.size + _HEIGHTS.size


def c_div(a, b):
    """Integer division that truncates toward zero, as C does.

    Not interchangeable with Python's //, which floors. AP_Terrain subtracts
    9999999 from negative coordinates precisely to compensate for C's
    truncation; letting // floor as well applies the correction twice and
    lands a degree south/west of the right tile.
    """
    q = abs(a) // abs(b)
    return -q if (a < 0) != (b < 0) else q


def longitude_scale(lat_e7):
    return max(math.cos(lat_e7 * 1.0e-7 * math.pi / 180.0), 0.01)


def grid_info(lat_e7, lon_e7, spacing):
    """Port of AP_Terrain::calculate_grid_info()."""
    lat_degrees = c_div(lat_e7 - 9999999 if lat_e7 < 0 else lat_e7, 10000000)
    lon_degrees = c_div(lon_e7 - 9999999 if lon_e7 < 0 else lon_e7, 10000000)

    ref_lat, ref_lon = lat_degrees * 10000000, lon_degrees * 10000000

    # ref.get_distance_NE(loc), Location.cpp
    off_x = (lat_e7 - ref_lat) * LATLON_TO_M
    off_y = (lon_e7 - ref_lon) * LATLON_TO_M * longitude_scale(c_div(lat_e7 + ref_lat, 2))

    idx_x = int(off_x / spacing)
    idx_y = int(off_y / spacing)

    return {
        "lat_degrees": lat_degrees,
        "lon_degrees": lon_degrees,
        "grid_idx_x": idx_x // BLOCK_SPACING_X,
        "grid_idx_y": idx_y // BLOCK_SPACING_Y,
        "idx_x": idx_x % BLOCK_SPACING_X,
        "idx_y": idx_y % BLOCK_SPACING_Y,
        "frac_x": (off_x - idx_x * spacing) / spacing,
        "frac_y": (off_y - idx_y * spacing) / spacing,
    }


def have_grid(bitmap, idx_x, idx_y):
    """Port of AP_Terrain::check_bitmap() -- a tile can be partially filled."""
    bitnum = (idx_y // GRID_MAVLINK_SIZE) + BLOCK_MUL_Y * (idx_x // GRID_MAVLINK_SIZE)
    return (bitmap >> bitnum) & 1 == 1


def find_block(path, info, spacing):
    with open(path, "rb") as f:
        while True:
            buf = f.read(IO_BLOCK_BYTES)
            if len(buf) < IO_BLOCK_BYTES:
                return None
            bitmap, _, _, _, version, blk_spacing = _HEAD.unpack_from(buf, 0)
            if version != GRID_FORMAT_VERSION or blk_spacing != spacing:
                continue  # empty (sparse hole) or a different grid spacing
            gx, gy, _, _ = _TAIL.unpack_from(buf, _TAIL_OFF)
            if gx == info["grid_idx_x"] and gy == info["grid_idx_y"]:
                return bitmap, _HEIGHTS.unpack_from(buf, _HEAD.size)


def height_amsl(terrain_dir, lat, lon, spacing):
    """Port of AP_Terrain::height_amsl(). Returns metres, or raises LookupError."""
    lat_e7, lon_e7 = int(round(lat * 1e7)), int(round(lon * 1e7))
    info = grid_info(lat_e7, lon_e7, spacing)

    name = "%c%02u%c%03u.DAT" % (
        "S" if info["lat_degrees"] < 0 else "N", min(abs(info["lat_degrees"]), 99),
        "W" if info["lon_degrees"] < 0 else "E", min(abs(info["lon_degrees"]), 999),
    )
    path = "%s/%s" % (terrain_dir, name)

    try:
        found = find_block(path, info, spacing)
    except FileNotFoundError:
        raise LookupError("no tile %s in %s" % (name, terrain_dir))
    if found is None:
        raise LookupError("%s holds no block covering %.6f,%.6f" % (name, lat, lon))

    bitmap, heights = found
    x, y = info["idx_x"], info["idx_y"]

    # All four surrounding grid points must be present, exactly as height_amsl() demands.
    for cx, cy in ((x, y), (x, y + 1), (x + 1, y), (x + 1, y + 1)):
        if not have_grid(bitmap, cx, cy):
            raise LookupError("tile %s is only partially downloaded around %.6f,%.6f" % (name, lat, lon))

    def h(cx, cy):
        return heights[cx * BLOCK_SIZE_Y + cy]

    fx, fy = info["frac_x"], info["frac_y"]
    avg1 = (1.0 - fx) * h(x, y) + fx * h(x + 1, y)
    avg2 = (1.0 - fx) * h(x, y + 1) + fx * h(x + 1, y + 1)
    return (1.0 - fy) * avg1 + fy * avg2


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lat", type=float)
    ap.add_argument("lon", type=float)
    ap.add_argument("--terrain-dir", default="sitl-run/terrain")
    ap.add_argument("--spacing", type=int, default=100, help="must match TERRAIN_SPACING (default 100)")
    args = ap.parse_args()

    try:
        print("%.1f" % height_amsl(args.terrain_dir, args.lat, args.lon, args.spacing))
    except LookupError as e:
        sys.stderr.write("%s\n" % e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
