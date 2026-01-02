param(
    [Parameter(Mandatory = $true)]
    [string]$Chapter,
    [Parameter(Mandatory = $true)]
    [string]$Timeline,
    [ValidateSet("image", "video", "all")]
    [string]$Type = "image",
    [string]$Source = "$PSScriptRoot\\produced_assets",
    [bool]$ByScene = $true,
    [string]$ComfyUrl = "http://127.0.0.1:8188",
    [switch]$SkipGenerate,
    [switch]$SkipDistribute,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = (Get-Command python -ErrorAction Stop).Source

if (-not $SkipGenerate) {
    try {
        $uri = [uri]$ComfyUrl
        $port = if ($uri.Port -gt 0) { $uri.Port } else { 8188 }
        $conn = Test-NetConnection -ComputerName $uri.Host -Port $port -WarningAction SilentlyContinue
        if (-not $conn.TcpTestSucceeded) {
            Write-Host "ComfyUI not reachable at $ComfyUrl. Start ComfyUI or adjust --ComfyUrl." -ForegroundColor Yellow
            exit 1
        }
    } catch {
        Write-Host "ComfyUI check failed: $($_.Exception.Message)" -ForegroundColor Yellow
        exit 1
    }

    $genArgs = @(
        Join-Path $root "generate_chapter_assets.py",
        "--chapter", $Chapter,
        "--type", $Type,
        "--timeline", $Timeline
    )
    if ($DryRun) { $genArgs += "--dry-run" }
    & $python @genArgs
}

if (-not $SkipDistribute) {
    $distArgs = @(
        Join-Path $root "distribute_chapter_assets.py",
        "--source", $Source,
        "--chapter", $Chapter,
        "--type", $Type,
        "--timeline", $Timeline
    )
    if ($ByScene) { $distArgs += "--by-scene" }
    if ($DryRun) { $distArgs += "--dry-run" }
    & $python @distArgs
}
