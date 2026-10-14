#!/usr/bin/env bash
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "Run with sudo."; exit 1; }
path="${1:-primary}"
case "$path" in
  primary) ./scripts/configure_primary.sh ;;
  backup) ./scripts/configure_backup.sh ;;
  *) echo "Usage: sudo ./scripts/test_path.sh [primary|backup]"; exit 2 ;;
esac
echo "Testing destination through ${path} policy..."
ip netns exec SR1 ping -6 -c 5 -W 2 2001:db8:ffff::5
