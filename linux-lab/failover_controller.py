#!/usr/bin/env python3

import csv
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
LOG = PROJECT / "results" / "linux-srv6" / "live_failover_events.csv"

DEST = "2001:db8:ffff::5/128"
INTERVAL = 0.05


def command(*args):
    result = subprocess.run(
        args, capture_output=True, text=True
    )
    if result.returncode:
        raise RuntimeError(
            f"{' '.join(args)}: {result.stderr.strip()}"
        )
    return result.stdout


def link_is_up():
    result = subprocess.run(
        ["ip", "-n", "R1", "-o", "link", "show", "r1eth0"],
        capture_output=True, text=True
    )
    return (
        result.returncode == 0
        and "LOWER_UP" in result.stdout
    )


def configure_primary():
    # Restore addresses removed by the link-down operation.
    command("ip", "-n", "R1", "-6", "addr", "replace",
            "2001:db8:12::1/64", "dev", "r1eth0")

    command("ip", "-n", "R2", "-6", "addr", "replace",
            "2001:db8:12::2/64", "dev", "r2eth0")

    command("ip", "-n", "R1", "-6", "route", "replace",
            "2001:db8:100::2/128",
            "via", "2001:db8:12::2", "dev", "r1eth0")

    # Keep return traffic on the operational primary path.
    command("ip", "-n", "R4", "-6", "route", "replace",
            "2001:db8:1::/64",
            "via", "2001:db8:24::2", "dev", "r4r2")

    command("ip", "-n", "R1", "-6", "route", "replace",
            DEST, "encap", "seg6", "mode", "encap",
            "segs", "2001:db8:100::2,2001:db8:100::5",
            "via", "2001:db8:12::2", "dev", "r1eth0")


def configure_backup():
    # Ensure replies avoid the failed R1-R2 link.
    command("ip", "-n", "R4", "-6", "route", "replace",
            "2001:db8:1::/64",
            "via", "2001:db8:34::3", "dev", "r4r3")

    command("ip", "-n", "R1", "-6", "route", "replace",
            DEST, "encap", "seg6", "mode", "encap",
            "segs", "2001:db8:100::3,2001:db8:100::5",
            "via", "2001:db8:13::3", "dev", "r1r3")


def record(event, path, elapsed_ms, status):
    timestamp = datetime.now(timezone.utc).isoformat()

    with LOG.open("a", newline="") as file:
        csv.writer(file).writerow([
            timestamp, event, path,
            f"{elapsed_ms:.3f}", status
        ])

    print(
        f"{timestamp} | {event} | {path} | "
        f"{elapsed_ms:.3f} ms | {status}",
        flush=True
    )


def main():
    LOG.parent.mkdir(parents=True, exist_ok=True)

    with LOG.open("w", newline="") as file:
        csv.writer(file).writerow([
            "timestamp_utc",
            "event",
            "active_path",
            "configuration_ms",
            "status"
        ])

    active = None
    print("AIORI-3 automatic SRv6 controller started", flush=True)

    while True:
        desired = "primary" if link_is_up() else "backup"

        if desired != active:
            start = time.perf_counter()

            try:
                if desired == "primary":
                    configure_primary()
                else:
                    configure_backup()

                elapsed = (time.perf_counter() - start) * 1000

                event = (
                    "INITIAL_POLICY" if active is None
                    else "FAILOVER" if desired == "backup"
                    else "FAILBACK"
                )

                record(event, desired, elapsed, "SUCCESS")
                active = desired

            except Exception as error:
                elapsed = (time.perf_counter() - start) * 1000
                record(
                    "CONFIGURATION_ERROR",
                    desired, elapsed, str(error)
                )

        time.sleep(INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Controller stopped", flush=True)
