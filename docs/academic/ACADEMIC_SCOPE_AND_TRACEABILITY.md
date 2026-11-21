# Academic Scope & Requirement Traceability Matrix

**Đề tài:** NGHIÊN CỨU VÀ TRIỂN KHAI PHÒNG THỦ MẠNG TỰ ĐỘNG QUA SDN TÍCH HỢP GIÁM SÁT BẰNG ELK STACK  
**Môn học:** Chuyên đề – Hệ thống mạng và bảo mật  
**Ghi chú đối chiếu tài liệu gốc:** Các tài liệu tham khảo học phần (`Nhom02_PhanPhatDat_Tong_quan_de_tai.docx`, `DeTai.pdf`, `QUY DINH TRINH BAY BAO CAO BAI TẬP LỚN.pdf`, `Chuong 01..05.pdf`, CEH v13) được đối chiếu ở chế độ **chỉ đọc** từ ngoài workspace và không sao chép vào kho mã nguồn. Xem ma trận truy vết chi tiết theo CEH v13 & Bài giảng UTH tại [`docs/audit/REQUIREMENTS_TRACEABILITY.md`](../audit/REQUIREMENTS_TRACEABILITY.md).

---

## 1. Bảng truy vết yêu cầu học thuật (Requirement Traceability Matrix)

| Mã YC | Yêu cầu đề tài | Thành phần hiện thực trong mã nguồn | Bằng chứng / Kiểm thử xác minh | Trạng thái xác minh |
|---|---|---|---|---|
| **REQ-01** | Giám sát an ninh mạng tập trung | `frontend/src/pages/Dashboard.js`, `TrafficOverview.js`, `AnomalyDetection.js`, `backend/run.py` | `test_frontend_backend_api_contracts.py`, `npm.cmd run build` (`EXIT 0`) | **LIVE_VERIFIED / INTEGRATION_TESTED** |
| **REQ-02** | Mô phỏng mạng SDN với ONOS, Open vSwitch và Mininet | `docker-compose.yml`, `infrastructure/mininet/sdnflowguard_lab_topo.py`, `backend/app/topology.py`, WSL2 systemd `sdnflowguard-topo.service` | 6 switches (`s1`..`s6`), 9 hosts (`h1`..`h9`), 10 directed links, 24 flows kết nối ONOS qua OpenFlow 1.3, `pingall` 0.0% packet drop | **LIVE_VERIFIED (Active 6S9H Lab)** |
| **REQ-03** | Quan sát topology, host, switch và flow | `backend/app/topology.py`, `backend/collectors/onos_elk_collector.py`, `frontend/src/pages/LiveSdnSummary.js`, `OnosLiveFlows.js`, `TrafficOverview.js` | `test_topology_service.py`, `test_flask_api_routes.py`, `test_onos_host_evidence_correlator.py`, vis-network 6S9H live canvas | **LIVE_VERIFIED / INTEGRATION_TESTED** |
| **REQ-04** | Thu thập lưu lượng và sự kiện | `backend/collectors/onos_elk_collector.py`, `onos_port_elk_collector.py`, `backend/app/reception.py` | `test_webhook_reception.py`, `test_checkpoint_integrity.py`, 145 docs trong Elasticsearch | **LIVE_VERIFIED (ELK)** / **INTEGRATION_TESTED** |
| **REQ-05** | Tích hợp Elasticsearch, Logstash và Kibana | `docker-compose.yml`, `infrastructure/logstash/pipeline/01-sdnflowguard.conf`, `backend/app/query_elastic.py` | `test_elasticsearch_query_contracts.py`, ES/Logstash/Kibana `UP` | **LIVE_VERIFIED** |
| **REQ-06** | Hiển thị dashboard giám sát, lịch sử, cảnh báo | `frontend/src/pages/SdnPortRates.js`, `frontend/src/components/ElkPortHistoryChart.js`, `SecurityAlertsTable.js` | `test_frontend_backend_api_contracts.py`, React build thành công | **LIVE_VERIFIED / INTEGRATION_TESTED** |
| **REQ-07** | Phát hiện lưu lượng bất thường theo quy tắc | `backend/collectors/sdn_port_anomaly_detector.py`, `sdn_reliable_alert_monitor.py`, `sdn_overlap_alert_monitor_v2.py` | `test_port_anomaly_detector.py`, `test_reliable_monitor_v1.py`, `test_reliable_monitor_v2.py` | **UNIT_TESTED / LIVE_VERIFIED (16 alerts)** |
| **REQ-08** | Phân tích bằng chứng nguồn IP/MAC và thời gian (Step 63 & Step 64) | `backend/defense/source_ip_evidence_analyzer.py`, `backend/defense/onos_host_evidence_correlator.py`, `sdnflowguard/domain/services/evidence_correlation.py` | `test_source_ip_evidence_analyzer.py`, `test_onos_host_evidence_correlator.py` | **LIVE_VERIFIED (Evidence)** / **UNIT_TESTED** |
| **REQ-09** | Đánh giá nguy cơ theo chính sách | `backend/defense/sdn_defense_policy.py`, `backend/app/decision.py`, `sdnflowguard/domain/policies/risk_scoring.py` | `test_defense_policy.py`, `test_risk_scoring_and_decision.py` | **UNIT_TESTED** |
| **REQ-10** | Đề xuất biện pháp phòng thủ có kiểm soát (Safety Gate + Dry-Run Default + Operator Auth) | `sdnflowguard/domain/policies/safety_gate.py`, `sdnflowguard/interfaces/http/security.py`, `backend/app/controller_actions.py`, `frontend/src/pages/ManualTrafficControl.js` | `test_safety_gate.py`, `test_dry_run_default.py`, `test_port_anomaly_never_blocks_ip.py`, `test_test_alert_never_blocks.py`, `test_audit_remediation_hardening.py` | **UNIT_TESTED / INTEGRATION_TESTED** |
| **REQ-11** | Kiểm thử chặn hoặc giới hạn lưu lượng trong mạng lab & xác minh bằng flow/rule thực tế | `backend/app/controller_actions.py`, `sdnflowguard/infrastructure/onos/onos_client.py` (`verify_ip_flow_rule_present`), `docker-compose.yml` (`ONOS_APPS=...acl`) | Payload contract, Dry-Run & ONOS read-back mock đã kiểm chứng (`test_onos_payload_contracts.py`, `test_audit_remediation_hardening.py`); drop gói trực tiếp trên Mininet: **PENDING** khi vận hành lab tương tác | **UNIT_TESTED (DRY_RUN + Mock) / LIVE LAB PENDING** |
| **REQ-12** | Cơ chế rollback hoặc khôi phục | `backend/app/controller_actions.py` (`unblock_ip`), `/api/defense/rollback`, `ManualTrafficControl.js` | `test_full_monitoring_to_policy_pipeline.py`, `test_fault_injection_and_resilience.py`, `test_audit_remediation_hardening.py` | **INTEGRATION_TESTED** |
| **REQ-13** | Nhật ký quyết định và bằng chứng thực nghiệm | `database/sdnflowguard.db` (bảng `actions`, `events`), `DecisionLogs.js`, `backend/defense/evidence/` | `test_sqlite_repository.py`, `test_checkpoint_integrity.py`, đối chiếu SHA-256 100% khớp | **LIVE_VERIFIED (Evidence)** |
| **REQ-14** | Mở rộng định hướng SIEM (Firewall & Windows Server logs) | `sdnflowguard/domain/services/siem_log_normalizer.py`, `/api/siem/evaluate-fixtures`, `AnomalyDetection.js` | `test_siem_log_normalizer.py` (gắn nhãn trung thực `FIXTURE_SIMULATION`) | **FIXTURE_SIMULATED** |
| **REQ-15** | Hướng dẫn tái hiện hệ thống và kiểm thử tự động | `scripts/*.ps1`, `docs/operations/*.md`, `README.md`, `.github/workflows/sdn_flowguard_ci.yml` | `scripts/test.ps1` (`91/91` tests `OK`, `4/4` CLI self-tests `PASS`, `0` `.pyc`) | **INTEGRATION_TESTED** |

---

## 2. Phân biệt rõ các mức độ xác minh trong đề tài

1. **VERIFIED (Đã xác minh bằng dữ liệu thật / kiểm thử tự động):**
   - Thu thập telemetry từ ONOS sang Logstash/Elasticsearch, phát hiện bất thường theo cổng (V1/V2), phân tích gói tin đầu vào switch Step 63 (`ingress_icmp_20261101_014645.txt/.json`), đối chiếu bằng chứng host với topology ONOS Step 64 (`CORROBORATED_HOST_OBSERVATION`), đánh giá chính sách phòng thủ (`OBSERVE`), cổng an toàn Active Defense Safety Gate (`DRY_RUN` mặc định), lưu trữ SQLite và giao diện React.
2. **FIXTURE_SIMULATION (Mô phỏng có cấu trúc bằng dữ liệu mẫu chuẩn hóa):**
   - Bộ chuẩn hóa nhật ký SIEM đa nguồn cho **Firewall Syslog (iptables/pfSense)** và **Windows Server Security Event Log (Event ID 4625/4624/5156)**. Do môi trường lab không có thiết bị Firewall vật lý hay máy chủ Windows Server thật đẩy log trực tiếp, mọi sự kiện chuẩn hóa từ hai nguồn này đều mang trường `"integration_status": "FIXTURE_SIMULATION"`.
3. **PENDING VERIFICATION (Chờ xác minh trên mạng ảo hóa đang chạy):**
   - Thực thi `ACTIVE_ENFORCEMENT` để đẩy ACL/Intent sang ONOS đang chạy và kiểm chứng gói tin bị chặn bằng `ping`/`tcpdump` trực tiếp trên Mininet.

