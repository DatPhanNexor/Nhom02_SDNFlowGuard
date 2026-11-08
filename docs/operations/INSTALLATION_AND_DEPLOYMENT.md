# Installation & Deployment Guide — SDNFlowGuard

## 1. System Requirements

- **Operating System:** Windows 10/11 (PowerShell 5.1+ or PowerShell 7+)
- **Python Environment:** Python **3.10.10** at `D:\Project\Nhom02_SDNFlowGuard\backend\venv\Scripts\python.exe`
- **Node.js & npm:** Node.js 18+ (`npm.cmd`) for building/running the React frontend
- **Docker Desktop:** Required when running the containerized SDN & ELK lab (`onos`, `elasticsearch`, `logstash`, `kibana`, `mininet`)

---

## 2. Environment Configuration (`.env`)

1. Copy the root environment template:
   ```powershell
   Copy-Item D:\Project\Nhom02_SDNFlowGuard\.env.example D:\Project\Nhom02_SDNFlowGuard\.env
   ```
2. Key environment variables in `.env`:
   - `SDNFLOW_DEFENSE_MODE=DRY_RUN` *(Default — prevents accidental ONOS flow/ACL mutations)*
   - `SDNFLOW_ONOS_URL=http://127.0.0.1:8181/onos/v1`
   - `SDNFLOW_ONOS_USER=onos`
   - `SDNFLOW_ONOS_PASSWORD=rocks` *(Local lab credential; configure only in `.env`, never hardcode in source)*
   - `SDNFLOW_ES_URL=http://127.0.0.1:9200`
   - `SDNFLOW_LOGSTASH_URL=http://127.0.0.1:18080`
   - `SDNFLOW_DB_PATH=D:\Project\Nhom02_SDNFlowGuard\database\sdnflowguard.db`
   - `SDNFLOW_API_KEY=` *(Optional; if set, mutating API endpoints require header `X-API-Key`)*

---

## 3. Verifying System Health & Running Automated Tests

Run the non-destructive health check and full 79-test suite:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\manage.ps1 -Action check
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

---

## 4. Starting the 6-Container SDNFlowGuard Stack (Docker Compose)

```powershell
cd D:\Project\Nhom02_SDNFlowGuard
docker compose up -d --build
docker compose ps
```

Service endpoints exposed on `127.0.0.1`:
- **ONOS Controller GUI / REST API:** `http://127.0.0.1:8181/onos/ui` (`http://127.0.0.1:8181/onos/v1/docs`)
- **OpenFlow Port:** `127.0.0.1:6653`
- **Elasticsearch:** `http://127.0.0.1:9200`
- **Kibana:** `http://127.0.0.1:5601`
- **Logstash HTTP Input:** `http://127.0.0.1:18080`

---

## 5. Starting Backend (Flask) and Frontend (React)

### 5.1. Start Flask Backend (`http://127.0.0.1:5000`)
```powershell
cd D:\Project\Nhom02_SDNFlowGuard\backend
$env:PYTHONDONTWRITEBYTECODE="1"
D:\Project\Nhom02_SDNFlowGuard\backend\venv\Scripts\python.exe -B run.py
```

### 5.2. Start React Frontend (`http://127.0.0.1:3000`)
```powershell
cd D:\Project\Nhom02_SDNFlowGuard\frontend
npm.cmd start
```

### 5.3. Build Production Frontend Bundle
```powershell
cd D:\Project\Nhom02_SDNFlowGuard\frontend
npm.cmd run build
```

