# SDNFlowGuard — Academic & Technical Requirements Traceability Matrix

**Course:** Chuyên đề – Hệ thống mạng và bảo mật (`123046`) — Trường Đại học Giao thông vận tải TP. Hồ Chí Minh (UTH)  
**Topic (Group 02):** *Nghiên cứu và triển khai phòng thủ mạng tự động qua SDN tích hợp giám sát bằng ELK Stack*  
**Date:** 2026-11-18  

> **Academic Integrity Notice:** All verification statuses strictly distinguish `IMPLEMENTED`, `UNIT_TESTED`, `INTEGRATION_TESTED`, `LIVE_VERIFIED`, `FIXTURE_SIMULATED`, `PENDING`, `BLOCKED_BY_ENVIRONMENT`, and `UNVERIFIED`. External course PDFs and CEH v13 reference materials were consulted read-only and are **never** copied into this repository.

---

## 1. Traceability to Course Project Specification & Proposal

Reference sources consulted read-only:
- `Nhom02_PhanPhatDat_Tong_quan_de_tai.docx` (Group 02 Topic Overview)
- `DeTai.pdf` (Course Topic Guidelines: Topic #12 SIEM ELK, #11 Snort/Suricata IDS/IPS, #26 DoS/DDoS Rate Limiting, 4-step Demo requirement: Setup -> Test -> Defense -> Verify)
- `QUY DINH TRINH BAY BAO CAO BAI TẬP LỚN.pdf` (Formatting & Submission Rules)

| Req ID | Requirement (Course & Proposal) | Implementation in Workspace | Automated / Evidence Verification | Current Status (Pre-Remediation) |
|---|---|---|---|---|
| **REQ-01** | Centralized SDN Security Monitoring Web UI (React + Flask + SQLite) | `frontend/src/pages/{Dashboard,TrafficOverview,AnomalyDetection,DecisionLogs,ManualTrafficControl,Reports,SystemSettings}.js`, `backend/run.py`, `database/sdnflowguard.db` | `test_frontend_backend_api_contracts.py`, `test_flask_api_routes.py`, Docker live healthcheck (`3000`, `5000`) | `LIVE_VERIFIED` (Frontend/Backend UP) + `INTEGRATION_TESTED` |
| **REQ-02** | SDN Lab Simulation with ONOS Controller, OpenFlow 1.3, Open vSwitch, Mininet | `docker-compose.yml` (`onosproject/onos:2.7-latest`), `infrastructure/mininet/sdnflowguard_lab_topo.py`, WSL2 systemd `sdnflowguard-topo.service` | 6 switches (`s1`..`s6`) & 9 hosts (`h1`..`h9`) connected to ONOS via OpenFlow 1.3; 10 links; 24 live flows; pingall 0% packet loss | `LIVE_VERIFIED` (Active 6S9H Lab + Historical Evidence) |
| **REQ-03** | Real-Time Topology, Switch, Host, Flow & Port Telemetry Visibility | `backend/app/topology.py`, `backend/run.py` (`/api/topology`, `/api/live-flows`, `/api/live-port-stats`), `frontend/src/pages/{TrafficOverview,LiveSdnSummary,SdnPortRates,OnosLiveFlows}.js` | `test_topology_service.py` (6 tests), `test_flask_api_routes.py` | `UNIT_TESTED` + `INTEGRATION_TESTED` |
| **REQ-04** | Telemetry Collection & Event Ingestion Pipeline (ONOS -> Logstash -> Elasticsearch -> Kibana) | `backend/collectors/{onos_elk_collector,onos_port_elk_collector}.py`, `infrastructure/logstash/pipeline/01-sdnflowguard.conf`, `docker-compose.yml` | ES holds 145 docs across 4 `sdnflowguard-events-*` indices; Logstash pipeline `UP`; `test_elasticsearch_query_contracts.py` | `LIVE_VERIFIED` (ELK Stack UP + indexed docs) + `INTEGRATION_TESTED` |
| **REQ-05** | Rule-Based Traffic Anomaly Detection (High-PPS Streak, Overlap Window V2, Deduplication) | `backend/collectors/{sdn_port_anomaly_detector,sdn_alert_publisher,sdn_reliable_alert_monitor,sdn_overlap_alert_monitor_v2}.py` | `test_port_anomaly_detector.py`, `test_alert_publisher.py`, `test_reliable_monitor_v1.py`, `test_reliable_monitor_v2.py`, CLI `--self-test` | `UNIT_TESTED` + `LIVE_VERIFIED` (16 historical alerts in ES) |
| **REQ-06** | Source IP/MAC Packet Evidence Capture & ONOS Topology Corroboration (Step 63 & Step 64) | `backend/defense/{source_ip_evidence_analyzer,onos_host_evidence_correlator}.py`, `backend/sdnflowguard/domain/services/evidence_correlation.py`, `backend/defense/evidence/*` | `test_source_ip_evidence_analyzer.py`, `test_onos_host_evidence_correlator.py`, real switch `tcpdump` captures (`s1-eth1`, `s1-eth2`) | `LIVE_VERIFIED` (Historical Captures) + `UNIT_TESTED` |
| **REQ-07** | Policy-Driven Risk Scoring & Defense Decision Engine (`ALLOW`, `OBSERVE`, `PROPOSE_BLOCK`) | `backend/defense/sdn_defense_policy.py`, `backend/app/decision.py`, `backend/sdnflowguard/domain/policies/{defense_policy,risk_scoring}.py` | `test_defense_policy.py`, `test_risk_scoring_and_decision.py`, `test_port_anomaly_never_blocks_ip.py` | `UNIT_TESTED` (P1-04 minor cleanup queued) |
| **REQ-08** | Fail-Safe Controlled Active Defense (Safety Gate, `DRY_RUN` Default, Protected IPs, Operator Auth) | `backend/sdnflowguard/domain/policies/safety_gate.py`, `backend/sdnflowguard/interfaces/http/security.py`, `backend/app/controller_actions.py` | `test_safety_gate.py`, `test_dry_run_default.py`, `test_test_alert_never_blocks.py`, `test_remediation_findings.py` | `UNIT_TESTED` — **P0-01 / P0-02 auth propagation defects identified & queued for remediation** |
| **REQ-09** | Controlled Block (ACL), Rate Limiting (OpenFlow 1.3 Meter), Redirect (Intent) & Post-Action Verification | `backend/app/controller_actions.py`, `backend/sdnflowguard/infrastructure/onos/onos_client.py` | `test_onos_payload_contracts.py` (`DRY_RUN` verified); live ONOS ACL/Meter verification blocked by P1-01 (`acl` app) & P1-02 (read-back check) | `UNIT_TESTED` (DRY_RUN) / Live enforcement `PENDING` (P1-01/P1-02 fixes queued) |
| **REQ-10** | Reversible Rollback & Network Recovery Verification | `backend/app/controller_actions.py` (`unblock_ip`), `/api/unblock`, `/api/defense/rollback`, `ManualTrafficControl.js` | `test_fault_injection_and_resilience.py`, `test_full_monitoring_to_policy_pipeline.py` | `INTEGRATION_TESTED` (P1-03 `NoneType` guard & meter rollback clarity queued) |
| **REQ-11** | Multi-Source SIEM Log Normalization (SDN, Suricata/IDS Webhook, Firewall Syslog, Windows Event Log) | `backend/app/reception.py`, `backend/sdnflowguard/domain/services/siem_log_normalizer.py`, `/api/siem/normalize`, `/api/siem/evaluate-fixtures` | `test_webhook_reception.py`, `test_siem_log_normalizer.py` | SDN/Webhook: `INTEGRATION_TESTED`; Firewall & Windows Server: `FIXTURE_SIMULATED` (explicitly tagged, no physical FW/AD host in lab) |
| **REQ-12** | Audit Logging, Decision Trail, PDF/JSON Reporting & Read-Only Security Assistant | `database/sdnflowguard.db` (`actions`, `events`, `flows`), `backend/app/{report,chatbot}.py`, `DecisionLogs.js`, `Reports.js` | `test_sqlite_repository.py`, `test_report_generator.py`, `test_flask_api_routes.py` | `INTEGRATION_TESTED` |
| **REQ-13** | Reproducibility, CI/CD, & Clean Source Delivery | `scripts/{manage,test,backup_database,reclaim_wsl_memory}.ps1`, `.github/workflows/sdn_flowguard_ci.yml`, `README.md`, `docs/*` | `scripts/test.ps1` (85/85 PASS) | `INTEGRATION_TESTED` (P2-01/02/03/04 doc & script sync queued) |

---

## 2. Traceability to Course Theory (UTH Slides Chapters 01–05)

| Course Chapter | Key Security Concepts Covered | Alignment in SDNFlowGuard |
|---|---|---|
| **Chương 01** (`Chuong 01.pdf`) | CIA Triad, Authenticity & Accountability, Saltzer & Schroeder Principles (pp. 23–25: *Fail-Safe Defaults*, *Least Privilege*, *Complete Mediation*, *Economy of Mechanism*), Defense-in-Depth, NIST CSF, Zero Trust | Default `DRY_RUN` mode & `AWAITING_OPERATOR_APPROVAL` (*Fail-Safe Defaults*); `check_api_key` + `is_operator_authenticated` on all mutating endpoints (*Complete Mediation*); SQLite `actions` audit trail (*Accountability*); Multi-layer defense: ELK detection -> Step 63/64 evidence -> Safety Gate -> ONOS ACL/Meter (*Defense-in-Depth*). |
| **Chương 02** (`Chuong 02.pdf`) | RFC 4949 Threat Taxonomy, Passive vs Active Attacks, Botnet/DoS/Scanning Attacks | Detection of high-PPS flooding anomalies (`sdn_port_anomaly_detector.py`, `sdn_overlap_alert_monitor_v2.py`), IDS webhook risk scoring (`decision.py`), and evidence distinction between benign traffic and active attack attribution. |
| **Chương 03** (`Chuong 03.pdf`) | Network Security Controls, Access Control / RBAC, Data Integrity & 3-2-1 Backup | Protected infrastructure allowlist (`10.0.0.254`, DNS, loopback, Controller/ELK IPs), SHA-256 verification of DB and packet captures, `scripts/backup_database.ps1` online SQLite backup. |
| **Chương 04** (`Chuong 04.pdf`) | Packet-Filtering & Stateful Firewalls, Default-Discard, IP Spoofing & Tiny Fragment Evasion | ONOS OpenFlow 1.3 ACL/Flow rules acting as programmable SDN distributed firewall; Step 63/64 `(MAC, IP, ingress_port)` verification defends against naive IP spoofing attribution (`HOST_IDENTITY_MISMATCH`); Firewall syslog normalization (`siem_log_normalizer.py`). |
| **Chương 05** (`Chuong 05.pdf`) | Authentication, Replay Protection, Network Access Control (NAC), Database Security | Constant-time `hmac.compare_digest` API key verification; parameterized SQLite queries (`?` placeholders) preventing SQL injection; strict input validation (`validate_ip_input`, `validate_rate_input`, `validate_device_id_input`). |

---

## 3. Traceability to CEH v13 Authorized Lab Curriculum

| CEH v13 Module | Verified Topics & Page Citations | Defensive Mapping in SDNFlowGuard |
|---|---|---|
| **Module 03 — Scanning Networks** | Host discovery, TCP flags, Nmap/Hping3 scanning (pp. 281–407); Ping Sweep, Port Scan & IP Spoofing countermeasures (pp. 408–420) | High-rate ICMP/TCP probe bursts captured by ONOS port counters -> Logstash -> Elasticsearch; Step 63 `tcpdump -nne` ingress inspection verifies true `(MAC, IP)` on switch port before any block decision; SDN ACL rules filter unauthorized probes. |
| **Module 08 — Sniffing** | Switched Ethernet, SPAN/mirroring, MAC Flooding, ARP Spoofing, Switch Port Stealing, Wireshark packet analysis (pp. 1267–1375); DAI & IP Source Guard concepts | Step 64 `onos_host_evidence_correlator.py` implements an SDN analogue of DAI/IP Source Guard verification: checks single-host vs `AMBIGUOUS_MULTI_HOST` port binding and flags `HOST_IDENTITY_MISMATCH` / `UNREGISTERED_HOST_ON_PORT` when observed L2/L3 headers diverge from ONOS host registry. |
| **Module 10 — Denial-of-Service** | Volumetric/Protocol floods (ICMP/UDP/SYN, pp. 1465–1515); Activity profiling & statistical anomaly detection (pp. 1516–1517); Rate limiting/throttling, ingress filtering (RFC 3704), post-attack forensics (pp. 1518–1530) | Consecutive high-PPS sliding-window detector (`sdn_overlap_alert_monitor_v2.py`); OpenFlow 1.3 Meter throttling (`rate_limit_for_host`, bps->kbps `KB_PER_SEC`); ingress switch-port packet capture forensics (`backend/defense/evidence/*`); post-incident rollback (`/api/defense/rollback`). |
| **Module 12 — Evading IDS, Firewalls & Honeypots** | IDS/IPS alert matrix TP/FP/FN/TN (p. 1635); Snort/Suricata + ELK integration (pp. 1656–1662); Evasion via False Positive Generation / Flooding (pp. 1720–1776); Hardening countermeasures (pp. 1777–1784) | Explicit False-Positive mitigation: `Attached Host != Verified Attacker`, `test_only` immunity, consecutive-sample streak requirement, Step 64 UTC capture-window corroboration, and Honeypot redirection support (`redirect_traffic_full` / `/api/redirectHoney`). |

---

## 4. Academic Submission Format Alignment Note

- **Course PDF (`QUY DINH TRINH BAY BAO CAO BAI TẬP LỚN.pdf`)** specifies a general capstone submission archive layout (`SETUP / SOURCE / THESIS / SOFT / HUONGDAN.PDF`) and Word styling (A4, Times New Roman 13pt, 1.3–1.5 line spacing, margins Top/Bottom/Right 2cm, Left 3cm, TOC depth 3, heading depth 4).
- **Project Delivery Strategy (per user instructions):** This repository (`D:\Project\Nhom02_SDNFlowGuard`) is strictly maintained as the clean **SOURCE** deliverable (zero `.doc`, `.docx`, `.ppt`, `.pptx`, or academic PDFs inside workspace; no `THESIS/` directory). The >60-page Word report will be authored separately outside the code repository.
- **Recommendation for Lecturer Confirmation:** Confirm with the course instructor whether the final zip/drive hand-in should wrap this clean repository inside `SOURCE/` alongside the separate Word report in `THESIS/` and a short `HUONGDAN.PDF`, while excluding `backend/venv/`, `frontend/node_modules/`, `frontend/build/`, `.env`, and `*.bak`.
