# SDNFlowGuard V21 — Sổ tay Hướng dẫn Trình diễn Thực nghiệm (Final Demonstration Runbook)

**Học phần:** Chuyên đề - Hệ thống mạng và bảo mật  
**Đề tài:** Nghiên cứu và triển khai phòng thủ mạng tự động qua SDN tích hợp giám sát bằng ELK Stack  
**Tổ chức:** Khoa Công nghệ Thông tin - Trường Đại học Giao thông Vận tải TP.HCM (UTH)  
**Tác giả:** Nhóm 02  
**Phiên bản:** Release Candidate V21  
**Mục tiêu:** Hướng dẫn các thành viên trong nhóm thực hiện bài thuyết trình và trình diễn thực nghiệm (Live Demo) trực tiếp trước Hội đồng chấm chuyên đề một cách mạch lạc, thuyết phục và an toàn.

---

## 1. Danh mục Địa chỉ Truy cập Dịch vụ (Service Access Directory)

| Phân hệ / Dịch vụ | Địa chỉ URL truy cập | Tài khoản / Mật khẩu | Chức năng chính |
|---|---|---|---|
| **Frontend Operations Dashboard** | `http://localhost:3000` | N/A (Giao diện mở) | Bảng điều khiển trung tâm 7 phân hệ của SDNFlowGuard. |
| **ONOS Controller Web GUI** | `http://localhost:8181/onos/ui` | `onos` / `rocks` | Giám sát đồ thị topo mạng, switch, host và luồng OpenFlow 1.3. |
| **Kibana Observability Dashboard** | `http://localhost:5601` | N/A (Mặc định mở) | Khám phá và trực quan hóa telemetry từ Elasticsearch. |
| **Backend API Technical Reference** | `http://localhost:5000/docs` | N/A | Tài liệu đặc tả các REST API endpoints của Flask Backend. |
| **Elasticsearch Cluster REST** | `http://localhost:9200` | N/A (HTTP REST JSON) | Kiểm tra sức khỏe cụm phân tán Elasticsearch. |
| **Logstash Ingestion Webhook** | `http://localhost:18080` | N/A (HTTP POST) | Cổng tiếp nhận telemetry và sự kiện bất thường từ ONOS. |
| **ONOS OpenFlow Southbound** | `127.0.0.1:6653` | Giao thức TCP OpenFlow 1.3 | Cổng kết nối southbound của các switch OVS Mininet. |

---

## 2. Kiểm tra Tiền trạm trước Buổi Báo cáo (Pre-flight Inspection)

Trước khi bắt đầu bài thuyết trình 5 phút, mở PowerShell tại thư mục gốc `D:\Project\Nhom02_SDNFlowGuard` và chạy 2 lệnh kiểm tra nhanh:

### Bước 2.1. Kiểm tra 7 cổng mạng dịch vụ:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\manage.ps1 check
```
*Kết quả kỳ vọng:* Toàn bộ 7 cổng dịch vụ (3000, 5000, 8181, 6653, 9200, 5601, 18080) báo `[ONLINE]`, CSDL SQLite hash báo `[PASS]`, và Overall Status báo `READY`.

### Bước 2.2. Kiểm tra hạ tầng mạng Mininet:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\manage.ps1 status-topo
```
*Kết quả kỳ vọng:* Báo `Active Switches: 6`, `Active Hosts: 9`, `Directed Links: 10`, `[HEALTHY] Full 6-switch reference topology active and discovered`.

---

## 3. Kịch bản Trình diễn 6 Bước trước Hội đồng (Step-by-Step Demo Scenarios)

### KỊCH BẢN 1: Giám sát Tôpô Mạng SDN Thời gian thực (Traffic Overview & ONOS Topology)
1. **Thao tác:** Mở trình duyệt tại `http://localhost:3000/traffic-overview`.
2. **Thuyết minh:**
   - Hệ thống phát hiện mạng SDN gồm 6 switch OpenFlow 1.3 và 9 trạm làm việc (hosts) được bố trí theo cấu trúc cây phân tầng (Core switches `s1`, `s2` và Distribution switches `s3` đến `s6`).
   - Mở đồng thời tab `http://localhost:8181/onos/ui` (đăng nhập `onos`/`rocks`, nhấn phím `H` và `/` để hiện đồ thị và nhãn host) để chứng minh tính đồng bộ 100% giữa giao diện ứng dụng và bộ điều khiển controller ONOS.
   - Bảng **Live ONOS Flow Rules** bên dưới hiển thị đúng 24 luật luồng đang nạp trên các switch. Giải thích rõ: Các luật thuộc Core Controller (`org.onosproject.core`) khớp theo `ETH_TYPE` nên các cột IP hiển thị `--` là hoàn toàn đúng bản chất kỹ thuật OpenFlow 1.3, không hề có dữ liệu giả mạo.

### KỊCH BẢN 2: Truyền thông Mạng Cơ sở & Thu thập Telemetry (Normal Traffic & ELK Ingestion)
1. **Thao tác:** Trên máy trạm, mở terminal kiểm tra lệnh ping giữa các host Mininet:
   ```powershell
   wsl.exe -d Ubuntu-26.04 -u root bash -c "mnexec -a 4413 ping -c 3 10.0.0.2"
   ```
2. **Thuyết minh:**
   - Host `h1` (`10.0.0.1`) gửi 3 gói tin ICMP tới Host `h2` (`10.0.0.2`) với tỷ lệ mất gói 0%, thời gian trễ RTT trung bình 15.5 ms.
   - Chuyển sang tab **Kibana Discover** (`http://localhost:5601`): Chọn chỉ mục `sdnflowguard-events-*`.
   - Chỉ cho Hội đồng thấy 145 tài liệu đo đạc đã được thu thập: 106 bản ghi đo thông lượng cổng switch (`sdn_port_traffic`) và 11 bản ghi cảnh báo an ninh (`sdn_anomaly_alert`).

### KỊCH BẢN 3: Phân tích Gói tin & Đối chiếu Nhận dạng Host (Step 64 Host Evidence Correlation)
1. **Thao tác:** Chuyển sang trang **Anomaly Detection** (`http://localhost:3000/anomaly-detection`).
2. **Thuyết minh:**
   - Trình bày điểm độc đáo của đề tài: Trong mạng SDN, một cảnh báo lưu lượng tăng cao trên cổng switch (`Port Anomaly`) **chưa đủ để khẳng định host gắn vào cổng đó là kẻ tấn công** (`Attached Host != Attacker`).
   - Phân hệ Step 64 thực hiện đối chiếu 2 tầng: Bóc tách gói tin capture thực tế (`observed_source_mac`, `observed_source_ip`) và đối sánh với danh bạ Host của ONOS.
   - Kết quả: Hệ thống đưa ra quyết định `OBSERVE` (Tiếp tục giám sát), không chặn nhầm máy trạm hợp lệ, thể hiện tính cẩn trọng và chuẩn mực an toàn cao của giải pháp.

### KỊCH BẢN 4: Mô phỏng Can thiệp Phòng thủ & Safety Gate (DRY_RUN Defense Intervention)
1. **Thao tác:** Chuyển sang trang **Manual Traffic Control** (`http://localhost:3000/manual-control`).
2. **Thực hiện:**
   - Chọn hành động: `Block Traffic (Drop)`.
   - Nhập Source IP: `10.0.0.2` (hoặc `10.0.0.2/32`).
   - Nhấn **Apply Network Policy**.
3. **Thuyết minh:**
   - Hệ thống phản hồi tức thì với huy hiệu xanh: `[DRY_RUN] Simulated block traffic for 10.0.0.2/32 (no ONOS change)`.
   - Xem trước luật luồng (Policy Preview): Thể hiện đầy đủ cấu trúc JSON gồm selector `IPV4_SRC: 10.0.0.2/32` và treatment `DROP`.
   - Nhấn mạnh trước Hội đồng: Hệ thống hoạt động ở chế độ `DRY_RUN`, Safety Gate đánh giá tính hợp lệ nhưng **không cài luật DROP thật xuống switch**, nhờ đó mạng Mininet không bị mất kết nối ngoài ý muốn trong quá trình vận hành thử nghiệm.

### KỊCH BẢN 5: Kiểm toán Quyết định & Lưu vết Hành động (Decision Logs & Audit Trail)
1. **Thao tác:** Chuyển sang trang **Decision Logs** (`http://localhost:3000/decision-logs`).
2. **Thuyết minh:**
   - Mọi hành vi can thiệp hoặc mô phỏng đều được ghi vết kiểm toán minh bạch trong cơ sở dữ liệu SQLite.
   - Hệ thống quản lý 89 quyết định can thiệp lịch sử, phân định rõ ràng giữa các hành động tự động (`Automated`) và can thiệp từ quản trị viên (`Admin`).

### KỊCH BẢN 6: Trung tâm Báo cáo An ninh & Xuất PDF Pháp chứng (Security Reports & Audit Center)
1. **Thao tác:** Chuyển sang trang **Security & Traffic Reports** (`http://localhost:3000/reports`).
2. **Thực hiện & Thuyết minh:**
   - Giải thích thiết kế V20/V21: Trang được xây dựng theo chuẩn trung tâm điều hành SOC với 4 thẻ KPI động và thanh công cụ đa tầng.
   - Khi ở bộ lọc mặc định `Last 30 Days`: Bảng hiển thị thông báo Empty State chuyên nghiệp với số liệu 0 sự cố, phản ánh trung thực rằng trong 30 ngày qua không có sự cố mạng nào ngoài tầm kiểm soát trong phòng lab.
   - Nhấn nút **"Xem toàn bộ lịch sử (All Time)"**: Toàn bộ 8 sự kiện bất thường và 89 quyết định phòng thủ lịch sử lập tức hiển thị.
   - Lọc theo khoảng thời gian đề tài: Chọn `Range: Custom Range`, nhập từ ngày `24/10/2026` đến `24/11/2026`, nhấn `Apply Filters`.
   - Nhấn nút **"Download PDF Report"**: Tải về tệp PDF A4 chuẩn pháp chứng. Mở tệp PDF lên để Hội đồng quan sát tiêu đề báo cáo, bảng dữ liệu phân trang, zebra shading và số trang `Page X of Y`.

---

## 4. Hướng dẫn Chụp ảnh Minh chứng Bổ sung (Hình 4.13 & 4.14)

Để hoàn thiện phụ lục báo cáo học phần:
- **Hình 4.13:** Truy cập `http://localhost:3000/reports`, chọn `Dataset: SDN Defense Decisions`, chọn `Time Range: Custom Range` (`24/10/2026` đến `24/11/2026`), nhấn `Apply Filters`. Dùng công cụ Snipping Tool chụp toàn màn hình trình duyệt.
- **Hình 4.14:** Nhấn nút **Download PDF Report**, mở tệp PDF vừa tải trong trình duyệt hoặc Adobe Acrobat, phóng to vừa vặn khổ trang và chụp lại trang 1 của tài liệu.

---

## 5. Quy trình Ứng phó Sự cố Khẩn cấp trong Buổi Báo cáo (Troubleshooting & Emergency Rollback)

| Hiện tượng | Nguyên nhân có thể | Thao tác xử lý khẩn cấp (dưới 10 giây) |
|---|---|---|
| **Mất kết nối Backend (Badge Offline)** | Container backend bị treo hoặc khởi động lại | Mở PowerShell chạy: `docker restart sdnflowguard-backend` |
| **ONOS không nhận đủ 6 switch** | Mininet topology trong WSL2 bị dừng | Mở PowerShell chạy: `powershell -File scripts\manage.ps1 start-topo` |
| **Giao diện React không cập nhật** | Cache trình duyệt lưu trữ bundle cũ | Nhấn tổ hợp phím `Ctrl + F5` hoặc `Ctrl + Shift + R` để tải lại trang trắng bộ nhớ đệm |
| **Tải PDF báo lỗi 500** | Lỗi định dạng ngày tùy chọn sai logic | Nhấn nút `Reset Filters` trên thanh công cụ để đưa về cấu hình chuẩn `Last 30 Days` |
| **Kibana báo lỗi kết nối Elasticsearch** | Cụm Elasticsearch đang khởi động lại chỉ mục | Chờ 10 giây hoặc kiểm tra: `curl http://localhost:9200/_cluster/health` |
