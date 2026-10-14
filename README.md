# AIORI-3-HACKATHON-PROJECTS
This repository will contain the code and resources for the AIORI-3 hackathon that will be developed during the AIORI-3
Project Presentation Video

Project: Local SRv6 Path Steering and Measured Failure Recovery

Team Code: A3-PS020-TC035

Presented by: Shiva P and Sanjay S

YouTube Video: https://www.youtube.com/watch?v=8H4Qlj_nEPw

## Verified SRv6 namespace demo

The repository includes scripts for a Linux network-namespace SRv6 lab with
a primary path through SR3 and a backup path through SR4.

- Demo instructions: [`docs/demo.md`](docs/demo.md)
- Architecture: [`docs/architecture.md`](docs/architecture.md)
- Verified lab results and limitations: [`docs/verified-results.md`](docs/verified-results.md)
- Backup packet capture: [`captures/srv6-backup.pcap`](captures/srv6-backup.pcap)

The primary path, scripted link failure, backup policy, and backup connectivity
were tested in the local namespace lab. Recovery timing and packet loss during
the transition have not been established rigorously. See the results report.
