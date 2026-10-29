# Real Linux SRv6 Lab — AIORI-3 PS-020

Team: A3-PS020-TC035
Project: Local SRv6 Path Steering and Measured Failure Recovery

## Network paths
Primary: HOST1 -> R1 -> R2 -> R4 -> R5
Backup: HOST1 -> R1 -> R3 -> R4 -> R5
Destination: 2001:db8:ffff::5

## Requirements
Linux SRv6 support, iproute2, Python 3, root privileges.

## Setup
WARNING: The setup script deletes and recreates the six lab namespaces.
Run only on a dedicated Linux test VM.

    sudo bash linux-lab/setup_topology.sh

The setup script passed syntax checking but has not yet been tested from a fresh rebuild.

## Automatic controller
    sudo python3 -u linux-lab/failover_controller.py

## Analyze recorded measurements
    python3 linux-lab/analyze_recovery.py

## Verified experiment results
- 359 of 360 ICMPv6 replies received
- Packet loss: 0.2778%
- Failover configuration: 15.009 ms
- Failback configuration: 35.698 ms
- Median RTT: 0.138 ms

Configuration times are not end-to-end recovery times.
The Python simulation is separate from the real Linux SRv6 experiment.
