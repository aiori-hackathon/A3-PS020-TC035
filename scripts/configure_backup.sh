#!/usr/bin/env bash
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "Run with sudo."; exit 1; }
ip -n SR1 -6 route replace 2001:db8:ffff::5/128 \
  encap seg6 mode encap \
  segs 2001:db8:101::2,2001:db8:100::4,2001:db8:100::5 \
  dev s1r2
echo "Backup SRv6 policy installed: SR1 -> SR2 -> SR4 -> SR5"
ip -n SR1 -6 -d route show 2001:db8:ffff::5/128
