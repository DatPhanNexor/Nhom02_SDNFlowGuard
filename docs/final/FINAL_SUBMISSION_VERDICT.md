# FINAL SUBMISSION VERDICT — SDNFLOWGUARD

**Đề tài:** Nghiên cứu và triển khai phòng thủ mạng tự động qua SDN tích hợp giám sát bằng ELK Stack  
**Học phần:** Chuyên đề – Hệ thống mạng và bảo mật (Mã HP: 123046)  
**Đơn vị đào tạo:** Trường Đại học Giao thông vận tải TP. Hồ Chí Minh (UTH) — Khoa Công nghệ thông tin  
**Học viên:** Phan Phát Đạt (Nhóm 02)  
**Ngày:** 05/11/2026  

---

## 1. KẾT LUẬN NGHIỆM THU CUỐI CÙNG

# **READY_FOR_SUBMISSION**

Hệ thống **SDNFlowGuard** đã hoàn thành toàn bộ chu trình phát triển, kiểm thử, tích hợp thực nghiệm và đóng gói bàn giao theo đúng quy định của môn học Chuyên đề – Hệ thống mạng và bảo mật.

---

## 2. MA TRẬN PHÂN LOẠI 18 HẠNG MỤC BẮT BUỘC

| STT | Hạng mục | Trạng thái | Bằng chứng kỹ thuật | Còn thiếu |
| :---: | :--- | :---: | :--- | :---: |
| 1 | **Source Code** | **PASS** | Kiến trúc Clean Architecture, 0 syntax error (`compileall`), 0 conflict markers | Không |
| 2 | **Backend** | **PASS** | Flask API port 5000 online, 32 Flask routes, API `/api/health` status OK | Không |
| 3 | **Frontend** | **PASS** | React Dashboard port 3000, build production (`build/index.html`) 918 bytes | Không |
| 4 | **Database** | **PASS** | SQLite `sdnflowguard.db`, `PRAGMA integrity_check` = `ok`, SHA-256: `3909de52...fe9` | Không |
| 5 | **ONOS** | **PASS** | REST port 8181, OpenFlow port 6653, Switch `of:0000000000000001` active | Không |
| 6 | **Mininet** | **PASS** | WSL2 Ubuntu SingleSwitchTopo ($k=2$), pingAll loss = 0.0%, RTT 11.4 ms | Không |
| 7 | **ELK Stack** | **PASS** | Elasticsearch 8.11+ lưu 119 docs, Kibana port 5601 online, Logstash port 18080 | Không |
| 8 | **Monitor V1/V2** | **PASS** | Anomaly detector tính toán delta PPS, deduplication, streak validation | Không |
| 9 | **Evidence Correlation** | **PASS** | Step 64 phân tích tương quan L2/L3 IP-MAC-Port, phân biệt host attached | Không |
| 10 | **Defense Safety** | **PASS** | Safety Gate bảo vệ Gateway, Controller, DNS, ngăn chặn Rogue flow rule | Không |
| 11 | **Live Enforcement** | **PENDING_APPROVAL** | Stage A (DRY RUN) PASS 100%; Stage B (Live OVS block) khóa chờ phê duyệt | Phê duyệt tại buổi demo |
| 12 | **Four Attack Scenarios** | **PASS** | ICMP Flood (LIVE_VERIFIED Stage A), SYN Flood, ARP Spoof, Port Scan (SIMULATED) | Không |
| 13 | **Automated Tests** | **PASS** | 53/53 tests PASS trong ~0.65s, 4/4 CLI self-tests PASS, Zero Regression | Không |
| 14 | **Academic Report** | **PASS** | Báo cáo Word và PDF 72 trang A4 (vượt yêu cầu $\ge 60$ trang), chuẩn UTH, 6 ảnh | Không |
| 15 | **Presentation** | **PASS** | Bài thuyết trình PowerPoint và PDF 30 slide (đáp ứng khung 25–40 slides của `DeTai.pdf`) | Không |
| 16 | **Submission Package** | **PASS** | Gói chính thức UTH (`Nhom02_SDNFlowGuard_Official_Submission`) 4 thư mục chuẩn | Không |
| 17 | **SHA-256 Manifest** | **PASS** | Khớp 100% với `CHECKSUM_SHA256.txt` (2,054 files) và `SUBMISSION_PACKAGE_SHA256.txt` | Không |
| 18 | **Demo Readiness** | **PASS** | Script `run_demo.ps1` và `run_demo.bat`, kịch bản 4 bước demo 10–15 phút | Không |

---

## 3. Ranh giới an toàn Stage B (Live Active Defense)
Chế độ Stage B (đẩy Flow Rule ngắt lưu lượng mạng Mininet thật) được cấu hình khóa an toàn có chủ đích ở trạng thái `AWAITING_OPERATOR_APPROVAL` / `LIVE_ACTIVE_DEFENSE_NOT_EXECUTED`. Đây là thiết kế chủ động nhằm đảm bảo môi trường phòng thí nghiệm không bị gián đoạn ngoài tầm kiểm soát khi bảo vệ trước Hội đồng.
