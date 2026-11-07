<#
.SYNOPSIS
    Safely reclaims unused buffer/page cache from WSL2 and Docker VM without restarting.
.DESCRIPTION
    Executes sync and drop_caches inside WSL2 to release cached disk pages back to Windows,
    leaving active processes, ONOS OpenFlow connections, and Mininet intact.
#>
[CmdletBinding()]
param()

Write-Host "Reclaiming WSL2 buffer/page cache safely..." -ForegroundColor Cyan
wsl -d Ubuntu-26.04 -u root bash -c "sync; echo 3 > /proc/sys/vm/drop_caches; free -m"
$os = Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory
$freeMb = [math]::Round($os.FreePhysicalMemory / 1024, 2)
Write-Host "Windows Host Free Physical Memory: $freeMb MB" -ForegroundColor Green
