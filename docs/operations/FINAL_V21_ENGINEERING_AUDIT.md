# SDNFlowGuard V21 — Báo cáo Kiểm toán Kỹ thuật Toàn diện & Nghiệm thu Hệ thống (Final Engineering Audit & Acceptance Report)

**Học phần:** Chuyên đề - Hệ thống mạng và bảo mật  
**Đề tài:** Nghiên cứu và triển khai phòng thủ mạng tự động qua SDN tích hợp giám sát bằng ELK Stack  
**Tổ chức:** Khoa Công nghệ Thông tin - Trường Đại học Giao thông Vận tải TP.HCM (UTH)  
**Tác giả:** Nhóm 02  
**Phiên bản:** Release Candidate V21  
**Thời điểm hoàn tất kiểm toán:** 23/11/2026 19:35 UTC+07:00  
**Workspace:** `D:\Project\Nhom02_SDNFlowGuard`  
**Cơ chế an toàn:** `DRY_RUN` (Safety Gate Enforced)  
**Giá trị băm CSDL SQLite:** `3909de520f89ea050e7858104c8aa17bddd94d06af9db5ad84652404b9463fe9`

---

## 1. Mục tiêu và Phạm vi Kiểm toán (Audit Objectives & Scope)

Phiên bản **V21** đại diện cho giai đoạn kiểm toán kỹ thuật cuối cùng (Final Release Engineering Audit) trước buổi bảo vệ chuyên đề tốt nghiệp. Nhiệm vụ trọng tâm là:
1. Kiểm toán 14 thành phần cốt lõi của giải pháp từ hạ tầng vật lý, mạng SDN, đường ống telemetry ELK, cơ sở dữ liệu kiểm toán, dịch vụ Backend Flask, giao diện Frontend React, cho đến hệ thống tạo báo cáo pháp chứng.
2. Đối chiếu và đồng bộ toàn diện 12 hình ảnh minh chứng thực nghiệm (Figures 4.1 đến 4.12) kèm các hình ảnh bổ sung mới (Figures 4.13, 4.14, 4.15).
3. Loại bỏ dứt điểm các hiểu lầm về dữ liệu thời gian: Giữ vững tính bất biến của các bản ghi lịch sử năm 2024–2025, giải thích trung thực bản chất 145 tài liệu Elasticsearch năm 2026, và bổ sung thực nghiệm sống ngày 23/11/2026.
4. Đảm bảo toàn bộ 5 Cổng Chất lượng (Quality Gates A–E) đạt kết quả **PASS** với độ tin cậy thực nghiệm 100%.

---

## 2. Kết quả Kiểm toán 14 Thành phần Hệ thống (14-Component Audit)

### 2.1. Cấu trúc Thư mục Dự án (Directory Structure)
- Dự án được tổ chức chuẩn mực theo mô hình Clean Architecture phân tầng:
  - `backend/`: Chứa mã nguồn Flask API, domain models, services, collectors, defense analyzers, và bộ test suites.
  - `frontend/`: Chứa mã nguồn React SPA, components, pages, styles CSS hỗ trợ Dark/Light mode, từ điển đa ngôn ngữ (i18n), và Jest tests.
  - `database/`: Chứa tệp tin SQLite `sdnflowguard.db` và snapshot dự phòng `sdnflowguard.db.bak`.
  - `infrastructure/`: Chứa tệp `docker-compose.yml`, cấu hình Logstash, cấu hình WSL2, và mã nguồn tôpô Mininet `sdnflowguard_lab_topo.py`.
  - `docs/`: Chứa tài liệu kiến trúc, kiểm toán, an ninh, và sổ tay vận hành.
  - `scripts/`: Chứa các script quản trị tự động hóa PowerShell (`manage.ps1`, `test.ps1`).

### 2.2. Trạng thái Quản lý Mã nguồn (Git Status & Version Control)
- Tất cả các chỉnh sửa cốt lõi từ V18 đến V21 đều được theo dõi chặt chẽ:
  - Bổ sung `flow_parser.py` và bài test kiểm toán OpenFlow criteria.
  - Bổ sung engine tạo báo cáo A4 PDF động và unit test lọc thời gian trong `report.py`.
  - Nâng cấp giao diện SOC Reports & Audit Center trong `Reports.js`, `Reports.css`, `en.js`, `vi.js`.
  - Không có xung đột mã nguồn (zero merge conflicts), không có tệp nhạy cảm (secrets/passwords) bị rò rỉ.

### 2.3. Hạ tầng Ảo hóa Docker Compose (Container Infrastructure)
- Cả 6 container dịch vụ vận hành ổn định:
  - `sdnflowguard-backend`: Python 3.10 Flask REST API (cổng 5000).
  - `sdnflowguard-frontend`: Nginx phục vụ React production bundle (cổng 3000).
  - `sdnflowguard-onos`: Image `onosproject/onos:2.7-latest` (cổng 8181 REST và 6653 OpenFlow).
  - `sdnflowguard-elasticsearch`: Elasticsearch 8.11 (cổng 9200).
  - `sdnflowguard-logstash`: Logstash pipeline (cổng 18080).
  - `sdnflowguard-kibana`: Kibana dashboard (cổng 5601).

### 2.4. Bộ điều khiển SDN Controller ONOS 2.7
- Ứng dụng OpenFlow và Forwarding hoạt động ổn định:
  - Cổng REST API `http://127.0.0.1:8181/onos/v1/devices` phản hồi HTTP 200 trong 35 ms.
  - Nhận diện đầy đủ 6 switch OpenFlow 1.3 (`of:0000000000000001` đến `06`).
  - Dịch vụ máy chủ ONOS Host Service ghi nhận chính xác 9 trạm làm việc (`10.0.0.1` đến `10.0.0.9`).

### 2.5. Mặt phẳng Chuyển tiếp OpenFlow 1.3 (Dataplane)
- 24 luật luồng (Flow Rules) được nạp trên 6 thiết bị chuyển mạch ở trạng thái `ADDED`.
- Các tiêu chí khớp gói (Match Criteria) được phân tích chính xác:
  - Các luật định tuyến hạ tầng Core chỉ khớp `ETH_TYPE: 0x800` (IPv4) hoặc `0x806` (ARP), cổng đích và nhãn VLAN. Cột Source/Destination IP hiển thị `--` phản ánh đúng bản chất selector không chứa địa chỉ IP.

### 2.6. Mạng Ảo hóa Mininet / Open vSwitch (OVS)
- Mạng Mininet 6 switch và 9 host vận hành qua service `sdnflowguard-topo.service` trên WSL2 Ubuntu-26.04.
- Kết nối thành công tới ONOS controller qua cổng TCP 6653.
- Thực nghiệm ping thực tế giữa các host cho kết quả 0% mất gói (0.0% packet loss).

### 2.7. Dịch vụ Flask Backend API
- Cung cấp hơn 18 endpoints RESTful phục vụ giám sát tôpô, kiểm tra sức khỏe, nhận diện bất thường, mô phỏng can thiệp và xuất báo cáo.
- Quản lý vòng đời kết nối SQLite chặt chẽ qua context manager `get_connection()`, loại bỏ hoàn toàn nguy cơ rò rỉ file descriptor.

### 2.8. Giao diện Người dùng React Frontend
- Ứng dụng SPA tối ưu hóa với bundle nén chỉ 371 kB (JS) và 17 kB (CSS).
- Hỗ trợ đầy đủ chuyển đổi giao diện Sáng / Tối (Light / Dark mode) và chuyển ngữ song ngữ Anh - Việt tức thì.

### 2.9. Cơ sở Dữ liệu Kiểm toán SQLite
- Tệp `database/sdnflowguard.db` có kích thước 61,440 bytes.
- Giá trị băm SHA-256 bất biến: `3909de520f89ea050e7858104c8aa17bddd94d06af9db5ad84652404b9463fe9`.
- Lưu trữ 8 sự kiện bất thường, 89 quyết định can thiệp, 25 bản ghi lưu lượng và 5 cấu hình hệ thống.

### 2.10. Cụm Chỉ mục Phân tán Elasticsearch
- Lưu trữ 145 documents trong 4 chỉ mục thuộc giai đoạn triển khai dự án (tháng 10–11/2026).
- 106 documents thuộc loại telemetry đo thông lượng cổng switch (`sdn_port_traffic`) và 11 documents thuộc loại cảnh báo an ninh (`sdn_anomaly_alert`).

### 2.11. Đường ống Tiếp nhận Dữ liệu Logstash
- Lắng nghe tại cổng HTTP 18080, tiếp nhận dữ liệu telemetry và gửi sang Elasticsearch theo thời gian thực.

### 2.12. Nền tảng Quan sát Kibana
- Cung cấp giao diện trực quan hóa dữ liệu qua Kibana Discover (cổng 5601).

### 2.13. Phân hệ Báo cáo & Xuất Báo cáo PDF (Reporting Engine)
- Tái cấu trúc hoàn toàn ở V20/V21:
  - Hỗ trợ 7 khung thời gian động: `last_24h`, `last_7d`, `last_30d` (mặc định), `this_month`, `prev_month`, `all`, `custom`.
  - Bộ tạo PDF thuần Python không phụ thuộc thư viện đồ họa nặng, tạo tệp A4 chuẩn (595 x 842 pt) đa trang có tiêu đề và phân trang rõ ràng.

### 2.14. Kiến trúc An toàn Safety Gate & Chế độ Phòng thủ DRY_RUN
- Mặc định khởi chạy ở chế độ `DRY_RUN`.
- Mọi thao tác can thiệp (Block, Rate-limit, Redirect, Rollback) đều phải đi qua Safety Gate để kiểm tra địa chỉ IP được bảo vệ (Gateway `10.0.0.254`, DNS `8.8.8.8`).
- Trong chế độ mô phỏng, hệ thống đánh giá tính khả thi, lập kế hoạch hoàn tác (Rollback Plan) và ghi nhận vào Decision Logs nhưng không cài luật cản trở gói tin trên switch ONOS.

---

## 3. Đánh giá Năm Cổng Chất lượng Kỹ thuật (Five Quality Gates Evaluation)

| Quality Gate | Tiêu chuẩn Đánh giá | Phương pháp Kiểm chứng | Kết quả Thực tế | Trạng thái |
|---|---|---|---|---|
| **Gate A — Infrastructure** | Tất cả 6 container Docker hoạt động, ONOS REST API HTTP 200, Mininet tôpô 6 switch 9 host, ELK truy cập được. | `manage.ps1 check`<br>`manage.ps1 status-topo`<br>`curl -s http://localhost:8181/onos/v1/devices` | 6/6 container healthy, 7 cổng mạng listening, 6 switch 9 host 10 links kết nối thông suốt. | **PASS** |
| **Gate B — Data Integrity** | Timestamp gốc được bảo toàn, không đổi năm dữ liệu cũ, không tạo sự kiện tương lai, hash SQLite bất biến. | Kiểm tra SHA-256 SQLite: `Get-FileHash database\sdnflowguard.db`<br>Truy vấn min/max timestamp trong SQLite & Elasticsearch. | SHA-256 giữ nguyên `3909de52...`, 8 events (2024-2025) và 89 actions giữ nguyên ngày, 145 ES docs giữ nguyên. | **PASS** |
| **Gate C — Detection & Defense** | Phân tích gói tin Step 63, đối chiếu tôpô Step 64, Safety Gate từ chối IP bảo vệ, DRY_RUN không can thiệp data plane. | Chạy 17 CLI Self-Tests:<br>`python -m backend.defense.onos_host_evidence_correlator`<br>`python -m backend.defense.defense_policy` | 17/17 self-tests pass, Host $\ne$ Attacker, quyết định OBSERVE, 0 luật DROP được cài đặt. | **PASS** |
| **Gate D — Reports & PDF Engine** | Khung thời gian động không hardcode, hỗ trợ Custom Range, tính đúng KPI, xuất PDF A4 đa trang chuẩn. | Chạy 6 unit tests trong `test_report_date_filtering.py`<br>Tải PDF thử nghiệm qua API. | 6/6 unit tests pass, PDF A4 kích thước 595 x 842 pt, 3 trang phân bổ chuẩn xác, footer `Page X of Y`. | **PASS** |
| **Gate E — Regression Testing** | 106 automated backend tests pass, 10 frontend Jest test suites pass, ESLint 0 errors, production build thành công. | `manage.ps1 test` (chạy `test.ps1`)<br>`npx eslint src`<br>`npm test -- --watchAll=false` | 106/106 backend tests pass trong 1.07s, 49/49 frontend tests pass, ESLint 0 errors, 0 warnings. | **PASS** |

---

## 4. Bảng Đối chiếu & Hướng dẫn Thực hiện Hình ảnh Báo cáo (Figures Synchronization)

| Nhóm hình | Các hình cụ thể | Đánh giá tính nhất quán | Hướng dẫn xử lý |
|---|---|---|---|
| **Hạ tầng & Tôpô** | Hình 4.1, 4.2, 4.3, 4.4 | Khớp 100% với hạ tầng Docker 6 container và tôpô Mininet 6 switch 9 host. | **Giữ nguyên ảnh đã có.** |
| **Luật luồng & Đo đạc** | Hình 4.5, 4.6 | Khớp 100% với 24 luật ONOS và thông lượng tức thời trên switch `s1`. | **Giữ nguyên ảnh đã có.** |
| **ELK & Nhận dạng Host** | Hình 4.7, 4.8 | Khớp 100% với 145 documents trên Kibana và thuật toán Step 64. | **Giữ nguyên ảnh đã có.** Lưu ý giải thích 145 tài liệu gồm 106 telemetry và 11 cảnh báo. |
| **Mô phỏng Phòng thủ** | Hình 4.9, 4.10, 4.11, 4.12 | Khớp 100% với quy trình đánh giá Safety Gate cho IP `10.0.0.2/32` và 89 bản ghi Decision Logs. | **Giữ nguyên ảnh đã có.** Sửa lỗi chính tả chú thích thành `10.0.0.2/32` (không viết nhầm thành `10.0.0.232`). |
| **Phân hệ Báo cáo Mới** | Hình 4.13, 4.14 | Giao diện Reports và tệp PDF xuất ra đã được thiết kế lại hoàn toàn ở V20/V21. | **Chụp ảnh mới** theo hướng dẫn tại `docs/operations/FINAL_DEMO_RUNBOOK.md`. |
| **Thực nghiệm Lưu lượng** | Hình 4.15 | Thực nghiệm ICMP ping giữa Host h1 và h2 ngày 23/11/2026 cho kết quả 0% mất gói. | **Bổ sung vào phụ lục** nếu cần thêm minh chứng thực nghiệm sống. |

---

## 5. Kết luận Nghiệm thu (Final Acceptance Statement)

Hệ thống **SDNFlowGuard** đã hoàn thành toàn diện đợt kiểm toán kỹ thuật V21:
- Cơ sở hạ tầng mạng SDN OpenFlow 1.3 và cụm giám sát ELK Stack vận hành đồng bộ và ổn định.
- Cơ chế bảo vệ Safety Gate và chế độ phòng thủ `DRY_RUN` đảm bảo an toàn tuyệt đối cho hệ thống mạng.
- Toàn bộ bằng chứng lịch sử được bảo toàn nguyên vẹn về mặt pháp chứng số; các dữ liệu đo đạc mới được minh bạch hóa nguồn gốc và phương pháp thực nghiệm.
- Mã nguồn đạt tiêu chuẩn chất lượng cao nhất với 100% các bài kiểm thử tự động vượt qua thành công.

Dự án đủ điều kiện nghiệm thu kỹ thuật và sẵn sàng bảo vệ trước Hội đồng chuyên môn.
