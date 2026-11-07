<p align="center">
  <img src="screenshots/sdnflowguard-logo.png" alt="SDNFlowGuard Logo" width="260" />
</p>

<h1 align="center">
  SDNFlowGuard
</h1>

<p align="center">
  <strong>Software-Defined Network Security & Monitoring Platform</strong>
</p>

<p align="center">
  Nền tảng giám sát và phòng thủ mạng SDN tích hợp ONOS, OpenFlow 1.3 và ELK Stack.
</p>

---

## 1. Tính năng chính

- **Giám sát mạng SDN & Trực quan hóa Tôpô:** Thu thập trạng thái thiết bị, cổng switch và lưu lượng luồng trực tiếp từ ONOS Controller qua REST API và OpenFlow 1.3.
- **Phát hiện bất thường & Tương quan bằng chứng:** Telemetry Collector liên tục đối soát mẫu lưu lượng và phân tích dữ liệu gói tin nhằm nhận diện lưu lượng tấn công.
- **Điều khiển lưu lượng linh hoạt:** Hỗ trợ xem trước và thực thi các quy tắc kiểm soát luồng (Block IP, Rate-limit, Redirect) qua OpenFlow Access Control List (ACL).
- **Cổng an toàn Safety Gate & DRY_RUN:** Ngăn chặn tuyệt đối việc ngắt kết nối router hạ tầng (`10.0.0.254`), DNS công cộng (`8.8.8.8`, `1.1.1.1`) hoặc toàn bộ subnet với giải thuật kiểm tra chồng lấn mạng (CIDR overlap check).
- **Hệ thống giám sát ELK Stack:** Đường ống Logstash tiếp nhận sự kiện JSON, Elasticsearch lưu trữ chỉ mục tập trung và Kibana cung cấp bảng trực quan hóa chuyên sâu.
- **Nhật ký quyết định & Báo cáo kỹ thuật:** Ghi vết đầy đủ lịch sử can thiệp mạng, hỗ trợ cơ chế hoàn tác an toàn (Rollback) và xuất báo cáo an ninh định dạng PDF.
- **Giao diện Dashboard song ngữ & Trợ lý vận hành:** Giao diện ReactJS hỗ trợ chuyển ngữ Tiếng Việt / Tiếng Anh cùng Trợ lý hỏi đáp vận hành SDN tích hợp (Read-only Assistant).

---

## 2. Kiến trúc hệ thống

```text
+-------------------------------------------------------------------------------+
| APPLICATION: React Dashboard (:3000) -> Nginx Reverse Proxy -> Flask API (:5000)|
+---------------------------------------+---------------------------------------+
                                        | (REST /onos/v1)              | (Local SQL)
                                        v                              v
+-----------------------------------------------+             +-----------------+
| CONTROL: ONOS Controller 2.7 (REST :8181)     |             | SQLite Database |
|          OpenFlow 1.3 Driver  (TCP :6653)     |             | sdnflowguard.db |
+-----------------------+-----------------------+             +-----------------+
                        | (OpenFlow Protocol via TCP 6653)
                        v
+-------------------------------------------------------------------------------+
| DATA PLANE:  Open vSwitch (OVS in WSL2) <---> Mininet Hosts (h1, h2, h3...)   |
+---------------------------------------+---------------------------------------+
                                        | (Telemetry Ingestion)
                                        v
+-------------------------------------------------------------------------------+
| OBSERVABILITY: Logstash (:18080) -> Elasticsearch (:9200) -> Kibana (:5601)   |
+-------------------------------------------------------------------------------+
```

### Danh mục Docker Services (`sdnflowguard-netsec`)

| Service | Container Name | Cổng ánh xạ | Chức năng chính |
| :--- | :--- | :---: | :--- |
| `frontend` | `sdnflowguard-frontend` | `3000:3000` | Giao diện React Dashboard phục vụ qua Nginx reverse proxy. |
| `backend` | `sdnflowguard-backend` | `5000:5000` | Flask REST API điều phối phòng thủ và kiểm tra Safety Gate. |
| `onos` | `sdnflowguard-onos` | `8181:8181`, `6653:6653` | SDN Controller quản lý tôpô (REST) và nhận kết nối switch (OpenFlow). |
| `elasticsearch` | `sdnflowguard-elasticsearch` | `9200:9200` | Lưu trữ chỉ mục log và dữ liệu sự kiện an ninh. |
| `logstash` | `sdnflowguard-logstash` | `18080:8080` | Pipeline tiếp nhận telemetry từ collector qua HTTP webhook. |
| `kibana` | `sdnflowguard-kibana` | `5601:5601` | Phân tích và trực quan hóa chuyên sâu các sự kiện an ninh. |

---

## 3. Yêu cầu hệ thống

| Thành phần | Yêu cầu tối thiểu | Khuyến nghị vận hành |
| :--- | :--- | :--- |
| **Hệ điều hành** | Windows 10/11 64-bit (hỗ trợ WSL2) | Windows 11 (WSL2 Ubuntu 22.04/24.04) |
| **Bộ nhớ RAM** | 8 GB RAM (chạy chế độ `-SkipKibana`) | 16 GB RAM (chạy đủ toàn bộ 6 container) |
| **CPU & Ổ cứng** | 4 nhân vật lý, 10 GB SSD trống | 6 nhân / 12 luồng, 20 GB SSD trống |
| **Phần mềm bắt buộc** | Docker Desktop (bật WSL2 engine) | Docker Desktop 4.25+ |
| **Phần mềm bổ sung** | `openvswitch-switch`, `mininet` (trong WSL2) | Chỉ khi cần chạy giả lập switch / host |
| **Môi trường Test** | Python 3.10+ (trên máy host) | Chỉ khi cần chạy automated test ngoài Docker |

---

## 4. Cài đặt và khởi động dự án

### Bước 1: Chuẩn bị môi trường
1. Khởi động **Docker Desktop** và đảm bảo Docker Engine ở trạng thái sẵn sàng (*Engine running*).
2. Mở PowerShell tại thư mục gốc dự án (`D:\Project\Nhom02_SDNFlowGuard`).
3. Khởi tạo named volume cho Elasticsearch: `docker volume create sdnflowguard-elasticsearch-data` *(script `manage.ps1` sẽ tự kiểm tra và tạo nếu thiếu)*.

### Bước 2: Khởi động hệ thống
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\manage.ps1 up
```
*Hệ thống khởi động theo thứ tự: Core (Elasticsearch, ONOS) -> Ứng dụng (Logstash, Backend, Frontend) -> Quan sát (Kibana).*
- **Tiết kiệm RAM (<= 8GB):** Thêm `-SkipKibana` để bỏ qua Kibana và tiết kiệm ~550 MB RAM.
- **Build lại image:** Thêm cờ `-Build` khi có thay đổi mã nguồn backend/frontend.

### Bước 3: Kiểm tra trạng thái vận hành
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\manage.ps1 status
```
Đảm bảo 6/6 container hiển thị trạng thái `Up (healthy)`.

### Bước 4: Mở Dashboard quản trị
Truy cập qua trình duyệt: **[http://127.0.0.1:3000](http://127.0.0.1:3000)** hoặc chạy:
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\manage.ps1 open
```

### Bước 5: Truy cập ONOS Web UI
- Địa chỉ truy cập: **[http://127.0.0.1:8181/onos/ui](http://127.0.0.1:8181/onos/ui)** (Tài khoản lab mặc định: `onos` / `rocks`).
- **Lưu ý:** Bắt buộc nhập `/onos/ui`. Truy cập root `http://127.0.0.1:8181/` sẽ nhận `HTTP 403 Forbidden` do cơ chế Jetty Servlet. Cổng `6653` (`tcp:127.0.0.1:6653`) là kênh TCP nhị phân OpenFlow 1.3, không phải HTTP.

### Bước 6: Kiểm tra dịch vụ ELK
- **Elasticsearch:** [http://127.0.0.1:9200](http://127.0.0.1:9200) | **Kibana:** [http://127.0.0.1:5601](http://127.0.0.1:5601).
- **Logstash Webhook:** [http://127.0.0.1:18080](http://127.0.0.1:18080) (Cổng tiếp nhận POST; phản hồi `ok` khi truy cập GET là tín hiệu probe chuẩn Elastic, không phải giao diện đồ họa).

### Bước 7: Dừng hệ thống an toàn
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\manage.ps1 down
```
*Lệnh dừng container an toàn, không làm mất dữ liệu SQLite và Elasticsearch. Tuyệt đối không thêm `-v`.*

---

## 5. Hướng dẫn sử dụng Dashboard

1. **Tổng quan (Dashboard):** Kiểm tra trạng thái 6 container và chỉ số lưu lượng tóm tắt.
2. **Giám sát lưu lượng (Traffic Overview):** Quan sát bản đồ tôpô ONOS và các quy tắc luồng OpenFlow đang hoạt động.
3. **Phát hiện bất thường (Anomaly Detection):** Đối soát cảnh báo lưu lượng vượt ngưỡng và bằng chứng thu thập.
4. **Điều khiển lưu lượng (Traffic Control):** Thử nghiệm chặn IP/bóp băng thông. Chế độ `DRY_RUN` hiển thị bản xem trước Flow Rule mà không ngắt luồng thật.
5. **Nhật ký quyết định (Decision Logs):** Tra cứu lịch sử can thiệp mạng và thực hiện hoàn tác quy tắc (Rollback).
6. **Báo cáo (Reports):** Xem thống kê an ninh và xuất báo cáo PDF.
7. **Cấu hình (Settings):** Tra cứu tham số API, dải IP bảo vệ và ngưỡng cảnh báo.
- **Chuyển ngữ VI/EN:** Sử dụng nút bấm góc trên Header để đổi giao diện song ngữ.
- **Trợ lý vận hành SDN:** Mở Chatbot ở góc giao diện để hỏi đáp kỹ thuật (chế độ chỉ đọc, an toàn tuyệt đối).

---

## 6. Kết nối Mininet với ONOS (Tùy chọn Lab)

1. Trong **WSL2 Ubuntu**, khởi động Open vSwitch:
   ```bash
   sudo service openvswitch-switch start
   ```
2. Khởi tạo Mininet kết nối về cổng OpenFlow 6653 của ONOS:
   ```bash
   sudo mn --topo single,3 --controller=remote,ip=127.0.0.1,port=6653 --switch ovsk
   ```
   *(Nếu WSL2 ở chế độ mạng NAT không thông `127.0.0.1`, thay bằng IP host lấy qua `ip route show | grep default | awk '{print $3}'`).*
3. Trong Mininet CLI, sinh lưu lượng kiểm tra:
   ```text
   mininet> pingall
   ```
4. Quan sát: Switch `of:0000000000000001` và các host xuất hiện trên ONOS UI (`8181/onos/ui`) và đồ thị lưu lượng bắt đầu ghi nhận trên SDNFlowGuard Dashboard (`3000`).

---

## 7. Kiểm thử hệ thống (Automated Testing)

Thực thi bộ kiểm thử toàn diện và đối soát tính toàn vẹn hệ thống bằng lệnh:
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```
Quy trình tự động thực hiện 5 cổng kiểm tra nghiêm ngặt:
1. **Cú pháp Python (`compileall`):** Xác minh 100% tệp backend biên dịch sạch, không lỗi cú pháp.
2. **CLI Self-Tests (4/4):** Thực thi độc lập các mô-đun an ninh (Monitor V2, Parser, Correlator, Policy) với 0 cuộc gọi mạng ngoài.
3. **Automated Test Suite (79 Tests):** Chạy toàn bộ Unit, Integration, API Contracts, CIDR Safety Gate và E2E.
4. **Kiểm tra Frontend Build:** Xác minh bundle production của giao diện (`frontend/build/index.html`).
5. **Toàn vẹn SQLite:** Kiểm tra cấu trúc bằng `PRAGMA integrity_check` và xác minh mã băm SHA-256 bất biến (`3909de520f89ea050e7858104c8aa17bddd94d06af9db5ad84652404b9463fe9`).

---

## 8. Cấu trúc thư mục

```text
Nhom02_SDNFlowGuard/
├── backend/                  # Flask REST API, SDN logic, collectors, 79 automated tests
├── frontend/                 # React 18 Dashboard, Nginx reverse proxy, asset logo
├── database/                 # Cơ sở dữ liệu SQLite sdnflowguard.db & bản sao lưu .bak
├── infrastructure/           # Pipeline tiếp nhận Logstash & cấu hình compose phụ trợ
├── scripts/                  # Bộ công cụ quản trị (manage.ps1, test.ps1, backup, reclaim)
├── docs/                     # Tài liệu kiến trúc, an ninh và hướng dẫn kỹ thuật
├── docker-compose.yml        # Cấu hình Docker Compose chuẩn duy nhất cho 6 container
├── .env.example              # Mẫu biến môi trường cấu hình (không chứa credentials)
├── LICENSE                   # Giấy phép mã nguồn mở MIT
└── README.md                 # Tài liệu hướng dẫn vận hành kỹ thuật
```

---

## 9. Xử lý sự cố thường gặp (Troubleshooting)

| Triệu chứng | Nguyên nhân khả dĩ | Cách kiểm tra | Giải pháp an toàn |
| :--- | :--- | :--- | :--- |
| **`error during connect` khi chạy script** | Docker Desktop chưa chạy hoặc named pipe bị ngắt. | Kiểm tra biểu tượng Docker ở Taskbar. | Khởi động Docker Desktop, chờ trạng thái *Engine running* rồi chạy lại lệnh. |
| **Cổng 8181 báo `HTTP 403 Forbidden`** | Nhập thiếu đường dẫn `/onos/ui`. | Kiểm tra thanh địa chỉ trình duyệt. | Truy cập đúng URL: `http://127.0.0.1:8181/onos/ui`. |
| **Cổng 6653 báo `ERR_EMPTY_RESPONSE`** | Truy cập giao thức OpenFlow 1.3 TCP bằng browser. | Kiểm tra URL đã nhập. | Không mở bằng browser; cổng 6653 chỉ dành cho switch kết nối nhị phân OpenFlow. |
| **Logstash cổng 18080 chỉ hiện chữ `ok`** | Mở webhook endpoint bằng phương thức GET. | Quan sát phản hồi `ok`. | Phản hồi probe bình thường; webhook nhận dữ liệu qua POST. Phân tích tại Kibana (5601). |
| **Dashboard không hiện thiết bị hoặc tôpô** | Chưa có switch OpenFlow kết nối vào ONOS. | Kiểm tra ONOS UI hoặc `/api/topology`. | Khởi động Mininet trong WSL2 và chạy `pingall` để sinh lưu lượng kích hoạt. |
| **PowerShell báo `scripts is disabled`** | Chính sách ExecutionPolicy giới hạn chạy script. | Quan sát thông báo lỗi đỏ. | Luôn gọi lệnh kèm cờ: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\<script>`. |

---

## 10. Giới hạn vận hành & Giấy phép (License)

- **Chế độ phòng vệ mặc định:** Hệ thống hoạt động mặc định ở chế độ `DRY_RUN`. Các hành động kiểm soát lưu lượng chỉ được mô phỏng để bảo đảm an toàn, không tự ý ngắt kết nối thực tế trừ khi được cấu hình chuyển sang `ACTIVE_ENFORCEMENT` với xác thực người vận hành hợp lệ.
- **Ranh giới môi trường:** Nền tảng được thiết kế và tối ưu cho môi trường nghiên cứu, kiểm thử phòng lab và mô phỏng mạng ảo hóa.
- **Giấy phép phần mềm:** Dự án được phát hành theo giấy phép **MIT License** (chi tiết xem tại tệp [`LICENSE`](LICENSE)).
