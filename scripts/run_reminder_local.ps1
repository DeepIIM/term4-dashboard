# Run the daily course reminder using the local .env file.
# This is used by Windows Task Scheduler for exact 21:00 IST delivery.

$ErrorActionPreference = "Stop"

# Resolve paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Resolve-Path (Join-Path $scriptDir "..")
$envFile = Join-Path $projectDir ".env"
$pythonScript = Join-Path $projectDir "scripts\send_reminder.py"

# Check .env exists
if (-not (Test-Path $envFile)) {
    Write-Error "Missing .env file. Please copy .env.example to .env and fill in your values."
    exit 1
}

# Load .env into process environment variables
Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if ([string]::IsNullOrWhiteSpace($line)) { return }
    if ($line.StartsWith("#")) { return }
    $idx = $line.IndexOf("=")
    if ($idx -lt 0) { return }
    $name = $line.Substring(0, $idx).Trim()
    $value = $line.Substring($idx + 1).Trim()
    [Environment]::SetEnvironmentVariable($name, $value, "Process")
}

# Validate required variables
$required = @("RESEND_API_KEY", "EMAIL_TO")
foreach ($var in $required) {
    if (-not [Environment]::GetEnvironmentVariable($var, "Process")) {
        Write-Error "Missing required environment variable: $var (check your .env file)"
        exit 1
    }
}

# Run the Python script
Set-Location $projectDir
python "$pythonScript"
