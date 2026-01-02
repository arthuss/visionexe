param(
  [string]$StoryRoot = ""
)

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$engineRoot = Split-Path -Parent $scriptRoot
$repoRoot = Split-Path -Parent $engineRoot
$engineConfigPath = Join-Path $engineRoot "config\\engine_config.json"

if (-not (Test-Path $engineConfigPath)) {
  Write-Host "Missing engine_config.json at $engineConfigPath"
  exit 1
}

$engineConfig = Get-Content $engineConfigPath | ConvertFrom-Json
if ([string]::IsNullOrWhiteSpace($StoryRoot)) {
  $StoryRoot = $engineConfig.default_story_root
}

$storyRootPath = Join-Path $repoRoot $StoryRoot
$storyConfigPath = Join-Path $storyRootPath "config\\story_config.json"
if (-not (Test-Path $storyConfigPath)) {
  Write-Host "Missing story_config.json at $storyConfigPath"
  exit 1
}

$storyConfig = Get-Content $storyConfigPath | ConvertFrom-Json
$subjectsRoot = Join-Path $repoRoot $storyConfig.subjects_root

if (-not (Test-Path $subjectsRoot)) {
  Write-Host "Subjects folder not found: $subjectsRoot"
  exit 1
}

$port = 8123
$url = "http://127.0.0.1:$port/subjects/index.html"

Write-Host "Serving $storyRootPath on $url"
Start-Process $url | Out-Null

python -m http.server $port --directory $storyRootPath
