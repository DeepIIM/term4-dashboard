# Creates a Windows scheduled task to run the daily course reminder at 21:00 IST.
# Run this script as Administrator.

$ErrorActionPreference = "Stop"

# Resolve paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runnerScript = Resolve-Path (Join-Path $scriptDir "run_reminder_local.ps1")
$taskName = "Term4DailyReminder"

# Check for admin privileges
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Please run this script as Administrator (right-click PowerShell -> Run as administrator)."
    exit 1
}

# Remove existing task if present
$existing = schtasks /Query /TN $taskName 2>$null
if ($existing) {
    Write-Host "Removing existing task '$taskName'..."
    schtasks /Delete /TN $taskName /F | Out-Null
}

# Create the task to run daily at 21:00
# /SC DAILY /ST 21:00 uses the local system timezone. If your PC is set to IST, this is 21:00 IST.
$action = "powershell.exe -ExecutionPolicy Bypass -File `"$runnerScript`""
Write-Host "Creating scheduled task '$taskName'..."
schtasks /Create `
    /TN $taskName `
    /TR "$action" `
    /SC DAILY `
    /ST 21:00 `
    /RL HIGHEST `
    /F | Out-Null

Write-Host "Done. Task '$taskName' will run daily at 21:00 local system time."
Write-Host "Verify in Task Scheduler, or run the following to test now:"
Write-Host "  .\scripts\run_reminder_local.ps1"
