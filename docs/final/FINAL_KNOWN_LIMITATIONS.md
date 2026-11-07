# FINAL KNOWN LIMITATIONS & ACADEMIC BOUNDARIES — SDNFLOWGUARD

**Đề tài:** Nghiên cứu và triển khai phòng thủ mạng tự động qua SDN tích hợp giám sát bằng ELK Stack  
**Học viên:** Phan Phát Đạt (Nhóm 02)  
**Ngày:** 05/11/2026  

Tài liệu này ghi nhận trung thực các giới hạn kỹ thuật và ranh giới nghiên cứu của đồ án, tuân thủ nguyên tắc liêm chính học thuật (Academic Integrity):

---

## 1. Giới hạn can thiệp thời gian thực (Stage B Active Enforcement)
- **Hiện trạng:** Hệ thống vận hành mặc định ở chế độ `SDNFLOW_DEFENSE_MODE=DRY_RUN` (Stage A).
- **Lý do chấp nhận:** Trong môi trường phòng thí nghiệm mô phỏng Mininet + ONOS, việc tự động đẩy OpenFlow Drop Rule vào switch thật mà không có sự kiểm duyệt của con người có thể làm ngắt kết nối giữa controller và switch, hoặc làm cô lập hoàn toàn các trạm mạng thử nghiệm. Do đó, việc duy trì khóa `AWAITING_OPERATOR_APPROVAL` là quyết định thiết kế an toàn (Fail-Safe by Default).
- **Phạm vi đã kiểm chứng:** Toàn bộ thuật toán sinh Flow Rule, kiểm tra hợp lệ, chống quy tắc độc hại (Anti-Rogue), và tính tương thích với API của ONOS Controller đã được kiểm chứng 100% qua bộ kiểm thử hợp đồng (`test_onos_payload_contracts.py`).

---

## 2. Mô phỏng dữ liệu SIEM đa nguồn (FIXTURE_SIMULATION)
- **Hiện trạng:** Module `siem_log_normalizer.py` hỗ trợ chuẩn hóa dữ liệu từ Firewall Syslog (pfSense/iptables) và Windows Security Event Log (Event ID 4625/4624/5156).
- **Lý do chấp nhận:** Phòng thí nghiệm không triển khai thiết bị phần cứng Firewall vật lý chuyên dụng hoặc máy chủ Active Directory vật lý. Các dữ liệu này được đưa vào qua các bộ dữ liệu mẫu (Fixtures) và được đánh nhãn tường minh `"integration_status": "FIXTURE_SIMULATION"`.
- **Phạm vi đã kiểm chứng:** Bộ chuẩn hóa tuân thủ 100% cấu trúc Elastic Common Schema (ECS), trích xuất chính xác các trường `source.ip`, `destination.ip`, `network.transport`, và gắn điểm rủi ro chuẩn xác.

---

## 3. Môi trường mạng mô phỏng (Mininet trên WSL2)
- Mạng truyền thông gồm 1 switch OVS kết nối 2 host vật lý ảo hóa. Khi khởi động lại máy chủ hoặc Docker Desktop, dải mạng NAT ảo của WSL/Docker có thể thay đổi, đòi hỏi kiểm tra phân vùng Raft cache của ONOS theo hướng dẫn trong [RUNBOOK.md](file:///D:/Project/Nhom02_SDNFlowGuard/docs/operations/RUNBOOK.md).

