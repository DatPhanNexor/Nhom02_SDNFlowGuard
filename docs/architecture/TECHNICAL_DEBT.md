# Danh Mục Nợ Kỹ Thuật, Bảo Mật Và Vận Hành (Technical Debt Audit)

Bảng kiểm toán dưới đây liệt kê toàn bộ các vấn đề kỹ thuật, bảo mật và vận hành được phát hiện qua quá trình đọc mã nguồn thực tế tại `D:\Project\Nhom02_SDNFlowGuard`.

---

## 1. Bảo Mật & Cấu Hình (Security & Configuration Debt)

| Mã | Mức độ | Vị trí | Mô tả chi tiết | Giải pháp khắc phục |
| :--- | :--- | :--- | :--- | :--- |
| **SEC-01** | **CRITICAL** | `backend/run.py:71-73` | Hardcode địa chỉ ELK cũ (`192.168.102.1:9200`), tài khoản và mật khẩu văn bản thuần trong endpoint `/api/get-documents-by-ip`. | Loại bỏ hoàn toàn mật khẩu hardcode khỏi mã nguồn; chuyển sang đọc từ biến môi trường (`SDNFLOW_ELK_URL`, `SDNFLOW_ELK_USER`, `SDNFLOW_ELK_PASSWORD`) và cấu hình trung tâm; cung cấp `.env.example`. |
| **SEC-02** | **HIGH** | `backend/app/reception.py:11-27`, `backend/app/decision.py:55-113` | Endpoint `/webhook` không có xác thực, không kiểm tra replay/duplicate `event_id`, không chặn sự kiện `test_only=True`, tự động gọi `process_event()` kích hoạt lệnh chặn/chuyển hướng mạng khi tổng điểm vượt ngưỡng. Además `run_webhook()` bật `debug=True` trên `0.0.0.0`. | Áp dụng kiểm tra dữ liệu đầu vào, chống phát lại (`event_id` deduplication), chặn thực thi tự động với `test_only=True`, tích hợp cổng an toàn (`SDNFLOW_DEFENSE_MODE=DRY_RUN` mặc định), tắt `debug=True`. |
| **SEC-03** | **HIGH** | `backend/run.py:318-477` | Các API điều khiển mạng (`/api/block`, `/api/allow`, `/api/rate-limit`, `/api/redirect`, `/api/redirectHoney`, `/api/unblock`) chưa có cổng kiểm soát an toàn (`Safety Gate`), chưa kiểm tra IP bảo vệ (controller/loopback/allowlist) và chưa hỗ trợ xác thực API key tùy chọn. | Bổ sung middleware kiểm tra API key (`SDNFLOW_API_KEY` khi bật chế độ bảo vệ), kiểm tra allowlist/controller IP, mặc định chạy qua `Safety Gate` (`DRY_RUN` trừ khi được phê duyệt rõ ràng) và trả về `request_id` kèm trạng thái xác minh. |
| **SEC-04** | **MEDIUM** | `backend/app/controller_actions.py:12-13`, `backend/app/app_logging.py:6-7` | Tài khoản ONOS để trống `''`/`''` trong khi ONOS lab yêu cầu thông tin xác thực từ biến môi trường (`ONOS_USER`/`ONOS_PASSWORD`, mặc định lab `onos`/`rocks`). | Chuẩn hóa việc lấy thông tin kết nối ONOS qua cấu hình trung tâm (`SDNFLOW_ONOS_USER` / `ONOS_USER`) và đọc động `SDN Controller IP` từ cấu hình/SQLite. |
| **SEC-05** | **MEDIUM** | `backend/run.py:42,56,79,93...` | Trả trực tiếp chuỗi ngoại lệ nội bộ `str(e)` về client trong một số lỗi `500`, có nguy cơ lộ đường dẫn tệp hoặc cấu trúc nội bộ. | Chuẩn hóa xử lý lỗi qua lớp phản hồi an toàn, ẩn chi tiết nhạy cảm và ghi nhật ký có cấu trúc (structured log). |

---

## 2. Kiến Trúc, Độ Tin Cậy & Phòng Thủ SDN (Architecture & Reliability Debt)

| Mã | Mức độ | Vị trí | Mô tả chi tiết | Giải pháp khắc phục |
| :--- | :--- | :--- | :--- | :--- |
| **ARCH-01** | **HIGH** | `backend/defense/*` | Bước 63 đã hoàn thành trích xuất bằng chứng gói tin ICMP (`source_ip_evidence_analyzer.py`), nhưng chưa có module **Bước 64 — ONOS Host Evidence Correlation** để đối chiếu `switch_id`, `ingress_port`, `MAC`, `IP` với topology ONOS và xử lý các trường hợp đa host trên 1 cổng, giả mạo/đổi IP-MAC, cổng bị tắt hoặc thiếu ngày/múi giờ. | Xây dựng module tương quan bằng chứng Bước 64 (`onos_host_evidence_correlator.py` & `sdnflowguard/domain/services/evidence_correlation.py`) và tích hợp vào `sdn_defense_policy.py` cùng REST API. |
| **ARCH-02** | **HIGH** | `backend/app/controller_actions.py`, `topology.py`, `app_logging.py`, `reception.py` | Gọi truy vấn SQLite và khởi tạo kết nối ngay lúc `import` module; dùng đường dẫn tương đối `sys.path.insert(1, 'app/')` phụ thuộc thư mục đứng chạy lệnh. | Chuyển sang truy vấn cấu hình động theo từng request/use-case; chuẩn hóa đường dẫn tuyệt đối dựa trên `Path(__file__).resolve()`; tách kiến trúc Clean Architecture (`backend/sdnflowguard/`). |
| **ARCH-03** | **HIGH** | `backend/app/controller_actions.py:82,173,184,224...` | Các lời gọi `requests.get`/`post`/`delete` tới ONOS không có `timeout`, dễ gây treo worker Flask nếu ONOS không phản hồi; báo thành công ngay khi gửi request mà không xác minh rule thực tế trên ONOS và không có cơ chế rollback. | Bổ sung timeout bắt buộc, kiểm tra kết quả trả về từ ONOS, xác minh rule sau thực thi (`Rule Verification`) và lưu thông tin rule để hỗ trợ `Rollback`. |
| **ARCH-04** | **MEDIUM** | `backend/app/controller_actions.py:14,164,411,575` | Ghi file JSON cấu hình intent vào đường dẫn cứng `C:\netsecflow\backend\app\` hoặc thư mục hiện hành. | Chuyển sang lưu trữ trong thư mục runtime được quản lý an toàn hoặc gửi payload JSON trực tiếp qua bộ nhớ kèm bản ghi audit. |
| **ARCH-05** | **MEDIUM** | `backend/app/report.py:20,88` | Dùng `datetime.fromisoformat()` không xử lý hậu tố `Z` trên Python 3.10 và gọi `pdfkit.from_string()` gây lỗi `500` nếu máy chưa cài binary `wkhtmltopdf`. | Chuẩn hóa bộ phân tích thời gian hỗ trợ mọi định dạng ISO-8601/SQLite và bổ sung bộ sinh PDF thuần Python chuẩn `%PDF-1.4` khi không có `wkhtmltopdf`. |

---

## 3. Giao Diện Frontend & Vận Hành (Frontend & DevOps Debt)

| Mã | Mức độ | Vị trí | Mô tả chi tiết | Giải pháp khắc phục |
| :--- | :--- | :--- | :--- | :--- |
| **FE-01** | **MEDIUM** | `frontend/src/components/Header.js:13` | Nút `<button>Logout</button>` không gắn hàm xử lý, khiến người dùng hiểu nhầm hệ thống có phiên đăng nhập/đăng xuất. | Thay thế nút Logout giả bằng nhãn hiển thị trạng thái vận hành thực tế (`Defense Mode: DRY_RUN` / trạng thái kết nối API). |
| **FE-02** | **MEDIUM** | `frontend/src/components/Sidebar.js:14-46` | Sử dụng prop `activeClassName="active"` của React Router v5 trên thư viện `react-router-dom` v6 (`^6.26.1`). | Cập nhật sang hàm `className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}` chuẩn React Router v6. |
| **FE-03** | **MEDIUM** | `frontend/src/pages/*.js` | URL API hardcode rải rác giữa `http://localhost:5000` và `http://127.0.0.1:5000`; thiếu hiển thị kết quả đối chiếu bằng chứng Bước 64, chế độ `DRY_RUN`, xác minh rule và rollback trên giao diện. | Tập trung cấu hình API vào `frontend/src/config/apiConfig.js`; nâng cấp các trang `Dashboard`, `AnomalyDetection`, `ManualTrafficControl`, `DecisionLogs`, `Reports`, `SystemSettings`. |
| **OPS-01** | **LOW** | `infrastructure/compose.yaml` & `infrastructure/elk/compose.yaml` | Tồn tại 2 file Docker Compose cùng định nghĩa container `sdnflowguard-elasticsearch` và volume `sdnflowguard-elasticsearch-data` (một bên `external: true`, một bên không). | Chuẩn hóa tài liệu và script khởi động để sử dụng `infrastructure/compose.yaml` làm cấu hình chính, giữ `infrastructure/elk/compose.yaml` cho trường hợp khởi tạo/chạy độc lập ELK và cảnh báo không chạy chồng chéo. |

