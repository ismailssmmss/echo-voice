param(
    [switch]$AllowLan
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker Desktop with Docker Compose v2 is required. Install/start Docker Desktop, then run this script again."
}

& docker info *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker is installed but the Docker Engine is not running. Start Docker Desktop and retry."
}

$envPath = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path -LiteralPath $envPath)) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot ".env.example") -Destination $envPath
    Write-Host "Created .env from .env.example."
}

$script:envLines = @(Get-Content -LiteralPath $envPath)

function Get-EnvValue([string]$Name) {
    $prefix = "$Name="
    foreach ($line in $script:envLines) {
        if ($line.StartsWith($prefix, [System.StringComparison]::Ordinal)) {
            return $line.Substring($prefix.Length)
        }
    }
    return $null
}

function Set-EnvValue([string]$Name, [string]$Value) {
    $prefix = "$Name="
    $found = $false
    for ($i = 0; $i -lt $script:envLines.Count; $i++) {
        if ($script:envLines[$i].StartsWith($prefix, [System.StringComparison]::Ordinal)) {
            $script:envLines[$i] = "$Name=$Value"
            $found = $true
        }
    }
    if (-not $found) {
        $script:envLines += "$Name=$Value"
    }
}

function New-RandomSecret {
    $bytes = New-Object byte[] 48
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $rng.GetBytes($bytes)
    }
    finally {
        $rng.Dispose()
    }
    return [Convert]::ToBase64String($bytes).TrimEnd("=").Replace("+", "-").Replace("/", "_")
}

foreach ($name in @("POSTGRES_PASSWORD", "SECRET_KEY", "WORKER_API_TOKEN")) {
    $value = Get-EnvValue $name
    if ([string]::IsNullOrWhiteSpace($value) -or $value -match "replace-with|local-only|change-before-production|not-for-production") {
        Set-EnvValue $name (New-RandomSecret)
        Write-Host "Generated a unique local value for $name."
    }
}

if ($AllowLan) {
    Set-EnvValue "ECHO_BIND_HOST" "0.0.0.0"
    Write-Warning "LAN mode exposes the API on all local interfaces. Use only on a trusted private network; do not port-forward it to the public internet."
}
else {
    Set-EnvValue "ECHO_BIND_HOST" "127.0.0.1"
}

[System.IO.File]::WriteAllLines($envPath, [string[]]$script:envLines, [System.Text.UTF8Encoding]::new($false))

Write-Host "Building and starting Echo Voice services. The first build can be large."
& docker compose --env-file ".env" up --build -d
if ($LASTEXITCODE -ne 0) {
    & docker compose logs --tail 100 backend ai-worker
    throw "Docker Compose could not start. Review the logs above."
}

$apiReady = $false
for ($attempt = 0; $attempt -lt 60; $attempt++) {
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health" -TimeoutSec 3
        if ($health.status -eq "ok") {
            $apiReady = $true
            break
        }
    }
    catch {
        Start-Sleep -Seconds 2
    }
}

if (-not $apiReady) {
    & docker compose logs --tail 120 backend ai-worker
    throw "The containers started but the API did not become healthy. Review the logs above."
}

Write-Host ""
Write-Host "Echo Voice API is responding: http://127.0.0.1:8000/api/v1/health"
Write-Host "API documentation:            http://127.0.0.1:8000/docs"
Write-Host "Worker health (internal test): http://127.0.0.1:8001/health"
Write-Host ""
Write-Host "Android emulator URL: http://10.0.2.2:8000/api/v1"

if ($AllowLan) {
    $ips = @(Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object {
            $_.IPAddress -notlike "127.*" -and
            $_.IPAddress -notlike "169.254.*" -and
            $_.InterfaceAlias -notmatch "Loopback|vEthernet|WSL|Docker"
        } |
        Select-Object -ExpandProperty IPAddress -Unique)
    if ($ips.Count -gt 0) {
        Write-Host "Candidate local addresses for a phone on the same Wi-Fi:"
        foreach ($ip in $ips) {
            Write-Host ("  http://" + $ip + ":8000/api/v1")
        }
    }
    Write-Host "Allow TCP port 8000 in Windows Firewall only for your trusted private network if needed."
}
else {
    Write-Host "For a physical phone on trusted Wi-Fi, rerun with: powershell -ExecutionPolicy Bypass -File .\start-echo-voice.ps1 -AllowLan"
}

Write-Host ""
Write-Host "First synthesis downloads the SILMA TTS model and vocoder and may take several minutes."
Write-Host "In the app, enter the API URL on the login screen, tap 'حفظ العنوان وفحص الاتصال', then sign in."
Write-Host "Use only your own voice or a voice you have explicit permission to use."
