#!/usr/bin/env bash
set -euo pipefail

# AIORI-3 PS-020: Linux SRv6 topology setup
# WARNING: Replaces the named lab network namespaces.

if [ "$(id -u)" -ne 0 ]; then
    echo "Run this script with sudo."
    exit 1
fi

for tool in ip python3; do
    command -v "$tool" >/dev/null || {
        echo "Missing dependency: $tool"
        exit 1
    }
done

echo "Creating AIORI-3 SRv6 lab..."

NAMESPACES=(HOST1 R1 R2 R3 R4 R5)

for ns in "${NAMESPACES[@]}"; do
    ip netns del "$ns" 2>/dev/null || true
    ip netns add "$ns"
    ip -n "$ns" link set lo up
done

create_link() {
    local ns1="$1" if1="$2" ns2="$3" if2="$4"
    for iface in "$if1" "$if2"; do
        if ip link show "$iface" >/dev/null 2>&1; then
            echo "ERROR: Interface $iface already exists."
            echo "Inspect it before deleting."
            exit 1
        fi
    done
    ip link add "$if1" type veth peer name "$if2"
    ip link set "$if1" netns "$ns1"
    ip link set "$if2" netns "$ns2"
    ip -n "$ns1" link set "$if1" up
    ip -n "$ns2" link set "$if2" up
}

create_link HOST1 h1eth0 R1 r1host0
create_link R1 r1eth0 R2 r2eth0
create_link R1 r1r3 R3 r3r1
create_link R2 r2r4 R4 r4r2
create_link R3 r3r4 R4 r4r3
create_link R4 r4r5 R5 r5r4

# Enable IPv6 forwarding and SRv6 in router namespaces.
for ns in R1 R2 R3 R4 R5; do
    ip netns exec "$ns" sysctl -qw net.ipv6.conf.all.forwarding=1
    ip netns exec "$ns" sysctl -qw net.ipv6.conf.all.seg6_enabled=1

    for iface in $(ip -n "$ns" -o link show | awk -F': ' '{print $2}' | cut -d@ -f1); do
        ip netns exec "$ns" sysctl -qw \
            "net.ipv6.conf.$iface.seg6_enabled=1"
    done
done

addr() {
    ip -n "$1" -6 addr add "$2" dev "$3"
}

addr HOST1 2001:db8:1::10/64 h1eth0
addr R1 2001:db8:1::1/64 r1host0

addr R1 2001:db8:12::1/64 r1eth0
addr R2 2001:db8:12::2/64 r2eth0

addr R1 2001:db8:13::1/64 r1r3
addr R3 2001:db8:13::3/64 r3r1

addr R2 2001:db8:24::2/64 r2r4
addr R4 2001:db8:24::4/64 r4r2

addr R3 2001:db8:34::3/64 r3r4
addr R4 2001:db8:34::4/64 r4r3

addr R4 2001:db8:45::4/64 r4r5
addr R5 2001:db8:45::5/64 r5r4

addr R5 2001:db8:ffff::5/128 lo

# HOST1 default gateway.
ip -n HOST1 -6 route replace default \
    via 2001:db8:1::1 dev h1eth0

# Forward and return underlay routes.
ip -n R2 -6 route replace 2001:db8:1::/64 \
    via 2001:db8:12::1 dev r2eth0

ip -n R3 -6 route replace 2001:db8:1::/64 \
    via 2001:db8:13::1 dev r3r1

ip -n R4 -6 route replace 2001:db8:1::/64 \
    via 2001:db8:24::2 dev r4r2

ip -n R5 -6 route replace 2001:db8:1::/64 \
    via 2001:db8:45::4 dev r5r4

# Routes to the final decapsulation SID.
ip -n R2 -6 route replace 2001:db8:100::5/128 \
    via 2001:db8:24::4 dev r2r4

ip -n R3 -6 route replace 2001:db8:100::5/128 \
    via 2001:db8:34::4 dev r3r4

ip -n R4 -6 route replace 2001:db8:100::5/128 \
    via 2001:db8:45::5 dev r4r5

# Primary and backup transit SIDs.
ip -n R2 -6 route replace 2001:db8:100::2/128 \
    encap seg6local action End dev r2eth0

ip -n R3 -6 route replace 2001:db8:100::3/128 \
    encap seg6local action End dev r3r1

# R5 decapsulation table and local destination.
ip -n R5 -6 route replace \
    2001:db8:100::5/128 \
    encap seg6local action End.DT6 table 105 dev r5r4

ip -n R5 -6 route replace local \
    2001:db8:ffff::5/128 dev lo table 105

ip -n R5 -6 route replace 2001:db8:1::/64 \
    via 2001:db8:45::4 dev r5r4 table 105

# R1 SID reachability.
ip -n R1 -6 route replace 2001:db8:100::2/128 \
    via 2001:db8:12::2 dev r1eth0

ip -n R1 -6 route replace 2001:db8:100::3/128 \
    via 2001:db8:13::3 dev r1r3

# Primary SRv6 encapsulation policy.
ip -n R1 -6 route replace \
    2001:db8:ffff::5/128 \
    encap seg6 mode encap \
    segs 2001:db8:100::2,2001:db8:100::5 \
    via 2001:db8:12::2 dev r1eth0

echo
echo "Topology configured."
echo "Testing primary SRv6 path..."
ip netns exec HOST1 ping -6 -c 5 -W 2 2001:db8:ffff::5

echo
echo "AIORI-3 topology setup complete."
