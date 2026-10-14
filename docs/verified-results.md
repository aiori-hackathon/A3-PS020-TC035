# Verified SRv6 Lab Results

## Environment
- Test type: Linux network namespaces with SRv6
- Namespaces: SR1, SR2, SR3, SR4, SR5
- Primary path: SR1 -> SR2 -> SR3 -> SR5
- Backup path: SR1 -> SR2 -> SR4 -> SR5
- Controlled failure: SR2-SR3 link brought down

## Verified tests

| Test | Packets sent | Replies received | Packet loss | Average RTT |
|---|---:|---:|---:|---:|
| Primary path test | 5 | 5 | 0% | 0.183 ms |
| Backup path test | 5 | 5 | 0% | 0.269 ms |
| Backup packet-capture test | 5 | 5 | 0% | 0.184 ms |

The RTT values are from separate ping runs and are not a controlled performance comparison.

## Packet capture
- File: `captures/srv6-backup.pcap`
- Packets decoded: 10
- Kernel packet drops reported by tcpdump: 0
- IPv6 Routing Header Type 4 (Segment Routing Header) was visible.
- The capture was taken on SR2 interface `s2r4`, the backup-side link.

## Failure and recovery demonstration
The failover script brought down the SR2-SR3 link and changed SR1's policy to the backup segment list. Subsequent backup-path pings succeeded.

The continuous-ping log contains 25 successful replies, but the script stopped the ping before printing its final statistics. Therefore, packet loss during the transition and interruption duration are not reported here.

The two shell timestamp markers are approximately 51.98 ms apart. This is the interval between recorded script timestamps, not a measured network recovery time.

## Limitations
- Recovery is triggered by a script; automatic BFD or TI-LFA convergence is not demonstrated.
- Failure detection delay, repair delay, interruption duration, and SRH overhead have not yet been measured rigorously.
- The repository's original simulation outputs remain separate from these live namespace-lab results.
