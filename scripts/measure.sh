#!/usr/bin/env bash
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "Run with sudo."; exit 1; }
mkdir -p results
OUT="results/measurement-$(date +%Y%m%d-%H%M%S).txt"
{
  echo "Timestamp: $(date --iso-8601=ns)"
  echo "Kernel: $(uname -r)"
  echo "iproute2: $(ip -Version 2>&1 | head -n1)"
  echo
  echo "Primary route:"
  ip -n SR1 -6 -d route show 2001:db8:ffff::5/128
  echo
  echo "Link states:"
  ip -n SR2 link show s2r3
  ip -n SR3 link show s3r2
  ip -n SR2 link show s2r4
  ip -n SR4 link show s4r2
  echo
  echo "Baseline ping (5 packets):"
  ip netns exec SR1 ping -6 -c 5 -W 2 2001:db8:ffff::5
} | tee "$OUT"
echo "Saved $OUT"
