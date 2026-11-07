"""Clean Architecture Flask Blueprint for SDNFlowGuard v2 endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from defense.onos_host_evidence_correlator import DEFAULT_EVIDENCE_PATH
from sdnflowguard.application.use_cases import (
    evaluate_control_action_safety_use_case,
    run_defense_policy_evaluation_use_case,
    run_siem_capability_evaluation_use_case,
    run_step64_evidence_correlation_use_case,
)
from sdnflowguard.domain.services.siem_log_normalizer import (
    normalize_firewall_log,
    normalize_windows_event_log,
)
from sdnflowguard.infrastructure.configuration.settings import AppSettings
from sdnflowguard.interfaces.http.security import check_api_key
from sdnflowguard.observability.structured_logger import generate_request_id

clean_api_bp = Blueprint("sdnflowguard_clean_api", __name__)


@clean_api_bp.route("/api/health", methods=["GET"])
def api_health():
    settings = AppSettings.from_env()
    return (
        jsonify(
            {
                "request_id": generate_request_id(),
                "status": "OK",
                "service": "SDNFlowGuard Backend",
                "version": "2.0.0",
                "defense_mode": settings.defense_mode,
                "step63_evidence_present": DEFAULT_EVIDENCE_PATH.is_file(),
                "database_exists": settings.db_path.is_file(),
                "config": settings.to_safe_summary(),
            }
        ),
        200,
    )


@clean_api_bp.route("/api/defense/evidence-correlation", methods=["GET"])
def api_evidence_correlation():
    try:
        report = run_step64_evidence_correlation_use_case()
        return jsonify({"status": "SUCCESS", "data": report}), 200
    except Exception as exc:
        return (
            jsonify(
                {
                    "status": "ERROR",
                    "error": str(exc),
                    "request_id": generate_request_id(),
                }
            ),
            500,
        )


@clean_api_bp.route("/api/defense/evaluate", methods=["GET"])
def api_defense_evaluate():
    try:
        result = run_defense_policy_evaluation_use_case()
        return jsonify({"status": "SUCCESS", "data": result}), 200
    except Exception as exc:
        return (
            jsonify(
                {
                    "status": "ERROR",
                    "error": str(exc),
                    "request_id": generate_request_id(),
                }
            ),
            500,
        )


@clean_api_bp.route("/api/defense/safety-check", methods=["POST"])
def api_defense_safety_check():
    authorized, auth_err = check_api_key(request.headers)
    if not authorized:
        return jsonify({"status": "UNAUTHORIZED", "error": auth_err}), 401

    payload = request.get_json(silent=True) or {}
    action_type = str(payload.get("action_type") or "block_ip")
    verdict = evaluate_control_action_safety_use_case(
        action_type=action_type,
        target_ip=payload.get("ip"),
        target_device_id=payload.get("device_id") or "of:0000000000000001",
        target_port=str(payload.get("port")) if payload.get("port") is not None else None,
        explicit_dry_run=payload.get("dry_run"),
        operator_approved=bool(payload.get("operator_approved", False)),
        manual_operator_override=bool(payload.get("manual_operator_override", True)),
        test_only=bool(payload.get("test_only", False)),
        source_ip_attributed=bool(payload.get("source_ip_attributed", False)),
        historical_alert_correlation_verified=bool(
            payload.get("historical_alert_correlation_verified", False)
        ),
    )
    return (
        jsonify(
            {
                "request_id": generate_request_id(),
                "status": "SUCCESS",
                "verdict": verdict,
            }
        ),
        200,
    )


@clean_api_bp.route("/api/siem/evaluate-fixtures", methods=["GET"])
def api_siem_evaluate_fixtures():
    result = run_siem_capability_evaluation_use_case()
    return jsonify({"status": "SUCCESS", "data": result}), 200


@clean_api_bp.route("/api/siem/normalize", methods=["POST"])
def api_siem_normalize():
    payload = request.get_json(silent=True) or {}
    source_type = str(payload.get("source_type") or "").upper()
    raw_event = payload.get("event")
    try:
        if source_type == "FIREWALL":
            normalized = normalize_firewall_log(raw_event)
        elif source_type == "WINDOWS_SERVER":
            normalized = normalize_windows_event_log(raw_event)
        else:
            return (
                jsonify(
                    {
                        "status": "ERROR",
                        "error": "Unsupported source_type. Use FIREWALL or WINDOWS_SERVER.",
                    }
                ),
                400,
            )
        return (
            jsonify(
                {
                    "request_id": generate_request_id(),
                    "status": "SUCCESS",
                    "data": normalized,
                }
            ),
            200,
        )
    except Exception as exc:
        return (
            jsonify(
                {
                    "request_id": generate_request_id(),
                    "status": "ERROR",
                    "error": str(exc),
                }
            ),
            400,
        )

