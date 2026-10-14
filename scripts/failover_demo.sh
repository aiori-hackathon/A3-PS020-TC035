#!/usr/bin/env bash
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "Run with sudo."; exit 1; }
command -v ping >/dev/null || { echo "ping is required."; exit 1; }

echo "[1/5] Install and test primary policy"
./scripts/configure_primary.sh
ip netns exec SR1 ping -6 -c 3 -W 1 2001:db8:ffff::5

echo
echo "[2/5] Start continuous ping in background"
LOG="results/failover-ping-$(date +%Y%m%d-%H%M%S).log"
mkdir -p results
ip netns exec SR1 ping -6 -n -i 0.2 -W 1 2001:db8:ffff::5 >"$LOG" 2>&1 &
PING_PID=$!
cleanup() { kill "$PING_PID" 2>/dev/null || true; }
trap cleanup EXIT
sleep 2

echo "[3/5] Introduce controlled failure: bring down SR2-SR3 primary link"
date +%s.%N | tee results/failure-injected.timestamp
ip -n SR2 link set s2r3 down
ip -n SR3 link set s3r2 down

echo "[4/5] Switch ingress policy to backup"
date +%s.%N | tee results/backup-policy-switch.timestamp
./scripts/configure_backup.sh
sleep 3
cleanup
trap - EXIT

echo "[5/5] Results"
cat "$LOG"
echo
echo "Ping log: $LOG"
echo "Timestamp files are rough timing markers. Derive loss/interruption from the log; do not treat shell timestamps as packet-level precision."
echo "Primary link remains DOWN. To restore it: sudo ip -n SR2 link set s2r3 up; sudo ip -n SR3 link set s3r2 up"
