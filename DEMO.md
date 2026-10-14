Demo Instructions

Project

Local SRv6 Path Steering and Measured Failure Recovery

Team Code

A3-PS020-TC035

Requirements

- Kali Linux VM
- IPv6 and SRv6 support
- iproute2 tools
- Python 3

Run the simulation

Open a terminal in the project directory and run:

cd src
python3 srv6_lab.py --trials 10 --packets 120

Results

Check the generated CSV and JSON files for simulation outputs.

## Demo status

The live SRv6 namespace lab has been verified on Kali Linux. The primary path (SR1 → SR2 → SR3 → SR5) and backup path (SR1 → SR2 → SR4 → SR5) each passed a five-packet connectivity test with 0% packet loss. A controlled failure of the SR2–SR3 link and a scripted switch to the backup policy were demonstrated. The primary link and IPv6 configuration were subsequently restored and the primary path passed its final connectivity test.

Recovery interruption duration and packet loss during the transition have not been rigorously measured. This prototype demonstrates scripted recovery, not automatic BFD/TI-LFA convergence. Simulation outputs are separate from live lab measurements.
