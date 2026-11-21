# Security Design & Hardening Report — SDNFlowGuard

## 1. Security Vulnerabilities & Operational Risks Remediated

| ID | Vulnerability / Risk Before Refactor | Location | Remediation Applied | Verification Test |
|---|---|---|---|---|
| **SEC-01** | Hardcoded Elasticsearch basic-auth password (`ELK_PASSWORD = "8i8R..."`) in source code | `backend/run.py` | Removed hardcoded password; loaded dynamically via `AppSettings.from_env()` (`SDNFLOW_ELK_PASSWORD`) with `.env.example` containing empty secret placeholders | `safety/test_no_secret_leakage.py` |
| **SEC-02** | Import-time side effects querying SQLite and reading credentials during module import | `backend/app/controller_actions.py`, `topology.py`, `report.py`, `service_stat.py`, `chatbot.py`, `database.py` | Converted all module-level DB queries and credential lookups into lazy runtime resolvers (`_resolve_onos_api()`, `_resolve_db_path()`) | `unit/*`, `integration/*` |
| **SEC-03** | Port-level traffic spike could be misinterpreted as source IP attribution (`Attached Host != Verified Attacker`) | `backend/defense/*`, `backend/app/decision.py` | Implemented Step 64 ONOS Host Evidence Correlator (`onos_host_evidence_correlator.py`) and Active Defense Safety Gate (`safety_gate.py`); port alerts alone emit `OBSERVE` and never trigger IP blocks | `safety/test_port_anomaly_never_blocks_ip.py` |
| **SEC-04** | Synthetic / lab replay alerts (`test_only: true`) could trigger automated enforcement | `backend/app/decision.py`, `backend/app/controller_actions.py` | Enforced strict `not_test_only_alert` check in `evaluate_safety_gate()` and `decision.process_event()` | `safety/test_test_alert_never_blocks.py` |
| **SEC-05** | Lack of protected IP guardrails (risk of blocking `127.0.0.1`, Controller IP, ELK IP, Gateway, DNS, multicast, or broadcast) | `backend/app/controller_actions.py`, `safety_gate.py` | Added `is_protected_ip()` blocking loopback, link-local, multicast, broadcast, unspecified, `10.0.0.254`, `8.8.8.8`, `1.1.1.1`, Controller IP, ELK IP, and allowlisted IPs/CIDRs | `unit/test_safety_gate.py`, `unit/test_remediation_findings.py` |
| **SEC-06** | Unsafe default active enforcement when starting the backend | `backend/run.py`, `backend/app/controller_actions.py` | Defaulted `SDNFLOW_DEFENSE_MODE=DRY_RUN` across all modules and UI forms | `safety/test_dry_run_default.py` |
| **SEC-07** | Unauthenticated mutating HTTP endpoints & unconfigured-key operator promotion | `backend/run.py`, `sdnflowguard/interfaces/http/security.py`, `controller_actions.py` | Enforced `check_api_key()` (`X-SDNFlow-API-Key` or Bearer token) on all mutating endpoints including `/api/save-flows`; separated `is_operator_authenticated()` so an unset `SDNFLOW_API_KEY` never authorizes live `MANUAL_APPROVAL` mutations; propagated auth through `block_ip -> create_acl_rule` | `integration/test_flask_api_routes.py`, `safety/test_audit_remediation_hardening.py` |
| **SEC-08** | Arbitrary query bounds on Elasticsearch endpoints (`minutes`, `limit`) | `backend/run.py`, `backend/app/query_elastic.py` | Enforced strict numeric bounds (`minutes: 1..10080`; `limit: 1..500` on port history, `1..200` on security alerts) returning HTTP `400` on invalid parameters | `contracts/test_elasticsearch_query_contracts.py` |
| **SEC-09** | Build-time API key exposure (`REACT_APP_API_KEY`) & raw HTTP 500 exception leakage | `frontend/src/config/apiConfig.js`, `backend/run.py`, `routes.py` | Replaced `REACT_APP_API_KEY` build-time embedding with runtime `sessionStorage` operator key lookup (`sdnflow_operator_api_key`); sanitized unexpected HTTP 500 error responses with correlation `request_id` | `safety/test_audit_remediation_hardening.py` |
| **SEC-10** | Unverified ONOS controller responses & false HTTP 200 on failed actions | `backend/app/controller_actions.py`, `backend/run.py` | Added read-back ACL verification (`verification_status`: `RULE_INSTALLED` vs `CONTROLLER_ACCEPTED_UNVERIFIED`), `RequestException` handling on rate-limit/redirect, `NoneType` guard on `unblock_ip`, and accurate HTTP `403`/`404`/`502` responses | `safety/test_audit_remediation_hardening.py` |

---

## 2. Fail-Safe Active Defense Lifecycle

Every defense action transitions through an explicit state machine (`DefenseLifecycleState`):
1. `NORMAL`: Normal network operation.
2. `ANOMALY_OBSERVED`: High packet rate or security alert observed (`decision = OBSERVE`).
3. `EVIDENCE_CORRELATED`: Step 63 switch ingress packet capture correlated with ONOS topology in Step 64 (`CORROBORATED_HOST_OBSERVATION`).
4. `BLOCK_PROPOSED`: Action staged in `DRY_RUN` or `AUTO_STAGE_ONLY` mode without modifying ONOS.
5. `BLOCK_APPROVED`: Approved by the Active Defense Safety Gate (`allowed_to_execute = True`).
6. `RULE_APPLIED`: Sent to ONOS REST API (`/onos/v1/acl/rules`, `/onos/v1/meters`, or `/onos/v1/intents`) with explicit `controller_accepted` and `verification_status` (`RULE_INSTALLED` vs `CONTROLLER_ACCEPTED_UNVERIFIED`).
7. `RULE_VERIFIED`: Confirmed via ONOS ACL read-back (`list_acl_rules()`) and/or `ONOSClient.verify_ip_flow_rule_present()`, plus dataplane check when Mininet lab is active.
8. `ROLLBACK_OR_EXPIRED`: Reversed via `/api/unblock` or `/api/defense/rollback` with post-delete verification (`ROLLBACK_VERIFIED` vs `CONTROLLER_ACCEPTED_UNVERIFIED`) and full audit trail in SQLite (`actions` table).

