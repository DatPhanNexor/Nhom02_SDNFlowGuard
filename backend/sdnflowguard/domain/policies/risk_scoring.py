"""Pure domain risk & trust scoring policy for SDNFlowGuard."""

from __future__ import annotations

from typing import Any

INITIAL_SCORE = 95.0
MAX_SCORE = 100.0
MIN_SCORE = 0.0

SEVERITY_PENALTIES = {
    1: 15.0,
    2: 5.0,
    3: 0.99,
}

MODE_THRESHOLDS = {
    "strict": {
        "block": 90.0,
        "redirect": 93.0,
        "throttle": 95.0,
    },
    "balanced": {
        "block": 80.0,
        "redirect": 85.0,
        "throttle": 90.0,
    },
    "lenient": {
        "block": 70.0,
        "redirect": 75.0,
        "throttle": 80.0,
    },
}


def normalize_mode(mode: str | None) -> str:
    """Normalize policy mode string to strict, balanced, or lenient."""
    if not mode:
        return "balanced"
    cleaned = str(mode).strip().lower()
    return cleaned if cleaned in MODE_THRESHOLDS else "balanced"


def calculate_updated_score(
    current_score: float,
    severity: int,
    *,
    test_only: bool = False,
) -> float:
    """Compute updated trust score after an alert, without side effects."""
    score = max(MIN_SCORE, min(MAX_SCORE, float(current_score)))
    if test_only:
        return round(score, 3)

    if severity in SEVERITY_PENALTIES:
        score = max(MIN_SCORE, score - SEVERITY_PENALTIES[severity])
    else:
        score = min(MAX_SCORE, score + 1.0)
    return round(score, 3)


def determine_recommended_action(
    score: float,
    mode: str = "balanced",
    *,
    test_only: bool = False,
) -> dict[str, Any]:
    """Determine recommended mitigation action from trust score and mode."""
    normalized_mode = normalize_mode(mode)
    thresholds = MODE_THRESHOLDS[normalized_mode]

    if test_only:
        return {
            "recommended_action": "OBSERVE",
            "LegacyAction": "none",
            "mode": normalized_mode,
            "score": round(float(score), 3),
            "reason": "Alert is marked test_only=True; active mitigation is prohibited.",
        }

    if score <= thresholds["block"]:
        action = "block_ip"
        policy_action = "PROPOSE_BLOCK"
    elif score <= thresholds["redirect"]:
        action = "redirect_traffic"
        policy_action = "PROPOSE_REDIRECT"
    elif score <= thresholds["throttle"]:
        action = "throttle_traffic"
        policy_action = "PROPOSE_THROTTLE"
    else:
        action = "none"
        policy_action = "ALLOW"

    return {
        "recommended_action": policy_action,
        "LegacyAction": action,
        "mode": normalized_mode,
        "score": round(float(score), 3),
        "thresholds": thresholds,
        "reason": f"Score {score:.3f} evaluated against {normalized_mode} thresholds.",
    }

