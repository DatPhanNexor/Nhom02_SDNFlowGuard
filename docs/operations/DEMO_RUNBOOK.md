# SDNFlowGuard — Complete Demonstration & Defense Verification Runbook
## Học phần: Chuyên đề - Hệ thống mạng và bảo mật
## Đề tài: Nghiên cứu và triển khai phòng thủ mạng tự động qua SDN tích hợp giám sát bằng ELK Stack

---

## MỤC LỤC
1. [Giới thiệu và Phạm vi tài liệu](#1-giới-thiệu-và-phạm-vi-tài-liệu)
2. [Phần A: Quy trình khởi động hệ thống (Cold Start to System Ready)](#phần-a-quy-trình-khởi-động-hệ-thống)
3. [Phần B: Kịch bản thuyết minh 11 màn hình chi tiết (Screens 01 – 11)](#phần-b-kịch-bản-thuyết-minh-11-màn-hình-chi-tiết)
   - [Màn hình 01: Tổng quan điều hành NOC/SOC (Dashboard)](#màn-hình-01-dashboard)
   - [Màn hình 02: Giám sát lưu lượng & Topo mạng SDN (Traffic Overview)](#màn-hình-02-traffic-overview)
   - [Màn hình 03: Phát hiện bất thường & Đối soát bằng chứng (Anomaly Detection)](#màn-hình-03-anomaly-detection)
   - [Màn hình 04: Điều khiển lưu lượng thủ công & Safety Gate (Manual Traffic Control)](#màn-hình-04-manual-traffic-control)
   - [Màn hình 05: Nhật ký kiểm toán quyết định chính sách (Decision Logs)](#màn-hình-05-decision-logs)
   - [Màn hình 06: Xuất báo cáo pháp chứng an ninh (Reports)](#màn-hình-06-reports)
   - [Màn hình 07: Cấu hình hệ thống & Độ nhạy (System Settings)](#màn-hình-07-system-settings)
   - [Màn hình 08: Quản trị hạ tầng Container (Docker Desktop)](#màn-hình-08-docker-desktop)
   - [Màn hình 09: Nền tảng phân tích nhật ký SIEM (Kibana)](#màn-hình-09-kibana)
   - [Màn hình 10: Bộ điều khiển mạng SDN trung tâm (ONOS Controller)](#màn-hình-10-onos-controller)
   - [Màn hình 11: Đặc tả giao diện lập trình backend (Backend REST API Docs)](#màn-hình-11-backend-rest-api-docs)
4. [Phần C: Kịch bản kiểm chứng phòng thủ mạng (Defense Verification Runbook)](#phần-c-kịch-bản-kiểm-chứng-phòng-thủ-mạng)
   - [Cấp độ 1: Trình diễn kiểm chứng an toàn mặc định (DRY_RUN Default)](#cấp-độ-1-trình-diễn-kiểm-chứng-an-toàn-mặc-định)
   - [Cấp độ 2: Thực nghiệm can thiệp Dataplane có cô lập & Phục hồi (Isolated Live Dataplane)](#cấp-độ-2-thực-nghiệm-can-thiệp-dataplane-có-cô-lập)
5. [Phần D: Quy trình tắt máy và khởi động lại an toàn (Safe Shutdown & Restart)](#phần-d-quy-trình-tắt-máy-và-khởi-động-lại-an-toàn)

---

## 1. GIỚI THIỆU VÀ PHẠM VI TÀI LIỆU

Tài liệu này được biên soạn dành cho sinh viên thực hiện báo cáo nghiệm thu đồ án **Chuyên đề - Hệ thống mạng và bảo mật**. Tài liệu cung cấp toàn bộ các lệnh kiểm tra, kịch bản thao tác, lời thuyết minh song ngữ kỹ thuật, bộ câu hỏi - trả lời phản biện của Hội đồng chấm thi, cùng phương án xử lý sự cố dự phòng (fallback) cho 11 giao diện của hệ thống **SDNFlowGuard**.

### Kiến trúc tổng thể hệ thống:
```
+-----------------------------------------------------------------------------------+
|                            HẠ TẦNG MẠNG DỮ LIỆU (DATAPLANE)                       |
|   Mininet (WSL2 Ubuntu-26.04) — 6 Open vSwitch (s1-s6) + 9 Virtual Hosts (h1-h9)  |
+-----------------------------------------------------------------------------------+
                                         │  OpenFlow 1.3 (TCP 6653)
                                         ▼
+-----------------------------------------------------------------------------------+
|                        TẦNG ĐIỀU KHIỂN SDN (CONTROL PLANE)                        |
|   ONOS Controller v2.7 (Docker: sdnflowguard-onos) — REST API (TCP 8181)           |
+-----------------------------------------------------------------------------------+
             ▲                                                   │
             │ REST (Flows, Intents, Meters)                     │ Ingress Samples
             ▼                                                   ▼
+------------------------------------------+   +------------------------------------+
|         SDNFLOWGUARD BACKEND             |   |         HẠ TẦNG SIEM / ELK         |
|   Python Flask + Gunicorn (TCP 5000)     |   |   Logstash (18080) -> ES (9200)    |
|   - Safety Gate & Policy Engine          |   |   Kibana UI (5601)                 |
|   - SQLite Repository (sdnflowguard.db)  |   |   - 145 tài liệu kiểm toán sự kiện |
+------------------------------------------+   +------------------------------------+
                     ▲
                     │ JSON REST API (Proxy: localhost:3000 -> localhost:5000)
                     ▼
+-----------------------------------------------------------------------------------+
|                        GIAO DIỆN ĐIỀU HÀNH NOC/SOC (MANAGEMENT)                   |
|   React 18 SPA + Nginx (Docker: sdnflowguard-frontend, TCP 3000)                  |
|   - 3-Mode Theme (Light/Dark/System), Song ngữ (VI/EN), WCAG 2.2 Đạt chuẩn         |
+-----------------------------------------------------------------------------------+
```

---

## PHẦN A: QUY TRÌNH KHỞI ĐỘNG HỆ THỐNG
*(Thực hiện từ 10 đến 15 phút trước khi bắt đầu phiên báo cáo)*

### Bước 1: Khởi động Docker Desktop & Kiểm tra Docker Engine
1. Mở ứng dụng **Docker Desktop** trên Windows. Chờ thanh trạng thái chuyển sang màu xanh lá cây (**Engine running**).
2. Mở cửa sổ **PowerShell** (Run as Administrator) và kiểm tra:
   ```powershell
   docker info --format '{{.ServerVersion}}'
   ```
   *Kết quả mong đợi:* Trả về phiên bản Docker (vd: `27.x.x` hoặc tương đương).

### Bước 2: Kiểm tra và Khởi chạy Docker Stack SDNFlowGuard
1. Điều hướng vào thư mục dự án:
   ```powershell
   Set-Location D:\Project\Nhom02_SDNFlowGuard
   ```
2. Kiểm tra trạng thái 6 container:
   ```powershell
   docker compose ps
   ```
   *Kết quả mong đợi:* Cả 6 dịch vụ đều ở trạng thái `Up`:
   - `sdnflowguard-backend` (port 127.0.0.1:5000)
   - `sdnflowguard-frontend` (port 127.0.0.1:3000)
   - `sdnflowguard-onos` (port 127.0.0.1:6653, 127.0.0.1:8181)
   - `sdnflowguard-elasticsearch` (port 127.0.0.1:9200)
   - `sdnflowguard-logstash` (port 127.0.0.1:18080)
   - `sdnflowguard-kibana` (port 127.0.0.1:5601)
3. Nếu container chưa chạy, khởi động bằng lệnh:
   ```powershell
   docker compose up -d
   ```
   *(Tuyệt đối không sử dụng cờ `-v` để tránh xóa dữ liệu volume SQLite và Elasticsearch)*.

### Bước 3: Kiểm tra WSL2 và Dịch vụ Giả lập Mininet
1. Kiểm tra distro WSL2:
   ```powershell
   wsl --list --verbose
   ```
   *Kết quả:* Phải thấy `Ubuntu-26.04` ở trạng thái `Running` (Version 2).
2. Kiểm tra dịch vụ mạng SDN Mininet bên trong WSL2:
   ```powershell
   wsl -d Ubuntu-26.04 systemctl status sdnflowguard-topo.service --no-pager
   ```
   *Kết quả mong đợi:* `Active: active (running)`. Topology đang chạy gồm 6 Open vSwitch (`s1` đến `s6`) và 9 host (`h1` đến `h9`), kết nối thành công tới ONOS controller tại `127.0.0.1:6653`.
3. Nếu dịch vụ chưa chạy, khởi động lại service:
   ```powershell
   wsl -d Ubuntu-26.04 sudo systemctl start sdnflowguard-topo.service
   ```

### Bước 4: Kiểm tra tính sẵn sàng của Backend & Bộ điều khiển ONOS
1. Kiểm tra Backend API Health:
   ```powershell
   Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/health' | ConvertTo-Json
   ```
   *Kết quả mong đợi:*
   ```json
   {
     "status": "OK",
     "defense_mode": "DRY_RUN",
     "database_exists": true,
     "step63_evidence_present": true,
     "version": "2.0.0"
   }
   ```
2. Kiểm tra ONOS Topology qua Backend REST:
   ```powershell
   Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/topology' | Select-Object -ExpandProperty devices
   ```
   *Kết quả mong đợi:* 6 thiết bị chuyển mạch (`of:0000000000000001` đến `of:0000000000000006`) với trạng thái `available: true`.

### Bước 5: Mở Trình duyệt Chrome vào Giao diện Điều hành
1. Mở Google Chrome và truy cập: `http://localhost:3000`.
2. Kiểm tra thanh trạng thái đầu trang (Top Navigation Bar):
   - Nút chuyển ngôn ngữ: `VI | EN` hoạt động bình thường.
   - Bộ chuyển theme 3 chế độ: `Sáng / Tối / Hệ thống` (mặc định Dark Mode chuẩn NOC/SOC).
   - Huy hiệu an toàn: `Defense Mode: DRY_RUN` (Màu xanh Teal).
   - Huy hiệu kết nối: `API: ONLINE` (Màu xanh lá cây nhấp nháy đồng bộ).

---

## PHẦN B: KỊCH BẢN THUYẾT MINH 11 MÀN HÌNH CHI TIẾT

---

### MÀN HÌNH 01: DASHBOARD
- **Địa chỉ truy cập:** `http://localhost:3000/` hoặc click mục `Dashboard` trên Sidebar.
- **Thao tác trình diễn:**
  1. Giới thiệu 4 KPI cards trên hàng đầu:
     - `6 Connected Switches` (OpenFlow 1.3 qua ONOS REST).
     - `9 Connected Hosts` (Định danh học được qua ARP/LLDP).
     - `24 Flow Rules` (Quy tắc luồng nạp trên 6 switch).
     - `0 Security Alerts (24h)` (Số lượng vi phạm ngưỡng trong khung thời gian).
  2. Chỉ vào card **Live SDN Port Throughput**:
     - Bấm nút `Refresh Ports`.
     - Cho Hội đồng thấy thông số băng thông tức thời được tính toán từ bộ đếm byte phần cứng (`port.bytes_rx`, `port.bytes_tx`) chia cho khoảng thời gian lấy mẫu `5.0s`.
  3. Chỉ vào card **ELK Traffic History**:
     - Giải thích rõ: Phần đồ thị này truy vấn trực tiếp Elasticsearch index `sdnflowguard-events-*` với bộ lọc thời gian `gte: now - 4h`.
     - *Lưu ý khoa học:* Khung 4 giờ hiện tại hiển thị 0 samples vì các đợt phát sinh mẫu vi phạm nghiên cứu thực nghiệm được ghi nhận vào giai đoạn kiểm thử 31/10 – 08/11/2026.
  4. Chỉ vào card **Stored Flow Traffic**:
     - Đồ thị 25 phiên luồng lịch sử được trích xuất từ cơ sở dữ liệu SQLite cục bộ `sdnflowguard.db`.
- **Lời thuyết minh mẫu:**
  > "Kính thưa Hội đồng, đây là giao diện giám sát trung tâm NOC/SOC của SDNFlowGuard. Hệ thống phân tách mạch lạc hai luồng đo: phía trên là băng thông thời gian thực lấy trực tiếp từ controller ONOS theo chu kỳ 5 giây, phía dưới là dữ liệu pháp chứng được đồng bộ vào ELK Stack và SQLite. Cơ chế này đảm bảo người vận hành vừa có cái nhìn tức thời về dataplane, vừa có đầy đủ dữ liệu lịch sử để điều tra nguồn gốc tấn công."
- **Câu hỏi Hội đồng & Cách trả lời:**
  - *Hỏi:* Tại sao đồ thị ELK Traffic History lại không có số liệu trong 4 giờ qua trong khi Live Port lại có?
  - *Đáp:* "Thưa Thầy/Cô, Live Port Throughput truy vấn trực tiếp bộ đếm phần cứng OpenFlow của switch đang chạy nên luôn phản ánh lưu lượng thực tế hiện tại. Trong khi đó, ELK Traffic History truy vấn các bản ghi sự kiện bất thường được Logstash gửi sang Elasticsearch theo mốc thời gian UTC thực. Khi không có kịch bản tấn công kích hoạt ngưỡng trong 4 giờ qua, hệ thống không ghi nhận cảnh báo mới, thể hiện đúng tính trung thực của dữ liệu mà không dùng dữ liệu mô phỏng giả lập."
- **Phương án dự phòng (Fallback):** Nếu API báo mất kết nối, kiểm tra container `sdnflowguard-backend` bằng lệnh `docker compose logs --tail=20 backend`.

---

### MÀN HÌNH 02: TRAFFIC OVERVIEW
- **Địa chỉ truy cập:** `http://localhost:3000/traffic-overview`.
- **Thao tác trình diễn:**
  1. Trình diễn tương tác trên canvas đồ họa topo mạng (**vis-network**):
     - Bấm nút `Phóng to (+)` và `Thu nhỏ (-)`.
     - Bấm nút `Vừa khung nhìn (Fit)` để đưa toàn bộ 6 switch và 9 host về chính giữa màn hình.
     - Kéo thả một node switch để chứng minh đồ thị có lực vật lý (Physics engine), sau đó bấm `Tắt lực đẩy (Physics)` để cố định bố cục.
  2. Bấm toggle `Chỉ thiết bị hoạt động (Active Only)` vs `Tất cả thiết bị (All Devices)`.
  3. Cuộn xuống bảng **Quy tắc luồng thời gian thực (Live ONOS Flow Rules)**:
     - Giải thích các cột: `Device ID`, `Priority`, `App ID`, `State: ADDED`, `Packets`, `Flow Bytes`, `Output Port`.
     - Chỉ ra các luồng cốt lõi của ONOS (`org.onosproject.core`, priority 40000) chuyển tiếp gói lên cổng CONTROLLER để xử lý ARP/LLDP.
- **Lời thuyết minh mẫu:**
  > "Màn hình Traffic Overview trực quan hóa toàn bộ topo 6 thiết bị chuyển mạch và 9 trạm làm việc được khám phá tự động qua giao thức OpenFlow 1.3. Mỗi switch hiển thị rõ DPID và trạng thái Master Controller. Bảng Live Flow bên dưới phản ánh trung thực trạng thái bảng luồng OpenFlow Flow Table, các giá trị gói tin và byte là bộ đếm phần cứng tích lũy thực tế."
- **Câu hỏi Hội đồng & Cách trả lời:**
  - *Hỏi:* vis-network có làm chậm giao diện khi topo có hàng trăm thiết bị không?
  - *Đáp:* "Hệ thống đã triển khai cơ chế tính toán Topology Hash. Khi dữ liệu thiết bị không thay đổi trạng thái, vis-network sẽ tái sử dụng cấu trúc Canvas hiện có mà không phá hủy đối tượng DOM, kết hợp tính năng tắt Physics để tối ưu hóa hiệu năng render đồ họa."

---

### MÀN HÌNH 03: ANOMALY DETECTION
- **Địa chỉ truy cập:** `http://localhost:3000/anomaly-detection`.
- **Thao tác trình diễn:**
  1. Chỉ vào huy hiệu điều phối: `Detection: ONLINE`, `Source: ONOS + SIEM + SQLite`, `Defense Mode: DRY_RUN`.
  2. Phần **Packet Evidence & ONOS Host Topology Correlation**:
     - Cho Hội đồng xem tệp bằng chứng gói tin: `ingress_icmp_20261101_014645.json` (Trích xuất từ kịch bản tấn công Step 63).
     - Huy hiệu góc phải: `Đối soát gói tin & Định danh ONOS Host` (với tooltip kỹ thuật `onos_host_correlated_packet_observation`).
     - Bảng đối soát: Switch `of:0000000000000001`, Ingress Port 1 (`s1-eth1`), MAC `00:00:00:00:00:01`, IP nguồn `10.0.0.1` được xác định là đối tượng tình nghi tấn công.
  3. Phần **Defense Policy Engine Per-Port Evaluation**:
     - Quyết định cổng: Port 1 đưa ra khuyến nghị `OBSERVE` (Quan sát) thay vì tự ý chặn, tuân thủ nguyên tắc Safety Gate để ngăn ngừa tấn công giả mạo IP (IP Spoofing).
  4. Phần **Recent Webhook / SIEM Anomalies**:
     - Bấm chọn dòng sự kiện `10.0.0.2` (Port Scanning, Score: 31).
     - Cho thấy ô **Target IP Address** bên dưới tự động điền `10.0.0.2` và hộp **Policy Action Preview** hiển thị cú pháp flow rule:
       `[SAFETY GATE STAGING] flow_rule: match={dl_type:0x800, nw_src:10.0.0.2} priority=50000 mode=DRY_RUN`
  5. Bấm nút `Block Traffic`:
     - Modal xác nhận an toàn mở ra. Bấm `Cancel` để đóng modal an toàn.
- **Lời thuyết minh mẫu:**
  > "Đây là mô-đun cốt lõi thể hiện tính học thuật và an ninh của đề tài: chu trình khép kín từ Quan sát lưu lượng → Bằng chứng gói tin → Đối soát định danh Host trên ONOS → Quyết định chính sách. Đề tài áp dụng cơ chế đánh giá đa tiêu chí kết hợp kiểm tra tính hợp lệ của đồng hồ UTC, ngăn chặn việc đưa ra quyết định sai lầm khi bằng chứng bị trễ hoặc sai lệch định danh."
- **Câu hỏi Hội đồng & Cách trả lời:**
  - *Hỏi:* Tại sao hệ thống không chặn ngay lập tức mà lại đưa ra quyết định OBSERVE?
  - *Đáp:* "Thưa Thầy/Cô, trong môi trường SDN, nếu kẻ tấn công giả mạo địa chỉ IP của một máy chủ hợp lệ (như Gateway hoặc Web Server) rồi gửi gói tin tấn công, việc tự động chặn ngay lập tức sẽ gây ra hiện tượng từ chối dịch vụ tự hại (Self-inflicted DoS). Vì vậy, Policy Engine của nhóm áp dụng Safety Gate: chỉ khi bằng chứng gói tin đối soát khớp hoàn toàn với cổng vật lý và địa chỉ MAC đã đăng ký trên ONOS (Single-host Corroboration), hệ thống mới đề xuất can thiệp."

---

### MÀN HÌNH 04: MANUAL TRAFFIC CONTROL
- **Địa chỉ truy cập:** `http://localhost:3000/manual-traffic-control`.
- **Thao tác trình diễn:**
  1. Chỉ rõ cấu trúc form tuần tự 5 bước hoàn chỉnh (**Fixed in V16**):
     - **1. Chọn loại hành động can thiệp (Action Selection):** Dropdown gồm Block, Rate Limit, Redirect, Unblock, Rollback.
     - **2. Điểm đầu và Điểm cuối (Layer 2 / Layer 3 Endpoints):** Nhập Source IP / Destination IP / MAC.
     - **3. Điều kiện khớp luồng (Match Criteria / Parameters):** Cấu hình Protocol, Port hoặc Giới hạn tốc độ bps (cho Rate Limit).
     - **4. Kiểm soát an toàn & Phê duyệt Safety Gate:** Checkbox xác nhận chế độ `DRY_RUN mode active`.
     - **5. Xem trước chính sách (Policy Preview):** Hiển thị rõ Hành động, Đối tượng mục tiêu, và Trạng thái Safety Gate.
  2. Thử nghiệm **Validation từ chối khi thiếu mục tiêu**:
     - Để trống IP nguồn và IP đích.
     - Bấm nút `Áp dụng chính sách mạng (Apply Network Policy)`.
     - Chỉ ra thông báo lỗi màu đỏ xuất hiện tức thì:
       `Lỗi xác thực: Vui lòng nhập địa chỉ IP nguồn hoặc IP đích hợp lệ.`
       Và trong Policy Preview hiển thị nhãn cảnh báo: `Chưa chỉ định (Cần nhập IP)`.
  3. Thử nghiệm **Cấu hình giới hạn tốc độ (Rate Limit)**:
     - Chuyển Action sang `Giới hạn tốc độ (Rate Limit)`.
     - Cho Hội đồng thấy Bước 3 tự động chuyển thành cấu hình tốc độ: `Giới hạn tốc độ (bps)` kèm ghi chú quy đổi `OpenFlow 1.3 Meter (KB_PER_SEC = bps / 8000)`.
     - Nhập giá trị âm `-500` và bấm áp dụng -> Hệ thống báo lỗi giá trị phải là số dương.
- **Lời thuyết minh mẫu:**
  > "Giao diện Điều khiển lưu lượng thủ công tuân thủ nghiêm ngặt quy trình 5 bước kiểm soát an toàn trước khi nạp chính sách mạng. Điểm nổi bật là toàn bộ thao tác đều được bảo vệ kép: Client kiểm tra tính hợp lệ của địa chỉ IP/CIDR và dải tốc độ, Backend kiểm duyệt qua Safety Gate ngăn chặn việc cô lập nhầm Gateway 10.0.0.254 hoặc máy chủ DNS."

---

### MÀN HÌNH 05: DECISION LOGS
- **Địa chỉ truy cập:** `http://localhost:3000/decision-logs`.
- **Thao tác trình diễn:**
  1. Giới thiệu 3 thẻ trạng thái ở header:
     - `Storage: SQLite (sdnflowguard.db)`
     - `Mode: DRY_RUN`
     - `Hiển thị 89 trên tổng số 89 bản ghi`
  2. Khối **Bộ lọc kiểm toán (Audit Filters)**:
     - Lọc theo loại hành động: Chọn `Block`, `Rate Limit`, `Redirect`, `Unblock`.
     - Lọc theo nguồn khởi tạo: Phân biệt rõ `Hệ thống tự động (Automated via Safety Gate)` và `Quản trị viên (Manual Admin)`.
     - Tìm kiếm theo từ khóa IP: Gõ `10.0.0.1` -> Bảng lập tức hiển thị các can thiệp liên quan đến `10.0.0.1`.
  3. Bảng **Bản ghi kiểm toán chính sách mạng (Network Policy Audit Records)**:
     - Chỉ vào bản ghi Rate Limit lịch sử 50 bps: Nhãn màu cam `Bản ghi lịch sử (Historical Log Entry)` xuất hiện, giải thích rõ đây là log kiểm thử trước đó, được bảo toàn nguyên trạng trong SQLite mà không bị ghi đè.
     - Cột Mức độ thực thi hiển thị: `DRY_RUN (Chưa xác minh Dataplane)` thể hiện tính trung thực khoa học, không nhận vơ là đã nạp phần cứng khi chỉ chạy mô phỏng.
- **Lời thuyết minh mẫu:**
  > "Decision Logs đóng vai trò là Sổ cái kiểm toán bất biến (Audit Trail) cho toàn bộ hoạt động can thiệp mạng. Mọi quyết định dù được khởi tạo tự động qua Safety Gate hay thao tác tay bởi Quản trị viên đều ghi nhận dấu ấn thời gian, lý do căn cứ và trạng thái xác minh dataplane."

---

### MÀN HÌNH 06: REPORTS
- **Địa chỉ truy cập:** `http://localhost:3000/reports`.
- **Thao tác trình diễn:**
  1. Khối **Điều khiển trích xuất dữ liệu & Xuất báo cáo PDF**:
     - Chọn tập dữ liệu: `Sự kiện bất thường & Vi phạm ngưỡng (Security Anomalies)` hoặc `Hành động can thiệp phòng vệ (Defense Actions)`.
     - Ghi chú thời gian: `Khung thời gian lưu trữ hàng tháng (Monthly Retention Window)`.
  2. Bảng **Bản xem trước báo cáo kiểm toán (Report Preview Table)**:
     - Hiển thị 2 bản ghi bất thường mẫu (`10.0.0.2` score 31 và `10.0.0.11` score 75) được truy vấn từ SQLite.
  3. Bấm nút `Tải báo cáo PDF (Download PDF Report)`:
     - Trình duyệt tải về tệp tin PDF (vd: `security_report_anomalies_20261123.pdf`).
     - Mở tệp PDF để chứng minh: Tệp có định dạng chuẩn ReportLab, có tiêu đề học phần, bảng biểu rõ ràng và mã băm toàn vẹn.
- **Lời thuyết minh mẫu:**
  > "Mô-đun Reports cho phép xuất báo cáo giám sát an ninh định dạng PDF phục vụ công tác thanh tra và lưu trữ pháp chứng. Dữ liệu trích xuất trực tiếp từ kho lưu trữ SQLite đã được chuẩn hóa múi giờ và cấu trúc bảng chuẩn."

---

### MÀN HÌNH 07: SYSTEM SETTINGS
- **Địa chỉ truy cập:** `http://localhost:3000/system-settings`.
- **Thao tác trình diễn:**
  1. Chỉ vào banner thông báo thứ tự ưu tiên:
     `Thông báo mức độ ưu tiên thời gian chạy: Trong chế độ triển khai Docker Compose, các biến môi trường SDNFLOW_* khai báo trong docker-compose.yml có quyền ưu tiên cao hơn cài đặt cơ sở dữ liệu.`
  2. Khối **Chế độ phát hiện (Detection Mode)**:
     - Ba tùy chọn: `Nghiêm ngặt (Strict)`, `Cân bằng (Balanced - Khuyến nghị)`, `Nới lỏng (Loose)`.
  3. Khối **Biến ứng dụng & Địa chỉ điểm cuối**:
     - SDN Controller IP: `127.0.0.1` (Cổng mặc định 8181).
     - SIEM Cluster IP: `127.0.0.1` (Cổng mặc định 9200).
     - Honeypot Server IP: `10.0.0.6` (Trạm bẫy h6 trong Mininet).
  4. Khối **Cấu hình thời gian chạy thực tế (Effective Runtime Configuration)**:
     - Bấm nút `Sao chép JSON Runtime (Copy Runtime JSON)`.
     - Cho thấy danh sách các giá trị an toàn đã che giấu mật khẩu (`api_key_enabled: false`, `allowlist_ips: ["127.0.0.1", "::1"]`).
- **Lời thuyết minh mẫu:**
  > "Trang Cấu hình hệ thống được thiết kế căn giữa chuyên nghiệp, thể hiện rõ nguyên lý DevSecOps: phân định ranh giới giữa cấu hình tạm thời trong cơ sở dữ liệu và cấu hình thực tế được nạp từ biến môi trường của container. Mọi địa chỉ IP nhạy cảm như Gateway và DNS đều được bảo vệ mặc định."

---

### MÀN HÌNH 08: DOCKER DESKTOP
- **Thao tác trình diễn:**
  1. Chuyển sang cửa sổ ứng dụng **Docker Desktop**.
  2. Mở ngăn xếp `sdnflowguard-netsec`:
     - Chứng minh cả 6 containers đều mang chấm xanh `Running` (`sdnflowguard-backend`, `sdnflowguard-frontend`, `sdnflowguard-onos`, `sdnflowguard-elasticsearch`, `sdnflowguard-logstash`, `sdnflowguard-kibana`).
     - Chỉ rõ phần `Port(s)`: Tất cả các cổng đều được ánh xạ về địa chỉ nội bộ `127.0.0.1` (`127.0.0.1:3000`, `127.0.0.1:5000`, `127.0.0.1:8181`, `127.0.0.1:9200`, `127.0.0.1:5601`, `127.0.0.1:18080`).
     - Tuyệt đối không mở port ra dải công cộng `0.0.0.0/0`.
- **Lời thuyết minh mẫu:**
  > "Hạ tầng của SDNFlowGuard được đóng gói thành các microservices độc lập trên Docker. Toàn bộ các cổng kết nối đều được ràng buộc nghiêm ngặt vào localhost 127.0.0.1 trên Host, loại bỏ hoàn toàn nguy cơ phơi nhiễm giao diện quản trị ra mạng trường hoặc Internet."

---

### MÀN HÌNH 09: KIBANA
- **Địa chỉ truy cập:** `http://127.0.0.1:5601/app/home#/`.
- **Thao tác trình diễn:**
  1. Mở trang chủ Kibana.
  2. Giải thích cảnh báo ở góc dưới phải: `Your data is not secure`:
     - *Nguyên nhân kỹ thuật:* Trong môi trường thí nghiệm một máy (Single-node Local Lab), tính năng `xpack.security.enabled` được tạm thời đặt là `false` để đơn giản hóa giao tiếp nội bộ giữa Logstash, Elasticsearch và Backend mà không cần chứng chỉ PKI tự ký phức tạp.
     - Nhấn mạnh: Cổng 9200 và 5601 chỉ lắng nghe trên `127.0.0.1`, nên mức độ rủi ro đã được cô lập ở mức an toàn tối đa cho bài báo cáo.
  3. Mở menu Kibana -> **Discover** (hoặc Management -> Index Management):
     - Chứng minh 4 indices đang tồn tại: `sdnflowguard-events-2026.10.31` (119 docs), `2026.11.05` (6 docs), `2026.11.07` (18 docs), `2026.11.08` (2 docs). Tổng cộng 145 tài liệu sự kiện mạng đã nạp thành công qua Logstash pipeline.
- **Lời thuyết minh mẫu:**
  > "Kibana là thành phần giám sát sự kiện tập trung (SIEM). Dữ liệu nhật ký luồng từ ONOS được Logstash chuẩn hóa và lưu trữ tại Elasticsearch theo định dạng schema đồng nhất. Cảnh báo an ninh 'Your data is not secure' đã được nhóm phân tích trong Hồ sơ Rủi ro Kỹ thuật: đây là đặc trưng của môi trường lab single-node, được bảo vệ nhờ lớp cách ly Host-bound port 127.0.0.1."

---

### MÀN HÌNH 10: ONOS CONTROLLER
- **Địa chỉ truy cập:** `http://127.0.0.1:8181/onos/ui/login.html`.
- **Thao tác trình diễn:**
  1. Đăng nhập với tài khoản: `onos` / `rocks`.
  2. Mở Topology View (phím tắt `H` trên bàn phím):
     - Hiển thị 6 Switch Open vSwitch (`of:0000000000000001` đến `06`).
     - Các đường liên kết Trunk Link kết nối theo mô hình hình cây/lưới.
  3. Mở menu **Applications**: Cho thấy các ứng dụng `OpenFlow Base Provider`, `LLDP Link Provider`, `Host Provider` đang ở trạng thái Active.
  4. Mở menu **Flows**: Thấy danh sách 24 rules mặc định đang nạp trên các thiết bị.
- **Lời thuyết minh mẫu:**
  > "ONOS 2.7 đóng vai trò là Bộ não điều khiển mạng (SDN Controller). Kết nối Southbound sử dụng OpenFlow 1.3 điều khiển trực tiếp các luồng dữ liệu trên Open vSwitch, trong khi Northbound REST API cung cấp dữ liệu tức thời cho SDNFlowGuard Backend."

---

### MÀN HÌNH 11: BACKEND REST API DOCS
- **Địa chỉ truy cập:** `http://127.0.0.1:5000/docs` hoặc link từ thanh tiêu đề.
- **Thao tác trình diễn:**
  1. Giới thiệu trang tài liệu kỹ thuật tự động sinh:
     - Liệt kê đầy đủ 22 endpoints của hệ thống.
     - Nhóm GET (Giám sát đọc dữ liệu an toàn): `/api/health`, `/api/topology`, `/api/live-flows`, `/api/live-port-stats`, `/api/get-report`, `/api/get-anomalies`, `/api/defense/evidence-correlation`.
     - Nhóm POST (Can thiệp được bảo vệ qua Safety Gate): `/api/block`, `/api/rate-limit`, `/api/redirect`, `/api/unblock`, `/api/defense/rollback`.
  2. Nhấn mạnh nguyên tắc: Toàn bộ các API can thiệp đều mặc định chạy ở chế độ `dry_run: true`, trừ khi có sự phê duyệt rõ ràng của quản trị viên và thỏa mãn điều kiện đối soát bằng chứng.
- **Lời thuyết minh mẫu:**
  > "Trang API Reference đặc tả chi tiết giao diện lập trình của Backend. Hệ thống áp dụng kiến trúc Clean Architecture, phân tách rõ ràng giữa tầng Giao diện (HTTP Handlers), tầng Nghiệp vụ (Use Cases, Domain Policies) và tầng Hạ tầng (ONOS, Elasticsearch, SQLite Repositories)."

---

## PHẦN C: KỊCH BẢN KIỂM CHỨNG PHÒNG THỦ MẠNG

---

### CẤP ĐỘ 1: TRÌNH DIỄN KIỂM CHỨNG AN TOÀN MẶC ĐỊNH (DRY_RUN DEFAULT)
*(Đây là kịch bản chuẩn được khuyến nghị sử dụng khi thuyết minh trước Hội đồng để bảo toàn 100% tính ổn định của bài thi)*

1. **Bước 1: Quan sát Trạng thái Bình thường (Baseline)**
   - Mở màn hình `Traffic Overview`: 6 switches, 9 hosts kết nối ổn định, ping thông suốt.
2. **Bước 2: Kích hoạt Chính sách qua Safety Gate (Policy Simulation)**
   - Vào `Manual Traffic Control`.
   - Chọn Action: `Chặn lưu lượng (Block)`.
   - Nhập Source IP: `10.0.0.2` (Host nghi vấn quét cổng).
   - Đảm bảo checkbox `DRY_RUN mode active` đang được chọn.
   - Bấm `Áp dụng chính sách mạng`.
3. **Bước 3: Xác minh Kết quả Mô phỏng (Verify)**
   - Khối phản hồi hiển thị huy hiệu xanh: `DRY_RUN (MÔ PHỎNG / STAGED)`.
   - Chuyển sang `Decision Logs`: Bản ghi mới được tạo với nhãn `Automated (Safety Gate)` và mức độ `DRY_RUN (Chưa xác minh Dataplane)`.
   - Dữ liệu mạng Mininet hoàn toàn không bị ngắt kết nối, chứng minh hệ thống không làm gián đoạn dịch vụ khi chưa phê duyệt.

---

### CẤP ĐỘ 2: THỰC NGHIỆM CAN THIỆP DATAPLANE CÓ CÔ LẬP (OPTIONAL ISOLATED LIVE EXPERIMENT)
*(Chỉ thực hiện khi Giảng viên / Hội đồng yêu cầu chứng minh luồng can thiệp phần cứng thực tế)*

#### Quy trình 5 bước: BASELINE → POLICY → VERIFY → ROLLBACK → RECOVERY

1. **Giai đoạn 1: Đo lường cơ sở (Baseline)**
   - Mở terminal Mininet trên WSL2:
     ```bash
     wsl -d Ubuntu-26.04
     # Kiểm tra ping giữa h1 (10.0.0.1) và h2 (10.0.0.2)
     mininet> h1 ping -c 3 h2
     ```
   - *Kết quả Baseline:* `3 packets transmitted, 3 received, 0% packet loss, rtt min/avg/max = 0.5/0.8/1.2 ms`.

2. **Giai đoạn 2: Nạp chính sách can thiệp (Policy Enforcement)**
   - Áp dụng lệnh chặn qua Backend API với Operator Authentication:
     ```powershell
     $body = @{ srcIp = '10.0.0.1'; dstIp = '10.0.0.2'; dry_run = $false } | ConvertTo-Json
     Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/block' -Method Post -ContentType 'application/json' -Body $body
     ```
   - Flow rule với `priority: 50000`, `match: nw_src=10.0.0.1, nw_dst=10.0.0.2`, `treatment: DROP` được đẩy xuống switch `s1` (`of:0000000000000001`).

3. **Giai đoạn 3: Kiểm chứng Dataplane (Verify Enforcement)**
   - Kiểm tra lại trên Mininet:
     ```bash
     mininet> h1 ping -c 3 -W 1 h2
     ```
   - *Kết quả thực nghiệm:* `3 packets transmitted, 0 received, 100% packet loss`.
   - Kiểm tra bộ đếm flow rule trên ONOS:
     ```powershell
     Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/live-flows' | Select-Object -ExpandProperty data | Where-Object { $_.priority -eq 50000 }
     ```
   - *Bằng chứng:* Flow rule tồn tại với `state: ADDED`, bộ đếm `packets > 0`.

4. **Giai đoạn 4: Hoàn tác chính sách (Rollback)**
   - Thực hiện Rollback thu hồi rule:
     ```powershell
     $rollbackBody = @{ srcIp = '10.0.0.1'; dry_run = $false } | ConvertTo-Json
     Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/defense/rollback' -Method Post -ContentType 'application/json' -Body $rollbackBody
     ```
   - Backend phát lệnh xóa rule trên switch `s1`.

5. **Giai đoạn 5: Xác nhận phục hồi (Recovery)**
   - Đo lại kết nối trên Mininet:
     ```bash
     mininet> h1 ping -c 3 h2
     ```
   - *Kết quả phục hồi:* `0% packet loss`, thời gian phục hồi dịch vụ (Recovery Time) `< 1.5 giây`.

---

## PHẦN D: QUY TRÌNH TẮT MÁY VÀ KHỞI ĐỘNG LẠI AN TOÀN

### Khi kết thúc buổi báo cáo (Clean Shutdown):
1. Dừng stack Docker một cách tuần tự (bảo toàn volumes):
   ```powershell
   Set-Location D:\Project\Nhom02_SDNFlowGuard
   docker compose stop
   ```
2. Dừng dịch vụ giả lập Mininet trong WSL2:
   ```powershell
   wsl -d Ubuntu-26.04 sudo systemctl stop sdnflowguard-topo.service
   ```
3. Thoát WSL2:
   ```powershell
   wsl --shutdown
   ```

### Khởi động lại lab trong phiên tiếp theo (Safe Restart):
```powershell
Set-Location D:\Project\Nhom02_SDNFlowGuard
docker compose start
wsl -d Ubuntu-26.04 sudo systemctl start sdnflowguard-topo.service
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```
*(Chạy `test.ps1` để xác nhận toàn bộ 5/5 giai đoạn kiểm thử tự động đều đạt kết quả PASS trước khi bắt đầu phiên làm việc mới).*
