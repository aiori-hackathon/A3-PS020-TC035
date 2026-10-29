# AIORI-3 PS-020 — SRv6 Demonstration

Team: A3-PS020-TC035

## 1. Show primary SRv6 policy
sudo ip -n R1 -6 route show 2001:db8:ffff::5/128

## 2. Test primary connectivity
sudo ip netns exec HOST1 ping -6 -c 5 2001:db8:ffff::5

## 3. Start automatic controller
sudo python3 -u linux-lab/failover_controller.py

Run the remaining commands in another terminal.

## 4. Simulate link failure
sudo ip -n R1 link set r1eth0 down

Expected backup path: R1 -> R3 -> R4 -> R5

## 5. Restore primary link
sudo ip -n R1 link set r1eth0 up

Expected primary path: R1 -> R2 -> R4 -> R5

## 6. Recorded experiment results
Packets received: 359/360
Packet loss: 0.2778%
Median RTT: 0.138 ms
Failover configuration: 15.009 ms
Failback configuration: 35.698 ms

Configuration time is not total network recovery time.
These results represent one real Linux SRv6 experiment.

## 7. Evidence files
results/linux-srv6/continuous_ping.txt
results/linux-srv6/failover_events.csv
results/linux-srv6/recovery_analysis.json
results/linux-srv6/recovery_report.md
