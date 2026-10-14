# SRv6 Demo Evidence

This folder contains evidence from the Linux SRv6 lab execution.

## Test Results
- Primary path: SR1 → SR2 → SR3 → SR5 — 5/5 packets received, 0% packet loss.
- Backup path: SR1 → SR2 → SR4 → SR5 — 5/5 packets received, 0% packet loss.
- Controlled failure: SR2–SR3 link brought down and ingress policy switched to backup.
- Recovery verification: primary link and IPv6 configuration restored; final primary test passed with 5/5 packets received.

Note: Recovery timestamps are approximate shell markers, not packet-level recovery measurements.
