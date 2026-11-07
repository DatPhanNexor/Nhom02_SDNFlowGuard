<#
.SYNOPSIS
    SDNFlowGuard Unified Management & Operations Controller.
.DESCRIPTION
    Provides unified management for the 6-container SDNFlowGuard stack,
    system health checks, log inspection, automated testing, and demo workflow.
.PARAMETER Action
    The operational command to execute:
    - up     : Start all 6 containers via Docker Compose (with optional build)
    - down   : Safely stop containers without deleting volumes or state
    - status : Inspect container state and local port listeners
    - check  : Run non-destructive system health verification
    - logs   : View container logs (optional -Service parameter)
    - test   : Run automated test suite via scripts\test.ps1
    - guide  : Display the demonstration scenario guide
    - open   : Open React Dashboard in default web browser
.PARAMETER Service
    Optional service name for logs (backend, frontend, onos, elasticsearch, logstash, kibana).
.PARAMETER Build
    When specified with 'up', forces a build of the images before starting.
.PARAMETER SkipKibana
    When specified with 'up', starts core services without Kibana to save ~550MB RAM.
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet("up", "down", "status", "check", "logs", "test", "guide", "open", "reclaim")]
    [string]$Action = "status",

    [Parameter(Position = 1)]
    [string]$Service = "",

    [switch]$Build,
    [switch]$SkipKibana
)

$ErrorActionPreference = "Continue"
$ScriptDir = $PSScriptRoot
$ProjectRoot = Split-Path -Parent $ScriptDir
$ComposeFile = Join-Path $ProjectRoot "docker-compose.yml"
if (-not (Test-Path $ComposeFile)) {
    $ComposeFile = Join-Path $ProjectRoot "infrastructure\compose.yaml"
}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   SDNFlowGuard: Unified Stack Manager                               " -ForegroundColor Cyan
Write-Host "   Department of Information Technology - UTH University (2026)      " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Action: $Action | Working Directory: $ProjectRoot`n" -ForegroundColor Gray

switch ($Action) {
    "up" {
        Set-Location $ProjectRoot
        $buildFlag = if ($Build) { "--build" } else { "" }
        Write-Host "[START] Staggered launch of SDNFlowGuard stack..." -ForegroundColor Cyan

        # Step 0: Ensure external persistent volume exists
        $volCheck = docker volume ls --filter "name=^sdnflowguard-elasticsearch-data$" --format "{{.Name}}" 2>$null
        if (-not $volCheck) {
            Write-Host "        Creating external volume sdnflowguard-elasticsearch-data..." -ForegroundColor Gray
            docker volume create sdnflowguard-elasticsearch-data | Out-Null
        }

        # Step 1: Core Controller & Database (Elasticsearch, ONOS)
        Write-Host "  [1/3] Starting Core Infrastructure (elasticsearch, onos)..." -ForegroundColor White
        if ($buildFlag) {
            docker compose -f $ComposeFile up -d --build elasticsearch onos
        } else {
            docker compose -f $ComposeFile up -d elasticsearch onos
        }

        # Bounded wait for Core layer readiness (max 30s)
        Write-Host "        Waiting for Elasticsearch (9200) and ONOS (8181) readiness (max 30s)..." -ForegroundColor Gray
        $esReady = $false
        $onosReady = $false
        for ($i = 0; $i -lt 30; $i++) {
            if (-not $esReady) {
                $esConn = Get-NetTCPConnection -LocalPort 9200 -State Listen -ErrorAction SilentlyContinue
                if ($esConn) { $esReady = $true }
            }
            if (-not $onosReady) {
                $onosConn = Get-NetTCPConnection -LocalPort 8181 -State Listen -ErrorAction SilentlyContinue
                if ($onosConn) { $onosReady = $true }
            }
            if ($esReady -and $onosReady) { break }
            Start-Sleep -Seconds 1
        }

        $stackState = "READY"
        if ($esReady -and $onosReady) {
            Write-Host "        [OK] Core services ready (Elasticsearch: 9200, ONOS: 8181)." -ForegroundColor Green
        } elseif (-not $esReady -and -not $onosReady) {
            Write-Host "        [FATAL] Both Elasticsearch and ONOS failed to listen within 30s." -ForegroundColor Red
            Write-Host "        Aborting application layer startup to prevent cascade failure." -ForegroundColor Red
            exit 1
        } else {
            $stackState = "DEGRADED"
            if (-not $esReady) { Write-Host "        [WARN] Elasticsearch (9200) not responding within timeout." -ForegroundColor Yellow }
            if (-not $onosReady) { Write-Host "        [WARN] ONOS (8181) not responding within timeout." -ForegroundColor Yellow }
            Write-Host "        Proceeding in DEGRADED mode..." -ForegroundColor Yellow
        }

        # Step 2: Telemetry Ingestion & Application Services (Logstash, Backend, Frontend)
        Write-Host "  [2/3] Starting Telemetry & Application Services (logstash, backend, frontend)..." -ForegroundColor White
        if ($buildFlag) {
            docker compose -f $ComposeFile up -d --build logstash backend frontend
        } else {
            docker compose -f $ComposeFile up -d logstash backend frontend
        }

        # Step 3: Observability UI (Kibana)
        if ($SkipKibana) {
            Write-Host "  [3/3] Observability UI (kibana): SKIPPED (-SkipKibana specified)" -ForegroundColor Yellow
            Write-Host "        Operating Mode: 5-SERVICE APPLICATION MODE (saving ~500MB RAM)" -ForegroundColor Yellow
            docker compose -f $ComposeFile stop kibana 2>$null
        } else {
            Write-Host "  [3/3] Starting Observability UI (kibana)..." -ForegroundColor White
            docker compose -f $ComposeFile up -d kibana
        }

        if ($LASTEXITCODE -eq 0) {
            if ($stackState -eq "DEGRADED") {
                Write-Host "`n[WARN] SDNFlowGuard stack launched with DEGRADED dependencies." -ForegroundColor Yellow
            } elseif ($SkipKibana) {
                Write-Host "`n[PASS] SDNFlowGuard 5-Service Application Stack launched successfully (Kibana Skipped)." -ForegroundColor Green
            } else {
                Write-Host "`n[PASS] SDNFlowGuard 6-Container Stack launched successfully." -ForegroundColor Green
            }
            Write-Host "  Frontend Dashboard : http://localhost:3000" -ForegroundColor White
            Write-Host "  Backend Health API : http://localhost:5000/api/health" -ForegroundColor White
            Write-Host "  ONOS REST API      : http://localhost:8181/onos/v1/devices" -ForegroundColor White
            if (-not $SkipKibana) {
                Write-Host "  Kibana Dashboard   : http://localhost:5601" -ForegroundColor White
            } else {
                Write-Host "  Kibana Dashboard   : (Disabled via -SkipKibana - 5-Service Mode)" -ForegroundColor DarkGray
            }
        } else {
            Write-Host "`n[ERROR] Docker Compose up exited with code $LASTEXITCODE" -ForegroundColor Red
            exit $LASTEXITCODE
        }
    }

    "down" {
        Write-Host "[STOP] Safely stopping SDNFlowGuard containers (volumes preserved)..." -ForegroundColor Yellow
        Set-Location $ProjectRoot
        docker compose -f $ComposeFile stop
        Write-Host "`n[INFO] Containers stopped safely. No persistent volumes were deleted." -ForegroundColor Green
    }

    "status" {
        Set-Location $ProjectRoot
        $runningContainers = @(& docker compose -f $ComposeFile ps --filter "status=running" --format "{{.Name}}" 2>$null)
        $kibanaRunning = $runningContainers -contains "sdnflowguard-kibana"
        $backendRunning = $runningContainers -contains "sdnflowguard-backend"

        if (-not $kibanaRunning -and $backendRunning) {
            Write-Host "[MODE] 5-SERVICE APPLICATION MODE ACTIVE (Kibana Skipped)" -ForegroundColor Yellow
        } else {
            Write-Host "[MODE] 6-CONTAINER FULL STACK MODE" -ForegroundColor Cyan
        }

        Write-Host "`n[1/2] Docker Containers Status:" -ForegroundColor Cyan
        docker compose -f $ComposeFile ps -a

        Write-Host "`n[2/2] Local Service Port Listeners:" -ForegroundColor Cyan
        $Ports = @(
            @{ Port = 3000; Service = "React Frontend"; Required = $true },
            @{ Port = 5000; Service = "Flask Backend API"; Required = $true },
            @{ Port = 8181; Service = "ONOS REST API"; Required = $true },
            @{ Port = 6653; Service = "ONOS OpenFlow"; Required = $true },
            @{ Port = 9200; Service = "Elasticsearch HTTP"; Required = $true },
            @{ Port = 5601; Service = "Kibana Dashboard"; Required = $false },
            @{ Port = 18080; Service = "Logstash Telemetry"; Required = $false }
        )
        foreach ($item in $Ports) {
            $listening = Get-NetTCPConnection -LocalPort $item.Port -State Listen -ErrorAction SilentlyContinue
            if ($listening) {
                Write-Host ("  [ONLINE]   Port {0,-5} ({1})" -f $item.Port, $item.Service) -ForegroundColor Green
            } elseif ($item.Port -eq 5601 -and -not $kibanaRunning) {
                Write-Host ("  [SKIPPED]  Port {0,-5} ({1} - Skipped via -SkipKibana)" -f $item.Port, $item.Service) -ForegroundColor DarkYellow
            } else {
                Write-Host ("  [OFFLINE]  Port {0,-5} ({1})" -f $item.Port, $item.Service) -ForegroundColor DarkGray
            }
        }
    }

    "check" {
        Write-Host "[HEALTH CHECK] Running Non-Destructive Environment & Health Inspection..." -ForegroundColor Cyan
        $allPassed = $true

        # 1. Python Venv check
        $PythonExe = Join-Path $ProjectRoot "backend\venv\Scripts\python.exe"
        if (Test-Path $PythonExe) {
            $PyVer = & $PythonExe -B -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
            Write-Host "  [PASS] Python Environment: $PyVer ($PythonExe)" -ForegroundColor Green
        } else {
            Write-Host "  [INFO] Host Python venv not found (Container mode active)" -ForegroundColor Gray
        }

        # 2. SQLite Database integrity
        $DbPath = Join-Path $ProjectRoot "database\sdnflowguard.db"
        if (Test-Path $DbPath) {
            $DbHash = (Get-FileHash -Path $DbPath -Algorithm SHA256).Hash.ToLower()
            Write-Host "  [PASS] SQLite Database SHA-256: $DbHash" -ForegroundColor Green
        } else {
            Write-Host "  [FAIL] Database not found at $DbPath" -ForegroundColor Red
            $allPassed = $false
        }

        # 3. Docker CLI & Compose Check
        $DockerCmd = Get-Command "docker" -ErrorAction SilentlyContinue
        if ($DockerCmd) {
            $DockerInfo = & docker info 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [PASS] Docker Engine is running" -ForegroundColor Green
            } else {
                Write-Host "  [WARN] Docker Desktop is stopped or unreachable" -ForegroundColor Yellow
                $allPassed = $false
            }
        } else {
            Write-Host "  [FAIL] Docker CLI not installed or not in PATH" -ForegroundColor Red
            $allPassed = $false
        }

        # 4. Port probing
        $runningContainers = @(& docker compose -f $ComposeFile ps --filter "status=running" --format "{{.Name}}" 2>$null)
        $kibanaRunning = $runningContainers -contains "sdnflowguard-kibana"

        $Ports = @(
            @{ Port = 3000; Service = "React Frontend"; Required = $true },
            @{ Port = 5000; Service = "Flask Backend API"; Required = $true },
            @{ Port = 8181; Service = "ONOS REST API"; Required = $true },
            @{ Port = 6653; Service = "ONOS OpenFlow"; Required = $true },
            @{ Port = 9200; Service = "Elasticsearch HTTP"; Required = $true },
            @{ Port = 5601; Service = "Kibana Dashboard"; Required = $false },
            @{ Port = 18080; Service = "Logstash Telemetry"; Required = $false }
        )
        Write-Host "`n  --- Service Port Listeners ---" -ForegroundColor Gray
        foreach ($item in $Ports) {
            $listening = Get-NetTCPConnection -LocalPort $item.Port -State Listen -ErrorAction SilentlyContinue
            if ($listening) {
                Write-Host ("  [ONLINE]   Port {0,-5} ({1})" -f $item.Port, $item.Service) -ForegroundColor Green
            } elseif ($item.Port -eq 5601 -and -not $kibanaRunning) {
                Write-Host ("  [SKIPPED]  Port {0,-5} ({1} - 5-Service Mode Active)" -f $item.Port, $item.Service) -ForegroundColor DarkYellow
            } else {
                if ($item.Required) {
                    Write-Host ("  [FAIL]     Port {0,-5} ({1} REQUIRED SERVICE OFFLINE)" -f $item.Port, $item.Service) -ForegroundColor Red
                    $allPassed = $false
                } else {
                    Write-Host ("  [OFFLINE]  Port {0,-5} ({1} Optional)" -f $item.Port, $item.Service) -ForegroundColor DarkGray
                }
            }
        }

        Write-Host "`n[HEALTH CHECK COMPLETE] Overall Status: $(if ($allPassed) { 'READY' } else { 'NEEDS_ATTENTION' })" -ForegroundColor Cyan
    }

    "logs" {
        Set-Location $ProjectRoot
        if ($Service) {
            Write-Host "[LOGS] Showing recent logs for service: $Service..." -ForegroundColor Cyan
            docker compose -f $ComposeFile logs --tail 100 -f $Service
        } else {
            Write-Host "[LOGS] Showing recent logs for all services..." -ForegroundColor Cyan
            docker compose -f $ComposeFile logs --tail 50
        }
    }

    "test" {
        $TestScript = Join-Path $ScriptDir "test.ps1"
        if (Test-Path $TestScript) {
            & powershell.exe -ExecutionPolicy Bypass -File $TestScript
        } else {
            & powershell.exe -ExecutionPolicy Bypass -File (Join-Path $ScriptDir "run_all_tests.ps1")
        }
    }

    "guide" {
        Write-Host @"
======================================================================
 SDNFlowGuard Demonstration & Verification Guide
======================================================================

[OFFICIAL SERVICE ACCESS DIRECTORY]
  - Frontend Operations Dashboard : http://localhost:3000
  - ONOS SDN Controller Web GUI   : http://localhost:8181/onos/ui (onos / rocks)
  - Kibana Telemetry Dashboard    : http://localhost:5601
  - Backend API Documentation     : http://localhost:5000/docs
  - Elasticsearch Cluster REST    : http://localhost:9200 (REST JSON)
  - Logstash Ingestion Pipeline   : http://localhost:18080 (Webhook POST)
  - ONOS OpenFlow Southbound Port : 127.0.0.1:6653 (TCP OpenFlow 1.3 - NOT HTTP)

[SCENARIO A] Standard Operation via Docker Compose (Recommended)
  1. Start the complete 6-container stack (staggered startup):
     .\scripts\manage.ps1 up
     (or .\scripts\manage.ps1 up -SkipKibana to save ~550MB RAM)
  2. Verify all containers are running:
     .\scripts\manage.ps1 status
  3. Access the Web Dashboard:
     .\scripts\manage.ps1 open
     (or .\scripts\manage.ps1 open onos / kibana / docs)

[SCENARIO B] Connecting WSL2 Mininet Virtual Network (Optional Lab)
  1. In WSL2 Ubuntu terminal:
     sudo mn --topo single,3 --controller=remote,ip=127.0.0.1,port=6653 --switch ovsk
  2. In Mininet CLI, test ping:
     mininet> pingall
  3. Observe real-time topology updates in the Web Dashboard at http://localhost:3000
     and in ONOS Web GUI at http://localhost:8181/onos/ui

[SCENARIO C] Memory Optimization & Cache Reclaim (16GB Windows Host)
  1. Reclaim WSL2 buffer/page cache non-destructively:
     .\scripts\manage.ps1 reclaim
  2. Permanent WSL2 memory capping template available at:
     infrastructure\wsl\.wslconfig.recommended

[SCENARIO D] Security Defense Verification (DRY_RUN Default)
  1. Navigate to 'Anomaly Detection' or 'Manual Traffic Control'
  2. Review detected anomalies and staged mitigation policies
  3. Inspect preview flow rules (Safety Gate protects 10.0.0.254 and DNS)
  4. Perform rollback test and observe structured status verification

"@ -ForegroundColor White
    }

    "open" {
        $targetUrl = switch ($Service.ToLower()) {
            "onos"   { "http://localhost:8181/onos/ui" }
            "kibana" { "http://localhost:5601" }
            "docs"   { "http://localhost:5000/docs" }
            "es"     { "http://localhost:9200" }
            default  { "http://localhost:3000" }
        }
        Write-Host "[OPEN] Launching $targetUrl in default web browser..." -ForegroundColor Green
        Start-Process $targetUrl
    }

    "reclaim" {
        $ReclaimScript = Join-Path $ScriptDir "reclaim_wsl_memory.ps1"
        if (Test-Path $ReclaimScript) {
            & powershell.exe -ExecutionPolicy Bypass -File $ReclaimScript
        } else {
            Write-Host "[WARN] reclaim_wsl_memory.ps1 not found." -ForegroundColor Yellow
        }
    }
}

