# Clean Architecture Design — SDNFlowGuard

## 1. Architectural Vision & Strangler Pattern

`Nhom02_SDNFlowGuard` applies **Clean Architecture (Hexagonal / Ports & Adapters)** via the **Strangler Pattern**:
- All new domain logic, safety policies, evidence correlation rules, SIEM log normalizers, and structured observability reside in `backend/sdnflowguard/`.
- Existing entrypoints (`backend/run.py`, `backend/app/*.py`, `backend/collectors/*.py`, `backend/defense/*.py`) remain 100% backward-compatible in their CLI flags and HTTP REST contracts while delegating core domain decisions, safety gating, and configuration loading to `backend/sdnflowguard/`.

```
+-----------------------------------------------------------------------+
|                   Interfaces & Entrypoints Layer                      |
|  - Flask API (backend/run.py + sdnflowguard/interfaces/http/routes.py)|
|  - CLI Collectors & Monitors (backend/collectors/*.py)                |
|  - CLI Defense & Evidence Tools (backend/defense/*.py)                |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                        Application Layer                              |
|  - Use Cases (sdnflowguard/application/use_cases.py)                  |
|    * EvaluateEvidenceCorrelationUseCase (Step 64)                     |
|    * EvaluateDefensePolicyUseCase                                     |
|    * ProposeOrExecuteDefenseActionUseCase (Safety Gate + Rollback)    |
|    * NormalizeSiemLogsUseCase (ONOS / Firewall / Windows Event Log)   |
|  - DTOs & Repository/Gateway Interfaces                               |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                      Domain Layer (Pure Python)                       |
|  - Entities & Value Objects (sdnflowguard/domain/models.py)           |
|  - Step 64 Evidence Correlation Service (evidence_correlation.py)     |
|  - SIEM Multi-Source Log Normalizer (siem_log_normalizer.py)          |
|  - Risk Scoring Policy (domain/policies/risk_scoring.py)              |
|  - Defense Policy Engine (domain/policies/defense_policy.py)          |
|  - Active Defense Safety Gate (domain/policies/safety_gate.py)        |
+-----------------------------------+-----------------------------------+
                                    ^
                                    |
+-----------------------------------------------------------------------+
|                       Infrastructure Layer                            |
|  - Environment Config Loader (configuration/settings.py)              |
|  - SQLite Repository (persistence/sqlite_repository.py)               |
|  - ONOS REST Client (onos/onos_client.py)                             |
|  - Elasticsearch & Logstash Clients (elasticsearch/, logstash/)       |
|  - Structured JSON Observability (observability/structured_logger.py) |
+-----------------------------------------------------------------------+
```

## 2. Layer Responsibilities

### 2.1. Domain Layer (`backend/sdnflowguard/domain/`)
- **Zero External I/O:** Contains no HTTP calls, database queries, or filesystem mutations.
- **Step 64 Host Evidence Correlation (`domain/services/evidence_correlation.py`):** Correlates Step 63 switch ingress packet observations (`ingress_port`, `observed_source_mac`, `observed_source_ip`) with ONOS topology (`devices`, `ports`, `hosts`, `flows`) and optional UTC capture metadata (`capture_started_utc`, `capture_finished_utc`).
- **Active Defense Safety Gate (`domain/policies/safety_gate.py`):** Enforces fail-safe invariants before any ONOS ACL or Intent mutation can occur:
  1. Rejects invalid, loopback (`127.0.0.0/8`), link-local, multicast, broadcast, or allowlisted/infrastructure IP addresses (Controller IP, ELK IP, Gateway IP).
  2. Rejects any automated action triggered by a `test_only=True` alert.
  3. Requires either corroborated Step 64 source attribution + verified alert window, or explicit operator manual approval.
  4. Defaults to `DefenseMode.DRY_RUN` (`allowed_to_execute=False`, `dry_run=True`).

### 2.2. Application Layer (`backend/sdnflowguard/application/`)
- Orchestrates domain services and infrastructure gateways through explicit use cases (`EvaluateEvidenceCorrelationUseCase`, `EvaluateDefensePolicyUseCase`, `ProposeOrExecuteDefenseActionUseCase`, `NormalizeSiemLogsUseCase`).

### 2.3. Infrastructure Layer (`backend/sdnflowguard/infrastructure/`)
- **`AppSettings` (`configuration/settings.py`):** Centralizes environment variable loading (`SDNFLOW_DEFENSE_MODE`, `SDNFLOW_ONOS_URL`, `SDNFLOW_ES_URL`, `SDNFLOW_LOGSTASH_URL`, `SDNFLOW_DB_PATH`, `SDNFLOW_API_KEY`, etc.) without hardcoded secrets.
- **`SQLiteRepository` (`persistence/sqlite_repository.py`):** Thread-safe SQLite access using context managers and parameterized SQL queries while supporting `SDNFLOW_DB_PATH` overrides for isolated testing.
- **`ONOSClient` (`onos/onos_client.py`):** Lazily resolves credentials at call time (eliminating import-time side effects) and provides flow rule verification (`verify_ip_flow_rule_present`).

### 2.4. Interfaces Layer (`backend/sdnflowguard/interfaces/http/` & `backend/run.py`)
- Exposes Flask Blueprint `/api/defense/*`, `/api/siem/*`, and `/api/health` alongside all 23 legacy routes in `backend/run.py`.
- Enforces optional API key protection (`X-API-Key` header when `SDNFLOW_API_KEY` is set) on mutating endpoints.

