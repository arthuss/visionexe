param(
    [string]$ModelPath = "",
    [string]$Host = "127.0.0.1",
    [int]$Port = 8090,
    [string]$Device = "auto",
    [string]$Dtype = "auto",
    [int]$OutputDim = 1024,
    [string]$Instruction = "Represent the user's input.",
    [int]$MaxLength = 512,
    [switch]$NoNormalize,
    [string]$VenvPath = "",
    [string]$CondaEnv = "",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ExtraArgs
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path "$PSScriptRoot/../.."
$exevisionRoot = Join-Path $repoRoot "engine/tools/exevision"
$embedScript = Join-Path $exevisionRoot "scripts/run_qwen3_vl_embed.ps1"

if (-not (Test-Path $embedScript)) {
    throw "exevision embed worker not found: $embedScript"
}

if (-not $ModelPath) {
    $ModelPath = $env:QWEN_EMBED_MODEL_PATH
}
if (-not $ModelPath) {
    Write-Host "Model path missing. Use -ModelPath or set QWEN_EMBED_MODEL_PATH." -ForegroundColor Yellow
}

if ($PSBoundParameters.ContainsKey("MaxLength") -or $NoNormalize -or $PSBoundParameters.ContainsKey("VenvPath")) {
    Write-Host "Note: MaxLength/NoNormalize/VenvPath are ignored by the exevision embed worker." -ForegroundColor DarkYellow
}

$psArgs = @(
    "-ModelPath", $ModelPath,
    "-Host", $Host,
    "-Port", $Port,
    "-Device", $Device,
    "-DType", $Dtype,
    "-OutputDim", $OutputDim,
    "-Instruction", $Instruction
)

if ($CondaEnv) {
    $psArgs += @("-CondaEnv", $CondaEnv)
}
if ($ExtraArgs.Count -gt 0) {
    $psArgs += $ExtraArgs
}

powershell -File $embedScript @psArgs
