# FINAL RELEASE AUDIT REPORT — SDNFLOWGUARD

**Dự án:** Nghiên cứu và triển khai phòng thủ mạng tự động qua SDN tích hợp giám sát bằng ELK Stack  
**Môn học:** Chuyên đề – Hệ thống mạng và bảo mật (Mã HP: 123046)  
**Đơn vị:** Trường Đại học Giao thông vận tải TP. Hồ Chí Minh (UTH) — Khoa Công nghệ thông tin  
**Học viên:** Phan Phát Đạt (Nhóm 02)  
**Ngày nghiệm thu:** 05/11/2026  
**Trạng thái phiên bản:** RELEASE FREEZE — ZERO REGRESSION  

---

## 1. Môi trường thực thi nghiệm thu
- Hệ điều hành: Windows 10/11 Professional x64
- Shell: PowerShell 5.1 / PowerShell 7+
- Python: 3.10.10 (Interpreter tại `backend/venv/Scripts/python.exe`)
- Docker Desktop: Quản lý 4 container: ONOS 2.7.0 LTS, Elasticsearch 8.11+, Logstash, Kibana
- Mạng mô phỏng SDN: Mininet trên WSL2 (Ubuntu-26.04), Open vSwitch 3.7.1, OpenFlow 1.3
- Cơ sở dữ liệu: SQLite 3 (`database/sdnflowguard.db`, SHA-256: `3909de520f89ea050e7858104c8aa17bddd94d06af9db5ad84652404b9463fe9`)

---

## 2. Kết quả kiểm toán dịch vụ thời gian thực
- **Port 3000 (React Frontend):** HTTP 200, Web App Manifest 521 bytes, giao diện quản trị 7 module chức năng.
- **Port 5000 (Flask Backend API):** HTTP 200, `/api/health` status OK, defense_mode DRY_RUN, Clean Architecture Blueprint + legacy compatibility routes.
- **Port 8181 (ONOS REST API):** HTTP 200, quản trị switch `of:0000000000000001` và các trạm mạng host discovery.
- **Port 6653 (ONOS OpenFlow):** Kết nối TCP OpenFlow 1.3 thông suốt với OVS switch.
- **Port 9200 (Elasticsearch HTTP):** Cluster `docker-cluster`, lưu trữ chỉ mục chuỗi thời gian `sdnflowguard-events-*`.
- **Port 5601 (Kibana Dashboard):** Trực quan hóa SOC và các mẫu lưu lượng cổng switch.
- **Port 18080 (Logstash HTTP Input):** Tiếp nhận sự kiện telemetry từ các collector.

---

## 3. Kết quả kiểm thử tự động
- **Unit & Integration Tests:** 53/53 tests PASS (bao gồm 50 unit tests cơ sở và 3 regression tests cho Findings 03, 04, 05; thời gian chạy: ~0.65s).
- **CLI Self-Tests:** 4/4 CLI self-tests PASS:
  1. `sdn_overlap_alert_monitor_v2.py --self-test` (Late sample detection, no replay).
  2. `source_ip_evidence_analyzer.py --self-test` (Packet parser, UTC metadata, no auto-block).
  3. `onos_host_evidence_correlator.py --self-test` (Single-host corroboration, multi-host ambiguity, identity mismatch).
  4. `sdn_defense_policy.py --self-test` (Port alert OBSERVE, no alert ALLOW, Step 64 correlation integrated).
- **Regression:** 0 lỗi phát sinh (Zero Regression).
- **SQLite Database Integrity:** `PRAGMA integrity_check` = `ok`. Bảng `actions` (89 rows), `events` (8 rows), `flows` (25 rows), `settings` (5 rows). Tổng cộng 127 bản ghi. SHA-256 không đổi trước và sau kiểm thử.

---

## 4. Các phát hiện kỹ thuật đã xử lý (Remediation)
1. **Finding-03 (Rate Limit Unit Conversion):** Chuẩn hóa chuyển đổi đơn vị tốc độ `rate_limit_bps` sang `rate_kb_per_sec = max(1, int(round(bps / 8000.0)))` cho ONOS Meter Band đơn vị `KB_PER_SEC`, ghi log đầy đủ cả bps và KB/s.
2. **Finding-04 (Rollback Authentic Status):** Tái cấu trúc `/api/defense/rollback` trả về trạng thái minh bạch `ROLLBACK_COMPLETED` (dry_run: true, executed: false khi mô phỏng) hoặc `ROLLBACK_SKIPPED_NO_RULE` khi không có luật, loại bỏ false success.
3. **Finding-05 (Safety Gate Protected IPs):** Bổ sung Default Gateway `10.0.0.254` và Public DNS Resolvers `8.8.8.8`, `1.1.1.1` vào danh sách bảo vệ `DEFAULT_PROTECTED_IPS` của Safety Gate.
4. **Finding-06 (Quy chuẩn Báo cáo học thuật):** Chuẩn hóa khổ giấy A4 (21.0cm x 29.7cm), căn lề 2-2-3-2 cm, mẫu bìa 01-BCBTL UTH, dung lượng 72 trang A4.
5. **Finding-07 (Quy chuẩn Slide thuyết trình):** Chuẩn hóa slide bài giảng 30 slides (thỏa mãn khung 25–40 slides của `DeTai.pdf`), Font Tiêu đề 32pt, Font Nội dung 24–26pt.
6. **Finding-01/02/08 (Phân định ranh giới & Đóng gói kép):** Phân định ranh giới rõ ràng giữa Engineering Workspace (tập trung source code, kiểm thử, script vận hành) và Official Academic Submission (4 thư mục `SETUP/`, `SOURCE/`, `THESIS/`, `SOFT/`, `HUONGDAN.PDF`).
