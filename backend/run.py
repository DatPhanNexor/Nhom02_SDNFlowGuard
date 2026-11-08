import io
import os
from pathlib import Path
import sys
import time

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import requests

BACKEND_ROOT = Path(__file__).resolve().parent
APP_DIR = BACKEND_ROOT / "app"
for p in (str(BACKEND_ROOT), str(APP_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from app.app_logging import log_flows_to_database  # noqa: E402
from app.chatbot import handle_chatbot_request  # noqa: E402
from app.controller_actions import (  # noqa: E402
    allow_ip,
    block_ip,
    rate_limit_for_host,
    redirect_traffic_full,
    unblock_ip,
)
from app.database import (  # noqa: E402
    delete_event_entry,
    get_actions,
    get_anomalies,
    get_flows,
    get_setting_value,
    get_settings,
    init_db,
    save_settings,
)
from app.query_elastic import get_documents_by_ip  # noqa: E402
from app.reception import webhook  # noqa: E402
from app.report import ReportGenerator  # noqa: E402
from app.service_stat import get_service_status, get_logstash_pipeline_stats  # noqa: E402
from app.topology import get_topology_data  # noqa: E402
from sdnflowguard.domain.exceptions import ValidationError  # noqa: E402
from sdnflowguard.infrastructure.configuration.settings import AppSettings  # noqa: E402
from sdnflowguard.interfaces.http.routes import clean_api_bp  # noqa: E402
from sdnflowguard.interfaces.http.security import (  # noqa: E402
    check_api_key,
    validate_ip_input,
    validate_rate_input,
)

app = Flask(__name__)
report_generator = ReportGenerator()
PDF_DIRECTORY = str(BACKEND_ROOT / "generated_reports")

DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
]
env_cors = os.environ.get("SDNFLOW_CORS_ORIGINS")
allowed_origins = [o.strip() for o in env_cors.split(",") if o.strip()] if env_cors else DEFAULT_ALLOWED_ORIGINS
CORS(app, resources={r"/*": {"origins": allowed_origins}})

app.add_url_rule("/webhook", view_func=webhook, methods=["POST"])
app.register_blueprint(clean_api_bp)
init_db()


@app.route("/", methods=["GET"])
def api_index():
    """Root index providing service identification and navigation pointers."""
    return (
        jsonify(
            {
                "service": "SDNFlowGuard Backend API",
                "health_endpoint": "/api/health",
                "dashboard_url": "http://127.0.0.1:3000",
                "docs_url": "/docs",
                "message": "Backend API is available.",
            }
        ),
        200,
    )


@app.route("/docs", methods=["GET"])
def api_docs():
    """Technical REST API reference documentation for developers and operators."""
    html_content = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SDNFlowGuard — REST API Reference</title>
    <style>
        :root {
            --bg-primary: #0b1329;
            --bg-card: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --navy-header: #0f172a;
            --accent-blue: #0284c7;
            --accent-green: #059669;
            --badge-get: #0284c7;
            --badge-post: #10b981;
            --border-color: #e2e8f0;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #f8fafc;
            color: var(--text-main);
            line-height: 1.5;
        }
        header {
            background-color: var(--navy-header);
            color: #ffffff;
            padding: 24px 32px;
            border-bottom: 2px solid #1e293b;
        }
        .header-container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }
        .header-title h1 {
            font-size: 22px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        .header-title p {
            font-size: 13px;
            color: #94a3b8;
            margin-top: 4px;
        }
        .header-links a {
            display: inline-block;
            background: #1e293b;
            color: #38bdf8;
            text-decoration: none;
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            margin-left: 8px;
            transition: background 0.2s;
        }
        .header-links a:hover {
            background: #334155;
            color: #ffffff;
        }
        .container {
            max-width: 1200px;
            margin: 24px auto;
            padding: 0 20px;
        }
        .status-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 18px 24px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #ecfdf5;
            color: #065f46;
            padding: 6px 12px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 700;
        }
        .status-badge::before {
            content: '';
            display: inline-block;
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
        }
        .endpoint-table {
            width: 100%;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            border-collapse: collapse;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .endpoint-table th {
            background: #f1f5f9;
            text-align: left;
            padding: 12px 16px;
            font-size: 12px;
            font-weight: 700;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--border-color);
        }
        .endpoint-table td {
            padding: 14px 16px;
            border-bottom: 1px solid var(--border-color);
            font-size: 14px;
            vertical-align: top;
        }
        .endpoint-table tr:last-child td {
            border-bottom: none;
        }
        .endpoint-table tr:hover {
            background: #f8fafc;
        }
        .method-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 800;
            font-family: ui-monospace, monospace;
            text-transform: uppercase;
        }
        .method-badge.get { background: #e0f2fe; color: #0369a1; }
        .method-badge.post { background: #dcfce7; color: #15803d; }
        .endpoint-path {
            font-family: ui-monospace, monospace;
            font-weight: 700;
            color: #0f172a;
        }
        .endpoint-desc {
            color: var(--text-muted);
            font-size: 13px;
            margin-top: 2px;
        }
        .code-example {
            background: #f1f5f9;
            padding: 6px 10px;
            border-radius: 4px;
            font-family: ui-monospace, monospace;
            font-size: 12px;
            color: #334155;
            display: inline-block;
            margin-top: 4px;
        }
        footer {
            text-align: center;
            padding: 30px 20px;
            font-size: 12px;
            color: var(--text-muted);
        }
    </style>
</head>
<body>
    <header>
        <div class="header-container">
            <div class="header-title">
                <h1>SDNFlowGuard — REST API Reference</h1>
                <p>Mặt phẳng Điều phối An ninh & Giám sát Mạng SDN (Python Flask / Gunicorn)</p>
            </div>
            <div class="header-links">
                <a href="/api/health">Kiểm tra /api/health</a>
                <a href="http://127.0.0.1:3000">Giao diện Dashboard (Port 3000)</a>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="status-card">
            <div>
                <strong>Hạ tầng API:</strong> <code>127.0.0.1:5000</code> &bull; <strong>Chế độ:</strong> <code>Production WSGI (Gunicorn)</code> &bull; <strong>An toàn:</strong> <code>READ-ONLY AUDIT & DRY_RUN ENFORCED</code>
            </div>
            <div class="status-badge">API ENGINE ACTIVE</div>
        </div>

        <table class="endpoint-table">
            <thead>
                <tr>
                    <th style="width: 100px;">Phương thức</th>
                    <th>Đường dẫn Endpoint & Chức năng</th>
                    <th>Mô tả Phản hồi & Dữ liệu</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><span class="method-badge get">GET</span></td>
                    <td>
                        <div class="endpoint-path">/</div>
                        <div class="endpoint-desc">Service Root Index</div>
                    </td>
                    <td>Trả về thông tin định danh dịch vụ và link điều hướng dạng JSON (HTTP 200).</td>
                </tr>
                <tr>
                    <td><span class="method-badge get">GET</span></td>
                    <td>
                        <div class="endpoint-path">/docs</div>
                        <div class="endpoint-desc">Technical REST API Reference</div>
                    </td>
                    <td>Tài liệu đặc tả các giao diện lập trình ứng dụng RESTful của hệ thống (Trang hiện tại).</td>
                </tr>
                <tr>
                    <td><span class="method-badge get">GET</span></td>
                    <td>
                        <div class="endpoint-path">/api/health</div>
                        <div class="endpoint-desc">System Health Check</div>
                    </td>
                    <td>Kiểm tra sức khỏe dịch vụ, cơ sở dữ liệu SQLite, và cờ an toàn <code>DRY_RUN</code>.</td>
                </tr>
                <tr>
                    <td><span class="method-badge get">GET</span></td>
                    <td>
                        <div class="endpoint-path">/api/topology</div>
                        <div class="endpoint-desc">ONOS SDN Topology</div>
                    </td>
                    <td>Truy vấn danh sách Switch OpenFlow (OVS) và Host kết nối thời gian thực từ ONOS.</td>
                </tr>
                <tr>
                    <td><span class="method-badge get">GET</span></td>
                    <td>
                        <div class="endpoint-path">/api/live-flows</div>
                        <div class="endpoint-desc">Live Flow Rules</div>
                    </td>
                    <td>Lấy toàn bộ Flow Rules đang nạp trên các thiết bị chuyển mạch từ ONOS REST API.</td>
                </tr>
                <tr>
                    <td><span class="method-badge get">GET</span></td>
                    <td>
                        <div class="endpoint-path">/api/live-port-stats</div>
                        <div class="endpoint-desc">Port Traffic Counters</div>
                    </td>
                    <td>Thống kê số gói tin (packets) và byte truyền/nhận trên từng cổng của switch.</td>
                </tr>
                <tr>
                    <td><span class="method-badge get">GET</span></td>
                    <td>
                        <div class="endpoint-path">/api/service-status</div>
                        <div class="endpoint-desc">Controller & ELK Status</div>
                    </td>
                    <td>Kiểm tra trạng thái kết nối tới ONOS Controller (Port 8181) và Elasticsearch (Port 9200).</td>
                </tr>
                <tr>
                    <td><span class="method-badge get">GET</span></td>
                    <td>
                        <div class="endpoint-path">/api/get-settings</div>
                        <div class="endpoint-desc">System Settings</div>
                    </td>
                    <td>Lấy cấu hình địa chỉ IP Controller, ELK, Honeypot và chế độ phòng thủ từ SQLite.</td>
                </tr>
                <tr>
                    <td><span class="method-badge get">GET</span></td>
                    <td>
                        <div class="endpoint-path">/api/get-anomalies</div>
                        <div class="endpoint-desc">Security Anomalies</div>
                    </td>
                    <td>Lấy danh mục các sự kiện lưu lượng bất thường và tấn công mạng được ghi nhận.</td>
                </tr>
                <tr>
                    <td><span class="method-badge get">GET</span></td>
                    <td>
                        <div class="endpoint-path">/api/get-actions</div>
                        <div class="endpoint-desc">Defense Action Logs</div>
                    </td>
                    <td>Lấy lịch sử kiểm toán các quyết định phòng thủ (Block, Rate Limit, Rollback).</td>
                </tr>
                <tr>
                    <td><span class="method-badge get">GET</span></td>
                    <td>
                        <div class="endpoint-path">/api/get-flows</div>
                        <div class="endpoint-desc">Stored Flow Table</div>
                    </td>
                    <td>Lấy danh sách các luồng dữ liệu đã được lưu vết trong cơ sở dữ liệu cục bộ.</td>
                </tr>
                <tr>
                    <td><span class="method-badge post">POST</span></td>
                    <td>
                        <div class="endpoint-path">/api/block</div>
                        <div class="endpoint-desc">Mitigate Host (Safety Gate)</div>
                    </td>
                    <td>Yêu cầu chặn một địa chỉ IP nguồn khả nghi. Chế độ DRY_RUN lưu dự thảo chờ phê duyệt.</td>
                </tr>
                <tr>
                    <td><span class="method-badge post">POST</span></td>
                    <td>
                        <div class="endpoint-path">/api/rate-limit</div>
                        <div class="endpoint-desc">Meter Bandwidth Limiting</div>
                    </td>
                    <td>Áp dụng giới hạn tốc độ (OpenFlow 1.3 Meter) theo đơn vị bps chuyển đổi sang kbps.</td>
                </tr>
                <tr>
                    <td><span class="method-badge post">POST</span></td>
                    <td>
                        <div class="endpoint-path">/api/unblock</div>
                        <div class="endpoint-desc">Remove Host Block</div>
                    </td>
                    <td>Gỡ bỏ luật chặn an ninh đối với một địa chỉ IP đã xử lý xong.</td>
                </tr>
                <tr>
                    <td><span class="method-badge post">POST</span></td>
                    <td>
                        <div class="endpoint-path">/api/defense/rollback</div>
                        <div class="endpoint-desc">Rollback Defense Rule</div>
                    </td>
                    <td>Khôi phục trạng thái mạng, thu hồi Flow Rule can thiệp và kiểm chứng qua controller.</td>
                </tr>
                <tr>
                    <td><span class="method-badge post">POST</span></td>
                    <td>
                        <div class="endpoint-path">/api/chatbot</div>
                        <div class="endpoint-desc">SDN Security Assistant</div>
                    </td>
                    <td>Trợ lý an ninh mạng trả lời các câu hỏi về Topo, Flow, Cảnh báo và Trạng thái Controller.</td>
                </tr>
                <tr>
                    <td><span class="method-badge get">GET</span></td>
                    <td>
                        <div class="endpoint-path">/api/get-report</div>
                        <div class="endpoint-desc">Generate Audit Report</div>
                    </td>
                    <td>Xuất dữ liệu báo cáo dạng bảng theo các nhóm: Sự cố an ninh hoặc Hành động can thiệp.</td>
                </tr>
                <tr>
                    <td><span class="method-badge get">GET</span></td>
                    <td>
                        <div class="endpoint-path">/api/download-pdf</div>
                        <div class="endpoint-desc">Download PDF Report</div>
                    </td>
                    <td>Tải về báo cáo an ninh mạng chính thức định dạng PDF phục vụ thanh tra học thuật.</td>
                </tr>
                <tr>
                    <td><span class="method-badge get">GET</span></td>
                    <td>
                        <div class="endpoint-path">/api/elk/port-traffic-history</div>
                        <div class="endpoint-desc">Historical Telemetry</div>
                    </td>
                    <td>Truy vấn lịch sử lưu lượng cổng (PPS/BPS) từ Logstash pipeline lưu trong Elasticsearch.</td>
                </tr>
                <tr>
                    <td><span class="method-badge get">GET</span></td>
                    <td>
                        <div class="endpoint-path">/api/defense/evidence-correlation</div>
                        <div class="endpoint-desc">Step 64 Corroboration</div>
                    </td>
                    <td>Đối soát chéo dữ liệu bắt gói Step 63 với bảng cấu hình cổng vật lý của switch ONOS.</td>
                </tr>
            </tbody>
        </table>
    </div>

    <footer>
        SDNFlowGuard &bull; Trường Đại học Giao thông vận tải TP. Hồ Chí Minh (UTH) &bull; Khoa Công nghệ Thông tin
    </footer>
</body>
</html>"""
    return html_content, 200, {"Content-Type": "text/html; charset=utf-8"}




def _resolve_onos_auth():
    settings = AppSettings.from_env()
    user = settings.onos_user or os.getenv("ONOS_USER") or "onos"
    password = settings.onos_password or os.getenv("ONOS_PASSWORD") or "rocks"
    return (user, password) if (user or password) else None


def _resolve_elk_url_and_auth():
    settings = AppSettings.from_env()
    elk_ip = get_setting_value("ELK IP Address") or "127.0.0.1"
    base_url = os.environ.get("SDNFLOW_ELK_URL") or f"http://{elk_ip}:9200"
    auth = (
        (settings.elk_user, settings.elk_password)
        if (settings.elk_user and settings.elk_password)
        else None
    )
    return base_url.rstrip("/"), auth


@app.route("/api/chatbot", methods=["POST"])
def chatbot():
    payload = request.get_json(silent=True) or {}
    user_question = payload.get("question")
    locale = payload.get("locale") or payload.get("lang") or "vi"
    if not user_question or not str(user_question).strip():
        return jsonify({"error": "No question provided"}), 400
    if len(str(user_question)) > 1000:
        return jsonify({"error": "Question exceeds maximum length of 1000 characters."}), 400
    response = handle_chatbot_request(str(user_question), locale=str(locale))
    return jsonify({"answer": response}), 200


@app.route("/api/get-report", methods=["GET"])
def get_report():
    try:
        report_type = request.args.get("report_type", "anomalies")
        report_data = report_generator.generate_report(report_type)
        return jsonify(report_data), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/download-pdf", methods=["GET"])
def download_pdf():
    try:
        report_type = request.args.get("report_type", "anomalies")
        pdf_content = report_generator.generate_pdf_report(report_type)
        return send_file(
            io.BytesIO(pdf_content),
            as_attachment=True,
            download_name=f"{report_type}_report_monthly.pdf",
            mimetype="application/pdf",
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/get-documents-by-ip", methods=["POST"])
def get_documents():
    """Retrieve documents across all indices for a given IP address without hardcoded secrets."""
    data = request.get_json(silent=True) or {}
    ip_address = data.get("ip_address")
    if not ip_address:
        return jsonify({"error": "IP address is required"}), 400
    try:
        validate_ip_input(ip_address, "ip_address")
    except ValidationError as exc:
        return jsonify({"error": exc.message}), 400

    elk_host, auth = _resolve_elk_url_and_auth()
    username = auth[0] if auth else ""
    password = auth[1] if auth else ""

    try:
        results = get_documents_by_ip(elk_host, username, password, ip_address)
        return jsonify({"data": results}), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/service-status", methods=["GET"])
def fetch_service_status():
    """Fetch the statuses of SIEM (ELK) and SDN Controller (ONOS)."""
    try:
        onos_controller_ip = get_setting_value("SDN Controller IP") or "127.0.0.1"
        elk_ip = get_setting_value("ELK IP Address") or "127.0.0.1"
        service_status = get_service_status(elk_ip, onos_controller_ip)
        return jsonify({"data": service_status}), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/logstash/pipeline-status", methods=["GET"])
def fetch_logstash_pipeline_status():
    """Fetch verified Logstash pipeline metrics from internal Monitoring API."""
    try:
        pipeline_stats = get_logstash_pipeline_stats()
        return jsonify({"data": pipeline_stats}), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/ignore", methods=["POST"])
def ignore_event():
    """Delete an event from the events table based on the source IP."""
    authorized, auth_err = check_api_key(request.headers)
    if not authorized:
        return jsonify({"error": auth_err}), 401

    data = request.get_json(silent=True) or {}
    source_ip = data.get("srcIp")
    if not source_ip:
        return jsonify({"error": "Source IP is required"}), 400
    try:
        validate_ip_input(source_ip, "srcIp")
        delete_event_entry(source_ip)
        return jsonify({"message": f"Event for Source IP {source_ip} ignored successfully"}), 200
    except ValidationError as exc:
        return jsonify({"error": exc.message}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/get-actions", methods=["GET"])
def fetch_actions():
    """Fetch all actions from the database."""
    try:
        actions = get_actions()
        return jsonify({"data": actions}), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/get-anomalies", methods=["GET"])
def fetch_anomalies():
    """Fetch recent anomalies from the events table."""
    try:
        anomalies = get_anomalies()
        return jsonify({"data": anomalies}), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/save-flows", methods=["POST"])
def save_flow_data():
    """Save flow data to the database by fetching from the ONOS controller."""
    try:
        log_flows_to_database()
        return jsonify({"message": "Flows fetched and saved successfully"}), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/live-flows", methods=["GET"])
def get_live_flows():
    """Read current ONOS flows without modifying SQLite."""
    base_url = os.environ.get("SDNFLOW_ONOS_URL")
    if not base_url:
        onos_ip = get_setting_value("SDN Controller IP")
        if not onos_ip:
            return jsonify({"error": "ONOS IP not configured"}), 503
        base_url = f"http://{onos_ip}:8181/onos/v1"
    try:
        response = requests.get(
            f"{base_url.rstrip('/')}/flows",
            auth=_resolve_onos_auth(),
            timeout=5,
        )
        response.raise_for_status()

        raw_flows = response.json().get("flows", [])
        data = []
        for flow in raw_flows:
            criteria = {
                item.get("type"): item
                for item in flow.get("selector", {}).get("criteria", [])
            }
            outputs = [
                item.get("port")
                for item in flow.get("treatment", {}).get("instructions", [])
                if item.get("type") == "OUTPUT"
            ]
            data.append(
                {
                    "id": flow.get("id"),
                    "device_id": flow.get("deviceId"),
                    "app_id": flow.get("appId"),
                    "state": flow.get("state"),
                    "priority": flow.get("priority"),
                    "source_ip": criteria.get("IPV4_SRC", {}).get("ip"),
                    "destination_ip": criteria.get("IPV4_DST", {}).get("ip"),
                    "source_mac": criteria.get("ETH_SRC", {}).get("mac"),
                    "destination_mac": criteria.get("ETH_DST", {}).get("mac"),
                    "packets": flow.get("packets", 0),
                    "bytes": flow.get("bytes", 0),
                    "life_seconds": flow.get("life", 0),
                    "output_ports": outputs,
                }
            )
        return jsonify({"source": "ONOS", "count": len(data), "data": data}), 200
    except (requests.RequestException, ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 502


@app.route("/api/live-port-stats", methods=["GET"])
def get_live_port_stats():
    """Read current ONOS switch port counters without modifying SQLite."""
    base = os.environ.get("SDNFLOW_ONOS_URL")
    if not base:
        onos_ip = get_setting_value("SDN Controller IP")
        if not onos_ip:
            return jsonify({"error": "ONOS IP not configured"}), 503
        base = f"http://{onos_ip}:8181/onos/v1"
    base = base.rstrip("/")
    auth = _resolve_onos_auth()

    try:
        response = requests.get(f"{base}/devices", auth=auth, timeout=5)
        response.raise_for_status()

        switches = [
            d
            for d in response.json().get("devices", [])
            if d.get("type") == "SWITCH" and d.get("available") is True
        ]
        devices = []
        for switch in switches:
            device_id = switch.get("id")
            if not device_id:
                continue
            stats_response = requests.get(
                f"{base}/statistics/ports/{device_id}",
                auth=auth,
                timeout=5,
            )
            stats_response.raise_for_status()

            ports = []
            for group in stats_response.json().get("statistics", []):
                for entry in group.get("ports", []):
                    port = str(entry.get("port", entry.get("portNumber", "")))
                    if not port.isdecimal():
                        continue
                    ports.append(
                        {
                            "port": port,
                            "rx_bytes": int(entry.get("bytesReceived") or 0),
                            "tx_bytes": int(entry.get("bytesSent") or 0),
                            "rx_packets": int(entry.get("packetsReceived") or 0),
                            "tx_packets": int(entry.get("packetsSent") or 0),
                        }
                    )
            devices.append({"device_id": device_id, "ports": ports})

        return jsonify({"source": "ONOS", "sample_time": time.time(), "devices": devices}), 200
    except (requests.RequestException, ValueError, TypeError, KeyError) as exc:
        return jsonify({"error": str(exc)}), 502


@app.route("/api/get-flows", methods=["GET"])
def fetch_flow_data():
    """Fetch all flow data from the database."""
    try:
        flows = get_flows()
        return jsonify({"data": flows}), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/save-settings", methods=["POST"])
def save_system_settings():
    """Save system settings with input validation."""
    authorized, auth_err = check_api_key(request.headers)
    if not authorized:
        return jsonify({"error": auth_err}), 401

    settings_payload = request.get_json(silent=True)
    if not isinstance(settings_payload, dict) or not settings_payload:
        return jsonify({"error": "Settings payload must be a non-empty JSON object"}), 400

    for ip_key in ("SDN Controller IP", "ELK IP Address", "Honeypot IP Address"):
        if ip_key in settings_payload and settings_payload[ip_key]:
            try:
                validate_ip_input(str(settings_payload[ip_key]), ip_key)
            except ValidationError as exc:
                return jsonify({"error": exc.message}), 400

    if "Mode" in settings_payload:
        mode_val = str(settings_payload["Mode"]).strip().lower()
        if mode_val not in ("strict", "balanced", "loose", "lenient"):
            return jsonify({"error": "Invalid Mode. Expected strict, balanced, or loose."}), 400

    try:
        save_settings(settings_payload)
        return jsonify({"message": "Settings saved successfully"}), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/get-settings", methods=["GET"])
def fetch_system_settings():
    """Fetch all system settings."""
    try:
        settings = get_settings()
        return jsonify({"data": settings}), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/block", methods=["POST"])
def block():
    """Block traffic using an ACL with Safety Gate enforcement."""
    authorized, auth_err = check_api_key(request.headers)
    if not authorized:
        return jsonify({"error": auth_err}), 401

    data = request.get_json(silent=True) or {}
    src_ip = data.get("srcIp")
    dst_ip = data.get("dstIp")
    if not src_ip and not dst_ip:
        return jsonify({"error": "At least one of srcIp or dstIp is required"}), 400

    prefix_length = str(data.get("prefixLength") or "32")
    try:
        if src_ip:
            if "/" in str(src_ip):
                base_src, prefix_length = str(src_ip).split("/", 1)
            else:
                base_src = str(src_ip)
            validate_ip_input(base_src, "srcIp")
            if not (0 <= int(prefix_length) <= 32):
                raise ValidationError(f"Invalid prefix length in srcIp: {prefix_length}")
            src_ip = f"{base_src}/{prefix_length}"
        if dst_ip:
            if "/" in str(dst_ip):
                base_dst, prefix_length = str(dst_ip).split("/", 1)
            else:
                base_dst = str(dst_ip)
            validate_ip_input(base_dst, "dstIp")
            if not (0 <= int(prefix_length) <= 32):
                raise ValidationError(f"Invalid prefix length in dstIp: {prefix_length}")
            dst_ip = f"{base_dst}/{prefix_length}"
    except (ValidationError, ValueError) as exc:
        return jsonify({"error": str(exc.message if isinstance(exc, ValidationError) else str(exc))}), 400

    result = block_ip(
        src_ip=src_ip,
        dst_ip=dst_ip,
        src_mac=data.get("srcMac"),
        dst_mac=data.get("dstMac"),
        vlan_id=data.get("vlanId"),
        eth_type=data.get("ethType"),
        ip_proto=data.get("ipProto"),
        src_port=data.get("srcPort"),
        dst_port=data.get("dstPort"),
        dry_run=data.get("dry_run"),
        test_only=bool(data.get("test_only", False)),
        operator_authenticated=authorized,
    )
    if isinstance(result, dict):
        status = result.get("status")
        if status == "REJECTED_BY_SAFETY_GATE":
            return jsonify({"error": f"Rejected by Safety Gate for {src_ip or dst_ip}", **result}), 403
        if status == "VALIDATION_ERROR":
            return jsonify({"error": result.get("error", "Validation error"), **result}), 400
        if status == "EXECUTION_FAILED":
            return jsonify({
                "error": f"Failed to enforce block rule in ONOS controller for {src_ip or dst_ip}",
                "message": result.get("error") or "ONOS controller returned execution failure",
                **result,
            }), 502

    is_dry = isinstance(result, dict) and result.get("dry_run")
    msg = (
        f"[DRY RUN] Simulated block traffic for {src_ip or dst_ip} (no ONOS change)"
        if is_dry
        else f"Blocked traffic for {src_ip or dst_ip} successfully"
    )
    return jsonify({"message": msg, **(result if isinstance(result, dict) else {})}), 200


@app.route("/api/topology", methods=["GET"])
def get_topology():
    """Fetch the network topology from ONOS controller."""
    try:
        topology_data = get_topology_data()
        return jsonify(topology_data), 200
    except Exception as exc:
        return jsonify({
            "error": str(exc),
            "devices": [],
            "hosts": [],
            "links": [],
            "controller_status": "UNAVAILABLE",
        }), 502


@app.route("/api/allow", methods=["POST"])
def allow():
    """Allow traffic using an ACL with Safety Gate enforcement."""
    authorized, auth_err = check_api_key(request.headers)
    if not authorized:
        return jsonify({"error": auth_err}), 401

    data = request.get_json(silent=True) or {}
    src_ip = data.get("srcIp")
    dst_ip = data.get("dstIp")
    if not src_ip and not dst_ip:
        return jsonify({"error": "srcIp or dstIp is required"}), 400

    prefix_length = str(data.get("prefixLength") or "32")
    try:
        if src_ip:
            if "/" in str(src_ip):
                base_src, prefix_length = str(src_ip).split("/", 1)
            else:
                base_src = str(src_ip)
            validate_ip_input(base_src, "srcIp")
            if not (0 <= int(prefix_length) <= 32):
                raise ValidationError(f"Invalid prefix length in srcIp: {prefix_length}")
            src_ip = f"{base_src}/{prefix_length}"
        if dst_ip:
            if "/" in str(dst_ip):
                base_dst, prefix_length = str(dst_ip).split("/", 1)
            else:
                base_dst = str(dst_ip)
            validate_ip_input(base_dst, "dstIp")
            if not (0 <= int(prefix_length) <= 32):
                raise ValidationError(f"Invalid prefix length in dstIp: {prefix_length}")
            dst_ip = f"{base_dst}/{prefix_length}"
    except (ValidationError, ValueError) as exc:
        return jsonify({"error": str(exc.message if isinstance(exc, ValidationError) else str(exc))}), 400

    result = allow_ip(
        src_ip=src_ip,
        dst_ip=dst_ip,
        src_mac=data.get("srcMac"),
        dst_mac=data.get("dstMac"),
        vlan_id=data.get("vlanId"),
        eth_type=data.get("ethType"),
        src_port=data.get("srcPort"),
        dst_port=data.get("dstPort"),
        dry_run=data.get("dry_run"),
    )
    is_dry = isinstance(result, dict) and result.get("dry_run")
    msg = (
        f"[DRY RUN] Simulated allow traffic for {src_ip} to {dst_ip}"
        if is_dry
        else f"Allowed traffic for {src_ip} to {dst_ip} successfully"
    )
    return jsonify({"message": msg, **(result if isinstance(result, dict) else {})}), 200


@app.route("/api/rate-limit", methods=["POST"])
def apply_rate_limit():
    """Apply rate limiting to traffic for a specific host by its IP address."""
    authorized, auth_err = check_api_key(request.headers)
    if not authorized:
        return jsonify({"error": auth_err}), 401

    data = request.get_json(silent=True) or {}
    host_ip = data.get("hostIp")
    rate_limit_bps = data.get("rateLimitBps")
    admin_or_automated = data.get("adminOrAutomated", "Admin")

    if not all([host_ip, rate_limit_bps]):
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        validate_ip_input(host_ip, "hostIp")
        parsed_rate = validate_rate_input(rate_limit_bps)
    except ValidationError as exc:
        return jsonify({"error": exc.message}), 400

    result = rate_limit_for_host(
        host_ip=host_ip,
        rate_limit_bps=parsed_rate,
        admin_or_automated=admin_or_automated,
        dry_run=data.get("dry_run"),
        test_only=bool(data.get("test_only", False)),
        operator_authenticated=authorized,
    )
    if isinstance(result, dict) and result.get("status") == "REJECTED_BY_SAFETY_GATE":
        return jsonify({"error": f"Rejected by Safety Gate for {host_ip}", **result}), 403

    is_dry = isinstance(result, dict) and result.get("dry_run")
    msg = (
        f"[DRY RUN] Simulated rate limit for host {host_ip} at {parsed_rate} bps"
        if is_dry
        else f"Rate limit applied for host {host_ip} at {parsed_rate} bps"
    )
    return jsonify({"message": msg, **(result if isinstance(result, dict) else {})}), 200


@app.route("/api/redirect", methods=["POST"])
def redirect():
    """Redirect traffic from one IP address to another."""
    authorized, auth_err = check_api_key(request.headers)
    if not authorized:
        return jsonify({"error": auth_err}), 401

    data = request.get_json(silent=True) or {}
    src_ip_address = data.get("srcIp")
    redirect_ip_address = data.get("redirectIp")
    if not src_ip_address or not redirect_ip_address:
        return jsonify({"error": "Source IP and Redirect IP must be provided"}), 400

    try:
        validate_ip_input(src_ip_address, "srcIp")
        validate_ip_input(redirect_ip_address, "redirectIp")
    except ValidationError as exc:
        return jsonify({"error": exc.message}), 400

    result = redirect_traffic_full(
        source_ip=src_ip_address,
        honeypot_ip=redirect_ip_address,
        admin_or_automated="Admin",
        dry_run=data.get("dry_run"),
        test_only=bool(data.get("test_only", False)),
    )
    if isinstance(result, dict) and result.get("status") == "REJECTED_BY_SAFETY_GATE":
        return jsonify({"error": f"Rejected by Safety Gate for {src_ip_address}", **result}), 403

    is_dry = isinstance(result, dict) and result.get("dry_run")
    msg = (
        f"[DRY RUN] Simulated redirect from {src_ip_address} to {redirect_ip_address}"
        if is_dry
        else f"Redirected traffic from {src_ip_address} to {redirect_ip_address} successfully"
    )
    return jsonify({"message": msg, **(result if isinstance(result, dict) else {})}), 200


@app.route("/api/redirectHoney", methods=["POST"])
def redirect_to_honeypot():
    """Redirect traffic from a given source IP to the configured honeypot."""
    authorized, auth_err = check_api_key(request.headers)
    if not authorized:
        return jsonify({"error": auth_err}), 401

    data = request.get_json(silent=True) or {}
    src_ip = data.get("srcIp")
    if not src_ip:
        return jsonify({"error": "Source IP must be provided"}), 400

    try:
        validate_ip_input(src_ip, "srcIp")
    except ValidationError as exc:
        return jsonify({"error": exc.message}), 400

    honeypot_ip = get_setting_value("Honeypot IP Address")
    if not honeypot_ip:
        return jsonify({"error": "Honeypot IP not configured in settings"}), 500

    result = redirect_traffic_full(
        source_ip=src_ip,
        honeypot_ip=honeypot_ip,
        admin_or_automated="Admin",
        dry_run=data.get("dry_run"),
    )
    if isinstance(result, dict) and result.get("status") == "REJECTED_BY_SAFETY_GATE":
        return jsonify({"error": f"Rejected by Safety Gate for {src_ip}", **result}), 403

    is_dry = isinstance(result, dict) and result.get("dry_run")
    msg = (
        f"[DRY RUN] Simulated redirect from {src_ip} to honeypot ({honeypot_ip})"
        if is_dry
        else f"Redirected traffic from {src_ip} to honeypot ({honeypot_ip}) successfully"
    )
    return jsonify({"message": msg, **(result if isinstance(result, dict) else {})}), 200


@app.route("/api/unblock", methods=["POST"])
def unblock():
    """Unblock traffic by removing the ACL rule for the specified IP address."""
    authorized, auth_err = check_api_key(request.headers)
    if not authorized:
        return jsonify({"error": auth_err}), 401

    data = request.get_json(silent=True) or {}
    src_ip = data.get("srcIp")
    dst_ip = data.get("dstIp")
    if not src_ip and not dst_ip:
        return jsonify({"error": "srcIp or dstIp is required"}), 400

    prefix_length = str(data.get("prefixLength") or "32")
    try:
        if src_ip:
            validate_ip_input(str(src_ip).split("/")[0], "srcIp")
        if dst_ip:
            validate_ip_input(str(dst_ip).split("/")[0], "dstIp")
    except ValidationError as exc:
        return jsonify({"error": exc.message}), 400

    result = unblock_ip(
        src_ip=src_ip,
        dst_ip=dst_ip,
        src_port=data.get("srcPort"),
        dst_port=data.get("dstPort"),
        prefix_length=prefix_length,
        dry_run=data.get("dry_run"),
        return_structured=True,
    )
    if isinstance(result, dict):
        status = result.get("status")
        if status == "REJECTED_BY_SAFETY_GATE":
            return jsonify({"error": "Rejected by Safety Gate", **result}), 403
        if status == "VALIDATION_ERROR":
            return jsonify({"error": result.get("error", "Validation error"), **result}), 400
        if status in ("CONTROLLER_UNAVAILABLE", "ROLLBACK_FAILED"):
            return jsonify({"error": result.get("message", "Controller error"), **result}), 502
        return jsonify({"message": result.get("message", "Success"), **result}), 200
    return jsonify({"message": str(result)}), 200


@app.route("/api/defense/rollback", methods=["POST"])
def api_defense_rollback():
    """Rollback a previous IP block/redirect/rate-limit ACL rule."""
    authorized, auth_err = check_api_key(request.headers)
    if not authorized:
        return jsonify({"error": auth_err}), 401

    data = request.get_json(silent=True) or {}
    target_ip = data.get("srcIp") or data.get("ip")
    if not target_ip:
        return jsonify({"error": "Target IP ('srcIp' or 'ip') is required for rollback"}), 400
    try:
        clean_ip = validate_ip_input(str(target_ip).split("/")[0], "ip")
    except ValidationError as exc:
        return jsonify({"error": exc.message}), 400

    structured_res = unblock_ip(src_ip=clean_ip, dry_run=data.get("dry_run"), return_structured=True)
    if isinstance(structured_res, dict):
        status = structured_res.get("status")
        if status == "REJECTED_BY_SAFETY_GATE":
            return jsonify({"error": "Rollback rejected by Safety Gate", "result": structured_res}), 403
        if status == "VALIDATION_ERROR":
            return jsonify({"error": structured_res.get("error", "Validation error"), "result": structured_res}), 400
        if status in ("CONTROLLER_UNAVAILABLE", "ROLLBACK_FAILED"):
            return jsonify({"error": "Rollback failed: ONOS controller error", "result": structured_res}), 502
        return jsonify(structured_res), 200

    return jsonify({"status": "ROLLBACK_FAILED", "target_ip": clean_ip, "executed": False, "message": str(structured_res)}), 502


# === STEP 42: ELK PORT TRAFFIC HISTORY (READ-ONLY) ===
@app.route("/api/elk/port-traffic-history", methods=["GET"])
def elk_port_traffic_history():
    try:
        minutes = int(request.args.get("minutes", "120"))
        limit = int(request.args.get("limit", "200"))
    except (TypeError, ValueError):
        return jsonify({"error": "minutes and limit must be integers"}), 400

    if not (1 <= minutes <= 10080 and 1 <= limit <= 500):
        return jsonify({"error": "minutes: 1-10080; limit: 1-500"}), 400

    search = {
        "size": limit,
        "sort": [{"@timestamp": {"order": "desc"}}],
        "_source": [
            "@timestamp",
            "switch_id",
            "port_number",
            "rx_mbps",
            "tx_mbps",
            "rx_pps",
            "tx_pps",
            "sample_seconds",
        ],
        "query": {
            "bool": {
                "filter": [
                    {"match_phrase": {"event_type": "sdn_port_traffic"}},
                    {"range": {"@timestamp": {"gte": f"now-{minutes}m"}}},
                ]
            }
        },
    }

    elk_base, elk_auth = _resolve_elk_url_and_auth()
    try:
        response = requests.post(
            f"{elk_base}/sdnflowguard-events-*/_search",
            json=search,
            auth=elk_auth,
            timeout=10,
        )
        response.raise_for_status()
        hits = response.json().get("hits", {}).get("hits", [])
    except (requests.RequestException, ValueError):
        return jsonify({"error": "Elasticsearch is unavailable"}), 503

    rows = []
    for hit in hits:
        item = hit.get("_source") or {}
        rows.append(
            {
                "timestamp": item.get("@timestamp"),
                "switch_id": item.get("switch_id"),
                "port_number": item.get("port_number"),
                "rx_mbps": item.get("rx_mbps", 0),
                "tx_mbps": item.get("tx_mbps", 0),
                "rx_pps": item.get("rx_pps", 0),
                "tx_pps": item.get("tx_pps", 0),
                "sample_seconds": item.get("sample_seconds"),
            }
        )
    rows.reverse()

    return (
        jsonify(
            {
                "source": "Elasticsearch",
                "minutes": minutes,
                "count": len(rows),
                "data": rows,
            }
        ),
        200,
    )


# === STEP 48: ELK SECURITY ALERTS (READ ONLY) ===
@app.route("/api/elk/security-alerts", methods=["GET"])
def elk_security_alerts():
    try:
        minutes = int(request.args.get("minutes", "1440"))
        limit = int(request.args.get("limit", "100"))
    except (TypeError, ValueError):
        return jsonify({"error": "minutes and limit must be integers"}), 400

    if not (1 <= minutes <= 10080 and 1 <= limit <= 200):
        return jsonify({"error": "minutes: 1-10080; limit: 1-200"}), 400

    query = {
        "size": limit,
        "track_total_hits": True,
        "sort": [{"@timestamp": {"order": "desc"}}],
        "_source": [
            "@timestamp",
            "event_id",
            "alert_key",
            "event_type",
            "detected_at_utc",
            "switch_id",
            "port_number",
            "rx_pps",
            "tx_pps",
            "peak_pps",
            "threshold_pps",
            "consecutive_samples",
            "severity",
            "status",
            "test_only",
            "detection_mode",
            "reason",
            "message",
        ],
        "query": {
            "bool": {
                "filter": [
                    {"term": {"event_type.keyword": "sdn_anomaly_alert"}},
                    {"range": {"@timestamp": {"gte": f"now-{minutes}m"}}},
                ]
            }
        },
    }

    elk_base, elk_auth = _resolve_elk_url_and_auth()
    try:
        response = requests.post(
            f"{elk_base}/sdnflowguard-events-*/_search",
            json=query,
            auth=elk_auth,
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
    except (requests.RequestException, ValueError):
        return jsonify({"error": "Cannot read Elasticsearch security alerts"}), 503

    hits = result.get("hits", {})
    alerts = []
    for hit in hits.get("hits", []):
        item = hit.get("_source") or {}
        alerts.append(
            {
                "event_id": item.get("event_id"),
                "alert_key": item.get("alert_key"),
                "timestamp": item.get("@timestamp"),
                "detected_at_utc": item.get("detected_at_utc"),
                "switch_id": item.get("switch_id"),
                "port_number": item.get("port_number"),
                "rx_pps": item.get("rx_pps"),
                "tx_pps": item.get("tx_pps"),
                "peak_pps": item.get("peak_pps"),
                "threshold_pps": item.get("threshold_pps"),
                "consecutive_samples": item.get("consecutive_samples"),
                "severity": item.get("severity"),
                "status": item.get("status"),
                "test_only": item.get("test_only"),
                "detection_mode": item.get("detection_mode"),
                "reason": item.get("reason"),
                "message": item.get("message"),
            }
        )

    total = hits.get("total", {})
    total_count = total.get("value", len(alerts)) if isinstance(total, dict) else total

    return (
        jsonify(
            {
                "source": "Elasticsearch",
                "minutes": minutes,
                "total": total_count,
                "count": len(alerts),
                "alerts": alerts,
            }
        ),
        200,
    )


if __name__ == "__main__":
    init_db()
    settings = AppSettings.from_env()
    app.run(
        debug=settings.flask_debug,
        host=settings.flask_host,
        port=settings.flask_port,
    )
