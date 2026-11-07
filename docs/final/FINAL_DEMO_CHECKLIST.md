# FINAL DEMO RUNBOOK & CHECKLIST — SDNFLOWGUARD

**Đề tài:** Nghiên cứu và triển khai phòng thủ mạng tự động qua SDN tích hợp giám sát bằng ELK Stack  
**Học viên:** Phan Phát Đạt (Nhóm 02)  
**Ngày:** 05/11/2026  
**Thời lượng đề xuất:** 10 – 15 phút  

---

## 1. BẢNG KIỂM TRA TRƯỚC KHI BẢO VỆ (PRE-DEMO CHECKLIST)

- [ ] **Docker Desktop:** Đang hoạt động, 4 container UP (`sdnflowguard-onos`, `sdnflowguard-elasticsearch`, `sdnflowguard-logstash`, `sdnflowguard-kibana`).
- [ ] **Mininet:** Đang chạy SingleSwitchTopo ($k=2$) trong WSL Ubuntu-26.04.
- [ ] **Flask API:** Đang lắng nghe trên `http://127.0.0.1:5000` (`mode: DRY_RUN`).
- [ ] **React Frontend:** Đang lắng nghe trên `http://127.0.0.1:3000`.
- [ ] **Trình duyệt Web:** Đã mở sẵn 2 tab:
  - Tab 1: `http://localhost:3000` (SDNFlowGuard Dashboard).
  - Tab 2: `http://localhost:5601` (Kibana SIEM Overview).
- [ ] **Tập lệnh kiểm chứng sức khỏe:**
  ```powershell
  & "D:\Project\Nhom02_SDNFlowGuard\scripts\verify_system_health.ps1"
  ```
  *(Yêu cầu cả 7 port hiển thị `[ONLINE]` và SQLite SHA-256 khớp `3909de52...fe9`).*

---

## 2. KỊCH BẢN TRÌNH DIỄN CHI TIẾT (10 BƯỚC)

1. **Bước 1 — Giới thiệu tổng quan kiến trúc (1–2 phút):**
   - Mở slide số 5 và giới thiệu 4 mặt phẳng SDN: Data Plane (Mininet OVS), Control Plane (ONOS), Management Plane (Flask/React), Security/Monitoring Plane (ELK SIEM).
2. **Bước 2 — Trình diễn giao diện Dashboard (1 phút):**
   - Mở `http://localhost:3000`, chỉ ra nhận diện thương hiệu SDNFlowGuard: Logo chiếc khiên mạng, thanh trạng thái kết nối các node.
3. **Bước 3 — Trình diễn Topology mạng SDN (1 phút):**
   - Mở trang **Network Topology**, chứng minh nhận dạng trực tiếp từ ONOS: Switch `of:0000000000000001`, Host `h1` (10.0.0.1) trên port 1, Host `h2` (10.0.0.2) trên port 2.
4. **Bước 4 — Trình diễn thông tuyến Mininet Baseline (1 phút):**
   - Trong terminal Mininet: Thực hiện `h1 ping -c 3 10.0.0.2`, kết quả 0.0% packet loss, RTT 11.4 ms.
5. **Bước 5 — Trình diễn Telemetry thời gian thực (2 phút):**
   - Quan sát số gói `rx_packets` và số byte `rx_bytes` tăng trưởng trên giao diện điều khiển React Dashboard.
6. **Bước 6 — Trình diễn giám sát tập trung qua ELK / Kibana (2 phút):**
   - Mở `http://localhost:5601`, vào Kibana Discover, trình diễn 119 bản ghi an ninh lịch sử đã được chuẩn hóa theo định dạng Elastic Common Schema (ECS).
7. **Bước 7 — Trình diễn phân tích tương quan bằng chứng Step 64 (2 phút):**
   - Mở trang **Anomaly Detection**, trình diễn cơ chế đối chiếu IP-MAC-Port để giải quyết vấn đề nhập nhằng host ("Attached Host != Verified Attacker").
8. **Bước 8 — Trình diễn cổng an toàn SDN Safety Gate (1 phút):**
   - Trình diễn việc gọi API kiểm tra địa chỉ Whitelist (Gateway, Controller) để chứng minh hệ thống không bao giờ tự ý chặn các trạm hạ tầng mạng.
9. **Bước 9 — Trình diễn cơ chế DRY RUN phòng thủ tự động (2 phút):**
   - Trình diễn hành động tạo quy tắc phòng thủ, hệ thống sinh ra bản xem trước (Flow Rule Preview) có độ ưu tiên cao (`priority: 40010`) và thời gian timeout 300s mà không ngắt mạng thật của switch.
10. **Bước 10 — Báo cáo kết quả kiểm thử tự động (1 phút):**
    - Mở terminal chạy `scripts/run_all_tests.ps1`, chứng minh 50/50 unit/integration tests PASS trong dưới 1 giây, cơ sở dữ liệu toàn vẹn 100%.

---

## 3. XỬ LÝ NHANH SỰ CỐ TẠI BUỔI BẢO VỆ (EMERGENCY RECOVERY)
- Nếu ONOS không kết nối OVS:
  ```powershell
  docker exec sdnflowguard-onos rm -rf /root/onos/apache-karaf-4.2.14/data/db/partitions
  docker restart sdnflowguard-onos
  ```
- Nếu Flask Backend bị dừng:
  ```powershell
  $env:SDNFLOW_DEFENSE_MODE="DRY_RUN"
  & "D:\Project\Nhom02_SDNFlowGuard\backend\venv\Scripts\python.exe" -B D:\Project\Nhom02_SDNFlowGuard\backend\run.py
  ```

