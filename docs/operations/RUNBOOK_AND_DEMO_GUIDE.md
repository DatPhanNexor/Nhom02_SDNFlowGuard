# Operational Runbook & Live Defense Demonstration Guide

## 1. Pre-Demo Checklist (3 Minutes)

1. Verify environment, container status, and database integrity:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\manage.ps1 -Action check
   ```
2. Create a fresh online SQLite backup before the demonstration:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\backup_database.ps1
   ```
3. Run the automated test suite (`61` tests across Unit, Integration, Contracts, Safety, and E2E):
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
   ```

---

## 2. Scenario A — Offline / Dry-Run Defense Demonstration (Works Anytime, Even Without Docker)

This scenario demonstrates the complete analytical, evidence-correlation, policy, and fail-safe pipeline using the captured lab evidence in `backend/defense/evidence/ingress_icmp_20261101_014645.json`.

### Step 1: Demonstrate Step 63 Switch Ingress Packet Evidence Analysis
```powershell
D:\Project\Nhom02_SDNFlowGuard\backend\venv\Scripts\python.exe -B D:\Project\Nhom02_SDNFlowGuard\backend\defense\source_ip_evidence_analyzer.py `
  --input D:\Project\Nhom02_SDNFlowGuard\backend\defense\evidence\ingress_icmp_20261101_014645.txt `
  --interface s1-eth1:1 `
  --interface s1-eth2:2
```
- **Expected Output:** Parses 24 packets (`s1-eth1` port `1` -> `10.0.0.1` / `00:00:00:00:00:01` echo requests; `s1-eth2` port `2` -> `10.0.0.2` / `00:00:00:00:00:02` echo replies).

### Step 2: Demonstrate Step 64 ONOS Host Evidence Correlation
```powershell
D:\Project\Nhom02_SDNFlowGuard\backend\venv\Scripts\python.exe -B D:\Project\Nhom02_SDNFlowGuard\backend\defense\onos_host_evidence_correlator.py
```
- **Expected Output:**
  - `Port=1 MAC=00:00:00:00:00:01 IP=10.0.0.1 Packets=12 Status=CORROBORATED_HOST_OBSERVATION`
  - `Port=2 MAC=00:00:00:00:00:02 IP=10.0.0.2 Packets=12 Status=CORROBORATED_HOST_OBSERVATION`
  - `Topology corroborated: True`
  - `Historical alert correlation verified: False`
  - `Attacker confirmed: False`
  - `Overall Decision: OBSERVE`
  - `Automatic Block Allowed: False`

### Step 3: Demonstrate Web UI (Flask + React)
1. Start `backend/run.py` and `frontend` (`npm.cmd start`).
2. Open **Dashboard**: Review the system health badges in the Header (`Defense: DRY_RUN`, `API: ONLINE`), network topology, and action distribution.
3. Open **Anomaly Detection**:
   - View **Step 64 ONOS Host Evidence Correlation** table (`CORROBORATED_HOST_OBSERVATION`, `Decision: OBSERVE`).
   - View **SIEM Multi-Source Normalization Matrix** showing `ONOS_SDN_TELEMETRY` (`VERIFIED_LAB_INTEGRATION`) alongside `FIREWALL` and `WINDOWS_SERVER` (`FIXTURE_SIMULATION`).
4. Open **Manual Traffic Control**:
   - Keep **Dry-Run Simulation Mode** checked (default) and submit a Block rule for `10.0.0.1/32` or click **Evaluate Safety Gate**.
   - Show that the Active Defense Safety Gate stages the rule safely (`DRY_RUN_SIMULATED`), logs the decision in **Decision Logs**, and generates the exact ONOS ACL JSON payload without mutating live switch state.

---

## 3. Scenario B — Live SDN + ELK Lab Demonstration (When Docker & Mininet Are Running)

1. Start Docker stack:
   ```powershell
   cd D:\Project\Nhom02_SDNFlowGuard\infrastructure
   docker compose up -d
   ```
2. Run ONOS Port Collector to stream live port counters into Logstash -> Elasticsearch:
   ```powershell
   cd D:\Project\Nhom02_SDNFlowGuard\backend\collectors
   D:\Project\Nhom02_SDNFlowGuard\backend\venv\Scripts\python.exe -B onos_port_elk_collector.py --cycles 12 --interval 10
   ```
3. Run Overlap Alert Monitor V2 in dry-run or test-publish mode:
   ```powershell
   D:\Project\Nhom02_SDNFlowGuard\backend\venv\Scripts\python.exe -B sdn_overlap_alert_monitor_v2.py --cycles 3 --poll-seconds 5 --threshold-pps 4 --consecutive 2
   ```
4. Run Defense Policy Engine with live ONOS + Elasticsearch + Step 64 evidence:
   ```powershell
   cd D:\Project\Nhom02_SDNFlowGuard\backend\defense
   D:\Project\Nhom02_SDNFlowGuard\backend\venv\Scripts\python.exe -B sdn_defense_policy.py --evidence evidence\ingress_icmp_20261101_014645.json
   ```
5. **Controlled Active Block & Rollback Verification (Lab Only):**
   - Only when explicitly demonstrating active blocking on Mininet (`h1 ping h2`), set `SDNFLOW_DEFENSE_MODE=MANUAL_APPROVAL`, uncheck Dry-Run in **Manual Traffic Control**, block `10.0.0.1/32`, verify rule presence on ONOS (`GET /onos/v1/acl/rules` and `GET /onos/v1/flows/of:0000000000000001`), observe ping drop in Mininet, and immediately click **Unblock / Rollback** to restore connectivity.

