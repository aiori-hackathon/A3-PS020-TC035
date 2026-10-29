#!/usr/bin/env python3

import csv
import json
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "linux-srv6"

PING_FILE = RESULTS / "continuous_ping.txt"
EVENT_FILE = RESULTS / "failover_events.csv"
FAILURE_FILE = RESULTS / "failure_trigger.txt"
RESTORE_FILE = RESULTS / "restore_trigger.txt"

reply_pattern = re.compile(
    r"\[(\d+(?:\.\d+)?)\].*?"
    r"icmp_seq=(\d+).*?"
    r"time=([\d.]+)\s*ms"
)

sent_pattern = re.compile(
    r"(\d+) packets transmitted,\s*(\d+) received"
)

replies = []
sent = None
received = None

for line in PING_FILE.read_text().splitlines():
    match = reply_pattern.search(line)

    if match:
        replies.append({
            "timestamp": float(match.group(1)),
            "sequence": int(match.group(2)),
            "rtt_ms": float(match.group(3)),
        })

    match = sent_pattern.search(line)
    if match:
        sent = int(match.group(1))
        received = int(match.group(2))


def read_trigger(path):
    text = path.read_text().strip()
    value = text.split("=", 1)[1]
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    ).timestamp()


failure_time = read_trigger(FAILURE_FILE)
restore_time = read_trigger(RESTORE_FILE)

with EVENT_FILE.open(newline="") as file:
    events = list(csv.DictReader(file))

events_by_name = {
    event["event"]: event
    for event in events
    if event.get("status") == "SUCCESS"
}

sequences = {r["sequence"] for r in replies}

missing = (
    [seq for seq in range(1, sent + 1)
     if seq not in sequences]
    if sent is not None else []
)

rtts = [r["rtt_ms"] for r in replies]

def nearby_replies(trigger):
    before = [
        r for r in replies
        if r["timestamp"] < trigger
    ]
    after = [
        r for r in replies
        if r["timestamp"] >= trigger
    ]

    return {
        "last_reply_before": before[-1] if before else None,
        "first_reply_after": after[0] if after else None,
    }


def event_delay_ms(event_name, trigger):
    event = events_by_name.get(event_name)

    if not event:
        return None

    timestamp = datetime.fromisoformat(
        event["timestamp_utc"]
    ).timestamp()

    return round((timestamp - trigger) * 1000, 3)


analysis = {
    "test_type": "Real Linux SRv6 continuous ICMPv6 test",
    "probe_interval_requested_ms": 50,
    "packets_transmitted": sent,
    "packets_received": received,
    "packet_loss_percent": (
        round((sent - received) / sent * 100, 4)
        if sent else None
    ),
    "missing_reply_sequences": missing,
    "rtt_ms": {
        "minimum": min(rtts) if rtts else None,
        "mean": round(statistics.mean(rtts), 3)
        if rtts else None,
        "median": round(statistics.median(rtts), 3)
        if rtts else None,
        "maximum": max(rtts) if rtts else None,
    },
    "failure_trigger_utc": datetime.fromtimestamp(
        failure_time, timezone.utc
    ).isoformat(),
    "restore_trigger_utc": datetime.fromtimestamp(
        restore_time, timezone.utc
    ).isoformat(),
    "failover": {
        "controller_configuration_ms": (
            float(events_by_name["FAILOVER"]["configuration_ms"])
            if "FAILOVER" in events_by_name else None
        ),
        "trigger_to_event_log_ms": event_delay_ms(
            "FAILOVER", failure_time
        ),
        "adjacent_replies": nearby_replies(failure_time),
    },
    "failback": {
        "controller_configuration_ms": (
            float(events_by_name["FAILBACK"]["configuration_ms"])
            if "FAILBACK" in events_by_name else None
        ),
        "trigger_to_event_log_ms": event_delay_ms(
            "FAILBACK", restore_time
        ),
        "adjacent_replies": nearby_replies(restore_time),
    },
    "measurement_notes": [
        "Controller configuration time is not end-to-end recovery time.",
        "Trigger-to-event-log delay includes polling, configuration, and logging.",
        "ICMP reply timestamps and RTTs do not directly measure outage duration.",
        "One missing reply does not imply only 50 ms of disruption.",
        "High RTT values may reflect delayed replies during route transitions.",
    ],
}

json_path = RESULTS / "recovery_analysis.json"
json_path.write_text(
    json.dumps(analysis, indent=2) + "\n"
)

report = f"""# AIORI-3 SRv6 Recovery Measurement

## Test environment

Real Linux IPv6 network namespaces using SRv6 segment routing.

Primary path: HOST1 → R1 → R2 → R4 → R5

Backup path: HOST1 → R1 → R3 → R4 → R5

## Continuous traffic results

- Packets transmitted: {sent}
- Packets received: {received}
- Packet loss: {analysis['packet_loss_percent']}%
- Missing reply sequences: {missing}
- Minimum RTT: {analysis['rtt_ms']['minimum']} ms
- Mean RTT: {analysis['rtt_ms']['mean']} ms
- Median RTT: {analysis['rtt_ms']['median']} ms
- Maximum RTT: {analysis['rtt_ms']['maximum']} ms

## Controller results

- Failover configuration: {analysis['failover']['controller_configuration_ms']} ms
- Failback configuration: {analysis['failback']['controller_configuration_ms']} ms
- Failure trigger to controller event log: {analysis['failover']['trigger_to_event_log_ms']} ms
- Restore trigger to controller event log: {analysis['failback']['trigger_to_event_log_ms']} ms

## Interpretation

The controller successfully changed the SRv6 forwarding
policy from the primary path to the backup path and back.

The continuous traffic test received {received} of {sent}
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
"""

report_path = RESULTS / "recovery_report.md"
report_path.write_text(report)

print("=" * 45)
print(" AIORI-3 RECOVERY ANALYSIS")
print("=" * 45)
print(f"Packets: {received}/{sent}")
print(f"Loss: {analysis['packet_loss_percent']}%")
print(f"Missing sequences: {missing}")
print(f"Mean RTT: {analysis['rtt_ms']['mean']} ms")
print(f"Median RTT: {analysis['rtt_ms']['median']} ms")
print(f"Max RTT: {analysis['rtt_ms']['maximum']} ms")
print()
print("Failover:")
print(json.dumps(analysis["failover"], indent=2))
print()
print("Failback:")
print(json.dumps(analysis["failback"], indent=2))
print()
print("Saved:")
print(json_path)
print(report_path)
