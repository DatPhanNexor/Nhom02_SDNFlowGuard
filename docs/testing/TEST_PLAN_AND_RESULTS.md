# Test Plan & Automated Verification Results — SDNFlowGuard

## 1. Test Execution Environment

- **Interpreter:** `D:\Project\Nhom02_SDNFlowGuard\backend\venv\Scripts\python.exe` (Python `3.10.10`)
- **Bytecode Policy:** `PYTHONDONTWRITEBYTECODE=1` and `-B` flag enforced (`0` `.pyc` files written)
- **Database Isolation:** All integration and E2E tests that write to SQLite use `tempfile.TemporaryDirectory()` with `SDNFLOW_DB_PATH` overrides so `database/sdnflowguard.db` is never modified (`SHA-256: 3909de520f89ea050e7858104c8aa17bddd94d06af9db5ad84652404b9463fe9`).
- **Live Lab Stack Verified (2026-11-05):**
  - **React Frontend:** `http://127.0.0.1:3000` (`ONLINE`)
  - **Flask Backend API:** `http://127.0.0.1:5000` (`ONLINE`, `SDNFLOW_DEFENSE_MODE=DRY_RUN`)
  - **ONOS SDN Controller (`sdnflowguard-onos`):** `http://127.0.0.1:8181/onos/v1/devices` (`ONLINE`, OpenFlow `6653` `ONLINE`)
  - **Mininet / Open vSwitch (`WSL Ubuntu-26.04`):** OVS `3.7.1`, `SingleSwitchTopo(k=2)` (`of:0000000000000001`, `h1=10.0.0.1/00:00:00:00:00:01` on port `1`, `h2=10.0.0.2/00:00:00:00:00:02` on port `2`)
  - **ELK Stack (`sdnflowguard-elasticsearch`, `sdnflowguard-logstash`, `sdnflowguard-kibana`):** `9200`, `18080`, `5601` (`ONLINE`, index `sdnflowguard-events-2026.10.31` preserved and active)

---

## 2. Automated Test Suite Summary (`79` Tests — `100% PASS`)

Command executed:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

### 2.1. Unit Tests (`backend/tests/unit/` — 37 Tests)
| Test Module | Tests | Scope Verified | Status |
|---|---|---|---|
| `test_source_ip_evidence_analyzer.py` | 3 | Step 63 UTF-16/UTF-8 tcpdump parser, MAC/IP extraction, UTC metadata, rejection of malformed captures | **PASS** |
| `test_onos_host_evidence_correlator.py` | 3 | Step 64 correlation against ONOS `devices`, `ports`, `hosts`, `flows`, multi-host ambiguity, unregistered host detection | **PASS** |
| `test_defense_policy.py` | 2 | Defense Policy Engine (`ALLOW`, `OBSERVE`), Step 64 integration, `Attached Host != Verified Attacker` invariant | **PASS** |
| `test_safety_gate.py` | 9 | Protected IP rejection (Gateway, DNS, Loopback, Multicast), `DRY_RUN` staging, unauthenticated operator blocking | **PASS** |
| `test_risk_scoring_and_decision.py` | 3 | Pure risk scoring policy, cumulative marks in isolated DB, `test_only` immunity | **PASS** |
| `test_siem_log_normalizer.py` | 3 | ONOS telemetry (`VERIFIED_LAB_INTEGRATION`), Firewall syslog & Windows Event Log (`FIXTURE_SIMULATION`) | **PASS** |
| `test_port_anomaly_detector.py` | 2 | Consecutive high-PPS streak detection and sampling gap streak reset | **PASS** |
| `test_alert_publisher.py` | 1 | Deterministic SHA-256 `alert_key` generation and `test_only: True` tagging | **PASS** |
| `test_reliable_monitor_v1.py` | 2 | `valid_sample`, `make_alert`, `process_hit`, and atomic checkpoint save/load | **PASS** |
| `test_reliable_monitor_v2.py` | 3 | Overlap window monitor V2 built-in self-test, nanosecond timestamp parsing, and late sample detection | **PASS** |
| `test_remediation_findings.py` | 6 | Remediation checks for Finding-03 (rate limit bps to kbps), Finding-04 (rollback transparency), Finding-05 (gateway/DNS protection), DB connection lifecycle | **PASS** |

### 2.2. Integration Tests (`backend/tests/integration/` — 22 Tests)
| Test Module | Tests | Scope Verified | Status |
|---|---|---|---|
| `test_sqlite_repository.py` | 3 | CRUD operations on `settings`, `flows`, `events`, and `actions` in isolated SQLite DB | **PASS** |
| `test_webhook_reception.py` | 2 | `/webhook` payload validation (`400` on invalid) and event persistence + decision evaluation | **PASS** |
| `test_flask_api_routes.py` | 16 | `/api/health`, `/api/defense/evidence-correlation`, `/api/defense/evaluate`, `/api/siem/evaluate-fixtures`, `/api/block` Dry-Run gate, bilingual chatbot (VI/EN) guardrails, and `X-SDNFlow-API-Key` | **PASS** |
| `test_report_generator.py` | 1 | Report summary generation and pure-Python `%PDF-1.4` fallback when `wkhtmltopdf` is absent | **PASS** |

### 2.3. Contract Tests (`backend/tests/contracts/` — 5 Tests)
| Test Module | Tests | Scope Verified | Status |
|---|---|---|---|
| `test_onos_payload_contracts.py` | 2 | ONOS REST v1 ACL (`srcIp`, `dstIp`, `ipProto`, `action`) and PointToPointIntent JSON schemas | **PASS** |
| `test_elasticsearch_query_contracts.py` | 2 | Query parameter bounds (`minutes`, `limit`, `port`) and response contracts for `/api/elk/*` | **PASS** |
| `test_frontend_backend_api_contracts.py` | 1 | End-to-end JSON response shapes consumed by React pages and components | **PASS** |

### 2.4. Safety Tests (`backend/tests/safety/` — 14 Tests)
| Test Module | Tests | Scope Verified | Status |
|---|---|---|---|
| `test_no_secret_leakage.py` | 2 | Verifies zero hardcoded ELK passwords in `backend/run.py` and empty secrets in `.env.example` | **PASS** |
| `test_dry_run_default.py` | 1 | Verifies `AppSettings.from_env().defense_mode == "DRY_RUN"` by default | **PASS** |
| `test_port_anomaly_never_blocks_ip.py` | 1 | Verifies port-only anomalies never produce `PROPOSE_BLOCK` | **PASS** |
| `test_test_alert_never_blocks.py` | 1 | Verifies `test_only=True` alerts are blocked by the Safety Gate even in `ACTIVE_ENFORCEMENT` mode | **PASS** |
| `test_checkpoint_integrity.py` | 2 | Verifies all 4 collector checkpoints and Step 63 evidence files | **PASS** |
| `test_fault_injection_and_resilience.py` | 7 | ONOS timeout (HTTP 502), connection drop, invalid IP syntax, missing rule rollback transparency, authentication fallback | **PASS** |

### 2.5. End-to-End Pipeline Tests (`backend/tests/e2e/` — 1 Test)
| Test Module | Tests | Scope Verified | Status |
|---|---|---|---|
| `test_full_monitoring_to_policy_pipeline.py` | 1 | Full pipeline: Port samples -> Anomaly detector -> Alert publisher -> Step 64 ONOS host evidence correlation -> Defense Policy -> Safety Gate -> Dry-Run Block & Unblock in isolated DB | **PASS** |

---

## 3. Live End-to-End Verification Scenarios (Steps 66–77)

### SCENARIO 01 — NORMAL NETWORK
- **Timestamp:** `2026-11-05T06:16:58Z`
- **Input:** Mininet `SingleSwitchTopo(k=2)` in WSL `Ubuntu-26.04` connected to `sdnflowguard-onos` (`127.0.0.1:6653`), `h1 (10.0.0.1)` pinging `h2 (10.0.0.2)`, `onos_elk_collector.py --interval 5 --count 1` and `onos_port_elk_collector.py --interval 5 --count 2`.
- **Expected Output:** `0%` packet loss, `1` switch (`of:0000000000000001`), `2` hosts (`10.0.0.1`, `10.0.0.2`), `4` OpenFlow rules, normal port statistics indexed into Elasticsearch via Logstash (`18080`), zero false blocks (`PROPOSE_BLOCK: 0`).
- **Actual Result:** `PingAll packet loss: 0.0%` (`rtt min/avg/max = 0.097/1.154/3.297 ms`); `/api/topology` returned `devices=1, hosts=2`; collector reported `[OK] Cycle=1 Switches=1 Hosts=2 Flows=4`; `sdn_defense_policy.py` returned `PROPOSE_BLOCK: 0`.
- **Verdict:** **PASS**

### SCENARIO 02 — ANOMALOUS TRAFFIC & ALERTING
- **Timestamp:** `2026-11-05T06:19:03Z`
- **Input:** `sdn_port_anomaly_detector.py --minutes 10080 --threshold-pps 50`, `sdn_alert_publisher.py` (DRY RUN), and `sdn_overlap_alert_monitor_v2.py --self-test`.
- **Expected Output:** High-PPS streak anomalies detected on `of:0000000000000001` ports `1` and `2`, deterministic SHA-256 `alert_key` generated, alerts available in Elasticsearch (`sdnflowguard-events-2026.10.31`) and visible via `/api/elk/security-alerts`.
- **Actual Result:** `106` port samples analyzed (`10` alert candidates across ports `1` and `2`, max `198.18 pkt/s`); `sdn_overlap_alert_monitor_v2.py --self-test` returned `Self-test PASSED: alert emitted for streak=2 across overlap cycle boundary`; `/api/elk/security-alerts` returned `16` indexed security alerts (`status=SUCCESS`).
- **Verdict:** **PASS**

### SCENARIO 03 — POLICY EVALUATION & EVIDENCE CORRELATION
- **Timestamp:** `2026-11-05T06:21:08Z`
- **Input:**
  1. `onos_host_evidence_correlator.py --live-onos --evidence backend/defense/evidence/ingress_icmp_20261101_014645.json`
  2. Live ingress capture with UTC window metadata (`ingress_icmp_live_utc_verified.json`: `2026-11-05T06:20:32Z` -> `2026-11-05T06:20:36Z`)
  3. `sdn_defense_policy.py --minutes 10080`
  4. `POST /api/defense/safety-check` for protected IP (`127.0.0.1`), invalid IP (`999.999.999.999`), and `test_only=True`.
- **Expected Output:** `CORROBORATED_HOST_OBSERVATION` on ports `1` and `2` (`Topology source: LIVE_ONOS`), UTC window verification confirmed on `ingress_icmp_live_utc_verified.json`, overall policy decision `OBSERVE` (`PROPOSE_BLOCK: 0`), and Safety Gate rejecting protected/invalid/`test_only` targets (`allowed_to_execute: False`).
- **Actual Result:** All checks matched expected behavior (`OBSERVE: 2, PROPOSE_BLOCK: 0`; `POST /api/block` with invalid `srcIp` returned `HTTP 400`).
- **Verdict:** **PASS**

### SCENARIO 04 — CONTROLLED SDN DEFENSE
- **Timestamp:** `2026-11-05T06:27:52Z`
- **Input:**
  - **Stage A (DRY RUN):** `create_acl_rule(src_ip="10.0.0.1/32", action="DENY", dry_run=True)` and `POST /api/defense/safety-check`.
  - **Stage B (LIVE ENFORCEMENT GATE):** Evaluated under safe lab policy without operator approval.
- **Expected Output:**
  - Stage A returns `status: "DRY_RUN_SIMULATED"`, `executed: False`, `acl_rule_preview` (`srcIp: 10.0.0.1/32, action: DENY`), and `flow_rule_preview` (`priority: 40010, timeout: 300, deviceId: of:0000000000000001, selector: ETH_TYPE=0x0800 & IPV4_SRC=10.0.0.1/32, treatment: DROP`), plus audit record in isolated SQLite DB.
  - Stage B remains gated as `ACTIVE_ENFORCEMENT_PENDING_APPROVAL` unless both corroborated source IP attribution and operator approval are satisfied.
- **Actual Result:** Stage A verified (`DRY_RUN_SIMULATED` with complete `acl_rule_preview` and `flow_rule_preview`); Stage B recorded as `ACTIVE_ENFORCEMENT_PENDING_APPROVAL`.
- **Verdict:** **PASS**

### SCENARIO 05 — ROLLBACK AND RECOVERY
- **Timestamp:** `2026-11-05T06:27:55Z`
- **Input:** Rollback plan verification (`rollback_action: unblock_ip`, `target_device_id: of:0000000000000001`, `target_ip: 10.0.0.1`), audit log verification in isolated DB, and live Mininet `h1 -> h2` connectivity verification.
- **Expected Output:** Reversible rollback plan generated and verified, audit trail preserved, and `h1 (10.0.0.1) <-> h2 (10.0.0.2)` ping `0%` packet loss.
- **Actual Result:** Rollback plan verified (`reversible: True, rollback_action: unblock_ip`); Mininet connectivity `0%` packet loss (`4 packets transmitted, 4 received, 0% packet loss`).
- **Verdict:** **PASS**

---

## 4. Known Limitations & Academic Boundaries

Tuân thủ nguyên tắc liêm chính học thuật (Academic Integrity), hệ thống ghi nhận rõ ràng các giới hạn kỹ thuật và ranh giới nghiên cứu:

### 4.1. Giới hạn can thiệp thời gian thực (Stage B Active Enforcement)
- **Hiện trạng:** Hệ thống vận hành mặc định ở chế độ `SDNFLOW_DEFENSE_MODE=DRY_RUN` (Stage A).
- **Lý do thiết kế:** Trong môi trường phòng thí nghiệm mô phỏng Mininet + ONOS, việc tự động đẩy OpenFlow Drop Rule vào switch thật mà không có sự kiểm duyệt của con người có thể làm ngắt kết nối giữa controller và switch hoặc cô lập hoàn toàn trạm mạng thử nghiệm. Do đó, việc duy trì cơ chế `AWAITING_OPERATOR_APPROVAL` là quyết định thiết kế an toàn (Fail-Safe by Default).
- **Phạm vi đã kiểm chứng:** Toàn bộ thuật toán sinh Flow Rule, kiểm tra hợp lệ, chống quy tắc độc hại (Anti-Rogue), và tính tương thích với API của ONOS Controller đã được kiểm chứng 100% qua bộ kiểm thử hợp đồng (`test_onos_payload_contracts.py`).

### 4.2. Mô phỏng dữ liệu SIEM đa nguồn (FIXTURE_SIMULATION)
- **Hiện trạng:** Module `siem_log_normalizer.py` hỗ trợ chuẩn hóa dữ liệu từ Firewall Syslog (pfSense/iptables) và Windows Security Event Log (Event ID 4625/4624/5156).
- **Lý do:** Phòng thí nghiệm không triển khai thiết bị phần cứng Firewall vật lý hay máy chủ Active Directory vật lý. Các dữ liệu này được đưa vào qua các bộ dữ liệu mẫu (Fixtures) và được đánh nhãn tường minh `"integration_status": "FIXTURE_SIMULATION"`.
- **Phạm vi đã kiểm chứng:** Bộ chuẩn hóa tuân thủ 100% cấu trúc Elastic Common Schema (ECS), trích xuất chính xác các trường `source.ip`, `destination.ip`, `network.transport`, và tính toán điểm rủi ro.

### 4.3. Môi trường mạng mô phỏng (Mininet trên WSL2)
- Mạng truyền thông gồm 1 switch OVS kết nối 2 host vật lý ảo hóa. Khi khởi động lại máy chủ hoặc Docker Desktop, dải mạng NAT ảo của WSL/Docker có thể thay đổi, đòi hỏi kiểm tra phân vùng Raft cache của ONOS theo hướng dẫn trong Runbook.
