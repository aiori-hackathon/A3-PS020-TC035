#!/usr/bin/env python3
"""
PS-020: Local SRv6 Path Steering and Measured Failure Recovery
Stage 1: educational simulation prototype (not a real SRv6 dataplane).

Runs a deterministic, repeatable experiment comparing:
  1. a baseline IPv6-like route with no scripted alternate-path switch
  2. an explicit primary path with a scripted backup-path switch

All output is SIMULATED. Use the later Linux SRv6 testbed for real packet captures
and real performance measurements.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

# Five routers: R1 is ingress; R5 is egress.
PRIMARY_PATH = ["R1", "R2", "R3", "R5"]
BACKUP_PATH = ["R1", "R2", "R4", "R5"]
FAILURE_LINK = ("R2", "R3")


@dataclass
class TrialResult:
    mode: str
    trial: int
    sent_packets: int
    received_packets: int
    lost_packets: int
    packet_loss_percent: float
    interruption_ms: float
    detection_delay_ms: float
    repair_delay_ms: float
    estimated_srv6_overhead_bytes: int
    note: str


def simulate_trial(mode: str, trial: int, seed: int, packet_count: int) -> TrialResult:
    """
    Simplified event model. Delays are synthetic parameters, not measured facts.
    A controlled failure is injected on the R2-R3 primary link.
    """
    rng = random.Random(seed + trial * 1009 + (0 if mode == "ipv6-baseline" else 500_000))
    failure_at_ms = 500.0
    probe_interval_ms = 20.0
    scripted_switch_ms = rng.uniform(15.0, 45.0)
    detection_delay_ms = rng.uniform(20.0, 60.0)
    packet_interval_ms = 10.0

    lost = 0
    received = 0
    interrupted_packet_count = 0

    for packet_index in range(packet_count):
        packet_time_ms = packet_index * packet_interval_ms
        if packet_time_ms < failure_at_ms:
            received += 1
            continue

        if mode == "srv6-scripted":
            # Recovery occurs after detection plus scripted policy-switch time.
            recovery_at_ms = failure_at_ms + detection_delay_ms + scripted_switch_ms
            if packet_time_ms < recovery_at_ms:
                lost += 1
                interrupted_packet_count += 1
            else:
                received += 1
        else:
            # Baseline intentionally models no scripted repair during this trial.
            # This is a model assumption; actual routing may converge differently.
            lost += 1

    interruption_ms = (
        interrupted_packet_count * packet_interval_ms
        if mode == "srv6-scripted"
        else max(0.0, (packet_count - int(failure_at_ms / packet_interval_ms)) * packet_interval_ms)
    )
    loss_pct = (lost / packet_count * 100.0) if packet_count else 0.0
    repair_delay_ms = detection_delay_ms + scripted_switch_ms if mode == "srv6-scripted" else 0.0

    return TrialResult(
        mode=mode,
        trial=trial,
        sent_packets=packet_count,
        received_packets=received,
        lost_packets=lost,
        packet_loss_percent=round(loss_pct, 3),
        interruption_ms=round(interruption_ms, 3),
        detection_delay_ms=round(detection_delay_ms, 3),
        repair_delay_ms=round(repair_delay_ms, 3),
        # Example estimate only: SRH base fields + 1 SID (16 bytes each).
        # Actual overhead depends on configured SRH and number of SIDs.
        estimated_srv6_overhead_bytes=(8 + 16 * 3) if mode == "srv6-scripted" else 0,
        note="SIMULATED; replace with measurements from real testbed",
    )


def write_csv(results: list[TrialResult], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(results[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(item) for item in results)


def summarize(results: list[TrialResult]) -> dict[str, Any]:
    summary: dict[str, Any] = {"warning": "SIMULATED RESULTS — not real network measurements", "modes": {}}
    for mode in sorted({r.mode for r in results}):
        rows = [r for r in results if r.mode == mode]
        summary["modes"][mode] = {}
        for field in (
            "packet_loss_percent", "interruption_ms",
            "detection_delay_ms", "repair_delay_ms",
            "estimated_srv6_overhead_bytes",
        ):
            vals = [float(getattr(r, field)) for r in rows]
            summary["modes"][mode][field] = {
                "mean": round(statistics.mean(vals), 3),
                "min": round(min(vals), 3),
                "max": round(max(vals), 3),
            }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="PS-020 Stage 1 simulated experiment")
    parser.add_argument("--trials", type=int, default=10, help="number of repeated trials (default: 10)")
    parser.add_argument("--packets", type=int, default=120, help="packets per trial (default: 120)")
    parser.add_argument("--seed", type=int, default=2026, help="random seed for reproducibility")
    args = parser.parse_args()
    if args.trials < 1 or args.packets < 1:
        parser.error("--trials and --packets must both be >= 1")

    results: list[TrialResult] = []
    for trial in range(1, args.trials + 1):
        for mode in ("ipv6-baseline", "srv6-scripted"):
            results.append(simulate_trial(mode, trial, args.seed, args.packets))

    csv_path = RESULTS / "simulation_trials.csv"
    json_path = RESULTS / "simulation_summary.json"
    write_csv(results, csv_path)
    json_path.write_text(json.dumps(summarize(results), indent=2), encoding="utf-8")

    print("PS-020 Stage 1 experiment complete.")
    print("IMPORTANT: These are simulated values, not real SRv6 measurements.")
    print(f"Trials per mode: {args.trials}; packets per trial: {args.packets}")
    print(f"CSV: {csv_path.relative_to(ROOT)}")
    print(f"Summary: {json_path.relative_to(ROOT)}")
    print("\nSummary:")
    print(json.dumps(summarize(results), indent=2))


if __name__ == "__main__":
    main()
