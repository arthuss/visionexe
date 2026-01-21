param(
    [string]$ModelPath = "..\\Models\\Qwen3-VL-Reranker-2B",
    [string]$Host = "127.0.0.1",
    [int]$Port = 8091,
    [string]$Device = "auto",
    [string]$DType = "auto",
    [string]$Instruction = "Retrieve images or text relevant to the user's query.",
    [string]$AttnImpl = "",
    [string]$CondaEnv = "",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ExtraArgs
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not available. Install Python 3.11+."
    exit 1
}

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Push-Location $root

$pyArgs = @(
    "-m", "model_workers.qwen3_vl_service",
    "--mode", "rerank",
    "--model-path", $ModelPath,
    "--host", $Host,
    "--port", $Port,
    "--device", $Device,
    "--dtype", $DType,
    "--rerank-instruction", $Instruction
)

if ($AttnImpl) {
    $pyArgs += "--attn-impl"
    $pyArgs += $AttnImpl
}

if ($ExtraArgs.Count -gt 0) {
    $pyArgs += $ExtraArgs
}

if ($CondaEnv) {
    if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
        Write-Host "conda is not available. Activate the env manually or install conda."
        Pop-Location
        exit 1
    }
    conda run -n $CondaEnv python @pyArgs
} else {
    python @pyArgs
}

Pop-Location
