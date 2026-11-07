try:
    from .controller_actions import (
        block_ip,
        rate_limit_for_host,
        redirect_to_intermediate_ovs,
        redirect_traffic_full,
    )
    from .database import get_setting_value, save_settings
except ImportError:
    from controller_actions import (
        block_ip,
        rate_limit_for_host,
        redirect_to_intermediate_ovs,
        redirect_traffic_full,
    )
    from database import get_setting_value, save_settings

CONFIDENCE_RATES = {
    "Netflow": 0.2,
    "AD-logs": 0.3,
    "Honeypot": 0.8,
    "dns-logs": 0.25,
    "EDR": 0.7,
    "IDS": 0.6,
}

DETECTION_MODES = {
    "strict": 0.8,
    "balanced": 0.5,
    "loose": 0.2,
    "lenient": 0.2,
}


def get_or_initialize_marks(sourceip):
    """Retrieve marks from the database or initialize them if not present."""
    key = f"{sourceip} marks"
    marks = get_setting_value(key)
    if marks is not None:
        try:
            return float(marks)
        except (TypeError, ValueError):
            return 0.0
    save_settings({key: "0.0"})
    return 0.0


def save_marks(sourceip, marks):
    """Save marks to the database."""
    save_settings({f"{sourceip} marks": str(round(float(marks), 4))})


def process_event(event):
    """Process an incoming event, calculate marks, update them, and take appropriate actions."""
    if not isinstance(event, dict):
        return []

    if event.get("test_only") is True:
        return ["Observe (test_only)"]

    source = event.get("Source")
    try:
        score = float(event.get("Score", 0))
    except (TypeError, ValueError):
        return []
    source_ip = event.get("SourceIP")
    if not source_ip:
        return []

    detection_mode = (get_setting_value("Mode") or "balanced").strip().lower()
    honeypot_ip = get_setting_value("Honeypot IP Address") or "10.0.0.6"

    if source not in CONFIDENCE_RATES or detection_mode not in DETECTION_MODES:
        return []

    confidence_rate = CONFIDENCE_RATES[source]
    detection_multiplier = DETECTION_MODES[detection_mode]

    marks_increase = score * confidence_rate * detection_multiplier
    marks = get_or_initialize_marks(source_ip)
    updated_marks = marks + marks_increase
    save_marks(source_ip, updated_marks)

    actions = []
    if updated_marks >= 100:
        block_ip(src_ip=f"{source_ip}/32", admin_or_automated="Automated")
        actions.append("Block")
    elif updated_marks >= 60:
        redirect_traffic_full(source_ip, honeypot_ip, admin_or_automated="Automated")
        actions.append("Redirect")
    elif updated_marks >= 40:
        rate_limit_for_host(
            source_ip,
            rate_limit_bps=50,
            admin_or_automated="Automated",
        )
        actions.append("Rate Limit")
    elif updated_marks >= 20:
        redirect_to_intermediate_ovs(
            source_ip,
            ovs_id="of:0000000000000003",
            admin_or_automated="Automated",
        )
        actions.append("Intermediate Redirect")
    else:
        actions.append("No Action")

    return actions
