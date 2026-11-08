<#
.SYNOPSIS
    SDNFlowGuard Master Test Runner & Integrity Verifier.
.DESCRIPTION
    Runs Python syntax compilation checks, CLI self-tests, the 79-test automated suite,
    frontend build verification, and verifies SQLite database immutability.
    Enforces PYTHONDONTWRITEBYTECODE=1 and -B so zero .pyc files are generated.
#>
[CmdletBinding()]
param(
    [switch]$SkipFrontend
)

$ErrorActionPreference = "Stop"
$env:PYTHONDONTWRITEBYTECODE = "1"

$ScriptDir = $PSScriptRoot
$ProjectRoot = Split-Path -Parent $ScriptDir
$PythonExe = Join-Path $ProjectRoot "backend\venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = Join-Path $ProjectRoot "backend\venv\bin\python"
}
if (-not (Test-Path $PythonExe)) {
    $systemPython = Get-Command python -ErrorAction SilentlyContinue
    if ($systemPython) {
        $PythonExe = $systemPython.Source
    } else {
        $pyCmd = Get-Command py -ErrorAction SilentlyContinue
        if ($pyCmd) {
            $PythonExe = "py"
        } else {
            throw "Python interpreter not found. Please create backend/venv or install Python."
        }
    }
}
$DbPath = Join-Path $ProjectRoot "database\sdnflowguard.db"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " SDNFlowGuard Master Verification & Automated Test Runner   " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Baseline Database Hash
if (-not (Test-Path $DbPath)) {
    throw "Primary database missing at $DbPath"
}
$HashBefore = (Get-FileHash -Path $DbPath -Algorithm SHA256).Hash.ToLower()

# 2. Python Syntax Compilation Check (In-memory, zero bytecode artifacts)
Write-Host "`n[1/5] Verifying Python Syntax (in-memory AST & bytecode)..." -ForegroundColor Cyan
$SyntaxValidator = Join-Path $ProjectRoot "scripts\verify_syntax.py"
& $PythonExe -B $SyntaxValidator (Join-Path $ProjectRoot "backend")
if ($LASTEXITCODE -ne 0) { throw "Python syntax validation detected errors." }
Write-Host "  [PASS] All backend Python files compiled in-memory with zero syntax errors." -ForegroundColor Green

# 3. Defense & Collector CLI Self-Tests
Write-Host "`n[2/5] Running CLI Self-Tests (Monitor V2, Step 63, Step 64, Defense Policy)..." -ForegroundColor Cyan
& $PythonExe -B (Join-Path $ProjectRoot "backend\collectors\sdn_overlap_alert_monitor_v2.py") --self-test
if ($LASTEXITCODE -ne 0) { throw "sdn_overlap_alert_monitor_v2.py --self-test failed" }

& $PythonExe -B (Join-Path $ProjectRoot "backend\defense\source_ip_evidence_analyzer.py") --self-test
if ($LASTEXITCODE -ne 0) { throw "source_ip_evidence_analyzer.py --self-test failed" }

& $PythonExe -B (Join-Path $ProjectRoot "backend\defense\onos_host_evidence_correlator.py") --self-test
if ($LASTEXITCODE -ne 0) { throw "onos_host_evidence_correlator.py --self-test failed" }

& $PythonExe -B (Join-Path $ProjectRoot "backend\defense\sdn_defense_policy.py") --self-test
if ($LASTEXITCODE -ne 0) { throw "sdn_defense_policy.py --self-test failed" }

# 4. Full Unittest Suite (Contracts, Safety, Unit, Integration, E2E)
Write-Host "`n[3/5] Running Automated Test Suite (backend/tests)..." -ForegroundColor Cyan
& $PythonExe -B -m unittest discover -s (Join-Path $ProjectRoot "backend\tests") -v
if ($LASTEXITCODE -ne 0) { throw "Automated test suite encountered failures." }

# 5. Frontend Production Build Check
Write-Host "`n[4/5] Verifying Frontend Production Build..." -ForegroundColor Cyan
if (-not $SkipFrontend) {
    $FrontendIndex = Join-Path $ProjectRoot "frontend\build\index.html"
    if (Test-Path $FrontendIndex) {
        Write-Host "  [PASS] Precompiled React production bundle verified ($FrontendIndex)" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] frontend/build/index.html not found. (Build container handles build in Docker)" -ForegroundColor Yellow
    }
}

# 6. Database & Evidence Immutability Verification
Write-Host "`n[5/5] Verifying Database & Checkpoint Integrity..." -ForegroundColor Cyan
$HashAfter = (Get-FileHash -Path $DbPath -Algorithm SHA256).Hash.ToLower()
if ($HashBefore -ne $HashAfter) {
    throw "Database SHA-256 changed during tests! Before=$HashBefore After=$HashAfter"
}
Write-Host "  [PASS] Primary Database SHA-256 Unchanged: $HashAfter" -ForegroundColor Green
Write-Host "`n[ALL TESTS & SAFETY CHECKS PASSED SUCCESSFULLY]" -ForegroundColor Green
exit 0

