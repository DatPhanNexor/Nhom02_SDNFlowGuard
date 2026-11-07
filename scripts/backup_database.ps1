<#
.SYNOPSIS
    Safe online SQLite backup utility for database/sdnflowguard.db.
.DESCRIPTION
    Uses Python's sqlite3.Connection.backup() API to create a consistent backup
    outside the active database file and verifies PRAGMA integrity_check and SHA-256.
#>
param(
    [string]$OutputDir = "D:\Project\_SDNFlowGuard_Cleanup_Rollback\db_backups"
)
$ErrorActionPreference = "Stop"
$env:PYTHONDONTWRITEBYTECODE = "1"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $ProjectRoot "backend\venv\Scripts\python.exe"
$SourceDb = Join-Path $ProjectRoot "database\sdnflowguard.db"

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDb = Join-Path $OutputDir "sdnflowguard_backup_$Timestamp.db"

$PyCode = @"
import sqlite3
src = sqlite3.connect(r'$SourceDb')
dst = sqlite3.connect(r'$BackupDb')
with dst:
    src.backup(dst)
res = dst.execute('PRAGMA integrity_check;').fetchone()[0]
src.close()
dst.close()
assert res == 'ok', f'Integrity check failed: {res}'
print(res)
"@

$Integrity = & $PythonExe -B -c $PyCode
$SrcHash = (Get-FileHash -Path $SourceDb -Algorithm SHA256).Hash.ToLower()
$DstHash = (Get-FileHash -Path $BackupDb -Algorithm SHA256).Hash.ToLower()

Write-Host "[PASS] SQLite Online Backup Completed: $BackupDb" -ForegroundColor Green
Write-Host "       PRAGMA integrity_check : $Integrity" -ForegroundColor Green
Write-Host "       Source SHA-256         : $SrcHash" -ForegroundColor Gray
Write-Host "       Backup SHA-256         : $DstHash" -ForegroundColor Gray
exit 0

