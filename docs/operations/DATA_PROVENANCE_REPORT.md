# SDNFlowGuard V21 — Báo cáo Nguồn gốc Dữ liệu & Pháp chứng Số (Data Provenance & Digital Forensics Report)

**Học phần:** Chuyên đề - Hệ thống mạng và bảo mật  
**Đề tài:** Nghiên cứu và triển khai phòng thủ mạng tự động qua SDN tích hợp giám sát bằng ELK Stack  
**Tổ chức:** Khoa Công nghệ Thông tin - Trường Đại học Giao thông Vận tải TP.HCM (UTH)  
**Tác giả:** Nhóm 02  
**Thời điểm lập báo cáo:** 23/11/2026 21:30 UTC+07:00  
**Tệp cơ sở dữ liệu chính:** `database/sdnflowguard.db` (SHA-256: `4be8f31ebdfefc2ab136c0671452375e8d0d8f9ad005901b905a852bc5fa23ac`)

---

## 1. Tuyên bố Liêm chính Học thuật & Nguyên tắc Pháp chứng (Academic Integrity Statement)

Trong nghiên cứu an toàn thông tin và điều tra số (Digital Forensics), **dấu thời gian (Timestamp) và nguồn gốc dữ liệu (Provenance) là tài sản bất biến**. Việc can thiệp, sửa đổi hoặc làm sai lệch dấu thời gian của các dữ liệu mẫu lịch sử để ngụy tạo thành sự kiện mới phát sinh trong giai đoạn triển khai dự án (24/10/2026 – 24/11/2026) là hành vi vi phạm nghiêm trọng chuẩn mực nghiên cứu khoa học.

Báo cáo này công bố chi tiết nguồn gốc của mọi bản ghi dữ liệu tồn tại trong hệ thống SDNFlowGuard, phân định rõ ràng giữa:
1. **Dữ liệu mẫu lịch sử (Historical Fixtures):** Dữ liệu chuẩn hóa tạo ra trong quá trình thiết kế và kiểm thử ban đầu (năm 2024–2025).
2. **Dữ liệu giám sát thực tế (Observed Telemetry):** Các gói tin và luồng dữ liệu thu thập qua cảm biến và đường ống ELK Stack trong năm 2026.
3. **Dữ liệu thực nghiệm tái lặp (Reproducible Experiment Data):** Các bài đo kiểm chứng trực tiếp trên hạ tầng mạng Mininet / ONOS Controller thực hiện vào ngày 23/11/2026.

---

## 2. Chuẩn hóa Mô hình Thời gian trong Hệ thống (Time Model Standardization)

Để loại bỏ hoàn toàn sự mập mờ giữa thời điểm phát sinh sự kiện và thời điểm vận hành hệ thống, SDNFlowGuard phân định 4 khái niệm thời gian độc lập:

```
+-------------------+       +-----------------------+       +---------------------+       +-----------------------+
|    EVENT TIME     |  -->  |    OBSERVATION TIME   |  -->  |    INGESTION TIME   |  -->  |    EXPERIMENT TIME    |
| (Thời điểm xảy ra |       | (Thời điểm cảm biến   |       | (Thời điểm ghi vào  |       | (Thời điểm kỹ sư tiến |
|  tấn công/sự cố)  |       |  ghi nhận gói tin)    |       |  CSDL hoặc Index)   |       |  hành kịch bản đo)    |
+-------------------+       +-----------------------+       +---------------------+       +-----------------------+
```

1. **Event Time (`event_time_utc`):** Thời điểm khách quan mà hành vi an ninh mạng diễn ra tại nguồn (ví dụ: cuộc quét cổng diễn ra lúc `2025-01-13 01:24:13`).
2. **Observation Time (`observed_at_utc`):** Thời điểm thiết bị mạng hoặc cảm biến OpenFlow/Suricata/Zeek nhìn thấy gói tin đầu tiên trên giao diện switch (ví dụ: dấu thời gian trong tệp pcap/tcpdump `ingress_icmp_20261101_014645.json`).
3. **Ingestion Time (`ingested_at_utc`):** Thời điểm hệ thống Backend API hoặc Logstash tiếp nhận, chuẩn hóa và lưu bản ghi vào CSDL SQLite hoặc chỉ mục Elasticsearch (`@timestamp`).
4. **Experiment Time (`experiment_time`):** Thời điểm nhà nghiên cứu thực hiện bài thử nghiệm kiểm chứng trong môi trường phòng lab (ví dụ: ngày 23/11/2026).

---

## 3. Kiểm toán Chi tiết Kho Dữ liệu SQLite (`database/sdnflowguard.db`)

Cơ sở dữ liệu SQLite cục bộ được bảo toàn toàn vẹn với giá trị băm SHA-256:  
`4BE8F31EBDFEFC2AB136C0671452375E8D0D8F9AD005901B905A852BC5FA23AC`.

### 3.1. Phân tích Bảng Sự kiện An ninh (`events` - 8 bản ghi)

Bảng `events` chứa đúng 8 bản ghi, hình thành từ các đợt thử nghiệm giai đoạn 2024–2025:

| Event ID | Timestamp gốc | Source IP | Destination IP | Anomaly Type | Risk Score | Cảm biến nguồn (`source`) | Phân loại dữ liệu (Provenance) |
|---|---|---|---|---|---|---|---|
| **1** | `2024-09-01 10:00` | `192.168.1.10` | `192.168.1.1` | Port Scanning | 75 | Netflow | `HISTORICAL_FIXTURE` (Bộ kiểm thử mẫu) |
| **2** | `2024-09-01 10:15` | `192.168.1.20` | `192.168.1.2` | Brute Force Attempt | 90 | AD-logs | `HISTORICAL_FIXTURE` (Bộ kiểm thử mẫu) |
| **3** | `2024-09-01 10:30` | `192.168.1.30` | `192.168.1.3` | Malware Upload | 85 | Honeypot | `HISTORICAL_FIXTURE` (Bộ kiểm thử mẫu) |
| **4** | `2024-09-01 10:45` | `192.168.1.15` | `192.168.1.4` | DNS Spike | 80 | dns-logs | `HISTORICAL_FIXTURE` (Bộ kiểm thử mẫu) |
| **5** | `2024-09-01 11:00` | `192.168.1.25` | `192.168.1.5` | Unusual Process | 60 | EDR | `HISTORICAL_FIXTURE` (Bộ kiểm thử mẫu) |
| **7** | `2024-10-01 10:00` | `10.0.0.11` | `10.0.0.12` | Port Scanning | 75 | Netflow | `HISTORICAL_FIXTURE` (Kiểm thử tôpô mạng 10.0.0.x) |
| **8** | `2025-01-03 10:00` | `10.0.0.11` | `10.0.0.12` | Port Scanning | 75 | Netflow | `HISTORICAL_FIXTURE` (Kiểm thử tôpô mạng 10.0.0.x) |
| **9** | `2025-01-13 01:24:13` | `10.0.0.2` | `10.0.0.3` | Port Scanning | 31 | AD-logs | `OBSERVED_TELEMETRY` (Thu thập từ Host h2) |

**Kết luận kiểm toán:**  
Toàn bộ 8 bản ghi này đều được giữ nguyên timestamp ban đầu. Khi người dùng lọc báo cáo theo mặc định `Last 30 Days` (tính đến tháng 11/2026), các sự kiện này không hiển thị vì chúng thuộc về năm 2024–2025. Chúng chỉ hiển thị khi người dùng chọn `All Time` hoặc thiết lập `Custom Range` bao hàm mốc thời gian đó.

### 3.2. Phân tích Bảng Quyết định Phòng thủ (`actions` - 93 bản ghi)

Bảng `actions` chứa 93 quyết định can thiệp mạng:
- **89 bản ghi lịch sử (2024–2025):** Phân bố từ `2024-09-01 11:45` đến `2025-01-17 16:49:32`.
  - `Redirect`: 50 bản ghi (Chuyển hướng luồng nghi ngờ sang Honeypot `10.0.0.6` hoặc switch trung gian `of:...03`).
  - `Rate Limit`: 32 bản ghi (Áp dụng hạn chế băng thông xuống 50 bps hoặc 100 kbps).
  - `Block`: 6 bản ghi (Đề xuất chặn địa chỉ IP `10.0.0.1/32`, `10.0.0.2/32`, `192.168.1.20`).
  - `Unblock`: 1 bản ghi (Gỡ bỏ chính sách chặn).
- **4 bản ghi thực nghiệm can thiệp an ninh trực tiếp (23/11/2026):**
  - Action IDs: 90, 91, 92, 93.
  - Timestamp: `2026-11-23 10:15:20`, `2026-11-23 10:15:22`, `2026-11-23 17:38:05`, `2026-11-23 17:40:15`.
  - Action Type: `Block [DRY_RUN]`.
  - Target IP: `10.0.0.2/32`.
  - Initiation Source: `Admin`.
  - Reason: `Blocked traffic for 10.0.0.2/32 to None. [DRY_RUN]`.
- **Trạng thái thực thi:** Trong chế độ phòng thủ mặc định `DRY_RUN`, toàn bộ các hành động được Safety Gate phê duyệt và gắn nhãn `[DRY_RUN] (SIMULATED)`, hiển thị đầy đủ và đồng bộ 100% giữa hai giao diện Decision Logs (93 bản ghi) và Security Reports (93 bản ghi trên All Time, 4 bản ghi trên Last 30 Days).

---

## 4. Kiểm toán Chi tiết Kho Dữ liệu Elasticsearch (ELK Stack)

Trên cụm phân tán Elasticsearch (`http://127.0.0.1:9200`), chỉ mục `sdnflowguard-events-*` lưu trữ đúng **145 tài liệu** trong khung thời gian triển khai chính thức của đề tài (tháng 10–11/2026):

### 4.1. Phân bố theo Chỉ mục Ngày:
- `sdnflowguard-events-2026.10.31`: 119 tài liệu
- `sdnflowguard-events-2026.11.05`: 6 tài liệu
- `sdnflowguard-events-2026.11.07`: 18 tài liệu
- `sdnflowguard-events-2026.11.08`: 2 tài liệu
- **Tổng cộng:** **145 tài liệu (Docs)** (Khớp 100% với Hình 4.7 Kibana Discover).

### 4.2. Phân loại Bản chất Kỹ thuật của 145 Tài liệu:
Dựa trên kết quả chạy aggregation theo trường `event_type.keyword`:
1. `sdn_port_traffic`: **106 tài liệu (73.1%)**  
   *Bản chất:* Dữ liệu đo đạc thông lượng định kỳ (Periodic Telemetry Metrics) từ các cổng của switch `of:0000000000000001` (RX/TX packets, RX/TX bytes, RX/TX Mbps, PPS). Đây **không phải là các cuộc tấn công mạng**.
2. `sdn_anomaly_alert`: **11 tài liệu (7.6%)**  
   *Bản chất:* Cảnh báo an ninh mạng do bộ giám sát Reliable Monitor V1/V2 phát hiện khi lưu lượng vượt ngưỡng PPS định trước (ví dụ: Peak 9.555 PPS so với ngưỡng 8.0 PPS).
3. `sdn_topology_snapshot`: **5 tài liệu (3.4%)**  
   *Bản chất:* Ảnh chụp trạng thái tôpô thiết bị từ ONOS REST API.
4. `pipeline_test`, `VERIFICATION_PROBE`, `perf_probe`, `test_probe`: **4 tài liệu (2.8%)**  
   *Bản chất:* Gói tin kiểm tra sức khỏe đường ống Logstash và khả năng chịu tải của Elasticsearch.

**Kết luận pháp chứng quan trọng:**  
Không được đồng nhất con số 145 tài liệu trên Kibana thành 145 cuộc tấn công an ninh mạng. Trong báo cáo khóa luận, nhóm khẳng định rõ: Hệ thống ghi nhận 106 bản ghi đo đạc vi mô và 11 cảnh báo bất thường trong giai đoạn thử nghiệm tháng 10–11/2026.

---

## 5. Thực nghiệm Tái lặp Ngày 23/11/2026 (Reproducible Live Lab Experiments)

Để bổ sung bằng chứng thực nghiệm thời gian thực trong giai đoạn bảo vệ đề tài, nhóm đã tiến hành các bài đo kiểm trực tiếp trên môi trường ảo hóa Mininet kết nối ONOS:

### 5.1. Experiment 01: Normal Traffic Baseline (Đo thông lượng cơ sở)
- **Thời điểm thực hiện:** `2026-11-23 19:23:43 UTC+07:00` (`12:23:43 UTC`).
- **Môi trường:** Mininet trên WSL2 Ubuntu-26.04 (`sdnflowguard-topo.service`).
- **Lệnh điều khiển:** `mnexec -a 4413 ping -c 3 10.0.0.2` (Từ Host h1 sang Host h2).
- **Kết quả thu được:**
  ```text
  PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
  64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=44.4 ms
  64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=2.05 ms
  64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=0.082 ms

  --- 10.0.0.2 ping statistics ---
  3 packets transmitted, 3 received, 0% packet loss, time 2003ms
  rtt min/avg/max/mdev = 0.082/15.515/44.414/20.450 ms
  ```
- **Xác minh ONOS:** Bộ đếm gói tin trên switch `s1` (`of:0000000000000001`) và flow rules tăng trưởng chính xác 3 packets, khẳng định đường truyền mạng thông suốt.

### 5.2. Experiment 02: DRY_RUN Defense Staging (Mô phỏng can thiệp)
- **Thời điểm thực hiện:** `2026-11-23 19:25:00 UTC+07:00`.
- **Hành động:** Gửi yêu cầu chặn `10.0.0.2/32` qua Backend API `/api/block`.
- **Đánh giá Safety Gate:**
  - Kiểm tra Target IP `10.0.0.2`: Không thuộc nhóm IP được bảo vệ (Gateway `10.0.0.254`, DNS `8.8.8.8`).
  - Chế độ phòng thủ: `DRY_RUN`.
  - Phản hồi: `dry_run: true`, `executed: false`, `status: APPROVAL_REQUIRED`.
  - Kiểm tra ONOS REST: **0 luật DROP mới** được đẩy xuống switch, đảm bảo an toàn tuyệt đối cho mạng Mininet.

---

## 6. Tổng kết Quy tắc Phân loại Dữ liệu trong Báo cáo Đề tài

Khi trình bày báo cáo hoặc trả lời câu hỏi của Hội đồng nghiệm thu:
1. **Các sự kiện năm 2024–2025 trong CSDL:** Được giải thích là bộ dữ liệu kiểm thử chuẩn hóa (Historical Test Fixtures) và nhật ký các lần chạy thử nghiệm trước đó, được bảo toàn để phục vụ kiểm toán hồi quy.
2. **145 bản ghi trên Kibana:** Được giải thích là kho lưu trữ telemetry bao gồm 106 bản ghi đo thông lượng cổng switch và 11 cảnh báo an ninh thời gian thực thu nhận từ đường ống Logstash trong giai đoạn 31/10/2026 – 08/11/2026.
3. **Bài thử nghiệm ngày 23/11/2026:** Minh chứng cho việc hệ thống tiếp tục vận hành sống (Live System), các switch và host Mininet liên lạc thông suốt với tỷ lệ mất gói 0%, và cơ chế Safety Gate hoạt động chính xác theo thiết kế.
