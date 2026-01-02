# Exeget:OS Scout Deck Launcher V2
$Port = 8001
$ServerScript = Join-Path $PSScriptRoot "server.py"

Write-Host "--- INITIALIZING SCOUT DECK V7 (MISSION PLANNER) ---" -ForegroundColor Cyan

# Cleanup old processes
$Connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($Connections) {
    Write-Host "Cleaning up port $Port..." -ForegroundColor Yellow
    foreach ($conn in $Connections) {
        $pid_to_kill = $conn.OwningProcess
        if ($pid_to_kill -gt 0) {
            try {
                Stop-Process -Id $pid_to_kill -Force -ErrorAction SilentlyContinue
                Write-Host "Stopped process $pid_to_kill" -ForegroundColor DarkGray
            } catch {
                Write-Host "Could not stop process $pid_to_kill" -ForegroundColor Red
            }
        }
    }
}

# Start Custom Python Server
Write-Host "Starting Exeget Server..." -ForegroundColor Green
Start-Process python -ArgumentList $ServerScript -WorkingDirectory $PSScriptRoot -WindowStyle Minimized

# Wait for server to be up
Start-Sleep -Seconds 2

# Open Browser
Start-Process "http://localhost:$Port/index.html"
Write-Host "System active. Editor Mode Enabled." -ForegroundColor Cyan