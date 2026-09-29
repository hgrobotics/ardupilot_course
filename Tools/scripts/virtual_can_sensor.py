#!/usr/bin/env python3
"""
virtual_can_sensor.py
Educational example: A Virtual CAN LiDAR / Rangefinder Transmitter for ArduPilot SITL.
Broadcasts realistic CAN frames containing distance, SNR, and temperature over UDP Multicast.

AP_FLAKE8_CLEAN
"""

import math
import socket
import struct
import sys
import time

# -----------------------------------------------------------------------------
# SITL Multicast CAN Network Constants
# -----------------------------------------------------------------------------
# In SITL, ArduPilot emulates CAN Bus 0 over UDP Multicast.
# These values match ArduPilot's C++ source code in:
# libraries/AP_HAL_SITL/CAN_Multicast.cpp
MCAST_ADDRESS = "239.65.82.0"  # Multicast IP group for SITL CAN Bus 0
MCAST_PORT = 57732             # UDP Port where SITL listens for CAN packets
MCAST_MAGIC = 0x2934           # 2-byte Magic header (SITL drops packets without this)

# -----------------------------------------------------------------------------
# CRC16-CCITT Lookup Table (Matching ArduPilot libraries/AP_Math/crc.cpp)
# -----------------------------------------------------------------------------
# ArduPilot uses CRC16-CCITT (polynomial 0x1021) to verify that UDP packets are not corrupted.
# Precomputing the 256-entry table makes CRC calculation instantaneous.
crc16tab = []
for i in range(256):
    curr = i << 8
    for _ in range(8):
        if (curr & 0x8000) != 0:
            curr = ((curr << 1) ^ 0x1021) & 0xFFFF
        else:
            curr = (curr << 1) & 0xFFFF
    crc16tab.append(curr)


def crc16_ccitt(data: bytes, crc: int = 0xFFFF) -> int:
    """Calculates the 16-bit CRC checksum across the byte string 'data'."""
    for b in data:
        # XOR next byte into top of CRC, then look up polynomial remainder in table
        crc = ((crc << 8) & 0xFFFF) ^ crc16tab[((crc >> 8) ^ b) & 0xFF]
    return crc


def make_mcast_can_packet(can_id: int, payload: bytes) -> bytes:
    """
    Wraps an 8-byte CAN frame into SITL's Multicast UDP wire format:
      [Magic (2B)] + [CRC16 (2B)] + [Flags (2B)] + [CAN_ID (4B)] + [Payload (8B)]
    Total size = 18 bytes.
    """
    flags = 0  # 0 = Classic CAN (up to 8 bytes), 1 = CAN-FD (up to 64 bytes)

    # In SITL's protocol, the CRC covers: Flags (2 bytes) + CAN ID (4 bytes) + Payload bytes
    # '<HI' means: '<' = Little-Endian, 'H' = 2-byte unsigned short, 'I' = 4-byte unsigned int
    crc_body = struct.pack('<HI', flags, can_id) + payload

    # Calculate the 16-bit CRC of the body
    crc = crc16_ccitt(crc_body, 0xFFFF)

    # Reassemble the final 18-byte packet to send over the network:
    # '<HHHI' packs: Magic (2B), CRC (2B), Flags (2B), CAN ID (4B)
    return struct.pack('<HHHI', MCAST_MAGIC, crc, flags, can_id) + payload


def main():
    # -------------------------------------------------------------------------
    # Network Socket Setup
    # -------------------------------------------------------------------------
    # Create a standard UDP/IP socket:
    #   AF_INET     = IPv4
    #   SOCK_DGRAM  = UDP (User Datagram Protocol)
    #   IPPROTO_UDP = UDP protocol
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Set Multicast Time-to-Live (TTL): 2 allows packets to reach the local machine
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    # Enable Multicast Loopback: Allows SITL running on the same computer to receive our packets
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

    # -------------------------------------------------------------------------
    # Banner / Explanatory Header
    # -------------------------------------------------------------------------
    print("==========================================================================================")
    print("                      Virtual CAN LiDAR / Rangefinder Simulator                          ")
    print("==========================================================================================")
    print(f"Target Transport : UDP Multicast {MCAST_ADDRESS}:{MCAST_PORT}")
    print("Broadcast Rate   : 20 Hz (every 50 ms)")
    print("CAN Frame Format : 11-bit Standard ID: 0x600, DLC: 8 Bytes")
    print("Payload Layout   : [B0: Dist_MSB | B1: Dist_LSB | B2: SNR% | B3: Temp_C | B4..B7: Reserved]")
    print("==========================================================================================\n")

    t = 0.0          # Time variable in seconds (used for the sine wave)
    CAN_ID = 0x600   # 1536 in decimal: Standard CAN ID of our virtual sensor

    try:
        # Infinite transmission loop: runs until user presses Ctrl+C
        while True:
            # -----------------------------------------------------------------
            # Step 1: Simulate Physics (Altitude Oscillating 2.0m to 12.0m)
            # -----------------------------------------------------------------
            # 7.0m center + 5.0m * sin(t) moves smoothly between 2.0m and 12.0m
            alt_m = 7.0 + 5.0 * math.sin(t * 0.5)

            # Convert meters to centimeters (e.g. 7.50m -> 750cm)
            dist_cm = max(20, min(5000, int(alt_m * 100)))

            # Simulated sensor health telemetry:
            snr = 95        # 95% Signal Quality (confidence)
            temp_c = 32     # Sensor temperature: 32 degrees Celsius

            # -----------------------------------------------------------------
            # Step 2: Pack the 8-Byte Binary Payload
            # -----------------------------------------------------------------
            # '>HBB4s' format string breakdown:
            #   '>'  : Big-Endian (Network byte order: MSB byte comes first)
            #   'H'  : 2-byte unsigned short for distance (Byte 0: MSB, Byte 1: LSB)
            #   'B'  : 1-byte unsigned char for SNR (Byte 2: 0-100%)
            #   'B'  : 1-byte unsigned char for Temperature (Byte 3: 32 C)
            #   '4s' : 4 bytes of raw zeros for padding/reserved fields (Bytes 4-7)
            payload = struct.pack('>HBB4s', dist_cm, snr, temp_c, b'\x00\x00\x00\x00')

            # -----------------------------------------------------------------
            # Step 3: Wrap into SITL UDP Packet and Send
            # -----------------------------------------------------------------
            pkt = make_mcast_can_packet(CAN_ID, payload)
            sock.sendto(pkt, (MCAST_ADDRESS, MCAST_PORT))

            # -----------------------------------------------------------------
            # Step 4: Display Raw Byte Breakdown in Terminal
            # -----------------------------------------------------------------
            # Format each byte in 2-digit uppercase Hexadecimal (e.g. "02 BC 5F 20 00 00 00 00")
            hex_bytes = " ".join(f"{b:02X}" for b in payload)

            # Print to the terminal on a single refreshing line ('\r' carriage return)
            status_line = (
                f"\r[CAN TX 0x{CAN_ID:03X}] Dist: {dist_cm/100.0:5.2f}m ({dist_cm:4d}cm) | "
                f"Raw (8B): [{hex_bytes}] | "
                f"B0..1=0x{payload[0]:02X}{payload[1]:02X} ({dist_cm}cm), B2=0x{payload[2]:02X} ({snr}%), "
                f"B3=0x{payload[3]:02X} ({temp_c}°C)"
            )
            sys.stdout.write(status_line)
            sys.stdout.flush()

            # Advance time by 0.05 seconds (50 ms)
            t += 0.05

            # Pause for 50 milliseconds to achieve 20 Hz transmission rate
            time.sleep(0.05)

    except KeyboardInterrupt:
        # Triggered cleanly when the user presses Ctrl+C in the terminal
        print("\n\nStopped Virtual CAN LiDAR.")


if __name__ == "__main__":
    main()
