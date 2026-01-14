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

function Write-Log {
  param([string]$Message)
  $timestamp = Get-Date -Format "HH:mm:ss"
  Write-Host ("[{0}] {1}" -f $timestamp, $Message)
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

function Get-SegmentIndex {
  param([string]$Name, [string]$SegmentLabel)
  $pattern = "^" + [regex]::Escape($SegmentLabel) + "_(\\d+)$"
  $match = [regex]::Match($Name, $pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
  if ($match.Success) {
    return [int]$match.Groups[1].Value
  }
  return $null
}

function Resolve-VersePath {
  param([string]$VerseRoot, [int]$ChapterNumber)
  $candidates = @(
    ("chapter_{0:D2}.txt" -f $ChapterNumber),
    ("chapter_{0:D3}.txt" -f $ChapterNumber)
  )
  foreach ($name in $candidates) {
    $path = Join-Path $VerseRoot $name
    if (Test-Path $path) {
      return $path
    }
  }
  return $null
}

function Load-VerseOverrides {
  param([string]$VerseRoot)
  $overrides = @{}
  if (-not $VerseRoot) { return $overrides }
  $path = Join-Path $VerseRoot "verse_overrides.json"
  if (-not (Test-Path $path)) { return $overrides }
  $data = Read-JsonFile -Path $path
  if (-not $data) { return $overrides }
  if ($data.PSObject.Properties.Name -contains "max_verse_by_chapter") {
    foreach ($entry in $data.max_verse_by_chapter.PSObject.Properties) {
      $chapter = $null
      $maxVerse = $null
      try { $chapter = [int]$entry.Name } catch { $chapter = $null }
      try { $maxVerse = [int]$entry.Value } catch { $maxVerse = $null }
      if ($chapter -and $maxVerse) {
        $overrides[$chapter] = $maxVerse
      }
    }
  }
  return $overrides
}

function Get-ExpectedVerseMax {
  param([string]$VerseRoot, [int]$ChapterNumber, [hashtable]$Overrides)
  if (-not $VerseRoot) { return $null }
  $versePath = Resolve-VersePath -VerseRoot $VerseRoot -ChapterNumber $ChapterNumber
  if (-not $versePath) { return $null }
  $maxVerse = 0
  foreach ($line in (Get-Content $versePath -Encoding UTF8)) {
    if ($line -match "^\s*\d+\s*:\s*(\d+)\s+") {
      $verse = [int]$Matches[1]
      if ($verse -gt $maxVerse) { $maxVerse = $verse }
    }
  }
  if ($Overrides -and $Overrides.ContainsKey($ChapterNumber)) {
    $maxVerse = [int]$Overrides[$ChapterNumber]
  }
  if ($maxVerse -le 0) { return $null }
  return $maxVerse
}

function Get-MissingSegmentIndices {
  param([object[]]$Segments, [string]$SegmentLabel, [int]$ExpectedMax)
  if (-not $Segments -or -not $ExpectedMax) { return @() }
  $indices = @()
  foreach ($segment in $Segments) {
    $index = Get-SegmentIndex -Name $segment.Name -SegmentLabel $SegmentLabel
    if ($index) { $indices += $index }
  }
  if (-not $indices -or $indices.Count -eq 0) { return @() }
  $missing = @()
  for ($i = 1; $i -le $ExpectedMax; $i++) {
    if ($indices -notcontains $i) {
      $missing += $i
    }
  }
  return $missing
}
function Get-MissingCount {
  param([object[]]$Segments, [string]$FileName)
  $missing = 0
  foreach ($segment in $Segments) {
    $path = Join-Path $segment.FullName $FileName
    if (-not (Test-Path $path)) {
      $missing += 1
      continue
    }
    try {
      if ((Get-Item $path).Length -le 0) {
        $missing += 1
      }
    } catch {
      $missing += 1
    }
  }
  return $missing
}

function Get-StageMissingCount {
  param(
    [string]$AnalysisScope,
    [string]$ChapterDir,
    [object[]]$Segments,
    [string]$FileName
  )
  if ($AnalysisScope -eq "chapter") {
    $chapterPath = Join-Path $ChapterDir $FileName
    if (Test-Path $chapterPath) {
      return 0
    }
    return ($Segments.Count)
  }
  return Get-MissingCount -Segments $Segments -FileName $FileName
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

function Invoke-SelfHeal {
  param(
    [int]$ChapterNumber,
    [string]$StoryConfigPath,
    [string]$VerseRoot,
    [string]$RepoRoot,
    [string]$PythonExe
  )
  $args = @(
    "engine/workers/segment_self_healer.py",
    "--story-config",
    $StoryConfigPath,
    "--verse-root",
    $VerseRoot,
    "--chapters",
    $ChapterNumber
  )
  Write-Log ("Self-heal start -> chapter {0}" -f $ChapterNumber)
  & $PythonExe @args
  Write-Log ("Self-heal done -> chapter {0}" -f $ChapterNumber)
}

function Build-WorkerArgs {
  param([string]$Stage, [object]$Chapter, [object]$Control)
  $analysisScope = Get-ControlValue -Control $Control -Name "analysis_scope" -Default "chapter-batch"
  if ($analysisScope) { $analysisScope = $analysisScope.ToString().ToLower() }
  $args = @($Chapter.Number)
  $lUsesPerSegment = $false
  switch ($analysisScope) {
    "segment" {
      if ($Stage -eq "L") {
        $args += "--per-segment"
        $lUsesPerSegment = $true
      }
    }
    "chapter-batch" {
      if ($Stage -ne "L") {
        $args += "--chapter-batch"
      } else {
        $args += "--per-segment"
        $lUsesPerSegment = $true
      }
    }
    "chapter" {
      if ($Stage -ne "L") {
        $args += "--per-segment"
      }
    }
    default {
      if ($Stage -ne "L") {
        $args += "--chapter-batch"
      } else {
        $args += "--per-segment"
        $lUsesPerSegment = $true
      }
    }
  }

  if ($Control.use_vertex) {
    $args += "--use-vertex"
    $vertexModel = $Control.vertex_model
    if (-not $vertexModel -and $Control.gemini_model) { $vertexModel = $Control.gemini_model }
    if ($vertexModel) { $args += @("--vertex-model", $vertexModel) }
    if ($Control.vertex_project) { $args += @("--vertex-project", $Control.vertex_project) }
    if ($Control.vertex_location) { $args += @("--vertex-location", $Control.vertex_location) }
  } elseif ($Control.use_gemini) {
    $args += "--use-gemini"
    if ($Control.gemini_model) { $args += @("--model", $Control.gemini_model) }
  }

  if ($Control.force) { $args += "--force" }
  if ($Stage -eq "L" -and $lUsesPerSegment) {
    if ($Control.wait_analysis_layers) { $args += "--wait-analysis-layers" }
    if ($Control.carry_location) { $args += "--carry-location" }
    if ($Control.include_prev_segment) { $args += "--include-prev-segment" }
    if ($Control.prev_context_chars) { $args += @("--prev-context-chars", $Control.prev_context_chars) }
  }

  return $args
}

function Get-StageScript {
  param([string]$Stage)
  switch ($Stage) {
    "G" { return "engine/workers/worker_llm_analysis_graphematic.py" }
    "M" { return "engine/workers/worker_llm_analysis_Morphologic.py" }
    "S" { return "engine/workers/worker_llm_analysis_synthactic.py" }
    "H" { return "engine/workers/worker_llm_analysis_semantic-historical.py" }
    "L" { return "engine/workers/worker_llm_analysis.py" }
  }
  return $null
}

function Get-StageFileName {
  param([string]$Stage)
  switch ($Stage) {
    "G" { return "analysis_llm_graphematic.txt" }
    "M" { return "analysis_llm_morphologic.txt" }
    "S" { return "analysis_llm_synthactic.txt" }
    "H" { return "analysis_llm_semantic_historical.txt" }
    "L" { return "analysis_llm.txt" }
  }
  return $null
}

function Start-WorkerJob {
  param([string]$Stage, [object]$Chapter, [object]$Control, [string]$RepoRoot, [string]$LogRoot)
  $scriptPath = Get-StageScript -Stage $Stage
  if (-not $scriptPath) { return $null }
  $args = Build-WorkerArgs -Stage $Stage -Chapter $Chapter -Control $Control
  Write-StageStart -Stage (Get-StageLabel -Stage $Stage) -Chapter $Chapter
  $timestamp = Get-Date -Format "HH:mm:ss"
  Write-Host ("[{0}] --- Running: {1} {2}" -f $timestamp, $scriptPath, ($args -join " "))
  $logPath = $null
  if ($LogRoot) {
    if (-not (Test-Path $LogRoot)) {
      New-Item -ItemType Directory -Path $LogRoot -Force | Out-Null
    }
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $logFile = "{0}_{1}_{2}.log" -f $Stage, $Chapter.Name, $stamp
    $logPath = Join-Path $LogRoot $logFile
    Write-Host ("[{0}] --- Log: {1}" -f $timestamp, $logPath)
  }
  $job = Start-Job -ScriptBlock {
    param($PythonExe, $Script, $ArgList, $WorkingRoot, $LogPath)
    Set-Location $WorkingRoot
    if ($LogPath) {
      $logDir = Split-Path $LogPath -Parent
      if ($logDir -and -not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
      }
      $startLine = "[{0}] START {1} {2}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Script, ($ArgList -join " ")
      $startLine | Out-File -FilePath $LogPath -Append -Encoding UTF8
      & $PythonExe $Script @ArgList *>&1 | Out-File -FilePath $LogPath -Append -Encoding UTF8
      $exitCode = $LASTEXITCODE
      $endLine = "[{0}] EXIT {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $exitCode
      $endLine | Out-File -FilePath $LogPath -Append -Encoding UTF8
      exit $exitCode
    }
    & $PythonExe $Script @ArgList
    exit $LASTEXITCODE
  } -ArgumentList $Python, $scriptPath, $args, $RepoRoot, $logPath
  return $job
}

function Get-StageLabel {
  param([string]$Stage)
  switch ($Stage) {
    "G" { return "Graphematic worker" }
    "M" { return "Morphologic worker" }
    "S" { return "Syntactic worker" }
    "H" { return "Semantic-historical worker" }
    "L" { return "Final analysis worker" }
  }
  return $Stage
}

function Select-ActiveChapters {
  param([object[]]$Incomplete, [int]$Max)
  $selected = New-Object System.Collections.ArrayList
  if (-not $Incomplete) { return $selected }
  $append = {
    param([object[]]$Items)
    foreach ($item in ($Items | Sort-Object { $_.Chapter.Number })) {
      if ($selected.Count -ge $Max) { break }
      $exists = $selected | Where-Object { $_.Chapter.Name -eq $item.Chapter.Name }
      if (-not $exists) {
        [void]$selected.Add($item)
      }
    }
  }
  $items = $Incomplete | Where-Object { $_.H -and -not $_.L }
  & $append $items
  $items = $Incomplete | Where-Object { $_.S -and -not $_.H }
  & $append $items
  $items = $Incomplete | Where-Object { $_.M -and -not $_.S }
  & $append $items
  $items = $Incomplete | Where-Object { $_.G -and -not $_.M }
  & $append $items
  $items = $Incomplete | Where-Object { -not $_.G }
  & $append $items
  return $selected
}

function Get-StageCaps {
  param([object]$Control, [int]$MaxParallelCalls, [string[]]$StageOrder)
  $caps = @{}
  $configCaps = $null
  if ($Control -and ($Control.PSObject.Properties.Name -contains "stage_slot_limits")) {
    $configCaps = $Control.stage_slot_limits
  }
  if ($configCaps) {
    foreach ($stage in $StageOrder) {
      if ($configCaps.PSObject.Properties.Name -contains $stage) {
        $caps[$stage] = [int]$configCaps.$stage
      }
    }
  }
  if (-not $caps.Keys.Count) {
    $base = 0
    $remainder = 0
    if ($MaxParallelCalls -gt 0) {
      $base = [math]::Floor($MaxParallelCalls / $StageOrder.Count)
      $remainder = $MaxParallelCalls % $StageOrder.Count
    }
    for ($i = 0; $i -lt $StageOrder.Count; $i++) {
      $stage = $StageOrder[$i]
      $extra = 0
      if ($i -lt $remainder) { $extra = 1 }
      $caps[$stage] = $base + $extra
    }
  }
  foreach ($stage in $StageOrder) {
    if (-not $caps.ContainsKey($stage)) { $caps[$stage] = 0 }
    if ($caps[$stage] -lt 0) { $caps[$stage] = 0 }
  }
  return $caps
}

function Get-StageCandidates {
  param(
    [object[]]$ActiveChapters,
    [System.Collections.ArrayList]$ActiveJobs,
    [string]$Stage
  )
  $candidates = New-Object System.Collections.ArrayList
  foreach ($status in $ActiveChapters) {
    $chapter = $status.Chapter
    $alreadyRunning = $ActiveJobs | Where-Object { $_.ChapterName -eq $chapter.Name -and $_.Stage -eq $Stage }
    if ($alreadyRunning) { continue }
    if ($status.$Stage) { continue }
    $gateOk = $true
    switch ($Stage) {
      "M" { $gateOk = $status.G }
      "S" { $gateOk = $status.M }
      "H" { $gateOk = $status.S }
      "L" { $gateOk = $status.H }
    }
    if (-not $gateOk) { continue }
    [void]$candidates.Add($status)
  }
  return $candidates | Sort-Object { $_.Chapter.Number }
}

function Format-Elapsed {
  param([datetime]$StartTime)
  if (-not $StartTime) { return "00:00:00" }
  $elapsed = (Get-Date) - $StartTime
  return ("{0:00}:{1:00}:{2:00}" -f $elapsed.Hours, $elapsed.Minutes, $elapsed.Seconds)
}

function Write-ActiveJobsStatus {
  param(
    [System.Collections.ArrayList]$ActiveJobs,
    [int]$MaxParallelCalls,
    [int]$ActiveChapterCount,
    [int]$MaxParallelChapters,
    [int]$TotalIncomplete,
    [hashtable]$ReadyCounts,
    [object[]]$ActiveChapters
  )
  $timestamp = Get-Date -Format "HH:mm:ss"
  $ready = ""
  if ($ReadyCounts) {
    $ready = (" G={0} M={1} S={2} H={3} L={4}" -f $ReadyCounts.G, $ReadyCounts.M, $ReadyCounts.S, $ReadyCounts.H, $ReadyCounts.L)
  }
  Write-Host ("[{0}] Active jobs: {1}/{2} | active chapters: {3}/{4} | remaining chapters: {5}{6}" -f $timestamp, $ActiveJobs.Count, $MaxParallelCalls, $ActiveChapterCount, $MaxParallelChapters, $TotalIncomplete, $ready)
  foreach ($entry in ($ActiveJobs | Sort-Object Stage, ChapterNumber)) {
    $elapsed = Format-Elapsed -StartTime $entry.StartTime
    $state = $entry.Job.State
    Write-Host ("[{0}]   - {1} {2} (id={3}, state={4}, {5})" -f $timestamp, $entry.Stage, $entry.ChapterName, $entry.Job.Id, $state, $elapsed)
  }
  if ($ActiveChapters) {
    foreach ($status in ($ActiveChapters | Sort-Object { $_.Chapter.Number })) {
      Write-Host ("[{0}]   - {1}: missing G={2} M={3} S={4} H={5} L={6}" -f $timestamp, $status.Chapter.Name, $status.MissingG, $status.MissingM, $status.MissingS, $status.MissingH, $status.MissingL)
    }
  }
}

function Cleanup-WorkerJobs {
  param([ref]$ActiveJobs)
  for ($i = $ActiveJobs.Value.Count - 1; $i -ge 0; $i--) {
    $entry = $ActiveJobs.Value[$i]
    if ($entry.Job.State -in @("Completed", "Failed", "Stopped")) {
      $exitCode = $null
      if ($entry.Job.ChildJobs -and $entry.Job.ChildJobs.Count -gt 0) {
        $exitCode = $entry.Job.ChildJobs[0].ExitCode
      }
      try {
        Receive-Job -Job $entry.Job -Keep | Out-Null
      } catch {}
      Remove-Job -Job $entry.Job -Force
      $timestamp = Get-Date -Format "HH:mm:ss"
      $elapsed = Format-Elapsed -StartTime $entry.StartTime
      Write-Host ("[{0}] {1} done -> {2} (exit {3}, {4})" -f $timestamp, (Get-StageLabel -Stage $entry.Stage), $entry.ChapterName, $exitCode, $elapsed)
      $ActiveJobs.Value.RemoveAt($i)
    }
  }
}

function Get-ControlValue {
  param([object]$Control, [string]$Name, $Default)
  if ($null -eq $Control) { return $Default }
  if ($Control.PSObject.Properties.Name -contains $Name) {
    $value = $Control.$Name
    if ($null -ne $value -and $value.ToString() -ne "") {
      return $value
    }
  }
  return $Default
}

$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$storyConfigPath = Resolve-RepoPath -Path $StoryConfig -RepoRoot $repoRoot
$controlPathResolved = Resolve-RepoPath -Path $ControlPath -RepoRoot $repoRoot
$lastStatusTime = $null
$selfHealDone = New-Object System.Collections.Generic.HashSet[int]

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
    analysis_scope = "chapter"
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
    max_parallel_chapters = 10
    max_parallel_calls = 10
    status_log_workers = $true
    status_interval_seconds = 10
    auto_self_heal = $false
    auto_self_heal_mode = "always"
    self_heal_verse_root = "docs/ethiopic_1enoch_p"
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

$activeJobs = New-Object System.Collections.ArrayList

while ($true) {
  $control = Read-JsonFile -Path $controlPathResolved
  if (-not $control.enabled -or $control.pause) {
    if ($activeJobs.Count -gt 0) {
      Cleanup-WorkerJobs -ActiveJobs ([ref]$activeJobs)
    }
    Start-Sleep -Seconds $control.poll_seconds
    continue
  }

  Cleanup-WorkerJobs -ActiveJobs ([ref]$activeJobs)
  $chapters = Get-Chapters -Root $filmsetsRoot -Label $chapterLabel -Only $control.chapters
  $didWork = $false

  $mode = Get-ControlValue -Control $control -Name "mode" -Default "chapter-batch"
  if ($mode -eq "pipeline-parallel") {
    $pollSeconds = [int](Get-ControlValue -Control $control -Name "poll_seconds" -Default 10)
    $maxParallelCalls = [int](Get-ControlValue -Control $control -Name "max_parallel_calls" -Default 10)
    if ($maxParallelCalls -lt 1) { $maxParallelCalls = 1 }
    $maxParallelChapters = [int](Get-ControlValue -Control $control -Name "max_parallel_chapters" -Default 10)
    if ($maxParallelChapters -lt 1) { $maxParallelChapters = 1 }
    $statusLog = [bool](Get-ControlValue -Control $control -Name "status_log_workers" -Default $true)
    $statusInterval = [int](Get-ControlValue -Control $control -Name "status_interval_seconds" -Default $pollSeconds)
    if ($statusInterval -lt 1) { $statusInterval = $pollSeconds }
    $analysisScope = Get-ControlValue -Control $control -Name "analysis_scope" -Default "chapter-batch"
    if ($analysisScope) { $analysisScope = $analysisScope.ToString().ToLower() }
    $autoSelfHeal = [bool](Get-ControlValue -Control $control -Name "auto_self_heal" -Default $false)
    $autoSelfHealMode = Get-ControlValue -Control $control -Name "auto_self_heal_mode" -Default "always"
    if ($autoSelfHealMode) { $autoSelfHealMode = $autoSelfHealMode.ToString().ToLower() }
    $selfHealVerseRoot = Get-ControlValue -Control $control -Name "self_heal_verse_root" -Default "docs/ethiopic_1enoch_p"
    $selfHealVerseRoot = Resolve-RepoPath -Path $selfHealVerseRoot -RepoRoot $repoRoot
    $verseOverrides = @{}
    if ($autoSelfHeal -and $autoSelfHealMode -eq "missing-only") {
      $verseOverrides = Load-VerseOverrides -VerseRoot $selfHealVerseRoot
    }
    $logRoot = Get-ControlValue -Control $control -Name "log_root" -Default "stories/template/data/analysis/logs"
    $logRoot = Resolve-RepoPath -Path $logRoot -RepoRoot $repoRoot

    $chapterStatus = @{}
    foreach ($chapter in $chapters) {
      $segments = Get-Segments -ChapterDir $chapter.Path -SegmentLabel $segmentLabel
      if ($autoSelfHeal -and -not $selfHealDone.Contains($chapter.Number)) {
        $shouldHeal = $true
        if ($autoSelfHealMode -eq "missing-only") {
          $expectedMax = Get-ExpectedVerseMax -VerseRoot $selfHealVerseRoot -ChapterNumber $chapter.Number -Overrides $verseOverrides
          $missingSegments = Get-MissingSegmentIndices -Segments $segments -SegmentLabel $segmentLabel -ExpectedMax $expectedMax
          $shouldHeal = ($missingSegments.Count -gt 0)
        }
        if ($shouldHeal) {
          Invoke-SelfHeal -ChapterNumber $chapter.Number -StoryConfigPath $storyConfigPath `
            -VerseRoot $selfHealVerseRoot -RepoRoot $repoRoot -PythonExe $Python
          $segments = Get-Segments -ChapterDir $chapter.Path -SegmentLabel $segmentLabel
        }
        $selfHealDone.Add($chapter.Number) | Out-Null
      }
      if (-not $segments -or $segments.Count -eq 0) { continue }
      $missingGCount = Get-StageMissingCount -AnalysisScope $analysisScope -ChapterDir $chapter.Path `
        -Segments $segments -FileName "analysis_llm_graphematic.txt"
      $missingMCount = Get-StageMissingCount -AnalysisScope $analysisScope -ChapterDir $chapter.Path `
        -Segments $segments -FileName "analysis_llm_morphologic.txt"
      $missingSCount = Get-StageMissingCount -AnalysisScope $analysisScope -ChapterDir $chapter.Path `
        -Segments $segments -FileName "analysis_llm_synthactic.txt"
      $missingHCount = Get-StageMissingCount -AnalysisScope $analysisScope -ChapterDir $chapter.Path `
        -Segments $segments -FileName "analysis_llm_semantic_historical.txt"
      $missingLCount = Get-StageMissingCount -AnalysisScope $analysisScope -ChapterDir $chapter.Path `
        -Segments $segments -FileName "analysis_llm.txt"
      $segmentCount = $segments.Count
      $effectiveMissingM = $missingMCount
      if ($missingGCount -gt 0) { $effectiveMissingM = $segmentCount }
      $effectiveMissingS = $missingSCount
      if ($effectiveMissingM -gt 0) { $effectiveMissingS = $segmentCount }
      $effectiveMissingH = $missingHCount
      if ($effectiveMissingS -gt 0) { $effectiveMissingH = $segmentCount }
      $effectiveMissingL = $missingLCount
      if ($effectiveMissingH -gt 0) { $effectiveMissingL = $segmentCount }
      $completeG = ($missingGCount -eq 0)
      $completeM = ($missingMCount -eq 0) -and $completeG
      $completeS = ($missingSCount -eq 0) -and $completeM
      $completeH = ($missingHCount -eq 0) -and $completeS
      $completeL = ($missingLCount -eq 0) -and $completeH
      $status = [ordered]@{
        Chapter = $chapter
        Segments = $segments
        G = $completeG
        M = $completeM
        S = $completeS
        H = $completeH
        L = $completeL
        MissingG = $missingGCount
        MissingM = $effectiveMissingM
        MissingS = $effectiveMissingS
        MissingH = $effectiveMissingH
        MissingL = $effectiveMissingL
      }
      $chapterStatus[$chapter.Name] = $status
    }

    $incomplete = $chapterStatus.Values | Where-Object { -not ($_.G -and $_.M -and $_.S -and $_.H -and $_.L) }
    $activeChapters = Select-ActiveChapters -Incomplete $incomplete -Max $maxParallelChapters
    $readyCounts = @{
      G = ($activeChapters | Where-Object { -not $_.G }).Count
      M = ($activeChapters | Where-Object { $_.G -and -not $_.M }).Count
      S = ($activeChapters | Where-Object { $_.M -and -not $_.S }).Count
      H = ($activeChapters | Where-Object { $_.S -and -not $_.H }).Count
      L = ($activeChapters | Where-Object { $_.H -and -not $_.L }).Count
    }
    if ($statusLog) {
      $now = Get-Date
      if (-not $lastStatusTime -or (($now - $lastStatusTime).TotalSeconds -ge $statusInterval)) {
        Write-ActiveJobsStatus -ActiveJobs $activeJobs -MaxParallelCalls $maxParallelCalls `
          -ActiveChapterCount $activeChapters.Count -MaxParallelChapters $maxParallelChapters `
          -TotalIncomplete $incomplete.Count -ReadyCounts $readyCounts -ActiveChapters $activeChapters
        $lastStatusTime = $now
      }
    }

    $stages = @("L", "H", "S", "M", "G")
    $stageCaps = Get-StageCaps -Control $control -MaxParallelCalls $maxParallelCalls -StageOrder $stages

    foreach ($stage in $stages) {
      if ($activeJobs.Count -ge $maxParallelCalls) { break }
      $cap = $stageCaps[$stage]
      if ($cap -le 0) { continue }
      $candidates = Get-StageCandidates -ActiveChapters $activeChapters -ActiveJobs $activeJobs -Stage $stage
      $started = 0
      foreach ($status in $candidates) {
        if ($activeJobs.Count -ge $maxParallelCalls) { break }
        if ($started -ge $cap) { break }
        $chapter = $status.Chapter
        $job = Start-WorkerJob -Stage $stage -Chapter $chapter -Control $control -RepoRoot $repoRoot -LogRoot $logRoot
        if ($job) {
          [void]$activeJobs.Add([PSCustomObject]@{
            Stage = $stage
            ChapterName = $chapter.Name
            ChapterNumber = $chapter.Number
            ChapterPath = $chapter.Path
            Job = $job
            StartTime = Get-Date
          })
          $started += 1
          $didWork = $true
        }
      }
    }

    if ($activeJobs.Count -lt $maxParallelCalls) {
      foreach ($stage in $stages) {
        if ($activeJobs.Count -ge $maxParallelCalls) { break }
        $candidates = Get-StageCandidates -ActiveChapters $activeChapters -ActiveJobs $activeJobs -Stage $stage
        foreach ($status in $candidates) {
          if ($activeJobs.Count -ge $maxParallelCalls) { break }
          $chapter = $status.Chapter
          $job = Start-WorkerJob -Stage $stage -Chapter $chapter -Control $control -RepoRoot $repoRoot -LogRoot $logRoot
          if ($job) {
            [void]$activeJobs.Add([PSCustomObject]@{
              Stage = $stage
              ChapterName = $chapter.Name
              ChapterNumber = $chapter.Number
              ChapterPath = $chapter.Path
              Job = $job
              StartTime = Get-Date
            })
            $didWork = $true
          }
        }
      }
    }

    if (-not $didWork) {
      Start-Sleep -Seconds $pollSeconds
    }
    continue
  }

  foreach ($chapter in $chapters) {
    $segments = Get-Segments -ChapterDir $chapter.Path -SegmentLabel $segmentLabel
    if (-not $segments -or $segments.Count -eq 0) {
      continue
    }

    $needG = -not (Test-StageComplete -Segments $segments -FileName "analysis_llm_graphematic.txt")
    if ($needG) {
      Write-StageStart -Stage "Graphematic worker" -Chapter $chapter
      $args = Build-WorkerArgs -Stage "G" -Chapter $chapter -Control $control
      $didWork = Invoke-Worker -ScriptPath "engine/workers/worker_llm_analysis_graphematic.py" -Args $args -Retries $control.max_retries -DelaySeconds $control.retry_delay_seconds
      break
    }

    $needM = -not (Test-StageComplete -Segments $segments -FileName "analysis_llm_morphologic.txt")
    if ($needM) {
      Write-StageStart -Stage "Morphologic worker" -Chapter $chapter
      $args = Build-WorkerArgs -Stage "M" -Chapter $chapter -Control $control
      $didWork = Invoke-Worker -ScriptPath "engine/workers/worker_llm_analysis_Morphologic.py" -Args $args -Retries $control.max_retries -DelaySeconds $control.retry_delay_seconds
      break
    }

    $needS = -not (Test-StageComplete -Segments $segments -FileName "analysis_llm_synthactic.txt")
    if ($needS) {
      Write-StageStart -Stage "Syntactic worker" -Chapter $chapter
      $args = Build-WorkerArgs -Stage "S" -Chapter $chapter -Control $control
      $didWork = Invoke-Worker -ScriptPath "engine/workers/worker_llm_analysis_synthactic.py" -Args $args -Retries $control.max_retries -DelaySeconds $control.retry_delay_seconds
      break
    }

    $needH = -not (Test-StageComplete -Segments $segments -FileName "analysis_llm_semantic_historical.txt")
    if ($needH) {
      Write-StageStart -Stage "Semantic-historical worker" -Chapter $chapter
      $args = Build-WorkerArgs -Stage "H" -Chapter $chapter -Control $control
      $didWork = Invoke-Worker -ScriptPath "engine/workers/worker_llm_analysis_semantic-historical.py" -Args $args -Retries $control.max_retries -DelaySeconds $control.retry_delay_seconds
      break
    }

    $needLlm = -not (Test-StageComplete -Segments $segments -FileName "analysis_llm.txt")
    if ($needLlm) {
      Write-StageStart -Stage "Final analysis worker" -Chapter $chapter
      $args = Build-WorkerArgs -Stage "L" -Chapter $chapter -Control $control
      $didWork = Invoke-Worker -ScriptPath "engine/workers/worker_llm_analysis.py" -Args $args -Retries $control.max_retries -DelaySeconds $control.retry_delay_seconds
      break
    }
  }

  if (-not $didWork) {
    Start-Sleep -Seconds $control.poll_seconds
  }
}
