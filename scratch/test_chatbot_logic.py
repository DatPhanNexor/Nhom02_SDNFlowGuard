import re
import datetime

def test_intent_classification():
    sample_queries = [
        ("ONOS Controller đang hoạt động không?", "controller_status"),
        ("Kiểm tra trạng thái onos", "controller_status"),
        ("Mạng SDN hiện có bao nhiêu switch?", "topology"),
        ("Có những host nào đang kết nối?", "topology"),
        ("Flow table hiện tại có bao nhiêu rule?", "flows"),
        ("Bảng luồng hiện tại", "flows"),
        ("Có cảnh báo bảo mật nào gần đây?", "security_alerts"),
        ("Sự kiện an ninh mới nhất", "security_alerts"),
        ("Defense Mode hiện tại là gì?", "defense_policy"),
        ("Tại sao Safety Gate không chặn một IP?", "defense_policy"),
        ("DRY_RUN khác LIVE_ENFORCEMENT như thế nào?", "defense_policy"),
        ("Elasticsearch và Logstash đang hoạt động không?", "elk_status"),
        ("Giải thích luồng hoạt động của SDNFlowGuard", "architecture"),
        ("Kiến trúc hệ thống", "architecture"),
        ("Nếu ONOS mất kết nối thì sao?", "troubleshooting"),
        ("Hướng dẫn sửa lỗi switch", "troubleshooting"),
        ("OpenFlow là gì?", "openflow"),
        ("Hệ thống đã chống DDoS thành công chưa?", "ddos_defense"),
        ("Chặn IP 10.0.0.5 ngay lập tức", "blocked_action"),
    ]
    print(f"Total test queries: {len(sample_queries)}")

test_intent_classification()
