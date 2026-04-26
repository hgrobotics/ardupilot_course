# Lab L2 — First Flight: STABILIZE to LAND

## Purpose

Students execute the canonical "first flight" sequence in MAVProxy: arm in STABILIZE mode, climb to above 10 m, switch to LAND, and confirm the vehicle disarms autonomously. This is the practical completion of Module 1.3 ("Your first flight: arm, take off, land, disarm").

## Module reference

Day 1 Module 1.3 — Your first flight: arm, take off, land, disarm.

## Prerequisites

- Lab L1 completed (SITL launches successfully and shows `online system 1`).
- MAVProxy command terminal open and connected.
- No hardware required.

## Estimated duration

20 minutes (5 min setup + 10 min flight + 5 min observation).

The full Module 1.3 is 45 minutes because it includes the lecture component and reading the source citations. This lab is the hands-on portion.

## Success criteria

1. `arm throttle` command is accepted without rejection (vehicle arms).
2. `rc 3 1700` causes the vehicle to climb above 10 m altitude (visible in console).
3. After `mode LAND` is issued, the vehicle descends and the `Disarming motors` STATUSTEXT appears.
4. `Disarming motors` STATUSTEXT appears within 90 seconds of the initial `arm throttle` command.
5. Final mode is `LAND` and final armed state is `DISARMED`.

lab-tester pass condition: `Disarming motors` statustext received within 90 seconds of `arm throttle`.
