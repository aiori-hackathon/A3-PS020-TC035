# Results template

Fill this from your own terminal output and packet captures. Leave a value blank until measured.

| Trial | Routing mode | Failure link | Packets sent | Packets received | Loss (%) | Interruption (ms) | Detection delay (ms) | Repair delay (ms) | SRH/header overhead (bytes) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | Ordinary IPv6 baseline | SR2–SR3 | | | | | | | N/A |
| 1 | SRv6 primary + scripted backup | SR2–SR3 | | | | | | | |
| 2 | SRv6 primary + scripted backup | SR2–SR3 | | | | | | | |
| 3 | SRv6 primary + scripted backup | SR2–SR3 | | | | | | | |

## Measurement notes

- Record exact command, kernel version, iproute2 version, ping interval, and trial duration.
- Define interruption consistently (e.g., time from last successful reply before failure to first successful reply after backup switch).
- Failure detection delay for this prototype is the script's detection/decision latency; because the script is operator-triggered, describe it as scripted detection/trigger delay rather than automatic network detection.
- Measure overhead from packet captures and state the exact layers included. SRH size depends on the number of segments and TLVs.
- Repeat trials and report mean/range; do not infer measurements from a single ping run.
