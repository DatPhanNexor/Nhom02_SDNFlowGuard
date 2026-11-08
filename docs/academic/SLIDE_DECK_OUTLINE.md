# ĐỀ CƯƠNG BÀI THUYẾT TRÌNH BẢO VỆ ĐỒ ÁN (30 SLIDES)
## ĐỀ TÀI: NGHIÊN CỨU VÀ TRIỂN KHAI PHÒNG THỦ MẠNG TỰ ĐỘNG QUA SDN TÍCH HỢP GIÁM SÁT BẰNG ELK STACK
### Học phần: Chuyên đề – Hệ thống mạng và bảo mật (Mã HP: 123046)
### Cơ sở đào tạo: Trường Đại học Giao thông vận tải TP. Hồ Chí Minh (UTH) — Khoa Công nghệ thông tin
### Sinh viên thực hiện: Phan Phát Đạt — Nhóm 02

---

### TIÊU CHUẨN ĐỊNH DẠNG (THEO DETAI.PDF & QUY ĐỊNH UTH):
- **Số lượng slides:** 30 slides (thỏa mãn khung bắt buộc 25–40 slides của `DeTai.pdf`).
- **Cỡ chữ tiêu đề (Title):** 32pt Bold.
- **Cỡ chữ nội dung (Body):** 24–26pt.
- **Mẫu trình bày:** UTH Corporate Blue/Navy & Gold Identity.

---

### DANH SÁCH CHI TIẾT 30 SLIDES BẢO VỆ:

1. **Slide 01 — Trang bìa chính thức (Mẫu UTH):**
   - Đơn vị: Trường Đại học Giao thông vận tải TP.HCM (UTH) — Khoa CNTT.
   - Tên đồ án: NGHIÊN CỨU VÀ TRIỂN KHAI PHÒNG THỦ MẠNG TỰ ĐỘNG QUA SDN TÍCH HỢP GIÁM SÁT BẰNG ELK STACK (SDNFlowGuard).
   - Sinh viên: Phan Phát Đạt — Nhóm 02.
2. **Slide 02 — Mục lục & Cấu trúc bài báo cáo:**
   - 4 phần chính: Cơ sở lý thuyết, Mô hình triển khai lab, 4 Kịch bản tấn công - phòng thủ, Kết quả kiểm thử tự động & Kết luận.
3. **Slide 03 — Đặt vấn đề & Tính cấp thiết đề tài:**
   - Thách thức DoS/DDoS và thám sát mạng; độ trễ phát hiện trong hạ tầng truyền thống; nhu cầu giám sát tập trung và phản ứng tự động.
4. **Slide 04 — Nghịch lý phòng thủ SDN cốt lõi:**
   - Nguyên lý: `Attached Host != Verified Attacker`.
   - Cổng switch nhận luồng lưu lượng lớn chưa chắc là nguồn tấn công (nguy cơ DoS tự thân nếu chặn nhầm).
5. **Slide 05 — Mục tiêu nghiên cứu & Cam kết đề tài:**
   - Giám sát chuỗi thời gian ELK Stack; điều khiển SDN ONOS Controller; chuỗi đối soát bằng chứng Step 63/64; Safety Gate & Rollback.
6. **Slide 06 — Chuẩn đầu ra (CLO) & Đối chiếu học phần:**
   - CLO1 (Lý thuyết an toàn mạng), CLO2 (Triển khai & đánh giá giải pháp), CLO3 (Tự nghiên cứu & làm việc độc lập).
7. **Slide 07 — Tổng quan kiến trúc SDN & OpenFlow 1.3:**
   - Phân tách Control Plane và Data Plane; cơ chế Flow Table, Flow Rule và Meter Band trong OpenFlow 1.3.
8. **Slide 08 — Bộ điều khiển mạng SDN Controller (ONOS):**
   - ONOS 2.7.0 LTS; REST API `:8181`; Host Discovery; Intent Framework và OpenFlow Channel `:6653`.
9. **Slide 09 — Ngăn xếp giám sát an ninh SIEM (ELK Stack):**
   - Elasticsearch 8.11 (lưu trữ chỉ mục `sdnflowguard-events-*`), Logstash (tiếp nhận HTTP `:18080`), Kibana `:5601`.
10. **Slide 10 — Kiến trúc tổng thể 4 mặt phẳng (Data, Control, Security, Application):**
    - Sơ đồ tích hợp Mininet/OVS, ONOS Controller, ELK Stack và Flask Backend/React Frontend.
11. **Slide 11 — Thiết kế Clean Architecture Backend:**
    - Tách biệt 4 tầng: Domain Policies, Application Use Cases, Infrastructure Adapters, Presentation Interfaces.
12. **Slide 12 — Pipeline thu thập dữ liệu & Telemetry mạng:**
    - `onos_port_elk_collector.py` định kỳ lấy mẫu thống kê byte/packet, tính toán delta PPS/MBPS và đẩy về Logstash.
13. **Slide 13 — Thuật toán phát hiện bất thường tin cậy (Monitor V1 & V2):**
    - Ngưỡng PPS động, chuỗi vượt ngưỡng liên tiếp (`consecutive_samples`), xử lý dữ liệu đến trễ bằng cửa sổ trượt 30 giây.
14. **Slide 14 — Phân tích gói tin & Trích xuất bằng chứng (Step 63):**
    - Trích xuất Layer 2 (MAC) và Layer 3 (IP) từ file bắt gói tại cổng vào switch (`s1-eth1`); bảo toàn chuỗi chứng cứ số.
15. **Slide 15 — Động cơ đối soát bằng chứng nguồn ONOS (Step 64):**
    - Correlator đối chiếu host bắt gói với vị trí kết nối trên ONOS; phân loại `CORROBORATED` vs `AMBIGUOUS` vs `IDENTITY_MISMATCH`.
16. **Slide 16 — Cổng an toàn (Safety Gate) & Đánh giá rủi ro:**
    - 5 chốt kiểm tra fail-safe: Chống chặn IP hạ tầng (Gateway `10.0.0.254`, DNS `8.8.8.8`/`1.1.1.1`), loại trừ `test_only`, yêu cầu bằng chứng.
17. **Slide 17 — Ranh giới vận hành: Stage A (DRY RUN) & Stage B (LIVE ENFORCE):**
    - Stage A: Sinh dự thảo Flow Rule/Meter Band an toàn, xem trước mà không can thiệp thiết bị.
    - Stage B: Khóa an toàn sau Operator Approval Gate, loại trừ rủi ro mất kết nối lab.
18. **Slide 18 — Bảng điều khiển quản trị ReactJS Dashboard:**
    - Trực quan hóa Topology, Live Flows, SDN Port Rates, Elk Port History Chart, Security Alerts Table, Chatbot hỗ trợ.
19. **Slide 19 — Mô hình thực nghiệm Lab Mininet & Open vSwitch:**
    - Môi trường Windows 11 + WSL2 Ubuntu-26.04; Open vSwitch 3.7.1; kết nối ONOS qua OpenFlow 1.3; kiểm chứng thông tuyến ping 0% loss.
20. **Slide 20 — Kịch bản 1: Mạng bình thường & Đo lường Baseline:**
    - Giao tiếp giữa các trạm `h1` và `h2`; quyết định ALLOW; không phát sinh cảnh báo giả.
21. **Slide 21 — Kịch bản 2: Tấn công DoS / TCP SYN Flood:**
    - Phân tích cơ chế chiếm dụng hàng đợi TCB; sinh luật phòng vệ ACL DENY và Flow Rule xem trước.
22. **Slide 22 — Kịch bản 3: Tấn công ICMP Flood & Bắt gói tin:**
    - Bơm lưu lượng ICMP tốc độ cao; vượt ngưỡng PPS cổng switch; bắt gói tin Step 63 và ghi nhận 119 sự kiện vào Elasticsearch.
23. **Slide 23 — Kịch bản 4: Tấn công giả mạo ARP Spoofing / MITM:**
    - Phân tích hành vi giả mạo MAC/IP; Step 64 Correlator phát hiện `IDENTITY_MISMATCH` và cách ly trạm giả mạo.
24. **Slide 24 — Kịch bản 5: Thám sát Port Scan & Chuẩn hóa SIEM:**
    - Chuẩn hóa Syslog tường lửa và Windows Event Log theo Elastic Common Schema (ECS), gắn nhãn minh bạch `FIXTURE_SIMULATION`.
25. **Slide 25 — Cơ chế hoàn nguyên chính sách phòng thủ (Rollback):**
    - Hoàn nguyên luật chặn tức thì qua `/api/defense/rollback`; xác minh xóa rule trên ONOS; loại bỏ trạng thái thành công giả.
26. **Slide 26 — Kết quả kiểm thử tự động toàn diện (79/79 Tests PASS):**
    - 79 bài kiểm thử unit/integration/safety/contract/e2e đạt 100% PASS trong ~0.9s; 4/4 CLI self-tests PASS; SQLite DB SHA-256 nguyên vẹn.
27. **Slide 27 — So sánh giải pháp & Giá trị thực tiễn:**
    - So sánh với Snort/Suricata và tường lửa tĩnh; ưu điểm can thiệp Data Plane tức thời và loại bỏ chặn nhầm qua Step 64.
28. **Slide 28 — Đóng góp của đề tài & Hướng phát triển:**
    - Đáp ứng 100% mục tiêu đồ án học phần; hoàn thiện quy trình Giám sát – Phòng vệ – Đánh giá; hướng tới SDN Spine-Leaf đa switch.
29. **Slide 29 — Tổng kết tiêu chuẩn nghiệm thu & Minh chứng:**
    - Bản bàn giao kép (Official Academic Submission 4 thư mục + Technical Audit Submission 7 phân vùng); tính toàn vẹn mã hóa SHA-256.
30. **Slide 30 — Trang kết thúc & Phiên hỏi đáp (Q&A):**
    - Lời cảm ơn Hội đồng chấm thi và sẵn sàng bước vào phần trả lời chất vấn chuyên môn.
