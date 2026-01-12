param(
  [string]$StoryConfig = "stories/template/config/story_config.json",
  [string]$ControlPath = "stories/template/data/analysis/analysis_orchestrator_control.json",
  [string]$Python = "python"
)

function Resolve-RepoPath {
  param([string]$Path, [string]$RepoRoot)
  if (-not $Path) {
    return $null
  }
  if ([System.IO.Path]::IsPathRooted($Path)) {
    return $Path
  }
  return Join-Path $RepoRoot $Path
}

function Read-JsonFile {
  param([string]$Path)
  if (-not (Test-Path $Path)) {
    return $null
  }
  return Get-Content $Path -Raw | ConvertFrom-Json
}

function Write-JsonFile {
  param([string]$Path, [object]$Payload)
  $json = $Payload | ConvertTo-Json -Depth 8
  $dir = Split-Path $Path -Parent
  if ($dir -and -not (Test-Path $dir)) {
    New-Item -ItemType Directory -Path $dir | Out-Null
  }
  $json | Set-Content -Path $Path -Encoding UTF8
}

function Get-ChapterNumber {
  param([string]$Name)
  $match = [regex]::Match($Name, "\d+")
  if ($match.Success) {
    return [int]$match.Value
  }
  return $null
}

function Get-Chapters {
  param([string]$Root, [string]$Label, [int[]]$Only)
  $prefix = ($Label + "_").ToLower()
  $dirs = Get-ChildItem -Path $Root -Directory | Where-Object { $_.Name.ToLower().StartsWith($prefix) }
  $items = foreach ($dir in $dirs) {
    $num = Get-ChapterNumber -Name $dir.Name
    [PSCustomObject]@{ Name = $dir.Name; Number = $num; Path = $dir.FullName }
  }
  if ($Only -and $Only.Count -gt 0) {
    $items = $items | Where-Object { $_.Number -in $Only }
  }
  return $items | Sort-Object -Property @{Expression = { $_.Number -eq $null } }, @{Expression = { $_.Number } }, @{Expression = { $_.Name } }
}

function Get-Segments {
  param([string]$ChapterDir, [string]$SegmentLabel)
  $prefix = $SegmentLabel + "_"
  return Get-ChildItem -Path $ChapterDir -Directory | Where-Object { $_.Name.StartsWith($prefix) }
}

function Test-StageComplete {
  param([object[]]$Segments, [string]$FileName)
  foreach ($segment in $Segments) {
    $path = Join-Path $segment.FullName $FileName
    if (-not (Test-Path $path)) {
      return $false
    }
    try {
      if ((Get-Item $path).Length -le 0) {
        return $false
      }
    } catch {
      return $false
    }
  }
  return $true
}

function Invoke-Worker {
  param([string]$ScriptPath, [string[]]$Args, [int]$Retries, [int]$DelaySeconds)
  for ($attempt = 0; $attempt -le $Retries; $attempt++) {
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host ("[{0}] --- Running: {1} {2}" -f $timestamp, $ScriptPath, ($Args -join " "))
    & $Python $ScriptPath @Args
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 0) {
      return $true
    }
    Write-Warning ("Worker failed (exit {0})." -f $exitCode)
    if ($attempt -lt $Retries) {
      Start-Sleep -Seconds $DelaySeconds
    }
  }
  return $false
}

function Write-StageStart {
  param([string]$Stage, [object]$Chapter)
  $timestamp = Get-Date -Format "HH:mm:ss"
  if ($Chapter) {
    Write-Host ("[{0}] {1} start -> {2} ({3})" -f $timestamp, $Stage, $Chapter.Name, $Chapter.Path)
  } else {
    Write-Host ("[{0}] {1} start" -f $timestamp, $Stage)
  }
}

$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$storyConfigPath = Resolve-RepoPath -Path $StoryConfig -RepoRoot $repoRoot
$controlPathResolved = Resolve-RepoPath -Path $ControlPath -RepoRoot $repoRoot

$storyConfigData = Read-JsonFile -Path $storyConfigPath
if (-not $storyConfigData) {
  throw "Story config not found: $storyConfigPath"
}

$control = Read-JsonFile -Path $controlPathResolved
if (-not $control) {
  $control = [PSCustomObject]@{
    enabled = $true
    pause = $false
    mode = "chapter-batch"
    use_gemini = $true
    use_vertex = $true
    gemini_model = ""
    vertex_model = ""
    vertex_project = ""
    vertex_location = ""
    force = $true
    poll_seconds = 10
    max_retries = 1
    retry_delay_seconds = 10
    chapters = @()
    carry_location = $true
    include_prev_segment = $true
    prev_context_chars = 2000
    wait_analysis_layers = $false
  }
  Write-JsonFile -Path $controlPathResolved -Payload $control
  Write-Host "Created control file: $controlPathResolved"
}

$filmsetsRoot = Resolve-RepoPath -Path $storyConfigData.filmsets_root -RepoRoot $repoRoot
$chapterLabel = $storyConfigData.chapter_label
$segmentLabel = $storyConfigData.segment_label

if (-not $storyConfigData.filmsets_root) {
  throw "filmsets_root missing in story config: $storyConfigPath"
}

if (-not $filmsetsRoot) {
  throw "filmsets_root could not be resolved: $($storyConfigData.filmsets_root)"
}

if (-not (Test-Path $filmsetsRoot)) {
  throw "Filmsets root not found: $filmsetsRoot"
}

Write-Host ("Filmsets root: {0}" -f $filmsetsRoot)
Write-Host ("Control file: {0}" -f $controlPathResolved)

while ($true) {
  $control = Read-JsonFile -Path $controlPathResolved
  if (-not $control.enabled -or $control.pause) {
    Start-Sleep -Seconds $control.poll_seconds
    continue
  }

  $chapters = Get-Chapters -Root $filmsetsRoot -Label $chapterLabel -Only $control.chapters
  $didWork = $false

  foreach ($chapter in $chapters) {
    $segments = Get-Segments -ChapterDir $chapter.Path -SegmentLabel $segmentLabel
    if (-not $segments -or $segments.Count -eq 0) {
      continue
    }

    $needG = -not (Test-StageComplete -Segments $segments -FileName "analysis_llm_graphematic.txt")
    if ($needG) {
      Write-StageStart -Stage "Graphematic worker" -Chapter $chapter
      $args = @($chapter.Number, "--chapter-batch")
      if ($control.use_vertex) {
        $args += "--use-vertex"
        $vertexModel = $control.vertex_model
        if (-not $vertexModel -and $control.gemini_model) { $vertexModel = $control.gemini_model }
        if ($vertexModel) { $args += @("--vertex-model", $vertexModel) }
        if ($control.vertex_project) { $args += @("--vertex-project", $control.vertex_project) }
        if ($control.vertex_location) { $args += @("--vertex-location", $control.vertex_location) }
      } elseif ($control.use_gemini) {
        $args += "--use-gemini"
        if ($control.gemini_model) { $args += @("--model", $control.gemini_model) }
      }
      if ($control.force) { $args += "--force" }
      $didWork = Invoke-Worker -ScriptPath "engine/workers/worker_llm_analysis_graphematic.py" -Args $args -Retries $control.max_retries -DelaySeconds $control.retry_delay_seconds
      break
    }

    $needM = -not (Test-StageComplete -Segments $segments -FileName "analysis_llm_morphologic.txt")
    if ($needM) {
      Write-StageStart -Stage "Morphologic worker" -Chapter $chapter
      $args = @($chapter.Number, "--chapter-batch")
      if ($control.use_vertex) {
        $args += "--use-vertex"
        $vertexModel = $control.vertex_model
        if (-not $vertexModel -and $control.gemini_model) { $vertexModel = $control.gemini_model }
        if ($vertexModel) { $args += @("--vertex-model", $vertexModel) }
        if ($control.vertex_project) { $args += @("--vertex-project", $control.vertex_project) }
        if ($control.vertex_location) { $args += @("--vertex-location", $control.vertex_location) }
      } elseif ($control.use_gemini) {
        $args += "--use-gemini"
        if ($control.gemini_model) { $args += @("--model", $control.gemini_model) }
      }
      if ($control.force) { $args += "--force" }
      $didWork = Invoke-Worker -ScriptPath "engine/workers/worker_llm_analysis_Morphologic.py" -Args $args -Retries $control.max_retries -DelaySeconds $control.retry_delay_seconds
      break
    }

    $needS = -not (Test-StageComplete -Segments $segments -FileName "analysis_llm_synthactic.txt")
    if ($needS) {
      Write-StageStart -Stage "Syntactic worker" -Chapter $chapter
      $args = @($chapter.Number, "--chapter-batch")
      if ($control.use_vertex) {
        $args += "--use-vertex"
        $vertexModel = $control.vertex_model
        if (-not $vertexModel -and $control.gemini_model) { $vertexModel = $control.gemini_model }
        if ($vertexModel) { $args += @("--vertex-model", $vertexModel) }
        if ($control.vertex_project) { $args += @("--vertex-project", $control.vertex_project) }
        if ($control.vertex_location) { $args += @("--vertex-location", $control.vertex_location) }
      } elseif ($control.use_gemini) {
        $args += "--use-gemini"
        if ($control.gemini_model) { $args += @("--model", $control.gemini_model) }
      }
      if ($control.force) { $args += "--force" }
      $didWork = Invoke-Worker -ScriptPath "engine/workers/worker_llm_analysis_synthactic.py" -Args $args -Retries $control.max_retries -DelaySeconds $control.retry_delay_seconds
      break
    }

    $needH = -not (Test-StageComplete -Segments $segments -FileName "analysis_llm_semantic_historical.txt")
    if ($needH) {
      Write-StageStart -Stage "Semantic-historical worker" -Chapter $chapter
      $args = @($chapter.Number, "--chapter-batch")
      if ($control.use_vertex) {
        $args += "--use-vertex"
        $vertexModel = $control.vertex_model
        if (-not $vertexModel -and $control.gemini_model) { $vertexModel = $control.gemini_model }
        if ($vertexModel) { $args += @("--vertex-model", $vertexModel) }
        if ($control.vertex_project) { $args += @("--vertex-project", $control.vertex_project) }
        if ($control.vertex_location) { $args += @("--vertex-location", $control.vertex_location) }
      } elseif ($control.use_gemini) {
        $args += "--use-gemini"
        if ($control.gemini_model) { $args += @("--model", $control.gemini_model) }
      }
      if ($control.force) { $args += "--force" }
      $didWork = Invoke-Worker -ScriptPath "engine/workers/worker_llm_analysis_semantic-historical.py" -Args $args -Retries $control.max_retries -DelaySeconds $control.retry_delay_seconds
      break
    }

    $needLlm = -not (Test-StageComplete -Segments $segments -FileName "analysis_llm.txt")
    if ($needLlm) {
      Write-StageStart -Stage "Final analysis worker" -Chapter $chapter
      $args = @($chapter.Number, "--per-segment")
      if ($control.use_vertex) {
        $args += "--use-vertex"
        $vertexModel = $control.vertex_model
        if (-not $vertexModel -and $control.gemini_model) { $vertexModel = $control.gemini_model }
        if ($vertexModel) { $args += @("--vertex-model", $vertexModel) }
        if ($control.vertex_project) { $args += @("--vertex-project", $control.vertex_project) }
        if ($control.vertex_location) { $args += @("--vertex-location", $control.vertex_location) }
      } elseif ($control.use_gemini) {
        $args += "--use-gemini"
        if ($control.gemini_model) { $args += @("--model", $control.gemini_model) }
      }
      if ($control.force) { $args += "--force" }
      if ($control.wait_analysis_layers) { $args += "--wait-analysis-layers" }
      if ($control.carry_location) { $args += "--carry-location" }
      if ($control.include_prev_segment) { $args += "--include-prev-segment" }
      if ($control.prev_context_chars) { $args += @("--prev-context-chars", $control.prev_context_chars) }
      $didWork = Invoke-Worker -ScriptPath "engine/workers/worker_llm_analysis.py" -Args $args -Retries $control.max_retries -DelaySeconds $control.retry_delay_seconds
      break
    }
  }

  if (-not $didWork) {
    Start-Sleep -Seconds $control.poll_seconds
  }
}
