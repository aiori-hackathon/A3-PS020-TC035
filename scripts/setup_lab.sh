#!/usr/bin/env bash
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Run with sudo: sudo $0"
  exit 1
fi
for cmd in ip sysctl; do
  command -v "$cmd" >/dev/null || { echo "Missing command: $cmd"; exit 1; }
done

# Use SR1-SR5 so the existing R1-R5 lab is not touched.
for ns in SR1 SR2 SR3 SR4 SR5; do
  ip netns del "$ns" 2>/dev/null || true
  ip netns add "$ns"
  ip -n "$ns" link set lo up
  ip netns exec "$ns" sysctl -qw net.ipv6.conf.all.forwarding=1
  ip netns exec "$ns" sysctl -qw net.ipv6.conf.all.seg6_enabled=1
done

make_link() {
  local a_ns="$1" a_if="$2" b_ns="$3" b_if="$4"
  ip link add "$a_if" type veth peer name "$b_if"
  ip link set "$a_if" netns "$a_ns"
  ip link set "$b_if" netns "$b_ns"
  ip -n "$a_ns" link set "$a_if" up
  ip -n "$b_ns" link set "$b_if" up
  ip netns exec "$a_ns" sysctl -qw "net.ipv6.conf.${a_if}.seg6_enabled=1"
  ip netns exec "$b_ns" sysctl -qw "net.ipv6.conf.${b_if}.seg6_enabled=1"
}

# Diamond-like topology: SR1-SR2; primary SR2-SR3-SR5; backup SR2-SR4-SR5.
make_link SR1 s1r2 SR2 s2r1
make_link SR2 s2r3 SR3 s3r2
make_link SR3 s3r5 SR5 s5r3
make_link SR2 s2r4 SR4 s4r2
make_link SR4 s4r5 SR5 s5r4

ip -n SR1 -6 addr add 2001:db8:12::1/64 dev s1r2
ip -n SR2 -6 addr add 2001:db8:12::2/64 dev s2r1
ip -n SR2 -6 addr add 2001:db8:23::2/64 dev s2r3
ip -n SR3 -6 addr add 2001:db8:23::3/64 dev s3r2
ip -n SR3 -6 addr add 2001:db8:35::3/64 dev s3r5
ip -n SR5 -6 addr add 2001:db8:35::5/64 dev s5r3
ip -n SR2 -6 addr add 2001:db8:24::2/64 dev s2r4
ip -n SR4 -6 addr add 2001:db8:24::4/64 dev s4r2
ip -n SR4 -6 addr add 2001:db8:45::4/64 dev s4r5
ip -n SR5 -6 addr add 2001:db8:45::5/64 dev s5r4

# Destination and SIDs.
ip -n SR5 -6 addr add 2001:db8:ffff::5/128 dev lo
ip -n SR2 -6 addr add 2001:db8:101::2/128 dev lo
ip -n SR3 -6 addr add 2001:db8:100::3/128 dev lo
ip -n SR4 -6 addr add 2001:db8:100::4/128 dev lo
ip -n SR5 -6 addr add 2001:db8:100::5/128 dev lo

# End behaviors on transit SIDs. End.DT6 decapsulates at SR5 into table 105.
ip -n SR2 -6 route replace 2001:db8:101::2/128 encap seg6local action End dev s2r1
ip -n SR3 -6 route replace 2001:db8:100::3/128 encap seg6local action End dev s3r2
ip -n SR4 -6 route replace 2001:db8:100::4/128 encap seg6local action End dev s4r2
ip -n SR5 -6 route replace table 105 local 2001:db8:ffff::5/128 dev lo
ip -n SR5 -6 route replace 2001:db8:100::5/128 encap seg6local action End.DT6 table 105 dev s5r3

# Keep return traffic on the backup-side link so replies still reach SR1 when SR2-SR3 is down.
ip -n SR5 -6 route replace 2001:db8:12::/64 via 2001:db8:45::4 dev s5r4
ip -n SR4 -6 route replace 2001:db8:12::/64 via 2001:db8:24::2 dev s4r2

# SID reachability at each transit router.
ip -n SR1 -6 route replace 2001:db8:101::2/128 via 2001:db8:12::2 dev s1r2
ip -n SR2 -6 route replace 2001:db8:100::3/128 via 2001:db8:23::3 dev s2r3
ip -n SR2 -6 route replace 2001:db8:100::4/128 via 2001:db8:24::4 dev s2r4
ip -n SR3 -6 route replace 2001:db8:100::5/128 via 2001:db8:35::5 dev s3r5
ip -n SR4 -6 route replace 2001:db8:100::5/128 via 2001:db8:45::5 dev s4r5

echo "SRv6 lab created. Run: sudo ./scripts/configure_primary.sh"
