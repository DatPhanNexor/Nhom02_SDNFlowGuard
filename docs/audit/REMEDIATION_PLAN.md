# SDNFlowGuard — Prioritized Remediation Plan

**Date:** 2026-11-18  
**Methodology:** `INSPECT -> HYPOTHESIS -> MINIMAL PATCH -> TEST -> VERIFY -> DOCUMENT`  
**Invariant Constraints:**
- Preserve `SDNFLOW_DEFENSE_MODE=DRY_RUN` default and Fail-Safe Safety Gate.
- Preserve `database/sdnflowguard.db` byte-for-byte (`SHA-256: 3909de520f89ea050e7858104c8aa17bddd94d06af9db5ad84652404b9463fe9`).
- Preserve `frontend/public/sdnflowguard-logo.png` byte-for-byte (`SHA-256: fb1f267cdafe39e99f97dc5c5d9eb06cde77ad6cf01c5e39a5739af0b590faba`).
- Maintain 100% backward compatibility with existing 85 tests and API response fields consumed by React frontend.
- Zero `.doc/.docx/.ppt/.pptx` or academic PDFs created in workspace.

---

## Loop 1 — P0 Security & Operator Authentication Hardening

| ID | Target Files | Minimal Patch | Verification Gate |
|---|---|---|---|
| **P0-01** | `backend/sdnflowguard/interfaces/http/security.py`, `backend/app/controller_actions.py` | Add `is_operator_authenticated(headers) -> bool` returning `True` ONLY when `SDNFLOW_API_KEY` is configured and matches header via `hmac.compare_digest`. In `_evaluate_action_gate()`, never auto-promote `operator_authenticated=True` when `SDNFLOW_API_KEY` is unset (an unauthenticated caller may still stage `DRY_RUN` proposals, but cannot execute live mutations in `MANUAL_APPROVAL` mode). | Add unit & integration tests verifying: (a) unset `SDNFLOW_API_KEY` + `MANUAL_APPROVAL` + `dry_run=False` cannot execute live mutation; (b) valid `SDNFLOW_API_KEY` + `MANUAL_APPROVAL` + `dry_run=False` passes Safety Gate. |
| **P0-02** | `backend/app/controller_actions.py`, `backend/run.py` | Add `operator_authenticated: bool | None = None` to `create_acl_rule`, `allow_ip`, `unblock_ip`, `redirect_traffic`, `redirect_traffic_full`, `redirect_to_intermediate_ovs`; forward `operator_authenticated` from `block_ip` -> `create_acl_rule`; pass `is_operator_authenticated(request.headers)` from all mutating endpoints in `run.py`. | Add unit/integration test confirming authenticated `block_ip` in `MANUAL_APPROVAL` propagates auth cleanly into `create_acl_rule` and calls ONOS mock. |
| **P0-03** | `backend/run.py`, `backend/sdnflowguard/interfaces/http/routes.py` | Require `check_api_key(request.headers)` on `POST /api/save-flows`. Sanitize unexpected HTTP 500 error responses to avoid exposing raw internal exceptions while logging safely. | Add integration test verifying `/api/save-flows` returns `401` when `SDNFLOW_API_KEY` is configured and missing. |
| **P0-04** | `frontend/src/config/apiConfig.js` | Support runtime `sessionStorage.getItem('sdnflow_operator_api_key')` before any fallback, and avoid relying on build-time secret embedding. | Frontend `npm run build` succeeds with zero warnings/errors. |

**Rollback Strategy (Loop 1):** All changes are isolated to 4 files; revert individual files via `git diff` inspection if any regression appears.

---

## Loop 2 — P1 SDN Control Plane, Execution Verification & Error Handling

| ID | Target Files | Minimal Patch | Verification Gate |
|---|---|---|---|
| **P1-01** | `docker-compose.yml` | Add `acl` to `ONOS_APPS=drivers,openflow,gui2,fwd,acl` so `/onos/v1/acl/rules` is active when ONOS boots. Validate with `docker compose config --quiet`. | `docker compose config --quiet` exits 0. |
| **P1-02** | `backend/app/controller_actions.py`, `backend/run.py` | 1. Wrap ONOS HTTP calls in `redirect_traffic`, `redirect_to_intermediate_ovs`, `rate_limit_for_host` with `try/except requests.RequestException` returning structured `EXECUTION_FAILED`.<br>2. Add structured `verification_status` (`RULE_INSTALLED` / `CONTROLLER_ACCEPTED_UNVERIFIED` / `EXECUTION_FAILED`) and `timestamp_utc` to live action responses, performing read-back verification (`list_acl_rules` for ACLs, ONOS meter/flow check for rate limits) while keeping backward-compatible `status="RULE_APPLIED"`.<br>3. Fix HTTP status codes in `/api/allow`, `/api/rate-limit`, `/api/redirect`, `/api/redirectHoney` so `REJECTED_BY_SAFETY_GATE` -> 403, `VALIDATION_ERROR` -> 400, `HOST_NOT_FOUND`/`NO_PATH_FOUND` -> 404, `EXECUTION_FAILED` -> 502 (never false HTTP 200 "applied successfully"). | Add unit/integration tests for: ONOS `RequestException` handling on rate-limit & redirect; read-back `RULE_INSTALLED` vs `CONTROLLER_ACCEPTED_UNVERIFIED`; proper 403/404/502 status codes on `/api/allow`, `/api/rate-limit`, `/api/redirect`. |
| **P1-03** | `backend/app/controller_actions.py`, `backend/sdnflowguard/domain/policies/safety_gate.py` | 1. Guard `rem_rules is None` in `unblock_ip()` so a dropped ONOS connection during post-delete read-back returns `CONTROLLER_ACCEPTED_UNVERIFIED` instead of raising `TypeError`.<br>2. In `rate_limit_for_host()`, parse meter ID from ONOS `Location` header first before rate-matching fallback, return `meter_id`/`device_id`, and clarify `rollback_plan` for `throttle_traffic` (`remove_meter_and_flow`). | Add unit tests for `unblock_ip` post-delete `None` guard and `rate_limit_for_host` `Location` header parsing & rollback plan metadata. |
| **P1-04** | `backend/app/decision.py` | Update automated rate-limit default from `50` bps to `50000` bps (50 kbps) and preserve existing decision return contract while safely annotating dry-run/staged executions. | Existing `test_risk_scoring_and_decision.py` + new test pass 100%. |

---

## Loop 3 — P2 Test Runner, Reproducibility & Documentation / Evidence Sync

| ID | Target Files | Minimal Patch | Verification Gate |
|---|---|---|---|
| **P2-01** | `docs/evidence/EVIDENCE_INDEX_AND_STEP64_REPORT.md` | Reconcile all file sizes and SHA-256 hashes directly against on-disk files (`sdnflowguard.db`, `sdnflowguard.db.bak`, all 6 evidence files in `backend/defense/evidence/`, all 4 state JSONs in `backend/collectors/state/`). | Automated verification script confirms 100% SHA-256 & byte-size match between doc and disk. |
| **P2-02** | `docs/testing/TEST_PLAN_AND_RESULTS.md`, `docs/security/SECURITY_DESIGN_AND_HARDENING.md`, `docs/academic/ACADEMIC_SCOPE_AND_TRACEABILITY.md`, `docs/operations/INSTALLATION_AND_DEPLOYMENT.md`, `docs/operations/RUNBOOK_AND_DEMO_GUIDE.md`, `docs/architecture/CLEAN_ARCHITECTURE_DESIGN.md`, `.github/workflows/sdn_flowguard_ci.yml` | Fix all stale test counts (`79`/`61` -> dynamic/actual count), wrong env var names (`SDNFLOW_ES_*` -> `SDNFLOW_ELK_*`), wrong header names (`X-API-Key` -> `X-SDNFlow-API-Key`), wrong paths (`infrastructure/compose.yaml` -> `docker-compose.yml`), and document Demo 01–06 + ONOS Raft recovery cleanly. | Cross-check grep confirms zero stale counts or wrong env var names in updated docs. |
| **P2-03** | `scripts/test.ps1` | Remove hardcoded `79-test` description; add `-BuildFrontend` option + build freshness check against `frontend/src`; add explicit zero-`.pyc`-outside-`venv` assertion. | `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1` exits 0 cleanly. |
| **P2-04** | `infrastructure/mininet/sdnflowguard_lab_topo.py` | Add clean, minimal, reproducible OpenFlow 1.3 Mininet lab topology script supporting `--topo single` (default `s1` + `h1,h2,h3`) and `--topo linear` (`s1,s2` + `h1..h4`). | Python syntax verified in-memory (`verify_syntax.py` / `ast.parse`). |

---

## Final Acceptance Verification Plan (Gates A–F)

1. Run `npm run build` in `frontend/` and verify zero build errors.
2. Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1` and verify all tests pass, `0` `.pyc` outside `venv`, `sdnflowguard.db` SHA-256 unchanged, `sdnflowguard-logo.png` SHA-256 unchanged.
3. Run `docker compose config --quiet` to verify compose syntax.
4. Probe live Docker services (Backend, Frontend, ES, Logstash, Kibana, ONOS) and document actual runtime status honestly (including live SIEM ingestion check if non-destructive, or marking ONOS/Mininet status truthfully).
5. Verify zero forbidden files (`.doc/.docx/.ppt/.pptx`/academic PDFs) in workspace.
6. Evaluate Gates A–F and produce final Vietnamese audit report (Sections A–H).
