# Experimental Evidence Index & Step 64 Correlation Report

## 1. Preserved & Live-Verified Experimental Artifacts Index

All historical experimental data, collector checkpoints, and switch packet captures are 100% preserved and verified by SHA-256:

| Artifact Path | Role | Size (Bytes) | SHA-256 |
|---|---|---:|---|
| `database/sdnflowguard.db` | Primary SQLite database (`flows`: 25, `events`: 8, `actions`: 89, `settings`: 5) | `28,672` | `3909de520f89ea050e7858104c8aa17bddd94d06af9db5ad84652404b9463fe9` |
| `database/netsecflow.db.bak` | Historical pre-branding SQLite backup | `28,672` | `d12be7a29b412061213ef13f1c7e47e75405f84a83fb9949bbde3c7e31110443` |
| `backend/defense/evidence/ingress_icmp_20261101_014645.txt` | Step 63 raw UTF-16 `tcpdump -nne` capture from switch `s1` (`s1-eth1`, `s1-eth2`) | `5,146` | `3076efccdc79564568e320b983b1fd12c2f1ef4f1ec2df55f7ab4e21a21b40d7` |
| `backend/defense/evidence/ingress_icmp_20261101_014645.json` | Step 63 structured packet observation JSON (`24` ICMP packets) | `2,202` | `05a659224fb184be2e0e7416f18602bc6d658a10d5d43d7b89c1420db024e91c` |
| `backend/defense/evidence/ingress_icmp_live_utc_verified.txt` | Step 72 live WSL `Ubuntu-26.04` `tcpdump -i any -nne -Q in` capture on `s1` | `959` | `bef49f603007d7f0fd154b691d8de9b8945a7e89055bf6f4c9fa7ff7d71c8cf8` |
| `backend/defense/evidence/ingress_icmp_live_utc_verified.json` | Step 72 structured observation JSON with full UTC window (`2026-11-05T06:20:32Z` -> `2026-11-05T06:20:36Z`) | `1,521` | `1d36f69569871845848c5cbcdec2c99ce2d1832da53b3b4cf70ba4750cfdda68` |
| `backend/collectors/state/auto_dry_t4_c2.json` | Reliable Monitor V1 dry-run cursor checkpoint | `376` | `c852e276cbca38ec0bc9a637c132d6cc3be6d735fc67d393055ff6a9ef19a91e` |
| `backend/collectors/state/auto_dry_t4_c2_v2.json` | Overlap Monitor V2 dry-run watermark checkpoint | `5,395` | `c011906fb042f684fd33945f2c5b8c04d31f925b80eb774da06346ff2512fc33` |
| `backend/collectors/state/auto_publish_t4_c2.json` | Reliable Monitor V1 publish cursor checkpoint | `376` | `a2ab7d86fc0bc5a19833a44a2232c1914f8fb2bc97c832c451ff1a4533bf0628` |
| `backend/collectors/state/auto_publish_t4_c2_v2.json` | Overlap Monitor V2 publish watermark checkpoint | `5,495` | `dc7fb2ef306c64e4ecbc0f950174da1cf002798efab5166037b0ab95395cb16e` |

---

## 2. Step 64 & Step 72 ONOS Host Evidence Correlation Report

### 2.1. Problem Statement
In SDN telemetry, OpenFlow port statistics (`rx_pps`, `tx_pps` on `of:0000000000000001` port `1` or `2`) only measure packet volume on a switch port. Discovering a host attached to that port via ONOS (`/onos/v1/hosts`) does **not** by itself prove that the host originated a malicious flood or spoofed traffic (`Attached Host != Verified Attacker`).

### 2.2. Step 63 + Step 64 Two-Stage Verification Methodology
1. **Step 63 (`backend/defense/source_ip_evidence_analyzer.py`):** Captures and parses actual L2/L3 packets entering switch ingress interfaces (`s1-eth1` -> port `1`, `s1-eth2` -> port `2`), extracting `observed_source_mac`, `observed_source_ip`, `observed_destination_ip`, `protocol`, `icmp_type`, `packet_count`, `first_seen_clock`, and `last_seen_clock`, plus optional UTC capture window bounds (`--started-utc`, `--finished-utc`).
2. **Step 64 (`backend/defense/onos_host_evidence_correlator.py` & `sdnflowguard/domain/services/evidence_correlation.py`):** Correlates Step 63 observations against ONOS topology (`devices`, `ports`, `hosts`, `flows`) and Elasticsearch alert windows:
   - Verifies that `of:0000000000000001` is available and ports `1` and `2` are enabled.
   - Verifies single-host vs. multi-host attachment on each port (`AMBIGUOUS_MULTI_HOST` if >1 host on the same port).
   - Verifies exact `(MAC, IP)` identity match between packet headers and ONOS host registry (`CORROBORATED_HOST_OBSERVATION` vs. `HOST_IDENTITY_MISMATCH` or `UNREGISTERED_HOST_ON_PORT`).
   - Checks whether the packet capture has full UTC date/timezone metadata overlapping an active non-test anomaly alert window (`historical_alert_correlation_verified`).

### 2.3. Live ONOS Execution Output on Historical Step 63 Evidence (`ingress_icmp_20261101_014645.json`)
```text
=== SDNFLOWGUARD STEP 64: ONOS HOST EVIDENCE CORRELATOR ===
Mode: DRY RUN - READ ONLY
Evidence file: D:\Project\Nhom02_SDNFlowGuard\backend\defense\evidence\ingress_icmp_20261101_014645.json
Topology source: LIVE_ONOS
Switch ID: of:0000000000000001
Total packets analyzed: 24

[1] Port=1 Interface=s1-eth1 MAC=00:00:00:00:00:01 IP=10.0.0.1 -> 10.0.0.2 Packets=12 Status=CORROBORATED_HOST_OBSERVATION
[2] Port=2 Interface=s1-eth2 MAC=00:00:00:00:00:02 IP=10.0.0.2 -> 10.0.0.1 Packets=12 Status=CORROBORATED_HOST_OBSERVATION

=== SECURITY ASSESSMENT ===
Topology corroborated: True
Historical alert correlation verified: False
Time verification reason: Evidence file only contains local clock timestamps without UTC date/timezone metadata.
Attacker confirmed: False
Overall Decision: OBSERVE
Automatic Block Allowed: False
```

### 2.4. Live ONOS Execution Output on UTC-Tagged Capture (`ingress_icmp_live_utc_verified.json`)
```text
=== SDNFLOWGUARD STEP 64: ONOS HOST EVIDENCE CORRELATOR ===
Mode: DRY RUN - READ ONLY
Evidence file: D:\Project\Nhom02_SDNFlowGuard\backend\defense\evidence\ingress_icmp_live_utc_verified.json
Topology source: LIVE_ONOS
Switch ID: of:0000000000000001
Total packets analyzed: 8

[1] Port=1 Interface=s1-eth1 MAC=00:00:00:00:00:01 IP=10.0.0.1 -> 10.0.0.2 Packets=4 Status=CORROBORATED_HOST_OBSERVATION
[2] Port=2 Interface=s1-eth2 MAC=00:00:00:00:00:02 IP=10.0.0.2 -> 10.0.0.1 Packets=4 Status=CORROBORATED_HOST_OBSERVATION

=== SECURITY ASSESSMENT ===
Topology corroborated: True
Historical alert correlation verified: False
Time verification reason: Full UTC capture window verified, but no matching alerts occurred during the capture window.
Attacker confirmed: False
Overall Decision: OBSERVE
Automatic Block Allowed: False
```
