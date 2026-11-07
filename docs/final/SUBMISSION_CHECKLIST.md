# Final Submission & Defense Readiness Checklist — Nhom02_SDNFlowGuard

| # | Hạng mục kiểm tra | Trạng thái | Bằng chứng xác minh |
|---|---|---|---|
| 1 | Dọn dẹp an toàn các file `.bak` trùng lặp/lỗi thời vào Recycle Bin kèm bản sao lưu ngoài workspace | **COMPLETED** | `D:\Project\_SDNFlowGuard_Cleanup_Rollback\session_20261105_013300` (`33` files, `0` functional regression) |
| 2 | Snapshot toàn bộ dự án trước khi refactor và bản sao lưu Step 65 ngoài workspace | **COMPLETED** | `D:\Project\_SDNFlowGuard_Cleanup_Rollback\pre_refactor_20261105_020500` & `D:\Project\_SDNFlowGuard_TestFix_Rollback\20261105_125619` |
| 3 | Sử dụng đúng Python `3.10.10` (`backend\venv\Scripts\python.exe`) với cờ `-B` (`0` file `.pyc` phát sinh) | **VERIFIED** | `scripts/verify_system_health.ps1` (`EXIT 0`) |
| 4 | Bảo toàn nguyên vẹn `database/sdnflowguard.db` (`SHA-256: 3909de520f89ea050e7858104c8aa17bddd94d06af9db5ad84652404b9463fe9`) và `database/netsecflow.db.bak` | **VERIFIED** | `safety/test_checkpoint_integrity.py` (`PASS`) |
| 5 | Bảo toàn nguyên vẹn 4 file checkpoint trong `backend/collectors/state/` và bằng chứng Step 63 + Step 72 trong `backend/defense/evidence/` | **VERIFIED** | `safety/test_checkpoint_integrity.py` (`PASS`) & `docs/evidence/EVIDENCE_INDEX_AND_STEP64_REPORT.md` |
| 6 | Hoàn thiện Step 64 ONOS Host Evidence Correlator (`backend/defense/onos_host_evidence_correlator.py`) và xác minh trực tiếp với `LIVE_ONOS` | **VERIFIED** | `Topology source: LIVE_ONOS`, `CORROBORATED_HOST_OBSERVATION` trên cả 2 cổng |
| 7 | Kiến trúc Clean Architecture (`backend/sdnflowguard/`) theo Strangler Pattern, tương thích ngược 100% | **VERIFIED** | `docs/architecture/CLEAN_ARCHITECTURE_DESIGN.md` |
| 8 | Loại bỏ mật khẩu cứng trong `backend/run.py`, tạo `.env.example` và `backend/.env.example` không chứa secret | **VERIFIED** | `safety/test_no_secret_leakage.py` (`PASS`) |
| 9 | Cổng an toàn Active Defense Safety Gate mặc định `DRY_RUN`, chặn cảnh báo `test_only` và bảo vệ IP hạ tầng (`127.0.0.1`, Controller, ELK) | **VERIFIED** | `unit/test_safety_gate.py`, `safety/test_dry_run_default.py`, `safety/test_test_alert_never_blocks.py` (`PASS`) |
| 10 | Chuẩn hóa nhật ký SIEM đa nguồn (ONOS `VERIFIED_LAB_INTEGRATION`, Firewall & Windows Server `FIXTURE_SIMULATION`) | **VERIFIED** | `unit/test_siem_log_normalizer.py` (`PASS`) |
| 11 | Hoàn thiện Frontend ReactJS trên cổng `3000` và Backend Flask trên cổng `5000` | **VERIFIED** | `npm.cmd run build` (`EXIT 0`), toàn bộ 7 cổng dịch vụ `[ONLINE]` |
| 12 | Khôi phục và xác minh trực tiếp Lab Docker ONOS (`8181`, `6653`), ELK (`9200`, `18080`, `5601`) và Mininet/OVS (`WSL Ubuntu-26.04`) | **VERIFIED** | `PingAll: 0.0% packet loss`, `sdnflowguard-events-2026.10.31` nguyên vẹn |
| 13 | Kiểm thử 5 kịch bản End-to-End thực tế (`SCENARIO 01` → `SCENARIO 05`) và bộ `50/50` bài kiểm thử tự động | **VERIFIED** | `docs/testing/TEST_PLAN_AND_RESULTS.md`, `scripts/run_all_tests.ps1` (`50/50 PASS`) |
| 14 | Báo cáo đồ án chuyên đề Word & PDF 76 trang (`BAO_CAO_DO_AN_CHUYEN_DE_SDNFLOWGUARD.docx/.pdf`), Slide thuyết trình 15 trang (`THUYET_TRINH_DO_AN_SDNFLOWGUARD.pptx/.pdf`), và gói nộp chuẩn hóa `D:\Project\SDNFlowGuard_Final_Submission` | **COMPLETED** | 76 trang Word/PDF, 15 slides PPTX/PDF, 2,075 files across 7 directories |
