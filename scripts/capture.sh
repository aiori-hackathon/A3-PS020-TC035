#!/usr/bin/env bash
set -euo pipefail

[[ $EUID -eq 0 ]] || {
  echo "Run with sudo: sudo ./scripts/capture.sh"
  exit 1
}

NS="${1:-SR2}"
IFACE="${2:-any}"
OUT="captures/srv6-lab.pcap"

command -v tcpdump >/dev/null || {
  echo "Missing tcpdump."
  exit 1
}

ip netns list | awk '{print $1}' | grep -Fxq "$NS" || {
  echo "Network namespace $NS does not exist."
  exit 1
}

mkdir -p captures
echo "Capturing IPv6 traffic inside namespace $NS on interface $IFACE"
echo "Output: $OUT"
echo "Press Ctrl+C to stop."

exec ip netns exec "$NS" tcpdump -U -ni "$IFACE" -s 0 \
  -w "$OUT" 'ip6'
