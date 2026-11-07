import ipaddress
import os
from flask import Flask, request

try:
    from .database import init_db, save_event
    from .decision import process_event
except ImportError:
    from database import init_db, save_event
    from decision import process_event

app = Flask(__name__)


def _validate_webhook_event(data):
    if not isinstance(data, dict) or not data:
        return False, "No data received"
    required = ("Source", "Event", "Score", "SourceIP", "DestinationIP")
    for field in required:
        if field not in data or data.get(field) in (None, ""):
            return False, f"Missing required field: {field}"
    try:
        ipaddress.ip_address(str(data["SourceIP"]).strip())
        ipaddress.ip_address(str(data["DestinationIP"]).strip())
    except ValueError as exc:
        return False, f"Invalid IP address: {exc}"
    try:
        float(data["Score"])
    except (TypeError, ValueError):
        return False, "Field 'Score' must be numeric"
    return True, None


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if not data:
        return {"message": "No data received"}, 400

    valid, err = _validate_webhook_event(data)
    if not valid:
        return {"message": "Invalid event payload", "error": err}, 400

    try:
        save_event(data)
        actions = process_event(data)
        return {"message": "Event processed successfully", "actions": actions}, 200
    except Exception as exc:
        return {"message": "Failed to process event", "error": str(exc)}, 500


def run_webhook():
    init_db()
    port = int(os.environ.get("WEBHOOK_PORT", 5001))
    app.run(host="127.0.0.1", port=port, debug=False)
