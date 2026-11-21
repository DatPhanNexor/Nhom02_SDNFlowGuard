# SDNFlowGuard — Final Engineering Audit Report

**Audit Date:** 2026-11-18  
**Workspace:** `D:\Project\Nhom02_SDNFlowGuard`  
**Git Branch / Base Commit:** `main` @ `f3c85de` (+ 14 modified working-tree files & 1 untracked test file from prior Dashboard/Topology refinement)  
**Baseline Test Suite:** `85/85` unittest PASS, `4/4` CLI self-tests PASS, `87` backend Python files syntax-verified with `0` `.pyc` artifacts written.  
**Academic Context:** Học phần *Chuyên đề – Hệ thống mạng và bảo mật* (`123046`), UTH — Đề tài: *"Nghiên cứu và triển khai phòng thủ mạng tự động qua SDN tích hợp giám sát bằng ELK Stack"*.

---

## 1. Repository & Asset Inventory (Read-Only Baseline)

| Directory / Asset | Files | Size | Key Integrity Baseline |
|---|---:|---:|---|
| Total Workspace | 54,129 | 654.31 MB | Includes `frontend/node_modules` & `backend/venv` (excluded in `.gitignore`) |
| `frontend/` | 50,272 | 580.07 MB | React SPA + `public/sdnflowguard-logo.png` (`168,888 B`, SHA-256 `fb1f267cdafe39e99f97dc5c5d9eb06cde77ad6cf01c5e39a5739af0b590faba`) |
| `backend/` | 3,761 | 66.46 MB | Flask REST API (`run.py`), Clean Architecture (`sdnflowguard/`), Collectors, Defense, 85 tests |
| `database/sdnflowguard.db` | 1 | 61,440 B | `PRAGMA integrity_check = ok`; SHA-256 `3909de520f89ea050e7858104c8aa17bddd94d06af9db5ad84652404b9463fe9`; tables: `settings(5)`, `alerts(0)`, `flows(25)`, `events(8)`, `actions(89)` |
| `database/sdnflowguard.db.bak` | 1 | 61,440 B | Exact mirror of `sdnflowguard.db` (same SHA-256) |
| `docs/` | 11 | — | Architecture, Security, Testing, Evidence, Operations, Academic docs |
| `infrastructure/` & `docker-compose.yml` | 5 | — | 6-container Compose stack + Logstash pipeline + WSL config |
| `scripts/` | 5 | — | `manage.ps1`, `test.ps1`, `backup_database.ps1`, `reclaim_wsl_memory.ps1`, `verify_syntax.py` |
| Forbidden Office / Academic Binaries | **0** | 0 B | Verified `0` `.doc`, `.docx`, `.ppt`, `.pptx`, or academic PDFs inside workspace |

### Live Runtime Baseline Probe (2026-11-18)

| Component | Endpoint / Mechanism | Observed Baseline Status | Evidence / Notes |
|---|---|---|---|
| React Frontend (`sdnflowguard-frontend`) | `http://127.0.0.1:3000/healthz` | **LIVE_VERIFIED (UP)** | HTTP 200 `healthy` |
| Flask Backend (`sdnflowguard-backend`) | `http://127.0.0.1:5000/api/health` | **LIVE_VERIFIED (UP)** | HTTP 200 `status=OK`, `defense_mode=DRY_RUN`, `api_key_enabled=false` |
| Elasticsearch (`sdnflowguard-elasticsearch`) | `http://127.0.0.1:9200/_cluster/health` | **LIVE_VERIFIED (UP)** | `status=yellow` (single-node, 1 replica), 4 preserved indices (`sdnflowguard-events-2026.10.31`: 119 docs, `2026.11.05`: 6 docs, `2026.11.07`: 18 docs, `2026.11.08`: 2 docs; total 145 docs) |
| Logstash (`sdnflowguard-logstash`) | `http://127.0.0.1:18080` + `/api/logstash/pipeline-status` | **LIVE_VERIFIED (UP)** | `operational=true`, `pipeline_id=main`, `reload_failures=0` |
| Kibana (`sdnflowguard-kibana`) | `http://127.0.0.1:5601` | **LIVE_VERIFIED (UP)** | Reported `UP` by `/api/service-status` |
| ONOS Controller (`sdnflowguard-onos`) | `http://127.0.0.1:8181/onos/v1/*` | **DEGRADED / DOWN (HTTP 503)** | Container up 3h, Karaf OSGi error `ServiceException: Service factory returned null (ComponentConfigManager / AuditManager)` — known ONOS 2.7 Atomix/Raft state corruption after host/Docker restart. Additionally `/onos/v1/acl/rules` returned HTTP 404 because `acl` is missing from `ONOS_APPS` in `docker-compose.yml`. |
| WSL2 Mininet / OVS (`Ubuntu-26.04`) | `wsl -d Ubuntu-26.04` | **BLOCKED_BY_ENVIRONMENT (Interactive sudo)** | `mn`, `ovs-vsctl`, `tcpdump`, `python3` are installed; `sudo -n` requires interactive operator password, so live Mininet topology cannot be started non-interactively without operator password. |

---

## 2. Prioritized Engineering Findings (P0 / P1 / P2 / P3)

### P0 — Critical Security & Safety Gate Integrity Bugs

#### [P0-01] Missing `SDNFLOW_API_KEY` Treated as Authenticated Operator for Live Mutations
- **Location:** `backend/sdnflowguard/interfaces/http/security.py:16-31`, `backend/app/controller_actions.py:73-112`, `backend/run.py:782-1115`
- **Observed Evidence:**
  - `check_api_key()` returns `(True, None)` both when a valid `X-SDNFlow-API-Key` is provided **and** when `SDNFLOW_API_KEY` is empty/unset.
  - In `backend/run.py`, endpoints pass `operator_authenticated=authorized` (`True`) into `block_ip()` and `rate_limit_for_host()`.
  - In `controller_actions.py:90-95`, when `operator_authenticated is None` and `SDNFLOW_API_KEY` is not set, it falls back to `operator_authenticated = is_manual` (`True` by default for `"Admin"`).
- **Security Impact:** If an operator switches `SDNFLOW_DEFENSE_MODE=MANUAL_APPROVAL` without configuring `SDNFLOW_API_KEY`, any unauthenticated client on localhost can satisfy `operator_authenticated=True` and execute live ONOS rule mutations, violating the documented Fail-Safe Operator Authentication invariant (CEH v13 / Course Ch.1 Saltzer & Schroeder *Fail-Safe Defaults* & *Complete Mediation*).
- **Remediation:**
  1. Add `is_operator_authenticated(headers)` in `security.py` that returns `True` **only** when `SDNFLOW_API_KEY` is configured AND matches `X-SDNFlow-API-Key` or `Authorization: Bearer <key>` via constant-time `hmac.compare_digest`.
  2. Keep `check_api_key(headers)` backward-compatible for read/DRY_RUN lab demos when `SDNFLOW_API_KEY` is unset, while ensuring `operator_authenticated` passed to live-mutation Safety Gate checks is strictly `False` unless `SDNFLOW_API_KEY` is configured and verified.
  3. In `controller_actions.py:_evaluate_action_gate()`, never promote `operator_authenticated` to `True` simply because `configured_key` is empty.

#### [P0-02] Broken `operator_authenticated` Propagation in `block_ip -> create_acl_rule` and Other Mutating Actions
- **Location:** `backend/app/controller_actions.py:169-286, 306-399, 556-620, 795-958`, `backend/run.py:906-1103`
- **Observed Evidence:**
  - `block_ip()` accepts `operator_authenticated=None`, evaluates the Safety Gate with it, and then calls `create_acl_rule(...)` at line 273 **without** forwarding `operator_authenticated`.
  - Inside `create_acl_rule()`, `_evaluate_action_gate()` runs again with `operator_authenticated=None`. When `SDNFLOW_API_KEY` is configured, `_evaluate_action_gate()` converts `None` to `False`, causing an authenticated operator's `block_ip()` call in `MANUAL_APPROVAL` mode to silently fail the Safety Gate and downgrade to `DRY_RUN_SIMULATED`!
  - `allow_ip()`, `unblock_ip()`, `redirect_traffic()`, `redirect_traffic_full()`, and `redirect_to_intermediate_ovs()` do not even accept `operator_authenticated` as a parameter, and `/api/allow`, `/api/redirect`, `/api/redirectHoney`, `/api/unblock`, `/api/defense/rollback` never pass it.
- **Impact:** Live authenticated blocking in `MANUAL_APPROVAL` mode is broken when `SDNFLOW_API_KEY` is configured, and operator auth is inconsistent across control actions.
- **Remediation:** Add `operator_authenticated: bool | None = None` to `create_acl_rule`, `allow_ip`, `unblock_ip`, `redirect_traffic`, `redirect_traffic_full`, `redirect_to_intermediate_ovs`, forward it from `block_ip` -> `create_acl_rule`, and pass `is_operator_authenticated(request.headers)` from all mutating endpoints in `backend/run.py`.

#### [P0-03] Unprotected Mutating Endpoint `/api/save-flows` & Raw Exception Leakage in HTTP 500 Responses
- **Location:** `backend/run.py:509, 526, 549, 561, 571, 592, 602, 612, 616-623, 738, 768, 778`, `backend/sdnflowguard/interfaces/http/routes.py:55, 73`
- **Observed Evidence:**
  - `POST /api/save-flows` mutates SQLite (`flows` table) without calling `check_api_key(request.headers)`.
  - Multiple `except Exception as exc:` handlers return raw `str(exc)` directly to HTTP clients (risk of leaking internal file paths, SQLite details, or stack internals).
- **Remediation:** Add `check_api_key(request.headers)` to `/api/save-flows` and sanitize unexpected 500 error responses (log internally via structured logger, return safe error message + `request_id`).

#### [P0-04] Build-Time `REACT_APP_API_KEY` Exposure Anti-Pattern
- **Location:** `frontend/src/config/apiConfig.js:11-14`
- **Observed Evidence:** `getApiHeaders()` reads `process.env.REACT_APP_API_KEY`, which Create React App statically inlines into public client JS bundles at build time.
- **Remediation:** Support runtime session-scoped operator key (`sessionStorage.getItem('sdnflow_operator_api_key')`) with an optional UI helper or safe fallback, and document explicitly that operator API keys must never be baked into production `REACT_APP_*` builds.

---

### P1 — SDN Control Plane, Execution Verification & Telemetry Bugs

#### [P1-01] ONOS `acl` Application Missing from `docker-compose.yml` (`ONOS_APPS`)
- **Location:** `docker-compose.yml:53`
- **Observed Evidence:** `ONOS_APPS=drivers,openflow,gui2,fwd` omits `acl` (`org.onosproject.acl`). Live probe of `http://127.0.0.1:8181/onos/v1/acl/rules` returned **HTTP 404 Not Found**.
- **Impact:** Even in `MANUAL_APPROVAL` or `ACTIVE_ENFORCEMENT` mode with a healthy ONOS container, `POST /onos/v1/acl/rules` and `GET /onos/v1/acl/rules` fail with 404 unless `acl` is activated.
- **Remediation:** Update `ONOS_APPS=drivers,openflow,gui2,fwd,acl` in `docker-compose.yml` and add lightweight container `healthcheck` definitions for ONOS and Elasticsearch where safe.

#### [P1-02] HTTP 200/201 Treated as `RULE_APPLIED` Without Controller Read-Back Verification & Silent False-Success HTTP 200 in Flask Routes
- **Location:** `backend/app/controller_actions.py:209-236, 610-635, 701-755, 853-866, 945-958`, `backend/run.py:906-1042`
- **Observed Evidence:**
  - `create_acl_rule()` marks `status="RULE_APPLIED"` purely on HTTP 200/201 without checking whether the rule is visible via `list_acl_rules()` or `ONOSClient.verify_ip_flow_rule_present()`, and does not return structured `verification_status` (`CONTROLLER_ACCEPTED` vs `RULE_INSTALLED` vs `UNVERIFIED`) or `timestamp_utc`.
  - `redirect_traffic()` (line 613), `redirect_to_intermediate_ovs()` (line 946), and `rate_limit_for_host()` (lines 701, 745) execute `requests.post()` / `requests.get()` **without** `try/except requests.RequestException`, causing unhandled HTTP 500 crashes when ONOS is unreachable!
  - In `backend/run.py`:
    - `/api/allow` returns HTTP 200 `"Allowed traffic ... successfully"` even when `status` is `REJECTED_BY_SAFETY_GATE` or `EXECUTION_FAILED`!
    - `/api/rate-limit` returns HTTP 200 `"Rate limit applied ..."` even when `status` is `HOST_NOT_FOUND`, `VALIDATION_ERROR`, or `EXECUTION_FAILED`!
    - `/api/redirect` and `/api/redirectHoney` return HTTP 200 `"Redirected traffic ... successfully"` even when `status` is `HOST_NOT_FOUND`, `NO_PATH_FOUND`, or `EXECUTION_FAILED`!
- **Remediation:**
  1. Wrap all ONOS HTTP calls in `controller_actions.py` with `try/except requests.RequestException` returning structured `EXECUTION_FAILED` responses.
  2. Add post-write read-back verification (`controller_accepted`, `verification_status`: `RULE_INSTALLED` / `CONTROLLER_ACCEPTED_UNVERIFIED` / `EXECUTION_FAILED`, `timestamp_utc`) to `create_acl_rule`, `rate_limit_for_host`, and `redirect_traffic`, while preserving backward-compatible `status` (`RULE_APPLIED` when verified or accepted, with explicit `verification_status` so callers never mistake acceptance for dataplane proof).
  3. Update `/api/allow`, `/api/rate-limit`, `/api/redirect`, `/api/redirectHoney` in `backend/run.py` to return proper HTTP status codes (`403` for Safety Gate rejection, `400` for validation errors, `404` for `HOST_NOT_FOUND`/`NO_PATH_FOUND`, `502` for `EXECUTION_FAILED`).

#### [P1-03] `unblock_ip()` Post-Delete `NoneType` Crash & Rate-Limit Meter Rollback Gap
- **Location:** `backend/app/controller_actions.py:474, 690-755`, `backend/sdnflowguard/domain/policies/safety_gate.py:224-228`
- **Observed Evidence:**
  - `unblock_ip()` line 474 calls `rem_rules = list_acl_rules()` and then `any(... for r in rem_rules)` without checking `if rem_rules is None:`. If ONOS drops between DELETE and verification GET, it raises `TypeError: 'NoneType' object is not iterable`.
  - `rate_limit_for_host()` matches created meters solely by `rate == rate_kb_per_sec` (fragile if multiple meters exist) and attaches the flow rule using `ETH_DST` (limits inbound traffic *to* host, not outbound attack traffic *from* host; should document/match `ETH_SRC` or both clearly). Moreover, `safety_gate.py:226` lists `rollback_action: "unblock_ip"` for `throttle_traffic`, even though `unblock_ip` only removes ACL rules and does not remove OpenFlow meters/flows.
- **Remediation:**
  1. Guard `rem_rules is None` in `unblock_ip()`, returning `verification_result="CONTROLLER_ACCEPTED_UNVERIFIED"` instead of crashing.
  2. In `rate_limit_for_host()`, extract meter ID from ONOS `Location` response header first (fallback to rate match), return `meter_id` and `device_id` in the structured response, and add a dedicated `remove_rate_limit_for_host()` / rollback metadata (`rollback_action: "remove_meter_and_flow"`) in `safety_gate.py` so rollback plans are truthful.

#### [P1-04] Automated Risk Engine (`decision.py`) Ignores Action Results & Uses 50 bps Rate Limit
- **Location:** `backend/app/decision.py:84-106`
- **Observed Evidence:**
  - `decision.py` calls `block_ip()`, `redirect_traffic_full()`, `rate_limit_for_host(source_ip, rate_limit_bps=50)`, `redirect_to_intermediate_ovs()` without inspecting returned status (`DRY_RUN_SIMULATED` vs `REJECTED_BY_SAFETY_GATE` vs `RULE_APPLIED`), always returning `["Block"]` / `["Rate Limit"]`.
  - `rate_limit_bps=50` (50 bits/sec, likely meant 50,000 bps = 50 kbps) clamps to 1 kbps.
- **Remediation:** Update `decision.py` to use `rate_limit_bps=50000` (50 kbps) and reflect simulated/rejected outcomes clearly while preserving backward compatibility for existing unit tests (`test_risk_scoring_and_decision.py`).

---

### P2 — Evidence Integrity, Documentation Drift, Test Runner & Reproducibility

#### [P2-01] Severe Evidence Metadata Drift in `docs/evidence/EVIDENCE_INDEX_AND_STEP64_REPORT.md`
- **Location:** `docs/evidence/EVIDENCE_INDEX_AND_STEP64_REPORT.md:7-18`
- **Observed Discrepancies (Doc vs Actual Disk):**
  - `database/sdnflowguard.db`: Doc `28,672 B` vs Actual `61,440 B` (SHA-256 `3909de52...` matches).
  - `database/netsecflow.db.bak`: Doc lists nonexistent file; actual backup is `database/sdnflowguard.db.bak` (`61,440 B`, `3909de52...`).
  - `ingress_icmp_20261101_014645.txt`: Doc `5,146 B` (`3076efcc...`) vs Actual `7,694 B` (`33e319e7...`).
  - `ingress_icmp_20261101_014645.json`: Doc `2,202 B` (`05a65922...`) vs Actual `1,195 B` (`de91995d...`).
  - All 4 `backend/collectors/state/*.json` files have stale sizes and stale SHA-256 hashes in the doc.
  - `ingress_icmp_20261101_014454.txt` and `ingress_icmp_20261101_014614.txt` are omitted from the index.
- **Remediation:** Recompute exact byte sizes and SHA-256 hashes directly from disk and synchronize `EVIDENCE_INDEX_AND_STEP64_REPORT.md`.

#### [P2-02] Cross-Document Metadata & Contract Drift Across `docs/` and CI
- **Locations:**
  - `scripts/test.ps1:5` and `.github/workflows/sdn_flowguard_ci.yml:48` and `docs/operations/INSTALLATION_AND_DEPLOYMENT.md:32` and `docs/academic/ACADEMIC_SCOPE_AND_TRACEABILITY.md:27`: still hardcode `79` tests (and `RUNBOOK_AND_DEMO_GUIDE.md:13` says `61` tests), whereas actual suite has `85` (and will grow after remediation tests).
  - `docs/security/SECURITY_DESIGN_AND_HARDENING.md:7,13,14,27`: references wrong env var `SDNFLOW_ES_PASSWORD` (actual: `SDNFLOW_ELK_PASSWORD`), wrong decorator `@require_api_key_if_configured` / header `X-API-Key` (actual: `check_api_key` / `X-SDNFlow-API-Key`), wrong `limit: 1..100` (actual: `1..500` / `1..200`), and claims `RULE_VERIFIED` via `verify_ip_flow_rule_present()` before it was wired into `controller_actions.py`.
  - `docs/operations/INSTALLATION_AND_DEPLOYMENT.md:23,24,26`: references `SDNFLOW_ES_URL`, `SDNFLOW_LOGSTASH_URL`, `X-API-Key` instead of actual `SDNFLOW_ELK_URL`, `SDNFLOW_LOGSTASH_HOST`/`PORT`, `X-SDNFlow-API-Key`.
  - `docs/academic/ACADEMIC_SCOPE_AND_TRACEABILITY.md:5,14,15,18`: claims `Tong_quan_de_tai.docx` wasn't consulted, points to `infrastructure/compose.yaml` instead of canonical `docker-compose.yml`, lists `LiveSdnSummary.js`/`SdnPortRates.js` in `components/` instead of `pages/`.
- **Remediation:** Synchronize all documentation and CI labels to match verified code and test outputs.

#### [P2-03] `scripts/test.ps1` Frontend Gate Does Not Support Live Build Verification or Zero-Bytecode Assertion
- **Location:** `scripts/test.ps1:74-93`
- **Observed Evidence:** Gate 4 only checks `Test-Path frontend\build\index.html` (can pass on a stale build), and Gate 5 does not explicitly verify zero `.pyc` files outside `backend/venv`.
- **Remediation:** Add `-RunFrontendBuild` switch (plus staleness warning if `frontend/src` is newer than `frontend/build/index.html`) and add an explicit check verifying zero `.pyc` files outside `backend/venv`.

#### [P2-04] Missing Reproducible Mininet Lab Topology Script & ONOS Raft Recovery Guidance
- **Location:** `infrastructure/` and `docs/operations/RUNBOOK_AND_DEMO_GUIDE.md`
- **Observed Evidence:** Users must manually type long `sudo mn ...` flags, and there is no reproducible Mininet topology script or automated ONOS Raft recovery command documented for when `sdnflowguard-onos` hits `ServiceException: Service factory returned null` after Docker/host restarts.
- **Remediation:** Add a clean, reproducible `infrastructure/mininet/sdnflowguard_lab_topo.py` script (OpenFlow 1.3, configurable `single,3` or `linear,2`) and document ONOS Raft recovery + Demo 01–06 exact commands in `RUNBOOK_AND_DEMO_GUIDE.md`.

---

### P3 — Low Priority / Hygiene Observations

#### [P3-01] `frontend/public/vendor` Legacy SB-Admin-2 Static Assets
- **Location:** `frontend/public/vendor/`
- **Observed Evidence:** Legacy static Bootstrap/Chart.js/FontAwesome vendor tree (~1,800+ SVG/CSS/JS files) remains in `frontend/public/vendor`. Need to verify whether `public/index.html` still references any files from `public/vendor` before touching anything (preserve stability if referenced).

#### [P3-02] Elasticsearch Single-Node `yellow` Cluster Health
- **Location:** `docker-compose.yml:59-73`, `infrastructure/logstash/pipeline/01-sdnflowguard.conf`
- **Observed Evidence:** Daily `sdnflowguard-events-*` indices default to `number_of_replicas: 1`, causing single-node ES to report `status=yellow` (4 unassigned replica shards). Functional impact is none in a single-node lab, and should be documented clearly rather than misreported as an outage.

#### [P3-03] Academic Submission Format Alignment Note
- **Location:** External course guideline `QUY DINH TRINH BAY BAO CAO BAI TẬP LỚN.pdf` vs user project setup
- **Observed Evidence:** The university PDF mentions a submission folder structure (`SETUP / SOURCE / THESIS / SOFT / HUONGDAN.PDF`), whereas the user explicitly requested keeping the code repository clean with **zero** `.doc/.docx/.ppt/.pptx` files and preparing the >60-page Word report separately outside this workspace. Documented transparently in `docs/audit/REQUIREMENTS_TRACEABILITY.md` for lecturer confirmation.
