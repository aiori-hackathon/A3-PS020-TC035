# AIORI-3 SRv6 Recovery Measurement

## Test environment

Real Linux IPv6 network namespaces using SRv6 segment routing.

Primary path: HOST1 → R1 → R2 → R4 → R5

Backup path: HOST1 → R1 → R3 → R4 → R5

## Continuous traffic results

- Packets transmitted: 360
- Packets received: 359
- Packet loss: 0.2778%
- Missing reply sequences: [84]
- Minimum RTT: 0.077 ms
- Mean RTT: 82.991 ms
- Median RTT: 0.138 ms
- Maximum RTT: 2032.0 ms

## Controller results

- Failover configuration: 15.009 ms
- Failback configuration: 35.698 ms
- Failure trigger to controller event log: 81.991 ms
- Restore trigger to controller event log: 95.601 ms

## Interpretation

The controller successfully changed the SRv6 forwarding
policy from the primary path to the backup path and back.

The continuous traffic test received 359 of 360
ICMPv6 replies.

Configuration execution times are distinct from
end-to-end recovery times. This test does not establish
a precise traffic-outage duration because ICMP replies
can be delayed, and ping timestamps represent received
replies rather than independently timestamped probe sends.

## Evidence

- `continuous_ping.txt`
- `failover_events.csv`
- `failure_trigger.txt`
- `restore_trigger.txt`
- `measurement_controller.log`
- `recovery_analysis.json`
