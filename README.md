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
  Nền tảng giám sát và phòng thủ mạng SDN tích hợp ONOS Controller, OpenFlow 1.3 và ELK Stack.
</p>

---

## 1. Tổng quan dự án

**SDNFlowGuard** là giải pháp giám sát an ninh mạng và điều khiển phòng thủ tự động trên nền tảng mạng điều khiển bằng phần mềm (Software-Defined Networking - SDN). Hệ thống tích hợp trực tiếp với bộ điều khiển **ONOS Controller 2.7** qua giao thức chuẩn **OpenFlow 1.3** và hệ sinh thái phân tích tập trung **ELK Stack (Elasticsearch, Logstash, Kibana)**.

SDNFlowGuard cho phép các kỹ sư mạng quan sát toàn diện trạng thái chuyển mạch, tự động phân tích và đối soát bằng chứng gói tin, đồng thời thiết lập chính sách kiểm soát luồng thông minh qua cơ chế phòng hộ nhiều tầng (**Multi-layer Safety Gate**), ngăn ngừa rủi ro gián đoạn hạ tầng mạng trọng yếu.

---

## 2. Tính năng kỹ thuật nổi bật

- **Giám sát mạng SDN & Trực quan hóa Tôpô:** Tự động phát hiện thiết bị mạng (switches), cổng giao tiếp (ports), máy trạm (hosts) và các quy tắc luồng (flow rules) đang hoạt động thông qua REST API của ONOS.
- **Phân tích Telemetry & Phát hiện bất thường:** Module Collector liên tục đối soát mẫu lưu lượng theo chu kỳ trượt nanosecond, nhận diện các chuỗi tăng đột biến tốc độ gói tin (high-PPS anomaly streaks).
- **Đối soát bằng chứng gói tin (Step 63/64 Evidence Correlation):** Trích xuất thông tin định danh L2/L3 (IP/MAC nguồn, nhãn thời gian UTC) từ mẫu gói tin và đối chiếu chéo với bảng trạng thái thiết bị thực tế của ONOS nhằm loại trừ hiện tượng giả mạo địa chỉ (IP/MAC spoofing).
- **Điều khiển lưu lượng linh hoạt:** Cung cấp cơ chế tạo và thực thi quy tắc OpenFlow Access Control List (ACL) đa dạng: Chặn địa chỉ IP vi phạm (`DENY`), bóp băng thông qua OpenFlow Meter (`RATE_LIMIT`), và chuyển hướng luồng kiểm tra (`REDIRECT`).
- **Cổng an toàn nhiều tầng (Safety Gate & DRY_RUN):**
  - Mặc định khởi chạy ở chế độ **`DRY_RUN`**, chỉ mô phỏng tác động và tính toán trước quy tắc mà không can thiệp luồng thực tế.
  - Tự động từ chối mọi yêu cầu thao tác nhắm vào các địa chỉ mạng trọng yếu: Default Gateway (`10.0.0.254`), DNS công cộng (`8.8.8.8`, `1.1.1.1`), dải Loopback (`127.0.0.0/8`), Multicast (`224.0.0.0/4`), và các dải mạng con chứa hạ tầng (CIDR Overlap Protection).
  - Ngăn chặn client chưa xác thực tự ý chiếm quyền phê duyệt của quản trị viên (`operator_approved`).
- **Hệ thống giám sát ELK Stack tập trung:** Pipeline Logstash tiếp nhận telemetry qua HTTP webhook, Elasticsearch lưu trữ chỉ mục sự kiện an ninh, và Kibana cung cấp dashboard đồ họa trực quan hóa lưu lượng theo thời gian thực.
- **Nhật ký quyết định & Khả năng hoàn tác an toàn (Rollback):** Lưu trữ toàn bộ lịch sử can thiệp mạng vào cơ sở dữ liệu SQLite, cho phép người vận hành hoàn tác nhanh chóng các quy tắc đã triển khai khi tình huống khẩn cấp kết thúc.
- **Giao diện Dashboard song ngữ & Trợ lý vận hành SDN:** Giao diện điều hành React 18 hỗ trợ chuyển ngữ mượt mà giữa Tiếng Việt và Tiếng Anh, tích hợp Trợ lý hỏi đáp vận hành mạng (SDN Operations Assistant) hoạt động hoàn toàn ở chế độ chỉ đọc (Read-only Guardrail).

---

## 3. Kiến trúc hệ thống

Kiến trúc SDNFlowGuard được tổ chức chuẩn hóa theo mô hình phân tách 3 mặt phẳng mạng kết hợp với mặt phẳng quan sát:

```text
+---------------------------------------------------------------------------------------+
| APPLICATION & MANAGEMENT PLANE                                                        |
|   - React 18 Operations Dashboard (Port 3000)                                         |
|   - Nginx Reverse Proxy (Port 3000 -> 5000)                                           |
|   - Flask REST API Backend (Port 5000)                                                |
|   - SQLite Database (database/sdnflowguard.db)                                        |
+-------------------------------------------+-------------------------------------------+
                                            | REST API (/onos/v1/*)
                                            v
+---------------------------------------------------------------------------------------+
| CONTROL PLANE                                                                         |
|   - ONOS SDN Controller 2.7.0 (Web UI & REST: Port 8181)                              |
|   - OpenFlow 1.3 Southbound Driver (Binary TCP: Port 6653)                            |
+-------------------------------------------+-------------------------------------------+
                                            | OpenFlow 1.3 Protocol (TCP 6653)
                                            v
+---------------------------------------------------------------------------------------+
| DATA PLANE                                                                            |
|   - Open vSwitch (OVS in WSL2 / Linux Host)                                           |
|   - Virtual Network Topology / Mininet (Hosts: h1, h2, h3...)                         |
+-------------------------------------------+-------------------------------------------+
                                            | Telemetry & Alert Webhook (HTTP POST)
                                            v
+---------------------------------------------------------------------------------------+
| OBSERVABILITY PLANE                                                                   |
|   - Logstash Telemetry Ingestion (Port 18080)                                         |
|   - Elasticsearch Indexing Engine (Port 9200)                                         |
|   - Kibana Visual Analytics Dashboard (Port 5601)                                     |
+---------------------------------------------------------------------------------------+
```

### Danh mục dịch vụ Docker Compose (`sdnflowguard-netsec`)

| Dịch vụ (Service) | Tên Container | Cổng ánh xạ (Host:Container) | Vai trò chức năng trong hệ thống |
| :--- | :--- | :---: | :--- |
| `frontend` | `sdnflowguard-frontend` | `3000:3000` | Giao diện điều hành React 18 phục vụ qua Nginx reverse proxy. |
| `backend` | `sdnflowguard-backend` | `5000:5000` | Cung cấp REST API, thực thi Safety Gate, đối soát bằng chứng và xử lý quyết định. |
| `onos` | `sdnflowguard-onos` | `8181:8181`<br>`6653:6653` | Bộ điều khiển SDN: REST API/UI quản trị (`8181`) và kênh OpenFlow 1.3 (`6653`). |
| `elasticsearch` | `sdnflowguard-elasticsearch` | `9200:9200` | Lưu trữ chỉ mục phân tán và tra cứu lịch sử sự kiện an ninh mạng. |
| `logstash` | `sdnflowguard-logstash` | `18080:8080` | Pipeline tiếp nhận dữ liệu telemetry từ collector qua HTTP webhook. |
| `kibana` | `sdnflowguard-kibana` | `5601:5601` | Nền tảng phân tích và biểu diễn trực quan dữ liệu sự kiện an ninh. |

---

## 4. Yêu cầu hệ thống

| Thành phần | Yêu cầu tối thiểu (Lab Mode) | Khuyến nghị sản xuất / Demo chuẩn |
| :--- | :--- | :--- |
| **Hệ điều hành** | Windows 10/11 64-bit (hỗ trợ WSL2) | Windows 11 64-bit với WSL2 Ubuntu 22.04 / 24.04 LTS |
| **Bộ nhớ RAM** | 8 GB RAM (chạy chế độ `-SkipKibana`) | 16 GB RAM (chạy đồng thời 6/6 container dịch vụ) |
| **CPU & Bộ nhớ lưu trữ** | 4 Cores vật lý, 15 GB SSD khả dụng | 6 Cores / 12 Threads, 25 GB SSD NVMe khả dụng |
| **Phần mềm điều khiển** | Docker Desktop 4.25+ (WSL2 Backend) | Docker Desktop phiên bản mới nhất, Docker Compose V2 |
| **Môi trường giả lập mạng** | WSL2 Linux kernel có hỗ trợ OVS | `openvswitch-switch`, `mininet` cài đặt bên trong WSL2 |
| **Môi trường kiểm thử máy host** | Python 3.10.x 64-bit (trên Windows) | Khuyến nghị sử dụng venv chuẩn tại `backend/venv` |

---

## 5. Hướng dẫn cài đặt và khởi động nhanh

### Bước 1: Sao chép mã nguồn dự án
```powershell
git clone https://github.com/DatPhanNexor/Nhom02_SDNFlowGuard.git
cd Nhom02_SDNFlowGuard
```

### Bước 2: Kiểm tra tiền điều kiện môi trường
Chạy script kiểm tra để xác nhận Docker, cổng mạng và các thư mục cấu hình đã sẵn sàng:
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\manage.ps1 check
```

### Bước 3: Khởi động hệ thống Docker
Khởi động cụm dịch vụ hoàn chỉnh (6 container):
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\manage.ps1 up
```
> **Mẹo tối ưu RAM:** Với máy có bộ nhớ RAM $\le$ 8 GB, thêm cờ `-SkipKibana` để bỏ qua Kibana, tiết kiệm ngay khoảng 550 MB RAM:
> ```powershell
> powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\manage.ps1 up -SkipKibana
> ```

### Bước 4: Kiểm tra trạng thái hoạt động của các dịch vụ
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\manage.ps1 status
```
Đảm bảo tất cả container báo trạng thái `Up (healthy)` hoặc `Up`.

### Bước 5: Mở Dashboard quản trị mạng
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\manage.ps1 open
```
Trình duyệt web mặc định sẽ tự động mở trang điều hành tại: **[http://127.0.0.1:3000](http://127.0.0.1:3000)**.

### Bước 6: Dừng hệ thống khi kết thúc phiên làm việc
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\manage.ps1 down
```
*Lệnh này giải phóng an toàn bộ nhớ và tài nguyên mà vẫn giữ nguyên 100% dữ liệu SQLite và chỉ mục Elasticsearch.*

---

## 6. Danh mục dịch vụ và cổng truy cập

| Dịch vụ | Địa chỉ truy cập / Endpoint | Giao thức | Ghi chú vận hành quan trọng |
| :--- | :--- | :---: | :--- |
| **SDNFlowGuard Dashboard** | **[http://127.0.0.1:3000](http://127.0.0.1:3000)** | HTTP | Bảng điều khiển trung tâm React 18 qua Nginx reverse proxy. |
| **Backend REST API** | **[http://127.0.0.1:5000/api/health](http://127.0.0.1:5000/api/health)** | HTTP | Endpoint kiểm tra sức khỏe hệ thống và phân phối dữ liệu JSON. |
| **ONOS Web Management UI** | **[http://127.0.0.1:8181/onos/ui](http://127.0.0.1:8181/onos/ui)** | HTTP | **Bắt buộc nhập `/onos/ui`**. Tài khoản mặc định: `onos` / `rocks`. |
| **ONOS OpenFlow Southbound** | **`tcp://127.0.0.1:6653`** | OpenFlow 1.3 TCP | Cổng giao tiếp nhị phân dành riêng cho Switch/Mininet. **Không mở bằng trình duyệt**. |
| **Elasticsearch API** | **[http://127.0.0.1:9200](http://127.0.0.1:9200)** | HTTP | Chỉ mục cơ sở dữ liệu sự kiện an ninh mạng. |
| **Kibana Analytics** | **[http://127.0.0.1:5601](http://127.0.0.1:5601)** | HTTP | Trực quan hóa và phân tích sâu các chỉ số lưu lượng ELK. |
| **Logstash Telemetry Webhook** | **[http://127.0.0.1:18080](http://127.0.0.1:18080)** | HTTP | Tiếp nhận sự kiện qua POST; khi mở bằng GET sẽ trả về chữ `ok` (Elastic probe chuẩn). |

---

## 7. Thực nghiệm giả lập mạng với Mininet & OpenFlow

Để mô phỏng môi trường mạng SDN thực tế có lưu lượng và switch kết nối về ONOS Controller:

### 1. Khởi động Open vSwitch trong WSL2 Ubuntu:
```bash
sudo service openvswitch-switch start
```

### 2. Khởi tạo tôpô Mininet kết nối về ONOS:
```bash
sudo mn --topo single,3 --controller=remote,ip=127.0.0.1,port=6653 --switch ovsk
```
> *Lưu ý về mạng WSL2:* Nếu WSL2 ở chế độ mạng NAT không truy cập được trực tiếp `127.0.0.1`, hãy thay thế bằng địa chỉ IP của Windows Host lấy qua lệnh:
> ```bash
> ip route show | grep default | awk '{print $3}'
> ```

### 3. Kiểm tra lưu lượng nội bộ mạng:
Trong dấu nhắc lệnh Mininet CLI, thực hiện kiểm tra thông mạch giữa các máy trạm:
```text
mininet> pingall
```

### 4. Xác nhận kết quả trên Dashboard:
- Truy cập ONOS UI (`http://127.0.0.1:8181/onos/ui`): Switch `of:0000000000000001` cùng 3 máy trạm (`10.0.0.1`, `10.0.0.2`, `10.0.0.3`) hiển thị trực quan trên bản đồ tôpô.
- Truy cập SDNFlowGuard Dashboard (`http://127.0.0.1:3000`): Dữ liệu gói tin, tốc độ lưu lượng cổng và các bản ghi Flow Rule được cập nhật theo thời gian thực.

---

## 8. Hướng dẫn sử dụng các phân hệ Dashboard

1. **Tổng quan (Dashboard):** Hiển thị thẻ tóm tắt sức khỏe của 6 container dịch vụ, thống kê tổng số thiết bị, cổng mạng và biểu đồ tổng hợp lưu lượng.
2. **Giám sát lưu lượng (Traffic Overview):** Quan sát bản đồ trực quan tôpô ONOS, bảng chi tiết cổng switch và các quy tắc luồng OpenFlow đang được nạp trên thiết bị.
3. **Phát hiện bất thường (Anomaly Detection):** Theo dõi các cảnh báo lưu lượng vượt ngưỡng (PPS Spike Alerts), phân tích biểu đồ biến động băng thông theo chu kỳ trượt.
4. **Điều khiển lưu lượng (Traffic Control):** Thiết lập quy tắc phòng thủ (Chặn IP, Bóp băng thông, Chuyển hướng). Trong chế độ `DRY_RUN`, hệ thống hiển thị bản xem trước JSON OpenFlow chuẩn xác mà không can thiệp luồng thực tế.
5. **Nhật ký quyết định (Decision Logs):** Tra cứu toàn bộ lịch sử các quyết định can thiệp mạng đã ghi nhận, phân tích điểm rủi ro và cung cấp nút **Hoàn tác (Rollback)** để hủy quy tắc tức thời.
6. **Báo cáo an ninh (Reports):** Tổng hợp sự kiện, đánh giá hiệu năng phòng thủ và xuất báo cáo an ninh mạng định dạng tài liệu PDF.
7. **Cấu hình hệ thống (Settings):** Tra cứu các tham số ngưỡng phát hiện bất thường, thời gian cửa sổ trượt, và danh sách các địa chỉ IP được bảo vệ mặc định.
8. **Chuyển đổi ngôn ngữ (Bilingual Switcher):** Nút chọn `VI | EN` tại thanh tiêu đề cho phép chuyển đổi ngôn ngữ tức thời trên toàn bộ các trang và bảng biểu.
9. **Trợ lý vận hành SDN (SDN Assistant):** Khung chat tương tác tích hợp tại góc phải, hỗ trợ tra cứu nhanh trạng thái tôpô, cú pháp lệnh và giải thích cảnh báo (hoạt động 100% ở chế độ chỉ đọc an toàn).

---

## 9. Kiểm thử tự động & Xác minh toàn vẹn hệ thống

SDNFlowGuard trang bị bộ kiểm thử toàn diện với **79 bài test tự động** nhằm đảm bảo tính ổn định và tính đúng đắn trước khi phát hành:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

Quy trình xác minh trải qua 5 cổng kiểm tra nghiêm ngặt:

1. **[1/5] Kiểm tra cú pháp Python in-memory (`scripts/verify_syntax.py`):** Kiểm tra AST và biên dịch bytecode trong bộ nhớ cho toàn bộ 86 tệp mã nguồn Python backend, tuyệt đối không tạo bất kỳ thư mục rác `__pycache__` hay tệp `.pyc` nào trên đĩa.
2. **[2/5] CLI Self-Tests (4/4 module độc lập):** Xác minh thuật toán Monitor V2, bộ phân tích tcpdump Step 63, đối soát bằng chứng Step 64, và chính sách Defense Policy với $0$ cuộc gọi mạng ra bên ngoài.
3. **[3/5] Bộ kiểm thử tự động Automated Test Suite (79 Tests):**
   - **Contract Tests (5 tests):** Kiểm chứng tính tương thích của JSON payload gửi sang ONOS REST API và cấu trúc phản hồi cho Frontend.
   - **Integration Tests (22 tests):** Kiểm tra toàn diện Flask REST API, cơ chế tiếp nhận Webhook, kho lưu trữ SQLite, và tính năng xuất báo cáo.
   - **Safety Tests (14 tests):** Kiểm tra cơ chế chống tiêm quy tắc độc hại (Anti-Rogue), bảo vệ Gateway/DNS, xác nhận chế độ `DRY_RUN`, và khả năng tự phục hồi khi tiêm lỗi.
   - **Unit Tests (37 tests):** Kiểm thử chi tiết từng thuật toán tính điểm rủi ro, phân loại nhật ký SIEM, cửa sổ trượt, và chính sách phòng thủ.
   - **End-to-End Pipeline (1 test):** Kiểm tra chu trình khép kín từ lúc nhận mẫu lưu lượng đến khi đối soát bằng chứng Step 64 và kích hoạt Safety Gate.
4. **[4/5] Kiểm tra Production Bundle Frontend:** Xác thực tính nguyên vẹn của bản build React production tại `frontend/build/index.html`.
5. **[5/5] Kiểm tra tính bất biến của cơ sở dữ liệu SQLite:** Xác thực tính toàn vẹn qua lệnh `PRAGMA integrity_check` và đối soát mã băm SHA-256 bất biến:
   ```text
   3909de520f89ea050e7858104c8aa17bddd94d06af9db5ad84652404b9463fe9
   ```

---

## 10. Cấu trúc thư mục dự án

```text
Nhom02_SDNFlowGuard/
├── backend/                       # Mã nguồn Flask API, bộ điều phối phòng thủ và kiểm thử
│   ├── app/                       # Flask application factory, controller actions, routes, chatbot
│   ├── collectors/                # Bộ thu thập dữ liệu lưu lượng mạng (Monitor V1 & V2)
│   ├── defense/                   # Mô-đun phân tích Step 63, đối soát Step 64, và Safety Gate
│   ├── sdnflowguard/              # Kiến trúc phân lớp miền (Domain models, policies, settings)
│   ├── tests/                     # 79 bài automated tests (contracts, integration, safety, unit, e2e)
│   └── requirements.txt           # Danh mục thư viện phụ thuộc Python
├── frontend/                      # Mã nguồn giao diện người dùng React 18
│   ├── public/                    # Logo thương hiệu nguyên bản, favicon và index.html
│   ├── src/                       # Components, Pages, Ngữ cảnh song ngữ (LanguageContext), CSS
│   └── package.json               # Cấu hình gói và thư viện giao diện React
├── database/                      # Cơ sở dữ liệu SQLite sdnflowguard.db & bản sao lưu .bak
├── infrastructure/                # Cấu hình Logstash pipeline và tệp compose phụ trợ
├── scripts/                       # Bộ công cụ tự động hóa PowerShell & Python
│   ├── manage.ps1                 # Script quản trị toàn diện hệ thống (up, down, status, check, open...)
│   ├── test.ps1                   # Master test runner thực thi 5 cổng kiểm tra chất lượng
│   └── verify_syntax.py           # Công cụ kiểm tra cú pháp Python in-memory, không sinh .pyc
├── docs/                          # Tài liệu kỹ thuật, kiến trúc và kết quả kiểm thử
├── screenshots/                   # Hình ảnh tài liệu và logo SDNFlowGuard nguyên bản (260px)
├── docker-compose.yml             # Tệp cấu hình Docker Compose chuẩn duy nhất cho 6 container
├── .env.example                   # Mẫu cấu hình biến môi trường an toàn (không chứa mật khẩu thật)
├── LICENSE                        # Giấy phép phần mềm nguồn mở MIT License
└── README.md                      # Tài liệu hướng dẫn kỹ thuật chính thức của dự án
```

---

## 11. Xử lý sự cố thường gặp (Troubleshooting)

| Tình huống phát sinh | Nguyên nhân gốc rễ | Dấu hiệu nhận biết | Biện pháp xử lý an toàn |
| :--- | :--- | :--- | :--- |
| **Lỗi `error during connect` khi chạy PowerShell** | Docker Desktop chưa khởi động hoàn tất hoặc pipe kết nối bị gián đoạn. | Xuất hiện thông báo lỗi đỏ `open //./pipe/docker_engine`. | Mở Docker Desktop, chờ biểu tượng góc dưới chuyển sang màu xanh lá (*Engine running*), sau đó chạy lại lệnh. |
| **Truy cập cổng 8181 báo `HTTP 403 Forbidden`** | Người dùng truy cập vào thư mục gốc `http://127.0.0.1:8181/` thay vì đường dẫn servlet UI. | Trình duyệt hiển thị trang lỗi 403 của Jetty Server. | **Bắt buộc nhập đúng URL:** `http://127.0.0.1:8181/onos/ui` để mở giao diện quản trị ONOS. |
| **Truy cập cổng 6653 báo `ERR_EMPTY_RESPONSE`** | Người dùng dùng trình duyệt web để mở cổng kết nối OpenFlow 1.3 của switch. | Trình duyệt không tải được trang và ngắt kết nối ngay lập tức. | Cổng `6653` là kênh socket TCP nhị phân dành riêng cho Switch OpenFlow kết nối về Controller; tuyệt đối không mở bằng trình duyệt web. |
| **Logstash cổng 18080 chỉ hiển thị chữ `ok`** | Mở webhook endpoint của Logstash bằng phương thức `GET` trên trình duyệt. | Trình duyệt hiển thị trang văn bản trắng với duy nhất một từ `ok`. | Đây là phản hồi probe chuẩn của Elastic HTTP input plugin; webhook nhận dữ liệu qua `POST`. Để xem dữ liệu, hãy truy cập Kibana (`5601`). |
| **Lỗi PowerShell báo `running scripts is disabled`** | Hệ điều hành Windows áp dụng chính sách ExecutionPolicy giới hạn thực thi script. | Lỗi đỏ `File ... cannot be loaded because running scripts is disabled`. | Luôn thực thi các script kèm cờ bỏ qua chính sách: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\<ten_script>.ps1`. |
| **Hệ thống chạy chậm hoặc tràn RAM** | Chạy đầy đủ cả 6 container trên máy tính có bộ nhớ hạn chế ($\le$ 8 GB RAM). | Máy tính đơ lag hoặc container bị tắt do cơ chế OOM Killer. | Dừng hệ thống (`manage.ps1 down`) và khởi động lại với chế độ tiết kiệm bộ nhớ: `manage.ps1 up -SkipKibana`. |

---

## 12. Ranh giới an ninh & Giới hạn vận hành

- **Chế độ phòng vệ mặc định (DRY_RUN):** Để đảm bảo tính sẵn sàng cao của hạ tầng mạng, SDNFlowGuard mặc định khởi chạy ở chế độ mô phỏng an toàn (`DRY_RUN`). Trong chế độ này, các cảnh báo bất thường và quy tắc kiểm soát lưu lượng chỉ được xuất dưới dạng bản xem trước cấu hình (Staged Proposal) mà không can thiệp luồng dữ liệu thực tế.
- **Ranh giới bảo vệ hạ tầng (Safety Boundary):** Thuật toán Safety Gate ngăn chặn tuyệt đối việc can thiệp vào Router/Gateway mặc định (`10.0.0.254`), hệ thống máy chủ phân giải tên miền DNS (`8.8.8.8`, `1.1.1.1`), hoặc chặn toàn bộ dải mạng cục bộ (Subnet wide block).
- **Phạm vi triển khai:** SDNFlowGuard được thiết kế, tối ưu hóa và kiểm chứng phục vụ mục đích nghiên cứu học thuật, phòng thí nghiệm an ninh mạng và các mô hình giả lập mạng ảo hóa SDN. Không sử dụng trực tiếp để điều khiển các hạ tầng mạng vật lý cấp doanh nghiệp khi chưa hoàn thành kiểm toán bảo mật và cấu hình xác thực khóa API chuyên dụng (`SDNFLOW_API_KEY`).

---

## 13. Giấy phép sử dụng & Bản quyền (License)

Dự án được phân phối chính thức dưới giấy phép phần mềm nguồn mở **MIT License**.

```text
MIT License

Copyright (c) 2025 Jia Yang
Copyright (c) 2026 SDNFlowGuard Research & Development Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

Chi tiết điều khoản bản quyền xem tại tệp [`LICENSE`](LICENSE).
