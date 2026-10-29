# AIORI-3 Hackathon Projects

**Project:** Local SRv6 Path Steering and Measured Failure Recovery  
**Team Code:** A3-PS020-TC035  
**Presented by:** Shiva P and Sanjay S

## Project Presentation Video

[Watch the project presentation on YouTube](https://www.youtube.com/watch?v=8H4Qlj_nEPw)

## Verified SRv6 Namespace Demo

This repository includes scripts for a Linux network-namespace SRv6 lab demonstrating primary-path steering, a controlled link failure, and scripted backup-path recovery.

### Network paths

- **Primary:** SR1 → SR2 → SR3 → SR5
- **Backup:** SR1 → SR2 → SR4 → SR5
- **Failure link:** SR2–SR3

### Run the demo

Run these commands from the repository directory in a Linux environment with the required networking tools and permissions:

```bash
sudo ./scripts/setup_lab.sh
sudo ./scripts/test_path.sh primary
sudo ./scripts/failover_demo.sh
sudo ./scripts/test_path.sh backup
```

**Note:** The setup script recreates the `SR1`–`SR5` namespaces if they already exist. Review the script before running it if you have existing namespaces with those names.

### Documentation and evidence

- [Demo instructions](docs/demo.md)
- [Architecture](docs/architecture.md)
- [Verified lab results and limitations](docs/verified-results.md)
- [Results template](docs/results-template.md)
- [Backup-path packet capture](captures/srv6-backup.pcap)
- [Original simulation source](src/srv6_lab.py)

## Verification status

The primary path, controlled link failure, backup policy switch, backup connectivity, and SRv6 packet capture were verified in the local namespace lab.

Recovery interruption duration and packet loss during the transition have not yet been rigorously measured. The prototype demonstrates **script-triggered recovery**, not automatic BFD/TI-LFA convergence.

The repository's simulation results are separate from the live namespace-lab measurements.
## Real Linux SRv6 Experiment

This project includes a real Linux kernel SRv6 experiment,
separate from the Python simulation.

**Primary path:** HOST1 -> R1 -> R2 -> R4 -> R5

**Backup path:** HOST1 -> R1 -> R3 -> R4 -> R5

### Verified results

| Metric | Result |
|---|---:|
| ICMPv6 packets received | 359 / 360 |
| Packet loss | 0.2778% |
| Median RTT | 0.138 ms |
| Mean RTT | 82.991 ms |
| Failover configuration time | 15.009 ms |
| Failback configuration time | 35.698 ms |

Configuration times are not end-to-end recovery times.
These measurements represent one experiment run.

### Project files

- [Linux setup guide](linux-lab/SETUP.md)
- [Topology setup script](linux-lab/setup_topology.sh)
- [Automatic failover controller](linux-lab/failover_controller.py)
- [Recovery analyzer](linux-lab/analyze_recovery.py)
- [Demonstration guide](docs/DEMO.md)
- [Measured recovery report](results/linux-srv6/recovery_report.md)

The topology script has passed syntax checking,
but a fresh rebuild has not yet been verified.
