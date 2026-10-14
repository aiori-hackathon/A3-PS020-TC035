# Step 10 — Working demo guide

## Live demonstration sequence

1. Create the lab: `sudo ./scripts/setup_lab.sh`
2. Start capture in a second terminal: `sudo ./scripts/capture.sh`
3. Verify the primary route: `sudo ./scripts/test_path.sh primary`
4. Run the failure and backup-policy switch: `sudo ./scripts/failover_demo.sh`
5. Verify the backup path after the switch: `sudo ./scripts/test_path.sh backup`
6. Stop the capture with Ctrl+C.
7. Review packets: `sudo tcpdump -nn -r captures/srv6-lab.pcap`
8. Save the terminal output and capture file as evaluation evidence.

## What to explain

- The ingress router SR1 inserts an SRH with ordered SIDs.
- The primary policy traverses SR2, SR3 and SR5.
- The SR2–SR3 link is deliberately taken down.
- The script changes SR1's route to the backup SID list through SR2, SR4 and SR5.
- Ping loss and interruption are measured from the actual terminal log; do not invent values.
- The script demonstrates scripted recovery, not automatic BFD/TI-LFA convergence.

## Demo link for GitHub

A local namespace demo is not a hosted web app, so there may be no public URL. For Step 10, put this guide in the repository and include a short screen recording or terminal screenshots. If your hackathon requires a URL, upload the video to an evaluator-accessible platform and put that URL here:

`Demo recording: [ADD YOUR REAL LINK AFTER UPLOAD]`
